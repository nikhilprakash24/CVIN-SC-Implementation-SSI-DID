"""
Scenario X1 (toll corridor) end to end against a Hardhat node.

Needs compiled 1_blockchain-identity artifacts (CI compiles them) and the
node fixture from conftest. Asserts outcomes, not latency.
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'scenarios'))

from toll_corridor import TollCorridorScenario, Vehicle, demo_fleet, FEE, CLASS  # noqa: E402


def _run(rpc_url, fleet=None, **kw):
    sc = TollCorridorScenario(rpc_url)
    sc.deploy()
    return sc, sc.run(fleet or demo_fleet(), **kw)


def test_mixed_fleet_admits_valid_and_denies_revoked(rpc_url):
    _, r = _run(rpc_url, revoke_offchain="suspended-5", revoke_onchain="revoked-6")
    ssi, legacy = r["ssi_lane"], r["legacy_lane"]
    assert ssi["vehicles"] == 6 and ssi["admitted"] == 4
    assert ssi["denied"] == {"suspended-5": "vp_invalid", "revoked-6": "onchain_code_7"}
    expected_ssi = (FEE[CLASS["ev"]] + FEE[CLASS["car"]] + FEE[CLASS["truck"]] + FEE[CLASS["emergency"]]) / 1e6
    assert ssi["revenue_cusd"] == expected_ssi
    assert legacy["admitted"] == 2 and legacy["revenue_cusd"] == (FEE[1] + FEE[3]) / 1e6
    assert r["reconciled_revenue_cusd"] == expected_ssi + legacy["revenue_cusd"]


def test_privacy_exposure_differs_by_lane(rpc_url):
    _, r = _run(rpc_url)
    for ids in r["ssi_lane"]["identifiers_exposed"].values():
        assert "plate" not in ids and "vin" not in ids
        assert any(i.startswith("did_address") for i in ids)  # stated linkability, not hidden
    for ids in r["legacy_lane"]["identifiers_exposed"].values():
        assert "plate" in ids


def test_batch_settles_once_and_treasury_matches(rpc_url):
    sc, r = _run(rpc_url)
    assert r["gas"]["settleBatch"] > 0
    assert sc.corridor.functions.treasury().call() == round(r["ssi_lane"]["revenue_cusd"] * 1e6)


def test_endorsement_bound_to_vc_content(rpc_url):
    """A VC edited after the ministry signed its EIP-712 twin no longer matches the anchored digest."""
    sc = TollCorridorScenario(rpc_url)
    sc.deploy()
    v = Vehicle("x", "car", "BC-X-1", "1HGCM82633A000099")
    sc.onboard(v)
    v.endorsement = dict(v.endorsement, credentialHash=b"\x11" * 32)
    from vc_verifier import CredentialVerifier, NonceStore, TrustedIssuerRegistry
    from toll_corridor import LaneReport
    tir = TrustedIssuerRegistry()
    for iss in (sc.ministry, sc.dmv):
        tir.register(iss.issuer_did, iss.address)
    ns = NonceStore()
    ver = CredentialVerifier(revocation_registry=[sc.ministry.revocation_registry, sc.dmv.revocation_registry],
                             trusted_issuers=tir, nonce_store=ns)
    rep = LaneReport()
    assert sc.gate_read(v, ver, ns, rep, ticket_nonce=1) is None
    assert rep.denied["x"] == "vc_endorsement_mismatch"
