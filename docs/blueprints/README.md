# CVIN-SSI Blueprint Set

Engineering-drawing views of the vehicle-identity system, from the primitives up to the application, generated from code. Every measured number carries its claim-register row from `docs/MEASUREMENT_CONDITIONS.md`.

**Start here:** `sheets/png/BP-000.png` (index and legend), then `sheets/png/BP-001.png` (the layer ladder).

| Document | Purpose |
|---|---|
| `PLAN_1_BLUEPRINT_PROGRAMME.md` | The plan: blueprint conventions (machine and software), the layer ladder, the 23-sheet list |
| `PLAN_2_PHASES_AND_PROMPTS.md` | Ten phases, each a prompt to paste into a fresh session |
| `PLAN_3_LIBERTY.md` | Beyond the set: data-bound figures, the primitives atlas, executable sequences |
| `SECURITY_GUARANTEE_INHERITANCE.md` | Why an identity record inherits the ledger's security, and where that stops |
| `INTEGRATION.md` | Where each sheet goes in the thesis, the docs and the defence |
| `AUDIT_REV_B.md` | P1 number audit: 17 corrections, Rev A → Rev B |

The complementary exploratory set, which Claude initiated and the author did not direct, is kept apart in `docs/figures/x_series/`.

## Regenerate

```bash
python3 docs/blueprints/make_blueprints.py            # SVG → docs/blueprints/sheets/
NODE_PATH=/opt/node-tools/node_modules node docs/blueprints/render_png.js   # PNG via Chromium
```

The `NODE_PATH` shown is the cloud container's Playwright location. Locally, `npm i playwright` and drop the prefix.
