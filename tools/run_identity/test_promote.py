"""The promote step refuses every run that is not a run of record (WM-2 step A4 gate).

Each test builds a run directory in a temporary `runs/` from the real stamp of a real producer, changes one
thing, and checks that promote.check() names it. Run: python3 -m pytest -q tools/run_identity/test_promote.py
"""
import json
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import promote  # noqa: E402
import stamp as S  # noqa: E402

PRODUCER = "1_blockchain-identity/test/L2-identity-system/security/securityScenarios.test.js"
DEST = "4_comparison-framework/security-analysis/results/attack_results.json"


@pytest.fixture
def run(tmp_path, monkeypatch):
    """A clean, promotable run of PRODUCER (the stamp is forced clean so the test runs on any tree)."""
    real = S.stamp(PRODUCER)
    clean = dict(real, code_dirty=False)
    monkeypatch.setattr(promote, "RUNS", tmp_path / "runs")
    monkeypatch.setattr(promote._stamp, "stamp", lambda p: clean)
    d = promote.new_run(PRODUCER, "security-matrix")
    (d / "attack_results.json").write_text('{"ok": true}\n')
    promote.write_manifest(d, PRODUCER, clean, {"attack_results.json": DEST})
    return d


def edit_manifest(d, fn):
    m = json.loads((d / "manifest.json").read_text())
    fn(m)
    (d / "manifest.json").write_text(json.dumps(m))


def test_clean_run_is_promotable(run):
    reasons, _ = promote.check(run)
    assert reasons == []


def test_dirty_run_refuses(run):
    edit_manifest(run, lambda m: m["stamp"].update(code_dirty=True))
    reasons, _ = promote.check(run)
    assert any("dirty" in r and "not a run of record" in r for r in reasons)


def test_unknown_cleanliness_refuses(run):
    edit_manifest(run, lambda m: m["stamp"].update(code_dirty=None))
    assert any("unknown state" in r for r in promote.check(run)[0])


def test_js_field_names_are_read(run):
    def js(m):
        st = m["stamp"]
        m["stamp"] = {"dirty": True, "commitFull": st["commit"], "scopeSha": st["scope_sha"], "scope": st["scope"]}
    edit_manifest(run, js)
    assert any("not a run of record" in r for r in promote.check(run)[0])


def test_other_commit_refuses(run):
    edit_manifest(run, lambda m: m["stamp"].update(commit="0" * 40))
    assert any("promote it from its own commit" in r for r in promote.check(run)[0])


def test_changed_scope_refuses(run):
    edit_manifest(run, lambda m: m["stamp"].update(scope_sha="000000000000"))
    assert any("scope changed" in r for r in promote.check(run)[0])


def test_code_edited_after_the_run_refuses(run, monkeypatch):
    stamped = json.loads((run / "manifest.json").read_text())["stamp"]
    monkeypatch.setattr(promote._stamp, "stamp", lambda p: dict(stamped, code_dirty=True))
    assert any("dirty now" in r for r in promote.check(run)[0])


def test_output_edited_after_the_run_refuses(run):
    (run / "attack_results.json").write_text('{"ok": false}\n')
    assert any("bytes differ" in r for r in promote.check(run)[0])


def test_destination_outside_the_producers_results_refuses(run):
    edit_manifest(run, lambda m: m["outputs"][0].update(dest="docs/thesis/chapter5.md"))
    assert any("not one of the producer's result paths" in r for r in promote.check(run)[0])


def test_unregistered_producer_refuses(run):
    edit_manifest(run, lambda m: m.update(producer="1_blockchain-identity/scripts/deployERC1056.js"))
    assert any("not a producer of record" in r for r in promote.check(run)[0])


def test_directory_without_manifest_refuses(tmp_path):
    assert "no manifest.json" in promote.check(tmp_path)[0][0]


def test_promote_copies_and_records(run, tmp_path, monkeypatch):
    monkeypatch.setattr(promote, "ROOT", tmp_path / "repo")
    assert promote.promote(run) == 0
    assert (tmp_path / "repo" / DEST).read_text() == '{"ok": true}\n'
    assert (run / "promoted.json").is_file()


def test_refused_promote_copies_nothing(run, tmp_path, monkeypatch):
    monkeypatch.setattr(promote, "ROOT", tmp_path / "repo")
    edit_manifest(run, lambda m: m["stamp"].update(code_dirty=True))
    assert promote.promote(run) == 1
    assert not (tmp_path / "repo" / DEST).exists()
