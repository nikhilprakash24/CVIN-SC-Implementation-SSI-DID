// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ERC1155} from "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import {IMinimalSSI} from "../interfaces/IMinimalSSI.sol";

/// @title O5_ERC1155
/// @notice Multi-token soulbound bundle: the identity is token id uint256(did) (balance 1 at the
///         controller) and EVERY CREDENTIAL IS ALSO A TOKEN, id uint256(credentialId), minted to
///         the subject; revocation burns it. Family A's "batch-credential lower bound".
/// @dev Native mechanics, per CLAUDE.md rule 2:
///      * createDID mints the identity token; issueCredential mints a credential token to the
///        subject; revokeCredential burns it (balance 0 = revoked); verifyCredential reads
///        balanceOf — the credential's status is a token balance, queryable without an indexer.
///      * Soulbound: `_update` reverts any transfer between non-zero addresses; burns are only
///        allowed for credential ids (never for identity ids — DID Core §7.3 deactivation keeps
///        the identity token and sets a flag).
///      * ERC-1155 has no DID lifecycle, keys, or delegates natively (Set A 3/8 in Pass 1);
///        those are per-token state added here, as for O2 — the measured cost of that addition
///        is the comparison.
///      * resolveDID returns the O1 document layout (did, controller, keyCount).
contract O5_ERC1155 is ERC1155, IMinimalSSI {
    struct Meta { address controller; uint256 created; uint256 updated; bool deactivated; uint256 versionId; uint256 keyCount; bool exists; }
    struct Credential { bytes32 issuer; bytes32 subject; bytes32 contentHash; uint256 validUntil; bool exists; }

    error Soulbound();
    event DIDAttributeChanged(bytes32 indexed did, bytes32 indexed key, bytes value, uint256 validTo);

    mapping(uint256 => Meta) private _meta;              // identity token id => meta
    mapping(uint256 => Credential) private _creds;       // credential token id => record
    mapping(bytes32 => mapping(bytes32 => bool)) private _keys;
    mapping(bytes32 => mapping(bytes32 => mapping(address => uint256))) private _delegates;
    mapping(bytes32 => bool) private _usedChallenges;
    uint256 private _nonce;

    constructor() ERC1155("") {}

    // ---- soulbound hook: mint ok; burn only credential tokens; no transfers ----
    function _update(address from, address to, uint256[] memory ids, uint256[] memory values) internal override {
        if (from != address(0) && to != address(0)) revert Soulbound();
        if (to == address(0)) for (uint256 i = 0; i < ids.length; i++) if (_meta[ids[i]].exists) revert Soulbound();
        super._update(from, to, ids, values);
    }

    modifier onlyController(bytes32 did) {
        Meta storage m = _meta[uint256(did)];
        if (!m.exists) revert DIDNotFound();
        if (msg.sender != m.controller) revert NotAuthorized();
        _;
    }
    modifier active(bytes32 did) { if (_meta[uint256(did)].deactivated) revert DIDAlreadyDeactivated(); _; }

    // ---- DID Lifecycle ----
    function createDID(address controller) external returns (bytes32 did) {
        did = keccak256(abi.encodePacked(controller, block.chainid, _nonce++, "erc1155"));
        uint256 id = uint256(did);
        _meta[id] = Meta(controller, block.timestamp, block.timestamp, false, 1, 1, true);
        _mint(controller, id, 1, "");
        emit DIDCreated(did, controller, block.timestamp);
    }

    function resolveDID(bytes32 did) external view returns (bytes memory document, bytes memory metadata) {
        Meta storage m = _meta[uint256(did)];
        if (!m.exists) return (bytes(""), bytes(""));
        document = abi.encode(did, m.controller, m.keyCount);
        metadata = abi.encode(DIDDocumentMetadata(m.created, m.updated, m.deactivated, m.versionId));
    }

    function updateDID(bytes32 did, bytes32 key, bytes calldata value, uint256 validity) external onlyController(did) active(did) {
        Meta storage m = _meta[uint256(did)];
        m.updated = block.timestamp; m.versionId += 1;
        emit DIDAttributeChanged(did, key, value, block.timestamp + validity);
        emit DIDUpdated(did, key, block.timestamp);
    }

    function deactivateDID(bytes32 did) external onlyController(did) active(did) {
        Meta storage m = _meta[uint256(did)];
        m.deactivated = true; m.updated = block.timestamp;
        emit DIDDeactivated(did, block.timestamp);
    }

    // ---- Credentials as tokens ----
    function issueCredential(bytes32 issuer, bytes32 subject, bytes32 credentialHash, uint256 validUntil)
        external onlyController(issuer) active(issuer)
        returns (bytes32 credentialId)
    {
        Meta storage s = _meta[uint256(subject)];
        if (!s.exists) revert DIDNotFound();
        credentialId = keccak256(abi.encodePacked(issuer, subject, credentialHash, _nonce++));
        _creds[uint256(credentialId)] = Credential(issuer, subject, credentialHash, validUntil, true);
        _mint(s.controller, uint256(credentialId), 1, ""); // the credential token, held by the subject's controller
        emit CredentialIssued(credentialId, issuer, subject);
    }

    function verifyCredential(bytes32 credentialId) external view returns (bool valid, bytes32 issuer, bool revoked, bool expired) {
        Credential storage c = _creds[uint256(credentialId)];
        if (!c.exists) return (false, bytes32(0), false, false);
        revoked = balanceOf(_meta[uint256(c.subject)].controller, uint256(credentialId)) == 0; // burned = revoked
        expired = c.validUntil != 0 && block.timestamp > c.validUntil;
        valid = !revoked && !expired && !_meta[uint256(c.issuer)].deactivated;
        issuer = c.issuer;
    }

    function revokeCredential(bytes32 credentialId) external {
        Credential storage c = _creds[uint256(credentialId)];
        if (!c.exists) revert CredentialNotFound();
        if (msg.sender != _meta[uint256(c.issuer)].controller) revert NotAuthorized();
        address holder = _meta[uint256(c.subject)].controller;
        if (balanceOf(holder, uint256(credentialId)) != 0) {
            _burn(holder, uint256(credentialId), 1); // native revocation: burn the credential token
            emit CredentialRevokedEvent(credentialId, block.timestamp);
        }
    }

    function createPresentation(bytes32 holder, bytes32[] calldata credentialIds, bytes32 challenge, string calldata domain)
        external onlyController(holder) active(holder)
        returns (bytes32 presentationId)
    {
        if (_usedChallenges[challenge]) revert InvalidCredential();
        address h = _meta[uint256(holder)].controller;
        for (uint256 i = 0; i < credentialIds.length; i++) {
            Credential storage c = _creds[uint256(credentialIds[i])];
            if (!c.exists) revert CredentialNotFound();
            if (c.subject != holder) revert NotAuthorized();
            if (balanceOf(h, uint256(credentialIds[i])) == 0) revert CredentialRevoked();
            if (c.validUntil != 0 && block.timestamp > c.validUntil) revert CredentialExpired();
        }
        _usedChallenges[challenge] = true;
        presentationId = keccak256(abi.encode(holder, credentialIds, challenge, domain));
        emit PresentationCreated(presentationId, holder, challenge);
    }

    // ---- Key Management (per-token state) ----
    function addVerificationMethod(bytes32 did, bytes32 keyType, bytes calldata publicKey) external onlyController(did) active(did) returns (bytes32 keyId) {
        keyId = keccak256(abi.encodePacked(did, keyType, publicKey));
        if (!_keys[did][keyId]) { _keys[did][keyId] = true; _meta[uint256(did)].keyCount += 1; }
        emit VerificationMethodAdded(did, keyId, keyType);
    }
    function removeVerificationMethod(bytes32 did, bytes32 keyId) external onlyController(did) active(did) {
        if (!_keys[did][keyId]) revert NotAuthorized();
        if (_meta[uint256(did)].keyCount <= 1) revert NotAuthorized();
        _keys[did][keyId] = false; _meta[uint256(did)].keyCount -= 1;
        emit VerificationMethodRemoved(did, keyId);
    }
    function addDelegate(bytes32 did, bytes32 delegateType, address delegate, uint256 validity) external onlyController(did) active(did) {
        uint256 expiration = block.timestamp + validity;
        _delegates[did][delegateType][delegate] = expiration;
        emit DelegateAdded(did, delegateType, delegate, expiration);
    }
    function validDelegate(bytes32 did, bytes32 delegateType, address delegate) external view returns (bool valid) {
        uint256 exp = _delegates[did][delegateType][delegate];
        valid = exp != 0 && exp > block.timestamp && !_meta[uint256(did)].deactivated;
    }
}
