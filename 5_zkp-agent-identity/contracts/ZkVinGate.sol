// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/*
 * ZkVinGate: an identity-dependent transaction (IDTx) whose dependency is KNOWLEDGE of what the identity committed
 * to, not equality with a public value. It closes the gap recorded as AR-5 in
 * docs/phase2/focus/F1_onchain_storage_idtx/ANALYSIS.md ("a knowledge-of-opening dependency would disclose the
 * opening or need a proof"): here it needs a proof, and discloses nothing but the predicate.
 *
 * Flow.
 *   1. The identity's ERC-1056 owner anchors a Poseidon commitment to (VIN, model year, region, salt).
 *   2. A governor publishes the authorised-manufacturer Merkle root and registers services, each with a scope,
 *      a minimum model year, a region and a current challenge.
 *   3. Anyone (the owner, the owner's agent, a relayer) submits `admit` with a ZK-VIN Groth16 proof. The gate
 *      checks that every public signal equals the on-chain value it must equal, that the nullifier is fresh in the
 *      service's scope, and that the proof verifies. Then the action runs (here: an event).
 *
 * What is public. The identity is named (this is an IDTx on a named identity), so its commitment is public and
 * a verifier knows which identity was admitted. What stays hidden: the VIN, the exact model year, the manufacturer.
 * Hiding *which* identity too needs a proof of membership in the set of anchored commitments (a Semaphore-style
 * anonymity set): Plan 1 to-do, not built here.
 *
 * Research artefact: the verifier's keys come from an INSECURE single-party setup (circuits/build_circuit.sh).
 */

interface IERC1056Owner {
    function identityOwner(address identity) external view returns (address);
}

interface IZkVinVerifier {
    function verifyProof(uint256[2] calldata a, uint256[2][2] calldata b, uint256[2] calldata c, uint256[7] calldata pub)
        external view returns (bool);
}

contract ZkVinGate {
    // public signal layout fixed by circuits/zkvin.circom: [nullifier, commitment, mfrRoot, minModelYear, region, scope, challenge]
    uint256 private constant NULLIFIER = 0;
    uint256 private constant COMMITMENT = 1;
    uint256 private constant MFR_ROOT = 2;
    uint256 private constant MIN_YEAR = 3;
    uint256 private constant REGION = 4;
    uint256 private constant SCOPE = 5;
    uint256 private constant CHALLENGE = 6;

    struct Service {
        uint256 scope;
        uint256 minModelYear;
        uint256 region;
        uint256 challenge;
        bool active;
    }

    IERC1056Owner public immutable registry;
    IZkVinVerifier public immutable verifier;
    address public governor;
    uint256 public mfrRoot;

    mapping(address => uint256) public commitmentOf;
    mapping(bytes32 => Service) public services;
    mapping(uint256 => mapping(uint256 => bool)) public nullifierUsed; // scope => nullifier => used

    event CommitmentAnchored(address indexed identity, uint256 commitment);
    event ServiceSet(bytes32 indexed serviceId, uint256 scope, uint256 minModelYear, uint256 region, uint256 challenge);
    event Admitted(address indexed identity, bytes32 indexed serviceId, uint256 nullifier, bytes32 action);

    error NotIdentityOwner();
    error NotGovernor();
    error UnknownService();
    error SignalMismatch(uint256 index);
    error NullifierUsed();
    error InvalidProof();

    constructor(IERC1056Owner registry_, IZkVinVerifier verifier_, uint256 mfrRoot_) {
        registry = registry_;
        verifier = verifier_;
        governor = msg.sender;
        mfrRoot = mfrRoot_;
    }

    function anchorCommitment(address identity, uint256 commitment) external {
        if (registry.identityOwner(identity) != msg.sender) revert NotIdentityOwner();
        commitmentOf[identity] = commitment;
        emit CommitmentAnchored(identity, commitment);
    }

    function setService(bytes32 serviceId, uint256 scope, uint256 minModelYear, uint256 region, uint256 challenge) external {
        if (msg.sender != governor) revert NotGovernor();
        services[serviceId] = Service(scope, minModelYear, region, challenge, true);
        emit ServiceSet(serviceId, scope, minModelYear, region, challenge);
    }

    function admit(
        address identity,
        bytes32 serviceId,
        uint256[2] calldata a,
        uint256[2][2] calldata b,
        uint256[2] calldata c,
        uint256[7] calldata pub,
        bytes32 action
    ) external {
        Service memory s = services[serviceId];
        if (!s.active) revert UnknownService();
        uint256 anchored = commitmentOf[identity];
        if (anchored == 0 || pub[COMMITMENT] != anchored) revert SignalMismatch(COMMITMENT);
        if (pub[MFR_ROOT] != mfrRoot) revert SignalMismatch(MFR_ROOT);
        if (pub[MIN_YEAR] != s.minModelYear) revert SignalMismatch(MIN_YEAR);
        if (pub[REGION] != s.region) revert SignalMismatch(REGION);
        if (pub[SCOPE] != s.scope) revert SignalMismatch(SCOPE);
        if (pub[CHALLENGE] != s.challenge) revert SignalMismatch(CHALLENGE);
        if (nullifierUsed[s.scope][pub[NULLIFIER]]) revert NullifierUsed();
        if (!verifier.verifyProof(a, b, c, pub)) revert InvalidProof();
        nullifierUsed[s.scope][pub[NULLIFIER]] = true;
        emit Admitted(identity, serviceId, pub[NULLIFIER], action);
    }
}
