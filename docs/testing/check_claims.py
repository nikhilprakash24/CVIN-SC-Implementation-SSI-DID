#!/usr/bin/env python3
"""Claims checked against their result files (WM-2 step A5; audit T-F3).

    python3 docs/testing/check_claims.py           # report
    python3 docs/testing/check_claims.py --check   # CI: exit 1 on any problem

`docs/testing/claims.yaml` gives every claim-register row a stable id and, for every V row, the result files that
carry its numbers. The check fails if:
  - a register row has no entry, or an entry names a row that does not exist (ids must be unique);
  - a V row lists no source, or a source is not a tracked file;
  - a **bold** number in a V row's claim cell is in none of its sources (after normalising: thousands separators
    removed; a file value rounded to the decimals the row shows), unless the entry lists it under `derived:` with a
    reason; a `derived:` value that *is* found in a source is refused, so the list cannot hide drift.
Only the claim cell is checked: the status cell keeps old values as history on purpose.
"""
import json
import pathlib
import re
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTER = ROOT / "docs/MEASUREMENT_CONDITIONS.md"
CLAIMS = ROOT / "docs/testing/claims.yaml"
BOLD = re.compile(r"\*\*([^*]+)\*\*")
NUM = re.compile(r"(?<![-\w.#])(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?![\w])")


def register_rows():
    rows = {}
    for line in REGISTER.read_text().splitlines():
        m = re.match(r"^\| (\d+) \|(.*)\|\s*$", line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(2).split(" | ")]
        st = re.match(r"\s*\*\*([VESUB])", " ".join(cells[4:]))
        rows[int(m.group(1))] = {"claim": cells[0], "status": st.group(1) if st else "?"}
    return rows


def tracked():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return set(out.split())


def bold_numbers(claim):
    """Numbers inside bold spans of the claim cell, as (text, digits-without-commas, decimals)."""
    out = []
    for span in BOLD.findall(claim):
        for whole, frac in NUM.findall(span):
            digits = whole.replace(",", "") + (frac or "")
            if re.fullmatch(r"\d", digits) or (len(whole) == 4 and not frac and whole.startswith(("19", "20"))):
                continue  # single digits and years are labels, not measurements
            out.append(((whole + (frac or "")), digits, len(frac) - 1 if frac else 0))
    return out


def file_numbers(path):
    """Every number in a result file: JSON leaves, or every numeric token of a text file."""
    text = (ROOT / path).read_text(errors="replace")
    vals = set()
    if path.endswith(".json"):
        try:
            def walk(o):
                if isinstance(o, bool):
                    return
                if isinstance(o, (int, float)):
                    vals.add(float(o))
                elif isinstance(o, dict):
                    for v in o.values():
                        walk(v)
                elif isinstance(o, list):
                    for v in o:
                        walk(v)
            walk(json.loads(text))
        except json.JSONDecodeError:
            pass
    for whole, frac in NUM.findall(text.replace("_", "")):
        try:
            vals.add(float(whole.replace(",", "") + (frac or "")))
        except ValueError:
            pass
    return vals


def found(digits, decimals, vals):
    target = float(digits)
    for v in vals:
        if round(v, decimals) == target or round(v * 100, decimals) == target:  # also a fraction shown as a percent
            return True
    return False


def problems():
    rows, files = register_rows(), tracked()
    doc = yaml.safe_load(CLAIMS.read_text())
    entries = doc["claims"]
    out = []
    ids, by_row = set(), {}
    for e in entries:
        if e["id"] in ids:
            out.append(f"duplicate id {e['id']}")
        ids.add(e["id"])
        if e["row"] in by_row:
            out.append(f"row #{e['row']} has two entries")
        by_row[e["row"]] = e
        if e["row"] not in rows:
            out.append(f"{e['id']}: names row #{e['row']}, which is not in the register")
    for n in sorted(rows):
        if n not in by_row:
            out.append(f"register row #{n} has no entry in claims.yaml")
    cache = {}
    for n, r in sorted(rows.items()):
        e = by_row.get(n)
        if not e or r["status"] != "V":
            continue
        srcs = e.get("sources") or []
        if not srcs:
            out.append(f"#{n} ({e['id']}): V row with no source")
        for s in srcs:
            if s not in files:
                out.append(f"#{n} ({e['id']}): source {s} is not a tracked file")
        vals = set()
        for s in srcs:
            if s in files:
                vals |= cache.setdefault(s, file_numbers(s))
        derived = {str(d["value"]): d for d in (e.get("derived") or [])}
        for shown, digits, dec in bold_numbers(r["claim"]):
            hit = found(digits, dec, vals)
            if shown in derived:
                if hit:
                    out.append(f"#{n} ({e['id']}): {shown} is listed as derived but is in a source; remove it from derived")
            elif not hit:
                out.append(f"#{n} ({e['id']}): bold {shown} is in none of its sources")
    return out, len(rows), sum(1 for r in rows.values() if r["status"] == "V")


def main():
    out, n, v = problems()
    for p in out:
        print("PROBLEM:", p)
    print(f"claims: {n} register rows, {v} V; {len(out)} problems")
    if "--check" in sys.argv and out:
        sys.exit(1)


if __name__ == "__main__":
    main()
