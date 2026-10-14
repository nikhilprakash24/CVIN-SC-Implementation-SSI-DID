"""L3 — verifier v3 (WM-2 step C0; pre-registration amendment A6; defects D37-D42).

Each test names the defect it guards and was run against verifier v2 (commit c7e333f) before the fix,
where it failed (after-action report 16). Chain-free.
"""
import math
import subprocess
import sys
from pathlib import Path

import pytest
from eth_account import Account

SUMO = Path(__file__).resolve().parents[3] / "cv2x-testbed" / "sumo"
sys.path.insert(0, str(SUMO))
from infrastructure_layer import InfrastructureLayer, signable  # noqa: E402


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def spat(t, rsu="rsu_1", intersection="int_1", **extra):
    m = {"msg_type": "SPaT", "rsu": rsu, "intersection": intersection, "phase": "GREEN",
         "time_to_change_s": 12.0, "timestamp": t}
    m.update(extra)
    return m


@pytest.fixture
def layer():
    lay = InfrastructureLayer(clock=Clock(), refresh_every=1)
    lay.enroll("rsu_1", "rsu", ["SPaT", "MAP"], extra={"intersectionId": "int_1"})
    lay.enroll("ctrl_1", "controller", ["SignalStateUpdate"], extra={"intersectionId": "int_1"})
    lay.enroll("rsu_unbound", "rsu", ["SPaT", "MAP"])          # credential without intersectionId
    return lay


def nested(depth):
    v = "leaf"
    for _ in range(depth):
        v = {"n": v}
    return v


# ---------------------------------------------------------------- D37 size and depth
def test_d37_deep_message_rejected_as_malformed(layer):
    m = spat(0.0, payload=nested(200))
    p, _ = layer.sign("rsu_1", m)
    ok, _, _, reason = layer.verify("veh_1", p)
    assert not ok and reason == "malformed"


def test_d37_pathological_depth_is_rejected_not_a_crash(layer):
    p, _ = layer.sign("rsu_1", spat(0.0))
    p["message"] = dict(p["message"], payload=nested(100_000))   # never canonicalised: rejected first
    ok, _, _, reason = layer.verify("veh_1", p)
    assert not ok and reason == "malformed"


def test_d37_too_many_values_rejected(layer):
    m = spat(0.0, payload=list(range(6000)))
    p, _ = layer.sign("rsu_1", m)
    ok, _, _, reason = layer.verify("veh_1", p)
    assert not ok and reason == "malformed"


def test_d37_ordinary_message_still_accepted(layer):
    p, _ = layer.sign("rsu_1", spat(0.0))
    assert layer.verify("veh_1", p)[0]


# ---------------------------------------------------------------- D38 binding fails closed
def test_d38_spat_without_rsu_field_rejected(layer):
    m = spat(0.0)
    del m["rsu"]
    p, _ = layer.sign("rsu_1", m)
    ok, _, _, reason = layer.verify("veh_1", p)
    assert not ok and reason == "binding"


def test_d38_spat_without_rsu_field_rejected_warm(layer):
    assert layer.verify("veh_1", layer.sign("rsu_1", spat(0.0))[0])[0]
    m = spat(0.0, seq=2)
    del m["rsu"]
    ok, _, cold, reason = layer.verify("veh_1", layer.sign("rsu_1", m)[0])
    assert not cold and not ok and reason == "binding"


def test_d38_rsu_credential_without_intersection_claim_rejected(layer):
    p, _ = layer.sign("rsu_unbound", spat(0.0, rsu="rsu_unbound", intersection="int_9"))
    ok, _, _, reason = layer.verify("veh_1", p)
    assert not ok and reason == "binding"


def test_d38_controller_update_without_intersection_rejected(layer):
    p, _ = layer.sign("ctrl_1", {"msg_type": "SignalStateUpdate", "phase": "RED", "timestamp": 0.0})
    ok, _, _, reason = layer.verify("rsu_1", p)
    assert not ok and reason == "binding"


def test_d38_bound_controller_update_accepted(layer):
    p, _ = layer.sign("ctrl_1", {"msg_type": "SignalStateUpdate", "intersection": "int_1", "phase": "RED",
                                 "timestamp": 0.0})
    assert layer.verify("rsu_1", p)[0]


# ---------------------------------------------------------------- D39 refresh_every
@pytest.mark.parametrize("bad", [True, False, 1.5, math.nan, math.inf, 0, -1, "3"])
def test_d39_refresh_every_must_be_a_positive_integer_or_none(bad):
    with pytest.raises((ValueError, TypeError)):
        InfrastructureLayer(refresh_every=bad)


@pytest.mark.parametrize("good", [None, 1, 5, 25])
def test_d39_valid_refresh_every(good):
    assert InfrastructureLayer(refresh_every=good).refresh_every == good


def test_d39_cli_rejects_a_non_integer_k_with_a_parser_error():
    r = subprocess.run([sys.executable, str(SUMO / "sumo_identity_integration.py"), "--simulate", "--rsu",
                        "--refresh-k", "abc", "--results", "/dev/null"], capture_output=True, text=True, cwd=SUMO)
    assert r.returncode == 2 and "--refresh-k" in r.stderr and "Traceback" not in r.stderr


# ---------------------------------------------------------------- D41 DID method and network
@pytest.mark.parametrize("did_form", ["did:ethr:0x5:{a}", "did:web:{a}", "did:ethr:{a}"])
def test_d41_cold_path_checks_did_method_and_network(layer, did_form):
    st = layer.stations["rsu_1"]
    did = did_form.format(a=st["account"].address)
    cred = layer.authority.issue_credential(credential_type="InfrastructureStationCredential", subject_did=did,
                                            claims={"stationId": "rsu_1", "stationKind": "rsu",
                                                    "permittedMessages": ["SPaT"], "intersectionId": "int_1"},
                                            validity_days=365)
    m = spat(0.0)
    p = {"message": m, "sender_did": did, "credential": cred, "identity_type": "infra_vc",
         "signature": Account.sign_message(signable(m), st["account"].key).signature.hex()}
    ok, _, _, reason = layer.verify("veh_1", p)
    assert not ok and reason == "wrong_key"


# ---------------------------------------------------------------- D42 the I2 gate
def test_d42_i2_gate_fails_when_a_warm_variant_ran_cold():
    sys.path.insert(0, str(SUMO))
    from run_infra_stats import i2_failures
    expected = {"i2a_unsigned_spat": "unsigned", "i2b_w_wrong_key_spat_warm": "wrong_key"}
    good = {"seed": 1, "attacks": {"i2a_unsigned_spat": True, "i2b_w_wrong_key_spat_warm": True},
            "attack_reasons": {"i2a_unsigned_spat": {"reason": "unsigned", "cold": True},
                               "i2b_w_wrong_key_spat_warm": {"reason": "wrong_key", "cold": False}}}
    assert i2_failures([good], expected) == []
    bad = {**good, "attack_reasons": {**good["attack_reasons"],
                                      "i2b_w_wrong_key_spat_warm": {"reason": "wrong_key", "cold": True}}}
    assert i2_failures([bad], expected) == [(1, "i2b_w_wrong_key_spat_warm", "ran cold")]
