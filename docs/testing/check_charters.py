#!/usr/bin/env python3
"""Guard for docs/testing/charters/ (testing-suite replan §4 gate).

Fails if a charter cites a claim-register row (`#nn`) that does not exist in docs/MEASUREMENT_CONDITIONS.md, or if
a charter listed in the index is missing. Probe: `python3 docs/testing/check_charters.py --probe` injects a citation
of a non-existent row into a copy and shows the check fails on it (guide rule 1.3.11).
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CH = ROOT / "docs/testing/charters"
REG = ROOT / "docs/MEASUREMENT_CONDITIONS.md"


def register_rows():
    return {int(m) for m in re.findall(r"^\| ?#?(\d{1,3}) \|", REG.read_text(), re.M)}


def problems(texts):
    rows, out = register_rows(), []
    for name, text in texts.items():
        for m in sorted({int(x) for x in re.findall(r"(?<![\w&])#(\d{1,3})\b", text)}):
            if m not in rows:
                out.append(f"{name}: cites #{m}, which is not a register row")
    index = texts.get("README.md", "")
    for f in re.findall(r"`([A-Z]_[A-Z]+\.md)`", index):
        if f not in texts:
            out.append(f"README.md lists {f}, which does not exist")
    return out


def main():
    texts = {p.name: p.read_text() for p in sorted(CH.glob("*.md"))}
    if "--probe" in sys.argv:
        broken = dict(texts)
        broken["F_FUNCTIONAL.md"] += "\nProbe: see #999.\n"
        found = problems(broken)
        assert any("#999" in p for p in found), "probe failed: a citation of a non-existent row was not caught"
        print("probe ok: the check fails on a citation of a non-existent row")
        return
    found = problems(texts)
    for p in found:
        print("CHARTER:", p)
    if found:
        sys.exit(1)
    cited = sorted({int(x) for t in texts.values() for x in re.findall(r"(?<![\w&])#(\d{1,3})\b", t)})
    print(f"{len(texts)} charter files; every cited register row exists ({len(cited)} rows cited)")


if __name__ == "__main__":
    main()
