"""The figures guard fires: --check fails when the stored figure data no longer matches the results files."""
import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "figures"))
import make_figures  # noqa: E402


def test_check_passes_on_current_data():
    assert make_figures.check()


def test_check_fires_on_stale_data(tmp_path):
    d = json.loads(make_figures.DATA.read_text())
    d["gas"]["admit_with_groth16"] += 1
    stale = tmp_path / "figures_data.json"
    stale.write_text(json.dumps(d))
    assert not make_figures.check(stale)
    assert not make_figures.check(tmp_path / "missing.json")
