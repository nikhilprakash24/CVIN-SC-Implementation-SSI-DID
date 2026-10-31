"""
Review 02 Pass 3 Low: the SUMO identity layers had a freshness window but no
replay cache, so a captured BSM re-delivered to the same receiver inside the
1.1 s window verified again. Both layers now use the same FreshnessPolicy
(identity/freshness.py) as the cv2x providers, replay cache on by default,
keyed per receiver. These tests fail on the pre-fix code.
"""

import os
import sys

import pytest

from conftest import ROOT
from identity.freshness import DEFAULT_REPLAY_CACHE_SIZE, FreshnessPolicy


@pytest.fixture(scope='module')
def sumo():
    sys.path.insert(0, os.path.join(ROOT, 'sumo'))
    import sumo_identity_integration as module
    return module


def _bsm(t, seq=1):
    return {"msg_type": "BSM", "seq": seq, "sender": "v", "timestamp": t,
            "position": [1.0, 2.0], "speed": 20.0, "heading": 90.0, "emergency": False}


def _layer(sumo, kind, now):
    if kind == 'ssi':
        layer = sumo.SSIIdentityLayer(clock=lambda: now[0])
        layer.enroll("v", "5YJ3E1EA0PF123456", "Tesla", "M3", 2024)
    else:
        layer = sumo.PKIIdentityLayer(clock=lambda: now[0])
        layer.enroll("v")
    return layer


@pytest.mark.parametrize('kind', ['ssi', 'pki'])
def test_replay_within_window_rejected(sumo, kind):
    now = [10.0]
    layer = _layer(sumo, kind, now)
    signed, _ = layer.sign("v", _bsm(10.0))
    assert layer.verify("rx", signed)[0] is True
    now[0] = 10.5                                    # still inside the 1.0 s window
    assert layer.verify("rx", signed)[0] is False    # replay to the same receiver
    assert layer.freshness.rejected_replay == 1
    # the same broadcast is still accepted ONCE by another receiver
    assert layer.verify("rx2", signed)[0] is True
    assert layer.verify("rx2", signed)[0] is False
    # a new message from the same sender is not a replay
    fresh, _ = layer.sign("v", _bsm(10.5, seq=2))
    assert layer.verify("rx", fresh)[0] is True


@pytest.mark.parametrize('kind', ['ssi', 'pki'])
def test_rejected_message_does_not_poison_cache(sumo, kind):
    now = [10.0]
    layer = _layer(sumo, kind, now)
    signed, _ = layer.sign("v", _bsm(10.0))
    forged = dict(signed, signature=signed["signature"][:-4] + ("0000" if not signed["signature"].endswith("0000") else "1111"))
    assert layer.verify("rx", forged)[0] is False
    assert layer.verify("rx", signed)[0] is True


@pytest.mark.parametrize('kind', ['ssi', 'pki'])
def test_layer_policy_matches_providers(sumo, kind):
    layer = _layer(sumo, kind, [0.0])
    assert layer.freshness.describe() == FreshnessPolicy().describe()   # on by default


def test_replay_cache_sizing(sumo):
    # 2 x N x (10 BSM + 1 FCW) msg/s x 8 receivers x 1.1 s, floor = provider default
    assert sumo.replay_cache_size_for(50) == DEFAULT_REPLAY_CACHE_SIZE
    assert sumo.replay_cache_size_for(1000) == 193_600
    sim = sumo.SUMOIdentityIntegration(simulation_mode=True, num_vehicles=1000)
    assert sim.pki.freshness.replay_cache_size == sim.ssi.freshness.replay_cache_size == 193_600


def test_simulation_attack_tests_include_replay(sumo, tmp_path):
    sim = sumo.SUMOIdentityIntegration(simulation_mode=True, num_vehicles=10,
                                       results_path=tmp_path / "out.json")
    sim.start_sumo()
    sim._sim_now = 3.0
    for vid in sim.mobility.vehicle_ids():
        sim.assign_vehicle_identity(vid)
        sim.vehicle_states[vid] = sim.get_vehicle_state(vid)
    sim.run_attack_tests(3.0)
    assert sim.attack_results['replay_pki_rejected'] is True
    assert sim.attack_results['replay_ssi_rejected'] is True
    results = sim.build_results(1, 0.0)
    assert results['freshness']['replay_cache'] is True
    assert results['freshness']['pki_evicted_live'] == 0
