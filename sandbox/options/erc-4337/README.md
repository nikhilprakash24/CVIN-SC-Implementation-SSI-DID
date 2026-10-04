# ERC-4337 — feature demos (plan S7)

**Identity model.** A vehicle identity is one `CVINVehicleAccount` contract whose *address* is the stable identifier; a single `owner` signing key controls it and can be rotated (`transferOwnership`) or replaced by a designated `guardian` (`recoverOwner`) without the identity changing. Operations reach the account either as direct calls by the owner key or as `PackedUserOperation`s validated by `CVINMinimalEntryPoint` (`handleOp` → `validateUserOp` → callData), a deliberately minimal research harness: no factory/initCode (so creation is an explicit deployment, not counterfactual), no bundler batching, paymaster, deposits or gas accounting.

Run one demo: `cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-4337/demos/<family>.js`. `demos/_lib.js` is the shared step printer. 109 steps, 28 mined transactions.

| Family | Demo | Functions exercised | Measured in comparison? |
|---|---|---|---|
| Identity creation | `demos/creation.js` | `CVINVehicleAccount` constructor (`VehicleAccountCreated`, zero guards), `owner`, `entryPoint`, `guardian`, `receive`, `CVINMinimalEntryPoint.nonces`, `handleOp` (initCode rejected) | yes (constructor = createIdentity) |
| Ownership / controller | `demos/controller.js` | `owner`, `transferOwnership` (direct, via UserOp, via `execute` self-call), `recoverOwner`, `setGuardian`, `handleOp`, `validateUserOp`, `execute` | yes (`recoverOwner`; `transferOwnership` is the benchmark's transferOwnership) |
| Keys / delegates | `demos/keys-delegates.js` | `guardian`, `setGuardian` (set, replace, via UserOp, clear), `recoverOwner`, `owner`, `setAttribute` (guardian rejected), `handleOp` (guardian signature rejected) | yes (`setGuardian`, `guardian`, `recoverOwner`) |
| Attributes / data store | `demos/attributes.js` | `entryPoint`, `setAttribute` (cold, warm, via UserOp, clear), `getAttribute`, `handleOp`, `validateUserOp` | no as a family (benchmark records `setAttribute` as updateAttribute / updateAttributeVia4337) |
| Signed execution | `demos/signed-execution.js` | `getUserOpHash` (+ off-chain recomputation), `handleOp` (happy path; replay, foreign signer, raw digest, malformed, future nonce, inner revert), `validateUserOp` (direct call rejected), `nonces`, `execute` (direct value transfer, via UserOp, self-call, inner revert), `getAttribute`, `transferOwnership` | no (one `handleOp` is measured as updateAttributeVia4337) |
| Lifecycle / history | `demos/lifecycle-history.js` | `setAttribute`, `setGuardian`, `transferOwnership`, `execute`, `recoverOwner`, `getAttribute`, log replay of `AttributeChanged`, `GuardianChanged`, `OwnershipTransferred`, `OwnerRecovered`, `Executed`, `UserOperationHandled`, adapter `resolve` | no |

Not applicable (no demo): claims, revocation (the account persists; only `setGuardian(0)` clears the delegate — shown in keys-delegates), authorisation roles, token economics, VIN linkage (the VIN is just an attribute), DID helpers, off-chain creation (no factory), off-chain messaging.

## Asymmetry notes

- **Creation: deployed.** One contract per vehicle (759 k gas in L1), deployed by whoever pays — the owner key needs no ether, ever. Canonical 4337's counterfactual CREATE2 address is *not* available in this harness (`initCode` is rejected), so "identity before first transaction" is a property of the standard, not of this implementation.
- **Veracity and automation.** The chain enforces the signature scheme (ecrecover of the EIP-191 envelope over `getUserOpHash`, must equal the current `owner`), strict sequential nonces, the entry-point binding, and the owner/entryPoint/self gate on every admin function. It enforces nothing about attribute *content*: every attribute is self-asserted by the vehicle (third parties cannot write), so an odometer rollback is accepted and only visible by replaying `AttributeChanged` logs. The guardian is a single address with instant, unbounded recovery power (no delay, no quorum, not cleared after use).
- **Cryptography / hashing.** `userOpHash = keccak256(abi.encode(keccak256(packed fields), entryPoint, chainId))` (v0.7 shape), signed under the **EIP-191** `"\x19Ethereum Signed Message:\n32"` envelope (SimpleAccount pattern); a raw-digest signature by the right key is rejected. Attribute keys are `keccak256(name)` (ERC-725Y style); validation returns `1` instead of reverting, as the standard requires. No EIP-1271, no validAfter/validUntil packing.
- **Implemented but never compared.** `execute()` (direct and inside a UserOperation, value transfers from account funds, self-call path), `getUserOpHash`, `nonces`, `validateUserOp` as a callable, the full negative space of signature/nonce validation, inner-revert bubbling (whole tx reverts, nonce rolled back — unlike the canonical EntryPoint), `receive()`, and guardian replacement/clearing via UserOperations.

## Coverage check

Union of functions exercised across the six demos vs the public/external ABI: **CVINVehicleAccount 10/10, CVINMinimalEntryPoint 3/3 — no uncovered function.**

Behaviour worth flagging: `recoverOwner` leaves the guardian in place, so a guardian is effectively a super-owner that can re-take the identity at will; the harness reverts the whole `handleOp` on an inner failure (canonical 4337 would emit `UserOperationRevertReason` and still consume the nonce), so the measured indirection overhead is a lower bound.
