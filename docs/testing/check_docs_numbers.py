#!/usr/bin/env python3
"""Fail if a citing document quotes a superseded figure as current (plan 2026-10-09 P3.4; TSR R7).

Superseded values, their current replacements and register rows are listed in
docs/testing/stale_numbers.yaml.

Scope: every tracked Markdown, SVG (text elements; report 40), HTML and TeX file (report 41) except the `history` globs (dated records, plans, reviews and
generated run reports, which keep the values of their time on purpose). Before matching, a line is
normalised so formatting cannot hide a value: thousands separators (`1,404,108`, `1 404 108`,
thin/no-break spaces) are removed between digit groups, and `ms` / `%` are separated from the number
(`0.165ms` -> `0.165 ms`, `93.2%` -> `93.2 %`). Patterns are written against the normalised form.

A line may keep a superseded value only when it marks it as history: a whole-word marker
(`history_markers`, matched as regular expressions with word boundaries), or "old -> new": an arrow
(`->`, `→`) after the value **and the entry's current value after that arrow**. An arrow alone does
not excuse a value, because arrows also write ranges (`52,170 → 1,680,816` cites 52,170 as current).
Hardened after after-action reports 11 (findings C3, C4) and 12 (range arrows).

An entry may list `pending` globs: hits in those files are printed as PENDING with the entry's `pending_reason`
and do not fail the check. This is for a superseded value found by an audit whose fix waits on a decision (report 37:
the chapter audit's stale #27 values wait on WM-2 D1). A hit in any other file still fails; a pending glob that no
longer has a hit is reported as CLEARED so the entry can be tightened.

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
    tracked = subprocess.run(["git", "ls-files", "*.md", "*.svg", "*.html", "*.tex"], cwd=ROOT, capture_output=True, text=True,
                             check=True).stdout.split()
    return [ROOT / p for p in tracked if not any(fnmatch.fnmatch(p, g) for g in CFG["history"])]


def _html_lines(raw):
    """HTML (report 41): visible text and inline script data, line by line. Style blocks and tags are removed with
    their newlines kept, so a hit's line number is the page's; entities are decoded; script text is kept because a
    page's numbers often live in an embedded JSON snapshot."""
    import html
    raw = re.sub(r"<style\b.*?</style>", lambda m: "\n" * m.group(0).count("\n"), raw, flags=re.S | re.I)
    raw = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), raw, flags=re.S)
    raw = re.sub(r"<[^>]*>", lambda m: " " + "\n" * m.group(0).count("\n"), raw)
    return [(n, html.unescape(l).replace("\u00a0", " ")) for n, l in enumerate(raw.splitlines(), 1) if l.strip()]


def _tex(line):
    """TeX (report 41): thousands groups written 1{,}757{,}881 or 1\\,757\\,881, and math markers, normalised."""
    line = re.sub(r"(?<=\d)\{,\}(?=\d)", ",", line)
    line = re.sub(r"(?<=\d)\\[,;:!](?=\d)", "", line)
    line = line.replace("\\%", "%").replace("\\times", "×").replace("$", "").replace("~", " ")
    return re.sub(r"\\(?:text|mathrm|textbf|mathbf)\{([^{}]*)\}", r"\1", line)


SVG_TEXT = re.compile(r"<text\b[^>]*>(.*?)</text>", re.S)


def lines_of(f):
    """(line number, text) pairs. Markdown: every line. SVG (report 40, T-19): the text content of each <text>
    element, tags removed, entities decoded, no-break spaces read as spaces, numbered by the line it starts on."""
    raw = f.read_text(errors="replace")
    if f.suffix == ".html":
        return _html_lines(raw)
    if f.suffix == ".tex":
        return [(n, _tex(l)) for n, l in enumerate(raw.splitlines(), 1)]
    if f.suffix != ".svg":
        return list(enumerate(raw.splitlines(), 1))
    import html
    out = []
    for m in SVG_TEXT.finditer(raw):
        text = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).replace("\u00a0", " ").replace("\u202f", " ")
        if text.strip():
            out.append((raw.count("\n", 0, m.start()) + 1, text))
    return out


def main():
    hits, pending, pend_seen = [], [], set()
    for f in files():
        for n, raw in lines_of(f):
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
                    rel = str(f.relative_to(ROOT))
                    globs = [g for g in e.get("pending", []) if fnmatch.fnmatch(rel, g)]
                    if globs:
                        pending.append((rel, n, e, raw.strip()))
                        pend_seen.update((e["pattern"], g) for g in globs)
                    else:
                        hits.append((rel, n, e, raw.strip()))
                    break
    for path, n, e, line in hits:
        print(f"{path}:{n}: '{e['pattern']}' superseded -> {e['current']} (register #{e['row']}): {line[:140]}")
    for path, n, e, line in pending:
        print(f"PENDING {path}:{n}: '{e['pattern']}' -> {e['current']} (#{e['row']}; {e.get('pending_reason', '')})")
    for e in CFG["entries"]:
        for g in e.get("pending", []):
            if (e["pattern"], g) not in pend_seen:
                print(f"CLEARED: '{e['pattern']}' has no hit left in {g}; remove that pending glob")
    print(f"{len(pending)} pending (known, waiting on a decision)")
    print(f"{len(hits)} stale figure(s) in {len({h[0] for h in hits})} file(s); {len(files())} files scanned")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
