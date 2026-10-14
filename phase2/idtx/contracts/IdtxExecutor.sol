// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/*
 * Identity-dependent transactions (IDTx): a prototype (Phase 2, focus F1, start of execution;
 * docs/phase2/focus/F1_onchain_storage_idtx/).
 *
 * Definition used here (F1 ANALYSIS §3): an IDTx is a state transition whose execution is conditioned on
 * a predicate over identity state that some ledger holds at execution time. The predicate is evaluated
 * either in the same transaction (in-contract) or by an automated agent that submits the next
 * transaction, which re-evaluates it on chain before acting.
 *
 * This prototype depends on an ERC-1056 registry (Phase 1's `EthereumDIDRegistry`, unchanged) and on a
 * small commitment store, because ERC-1056 keeps attributes in events only and no contract can read an
 * event (Phase 1 register #49). Three dependency kinds:
 *   Owner       identityOwner(identity) == party                      (registry state, plaintext)
 *   Delegate    validDelegate(identity, key, party)                   (registry state, time-bounded)
 *   Commitment  commitments.valueOf(identity, key) == expected, and still valid
 *               (a hash of a plaintext with a salt, or of a ciphertext: the value itself never
 *               appears on chain; the dependency is equality of commitments)
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
        emit CommitmentSet(identity, key, commitment, until);
    }

    function revokeCommitment(address identity, bytes32 key) external onlyIdentityOwner(identity) {
        delete _value[identity][key];
        delete validUntil[identity][key];
        emit CommitmentRevoked(identity, key);
    }

    /// The commitment if it is still valid, else zero.
    function valueOf(address identity, bytes32 key) external view returns (bytes32) {
        return validUntil[identity][key] > block.timestamp ? _value[identity][key] : bytes32(0);
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

    /// The identity predicate, evaluated against current chain state.
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
