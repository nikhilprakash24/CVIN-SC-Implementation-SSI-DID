// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IMinimalSSI} from "../interfaces/IMinimalSSI.sol";
import {ISetC} from "../interfaces/ISetC.sol";
import {IdentityRegistry8004, ReputationRegistry8004, ValidationRegistry8004} from "./ERC8004Registries.sol";

/// @title O7_ERC8004
/// @notice Agent/registry option: the IMinimalSSI + ISetC compliance layer over the three
///         ERC-8004 registries (deployed by this contract's constructor, wired per the spec's
///         initialize(identityRegistry) pattern). This is the reference Set C implementation.
/// @dev Native mechanics, per CLAUDE.md rule 2:
///      * createDID = IdentityRegistry.registerFor(controller): the agent NFT is minted; DID =
///        bytes32(agentId); controller = ownerOf(agentId). Agents are TRANSFERABLE in ERC-8004
///        (unlike O2/O5); a transfer changes the controller — recorded, not prevented.
///      * updateDID writes agent metadata (setMetadata) — the spec's on-chain metadata hook;
///        the agentURI (registration file) is the off-chain DID-document analogue.
///      * deactivateDID sets metadata "cvin.deactivated"; the NFT persists (resolvable, flagged).
///      * F9–F12 are metadata entries (ERC-8004 has no key or delegate model; operators via
///        ERC-721 approvals are the native delegation and are honoured by isOwnerOrOperator).
///      * Set B is the anchor pattern in this contract (ERC-8004 has no credential object).
///      * ISetC: attestReputation → ReputationRegistry.giveFeedback(value=score, decimals=0,
///        tag1="starred") from the CALLER as client (spec: never the owner/operator);
///        getReputation → getSummary over all recorded clients, clamped to 0–100;
///        requestValidation → ValidationRegistry.validationRequest(validator = first 20 bytes
///        of payload, requestHash = keccak(did, type, payload, nonce));
///        validationStatus → 0 unknown · 1 requested · 2 response ≥ 50 · 3 response < 50.
///      Mainnet addresses for fidelity are cited in ERC8004Registries.sol.
///      resolveDID returns the O1 document layout (did, controller, keyCount).
contract O7_ERC8004 is IMinimalSSI, ISetC {
    struct Meta { uint256 created; uint256 updated; uint256 versionId; uint256 keyCount; bool exists; }
    struct Credential { bytes32 issuer; bytes32 subject; bytes32 contentHash; uint256 validUntil; bool revoked; bool exists; }

    IdentityRegistry8004 public immutable identity;
    ReputationRegistry8004 public immutable reputation;
    ValidationRegistry8004 public immutable validation;

    mapping(bytes32 => Meta) private _meta;
    mapping(bytes32 => Credential) private _creds;
    mapping(bytes32 => mapping(bytes32 => bool)) private _keys;
    mapping(bytes32 => mapping(bytes32 => mapping(address => uint256))) private _delegates;
    mapping(bytes32 => bool) private _usedChallenges;
    mapping(bytes32 => bytes32) private _reqDid; // requestHash => did
    uint256 private _nonce;

    constructor() {
        identity = new IdentityRegistry8004(address(this));
        reputation = new ReputationRegistry8004(); reputation.initialize(address(identity));
        validation = new ValidationRegistry8004(); validation.initialize(address(identity));
    }

    function _id(bytes32 did) internal pure returns (uint256) { return uint256(did); }
    function _deactivated(bytes32 did) internal view returns (bool) { return identity.getMetadata(_id(did), "cvin.deactivated").length != 0; }
    function _controller(bytes32 did) internal view returns (address) { return identity.ownerOf(_id(did)); }

    modifier onlyController(bytes32 did) {
        if (!_meta[did].exists) revert DIDNotFound();
        if (!identity.isOwnerOrOperator(_id(did), msg.sender) || msg.sender == address(this)) revert NotAuthorized();
        _;
    }
    modifier active(bytes32 did) { if (_deactivated(did)) revert DIDAlreadyDeactivated(); _; }

    // ---- DID Lifecycle ----
    function createDID(address controller) external returns (bytes32 did) {
        uint256 agentId = identity.registerFor(controller, "");
        did = bytes32(agentId);
        _meta[did] = Meta(block.timestamp, block.timestamp, 1, 1, true);
        _nonce++;
        emit DIDCreated(did, controller, block.timestamp);
    }
    function resolveDID(bytes32 did) external view returns (bytes memory document, bytes memory metadata) {
        Meta storage m = _meta[did];
        if (!m.exists) return (bytes(""), bytes(""));
        document = abi.encode(did, _controller(did), m.keyCount);
        metadata = abi.encode(DIDDocumentMetadata(m.created, m.updated, _deactivated(did), m.versionId));
    }
    function updateDID(bytes32 did, bytes32 key, bytes calldata value, uint256 validity) external onlyController(did) active(did) {
        identity.setMetadata(_id(did), string(abi.encodePacked("cvin.attr.", key)), abi.encode(value, block.timestamp + validity));
        Meta storage m = _meta[did]; m.updated = block.timestamp; m.versionId += 1;
        emit DIDUpdated(did, key, block.timestamp);
    }
    function deactivateDID(bytes32 did) external onlyController(did) active(did) {
        identity.setMetadata(_id(did), "cvin.deactivated", abi.encode(block.timestamp));
        _meta[did].updated = block.timestamp;
        emit DIDDeactivated(did, block.timestamp);
    }

    // ---- Credentials (anchor pattern) ----
    function issueCredential(bytes32 issuer, bytes32 subject, bytes32 credentialHash, uint256 validUntil) external onlyController(issuer) active(issuer) returns (bytes32 credentialId) {
        if (!_meta[subject].exists) revert DIDNotFound();
        credentialId = keccak256(abi.encodePacked(issuer, subject, credentialHash, _nonce++));
        _creds[credentialId] = Credential(issuer, subject, credentialHash, validUntil, false, true);
        emit CredentialIssued(credentialId, issuer, subject);
    }
    function verifyCredential(bytes32 credentialId) external view returns (bool valid, bytes32 issuer, bool revoked, bool expired) {
        Credential storage c = _creds[credentialId];
        if (!c.exists) return (false, bytes32(0), false, false);
        revoked = c.revoked; expired = c.validUntil != 0 && block.timestamp > c.validUntil;
        valid = !revoked && !expired && !_deactivated(c.issuer); issuer = c.issuer;
    }
    function revokeCredential(bytes32 credentialId) external {
        Credential storage c = _creds[credentialId];
        if (!c.exists) revert CredentialNotFound();
        if (!identity.isOwnerOrOperator(_id(c.issuer), msg.sender)) revert NotAuthorized();
        if (!c.revoked) { c.revoked = true; emit CredentialRevokedEvent(credentialId, block.timestamp); }
    }
    function createPresentation(bytes32 holder, bytes32[] calldata credentialIds, bytes32 challenge, string calldata domain) external onlyController(holder) active(holder) returns (bytes32 presentationId) {
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

    // ---- Key Management (agent metadata) ----
    function addVerificationMethod(bytes32 did, bytes32 keyType, bytes calldata publicKey) external onlyController(did) active(did) returns (bytes32 keyId) {
        keyId = keccak256(abi.encodePacked(did, keyType, publicKey));
        if (!_keys[did][keyId]) {
            _keys[did][keyId] = true; _meta[did].keyCount += 1;
            identity.setMetadata(_id(did), string(abi.encodePacked("cvin.key.", keyId)), abi.encode(keyType, publicKey));
        }
        emit VerificationMethodAdded(did, keyId, keyType);
    }
    function removeVerificationMethod(bytes32 did, bytes32 keyId) external onlyController(did) active(did) {
        if (!_keys[did][keyId]) revert NotAuthorized();
        if (_meta[did].keyCount <= 1) revert NotAuthorized();
        _keys[did][keyId] = false; _meta[did].keyCount -= 1;
        identity.setMetadata(_id(did), string(abi.encodePacked("cvin.key.", keyId)), "");
        emit VerificationMethodRemoved(did, keyId);
    }
    function addDelegate(bytes32 did, bytes32 delegateType, address delegate, uint256 validity) external onlyController(did) active(did) {
        uint256 expiration = block.timestamp + validity;
        _delegates[did][delegateType][delegate] = expiration;
        identity.setMetadata(_id(did), string(abi.encodePacked("cvin.delegate.", delegateType, delegate)), abi.encode(expiration));
        emit DelegateAdded(did, delegateType, delegate, expiration);
    }
    function validDelegate(bytes32 did, bytes32 delegateType, address delegate) external view returns (bool valid) {
        if (!_meta[did].exists) return false;
        uint256 exp = _delegates[did][delegateType][delegate];
        valid = exp != 0 && exp > block.timestamp && !_deactivated(did);
    }

    // ---- ISetC over the native registries ----
    function attestReputation(bytes32 did, uint8 score, string calldata evidenceURI) external {
        if (!_meta[did].exists) revert DIDNotFound();
        if (score > 100) revert NotAuthorized();
        reputation.giveFeedbackFor(msg.sender, _id(did), int128(uint128(score)), 0, "starred", "", "", evidenceURI, bytes32(0));
        emit ReputationAttested(did, bytes32(uint256(uint160(msg.sender))), score, evidenceURI);
    }
    function getReputation(bytes32 did) external view returns (uint8 meanScore, uint256 attestationCount) {
        address[] memory clients = reputation.getClients(_id(did));
        if (clients.length == 0) return (0, 0);
        (uint64 count, int128 v, ) = reputation.getSummary(_id(did), clients, "starred", "");
        int128 c = v < 0 ? int128(0) : (v > 100 ? int128(100) : v);
        return (uint8(uint128(c)), count);
    }
    function requestValidation(bytes32 did, bytes32 validationType, bytes calldata payload) external returns (bytes32 requestId) {
        if (!identity.isOwnerOrOperator(_id(did), msg.sender)) revert NotAuthorized();
        address validator = payload.length >= 20 ? address(bytes20(payload[0:20])) : msg.sender;
        requestId = keccak256(abi.encodePacked(did, validationType, payload, _nonce++));
        _reqDid[requestId] = did;
        validation.validationRequest(validator, _id(did), "", requestId);
        emit ValidationRequested(did, validationType, requestId);
    }
    function validationStatus(bytes32 requestId) external view returns (uint8 status) {
        (bool requested, bool responded) = validation.requestState(requestId);
        if (!requested) return 0;
        if (!responded) return 1;
        (, , uint8 response, , , ) = validation.getValidationStatus(requestId);
        return response >= 50 ? 2 : 3;
    }
}
