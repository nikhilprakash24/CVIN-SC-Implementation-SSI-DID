#!/usr/bin/env python3
"""Render thesis figures from a V2V identity event trace (JSONL).

Input:  a cvin-v2v-trace/1 trace written by `sumo_identity_integration.py --trace PATH`
        (schema: docs/PLAN_SUMO_VISUALISATION.md §3/§7.1 plus docs/visual/TRACE_SCHEMA.md).
Output: PNG + SVG figures in --out (default docs/visual/figures/<trace stem>/).

Every mark on every figure comes from an event in the trace; nothing is
typed in by hand. The caption line printed under each figure names the
trace file, mode, seed, duration and the counts the figure is drawn from, so
a reader can regenerate it.

Figures
  F1  road_frame      The road at one instant: vehicles by identity layer,
                      the broadcasts of that 100 ms step, cold / warm / failed
                      verifications as links.
  F2  contact_matrix  One receiver, every peer it ever heard, over time:
                      first contact (cold, full credential verification) once,
                      then warm per-message signature checks. The
                      "verify-once, check-every-message" architecture in one
                      picture.
  F3  latency_strip   Every receiver-side verification over simulated time
                      against the 10 ms and 100 ms budget lines (log scale).
  F4  attack_board    The injected attacks and their outcome.
  F5  cold_warm_hist  Latency distributions, cold vs warm, per population.
  F6  safety_events   FCW / EEBL events on a timeline, with how many
                      receivers verified each warning.

Style: "academic urban" (docs/visual/VISUAL_PLAN.md §4). Data panels are
conventional (axes, units, n); only the title block uses the stencil voice.
Colour never carries meaning alone: every class is also labelled.
"""
import argparse
import collections
import json
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

# ---------------------------------------------------------------- palette
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SSI = "#2a78d6"      # SSI / MOBI VID (blue)
PKI = "#c99228"      # PKI baseline (ochre)
COLD = "#0b0b0b"     # first contact: full verification
WARM = "#9a9890"     # cached peer: signature check
FAIL = "#d03b3b"     # rejected
SPRAY = "#ff3d00"    # the one accent (alerts, stamps)
GOOD = "#0ca30c"

plt.rcParams.update({
    "font.family": ["DejaVu Sans", "sans-serif"],
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": GRID, "grid.linewidth": 0.6,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "legend.frameon": False,
})

POP_COLOR = {"ssi": SSI, "pki": PKI, "rogue": INK}
POP_LABEL = {"ssi": "SSI / MOBI VID (W3C VC + secp256k1)",
             "pki": "PKI (IEEE 1609.2-style X.509 + ECDSA P-256)",
             "rogue": "rogue (Phase 5 attacker)"}
IDENT_POP = {"MOBI_VID": "ssi", "PKI": "pki", "ROGUE": "rogue"}


# ---------------------------------------------------------------- loading
VEHICLE_KINDS = ("BSM", "FCW", "EEBL")


def _open(path):
    import gzip
    p = str(path)
    return gzip.open(p, "rt") if p.endswith(".gz") else open(p)


def load_trace(path):
    """Read a cvin-v2v-trace/1 trace (docs/PLAN_SUMO_VISUALISATION.md §3, §7.1;
    additive enroll/safety/lane fields in docs/visual/TRACE_SCHEMA.md) into the
    event model the figures use. Plain or .gz.

    Only vehicle messages (BSM, FCW, EEBL) become `tx` here; infrastructure
    messages (SPaT, SignalStateUpdate, TimingPlan) are counted in meta['infra_tx']
    and drawn by the trunk renderer (cv2x-testbed/sumo/render_trace.py)."""
    ev = collections.defaultdict(list)
    header = None
    txs = {}
    pop_of = {}
    last_t = 0.0
    step_i = 0
    infra_tx = 0
    with _open(path) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            kind = r.get("type")
            if kind == "header":
                header = r
            elif kind == "enroll":
                pop_of[r["id"]] = r["pop"]
                ev["enroll"].append({"t": r["t"], "vehicle": r["id"],
                                     "identity": {"ssi": "MOBI_VID", "rogue": "ROGUE"}.get(r["pop"], "PKI"),
                                     "did": r.get("did"), "vin": r.get("vin"), "make": r.get("make"),
                                     "model": r.get("model"), "year": r.get("year")})
            elif kind == "step":
                last_t = max(last_t, r["t"])
                vs = []
                for v in r["vehicles"]:
                    pop_of.setdefault(v["id"], v.get("pop", "pki"))
                    vs.append([v["id"], v["x"], v["y"], v.get("speed", 0.0),
                               v.get("heading", 0.0), v.get("lane", "lane")])
                ev["snap"].append({"t": r["t"], "step": step_i, "v": vs})
                step_i += 1
            elif kind == "tx":
                if r.get("kind") not in VEHICLE_KINDS:
                    infra_tx += 1
                    continue
                rec = {"t": r["t"], "seq": r["msg"], "sender": r["from"], "type": r["kind"],
                       "emergency": r["kind"] != "BSM", "attack": r.get("attack"),
                       "pop": pop_of.get(r["from"], "pki"), "sign_ms": r.get("sign_ms"), "rx": []}
                txs[r["msg"]] = rec
                ev["tx"].append(rec)
            elif kind == "rx":
                tx = txs.get(r["msg"])
                if tx is not None:
                    tx["rx"].append([r["to"], bool(r["ok"]), r.get("path") == "cold",
                                     r.get("verify_ms") or 0.0])
                    if not r["ok"]:  # additive `why` (docs/visual/TRACE_SCHEMA.md)
                        ev["rejections"].append({"t": r["t"], "pop": tx["pop"], "to": r["to"],
                                                 "why": r.get("why") or r.get("reason") or "rejected",
                                                 "attack": tx.get("attack")})
                    if r.get("stages"):
                        ev["stages"].append({"pop": tx["pop"], "total": r.get("verify_ms"),
                                             **r["stages"]})
            elif kind == "safety":
                ev["safety"].append({"t": r["t"], "app": r["app"], "vehicle": r["id"],
                                     "warned": r.get("warned", 0), "target": r.get("target"),
                                     "ttc_s": r.get("ttc_s"), "gap_m": r.get("gap_m")})
            elif kind == "attack":
                ev["attack"].append({"t": r["t"], "name": r["id"], "rejected": bool(r["rejected"]),
                                     "reason": r.get("reason")})
            elif kind == "revoke":
                ev["revoke"].append(r)
    if header is None or header.get("schema") != "cvin-v2v-trace/1":
        sys.exit(f"{path}: not a cvin-v2v-trace/1 trace (no header line)")
    if not ev["enroll"]:
        ev["enroll"] = [{"vehicle": vid, "identity": "MOBI_VID" if p == "ssi" else "PKI"}
                        for vid, p in pop_of.items()]
    envd = header.get("environment", {})
    ev["meta"] = [{
        "mode": "sumo" if header.get("mobility") == "traci" else "simulate",
        "seed": header.get("seed"),
        "duration_s": int(round(last_t + header.get("step_ms", 100) / 1000.0)),
        "step_s": header.get("step_ms", 100) / 1000.0,
        "bsm_rate_hz": int(round(1000.0 / header.get("step_ms", 100))),
        "neighbor_radius_m": header.get("radius_m", 300.0),
        "max_neighbors": header.get("max_receivers", 8),
        "budgets": {"v2v_ms": 100.0, "sig_check_ms": 10.0},
        "commit": (envd.get("git_commit") or "")[:7],
        "rsu": header.get("rsu", False),
        "infra_tx": infra_tx,
        "snapshot_every": 1,
    }]
    return ev


def trace_name(path):
    n = pathlib.Path(path).name
    for suf in (".gz", ".jsonl"):
        n = n[:-len(suf)] if n.endswith(suf) else n
    return n


def provenance(path, meta, extra=""):
    return (f"trace {pathlib.Path(path).name} · mode {meta['mode']} · seed "
            f"{meta['seed']} · {meta['duration_s']} s · "
            f"{meta['bsm_rate_hz']} Hz BSM · {meta['neighbor_radius_m']:.0f} m "
            f"radius · ≤{meta['max_neighbors']} rx/broadcast · commit {meta.get('commit') or 'n/a'}"
            f" · no radio channel, no MAC{extra}")


def stencil_title(fig, title, sub, prov):
    """Title block in the stencil voice; the data panel below stays formal."""
    fig.text(0.012, 0.975, title.upper(), fontsize=15, fontweight="bold",
             color=INK, va="top", ha="left",
             fontfamily="DejaVu Sans Mono")
    fig.text(0.012, 0.93, sub, fontsize=9.5, color=INK2, va="top")
    fig.text(0.012, -0.02, prov, fontsize=7, color=MUTED, va="top")


def stamp(ax, x, y, text, color=SPRAY, size=11, rot=-8):
    ax.text(x, y, text, fontsize=size, fontweight="bold", color=color,
            rotation=rot, ha="center", va="center",
            fontfamily="DejaVu Sans Mono",
            bbox=dict(boxstyle="square,pad=0.25", fc="none", ec=color, lw=1.6))


SAVE_SVG = False


def save(fig, out, name):
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.png", dpi=200, bbox_inches="tight")
    if SAVE_SVG:  # vector copies for the thesis PDF; F3 can reach tens of MB
        fig.savefig(out / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out / name}.png{' (+svg)' if SAVE_SVG else ''}")


# ---------------------------------------------------------------- helpers
def identity_map(ev):
    return {e["vehicle"]: IDENT_POP.get(e["identity"], "pki") for e in ev["enroll"]}


def snapshot_at(ev, t):
    snaps = ev["snap"]
    best = min(snaps, key=lambda s: abs(s["t"] - t))
    return best


def lane_rows(snap):
    lanes = sorted({v[5] for v in snap["v"]})
    return {lane: i for i, lane in enumerate(lanes)}


# ---------------------------------------------------------------- F1
def fig_road_frame(ev, path, out, t, focus=None):
    meta = ev["meta"][0]
    ident = identity_map(ev)
    snap = snapshot_at(ev, t)
    t = snap["t"]
    rows = lane_rows(snap)
    pos = {v[0]: (v[1], rows[v[5]], v[3]) for v in snap["v"]}
    txs = [e for e in ev["tx"] if abs(e["t"] - t) < 1e-6]

    fig, ax = plt.subplots(figsize=(13, 4.6))
    fig.subplots_adjust(top=0.80, bottom=0.3, left=0.05, right=0.99)

    # lanes
    for lane, r in rows.items():
        ax.axhspan(r - 0.42, r + 0.42, color="#f1f0eb", zorder=0)
        ax.text(ax.get_xlim()[0], r + 0.46, lane, fontsize=6.5, color=MUTED,
                va="bottom")

    # links of this step
    n_cold = n_warm = n_fail = 0
    for e in txs:
        if e["sender"] not in pos:
            continue
        sx, sy, _ = pos[e["sender"]]
        for rid, ok, cold, lat in e["rx"]:
            if rid not in pos:
                continue
            rx, ry, _ = pos[rid]
            if not ok:
                ax.plot([sx, rx], [sy, ry], color=FAIL, lw=1.1, ls="--",
                        alpha=0.9, zorder=2)
                n_fail += 1
            elif cold:
                ax.plot([sx, rx], [sy, ry], color=COLD, lw=1.6, alpha=0.9,
                        zorder=3)
                n_cold += 1
            else:
                ax.plot([sx, rx], [sy, ry], color=WARM, lw=0.5, alpha=0.55,
                        zorder=1)
                n_warm += 1

    # vehicles
    for vid, (x, y, spd) in pos.items():
        p = ident.get(vid, "pki")
        c = POP_COLOR[p]
        ax.add_patch(Rectangle((x - 22, y - 0.18), 44, 0.36, fc=c,
                               ec=SPRAY if p == "rogue" else INK,
                               lw=1.6 if p == "rogue" else 0.4, zorder=6 if p == "rogue" else 5))
        if p == "rogue":
            ax.text(x, y - 0.32, "ROGUE", fontsize=7, color=SPRAY, ha="center", va="top",
                    fontweight="bold", fontfamily="DejaVu Sans Mono", zorder=7)
    if focus and focus in pos:
        fx, fy, _ = pos[focus]
        r = meta["neighbor_radius_m"]
        ax.axvspan(fx - r, fx + r, color=SPRAY, alpha=0.06, zorder=0)
        ax.axvline(fx - r, color=SPRAY, lw=0.9, ls=":", zorder=4)
        ax.axvline(fx + r, color=SPRAY, lw=0.9, ls=":", zorder=4)
        ax.text(fx, len(rows) - 0.45, f"±{r:.0f} m radio range of {focus}",
                color=SPRAY, fontsize=7.5, ha="center", va="bottom")
        ax.annotate(focus, (fx, fy), xytext=(fx, fy + 1.2), fontsize=8,
                    color=SPRAY, ha="center",
                    arrowprops=dict(arrowstyle="-", color=SPRAY, lw=0.8))

    xs = [p[0] for p in pos.values()]
    ax.set_xlim(min(xs) - 150, max(xs) + 150)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_yticks([])
    ax.set_xlabel("position along road, m")
    ax.grid(axis="x")

    # legend (labelled, colour never alone)
    hs = [plt.Line2D([], [], marker="s", ms=9, ls="", mfc=SSI, mec=INK, mew=0.4),
          plt.Line2D([], [], marker="s", ms=9, ls="", mfc=PKI, mec=INK, mew=0.4),
          plt.Line2D([], [], color=COLD, lw=1.6),
          plt.Line2D([], [], color=WARM, lw=0.8),
          plt.Line2D([], [], color=FAIL, lw=1.1, ls="--")]
    ax.legend(hs, [f"SSI / MOBI VID vehicle (n={sum(1 for v in pos if ident.get(v)=='ssi')})",
                   f"PKI vehicle (n={sum(1 for v in pos if ident.get(v)=='pki')})",
                   f"cold: first contact, full credential verify ({n_cold})",
                   f"warm: cached peer, signature check ({n_warm})",
                   f"rejected ({n_fail})"],
              loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3,
              fontsize=8)
    stencil_title(fig, f"The road at t = {t:.1f} s",
                  f"One 100 ms step: {len(txs)} signed BSM broadcasts, "
                  f"{n_cold + n_warm + n_fail} receiver-side verifications, "
                  "every one a real cryptographic operation.",
                  provenance(path, meta))
    save(fig, out, f"F1_road_frame_t{int(round(t)):03d}")


# ---------------------------------------------------------------- F2
def fig_contact_matrix(ev, path, out, receiver=None):
    meta = ev["meta"][0]
    ident = identity_map(ev)
    by_rx = collections.defaultdict(list)   # receiver -> [(t, sender, ok, cold)]
    for e in ev["tx"]:
        for rid, ok, cold, lat in e["rx"]:
            by_rx[rid].append((e["t"], e["sender"], ok, cold, lat))
    if not by_rx:
        return
    if receiver is None:
        receiver = max(by_rx, key=lambda r: len({s for _, s, *_ in by_rx[r]}))
    rows = by_rx[receiver]
    peers = []
    first = {}
    for t, s, ok, cold, lat in rows:
        if s not in first:
            first[s] = t
            peers.append(s)
    peers.sort(key=lambda s: first[s])
    yidx = {s: i for i, s in enumerate(peers)}

    fig, ax = plt.subplots(figsize=(13, max(4.0, 0.22 * len(peers) + 2.2)))
    fig.subplots_adjust(top=0.80, bottom=0.12, left=0.12, right=0.99)
    warm_t, warm_y, cold_t, cold_y, fail_t, fail_y = [], [], [], [], [], []
    for t, s, ok, cold, lat in rows:
        y = yidx[s]
        if not ok:
            fail_t.append(t); fail_y.append(y)
        elif cold:
            cold_t.append(t); cold_y.append(y)
        else:
            warm_t.append(t); warm_y.append(y)
    ax.scatter(warm_t, warm_y, s=4, color=WARM, marker="|", lw=0.6,
               label=f"warm signature check (n={len(warm_t)})", zorder=1)
    ax.scatter(cold_t, cold_y, s=70, color=COLD, marker="o", zorder=3,
               label=f"cold: full credential verification at first contact (n={len(cold_t)})")
    if fail_t:
        ax.scatter(fail_t, fail_y, s=50, color=FAIL, marker="x", zorder=4,
                   label=f"rejected (n={len(fail_t)})")
    ax.set_yticks(range(len(peers)))
    ax.set_yticklabels(peers, fontsize=7)
    for s, i in yidx.items():
        ax.get_yticklabels()[i].set_color(POP_COLOR[ident.get(s, "pki")])
    ax.set_xlabel("simulated time, s")
    ax.set_ylabel("peer (label colour: blue = SSI, ochre = PKI)", fontsize=8.5)
    ax.grid(axis="x")
    ax.legend(loc="lower right", fontsize=8)
    stencil_title(fig, "Verify once, check every message",
                  f"Receiver {receiver} ({POP_LABEL[ident.get(receiver, 'pki')]}). A peer's credential "
                  "is fully verified at first contact; each later 10 Hz message is one signature check.\n"
                  "PKI peers re-enter cold whenever their pseudonym certificate rotates "
                  "(every 100 messages); an SSI peer's DID binding is verified once.",
                  provenance(path, meta))
    save(fig, out, f"F2_contact_matrix_{receiver}")


# ---------------------------------------------------------------- F3
def fig_latency_strip(ev, path, out):
    meta = ev["meta"][0]
    series = collections.defaultdict(lambda: ([], []))
    for e in ev["tx"]:
        for rid, ok, cold, lat in e["rx"]:
            if ok and e["pop"] in ("ssi", "pki"):
                k = (e["pop"], "cold" if cold else "warm")
                series[k][0].append(e["t"]); series[k][1].append(lat)
    fig, ax = plt.subplots(figsize=(13, 4.6))
    fig.subplots_adjust(top=0.82, bottom=0.14, left=0.07, right=0.99)
    style = {("ssi", "warm"): dict(color=SSI, s=2, alpha=0.25, marker="."),
             ("pki", "warm"): dict(color=PKI, s=2, alpha=0.25, marker="."),
             ("ssi", "cold"): dict(color=SSI, s=26, alpha=0.95, marker="o", edgecolors=INK, linewidths=0.4),
             ("pki", "cold"): dict(color=PKI, s=26, alpha=0.95, marker="o", edgecolors=INK, linewidths=0.4)}
    for k, (ts, ls) in sorted(series.items()):
        ax.scatter(ts, ls, label=f"{k[0].upper()} {k[1]} (n={len(ts)})",
                   **style[k], zorder=3 if k[1] == "cold" else 1)
    b = meta["budgets"]
    ax.axhline(b["v2v_ms"], color=SPRAY, lw=1.2)
    ax.text(ax.get_xlim()[1], b["v2v_ms"] * 1.15, "100 ms V2V budget",
            color=SPRAY, fontsize=8, ha="right")
    ax.axhline(b["sig_check_ms"], color=SPRAY, lw=1.2, ls="--")
    ax.text(ax.get_xlim()[1], b["sig_check_ms"] * 1.15,
            "10 ms signature-check target", color=SPRAY, fontsize=8, ha="right")
    ax.set_yscale("log")
    ax.set_ylim(0.03, 300)
    ax.set_xlabel("simulated time, s")
    ax.set_ylabel("receiver-side verification latency, ms (log)")
    ax.grid(axis="y", which="both")
    ax.legend(loc="upper left", fontsize=8, ncol=4, markerscale=3)
    stencil_title(fig, "Every verification, against the budget",
                  "Each mark is one measured receiver-side verification "
                  "(time.perf_counter around the cryptographic call). Compute latency "
                  "only: no radio, MAC or channel loss is modelled.",
                  provenance(path, meta))
    save(fig, out, "F3_latency_strip")


# ---------------------------------------------------------------- F4
def fig_attack_board(ev, path, out):
    meta = ev["meta"][0]
    attacks = ev.get("attack", [])
    labels = {
        "tampered_pki_rejected": ("Tampered PKI BSM", "speed field altered after signing"),
        "tampered_ssi_rejected": ("Tampered SSI BSM", "position altered after signing"),
        "stale_pki_rejected": ("Stale PKI BSM", "genuine signature, timestamp 5 s old"),
        "stale_ssi_rejected": ("Stale SSI BSM", "genuine signature, timestamp 5 s old"),
        "replay_pki_rejected": ("Replayed PKI BSM", "accepted once, delivered again"),
        "replay_ssi_rejected": ("Replayed SSI BSM", "accepted once, delivered again"),
        "uncredentialed_sender_rejected": ("Uncredentialed sender", "valid key, DID, no credential"),
    }
    fig, ax = plt.subplots(figsize=(9, 0.62 * len(attacks) + 2.4))
    fig.subplots_adjust(top=0.80, bottom=0.08, left=0.03, right=0.97)
    ax.set_xlim(0, 10); ax.set_ylim(-0.5, len(attacks) - 0.5)
    ax.axis("off")
    for i, a in enumerate(attacks):
        y = len(attacks) - 1 - i
        name, how = labels.get(a["name"], (a["name"], ""))
        ax.add_patch(FancyBboxPatch((0.2, y - 0.36), 9.6, 0.72,
                                    boxstyle="round,pad=0.02", fc="#f1f0eb",
                                    ec=GRID, lw=0.8))
        ax.text(0.5, y + 0.08, name, fontsize=10.5, fontweight="bold", color=INK, va="center")
        ax.text(0.5, y - 0.2, how, fontsize=8, color=INK2, va="center")
        if a["rejected"]:
            stamp(ax, 8.3, y, "REJECTED", color=SPRAY, size=10)
        else:
            stamp(ax, 8.3, y, "ACCEPTED", color=FAIL, size=10, rot=0)
    n_ok = sum(1 for a in attacks if a["rejected"])
    stencil_title(fig, "Attack board",
                  f"{n_ok}/{len(attacks)} injected bad messages rejected at t = "
                  f"{attacks[0]['t'] if attacks else 0:.1f} s. Pass/fail is computed by the "
                  "receiver's real verification path, not asserted.",
                  provenance(path, meta))
    save(fig, out, "F4_attack_board")


# ---------------------------------------------------------------- F5
def fig_cold_warm_hist(ev, path, out):
    meta = ev["meta"][0]
    data = collections.defaultdict(list)
    for e in ev["tx"]:
        for rid, ok, cold, lat in e["rx"]:
            if ok:
                data[(e["pop"], "cold" if cold else "warm")].append(lat)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2), sharey=False)
    fig.subplots_adjust(top=0.80, bottom=0.16, left=0.06, right=0.99, wspace=0.18)
    for ax, pop in zip(axes, ("ssi", "pki")):
        for kind, alpha in (("warm", 0.45), ("cold", 0.9)):
            xs = data.get((pop, kind), [])
            if not xs:
                continue
            xs_s = sorted(xs)
            med = xs_s[len(xs_s) // 2]
            p95 = xs_s[min(len(xs_s) - 1, int(0.95 * len(xs_s)))]
            ax.hist(xs, bins=60, color=POP_COLOR[pop], alpha=alpha,
                    edgecolor="none" if kind == "warm" else INK, lw=0.4,
                    label=f"{kind}: n={len(xs)}, median {med:.3f} ms, p95 {p95:.3f} ms",
                    density=True)
        ax.set_title(POP_LABEL[pop], fontsize=9.5, color=INK2, loc="left")
        ax.set_xlabel("verification latency, ms")
        ax.set_ylabel("density")
        ax.legend(fontsize=8)
        ax.grid(axis="y")
    stencil_title(fig, "Cold vs warm",
                  "First-contact verification (cold) pays for the credential; every "
                  "message after it (warm) pays for one signature check.",
                  provenance(path, meta))
    save(fig, out, "F5_cold_warm_hist")


# ---------------------------------------------------------------- F6
def fig_safety_events(ev, path, out):
    meta = ev["meta"][0]
    events = ev.get("safety", [])
    if not events:
        return
    fig, ax = plt.subplots(figsize=(13, 3.6))
    fig.subplots_adjust(top=0.78, bottom=0.2, left=0.06, right=0.99)
    for app, color, mk in (("FCW", SSI, "v"), ("EEBL", SPRAY, "^")):
        es = [e for e in events if e["app"] == app]
        if es:
            ax.scatter([e["t"] for e in es], [e["warned"] for e in es],
                       color=color, marker=mk, s=60, edgecolors=INK, lw=0.4,
                       label=f"{app} (n={len(es)})", zorder=3)
    for e in events:
        if e["app"] == "EEBL":
            ax.annotate(e["vehicle"], (e["t"], e["warned"]),
                        xytext=(0, 8), textcoords="offset points",
                        fontsize=7, ha="center", color=INK2)
    ax.set_xlabel("simulated time, s")
    ax.set_ylabel("receivers that verified the warning")
    ax.set_xlim(0, meta["duration_s"])
    ax.set_ylim(-0.5, meta["max_neighbors"] + 1)
    ax.grid(axis="y")
    ax.legend(loc="upper left", fontsize=8)
    stencil_title(fig, "Safety messages ride the verified path",
                  "Forward-collision warnings (FCW, TTC < 3 s) and emergency brake lights (EEBL) "
                  "are signed and verified exactly like every other BSM.",
                  provenance(path, meta))
    save(fig, out, "F6_safety_events")


# ---------------------------------------------------------------- F8
def fig_cold_stages(ev, path, out):
    """Where cold latency goes: median per stage, per population (--stage-timers)."""
    import statistics as st
    meta = ev["meta"][0]
    stages = ["freshness_ms", "signature_ms", "credential_ms", "bookkeeping_ms"]
    names = {"freshness_ms": "freshness + replay check", "signature_ms": "message signature",
             "credential_ms": "credential (VC verify + DID binding / X.509 chain + validity + CRL)",
             "bookkeeping_ms": "replay record + cache"}
    shades = {"freshness_ms": GRID, "signature_ms": INK, "credential_ms": None, "bookkeeping_ms": MUTED}
    fig, ax = plt.subplots(figsize=(13, 4.0))
    fig.subplots_adjust(top=0.74, bottom=0.24, left=0.17, right=0.98)
    rows = []
    for y, pop in enumerate(("ssi", "pki")):
        recs = [r for r in ev["stages"] if r["pop"] == pop]
        if not recs:
            continue
        med = {k: st.median(r[k] for r in recs) for k in stages}
        tot = st.median(r["total"] for r in recs if r.get("total") is not None)
        x = 0.0
        for k in stages:
            col = shades[k] or POP_COLOR[pop]
            ax.barh(y, med[k], left=x, color=col, edgecolor=SURFACE, lw=1.2, height=0.55)
            if med[k] > 0.04:
                ax.text(x + med[k] / 2, y, f"{med[k]:.3f}", ha="center", va="center", fontsize=8,
                        color="white" if col in (INK, MUTED, POP_COLOR[pop]) else INK)
            x += med[k]
        ax.text(x + 0.01, y, f"sum of stage medians {x:.3f} ms · median total {tot:.3f} ms · n={len(recs)}",
                va="center", fontsize=8, color=INK2)
        rows.append(pop)
    ax.set_yticks(range(2)); ax.set_yticklabels([POP_LABEL[p] for p in ("ssi", "pki")], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlabel("median ms per stage, cold (first-contact) verifications that succeeded")
    ax.grid(axis="x")
    hs = [plt.Rectangle((0, 0), 1, 1, color=(shades[k] or SSI)) for k in stages]
    ax.legend(hs, [names[k] for k in stages], loc="upper center", bbox_to_anchor=(0.5, -0.3), ncol=2, fontsize=8)
    stencil_title(fig, "Where cold latency goes",
                  "Each first-contact verification split at its stage boundaries. The stage timers add their own "
                  "perf_counter calls, so these totals sit slightly above the single-timer cold medians;\n"
                  "they show proportions, not results of record (register #27).",
                  provenance(path, meta))
    save(fig, out, "F8_cold_stages")


# ---------------------------------------------------------------- F9
def fig_rejections(ev, path, out):
    """Rejections over time by reason (rogue and injected), one row per reason."""
    meta = ev["meta"][0]
    rej = ev["rejections"]
    reasons = sorted({r["why"] for r in rej}, key=lambda w: -sum(1 for r in rej if r["why"] == w))
    fig, ax = plt.subplots(figsize=(13, 1.2 + 0.55 * len(reasons) + 1.6))
    fig.subplots_adjust(top=0.72, bottom=0.2, left=0.16, right=0.98)
    for y, w in enumerate(reasons):
        pts = [r for r in rej if r["why"] == w]
        for pop, mk in (("rogue", "x"), ("ssi", "|"), ("pki", "|")):
            sel = [r["t"] for r in pts if r["pop"] == pop]
            if sel:
                ax.scatter(sel, [y] * len(sel), marker=mk, s=28, color=POP_COLOR[pop] if pop != "rogue" else SPRAY,
                           lw=1.1, label=f"{w}: from {pop} (n={len(sel)})")
    ax.set_yticks(range(len(reasons))); ax.set_yticklabels(reasons, fontsize=9, fontfamily="DejaVu Sans Mono")
    ax.set_ylim(-0.6, len(reasons) - 0.4); ax.invert_yaxis()
    ax.set_xlim(0, meta["duration_s"])
    ax.set_xlabel("simulated time, s")
    ax.grid(axis="x")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=3, fontsize=8)
    modes = sorted({r["attack"] for r in rej if r.get("attack")})
    stencil_title(fig, "Rejected, and why",
                  f"Every receiver-side rejection in the run, by the verifier's reason ({len(rej)} in total). "
                  f"Rogue mode: {', '.join(modes) or 'none'}. The attack-board probes at the end of the run are not "
                  "receiver traffic and are not drawn here.",
                  provenance(path, meta))
    save(fig, out, "F9_rejections")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("trace", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, default=None)
    ap.add_argument("--t", type=float, nargs="*", default=[1.0, 20.0],
                    help="instants for F1 road frames (s)")
    ap.add_argument("--focus", default=None, help="vehicle to ring in F1")
    ap.add_argument("--receiver", default=None, help="receiver for F2")
    ap.add_argument("--only", nargs="*", default=None,
                    help="subset of F1..F6, F8, F9 to render (F8 needs --stage-timers, F9 needs rejections)")
    ap.add_argument("--svg", action="store_true", help="also write SVG")
    args = ap.parse_args()
    global SAVE_SVG
    SAVE_SVG = args.svg

    ev = load_trace(args.trace)
    out = args.out or (pathlib.Path(__file__).resolve().parents[3]
                       / "docs" / "visual" / "figures" / trace_name(args.trace))
    want = set(args.only) if args.only else {"F1", "F2", "F3", "F4", "F5", "F6", "F8", "F9"}
    print(f"rendering from {args.trace} -> {out}")
    if "F1" in want:
        for t in args.t:
            fig_road_frame(ev, args.trace, out, t, args.focus)
    if "F2" in want:
        fig_contact_matrix(ev, args.trace, out, args.receiver)
    if "F3" in want:
        fig_latency_strip(ev, args.trace, out)
    if "F4" in want:
        fig_attack_board(ev, args.trace, out)
    if "F5" in want:
        fig_cold_warm_hist(ev, args.trace, out)
    if "F6" in want:
        fig_safety_events(ev, args.trace, out)
    if "F8" in want and ev["stages"]:
        fig_cold_stages(ev, args.trace, out)
    if "F9" in want and ev["rejections"]:
        fig_rejections(ev, args.trace, out)


if __name__ == "__main__":
    main()
