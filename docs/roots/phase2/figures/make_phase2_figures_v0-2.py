#!/usr/bin/env python3
"""Generate Roots Phase 2 figures FIG-R7..FIG-R16, v0-2 set (reproducible).

Run from anywhere:  python3 docs/roots/phase2/figures/make_phase2_figures_v0-2.py
v0-1 SVGs (no suffix) are left untouched; this script writes *_v0-2.svg only.

Sources (parsed where the figure is a table view, curated-with-check where it is a diagram):
  R6  docs/roots/phase2/60_R6_full_stack_atlas/claude_CVIN_SC_Roots_FullStack_Atlas_R6_v0-2.md
  R7  docs/roots/phase2/70_R7_theory_ece_bounds/claude_CVIN_SC_Roots_Theory_ECE_Bounds_R7_v0-2.md
      + the printed output of r7_calc_v0-2.py (run by this script; FIG-R15, FIG-R16 use only its numbers)
  R9  docs/roots/phase2/90_R9_panel_review/claude_CVIN_SC_Roots_Panel_Review_R9_v0-1.md
  R8  docs/roots/phase2/80_R8_reverse_register/claude_CVIN_SC_Roots_Reverse_Anchor_Register_R8_v0-2.md
  Phase 1 README + R1..R5, Phase 2 shared brief.
Every tag printed is passed through tag(); a tag not found verbatim in the source corpus is
reported at the end (UNSOURCED) and the script exits non-zero.
"""
import os, re, sys, glob, subprocess
from xml.dom import minidom
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
P2 = os.path.dirname(HERE)
ROOTS = os.path.dirname(P2)
R6P = os.path.join(P2, "60_R6_full_stack_atlas", "claude_CVIN_SC_Roots_FullStack_Atlas_R6_v0-2.md")
R8P = os.path.join(P2, "80_R8_reverse_register", "claude_CVIN_SC_Roots_Reverse_Anchor_Register_R8_v0-2.md")
R7P = os.path.join(P2, "70_R7_theory_ece_bounds", "claude_CVIN_SC_Roots_Theory_ECE_Bounds_R7_v0-2.md")
R7CALC = os.path.join(P2, "70_R7_theory_ece_bounds", "r7_calc_v0-2.py")
R9P = os.path.join(P2, "90_R9_panel_review", "claude_CVIN_SC_Roots_Panel_Review_R9_v0-1.md")
R6 = open(R6P, encoding="utf-8").read()
R8 = open(R8P, encoding="utf-8").read()
R7 = open(R7P, encoding="utf-8").read()
R9 = open(R9P, encoding="utf-8").read()
R7OUT = subprocess.run([sys.executable, R7CALC], capture_output=True, text=True, cwd=os.path.dirname(R7CALC), check=True).stdout
CORPUS = R6 + R8 + R7 + R9 + R7OUT + open(os.path.join(P2, "00_control", "PHASE2_SHARED_BRIEF.md"), encoding="utf-8").read()
for f in glob.glob(os.path.join(ROOTS, "phase1", "**", "*.md"), recursive=True):
    CORPUS += open(f, encoding="utf-8").read()

UNSOURCED = []
def tag(t):
    """Return t; record it if it does not occur verbatim in the corpus."""
    if re.fullmatch(r"FIG-R(\d+)", t) and int(t[5:]) >= 7:
        return t  # brief §3: FIG-R7+ assigned to the visual agent (this script)
    if t not in CORPUS and t not in UNSOURCED:
        UNSOURCED.append(t)
    return t

# ---------------------------------------------------------------- style
FONT = "Helvetica, Arial, 'DejaVu Sans', sans-serif"
LAYER = {  # Phase 1 house colours (FIG-R1): fill, stroke
    "LH": ("#e6dfd8", "#5a4632"),
    "L0": ("#eeeeee", "#555555"), "L1": ("#fbe4e4", "#9c2c2c"), "L2": ("#ece3f5", "#5c3d8c"),
    "L3": ("#d9e7f5", "#2c5a8c"), "L4": ("#e3f0d8", "#4d7a2a"), "L5": ("#fde2c8", "#c46f00"),
    "L6": ("#fff1c9", "#a37a00"), "L7": ("#dff3f0", "#1f6f63"),
}
LAYER_NAME = {"LH": "Hardware", "L0": "Network", "L1": "Crypto", "L2": "Data/storage", "L3": "Agreement",
              "L4": "Econ/gov", "L5": "Ledger/EVM", "L6": "Identity", "L7": "Application"}
ST = {  # status styles
    "M": dict(fill="#3f8f3f", stroke="#2b6b2b", dash=None, name="MEASURED"),
    "Dv": dict(fill="#2c5a8c", stroke="#1d3f66", dash=None, name="DERIVED"),
    "I": dict(fill="#ffffff", stroke="#1f8a7a", dash=None, name="I implemented-unmeasured"),
    "D": dict(fill="#f3f3f3", stroke="#c46f00", dash="3,2", name="Ds DESIGN"),
    "E": dict(fill="url(#hatch)", stroke="#b8860b", dash=None, name="ESTIMATED"),
    "N": dict(fill="#ffffff", stroke="#bbbbbb", dash=None, name="— not used / empty"),
}
DEFS = ('<defs><pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" '
        'patternTransform="rotate(45)"><rect width="5" height="5" fill="#fff4cc"/>'
        '<line x1="0" y1="0" x2="0" y2="5" stroke="#e0a800" stroke-width="2"/></pattern>'
        '<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#555"/></marker></defs>')

def lay(sub):
    return sub.split(".")[0] if sub.startswith("L") else "LH"

class S:
    def __init__(s, w, h):
        s.w, s.h, s.o = w, h, []
    def add(s, x): s.o.append(x)
    def rect(s, x, y, w, h, fill="#fff", stroke="#bbb", sw=1, rx=0, dash=None, extra=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        s.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{extra}/>')
    def text(s, x, y, t, fs=9, anchor="start", weight=None, fill="#222", italic=False, rot=None):
        fs = max(fs, 9)
        a = f' font-weight="{weight}"' if weight else ""
        a += ' font-style="italic"' if italic else ""
        a += f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot is not None else ""
        s.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" text-anchor="{anchor}" fill="{fill}"{a}>{escape(str(t))}</text>')
    def line(s, x1, y1, x2, y2, stroke="#555", sw=1, arrow=False, dash=None):
        m = ' marker-end="url(#arr)"' if arrow else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        s.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{m}{d}/>')
    def marker(s, x, y, st, size=8):
        k = ST[st]
        s.rect(x, y, size, size, fill=k["fill"], stroke=k["stroke"], sw=1.4, dash=k["dash"])
    def header(s, fig, title, source):
        s.text(s.w / 2, 24, f"{tag(fig)} · {title}", fs=16, anchor="middle", weight="bold")
        s.text(s.w / 2, 41, f"Source: {source}", fs=10, anchor="middle", fill="#666")
    def legend(s, y, keys=("M", "Dv", "I", "D", "E", "N"), x0=20):
        x = x0
        for k in keys:
            s.marker(x, y - 8, k, 9)
            s.text(x + 13, y, ST[k]["name"], fs=9, fill="#444")
            x += 30 + 5.4 * len(ST[k]["name"])
    def footer(s, source, keys=("M", "Dv", "I", "D", "E", "N"), note=None):
        y = s.h - 30
        s.line(15, y - 14, s.w - 15, y - 14, stroke="#ccc")
        s.legend(y, keys)
        s.text(20, y + 16, f"Source: {source}. Scale R9 PN-32 · make_phase2_figures_v0-2.py (v0-2 inputs).", fs=9, fill="#666")
        if note:
            s.text(s.w - 20, y, note, fs=9, anchor="end", fill="#666", italic=True)
    def save(s, name):
        body = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s.w} {s.h}" width="{s.w}" height="{s.h}" '
                f'font-family="{FONT}">' + DEFS + f'<rect width="{s.w}" height="{s.h}" fill="#fff"/>'
                + "\n".join(s.o) + "</svg>\n")
        assert s.w <= 1000
        minidom.parseString(body)  # well-formedness check
        open(os.path.join(HERE, name.replace(".svg", "_v0-2.svg")), "w", encoding="utf-8").write(body)
        print("wrote + validated", name.replace(".svg", "_v0-2.svg"))

def wrap(t, width_px, fs=9):
    maxc = max(4, int(width_px / (fs * 0.53)))
    words, lines, cur = str(t).split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= maxc:
            cur = (cur + " " + w).strip()
        else:
            if cur: lines.append(cur)
            while len(w) > maxc:
                lines.append(w[:maxc]); w = w[maxc:]
            cur = w
    if cur: lines.append(cur)
    return lines or [""]

def md_table_after(text, heading):
    """Return rows (list of cell lists) of the first markdown table after heading."""
    i = text.index(heading)
    rows = []
    for l in text[i:].splitlines()[1:]:
        if l.startswith("|"):
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            rows.append(cells)
        elif rows:
            break
    return rows

def clean(t):
    return re.sub(r"[*`]", "", t)

SUBLAYERS = ["LH.1", "LH.2", "LH.3", "LH.4", "LH.5", "L0.1", "L0.2", "L0.3", "L0.4", "L1.1", "L1.2",
             "L2.1", "L2.2", "L2.3", "L3.1", "L3.2", "L4.1", "L4.2", "L4.3", "L5.1", "L5.2", "L5.3",
             "L6.1", "L6.2", "L6.3", "L7.1", "L7.2", "L7.3"]
for sl in SUBLAYERS:
    tag(sl)

R6SRC = "R6 Full-Stack Atlas v0-2"
R8SRC = "R8 Reverse Anchor Register v0-2"
R7SRC = "R7 Theory and ECE Bounds v0-2 + r7_calc_v0-2.py output"

# =========================================================== R6 St parsing (v0-2)
def r6_status_map():
    """Tag -> raw St cell from every R6 v0-2 register table that has an St column."""
    out, hdr = {}, None
    for l in R6.splitlines():
        if l.startswith("| Tag |"):
            hdr = [c.strip() for c in l.strip().strip("|").split("|")]; continue
        if not l.startswith("|"):
            hdr = None if not l.strip() == "" else hdr; continue
        if hdr and "St" in hdr:
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if len(c) == len(hdr):
                t = re.sub(r"\(~~.*?~~\)|[*`]", "", c[0]).strip()
                out[t] = c[hdr.index("St")]
    return out
R6ST = r6_status_map()

def st_code(cell):
    c = clean(cell).strip()
    if c.startswith("M"): return "M"
    if c.startswith("Dv"): return "Dv"
    if c.startswith("Ds"): return "D"
    if c.startswith("I"): return "I"
    if c.startswith("E"): return "E"
    return "N"

PARSED_ST = []  # tags whose marker came from the R6 v0-2 St cell
def r6st(t, fallback):
    if t in R6ST:
        PARSED_ST.append(t); return st_code(R6ST[t])
    return fallback

# =========================================================== FIG-R7
ATLAS = {  # sub-layer: [(tag, short label, status)] -- status read from R6 §2 row "Status" cell
 "LH.1": [("HW-01", "Xeon CPU (env.)", "M"), ("HW-02", "hardware RNG", "N"), ("IMP-LH.1-01", "OS CSPRNG", "I"), ("IMP-LH.1-02", "SHA-256(vehicle_id) keys", "I"), ("IMP-LH.1-03", "seeded PRNG", "I")],
 "LH.2": [("HW-03", "HSM", "D"), ("HW-04", "TPM 2.0", "N"), ("HW-05", "TEE (candidate)", "N"), ("HW-06", "SE / eSIM", "D")],
 "LH.3": [("HW-07", "ECU / gateway", "N"), ("HW-08", "OBU (Python obj.)", "I"), ("PRO-01", "CAN / CAN-FD", "N"), ("PRO-02", "Auto Ethernet", "N")],
 "LH.4": [("HW-09", "V2X modem (sim.)", "I"), ("HW-10", "GNSS time+pos", "D")],
 "LH.5": [("HW-11", "cloud host (env.)", "M"), ("HW-12", "validator host", "D"), ("IMP-LH.5-01", "docker compose", "D")],
 "L0.1": [("PRO-03", "802.11p/bd", "N"), ("PRO-04", "PC5 mode 4 (sim.)", "I"), ("PRO-05", "PC5 mode 3 (enum)", "N"), ("PRO-06", "NR-V2X", "N"), ("PRO-07", "cellular Uu", "N")],
 "L0.2": [("PRO-08", "WSMP 1609.3", "N"), ("PRO-09", "UDP/TCP loopback", "I"), ("PRO-10", "QUIC", "N")],
 "L0.3": [("PRO-11", "devp2p RLPx", "N"), ("PRO-11a", "discv4", "N"), ("PRO-11b", "discv5", "N"), ("PRO-11c", "libp2p", "N"), ("IMP-L0.3-01", "Besu static nodes", "D")],
 "L0.4": [("PRO-13", "JSON-RPC HTTP", "M"), ("PRO-13b", "Hardhat RPC", "I"), ("PRO-15", "TLS on RPC", "D"), ("IMP-L0.4-01", "web3.py HTTP", "I"), ("IMP-L0.4-02", "ethers provider", "I")],
 "L1.1": [("ALG-02", "ECDSA k1 RFC 6979", "I"), ("ALG-05", "ECDSA P-256", "M"), ("ALG-07", "keccak-256", "I"), ("ALG-12", "Groth16", "M"), ("ALG-14", "sigma protocols", "M"), ("ALG-16", "CL / BBS+", "N")],
 "L1.2": [("IMP-L1.2-01", "py cryptography", "I"), ("IMP-L1.2-02", "coincurve", "I"), ("IMP-L1.2-08", "snarkjs 0.7.6", "I"), ("IMP-L1.2-09", "zkid (not c.t.)", "I"), ("IMP-L1.2-06", "BouncyCastle", "D"), ("IMP-L1.2-10", "anoncreds-rs", "N")],
 "L2.1": [("ALG-18", "MPT (never proved)", "I"), ("IMP-L2.1-02", "receipts / logs", "M"), ("IMP-L2.1-03", "mapping storage", "M"), ("IMP-L2.1-04", "changed list", "I"), ("IMP-L2.1-01", "Bonsai tries", "D")],
 "L2.2": [("IMP-L2.2-01", "Hardhat in-memory", "I"), ("IMP-L2.2-03", "dict registry", "I"), ("IMP-L2.2-02", "RocksDB/LevelDB", "D")],
 "L2.3": [("IMP-L2.3-01", "RevocationRegistry", "I"), ("IMP-L2.3-04", "Poseidon WMI tree", "I"), ("IMP-L2.3-06", "replay cache", "I"), ("IMP-L2.3-02", "status list", "D"), ("IMP-L2.3-05", "IPFS / CAS", "N")],
 "L3.1": [("ALG-19", "Hardhat automine", "M"), ("ALG-19a", "interval mining", "I"), ("ALG-20", "QBFT", "D"), ("ALG-20b", "Clique", "N"), ("ALG-20c", "Gasper", "D")],
 "L3.2": [("IMP-L3.2-02", "Hardhat 2.28.6", "M"), ("IMP-L3.2-01", "Hyperledger Besu", "D"), ("IMP-L3.2-06", "Quorum", "D"), ("IMP-L3.2-05", "Ganache (config)", "N"), ("IMP-L3.2-03", "Geth", "N")],
 "L4.1": [("ALG-21", "EVM gas schedule", "M"), ("ALG-22", "EIP-1559", "N"), ("IMP-L4.1-01", "free-gas", "D")],
 "L4.2": [("IMP-L4.2-03", "contract roles", "M"), ("IMP-L4.2-01", "Besu permissioning", "D"), ("IMP-L4.2-02", "validator gov.", "D")],
 "L4.3": [("IMP-L4.3-01", "block gas limit", "I"), ("IMP-L4.3-02", "unlimited code size", "I")],
 "L5.1": [("PRO-16", "ecrecover 0x01", "I"), ("PRO-18", "bn256 0x06-0x08", "M"), ("IMP-L5.1-03", "block.timestamp", "I"), ("PRO-20", "BLS12-381 precomp.", "N")],
 "L5.2": [("SCF-EDR-03", "changeOwner", "M"), ("SCF-MOBI2-04", "attestEvent", "M"), ("SCF-ZKG-03", "admit", "M"), ("SCF-IDTX-03", "createIntent", "I")],
 "L5.3": [("PRO-21", "legacy EIP-155 tx", "I"), ("PRO-22", "4337 UserOp", "M"), ("PRO-22a", "*Signed meta-tx", "M"), ("PRO-21d", "EIP-7702", "N")],
 "L6.1": [("ALG-23", "did:ethr on-chain", "M"), ("ALG-23a", "did:ethr offline", "I"), ("ALG-24", "did:mobi", "I"), ("IMP-L6.1-01", "did:indy", "N")],
 "L6.2": [("IMP-L6.2-01", "VC 2.0 DI (eip191)", "M"), ("IMP-L6.2-02", "SD-JWT-style digests", "I"), ("IMP-L6.2-06", "ZK-VIN credential", "M"), ("IMP-L6.2-07", "AnonCreds/BBS+/mDL", "N")],
 "L6.3": [("IMP-L6.3-01", "IMinimalSSI F1-F12", "M"), ("IMP-L6.3-03", "ZkVinGate.admit", "M"), ("IMP-L6.3-04", "attestEvent", "M"), ("IMP-L6.3-02", "IdtxExecutor", "I")],
 "L7.1": [("IMP-L7.1-04", "identity providers", "I"), ("IMP-L7.1-05", "Steward (Sim)", "M"), ("IMP-L7.1-02", "web3.py", "I"), ("IMP-L7.1-06", "ACA-Py / Veramo", "N")],
 "L7.2": [("IMP-L7.2-01", "freshness module", "M"), ("IMP-L7.2-02", "JSON-signed BSM", "M"), ("IMP-L7.2-03", "verifier v3", "M"), ("PRO-12", "1609.2-style (X.509)", "D"), ("PRO-25", "DIDComm v2", "N")],
 "L7.3": [("IMP-L7.3-01", "SUMO V2V", "M"), ("IMP-L7.3-02", "RSU / TMC", "M"), ("IMP-L7.3-04", "pseudonym pool", "M"), ("IMP-L7.3-03", "MOBI lifecycle", "M"), ("IMP-L7.3-07", "ns-3", "D")],
}

def fig_r7():
    order = list(reversed(SUBLAYERS))  # L7.3 top ... LH.1 bottom
    bh, y0 = 27, 62
    s = S(1000, y0 + bh * len(order) + 62)
    s.header("FIG-R7", "Full-stack atlas: LH + L0.1–L7.3 with key IMP/PRO/ALG/HW/SCF items",
             f"{R6SRC} §1 (extended stack) and §2 (layer registers)")
    xl, xs, xi, iw, xr = 15, 62, 140, 128, 912
    # group strips by phase-1 layer
    groups = {}
    for i, sl in enumerate(order):
        groups.setdefault(lay(sl), []).append(i)
    for L, idx in groups.items():
        f, st = LAYER[L]
        ya, yb = y0 + idx[0] * bh, y0 + (idx[-1] + 1) * bh
        s.rect(xl, ya + 1, 44, yb - ya - 2, fill=f, stroke=st, sw=1.5, rx=3)
        s.text(xl + 22, (ya + yb) / 2 - 1, L, fs=12, anchor="middle", weight="bold", fill=st)
        s.text(xl + 22, (ya + yb) / 2 + 10, LAYER_NAME[L], fs=9, anchor="middle", fill=st) if len(idx) > 1 else None
    for i, sl in enumerate(order):
        y = y0 + i * bh
        f, st = LAYER[lay(sl)]
        s.rect(xs, y + 1, xr - xs, bh - 2, fill=f, stroke=st, sw=0.6)
        s.text(xs + 6, y + 17, sl, fs=11, weight="bold", fill=st)
        for j, (t, lab, stt) in enumerate(ATLAS[sl]):
            stt = r6st(t, stt)
            x = xi + j * iw
            s.marker(x, y + 6, stt, 8)
            s.text(x + 11, y + 13, tag(t), fs=9, weight="bold")
            s.text(x + 11, y + 23, lab, fs=9, fill="#333")
    # right edge
    ytop, ybot = y0 + 4, y0 + bh * len(order) - 4
    s.line(940, ytop + 10, 940, ybot, arrow=True, sw=1.6)
    s.line(972, ybot - 10, 972, ytop, arrow=True, sw=1.6)
    s.text(934, (ytop + ybot) / 2, "secured by ↓ (each band trusts the bands below)", fs=10, anchor="middle", rot=-90, fill="#444")
    s.text(984, (ytop + ybot) / 2, "enables ↑ (each band gives the band above)", fs=10, anchor="middle", rot=-90, fill="#444")
    s.footer(f"{R6SRC} §1–§2 (marker parsed from each row's St cell; SCF rows from §2.L5.2 notes)", keys=("M", "I", "D", "N"),
             note="LH = new layer below L0 (dark slate/brown)")
    s.save("FIG-R7_full_stack_atlas.svg")

# =========================================================== FIG-R8
def fig_r8():
    rows = md_table_after(R6, "## 7. What is measured vs designed")[1:]
    cols = [("Sub-layer", 58), ("M in this programme (rows / files)", 250), ("Ds only", 190),
            ("Not used", 170), ("Honest one-line summary (R6 §7)", 302)]
    lay_rows = []
    for r in rows:
        r = [clean(c) for c in r]
        lines = [wrap(r[k], cols[k][1] - 8) for k in range(1, 5)]
        h = max(len(x) for x in lines) * 10.5 + 7
        lay_rows.append((r, lines, h))
    y0 = 78
    H = y0 + sum(h for *_, h in lay_rows) + 124
    s = S(1000, int(H))
    s.header("FIG-R8", "Measured vs designed — the honesty map, one row per sub-layer",
             f"{R6SRC} §7 (parsed verbatim) and §2.L3 narrative")
    x = 10
    xs = []
    for name, w in cols:
        xs.append(x); s.text(x + 4, y0 - 6, name, fs=10, weight="bold"); x += w
    y = y0
    hot = {"L0.3", "L3.1", "L3.2", "L4.2", "L2.2"}
    for r, lines, h in lay_rows:
        sl = r[0]
        f, st = LAYER[lay(sl)]
        s.rect(xs[0], y, cols[0][1], h, fill=f, stroke=st)
        s.text(xs[0] + 6, y + 13, tag(sl), fs=10, weight="bold", fill=st)
        none_m = r[1].startswith("—")
        none_d = r[2].startswith("—")
        kinds = ["N" if none_m else "M", "N" if none_d else "D", "N", "N"]
        for k in range(4):
            K = ST[kinds[k]]
            fill = "#e4f2e4" if kinds[k] == "M" else ("#fbf1e6" if kinds[k] == "D" else "#ffffff")
            s.rect(xs[k + 1], y, cols[k + 1][1], h, fill=fill, stroke=K["stroke"] if kinds[k] != "N" else "#ccc",
                   dash=K["dash"], sw=1.2 if kinds[k] != "N" else 0.6)
            for li, t in enumerate(lines[k]):
                s.text(xs[k + 1] + 4, y + 12 + li * 10.5, t, fs=9, fill="#222" if k != 2 else "#777")
        if re.search(r"\bI\b", " ".join(r[1:])):
            s.marker(xs[0] + 44, y + 5, "I", 9)
        if sl in hot:
            s.rect(xs[0] - 2, y - 1, sum(w for _, w in cols) + 4, h + 2, fill="none", stroke="#c0392b", sw=2)
        y += h
    s.text(14, y + 44, "Teal I marker = the row names an item at status I (implemented, unmeasured: code runs, no register row) — "
           "L0.1 ResourcePool, LH.3 OBU object, L5.2 IdtxExecutor/CEI check, L6.3 IDTX.", fs=9, fill=ST["I"]["stroke"])
    s.text(14, y + 18, "Red outline = consensus / finality / availability / persistence sub-layers: nothing above an "
           "automining single process has been executed. R6 §2.L3: \"The repository's executed agreement mechanism", fs=9, fill="#c0392b")
    s.text(14, y + 30, "is Hardhat automine ... provides ordering trivially and safety and liveness not at all\"; "
           "Besu, QBFT, Gasper, RocksDB, node permissioning are DESIGN.", fs=9, fill="#c0392b")
    s.footer(f"{R6SRC} §7 table, locked by R9 SLD-12 (cell text verbatim, markdown stripped)", keys=("M", "I", "D", "N"))
    s.save("FIG-R8_measured_vs_designed.svg")

# =========================================================== FIG-R9
CHAINS = [
 ("Trace 1 — key rotation", "SCF-EDR-03 changeOwner", [
   ("L5.2", "SCF-EDR-03", "changeOwner writes owners[id]", "M"),
   ("L5.2", "SCF-EDR-01", "onlyOwner: identityOwner", "I"),
   ("L2.1", "IMP-L2.1-03", "mapping storage slot", "M"),
   ("L5.3", "PRO-21", "outer tx sig, EIP-155", "I"),
   ("L1.1", "ALG-02", "ECDSA k1 over keccak (ALG-07)", "I"),
   ("L7.1", "IMP-L7.1-02", "eth-account key (testbed)", "I"),
   ("LH.2", "HW-06", "SE key (deployment)", "D"),
   ("LH.1", "IMP-LH.1-01", "OS CSPRNG", "I"),
   ("LH.1", "HW-02", "RDRAND / TRNG", "N"),
  ], "weakest: BP-LH-02 (key = SHA-256(vehicle_id)). Gas: 68,854 (#2, test ctx) / 51,754 (harness U1, run 1f4ace0)"),
 ("Trace 3 — V2V SSI BSM", "IMP-L7.2-02 accept BSM", [
   ("L7.2", "IMP-L7.2-02", "receiver accepts BSM", "M"),
   ("L7.2", "IMP-L7.2-01", "freshness window", "M"),
   ("L2.3", "IMP-L2.3-06", "replay cache", "I"),
   ("L7.2", "IMP-L7.2-04", "state cache, refresh every k_f", "I"),
   ("LH.4", "HW-10", "receiver clock = GNSS", "D"),
   ("L1.1", "ALG-04", "ECDSA k1 / SHA-256 (not EIP-191)", "I"),
   ("L1.2", "IMP-L1.2-01", "py cryptography", "I"),
   ("L5.2", "SCF-VPR-05", "veriKey attribute", "I"),
   ("L6.1", "ALG-23", "eth_getLogs replay", "M"),
   ("L0.4", "PRO-13", "JSON-RPC (unproven)", "M"),
   ("L5.1", "IMP-L5.1-03", "chain time for validTo", "I"),
  ], "weakest: BP-LH-04, BP-L0.4-02, BP-L7.2-03 (no TTL), BP-L7.2-04 (size); #21 #27 #37"),
 ("Trace 5 — ZK-VIN admission", "SCF-ZKG-03 admit", [
   ("L5.2", "SCF-ZKG-03", "admit emits Admitted", "M"),
   ("L5.2", "SCF-ZKG-01", "nullifier + public signals", "I"),
   ("L5.2", "SCF-G16-01", "Groth16 verifyProof", "M"),
   ("L5.1", "PRO-18", "ecAdd/ecMul/ecPairing", "M"),
   ("L1.1", "ALG-10", "BN254 pairing (PF-10)", "I"),
   ("L1.2", "BP-L1.2-04", "single-party setup", "D"),
   ("L1.2", "IMP-L1.2-07", "circom R1CS soundness", "I"),
   ("L1.1", "ALG-09", "Poseidon commitment", "I"),
   ("L5.2", "SCF-EDR-03", "anchored by owner (Trace 1)", "M"),
  ], "weakest: the setup (BP-L1.2-04; R7 PF-35, t_s = 1); #56-#58; model within 1.3 % (PF-51)"),
 ("Trace 6 — lifecycle attestation", "SCF-MOBI2-04 attestEvent", [
   ("L5.2", "SCF-MOBI2-04", "attestation stored", "M"),
   ("L1.2", "IMP-L1.2-11", "OZ ECDSA: low-s, chain-bound", "I"),
   ("L1.1", "ALG-03", "ecrecover recovery", "I"),
   ("L5.2", "SCF-MOBI2-01", "issuer role check", "I"),
   ("L4.2", "IMP-L4.2-03", "single registryAuthority key", "M"),
   ("L5.2", "SCF-VPR-01", "owner / validDelegate", "I"),
   ("L5.1", "IMP-L5.1-03", "chain time", "I"),
   ("L5.3", "PRO-21", "outer tx (Trace 1)", "I"),
  ], "weakest: BP-L4.2-02 single registry-authority key (PF-66 req.); #28 198,694 gas"),
]

def fig_r9():
    cw, bh, gap, y0 = 240, 38, 10, 92
    n = max(len(c[2]) for c in CHAINS)
    s = S(1000, y0 + n * (bh + gap) + 110)
    s.header("FIG-R9", "Secured-by chains: four vertical traces from function or message to silicon",
             f"{R6SRC} §6 (Traces 1, 3, 5, 6)")
    for ci, (title, top, steps, weak) in enumerate(CHAINS):
        x = 12 + ci * (cw + 8)
        s.text(x + cw / 2, 62, title, fs=11, anchor="middle", weight="bold")
        s.text(x + cw / 2, 76, "starts at " + top, fs=9, anchor="middle", fill="#555")
        for i, (sl, t, lab, st) in enumerate(steps):
            st = r6st(t, st)
            y = y0 + i * (bh + gap)
            f, sc = LAYER[lay(sl)]
            s.rect(x, y, cw - 10, bh, fill=f, stroke=sc, sw=1.3, rx=4)
            s.marker(x + 6, y + 6, st, 9)
            s.text(x + 20, y + 14, tag(t), fs=10, weight="bold")
            s.text(x + cw - 16, y + 14, tag(sl), fs=9, anchor="end", fill=sc, weight="bold")
            s.text(x + 20, y + 29, lab, fs=9, fill="#333")
            if i < len(steps) - 1:
                s.line(x + (cw - 10) / 2, y + bh, x + (cw - 10) / 2, y + bh + gap - 1, arrow=True)
                s.text(x + (cw - 10) / 2 + 5, y + bh + 8, "⇐ secured by", fs=9, fill="#888")
        yb = y0 + len(steps) * (bh + gap) + 4
        for li, t in enumerate(wrap(weak, cw - 10)):
            s.text(x, yb + li * 11, t, fs=9, fill="#c0392b", italic=True)
    s.footer(f"{R6SRC} §6 worked traces; step marker parsed from the matching §2 St cell", keys=("M", "I", "D", "N"),
             note="box colour = Phase 1 layer; LH slate/brown")
    s.save("FIG-R9_secured_by_chains.svg")

# =========================================================== R8 parsing
CATS = ["TX", "IDTX", "VC", "SIG", "READ", "PRIM", "ALG", "PROT", "SC", "SCF", "NET", "DLT", "IMPL", "HW",
        "SVC", "SCN", "GOV", "MET", "THR"]
LAYERS = ["L7", "L6", "L5", "L4", "L3", "L2", "L1", "L0", "LH"]

def r8_rows():
    out = {}
    hdr = None
    for l in R8.splitlines():
        if l.startswith("| RV |"):
            hdr = [c.strip() for c in l.strip().strip("|").split("|")]
            continue
        m = re.match(r"\| (RV-([A-Z]+)-\d+) \|", l)
        if m and hdr:
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            d = dict(zip(hdr, cells))
            d["cat"] = m.group(2)
            out[m.group(1)] = d
    return out

def layers_of(sub):
    res = set()
    for part in re.split(r"[,;]", sub):
        part = part.strip()
        m = re.match(r"^L(\d)\s*[–-]\s*L(\d)", part)
        if m:
            res |= {f"L{k}" for k in range(int(m.group(1)), int(m.group(2)) + 1)}
            continue
        m = re.match(r"^(LH|L\d)", part)
        if m:
            res.add(m.group(1))
    return res

HOME = {  # home (start) level per R8 §3.x opening paragraph
 "SCN": ("L7", "L7.3"), "SVC": ("L7", "L2.3 / L7.1"), "PROT": ("L7", "L0.2–L0.4, L7.2"), "IDTX": ("L6", "L6.3"),
 "VC": ("L6", "L6.2"), "READ": ("L6", "L6.1 / L0.4 / L2"), "TX": ("L5", "L5.3"), "SC": ("L5", "L5.2"),
 "SCF": ("L5", "L5.2"), "GOV": ("L4", "L4.2"), "DLT": ("L4", "L2–L4"), "IMPL": ("L3", "L3.2, L1.2, L7.1"),
 "ALG": ("L1", "L1.2–L6.1"), "SIG": ("L1", "L1.1/L1.2"), "PRIM": ("L1", "L1"), "NET": ("L0", "L0.1–L0.4"),
 "HW": ("LH", "LH"), "THR": (None, "various"), "MET": (None, "outside stack"),
}
CAT_ORDER = ["SCN", "SVC", "PROT", "IDTX", "VC", "READ", "TX", "SC", "SCF", "GOV", "DLT", "IMPL", "ALG", "SIG",
             "PRIM", "NET", "HW", "THR", "MET"]

def fig_r10():
    rows = r8_rows()
    count = {c: 0 for c in CATS}
    grid = {c: {L: 0 for L in LAYERS} for c in CATS}
    unplaced = {c: 0 for c in CATS}
    for rv, d in rows.items():
        c = d["cat"]; count[c] += 1
        sub = d.get("Sub-layer", "")
        if c == "SCF" and not sub:
            sub = "L5.2"  # R8 §3.10: "The verbs of L5.2" (table has no Sub-layer column)
        ls = layers_of(sub)
        if not ls:
            unplaced[c] += 1
        for L in ls:
            grid[c][L] += 1
    total = sum(count.values())
    xl, cw, y0, rh = 92, 47, 140, 50
    s = S(1000, y0 + rh * len(LAYERS) + 120)
    s.header("FIG-R10", "Reverse-anchor categories: where each RV category starts and which layers its rows anchor to",
             f"{R8SRC} §3.1–§3.19 (Sub-layer column parsed) and §7 row counts")
    for i, L in enumerate(LAYERS):
        f, st = LAYER[L]
        y = y0 + i * rh
        s.rect(15, y + 2, 70, rh - 4, fill=f, stroke=st, rx=3, sw=1.4)
        s.text(50, y + rh / 2 + 1, L, fs=12, anchor="middle", weight="bold", fill=st)
        s.text(50, y + rh / 2 + 13, LAYER_NAME[L], fs=9, anchor="middle", fill=st)
        s.rect(xl, y + 2, cw * len(CAT_ORDER), rh - 4, fill=f, stroke="none", extra=' opacity="0.35"')
    for j, c in enumerate(CAT_ORDER):
        x = xl + j * cw + cw / 2
        home, homelab = HOME[c]
        f, st = LAYER[home] if home else ("#f6f6f6", "#777")
        s.rect(x - 22, 56, 44, 50, fill=f, stroke=st, sw=1.5, rx=4)
        s.text(x, 70, tag("RV-" + c), fs=9, anchor="middle", weight="bold", fill=st)
        s.text(x, 84, f"{count[c]} rows", fs=9, anchor="middle")
        s.text(x, 98, home or "—", fs=9, anchor="middle", fill=st)
        filled = [i for i, L in enumerate(LAYERS) if grid[c][L]]
        if filled:
            s.line(x, 106, x, y0 + filled[-1] * rh + rh / 2 - 9, sw=1.2, arrow=True, stroke="#777")
        for i, L in enumerate(LAYERS):
            n = grid[c][L]
            if n:
                r = 3 + 2.2 * n ** 0.5
                s.add(f'<circle cx="{x:.1f}" cy="{y0 + i * rh + rh / 2:.1f}" r="{r:.1f}" fill="{LAYER[L][1]}" opacity="0.85"/>')
                s.text(x + r + 2, y0 + i * rh + rh / 2 - r + 2, n, fs=9, fill="#222")
            if home == L:
                s.rect(x - 21, y0 + i * rh + 4, 42, rh - 8, fill="none", stroke="#222", sw=1.4, dash="2,2")
        if unplaced[c]:
            s.text(x, y0 + len(LAYERS) * rh + 12, f"+{unplaced[c]} n/s", fs=9, anchor="middle", fill="#a33")
    yb = y0 + len(LAYERS) * rh + 30
    s.text(15, yb, f"Columns ordered by home level (R8 §3 opening paragraphs), top of stack left. Total {total} RV rows "
           f"(R8 v0-2 header states 311). Dot = rows of that category whose Sub-layer cell names that layer (size ~ √count);",
           fs=9, fill="#444")
    s.text(15, yb + 12, "a row naming several layers counts in each. Dashed box = home level. Arrow = descent to the lowest "
           "anchored layer. RV-SCF has an SCF-tag column, no Sub-layer: placed at L5.2 per §3.10.",
           fs=9, fill="#444")
    s.text(15, yb + 24, "'n/s' = no sub-layer stated (all of MET; some TX, GOV, THR rows).",
           fs=9, fill="#444")
    s.footer(f"{R8SRC} §3, §7", keys=(), note="colours = Phase 1 layers; LH slate/brown")
    s.save("FIG-R10_reverse_anchor_categories.svg")
    return count, total

# =========================================================== FIG-R11
MD_SHORT = None
def md_names():
    rows = md_table_after(R8, "## 1. Measurement dimensions MD-01..MD-22")[1:]
    return {r[0]: clean(r[1]) for r in rows}

def fig_r11():
    names = md_names()
    rows = md_table_after(R8, "## 5. Coverage matrix")
    hdr, body = rows[0], rows[1:]
    mds = [f"MD-{h}" for h in hdr[1:]]
    xl, cw, rh, y0 = 70, 33, 22, 190
    s = S(1000, y0 + rh * (len(body) + 1) + 140)
    s.header("FIG-R11", "Coverage matrix: 19 RV categories × 22 measurement dimensions (four-state, PN-27)",
             f"{R8SRC} §5 (cells parsed verbatim; recomputed by r8_coverage.py) and §1 (MD names)")
    SYM = {"●": 0, "◐": 1, "○": 2, "·": 3}
    colt = {m: [0, 0, 0, 0] for m in mds}
    tot = [0, 0, 0, 0]
    for j, m in enumerate(mds):
        x = xl + j * cw + cw / 2
        s.text(x + 3, y0 - 8, f"{tag(m)} {names[m][:24]}", fs=9, rot=-60)
    s.text(xl + len(mds) * cw + 6, y0 - 8, "M / Dv / Ds / empty", fs=9, weight="bold")
    for i, r in enumerate(body):
        c = r[0]; y = y0 + i * rh
        s.text(xl - 6, y + 15, tag("RV-" + c), fs=9, anchor="end", weight="bold")
        rc = [0, 0, 0, 0]
        for j, v in enumerate(r[1:]):
            x = xl + j * cw
            k = SYM[v.strip()]
            rc[k] += 1; colt[mds[j]][k] += 1; tot[k] += 1
            if k == 0:
                s.rect(x + 1, y + 1, cw - 2, rh - 2, fill=ST["M"]["fill"], stroke="#fff")
            elif k == 1:
                s.rect(x + 1, y + 1, cw - 2, rh - 2, fill=ST["Dv"]["fill"], stroke="#fff")
            elif k == 2:
                s.rect(x + 2, y + 2, cw - 4, rh - 4, fill=ST["D"]["fill"], stroke=ST["D"]["stroke"], dash="3,2", sw=1.2)
            else:
                s.rect(x + 1, y + 1, cw - 2, rh - 2, fill="#fff", stroke="#e2e2e2")
        s.text(xl + len(mds) * cw + 6, y + 15, f"{rc[0]} / {rc[1]} / {rc[2]} / {rc[3]}", fs=9)
    yt = y0 + len(body) * rh
    s.text(xl - 6, yt + 14, "measured", fs=9, anchor="end", weight="bold")
    s.text(xl - 6, yt + 26, "Dv/design", fs=9, anchor="end")
    for j, m in enumerate(mds):
        x = xl + j * cw + cw / 2
        s.text(x, yt + 14, colt[m][0], fs=9, anchor="middle", weight="bold", fill="#c0392b" if colt[m][0] == 0 else "#222")
        s.text(x, yt + 26, f"{colt[m][1]}/{colt[m][2]}" if colt[m][1] else colt[m][2], fs=9, anchor="middle", fill="#c46f00")
    zero = [m for m in mds if colt[m][0] == 0]
    stated = re.search(r"\*\*● (\d+) measured\*\*.*?\*\*◐ (\d+) derived only\*\*.*?\*\*○ (\d+) design\*\*.*?\*\*· (\d+) empty\*\*", R8)
    stated = tuple(int(g) for g in stated.groups())
    assert tuple(tot) == stated, (tot, stated)
    s.text(15, yt + 48, f"Totals (computed from the parsed cells): measured {tot[0]} · derived only {tot[1]} · design {tot[2]} · "
           f"empty {tot[3]} of {sum(tot)} cells, matching the R8 v0-2 §5 headline.", fs=10, weight="bold")
    s.text(15, yt + 62, "Red measured totals = no measured cell: " + ", ".join(zero) + " (R8 §5: one automining node, PF-39, and absent hardware).",
           fs=9, fill="#c0392b")
    s.text(15, yt + 75, "v0-1's 128 measured cells fell to 77 through the measured/derived split (PN-27), the slash rule and the PN-23 downgrades; R8 states no measurement was lost.",
           fs=9, fill="#444")
    s.text(15, yt + 88, "Cell code (R8 §5): green = ≥ 1 St-M row evidencing the MD (before slash) · blue = Dv only · "
           "dashed = MD targeted, not evidenced (Ds, I, E, S, —, or after slash) · white = no row.", fs=9, fill="#444")
    s.footer(f"{R8SRC} §5 cell code (PN-27); I never counts as measured", keys=("M", "Dv", "D", "N"))
    s.save("FIG-R11_coverage_matrix.svg")
    return tot

# =========================================================== FIG-R12
def fig_r12():
    rows = r8_rows()
    sec = R8[R8.index("### 4.1 Lead chain"):R8.index("### 4.2")]
    steps = []
    last = "L7.1"
    for l in sec.splitlines():
        m = re.match(r"^(\d+)\. (?:\*\*(L[\dH][^*]*)\*\* )?(.*)$", l)
        if m:
            layer = (m.group(2) or "").strip()
            if layer:
                last = layer
            steps.append((m.group(1), layer, clean(m.group(3)), layer or last))
    mds_line = clean(re.search(r"\*\*MDs:\*\*(.*)", sec).group(1))
    rh, y0 = 54, 70
    s = S(1000, y0 + rh * len(steps) + 150)
    s.header("FIG-R12", "Lead anchor chain: revokeCredential and the revocation window W",
             f"{R8SRC} §4.1 (steps parsed verbatim; v0-1 §4(d), promoted by PN-30); per-row MD and St from §3")
    s.text(140, y0 - 6, "Step (R8 §4.1 wording)", fs=10, weight="bold")
    s.text(690, y0 - 6, "RV rows cited → MD · St", fs=10, weight="bold")
    for i, (n, layer, txt, Lc) in enumerate(steps):
        y = y0 + i * rh
        L = Lc.split()[0]
        f, sc = LAYER[lay(L)]
        s.rect(15, y + 4, 110, rh - 12, fill=f if layer else "#f6f6f6", stroke=sc, sw=1.5, rx=4,
               dash=None if layer else "3,2")
        s.text(24, y + 20, f"{n}.", fs=11, weight="bold", fill=sc)
        s.text(76, y + 20, layer if layer else "(no layer)", fs=10 if len(layer) < 10 else 9, anchor="middle", weight="bold", fill=sc)
        s.text(76, y + 33, LAYER_NAME[lay(L)] if layer else "forensic only", fs=9, anchor="middle", fill=sc)
        for li, t in enumerate(wrap(txt, 535)[:4]):
            s.text(140, y + 14 + li * 11, t, fs=9)
        cited = [t for t in dict.fromkeys(re.findall(r"RV-[A-Z]+-\d+", txt))]
        x = 690
        for k, rv in enumerate(cited[:3]):
            d = rows.get(rv, {})
            st = st_code(d.get("St", "—"))
            yy = y + 6 + k * 13
            s.marker(x, yy, st, 9)
            s.text(x + 13, yy + 8, f"{tag(rv)} · MD {d.get('MD', '?')} · {clean(d.get('St', '?'))}"[:50], fs=9)
        if i < len(steps) - 1:
            s.line(70, y + rh - 8, 70, y + rh + 3, arrow=True)
    yb = y0 + rh * len(steps) + 8
    s.text(15, yb + 6, "Whole-chain MDs and status (R8 §4.1):", fs=10, weight="bold")
    for li, t in enumerate(wrap(mds_line, 960, 9)[:4]):
        s.text(15, yb + 20 + li * 11, t, fs=9)
    s.footer(f"{R8SRC} §4.1 + §3 rows; marker = each cited RV row's St cell", keys=("M", "Dv", "I", "D", "N"),
             note="k-bound M (#46); time bound needs a TTL (SLD-05)")
    s.save("FIG-R12_anchor_chain_revocation.svg")

# =========================================================== FIG-R13
CLASSES = ["Sybil / identity", "Key compromise", "Availability / liveness", "Ordering / finality / replay",
           "Linkability", "Collusion / governance", "Economic / capacity", "Coverage gap"]
BP_CLASS = {  # figure author's classification of R6 §4 rows into Phase 1 FIG-R2 attack classes
 "BP-LH-01": 1, "BP-LH-02": 1, "BP-LH-03": 1, "BP-LH-04": 3, "BP-LH-05": 7, "BP-LH-06": 7,
 "BP-L0.1-01": 2, "BP-L0.2-01": 2, "BP-L0.3-01": 0, "BP-L0.4-01": 2, "BP-L0.4-02": 7, "BP-L0.4-03": 0,
 "BP-L1.1-01": 7, "BP-L1.1-02": 1, "BP-L1.2-01": 7, "BP-L1.2-02": 7, "BP-L1.2-03": 0, "BP-L1.2-04": 1,
 "BP-L1.2-05": 3, "BP-L2.1-01": 7, "BP-L2.1-02": 7, "BP-L2.2-01": 2, "BP-L2.3-01": 2, "BP-L2.3-02": 3,
 "BP-L3.2-01": 2, "BP-L3.2-02": 7, "BP-L4.2-01": 5, "BP-L4.2-02": 5, "BP-L5.2-01": 3, "BP-L5.2-02": 0,
 "BP-L5.2-03": 3, "BP-L5.2-04": 1, "BP-L5.2-05": 1, "BP-L5.2-06": 7, "BP-L6.1-01": 4, "BP-L6.2-01": 7,
 "BP-L7.2-01": 4, "BP-L7.2-02": 3, "BP-L7.3-01": 5,
 # v0-2 additions (R6 v0-2 §4.1 marks them "(new)"); classes again this figure's reading
 "BP-L0.1-02": 4, "BP-L7.2-03": 3, "BP-L7.2-04": 6,
}
NEW_V02 = {"BP-L0.1-02", "BP-L7.2-03", "BP-L7.2-04"}

def fig_r13():
    rows = md_table_after(R6, "### 4.1 Register")[1:]
    bps = []
    for r in rows:
        t = clean(r[0]).replace("(new)", "").strip()
        closed = clean(r[4]).lower()
        state = "open" if re.search(r"\bopen\b", closed) else ("closed" if "closed" in closed and "partial" not in closed else "partial")
        sub = "LH" if t.startswith("BP-LH") else re.match(r"BP-(L\d\.\d)", t).group(1)
        bps.append((t, sub, state))
    assert set(b[0] for b in bps) == set(BP_CLASS), "BP list changed in R6 §4 — update BP_CLASS"
    assert not re.search(r"attack class", R6[R6.index("## 4."):R6.index("## 5.")], re.I), "R6 now assigns classes — use them"
    subs = []
    for _, sub, _ in bps:
        if sub not in subs: subs.append(sub)
    subs = list(reversed(subs))
    xl, cw, rh, y0 = 70, 104, 34, 78
    s = S(1000, y0 + rh * len(subs) + 124)
    s.header("FIG-R13", "New breaking points by sub-layer × attack class (extends Phase 1 FIG-R2)",
             f"{R6SRC} §4.1 ({len(bps)} rows: BP-LH-01..06 + {len(bps) - 6} BP-Lx.y; * = new in v0-2)")
    for j, c in enumerate(CLASSES):
        for li, t in enumerate(wrap(c, cw - 4)):
            s.text(xl + j * cw + cw / 2, y0 - 18 + li * 10, t, fs=9, anchor="middle", weight="bold")
    s.text(xl + len(CLASSES) * cw + 25, y0 - 8, "n", fs=9, anchor="middle", weight="bold")
    for i, sub in enumerate(subs):
        y = y0 + i * rh
        f, st = LAYER[lay(sub) if sub != "LH" else "LH"]
        s.text(xl - 8, y + 21, tag(sub) if sub != "LH" else "LH", fs=11, anchor="end", weight="bold", fill=st)
        n = 0
        for j in range(len(CLASSES)):
            cell = [b for b in bps if b[1] == sub and BP_CLASS[b[0]] == j]
            n += len(cell)
            s.rect(xl + j * cw + 1, y + 1, cw - 2, rh - 2, fill=f if cell else "#fafafa", stroke="#bbb")
            for k, (t, _, state) in enumerate(cell[:3]):
                short = t.replace("BP-", "")
                col = {"open": "#c0392b", "partial": "#a36a00", "closed": "#2b6b2b"}[state]
                xx = xl + j * cw + 6 + (k % 2) * 49
                yy = y + 14 + (k // 2) * 13
                tag(t)
                s.add(f'<circle cx="{xx:.1f}" cy="{yy - 3:.1f}" r="2.6" fill="{col}"/>')
                s.text(xx + 5, yy, short + ("*" if t in NEW_V02 else ""), fs=9, weight="bold" if t in NEW_V02 else None)
        s.text(xl + len(CLASSES) * cw + 25, y + 21, n, fs=10, anchor="middle")
    yb = y0 + rh * len(subs) + 14
    for k, (lab, col) in enumerate([("open (Closed-by cell says 'open')", "#c0392b"), ("partial / DESIGN mitigation", "#a36a00"), ("closed", "#2b6b2b")]):
        s.add(f'<circle cx="{25 + k * 230:.1f}" cy="{yb - 3:.1f}" r="3" fill="{col}"/>')
        s.text(32 + k * 230, yb, lab, fs=9)
    s.text(15, yb + 28, "R6 v0-2 still assigns no attack class (checked by the script); FLAG for the author: confirm or override BP_CLASS.",
           fs=9, fill="#c0392b", weight="bold")
    s.text(15, yb + 14, "Caveat: R6 §4 does not assign attack classes; the column placement is this figure's reading of each row's "
           "'Attack / failure' cell using FIG-R2's eight classes (replay and clock faults placed under ordering).", fs=9, fill="#666")
    s.footer(f"{R6SRC} §4.1; fill = Phase 1 layer colour (LH slate/brown); open/closed parsed from 'Closed by'", keys=())
    s.save("FIG-R13_new_breaking_points_heatmap.svg")

# =========================================================== FIG-R14
def fig_r14():
    s = S(1000, 700)
    s.header("FIG-R14", "Phase 1 to Phase 2 map: documents, directions and tag ownership (all R1–R9 issued)",
             "Phase 1 README (tag table); PHASE2_SHARED_BRIEF §3–§4; R6/R7/R8 v0-2 'Assigns'/'Owns' rows; R9 v0-1 §3.2")
    s.rect(15, 54, 970, 150, fill="#fafafa", stroke="#ccc", rx=6)
    s.text(25, 72, "PHASE 1 (docs/roots/phase1/) — primitives and architectures, tags frozen", fs=11, weight="bold")
    p1 = [("R1", "Roots Lineage", ["L0–L7", "T-01..T-24", "T-I01..T-I22", "issued v1-1"]),
          ("R2", "Integration Scan", ["SOL-01..09", "options O1–O18", "issued v0-1"]),
          ("R3", "I2I Identity Stack", ["BP-L0-01..BP-L7-07", "FIG-R1..R6", "R1–R8, I1–I9", "issued v0-1"]),
          ("R4", "Proofs and Bounds", ["PF-01..31", "SYM-01..24", "issued v0-1"]),
          ("R5", "Pass Record", ["KD-R1..3, Q-R1..6", "CEV, LIM, MC", "issued v0-1"])]
    for i, (r, n, tags) in enumerate(p1):
        x = 30 + i * 192
        s.rect(x, 82, 176, 110, fill="#fff", stroke=ST["I"]["stroke"], sw=1.3, rx=5)
        s.text(x + 8, 100, f"{tag(r)} {n}", fs=11, weight="bold")
        for k, t in enumerate(tags):
            s.text(x + 8, 118 + k * 14, t, fs=9, fill="#333" if not t.startswith("issued") else "#1f6f63")
        if i < 4:
            s.line(x + 176, 137, x + 190, 137, arrow=True)
    s.text(650, 232, "consumed (cited, never redefined) ↓", fs=10, anchor="middle", fill="#555")
    for x in (200, 500, 800):
        s.line(x, 205, x, 248, arrow=True, sw=1.4)
    s.rect(15, 252, 970, 400, fill="#fafafa", stroke="#ccc", rx=6)
    s.text(25, 270, "PHASE 2 (docs/roots/phase2/) — hardware → application forward (R6), reverse register (R8), bounds (R7), review (R9)",
           fs=11, weight="bold")
    sx, sy = 430, 300
    for i, L in enumerate(LAYERS):
        f, st = LAYER[L]
        s.rect(sx, sy + i * 26, 160, 24, fill=f, stroke=st, rx=3)
        s.text(sx + 80, sy + i * 26 + 16, f"{L} {LAYER_NAME[L]}", fs=9, anchor="middle", fill=st, weight="bold")
    s.line(sx - 14, sy + 9 * 26 - 4, sx - 14, sy + 4, arrow=True, sw=2, stroke="#2c5a8c")
    s.text(sx - 22, sy + 117, "forward: enables ↑ (bottom-up)", fs=9, anchor="middle", rot=-90, fill="#2c5a8c")
    s.line(sx + 174, sy + 4, sx + 174, sy + 9 * 26 - 4, arrow=True, sw=2, stroke="#a33")
    s.text(sx + 186, sy + 117, "reverse: anchors ↓ (top-down)", fs=9, anchor="middle", rot=90, fill="#a33")
    def box(x, y, w, h, title, status, lines):
        s.rect(x, y, w, h, fill="#fff", stroke=ST["I"]["stroke"], sw=1.6, rx=5)
        s.text(x + 8, y + 16, title, fs=11, weight="bold")
        s.text(x + w - 8, y + 16, status, fs=9, anchor="end", fill="#1f6f63")
        for i, t in enumerate(lines):
            s.text(x + 8, y + 32 + i * 13, t, fs=9, fill="#333")
    box(30, 290, 345, 160, f"{tag('R6')} Full-Stack Atlas (forward)", "v0-1 + v0-2 issued", [
        "owns: HW-01..12 · PRO-01..25 · ALG-01..24", "IMP-<sublayer>-nn · SCF-<prefix>-nn (117 rows)",
        "BP-LH-01..06 + 36 BP-Lx.y-nn · SOL-10..17", "Q-R6-01..07 · KD-R6-01/03/04",
        "v0-2: PRO-13x/y/z → PRO-23/24/25; 3 new BP", "§6 traces · §7 measured vs designed (SLD-12)",
        "requests PF-63..66 from R7", "figures: FIG-R7, R8, R9, R13"])
    box(30, 462, 345, 172, f"{tag('R7')} Theory and ECE Bounds", "v0-1 + v0-2 issued", [
        "owns: SYM-25..58 · SR-L..T · PF-32..66", "Q-R7-01..08 · KD-R7-01..07 · CEV-R7-01/02",
        "LIM-R7-01..08 (unfetched citations)", "v0-2: KD-R4 → KD-R7; PAR → R8 numbers;",
        "PF-45/46 filled; PF-63..66 added", "script: r7_calc.py (v0-1), r7_calc_v0-2.py",
        "bounds ALG- (R6 defines, R7 bounds)", "figures: FIG-R15, FIG-R16"])
    box(640, 290, 345, 160, f"{tag('R8')} Reverse Anchor Register", "v0-1 + v0-2 issued", [
        "owns: RV-<CAT>-nn (19 categories, 311 rows)", "MD-01..MD-22 · PAR-01..PAR-43 (sole PAR owner)",
        "Q-R8-01..05 · KD-R8-01..06", "v0-2 coverage M / Dv / Ds / empty = 77/3/115/223",
        "lead chain = revocation W (§4.1, PN-30)", "zero ⟦⟧ placeholders (r8_coverage.py)",
        "figures: FIG-R10, R11, R12"])
    box(640, 462, 345, 172, f"{tag('R9')} Professors' Panel Review", "v0-1 issued (v0-2 next)", [
        "owns: PN-01..33 · SLD-01..16 · DRP-01..10", "NC-01..10 · CA-01..18 · PRM-<sublayer>-nn",
        "§3.1 re-keying applied by R6/R7/R8 v0-2", "reviews R6–R8 at v0-1; v0-2 review pending",
        "panel: DS CR TCS ECE ITS STD MTH", "visual agent owns FIG-R7+ (this set)"])
    s.line(375, 370, 412, 370, arrow=True, stroke="#2c5a8c", sw=1.4)
    s.line(638, 370, 608, 370, arrow=True, stroke="#a33", sw=1.4)
    s.line(375, 548, 638, 548, arrow=True, dash="4,3")
    s.text(507, 543, "PF-tags bound to MD / PAR", fs=9, anchor="middle", fill="#555")
    s.line(640, 600, 377, 600, arrow=True, dash="4,3")
    s.text(507, 595, "R9 §3.1 re-keying → all v0-2", fs=9, anchor="middle", fill="#555")
    s.line(200, 450, 200, 460, arrow=True)
    s.footer("Phase 1 README §tags; PHASE2_SHARED_BRIEF §3–§4; R6/R7/R8 v0-2 headers; R9 v0-1 header and §3.2",
             keys=(), note="teal outline = issued; each Phase 2 namespace has exactly one owner")
    s.save("FIG-R14_phase1_phase2_map.svg")

# =========================================================== R7 output parsing (FIG-R15, FIG-R16)
def r7_lines(pf):
    return [l for l in R7OUT.splitlines() if l.startswith(f"[{pf}]")]

def fig_r15():
    cls = []
    for l in r7_lines("PF-43"):
        m = re.match(r"\[PF-43\] (.+?): t_ver=([\d.]+) ms v_max=([\d,]+)/s P\*\(0\.5\)=floor\(50/t\)=(\d+) P\*\(1\)=(\d+) rho at (.*)$", l)
        if m:
            rho = [(int(a), float(b)) for a, b in re.findall(r"P=(\d+):([\d.]+)", m.group(6))]
            cls.append((m.group(1), float(m.group(2)), int(m.group(4)), int(m.group(5)), rho))
    assert len(cls) == 5, cls
    lin = re.search(r"#26 linear model P\*\(0\.5\)=50/([\d.]+).*?= ([\d.]+)", R7OUT)
    t26, p26 = float(lin.group(1)), float(lin.group(2))
    air = {}
    for l in r7_lines("PF-44"):
        m = re.match(r"\[PF-44\] 802\.11p (.+?): MPDU=.*N_fit@CBR0\.6=(\d+)", l)
        if m: air[m.group(1)] = int(m.group(2))
    ratio = re.search(r"repo JSON airtime / digest airtime = ([\d.]+)x \(ERC-1056\), ([\d.]+)x \(PKI\)", R7OUT).groups()
    kf = re.search(r"total-budget criterion .*?P=100 = (\d+)", R7OUT).group(1)
    kr = re.search(r"refresh-load criterion .*?P=100 \(PN-11 corrected\) = ([\d.]+)", R7OUT).group(1)
    s = S(1000, 664)
    s.header("FIG-R15", "V2X safety-message path: verification load vs neighbours — hardware and airtime bind before the ledger",
             f"{R7SRC} §4.2 (PF-43) and §4.3 (PF-44)")
    X0, Y0, W, H = 90, 80, 640, 400
    Pmax, Tmax = 320, 200.0  # ms of verification per 100 ms BSM interval
    px = lambda P: X0 + W * P / Pmax
    py = lambda t: Y0 + H - H * min(t, Tmax) / Tmax
    s.rect(X0, Y0, W, H, fill="#fff", stroke="#999")
    for P in range(0, Pmax + 1, 50):
        s.line(px(P), Y0 + H, px(P), Y0, stroke="#eee"); s.text(px(P), Y0 + H + 14, P, fs=9, anchor="middle")
    for t in range(0, int(Tmax) + 1, 25):
        s.line(X0, py(t), X0 + W, py(t), stroke="#eee"); s.text(X0 - 6, py(t) + 3, t, fs=9, anchor="end")
    s.text(X0 + W / 2, Y0 + H + 32, "neighbours P (each sending BSMs at 10 Hz)", fs=10, anchor="middle")
    s.text(X0 - 50, Y0 + H / 2, "verification time per 100 ms interval, ms  (= ρ_v × 100)", fs=10, anchor="middle", rot=-90)
    # budget lines
    s.line(X0, py(100), X0 + W, py(100), stroke="#c0392b", sw=2)
    s.rect(X0 + W - 300, py(100) - 15, 296, 13, fill="#fff", stroke="none")
    s.text(X0 + W - 4, py(100) - 5, "100 ms Tier-1 budget (ρ_v = 1: queue unstable above)", fs=9, anchor="end", fill="#c0392b", weight="bold")
    s.line(X0, py(50), X0 + W, py(50), stroke="#c0392b", sw=1.2, dash="5,3")
    s.rect(X0 + W - 400, py(50) - 15, 266, 13, fill="#fff", stroke="none")
    s.text(X0 + W - 134, py(50) - 5, "identity share f_id = 0.5 → 50 ms (defines P*(0.5))", fs=9, anchor="end", fill="#c0392b")
    cols = ["#3f8f3f", "#2b6b2b", "#b8860b", "#c46f00", "#8e2c2c"]
    dash = [None, "2,2", None, "6,3", None]
    for i, (name, t, p05, p1, rho) in enumerate(cls):
        st = "M" if ", M)" in name else "E"
        pts = [(0, 0)] + [(P, r * 100) for P, r in rho]
        Pend = min(Pmax, Tmax / t)
        assert all(abs(r * 100 - P * t) < 0.6 for P, r in rho), (name, rho)  # rho_v*100 ms == P*t_ver
        s.line(px(0), py(0), px(Pend), py(Pend * t), stroke=cols[i], sw=2.2, dash=dash[i] if st == "M" else "5,3")
        for P, v in pts[1:]:
            if v <= Tmax:
                s.add(f'<circle cx="{px(P):.1f}" cy="{py(v):.1f}" r="3" fill="{cols[i]}"/>')
        ly = Y0 + 16 + i * 30
        s.line(X0 + W + 18, ly - 3, X0 + W + 40, ly - 3, stroke=cols[i], sw=2.2, dash=None if st == "M" else "5,3")
        s.text(X0 + W + 46, ly, f"{name}", fs=9, weight="bold")
        s.text(X0 + W + 46, ly + 12, f"t_ver {t} ms · P*(0.5)={p05} · P*(1)={p1}", fs=9, fill="#444")
    # #26 model
    s.line(px(0), py(0), px(Pmax), py(Pmax * t26), stroke="#2c5a8c", sw=1.6, dash="1,3")
    s.add(f'<circle cx="{px(p26):.1f}" cy="{py(50):.1f}" r="4" fill="none" stroke="#2c5a8c" stroke-width="1.6"/>')
    s.rect(px(p26) - 270, py(50) + 26, 266, 13, fill="#fff", stroke="none")
    s.text(px(p26) - 4, py(50) + 36, f"#26 model {t26} ms/nbr → P*(0.5) = {p26:.0f} (lead, M)", fs=9, anchor="end", fill="#2c5a8c")
    ly = Y0 + 16 + 5 * 30
    s.line(X0 + W + 18, ly - 3, X0 + W + 40, ly - 3, stroke="#2c5a8c", sw=1.6, dash="1,3")
    s.text(X0 + W + 46, ly, "register #26 linear model (M; P ≤ 80 tested)", fs=9, weight="bold")
    # airtime
    yA = Y0 + 16 + 6 * 30 + 6
    s.text(X0 + W + 18, yA, "PF-44 airtime: vehicles that fit", fs=9, weight="bold")
    s.text(X0 + W + 18, yA + 12, "an 802.11p channel at CBR 0.6", fs=9, weight="bold")
    for k, key in enumerate(["repo JSON PKI (#23 1,110 B)", "repo JSON ERC-1056 (#23 596 B)", "1609.2 digest"]):
        n = air[key]
        c = "#7a3e9d"
        s.line(px(n), Y0, px(n), Y0 + H, stroke=c, sw=1.4, dash="4,2")
        s.text(px(n) + 3, Y0 + 12 + k * 11 + (24 if k == 2 else 0), f"N_fit={n}", fs=9, fill=c, weight="bold")
        s.text(X0 + W + 18, yA + 26 + k * 12, f"{key}: {n}", fs=9, fill=c)
    s.text(X0 + W + 18, yA + 66, f"JSON costs {ratio[0]}× / {ratio[1]}× digest airtime", fs=9, fill="#7a3e9d")
    yb = Y0 + H + 50
    s.text(15, yb, "Reading: a curve crossing the dashed 50 ms line marks the neighbour count where verification alone uses the identity "
           "budget; crossing the red 100 ms line, the verifier queue is unstable.", fs=9)
    s.text(15, yb + 13, f"The MCU HSM class saturates at P = 20 and the Cortex-A53 class at P = 100, below the {air['repo JSON PKI (#23 1,110 B)']}–"
           f"{air['1609.2 digest']} vehicles the channel can carry; the repo's JSON encoding caps the channel first for software verifiers.",
           fs=9)
    s.text(15, yb + 26, f"The ledger enters only through state refreshes: with k_f ≥ {kr} (refresh-load criterion, P = 100) refreshes stay "
           f"inside the budget; the whole-path criterion needs k_f ≥ {kf} (#32 knee ≈ 90).", fs=9)
    s.text(15, yb + 39, "Under HAA-1 (k_f → ∞) both criteria reduce to a pure verification-hardware condition.", fs=9)
    s.text(15, yb + 52, "Caveats: Xeon rows are M (#27) on a server host, not an OBU (NC-05); ASIC/HSM, A53 and MCU classes are E (LIM-R7-03); "
           "PF-44 sizes are E (LIM-R7-02/07). Numbers parsed from r7_calc_v0-2.py output.", fs=9, fill="#666")
    s.footer("r7_calc_v0-2.py §G (PF-43), §H (PF-44); register rows #23 #26 #27 #32", keys=("M", "E"),
             note="solid = M, dashed = E")
    s.save("FIG-R15_v2x_bottleneck.svg")
    return cls

def fig_r16():
    cells = []
    for l in r7_lines("PF-48"):
        m = re.match(r"\[PF-48\] mu_off=(\d+)s A_L=([\d.]+): E\[W\]=([\d.]+)s \(MC ([\d.]+)\) p99=([\d.]+)s \(MC ([\d.]+)\) p99\.9=([\d.]+)s \(MC ([\d.]+)\)", l)
        if m:
            cells.append(tuple(float(g) for g in m.groups()))
    assert len(cells) == 9, cells
    dev = re.search(r"max relative MC deviation.*?= ([\d.]+) %", R7OUT).group(1)
    poll = re.findall(r"poll period adds mean T_p/2, max T_p = ([\d.]+) / (\d+) s", R7OUT)
    import math
    s = S(1000, 600)
    s.header("FIG-R16", "Revocation latency W with intermittent RSU backhaul: mean vs tail quantiles",
             f"{R7SRC} §4.8 (PF-48, alternating-renewal model, Ds; W_0 = 8.5 s from R4 PF-28)")
    X0, Y0, W, H = 80, 80, 880, 360
    lo, hi = 1.0, 4000.0
    py = lambda v: Y0 + H - H * (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))
    s.rect(X0, Y0, W, H, fill="#fff", stroke="#999")
    for v, lab in [(1, "1 s"), (10, "10 s"), (60, "1 min"), (600, "10 min"), (3600, "1 h")]:
        s.line(X0, py(v), X0 + W, py(v), stroke="#eee")
        s.text(X0 - 6, py(v) + 3, lab, fs=9, anchor="end")
    s.text(X0 - 55, Y0 + H / 2, "W (log scale)", fs=10, anchor="middle", rot=-90)
    s.line(X0, py(8.5), X0 + W, py(8.5), stroke="#555", dash="4,3")
    s.line(X0 + 290, Y0 + 13, X0 + 312, Y0 + 13, stroke="#555", dash="4,3")
    s.text(X0 + 318, Y0 + 17, "W_0 = 8.5 s (R4 PF-28, Ds)", fs=9, fill="#555")
    gw = W / 9
    cols = [("E[W]", "#2c5a8c"), ("p99", "#c46f00"), ("p99.9", "#c0392b")]
    for i, (mu, al, ew, ewmc, p99, p99mc, p999, p999mc) in enumerate(cells):
        gx = X0 + i * gw
        if i % 3 == 0 and i:
            s.line(gx, Y0, gx, Y0 + H + 40, stroke="#bbb")
        for k, v in enumerate((ew, p99, p999)):
            bx = gx + 14 + k * 23
            s.rect(bx, py(v), 20, Y0 + H - py(v), fill=cols[k][1], stroke="none")
            s.text(bx + 10, py(v) - 3, f"{v:g}", fs=9, anchor="middle")
        s.text(gx + gw / 2, Y0 + H + 14, f"A_L = {al:g}", fs=9, anchor="middle")
        if i % 3 == 1:
            s.text(gx + gw / 2, Y0 + H + 30, f"mean outage μ_off = {mu:g} s", fs=10, anchor="middle", weight="bold")
    for k, (lab, c) in enumerate(cols):
        s.rect(X0 + 10 + k * 90, Y0 + 8, 10, 10, fill=c, stroke="none")
        s.text(X0 + 24 + k * 90, Y0 + 17, lab, fs=9)
    yb = Y0 + H + 56
    a = cells[6]
    s.text(15, yb, f"Reading: at 99 % availability with 10-minute outages the mean is {a[2]:g} s but p99.9 is {a[6]:g} s (≈ {a[6]/60:.0f} min). "
           "Revocation guarantees must be stated as tail quantiles of the down-time, not as availability percentages.", fs=9)
    s.text(15, yb + 13, f"p99 = W_0 where 1 − A_L ≤ 1 − q (atom at W_0). Monte Carlo (2e6 draws, seed 42) agrees within {dev} % on every "
           "non-degenerate cell; the A_L = 0.99, q = 0.99 edge cell is excluded (sampling artefact).", fs=9)
    s.text(15, yb + 26, "A poll-based RSU adds " + ", ".join(f"{m} s mean / {x} s max" for m, x in poll) + " for T_p = 1 / 10 / 60 s. "
           "The repo's RSU rows (#46) bound staleness in messages with no propagation model (Q-R7-05).", fs=9)
    s.text(15, yb + 39, "Caveat: the whole model is Ds (exponential down-times, stationary renewal); no backhaul was measured. Values parsed "
           "from r7_calc_v0-2.py output; cited tags PF-48, PF-28, BP-L0.2-01, RV-SVC-03.", fs=9, fill="#666")
    s.footer("r7_calc_v0-2.py §L (PF-48)", keys=("D",), note="all bars DESIGN-model values")
    s.save("FIG-R16_revocation_tail.svg")
    return cells

if __name__ == "__main__":
    fig_r7(); fig_r8(); fig_r9()
    count, total = fig_r10()
    tot = fig_r11()
    fig_r12(); fig_r13(); fig_r14(); fig_r15(); fig_r16()
    for t in ["PF-43", "PF-44", "PF-48", "PF-28", "BP-L0.2-01", "RV-SVC-03", "LIM-R7-03", "LIM-R7-02", "LIM-R7-07", "NC-05",
              "Q-R7-05", "SLD-05", "PN-30", "PN-27", "SLD-12", "HAA-1", "PRO-23", "PRO-24", "PRO-25", "KD-R6-01", "KD-R7-01",
              "CEV-R7-01", "PAR-43", "SYM-58", "SR-L", "SR-T", "PF-66", "PN-33", "SLD-16", "CA-18", "Q-R8-05", "KD-R8-06"]:
        tag(t)
    print("RV rows parsed:", total, count)
    print("coverage totals ● ◐ ○ ·:", tot)
    print("markers parsed from R6 v0-2 St cells:", len(PARSED_ST))
    for f in sorted(glob.glob(os.path.join(HERE, "FIG-R*_v0-2.svg"))):
        minidom.parse(f)
        print("re-validated", os.path.basename(f))
    if UNSOURCED:
        print("UNSOURCED tags:", UNSOURCED)
        sys.exit(1)
    print("all printed tags found in source corpus")
