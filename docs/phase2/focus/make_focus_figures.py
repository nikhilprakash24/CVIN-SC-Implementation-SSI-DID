#!/usr/bin/env python3
"""Figures and tables for the Phase 2 focus areas F1-F3, from committed run-of-record data only
(guide rule 1.3.10; register rows named on every figure).

Revised 2026-10-14 after the academic review (docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md):
  F1-1 (AR-39) excluded-event totals hatched; axis labelled "zero→nonzero SSTOREs"; code deposit noted.
  F1-2 (AR-15, AR-40) a state-storing flat reader (ERC-725xy) replaces ERC-1155; cells registered (#51).
  F2-1 (AR-37) a dot plot on a log axis with all six #33 rows; the pre-registered FAIL marked; both conditions named.
  F3-2 (AR-28, AR-38) withdrawn: three rows from different runs and hosts are a table, not one axis.

    python3 docs/phase2/focus/make_focus_figures.py          # write figures/*.svg, figures_data.json, FIGURES.md
    python3 docs/phase2/focus/make_focus_figures.py --check  # CI: data and tables current (images are not compared)

Palette: the visualisation guide's reference palette, slots 1-3 only; figures that compare ten standards use one
hue with the standards named on the axis. No dual axes; no bars on a log axis.
"""
import csv
import json
import pathlib
import re
import sys
import textwrap

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
PARITY_OPS = ["birth", "lifecycle_event", "ownership_transfer", "history_query", "history_query_cached",
              "history_query_cached_validated"]


def table(name):
    with open(TABLES / name) as f:
        return list(csv.reader(f))


def row(rows, label):
    head = rows[0]
    r = next(r for r in rows if r[0] == label)
    return {head[i]: r[i] for i in range(1, len(head))}


def num(cell):
    """Leading integer of a table cell ('5,797,549 (excl. 3 n/a)' -> 5797549) and its note, if any."""
    m = re.match(r"\s*([\d,]+)\s*(.*)", cell)
    return int(m.group(1).replace(",", "")), m.group(2).strip()


def rpc_bytes(cell):
    rpc, b = cell.split(" / ")
    return int(rpc.split()[0]), int(b.split()[0])


def host(path):
    e = json.loads((ROOT / path).read_text())["environment"]
    plat = e.get("platform") or e.get("os") or ""
    cpu = (e.get("cpu") or e.get("cpu_model") or "").replace("Intel(R) Xeon(R) Processor", "Xeon")
    kernel = plat.split("-")[2] if plat.count("-") > 2 else plat
    return f"{cpu}, kernel {kernel}"


def collect():
    life_tot = table("lifecycle_totals.csv")
    life_gas = row(table("lifecycle_gas.csv"), "**Lifetime total**")
    sst, logb = row(life_tot, "Zero→nonzero SSTOREs"), row(life_tot, "Log bytes")
    scale = table("scale.csv")
    r3 = {h: dict(zip(scale[0][1:], next(r for r in scale if r[0] == f"{h}|R3_resolve_document")[1:]))
          for h in ("h=1", "h=10", "h=50")}
    gas = table("crud_gas.csv")
    u3, u5 = row(gas, "U3_set_attribute"), row(gas, "U5_meta_tx")
    parity = json.loads((ROOT / "cv2x-testbed/results/lifecycle_parity.json").read_text())["results"]
    par = {}
    for r in parity:
        if r["operation"] in PARITY_OPS:
            par.setdefault(r["operation"], {})[r["backend"]] = round(r["median_ms"], 4)
    v2v = json.loads((ROOT / "cv2x-testbed/sumo/results/v2v_latency_stats.json").read_text())
    pki = json.loads((ROOT / "cv2x-testbed/results/pki_vs_erc1056.json").read_text())["results"]
    probe = json.loads((ROOT / "cv2x-testbed/results/freshness_k_probe.json").read_text())["derived"]
    full = next(r for r in pki if r.get("provider") == "erc1056_did" and r.get("operation") == "verify_message")
    return {
        "source_run": RUN,
        "f1_state_vs_gas": {"rows": "#35 (lifecycle gas), #49 (zero→nonzero SSTOREs, log bytes)",
                            "standards": {NAMES[k]: {"lifetime_gas": num(life_gas[k])[0], "note": num(life_gas[k])[1],
                                                     "zero_to_nonzero_sstores": num(sst[k])[0], "log_bytes": num(logb[k])[0]}
                                          for k in NAMES}},
        "f1_read_cost_vs_history": {"rows": "#31 (ERC-1056), #51 (all columns)",
                                    "series": {NAMES[k]: {h: dict(zip(("rpc", "bytes"), rpc_bytes(r3[h][k]))) for h in r3}
                                               for k in ("erc1056", "erc735", "erc725xy")}},
        "f2_lifecycle_parity_ms": {"rows": "#33 (committed 2026-10-04 re-run; D60)",
                                   "conditions": "centralized registry: M0, in-process, a lower bound; MOBI-VID-V2: M1, local Hardhat node",
                                   "preregistered_fail": "history query cached vs the database's history query: 'equal once cached' band [0.5, 2] FAILED (ratio 0.041)",
                                   "operations": par},
        "f3_write_paths_gas": {"rows": "#50, #34", "ERC-1056": {"direct (U3)": int(u3["erc1056"]), "relayed signed (U5)": int(u5["erc1056"])},
                               "ERC-4337": {"direct (U3)": int(u3["erc4337"]), "UserOperation via EntryPoint (U5)": int(u5["erc4337"])}},
        "f3_read_costs_table": {
            "note": "three separately measured costs from different runs and hosts; not comparable as ratios (guide 1.1.7); the figure was withdrawn (AR-38)",
            "rows": [
                {"what": "verify one V2V message, warm cached credential, no chain contact (SSI)", "median_ms": round(v2v["per_population"]["ssi"]["warm"]["median"], 4),
                 "unit": "per message", "condition": "M0", "host": host("cv2x-testbed/sumo/results/v2v_latency_stats.json"), "row": "#27"},
                {"what": "one probe refresh: an eth_call to check the identity is unchanged", "median_ms": round(probe["t_chain_ms"], 3),
                 "unit": "per refresh, not per message", "condition": "M1", "host": host("cv2x-testbed/results/freshness_k_probe.json"), "row": "#37 (predates the D51 fix)"},
                {"what": "verify one message with an uncached ERC-1056 resolution (key replayed from event logs)", "median_ms": round(full["median_ms"], 3),
                 "unit": "per message", "condition": "M1", "host": host("cv2x-testbed/results/pki_vs_erc1056.json"), "row": "#21 (predates the D51 fix)"},
            ]},
    }


def footer(fig, text):
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
    import matplotlib.ticker as ticker
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.hashsalt": "phase2", "figure.facecolor": SURFACE,
                         "axes.facecolor": SURFACE, "svg.fonttype": "none", "hatch.color": SURFACE})
    OUT.mkdir(exist_ok=True)
    meta = {"Creator": "make_focus_figures.py", "Date": None}
    (OUT / "f3_read_modes.svg").unlink(missing_ok=True)   # withdrawn (AR-38)

    # F1-1
    st = data["f1_state_vs_gas"]["standards"]
    order = sorted(st, key=lambda k: st[k]["lifetime_gas"])
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.5, 4.4), sharey=True)
    for ax, key, scale, xl, title in ((a, "zero_to_nonzero_sstores", 1, "zero→nonzero SSTOREs (opcodes, not net slots)", "State written over the 17-event lifecycle"),
                                      (b, "lifetime_gas", 1e6, "gas (millions)", "Lifetime gas, same lifecycle")):
        for i, k in enumerate(order):
            v = st[k][key] / scale
            excluded = bool(st[k]["note"]) and key == "lifetime_gas"
            ax.barh(i, v, color=S2 if k == "ERC-1056" else S1, height=0.6, hatch="////" if excluded else None)
            label = f" {v:,.0f}" if scale == 1 else f" {v:.2f}" + (" (excl. n/a)" if excluded else "")
            ax.text(v, i, label, va="center", fontsize=7.5, color=INK2)
        style(ax, title, xl)
    a.set_yticks(range(len(order)), order)
    b.set_xlim(0, 7.2)
    footer(fig, f"Source: {RUN}; register {data['f1_state_vs_gas']['rows']}. Hatched: totals that exclude events the standard cannot express. "
                "ERC-1056 (orange) keeps attributes in events. Association, not cause: ERC-735 and ERC-725xy creation cost is mostly per-identity contract code, which SSTOREs do not count.")
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    fig.savefig(OUT / "f1_state_vs_gas.svg", metadata=meta)
    plt.close(fig)

    # F1-2
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
        for v, names in ends.items():
            ax.text(hs[-1], v, "  " + " = ".join(names), va="center", fontsize=7.5, color=INK)
        ax.set_xticks(hs)
        style(ax, title, "history h (lifecycle events before the read)")
        ax.grid(axis="y", color=GRID, linewidth=0.6)
        ax.set_ylabel(yl, color=INK2, fontsize=8.5)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        ax.set_xlim(0, 66)
    a.legend(frameon=False, fontsize=7.5, loc="upper left")
    footer(fig, f"Source: {RUN}, tables/scale.csv; register {data['f1_read_cost_vs_history']['rows']}. "
                "ERC-735 and ERC-725xy store attributes in contract state; ERC-1056 replays events.")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(OUT / "f1_read_cost_vs_history.svg", metadata=meta)
    plt.close(fig)

    # F2-1: dot plot, log axis, all six operations
    pa = data["f2_lifecycle_parity_ms"]
    fig, ax = plt.subplots(figsize=(8.5, 4.3))
    for j, (backend, c, mk, nm) in enumerate((("centralized_registry", S1, "o", "centralized registry (M0, in-process: a lower bound)"),
                                              ("mobi_vid_v2", S2, "s", "MOBI-VID-V2 (M1, local Hardhat node)"))):
        xs, ys = [], []
        for i, o in enumerate(PARITY_OPS):
            v = pa["operations"].get(o, {}).get(backend)
            if v is not None:
                xs.append(v)
                ys.append(i)
                ax.text(v * 1.3, i, f"{v:g}", va="center", fontsize=7, color=INK2)
        ax.scatter(xs, ys, color=c, marker=mk, s=42, label=nm, zorder=3)
    fail_y = PARITY_OPS.index("history_query_cached")
    ax.text(0.0007, fail_y + 0.35, "pre-registered 'equal once cached' vs the database's history query: FAIL (ratio 0.041)",
            fontsize=7, color=INK)
    ax.set_xscale("log")
    ax.set_xlim(0.0005, 2000)
    ax.set_yticks(range(len(PARITY_OPS)), [o.replace("_", " ") for o in PARITY_OPS])
    ax.invert_yaxis()
    style(ax, "Lifecycle operations: median latency (ms, log scale)", "ms")
    ax.set_title("Lifecycle operations: median latency (ms, log scale)", loc="left", color=INK, fontsize=10, pad=26)
    ax.legend(frameon=False, fontsize=7.5, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, borderaxespad=0.2)
    footer(fig, f"Source: cv2x-testbed/results/lifecycle_parity.json; register {pa['rows']}. Different conditions: an in-process dictionary against "
                "a chain reached over a local node; the database series is a lower bound. The cached rows exist only for the chain backend.")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(OUT / "f2_lifecycle_parity.svg", metadata=meta)
    plt.close(fig)

    # F3-1
    wp = {k: v for k, v in data["f3_write_paths_gas"].items() if k != "rows"}
    fig, ax = plt.subplots(figsize=(8, 2.9))
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
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    style(ax, "One attribute update, written directly and through a third party (gas)", "gas")
    footer(fig, f"Source: {RUN}, tables/crud_gas.csv; register {data['f3_write_paths_gas']['rows']}. "
                "ERC-1056 U5: a relayer submits and pays; ERC-4337 U5: a bundler submits and the account pays (no paymaster).")
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    fig.savefig(OUT / "f3_write_paths.svg", metadata=meta)
    plt.close(fig)


def markdown(data):
    L = ["# Phase 2 Focus Figures — data tables", "",
         "**Generated** by `docs/phase2/focus/make_focus_figures.py` from committed run-of-record data; do not edit. "
         "Each table is the data behind one figure in `figures/` (the table view). **Author:** Nikhil Prakash (MASc, UBC ECE). "
         "Revised 2026-10-14 after the academic review (AR-15, AR-28, AR-37 to AR-40).", ""]
    st = data["f1_state_vs_gas"]
    L += ["## F1-1 State written and lifetime gas (`figures/f1_state_vs_gas.svg`)", f"Register {st['rows']}; {RUN}. "
          "Zero→nonzero SSTOREs are opcodes, not net slots, and exclude per-identity contract code.", "",
          "| Standard | zero→nonzero SSTOREs | log bytes | lifetime gas |", "|---|---:|---:|---:|"]
    for k, v in sorted(st["standards"].items(), key=lambda kv: kv[1]["lifetime_gas"]):
        L.append(f"| {k} | {v['zero_to_nonzero_sstores']:,} | {v['log_bytes']:,} | {v['lifetime_gas']:,}{' ' + v['note'] if v['note'] else ''} |")
    rc = data["f1_read_cost_vs_history"]
    L += ["", "## F1-2 Read cost against history (`figures/f1_read_cost_vs_history.svg`)", f"Register {rc['rows']}.", "",
          "| Standard | h=1 RPC / bytes | h=10 RPC / bytes | h=50 RPC / bytes |", "|---|---:|---:|---:|"]
    for k, s in rc["series"].items():
        L.append(f"| {k} | " + " | ".join(f"{s[h]['rpc']} / {s[h]['bytes']:,}" for h in ("h=1", "h=10", "h=50")) + " |")
    pa = data["f2_lifecycle_parity_ms"]
    L += ["", "## F2-1 Lifecycle operations, centralized vs on chain (`figures/f2_lifecycle_parity.svg`)",
          f"Register {pa['rows']}. Conditions: {pa['conditions']}. {pa['preregistered_fail']}.", "",
          "| Operation | centralized (ms) | MOBI-VID-V2 on chain (ms) |", "|---|---:|---:|"]
    for o in PARITY_OPS:
        v = pa["operations"].get(o, {})
        c = v.get("centralized_registry")
        L.append(f"| {o.replace('_', ' ')} | {'n/a' if c is None else f'{c:g}'} | {v['mobi_vid_v2']:g} |")
    wp = data["f3_write_paths_gas"]
    L += ["", "## F3-1 Direct and relayed writes (`figures/f3_write_paths.svg`)", f"Register {wp['rows']}.", "", "| Standard | path | gas |", "|---|---|---:|"]
    for std, paths in wp.items():
        if std == "rows":
            continue
        for p, v in paths.items():
            L.append(f"| {std} | {p} | {v:,} |")
    rt = data["f3_read_costs_table"]
    L += ["", "## F3-2 Read costs by chain contact (table only; the figure was withdrawn)", rt["note"] + ".", "",
          "| What is measured | median (ms) | unit | condition | host | register |", "|---|---:|---|---|---|---|"]
    for r in rt["rows"]:
        L.append(f"| {r['what']} | {r['median_ms']:g} | {r['unit']} | {r['condition']} | {r['host']} | {r['row']} |")
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
