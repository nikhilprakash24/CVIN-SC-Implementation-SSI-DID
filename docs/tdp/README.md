# TDP-000 — Technical Data Package: Index and Conventions

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-15 (after-action report 20). **Revision:** A.
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md` (numbers, claims, process). **Supersedes:** nothing; this is the first issue.
**Relation to the thesis documents:** a second reading of the same evidence, in the register of an engineering
technical data package. The thesis documents (`docs/thesis/`, `COMPOSITION.md`) argue; this package specifies,
draws, verifies and lists. Nothing here adds a measurement, a claim or a number that the claim register
(`docs/MEASUREMENT_CONDITIONS.md`) does not already hold at status V.

## 1. Purpose

A technical data package (TDP) is the set of documents sufficient to describe an item, verify it against its
requirements, and reproduce it (MIL-STD-31000B defines the term and its elements). This package applies that
definition to a research testbed whose "item" is software, data and procedure. The purpose is procedural: a reader
who has not watched the work can find, for any requirement, the drawing that shows the mechanism, the matrix row that
states its verification status, the worksheet row for each defect on its path, and the baseline that names the exact
code and toolchain behind every figure.

## 2. Document tree

| Number | Title | Kind | Governing format (format only; no certification is claimed) | Data sources | Check |
|---|---|---|---|---|---|
| TDP-000 | this index and conventions | hand-written | MIL-STD-31000B (TDP elements) | — | `check_docs_numbers.py` |
| TDP-001 | `TDP-001_PROGRAM_SUMMARY.md` — programme summary: the Heilmeier Catechism answered from the evidence; technology readiness per subsystem; the exams | hand-written | DARPA Heilmeier Catechism; DoD Technology Readiness Assessment Guidebook | register V rows; crux register | `check_docs_numbers.py` |
| TDP-002 | `TDP-002_SYSTEM_SPECIFICATION.md` — system specification: 36 shall-statements in 7 groups | **generated** by `make_vcrm.py` | MIL-STD-961E (six-section specification) | `requirements.yaml` | `make_vcrm.py --check` (CI) |
| TDP-003 | `TDP-003_INTERFACE_CONTROL_DOCUMENT.md` — interface control document: the interfaces between planes, the message and credential formats, the evidence formats | hand-written | MIL-STD-498 IDD/IRS (interface description) | source files named per interface | `check_icd.py --check` (CI): every backticked identifier exists in the section's source; `check_docs_numbers.py` |
| TDP-004 | `TDP-004_DESIGN_DESCRIPTION_AND_BLUEPRINTS.md` — design description with the six drawings | hand-written text; **generated** drawings `drawings/DWG-00n.svg` by `make_blueprints.py` | MIL-STD-498 SDD; MIL-STD-31000B with ASME Y14.100 drawing conventions | `dashboard_snapshot.json`, result files, source constants, workflows | `make_blueprints.py --check` (CI) |
| TDP-005 | `TDP-005_VERIFICATION_CROSS_REFERENCE_MATRIX.md` — requirement → method → evidence rows → status; requirement-to-test trace | **generated** by `make_vcrm.py` | MIL-STD-961E section 4 (verification cross-reference) | register, snapshot, tree, workflows | `make_vcrm.py --check` (CI) |
| TDP-006 | `TDP-006_FMECA.md` — failure mode, effects and criticality worksheet over every logged defect | **generated** by `make_fmeca.py` | MIL-STD-1629A Task 101 worksheet | `docs/DEFECT_LOG.md`, `cruxes.yaml`, `THREAT_MODEL.md` | `make_fmeca.py --check` (CI) |
| TDP-007 | `TDP-007_TEST_AND_EVALUATION_MASTER_PLAN.md` — test architecture, pre-registration protocol, gates, exams | hand-written | DoD TEMP structure (test architecture, evaluation framework, resources) | grand report; CI; pre-registrations | `check_docs_numbers.py` |
| TDP-008 | `TDP-008_CONFIGURATION_BASELINE.md` — as-built baseline: commits, runs of record, toolchain pins, producers | hand-written | MIL-STD-498 SVD (software version description) | `meta.json`, `package.json`, workflows, `producers.json` | `check_docs_numbers.py` |
| TDP-009 | `TDP-009_RISK_REGISTER.md` — programme risks on the DoD five-by-five matrix | hand-written | DoD Risk, Issue and Opportunity Management Guide (likelihood × consequence) | crux gaps; deferred items; defects | `check_docs_numbers.py` |
| TDP-010 | `TDP-010_THESIS_ADAPTATION_MAP.md` — the specification mapped onto chapter 3: state of the current text per requirement, the sentence that carries it, the drift table, chapter 3 outline v2 | hand-written | — | TDP-002; chapter 3; register; passes 21 to 24 | `check_docs_numbers.py` |
| TDP-PLAN | `TDP-PLAN.md` — the plan that produced this package and what remains | hand-written | — | — | — |
| TDP-RUNBOOK | `TDP-RUNBOOK.md` — the same plan as phases with self-contained prompts for another session | hand-written | — | — | — |

Drawings: `drawings/DWG-001.svg` general arrangement; `DWG-002` substrate assembly; `DWG-003` verification engine;
`DWG-004` freshness governor; `DWG-005` evidence line; `DWG-006` threat envelope. Each carries a title block, a
revision block, numbered notes and a bill of materials whose items name source files.

## 3. Conventions

1. **Numbers.** A figure appears in a hand-written TDP document only with its register row (`#n`) and only if that row
   is status V. Generated documents read their figures from files and name the file. The stale-figure checker scans
   every hand-written document here as it scans a chapter.
2. **Verbs.** "Shall" states a requirement (TDP-002). "Is" states what the tree contains. "Measured" states a V row.
   "Declared" states a value chosen before a run (a threshold, a band, a seed). No other modal verbs are used.
3. **Limits travel with the figure.** Every requirement, drawing note and summary line carries the register's own
   caveat for the figure it uses, unsoftened: condition tag, host, mobility model, the absence of radio.
4. **Generated, never edited.** TDP-002, TDP-005, TDP-006 and the six drawings are rebuilt by their scripts and
   compared byte for byte in CI. A change to the register, the snapshot, the defect log, the threat model, the
   workflows or the source constants the drawings read makes them stale until regenerated:
   ```bash
   python3 docs/tdp/make_vcrm.py && python3 docs/tdp/make_fmeca.py && python3 docs/tdp/make_blueprints.py
   ```
5. **Revision.** Rev A is this issue. A later issue increments the letter, adds a row to each drawing's revision
   block, and states what changed in TDP-PLAN section 6. Documents are never rewritten in place without the row.
6. **Classification banner.** Every drawing carries "UNCLASSIFIED // OPEN SOURCE (MIT) // RESEARCH TESTBED // NOT FOR
   PRODUCTION USE". It states the repository's licence and the package's status; it is not a claim of any review.
7. **Standards named are formats.** MIL-STD-961E, MIL-STD-498, MIL-STD-31000B, MIL-STD-1629A, the DoD TRA Guidebook
   and the DoD RIO Guide supply section orders, worksheet columns, scales and drawing conventions. No conformance to
   any of them is claimed, and none has been assessed by anyone outside this repository.
8. **Attribution.** Every document names its author, date, what binds it and what it supersedes (guide 2.1.8).
   The hypotheses, thrusts and design decisions are the author's (`PROVENANCE.md`).

## 4. Reading order

| Reader | Order |
|---|---|
| An examiner with ten minutes | TDP-001 sections 1 and 3; DWG-001; TDP-005 section 0 |
| A reviewer of a claim | the register row; TDP-005 reverse index (row → requirements); the drawing that shows the mechanism; TDP-006 for defects on the path |
| A successor who must reproduce a figure | TDP-008 (baseline and commands); DWG-005 (the evidence line); `docs/HANDBACK_2026-10-14.md` section 5 |
| The author adapting the package into the thesis | TDP-002 section 3 (the shall-statements become the method's commitments); TDP-009 (limitations and future work, already ranked) |

## 5. Sources for the formats

| Format | Source |
|---|---|
| Heilmeier Catechism (eight questions) | DARPA, "The Heilmeier Catechism", https://www.darpa.mil/about/heilmeier-catechism |
| Defense specification sections | MIL-STD-961E, "Defense and Program-Unique Specifications Format and Content", DoD, 2020 change; ASSIST document 36063 |
| Software document kinds (SSS, IRS, IDD, SDD, STP, STR, SVD) | MIL-STD-498, "Software Development and Documentation", 5 December 1994 (cancelled 1998; retained here for its data item descriptions) |
| Technical data package elements; drawing practice | MIL-STD-31000B, "Technical Data Packages", DoD; ASME Y14.100, "Engineering Drawing Practices" |
| FMECA worksheet | MIL-STD-1629A, "Procedures for Performing a Failure Mode, Effects and Criticality Analysis", 24 November 1980 (cancelled 1998; the worksheet is retained in practice) |
| Technology readiness levels | DoD, "Technology Readiness Assessment Guidebook", February 2025 (supersedes the 2009 and 2011 TRA guidance) |
| Risk matrix (likelihood × consequence, five by five) | DoD, "Risk, Issue, and Opportunity Management Guide for Defense Acquisition Programs", 2023 revision of the 2017 guide |
