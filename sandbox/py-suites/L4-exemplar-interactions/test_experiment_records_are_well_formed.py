"""L4 — experiment reproducibility, schema level (plan S6, first part).

The three measured experiments write JSON results of record. These tests check the
records are present, carry an environment header (so numbers are never cited without
conditions) and keep their row structure. They deliberately do not assert numbers:
hosts differ (register #29 caveat); a number is compared only within its own run.
"""
import json, pathlib, pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]
RECORDS = {
    "pki_vs_erc1056": ROOT / "cv2x-testbed/results/pki_vs_erc1056.json",
    "freshness_k": ROOT / "cv2x-testbed/results/freshness_k.json",
    "lifecycle_parity": ROOT / "cv2x-testbed/results/lifecycle_parity.json",
}
HEADER_KEYS = {"date_utc", "git_commit", "python_version", "cpu_model", "chain_id"}


@pytest.mark.parametrize("name,path", RECORDS.items())
def test_record_exists_with_environment_header(name, path):
    assert path.exists(), f"{name}: results of record missing at {path}"
    d = json.loads(path.read_text())
    env = d.get("environment") or d.get("meta") or {}
    missing = HEADER_KEYS - set(env)
    assert not missing, f"{name}: environment header lacks {sorted(missing)}"


@pytest.mark.parametrize("name,path", RECORDS.items())
def test_record_has_rows_with_latency_stats(name, path):
    d = json.loads(path.read_text())
    rows = d.get("rows") or d.get("results") or []
    assert rows, f"{name}: no result rows"
    for r in rows:
        if isinstance(r, dict):
            assert "median_ms" in r or "median" in r, f"{name}: row without a median: {list(r)[:8]}"
