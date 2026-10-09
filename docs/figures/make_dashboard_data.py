#!/usr/bin/env python3
"""Build the results-dashboard snapshot and the crux register from committed files only.

Plan 2026-10-09 P1.1 and P4.1. Every value in the snapshot carries `source` (path, and key
where it helps); nothing is typed by hand. Run from the repository root:

    python3 docs/figures/make_dashboard_data.py           # writes the two outputs
    python3 docs/figures/make_dashboard_data.py --check   # exit 1 if either output is stale

Outputs:
    docs/figures/dashboard_snapshot.json
    docs/thesis/CRUX_REGISTER.md        (generated from docs/thesis/cruxes.yaml + the register)
"""
import glob
import json
import pathlib
import re
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_SNAPSHOT = ROOT / "docs/figures/dashboard_snapshot.json"
OUT_CRUX = ROOT / "docs/thesis/CRUX_REGISTER.md"


def rel(p):
    return str(pathlib.Path(p).resolve().relative_to(ROOT))


def load(p):
    with open(ROOT / p) as f:
        return json.load(f)


def src(path, key=None):
    return {"path": path, **({"key": key} if key else {})}


# ---------------------------------------------------------------- register
def parse_register():
    text = (ROOT / "docs/MEASUREMENT_CONDITIONS.md").read_text()
    rows = {}
    for line in text.splitlines():
        m = re.match(r"^\| (\d+) \| (.*)\|\s*$", line)
        if not m:
            continue
        n = int(m.group(1))
        cells = [c.strip() for c in m.group(2).split(" | ")]
        claim = re.sub(r"\*\*", "", cells[0])
        status_text = " ".join(cells[4:]) if len(cells) > 4 else ""
        st = re.search(r"\*\*([VESUB])(?=\*\*|,|\s)", status_text)
        status = st.group(1) if st else "?"
        rows[n] = {"row": n, "status": status, "claim": claim[:220] + ("…" if len(claim) > 220 else ""),
                   "tag": cells[2] if len(cells) > 2 else ""}
    return rows


# ---------------------------------------------------------------- results
def gas():
    p = "4_comparison-framework/results/gas_benchmark.json"
    d = load(p)
    stats = load("4_comparison-framework/results/gas_benchmark_stats.json")
    ops = ["deployRegistry", "createIdentity", "updateAttribute", "updateAttributeVia4337",
           "addDelegateOrClaim", "revoke", "transferOwnership"]
    table = {}
    for std, v in d.items():
        if std == "metadata":
            continue
        table[std] = {op: (v[op]["gasUsed"] if isinstance(v.get(op), dict) and v[op].get("gasUsed") is not None else None)
                      for op in ops}
    creates = {k: t["createIdentity"] for k, t in table.items() if t["createIdentity"]}
    lo, hi = min(creates, key=creates.get), max(creates, key=creates.get)
    return {
        "source": src(p), "measured": d["metadata"].get("date"), "condition": "M1",
        "operations": ops, "table": table,
        "create_min": {"standard": lo, "gas": creates[lo]},
        "create_max": {"standard": hi, "gas": creates[hi]},
        "create_spread": round(creates[hi] / creates[lo], 2),
        "determinism": {"n_runs": stats["n_runs"], "all_deterministic": stats["all_deterministic"],
                        "source": src("4_comparison-framework/results/gas_benchmark_stats.json")},
        "moved_by_fixes": [rel(x) for x in sorted(glob.glob(str(ROOT / "4_comparison-framework/results/gas_moved_by_*.json")))],
        "register": [25],
    }


def lifetime():
    p = "4_comparison-framework/results/scaling_lifetime.json"
    d = load(p)
    rank = []
    for e in d["ranking"]:
        b = d["standards"][e["name"]]["sensitivityBand"]
        rank.append({"standard": e["name"], "total": e["total"], "low": b["low"], "high": b["high"]})
    return {"source": src(p), "ranking": rank, "register": [26], "note": "model over an assumed 15-year profile"}


def sweep():
    p = "4_comparison-framework/results/mobi_vid_backends.json"
    d = load(p)["backends"]
    out = {}
    for b, v in d.items():
        out[b] = {op: {"gas": v[op]["gasUsed"], "native": bool(v[op].get("nativeSupport", True))}
                  for op in ("birthAttestation", "lifecycleEvent", "thirdPartyAttestation")}
        out[b]["fidelity"] = f'{v["fidelity"]["score"]}/{v["fidelity"]["outOf"]}'
    return {"source": src(p), "backends": out, "register": [25]}


def security():
    p = "4_comparison-framework/security-analysis/results/attack_results.json"
    d = load(p)
    per = {}
    total = {}
    for std, cells in d.items():
        if std == "metadata" or not isinstance(cells, dict):
            continue
        c = {}
        for v in cells.values():
            if isinstance(v, dict) and "outcome" in v:
                c[v["outcome"]] = c.get(v["outcome"], 0) + 1
                total[v["outcome"]] = total.get(v["outcome"], 0) + 1
        per[std] = c
    return {"source": src(p), "per_standard": per, "total": total, "register": [28],
            "harness": "strict: DEFENDED only when the revert matches the documented expected reason"}


def compliance():
    p = "4_comparison-framework/results/w3c_compliance.json"
    s = load(p)["summary"]
    return {"source": src(p, "summary"), "score": round(s["score"], 1), "executed": s["executed_checks"],
            "pass": s["pass"], "partial": s["partial"], "fail": s["fail"], "register": [4]}


def conformance():
    base = "docs/conformance/reports/merged-2026-10-06"
    out = {}
    for run in ("default", "registry-did"):
        files = sorted(glob.glob(str(ROOT / base / run / "jest-cvin" / "*.json")))
        passed = total = 0
        suites = {}
        for f in files:
            j = json.load(open(f))
            name = pathlib.Path(f).stem.replace("cvin-cli-", "")
            suites[name] = f'{j["numPassedTests"]}/{j["numTotalTests"]}'
            passed += j["numPassedTests"]
            total += j["numTotalTests"]
        out[run] = {"passed": passed, "total": total, "suites": suites, "source": src(f"{base}/{run}/jest-cvin/")}
    return {"runs": out, "register": [24]}


def v2v():
    p = "cv2x-testbed/sumo/results/v2v_latency_stats.json"
    d = load(p)
    pops = {}
    for pop in ("ssi", "pki"):
        pops[pop] = {m: {"median": d["per_population"][pop][m]["median"], "ci95": d["per_population"][pop][m]["ci95"]}
                     for m in ("sign", "cold", "warm")}
    return {"source": src(p), "n_runs": d["n_runs"], "vehicles": d["vehicles_per_run"], "per_population": pops,
            "totals": d["totals"], "condition": "M0, simulated mobility, real cryptography", "register": [27]}


def freshness():
    out = {}
    for name, p, reg in (("full", "cv2x-testbed/results/freshness_k.json", 32),
                         ("probe", "cv2x-testbed/results/freshness_k_probe.json", 37)):
        d = load(p)
        out[name] = {"source": src(p), "register": reg,
                     "by_k": [{"k": r["k"], "median_ms": round(r["median_ms"], 3), "p95_ms": round(r["p95_ms"], 3)} for r in d["latency"]],
                     "t_local_ms": round(d["derived"]["t_local_ms"], 3), "t_chain_ms": round(d["derived"]["t_chain_ms"], 3),
                     "host": d["environment"].get("cpu_model")}
    return out


def parity():
    p = "cv2x-testbed/results/lifecycle_parity.json"
    d = load(p)
    return {"source": src(p, "verdicts"), "register": [33],
            "verdicts": [{"operation": v["operation"], "claim": v["claim"], "verdict": v["verdict"],
                          "ratio_median": round(v["ratio_median"], 3)} for v in d["verdicts"]]}


def pseudonyms():
    p = "4_comparison-framework/results/pseudonym_pool.json"
    v = load(p)["verdicts"]
    return {"source": src(p, "verdicts"), "register": [38],
            "gas_verdict": v["gas"]["verdict"], "epoch_gas": v["gas"]["measured_epoch_gas"],
            "prereg_gas": v["gas"]["prereg_value"], "linkability_verdict": v["linkability"]["verdict"]}


def harness():
    p = "1_blockchain-identity/results/metrics/latest/analysis.json"
    d = load(p)
    meta = load("1_blockchain-identity/results/metrics/latest/meta.json")
    return {"source": src(p), "runId": d["runId"], "dirty": meta.get("dirty"),
            "criteria": [c["label"] for c in d["criteria"]], "frontier": d["frontier"],
            "dominated_by_all": d["dominatedBy"]["all"], "register": [34, 35, 36]}


def infrastructure():
    """Infrastructure messaging I1-I5 (docs/design/INFRASTRUCTURE_PREREG.md); absent until run."""
    base = "cv2x-testbed/sumo/results/"
    out = {}
    if (ROOT / base / "infrastructure_stats.json").exists():
        d = load(base + "infrastructure_stats.json")
        out["I1"] = {"verdict": d["I1"]["verdict"], "ratio_median": d["I1"]["ratio"]["median"], "ratio_ci95": d["I1"]["ratio"]["ci95"],
                     "spat_warm_ms": d["I1"]["spat_warm_ms"]["median"], "bsm_warm_ms": d["I1"]["bsm_ssi_warm_ms"]["median"],
                     "spat_cold_ms": d["I1"]["spat_cold_ms"]["median"], "runs": d["config"]["runs"]}
        out["I2"] = {"verdict": d["I2"]["verdict"], "attacks": len(d["I2"]["attacks"]), "runs_all_rejected": d["I2"]["runs_all_rejected"],
                     "runs": d["I2"]["runs"]}
        out["I5"] = {"controller_to_vehicle_ms": d["I5"]["controller_to_vehicle_ms"]["median"],
                     "tmc_to_controller_ms": d["I5"]["tmc_to_controller_ms"]["median"]}
        out["source_stats"] = src(base + "infrastructure_stats.json")
    if (ROOT / base / "infrastructure_revocation.json").exists():
        d = load(base + "infrastructure_revocation.json")
        out["I3"] = {"verdict": d["I3"]["verdict"], "per_k": {k: {"max": v["max_accepted_after_revocation"], "bound": v["bound_k_minus_1"],
                     "verdict": v["verdict"]} for k, v in d["I3"]["per_k"].items()}}
        out["source_revocation"] = src(base + "infrastructure_revocation.json")
    if (ROOT / "4_comparison-framework/results/infrastructure_gas.json").exists():
        d = load("4_comparison-framework/results/infrastructure_gas.json")
        out["I4"] = {k: v["gasUsed"] for k, v in d["operations"].items()}
        out["source_gas"] = src("4_comparison-framework/results/infrastructure_gas.json")
    out["register"] = [44, 45, 46, 47, 48]
    return out


def tests():
    p = "sandbox/grand/report/GRAND_REPORT.md"
    text = (ROOT / p).read_text()
    m = re.search(r"Generated (\S+) at commit `(\w+)`", text)
    stages = {}
    for line in text.splitlines():
        r = re.match(r"^\| (smoke|L1|L1\+L2|L3\+L4|demos) \| (\S) \| (.*?) \|", line)
        if r:
            stages[r.group(1)] = {"ok": r.group(2) == "✓", "result": r.group(3)}
    return {"source": src(p), "generated": m.group(1) if m else None, "commit": m.group(2) if m else None, "stages": stages}


def demos():
    p = "sandbox/grand/report/demos.json"
    d = load(p)["options"]
    out = {}
    for opt, fams in d.items():
        out[opt] = {"demos": len(fams), "ok": sum(1 for f in fams if f["ok"]), "steps": sum(f["steps"] for f in fams),
                    "flagged": sum(f["flagged"] for f in fams)}
    return {"source": src(p), "per_option": out}


def defects():
    p = "docs/DEFECT_LOG.md"
    text = (ROOT / p).read_text()
    rows = []
    for line in text.splitlines():
        m = re.match(r"^\| (D\d+b?) \| (.*)\|\s*$", line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(2).split(" | ")]
        if len(cells) < 4:
            continue
        sev_cell, status_cell = (cells[2], cells[3]) if len(cells) >= 4 else ("", "")
        sev = "H" if "**H**" in sev_cell or sev_cell.startswith("H") else ("M" if sev_cell.startswith("M") else ("L" if sev_cell.startswith("L") else sev_cell[:12]))
        low = status_cell.lower()
        if low.startswith("fixed") or low.startswith("**fixed") or "**fixed" in low[:40]:
            st = "fixed"
        elif "partly" in low[:60] or "second half fixed" in low[:60] or "first three fixed" in low[:60] or "d25a/d25b fixed" in low[:60]:
            st = "partly fixed"
        elif "manifest reason corrected" in low[:60]:
            st = "open"
        else:
            st = "open"
        rows.append({"id": m.group(1), "severity": sev, "status": st})
    counts = {}
    for r in rows:
        k = f'{r["severity"]}:{r["status"]}'
        counts[k] = counts.get(k, 0) + 1
    return {"source": src(p), "rows": rows, "counts": counts}


# ---------------------------------------------------------------- cruxes
def cruxes(register):
    d = yaml.safe_load((ROOT / "docs/thesis/cruxes.yaml").read_text())["cruxes"]
    out = []
    for c in d:
        ev = [{"row": n, "status": register.get(n, {}).get("status", "missing"),
               "claim": register.get(n, {}).get("claim", "(row not in register)")} for n in c.get("evidence_rows", [])]
        if not ev:
            state = "gap"
        elif all(e["status"] == "V" for e in ev) and not c.get("gaps"):
            state = "evidenced"
        else:
            state = "partial"
        out.append({**{k: c[k] for k in ("id", "title", "question", "claim", "hypotheses", "thrusts", "defects", "artefacts", "gaps", "examiner")},
                    "evidence": ev, "state": state})
    return out


def head():
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "log", "-1", "--format=%h"], text=True).strip()
    except Exception:
        return None


def build():
    register = parse_register()
    status_counts = {}
    for r in register.values():
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1
    snap = {
        "about": "Results dashboard snapshot. Generated by docs/figures/make_dashboard_data.py from committed files only; every block names its source and register rows.",
        "register": {"source": src("docs/MEASUREMENT_CONDITIONS.md"), "rows": len(register), "by_status": status_counts},
        "hypotheses": {
            "H1": "minimal-state identity standards are cheaper to create than heavyweight account standards",
            "H2": "a blockchain identity layer can reach ≥90 % W3C compliance",
            "H3": "off-chain credential verification fits the V2V latency budget",
            "H4": "MOBI VID is realisable across blockchain backends",
            "H5": "the hybrid sits on the cost/capability frontier",
            "source": src("README.md", "Hypotheses"),
        },
        "gas": gas(), "lifetime": lifetime(), "mobi_sweep": sweep(), "security": security(),
        "compliance": compliance(), "conformance": conformance(), "v2v": v2v(), "freshness": freshness(),
        "lifecycle_parity": parity(), "pseudonyms": pseudonyms(), "harness": harness(),
        "infrastructure": infrastructure(),
        "tests": tests(), "demos": demos(), "defects": defects(),
        "cruxes": cruxes(register),
        "register_rows": {str(k): v for k, v in sorted(register.items())},
    }
    return snap


def crux_markdown(snap):
    lines = ["# Crux Register", "",
             "**Generated** by `docs/figures/make_dashboard_data.py` from `docs/thesis/cruxes.yaml` and the claim register "
             "(`docs/MEASUREMENT_CONDITIONS.md`). Do not edit by hand; edit the YAML and regenerate.", "",
             "A crux is a question the thesis must answer for an examiner. State: **evidenced** = every evidence row is status V "
             "and no gap is open; **partial** = some evidence, or an open gap; **gap** = no evidence row.", "",
             "| Crux | State | Hypotheses | Evidence rows (status) | Open gaps |", "|---|---|---|---|---|"]
    for c in snap["cruxes"]:
        ev = ", ".join(f'#{e["row"]} ({e["status"]})' for e in c["evidence"]) or "none"
        lines.append(f'| {c["id"]} {c["title"]} | **{c["state"]}** | {", ".join(c["hypotheses"]) or "—"} | {ev} | {len(c["gaps"])} |')
    for c in snap["cruxes"]:
        lines += ["", f'## {c["id"]} — {c["title"]}', "", f'**Question.** {c["question"]}', "", f'**Claim.** {c["claim"]}', "",
                  f'**Thrusts:** {", ".join(str(t) for t in c["thrusts"])} · **Hypotheses:** {", ".join(c["hypotheses"]) or "none yet"} · '
                  f'**Defects bearing on it:** {", ".join(c["defects"]) or "none"}', ""]
        if c["evidence"]:
            lines += ["| Row | Status | Claim (from the register) |", "|---|---|---|"]
            lines += [f'| #{e["row"]} | {e["status"]} | {e["claim"].replace("|", "/")} |' for e in c["evidence"]]
        else:
            lines.append("_No evidence row exists._")
        lines += ["", "**Open gaps:**"] + [f"- {g}" for g in c["gaps"]] if c["gaps"] else ["", "**Open gaps:** none."]
        lines += ["", f'**The examiner will ask:** {c["examiner"]}', "", f'**Artefacts:** ' + ", ".join(f"`{a}`" for a in c["artefacts"])]
    return "\n".join(lines) + "\n"


def main():
    snap = build()
    js = json.dumps(snap, indent=2, ensure_ascii=False) + "\n"
    md = crux_markdown(snap)
    if "--check" in sys.argv:
        stale = []
        if not OUT_SNAPSHOT.exists() or OUT_SNAPSHOT.read_text() != js:
            stale.append(rel(OUT_SNAPSHOT))
        if not OUT_CRUX.exists() or OUT_CRUX.read_text() != md:
            stale.append(rel(OUT_CRUX))
        if stale:
            print("STALE (regenerate with docs/figures/make_dashboard_data.py): " + ", ".join(stale))
            sys.exit(1)
        print("dashboard snapshot and crux register are current")
        return
    OUT_SNAPSHOT.write_text(js)
    OUT_CRUX.write_text(md)
    print(f"wrote {rel(OUT_SNAPSHOT)} and {rel(OUT_CRUX)}")


if __name__ == "__main__":
    main()
