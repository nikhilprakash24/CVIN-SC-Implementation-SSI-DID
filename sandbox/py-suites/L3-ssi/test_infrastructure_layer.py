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


def spat(rsu, t, phase="GREEN", intersection="int_1"):
    return {"msg_type": "SPaT", "rsu": rsu, "intersection": intersection, "phase": phase,
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
    assert all(lay.verify("veh_001", lay.sign("rsu_1", dict(spat("rsu_1", 0.0), seq=i))[0])[0] for i in range(50))
    ok, _, cold, reason = lay.verify("veh_new", lay.sign("rsu_1", spat("rsu_1", 0.0))[0])
    assert not ok and cold and reason == "credential_invalid"


def test_malformed_package_is_a_rejection_not_a_crash(layer):
    lay, _ = layer
    ok, _, _, reason = lay.verify("veh_001", {"sender_did": "x"})
    assert not ok and reason.startswith("error:")


# ---- added after the adversarial review (after-action report 11, findings B-F1, B-F2, B-F4, B-F5) ----

@pytest.fixture
def bound():
    clock = Clock()
    lay = InfrastructureLayer(clock=clock, refresh_every=None)
    lay.enroll("rsu_1", "rsu", ["SPaT", "MAP"], extra={"intersectionId": "int_1"})
    lay.enroll("rsu_2", "rsu", ["SPaT", "MAP"], extra={"intersectionId": "int_2"})
    lay.enroll("ctrl_1", "controller", ["SignalStateUpdate"], extra={"intersectionId": "int_1"})
    return lay, clock


@pytest.mark.parametrize("warm", [False, True])
def test_i2h_cross_intersection_spat_rejected(bound, warm):
    lay, clock = bound
    if warm:
        assert lay.verify("veh", lay.sign("rsu_2", spat("rsu_2", 0.0, intersection="int_2"))[0])[0]
    p, _ = lay.sign("rsu_2", spat("rsu_2", 0.0, phase="RED", intersection="int_1"))
    ok, _, cold, reason = lay.verify("veh", p)
    assert not ok and reason == "binding" and cold is (not warm)


def test_rsu_field_must_name_the_signing_station(bound):
    lay, _ = bound
    p, _ = lay.sign("rsu_2", spat("rsu_1", 0.0, intersection="int_2"))
    assert lay.verify("veh", p)[3] == "binding"


def test_controller_update_bound_to_its_intersection(bound):
    lay, _ = bound
    p, _ = lay.sign("ctrl_1", {"msg_type": "SignalStateUpdate", "intersection": "int_2", "phase": "GREEN", "timestamp": 0.0})
    assert lay.verify("rsu_2", p)[3] == "binding"
    p, _ = lay.sign("ctrl_1", {"msg_type": "SignalStateUpdate", "intersection": "int_1", "phase": "GREEN", "timestamp": 0.0})
    assert lay.verify("rsu_1", p)[0]


def test_i2i_replay_to_same_receiver_rejected_but_broadcast_accepted(bound):
    lay, clock = bound
    p, _ = lay.sign("rsu_1", spat("rsu_1", 0.0))
    assert lay.verify("veh_a", p)[0]
    assert lay.verify("veh_b", p)[0]          # the same broadcast at a second receiver is not a replay
    clock.t = 0.9
    ok, _, cold, reason = lay.verify("veh_a", p)
    assert not ok and not cold and reason == "replay"


def test_replay_of_a_rejected_message_is_not_recorded(bound):
    lay, _ = bound
    p, _ = lay.sign("rsu_1", spat("rsu_1", 0.0))
    good_sig = p["signature"]
    p["signature"] = Account.sign_message(signable(p["message"]), Account.create().key).signature.hex()
    assert lay.verify("veh", p)[3] == "wrong_key"
    p["signature"] = good_sig                 # a forgery must not pre-poison the replay cache
    assert lay.verify("veh", p)[0]


def test_i2j_future_timestamp_rejected(bound):
    lay, _ = bound
    p, _ = lay.sign("rsu_1", spat("rsu_1", 0.5))
    assert lay.verify("veh", p)[3] == "future"
    p, _ = lay.sign("rsu_1", spat("rsu_1", 0.09))   # inside the 0.1 s skew allowance
    assert lay.verify("veh", p)[0]


def test_warm_not_permitted_rejected(bound):
    lay, _ = bound
    assert lay.verify("veh", lay.sign("rsu_1", dict(spat("rsu_1", 0.0), msg_type="MAP"))[0])[0]
    p, _ = lay.sign("rsu_1", {"msg_type": "TimingPlan", "intersection": "int_1", "timestamp": 0.0})
    ok, _, cold, reason = lay.verify("veh", p)
    assert not ok and not cold and reason == "not_permitted"


def test_warm_stale_rejected(bound):
    lay, clock = bound
    assert lay.verify("veh", lay.sign("rsu_1", spat("rsu_1", 0.0))[0])[0]
    clock.t = 10.0
    ok, _, cold, reason = lay.verify("veh", lay.sign("rsu_1", spat("rsu_1", 5.0))[0])
    assert not ok and not cold and reason == "stale"


def test_subject_mismatch_rejected(bound):
    lay, _ = bound
    p, _ = lay.sign("rsu_1", spat("rsu_1", 0.0))
    p["sender_did"] = lay.stations["rsu_2"]["did"]   # rsu_1's credential presented under rsu_2's DID
    assert lay.verify("veh", p)[3] == "subject_mismatch"


def test_missing_credential_rejected(bound):
    lay, _ = bound
    p, _ = lay.sign("rsu_1", spat("rsu_1", 0.0))
    del p["credential"]
    assert lay.verify("veh", p)[3] == "no_credential"


def test_warm_path_rechecks_expiry(bound, monkeypatch):
    lay, _ = bound
    assert lay.verify("veh", lay.sign("rsu_1", spat("rsu_1", 0.0))[0])[0]
    import infrastructure_layer as il
    monkeypatch.setattr(il.time, "time", lambda: 4.0e9)   # year 2096, after the 365-day validity
    ok, _, cold, reason = lay.verify("veh", lay.sign("rsu_1", spat("rsu_1", 0.0, phase="RED"))[0])
    assert not ok and not cold and reason == "expired"


def test_unhashable_sender_did_is_a_rejection_not_a_crash(bound):
    lay, _ = bound
    p, _ = lay.sign("rsu_1", spat("rsu_1", 0.0))
    p["sender_did"] = ["a"]
    ok, _, _, reason = lay.verify("veh", p)
    assert not ok and reason.startswith("error:")


@pytest.mark.parametrize("k", [5, 25])
def test_i3_recheck_happens_on_the_kth_message_not_earlier(k):
    """Lower bound to go with the k-1 upper bound: a revoked signer is still accepted until its
    k-th message after caching, so a verifier that re-checks too often (or never) fails here."""
    clock = Clock()
    lay = InfrastructureLayer(clock=clock, refresh_every=k)
    lay.enroll("rsu_1", "rsu", ["SPaT"])
    assert lay.verify("veh", lay.sign("rsu_1", spat("rsu_1", 0.0))[0])[0]   # cold: caches, seen = 0
    lay.revoke("rsu_1")
    results = [lay.verify("veh", lay.sign("rsu_1", dict(spat("rsu_1", 0.0), seq=i))[0]) for i in range(k)]
    assert all(r[0] for r in results[:k - 1])
    assert results[k - 1][3] == "revoked"


# ---- added at the close of WM-1 (after-action report 12, audit brief 2 finding F1): tests the
# ---- pass-11 mutation set did not demand. Each kills a mutant that survived the 31 tests above.

def test_warm_replay_rejected(bound):
    """Replay of a message accepted on the WARM path (mutant: replay cache filled on cold path only)."""
    lay, clock = bound
    assert lay.verify("veh", lay.sign("rsu_1", spat("rsu_1", 0.0))[0])[0]           # cold
    p, _ = lay.sign("rsu_1", spat("rsu_1", 0.0, phase="RED"))
    ok, _, cold, _ = lay.verify("veh", p)
    assert ok and not cold                                                          # warm accept
    ok, _, cold, reason = lay.verify("veh", p)
    assert not ok and not cold and reason == "replay"


@pytest.mark.parametrize("age, ok_expected", [(1.0, True), (1.001, False)])
def test_freshness_age_boundary(bound, age, ok_expected):
    """Exactly max_age (1.0 s) is fresh; just past it is stale (mutant: > becomes >=)."""
    lay, clock = bound
    clock.t = 10.0
    ok, _, _, reason = lay.verify("veh", lay.sign("rsu_1", spat("rsu_1", 10.0 - age))[0])
    assert ok is ok_expected and (ok or reason == "stale")


@pytest.mark.parametrize("ahead, ok_expected", [(0.1, True), (0.101, False)])
def test_freshness_future_boundary(bound, ahead, ok_expected):
    """Exactly max_future (0.1 s) ahead is accepted; just past it is 'future' (mutant: > becomes >=)."""
    lay, clock = bound
    clock.t = 0.0
    ok, _, _, reason = lay.verify("veh", lay.sign("rsu_1", spat("rsu_1", ahead))[0])
    assert ok is ok_expected and (ok or reason == "future")


def test_expired_signer_dropped_from_cache(bound, monkeypatch):
    """After an 'expired' rejection the signer is no longer cached: the next message is cold
    (mutant: the expiry branch keeps the cache entry)."""
    lay, _ = bound
    assert lay.verify("veh", lay.sign("rsu_1", spat("rsu_1", 0.0))[0])[0]
    import infrastructure_layer as il
    real = il.time.time
    monkeypatch.setattr(il.time, "time", lambda: 4.0e9)
    assert lay.verify("veh", lay.sign("rsu_1", spat("rsu_1", 0.0, phase="RED"))[0])[3] == "expired"
    monkeypatch.setattr(il.time, "time", real)
    ok, _, cold, _ = lay.verify("veh", lay.sign("rsu_1", spat("rsu_1", 0.0, phase="YELLOW"))[0])
    assert ok and cold
