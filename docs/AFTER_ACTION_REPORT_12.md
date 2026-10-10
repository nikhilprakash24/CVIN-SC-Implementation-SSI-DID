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
- **Recorded checks (audit P-F26).** V2 byte-identity: `python3 render_trace.py results/traces/trace_rsu_seed1.jsonl.gz --out $SCRATCH/rerender && python3 render_trace.py results/traces/trace_revocation_k5_seed1.jsonl.gz --out $SCRATCH/rerender --revocation --no-animation`, then `cmp` of each committed output against its re-render: 5 of 5 identical (matplotlib 3.11.2, Pillow 12.3.0); brief 3 reproduced the same sha256 values. No-change gate (passes 10–11): `python3 sumo_identity_integration.py --simulate --seed 7 --duration 10 --results $SCRATCH/x.json` with flags off, and again with `--trace`; every integer field of the two results files (19 at the time; the audit compared 25) equal to the pre-change baseline.
- **A slip in this pass.** Commit `a1c9cb8` was made while the stale-figure checker failed (43 hits in the newly committed verbatim reports); the failure was hidden because the check was piped into `tail`, which returns its own exit code. Fixed a minute later (`0fe7d29`: the verbatim reports are records, on the history list). CI on `a1c9cb8` is expected to fail its documents step; checks are now run unpiped before each commit.
- **W5.** `docs/presentation/make_presentation.py` generates `REPORT_DRAFT_1.md` (10 sections, ~25
  tables, 8 generated figures plus the trace figure and an architecture diagram) and the published page
  from the snapshot, the infrastructure per-run files and a process-metrics file whose every value names
  its source. Figures follow the data-viz method (validated palette; one axis; dots for independent
  runs); one headless look fixed tick rounding, a clipped label, a legend over a value and double TOC
  numbering. `--check` added to CI and shown to fail on a tampered number. Every number the draft
  prints was cross-checked against the register text. Published: https://claude.ai/artifact/EKvpiR7SxXgr4T3UWCdbAH.
  `EXPANSION_PLAN_DRAFT2.md` ranks twelve expansions.

## 4. Findings register (audit of WM-1)
Five auditors on a different model ran the briefs a separate brief-writer agent wrote (`docs/milestones/
audit_WM-1/briefs/`), on a frozen checkout of `d61a284`. Their reports are committed verbatim
(`docs/milestones/audit_WM-1/findings/`, model names redacted). Ids: A = claims (brief 1), B = code and
security (2), T = tooling and CI (3), P = process and documents (4), U = unaudited code (5). Severity is the
auditor's. The orchestrator reproduced each high finding before acting on it.

| # | Sev | Finding | Disposition | Commit |
|---|---|---|---|---|
| A-F1 | H | register #29/#30/#34–#36 kept pre-merge harness values; #39 on pre-merge contracts; report said no number moved | **Confirmed.** Rows re-stated from run `7a9a996` with history; #39 → U; report §4.2 rewritten (D43) | `8d5d25c` |
| A-F2 | H | 1,535,776 removed from the stale list on a stale premise | **Confirmed.** Restored with rounded forms; live citations fixed (D44) | `8d5d25c` |
| A-F3 | H | "gas is deterministic" unqualified; I4 spread wider than two runs | **Confirmed.** Rule and statements qualified; I4 re-run 30 times and re-reported as ranges (D45) | `8d5d25c` |
| A-F4 | H | chapter 7: H5 "Pareto-optimal" against #36 | **Confirmed.** Scoped to the fidelity-per-gas plane; dominance by ERC-4337 stated (D46) | `8d5d25c` |
| A-F5 | M | latency rows lack p95; no warm-up discard | **Confirmed.** p95 of run medians added; deviation in rows and amendment A5 | `8d5d25c` |
| A-F6 | M | I3 PASS shown without its conformance-check caveat | **Confirmed.** Caveat in README, crux C3, dashboard, thesis README, report | `8d5d25c`, `a1c9cb8` |
| A-F7 | M | live stale test counts; markers excused whole lines | **Confirmed.** Lines fixed; patterns widened; markers explicit only (D48) | `8d5d25c` |
| A-F8 | M | "Python layers L3 + L4: 291" includes 226 SSI-layer tests | **Confirmed** (orchestrator recount 46 / 19 / 226). Labels fixed in runner, dashboard, report, presentation | `8d5d25c` |
| A-F9 | M | (d) changed meaning in A4; 13 checks are 10 attacks + 3 warm; "12" should be 6 | **Confirmed.** Amendment A5; wording fixed in register, design, chapters, dashboard | `8d5d25c` |
| A-F10 | M | chapter 4 web3 v7, "6-stage", chapter 5 "most expensive" | **Confirmed in part.** web3 and ERC-725xy wording fixed; "6-stage" matches the code (proof metadata sits inside the signature stage) and was made explicit | `8d5d25c` |
| A-F11 | M | chapter 1 H1 includes update; tested for creation only | **Confirmed.** Note in chapter 1 that the update half is not supported (3.4× / 3.9×) | `8d5d25c` |
| A-F12 | M | chapter 6 §6.4 "confined to two places" (N-6) | **Confirmed.** Reworded (two failures and one PARTIAL, verified in the result file); N-6 closed | `8d5d25c` |
| A-F13 | M | dashboard shows two BSM warm values without a note; I1 label overclaims | **Confirmed.** Host note and k = ∞ label in the infrastructure panel | `8d5d25c` |
| A-F14 | M | design §7 omits I4 and I5 changes | **Confirmed.** Rows added (and I4's unmeasured issuance cost stated) | `a1c9cb8` |
| A-F15 | L | "50 files are documents" | **Confirmed.** 55 Markdown files outside the harness run | `a1c9cb8` |
| A-F16 | L | chapter 7: attacks "over 1.65 M verifications" | **Confirmed.** 5 attack types, 150 of 150 rejected; no benign message rejected | `8d5d25c` |
| A-F17 | L | chapters 1, 4, 6, 7 silent on infrastructure | **Confirmed; deferred** to WM-2 D1 (disclosed in SC-21) | — |
| B-F1 | H | replay cached on the cold path only survives the 31 tests; 26-mutant set not committed | **Confirmed** (orchestrator reproduced via the committed script). 6 tests added; 30-mutant script committed, 30/30 killed | `8d5d25c` |
| B-F2 | M | deeply nested message crashes the process | **Confirmed; deferred** (D37, WM-2 C0 with re-run) | — |
| B-F3 | M | field binding fails open | **Confirmed; deferred** (D38, C0). The harness credentials carry the claims, so I2(h) stands | — |
| B-F4 | M | refresh_every accepts nan/inf/floats; CLI crash | **Confirmed; deferred** (D39, C0) | — |
| B-F5 | M | credential validity ignores the injected clock | **Confirmed; deferred** (D40, C0) | — |
| B-F6 | L | warm I2 variants not asserted warm | **Confirmed; deferred** (D42, C0); data show cold False in 30/30 | — |
| B-F7 | L | arrow rule matches substrings | **Confirmed.** Whole-number match; the auditor's counter-example now flagged | `8d5d25c` |
| B-F8 | L | DID method and chain not validated | **Confirmed; deferred** (D41, C0) | — |
| B-F9 | L | I4 range from two samples | **Confirmed.** 30 runs committed; #47 re-reported | `8d5d25c` |
| B-F10 | L | trace schema doc differs from the traces | **Confirmed.** As-built schema in the visualisation plan §7.1 | `a1c9cb8` |
| T-F1 | H | live stale test counts missed by patterns and markers | **Confirmed** (same as A-F7) | `8d5d25c` |
| T-F2 | H | no guard notices a deleted test or demo | **Confirmed; partly fixed.** CI Hardhat count gate against the grand report, shown to fail on 535; demo count → WM-2 G (D47) | `8d5d25c` |
| T-F3 | M | no check ties register numbers to result files | **Confirmed; deferred** to WM-2 A5 (claim cross-check) | — |
| T-F4 | M | §5.F names the inert `dirtyMeasured` as the criterion | **Confirmed.** Correction in §5.F; N-19 unchanged | `8d5d25c` |
| T-F5 | M | #27 "merged trunk" wrong; seven V rows' code changed since their stamp | **Confirmed.** #27 reworded; register note; inventory column "code changed since" (per-producer paths); re-runs WM-2 A3b (D50) | `8d5d25c` |
| T-F6 | M | testbed lock pins OpenZeppelin 5.4.0; artifacts reproduce only with the root install | **Confirmed.** Documented in `cv2x-testbed/QUICKSTART.md`; pin → WM-2 G | `a1c9cb8` |
| T-F7 | M | requirements.txt not installable; deps missing | **Confirmed.** QUICKSTART gives the working install; the file → WM-2 G | `a1c9cb8` |
| T-F8 | M | "run alone on the host" not evidenced | **Confirmed.** Reworded to what the record shows; run log committed | `a1c9cb8` |
| T-F9 | M | stamp inventory scope 29 of 63 not stated | **Confirmed.** Scope stated in the report; widening is N-21 | `a1c9cb8` |
| T-F10 | M | run-stamp scope misses imported producer code | **Confirmed; deferred** (D49, WM-2 A2) | — |
| T-F11 | M | CI not triggered by PRs into the default branch | **Confirmed.** PR triggers on any base branch in all three workflows | `8d5d25c` |
| T-F12 | M | three CI jobs are run-only | **Confirmed.** Stated in the report; compare steps → WM-2 G | `a1c9cb8` |
| T-F13 | M | L1 and demo gas vary between runs; N-18 understated | **Confirmed.** Rule amended; N-18 widened with the audit's counts | this pass |
| T-F14 | M | smoke count only on the console; steps are logged lines, not assertions | **Confirmed.** Runner records the adapter count and step kinds; report wording fixed | `8d5d25c`, `a1c9cb8` |
| T-F15 | L | figure byte-identity depends on unpinned matplotlib/Pillow | **Confirmed.** Stated in the figures README; pins → WM-2 G | `a1c9cb8` |
| T-F16 | L | HTML dossiers state superseded figures; non-Markdown not scanned | **Confirmed.** Dossiers marked dated (manifest, INDEX); non-Markdown scan → WM-2 G | `a1c9cb8` |
| T-F17 | L | checker misses some number forms | **Confirmed in part.** ASCII x, no tilde, decimal comma, "percent" added; split-line and other forms remain (stated) | `8d5d25c` |
| T-F18 | L | `d0cc19c` has no CI run | **Confirmed.** Recorded in the report | `a1c9cb8` |
| P-F1 | H | "0 delegated results accepted without a re-run gate" is false (P3.5, P3.6) | **Confirmed.** Report §8 corrected; post-close correction in report 09 | `a1c9cb8` |
| P-F2 | M | milestone called closed before its conditions held | **Confirmed (timing).** Conditions checked at the close commit (§6) | close |
| P-F3 | M | consolidated handback missing; old handback §1 stale | **Confirmed (timing).** `HANDBACK_2026-10-10.md` written (`d877a4f`); the old one marked historical | `d877a4f`, `a1c9cb8` |
| P-F4 | M | P3.2 carried to "B4" (no such step) | **Confirmed.** A5 | `a1c9cb8` |
| P-F5 | M | PLAN_WM-2 cites a presentation file not yet written | **Confirmed (timing).** Written in W5 (`c363358`) | `c363358` |
| P-F6 | M | plan rows vs items mixed in the count | **Confirmed.** 25 rows / 26 items stated; recount 15 / 3 / 4 / 1 / 2 | `a1c9cb8` |
| P-F7 | M | P0.4 unrecorded; P1.3 partial; P3.1 changed | **Confirmed.** Status table and report corrected | `a1c9cb8` |
| P-F8 | M | N-15 and P2b items had no WM-2 step | **Confirmed.** A7 added; P2b items marked out of WM-2 (need N-4) | `a1c9cb8` |
| P-F9 | M | A4 "before any code change" literally false | **Confirmed.** Amendment A5 states it; report wording fixed | `8d5d25c`, `a1c9cb8` |
| P-F10 | M | pass-11 severities and independence unrecomputable from the repository | **Confirmed.** Reviewer reports committed verbatim (model names redacted); severities recompute to 7 / 15 / 11; scale note in the defect log; independence stated as unverifiable | `8d5d25c` |
| P-F11 | M | CHANGELOG overstates (stamp inventory in CI; D33 fixed; four faults) | **Confirmed.** Corrected | `a1c9cb8` |
| P-F12 | M | 26/26 mutants unrecorded | **Confirmed** (same as B-F1) | `8d5d25c` |
| P-F13 | M | orchestrator defaults presented as the author's | **Confirmed.** Decision table distinguishes author-explicit, author-defaults and orchestrator-default | `a1c9cb8` |
| P-F14 | M | no AI-use statement; first-person assistant voice under the author's byline | **Accepted as the author's decision** (N-23); the orchestrator changes no byline or disclosure on its own | `a1c9cb8` |
| P-F15 | M | "what went wrong" was selective | **Confirmed.** Eight items added | `a1c9cb8` |
| P-F16 | M | dashboard v5 unrecorded | **Confirmed.** Recorded (from `291bbca` at pass 11's close); v6 at this close | `a1c9cb8` |
| P-F17 | M | "12 further checks" (6) | **Confirmed.** Fixed | `8d5d25c` |
| P-F18 | M | SC-21/22 missing columns; chapters silent on SC-21 | **Confirmed.** Columns added; chapters → WM-2 D1 | `a1c9cb8` |
| P-F19 | M | D35 reopening and D33 severity unexplained; pass-9 generator findings not logged | **Confirmed in part.** D35 and severity notes added; the pass-9 findings were documentation faults, recorded in the report §5.1, not logged as code defects (reason stated) | `8d5d25c` |
| P-F20 | M | WM-2 order makes A3's re-runs stale | **Confirmed.** Order revised | `a1c9cb8` |
| P-F21 | L | counts (55 files; 89 vs 87 scanned; 5 outputs) | **Confirmed.** Corrected with the commit each count belongs to | `a1c9cb8` |
| P-F22 | L | dashboard lacks the failed-expectation note; A4 predicted direction only | **Confirmed.** Both fixed | `8d5d25c`, `a1c9cb8` |
| P-F23 | L | plan header still "awaiting audit" | **Confirmed.** Header note added | `a1c9cb8` |
| P-F24 | L | id collisions (A1 finding vs A1 amendment); dispositions without hashes | **Confirmed.** Note in report 11; this register uses A-F/B-F/T-F/P-F/U-F ids and hashes | `a1c9cb8` |
| P-F25 | L | guards without a mutation probe | **Resolved by the audit itself:** brief 3 (C2) mutation-tested the snapshot, crux register, page, test register and coverage matrix checks; all failed as they should. The test-count gate is new and shown to fail | — |
| P-F26 | L | no-change gate and V2 check commands unrecorded | **Confirmed.** Recorded in §3 of this report | `a1c9cb8` |
| P-F27 | L | binding conditional; expiry uses wall clock | **Confirmed** (same as B-F3, B-F5); deferred to C0 | — |
| U-F1 | H | register #34 kept pre-merge values | **Confirmed** (same as A-F1) | `8d5d25c` |
| U-F2 | H | ERC-1056 provider accepts a revoked key when the verifier's clock is >900 s behind the chain; test not idempotent | **Confirmed** (orchestrator read the code; the auditor's reproduction is in its report). **Deferred** to WM-2 (D51, H): the fix changes resolution cost that #21/#32/#37 measure; those rows and crux C4 now state the clock assumption (guide rule 1.2.4) | this pass |
| U-F3 | H | four mutants survive: VC proof options unsigned, rollback never flagged, forged attestation valid, D2 reverted | **Confirmed.** Tests added for all four; each shown to fail on its mutant (D55) | this pass |
| U-F4 | H | 94.3 % called compliance/conformance; it is a structural self-score; a third deviation undisclosed; thesis README 13/15 | **Confirmed.** Chapters 5.5, 6.4, 7, thesis README and README narrowed to "structural self-score"; status-method deviation stated; 14/15 corrected; register #4 carries the audit's classification | this pass |
| U-F5 | M | resolver synthesises documents (no chain read); its latency figure is stale | **Confirmed.** Chapter 4 states it; the register's resolution-latency figure marked superseded pending WM-2 C1 | this pass |
| U-F6 | M | external-suite limits not carried to README/H2 | **Confirmed.** README and chapter 5 state 336 generated tests on three recorded outputs, dereferencing not run, registry-minted run adds no resolver evidence | this pass |
| U-F7 | M | CI `python-layers` reports 27 skips as success | **Confirmed.** Node, compile and a skip gate added to the job | this pass |
| U-F8 | M | threat model counts and paths wrong; ERC-1056 signed digest lacks the chain id | **Confirmed.** Counts and paths fixed; G3 narrowed; D52 (upstream behaviour, author decision via N-9) | this pass |
| U-F9 | M | D15, D23, D26 confirmed by PoC; new zero-identity defect; D22 open parts missing from §C; recovery claims uncaveated | **Confirmed.** D53 logged; D22 rest added to §C; D15 caveat at every "genuine on-chain key recovery" claim | this pass |
| U-F10 | M | `attestEvent` lets any role-holder attest any vehicle; duplicates | **Confirmed.** D54; threat model G4 narrowed; WM-2 C2 | this pass |
| U-F11 | M | gas varies with random keys; `hardhat test` rewrites tracked files | **Confirmed.** Determinism rule already amended (A-F3); file rewriting is D56 → WM-2 G | this pass |
| U-F12 | M | the on-chain security script accepts any revert | **Confirmed.** "43/43" now stated as the strict harness's result in README and threat model | this pass |
| U-F13 | L | duplicate `_registered_key_for` (dead code) | **Confirmed; deferred** (D57, WM-2 G) | — |
| U-F14 | L | README and #4 state CI floor 93.0 (it is 94.0) | **Confirmed.** Fixed | this pass |
| U-F15 | L | demo steps are not assertions | **Confirmed** (same as T-F14) | `8d5d25c` |
| U-F16 | L | create-cost definition differs by standard; chapter 7 silent | **Confirmed.** Chapter 7 states the definition and that a clone variant was not measured | this pass |

**Totals** (computed from the table above by script, not typed). 88 findings: 12 high, 53 medium, 23 low
(brief 1: 17, brief 2: 10, brief 3: 18, brief 4: 27, brief 5: 16). Dispositions: 84 confirmed — of which 12
deferred to WM-2 with an owner and 3 resolved by timing (the item was written later in this pass) — 3
confirmed in part with a stated reason (A-F10: "6-stage" matches the code; T-F17: some number forms remain;
P-F19: the pass-9 entries were documentation faults, not code defects), and 1 accepted as the author's
decision (P-F14, N-23). None rejected. A first draft of this sentence gave typed totals that the recount
contradicted; it was corrected before commit.

## 5. Decisions

## 6. Closing — *(written last)*
