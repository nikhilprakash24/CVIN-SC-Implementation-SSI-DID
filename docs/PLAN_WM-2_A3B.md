# WM-2 A3b on the One Trunk — Plan (Plan 5, phase 8)

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-22, before any run. **Binds:**
`docs/STYLE_AND_RIGOUR_GUIDE.md` (rules 1.1.4–1.1.7, 1.1.10), `docs/PLAN_WM-2.md` A3b.

**Gate (from WM-2):** `docs/testing/STAMP_INVENTORY.md` column "code changed since" reads `no` for every V row's result.
At the opening (trunk `38441a5`) 20 result files read `yes`, mostly because the three-lineage merge brought code
into their families. **Rule for each re-run:** one clean commit for the whole batch; one producer at a time with no
other load on the host; the output is compared with the committed file; an unchanged result is re-stamped only;
a moved one restates its register row with the old value as history. No re-roll: one run per producer, unless a
run is invalidated by a recorded cause (concurrent load, a crash), which is then disclosed.

## Batches (in order; each batch ends with a commit and the document checks)

| Batch | Producer (command of record) | Results | Rows | Kind |
|---|---|---|---|---|
| G1 | `npx hardhat run scripts/benchmark_gas.js`; `run_gas_stats.py --runs 30` | `gas_benchmark*.json` | #25 | gas, deterministic |
| G2 | `scripts/mobi_vid_backend_sweep.js` | `mobi_vid_backends.json` | H4 table | gas |
| G3 | `scripts/benchmark_scaling.js` | `scaling_lifetime.json`, `scaling_marginal.json` | #26 A/B | gas |
| G4 | `scripts/infrastructure_gas.js` (and its 30-run driver) | `infrastructure_gas*.json`, `infrastructure_gas_runs/` | #47 | gas, seeded |
| G5 | `scripts/experiment_pseudonym_pool.js` | `pseudonym_pool.json` | #38 | gas |
| L1 | `cv2x-testbed/scripts/experiment_pki_vs_erc1056.py --deploy` | `pki_vs_erc1056.*` | #21 | latency (host) |
| L2 | `cv2x-testbed/sumo/run_v2v_stats.py`; `run_verify_scaling.py`; `run_infra_stats.py` (+ `--revocation`) | `v2v_latency_stats`, `scaling_verify*`, `infrastructure_stats`, `infrastructure_revocation` | #26 C/D, #27, #44–#46, #48 | latency, M0 |
| L3 | `experiment_freshness_k.py --deploy` (#32 configuration) and `--refresh-mode {probe,full} --rotation` (#37, two replicates) | `freshness_k*.json` | #32, #37 (#40 history) | latency (host); compared within the run only, never with #52/#55 |
| H | `npm run metrics` (+ `metrics:analyze`) and the HTTP-RPC run | `results/metrics{,-rpc}/latest/` | #29–#31, #34–#36, #39, #49–#51, #54 | harness; also A6's one-line `dirtyMeasured` switch first |

## Not in scope
New experiments; changing any producer except A6's recorded one-line switch; the sensitivity sweep (no producer).
