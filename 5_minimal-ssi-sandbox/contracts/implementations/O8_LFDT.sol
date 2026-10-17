// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IMinimalSSI} from "../interfaces/IMinimalSSI.sol";

/// @title O8_LFDT — Indy-on-Besu (did:indy:besu) adapter
/// @notice Indy ledger semantics in Solidity, following the hyperledger/indy-besu contract
///         layout (read 2026-10-17): IndyDidRegistry {createDid(identity, document),
///         updateDid, deactivateDid, resolveDid → DidRecord{document, metadata{owner, created,
///         updated, versionId, deactivated}}}, SchemaRegistry {createSchema}, Credential-
///         DefinitionRegistry {createCredentialDefinition}, RevocationRegistry {create-
///         RevocationRegistryDefinition, createRevocationRegistryEntry}.
/// @dev Indy transaction type → IMinimalSSI function (the WO-3 mapping):
///      | NYM (createDid)                      | F1 createDID        | identity address = nym; document bytes stored |
///      | GET_NYM / resolveDid                 | F2 resolveDID       | DidRecord.document + metadata                  |
///      | ATTRIB / updateDid                   | F3 updateDID        | document rewritten (Indy stores the whole doc) |
///      | NYM role=null / deactivateDid        | F4 deactivateDID    | metadata.deactivated                           |
///      | SCHEMA + CLAIM_DEF (lazy, per issuer)| F5 issueCredential  | NO per-credential hash on-ledger: AnonCreds    |
///      |   + REVOC_REG_DEF index allocation   |                     | anchors the credential DEFINITION only; the    |
///      |                                      |                     | credential is bound to it by the issuer's      |
///      |                                      |                     | signature off-ledger (doc 01 §3.7)             |
///      | REVOC_REG_ENTRY (accumulator delta)  | F7 revokeCredential | revoked index set in the issuer's registry      |
///      | GET_REVOC_REG_DELTA                  | F6 verifyCredential | revoked bit + validUntil (sandbox index)       |
///      | — (no Indy equivalent)               | F8 createPresentation | anchor pattern; AnonCreds presentations are   |
///      |                                      |                     | fully off-ledger (the Set B ceiling, unreached |
///      |                                      |                     | by any on-chain function)                      |
///      | verkey in DID doc                    | F9/F10              | document rewrite (updateDid)                   |
///      | — (no delegation in did:indy)        | F11/F12             | sandbox-side, annotated non-native             |
///      The interface demands a credentialId and a validity for F5; the sandbox index
///      (issuer, subject, validUntil, revIndex) carries those. The content hash is NOT stored —
///      the one option where F5 anchors nothing credential-specific. Admission to the suite
///      therefore tests the index, not an Indy write; FINDINGS records this as the designed gap.
///      resolveDID returns the O1 document layout (did, controller, keyCount) as `document`.
contract O8_LFDT is IMinimalSSI {
    // ---- IndyDidRegistry ----
    struct DidMetadata { address owner; uint256 created; uint256 updated; uint256 versionId; bool deactivated; }
    struct DidRecord { bytes document; DidMetadata metadata; bool exists; uint256 keyCount; }
    event DIDCreatedIndy(address identity);
    event DIDUpdatedIndy(address identity);
    event DIDDeactivatedIndy(address identity);
    mapping(address => DidRecord) private _dids;

    // ---- SchemaRegistry / CredentialDefinitionRegistry (one lazily-created pair per issuer) ----
    struct SchemaRecord { bytes schema; string issuerId; uint256 created; bool exists; }
    struct CredDefRecord { bytes credDef; bytes32 schemaId; string issuerId; uint256 created; bool exists; }
    event SchemaCreated(bytes32 schemaId, address identity);
    event CredentialDefinitionCreated(bytes32 credentialDefinitionId, address identity);
    mapping(bytes32 => SchemaRecord) private _schemas;
    mapping(bytes32 => CredDefRecord) private _credDefs;
    mapping(address => bytes32) private _issuerCredDef;

    // ---- RevocationRegistry ----
    struct RevRegDef { bytes32 credDefId; uint256 maxCredNum; uint256 issued; uint256 created; bool exists; }
    event RevocationRegistryDefinitionCreated(bytes32 revocationRegistryDefinitionId, address identity);
    event RevocationRegistryEntryCreated(bytes32 revocationRegistryDefinitionId, uint256[] issued, uint256[] revoked, bytes32 currentAccumulator);
    mapping(bytes32 => RevRegDef) private _revRegs;
    mapping(bytes32 => mapping(uint256 => bool)) private _revoked; // revRegDefId => index => revoked
    mapping(bytes32 => bytes32) private _accumulator;

    // ---- sandbox index (interface obligations Indy does not carry) ----
    struct CredIndex { bytes32 issuer; bytes32 subject; uint256 validUntil; bytes32 revRegDefId; uint256 revIndex; bool exists; }
    mapping(bytes32 => CredIndex) private _creds;
    mapping(bytes32 => mapping(bytes32 => mapping(address => uint256))) private _delegates; // non-native
    mapping(bytes32 => mapping(bytes32 => bool)) private _keys;
    mapping(bytes32 => bool) private _usedChallenges;
    uint256 private _nonce;

    function _nym(bytes32 did) internal pure returns (address) { return address(uint160(uint256(did))); }
    function _doc(bytes32 did, DidRecord storage r) internal view returns (bytes memory) { return abi.encode(did, r.metadata.owner, r.keyCount); }

    modifier onlyController(bytes32 did) {
        DidRecord storage r = _dids[_nym(did)];
        if (!r.exists) revert DIDNotFound();
        if (msg.sender != r.metadata.owner) revert NotAuthorized();
        _;
    }
    modifier active(bytes32 did) { if (_dids[_nym(did)].metadata.deactivated) revert DIDAlreadyDeactivated(); _; }

    // ---- F1–F4: NYM / ATTRIB ----
    function createDID(address controller) external returns (bytes32 did) {
        address nym = address(uint160(uint256(keccak256(abi.encodePacked(controller, block.chainid, _nonce++, "indy")))));
        did = bytes32(uint256(uint160(nym)));
        DidRecord storage r = _dids[nym];
        r.metadata = DidMetadata(controller, block.timestamp, block.timestamp, 1, false);
        r.exists = true; r.keyCount = 1;
        r.document = _doc(did, r);           // Indy stores the document bytes
        emit DIDCreatedIndy(nym);
        emit DIDCreated(did, controller, block.timestamp);
    }
    function resolveDID(bytes32 did) external view returns (bytes memory document, bytes memory metadata) {
        DidRecord storage r = _dids[_nym(did)];
        if (!r.exists) return (bytes(""), bytes(""));
        document = r.document;
        metadata = abi.encode(DIDDocumentMetadata(r.metadata.created, r.metadata.updated, r.metadata.deactivated, r.metadata.versionId));
    }
    function updateDID(bytes32 did, bytes32 key, bytes calldata value, uint256 validity) external onlyController(did) active(did) {
        DidRecord storage r = _dids[_nym(did)];
        r.document = abi.encode(did, r.metadata.owner, r.keyCount, key, value, block.timestamp + validity); // ATTRIB: document rewrite
        r.metadata.updated = block.timestamp; r.metadata.versionId += 1;
        emit DIDUpdatedIndy(_nym(did));
        emit DIDUpdated(did, key, block.timestamp);
    }
    function deactivateDID(bytes32 did) external onlyController(did) active(did) {
        DidRecord storage r = _dids[_nym(did)];
        r.metadata.deactivated = true; r.metadata.updated = block.timestamp;
        emit DIDDeactivatedIndy(_nym(did));
        emit DIDDeactivated(did, block.timestamp);
    }

    // ---- F5–F7: SCHEMA / CLAIM_DEF / REVOC_REG ----
    function _ensureCredDef(bytes32 issuer) internal returns (bytes32 revRegDefId) {
        address nym = _nym(issuer);
        bytes32 cd = _issuerCredDef[nym];
        if (cd == bytes32(0)) {
            bytes32 schemaId = keccak256(abi.encodePacked("schema", nym));
            _schemas[schemaId] = SchemaRecord(abi.encode("cvin.credential.v1"), string(abi.encodePacked("did:indy:besu:", nym)), block.timestamp, true);
            emit SchemaCreated(schemaId, nym);
            cd = keccak256(abi.encodePacked("creddef", nym));
            _credDefs[cd] = CredDefRecord(abi.encode("CL", schemaId), schemaId, "", block.timestamp, true); // public key material would live here
            emit CredentialDefinitionCreated(cd, nym);
            _issuerCredDef[nym] = cd;
            revRegDefId = keccak256(abi.encodePacked("revreg", cd));
            _revRegs[revRegDefId] = RevRegDef(cd, type(uint256).max, 0, block.timestamp, true);
            _accumulator[revRegDefId] = keccak256(abi.encodePacked(revRegDefId, uint256(0)));
            emit RevocationRegistryDefinitionCreated(revRegDefId, nym);
        } else {
            revRegDefId = keccak256(abi.encodePacked("revreg", cd));
        }
    }
    function issueCredential(bytes32 issuer, bytes32 subject, bytes32 credentialHash, uint256 validUntil) external onlyController(issuer) active(issuer) returns (bytes32 credentialId) {
        if (!_dids[_nym(subject)].exists) revert DIDNotFound();
        bytes32 rr = _ensureCredDef(issuer);
        uint256 idx = ++_revRegs[rr].issued;                 // index allocation; credentialHash is deliberately NOT stored
        credentialId = keccak256(abi.encodePacked(issuer, subject, credentialHash, _nonce++));
        _creds[credentialId] = CredIndex(issuer, subject, validUntil, rr, idx, true);
        uint256[] memory issued = new uint256[](1); issued[0] = idx;
        emit RevocationRegistryEntryCreated(rr, issued, new uint256[](0), _accumulator[rr]);
        emit CredentialIssued(credentialId, issuer, subject);
    }
    function verifyCredential(bytes32 credentialId) external view returns (bool valid, bytes32 issuer, bool revoked, bool expired) {
        CredIndex storage c = _creds[credentialId];
        if (!c.exists) return (false, bytes32(0), false, false);
        revoked = _revoked[c.revRegDefId][c.revIndex];
        expired = c.validUntil != 0 && block.timestamp > c.validUntil;
        valid = !revoked && !expired && !_dids[_nym(c.issuer)].metadata.deactivated;
        issuer = c.issuer;
    }
    function revokeCredential(bytes32 credentialId) external {
        CredIndex storage c = _creds[credentialId];
        if (!c.exists) revert CredentialNotFound();
        if (msg.sender != _dids[_nym(c.issuer)].metadata.owner) revert NotAuthorized();
        if (!_revoked[c.revRegDefId][c.revIndex]) {
            _revoked[c.revRegDefId][c.revIndex] = true;
            _accumulator[c.revRegDefId] = keccak256(abi.encodePacked(_accumulator[c.revRegDefId], c.revIndex)); // accumulator delta (stand-in)
            uint256[] memory rev = new uint256[](1); rev[0] = c.revIndex;
            emit RevocationRegistryEntryCreated(c.revRegDefId, new uint256[](0), rev, _accumulator[c.revRegDefId]);
            emit CredentialRevokedEvent(credentialId, block.timestamp);
        }
    }
    function createPresentation(bytes32 holder, bytes32[] calldata credentialIds, bytes32 challenge, string calldata domain) external onlyController(holder) active(holder) returns (bytes32 presentationId) {
        if (_usedChallenges[challenge]) revert InvalidCredential();
        for (uint256 i = 0; i < credentialIds.length; i++) {
            CredIndex storage c = _creds[credentialIds[i]];
            if (!c.exists) revert CredentialNotFound();
            if (c.subject != holder) revert NotAuthorized();
            if (_revoked[c.revRegDefId][c.revIndex]) revert CredentialRevoked();
            if (c.validUntil != 0 && block.timestamp > c.validUntil) revert CredentialExpired();
        }
        _usedChallenges[challenge] = true;
        presentationId = keccak256(abi.encode(holder, credentialIds, challenge, domain));
        emit PresentationCreated(presentationId, holder, challenge);
    }

    // ---- F9–F12 ----
    function addVerificationMethod(bytes32 did, bytes32 keyType, bytes calldata publicKey) external onlyController(did) active(did) returns (bytes32 keyId) {
        keyId = keccak256(abi.encodePacked(did, keyType, publicKey));
        DidRecord storage r = _dids[_nym(did)];
        if (!_keys[did][keyId]) { _keys[did][keyId] = true; r.keyCount += 1; r.document = _doc(did, r); r.metadata.versionId += 1; emit DIDUpdatedIndy(_nym(did)); }
        emit VerificationMethodAdded(did, keyId, keyType);
    }
    function removeVerificationMethod(bytes32 did, bytes32 keyId) external onlyController(did) active(did) {
        DidRecord storage r = _dids[_nym(did)];
        if (!_keys[did][keyId]) revert NotAuthorized();
        if (r.keyCount <= 1) revert NotAuthorized();
        _keys[did][keyId] = false; r.keyCount -= 1; r.document = _doc(did, r); r.metadata.versionId += 1;
        emit DIDUpdatedIndy(_nym(did));
        emit VerificationMethodRemoved(did, keyId);
    }
    function addDelegate(bytes32 did, bytes32 delegateType, address delegate, uint256 validity) external onlyController(did) active(did) {
        uint256 expiration = block.timestamp + validity;
        _delegates[did][delegateType][delegate] = expiration; // non-native: did:indy has no delegation
        emit DelegateAdded(did, delegateType, delegate, expiration);
    }
    function validDelegate(bytes32 did, bytes32 delegateType, address delegate) external view returns (bool valid) {
        uint256 exp = _delegates[did][delegateType][delegate];
        valid = exp != 0 && exp > block.timestamp && !_dids[_nym(did)].metadata.deactivated;
    }

    // ---- Indy-native reads ----
    function resolveDid(address identity) external view returns (bytes memory document, DidMetadata memory metadata) { DidRecord storage r = _dids[identity]; return (r.document, r.metadata); }
    function resolveCredentialDefinition(bytes32 id) external view returns (bytes memory credDef, bytes32 schemaId, bool exists) { CredDefRecord storage c = _credDefs[id]; return (c.credDef, c.schemaId, c.exists); }
    function currentAccumulator(bytes32 revRegDefId) external view returns (bytes32) { return _accumulator[revRegDefId]; }
    function issuerCredDef(bytes32 issuer) external view returns (bytes32) { return _issuerCredDef[_nym(issuer)]; }
}
