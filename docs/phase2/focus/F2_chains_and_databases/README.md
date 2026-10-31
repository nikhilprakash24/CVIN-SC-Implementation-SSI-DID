# F2: Public and Private Blockchains, and Other Databases

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Written:** 2026-10-14 (Phase 2, focus F2) · **Binds:** `docs/phase2/README.md`
**Revised:** 2026-10-14 after the academic review (`docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md`), findings AR-18, AR-19, AR-20, AR-22, AR-26, AR-35, AR-41

## Executive summary
**The question.** On which kind of ledger or database should vehicle identity live, and which Phase 1 results
survive a change of substrate?

**Recommendation** (the review's §4.1).

| Item | In the thesis? | Where |
|---|---|---|
| The transfer table, re-stated with its conditions (analysis §2) | **keep** | chapter 3, threats to validity (a validity argument, not a result) |
| The #33 and #21 comparisons, with #33's pre-registered FAIL reported as a FAIL (analysis §4) | **keep** | chapter 5 (as SC-13 promised, D62) and chapter 6, "why a blockchain" |
| The substrate taxonomy (analysis §3) | **cut** | chapter 2, with citations |
| The hybrid placement by data class (analysis §5) and the SQLite backend (`EXECUTION.md`) | **cut** | future work |
| The plan (`PLAN.md`) | **cut** | one future-work paragraph |
| The Sepolia witness (N-11) | optional before the defence | chapter 3, under the gas wording below |

**Key terms.**
- A *register row* (#n) is a row of the claim register, `docs/MEASUREMENT_CONDITIONS.md`.
- A *substrate* is the ledger or database itself. In Phase 1's crux C1 the word meant a standard; in F2 it does not.
- *M1* is the measurement condition of a single local Hardhat node.

**What Phase 1 already shows.** Every on-chain number comes from one local node (condition M1). The other substrates
are an in-memory registry and a PKI baseline. That is enough to say three things:

| Finding | Evidence |
|---|---|
| **Execution gas is identical for identical bytecode, calldata, pre-state and execution fork.** Intrinsic gas moves with calldata bytes, so cross-network gas is reported within a stated tolerance: 100 gas in the Sepolia script. Fees, latency and finality do not transfer. | analysis §2; #47; `validate_sepolia.js:59` |
| **On-chain writes cost latency, and a cache does not make reads free.** On the 2026-10-04 re-run, lifecycle writes are 1.6e3 to 6.0e3 times slower than the in-memory registry (first run: ≈1,850 to 5,930 times). The pre-registered "equal once cached" result **FAILED**: 0.011 ms against 0.2627 ms, ratio 0.041 on the re-run. A cached read that is also checked for freshness costs 15.403 ms and 6 RPC calls. | #33; `lifecycle_parity.md:60` |
| **Design argument, not a measurement:** what a chain buys is verification by parties who do not trust the operator. M1 has a single operator, so Phase 1 never measured it. The database baseline has no persistence, no caller authentication and no audit log. | analysis §4 |

**What Phase 1 did not do.**
- No permissioned or private ledger was built or run.
- No public network was run. The Sepolia witness, N-11, is scripted and unrun.
- There was no rollup and no persistent database.
- There were no ordering or mempool effects.

**What this pass did.**

| Step | Output |
|---|---|
| Capture and analysis | the Phase 1 evidence; a substrate taxonomy drawn from literature; a hybrid placement by data class (design, no evidence) |
| Plan | four experiments, as a pre-registration draft with verdict rules and kill criteria |
| Execution | a database lifecycle backend: persistent, transactional, with an append-only, hash-chained journal, behind the same interface as Phase 1's two backends |

The journal has two limits, and both need a head hash kept outside the database.
An operator who re-derives every later hash passes the database's own audit.
Deleting rows at the tail goes undetected by the journal alone.
Only an external anchor, for example on a chain, reveals either change; the anchor is not built yet (F2-S3).

## Files

| File | What it holds |
|---|---|
| `CAPTURE.md` | every substrate Phase 1 uses or prepares; measured comparisons; what the repository says about private chains and databases; gaps |
| `ANALYSIS.md` | what transfers, and under which conditions; substrate taxonomy (literature); the two comparisons; hybrid placement by data class (design) |
| `PLAN.md` | four experiments (pre-registration draft) |
| `EXECUTION.md` | the database backend and what its tests establish |
| `../FIGURES.md` | the data tables behind the focus figures, generated |
