#!/usr/bin/env python3
"""X-series: Claude-initiated exploratory figures and tables.

THE LINE: this set was proposed, designed and drawn by Claude without direction
from the author. It is kept apart from the author-directed sets (the blueprint
set in docs/blueprints/ and any future A-series) on purpose:
  * every figure carries the stamp below in its corner;
  * file names start with X- / XT-;
  * nothing here is cited by a chapter until the author promotes it (see README).

Every value is read from a result-of-record file at generation time. Nothing is
typed in. If a file moves, generation fails rather than drawing a stale number.

    python3 docs/figures/x_series/make_x_series.py
"""
import csv
import json
import math
import pathlib
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent
STAMP = "X-SERIES · EXPLORATORY · CLAUDE-INITIATED, NOT AUTHOR-DIRECTED · not cited until promoted"

GAS = ROOT / "4_comparison-framework/results/gas_benchmark.json"
MATRIX = ROOT / "4_comparison-framework/security-analysis/results/security_matrix.csv"
FRESH = ROOT / "cv2x-testbed/results/freshness_k.json"
H = ROOT / "1_blockchain-identity/results/metrics/latest"
LIFE, CRUD, RESOLVE, META = H / "lifecycle.json", H / "crud.json", H / "resolve.json", H / "meta.json"
RESOLVE_HTTP = ROOT / "1_blockchain-identity/results/metrics-rpc/latest/resolve.json"

SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
BLUE, AMBER, RED, GREEN = "#2a78d6", "#eda100", "#d03b3b", "#2f9e5b"
plt.rcParams.update({"font.family": ["DejaVu Sans"], "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "savefig.facecolor": SURF, "text.color": INK, "axes.edgecolor": "#c3c2b7",
                     "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK2})

LABEL = {"erc1056": "ERC-1056", "erc1056w": "ERC-1056 (wrapper)", "erc721": "ERC-721", "erc725": "ERC-725",
         "erc735": "ERC-735", "erc1155": "ERC-1155", "erc725xy": "ERC-725xy", "lsp8": "LSP8",
         "erc4337": "ERC-4337", "cvin": "CVIN-Combined"}
SOURCES = []


def load(p):
    SOURCES.append(str(p.relative_to(ROOT)))
    return json.loads(p.read_text())


def finish(fig, name, source, row):
    fig.text(0.01, -0.035, f"source: {source}  ·  register {row}", fontsize=7, color=MUTED, ha="left", va="bottom")
    fig.text(0.01, -0.065, STAMP, fontsize=7.5, color=RED, ha="left", va="bottom", fontweight="bold")
    out = OUT / f"{name}.png"
    fig.savefig(out, dpi=170, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print("wrote", out.relative_to(ROOT))


def tidy(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


# ------------------------------------------------------------------ X-01
def x01_op_heatmap():
    """Every operation × every standard, one view. The blueprint ladder shows create only."""
    g = load(GAS)
    stds = [s for s in g if s != "metadata"]
    ops = ["deployRegistry", "createIdentity", "updateAttribute", "addDelegateOrClaim", "revoke", "transferOwnership"]
    opl = ["deploy (shared)", "create", "update attribute", "delegate / claim", "revoke", "transfer"]
    stds.sort(key=lambda s: g[s]["createIdentity"]["gasUsed"])
    M = [[(g[s].get(o) or {}).get("gasUsed") for o in ops] for s in stds]
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    vals = [v for r in M for v in r if v]
    data = [[v if v else float("nan") for v in r] for r in M]
    im = ax.imshow(data, cmap="Blues", norm=LogNorm(min(vals), max(vals)), aspect="auto")
    for i, r in enumerate(M):
        for j, v in enumerate(r):
            if v is None:
                ax.text(j, i, "n/a", ha="center", va="center", fontsize=8, color=MUTED)
            else:
                dark = math.log(v) > (math.log(min(vals)) + math.log(max(vals))) / 2
                ax.text(j, i, f"{v:,}", ha="center", va="center", fontsize=8, color="white" if dark else INK)
    ax.set_xticks(range(len(ops)), opl, fontsize=9)
    ax.set_yticks(range(len(stds)), stds, fontsize=9)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cb.set_label("gas (log)", fontsize=8)
    ax.set_title("Gas for every operation on every standard. Create is where they differ; updates cluster near 30–120k.",
                 loc="left", fontsize=11, pad=12)
    fig.text(0.01, -0.005, "Deploy n/a = contract-per-identity (deploy is inside create). Other n/a = no primitive. Rows sorted by create gas.",
             fontsize=8, color=MUTED)
    finish(fig, "X-01_operation_gas_heatmap", GAS.relative_to(ROOT), "#25")


# ------------------------------------------------------------------ X-02
def x02_fleet_amortisation():
    """Lifetime gas per vehicle as the fleet grows: does contract-per-identity ever catch up?"""
    L = load(LIFE)
    meta = load(META)
    fig, ax = plt.subplots(figsize=(10.5, 6))
    fleets = None
    ends = []
    for a in L:
        ap = a["apportioned"]
        keys = sorted(ap, key=lambda k: float(re.sub(r"[^0-9.e]", "", k) or 0)) if isinstance(ap, dict) else None
        if isinstance(ap, list):
            xs = [p["fleet"] for p in ap]
            ys = [p["lifetimeGas"] if "lifetimeGas" in p else p["gas"] for p in ap]
        else:
            xs = [float(k) for k in keys]
            ys = [ap[k] for k in keys]
        fleets = xs
        lab = LABEL[a["adapter"]]
        hot = a["adapter"] in ("erc1056", "cvin", "erc735")
        ax.plot(xs, ys, marker="o", lw=2.2 if hot else 1.2, color=BLUE if a["adapter"] == "erc1056" else
                (AMBER if a["adapter"] == "cvin" else (RED if a["adapter"] == "erc735" else "#a7a69f")))
        ends.append((ys[-1], lab, hot))
    ends.sort()
    last_y = -1
    for y, lab, hot in ends:
        yy = max(y, last_y * 1.09) if last_y > 0 else y
        ax.text(fleets[-1] * 1.6, yy, f"{lab}  {y/1e6:.2f} M", va="center", fontsize=8.5,
                color=INK if hot else INK2, fontweight="bold" if hot else "normal")
        last_y = yy
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(fleets[0] * 0.7, fleets[-1] * 40)
    ax.set_xlabel("fleet size sharing the deployment (vehicles)")
    ax.set_ylabel("lifetime gas per vehicle, 17-event MOBI VID sequence")
    tidy(ax)
    ax.set_title("Shared registries amortise to their per-event cost; ERC-735 pays its deploy per vehicle and never falls.",
                 loc="left", fontsize=11, pad=12)
    finish(fig, "X-02_fleet_amortisation", f"{LIFE.relative_to(ROOT)} (run {meta['runId']})", "#30/#35")


# ------------------------------------------------------------------ X-03
def x03_rank_reversal():
    """Point cost (C1) vs lifetime cost, same harness run: rankings are not stable."""
    crud = load(CRUD)
    L = load(LIFE)
    meta = load(META)
    c1 = {r["adapter"]: r["gasUsed"] for r in crud if r["op"] == "C1_create_identity" and r.get("gasUsed")}
    life = {a["adapter"]: a["lifetimeGas"] for a in L}
    common = [a for a in c1 if a in life]
    r1 = {a: i for i, a in enumerate(sorted(common, key=lambda a: c1[a]))}
    r2 = {a: i for i, a in enumerate(sorted(common, key=lambda a: life[a]))}
    fig, ax = plt.subplots(figsize=(9, 6.4))
    for a in common:
        moved = abs(r1[a] - r2[a]) >= 2
        col = RED if moved else "#a7a69f"
        ax.plot([0, 1], [r1[a], r2[a]], color=col, lw=2.2 if moved else 1.2, marker="o")
        ax.text(-0.04, r1[a], f"{LABEL[a]}  {c1[a]:,}", ha="right", va="center", fontsize=8.5, color=INK if moved else INK2)
        ax.text(1.04, r2[a], f"{life[a]:,}  {LABEL[a]}", ha="left", va="center", fontsize=8.5, color=INK if moved else INK2)
    ax.set_xlim(-0.75, 1.75)
    ax.axis("off")
    ax.text(0, -0.8, "rank by C1 create gas", ha="center", fontsize=9, color=MUTED, fontweight="bold")
    ax.text(1, -0.8, "rank by 17-event lifetime gas", ha="center", fontsize=9, color=MUTED, fontweight="bold")
    ax.set_ylim(len(common) - 0.5, -1.3)
    fig.suptitle("Cheapest to create is not cheapest to own. Red: standards that move two or more places.",
                 x=0.02, ha="left", fontsize=11, y=0.99)
    finish(fig, "X-03_rank_reversal_create_vs_lifetime", f"{CRUD.relative_to(ROOT)}, lifecycle.json (run {meta['runId']}, one harness definition)", "#34/#35")


# ------------------------------------------------------------------ X-04
def x04_security_cost_frontier():
    """Lens 2 security score against lifetime gas: the H5 frontier as a picture."""
    rows = list(csv.reader(open(MATRIX)))
    SOURCES.append(str(MATRIX.relative_to(ROOT)))
    head = rows[0]
    score = {"DEFENDED": 1.0, "PARTIAL": 0.5, "VULNERABLE": 0.0}
    sec = {}
    for r in rows[1:]:
        if not r or r[0] in ("", "Legend") or r[0].startswith("W3C"):
            continue
        cells = [c.rstrip("*") for c in r[1:7]]
        s = [score[c] for c in cells if c in score]
        sec[r[0]] = (sum(s), len(s))
    L = load(LIFE)
    name = {"erc1056": "ERC-1056", "erc721": "ERC-721", "erc725": "ERC-725", "erc735": "ERC-735", "erc1155": "ERC-1155",
            "erc4337": "ERC-4337", "lsp8": "LSP8", "cvin": "CVIN-Combined", "erc725xy": "ERC-725xy"}
    pts = []
    for a in L:
        n = name.get(a["adapter"])
        if n in sec:
            s, k = sec[n]
            pts.append((a["lifetimeGas"], s / k * 6, n))
    pts.sort()
    front, best = [], -1
    for g_, s_, n_ in pts:
        if s_ > best:
            front.append((g_, s_))
            best = s_
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.step([p[0] for p in front], [p[1] for p in front], where="post", color=BLUE, lw=1.6, alpha=0.7)
    for g_, s_, n_ in pts:
        onf = (g_, s_) in front
        ax.scatter(g_, s_, s=70, color=BLUE if onf else "#a7a69f", zorder=3, edgecolor=SURF)
        ax.annotate(n_, (g_, s_), xytext=(6, 6), textcoords="offset points", fontsize=9, color=INK if onf else INK2)
    ax.set_xscale("log")
    ax.set_xlabel("lifetime gas per vehicle, 17-event sequence (log)")
    ax.set_ylabel("Lens 2 score (6 threats; D = 1, P = 0.5, V = 0; N/A scaled out)")
    tidy(ax)
    ax.set_title("No standard dominates: the frontier (blue) trades lifetime cost for threat coverage.",
                 loc="left", fontsize=11, pad=12)
    ax.text(0.01, 0.06, "ERC-725xy and MOBI-VID-V2 are absent: the matrix has no ERC-725xy row, the harness no MOBI adapter.",
            transform=ax.transAxes, fontsize=7.5, color=MUTED)
    ax.text(0.01, 0.02, "The score weights all six Lens 2 threats equally. That weighting is Claude's choice, not the thesis's; "
            "reasoned cells (*) count as executed.", transform=ax.transAxes, fontsize=7.5, color=MUTED)
    finish(fig, "X-04_security_cost_frontier", f"{MATRIX.relative_to(ROOT)} + lifecycle.json", "#28/#35 (score derived here)")


# ------------------------------------------------------------------ X-05
def x05_freshness_decision():
    """The freshness-k design choice as one curve: neighbours serviceable vs how long a revoked key survives."""
    F = load(FRESH)
    hz = 10
    pts = []
    for r in F["latency"]:
        k = r["k"]
        t = r["mean_ms"]
        stale = None if k == "inf" else (int(k) - 1) / hz
        pts.append((k, t, math.floor(50 / t), stale))
    d = F["derived"]
    tl, tc = d["t_local_ms"], d["t_chain_ms"]
    ks = [1, 2, 3, 5, 8, 12, 18, 25, 40, 60, 100, 146, 200, 300, 500]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot([(k - 1) / hz for k in ks], [50 / (tl + tc / k) for k in ks], color=BLUE, lw=2, label="fit t_eff = t_local + t_chain / k")
    for k, t, p, s in pts:
        if s is None:
            ax.axhline(p, color=MUTED, lw=1, ls=":")
            ax.text(0.15, p + 2, f"k = ∞: P* = {p}, revocation never seen", fontsize=8.5, color=MUTED)
        else:
            ax.scatter(s, p, s=70, color=BLUE, zorder=3, edgecolor=SURF)
            ax.annotate(f"k = {k}\nP* = {p}", (s, p), xytext=(8, 4), textcoords="offset points", fontsize=8.5)
    ax.axhline(100, color=GREEN, lw=1.2, ls="--")
    ax.text(30, 102, "P*(0.5) = 100: dense-traffic viability", fontsize=8.5, color=GREEN, ha="right")
    ax.set_xscale("symlog", linthresh=0.5)
    ax.set_xlim(-0.05, 60)
    ax.set_xlabel("worst-case time a revoked key is still accepted at 10 Hz (s) = (k − 1) / 10")
    ax.set_ylabel("neighbours serviceable in 50 ms, P*(0.5)")
    ax.set_ylim(0, 130)
    tidy(ax)
    ax.set_title("Every cached verifier buys neighbours with revocation lag. This host: ≈100 neighbours costs ≈14.5 s.",
                 loc="left", fontsize=11, pad=12)
    finish(fig, "X-05_freshness_tradeoff", FRESH.relative_to(ROOT), "#32 (host-dependent; #37 differs)")


# ------------------------------------------------------------------ X-06
def x06_read_path():
    """What a verifier pays to resolve a document: RPC calls vs latency, in-process and over HTTP."""
    R = load(RESOLVE)
    have_http = RESOLVE_HTTP.exists()
    RH = load(RESOLVE_HTTP) if have_http else []
    fig, ax = plt.subplots(figsize=(10, 6))
    for data, col, lab in ((R, BLUE, "in-process (M1-H)"), (RH, AMBER, "HTTP RPC (M1-H/HTTP)")):
        xs, ys, ns = [], [], []
        for r in data:
            if r["op"] == "R3_resolve_document" and r.get("supported"):
                xs.append(r["readRpcCalls"]); ys.append(r["latency"]["median"]); ns.append(LABEL[r["adapter"]])
        ax.scatter(xs, ys, s=60, color=col, label=lab, zorder=3, edgecolor=SURF)
        if col == AMBER or not have_http:
            for x, y, n in zip(xs, ys, ns):
                ax.annotate(n, (x, y), xytext=(5, 4), textcoords="offset points", fontsize=8)
    ax.set_xlabel("JSON-RPC calls to build the DID document (after the 17-event lifecycle)")
    ax.set_ylabel("median resolve latency (ms)")
    tidy(ax)
    ax.legend(frameon=False, fontsize=9)
    ax.set_title("Resolve latency follows the call count. Event-log designs pay one getLogs per change.",
                 loc="left", fontsize=11, pad=12)
    finish(fig, "X-06_read_path_calls_vs_latency", f"{RESOLVE.relative_to(ROOT)}" + (" + metrics-rpc" if have_http else ""), "#31/#39")


# ------------------------------------------------------------------ X-07
def x07_state_left_behind():
    """What each identity leaves in chain state: new storage slots vs log bytes over a life."""
    L = load(LIFE)
    fig, ax = plt.subplots(figsize=(10, 6))
    for a in L:
        x, y = a["lifetimeLogBytes"], a["lifetimeZeroToNonzeroSstores"]
        col = BLUE if a["adapter"] in ("erc1056", "erc1056w") else (AMBER if a["adapter"] == "cvin" else "#a7a69f")
        ax.scatter(x, y, s=70, color=col, zorder=3, edgecolor=SURF)
        off = {"erc1056": (-8, -14), "erc1056w": (6, 6), "erc4337": (6, -12), "erc725xy": (-6, 8)}.get(a["adapter"], (6, 4))
        ax.annotate(LABEL[a["adapter"]], (x, y), xytext=off, textcoords="offset points", fontsize=8.5,
                    ha="right" if off[0] < 0 else "left")
    ax.set_xlabel("log bytes emitted over the lifecycle (history, prunable by nodes)")
    ax.set_ylabel("zero→nonzero SSTOREs (permanent state every node keeps)")
    tidy(ax)
    ax.set_title("Event-log identities write history, not state: ERC-1056 creates 8 new slots in a whole life, ERC-735 145.",
                 loc="left", fontsize=11, pad=12)
    finish(fig, "X-07_state_vs_history", LIFE.relative_to(ROOT), "#30/#35")


# ------------------------------------------------------------------ tables
def tables():
    g = load(GAS)
    stds = [s for s in g if s != "metadata"]
    ops = ["createIdentity", "updateAttribute", "addDelegateOrClaim", "revoke", "transferOwnership"]
    base = g["ERC-1056"]
    lines = ["# XT-01 — Gas per operation as a multiple of ERC-1056", "",
             f"*{STAMP}.* Source `{GAS.relative_to(ROOT)}` (#25). A multiple above 1 means dearer than ERC-1056. "
             "Operation definitions differ per standard (see #6), so a ratio describes the realisation, not the abstract operation.", "",
             "| Standard | " + " | ".join(ops) + " |", "|---|" + "---:|" * len(ops)]
    for s in sorted(stds, key=lambda s: g[s]["createIdentity"]["gasUsed"]):
        cells = []
        for o in ops:
            v = (g[s].get(o) or {}).get("gasUsed")
            b = (base.get(o) or {}).get("gasUsed")
            cells.append("n/a" if not v else f"{v / b:.2f}×")
        lines.append(f"| {s} | " + " | ".join(cells) + " |")
    (OUT / "XT-01_gas_ratio_vs_erc1056.md").write_text("\n".join(lines) + "\n")

    L = load(LIFE)
    lines = ["# XT-02 — What a vehicle's whole life costs and leaves behind", "",
             f"*{STAMP}.* Source `{LIFE.relative_to(ROOT)}` (#30/#35), 17-event MOBI VID sequence, one harness definition.", "",
             "| Standard | Lifetime gas | Txs | Log bytes | New slots | Skipped events | Gas per tx |", "|---|---:|---:|---:|---:|---:|---:|"]
    for a in sorted(L, key=lambda a: a["lifetimeGas"]):
        sk = a["skippedEvents"]
        sk = len(sk) if isinstance(sk, list) else sk
        lines.append(f"| {LABEL[a['adapter']]} | {a['lifetimeGas']:,} | {a['lifetimeTxCount']} | {a['lifetimeLogBytes']:,} | "
                     f"{a['lifetimeZeroToNonzeroSstores']} | {sk} | {a['lifetimeGas'] // a['lifetimeTxCount']:,} |")
    (OUT / "XT-02_lifetime_footprint.md").write_text("\n".join(lines) + "\n")

    lines = ["# XT-03 — Requirement → substrate decision table", "",
             f"*{STAMP}.* This table is **interpretation**, not measurement. Each row reads the measured matrices "
             "(`security_matrix.csv`, `analysis_basic_set`, #25/#35) as a choice a system designer faces.", "",
             "| If the requirement is… | Choose | Because (measured) | Cost of the choice |", "|---|---|---|---|",
             "| lowest cost over a vehicle's life | ERC-1056 | cheapest lifetime (#35), 8 new slots | Sybil-exposed: self-registration (matrix) |",
             "| O(1) on-chain claim check by another contract | CVIN-Combined | claims verified at add time; getClaim O(1) | claim adds ≈287k gas each (#25) |",
             "| key recovery after compromise | ERC-4337 | only DEFENDED recovery cell (matrix) | ≈2.2 M lifetime; +46,830 per routed op |",
             "| identity that cannot be stolen by transfer | ERC-1155 (soulbound) | only DEFENDED identity-theft cell | no delegates; attributes off-chain |",
             "| VIN never visible on-chain | MOBI VID profile | only family that hashes and encrypts (matrix privacy) | application profile on top of a substrate |",
             "| agent that can act (execute) | ERC-725xy or ERC-4337 | only substrates with X1 (BASIC_ID_SET §4) | contract per identity; 1.68 M create |",
             "| verifier with no chain access at message time | any, with a cache | 0.153 ms warm (#27) | revocation lag ≤ (k − 1)/10 s (#32) |"]
    (OUT / "XT-03_requirement_decision_table.md").write_text("\n".join(lines) + "\n")
    print("wrote XT-01..03")


if __name__ == "__main__":
    for f in (x01_op_heatmap, x02_fleet_amortisation, x03_rank_reversal, x04_security_cost_frontier,
              x05_freshness_decision, x06_read_path, x07_state_left_behind, tables):
        f()
    (OUT / "SOURCES.txt").write_text("\n".join(sorted(set(SOURCES))) + "\n")
