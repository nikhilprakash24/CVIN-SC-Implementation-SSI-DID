# Documentation Index — which document is canonical for what

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-09-24 (the day the analysis lineage was merged onto the trunk)

Two lineages of documentation now live in one repository: the analysis
lineage (recovered from the git bundle, tip `7118b83`) and the
verification/audit lineage written on the trunk. They overlap in purpose.
This index says which file is **canonical** for each question so nothing is
cited twice with different numbers. Files marked *historical* are kept for
provenance and must not be cited in chapters.

## Canonical, by question

| Question | Canonical file | Notes |
|---|---|---|
| What is the argument of the thesis, and how should it be written? | `COMPOSITION.md` | master through-line + writing discipline; unchanged by the merge |
| What is measured, under what conditions, and is each number verified? | `docs/MEASUREMENT_CONDITIONS.md` | condition tags M0/M1/M2 and the claim register (#1–#31; #29–#31 and §5 are the metrics harness, tag M1-H); **the only place a chapter should look up a number's status** |
| What are the results of record? | `4_comparison-framework/results/` (nine-standard gas, scaling, MOBI backends, V2V latency), `1_blockchain-identity/results/metrics/latest/` (operation-catalogue / lifecycle / scale / read-path harness, run-stamped `meta.json`), `cv2x-testbed/results/` (PKI vs ERC-1056), `docs/figures/results_snapshot.json` (trunk verification snapshot), `docs/conformance/` (external W3C DID test suite) | files, not prose |
| Where do the measured results appear as thesis text? | `docs/thesis/chapter5-results/` | the measured anchor for chapter 5 |
| What exists in the repository and does it run? | `docs/PROJECT_SUMMARY.md` | inventory + verification table; supersedes `MASTER_UPDATE.md` §2 and `INVENTORY.md` for status |
| What did the work drift from, and what does an examiner ask? | `docs/AUDIT_01_ORIGINAL_GOALS.md` | goal register, findings F1–F10 with closure notes; `docs/RESEARCH_AUDIT.md` remains the **validity-threat** audit (§4 items) and is complementary, not superseded |
| What changed in scope, and why? | `docs/SCOPE_CHANGES.md` | SC-01 onward; append-only |
| What is the V2V timing budget and where does each design sit? | `docs/LATENCY_BUDGET.md` | derived from SAE J2945/1; P*(f) from measured data |
| How do the standards compare qualitatively? | `docs/DID_METHOD_RUBRIC.md` | W3C DID Method Rubric v2.0 mapping |
| What is the adversary model? | `docs/THREAT_MODEL.md` | Dolev–Yao adversary, A1–A4, goals G1–G8 |
| What are the scaling experiments and their pre-registration? | `docs/SCALING_EXPERIMENTS.md` | design; results in `4_comparison-framework/results/scaling_*` |
| Where did each idea, decision and source come from? | `PROVENANCE.md`, `SOURCES.md`, `docs/DEVELOPMENT_HISTORY.md`, `docs/artifacts/` (provenance dossiers, `docs/ARTIFACTS_MANIFEST.md`) | attribution: hypotheses, thrusts and design decisions are the author's |
| What is the plan and what is needed from the author? | `docs/AFTER_ACTION_REPORT.md` (integration) + `META_COMMENTARY.md` (living handoff) | `MASTER_UPDATE.md` §5–§7 were the pre-merge version of the same lists |
| What was this research originally asked to be, and how is it to be done? | `docs/ORIGINAL_PROMPT_AND_DIRECTION.md` | verbatim original direction (A), the author's working directives (B), and where each stands (C) |
| How do I resume, and what is pending for whom? | `docs/HANDBACK_2026-09-30.md` (sandbox lineage, addenda 0–0e) and `docs/HANDBACK_2026-10-04.md` (review-2 lineage) | both to read until `docs/HANDBACK_2026-10-06.md` closes the merge of the two lineages (`docs/PLAN_MERGE_LINEAGES.md`) |
| What can each identity option actually do, from code? | `docs/FEATURE_ASYMMETRY_MATRIX.md` | generated from the compiled ABIs by `4_comparison-framework/feature-matrix/make_feature_matrix.py`; interpretation in Review 02 §4 |
| What is the state of all the work as one picture (three contract generations, the ERC-1056 fork, coverage by layer)? | `docs/REVIEW_02_STATE_AND_PARALLEL_WORK.md` | the clean review of 2026-10-03 |
| How do the grand sandbox, per-option sandboxes and the L1–L4 suites get built? | `docs/PLAN_SANDBOX_AND_SUITES.md` | steps S0–S10 with acceptance checks |
| What is the relation between this branch and the parallel review-2 trunk (`clone-cvin-id-scs`, now the default branch), and what did each do? | `docs/REVIEW_03_PARALLEL_LINEAGES.md` | the clean review of the two lineages (agreements, same quantities measured twice, 21 contradictions); appendices `docs/reconciliation/RECON_{DOCS,CODE,TSR}.md` |
| How are the two lineages merged, and which decisions does that need? | `docs/PLAN_MERGE_LINEAGES.md` | decisions M-A…M-L with defaults; steps S0–S10 with gates; what is re-executed |
| Thinking out loud, October 2026 | `docs/META_COMMENTARY_2026-10.md` | the asymmetry as the thesis; brainstorm; what to do first |
| How is a substrate measured operation by operation (CRUD and beyond), and what did it show? | `docs/CVIN-DATA-COLLECTION-FRAMEWORK.md` (method: 18-op catalogue, scenarios, falsifiers) + `HANDOFF-DATA-COLLECTION-FRAMEWORK.md` (results and hypothesis verdicts) | harness in `1_blockchain-identity/benchmarks/`; numbers via register #29–#31 only |
| What did the code-level review find, and what was fixed? | `docs/REVIEW_02_CODEBASE.md` (findings K/H/S/T/Q), `docs/PLAN_REVIEW_02.md`, `docs/review02/PASS*_*.md` (per-stream changes), `docs/review02/AAR_REVIEW2_03.md` | review 2, 2026-10-03; complements `AUDIT_01` (claims) and `RESEARCH_AUDIT` (validity) |
| How are the tests and results organised as one suite (subject × identity function × property × evidence), and what is the plan to get there? | `docs/planning/TESTING_SUITE_RESULTS_PLAN.md` (TSR Plan v1.0) + `docs/planning/TESTING_SUITE_SECOND_PASS_SHEET.md` (author's second pass) | as-found survey in `docs/planning/testing_suite/INVENTORY_AS_FOUND_2026-10-04.md`; `docs/testing/` is created by the plan's Phase 1 |
| What does the TSR plan map onto in the sandbox already built here, and what is adopted from it? | `docs/reconciliation/RECON_TSR.md` (40-row mapping, 13 naming conflicts, what to adopt) | reconciliation of 2026-10-06; the merge plan's step S10 |
| Where is any test, and how do the TSR plan and the grand sandbox fit together? | `docs/testing/README.md` | the entry point for the organised suite after the merge: three clicks to any test, the TSR→sandbox mapping, what the plan still asks for |
| What is the current plan, awaiting audit? | `docs/PLAN_2026-10-09.md` | close the merge; generated results dashboard; SUMO visualisation; structured tests and the onboarding lineage; thesis cruxes; eight questions with defaults |
| What rules bind every session (rigour and style)? | `docs/STYLE_AND_RIGOUR_GUIDE.md` | consolidated 2026-10-09 from the direction record, the register's rules and the handbacks |
| How is the work organised as an agentic team, and what did that structure learn? | `docs/TEAM_STRUCTURE.md` | roles, ownership, acceptance gates, lessons of 2026-10-03 to 2026-10-06 |
| Candidate side papers | `SIDE_PAPERS.md` | — |
| Thesis outline and chapter drafts | `docs/thesis/SCAFFOLD.md`, `docs/thesis/chapter*/` | ch. 2 is a stub pending the citation set |

## Historical (keep, do not cite)

- `MASTER_UPDATE.md` — the single-source status as of the bundle (v0.9.0-dev,
  before push was possible). Its numbers predate the merge and the trunk
  verification; superseded by `PROJECT_SUMMARY.md` + `MEASUREMENT_CONDITIONS.md`.
- `INVENTORY.md`, `CAPABILITIES.md`, `QUICKSTART.md` — descriptive; carry a
  banner pointing to the results of record.
- `SESSION_3_SUMMARY.md`, `SESSION_THESIS_INTEGRATION.md`,
  `docs/RESEARCH_THRUSTS_REPORT.md` — session-time snapshots. The four
  `AUTONOMOUS_*.md` logs were consolidated into `docs/DEVELOPMENT_HISTORY.md`
  and removed in the analysis lineage.
- `CV2X_REALISTIC_ROADMAP.md`, `cv2x-testbed/V2_*.md`, `SECOND_PASS_PLAN.md`
  — planning documents; their success criteria are tracked in
  `AUDIT_01_ORIGINAL_GOALS.md` §1.4–1.5 and `SCOPE_CHANGES.md`.

## Rule

A number appears in a chapter only if it has a row in the claim register
with status **V** and a source path. Everything else is labelled as an
estimate, a target, or prior-lineage work pending re-execution.
