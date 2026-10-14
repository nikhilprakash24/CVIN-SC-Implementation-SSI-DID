#!/usr/bin/env python3
"""Figures and tables for the Phase 2 focus areas F1-F3, from committed run-of-record data only
(guide rule 1.3.10; register rows named on every figure).

    python3 docs/phase2/focus/make_focus_figures.py          # write figures/*.svg, figures_data.json, FIGURES.md
    python3 docs/phase2/focus/make_focus_figures.py --check  # CI: data and tables current (images are not compared)

Palette: the visualisation guide's reference palette, slots 1-3 only (they validate all-pairs); figures that
compare ten standards use one hue with the standards named on the axis, never ten colours. No dual axes:
two measures are two panels.
"""
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "figures"
TABLES = ROOT / "1_blockchain-identity/results/metrics/latest/tables"
RUN = "harness run 2026-10-09T02-09-36Z_7a9a996 (M1-H)"
NAMES = {"erc1056": "ERC-1056", "erc1056w": "ERC-1056 (wrapper)", "erc721": "ERC-721", "erc725": "ERC-725",
         "erc735": "ERC-735", "erc1155": "ERC-1155", "erc725xy": "ERC-725xy", "lsp8": "LSP8",
         "erc4337": "ERC-4337", "cvin": "CVIN-Combined"}
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"


def table(name):
    with open(TABLES / name) as f:
        return list(csv.reader(f))


def row(rows, label):
    head = rows[0]
    r = next(r for r in rows if r[0] == label)
    return {head[i]: r[i] for i in range(1, len(head))}


def num(cell):
    """Leading integer of a table cell ('5,797,549 (excl. 3 n/a)' -> 5797549) and its note, if any."""
    import re
    m = re.match(r"\s*([\d,]+)\s*(.*)", cell)
    return int(m.group(1).replace(",", "")), m.group(2).strip()


def collect():
    life_tot = table("lifecycle_totals.csv")
    life_gas = row(table("lifecycle_gas.csv"), "**Lifetime total**")
    sst = row(life_tot, "Zero→nonzero SSTOREs")
    logb = row(life_tot, "Log bytes")
    scale = table("scale.csv")
    r3 = {}
    for h in ("h=1", "h=10", "h=50"):
        r = next(r for r in scale if r[0] == f"{h}|R3_resolve_document")
        r3[h] = {scale[0][i]: r[i] for i in range(1, len(scale[0]))}
    gas = table("crud_gas.csv")
    u3, u5 = row(gas, "U3_set_attribute"), row(gas, "U5_meta_tx")

    def rpc_bytes(cell):
        rpc, b = cell.split(" / ")
        return int(rpc.split()[0]), int(b.split()[0])

    parity = json.loads((ROOT / "cv2x-testbed/results/lifecycle_parity.json").read_text())["results"]
    par = {}
    for r in parity:
        if r["operation"] in ("birth", "lifecycle_event", "ownership_transfer", "history_query"):
            par.setdefault(r["operation"], {})[r["backend"]] = round(r["median_ms"], 4)
    v2v = json.loads((ROOT / "cv2x-testbed/sumo/results/v2v_latency_stats.json").read_text())
    pki = json.loads((ROOT / "cv2x-testbed/results/pki_vs_erc1056.json").read_text())["results"]
    probe = json.loads((ROOT / "cv2x-testbed/results/freshness_k_probe.json").read_text())["derived"]
    full = next(r for r in pki if r.get("provider") == "erc1056_did" and r.get("operation") == "verify_message")
    return {
        "source_run": RUN,
        "f1_state_vs_gas": {"rows": "#35 (lifecycle gas), #49 (zero→nonzero SSTOREs, log bytes)",
                            "standards": {NAMES[k]: {"lifetime_gas": num(life_gas[k])[0], "note": num(life_gas[k])[1],
                                                     "new_slots": num(sst[k])[0], "log_bytes": num(logb[k])[0]} for k in NAMES}},
        "f1_read_cost_vs_history": {"rows": "#31", "series": {NAMES[k]: {h: dict(zip(("rpc", "bytes"), rpc_bytes(r3[h][k])))
                                                                         for h in r3} for k in ("erc1056", "erc735", "erc1155")}},
        "f2_lifecycle_parity_ms": {"rows": "#33 (committed second run; D60)", "operations": par},
        "f3_write_paths_gas": {"rows": "#50, #34", "ERC-1056": {"direct (U3)": int(u3["erc1056"]), "relayed signed (U5)": int(u5["erc1056"])},
                               "ERC-4337": {"direct (U3)": int(u3["erc4337"]), "UserOperation via EntryPoint (U5)": int(u5["erc4337"])}},
        "f3_read_modes_ms": {"rows": "#27 (offline), #37 (probe), #21 (full resolution); #21 and #37 predate the D51 fix and its added RPC (re-run due, A3b)",
                             "offline: cached credential, no chain contact (V2V warm, M0)": round(v2v["per_population"]["ssi"]["warm"]["median"], 4),
                             "probe: one eth_call to check the identity is unchanged": round(probe["t_chain_ms"], 3),
                             "full resolution: key replayed from event logs, uncached": round(full["median_ms"], 3)},
    }


def footer(fig, text):
    import textwrap
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(text, 150)), fontsize=7, color=INK2, va="bottom")


def style(ax, title, xlabel):
    ax.set_title(title, loc="left", color=INK, fontsize=10, pad=8)
    ax.set_xlabel(xlabel, color=INK2, fontsize=8.5)
    ax.tick_params(colors=INK2, labelsize=8, length=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def draw(data):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker  # noqa: F401
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.hashsalt": "phase2", "figure.facecolor": SURFACE,
                         "axes.facecolor": SURFACE, "svg.fonttype": "none"})
    OUT.mkdir(exist_ok=True)
    meta = {"Creator": "make_focus_figures.py", "Date": None}

    # F1-1: state written vs lifetime gas, two panels sharing the standards axis
    st = data["f1_state_vs_gas"]["standards"]
    order = sorted(st, key=lambda k: st[k]["lifetime_gas"])
    fig, (a, b) = plt.subplots(1, 2, figsize=(9, 4.2), sharey=True)
    y = range(len(order))
    for ax, key, scale, xl, title in ((a, "new_slots", 1, "new storage slots (zero→nonzero SSTOREs)", "State written over the 17-event lifecycle"),
                                      (b, "lifetime_gas", 1e6, "gas (millions)", "Lifetime gas, same lifecycle")):
        vals = [st[k][key] / scale for k in order]
        ax.barh(list(y), vals, color=[S2 if k == "ERC-1056" else S1 for k in order], height=0.6)
        for i, v in enumerate(vals):
            ax.text(v, i, f" {v:,.0f}" if scale == 1 else f" {v:.2f}", va="center", fontsize=7.5, color=INK2)
        style(ax, title, xl)
    a.set_yticks(list(y), order)
    footer(fig, f"Source: {RUN}; register {data['f1_state_vs_gas']['rows']}. ERC-1056 (orange) keeps attributes in events.")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(OUT / "f1_state_vs_gas.svg", metadata=meta)
    plt.close(fig)

    # F1-2: read cost against history, two panels (RPC calls; bytes), three series
    se = data["f1_read_cost_vs_history"]["series"]
    hs = [1, 10, 50]
    fig, (a, b) = plt.subplots(1, 2, figsize=(9, 3.8))
    for ax, key, yl, title in ((a, "rpc", "RPC calls", "RPC calls to resolve the DID document"),
                               (b, "bytes", "bytes returned", "Bytes returned by the resolution")):
        ends = {}
        for (name, s), c in zip(se.items(), (S2, S1, S3)):
            vals = [s[f"h={h}"][key] for h in hs]
            ax.plot(hs, vals, color=c, linewidth=2, marker="o", markersize=5, label=name)
            ends.setdefault(vals[-1], []).append(name)
        for v, names in ends.items():   # series ending on the same value share one label (no overprint)
            ax.text(hs[-1], v, "  " + " = ".join(names), va="center", fontsize=7.5, color=INK)
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        ax.set_xticks(hs)
        style(ax, title, "history h (lifecycle events before the read)")
        ax.grid(axis="y", color=GRID, linewidth=0.6)
        ax.set_ylabel(yl, color=INK2, fontsize=8.5)
        ax.set_xlim(0, 62)
    a.legend(frameon=False, fontsize=7.5, loc="upper left")
    footer(fig, f"Source: {RUN}, tables/scale.csv; register {data['f1_read_cost_vs_history']['rows']}.")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(OUT / "f1_read_cost_vs_history.svg", metadata=meta)
    plt.close(fig)

    # F2-1: centralized vs on-chain lifecycle backend, log scale, two series
    ops = data["f2_lifecycle_parity_ms"]["operations"]
    labels = list(ops)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    w = 0.38
    for j, (backend, c, nm) in enumerate((("centralized_registry", S1, "centralized registry (in-process)"),
                                          ("mobi_vid_v2", S2, "MOBI-VID-V2 on a local chain"))):
        xs = [i + (j - 0.5) * w for i in range(len(labels))]
        vals = [ops[o][backend] for o in labels]
        ax.bar(xs, vals, width=w - 0.04, color=c, label=nm)
        for x, v in zip(xs, vals):
            ax.text(x, v * 1.15, f"{v:g}", ha="center", fontsize=7, color=INK2)
    ax.set_yscale("log")
    ax.set_xticks(range(len(labels)), [l.replace("_", " ") for l in labels])
    style(ax, "Lifecycle operations: median latency (ms, log scale)", "")
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, fontsize=7.5)
    footer(fig, f"Source: cv2x-testbed/results/lifecycle_parity.json; register {data['f2_lifecycle_parity_ms']['rows']}.")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(OUT / "f2_lifecycle_parity.svg", metadata=meta)
    plt.close(fig)

    # F3-1: direct vs relayed writes (gas)
    wp = {k: v for k, v in data["f3_write_paths_gas"].items() if k != "rows"}
    fig, ax = plt.subplots(figsize=(8, 2.8))
    ylab, vals, cols = [], [], []
    for std, paths in wp.items():
        for (p, v), c in zip(paths.items(), (S1, S2)):
            ylab.append(f"{std}: {p}")
            vals.append(v)
            cols.append(c)
    ax.barh(range(len(vals)), vals, color=cols, height=0.6)
    for i, v in enumerate(vals):
        ax.text(v, i, f" {v:,}", va="center", fontsize=7.5, color=INK2)
    ax.set_yticks(range(len(vals)), ylab)
    ax.invert_yaxis()
    style(ax, "One attribute update, written directly and through a third party (gas)", "gas")
    footer(fig, f"Source: {RUN}, tables/crud_gas.csv; register {data['f3_write_paths_gas']['rows']}.")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(OUT / "f3_write_paths.svg", metadata=meta)
    plt.close(fig)

    # F3-2: read modes, log scale
    rm = {k: v for k, v in data["f3_read_modes_ms"].items() if k != "rows"}
    fig, ax = plt.subplots(figsize=(8, 2.6))
    names = list(rm)
    ax.barh(range(len(names)), [rm[n] for n in names], color=[S3, S1, S2], height=0.6)
    for i, n in enumerate(names):
        ax.text(rm[n] * 1.08, i, f"{rm[n]:.3g} ms", va="center", fontsize=7.5, color=INK2)
    ax.set_xscale("log")
    ax.set_yticks(range(len(names)), names, fontsize=7.5)
    ax.invert_yaxis()
    style(ax, "Verifying one vehicle message, by chain contact (median ms, log scale)", "ms")
    footer(fig, "Register " + data["f3_read_modes_ms"]["rows"] + ".")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(OUT / "f3_read_modes.svg", metadata=meta)
    plt.close(fig)


def markdown(data):
    L = ["# Phase 2 Focus Figures — data tables", "",
         "**Generated** by `docs/phase2/focus/make_focus_figures.py` from committed run-of-record data; do not edit. "
         "Each table is the data behind one figure in `figures/` (the table view). **Author:** Nikhil Prakash (MASc, UBC ECE).", ""]
    st = data["f1_state_vs_gas"]
    L += ["## F1-1 State written and lifetime gas (`figures/f1_state_vs_gas.svg`)", f"Register {st['rows']}; {RUN}.", "",
          "| Standard | new storage slots | log bytes | lifetime gas |", "|---|---:|---:|---:|"]
    for k, v in sorted(st["standards"].items(), key=lambda kv: kv[1]["lifetime_gas"]):
        L.append(f"| {k} | {v['new_slots']:,} | {v['log_bytes']:,} | {v['lifetime_gas']:,}{' ' + v['note'] if v['note'] else ''} |")
    rc = data["f1_read_cost_vs_history"]
    L += ["", "## F1-2 Read cost against history (`figures/f1_read_cost_vs_history.svg`)", f"Register {rc['rows']}.", "",
          "| Standard | h=1 RPC / bytes | h=10 RPC / bytes | h=50 RPC / bytes |", "|---|---:|---:|---:|"]
    for k, s in rc["series"].items():
        L.append(f"| {k} | " + " | ".join(f"{s[h]['rpc']} / {s[h]['bytes']:,}" for h in ("h=1", "h=10", "h=50")) + " |")
    pa = data["f2_lifecycle_parity_ms"]
    L += ["", "## F2-1 Lifecycle operations, centralized vs on chain (`figures/f2_lifecycle_parity.svg`)", f"Register {pa['rows']}.", "",
          "| Operation | centralized (ms) | MOBI-VID-V2 on chain (ms) |", "|---|---:|---:|"]
    for o, v in pa["operations"].items():
        L.append(f"| {o.replace('_', ' ')} | {v['centralized_registry']:g} | {v['mobi_vid_v2']:g} |")
    wp = data["f3_write_paths_gas"]
    L += ["", "## F3-1 Direct and relayed writes (`figures/f3_write_paths.svg`)", f"Register {wp['rows']}.", "", "| Standard | path | gas |", "|---|---|---:|"]
    for std, paths in wp.items():
        if std == "rows":
            continue
        for p, v in paths.items():
            L.append(f"| {std} | {p} | {v:,} |")
    rm = data["f3_read_modes_ms"]
    L += ["", "## F3-2 Read modes (`figures/f3_read_modes.svg`)", f"Register {rm['rows']}.", "", "| Mode | median ms |", "|---|---:|"]
    for k, v in rm.items():
        if k != "rows":
            L.append(f"| {k} | {v:g} |")
    return "\n".join(L) + "\n"


def main():
    data = collect()
    text_json = json.dumps(data, indent=1, ensure_ascii=False) + "\n"
    md = markdown(data)
    if "--check" in sys.argv:
        stale = [p.name for p, t in ((OUT / "figures_data.json", text_json), (HERE / "FIGURES.md", md))
                 if not p.exists() or p.read_text() != t]
        if stale:
            print("STALE (run docs/phase2/focus/make_focus_figures.py): " + ", ".join(stale))
            return 1
        print("phase 2 focus figures: data and tables current")
        return 0
    draw(data)
    (OUT / "figures_data.json").write_text(text_json)
    (HERE / "FIGURES.md").write_text(md)
    print(f"wrote {len(list(OUT.glob('*.svg')))} figures, figures_data.json and FIGURES.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
