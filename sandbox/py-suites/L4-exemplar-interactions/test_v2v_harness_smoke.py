"""L4 — V2V harness smoke (plan S6, second part).

Runs cv2x-testbed/sumo/sumo_identity_integration.py in --simulate mode (mock mobility,
real ECDSA P-256 / secp256k1 / VC crypto) for a short, small run and checks that it
exits 0 and reports sign/verify statistics for BOTH populations (PKI and SSI). The
results JSON is written to a pytest temp dir via --results so the committed record
under cv2x-testbed/sumo/results/ is never touched (verified by hash). No latency
number is asserted: hosts differ; this is a does-it-run check, not a measurement.
"""
import hashlib, json, pathlib, re, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "cv2x-testbed/sumo/sumo_identity_integration.py"
COMMITTED = ROOT / "cv2x-testbed/sumo/results/v2v_latency.json"
VEHICLES, DURATION_S, WALL_LIMIT_S = 10, 2, 60


def _sha(p: pathlib.Path):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def test_v2v_harness_simulate_smoke(tmp_path):
    before = _sha(COMMITTED)
    out_json = tmp_path / "v2v_latency.json"
    cmd = [sys.executable, str(SCRIPT), "--simulate",
           "--duration", str(DURATION_S), "--vehicles", str(VEHICLES),
           "--results", str(out_json)]
    t0 = time.perf_counter()
    r = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True, timeout=WALL_LIMIT_S)
    wall = time.perf_counter() - t0
    assert r.returncode == 0, f"rc={r.returncode}\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}"
    assert wall < WALL_LIMIT_S, f"smoke took {wall:.1f}s"
    assert _sha(COMMITTED) == before, "committed results/v2v_latency.json was modified"

    # stdout: the statistics block names both populations with real sample counts.
    assert "SIMULATION MODE" in r.stdout
    assert re.search(rf"Vehicles:\s+{VEHICLES} total", r.stdout), r.stdout[-1500:]
    for label in ("PKI", "SSI"):
        for op in ("sign", "verify (warm)"):
            m = re.search(rf"{label}\s+{re.escape(op)}\s*:\s*median\s+[\d.]+ ms \| p95\s+[\d.]+ ms \| n=(\d+)",
                          r.stdout)
            assert m and int(m.group(1)) > 0, f"{label} {op}: no stats line with samples\n{r.stdout[-1500:]}"
    assert "all injected bad messages rejected" in r.stdout, r.stdout[-1500:]

    # JSON: same facts, structured; both populations sent and verified messages.
    d = json.loads(out_json.read_text())
    assert d["mode"] == "simulate" and d["vehicles"]["total"] == VEHICLES
    assert d["vehicles"]["pki"] > 0 and d["vehicles"]["ssi_mobi_vid"] > 0
    for pop in ("pki", "ssi"):
        blk = d[pop]
        assert blk["messages_sent"] > 0 and blk["messages_verified"] > 0, (pop, blk)
        for key in ("sign_ms", "cold_ms", "warm_ms"):
            assert blk[key] and blk[key]["n"] > 0, (pop, key, blk[key])
    assert all(d["attack_tests"].values()), d["attack_tests"]
