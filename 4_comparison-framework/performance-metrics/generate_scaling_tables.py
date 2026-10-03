#!/usr/bin/env python3
"""
generate_scaling_tables.py

Table/figure generator for the §5.9 Scaling & Lifetime Cost sub-section
(design: docs/SCALING_EXPERIMENTS.md; addresses RESEARCH_AUDIT.md §4.8). Emits
thesis-ready CSV + LaTeX (booktabs) tables, plus PNG figures when matplotlib is
importable, into ../results/ for each experiment whose JSON input is present:

  Experiment A (marginal-cost stationarity) -- ../results/scaling_marginal.json:
    ../results/scaling_marginal.csv           - slope table (per standard)
    ../results/scaling_marginal.tex           - LaTeX booktabs tabular
    ../results/scaling_marginal.png           - gasUsed vs op index (if matplotlib)

  Experiment B (lifetime cost MODEL) -- ../results/scaling_lifetime.json:
    ../results/scaling_lifetime.csv           - lifetime-gas table (ranked)
    ../results/scaling_lifetime.tex           - LaTeX booktabs tabular
    ../results/scaling_lifetime.png           - stacked lifetime bars (if matplotlib)

  Experiment C (verification latency vs credential richness) -- scaling_verify.json:
    ../results/scaling_verify_richness.csv    - latency vs N claims (+ SD vs k)
    ../results/scaling_verify_richness.tex    - LaTeX booktabs tabular
    ../results/scaling_verify_richness.png    - line plot (if matplotlib present)

  Experiment D (V2V verification saturation vs neighbor density) -- scaling_verify.json:
    ../results/scaling_verify_density.csv     - per-interval time vs P
    ../results/scaling_verify_density.tex     - LaTeX booktabs tabular
    ../results/scaling_verify_density.png     - line plot with 100 ms budget

Inputs A/B come from 1_blockchain-identity/scripts/benchmark_scaling.js; inputs
C/D come from the verification drivers. Each experiment is generated independently
and skipped (with a note) when its input JSON is absent.

Usage:
  python3 generate_scaling_tables.py                       (uses default result paths)
  python3 generate_scaling_tables.py [path/to/scaling_verify.json]
"""

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS_DIR = HERE.parent / "results"
DEFAULT_INPUT = RESULTS_DIR / "scaling_verify.json"
DEFAULT_MARGINAL = RESULTS_DIR / "scaling_marginal.json"
DEFAULT_LIFETIME = RESULTS_DIR / "scaling_lifetime.json"

# Stable presentation order for Experiment A.
STD_ORDER = ["ERC-1056", "ERC-735", "ERC-1155", "CVIN-Combined", "MOBI-VID-V2"]

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAVE_MPL = True
except Exception:
    HAVE_MPL = False


def tex_escape(s: str) -> str:
    repl = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
            "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}"}
    return "".join(repl.get(c, c) for c in str(s))


def fmt_date(iso: str) -> str:
    try:
        return (datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
                .astimezone(timezone.utc).strftime("%Y-%m-%d"))
    except (ValueError, AttributeError):
        return iso or "n/a"


def ordered_standards(std_dict):
    """Yield (name, value) in STD_ORDER, then any extras."""
    seen = set()
    for name in STD_ORDER:
        if name in std_dict:
            seen.add(name)
            yield name, std_dict[name]
    for name, value in std_dict.items():
        if name not in seen:
            yield name, value


# ---------------------------------------------------------------------------
# Experiment A — marginal-cost stationarity (slope table)
# ---------------------------------------------------------------------------

def write_marginal_csv(marginal, out_path):
    meta = marginal["metadata"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["# Experiment A: marginal-cost stationarity "
                    "(gasUsed of K sequential same-type appends)"])
        w.writerow(["standard", "append_op", "first_op_gas", "op50_gas",
                    "delta_gas", "slope_gas_per_op", "r2", "constant_O1"])
        for name, s in ordered_standards(marginal["standards"]):
            w.writerow([name, s["op"], s["first"], s["last"], s["delta"],
                        round(s["slope"], 3), round(s["r2"], 4),
                        "yes" if s["constantMarginalCost"] else "no"])
        w.writerow([])
        w.writerow(["# Conditions",
                    f"K={meta.get('K','?')} appends/standard on a fresh chain",
                    f"solc {meta.get('solcVersion','?')} (optimizer 200, viaIR)",
                    f"OZ {meta.get('ozVersion','?')}",
                    f"chainId {meta.get('chainId','?')}",
                    f"measured {fmt_date(meta.get('date',''))}"])
        w.writerow(["# Legend",
                    "gasUsed = exact receipt.gasUsed; slope/R^2 are exact "
                    "least-squares fits vs op index. O(1)=yes means marginal "
                    "append cost does not grow with history (a negative slope is "
                    "a one-off cold-slot first write, amortized thereafter)."])
    print(f"Wrote {out_path}")


def write_marginal_tex(marginal, out_path):
    meta = marginal["metadata"]
    date_h = fmt_date(meta.get("date", ""))
    caption = (
        "Experiment A --- marginal-cost stationarity. On a fresh deployment of "
        f"each standard, $K={meta.get('K', 50)}$ sequential same-type "
        "append-to-history operations were executed with a fixed-size payload "
        "and a fixed actor; \\texttt{gasUsed} was recorded for every operation "
        "index. Columns give the first-operation gas, the "
        "$50$\\textsuperscript{th}-operation gas, their difference $\\Delta$, the "
        "exact least-squares slope (gas per operation) and $R^2$ of "
        "\\texttt{gasUsed} versus index, and whether the marginal cost is "
        "constant ($O(1)$). A slightly negative slope is a one-off cold-storage "
        "first write (each counter/length slot pays $\\approx$\\,$17{,}100$ gas "
        "once, then is warm) and is amortized away --- cost does not grow with "
        "history. "
        f"Local Hardhat network (chain id {meta.get('chainId', 31337)}), "
        f"Solidity {meta.get('solcVersion', '?')} (optimizer, 200 runs, via-IR), "
        f"OpenZeppelin {meta.get('ozVersion', '?')}, {date_h}."
    )
    lines = [
        "% Auto-generated by generate_scaling_tables.py -- do not edit by hand.",
        "% Requires \\usepackage{booktabs}.",
        "\\begin{table}[htbp]",
        "  \\centering",
        f"  \\caption{{{caption}}}",
        "  \\label{tab:scaling-marginal}",
        "  \\footnotesize",
        "  \\setlength{\\tabcolsep}{5pt}",
        "  \\resizebox{\\textwidth}{!}{%",
        "  \\begin{tabular}{llrrrrrc}",
        "    \\toprule",
        "    Standard & Append op & First-op & $50$th-op & $\\Delta$ & "
        "Slope (gas/op) & $R^2$ & $O(1)$? \\\\",
        "    \\midrule",
    ]
    for name, s in ordered_standards(marginal["standards"]):
        o1 = "yes" if s["constantMarginalCost"] else "\\textbf{no}"
        lines.append(
            f"    {tex_escape(name)} & \\texttt{{{tex_escape(s['op'])}}} & "
            f"{s['first']:,} & {s['last']:,} & {s['delta']:,} & "
            f"{s['slope']:.2f} & {s['r2']:.4f} & {o1} \\\\")
    lines += ["    \\bottomrule", "  \\end{tabular}}", "\\end{table}", ""]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path}")


def plot_marginal(marginal, out_path):
    if not HAVE_MPL:
        print("matplotlib not available - skipped marginal PNG")
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    markers = ["o", "s", "^", "D", "v"]
    for i, (name, s) in enumerate(ordered_standards(marginal["standards"])):
        xs = list(range(1, len(s["gas"]) + 1))
        ax.plot(xs, s["gas"], marker=markers[i % len(markers)], markersize=3,
                linewidth=1.2,
                label=f"{name} ({s['op']}), slope={s['slope']:.1f} gas/op")
    ax.set_xlabel("operation index $i$ (sequential appends)")
    ax.set_ylabel("gasUsed")
    ax.set_ylim(bottom=0)
    ax.set_title("Experiment A: marginal append cost vs history depth "
                 "(flat = O(1))")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, loc="center right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Wrote {out_path}")


# ---------------------------------------------------------------------------
# Experiment B — lifetime cost model (lifetime table)
# ---------------------------------------------------------------------------

def write_lifetime_csv(lifetime, out_path):
    meta = lifetime["metadata"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["# Experiment B: lifetime cost MODEL over an assumed "
                    "39-event profile (not a measurement)"])
        w.writerow(["rank", "standard", "append_op", "birth_x1_gas",
                    "appends_x35_gas", "transfers_x3_gas", "lifetime_total_gas",
                    "band_minus50pct_gas", "band_plus50pct_gas"])
        for idx, r in enumerate(lifetime["ranking"], 1):
            name = r["name"]
            s = lifetime["standards"][name]
            d = s["decomposition"]
            w.writerow([idx, name, s["appendOp"], d["birth"]["subtotalGas"],
                        d["appends"]["subtotalGas"], d["transfers"]["subtotalGas"],
                        s["totalLifetimeGas"], s["sensitivityBand"]["low"],
                        s["sensitivityBand"]["high"]])
        w.writerow([])
        prof = meta.get("profile", {})
        w.writerow(["# Profile (assumed)", f"birth={prof.get('birth')}",
                    f"maintenance={prof.get('maintenance')}",
                    f"inspection={prof.get('inspection')}",
                    f"recall={prof.get('recall')}",
                    f"transfer={prof.get('transfer')}",
                    f"total_events={meta.get('profileTotalEvents')}"])
        w.writerow(["# Model",
                    "MODEL over an ASSUMED profile. Lifetime = birth"
                    "(createIdentity) + 35 x steady-state append marginal (Exp A) "
                    "+ 3 x transferOwnership. Band = +/-50% recurring event "
                    "frequency (birth fixed). Gas is relative on-chain work, not "
                    "fiat."])
    print(f"Wrote {out_path}")


def write_lifetime_tex(lifetime, out_path):
    meta = lifetime["metadata"]
    date_h = fmt_date(meta.get("date", ""))
    prof = meta.get("profile", {})
    caption = (
        "Experiment B --- lifetime cost \\textbf{model} (an assumption, not a "
        "measurement). Total on-chain gas to carry one vehicle identity through "
        "the canonical 15-year profile "
        f"({prof.get('birth',1)} birth, {prof.get('maintenance',30)} "
        f"maintenance, {prof.get('inspection',4)} inspections, "
        f"{prof.get('recall',1)} recall, {prof.get('transfer',3)} transfers "
        f"$= {meta.get('profileTotalEvents',39)}$ events), decomposed by event "
        "class. Birth uses each standard's identity-creation cost and transfers "
        "its ownership-transfer cost (\\texttt{gas\\_benchmark.json}); the "
        "recurring maintenance/inspection/recall events use the Experiment~A "
        "steady-state append marginal. Rows are ranked by total (cheapest "
        "first). The last two columns give the $\\pm 50\\%$ event-frequency "
        "sensitivity band (birth fixed). Gas is relative on-chain work, not "
        "fiat. "
        f"Solidity {meta.get('solcVersion', '?')} (optimizer, 200 runs, via-IR), "
        f"OpenZeppelin {meta.get('ozVersion', '?')}, chain id "
        f"{meta.get('chainId', 31337)}, {date_h}."
    )
    lines = [
        "% Auto-generated by generate_scaling_tables.py -- do not edit by hand.",
        "% Requires \\usepackage{booktabs}.",
        "\\begin{table}[htbp]",
        "  \\centering",
        f"  \\caption{{{caption}}}",
        "  \\label{tab:scaling-lifetime}",
        "  \\footnotesize",
        "  \\setlength{\\tabcolsep}{5pt}",
        "  \\resizebox{\\textwidth}{!}{%",
        "  \\begin{tabular}{llrrrrrr}",
        "    \\toprule",
        "    Rank & Standard & Birth ($\\times1$) & Appends ($\\times35$) & "
        "Transfers ($\\times3$) & \\textbf{Lifetime total} & $-50\\%$ & "
        "$+50\\%$ \\\\",
        "    \\midrule",
    ]
    for idx, r in enumerate(lifetime["ranking"], 1):
        name = r["name"]
        s = lifetime["standards"][name]
        d = s["decomposition"]
        lines.append(
            f"    {idx} & {tex_escape(name)} & "
            f"{d['birth']['subtotalGas']:,} & {d['appends']['subtotalGas']:,} & "
            f"{d['transfers']['subtotalGas']:,} & "
            f"\\textbf{{{s['totalLifetimeGas']:,}}} & "
            f"{s['sensitivityBand']['low']:,} & {s['sensitivityBand']['high']:,} "
            "\\\\")
    lines += ["    \\bottomrule", "  \\end{tabular}}", "\\end{table}", ""]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path}")


def plot_lifetime(lifetime, out_path):
    if not HAVE_MPL:
        print("matplotlib not available - skipped lifetime PNG")
        return
    ranking = lifetime["ranking"]
    names = [r["name"] for r in ranking]
    st = lifetime["standards"]
    births = [st[n]["decomposition"]["birth"]["subtotalGas"] for n in names]
    appends = [st[n]["decomposition"]["appends"]["subtotalGas"] for n in names]
    transfers = [st[n]["decomposition"]["transfers"]["subtotalGas"] for n in names]
    totals = [st[n]["totalLifetimeGas"] for n in names]
    lows = [st[n]["sensitivityBand"]["low"] for n in names]
    highs = [st[n]["sensitivityBand"]["high"] for n in names]

    x = list(range(len(names)))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x, births, label="Birth ($\\times1$)", color="#4C72B0")
    ax.bar(x, appends, bottom=births, label="Appends ($\\times35$)",
           color="#DD8452")
    base2 = [b + a for b, a in zip(births, appends)]
    ax.bar(x, transfers, bottom=base2, label="Transfers ($\\times3$)",
           color="#55A868")
    yerr = [[t - lo for t, lo in zip(totals, lows)],
            [hi - t for t, hi in zip(totals, highs)]]
    ax.errorbar(x, totals, yerr=yerr, fmt="none", ecolor="black", capsize=4,
                linewidth=1.2, label="$\\pm50\\%$ event-frequency band")
    for xi, t in zip(x, totals):
        ax.annotate(f"{t:,}", (xi, t), textcoords="offset points",
                    xytext=(0, 6), ha="center", fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=20, ha="right", fontsize=8)
    ax.set_ylabel("lifetime gas (39-event profile)")
    ax.set_title("Experiment B: modeled 15-year lifetime cost per standard "
                 "(MODEL, not fiat)")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Wrote {out_path}")


# ---------------------------------------------------------------------------
# Experiment C — credential richness + selective disclosure
# ---------------------------------------------------------------------------

def write_richness_csv(rich, sd, out_path):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["# Experiment C: VC verification latency vs credential richness"])
        w.writerow(["N_claims", "median_ms", "p95_ms", "mean_ms"])
        for N, med, p95, mean in zip(rich["N"], rich["median_ms"],
                                     rich["p95_ms"], rich["mean_ms"]):
            w.writerow([N, med, p95, mean])
        w.writerow([])
        w.writerow([f"# Selective disclosure (N={sd['N']}): latency vs disclosed k"])
        w.writerow(["k_disclosed", "median_ms", "p95_ms", "mean_ms"])
        for k, med, p95, mean in zip(sd["k"], sd["median_ms"],
                                     sd["p95_ms"], sd["mean_ms"]):
            w.writerow([k, med, p95, mean])
        w.writerow([])
        sc = rich["scaling"]
        w.writerow(["# richness scaling order", sc["order"]])
        w.writerow(["# richness fit", f"median_ms = {sc['intercept_ms']} "
                    f"+ {sc['slope_ms_per_unit']}*N  (R^2={sc['r2']})"])
        w.writerow(["# sig-check target ms", rich["sig_check_target_ms"]])
        w.writerow(["# p95 under target across range",
                    rich["stays_under_target_across_range"]])
    print(f"Wrote {out_path}")


def write_richness_tex(rich, sd, out_path):
    sc = rich["scaling"]
    target = rich["sig_check_target_ms"]
    caption = (
        "Experiment C: real W3C Verifiable Credential verification latency vs "
        "credential richness. Left: full verification of a credential carrying "
        "$N$ claims. Right: selective disclosure of $k$ of $N=" f"{sd['N']}" "$ "
        "salted claim digests. Each cell is the median over "
        f"{rich['runs_per_point']} warm runs (p95 in parentheses), real "
        "secp256k1 EIP-191 recovery, single host (repeatability framing, thesis "
        f"\\S5.4). Verification is {tex_escape(sc['order'])} in $N$ and remains "
        f"far below the {target:.0f}\\,ms signature-check target across the "
        "whole range."
    )
    lines = [
        "% Auto-generated by generate_scaling_tables.py -- do not edit by hand.",
        "% Requires \\usepackage{booktabs}.",
        "\\begin{table}[htbp]",
        "  \\centering",
        f"  \\caption{{{caption}}}",
        "  \\label{tab:scaling-verify-richness}",
        "  \\footnotesize",
        "  \\begin{tabular}{rr@{\\hskip 2em}rr}",
        "    \\toprule",
        "    \\multicolumn{2}{c}{Credential richness} & "
        "\\multicolumn{2}{c}{Selective disclosure ($N=" f"{sd['N']}" "$)} \\\\",
        "    \\cmidrule(r){1-2}\\cmidrule(l){3-4}",
        "    $N$ claims & median (p95) ms & $k$ disclosed & median (p95) ms \\\\",
        "    \\midrule",
    ]
    rows_left = list(zip(rich["N"], rich["median_ms"], rich["p95_ms"]))
    rows_right = list(zip(sd["k"], sd["median_ms"], sd["p95_ms"]))
    nrows = max(len(rows_left), len(rows_right))
    for i in range(nrows):
        if i < len(rows_left):
            N, med, p95 = rows_left[i]
            left = f"{N} & {med:.4f} ({p95:.4f})"
        else:
            left = " & "
        if i < len(rows_right):
            k, med, p95 = rows_right[i]
            right = f"{k} & {med:.4f} ({p95:.4f})"
        else:
            right = " & "
        lines.append(f"    {left} & {right} \\\\")
    lines += [
        "    \\bottomrule",
        "  \\end{tabular}",
        "\\end{table}",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path}")


def plot_richness(rich, sd, out_path):
    if not HAVE_MPL:
        print("matplotlib not available - skipped richness PNG")
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.6))
    ax1.plot(rich["N"], rich["median_ms"], "o-", color="#1f77b4",
             label="median")
    ax1.plot(rich["N"], rich["p95_ms"], "s--", color="#7fb0d8", label="p95",
             linewidth=1)
    ax1.set_xscale("log", base=2)
    ax1.set_xticks(rich["N"])
    ax1.set_xticklabels(rich["N"])
    ax1.set_xlabel("credential richness $N$ (claims)")
    ax1.set_ylabel("verification latency (ms)")
    ax1.set_title("(a) latency vs richness")
    ax1.set_ylim(bottom=0)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=8)

    ax2.plot(sd["k"], sd["median_ms"], "o-", color="#d62728", label="median")
    ax2.plot(sd["k"], sd["p95_ms"], "s--", color="#e58a8b", label="p95",
             linewidth=1)
    ax2.set_xscale("log", base=2)
    ax2.set_xticks(sd["k"])
    ax2.set_xticklabels(sd["k"])
    ax2.set_xlabel(f"disclosed claims $k$ (of $N={sd['N']}$)")
    ax2.set_ylabel("verification latency (ms)")
    ax2.set_title("(b) selective disclosure")
    ax2.set_ylim(bottom=0)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=8)

    fig.suptitle("Experiment C — VC verification latency vs credential richness "
                 f"(\\ll {rich['sig_check_target_ms']:.0f} ms target)"
                 .replace("\\ll", "«"), fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Wrote {out_path}")


# ---------------------------------------------------------------------------
# Experiment D — V2V verification saturation vs neighbor density
# ---------------------------------------------------------------------------

def write_density_csv(dens, out_path):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["# Experiment D: V2V per-interval verification time vs "
                    "neighbor density"])
        w.writerow(["P_neighbors", "per_interval_median_ms", "per_interval_p95_ms",
                    "per_message_median_ms", "pct_of_100ms_budget"])
        for P, med, p95, pm in zip(dens["P"], dens["per_interval_ms"],
                                   dens["per_interval_p95_ms"],
                                   dens["per_message_median_ms"]):
            w.writerow([P, med, p95, pm,
                        f"{100.0 * med / dens['budget_ms']:.2f}"])
        w.writerow([])
        fit = dens["fit"]
        w.writerow(["# budget ms", dens["budget_ms"]])
        w.writerow(["# saturation_P within range", dens["saturation_P"]])
        w.writerow(["# extrapolated saturation P*",
                    dens["extrapolated_saturation_P"]])
        w.writerow(["# fit", f"per_interval_ms = {fit['intercept_ms']} "
                    f"+ {fit['slope_ms_per_neighbor']}*P  (R^2={fit['r2']})"])
    print(f"Wrote {out_path}")


def write_density_tex(dens, out_path):
    fit = dens["fit"]
    budget = dens["budget_ms"]
    if dens["saturation_P"] is not None:
        sat = f"$P^*={dens['saturation_P']}$ neighbors (within the tested range)"
    else:
        sat = (f"beyond the tested range ($P\\le 80$); extrapolated "
               f"$P^*\\approx{dens['extrapolated_saturation_P']:.0f}$ neighbors")
    caption = (
        "Experiment D: per-vehicle per-interval V2V verification time vs neighbor "
        "density $P$ (the dense-intersection case). Each vehicle verifies $P$ "
        "cached neighbours per 10\\,Hz BSM interval; the median over "
        f"{dens['intervals_per_point']} warm 100\\,ms intervals is reported. "
        "Verification time is linear in $P$ "
        f"($\\approx{fit['slope_ms_per_neighbor']:.4f}$\\,ms/neighbour, "
        f"$R^2={fit['r2']:.4f}$). The saturation point is {sat}. "
        f"Crypto verification load only, excluding radio/MAC "
        "(RESEARCH\\_AUDIT \\S4.4)."
    )
    lines = [
        "% Auto-generated by generate_scaling_tables.py -- do not edit by hand.",
        "% Requires \\usepackage{booktabs}.",
        "\\begin{table}[htbp]",
        "  \\centering",
        f"  \\caption{{{caption}}}",
        "  \\label{tab:scaling-verify-density}",
        "  \\footnotesize",
        "  \\begin{tabular}{rrrr}",
        "    \\toprule",
        f"    Neighbours $P$ & per-interval median (ms) & p95 (ms) & "
        f"\\% of {budget:.0f}\\,ms budget \\\\",
        "    \\midrule",
    ]
    for P, med, p95 in zip(dens["P"], dens["per_interval_ms"],
                           dens["per_interval_p95_ms"]):
        pct = 100.0 * med / budget
        lines.append(f"    {P} & {med:.4f} & {p95:.4f} & {pct:.2f}\\% \\\\")
    lines += [
        "    \\bottomrule",
        "  \\end{tabular}",
        "\\end{table}",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path}")


def plot_density(dens, out_path):
    if not HAVE_MPL:
        print("matplotlib not available - skipped density PNG")
        return
    import numpy as np
    P = dens["P"]
    med = dens["per_interval_ms"]
    budget = dens["budget_ms"]
    fit = dens["fit"]
    extrap = dens["extrapolated_saturation_P"]

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    # Fit / extrapolation line out to the (extrapolated) saturation point.
    x_max = max(P + [extrap if extrap else max(P)])
    xs = np.linspace(0, x_max * 1.02, 200)
    ys = fit["intercept_ms"] + fit["slope_ms_per_neighbor"] * xs
    ax.plot(xs, ys, "-", color="#999999", linewidth=1,
            label=f"fit {fit['slope_ms_per_neighbor']:.3f} ms/neighbour")
    ax.plot(P, med, "o-", color="#1f77b4", label="measured median")
    ax.axhline(budget, color="#d62728", linestyle="--",
               label=f"{budget:.0f} ms budget")
    if extrap:
        ax.axvline(extrap, color="#2ca02c", linestyle=":",
                   label=f"extrapolated $P^*\\approx${extrap:.0f}")
    ax.set_xlabel("neighbour density $P$ (vehicles verified per 100 ms interval)")
    ax.set_ylabel("per-interval verification time (ms)")
    ax.set_title("Experiment D — V2V verification saturation vs neighbour density")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Wrote {out_path}")


def generate_a_b(marginal_path, lifetime_path):
    """Experiments A + B. Each is generated only if its JSON input exists."""
    if marginal_path.exists():
        marginal = json.loads(marginal_path.read_text())
        write_marginal_csv(marginal, RESULTS_DIR / "scaling_marginal.csv")
        write_marginal_tex(marginal, RESULTS_DIR / "scaling_marginal.tex")
        plot_marginal(marginal, RESULTS_DIR / "scaling_marginal.png")
    else:
        print(f"No Experiment A input ({marginal_path.name}) - skipping A. "
              "Run: cd 1_blockchain-identity && "
              "npx hardhat run scripts/benchmark_scaling.js")

    if lifetime_path.exists():
        lifetime = json.loads(lifetime_path.read_text())
        write_lifetime_csv(lifetime, RESULTS_DIR / "scaling_lifetime.csv")
        write_lifetime_tex(lifetime, RESULTS_DIR / "scaling_lifetime.tex")
        plot_lifetime(lifetime, RESULTS_DIR / "scaling_lifetime.png")
    else:
        print(f"No Experiment B input ({lifetime_path.name}) - skipping B. "
              "Run: cd 1_blockchain-identity && "
              "npx hardhat run scripts/benchmark_scaling.js")


def generate_c_d(input_path):
    """Experiments C + D from scaling_verify.json (skipped if absent)."""
    if not input_path.exists():
        print(f"No Experiment C/D input ({input_path.name}) - skipping C/D. "
              "Run the verification drivers to produce scaling_verify.json.")
        return
    data = json.loads(input_path.read_text())
    if "credential_richness" in data and "selective_disclosure" in data:
        rich = data["credential_richness"]
        sd = data["selective_disclosure"]
        write_richness_csv(rich, sd, RESULTS_DIR / "scaling_verify_richness.csv")
        write_richness_tex(rich, sd, RESULTS_DIR / "scaling_verify_richness.tex")
        plot_richness(rich, sd, RESULTS_DIR / "scaling_verify_richness.png")
    else:
        print("No Experiment C data (credential_richness) in input - skipping C")

    if "v2v_density" in data:
        dens = data["v2v_density"]
        write_density_csv(dens, RESULTS_DIR / "scaling_verify_density.csv")
        write_density_tex(dens, RESULTS_DIR / "scaling_verify_density.tex")
        plot_density(dens, RESULTS_DIR / "scaling_verify_density.png")
    else:
        print("No Experiment D data (v2v_density) in input - skipping D")


def main():
    # Optional positional arg overrides the C/D verify input (backward compatible).
    verify_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    generate_a_b(DEFAULT_MARGINAL, DEFAULT_LIFETIME)
    generate_c_d(verify_path)


if __name__ == "__main__":
    main()
