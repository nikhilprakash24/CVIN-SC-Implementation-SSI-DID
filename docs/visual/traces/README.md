# Reference traces (cvin-v2v-trace/1, gzipped)

Schema: `docs/PLAN_SUMO_VISUALISATION.md` §3/§7.1 plus the additive fields in
`../TRACE_SCHEMA.md`. Traced runs write `--results` to scratch, so no file here
is a result of record; that is register row #27. Each header carries the commit
and the `code_dirty` flag.

| File | What | Command (from `cv2x-testbed/sumo/`) |
|---|---|---|
| `sim_50v_20s_seed6.jsonl.gz` | Seed 6 of the registered N=30 configuration (50 vehicles, 20 s, mock mobility). It is the median seed by SSI warm p95 in the traced N=30 run of 2026-10-22 | `python3 sumo_identity_integration.py --simulate --duration 20 --vehicles 50 --seed 6 --results /tmp/s6.json --trace ../../docs/visual/traces/sim_50v_20s_seed6.jsonl.gz` |
| `sim_50v_20s_seed1.jsonl.gz` | Seed 1 of the same configuration, the worst seed by SSI warm p95 | same, `--seed 1` |
| `sumo_traci_60s.jsonl.gz` | Real SUMO 1.28 over TraCI, headless, 60 s | `python3 sumo_identity_integration.py --duration 60 --results /tmp/t.json --trace ../../docs/visual/traces/sumo_traci_60s.jsonl.gz` |
| `sumo_gui_45s.jsonl.gz` | SUMO-GUI under Xvfb, 45 s: the run that produced `../sumo_frames/` and `../figures/pairs/` | `xvfb-run -a -s "-screen 0 1600x900x24" python3 sumo_identity_integration.py --gui --duration 45 --screenshot-dir ../../docs/visual/sumo_frames --screenshot-every 50 --gui-zoom 400 --gui-track platoon_leader --trace ../../docs/visual/traces/sumo_gui_45s.jsonl.gz --results /tmp/g.json` |

**How the median and worst seeds were chosen.** On 2026-10-22, at commit
`65aa8a8`, Python 3.13.16, coincurve 21.0.0 and an Intel Xeon 2.10 GHz, the
command below ran all 30 seeds:

```bash
python3 run_v2v_stats.py --runs 30 --duration 20 --vehicles 50 --out DIR/stats.json --trace-dir DIR
```

The totals matched #27 exactly: 1,650,318 verifications, and 210 failures from
the 7 attacks in each of 30 runs. The across-run SSI warm median was 0.141 ms,
consistent with #27's re-executed 0.142 ms [0.141, 0.143]. Per-seed traces are
about 3 MB each and are not committed. Mobility and message counts are
deterministic for a seed, so they regenerate exactly; timings are one run on
one host.
