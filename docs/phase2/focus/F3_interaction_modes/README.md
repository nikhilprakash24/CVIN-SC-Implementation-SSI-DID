# F3 — Three Modes of Communicating with the Chain, for Reads and Writes

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Written:** 2026-10-14 (Phase 2, focus F3) · **Binds:** `docs/phase2/README.md`

## Executive summary
**The question.** By what modes does a party reach the chain, for reads and for writes, and what does each cost and
imply?

**A proposed taxonomy** (the orchestrator's default; the author decides, P2-D7). One question decides the mode: who
carries the request to the chain at the moment it is needed?
- **A, direct:** the party itself.
- **B, mediated:** a third party. Split into **B-submit** (a relayer or bundler sends a signed write) and **B-serve**
  (a provider or indexer answers a read).
- **C, detached:** nobody at that moment, because a credential, cache or proof obtained earlier is checked in-process.

The letters avoid a clash: in this repository, "Mode 3" and "Mode 4" already name C-V2X radio modes.

**What Phase 1 already shows.**
- **Writes.** A relayed write costs more gas than a direct one: +27,622 for ERC-1056, +47,116 for ERC-4337 (#50, #34).
  Only these two of the ten standards have a relayed path at all.
- **Reads.** Verifying one vehicle message spans three orders of magnitude by mode:
  - C: 0.153 ms, cached, no chain contact (#27);
  - A, cheapest check: 2.76 ms, a probe (#37);
  - A, full: 9.654 ms, replayed from logs (#21).
- **Only Mode C fits a 10 Hz safety budget at density.** On the radio's autonomous sidelink, a vehicle has no network
  path at all, so Mode C is forced.

**What Phase 1 never did.**
- **B-serve was never measured.** There was no provider and no indexer.
- **There is no detached write.** The ERC-1056 signed digest uses the current nonce, so an offline signature goes
  stale.

**What was done in this pass.**
- **Capture and analysis.** The Phase 1 evidence, the taxonomy with three alternative cuts mapped onto it, and the
  cost, trust, privacy and staleness tables.
- **Plan.** Four experiments, as a pre-registration draft.
- **Execution.** A generated classification of every Phase 1 operation and of all 1,752 demo steps by mode, checked
  in CI.
- **A defect found on the way.** The classification shows the grand report's "off-chain" count is mostly reads and
  expected reverts logged under one flag (D61).

**Recommendation.** In the thesis: the taxonomy and the measured write and read tables, in chapter 6. Before the
defence, if wanted: one B-serve data point through the Sepolia run. After the thesis: mode selection per message
class, with verified reads and detached writes.

## Files
| File | What it holds |
|---|---|
| `CAPTURE.md` | every interaction dimension Phase 1 evidences; candidate taxonomies; inconsistencies found |
| `ANALYSIS.md` | the taxonomy; costs and implications by mode; radio coupling |
| `PLAN.md` | four experiments (pre-registration draft) |
| `classify_modes.py`, `MODE_CLASSIFICATION.md` | the generated classification (execution start) |
| `EXECUTION.md` | what was built and checked in this pass |
| `../figures/f3_*.svg` | figures F3-1 (write paths) and F3-2 (read modes), generated |
