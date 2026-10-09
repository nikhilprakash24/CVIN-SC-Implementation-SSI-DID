#!/usr/bin/env python3
"""Fail if a citing document quotes a superseded figure as current (plan 2026-10-09 P3.4; TSR R7).

Superseded values, their current replacements and register rows are listed in
docs/testing/stale_numbers.yaml. A line may keep a superseded value only when it marks it as
history (a `history_markers` entry on the same line).

    python3 docs/testing/check_docs_numbers.py          # report; exit 1 on any hit
"""
import glob
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
CFG = yaml.safe_load((ROOT / "docs/testing/stale_numbers.yaml").read_text())
EXCLUDE = {"docs/thesis/CRUX_REGISTER.md"}  # generated from the register, which keeps history in its cells


def files():
    out = []
    for pat in CFG["scope"]:
        out += [pathlib.Path(p) for p in glob.glob(str(ROOT / pat), recursive=True)]
    return sorted({p for p in out if p.is_file() and str(p.relative_to(ROOT)) not in EXCLUDE})


def main():
    hits = []
    for f in files():
        for n, line in enumerate(f.read_text().splitlines(), 1):
            if any(m in line for m in CFG["history_markers"]):
                continue
            for e in CFG["entries"]:
                if re.search(e["pattern"], line):
                    hits.append((str(f.relative_to(ROOT)), n, e, line.strip()))
    for path, n, e, line in hits:
        print(f"{path}:{n}: '{e['pattern']}' superseded -> {e['current']} (register #{e['row']}): {line[:140]}")
    print(f"{len(hits)} stale figure(s) in {len({h[0] for h in hits})} file(s)")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
