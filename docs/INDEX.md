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
| What is measured, under what conditions, and is each number verified? | `docs/MEASUREMENT_CONDITIONS.md` | condition tags M0/M1/M2 and the claim register (#1–#28); **the only place a chapter should look up a number's status** |
| What are the results of record? | `4_comparison-framework/results/` (nine-standard gas, scaling, MOBI backends, V2V latency), `cv2x-testbed/results/` (PKI vs ERC-1056), `docs/figures/results_snapshot.json` (trunk verification snapshot), `docs/conformance/` (external W3C DID test suite) | files, not prose |
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
