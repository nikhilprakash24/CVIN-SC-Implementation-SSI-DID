// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IMinimalSSI} from "../interfaces/IMinimalSSI.sol";
import {IControllerAdapter} from "./IControllerAdapter.sol";

/// @title O1ControllerAdapter
/// @notice Controller resolution for O1_ERC1056, whose resolveDID returns
///         document = abi.encode(did, controller, keyCount) and
///         metadata  = abi.encode(DIDDocumentMetadata).
/// @dev Read-only; every call is a view over F2 (resolveDID). Cost of this
///      adapter is therefore a read cost, never a write cost — which is the
///      point: governance authorisation is a *read path* over the identity
///      anchor (see HDA campaign doc 01 §4).
contract O1ControllerAdapter is IControllerAdapter {
    IMinimalSSI public immutable ssi;

    constructor(IMinimalSSI ssi_) {
        ssi = ssi_;
    }

    function controllerOf(bytes32 did) external view returns (address controller) {
        (bytes memory doc, ) = ssi.resolveDID(did);
        if (doc.length == 0) return address(0);
        (, controller, ) = abi.decode(doc, (bytes32, address, uint256));
    }

    function isActive(bytes32 did) external view returns (bool active) {
        (bytes memory doc, bytes memory meta) = ssi.resolveDID(did);
        if (doc.length == 0) return false;
        IMinimalSSI.DIDDocumentMetadata memory m = abi.decode(meta, (IMinimalSSI.DIDDocumentMetadata));
        return !m.deactivated;
    }
}
