# After-Action Report 13 — Work Milestone WM-2, First Step: A1 (Stamp Inventory Over Every Result Directory)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-10, after WM-1 closed at `8c9fe6b`; closed at the end of this pass
**Brief:** the author's "accept defaults and continue to the next executable", after the milestone close
(after-action report 12, default D-5). The next executable is `docs/PLAN_WM-2.md` step **A1** (N-21).

## 1. Plan
| Step | Work | Gate |
|---|---|---|
| A1 | `check_stamps.py` covers every tracked result directory: single result files as before; multi-file run directories (I4's 30 runs, the scaling-verify repeats) as one aggregated row each; the HTTP-RPC run's `meta.json`; the conformance reports classified as external-tool output; the archive as history | every tracked result JSON outside the excluded lineage copies is either a row, inside an aggregated row, or in a named class; the inventory states the scope count |

Scope stops at A1 in this pass; A2 (one stamp helper with per-producer scope) is the next step.

## 2. Execution log
- 2026-10-10 — report opened.
- **A1.** `check_stamps.py` now accounts for every tracked result JSON outside the lineage copies: 161 files —
  30 with an own row (the HTTP-RPC run's `meta.json` added), 46 in two aggregated run directories (I4's 30 runs:
  30/30 stamped, live clean flag; the scaling-verify repeats: 8 of 16 stamped, code changed since, part of D50),
  13 covered by the harness runs' `meta.json`, 68 external-tool output (W3C DID suite reports), 2 derived, 2
  history; **0 uncovered**. A first version missed four conformance summaries at the top of `reports/`; fixed.
- **Guard.** `--check-coverage` in CI fails when a tracked result file has neither a complete stamp, an
  aggregate nor a class. The first version passed a probe file because the file got a row marked
  "unclassified"; the guard now counts such rows. Shown to fail on both an unstamped file in a scanned
  directory and a file in an uncovered directory.

## 3. Closing
A1 done: N-21 closed; the stamp inventory covers 161 result files with none unaccounted for, and CI enforces
it. The first guard draft would have passed the very case it was meant to catch; the probe found that
before commit (guide rule 1.3.11 at work). Next: WM-2 step A2 (one stamp helper with per-producer scope,
D49), then A4 and C0 (`docs/PLAN_WM-2.md` §4).
