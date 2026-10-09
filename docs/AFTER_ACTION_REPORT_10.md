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

## 3. Decisions
- **F-A** (taken before the registered runs; the pre-registration was silent on it). I1 runs with
  k = ∞ (no revocation re-check on the warm path), because the BSM warm path it is compared with
  has none. The cost of re-checking is visible in I3, which runs k = 1, 5, 25, ∞.
- **F-B.** I3 runs the same 30 seeds as I1, revoking `rsu_1` at t = 10 s.

## 4. Closing — *(written last)*
