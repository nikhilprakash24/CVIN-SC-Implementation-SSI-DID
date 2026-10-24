# F3: Three Modes of Communicating with the Chain, for Reads and Writes

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Written:** 2026-10-14 (Phase 2, focus F3) · **Binds:** `docs/phase2/README.md`
**Revised:** 2026-10-14 after the academic review (`docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md`), findings AR-28, AR-29, AR-30, AR-31, AR-32, AR-34, AR-35, AR-36, AR-41

## Executive summary
**The question.** By what modes does a party reach the chain, for reads and for writes, and what does each cost and
imply?

**Recommendation** (the review's §4.1 and decision P2-D7).

| Item | In the thesis? | Where |
|---|---|---|
| The six-cell table: write direct, relayed, account-abstracted; read on demand, cached, offline (analysis §2) | **keep** | chapter 4 or chapter 6; every cell has a V row |
| The A/B/C taxonomy, the radio coupling, the mode classification of demo steps | **cut** | paper P4; D61 stays a sandbox defect |
| The plan (`PLAN.md`) | **cut** | one future-work paragraph |

**Key terms.**
- A *register row* (#n) is a row of the claim register, `docs/MEASUREMENT_CONDITIONS.md`.
- A *relayer* is a third party that signs and submits the outer transaction of a write the owner has signed, and pays its gas.
- A *bundler* submits an owner's signed ERC-4337 UserOperation to the *EntryPoint*, the contract that validates and executes it.
  Under ERC-4337 the account pays; no paymaster is used here.
- *k* is the re-check interval of a caching verifier: it asks the chain on every k-th message.
- **The thesis frame** (P2-D7) is six cells: write direct, relayed or account-abstracted; read on demand, cached or offline.
- **Phase 2's and paper P4's frame** is A/B/C, defined per interaction at its time of use (analysis §3).
  The letters avoid "Mode 3" and "Mode 4", which already name C-V2X radio modes in this repository.

**What Phase 1 already shows.**

| Finding | Evidence |
|---|---|
| **Writes.** A relayed or account-abstracted write costs between a half and four fifths more gas than a direct one. ERC-1056: +27,622 on 35,024 (0.79), and the relayer pays. ERC-4337: +47,116 on 94,651 (0.50); the bundler submits and, under the standard, the account pays. Only these two of the ten harness columns have such a path. | #50, #34 |
| **Reads.** Each row is quoted with its own condition, and no ratio is formed across them (rule 1.1.7). Offline SSI verify: 0.153 ms (#27, M0). One probe refresh of the cached ERC-1056 verifier: 2.76 ms, the cost of one refresh, not of verifying one message (#37, another host). Uncached ERC-1056 verify: 9.654 ms (#21, M1). | #27, #37, #21 |
| **The 10 Hz budget, per path and host.** The SSI offline path fits (#26, #27). The ERC-1056 cached verifier does not: on #37's host no finite k reaches P*(0.5) = 100, and k = ∞ gives 78 and 87. #32 gives 110 at k = ∞ on another host. | analysis §4 |
| **Argument from the standard, not evidence:** out of cellular coverage, only Mode C is available. The testbed has no radio. | analysis §4 |

**What Phase 1 did not do.**
- **B-serve was never measured.** There was no provider and no indexer.
- **No detached write was timed.** ERC-1056 signed operations are detached writes with no deadline: each stays valid until its nonce is used. Phase 1 signs and submits them at once, so t₁ − t₀ was never measured.

**What this pass did.**

| Step | Output |
|---|---|
| Capture and analysis | the Phase 1 evidence; the six-cell table; the repaired A/B/C frame; the cost, trust, privacy and staleness tables |
| Plan | four items, as a pre-registration draft: three experiments and one design step |
| Execution | a generated classification of every Phase 1 operation and of all 1,752 demo steps by mode, checked in CI |
| Defect found on the way | D61: the grand report's "off-chain" flag is not set the same way across options; for what the flagged steps are, see the cross-tabulation in `MODE_CLASSIFICATION.md` §3 |

## Files

| File | What it holds |
|---|---|
| `CAPTURE.md` | every interaction dimension Phase 1 evidences; candidate taxonomies; inconsistencies found |
| `ANALYSIS.md` | the six-cell table; the A/B/C frame; costs and implications; radio coupling (argument) |
| `PLAN.md` | three experiments and one design step (pre-registration draft) |
| `classify_modes.py`, `MODE_CLASSIFICATION.md` | the generated classification (execution start) |
| `EXECUTION.md` | what was built and checked in this pass |
| `../FIGURES.md` | the data tables behind the focus figures, generated; the read-mode figure is withdrawn |
