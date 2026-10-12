# After-Action Report 14 — Work Milestone WM-2, Step A2 (One Stamp Helper with Per-Producer Scope)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-12, after report 13 closed at `e639dad` (CI 8/8 green); closed at the end of this pass
**Brief:** the author's "accept defaults and continue to the next executable". The next executable is
`docs/PLAN_WM-2.md` step **A2** (defect D49, audit T-F10).

## 1. Plan
| Step | Work | Gate |
|---|---|---|
| A2.1 | One scope table, `run_identity/scopes.json`, read by both a JS helper (`1_blockchain-identity/scripts/lib/run_stamp.js`) and a Python helper (`run_identity/stamp.py`): each scope lists the root-anchored paths of the code a producer runs, results excluded; each producer of record names its scope | one file defines every scope; neither helper carries its own path list |
| A2.2 | The producers move to the helper: the JS scripts, the metrics harness (`dirtyMeasured`, the unanchored pathspec of N-19), the security harness, the SUMO drivers, the `cv2x-testbed/scripts` experiments, the richness driver; existing stamp field names kept, so `check_stamps.py` and the L4 record tests read old and new stamps alike | every producer in the stamp inventory uses the helper or is listed as not converted, with the reason |
| A2.3 | A scope check: each producer's import closure (Python `import`, JS relative `require`) resolved statically and shown to lie inside its scope | `stamp.py --check` exits 1 on a producer importing code outside its scope; in CI |
| A2.4 | The run-identity probe extended to every scope: an edit to a tracked imported file (not only an untracked file) marks the run dirty; a results file does not; a broken helper (pathspecs not root-anchored) fails the probe | probe shown to fail on a broken helper and to pass on the real one; in CI |

Out of scope: re-running any producer (A3, A3b, A6 do that after C0–C2); the harness flag change is code
only here, and A6 still owns the harness re-run of record.

## 2. Execution log
- 2026-10-12 — report opened.
