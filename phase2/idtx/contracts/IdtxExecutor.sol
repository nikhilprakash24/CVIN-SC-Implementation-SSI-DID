// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/*
 * Revised 2026-10-14 after the academic review (docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md): AR-4 (the
 * dependency is on the named identity, not on the caller: see `holds`), AR-5 ("registered-commitment
 * validity", not knowledge of a value), AR-6 (a commitment stops counting when its setter no longer owns
 * the identity).
 *
 * Identity-dependent transactions (IDTx): a prototype (Phase 2, focus F1, start of execution;
 * docs/phase2/focus/F1_onchain_storage_idtx/).
 *
 * Definition used here (F1 ANALYSIS §4.1, the review's §3.3): an IDTx is a transaction whose admissibility
 * or effect is a function of the state of an identity that the transaction names, evaluated during execution
 * from ledger state or from an attestation or proof the transaction carries. Authentication of the sender and
 * administration of the record the transaction itself modifies are excluded. The caller is deliberately not
 * part of the predicate: anyone (a keeper, an insurer, a toll system) may submit an IDTx; what decides is the
 * named identity's state.
 *
 * This prototype depends on an ERC-1056 registry (Phase 1's `EthereumDIDRegistry`, unchanged) and on a
 * small commitment store, because ERC-1056 keeps attributes in events only and no contract can read an
 * event (Phase 1 register #49). Three dependency kinds:
 *   Owner       identityOwner(identity) == party                      (registry state, plaintext)
 *   Delegate    validDelegate(identity, key, party)                   (registry state, time-bounded)
 *   Commitment  registered-commitment validity: the identity's owner registered `expected` under `key`,
 *               it has not expired, and the owner who set it still owns the identity. The commitment
 *               (a salted hash, or a ciphertext digest) is public; this proves no knowledge of the value
 *               behind it (AR-5). A knowledge-of-opening dependency would disclose the opening or need a proof.
 * Two continuations:
 *   execute(dep, action)        same transaction: the predicate and the action are atomic
 *   createIntent / fulfil       next transaction: an agent fulfils later, and the predicate is
 *                               re-evaluated at fulfilment, so a change between the two (owner
 *                               transfer, delegate revocation, commitment revocation) makes it fail
 *                               (no time-of-check to time-of-use gap on chain)
 * No number from this prototype is a result (Phase 2 principle 4); the measurement plan is F1 PLAN.
 */

/// @title IERC1056
/// @notice Subset of the ERC-1056 registry read by the IDTx prototype (Phase 1 `EthereumDIDRegistry`, unmodified).
/// @custom:standard ERC-1056 Ethereum Lightweight Identity (https://github.com/ethereum/EIPs/issues/1056)
interface IERC1056 {
    /// @notice Current owner of `identity`.
    /// @param identity The ERC-1056 identity.
    /// @return The owner address.
    function identityOwner(address identity) external view returns (address);
    /// @notice Whether `delegate` is an unexpired delegate of `identity` for `delegateType`.
    /// @param identity The ERC-1056 identity.
    /// @param delegateType Delegate type (e.g. "veriKey").
    /// @param delegate Candidate delegate.
    /// @return True while the delegation is valid (block.timestamp < validity).
    function validDelegate(address identity, bytes32 delegateType, address delegate) external view returns (bool);
}

/// @title IdentityCommitments
/// @author CVIN research project
/// @notice Identity-bound commitments in contract state, settable only by the identity's current owner.
/// @dev Exists because ERC-1056 keeps attributes in events only, which no contract can read (Phase 1 register #49).
///      A commitment counts only while unexpired and while its setter still owns the identity (AR-6).
///      It proves registration of a public digest, not knowledge of the value behind it (AR-5).
/// @custom:standard ERC-1056 Ethereum Lightweight Identity (https://github.com/ethereum/EIPs/issues/1056)
/// @custom:security A commitment (salted hash or ciphertext digest) is public; validity is not knowledge (AR-5).
/// @custom:see docs/smart-contracts/05-zkp-and-idtx.md (section 3.4)
/// @custom:see phase2/idtx/test/idtx.test.js
/// @custom:see phase2/idtx/mutate_idtx.sh (mutation probe)
contract IdentityCommitments {
    /// @notice ERC-1056 registry used for ownership checks.
    IERC1056 public immutable registry;
    /// @dev Commitment per (identity, key); read through `valueOf`.
    mapping(address => mapping(bytes32 => bytes32)) private _value;
    /// @notice Expiry timestamp per (identity, key).
    mapping(address => mapping(bytes32 => uint64)) public validUntil;
    /// @notice Owner at set time per (identity, key) (AR-6).
    mapping(address => mapping(bytes32 => address)) public setBy;   // AR-6: the owner at set time

    /// @notice Emitted when a commitment is set.
    /// @param identity The ERC-1056 identity.
    /// @param key Commitment key.
    /// @param commitment The commitment digest.
    /// @param validUntil Expiry timestamp.
    event CommitmentSet(address indexed identity, bytes32 indexed key, bytes32 commitment, uint64 validUntil);
    /// @notice Emitted when a commitment is revoked.
    /// @param identity The ERC-1056 identity.
    /// @param key Commitment key.
    event CommitmentRevoked(address indexed identity, bytes32 indexed key);

    /// @notice Binds the store to an ERC-1056 registry.
    /// @param registry_ The registry.
    constructor(IERC1056 registry_) {
        registry = registry_;
    }

    /// @notice Restricts to the identity's current ERC-1056 owner; reverts "not the identity owner".
    /// @param identity The ERC-1056 identity.
    modifier onlyIdentityOwner(address identity) {
        require(registry.identityOwner(identity) == msg.sender, "not the identity owner");
        _;
    }

    /// @notice Sets the commitment for (identity, key), recording the setter (AR-6).
    /// @dev Reverts on a zero commitment or a non-future expiry.
    /// @param identity The ERC-1056 identity.
    /// @param key Commitment key.
    /// @param commitment Non-zero commitment digest.
    /// @param until Expiry timestamp, strictly in the future.
    function setCommitment(address identity, bytes32 key, bytes32 commitment, uint64 until)
        external onlyIdentityOwner(identity)
    {
        require(commitment != bytes32(0), "empty commitment");
        require(until > block.timestamp, "already expired");
        _value[identity][key] = commitment;
        validUntil[identity][key] = until;
        setBy[identity][key] = msg.sender;
        emit CommitmentSet(identity, key, commitment, until);
    }

    /// @notice Deletes the commitment, its expiry and its setter for (identity, key).
    /// @param identity The ERC-1056 identity.
    /// @param key Commitment key.
    function revokeCommitment(address identity, bytes32 key) external onlyIdentityOwner(identity) {
        delete _value[identity][key];
        delete validUntil[identity][key];
        delete setBy[identity][key];
        emit CommitmentRevoked(identity, key);
    }

    /// @notice The commitment if it is still valid and its setter still owns the identity (AR-6), else zero.
    /// @param identity The ERC-1056 identity.
    /// @param key Commitment key.
    /// @return The commitment, or bytes32(0) if expired, unset, or set by a former owner.
    function valueOf(address identity, bytes32 key) external view returns (bytes32) {
        if (validUntil[identity][key] <= block.timestamp) return bytes32(0);
        if (registry.identityOwner(identity) != setBy[identity][key]) return bytes32(0);
        return _value[identity][key];
    }
}

/// @title IdtxExecutor
/// @author CVIN research project
/// @notice Identity-dependent transactions (IDTx): an action runs only if a predicate over a named ERC-1056
///         identity holds, either in the same transaction (`execute`) or at a later fulfilment (`createIntent`/`fulfil`).
/// @dev Three plaintext dependency kinds: Owner, Delegate (time-bounded), Commitment (registered-commitment validity).
///      The caller is never part of the predicate (AR-4). The predicate is re-evaluated at fulfilment, so there is no
///      on-chain time-of-check/time-of-use gap. Actions are events only (no external call, no value transfer).
///      Prototype: no number from it is a result (Phase 2 principle 4).
/// @custom:standard ERC-1056 Ethereum Lightweight Identity (https://github.com/ethereum/EIPs/issues/1056)
/// @custom:security Anyone can create intents; `_intents` can be spammed (storage growth paid by the spammer). `creator` is stored but never read.
/// @custom:security The Commitment kind proves no knowledge of the committed value (AR-5); see ZkVinGate for knowledge-of-opening.
/// @custom:security An out-of-range `fulfil(id)` reverts with panic 0x32.
/// @custom:see docs/smart-contracts/05-zkp-and-idtx.md (section 3.4)
/// @custom:see phase2/idtx/test/idtx.test.js
/// @custom:see phase2/idtx/mutate_idtx.sh (mutation probe)
contract IdtxExecutor {
    /// @notice Dependency kind evaluated by `holds`.
    enum Kind { Owner, Delegate, Commitment }

    /// @notice An identity predicate over a named ERC-1056 identity.
    struct Dependency {
        Kind kind;
        address identity;
        bytes32 key;       // delegate type (Delegate) or commitment key (Commitment); unused for Owner
        bytes32 expected;  // the expected commitment (Commitment); unused otherwise
        address party;     // the expected owner (Owner) or delegate (Delegate); unused for Commitment
    }

    /// @notice A pending next-transaction IDTx: dependency, action tag, deadline, creator and completion flag.
    struct Intent {
        Dependency dep;
        bytes32 action;
        uint64 deadline;
        address creator;
        bool done;
    }

    /// @notice ERC-1056 registry read by `holds`.
    IERC1056 public immutable registry;
    /// @notice Commitment store read for the Commitment kind.
    IdentityCommitments public immutable commitments;
    /// @dev Intents indexed by id (array position).
    Intent[] private _intents;

    /// @notice Emitted when an IDTx action runs (from `execute` or `fulfil`).
    /// @param action Action tag.
    /// @param identity The named identity.
    /// @param kind Dependency kind that held.
    /// @param caller The submitter (not part of the predicate).
    event Executed(bytes32 indexed action, address indexed identity, Kind kind, address caller);
    /// @notice Emitted when an intent is recorded.
    /// @param id Intent id.
    /// @param action Action tag.
    /// @param identity The named identity.
    /// @param deadline Last timestamp at which it can be fulfilled.
    event IntentCreated(uint256 indexed id, bytes32 indexed action, address indexed identity, uint64 deadline);
    /// @notice Emitted when an intent is fulfilled.
    /// @param id Intent id.
    /// @param keeper The fulfilling account.
    event IntentFulfilled(uint256 indexed id, address keeper);

    /// @notice Binds the executor to a registry and a commitment store.
    /// @param registry_ ERC-1056 registry.
    /// @param commitments_ Commitment store.
    constructor(IERC1056 registry_, IdentityCommitments commitments_) {
        registry = registry_;
        commitments = commitments_;
    }

    /// @notice The identity predicate, evaluated against current chain state. It does not involve msg.sender (AR-4).
    /// @dev Owner: identityOwner == party. Delegate: validDelegate(identity, key, party). Commitment: valueOf != 0 and == expected.
    /// @param d The dependency.
    /// @return True if the dependency holds now.
    function holds(Dependency memory d) public view returns (bool) {
        if (d.kind == Kind.Owner) return registry.identityOwner(d.identity) == d.party;
        if (d.kind == Kind.Delegate) return registry.validDelegate(d.identity, d.key, d.party);
        bytes32 v = commitments.valueOf(d.identity, d.key);
        return v != bytes32(0) && v == d.expected;
    }

    /// @notice Same-transaction IDTx: the action happens only if the predicate holds now.
    /// @dev Reverts "identity dependency not met" otherwise. Callable by anyone.
    /// @param d The dependency.
    /// @param action Action tag to emit.
    function execute(Dependency calldata d, bytes32 action) external {
        require(holds(d), "identity dependency not met");
        emit Executed(action, d.identity, d.kind, msg.sender);
    }

    /// @notice Next-transaction IDTx, step 1: record what is to happen and on which dependency.
    /// @param d The dependency to re-check at fulfilment.
    /// @param action Action tag.
    /// @param deadline Last fulfilment timestamp; must be in the future.
    /// @return id The new intent's id.
    function createIntent(Dependency calldata d, bytes32 action, uint64 deadline) external returns (uint256 id) {
        require(deadline > block.timestamp, "deadline passed");
        id = _intents.length;
        _intents.push(Intent(d, action, deadline, msg.sender, false));
        emit IntentCreated(id, action, d.identity, deadline);
    }

    /// @notice Next-transaction IDTx, step 2: any agent may fulfil; the predicate is re-evaluated here.
    /// @dev Reverts if already fulfilled, past the deadline, or the dependency no longer holds.
    /// @param id Intent id.
    function fulfil(uint256 id) external {
        Intent storage it = _intents[id];
        require(!it.done, "already fulfilled");
        require(block.timestamp <= it.deadline, "deadline passed");
        require(holds(it.dep), "identity dependency not met");
        it.done = true;
        emit IntentFulfilled(id, msg.sender);
        emit Executed(it.action, it.dep.identity, it.dep.kind, msg.sender);
    }

    /// @notice Number of intents created.
    /// @return The length of the intent list.
    function intentCount() external view returns (uint256) {
        return _intents.length;
    }
}
