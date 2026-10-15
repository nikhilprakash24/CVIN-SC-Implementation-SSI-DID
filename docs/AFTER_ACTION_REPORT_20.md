# After-Action Report 20 — Technical Data Package (parallel document set, engineering register)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-15, after report 19 closed at `c4b35ce`; closed at the end of this pass
**Brief (the author, 2026-10-15):** a parallel pass on this branch, on a different assistant configuration from
passes 8–19. Produce a second set of documents beside the thesis documents, written to the standard, style and
directness of a defence-research programme: a specification and blueprint register for the testbed, with diagrams,
sources and roots, in a cold engineering tone that the thesis can later adapt. Deliver the plan, execute it, and
deliver the plan a second time as phases with prompts that can be run one at a time in another session. Take time.

## 1. Plan
| Step | Work | Owner | Gate |
|---|---|---|---|
| T0 | Open this report; commit it first (guide 1.3.3) | orchestrator | committed before any other file |
| T1 | `docs/tdp/TDP-PLAN.md`: the plan for the Technical Data Package (TDP), with its document tree, numbering, the standards each document follows, and what each document may and may not contain | orchestrator; thesis methodologist | every document in the tree names its governing standard and its data sources |
| T2 | `docs/tdp/TDP-RUNBOOK.md`: the same plan as phases, each with a self-contained prompt, the files it reads, the files it may write, its gate command and its stop condition, so that any later session can execute one phase without this one's context | orchestrator | each prompt names its inputs, outputs and gate; no prompt depends on an unrecorded decision |
| T3 | `docs/tdp/requirements.yaml` + `docs/tdp/make_vcrm.py` → `TDP-002` (system specification, MIL-STD-961E section order) and `TDP-005` (verification cross-reference matrix). Every requirement is a shall-statement traced to a research question, hypothesis, pre-registration or threat goal already on the trunk; verification status is read from the claim register (`docs/MEASUREMENT_CONDITIONS.md`), never typed | orchestrator; measurement methodologist | `make_vcrm.py --check` passes; a tampered matrix fails it (probe); every evidence row cited exists in the register; a requirement citing a non-V row is marked not verified |
| T4 | `docs/tdp/make_blueprints.py` → `docs/tdp/drawings/DWG-00n.svg` (six drawings: general arrangement, substrate assembly, verification engine, freshness governor, evidence line, threat envelope) with title block, revision block, notes and bill of materials; every number on a drawing read from `docs/figures/dashboard_snapshot.json`, `tools/run_identity/producers.json` or `docs/thesis/cruxes.yaml` | orchestrator; visualisation engineer | `--check` passes; drawings carry no hand-typed measurement; each component names its source file |
| T5 | `docs/tdp/make_fmeca.py` → `TDP-006` failure-mode, effects and criticality worksheet (MIL-STD-1629A worksheet columns), generated from `docs/DEFECT_LOG.md` and `docs/THREAT_MODEL.md` | orchestrator; security specialist | `--check` passes; every defect row in the log appears once; severities copied, never re-rated |
| T6 | Hand-written documents: `TDP-000` index and conventions; `TDP-001` programme summary (the Heilmeier Catechism answered from the evidence; technology readiness per subsystem on the DoD scale, with the reason for each level); `TDP-003` interface control document; `TDP-007` test and evaluation master plan; `TDP-008` configuration baseline; `TDP-009` risk register (DoD five-by-five) | orchestrator; specialists per document | every number has a V register row; `check_docs_numbers.py` clean; each document states who wrote it, when, what binds it and what it supersedes |
| T7 | CI: the three new `--check` commands added to the document step; one tamper probe in CI shown to fail; records (INDEX row, handback addendum, session manifest); commit and push; close this report | orchestrator; CI engineer | all document checks pass locally; CI result recorded here if readable from the session, else stated as unread |

**Scope.** This pass changes no contract, script, test, result file or register row. It adds a document set and its
generators under `docs/tdp/` and the CI lines that check them. The grand runner is therefore not re-run (nothing it
measures changed); the document checks are run in full.

**Defaults taken by the orchestrator (the author may overturn any).**
| # | Decision | Default |
|---|---|---|
| T-a | Name and home of the document set | "Technical Data Package", `docs/tdp/`, document ids `TDP-nnn`, drawing ids `DWG-nnn` |
| T-b | Governing standards (format only; no claim of certification) | MIL-STD-961E (specification sections), MIL-STD-498 (document kinds), MIL-STD-31000B with ASME Y14.100 (drawing conventions), MIL-STD-1629A (FMECA worksheet), DoD TRA Guidebook (TRL scale), DoD RIO Guide (risk matrix), DARPA Heilmeier Catechism (programme summary) |
| T-c | Register discipline carried over unchanged | a number appears only with a V row; generated documents are never edited by hand; every guard is shown to fire |
| T-d | Tone | declarative, present tense, no hedging adverbs, no rhetorical questions; the thesis adapts, this set does not |

## 2. Execution log
- 2026-10-15 — report opened.
