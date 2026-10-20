"""
Freshness-k verifier (after-action report 04, stream F-D; review §5.1;
LATENCY_BUDGET.md §4): ERC1056Provider(refresh_every=k) re-reads a sender's
key/revocation state every k messages per sender.

Offline tests drive verify_message with a stubbed resolver (no chain) and pin
the refresh schedule and the staleness bound; the on-chain tests (Hardhat
node at $CV2X_TEST_RPC_URL, skipped only when none answers) revoke a real
identity mid-stream, and check that a cached verify issues no RPC.
"""

import itertools
import time

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from conftest import deploy, load_artifact
from experiment_pki_vs_erc1056 import RPCCounter, make_bsm
from experiment_freshness_k import derive, p_star, predicted_after, t_eff
from identity.base import IdentityProvider, IdentityType
from identity.erc1056_provider import ERC1056Provider
from identity.freshness import FreshnessPolicy

CHAIN = 31337
_seq = itertools.count()


# ---------------------------------------------------------------- offline --
class _Chain:
    """Stub registry state: per-address revoked flag; counts resolutions."""

    def __init__(self):
        self.revoked = {}
        self.keys = {}
        self.calls = []

    def resolve(self, address):
        self.calls.append(address)
        return {'address': address, 'is_revoked': self.revoked.get(address, False),
                'public_key': self.keys[address]}, 1.0


def _offline(k):
    p = object.__new__(ERC1056Provider)
    IdentityProvider.__init__(p, IdentityType.ERC1056_DID)
    p._chain_id = CHAIN
    p.freshness = FreshnessPolicy(max_age_s=60.0)
    p.vehicles = {}
    p.set_refresh_every(k)
    chain = _Chain()
    p.resolve_identity_from_address = chain.resolve
    return p, chain


def _add_sender(p, chain, n):
    key = ec.generate_private_key(ec.SECP256K1())
    address = '0x' + f'{n:040x}'
    from web3 import Web3
    address = Web3.to_checksum_address(address)
    vid = f'S{n}'
    p.vehicles[vid] = {'did': f'did:ethr:0x{CHAIN:x}:{address}', 'private_key': key, 'address': address}
    chain.keys[address] = key.public_key().public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint).hex()
    return vid, address


def _verify(p, vid):
    return p.verify_message(p.sign_message(vid, make_bsm(next(_seq))))[0]


@pytest.mark.parametrize('k,n_msgs,expected', [(1, 12, 12), (5, 12, 3), (25, 60, 3), (None, 40, 1)])
def test_refresh_schedule(k, n_msgs, expected):
    """Message 1 resolves; 2..k are cached; k+1 resolves again (k=None: once)."""
    p, chain = _offline(k)
    vid, _ = _add_sender(p, chain, 1)
    assert all(_verify(p, vid) for _ in range(n_msgs))
    assert len(chain.calls) == expected
    assert p.chain_refreshes == expected
    assert p.cache_hits == n_msgs - expected


def test_default_is_uncached():
    p, chain = _offline(1)
    assert p.refresh_every == 1
    vid, _ = _add_sender(p, chain, 2)
    for _ in range(4):
        assert _verify(p, vid)
    assert len(chain.calls) == 4 and p._sender_state == {}


def test_refresh_is_per_sender():
    p, chain = _offline(5)
    a, addr_a = _add_sender(p, chain, 3)
    b, addr_b = _add_sender(p, chain, 4)
    for _ in range(5):
        assert _verify(p, a) and _verify(p, b)
    assert chain.calls.count(addr_a) == 1 and chain.calls.count(addr_b) == 1
    assert _verify(p, a)
    assert chain.calls.count(addr_a) == 2 and chain.calls.count(addr_b) == 1


@pytest.mark.parametrize('k', [1, 2, 5, 25])
def test_staleness_bound_offline(k):
    """After a revocation, at most k-1 messages verify, exactly k-1-((m-1) mod k)."""
    p, chain = _offline(k)
    for m_pre in range(1, k + 3):
        vid, addr = _add_sender(p, chain, 100 + 1000 * k + m_pre)
        for _ in range(m_pre):
            assert _verify(p, vid)
        chain.revoked[addr] = True
        accepted = 0
        while _verify(p, vid):
            accepted += 1
            assert accepted <= k, "staleness bound exceeded"
        assert accepted <= k - 1
        assert accepted == predicted_after(k, m_pre)
        assert not _verify(p, vid) and not _verify(p, vid)   # stays rejected


def test_k_infinite_never_sees_revocation():
    p, chain = _offline(None)
    vid, addr = _add_sender(p, chain, 7)
    assert _verify(p, vid)
    chain.revoked[addr] = True
    assert all(_verify(p, vid) for _ in range(30))
    assert len(chain.calls) == 1


@pytest.mark.parametrize('k', [1, 5, None])
def test_freshness_policy_runs_before_cache(k):
    """T-9 is identical across k: a replay is rejected even when the sender is cached."""
    p, chain = _offline(k)
    vid, _ = _add_sender(p, chain, 8)
    signed = p.sign_message(vid, make_bsm(next(_seq)))
    assert p.verify_message(signed)[0] is True
    calls = len(chain.calls)
    assert p.verify_message(dict(signed))[0] is False
    assert p.freshness.rejected_replay == 1
    assert len(chain.calls) == calls          # rejected before any resolution


def test_invalid_k_rejected():
    p, _ = _offline(1)
    with pytest.raises(ValueError):
        p.set_refresh_every(0)


def test_analytic_helpers():
    assert t_eff(0.4, 2.5, 25) == pytest.approx(0.5)
    assert t_eff(0.4, 2.5, None) == 0.4
    assert p_star(0.5, 0.5) == 100 and p_star(18.158, 0.5) == 2
    rows = [{'k': '1', 'median_ms': 10.4, 'mean_ms': 10.5, 'p95_ms': 12.0},
            {'k': '5', 'median_ms': 0.45, 'mean_ms': 2.5, 'p95_ms': 10.0},
            {'k': 'inf', 'median_ms': 0.4, 'mean_ms': 0.41, 'p95_ms': 0.5}]
    d = derive(rows)
    assert d['t_local_ms'] == pytest.approx(0.4) and d['t_chain_ms'] == pytest.approx(10.0)
    k5 = next(e for e in d['per_k'] if e['k'] == '5')
    assert k5['analytic_this_run_ms'] == pytest.approx(2.4)
    assert k5['analytic_latency_budget_ms'] == pytest.approx(0.9)
    assert k5['P*(0.5)_measured_mean'] == 20
    assert d['k_for_Pstar_0.5_ge_100_this_run'] == pytest.approx(100.0)


# --------------------------------------------------------------- on chain --
@pytest.fixture(scope='module')
def registry(rpc_url):
    p = ERC1056Provider(rpc_url)
    address = deploy(p.w3, p.account, load_artifact('ERC1056Registry'))
    p._load_contract(address)
    p.contract_address = address
    return rpc_url, address, p


def _chain_sender(signer):
    vid = f"FK-T-{time.time_ns()}-{next(_seq)}"
    signer.fund_vehicle_account(vid, 10 ** 18)
    signer.register_vehicle(vid)
    return vid


def _chain_verifier(rpc_url, address, k):
    v = ERC1056Provider(rpc_url, contract_address=address, refresh_every=k)
    v.freshness = FreshnessPolicy(max_age_s=60.0)
    return v


@pytest.mark.parametrize('k,m_pre', [(1, 1), (3, 1), (3, 2), (5, 1)])
def test_onchain_revocation_staleness(registry, k, m_pre):
    rpc_url, address, signer = registry
    verifier = _chain_verifier(rpc_url, address, k)
    vid = _chain_sender(signer)
    for _ in range(m_pre):
        assert verifier.verify_message(signer.sign_message(vid, make_bsm(next(_seq))))[0] is True
    assert signer.revoke_credential(vid) is True          # mined before the next verify
    accepted = 0
    while verifier.verify_message(signer.sign_message(vid, make_bsm(next(_seq))))[0]:
        accepted += 1
        assert accepted <= k
    assert accepted == predicted_after(k, m_pre) <= k - 1


def test_onchain_cached_verify_issues_no_rpc(registry):
    rpc_url, address, signer = registry
    verifier = _chain_verifier(rpc_url, address, 4)
    counter = RPCCounter(verifier.w3)
    vid = _chain_sender(signer)
    counts = []
    for _ in range(8):
        msg = signer.sign_message(vid, make_bsm(next(_seq)))
        counter.reset()
        assert verifier.verify_message(msg)[0] is True
        counts.append(counter.count)
    assert counts[0] > 0 and counts[4] > 0
    assert [c for i, c in enumerate(counts) if i % 4] == [0] * 6


def test_onchain_k1_matches_uncached_rpc_pattern(registry):
    """k = 1 keeps #21's per-verify RPC pattern (getIdentityInfo + eth_getLogs, no isRevoked)."""
    rpc_url, address, signer = registry
    verifier = _chain_verifier(rpc_url, address, 1)
    counter = RPCCounter(verifier.w3)
    vid = _chain_sender(signer)
    for _ in range(2):
        msg = signer.sign_message(vid, make_bsm(next(_seq)))
        counter.reset()
        assert verifier.verify_message(msg)[0] is True
        assert [m for m in counter.methods if m != 'eth_chainId'] == ['eth_call', 'eth_getLogs']
