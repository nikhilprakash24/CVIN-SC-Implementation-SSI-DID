# F1 Plan — Experiments for On-Chain Storage and IDTx (Pre-Registration Draft)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, focus F1, plan). **State:** a **draft**. It is not locked and nothing has been run.
It becomes a pre-registration only when committed under `docs/phase2/prereg/` before the first run (Phase 2
principle 4; ROADMAP P2.3). **Builds on:** `ANALYSIS.md`; the prototype `phase2/idtx/` (EXECUTION.md).

## 1. Experiments
| ID | Question | Design | Measure | Prediction (written before any run) | Verdict rule |
|---|---|---|---|---|---|
| **E-F1-1** | What does an IDTx cost over the plain action, per dependency kind and continuation? | the prototype on the Phase 1 harness conditions (M1, solc 0.8.24, optimizer 200, viaIR, cancun); an action with no dependency as the control; Owner, Delegate, Commitment dependencies; same-transaction and intent-plus-fulfil | gas from receipts; exact (seeded inputs), or a min–max range by guide rule 1.1.10 | same-transaction overhead under 10,000 gas per dependency (one external call and a cold storage read); next-transaction cost dominated by the intent's new slots and the second transaction's base cost | reported against the prediction; a miss is reported as a miss |
| **E-F1-2** | What does the storage locus change, holding the datum fixed? | one identity datum (a VIN-bound attribute) stored at L0 (state), L1 (event), L3 (commitment), L4 (anchored credential) | write gas; read RPC calls and bytes at h ∈ {1, 10, 50}; whether an in-contract IDTx is possible | L1 cheapest to write and the only one with history-dependent reads; L0 and L3 flat reads; only L0 and L3 support an in-contract IDTx | each cell reported; the "IDTx possible" column is a test, not a measurement |
| **E-F1-3** | How large is the time-of-check to time-of-use window when the dependency is evaluated off chain? | an agent reads the dependency, then submits; the state changes in between with a set probability; with and without the on-chain re-check of `fulfil` | count of actions executed on a false dependency, over N trials | zero with the re-check; with no re-check, equal to the number of changes landing in the window | PASS iff the re-check variant executes none |
| **E-F1-4** | What does an observer learn from the dependency? | the dependency reads and events of E-F1-1 and E-F1-2, examined by an adversary who knows candidate VINs | identifier recovery and linkage rate | with a VIN-derived identity (D64), recovery for every candidate VIN; with a salted, non-derived identity, none from the dependency alone | reported; feeds the D64 fix |

## 2. Conditions and identity of runs
- Producers are registered in `tools/run_identity/producers.json` from their first line (ADR-0002); they write to
  `runs/` and reach a result path only through `tools/run_identity/promote.py`.
- Gas condition M1 as in Phase 1; latency is not a measure in F1 (reads are counted in RPC calls and bytes).
- Randomness seeded; where a seeded input would hide a real cost, ranges are reported (guide rule 1.1.10).

## 3. Steps, in order
| Step | Work | Gate | Depends on |
|---|---|---|---|
| F1-S1 | **done:** the prototype with 10 behaviour tests (EXECUTION.md) | tests pass and fail on a broken gate | — |
| F1-S2 | the author decides placement (P2-D1; scope reconciliation §4 recommends concept-only in the thesis) | decision recorded | — |
| F1-S3 | fix D64 in the testbed provider (salted, non-derived identity), with a test that fails on the current derivation | test | WM-2 D1 |
| F1-S4 | lock this plan as a pre-registration | committed before any run | P2-D1 |
| F1-S5 | run E-F1-1 and E-F1-2 (gas and counts only) | promote clean runs; register rows | F1-S4 |
| F1-S6 | run E-F1-3 and E-F1-4 | as above | F1-S5 |
| F1-S7 | write-up: a chapter 6 section (concept) or the first post-thesis paper (measured) | academic review | F1-S5/S6 |

## 4. Risks
| Risk | Mitigation |
|---|---|
| IDTx is judged a re-label of access control | the five-axis taxonomy and E-F1-3 (TOCTOU) carry the claim; position against ERC-3643, ERC-4337 validation and oracles at their sources |
| The prototype is mistaken for the contribution | it is a measurement instrument; the contribution is the definition, taxonomy and evaluation dimensions |
| Gas varies with random keys (Phase 1 B1 issue) | seed inputs; report ranges where the input is the thing measured |
