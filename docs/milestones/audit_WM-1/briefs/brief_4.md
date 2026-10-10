# Brief 4 - Process and documents: is the milestone report (and the plans, reports and logs around it) accurate and mutually consistent?

## 1. Scope

**Question this brief answers:** does the paper trail of WM-1 say what actually happened, in every document, and
does the milestone satisfy its own closing conditions? Every statement of fact in the milestone report, the
plan status table, the after-action reports, the defect log, the scope log and the deferred list is a claim to
check against git history, file existence and each other.

**Documents**
- `docs/milestones/WM-1_REPORT.md` (the report under audit), `docs/milestones/README.md` (the closing conditions).
- `docs/PLAN_2026-10-09.md` (its §5 status table), `docs/PLAN_WM-2.md`, `docs/MILESTONE_NEXT.md` (N-1 ... N-22).
- `docs/AFTER_ACTION_REPORT_08.md`, `_09`, `_10`, `_11` (findings register §4), `_12` (opened; §3-§6 still empty).
- `docs/STYLE_AND_RIGOUR_GUIDE.md` (amended in pass 12), `docs/TEAM_STRUCTURE.md` (§4a review protocol, §4b lessons).
- `docs/DEFECT_LOG.md` (§F, D28-D36; and the earlier entries' status), `docs/SCOPE_CHANGES.md` (SC-21, SC-22 and numbering), `docs/INDEX.md`, `CHANGELOG.md` ("Unreleased"), `VERSION`, `docs/HANDBACK_2026-10-09.md` (+ addenda), `docs/META_COMMENTARY_2026-10-09.md`, `docs/SESSION_MANIFEST_2026-09.md`, `docs/DEVELOPMENT_HISTORY.md`, `PROVENANCE.md`, `docs/prior-survey/README.md`.
- Git history: `git log db6c381..d61a284` (30 commits: 27 in the milestone range, 3 in pass 12).

## Common context (read first; identical in all five briefs)

**The repository.** A master's-thesis research repository (author: Nikhil Prakash, UBC ECE) on blockchain /
self-sovereign identity (SSI) for connected vehicles. It holds: Solidity contracts for nine identity
standards (Hardhat, `1_blockchain-identity/`), a Python W3C DID / Verifiable-Credential layer
(`2_w3c-ssi-layer/`), a V2V / V2I message-path testbed with a mock-mobility simulation harness
(`cv2x-testbed/`), a comparison framework and committed result files (`4_comparison-framework/`), a
"sandbox" with per-option demos and test layers (`sandbox/`), a claim register
(`docs/MEASUREMENT_CONDITIONS.md`, rows #1-#48; status V = verified, S, E, B, ...), generated dashboards and
registers (`docs/figures/`, `docs/testing/`, `docs/thesis/`), and thesis chapters (`docs/thesis/chapter1..7`).

**The work under audit.** Work milestone WM-1 = passes 8-11, commit range `db6c381..291bbca` (27 commits),
plus the closing pass 12 (commits `3e19e72`, `44dc926`, `d61a284`) which made "backward fixes" and wrote the
milestone report. WM-1's headline content: merge closure; generated, CI-checked documents (dashboard,
crux register, test register, stale-figure checker, run-stamp / "dirty flag" tooling); and a new
infrastructure-messaging layer (roadside units, signal controllers, a traffic-management centre as
credentialed DIDs; signed SPaT messages) with five pre-registered experiments I1-I5 (register rows #44-#48),
an adversarial review in pass 11, hardening, and a re-run. The milestone report
(`docs/milestones/WM-1_REPORT.md`) was written BEFORE this audit, so the report is itself under audit.
The orchestrating assistant did the work and wrote the report; you are independent of it. Nothing it wrote
is evidence of its own correctness: re-derive.

**Frozen checkout (read only).** `$SCRATCH/audit_d61a284` (commit `d61a284`). Do not edit, commit, push, stash, `git worktree add`,
`git checkout`, or run anything that writes inside it. Do NOT touch `/home/user/CVIN-SC-Implementation-SSI-DID`.
`node_modules` is available through a symlink in `$SCRATCH/audit_d61a284/1_blockchain-identity`. When you need a writable copy,
clone locally into your scratch directory: `git clone -q $SCRATCH/audit_d61a284 $SCRATCH/audit_scratch/brief-4/clone && ln -s $SCRATCH/audit_d61a284/1_blockchain-identity/node_modules $SCRATCH/audit_scratch/brief-4/clone/1_blockchain-identity/node_modules`
(the clone is yours to modify; old commits are reachable in it with `git -C $SCRATCH/audit_scratch/brief-4/clone show <rev>:<path>` or `git archive`).

**Hard rules for commands.**
- Write only to your scratch directory `$SCRATCH/audit_scratch/brief-4/` (create it).
- Long experiments (the 30-run sweeps of ~7-30 min: `run_infra_stats.py`, `run_v2v_stats.py`, `run_verify_scaling.py`, `npm run metrics`, `benchmark_scaling.js`, the I3 revocation sweep) must NOT be re-run. Recompute from the committed JSON instead.
- Allowed short runs: a single seed of the harness (seconds), the pytest suites, `npx hardhat test` (about 25-60 s) and single Hardhat scripts, the document generators in `--check` mode, `git`, `grep`, `python3 -I`, `node`. A Hardhat node, if you need one, must use a non-default port (for example 18548) and you must kill it by recorded pid.
- When running `cv2x-testbed/sumo/sumo_identity_integration.py` ALWAYS pass `--results $SCRATCH/audit_scratch/brief-4/<name>.json` (its default overwrites a committed file). Run it from a clone, not from `$SCRATCH/audit_d61a284`.
- Network is available only through a proxy; do not rely on it except for `gh api repos/nikhilprakash24/CVIN-SC-Implementation-SSI-DID/...` read calls (CI check runs) where a check says so. If the network call fails, say so under "Not checked".
- Installed toolchain at audit time: Python 3.11.15, Node 22, pytest 9.1.1, eth-account 0.14.0, cryptography 41.0.7, coincurve 21.0.0, web3 8.0.0, matplotlib 3.11.2, numpy 2.4.6, PyYAML 6.0.1. Differences from CI (unpinned installs) are themselves worth noting but are not findings unless they change an outcome.

**Mindset.** Be adversarial. The audit exists because the people who did the work chose the earlier review's
scope. Prefer checks that could FAIL. For every "passes / is verified / is covered / is CI-checked / byte-identical /
N of N" statement you meet, ask: what would the check look like if the claim were false, and does the
existing check actually distinguish the two? Look especially in places the milestone report does not mention.
If you find a claim you cannot verify because the evidence is not in the repository (for example a script
or data set that is described but not committed), that IS a finding (irreproducibility), with severity medium
or higher if a register number depends on it.


## 2. Numbered checks

**C1. Does every artefact the report and plans name exist?** Extract every backticked path, every 7-40-hex commit hash and every document title from `WM-1_REPORT.md`, `milestones/README.md`, `PLAN_2026-10-09.md` §5, `PLAN_WM-2.md`, `AFTER_ACTION_REPORT_12.md`, `MILESTONE_NEXT.md` and `INDEX.md`; check each path with `git cat-file -e d61a284:<path>` and each hash with `git cat-file -e <hash>^{commit}`. Already visible: the plan's status table and the report refer to a consolidated `HANDBACK_2026-10-10.md` ("superseded at WM-1's close by"; report §13 "the consolidated handback"; milestones README closing condition 7) and `docs/PLAN_2026-10-09.md` says `P3.2` is "carried to WM-2 (plan item B4)". Confirm those, and find all others (e.g. `docs/presentation/`, `EXPANSION_PLAN_DRAFT2.md`, `docs/planning/TESTING_SUITE_RESULTS_PLAN.md`, `docs/planning/TESTING_SUITE_SECOND_PASS_SHEET.md`).

**C2. Closing conditions applied literally.** `docs/milestones/README.md` lists seven conditions for closing a work milestone. For each, state whether it holds at `d61a284` and what the milestone table says (the table marks WM-1 "closed at pass 12's last commit" and names the audit location). In particular: (3) an audit with a findings register where every finding has a disposition (report §14 and AAR 12 §4 are empty at `d61a284`; is the milestone nevertheless presented as closed anywhere - README table, INDEX, CHANGELOG, handback, MILESTONE_NEXT header "Status at the close of work milestone WM-1"?); (4) confirmed findings fixed; (5) grand run ALL OK and CI green on the closing commit (which commit is closing: `291bbca` or `d61a284`; see Brief 3 C12 for CI); (6) reformulated plan (PLAN_WM-2 says "Revised after the WM-1 audit (§7)" but §7 contains only the initial entry); (7) consolidated handback (absent). Report each place that states or implies completion that the repository does not show.

**C3. Plan status table recount.** `PLAN_2026-10-09.md` §5 lists items P0.1-P5. Count the item rows and their statuses yourself (done / changed / partial / deferred / not done). The report §1 says 25 items: 18 done, 2 changed, 3 partial, 1 deferred, 1 not done, and lists ids in the "done" cell. Compare the list of ids with the table (the report's "done" list has 19 ids as written, the plan has more than 25 rows if P4.1 and P4.2 are separate rows). Report every miscount, every item in two cells, every item missing. Then test the status words against the plan's own gates: for each "done" item whose gate text differs from what was done (examples: P3.1 gate says TC identifiers go in test titles and pytest markers while the status says ids are "derived from records, not written into test titles"; P1.2 names `check_dashboard_numbers.py`; P4.2 "map the five thrusts and H1-H5 to the cruxes" while `cruxes.yaml` C3 has `hypotheses: []`; P1.3 panels (a)-(i): open `dashboard_template.html` and confirm all nine; P0.4 "no row describing code left unstamped after the merge": count register rows that describe code and carry no commit), decide whether "done" should read "changed" or "partial".

**C4. Cross-references between plans.** Build a table of every item id that appears in more than one document and compare the descriptions: report §12 (A1-A6, B1-B3, C1-C3, D1-D2, E1-E2, F1-F2, G) vs `PLAN_WM-2.md` §3; the plan §5 "B4" vs WM-2 "A5"; MILESTONE_NEXT's N-ids vs report §12 ("author decisions" N-1, N-4, N-5...N-12, N-17; "executable" N-2, N-3, N-15, N-16, N-18...N-22) vs WM-2 §1; Q1-Q8 vs report §7; the decision ids (I-a...I-d, S-a...S-c, F-A...F-D, G-A...G-E, O-A...O-D, E-A...E-E) in the report §7 vs the after-action reports (do all exist; is each attributed to the right pass and to the right decider; "author (defaults)" means the author said "go with defaults" - did the author ever see or approve the specific decision, and does the report distinguish an author decision from a default the orchestrator applied?). Report mismatched ids and decisions credited to the author that appear in no report as put to the author.

**C5. Timeline table (report §2).** For each of the 27 commits: confirm the hash, the committer time in UTC (`git log --format='%h %cI %aI %s'`), the pass, and that the "What" cell matches the commit message and the files changed (`git show --stat`). Check the order and that the table has all 27 (it lists some two-hash rows). Check statements attached to rows: `d0cc19c, d54178e` ("run stamp scoped to producing code (inert, found later: D33); four JS producers re-run"), `f976e57` ("metrics-harness run of record on a clean tree") whose run directory is `2026-10-09T02-09-36Z_7a9a996`: the run id names HEAD `7a9a996` and a time of 02:09, but later commits (`ca3a44d`, `3a2a806`, `aef16af`, `230ac1a`) landed between it and `f976e57` at 02:22. Determine whether any harness / contracts / adapter / config code changed between `7a9a996` and `f976e57` (`git diff 7a9a996 f976e57 -- 1_blockchain-identity`), and whether the run was made in a separate worktree (decision E-A) as the report implies; report a mismatch between "run of record at a commit" and what the commit contained. Also check "commit times show when work was committed" for implausible simultaneity (several commits within a minute: were they one batch committed afterwards?), and the claim "27 commits, all authored by the author, no assistant trailer" (`git log --format='%an <%ae>%n%b' db6c381..d61a284 | grep -i -E 'co-authored|claude|assistant'`).

**C6. Findings register of the pass-11 review.** Open `AFTER_ACTION_REPORT_11.md` §4. Recompute: 33 findings; A 11 (0 H / 7 M / 4 L), B 11 (2/3/6), C 11 (5/5/1); totals 7 / 15 / 11; "32 confirmed, 1 accepted as a judgement, none rejected"; "findings with a written disposition 33 of 33". For every high finding (7) and at least ten others, follow the disposition to its commit and to the code/document change (use `git show <commit> -- <file>`): is it really fixed, deferred with an owner, or only "recorded"? Check whether any finding's severity was lowered between the reviewer's wording and the register, whether a "confirmed" finding is only reworded, and whether any "deferred" finding lacks an owner (closing condition 4). Which finding ids does the report's §5.2 table of defects (D28-D36) map to, and does the mapping hold (B-F1 -> D28, ...)?

**C7. Defect log.** `git diff db6c381 d61a284 -- docs/DEFECT_LOG.md`. (a) D28-D36 entries: severity letters vs report §5.2 (D28 H, D29 H, D30 M, D31/D32 L, D33 M, D34 L, D35/D36 M); the log's own severity definition (H = affects a thesis claim or a security property; M = wrong behaviour, bounded; L = cosmetic) applied to each: D29 "replay inside the window accepted ... residual relay limit stated" is H and fixed; is D33 (inert guards that certified results for two passes) "M" or does it affect thesis claims (H)? (b) For D31 and D32 reproduce the "fixed" status with a 5-line PoC on `d61a284` code (`--refresh-k 0` rejected; malformed sender returns a rejection, no exception). (c) Look for defects found in WM-1 that are NOT in the log: scan AAR 08-12, the plan §5 and the report §5.1/5.3 for failures (register rows inconsistent with themselves, nine demos broken by the merge, the 82 stale figures, the stale-figure checker hole, the inventory polarity D34, the "arrow rule" hole that hid a superseded figure in pass 12, the I4 expectation failure, the cut-off agent) and say which are logged. (d) Did any earlier entry (D1-D27) change status in WM-1 without a commit reference?

**C8. Report §9 "What went wrong, plainly" - complete?** The report lists seven items. Search AAR 09-12, the style guide's "amendments", TEAM_STRUCTURE §4b, the META_COMMENTARY and the commit messages for failures that are missing: e.g. the first fix of warm expiry that was inert; the registered attack list shrinking silently between design and pre-registration; F-C accepting a run whose whole-tree flag was false; 4 of 17 mutants surviving; the pass-9 numbers presented as clean; CI failures in between (see Brief 3 C12); documents corrected after being cited as evidence; any rule broken (for example "pre-registration locked before any code" while the design note was committed earlier; amendments A1-A3 written AFTER the first results). List the omitted ones with references.

**C9. Process metrics (report §8).** Verify each: passes/reports; commits 27; "delegated agents": pass 8 none, pass 9: 4, pass 10: none, pass 11: 3 reviewers; "delegated results accepted without the orchestrator re-running the gate: 0" (find, for each of the 4 pass-9 agent tasks and 3 reviewers, the logged gate re-run in AAR 09/11; "0" is a claim of absence: look for any accepted delegated result without a logged re-run); "1 pre-registration / 4 amendments (3 post hoc, 1 before the re-run)"; "dashboard versions published 3 (v3, v4, v5)" (what happened to v1, v2 - the earlier artifact was published on 2026-09-24; is "v3" the third version overall?); "findings with written disposition 33 of 33".

**C10. Reasons the numbers moved (report §4.1).** "That is the bias amendment A4 predicted": read amendment A4 in `INFRASTRUCTURE_PREREG.md` (commit `98e64e4`, before the re-run). Does it predict the direction and size of the I1 shift, or only that the SPaT path now does more? Quote. "I3's counts did not move: the re-check cadence was not changed": check against the `f1f9e37` diff. "I4 varies by +-12 gas ... consistent with one calldata byte being zero or not": the report says the TSR plan had already recorded input-dependent gas in 14 harness cells; find that record (`docs/planning/TESTING_SUITE_RESULTS_PLAN.md`) and check the number. "A4's expectation of identical runs failed and is reported as failed" - verify that the register, chapter 5 and the dashboard all carry that statement.

**C11. Independence and attribution.** The report §11 and TEAM_STRUCTURE §4a state that reviewers ran "on a different model" with fresh context, read-only, on a frozen checkout. What evidence (transcripts, hashes of the frozen commit, reviewer outputs committed under `docs/`) is in the repository? Compare with the claim in `docs/PLAN_2026-10-09.md` Q7 and AAR 10 line ~123 ("the structure's independence remains procedural: the same assistant configuration ..."). Separately: the author line of every document is "Nikhil Prakash"; commits carry no assistant trailer (decision O-C "attribution", commit `577a5ab` "tool-attribution line removed", `36e0309` "model name removed from PROJECT_SUMMARY"). Establish from `git show 577a5ab` and `git show 36e0309` exactly what text was removed. Then check whether the repository or the thesis anywhere discloses that an AI assistant did the engineering, wrote the after-action reports, ran or drafted the analyses and review (look in `README.md`, `PROVENANCE.md`, `CHANGELOG.md`, `docs/thesis/README.md`, `docs/ORIGINAL_PROMPT_AND_DIRECTION.md`, `docs/META_COMMENTARY_*.md`, `docs/TEAM_STRUCTURE.md`, thesis front matter/appendices). For a master's thesis whose institution requires disclosure of AI use, report: (1) what is disclosed and where, (2) whether any removed text was a disclosure, (3) any document that attributes to "the author" decisions, reviews or measurements that the records show were done by the assistant ("author (defaults)" for decisions in report §7 where the author only said "go with defaults"). State facts and quote; do not opine on policy.

**C12. Scope log and numbering.** `docs/SCOPE_CHANGES.md`: SC-21 and SC-22 content vs the actual scope change (the infrastructure scope is added to a thesis titled for connected vehicles; chapter titles and thrusts?); check SC numbering continuity and the note correcting SC-15...SC-20 (written 2026-10-09 "corrects the 2026-10-06 note"), uniqueness of ids, and that every scope change visible in WM-1 (RSU/infra messaging, SUMO deferral, TSR "tag, do not relocate" instead of ids in titles, the checker scope, registering new row categories) has an entry. Check "Decision pending" items that the report treats as settled.

**C13. Style-guide compliance of the report itself.** Read `STYLE_AND_RIGOUR_GUIDE.md` (rules, the "amendments" and the pass-close checklist §3). Apply its rules to `WM-1_REPORT.md` and AAR 12: every number with a source (many report numbers cite "grand report", "register", "report 11"); counts vs times; ranges for non-deterministic gas; forbidden or restricted verbs; mutation-testing statements; "shown to fail" statements. List each rule the report breaks and each number in the report with no traceable source (for example "28 and 29 min", "175 files", "66 files and +-22,150 lines", "87 documents", "20 of 29", "305 TC", "T 51, T* 40, N 78, G 13": recompute the last one from `docs/testing/coverage_matrix.md`).

**C14. Open-item bookkeeping.** For each N-id in `MILESTONE_NEXT.md` (N-1 ... N-22): is it consistently open/closed across MILESTONE_NEXT, the report §12, WM-2 §1, the handback and the defect log (N-13, N-14 closed; N-14 "closed in pass 11 but still listed open" was fixed in pass 12: confirm no other document still lists it open)? Are items that the report treats as "carried" actually in WM-2's steps (N-2, N-3 -> G; N-15 -> ?, N-16 -> D2, N-17 -> ?, N-18 -> B1, N-19 -> A6, N-20 -> A3, N-21 -> A1, N-22 -> E1)? Report N-ids with no home in WM-2 and WM-2 steps with no N-id/source.

**C15. WM-2 plan realism and scope creep.** `PLAN_WM-2.md` says "No new experiment is started in WM-2 except re-runs forced by these fixes" yet A3 re-runs five producers, C1/C2 change behaviour the thesis measures (resolver reads the chain; `attestEvent` restriction = a contract change, while §6 says "no change to the nine-standard contract set beyond C2"), and A6 re-runs the harness. Does the ordering in §4 contradict the dependencies (e.g. A4 beside A3; A5 before B1; A6 after C2)? Is anything the audit of WM-1 will likely find (stale-claim classes) already planned? Report only concrete inconsistencies or contradictions.

**C16. Changelog, version and index.** `CHANGELOG.md` "Unreleased": each bullet true against the diff; `VERSION` and the changelog's last release; `docs/INDEX.md`: every row's path exists and its one-line description matches the file (sample all rows touched in pass 12 and all rows for AAR 08-12); the resume pointer; register range "#1-#48".

**C17. Documents that contradict each other about the same fact.** Choose twenty facts that appear in at least three documents (examples: number of standards; number of tests per layer; the I1 ratio; the number of attacks (7 vs 13 vs 10); "k" values; what C3 and C4 claim; the date of the pre-registration lock; the number of agents; number of cruxes; where the Infura credential sits; who closes a milestone; the default branch name; the dashboard link version) and compare them across README.md, INVENTORY.md, CAPABILITIES.md, QUICKSTART.md, COMPOSITION.md, PROJECT_SUMMARY.md, the thesis README, chapter 5, the dashboard snapshot and the report. Report each disagreement (different numbers or different statements about status).

**C18. Retroactive wording.** The report is said to be written before the audit; but it contains statements about the audit ("pass 12's audit narrows that with a brief-writer agent (§14)", "audited ... ") and about outcomes of pass 12 (checks "in pass 12"). Check that each "checked in pass 12" claim (figures byte-identical; V2 gate; N-14 closed; stale lines fixed) has a recorded command and output somewhere in the repository (AAR 12 execution log is almost empty: `AFTER_ACTION_REPORT_12.md` §3 has a single line). Claims of checks without a record are findings (a false or unverifiable statement about verification).

**C19. Presentation and next-iteration documents.** AAR 12 plan step W5 promises `docs/presentation/` and `EXPANSION_PLAN_DRAFT2.md`; neither exists at `d61a284`. Is anything in the repository (INDEX, WM-2 plan F1, the report) written as if they exist? Report.


## 3. Commands you may run

### Commands you may use (read-only on the frozen checkout; writes only under `$SCRATCH/audit_scratch/brief-4/`)
```
FC=$SCRATCH/audit_d61a284
S=$SCRATCH/audit_scratch/brief-4
mkdir -p $S
cd $FC && git log --oneline db6c381..d61a284          # the commit range
git -C $FC show <rev>:<path>                            # old versions
git -C $FC diff db6c381 291bbca -- <path>               # WM-1 diff; also 291bbca..d61a284 for pass 12
git -C $FC grep -n "<pattern>" -- <paths>               # search tracked files (does not write)
python3 -I -c '...'                                     # recompute from committed JSON
```

### Brief-specific commands
```
git -C $FC log --format='%h %cI %aI %an %s' db6c381..d61a284
git -C $FC show --stat <commit>
git -C $FC grep -n -E "HANDBACK_2026-10-10|docs/presentation|EXPANSION_PLAN|plan item B4" -- .
git -C $FC grep -n -i -E "co-authored|generated with|claude|assistant|language model|AI[- ]assist" -- README.md PROVENANCE.md CHANGELOG.md docs/thesis docs/PROJECT_SUMMARY.md docs/TEAM_STRUCTURE.md
python3 -I - <<'PY'   # extract backticked paths from a document and test existence at d61a284
import re, subprocess, sys
doc = open("$SCRATCH/audit_d61a284/docs/milestones/WM-1_REPORT.md").read()
PY
```

## Output format (mandatory)

Write your report to `$SCRATCH/audit_scratch/brief-4/REPORT_brief_4.md` and also return it as your final message. Report ONLY what is
wrong, with evidence. No praise, no style or taste preferences, no restating what the repository says.

Severity:
- **high**: a wrong number, verdict or security property in the register, thesis, dashboard or milestone report;
  a check or test that can pass while the thing it certifies is wrong; a false statement about what was verified.
- **medium**: an overclaim, misleading wording, irreproducibility (cannot be regenerated or re-derived from the
  repository), a documented-as-complete item that is incomplete, an inconsistency between two documents.
- **low**: cosmetic or trivially fixable with no effect on a claim.

Sections, in this order:

### Findings
One item per finding, exactly in this shape:

`F<n> | <high|medium|low> | <file>:<line> | <claim in the repo, quoted or tightly paraphrased> | <what is actually true, with evidence: the command you ran and its output, or a quoted line> | <suggested fix>`

Number findings F1, F2, ... in the order you want them read (high first). Give a file:line for every finding
(use the frozen checkout's line numbers; for a document claim give the line of the claim). If a finding
spans several places, list the primary one and name the others in the evidence column.

### Checked and found sound
One line per numbered check of this brief (use the brief's own numbering, e.g. "C7: sound, because ...") that you
executed and that did not produce a finding, with the one-line evidence (the value you recomputed and the value
in the repository). Checks that produced findings are not repeated here.

### Not checked (and why)
Every numbered check you did not complete or could only partly complete, and why (tool missing, would require
a long run, ambiguity, out of time). Also list anything you noticed outside this brief's scope that you did not
pursue; the coordinator will route it.

Do not pad. A short report with five well-evidenced findings is better than a long one with speculation. Mark
anything you could not confirm as "unconfirmed" and say what would confirm it.
