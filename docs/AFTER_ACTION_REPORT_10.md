# After-Action Report 10 — Building the Approved Designs: Infrastructure Messaging and the SUMO Trace

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-09, before any code; updated per step; closed at the end
**Trunk at start:** `0874b99`, clean, CI green
**Brief:** "approve both designs with defaults and continue — push Infura or other decisions that can be
pushed to the next milestone." Defaults: I-a approved, I-b back-haul included and reported only, I-c RSU
layer in the visualisation, I-d chapter-5 section if run; S-a approved, S-b no SUMO install, S-c one
trace of record per figure. Deferred decisions: `docs/MILESTONE_NEXT.md`.

## 1. Plan
| Step | Work | Gate |
|---|---|---|
| B0 | Lock the pre-registration (`docs/design/INFRASTRUCTURE_PREREG.md`) and the deferral list in a commit before any code | committed first |
| B1 | Infrastructure layer: road authority, RSU, controller and TMC identities; signed SPaT and I2I messages; permitted-type check; revocation with refresh-every-k (`cv2x-testbed/sumo/infrastructure_layer.py`) | unit tests (L3) incl. every I2 attack |
| B2 | Trace recorder (`--trace`) and `--rsu` in the harness; both off by default | a run without the flags reproduces the counts of a run before the change; a run with `--trace` reproduces the counts of one without |
| B3 | Experiments: `run_infra_stats.py` (I1, I2, I5 over 30 seeds), I3 revocation sweep, `infrastructure_gas.js` (I4) | results files with environment headers, clean tree |
| B4 | Register rows #44–#48, crux C3 evidence, defect log if anything breaks | snapshot, register, stale check current |
| B5 | Renderers: static figures and animation from a committed trace; dashboard panel (V2, V3, V5) | figures regenerate from the trace |
| B6 | Grand run, CI, dashboard republish, handback addendum, meta commentary, close | ALL OK; CI green |

## 2. Execution log
- 2026-10-09 — report opened; pre-registration and deferral list committed before any code (`cfbdcbc`).
- **Baseline for the no-change gate.** The unchanged harness, seed 7, 10 s: sent 5,011, delivered
  26,877, verified 26,877, rejected 5 (the injected V2V attacks), 11 safety events.
- **B1.** `cv2x-testbed/sumo/infrastructure_layer.py`: road authority as the only trusted issuer;
  RSU, controller and TMC identities; signing as for SSI BSMs; verification with a permitted-message
  check and a revocation re-check every k messages. 16 L3 tests, every I2 attack (a)–(g), the I3 bound
  for k = 1, 5, 25 and the k = ∞ case.
- **B2.** `--rsu`, `--refresh-k`, `--revoke-rsu-at`, `--trace` in the harness, all off by default.
  Gate: with the flags off, and with `--trace` on, the seed-7 counts are identical to the baseline.
  A 10 s trace is 290 KB gzipped (100 step, 5,011 tx, 26,877 rx events).
- **Trial run, disclosed.** Before the registered runs one trial (seed 3, 20 s) on uncommitted code
  checked the wiring: all seven I2 attacks rejected; per-k revocation counts within k − 1. It is not a
  result and is not reported as one.
- **B3, registered runs** at `1e690c3`. Verdicts reported as they fell:
  - **I1 PASS** — median SPaT/BSM warm-verify ratio 0.996, 95 % CI [0.995, 1.001], N=30 (band
    [0.80, 1.20]). Header `tree_clean` true. 6 min.
  - **I2 PASS** — all 7 attacks rejected in 30/30 runs; 0 of 138,895 legitimate SPaT rejected.
  - **I5** (reported) — controller → RSU → vehicle 0.840 ms [0.832, 0.845]; TMC hop 0.433 ms.
  - **I4** (reported) — RSU key anchor 52,594 gas (the same write as the ERC-1056 create cell of #6);
    hand control to the authority 51,754; rotate 35,498; revoke old key 35,050; creation 0. Run
    stamp `dirty` false.
  - **I3 PASS** — max SPaT accepted after revocation 0 / 4 / 24 for k = 1 / 5 / 25 (bounds 0 / 4 / 24,
    each reached); k = ∞ 100. 28 min. The trial's k = 25 count was 21; the registered one is 24 —
    which seed reaches the bound depends on where each vehicle sits in its refresh cycle at
    revocation.
- **Finding, run identity (I3).** The header's `tree_clean` is false: `environment_header()` runs a
  whole-tree `git status`, and when I3 started, I1's results file had just been written and the
  renderer was untracked. Checked by hand against rule 1.1.6: the producing code had an empty diff
  against `1e690c3` and no producer's mtime is after the start. Accepted as a run of record and
  disclosed in register #46; the fix (scope the flag, as `run_stamp.js` already is) is N-14. Same
  failure class as the run-stamp fault of pass 9 — this second instance was in a Python header the
  pass-9 fix did not reach.
- **Finding, I4 wording.** The pre-registration named "revocation of the RSU identity"; ERC-1056 has
  none. The nearest operation (key revocation) was measured and the deviation disclosed in #47.
- **B4.** Register rows #44–#48 (V); crux C3 gap → partial (evidence #44–#48; remaining gaps: mock
  mobility, no radio, in-process back-haul, RSU-to-RSU not modelled); C4 gains #46. Chapter 5 §5.4.1
  drafted (default I-d). Snapshot, crux register, test register, stale check (0) current; stamp
  inventory 19/28.
- **B5.** `render_trace.py` renders spacetime, latency, revocation, a GIF and the dashboard replay
  from the two traces of record (seed 1; `code_dirty` false). The revocation trace's spacetime,
  latency and replay outputs were byte-identical to or redundant with the first trace's (same seed,
  same mobility) and were removed under S-c; `results/figures/README.md` maps each figure to its
  trace. The dashboard gained the infrastructure panel and the replay; a headless check found an
  empty band above the replay controls (grid stretch), fixed. No horizontal scroll at 390 px.
  Committed `9006d4c`.
- **Not added, recorded instead.** The TSR test register is built from L1, the security harness and
  the demos; the 16 L3 infrastructure tests are counted by the grand runner only (N-15).
- **B6, grand run** on `9006d4c`: ALL OK — smoke 11/11, L1 99, Hardhat 536 passing, Python layers
  276 (260 + the 16 infrastructure tests), 92 demos / 1,752 steps.
- **Finding, L1 gas is input-dependent.** Against the previous grand report, 3 of 99 L1 gas cells moved
  with no contract change: CVIN-Combined claim −26, revoke +9, ERC-725Y/X signed-op −12. Those tests
  use random claim ids and keys; the mechanism was not isolated. No register row cites the L1 table (it
  is the feature-asymmetry view; gas of record is the benchmark, #25). Seeding those inputs would make
  the table reproducible to the unit (N-18).

## 3. Decisions
- **F-A** (taken before the registered runs; the pre-registration was silent on it). I1 runs with
  k = ∞ (no revocation re-check on the warm path), because the BSM warm path it is compared with
  has none. The cost of re-checking is visible in I3, which runs k = 1, 5, 25, ∞.
- **F-B.** I3 runs the same 30 seeds as I1, revoking `rsu_1` at t = 10 s.
- **F-C** (after the run). The I3 run is accepted as a run of record although its whole-tree
  `tree_clean` is false: rule 1.1.6 is about the producing code, which was checked by hand and found
  equal to `1e690c3`. Re-running for 28 min to flip a flag that measures the wrong thing was judged
  worse than disclosing it; the flag's fix is N-14. **Accepted by the author, 2026-10-09.**
- **F-D.** Under S-c the revocation trace owns only its revocation figure; its spacetime, latency and
  replay outputs (same seed, same mobility as the first trace) were deleted, not committed.

## 4. Closing
**Plan vs done.** B0–B6 all closed. Commits: `cfbdcbc` (pre-registration, deferral list), `47c3314`
(layer, flags, driver, tests), `1e690c3` (header at start), `9006d4c` (results of record, register,
chapter section, figures, dashboard), `94c2b7c` (grand run, reports). CI: all 8 jobs green on `9006d4c`
and `94c2b7c`. Dashboard republished (version 4, same URL).

**Verdicts, all pre-registered.** I1 PASS, I2 PASS, I3 PASS (bound reached at every finite k), I4 and
I5 reported. Crux C3 moves from gap to partial; no crux is a gap any more. No contract changed; no
existing register row changed.

**What went wrong.** (1) The Python environment header counted a results file as a dirty tree,
the same class of fault fixed in pass 9 in the JavaScript run stamp. The fix was not generalised then.
(2) The pre-registration named an operation that ERC-1056 does not have. Both were caught and
disclosed, neither changed a verdict. (3) Two of the revocation trace's figures were redundant and
were produced before anyone asked which trace owns which figure; S-c should have been applied at
render time, not after.

**What the author should look at.** Register #44–#48 and §5.4.1 of chapter 5; F-C (accepting the I3
run with a false whole-tree flag); N-17 (the k the thesis defends now has a safety reading: 24
messages, 2.4 s, at k = 25).

### 4.1 How the team structure performed
| Role in this pass | Work | Outcome | Acceptance gate the orchestrator re-ran |
|---|---|---|---|
| Orchestrator (architect) | pre-registration, layer, harness flags, drivers, renderer, register rows, chapter section, dashboard, reports | all steps closed | no-change gate on seed 7; L3 16/16; grand run; CI; headless render |
| Security engineer (role, same configuration) | attack set (a)–(g) and the untrusted-issuer cases | all 7 rejected in 30/30 runs | L3 tests per attack; the I2 count in every run |
| Measurement methodologist (role) | verdict rules before code; F-A before the runs; run-identity check after | I3 run-identity fault found and disclosed | rule 1.1.6 checked by diff and mtimes |
| Visualisation engineer (role) | trace schema, renderer, dashboard replay | redundant outputs removed (F-D); layout fault found headless and fixed | figures regenerate from the trace; md5 comparison |
| Thesis methodologist (role) | chapter 5 §5.4.1, crux C3/C4, meta commentary | the first-contact claim in §5.4.1 was attributed to the L3 test, not the sweep | every number traced to a V row |
| Adversarial reviewer | — | reserved (Q7, N-10) | — |

No sub-agents were spawned this pass: the work was one connected chain (layer → harness → runs →
register → chapter), and splitting it by file would have put two writers on the harness. The roles
were therefore lenses applied by one worker, which is weaker than pass 9's split. The independence
the structure promises was again only procedural. What it still bought was that each role's
question was asked at its step (the methodologist's "which code produced this run?" is what found
the I3 flag), not that anyone disagreed with the orchestrator. The case for the different-configuration
adversarial review (N-10) is stronger after this pass than before it.
