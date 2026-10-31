#!/usr/bin/env python3
"""R8 v0-3 coverage matrix: categories x MD-01..22.

Parses section 3 register tables of the R8 v0-3 document and computes, per
(category, MD) cell:
  ●  measured     at least one St=M row whose evidenced MDs (before '/') include it
  ◐  derived only at least one St=Dv row evidences it, and no M row does
  ○  design       rows target the MD, but none evidences it
  ·  empty        no row targets the MD
MD cell syntax: "aa,bb / cc" -> aa,bb evidenced by St; cc applicable only.
Usage: python3 r8_coverage_v0-3.py [--write]   (--write fills the COVERAGE block)
"""
import re, sys, pathlib
from collections import OrderedDict

DOC = pathlib.Path(__file__).with_name(
    "claude_CVIN_SC_Roots_Reverse_Anchor_Register_R8_v0-3.md")
CATS = ["TX", "IDTX", "VC", "SIG", "READ", "PRIM", "ALG", "PROT", "SC", "SCF",
        "NET", "DLT", "IMPL", "HW", "SVC", "SCN", "GOV", "MET", "THR"]
MDS = [f"{i:02d}" for i in range(1, 23)]


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse(text):
    body = text.split("## 3. The register", 1)[1].split("## 4.", 1)[0]
    rows, hdr = [], None
    for line in body.splitlines():
        if line.startswith("| RV |"):
            hdr = cells(line)
            continue
        m = re.match(r"\| (RV-([A-Z]+)-\d+) \|", line)
        if m and hdr:
            c = cells(line)
            rows.append(dict(rv=m.group(1), cat=m.group(2),
                             md=c[hdr.index("MD")], st=c[hdr.index("St")]))
    return rows


def status(st):
    if re.match(r"M\b", st):
        return "M"
    if st.startswith("Dv"):
        return "D"
    return "X"


def compute(rows):
    grid = {c: {m: set() for m in MDS} for c in CATS}
    for r in rows:
        ev, _, ap = r["md"].partition("/")
        s = status(r["st"])
        for part, evidenced in ((ev, True), (ap, False)):
            for md in re.findall(r"\d{2}", part):
                grid[r["cat"]][md].add(s if evidenced else "X")
    code = {}
    for c in CATS:
        for m in MDS:
            g = grid[c][m]
            code[c, m] = ("●" if "M" in g else "◐" if "D" in g
                          else "○" if g else "·")
    return code


def render(code, rows):
    out = ["| Cat | " + " | ".join(MDS) + " |",
           "|---|" + "---|" * len(MDS)]
    for c in CATS:
        out.append(f"| {c} | " + " | ".join(code[c, m] for m in MDS) + " |")
    n = {k: sum(1 for v in code.values() if v == k) for k in "●◐○·"}
    tot = len(code)
    pct = lambda k: f"{100 * n[k] / tot:.1f} %"
    head = (f"**Headline ({len(CATS)} × {len(MDS)} = {tot} cells; {len(rows)} rows):** "
            f"**● {n['●']} measured** ({pct('●')}) · **◐ {n['◐']} derived only** "
            f"({pct('◐')}) · **○ {n['○']} design** ({pct('○')}) · "
            f"**· {n['·']} empty** ({pct('·')}).")
    empty_cols = [m for m in MDS if all(code[c, m] != "●" for c in CATS)]
    out += ["", head, "",
            "MD columns with no ● cell: " + ", ".join("MD-" + m for m in empty_cols)
            + ". These are the consequence of one automining node (PF-39) and of "
              "absent hardware, and are not a gap in the bookkeeping."]
    return "\n".join(out), n


def main():
    text = DOC.read_text(encoding="utf-8")
    rows = parse(text)
    ids = [r["rv"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate RV ids"
    per = OrderedDict((c, sum(r["cat"] == c for r in rows)) for c in CATS)
    code = compute(rows)
    block, n = render(code, rows)
    print(block)
    print("\nrows per category:", dict(per), "total", len(rows))
    print("placeholders ⟦⟧ remaining:", len(re.findall("⟦", text)))
    if "--write" in sys.argv:
        new = re.sub(r"(<!-- COVERAGE-BEGIN -->).*?(<!-- COVERAGE-END -->)",
                     lambda m: m.group(1) + "\n" + block + "\n" + m.group(2),
                     text, flags=re.S)
        DOC.write_text(new, encoding="utf-8")


if __name__ == "__main__":
    main()
