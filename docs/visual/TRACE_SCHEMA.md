# V2V identity event trace — schema

**Writer:** `cv2x-testbed/sumo/sumo_identity_integration.py --trace PATH`
**Format:** JSON Lines (one object per line, UTF-8). Every object has `"ev"`.
**Readers:** `cv2x-testbed/sumo/viz/render_trace.py` (figures F1–F6),
`docs/visual/replay/replay.html` (interactive replay).

The trace records *what happened*; it does not change *what is measured*.
Every latency in it is the same `time.perf_counter` sample the results JSON
is built from. Tracing adds wall-clock time (file writes), never
identity-verification time. Figures and the replay therefore show the same
numbers as `results/v2v_latency.json` for the same run.

## Events, in order of first appearance

| `ev` | When | Fields |
|---|---|---|
| `meta` | once, at start | `generated_at`, `mode` (`simulate` or `sumo`), `seed`, `duration_s`, `step_s` (0.1), `bsm_rate_hz` (10), `neighbor_radius_m` (300), `max_neighbors` (8), `budgets{v2v_ms, sig_check_ms}`, `road` (simulate: `length_m`, `lanes`, `lane_y`; sumo: `source`), `snapshot_every` |
| `enroll` | first time a vehicle is seen | `t`, `vehicle`, `identity` (`MOBI_VID` = SSI, `PKI`), `did` (SSI only), `vin`, `make`, `model`, `year`, `sumo_type` |
| `snap` | every `snapshot_every` steps, before that step's broadcasts | `t`, `step`, `v`: list of `[vehicle, x_m, y_m, speed_mps, heading_deg, lane_id]` |
| `tx` | every signed broadcast | `t`, `seq`, `sender`, `type` (`BSM`, `FCW`, `EEBL`), `emergency`, `pop` (`ssi`/`pki`), `sign_ms`, `rx`: list of `[receiver, ok, cold, latency_ms]` |
| `safety` | FCW or EEBL raised | `t`, `app` (`FCW`/`EEBL`), `vehicle`, `warned` (receivers that verified it); FCW adds `target`, `ttc_s`, `gap_m` |
| `attack` | after the run, one per injected attack | `t`, `name`, `rejected` |
| `summary` | once, at end | the full results JSON (same object as `results/v2v_latency.json`) |

`cold = true` means the receiver had no cached key for that sender's current
credential and ran the full path (PKI: certificate chain + validity + CRL +
ECDSA; SSI: W3C VC structure, validity, revocation, issuer signature
recovery, trusted-issuer check, subject/DID binding, then BSM signature
recovery). `cold = false` is one signature check against the cached key.
A PKI sender's pseudonym certificate rotates every 100 messages, so a PKI
peer re-enters cold at each rotation; an SSI peer is cold once per receiver.

## Sizes

About 300 events per simulated second at 30 vehicles (one `tx` per vehicle
per 100 ms step plus one `snap`). 30 s / 30 vehicles ≈ 2.4 MB; 60 s in
TraCI mode with ~26 vehicles ≈ 3.6 MB. `--trace-every N` thins only the
`snap` events; `tx` is never thinned, so figure counts stay exact.

## Reproduce the committed traces

```bash
cd cv2x-testbed/sumo
# mock mobility, real crypto (no SUMO needed)
python3 sumo_identity_integration.py --simulate --duration 30 --vehicles 30 --seed 42 \
    --results /tmp/v2v.json --trace ../../docs/visual/traces/sim_30v_30s_seed42.jsonl
# real SUMO mobility over TraCI (pip install eclipse-sumo)
python3 sumo_identity_integration.py --duration 60 \
    --results /tmp/v2v.json --trace ../../docs/visual/traces/sumo_traci_60s.jsonl
```

`--results` is pointed away from `results/v2v_latency.json` on purpose: that
file is the result of record (register row #27) and is only rewritten by the
N=30 statistics driver.
