#!/usr/bin/env python3
"""
Gas-benchmark reproducibility / determinism driver (Stage 0.8 rigor)
====================================================================

Unlike wall-clock latency, EVM gas is DETERMINISTIC: for a fixed contract,
fixed calldata, and fixed pre-state, `receipt.gasUsed` is exactly reproducible
run to run. The statistical question for the thesis is therefore not "what is
the noise band" but "are the single-run point estimates in gas_benchmark.json
stable, or could they be one-off flukes?"

This driver answers that empirically: it re-runs the full 9-standard gas
benchmark N times (each a fresh in-process Hardhat network) and aggregates
`gasUsed` per (standard, operation). If every run agrees to the gas, the
point estimates are exact and the CI width is zero — which is the expected
and desired result for deterministic gas, and is itself the reproducibility
evidence an examiner asks for.

Output: 4_comparison-framework/results/gas_benchmark_stats.json

Usage:
    python3 run_gas_stats.py --runs 30
"""

import argparse
import json
import os
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
HARDHAT_DIR = os.path.join(REPO, "1_blockchain-identity")
BENCH_JSON = os.path.join(REPO, "4_comparison-framework", "results",
                          "gas_benchmark.json")
STATS_JSON = os.path.join(REPO, "4_comparison-framework", "results",
                          "gas_benchmark_stats.json")


def one_run():
    """Run the benchmark once; return {standard: {op: gasUsed|None}}."""
    subprocess.run(
        ["npx", "hardhat", "run", "scripts/benchmark_gas.js"],
        cwd=HARDHAT_DIR, check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    with open(BENCH_JSON) as f:
        d = json.load(f)
    snap = {}
    for std, ops in d.items():
        if std == "metadata":
            continue
        snap[std] = {
            op: (v.get("gasUsed") if isinstance(v, dict) else None)
            for op, v in ops.items()
        }
    return snap, d.get("metadata", {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=30)
    args = ap.parse_args()
    n = max(2, args.runs)

    runs = []
    metadata = {}
    for i in range(n):
        snap, metadata = one_run()
        runs.append(snap)
        print(f"[run {i + 1}/{n}] ok")

    standards = list(runs[0].keys())
    per_standard = {}
    non_deterministic = []
    for std in standards:
        per_standard[std] = {}
        for op in runs[0][std]:
            vals = [r[std].get(op) for r in runs if r[std].get(op) is not None]
            if not vals:
                per_standard[std][op] = {"n": 0, "gasUsed": None,
                                         "note": "not supported by this standard"}
                continue
            lo, hi = min(vals), max(vals)
            deterministic = (lo == hi)
            if not deterministic:
                non_deterministic.append(f"{std}.{op} [{lo}, {hi}]")
            per_standard[std][op] = {
                "n": len(vals),
                "median": statistics.median(vals),
                "min": lo,
                "max": hi,
                "stdev": statistics.pstdev(vals) if len(vals) > 1 else 0.0,
                "deterministic": deterministic,
                # For deterministic gas the 95% CI collapses to the point value;
                # if any variance appears it is calldata/state-ordering driven
                # and the [min,max] envelope bounds it.
                "ci95": [lo, hi],
            }

    all_deterministic = len(non_deterministic) == 0
    out = {
        "n_runs": n,
        "all_deterministic": all_deterministic,
        "non_deterministic_cells": non_deterministic,
        "method": (
            "Full 9-standard gas benchmark re-run N times on a fresh "
            "in-process Hardhat network each time; gasUsed aggregated per "
            "(standard, operation). EVM gas is deterministic for fixed "
            "calldata + pre-state, so identical values across runs (CI "
            "width 0) is the expected, correct reproducibility result."
        ),
        "source_metadata": metadata,
        "per_standard": per_standard,
    }
    with open(STATS_JSON, "w") as f:
        json.dump(out, f, indent=2)

    print(f"\nN={n} runs. all_deterministic={all_deterministic}")
    if non_deterministic:
        print("Non-deterministic cells (calldata/state variance):")
        for c in non_deterministic:
            print(f"  - {c}")
    else:
        print("Every operation returned byte-identical gasUsed across all "
              f"{n} runs — point estimates in gas_benchmark.json are exact.")
    print(f"Stats written to {STATS_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
