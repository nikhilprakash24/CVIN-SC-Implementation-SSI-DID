// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IMinimalSSI} from "../interfaces/IMinimalSSI.sol";

/// @title O1_ERC1056
/// @notice Reference implementation: ERC-1056 (did:ethr) pattern.
/// @dev Event-sourced attributes, minimal on-chain state, implicit identity model
///      adapted to explicit bytes32 DIDs for interface uniformity. Lowest-gas option.
///      Set A functions are native to ERC-1056; Set B (credential layer) is provided
///      by the shared anchor pattern (hash-on-chain, content off-chain) since no ERC
///      natively supports credentials — the Set A/Set B finding.
contract O1_ERC1056 is IMinimalSSI {

    struct Identity {
        address controller;
        uint256 created;
        uint256 updated;
        bool deactivated;
        uint256 versionId;
        bool exists;
        uint256 keyCount;
    }

    struct Credential {
        bytes32 issuer;
        bytes32 subject;
        bytes32 contentHash;
        uint256 validUntil;
        bool revoked;
        bool exists;
    }

    /// @dev ERC-1056-style attribute event (value + validity captured by off-chain indexer).
    event DIDAttributeChanged(bytes32 indexed did, bytes32 indexed key, bytes value, uint256 validTo);

    mapping(bytes32 => Identity) private _ids;
    mapping(bytes32 => Credential) private _creds;
    mapping(bytes32 => mapping(bytes32 => bool)) private _keys;
    mapping(bytes32 => mapping(bytes32 => mapping(address => uint256))) private _delegates;
    mapping(bytes32 => bool) private _usedChallenges;
    uint256 private _nonce;

    modifier exists_(bytes32 did) {
        if (!_ids[did].exists) revert DIDNotFound();
        _;
    }

    modifier onlyController(bytes32 did) {
        if (!_ids[did].exists) revert DIDNotFound();
        if (msg.sender != _ids[did].controller) revert NotAuthorized();
        _;
    }

    modifier active(bytes32 did) {
        if (_ids[did].deactivated) revert DIDAlreadyDeactivated();
        _;
    }

    // ---- DID Lifecycle ----

    function createDID(address controller) external returns (bytes32 did) {
        did = keccak256(abi.encodePacked(controller, block.chainid, _nonce++));
        Identity storage id_ = _ids[did];
        id_.controller = controller;
        id_.created = block.timestamp;
        id_.updated = block.timestamp;
        id_.versionId = 1;
        id_.exists = true;
        id_.keyCount = 1; // implicit controller key (did:ethr semantics)
        emit DIDCreated(did, controller, block.timestamp);
    }

    function resolveDID(bytes32 did) external view returns (bytes memory document, bytes memory metadata) {
        Identity storage id_ = _ids[did];
        if (!id_.exists) return (bytes(""), bytes(""));
        document = abi.encode(did, id_.controller, id_.keyCount);
        metadata = abi.encode(DIDDocumentMetadata(id_.created, id_.updated, id_.deactivated, id_.versionId));
    }

    function updateDID(bytes32 did, bytes32 key, bytes calldata value, uint256 validity)
        external onlyController(did) active(did)
    {
        Identity storage id_ = _ids[did];
        id_.updated = block.timestamp;
        id_.versionId += 1;
        emit DIDAttributeChanged(did, key, value, block.timestamp + validity);
        emit DIDUpdated(did, key, block.timestamp);
    }

    function deactivateDID(bytes32 did) external onlyController(did) active(did) {
        _ids[did].deactivated = true;
        _ids[did].updated = block.timestamp;
        emit DIDDeactivated(did, block.timestamp);
    }

    // ---- Credential Operations (Set B via shared anchor pattern) ----

    function issueCredential(bytes32 issuer, bytes32 subject, bytes32 credentialHash, uint256 validUntil)
        external onlyController(issuer) active(issuer) exists_(subject)
        returns (bytes32 credentialId)
    {
        credentialId = keccak256(abi.encodePacked(issuer, subject, credentialHash, _nonce++));
        _creds[credentialId] = Credential(issuer, subject, credentialHash, validUntil, false, true);
        emit CredentialIssued(credentialId, issuer, subject);
    }

    function verifyCredential(bytes32 credentialId)
        external view
        returns (bool valid, bytes32 issuer, bool revoked, bool expired)
    {
        Credential storage c = _creds[credentialId];
        if (!c.exists) return (false, bytes32(0), false, false);
        revoked = c.revoked;
        expired = c.validUntil != 0 && block.timestamp > c.validUntil;
        bool issuerDeactivated = _ids[c.issuer].deactivated;
        valid = !revoked && !expired && !issuerDeactivated;
        issuer = c.issuer;
    }

    function revokeCredential(bytes32 credentialId) external {
        Credential storage c = _creds[credentialId];
        if (!c.exists) revert CredentialNotFound();
        if (msg.sender != _ids[c.issuer].controller) revert NotAuthorized();
        if (!c.revoked) {
            c.revoked = true;
            emit CredentialRevokedEvent(credentialId, block.timestamp);
        } // idempotent
    }

    function createPresentation(bytes32 holder, bytes32[] calldata credentialIds, bytes32 challenge, string calldata domain)
        external onlyController(holder) active(holder)
        returns (bytes32 presentationId)
    {
        if (_usedChallenges[challenge]) revert InvalidCredential(); // replay prevention
        for (uint256 i = 0; i < credentialIds.length; i++) {
            Credential storage c = _creds[credentialIds[i]];
            if (!c.exists) revert CredentialNotFound();
            if (c.subject != holder) revert NotAuthorized();
            if (c.revoked) revert CredentialRevoked();
            if (c.validUntil != 0 && block.timestamp > c.validUntil) revert CredentialExpired();
        }
        _usedChallenges[challenge] = true;
        presentationId = keccak256(abi.encode(holder, credentialIds, challenge, domain));
        emit PresentationCreated(presentationId, holder, challenge);
    }

    // ---- Key Management ----

    function addVerificationMethod(bytes32 did, bytes32 keyType, bytes calldata publicKey)
        external onlyController(did) active(did)
        returns (bytes32 keyId)
    {
        keyId = keccak256(abi.encodePacked(did, keyType, publicKey));
        if (!_keys[did][keyId]) {
            _keys[did][keyId] = true;
            _ids[did].keyCount += 1;
        }
        emit VerificationMethodAdded(did, keyId, keyType);
    }

    function removeVerificationMethod(bytes32 did, bytes32 keyId)
        external onlyController(did) active(did)
    {
        if (!_keys[did][keyId]) revert NotAuthorized();
        if (_ids[did].keyCount <= 1) revert NotAuthorized(); // never remove last key
        _keys[did][keyId] = false;
        _ids[did].keyCount -= 1;
        emit VerificationMethodRemoved(did, keyId);
    }

    function addDelegate(bytes32 did, bytes32 delegateType, address delegate, uint256 validity)
        external onlyController(did) active(did)
    {
        uint256 expiration = block.timestamp + validity;
        _delegates[did][delegateType][delegate] = expiration;
        emit DelegateAdded(did, delegateType, delegate, expiration);
    }

    function validDelegate(bytes32 did, bytes32 delegateType, address delegate)
        external view
        returns (bool valid)
    {
        uint256 exp = _delegates[did][delegateType][delegate];
        valid = exp != 0 && exp > block.timestamp && !_ids[did].deactivated;
    }
}
