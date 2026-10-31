#!/usr/bin/env python3
"""A1 poster (594 x 841 mm, portrait) for the V2V identity visual layer (Phase 6).

    python3 docs/visual/poster/build_poster.py

Writes docs/visual/poster/cvin_v2v_poster_A1.pdf (vector text and layout; the
figures are the committed PNGs at their native resolution) and a 150 dpi PNG
preview. Layout from docs/visual/VISUAL_PHASES_PROMPTS.md Phase 6:
  - F1 road frame across the top as the hero, with the F3 latency strip as a band below it;
  - F2 and F5 side by side, and the attack board down the right;
  - the rogue findings, the mock/real table and the headline number, then F8 (cold stages) at the bottom.
Style: VISUAL_PLAN.md §4. No number on the poster is typed in unless it is a
register value (#27, #25) or a count from a committed trace (FIGURES.md).
"""
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[3]
FIG = ROOT / "docs" / "visual" / "figures"
OUT = ROOT / "docs" / "visual" / "poster"

PAPER, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
SSI, PKI, SPRAY = "#2a78d6", "#c99228", "#ff3d00"
MONO = "DejaVu Sans Mono"
SANS = "DejaVu Sans"

W_MM, H_MM = 594.0, 841.0
INCH = 25.4


def mm(x, y, w, h):
    """mm from top-left -> figure-fraction axes rect."""
    return [x / W_MM, 1 - (y + h) / H_MM, w / W_MM, h / H_MM]


def place(fig, path, x, y, w, h):
    im = mpimg.imread(path)
    ih, iw = im.shape[:2]
    ar = iw / ih
    # fit inside the box, top-left aligned
    if w / h > ar:
        w2, h2 = h * ar, h
    else:
        w2, h2 = w, w / ar
    ax = fig.add_axes(mm(x, y, w2, h2))
    ax.imshow(im, interpolation="lanczos")
    ax.axis("off")
    return h2


def text(fig, x, y, s, size, **kw):
    fig.text(x / W_MM, 1 - y / H_MM, s, fontsize=size, va="top", ha=kw.pop("ha", "left"),
             family=kw.pop("family", SANS), color=kw.pop("color", INK), **kw)


def main():
    plt.rcParams["pdf.fonttype"] = 42
    fig = plt.figure(figsize=(W_MM / INCH, H_MM / INCH), facecolor=PAPER)

    # --- title block (stencil voice) and the road motif
    text(fig, 30, 26, "SELF-SOVEREIGN IDENTITY\nFOR CONNECTED VEHICLES", 60, family=MONO, weight="bold",
         linespacing=1.05)
    text(fig, 30, 84, "Every V2V message signed. Every receiver verifying. The identity layer, shown.", 22,
         color=INK2)
    text(fig, 30, 95, "Nikhil Prakash  ·  MASc, Electrical and Computer Engineering, University of British Columbia",
         15, color=MUTED)
    motif = fig.add_axes(mm(410, 28, 154, 44))
    motif.set_xlim(0, 1); motif.set_ylim(0, 3); motif.axis("off")
    for i in range(3):
        motif.add_patch(Rectangle((0, i + 0.12), 1, 0.76, color="#2a2a27"))
    for fx, ln, s in [(0.05, 0, 1), (0.2, 1, 0), (0.33, 2, 1), (0.48, 0, 1), (0.6, 1, 1), (0.71, 2, 0),
                      (0.84, 0, 1), (0.9, 1, 1), (0.12, 2, 1)]:
        motif.add_patch(Rectangle((fx, ln + 0.33), 0.07, 0.34, color=SSI if s else PKI, ec=INK, lw=0.6))
    text(fig, 410, 75, "blue = SSI / MOBI VID (W3C credential, secp256k1)\nochre = PKI (X.509, ECDSA P-256)",
         11, color=MUTED, linespacing=1.3)

    # Each figure carries its own stencil title, so the poster adds no section headers.
    # Row 1, the hero: the road frame across the full width.
    y = 112
    y += place(fig, FIG / "sim_50v_20s_seed6" / "F1_road_frame_t015.png", 30, y, 534, 205) + 8
    # Row 2: latency strip and attack board.
    h3 = place(fig, FIG / "sim_50v_20s_seed6" / "F3_latency_strip.png", 30, y, 372, 150)
    h4 = place(fig, FIG / "sim_50v_20s_seed6" / "F4_attack_board.png", 412, y, 152, 150)
    y += max(h3, h4) + 8
    # Row 3: contact matrix and cold vs warm.
    h2 = place(fig, FIG / "sim_50v_20s_seed6" / "F2_contact_matrix_veh_045.png", 30, y, 263, 110)
    h5 = place(fig, FIG / "sim_50v_20s_seed6" / "F5_cold_warm_hist.png", 301, y, 263, 110)
    y += max(h2, h5) + 8
    # Row 4: the rogue, the claims table and the headline number.
    hr = place(fig, FIG / "sim_50v_20s_seed6_rogue_replay" / "F9_rejections.png", 30, y, 263, 95)
    text(fig, 30, y + hr + 4,
         "617 of 617 uncredentialed and 517 of 517 tampered rogue messages rejected.\n"
         "17 replays accepted: fresh genuine messages relayed to receivers that missed\n"
         "the original. Authenticity holds; reach is extended.",
         12, color=INK2, linespacing=1.35)
    tx = 305
    text(fig, tx, y, "WHAT THE PICTURES MAY CLAIM", 18, family=MONO, weight="bold")
    rows = [("Signing, verification", "real crypto, every message"),
            ("Latency on any axis", "real, perf_counter, compute only"),
            ("Vehicle motion", "mock model or SUMO 1.28 (TraCI)"),
            ("Radio channel", "mock: 8 nearest within 300 m"),
            ("The blockchain", "not in the V2V loop")]
    ry = y + 10
    for i, (a, b) in enumerate(rows):
        bx = fig.add_axes(mm(tx, ry + i * 11, 259, 10))
        bx.axis("off")
        bx.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="square,pad=0", fc="#f1f0eb" if i % 2 == 0 else PAPER,
                                    ec=GRID, lw=0.6, transform=bx.transAxes))
        text(fig, tx + 3, ry + i * 11 + 2.5, a, 12, weight="bold")
        text(fig, tx + 95, ry + i * 11 + 2.5, b, 12, color=INK2)
    sy = ry + 5 * 11 + 8
    text(fig, tx, sy, "0.142 ms", 40, family=MONO, weight="bold", color=SSI)
    text(fig, tx + 112, sy + 2, "SSI warm verify, median of 30 run-medians\n(register #27), against a 100 ms V2V budget",
         12, color=INK2, linespacing=1.3)
    # Row 5: where cold latency goes (stage timers; proportions only).
    y = max(y + hr + 26, sy + 24) + 10
    place(fig, FIG / "sim_50v_20s_seed6_rogue_uncredentialed" / "F8_cold_stages.png", 30, y, 534, min(150, H_MM - 32 - y))

    # --- footer
    text(fig, 30, H_MM - 16,
         "Every figure regenerates from a committed trace: docs/visual/FIGURES.md · trace schema cvin-v2v-trace/1 · "
         "mock mobility unless marked SUMO · no radio channel or MAC modelled · interactive replay: docs/visual/replay/",
         11, color=MUTED)

    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "cvin_v2v_poster_A1.pdf", facecolor=PAPER)
    fig.savefig(OUT / "cvin_v2v_poster_A1_preview.png", dpi=60, facecolor=PAPER)
    print("wrote", OUT / "cvin_v2v_poster_A1.pdf")


if __name__ == "__main__":
    main()
