#!/usr/bin/env python3
"""Render the trunk verification figure (tests, gas, W3C compliance).

Reads docs/figures/results_snapshot.json (produced by re-running the suites on
this trunk) and writes verification_dashboard.{png,svg} beside it. Every
number in the figure must be traceable to that snapshot; nothing is typed in
here by hand.

Palette follows the validated reference set in the dataviz method: status
colours (good / critical / warning) for pass-fail-partial state, paired with
text labels so colour never carries meaning alone; a single blue hue for the
magnitude (gas) panel; recessive grid and axis ink.
"""
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
SNAP = HERE / "results_snapshot.json"

# Reference palette (light surface).
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
GOOD = "#0ca30c"
CRIT = "#d03b3b"
WARN = "#fab219"
BLUE = "#2a78d6"

FONT = {"family": ["DejaVu Sans", "sans-serif"]}
plt.rcParams.update({
    "font.family": FONT["family"],
    "axes.edgecolor": AXIS,
    "axes.labelcolor": INK2,
    "xtick.color": MUTED,
    "ytick.color": INK2,
    "text.color": INK,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def strip(ax, keep_left=True):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_visible(keep_left)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(length=0)


def panel_tests(ax, suites):
    names = [s["name"] for s in suites]
    passed = [s["passed"] for s in suites]
    failed = [s["failed"] for s in suites]
    y = range(len(names))
    # Passed in the blue series hue, failed in critical red with a hatch:
    # blue/red is the CVD-safe diverging pair (green/red fails deutan
    # separation), and the hatch plus the ✓/✗ labels keep state readable
    # without colour.
    ax.barh(y, passed, color=BLUE, height=0.55, label="passed")
    ax.barh(y, failed, left=passed, color=CRIT, height=0.55, label="failed",
            hatch="///", edgecolor=SURFACE, linewidth=0.6)
    ax.set_yticks(list(y))
    ax.set_yticklabels(names, fontsize=9)
    ax.invert_yaxis()
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    strip(ax)
    for i, (p, f) in enumerate(zip(passed, failed)):
        label = f"{p} ✓" if f == 0 else f"{p} ✓  {f} ✗"
        ax.text(p + f + 0.4, i, label, va="center", fontsize=9, color=INK2)
    total_p, total_f = sum(passed), sum(failed)
    ax.set_title(f"Test suites — {total_p} passed, {total_f} failed",
                 loc="left", fontsize=11, color=INK, pad=10)
    ax.set_xlabel("tests", fontsize=9)
    ax.set_xlim(0, max(p + f for p, f in zip(passed, failed)) * 1.28)
    ax.legend(frameon=False, fontsize=8, loc="lower right")


def panel_gas(ax, gas):
    ops = list(gas.keys())
    vals = [gas[o] for o in ops]
    y = range(len(ops))
    ax.barh(y, vals, color=BLUE, height=0.55)
    ax.set_yticks(list(y))
    ax.set_yticklabels(ops, fontsize=9)
    ax.invert_yaxis()
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    strip(ax)
    for i, v in enumerate(vals):
        ax.text(v + max(vals) * 0.015, i, f"{v:,}", va="center",
                fontsize=9, color=INK2)
    ax.set_title("Gas per operation (Hardhat, solc 0.8.24, cancun)",
                 loc="left", fontsize=11, color=INK, pad=10)
    ax.set_xlabel("gas units", fontsize=9)
    ax.set_xlim(0, max(vals) * 1.22)
    ax.ticklabel_format(axis="x", style="plain")


def panel_compliance(ax, comp):
    specs = list(comp["by_spec"].keys())
    pct = [comp["by_spec"][s]["pct"] for s in specs]
    y = range(len(specs))
    ax.barh(y, [100] * len(specs), color=GRID, height=0.55)
    ax.barh(y, pct, color=BLUE, height=0.55)
    ax.set_yticks(list(y))
    ax.set_yticklabels(specs, fontsize=9)
    ax.invert_yaxis()
    strip(ax)
    ax.set_xlim(0, 118)
    ax.set_xticks([0, 25, 50, 75, 100])
    for i, s in enumerate(specs):
        d = comp["by_spec"][s]
        ax.text(102, i, f"{d['pct']:.1f}%  ({d['pass']}/{d['total']})",
                va="center", fontsize=9, color=INK2)
    ax.set_title(f"W3C compliance — {comp['overall_pct']:.1f}% overall "
                 f"({comp['pass']} pass · {comp['partial']} partial · "
                 f"{comp['fail']} fail of {comp['total']})",
                 loc="left", fontsize=11, color=INK, pad=10)
    ax.set_xlabel("% of checks passing (self-authored checker)", fontsize=9)


def main():
    snap = json.loads(SNAP.read_text())
    fig, axes = plt.subplots(3, 1, figsize=(9.5, 10.2),
                             gridspec_kw={"height_ratios": [1.25, 1, 0.8]})
    panel_tests(axes[0], snap["suites"])
    panel_gas(axes[1], snap["gas"])
    panel_compliance(axes[2], snap["compliance"])
    # Title on its own line, meta line beneath it, plots start below both.
    fig.suptitle("Trunk verification snapshot", x=0.02, y=0.985, ha="left",
                 va="top", fontsize=14, color=INK, fontweight="bold")
    fig.text(0.02, 0.962,
             f"{snap['meta']['repo']} @ {snap['meta']['commit']} · "
             f"{snap['meta']['date']} · {snap['meta']['env']}",
             fontsize=8.5, color=MUTED, va="top")
    fig.tight_layout(rect=(0, 0, 1, 0.935))
    for ext in ("png", "svg"):
        out = HERE / f"verification_dashboard.{ext}"
        fig.savefig(out, dpi=200 if ext == "png" else None)
        print("wrote", out)


if __name__ == "__main__":
    main()
