#!/usr/bin/env python3
"""F7 — one message, anatomised: the signed SSI and PKI BSM packages, field by field.

Signs one real BSM per identity population through the harness's own identity
layers (`sumo_identity_integration.SSIIdentityLayer` / `PKIIdentityLayer`, mock
mobility, the given seed) and draws each package as a stacked bar of bytes per
field. Sizes are the compact-JSON length of each field as the harness packages
it in-process; this is not an over-the-air encoding (IEEE 1609.2 / SAE J2735
use ASN.1 UPER, which is smaller). The figure shows composition, not air time.

Writes:  docs/visual/figures/packet_anatomy/F7_packet_anatomy.png (+ .svg)
         docs/visual/figures/packet_anatomy/F7_packet_anatomy.json  (sizes only)
The JSON records field names, byte counts and, for the identity fields,
a shortened preview. It holds no private keys. The signature and credential
values are public on the air in any case, and only their first characters are
kept.

    python3 packet_anatomy.py [--seed 1]
"""
import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
SUMO = HERE.parent
sys.path.insert(0, str(SUMO))
sys.path.insert(0, str(SUMO.parent))
sys.path.insert(0, str(HERE))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import thesis_figures as rt  # noqa: E402

OUT = HERE.parents[2] / "docs" / "visual" / "figures" / "packet_anatomy"

# Field groups, in drawing order: what the receiver needs for each job.
GROUPS = {
    "payload (BSM fields)": rt.MUTED,
    "signature": rt.INK,
    "identity material": None,   # population colour
    "metadata": rt.GRID,
}


def _size(value):
    if hasattr(value, "_document"):           # VCHandle: the W3C VC document
        value = value._document
    return len(json.dumps(value, separators=(",", ":"), default=str).encode())


def _preview(value, n=28):
    if hasattr(value, "_document"):
        value = value._document
    s = value if isinstance(value, str) else json.dumps(value, separators=(",", ":"), default=str)
    return s[:n] + ("…" if len(s) > n else "")


def packages(seed):
    import sumo_identity_integration as m
    sim = m.SUMOIdentityIntegration(simulation_mode=True, num_vehicles=10, seed=seed)
    sim.start_sumo()
    sim.mobility.step(0.0)
    for vid in sim.mobility.vehicle_ids():
        sim.assign_vehicle_identity(vid)
        sim.vehicle_states[vid] = sim.get_vehicle_state(vid)
    got = {}
    for vid, ident in sim.vehicles.items():
        pop = "ssi" if ident.identity_type == "MOBI_VID" else "pki"
        if pop in got:
            continue
        layer = sim.ssi if pop == "ssi" else sim.pki
        pkg, _ = layer.sign(vid, sim._build_bsm(vid, "BSM", 0.0, False))
        got[pop] = (vid, pkg)
    return got


def classify(key):
    if key == "message":
        return "payload (BSM fields)"
    if key == "signature":
        return "signature"
    if key in ("credential", "certificate", "sender_did"):
        return "identity material"
    return "metadata"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()

    pk = packages(args.seed)
    rows = {}
    for pop, (vid, pkg) in pk.items():
        fields = []
        for k, v in pkg.items():
            fields.append({"field": k, "group": classify(k), "bytes": _size(v),
                           "preview": _preview(v) if classify(k) in ("signature", "identity material") else None})
        rows[pop] = {"vehicle": vid, "total_bytes": sum(f["bytes"] for f in fields), "fields": fields}

    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=HERE,
                            capture_output=True, text=True).stdout.strip()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "F7_packet_anatomy.json").write_text(json.dumps({
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "commit": commit, "seed": args.seed,
        "encoding": "compact JSON as packaged in-process by the harness (not ASN.1 UPER)",
        "populations": rows}, indent=2))

    fig, ax = plt.subplots(figsize=(13, 4.4))
    fig.subplots_adjust(top=0.74, bottom=0.2, left=0.17, right=0.98)
    order = [("ssi", "SSI / MOBI VID"), ("pki", "PKI (IEEE 1609.2-style)")]
    for y, (pop, label) in enumerate(order):
        if pop not in rows:
            continue
        x = 0
        for f in rows[pop]["fields"]:
            col = GROUPS[f["group"]] or rt.POP_COLOR[pop]
            ax.barh(y, f["bytes"], left=x, color=col, edgecolor=rt.SURFACE, lw=1.5, height=0.55)
            if f["bytes"] >= 60:
                ax.text(x + f["bytes"] / 2, y, f"{f['field']}\n{f['bytes']} B", ha="center", va="center",
                        fontsize=7.5, color="white" if col in (rt.INK, rt.MUTED, rt.POP_COLOR[pop]) else rt.INK)
            x += f["bytes"]
        ax.text(x + 12, y, f"{x} B", va="center", fontsize=9, color=rt.INK, fontweight="bold")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([lbl for _, lbl in order], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("bytes (compact JSON, as packaged in-process by the harness)")
    ax.grid(axis="x")
    small = sorted({f["field"] for p in rows.values() for f in p["fields"] if f["bytes"] < 60})
    hs = [plt.Rectangle((0, 0), 1, 1, color=c or rt.SSI) for c in GROUPS.values()]
    ax.legend(hs, [g if c else "identity material (credential / certificate / DID)" for g, c in GROUPS.items()],
              loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=4, fontsize=8)
    rt.stencil_title(
        fig, "One message, anatomised",
        "One real signed BSM per population, field by field. The SSI package carries the sender's DID and its W3C "
        "credential; the PKI package carries an X.509 pseudonym certificate.\n"
        f"Unlabelled narrow fields: {', '.join(small)}. Not an over-the-air size: 1609.2 / J2735 use ASN.1 UPER.",
        f"seed {args.seed} · mock mobility · commit {commit} · sizes in F7_packet_anatomy.json")
    fig.savefig(OUT / "F7_packet_anatomy.svg", bbox_inches="tight")
    rt.save(fig, OUT, "F7_packet_anatomy")
    for pop, r in rows.items():
        print(pop, r["total_bytes"], [(f["field"], f["bytes"]) for f in r["fields"]])


if __name__ == "__main__":
    main()
