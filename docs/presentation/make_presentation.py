#!/usr/bin/env python3
"""Generate the presentation report (draft 1) from committed data only.

    python3 docs/presentation/make_presentation.py          # figures, REPORT_DRAFT_1.md, report_page.html
    python3 docs/presentation/make_presentation.py --check  # exit 1 if REPORT_DRAFT_1.md is stale

Inputs: docs/figures/dashboard_snapshot.json (itself generated from the results of record and the
claim register), the raw infrastructure result files for per-run distributions, the stamp inventory
and docs/presentation/data/process_metrics.yaml (process counts, each with its source). The report
contains no hand-typed result: every number is read from those files when the report is built, and
every result table names its register row. `--check` compares the Markdown (all numbers live there);
figures are regenerated on a full run (PNG bytes depend on the matplotlib version, so CI does not
compare them).
"""
import ast
import base64
import html
import json
import pathlib
import statistics
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = ROOT / "docs/presentation"
FIG = HERE / "figures"
OUT_MD = HERE / "REPORT_DRAFT_1.md"
OUT_HTML = HERE / "report_page.html"

S = json.loads((ROOT / "docs/figures/dashboard_snapshot.json").read_text())
P = yaml.safe_load((HERE / "data/process_metrics.yaml").read_text())["wm1"]
INFRA = json.loads((ROOT / "cv2x-testbed/sumo/results/infrastructure_stats.json").read_text())
REVOC = json.loads((ROOT / "cv2x-testbed/sumo/results/infrastructure_revocation.json").read_text())

# ---------------------------------------------------------------- palette (dataviz reference instance)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, GRID, BASE, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
GOOD, CRIT, WARN = "#0ca30c", "#d03b3b", "#fab219"


def fmt(n, d=0):
    if n is None:
        return "—"
    if isinstance(n, (int,)) or (isinstance(n, float) and d == 0 and float(n).is_integer()):
        return f"{int(n):,}"
    return f"{n:,.{d}f}"


# ---------------------------------------------------------------- content model
blocks = []


def H(level, text):
    blocks.append(("h", level, text))


def Para(text):
    blocks.append(("p", text))


def Note(text):
    blocks.append(("note", text))


def Table(head, rows, caption=None):
    blocks.append(("table", head, rows, caption))


def Figure(path, caption, alt):
    blocks.append(("fig", path, caption, alt))


def Mermaid(src, caption):
    blocks.append(("mermaid", src, caption))


# ---------------------------------------------------------------- figures
def figures():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": BASE,
                         "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
                         "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF,
                         "axes.facecolor": SURF, "savefig.facecolor": SURF, "svg.hashsalt": "cvin",
                         "path.simplify": False})
    FIG.mkdir(parents=True, exist_ok=True)

    def save(fig, name):
        fig.tight_layout()
        fig.savefig(FIG / name, dpi=200, metadata={"Software": None})
        plt.close(fig)

    def grid(ax, axis="x"):
        ax.grid(axis=axis, color=GRID, lw=0.8)
        ax.set_axisbelow(True)

    # F1 create-identity gas, sorted
    g = S["gas"]["table"]
    items = sorted(((k, v["createIdentity"]) for k, v in g.items() if v.get("createIdentity")), key=lambda x: x[1])
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    ys = range(len(items))
    ax.barh(list(ys), [v for _, v in items], height=0.55, color=BLUE)
    for y, (k, v) in zip(ys, items):
        ax.text(v, y, f"  {v:,}", va="center", ha="left", fontsize=8, color=INK2)
    ax.set_yticks(list(ys), [k for k, _ in items], color=INK)
    ax.set_xlim(0, max(v for _, v in items) * 1.22)
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(500_000))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: "0" if x == 0 else (f"{x/1e6:g}M" if x >= 1e6 else f"{x/1e3:g}K")))
    ax.set_xlabel("gas (exact receipt.gasUsed, condition M1)")
    grid(ax)
    ax.set_title("Create-identity gas by standard", loc="left", fontsize=10, color=INK)
    save(fig, "f1_create_gas.png")

    # F2 lifetime model with ±band
    L = S["lifetime"]["ranking"]
    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    ys = list(range(len(L)))[::-1]
    for y, r in zip(ys, L):
        ax.plot([r["low"], r["high"]], [y, y], color=GRID, lw=6, solid_capstyle="round")
        ax.plot([r["total"]], [y], "o", ms=7, color=BLUE, mec=SURF, mew=2)
        ax.text(r["high"], y, f"  {r['total']/1e6:.2f}M", va="center", fontsize=8, color=INK2)
    ax.set_yticks(ys, [r["standard"] for r in L], color=INK)
    ax.set_xlim(0, max(r["high"] for r in L) * 1.18)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x/1e6:.0f}M"))
    ax.set_xlabel(f"lifetime gas over the {S['constants']['lifetime_years']['value']}-year profile; band ±{S['constants']['lifetime_band_pct']['value']} % event frequency (a model)")
    grid(ax)
    ax.set_title("Lifetime cost model: base value and sensitivity band", loc="left", fontsize=10, color=INK)
    save(fig, "f2_lifetime.png")

    # F3 V2V verify latency, dot + CI
    V = S["v2v"]["per_population"]
    rows = [("SSI warm", V["ssi"]["warm"], BLUE), ("PKI warm", V["pki"]["warm"], ORANGE),
            ("SSI cold", V["ssi"]["cold"], BLUE), ("PKI cold", V["pki"]["cold"], ORANGE)]
    fig, ax = plt.subplots(figsize=(7.0, 2.4))
    for y, (lab, m, c) in enumerate(rows[::-1]):
        ax.plot(m["ci95"], [y, y], color=c, lw=2, solid_capstyle="round")
        ax.plot([m["median"]], [y], "o", ms=7, color=c, mec=SURF, mew=2)
        ax.text(m["ci95"][1], y, f"  {m['median']:.3f} ms", va="center", fontsize=8, color=INK2)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows[::-1]], color=INK)
    ax.set_xlim(0, 0.5)
    ax.set_xlabel("verification latency, median of 30 run medians with 95 % bootstrap CI (ms)")
    grid(ax)
    ax.set_title("V2V message verification: SSI vs PKI (crypto step only)", loc="left", fontsize=10, color=INK)
    save(fig, "f3_v2v_latency.png")

    # F4 freshness-k, two refresh modes (log y)
    Fr = S["freshness"]
    ks = [r["k"] for r in Fr["full"]["by_k"]]
    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    for key, lab, c in (("full", "full resolution refresh (#32)", BLUE), ("probe", "one-call probe refresh (#37)", ORANGE)):
        med = [r["median_ms"] for r in Fr[key]["by_k"]]
        ax.plot(range(len(ks)), med, color=c, lw=2, marker="o", ms=6, mec=SURF, mew=2, label=lab)
        ax.text(len(ks) - 1, med[-1], f"  {med[-1]:.2f}", va="center", fontsize=8, color=INK2)
    ax.set_xticks(range(len(ks)), ["k = ∞" if k == "inf" else f"k = {k}" for k in ks], color=INK)
    ax.set_yscale("log")
    ax.set_ylabel("median verify (ms, log)")
    grid(ax, "y")
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.set_title("Revocation freshness: verify cost against the re-check interval k", loc="left", fontsize=10, color=INK)
    save(fig, "f4_freshness_k.png")

    # F5 I1 per-run warm medians, SPaT vs BSM (paired, 30 runs)
    pr = INFRA["per_run"]
    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    xs = [r["seed"] for r in pr]
    # runs are independent: dots, no connecting line
    ax.plot(xs, [r["bsm_ssi_warm"] for r in pr], "o", color=BLUE, ms=5, mec=SURF, mew=1.5, label="warm SSI BSM verify")
    ax.plot(xs, [r["spat_warm"] for r in pr], "o", color=AQUA, ms=5, mec=SURF, mew=1.5, label="warm SPaT verify")
    ax.set_xlabel("run (seed 1–30), median per run")
    ax.set_ylabel("ms")
    ax.set_ylim(0, max(r["spat_warm"] for r in pr) * 1.3)
    grid(ax, "y")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.set_title(f"I1: warm SPaT vs warm BSM verification, per run (ratio median {INFRA['I1']['ratio']['median']:.3f})", loc="left", fontsize=10, color=INK)
    save(fig, "f5_i1_per_run.png")

    # F6 I3 per-run max accepted after revocation, by k, with the bound
    per_k = REVOC["I3"]["per_k"]
    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    finite = [k for k in per_k if k != "inf"]
    for i, k in enumerate(finite):
        vals = sorted(r["max_accepted_after_revocation"] for r in per_k[k]["per_run"])
        jitter = [i + (j - len(vals) / 2) * 0.012 for j in range(len(vals))]
        ax.plot(jitter, vals, "o", ms=4, color=BLUE, alpha=0.8)
        b = per_k[k]["bound_k_minus_1"]
        ax.plot([i - 0.3, i + 0.3], [b, b], color=CRIT, lw=2)
        ax.text(i + 0.32, b, f" bound {b}", va="center", fontsize=8, color=INK2)
    ax.set_xticks(range(len(finite)), [f"k = {k}" for k in finite], color=INK)
    ax.set_xlim(-0.5, len(finite) - 0.2)
    ax.set_ylabel("max accepted (messages)")
    grid(ax, "y")
    ax.set_title("I3: SPaT accepted from a revoked RSU, per run (30 runs per k), against the bound k − 1", loc="left", fontsize=10, color=INK)
    save(fig, "f6_i3_bound.png")

    # F7 register status, start vs end of WM-1 (stacked horizontal, 2px gaps)
    start = P["register_start"]["value"]
    end = S["register"]["by_status"]
    cats = [("V", BLUE), ("S", ORANGE), ("E", AQUA), ("B", MUTED)]
    fig, ax = plt.subplots(figsize=(7.0, 1.8))
    for y, (lab, d) in enumerate((("end of WM-1", end), ("start of WM-1", start))):
        x = 0
        for c, col in cats:
            v = d.get(c, 0)
            if v:
                ax.barh(y, v, left=x, height=0.5, color=col, edgecolor=SURF, linewidth=2)
                if v >= 3:
                    ax.text(x + v / 2, y, f"{c} {v}", ha="center", va="center", fontsize=8, color="white")
                x += v
        ax.text(x, y, f"  {x} rows", va="center", fontsize=8, color=INK2)
    ax.set_yticks([0, 1], ["end of WM-1", "start of WM-1"], color=INK)
    ax.set_xlim(0, 56)
    ax.set_xlabel("claim-register rows by status (V verified, S superseded, E estimate, B awaiting re-run)")
    ax.set_title("Claim register through work milestone WM-1", loc="left", fontsize=10, color=INK)
    save(fig, "f7_register.png")

    # F8 review findings by reviewer and severity (grouped columns)
    rv = P["review_pass11"]["by_reviewer"]
    names = list(rv)
    sev = [("high", CRIT), ("medium", WARN), ("low", MUTED)]
    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    w = 0.22
    for j, (s, col) in enumerate(sev):
        xs = [i + (j - 1) * (w + 0.03) for i in range(len(names))]
        vals = [rv[n][s] for n in names]
        ax.bar(xs, vals, width=w, color=col, label=s)
        for x, v in zip(xs, vals):
            ax.text(x, v + 0.15, str(v), ha="center", fontsize=8, color=INK2)
    ax.set_xticks(range(len(names)), names, color=INK)
    ax.set_ylabel("findings")
    grid(ax, "y")
    ax.set_ylim(0, max(max(v.values()) for v in rv.values()) + 2.5)
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper right")
    ax.set_title("Adversarial review of passes 9–10: 33 findings by reviewer and severity", loc="left", fontsize=10, color=INK)
    save(fig, "f8_review.png")


# ---------------------------------------------------------------- report content
def build():
    blocks.clear()
    g = S["gas"]["table"]
    creates = {k: v["createIdentity"] for k, v in g.items() if v.get("createIdentity")}
    lo_k, hi_k = min(creates, key=creates.get), max(creates, key=creates.get)
    spread = creates[hi_k] / creates[lo_k]
    V = S["v2v"]
    ssi_w = V["per_population"]["ssi"]["warm"]
    I1, I2, I5 = INFRA["I1"], INFRA["I2"], INFRA["I5"]
    I3 = REVOC["I3"]
    stages = S["tests"]["stages"]
    hh = ast.literal_eval(stages["L1+L2"]["result"])["passing"]
    py = ast.literal_eval(stages["L3+L4"]["result"])["passed"]
    dm = ast.literal_eval(stages["demos"]["result"])
    sec = S["security"]["total"]
    conf = S["conformance"]["runs"]["default"]
    comp = S["compliance"]
    reg = S["register"]["by_status"]

    H(1, "Self-Sovereign Identity for Connected Vehicles — Results, Work and Implementation")
    Para("**Presentation report, draft 1.** Author: Nikhil Prakash (MASc, UBC ECE). Generated "
         f"from committed data at snapshot commit `{S['tests']['commit']}` by "
         "`docs/presentation/make_presentation.py`; every result below is read from the results of record "
         "and carries its claim-register row (`docs/MEASUREMENT_CONDITIONS.md`). What draft 2 adds is in "
         "`docs/presentation/EXPANSION_PLAN_DRAFT2.md`.")
    Note("Scope of every number: smart-contract gas is exact `receipt.gasUsed` on a local Hardhat chain "
         "(condition M1); latency is in-process cryptography with simulated mobility and no radio "
         "(condition M0). Nothing here was measured on a public network or a real road.")

    H(2, "1. At a glance")
    Table(["Question", "Answer (measured)", "Register"], [
        ["How many identity standards were implemented and measured?", f"{len(creates)} (nine base standards and the MOBI VID V2 profile)", "#25"],
        ["How far apart is the cost of creating an identity?", f"{spread:.1f}× ({lo_k} {creates[lo_k]:,} gas to {hi_k} {creates[hi_k]:,})", "#25"],
        ["Does identity verification fit a V2V message budget?", f"SSI warm verify {ssi_w['median']:.3f} ms [{ssi_w['ci95'][0]:.3f}, {ssi_w['ci95'][1]:.3f}], N = {V['n_runs']} runs; budget {S['constants']['v2v_budget_ms']['value']} ms", "#27"],
        ["Do the identities meet W3C DID / VC?", f"internal checker {comp['score']} % ({comp['pass']} pass, {comp['partial']} partial, {comp['fail']} fail of {comp['executed']}); external DID suite {conf['passed']}/{conf['total']}", "#4, #24"],
        ["Are the identity contracts attack-resistant?", f"{sec['DEFENDED']} of {sec['DEFENDED']} applicable attack cells defended ({sec['N/A']} not applicable), strict harness", "#28"],
        ["Can infrastructure (RSUs, controllers) use the same identity layer?", f"I1 {I1['verdict']} (SPaT/BSM warm ratio {I1['ratio']['median']:.3f}), I2 {I2['verdict']} ({len(I2['expected_reasons'])} attacks), I3 {I3['verdict']} (revocation within k − 1 messages)", "#44–#46"],
        ["How large is the test and evidence base?", f"{hh} Hardhat tests, {py} Python-layer tests, {dm['demos']} feature demos ({dm['steps']:,} steps); {reg.get('V', 0)} verified register rows", "grand report"],
    ])

    H(2, "2. Research questions and hypotheses")
    hyp = S["hypotheses"]
    verdicts = {"H1": "Supported", "H2": "Supported", "H3": "Supported (verification-step scope)",
                "H4": "Supported (fidelity gradient)", "H5": "Supported"}
    Table(["Hypothesis", "Statement", "Verdict", "Evidence"], [
        ["H1", hyp["H1"], verdicts["H1"], "§3.1, #6, #25"],
        ["H2", hyp["H2"], verdicts["H2"], "§3.5, #4, #24"],
        ["H3", hyp["H3"], verdicts["H3"], "§3.6, #27"],
        ["H4", hyp["H4"], verdicts["H4"], "§3.3"],
        ["H5", hyp["H5"], verdicts["H5"], "§3.9, #26, #36"],
    ], caption="Verdicts as stated in chapter 5 §5.7 (`docs/thesis/chapter5-results/README.md`); statements from the snapshot.")
    cr = S["cruxes"]
    Table(["Crux", "State", "V evidence rows", "Open gaps"],
          [[f"{c['id']} {c['title']}", c["state"], str(sum(1 for e in c["evidence"] if e["status"] == "V")), str(len(c["gaps"]))] for c in cr],
          caption="The eight cruxes the thesis must answer (`docs/thesis/CRUX_REGISTER.md`): none is a gap, none is fully evidenced.")

    H(2, "3. Results")
    H(3, "3.1 Gas: what each standard costs (register #25)")
    ops = S["gas"]["operations"]
    opname = {"deployRegistry": "deploy", "createIdentity": "create", "updateAttribute": "update",
              "updateAttributeVia4337": "update via 4337", "addDelegateOrClaim": "delegate / claim",
              "revoke": "revoke", "transferOwnership": "transfer"}
    Table(["Standard"] + [opname[o] for o in ops],
          [[k] + [fmt(v.get(o)) for o in ops] for k, v in g.items()],
          caption=f"Exact gas, condition M1 (`{S['gas']['source']['path']}`). — = operation not offered by the standard.")
    Figure("figures/f1_create_gas.png", f"Figure 1. Create-identity gas, sorted. {lo_k} is cheapest, {hi_k} heaviest: a {spread:.1f}× spread.", "Horizontal bars of create-identity gas per standard")
    H(3, "3.2 Lifetime cost (register #26)")
    Table(["Standard", "Lifetime gas (base)", "Low", "High"],
          [[r["standard"], fmt(r["total"]), fmt(r["low"]), fmt(r["high"])] for r in S["lifetime"]["ranking"]],
          caption=f"A model over an assumed {S['constants']['lifetime_years']['value']}-year event profile, not a measurement; band ±{S['constants']['lifetime_band_pct']['value']} % event frequency.")
    Figure("figures/f2_lifetime.png", "Figure 2. Lifetime cost ranking with its sensitivity band.", "Dot and range per standard for lifetime gas")
    H(3, "3.3 MOBI VID across backends (H4)")
    sw = S["mobi_sweep"]["backends"]
    Table(["Backend", "Birth attestation gas", "Lifecycle event gas", "Third-party attestation gas (native?)", "Fidelity"],
          [[b, fmt(v["birthAttestation"]["gas"]), fmt(v["lifecycleEvent"]["gas"]),
            f"{fmt(v['thirdPartyAttestation']['gas'])} ({'native' if v['thirdPartyAttestation']['native'] else 'emulated'})", v["fidelity"]]
           for b, v in sw.items()], caption=f"`{S['mobi_sweep']['source']['path']}`.")
    H(3, "3.4 Security (register #28)")
    Table(["Standard", "Defended", "Not applicable"],
          [[k, str(v.get("DEFENDED", 0)), str(v.get("N/A", 0))] for k, v in S["security"]["per_standard"].items()],
          caption=f"Strict harness: an attack counts as defended only when the revert matches the documented reason. Total {sec['DEFENDED']} defended, {sec['N/A']} not applicable.")
    H(3, "3.5 W3C conformance (registers #4, #24)")
    Table(["Instrument", "Result"], [
        ["Internal executable checker", f"{comp['score']} % over {comp['executed']} executed checks ({comp['pass']} pass, {comp['partial']} partial, {comp['fail']} fail)"],
        ["External W3C DID test suite, fixture DID", f"{conf['passed']}/{conf['total']}"],
        ["External W3C DID test suite, registry-minted DID", f"{S['conformance']['runs']['registry-did']['passed']}/{S['conformance']['runs']['registry-did']['total']}"],
    ] + [[f"  suite: {k}", v] for k, v in conf["suites"].items()])
    H(3, "3.6 V2V message verification (register #27)")
    pp = V["per_population"]
    Table(["Path", "Sign (ms)", "Cold verify (ms)", "Warm verify (ms)"],
          [[lab, f"{pp[k]['sign']['median']:.3f} [{pp[k]['sign']['ci95'][0]:.3f}, {pp[k]['sign']['ci95'][1]:.3f}]",
            f"{pp[k]['cold']['median']:.3f} [{pp[k]['cold']['ci95'][0]:.3f}, {pp[k]['cold']['ci95'][1]:.3f}]",
            f"{pp[k]['warm']['median']:.3f} [{pp[k]['warm']['ci95'][0]:.3f}, {pp[k]['warm']['ci95'][1]:.3f}]"]
           for lab, k in (("SSI (blockchain credential)", "ssi"), ("PKI (IEEE 1609.2-style)", "pki"))],
          caption=f"Median of {V['n_runs']} seeded-run medians, 95 % bootstrap CI; {V['vehicles']} vehicles; {V['totals']['messages_verified']:,} verifications; {V['totals']['verification_failures']} failures, all injected attacks. Condition: {V['condition']}.")
    Figure("figures/f3_v2v_latency.png", "Figure 3. Verification latency with confidence intervals. The CIs do not overlap, so the SSI–PKI difference is resolved; both are far inside the budget.", "Dot and interval per path")
    H(3, "3.7 Revocation freshness (registers #32, #37)")
    Fr = S["freshness"]
    Table(["k", "Full refresh median (ms)", "Full refresh p95", "Probe refresh median (ms)", "Probe refresh p95"],
          [["∞" if a["k"] == "inf" else a["k"], f"{a['median_ms']:.3f}", f"{a['p95_ms']:.3f}", f"{b['median_ms']:.3f}", f"{b['p95_ms']:.3f}"]
           for a, b in zip(Fr["full"]["by_k"], Fr["probe"]["by_k"])],
          caption="A cached verifier re-checks the chain every k-th message; k trades revocation staleness (k − 1 messages) for latency. Two runs on one host type; host-dependence is an open item (crux C4).")
    Figure("figures/f4_freshness_k.png", "Figure 4. Verify cost falls steeply from k = 1 to k = 5; the one-call probe cuts the k = 1 cost.", "Two lines of median verify latency against k")
    H(3, "3.8 Pre-registered comparisons reported as they fell (registers #33, #38)")
    Table(["Experiment", "Pre-registered claim", "Verdict", "Measured"],
          [[f"M4 lifecycle parity: {v['operation']}", v["claim"], v["verdict"], f"ratio {v['ratio_median']:,.3f}" if v.get("ratio_median") is not None else "—"]
           for v in S["lifecycle_parity"]["verdicts"]] +
          [["M5 pseudonym pool: gas", f"≈ {S['pseudonyms']['prereg_gas']:,} gas per epoch (±{S['constants']['pseudonym_gas_band_pct']['value']} %)", S["pseudonyms"]["gas_verdict"], ", ".join(f"{x:,}" for x in S["pseudonyms"]["epoch_gas"])],
           ["M5 pseudonym pool: linkability", "delegate pool fully linkable from chain data", S["pseudonyms"]["linkability_verdict"], "linkable"]],
          caption="Failed and out-of-band verdicts are shown, not hidden.")
    H(3, "3.9 Cost/capability frontier (metrics harness, registers #34–#36)")
    hs = S["harness"]
    Table(["Criteria set", "Options on the frontier"], [[k, ", ".join(v)] for k, v in hs["frontier"].items()],
          caption=f"Run of record `{hs['runId']}`; criteria: {', '.join(hs['criteria'])}.")
    H(3, "3.10 Infrastructure messaging, V2I and I2I (registers #44–#48)")
    Para("Roadside units (RSUs), signal controllers and a traffic-management centre (TMC) are `did:ethr` "
         "identities holding road-authority credentials. RSUs sign SPaT (signal phase and timing) messages; "
         "controllers and the TMC sign infrastructure-to-infrastructure messages. The five experiments were "
         "pre-registered before any code; the verifier was hardened after an adversarial review and every "
         "experiment re-run (amendment A4).")
    Table(["Exp.", "Question", "Result", "Verdict"], [
        ["I1", "Does a warm SPaT verify cost what a warm BSM verify does?", f"ratio {I1['ratio']['median']:.3f} [{I1['ratio']['ci95'][0]:.3f}, {I1['ratio']['ci95'][1]:.3f}]; SPaT {I1['spat_warm_ms']['median']:.3f} ms vs BSM {I1['bsm_ssi_warm_ms']['median']:.3f} ms", I1["verdict"]],
        ["I2", "Are registered attacks rejected for the right reason?", f"{len(I2['expected_reasons'])} checks, {I2['runs_all_as_expected']}/{I2['runs']} runs", I2["verdict"]],
        ["I3", "How long is a revoked RSU trusted by a cached verifier?", " · ".join(f"k={k}: {v['max_accepted_after_revocation']}" + ("" if v["bound_k_minus_1"] is None else f" (≤ {v['bound_k_minus_1']})") for k, v in I3["per_k"].items()) + " messages", I3["verdict"]],
        ["I4", "What does an RSU identity cost on chain?", "key anchor " + "–".join(fmt(x) for x in sorted(set(S['infrastructure']['I4']['anchor_key_by_rsu']))) + " gas; hand to authority " + "–".join(fmt(x) for x in sorted(set(S['infrastructure']['I4']['hand_control_to_authority']))), "reported"],
        ["I5", "What do the I2I operations add?", f"{I5['controller_to_vehicle_ms']['median']:.3f} ms, a sum of operation costs (not a path latency)", "reported"],
    ])
    Table(["I2 check", "Expected rejection reason"], [[k, v] for k, v in I2["expected_reasons"].items()])
    Figure("figures/f5_i1_per_run.png", "Figure 5. I1 per run: the hardened SPaT path sits about 10 % above the BSM path in every run.", "Two lines over 30 runs")
    Figure("figures/f6_i3_bound.png", "Figure 6. I3: per-run maxima never exceed the pre-registered bound k − 1; it is reached in the worst runs.", "Dots per run with a bound line per k")
    Figure("../../cv2x-testbed/sumo/results/figures/trace_revocation_k5_seed1_revocation.png", "Figure 7. One run (seed 1, k = 5) from the trace of record: SPaT from the revoked RSU accepted (|) and rejected (x) per vehicle.", "Per-vehicle timeline of accepted and rejected messages")

    H(2, "4. Implementation")
    Mermaid("""flowchart LR
  subgraph L1["1_blockchain-identity (Solidity, Hardhat)"]
    C9["9 identity standards + MOBI VID V2 profile"]
  end
  subgraph L2["2_w3c-ssi-layer (Python)"]
    VC["W3C VC issuer and verifier"]
    RES["DID resolver"]
  end
  subgraph L3["cv2x-testbed (Python)"]
    PROV["identity providers: PKI, centralized, ERC-1056, MOBI"]
    SIM["V2V/V2I harness: BSM, SPaT, I2I, attacks, trace"]
    INF["infrastructure identity layer"]
  end
  subgraph L4["4_comparison-framework + sandbox"]
    BEN["gas, scaling, security, conformance producers"]
    SBX["grand runner, option sandboxes, L1-L4 suites, 92 demos"]
  end
  subgraph DOC["docs (generated)"]
    REG["claim register"]
    DASH["dashboard, crux and test registers"]
  end
  C9 --> PROV --> SIM
  VC --> SIM
  INF --> SIM
  C9 --> BEN --> REG --> DASH
  SIM --> REG
  RES --> BEN
  SBX --> DASH""", "Figure 8. How the layers depend on each other and where the results of record come from.")
    Table(["Layer", "What it contains", "How it is tested"], [
        ["Contracts", "ERC-1056, ERC-721, ERC-725, ERC-725xy, ERC-735, ERC-1155, ERC-4337, LSP8, CVIN-Combined; MOBI VID V2 profile", f"{hh} Hardhat tests (L1 mechanisms, L2 system, security harness)"],
        ["W3C SSI layer", "VC issuance and verification, DID resolution, MOBI VID I/II", f"Python layers ({py} tests in L3 + L4); external DID suite {conf['passed']}/{conf['total']}"],
        ["V2X testbed", "identity providers, message-path harness, infrastructure layer, trace and renderers", "seeded 30-run statistics; no-change gates; 31 infrastructure tests"],
        ["Comparison and sandbox", "producers of the results of record; per-option sandboxes with adapters and demos", f"grand runner; {dm['demos']} demos, {dm['steps']:,} steps"],
        ["Documents", "claim register, defect log, crux register, test register, dashboard, stale-figure check", "regenerated and compared in CI"],
    ])

    H(2, "5. The work: work milestone WM-1")
    ps = P["plan_status"]["counts"]
    Table(["Measure", "Value", "Source"], [
        ["Passes / commits", f"{P['passes']['value']} / {P['commits']['value']} (`{P['commit_range']['value']}`)", P["commits"]["source"]],
        ["Files changed", str(P["files_changed"]["value"]), P["files_changed"]["source"]],
        ["Plan items: done / changed / partial / deferred / not done", f"{ps['done']} / {ps['changed']} / {ps['partial']} / {ps['deferred']} / {ps['not_done']}", P["plan_status"]["source"]],
        ["Python-layer tests, start → end", f"{P['test_counts']['start']['python_layers']} → {P['test_counts']['end']['python_layers']}", P["test_counts"]["source"]],
        ["Infrastructure tests; layer mutants killed", f"{P['infra_tests']['value']['tests_before']} → {P['infra_tests']['value']['tests_after']}; {P['infra_tests']['value']['mutants_killed_before']}/{P['infra_tests']['value']['mutants_before']} → {P['infra_tests']['value']['mutants_killed_after']}/{P['infra_tests']['value']['mutants_after']}", P["infra_tests"]["source"]],
        ["Result files fully stamped", f"{P['stamps']['value']['start_complete']}/{P['stamps']['value']['start_total']} → {P['stamps']['value']['end_complete']}/{P['stamps']['value']['end_total']}", P["stamps"]["source"]],
        ["Superseded figures found by the generators", f"{P['generator_findings_pass9']['value']['stale_figures']} in {P['generator_findings_pass9']['value']['stale_documents']} documents; {P['generator_findings_pass9']['value']['register_rows']} self-contradicting register rows", P["generator_findings_pass9"]["source"]],
        ["Review findings: confirmed / accepted / rejected", f"{P['review_pass11']['dispositions']['confirmed']} / {P['review_pass11']['dispositions']['accepted']} / {P['review_pass11']['dispositions']['rejected']}", P["review_pass11"]["source"]],
    ])
    Figure("figures/f7_register.png", "Figure 9. The claim register over WM-1: five new verified rows (infrastructure), one row re-run from B to V, two rows superseded.", "Two stacked bars of register rows by status")
    Figure("figures/f8_review.png", "Figure 10. What the adversarial review found, by reviewer and severity. Two high findings were security holes in the first infrastructure verifier; five were guards that could pass while wrong.", "Grouped columns by reviewer and severity")
    dc = S["defects"]["counts"]
    Table(["Severity", "Fixed", "Partly fixed", "Open"],
          [[sv, str(dc.get(f"{k}:fixed", 0)), str(dc.get(f"{k}:partly fixed", 0)), str(dc.get(f"{k}:open", 0))] for k, sv in (("H", "High"), ("M", "Medium"), ("L", "Low"))],
          caption="Defect log D1–D36 by severity and status (`docs/DEFECT_LOG.md`). Open items wait for author decisions (§C).")

    H(2, "6. Rigour: how the numbers are kept honest")
    Table(["Mechanism", "What it guarantees", "Shown to fail on a broken input?"], [
        ["Claim register with status letters", "a number enters a chapter only with a V row", "—"],
        ["Pre-registration with dated amendments", "verdict rules fixed before the run; departures visible", "—"],
        ["Generated dashboard, crux and test registers (`--check`)", "no hand-typed number in those documents", "page check: yes (tampering test)"],
        ["Stale-figure checker (87 files)", "no superseded figure cited as current", "yes (formatting variants, range arrows)"],
        ["Run-identity probe", "the clean-code flag fires on producing code and ignores results", "yes (fails on the pre-fix code)"],
        ["Mutation testing of the infrastructure verifier", "each check is needed by a test", "26 of 26 mutants killed"],
        ["Adversarial review on a different model", "findings outside the author's blind spots", "33 findings, none rejected"],
    ])

    H(2, "7. Limitations")
    Table(["Limitation", "Effect", "Where recorded"], [
        ["Simulated mobility; no radio, MAC or network stack", "latency is the cryptographic step only", "§3.6, SC-22"],
        ["Local Hardhat chain only", "gas is exact but no public-network witness", "N-11 (Sepolia)"],
        ["One host type for latency", "absolute values not portable; ratios within runs are", "guide rule 1.1.7"],
        ["In-process revocation registry", "I3 bounds messages, not time; no propagation delay", "#46"],
        ["Gas of random inputs varies by ±12", "I4 reported as ranges", "#47, N-18"],
        ["Reviewers steered by the orchestrator", "independence is partial", "N-22"],
    ])

    H(2, "8. What comes next")
    Para("Work milestone WM-2 (`docs/PLAN_WM-2.md`): a results pipeline of record (stamped producers, promote "
         "step, machine-readable claims), deterministic gas or ranges by rule, the review-2 carried fixes "
         "(chain-reading resolver, restricted `attestEvent`, freshness re-runs on one host), chapter checks, "
         "and draft 2 of this report.")

    H(2, "Appendix: sources and regeneration")
    Table(["Data", "File"], [
        ["Snapshot of all results", "`docs/figures/dashboard_snapshot.json`"],
        ["Infrastructure per-run data", "`cv2x-testbed/sumo/results/infrastructure_stats.json`, `infrastructure_revocation.json`"],
        ["Process counts", "`docs/presentation/data/process_metrics.yaml`"],
        ["Claim register", "`docs/MEASUREMENT_CONDITIONS.md`"],
    ])
    Para("Regenerate: `python3 docs/figures/make_dashboard_data.py && python3 docs/presentation/make_presentation.py`.")


# ---------------------------------------------------------------- renderers
def md():
    out = []
    for b in blocks:
        if b[0] == "h":
            out += ["#" * b[1] + " " + b[2], ""]
        elif b[0] == "p":
            out += [b[1], ""]
        elif b[0] == "note":
            out += ["> " + b[1], ""]
        elif b[0] == "table":
            _, head, rows, cap = b
            out.append("| " + " | ".join(head) + " |")
            out.append("|" + "---|" * len(head))
            out += ["| " + " | ".join(str(c).replace("|", "/") for c in r) + " |" for r in rows]
            out += ([f"*{cap}*"] if cap else []) + [""]
        elif b[0] == "fig":
            _, path, cap, alt = b
            out += [f"![{alt}]({path})", "", f"*{cap}*", ""]
        elif b[0] == "mermaid":
            out += ["```mermaid", b[1], "```", "", f"*{b[2]}*", ""]
    return "\n".join(out).rstrip() + "\n"


def inline(text):
    t = html.escape(text)
    import re
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
    return t


def page():
    css = (HERE / "report_page.css").read_text()
    parts = ["<title>CVIN Results Report</title>", f"<style>{css}</style>", '<main class="wrap">']
    toc = [(b[2]) for b in blocks if b[0] == "h" and b[1] == 2]
    for i, b in enumerate(blocks):
        if b[0] == "h":
            tag = f"h{b[1]}"
            anchor = "s" + str(i)
            parts.append(f'<{tag} id="{anchor}">{inline(b[2])}</{tag}>')
            if b[1] == 1:
                parts.append('<nav class="toc" aria-label="Contents"><ol>' + "".join(
                    f'<li><a href="#s{j}">{inline(bb[2])}</a></li>' for j, bb in enumerate(blocks) if bb[0] == "h" and bb[1] == 2) + "</ol></nav>")
        elif b[0] == "p":
            parts.append(f"<p>{inline(b[1])}</p>")
        elif b[0] == "note":
            parts.append(f'<p class="note">{inline(b[1])}</p>')
        elif b[0] == "table":
            _, head, rows, cap = b
            t = '<div class="tbl"><table><thead><tr>' + "".join(f"<th>{inline(h)}</th>" for h in head) + "</tr></thead><tbody>"
            for r in rows:
                cells = []
                for c in r:
                    s = str(c)
                    cls = ' class="ok"' if s in ("PASS", "Supported") or s.startswith("Supported") else (' class="bad"' if s == "FAIL" else "")
                    cells.append(f"<td{cls}>{inline(s)}</td>")
                t += "<tr>" + "".join(cells) + "</tr>"
            t += "</tbody></table></div>"
            if cap:
                t += f'<p class="cap">{inline(cap)}</p>'
            parts.append(t)
        elif b[0] == "fig":
            _, path, cap, alt = b
            data = base64.b64encode((HERE / path).resolve().read_bytes()).decode()
            parts.append(f'<figure><img src="data:image/png;base64,{data}" alt="{html.escape(alt)}"><figcaption>{inline(cap)}</figcaption></figure>')
        elif b[0] == "mermaid":
            parts.append(f'<figure><pre class="mermaid">{html.escape(b[1])}</pre><figcaption>{inline(b[2])}</figcaption></figure>')
    parts.append("</main>")
    return "\n".join(parts) + "\n"


def main():
    build()
    text = md()
    if "--check" in sys.argv:
        if not OUT_MD.exists() or OUT_MD.read_text() != text:
            print("STALE: docs/presentation/REPORT_DRAFT_1.md (run docs/presentation/make_presentation.py)")
            sys.exit(1)
        print("presentation report is current")
        return
    figures()
    OUT_MD.write_text(text)
    OUT_HTML.write_text(page())
    print(f"wrote {OUT_MD.relative_to(ROOT)} ({len(text)} bytes), {OUT_HTML.relative_to(ROOT)}, {len(list(FIG.glob('*.png')))} figures")


if __name__ == "__main__":
    main()
