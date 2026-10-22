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

interface IERC1056 {
    function identityOwner(address identity) external view returns (address);
    function validDelegate(address identity, bytes32 delegateType, address delegate) external view returns (bool);
}

/// Identity-bound commitments in contract state, settable only by the identity's current owner.
contract IdentityCommitments {
    IERC1056 public immutable registry;
    mapping(address => mapping(bytes32 => bytes32)) private _value;
    mapping(address => mapping(bytes32 => uint64)) public validUntil;
    mapping(address => mapping(bytes32 => address)) public setBy;   // AR-6: the owner at set time

    event CommitmentSet(address indexed identity, bytes32 indexed key, bytes32 commitment, uint64 validUntil);
    event CommitmentRevoked(address indexed identity, bytes32 indexed key);

    constructor(IERC1056 registry_) {
        registry = registry_;
    }

    modifier onlyIdentityOwner(address identity) {
        require(registry.identityOwner(identity) == msg.sender, "not the identity owner");
        _;
    }

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

    function revokeCommitment(address identity, bytes32 key) external onlyIdentityOwner(identity) {
        delete _value[identity][key];
        delete validUntil[identity][key];
        delete setBy[identity][key];
        emit CommitmentRevoked(identity, key);
    }

    /// The commitment if it is still valid and its setter still owns the identity (AR-6), else zero.
    function valueOf(address identity, bytes32 key) external view returns (bytes32) {
        if (validUntil[identity][key] <= block.timestamp) return bytes32(0);
        if (registry.identityOwner(identity) != setBy[identity][key]) return bytes32(0);
        return _value[identity][key];
    }
}

contract IdtxExecutor {
    enum Kind { Owner, Delegate, Commitment }

    struct Dependency {
        Kind kind;
        address identity;
        bytes32 key;       // delegate type (Delegate) or commitment key (Commitment); unused for Owner
        bytes32 expected;  // the expected commitment (Commitment); unused otherwise
        address party;     // the expected owner (Owner) or delegate (Delegate); unused for Commitment
    }

    struct Intent {
        Dependency dep;
        bytes32 action;
        uint64 deadline;
        address creator;
        bool done;
    }

    IERC1056 public immutable registry;
    IdentityCommitments public immutable commitments;
    Intent[] private _intents;

    event Executed(bytes32 indexed action, address indexed identity, Kind kind, address caller);
    event IntentCreated(uint256 indexed id, bytes32 indexed action, address indexed identity, uint64 deadline);
    event IntentFulfilled(uint256 indexed id, address keeper);

    constructor(IERC1056 registry_, IdentityCommitments commitments_) {
        registry = registry_;
        commitments = commitments_;
    }

    /// The identity predicate, evaluated against current chain state. It does not involve msg.sender (AR-4).
    function holds(Dependency memory d) public view returns (bool) {
        if (d.kind == Kind.Owner) return registry.identityOwner(d.identity) == d.party;
        if (d.kind == Kind.Delegate) return registry.validDelegate(d.identity, d.key, d.party);
        bytes32 v = commitments.valueOf(d.identity, d.key);
        return v != bytes32(0) && v == d.expected;
    }

    /// Same-transaction IDTx: the action happens only if the predicate holds now.
    function execute(Dependency calldata d, bytes32 action) external {
        require(holds(d), "identity dependency not met");
        emit Executed(action, d.identity, d.kind, msg.sender);
    }

    /// Next-transaction IDTx, step 1: record what is to happen and on which dependency.
    function createIntent(Dependency calldata d, bytes32 action, uint64 deadline) external returns (uint256 id) {
        require(deadline > block.timestamp, "deadline passed");
        id = _intents.length;
        _intents.push(Intent(d, action, deadline, msg.sender, false));
        emit IntentCreated(id, action, d.identity, deadline);
    }

    /// Next-transaction IDTx, step 2: any agent may fulfil; the predicate is re-evaluated here.
    function fulfil(uint256 id) external {
        Intent storage it = _intents[id];
        require(!it.done, "already fulfilled");
        require(block.timestamp <= it.deadline, "deadline passed");
        require(holds(it.dep), "identity dependency not met");
        it.done = true;
        emit IntentFulfilled(id, msg.sender);
        emit Executed(it.action, it.dep.identity, it.dep.kind, msg.sender);
    }

    function intentCount() external view returns (uint256) {
        return _intents.length;
    }
}
