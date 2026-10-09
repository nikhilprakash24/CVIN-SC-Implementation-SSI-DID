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
- 2026-10-09 — report opened; pre-registration and deferral list written.

## 3. Decisions
*(as made)*

## 4. Closing — *(written last)*
