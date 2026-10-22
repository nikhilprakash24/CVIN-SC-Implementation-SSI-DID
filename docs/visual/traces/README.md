# Reference traces

Schema: `../TRACE_SCHEMA.md`. Traced runs write `--results` to scratch, so no
file here is a result of record (that is register row #27).

| File | What | Command |
|---|---|---|
| `sim_50v_20s_median.jsonl` | Seed 6 of the registered N=30 configuration (50 vehicles, 20 s, `--simulate`): the median seed by SSI warm p95 (0.2505 ms) | `run_v2v_stats.py --runs 30 --duration 20 --vehicles 50 --trace-dir DIR`, then `DIR/seed_006.jsonl` |
| `sim_50v_20s_worst.jsonl` | Seed 1 of the same run: the worst seed by SSI warm p95 (0.2799 ms) | same run, `DIR/seed_001.jsonl` |
| `sim_30v_30s_seed42.jsonl` | 30 vehicles, 30 s, seed 42, `--simulate` | see `../TRACE_SCHEMA.md` |
| `sumo_traci_60s.jsonl` | Real SUMO 1.28 over TraCI, 60 s, headless | see `../TRACE_SCHEMA.md` |
| `sumo_gui_45s.jsonl` | Real SUMO-GUI under Xvfb, 45 s, the run that produced `../sumo_frames/` | `xvfb-run -a -s "-screen 0 1600x900x24" python3 sumo_identity_integration.py --gui --duration 45 --screenshot-dir ../../docs/visual/sumo_frames --screenshot-every 50 --gui-zoom 400 --gui-track platoon_leader --trace ../../docs/visual/traces/sumo_gui_45s.jsonl --results /tmp/v2v_gui.json` |

**Traced N=30 run, 2026-10-22.** Commit `65aa8a8`, Python 3.13.16, coincurve
21.0.0, Intel Xeon 2.10 GHz. 30/30 seeds completed. Its totals match row #27
exactly (1,650,318 verifications). The 210 failures are the 7 injected attacks
× 30. Across-run SSI warm median is 0.141 ms [0.140, 0.142] against the
registered 0.153 ms. That is a different host and day with tracing on, so these
numbers are illustrations, not a re-measurement. The 28 other per-seed traces
(97 MB in total) are not committed. Regenerate them with the command above.
