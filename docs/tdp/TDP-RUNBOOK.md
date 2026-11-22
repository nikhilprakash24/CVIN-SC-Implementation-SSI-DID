# TDP-RUNBOOK — The Plan as Phases and Prompts

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-15 (after-action report 20). **Revision:** A.
**Purpose:** the same plan as `TDP-PLAN.md`, cut into phases that a later session can run one at a time with no
memory of this one. Each phase states what it reads, what it may write, its gate command and its stop condition.
Phases 0 to 7 record what pass 20 executed (so a session can re-run or audit one); phase 10 was executed in pass 25 and
phases 8 and 9 in pass 27, phase 11 in pass 37 and phase 12 in passes 38 and 39. Every phase has run once; phases 1 to 7
recur whenever their triggers fire. A prompt is text to paste; the words in angle brackets are filled in by the
person running it.

## How to run a phase

1. Start a session on the trunk branch, clean tree, `git fetch` first (two sessions share the branch).
2. Paste the phase's prompt. Nothing else is needed; the prompt names every file.
3. The phase ends when its gate command exits 0 and its stop condition holds. Commit under the author's name with
   the phase id in the message. Do not continue into the next phase in the same prompt.
4. If the gate fails, the session reports the failure and stops; it does not weaken the gate.

Standing preamble, prepended to every prompt:

> Read `docs/STYLE_AND_RIGOUR_GUIDE.md`, `docs/tdp/README.md` and `docs/tdp/TDP-PLAN.md` before acting. Rules that
> apply without exception: no number without a claim-register row of status V (`docs/MEASUREMENT_CONDITIONS.md`);
> generated documents are never edited by hand; every new guard gets a probe that fails on the broken version; commits
> under the author's name with no co-author trailer and no assistant or model identifier in any tracked file; open or
> continue an after-action report before changing anything; commit at the step boundary and stop.

---

## Phase 0 — Orientation (read-only)

**Reads:** `docs/HANDBACK_2026-10-14.md`, the latest `docs/AFTER_ACTION_REPORT_*.md`, `docs/tdp/README.md`,
`docs/tdp/TDP-005_VERIFICATION_CROSS_REFERENCE_MATRIX.md` section 0. **Writes:** nothing.
**Gate:** `python3 docs/tdp/make_vcrm.py --check && python3 docs/tdp/make_fmeca.py --check && python3 docs/tdp/make_blueprints.py --check`.
**Stop:** a one-screen statement of the verified state and which phase is next.

**Prompt.**
> Orient only. State, in one screen: the trunk commit, the last after-action report and whether it is closed, the
> register totals by status, the TDP-005 totals (VERIFIED, PARTIAL, OPEN) and the pending items that cap any
> requirement at PARTIAL, and which runbook phase of `docs/tdp/TDP-RUNBOOK.md` is next. Run the three TDP checks and
> report their exit codes. Change nothing.

## Phase 1 — Requirements maintenance

**Reads:** `docs/tdp/requirements.yaml`, the register, `docs/PLAN_WM-2.md` section 3, `docs/DEFECT_LOG.md`.
**Writes:** `requirements.yaml`; regenerated TDP-002 and TDP-005. **Gate:** `python3 docs/tdp/make_vcrm.py --check`.
**Stop:** every requirement's `pending` list names only items still open; any V row the plan has since added is cited
by a requirement or listed as supporting data in TDP-PLAN section 4.

**Prompt.**
> Maintain the requirements source `docs/tdp/requirements.yaml`. For each requirement, confirm its evidence rows exist
> and its `pending` items are still open (the generator fails on a closed one; remove such items and say why). For
> each register row added since Rev A (list them from `docs/MEASUREMENT_CONDITIONS.md` against TDP-005 section 2),
> decide whether an existing requirement cites it or a new shall-statement is needed; a new requirement must be
> traced to an RQ, hypothesis, pre-registration, threat goal or rigour rule, and must carry the row's own caveat as
> its limit. Regenerate with `python3 docs/tdp/make_vcrm.py`, run `--check`, record the status totals before and
> after in the after-action report, commit as "TDP phase 1: requirements maintenance", and stop.

## Phase 2 — Drawing revision

**Reads:** `docs/tdp/make_blueprints.py`, the rendered sheets. **Writes:** the generator; regenerated SVGs; a new
revision-block row. **Gate:** `python3 docs/tdp/make_blueprints.py --check` and `bash docs/tdp/probe_tdp_checks.sh`.
**Stop:** every sheet renders at 1400 x 990 with no overflow, and the revision block names the change.

**Prompt.**
> Revise the blueprints. Render each `docs/tdp/drawings/DWG-00n.svg` to PNG with the installed headless Chromium
> (`/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell --headless --no-sandbox --screenshot=<out>
> --window-size=1400,990 file://<svg>`) and inspect it. Fix any text overflow or collision in
> `docs/tdp/make_blueprints.py`, never in the SVG. Make the requested content change: <state it; a new sheet needs a
> number DWG-007 onward, a title block, notes, a bill of materials, and every number read from a file>. Increment the
> revision letter in the generator and add the revision row. Regenerate, run `--check` and the probe, commit as
> "TDP phase 2: drawings Rev <letter>", and stop.

## Phase 3 — Worksheet and risk re-rating

**Reads:** `docs/DEFECT_LOG.md`, `docs/tdp/TDP-009_RISK_REGISTER.md`, `docs/thesis/CRUX_REGISTER.md`,
`docs/MILESTONE_NEXT.md`. **Writes:** TDP-009 (hand); regenerated TDP-006. **Gate:** `python3 docs/tdp/make_fmeca.py --check`
and `python3 docs/testing/check_docs_numbers.py`. **Stop:** every risk whose trigger fired is re-rated or moved to
issues, with the reason in the row.

**Prompt.**
> Re-rate the risk register `docs/tdp/TDP-009_RISK_REGISTER.md`. For each risk, check whether its trigger has fired
> (name the file or commit that shows it). Re-rate likelihood and consequence on the scales in section 1, move a
> realised risk to section 3 with its treatment, retire a closed one with its reason, and add any new risk the crux
> gaps or deferred items now show. Regenerate TDP-006 (`python3 docs/tdp/make_fmeca.py`) so the worksheet reflects the
> current defect log, run both gates, commit as "TDP phase 3: risk re-rating and worksheet", and stop.

## Phase 4 — Baseline revision after a run of record

**Reads:** the register rows that moved, their result files' headers, `1_blockchain-identity/results/metrics/latest/meta.json`.
**Writes:** `docs/tdp/TDP-008_CONFIGURATION_BASELINE.md` section 3 and 4. **Gate:** `python3 docs/testing/check_docs_numbers.py`.
**Stop:** every row in section 3 names the current run of record's code commit and result identity.

**Prompt.**
> A run of record has moved: <name the register rows and the after-action report>. Update
> `docs/tdp/TDP-008_CONFIGURATION_BASELINE.md` section 3 so each moved row names its new producer commit, result commit
> or run id, and identity fields, copied from the register row and the result file header. Update section 4 if any
> pin changed. Do not touch any other TDP document; the generated ones regenerate in phase 5. Run the stale-figure
> checker, commit as "TDP phase 4: baseline after <rows>", and stop.

## Phase 5 — Regeneration after any source change

**Reads:** nothing new. **Writes:** TDP-002, TDP-005, TDP-006, the six SVGs. **Gate:** the three `--check` commands
and the probe. **Stop:** CI's document step green on the commit.

**Prompt.**
> Regenerate the TDP's generated documents after the source change in <commit>: run
> `python3 docs/tdp/make_vcrm.py && python3 docs/tdp/make_fmeca.py && python3 docs/tdp/make_blueprints.py`, then
> the three `--check` commands and `bash docs/tdp/probe_tdp_checks.sh`. State in the after-action report which
> documents changed and why (a register total, a moved cell, a source constant, a CI step). Commit as "TDP phase 5:
> regenerated after <commit>", and stop.

## Phase 6 — Summary revision (Rev B)

**Reads:** `docs/tdp/TDP-001_PROGRAM_SUMMARY.md`, the register, `docs/phase2/SCOPE_RECONCILIATION.md`.
**Writes:** TDP-001. **Gate:** `python3 docs/testing/check_docs_numbers.py`. **Stop:** every number in TDP-001 is a
current V row, and section 3's readiness levels have a reason for the level met and the level withheld.

**Prompt.**
> Revise `docs/tdp/TDP-001_PROGRAM_SUMMARY.md` to Rev B. Check every number against its register row and replace any
> that moved, keeping the row citation. Re-assess each subsystem's readiness level against the DoD TRA Guidebook
> definitions quoted in section 3: raise a level only when the environment condition is met by a run of record, and
> say which. Keep section 4 ("what the programme does not claim") complete against the scope reconciliation's cut
> list. Do not add a claim, a hypothesis or an adjective. Run the stale-figure checker, commit as "TDP phase 6:
> programme summary Rev B", and stop.

## Phase 7 — Interface control after a code change

**Reads:** the changed source file, `docs/tdp/TDP-003_INTERFACE_CONTROL_DOCUMENT.md`. **Writes:** TDP-003.
**Gate:** the stale-figure checker; the field names in TDP-003 grep-match the source. **Stop:** every field, method
and reason named in TDP-003 exists in the source at HEAD.

**Prompt.**
> The interface <IF-nn> changed in <commit>. Update `docs/tdp/TDP-003_INTERFACE_CONTROL_DOCUMENT.md` so every field,
> method name and rejection reason it lists for that interface is copied from the source at HEAD (grep each one and
> show the match). Do not describe an interface the tree does not contain; planned interfaces stay in section 8.
> Commit as "TDP phase 7: IF-<nn> after <commit>", and stop.

---

## Follow-on phases (not executed in this pass)

## Phase 8 — Requirement-to-test trace (executed 2026-10-22, after-action report 27)

**Reads:** `docs/testing/test_register.yaml`, `docs/tdp/requirements.yaml`. **Writes:** a `tests` field per
requirement (test-register ids); `make_vcrm.py` extended to print and check them. **Gate:** `make_vcrm.py --check`
fails on a test id not in the register. **Stop:** every T-method requirement names at least one test or
experiment script that exists.

**Prompt.**
> Extend the verification matrix with a requirement-to-test trace. Add a `tests` list to each requirement in
> `docs/tdp/requirements.yaml` naming entries of `docs/testing/test_register.yaml` (or the experiment script, for a
> measurement). Extend `docs/tdp/make_vcrm.py` to print the trace in TDP-005 and to fail `--check` on an id that does
> not exist. Show the new check firing on a fake id, record it in the after-action report, regenerate, commit as
> "TDP phase 8: requirement-to-test trace", and stop.

## Phase 9 — Interface tests as the ICD's gate (executed 2026-10-22, after-action report 27; `docs/tdp/check_icd.py`)

**Reads:** TDP-003, the source files it names. **Writes:** `docs/tdp/check_icd.py` with `--check`; a CI line.
**Gate:** the check fails when a listed field or method is absent from the source. **Stop:** TDP-003 is held by a
check, not by reading.

**Prompt.**
> Give the interface control document a gate. Write `docs/tdp/check_icd.py` that reads
> `docs/tdp/TDP-003_INTERFACE_CONTROL_DOCUMENT.md`, extracts every backticked identifier in sections 2 to 7, and
> verifies each exists in the source file its section names (method names, field names, constants, rejection
> reasons). Add it to the CI document step and to `docs/tdp/probe_tdp_checks.sh` with a tamper probe. Show it firing on
> a fake identifier. Commit as "TDP phase 9: ICD gate", and stop.

## Phase 10 — Thesis adaptation map (executed 2026-10-21, after-action report 25; output `TDP-010_THESIS_ADAPTATION_MAP.md`)

**Reads:** TDP-002 section 3, `docs/thesis/chapter3-methodology/README.md`, `docs/thesis/chapter5-results/README.md`.
**Writes:** `docs/tdp/TDP-010_THESIS_ADAPTATION_MAP.md`. **Gate:** the stale-figure checker. **Stop:** every
shall-statement maps to a chapter section or is marked "not for the thesis".

**Prompt.**
> Write `docs/tdp/TDP-010_THESIS_ADAPTATION_MAP.md`: a table mapping each requirement of TDP-002 to the chapter
> section where its commitment is stated (chapter 3 for method, 5 for result, 6 for interpretation, 7 for
> limitation), and the sentence that would carry it, in the thesis register. Mark requirements that belong only to
> the package. Do not edit any chapter. Commit as "TDP phase 10: thesis adaptation map", and stop.

## Phase 11 — External review of the package (executed 2026-10-24 by a subagent in report 37; `docs/tdp/REVIEW_2026-10.md`)

**Reads:** the whole `docs/tdp/`. **Writes:** `docs/tdp/reviews/REVIEW_01.md` and a dispositions file.
**Gate:** every finding has a disposition. **Stop:** the review protocol of `docs/TEAM_STRUCTURE.md` section 4a
is followed: frozen checkout, different model, read-only, briefs written outside the authoring session.

**Prompt.**
> Review the technical data package under `docs/tdp/` at commit <hash> on a frozen worktree, read-only. Find what is
> wrong: a number without a V row, a limit softened relative to its register caveat, a format claim beyond "format
> only", a drawing element not traceable to a file, a requirement that adds a claim, a runbook prompt that depends on
> unrecorded context. For each finding give the file and line, the evidence, and a severity. List what was checked
> and found sound. Write `docs/tdp/reviews/REVIEW_01.md`. Do not fix anything. Stop.

## Phase 12 — Rev B issue (executed: TDP-001, 003, 007, 008, 009 in report 38; TDP-000, 004, 010 and the drawings in report 39)

**Reads:** everything above. **Writes:** every hand-written TDP document's header and TDP-PLAN section 6.
**Gate:** all checks and the probe. **Stop:** Rev B stated in every header, with the reason.

**Prompt.**
> Issue Rev B of the technical data package after <WM-2 step or review>: update each hand-written document's
> revision line and TDP-PLAN section 6 with what changed and why; regenerate the generated documents; add the
> revision row to each drawing's block. Run all checks and the probe. Commit as "TDP Rev B", and stop.
