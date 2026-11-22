# TDP-PLAN — The Plan for the Technical Data Package

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-15 (after-action report 20), before execution; status column filled at the pass's close.
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`; `docs/tdp/README.md` (TDP-000).
**Relation to the thesis plan:** this plan runs beside `docs/PLAN_WM-2.md` and takes nothing from it. It adds a
document set and three CI checks; it changes no contract, script, test, result file or register row. The two
sessions that share the branch (reports 20 and 21) coordinate through rebase and the generated-document checks.

## 1. Objective

Produce, from the evidence already on the trunk, a technical data package in the engineering register: a
specification whose requirements are shall-statements traced to the research questions, a verification matrix whose
statuses are computed from the claim register, drawings of the mechanisms generated from the result files, a
failure-mode worksheet generated from the defect log, a programme summary on the Heilmeier questions, an interface
control document, a test plan, a configuration baseline and a risk register. The thesis later adapts the content;
the package itself keeps the register of a programme office.

## 2. Principles that bound the work

1. **No new number.** Every figure is a V row or is read from a result file by a committed generator.
2. **Generated where the source is structured.** Requirements, defects, register statuses, snapshot values, source
   constants and CI steps are structured; the documents built on them are generated and CI-checked. Prose that
   interprets (summary, interfaces, plan, risks) is hand-written and scanned by the stale-figure checker.
3. **Formats, not certifications.** Six military and agency formats supply section orders, worksheet columns, a
   readiness scale and a risk matrix. The package claims no conformance to any of them.
4. **Limits are carried, not softened.** Each requirement ends with the register's caveat; each drawing has a note
   for what it does not show; the summary has a section titled "what the programme does not claim".
5. **Every guard fires.** The three new `--check` commands have a tamper probe in CI.
6. **Process rules unchanged.** After-action report first; commit at step boundaries; author-only commits; no model
   identifiers in any tracked file; handback addendum and session manifest at the close.

## 3. Work breakdown and status

| Step | Deliverable | Method | Gate | Status at close |
|---|---|---|---|---|
| T0 | `docs/AFTER_ACTION_REPORT_20.md` opened and committed first | hand | committed before any other file | done (`854bf3b`, rebased to `ac0dbb9`) |
| T3 | `requirements.yaml` (36 requirements, 7 groups); `make_vcrm.py` → TDP-002, TDP-005 | generator | `--check` passes; cited rows exist; pending items verified against the defect log and the WM-2 plan | done; 29 VERIFIED, 7 PARTIAL, 0 OPEN at the close (EVD-05 was OPEN until the probe existed; STD-01's C1 item was cleared by the parallel pass when C1 landed) |
| T4 | `make_blueprints.py` → `drawings/DWG-001..006.svg`; TDP-004 text | generator; hand | `--check` passes; every number read from a file; rendered and inspected at 1400 x 990 | done; four layout defects found on inspection and fixed before commit (overflowing station text, operation list into the bill of materials, long notes into the title block, title-block columns) |
| T5 | `make_fmeca.py` → TDP-006 | generator | `--check` passes; counts equal the snapshot's; every defect row once | done; 66 defects; the worksheet is exempted from the stale-figure scan as a verbatim record, like the defect log it quotes |
| T6 | TDP-000, TDP-001, TDP-003, TDP-007, TDP-008, TDP-009 | hand | stale-figure checker clean; every number a V row | done |
| T1, T2 | this plan; `TDP-RUNBOOK.md` | hand | each runbook phase self-contained with inputs, outputs, gate and stop condition | done |
| T7 | CI: three checks in the document step; `probe_tdp_checks.sh` as a CI step; records; push; report closed | hand | probe passes locally and in CI; all twelve document checks pass; CI result read or stated unread | see report 20 section 3 |

## 4. What was found while building (the package's own findings)

| # | Finding | Where it landed |
|---|---|---|
| F-1 | Seven V rows are cited by no requirement (#1, #2, #3, #22, #29, #42, #43): the 2026-09-24 snapshot gas, the cv2x registry gas, the three-substrate harness row and the two pre-merge history rows. They are supporting data, not claims a requirement needs | TDP-005 section 2; left as listed, no requirement added |
| F-2 | A status rule that reads only register letters calls SEC-04 (revoked key under clock skew) VERIFIED while #32 and #37 await the A3b re-run; the same for SEC-05 with D54 open. The rule was given a `pending` field that caps status at PARTIAL and fails the build if the named item is later marked fixed or done | `make_vcrm.py`; eight requirements carry pending items |
| F-3 | ERC-725xy is absent from the security harness; a naive join printed "0 defended, 0 n/a" on DWG-002. It now reads "not in harness" | DWG-002 |
| F-4 | The grand-run commit printed on DWG-001 changes every pass and would make the sheet stale at every grand run for no change in content; removed, the counts remain | DWG-001 |
| F-5 | The verifier's rejection reasons, the limits (depth, values, window, cache size) and the adapter and provider method names can be parsed from source; the drawings now read them, so a code change fails the drawing check until regenerated | DWG-002, DWG-003 |
| F-6 | The defect log's "same" in the Where column (inheriting the previous row) and ten defects with no path in that column needed a path-to-plane rule; the rule is declared in the generator and leaves no row unclassified | `make_fmeca.py` |

None of these is a defect of the system under test; none goes to the defect log.

## 5. What this plan does not do

No run, no re-run, no contract or script change, no register row, no change to any thesis chapter, no SUMO, no
Sepolia, no slide deck. The hand-written documents will need a revision (Rev B) when WM-2 C1, C2 and A3b move the
rows they quote; the generated ones will regenerate.

## 6. Revisions

- 2026-10-15, Rev A: initial issue, after-action report 20.
- 2026-10-21, Rev A unchanged; TDP-010 added by runbook phase 10 (after-action report 25). The matrix read 30 VERIFIED, 6 PARTIAL after passes 21 and 22 cleared C1 and D54.
- 2026-10-24, review (phase 11, report 37): 101 claims in TDP-001, 003, 007, 008, 009; 45 OK, 6 mismatch, 2 overstated, 37 stale, 11 missing, most from the A3b re-runs the documents predated.
- 2026-10-24, Rev B of TDP-001, 003, 007, 008, 009 (phase 12, report 38): the review's rows applied; layer 5 added.
- 2026-10-31, Rev B completed (report 39): TDP-000, TDP-004, TDP-010 and the drawings; SYS-04 and the L5 group (#53 to #62) in the specification, 44 requirements; DWG-007; verdicts read from committed result files outside the snapshot. The matrix read 43 VERIFIED, 1 PARTIAL (SEC-06, D64 open).
