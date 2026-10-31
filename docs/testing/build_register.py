#!/usr/bin/env python3
"""Generate the TSR test register and coverage matrix from what the suites already record.

Plan 2026-10-09 P3.1 (TSR phases 1-3, adapted per docs/testing/README.md §2). Principle "tag, do
not relocate": no test title is changed. Each test cell gets a deterministic TC identifier
derived from the record that already identifies it:

    L1 uniform mechanisms   sandbox/grand/report/L1-asymmetry.json     TC-<slug>-<op>-F (and -G when gas is measured)
    strict security harness 4_comparison-framework/security-analysis/results/attack_results.json  TC-<slug>-<attack>-A
    feature demos           sandbox/grand/report/demos.json             TC-<slug>-<family>-F
    Python layers (WM-2 A7) sandbox/grand/report/py_layers.json         TC-py-<module>-<test> (layer L3, L4 or SSI)
The coverage matrix (option x capability family) is derived from the manifests' stances and the
demo runs: N = not applicable (manifest reason), T = exercised by a passing demo, F = demo
failing (X is reserved by the TSR plan for out of scope), G = implemented but no demo; "+M" marks families measured in the comparison.

    python3 docs/testing/build_register.py           # writes docs/testing/{test_register.yaml,coverage_matrix.md}
    python3 docs/testing/build_register.py --check   # exit 1 if either is stale
"""
import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_REG = ROOT / "docs/testing/test_register.yaml"
OUT_COV = ROOT / "docs/testing/coverage_matrix.md"

# mechanism -> TSR operation id (docs/testing/README.md §2; V7 = add-claim, proposed with TSR's U6)
OP = {"create": "C1", "controller-change": "U1", "key-or-delegate": "U2", "attribute": "U3", "claim": "V7",
      "revoke": "D1", "transfer": "U4", "signed-op": "U5", "resolve": "R3"}
STD_TO_SLUG = {"ERC-1056": "erc-1056-uport", "ERC-721": "erc-721", "ERC-725": "erc-725", "ERC-725xy": "erc-725xy",
               "ERC-735": "erc-735", "ERC-1155": "erc-1155", "ERC-4337": "erc-4337", "LSP8": "lsp8",
               "MOBI-VID-V2": "mobi-vid", "CVIN-Combined": "cvin-combined"}
FAMILY_SLUG = {
    "Identity creation (explicit)": "creation", "Ownership / controller change": "controller",
    "Key / delegate management": "keys-delegates", "Attributes / data store": "attributes",
    "Claims / credentials": "claims", "Revocation / status": "revocation",
    "Delegated / signed (off-chain-authorised) execution": "signed-execution",
    "Lifecycle events / history": "lifecycle-history", "Authorisation / roles": "authorisation-roles",
    "Token economics (approvals, royalties, payments)": "token-economics", "VIN linkage": "vin-linkage",
    "DID / resolution helpers": "did-resolution",
    "Off-chain creation (identity exists before any transaction)": "offchain-creation",
    "Message signing / verification (off-chain hot path)": "offchain-messaging",
}


def load(p):
    return json.loads((ROOT / p).read_text())


# --- Test bodies that record no structured result (TSR Phase 3 / WM-2 A7; replan 2026-10-22 §3) -----------------
# Static parse of test source, so the register is reproducible without running a suite. Rules and subjects live in
# docs/testing/unit_rules.yaml; each entry records the rule that mapped it. No test title is edited (replan R-2).
import hashlib
import re

UNIT_RULES = ROOT / "docs/testing/unit_rules.yaml"
_MOCHA = re.compile(r"""^(\s*)(describe|context|it)(?:\.only|\.skip)?\(\s*(["'`])(.*?)\3""")
_PYDEF = re.compile(r"^(\s*)(?:async\s+)?def (test_\w+)\s*\(")
_PYCLS = re.compile(r"^(\s*)class (Test\w*)")
_DOCQ = ('"' * 3, "'" * 3, "r" + '"' * 3)


def _first(rules, text, default=None):
    for pat, val in rules:
        if re.search(pat, text, re.I):
            return val, pat
    return default, None


def _tc(sut, op, cls, key):
    return f"TC-{sut}-{op}-{cls}-" + hashlib.sha1(key.encode()).hexdigest()[:8]


def unit_entries(rules_path=None, root=None):
    root = root or ROOT
    r = yaml.safe_load((rules_path or UNIT_RULES).read_text())
    out, unmapped = [], []

    def classify(rel, title, desc):
        cls, why = None, None
        for frag, c in r["class_by_path"]:
            if frag in rel:
                cls, why = c, f"path:{frag}"
                break
        if cls in (None, "R"):
            c2, pat = _first(r["class_rules"], f"{desc} / {title}")
            if c2:
                cls, why = c2, f"title:{pat}"
            elif cls == "R":
                cls, why = "N", "path:regression (no title rule fired; a regression test asserts a fixed defect)"
            else:
                cls, why = "F", "default"
        op, pat = _first(r["op_rules"], title)
        where = "title"
        if op is None:
            op, pat = _first(r["op_rules"], desc)
            where = "describe"
        if op is None:
            op, pat = _first([(re.escape(f), o) for f, o in r["file_op_defaults"]], rel)
            where = "file"
        return cls, why, op or "?", f"{where}:{pat}" if pat else "none"

    def add(rel, line, layer, title, desc):
        sut, _ = _first([(re.escape(f), s) for f, s in r["subject_by_path"]], rel, "?")
        cls, cwhy, ops, owhy = classify(rel, title, desc)
        key = f"{rel}::{desc}::{title}"
        for op in ops.split(";"):
            out.append({"id": _tc(sut, op, cls, key), "layer": layer, "sut": sut, "op": op, "class": cls,
                        "evidence": "E3", "verdict": "asserted", "location": f"{rel}:{line}", "title": title,
                        "mapped_by": f"class {cwhy}; op {owhy}", "source": "docs/testing/unit_rules.yaml"})
            if sut == "?" or op == "?":
                unmapped.append(f"{rel}:{line} {title}")

    for base in r["sources"]["mocha"]:
        for f in sorted((root / base).rglob("*.js")):
            rel, stack = str(f.relative_to(root)), []
            for i, ln in enumerate(f.read_text().splitlines(), 1):
                m = _MOCHA.match(ln)
                if not m:
                    continue
                ind, kind, title = len(m.group(1)), m.group(2), m.group(4)
                while stack and stack[-1][0] >= ind:
                    stack.pop()
                if kind == "it":
                    add(rel, i, "L2u", title, " / ".join(t for _, t in stack))
                else:
                    stack.append((ind, title))
    for base in r["sources"]["pytest"]:
        for f in sorted((root / base).rglob("test_*.py")):
            rel, cls_name, lines = str(f.relative_to(root)), "", f.read_text().splitlines()
            for i, ln in enumerate(lines, 1):
                mc = _PYCLS.match(ln)
                if mc:
                    cls_name = mc.group(2)
                md = _PYDEF.match(ln)
                if not md:
                    continue
                if not md.group(1):
                    cls_name = ""
                doc = ""
                for j in range(i, min(i + 4, len(lines))):
                    t = lines[j].strip()
                    if t.startswith(_DOCQ):
                        doc = t.lstrip("r").strip("\"' ")
                        break
                title = md.group(2)[5:].replace("_", " ") + (f" — {doc}" if doc else "")
                add(rel, i, "py", title, f.stem + (f" / {cls_name}" if cls_name else ""))
    ids = [e["id"] for e in out]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    return out, unmapped, dup


def check_complete(root=None, rules_path=None):
    """Guard (replan T5): every tracked test file is registered from source, registered from its results, or
    excluded with a reason; and every registered source file's parsed count equals an independent token count."""
    import subprocess
    root = root or ROOT
    r = yaml.safe_load((rules_path or UNIT_RULES).read_text())
    files = subprocess.check_output(["git", "ls-files"], cwd=root, text=True).splitlines()
    tests = [f for f in files if re.search(r"(^|/)test_[^/]*\.py$|\.test\.js$|/test/[^/]*\.js$", f)
             and "node_modules/" not in f]
    covered = [b + "/" for b in r["sources"]["mocha"] + r["sources"]["pytest"]]
    covered += [p for p, _ in r["results_derived"]] + [p for p, _ in r["excluded"]]
    problems = [f"not registered and not excluded: {f}" for f in tests if not any(f.startswith(c) for c in covered)]
    units, _, _ = unit_entries(rules_path, root)
    parsed = {}
    for t in units:
        parsed.setdefault(t["location"].rsplit(":", 1)[0], set()).add(t["location"])
    for base in r["sources"]["mocha"]:
        for f in sorted((root / base).rglob("*.js")):
            rel = str(f.relative_to(root))
            n = len(re.findall(r"(?<![\w.$])it(?:\.only|\.skip)?\s*\(", f.read_text()))
            if n != len(parsed.get(rel, ())):
                problems.append(f"{rel}: {n} it( tokens, {len(parsed.get(rel, ()))} registered")
    for base in r["sources"]["pytest"]:
        for f in sorted((root / base).rglob("test_*.py")):
            rel = str(f.relative_to(root))
            n = len(re.findall(r"^\s*(?:async\s+)?def test_\w+", f.read_text(), re.M))
            if n != len(parsed.get(rel, ())):
                problems.append(f"{rel}: {n} test functions, {len(parsed.get(rel, ()))} registered")
    return problems


def build():
    tcs = []
    l1 = load("sandbox/grand/report/L1-asymmetry.json")
    for r in l1["records"]:
        base = f'TC-{r["option"]}-{OP.get(r["mechanism"], r["mechanism"])}'
        verdict = {"ok": "pass", "na": "n/a", "fail": "fail"}.get(r["outcome"], r["outcome"])
        loc = "1_blockchain-identity/test/L1-identity-mechanisms"
        tcs.append({"id": base + "-F", "layer": "L1", "sut": r["option"], "op": OP.get(r["mechanism"], r["mechanism"]),
                    "class": "F", "evidence": "E3", "verdict": verdict, "location": loc,
                    "reason": r.get("reason"), "source": "sandbox/grand/report/L1-asymmetry.json"})
        if r["outcome"] == "ok" and r.get("gasUsed") not in (None, "0", 0):
            tcs.append({"id": base + "-G", "layer": "L1", "sut": r["option"], "op": OP.get(r["mechanism"], r["mechanism"]),
                        "class": "G", "evidence": "E3", "verdict": "measured", "value": int(r["gasUsed"]), "location": loc,
                        "source": "sandbox/grand/report/L1-asymmetry.json"})
    sec = load("4_comparison-framework/security-analysis/results/attack_results.json")
    for std, cells in sec.items():
        if std == "metadata" or not isinstance(cells, dict):
            continue
        for attack, v in cells.items():
            if not isinstance(v, dict) or "outcome" not in v:
                continue
            tcs.append({"id": f'TC-{STD_TO_SLUG.get(std, std)}-{attack}-A', "layer": "L2", "sut": STD_TO_SLUG.get(std, std),
                        "op": attack, "class": "A", "evidence": "E3", "verdict": v["outcome"],
                        "expected": v.get("expectedRevert"), "location": "1_blockchain-identity/test/L2-identity-system/security/securityScenarios.test.js",
                        "source": "4_comparison-framework/security-analysis/results/attack_results.json"})
    demos = load("sandbox/grand/report/demos.json")["options"]
    for opt, fams in demos.items():
        for f in fams:
            tcs.append({"id": f'TC-{opt}-{f["family"]}-F', "layer": "demo", "sut": opt, "op": f["family"], "class": "F",
                        "evidence": "E2", "verdict": "pass" if f["ok"] else "fail", "steps": f["steps"],
                        "location": f'sandbox/options/{opt}/demos/{f["family"]}.js', "source": "sandbox/grand/report/demos.json"})
    # Python layers (WM-2 A7): one TC per test in the grand runner's per-test record
    py = ROOT / "sandbox/grand/report/py_layers.json"
    if py.exists():
        import hashlib
        import re as _re
        layer_of = (("sandbox/py-suites/L3-ssi/", "L3"), ("sandbox/py-suites/L4-exemplar-interactions/", "L4"),
                    ("2_w3c-ssi-layer/", "SSI"))
        seen = set()
        for t in json.loads(py.read_text())["tests"]:
            layer = next((l for pre, l in layer_of if t["file"].startswith(pre)), "py")
            stem = pathlib.Path(t["file"]).stem.removeprefix("test_")
            slug = _re.sub(r"[^A-Za-z0-9]+", "-", f'{stem}-{t["name"].removeprefix("test_")}').strip("-")[:80]
            tid = f"TC-py-{slug}"
            if tid in seen:  # parametrised or truncated names: disambiguate deterministically
                tid += "-" + hashlib.sha256(f'{t["file"]}::{t["name"]}'.encode()).hexdigest()[:6]
            seen.add(tid)
            tcs.append({"id": tid, "layer": layer, "sut": t["file"].split("/")[0] if layer == "SSI" else "py-suites",
                        "op": t["name"], "class": "F", "evidence": "E3",
                        "verdict": {"passed": "pass", "failed": "fail"}.get(t["outcome"], t["outcome"]),
                        "location": f'{t["file"]}::{t["name"]}', "source": "sandbox/grand/report/py_layers.json"})
    units, unmapped, udup = unit_entries()
    if unmapped:
        raise SystemExit(f"unmapped tests (fix docs/testing/unit_rules.yaml): {unmapped[:5]}")
    if udup:
        raise SystemExit(f"two tests share path, describe chain and title: {udup[:5]}")
    tcs.extend(units)
    tcs.sort(key=lambda t: t["id"])
    ids = [t["id"] for t in tcs]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise SystemExit(f"duplicate TC ids: {dup[:5]}")

    # coverage matrix
    manifests = {}
    for p in sorted((ROOT / "sandbox/options").glob("*/manifest.yaml")):
        m = yaml.safe_load(p.read_text())
        manifests[p.parent.name] = m
    fam_order = list(FAMILY_SLUG)
    demo_ok = {(o, f["family"]): f["ok"] for o, fams in demos.items() for f in fams}
    demo_flagged = {(o, f["family"]): f.get("flagged", 0) for o, fams in demos.items() for f in fams}
    rows = {}
    mismatches = []
    for opt, m in manifests.items():
        cells = {}
        for fam in m["families"]:
            name = fam["name"]
            slug = FAMILY_SLUG.get(name)
            if fam["stance"] == "not-applicable":
                c = "N"
                if demo_ok.get((opt, slug)):
                    mismatches.append(f"{opt} / {name}: manifest says not applicable, but a passing demo exists")
            elif (opt, slug) in demo_ok:
                c = "T" if demo_ok[(opt, slug)] else "F"
                if c == "T" and demo_flagged.get((opt, slug)):
                    c = "T*"   # passing demo with steps it flags as DEFECT or OBSERVATION (after-action report 11, C9)
            else:
                c = "G"
            if fam["stance"] == "measured-in-comparison" and c != "N":
                c += "+M"
            cells[name] = c
        rows[opt] = cells
    return tcs, rows, fam_order, mismatches


def render(tcs, rows, fam_order, mismatches=()):
    counts = {}
    for t in tcs:
        k = f'{t["layer"]}:{t["class"]}:{t["verdict"]}'
        counts[k] = counts.get(k, 0) + 1
    reg = {"about": "Generated by docs/testing/build_register.py. Do not edit; regenerate.",
           "counts": dict(sorted(counts.items())), "tests": tcs}
    reg_text = yaml.safe_dump(reg, sort_keys=False, allow_unicode=True, width=200)
    short = {n: FAMILY_SLUG[n] for n in fam_order}
    lines = ["# Coverage Matrix — option × capability family", "",
             "**Generated** by `docs/testing/build_register.py` from `sandbox/options/*/manifest.yaml` and "
             "`sandbox/grand/report/demos.json`. Do not edit; regenerate.", "",
             "T = exercised by a passing demo · T* = passing demo that flags steps (DEFECT or OBSERVATION; see "
             "`sandbox/grand/report/demos.md`) · F = demo failing · G = implemented, no demo · N = not applicable "
             "(reason in the manifest) · +M = measured in the comparison.", "",
             "| Option | " + " | ".join(short[n] for n in fam_order) + " |",
             "|---|" + "---|" * len(fam_order)]
    tally = {}
    for opt in sorted(rows):
        cells = [rows[opt].get(n, "·") for n in fam_order]
        for c in cells:
            tally[c.split("+")[0]] = tally.get(c.split("+")[0], 0) + 1   # T and T* are counted apart
        lines.append(f"| {opt} | " + " | ".join(cells) + " |")
    lines += ["", "Totals: " + ", ".join(f"{k} {v}" for k, v in sorted(tally.items())) + ".",
              "The two baselines (centralized registry, IEEE 1609.2-style PKI) are Python providers with no feature demos by "
              "design; their G cells are exercised by the Python suites and the experiments, not by demos.", "",
              f"Test register: {len(tcs)} TC entries in `docs/testing/test_register.yaml`."]
    if mismatches:
        lines += ["", "**Manifest / demo mismatches** (shown as N above):"] + [f"- {m}" for m in mismatches]
    units = [t for t in tcs if t["source"] == "docs/testing/unit_rules.yaml"]
    if units:
        cls_order = ["F", "N", "A", "W", "G", "L", "S", "D", "I"]
        lines += ["", "## Unit and Python test bodies — subject × property class", "",
                  "Count of registered tests (per-option contract tests, harness and stats tests, testbed Python tests, Phase 2 "
                  "prototypes, promote-step tests), mapped by `docs/testing/unit_rules.yaml`; each register entry records "
                  "the rule that mapped it. F functional · N negative · A adversarial · W conformance · G gas · L latency "
                  "· S scale · D determinism · I integration. A test counted under two functions is counted once here.", "",
                  "| Subject | " + " | ".join(cls_order) + " | total |", "|---|" + "---:|" * (len(cls_order) + 1)]
        seen = {}
        for t in units:
            seen.setdefault((t["sut"], t["location"]), t["class"])
        for sut in sorted({k[0] for k in seen}):
            n = [sum(1 for (s_, _), c in seen.items() if s_ == sut and c == k) for k in cls_order]
            lines.append(f"| {sut} | " + " | ".join(str(x) if x else "·" for x in n) + f" | {sum(n)} |")
        lines.append(f"| **all** | " + " | ".join(str(sum(1 for c in seen.values() if c == k)) for k in cls_order)
                     + f" | {len(seen)} |")
    return reg_text, "\n".join(lines) + "\n"


def main():
    if "--check-complete" in sys.argv:
        problems = check_complete()
        for p in problems:
            print("INCOMPLETE:", p)
        if problems:
            sys.exit(1)
        print("every tracked test file is registered, results-derived or excluded with a reason")
        return
    reg_text, cov_text = render(*build())
    if "--check" in sys.argv:
        stale = [str(p.relative_to(ROOT)) for p, t in ((OUT_REG, reg_text), (OUT_COV, cov_text))
                 if not p.exists() or p.read_text() != t]
        if stale:
            print("STALE (regenerate with docs/testing/build_register.py): " + ", ".join(stale))
            sys.exit(1)
        print("test register and coverage matrix are current")
        return
    OUT_REG.write_text(reg_text)
    OUT_COV.write_text(cov_text)
    print(f"wrote {OUT_REG.relative_to(ROOT)} and {OUT_COV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
