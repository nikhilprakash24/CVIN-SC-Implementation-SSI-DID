#!/usr/bin/env python3
"""The class-G (gas) charter (WM-2 step B2; TSR P4-3; guide rule 1.1.10).

Generates docs/testing/GAS_CHARTER.md:
  1. the rule: every gas figure is one of G-exact, G-seeded, G-first-call, G-mode, G-range, G-derived, G-history;
  2. the harness's varying cells, root-caused from its run of record's raw rows (every iteration, with gas split
     into intrinsic and execution, EVM steps and storage writes), not from the harness's own flag;
  3. every V row of the claim register that reports gas, with its class (hand-classified here; the check fails
     if a V row that mentions gas has no class).

    python3 docs/testing/gas_charter.py          # write GAS_CHARTER.md
    python3 docs/testing/gas_charter.py --check  # CI
"""
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUN = ROOT / "1_blockchain-identity/results/metrics/latest"
REGISTER = ROOT / "docs/MEASUREMENT_CONDITIONS.md"
OUT = ROOT / "docs/testing/GAS_CHARTER.md"

CLASSES = {
    "G-exact": "deterministic for its inputs: one value, quoted as exact",
    "G-seeded": "an incidental random input fixed by a recorded seed: exact for that seed",
    "G-first-call": "deterministic, but the first call meets different contract state: two exact values (first call, steady state)",
    "G-mode": "varies across the iterations of one cell with per-iteration inputs (keys, signatures, ids), each deterministic, so the cell reproduces run to run: the mode is quoted, with the range beside it",
    "G-range": "the varying input is the thing measured: a range over declared seeds or runs",
    "G-derived": "computed from other gas figures; inherits their classes",
    "G-history": "a record of how a past run's gas moved; not a current measurement",
}

# Register rows that report gas, classified by hand (WM-2 B2). Status V rows only; E, S and U rows are not classified.
ROWS = {
    1: ("G-exact", "Hardhat test suite, fixed signers"),
    3: ("G-exact", "gas-reporter average over the suite's calls; exact for the suite, not a single operation"),
    6: ("G-derived", "ratio of exact creation costs (#25)"),
    22: ("G-range", "the row reports 37,767–37,791 from calldata zero bytes"),
    25: ("G-exact", "benchmark_gas.js with fixed signers and its own run-to-run determinism check"),
    26: ("G-derived", "scaling and lifetime figures built from exact per-operation costs"),
    28: ("G-exact", "security scenarios with fixed accounts; the attestEvent gas is a single run"),
    29: ("G-mode", "metrics harness: modes of 36 iterations; varying cells in §2"),
    30: ("G-mode", "metrics harness lifecycle: sums of per-operation modes"),
    31: ("G-mode", "metrics harness scale: modes; the row notes ≤ 12 gas from tokenId width"),
    33: ("G-range", "lifecycle parity: the row reports birth 398,274–398,298"),
    34: ("G-mode", "metrics harness: modes of 36 iterations; varying cells in §2"),
    35: ("G-mode", "metrics harness lifecycle: sums of per-operation modes"),
    36: ("G-derived", "dominance analysis over #34 and #35"),
    38: ("G-exact", "pseudonym pool: the row states gas exact"),
    42: ("G-history", "gas moved by the 2026-10-04 defect fixes"),
    43: ("G-history", "gas moved by the pass-06 fixes"),
    47: ("G-range", "I4 over declared seeds 1–30; seed 1 exact (WM-2 B1)"),
    39: ("G-mode", "metrics harness over HTTP-RPC: gas identical to the in-process run of record (#29, #34, #35); modes as there"),
    57: ("G-exact", "layer 5 measure_gas.js: fixed proof and signers, receipt gas; view rows are eth_estimateGas"),
    49: ("G-mode", "metrics harness storage and log counts; gas column inherits §2"),
    50: ("G-mode", "metrics harness: ERC-1056 U5 varies 62,634–62,646 (calldata only); U3 exact"),
    53: ("G-mode", "metrics harness: P1 and X1 cells are modes; re-run on the merged tree, run 2026-10-21T03-28-59Z_a9e2a28"),
}


def raw_cells():
    rows = collections.defaultdict(list)
    for line in (RUN / "raw.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r.get("scenario") == "crud" and r.get("kind") == "tx" and r.get("gasUsed") is not None:
            rows[(r["adapter"], r["op"])].append(r)
    return rows


def classify(rs):
    """Root-cause class of one varying cell from its iterations."""
    rs = sorted(rs, key=lambda r: r["iteration"])
    intr = {r["gasIntrinsic"] for r in rs}
    exe = [r["gasExecution"] for r in rs]
    steps = {r["evmSteps"] for r in rs}
    causes = []
    if len(intr) > 1:
        causes.append("calldata zero bytes")
    if len(set(exe)) > 1:
        rest = set(exe[1:])
        if len(rest) == 1 and exe[0] not in rest:
            z = {r["zeroToNonzeroSstores"] for r in rs}
            causes.append("first-call state" + (" (one more new storage slot)" if len(z) > 1 else " (same storage writes; a slot already warm or set)"))
        elif len(steps) > 1:
            causes.append("execution path differs (EVM steps vary)")
        else:
            causes.append("value-dependent opcode cost (same EVM steps)")
    return causes


def build():
    crud = {(c["adapter"], c["op"]): c for c in json.loads((RUN / "crud.json").read_text())}
    cells = raw_cells()
    varying = {k: rs for k, rs in cells.items() if len({r["gasUsed"] for r in rs}) > 1}
    per_cause = collections.Counter()
    table = []
    for (a, op), rs in sorted(varying.items()):
        causes = classify(rs)
        for c in causes:
            per_cause[c.split(" (")[0]] += 1
        gas = sorted({r["gasUsed"] for r in rs})
        exe = sorted({r["gasExecution"] for r in rs})
        steps = sorted({r["evmSteps"] for r in rs})
        flag = crud.get((a, op), {}).get("gasDeterministic")
        cls = "G-first-call" if any(c.startswith("first-call") for c in causes) and len(causes) == 1 else "G-mode"
        table.append((a, op, crud[(a, op)]["gasUsed"], gas[0], gas[-1], exe[-1] - exe[0], steps[-1] - steps[0],
                      "; ".join(causes), "execution-deterministic" if flag else "execution varies", cls))

    reg = REGISTER.read_text()
    gas_rows, problems = [], []
    for line in reg.splitlines():
        m = re.match(r"^\| (\d+) \|(.*)", line)
        if not m:
            continue
        n = int(m.group(1))
        status = line.rstrip().rstrip("|").split(" | ")[-1]
        if re.search(r"\bgas\b", m.group(2), re.I) and status.lstrip(" *").startswith("V"):
            gas_rows.append(n)
            if n not in ROWS:
                problems.append(f"register row #{n} reports gas and has status V but no class in gas_charter.py ROWS")
    for n in ROWS:
        if not re.search(rf"^\| {n} \|", reg, re.M):
            problems.append(f"ROWS classifies #{n}, which is not a register row")

    L = ["# Gas Charter (Class G)", "",
         "**Generated** by `docs/testing/gas_charter.py`; do not edit. **Author:** Nikhil Prakash (MASc, UBC ECE). "
         "**Written:** 2026-10-15 (WM-2 step B2; TSR P4-3; guide rule 1.1.10).", "",
         "## 1. The rule",
         "Every gas figure quoted in the thesis or the register is in exactly one class, and is quoted as its class says.", "",
         "| Class | Meaning |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in CLASSES.items()]
    n_cells = len(cells)
    L += ["", "## 2. The metrics harness's varying cells (run of record `7a9a996`)", "",
          f"Of **{n_cells}** transaction cells (36 iterations each: 1 exact + 5 warm-up + 30 samples), **{len(varying)}** vary in total gas. "
          "The harness's own `gasDeterministic` flag tracks **execution** gas only (its comment: total gas \"may differ by a few units "
          "through calldata zero-byte pricing\"), so it marks "
          f"{sum(1 for t in table if t[8] == 'execution varies')} cells; the other "
          f"{sum(1 for t in table if t[8] != 'execution varies')} vary in calldata only. The harness tables quote the **mode**; "
          "`crud.json` stores each cell's `gasUsedRange`. Causes, computed from every iteration in `raw.jsonl`:", "",
          "| Cause | Cells |", "|---|---:|"]
    L += [f"| {c} | {k} |" for c, k in sorted(per_cause.items(), key=lambda x: -x[1])]
    L += ["", "| Standard | Operation | mode | min | max | Δ execution | Δ EVM steps | cause | harness flag | class |",
          "|---|---|---:|---:|---:|---:|---:|---|---|---|"]
    for t in table:
        L.append(f"| {t[0]} | `{t[1]}` | {t[2]:,} | {t[3]:,} | {t[4]:,} | {t[5]} | {t[6]} | {t[7]} | {t[8]} | {t[9]} |")
    L += ["", "**What follows.**",
          "- **No random input.** The harness draws every fresh key from `keccak256(\"cvin-bench/fresh-key/v1\", 42, i)` and every "
          "credential hash from a salted keccak, both skipping values with a zero byte (register §5.A), and ethers signs "
          "deterministically (RFC 6979). A cell therefore reproduces from run to run (register §5.A, reproducibility). What varies is the "
          "input from one iteration to the next: the 36 iterations of a cell use 36 different keys, and the values derived from them "
          "(signatures, token ids, created addresses) are not filtered for zero bytes. These cells are G-mode, not G-seeded: the mode is "
          "reproducible, and a single cell is quoted with its `gasUsedRange`.",
          "- **The fix, at A6.** Extending the zero-byte rule from keys and hashes to every derived calldata value (or quoting the range "
          "per cell) would move the calldata cells to G-exact. The harness code is frozen until its re-run of record (WM-2 A6, N-19), so "
          "the change lands there.",
          "- **First-call state:** deterministic. The first iteration meets a contract-global slot in a different state; quote the steady "
          "state (the mode) and, where the first call matters, its value too.",
          "- **Mechanisms not isolated:** the 8-step execution-path difference and the 2–5 gas value-dependent difference follow the "
          "per-iteration key and signature, but are not traced to an opcode. That is stated, not assumed. The plan's guess of "
          "\"address-dependent storage\" is not borne out: no varying cell changes its storage writes except lsp8 C1, which is first-call state.",
          "", "## 3. Register rows that report gas (status V)", "",
          "| Row | Class | Why |", "|---|---|---|"]
    for n in sorted(ROWS):
        L.append(f"| #{n} | {ROWS[n][0]} | {ROWS[n][1]} |")
    L += ["", f"{len(ROWS)} rows classified; every V row whose claim mentions gas ({len(gas_rows)}) has a class."]
    return "\n".join(L) + "\n", problems


def main():
    text, problems = build()
    for p in problems:
        print("PROBLEM:", p)
    if "--check" in sys.argv:
        stale = not OUT.exists() or OUT.read_text() != text
        if stale:
            print("STALE: run python3 docs/testing/gas_charter.py")
        if not (stale or problems):
            print("gas charter current; every V gas row classified")
        return 1 if (stale or problems) else 0
    OUT.write_text(text)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
