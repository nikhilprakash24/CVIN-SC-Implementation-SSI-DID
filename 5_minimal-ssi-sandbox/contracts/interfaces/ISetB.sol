// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title ISetB — Credential & presentation layer (4 functions: F5–F8)
/// @notice No ERC standard provides these natively (the central Set A/Set B
///         finding). Coverage ceiling reference: AnonCreds (native
///         createPresentation with ZKP selective disclosure). EVM options
///         satisfy Set B via the anchor pattern + pairing (JWT-VC, SD-JWT,
///         AnonCreds, BBS+).
interface ISetB {
    function issueCredential(bytes32 issuer, bytes32 subject, bytes32 credentialHash, uint256 validUntil) external returns (bytes32 credentialId);
    function verifyCredential(bytes32 credentialId) external view returns (bool valid, bytes32 issuer, bool revoked, bool expired);
    function revokeCredential(bytes32 credentialId) external;
    function createPresentation(bytes32 holder, bytes32[] calldata credentialIds, bytes32 challenge, string calldata domain) external returns (bytes32 presentationId);
}
