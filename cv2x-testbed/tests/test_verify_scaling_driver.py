"""
WM-2 A3b (2026-10-22): the verify-scaling driver (Exp. D, register #26) restarted simulation time at 0 for
each neighbour count P. Since the SUMO layer's replay cache is on by default (8c325cc), a sender's BSM with
a timestamp it had already used at a smaller P was refused as a replay, and the driver stopped with
"expected warm successful verification" at P = 10. This test runs the driver end to end at a tiny size and
fails on that code.
"""

import importlib.util
import json
import os
import sys

from conftest import ROOT


def test_driver_runs_every_density_with_the_replay_cache_on(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(os.path.join(ROOT, 'sumo'))
    path = os.path.join(ROOT, 'sumo', 'run_verify_scaling.py')
    spec = importlib.util.spec_from_file_location('run_verify_scaling_under_test', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = tmp_path / 'scaling_verify.json'
    monkeypatch.setattr(mod, 'OUT_JSON', out)
    monkeypatch.setattr(sys, 'argv', ['run_verify_scaling.py', '--intervals', '3', '--warmup', '1'])
    mod.main()
    doc = json.loads(out.read_text())
    assert 'v2v_density' in doc
    assert len(json.dumps(doc['v2v_density'])) > 0
