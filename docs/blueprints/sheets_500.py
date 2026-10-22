"""500-series instruments (cost, latency) and 600-series shipyard (deployment)."""
from bplib import *  # noqa: F401,F403
from sheets_100 import CREATE_GAS


def bp501():
    s = Sheet("BP-501", "Gas ladder — create-identity cost", "Instrument panel: one representative createIdentity transaction per substrate, register #25 (M1, cancun, N=30, CI width 0)",
              notes=["Operation definitions differ by design (bare createIdentity vs VIN-bound mintVehicle); the reconciliation is in MEASUREMENT_CONDITIONS #6/#25: ~10× bare, ≈7× when the VIN is bound on both sides (createVehicleDID 78,068).",
                     "Over a full MOBI VID lifecycle (#30) the minimal registry is cheapest by 2.6× (vs ERC-721) and 3.0× (vs ERC-725), not 10×; H1's restatement is the author's framing decision.",
                     "ERC-4337 EntryPoint and LSP8 are minimal representatives (lower bounds). MOBI-VID-V2 is an application profile. Fiat is a parameter and is not drawn."],
              refs=["4_comparison-framework/results/gas_benchmark.json · gas_comparison.tex/.csv (#25)", "docs/MEASUREMENT_CONDITIONS.md #6, #25, #30, #31 · 1_blockchain-identity/scripts/benchmark_gas.js"],
              notes_width=1060)
    x, y = 120, 215
    s.section_label(x, y, "LOG-SCALE LADDER (gas, create identity)")
    lo, hi = math.log10(40000), math.log10(2000000)
    bw = 1000
    for i, (name, gas, model) in enumerate(CREATE_GAS):
        yy = y + 30 + i * 46
        frac = (math.log10(gas) - lo) / (hi - lo)
        s.rect(x + 160, yy, bw, 30, sw=0.8, stroke=LINE_FAINT)
        s.rect(x + 160, yy, bw * frac, 30, sw=1.6, fill=GROUND_DK if gas < 60000 else "none", stroke=ACCENT if gas < 60000 else LINE)
        s.text(x + 150, yy + 20, name, size=11, anchor="end", mono=True, weight="bold" if gas < 60000 else "normal")
        s.text(x + 170 + bw * frac, yy + 20, f"{gas:,}", size=11, mono=True, color=ACCENT)
        s.text(x + 170 + bw * frac + 90, yy + 20, model, size=9, mono=True, color=LINE_SOFT)
    # axis ticks
    ay = y + 30 + 10 * 46 + 4
    for g in (50000, 100000, 200000, 500000, 1000000):
        fx = x + 160 + bw * (math.log10(g) - lo) / (hi - lo)
        s.line(fx, ay, fx, ay + 6, sw=0.9, stroke=LINE_SOFT); s.text(fx, ay + 18, f"{g // 1000}k", size=9, anchor="middle", mono=True, color=LINE_SOFT)
    s.line(x + 160, ay, x + 160 + bw, ay, sw=0.9, stroke=LINE_SOFT)
    # ratio dials
    dx, dy = 120, ay + 50
    s.section_label(dx, dy, "RATIO DIALS (the H1 claim, four honest ways)")
    dials = [("32.2×", "spread, cheapest → dearest", "52,216 → 1,680,816"), ("≈10×", "ERC-1056 bare vs ERC-721 VIN-bound", "52,594 vs 542,378"), ("≈7×", "VIN bound on both sides", "78,068 vs 542,378"),
             ("2.6× / 3.0×", "lifetime, vs ERC-721 / ERC-725", "#30, 17-event sequence"), ("+46,830", "ERC-4337 EntryPoint per routed op", "96,228 vs 49,366 direct")]
    for i, (big, lab, sub) in enumerate(dials):
        cx = dx + 110 + i * 250
        s.circle(cx, dy + 70, 48, sw=2.0)
        s.text(cx, dy + 76, big, size=15, anchor="middle", weight="bold", mono=True, color=ACCENT)
        s.text(cx, dy + 136, lab, size=9, anchor="middle", mono=True)
        s.text(cx, dy + 150, sub, size=8, anchor="middle", mono=True, color=LINE_SOFT)
    return s


def bp502():
    s = Sheet("BP-502", "Latency budget — J2945/1, P*(f), freshness-k", "Instrument panel: where each design sits against the 100 ms BSM interval and the identity share f",
              notes=["Identity budget = f × 100 ms (f = 0.5 working assumption; results for f ∈ {0.25, 0.5, 1.0}). P*(f) = floor(f·100 ms / t) = neighbours serviceable per interval; viable in dense traffic when P* ≫ 100.",
                     "t_eff(k) = 0.428 + 10.52/k ms fits the k ∈ {1, 5, 25, ∞} sweep within ±7 % (#32). On a second host with t_local ≈ 0.5 ms no k reaches P*(0.5) = 100 (#37): the knee is host-dependent and is always quoted with its t_local.",
                     "All ERC-1056 round-trips are to a local Hardhat node (≈2.5 ms); a public network makes the uncached rows worse, not better, and leaves the off-chain rows unchanged."],
              refs=["docs/LATENCY_BUDGET.md §1–§5 · cv2x-testbed/results/freshness_k.md, freshness_k_probe*.md (#32, #37)", "cv2x-testbed/results/pki_vs_erc1056.md (#21) · 4_comparison-framework/results/v2v_latency_stats (#27)"],
              notes_width=1060)
    # budget bar
    x, y = 120, 215
    s.section_label(x, y, "THE BUDGET — ONE 100 ms BSM INTERVAL")
    bw = 1000
    s.rect(x, y + 20, bw, 40, sw=2.0)
    s.rect(x, y + 20, bw * 0.5, 40, sw=1.6, fill=GROUND_DK, stroke=ACCENT)
    s.text(x + bw * 0.25, y + 45, "identity share f·100 ms  (f = 0.5 → 50 ms)", size=11, anchor="middle", mono=True, color=ACCENT)
    s.text(x + bw * 0.75, y + 45, "sensor fusion, application logic, network (out of scope)", size=10, anchor="middle", mono=True, color=LINE_SOFT)
    s.dim(x, y + 76, x + bw, y + 76, "100 ms (SAE J2945/1, 10 Hz)")
    # P* table
    tx, ty = 120, 325
    s.section_label(tx, ty, "MEASURED POSITION — PER-NEIGHBOUR COST t AND SATURATION P*(f)")
    rows = [("PKI, cert in message (M0)", "0.321 / 0.366", "77", "155", "311", "viable, dense"),
            ("ERC-1056 uncached, 4 RPC per msg (k = 1)", "10.946 / 16.153", "2", "4", "9", "not viable"),
            ("ERC-1056 refresh every k = 25", "0.425 / 0.764 (amort. 0.850)", "29", "58", "117", "marginal → viable"),
            ("ERC-1056 cached, k = ∞ (off-chain verify)", "0.428 / 0.631", "58", "116", "233", "viable, dense"),
            ("SSI warm VC verify, V2V sim (#27)", "0.153 [0.151, 0.154]", "163", "326", "653", "viable; ≈600× under 100 ms")]
    s.table(tx, ty + 14, [("DESIGN / CONDITION", 330), ("t median / p95 (ms)", 230), ("P*(.25)", 70), ("P*(.5)", 70), ("P*(1)", 70), ("VERDICT", 200)], rows, size=10, lh=22,
            cell_colors=lambda ri, ci, v: (WARN if "not" in v else OK if "viable" in v else None) if ci == 5 else None)
    # curve t_eff(k)
    cx, cy, cw, ch = 120, 520, 620, 240
    s.section_label(cx, cy - 12, "t_eff(k) = 0.428 + 10.52 / k   — refresh every k messages (#32)")
    s.rect(cx, cy, cw, ch, sw=1.0, stroke=LINE_SOFT)
    ks = [1, 2, 3, 5, 8, 12, 25, 50, 100, 146, 250, 500]
    def px(k): return cx + cw * (math.log10(k) / math.log10(500))
    def py(t): return cy + ch - ch * (math.log10(t) - math.log10(0.3)) / (math.log10(12) - math.log10(0.3))
    pts = [(px(k), py(0.428 + 10.52 / k)) for k in ks]
    s.poly(pts, stroke=ACCENT, sw=2.0)
    for k, t in ((1, 10.946), (5, 2.379), (25, 0.850), (500, 0.453)):
        s.circle(px(k), py(t), 4, fill=LINE)
    for k in (1, 5, 25, 146, 500):
        s.line(px(k), cy + ch, px(k), cy + ch + 5, sw=0.9, stroke=LINE_SOFT); s.text(px(k), cy + ch + 17, "∞" if k == 500 else str(k), size=9, anchor="middle", mono=True, color=LINE_SOFT)
    for t in (0.5, 1, 2, 5, 10):
        s.line(cx - 5, py(t), cx, py(t), sw=0.9, stroke=LINE_SOFT); s.text(cx - 8, py(t) + 4, str(t), size=9, anchor="end", mono=True, color=LINE_SOFT)
    s.text(cx + cw / 2, cy + ch + 32, "k (messages between chain refreshes, log)", size=9, anchor="middle", mono=True, color=LINE_SOFT)
    s.text(cx - 40, cy + ch / 2, "ms", size=9, anchor="middle", mono=True, color=LINE_SOFT, rotate=-90)
    # budget line: t for P*(0.5)=100 → 0.5 ms
    s.line(cx, py(0.5), cx + cw, py(0.5), stroke=OK, sw=1.2, dash="6,4"); s.text(cx + cw - 6, py(0.5) - 6, "P*(0.5) = 100 ⇔ t = 0.5 ms", size=9, anchor="end", mono=True, color=OK)
    s.line(px(146), cy, px(146), cy + ch, stroke=OK, sw=1.0, dash="3,3"); s.text(px(146) + 4, cy + 14, "k ≈ 146", size=9, mono=True, color=OK)
    s.text(cx, cy + ch + 56, "dots = measured medians (amortised mean at k = 5, 25); line = fit. Staleness: a revoked key is honoured for ≤ k − 1 further messages.", size=9, mono=True, color=LINE_SOFT)
    # right commentary
    rx, ry = 800, 520
    s.section_label(rx, ry - 12, "VERDICT ON H3")
    s.lines(rx, ry + 14, ["Reading the chain at message time fails even sparse traffic (P* = 4).", "Fully off-chain verification is within a small factor of PKI", "(0.43 vs 0.32 ms): the substrate is not the bottleneck once the",
                          "chain is off the hot path.", "", "The engineering question is freshness: how stale may a cached", "key / revocation be? k trades P* against a bounded staleness —",
                          "at 10 Hz and k = 146 a revocation can lag ≤ 14.5 s.", "", "Caveats: no radio / MAC / PHY; mobility simulated; single core;", "P* is an extrapolation beyond the tested P ≤ 80 (#26)."], size=11, lh=16)
    return s


def bp601():
    s = Sheet("BP-601", "Deployment and test harness — the shipyard", "SV-1 interface description of where each part runs, what talks to what, and the CI gates that keep the set honest",
              notes=["739 automated tests green: 369 Hardhat (incl. 43 strictly-asserted attack scenarios + nine-adapter conformance) + 358 Python (VC, resolver, MOBI VID, testbed) + 12/12 lifecycle use cases; no skips in CI.",
                     "Public-testnet (Sepolia) harness authored, not yet executed (needs RPC URL + funded key): sepolia_validation.json is a placeholder until then (M2). Real SUMO binary optional; --simulate used.",
                     "Every reported number maps to a file under results/ and a row in MEASUREMENT_CONDITIONS.md; CAPABILITIES/INVENTORY are descriptive and are never cited by chapters."],
              parts=[(1, "Hardhat project", "1_blockchain-identity: 16 contracts / 10 substrates, solc 0.8.24, OZ 5.0.2, Node 18/22"),
                     (2, "Benchmark harness", "benchmarks/: adapters ×10, MetricsCollector, scenarios crud/lifecycle/scale/batch/throughput/resolve"),
                     (3, "Security suite", "test/security/securityScenarios.test.js + attackHarness.js (54 cells)"),
                     (4, "W3C SSI layer (Python 3.11)", "did_resolver.py · vc_issuer/holder/verifier.py · mobi-vid/*.py"),
                     (5, "CV2X testbed (Python)", "identity providers, cv2x_stack.py (PHY/MAC model), sumo_identity_integration.py --simulate"),
                     (6, "Comparison framework", "4_comparison-framework: table generators → JSON / CSV / LaTeX; security-analysis"),
                     (7, "CI workflows", ".github/workflows: test-contracts.yml · w3c-compliance.yml (floor 93.0%) · benchmark.yml"),
                     (8, "Results of record", "4_comparison-framework/results · 1_blockchain-identity/results/metrics/latest · cv2x-testbed/results · docs/conformance"),
                     (9, "Sepolia harness (unrun)", "scripts/validate_sepolia.js + SEPOLIA_VALIDATION.md (M2)"),
                     (10, "This drawing set", "docs/blueprints/make_blueprints.py → sheets/*.svg → render_png.js (Chromium)")],
              parts_width=820,
              refs=["README.md (status, getting started) · docs/PROJECT_SUMMARY.md (inventory + verification table)", "docs/MEASUREMENT_CONDITIONS.md (M0 in-process · M1 Hardhat local · M1-H harness · M2 Sepolia)"])
    # three boxes: node runtime, python runtime, CI; with results store
    x, y = 560, 150
    s.box(x, y, 420, 190, "NODE / HARDHAT RUNTIME ①", ["in-process Hardhat network, chainId 31337, automine", "contracts ×16  ·  tests ×369  ·  benchmark_gas.js (N=30)",
                                                        "benchmarks/run.js → results/metrics/<ts>_<sha>/ ②", "security_scenarios → attack_results.json ③", "validate_sepolia.js (M2, unrun) ⑨"], bsize=9)
    s.box(x + 460, y, 420, 190, "PYTHON 3.11 RUNTIME ④ ⑤", ["web3 · eth-account · coincurve · cryptography · pytest", "VC layer (28 + negatives) · resolver · MOBI VID (32 + 6)",
                                                            "test_use_cases.py 12/12 · w3c_compliance_checker.py 94.3%", "sumo_identity_integration.py --simulate · run_v2v_stats.py N=30", "experiment_freshness_k.py (#32), _pki_vs_erc1056.py (#21)"], bsize=9)
    s.arrow(x + 420, y + 95, x + 460, y + 95, both=True, head=7, label="JSON-RPC 127.0.0.1 (M1) · in-process (M0)", lsize=9)
    s.box(x, y + 230, 880, 90, "RESULTS OF RECORD ⑧ (files, not prose)", ["gas_benchmark.json · scaling_*.json · mobi_vid_backends.json · v2v_latency_stats.json · security_matrix.json · attack_results.json",
                                                                          "metrics/latest/tables/*.md (crud, lifecycle, scale, resolve, analysis_basic_set) · freshness_k*.json · conformance reports"], bsize=9, dash="6,4")
    s.arrow(x + 210, y + 190, x + 210, y + 230, head=7); s.arrow(x + 670, y + 190, x + 670, y + 230, head=7)
    s.box(x, y + 350, 420, 110, "CI GATES ⑦", ["test-contracts.yml: 369 Hardhat, no skips", "w3c-compliance.yml: executable checker ≥ 93.0%", "benchmark.yml: determinism (CI width 0) and tables"], bsize=9, stroke=OK)
    s.box(x + 460, y + 350, 420, 110, "COMPARISON FRAMEWORK ⑥ → THESIS", ["generate_tables.py → gas_comparison.tex / .csv", "generate_attack_tables.py → security_comparison.tex", "docs/thesis/chapter5-results/ cites rows #n only"], bsize=9)
    s.arrow(x + 210, y + 320, x + 210, y + 350, head=7); s.arrow(x + 670, y + 320, x + 670, y + 350, head=7)
    s.box(x, y + 490, 880, 60, "BLUEPRINT SET ⑩", ["make_blueprints.py (data in script, numbers copied from ⑧ with their register row) → sheets/*.svg → render_png.js → sheets/png/*.png"], bsize=9, stroke=ACCENT)
    s.arrow(x + 440, y + 460, x + 440, y + 490, head=7)
    return s


SHEETS = [bp501, bp502, bp601]
