#!/usr/bin/env python3
"""Layer 5 figures, generated from committed data only (guide rule 1.3.10). Diagrams are drawn from the structures
they depict (the circuit's signals, the agent's modules); data figures name their source file and condition.

    python3 figures/make_figures.py          # write figures/*.png and figures/figures_data.json
    python3 figures/make_figures.py --check  # CI: figures_data.json matches the results files (images not compared)

Palette: the repository's reference palette, slots 1-3 (validated: lightness, chroma, CVD separation pass; slot 3
needs relief, so every mark is direct-labelled or shape-coded). One axis per chart; no bars on a log axis.
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
RES = ROOT / "results"
DATA = HERE / "figures_data.json"
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
FILL1, FILL2, FILL3 = "#e3eefb", "#fde9e0", "#ddf4ea"


def load(name):
    return json.loads((RES / name).read_text())


def derive() -> dict:
    """Every number a figure shows, in one place, so --check can compare it with the results files."""
    zb, gas, att, sb, mb, vb = (load(n) for n in ("zkvin_bench.json", "gas_zk.json", "attacks.json",
                                                   "sigma_bench.json", "manual_burden.json", "vin_bruteforce.json"))
    lc = load("learning_curve.json")
    attacks = {}
    for k, v in {**att["results"], **att["post_hoc_A2_insider"]}.items():
        attacks[k] = {"adv_mean": round(v["adversary_bits"]["mean"], 4), "adv_max": round(v["adversary_bits"]["max"], 4),
                      "adv_min": round(v["adversary_bits"]["min"], 4), "exact": v["adversary_exact_recoveries"],
                      "serv_mean": round(v["honest_service"]["mean"], 4), "serv_min": round(v["honest_service"]["min"], 4)}
    return {
        "sources": {n: load(n)["run"]["commit"] for n in ("zkvin_bench.json", "gas_zk.json", "attacks.json",
                                                         "sigma_bench.json", "manual_burden.json", "vin_bruteforce.json")},
        "zkvin": {"prove_ms": round(zb["prove_ms"]["median"], 1), "verify_ms": round(zb["verify_ms"]["median"], 2),
                  "constraints": mb["measured"]["zkvin_constraints"], "wires": mb["measured"]["zkvin_wires"]},
        "sigma": {k: round(v["median_ms"], 3) for k, v in sb["timing"].items()},
        "gas": gas["gas"],
        "attacks": attacks,
        "manual_hours": {k: round(v["hours"], 1) for k, v in mb["estimated_E"]["time_by_hand"].items()},
        "p_copy": round(mb["estimated_E"]["p_one_presentation_copied_without_error"], 6),
        "vin": {"seconds": round(vb["elapsed_s"], 2), "space": vb["space"]},
        "learning_curve": lc["curve"],
        "sample_proof": zb["sample_proof"], "sample_signals": zb["sample_public_signals"],
    }


# ------------------------------------------------------------------ drawing helpers

def plt_setup():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                         "xtick.color": INK2, "ytick.color": INK2, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
                         "savefig.facecolor": SURFACE, "axes.spines.top": False, "axes.spines.right": False})
    return plt


def box(ax, x, y, w, h, text, fill=FILL1, edge=S1, size=9, bold=False):
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fill, ec=edge, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=INK,
            fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, x1, y1, x2, y2, text="", color=INK2, size=8, rad=0.0):
    from matplotlib.patches import FancyArrowPatch
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12, color=color, lw=1.3,
                                 connectionstyle=f"arc3,rad={rad}"))
    if text:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, text, ha="center", va="bottom", fontsize=size, color=INK2)


def canvas(plt, w, h, xlim, ylim, title):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=12, color=INK, fontweight="bold")
    return fig, ax


def save(fig, name, note=None):
    if note:
        fig.text(0.01, -0.02, note, fontsize=7, color=INK2, ha="left", va="top")
    fig.savefig(HERE / name, dpi=160, bbox_inches="tight")


# ------------------------------------------------------------------ figures

def fig01_pipeline(plt, d):
    fig, ax = canvas(plt, 12, 4.6, (0, 12), (0, 5), "Figure 1. ZK-VIN from statement to an on-chain decision (Groth16)")
    steps = [(0.2, "Statement\n'my VIN's maker is\nauthorised, year ≥ t,\nregion = r'"), (2.2, "Circuit\nzkvin.circom\n(circom 2.2.2)"),
             (4.2, f"R1CS\n{d['zkvin']['constraints']:,} constraints\n{d['zkvin']['wires']:,} wires"),
             (6.2, "Setup\npowers of tau +\ncircuit keys\n(dev, INSECURE)"), (8.2, "Proving key\nVerification key\nSolidity verifier")]
    for x, t in steps:
        box(ax, x, 3.0, 1.7, 1.5, t, FILL1, S1, 8.5)
    for i in range(len(steps) - 1):
        arrow(ax, steps[i][0] + 1.7, 3.75, steps[i + 1][0], 3.75)
    box(ax, 0.2, 0.6, 2.2, 1.6, "Private witness\nVIN (17 chars), model year,\nsalt, Merkle path", FILL2, S2, 8.5)
    box(ax, 3.2, 0.6, 2.2, 1.6, f"Prove (Steward)\nmedian {d['zkvin']['prove_ms']:.0f} ms\nproof: 8 field elements", FILL3, S3, 8.5)
    box(ax, 6.2, 0.6, 2.3, 1.6, f"Verify off chain\nsnarkjs, median\n{d['zkvin']['verify_ms']:.1f} ms (M0)", FILL1, S1, 8.5)
    box(ax, 9.2, 0.6, 2.6, 1.6, f"Verify on chain\nZkVinGate.admit\n{d['gas']['admit_with_groth16']:,} gas (M1)\nnullifier per scope", FILL1, S1, 8.5)
    arrow(ax, 2.4, 1.4, 3.2, 1.4)
    arrow(ax, 5.4, 1.4, 6.2, 1.4)
    ax.text(5.8, 0.35, "π + public signals", ha="center", fontsize=8, color=INK2)
    arrow(ax, 8.5, 1.4, 9.2, 1.4)
    arrow(ax, 9.05, 3.0, 4.6, 2.2, "proving key", rad=0.15)
    arrow(ax, 9.3, 3.0, 10.4, 2.2, "verifier")
    save(fig, "fig01_zk_pipeline.png", f"Sources: results/zkvin_bench.json, results/gas_zk.json (commit {d['sources']['gas_zk.json']}).")


def fig02_sigma(plt, d):
    fig, ax = canvas(plt, 10, 5.4, (0, 10), (0, 6), "Figure 2. A sigma protocol (Schnorr): commit, challenge, respond")
    box(ax, 0.3, 4.9, 2.6, 0.8, "Prover knows x\nP = x·G is public", FILL3, S3, 9, True)
    box(ax, 7.1, 4.9, 2.6, 0.8, "Verifier knows P", FILL1, S1, 9, True)
    for x in (1.6, 8.4):
        ax.plot([x, x], [1.75, 4.9], color=GRID, lw=2)
    arrow(ax, 1.6, 4.2, 8.4, 4.2, "1. commit   R = k·G   (k random, used once)")
    arrow(ax, 8.4, 3.2, 1.6, 3.2, "2. challenge   e  (random; or e = H(P, R, context) — Fiat–Shamir)")
    arrow(ax, 1.6, 2.2, 8.4, 2.2, "3. respond   s = k + e·x  mod n")
    box(ax, 6.2, 0.7, 3.5, 0.9, "check  s·G  =  R + e·P", FILL1, S1, 10, True)
    ax.text(0.2, 0.55, "Completeness: honest s always passes.\nSpecial soundness: two answers to one R give x = (s1−s2)/(e1−e2).\n"
            "Zero knowledge (honest verifier): pick e, s first, set R = s·G − e·P;\nthe transcript verifies without x. "
            "All three are tests in tests/test_zkid.py.", fontsize=8.2, color=INK2, va="bottom")
    save(fig, "fig02_sigma_protocol.png")


def fig03_circuit(plt, d):
    fig, ax = canvas(plt, 12, 5.6, (0, 12), (0, 6.2), "Figure 3. The ZK-VIN circuit: what is constrained, and what stays private")
    box(ax, 0.2, 4.6, 2.2, 1.2, "vin[17]\n(private, 6-bit codes)", FILL2, S2, 8.5)
    box(ax, 0.2, 3.0, 2.2, 1.0, "modelYear, salt\n(private)", FILL2, S2, 8.5)
    box(ax, 0.2, 1.4, 2.2, 1.0, "Merkle path\n(private)", FILL2, S2, 8.5)
    box(ax, 3.1, 4.6, 2.1, 1.2, "Num2Bits(6) ×17\npack → vinPacked\nWMI = first 3", FILL1, S1, 8.5)
    box(ax, 6.0, 4.6, 2.4, 1.2, "Poseidon(vinPacked,\nmodelYear, region, salt)", FILL1, S1, 8.5)
    box(ax, 6.0, 2.9, 2.4, 1.2, "MerkleInclusion(4)\nPoseidon(2) per level", FILL1, S1, 8.5)
    box(ax, 6.0, 1.3, 2.4, 1.1, "GreaterEqThan(12)\nmodelYear ≥ minModelYear", FILL1, S1, 8.5)
    box(ax, 6.0, 0.1, 2.4, 0.9, "Poseidon(salt, scope)", FILL1, S1, 8.5)
    for y, t in ((5.2, "= commitment  (anchored on chain)"), (3.5, "= mfrRoot  (authorised makers)"),
                 (1.85, "= 1  (threshold holds)"), (0.55, "→ nullifier  (public output)")):
        box(ax, 9.1, y - 0.42, 2.8, 0.84, t, FILL3, S3, 8.5)
        arrow(ax, 8.4, y, 9.1, y)
    arrow(ax, 2.4, 5.2, 3.1, 5.2)
    arrow(ax, 5.2, 5.2, 6.0, 5.2)
    arrow(ax, 5.2, 4.8, 6.0, 3.6, "WMI")
    arrow(ax, 2.4, 3.5, 6.0, 4.75, rad=-0.1)
    arrow(ax, 2.4, 3.3, 6.0, 1.85)
    arrow(ax, 2.4, 1.9, 6.0, 3.2)
    arrow(ax, 2.4, 3.1, 6.0, 0.55, rad=0.1)
    ax.text(0.2, 0.2, f"{d['zkvin']['constraints']:,} constraints. region, scope, challenge are public inputs.",
            fontsize=8.5, color=INK2)
    save(fig, "fig03_zkvin_circuit.png", "Source: 5_zkp-agent-identity/circuits/zkvin.circom; counts from artifacts/circuit_info.txt.")


def fig04_spectrum(plt, d):
    rows = [("Plaintext attribute", "the value", "yes", "yes", "Phase 1 L0"),
            ("Unsalted hash on chain", f"the value, by enumeration ({d['vin']['seconds']:.1f} s for 10^6 VINs)", "yes", "yes", "measured here"),
            ("Salted hash (commitment)", "equality with a value it already has", "if salt shown", "yes (same hash)", "Phase 1 L3"),
            ("SD-JWT-style digests", "each disclosed claim, exactly", "for disclosed claims", "yes", "Phase 1 VC layer"),
            ("ZK predicate proof", "one bit per predicate", "no", "no (scoped nullifier)", "ZK-VIN, zkid"),
            ("ZK + Steward budget", "≤ 3.0 bits in total, even if all collude", "no", "no", "this layer")]
    fig, ax = plt.subplots(figsize=(12, 3.6))
    ax.axis("off")
    ax.set_title("Figure 4. The disclosure spectrum: what a verifier learns about a vehicle attribute", loc="left",
                 fontsize=12, fontweight="bold", color=INK)
    t = ax.table(cellText=[list(r) for r in rows], colLabels=["Mechanism", "Verifier learns", "Value recoverable",
                 "Linkable", "Where"], loc="center", cellLoc="left", colWidths=[0.19, 0.37, 0.15, 0.15, 0.14])
    t.auto_set_font_size(False)
    t.set_fontsize(8.2)
    t.scale(1, 1.55)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(GRID)
        if r == 0:
            cell.set_facecolor(FILL1)
            cell.set_text_props(fontweight="bold")
        elif r >= 5:
            cell.set_facecolor(FILL3)
    save(fig, "fig04_disclosure_spectrum.png", "Unsalted-hash time: results/vin_bruteforce.json (M0). Budget: results/attacks.json.")


def fig05_architecture(plt, d):
    fig, ax = canvas(plt, 12, 6.6, (0, 12), (-0.3, 7), "Figure 5. The Steward: an agent wrapping an identity. The model proposes; the kernel disposes")
    box(ax, 0.2, 5.6, 2.4, 1.0, "Owner\n(plain English)", FILL2, S2, 9, True)
    box(ax, 9.4, 5.6, 2.4, 1.0, "Verifier / RSU /\ninsurer / other agent", FILL2, S2, 9, True)
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((0.4, 0.9), 11.2, 4.3, boxstyle="round,pad=0.02,rounding_size=0.15", fc="none", ec=INK2, lw=1.2, ls="--"))
    ax.text(0.6, 4.95, "Steward  (own DID + delegation credential from the owner)", fontsize=9, color=INK2)
    box(ax, 0.8, 3.3, 2.6, 1.3, "Compiler\ngrammar, or a language\nmodel under a schema", FILL1, S1, 8.5)
    box(ax, 4.2, 3.3, 3.4, 1.3, "Policy kernel (deterministic)\nsigned policy · rules · consent\nleakage budget (simulatable)", FILL3, S3, 8.5, True)
    box(ax, 8.4, 3.3, 2.9, 1.3, "Interpreter\nmessage → structured\nrequest (may be a model)", FILL1, S1, 8.5)
    box(ax, 0.8, 1.2, 2.6, 1.5, "Vault\nkeys, salts, values\nno getter; sealed repr", FILL2, S2, 8.5)
    box(ax, 4.2, 1.2, 1.6, 1.5, "Proof engine\nzkid / Groth16", FILL1, S1, 8.5)
    box(ax, 6.0, 1.2, 1.6, 1.5, "Responder\nQ-learning,\nshielded", FILL1, S1, 8.5)
    box(ax, 8.4, 1.2, 2.9, 1.5, "Audit log\nhash chain + Merkle root\n(anchorable)", FILL1, S1, 8.5)
    arrow(ax, 1.4, 5.6, 1.9, 4.6)
    ax.text(2.0, 5.3, "intent", fontsize=8, color=INK2)
    arrow(ax, 3.4, 3.95, 4.2, 3.95, "draft ≤ signed")
    arrow(ax, 10.6, 5.6, 9.9, 4.6)
    ax.text(10.5, 5.0, "message", fontsize=8, color=INK2)
    arrow(ax, 8.4, 3.95, 7.6, 3.95, "request")
    arrow(ax, 6.8, 3.3, 6.8, 2.7)
    ax.text(6.9, 2.9, "permitted", fontsize=8, color=INK2)
    arrow(ax, 5.0, 3.3, 5.0, 2.7)
    ax.text(5.1, 2.9, "decision", fontsize=8, color=INK2)
    arrow(ax, 3.4, 1.95, 4.2, 1.95)
    ax.text(3.8, 1.0, "proofs out,\nvalues never", ha="center", fontsize=7.5, color=INK2)
    arrow(ax, 7.6, 1.95, 8.4, 1.95, "logged")
    box(ax, 0.6, 0.0, 5.0, 0.7, "Chain: ERC-1056 · MOBI VID · ZkVinGate", FILL1, S1, 8.5)
    box(ax, 6.4, 0.0, 5.0, 0.7, "W3C VC layer: delegation credential, verifier", FILL1, S1, 8.5)
    save(fig, "fig05_agent_architecture.png", "Code: 5_zkp-agent-identity/steward/. Each module's claim is a test in tests/test_steward.py.")


def fig06_hexwall(plt, d):
    proof = json.dumps(d["sample_proof"]) + "  " + json.dumps(d["sample_signals"])
    lines = [proof[i:i + 120] for i in range(0, len(proof), 120)]
    fig, ax = plt.subplots(figsize=(12, 2.6))
    ax.axis("off")
    ax.set_title("Figure 6. One ZK-VIN proof and its public signals, as a person would have to copy them", loc="left",
                 fontsize=12, fontweight="bold", color=INK)
    ax.text(0, 1, "\n".join(lines), family="DejaVu Sans Mono", fontsize=7.2, color=INK2, va="top", transform=ax.transAxes)
    ax.text(0.0, -0.05, f"{len(proof):,} characters.  Chance of copying them with no error at 0.6 % per character: "
            f"{d['p_copy'] * 100:.2f} % (status E).  The Steward produces and checks this in {d['zkvin']['prove_ms']:.0f} ms + "
            f"{d['zkvin']['verify_ms']:.0f} ms.", ha="left", va="top", fontsize=9.5, color=INK, transform=ax.transAxes)
    save(fig, "fig06_hex_wall.png", "Proof from results/zkvin_bench.json (sample_proof); error rate per docs/zkp/SOURCES_ZKP.md [PANKO-BASIC].")


def fig07_manual(plt, d):
    zb_ms = {"Schnorr verification (one signature-sized proof)": d["sigma"]["schnorr_verify"],
             "6-bit threshold proof, prove (model year >= t)": d["sigma"]["threshold_prove_6bit"],
             "6-bit threshold proof, verify": d["sigma"]["threshold_verify_6bit"],
             "ZK-VIN Groth16 proof, prove (E: textbook algorithm)": d["zkvin"]["prove_ms"],
             "ZK-VIN Groth16 proof, verify (E: four pairings)": d["zkvin"]["verify_ms"]}
    names = list(zb_ms)
    fig, ax = plt.subplots(figsize=(11, 4.4))
    ys = range(len(names))
    hand = [d["manual_hours"][n] * 3600 for n in names]
    agent = [zb_ms[n] / 1000 for n in names]
    for y, h, a in zip(ys, hand, agent):
        ax.plot([a, h], [y, y], color=GRID, lw=2, zorder=1)
    ax.scatter(hand, ys, s=70, color=S2, marker="s", zorder=3, edgecolor=SURFACE, linewidth=2, label="by hand (estimate, E)")
    ax.scatter(agent, ys, s=70, color=S1, marker="o", zorder=3, edgecolor=SURFACE, linewidth=2, label="by the Steward (measured, M0)")
    for y, h, a in zip(ys, hand, agent):
        ax.text(h * 1.6, y, f"{h / 3600 / 2000:,.1f} working years" if h > 3600 * 2000 else f"{h / 3600:,.0f} h",
                va="center", fontsize=8.5, color=INK)
        ax.text(a / 1.6, y, f"{a * 1000:,.0f} ms" if a >= 0.01 else f"{a * 1000:.1f} ms", va="center", ha="right", fontsize=8.5, color=INK)
    ax.set_xscale("log")
    ax.set_xlim(1e-4, 1e14)
    ax.set_yticks(list(ys), [n.replace(" (E: textbook algorithm)", "*").replace(" (E: four pairings)", "*") for n in names])
    ax.invert_yaxis()
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_xlabel("seconds (log scale)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.17), ncol=2, frameon=False, fontsize=8.5)
    fig.subplots_adjust(bottom=0.3)
    ax.set_title("Figure 7. The same cryptography by hand and by the agent", loc="left", fontsize=12, fontweight="bold")
    save(fig, "fig07_manual_vs_agent.png", "Hand: results/manual_burden.json (counts measured; rates cited, status E; * = operation count also E). "
         "Agent: results/sigma_bench.json, results/zkvin_bench.json (M0).")


def fig08_attack(plt, d):
    defences = [("none", "No defence"), ("static_cap", "Static cap (2 per verifier)"), ("budget_only", "Global budget only"),
                 ("steward_fixed", "Steward, fixed responder"), ("steward", "Steward, learned responder"),
                 ("steward_no_budget", "Learner without kernel budget")]
    variants = [("single", "single identity", S1, "o"), ("sybil", "Sybil split", S2, "s"), ("insider", "accredited insider (post hoc)", S3, "D")]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
    for i, (key, label) in enumerate(defences):
        for j, (v, vl, col, mk) in enumerate(variants):
            r = d["attacks"][f"{key}|{v}"]
            y = i + (j - 1) * 0.22
            a1.plot([r["adv_min"], r["adv_max"]], [y, y], color=col, lw=1.6, alpha=0.6)
            a1.scatter([r["adv_mean"]], [y], color=col, marker=mk, s=40, zorder=3, edgecolor=SURFACE, linewidth=1.5,
                       label=vl if i == 0 else None)
            a2.scatter([r["serv_mean"] * 100], [y], color=col, marker=mk, s=40, zorder=3, edgecolor=SURFACE, linewidth=1.5)
            a2.plot([r["serv_min"] * 100, r["serv_mean"] * 100], [y, y], color=col, lw=1.6, alpha=0.6)
    a1.axvline(3.0, color=INK2, ls="--", lw=1)
    a1.text(3.0, 1.01, "budget 3.0 bits", fontsize=8, color=INK2, ha="center", va="bottom", transform=a1.get_xaxis_transform())
    a1.axvline(5.0, color=GRID, lw=1)
    a1.text(5.0, 1.01, "exact value (5 bits)", fontsize=8, color=INK2, ha="center", va="bottom", transform=a1.get_xaxis_transform())
    a2.axvline(90, color=INK2, ls="--", lw=1)
    a2.text(90, 1.01, "Z-E6 floor 90 %", fontsize=8, color=INK2, ha="center", va="bottom", transform=a2.get_xaxis_transform())
    a1.set_yticks(range(len(defences)), [l for _, l in defences])
    a1.set_ylim(len(defences) - 0.5, -0.5)
    a1.set_xlabel("bits the adversary learns about the model year (mean, range over 30 seeds)")
    a2.set_xlabel("honest requests served, % (mean; line to the worst seed)")
    a1.set_xlim(-0.2, 5.4)
    a2.set_xlim(25, 102)
    for a in (a1, a2):
        a.grid(axis="x", color=GRID, lw=0.6)
    a1.legend(loc="upper center", bbox_to_anchor=(1.05, -0.2), ncol=3, frameon=False, fontsize=8.5)
    fig.subplots_adjust(top=0.84, bottom=0.3, wspace=0.08)
    fig.suptitle("Figure 8. The twenty-questions attack: leakage and honest service under six defences", x=0.01, ha="left",
                 fontsize=12, fontweight="bold")
    save(fig, "fig08_attack_leakage.png", f"Simulation, seeds 1-30, Plan 1 amendment A1 (A2 post hoc). Source: results/attacks.json, commit {d['sources']['attacks.json']}.")


def fig09_learning(plt, d):
    c = d["learning_curve"]
    x = [p["episodes"] for p in c]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.6))
    a1.plot(x, [p["adversary_bits_mean"] for p in c], color=S2, lw=2, marker="s", ms=5)
    a2.plot(x, [p["honest_service_mean"] * 100 for p in c], color=S1, lw=2, marker="o", ms=5)
    a1.set_ylabel("adversary bits (held-out mean)")
    a2.set_ylabel("honest service, % (held-out mean)")
    for a in (a1, a2):
        a.set_xlabel("training episodes")
        a.grid(color=GRID, lw=0.6)
    a1.set_ylim(bottom=0)
    a2.set_ylim(80, 100)
    fig.suptitle("Figure 9. The Steward's responder learning (held-out seeds 20000-20029, single and Sybil variants)",
                 x=0.01, ha="left", fontsize=12, fontweight="bold")
    save(fig, "fig09_learning_curve.png", "Simulation. Source: results/learning_curve.json; training seeds 10000-12999.")


def fig10_gas(plt, d):
    g = d["gas"]
    rows = [("Schnorr proof of key knowledge (tx)", g["schnorr_prove_tx"], S1),
            ("Anchor a VIN commitment", g["anchor_commitment"], S1),
            ("ERC-1056 createIdentity (Phase 1, #6)", 52594, INK2),
            ("Groth16 verify (view, estimate)", g["verify_proof_view_estimate"], S1),
            ("ZkVinGate.admit (Groth16 + checks)", g["admit_with_groth16"], S2)]
    fig, ax = plt.subplots(figsize=(10, 3.6))
    ys = range(len(rows))
    ax.barh(list(ys), [r[1] for r in rows], color=[r[2] for r in rows], height=0.55, edgecolor=SURFACE, linewidth=2)
    for y, r in zip(ys, rows):
        ax.text(r[1] + 4000, y, f"{r[1]:,}", va="center", fontsize=9, color=INK)
    ax.set_yticks(list(ys), [r[0] for r in rows])
    ax.invert_yaxis()
    ax.set_xlabel("gas (exact receipt gasUsed; view rows are eth_estimateGas incl. 21,000 base)")
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(__import__("matplotlib").ticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_xlim(0, max(r[1] for r in rows) * 1.18)
    ax.set_title("Figure 10. What zero knowledge costs on chain (M1)", loc="left", fontsize=12, fontweight="bold")
    save(fig, "fig10_gas.png", f"Source: results/gas_zk.json, commit {d['sources']['gas_zk.json']}; ERC-1056 row: register #6.")


def fig11_tables(plt, d):
    t = json.loads((HERE / "ssi_tables.json").read_text())
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(13, 13), gridspec_kw={"height_ratios": [1.05, 1]})
    for ax, title, rows, cols, keys, widths in (
            (a1, t["table_a_title"], t["table_a"], ["Function", "Requirement", "This build", "Status"],
             ["function", "requirement", "cvin", "status"], [0.17, 0.27, 0.45, 0.11]),
            (a2, t["table_b_title"], t["table_b"], ["Property", "Strict SSI asks", "Default here", "Strict mode", "Constraint"],
             ["property", "strict", "default", "strict_mode", "constraint"], [0.13, 0.24, 0.25, 0.08, 0.30])):
        ax.axis("off")
        ax.set_title(title, loc="left", fontsize=10.5, fontweight="bold", color=INK)
        import textwrap
        wrapped = [[textwrap.fill(str(r[k]), max(8, int(w * 150))) for k, w in zip(keys, widths)] for r in rows]
        tb = ax.table(cellText=wrapped, colLabels=cols, loc="upper center", cellLoc="left", colWidths=widths)
        tb.auto_set_font_size(False)
        tb.set_fontsize(7.4)
        base = 0.052
        for (r, c), cell in tb.get_celld().items():
            lines = 1 if r == 0 else max(t.count("\n") + 1 for t in wrapped[r - 1])
            cell.set_height(base * (0.75 + 0.45 * lines))
            cell.PAD = 0.03
        for (r, c), cell in tb.get_celld().items():
            cell.set_edgecolor(GRID)
            if r == 0:
                cell.set_facecolor(FILL1)
                cell.set_text_props(fontweight="bold")
            elif cols[c] in ("Status", "Strict mode"):
                txt = cell.get_text().get_text()
                cell.set_facecolor(FILL3 if txt.startswith(("Built", "Yes")) else FILL2)
    fig.suptitle("Figure 11. An identity-management system first, SSI-compatible by extension", x=0.01, ha="left",
                 fontsize=12, fontweight="bold")
    save(fig, "fig11_ssi_tables.png", "Data: figures/ssi_tables.json (Report C tables C-1, C-2).")


def fig12_loop(plt, d):
    import math
    fig, ax = canvas(plt, 9.5, 8.8, (-5.2, 5.2), (-4.4, 4.4), "Figure 12. The closed loop: identity for machines, machines for identity")
    labels = ["Vehicles, IoV and agents\nneed identities\n(Phase 1: 9 standards, W3C, MOBI)",
              "Privacy needs\nzero knowledge\n(SC-12, AR-5 → ZK-VIN)",
              "ZK is not for hands\n(Fig. 7: years per proof;\n0.04 % clean copy)",
              "So a permanent custodian:\nan agent wrapping the identity\n(the Steward)",
              "A custodian must be bounded\nand adaptive (kernel + budget;\ntwenty questions, Fig. 8)",
              "The agent needs an identity:\nDID + delegation VC +\nrevocation + audit"]
    n = len(labels)
    pts = []
    for i, lab in enumerate(labels):
        a = math.pi / 2 - 2 * math.pi * i / n
        x, y = 3.45 * math.cos(a), 3.45 * math.sin(a)
        pts.append((x, y))
        col, fill = ((S1, FILL1), (S3, FILL3), (S2, FILL2))[i % 3]
        box(ax, x - 1.45, y - 0.62, 2.9, 1.24, lab, fill, col, 8)
    for i in range(n):
        a1_ = math.pi / 2 - 2 * math.pi * i / n - math.radians(14)
        a2_ = math.pi / 2 - 2 * math.pi * (i + 1) / n + math.radians(14)
        ax.annotate("", xy=(1.7 * math.cos(a2_), 1.7 * math.sin(a2_)), xytext=(1.7 * math.cos(a1_), 1.7 * math.sin(a1_)),
                    arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.6, connectionstyle="arc3,rad=-0.3"))
    ax.text(0, 0, "the same\nidentity\nstack at\nboth ends", ha="center", va="center", fontsize=9, color=INK, fontweight="bold")
    save(fig, "fig12_full_circle.png")


FIGS = [fig01_pipeline, fig02_sigma, fig03_circuit, fig04_spectrum, fig05_architecture, fig06_hexwall, fig07_manual,
        fig08_attack, fig09_learning, fig10_gas, fig11_tables, fig12_loop]


def check(data_path=DATA) -> bool:
    current = derive()
    try:
        stored = json.loads(pathlib.Path(data_path).read_text())
    except FileNotFoundError:
        return False
    return stored == json.loads(json.dumps(current))


def main():
    if "--check" in sys.argv:
        ok = check()
        print("figures data current" if ok else "figures data STALE: run python3 figures/make_figures.py")
        sys.exit(0 if ok else 1)
    d = derive()
    DATA.write_text(json.dumps(d, indent=1) + "\n")
    plt = plt_setup()
    for f in FIGS:
        f(plt, d)
        plt.close("all")
    print(f"wrote {len(FIGS)} figures and {DATA.name}")


if __name__ == "__main__":
    main()
