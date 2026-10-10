# After-Action Report 12 — Closing Work Milestone WM-1: Plan Review, Backward Fixes, Milestone Report, Audit, Presentation Draft

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-10, before any change; updated per step; closed at the end
**Trunk at start:** `291bbca`, clean, CI green (8/8)
**Brief:** "accept defaults and continue to the next executable — first make last sessions' work into
a work milestone or overall milestone; review the work done and the plan; reformulate, update or edit
the plan and anything backwards to be updated or fixed; a very detailed report on this work
milestone (a work milestone, not the overall milestone), with the same style, rigour and agentic
approach; another full audit process and output for this work milestone; finally a presentation
report on everything so far (results, work, implementation; many tables, numbers and figures) — one
draft, and another document on what to expand in the next iteration."

## 1. Defaults taken (the author said "accept defaults")
| # | Question | Default taken |
|---|---|---|
| D-1 | Work milestone or overall milestone? | **Work milestone WM-1** = passes 8–11 (`db6c381..291bbca`, 27 commits, 2026-10-09). The overall milestone stays v0.9.0 as defined in `docs/MILESTONE_NEXT.md` (cut with the merge and a Sepolia witness); WM-1 is a step inside it. |
| D-2 | Git tag for WM-1? | **No tag pushed.** Pushing tags is the open author decision N-11; the milestone is identified by its commit range and its report. A tag `wm-1` can be added when N-11 is decided. |
| D-3 | Who writes the audit briefs? | **A brief-writer agent** (different model, fresh context) writes them from the milestone report, the plans and the reports, so the briefs are not the orchestrator's (N-22, narrowed as in report 11 §1). Auditors also run on a different model, read-only, on a frozen checkout. |
| D-4 | Presentation format | **A document report** in the repository (Markdown with generated figures, every number tagged with its register row), also published as a private web page for presenting. A slide deck derived from it is listed for the next iteration. |
| D-5 | "Continue to the next executable" after the milestone | After WM-1 closes: WM-2 starts with the cheapest items of the new plan (N-21, then N-20), in this pass if the gates close. |

## 2. Plan
| Step | Work | Gate |
|---|---|---|
| W0 | This report with the plan and defaults, committed first | committed and pushed before any other change |
| W1 | Milestone scheme: `docs/milestones/README.md` (work vs overall milestones, naming, what closes a work milestone) | WM-1 boundary commits verified |
| W2 | Plan review: plan of 2026-10-09 (P0–P4, Q1–Q8), the TSR plan phases, the handback's "next executable" lists, `MILESTONE_NEXT.md` → status table; **reformulated plan for WM-2** (`docs/PLAN_WM-2.md`); **backward fixes**: defect log (the verifier holes and the inert flags were never logged), style guide and team structure (rules learned in passes 10–11), INDEX, SCOPE_CHANGES, CHANGELOG, chapter 5 summary §5.7, README key results, a consolidated handback for WM-1 that supersedes the 2026-10-09 handback and its addenda | every plan item has a status; every backward fix listed in §3 |
| W3 | **WM-1 report** (`docs/milestones/WM-1_REPORT.md`), drafted before the audit so the audit checks it: scope, timeline, commits, deliverables, results with register rows, decisions, defects and findings, test and CI state, process metrics, what went wrong, open items | every number traceable to a file or register row |
| W4 | **Audit of WM-1**: brief-writer agent → 4–5 auditors in parallel on a frozen checkout of the W3 commit (claims and chapters; code and security incl. Python suites outside L3; tooling, CI and reproducibility from a clean checkout; reports, plans and the milestone report itself). Findings register with dispositions; fixes re-verified by the orchestrator | no finding without a disposition; confirmed fixes re-checked |
| W5 | **Presentation report, draft 1** (`docs/presentation/`): figure script reading committed results only; report with tables and figures; published page; `EXPANSION_PLAN_DRAFT2.md` | figures regenerate from the script; numbers checked against the register |
| W6 | Grand run, CI, dashboard if a shown number moved, handback, meta commentary, manifest, close | ALL OK; CI green |
| W7 | WM-2 start (D-5) | per item |

## 3. Execution log
- 2026-10-10 — report opened with defaults D-1…D-5.
- **W1.** `docs/milestones/README.md`: work milestones (commit ranges, audited, closed by seven conditions)
  inside overall milestones (version tags). WM-1 = passes 8–11, `db6c381..291bbca`, 27 commits.
- **W2, plan review.** The plan of 2026-10-09 has 25 items: 18 done, 2 changed, 3 partial, 1 deferred,
  **1 not done and never reported as not done (P3.2 `claims.yaml`)**. Status table appended to the plan
  (§5); the plan itself not edited. `docs/PLAN_WM-2.md` written (workstreams A–G, author defaults W2-a…d).
- **W2, backward fixes** (`44dc926`): defect log §F (D28–D36: the review's
  defects of the system under test had been recorded only in report 11); style guide amended (rules
  1.1.6, 1.1.9, 1.1.10, 1.2.7–1.2.9, 1.3.11–1.3.13, checklist); team structure (review protocol §4a,
  lessons §4b); SC-21 (infrastructure scope) and SC-22 (SUMO deferral), both decided in passes 9–10
  without an entry; CHANGELOG "Unreleased" (nothing after 0.8.0 had been entered); infrastructure
  results added to README, thesis README and chapter 5 §5.7, which omitted them; the design's "as built"
  section (its I2 list had "replayed", which the pre-registration dropped silently — the root of D29);
  the visualisation plan's status (V2's byte-stability gate had never been checked: checked, 5 of 5
  identical); N-14 closed (it was still listed open).
- **W2, a hole in pass 11's own fix.** The stale-figure checker excused any value before an arrow,
  but arrows also write ranges: the thesis README's "52,170 → 1,680,816" (and "~33×") passed. The rule
  now excuses a value only if the entry's current value follows the arrow. Eight live stale lines then
  surfaced and were fixed (test counts 217/369 in README, INVENTORY, QUICKSTART; the thesis README's RQ1
  answer; one conformance history line marked).
- **W3.** `docs/milestones/WM-1_REPORT.md` drafted before the audit (`d61a284`). The orchestrator's
  own read-through corrected three of its claims before the audit started: "each guard shown to fail on
  a mutated input" (true for three of seven), the pass-8 agent count, and a defect-log row count.
- **W4, briefs.** A brief-writer agent on a different model wrote five briefs (19–22 checks each) and
  an index of what it left out, from the milestone report, plans and reports; the orchestrator did not
  edit them (archived under `docs/milestones/audit_WM-1/briefs/`, scratch paths normalised). Five
  auditors on a different model run them on a frozen checkout of `d61a284`.
- **W5.** `docs/presentation/make_presentation.py` generates `REPORT_DRAFT_1.md` (10 sections, ~25
  tables, 8 generated figures plus the trace figure and an architecture diagram) and the published page
  from the snapshot, the infrastructure per-run files and a process-metrics file whose every value names
  its source. Figures follow the data-viz method (validated palette; one axis; dots for independent
  runs); one headless look fixed tick rounding, a clipped label, a legend over a value and double TOC
  numbering. `--check` added to CI and shown to fail on a tampered number. Every number the draft
  prints was cross-checked against the register text. Published: https://claude.ai/artifact/EKvpiR7SxXgr4T3UWCdbAH.
  `EXPANSION_PLAN_DRAFT2.md` ranks twelve expansions.

## 4. Findings register (audit of WM-1)
*(filled in W4)*

## 5. Decisions

## 6. Closing — *(written last)*
