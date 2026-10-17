// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title ISetA — Identity-layer baseline (8 functions: F1–F4, F9–F12)
/// @notice DID lifecycle + key management. Directly evaluable against ERC
///         standards natively (Pass 1 scoring, /24). Subset of IMinimalSSI.
interface ISetA {
    function createDID(address controller) external returns (bytes32 did);
    function resolveDID(bytes32 did) external view returns (bytes memory document, bytes memory metadata);
    function updateDID(bytes32 did, bytes32 key, bytes calldata value, uint256 validity) external;
    function deactivateDID(bytes32 did) external;
    function addVerificationMethod(bytes32 did, bytes32 keyType, bytes calldata publicKey) external returns (bytes32 keyId);
    function removeVerificationMethod(bytes32 did, bytes32 keyId) external;
    function addDelegate(bytes32 did, bytes32 delegateType, address delegate, uint256 validity) external;
    function validDelegate(bytes32 did, bytes32 delegateType, address delegate) external view returns (bool valid);
}
