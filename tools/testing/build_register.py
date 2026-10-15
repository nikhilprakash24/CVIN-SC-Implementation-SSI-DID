#!/usr/bin/env python3
"""Build the Test Case Register and Coverage Matrix (TSR Plan v1.0, Phase 1, v0).

Reads every Mocha test (1_blockchain-identity/test), every pytest test
(2_w3c-ssi-layer, cv2x-testbed/tests), the script-style use-case suite and the
W3C compliance checker, and emits:

  docs/testing/test_register.csv / .json   one row per (test, subject)
  docs/testing/COVERAGE_MATRIX.md          Function x SUT per property class
  docs/testing/UNTAGGED.md                 tests with no explicit [TC-...] tag
  docs/testing/UNMAPPED.md                 tests whose op/class came from no rule

Mapping precedence: explicit tag in the test title (`[TC-<sut>-<op>-<cls>...]`)
or a `@pytest.mark.tc("TC-...")` marker > file defaults > title rules
(tools/testing/mapping_rules.json). Nothing here is typed by hand except the
rules file; re-run after any test change. Exit status is non-zero only when
--strict is given and untagged tests exist (Phase 3 gate).
"""
import csv, json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULES = json.loads((ROOT / "tools/testing/mapping_rules.json").read_text())
OUT = ROOT / "docs/testing"
OUT.mkdir(parents=True, exist_ok=True)

SUTS = ["erc1056", "erc1056w", "erc721", "erc725", "erc725xy", "erc735", "erc1155", "erc4337", "lsp8", "cvin",
        "mobi-v1", "mobi-v2", "mobi-backends", "cv2x-erc1056", "pki", "central", "did-resolver", "vc-layer",
        "v2v-path", "use-cases", "pipeline"]
ADAPTERS = ["erc1056", "erc1056w", "erc721", "erc725", "erc735", "erc1155", "erc725xy", "lsp8", "erc4337", "cvin"]
OPS_B1 = ["C1", "C2", "R1", "R2", "R3", "R4", "U1", "U2", "U3", "U4", "U5", "D1", "D2", "D3", "V1", "V3", "V5", "V6"]
OPS_B2 = ["L01", "L02", "L12", "L14", "L16"]
OPS_B3 = [f"K{i}" for i in range(1, 13)]
OPS_B4 = [f"M{i}" for i in range(1, 9)]
OPS_X = ["U6", "pipeline-stats", "misc"]
ALL_OPS = OPS_B1 + ["U6", "misc"] + OPS_B2 + OPS_B3 + OPS_B4 + ["pipeline-stats"]
CLASSES = ["F", "N", "A", "W", "G", "L", "S", "D", "I", "Q"]
TAG_RE = re.compile(r"\[(TC-[A-Za-z0-9\-/;]+)\]")
MARK_RE = re.compile(r"@pytest\.mark\.tc\(\s*[\"'](TC-[^\"']+)[\"']")


def first(rules, text, default=None, n=1):
    for pat, val in rules:
        if re.search(pat, text):
            return val
    return default


def sut_for(relpath):
    for frag, s in RULES["sut_by_path"]:
        if frag in relpath:
            return s
    return "?"


def cls_for(relpath, title):
    for frag, c in RULES["file_class_defaults"]:
        if frag in relpath:
            return c, "T", "file"
    for pat, c, cell in RULES["class_rules"]:
        if re.search(pat, title, re.I):
            return c, cell, "title"
    return "F", "T", "default"


def ops_for(relpath, title, describe):
    hits = []
    for pat, op in RULES["op_rules"]:
        if re.search(pat, title + " " + describe, re.I):
            for o in op.split(";"):
                if o not in hits:
                    hits.append(o)
            if len(hits) >= 2:
                break
    src = "title"
    if not hits:
        for frag, ops in RULES["file_op_defaults"]:
            if frag in relpath:
                hits = ops.split(";")
                src = "file"
                break
    if not hits:
        hits, src = ["?"], "none"
    return hits, src


def tier_for(relpath):
    for frag, t in RULES["tier_by_path"]:
        if frag in relpath:
            return t
    return "full"


def in_ci(relpath):
    return any(relpath.startswith(p) for p in RULES["ci_paths"])


def hyps_for(cls, sut):
    out = []
    for c, s, h in RULES["hyp_by_class_sut"]:
        if (c == "*" or c == cls) and (s == "*" or s == sut) and h not in out:
            out.append(h)
    return ";".join(out)


rows = []
untagged = []
unmapped = []


def add(relpath, line, framework, title, describe, suts, explicit=None):
    tag = explicit or (TAG_RE.search(title).group(1) if TAG_RE.search(title) else None)
    if tag:
        parts = tag.split("-")
        sut_list = [parts[1]] if len(parts) > 1 else suts
        ops = [parts[2]] if len(parts) > 2 else ["?"]
        cls, cell, src = (parts[3][0] if len(parts) > 3 else "F"), ("N" if "N/A" in title else "T"), "tag"
        opsrc = "tag"
    else:
        untagged.append(f"{relpath}:{line}  {title}")
        cls, cell, src = cls_for(relpath, title)
        ops, opsrc = ops_for(relpath, title, describe)
        sut_list = suts
    if "?" in ops or sut_list == ["?"]:
        unmapped.append(f"{relpath}:{line}  [{';'.join(sut_list)}] [{';'.join(ops)}] {title}")
    for sut in sut_list:
        for op in ops:
            tc = tag or f"TC-{sut}-{op}-{cls}-{len(rows)+1:04d}"
            rows.append({
                "id": tc, "sut": sut, "op": op, "cls": cls, "cell": cell,
                "evidence": "E3" if in_ci(relpath) else "E1",
                "condition": "M1" if framework == "mocha" else ("M1" if "cv2x-testbed/tests" in relpath and "on-chain" in describe.lower() else "M0"),
                "tier": tier_for(relpath), "hyp": hyps_for(cls, sut),
                "location": f"{relpath}:{line}", "framework": framework,
                "describe": describe, "title": title.strip(),
                "mapped_by": f"cls:{src};op:{opsrc}", "source": "repo", "status": "active" if cell == "T" else "n-a",
            })


# --- Mocha ---------------------------------------------------------------
MOCHA_LINE = re.compile(r"^(\s*)(describe|context|it)\(\s*([\"'`])(.*?)\3")
for f in sorted((ROOT / "1_blockchain-identity/test").rglob("*.js")):
    rel = str(f.relative_to(ROOT))
    if f.name == "attackHarness.js":
        continue
    stack = []  # (indent, title)
    for i, ln in enumerate(f.read_text().splitlines(), 1):
        m = MOCHA_LINE.match(ln)
        if not m:
            continue
        indent, kind, title = len(m.group(1)), m.group(2), m.group(4)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if kind in ("describe", "context"):
            stack.append((indent, title))
            continue
        describe = " / ".join(t for _, t in stack)
        base = sut_for(rel)
        if base == "SECURITY":
            s = first([(re.escape(k), v) for k, v in RULES["security_describe_to_sut"]], describe, "pipeline")
            suts = [s]
        elif base == "ADAPTERS":
            suts = ADAPTERS
        elif base == "MOBI":
            suts = ["mobi-v1"] if any(k in describe or k in title for k in RULES["mobi_describe_v1_keywords"]) else ["mobi-v2"]
        else:
            suts = base.split(";")
        add(rel, i, "mocha", title, describe, suts)

# --- pytest ----------------------------------------------------------------
PY_DEF = re.compile(r"^(\s*)def (test_[A-Za-z0-9_]+)")
PY_CLASS = re.compile(r"^(\s*)class (\w+)")
PARAM = re.compile(r"@pytest\.mark\.parametrize\(\s*[\"']([^\"']+)[\"']\s*,\s*(\[.*?\])", re.S)
py_files = sorted(list((ROOT / "2_w3c-ssi-layer").rglob("test_*.py")) + list((ROOT / "cv2x-testbed/tests").rglob("test_*.py"))
                  + [ROOT / "cv2x-testbed/scripts/test_vin_encryption.py"])
for f in py_files:
    rel = str(f.relative_to(ROOT))
    lines = f.read_text().splitlines()
    cur_class = ""
    pending_mark = None
    for i, ln in enumerate(lines, 1):
        mc = PY_CLASS.match(ln)
        if mc:
            cur_class = mc.group(2)
        mm = MARK_RE.search(ln)
        if mm:
            pending_mark = mm.group(1)
        md = PY_DEF.match(ln)
        if not md:
            continue
        name = md.group(2)
        # docstring first line as extra context
        doc = ""
        for j in range(i, min(i + 3, len(lines))):
            s = lines[j].strip()
            if s.startswith(('"""', "'''")):
                doc = s.strip("\"' ")
                break
        title = name.replace("test_", "", 1).replace("_", " ") + (f" — {doc}" if doc else "")
        describe = f"{f.stem}" + (f" / {cur_class}" if cur_class else "")
        add(rel, i, "pytest", title, describe + (" on-chain" if "rpc_url" in "".join(lines[i-1:i+1]) or "erc" in ln else ""), sut_for(rel).split(";"), explicit=pending_mark)
        pending_mark = None

# --- script-style: use cases --------------------------------------------------
uc = ROOT / "cv2x-testbed/scripts/test_use_cases.py"
for i, ln in enumerate(uc.read_text().splitlines(), 1):
    m = re.match(r"^def use_case_(\d+)_([a-z0-9_]+)\(", ln)
    if m:
        n, name = m.groups()
        for op in RULES["use_case_ops"].get(n, "?").split(";"):
            rows.append({"id": f"TC-use-cases-{op}-I-UC{int(n):02d}", "sut": "use-cases", "op": op, "cls": "I", "cell": "T",
                         "evidence": "E1", "condition": "M0", "tier": "none", "hyp": "H4",
                         "location": f"{uc.relative_to(ROOT)}:{i}", "framework": "script", "describe": "test_use_cases (centralized backend + VC shim)",
                         "title": f"use case {n}: {name.replace('_', ' ')}", "mapped_by": "use_case_ops", "source": "repo", "status": "active",
                         "notes": "pass = no exception; explicit oracle only in UC 3, 6, 10, 11, 12 (plan §7.1)"})
        untagged.append(f"{uc.relative_to(ROOT)}:{i}  use_case_{n}_{name}")

# --- script-style: compliance checker ---------------------------------------
ck = ROOT / "cv2x-testbed/scripts/w3c_compliance_checker.py"
CHECK = re.compile(r"self\._run_check\(\s*spec\s*,\s*\"([^\"]+)\"\s*,\s*((?:\"[^\"]*\"\s*)+),")
src = ck.read_text()
groups = [(m.start(), m.group(1)) for m in re.finditer(r"def (_check_[a-z_]+)\(", src)]
SPEC = {"_check_did_core": ("DID Core", "did-resolver", "K8"), "_check_vc_data_model": ("VC DM", "vc-layer", "K1;K4"),
        "_check_presentations": ("VC DM", "vc-layer", "K5"), "_check_selective_disclosure": ("VC DM", "vc-layer", "K3"),
        "_check_securing_mechanism_deviations": ("VC DM", "vc-layer", "K1")}
for m in CHECK.finditer(src):
    line = src[:m.start()].count("\n") + 1
    sec, req = m.group(1), " ".join(re.findall(r"\"([^\"]*)\"", m.group(2)))
    fn = max((g for g in groups if g[0] < m.start()), key=lambda g: g[0])[1]
    spec, sut, ops = SPEC.get(fn, ("?", "?", "?"))
    if sec in ("7.1.2", "7.1.3", "7.2"): ops = "K9;K10" if sec != "7.2" else "K8"
    if "error" in req.lower() or "malformed" in req.lower() or "unsupported" in req.lower(): ops = "K10"
    cell = "T"
    for op in ops.split(";"):
        rows.append({"id": f"TC-{sut}-{op}-W-chk{line}", "sut": sut, "op": op, "cls": "W" if not re.search(r"tamper|forg|replay|stolen|wrong domain|attack", req, re.I) else "A", "cell": cell,
                     "evidence": "E3", "condition": "M0", "tier": "full", "hyp": "H2",
                     "location": f"{ck.relative_to(ROOT)}:{line}", "framework": "script", "describe": f"w3c_compliance_checker / {fn}",
                     "title": f"{spec} {sec}: {req}", "mapped_by": "checker", "source": "repo", "status": "active", "notes": ""})
    untagged.append(f"{ck.relative_to(ROOT)}:{line}  {spec} {sec}")

# --- harness capability cells (class G/L from the run of record) ---------------
cap = {}
crud = ROOT / "1_blockchain-identity/results/metrics/latest/crud.json"
run_id = "?"
if crud.exists():
    meta = json.loads((ROOT / "1_blockchain-identity/results/metrics/latest/meta.json").read_text())
    run_id = meta.get("runId", "?")
    data = json.loads(crud.read_text())
    data = data if isinstance(data, list) else data.get("rows", [])
    for r in data:
        op = r["op"].split("_")[0]
        cap[(r["adapter"], op)] = ("T" if r.get("supported", True) else "N", r.get("gasDeterministic"))
    for a in ADAPTERS:
        for op in OPS_B1:
            cell, det = cap.get((a, op), ("?", None))
            for cls in ("G", "L"):
                rows.append({"id": f"TC-{a}-{op}-{cls}-harness", "sut": a, "op": op, "cls": cls, "cell": cell,
                             "evidence": "E5", "condition": "M1-H", "tier": "measure", "hyp": "H1" if cls == "G" else "H3",
                             "location": f"1_blockchain-identity/results/metrics/latest/crud.json#{a}/{op}", "framework": "harness",
                             "describe": f"metrics harness run {run_id}", "title": f"{op} on {a} (" + ("exact gas" if cls == "G" else "latency N=30") + ")",
                             "mapped_by": "harness", "source": "repo",
                             "status": "active" if cell == "T" else "n-a",
                             "notes": "" if det in (None, True) else "gasDeterministic:false (iteration range; see plan §6.4)"})

# --- write register --------------------------------------------------------------
fields = ["id", "sut", "op", "cls", "cell", "evidence", "condition", "tier", "hyp", "location", "framework", "describe", "title", "mapped_by", "source", "status", "notes"]
with open(OUT / "test_register.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in fields})
(OUT / "test_register.json").write_text(json.dumps(rows, indent=1))

# --- matrix ----------------------------------------------------------------------
def matrix(cls, ops, suts):
    head = "| Op | " + " | ".join(suts) + " |\n|---|" + "---|" * len(suts) + "\n"
    body = ""
    for op in ops:
        cells = []
        for s in suts:
            rs = [r for r in rows if r["cls"] == cls and r["op"] == op and r["sut"] == s]
            if not rs:
                cells.append("·")
            elif all(r["cell"] == "N" for r in rs):
                cells.append("N")
            else:
                n = sum(1 for r in rs if r["cell"] == "T")
                cells.append(f"T{n}")
        body += f"| {op} | " + " | ".join(cells) + " |\n"
    return head + body

chain = ADAPTERS + ["mobi-v1", "mobi-v2"]
other = ["cv2x-erc1056", "pki", "central", "did-resolver", "vc-layer", "v2v-path", "use-cases", "pipeline"]
md = ["# Coverage Matrix (generated; do not edit)",
      "",
      f"Built by `tools/testing/build_register.py` from {len(rows)} register rows. Cells: `T<n>` = n tests/measurements with an asserting outcome · `N` = n/a, no primitive (declared) · `·` = no row (a gap until Phase 2 triages it as G/P/X). Harness cells (classes G, L) come from run `{run_id}`; all other cells from parsed test titles with the heuristic rules in `tools/testing/mapping_rules.json` (Phase 1 v0; hand review in Phase 2; explicit tags replace the heuristics in Phase 3).",
      ""]
for cls, name in [("F", "Functional"), ("N", "Negative / revert"), ("A", "Adversarial / security"), ("W", "Conformance"), ("G", "Cost (exact)"), ("L", "Latency (statistical)"), ("D", "Determinism"), ("I", "Integration / lifecycle")]:
    md.append(f"## Class {cls} — {name}")
    md.append("")
    md.append("### Chain subjects (B1 identity/credential ops)")
    md.append(matrix(cls, OPS_B1 + ["U6", "misc"] + OPS_B2, chain))
    md.append("### Credential layer, V2V path, baselines, pipeline (B3/B4 ops)")
    md.append(matrix(cls, OPS_B3 + OPS_B4 + ["pipeline-stats"] + OPS_B2, other))
    md.append("")
# roll-up
md.append("## Roll-up — rows per subject × class")
md.append("")
md.append("| SUT | " + " | ".join(CLASSES) + " | total |")
md.append("|---|" + "---|" * (len(CLASSES) + 1))
for s in SUTS:
    cnt = [sum(1 for r in rows if r["sut"] == s and r["cls"] == c and r["cell"] == "T") for c in CLASSES]
    md.append(f"| {s} | " + " | ".join(str(c) if c else "·" for c in cnt) + f" | {sum(cnt)} |")
md.append("")
md.append("## Roll-up — rows per hypothesis")
md.append("")
for h in ["H1", "H2", "H3", "H4", "H5", "PKI"]:
    md.append(f"- {h}: {sum(1 for r in rows if h in r['hyp'].split(';') and r['cell']=='T')} rows")
(OUT / "COVERAGE_MATRIX.md").write_text("\n".join(md) + "\n")

(OUT / "UNTAGGED.md").write_text("# Tests without an explicit [TC-…] tag (generated)\n\n"
                                 f"{len(untagged)} tests. Phase 3 tags them; after that this file must be empty and `--strict` fails on any entry.\n\n"
                                 + "\n".join(f"- `{u}`" for u in untagged) + "\n")
(OUT / "UNMAPPED.md").write_text("# Tests whose subject or function no rule could map (generated)\n\n"
                                 f"{len(unmapped)} tests. Fix by adding a rule to `tools/testing/mapping_rules.json` (Phase 2) or a tag (Phase 3).\n\n"
                                 + "\n".join(f"- `{u}`" for u in unmapped) + "\n")

by_fw = {}
for r in rows:
    by_fw[r["framework"]] = by_fw.get(r["framework"], 0) + 1
print(f"rows={len(rows)} by framework={by_fw} untagged={len(untagged)} unmapped={len(unmapped)} harness_run={run_id}")
if "--strict" in sys.argv and untagged:
    sys.exit(1)
