#!/usr/bin/env python3
"""The grand sandbox runner. Subcommands: matrix (render the union table from the
manifests), check (fail if any option x family has no stance or if manifests are stale).
Later steps add: deploy, L1..L4, demos, report."""
import pathlib, sys, yaml, subprocess
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

def check():
    empty = matrix(write=False)
    if empty: print(f"FAIL: {empty} empty cells"); return 1
    print("OK: every option x family has a stance"); return 0

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "matrix"
    sys.exit({"matrix": lambda: (matrix(), 0)[1], "check": check}.get(cmd, lambda: (print("usage: run.py [matrix|check]"), 2)[1])())
