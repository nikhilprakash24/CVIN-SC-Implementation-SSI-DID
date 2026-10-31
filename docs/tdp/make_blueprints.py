#!/usr/bin/env python3
"""Draw the six TDP blueprints (SVG) from committed data only.

After-action report 20, step T4. Every number on a drawing is read at build time from
docs/figures/dashboard_snapshot.json (itself generated from the results of record), cv2x-testbed/results/pki_vs_erc1056.json,
tools/run_identity/producers.json, docs/THREAT_MODEL.md, .github/workflows/*.yml, and the source files whose constants
or method names the drawing shows. Structural text (what a box is) is written here and cites its source file in the
bill of materials. Output is deterministic (no timestamps, no commit hashes), so CI can compare it byte for byte.

    python3 docs/tdp/make_blueprints.py           # writes docs/tdp/drawings/DWG-001.svg … DWG-006.svg
    python3 docs/tdp/make_blueprints.py --check   # CI: exit 1 if any drawing is stale

Drawing conventions (MIL-STD-31000B / ASME Y14.100, applied to a software system): border with zone marks, title
block (number, title, sheet, revision, scale, source data), revision block, numbered notes, bill of materials with
balloon references. Scale is "not to scale" on every sheet.
"""
import json
import pathlib
import re
import sys
import textwrap
from xml.sax.saxutils import escape

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/tdp/drawings"
SNAP = json.loads((ROOT / "docs/figures/dashboard_snapshot.json").read_text())
ISSUE = "2026-10-15"
REV = "B"
REVISIONS = [("A", "2026-10-15", "initial issue", "AAR-20"),
             ("B", "2026-10-31", "DWG-007 added; test paths; Layer 5 on DWG-001", "AAR-39")]
SHEETS = 7
W, H = 1400, 990
BG, INK, ACC, WARN, DIM, GRID = "#0f2d5c", "#e3ecf9", "#7cc9ff", "#ffb454", "#93a9cb", "#1b4280"
FONT = "DejaVu Sans Mono, Menlo, Consolas, monospace"


def fmt(n):
    return f"{n:,}" if isinstance(n, int) else str(n)


# ----------------------------------------------------------------------------- svg primitives
class Sheet:
    def __init__(self):
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, t, size=11, anchor="start", color=INK, weight="normal", rotate=None):
        tr = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
                 f'font-weight="{weight}"{tr}>{escape(str(t))}</text>')

    def lines(self, x, y, items, size=10.5, dy=14, color=INK):
        for i, t in enumerate(items):
            self.text(x, y + i * dy, t, size, color=color)

    def rect(self, x, y, w, h, stroke=INK, fill="none", dash=None, sw=1.2, rx=0):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" stroke="{stroke}" fill="{fill}" '
                 f'stroke-width="{sw}" rx="{rx}"{d}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, dash=None, sw=1.2, arrow=False):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = ' marker-end="url(#arrow)"' if arrow else ""
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{d}{m}/>')

    def path(self, d, stroke=INK, fill="none", sw=1.2, dash=None, arrow=False):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        m = ' marker-end="url(#arrow)"' if arrow else ""
        self.add(f'<path d="{d}" stroke="{stroke}" fill="{fill}" stroke-width="{sw}"{da}{m}/>')

    def circle(self, x, y, r, stroke=INK, fill="none", sw=1.2):
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" stroke="{stroke}" fill="{fill}" stroke-width="{sw}"/>')

    def balloon(self, x, y, n):
        self.circle(x, y, 9, ACC, BG, 1.4)
        self.text(x, y + 3.5, n, 9.5, "middle", ACC, "bold")

    def box(self, x, y, w, h, title, body=(), stroke=INK, title_size=11, body_size=9.5, dash=None, fill="none"):
        self.rect(x, y, w, h, stroke, fill, dash)
        self.text(x + 8, y + 15, title, title_size, color=stroke, weight="bold")
        if body:
            self.line(x, y + 21, x + w, y + 21, stroke, sw=0.8)
        self.lines(x + 8, y + 35, body, body_size, 12.5)

    def render(self):
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" xml:space="preserve" '
                f'font-family="{FONT}">\n'
                '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>'
                f'<pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                f'<line x1="0" y1="0" x2="0" y2="8" stroke="{WARN}" stroke-width="1"/></pattern></defs>\n'
                f'<rect width="{W}" height="{H}" fill="{BG}"/>\n' + "\n".join(self.parts) + "\n</svg>\n")


def frame(sh, number, title, sheet, notes, bom, sources):
    # border and zones
    sh.rect(14, 14, W - 28, H - 28, INK, sw=2)
    sh.rect(30, 30, W - 60, H - 60, INK, sw=0.8)
    for i in range(8):
        x = 30 + i * (W - 60) / 8
        sh.line(x, 14, x, 30, INK, sw=0.6)
        sh.line(x, H - 30, x, H - 14, INK, sw=0.6)
        sh.text(x + (W - 60) / 16, 26, str(i + 1), 9, "middle", DIM)
        sh.text(x + (W - 60) / 16, H - 18, str(i + 1), 9, "middle", DIM)
    for i, z in enumerate("ABCDEF"):
        y = 30 + i * (H - 60) / 6
        sh.line(14, y, 30, y, INK, sw=0.6)
        sh.line(W - 30, y, W - 14, y, INK, sw=0.6)
        sh.text(22, y + (H - 60) / 12 + 3, z, 9, "middle", DIM)
        sh.text(W - 22, y + (H - 60) / 12 + 3, z, 9, "middle", DIM)
    # classification banner
    sh.text(W / 2, 48, "UNCLASSIFIED // OPEN SOURCE (MIT) // RESEARCH TESTBED // NOT FOR PRODUCTION USE", 10, "middle", DIM)
    sh.text(W / 2, H - 42, "UNCLASSIFIED // OPEN SOURCE (MIT)", 10, "middle", DIM)
    # heading
    sh.text(44, 78, f"{number}  {title}", 17, color=INK, weight="bold")
    # revision block (top right)
    x0, y0 = 1010, 56
    sh.rect(x0, y0, 346, 48, INK, sw=1)
    sh.line(x0, y0 + 16, x0 + 346, y0 + 16, INK, sw=0.8)
    sh.text(x0 + 6, y0 + 12, "REV   DATE         DESCRIPTION                 REF", 9.5, color=DIM)
    for i, (rv, dt, desc, ref) in enumerate(REVISIONS[-2:]):
        sh.text(x0 + 6, y0 + 30 + i * 13, f"{rv}     {dt}   {desc[:36]:<36} {ref}", 8.5)
    # notes (bottom left)
    nx, ny = 44, 798
    sh.text(nx, ny, "NOTES", 11, weight="bold")
    wrapped = []
    for i, n in enumerate(notes):
        wrapped += textwrap.wrap(f"{i + 1}. {n}", 150, subsequent_indent="   ")
    sh.lines(nx, ny + 16, wrapped[:11], 9.3, 12.5)
    # bill of materials (right column)
    bx, by = 1000, 118
    sh.text(bx, by, "BILL OF MATERIALS (balloon → item)", 11, weight="bold")
    sh.rect(bx, by + 8, 356, 24 + 26 * len(bom), INK, sw=0.8)
    sh.text(bx + 6, by + 20, "NO  ITEM                      SOURCE", 9.5, color=DIM)
    for i, (desc, src) in enumerate(bom):
        y = by + 36 + i * 26
        sh.text(bx + 6, y, f"{i + 1:<3} {desc[:26]:<26}", 9.5)
        sh.text(bx + 6, y + 11, f"    {src[:52]}", 8.5, color=ACC)
    # title block (bottom right)
    tx, ty = 960, 822
    sh.rect(tx, ty, 396, 134, INK, sw=1.6)
    sh.line(tx, ty + 44, tx + 396, ty + 44, INK, sw=0.8)
    sh.line(tx, ty + 88, tx + 396, ty + 88, INK, sw=0.8)
    sh.line(tx + 198, ty + 44, tx + 198, ty + 134, INK, sw=0.8)
    sh.text(tx + 8, ty + 14, "CVIN-SC VEHICLE IDENTITY TESTBED — TECHNICAL DATA PACKAGE", 9.5, color=DIM)
    sh.text(tx + 8, ty + 32, title, 12, weight="bold")
    sh.text(tx + 8, ty + 58, "DRAWING NO.", 8.5, color=DIM)
    sh.text(tx + 8, ty + 76, number, 14, weight="bold", color=ACC)
    sh.text(tx + 206, ty + 58, "SHEET        REV      SCALE", 8.5, color=DIM)
    sh.text(tx + 206, ty + 76, f"{sheet} OF {SHEETS}       {REV}        NTS", 11)
    sh.text(tx + 8, ty + 101, "DRAWN  make_blueprints.py", 8.5, color=DIM)
    sh.text(tx + 8, ty + 113, "CHECKED  CI (--check, byte for byte)", 8.5, color=DIM)
    sh.text(tx + 8, ty + 125, f"ISSUE {ISSUE}  N. Prakash, UBC ECE", 8.5, color=DIM)
    sh.text(tx + 206, ty + 101, "SOURCE DATA", 8.5, color=DIM)
    for i, s in enumerate(sources[:2]):
        sh.text(tx + 206, ty + 113 + i * 12, s[:30], 8.5, color=ACC)


# ----------------------------------------------------------------------------- data readers
def adapter_ops():
    src = (ROOT / "1_blockchain-identity/benchmarks/adapters/IdentityAdapter.js").read_text()
    return re.findall(r"^\s+async (\w+)\(", src, re.M)


def provider_ops():
    src = (ROOT / "cv2x-testbed/identity/base.py").read_text()
    return re.findall(r"@abstractmethod\n\s+def (\w+)\(", src)


def reject_reasons():
    src = (ROOT / "cv2x-testbed/sumo/infrastructure_layer.py").read_text()
    seen, out = set(), []
    for r in re.findall(r'reason(?:, ok)? = "([a-z_]+)"', src):
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


def limits():
    src = (ROOT / "cv2x-testbed/sumo/infrastructure_layer.py").read_text()
    depth = re.search(r"^MAX_DEPTH\s*=\s*(\d+)", src, re.M)
    values = re.search(r"^MAX_VALUES\s*=\s*([\d_]+)", src, re.M)
    fr = (ROOT / "cv2x-testbed/identity/freshness.py").read_text()
    age = re.search(r"^DEFAULT_MAX_AGE_S\s*=\s*([\d.]+)", fr, re.M).group(1)
    fut = re.search(r"^DEFAULT_MAX_FUTURE_S\s*=\s*([\d.]+)", fr, re.M).group(1)
    cache = re.search(r"^DEFAULT_REPLAY_CACHE_SIZE\s*=\s*([\d_]+)", fr, re.M).group(1)
    return {"depth": depth.group(1) if depth else "?", "values": values.group(1).replace("_", ",") if values else "?",
            "age": age, "future": fut, "cache": fmt(int(cache.replace("_", "")))}


def pki_rows():
    d = json.loads((ROOT / "cv2x-testbed/results/pki_vs_erc1056.json").read_text())
    out = {}
    for r in d["results"]:
        out[(r["provider"], r["operation"])] = r
    return out


def ci_jobs():
    jobs = []
    for p in sorted((ROOT / ".github/workflows").glob("*.yml")):
        d = yaml.safe_load(p.read_text())
        jobs += [(p.name, j) for j in d["jobs"]]
    return jobs


def ci_document_checks():
    src = (ROOT / ".github/workflows/test-contracts.yml").read_text()
    return re.findall(r"python3 (docs/[\w/.-]+\.py) --check", src)


def threat_goals():
    out = []
    for line in (ROOT / "docs/THREAT_MODEL.md").read_text().splitlines():
        m = re.match(r"^\| (G\d) — ([^|]+) \| (.*) \| ([^|]+) \|\s*$", line)
        if m:
            out.append({"id": m.group(1), "goal": m.group(2).strip(), "text": m.group(3), "adv": re.findall(r"A\d", m.group(4))})
    assert len(out) == 8
    return out


# ----------------------------------------------------------------------------- drawings
PLANES = [
    ("P6", "PRESENTATION", "dashboard · result cards · presentation report · TDP (generated only)", "docs/figures/, docs/presentation/, docs/tdp/"),
    ("P5", "EVIDENCE", "run stamps (per-producer scope) · runs/ + promote · claim register · checkers", "tools/run_identity/, docs/testing/, docs/MEASUREMENT_CONDITIONS.md"),
    ("P4", "TRUST", "freshness policy (k) · revocation status · RSU cache · trusted-issuer list", "cv2x-testbed/identity/freshness.py, cv2x-testbed/sumo/infrastructure_layer.py"),
    ("P3", "CREDENTIAL", "W3C VC issue/present/verify · DID resolution (4 methods) · MOBI VID I/II · PKI certs", "2_w3c-ssi-layer/, cv2x-testbed/identity/standard/pki_identity.py"),
    ("P2", "LEDGER", "nine substrates + MOBI profile behind IdentityAdapter (JS) and IdentityProvider (Py)", "1_blockchain-identity/contracts/, benchmarks/adapters/, cv2x-testbed/identity/base.py"),
    ("P1", "MESSAGING", "BSM · SPaT signing and verification · in-process back-haul (controller, TMC)", "cv2x-testbed/sumo/sumo_identity_integration.py, infrastructure_layer.py"),
    ("P0", "MOBILITY", "MockMobility: positions, neighbours, contact times (no SUMO run of record)", "cv2x-testbed/sumo/sumo_identity_integration.py (MockMobility)"),
]
INTERFACES = {"P0": "MobilitySource", "P1": "Channel", "P2": "LedgerTarget", "P3": "CredentialSuite", "P4": "RevocationPolicy", "P5": "producer manifest"}


def dwg_001():
    sh = Sheet()
    t = SNAP["tests"]["stages"]
    reg = {s: 0 for s in "VSEUB"} | SNAP["register"]["by_status"]  # a status with no rows is absent from the snapshot
    producers = len(json.loads((ROOT / "tools/run_identity/producers.json").read_text())["producers"])
    jobs = ci_jobs()
    sh.text(44, 104, "SIDE ELEVATION — the seven planes of the testbed, Phase 1 code per plane; a plane depends only on the planes below it and on P5", 10.5, color=DIM)
    x, y0, w, h = 60, 122, 900, 84
    for i, (pid, name, code, path) in enumerate(PLANES):
        y = y0 + i * (h + 6)
        fill = "none"
        sh.rect(x, y, w, h, INK, fill, sw=1.4)
        sh.rect(x, y, 70, h, ACC, "none", sw=1.4)
        sh.text(x + 35, y + 36, pid, 20, "middle", ACC, "bold")
        sh.text(x + 35, y + 58, name, 8.5, "middle", ACC)
        sh.text(x + 84, y + 22, code, 10.5, weight="bold")
        sh.text(x + 84, y + 40, path, 9, color=ACC)
        if pid in INTERFACES:
            sh.text(x + 84, y + 58, f"interface (Phase 2 sketch): {INTERFACES[pid]} — reference implementation = the Phase 1 code above", 9, color=DIM)
        sh.balloon(x + w - 18, y + 18, i + 1)
        if i < len(PLANES) - 1:
            # dependency port between planes
            sh.line(x + w / 2, y + h, x + w / 2, y + h + 6, INK, sw=2)
    # P5 and P6 annotations with counts
    y5 = y0 + 1 * (h + 6)
    sh.text(x + 84, y5 + 74, f"register {SNAP['register']['rows']} rows: V {reg['V']} · S {reg['S']} · E {reg['E']} · U {reg['U']}   |   producers of record {producers}   |   CI jobs {len(jobs)}", 9.5, color=WARN)
    y6 = y0
    sh.text(x + 84, y6 + 74, f"suites at the last grand run: L1 {t['L1']['result']}  L1+L2 {t['L1+L2']['result']}  L3+L4 {t['L3+L4']['result']}", 9.5, color=WARN)
    # Layer 5 annotation (ZK-VIN gate and the Steward), on the credential and ledger planes
    y3 = y0 + 3 * (h + 6)
    sh.text(x + 84, y3 + 74, "layer 5 (5_zkp-agent-identity): ZK-VIN proof of VIN predicates (P3), ZkVinGate on P2, the Steward on P4 — DWG-007", 9.5, color=WARN)
    # dependency rule, drawn as a dimension line on the left
    yt, yb = y0, y0 + 7 * (h + 6) - 6
    sh.line(46, yt, 46, yb, DIM, sw=0.8)
    sh.line(42, yt, 50, yt, DIM, sw=0.8)
    sh.line(42, yb, 50, yb, DIM, sw=0.8)
    sh.text(40, (yt + yb) / 2, "DEPENDENCY: DOWNWARD ONLY (+P5)", 8.5, "middle", DIM, rotate=-90)
    notes = [
        "Planes and interfaces per docs/phase2/ARCHITECTURE.md section 1 and 2; Phase 1 code per plane as listed there.",
        "P0 has no SUMO run of record (SC-22): every message-path result uses MockMobility (--simulate).",
        "P1 has no radio, MAC or channel model; the back-haul is an in-process bus (register #44-#48 conditions).",
        "P2 gas is M1 (in-process Hardhat, chain 31337); no M2 (public testnet) run exists (N-11).",
        "Counts on P5 and P6 are read from docs/figures/dashboard_snapshot.json (the last grand run; its commit is in the snapshot).",
        "Balloon numbers refer to the bill of materials; each item names the directory or file it stands for.",
        "Layer 5 (zero-knowledge VIN predicates and the agent wrapper, register #56 to #62) sits across P2 to P4 and is drawn on DWG-007.",
    ]
    bom = [(f"{p[0]} {p[1]}", p[3].split(",")[0]) for p in PLANES] + [("Layer 5", "5_zkp-agent-identity/")]
    frame(sh, "DWG-001", "GENERAL ARRANGEMENT — SEVEN-PLANE SYSTEM", 1, notes, bom, ["dashboard_snapshot.json", "producers.json"])
    return sh.render()


def dwg_002():
    sh = Sheet()
    gas = SNAP["gas"]["table"]
    sec = SNAP["security"]["per_standard"]
    fr = SNAP["harness"]["frontier"]
    order = ["ERC-1056", "CVIN-Combined", "ERC-1155", "LSP8", "ERC-721", "ERC-4337", "ERC-725", "ERC-725xy", "ERC-735", "MOBI-VID-V2"]
    key = {"ERC-1056": "erc1056", "CVIN-Combined": "cvin", "ERC-1155": "erc1155", "LSP8": "lsp8", "ERC-721": "erc721",
           "ERC-4337": "erc4337", "ERC-725": "erc725", "ERC-725xy": "erc725xy", "ERC-735": "erc735", "MOBI-VID-V2": None}
    sh.text(44, 104, "EXPLODED VIEW — ten substrate cylinders between the JS adapter manifold (benchmarks) and the Python provider manifold (testbed)", 10.5, color=DIM)
    # top manifold
    ops = adapter_ops()
    sh.rect(60, 120, 900, 76, ACC, sw=1.4)
    sh.text(70, 138, "MANIFOLD A — IdentityAdapter (JS): one declared operation catalogue; a substrate without a primitive throws NotSupported, never emulates", 10, color=ACC, weight="bold")
    for i, chunk in enumerate(textwrap.wrap(" ".join(ops), 150)[:3]):
        sh.text(70, 156 + i * 13, chunk, 9)
    # cylinders
    cx0, cy, cw, ch = 70, 232, 82, 300
    for i, std in enumerate(order):
        x = cx0 + i * 89
        sh.add(f'<ellipse cx="{x + cw / 2}" cy="{cy}" rx="{cw / 2}" ry="10" stroke="{INK}" fill="{BG}" stroke-width="1.3"/>')
        sh.line(x, cy, x, cy + ch, INK, sw=1.3)
        sh.line(x + cw, cy, x + cw, cy + ch, INK, sw=1.3)
        sh.path(f"M{x},{cy + ch} a{cw / 2},10 0 0,0 {cw},0", INK, sw=1.3)
        sh.text(x + cw / 2, cy + 30, std, 9.5, "middle", INK, "bold")
        g = gas[std]
        sh.text(x + cw / 2, cy + 56, "create", 8, "middle", DIM)
        sh.text(x + cw / 2, cy + 70, fmt(g["createIdentity"]), 9.5, "middle", WARN)
        sh.text(x + cw / 2, cy + 92, "deploy", 8, "middle", DIM)
        sh.text(x + cw / 2, cy + 106, fmt(g["deployRegistry"]) if g["deployRegistry"] else "per identity", 9, "middle", WARN)
        sh.text(x + cw / 2, cy + 128, "update", 8, "middle", DIM)
        sh.text(x + cw / 2, cy + 142, fmt(g["updateAttribute"]) if g["updateAttribute"] else "n/a", 9, "middle", WARN)
        sh.text(x + cw / 2, cy + 164, "revoke", 8, "middle", DIM)
        sh.text(x + cw / 2, cy + 178, fmt(g["revoke"]) if g.get("revoke") else "n/a", 9, "middle", WARN)
        s = sec.get(std)
        sh.text(x + cw / 2, cy + 204, "harness", 8, "middle", DIM)
        sh.text(x + cw / 2, cy + 218, f"{s.get('DEFENDED', 0)} DEF / {s.get('N/A', 0)} n/a" if s else "not in harness", 8.5, "middle", INK if s else DIM)
        k = key[std]
        marks = []
        if k and k in fr["cost"]:
            marks.append("C")
        if k and k in fr["costRead"]:
            marks.append("R")
        if k and k in fr["all"]:
            marks.append("6")
        sh.text(x + cw / 2, cy + 244, "frontier", 8, "middle", DIM)
        sh.text(x + cw / 2, cy + 258, " ".join(marks) if k else "profile", 9.5, "middle", ACC, "bold")
        sh.balloon(x + cw - 6, cy + 16, i + 1)
        sh.line(x + cw / 2, 196, x + cw / 2, cy - 10, INK, sw=0.8)
    # bottom manifold
    pops = provider_ops()
    sh.rect(60, 560, 900, 64, ACC, sw=1.4)
    sh.text(70, 578, "MANIFOLD B — IdentityProvider (Python): PKI, centralized, ERC-1056, MOBI VID providers behind one interface (cv2x-testbed/identity/base.py)", 10, color=ACC, weight="bold")
    sh.text(70, 596, " ".join(pops), 9)
    sh.text(70, 612, "providers attach to the cylinders they drive: ERC-1056 (vehicle profile) and MOBI VID V2; PKI and centralized are in-process baselines, not cylinders", 9, color=DIM)
    for i in (0, 9):
        x = cx0 + i * 89
        sh.line(x + cw / 2, cy + ch + 10, x + cw / 2, 560, INK, sw=0.8, dash="4,3")
    # legend
    sh.text(60, 660, "LEGEND  create/deploy/update/revoke = exact receipt gas, M1 (register #25; 30/30 runs byte-identical)   harness = strict revert cells, register #28", 9.5, color=DIM)
    sh.text(60, 676, "frontier (register #36, harness run of record): C = on the cost-only frontier · R = cost + read path · 6 = all six criteria.  CVIN-Combined carries no mark: dominated by ERC-4337 on all six.", 9.5, color=DIM)
    sh.text(60, 692, f"create-identity spread on this table: {fmt(SNAP['gas']['create_min']['gas'])} ({SNAP['gas']['create_min']['standard']}) to {fmt(SNAP['gas']['create_max']['gas'])} ({SNAP['gas']['create_max']['standard']}) = {SNAP['gas']['create_spread']}x", 9.5, color=WARN)
    notes = [
        "Each cylinder is one contract set under 1_blockchain-identity/contracts/<standard>/; MOBI-VID-V2 is an application profile measured beside the nine.",
        "Operation definitions differ per standard and are declared per row in the register; a ratio is meaningful only under a stated definition (#6).",
        "ERC-4337 and LSP8 are feature-minimal representative implementations (chapter 4 caveats); their gas is a lower bound.",
        "Frontier marks come from the six-criterion analysis of harness run 2026-10-09T02-09-36Z_7a9a996; the O(1) credential check is a declared design property.",
        "The two ERC-1056 variants (uPort-style registry; vehicle-profile registry in cv2x-testbed) are distinct options in the sandbox manifests; this sheet shows the benchmark column.",
    ]
    bom = [(std, f"contracts/{std}" if std != "MOBI-VID-V2" else "contracts/MOBI") for std in order]
    bom = [(d, "1_blockchain-identity/" + s) for d, s in bom]
    frame(sh, "DWG-002", "SUBSTRATE ASSEMBLY — TEN CYLINDERS, TWO MANIFOLDS", 2, notes, bom, ["gas_benchmark.json", "attack_results.json"])
    return sh.render()


def dwg_003():
    sh = Sheet()
    lim = limits()
    reasons = reject_reasons()
    v = SNAP["v2v"]["per_population"]
    i1 = SNAP["infrastructure"]["I1"]
    pki = pki_rows()
    sh.text(44, 104, "PROCESS FLOW — the message verification engine: eight stations in series; every rejection leaves by the exhaust with a named reason", 10.5, color=DIM)
    stations = [
        ("S1 INTAKE", ["package = {message,", " sender_did, signature,", " credential,", " identity_type}"], []),
        ("S2 LIMITS", [f"depth <= {lim['depth']}", f"values <= {lim['values']}", "walked, no recursion", "(D37)"], ["malformed"]),
        ("S3 FRESHNESS", ["signed generation", " time (T-9)", f"max age {lim['age']} s", f"max future {lim['future']} s"], ["stale", "future"]),
        ("S4 REPLAY", ["key = (receiver,", " sender, sha256 of", " signed bytes)", f"cache {lim['cache']} (D29)"], ["replay"]),
        ("S5 SIGNATURE", ["EIP-191 secp256k1", "recover address", "DID = network +", " address (D41)"], ["unsigned", "wrong_key"]),
        ("S6 KEY SOURCE", ["WARM: cached addr.", "COLD: verify cred.:", " trusted issuer,", " validUntil, revoked"], ["no_credential", "credential_invalid", "subject_mismatch", "revoked", "expired"]),
        ("S7 AUTHORITY", ["permitted msg type", "field binding:", " intersection, rsu", "(D28, D38)"], ["not_permitted", "binding"]),
        ("S8 OUTPUT", ["(ok, latency_ms,", " cold, reason)", "trust decision", "per message"], []),
    ]
    x0, y0, bw, bh, gap = 50, 130, 108, 100, 6
    for i, (name, body, rej) in enumerate(stations):
        x = x0 + i * (bw + gap)
        sh.box(x, y0, bw, bh, name, body, ACC if i in (0, 7) else INK, 10, 8.5)
        sh.balloon(x + bw - 10, y0 + bh - 10, i + 1)
        if i < len(stations) - 1:
            sh.line(x + bw, y0 + bh / 2, x + bw + gap, y0 + bh / 2, INK, sw=1.6, arrow=True)
        if rej:
            sh.line(x + bw / 2, y0 + bh, x + bw / 2, y0 + bh + 28, WARN, sw=1.2, arrow=True)
            sh.lines(x + 4, y0 + bh + 42, rej, 8.5, 11, WARN)
    sh.line(x0, y0 + bh + 110, x0 + 8 * (bw + gap) - gap, y0 + bh + 110, WARN, sw=1.4)
    sh.text(x0, y0 + bh + 124, f"EXHAUST — rejection reasons as named in the code ({len(reasons)}):", 9, color=WARN)
    sh.text(x0, y0 + bh + 137, ", ".join(reasons), 9, color=WARN)
    sh.text(x0, y0 + bh + 152, "register #45: each of 15 registered checks rejected for its expected reason in 30/30 runs; 0 legitimate SPaT rejected of 138,895", 9, color=DIM)
    # timing scale (log)
    ty = 430
    sh.text(x0, ty, "TIMING — per-message verification cost (medians), log scale; the budget marks are the ones the latency budget declares", 10.5, weight="bold")
    sx0, sx1 = 60, 940
    lo, hi = 0.05, 200.0

    import math

    def X(ms):
        return sx0 + (math.log10(ms) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (sx1 - sx0)
    base = ty + 150
    sh.line(sx0, base, sx1, base, INK, sw=1)
    for tick in (0.1, 0.5, 1, 5, 10, 50, 100):
        sh.line(X(tick), base, X(tick), base + 6, INK, sw=1)
        sh.text(X(tick), base + 18, f"{tick} ms", 8.5, "middle", DIM)
    bars = [
        ("PKI verify (in-process, CA sig + CRL)", pki[("pki_standard", "verify_message")]["median_ms"], "#21"),
        ("SSI BSM verify WARM (cached key)", v["ssi"]["warm"]["median"], "#27"),
        ("SPaT verify WARM (verifier v3)", i1["spat_warm_ms"], "#44"),
        ("SSI BSM verify COLD (credential verify)", v["ssi"]["cold"]["median"], "#27"),
        ("SPaT verify COLD", i1["spat_cold_ms"], "#44"),
        ("ERC-1056 verify UNCACHED (4 RPC, local node)", pki[("erc1056_did", "verify_message")]["median_ms"], "#21"),
    ]
    for i, (label, ms, row) in enumerate(bars):
        y = ty + 22 + i * 20
        sh.rect(sx0, y, X(ms) - sx0, 12, ACC if ms < 0.5 else WARN, ACC if ms < 0.5 else WARN, sw=0.8)
        sh.text(X(ms) + 6, y + 10, f"{ms:.3f} ms  {label}  [{row}]", 8.5)
    for mark, label in ((0.5, "0.5 ms: 100 neighbours in half the interval (P*(0.5)=100)"), (100, "100 ms: BSM interval (SAE J2945/1, 10 Hz)")):
        sh.line(X(mark), ty + 16, X(mark), base, WARN, sw=1, dash="5,4")
        sh.text(X(mark) + 4, ty + 14, label, 8, color=WARN)
    sh.text(x0, base + 40, "Bars are medians from different runs and hosts (register conditions); they are placed on one scale for orientation only. Within-run comparisons are the ones the register makes (guide 1.1.7).", 8.5, color=DIM)
    notes = [
        "Station order follows InfrastructureLayer.verify (cv2x-testbed/sumo/infrastructure_layer.py) and FreshnessPolicy (cv2x-testbed/identity/freshness.py); the V2V SSI layer runs S1, S3-S6, S8.",
        "Limits (depth, values, window, cache) are read from the source constants at build time; a change in code changes this sheet and fails --check until regenerated.",
        "S6 cold path verifies the attached credential through the canonical VC layer (2_w3c-ssi-layer/verifiable-credentials) against the trusted-issuer list; warm path uses the cached signing address.",
        "Residual, by design: a fresh message relayed within the window to a receiver that never heard it passes S4 (register #45 'not covered').",
        "Timing bars: #21 host 2.10 GHz Xeon (PKI, ERC-1056 uncached, n=50); #27 mock mobility, 30 seeded runs; #44 verifier v3, 30 runs. No radio or channel time is included anywhere.",
    ]
    bom = [("verify(), stations", "cv2x-testbed/sumo/infrastructure_layer.py"), ("FreshnessPolicy", "cv2x-testbed/identity/freshness.py"),
           ("SSIIdentityLayer", "cv2x-testbed/sumo/sumo_identity_integration.py"), ("CredentialVerifier", "2_w3c-ssi-layer/verifiable-credentials/vc_verifier.py"),
           ("I2 checks (15)", "docs/design/INFRASTRUCTURE_PREREG.md"), ("v3 tests (26)", "sandbox/py-suites/L3-ssi/test_infrastructure_v3.py"),
           ("PKI baseline", "cv2x-testbed/identity/standard/pki_identity.py"), ("timing data", "cv2x-testbed/results/pki_vs_erc1056.json")]
    frame(sh, "DWG-003", "VERIFICATION ENGINE — EIGHT-STATION PROCESS FLOW", 3, notes, bom, ["dashboard_snapshot.json", "pki_vs_erc1056.json"])
    return sh.render()


def dwg_004():
    sh = Sheet()
    f, p = SNAP["freshness"]["full"], SNAP["freshness"]["probe"]
    i3 = SNAP["infrastructure"]["I3"]["per_k"]
    sh.text(44, 104, "MECHANISM — the freshness governor: a per-sender message counter that forces a chain re-check every k-th message; two refresh modes", 10.5, color=DIM)
    # governor schematic
    sh.box(60, 124, 300, 150, "CACHE ENTRY (per receiver, per sender)", ["address      signing key, from the last resolution", "seen         messages accepted since the last re-check", "credential   id, validUntil (warm expiry check, D30)", "", "rule: if seen % k == 0 → REFRESH before verifying", "k = 1: every message · k = ∞: never (reported only)"], INK, 10.5, 9)
    sh.box(400, 124, 260, 150, "REFRESH MODE A — FULL", ["resolve the DID document:", " owner, delegates, attributes via", " changed() event walk (4 RPC, #32)", f"t_chain {f['t_chain_ms']} ms (host {f['host'].split('@')[-1].strip()})", f"t_local {f['t_local_ms']} ms", "producer: experiment_freshness_k.py"], WARN, 10.5, 9)
    sh.box(690, 124, 270, 150, "REFRESH MODE B — PROBE", ["one eth_call getIdentityInfo:", " changed? no → keep cache", "          yes → full resolution", f"t_chain {p['t_chain_ms']} ms (host {p['host'].split('@')[-1].strip()})", f"t_local {p['t_local_ms']} ms", "--refresh-mode probe (#37)"], ACC, 10.5, 9)
    sh.line(360, 199, 400, 199, INK, sw=1.4, arrow=True)
    sh.line(660, 199, 690, 199, INK, sw=1.4, arrow=True, dash="4,3")
    sh.text(380, 186, "every k-th", 8, "middle", DIM)
    # curve table
    ty = 300
    sh.text(60, ty, "GOVERNOR CURVE — verify latency by k (medians and p95, ms), each mode on its own host; absolute values are not comparable across the two rows", 10.5, weight="bold")
    sh.text(60, ty + 20, "k        FULL median   FULL p95     PROBE median  PROBE p95     I3 (RSU, k) max accepted after revocation / bound", 9.5, color=DIM)
    for i, (a, b) in enumerate(zip(f["by_k"], p["by_k"])):
        y = ty + 38 + i * 16
        k = a["k"]
        r = i3.get(k, {})
        bound = r.get("bound")
        sh.text(60, y, f"{k:<8} {a['median_ms']:<13} {a['p95_ms']:<12} {b['median_ms']:<13} {b['p95_ms']:<13} {r.get('max', '—')} / {bound if bound is not None else '∞'}   {r.get('verdict', '')}", 9.5, WARN if k == "1" else INK)
    # small plot
    px0, py0, pw, ph = 620, ty + 34, 330, 130
    sh.rect(px0, py0, pw, ph, DIM, sw=0.8)
    ks = [a["k"] for a in f["by_k"]]
    import math
    vmax = max(max(a["median_ms"] for a in f["by_k"]), max(b["median_ms"] for b in p["by_k"]))

    def P(i, val):
        return px0 + 30 + i * (pw - 60) / (len(ks) - 1), py0 + ph - 12 - (math.log10(val) - math.log10(0.1)) / (math.log10(vmax * 1.5) - math.log10(0.1)) * (ph - 24)
    for series, color, label in ((f["by_k"], WARN, "FULL"), (p["by_k"], ACC, "PROBE")):
        pts = [P(i, a["median_ms"]) for i, a in enumerate(series)]
        sh.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), color, sw=1.6)
        for x, y in pts:
            sh.circle(x, y, 3, color, color)
        sh.text(pts[-1][0] + 6, pts[-1][1] + 3, label, 8.5, color=color)
    for i, k in enumerate(ks):
        sh.text(P(i, 0.1)[0], py0 + ph + 12, f"k={k}", 8.5, "middle", DIM)
    sh.text(px0, py0 - 6, "median verify ms vs k (log y)", 8.5, color=DIM)
    # staleness bound
    sy = 500
    sh.box(60, sy, 900, 96, "STALENESS BOUND (the price of the cache)", [
        "A revoked sender is accepted for at most k − 1 further messages after revocation; k = ∞ never stops (#32: 0 / 4 / 24 for k = 1 / 5 / 25, 35/35 trials; #37: 280/280 trials; #46 RSU analogue above).",
        "A count of messages, not a time: the cache does not expire; at 10 Hz the count converts to time only for a sender that keeps transmitting.",
        "Fail-open case found and fixed: a verifier whose clock lags the chain by more than 900 s accepted a revoked key (D51; fixed at WM-2 C0; #32/#37 re-run pending at A3b).",
        "The thesis defends no k as 'fitting': zero staleness (k = 1) and P*(0.5) >= 100 were not achieved together on either host (D-12 withdrawn; #52 reaches it at k = 25 on a third host).",
    ], INK, 10.5, 9)
    notes = [
        "Sources: cv2x-testbed/results/freshness_k.json (#32, full refresh) and freshness_k_probe.json (#37, probe), read through the dashboard snapshot; I3 from infrastructure_revocation.json (#46).",
        "The two modes were measured on different hosts; #52 re-ran both at their own code on one host and attributes the difference between #32 and #37 to the host, not the code.",
        "The knee (the k at which P*(0.5) reaches 100) depends on 0.5 − t_local and is the most host-sensitive figure; it is never quoted without its t_local.",
        "Mechanism as built in cv2x-testbed/identity/erc1056_provider.py and the harness flags --refresh-k / --refresh-mode of experiment_freshness_k.py.",
    ]
    bom = [("freshness experiment", "cv2x-testbed/scripts/experiment_freshness_k.py"), ("ERC-1056 provider", "cv2x-testbed/identity/erc1056_provider.py"),
           ("RSU cache, re-check", "cv2x-testbed/sumo/infrastructure_layer.py"), ("full-refresh run", "cv2x-testbed/results/freshness_k.json"),
           ("probe-refresh runs", "cv2x-testbed/results/freshness_k_probe*.json"), ("one-host comparison", "cv2x-testbed/results/freshness_k_c3/"),
           ("D51 regression test", "cv2x-testbed/tests/test_d51_chain_time.py")]
    frame(sh, "DWG-004", "FRESHNESS GOVERNOR — RE-CHECK CADENCE k", 4, notes, bom, ["freshness_k.json", "freshness_k_probe.json"])
    return sh.render()


def dwg_005():
    sh = Sheet()
    producers = json.loads((ROOT / "tools/run_identity/producers.json").read_text())["producers"]
    reg = {s: 0 for s in "VSEUB"} | SNAP["register"]["by_status"]  # a status with no rows is absent from the snapshot
    jobs = ci_jobs()
    checks = ci_document_checks()
    sh.text(44, 104, "PROCESS LINE — how a number travels from a producer to a document, and the inspection station at every transfer", 10.5, color=DIM)
    st = [
        ("1 PRODUCER", [f"{len(producers)} registered", "producers.json names the", "file that runs, its inputs", "and its result paths"], INK),
        ("2 RUN", ["writes runs/<name>/<id>/", "untracked; manifest.json", "with the stamp"], INK),
        ("3 STAMP", ["commit · code_dirty over", "the resolved import closure", "+ declared inputs · tree_dirty", "· scope_sha (stamp.py)"], ACC),
        ("4 PROMOTE", ["promote.py copies to the", "tracked path only if clean;", "refuses: dirty run, other", "commit, changed scope, edited", "output, undeclared destination"], ACC),
        ("5 RESULT OF RECORD", ["tracked JSON/CSV/MD with", "environment header;", "check_stamps.py --check-", "coverage: 0 uncovered"], INK),
        ("6 REGISTER ROW", [f"#1-#{SNAP['register']['rows']}: V {reg['V']} S {reg['S']}", f"E {reg['E']} U {reg['U']}; tag, source,", "commit, status, caveats", "(MEASUREMENT_CONDITIONS.md)"], WARN),
        ("7 GENERATORS", ["snapshot · registers · charter", "· cards · presentation · TDP", "read files, never prose;", "--check compares output"], INK),
        ("8 DOCUMENTS + CI", [f"{len(jobs)} CI jobs; document step", f"runs {len(checks)} --check commands;", "stale-figure checker over", "every tracked .md"], ACC),
    ]
    x0, y0, bw, bh, gap = 60, 126, 215, 104, 13
    for i, (name, body, color) in enumerate(st):
        row, col = divmod(i, 4)
        x, y = x0 + col * (bw + gap), y0 + row * (bh + 30)
        sh.box(x, y, bw, bh, name, body, color, 10, 8.8)
        sh.balloon(x + bw - 10, y + bh - 10, i + 1)
        if col < 3:
            sh.line(x + bw, y + bh / 2, x + bw + gap, y + bh / 2, INK, sw=1.6, arrow=True)
        elif i == 3:
            sh.path(f"M{x + bw / 2},{y + bh} L{x + bw / 2},{y + bh + 15} L{x0 + bw / 2},{y + bh + 15} L{x0 + bw / 2},{y + bh + 28}", INK, sw=1.6, arrow=True)
    iy = y0 + 2 * (bh + 30) + 2
    sh.text(x0, iy, "INSPECTION STATIONS AT THE TRANSFERS", 10.5, weight="bold", color=WARN)
    insp = ["2→3  probe_run_identity.sh: the producing-code dirty flag shown to fire per producer (CI)",
            "3→4  test_promote.py: 13 refusal tests (CI); a dirty run, another commit, a changed scope, an edited output or an undeclared destination is refused",
            "5→6  build_register.py --check; a new V row needs a result card (make_result_cards.py) and, if it reports gas, a class (gas_charter.py)",
            "6→7  check_docs_numbers.py: a superseded figure cannot be cited as current in any tracked .md outside the history globs",
            "7→8  every generated document is rebuilt and compared byte for byte in CI; a stale page fails the job"]
    for i, t in enumerate(insp):
        sh.text(x0, iy + 16 + i * 14, "⊳ " + t, 9, color=WARN)
    # CI job table and document checks
    cy = 496
    sh.text(60, cy, "CI JOBS (parsed from .github/workflows)", 10.5, weight="bold")
    for i, (wf, job) in enumerate(jobs):
        sh.text(60, cy + 18 + i * 14, f"{i + 1}. {job:<22} {wf}", 9.5)
    sh.text(480, cy, "DOCUMENT CHECKS IN THE hardhat-tests JOB (parsed)", 10.5, weight="bold")
    for i, c in enumerate(checks):
        sh.text(480, cy + 18 + i * 14, f"{i + 1}. {c} --check", 9.5, color=ACC if "tdp" in c else INK)
    # rules strip
    ry = 660
    sh.box(60, ry, 900, 104, "RULES THAT HOLD THE LINE (docs/STYLE_AND_RIGOUR_GUIDE.md)", [
        "1.1.2  a number enters a chapter only with a register row of status V       1.1.6  a run of record comes from a clean tree; a dirty run is discarded and the discard written down",
        "1.2.7  a pre-registration is never edited; departures are dated amendments    1.3.10 figures are generated from committed data by committed scripts",
        "1.3.11 every guard is shown to fire (a probe in CI)                            1.3.7  delegated work is accepted only after the orchestrator's own re-run of its gate",
        "Known inert flag: the metrics harness's dirtyMeasured (D33) until A6; the whole-tree flag is the criterion meanwhile (register section 5.F).",
    ], INK, 10.5, 8.5)
    notes = [
        "Producer registry: tools/run_identity/producers.json (hand-maintained) → scopes.json (generated by stamp.py --write; checked by stamp.py --check in CI).",
        "A run at an earlier commit cannot pass the promote step (the stamp's commit must be HEAD); such runs are copied with a manifest as a declared deviation (reports 16, 19).",
        "The contribution record is regenerated at each pass's close and not checked in CI, because it depends on git history.",
        "Generated-document checks and the stale-figure checker are the inspection stations a reviewer re-runs; their probes are the evidence that they can trip.",
    ]
    bom = [("producer registry", "tools/run_identity/producers.json"), ("stamp helper", "tools/run_identity/stamp.py"), ("promote step", "tools/run_identity/promote.py"),
           ("stamp inventory", "docs/testing/check_stamps.py"), ("claim register", "docs/MEASUREMENT_CONDITIONS.md"), ("stale-figure checker", "docs/testing/check_docs_numbers.py"),
           ("document step", ".github/workflows/test-contracts.yml"), ("grand runner", "sandbox/grand/run.py")]
    frame(sh, "DWG-005", "EVIDENCE LINE — PRODUCER TO DOCUMENT", 5, notes, bom, ["producers.json", "workflows/*.yml"])
    return sh.render()


def dwg_006():
    sh = Sheet()
    goals = threat_goals()
    sec = SNAP["security"]["per_standard"]
    tm = (ROOT / "docs/THREAT_MODEL.md").read_text()
    sh.text(44, 104, "ENVELOPE — adversaries A1-A4 against goals G1-G8 (docs/THREAT_MODEL.md), the lens that tests each goal, and the harness verdict per substrate", 10.5, color=DIM)
    advs = [("A1", "network / message (Dolev-Yao)"), ("A2", "malicious registered party"), ("A3", "key compromise"), ("A4", "passive on-chain observer")]
    gx0, gy0, cw, rh = 300, 150, 80, 34
    sh.text(gx0 - 240, gy0 - 14, "ADVERSARY \\ GOAL", 9.5, color=DIM)
    for j, g in enumerate(goals):
        sh.text(gx0 + j * cw + cw / 2, gy0 - 14, g["id"], 10, "middle", ACC, "bold")
        sh.text(gx0 + j * cw + cw / 2, gy0 - 2, g["goal"][:13], 7, "middle", DIM)
    for i, (aid, name) in enumerate(advs):
        y = gy0 + i * rh
        sh.text(gx0 - 240, y + 22, f"{aid}  {name}", 9.5)
        for j, g in enumerate(goals):
            sh.rect(gx0 + j * cw, y, cw, rh, DIM, sw=0.6)
            if aid in g["adv"]:
                sh.circle(gx0 + j * cw + cw / 2, y + rh / 2, 7, ACC, ACC)
    # lens row
    ly = gy0 + 4 * rh + 10
    sh.text(gx0 - 240, ly + 22, "LENS", 9.5, weight="bold")
    for j, g in enumerate(goals):
        lens = "1 revert suite" if g["id"] in ("G1", "G2", "G3", "G4") else "2 threat matrix"
        sh.rect(gx0 + j * cw, ly, cw, rh, DIM, sw=0.6)
        sh.text(gx0 + j * cw + cw / 2, ly + 21, lens, 7.5, "middle", INK)
    # narrowed goals
    ny = ly + rh + 10
    sh.text(gx0 - 240, ny + 22, "NARROWED", 9.5, weight="bold", color=WARN)
    narrow = {"G3": "chain id (D52)", "G4": "attest (D54)"}
    assert "D52" in tm and "D54" in tm
    for j, g in enumerate(goals):
        sh.rect(gx0 + j * cw, ny, cw, rh, DIM, sw=0.6, fill="url(#hatch)" if g["id"] in narrow else "none")
        if g["id"] in narrow:
            sh.rect(gx0 + j * cw + 8, ny + 9, cw - 16, 16, WARN, BG, sw=0.6)
            sh.text(gx0 + j * cw + cw / 2, ny + 21, narrow[g["id"]], 7.5, "middle", WARN)
    # per substrate harness
    hy = ny + rh + 40
    sh.text(60, hy, "LENS 1 — STRICT REVERT HARNESS PER SUBSTRATE (register #28): DEFENDED = reverted with the documented reason; n/a = cell declared not applicable", 10.5, weight="bold")
    stds = list(sec.keys())
    for i, s in enumerate(stds):
        x = 60 + i * 100
        d, na = sec[s].get("DEFENDED", 0), sec[s].get("N/A", 0)
        sh.rect(x, hy + 14, 92, 56, INK, sw=1)
        sh.text(x + 46, hy + 30, s, 8.5, "middle", INK, "bold")
        sh.text(x + 46, hy + 46, f"{d} DEF", 10, "middle", ACC, "bold")
        sh.text(x + 46, hy + 60, f"{na} n/a", 8.5, "middle", DIM)
    tot = SNAP["security"]["total"]
    sh.text(60, hy + 92, f"total: {tot['DEFENDED']} DEFENDED, {tot['N/A']} not applicable, 0 other outcomes. Lens 2 (G5-G8) is the comparative threat matrix: security_matrix.json, scored, not reverted.", 9.5, color=WARN)
    # assumptions and out of scope
    ay = hy + 120
    sh.box(60, ay, 440, 150, "TRUST ASSUMPTIONS (threat model section 3)", ["T1 chain integrity: the ledger executes faithfully; consensus attacks out", "T2 issuer honesty at issuance: an authorised first attestation is trusted", "T3 key custody: owners protect keys; A3 models the failure", "T4 verifier correctness: relying parties run correct logic", "", "Adversary is computationally bounded: no ECDSA forgery, no keccak preimage"], INK, 10.5, 9)
    sh.box(520, ay, 440, 150, "OUT OF SCOPE (threat model section 6)", ["51 % / consensus-level attacks · cryptographic primitive breaks", "verifier or HSM compromise · physical and side-channel attacks", "economic / MEV manipulation of the fee market", "governance attacks on upgradeable contracts (tested contracts are not)", "", "Claims are bounded to the application / contract layer"], INK, 10.5, 9)
    notes = [
        "Dots: the adversary the goal counters, parsed from the goal table of docs/THREAT_MODEL.md section 4 at build time.",
        "Lens assignment per section 5 of the threat model: G1-G4 by the executable revert suite; G5-G8 by the comparative threat matrix.",
        "Hatched cells are goals the threat model itself narrows: G3 (ERC-1056 signed operations omit the chain id, D52, upstream behaviour) and G4 for attestations (D54, WM-2 C2).",
        "Found-and-fixed: MOBI attestEvent accepted an attestation without verifying the attester's signature (G2/G3); the fix costs gas that the register prices (#28).",
        "The harness proves a barrier exists where it reverts; it does not prove the absence of other paths (register #28 caveat; C8 asks what another implementation would show).",
    ]
    bom = [("threat model", "docs/THREAT_MODEL.md"), ("revert harness", "1_blockchain-identity/test/L2-identity-system/security/securityScenarios.test.js"),
           ("attack results", "4_comparison-framework/security-analysis/results/attack_results.json"), ("threat matrix", "4_comparison-framework/security-analysis/results/security_matrix.json"),
           ("attestEvent regression", "1_blockchain-identity/test/L2-identity-system/per-option/MOBIVID/attestEventRegression.test.js"), ("freshness/replay tests", "cv2x-testbed/tests/test_t9_freshness.py")]
    frame(sh, "DWG-006", "THREAT ENVELOPE — ADVERSARIES, GOALS, LENSES", 6, notes, bom, ["THREAT_MODEL.md", "attack_results.json"])
    return sh.render()


def dwg_007():
    sh = Sheet()
    L5 = ROOT / "5_zkp-agent-identity/results"
    gas = json.loads((L5 / "gas_zk.json").read_text())
    bench = json.loads((L5 / "zkvin_bench.json").read_text())
    att = json.loads((L5 / "attacks.json").read_text())
    g = gas["gas"]
    sh.text(44, 104, "PROCESS FLOW — layer 5: a vehicle proves a VIN predicate without the VIN (ZK-VIN) and a bounded agent (the Steward) operates the identity", 10.5, color=DIM)
    # pipeline
    st = [
        ("1 VIN + SALT", ["owner's VIN and salt", "never leave the vault", "(steward/vault.py)"], INK),
        ("2 COMMITMENT", [f"anchor on chain", f"{fmt(g['anchor_commitment'])} gas", "ZkVinGate (M1)"], INK),
        ("3 PROVE", [f"Groth16, circom 2.2.2", f"prove median {bench['prove_ms']['median']:.1f} ms", f"(N={bench['prove_ms']['n']}, descriptive)", f"proof {bench['proof_calldata_bytes']} B calldata"], ACC),
        ("4 VERIFY OFF CHAIN", [f"verify median {bench['verify_ms']['median']:.2f} ms", f"(N={bench['verify_ms']['n']})", f"{bench['public_signals']} public signals"], ACC),
        ("5 ADMIT ON CHAIN", [f"ZkVinGate.admit", f"{fmt(g['admit_with_groth16'])} gas", "an IDTx: effect gated", "on knowledge of opening"], WARN),
        ("6 SCHNORR PoK", [f"ecrecover-based verifier", f"{fmt(g['schnorr_prove_tx'])} gas (tx)", f"deploy {fmt(g['deploy_schnorr_verifier'])}"], INK),
    ]
    x0, y0, bw, bh, gap = 50, 126, 145, 104, 8
    for i, (name, body, color) in enumerate(st):
        x = x0 + i * (bw + gap)
        sh.box(x, y0, bw, bh, name, body, color, 9.5, 8.6)
        sh.balloon(x + bw - 10, y0 + bh - 10, i + 1)
        if i < len(st) - 1:
            sh.line(x + bw, y0 + bh / 2, x + bw + gap, y0 + bh / 2, INK, sw=1.6, arrow=True)
    ex = bench["expectations"]
    ex.update(gas["expectations"])
    ey = y0 + bh + 22
    sh.text(x0, ey, "PRE-REGISTERED EXPECTATIONS AS THEY FELL (Plan 1, written before any run):", 10, weight="bold")
    for i, (k, v) in enumerate(list(ex.items()) + list(att["expectations"].items())):
        sh.text(x0, ey + 16 + i * 13, f"{v:<5} {k[:150]}", 8.8, color=WARN if v == "FAIL" else INK)
    # steward loop
    sy = ey + 16 + 13 * (len(ex) + len(att["expectations"])) + 18
    sh.text(x0, sy, "THE STEWARD — a language model proposes, a deterministic kernel disposes; leakage is audited against a bit budget per verifier set", 10, weight="bold")
    loop = [("POLICY", ["owner's rules in", "plain English", "→ signed policy", "(policy.py, compiler.py)"]),
            ("KERNEL", ["deterministic", "admit / refuse /", "coarsen a request", "(kernel.py)"]),
            ("LEAKAGE AUDIT", [f"prior {att['prior_bits']} bits", f"budget {att['budget_bits']} bits", "per verifier set", "(leakage.py)"]),
            ("LEARNER", ["responder trained on", "seeds 10,000–12,999", "evaluated on 1–30", "(learner.py)"]),
            ("DELEGATION", ["the agent's own DID", "and credential from", "the owner (P3)", "(delegation.py)"])]
    for i, (name, body) in enumerate(loop):
        x = x0 + i * (bw + gap)
        sh.box(x, sy + 12, bw, 92, name, body, ACC, 9.5, 8.6)
        if i < len(loop) - 1:
            sh.line(x + bw, sy + 58, x + bw + gap, sy + 58, INK, sw=1.4, arrow=True)
    # attack table
    ay = sy + 120
    sh.text(x0, ay, "NARROWING ATTACK, seeds 1–30 (Sim): adversary bits (mean / max) and honest service (mean) per defence × variant", 10, weight="bold")
    sh.text(x0, ay + 16, f"{'defence':<18}{'single bits':<16}{'sybil bits':<16}{'service single':<16}{'service sybil':<16}", 8.8, color=DIM)
    res = att["results"]
    for i, d in enumerate(["none", "static_cap", "budget_only", "steward_fixed", "steward", "steward_no_budget"]):
        a, b = res[f"{d}|single"], res[f"{d}|sybil"]
        sh.text(x0, ay + 30 + i * 13, f"{d:<18}{a['adversary_bits']['mean']:.2f} / {a['adversary_bits']['max']:.2f}      {b['adversary_bits']['mean']:.2f} / {b['adversary_bits']['max']:.2f}      {a['honest_service']['mean']:.3f}           {b['honest_service']['mean']:.3f}", 8.8, WARN if d == "steward" else INK)
    sh.text(x0, ay + 30 + 6 * 13 + 4, f"Z-E6 parts: leakage bound held on all 60 runs = {att['z_e6_parts']['leakage_bound_held_on_all_60']}; seeds below 90 % service = {att['z_e6_parts']['seeds_below_90pct_service']}; minimum service = {att['z_e6_parts']['min_service']}", 8.8, color=WARN)
    notes = [
        "Every number is read from 5_zkp-agent-identity/results/{gas_zk,zkvin_bench,attacks}.json at build time; register rows #56 to #62 (status V) are their rows of record.",
        "The Groth16 keys come from an INSECURE single-party setup and zkid is not constant time: research code, not a deployable system (layer 5 README).",
        "Proving time has N = 10 and is descriptive only (latency charter, WM-2 B3); the verify time (N = 30) conforms; both are one host.",
        "Z-E6 FAIL is reported as it fell: the Steward holds leakage under budget on every run but serves under 90 % of honest requests on 25 of 60; a global budget alone bounds leakage as well (register #61).",
        "The insider variant (amendment A2) is post hoc and enters neither Z-E5 nor Z-E6; the learner was not retrained on it.",
    ]
    bom = [("ZK-VIN circuit", "5_zkp-agent-identity/circuits/zkvin.circom"), ("gate contract", "5_zkp-agent-identity/contracts/ZkVinGate.sol"),
           ("Groth16 verifier", "5_zkp-agent-identity/contracts/Groth16Verifier.sol"), ("prove / verify", "5_zkp-agent-identity/scripts/prove_and_verify.js"),
           ("gas producer", "5_zkp-agent-identity/scripts/measure_gas.js"), ("Schnorr verifier", "5_zkp-agent-identity/contracts/SchnorrEcrecoverVerifier.sol"),
           ("the Steward", "5_zkp-agent-identity/steward/"), ("attack simulator", "5_zkp-agent-identity/attacks/run_attacks.py"),
           ("pre-registration", "docs/zkp/PLAN_1_ZKP_AND_AGENT_IDENTITY.md")]
    frame(sh, "DWG-007", "ZK-VIN GATE AND THE STEWARD — LAYER 5", 7, notes, bom, ["gas_zk.json", "attacks.json"])
    return sh.render()


DRAWINGS = {"DWG-001": dwg_001, "DWG-002": dwg_002, "DWG-003": dwg_003, "DWG-004": dwg_004, "DWG-005": dwg_005, "DWG-006": dwg_006, "DWG-007": dwg_007}


def main():
    OUT.mkdir(exist_ok=True)
    outputs = {OUT / f"{k}.svg": fn() for k, fn in DRAWINGS.items()}
    if "--check" in sys.argv:
        stale = [p.name for p, s in outputs.items() if not p.exists() or p.read_text() != s]
        if stale:
            print("stale drawings: " + ", ".join(stale) + "; run make_blueprints.py")
            sys.exit(1)
        print(f"{len(outputs)} drawings up to date")
        return
    for p, s in outputs.items():
        p.write_text(s)
        print("wrote", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
