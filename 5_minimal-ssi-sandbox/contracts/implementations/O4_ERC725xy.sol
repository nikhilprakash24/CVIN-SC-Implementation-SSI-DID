// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IMinimalSSI} from "../interfaces/IMinimalSSI.sol";
import {ClaimHolderAccount} from "./ClaimHolderAccount.sol";

/// @title O4_ERC725xy
/// @notice Contract account + ERC-735 claims + ERC-734 key purposes (LUKSO/Origin lineage).
/// @dev Native mechanics, per CLAUDE.md rule 2:
///      * createDID deploys a ClaimHolderAccount whose MANAGEMENT key is keccak(controller).
///      * Authorisation = the caller holds a MANAGEMENT key on the identity's account.
///      * Keys (F9/F10) are ERC-734 keys with purposes; the controller's MANAGEMENT key is the
///        implicit first key. Delegates (F11/F12) are ACTION-purpose keys; ERC-734 has no expiry,
///        so the expiry is kept beside the key as 725Y data (hybrid, annotated).
///      * Set B is CLAIMS-ASSISTED: issueCredential adds an ERC-735 claim ON THE SUBJECT's
///        account (topic = credential hash, data = hash, issuer = issuer's account address);
///        verifyCredential reads the claim from the subject's account; revokeCredential removes
///        the claim. The registry keeps only credentialId → (issuer, subject, validUntil): ERC-735
///        has no expiry field, which is the gap that keeps F5–F7 "assisted" rather than native.
///        createPresentation remains the anchor pattern (no ERC provides it).
///      * resolveDID returns the O1 document layout (did, controller, keyCount) — the controller
///        reported is the first MANAGEMENT key's address (kept in 725Y data) so the governance
///        adapter is reusable.
contract O4_ERC725xy is IMinimalSSI {
    bytes32 private constant K_CONTROLLER = keccak256("cvin.did.controller");
    bytes32 private constant K_CREATED = keccak256("cvin.did.created");
    bytes32 private constant K_UPDATED = keccak256("cvin.did.updated");
    bytes32 private constant K_VERSION = keccak256("cvin.did.versionId");
    bytes32 private constant K_DEACTIVATED = keccak256("cvin.did.deactivated");
    uint256 private constant SCHEME_CVIN_ANCHOR = 1; // ERC-735 scheme id: "keccak256 anchor of an off-chain W3C VC"

    struct CredIndex { bytes32 issuer; bytes32 subject; uint256 validUntil; bool exists; }

    mapping(bytes32 => bool) private _isDID;
    mapping(bytes32 => CredIndex) private _cred;
    mapping(bytes32 => bool) private _usedChallenges;
    uint256 private _nonce;

    function _acct(bytes32 did) internal pure returns (ClaimHolderAccount) { return ClaimHolderAccount(address(uint160(uint256(did)))); }
    function _u(bytes32 did, bytes32 k) internal view returns (uint256 v) { bytes memory b = _acct(did).getData(k); if (b.length == 32) v = abi.decode(b, (uint256)); }
    function _set(bytes32 did, bytes32 k, uint256 v) internal { _acct(did).setData(k, abi.encode(v)); }
    function _deactivated(bytes32 did) internal view returns (bool) { return _u(did, K_DEACTIVATED) == 1; }
    function _controller(bytes32 did) internal view returns (address) { return address(uint160(_u(did, K_CONTROLLER))); }
    function _delKey(bytes32 t, address d) internal pure returns (bytes32) { return keccak256(abi.encodePacked("cvin.did.delegate", t, d)); }

    modifier onlyController(bytes32 did) {
        if (!_isDID[did]) revert DIDNotFound();
        if (!_acct(did).keyHasPurpose(keccak256(abi.encodePacked(msg.sender)), 1)) revert NotAuthorized();
        _;
    }
    modifier active(bytes32 did) { if (_deactivated(did)) revert DIDAlreadyDeactivated(); _; }

    // ---- DID Lifecycle ----

    function createDID(address controller) external returns (bytes32 did) {
        ClaimHolderAccount a = new ClaimHolderAccount(controller, address(this));
        did = bytes32(uint256(uint160(address(a))));
        _isDID[did] = true;
        a.setData(K_CONTROLLER, abi.encode(uint256(uint160(controller))));
        a.setData(K_CREATED, abi.encode(block.timestamp));
        a.setData(K_UPDATED, abi.encode(block.timestamp));
        a.setData(K_VERSION, abi.encode(uint256(1)));
        _nonce++;
        emit DIDCreated(did, controller, block.timestamp);
    }

    function resolveDID(bytes32 did) external view returns (bytes memory document, bytes memory metadata) {
        if (!_isDID[did]) return (bytes(""), bytes(""));
        document = abi.encode(did, _controller(did), _acct(did).keyCount());
        metadata = abi.encode(DIDDocumentMetadata(_u(did, K_CREATED), _u(did, K_UPDATED), _deactivated(did), _u(did, K_VERSION)));
    }

    function updateDID(bytes32 did, bytes32 key, bytes calldata value, uint256 validity) external onlyController(did) active(did) {
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

    // ---- Credential Operations: ERC-735 claims on the subject (claims-assisted) ----

    function issueCredential(bytes32 issuer, bytes32 subject, bytes32 credentialHash, uint256 validUntil)
        external onlyController(issuer) active(issuer)
        returns (bytes32 credentialId)
    {
        if (!_isDID[subject]) revert DIDNotFound();
        uint256 topic = uint256(keccak256(abi.encodePacked(credentialHash, _nonce++))); // unique topic per credential
        credentialId = _acct(subject).addClaim(topic, SCHEME_CVIN_ANCHOR, address(_acct(issuer)), "", abi.encodePacked(credentialHash), "");
        _cred[credentialId] = CredIndex(issuer, subject, validUntil, true);
        emit CredentialIssued(credentialId, issuer, subject);
    }

    function verifyCredential(bytes32 credentialId)
        external view returns (bool valid, bytes32 issuer, bool revoked, bool expired)
    {
        CredIndex storage c = _cred[credentialId];
        if (!c.exists) return (false, bytes32(0), false, false);
        revoked = !_acct(c.subject).hasClaim(credentialId); // removed claim = revoked
        expired = c.validUntil != 0 && block.timestamp > c.validUntil;
        valid = !revoked && !expired && !_deactivated(c.issuer);
        issuer = c.issuer;
    }

    function revokeCredential(bytes32 credentialId) external {
        CredIndex storage c = _cred[credentialId];
        if (!c.exists) revert CredentialNotFound();
        if (!_acct(c.issuer).keyHasPurpose(keccak256(abi.encodePacked(msg.sender)), 1)) revert NotAuthorized();
        if (_acct(c.subject).hasClaim(credentialId)) {
            _acct(c.subject).removeClaim(credentialId); // native ERC-735 revocation
            emit CredentialRevokedEvent(credentialId, block.timestamp);
        }
    }

    function createPresentation(bytes32 holder, bytes32[] calldata credentialIds, bytes32 challenge, string calldata domain)
        external onlyController(holder) active(holder)
        returns (bytes32 presentationId)
    {
        if (_usedChallenges[challenge]) revert InvalidCredential();
        ClaimHolderAccount h = _acct(holder);
        for (uint256 i = 0; i < credentialIds.length; i++) {
            CredIndex storage c = _cred[credentialIds[i]];
            if (!c.exists) revert CredentialNotFound();
            if (c.subject != holder) revert NotAuthorized();
            if (!h.hasClaim(credentialIds[i])) revert CredentialRevoked();
            if (c.validUntil != 0 && block.timestamp > c.validUntil) revert CredentialExpired();
        }
        _usedChallenges[challenge] = true;
        presentationId = keccak256(abi.encode(holder, credentialIds, challenge, domain));
        emit PresentationCreated(presentationId, holder, challenge);
    }

    // ---- Key Management: ERC-734 purpose keys ----

    function addVerificationMethod(bytes32 did, bytes32 keyType, bytes calldata publicKey)
        external onlyController(did) active(did)
        returns (bytes32 keyId)
    {
        keyId = keccak256(abi.encodePacked(did, keyType, publicKey));
        _acct(did).addKey(keyId, 2, uint256(keyType)); // ACTION purpose; keyType carried as the ERC-734 keyType
        emit VerificationMethodAdded(did, keyId, keyType);
    }

    function removeVerificationMethod(bytes32 did, bytes32 keyId) external onlyController(did) active(did) {
        ClaimHolderAccount a = _acct(did);
        (, , bytes32 k) = a.getKey(keyId);
        if (k == bytes32(0)) revert NotAuthorized();
        if (a.keyCount() <= 1) revert NotAuthorized();
        a.removeKey(keyId);
        emit VerificationMethodRemoved(did, keyId);
    }

    function addDelegate(bytes32 did, bytes32 delegateType, address delegate, uint256 validity)
        external onlyController(did) active(did)
    {
        uint256 expiration = block.timestamp + validity;
        ClaimHolderAccount a = _acct(did);
        bytes32 k = keccak256(abi.encodePacked(delegate));
        if (!a.keyHasPurpose(k, 2) && !a.keyHasPurpose(k, 1)) a.addKey(k, 2, uint256(delegateType)); // delegate = ACTION key
        a.setData(_delKey(delegateType, delegate), abi.encode(expiration));             // expiry beside it (ERC-734 has none)
        emit DelegateAdded(did, delegateType, delegate, expiration);
    }

    function validDelegate(bytes32 did, bytes32 delegateType, address delegate) external view returns (bool valid) {
        if (!_isDID[did]) return false;
        uint256 exp = _u(did, _delKey(delegateType, delegate));
        valid = exp != 0 && exp > block.timestamp && !_deactivated(did);
    }
}
