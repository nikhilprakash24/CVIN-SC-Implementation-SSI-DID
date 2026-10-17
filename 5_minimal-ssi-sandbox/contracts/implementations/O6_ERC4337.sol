// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IMinimalSSI} from "../interfaces/IMinimalSSI.sol";
import {SmartAccount} from "./SmartAccount.sol";

/// @title O6_ERC4337
/// @notice Smart account = DID. Authorisation is routed through the account's validation keys
///         (validateUserOp-style), delegates are ERC-4337 session keys whose expiry is the
///         standard's own validUntil, and verification methods are validation keys.
/// @dev Native mechanics, per CLAUDE.md rule 2:
///      * createDID deploys a SmartAccount with the controller as owner-class validation key.
///      * onlyController == account.validateCaller(msg.sender): the same key set that
///        validateUserOp evaluates for a signed op (test/o6_native.js checks both agree).
///      * F11 addDelegate = setSessionKey(validAfter=now, validUntil=now+validity);
///        F12 validDelegate = sessionValid — no sandbox-side expiry bookkeeping at all.
///      * F9 addVerificationMethod: a 20-byte publicKey registers a validation key (address);
///        other key material is recorded as account data (queryable) and counted.
///      * Set B is the shared anchor pattern (anchors in the registry; the account is the
///        signer, not the store — the 4337 account is an authorisation object, not a record).
///      * resolveDID returns the O1 document layout (did, controller, keyCount).
contract O6_ERC4337 is IMinimalSSI {
    struct Meta { uint256 created; uint256 updated; bool deactivated; uint256 versionId; uint256 extraKeys; bool exists; }
    struct Credential { bytes32 issuer; bytes32 subject; bytes32 contentHash; uint256 validUntil; bool revoked; bool exists; }

    event DIDAttributeChanged(bytes32 indexed did, bytes32 indexed key, bytes value, uint256 validTo);

    mapping(bytes32 => Meta) private _meta;
    mapping(bytes32 => Credential) private _creds;
    mapping(bytes32 => mapping(bytes32 => address)) private _keyAddr; // keyId => validation key address (if any)
    mapping(bytes32 => mapping(bytes32 => bool)) private _keyExists;
    mapping(bytes32 => bool) private _usedChallenges;
    uint256 private _nonce;

    function _acct(bytes32 did) internal pure returns (SmartAccount) { return SmartAccount(payable(address(uint160(uint256(did))))); }

    modifier onlyController(bytes32 did) {
        if (!_meta[did].exists) revert DIDNotFound();
        if (!_acct(did).validateCaller(msg.sender)) revert NotAuthorized(); // validation-key routing
        _;
    }
    modifier active(bytes32 did) { if (_meta[did].deactivated) revert DIDAlreadyDeactivated(); _; }

    // ---- DID Lifecycle ----
    function createDID(address controller) external returns (bytes32 did) {
        SmartAccount a = new SmartAccount(controller, address(this));
        did = bytes32(uint256(uint160(address(a))));
        _meta[did] = Meta(block.timestamp, block.timestamp, false, 1, 0, true);
        _nonce++;
        emit DIDCreated(did, controller, block.timestamp);
    }

    function resolveDID(bytes32 did) external view returns (bytes memory document, bytes memory metadata) {
        Meta storage m = _meta[did];
        if (!m.exists) return (bytes(""), bytes(""));
        SmartAccount a = _acct(did);
        document = abi.encode(did, a.owner(), a.validationKeyCount() + m.extraKeys);
        metadata = abi.encode(DIDDocumentMetadata(m.created, m.updated, m.deactivated, m.versionId));
    }

    function updateDID(bytes32 did, bytes32 key, bytes calldata value, uint256 validity) external onlyController(did) active(did) {
        _acct(did).setData(keccak256(abi.encodePacked("cvin.did.attr", key)), abi.encode(value, block.timestamp + validity));
        Meta storage m = _meta[did]; m.updated = block.timestamp; m.versionId += 1;
        emit DIDUpdated(did, key, block.timestamp);
    }

    function deactivateDID(bytes32 did) external onlyController(did) active(did) {
        Meta storage m = _meta[did]; m.deactivated = true; m.updated = block.timestamp;
        emit DIDDeactivated(did, block.timestamp);
    }

    // ---- Credentials (anchor pattern) ----
    function issueCredential(bytes32 issuer, bytes32 subject, bytes32 credentialHash, uint256 validUntil)
        external onlyController(issuer) active(issuer) returns (bytes32 credentialId)
    {
        if (!_meta[subject].exists) revert DIDNotFound();
        credentialId = keccak256(abi.encodePacked(issuer, subject, credentialHash, _nonce++));
        _creds[credentialId] = Credential(issuer, subject, credentialHash, validUntil, false, true);
        emit CredentialIssued(credentialId, issuer, subject);
    }
    function verifyCredential(bytes32 credentialId) external view returns (bool valid, bytes32 issuer, bool revoked, bool expired) {
        Credential storage c = _creds[credentialId];
        if (!c.exists) return (false, bytes32(0), false, false);
        revoked = c.revoked; expired = c.validUntil != 0 && block.timestamp > c.validUntil;
        valid = !revoked && !expired && !_meta[c.issuer].deactivated; issuer = c.issuer;
    }
    function revokeCredential(bytes32 credentialId) external {
        Credential storage c = _creds[credentialId];
        if (!c.exists) revert CredentialNotFound();
        if (!_acct(c.issuer).validateCaller(msg.sender)) revert NotAuthorized();
        if (!c.revoked) { c.revoked = true; emit CredentialRevokedEvent(credentialId, block.timestamp); }
    }
    function createPresentation(bytes32 holder, bytes32[] calldata credentialIds, bytes32 challenge, string calldata domain)
        external onlyController(holder) active(holder) returns (bytes32 presentationId)
    {
        if (_usedChallenges[challenge]) revert InvalidCredential();
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

    // ---- Key Management: validation keys and session keys ----
    function addVerificationMethod(bytes32 did, bytes32 keyType, bytes calldata publicKey)
        external onlyController(did) active(did) returns (bytes32 keyId)
    {
        keyId = keccak256(abi.encodePacked(did, keyType, publicKey));
        if (!_keyExists[did][keyId]) {
            _keyExists[did][keyId] = true;
            if (publicKey.length == 20) { // an address: becomes a validation key (full authority)
                address k = address(bytes20(publicKey));
                _acct(did).addValidationKey(k); _keyAddr[did][keyId] = k;
            } else {                      // other key material: recorded on the account, counted
                _acct(did).setData(keccak256(abi.encodePacked("cvin.did.key", keyId)), abi.encode(keyType, publicKey));
                _meta[did].extraKeys += 1;
            }
        }
        emit VerificationMethodAdded(did, keyId, keyType);
    }

    function removeVerificationMethod(bytes32 did, bytes32 keyId) external onlyController(did) active(did) {
        if (!_keyExists[did][keyId]) revert NotAuthorized();
        SmartAccount a = _acct(did);
        if (a.validationKeyCount() + _meta[did].extraKeys <= 1) revert NotAuthorized();
        address k = _keyAddr[did][keyId];
        if (k != address(0)) { if (a.validationKeyCount() <= 1) revert NotAuthorized(); a.removeValidationKey(k); delete _keyAddr[did][keyId]; }
        else { a.setData(keccak256(abi.encodePacked("cvin.did.key", keyId)), ""); _meta[did].extraKeys -= 1; }
        _keyExists[did][keyId] = false;
        emit VerificationMethodRemoved(did, keyId);
    }

    function addDelegate(bytes32 did, bytes32 delegateType, address delegate, uint256 validity) external onlyController(did) active(did) {
        uint256 expiration = block.timestamp + validity;
        _acct(did).setSessionKey(delegate, uint48(block.timestamp), uint48(expiration)); // ERC-4337 session key = delegate
        emit DelegateAdded(did, delegateType, delegate, expiration);
    }

    function validDelegate(bytes32 did, bytes32 /*delegateType*/, address delegate) external view returns (bool valid) {
        if (!_meta[did].exists) return false;
        valid = _acct(did).sessionValid(delegate) && !_meta[did].deactivated; // expiry lives in the account
    }
}
