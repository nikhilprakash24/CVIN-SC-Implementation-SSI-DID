#!/usr/bin/env python3
"""The grand sandbox runner (plan S8).

Subcommands:
  matrix   render the union table from the manifests -> report/asymmetry.md
  check    fail if any option x family has no stance
  smoke    run the S2 acceptance runner over every adapter
  l1       run the uniform L1 suite (writes report/L1-asymmetry.{json,md})
  l2       run the whole Hardhat tree (L1 + L2 per-option + security)
  py       run the Python layers (L3 + L4 + SSI-layer suites)
  demos    run every option's demos, collect the JSON steps -> report/demos.{json,md}
  all      everything above, then assemble report/GRAND_REPORT.md
Everything references the canonical code; nothing is copied."""
import pathlib, sys, yaml, subprocess, json, time, re
HH = None
ROOT = pathlib.Path(__file__).resolve().parents[2]
SYM = {"measured-in-comparison": "M", "implemented": "I", "not-applicable": "—"}

def load():
    g = yaml.safe_load((ROOT / "sandbox/grand/manifest.yaml").read_text())
    opts = {p.parent.name: yaml.safe_load(p.read_text()) for p in sorted((ROOT / "sandbox/options").glob("*/manifest.yaml"))}
    return g, opts

def matrix(write=True):
    g, opts = load(); fams = g["families"]; slugs = list(opts)
    lines = ["# Feature asymmetry — union table from the per-option manifests", "",
             "M = measured in the comparison or an experiment · I = implemented but not used by the comparison · — = not applicable (reason in the manifest)", "",
             "| Capability family | " + " | ".join(opts[s]["option"].split(" (")[0] for s in slugs) + " |", "|---|" + "---|" * len(slugs)]
    empty = 0
    for f in fams:
        cells = []
        for s in slugs:
            st = next((x["stance"] for x in opts[s]["families"] if x["name"] == f), None)
            if st is None: empty += 1
            cells.append(SYM.get(st, "?"))
        lines.append(f"| {f} | " + " | ".join(cells) + " |")
    unreviewed = sum(1 for s in slugs for x in opts[s]["families"] if not x.get("reviewed"))
    total = sum(len(opts[s]["families"]) for s in slugs)
    lines += ["", f"Options: {len(slugs)} · families: {len(fams)} · cells: {total} · empty: {empty} · unreviewed: {unreviewed}/{total}", "",
              "Per option — M / I / — counts:", ""]
    for s in slugs:
        c = {k: sum(1 for x in opts[s]["families"] if x["stance"] == k) for k in SYM}
        lines.append(f"- {opts[s]['option']}: M {c['measured-in-comparison']} · I {c['implemented']} · — {c['not-applicable']}  (surface: {opts[s]['surface']})")
    out = "\n".join(lines) + "\n"
    if write:
        (ROOT / "sandbox/grand/report").mkdir(exist_ok=True)
        (ROOT / "sandbox/grand/report/asymmetry.md").write_text(out)
    print(out); return empty

def _hh():
    return str(ROOT / "1_blockchain-identity")

def _run(cmd, cwd, timeout=1800):
    t0 = time.time()
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout + r.stderr, round(time.time() - t0, 1)

def _summary_line(out, pat=r"(\d+) passing(?: \(.*?\))?(?:\s+(\d+) failing)?"):
    m = re.search(pat, out); return (int(m.group(1)), int(m.group(2) or 0)) if m else (None, None)

def smoke():
    rc, out, dt = _run(["npx", "hardhat", "run", "../sandbox/grand/smoke.js"], _hh())
    ok = rc == 0 and "conform" in out and "FAILED" not in out
    print(f"smoke: {'ok' if ok else 'FAIL'} ({dt}s) — {[l for l in out.splitlines() if 'conform' in l or 'failed' in l][-1:]}")
    return {"stage": "smoke", "ok": ok, "seconds": dt, "detail": [l for l in out.splitlines() if l.startswith('==')]}

def l1():
    files = sorted(str(f) for f in (ROOT / "1_blockchain-identity/test/L1-identity-mechanisms").glob("*.test.js"))
    rc, out, dt = _run(["npx", "hardhat", "test", *files], _hh())
    p, f = _summary_line(out); ok = rc == 0 and p and not f
    print(f"L1: {'ok' if ok else 'FAIL'} {p} passing / {f} failing ({dt}s)")
    return {"stage": "L1", "ok": ok, "passing": p, "failing": f, "seconds": dt}

def l2():
    rc, out, dt = _run(["npx", "hardhat", "test"], _hh())
    p, f = _summary_line(out); ok = rc == 0 and p and not f
    print(f"L1+L2 (whole Hardhat tree): {'ok' if ok else 'FAIL'} {p} passing / {f} failing ({dt}s)")
    return {"stage": "L1+L2", "ok": ok, "passing": p, "failing": f, "seconds": dt}

def py():
    rc, out, dt = _run([str(ROOT / "sandbox/py-suites/run.sh")], str(ROOT))
    m = re.search(r"(\d+) passed", out); p = int(m.group(1)) if m else None
    ok = rc == 0 and p and not re.search(r"\d+ (failed|error)", out)
    print(f"L3+L4 (Python): {'ok' if ok else 'FAIL'} {p} passed ({dt}s)")
    return {"stage": "L3+L4", "ok": ok, "passed": p, "seconds": dt}

def demos():
    steps, per, failures = [], {}, []
    for d in sorted((ROOT / "sandbox/options").glob("*/demos/*.js")):
        if d.name.startswith("_"): continue
        slug, fam = d.parent.parent.name, d.stem
        rc, out, dt = _run(["npx", "hardhat", "run", str(d)], _hh(), timeout=600)
        rows = []
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try: rows.append(json.loads(line))
                except Exception: pass
        summ = next((r for r in rows if r.get("summary")), None)
        ok = rc == 0 and bool(summ) and summ.get("ok") is True
        if not ok: failures.append(f"{slug}/{fam} (rc={rc})")
        n = sum(1 for r in rows if not r.get("summary"))
        gas = sum(int(r.get("gasUsed") or 0) for r in rows if not r.get("summary") and str(r.get("gasUsed", "0")).isdigit())
        flagged = sum(1 for r in rows if not r.get("summary") and re.search(r"DEFECT|OBSERVATION", str(r.get("note", "")), re.I))
        per.setdefault(slug, []).append({"family": fam, "ok": ok, "steps": n, "gas_total": gas, "flagged": flagged, "seconds": dt})
        steps += [r for r in rows if not r.get("summary")]
    rep = ROOT / "sandbox/grand/report"; rep.mkdir(exist_ok=True)
    (rep / "demos.json").write_text(json.dumps({"options": per, "steps": steps}, indent=1))
    lines = ["# Demos — every implemented feature exercised, per option and family", "",
             "steps = contract calls demonstrated (gas is the sum of the on-chain ones) · flagged = steps whose note marks a potential defect or observation (see docs/DEFECT_LOG.md)", "",
             "| Option | Family | ok | steps | gas (sum) | flagged | s |", "|---|---|---|---:|---:|---:|---:|"]
    for slug in sorted(per):
        for r in per[slug]:
            lines.append(f"| {slug} | {r['family']} | {'✓' if r['ok'] else '✗'} | {r['steps']} | {r['gas_total']:,} | {r['flagged']} | {r['seconds']} |")
    tot = sum(r["steps"] for v in per.values() for r in v); fl = sum(r["flagged"] for v in per.values() for r in v)
    lines += ["", f"Totals: {sum(len(v) for v in per.values())} demos · {tot} steps · {fl} flagged · failures: {len(failures)}"]
    (rep / "demos.md").write_text("\n".join(lines) + "\n")
    print(f"demos: {sum(len(v) for v in per.values())} run, {len(failures)} failed, {tot} steps, {fl} flagged")
    return {"stage": "demos", "ok": not failures, "demos": sum(len(v) for v in per.values()), "steps": tot, "flagged": fl, "failures": failures}

def all_():
    results = [smoke(), l1(), l2(), py(), demos()]
    matrix(write=True)
    rep = ROOT / "sandbox/grand/report"
    commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    lines = ["# Grand sandbox report", "", f"Generated {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} at commit `{commit}` by `python3 sandbox/grand/run.py all`.", "",
             "## Stages", "", "| Stage | ok | result | s |", "|---|---|---|---:|"]
    for r in results:
        res = {k: v for k, v in r.items() if k not in ("stage", "ok", "seconds", "detail")}
        lines.append(f"| {r['stage']} | {'✓' if r['ok'] else '✗'} | {res} | {r.get('seconds', '')} |")
    lines += ["", "## Reports produced", "", "- `report/asymmetry.md` — union table from the manifests (declared stances)",
              "- `report/L1-asymmetry.md` — mechanism × option table from the L1 tests (observed), with manifest agreement",
              "- `report/demos.md` — every implemented feature exercised, with gas and flagged observations",
              "- `docs/DEFECT_LOG.md` — what the sandbox found", ""]
    for name in ("asymmetry.md", "L1-asymmetry.md", "demos.md"):
        f = rep / name
        if f.exists():
            body = f.read_text().split("\n")
            lines += [f"## {name}", ""] + body[:60] + (["", f"*(truncated; see `report/{name}`)*"] if len(body) > 60 else []) + [""]
    (rep / "GRAND_REPORT.md").write_text("\n".join(lines))
    ok = all(r["ok"] for r in results)
    print(f"\nGRAND: {'ALL OK' if ok else 'FAILURES'} — report/GRAND_REPORT.md")
    return 0 if ok else 1

def check():
    empty = matrix(write=False)
    if empty: print(f"FAIL: {empty} empty cells"); return 1
    print("OK: every option x family has a stance"); return 0

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "matrix"
    cmds = {"matrix": lambda: (matrix(), 0)[1], "check": check, "smoke": lambda: 0 if smoke()["ok"] else 1,
            "l1": lambda: 0 if l1()["ok"] else 1, "l2": lambda: 0 if l2()["ok"] else 1, "py": lambda: 0 if py()["ok"] else 1,
            "demos": lambda: 0 if demos()["ok"] else 1, "all": all_}
    sys.exit(cmds.get(cmd, lambda: (print(__doc__), 2)[1])())
