# Blueprint Set — P2 Data Binding (Rev B → Rev C)

**Date:** 2026-10-31 · **Scope:** Plan 2 phase P2. Every measured value on the 23 sheets is now read from a result-of-record file at generation time. No measured value is typed into a sheet module. CI now fails if the sheets and the results disagree.

## What changed

| Piece | File | What it does |
|---|---|---|
| Data layer | `data.py` | 169 named values, each with a loader, a display format, a source path and a register row |
| Lock | `data.lock.json` | The value of every key when the sheets were last accepted |
| Generator | `make_blueprints.py` | `--check` fails on drift or a stale SVG; `--update-lock` accepts a deliberate re-measurement |
| CI | `.github/workflows/benchmark.yml`, job `blueprint-data-check` | Runs `--check` on every push to `claude/**` and nightly; standard library only |
| Sheets | `sheets_*.py` | Literals replaced by `D("key")` / `raw("key")`. The BP-403 lens tables are read from the two CSVs, with a column-order assertion |

Most values come from a result file: gas, lifecycle, V2V, freshness-k, PKI, parity, read path and both security tables. Where no file holds the value, `data.py` parses it from the register row by pattern. That covers the W3C checker score (#4), the external suite (#24), the attestEvent gas (#28), createVehicleDID (#6) and the fit tolerance (#32). The extrapolated P* is parsed from `LATENCY_BUDGET.md`, the canon S1 gas from `BASIC_ID_SET_EXTENSION.md`, and the test totals from `README.md`. A pattern that stops matching is an error, not a silent blank.

The deliberate exemptions are listed at the top of `data.py`. They are EVM protocol constants, structural counts, the basic-set coverage fractions, per-suite test counts, and two illustrative values marked E.

## Verified failure modes

| Test | Result |
|---|---|
| A lock value edited (52,594 → 52,600) | `DATA DRIFT: 1 value(s) differ`, exit 1 |
| A committed SVG altered | `stale: sheets/BP-001.svg`, exit 1 |
| A result file removed (`freshness_k_probe.json`) | `DATA ERROR: missing result file`, exit 1 |
| Clean tree | `169 data values match … 0 differ`, exit 0 |

## Visible changes the binding made (6 sheets)

Each one replaces a rounded or hand-approximated figure with the file value.

| Sheet | Rev B | Rev C | Why |
|---|---|---|---|
| BP-102 | "spread 32×", "52,2xx–52,5xx" | 32.2×, 52,216–52,594 | computed from `gas_benchmark.json` |
| BP-103 | createVehicleDID … #25 | … #6 | 78,068 is a register #6 value |
| BP-301 | MOBI birth 14.13 ms | **17.69 ms** | see finding 1 |
| BP-302, BP-502 | 10.9 / 0.45 / 0.43 / 0.25 ms | 10.946 / 0.453 / 0.425 / 0.253 | file precision |
| BP-502 | SSI P*(0.5) 326, P*(1) 653, "≈600×" | **327, 654, ≈650×** | see finding 2 |
| BP-502 | second-host t_local ≈ 0.5 ms | 0.54 ms | `freshness_k_probe.json` |

## Findings for the author

1. **Register #33 and its file disagree.** `cv2x-testbed/results/lifecycle_parity.json` (commit `4f09875`) gives MOBI-VID-V2 birth a median of 17.69 ms and a lifecycle-event gas of 255,490. Register #33 cites 14.13 ms and 255,267, from code `8216507`. The file was re-run after the row was written. Either re-run and re-record, or update #33. BP-301 shows the file value and says the two differ.
2. **The rounding in Rev B was off by one.** P*(0.5) computed from the stored median 0.1528 ms is 327, not 326. The README's "≈600× margin" computes to ≈650× from the same number. Neither changes a conclusion. Both were artifacts of copying a rounded number and computing from it.
3. **The drift points listed in `AUDIT_REV_B.md` still stand.** They are the README and CAPABILITIES "90 failures", the stale `w3c_compliance.json`, and the header of register #26. This phase changes no file outside `docs/blueprints/` and the workflow.

## Workflow from now on

```bash
python3 docs/blueprints/make_blueprints.py            # regenerate SVGs
NODE_PATH=/opt/node-tools/node_modules node docs/blueprints/render_png.js
python3 docs/blueprints/make_blueprints.py --check    # what CI runs
# after a deliberate re-measurement changes a result file:
python3 docs/blueprints/make_blueprints.py --update-lock && python3 docs/blueprints/make_blueprints.py
```
