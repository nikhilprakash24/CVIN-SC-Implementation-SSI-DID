"""
One-call refresh for freshness-k (after-action report 05, stream G-K):
ERC1056Provider(refresh_every=k, refresh_mode='probe') refreshes a cached
sender with ONE getIdentityInfo eth_call and runs the full resolution only
when the identity's owner / `changed` block / revoked flag moved.

Offline tests pin the schedule with a stubbed registry; on-chain tests (Hardhat
node at $CV2X_TEST_RPC_URL, skipped only when none answers) check that an
unchanged refresh is exactly one eth_call, and that revokeIdentity, a key
rotation (updateVehicleKey) and an attribute revocation are all detected at the
next refresh, within the same k - 1 staleness bound as the full mode.
"""

import itertools
import time

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from web3 import Web3

from conftest import deploy, load_artifact
from experiment_pki_vs_erc1056 import RPCCounter, make_bsm
from experiment_freshness_k import predicted_after
from identity.base import IdentityProvider, IdentityType
from identity.erc1056_provider import ERC1056Provider
from identity.freshness import FreshnessPolicy

CHAIN = 31337
_seq = itertools.count(10 ** 6)


# ---------------------------------------------------------------- offline --
class _Chain:
    """Stub registry: per-address (owner, changed, revoked) and key; counts calls."""

    def __init__(self):
        self.state = {}
        self.keys = {}
        self.probes = []
        self.resolutions = []

    def bump(self, address, revoked=None):
        owner, changed, rev = self.state[address]
        self.state[address] = (owner, changed + 1, rev if revoked is None else revoked)

    def probe(self, address):
        self.probes.append(address)
        owner, changed, rev = self.state[address]
        return owner, changed, rev, 0

    def resolve(self, address, identity_info=None):
        self.resolutions.append((address, identity_info is not None))
        owner, changed, rev = identity_info[:3] if identity_info is not None else self.state[address]
        return {'address': address, 'owner': owner, 'last_changed': changed, 'is_revoked': rev,
                'public_key': self.keys[address], 'public_key_valid_to': 2 ** 255}, 1.0


def _offline(k, mode='probe'):
    p = object.__new__(ERC1056Provider)
    IdentityProvider.__init__(p, IdentityType.ERC1056_DID)
    p._chain_id = CHAIN
    p.freshness = FreshnessPolicy(max_age_s=60.0)
    p.vehicles = {}
    p.set_refresh_every(k, mode)
    chain = _Chain()
    p.resolve_identity_from_address = chain.resolve
    p._probe_identity_info = chain.probe
    return p, chain


def _add_sender(p, chain, n):
    key = ec.generate_private_key(ec.SECP256K1())
    address = Web3.to_checksum_address('0x' + f'{n:040x}')
    vid = f'S{n}'
    p.vehicles[vid] = {'did': f'did:ethr:0x{CHAIN:x}:{address}', 'private_key': key, 'address': address}
    chain.keys[address] = key.public_key().public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint).hex()
    chain.state[address] = (address, 1, False)
    return vid, address


def _verify(p, vid):
    return p.verify_message(p.sign_message(vid, make_bsm(next(_seq))))[0]


def test_default_mode_is_full():
    p = object.__new__(ERC1056Provider)
    IdentityProvider.__init__(p, IdentityType.ERC1056_DID)
    p.set_refresh_every(5)
    assert p.refresh_mode == 'full'
    with pytest.raises(ValueError):
        p.set_refresh_every(5, 'cheap')


@pytest.mark.parametrize('k,n_msgs', [(1, 12), (5, 25), (25, 75)])
def test_probe_schedule_unchanged_identity(k, n_msgs):
    """One full resolution at first contact; every later refresh is a probe only."""
    p, chain = _offline(k)
    vid, _ = _add_sender(p, chain, 1)
    assert all(_verify(p, vid) for _ in range(n_msgs))
    refreshes = n_msgs if k == 1 else n_msgs // k
    assert p.chain_refreshes == refreshes
    assert p.full_resolutions == 1 and len(chain.resolutions) == 1
    assert p.chain_probes == refreshes - 1 and len(chain.probes) == refreshes - 1
    assert p.cache_hits == n_msgs - refreshes


def test_probe_change_triggers_full_resolution_reusing_probe():
    p, chain = _offline(3)
    vid, addr = _add_sender(p, chain, 2)
    for _ in range(3):
        assert _verify(p, vid)
    chain.bump(addr)                       # e.g. an attribute write
    assert _verify(p, vid)                 # refresh: probe saw the move -> full resolution
    assert p.full_resolutions == 2
    assert chain.resolutions[-1] == (addr, True)   # the probe's getIdentityInfo was reused


def test_probe_ignores_nothing_when_key_nears_expiry():
    """Time-based expiry does not move `changed`: a key near validTo forces a full resolution."""
    p, chain = _offline(2)
    vid, addr = _add_sender(p, chain, 3)
    assert _verify(p, vid)
    p._sender_state[p.vehicles[vid]['did']][0]['public_key_valid_to'] = int(time.time()) + 10
    assert _verify(p, vid) and _verify(p, vid)
    assert p.full_resolutions == 2 and p.chain_probes == 0


@pytest.mark.parametrize('k', [1, 2, 5, 25])
def test_probe_staleness_bound_offline(k):
    """Revocation seen by the probe: exactly k-1-((m-1) mod k) messages late, never more."""
    p, chain = _offline(k)
    for m_pre in range(1, k + 3):
        vid, addr = _add_sender(p, chain, 100 + 1000 * k + m_pre)
        for _ in range(m_pre):
            assert _verify(p, vid)
        chain.bump(addr, revoked=True)
        accepted = 0
        while _verify(p, vid):
            accepted += 1
            assert accepted <= k
        assert accepted == predicted_after(k, m_pre) <= k - 1
        assert not _verify(p, vid) and not _verify(p, vid)


@pytest.mark.parametrize('k', [1, 5])
def test_probe_mode_runs_freshness_first(k):
    p, chain = _offline(k)
    vid, _ = _add_sender(p, chain, 9)
    signed = p.sign_message(vid, make_bsm(next(_seq)))
    assert p.verify_message(signed)[0] is True
    before = (len(chain.probes), len(chain.resolutions))
    assert p.verify_message(dict(signed))[0] is False
    assert p.freshness.rejected_replay == 1
    assert (len(chain.probes), len(chain.resolutions)) == before


# --------------------------------------------------------------- on chain --
@pytest.fixture(scope='module')
def registry(rpc_url):
    p = ERC1056Provider(rpc_url)
    address = deploy(p.w3, p.account, load_artifact('ERC1056Registry'))
    p._load_contract(address)
    p.contract_address = address
    return rpc_url, address, p


def _chain_sender(signer):
    vid = f"FKP-T-{time.time_ns()}-{next(_seq)}"
    signer.fund_vehicle_account(vid, 10 ** 18)
    signer.register_vehicle(vid)
    return vid


def _chain_verifier(rpc_url, address, k, mode='probe'):
    v = ERC1056Provider(rpc_url, contract_address=address, refresh_every=k, refresh_mode=mode)
    v.freshness = FreshnessPolicy(max_age_s=60.0)
    return v


def _send(verifier, signer, vid):
    return verifier.verify_message(signer.sign_message(vid, make_bsm(next(_seq))))[0]


def test_onchain_probe_matches_contract_call(registry):
    rpc_url, address, signer = registry
    vid = _chain_sender(signer)
    a = Web3.to_checksum_address(signer.vehicles[vid]['address'])
    v = _chain_verifier(rpc_url, address, 1)
    assert v._probe_identity_info(a) == tuple(signer.contract.functions.getIdentityInfo(a).call())


def test_onchain_unchanged_refresh_is_one_eth_call(registry):
    """k = 1, probe mode: after first contact every verify issues exactly one RPC, an eth_call."""
    rpc_url, address, signer = registry
    verifier = _chain_verifier(rpc_url, address, 1)
    counter = RPCCounter(verifier.w3)
    vid = _chain_sender(signer)
    methods = []
    for _ in range(4):
        msg = signer.sign_message(vid, make_bsm(next(_seq)))
        counter.reset()
        assert verifier.verify_message(msg)[0] is True
        methods.append(list(counter.methods))
    assert 'eth_getLogs' in methods[0]
    assert methods[1:] == [['eth_call']] * 3


def test_onchain_full_mode_k1_unchanged(registry):
    """The default (full) mode keeps #21/#32's per-verify pattern: getIdentityInfo + eth_getLogs."""
    rpc_url, address, signer = registry
    verifier = _chain_verifier(rpc_url, address, 1, 'full')
    counter = RPCCounter(verifier.w3)
    vid = _chain_sender(signer)
    for _ in range(2):
        msg = signer.sign_message(vid, make_bsm(next(_seq)))
        counter.reset()
        assert verifier.verify_message(msg)[0] is True
        assert [m for m in counter.methods if m != 'eth_chainId'] == ['eth_call', 'eth_getLogs']


@pytest.mark.parametrize('k,m_pre', [(1, 1), (1, 3), (3, 1), (3, 2), (5, 5)])
def test_onchain_probe_detects_revocation(registry, k, m_pre):
    rpc_url, address, signer = registry
    verifier = _chain_verifier(rpc_url, address, k)
    vid = _chain_sender(signer)
    for _ in range(m_pre):
        assert _send(verifier, signer, vid) is True
    assert signer.revoke_credential(vid) is True
    accepted = 0
    while _send(verifier, signer, vid):
        accepted += 1
        assert accepted <= k
    assert accepted == predicted_after(k, m_pre) <= k - 1
    assert _send(verifier, signer, vid) is False


@pytest.mark.parametrize('k,m_pre', [(1, 2), (4, 1), (4, 3)])
def test_onchain_probe_detects_key_rotation(registry, k, m_pre):
    rpc_url, address, signer = registry
    verifier = _chain_verifier(rpc_url, address, k)
    vid = _chain_sender(signer)
    for _ in range(m_pre):
        assert _send(verifier, signer, vid) is True
    old_key = signer.vehicles[vid]['private_key']
    assert signer.update_credential(vid, {'rotate_key': True})
    stale = 0
    while not _send(verifier, signer, vid):
        stale += 1
        assert stale <= k
    assert stale == predicted_after(k, m_pre)
    new_key = signer.vehicles[vid]['private_key']
    signer.vehicles[vid]['private_key'] = old_key
    assert _send(verifier, signer, vid) is False          # old key no longer accepted
    signer.vehicles[vid]['private_key'] = new_key
    assert verifier.full_resolutions == 2


def test_onchain_probe_detects_attribute_revocation(registry):
    """revokeAttribute on the signing key moves `changed`; the next probe re-resolves and rejects."""
    rpc_url, address, signer = registry
    verifier = _chain_verifier(rpc_url, address, 1)
    vid = _chain_sender(signer)
    assert _send(verifier, signer, vid) is True
    assert _send(verifier, signer, vid) is True
    v = signer.vehicles[vid]
    pub = v['public_key'].public_bytes(serialization.Encoding.X962,
                                       serialization.PublicFormat.UncompressedPoint)
    signer._send_tx(signer.contract.functions.revokeAttribute(
        Web3.to_checksum_address(v['address']), signer.KEY_ATTRIBUTE_NAME, pub),
        signer.vehicle_account(vid), gas=200000)
    assert _send(verifier, signer, vid) is False
