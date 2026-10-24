# Trace schema used by the visual layer

**Canonical schema:** `cvin-v2v-trace/1`, approved by the author on 2026-10-09
(`docs/PLAN_SUMO_VISUALISATION.md` §3, decision S-a; as-built differences in §7.1).
It is written by `cv2x-testbed/sumo/sumo_identity_integration.py --trace PATH`
(plain, or gzipped when PATH ends in `.gz`). This page records only what the
visual work added. Nothing existing was renamed or removed.

**Readers:**

| Reader | Output |
|---|---|
| `cv2x-testbed/sumo/render_trace.py` (trunk, WM-1) | space-time, latency, animation GIF, dashboard replay JSON, revocation |
| `cv2x-testbed/sumo/viz/thesis_figures.py` | thesis figures F1–F6 (road frame, contact matrix, latency strip, attack board, cold/warm, safety) |
| `cv2x-testbed/sumo/viz/sumo_views.py` | cold map over the real network, SUMO-frame / trace-frame pairs |
| `docs/visual/replay/replay.html` | interactive replay (reads `.jsonl` and `.jsonl.gz`) |

## Additive fields (visual work, 2026-10-24)

| Where | Added | Why |
|---|---|---|
| new event `enroll` | `t`, `id`, `pop` (`ssi`/`pki`), `did` (SSI only), `vin`, `make`, `model`, `year`, `vtype` | identity card in the replay; public identifiers only, never key material, signatures or credentials (audit brief 2, C15 still holds) |
| new event `safety` | `t`, `app` (`FCW`/`EEBL`), `id`, `warned`; FCW adds `target`, `ttc_s`, `gap_m` | the safety-events figure and the replay log |
| `attack` events | V2V attack outcomes (`tampered_*`, `stale_*`, `replay_*`, `uncredentialed_sender_rejected`) with `reason`, `expected`, `cold` = null | the attack board; before this only the infrastructure (I2) attacks were traced |
| `step.vehicles[]` | `lane` (lane id) | lane rows in the road frame; FCW lane test |

The aggregates gate of `PLAN_SUMO_VISUALISATION.md` §3 still holds. A run with
`--trace` gives the same message counts as the same seed without it. This was
checked on seed 6 of the registered N=30 configuration: sent and verified
counts were identical.

## Committed traces

See `traces/README.md`. All are gzipped, following decision S-c.
