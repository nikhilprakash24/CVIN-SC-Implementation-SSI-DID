"""L3 — the internal W3C compliance checker as a test (plan S5).

Runs cv2x-testbed/scripts/w3c_compliance_checker.py and asserts the executable score
is at least the verified floor (94.3 on 2026-10-03; raise it when the score genuinely
rises, never to a target). Mirrors the CI gate in .github/workflows/w3c-compliance.yml.
"""
import pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
FLOOR = 94.3


def test_internal_checker_score_at_least_floor(tmp_path):
    out = subprocess.run([sys.executable, str(ROOT / "cv2x-testbed/scripts/w3c_compliance_checker.py")],
                         cwd=tmp_path, capture_output=True, text=True, timeout=180)
    m = re.search(r"(?:OVERALL|EXECUTABLE) COMPLIANCE SCORE:\s*([0-9]+(?:\.[0-9]+)?)%", out.stdout)
    assert m, f"score line not found; rc={out.returncode}\n{out.stdout[-800:]}\n{out.stderr[-400:]}"
    score = float(m.group(1))
    assert score >= FLOOR, f"internal compliance score {score} below floor {FLOOR}"
