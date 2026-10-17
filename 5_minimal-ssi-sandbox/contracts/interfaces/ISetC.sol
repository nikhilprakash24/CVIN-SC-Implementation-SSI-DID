// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title ISetC — Extended agent trust layer (beyond the 12 minimal functions)
/// @notice Derived from ERC-8004 patterns (Identity/Reputation/Validation
///         registries; mainnet since Jan 2026). Optional: not required for
///         IMinimalSSI compliance. Exercised by agentic scenarios (Stage 31)
///         and Set C benchmarking.
interface ISetC {
    event ReputationAttested(bytes32 indexed did, bytes32 indexed attester, uint8 score, string evidenceURI);
    event ValidationRequested(bytes32 indexed did, bytes32 indexed validationType, bytes32 requestId);

    function attestReputation(bytes32 did, uint8 score, string calldata evidenceURI) external;
    function getReputation(bytes32 did) external view returns (uint8 meanScore, uint256 attestationCount);
    function requestValidation(bytes32 did, bytes32 validationType, bytes calldata payload) external returns (bytes32 requestId);
    function validationStatus(bytes32 requestId) external view returns (uint8 status);
}
