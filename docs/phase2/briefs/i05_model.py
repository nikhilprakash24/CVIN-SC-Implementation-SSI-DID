#!/usr/bin/env python3
"""I-05's freshness model as code (unblocked item U8; after-action report 37).

PHASE 2 PREDICTION, NOT A RESULT (Phase 2 principle 4). It computes the brief's predictions P0 to P3
(docs/phase2/briefs/I-05_FRESHNESS.md, section 7) from the V-row inputs the brief cites, so the prediction is fixed
and reproducible before any measurement. Nothing here is measured.

    k_min = ceil(t_chain / (B - t_local)),  B = 0.5 ms         (the knee; brief section 6)
    sensitivity = t_local / (B - t_local)                      (condition number of k_min in t_local)

Intervals take the favourable ends together (smallest t_chain with smallest t_local) and the unfavourable ends
together, as the brief does. Exact decimal arithmetic, so a ceil never turns on float error.

    python3 docs/phase2/briefs/i05_model.py          # print the predictions
    python3 docs/phase2/briefs/i05_model.py --check  # fail if the brief's table no longer matches the model
"""
import math
import pathlib
import re
import sys
from decimal import Decimal as D

BRIEF = pathlib.Path(__file__).with_name("I-05_FRESHNESS.md")
B = D("0.5")

# Inputs, in ms, with the register row each comes from
T_LOCAL_H3 = (D("0.326"), D("0.339"))      # #52, host 3
T_CHAIN_FULL_H3 = (D("6.94"), D("8.15"))   # #52, full refresh, pre-D51 code
T_CHAIN_PROBE_H3 = (D("2.03"), D("2.20"))  # #52, probe refresh (one eth_call)
T_LOCAL_H1 = D("0.428")                    # #32, host 1
T_LOCAL_H2 = D("0.49")                     # #37, host 2 (lower end; the knee is ill-conditioned there)


def k_min(t_chain, t_local):
    if t_local >= B:
        return None  # no message-bounded policy is feasible
    return math.ceil(t_chain / (B - t_local))


def interval(chain, local=T_LOCAL_H3, extra=(D(0), D(0))):
    return (k_min(chain[0] + extra[0], local[0]), k_min(chain[1] + extra[1], local[1]))


def predictions():
    return {
        "P0": interval(T_CHAIN_FULL_H3),
        "P1": interval(T_CHAIN_PROBE_H3),
        # P2: the D51 fix adds one RPC, assumed equal to the probe's one eth_call
        "P2": interval(T_CHAIN_FULL_H3, extra=T_CHAIN_PROBE_H3),
        "P3": [round(float(t / (B - t)), 2) for t in (*T_LOCAL_H3, T_LOCAL_H1, T_LOCAL_H2)],
    }


def check(p):
    text = BRIEF.read_text()
    problems = []
    for name in ("P0", "P1", "P2"):
        lo, hi = p[name]
        row = next((l for l in text.splitlines() if re.match(rf"^\| \**{name}\b", l)), "")
        if f"k = {lo} to {hi}" not in row:
            problems.append(f"{name}: model gives k = {lo} to {hi}; the brief's row says: {row[:160]}")
    s = p["P3"]
    for shown, val in [("1.9", s[0]), ("2.1", s[1]), ("5.9", s[2]), ("49", s[3])]:
        if round(val, 0 if shown == "49" else 1) != float(shown):
            problems.append(f"P3: model gives {val}, the brief shows ≈ {shown}")
    return problems


def main():
    p = predictions()
    print("PHASE 2 PREDICTION (not a result):")
    for k in ("P0", "P1", "P2"):
        print(f"  {k}: k = {p[k][0]} to {p[k][1]}")
    print(f"  P3: sensitivity host 3 {p['P3'][0]}–{p['P3'][1]}, host 1 {p['P3'][2]}, host 2 {p['P3'][3]}")
    if "--check" in sys.argv:
        problems = check(p)
        for x in problems:
            print("PROBLEM:", x)
        print("i05 model reproduces the brief's P0 to P3" if not problems else "i05 model and brief disagree")
        return 1 if problems else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
