# docs/visual — the simulation, shown

| What | Where |
|---|---|
| The plan: what we can do, what would be awesome, shot list, style, image prompts | `VISUAL_PLAN.md` |
| Phases with copy-paste prompts to run one at a time | `VISUAL_PHASES_PROMPTS.md` |
| Trace format | `TRACE_SCHEMA.md` |
| Reference traces (mock mobility 30 v / 30 s; real SUMO 60 s) | `traces/` |
| Figures F1–F6 per trace, replay screenshot, SUMO contact sheet | `figures/` |
| SUMO-GUI frames captured headless (1600×900, every 5 s) | `sumo_frames/` |
| Interactive replay viewer (open, pick a trace from `traces/`) | `replay/replay.html` |

Regenerate everything:

```bash
cd cv2x-testbed/sumo
python3 sumo_identity_integration.py --simulate --duration 30 --vehicles 30 --seed 42 \
    --results /tmp/v2v.json --trace ../../docs/visual/traces/sim_30v_30s_seed42.jsonl
python3 viz/render_trace.py ../../docs/visual/traces/sim_30v_30s_seed42.jsonl --t 0 15 --focus veh_001
```
