#!/usr/bin/env python3
"""Build TDP-006, the failure mode, effects and criticality worksheet, from the defect log and the threat model.

After-action report 20, step T5. Inputs: docs/DEFECT_LOG.md (every defect row, parsed with the dashboard's own
rules so the counts agree with docs/figures/dashboard_snapshot.json), docs/thesis/cruxes.yaml (which thesis crux
each defect bears on), docs/THREAT_MODEL.md (goals and the adversary each counters). Nothing is re-rated: the log's
severity letter is carried, and the MIL-STD-1629A severity class beside it is a declared translation, stated once.

    python3 docs/tdp/make_fmeca.py            # writes TDP-006
    python3 docs/tdp/make_fmeca.py --check    # CI: exit 1 if stale, or if the counts disagree with the snapshot
"""
import importlib.util
import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/tdp/TDP-006_FMECA.md"
LOG = ROOT / "docs/DEFECT_LOG.md"
SNAP = ROOT / "docs/figures/dashboard_snapshot.json"

# Declared translation (not a re-rating). The log rates by effect on a thesis claim or a security property.
CLASS = {"H": "II Critical (affects a thesis claim or a security property)",
         "M": "III Marginal (wrong behaviour, bounded impact)",
         "L": "IV Minor (cosmetic or advisory)"}
# Subsystem by path prefix of the "Where" cell (the seven planes of docs/phase2/ARCHITECTURE.md section 1).
PLANES = [("1_blockchain-identity/contracts", "P2 Ledger"), ("cv2x-testbed/contracts", "P2 Ledger"),
          ("MOBIVIDRegistry", "P2 Ledger"), ("ERC1056Registry", "P2 Ledger"), ("CVIN", "P2 Ledger"),
          ("ERC-", "P2 Ledger"), ("OpenZeppelin", "P2 Ledger"), ("Registry", "P2 Ledger"), ("ERC", "P2 Ledger"),
          ("did_resolver", "P3 Credential"), ("2_w3c-ssi-layer", "P3 Credential"), ("vc_", "P3 Credential"),
          ("mobi_vid_provider", "P3 Credential"), ("erc1056_provider", "P3 Credential"),
          ("infrastructure_layer", "P4 Trust / P1 Messaging"), ("sumo_identity_integration", "P1 Messaging"),
          ("freshness", "P4 Trust"), ("MOBI VID", "P2 Ledger"), ("credential validity", "P4 Trust / P1 Messaging"),
          ("DID check", "P4 Trust / P1 Messaging"), ("checker", "P5 Evidence"), ("chapter", "P5 Evidence"),
          ("statements", "P5 Evidence"), ("rows", "P5 Evidence"), ("benchmarks", "P5 Evidence"), ("run_stamp", "P5 Evidence"),
          ("check_", "P5 Evidence"), ("make_", "P5 Evidence"), ("docs/", "P5 Evidence"), ("test", "P5 Evidence"),
          ("sandbox", "P5 Evidence"), ("tools/", "P5 Evidence"), ("CI", "P5 Evidence"), ("harness", "P5 Evidence")]


def dashboard():
    spec = importlib.util.spec_from_file_location("dash", ROOT / "docs/figures/make_dashboard_data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def plane(where):
    for key, name in PLANES:
        if key in where:
            return name
    return "unclassified"


def parse_log():
    """Every 5-column defect row, with the section heading it sits under (the detection method)."""
    rows, section = [], ""
    for line in LOG.read_text().splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        m = re.match(r"^\| (D\d+b?) \| (.*)\|\s*$", line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(2).split(" | ")]
        if len(cells) < 4:
            continue
        if cells[0] == "same" and rows:
            cells[0] = rows[-1]["where"]
        rows.append({"id": m.group(1), "where": cells[0], "defect": cells[1], "sev_cell": cells[2],
                     "status_cell": cells[3], "section": section})
    return rows


def clip(text, n=230):
    text = text.replace("|", "\\|")
    return text if len(text) <= n else text[:n].rstrip() + " …"


def goals():
    out = []
    for line in (ROOT / "docs/THREAT_MODEL.md").read_text().splitlines():
        m = re.match(r"^\| (G\d) — ([^|]+) \| (.*) \| ([^|]+) \|\s*$", line)
        if m:
            out.append({"id": m.group(1), "goal": m.group(2).strip(), "text": m.group(3).strip(), "adv": m.group(4).strip()})
    if len(out) != 8:
        raise SystemExit(f"expected 8 goals in THREAT_MODEL.md, parsed {len(out)}")
    return out


def main():
    mod = dashboard()
    dash_rows = {d["id"]: d for d in mod.defects()["rows"]}
    rows = parse_log()
    if set(dash_rows) != {r["id"] for r in rows}:
        raise SystemExit("defect ids differ between this parser and the dashboard's")
    cruxes = yaml.safe_load((ROOT / "docs/thesis/cruxes.yaml").read_text())["cruxes"]
    bearing = {}
    for c in cruxes:
        for d in c.get("defects", []):
            bearing.setdefault(d, []).append(c["id"])
    snap = json.loads(SNAP.read_text())
    counts = {}
    for r in rows:
        d = dash_rows[r["id"]]
        k = f"{d['severity']}:{d['status']}"
        counts[k] = counts.get(k, 0) + 1
    if counts != snap["defects"]["counts"]:
        raise SystemExit(f"counts disagree with the snapshot: {counts} vs {snap['defects']['counts']}")

    s = ("# TDP-006 — Failure Mode, Effects and Criticality Worksheet\n\n"
         "**Author:** Nikhil Prakash (MASc, UBC ECE)\n"
         "**Generated** by `docs/tdp/make_fmeca.py` from `docs/DEFECT_LOG.md`, `docs/thesis/cruxes.yaml` and "
         "`docs/THREAT_MODEL.md`. Do not edit by hand. Checked in CI; the severity-by-status counts are cross-checked "
         "against `docs/figures/dashboard_snapshot.json`.\n"
         "**Format:** MIL-STD-1629A Task 101 worksheet columns, adapted to a software testbed: identification, item, "
         "function (plane), failure mode and cause, end effect (the thesis crux the defect bears on), detection method "
         "(the pass or review that found it), compensating provision (the fix or the recorded treatment), severity "
         "class. Format only. No failure rates or criticality numbers are computed: the testbed has no operating-hours "
         "data, and inventing a rate would violate guide rule 1.1.1.\n\n"
         "## 1. Severity translation (declared once)\n\n"
         "| Log letter | Log meaning | Worksheet class |\n|---|---|---|\n")
    for k, v in CLASS.items():
        s += f"| {k} | {'affects a thesis claim or a security property' if k == 'H' else 'wrong behaviour, bounded impact' if k == 'M' else 'cosmetic or advisory'} | {v} |\n"
    s += ("\nClass I (catastrophic) is not used: no failure of this testbed endangers life or equipment. The letter is "
          "the log's; the class is a translation of it, not a new rating.\n\n")
    s += "## 2. Totals\n\n| Severity | fixed | partly fixed | open | total |\n|---|---|---|---|---|\n"
    for sev in ("H", "M", "L"):
        f, p, o = (counts.get(f"{sev}:fixed", 0), counts.get(f"{sev}:partly fixed", 0), counts.get(f"{sev}:open", 0))
        s += f"| {sev} | {f} | {p} | {o} | {f + p + o} |\n"
    s += f"| all | {sum(v for k, v in counts.items() if k.endswith(':fixed'))} | {sum(v for k, v in counts.items() if k.endswith(':partly fixed'))} | {sum(v for k, v in counts.items() if k.endswith(':open'))} | {len(rows)} |\n\n"
    s += "## 3. Worksheet\n\n"
    s += ("| ID | Item (where) | Plane | Failure mode and cause | End effect (crux) | Detection method | Compensating provision | Sev | Class | Status |\n"
          "|---|---|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        d = dash_rows[r["id"]]
        s += (f"| {r['id']} | {clip(r['where'], 90)} | {plane(r['where'])} | {clip(r['defect'])} | "
              f"{', '.join(bearing.get(r['id'], [])) or '—'} | {clip(r['section'], 70)} | {clip(r['status_cell'], 200)} | "
              f"{d['severity']} | {CLASS[d['severity']].split(' (')[0]} | {d['status']} |\n")
    s += "\n## 4. Security goals and the adversary each counters (from the threat model)\n\n"
    s += "| Goal | Statement | Countered adversary |\n|---|---|---|\n"
    for g in goals():
        s += f"| {g['id']} {g['goal']} | {clip(g['text'], 260)} | {g['adv']} |\n"
    s += ("\n## 5. Reading rule\n\n"
          "A row with severity H and status other than fixed blocks every chapter claim on its path "
          "(`docs/DEFECT_LOG.md` section D). A row with status fixed names its commit in the compensating-provision "
          "column; the regression test that holds it is in the layer that owns the path (guide rule 1.2.5).\n")
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text() != s:
            print("stale: TDP-006; run make_fmeca.py")
            sys.exit(1)
        print(f"TDP-006 up to date ({len(rows)} defects)")
        return
    OUT.write_text(s)
    print("wrote", OUT.relative_to(ROOT), len(rows), "defects")


if __name__ == "__main__":
    main()
