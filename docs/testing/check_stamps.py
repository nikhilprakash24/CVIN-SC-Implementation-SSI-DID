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

    python3 docs/testing/check_stamps.py                    # writes STAMP_INVENTORY.md
    python3 docs/testing/check_stamps.py --check-coverage   # CI: exit 1 if a tracked result file is uncovered
"""
import glob
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
GLOBS = ["4_comparison-framework/results/*.json", "4_comparison-framework/security-analysis/results/*.json",
         "cv2x-testbed/results/*.json", "cv2x-testbed/sumo/results/*.json",
         "1_blockchain-identity/results/metrics/latest/meta.json", "1_blockchain-identity/results/metrics-rpc/latest/meta.json",
         "5_zkp-agent-identity/results/*.json"]
KEYS = {
    "date": ["date", "date_utc", "generated_at", "generatedAt", "timestamp", "generated", "at"],
    "commit": ["commit", "git_commit", "gitCommit", "baseline_commit"],
    "toolchain": ["solcVersion", "solc", "solc_version", "hardhat", "hardhat_version", "python_version", "python", "cryptography_version", "node", "node_version", "ozVersion", "libraries", "condition"],
}


# Result files without a complete stamp, classified (TSR phase 5, first item; after-action report 11 R4).
CLASSES = {
    "4_comparison-framework/results/gas_moved_by_defect_fixes_2026-10-04.json": ("history", "a diff between two runs of record, each stamped or registered; not a measurement"),
    "4_comparison-framework/results/gas_moved_by_defect_fixes_2026-10-04_pass06.json": ("history", "same"),
    "4_comparison-framework/results/gas_moved_by_merge_2026-10-06.json": ("history", "same"),
    "4_comparison-framework/results/gas_moved_by_natspec_2026-10-24.json": ("history", "diff between the results of record and one scratch re-run (not kept) after the NatSpec pass; logs a ±12-gas deployment shift from the metadata hash; not a measurement of record"),
    "4_comparison-framework/results/sensitivity.json": ("stamp producer", "no producer in the tree (optimizer sweep, July run); WM-2 A3 gap, pass 31"),
    "cv2x-testbed/sumo/results/v2v_latency.json": ("single run", "default output of one harness run; the results of record are v2v_latency_stats.json"),
    "cv2x-testbed/results/freshness_k_samehost.json": ("derived", "summary of the 12 stamped same-host replicates in freshness_k_samehost/ (#55, clone lineage #42); all_git_clean recorded"),
    "5_zkp-agent-identity/results/learning_curve.json": ("derived", "written by attacks/train_responder.py; deterministic, reproduced byte for byte by bench/run_all.sh before each run of record (AAR 19)"),
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
    return ":(top)" in src or (kind == "harness" and "runStamp(__filename)" in src)  # A6: the harness calls the shared helper


def _first(flat, keys):
    for key, negate, *kind in keys:
        if flat.get(key) is not None:
            v = flat[key]
            return (not v) if negate else bool(v), (kind[0] if kind else None)
    return None, None


# Producing code per result, for the "code changed since the stamp" column (after-action report 12,
# audit finding T-5: a stamp can be clean and still describe code the trunk no longer has). Since WM-2
# step A2 (D49) this is the scope of every producer whose results include the file, from
# tools/run_identity/scopes.json: the producer, its import closure and its declared inputs. The stamp
# helpers themselves are left out: they decide what a stamp says, not what a result is.
SCOPES = ROOT / "tools/run_identity/scopes.json"
HELPERS = {"tools/run_identity/stamp.py", "1_blockchain-identity/scripts/lib/run_stamp.js"}
# Commits that changed producing code only to call the stamp helper (no measured behaviour changed).
# A result whose producing code differs from its stamp only by these commits reads "no (stamp-only)".
# --check-coverage verifies each listed commit: within producing code, every changed line is stamp code.
STAMP_ONLY_COMMITS = {"188efec540cfb1db0064e5c5322adc26508a368b": "WM-2 A2: producers call the shared stamp helper (D49)"}
STAMP_LINE = (r"runStamp|run_stamp|_stamp\b|\bst\[|st = _stamp|\bstamp\b|scope|code_clean|code_dirty|dirtyMeasured|"
              r"PRODUCING_PATHSPECS|_code_dirty|run_identity|_sys\b|^\s*(#|//)|^\s*$|producer|environment_header\(|"
              r"H\.environment\(|def environment\(|git_dirty|\bcode_status\b|^\s*\"\"\"|`producer`|"
              r":\(top\)|return None if status is None else bool\(status\)|CPU, Python, libraries, date, commit")


def code_paths(path):
    scopes = json.loads(SCOPES.read_text())["scopes"]
    paths = sorted({q for sc in scopes.values() if any(path.startswith(r) for r in sc["results"])
                    for q in sc["paths"]} - HELPERS)
    return paths or None


def _commits_between(commit, paths):
    import subprocess
    out = subprocess.run(["git", "rev-list", f"{commit}..HEAD", "--", *paths], cwd=ROOT, capture_output=True,
                         text=True)
    return out.stdout.split() if out.returncode == 0 else None


def changed_since(commit, path):
    """'no' if the producing code is identical at HEAD, 'yes' if it differs, None if unknown."""
    import re
    import subprocess
    m = re.match(r"[0-9a-f]{7,40}", str(commit or ""))
    paths = code_paths(path)
    if not m or paths is None:
        return None
    r = subprocess.run(["git", "diff", "--quiet", m.group(0), "HEAD", "--", *paths], cwd=ROOT,
                       capture_output=True)
    state = {0: "no", 1: "yes"}.get(r.returncode)
    if state == "yes":
        commits = _commits_between(m.group(0), paths)
        if commits and all(any(c.startswith(s) for s in STAMP_ONLY_COMMITS) for c in commits):
            return "no (stamp-only)"
    return state


def verify_stamp_only():
    """Each STAMP_ONLY commit changes, within producing code, only stamp lines. Returns problems."""
    import re
    import subprocess
    scopes = json.loads(SCOPES.read_text())["scopes"]
    code = sorted({q for sc in scopes.values() for q in sc["paths"]} - HELPERS)
    pat, problems = re.compile(STAMP_LINE), []
    for sha in STAMP_ONLY_COMMITS:
        r = subprocess.run(["git", "show", "--format=", "-U0", sha, "--", *code], cwd=ROOT,
                           capture_output=True, text=True)
        if r.returncode != 0:
            problems.append(f"{sha}: not in this clone's history (a shallow checkout? CI needs fetch-depth: 0)")
            continue
        diff = r.stdout
        for line in diff.splitlines():
            if line[:1] in "+-" and not line.startswith(("+++", "---")) and not pat.search(line[1:]):
                problems.append(f"{sha}: not a stamp line: {line[:120]}")
    return problems


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


def stamp_of(p):
    """The stamp fields of one result file, or None if it is not a JSON object."""
    try:
        d = json.load(open(p))
    except Exception:
        return None
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
        have["code"] = "False (hand check)"
    have["changed"] = changed_since(have["commit"], path_of(p))
    return have


# Multi-file run directories: one aggregated row each (WM-2 step A1, N-21).
AGGREGATES = {
    "4_comparison-framework/results/infrastructure_gas_runs/run_*.json": "I4 repeated 30 times (#47)",
    "4_comparison-framework/results/scaling_verify_repeats/*.json": "scaling-verify repeats (#26)",
    "cv2x-testbed/results/freshness_k_c3/c3_*.json": "WM-2 C3: #32 and #37 configurations on one host, 2 replicates each (#52)",
    "cv2x-testbed/results/freshness_k_samehost/r*_full.json": "same-host freshness-k, full-refresh replicates (#55)",
    "cv2x-testbed/results/freshness_k_samehost/r*_probe.json": "same-host freshness-k, probe-refresh replicates (#55)",
}
# Tracked result JSON that is not stamped on its own, by class (pattern -> class, reason).
COVERED = [
    ("1_blockchain-identity/results/metrics/latest/*.json", "covered by meta.json", "harness run of record; its meta.json carries the stamp"),
    ("1_blockchain-identity/results/metrics-rpc/latest/*.json", "covered by meta.json", "HTTP-RPC run; its meta.json carries the stamp"),
    ("4_comparison-framework/results/infrastructure_gas_runs/summary.json", "derived", "summary of the 30 stamped runs"),
    ("cv2x-testbed/sumo/results/figures/*.json", "derived", "down-sampled trace for the dashboard"),
    ("cv2x-testbed/results/archive-2026-10-03/*.json", "history", "archived pre-merge results"),
    ("cv2x-testbed/results/freshness_k_c3/manifest.json", "derived", "order, commits and sha256 of the six C3 runs (report 19)"),
    ("cv2x-testbed/results/freshness_k_samehost/*.load.json", "derived", "host-load log beside each stamped same-host replicate (#55)"),
    ("docs/conformance/reports/**/*.json", "external tool output", "jest reports of the W3C DID test suite, dated by directory (#24)"),
    ("docs/conformance/reports/*.json", "external tool output", "W3C DID test-suite run summaries, dated by file name (#24)"),
]
SCOPE = ["*/results/*.json", "*/results/**/*.json", "**/results/**/*.json", "docs/conformance/reports/**/*.json"]
SCOPE_EXCLUDE = ("docs/prior-survey/", "docs/review02/", "_research-copies/", "sandbox/options/", "docs/figures/")


def tracked_results():
    import subprocess
    out = subprocess.run(["git", "ls-files", "*.json"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    return sorted(f for f in out if ("/results/" in f or f.startswith("docs/conformance/reports/"))
                  and not any(x in f for x in SCOPE_EXCLUDE))


def main():
    import fnmatch
    rows = []
    for g in GLOBS:
        for p in sorted(glob.glob(str(ROOT / g))):
            have = stamp_of(p)
            if have is not None:
                rows.append((path_of(p), have))
    aggs = []
    for pat, label in AGGREGATES.items():
        files = sorted(glob.glob(str(ROOT / pat)))
        stamps = [stamp_of(f) for f in files]
        stamps = [s for s in stamps if s is not None]
        full = [s for s in stamps if all(s[k] is not None for k in ("date", "commit", "toolchain")) and s["code"] is not None]
        aggs.append((pat, label, len(files), len(full), sorted({str(s["commit"])[:12] for s in stamps if s["commit"]}),
                     sorted({str(s["code"]) for s in stamps}), sorted({str(s["any"]) for s in stamps}),
                     sorted({str(s["changed"]) for s in stamps})))

    def complete(h):
        return all(h[k] is not None for k in ("date", "commit", "toolchain")) and h["code"] is not None
    full = sum(1 for _, h in rows if complete(h))
    # coverage account: every tracked result JSON is a row, inside an aggregate, or in a named class
    listed = {path for path, _ in rows}
    in_agg = {path_of(f) for pat in AGGREGATES for f in glob.glob(str(ROOT / pat))}
    account, uncovered = {}, []
    for f in tracked_results():
        if f in listed:
            account["own row"] = account.get("own row", 0) + 1
        elif f in in_agg:
            account["aggregated run directory"] = account.get("aggregated run directory", 0) + 1
        else:
            cls = next((c for pat, c, _ in COVERED if fnmatch.fnmatch(f, pat)), None)
            if cls:
                account[cls] = account.get(cls, 0) + 1
            else:
                uncovered.append(f)
    total = sum(account.values()) + len(uncovered)
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
             f"**Scope** (WM-2 step A1, N-21): {total} tracked result JSON files outside the lineage copies "
             f"({', '.join(SCOPE_EXCLUDE)}). " + "; ".join(f"{k}: {v}" for k, v in sorted(account.items()))
             + (f"; **uncovered: {len(uncovered)}**" if uncovered else "; uncovered: 0") + ".", "",
             f"{full} of {len(rows)} individually listed result files carry a complete stamp.", "",
             "| File | date | commit | dirty (code) | dirty (any) | code changed since | toolchain | class |", "|---|---|---|---|---|---|---|---|"]
    for path, h in rows:
        cell = lambda v: "MISSING" if v is None else str(v)[:24]
        cls = (f"hand check: {HAND_CHECKED[path]}" if path in HAND_CHECKED else "") if complete(h) else ("**unclassified**" if path not in CLASSES else f"{CLASSES[path][0]}: {CLASSES[path][1]}")
        lines.append(f"| `{path}` | {cell(h['date'])} | {cell(h['commit'])} | {cell(h['code'])} | {cell(h['any'])} | "
                     f"{cell(h['changed'])} | {cell(h['toolchain'])} | {cls} |")
    lines += ["", "## Run directories (one row each)", "",
              "| Files | What | runs | complete stamps | commits | dirty (code) | dirty (any) | code changed since |",
              "|---|---|---|---|---|---|---|---|"]
    for pat, label, n, nfull, commits, codes, anys, changed in aggs:
        lines.append(f"| `{pat}` | {label} | {n} | {nfull} | {', '.join(commits) or 'MISSING'} | {', '.join(codes)} | {', '.join(anys)} | {', '.join(changed)} |")
    lines += ["", "## Covered without an own stamp", "", "| Files | Class | Why |", "|---|---|---|"]
    lines += [f"| `{pat}` | {c} | {why} |" for pat, c, why in COVERED]
    if uncovered:
        lines += ["", "## Uncovered (add a row, an aggregate or a class)", ""] + [f"- `{f}`" for f in uncovered]
    if "--check-coverage" in sys.argv:
        # CI guard (WM-2 A1): a new result file must carry a complete stamp, sit in an aggregate, or have a class
        unclassified = [path for path, h in rows if not complete(h) and path not in CLASSES]
        bad = uncovered + unclassified
        stamp_only = verify_stamp_only()
        for problem in stamp_only:
            print("STAMP_ONLY_COMMITS:", problem)
        if bad:
            print("result files without a complete stamp, an aggregate or a class: " + ", ".join(bad))
        if bad or stamp_only:
            sys.exit(1)
        print(f"stamp coverage: {total} tracked result files, 0 uncovered")
        return
    (ROOT / "docs/testing/STAMP_INVENTORY.md").write_text("\n".join(lines) + "\n")
    print(f"{full}/{len(rows)} fully stamped; {len(aggs)} run directories; {total} files in scope, {len(uncovered)} uncovered; wrote docs/testing/STAMP_INVENTORY.md")


if __name__ == "__main__":
    main()
