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
- **S2, the blueprint branch merged (no conflicts) and refreshed.** Rev C (`70a21b4`, the blueprint session, this
  morning) had already moved every measured value on the 23 sheets behind `docs/blueprints/data.py`, checked against
  `data.lock.json`; this pass verifies and completes it rather than redoing it. On the merged tree:
  - **The new SVG check found 46 superseded figures in 14 files** before regeneration (0.153 ms, 542,378, "369
    Hardhat" and others in the sheets), because the branch's lock held the results of its fork point, 2026-10-15.
  - **Rev C's own data check stopped on three sources the trunk no longer has:** #28 now records the attestEvent
    receipt as a range (222,058–222,082), so `attest.now` reads the range; the README no longer carries test totals,
    so the counts come from the grand report (Hardhat 563, Python 376, total 939); #39 no longer states an
    in-process/RPC latency factor (its two runs are on different hosts, report 38), so the factor is removed and
    BP-201's sentence keeps the RPC value, marked descriptive only. The W3C floor now comes from the CI gate itself
    (`COMPLIANCE_FLOOR` in `w3c-compliance.yml`) instead of a README sentence.
  - **96 lock values changed, and each was traced:** 95 to a result file that `claims.yaml` binds to a V row (#21,
    #22, #25, #27, #30, #32, #33, #35, #37, #39) or to the grand run; the last one, the floor, to the workflow. Examples:
    V2V warm 0.153 → 0.142 ms, PKI 0.253 → 0.226 ms, failures 150 → 210, ERC-735 create 1,535,776 → 1,757,893, tests
    369 → 563 Hardhat. Lock updated (168 values), 23 sheets regenerated, 23 PNGs rendered with the installed Chromium.
  - **Rev C's register #33 finding is settled on the trunk:** the 2026-10-22 re-run's note in #33 gives birth
    398,261–398,285 and event 255,466–255,490 gas, which match the file (398,285, 255,490); that run's latencies are not
    quoted as claims.
  - The X-series tables regenerated from current data; both README observations re-checked and still true (wrapper
    1,025,469 against 1,050,809 over a life; CVIN-Combined fifth-cheapest harness C1 at 271,402). The two blueprint
    audits (Rev B, Rev C) join the history globs: they quote the values they found.
- **S3, wiring.** Rev C's CI job (`blueprint-data-check` in `benchmark.yml`) runs the data check; the pre-push guard
  now runs it too. CI has 12 jobs, not 11; the master plan, the progress report and TDP-001, 007 and 008 say so.

## 3. Closing
Both tasks are done. **T-19:** the stale-figure checker reads the text of every tracked SVG, and on its first real use
it found 46 superseded figures that no check could see. **T-18:** the blueprint set is on the trunk, every measured
value on it is read from a result of record, and two checks guard it: the data lock (a value changes only with its
source) and the stale-figure checker (no superseded value in any sheet). B-1 is complete; B-2 to B-4 stay open.
