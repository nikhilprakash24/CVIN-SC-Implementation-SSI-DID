#!/usr/bin/env python3
"""
Render a V2V/V2I trace (schema cvin-v2v-trace/1) into thesis figures, a defence animation and a
down-sampled replay for the results dashboard (docs/PLAN_SUMO_VISUALISATION.md, steps V2, V3, V5).

    python3 render_trace.py results/traces/trace_rsu_seed1.jsonl.gz --out results/figures
    python3 render_trace.py results/traces/trace_revocation_k5_seed1.jsonl.gz --out results/figures --revocation

Every figure states its mobility source, seed, commit and the radio caveat in the frame.
Outputs (prefix = trace file stem):
    <prefix>_spacetime.png      vehicle trajectories (x over time) by identity population, RSU positions
    <prefix>_latency.png        verification latency over time by path (BSM SSI/PKI, SPaT; cold vs warm)
    <prefix>_revocation.png     (--revocation) SPaT from the revoked RSU accepted per receiver over time
    <prefix>_animation.gif      top-down replay of a 1.5 km window around RSU 2 (or the busiest RSU)
    <prefix>_replay.json        down-sampled replay (every 5th step) for the dashboard panel
"""
import argparse
import gzip
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import animation  # noqa: E402

INK = "#15191c"
INK2 = "#4c555b"
GRID = "#dde1df"
SSI = "#2f5d73"      # SSI / W3C credential population
PKI = "#a86400"      # PKI population
RSU = "#6b3fa0"      # infrastructure
OK = "#217a3c"
BAD = "#b3261e"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "text.color": INK, "savefig.dpi": 300, "figure.dpi": 100})


def load(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    header, steps, tx, rx, attacks, revokes = None, [], {}, [], [], []
    with opener(path, "rt") as f:
        for line in f:
            e = json.loads(line)
            t = e["type"]
            if t == "header":
                header = e
            elif t == "step":
                steps.append(e)
            elif t == "tx":
                tx[e["msg"]] = e
            elif t == "rx":
                rx.append(e)
            elif t == "attack":
                attacks.append(e)
            elif t == "revoke":
                revokes.append(e)
    return header, steps, tx, rx, attacks, revokes


def caption(h):
    env = h.get("environment") or {}
    return (f"mobility: {h['mobility']} · seed {h['seed']} · commit {env.get('git_commit')}"
            f"{' (code dirty)' if env.get('code_dirty') else ''} · {h['caveat']}")


def stamp(fig, h):
    fig.text(0.01, 0.005, caption(h), fontsize=6.5, color=INK2, ha="left", va="bottom")


def spacetime(h, steps, out):
    pop = {}
    tracks = defaultdict(lambda: ([], []))
    for s in steps:
        for v in s["vehicles"]:
            pop[v["id"]] = v["pop"]
            xs, ts = tracks[v["id"]]
            xs.append(v["x"])
            ts.append(s["t"])
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    for vid, (xs, ts) in tracks.items():
        # break the line where the mock highway wraps around
        seg_x, seg_t = [xs[0]], [ts[0]]
        for x, t in zip(xs[1:], ts[1:]):
            if x < seg_x[-1] - 1000:
                ax.plot(seg_t, seg_x, color=SSI if pop[vid] == "ssi" else PKI, lw=0.6, alpha=0.8)
                seg_x, seg_t = [], []
            seg_x.append(x)
            seg_t.append(t)
        ax.plot(seg_t, seg_x, color=SSI if pop[vid] == "ssi" else PKI, lw=0.6, alpha=0.8)
    for r in h.get("rsus") or []:
        ax.axhline(r["x"], color=RSU, lw=0.8, ls="--")
        ax.text(steps[-1]["t"] if steps else 0, r["x"], f" {r['id']}", color=RSU, fontsize=7, va="center")
    ax.set_xlabel("simulated time (s)")
    ax.set_ylabel("position along the highway (m)")
    ax.set_title("Vehicle trajectories by identity population", loc="left", fontsize=10)
    ax.plot([], [], color=SSI, label="SSI (W3C credential, secp256k1)")
    ax.plot([], [], color=PKI, label="PKI (IEEE 1609.2-style)")
    if h.get("rsus"):
        ax.plot([], [], color=RSU, ls="--", label="roadside unit")
    ax.legend(loc="upper right", fontsize=7, frameon=False)
    ax.grid(color=GRID, lw=0.5)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    stamp(fig, h)
    fig.savefig(out)
    plt.close(fig)


def latency(h, steps, tx, rx, out):
    pop = {}
    for s in steps:
        for v in s["vehicles"]:
            pop[v["id"]] = v["pop"]
    series = defaultdict(lambda: defaultdict(list))
    for e in rx:
        if not e["ok"]:
            continue
        t = tx.get(e["msg"])
        if t is None:
            continue
        kind = t["kind"]
        if kind in ("BSM", "FCW", "EEBL"):
            label = f"BSM {pop.get(t['from'], '?').upper()} {e['path']}"
        elif kind == "SPaT":
            label = f"SPaT {e['path']}"
        else:
            continue
        series[label][round(e["t"])].append(e["verify_ms"])
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    colors = {"BSM SSI warm": SSI, "BSM PKI warm": PKI, "SPaT warm": RSU,
              "BSM SSI cold": SSI, "BSM PKI cold": PKI, "SPaT cold": RSU}
    for label in sorted(series):
        pts = sorted(series[label].items())
        xs = [p[0] for p in pts]
        ys = [sorted(p[1])[len(p[1]) // 2] for p in pts]
        ax.plot(xs, ys, marker="o" if "cold" in label else None, ms=3, lw=1.2,
                ls=":" if "cold" in label else "-", color=colors.get(label, INK2), label=label)
    ax.set_yscale("log")
    ax.set_xlabel("simulated time (s), per-second median")
    ax.set_ylabel("verify latency (ms, log)")
    ax.set_title("Verification latency by message path", loc="left", fontsize=10)
    ax.legend(fontsize=7, frameon=False, ncol=2)
    ax.grid(color=GRID, lw=0.5, which="both")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    stamp(fig, h)
    fig.savefig(out)
    plt.close(fig)


def revocation(h, tx, rx, revokes, out):
    if not revokes:
        return
    t_rev = revokes[0]["t"]
    per = defaultdict(list)
    for e in rx:
        t = tx.get(e["msg"])
        if t is None or t["from"] != "rsu_1" or t["kind"] != "SPaT":
            continue
        per[e["to"]].append((e["t"], e["ok"]))
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    for i, (vid, evs) in enumerate(sorted(per.items())):
        for t, ok in evs:
            ax.plot([t], [i], marker="|" if ok else "x", ms=6, color=OK if ok else BAD, lw=0)
    ax.axvline(t_rev, color=BAD, lw=1)
    ax.text(t_rev, len(per) - 0.4, "  rsu_1 revoked", color=BAD, fontsize=7, va="top")
    ax.set_yticks(range(len(per)))
    ax.set_yticklabels(sorted(per), fontsize=6)
    ax.set_xlabel("simulated time (s)")
    ax.set_title(f"SPaT from a revoked RSU: accepted (|) and rejected (x), revocation re-check every k = {h.get('refresh_k')}",
                 loc="left", fontsize=9)
    ax.grid(color=GRID, lw=0.5, axis="x")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    stamp(fig, h)
    fig.savefig(out)
    plt.close(fig)


def window_center(h, steps):
    rsus = h.get("rsus") or []
    if rsus:
        return rsus[1]["x"] if len(rsus) > 1 else rsus[0]["x"]
    xs = [v["x"] for v in steps[len(steps) // 2]["vehicles"]]
    return sorted(xs)[len(xs) // 2]


def animate(h, steps, tx, rx, out, frames_every=2):
    cx = window_center(h, steps)
    lo, hi = cx - 750, cx + 750
    rx_by_t = defaultdict(list)
    for e in rx:
        t = tx.get(e["msg"])
        if t is not None:
            rx_by_t[round(e["t"], 1)].append((t["from"], e["to"], e["ok"], t["kind"]))
    rsu_pos = {r["id"]: (r["x"], r["y"]) for r in h.get("rsus") or []}
    fig, ax = plt.subplots(figsize=(7.5, 2.6))
    sel = steps[::frames_every]

    def draw(i):
        ax.clear()
        s = sel[i]
        pos = {v["id"]: (v["x"], v["y"], v["pop"]) for v in s["vehicles"]}
        for a, b, ok, kind in rx_by_t.get(round(s["t"], 1), []):
            pa = rsu_pos.get(a) or (pos[a][:2] if a in pos else None)
            pb = pos[b][:2] if b in pos else None
            if pa and pb and lo <= pa[0] <= hi and lo <= pb[0] <= hi:
                ax.plot([pa[0], pb[0]], [pa[1], pb[1]], color=(OK if ok else BAD) if kind == "SPaT" else (GRID if ok else BAD),
                        lw=0.8 if kind == "SPaT" else 0.4, alpha=0.9 if kind == "SPaT" else 0.6, zorder=1)
        for vid, (x, y, p) in pos.items():
            if lo <= x <= hi:
                ax.plot(x, y, "o", ms=5, color=SSI if p == "ssi" else PKI, zorder=3)
        for rid, (x, y) in rsu_pos.items():
            if lo <= x <= hi:
                ax.plot(x, y, "^", ms=9, color=RSU, zorder=4)
                ax.text(x, y + 4, rid, color=RSU, fontsize=7, ha="center")
        ax.set_xlim(lo, hi)
        ax.set_ylim(495, 520)
        ax.set_yticks([])
        ax.set_xlabel("position along the highway (m)")
        ax.set_title(f"t = {s['t']:.1f} s · dots: SSI (blue) / PKI (amber) vehicles · triangles: RSUs · "
                     f"lines: SPaT verified (green) / rejected (red), BSM verified (grey) / rejected (red)", loc="left", fontsize=7)
        ax.text(lo, 496, caption(h), fontsize=5.5, color=INK2)

    anim = animation.FuncAnimation(fig, draw, frames=len(sel), interval=200)
    anim.save(out, writer=animation.PillowWriter(fps=5))
    plt.close(fig)


def replay(h, steps, tx, rx, out, every=5):
    """Down-sampled replay for the dashboard: positions every `every` steps and the SPaT links."""
    spat = defaultdict(list)
    for e in rx:
        t = tx.get(e["msg"])
        if t is not None and t["kind"] == "SPaT":
            spat[round(e["t"], 1)].append([t["from"], e["to"], 1 if e["ok"] else 0])
    frames = []
    for s in steps[::every]:
        frames.append({"t": s["t"], "v": [[v["id"], round(v["x"]), round(v["y"], 1), 1 if v["pop"] == "ssi" else 0]
                                          for v in s["vehicles"]],
                       "spat": spat.get(round(s["t"], 1), [])})
    data = {"source": "cvin-v2v-trace/1", "caption": caption(h), "rsus": h.get("rsus") or [], "frames": frames}
    Path(out).write_text(json.dumps(data, separators=(",", ":")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trace")
    ap.add_argument("--out", default="results/figures")
    ap.add_argument("--revocation", action="store_true")
    ap.add_argument("--no-animation", action="store_true")
    a = ap.parse_args()
    h, steps, tx, rx, attacks, revokes = load(a.trace)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = Path(a.trace).name.split(".")[0]
    spacetime(h, steps, out / f"{stem}_spacetime.png")
    latency(h, steps, tx, rx, out / f"{stem}_latency.png")
    if a.revocation:
        revocation(h, tx, rx, revokes, out / f"{stem}_revocation.png")
    if not a.no_animation:
        animate(h, steps, tx, rx, out / f"{stem}_animation.gif")
    replay(h, steps, tx, rx, out / f"{stem}_replay.json")
    print("rendered", stem, "->", out)


if __name__ == "__main__":
    main()
