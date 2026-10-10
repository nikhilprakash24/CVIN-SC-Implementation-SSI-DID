# Stamp Inventory — results of record

**Generated** by `docs/testing/check_stamps.py`. A stamp = date, commit, producing-code cleanliness, toolchain. Columns *code* and *any* are both "dirty" (True = not clean): *code* covers the producing code only (what a run of record requires, guide rule 1.1.6); *any* covers every file, so False there implies clean code and True says nothing. *inert*: the code flag's source at that commit could not detect a change (after-action report 11); such a stamp is vouched for by *any* or by the hand check in the claim register. Rows without a complete stamp carry a class: *stamp producer* (the work list), *history* (a diff of two runs, exempt), *single run* (not a result of record). *code changed since*: whether the producing code of the result's family differs between the stamped commit and HEAD (yes = the result describes code the trunk no longer has; re-run or disclose).

20 of 29 result files carry a complete stamp.

| File | date | commit | dirty (code) | dirty (any) | code changed since | toolchain | class |
|---|---|---|---|---|---|---|---|
| `4_comparison-framework/results/gas_benchmark.json` | 2026-10-09T02:27:39.007Z | d0cc19c | False (from any) | False | no | 0.8.24 |  |
| `4_comparison-framework/results/gas_benchmark_stats.json` | 2026-10-06T04:53:48.231Z | MISSING | MISSING | MISSING | MISSING | 0.8.24 | stamp producer: 4_comparison-framework/performance-metrics/run_gas_stats.py |
| `4_comparison-framework/results/gas_moved_by_defect_fixes_2026-10-04.json` | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | history: a diff between two runs of record, each stamped or registered; not a measurement |
| `4_comparison-framework/results/gas_moved_by_defect_fixes_2026-10-04_pass06.json` | 2026-10-04 | a764387 (results of reco | MISSING | MISSING | yes | M1: solc 0.8.24, optimiz | history: same |
| `4_comparison-framework/results/gas_moved_by_merge_2026-10-06.json` | 2026-10-06 | MISSING | MISSING | MISSING | MISSING | M1: solc 0.8.24, optimiz | history: same |
| `4_comparison-framework/results/infrastructure_gas.json` | 2026-10-09T06:08:44.765Z | f1f9e37 | False | True | no | 0.8.24 |  |
| `4_comparison-framework/results/infrastructure_gas_run1.json` | 2026-10-09T06:08:42.697Z | f1f9e37 | False | True | no | 0.8.24 |  |
| `4_comparison-framework/results/mobi_vid_backends.json` | 2026-10-09T02:27:44.231Z | d0cc19c | False (hand check) | True | no | 0.8.24 | hand check: AAR-11 R3: tree clean at 02:27:39 (gas_benchmark), outputs-only commit d54178e |
| `4_comparison-framework/results/pseudonym_pool.json` | 2026-10-04T22:17:54.329Z | e49bcb4 | False (from any) | False | yes | 2.28.6 |  |
| `4_comparison-framework/results/scaling_lifetime.json` | 2026-10-09T02:27:41.957Z | d0cc19c | False (hand check) | True | no | 0.8.24 | hand check: same |
| `4_comparison-framework/results/scaling_marginal.json` | 2026-10-09T02:27:41.933Z | d0cc19c | False (hand check) | True | no | 0.8.24 | hand check: same |
| `4_comparison-framework/results/scaling_verify.json` | 2026-10-04T09:22:18+00:0 | d78e344a79705286bf7572a0 | False (from any) | False | yes | 3.11.15 |  |
| `4_comparison-framework/results/sensitivity.json` | 2026-07-24T03:18:28.250Z | MISSING | MISSING | MISSING | MISSING | 0.8.24 | stamp producer: 1_blockchain-identity/scripts/benchmark_scaling.js (July run; re-run due) |
| `4_comparison-framework/results/w3c_compliance.json` | 2026-10-04T22:26:35.2592 | MISSING | MISSING | MISSING | MISSING | MISSING | stamp producer: cv2x-testbed/scripts/w3c_compliance_checker.py |
| `4_comparison-framework/security-analysis/results/attack_results.json` | 2026-07-19T21:10:16.411Z | MISSING | MISSING | MISSING | MISSING | 0.8.24 | stamp producer: 1_blockchain-identity/test/L2-identity-system/security/attackHarness.js |
| `4_comparison-framework/security-analysis/results/onchain_security.json` | 2026-10-09T02:27:46.849Z | d0cc19c | False (hand check) | True | no | 0.8.24 | hand check: same |
| `4_comparison-framework/security-analysis/results/security_matrix.json` | 2026-10-06T04:26:37Z | MISSING | MISSING | MISSING | MISSING | MISSING | stamp producer: 4_comparison-framework/security-analysis/attack_scenarios.py |
| `cv2x-testbed/results/freshness_k.json` | 2026-10-04T09:24:10+00:0 | 8216507 | False (from any) | False | yes | 2.28.6 |  |
| `cv2x-testbed/results/freshness_k_probe.json` | 2026-10-04T22:12:41+00:0 | dd31d22 | False (from any) | False | yes | 3.11.15 |  |
| `cv2x-testbed/results/freshness_k_probe_fullref.json` | 2026-10-04T22:11:47+00:0 | f660402 | False (from any) | False | yes | 3.11.15 |  |
| `cv2x-testbed/results/freshness_k_probe_fullref_r2.json` | 2026-10-04T22:18:57+00:0 | 22a556f | False (from any) | False | yes | 3.11.15 |  |
| `cv2x-testbed/results/freshness_k_probe_r2.json` | 2026-10-04T22:18:19+00:0 | 439b118 | False (from any) | False | yes | 3.11.15 |  |
| `cv2x-testbed/results/lifecycle_parity.json` | 2026-10-04T22:17:02+00:0 | 4f09875 | False (from any) | False | yes | 3.11.15 |  |
| `cv2x-testbed/results/pki_vs_erc1056.json` | 2026-10-04T05:26:56+00:0 | 1c1b8e1 | False (from any) | False | yes | 2.28.6 |  |
| `cv2x-testbed/sumo/results/infrastructure_revocation.json` | 2026-10-09T05:38:02+00:0 | f1f9e37cc516b318892dd124 | False | True | no | 3.11.15 |  |
| `cv2x-testbed/sumo/results/infrastructure_stats.json` | 2026-10-09T05:30:59+00:0 | f1f9e37cc516b318892dd124 | False | False | no | 3.11.15 |  |
| `cv2x-testbed/sumo/results/v2v_latency.json` | 2026-10-04T09:19:33.3911 | MISSING | MISSING | MISSING | MISSING | MISSING | single run: default output of one harness run; the results of record are v2v_latency_stats.json |
| `cv2x-testbed/sumo/results/v2v_latency_stats.json` | 2026-10-04T09:13:58+00:0 | 58a65132bf38c37e0f0467b3 | False (from any) | False | yes | 3.11.15 |  |
| `1_blockchain-identity/results/metrics/latest/meta.json` | 2026-10-09T02:09:37.654Z | 7a9a996edb246661f32a5565 | False (from any) | False | no | 0.8.24 |  |
