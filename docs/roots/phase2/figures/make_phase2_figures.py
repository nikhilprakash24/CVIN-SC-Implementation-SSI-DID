#!/usr/bin/env python3
"""Generate Roots Phase 2 figures FIG-R7..FIG-R14 (reproducible).

Run from anywhere:  python3 docs/roots/phase2/figures/make_phase2_figures.py

Sources (parsed where the figure is a table view, curated-with-check where it is a diagram):
  R6  docs/roots/phase2/60_R6_full_stack_atlas/claude_CVIN_SC_Roots_FullStack_Atlas_R6_v0-1.md
  R8  docs/roots/phase2/80_R8_reverse_register/claude_CVIN_SC_Roots_Reverse_Anchor_Register_R8_v0-1.md
  Phase 1 README + R1..R5, Phase 2 shared brief.
Every tag printed is passed through tag(); a tag not found verbatim in the source corpus is
reported at the end (UNSOURCED) and the script exits non-zero.
"""
import os, re, sys, glob
from xml.dom import minidom
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
P2 = os.path.dirname(HERE)
ROOTS = os.path.dirname(P2)
R6P = os.path.join(P2, "60_R6_full_stack_atlas", "claude_CVIN_SC_Roots_FullStack_Atlas_R6_v0-1.md")
R8P = os.path.join(P2, "80_R8_reverse_register", "claude_CVIN_SC_Roots_Reverse_Anchor_Register_R8_v0-1.md")
R6 = open(R6P, encoding="utf-8").read()
R8 = open(R8P, encoding="utf-8").read()
CORPUS = R6 + R8 + open(os.path.join(P2, "00_control", "PHASE2_SHARED_BRIEF.md"), encoding="utf-8").read()
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
FONT = "Helvetica, Arial, sans-serif"
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
    "I": dict(fill="#ffffff", stroke="#1f8a7a", dash=None, name="I implemented-unmeasured / used"),
    "D": dict(fill="#f3f3f3", stroke="#c46f00", dash="3,2", name="DESIGN"),
    "E": dict(fill="url(#hatch)", stroke="#b8860b", dash=None, name="ESTIMATED"),
    "N": dict(fill="#ffffff", stroke="#bbbbbb", dash=None, name="empty / not used"),
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
        s.text(20, y + 16, f"Source: {source}. Status legend per R6 header / R8 §0 (M, Dv, Ds, E, S, I). "
               "Generated by make_phase2_figures.py; first-pass (v0-1) inputs.", fs=9, fill="#666")
        if note:
            s.text(s.w - 20, y, note, fs=9, anchor="end", fill="#666", italic=True)
    def save(s, name):
        body = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s.w} {s.h}" width="{s.w}" height="{s.h}" '
                f'font-family="{FONT}">' + DEFS + f'<rect width="{s.w}" height="{s.h}" fill="#fff"/>'
                + "\n".join(s.o) + "</svg>\n")
        assert s.w <= 1000
        minidom.parseString(body)  # well-formedness check
        open(os.path.join(HERE, name), "w", encoding="utf-8").write(body)
        print("wrote + validated", name)

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

R6SRC = "R6 Full-Stack Atlas v0-1"
R8SRC = "R8 Reverse Anchor Register v0-1"

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
 "L1.1": [("ALG-02", "ECDSA k1 RFC 6979", "I"), ("ALG-05", "ECDSA P-256", "I"), ("ALG-07", "keccak-256", "I"), ("ALG-12", "Groth16", "M"), ("ALG-14", "sigma protocols", "M"), ("ALG-16", "CL / BBS+", "N")],
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
 "L7.2": [("IMP-L7.2-01", "freshness module", "M"), ("IMP-L7.2-02", "JSON-signed BSM", "M"), ("IMP-L7.2-03", "verifier v3", "M"), ("PRO-12", "IEEE 1609.2", "D"), ("PRO-13z", "DIDComm v2", "N")],
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
    s.footer(f"{R6SRC} §1–§2 (status from each row's Status cell; 'used' drawn as I)", keys=("M", "I", "D", "N"),
             note="LH = new layer below L0 (dark slate/brown)")
    s.save("FIG-R7_full_stack_atlas.svg")

# =========================================================== FIG-R8
def fig_r8():
    rows = md_table_after(R6, "## 7. What is measured vs designed")[1:]
    cols = [("Sub-layer", 58), ("MEASURED in this programme (rows / files)", 250), ("DESIGN only", 190),
            ("Not used", 170), ("Honest one-line summary (R6 §7)", 302)]
    lay_rows = []
    for r in rows:
        r = [clean(c) for c in r]
        lines = [wrap(r[k], cols[k][1] - 8) for k in range(1, 5)]
        h = max(len(x) for x in lines) * 10.5 + 7
        lay_rows.append((r, lines, h))
    y0 = 78
    H = y0 + sum(h for *_, h in lay_rows) + 110
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
        if sl in hot:
            s.rect(xs[0] - 2, y - 1, sum(w for _, w in cols) + 4, h + 2, fill="none", stroke="#c0392b", sw=2)
        y += h
    s.text(14, y + 18, "Red outline = consensus / finality / availability / persistence sub-layers: nothing above an "
           "automining single process has been executed. R6 §2.L3: \"The repository's executed agreement mechanism", fs=9, fill="#c0392b")
    s.text(14, y + 30, "is Hardhat automine ... provides ordering trivially and safety and liveness not at all\"; "
           "Besu, QBFT, Gasper, RocksDB, node permissioning are DESIGN.", fs=9, fill="#c0392b")
    s.footer(f"{R6SRC} §7 table (cell text verbatim, markdown stripped)", keys=("M", "D", "N"))
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
  ], "weakest: BP-LH-02 (key = SHA-256(vehicle_id)); gas #2"),
 ("Trace 3 — V2V SSI BSM", "IMP-L7.2-02 accept BSM", [
   ("L7.2", "IMP-L7.2-02", "receiver accepts BSM", "M"),
   ("L7.2", "IMP-L7.2-01", "freshness window", "M"),
   ("L2.3", "IMP-L2.3-06", "replay cache", "I"),
   ("LH.4", "HW-10", "receiver clock = GNSS", "D"),
   ("L1.1", "ALG-04", "ECDSA k1 / SHA-256", "I"),
   ("L1.2", "IMP-L1.2-01", "py cryptography", "I"),
   ("L5.2", "SCF-VPR-05", "veriKey attribute", "I"),
   ("L6.1", "ALG-23", "eth_getLogs replay", "M"),
   ("L0.4", "PRO-13", "JSON-RPC (unproven)", "M"),
   ("L5.1", "IMP-L5.1-03", "chain time for validTo", "I"),
  ], "weakest: BP-LH-04, BP-L0.4-02; #21 #27 #37"),
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
  ], "weakest: the setup (PF-11, t_s = 1); #56-#58"),
 ("Trace 6 — lifecycle attestation", "SCF-MOBI2-04 attestEvent", [
   ("L5.2", "SCF-MOBI2-04", "attestation stored", "M"),
   ("L1.2", "IMP-L1.2-11", "OZ ECDSA: low-s, chain-bound", "I"),
   ("L1.1", "ALG-03", "ecrecover recovery", "I"),
   ("L5.2", "SCF-MOBI2-01", "issuer role check", "I"),
   ("L4.2", "IMP-L4.2-03", "single registryAuthority key", "M"),
   ("L5.2", "SCF-VPR-01", "owner / validDelegate", "I"),
   ("L5.1", "IMP-L5.1-03", "chain time", "I"),
   ("L5.3", "PRO-21", "outer tx (Trace 1)", "I"),
  ], "weakest: BP-L4.2-02 governance key; #28"),
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
    s.footer(f"{R6SRC} §6 worked traces; step status from the matching §2 row", keys=("M", "I", "D", "N"),
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
           f"(R8 §7 states 301). Dot = rows of that category whose Sub-layer cell names that layer (size ~ √count);",
           fs=9, fill="#444")
    s.text(15, yb + 12, "a row naming several layers counts in each. Dashed box = home level. Arrow = descent to the lowest "
           "anchored layer. RV-SCF has no Sub-layer column: placed at L5.2 per §3.10. 'n/s' = no sub-layer stated (MET, part of GOV).",
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
    xl, cw, rh, y0 = 70, 34, 22, 190
    s = S(1000, y0 + rh * (len(body) + 1) + 120)
    s.header("FIG-R11", "Coverage matrix: 19 RV categories × 22 measurement dimensions",
             f"{R8SRC} §5 (cells parsed verbatim) and §1 (MD names)")
    colt = {m: [0, 0, 0] for m in mds}
    tot = [0, 0, 0]
    for j, m in enumerate(mds):
        x = xl + j * cw + cw / 2
        s.text(x + 3, y0 - 8, f"{tag(m)} {names[m][:24]}", fs=9, rot=-60)
    s.text(xl + len(mds) * cw + 8, y0 - 8, "meas/des/empty", fs=9, weight="bold")
    for i, r in enumerate(body):
        c = r[0]; y = y0 + i * rh
        s.text(xl - 6, y + 15, tag("RV-" + c), fs=9, anchor="end", weight="bold")
        rc = [0, 0, 0]
        for j, v in enumerate(r[1:]):
            x = xl + j * cw
            k = {"●": 0, "○": 1, "·": 2}[v.strip()]
            rc[k] += 1; colt[mds[j]][k] += 1; tot[k] += 1
            if k == 0:
                s.rect(x + 1, y + 1, cw - 2, rh - 2, fill=ST["M"]["fill"], stroke="#fff")
            elif k == 1:
                s.rect(x + 2, y + 2, cw - 4, rh - 4, fill=ST["D"]["fill"], stroke=ST["D"]["stroke"], dash="3,2", sw=1.2)
            else:
                s.rect(x + 1, y + 1, cw - 2, rh - 2, fill="#fff", stroke="#e2e2e2")
        s.text(xl + len(mds) * cw + 8, y + 15, f"{rc[0]} / {rc[1]} / {rc[2]}", fs=9)
    yt = y0 + len(body) * rh
    s.text(xl - 6, yt + 14, "measurable", fs=9, anchor="end", weight="bold")
    for j, m in enumerate(mds):
        s.text(xl + j * cw + cw / 2, yt + 14, colt[m][0], fs=9, anchor="middle", weight="bold",
               fill="#c0392b" if colt[m][0] == 0 else "#222")
    s.text(xl - 6, yt + 26, "design", fs=9, anchor="end")
    for j, m in enumerate(mds):
        s.text(xl + j * cw + cw / 2, yt + 26, colt[m][1], fs=9, anchor="middle", fill="#c46f00")
    s.text(15, yt + 48, f"Totals (computed from the parsed cells): measurable now (●) {tot[0]} · design only (○) {tot[1]} · "
           f"empty (·) {tot[2]} of {sum(tot)} cells. R8 §5 headline states 128 / 83 / 207.", fs=10, weight="bold")
    s.text(15, yt + 62, "Red column totals = no measurable cell: finality, decentralisation confidence, trilemma position, "
           "availability are not measurable on a single automining node (R8 §5).", fs=9, fill="#c0392b")
    s.footer(f"{R8SRC} §5; a measurable cell requires an M or Dv row, I does not count (R8 §7 decision 5)", keys=("M", "D", "N"))
    s.save("FIG-R11_coverage_matrix.svg")
    return tot

# =========================================================== FIG-R12
def fig_r12():
    rows = r8_rows()
    sec = R8[R8.index("### 4(a)"):R8.index("### 4(b)")]
    steps = []
    for l in sec.splitlines():
        m = re.match(r"^(\d+)\. \*\*(L[\dH][^*]*)\*\* (.*)$", l)
        if m:
            steps.append((m.group(1), m.group(2).strip(), clean(m.group(3))))
    mds_line = clean(re.search(r"\*\*MDs:\*\*(.*)", sec).group(1))
    rh, y0 = 50, 70
    s = S(1000, y0 + rh * len(steps) + 150)
    s.header("FIG-R12", "Anchor chain (a): VC endorsement — licence class upgrade (class 7 → class 5)",
             f"{R8SRC} §4(a) (steps parsed verbatim); per-step MD and St from the cited RV rows (§3)")
    s.text(140, y0 - 6, "Step (R8 §4(a) wording)", fs=10, weight="bold")
    s.text(700, y0 - 6, "RV rows cited → MD · St", fs=10, weight="bold")
    stmap = lambda t: "M" if t.startswith("M") else ("I" if t.startswith("I") else ("D" if t.startswith("Ds") else ("E" if t.startswith("E") else ("Dv" if t.startswith("Dv") else "N"))))
    for i, (n, layer, txt) in enumerate(steps):
        y = y0 + i * rh
        L = layer.split()[0]
        f, sc = LAYER[lay(L)]
        s.rect(15, y + 4, 110, rh - 12, fill=f, stroke=sc, sw=1.5, rx=4)
        s.text(24, y + 20, f"{n}.", fs=11, weight="bold", fill=sc)
        s.text(70, y + 20, layer, fs=10, anchor="middle", weight="bold", fill=sc)
        s.text(70, y + 33, LAYER_NAME[lay(L)], fs=9, anchor="middle", fill=sc)
        for li, t in enumerate(wrap(txt, 540)[:3]):
            s.text(140, y + 15 + li * 11, t, fs=9)
        cited = [t for t in dict.fromkeys(re.findall(r"RV-[A-Z]+-\d+", txt))]
        x = 700
        for k, rv in enumerate(cited[:3]):
            d = rows.get(rv, {})
            st = stmap(d.get("St", "—"))
            yy = y + 6 + k * 13
            s.marker(x, yy, st, 9)
            s.text(x + 13, yy + 8, f"{tag(rv)} · MD {d.get('MD', '?')} · {d.get('St', '?')}"[:52], fs=9)
        if i < len(steps) - 1:
            s.line(70, y + rh - 8, 70, y + rh + 3, arrow=True)
    yb = y0 + rh * len(steps) + 8
    s.text(15, yb + 6, "Whole-chain MDs (R8 §4(a)):", fs=10, weight="bold")
    for li, t in enumerate(wrap(mds_line, 960, 9)[:4]):
        s.text(15, yb + 20 + li * 11, t, fs=9)
    s.footer(f"{R8SRC} §4(a) + §3 rows; status of each RV row from its St cell", keys=("M", "I", "D", "N"),
             note="the chain as a whole is Ds (R8 §4(a))")
    s.save("FIG-R12_anchor_chain_vc_endorsement.svg")

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
}

def fig_r13():
    rows = md_table_after(R6, "## 4. New breaking points at the deeper levels")[1:]
    bps = []
    for r in rows:
        t = r[0]
        closed = clean(r[4]).lower()
        state = "open" if re.search(r"\bopen\b", closed) else ("closed" if "closed" in closed and "partial" not in closed else "partial")
        sub = "LH" if t.startswith("BP-LH") else re.match(r"BP-(L\d\.\d)", t).group(1)
        bps.append((t, sub, state))
    assert set(b[0] for b in bps) == set(BP_CLASS), "BP list changed in R6 §4 — update BP_CLASS"
    subs = []
    for _, sub, _ in bps:
        if sub not in subs: subs.append(sub)
    subs = list(reversed(subs))
    xl, cw, rh, y0 = 70, 104, 34, 78
    s = S(1000, y0 + rh * len(subs) + 110)
    s.header("FIG-R13", "New breaking points by sub-layer × attack class (extends Phase 1 FIG-R2)",
             f"{R6SRC} §4 (39 rows: BP-LH-01..06 + 33 BP-Lx.y)")
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
                s.text(xx + 5, yy, short, fs=9)
        s.text(xl + len(CLASSES) * cw + 25, y + 21, n, fs=10, anchor="middle")
    yb = y0 + rh * len(subs) + 14
    for k, (lab, col) in enumerate([("open (Closed-by cell says 'open')", "#c0392b"), ("partial / DESIGN mitigation", "#a36a00"), ("closed", "#2b6b2b")]):
        s.add(f'<circle cx="{25 + k * 230:.1f}" cy="{yb - 3:.1f}" r="3" fill="{col}"/>')
        s.text(32 + k * 230, yb, lab, fs=9)
    s.text(15, yb + 14, "Caveat: R6 §4 does not assign attack classes; the column placement is this figure's reading of each row's "
           "'Attack / failure' cell using FIG-R2's eight classes (replay and clock faults placed under ordering).", fs=9, fill="#666")
    s.footer(f"{R6SRC} §4; fill = Phase 1 layer colour (LH slate/brown); open/closed parsed from 'Closed by'", keys=())
    s.save("FIG-R13_new_breaking_points_heatmap.svg")

# =========================================================== FIG-R14
def fig_r14():
    s = S(1000, 640)
    s.header("FIG-R14", "Phase 1 to Phase 2 map: documents, directions and tag ownership",
             "Phase 1 README (tag table); PHASE2_SHARED_BRIEF §3–§4; R6 and R8 v0-1 headers")
    # Phase 1 lane
    s.rect(15, 54, 970, 150, fill="#fafafa", stroke="#ccc", rx=6)
    s.text(25, 72, "PHASE 1 (docs/roots/phase1/) — primitives and architectures, tags frozen", fs=11, weight="bold")
    p1 = [("R1", "Roots Lineage", ["L0–L7", "T-01..T-24", "T-I01..T-I22"]),
          ("R2", "Integration Scan", ["SOL-01..09", "options O1–O18"]),
          ("R3", "I2I Identity Stack", ["BP-L0-01..BP-L7-07", "FIG-R1..R6", "R1–R8, I1–I9"]),
          ("R4", "Proofs and Bounds", ["PF-01..31", "SYM-01..24"]),
          ("R5", "Pass Record", ["KD-R1..3, Q-R1..6", "CEV, LIM, MC"])]
    for i, (r, n, tags) in enumerate(p1):
        x = 30 + i * 192
        s.rect(x, 82, 176, 110, fill="#fff", stroke="#555", sw=1.3, rx=5)
        s.text(x + 8, 100, f"{tag(r)} {n}", fs=11, weight="bold")
        for k, t in enumerate(tags):
            s.text(x + 8, 118 + k * 14, t, fs=9, fill="#333")
        if i < 4:
            s.line(x + 176, 137, x + 190, 137, arrow=True)
    s.text(650, 232, "consumed (cited, never redefined) ↓", fs=10, anchor="middle", fill="#555")
    for x in (200, 500, 800):
        s.line(x, 205, x, 248, arrow=True, sw=1.4)
    # Phase 2 lane
    s.rect(15, 252, 970, 330, fill="#fafafa", stroke="#ccc", rx=6)
    s.text(25, 270, "PHASE 2 (docs/roots/phase2/) — deeper and complete: hardware → application, plus reverse register", fs=11, weight="bold")
    # mini stack
    sx, sy = 430, 290
    for i, L in enumerate(LAYERS):
        f, st = LAYER[L]
        s.rect(sx, sy + i * 26, 160, 24, fill=f, stroke=st, rx=3)
        s.text(sx + 80, sy + i * 26 + 16, f"{L} {LAYER_NAME[L]}", fs=9, anchor="middle", fill=st, weight="bold")
    s.line(sx - 14, sy + 9 * 26 - 4, sx - 14, sy + 4, arrow=True, sw=2, stroke="#2c5a8c")
    s.text(sx - 22, sy + 165, "forward: enables ↑ (bottom-up)", fs=9, anchor="middle", rot=-90, fill="#2c5a8c")
    s.line(sx + 174, sy + 4, sx + 174, sy + 9 * 26 - 4, arrow=True, sw=2, stroke="#a33")
    s.text(sx + 186, sy + 165, "reverse: anchors ↓ (top-down)", fs=9, anchor="middle", rot=90, fill="#a33")
    def box(x, y, w, h, title, status, lines, st):
        k = ST[st]
        s.rect(x, y, w, h, fill="#fff", stroke=k["stroke"], sw=1.6, rx=5, dash=k["dash"])
        s.text(x + 8, y + 16, title, fs=11, weight="bold")
        s.text(x + w - 8, y + 16, status, fs=9, anchor="end", fill="#666")
        for i, t in enumerate(lines):
            s.text(x + 8, y + 32 + i * 13, t, fs=9, fill="#333")
    box(30, 290, 340, 140, f"{tag('R6')} Full-Stack Atlas (forward)", "v0-1 issued", [
        "owns: HW-01..12 · PRO-01..22 · ALG-01..24", "IMP-<sublayer>-nn · SCF-<contract>-nn (117 rows)",
        "BP-LH-01..06 + 33 BP-Lx.y-nn · SOL-10..17", "sub-layers LH, L0.1–L7.3 populated",
        "§6 secured-by traces · §7 measured vs designed", "→ PF-⟦n⟧ placeholders handed to R7", "figures: FIG-R7, R8, R9, R13"], "I")
    box(30, 440, 340, 128, f"{tag('R7')} Theory and ECE Bounds", "pending (r7_calc.py only)", [
        "owns: PF-32+ · SYM-25+", "bounds ALG- (R6 defines, R7 bounds)",
        "resolves R6 PF-⟦1⟧..⟦24⟧ and R8 ⟦PF-??⟧", "moves R8 rows from unbounded to bounded"], "D")
    box(640, 290, 345, 140, f"{tag('R8')} Reverse Anchor Register", "v0-1 issued", [
        "owns: RV-<CAT>-nn (19 categories, 301 rows)", "MD-01..MD-22 · PAR-01..PAR-30 (declared only)",
        "cites R6 tags as ⟦…-??⟧ placeholders (v0-2)", "§4 five anchor chains · §5 coverage 19×22",
        "status scale adds I (implemented-unmeasured)", "figures: FIG-R10, R11, R12"], "I")
    box(640, 440, 345, 128, f"{tag('R9')} Professors' Panel Review", "pending", [
        "reviews R6–R8 (and R7) at v0-1 → v0-2", "record keys continue: KD-R4+, Q-R7+, F-R5+,",
        "LIM-R5+, MC-R6+ (all documents)", "visual agent owns FIG-R7+ (this set)"], "D")
    s.line(370, 360, 408, 360, arrow=True, stroke="#2c5a8c", sw=1.4)
    s.line(638, 360, 612, 360, arrow=True, stroke="#a33", sw=1.4)
    s.line(200, 430, 200, 440, arrow=True)
    s.line(640, 548, 370, 548, arrow=True, dash="4,3")
    s.text(510, 543, "⟦PF-??⟧ / PAR → R7", fs=9, anchor="middle", fill="#555")
    s.line(370, 572, 640, 572, arrow=True, dash="4,3")
    s.text(510, 567, "all → R9 review", fs=9, anchor="middle", fill="#555")
    s.footer("Phase 1 README §tags; PHASE2_SHARED_BRIEF §3 (tag namespaces) §4 (files); R6/R8 'Assigns' rows",
             keys=(), note="solid teal outline = issued v0-1 · dashed orange = pending (not yet written)")
    s.save("FIG-R14_phase1_phase2_map.svg")

if __name__ == "__main__":
    fig_r7(); fig_r8(); fig_r9()
    count, total = fig_r10()
    tot = fig_r11()
    fig_r12(); fig_r13(); fig_r14()
    print("RV rows parsed:", total, count)
    print("coverage totals ● ○ ·:", tot)
    for f in sorted(glob.glob(os.path.join(HERE, "FIG-R*.svg"))):
        minidom.parse(f)
        print("re-validated", os.path.basename(f))
    if UNSOURCED:
        print("UNSOURCED tags:", UNSOURCED)
        sys.exit(1)
    print("all printed tags found in source corpus")
