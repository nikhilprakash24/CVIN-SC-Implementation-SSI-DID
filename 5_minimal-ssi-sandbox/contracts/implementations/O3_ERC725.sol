// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IMinimalSSI} from "../interfaces/IMinimalSSI.sol";
import {ERC725Account} from "./ERC725Account.sol";

/// @title O3_ERC725
/// @notice Contract-account option: every createDID DEPLOYS an ERC725Account; the DID is the
///         account address; the DID Document is the account's ERC-725Y store, read with
///         getData — directly queryable on-chain with no indexer (the Family C property).
/// @dev Native mechanics, per CLAUDE.md rule 2:
///      * All identity state (metadata, keys, delegates, deactivation) is ERC-725Y data in
///        the identity's own account under namespaced bytes32 keys. This registry holds
///        only the account set and the credential → issuer index.
///      * The registry is each account's `manager`; it writes to an account only after
///        checking msg.sender == account.owner() (the controller).
///      * Set B is the shared anchor pattern; anchors live in the ISSUER's 725Y store so a
///        credential is discoverable from its issuer without an indexer.
///      Costs are expected to be the highest of the EVM options (deployment per identity,
///      external calls per operation) — that is the trade-off under measurement.
///      resolveDID returns the O1 document layout (did, controller, keyCount) so the
///      governance adapter is reused.
contract O3_ERC725 is IMinimalSSI {
    // ERC-725Y data keys (namespaced; a production deployment would register them in an ERC725 schema)
    bytes32 private constant K_CREATED = keccak256("cvin.did.created");
    bytes32 private constant K_UPDATED = keccak256("cvin.did.updated");
    bytes32 private constant K_VERSION = keccak256("cvin.did.versionId");
    bytes32 private constant K_DEACTIVATED = keccak256("cvin.did.deactivated");
    bytes32 private constant K_KEYCOUNT = keccak256("cvin.did.keyCount");

    mapping(bytes32 => bool) private _isDID;          // did => deployed by this registry
    mapping(bytes32 => bytes32) private _credIssuer;  // credentialId => issuer did
    mapping(bytes32 => bool) private _usedChallenges;
    uint256 private _nonce;

    function _acct(bytes32 did) internal pure returns (ERC725Account) { return ERC725Account(payable(address(uint160(uint256(did))))); }
    function _u(bytes32 did, bytes32 k) internal view returns (uint256 v) { bytes memory b = _acct(did).getData(k); if (b.length == 32) v = abi.decode(b, (uint256)); }
    function _set(bytes32 did, bytes32 k, uint256 v) internal { _acct(did).setData(k, abi.encode(v)); }
    function _deactivated(bytes32 did) internal view returns (bool) { return _u(did, K_DEACTIVATED) == 1; }
    function _keyKey(bytes32 keyId) internal pure returns (bytes32) { return keccak256(abi.encodePacked("cvin.did.key", keyId)); }
    function _delKey(bytes32 t, address d) internal pure returns (bytes32) { return keccak256(abi.encodePacked("cvin.did.delegate", t, d)); }
    function _credKey(bytes32 id) internal pure returns (bytes32) { return keccak256(abi.encodePacked("cvin.vc", id)); }

    modifier onlyController(bytes32 did) {
        if (!_isDID[did]) revert DIDNotFound();
        if (msg.sender != _acct(did).owner()) revert NotAuthorized();
        _;
    }
    modifier active(bytes32 did) { if (_deactivated(did)) revert DIDAlreadyDeactivated(); _; }

    // ---- DID Lifecycle ----

    function createDID(address controller) external returns (bytes32 did) {
        ERC725Account a = new ERC725Account(controller, address(this)); // the native primitive: deploy
        did = bytes32(uint256(uint160(address(a))));
        _isDID[did] = true;
        a.setData(K_CREATED, abi.encode(block.timestamp));
        a.setData(K_UPDATED, abi.encode(block.timestamp));
        a.setData(K_VERSION, abi.encode(uint256(1)));
        a.setData(K_KEYCOUNT, abi.encode(uint256(1))); // owner key implicit
        _nonce++;
        emit DIDCreated(did, controller, block.timestamp);
    }

    function resolveDID(bytes32 did) external view returns (bytes memory document, bytes memory metadata) {
        if (!_isDID[did]) return (bytes(""), bytes(""));
        ERC725Account a = _acct(did);
        document = abi.encode(did, a.owner(), _u(did, K_KEYCOUNT));
        metadata = abi.encode(DIDDocumentMetadata(_u(did, K_CREATED), _u(did, K_UPDATED), _deactivated(did), _u(did, K_VERSION)));
    }

    function updateDID(bytes32 did, bytes32 key, bytes calldata value, uint256 validity)
        external onlyController(did) active(did)
    {
        // Attribute is written INTO the account store (queryable), validity alongside it.
        _acct(did).setData(keccak256(abi.encodePacked("cvin.did.attr", key)), abi.encode(value, block.timestamp + validity));
        _set(did, K_UPDATED, block.timestamp);
        _set(did, K_VERSION, _u(did, K_VERSION) + 1);
        emit DIDUpdated(did, key, block.timestamp);
    }

    function deactivateDID(bytes32 did) external onlyController(did) active(did) {
        _set(did, K_DEACTIVATED, 1);
        _set(did, K_UPDATED, block.timestamp);
        emit DIDDeactivated(did, block.timestamp);
    }

    // ---- Credential Operations (anchor pattern; anchor lives in the issuer's store) ----

    function issueCredential(bytes32 issuer, bytes32 subject, bytes32 credentialHash, uint256 validUntil)
        external onlyController(issuer) active(issuer)
        returns (bytes32 credentialId)
    {
        if (!_isDID[subject]) revert DIDNotFound();
        credentialId = keccak256(abi.encodePacked(issuer, subject, credentialHash, _nonce++));
        _credIssuer[credentialId] = issuer;
        _acct(issuer).setData(_credKey(credentialId), abi.encode(subject, credentialHash, validUntil, false));
        emit CredentialIssued(credentialId, issuer, subject);
    }

    function _cred(bytes32 id) internal view returns (bool exists, bytes32 issuer, bytes32 subject, uint256 validUntil, bool revoked) {
        issuer = _credIssuer[id];
        if (issuer == bytes32(0)) return (false, 0, 0, 0, false);
        bytes memory b = _acct(issuer).getData(_credKey(id));
        (subject, , validUntil, revoked) = abi.decode(b, (bytes32, bytes32, uint256, bool));
        exists = true;
    }

    function verifyCredential(bytes32 credentialId)
        external view returns (bool valid, bytes32 issuer, bool revoked, bool expired)
    {
        (bool exists, bytes32 iss, , uint256 validUntil, bool rev) = _cred(credentialId);
        if (!exists) return (false, bytes32(0), false, false);
        revoked = rev;
        expired = validUntil != 0 && block.timestamp > validUntil;
        valid = !revoked && !expired && !_deactivated(iss);
        issuer = iss;
    }

    function revokeCredential(bytes32 credentialId) external {
        (bool exists, bytes32 iss, bytes32 subject, uint256 validUntil, bool rev) = _cred(credentialId);
        if (!exists) revert CredentialNotFound();
        if (msg.sender != _acct(iss).owner()) revert NotAuthorized();
        if (!rev) {
            bytes memory b = _acct(iss).getData(_credKey(credentialId));
            (, bytes32 h, , ) = abi.decode(b, (bytes32, bytes32, uint256, bool));
            _acct(iss).setData(_credKey(credentialId), abi.encode(subject, h, validUntil, true));
            emit CredentialRevokedEvent(credentialId, block.timestamp);
        }
    }

    function createPresentation(bytes32 holder, bytes32[] calldata credentialIds, bytes32 challenge, string calldata domain)
        external onlyController(holder) active(holder)
        returns (bytes32 presentationId)
    {
        if (_usedChallenges[challenge]) revert InvalidCredential();
        for (uint256 i = 0; i < credentialIds.length; i++) {
            (bool exists, , bytes32 subject, uint256 validUntil, bool rev) = _cred(credentialIds[i]);
            if (!exists) revert CredentialNotFound();
            if (subject != holder) revert NotAuthorized();
            if (rev) revert CredentialRevoked();
            if (validUntil != 0 && block.timestamp > validUntil) revert CredentialExpired();
        }
        _usedChallenges[challenge] = true;
        presentationId = keccak256(abi.encode(holder, credentialIds, challenge, domain));
        emit PresentationCreated(presentationId, holder, challenge);
    }

    // ---- Key Management (ERC-725Y data) ----

    function addVerificationMethod(bytes32 did, bytes32 keyType, bytes calldata publicKey)
        external onlyController(did) active(did)
        returns (bytes32 keyId)
    {
        keyId = keccak256(abi.encodePacked(did, keyType, publicKey));
        ERC725Account a = _acct(did);
        if (a.getData(_keyKey(keyId)).length == 0) {
            a.setData(_keyKey(keyId), abi.encode(keyType, publicKey)); // the key itself is on-chain and queryable
            _set(did, K_KEYCOUNT, _u(did, K_KEYCOUNT) + 1);
        }
        emit VerificationMethodAdded(did, keyId, keyType);
    }

    function removeVerificationMethod(bytes32 did, bytes32 keyId) external onlyController(did) active(did) {
        ERC725Account a = _acct(did);
        if (a.getData(_keyKey(keyId)).length == 0) revert NotAuthorized();
        if (_u(did, K_KEYCOUNT) <= 1) revert NotAuthorized();
        a.setData(_keyKey(keyId), "");
        _set(did, K_KEYCOUNT, _u(did, K_KEYCOUNT) - 1);
        emit VerificationMethodRemoved(did, keyId);
    }

    function addDelegate(bytes32 did, bytes32 delegateType, address delegate, uint256 validity)
        external onlyController(did) active(did)
    {
        uint256 expiration = block.timestamp + validity;
        _acct(did).setData(_delKey(delegateType, delegate), abi.encode(expiration));
        emit DelegateAdded(did, delegateType, delegate, expiration);
    }

    function validDelegate(bytes32 did, bytes32 delegateType, address delegate) external view returns (bool valid) {
        if (!_isDID[did]) return false;
        uint256 exp = _u(did, _delKey(delegateType, delegate));
        valid = exp != 0 && exp > block.timestamp && !_deactivated(did);
    }
}
