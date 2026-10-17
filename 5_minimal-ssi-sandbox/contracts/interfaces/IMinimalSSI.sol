// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title IMinimalSSI
/// @notice Minimal interface for W3C-compliant Self-Sovereign Identity.
/// @dev Twelve functions: DID lifecycle (1-4), credential operations (5-8),
///      key management (9-12). Set A = {1,2,3,4,9,10,11,12}; Set B = {5,6,7,8}.
///      Source: "Minimal Function Set for Blockchain-Based SSI" (CVIN-SC formal spec).
interface IMinimalSSI {

    struct DIDDocumentMetadata {
        uint256 created;
        uint256 updated;
        bool deactivated;
        uint256 versionId;
    }

    error NotAuthorized();
    error DIDNotFound();
    error DIDAlreadyDeactivated();
    error CredentialNotFound();
    error CredentialRevoked();
    error CredentialExpired();
    error InvalidCredential();

    event DIDCreated(bytes32 indexed did, address indexed controller, uint256 timestamp);
    event DIDUpdated(bytes32 indexed did, bytes32 indexed key, uint256 timestamp);
    event DIDDeactivated(bytes32 indexed did, uint256 timestamp);
    event CredentialIssued(bytes32 indexed credentialId, bytes32 indexed issuer, bytes32 indexed subject);
    event CredentialRevokedEvent(bytes32 indexed credentialId, uint256 timestamp);
    event PresentationCreated(bytes32 indexed presentationId, bytes32 indexed holder, bytes32 challenge);
    event VerificationMethodAdded(bytes32 indexed did, bytes32 indexed keyId, bytes32 keyType);
    event VerificationMethodRemoved(bytes32 indexed did, bytes32 indexed keyId);
    event DelegateAdded(bytes32 indexed did, bytes32 indexed delegateType, address indexed delegate, uint256 expiration);

    // ---- DID Lifecycle (Functions 1-4) ----
    function createDID(address controller) external returns (bytes32 did);
    function resolveDID(bytes32 did) external view returns (bytes memory document, bytes memory metadata);
    function updateDID(bytes32 did, bytes32 key, bytes calldata value, uint256 validity) external;
    function deactivateDID(bytes32 did) external;

    // ---- Credential Operations (Functions 5-8, Set B) ----
    function issueCredential(bytes32 issuer, bytes32 subject, bytes32 credentialHash, uint256 validUntil) external returns (bytes32 credentialId);
    function verifyCredential(bytes32 credentialId) external view returns (bool valid, bytes32 issuer, bool revoked, bool expired);
    function revokeCredential(bytes32 credentialId) external;
    function createPresentation(bytes32 holder, bytes32[] calldata credentialIds, bytes32 challenge, string calldata domain) external returns (bytes32 presentationId);

    // ---- Key Management (Functions 9-12) ----
    function addVerificationMethod(bytes32 did, bytes32 keyType, bytes calldata publicKey) external returns (bytes32 keyId);
    function removeVerificationMethod(bytes32 did, bytes32 keyId) external;
    function addDelegate(bytes32 did, bytes32 delegateType, address delegate, uint256 validity) external;
    function validDelegate(bytes32 did, bytes32 delegateType, address delegate) external view returns (bool valid);
}
