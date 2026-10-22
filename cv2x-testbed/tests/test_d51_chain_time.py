"""
Defect D51 (WM-1 audit U-F2; WM-2 C0): key validity must be decided in chain time.

Before the fix, `_ValidityClock` trusted the verifier's wall clock whenever a
key's validTo lay more than CLOCK_SKEW_S (900 s) from it. A revocation sets
validTo = block.timestamp, so on a chain running more than 15 minutes ahead of
the verifier (or a test chain advanced with evm_increaseTime) the revoked key
looked valid and kept verifying messages. Both tests failed on the code before
the fix (after-action report 16).

The on-chain test advances the node's clock; on a shared node that is
permanent, which is the reused-node condition the auditor reported.
"""

import itertools
import time

import pytest
from cryptography.hazmat.primitives import serialization
from web3 import Web3

from conftest import deploy, load_artifact
from identity.erc1056_provider import CLOCK_SKEW_S, ERC1056Provider
from identity.freshness import FreshnessPolicy

_ids = itertools.count()
AHEAD_S = 2000   # chain ahead of the verifier by more than CLOCK_SKEW_S


@pytest.fixture(scope='module')
def provider(rpc_url):
    p = ERC1056Provider(rpc_url)
    address = deploy(p.w3, p.account, load_artifact('ERC1056Registry'))
    p._load_contract(address)
    p.contract_address = address
    p.freshness = FreshnessPolicy(max_age_s=1e9)   # message age is not under test here
    chain = int(p.w3.eth.get_block('latest')['timestamp'])
    lead = chain - int(time.time())
    if lead < AHEAD_S:
        p.w3.provider.make_request('evm_increaseTime', [AHEAD_S - lead + 5])
        p.w3.provider.make_request('evm_mine', [])
    return p


def test_revoked_key_rejected_when_chain_runs_ahead_of_the_verifier(provider):
    assert int(provider.w3.eth.get_block('latest')['timestamp']) - int(time.time()) > CLOCK_SKEW_S
    vid = f"D51-VEH-{time.time_ns()}-{next(_ids)}"
    provider.fund_vehicle_account(vid, 10 ** 18)
    provider.register_vehicle(vid)
    before = provider.sign_message(vid, {'msgID': 'BSM', 'speed': 10.0})
    assert provider.verify_message(before)[0] is True

    key = provider.vehicles[vid]['public_key'].public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    provider._send_tx(provider.contract.functions.revokeAttribute(
        Web3.to_checksum_address(provider.vehicles[vid]['address']),
        provider.KEY_ATTRIBUTE_NAME, key), provider.vehicle_account(vid), 200000)

    data, _ = provider.resolve_identity(vid)
    assert data['public_key'] is None, "a key revoked in chain time resolved as valid (D51)"
    assert provider.verify_message(provider.sign_message(vid, {'msgID': 'BSM', 'speed': 11.0}))[0] is False


def test_probe_margin_is_measured_in_chain_time():
    """Chain 2,000 s ahead; a cached key expiring 300 s from chain time is inside the 900 s margin."""
    p = object.__new__(ERC1056Provider)
    p._chain_offset_s = AHEAD_S
    wall = int(time.time())
    cached = {'last_changed': 7, 'is_revoked': False, 'owner': '0xabc',
              'public_key_valid_to': wall + AHEAD_S + 300}
    assert p._probe_unchanged(cached, ('0xabc', 7, False, 0)) is False
    cached['public_key_valid_to'] = wall + AHEAD_S + 10 * CLOCK_SKEW_S
    assert p._probe_unchanged(cached, ('0xabc', 7, False, 0)) is True
