// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title IControllerAdapter
/// @notice Resolves the controlling address of a DID for a specific IMinimalSSI
///         implementation. IMinimalSSI deliberately returns an opaque DID document
///         (bytes) from resolveDID, so "who controls this DID" is implementation-
///         specific. Governance contracts that must authorise actions *by a DID*
///         (rather than by an address) therefore go through an adapter, one per
///         option (O1..O8). This keeps the governance layer implementation-agnostic
///         without altering the normative interface.
interface IControllerAdapter {
    /// @return controller The address currently authorised to act for `did`,
    ///         or address(0) if the DID does not exist.
    function controllerOf(bytes32 did) external view returns (address controller);

    /// @return active False if the DID is unknown or deactivated.
    function isActive(bytes32 did) external view returns (bool active);
}
