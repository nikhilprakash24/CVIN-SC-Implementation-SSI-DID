# Stamp Inventory — results of record

**Generated** by `docs/testing/check_stamps.py`. A stamp = date, commit, producing-code cleanliness, toolchain. Columns *code* and *any* are both "dirty" (True = not clean): *code* covers the producing code only (what a run of record requires, guide rule 1.1.6); *any* covers every file, so False there implies clean code and True says nothing. *inert*: the code flag's source at that commit could not detect a change (after-action report 11); such a stamp is vouched for by *any* or by the hand check in the claim register. Rows without a complete stamp carry a class: *stamp producer* (the work list), *history* (a diff of two runs, exempt), *single run* (not a result of record). *code changed since*: whether the producing code of the result's family differs between the stamped commit and HEAD (yes = the result describes code the trunk no longer has; re-run or disclose).

**Scope** (WM-2 step A1, N-21): 216 tracked result JSON files outside the lineage copies (docs/prior-survey/, docs/review02/, _research-copies/, sandbox/options/, docs/figures/). aggregated run directory: 64; covered by meta.json: 13; derived: 15; external tool output: 84; history: 2; own row: 38; uncovered: 0.

31 of 38 individually listed result files carry a complete stamp.

| File | date | commit | dirty (code) | dirty (any) | code changed since | toolchain | class |
|---|---|---|---|---|---|---|---|
| `4_comparison-framework/results/gas_benchmark.json` | 2026-10-22T23:16:49.669Z | ddb9b05 | False | True | no | 0.8.24 |  |
| `4_comparison-framework/results/gas_benchmark_stats.json` | 2026-10-22T23:16:47.548Z | ddb9b05 | False | True | no | 0.8.24 |  |
| `4_comparison-framework/results/gas_moved_by_defect_fixes_2026-10-04.json` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | history: a diff between two runs of record, each stamped or registered; not a measurement |
| `4_comparison-framework/results/gas_moved_by_defect_fixes_2026-10-04_pass06.json` | 2026-10-04 | a764387 (results of reco | MISSING | MISSING | MISSING | M1: solc 0.8.24, optimiz | history: same |
| `4_comparison-framework/results/gas_moved_by_merge_2026-10-06.json` | 2026-10-06 | MISSING | MISSING | MISSING | MISSING | M1: solc 0.8.24, optimiz | history: same |
| `4_comparison-framework/results/infrastructure_gas.json` | 2026-10-22T23:16:56.033Z | ddb9b05 | False | True | no | 0.8.24 |  |
| `4_comparison-framework/results/infrastructure_gas_run1.json` | 2026-10-09T06:08:42.697Z | f1f9e37 | False | True | yes | 0.8.24 |  |
| `4_comparison-framework/results/mobi_vid_backends.json` | 2026-10-22T23:16:51.402Z | ddb9b05 | False | True | no | 0.8.24 | hand check: AAR-11 R3: tree clean at 02:27:39 (gas_benchmark), outputs-only commit d54178e |
| `4_comparison-framework/results/pseudonym_pool.json` | 2026-10-22T23:17:03.801Z | ddb9b05 | False | True | no | 2.28.6 |  |
| `4_comparison-framework/results/scaling_lifetime.json` | 2026-10-22T23:16:54.582Z | ddb9b05 | False | True | no | 0.8.24 | hand check: same |
| `4_comparison-framework/results/scaling_marginal.json` | 2026-10-22T23:16:54.551Z | ddb9b05 | False | True | no | 0.8.24 | hand check: same |
| `4_comparison-framework/results/scaling_verify.json` | 2026-10-04T09:22:18+00:0 | d78e344a79705286bf7572a0 | False | False | yes | 3.11.15 |  |
| `4_comparison-framework/results/sensitivity.json` | 2026-07-24T03:18:28.250Z | MISSING | MISSING | MISSING | MISSING | 0.8.24 | stamp producer: no producer in the tree (optimizer sweep, July run); WM-2 A3 gap, pass 31 |
| `4_comparison-framework/results/w3c_compliance.json` | 2026-10-22T22:58:40.9497 | 205115991a560bd6d1b3dfb1 | False (inert) | MISSING | no | 3.13.16 |  |
| `4_comparison-framework/security-analysis/results/attack_results.json` | 2026-10-22T22:58:46.917Z | 2051159 | False | True | no | 0.8.24 |  |
| `4_comparison-framework/security-analysis/results/onchain_security.json` | 2026-10-22T22:58:43.977Z | 2051159 | False | True | no | 0.8.24 | hand check: same |
| `4_comparison-framework/security-analysis/results/security_matrix.json` | 2026-10-22T22:58:44Z | 205115991a560bd6d1b3dfb1 | False (inert) | MISSING | no | 3.13.16 |  |
| `cv2x-testbed/results/freshness_k.json` | 2026-10-04T09:24:10+00:0 | 8216507 | False (from any) | False | yes | 2.28.6 |  |
| `cv2x-testbed/results/freshness_k_probe.json` | 2026-10-04T22:12:41+00:0 | dd31d22 | False (from any) | False | yes | 3.11.15 |  |
| `cv2x-testbed/results/freshness_k_probe_fullref.json` | 2026-10-04T22:11:47+00:0 | f660402 | False (from any) | False | yes | 3.11.15 |  |
| `cv2x-testbed/results/freshness_k_probe_fullref_r2.json` | 2026-10-04T22:18:57+00:0 | 22a556f | False (from any) | False | yes | 3.11.15 |  |
| `cv2x-testbed/results/freshness_k_probe_r2.json` | 2026-10-04T22:18:19+00:0 | 439b118 | False (from any) | False | yes | 3.11.15 |  |
| `cv2x-testbed/results/freshness_k_samehost.json` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | derived: summary of the 12 stamped same-host replicates in freshness_k_samehost/ (#55, clone lineage #42); all_git_clean recorded |
| `cv2x-testbed/results/lifecycle_parity.json` | 2026-10-22T22:58:49+00:0 | 2051159 | False (inert) | True | no | 0.8.20+commit.a1b79de6 |  |
| `cv2x-testbed/results/pki_vs_erc1056.json` | 2026-10-22T23:58:19+00:0 | 0b39570 | False (from any) | False | no | 0.8.20+commit.a1b79de6 |  |
| `cv2x-testbed/sumo/results/infrastructure_revocation.json` | 2026-10-23T00:13:18+00:0 | 0b395705838af3554d0f33ea | False | True | no | 3.13.16 |  |
| `cv2x-testbed/sumo/results/infrastructure_stats.json` | 2026-10-23T00:07:06+00:0 | 0b395705838af3554d0f33ea | False | True | no | 3.13.16 |  |
| `cv2x-testbed/sumo/results/v2v_latency.json` | 2026-10-23T00:43:21.5170 | MISSING | MISSING | MISSING | MISSING | MISSING | single run: default output of one harness run; the results of record are v2v_latency_stats.json |
| `cv2x-testbed/sumo/results/v2v_latency_stats.json` | 2026-10-23T00:37:55+00:0 | 0b395705838af3554d0f33ea | False | True | no | 3.13.16 |  |
| `1_blockchain-identity/results/metrics/latest/meta.json` | 2026-10-21T03:29:00.049Z | a9e2a28066f7158dfc6d0a58 | False (from any) | False | yes | 0.8.24 |  |
| `1_blockchain-identity/results/metrics-rpc/latest/meta.json` | 2026-10-21T09:02:59.111Z | bd55af2a57db0b2aec373707 | False (from any) | False | yes | 0.8.24 |  |
| `5_zkp-agent-identity/results/attacks.json` | 2026-10-15T05:15:04+00:0 | 978988e | False | False | MISSING | 3.13.16 |  |
| `5_zkp-agent-identity/results/gas_zk.json` | 2026-10-15T05:15:13.814Z | 978988e | False | True | MISSING | 2.28.6 |  |
| `5_zkp-agent-identity/results/learning_curve.json` | MISSING | MISSING | MISSING | MISSING | MISSING | simulation, seeded; held | derived: written by attacks/train_responder.py; deterministic, reproduced byte for byte by bench/run_all.sh before each run of record (AAR 19) |
| `5_zkp-agent-identity/results/manual_burden.json` | 2026-10-15T05:32:58+00:0 | e780d40 | False | False | MISSING | 3.13.16 |  |
| `5_zkp-agent-identity/results/sigma_bench.json` | 2026-10-15T05:15:14+00:0 | 978988e | False | True | MISSING | 3.13.16 |  |
| `5_zkp-agent-identity/results/vin_bruteforce.json` | 2026-10-15T05:15:22+00:0 | 978988e | False | True | MISSING | 3.13.16 |  |
| `5_zkp-agent-identity/results/zkvin_bench.json` | 2026-10-15T05:15:11.485Z | 978988e | False | True | MISSING | v22.22.0 |  |

## Run directories (one row each)

| Files | What | runs | complete stamps | commits | dirty (code) | dirty (any) | code changed since |
|---|---|---|---|---|---|---|---|
| `4_comparison-framework/results/infrastructure_gas_runs/run_*.json` | I4 repeated 30 times (#47) | 30 | 30 | ddb9b05 | False | True | no |
| `4_comparison-framework/results/scaling_verify_repeats/*.json` | scaling-verify repeats (#26) | 16 | 8 | 38909df33fe1, d78e344a7970, f1c2399057f3, fd25d0529c6e | False (from any), None | False, None, True | None, yes |
| `cv2x-testbed/results/freshness_k_c3/c3_*.json` | WM-2 C3: #32 and #37 configurations on one host, 2 replicates each (#52) | 6 | 6 | 8216507, f660402 | False (from any) | False | yes |
| `cv2x-testbed/results/freshness_k_samehost/r*_full.json` | same-host freshness-k, full-refresh replicates (#55) | 6 | 6 | 3100e2a, 331d55c, 364ad1e, 9ede056, b151082, b3d3f65 | False (from any) | False | yes |
| `cv2x-testbed/results/freshness_k_samehost/r*_probe.json` | same-host freshness-k, probe-refresh replicates (#55) | 6 | 6 | 0cf6c3a, 676db30, 7a836dd, 7f41781, a7baac0, e3284ee | False (from any) | False | yes |

## Covered without an own stamp

| Files | Class | Why |
|---|---|---|
| `1_blockchain-identity/results/metrics/latest/*.json` | covered by meta.json | harness run of record; its meta.json carries the stamp |
| `1_blockchain-identity/results/metrics-rpc/latest/*.json` | covered by meta.json | HTTP-RPC run; its meta.json carries the stamp |
| `4_comparison-framework/results/infrastructure_gas_runs/summary.json` | derived | summary of the 30 stamped runs |
| `cv2x-testbed/sumo/results/figures/*.json` | derived | down-sampled trace for the dashboard |
| `cv2x-testbed/results/archive-2026-10-03/*.json` | history | archived pre-merge results |
| `cv2x-testbed/results/freshness_k_c3/manifest.json` | derived | order, commits and sha256 of the six C3 runs (report 19) |
| `cv2x-testbed/results/freshness_k_samehost/*.load.json` | derived | host-load log beside each stamped same-host replicate (#55) |
| `docs/conformance/reports/**/*.json` | external tool output | jest reports of the W3C DID test suite, dated by directory (#24) |
| `docs/conformance/reports/*.json` | external tool output | W3C DID test-suite run summaries, dated by file name (#24) |
