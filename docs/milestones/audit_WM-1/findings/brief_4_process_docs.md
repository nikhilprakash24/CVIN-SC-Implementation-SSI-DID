> Verbatim final report of an independent reviewer agent (different model from the orchestrator's; fresh context; read-only on a frozen checkout). Extracted from the agent transcript by script on 2026-10-10 (after-action report 12, audit finding P-10); scratch paths normalised to `$SCRATCH`; model names redacted as `[model name]` (guide rule 1.3.1). Dispositions: after-action report 12 §4.

Brief 4 audit of d61a284: I found 1 high, 20 medium and 6 low findings. I could not write `REPORT_brief_4.md` to the scratch directory because the write tool rejected it. The full report is below, with the same content.

Paths are relative to the frozen checkout, and "AAR n" means `docs/AFTER_ACTION_REPORT_n.md`. A finding marked NOT-YET is only that something is not written yet at d61a284, so it can be re-checked at the close.

### Findings

F1 | high | docs/milestones/WM-1_REPORT.md:250 | "delegated results accepted without the orchestrator re-running the gate: 0" (AAR 09:120-121 says "every acceptance re-run by the orchestrator") | AAR 09 records two pass-9 agent results accepted without a gate re-run. P3.5 is "(delegated, accepted by reading)" (AAR 09:44), with gate "credential scan, byte comparison claimed by the agent and spot-checked" (:115). P3.6 is "(delegated, accepted by reading its citations)" (:69), with gate "sheet citations read" (:117). Style guide rule 1.3.7 (docs/STYLE_AND_RIGOUR_GUIDE.md:69) says delegated work is accepted only after the orchestrator's own re-run. So the "0" is false on the repo's own record, and the breach is not in report §9. | Give the true count (at least 2 of 4 pass-9 agents), list the breach in §9, and fix AAR 09:120.

F2 | medium | docs/milestones/README.md:27 (also :21, WM-1_REPORT.md:314, PLAN_2026-10-09.md:132 and :162, MILESTONE_NEXT.md:10, CHANGELOG.md:13, DEFECT_LOG.md:107, PLAN_WM-2.md:4) | The milestone table says WM-1 is "closed at pass 12's last commit". Other documents say "Status at the close of work milestone WM-1", "superseded at WM-1's close by `HANDBACK_2026-10-10.md`", and that the pass-12 review was already run (PLAN_2026-10-09.md:162). | Closing conditions at d61a284:
- (1) A status exists for every item, but see F6 and F7.
- (2) The report exists.
- (3) Not held: AAR 12 §4 and report §14 are placeholders. NOT-YET.
- (4) Not held: there is no register to fix against. NOT-YET.
- (5) CI is 8/8 green on d61a284 (`gh api .../commits/d61a284/check-runs`). The grand run, however, was last made before 291bbca: `sandbox/grand/report/GRAND_REPORT.md:3` says "Generated 2026-10-09T06:16:38Z at commit `601e1de`". It was not re-run after pass 12 changed the dashboard snapshot and page and the stale-figure checker.
- (6) PLAN_WM-2.md:5 says "Revised after the WM-1 audit (§7)", but §7 holds only the initial entry. NOT-YET.
- (7) `docs/HANDBACK_2026-10-10.md` does not exist. NOT-YET.

Nothing marks the milestone as provisional. | Mark WM-1 "closing, audit pending" until conditions 3-7 hold, and re-check these places at the close.

F3 | medium | docs/PLAN_2026-10-09.md:132 and docs/milestones/WM-1_REPORT.md:314 | "superseded at WM-1's close by `HANDBACK_2026-10-10.md`"; report §13 "the consolidated handback" | `git cat-file -e d61a284:docs/HANDBACK_2026-10-10.md` fails, so the file is NOT-YET. `HANDBACK_2026-10-09.md` is the "single entry point" (docs/INDEX.md:31) and has no pass-12 addendum. Its §1 is stale now. Line 17 says "19 of 28 result files fully stamped", but STAMP_INVENTORY says 20 of 29. Line 23 says "CI all 8 jobs green on `577a5ab`" next to "Python layers 291 (pass 11)". | Write the consolidated handback, and fix the §1 numbers.

F4 | medium | docs/PLAN_2026-10-09.md:145 | P3.2 is "carried to WM-2 (plan item B4)" | PLAN_WM-2.md has no B4 (only B1-B3). `claims.yaml` is step A5 (PLAN_WM-2.md:36). The report (WM-1_REPORT.md:207) correctly says A5. | Change B4 to A5.

F5 | medium | docs/PLAN_WM-2.md:19 and :68 | "draft 2 per `docs/presentation/EXPANSION_PLAN_DRAFT2.md`"; F1 "per its expansion plan" | Neither `docs/presentation/` nor `EXPANSION_PLAN_DRAFT2.md` exists at d61a284. Only WM-2 treats the file as existing; INDEX and the report do not. NOT-YET (AAR 12 step W5). | Write "to be written in W5", or re-check at the close.

F6 | medium | docs/milestones/WM-1_REPORT.md:55-61 | "done 18 of 25 ... " with a done list at :57 | PLAN_2026-10-09.md §5 (lines 126-152) has 25 table rows. The P4.1-P4.2 row is two plan items, so there are 26 items. By row, the counts are done 18, changed 2, partial 3, deferred 1, not done 1, which sum to 25. The report's "done" cell lists 19 ids: P0.1, P0.2, P0.3, P0.4, P0.6, P1.1, P1.3, P1.4, P2a.1, P2a.2, P2b.4, P3.1, P3.4, P3.5, P3.6, P4.1, P4.2, P4.3, P5. Rows and items are mixed. | State "25 rows / 26 items" or split P4.1/P4.2, so the list and the count agree.

F7 | medium | docs/PLAN_2026-10-09.md:128-152 | Status "done" for P0.4, P1.3 and P3.1 | See the three cases below.
- **P0.4** is "done | report 09", but AAR 09 has no P0.4 entry. The gate "no row describing code left unstamped" has no recorded check. As a proxy, 26 of 48 register rows contain no commit hash (rows 2-15, 20, 23, 28, 30, 31, 35, 36, 39-43). This is unconfirmed; a recorded renumbering/stamp check would confirm it.
- **P1.3** gate (a) is "hypotheses H1-H5 with verdict and evidence rows". `docs/figures/dashboard_template.html:170-175,342-344` renders only the hypothesis text and crux ids. Its source line says "verdicts with evidence in the crux register", so the panel shows no verdict and no evidence rows.
- **P3.1** gate is "TC identifiers in test titles and pytest markers ... generated from the titles". The status is "done: TC ids derived from records, not written into test titles", and author decision D-02 (N-5) is still open. The report calls P0.5 and P1.2 "changed" for deviations of this kind, but calls P3.1 "done". | Re-label P3.1 "changed" and P1.3 "partial" (or add verdict and evidence rows to panel (a)). Give P0.4 a recorded check, or mark it "not recorded".

F8 | medium | docs/PLAN_WM-2.md:16 (also MILESTONE_NEXT.md:31, WM-1_REPORT.md:306, PLAN_SUMO_VISUALISATION.md:77) | N-15 is "executable ... scheduled in `docs/PLAN_WM-2.md`"; PLAN_SUMO §7 lists "network drawing and per-vehicle inspector" under "WM-2 plan" | N-15 (extend the TSR register to the Python layers) appears only in WM-2's §1 table. No step A-G covers it, and report §12 omits it. P2b.1 and P2b.2 (TraCI path, network drawing, inspector) are listed as WM-2 open items (PLAN_WM-2.md:14), and PLAN_SUMO §7 names WM-2 as their home. WM-2 has no step for them, and §6 excludes SUMO. | Add steps, or mark these items out of WM-2.

F9 | medium | docs/design/INFRASTRUCTURE_PREREG.md:55 (also WM-1_REPORT.md:87) | Amendment A4 heading: "2026-10-09, before any code change or run of pass 11"; the report timeline says "amendments A1-A4 before any code change" | Commit b1d3f72 (05:23:33) is pass 11 and changed code: `sumo_identity_integration.py` (about 15 lines), `run_v2v_stats.py` (+5), `run_stamp.js` and `test-contracts.yml`. A4 landed in 98e64e4 (05:25:54), two minutes later. I read the diff: it is header metadata only (`PRODUCING_PATHSPECS`, `code_clean`), so no measured path changed. The sentence is still literally false, and it is repeated in the report. | Reword to "before any change to the verifier or any registered re-run".

F10 | medium | docs/AFTER_ACTION_REPORT_11.md:75-78 and WM-1_REPORT.md:181-190 | "Severity is the reviewer's"; the column header says "reviewer's severity in the full report"; the report gives 0/7/4, 2/3/6, 5/5/1 = 7/15/11 | The §4 register has no severity column. The reviewers' full reports are not in the repository. So the 7/15/11 split, "32 confirmed / 1 accepted / none rejected" and "nothing dropped" cannot be recomputed. If the table is right, it is inconsistent with the defect log: reviewer C has 5 high findings, and only C6, C9, C10 and C11 are not mapped to defects. So at least one high C finding sits in D33-D36, which the defect log rates M, L, M, M (DEFECT_LOG.md:118-121). "Different model" and "fresh context" (TEAM_STRUCTURE.md:77) also have no record in the repository, because AAR 08:49-50 forbids model identifiers. Independence therefore rests on assertion. | Commit the three reviewer outputs or add a severity column, re-derive the table, and reconcile the D33-D36 severities.

F11 | medium | CHANGELOG.md:21-23 and :25-27 | "stamp inventory, stale-figure checker, run-identity probe - all regenerated and compared in CI"; "Fixed: ... three inert producing-code clean flags (D33) and four tooling faults (D34-D36)" | Three problems:
- `.github/workflows/test-contracts.yml:46,74-76` runs the probe, `make_dashboard_data.py --check`, `build_register.py --check` and `check_docs_numbers.py`. It does not run `check_stamps.py`; report §3.1 itself says "report only".
- D33 is "partly fixed ... open for `benchmarks/run.js`" (DEFECT_LOG.md:118; N-19), so one of the three flags is still inert but is listed as Fixed.
- D34-D36 are three entries, not four. | Correct the three bullets.

F12 | medium | docs/MEASUREMENT_CONDITIONS.md:131 (#45, status V); WM-1_REPORT.md:121 and :226 | "31 tests; 26/26 mutants of the layer killed" | The 31 tests are real: pytest on `test_infrastructure_layer.py` gives 31 passed in my clone. The mutant set and the script that applied it are not in the repository (`git ls-files | grep -i mutan` is empty; AAR 11 B5 says "orchestrator re-ran an extended mutation set"). A V row and the report cite a verification that cannot be re-run. | Commit the mutants and script, or relabel the claim as unrecorded.

F13 | medium | docs/PLAN_WM-2.md:9 and :81; AAR 12:14-21 | "the author said 'accept defaults and continue'"; W2-a "Start WM-2 now ... yes ('accept defaults and continue')"; AAR 12 D-1..D-5 "Defaults taken (the author said 'accept defaults')" | The author's single message is quoted at AAR 12:6-12. D-1..D-5 and W2-a..W2-d were written afterwards by the orchestrator, so they were not put to the author before being applied. D-3 (who writes the audit briefs, and that auditors run on another model) and D-2 (no tag) are among them. Report §7 (lines 232-240) labels Q, I, S and F-C "author (defaults)" and omits D-1..D-5 and W2-a..d. WM-2 "starts" (PLAN_WM-2.md:9), although D-5 (AAR 12:21) made it conditional on the gates closing. SCOPE_CHANGES.md:33 records a thesis-scope addition as "author decisions Q1 and I-a…I-d, defaults". | Add D-1..D-5 and W2-a..d to report §7 as orchestrator defaults pending the author. Separate "author approved" from "default applied".

F14 | medium | PROVENANCE.md:91; AAR 09:48 and :54; docs/META_COMMENTARY_2026-10-09.md:1-3 and :13; WM-1_REPORT.md:3, :6 and :248 | Every WM-1 document carries "Author: Nikhil Prakash"; the report says "27 commits, all authored by the author, no assistant trailer" | These are the facts on disclosure; I give no policy opinion.
- **Disclosed:**
  - PROVENANCE.md:91 says "Implementation, experiments, measurement, drafting | AI tooling, under researcher direction". It was last changed 2026-07-23 (a9522b6), before WM-1.
  - ORIGINAL_PROMPT_AND_DIRECTION.md:127-130 says "no AI co-author trailers ... the tooling implemented and measured".
  - PROJECT_SUMMARY.md:257 says "early commits show author 'Claude'".
  - TEAM_STRUCTURE.md describes an "orchestrator" and agents without saying it is an AI until §5 (:100, "instances of the same assistant").
  - README.md, the thesis README, chapters and appendices contain no AI-use statement (`git grep -i` for "\bAI\b", "assistant" and "language model" in them finds nothing).
- **Removed text:**
  - 577a5ab removed one line from TEST_ONBOARDING.md: "🤖 Generated with [Claude Code](https://claude.com/claude-code)". AAR 09:75 calls it a broken "no-AI-attribution rule".
  - 36e0309 replaced "The [model name] pass will take it ..." in PROJECT_SUMMARY.md with "A later writing pass" (a model name).
- **Rule vs residue:** the guide (STYLE_AND_RIGOUR_GUIDE.md:60) says no assistant identifier appears in any repository artifact. "claude/..." branch names remain (HANDBACK_2026-10-09.md:6, COMPOSITION.md:147, PROJECT_SUMMARY.md:5), as do a claude.ai artifact URL (AAR 09:66) and /tmp/claude-0 scratch paths in committed results (cv2x-testbed/results/pki_vs_erc1056.json:27). AAR 11 C11 left these in place.
- **First-person attribution:** documents bylined to the author speak in the assistant's first person. Examples: "I checked the import for credentials myself" (AAR 09:48), "a fault in my own helper" (AAR 09:54), "one mine from pass 9" (AAR 11:134), "The repository carried me" (META_COMMENTARY_2026-10-09.md:13). "author (defaults)" in report §7 means only that the author said "go with defaults" (F13). | Put an AI-use statement in the thesis front matter and README, and in the WM-1 bylines. Reconcile the guide rule with the branch, URL and path residue.

F15 | medium | docs/milestones/WM-1_REPORT.md:257-272 (§9) | "What went wrong, plainly" lists seven items | Failures recorded elsewhere and missing from §9:
- (a) Three pre-registration departures, A1-A3. I1 was run at k = ∞ (F-A), decided before the runs but recorded as an amendment only after them. I4's operation was changed because ERC-1056 has no identity-level revocation. I5 was "not computable" as registered. See PREREG:39-53 and AAR 10:55-56 and :79-81.
- (b) F-C: a run of record accepted with a false whole-tree flag (AAR 10:83-86). It appears only in §7.
- (c) 4 of 17 mutants survived the first L3 suite (commit f1f9e37, AAR 11 B5). The report mentions it only in a parenthesis in §6.
- (d) The sheet agent found six defects in the orchestrator's own pass-9 outputs, among them the X/S letter conflicts, the "47 tests" CI header and the scope-log double numbering (AAR 09:72-78). The report has only a row in §5.1.
- (e) AAR 10 "what went wrong (3)": redundant figures were produced before S-c was applied (AAR 10:103-105).
- (f) Documents corrected after being cited as evidence (AAR 09:127, AAR 10:130-135, handback overstatements C10).
- (g) Execution started minutes after the plan "waits for the author's audit". Plan commit 0f1dbc5 is at 02:04:18 and AAR 09 opened at 02:08:46 (AAR 08:55-56). The nine demos were committed before audit by decision O-A.
- CI had no failures in the range: all 30 commits show 8/8, except d0cc19c, which has no check runs. | Add (a)-(f) to §9, or say §9 is selective.

F16 | medium | docs/milestones/WM-1_REPORT.md:253 and docs/PLAN_2026-10-09.md:136-137 | "dashboard versions published 3 (v3, v4, v5)"; P1.3/P1.4 "versions 3, 4, 5" | AAR 09:66 records v3 and AAR 10:94 records v4. No document records v5: AAR 11 §3 has no republish, and handback addendum 8 has no dashboard row. HANDBACK_2026-10-09.md:95 still says "version 4". The repo page changed after the last recorded publication (601e1de, 36e0309, 44dc926), so what v5 contains cannot be recovered. This is unconfirmed; the hosted version history would confirm it, and I did not check the hosted copy. | Record when and from which commit v5 was published, or drop it.

F17 | medium | docs/design/INFRASTRUCTURE_MESSAGING.md:98 | "amendment A4 restored it with 12 further checks" | A4 extends I2 from 7 to 13 checks (PREREG.md:61-72: (a)-(g), (h), (i), (j), (b-w), (c-w), (f-w)). That is 6 further checks, not 12. | Correct to 6.

F18 | medium | docs/SCOPE_CHANGES.md:33-34 | SC-21 and SC-22 | The table has 7 columns (ID, Date, Item, Change, Reason, Evidence, Thesis treatment), and the file header requires evidence and thesis treatment. Both rows have 5 cells, so those two columns are missing. SC-21 adds infrastructure messaging to the thesis scope. Chapters 1, 4, 6 and 7 do not mention SPaT or RSU (`git grep` finds nothing relevant), although AAR 10:8 default I-d promised "a paragraph in ch. 1". WM-1 scope moves with no entry include "tag, do not relocate" instead of TC ids in titles (E-B), the checker scope, and the new register row categories. | Complete the two rows and add the missing entries.

F19 | medium | docs/DEFECT_LOG.md:120 (D35) | D35 "fixed 36e0309" | Report §9 item 7 and the 44dc926 diff of `check_docs_numbers.py` show the 36e0309 fix introduced the arrow-rule hole. It hid `52,170 -> 1,680,816` and 8 live stale lines until pass 12. The log records neither the second fix nor the reopening. No entry covers the pass-9 generator findings (82 stale figures, five self-contradicting register rows), although the checklist asks for defects to be logged. D33 is rated M, but the log's own definition (DEFECT_LOG.md:8-9) makes H "affects a thesis claim or a security property", and the report says the inert guards certified runs for two passes. | Add 44dc926 to D35, log the pass-9 findings, and justify D33's M.

F20 | medium | docs/PLAN_WM-2.md:75 (§4 order) | "A1 → A2 → A3 → A5 → B1 → B2 → C3 → C1 → C2 → A6 ... A4 can run beside A3" | A3 re-runs the five stamp producers before C1 and C2. C1 (resolver) moves the W3C results. C2 (`attestEvent` restriction) moves the gas and security results, with gate "gas re-run of record for the moved cells". So A3's stamped re-runs go stale. Only A6 is placed after C2 for that reason. A4 (promote refuses dirty runs) is "beside A3", although A3's re-runs are the runs it should gate. §2 line 26 says "No new experiment ... except re-runs forced by these fixes", while §6 line 88 allows a contract change (C2). | Move the affected A3 producers after C2, and put A4 before A3.

F21 | low | docs/milestones/WM-1_REPORT.md:96-97, :36, :109, :126 | "50 files are documents"; "87 documents scanned"; "four figures, one GIF, one dashboard replay" | Recomputed with `git diff --numstat db6c381 291bbca`:
- 175 files and +38,505/−23,197 are correct.
- 66 metrics files at +22,153/−22,154 are correct.
- 28 code files at +2,446/−98 are correct.
- Markdown files outside the metrics run number 55, not 50, and 26 other files (json, yaml, png, gif, html) are unaccounted for.
- `check_docs_numbers.py` at d61a284 says "89 files scanned". 87 was true at 291bbca, and the report names no commit.
- The figures README lists 3 PNGs + 1 GIF + 1 replay JSON, which is 5 outputs, not 6. | Correct the counts and name the commit for each.

F22 | low | docs/figures/results_dashboard.html (no hit) vs WM-1_REPORT.md:158-161, docs/MEASUREMENT_CONDITIONS.md:133, chapter5-results/README.md:387 | "A4's expectation of identical runs failed and is reported as failed" | Register #47 and chapter 5 carry the statement. The dashboard shows only the I4 ranges (template line 358; grep for "did not hold|expectation" in the page gives 0). "That is the bias amendment A4 predicted": A4 (PREREG.md:75-77) says only that "any bias is against SPaT", which is a direction and not the +9.6 % size. | Add the sentence to the dashboard row, and say "direction predicted".

F23 | low | docs/PLAN_2026-10-09.md:4 vs :121 | The header says "PROPOSED, awaiting the author's audit. Nothing below P0.1 is executed until approved" | The same file now carries §5 "Status at the close of WM-1" with executed items, and the header was left unchanged. | Add a one-line header note.

F24 | low | AAR 11:78-112 vs docs/design/INFRASTRUCTURE_PREREG.md:41 and :56 | Review findings A1-A11 and amendments A1-A4 share ids | The same id means two things. Finding A4 is "(k−1)×0.1 s read as time"; amendment A4 is the verifier hardening. AAR 10:132-135 mixes both. PREREG uses "A-F2" and "B-F1", while AAR 11 uses "A2" and "B1". Eleven dispositions give "docs" or "R2 tooling" instead of a commit hash (A4, A6, A7, A11, C3-C10), which closing condition 4 wants. B10 is "Confirmed, no code change" but counted as confirmed. | Use distinct ids and commit hashes.

F25 | low | WM-1_REPORT.md:224 vs docs/STYLE_AND_RIGOUR_GUIDE.md:77 (rule 1.3.11) | CI checks are "shown to fail on a mutated input: the page check, the stale-figure check and the probe; the others not mutation-tested" | The rule written in this same pass says a guard never seen to trip "is not evidence". The pass-close checklist requires a probe for every new guard. The report admits the snapshot, crux register, test register and coverage-matrix checks have none, and does not list this as a breach in §9. Beyond AAR 11 prose, no command or output is recorded for the page and stale-figure trips. | List it as open, or add probes. Brief 3 tests the guards.

F26 | low | docs/PLAN_SUMO_VISUALISATION.md:73; WM-1_REPORT.md:126; AAR 12:36 | "V2 gate re-checked 2026-10-10: all five outputs regenerate byte-identically"; "checked in pass 12"; "N-14 closed" | No command or output is recorded anywhere (AAR 12 §3 has one line, NOT-YET). I re-ran `render_trace.py` on both committed traces into a scratch directory, and `cmp` of all five outputs was identical (matplotlib 3.11.2). The no-change gate (seed 7, 10 s) is also identical, base 0874b99 vs d61a284, across 25 integer fields. The report says "19 of 19", and no document lists the 19. The claims are unrecorded, not wrong. | Record the commands and outputs in AAR 12 §3.

F27 | low | cv2x-testbed/sumo/infrastructure_layer.py:81 and :178 (route to Brief 2) | D28 "fixed ... binding to `intersectionId`/`stationId`"; D30 "warm expiry fixed" | My PoC on d61a284 (scratch `poc2.py`) shows a SPaT with the `rsu` key removed is accepted (`no-rsu-key True None`). The station check applies only `if "rsu" in message`. The intersection check does fire (`other-intersection False binding`). Warm expiry compares with `time.time()` (line 178), not the injected clock. D31 and D32 reproduce as fixed: an unhashable or non-string `sender_did` gives `False error:TypeError`, and `--refresh-k 0` gives "error: --refresh-k must be >= 1, or inf". | Say the station binding is conditional, or make it unconditional.

### Checked and found sound

- **C1:** every commit hash in the seven documents resolves. The only missing artefacts are the ones in the findings: `HANDBACK_2026-10-10.md`, `docs/presentation/EXPANSION_PLAN_DRAFT2.md`, `claims.yaml` (documented as not done), `check_dashboard_numbers.py` (documented as changed) and the optional `docs/testing/stamp.py`.
- **C5:**
  - All 27 hashes, times (UTC to the minute), passes and order match `git log --format='%h %cI'`.
  - The range has 30 commits. All have author equal to committer (Nikhil Prakash) and no co-author trailer.
  - `git diff 7a9a996 f976e57 -- 1_blockchain-identity` touches only the benchmark/scaling/security/sweep producers and `run_stamp.js`.
  - The benchmarks tree (4984d75) and contracts tree (2e70d1f) are identical at 7a9a996 and 291bbca and equal meta.json "measured".
  - The harness run lasted 647 s (02:09:37 to about 02:20:24), before the 02:22:11 commit.
  - The contracts diff db6c381..d61a284 is empty.
- **C6 (mapping part):**
  - The findings number 33, as 11/11/11 by id.
  - D28-D36 map to B1, B2, B4, B6, B7, C1, C2, C3+C4 and C5+C7+C8, as report §5.2 and DEFECT_LOG §F say.
  - D31 and D32 reproduce as fixed (F27).
- **C7:** the DEFECT_LOG diff db6c381..d61a284 is 19 added lines only, so no earlier entry changed status. The D28-D36 severity letters equal the report's.
- **C9:** 27 commits, 4 pass-9 agents, 3 reviewers, no agents in pass 10, and 1 pre-registration with A1-A3 post hoc and A4 before the re-run all match the AARs. The exceptions are in F1, F9 and F16.
- **C10:** "I3's counts did not move" holds: 0/4/24/100 in both runs, with no cadence change in the f1f9e37 diff. The "14 non-deterministic harness cells" are recorded in `docs/planning/TESTING_SUITE_RESULTS_PLAN.md:466`, with the calldata-zero-byte cause. Register #47 and chapter 5 carry the failed identical-run expectation (the dashboard does not: F22).
- **C12:** SC numbering is continuous and unique (SC-01 to SC-14a, SC-15 to SC-22), and the SC-15..SC-20 correction note is present. SC-18 and SC-20 "Decision pending" are not treated as settled in the report.
- **C13:** I recomputed these:
  - The coverage matrix gives T 51, T* 40, N 78, G 13 (13 rows × 14 families).
  - The test register gives 305 TC (27+72+60+43+11+92).
  - The stamp inventory gives 20 of 29 (9 MISSING rows).
  - "28 and 29 min" and "6 and 7 min" match AAR 10/11 and `infrastructure_stats.json` `wall_clock_s` 422.8.
  - "0 of 138,895" matches `totals`.
  - Register rows 43 (27/8/7/1) and 48 (31/10/7/0) reproduce. The #26 B→V and #40/#41 V→S reclassifications net out.
- **C14:** N-13 and N-14 are closed in MILESTONE_NEXT, and no live document lists N-14 as open; the remaining N-14 mentions are in dated history in the handback addendum. The other N-ids map to WM-2 steps as stated (N-2 and N-3 to G, N-16 to D2, N-18 to B1, N-19 to A6, N-20 to A3, N-21 to A1, N-22 to E1), except N-15 (F8).
- **C16:** VERSION is 0.9.0-dev and the changelog's last release is 0.8.0. The register range #1-#48 is right (48 rows) and the INDEX paths I checked exist. INDEX has no row for AAR 08-12, META_COMMENTARY_2026-10-09, the dashboard or the crux register; that is a gap, not a falsehood.
- **C17 (sample):** the infrastructure numbers (1.096, 13 checks, 0/4/24, 0.886) agree in README.md:159-163, the thesis README, chapter 5, the register and AAR 11. The 43/43 security figure agrees across the documents I grepped. The default branch from `gh api` matches INDEX and plan Q6.
- **C19:** INDEX, the report and AAR 12 do not say the presentation files exist; only PLAN_WM-2 does (F5).

### Not checked (and why)

- **C2:** conditions (1) and (2) were only partly checked: statuses exist, but see F6 and F7. Condition (4) cannot be judged until a register exists (NOT-YET).
- **C3:** P1.4 ("same link", versions 3-5), P2a.2 ("schema reviewed against SAE J2945/1") and P4.3 ("design audited before code") were not verified. The hosted artifact and the external review are outside the repository.
- **C6:** the 7/15/11 recount and "no severity lowered" could not be done (F10). I followed dispositions to code only for B1, B2, B4, B6, B7, C1, C2 and A1-A3. B8, B9, B3 and C3-C9 were only spot-read, and ten further findings were not followed in depth.
- **C11:** the repository holds no transcripts and no frozen-checkout hash beyond `0ba7c6c`, so "different model" is unverifiable here.
- **C12:** the thesis chapters were checked only by the SPaT/RSU grep, for scope entries on chapter titles and thrusts.
- **C13:** I did not trace every number to a source, only the ones listed above.
- **C15:** I could not establish that #32/#37 depend on `_resolve_ethr`, because the freshness script is archived. So there is no finding on C3 running before C1.
- **C17:** this was a sample only. I grepped INVENTORY, CAPABILITIES, COMPOSITION and QUICKSTART for test counts and attack counts and found no contradiction in the sample.
- **C18:** AAR 12 §3 is almost empty (NOT-YET). The claims I could reproduce are in F26.
- **Outside this brief, noticed and not pursued, for routing:**
  - The grand report is generated at `601e1de` but cited as `291bbca` (Brief 3).
  - `check_stamps.py` is not in CI (Brief 3).
  - Commit d0cc19c has no CI check runs.
  - Committed results contain `/tmp/claude-0` scratch paths (Brief 3 or 2).
  - `benchmarks/run.js` `dirtyMeasured` is still inert (N-19, documented).
