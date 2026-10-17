// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ISetC} from "../interfaces/ISetC.sol";
import {IControllerAdapter} from "../governance/IControllerAdapter.sol";
import {EndorsementRegistry} from "../governance/EndorsementRegistry.sol";

/// @title SetCHarness — a HARNESS, not option O7.
/// @notice Minimal ISetC so that scenarios needing C1–C4 (S11, S16) can run before the
///         ERC-8004 option (O7, WO-2) exists. It is deliberately not an ERC-8004
///         implementation: no identity NFT, no mainnet registry fidelity. Its one design
///         choice that matters for the thesis argument (HDA doc 09 §4–§5) is that an
///         attester must be *entitled* to score: it must hold an endorsement for the
///         credential type `REPUTATION_ATTESTER` in the EndorsementRegistry. Without that
///         gate, reputation is Sybil-manufacturable; with it, the Sybil cost is the
///         endorsement cost. Gas measured on this harness must be labelled "harness", never
///         "ERC-8004".
contract SetCHarness is ISetC {
    bytes32 public constant REPUTATION_ATTESTER = keccak256("cvin.role.reputation-attester.v1");

    error NotAuthorized();
    error NotEntitled();

    struct Rep { uint256 sum; uint256 count; }
    struct Val { bytes32 did; bytes32 validationType; uint8 status; } // 0 none, 1 pending, 2 valid, 3 invalid

    IControllerAdapter public immutable adapter;
    EndorsementRegistry public immutable endorsements;
    bool public immutable gated; // false = ungated harness (the control in the Sybil experiment)

    mapping(bytes32 => Rep) private _rep;
    mapping(bytes32 => mapping(bytes32 => bool)) private _attested; // did => attester => already scored
    mapping(bytes32 => Val) private _val;
    uint256 private _nonce;

    event ValidationResolved(bytes32 indexed requestId, uint8 status);

    constructor(IControllerAdapter adapter_, EndorsementRegistry endorsements_, bool gated_) {
        adapter = adapter_; endorsements = endorsements_; gated = gated_;
    }

    /// @notice C1. `attester` is the DID msg.sender acts for. One score per (subject, attester).
    function attestReputationAs(bytes32 attester, bytes32 did, uint8 score, string calldata evidenceURI) external {
        if (adapter.controllerOf(attester) != msg.sender) revert NotAuthorized();
        if (gated) { (bool ok, ) = endorsements.isEndorsed(attester, REPUTATION_ATTESTER); if (!ok) revert NotEntitled(); }
        if (score > 100) revert NotAuthorized();
        Rep storage r = _rep[did];
        if (!_attested[did][attester]) { _attested[did][attester] = true; r.count += 1; r.sum += score; }
        emit ReputationAttested(did, attester, score, evidenceURI);
    }

    /// @dev ISetC's C1 signature has no attester parameter; the harness treats msg.sender's
    ///      address as an attester *address* only when ungated (no DID known). Gated mode
    ///      requires attestReputationAs.
    function attestReputation(bytes32 did, uint8 score, string calldata evidenceURI) external {
        if (gated) revert NotEntitled();
        bytes32 attester = bytes32(uint256(uint160(msg.sender)));
        if (score > 100) revert NotAuthorized();
        Rep storage r = _rep[did];
        if (!_attested[did][attester]) { _attested[did][attester] = true; r.count += 1; r.sum += score; }
        emit ReputationAttested(did, attester, score, evidenceURI);
    }

    /// @notice C2.
    function getReputation(bytes32 did) external view returns (uint8 meanScore, uint256 attestationCount) {
        Rep storage r = _rep[did];
        if (r.count == 0) return (0, 0);
        return (uint8(r.sum / r.count), r.count);
    }

    /// @notice C3. Anyone may request; payload is opaque (e.g. a zkML/TEE claim hash).
    function requestValidation(bytes32 did, bytes32 validationType, bytes calldata payload) external returns (bytes32 requestId) {
        requestId = keccak256(abi.encodePacked(did, validationType, keccak256(payload), _nonce++));
        _val[requestId] = Val(did, validationType, 1);
        emit ValidationRequested(did, validationType, requestId);
    }

    /// @notice Resolution hook (not in ISetC — FINDING: ISetC defines no validation-response write).
    ///         Only an endorsed REPUTATION_ATTESTER may resolve, acting as its DID.
    function resolveValidationAs(bytes32 validator, bytes32 requestId, bool valid) external {
        if (adapter.controllerOf(validator) != msg.sender) revert NotAuthorized();
        if (gated) { (bool ok, ) = endorsements.isEndorsed(validator, REPUTATION_ATTESTER); if (!ok) revert NotEntitled(); }
        Val storage v = _val[requestId];
        if (v.status != 1) revert NotAuthorized();
        v.status = valid ? 2 : 3;
        emit ValidationResolved(requestId, v.status);
    }

    /// @notice C4.
    function validationStatus(bytes32 requestId) external view returns (uint8 status) { return _val[requestId].status; }
}
