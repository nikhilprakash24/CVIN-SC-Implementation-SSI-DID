// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IMinimalSSI} from "../interfaces/IMinimalSSI.sol";
import {IControllerAdapter} from "./IControllerAdapter.sol";

/// @title EndorsementRegistry
/// @notice The governance extension named (but not specified) by the formal
///         specification §6: registerIssuer / endorseIssuer. It answers the
///         question the twelve functions presuppose but do not contain:
///         verifyCredential (F6) says "this credential was validly issued by
///         issuer X"; endorsement says "issuer X was entitled to issue credentials
///         of type T at that time, because an endorser the verifier trusts said so."
///
/// @dev Design constraints (HDA campaign):
///   * Never alters IMinimalSSI. Lives beside it; authorises *by DID* through an
///     IControllerAdapter (implementation-specific read) or through F12
///     validDelegate with delegateType ENDORSE_DELEGATE — so an OEM's plant key or
///     a ministry's signing service can act as a delegate of the root DID without
///     holding the controller key.
///   * Endorsements are typed (per credentialType) and time-bounded, and form a
///     bounded chain: a ROOT endorses a transitive endorser (e.g. a ministry), which
///     endorses a non-transitive issuer (e.g. a DMV). MAX_DEPTH bounds the read cost
///     of isEndorsed so it stays a cheap view (see doc 01 §4 read paths).
///   * On-chain state is minimal: roots, issuer roles, and endorsement records
///     keyed by (endorser, issuer, type). No credential content, no PII.
///   * Every state change emits an event; every read returns structured data and
///     never reverts on absent records (spec §5.2 conventions).
contract EndorsementRegistry {
    // ---- Types ----

    struct Endorsement {
        uint256 validUntil;   // 0 = none / revoked
        bool transitive;      // may the endorsed issuer endorse others for this type?
        uint256 issuedAt;
    }

    bytes32 public constant ENDORSE_DELEGATE = keccak256("endorse");

    /// @dev Bound on endorsement-chain depth checked by isEndorsed (root -> ... -> issuer).
    uint8 public constant MAX_DEPTH = 3;

    // ---- Errors ----
    error NotAuthorized();
    error NotRoot();
    error NotTransitiveEndorser();
    error UnknownIssuer();
    error SelfEndorsement();

    // ---- Events ----
    event RootAdded(bytes32 indexed rootDid, uint256 timestamp);
    event RootRemoved(bytes32 indexed rootDid, uint256 timestamp);
    event IssuerRegistered(bytes32 indexed issuerDid, bytes32 indexed role, address indexed by, uint256 timestamp);
    event IssuerEndorsed(bytes32 indexed endorserDid, bytes32 indexed issuerDid, bytes32 indexed credentialType, uint256 validUntil, bool transitive);
    event EndorsementRevoked(bytes32 indexed endorserDid, bytes32 indexed issuerDid, bytes32 indexed credentialType, uint256 timestamp);

    // ---- State ----
    IMinimalSSI public immutable ssi;
    IControllerAdapter public immutable adapter;
    address public admin;

    mapping(bytes32 => bool) public isRoot;                        // rootDid => true
    mapping(bytes32 => bytes32) public issuerRole;                 // issuerDid => role (0 = unregistered)
    mapping(bytes32 => mapping(bytes32 => mapping(bytes32 => Endorsement))) private _end; // endorser => issuer => type
    mapping(bytes32 => mapping(bytes32 => bytes32[])) private _endorsersOf; // issuer => type => endorsers (append-only index)

    constructor(IMinimalSSI ssi_, IControllerAdapter adapter_) {
        ssi = ssi_;
        adapter = adapter_;
        admin = msg.sender;
    }

    // ---- Authorisation: act *as a DID* ----

    /// @notice msg.sender may act for `did` if it is the DID's controller (adapter
    ///         read over F2) or a valid ENDORSE_DELEGATE (F12) of the DID.
    function _actsFor(bytes32 did) internal view returns (bool) {
        if (!adapter.isActive(did)) return false;
        if (adapter.controllerOf(did) == msg.sender) return true;
        return ssi.validDelegate(did, ENDORSE_DELEGATE, msg.sender);
    }

    modifier onlyActingFor(bytes32 did) {
        if (!_actsFor(did)) revert NotAuthorized();
        _;
    }

    // ---- Roots of trust (governance bootstrap) ----

    /// @notice Registry admin declares a root-of-trust DID (e.g. a transport
    ///         ministry, an OEM group root). Roots are the only endorsers that
    ///         need no endorsement themselves.
    function addRoot(bytes32 rootDid) external {
        if (msg.sender != admin) revert NotAuthorized();
        isRoot[rootDid] = true;
        emit RootAdded(rootDid, block.timestamp);
    }

    function removeRoot(bytes32 rootDid) external {
        if (msg.sender != admin) revert NotAuthorized();
        isRoot[rootDid] = false;
        emit RootRemoved(rootDid, block.timestamp);
    }

    // ---- G1: registerIssuer ----

    /// @notice An issuer DID declares its role (e.g. keccak("DMV"), keccak("OEM_PLANT")).
    ///         Self-registration is permissionless; entitlement comes only from endorsement.
    function registerIssuer(bytes32 issuerDid, bytes32 role) external onlyActingFor(issuerDid) {
        issuerRole[issuerDid] = role;
        emit IssuerRegistered(issuerDid, role, msg.sender, block.timestamp);
    }

    // ---- G2: endorseIssuer ----

    /// @notice `endorserDid` (acting via msg.sender) endorses `issuerDid` to issue
    ///         credentials of `credentialType` for `validity` seconds.
    /// @param transitive if true, `issuerDid` may itself endorse others for this type
    ///        (bounded by MAX_DEPTH).
    function endorseIssuer(
        bytes32 endorserDid,
        bytes32 issuerDid,
        bytes32 credentialType,
        uint256 validity,
        bool transitive
    ) external onlyActingFor(endorserDid) {
        if (endorserDid == issuerDid) revert SelfEndorsement();
        if (issuerRole[issuerDid] == bytes32(0)) revert UnknownIssuer();
        if (!isRoot[endorserDid]) {
            // Non-root endorsers must themselves hold a transitive endorsement for this type.
            (bool ok, , bool trans) = _endorsedDepth(endorserDid, credentialType, MAX_DEPTH - 1);
            if (!ok || !trans) revert NotTransitiveEndorser();
        }
        Endorsement storage e = _end[endorserDid][issuerDid][credentialType];
        if (e.issuedAt == 0) _endorsersOf[issuerDid][credentialType].push(endorserDid);
        e.validUntil = block.timestamp + validity;
        e.transitive = transitive;
        e.issuedAt = block.timestamp;
        emit IssuerEndorsed(endorserDid, issuerDid, credentialType, e.validUntil, transitive);
    }

    // ---- G3: revokeEndorsement ----

    function revokeEndorsement(bytes32 endorserDid, bytes32 issuerDid, bytes32 credentialType)
        external onlyActingFor(endorserDid)
    {
        Endorsement storage e = _end[endorserDid][issuerDid][credentialType];
        if (e.validUntil != 0) {
            e.validUntil = 0; // idempotent, irreversible for this record (re-endorse creates a new validity)
            emit EndorsementRevoked(endorserDid, issuerDid, credentialType, block.timestamp);
        }
    }

    // ---- G4: isEndorsed (view; never reverts) ----

    /// @notice Is `issuerDid` currently entitled to issue `credentialType`?
    /// @return endorsed true if an unexpired endorsement chain of depth <= MAX_DEPTH
    ///         reaches a root; `endorser` is the immediate endorser found.
    function isEndorsed(bytes32 issuerDid, bytes32 credentialType)
        external view returns (bool endorsed, bytes32 endorser)
    {
        (endorsed, endorser, ) = _endorsedDepth(issuerDid, credentialType, MAX_DEPTH);
    }

    /// @notice Endorsement record lookup (structured, non-reverting).
    function endorsement(bytes32 endorserDid, bytes32 issuerDid, bytes32 credentialType)
        external view returns (uint256 validUntil, bool transitive, uint256 issuedAt)
    {
        Endorsement storage e = _end[endorserDid][issuerDid][credentialType];
        return (e.validUntil, e.transitive, e.issuedAt);
    }

    function endorsersOf(bytes32 issuerDid, bytes32 credentialType) external view returns (bytes32[] memory) {
        return _endorsersOf[issuerDid][credentialType];
    }

    /// @dev Depth-bounded search for an active endorsement chain to a root.
    ///      Returns (found, immediateEndorser, transitiveFlagOfThatEndorsement).
    function _endorsedDepth(bytes32 issuerDid, bytes32 credentialType, uint8 depth)
        internal view returns (bool, bytes32, bool)
    {
        if (isRoot[issuerDid]) return (true, issuerDid, true);
        if (depth == 0) return (false, bytes32(0), false);
        bytes32[] storage ends = _endorsersOf[issuerDid][credentialType];
        for (uint256 i = 0; i < ends.length; i++) {
            bytes32 en = ends[i];
            Endorsement storage e = _end[en][issuerDid][credentialType];
            if (e.validUntil == 0 || e.validUntil <= block.timestamp) continue;
            if (!adapter.isActive(en)) continue; // deactivated endorser DID (F4) voids its endorsements
            if (isRoot[en]) return (true, en, e.transitive);
            (bool ok, , bool trans) = _endorsedDepth(en, credentialType, depth - 1);
            if (ok && trans) return (true, en, e.transitive);
        }
        return (false, bytes32(0), false);
    }
}
