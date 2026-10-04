"""L3 — external conformance regression (plan S5).

Reads the committed raw jest results of the official W3C DID test suite run
(docs/conformance/reports/rerun-2026-10-03/jest-cvin/*.json) and asserts the recorded
pass count has not regressed below the verified level (335 of 336). This guards the
*record*; re-running the suite itself is a manual step documented in
docs/conformance/W3C_DID_TEST_SUITE.md.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
REPORTS = ROOT / "docs/conformance/reports/rerun-2026-10-03/jest-cvin"
FLOOR_PASSED, MAX_FAILED = 335, 1


def _counts():
    passed = failed = 0
    files = sorted(REPORTS.glob("*.json"))
    assert files, f"no jest reports under {REPORTS}"
    for f in files:
        d = json.loads(f.read_text())
        if "numPassedTests" in d:
            passed += d["numPassedTests"]; failed += d["numFailedTests"]
        else:  # per-suite shape: walk testResults
            for tr in d.get("testResults", []):
                for a in tr.get("assertionResults", []):
                    passed += a.get("status") == "passed"; failed += a.get("status") == "failed"
    return passed, failed, len(files)


def test_external_did_suite_record_has_not_regressed():
    passed, failed, n = _counts()
    assert n >= 5, f"expected per-suite reports, found {n}"
    assert passed >= FLOOR_PASSED, f"external DID suite record regressed: {passed} passed (< {FLOOR_PASSED})"
    assert failed <= MAX_FAILED, f"external DID suite record regressed: {failed} failed (> {MAX_FAILED})"
