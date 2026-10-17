// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {IMinimalSSI} from "../interfaces/IMinimalSSI.sol";

/// @title O2_ERC721
/// @notice Token-as-identity option: a soulbound ERC-721 token IS the DID (EIP-5192 pattern).
/// @dev Native mechanics, per CLAUDE.md rule 2:
///      * createDID actually mints; tokenId = uint256(did); `ownerOf` is the resolution
///        primitive and the controller.
///      * Transfers revert unconditionally (soulbound); approvals are therefore inert.
///      * Deactivation does NOT burn. DID Core §7.3 requires a deactivated DID to remain
///        resolvable with its flag set, and burn destroys resolvability — the structural
///        gap recorded for this option in Building Paths (O2 L4/L6). The flag lives in a
///        per-token mapping; the token persists as the historical record.
///      * Key management is per-token attribute state (ERC-721 has none natively).
///      * Set B is the shared anchor pattern (content hash on-chain, content off-chain),
///        as for every EVM option — the Set A/Set B finding.
///      resolveDID returns the same document layout as O1 — abi.encode(did, controller,
///      keyCount) — so the governance layer's controller adapter is reusable unchanged.
contract O2_ERC721 is ERC721, IMinimalSSI {
    struct Meta { uint256 created; uint256 updated; bool deactivated; uint256 versionId; uint256 keyCount; }
    struct Credential { bytes32 issuer; bytes32 subject; bytes32 contentHash; uint256 validUntil; bool revoked; bool exists; }

    error Soulbound();

    /// @dev ERC-721 attribute record (event-sourced detail; value kept off-chain by indexers).
    event DIDAttributeChanged(bytes32 indexed did, bytes32 indexed key, bytes value, uint256 validTo);
    /// @dev EIP-5192: emitted at mint to signal the token is locked.
    event Locked(uint256 tokenId);

    mapping(uint256 => Meta) private _meta;
    mapping(bytes32 => Credential) private _creds;
    mapping(bytes32 => mapping(bytes32 => bool)) private _keys;
    mapping(bytes32 => mapping(bytes32 => mapping(address => uint256))) private _delegates;
    mapping(bytes32 => bool) private _usedChallenges;
    uint256 private _nonce;

    constructor() ERC721("CVIN Vehicle Identity", "CVID") {}

    // ---- soulbound enforcement (native ERC-721 hook) ----
    function _update(address to, uint256 tokenId, address auth) internal override returns (address) {
        address from = _ownerOf(tokenId);
        if (from != address(0)) revert Soulbound(); // any transfer or burn
        return super._update(to, tokenId, auth);
    }

    function _exists(bytes32 did) internal view returns (bool) { return _ownerOf(uint256(did)) != address(0); }

    modifier onlyController(bytes32 did) {
        if (!_exists(did)) revert DIDNotFound();
        if (msg.sender != _ownerOf(uint256(did))) revert NotAuthorized();
        _;
    }
    modifier active(bytes32 did) {
        if (_meta[uint256(did)].deactivated) revert DIDAlreadyDeactivated();
        _;
    }

    // ---- DID Lifecycle ----

    function createDID(address controller) external returns (bytes32 did) {
        did = keccak256(abi.encodePacked(controller, block.chainid, _nonce++, "erc721"));
        uint256 tokenId = uint256(did);
        _mint(controller, tokenId); // native mint; soulbound from here on
        _meta[tokenId] = Meta(block.timestamp, block.timestamp, false, 1, 1); // owner key implicit
        emit Locked(tokenId);
        emit DIDCreated(did, controller, block.timestamp);
    }

    function resolveDID(bytes32 did) external view returns (bytes memory document, bytes memory metadata) {
        if (!_exists(did)) return (bytes(""), bytes(""));
        Meta storage m = _meta[uint256(did)];
        document = abi.encode(did, _ownerOf(uint256(did)), m.keyCount);
        metadata = abi.encode(DIDDocumentMetadata(m.created, m.updated, m.deactivated, m.versionId));
    }

    function updateDID(bytes32 did, bytes32 key, bytes calldata value, uint256 validity)
        external onlyController(did) active(did)
    {
        Meta storage m = _meta[uint256(did)];
        m.updated = block.timestamp;
        m.versionId += 1;
        emit DIDAttributeChanged(did, key, value, block.timestamp + validity);
        emit DIDUpdated(did, key, block.timestamp);
    }

    function deactivateDID(bytes32 did) external onlyController(did) active(did) {
        Meta storage m = _meta[uint256(did)];
        m.deactivated = true;
        m.updated = block.timestamp;
        emit DIDDeactivated(did, block.timestamp);
    }

    // ---- Credential Operations (shared anchor pattern) ----

    function issueCredential(bytes32 issuer, bytes32 subject, bytes32 credentialHash, uint256 validUntil)
        external onlyController(issuer) active(issuer)
        returns (bytes32 credentialId)
    {
        if (!_exists(subject)) revert DIDNotFound();
        credentialId = keccak256(abi.encodePacked(issuer, subject, credentialHash, _nonce++));
        _creds[credentialId] = Credential(issuer, subject, credentialHash, validUntil, false, true);
        emit CredentialIssued(credentialId, issuer, subject);
    }

    function verifyCredential(bytes32 credentialId)
        external view returns (bool valid, bytes32 issuer, bool revoked, bool expired)
    {
        Credential storage c = _creds[credentialId];
        if (!c.exists) return (false, bytes32(0), false, false);
        revoked = c.revoked;
        expired = c.validUntil != 0 && block.timestamp > c.validUntil;
        valid = !revoked && !expired && !_meta[uint256(c.issuer)].deactivated;
        issuer = c.issuer;
    }

    function revokeCredential(bytes32 credentialId) external {
        Credential storage c = _creds[credentialId];
        if (!c.exists) revert CredentialNotFound();
        if (msg.sender != _ownerOf(uint256(c.issuer))) revert NotAuthorized();
        if (!c.revoked) { c.revoked = true; emit CredentialRevokedEvent(credentialId, block.timestamp); }
    }

    function createPresentation(bytes32 holder, bytes32[] calldata credentialIds, bytes32 challenge, string calldata domain)
        external onlyController(holder) active(holder)
        returns (bytes32 presentationId)
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

    // ---- Key Management (per-token attributes) ----

    function addVerificationMethod(bytes32 did, bytes32 keyType, bytes calldata publicKey)
        external onlyController(did) active(did)
        returns (bytes32 keyId)
    {
        keyId = keccak256(abi.encodePacked(did, keyType, publicKey));
        if (!_keys[did][keyId]) { _keys[did][keyId] = true; _meta[uint256(did)].keyCount += 1; }
        emit VerificationMethodAdded(did, keyId, keyType);
    }

    function removeVerificationMethod(bytes32 did, bytes32 keyId) external onlyController(did) active(did) {
        if (!_keys[did][keyId]) revert NotAuthorized();
        if (_meta[uint256(did)].keyCount <= 1) revert NotAuthorized();
        _keys[did][keyId] = false;
        _meta[uint256(did)].keyCount -= 1;
        emit VerificationMethodRemoved(did, keyId);
    }

    function addDelegate(bytes32 did, bytes32 delegateType, address delegate, uint256 validity)
        external onlyController(did) active(did)
    {
        uint256 expiration = block.timestamp + validity;
        _delegates[did][delegateType][delegate] = expiration;
        emit DelegateAdded(did, delegateType, delegate, expiration);
    }

    function validDelegate(bytes32 did, bytes32 delegateType, address delegate) external view returns (bool valid) {
        uint256 exp = _delegates[did][delegateType][delegate];
        valid = exp != 0 && exp > block.timestamp && !_meta[uint256(did)].deactivated;
    }
}
