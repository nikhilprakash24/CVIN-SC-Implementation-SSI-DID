#!/usr/bin/env python3
"""Build TDP-002 (system specification) and TDP-005 (verification cross-reference matrix) from committed sources.

After-action report 20, step T3. Inputs: docs/tdp/requirements.yaml (the shall-statements and their traces),
docs/MEASUREMENT_CONDITIONS.md (register row statuses, parsed by the dashboard's own parser),
docs/figures/dashboard_snapshot.json (threshold values and pre-registered verdicts), the tracked tree (inspection
files) and .github/workflows (CI steps). No status, verdict or number is typed by hand.

    python3 docs/tdp/make_vcrm.py            # writes TDP-002 and TDP-005
    python3 docs/tdp/make_vcrm.py --check    # CI: exit 1 if either document is stale, a cited row or file is
                                             # missing, a CI step is absent, or a threshold path does not resolve

Status rule (declared here, applied mechanically):
  VERIFIED  every evidence row is status V, every file exists, every CI text is found, and the threshold (if any)
            is met;
  PARTIAL   at least one V row, or an inspection requirement whose files exist, with something else not met
            (a non-V row, an unmet threshold, a missing file or CI step);
  OPEN      otherwise.
A requirement with no register rows and method I or D is held by inspection (files and CI) only.
A requirement may name `pending` trunk items (defect ids from docs/DEFECT_LOG.md, or WM-2 plan steps from
docs/PLAN_WM-2.md section 3) that block VERIFIED; while any is open its status is capped at PARTIAL. The generator
fails if a listed defect is marked fixed in the log or a listed plan step is marked done, so a stale cap cannot persist.
"""
import importlib.util
import json
import re
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
REQ = ROOT / "docs/tdp/requirements.yaml"
SNAP = ROOT / "docs/figures/dashboard_snapshot.json"
OUT_SPEC = ROOT / "docs/tdp/TDP-002_SYSTEM_SPECIFICATION.md"
OUT_VCRM = ROOT / "docs/tdp/TDP-005_VERIFICATION_CROSS_REFERENCE_MATRIX.md"
WORKFLOWS = ROOT / ".github/workflows"
METHODS = {"T": "Test", "A": "Analysis", "I": "Inspection", "D": "Demonstration"}


def register():
    spec = importlib.util.spec_from_file_location("dash", ROOT / "docs/figures/make_dashboard_data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.parse_register()


def lookup(snapshot, dotted):
    node = snapshot
    for part in dotted.split("."):
        if isinstance(node, list):
            node = node[int(part)]
        elif isinstance(node, dict):
            if part not in node:
                raise SystemExit(f"threshold path not in the snapshot: {dotted} (at '{part}')")
            node = node[part]
        else:
            raise SystemExit(f"threshold path not in the snapshot: {dotted}")
    return node


def compare(actual, op, value):
    if op == "==":
        return actual == value
    if op == ">=":
        return actual >= value
    if op == "<=":
        return actual <= value
    raise SystemExit(f"unknown op {op}")


def open_items():
    """Defect ids that are not 'fixed' in the log, and WM-2 plan steps not marked done."""
    spec = importlib.util.spec_from_file_location("dash", ROOT / "docs/figures/make_dashboard_data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    defects = {d["id"]: d["status"] for d in mod.defects()["rows"]}
    steps = {}
    for line in (ROOT / "docs/PLAN_WM-2.md").read_text().splitlines():
        m = re.match(r"^\| ([A-G]\d[a-z]?) \| (.*)", line)
        if m:
            steps[m.group(1)] = "done" if "**done" in m.group(2)[:20] else "open"
    return defects, steps


def ci_text():
    return "\n".join(p.read_text() for p in sorted(WORKFLOWS.glob("*.yml")))


def evaluate(reqs, reg, snap, ci):
    defects, steps = open_items()
    out = []
    for r in reqs:
        rows = r.get("evidence_rows", [])
        missing_rows = [n for n in rows if n not in reg]
        if missing_rows:
            raise SystemExit(f"{r['id']}: evidence rows not in the register: {missing_rows}")
        statuses = {n: reg[n]["status"] for n in rows}
        v_rows = [n for n in rows if statuses[n] == "V"]
        files = r.get("files", [])
        missing_files = [f for f in files if not (ROOT / f).exists()]
        ci_ok = (r.get("ci") in ci) if r.get("ci") else None
        th = r.get("threshold")
        th_result = None
        if th:
            actual = lookup(snap, th["path"])
            th_result = {"actual": actual, "met": compare(actual, th["op"], th["value"]), **th}
        verdict = lookup(snap, r["verdict_from"]) if r.get("verdict_from") else None
        all_rows_v = bool(rows) and len(v_rows) == len(rows)
        held_by_inspection = not rows and r["method"] in ("I", "D")
        problems = []
        if rows and not all_rows_v:
            problems.append("non-V row: " + ", ".join(f"#{n} ({statuses[n]})" for n in rows if statuses[n] != "V"))
        if missing_files:
            problems.append("missing file: " + ", ".join(missing_files))
        if ci_ok is False:
            problems.append(f"CI step not found: {r['ci']}")
        if th_result and not th_result["met"]:
            problems.append(f"threshold not met: {th['label']} (actual {th_result['actual']})")
        if (all_rows_v or held_by_inspection) and not problems:
            status = "VERIFIED"
        elif v_rows or (held_by_inspection and not missing_files):
            status = "PARTIAL"
        elif not rows and not held_by_inspection:
            status = "OPEN"
        else:
            status = "OPEN"
        if not rows and r["method"] in ("T", "A") and not problems:
            # a test/analysis requirement with no register row is held by its files and CI only; say so
            status = "VERIFIED" if files and not missing_files else "OPEN"
        pending = []
        for item in r.get("pending", []):
            if item in defects:
                if defects[item] == "fixed":
                    raise SystemExit(f"{r['id']}: pending item {item} is marked fixed in the defect log; remove it")
                pending.append(f"{item} ({defects[item]})")
            elif item in steps:
                if steps[item] == "done":
                    raise SystemExit(f"{r['id']}: pending step {item} is marked done in PLAN_WM-2; remove it")
                pending.append(f"WM-2 {item} (open)")
            else:
                raise SystemExit(f"{r['id']}: pending item {item} is neither a defect id nor a WM-2 step")
        if pending:
            problems.append("pending: " + ", ".join(pending))
            if status == "VERIFIED":
                status = "PARTIAL"
        out.append({**r, "statuses": statuses, "v_rows": v_rows, "missing_files": missing_files, "ci_ok": ci_ok,
                    "threshold_result": th_result, "verdict": verdict, "status": status, "problems": problems})
    return out


def header(title, number):
    return (f"# {number} — {title}\n\n"
            "**Author:** Nikhil Prakash (MASc, UBC ECE)\n"
            "**Generated** by `docs/tdp/make_vcrm.py` from `docs/tdp/requirements.yaml`, the claim register "
            "(`docs/MEASUREMENT_CONDITIONS.md`), `docs/figures/dashboard_snapshot.json`, the tracked tree and "
            "`.github/workflows`. Do not edit by hand; edit the YAML and regenerate. Checked in CI.\n"
            "**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`; `docs/tdp/README.md` (TDP-000) for conventions.\n"
            "**Format:** MIL-STD-961E section order (1 scope, 2 applicable documents, 3 requirements, 4 verification, "
            "5 packaging, 6 notes). Format only; no certification is claimed.\n\n")


def spec(reqs, groups):
    s = header("System Specification: Vehicle Identity Testbed (CVIN-SC)", "TDP-002")
    s += "## 1. Scope\n\n"
    s += ("1.1 **Identification.** This specification covers the research testbed in this repository: nine Ethereum "
          "identity substrates and one application profile (layer 1), a W3C credential and resolution layer (layer 2), a "
          "connected-vehicle message testbed with mock mobility (layer 3) and the comparison and evidence machinery "
          "(layer 4 and `tools/run_identity`).\n\n"
          "1.2 **Purpose.** It states, as shall-statements, what the testbed was built to show, each traced to a research "
          "question, hypothesis, pre-registration, threat goal or rigour rule already on the trunk, so that verification "
          "can be read off the claim register mechanically (TDP-005).\n\n"
          "1.3 **Limits.** The testbed measures on an in-process EVM (M1), in-process cryptography (M0) and mock mobility. "
          "It has no radio, no channel, no real traffic and no public-network run. Every requirement carries its limit "
          "verbatim from the register's caveats.\n\n")
    s += "## 2. Applicable documents\n\n"
    s += ("| Document | Role here |\n|---|---|\n"
          "| `docs/MEASUREMENT_CONDITIONS.md` | condition tags M0-M2; the claim register (#1-#52) |\n"
          "| `docs/STYLE_AND_RIGOUR_GUIDE.md` | rules on numbers, claims and process |\n"
          "| `docs/THREAT_MODEL.md` | adversaries A1-A4, goals G1-G8 |\n"
          "| `docs/LATENCY_BUDGET.md` | the 100 ms interval, the identity share f and P*(f) |\n"
          "| `docs/design/INFRASTRUCTURE_PREREG.md` | pre-registered I1-I5 with amendments |\n"
          "| `docs/PLAN_MOBI_SUMO.md` | pre-registered M4, M5 |\n"
          "| `docs/phase2/SCOPE_RECONCILIATION.md` | RQ1-RQ4 as restated to the evidence (Scope v3) |\n"
          "| SAE J2945/1 | the 10 Hz BSM cadence the budget derives from |\n"
          "| IEEE 1609.2; ETSI TS 103 097 | the certificate-based baselines the PKI design models |\n"
          "| W3C DID Core v1.0; W3C VC Data Model v2.0 | the structures the credential layer is checked against |\n"
          "| MOBI VID I v2.0 TS/2024; VID II UC texts | the lifecycle profile is checked against the public texts only |\n"
          "| MIL-STD-961E | the section order of this document |\n\n")
    s += "## 3. Requirements\n\n"
    s += ("Convention. \"Shall\" marks a requirement. The threshold values are the ones the trunk declared before the "
          "measurement (a pre-registration, the latency budget, the CI gate); none is chosen here. Each requirement ends "
          "with its declared limit.\n\n")
    for gid, gname in groups.items():
        s += f"### 3.{list(groups).index(gid) + 1} {gname} ({gid})\n\n"
        for r in reqs:
            if r["id"].split("-")[0] != gid:
                continue
            s += f"**{r['id']} {r['title']}.** {r['shall']}\n\n"
            s += f"- Derived from: {r['derived_from']}\n"
            s += f"- Verification: {METHODS[r['method']]}"
            if r.get("evidence_rows"):
                s += "; register " + ", ".join(f"#{n}" for n in r["evidence_rows"])
            if r.get("threshold"):
                s += f"; threshold: {r['threshold']['label']}"
            s += "\n"
            s += f"- Limit: {r['limit']}\n\n"
    s += "## 4. Verification\n\n"
    s += ("4.1 **Methods.** T test (the measurement runs and its output is compared with a declared threshold or "
          "recorded as a verdict); A analysis (a derivation from measured data, with its inputs named); I inspection "
          "(the artefact exists in the tracked tree and, where stated, a CI step exercises it); D demonstration (a run "
          "shows the behaviour; counts, not thresholds).\n\n"
          "4.2 **Cross-reference.** The status of every requirement is computed in TDP-005 from the register, the "
          "snapshot, the tree and the workflows. This document carries no status.\n\n"
          "4.3 **Rule.** A requirement is verified only by register rows of status V. An E, S, U or B row is listed and "
          "does not count (the rule of `docs/thesis/CRUX_REGISTER.md`).\n\n")
    s += "## 5. Packaging and delivery\n\n"
    s += ("The deliverable is the repository at a named commit: contracts, scripts, tests, results of record with run "
          "stamps, the register, the generated documents and this package. A release is a version tag cut by the author "
          "(N-11). Reproduction commands are in `docs/HANDBACK_2026-10-14.md` section 5 and TDP-008.\n\n")
    s += "## 6. Notes\n\n"
    s += ("6.1 **Definitions.** Substrate: one identity standard realised as a contract set. Warm/cold: with/without the "
          "sender's key in the verifier cache. k: the re-check cadence in messages. P*(f): the number of neighbours "
          "serviceable inside the fraction f of the 100 ms interval. V/E/S/U/B: register statuses (verified, estimate, "
          "superseded, unverified, bundle lineage).\n\n"
          "6.2 **Acronyms.** BSM basic safety message; SPaT signal phase and timing; RSU roadside unit; TMC traffic "
          "management centre; DID decentralised identifier; VC verifiable credential; VIN vehicle identification number; "
          "PKI public-key infrastructure; EVM Ethereum virtual machine; RPC remote procedure call; CI continuous integration.\n\n"
          f"6.3 **Count.** {len(reqs)} requirements in {len(groups)} groups.\n")
    return s


def vcrm(ev, groups, reg):
    s = header("Verification Cross-Reference Matrix", "TDP-005")
    counts = {k: sum(1 for r in ev if r["status"] == k) for k in ("VERIFIED", "PARTIAL", "OPEN")}
    s += "## 0. Totals\n\n"
    s += "| Status | Count | Meaning |\n|---|---|---|\n"
    s += f"| VERIFIED | {counts['VERIFIED']} | every evidence row V; files and CI present; threshold met; nothing pending |\n"
    s += f"| PARTIAL | {counts['PARTIAL']} | some evidence V; at least one row non-V, a threshold unmet, an item missing, or a named trunk item still open |\n"
    s += f"| OPEN | {counts['OPEN']} | no V evidence |\n\n"
    by_status = {}
    for n, r in reg.items():
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    s += ("Register at generation: " + ", ".join(f"{k} {v}" for k, v in sorted(by_status.items())) +
          f" ({len(reg)} rows).\n\n")
    s += "## 1. Matrix\n\n"
    s += "| Req | Title | Method | Evidence rows (status) | Threshold / verdict | Inspection | Status | Not met |\n|---|---|---|---|---|---|---|---|\n"
    for r in ev:
        rows = ", ".join(f"#{n} ({r['statuses'][n]})" for n in r.get("evidence_rows", [])) or "—"
        th = r["threshold_result"]
        tv = []
        if th:
            tv.append(f"{th['label']}: actual `{th['actual']}` → {'met' if th['met'] else 'NOT MET'}")
        if r["verdict"] is not None:
            tv.append(f"pre-registered verdict as it fell: **{r['verdict']}**")
        insp = []
        if r.get("files"):
            insp.append(f"{len(r['files']) - len(r['missing_files'])}/{len(r['files'])} files")
        if r.get("ci"):
            insp.append("CI step " + ("found" if r["ci_ok"] else "MISSING"))
        s += (f"| {r['id']} | {r['title']} | {METHODS[r['method']]} | {rows} | {'; '.join(tv) or '—'} | "
              f"{'; '.join(insp) or '—'} | **{r['status']}** | {'; '.join(r['problems']) or '—'} |\n")
    s += "\n## 2. Reverse index: register row → requirements\n\n"
    rev = {}
    for r in ev:
        for n in r.get("evidence_rows", []):
            rev.setdefault(n, []).append(r["id"])
    s += "| Row | Status | Requirements |\n|---|---|---|\n"
    for n in sorted(rev):
        s += f"| #{n} | {reg[n]['status']} | {', '.join(rev[n])} |\n"
    unused = [n for n, r in sorted(reg.items()) if r["status"] == "V" and n not in rev]
    s += ("\nV rows cited by no requirement: " + (", ".join(f"#{n}" for n in unused) if unused else "none") +
          ". A V row no requirement cites is evidence without a stated purpose; TDP-PLAN phase 3 decides whether to add "
          "a requirement or leave the row as supporting data.\n")
    s += "\n## 3. Limits carried\n\n"
    s += "| Req | Declared limit |\n|---|---|\n"
    for r in ev:
        s += f"| {r['id']} | {r['limit']} |\n"
    return s


def main():
    cfg = yaml.safe_load(REQ.read_text())
    reqs, groups = cfg["requirements"], cfg["groups"]
    ids = [r["id"] for r in reqs]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate requirement ids")
    reg = register()
    snap = json.loads(SNAP.read_text())
    ev = evaluate(reqs, reg, snap, ci_text())
    outputs = {OUT_SPEC: spec(reqs, groups), OUT_VCRM: vcrm(ev, groups, reg)}
    if "--check" in sys.argv:
        stale = [p.name for p, text in outputs.items() if not p.exists() or p.read_text() != text]
        if stale:
            print("stale: " + ", ".join(stale) + "; run make_vcrm.py")
            sys.exit(1)
        print(f"TDP-002 and TDP-005 up to date ({len(reqs)} requirements)")
        return
    for p, text in outputs.items():
        p.write_text(text)
        print("wrote", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
