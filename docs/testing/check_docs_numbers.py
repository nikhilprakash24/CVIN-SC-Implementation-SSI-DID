#!/usr/bin/env python3
"""Fail if a citing document quotes a superseded figure as current (plan 2026-10-09 P3.4; TSR R7).

Superseded values, their current replacements and register rows are listed in
docs/testing/stale_numbers.yaml.

Scope: every tracked Markdown file except the `history` globs (dated records, plans, reviews and
generated run reports, which keep the values of their time on purpose). Before matching, a line is
normalised so formatting cannot hide a value: thousands separators (`1,404,108`, `1 404 108`,
thin/no-break spaces) are removed between digit groups, and `ms` / `%` are separated from the number
(`0.165ms` -> `0.165 ms`, `93.2%` -> `93.2 %`). Patterns are written against the normalised form.

A line may keep a superseded value only when it marks it as history: a whole-word marker
(`history_markers`, matched as regular expressions with word boundaries), or "old -> new": an arrow
(`->`, `→`) after the value **and the entry's current value after that arrow**. An arrow alone does
not excuse a value, because arrows also write ranges (`52,170 → 1,680,816` cites 52,170 as current).
Hardened after after-action reports 11 (findings C3, C4) and 12 (range arrows).

    python3 docs/testing/check_docs_numbers.py          # report; exit 1 on any hit
"""
import fnmatch
import pathlib
import re
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
CFG = yaml.safe_load((ROOT / "docs/testing/stale_numbers.yaml").read_text())
MARKERS = re.compile(r"(?<!\w)(?:" + "|".join(CFG["history_markers"]) + r")(?!\w)", re.IGNORECASE)
ARROW = re.compile(r"->|→")
GROUP_SEP = re.compile(r"(?<=\d)[,    ](?=\d{3}(?!\d))")


def normalise(line: str) -> str:
    prev = None
    while prev != line:                     # repeat: 1,404,108 needs two passes for overlapping groups
        prev, line = line, GROUP_SEP.sub("", line)
    line = re.sub(r"(?<=\d)(ms|%)", r" \1", line)
    return line


def files():
    tracked = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    return [ROOT / p for p in tracked if not any(fnmatch.fnmatch(p, g) for g in CFG["history"])]


def main():
    hits = []
    for f in files():
        for n, raw in enumerate(f.read_text(errors="replace").splitlines(), 1):
            line = normalise(raw)
            if MARKERS.search(line):
                continue
            arrows = [m.start() for m in ARROW.finditer(line)]
            for e in CFG["entries"]:
                cur = re.search(r"\d[\d.]*", normalise(e["current"]))
                for m in re.finditer(e["pattern"], line):
                    later = [a for a in arrows if a > m.start()]
                    # the current value must appear as a whole number after the arrow (audit finding B2-F7:
                    # a substring test let "150" match inside "1500")
                    if later and cur and re.search(r"(?<![\d.])" + re.escape(cur.group(0)) + r"(?![\d])", line[later[0]:]):
                        continue                # old -> new, with the current value on the new side
                    hits.append((str(f.relative_to(ROOT)), n, e, raw.strip()))
                    break
    for path, n, e, line in hits:
        print(f"{path}:{n}: '{e['pattern']}' superseded -> {e['current']} (register #{e['row']}): {line[:140]}")
    print(f"{len(hits)} stale figure(s) in {len({h[0] for h in hits})} file(s); {len(files())} files scanned")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
