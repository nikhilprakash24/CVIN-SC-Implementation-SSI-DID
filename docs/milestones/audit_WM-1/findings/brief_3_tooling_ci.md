> Verbatim final report of an independent reviewer agent (different model from the orchestrator's; fresh context; read-only on a frozen checkout). Extracted from the agent transcript by script on 2026-10-10 (after-action report 12, audit finding P-10); scratch paths normalised to `$SCRATCH`. Dispositions: after-action report 12 §4.

### Findings

F1 | high | INVENTORY.md:28 (also :53, :90, :233; QUICKSTART.md:78; README.md:53 and :93; docs/PROJECT_SUMMARY.md:39) | WM-1 report line 212 and commit 44dc926 say "8 live stale lines fixed (test counts 217/369, 52,170, ~33x)". The checker "exits clean: 0 stale figure(s), 89 files scanned". | Live, unmarked superseded Hardhat counts remain in scanned Markdown. Current value is 536 passing and 23 pending, from my `npx hardhat test` in a clean clone and from GRAND_REPORT.md. INDEX.md:21 names PROJECT_SUMMARY.md the status document. Remaining lines:
- INVENTORY.md:28 "**217 tests passing.**", :53 "217 tests total", :90 "tested (217)", :233 "100% (217 tests)".
- QUICKSTART.md:78 "the 217-test suite passes against".
- README.md:53 and :93 "369 contract tests" / "369-test Hardhat suite".
- PROJECT_SUMMARY.md:39 "219 passing / 0 failing on the merged trunk".

`check_docs_numbers.py` exits 0 on all of them, for two reasons:
- The entries at stale_numbers.yaml:106 and :112 match only `\b(217|219|369|386) passing` and `\b217 Hardhat`. So "217 tests", "217-test" and "369-test" never match.
- PROJECT_SUMMARY.md:39 is excused by the word "before" later on the same line. check_docs_numbers.py:54-55 skips the whole line when any marker occurs anywhere on it.

I found these by scanning the 89 scanned files with the normaliser and a wider pattern set. | Fix the lines. Match the count by number alone near test/Hardhat/passing. Apply markers only within a window around the figure, not to the whole line.

F2 | high | docs/testing/build_register.py:53-95 (CI step at .github/workflows/test-contracts.yml:75) | WM-1 report line 108: test register and coverage matrix are "`--check` in CI". Commit aef16af: "both CI-checked". | The check compares the YAML/MD with a regeneration from committed JSON (`L1-asymmetry.json`, `demos.json`, `attack_results.json`) and the manifests. It never reads a test source. Three mutations in a clone:
- Renamed the describe title in `01-create.test.js`.
- Deleted `sandbox/options/erc-721/demos/controller.js`.
- Deleted `05-claim.test.js` (87 lines).

`make_dashboard_data.py --check`, `build_register.py --check` and `check_docs_numbers.py` all exited 0 for each. Nothing in CI gates a test count either: `hardhat test` passes with fewer tests. So "305 TC entries" can describe tests that no longer exist. | Regenerate or verify the JSON against the real test titles and demo files in CI. Gate the Hardhat count (536) and the 92 demos.

F3 | medium | docs/MEASUREMENT_CONDITIONS.md:130 and :132 (rows #44, #46); docs/HANDBACK_2026-10-09.md:86; docs/thesis/chapter5-results/README.md:347 | HANDBACK line 86: "After any result or register change, regenerate the snapshot, the test register and the dashboard page; CI fails otherwise." | No check ties register numbers to the result JSON. I ran these mutations, and every guard exited 0:
- Row #44 `**1.096**` to `**1.196**`.
- Row #46 `0/4/24` to `9/9/99`.
- Chapter 5 `1.096` to `1.196`.

Only the first 220 characters of a claim reach the snapshot (make_dashboard_data.py:56). So row #27 `0.153 ms` to `0.253 ms` was caught, but edits to #44/#46 text were not. The JSON side is guarded: changing `I1.ratio.median` makes `--check` fail. Regenerating the dashboard then hides any mismatch with the register text. No step recomputes #44-#48 from JSON. | Add a check that each V row's quoted figures equal the value in its named result file, and run it in CI.

F4 | medium | docs/MEASUREMENT_CONDITIONS.md:256-260; 1_blockchain-identity/benchmarks/run.js:73 | The register rule says a run is the run of record if "`dirtyMeasured = false`". WM-1 report line 166 relies on whole-tree `dirty` instead. | `dirtyMeasured` is still inert (open item N-19, deferred). run.js:73 uses relative pathspecs, and `git()` at run.js:31 has no `cwd`. Experiment in a clone with an untracked `1_blockchain-identity/contracts/zz_probe.sol`:
- The exact command, run from `1_blockchain-identity`, printed `warning: could not open directory '1_blockchain-identity/1_blockchain-identity/'` and 0 bytes.
- Whole-tree `git status --porcelain` showed the file.

The register rule still names this flag as the criterion and does not say it cannot fire. `probe_run_identity.sh` covers only run_stamp.js and the two Python headers. | Root-anchor the pathspecs with `:(top)` and extend the probe, or amend :256-260 to say the flag is not valid.

F5 | medium | docs/MEASUREMENT_CONDITIONS.md:94 (row #27, V); docs/testing/STAMP_INVENTORY.md | #27 says "V, re-executed on the merged trunk 2026-10-04", producer commit `58a6513`. The inventory lists it as a complete stamp, "False (from any)". | `58a6513` (2026-10-04T09:13) is a review-2 lineage commit. The merge `bd90004` is 2026-10-06T04:25, so "merged trunk" is wrong for that commit. The measured code has changed since the stamp: `git diff --stat 58a6513 HEAD -- cv2x-testbed/sumo cv2x-testbed/identity` shows `sumo_identity_integration.py` +313, `run_v2v_stats.py` +5, `identity/mobi_vid_provider.py` +227, plus new `infrastructure_layer.py` and `render_trace.py`. The 30-run #27 numbers were not re-run; only a seed-7 count comparison was done with flags off. `check_stamps.py` has no staleness test. The same applies to freshness_k (`8216507`), lifecycle_parity (`4f09875`), pki_vs_erc1056 and scaling_verify (`d78e344`). The testbed code each used differs from HEAD by about 2,600-4,500 lines. | Record in #27 that the code differs from HEAD, or re-run. Add a "producer changed since stamp" column to `check_stamps.py`.

F6 | medium | cv2x-testbed/package-lock.json:1282-1283; .github/workflows/w3c-compliance.yml:85-87; docs/HANDBACK_2026-10-09.md Gotchas | The CI step "Testbed artifacts match a fresh compile" passes. | It passes only because CI symlinks the root `node_modules` (OpenZeppelin 5.0.2) into `cv2x-testbed`. The testbed's own lock pins OpenZeppelin 5.4.0. Experiment: in a clone, `cd cv2x-testbed && npm ci --offline` (resolved from the npm cache), then `node scripts/check_artifacts_fresh.js`. It printed `STALE ... MOBIVIDRegistryV2.json: bytecode differs ... deployedBytecode differs`, exit 1. So the per-project install yields a tracked artifact that does not reproduce. The coupling is noted only as a handback "gotcha". `npm ci --dry-run --ignore-scripts` succeeds for both projects. | Pin OpenZeppelin identically in both projects, or document in cv2x-testbed/QUICKSTART.md that artifacts are built with the root install.

F7 | medium | QUICKSTART.md:86; 2_w3c-ssi-layer/requirements.txt:13 | QUICKSTART: "pip3 install -r 2_w3c-ssi-layer/requirements.txt". | `did-jwt==0.1.0` does not exist. In a fresh venv, `pip download --no-deps did-jwt==0.1.0` gives `ERROR: No matching distribution found ... (from versions: none)`. So the primary documented install fails. The workflow header (w3c-compliance.yml:10-13) admits this; QUICKSTART does not. No requirements file lists:
- `coincurve`, which the VC layer imports.
- `pyyaml`, which every generator and checker needs.
- `pillow`, which `PillowWriter` needs at render_trace.py:225.

The pins `web3==6.11.0` and `eth-account==0.10.0` differ from the versions used for results (web3 8.0.0, eth-account 0.14.0). | Drop the pointer or fix the file. List pyyaml, coincurve, pillow, numpy and matplotlib. Pin to the stamped versions.

F8 | medium | docs/MEASUREMENT_CONDITIONS.md:130 (#44); docs/AFTER_ACTION_REPORT_11.md:50 and :89 | #44: "Run alone on the host". AAR 11: "I1 alone on the host". | The timestamps do not support this, and no run log is in the repository.
- I1 (`infrastructure_stats.json`): `date_utc` 05:30:59 plus `wall_clock_s` 422.8 ends at 05:38:02.
- I3 (`infrastructure_revocation.json`): starts at 05:38:02 and runs 1763.8 s, ending at about 06:07:26.
- I4: 06:08:42-44.
- Commit `36e0309` (05:41:49, 22 files, stale-checker work) was made in the main worktree during I3. The run itself used a separate worktree on the same 4-vCPU host.
- I1 began 19 s after `f1f9e37` (05:30:40).

Overlap with I1 cannot be shown from the repository. Overlap with I3 cannot be excluded. This is unconfirmed; the shell history or process log would settle it. | Drop "alone" or commit the run log. Record load average in the environment header.

F9 | medium | docs/testing/check_stamps.py:24-26; docs/milestones/WM-1_REPORT.md:35 | "Result files with a complete stamp: 20 of 29". | The denominator comes from the globs. `git ls-files` lists 63 result JSON files (excluding prior-survey, review02, research copies, sandbox options and docs/figures). 34 are not in the inventory:
- metrics-rpc/latest, 7 files.
- metrics/latest, 13 files.
- scaling_verify_repeats, 14 files.
- cv2x-testbed/results/archive-2026-10-03 and others, 7 files in total including the docs/conformance report JSON and the trace replay JSON, which were not itemised.

V rows #24 (conformance), #39 (metrics-rpc) and #43 cite unlisted files. N-21 (deferred) admits narrow globs, but the report states 20 of 29 without that scope. Re-running `check_stamps.py` in a clone reproduces STAMP_INVENTORY.md exactly. It is not run in CI. | Widen the globs (N-21), or state in the report that 29 is a subset.

F10 | medium | 1_blockchain-identity/scripts/lib/run_stamp.js:19-20; cv2x-testbed/sumo/sumo_identity_integration.py:469-470 | d0cc19c: dirty "is measured over the producing code paths". The four producers are stamped "False". | Producers use code outside the scoped paths. `scripts/security_scenarios.js:36` requires `test/L2-identity-system/security/attackHarness`. `cv2x-testbed/scripts/experiment_{freshness_k,lifecycle_parity}.py` and `4_comparison-framework/performance-metrics/generate_tables.py` are also outside the scoped paths. Experiments in a clone:
- Appending to `attackHarness.js` left `runStamp().dirty` false.
- Appending to `generate_tables.py` left it false.
- Appending to `cv2x-testbed/scripts/experiment_freshness_k.py` left `code_clean` True and `code_dirty` False.

A modified `cv2x-testbed/sumo/*.py` and an untracked `cv2x-testbed/contracts/zz.sol` are flagged. | Add test/attackHarness, cv2x-testbed/scripts and the 4_comparison-framework post-processing to the scope, or document the exclusion beside each stamp.

F11 | medium | .github/workflows/test-contracts.yml:10-11; w3c-compliance.yml:18-19; benchmark.yml (no `pull_request`) | WM-1 documents describe the jobs as CI-checked and say "CI fails otherwise". | The default branch is `claude/clone-cvin-id-scs-011CUyxScetMdSQFkuQUNLTt` (from the repo API). `pull_request` triggers only for PRs into `main`, and `main` does not exist as a branch. A PR into the default branch runs none of the 8 jobs. A push to `docs/root-readme`, `sandbox-onboarding` or `wo-s0/*` runs nothing. benchmark.yml has no PR trigger at all. | Add the default branch and `**` to `pull_request` and `push`.

F12 | medium | .github/workflows/benchmark.yml:244-252; w3c-compliance.yml:140-172; 4_comparison-framework/results/w3c_compliance.json | The metrics-harness job counts among the 8 green jobs. The "94.3 %" is described as CI-gated. | These jobs run but compare nothing against committed results.
- The metrics-harness job runs the conformance gate and `npm run metrics` and uploads the output. It does not compare with the committed `results/metrics/latest`. run.js exits non-zero only on an exception (run.js:129).
- The gas job compares only `gas_benchmark.json`; I reproduced 55 of 55 cells locally. `infrastructure_gas*.json`, `mobi_vid_backends.json`, `scaling_*.json` and `onchain_security.json` have no CI recomputation.
- `check_stamps.py` and grand-report freshness are in no workflow.
- The W3C gate parses the freshly generated, gitignored `w3c_compliance_report.json`. The committed `4_comparison-framework/results/w3c_compliance.json` is a 2026-10-04 copy. Register #4 and the dashboard read it.
- Scores are equal at 94.318. Its check notes already differ from a current checker run, for example the 7.1.2 note.

| Add compare steps, or state in the report that these jobs are run-only.

F13 | medium | docs/MEASUREMENT_CONDITIONS.md:23 and :30-32 | "Gas is deterministic ... report a single exact value ... No confidence intervals." The L1 table header says "exact gasUsed". | False for several cells, and the rule was not amended.
- Two clean-clone `hardhat test` runs gave the cvin-combined claim cell as 316465 and 316451, against 316477 committed.
- 45 of 1,752 demo step gas values differed between committed `demos.json` and my `run.py all`.
- Two `infrastructure_gas.js` runs gave anchor_key 52606 and 52594; committed values are 52594 and 52606 (run1).
- Of the other cells, my two runs gave identical values (34050, 35510); the committed values were different (34038/34050 and 35486/35498).
- N-18 says "3 of 99 cells moved < 30 gas". I saw 1 of 99 per run, and the demo variation is not mentioned.
- `build_register.py` copies L1 gas into the `TC-*-G` entries as "measured".

| Amend M1. Seed the keys (N-18). Disclose the demo variation.

F14 | medium | docs/milestones/WM-1_REPORT.md:222; sandbox/grand/run.py:61-65 and :87-119; sandbox/options/*/demos/_lib.js | "grand runner ALL OK: smoke 11/11, L1 99, Hardhat 536, Python layers 291, 92 demos / 1,752 steps". | The counts reproduce in a clean clone: 99, 536, 291, 92/1752/62, "GRAND: ALL OK", about 4 minutes. Three problems:
- (a) "smoke 11/11" is not in GRAND_REPORT.md; the smoke row prints `{}`. The count exists only in console output.
- (b) "Steps" are logged JSON lines, not assertions. `offchain()` has 137 call sites and asserts nothing. `view()` has an optional check. `tx()` asserts only that the transaction mined. Of the 1,752 steps, 1,052 are transactions, 471 are views or off-chain, and 229 are asserted reverts.
- (c) "flagged 62" counts steps whose note matches DEFECT|OBSERVATION. The verdict ignores it.

The runner does fail correctly when an assertion breaks: a broken `assert.equal(v, 3n)` in an ERC-721 demo gave `"ok":false` and rc 1. The 23 pending tests are not recorded. | Report asserted versus logged steps. Write the smoke count into the report.

F15 | low | cv2x-testbed/sumo/render_trace.py:23-26; cv2x-testbed/requirements.txt:6; docs/milestones/WM-1_REPORT.md:126 and :225 | "5 of 5 byte-identical". | Reproduced: all five outputs have the same sha256 as the committed files. I tried PYTHONHASHSEED=1 with MPLBACKEND=Agg, and PYTHONHASHSEED=2, with matplotlib 3.11.2 and Pillow 12.3.0. The claim is environment-dependent and unpinned:
- The requirements say `matplotlib>=3.4.0`.
- Pillow is in no requirements file.
- No CI step regenerates the figures.
- The other images (`docs/figures/review_*.png`, `verification_dashboard.*`) have no regeneration check.

| Pin matplotlib and Pillow. Add a CI regeneration compare.

F16 | low | docs/artifacts/result-gas-benchmark.html:96-103 (also cvin-combined.html:98, erc-721.html:98, erc-725xy.html:98, erc-735.html:98, result-w3c-compliance.html:95, result-v2v-latency.html:101) | Tracked "Key numbers" pages. | They state superseded figures as current: 52,178; 1,704,992; ~33x; +46,862; 542,429; 93.2%; "3 injected attacks". The checker scans only `git ls-files '*.md'`, so .html, .json, .csv, .tex and .yaml are never scanned. A scan of non-.md tracked files finds these pages plus `sensitivity.csv/json/tex` and make_review_figures.py:72,76. These are July provenance dossiers but carry no history marker. | Mark them as dated snapshots, or extend the scan.

F17 | low | docs/testing/check_docs_numbers.py:33, :45-47; docs/testing/stale_numbers.yaml | The report says the checker "normalises number formatting". | I tested constructions by replicating the checker's per-line loop on synthetic lines. These produced no hit:
- Formats: `52.170`, `93,2 %`, `93.2 percent`, `0.165 milliseconds`, `0.40 ms`.
- Variants: `33×` without a tilde, `~33x` with ASCII x, `32.2x`, `336 / 441`, `1.704.992`.
- Odd splits: `1,705 k gas`, a figure split across two lines.
- Any line that also holds "was", "before" or "old", for example "It was measured as 52,170 gas".

Caught: plain, space-grouped, `52170`, table cell, backticks, link text, reversed arrow, range arrow, `336/441`, `0.165ms`. Superseded values with no entry: I1 `0.996`, I5 `0.840`, "7 attacks", L3 "16 tests". They occur only as history today. The "current" values in stale_numbers.yaml match the data: 52,216; 1,757,881; 1,680,816; 545,101; +46,830; 1,450,146. | Tighten per F1.

F18 | low | commit d0cc19c | The stamps for gas_benchmark, mobi_vid_backends, scaling_* and onchain_security cite `d0cc19c`. | The check-runs API for `d0cc19c` returns total_count 0, so the stamped commit has no CI run. It was pushed 24 s before d54178e. The other 29 queried commits each show 8 of 8 success, so the "8 of 8 on every closing commit" claim holds. | None needed beyond noting it.

### Checked and found sound

C1: sound except as noted in F6 and F12. Results in a clean clone at d61a284:
- The three MOBI `cmp` runs exit 0.
- The feature matrix has no diff after `hardhat compile`. It differs before compile ("ARTIFACT MISSING"), and CI order is correct.
- `make_dashboard_data.py --check`, `build_register.py --check`, `check_docs_numbers.py` (89 files) and `probe_run_identity.sh` all exit 0.
- `hardhat compile` builds 47 files. `hardhat test` gives 536 passing, 23 pending, 0 failing.
- pytest on my node (port 18583): 331 passed, 27 skipped. All 27 skips came from port 8547 being held by another process, because the MOBI layer refuses to reuse it.
- An earlier pytest run against a node on 18548 that is not mine gave 358 passed, 0 skipped.
- With an unreachable RPC, pytest gave 318 passed, 40 skipped. CI's skip grep would catch that.
- `sandbox/py-suites/run.sh -rs` gives 291 passed, 0 skipped, with no node.
- The W3C checker scores 94.3 % (41 pass, 2 fail, 1 partial of 44), above the 94.0 floor.
- `check_artifacts_fresh.js` with the root-link install reports fresh.

C2: sound for these mutations (each exited non-zero):
- V to E in a register row.
- A number in the snapshot.
- A number in `results_dashboard.html`, and separately in `dashboard_template.html`.
- Removing an `evidence_rows` entry.
- A hand edit of CRUX_REGISTER.md.
- A coverage-matrix cell, and a `test_register.yaml` entry.
- A value in `gas_benchmark.json` or `infrastructure_stats.json`.
- Status `V?`, `v`, `V`, `**F**`, `**A**`.

`**V**x` and `**V,` are accepted by design. Gaps are in F2 (rename or delete on real test sources), F3 (register text) and F1/F17 (stale-figure forms). The parser rejects F and A statuses although commit 5577a5ab aligned the register vocabulary with "F failing, A adversarial".

C3: sound. Both `--check` modes regenerate in memory and compare byte-for-byte with the committed files (make_dashboard_data.py:395-404, build_register.py:155). No generated file embeds a timestamp, since the snapshot's "generated" value is read from GRAND_REPORT.md. Running the generators twice gives no diff. The comparison is against the checked-out files, so it detects generator-versus-commit drift only (see F3).

C4: partly sound. The scanned set is 89 tracked .md files; 134 of 223 are excluded as history. The current values are correct (F17). Hidden constructions are in F1 and F17.

C5: sound on the arithmetic. I recounted the complete stamps from the JSON: 20 of 29. The nine unstamped files' classes match their content. Scope is F9.

C6: partly sound. All 13 stamp commits tested are ancestors of HEAD. The metrics `measured` trees equal HEAD (4984d75, 2e70d1f, 3c665d6, a2965fb). Since `d0cc19c`, only `infrastructure_gas.js` and `run_stamp.js` changed under the scoped paths. Problems are in F5 and F10.

C7: sound except F6. Both lockfiles agree with their package.json (`npm ci --dry-run --ignore-scripts`: 1,100 and 579 packages). The only git dependency is `ethereumjs-abi` (git+ssh, package-lock.json:5600 and :5683), and CI installs it fine.

C9: sound. See F15 for the environment-dependence caveat.

C10: sound apart from F14. `check` and `matrix` exit 0. `all` exits 0 and its counts equal GRAND_REPORT.md except timestamps and per-step gas (F13).

C11: sound. `git diff 601e1de 291bbca --stat` over sandbox, test, contracts, cv2x-testbed and 2_w3c-ssi-layer shows only the five `sandbox/grand/report/*` files. No exercised code changed after 601e1de. GRAND_REPORT "at commit 601e1de" is HEAD at run time (06:16:38Z) with only report files modified. The `--check` runs for test_register, coverage_matrix and the dashboard pass at d61a284.

C12: sound. 29 of 30 queried commits have 8 check runs, all success, with no skipped, neutral or cancelled jobs. The queried set covers the report's six closing commits plus `d61a284`, `44dc926`, `3e19e72`, `36e0309` and `601e1de`, and a sample of the rest. The jobs are 1 (test-contracts) + 3 (benchmark) + 4 (w3c) = 8, and the names are stable across the range. The exception is `d0cc19c` (no runs, F18).

C14: partly sound. `benchmark_gas.js` in a clone reproduces 55 of 55 `gas_benchmark.json` cells. Deviations are in F13.

C15: partly sound. The probe passes in a clean clone, a `--depth 1` clone and a git worktree. Modifying a tracked contract flips the JS `dirty` flag. Modifying tracked `cv2x-testbed/sumo` files flips the Python flags. Gaps are in F4 and F10.

C16: sound. Tests and generators create only ignored files, apart from rewriting tracked `sandbox/grand/report/L1-asymmetry.*` (F13). `cv2x-testbed/artifacts` matches a fresh compile with the CI linking (F6 otherwise). `metrics/runs/` is gitignored; the register cites run id `2026-10-09T02-09-36Z_7a9a996`, and `latest/meta.json` carries that runId.

C17: partly sound. The timeline arithmetic is internally consistent: no overlap among I1, I3 and I4, and `f1f9e37` precedes the I1 start. "Alone on the host" is F8. Contrary to the brief's wording, `infrastructure_revocation.json` has `tree_clean` False (I1's output) and `code_clean` True, as AAR 11 says.

C18: partly sound. `results_dashboard.html` equals the render of the regenerated snapshot and embeds snapshot and replay. It has one external resource (a Google Fonts stylesheet), no CDN scripts, and a phone breakpoint at 860 px in the CSS. The 11 GitHub links all point to existing files on an existing branch.

C19: sound for commands. The handback resume block (`npm ci`, the pip line, `run.py all`, the three checks) runs and prints the GRAND_REPORT counts. INDEX.md has no runnable commands. WM-1_REPORT.md:314 cites a "consolidated handback" that is absent from the checkout (docs/ has HANDBACK_2026-09-30, 10-04 and 10-09 only). Routing note for the coordinator.

C20: sound. Seed 7 with `--rsu`, run twice: 191 JSON leaves, and the 77 that differ are all timing statistics plus `generated_at` and `wall_clock_s`. All 71,306 trace records are identical outside timing fields. Unseeded `Account.create()` does not change any count or rejection outcome. I4 gas does vary with the key (F13).

### Not checked (and why)

- **C1:** A zero-skip pytest run against a node I own was not obtained, because port 8547 was held by another process. The 0-skip result comes from a node on 18548 that is not mine. CI job logs (skip-count line) are not readable through the provided `gh`, which refuses the log-host redirect.
- **C2 (j):** I replicated the checker's per-line logic and scanned non-.md files. I did not edit each file type through the checker, because the checker never opens them.
- **C6:** The per-producer import and diff check for each of the 20 stamps was done by experiment for the JS and Python scopes (F10) and by diff stats for the Python producers (F5). It was not done stamp by stamp.
- **C7:** No full network `npm ci` without the symlink; only `--dry-run` plus an `--offline` install in `cv2x-testbed`. Whether `git+ssh://` works without GitHub ssh keys on a stock machine was not tested (CI is green).
- **C8:** Only `pip download` of did-jwt==0.1.0 and pyld==2.0.3 was done. A full venv install of both requirements files was not completed.
- **C9:** Only one matplotlib/Pillow environment was available.
- **C12:** The `python-full-suite` log and the `metrics-harness` artifact were not readable. I read timestamps and step conclusions only.
- **C13:** A PR or push to a non-`claude/**` branch was not exercised. F11 is from workflow YAML and the default-branch API.
- **C14:** The I3 sweep was not re-run, per the brief. `infrastructure_gas.js` was run twice and compared to the two committed runs.
- **C17:** No process log, shell history or load average exists to confirm or rule out overlapping work during I1 and I3. F8 is unconfirmed.
- **C18:** The page was not rendered at 360 px, and I did no accessibility check beyond reading the CSS.
- **Outside this brief, not pursued:**
  - README.md:169 "43/43 ... CI-gated" rests on a committed `attack_results.json` that the Hardhat run does not compare (brief 5).
  - `docs/figures/results_snapshot.json` and `verification_dashboard.*` are older hand-made dashboards that no generator covers (brief 1/4).
  - #27 mentions "cryptography 49.0.0" while the V2V stamp header lists 41.0.7 in other results (brief 1).

I could not write the report file. The Write call to `REPORT_brief_3.md` under `audit_scratch/brief-3/` was rejected with "Subagents should return findings as text, not write report files", so this message is the only copy. My scratch clones, the log and JSON files, and the mutation script are under `audit_scratch/brief-3/`. I used the recorded-pid kill for my node on 18583, and it is gone.
