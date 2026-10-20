#!/usr/bin/env python3
"""Figures for docs/REVIEW_CV2X_TESTBED_LINEAGE.md.

Three figures, generated from the plan-vs-actual assessment encoded below so
the figure and the review text cannot drift apart:

  review_roadmap_timeline.png   - the roadmap's phases: planned week vs actual state
  review_criteria_matrix.png    - every success criterion in the three design docs, its status
  review_architecture.png       - as-designed (VID1 spec) vs as-built (trunk) layer stack

Status vocabulary (single source, used by all three):
  MET      criterion satisfied with trunk-traceable evidence
  PARTIAL  satisfied in part, or satisfied at a different layer than planned
  OPEN     not attempted yet, still in scope
  DROPPED  removed from scope (recorded in docs/SCOPE_CHANGES.md)

Colours follow the validated reference palette (blue for progress magnitude;
status colours carry a glyph+label so colour is never the only channel).
"""
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = pathlib.Path(__file__).resolve().parent
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, BLUE_L = "#2a78d6", "#9ec5f4"
STATUS = {  # colour, glyph
    "MET": ("#2a78d6", "✓"), "PARTIAL": ("#eda100", "◐"),
    "OPEN": ("#c3c2b7", "○"), "DROPPED": ("#d03b3b", "✗"),
}
plt.rcParams.update({"font.family": ["DejaVu Sans", "sans-serif"], "figure.facecolor": SURFACE,
                     "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE, "text.color": INK,
                     "axes.edgecolor": AXIS, "xtick.color": MUTED, "ytick.color": INK2})

# ---------------------------------------------------------------- data ----
# CV2X_REALISTIC_ROADMAP.md (2025-11-10): phase, planned window (weeks from
# 2025-11-10), actual state on the merged trunk (2026-09-25), evidence.
PHASES = [
    ("P1 Identity systems (VID I/II, VC, centralized)", 0, 0, "MET", "contracts + VC layer + 32 MOBI tests"),
    ("P2 CV2X protocol stack + PKI provider", 0, 0, "MET", "cv2x_stack.py, pki_identity.py, IEEE 1609.2 model"),
    ("P3 Comparison framework + use cases", 0, 0, "MET", "12/12 use cases; 4_comparison-framework"),
    ("P4 SUMO integration (50 vehicles, FCW/EEBL/IMA)", 1, 1, "PARTIAL", "run in --simulate mode (mock mobility): 50 veh, 35 SSI + 15 PKI, 30 seeds; real TraCI mode unrun (no SUMO binary)"),
    ("P5 Safety-critical scenarios (5)", 2, 2, "PARTIAL", "safety apps referenced in the harness; scenarios realised as 12 use cases, not as SUMO scenarios"),
    ("P6 Large-scale (100/200 vehicles, mixed PKI+VID)", 3, 3, "PARTIAL", "mixed 35 SSI + 15 PKI fleet at 50 vehicles; 100/200 not attempted"),
    ("P7 Attack scenarios (Sybil, position, replay)", 4, 4, "PARTIAL", "68-scenario Hardhat security harness across 9 standards + harness-level run_attack_tests; position falsification dropped (SC-01)"),
    ("P8 Real hardware (OBD-II, RSU)", 5, 6, "OPEN", "optional in the roadmap; not attempted"),
]

# Success criteria from the three design documents.
CRITERIA = [
    # (document, criterion, status, evidence)
    ("Roadmap", "BSM signing < 100 ms", "MET", "0.054 ms PKI / 0.401 ms ERC-1056 (register #21)"),
    ("Roadmap", "BSM verification < 10 ms", "PARTIAL", "0.32 ms off-chain; 18.2 ms if chain read per message (#21)"),
    ("Roadmap", "Identity resolution < 50 ms", "MET", "0.009 ms in-process (M0); M2 unmeasured"),
    ("Roadmap", "SUMO 50+ vehicles", "PARTIAL", "50 vehicles run with mock mobility (--simulate), 30 seeds; real SUMO/TraCI unrun"),
    ("Roadmap", "Safety-app latency < 100 ms e2e", "PARTIAL", "identity part measured (sign/verify, cold/warm) in the harness; safety-app decision path not timed"),
    ("Roadmap", "Prevent Sybil (MOBI VID)", "MET", "manufacturer-authorized birth; security harness"),
    ("Roadmap", "Position-falsification detection > 95%", "DROPPED", "SC-01"),
    ("Roadmap", "Replay prevention 100%", "MET", "challenge/domain + timestamp checks; security harness"),
    ("Roadmap", "Misbehaviour reporting functional", "OPEN", "no reporting path implemented"),
    ("Roadmap", "Centralized vs MOBI VID gap quantified", "MET", "PKI vs ERC-1056 experiment (#21)"),
    ("Roadmap", "Privacy analysis complete", "DROPPED", "SC-02 (deferred, partially subsumed)"),
    ("Roadmap", "Cost analysis complete", "MET", "nine-standard gas table (#25)"),
    ("Roadmap", "Trust-model comparison documented", "PARTIAL", "qualitative in architecture doc; rubric mapping started"),
    ("VID I spec", "Birth registration < 5 s", "MET", "16.9 ms median on Hardhat (M1)"),
    ("VID I spec", "DID resolution < 100 ms", "MET", "0.009 ms (M0)"),
    ("VID I spec", "100% test coverage, critical paths", "PARTIAL", "219 tests; coverage not measured"),
    ("VID I spec", "Gas < $5 / registration", "PARTIAL", "298,941 gas (MOBI-VID-V2 birth); fiat depends on gas price (register #20)"),
    ("VID I spec", "Zero VIN leakage on-chain", "MET", "vinHash + encrypted VIN; VIN cipher tests"),
    ("VID I spec", "W3C DID validator passes", "PARTIAL", "external suite 328/441; resolution metadata fails (#24)"),
    ("VID I spec", "MOBI VID I checklist 100%", "PARTIAL", "birth anchoring native on all 5 backends; checklist not formalised"),
    ("VID II design", "10+ event types, multi-party issuance", "MET", "11 event types, 9 roles, attestations"),
    ("VID II design", "VC issue / verify / present / SD / revoke", "MET", "28 VC tests"),
    ("VID II design", "100% DID Core + 100% VC DM", "PARTIAL", "93.2% internal executable score"),
    ("VID II design", "Centralized feature parity", "MET", "centralized_vehicle_registry.py; PKI baseline"),
    ("VID II design", "5-10 use cases end-to-end", "MET", "12/12"),
]

# Architecture: as designed (MOBI_VID1_TECHNICAL_SPEC §System Overview) vs as built.
DESIGNED = [
    ("Application layer", "Vehicle registrar · Owner portal · Authority validator"),
    ("MOBI VID Provider (Python)", "register_vehicle_birth · resolve_vid_did · verify · DID document builder"),
    ("Smart-contract layer", "MOBIVIDRegistry.sol extends ERC-1056"),
    ("Blockchain layer", "Ethereum / Polygon / private chain"),
]
BUILT = [
    ("Application layer", "12 lifecycle use cases · SUMO V2V harness (unrun) · PKI-vs-ERC-1056 experiment"),
    ("W3C SSI layer", "VC issuer/holder/verifier (28 tests) · DID resolver (did:ethr/mobi/nft) · MOBI VID I/II Python (32 tests) · VIN cipher"),
    ("Identity providers", "PKI (IEEE 1609.2 model) · centralized registry · ERC-1056 (on-chain key resolution) · MOBI VID"),
    ("Smart-contract layer", "16 contracts / 10 standards: ERC-1056, 721, 725, 725xy, 735, 1155, 4337, LSP8, CVIN-Combined, MOBI VID I/II"),
    ("Blockchain layer", "Hardhat local (M1) · Sepolia harness (M2, unrun)"),
]


def strip(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)


def timeline():
    import textwrap
    fig, ax = plt.subplots(figsize=(13, 6.2))
    y = [i * 1.0 for i in range(len(PHASES))][::-1]
    for yi, (name, w0, w1, st, ev) in zip(y, PHASES):
        c, g = STATUS[st]
        ax.barh(yi, max(w1 - w0, 0.35), left=w0, height=0.5, color=BLUE_L, edgecolor=SURFACE)
        label = textwrap.fill(f"{g} {st.title()} — {ev}", width=78)
        ax.text(max(w1, w0 + 0.35) + 0.12, yi, label, va="center", fontsize=7.8, color=INK2, linespacing=1.15)
        ax.scatter([w0 - 0.18], [yi], s=90, color=c, zorder=3, edgecolor=SURFACE)
    ax.set_yticks(y); ax.set_yticklabels([p[0] for p in PHASES], fontsize=8.6)
    ax.set_xticks(range(0, 8)); ax.set_xticklabels(["done at\n2025-11-10"] + [f"wk {i}" for i in range(1, 8)], fontsize=8)
    ax.set_xlim(-0.6, 15.5); ax.set_ylim(-0.7, len(PHASES) - 0.3)
    ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True); strip(ax)
    ax.set_title("CV2X roadmap (2025-11-10): planned window vs state on the merged trunk (2026-09-25)",
                 loc="left", fontsize=11, pad=12)
    ax.set_xlabel("bar = planned window (weeks after 2025-11-10) · dot = status on the trunk: "
                  "✓ met · ◐ partial · ○ open · ✗ dropped (SCOPE_CHANGES.md)", fontsize=8, color=MUTED, labelpad=10)
    fig.tight_layout(); out = HERE / "review_roadmap_timeline.png"; fig.savefig(out, dpi=200); print("wrote", out)


def matrix():
    fig, ax = plt.subplots(figsize=(12.5, 8.6))
    n = len(CRITERIA); ax.set_xlim(0, 12); ax.set_ylim(-0.5, n - 0.5)
    # Column x-positions: document | criterion | chip | evidence. The chip sits at
    # 4.05 so the longest criterion label (≈40 chars at 8.8 pt) clears it.
    for i, (doc, crit, st, ev) in enumerate(CRITERIA):
        yi = n - 1 - i; c, g = STATUS[st]
        ax.add_patch(FancyBboxPatch((4.05, yi - 0.36), 0.55, 0.72, boxstyle="round,pad=0.02,rounding_size=0.08", fc=c, ec=SURFACE))
        ax.text(4.325, yi, g, ha="center", va="center", fontsize=10, color=SURFACE if st != "OPEN" else INK, fontweight="bold")
        ax.text(0.02, yi, doc, va="center", fontsize=8, color=MUTED)
        ax.text(0.95, yi, crit, va="center", fontsize=8.8, color=INK)
        ax.text(4.8, yi, f"{st.title()} — {ev}", va="center", fontsize=8, color=INK2)
        if i < n - 1:
            ax.plot([0, 12], [yi - 0.5, yi - 0.5], color=GRID, lw=0.6)
    ax.axis("off")
    counts = {k: sum(1 for c in CRITERIA if c[2] == k) for k in STATUS}
    ax.set_title("Success criteria across the three design documents — status on the merged trunk  "
                 + " · ".join(f"{STATUS[k][1]} {v} {k.lower()}" for k, v in counts.items()),
                 loc="left", fontsize=10.5, pad=10)
    fig.tight_layout(); out = HERE / "review_criteria_matrix.png"; fig.savefig(out, dpi=200); print("wrote", out)


def architecture():
    import textwrap
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.4), gridspec_kw={"width_ratios": [1, 1.25]})
    for ax, layers, title, width in ((axes[0], DESIGNED, "As designed — MOBI_VID1_TECHNICAL_SPEC (2025-11-10)", 60),
                                     (axes[1], BUILT, "As built — merged trunk (2026-09-25)", 76)):
        ax.set_xlim(0, 1); ax.set_ylim(0, len(layers)); ax.axis("off")
        for i, (name, body) in enumerate(layers):
            yi = len(layers) - 1 - i
            ax.add_patch(FancyBboxPatch((0.02, yi + 0.06), 0.96, 0.88, boxstyle="round,pad=0.01,rounding_size=0.03",
                                        fc=SURFACE, ec=BLUE, lw=1.4))
            ax.text(0.05, yi + 0.76, name, fontsize=9.5, fontweight="bold", color=BLUE, va="center")
            # Explicit wrapping: matplotlib's wrap=True does not respect axes bounds.
            ax.text(0.05, yi + 0.40, textwrap.fill(body, width=width), fontsize=7.8, color=INK2,
                    va="center", linespacing=1.2)
        ax.set_title(title, loc="left", fontsize=10.5, pad=8)
    fig.suptitle("Testbed architecture: four planned layers became five, with the SSI layer and the provider "
                 "abstraction as the additions", x=0.02, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93)); out = HERE / "review_architecture.png"; fig.savefig(out, dpi=200); print("wrote", out)


if __name__ == "__main__":
    timeline(); matrix(); architecture()
