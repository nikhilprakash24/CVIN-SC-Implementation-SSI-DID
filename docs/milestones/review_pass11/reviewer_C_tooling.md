> Verbatim final report of an independent reviewer agent (different model from the orchestrator's; fresh context; read-only on a frozen checkout). Extracted from the agent transcript by script on 2026-10-10 (after-action report 12, audit finding P-10); scratch paths normalised to `$SCRATCH`; model names redacted as `[model name]` (guide rule 1.3.1). Dispositions: after-action report 11 §4.

## Findings

**F1 | high | `1_blockchain-identity/scripts/lib/run_stamp.js:14-23` | The scoped `dirty` flag can never be true.**
- `git()` runs with `cwd = path.resolve(__dirname, "../..")`, which is `1_blockchain-identity/`. `MEASURED` holds repo-root-relative paths (`1_blockchain-identity/contracts`, …). Git resolves those against the cwd, so they point at `1_blockchain-identity/1_blockchain-identity/...`, which does not exist. `git status --porcelain -- <missing path>` prints nothing.
- Experiment in `review_tools/t6`: a toy repo with the same layout and the real `run_stamp.js`. I edited `1_blockchain-identity/contracts/x.sol`, then separately `cv2x-testbed/contracts/y.sol`, `benchmarks/run.js` and `4_comparison-framework/p.js`. Every case gave `"dirty":false,"dirtyAnyFile":true`.
- Running `git status --porcelain -- 1_blockchain-identity/contracts` from inside `1_blockchain-identity` prints `warning: could not open directory '1_blockchain-identity/1_blockchain-identity/'`.
- Consequences:
  - The gate behind style guide rule 1.1.6 (`STYLE_AND_RIGOUR_GUIDE.md:26`) is vacuous.
  - In `STAMP_INVENTORY.md`, `dirty False` for gas_benchmark, infrastructure_gas, mobi_vid_backends, scaling_lifetime, scaling_marginal and onchain_security means nothing. Four of those files have `dirtyAnyFile:true`.
  - `AFTER_ACTION_REPORT_09.md:56` ("all four `dirty: false`") and `AFTER_ACTION_REPORT_10.md:43` ("Run stamp `dirty` false") are false assurances.
  - `AFTER_ACTION_REPORT_09.md:122` says the helper bug was "caught because the gate was read". The fix replaced one fault with a worse one.
  - `HANDBACK_2026-10-09.md:85` ("`dirty` covers the producing code paths only") is untrue in practice.
- Possible same bug in `1_blockchain-identity/benchmarks/run.js:73`. `dirtyMeasured` uses root-relative pathspecs, and `git()` there has no `cwd`. CI runs it with `working-directory: 1_blockchain-identity`. I did not run the harness, so this is not confirmed.
- Fix: pass `cwd` as the repo root (`path.resolve(__dirname, "../../..")`), or use `git -C <root>` or `:/` pathspecs. Add a self-test that dirties a contract and expects `dirty:true`.

**F2 | high | `docs/testing/check_stamps.py:21` and `STAMP_INVENTORY.md` | The `dirty` column mixes opposite semantics.**
- The key list `["dirty","git_dirty","tree_clean"]` treats `tree_clean` as if it meant dirty. Per-file raw header fields:
  - `scaling_verify.json`: `tree_clean:true` (clean), inventory shows `True`.
  - `infrastructure_stats.json`: `tree_clean:true` (clean), inventory shows `True`.
  - `v2v_latency_stats.json`: `tree_clean:true` (clean), inventory shows `True`.
  - `infrastructure_revocation.json`: `tree_clean:false` (dirty, the I3 run), inventory shows `False`.
- A reader sees the I3 file as clean and the three clean files as dirty.
- Fully stamped:
  - "19 of 28" matches the script's definition (10 rows contain MISSING, 28 − 10 = 18 by grep, and the 19 is non-MISSING rows plus one counting artefact; the script's own `full` count is 19).
  - The definition only requires the field to exist. A dirty or inverted value still counts as stamped.
  - `dirtyAnyFile:true` files count as stamped.
  - The GLOBS miss `1_blockchain-identity/results/metrics-rpc/latest/*`, the `scaling_verify_repeats/*` files, `docs/conformance/**` (the dashboard reads these) and `sandbox/grand/report/*.json`.
  - The script always exits 0, is not in CI, and its output is not staleness-checked.
- Fix: map `tree_clean` to `not value`, and add a `code_dirty` alias. Count a file as stamped only if the dirty flag is False. Fail on dirty runs, or at least print them.

**F3 | high | `docs/testing/stale_numbers.yaml:11` (`history_markers`) | Substring markers mask live stale figures.**
- The markers include `"old "`, `"was "`, `"before"`, `"→"`, `"->"`, `" S "` and `"bundle"`. They match inside ordinary words: `"cold "` contains `"old "`, `"threshold "` matches too, and `→` is common in command output.
- Real hits in a scanned file with the checker exiting 0:
  - `INVENTORY.md:157`: "**Measured V2V result** … SSI warm verify **0.165 ms** [0.162, 0.168]; cold 0.400 ms … 90 failures = exactly the 3 injected attacks". It is presented as current and matches four stale patterns, but the "cold" in the line triggers the `old ` marker.
  - `INVENTORY.md:273`: `… → 93.2%`, masked by the arrow.
- Fix: use whole-word or regex markers, such as `\b(was|superseded|history)\b`. Better, require an explicit annotation like `<!-- history -->`. Fail if a superseded pattern appears on a line that lacks a "current" value.

**F4 | high | `docs/testing/stale_numbers.yaml` and `check_docs_numbers.py:29-31` | Formatting variants and unscanned files let superseded numbers through.**
- Mutated copy `review_tools/t4`, a thesis chapter with these lines:

| Line | Text | Result |
|---|---|---|
| 1 | `1404108 gas` | passes |
| 2 | `0.165ms` | passes |
| 3 | `0.15 ms` | passes |
| 4 | `1.404.108` | passes |
| 5 | `542 378` | passes |
| 6 | `0,165 ms` | passes |
| 7 | `93.2%` | passes (the regex needs a space or none before `%`; only `93.2 %` is caught) |
| 8 | `93.2 %` | caught |
| 9 | `0.165 ms` | caught |

- Gaps in the design:
  - The check is a denylist of 17 hand-typed regexes. Nothing compares chapter numbers against the snapshot or register.
  - `scope` is README, CAPABILITIES, COMPOSITION, SIDE_PAPERS, QUICKSTART, INVENTORY and `docs/thesis/**`.
  - Stale figures sit in unscanned files:
    - `3_cv2x-testbed/README.md:18`: "measured 93.2%".
    - `MASTER_UPDATE.md:33,50,51`: "93.2%", "0.165 ms warm".
    - `docs/PROJECT_SUMMARY.md` is also unscanned, even though register row 1 cites it.
  - Line-based matching misses numbers split across a wrapped line.
- `HANDBACK_2026-10-09.md:49` (X-7) admits that `3_cv2x-testbed/README.md` is outside the scope. Line 21 still says "all current".
- Fix: normalise before matching (strip `,`, `.`, space and NBSP between digits, and `ms` spacing). Widen scope to all tracked `*.md` except history files, using an explicit allowlist of history files instead of line markers. Add a positive check that the cited current value matches the snapshot.

**F5 | high | `docs/figures/make_dashboard_data.py:355-371` and `.github/workflows/test-contracts.yml:64` | `--check` does not cover `results_dashboard.html`.**
- Experiment in `review_tools/full`: I replaced `0.153` with `9.999` in `results_dashboard.html`, then ran `make_dashboard_data.py --check`. It printed "dashboard snapshot and crux register are current" with rc=0.
- Only `dashboard_snapshot.json` and `CRUX_REGISTER.md` are compared. CI never runs `make_dashboard_page.py`.
- The page also embeds `cv2x-testbed/sumo/results/figures/trace_rsu_seed1_replay.json`, which is not in the snapshot and not checked.
- Statements that are false:
  - `HANDBACK_2026-10-09.md:86`: "regenerate … the dashboard page; CI fails otherwise".
  - `SESSION_MANIFEST_2026-09.md:127`: lists `results_dashboard.html` as "CI-checked".
  - The `make_dashboard_page.py` docstring: "contains no number of its own".
- At commit 0ba7c6c the page is currently in sync (regenerating gives no diff). The check just would not notice drift.
- Fix: have `--check` also rebuild the page in memory and compare it. Or add `make_dashboard_page.py` plus `git diff --exit-code` to CI.

**F6 | medium | `docs/figures/dashboard_template.html:108,110,118,145,277,318` | The page does contain numbers of its own.**
- Hard-coded in the template: "15-year", "±50 %", "100 ms V2V safety budget", "five backends", "±10 %", and `Math.round(100 / ssi.warm.median)`, which bakes 100 ms into a computed KPI.
- Also hard-coded: the register row labels "(#33)", "(#4)", "(#24)", "(#38)".
- The `hypotheses` text (e.g. "≥90 %") is typed in `make_dashboard_data.py:310-318`. Its `source: README.md` is never verified.
- The experiments table (`template:315-316`) filters `verdict` to PASS or FAIL only, so any other parity verdict is silently dropped from a panel captioned "reported as they fell". Snapshot rows with verdict `(outside band)` are hidden. This looks intentional but is undisclosed.
- Fix: move these constants into the snapshot with sources, and show the dropped rows.

**F7 | medium | `docs/figures/make_dashboard_data.py:47-56` | The register status parser takes the first `**X**` anywhere in the status text and does not anchor to the cell start.**
- For all 48 real rows the result is right (V 31, S 10, E 7, matching my manual count). Every status cell begins with the marker.
- Experiment: I rewrote row 3's cell to "Unverified on trunk, was **V** earlier; now **B**". The snapshot still showed status V and by_status unchanged.
- Rows 29 and 30 show the pattern is realistic: they say "**V** … Old row **S**".
- Row order is not an issue (row 23 sits last but is parsed correctly). Rows 40 and 41 ("**S** by instrument … Was **V**") are correct only because S comes first.
- Fix: require the marker at the start of the cell, and fail on an unparsed `?` status.

**F8 | medium | `make_dashboard_data.py:260-269` (`cruxes()`) and `CRUX_REGISTER.md:5` | Crux status is not validated against its rows, and `gap` is nearly unreachable.**
- A crux is `gap` only if `evidence_rows` is empty. It is `evidenced` only if all rows are V and the hand-typed `gaps` list is empty. Otherwise it is `partial`.
- Experiment: I set C7's evidence to `[999, 11, 13]`, where 999 is not in the register and 11 and 13 are S. The output was `#999 (missing), #11 (S), #13 (S)` and **partial**. The generator exits 0, CI would pass, and the register legend says "some evidence".
- Real data: C4 and C6 include S rows (#40, #41) alongside V rows. Their text says "partial", which is acceptable but not distinguished.
- `HANDBACK_2026-10-09.md:~100` says "C3 gap → partial; no crux is a gap". All 8 cruxes are `partial` because `gaps` is typed by hand, so the state says little.
- Fix: fail on a missing row. Count only V rows as evidence. Report E, S and U rows separately, and make `gap` mean no V row.

**F9 | medium | `docs/testing/build_register.py:117-126` and `coverage_matrix.md` | The matrix reports "T" for flagged demos and ignores failures elsewhere.**
- A demo is `ok` if rc==0 and its own summary says ok. 40 of the 92 demos have `flagged > 0` (steps annotated DEFECT or OBSERVATION) and still show **T**. The legend says only "exercised by a passing demo".
- L1 records with outcome `fail` and security verdicts other than DEFENDED never reach the matrix.
- `erc-1056-vehicle/claims` has a passing demo and a TC entry, but the matrix shows **N** because the manifest says not-applicable. That is why T=91 while there are 92 demo TCs. The mismatch is silent.
- `--check` compares generated output with the committed `demos.json`. It does not re-run demos, and `demos.json` carries no commit stamp. `GRAND_REPORT.md` names commit `9006d4c`, two commits before HEAD. The contracts and tests are unchanged since then, so this is currently fine.
- A failing demo would regenerate as `F`, and `--check` would still pass once the files were consistent. CI cannot fail on a failing demo.
- TC ids are unique (the script raises on duplicates) and derive from option, op and attack names. L1 TCs share one directory location, not a test title, so they are not traceable to a test body (acknowledged in `testing/README.md` D-02).
- Fix: add a `T!` or `T*` marker for flagged demos. Warn when a demo exists for an N family. Stamp `demos.json`.

**F10 | medium | `HANDBACK_2026-10-09.md:17,21` | Overstated claims about stamping and "all current".**
- Line 17 says "producers stamped (commit, dirty)". The inventory shows 9 of 28 files unstamped, and the `dirty` values are meaningless per F1 and F2.
- Line 21 says "stale-figure check: all current, all CI-checked". F3 and F4 show real stale figures that pass.
- Line 12 still reports "Python layers 260" next to the §7 figure of 276 (internal inconsistency).
- Line 23: "all 8 jobs green on `577a5ab`". I confirmed 8 jobs exist and are green on 0ba7c6c via `gh api` check-runs. That includes the `Check the dashboard snapshot…` step, so the CI wiring is real. I did not verify the claim for `577a5ab` itself.

**F11 | low | `docs/PROJECT_SUMMARY.md:276` | Model identifier "[model name]" in a committed file.**
- "The [model name] pass will take it…". It sits in a project file. `[model name]` is the only direct hit for [model name], [model name], [model name] or [model name], and no `claude-<model>` strings were found.
- Other tracked artefacts that leak session identity:
  - 23 historical commits authored as "Claude <noreply@anthropic.com>".
  - 5 commit messages with trailers, e.g. `ffedb4e`.
  - `/tmp/claude-0/...` scratchpad paths in `cv2x-testbed/results/pki_vs_erc1056.{json,md}` and about 40 `docs/conformance/reports/**` files.
  - `docs/reconciliation/RECON_TSR.md:289` mentions the trailer rule.
- Fix: reword the "[model name]" line. Decide whether the path leaks need scrubbing.

## Checked and found sound
- `make_dashboard_data.py --check` and `build_register.py --check` pass on the frozen tree. The generated output is deterministic: `make_dashboard_page.py` rewrote an identical file.
- Register parse on `MEASUREMENT_CONDITIONS.md` §3 matches my manual count (48 rows, V 31, S 10, E 7). Row 23 at the table end and the multi-status rows 6, 17, 29, 30, 40, 41 are classed correctly. Rows 1-4 are classed correctly.
- `defects()` classification of D1-D27 and D11b (28 rows, H12/M12/L4 by `counts`) matches the log's first-token statuses.
- `build_register.py`: duplicate TC ids raise `SystemExit`. T91/N78/G13 is arithmetically correct, and every G is on the two baselines as `AFTER_ACTION_REPORT_09.md` says.
- CI: `test-contracts.yml` calls all three checks with `shell: bash` and no `|| true` or `continue-on-error`. There are no such constructs in the other workflows apart from the intentional `|| true` in a grep inside `w3c-compliance.yml:149`. The step passed in run 37884980550 (job 113672842755). `pyyaml` is installed in that step, and the scripts import only `yaml` and the stdlib. The generated-document checks run only on push to main or `claude/**` and on PRs to main.
- Job count of 8 is correct (3 benchmark, 1 contracts, 4 w3c). All 8 are green on 0ba7c6c.
- The 19 of 28 figure is the script's own count under its definition. The CI-checked claims for snapshot, crux register, test register and coverage matrix are literally true.

## Not checked (and why)
- Whether the `stale_numbers.yaml` "current" values equal the register. I did not recompute each of the 17 entries.
- Per-file correctness of dashboard values against raw result JSON. I checked structure and sources only, not each of the several hundred numbers.
- The claim "577a5ab green" and the Python 276 and 358 counts. Re-running the grand runner was out of scope.
- `benchmarks/run.js` `dirtyMeasured` cwd bug (F1 aside). I did not execute the harness.
- `3_cv2x-testbed/README.md` and `MASTER_UPDATE.md` for other stale figures beyond 93.2% and 0.165 ms.
- Full history scan for model identifiers inside commit diffs. I scanned the HEAD tree and commit message metadata only.
