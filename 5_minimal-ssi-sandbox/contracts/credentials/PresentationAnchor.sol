// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IMinimalSSI} from "../interfaces/IMinimalSSI.sol";

/// @title PresentationAnchor — Set B overlay adapter (WO-9 / Stage 19)
/// @notice Anchors a presentation produced in an off-chain format — SD-JWT (RFC 9901), BBS+
///         (Data Integrity BBS cryptosuite), AnonCreds, or a Groth16 predicate — beside the
///         interface's F8 record. F8 commits that a presentation happened for a challenge; this
///         adapter commits WHICH FORMAT and the proof's hash, so a verifier (or auditor) can
///         later check that the proof bytes it holds are the ones presented, and a policy can
///         require a format (e.g. "unlinkable formats only at this verifier class", doc 03 §7).
///         The proof itself stays off-chain; nothing disclosed is written.
/// @dev One write per anchored presentation (optional; the hash path and BBS+ path in S19 run
///      without it). Status = revoked flag by the holder (withdraws a presentation from audit
///      scope) — the "status on-chain, proof off-chain" half of the adapter pattern.
contract PresentationAnchor {
    bytes32 public constant FMT_SD_JWT = keccak256("sd-jwt-vc/rfc9901");
    bytes32 public constant FMT_BBS = keccak256("bbs-2023/data-integrity");
    bytes32 public constant FMT_ANONCREDS = keccak256("anoncreds/v1-cl");
    bytes32 public constant FMT_GROTH16 = keccak256("groth16/bn128");

    struct Record { bytes32 holder; bytes32 format; bytes32 proofHash; bytes32 presentationId; uint64 anchoredAt; bool revoked; }
    error NotHolder();
    error Exists();
    event PresentationAnchored(bytes32 indexed anchorId, bytes32 indexed holder, bytes32 indexed format, bytes32 proofHash, bytes32 presentationId);
    event PresentationWithdrawn(bytes32 indexed anchorId);

    IMinimalSSI public immutable ssi;
    mapping(bytes32 => Record) private _rec;
    mapping(bytes32 => uint256) public countByFormat;

    constructor(IMinimalSSI ssi_) { ssi = ssi_; }

    function _controllerOf(bytes32 did) internal view returns (address c) {
        (bytes memory doc, ) = ssi.resolveDID(did);
        if (doc.length == 0) return address(0);
        (, c, ) = abi.decode(doc, (bytes32, address, uint256)); // sandbox document layout convention
    }

    /// @param presentationId the F8 presentationId this proof accompanies (bytes32(0) if the
    ///        presentation was never committed through F8 — the fully off-chain path)
    function anchorPresentation(bytes32 holder, bytes32 format, bytes32 proofHash, bytes32 presentationId) external returns (bytes32 anchorId) {
        if (_controllerOf(holder) != msg.sender) revert NotHolder();
        anchorId = keccak256(abi.encodePacked(holder, format, proofHash, presentationId));
        if (_rec[anchorId].anchoredAt != 0) revert Exists();
        _rec[anchorId] = Record(holder, format, proofHash, presentationId, uint64(block.timestamp), false);
        countByFormat[format] += 1;
        emit PresentationAnchored(anchorId, holder, format, proofHash, presentationId);
    }

    function withdraw(bytes32 anchorId) external {
        Record storage r = _rec[anchorId];
        if (r.anchoredAt == 0 || _controllerOf(r.holder) != msg.sender) revert NotHolder();
        if (!r.revoked) { r.revoked = true; emit PresentationWithdrawn(anchorId); }
    }

    /// @notice Verifier/auditor check: does the proof I hold match an anchored presentation by this holder in this format?
    function verifyAnchored(bytes32 holder, bytes32 format, bytes32 proofHash, bytes32 presentationId)
        external view returns (bool anchored, bool withdrawn, uint64 anchoredAt)
    {
        Record storage r = _rec[keccak256(abi.encodePacked(holder, format, proofHash, presentationId))];
        return (r.anchoredAt != 0, r.revoked, r.anchoredAt);
    }
}
