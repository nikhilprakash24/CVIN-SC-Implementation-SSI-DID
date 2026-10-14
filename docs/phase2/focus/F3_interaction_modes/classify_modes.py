#!/usr/bin/env python3
"""Classify Phase 1's chain interactions by mode (Phase 2, focus F3, start of execution).

Default taxonomy (orchestrator proposal; author decision P2-D7), one axis for reads and writes alike:
"who carries the request to the chain at the moment it is needed".
  A  direct    the party's own key and its own node connection (EOA transaction; eth_call / eth_getLogs)
  B  mediated  a third party carries it: B-submit (a relayer or bundler submits and pays for a signed
               write) or B-serve (an RPC provider or indexer answers a read)
  C  detached  no chain contact at the moment of use: a credential, cache or proof obtained earlier is
               checked in-process (reads); a write signed now and anchored later (writes)

Sources, all committed: the metrics harness run of record (operation catalogue x standard; gas and read
tables), and the grand runner's demo log (sandbox/grand/report/demos.json), whose per-step `onchain` flag
is not comparable across options (defect D61). This script therefore classifies demo steps from the
function name and the note, by stated rules, and reports both the flag-based and the rule-based counts.

    python3 docs/phase2/focus/F3_interaction_modes/classify_modes.py          # write MODE_CLASSIFICATION.md
    python3 docs/phase2/focus/F3_interaction_modes/classify_modes.py --check  # CI
After a grand run rewrites demos.json, regenerate this file as well.
"""
import collections
import csv
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TABLES = ROOT / "1_blockchain-identity/results/metrics/latest/tables"
DEMOS = ROOT / "sandbox/grand/report/demos.json"
OUT = HERE / "MODE_CLASSIFICATION.md"

WRITE_MODE = {  # harness operation -> mode of the write path it exercises
    "U5_meta_tx": "B-submit",
}
READ_OPS = ("R1_resolve_owner", "R2_resolve_by_vin", "R3_resolve_document", "R4_verify_delegate", "V6_status_check")
VIEW = re.compile(r"(^|\.)(get|is|has|valid|resolve|lookup|identityOwner|owner(Of)?|balanceOf|tokenURI|claims?|keys?|"
                  r"supportsInterface|changed|nonce|history|verify|read|query|count|status|exists)", re.I)
REVERT = re.compile(r"revert|rejected|refused|denied|must fail|expected fail", re.I)
OFFCHAIN = re.compile(r"sign|signature|credential|\bVC\b|presentation|hash|encrypt|decrypt|did document|proof|off[- ]chain|local", re.I)


def table(name):
    with open(TABLES / name) as f:
        return list(csv.reader(f))


def classify_step(s):
    """Rule-based class of one demo step: write-A (mined), read-A (view call), revert-A (expected revert),
    detached-C (off-chain work), unclassified."""
    gas = str(s.get("gasUsed", "0"))
    fn, note = str(s.get("fn", "")), str(s.get("note", ""))
    if s.get("onchain") and gas not in ("0", "", "None"):
        return "write (A, mined)"
    if REVERT.search(note) or REVERT.search(s.get("step", "")):
        return "expected revert (A)"
    if VIEW.search(fn.split(".")[-1]) and not OFFCHAIN.search(fn):
        return "read (A, view call)"
    if OFFCHAIN.search(fn) or OFFCHAIN.search(note):
        return "off-chain (C)"
    return "unclassified"


def build():
    gas = table("crud_gas.csv")
    head = gas[0][1:]
    writes = collections.OrderedDict()
    for r in gas[1:]:
        op = r[0]
        cells = dict(zip(head, r[1:]))
        mode = WRITE_MODE.get(op, "A")
        writes[op] = (mode, sum(1 for v in cells.values() if v != "n/a"), len(cells))
    reads = table("crud_reads.csv")
    rhead = reads[0][1:]
    readrows = []
    for r in reads[1:]:
        if r[0] not in READ_OPS:
            continue
        cells = dict(zip(rhead, r[1:]))
        rpcs = [int(v.split(" / ")[0]) for v in cells.values() if v != "n/a"]
        readrows.append((r[0], min(rpcs), max(rpcs), sum(1 for v in cells.values() if v != "n/a")))

    demos = json.loads(DEMOS.read_text())["steps"]
    by_option = collections.defaultdict(collections.Counter)
    flag = collections.defaultdict(collections.Counter)
    for s in demos:
        by_option[s["option"]][classify_step(s)] += 1
        mined = s.get("onchain") and str(s.get("gasUsed", "0")) not in ("0", "", "None")
        flag[s["option"]]["mined" if mined else ("on-chain, no gas" if s.get("onchain") else "flag: off-chain")] += 1
    classes = ["write (A, mined)", "read (A, view call)", "expected revert (A)", "off-chain (C)", "unclassified"]

    L = ["# F3 Mode Classification of Phase 1's Chain Interactions", "",
         "**Generated** by `docs/phase2/focus/F3_interaction_modes/classify_modes.py`; do not edit. "
         "**Author:** Nikhil Prakash (MASc, UBC ECE). **Taxonomy:** the orchestrator's default (A direct, B mediated "
         "(B-submit, B-serve), C detached), pending the author's decision P2-D7 (`docs/phase2/DECISIONS.md`).", "",
         "## 1. Writes in the harness operation catalogue (run of record, M1-H)", "",
         "| Operation | Mode | standards with this operation |", "|---|---|---:|"]
    for op, (mode, n, tot) in writes.items():
        L.append(f"| `{op}` | {mode} | {n} of {tot} |")
    L += ["", "Every harness write is Mode A except `U5_meta_tx`: ERC-1056 signed operations sent by a relayer and "
          "ERC-4337 UserOperations sent by a bundler (B-submit; gas in register #50). No write in Phase 1 is Mode C.", "",
          "## 2. Reads in the harness (all Mode A: the harness's own node; RPC calls per read)", "",
          "| Operation | fewest RPC calls | most RPC calls | standards |", "|---|---:|---:|---:|"]
    for op, lo, hi, n in readrows:
        L.append(f"| `{op}` | {lo} | {hi} | {n} |")
    L += ["", "B-serve (a provider or indexer answers) was never measured: every read went to a local node (F3 capture §2). "
          "Mode C reads are the testbed's cached verification (register #27, #32, #37, #46), not harness operations.", "",
          "## 3. Demo steps, classified by rule (grand runner log)", "",
          f"Source: `sandbox/grand/report/demos.json` ({len(demos)} steps). Rules: a step with gas is a mined write; a note or "
          "step naming a revert is an expected revert; a view-style function name is a read; a signing, credential, hashing "
          "or proof function is off-chain work. Rule-based and approximate: `unclassified` is reported, not hidden.", "",
          "| Option | " + " | ".join(classes) + " | flag-based off-chain (D61) |", "|---|" + "---:|" * (len(classes) + 1)]
    tot = collections.Counter()
    for opt in sorted(by_option):
        c = by_option[opt]
        tot.update(c)
        L.append(f"| {opt} | " + " | ".join(str(c[k]) for k in classes) + f" | {flag[opt]['flag: off-chain']} |")
    L.append("| **all** | " + " | ".join(f"**{tot[k]}**" for k in classes) +
             f" | **{sum(f['flag: off-chain'] for f in flag.values())}** |")
    L += ["", "The flag-based column is what the grand report's \"off-chain\" count adds up from. The rule-based columns show "
          "how much of it is reads and expected reverts logged under the flag (D61)."]
    return "\n".join(L) + "\n"


def main():
    text = build()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text() != text:
            print("STALE: run docs/phase2/focus/F3_interaction_modes/classify_modes.py")
            return 1
        print("F3 mode classification current")
        return 0
    OUT.write_text(text)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
