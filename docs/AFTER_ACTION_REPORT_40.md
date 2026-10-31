# After-Action Report 40 — The Stale-Figure Checker Reads SVG (T-19); the Blueprint Set Refreshed and Merged (T-18)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-31, after report 38 closed (CI green on `18fb9f8`) and report 39 (the TDP session, opened the same
morning on this branch). **Brief (the author):** "go ahead with the blueprint refresh and SVG checker".
**Claim, pushed before the work (rule of report 38):** this pass merges `claude/system-blueprint-diagrams-fd8apg` and
regenerates its sheets; it re-runs no producer of record.

## 1. Plan
| Step | Work | Gate |
|---|---|---|
| S1 | T-19: `check_docs_numbers.py` also scans tracked SVG files, reading their text content (tags and entities removed, `tspan` runs joined per `text` element), with the same history globs and pending rule | shown to fire on a superseded value in an SVG; the trunk's existing SVGs pass or each hit is fixed |
| S2 | T-18: merge the blueprint branch. Its Rev C (pushed 2026-10-31 by the blueprint session) binds every measured value to the results of record through `docs/blueprints/data.py` and `data.lock.json`; on its own branch those are the results of 2026-10-15. Regenerate on the trunk's current results, update the lock, and read every change | `make_blueprints.py --check` passes; the SVG checker finds no superseded value in the sheets; every lock change is traced to a register row |
| S3 | Wire both checks into CI and the pre-push guard; records | CI green on the closing commit |

## 2. Execution log
- 2026-10-31 — report opened. Branch state: the TDP session's report 39 (TDP revision B completed, DWG-007 for layer 5)
  is on this branch; the blueprint branch gained Rev C (`70a21b4`) today.
- **S1, the checker reads SVG.** `check_docs_numbers.py` now scans tracked `.svg` files as well as Markdown: each
  `<text>` element's content, with tags removed, entities decoded and no-break spaces read as spaces, is one line. The
  same entries, history globs and pending rule apply. Scope 159 → 173 files; the trunk's existing drawings are clean.
  Shown to fire on the hard case: `warm <tspan>0.153</tspan>&#160;ms` injected into DWG-001 is caught; restored, clean.
  CI and the pre-push guard already run this checker, so SVG is covered with no new step.
