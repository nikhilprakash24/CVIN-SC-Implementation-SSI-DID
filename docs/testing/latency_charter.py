#!/usr/bin/env python3
"""The class-L (latency) charter (WM-2 step B3; after-action report 35).

Generates docs/testing/LATENCY_CHARTER.md. Every V row of the claim register that reports a latency is in one class:

  L-within      its comparisons are made within one run or one host; N >= 30 per reported statistic;
                host and library versions recorded in the row or in its result file
  L-absolute    no comparison, an absolute value; the same N and record rules
  L-descriptive fails one of the rules; the reason is stated and the register row says "descriptive only"
  L-derived     computed from other rows; inherits their classes

Rows are classified by hand here (ROWS). The check fails if:
  - a V row whose claim reports a latency has no class, or a class names a row that is not V;
  - an L-within or L-absolute row's result file does not exist or records no CPU.

    python3 docs/testing/latency_charter.py          # write LATENCY_CHARTER.md
    python3 docs/testing/latency_charter.py --check  # CI and tools/prepush_check.sh
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTER = ROOT / "docs/MEASUREMENT_CONDITIONS.md"
OUT = ROOT / "docs/testing/LATENCY_CHARTER.md"
LATENCY = re.compile(r"\bms\b|latency|µs")
CPU = re.compile(r'"(cpu|cpu_model)"\s*:\s*"[^"]+"')

CLASSES = {
    "L-within": "comparisons within one run or one host; N ≥ 30 per statistic; host and libraries recorded",
    "L-absolute": "an absolute value, no comparison; N ≥ 30; host and libraries recorded",
    "L-descriptive": "fails one rule (stated); quoted as descriptive only, never compared across hosts or runs",
    "L-derived": "computed from other rows; inherits their classes",
}

# row: (class, files that must record the host, N as stated, the reason)
ROWS = {
    21: ("L-within", ["cv2x-testbed/results/pki_vs_erc1056.json"], "n = 50 per operation",
         "PKI and ERC-1056 timed in the same run of one script"),
    26: ("L-descriptive", ["4_comparison-framework/results/scaling_verify.json"], "one sweep per density point",
         "the V2V slope and P* come from one sweep per point with no replicate spread; host recorded"),
    27: ("L-within", ["cv2x-testbed/sumo/results/v2v_latency_stats.json"], "30 seeded runs",
         "SSI and PKI verify in the same runs; bootstrap CI over run medians"),
    31: ("L-descriptive", ["1_blockchain-identity/results/metrics/latest/meta.json"], "scale reads: N = 10",
         "the h = 50 figure is from the harness's scale reads (2 warm-up + 10) and the harness's meta.json records no CPU"),
    32: ("L-within", ["cv2x-testbed/results/freshness_k.json"], "n = 250 per k",
         "the k comparison is within one run; absolute ms are host-dependent (#52)"),
    33: ("L-within", ["cv2x-testbed/results/lifecycle_parity.json"], "n = 50 per operation",
         "centralized and MOBI timed in the same run; ratios are upper bounds (in-process baseline)"),
    36: ("L-derived", [], "from #29–#35",
         "one of its six criteria is R3 median ms after the lifecycle, from the harness (#31 class: descriptive)"),
    37: ("L-within", ["cv2x-testbed/results/freshness_k_probe.json"], "n = 250 per k, 2 replicates",
         "the probe-versus-full comparison is within each replicate; the knee is host-dependent (#52)"),
    39: ("L-descriptive", ["1_blockchain-identity/results/metrics-rpc/latest/meta.json"], "N = 30",
         "comparisons are within one run and N = 30, but the harness's meta.json records no CPU"),
    44: ("L-within", ["cv2x-testbed/sumo/results/infrastructure_stats.json"], "30 runs",
         "SPaT and BSM verified in the same runs (per-run ratio); stated deviation: no warm-up discard (amendment A5)"),
    48: ("L-absolute", ["cv2x-testbed/sumo/results/infrastructure_stats.json"], "N = 30 runs",
         "an absolute sum of four medians, not a path latency; stated deviation: no warm-up discard"),
    52: ("L-within", ["cv2x-testbed/results/freshness_k_c3/c3_r1_k32_full.json"], "n = 250 per k, 2 replicates each",
         "the two codes compared on one host, back to back, under a rule committed first"),
    55: ("L-within", ["cv2x-testbed/results/freshness_k_samehost/r10_full.json"], "12 replicates",
         "both refresh modes on one host in alternating blocks; the summary file records no CPU, each of the 12 replicate files does"),
    57: ("L-descriptive", ["5_zkp-agent-identity/results/zkvin_bench.json"], "prove N = 10; verify N = 30",
         "the proving time has N = 10; the verify time alone (N = 30) would be L-absolute"),
}


def v_rows():
    out = {}
    for line in REGISTER.read_text().splitlines():
        m = re.match(r"^\| (\d+) \|", line)
        if not m:
            continue
        cells = [c.strip() for c in line.split(" | ")]
        status = re.search(r"\*\*([VSEUB])", " ".join(cells[5:]))
        out[int(m.group(1))] = (status.group(1) if status else "?", cells[1])
    return out


def build():
    rows = v_rows()
    problems = []
    lat = sorted(n for n, (st, claim) in rows.items() if st == "V" and LATENCY.search(claim))
    for n in lat:
        if n not in ROWS:
            problems.append(f"register row #{n} is V and reports a latency but has no class in latency_charter.py ROWS")
    for n, (cls, files, _N, _why) in ROWS.items():
        if rows.get(n, ("?",))[0] != "V":
            problems.append(f"ROWS classifies #{n}, which is not a V row")
        if cls in ("L-within", "L-absolute"):
            for f in files:
                p = ROOT / f
                if not p.exists():
                    problems.append(f"#{n}: result file {f} does not exist")
                elif not CPU.search(p.read_text(errors="replace")):
                    problems.append(f"#{n}: {f} records no CPU, so the row cannot be {cls}")
    L = ["# Latency Charter (Class L)", "",
         "**Generated** by `docs/testing/latency_charter.py`; do not edit. **Author:** Nikhil Prakash (MASc, UBC ECE). "
         "**Written:** 2026-10-23 (WM-2 step B3, after-action report 35; guide rule 1.1.7).", "",
         "## 1. The rule",
         "A latency figure is compared only within one run or one host, carries N ≥ 30 per reported statistic, and "
         "names its host and library versions (in the register row or in the result file it cites). A row that "
         "fails a rule is quoted as **descriptive only**: its value may be reported, never compared with a value "
         "from another run or host.", "",
         "| Class | Meaning |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in CLASSES.items()]
    L += ["", "## 2. The register's latency rows (status V)", "",
          "| Row | Class | N | Host recorded in | Why |", "|---|---|---|---|---|"]
    for n in sorted(ROWS):
        cls, files, N, why = ROWS[n]
        L.append(f"| #{n} | {cls} | {N} | {', '.join(f'`{f}`' for f in files) or '—'} | {why} |")
    counts = {c: sum(1 for v in ROWS.values() if v[0] == c) for c in CLASSES}
    L += ["", f"{len(ROWS)} rows classified: " + ", ".join(f"{k} {v}" for k, v in counts.items()) +
          f". Every V row whose claim reports a latency ({len(lat)}) has a class; every L-within and L-absolute "
          "row's result file records its CPU (checked).", "",
          "## 3. What follows",
          "- **The harness records no host.** The metrics harness's `meta.json` names Node and the compiler but not the "
          "CPU, so its latency figures (#31, #39) are descriptive only. Its gas figures are unaffected (gas does not "
          "depend on the host). Recording the CPU in `meta.json` at the next harness run of record would move both "
          "rows to L-within (deferred item N-26).",
          "- **Two deviations are stated, not hidden.** The infrastructure rows (#44, #48) discard no warm-up run, a "
          "deviation recorded in the pre-registration's amendment A5.",
          "- **Short runs.** The ZK proving time (#57, N = 10) and the V2V scaling slope (#26, one sweep per point) are "
          "descriptive; their verify and gas parts are not affected."]
    return "\n".join(L) + "\n", problems


def main():
    text, problems = build()
    for p in problems:
        print("PROBLEM:", p)
    if "--check" in sys.argv:
        stale = not OUT.exists() or OUT.read_text() != text
        if stale:
            print("STALE: run python3 docs/testing/latency_charter.py")
        if not (stale or problems):
            print("latency charter current; every V latency row classed; conforming rows record their host")
        return 1 if (stale or problems) else 0
    OUT.write_text(text)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
