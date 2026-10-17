// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IMinimalSSI} from "../interfaces/IMinimalSSI.sol";
import {IControllerAdapter} from "../governance/IControllerAdapter.sol";

/// @title BatchAnchorRegistry (scenario S17)
/// @notice A dedicated batch anchor beside the interface. S8 showed that anchoring a
///         Merkle root *through F5* costs the same as one credential (130,151 gas) and
///         gives up per-leaf verifiability on-chain. This contract does two things the
///         F5 route cannot: it stores the root under a batch id with the issuer DID, and
///         it verifies inclusion of a leaf on-chain (a view). Per-leaf revocation is
///         still absent — that belongs to a status list or accumulator (doc 01 §3, 02 §6).
///
/// @dev Leaves are the typed credential anchors (keccak(abi.encode(type, schema, content))).
///      Pair hashing sorts the two children so proofs need no direction bits — the same
///      rule as `merkleRoot` in scenarios/run_vid_lifecycle.js.
contract BatchAnchorRegistry {
    struct Batch { bytes32 root; bytes32 issuer; uint32 leafCount; uint64 anchoredAt; bool revoked; }

    error NotAuthorized();
    error BatchExists();

    event BatchAnchored(bytes32 indexed batchId, bytes32 indexed issuer, bytes32 root, uint32 leafCount);
    event BatchRevoked(bytes32 indexed batchId, uint256 timestamp);

    IControllerAdapter public immutable adapter;
    mapping(bytes32 => Batch) private _batches;

    constructor(IControllerAdapter adapter_) { adapter = adapter_; }

    /// @notice Anchor one root for `leafCount` credentials, acting as `issuerDid`.
    function anchorBatch(bytes32 issuerDid, bytes32 batchId, bytes32 root, uint32 leafCount) external {
        if (!adapter.isActive(issuerDid) || adapter.controllerOf(issuerDid) != msg.sender) revert NotAuthorized();
        if (_batches[batchId].anchoredAt != 0) revert BatchExists();
        _batches[batchId] = Batch(root, issuerDid, leafCount, uint64(block.timestamp), false);
        emit BatchAnchored(batchId, issuerDid, root, leafCount);
    }

    /// @notice Whole-batch revocation (the only granularity a root anchor offers).
    function revokeBatch(bytes32 batchId) external {
        Batch storage b = _batches[batchId];
        if (b.anchoredAt == 0 || adapter.controllerOf(b.issuer) != msg.sender) revert NotAuthorized();
        if (!b.revoked) { b.revoked = true; emit BatchRevoked(batchId, block.timestamp); }
    }

    function batch(bytes32 batchId) external view returns (bytes32 root, bytes32 issuer, uint32 leafCount, uint64 anchoredAt, bool revoked) {
        Batch storage b = _batches[batchId];
        return (b.root, b.issuer, b.leafCount, b.anchoredAt, b.revoked);
    }

    /// @notice On-chain inclusion check (view; never reverts). `proof` lists sibling hashes leaf→root.
    function verifyInclusion(bytes32 batchId, bytes32 leaf, bytes32[] calldata proof)
        external view returns (bool included, bool batchRevoked, bytes32 issuer)
    {
        Batch storage b = _batches[batchId];
        if (b.anchoredAt == 0) return (false, false, bytes32(0));
        bytes32 h = leaf;
        for (uint256 i = 0; i < proof.length; i++) {
            bytes32 p = proof[i];
            h = h < p ? keccak256(abi.encodePacked(h, p)) : keccak256(abi.encodePacked(p, h));
        }
        return (h == b.root, b.revoked, b.issuer);
    }
}
