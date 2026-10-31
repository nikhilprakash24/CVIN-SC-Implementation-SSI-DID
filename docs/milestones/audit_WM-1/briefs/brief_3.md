# Brief 3 - Tooling, CI and reproducibility from a clean checkout

## 1. Scope

**Question this brief answers:** can what WM-1 calls "generated", "CI-checked", "byte-identical", "stamped" and
"ALL OK" be reproduced by someone with only the repository; and can each guard actually fail?

**Tooling and files**
- CI: `.github/workflows/test-contracts.yml`, `w3c-compliance.yml`, `benchmark.yml` (8 jobs in total).
- Generators and checkers: `docs/figures/make_dashboard_data.py`, `make_dashboard_page.py`, `dashboard_template.html`; `docs/testing/build_register.py`, `check_docs_numbers.py`, `stale_numbers.yaml`, `check_stamps.py`, `probe_run_identity.sh`, `STAMP_INVENTORY.md`, `test_register.yaml`, `coverage_matrix.md`; `docs/thesis/cruxes.yaml` -> `CRUX_REGISTER.md`; `4_comparison-framework/feature-matrix/make_feature_matrix.py`; `sandbox/grand/run.py`, `make_manifests.py`, `manifest.yaml`, `report/`.
- Run identity: `1_blockchain-identity/scripts/lib/run_stamp.js`, `cv2x-testbed/sumo/run_v2v_stats.py` header, `1_blockchain-identity/benchmarks/run.js` (`dirtyMeasured`, open item N-19).
- Reproduction entry points and install instructions: `QUICKSTART.md`, `README.md`, `1_blockchain-identity/README.md`, `cv2x-testbed/QUICKSTART.md`, `2_w3c-ssi-layer/requirements.txt`, `cv2x-testbed/requirements.txt`, `package.json` / `package-lock.json` (both Node projects), `.gitignore`.
- Renderer determinism: `cv2x-testbed/sumo/render_trace.py` and the committed figures / GIF in `cv2x-testbed/sumo/results/figures/`.
- Commits `ca3a44d`, `230ac1a`, `d0cc19c`, `d54178e`, `b1d3f72`, `36e0309`, `601e1de`, `291bbca`, and the pass-12 commits.

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
clone locally into your scratch directory: `git clone -q $SCRATCH/audit_d61a284 $SCRATCH/audit_scratch/brief-3/clone && ln -s $SCRATCH/audit_d61a284/1_blockchain-identity/node_modules $SCRATCH/audit_scratch/brief-3/clone/1_blockchain-identity/node_modules`
(the clone is yours to modify; old commits are reachable in it with `git -C $SCRATCH/audit_scratch/brief-3/clone show <rev>:<path>` or `git archive`).

**Hard rules for commands.**
- Write only to your scratch directory `$SCRATCH/audit_scratch/brief-3/` (create it).
- Long experiments (the 30-run sweeps of ~7-30 min: `run_infra_stats.py`, `run_v2v_stats.py`, `run_verify_scaling.py`, `npm run metrics`, `benchmark_scaling.js`, the I3 revocation sweep) must NOT be re-run. Recompute from the committed JSON instead.
- Allowed short runs: a single seed of the harness (seconds), the pytest suites, `npx hardhat test` (about 25-60 s) and single Hardhat scripts, the document generators in `--check` mode, `git`, `grep`, `python3 -I`, `node`. A Hardhat node, if you need one, must use a non-default port (for example 18548) and you must kill it by recorded pid.
- When running `cv2x-testbed/sumo/sumo_identity_integration.py` ALWAYS pass `--results $SCRATCH/audit_scratch/brief-3/<name>.json` (its default overwrites a committed file). Run it from a clone, not from `$SCRATCH/audit_d61a284`.
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

Use a fresh local clone per scenario so earlier checks do not contaminate later ones, e.g.
`git clone -q $FC $S/clean1 && ln -s $FC/1_blockchain-identity/node_modules $S/clean1/1_blockchain-identity/node_modules`.
Record exit codes (`echo $?`).

**C1. Every CI step, locally, from a clean clone.** For each step of the three workflows that can be run offline in under ~2 minutes, run the same command in a fresh clone and record exit code and key output: MOBI copies `cmp`; feature-matrix generator + `git diff --exit-code`; `make_dashboard_data.py --check`; `build_register.py --check`; `check_docs_numbers.py`; `probe_run_identity.sh`; `npx hardhat compile`; `npx hardhat test` (record passing / pending / failing); `python -m pytest 2_w3c-ssi-layer cv2x-testbed/tests -q -rs` (these need a Hardhat node on a port you choose; set `CV2X_TEST_RPC_URL` / `CV2X_TEST_ARTIFACTS_DIR` as the workflow does; list every skip); `sandbox/py-suites/run.sh`; the W3C compliance checker and its floor gate (read the gate script in the workflow and run its logic). Report any step that fails or behaves differently from the workflow's expectation.

**C2. Do the generated-document guards fail?** The report (§6) says only the page check, the stale-figure check and the probe were "shown to fail on a mutated input" and the others "not mutation-tested". In a clone, mutate one input at a time and run the corresponding check; each must exit non-zero: (a) change a V to E in one register row; (b) change one number in `dashboard_snapshot.json`; (c) change one number in `results_dashboard.html` and, separately, in `dashboard_template.html`; (d) delete an `evidence_rows` entry in `cruxes.yaml`; (e) edit `CRUX_REGISTER.md` by hand; (f) change a cell of `coverage_matrix.md` and one entry of `test_register.yaml`; (g) rename an L1 test title that a TC id derives from; (h) change a JSON result value that feeds the snapshot; (i) make a register row's status cell unparsable (`V?`, `v`, `**V**` with trailing text); (j) add a stale figure to a tracked `.md`, `.html`, `.json`, `.yaml` and a docs sub-directory file. List every mutation the CI check does not catch. A guard that passes on a mutated input is a high-severity finding (a check that can pass while wrong).

**C3. Is a CI "check" a real comparison?** For each `--check` mode, read the code path: does it regenerate to memory/temp and compare byte-for-byte against the committed file, or regenerate in place and compare to itself, or compare only a subset of fields (e.g. counts but not text)? Is the comparison against the committed file or against the working tree (which CI always has equal)? Do any of them tolerate whitespace/ordering/timestamps? Do the generated files contain timestamps (run each generator twice in a clone, `diff` the results)?

**C4. Stale-figure checker scope and masking.** Read `check_docs_numbers.py` and `stale_numbers.yaml`. Confirm the claim "scans every tracked Markdown file except named history files" (87 files) by listing the scanned set and the excluded set. Test the masking rules with synthetic lines: a stale figure after an arrow (range arrow, ASCII `->` and Unicode), inside a table cell, in a code fence, in a link text, in parentheses with "was", with different number formatting (`52 170`, `52170`, `52.170`, `52,170 gas`), in plural/unit variants, split across lines. Report constructions that hide a superseded figure although the file is a scanned one. Check each entry in `stale_numbers.yaml`: is the "current value" it points to still the register's value; are there superseded figures the history shows (e.g. `git log -p` of the register for replaced values) that are missing from the list.

**C5. Stamp inventory.** Recompute "20 of 29" by reading every result file listed in `STAMP_INVENTORY.md` and counting the ones with a complete `meta`/`environment` block (commit, dirty/`tree_clean`, `code_clean`, toolchain). Run `docs/testing/check_stamps.py` in a clone and diff its output against the committed `STAMP_INVENTORY.md` (is the inventory regenerated and checked in CI? the report says "report only"). Then list result files under `results/` directories (all of `git ls-files | grep -i result`) that the inventory does not list (the report's own open item N-21 says the globs are narrow: `metrics-rpc`, `scaling_verify_repeats`, `docs/conformance`, grand-report JSON) and say how many register V rows depend on them. Check the "class" assigned to the nine not-stamped files (history / stamp producer / single run) is consistent with what the files are.

**C6. Do the stamps mean what the register says?** For each stamped result file backing a V row: (1) is the stamped `commit` an ancestor of HEAD (`git merge-base --is-ancestor`); (2) does `git diff <commit> HEAD -- <the producer's own code and its imports>` show changes since (then the stamp is stale); (3) is `dirty` computed on a path set that includes everything the producer imports? In particular inspect `d0cc19c`'s "scoped to producing code (contracts, scripts, configuration, lockfile)" rule: is `4_comparison-framework/` (post-processing, `generate_tables.py`), `1_blockchain-identity/benchmarks/`, `sandbox/lib` or the Python `identity/` package inside or outside the scoped paths for the producers that use them? Report each stamped number whose producing code is partly outside the stamped scope.

**C7. Clean-checkout Node install.** `npm ci` needs network and possibly `git+ssh://` dependencies (open item N-2: `ethereumjs-abi` via `git+ssh`). Without running a full install in the frozen checkout: `grep -n "git+ssh\|git+https\|github:" 1_blockchain-identity/package-lock.json cv2x-testbed/package-lock.json`; try `npm ci --dry-run --ignore-scripts` in a clone WITHOUT the node_modules symlink (if the network is unavailable say so under Not checked). Check that `package.json` and `package-lock.json` agree (`npm ls` / `npm ci --dry-run` errors), and that `cv2x-testbed` has its own lockfile consistent with CI's "ln -sfn ../1_blockchain-identity/node_modules" workaround (the CI job links the other project's node_modules into the testbed: does the testbed's own `package.json` resolve differently, e.g. a different OpenZeppelin version? The team notes OZ 5.4.0 vs 5.0.2 once changed an artifact).

**C8. Clean-checkout Python install.** `2_w3c-ssi-layer/requirements.txt` pins `did-jwt==0.1.0`, which the workflow header says does not exist on PyPI. Check what `QUICKSTART.md` and READMEs tell a newcomer to run, then try each documented install and run command that works offline or from the sandbox's pip cache in a fresh venv under `$S` (`python3 -m venv $S/venv`; if `pip install` has no network, say so and instead verify by reading which imports each suite needs and whether `requirements.txt` lists them: `numpy`, `pyyaml`, `matplotlib`, `web3`, `eth-account`, `coincurve`, `cryptography`, `pytest`, `pillow`). Report documented commands that fail on a clean machine and dependencies missing from every requirements file.

**C9. Byte-identical figure regeneration.** The report claims 5 of 5 outputs regenerate byte-identically from the committed traces (checked "in pass 12"). Recompute: for the two traces of record, run `render_trace.py` with the documented arguments (read `docs/PLAN_SUMO_VISUALISATION.md` §7 and `cv2x-testbed/sumo/README.md`) into `$S/figs/` and compare `sha256sum` with the committed files. Repeat with `PYTHONHASHSEED=1` and `PYTHONHASHSEED=2`, and with `MPLBACKEND=Agg` vs unset. Identify the five outputs the report means, say if any other generated image (`docs/figures/*.png|svg|gif`) is not covered. The renderer depends on matplotlib and Pillow versions: are they pinned anywhere? If outputs differ in this environment, report the first differing bytes' cause and that the claim is environment-dependent.

**C10. Grand runner.** In a clone run `python3 sandbox/grand/run.py check`, `matrix`, and then `python3 sandbox/grand/run.py all` (about 1 minute; it regenerates reports inside the clone). Compare its counts with `sandbox/grand/report/GRAND_REPORT.md` (smoke 11/11? L1 99, Hardhat 536 and pending, Python layers 291, demos 92 / steps 1,752 / flagged 62) and diff the regenerated reports against the committed ones (timestamps aside). Does the runner exit non-zero when a stage fails? Verify by breaking one test and one demo assertion in the clone and re-running the relevant sub-command. What does "flagged: 62" (demos) mean for "ALL OK" - are 62 of 92 demos carrying observations/warnings yet the verdict is OK? Does a demo step count if it only logs and asserts nothing?

**C11. The commit the numbers belong to.** `GRAND_REPORT.md` says it was generated at commit `601e1de`; the milestone report and several documents cite it as `291bbca`'s result. `git log --format='%h %cI %s' -- sandbox/grand/report/GRAND_REPORT.md` and `git diff 601e1de 291bbca --stat -- sandbox 1_blockchain-identity/test 1_blockchain-identity/contracts cv2x-testbed 2_w3c-ssi-layer`: did anything that the grand run exercises change after `601e1de`? Same question for the README "current counts" and for the generated `test_register.yaml` / `coverage_matrix.md` / dashboard snapshot (generated from which commit). And for pass-12 documents: is any generated artefact now stale relative to `d61a284` (run every `--check` at `d61a284`, done in C1; also run `check_docs_numbers.py` after the pass-12 doc edits).

**C12. CI history, not just the closing commit.** With `gh api repos/nikhilprakash24/CVIN-SC-Implementation-SSI-DID/commits/<sha>/check-runs` (read-only) fetch the check runs for every commit in `db6c381..d61a284` (or at least the six the report names and `d61a284`, `44dc926`, `3e19e72`, and all commits that touched `.github/`, generators or tests). Tabulate job name, conclusion, started/completed, and whether any is `skipped`/`neutral`/`cancelled`/`failure`. Check "8 of 8 green on every closing commit": which jobs exist (7? 8?), whether intermediate commits were red, whether a job name was renamed/removed so that "8" is not comparable, and the status of the three pass-12 commits (the milestone closing condition 5 needs CI green on the closing commit). Look at logs of one run of the `python-full-suite` job for the skip count line and at the `metrics-harness` job for what it asserts. If `gh` returns 403 or no data, state so.

**C13. What CI does not guard, versus what documents say is guarded.** `git grep -n -i -E "CI[- ]checked|checked in CI|CI fails|fails the build|in CI\b|guard" -- '*.md'` over WM-1 documents (report, AAR 09-12, style guide, testing README, thesis README, handback). For each claimed guard, find the workflow step. Known candidates to test: the figure regeneration gate; the stamp inventory; the grand report freshness; `check_docs_numbers.py` covering the thesis; the infrastructure result JSONs vs the register (is there any step that recomputes #44-#48 from JSON?); the `metrics-harness` job (does it compare its output to the committed run of record, or only upload?); the `nine-standard-gas` job compares only `gas_benchmark.json` (not `infrastructure_gas*.json`, `mobi_vid_backends.json`, scaling); the workflows trigger on `push` to `main`/`claude/**` and PRs into `main` only: does a push to any other branch name, or a PR into the actual default branch, run them (N-12 says the default branch is the review-2 branch, not main)? Report each claimed-but-absent guard.

**C14. Determinism claims.** Find every statement that something "reproduces", "is deterministic", "byte-identical", "exact" or "identical" in WM-1 documents and results. For gas: run `npx hardhat run scripts/benchmark_gas.js` in a clone (short) and compare every cell with `4_comparison-framework/results/gas_benchmark.json`; run `npx hardhat test` twice in a clone and diff the L1 gas table outputs (open item N-18: 3 of 99 cells moved < 30 gas); run `infrastructure_gas.js` twice. Report any claim of exactness/determinism that fails (the register rule says gas "needs no confidence intervals"; non-deterministic cells contradict it).

**C15. Run-identity flags: what the probe proves.** Read `probe_run_identity.sh`. It proves that a flag flips when an untracked file is added in two places. Test what it does not: a modified tracked file; a file in a subdirectory not covered; a clone where the repository is a git worktree or has a `.git` file; a shallow clone (`git clone --depth 1 file://$FC`) as GitHub Actions makes; running the producers from a different working directory (the original fault was relative pathspecs). Also read `1_blockchain-identity/benchmarks/run.js` `dirtyMeasured`: confirm by experiment (untracked file in `contracts/`, then run only the stamp part if possible, otherwise by reading the code) that the metrics-harness flag is still inert, and list which register rows (#34-#36) and which dashboard/chapter statements rely on it ("whole-tree `dirty` false (the valid flag; D33)").

**C16. Gitignored or untracked inputs.** After running the tests/generators in a clone, `git status --ignored --short` and `git ls-files --others`: does any committed result or test depend on a file that is ignored (compiled artifacts, `deployments/`, `cache/`, `.env`, `gas-report.txt`, `results/runs/`)? Does `cv2x-testbed/artifacts` (tracked ABI/bytecode) match a fresh compile (`cd cv2x-testbed && node scripts/check_artifacts_fresh.js`, needs the node_modules link)? Does a missing Hardhat node make suites skip (CI counts skips as failures; local `run.sh` may not: run `sandbox/py-suites/run.sh -rs` without a node and report the number of skips hidden behind a green result)?

**C17. Timeline plausibility of the runs of record.** The report says the longest steps were the two I3 sweeps (28 and 29 min of wall clock) and the two I1 runs (6 and 7 min), one of each per run of record. Compare the `wall_clock_s` and `date_utc` fields in `infrastructure_stats.json` / `infrastructure_revocation.json` with the commit times (`git log --format='%h %cI %s' db6c381..d61a284`): the re-run of record is said to be at code commit `f1f9e37` (05:30 UTC) and committed at `601e1de` (06:11 UTC); the data files claim `tree_clean` true at that commit. Can I1 (about 7 min) plus I3 (about 29 min) plus I4 and the figure/trace regeneration fit in that window, were they run in parallel (which would invalidate the "run alone on the host" statement of #44, because latency is host-load dependent), and does the stamp's commit/clean flag refer to the start or the end of the run? Report contradictions between the statement "run alone on the host" and the timestamps.

**C18. Dashboard page offline and robustness.** Open `docs/figures/results_dashboard.html` as text: external URLs (CDN scripts without version pin or integrity hash, web fonts), inline JS that fails when the snapshot is missing, any `eval`/`innerHTML` of data, accessibility (phone width, no horizontal scroll at 360 px if you can render it; otherwise by CSS inspection). Is the page identical to what `make_dashboard_page.py` produces (`--check`) and does it embed the snapshot (so it works as a standalone artifact)?

**C19. Handback commands.** The handback (`docs/HANDBACK_2026-10-09.md`, "resume commands") and `docs/INDEX.md` give commands to resume/reproduce. Run every command in them that is short; report those that fail, reference a missing file (the milestone report refers to a "consolidated handback" that this checkout does not contain), or print numbers different from the document.

**C20. Seeds and randomness in generated results.** In `infrastructure_stats.json` the per-run `seed` list and in `sumo_identity_integration.py` the use of `random`, `numpy.random`, `Account.create()` (OS entropy, unseeded). Which quantities in the registered results depend on unseeded randomness (key bytes, signature lengths, credential ids/timestamps)? Run seed 7 twice and compare all counts and non-timing fields: report non-reproducible fields and whether any register claim of "seeded / reproducible" covers them.


## 3. Commands you may run

### Commands you may use (read-only on the frozen checkout; writes only under `$SCRATCH/audit_scratch/brief-3/`)
```
FC=$SCRATCH/audit_d61a284
S=$SCRATCH/audit_scratch/brief-3
mkdir -p $S
cd $FC && git log --oneline db6c381..d61a284          # the commit range
git -C $FC show <rev>:<path>                            # old versions
git -C $FC diff db6c381 291bbca -- <path>               # WM-1 diff; also 291bbca..d61a284 for pass 12
git -C $FC grep -n "<pattern>" -- <paths>               # search tracked files (does not write)
python3 -I -c '...'                                     # recompute from committed JSON
```

### Brief-specific commands
```
git clone -q $FC $S/clean1 && ln -s $FC/1_blockchain-identity/node_modules $S/clean1/1_blockchain-identity/node_modules
git clone -q --depth 1 file://$FC $S/shallow
cd $S/clean1 && bash docs/testing/probe_run_identity.sh; echo $?
cd $S/clean1 && python3 docs/figures/make_dashboard_data.py --check; python3 docs/testing/build_register.py --check; python3 docs/testing/check_docs_numbers.py
cd $S/clean1 && python3 docs/testing/check_stamps.py            # then: git diff --stat   (inventory drift)
cd $S/clean1 && python3 sandbox/grand/run.py all                # ~1 min; writes only inside the clone
gh api repos/nikhilprakash24/CVIN-SC-Implementation-SSI-DID/commits/<sha>/check-runs --jq '.check_runs[] | [.name,.conclusion,.started_at,.completed_at] | @tsv'
sha256sum $FC/cv2x-testbed/sumo/results/figures/*
```

## Output format (mandatory)

Write your report to `$SCRATCH/audit_scratch/brief-3/REPORT_brief_3.md` and also return it as your final message. Report ONLY what is
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
