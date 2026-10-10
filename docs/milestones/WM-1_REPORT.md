# Work Milestone WM-1 — Report

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-10 in pass 12 (after-action report 12, step W3), **before** the milestone audit, so
the audit checks this report as well as the work. **Revised after the audit** (findings cited in brackets,
e.g. [A-F1]; the full register is §14 and after-action report 12 §4); the pre-audit text is commit `d61a284`.
**Scope:** passes 8–11, commit range `db6c381..291bbca` (27 commits, all authored by the author), plus the
closing pass 12. **Not** an overall milestone: the next version, v0.9.0, is cut by the author
(`docs/milestones/README.md`, `docs/MILESTONE_NEXT.md`).
**Sources:** after-action reports 08–12; `docs/MEASUREMENT_CONDITIONS.md` (the register: every number
below with a row is quoted from it); `docs/DEFECT_LOG.md`; `docs/PLAN_2026-10-09.md` §5;
`sandbox/grand/report/GRAND_REPORT.md`; GitHub check runs; `git log`.
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`.

---

## 0. Summary

WM-1 closed the merge of the two lineages, turned the results and registers into generated,
CI-checked documents, and filled the thesis's one empty crux: infrastructure messaging (C3). That
last part went the whole way: designed, pre-registered, built, measured, reviewed adversarially,
found wanting, hardened, and re-run. Every pre-registered verdict passes on the hardened code.
The review also found that the guards which certify runs of record had never worked. No result
moved because of that: every affected run was clean on other evidence. But the evidence had been
mis-stated for two passes.

The milestone audit found more than the pass-11 review did, and some of it was serious: five register
rows still quoted the pre-merge harness run although the run had been repeated on 2026-10-09 (the
gas figures moved; the conclusions did not) [A-F1]; chapter 7 claimed H5 more strongly than the
register allows [A-F4]; two delegated results had been accepted by reading, not by a re-run gate
[P-F1]; seven V rows describe code the trunk has since changed [T-F5]; the ERC-1056 provider accepts
a revoked key when the verifier's clock lags the chain by more than 15 minutes [U-F2, open high defect
D51]; the 94.3 % W3C figure is a structural self-score that the chapters had called compliance [U-F4];
and the infrastructure verifier still has five robustness gaps for WM-2 [B-F2…F5, F8]. All 88 findings
are fixed, narrowed or deferred with an owner (§14).

| Measure | Start of WM-1 (`db6c381`) | End of WM-1 (`291bbca`) | Source |
|---|---|---|---|
| Claim-register rows (V / S / E / B) | 43 (27 / 8 / 7 / 1) | 48 (31 / 10 / 7 / 0) | register |
| Cruxes with no V evidence | 1 of 8 (C3) | 0 of 8 | `docs/thesis/CRUX_REGISTER.md` |
| Hardhat tests (passing / pending) | 536 / 23 | 536 / 23 | grand report |
| Python layers: L3, L4 and the SSI-layer suites (grand runner stage `L3+L4`) | 260 | 291 (L3 46, L4 19, SSI layer 226) | grand report |
| Feature demos / steps | 92 / 1,752 (9 repaired in pass 8) | 92 / 1,752 | grand report |
| Infrastructure L3 tests / layer mutants killed | — | 31 at the close (37 after pass 12) / 30 of 30 with the committed mutation script (the pass-11 set of 26 was not committed) [B-F1] | report 11, 12 |
| Defect log entries | D1–D27 | D1–D36 | `docs/DEFECT_LOG.md` |
| Result files with a complete stamp | 11 of 25 (pass 9's first count) | 20 of 29 in the inventory's scope (63 result JSON files are tracked; N-21) [T-F9] | stamp inventory |
| Documents scanned for superseded figures | none (no checker) | 87 at `291bbca` (96 after pass 12) | `check_docs_numbers.py` |
| CI jobs green on the closing commit | 8 of 8 | 8 of 8 | check runs |
| Contracts changed | — | **none** | `git diff db6c381 291bbca -- 1_blockchain-identity/contracts` |

After the audit (pass 12) the register reads 48 rows: 30 V, 10 S, 7 E, 1 U (#39 moved to U); Hardhat 537 and
Python layers 305 with the audit's new tests; defect log D1–D57.

---

## 1. What the milestone was asked to do

| Pass | Date | The author's brief (abridged) | Report |
|---|---|---|---|
| 8 | 2026-10-09 | after a change of assistant: get familiar; report on the switch; build a dashboard; plan SUMO visualisation; incorporate the parallel work on results and structured tests; cover the thesis cruxes (I2I, CAV identities); plan first, for audit; agentic team; report on that structure | 08 |
| 9 | 2026-10-09 | "go with the defaults and continue" | 09 |
| 10 | 2026-10-09 | "approve both designs with defaults and continue; push Infura and other decisions to the next milestone" | 10 |
| 11 | 2026-10-09 | "accept F-C with defaults and continue to the next executable" | 11 |
| 12 | 2026-10-10 | close the work as a milestone; review the plan; fix backwards; detailed report; full audit; presentation draft | 12 |

The plan executed was `docs/PLAN_2026-10-09.md` (phases P0–P5, questions Q1–Q8), under the author's
defaults. Its item-by-item status is in its §5; in short:

25 status rows cover 26 items (P4.1 and P4.2 share a row) [P-F6]; corrected after the audit [P-F7]:

| Plan status | Rows | Which |
|---|---|---|
| done | 15 of 25 | P0.1, P0.2, P0.3, P0.6, P1.1, P1.4, P2a.1, P2a.2, P2b.4, P3.4, P3.5, P3.6, P4.1–P4.2, P4.3, P5 |
| changed (done another way, reason recorded) | 3 | P0.5 (handback name), P1.2 (check by regeneration), P3.1 (TC ids from records, not titles) |
| partial | 4 | P1.3 (hypothesis panel without verdicts), P2b.1 (TraCI path untested), P2b.2 (no network drawing or inspector), P3.3 (20/29 stamped; no promote step) |
| deferred | 1 | P2b.3 (SUMO install, Q2) |
| **not done and not reported as not done** | 2 | **P3.2 `claims.yaml`** (found in pass 12's plan review); **P0.4** (the register stamping check was never recorded; the audit found the stale rows it should have caught) |

---

## 2. Timeline

| Commit | Time (UTC, 2026-10-09) | Pass | What |
|---|---|---|---|
| `dc8348c` | 01:59 | 8 | nine demos repaired after the merge |
| `0f1dbc5` | 02:04 | 8 | plan of 2026-10-09, for audit |
| `7a9a996` | 02:08 | 9 | report 09 opened |
| `ca3a44d` | 02:13 | 9 | generated dashboard snapshot and crux register |
| `3a2a806` | 02:14 | 9 | onboarding lineage imported as provenance |
| `aef16af` | 02:16 | 9 | four option READMEs; test register and coverage matrix |
| `230ac1a` | 02:19 | 9 | run-stamp helper; stamp inventory |
| `f976e57` | 02:22 | 9 | metrics-harness run of record on a clean tree |
| `5a83bc2` | 02:24 | 9 | 82 superseded figures in 12 documents fixed |
| `8885a7f` | 02:26 | 9 | grand run ALL OK |
| `d0cc19c`, `d54178e` | 02:27 | 9 | run stamp scoped to producing code (inert, found later: D33); four JS producers re-run |
| `577a5ab`, `0874b99` | 02:31–02:39 | 9 | pass 9 closed; handback 2026-10-09 |
| `cfbdcbc` | 03:42 | 10 | designs approved; **pre-registration locked before any code**; deferred list |
| `47c3314`, `1e690c3` | 03:47–03:48 | 10 | infrastructure layer, harness flags, drivers, 16 tests |
| `9006d4c` | 04:26 | 10 | first results of record I1–I5 |
| `94c2b7c`, `0ba7c6c` | 04:31–04:40 | 10 | pass 10 closed |
| `5cc39c2` | 05:18 | 11 | report 11 opened; F-C accepted |
| `b1d3f72` | 05:23 | 11 | run-identity flags fixed; CI probe |
| `98e64e4` | 05:25 | 11 | **amendments A1–A4 before any code change** |
| `f1f9e37` | 05:30 | 11 | verifier hardened; 13 I2 checks; 31 tests |
| `36e0309` | 05:41 | 11 | generated-document checks hardened |
| `601e1de` | 06:11 | 11 | results of record re-run on the hardened verifier |
| `291bbca` | 06:17 | 11 | pass 11 closed |

Commit times show when work was committed, not how long it took: the longest single steps were the
two I3 sweeps (28 and 29 min of wall clock each) and the two I1 runs (6 and 7 min).

Size of the change: 175 files, +38,505 / −23,197 lines. Of these, 66 files and ±22,150 lines are the
regenerated metrics-harness run of record; 55 Markdown files outside that run are documents (plus 26 other data, page and figure files); 28 code files carry +2,446 / −98 [P-F21, A-F15].

---

## 3. Deliverables by workstream

### 3.1 Results presentation and registers (P1, P3, P4)
| Deliverable | What it does | Guard |
|---|---|---|
| `docs/figures/make_dashboard_data.py` → `dashboard_snapshot.json`; `make_dashboard_page.py` → `results_dashboard.html` | every dashboard number from committed files; published (versions 3–5) | `--check` regenerates and compares snapshot, crux register and (since `36e0309`) the page |
| `docs/thesis/cruxes.yaml` → `CRUX_REGISTER.md` | eight cruxes C1–C8 with evidence rows and gaps | missing rows fail the build; only V rows count (since `36e0309`) |
| `docs/testing/build_register.py` → `test_register.yaml` (305 TC), `coverage_matrix.md` | TSR register derived from records; option × family matrix (T 51, T\* 40, N 78, G 13) | `--check` in CI compares against the **recorded** runs, not the test sources: a deleted test passed every guard until pass 12 added a Hardhat count gate [T-F2] |
| `docs/testing/check_docs_numbers.py` + `stale_numbers.yaml` | no superseded figure cited as current | CI; 87 files since pass 11; range arrows fixed in pass 12 |
| `docs/testing/check_stamps.py` → `STAMP_INVENTORY.md` | which results of record carry a stamp; both cleanliness flags; classes | report only; the flags themselves are probed in CI |
| `docs/testing/probe_run_identity.sh` | proves the producing-code flags fire and ignore results files | CI step; shown to fail on the pre-fix code |

### 3.2 Infrastructure messaging (P4.3; crux C3)
| Deliverable | Content |
|---|---|
| `docs/design/INFRASTRUCTURE_MESSAGING.md` | design: identities, messages, paths, threats, grounding (SAE J2735, IEEE 1609.2, ETSI TS 103 097/102 941, CAMP SCMS, NTCIP); §7 as built |
| `docs/design/INFRASTRUCTURE_PREREG.md` | I1–I5 locked before code; amendments A1–A3 (post hoc) and A4 (before the re-run) |
| `cv2x-testbed/sumo/infrastructure_layer.py` | road authority (only trusted issuer); RSU, controller, TMC credentials with permitted messages and intersection; signing as for SSI BSMs; verifier: freshness, per-receiver replay, signature, credential, subject, permitted type, field binding, warm expiry, revocation re-check every k |
| harness flags `--rsu`, `--refresh-k`, `--revoke-rsu-at`, `--trace` | off by default; the V2V counts of seed 7 are unchanged with them off and with `--trace` (19 of 19 integer counts) |
| `run_infra_stats.py`, `infrastructure_gas.js` | drivers for I1, I2, I3, I5 (30 seeds) and I4 |
| `sandbox/py-suites/L3-ssi/test_infrastructure_layer.py`, `mutation/mutate_infrastructure_layer.py` | 31 tests at the close; the audit's mutant (replay cached on the cold path only) survived them; 37 tests and a committed 30-mutant script, all killed, after pass 12 [B-F1] |

### 3.3 Visualisation (P2)
`docs/PLAN_SUMO_VISUALISATION.md` (schema `cvin-v2v-trace/1`; steps V1–V5); `render_trace.py`; two
traces of record (seed 1, `f1f9e37`); three figures, one GIF and one dashboard replay; all regenerate
byte-identically with matplotlib 3.11.2 and Pillow 12.3.0, which are not pinned (checked in pass 12 and by the audit) [P-F21, T-F15]. V4 (SUMO with real mobility) deferred (SC-22).

### 3.4 Parallel work incorporated (P3)
Onboarding lineage imported as provenance (`docs/prior-survey/`, its hazard H1 reported for
rotation: N-1); TSR plan phases 1–3 adapted; TSR second-pass sheet pre-filled (v1.1).

### 3.5 Rules and organisation
`docs/STYLE_AND_RIGOUR_GUIDE.md` (written in pass 8, amended in pass 12), `docs/TEAM_STRUCTURE.md`
(review protocol §4a, lessons §4b), `docs/MILESTONE_NEXT.md` (N-1…N-22), `docs/milestones/`.

---

## 4. Results of record produced in WM-1

### 4.1 Infrastructure messaging, pre-registered (register #44–#48; runs of record at `f1f9e37`)
| Exp. | Measure | First run (`1e690c3`) | Run of record (`f1f9e37`) | Verdict |
|---|---|---|---|---|
| I1 | median of per-run ratios, warm SPaT / warm SSI BSM verify, N=30 | 0.996 [0.995, 1.001] | **1.096 [1.091, 1.101]** | PASS (band [0.80, 1.20]) |
| I1 | SPaT warm / BSM warm / SPaT cold / SPaT sign (ms, medians of run medians); p95 of run medians | 0.163 / 0.164 / 0.452 / 0.250 | 0.182 / 0.166 / 0.477 / 0.255; p95 0.194 / 0.176 / 0.507 (no warm-up discard; A5) [A-F5] | — |
| I2 | registered checks rejected (for the expected reason), runs | 7 (reason not recorded), 30/30 | **13 of 13 (10 attacks, 3 warm variants), 30/30** [A-F9] | PASS |
| I2 | legitimate SPaT rejected | 0 of 138,895 | 0 of 138,895 | — |
| I3 | max SPaT accepted after revocation, k = 1 / 5 / 25 / ∞ | 0 / 4 / 24 / 100 | **0 / 4 / 24 / 100** | PASS (≤ k − 1; a conformance check of the re-check cadence, which cannot fail without a code change [A-F6]) |
| I3 | runs reaching the bound, k = 1 / 5 / 25 | (not recorded) | 30 / 16 / 6 | — |
| I4 | gas: key anchor; endpoint; hand to authority; rotate; revoke old key | 52,594; 34,050; 51,754; 35,498; 35,050 | 52,558–52,606; 34,038–34,050; 51,742–51,754; 35,486–35,510; 35,014–35,062 (30 runs, after the audit; the two runs of record gave narrower ranges) [A-F3, B-F9] | reported |
| I5 | sum of four operation costs, controller → RSU → vehicle (ms) | 0.840 [0.832, 0.845] | **0.886 [0.879, 0.913]**; TMC hop 0.464 | reported |

Conditions: M0 (I1–I3, I5): mock mobility, 50 vehicles, 4 RSUs, 20 s, seeds 1–30, real cryptography,
no radio, in-process back-haul and revocation registry; host Xeon 2.10 GHz × 4, Python 3.11.15,
`cryptography` 41.0.7. M1 (I4): Hardhat local, solc 0.8.24.

**Why the numbers moved between the runs.** I1 rose by about 10 %. The hardened SPaT path checks
binding, replay and expiry; the BSM path does not. That is the bias amendment A4 predicted, and it
works against SPaT (A4 predicted the direction, not the size [P-F22]). I3's counts did not move: the
re-check cadence was not changed. I4 varies in multiples of 12 gas between runs with a random RSU key
and address; this is consistent with zero vs non-zero calldata bytes (EIP-2028), but the mechanism was
not isolated. A4's expectation of identical runs failed and is reported as failed. I5 moved with I1's
components.

### 4.2 Other results re-executed in WM-1
| Result | Re-run | Outcome |
|---|---|---|
| metrics harness (#29, #30, #34–#36) | run of record `2026-10-09T02-09-36Z_7a9a996` on a clean tree | **numbers moved** (merged contracts: ERC-735 create 1,535,776 → 1,757,881; ERC-1155 lifetime +9.6 %; margins over ERC-1155 1.10× → 1.20× and over ERC-735 5.1× → 5.52×); frontier and dominance sets unchanged. **The register rows kept the old values until the audit found them** [A-F1; D43]; re-stated in pass 12. Whole-tree `dirty` false (the valid flag; D33) |
| nine-standard gas, MOBI sweep, scaling A/B, on-chain security (#25, #26, #28, H4 sweep) | four JS producers re-run with stamps at `d0cc19c` | no gas or sweep cell moved; clean shown by the tree being clean seconds before and an outputs-only commit (`d54178e`) |
| V2V, seed 7, 10 s, flags off (no-change gate) | three times (passes 10, 11, 11) | 19 of 19 integer counts identical each time (the counts compared are the integer fields of the results file; the audit compared 25 and found them identical too) [P-F26] |
| HTTP-RPC condition (#39) | **not re-run** | its run measured the pre-merge contracts; the row is U until WM-2 re-runs it [A-F1] |

---

## 5. Defects and review findings

### 5.1 Found by the generators (pass 9)
| Finding | Count | Fixed in |
|---|---|---|
| register rows inconsistent with themselves (#6 unparseable, #26 opened with **B**, #40/#41 S in claim but V in status, #25/#26 quoting superseded figures) | 5 rows | `ca3a44d` |
| superseded figures in citing documents | 82 in 12 documents | `5a83bc2` |
| vocabulary conflicts with the TSR plan (X, S letters) and other faults in the orchestrator's outputs, found by the sheet agent | 6 (5 fixed, 1 recorded) | pass 9 |

### 5.2 Found by the adversarial review (pass 11; report 11 §4)
33 findings from three reviewers on a different model, on a frozen checkout of `0ba7c6c`: 32
confirmed, 1 accepted as a judgement, none rejected.

| Reviewer | Findings | High | Medium | Low |
|---|---|---|---|---|
| claims and measurement (A) | 11 | 0 | 7 | 4 |
| code and security (B) | 11 | 2 | 3 | 6 |
| tooling and process (C) | 11 | 5 | 5 | 1 |
| **total** | **33** | **7** | **15** | **11** |

Defects of the system under test from that review, entered in the defect log in pass 12 (§F):

| Defect | Severity | What | Status |
|---|---|---|---|
| D28 | H | SPaT for another intersection accepted (no field binding) | fixed `f1f9e37` |
| D29 | H | replay inside the window accepted | fixed `f1f9e37`; residual relay limit stated |
| D30 | M | warm path ignored credential expiry; first fix inert (wrong field) | fixed `f1f9e37` |
| D31, D32 | L | malformed sender crashed; `--refresh-k 0` meant ∞ | fixed `f1f9e37` |
| D33 | M | producing-code clean flags could never fire (run stamp, harness header, metrics harness) | partly fixed `b1d3f72`; metrics harness N-19 |
| D34 | L | stamp inventory polarity inverted | fixed `b1d3f72` |
| D35, D36 | M | stale-figure checker scope/masking; dashboard check missed the page; crux evidence counting | fixed `36e0309` |

### 5.3 Found by pass 12's plan review (backward fixes)
| Finding | Fixed |
|---|---|
| P3.2 `claims.yaml` never done and never reported as not done | recorded in the plan's §5; carried to WM-2 (A5) |
| the review's defects of the system under test were not in the defect log | §F added (D28–D36) |
| infrastructure scope and the SUMO deferral had no scope-change entry | SC-21, SC-22 |
| CHANGELOG ended at 0.8.0 (July) | "Unreleased" section |
| README, thesis README and chapter 5 §5.7 did not mention the infrastructure results | added |
| stale-figure checker excused any value before an arrow, so a range ("52,170 → 1,680,816") hid a superseded figure | rule changed; 8 live stale lines fixed (test counts 217/369, 52,170, ~33×) |
| the design's I2 list had "replayed"; the pre-registration dropped it without an amendment | recorded in the design's §7 |
| visualisation step V2's gate (byte-stable figures) had never been checked | checked: all five outputs identical |
| N-14 closed in pass 11 but still listed open | closed |

---

## 6. Tests, CI and reproducibility
| Check | Value at WM-1 close | Note |
|---|---|---|
| grand runner `all` | ALL OK: smoke 11/11 adapters, L1 99, Hardhat 536, Python layers 291, 92 demos / 1,752 logged steps (594 mined transactions, the rest reads, reverts and off-chain calls; a step is a logged demonstration, not an assertion) | run at `601e1de`, committed in `291bbca` [T-F14, P-routing] |
| CI | 8 of 8 green on every closing commit (`577a5ab`, `94c2b7c`, `9006d4c`, `b1d3f72`, `f1f9e37`, `291bbca`); 29 of 30 commits in the range checked by the audit, the 30th (`d0cc19c`) has no CI run [T-F18]. Three jobs are run-only (metrics harness, compliance score, gas report) and compare nothing with committed results [T-F12] | GitHub check runs |
| generated-document checks in CI | snapshot, crux register, page, test register, coverage matrix, stale figures, run-identity probe | shown to fail on a mutated input: the page check, the stale-figure check and the probe; the others not mutation-tested |
| figure regeneration | 5 of 5 byte-identical from the committed traces | pass 12 |
| verifier mutation testing | pass 11: 26 of 26 (uncommitted set); audit: a cold-only replay mutant and three boundary mutants survived the 31 tests; pass 12: 30 of 30 with the committed script and 6 new tests | report 11; audit [B-F1] |
| no-change gate (flags off) | 19 of 19 counts identical | three times |

---

## 7. Decisions taken in WM-1
| Id | Decision | Whose | Where |
|---|---|---|---|
| Q1–Q8 | the plan's eight questions, all defaults taken | author (defaults) | plan §2, §5 |
| I-a…I-d, S-a…S-c | infrastructure and visualisation designs approved with defaults | author (defaults) | report 10 |
| F-C | I3 first run accepted despite a false whole-tree flag | author (accepted) | report 10 |
| O-A…O-D | demos committed before the audit; plan before execution; attribution; onboarding as documents only | orchestrator | report 08 |
| E-A…E-E | separate worktree for long runs; TC ids from records; scoped run stamp; stale-figure fix rule; register claim cells | orchestrator | report 09 |
| F-A, F-B, F-D | I1 at k = ∞; I3 on the same seeds; one trace of record per figure | orchestrator | report 10 |
| G-A…G-E | review on a different model in-session; harden and re-run; rows rewritten with history; no tuning after the dry run; harness flag left for its next run | orchestrator | report 11 |
| D-1…D-5 | WM-1 as a work milestone; no tag; brief-writer agent; presentation as a document; WM-2 starts after the close | **orchestrator defaults, not yet seen by the author** (written after the author's "accept defaults") [P-F13] | report 12 |
| W2-a…W2-d | start WM-2; re-run what C1/C2 move; seed or range; other decisions unchanged | **orchestrator defaults, not yet seen by the author** [P-F13] | `docs/PLAN_WM-2.md` §5 |

"Whose" distinguishes three things [P-F13]: **author (explicit)** — the author named the decision (designs
approved, F-C accepted); **author (defaults)** — the author said "go with the defaults" for a list already
written and shown; **orchestrator default** — written after the author's last message and applied without
being shown.

---

## 8. How the work was done (process metrics)
| Measure | Value |
|---|---|
| passes / after-action reports | 4 (+ the closing pass 12) / reports 08–11 (+ 12) |
| commits | 27, all authored by the author, no assistant trailer |
| delegated agents | pass 8: none (the demo-repair agent cut off by a usage limit belonged to the session before the switch; its nine demos were checked and committed in `dc8348c`); pass 9: 4 (option READMEs, onboarding import, stale figures, TSR sheet); pass 10: none; pass 11: 3 reviewers on a different model |
| delegated results accepted without the orchestrator re-running the gate | **2 of 4 in pass 9**: the onboarding import (P3.5, accepted by reading and a credential scan) and the TSR sheet (P3.6, citations read); guide rule 1.3.7 was breached and report 09 said otherwise [P-F1] |
| pre-registrations / amendments | 1 / 4 (3 post hoc, 1 before the re-run) |
| findings with a written disposition | 33 of 33 (report 11) |
| dashboard versions published | 3 in WM-1 (v3 pass 9, v4 pass 10, v5 at pass 11's close from `291bbca`; v5 had not been recorded) [P-F16]; v6 in pass 12 |

---

## 9. What went wrong, plainly
1. **Guards that never fired.** The producing-code "dirty" flags of the run stamp (written in pass 9),
   the harness header (pass 10) and the metrics harness (inherited) resolved their paths from the wrong
   directory. For two passes, reports said "dirty: false" as if it were evidence (D33).
2. **The attack set missed two attacks.** The pre-registration fixed seven attacks; the design had
   listed "replayed" and the pre-registration dropped it silently; nobody listed cross-intersection
   SPaT. The first verifier accepted both (D28, D29).
3. **Claims said more than the measurements.** "Secures", "costs exactly", "2.4 s of trust", "end to
   end", "clean tree" for a run whose tree was not. Rewritten in pass 11.
4. **A plan item vanished.** P3.2 (`claims.yaml`) was neither done nor listed as not done.
5. **A fix failed silently.** The first warm-expiry fix read a field the credential layer does not write;
   a new test caught it.
6. **An expectation was wrong.** A4 expected byte-identical I4 runs; the TSR plan had already recorded
   input-dependent gas in 14 harness cells, and the connection was not made before writing it.
7. **A checker fix created a new hole.** Pass 11's arrow rule excused range arrows; pass 12 found a
   superseded figure hidden by it; the audit then found the rule matched substrings and that ordinary
   words excused whole lines [B-F7, T-F1].

Added after the audit, which found this list selective [P-F15]:

8. **Register rows were not updated when their run was.** Pass 9 re-ran the harness on the merged
   contracts and added "re-executed" notes to #34–#36 while keeping the old numbers; this report then
   said "no number moved" [A-F1].
9. **Two delegated results were accepted by reading, not by re-running a gate** (P3.5, P3.6), and the
   report of the time said every acceptance was re-run [P-F1].
10. **Pre-registration departures were recorded late.** F-A (k = ∞ for I1) was decided before the runs
    but became an amendment only after them; I4's operation and I5's statistic changed; A4 silently
    changed the meaning of attack (d) [P-F15, A-F9].
11. **A run of record was accepted with a false whole-tree flag** (F-C, accepted by the author).
12. **Results whose code has since changed stayed V without a note** (seven rows) [T-F5].
13. **Outputs were produced before their rule was applied**: redundant figures before S-c (report 10).
14. **Execution began four minutes after the plan "awaiting audit"** was committed, under defaults the
    author had not yet seen; the nine demos were committed before the plan (O-A) [P-F15].
15. **Unrecorded checks.** The no-change gate's 19 counts and the V2 byte-identity check had no recorded
    command and output until the audit asked [P-F26].

---

## 10. Crux status at WM-1 close
| Crux | State | V evidence rows | Changed in WM-1 |
|---|---|---|---|
| C1 CAV identity substrate | partial | 7 | stamps on its producers |
| C2 Secure V2V messaging | partial | 5 | — |
| C3 Infrastructure messaging | partial | 5 (#44–#48) | **gap → partial** |
| C4 Revocation freshness | partial | 2 | #46 considered and excluded (count, not latency) |
| C5 W3C conformance | partial | 2 | — |
| C6 MOBI lifecycle | partial | 2 | — |
| C7 Privacy and linkability | partial | 1 | — |
| C8 Veracity vs automation | partial | 3 | D28–D36 add to its evidence base |

---

## 11. Threats to validity of WM-1's results
- **Mobility and radio.** Mock mobility; no channel, MAC or back-haul network (SC-21, SC-22).
- **Host.** All latency on one host; I1 compares within runs, absolute values are not portable.
- **In-process registry.** I3 has no propagation delay and no lookup cost; a chain read costs
  milliseconds (#37, #40).
- **The reviewers' independence.** Pass 11's reviewers ran on a different model but with briefs the
  orchestrator wrote; pass 12's audit narrows that with a brief-writer agent (§14). A review whose
  briefs are written outside the session is still open (N-22). The repository cannot show which model
  ran (model identifiers are excluded by rule 1.3.1), so independence rests on this statement [P-F10].
- **Code changed since stamp.** Seven V rows measured code the trunk has since changed (register note)
  [T-F5].
- **Count, not time.** I3 bounds messages; the verifier cache does not expire.

---

## 12. Handed on
| To | Items |
|---|---|
| the author (decisions; defaults stand) | N-1, N-4, N-5…N-12, N-17; F-C accepted |
| WM-2 (`docs/PLAN_WM-2.md`) | A1–A6 (pipeline: N-21, stamp helper, N-20, promote, `claims.yaml`, N-19), B1–B3 (determinism and charters), C1–C3 (review-2 carried fixes), D1–D2 (chapters; RSU-to-RSU design), E1–E2 (reviews), F1–F2 (presentation), G (N-2, N-3) |

---

## 13. Where everything is
After-action reports 08–12 · plan of 2026-10-09 (§5 status) · `docs/PLAN_WM-2.md` ·
`docs/MEASUREMENT_CONDITIONS.md` #44–#48 · `docs/DEFECT_LOG.md` §F · `docs/design/` ·
`cv2x-testbed/sumo/results/` · `docs/figures/results_dashboard.html` · `docs/testing/` ·
`docs/milestones/` (including `audit_WM-1/` and `review_pass11/`) · `docs/HANDBACK_2026-10-10.md`.

---

## 14. Audit of WM-1
**How it was run.** A brief-writer agent (a different model from the orchestrator's, fresh context) read
this report, the plans and the reports and wrote five briefs (`docs/milestones/audit_WM-1/briefs/`,
19–22 checks each, plus what it deliberately left out). Five auditor agents on a different model ran the
briefs read-only on a frozen checkout of `d61a284` (this report before revision). Their reports are
committed verbatim (`docs/milestones/audit_WM-1/findings/`). The orchestrator reproduced each high finding
before acting on it, wrote the dispositions (after-action report 12 §4), fixed what could be fixed without
changing code that produced a result of record, and deferred the rest to WM-2 with an owner.

**What it found** (counts computed from the register):

| Brief | Scope | Findings | High | Medium | Low |
|---|---|---|---|---|---|
| 1 | claims, numbers, chapters | 17 | 4 | 10 | 3 |
| 2 | code and security of what WM-1 built | 10 | 1 | 4 | 5 |
| 3 | tooling, CI, reproducibility | 18 | 2 | 12 | 4 |
| 4 | process and documents (this report included) | 27 | 1 | 19 | 7 |
| 5 | code nobody had audited (Python suites, contracts, their tests) | 16 | 4 | 8 | 4 |
| **total** | | **88** | **12** | **53** | **23** |

**The twelve high findings and what happened:**

| Finding | What | Outcome |
|---|---|---|
| A-F1 / U-F1 | register rows #29–#36 kept pre-merge harness values; #39 measured pre-merge contracts | re-stated with history; #39 → U (D43) |
| A-F2 | the superseded 1,535,776 dropped from the stale list on a stale premise | restored (D44) |
| A-F3 | gas called deterministic without "for fixed inputs"; I4 range from two runs | rule qualified; I4 over 30 runs (D45) |
| A-F4 | chapter 7 called the hybrid Pareto-optimal | scoped (D46) |
| B-F1 | replay cached on the cold path only would pass every test; mutant set not committed | 6 tests; committed 30-mutant script, 30/30 |
| T-F1 | live stale test counts | fixed; checker round 3 (D48) |
| T-F2 | deleting a test passed every guard | Hardhat count gate in CI (D47; demo count to WM-2) |
| P-F1 | two delegated results accepted by reading | report corrected; report 09 corrected |
| U-F2 | revoked ERC-1056 key accepted under clock skew | **open high defect D51**, deferred to WM-2 with the re-runs; dependent rows narrowed |
| U-F3 | four mutants survived the suites | four tests, each shown to fail on its mutant (D55) |
| U-F4 | W3C self-score presented as compliance | chapters and README narrowed |

**Dispositions.** 84 confirmed (12 deferred with an owner, 3 resolved by timing), 3 confirmed in part with
a reason, 1 accepted as the author's decision (N-23, AI-use disclosure). None rejected.

**What the audit says about WM-1.** The infrastructure results stand: every number in #44–#48 recomputed
from the committed data, and the verdicts hold. What did not stand was the paper trail around the
results: register rows lagging their runs, checks that could not fail, plan items silently dropped,
claims worded beyond the evidence, and decisions attributed to the author that the author had not seen.
The pass-11 review had caught the first layer; this audit, with briefs the orchestrator did not write and
a scope that included code nobody had reviewed, caught a second layer. The closing conditions of
`docs/milestones/README.md` are checked in after-action report 12 §6.
