#!/usr/bin/env python3
"""Generate the TSR test register and coverage matrix from what the suites already record.

Plan 2026-10-09 P3.1 (TSR phases 1-3, adapted per docs/testing/README.md §2). Principle "tag, do
not relocate": no test title is changed. Each test cell gets a deterministic TC identifier
derived from the record that already identifies it:

    L1 uniform mechanisms   sandbox/grand/report/L1-asymmetry.json     TC-<slug>-<op>-F (and -G when gas is measured)
    strict security harness 4_comparison-framework/security-analysis/results/attack_results.json  TC-<slug>-<attack>-A
    feature demos           sandbox/grand/report/demos.json             TC-<slug>-<family>-F
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
    return reg_text, "\n".join(lines) + "\n"


def main():
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
