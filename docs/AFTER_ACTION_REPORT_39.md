# After-Action Report 39 — TDP Revision B Completed: Records, Layer 5 in the Specification, TDP-004 and TDP-010

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-31, after report 38 closed at `b50864c` (CI green on `18fb9f8`) and report 27 closed at `ec7e19b`;
closed at the end of this pass.
**Brief (the author, 2026-10-31):** continue.

## 1. What a fresh look shows
Passes 37 and 38 executed runbook phases 11 (the read-only review, `docs/tdp/REVIEW_2026-10.md`) and 12 (revision B of
TDP-001, 003, 007, 008, 009) without the package's own records following: the runbook still says phases 11 and 12
remain, TDP-PLAN section 6 has no Rev B line, TDP-000 and the six drawings are at Rev A, and the two hand-written
documents outside the review's scope (TDP-004, TDP-010) still quote A3b-era figures (0.153 ms, 9.654 ms) and chapter
3 line numbers from a 539-line chapter that is now 632 lines. The register has grown to 62 rows; ten V rows (#53 to
#62: the basic-set coverage, the same-host freshness run, and the seven Layer 5 rows) are cited by no requirement.

## 2. Plan
| Step | Work | Gate |
|---|---|---|
| Q1 | Runbook phase 1 (requirements maintenance): cite #53 to #55 from existing requirements where they belong; a new group L5 for the Layer 5 rows (#56 to #62), each shall-statement traced to its pre-registered row or to the layer-5 hypothesis, with the row's own limit | `make_vcrm.py --check`; no V row left uncited except the history and snapshot rows (#1, #2, #3, #22, #29, #39, #42, #43) with their reason stated |
| Q2 | TDP-004 Rev B: design decisions re-quoted from the current rows; Layer 5 added as a design decision and in the machine paragraph; drawings Rev B (revision row; a seventh sheet only if the snapshot carries the Layer 5 data) | `make_blueprints.py --check`; probe |
| Q3 | TDP-010 Rev B: chapter 3 re-read at HEAD; every line reference re-derived; the chapter's new 3.9 reconciled with the proposed outline; the map's states re-checked against the current register and D1's status | stale check clean |
| Q4 | Records: TDP-000 Rev B with the review in the tree; runbook phases 11 and 12 marked executed with their reports; TDP-PLAN section 6; handback addendum; manifest | prepush guard; CI read and recorded |

**Defaults.** Q1-a: Layer 5 requirements are written only where a V row exists; nothing is required of the Steward
or the circuit beyond what #56 to #62 measured. Q2-a: a seventh drawing is drawn only from data already in a committed
JSON the generator can read; otherwise Layer 5 appears on DWG-001 as a plane annotation and the sheet is deferred.

## 3. Execution log
- 2026-10-31 — report opened.
