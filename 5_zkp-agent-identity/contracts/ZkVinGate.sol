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

/// @title IERC1056Owner
/// @notice Minimal view of an ERC-1056 registry: who owns an identity.
/// @custom:standard ERC-1056 Ethereum Lightweight Identity (https://github.com/ethereum/EIPs/issues/1056)
interface IERC1056Owner {
    /// @notice Current owner of `identity` (the identity itself until changed).
    /// @param identity The ERC-1056 identity address.
    /// @return The owner address.
    function identityOwner(address identity) external view returns (address);
}

/// @title IZkVinVerifier
/// @notice ABI of the snarkjs-generated Groth16Verifier for the ZK-VIN circuit (7 public signals).
interface IZkVinVerifier {
    /// @notice Verifies a Groth16 proof over BN254.
    /// @dev Returns false (does not revert) on an invalid proof or an out-of-field signal. `b` uses snarkjs's swapped G2 order.
    /// @param a Proof point A (G1).
    /// @param b Proof point B (G2).
    /// @param c Proof point C (G1).
    /// @param pub Public signals [nullifier, commitment, mfrRoot, minModelYear, region, scope, challenge].
    /// @return True if the pairing check passes.
    function verifyProof(uint256[2] calldata a, uint256[2][2] calldata b, uint256[2] calldata c, uint256[7] calldata pub)
        external view returns (bool);
}

/// @title ZkVinGate
/// @author CVIN research project
/// @notice Identity-dependent transaction gate: admits an action for an ERC-1056 identity only with a zero-knowledge
///         proof of knowing the opening (VIN, model year, region, salt) of the identity's anchored Poseidon commitment.
/// @dev The ZK-VIN circuit (circuits/zkvin.circom, ZkVin(4)) proves: Poseidon(packedVIN, modelYear, region, salt)
///      equals the commitment; the VIN's WMI is a leaf of the authorised-manufacturer Merkle tree (depth 4);
///      modelYear >= minModelYear; region matches; nullifier = Poseidon(salt, scope). The gate checks every public
///      signal against on-chain values, enforces one nullifier per scope, then calls the Groth16 verifier.
///      Hides the VIN, exact model year and manufacturer; the identity itself is public (no anonymity set).
///      Closes gap AR-5 of docs/phase2/focus/F1_onchain_storage_idtx/ANALYSIS.md. Deviations from the header text:
///      `governor` and `mfrRoot` are fixed at deployment and services cannot be deactivated.
/// @custom:standard Groth16 (J. Groth, "On the Size of Pairing-based Non-interactive Arguments", EUROCRYPT 2016, https://eprint.iacr.org/2016/260)
/// @custom:standard EIP-196 alt_bn128 add/mul precompiles (https://eips.ethereum.org/EIPS/eip-196)
/// @custom:standard EIP-197 alt_bn128 pairing precompile (https://eips.ethereum.org/EIPS/eip-197)
/// @custom:standard EIP-1108 alt_bn128 gas repricing (https://eips.ethereum.org/EIPS/eip-1108)
/// @custom:standard ERC-1056 Ethereum Lightweight Identity (https://github.com/ethereum/EIPs/issues/1056)
/// @custom:standard Poseidon hash (https://eprint.iacr.org/2019/458)
/// @custom:security Verifier keys come from an INSECURE single-party trusted setup with fixed entropy (circuits/build_circuit.sh): anyone can forge proofs. Research artefact only.
/// @custom:security `action` and `serviceId` are not bound into the proof: a mempool observer can front-run `admit` with the same proof and a different action (or a service with identical parameters), spending the nullifier.
/// @custom:security `challenge` is static per service (a session parameter, not a fresh nonce); replay is stopped only by the nullifier.
/// @custom:security A nullifier is never cleared: one admission per (salt, scope); a second needs re-anchoring with a new salt.
/// @custom:security No AR-6 equivalent: after an ERC-1056 ownership transfer the previous owner's commitment stays valid until the new owner re-anchors.
/// @custom:security Groth16 proofs are malleable; replay protection is correctly keyed on the nullifier, not on proof bytes.
/// @custom:see docs/smart-contracts/05-zkp-and-idtx.md (section 3.3)
/// @custom:see 5_zkp-agent-identity/test-contracts/zkvin_gate.test.js
contract ZkVinGate {
    /// @dev public signal layout fixed by circuits/zkvin.circom: [nullifier, commitment, mfrRoot, minModelYear, region, scope, challenge]
    ///      (the circuit output, the nullifier, comes first, then the public inputs).
    uint256 private constant NULLIFIER = 0;
    uint256 private constant COMMITMENT = 1;
    uint256 private constant MFR_ROOT = 2;
    uint256 private constant MIN_YEAR = 3;
    uint256 private constant REGION = 4;
    uint256 private constant SCOPE = 5;
    uint256 private constant CHALLENGE = 6;

    /// @notice Per-service verification policy, set by the governor.
    /// @dev Fields: scope (nullifier domain), minModelYear, region, challenge (static per service), active (always true once set).
    struct Service {
        uint256 scope;
        uint256 minModelYear;
        uint256 region;
        uint256 challenge;
        bool active;
    }

    /// @notice Phase 1 ERC-1056 registry used for ownership checks.
    IERC1056Owner public immutable registry;
    /// @notice Groth16 verifier for the ZK-VIN circuit.
    IZkVinVerifier public immutable verifier;
    /// @notice Deployer; the only account allowed to call `setService`. No setter: cannot be transferred.
    address public governor;
    /// @notice Merkle root of the authorised-manufacturer (WMI) set. Set only in the constructor.
    uint256 public mfrRoot;

    /// @notice Anchored Poseidon commitment per identity (0 = none).
    mapping(address => uint256) public commitmentOf;
    /// @notice Service policy by service id.
    mapping(bytes32 => Service) public services;
    /// @notice Whether a nullifier has been spent within a scope.
    mapping(uint256 => mapping(uint256 => bool)) public nullifierUsed; // scope => nullifier => used

    /// @notice Emitted when an identity's owner anchors or replaces its commitment.
    /// @param identity The ERC-1056 identity.
    /// @param commitment The Poseidon commitment.
    event CommitmentAnchored(address indexed identity, uint256 commitment);
    /// @notice Emitted when the governor creates or overwrites a service.
    /// @param serviceId Service identifier.
    /// @param scope Nullifier scope.
    /// @param minModelYear Minimum model year the proof must satisfy.
    /// @param region Required region code.
    /// @param challenge Challenge the proof must carry.
    event ServiceSet(bytes32 indexed serviceId, uint256 scope, uint256 minModelYear, uint256 region, uint256 challenge);
    /// @notice Emitted when a proof is accepted; this event is the gated action.
    /// @param identity The admitted identity.
    /// @param serviceId The service admitted to.
    /// @param nullifier The nullifier now spent in the service's scope.
    /// @param action Caller-chosen action tag (not bound into the proof).
    event Admitted(address indexed identity, bytes32 indexed serviceId, uint256 nullifier, bytes32 action);

    /// @notice Caller is not the identity's current ERC-1056 owner.
    error NotIdentityOwner();
    /// @notice Caller is not the governor.
    error NotGovernor();
    /// @notice The service id has not been set.
    error UnknownService();
    /// @notice A public signal does not equal the on-chain value it must equal.
    /// @param index Index of the mismatching public signal.
    error SignalMismatch(uint256 index);
    /// @notice The nullifier was already spent in this scope.
    error NullifierUsed();
    /// @notice The Groth16 verifier rejected the proof.
    error InvalidProof();

    /// @notice Deploys the gate; the deployer becomes the governor.
    /// @param registry_ ERC-1056 registry.
    /// @param verifier_ Groth16 verifier for the ZK-VIN circuit.
    /// @param mfrRoot_ Authorised-manufacturer Merkle root (fixed for the contract's lifetime).
    constructor(IERC1056Owner registry_, IZkVinVerifier verifier_, uint256 mfrRoot_) {
        registry = registry_;
        verifier = verifier_;
        governor = msg.sender;
        mfrRoot = mfrRoot_;
    }

    /// @notice Anchors (or overwrites) the Poseidon commitment for an identity.
    /// @dev Only the identity's current ERC-1056 owner. Anchoring 0 effectively disables admission for the identity.
    /// @param identity The ERC-1056 identity.
    /// @param commitment Poseidon(packedVIN, modelYear, region, salt).
    function anchorCommitment(address identity, uint256 commitment) external {
        if (registry.identityOwner(identity) != msg.sender) revert NotIdentityOwner();
        commitmentOf[identity] = commitment;
        emit CommitmentAnchored(identity, commitment);
    }

    /// @notice Creates or overwrites a service policy (always active).
    /// @dev Governor only.
    /// @param serviceId Service identifier.
    /// @param scope Nullifier scope.
    /// @param minModelYear Minimum model year.
    /// @param region Required region code.
    /// @param challenge Challenge the proof must carry.
    function setService(bytes32 serviceId, uint256 scope, uint256 minModelYear, uint256 region, uint256 challenge) external {
        if (msg.sender != governor) revert NotGovernor();
        services[serviceId] = Service(scope, minModelYear, region, challenge, true);
        emit ServiceSet(serviceId, scope, minModelYear, region, challenge);
    }

    /// @notice Admits `identity` to `serviceId` given a valid ZK-VIN proof; callable by anyone (owner, agent, relayer).
    /// @dev Checks, in order: service active; pub[1] equals the non-zero anchored commitment; pub[2..6] equal mfrRoot,
    ///      minModelYear, region, scope, challenge; nullifier fresh in scope; verifier accepts. Then marks the
    ///      nullifier spent and emits `Admitted`. The external call to the trusted immutable verifier is a view call.
    /// @param identity The ERC-1056 identity whose commitment the proof opens.
    /// @param serviceId The service to be admitted to.
    /// @param a Proof point A.
    /// @param b Proof point B (snarkjs calldata order).
    /// @param c Proof point C.
    /// @param pub Public signals [nullifier, commitment, mfrRoot, minModelYear, region, scope, challenge].
    /// @param action Action tag emitted with the admission.
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
