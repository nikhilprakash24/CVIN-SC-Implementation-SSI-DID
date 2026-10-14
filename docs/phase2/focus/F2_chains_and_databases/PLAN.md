# F2 Plan — Substrate Experiments (Pre-Registration Draft)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, focus F2, plan). **State:** a draft, not locked, nothing run (principle 4).
**Builds on:** `ANALYSIS.md`; the database backend `phase2/backends/` (EXECUTION.md).

## 1. Experiments
| ID | Question | Design | Measure | Prediction | Needs |
|---|---|---|---|---|---|
| **E-F2-1** | The same lifecycle, four substrates: what does each cost and buy? | the M4 operation sequence (#33) through the in-memory registry, the SQLite journal, the local chain, and a permissioned EVM chain | per-operation median and p95 latency (N ≥ 30 per guide rule 1.1.7), gas where applicable, and a verification column: who can detect a rewrite | journal within an order of magnitude of the in-memory registry; permissioned chain within an order of magnitude of the local chain; only the chains and the anchored journal pass the third-party-verification test | a permissioned EVM client installed (author decision P2-D9) |
| **E-F2-2** | What does anchoring a database's journal on a chain cost, per write? | journal head anchored every N writes, N ∈ {1, 10, 100}, on the local chain | anchor gas ÷ N; detection of a rewrite made after an anchor (test) | amortised anchor gas falls as 1/N; every rewrite before the last anchor is detected | the backend's anchoring step (F2-S3) |
| **E-F2-3** | Does gas transfer to a public network to the unit? | the Phase 1 validation script on Sepolia | per-operation gas; fee in the network's units at the dated price | identical gas; fee reported, not compared | secrets for N-11 |
| **E-F2-4** | What does a rollup add? | the nine-standard benchmark on one rollup testnet | gas on L2, L1 data cost | the ranking of standards unchanged; absolute costs change | access to a rollup testnet |

## 2. Steps
| Step | Work | Gate |
|---|---|---|
| F2-S1 | **done:** the SQLite journal backend, with parity and tamper-evidence tests (EXECUTION.md) | tests pass |
| F2-S2 | register the backend in the parity experiment as a third backend, behind the same interface; stamp and promote | producer registered before any run |
| F2-S3 | anchoring: write the journal head to a small anchor contract every N entries; a test that a post-anchor rewrite is detected | test fails without the anchor |
| F2-S4 | lock this plan; then run E-F2-1 (three local substrates first) and E-F2-2 | pre-registration committed first |
| F2-S5 | E-F2-3 and E-F2-4 when the author's decisions allow | N-11, P2-D9 |

## 3. Risks
| Risk | Mitigation |
|---|---|
| Comparing an in-process database with a networked chain flatters the database | report both, and add the journal as a persistent, transactional middle point; state that the in-memory registry is a lower bound (#33 caveat) |
| A permissioned chain's latency depends on its consensus settings | fix and record block interval, validator count and consensus; report as one configuration, not "private chains" in general |
| Public-network fees change daily | fees are reported dated and never compared across dates |
