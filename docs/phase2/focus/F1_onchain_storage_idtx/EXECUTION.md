# F1 Execution — The IDTx Prototype (Start of Execution)

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Written:** 2026-10-14 (after-action report 16) · **Plan step:** F1-S1
**Revised:** 2026-10-14 after the academic review (`docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md`), findings AR-4,
AR-5, AR-6, AR-14. **Placement:** in the thesis the prototype is cited as an artefact only (review §4.1).

## What was built
| File | What it is |
|---|---|
| `phase2/idtx/contracts/IdtxExecutor.sol` | two contracts. `IdentityCommitments` holds identity-bound commitments in contract state. Only the identity's current ERC-1056 owner can set one; each has a chain-time validity, and **stops counting when its setter no longer owns the identity** (AR-6). `IdtxExecutor` is the IDTx gate: three dependency kinds (Owner, Delegate, registered-commitment validity) and two continuations (same transaction; intent then fulfilment) |
| `phase2/idtx/test/idtx.test.js` | 12 behaviour tests against Phase 1's **unmodified** `EthereumDIDRegistry`, deployed from the Phase 1 build's artifact |
| `phase2/idtx/mutate_idtx.sh` | 5 gate mutants; each must make the suite fail. Run in CI (AR-14) |
| `1_blockchain-identity/hardhat.phase2.config.js` | a separate Hardhat configuration whose sources, tests, cache and artifacts are under `phase2/`. It reuses the Phase 1 project's `node_modules` and changes nothing Phase 1 compiles or measures |

**What the predicate is about (AR-4).** The predicate is about the **named identity's state**, never about the
caller. Anyone (a keeper, an insurer, a toll system) may submit an IDTx, and the named identity's state decides.
This follows the definition in `ANALYSIS.md` §4.1, and test 2 shows it.

## What the tests establish (behaviour, not cost)
| # | Test | What it shows |
|---|---|---|
| 1 | Owner dependency | the action runs only when the named party is the identity's current owner |
| 2 | The caller is not part of the predicate | a third party may submit; a wrong named party fails |
| 3 | Delegate dependency | valid while the delegation lasts; not after expiry (chain time) or revocation |
| 4 | Registered-commitment validity, plaintext | a VIN-bound action gated by a registered salted commitment; the VIN is not on chain. This proves no knowledge of the VIN (AR-5) |
| 5 | Registered-commitment validity, ciphertext | an encrypted value gates an action by its registered digest, never by its content |
| 6 | A commitment outlives its setter (AR-6) | after an ownership change, the old owner's commitment no longer counts |
| 7 | Commitment authority | only the current owner can set or revoke a commitment |
| 8 | Next-transaction fulfilment | an agent fulfils later; double fulfilment is refused |
| 9 | Ownership change before fulfilment | fulfilment fails: the dependency is re-evaluated on chain |
| 10 | Commitment revoked before fulfilment | fulfilment fails, for the same reason |
| 11 | Expired intent | refused |
| 12 | The storage link | ERC-1056 exposes no view that returns an attribute, so a contract cannot read its attributes directly. A carried receipt proof would be the only route (AR-1) |

**Each guard shown to fire, in CI** (guide rule 1.3.11): every mutant is caught, and the contract is restored after
the run.

| Mutant | What it removes |
|---|---|
| `holds_always_true` | the dependency check |
| `no_recheck_at_fulfil` | the re-evaluation at fulfilment |
| `commitment_validity_ignored` | the commitment's validity window |
| `commitment_setter_ignored` | the setter-ownership binding (AR-6) |
| `deadline_ignored` | the intent's deadline |

## What it does not establish
No gas or latency from these tests is a result (Phase 2 principle 4). The costs are E-F1-1 and E-F1-2 in `PLAN.md`,
with point predictions written before any run. The ordering race between a dependency's change and the dependent
transaction is not tested here (`ANALYSIS.md` §4.5).

## Run it
```bash
cd 1_blockchain-identity && npx hardhat compile && npx hardhat --config hardhat.phase2.config.js test
cd .. && bash phase2/idtx/mutate_idtx.sh
```
