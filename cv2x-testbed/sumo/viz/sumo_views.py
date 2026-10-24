#!/usr/bin/env python3
"""Figures that need the real SUMO network (TraCI-mode traces only).

    python3 sumo_views.py coldmap TRACE.jsonl [--out PNG]
    python3 sumo_views.py pairs   TRACE.jsonl FRAME_DIR [--every 10] [--out DIR]

coldmap  The network outline read with sumolib from highway_intersection.net.xml,
         with every first-contact (cold) verification drawn as a dot at the
         receiver's real x, y. Where vehicles meet, receivers pay for the
         credential.
pairs    For each SUMO-GUI frame captured with --screenshot-dir during the SAME
         run that wrote TRACE, the frame on the left and the trace-drawn road
         view at the same t on the right: what the simulator showed beside what
         the identity layer did.

Style and palette: docs/visual/VISUAL_PLAN.md §4 (shared with thesis_figures.py).
"""
import argparse
import collections
import os
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import thesis_figures as rt  # noqa: E402

NET = HERE.parent / "highway_intersection.net.xml"


def _sumolib():
    try:
        import sumolib
        return sumolib
    except ImportError:
        pass
    cands = [pathlib.Path(os.environ["SUMO_HOME"]) / "tools"] if os.environ.get("SUMO_HOME") else []
    try:
        import sumo as _s
        cands.append(pathlib.Path(_s.__file__).parent / "tools")
    except ImportError:
        pass
    for c in cands:
        if (c / "sumolib").is_dir():
            sys.path.append(str(c))
            import sumolib
            return sumolib
    sys.exit("sumolib not found: pip install eclipse-sumo or set SUMO_HOME")


def draw_net(ax, net, xlim=None, ylim=None):
    for edge in net.getEdges():
        for lane in edge.getLanes():
            xs, ys = zip(*lane.getShape())
            ax.plot(xs, ys, color=rt.GRID, lw=3.2, solid_capstyle="butt", zorder=0)
    for edge in net.getEdges():
        xs, ys = zip(*edge.getShape())
        ax.text(sum(xs) / len(xs), sum(ys) / len(ys) + 18, edge.getID(),
                fontsize=7, color=rt.MUTED, ha="center")


def coldmap(trace, out):
    sumolib = _sumolib()
    net = sumolib.net.readNet(str(NET))
    ev = rt.load_trace(trace)
    meta = ev["meta"][0]
    if meta["mode"] != "sumo":
        sys.exit("coldmap needs a TraCI-mode trace (real coordinates)")
    ident = rt.identity_map(ev)
    # receiver position at the step of each cold verification
    pos_at = {}
    for s in ev["snap"]:
        pos_at[round(s["t"], 3)] = {v[0]: (v[1], v[2]) for v in s["v"]}
    pts = collections.defaultdict(list)
    for e in ev["tx"]:
        where = pos_at.get(round(e["t"], 3))
        if not where:
            continue
        for rid, ok, cold, lat in e["rx"]:
            if ok and cold and rid in where:
                pts[ident.get(rid, "pki")].append(where[rid])
    fig, ax = plt.subplots(figsize=(13, 5.2))
    fig.subplots_adjust(top=0.80, bottom=0.12, left=0.05, right=0.99)
    draw_net(ax, net)
    for pop in ("ssi", "pki"):
        if pts[pop]:
            xs, ys = zip(*pts[pop])
            ax.scatter(xs, ys, s=22, color=rt.POP_COLOR[pop], edgecolors=rt.INK,
                       linewidths=0.4, alpha=0.85, zorder=3,
                       label=f"cold verification by a {pop.upper()} receiver (n={len(xs)})")
    ax.set_aspect("equal")
    allx = [p[0] for v in pts.values() for p in v] or [0, 5000]
    ax.set_xlim(min(0, min(allx) - 100), max(5000, max(allx) + 100))
    ax.set_ylim(-60, 1060)
    ax.set_xlabel("x, m (SUMO network coordinates)")
    ax.set_ylabel("y, m")
    ax.grid(False)
    ax.legend(loc="upper left", fontsize=8)
    rt.stencil_title(fig, "Where trust is paid for",
                     "Every first-contact verification, at the receiver's position. "
                     "Network outline read from highway_intersection.net.xml with sumolib.",
                     rt.provenance(trace, meta))
    out = pathlib.Path(out)
    rt.save(fig, out.parent, out.stem)


def pairs(trace, frame_dir, out_dir, every):
    from PIL import Image
    ev = rt.load_trace(trace)
    meta = ev["meta"][0]
    frames = sorted(pathlib.Path(frame_dir).glob("frame_*.png"))
    out_dir = pathlib.Path(out_dir)
    tmp = out_dir / "_f1"
    made = 0
    for f in frames:
        step = int(f.stem.split("_")[1])
        t = step * meta["step_s"]
        if round(t) % every or t == 0:
            continue
        rt.fig_road_frame(ev, trace, tmp, t, None)
        f1 = sorted(tmp.glob(f"F1_road_frame_t{int(round(t)):03d}.png"))[-1]
        a, b = Image.open(f).convert("RGB"), Image.open(f1).convert("RGB")
        h = 700
        a = a.resize((int(a.width * h / a.height), h))
        b = b.resize((int(b.width * h / b.height), h))
        sheet = Image.new("RGB", (a.width + b.width + 30, h + 50), (252, 252, 251))
        sheet.paste(a, (0, 40)); sheet.paste(b, (a.width + 30, 40))
        from PIL import ImageDraw
        d = ImageDraw.Draw(sheet)
        d.text((10, 10), f"t = {t:.0f} s   left: SUMO-GUI frame {f.name}   right: identity layer, same run, same instant"
               f"   ({pathlib.Path(trace).name}, seed {meta['seed']})", fill=(11, 11, 11))
        out_dir.mkdir(parents=True, exist_ok=True)
        sheet.save(out_dir / f"pair_t{int(round(t)):03d}.png")
        made += 1
    for p in tmp.glob("*"):
        p.unlink()
    if tmp.exists():
        tmp.rmdir()
    print(f"wrote {made} pairs to {out_dir}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("coldmap"); c.add_argument("trace"); c.add_argument("--out", default=None)
    p = sub.add_parser("pairs"); p.add_argument("trace"); p.add_argument("frames")
    p.add_argument("--every", type=int, default=10); p.add_argument("--out", default=None)
    a = ap.parse_args()
    root = HERE.parents[2] / "docs" / "visual" / "figures"
    if a.cmd == "coldmap":
        coldmap(a.trace, a.out or root / "sumo_coldmap" / f"coldmap_{rt.trace_name(a.trace)}.png")
    else:
        pairs(a.trace, a.frames, a.out or root / "pairs", a.every)


if __name__ == "__main__":
    main()
