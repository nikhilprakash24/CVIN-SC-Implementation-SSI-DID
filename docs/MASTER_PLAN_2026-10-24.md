# Master Plan and Atlas, 2026-10-24: All Work, Integration, the Plan Forward, Phase B Open Questions, Reading List

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-24, in after-action report 37, on branch
`claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy` at `6a7fe6c` or later.
**Purpose:** one entry point to the whole programme. It shows every phase, milestone and pass, how the lines of work
connect, what happens next, the open questions (Phase B), how every to-do and blocker fits the plan, what to read
first, and a catalogue of the project's outputs by importance and by date.
**Visual version:** the private page *CVIN-SC Master Atlas* (link in §10.3), built from this file.
**Rule:** every number here comes from a named source file. Where a source is older than today, its date is given.
This file is a map and adds no new result.

## Contents
1. [The project on one page](#1-the-project-on-one-page)
2. [Phases, milestones and passes](#2-phases-milestones-and-passes)
3. [Integration: the lines of work and how they joined](#3-integration-the-lines-of-work-and-how-they-joined)
4. [Where things stand today](#4-where-things-stand-today)
5. [The plan forward](#5-the-plan-forward)
6. [Phase B: the open questions](#6-phase-b-the-open-questions)
7. [How the to-dos and blockers fit](#7-how-the-to-dos-and-blockers-fit)
8. [What to read and review, in order](#8-what-to-read-and-review-in-order)
9. [Artifact catalogue by importance](#9-artifact-catalogue-by-importance)
10. [Artifact catalogue by date, and the published pages](#10-artifact-catalogue-by-date-and-the-published-pages)

---

## 1. The project on one page

**The thesis.** Which blockchain identity standard suits connected vehicles, measured rather than argued. Nine
Ethereum identity standards and the MOBI Vehicle Identity (VID) standard are built, tested and compared on cost,
security, W3C conformance and real-time feasibility. Source: `docs/thesis/chapter1-introduction/README.md`.

| Question | Asks | Main evidence |
|---|---|---|
| RQ1 Performance | how the nine standards compare on gas cost | register rows on gas, `docs/testing/GAS_CHARTER.md` |
| RQ2 Security | which architecture resists the V2X threat model | `docs/THREAT_MODEL.md`, security matrix |
| RQ3 W3C compliance | whether chain-rooted identities lift to W3C DIDs and credentials | W3C checker, resolver tests |
| RQ4 Real-time feasibility | whether identity checks fit the 100 ms V2X message budget | `docs/LATENCY_BUDGET.md`, `docs/testing/LATENCY_CHARTER.md` |
| RQ5 (layer 5) | zero-knowledge VIN proofs and the agent-wrapped identity | `5_zkp-agent-identity/`, register #55 to #61 |

**The five layers of code.**

| Layer | Directory | What it is |
|---|---|---|
| 1 | `1_blockchain-identity/` | the contracts for nine standards plus MOBI VID, with Hardhat tests and the metrics harness |
| 2 | `2_w3c-ssi-layer/` | W3C credentials, the DID resolver, the MOBI VID Python layer |
| 3 | `cv2x-testbed/` | the V2X testbed: lifecycle use cases, SUMO traffic runs, freshness and latency studies |
| 4 | `4_comparison-framework/` | benchmarks, scaling, security analysis, the W3C compliance checker |
| 5 | `5_zkp-agent-identity/` | zero-knowledge VIN proofs and the agent-wrapped identity |

**The method of record.** Every quoted number is a row of the claim register `docs/MEASUREMENT_CONDITIONS.md`,
marked V (verified), S (superseded), E (estimate) or U (unsupported). Every pass is an after-action report (AAR)
opened before the work and closed with CI green. The rules are in `docs/STYLE_AND_RIGOUR_GUIDE.md`.

---

## 2. Phases, milestones and passes

### 2.1 Phases
| Phase | When | What happened | Record |
|---|---|---|---|
| 0. Prior work | before 2025 | the author's earlier identity research and the CVIN-ID-SCs repository | `docs/DEVELOPMENT_HISTORY.md` §Phase 0 |
| 1. Build | 2025-11-10 to 11 | three sessions: design, MOBI VID 1.0, use cases and SUMO | `docs/DEVELOPMENT_HISTORY.md`, `SESSION_3_SUMMARY.md` |
| 2. Thesis integration | 2026-06-21 | restructure into the thesis layout | `SESSION_THESIS_INTEGRATION.md` |
| 3. Rigour passes | 2026-07 | integration, verification, tags `v0.7.0` and `v0.8.0`, PR #1 | `MASTER_UPDATE.md` (a July snapshot) |
| 4. Restoration | 2026-09-24 to 30 | GitHub restored, the CV2X testbed lineage reviewed, PR #2 | AAR 01, AAR 02, `docs/HANDBACK_2026-09-30.md` |
| 5. Evidence engineering | 2026-10-03 onward | 37 passes: sandbox, defect fixing, claim register, run identity, two milestones | AAR 03 to 37 |
| Phase 2 (research ideas) | 2026-10-14 onward | documents only until the defence (decision D-13): 26 ideas, three focuses, two deep-dive briefs | `docs/phase2/` |

The git history has 545 commits. 434 of them are from October 2026.

### 2.2 Work milestones
| Milestone | State | Steps | Record |
|---|---|---|---|
| WM-1 | closed 2026-10-10 under a four-brief audit (72 findings, all dispositioned) | passes 1 to 12 | `docs/milestones/WM-1_REPORT.md`, `docs/milestones/audit_WM-1/` |
| WM-2 | open: 15 of 20 steps done | A1 to A7, B1 to B3, C0 to C3, D1, D2, E1, E2, F1, F2 and the G hygiene list | `docs/PLAN_WM-2.md` |

**WM-2 step by step.**

| Group | Done | Left |
|---|---|---|
| A. Run identity and stamps | A1, A2, A3, A3b, A4, A5, A6, A7 | none |
| B. Determinism and statistics | B1, B2 (gas charter), B3 (latency charter) | none |
| C. Correctness fixes | C0 (verifier v3, D51), C1 (resolver reads the chain), C2 (D54 consent), C3 (freshness on one host) | none |
| D. Thesis readiness | none | D1 chapters against the register (waits on D-1), D2 RSU-to-RSU note |
| E. Review | none | E1 an outside-written review (the check session), E2 the close audit |
| F. Presentation | none | F1 presentation draft 2, F2 a deck if wanted |

### 2.3 Passes (after-action reports)
| Reports | Dates | Theme |
|---|---|---|
| 01 to 02 | 09-24 to 09-30 | restoration; the testbed lineage reviewed |
| 03 to 07 | 10-03 to 10-06 | sandbox and layered suites; the High defects fixed; parallel work reconciled |
| 08 to 12 | 10-09 to 10-10 | change of assistant; plan of 10-09; infrastructure messaging; adversarial review; **WM-1 closed** |
| 13 to 19 | 10-10 to 10-15 | WM-2 A1, A2, A4, C0, B1, B2, C3; Phase 2 opened; result cards; contribution record |
| 20, 25, 27 | 10-15 to 10-22 | Technical Data Package, from a parallel session |
| 21 to 24, 26 | 10-15 to 10-20 | C1, C2 (D54); Phase 2 deep-dive briefs; decision sheet and pre-push guard; chapter drafts |
| 28 to 31 | 10-22 | the second workstream: layer 5, the clone lineage merge, thesis record, chapter 2 |
| 32 to 33 | 10-22 to 10-23 | **one trunk** (Plan 5); A3b and A6 re-runs from clean commits |
| 34 to 36 | 10-23 | A5 claims check; B3 latency charter; A7 Python tests in the register; mutation probes |
| 37 | 10-24 | open: CI pins (U9), the I-05 model (U8), the chapter audit (U6), this master plan |

AAR 06 also has a clone-lineage sibling, `docs/AFTER_ACTION_REPORT_06_CLONE_LINEAGE.md`.

---

## 3. Integration: the lines of work and how they joined

### 3.1 The two lineages that became one trunk
Two branches grew apart from report 18 and were merged on 2026-10-22 (Plan 5, AAR 32, `docs/LINEAGE_RELATION_2026-10-22.md`).

| Lineage | Branch | Brought |
|---|---|---|
| W, the workspace (this branch) | `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy` | C1, C2, C3, the TDP, the decision sheet, the pre-push guard, the briefs |
| T, the trunk (default branch) | `claude/clone-cvin-id-scs-011CUyxScetMdSQFkuQUNLTt` | layer 5, the clone lineage (PR #3), Plans 1 to 4, a full chapter 2 |

The design conflict between them was who may attest a vehicle event (C2). W's rule was taken, because it implies T's
rule and closes D54. Register rows from T were renumbered #52 to #61 into #53 to #62.

### 3.2 Pull requests
| PR | Merged | What |
|---|---|---|
| #1 | 2026-07-24 | MOBI VID identity system with W3C DID and SSI compliance |
| #2 | 2026-09-24 | the CV2X testbed setup branch |
| #3 | 2026-10-22 | MOBI VID I section-level reconciliation; clone lineage merged |
| #4, #5 | 2026-10-22 | Plans 3 and 4: layer 5 in the thesis record; chapter 2; C1 to C3 reconciled |
| #6, #7 | 2026-10-22 | Plan 5: one trunk, and the trunk synced back to the workspace |
| #8 to #12 | 2026-10-23 | A3b and A6; A5; syncs between the trunk and the workspace |

### 3.3 Other branches in this repository
Counts are commits on that branch that are not on this one, as of `6a7fe6c`.

| Branch | Last commit | Not merged here | What it is | Integration state |
|---|---|---|---|---|
| `claude/clone-cvin-id-scs-…` (default) | 10-22 | 2 (merge commits) | the trunk | synced; this branch is 13 commits ahead |
| `claude/zkp-ai-identity-research-n5uho9` | 10-23 | 0 | layer 5's source branch | fully merged |
| `claude/cvin-research-improvements-559o01` | 10-22 | 4 | the research expansion, X1 on chain time | **open**: review and merge or record |
| `claude/simulation-visual-plan-gp4exp` | 10-22 | 3 | SUMO visuals: N = 30 traces, chapter figures, offline replay | **open** |
| `claude/system-blueprint-diagrams-fd8apg` | 10-22 | 2 | blueprint Rev B number audit, X-series figures | **open** |
| `claude/testing-suite-organization-z5j7dc` | 10-22 | 4 | the test-suite reorganisation (TSR) phases 3 and 6, as a staged patch series | **open** |
| `claude/exploration-plan` | 10-15 | 2 | related-work workspace scaffold | **open**, small |
| `vid-build` | 10-19 | 11 | the VID build work orders WO-8, WO-9 | **open**, separate base |
| `sandbox-onboarding`, `wo-s0/*` | 07-05 to 10-19 | 2 to 23 | onboarding and the understanding report | separate base, kept apart |
| `docs/root-readme` | 07-05 | 2 | an early root README | superseded |
| `claude/npat-game-planning-…` | 10-04 | 9 | an unrelated game plan | not this project |

**What this means.** Five research branches hold work this branch does not have. None has been reviewed for merge.
That is item Q-B7 in §6 and task T-12 in §7.

### 3.4 Other sessions and outside work
| Line of work | Where it lives | Connection |
|---|---|---|
| The TDP session | `docs/tdp/`, AAR 20, 25, 27 | merged; its checks run in CI |
| The second workstream (layer 5, Plans 1 to 5) | AAR 28 to 33 | merged into the one trunk |
| The cross-model check session | `docs/milestones/check_passes_16-22/` | the brief is written; the check has not run (no `FINDINGS.md`) |
| The sister "Build CV2X code" session | its own Master Plan and Atlas (§10.3) | its Phase B section is the model for §6 here. This session could not read it, because the documents connector did not connect. |
| Research and writing feeds | pages in §10.3 | parallel chats for the literature, writing and directions |
| **Rule for every session (added 2026-10-24, report 38)** | this file | before a re-run of record, push the opened after-action report naming the producers, so a session that fetches sees the claim; one run per producer, the first one counts. A change to any contract source, comments included, moves deployment gas: CI's stamp gate now fails until the gas producers are re-run or the commit is proved comment-only |

---

## 4. Where things stand today
| Measure | Value | Source |
|---|---|---|
| Claim register | 62 rows, 45 verified | `docs/MEASUREMENT_CONDITIONS.md` |
| Hardhat tests | 563 | grand run at `cea9cf0`, AAR 36 |
| Python layer tests | 376 | the same run |
| Demos | 92, with 1,758 logged steps | the same run |
| Defects | 66 logged; 42 fixed, 6 partly, 18 open (as of 10-22) | `docs/DEFECT_LOG.md`, `docs/STATUS_2026-10-22.md` |
| CI | 12 jobs in four workflows (the blueprint data check added 2026-10-31), green on every closing commit | `.github/workflows/` |
| Mutation probes | IDTx, verifier, ZK, D54 (8 of 8 killed), resolver (9 of 9 killed) | AAR 36 |
| Thesis chapters | 1 to 7 drafted; chapter 2 written §2.1 to §2.9; chapter 6 has §6.8 and §6.9 | `docs/thesis/` |

---

## 5. The plan forward

### 5.1 Next, in order
| # | Work | Produces | Waits on |
|---|---|---|---|
| 1 | U6: read-only chapter audit, **done 10-24**: 39 OK, 22 mismatch, 2 overstated, 16 unsourced, 13 stale | `docs/thesis/CHAPTER_AUDIT_2026-10.md` | the fixes are WM-2 D1, after D-1 |
| 2 | U7: read-only TDP review, **done 10-24**: 45 OK, 6 mismatch, 2 overstated, 37 stale, 11 missing (layer 5 absent) | `docs/tdp/REVIEW_2026-10.md` | corrections are task T-15 |
| 3 | U5 = WM-2 D2: RSU-to-RSU design note, **done 10-24**: recommends scope out (D2-a) | `docs/design/RSU_TO_RSU_NOTE.md` | **your D2** |
| 4 | U10: stale-figure checker, **done 10-24**: the old V2V figures found in 24 files and corrected outside the thesis; 28 thesis hits pending on D1 | checker entries | nothing |
| 5 | U11, U12, **done 10-24**: progress report draft 2; index and handback hygiene | the report, index rows | N-23 and the reader, for the final form |
| 6 | Branch review (T-12), **done 10-24**: nothing merged; 21 stale figures block the two docs-only branches | `docs/planning/BRANCH_REVIEW_2026-10-24.md` | **your B-1 to B-4** |
| 7 | WM-2 D1: edit chapters 1, 4, 6, 7 to the register | chapter edits | **D-1** |
| 8 | WM-2 E1: the cross-model check | `FINDINGS.md` | **you open the session** |
| 9 | WM-2 F1: presentation draft 2 | the report | E1 findings, so they go in once |
| 10 | WM-2 E2: the close audit | WM-2 closed | all of the above |
| 11 | Phase 2 session 4: record P2-D1; pre-register I-05's P1 | Phase 2 records | **P2-D1** |

### 5.2 After WM-2
The thesis write-up to submission, the defence, then Phase 2 builds (D-13 keeps Phase 2 to documents until then).

---

## 6. Phase B: the open questions
These are the questions the programme cannot answer by itself. Each names who answers it, what it blocks, and the
default that runs if no answer comes.

| Id | Question | Who answers | Blocks | Default if unanswered |
|---|---|---|---|---|
| Q-B1 | What AI-use statement goes in the README and the thesis, and do the reports keep the first person? (N-23) | you, under UBC policy | the progress report, sharing any page | nothing is shared |
| Q-B2 | Who reads the progress report: supervisor, committee or successor? | you | its final draft | draft stays marked |
| Q-B3 | Adopt Scope v3 and decisions D-2 to D-15 as a block? (D-1) | you | WM-2 D1, chapter edits | chapters stay as drafted |
| Q-B4 | What is the reference set for chapter 2 §2.1 to §2.5? | you | those sections being cited from sources read at origin | sections stay as written by the other session, unchecked |
| Q-B5 | Is IDTx a paper or a chapter 6 taxonomy? (I-24) | you | Phase 2 F1 plans | taxonomy only (D-7 (a)) |
| Q-B6 | Will there be a Sepolia witness run? (D-10) | you, with two secrets | the most visible open limitation | stated as a limitation |
| Q-B7 | What happens to the five open research branches (§3.3)? Reviewed: decisions B-1 to B-4 in `docs/planning/BRANCH_REVIEW_2026-10-24.md` | you | figures, the TSR series, the research expansion | they stay unmerged |
| Q-B8 | Does the thesis need RSU-to-RSU messaging? (D2; the note recommends D2-a, scope out) | you | crux C3's scope, WM-2 D2 | scoped out |
| Q-B9 | Which Phase 2 programme and ideas? (P2-D1) | you | Phase 2 session 4 | none chosen |
| Q-B10 | Does the cross-model check agree with passes 16 to 22? | the check session | WM-2 E1, E2 | WM-2 cannot close |
| Q-B11 | Does I-05's model predict the probe knee (P1: k = 12 to 14 on host 3)? | a measurement after P2-D1 | the freshness theory claim | stays a prediction |
| Q-B12 | Can the metrics harness record its host? (N-26) | the next harness run | #31, #39 becoming comparable | they stay descriptive only |

---

## 7. How the to-dos and blockers fit
Each task names what it blocks. "You" means the author. The order is the order of impact.

| Id | Task | Owner | Blocked by | Unblocks |
|---|---|---|---|---|
| T-1 | Answer N-23 (Q-B1) | you | nothing | T-9, sharing every page |
| T-2 | Run the check session | you open it; it runs alone | nothing | WM-2 E1, F1, E2 |
| T-3 | Answer D-1 and D-15 (Q-B3) | you | nothing | WM-2 D1 |
| T-4 | Name the report's reader (Q-B2) | you | nothing | T-9 |
| T-5 | Supply the chapter 2 reference set (Q-B4) | you | nothing | chapter 2 §2.1 to §2.5 checked |
| T-6 | Decide I-24 (Q-B5) | you | nothing | Phase 2 F1 |
| T-7 | Sepolia secrets or "limitation" (Q-B6) | you | nothing | D-10 |
| T-8 | U6, U7, U5, U10, **done 10-24** | this session | nothing | D1 is faster; the TDP is checked |
| T-9 | U11, U12, then the final progress report | this session | T-1, T-4 for the final form | the hand-over |
| T-10 | WM-2 D1 | this session | T-3 | E2 |
| T-11 | WM-2 F1, then E2 | this session | T-2 | WM-2 closed |
| T-12 | Review the five open branches, **done 10-24** | this session | nothing | Q-B7 |
| T-15 | Correct the TDP's stale figures and add layer 5, **done 10-24 (report 38)** | this session | nothing | the TDP current |
| T-17 | Confirm why #26's density sweep (2026-10-04) was not re-run at A3b, **done 10-31 (report 42)**: it was; the Exp. D driver writes no stamp into the shared file | this session | nothing | an empty KNOWN_STALE reason |
| T-20 | Mark `docs/PROJECT_SUMMARY.md` dated or refresh it, **done 10-31 (report 42)**: dated banner; the index points to the master plan | this session | nothing | no September snapshot listed as canonical |
| T-21 | At the next Exp. D run, have `run_verify_scaling.py` write its own stamp block into `scaling_verify.json`, then drop its KNOWN_STALE entry | this session | the next #26 re-run | the stamp gate without an exception |
| T-18 | Refresh the blueprint branch's 23 sheet sources against the register, then merge it (B-1, second half), **done 10-31 (report 40)** | this session | nothing | the blueprint set on the trunk |
| T-19 | Extend the stale-figure checker to SVG (WM-2 G, T-F16), **done 10-31 (reports 40 and 41)**: Markdown, SVG, HTML and TeX are all read | this session | nothing | figures checked like Markdown |
| T-16 | D2 answered 10-24 (out of scope); B-1 taken as recommended (exploration merged, blueprints after T-18); B-2 to B-4 open | you | nothing | the branch merges |
| T-13 | The rest of the decision sheet (P2-D*, C1-d*, C2-d*) | you | nothing | the records |
| T-14 | Commit signing, optional | you, with a key | nothing | verified commits |

**The critical path to closing WM-2:** T-2 (check), T-3 (D-1), then D1, F1 and E2. Two answers from you sit on it.

---

## 8. What to read and review, in order
| Order | Read | Why | Time |
|---|---|---|---|
| 1 | This file, §4 to §7 | the state, the plan and what needs you | 15 min |
| 2 | `docs/DECISION_SHEET_2026-10-20.md` | every decision you owe, each with a recommendation | 15 min |
| 3 | `docs/MEASUREMENT_CONDITIONS.md` | the 45 verified claims the thesis rests on | 40 min |
| 4 | `docs/thesis/chapter5-results/README.md` | the results chapter, the measured anchor | 45 min |
| 5 | `docs/thesis/chapter2-literature-review/README.md` | written by another session; needs your reference set | 45 min |
| 6 | `docs/PROGRESS_REPORT_2026-07_TO_2026-10.md` | the hand-over draft; you will sign it | 30 min |
| 7 | `docs/LINEAGE_RELATION_2026-10-22.md` | why the trunk looks as it does | 10 min |
| 8 | `docs/milestones/WM-1_REPORT.md` | the last closed milestone and its audit | 30 min |
| 9 | `docs/phase2/briefs/I-24_IDTX.md`, `I-05_FRESHNESS.md` | the two research directions you decide on | 40 min |
| 10 | `docs/thesis/CHAPTER_AUDIT_2026-10.md`, once written | what in the chapters lacks a verified row | 20 min |

To review rather than read: skim `docs/DEFECT_LOG.md` for open High defects, and `docs/testing/LATENCY_CHARTER.md`
for which latency figures may not be compared.

---

## 9. Artifact catalogue by importance
**Tier 1, the thesis rests on these.**

| Artifact | What | Why important |
|---|---|---|
| `docs/MEASUREMENT_CONDITIONS.md` | the claim register | every number in the thesis must be a V row here |
| `docs/thesis/` chapters 1 to 7 | the thesis drafts | the deliverable |
| `docs/DECISION_SHEET_2026-10-20.md` | your open decisions | two of them sit on the critical path |
| `docs/DEFECT_LOG.md` | D1 to D66 | what was wrong, who found it, what was fixed |
| `docs/THREAT_MODEL.md` | the V2X threat model | RQ2 is judged against it |
| `docs/STYLE_AND_RIGOUR_GUIDE.md` | the rules every pass follows | why the evidence is defensible |

**Tier 2, the plan and the state.**

| Artifact | What | Why important |
|---|---|---|
| This file | master plan and atlas | the entry point |
| `docs/PLAN_WM-2.md` | the open milestone | what closes before the write-up |
| `docs/STATUS_2026-10-22.md` | done, next, what needs you | the detail behind §5 and §7 |
| `docs/planning/UNBLOCKED_WORK_2026-10-23.md` | the work needing no answer | U1 to U12 |
| `docs/PROGRESS_REPORT_2026-07_TO_2026-10.md` | the hand-over draft | for the professors, after N-23 |
| `docs/LINEAGE_RELATION_2026-10-22.md` | the merge record | why two lineages became one |
| `docs/milestones/` | WM-1 report, audit, check brief | the milestone evidence |

**Tier 3, the evidence engine.**

| Artifact | What | Why important |
|---|---|---|
| `sandbox/grand/run.py` and its report | runs every suite and demo | one command reproduces the test base |
| `docs/testing/` | claims check, charters, stamps, test register | CI proves the register matches the results |
| `tools/prepush_check.sh` | CI's document guards, locally | stops a stale figure before it is pushed |
| `.github/workflows/` | 12 CI jobs | every closing commit is green |
| `docs/tdp/` | the Technical Data Package | an engineering view of the same system |
| `5_zkp-agent-identity/` | layer 5 | RQ5 |

**Tier 4, the records.** AAR 01 to 37, the handbacks, the session manifest and the meta commentaries. They show how
each result was reached and are dated history, never current figures.

**Tier 5, the ideas.** `docs/phase2/`: the programme, 26 ideas, three focuses, the briefs and the I-05 model. These
are documents only until the defence.

---

## 10. Artifact catalogue by date, and the published pages

### 10.1 Repository documents by date
| Date | Artifact | Short description |
|---|---|---|
| 2025-11-10 | the first commit, `1_blockchain-identity/`, `cv2x-testbed/` | the build begins |
| 2025-11-11 | `SESSION_3_SUMMARY.md` | use cases and SUMO |
| 2026-06-21 | `SESSION_THESIS_INTEGRATION.md` | thesis layout |
| 2026-07 | `MASTER_UPDATE.md`, `PROVENANCE.md`, tags `v0.7.0`, `v0.8.0` | the July state (superseded snapshot) |
| 2026-09-24 | AAR 01 | GitHub restoration |
| 2026-09-30 | AAR 02, `docs/HANDBACK_2026-09-30.md` | testbed lineage review |
| 2026-10-04 | AAR 04 to 06, the grand sandbox | sandbox and layered suites |
| 2026-10-09 | `docs/PLAN_2026-10-09.md`, AAR 08 to 11 | the plan of record; run identity |
| 2026-10-10 | `docs/milestones/WM-1_REPORT.md`, AAR 12 | WM-1 closed |
| 2026-10-14 | `docs/phase2/`, `docs/PLAN_WM-2.md`, AAR 15 to 17 | Phase 2 opened; WM-2 under way |
| 2026-10-15 | `docs/testing/GAS_CHARTER.md`, result cards, contribution record, `docs/tdp/` | B2; the TDP |
| 2026-10-17 | `docs/HANDOFF_2026-10-17.md`, AAR 22 | C2 (D54); hand-off |
| 2026-10-20 | `docs/DECISION_SHEET_2026-10-20.md`, `tools/prepush_check.sh`, progress report draft 1, briefs | the lead's pass |
| 2026-10-22 | `docs/LINEAGE_RELATION_2026-10-22.md`, `docs/STATUS_2026-10-22.md`, AAR 27 to 32 | one trunk |
| 2026-10-23 | `docs/testing/claims.yaml`, `docs/testing/LATENCY_CHARTER.md`, `docs/planning/UNBLOCKED_WORK_2026-10-23.md`, AAR 33 to 36 | A5, B3, A7, mutation probes |
| 2026-10-24 | `ci/requirements-ci.txt`, `docs/phase2/briefs/i05_model.py`, this file | U9, U8 |

### 10.2 Generated pages in the repository
| File | What | Regenerated by |
|---|---|---|
| `docs/figures/results_dashboard.html` | the results dashboard | `make_dashboard_page.py` |
| `docs/figures/result_cards.html` | one card per verified result | `make_result_cards.py` |
| `docs/figures/contribution_record.html` | the contribution record from git | `make_contribution_record.py` |
| `docs/presentation/report_page.html` | the presentation report | `make_presentation.py` |

### 10.3 Published pages (private, in your claude.ai gallery)
| Page | Link | What | Last updated |
|---|---|---|---|
| CVIN-SC Master Atlas | https://claude.ai/artifact/99tvf1uGNF8r8ekpWXJffM (source `docs/figures/master_atlas.html`) | the visual version of this file | 2026-10-24 |
| Programme Atlas (sister session) | https://claude.ai/artifact/3HD23T6TaRpegV24TtFDoU | the sister session's atlas | 2026-10-24 |
| Programme Master Plan and Audit Pack (sister session) | https://claude.ai/artifact/Q5Gd1ifKqgzAWUQ7xXoBQ7 | holds the Phase B section this file mirrors | 2026-10-23 |
| CVIN Status Brief | https://claude.ai/artifact/MDkTRXxMhz6QRtNnvXTk52 | the 10-22 status as a page | 2026-10-23 |
| Researcher To-Do List | https://claude.ai/artifact/GZ7xSnfCHQjuYi6ZdU8Bnm | your to-do list | 2026-10-21 |
| Programme Work Log and Status | https://claude.ai/artifact/Efjom4Lc5MCQffUktAxZ2C | work log | 2026-10-22 |
| Directions for Parallel Chats | https://claude.ai/artifact/XQjUa5D3Mkd2TBWTKqyYSn | what each parallel chat does | 2026-10-22 |
| Thesis and Paper Writing Feed | https://claude.ai/artifact/Ls8hA1XJrzxuSuhKSBaxDU | writing feed | 2026-10-22 |
| Literature and Systematic Survey Feed | https://claude.ai/artifact/RcmJqAZLcXmsLe1t1jXiaV | literature feed | 2026-10-22 |
| CVIN Research Expansion | https://claude.ai/artifact/FEQqytm8Tj9otgS3t2MnQC | research expansion | 2026-10-22 |
| CVIN Contribution Record | https://claude.ai/artifact/6kumQ7cg1tHRjiQJy7MmAp | contribution visual for the professors | 2026-10-18 |
| CVIN Result Cards | https://claude.ai/artifact/4vwTQ98TuLUgaWsiBim2Bq | result cards | 2026-10-18 |
| CVIN-SC Mission Control | https://claude.ai/artifact/4pD4FPyWcCNkHHYcnJFj7r | an earlier control page | 2026-10-15 |
| CVIN Results Board | https://claude.ai/artifact/1C5X9GpPcEwyCRDMYxYhpa | results board | 2026-10-10 |
| CVIN Results Report | https://claude.ai/artifact/EKvpiR7SxXgr4T3UWCdbAH | results report | 2026-10-10 |
| CVIN Thesis Multi-Chat Workflow Protocol | https://claude.ai/artifact/QGsLBsNaDuV65J44ZaZmnt | how the chats divide work | 2026-10-03 |

Pages older than 2026-10-22 predate the one-trunk merge, so their numbers may be superseded. The register is current.
None of these pages should be shared until N-23 is answered.
