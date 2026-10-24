# Latency Charter (Class L)

**Generated** by `docs/testing/latency_charter.py`; do not edit. **Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-23 (WM-2 step B3, after-action report 35; guide rule 1.1.7).

## 1. The rule
A latency figure is compared only within one run or one host, carries N ≥ 30 per reported statistic, and names its host and library versions (in the register row or in the result file it cites). A row that fails a rule is quoted as **descriptive only**: its value may be reported, never compared with a value from another run or host.

| Class | Meaning |
|---|---|
| L-within | comparisons within one run or one host; N ≥ 30 per statistic; host and libraries recorded |
| L-absolute | an absolute value, no comparison; N ≥ 30; host and libraries recorded |
| L-descriptive | fails one rule (stated); quoted as descriptive only, never compared across hosts or runs |
| L-derived | computed from other rows; inherits their classes |

## 2. The register's latency rows (status V)

| Row | Class | N | Host recorded in | Why |
|---|---|---|---|---|
| #21 | L-within | n = 50 per operation | `cv2x-testbed/results/pki_vs_erc1056.json` | PKI and ERC-1056 timed in the same run of one script |
| #26 | L-descriptive | one sweep per density point | `4_comparison-framework/results/scaling_verify.json` | the V2V slope and P* come from one sweep per point with no replicate spread; host recorded |
| #27 | L-within | 30 seeded runs | `cv2x-testbed/sumo/results/v2v_latency_stats.json` | SSI and PKI verify in the same runs; bootstrap CI over run medians |
| #31 | L-descriptive | scale reads: N = 10 | `1_blockchain-identity/results/metrics/latest/meta.json` | the h = 50 figure is from the harness's scale reads (2 warm-up + 10) and the harness's meta.json records no CPU |
| #32 | L-within | n = 250 per k | `cv2x-testbed/results/freshness_k.json` | the k comparison is within one run; absolute ms are host-dependent (#52) |
| #33 | L-within | n = 50 per operation | `cv2x-testbed/results/lifecycle_parity.json` | centralized and MOBI timed in the same run; ratios are upper bounds (in-process baseline) |
| #36 | L-derived | from #29–#35 | — | one of its six criteria is R3 median ms after the lifecycle, from the harness (#31 class: descriptive) |
| #37 | L-within | n = 250 per k, 2 replicates | `cv2x-testbed/results/freshness_k_probe.json` | the probe-versus-full comparison is within each replicate; the knee is host-dependent (#52) |
| #39 | L-descriptive | N = 30 | `1_blockchain-identity/results/metrics-rpc/latest/meta.json` | comparisons are within one run and N = 30, but the harness's meta.json records no CPU |
| #44 | L-within | 30 runs | `cv2x-testbed/sumo/results/infrastructure_stats.json` | SPaT and BSM verified in the same runs (per-run ratio); stated deviation: no warm-up discard (amendment A5) |
| #48 | L-absolute | N = 30 runs | `cv2x-testbed/sumo/results/infrastructure_stats.json` | an absolute sum of four medians, not a path latency; stated deviation: no warm-up discard |
| #52 | L-within | n = 250 per k, 2 replicates each | `cv2x-testbed/results/freshness_k_c3/c3_r1_k32_full.json` | the two codes compared on one host, back to back, under a rule committed first |
| #55 | L-within | 12 replicates | `cv2x-testbed/results/freshness_k_samehost/r10_full.json` | both refresh modes on one host in alternating blocks; the summary file records no CPU, each of the 12 replicate files does |
| #57 | L-descriptive | prove N = 10; verify N = 30 | `5_zkp-agent-identity/results/zkvin_bench.json` | the proving time has N = 10; the verify time alone (N = 30) would be L-absolute |

14 rows classified: L-within 8, L-absolute 1, L-descriptive 4, L-derived 1. Every V row whose claim reports a latency (14) has a class; every L-within and L-absolute row's result file records its CPU (checked).

## 3. What follows
- **The harness records no host.** The metrics harness's `meta.json` names Node and the compiler but not the CPU, so its latency figures (#31, #39) are descriptive only. Its gas figures are unaffected (gas does not depend on the host). Recording the CPU in `meta.json` at the next harness run of record would move both rows to L-within (deferred item N-26).
- **Two deviations are stated, not hidden.** The infrastructure rows (#44, #48) discard no warm-up run, a deviation recorded in the pre-registration's amendment A5.
- **Short runs.** The ZK proving time (#57, N = 10) and the V2V scaling slope (#26, one sweep per point) are descriptive; their verify and gas parts are not affected.
