"""L3 — infrastructure identity layer (design docs/design/INFRASTRUCTURE_MESSAGING.md;
pre-registration docs/design/INFRASTRUCTURE_PREREG.md). Chain-free: the layer's identities are
did:ethr keys with credentials from the canonical VC layer.

Covers the legitimate SPaT and I2I paths, every pre-registered I2 attack (a)-(g), and the I3
revocation bound for k in {1, 5, 25} and the k = infinity non-stop case.
"""
import sys
from pathlib import Path

import pytest
from eth_account import Account

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "cv2x-testbed" / "sumo"))
from infrastructure_layer import InfrastructureLayer, signable  # noqa: E402


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def spat(rsu, t, phase="GREEN"):
    return {"msg_type": "SPaT", "rsu": rsu, "intersection": "int_1", "phase": phase,
            "time_to_change_s": 12.0, "timestamp": t}


@pytest.fixture
def layer():
    clock = Clock()
    lay = InfrastructureLayer(clock=clock, refresh_every=1)
    lay.enroll("rsu_1", "rsu", ["SPaT", "MAP"], position=(625.0, 510.0))
    lay.enroll("ctrl_1", "controller", ["SignalStateUpdate"])
    lay.enroll("tmc", "tmc", ["TimingPlan"])
    lay.enroll("rsu_maponly", "rsu", ["MAP"])
    return lay, clock


def test_legitimate_spat_cold_then_warm(layer):
    lay, clock = layer
    p, _ = lay.sign("rsu_1", spat("rsu_1", 0.0))
    ok, _, cold, reason = lay.verify("veh_001", p)
    assert ok and cold and reason is None
    clock.t = 0.1
    p, _ = lay.sign("rsu_1", spat("rsu_1", 0.1))
    ok, _, cold, reason = lay.verify("veh_001", p)
    assert ok and not cold


def test_i2i_controller_update_and_timing_plan(layer):
    lay, _ = layer
    p, _ = lay.sign("ctrl_1", {"msg_type": "SignalStateUpdate", "phase": "RED", "timestamp": 0.0})
    assert lay.verify("rsu_1", p)[0]
    p, _ = lay.sign("tmc", {"msg_type": "TimingPlan", "cycle_s": 90, "timestamp": 0.0})
    assert lay.verify("ctrl_1", p)[0]


def test_i2a_unsigned_rejected(layer):
    lay, _ = layer
    p, _ = lay.sign("rsu_1", spat("rsu_1", 0.0))
    p["signature"] = ""
    ok, _, _, reason = lay.verify("veh_001", p)
    assert not ok and reason == "unsigned"


def test_i2b_wrong_key_under_rsu_did_rejected(layer):
    lay, _ = layer
    p, _ = lay.sign("rsu_1", spat("rsu_1", 0.0))
    impostor = Account.create()
    p["signature"] = Account.sign_message(signable(p["message"]), impostor.key).signature.hex()
    ok, _, _, reason = lay.verify("veh_001", p)
    assert not ok and reason == "wrong_key"


def test_i2b_wrong_key_after_warm_cache_rejected(layer):
    lay, _ = layer
    p, _ = lay.sign("rsu_1", spat("rsu_1", 0.0))
    assert lay.verify("veh_001", p)[0]
    impostor = Account.create()
    p2, _ = lay.sign("rsu_1", spat("rsu_1", 0.0, "RED"))
    p2["signature"] = Account.sign_message(signable(p2["message"]), impostor.key).signature.hex()
    ok, _, cold, reason = lay.verify("veh_001", p2)
    assert not ok and not cold and reason == "wrong_key"


def test_i2c_rsu_not_permitted_for_spat_rejected(layer):
    lay, _ = layer
    p, _ = lay.sign("rsu_maponly", spat("rsu_maponly", 0.0))
    ok, _, _, reason = lay.verify("veh_001", p)
    assert not ok and reason == "not_permitted"


def test_i2d_vehicle_credential_cannot_sign_spat(layer):
    lay, _ = layer
    # a vehicle-style credential from an issuer the infrastructure verifier does not trust
    from identity.w3c_verifiable_credentials import CredentialIssuer
    oem = Account.create()
    consortium = CredentialIssuer(f"did:ethr:0x1:{oem.address}", oem.key.hex(), "OEM consortium")
    veh = Account.create()
    did = f"did:ethr:0x1:{veh.address}"
    cred = consortium.issue_credential("V2VSafetyCredential", did, {"authorizedMessages": ["BSM", "DENM"]})
    msg = spat("veh_009", 0.0)
    p = {"message": msg, "sender_did": did, "credential": cred,
         "signature": Account.sign_message(signable(msg), veh.key).signature.hex()}
    ok, _, _, reason = lay.verify("veh_001", p)
    assert not ok and reason == "credential_invalid"


def test_i2e_untrusted_authority_rejected(layer):
    lay, _ = layer
    lay.enroll("rsu_rogue", "rsu", ["SPaT"], issuer=lay.rogue_authority)
    p, _ = lay.sign("rsu_rogue", spat("rsu_rogue", 0.0))
    ok, _, _, reason = lay.verify("veh_001", p)
    assert not ok and reason == "credential_invalid"


def test_i2f_stale_rejected(layer):
    lay, clock = layer
    clock.t = 10.0
    p, _ = lay.sign("rsu_1", spat("rsu_1", 5.0))
    ok, _, _, reason = lay.verify("veh_001", p)
    assert not ok and reason == "stale"


def test_i2g_forged_controller_update_rejected(layer):
    lay, _ = layer
    p, _ = lay.sign("ctrl_1", {"msg_type": "SignalStateUpdate", "phase": "GREEN", "timestamp": 0.0})
    rogue = Account.create()
    p["signature"] = Account.sign_message(signable(p["message"]), rogue.key).signature.hex()
    ok, _, _, reason = lay.verify("rsu_1", p)
    assert not ok and reason == "wrong_key"


def test_controller_cannot_sign_spat(layer):
    lay, _ = layer
    p, _ = lay.sign("ctrl_1", spat("ctrl_1", 0.0))
    ok, _, _, reason = lay.verify("veh_001", p)
    assert not ok and reason == "not_permitted"


@pytest.mark.parametrize("k", [1, 5, 25])
def test_i3_revocation_bound_k_minus_1(k):
    clock = Clock()
    lay = InfrastructureLayer(clock=clock, refresh_every=k)
    lay.enroll("rsu_1", "rsu", ["SPaT"])
    t = 0.0
    for _ in range(7):  # warm the cache to an arbitrary phase of the refresh cycle
        p, _ = lay.sign("rsu_1", spat("rsu_1", t))
        assert lay.verify("veh_001", p)[0]
        t += 0.1
        clock.t = t
    lay.revoke("rsu_1")
    accepted = 0
    for _ in range(3 * k + 5):
        p, _ = lay.sign("rsu_1", spat("rsu_1", t))
        ok = lay.verify("veh_001", p)[0]
        if not ok:
            break
        accepted += 1
        t += 0.1
        clock.t = t
    assert accepted <= k - 1
    # once dropped, the next contact is cold and the credential check rejects it
    p, _ = lay.sign("rsu_1", spat("rsu_1", t))
    ok, _, cold, reason = lay.verify("veh_001", p)
    assert not ok and cold and reason == "credential_invalid"


def test_i3_k_infinity_never_stops_for_cached_receiver_but_new_receiver_rejects():
    clock = Clock()
    lay = InfrastructureLayer(clock=clock, refresh_every=None)
    lay.enroll("rsu_1", "rsu", ["SPaT"])
    p, _ = lay.sign("rsu_1", spat("rsu_1", 0.0))
    assert lay.verify("veh_001", p)[0]
    lay.revoke("rsu_1")
    assert all(lay.verify("veh_001", lay.sign("rsu_1", spat("rsu_1", 0.0))[0])[0] for _ in range(50))
    ok, _, cold, reason = lay.verify("veh_new", lay.sign("rsu_1", spat("rsu_1", 0.0))[0])
    assert not ok and cold and reason == "credential_invalid"


def test_malformed_package_is_a_rejection_not_a_crash(layer):
    lay, _ = layer
    ok, _, _, reason = lay.verify("veh_001", {"sender_did": "x"})
    assert not ok and reason.startswith("error:")
