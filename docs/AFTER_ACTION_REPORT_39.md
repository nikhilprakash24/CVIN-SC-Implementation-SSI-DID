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
- **Q1, requirements.** SYS-04 (basic-set coverage, #53, #54) and a new group L5 with seven requirements (#56 to
  #62), each a shall-statement on what its row measured and nothing more, with the row's limit; #39 cited by SYS-03
  and #55 by RTV-03. `make_vcrm.py` gained file-backed verdicts (`file:<path>:<key>`), so the pre-registered Z-E
  verdicts are read from the layer-5 result files, including Z-E6 FAIL as it fell. 44 requirements: 43 VERIFIED,
  1 PARTIAL (SEC-06, D64 open). The uncited V rows are now the eight history and snapshot rows only (#1, #2, #3, #22,
  #29, #39 is now cited, #42, #43).
- **Q2, TDP-004 and the drawings.** DD-02 and DD-05 re-quoted from the A3b rows (#21 at 15.513 ms with 5 RPCs; #55's
  one-host comparison, probe 3.2 times cheaper, no knee); DD-12 for layer 5. DWG-007 drawn from the three committed
  layer-5 result files (pipeline, expectations as they fell, the Steward's loop, the attack table per defence and
  variant); DWG-001 carries a layer-5 annotation and bill-of-materials item. The revision block now lists revisions
  (Rev B row on every sheet, 7 sheets). One rendering defect found on inspection: SVG collapses runs of spaces, so
  column-aligned text lost its alignment; `xml:space="preserve"` on the root fixes it for every sheet.
- **Q3, TDP-010.** Chapter 3 re-read at `b50864c`: 632 lines, sections 3.1 to 3.8 unchanged line for line, a new 3.9
  (zero-knowledge extension) appended; every line reference holds. The proposed sections renumbered 3.10 and 3.11;
  section 2.6a maps L5-01 to L5-07 (carried by 3.9) and SYS-04 (absent); EVD-03 moved from absent to partial because
  3.9.1 and 3.9.2 state the protocol for layer 5 only; drift item 15 reworded.
- **Q4, records.** TDP-000 Rev B with the review in the tree; runbook phases 11 and 12 marked executed with their
  reports; TDP-PLAN section 6; this report; handback and manifest. Probe: four guards fire; every document check passes.

## 4. Closing
The pass delivered Q1 to Q4. **CI green on all four workflows on the closing commit `8cf93fe`** (Smart Contract Tests
41164231981, W3C SSI Compliance Tests 41164232021, Performance Benchmarks 41164231944, Layer 5 41164231902), read over
the public Actions API; the superseded `219a844` was green as well.

**Every runbook phase has now run once.** Phases 1 to 7 recur on their triggers; the package is at revision B
throughout, with 44 requirements, 7 drawings, 4 guards.

**Next:** for the package, phase 1 when A3 closes or D64 is fixed; for the thesis, D1 with TDP-010 once D-1 is decided.
- **Addendum, same day.** The first whitespace fix (`xml:space="preserve"`, then `white-space: pre`) did not take in
  Chromium; the generator now writes runs of spaces as no-break spaces, which every renderer keeps. Inspection of the
  re-render also found one sentence on DWG-004 that predated A3b ("re-run pending"); corrected, and #55 added to the
  staleness note. Follow-up commit after `219a844`.
