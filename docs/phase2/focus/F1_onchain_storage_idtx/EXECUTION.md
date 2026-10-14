# F1 Execution — The IDTx Prototype (Start of Execution)

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Written:** 2026-10-14 (after-action report 16) · **Plan step:** F1-S1

## What was built
| File | What it is |
|---|---|
| `phase2/idtx/contracts/IdtxExecutor.sol` | `IdentityCommitments` (identity-bound commitments in contract state, settable only by the identity's current ERC-1056 owner, each with a chain-time validity) and `IdtxExecutor` (the IDTx gate: three dependency kinds and two continuations) |
| `phase2/idtx/test/idtx.test.js` | 10 behaviour tests against Phase 1's **unmodified** `EthereumDIDRegistry`, deployed from the Phase 1 build's artifact |
| `1_blockchain-identity/hardhat.phase2.config.js` | a separate Hardhat configuration whose sources, tests, cache and artifacts are under `phase2/`; it reuses the Phase 1 project's `node_modules` and changes nothing Phase 1 compiles or measures |

The prototype lives outside the Phase 1 sources under the proposed ADR-0001 (a plug-in layer). It is reversible if
the author chooses another structure.

## What the tests establish (behaviour, not cost)
| # | Test | What it shows for F1 |
|---|---|---|
| 1 | Owner dependency | an action conditioned on who owns a vehicle identity runs for the owner only |
| 2 | Delegate dependency | a delegation is a valid dependency while it lasts, and not after expiry (chain time) or revocation |
| 3 | Commitment over a plaintext | a VIN-bound action can be gated without the VIN appearing on chain: equality of salted commitments |
| 4 | Commitment over a ciphertext | an encrypted value can gate an action by its commitment, never by its content |
| 5 | Commitment authority | only the identity's current owner can set a commitment; after an ownership change, only the new owner |
| 6 | Next-transaction fulfilment | an agent can fulfil an intent later; double fulfilment is refused |
| 7 | Ownership change before fulfilment | fulfilment fails: the dependency is re-evaluated on chain (no time-of-check to time-of-use gap) |
| 8 | Commitment revoked before fulfilment | fulfilment fails, for the same reason |
| 9 | Expired intent | refused |
| 10 | The storage link | ERC-1056's interface has no view that returns an attribute: attributes in events cannot be an in-contract dependency |

**Each guard shown to fire** (guide rule 1.3.11): three mutants of the contract, each caught by the suite.

| Mutant | Tests failing |
|---|---:|
| the dependency always holds | 6 of 10 |
| no re-evaluation at fulfilment | 2 of 10 |
| commitment validity ignored | 1 of 10 |

## What it does not establish
No gas or latency from these tests is a result (Phase 2 principle 4). The costs are E-F1-1 and E-F1-2 in `PLAN.md`,
to be run under a locked pre-registration.

## Run it
```bash
cd 1_blockchain-identity && npx hardhat compile && npx hardhat --config hardhat.phase2.config.js test
```
