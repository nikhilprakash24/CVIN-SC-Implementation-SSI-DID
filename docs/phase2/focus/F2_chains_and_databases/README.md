# F2 — Public and Private Blockchains, and Other Databases

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Written:** 2026-10-14 (Phase 2, focus F2) · **Binds:** `docs/phase2/README.md`

## Executive summary
**The question.** On which kind of ledger or database should vehicle identity live, and which Phase 1 results
survive a change of substrate?

**What Phase 1 already shows.** Every on-chain number comes from one local node (condition M1). Its other substrates
are an in-memory registry and a PKI baseline. That is enough to say three things:
- **Gas transfers, to the unit, to any EVM chain with the same rules.** Fees and chain latency do not transfer (§2 of
  the analysis).
- **The chain costs latency on every write, and nothing on reads served from a cache.** On-chain lifecycle writes are
  about 1,600 to 6,000 times slower than the in-memory registry. A cached on-chain history matches the database's
  speed (#33).
- **What the chain buys is verification by parties who do not trust the operator.** The database baseline offers
  none: no persistence, no authentication, no audit log.

**What Phase 1 never did.** No permissioned or private ledger was built or run. No public network was run (the Sepolia
witness, N-11, is scripted and unrun). There was no rollup, no persistent database, and no ordering or mempool
effects.

**What was done in this pass.**
- **Capture and analysis.** The Phase 1 evidence; a substrate taxonomy along write, read, verify, finality, cost,
  trust and privacy; and a hybrid placement by data class.
- **Plan.** Four experiments, as a pre-registration draft.
- **Execution.** A database lifecycle backend: persistent, transactional, with an append-only, hash-chained journal.
  It sits behind the same interface as Phase 1's two backends, with parity and tamper-evidence tests. One test shows
  exactly where a database stops: an operator who re-derives every later hash passes the database's own audit. Only
  an anchor kept outside, for example on a chain, reveals the rewrite.

**Recommendation.** In the thesis: the transfer table and the two existing comparisons (#33, #21), in chapter 6.
Chapter 5 should cite #33, as SC-13 promised (D62). Before the defence, if wanted: the Sepolia witness. After the
thesis: the four-substrate study.

## Files
| File | What it holds |
|---|---|
| `CAPTURE.md` | every substrate Phase 1 uses or prepares; measured comparisons; what the repository says about private chains and databases; gaps |
| `ANALYSIS.md` | what transfers; substrate taxonomy; the two comparisons; hybrid placement by data class |
| `PLAN.md` | four experiments (pre-registration draft) |
| `EXECUTION.md` | the database backend and its tests |
| `../figures/f2_lifecycle_parity.svg` | figure F2-1, generated |
