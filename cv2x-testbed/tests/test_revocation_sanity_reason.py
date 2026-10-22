"""
Review 02 Pass 3 Low (#21 sanity check): `verify_after_revocation_is_false`
must hold BECAUSE the identity is revoked, not merely because verify failed.

Before the fix the check was `verify(signed_before) is False`. ERC-1056 checks
freshness before revocation, so a > 1 s gap between signing and the check (a
slow node, a long revoke) made the check pass on staleness alone. The test
`test_sanity_check_not_satisfied_by_staleness` replays exactly that: the
"sanity" revocation is replaced by a 5 s clock jump, so verify fails as stale
and the identity is NOT revoked. The old check reported True; the new one
reports False.
"""

import time

import pytest

from conftest import deploy, load_artifact
import experiment_pki_vs_erc1056 as exp
from experiment_pki_vs_erc1056 import (Backend, StandardPKIAdapter, configure_freshness,
                                       make_bsm, rejected_for_revocation, run_backend)
from identity.centralized_provider import CentralizedIdentityProvider
from identity.freshness import REASON_REVOKED


def _verifier(prov):
    return prov.peer if isinstance(prov, StandardPKIAdapter) else prov


class _StaleInsteadOfRevoked:
    """Provider wrapper: the sanity 'revocation' only moves the verifier clock 5 s on."""

    def __init__(self, inner):
        self._inner = inner

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def __setattr__(self, name, value):
        if name == '_inner':
            object.__setattr__(self, name, value)
        else:
            setattr(self._inner, name, value)

    def revoke_credential(self, vehicle_id, reason=""):
        if reason == "sanity":
            _verifier(self._inner).freshness.clock = lambda: time.time() + 5.0
            return True
        return self._inner.revoke_credential(vehicle_id, reason)


def _in_process():
    return [StandardPKIAdapter(), CentralizedIdentityProvider("CVIN-Central-CA")]


@pytest.mark.parametrize('idx', [0, 1], ids=['pki_standard', 'pki_centralized'])
def test_sanity_check_not_satisfied_by_staleness(idx):
    prov = _in_process()[idx]
    configure_freshness(prov)
    out = run_backend(Backend(f'b{idx}', _StaleInsteadOfRevoked(prov), False), n=2, warmup=0,
                      run_tag='stale')
    # verify did fail (stale), but nothing was revoked: the check must not pass
    assert _verifier(prov).last_reject_reason != REASON_REVOKED
    assert out['sanity']['verify_after_revocation_is_false'] is False


@pytest.mark.parametrize('idx', [0, 1], ids=['pki_standard', 'pki_centralized'])
def test_sanity_check_passes_on_real_revocation(idx):
    prov = _in_process()[idx]
    configure_freshness(prov)
    out = run_backend(Backend(f'b{idx}', prov, False), n=2, warmup=0, run_tag='real')
    assert all(out['sanity'].values()), out['sanity']


@pytest.mark.parametrize('idx', [0, 1], ids=['pki_standard', 'pki_centralized'])
def test_reason_recorded_and_accept_path_leaves_it(idx):
    prov = _in_process()[idx]
    prov.register_vehicle("A")
    prov.register_vehicle("B")
    signed_a = prov.sign_message("A", make_bsm(1))
    prov.revoke_credential("A", "t")
    assert rejected_for_revocation(prov, signed_a) is True
    # the accept path does not write the attribute (no added work on a timed verify)
    prov.last_reject_reason = "sentinel"
    assert prov.verify_message(prov.sign_message("B", make_bsm(2)))[0] is True
    assert prov.last_reject_reason == "sentinel"
    # a stale but unrevoked message is rejected for staleness, not revocation
    stale = prov.sign_message("B", make_bsm(3))
    _verifier(prov).freshness.clock = lambda: time.time() + 5.0
    assert rejected_for_revocation(prov, stale) is False
    assert _verifier(prov).last_reject_reason.startswith("stale")


# ------------------------------------------------------------- ERC-1056 (chain)

@pytest.fixture(scope='module')
def erc(rpc_url):
    from identity.erc1056_provider import ERC1056Provider
    p = ERC1056Provider(rpc_url)
    address = deploy(p.w3, p.account, load_artifact('ERC1056Registry'))
    p._load_contract(address)
    p.contract_address = address
    return p


def test_erc1056_revocation_reason(erc):
    p = erc
    tag = time.time_ns()
    a, b = f"RR-A-{tag}", f"RR-B-{tag}"
    for v in (a, b):
        p.fund_vehicle_account(v, 10 ** 18)
        p.register_vehicle(v)
    signed_a = p.sign_message(a, make_bsm(1))
    p.revoke_credential(a, "t")
    assert rejected_for_revocation(p, signed_a) is True
    # staleness (checked before any RPC) is not reported as revocation
    stale = p.sign_message(b, make_bsm(2))
    clock = p.freshness.clock
    p.freshness.clock = lambda: time.time() + 5.0
    try:
        assert rejected_for_revocation(p, stale) is False
        assert p.last_reject_reason.startswith("stale")
    finally:
        p.freshness.clock = clock


def test_erc1056_sanity_check_not_satisfied_by_staleness(erc):
    p = erc
    configure_freshness(p)
    out = run_backend(Backend('erc', _StaleInsteadOfRevoked(p), True), n=2, warmup=0,
                      run_tag=f"stale{time.time_ns()}")
    assert out['sanity']['verify_after_revocation_is_false'] is False
    configure_freshness(p)
