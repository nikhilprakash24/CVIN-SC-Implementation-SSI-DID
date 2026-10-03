#!/usr/bin/env python3
"""
Multi-run statistical driver for the V2V verification-latency benchmark
=======================================================================

Runs `sumo_identity_integration.py --simulate` N>=30 times with reproducible
seeds 1..N (each an INDEPENDENT subprocess: fresh interpreter, fresh crypto
state, fresh mock-mobility RNG seeded by --seed), captures the per-run
per-population per-metric MEDIAN latency, then aggregates ACROSS runs.

For each population (pki, ssi) and metric (sign, cold, warm) it reports, over
the N per-run medians:
    - run_medians : the N per-run median latencies (ms)
    - median      : across-run median of run_medians
    - mean        : across-run mean of run_medians
    - ci95        : 95% bootstrap percentile CI of the across-run MEDIAN
                    (10 000 resamples, fixed bootstrap seed for reproducibility)
    - p95         : 95th percentile of the N per-run median latencies

Totals (messages_sent / messages_verified / verification_failures) are summed
across all runs. The core measurement script is invoked unchanged; only its
existing --seed / --duration / --vehicles arguments are used.

Usage:
    python3.11 run_v2v_stats.py --runs 30 --duration 30 --vehicles 50
"""

import argparse
import json
import random
import statistics
import subprocess
import sys
import time
from pathlib import Path

SUMO_DIR = Path(__file__).resolve().parent
SCRIPT = SUMO_DIR / "sumo_identity_integration.py"
PER_RUN_JSON = SUMO_DIR / "results" / "v2v_latency.json"
DEFAULT_OUT = SUMO_DIR / "results" / "v2v_latency_stats.json"

POPULATIONS = ("pki", "ssi")
METRICS = (("sign", "sign_ms"), ("cold", "cold_ms"), ("warm", "warm_ms"))


def percentile(sorted_vals, p):
    """Nearest-rank 95th-percentile helper, matching the base script's pct()."""
    import math
    n = len(sorted_vals)
    if n == 0:
        return None
    idx = min(n - 1, max(0, math.ceil(p / 100.0 * n) - 1))
    return sorted_vals[idx]


def bootstrap_ci_of_median(values, n_boot=10000, rng=None, alpha=0.05):
    """Percentile bootstrap CI for the median of `values`."""
    if not values:
        return [None, None]
    if len(values) == 1:
        return [round(values[0], 6), round(values[0], 6)]
    rng = rng or random.Random(20260719)
    n = len(values)
    boot_medians = []
    for _ in range(n_boot):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        boot_medians.append(statistics.median(sample))
    boot_medians.sort()
    lo = percentile_linear(boot_medians, 100.0 * (alpha / 2.0))
    hi = percentile_linear(boot_medians, 100.0 * (1.0 - alpha / 2.0))
    return [round(lo, 6), round(hi, 6)]


def percentile_linear(sorted_vals, p):
    """Linear-interpolation percentile (for bootstrap CI endpoints)."""
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    rank = (p / 100.0) * (n - 1)
    lo_i = int(rank)
    hi_i = min(lo_i + 1, n - 1)
    frac = rank - lo_i
    return sorted_vals[lo_i] * (1.0 - frac) + sorted_vals[hi_i] * frac


def main():
    ap = argparse.ArgumentParser(description="Multi-run V2V latency statistics driver")
    ap.add_argument("--runs", type=int, default=30, help="number of runs (seeds 1..runs)")
    ap.add_argument("--duration", type=int, default=30, help="sim seconds per run")
    ap.add_argument("--vehicles", type=int, default=50, help="vehicles per run")
    ap.add_argument("--python", default=sys.executable, help="python interpreter for child runs")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="stats output path")
    ap.add_argument("--boot", type=int, default=10000, help="bootstrap resamples")
    ap.add_argument("--log-dir", default=None, help="per-run stdout log directory")
    args = ap.parse_args()

    seeds = list(range(1, args.runs + 1))
    log_dir = Path(args.log_dir) if args.log_dir else None
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)

    # per_run[pop][metric] = list of per-run medians (one entry per successful run)
    per_run = {pop: {m[0]: [] for m in METRICS} for pop in POPULATIONS}
    totals = {"messages_sent": 0, "messages_verified": 0, "verification_failures": 0}
    step_length_ms = None
    completed_seeds = []
    failed_runs = []

    wall0 = time.time()
    for seed in seeds:
        cmd = [args.python, str(SCRIPT), "--simulate",
               "--duration", str(args.duration),
               "--vehicles", str(args.vehicles),
               "--seed", str(seed)]
        proc = subprocess.run(cmd, cwd=str(SUMO_DIR),
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True)
        if log_dir:
            (log_dir / f"seed_{seed:03d}.log").write_text(proc.stdout)
        if proc.returncode != 0:
            failed_runs.append({"seed": seed, "reason": f"exit={proc.returncode}",
                                "tail": proc.stdout[-500:]})
            print(f"[seed {seed:2d}] FAILED exit={proc.returncode}")
            continue
        try:
            res = json.loads(PER_RUN_JSON.read_text())
        except Exception as e:  # noqa: BLE001
            failed_runs.append({"seed": seed, "reason": f"json:{e}"})
            print(f"[seed {seed:2d}] FAILED reading result json: {e}")
            continue

        step_length_ms = res.get("step_length_ms", step_length_ms)
        ok_this_run = True
        run_medians = {}
        for pop in POPULATIONS:
            block = res.get(pop, {})
            run_medians[pop] = {}
            for short, key in METRICS:
                stat = block.get(key)
                if not stat or stat.get("median_ms") is None:
                    ok_this_run = False
                    run_medians[pop][short] = None
                else:
                    run_medians[pop][short] = stat["median_ms"]
        if not ok_this_run:
            failed_runs.append({"seed": seed, "reason": "missing metric data"})
            print(f"[seed {seed:2d}] FAILED: missing metric data")
            continue

        for pop in POPULATIONS:
            for short, _ in METRICS:
                per_run[pop][short].append(run_medians[pop][short])
        totals["messages_sent"] += res.get("messages_sent", 0)
        totals["messages_verified"] += res.get("messages_verified", 0)
        totals["verification_failures"] += res.get("verification_failures", 0)
        completed_seeds.append(seed)
        print(f"[seed {seed:2d}] ok  "
              f"PKIwarm={run_medians['pki']['warm']:.4f}  "
              f"SSIwarm={run_medians['ssi']['warm']:.4f}  "
              f"sent={res.get('messages_sent')}  fail={res.get('verification_failures')}")

    # ---------------- Aggregate across runs ----------------
    boot_rng = random.Random(20260719)
    per_population = {}
    for pop in POPULATIONS:
        per_population[pop] = {}
        for short, _ in METRICS:
            vals = per_run[pop][short]
            svals = sorted(vals)
            block = {
                "run_medians": [round(v, 6) for v in vals],
                "median": round(statistics.median(vals), 6) if vals else None,
                "mean": round(statistics.fmean(vals), 6) if vals else None,
                "ci95": bootstrap_ci_of_median(vals, n_boot=args.boot, rng=boot_rng),
                "p95": round(percentile(svals, 95.0), 6) if vals else None,
            }
            per_population[pop][short] = block

    out = {
        "n_runs": len(completed_seeds),
        "seeds": completed_seeds,
        "runs_requested": args.runs,
        "failed_runs": failed_runs,
        "step_length_ms": step_length_ms,
        "sim_duration_s_per_run": args.duration,
        "vehicles_per_run": args.vehicles,
        "per_population": per_population,
        "totals": totals,
        "method": (
            "Each run is an independent subprocess of sumo_identity_integration.py "
            "--simulate (real ECDSA P-256 for PKI, real W3C VC + secp256k1 EIP-191 "
            "for SSI; latencies measured with time.perf_counter). Seeds 1..N seed "
            "Python's random.Random driving mock highway mobility. Per run we take "
            "the MEDIAN latency for each population/metric; across the N run-medians "
            "we report median, mean, a 95% CI of the median via percentile bootstrap "
            f"({args.boot} resamples, bootstrap seed 20260719, linearly interpolated "
            "2.5/97.5 endpoints), and p95 (nearest-rank 95th percentile of the N "
            "per-run medians). Totals are summed across all runs."
        ),
        "caveats": [
            "Mock vehicle mobility in --simulate mode (no SUMO binary); kinematics "
            "are a persistent 3-lane highway model, not calibrated traffic.",
            "No radio/network-stack latency: BSMs are delivered in-process, so there "
            "is no channel loss, MAC-layer contention, propagation, or queueing "
            "delay. Reported figures are pure identity-verification CPU time only.",
            "Single host, single process per run, no CPU pinning: absolute latencies "
            "are hardware-dependent (this machine) and reflect a warm, uncontended "
            "core; runs were executed serially to avoid inter-run CPU contention.",
            "verification_failures are exclusively the 3 injected attacks per run "
            "(tampered PKI BSM, tampered SSI BSM, uncredentialed SSI sender); the "
            "benign BSM flow produces zero failures.",
            "p95 here is the 95th percentile OF the per-run medians (across-run tail "
            "of the typical latency), not a pooled per-message p95.",
        ],
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))

    elapsed = time.time() - wall0
    print(f"\nCompleted {len(completed_seeds)}/{args.runs} runs in {elapsed:.0f}s "
          f"({len(failed_runs)} failed)")
    print(f"Stats written to {out_path}")
    if per_population["ssi"]["warm"]["median"] is not None:
        print(f"SSI warm: median={per_population['ssi']['warm']['median']:.4f} ms "
              f"ci95={per_population['ssi']['warm']['ci95']}")
        print(f"PKI warm: median={per_population['pki']['warm']['median']:.4f} ms "
              f"ci95={per_population['pki']['warm']['ci95']}")
    print(f"Totals: {totals}")


if __name__ == "__main__":
    main()
