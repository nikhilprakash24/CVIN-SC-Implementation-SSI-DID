# Figures from the traces of record

Plan `docs/PLAN_SUMO_VISUALISATION.md`, decision S-c: **one trace of record per figure**.
Every figure states its mobility source, seed, commit and the radio caveat in the frame.
They illustrate seed 1; the evidence is the 30-run statistics (register #44–#48).

| Figure | Trace of record | Shows |
|---|---|---|
| `trace_rsu_seed1_spacetime.png` | `../traces/trace_rsu_seed1.jsonl.gz` | vehicle trajectories by identity population, RSU positions |
| `trace_rsu_seed1_latency.png` | same | verification latency over time: BSM SSI/PKI and SPaT, cold and warm |
| `trace_rsu_seed1_animation.gif` | same | top-down replay of a 1.5 km window around RSU 2 |
| `trace_rsu_seed1_replay.json` | same | every fifth step, embedded in the results dashboard |
| `trace_revocation_k5_seed1_revocation.png` | `../traces/trace_revocation_k5_seed1.jsonl.gz` | SPaT from `rsu_1` accepted per receiver before and after its revocation at 10 s, k = 5 |

Both traces: mock mobility (5 km three-lane highway), 50 vehicles, 4 RSUs, seed 1, 20 s,
commit `1e690c3`, `cryptography` 41.0.7. Their `code_dirty: false` is not evidence (the flag could
not fire until after-action report 11); the producing code was checked by hand against `1e690c3`
(no producer modified after 03:48, empty diff). The revocation trace's
mobility is identical to the other trace's (same seed), so it owns only the revocation figure.

Reproduce (from `cv2x-testbed/sumo/`):

    python3 sumo_identity_integration.py --simulate --rsu --seed 1 --duration 20 \
        --results /tmp/rsu.json --trace results/traces/trace_rsu_seed1.jsonl.gz
    python3 sumo_identity_integration.py --simulate --rsu --seed 1 --duration 20 --results /tmp/rev.json \
        --refresh-k 5 --revoke-rsu-at 10 --trace results/traces/trace_revocation_k5_seed1.jsonl.gz
    python3 render_trace.py results/traces/trace_rsu_seed1.jsonl.gz --out results/figures
    python3 render_trace.py results/traces/trace_revocation_k5_seed1.jsonl.gz --out results/figures \
        --revocation --no-animation   # then keep only the _revocation.png

`--results` keeps the run from overwriting the committed `results/v2v_latency.json`.
Timing values in a trace are one run on one host; mobility and message counts are
deterministic for a seed.
