# After-Action Report 14 — Work Milestone WM-2, Step A2 (One Stamp Helper with Per-Producer Scope)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-12, after report 13 closed at `e639dad` (CI 8/8 green); closed at the end of this pass
**Brief:** the author's "accept defaults and continue to the next executable". The next executable is
`docs/PLAN_WM-2.md` step **A2** (defect D49, audit T-F10).

## 1. Plan
| Step | Work | Gate |
|---|---|---|
| A2.1 | One scope table, `run_identity/scopes.json`, read by both a JS helper (`1_blockchain-identity/scripts/lib/run_stamp.js`) and a Python helper (`run_identity/stamp.py`): each scope lists the root-anchored paths of the code a producer runs, results excluded; each producer of record names its scope | one file defines every scope; neither helper carries its own path list |
| A2.2 | The producers move to the helper: the JS scripts, the metrics harness (`dirtyMeasured`, the unanchored pathspec of N-19), the security harness, the SUMO drivers, the `cv2x-testbed/scripts` experiments, the richness driver; existing stamp field names kept, so `check_stamps.py` and the L4 record tests read old and new stamps alike | every producer in the stamp inventory uses the helper or is listed as not converted, with the reason |
| A2.3 | A scope check: each producer's import closure (Python `import`, JS relative `require`) resolved statically and shown to lie inside its scope | `stamp.py --check` exits 1 on a producer importing code outside its scope; in CI |
| A2.4 | The run-identity probe extended to every scope: an edit to a tracked imported file (not only an untracked file) marks the run dirty; a results file does not; a broken helper (pathspecs not root-anchored) fails the probe | probe shown to fail on a broken helper and to pass on the real one; in CI |

Out of scope: re-running any producer (A3, A3b, A6 do that after C0–C2); the harness flag change is code
only here, and A6 still owns the harness re-run of record.

## 2. Execution log
- 2026-10-12 — report opened.
- **A2.1 scope table.** `tools/run_identity/producers.json` (hand-maintained) names 20 producers of record:
  the result paths each writes, and the non-code inputs it reads (two input sets: the Hardhat project; the
  testbed chain, including the tracked `cv2x-testbed/artifacts/contracts` the Python providers load, which no
  earlier scope covered). A child-process producer listed as an input brings its own scope
  (`run_gas_stats.py` runs `benchmark_gas.js`; `attack_scenarios.py` runs `security_scenarios.js`).
  `stamp.py --write` resolves each import closure statically (every `import`, nested ones included, on the
  producer's directory plus the declared `sys.path` directories; JS relative `require`) into `scopes.json`.
  Closures range from 1 file (`render_trace.py`) to 27 (the metrics harness). Both helpers read only
  `scopes.json`; neither carries a path list. Results directories are excluded by glob.
- **A2.2 producers.** 14 of 20 call the helper with their own file: 6 JS scripts (`runStamp(__filename)`;
  `experiment_pseudonym_pool.js` had only a whole-tree flag), the SUMO drivers (`sumo_identity_integration`,
  `run_v2v_stats`, `run_infra_stats`, `run_verify_scaling`), the three testbed experiments, and
  `run_verify_richness`. Two of these had no code flag at all before (`run_verify_scaling` and
  `run_verify_richness` had a whole-tree `tree_clean` only); the three testbed experiments had only the
  whole-tree `git_dirty` and now carry `code_dirty` too. Stamp field names are kept (`dirty`, `code_clean`,
  `code_dirty`), with `scope` and `scope_sha` added, so `check_stamps.py` and the L4 record tests read old and
  new stamps alike. Not converted: the four unstamped "stamp producers" (A3: `attackHarness.js` writes a
  tracked file on every `npx hardhat test`, D56, so its stamp waits for the promote step A4), and
  `render_trace.py` (derived figures; it echoes the trace's stamp).
- **The metrics harness: made, then reverted (a departure from §1).** `benchmarks/run.js` was moved to the
  helper in the first commit (`188efec`). Checking N-19's recorded reason afterwards showed the deferral was
  deliberate: any edit to `run.js` changes `benchmarksTree`, the identity of the harness run of record
  (conditions §5.F). At `2ef1133` HEAD's tree matched the run of record's (`4984d75…`); after `188efec` it did not
  (`4b44a3b…`). The file is restored to its pre-A2 content in the second commit, so HEAD's tree is `4984d75…`
  again; the harness stays a registered producer with a probed scope, and A6 makes the one-line switch with
  its re-run. Lesson: read an item's recorded reason for deferral before folding it into a neighbouring step.
- **A2.3 scope check.** `stamp.py --check` (in CI) fails when `scopes.json` is stale or when a producer imports
  a name some repository file has but the import does not resolve on the declared search path. Shown to fail
  on both: a producer given a new local import without regenerating; a producer importing a module placed
  outside the search path. The first resolver missed namespace packages (`identity`, `sumo` have no
  `__init__.py`) and reported seven unresolved imports; fixed before commit.
- **A2.4 probe.** `tools/run_identity/probe.py`, called by `docs/testing/probe_run_identity.sh` in CI: for each
  of the 20 producers, both helpers, called from the producer's own directory, must read clean on the tree,
  dirty after a one-byte edit to a tracked file in the closure and after a new file in an input directory,
  and clean with a new file in each results directory (158 helper checks; 12 s). The script then checks that
  the SUMO headers flip on an edit to `cv2x-testbed/identity/freshness.py`, imported code outside the drivers'
  directory: the case the old single-file probe could not see. The old probe's "untracked file in
  `cv2x-testbed/sumo`" case no longer applies: scopes are file-level, so a new file nothing imports is not
  producing code. Passed on the clean tree, which was clean again afterwards. **Four broken helpers, each
  failing:**

  | Mutant | What it breaks | Probe failures |
  |---|---|---|
  | Python helper, git from the caller's cwd with unanchored pathspecs | the after-action-report-11 fault | 36 |
  | Python helper, scope = the producer file only | D49 (no import closure) | 35 |
  | JS helper, unanchored pathspecs from the caller's cwd | the report-11 fault, JS | 36 |
  | JS helper with the pre-A2 fixed path list | **D49 as found:** misses an edit to `attackHarness.js` for `security_scenarios.js`, and every Python producer's imports | 18 |
- **Inventory.** `check_stamps.py` now takes the producing code of each result from the scopes (the union
  over every producer that writes it), without the two helpers. Effect on "code changed since": the two
  infrastructure results (`infrastructure_stats`, `infrastructure_revocation`) go from yes to **no**. The old
  family scope covered all of `2_w3c-ssi-layer`, and the only change there since `f1f9e37` is two test files
  added by the WM-1 audit, so "yes" was a false positive. The pass-06 history diff has no producer and reads
  MISSING, like the other history rows. No row went from no to yes.
- **Stamp-only commits.** The producer edits of `188efec` would turn every "no" into "yes" while changing no
  measured behaviour. `STAMP_ONLY_COMMITS` in `check_stamps.py` lists such commits. A result whose code
  differs from its stamp only by listed commits reads "no (stamp-only)", which 10 rows do now (the harness run of record reads plain "no": `run.js` is back to its stamped content). `--check-coverage`
  verifies each listed commit line by line: within producing code, every changed line must be stamp code.
  A control, listing `f1f9e37` (the verifier hardening), gives 204 problems.

- **CI red on `4e99cf1`, then fixed.** 7 of 8 jobs passed. "Compile and test contracts" failed in its document-check
  step: CI checks out one commit (depth 1), so `git show 188efec` in the stamp-only verification had no
  history and raised a traceback. Reproduced in a local `--depth 1` clone. Fix: the job checks out full history
  (`fetch-depth: 0`, about 7 MB). A shallow clone now fails with a message naming the cause. This is a fault of
  this pass: every local check ran on a full clone, so none of them could see it. CI on the fixed commit:
  see §3.
- **Grand run (last).** ALL OK: smoke 11 adapters, L1 99, Hardhat 537, Python layers 305, 92 demos /
  1,752 steps (594 mined transactions). These are the WM-1 close counts unchanged, as expected for a step that
  changed no measured code. One L1 cell moved: CVIN-Combined `claim` 316,477 → 316,439 gas. This is the
  random-input variation the WM-1 audit recorded (316,465 and 316,451 on two clean clones; audit briefs 3 and
  5, finding U-F11), scheduled for B1 (N-18). No chapter or register row quotes it. The snapshot and test register
  were regenerated from the run.

## 3. Closing
A2 done: D49 fixed. One scope table drives both helpers; 14 of 20 producers use it, and the other six are
assigned (A3, A6, derived). The probe shows, for every producer and both languages, that an edit to imported
code marks the run dirty. It fails on four broken helpers, one of them the pre-A2 list that is D49 itself.
No result was re-run and no register row changed. The inventory corrected two false "code changed since"
flags. One CI failure, caused by a shallow clone and found only by CI, was fixed in the same pass.

One departure, recorded above: the harness edit was made against N-19's recorded reason and reverted in the
same pass. HEAD's `benchmarksTree` equals the run of record's again.

Next: WM-2 step A4, the promote step (`runs/<id>/`, promote only on a clean stamp), piloted on one producer.
Then C0, verifier v3 with the D51 fix (`docs/PLAN_WM-2.md` §4).
