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
- **T0.** Report committed first (`854bf3b`); the push was refused because the parallel pass had landed its grand-run
  commit, so the report was rebased onto it (`ac0dbb9`). Two sessions share the branch for the rest of this pass;
  every push is preceded by a fetch and rebase, and the generated-document checks are re-run after each rebase.
- **T3, requirements and matrix.** `docs/tdp/requirements.yaml` holds 36 shall-statements in seven groups (SYS, PRF,
  SEC, STD, RTV, INF, EVD), each traced to an RQ, a hypothesis, a pre-registration, a threat goal or a rigour rule,
  each ending with the register's own caveat. `make_vcrm.py` computes the status of each from the register (through
  the dashboard's own parser), the snapshot (thresholds and pre-registered verdicts), the tree (inspection files) and
  the workflows (CI steps). First build: 34 VERIFIED, 0 PARTIAL, 1 OPEN. That was wrong in a way the rule allowed:
  SEC-04 (revoked key under clock skew) read VERIFIED on #32 and #37 although both await the A3b re-run, and SEC-05
  read VERIFIED on #28 although D54 is open. A `pending` field was added; it caps status at PARTIAL and the build
  fails if a pending defect is later marked fixed or a pending WM-2 step marked done (shown to fire by naming a fixed
  defect). Eight requirements carried pending items (A3b, A6, C1, C2, D54, D64); the parallel pass removed C1 from STD-01
  when WM-2 C1 landed, because the guard asked for it (`7e43ea0`). Close of pass: 29 VERIFIED, 7 PARTIAL, 0 OPEN. Seven V rows are cited by no requirement (#1, #2, #3, #22, #29, #42, #43); they are supporting data and are
  listed as such in TDP-005 section 2 and TDP-PLAN section 4.
- **T5, worksheet.** `make_fmeca.py` parses every defect row (66) with the same rules as the dashboard, so the
  severity-by-status counts are cross-checked against the snapshot and the build fails on a disagreement. The
  worksheet carries the log's letter and a declared translation to the MIL-STD-1629A class beside it; no rate or
  criticality number is computed. Ten rows had no path in the Where column ("same", a chapter, a statement); the
  plane rule in the generator classifies them and leaves none unclassified. The worksheet quotes a defect whose text
  contains a superseded test count; it is a verbatim record like the defect log it quotes, and is added to the
  stale-figure checker's history globs for that reason (the hand-written TDP documents stay scanned).
- **T4, drawings.** `make_blueprints.py` writes six sheets; every number is read from the snapshot, the PKI result
  file, `producers.json`, the workflows, the threat model's goal table, or source constants (the verifier's depth and
  value limits, the freshness window and cache size, the rejection reasons, the adapter and provider method names).
  Rendered to PNG with the installed headless Chromium and inspected at 1400 x 990. Four layout defects found and
  fixed before commit: station body text overflowing the 108 px boxes on sheets 3 and 5 (sheet 5 re-laid as two rows
  of four; sheet 3 texts shortened), the adapter operation list running into the bill of materials on sheet 2
  (wrapped), notes colliding with the title block (wrapped at 150 characters), and the title block's two columns
  overlapping. Two content corrections: ERC-725xy is not in the security harness and read "0 defended / 0 n/a"
  (now "not in harness"); the grand-run commit printed on sheet 1 would have changed every pass for no change in
  content (removed; the counts remain). After the CI workflow gained the TDP checks, `make_blueprints.py --check`
  failed on the clean tree because sheet 5 reads the document-check list from the workflow; that is the check
  firing as designed, and the sheet was regenerated (12 document checks listed).
- **T6, hand-written documents.** TDP-000 (index, conventions, sources), TDP-001 (the eight Heilmeier questions
  answered from V rows; readiness levels per plane with the reason each next level is withheld; the full-circle
  statement in one paragraph; what is not claimed), TDP-003 (thirteen interfaces with fields copied from source),
  TDP-004 (drawing index, the machine in one paragraph, eleven design decisions with their measured consequence),
  TDP-007 (test architecture with counts, evaluation framework, pre-registration protocol, resources, exams,
  limits), TDP-008 (configuration items, runs of record with identities, toolchain pins including the two pins that
  disagree with the runs of record, build and change control), TDP-009 (thirteen risks on the five-by-five scale with
  triggers, four issues). The stale-figure checker is clean over all of them.
- **T1, T2.** `TDP-PLAN.md` (objective, principles, work breakdown with status, six findings made while building, what
  the plan does not do) and `TDP-RUNBOOK.md` (phases 0 to 7 recording what this pass executed so each can be re-run
  or audited; phases 8 to 12 as follow-on work; each with reads, writes, gate, stop condition and a self-contained
  prompt under a standing preamble).
- **T7, CI and probe.** The three `--check` commands are added to the document step of `test-contracts.yml`, and
  `docs/tdp/probe_tdp_checks.sh` runs as its own step: for each generator it tampers the output, expects `--check` to
  exit 1, restores, and expects 0. Run locally: all three probes pass. All fourteen document and stamp checks pass
  locally after regeneration. Records: INDEX row, handback section 12 with four gotchas, session manifest pass 20.
- **Interaction with the parallel pass (report 21).** Its grand run turned CI red on my first push (the worksheet
  quoted a superseded test count); it applied the same exemption I had made locally, regenerated DWG-001 after its
  grand run, and removed C1 from STD-01's pending list when the matrix guard asked for it. The rebase of this pass's
  closing commit conflicted on the handback, the manifest, the matrix and sheet 1; the shared files keep both
  passes' sections (handback section 12 is pass 21's, section 13 this pass's), and the generated ones were rebuilt
  after the rebase. Every document check passed on the rebased tree.
- **Not done, by scope.** No grand run (nothing it measures changed; the pass adds documents, generators and CI lines
  only). The CI result of the closing commit could not be read from this session (no GitHub API access); it is to be
  read by the author or the next session and recorded in the closing commit of this report.

## 3. Closing
The pass delivered every step of section 1. **CI 8 of 8 green on the closing commit `914dcb2`** (Smart Contract
Tests run 38688011214, W3C SSI Compliance Tests 38688011299, Performance Benchmarks 38688011225), read over the
public Actions API from this session after the push. Closed 2026-10-20; passes 21 to 24 landed on the branch in
between and kept the three TDP checks green (report 21 section 2 records the one red they caused and fixed).

**The package stands on the register and adds nothing to it.** 36 requirements, 29 verified by V rows with nothing
pending and 7 partial with their blocking item named; 66 defects on a worksheet whose counts equal the snapshot's;
six drawings whose every number has a file behind it; nine hand-written documents whose every number has a row.

**What the author decides** (defaults T-a to T-d in section 1 stand until overturned): whether the package name and
home stay; whether the thesis adapts TDP-002's shall-statements as chapter 3's commitments (runbook phase 10 maps
them); whether to open the external review of the package (phase 11).

**Next:** runbook phase 1 after C1 lands (requirements maintenance), phase 5 at every regeneration, phases 8 to 12
when the author chooses. Phase 1 of WM-2 continues in report 21.
