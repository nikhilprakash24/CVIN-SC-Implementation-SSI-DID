#!/usr/bin/env python3
"""Inventory which results of record carry a run stamp (plan 2026-10-09 P3.3; TSR S11).

A stamp is: when (date), what code (commit), whether the producing code was clean, and on which
toolchain/host. Writes docs/testing/STAMP_INVENTORY.md. It reports; it does not yet fail, because
stamping every producer is a later step of the plan (each producer listed MISSING is the work list).

Two cleanliness columns, both read as "dirty" (True = not clean):
  code  -- the producing code only (run_stamp.js `dirty`, harness `dirtyMeasured`, header `code_clean`
           negated). This is what a run of record requires (guide rule 1.1.6).
  any   -- any file in the tree (run_stamp.js `dirtyAnyFile`, harness `dirty`, header `tree_clean`
           negated). False here implies clean code; True says nothing about the code.
A code flag is marked "inert" when the flag's own source at the stamp's commit used pathspecs that
could not match (fault found in after-action report 11): such a stamp is vouched for by `any` or by
the hand check recorded in the claim register.

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
    "toolchain": ["solcVersion", "solc", "solc_version", "hardhat", "hardhat_version", "python_version", "python", "cryptography_version", "node", "node_version", "ozVersion", "libraries", "condition"],
}


# Result files without a complete stamp, classified (TSR phase 5, first item; after-action report 11 R4).
CLASSES = {
    "4_comparison-framework/results/gas_moved_by_defect_fixes_2026-10-04.json": ("history", "a diff between two runs of record, each stamped or registered; not a measurement"),
    "4_comparison-framework/results/gas_moved_by_defect_fixes_2026-10-04_pass06.json": ("history", "same"),
    "4_comparison-framework/results/gas_moved_by_merge_2026-10-06.json": ("history", "same"),
    "4_comparison-framework/results/gas_benchmark_stats.json": ("stamp producer", "4_comparison-framework/performance-metrics/run_gas_stats.py"),
    "4_comparison-framework/results/sensitivity.json": ("stamp producer", "1_blockchain-identity/scripts/benchmark_scaling.js (July run; re-run due)"),
    "4_comparison-framework/results/w3c_compliance.json": ("stamp producer", "cv2x-testbed/scripts/w3c_compliance_checker.py"),
    "4_comparison-framework/security-analysis/results/attack_results.json": ("stamp producer", "1_blockchain-identity/test/L2-identity-system/security/attackHarness.js"),
    "4_comparison-framework/security-analysis/results/security_matrix.json": ("stamp producer", "4_comparison-framework/security-analysis/attack_scenarios.py"),
    "cv2x-testbed/sumo/results/v2v_latency.json": ("single run", "default output of one harness run; the results of record are v2v_latency_stats.json"),
}
# (The first I3 and I4 runs at 1e690c3 were hand-checked too; they were replaced by the runs at f1f9e37,
# whose flags are live. Record: after-action report 11 R3.)
# Runs whose code flag was inert or absent and whose tree had other files changed: producing code
# checked by hand (diff against the stamp's commit, producer mtimes before the run, or a clean tree
# seconds before in the same scripted sequence). Shown as "False (hand check)" with the reference.
HAND_CHECKED = {
    "4_comparison-framework/results/mobi_vid_backends.json": "AAR-11 R3: tree clean at 02:27:39 (gas_benchmark), outputs-only commit d54178e",
    "4_comparison-framework/results/scaling_lifetime.json": "same",
    "4_comparison-framework/results/scaling_marginal.json": "same",
    "4_comparison-framework/security-analysis/results/onchain_security.json": "same",
}
CODE_DIRTY = [("dirty", False, "run_stamp"), ("dirtyMeasured", False, "harness"), ("code_clean", True, None), ("code_dirty", False, "sumo")]
ANY_DIRTY = [("dirtyAnyFile", False), ("tree_clean", True), ("git_dirty", False)]
FLAG_SOURCE = {"run_stamp": "1_blockchain-identity/scripts/lib/run_stamp.js",
               "harness": "1_blockchain-identity/benchmarks/run.js",
               "sumo": "cv2x-testbed/sumo/sumo_identity_integration.py"}


def _flag_live(kind, commit):
    """Did the producing-code flag's source at `commit` use root-anchored pathspecs?"""
    import subprocess
    if kind is None or not commit:
        return True
    try:
        src = subprocess.run(["git", "show", f"{str(commit)[:40]}:{FLAG_SOURCE[kind]}"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
    except Exception:  # noqa: BLE001
        return False
    return ":(top)" in src


def _first(flat, keys):
    for key, negate, *kind in keys:
        if flat.get(key) is not None:
            v = flat[key]
            return (not v) if negate else bool(v), (kind[0] if kind else None)
    return None, None


# Producing code per result family, for the "code changed since the stamp" column (after-action report 12,
# audit finding T-5: a stamp can be clean and still describe code the trunk no longer has).
JS_SHARED = ["1_blockchain-identity/contracts", "1_blockchain-identity/hardhat.config.js",
             "1_blockchain-identity/package-lock.json", "cv2x-testbed/contracts"]
PY_SHARED = ["cv2x-testbed/identity", "2_w3c-ssi-layer", "cv2x-testbed/contracts"]
SUMO = ["cv2x-testbed/sumo", ":(exclude)cv2x-testbed/sumo/results"]
S = "1_blockchain-identity/scripts/"
PRODUCER = {  # result file (prefix) -> its producer script(s); the shared code of its family is added
    "4_comparison-framework/results/gas_benchmark": [S + "benchmark_gas.js"],
    "4_comparison-framework/results/mobi_vid_backends": [S + "mobi_vid_backend_sweep.js"],
    "4_comparison-framework/results/scaling_lifetime": [S + "benchmark_scaling.js"],
    "4_comparison-framework/results/scaling_marginal": [S + "benchmark_scaling.js"],
    "4_comparison-framework/results/pseudonym_pool": [S + "experiment_pseudonym_pool.js"],
    "4_comparison-framework/results/infrastructure_gas": [S + "infrastructure_gas.js"],
    "4_comparison-framework/security-analysis/results/onchain_security": [S + "security_scenarios.js", "1_blockchain-identity/test/L2-identity-system/security"],
    "4_comparison-framework/results/scaling_verify": ["cv2x-testbed/sumo/run_verify_scaling.py"],
    "cv2x-testbed/results/freshness_k": ["cv2x-testbed/scripts/experiment_freshness_k.py"],
    "cv2x-testbed/results/lifecycle_parity": ["cv2x-testbed/scripts/experiment_lifecycle_parity.py"],
    "cv2x-testbed/results/pki_vs_erc1056": ["cv2x-testbed/scripts/experiment_pki_vs_erc1056.py"],
}
HARNESS_CODE = ["1_blockchain-identity/benchmarks", "1_blockchain-identity/contracts", "1_blockchain-identity/hardhat.config.js",
                "1_blockchain-identity/package-lock.json"]


def code_paths(path):
    if path.startswith("1_blockchain-identity/results/metrics"):
        return HARNESS_CODE
    if path.startswith("cv2x-testbed/sumo/"):
        return SUMO + PY_SHARED
    for prefix, scripts in PRODUCER.items():
        if path.startswith(prefix):
            return scripts + (PY_SHARED if scripts[0].endswith(".py") else JS_SHARED)
    return (PY_SHARED + ["cv2x-testbed/scripts"]) if path.startswith("cv2x-testbed/") else (JS_SHARED + [S])


def changed_since(commit, path):
    """'no' if the producing code is identical at HEAD, 'yes' if it differs, None if unknown."""
    import re
    import subprocess
    m = re.match(r"[0-9a-f]{7,40}", str(commit or ""))
    if not m:
        return None
    r = subprocess.run(["git", "diff", "--quiet", m.group(0), "HEAD", "--", *code_paths(path)], cwd=ROOT,
                       capture_output=True)
    return {0: "no", 1: "yes"}.get(r.returncode)


def path_of(p):
    return str(pathlib.Path(p).relative_to(ROOT))


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
            if flat.get("dirtyMeasured") is not None:  # metrics harness: `dirty` is its whole-tree flag
                code, kind, anyd = bool(flat["dirtyMeasured"]), "harness", flat.get("dirty")
            else:
                code, kind = _first(flat, CODE_DIRTY)
                anyd = _first(flat, ANY_DIRTY)[0]
            live = code is not None and _flag_live(kind, have["commit"])
            have["any"] = anyd
            if live:
                have["code"] = code
            elif anyd is False:
                have["code"] = "False (from any)"
            else:
                have["code"] = None if code is None else f"{code} (inert)"
            if not live and anyd is not False and path_of(p) in HAND_CHECKED:
                have["code"] = f"False (hand check)"
            have["changed"] = changed_since(have["commit"], path_of(p))
            rows.append((path_of(p), have))
    def complete(h):
        return all(h[k] is not None for k in ("date", "commit", "toolchain")) and h["code"] is not None
    full = sum(1 for _, h in rows if complete(h))
    lines = ["# Stamp Inventory — results of record", "",
             "**Generated** by `docs/testing/check_stamps.py`. A stamp = date, commit, producing-code cleanliness, "
             "toolchain. Columns *code* and *any* are both \"dirty\" (True = not clean): *code* covers the producing "
             "code only (what a run of record requires, guide rule 1.1.6); *any* covers every file, so False there "
             "implies clean code and True says nothing. *inert*: the code flag's source at that commit could not "
             "detect a change (after-action report 11); such a stamp is vouched for by *any* or by the hand check in "
             "the claim register. Rows without a complete stamp carry a class: *stamp producer* (the work list), "
             "*history* (a diff of two runs, exempt), *single run* (not a result of record). *code changed since*: whether the "
             "producing code of the result's family differs between the stamped commit and HEAD (yes = the result describes "
             "code the trunk no longer has; re-run or disclose).", "",
             f"{full} of {len(rows)} result files carry a complete stamp.", "",
             "| File | date | commit | dirty (code) | dirty (any) | code changed since | toolchain | class |", "|---|---|---|---|---|---|---|---|"]
    for path, h in rows:
        cell = lambda v: "MISSING" if v is None else str(v)[:24]
        cls = (f"hand check: {HAND_CHECKED[path]}" if path in HAND_CHECKED else "") if complete(h) else ("**unclassified**" if path not in CLASSES else f"{CLASSES[path][0]}: {CLASSES[path][1]}")
        lines.append(f"| `{path}` | {cell(h['date'])} | {cell(h['commit'])} | {cell(h['code'])} | {cell(h['any'])} | "
                     f"{cell(h['changed'])} | {cell(h['toolchain'])} | {cls} |")
    (ROOT / "docs/testing/STAMP_INVENTORY.md").write_text("\n".join(lines) + "\n")
    print(f"{full}/{len(rows)} fully stamped; wrote docs/testing/STAMP_INVENTORY.md")


if __name__ == "__main__":
    main()
