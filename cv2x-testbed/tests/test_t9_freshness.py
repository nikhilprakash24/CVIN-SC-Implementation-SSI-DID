"""
Review 02, T-9: replay and freshness.

Before the fix every provider signed only `message`; the `timestamp` beside
the signature was unsigned and never checked, and no verifier remembered what
it had accepted. A captured packet therefore verified forever (replay), its
timestamp could be rewritten, and `protocols/cv2x_stack.py` reported
`success=True` for a message whose signature failed.

These tests fail on the pre-fix code:
  * replayed packet accepted            -> test_*_replay_rejected
  * stale signed timestamp accepted     -> test_*_stale_rejected
  * altered (unsigned) timestamp accepted -> test_*_altered_timestamp_rejected
  * invalid message counted as success  -> test_stack_invalid_signature_is_not_success,
                                           test_scenario_does_not_count_invalid_as_success
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import pytest

from conftest import ROOT, deploy, load_artifact
from experiment_pki_vs_erc1056 import StandardPKIAdapter, make_bsm
import identity.centralized_provider as central_mod
import identity.standard.pki_identity as pki_mod
from identity.centralized_provider import CentralizedIdentityProvider
from identity.freshness import (DEFAULT_MAX_AGE_S, DEFAULT_MAX_FUTURE_S, FreshnessPolicy,
                                generation_timestamp, signed_bytes)
from identity.standard.pki_identity import VehiclePKI_CA, VehiclePKIIdentity


def _iso(offset_s: float) -> str:
    """Naive-UTC ISO timestamp `offset_s` seconds from now (provider format)."""
    return (datetime.now(timezone.utc) + timedelta(seconds=offset_s)).replace(tzinfo=None).isoformat()


# ------------------------------------------------------------------ fixtures

@pytest.fixture
def standard():
    ca = VehiclePKI_CA("CVIN-Standard-CA")
    sender = VehiclePKIIdentity("SENDER")
    sender.generate_keypair()
    sender.request_enrollment_certificate(ca)
    sender.request_pseudonym_certificates(ca, count=2)
    verifier = VehiclePKIIdentity("VERIFIER")
    verifier.trust_ca(ca.ca_certificate)
    return ca, sender, verifier


@pytest.fixture
def central():
    p = CentralizedIdentityProvider("CVIN-Central-CA")
    p.register_vehicle("A")
    return p


# ------------------------------------------------- the default is security ON

def test_defaults_are_on():
    for policy in (VehiclePKIIdentity("X").freshness, CentralizedIdentityProvider().freshness):
        assert policy.enabled and policy.replay_cache
        assert policy.max_age_s == DEFAULT_MAX_AGE_S == 1.0
        assert policy.max_future_s == DEFAULT_MAX_FUTURE_S == 0.1


# ------------------------------------------------------------- standard PKI

def test_standard_genuine_accepted(standard):
    ca, sender, verifier = standard
    assert verifier.verify_message(sender.sign_message(make_bsm(1)), ca.get_crl())[0] is True


def test_standard_replay_rejected(standard):
    ca, sender, verifier = standard
    signed = sender.sign_message(make_bsm(2))
    assert verifier.verify_message(signed, ca.get_crl())[0] is True
    replay = json.loads(json.dumps(signed))            # byte-identical capture
    assert verifier.verify_message(replay, ca.get_crl())[0] is False
    assert verifier.freshness.rejected_replay == 1


def test_standard_replay_with_malleated_signature_rejected(standard):
    """(r, n-s) is a second valid ECDSA signature; the cache keys on the signed bytes."""
    from cryptography.hazmat.primitives.asymmetric.utils import (decode_dss_signature,
                                                                encode_dss_signature)
    ca, sender, verifier = standard
    signed = sender.sign_message(make_bsm(3))
    assert verifier.verify_message(signed, ca.get_crl())[0] is True
    r, s = decode_dss_signature(bytes.fromhex(signed['signature']))
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551   # P-256 order
    malleated = dict(signed, signature=encode_dss_signature(r, n - s).hex())
    assert verifier.verify_message(malleated, ca.get_crl())[0] is False


def test_standard_replay_accepted_only_when_cache_explicitly_off(standard):
    """Configuration control: the cache, not something else, rejects the replay."""
    ca, sender, verifier = standard
    verifier.freshness = FreshnessPolicy(replay_cache=False)
    signed = sender.sign_message(make_bsm(4))
    assert verifier.verify_message(signed, ca.get_crl())[0] is True
    assert verifier.verify_message(signed, ca.get_crl())[0] is True


def test_standard_stale_rejected(standard, monkeypatch):
    """Genuinely signed, but the signed generation time is 5 s old."""
    ca, sender, verifier = standard
    monkeypatch.setattr(pki_mod, 'generation_timestamp', lambda: _iso(-5.0), raising=False)
    stale = sender.sign_message(make_bsm(5))
    assert verifier.verify_message(stale, ca.get_crl())[0] is False
    assert verifier.freshness.rejected_stale == 1


def test_standard_future_rejected(standard, monkeypatch):
    ca, sender, verifier = standard
    monkeypatch.setattr(pki_mod, 'generation_timestamp', lambda: _iso(+5.0), raising=False)
    future = sender.sign_message(make_bsm(6))
    assert verifier.verify_message(future, ca.get_crl())[0] is False


def test_standard_message_ages_out(standard):
    """The same genuine message is accepted now and rejected once the window has passed."""
    ca, sender, verifier = standard
    signed = sender.sign_message(make_bsm(7))
    verifier.freshness = FreshnessPolicy(replay_cache=False, clock=lambda: time.time() + 1.5)
    assert verifier.verify_message(signed, ca.get_crl())[0] is False


def test_standard_altered_timestamp_rejected(standard):
    """Rewriting a stale packet's timestamp to 'now' breaks the signature."""
    ca, sender, verifier = standard
    signed = sender.sign_message(make_bsm(8))
    altered = dict(signed, timestamp=_iso(+0.05))
    assert verifier.verify_message(altered, ca.get_crl())[0] is False
    assert verifier.verify_message(signed, ca.get_crl())[0] is True   # original still fine


def test_standard_missing_timestamp_rejected(standard):
    ca, sender, verifier = standard
    signed = sender.sign_message(make_bsm(9))
    del signed['timestamp']
    assert verifier.verify_message(signed, ca.get_crl())[0] is False


def test_standard_forged_packet_does_not_poison_cache(standard):
    """A bad-signature copy is rejected and does not block the genuine packet."""
    ca, sender, verifier = standard
    signed = sender.sign_message(make_bsm(10))
    sig = bytearray(bytes.fromhex(signed['signature']))
    sig[-1] ^= 1
    assert verifier.verify_message(dict(signed, signature=sig.hex()), ca.get_crl())[0] is False
    assert verifier.verify_message(signed, ca.get_crl())[0] is True


def test_signed_bytes_cover_timestamp():
    assert signed_bytes({'a': 1}, 't1') != signed_bytes({'a': 1}, 't2')
    # wire format unchanged: same field name and length as utcnow().isoformat()
    assert len(generation_timestamp()) in (19, 26)


# ---------------------------------------------------------- centralized PKI

def test_centralized_replay_rejected(central):
    signed = central.sign_message("A", make_bsm(1))
    assert central.verify_message(signed)[0] is True
    assert central.verify_message(json.loads(json.dumps(signed)))[0] is False


def test_centralized_stale_rejected(central, monkeypatch):
    monkeypatch.setattr(central_mod, 'generation_timestamp', lambda: _iso(-5.0), raising=False)
    assert central.verify_message(central.sign_message("A", make_bsm(2)))[0] is False


def test_centralized_altered_timestamp_rejected(central):
    signed = central.sign_message("A", make_bsm(3))
    assert central.verify_message(dict(signed, timestamp=_iso(+0.05)))[0] is False


# ----------------------------------------------------- PolicyFreshness unit

def test_replay_cache_is_bounded():
    now = [1000.0]
    p = FreshnessPolicy(replay_cache_size=3, clock=lambda: now[0])
    for i in range(10):
        p.accept('s', str(i).encode(), now[0])
    assert len(p) == 3
    assert p.evicted_live == 7
    # expired entries are dropped on the next insert
    now[0] += 10.0
    p.accept('s', b'new', now[0])
    assert len(p) == 1


def test_window_edges():
    now = 1000.0
    p = FreshnessPolicy(replay_cache=False, clock=lambda: now)
    assert p.check(now - 0.99, 's', b'') is None
    assert p.check(now - 1.01, 's', b'') is not None
    assert p.check(now + 0.09, 's', b'') is None
    assert p.check(now + 0.11, 's', b'') is not None
    assert p.check('not a time', 's', b'') is not None
    assert p.check(None, 's', b'') is not None


# --------------------------------------------- experiment adapter (benchmark)

def test_experiment_adapter_configures_identical_policy():
    """The #21 benchmark configures freshness explicitly and identically per backend."""
    import experiment_pki_vs_erc1056 as exp
    a = StandardPKIAdapter()
    c = CentralizedIdentityProvider()
    exp.configure_freshness(a)
    exp.configure_freshness(c)
    assert a.peer.freshness.describe() == c.freshness.describe() == exp.BENCHMARK_FRESHNESS
    assert exp.BENCHMARK_FRESHNESS['enabled'] and exp.BENCHMARK_FRESHNESS['replay_cache']


# --------------------------------------------------------- cv2x_stack (T-9)

def _stack_pair():
    from protocols.cv2x_stack import CV2XStack, CommunicationMode, Position, VehicleState
    ca = VehiclePKI_CA("Stack-CA")
    ids = []
    for vid in ("V001", "V002"):
        m = VehiclePKIIdentity(vid)
        m.generate_keypair()
        m.request_enrollment_certificate(ca)
        m.request_pseudonym_certificates(ca, count=2)
        ids.append(m)
    # MODE_3 (network-assisted) always allocates a resource; MODE_4 sensing
    # needs 100 ms of idle channel first.
    tx = CV2XStack("V001", identity_manager=ids[0], mode=CommunicationMode.MODE_3)
    rx = CV2XStack("V002", identity_manager=ids[1], mode=CommunicationMode.MODE_3)
    pos_tx = Position(latitude=49.2827, longitude=-123.1207, elevation=50.0)
    pos_rx = Position(latitude=49.2828, longitude=-123.1207, elevation=50.0)
    state = VehicleState(vehicle_id="V001", timestamp=datetime.utcnow().isoformat(),
                         position=pos_tx, speed=15.0, heading=90.0, acceleration=0.0)
    return ca, tx, rx, pos_tx, pos_rx, state


def _deliver(tx, rx, pos_tx, pos_rx, state, crl, mutate=None):
    """Send until the PHY delivers a frame; optionally tamper with the bytes."""
    for _ in range(200):
        info = tx.send_bsm(state)
        if not info:
            continue
        if mutate is not None:
            info = mutate(info)
        ok, rx_info = rx.receive_message(info, pos_rx, pos_tx, crl)
        if 'signature_valid' in rx_info:
            return ok, rx_info
    pytest.fail("PHY never delivered a frame")


def _tamper(info):
    key = 'message' if 'message' in info else None
    raw = info[key] if key else None
    assert isinstance(raw, (bytes, bytearray)), sorted(info)
    doc = json.loads(raw.decode())
    doc['message'] = dict(doc['message'], speed=99.9)
    out = dict(info)
    out[key] = json.dumps(doc).encode()
    return out


def test_stack_valid_signature_is_success():
    ca, tx, rx, pos_tx, pos_rx, state = _stack_pair()
    ok, rx_info = _deliver(tx, rx, pos_tx, pos_rx, state, ca.get_crl())
    assert ok is True and rx_info['success'] is True and rx_info['signature_valid'] is True


def test_stack_invalid_signature_is_not_success():
    ca, tx, rx, pos_tx, pos_rx, state = _stack_pair()
    ok, rx_info = _deliver(tx, rx, pos_tx, pos_rx, state, ca.get_crl(), mutate=_tamper)
    assert rx_info['signature_valid'] is False
    assert ok is False
    assert rx_info['success'] is False
    assert rx.get_statistics()['verification_failures'] == 1


def test_scenario_does_not_count_invalid_as_success(monkeypatch, capsys):
    """basic_v2v_scenario: messages failing verification are not 'successful receptions'."""
    sys.path.insert(0, os.path.join(ROOT, 'scenarios'))
    import basic_v2v_scenario as scen
    monkeypatch.setattr(VehiclePKIIdentity, 'verify_message',
                        lambda self, signed, crl, ca_certificate=None: (False, 0.1))
    metrics = scen.run_basic_v2v_scenario(use_identity=True, num_vehicles=2, simulation_time=1)
    assert metrics['total_transmissions'] > 0
    assert metrics['successful_receptions'] == 0
    assert metrics.get('rejected_messages', 0) > 0


# ----------------------------------------------------- SUMO layers (T-9)

@pytest.fixture(scope='module')
def sumo():
    sys.path.insert(0, os.path.join(ROOT, 'sumo'))
    import sumo_identity_integration as module
    return module


def _sumo_bsm(t):
    return {"msg_type": "BSM", "seq": 1, "sender": "v", "timestamp": t,
            "position": [1.0, 2.0], "speed": 20.0, "heading": 90.0, "emergency": False}


@pytest.mark.parametrize('kind', ['ssi', 'pki'])
def test_sumo_layer_checks_signed_timestamp_against_clock(sumo, kind):
    now = [10.0]
    if kind == 'ssi':
        layer = sumo.SSIIdentityLayer(clock=lambda: now[0])
        layer.enroll("v", "5YJ3E1EA0PF123456", "Tesla", "M3", 2024)
    else:
        layer = sumo.PKIIdentityLayer(clock=lambda: now[0])
        layer.enroll("v")
    fresh, _ = layer.sign("v", _sumo_bsm(10.0))
    assert layer.verify("rx", fresh)[0] is True
    stale, _ = layer.sign("v", _sumo_bsm(5.0))
    assert layer.verify("rx", stale)[0] is False
    # altering the signed timestamp to "now" breaks the signature
    altered = dict(stale, message=dict(stale['message'], timestamp=10.0))
    assert layer.verify("rx", altered)[0] is False
    # the clock moves on: the formerly fresh message is now stale
    now[0] = 12.0
    assert layer.verify("rx2", fresh)[0] is False


def test_sumo_attack_tests_include_stale(sumo, tmp_path):
    sim = sumo.SUMOIdentityIntegration(simulation_mode=True, num_vehicles=10,
                                       results_path=tmp_path / "out.json")
    sim.start_sumo()
    sim._sim_now = 3.0
    for vid in sim.mobility.vehicle_ids():
        sim.assign_vehicle_identity(vid)
        sim.vehicle_states[vid] = sim.get_vehicle_state(vid)
    sim.run_attack_tests(3.0)
    assert sim.attack_results['stale_ssi_rejected'] is True
    assert sim.attack_results['stale_pki_rejected'] is True


# --------------------------------------------------------- ERC-1056 (chain)

@pytest.fixture(scope='module')
def erc(rpc_url):
    from identity.erc1056_provider import ERC1056Provider
    p = ERC1056Provider(rpc_url)
    address = deploy(p.w3, p.account, load_artifact('ERC1056Registry'))
    p._load_contract(address)
    p.contract_address = address
    vid = f"T9-{time.time_ns()}"
    p.fund_vehicle_account(vid, 10 ** 18)
    p.register_vehicle(vid)
    return p, vid


def test_erc1056_default_policy_on(erc):
    p, _ = erc
    assert p.freshness.describe() == FreshnessPolicy().describe()


def test_erc1056_replay_rejected(erc):
    p, vid = erc
    signed = p.sign_message(vid, make_bsm(1))
    assert p.verify_message(signed)[0] is True
    assert p.verify_message(json.loads(json.dumps(signed)))[0] is False


def test_erc1056_stale_rejected(erc, monkeypatch):
    import identity.erc1056_provider as erc_mod
    p, vid = erc
    monkeypatch.setattr(erc_mod, 'generation_timestamp', lambda: _iso(-5.0), raising=False)
    assert p.verify_message(p.sign_message(vid, make_bsm(2)))[0] is False


def test_erc1056_altered_timestamp_rejected(erc):
    p, vid = erc
    signed = p.sign_message(vid, make_bsm(3))
    assert p.verify_message(dict(signed, timestamp=_iso(+0.05)))[0] is False
    assert p.verify_message(signed)[0] is True


def test_erc1056_stale_rejected_before_any_rpc(erc, monkeypatch):
    """Freshness is checked first: a stale packet costs no chain round trip."""
    import identity.erc1056_provider as erc_mod
    from experiment_pki_vs_erc1056 import RPCCounter
    p, vid = erc
    monkeypatch.setattr(erc_mod, 'generation_timestamp', lambda: _iso(-5.0), raising=False)
    stale = p.sign_message(vid, make_bsm(4))
    rc = RPCCounter(p.w3)
    try:
        assert p.verify_message(stale)[0] is False
        assert rc.count == 0, rc.methods
    finally:
        p.w3.provider.make_request = rc._orig
        if hasattr(p.w3.provider, '_request_func_cache'):
            p.w3.provider._request_func_cache = (None, None)
