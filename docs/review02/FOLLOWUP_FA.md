# Follow-up F-A: re-running register rows #26 (Exp. C/D) and #27 (DRAFT)

## Exp. C confirmation block (declared before it ran)

The run of record for Exp. C (repeat 1, `fd25d05`) has two anomalies: N=16/32 medians of
0.234/0.301 ms and a selective-disclosure k=1 median of 0.362 ms. The four back-to-back repeats
that followed (`scaling_verify_repeats/C_run2..5.json`) do not reproduce them. Those repeats were
decided on **after** seeing repeat 1. To avoid picking a run, this block is declared and committed
before it runs:

- **Runs:** 5 fresh repeats R6–R10 of
  `python3 4_comparison-framework/performance-metrics/run_verify_richness.py`. The parameters are
  the pre-registered defaults: N ∈ {1,2,4,8,16,32}, k ∈ {1,2,4,8,16} of 16, 300 warm runs per point
  after 50 warm-ups. They run back to back on a clean tree at the commit that adds this file.
- **Statistic:** per point, the median of the 5 repeat medians. The scaling order comes from the
  script's own `scaling_verdict()` applied to those medians.
- **Prediction (from `SCALING_EXPERIMENTS.md` and the July result):** verify is O(1) in N
  (spread < 1.25 and |relative slope| < 0.02). Selective disclosure grows linearly in k. Every p95
  is below 10 ms. Review 02 (PASS1_S §7) predicted about +6 % (+0.013 ms) per verify from the new
  checks.
- **Reporting:** R6–R10 are reported whether or not they agree with the prediction. Repeat 1 stays
  the committed `scaling_verify.json`, and the table generated from it is not replaced.
