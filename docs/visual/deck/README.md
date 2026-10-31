# Defence deck (Phase 6)

| File | What |
|---|---|
| `cvin_v2v_defence.pptx` | 12 slides, structured: a theme with two named layouts (CONTENT, DARK) and four sections. Restyle in one place in PowerPoint |
| `cvin_v2v_defence.pdf` | the same deck rendered with LibreOffice |
| `png/slide-NN.png` | one image per slide, 96 dpi |
| `build_deck.js` | the generator; each slide's speaker notes name its figure and source |

Slides: title · four questions · the road at 100 ms · verify once · against the
budget · where cold latency goes · seven attacks · an attacker on the road ·
one message anatomised · gas per identity · what the pictures may claim · what is next.

Every data slide uses a committed figure PNG unchanged (`docs/visual/FIGURES.md`).
The gas slide is a native PowerPoint chart read from
`4_comparison-framework/results/gas_benchmark.json` (register #25); the README key-results table
agrees with both.

## Rebuild

```bash
npm install --prefix /tmp/deckbuild pptxgenjs@3.12.0            # once, outside the repository
python3 - <<'PY' > /tmp/deckbuild/assets.json                    # figure paths, aspect ratios, gas values
import json, pathlib; from PIL import Image
F = pathlib.Path("docs/visual/figures")
keys = {"f1_t0": "sim_50v_20s_seed6/F1_road_frame_t000.png", "f1_t15": "sim_50v_20s_seed6/F1_road_frame_t015.png",
        "f2": "sim_50v_20s_seed6/F2_contact_matrix_veh_045.png", "f3": "sim_50v_20s_seed6/F3_latency_strip.png",
        "f5": "sim_50v_20s_seed6/F5_cold_warm_hist.png", "f8": "sim_50v_20s_seed6_rogue_uncredentialed/F8_cold_stages.png",
        "f4": "sim_50v_20s_seed6/F4_attack_board.png", "f1_rogue": "sim_50v_20s_seed6_rogue_uncredentialed/F1_road_frame_t012.png",
        "f9_replay": "sim_50v_20s_seed6_rogue_replay/F9_rejections.png", "f7": "packet_anatomy/F7_packet_anatomy.png",
        "pair": "pairs/pair_t030.png", "replay": "replay/replay_rogue_t12.png"}
out = {k: {"path": str((F / v).resolve()), "ar": (lambda s: s[0] / s[1])(Image.open(F / v).size)} for k, v in keys.items()}
g = json.load(open("4_comparison-framework/results/gas_benchmark.json"))
out["_gas"] = sorted([(k, v["createIdentity"]["gasUsed"]) for k, v in g.items() if k != "metadata"], key=lambda x: x[1])
out["_gas_meta"] = {"commit": g["metadata"].get("commit"), "solc": g["metadata"].get("solcVersion")}
print(json.dumps(out))
PY
NODE_PATH=/tmp/deckbuild/node_modules PPTX_SKILL_DIR=<pptx skill dir, for apply_theme.js> \
  node docs/visual/deck/build_deck.js /tmp/deckbuild/assets.json docs/visual/deck/cvin_v2v_defence.pptx
```

Without `PPTX_SKILL_DIR` the deck still builds, but the theme colours fall back
to Office's stock palette until the theme is applied.
