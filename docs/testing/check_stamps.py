#!/usr/bin/env python3
"""Inventory which results of record carry a run stamp (plan 2026-10-09 P3.3; TSR S11).

A stamp is: when (date), what code (commit), whether the tree was clean (dirty), and on which
toolchain/host. Writes docs/testing/STAMP_INVENTORY.md. It reports; it does not yet fail, because
stamping every producer is a later step of the plan (each producer listed MISSING is the work list).

    python3 docs/testing/check_stamps.py
"""
import glob
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
GLOBS = ["4_comparison-framework/results/*.json", "4_comparison-framework/security-analysis/results/*.json",
         "cv2x-testbed/results/*.json", "cv2x-testbed/sumo/results/*.json",
         "1_blockchain-identity/results/metrics/latest/meta.json"]
KEYS = {
    "date": ["date", "date_utc", "generated_at", "generatedAt", "timestamp", "generated"],
    "commit": ["commit", "git_commit", "gitCommit", "baseline_commit"],
    "dirty": ["dirty", "git_dirty", "tree_clean"],
    "toolchain": ["solcVersion", "solc", "solc_version", "hardhat", "hardhat_version", "python_version", "python", "cryptography_version", "node", "node_version", "ozVersion", "libraries", "condition"],
}


def flatten(d, depth=0):
    if not isinstance(d, dict) or depth > 2:
        return {}
    out = dict(d)
    for v in d.values():
        if isinstance(v, dict):
            out.update(flatten(v, depth + 1))
    return out


def main():
    rows = []
    for g in GLOBS:
        for p in sorted(glob.glob(str(ROOT / g))):
            try:
                d = json.load(open(p))
            except Exception:
                continue
            flat = flatten(d) if isinstance(d, dict) else {}
            have = {k: next((flat[a] for a in alts if flat.get(a) is not None), None) for k, alts in KEYS.items()}
            rows.append((str(pathlib.Path(p).relative_to(ROOT)), have))
    full = sum(1 for _, h in rows if all(v is not None for v in h.values()))
    lines = ["# Stamp Inventory — results of record", "",
             "**Generated** by `docs/testing/check_stamps.py`. A stamp = date, commit, dirty flag, toolchain. "
             "MISSING entries are the work list for stamping their producers (plan 2026-10-09 P3.3).", "",
             f"{full} of {len(rows)} result files carry a complete stamp.", "",
             "| File | date | commit | dirty | toolchain |", "|---|---|---|---|---|"]
    for path, h in rows:
        cell = lambda v: "MISSING" if v is None else str(v)[:24]
        lines.append(f"| `{path}` | {cell(h['date'])} | {cell(h['commit'])} | {cell(h['dirty'])} | {cell(h['toolchain'])} |")
    (ROOT / "docs/testing/STAMP_INVENTORY.md").write_text("\n".join(lines) + "\n")
    print(f"{full}/{len(rows)} fully stamped; wrote docs/testing/STAMP_INVENTORY.md")


if __name__ == "__main__":
    main()
