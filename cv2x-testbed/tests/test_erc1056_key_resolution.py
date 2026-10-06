"""
Review 02, T-2 and T-5 (on-chain; needs a Hardhat node, see conftest.py).

T-2 (reviewer PoC poc_erc1056_revoke_attr.py): the old resolver walked the
change chain backwards and returned the first still-valid key it met, so the
owner's `revokeAttribute` event (validTo = block.timestamp) was skipped and the
older "set" event for the same key was returned: a revoked key kept verifying.
The fixed resolver collects the events and replays them forward in
(block, logIndex) order; the newest event per (name, value) wins and a
validTo <= now removes the pair.

T-5 (reviewer PoC poc_erc_redundant_rpc.py): verify_message made a second
`isRevoked` eth_call although `getIdentityInfo` already returns the flag.

No sleeps: the revocation must be recognised even though a Hardhat node's
block timestamps run ahead of the wall clock.
"""

import itertools
import time

import pytest
from cryptography.hazmat.primitives import serialization
from web3 import Web3

from conftest import deploy, load_artifact
from experiment_pki_vs_erc1056 import RPCCounter, make_bsm
from identity.erc1056_provider import ERC1056Provider
from identity.freshness import FreshnessPolicy

_ids = itertools.count()


@pytest.fixture(scope='module')
def provider(rpc_url):
    p = ERC1056Provider(rpc_url)
    address = deploy(p.w3, p.account, load_artifact('ERC1056Registry'))
    p._load_contract(address)
    p.contract_address = address
    # These tests are about key resolution (T-2/T-5). Give the T-9 freshness
    # window head-room over the on-chain transactions between sign and verify,
    # so a rejection below can only come from key state, not from age. The
    # replay cache stays on; no test re-verifies a message it already accepted.
    p.freshness = FreshnessPolicy(max_age_s=60.0)
    return p


@pytest.fixture
def vid(provider):
    v = f"T2-VEH-{time.time_ns()}-{next(_ids)}"
    provider.fund_vehicle_account(v, 10 ** 18)
    provider.register_vehicle(v)
    return v


def _key_bytes(provider, vid):
    return provider.vehicles[vid]['public_key'].public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)


def _revoke_attr(provider, vid, key_bytes):
    provider._send_tx(provider.contract.functions.revokeAttribute(
        Web3.to_checksum_address(provider.vehicles[vid]['address']),
        provider.KEY_ATTRIBUTE_NAME, key_bytes), provider.vehicle_account(vid), 200000)


def _set_attr(provider, vid, key_bytes, validity=31536000):
    provider._send_tx(provider.contract.functions.setAttribute(
        Web3.to_checksum_address(provider.vehicles[vid]['address']),
        provider.KEY_ATTRIBUTE_NAME, key_bytes, validity), provider.vehicle_account(vid), 200000)


def test_revoked_key_no_longer_verifies(provider, vid):
    """The PoC: set key, revoke key -> verify with the revoked key fails."""
    signed = provider.sign_message(vid, {'msgID': 'BSM', 'speed': 13.9})
    # Signed with the key before its revocation, verified after it. A distinct
    # message from `signed`, so the T-9 replay cache cannot be the reason.
    signed_before_revoke = provider.sign_message(vid, {'msgID': 'BSM', 'speed': 14.0})
    assert provider.verify_message(signed)[0] is True

    kb = _key_bytes(provider, vid)
    _revoke_attr(provider, vid, kb)

    data, _ = provider.resolve_identity(vid)
    assert data['public_key'] is None, "resolver returned a key its owner revoked"
    assert provider.verify_message(signed_before_revoke)[0] is False
    assert provider.freshness.rejected_replay == 0
    assert provider.verify_message(provider.sign_message(vid, make_bsm(1)))[0] is False


def test_rotation_newest_key_wins(provider, vid):
    old_signed = provider.sign_message(vid, make_bsm(2))
    assert provider.update_credential(vid, {'rotate_key': True}) is True
    new_signed = provider.sign_message(vid, make_bsm(3))
    data, _ = provider.resolve_identity(vid)
    assert data['public_key'] == _key_bytes(provider, vid).hex()
    assert data['resolution_hops'] == 2
    assert provider.verify_message(new_signed)[0] is True
    assert provider.verify_message(old_signed)[0] is False


def test_revoking_an_older_key_leaves_newer_key(provider, vid):
    old_kb = _key_bytes(provider, vid)
    provider.update_credential(vid, {'rotate_key': True})
    _revoke_attr(provider, vid, old_kb)
    assert provider.verify_message(provider.sign_message(vid, make_bsm(4)))[0] is True


def test_reset_after_revoke_restores_key(provider, vid):
    """Newest event per (name, value) wins: set -> revoke -> set is valid again."""
    kb = _key_bytes(provider, vid)
    _revoke_attr(provider, vid, kb)
    assert provider.verify_message(provider.sign_message(vid, make_bsm(5)))[0] is False
    _set_attr(provider, vid, kb)
    assert provider.verify_message(provider.sign_message(vid, make_bsm(6)))[0] is True


def test_revoked_identity_rejected(provider, vid):
    signed = provider.sign_message(vid, make_bsm(7))
    assert provider.revoke_credential(vid) is True
    assert provider.verify_message(signed)[0] is False


def test_revoked_flag_rejects_even_when_a_key_resolves(provider, vid):
    """
    Exercises the `is_revoked` check itself (Pass 2 re-review, M3).

    In the test above `DIDRevoked` (no previousChange) cuts the event chain,
    so no key resolves and verify fails whether or not the revoked flag is
    checked. Here a key rotation and the revocation are mined in the SAME
    block: `changed` points at that block, its DIDAttributeChanged event
    carries previousChange, so the new key DOES resolve, and only the
    registry's revoked flag (from getIdentityInfo) can reject the message.
    """
    from cryptography.hazmat.primitives.asymmetric import ec

    w3 = provider.w3
    acct = provider.vehicle_account(vid)
    identity = Web3.to_checksum_address(provider.vehicles[vid]['address'])
    new_key = ec.generate_private_key(ec.SECP256K1())
    new_pub = new_key.public_key().public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    nonce = w3.eth.get_transaction_count(acct.address)
    base = {'from': acct.address, 'gas': 200000, 'gasPrice': w3.eth.gas_price}
    txs = [
        provider.contract.functions.updateVehicleKey(identity, new_pub).build_transaction(
            dict(base, nonce=nonce)),
        provider.contract.functions.revokeIdentity(identity).build_transaction(
            dict(base, nonce=nonce + 1)),
    ]
    w3.provider.make_request('evm_setAutomine', [False])
    try:
        hashes = [w3.eth.send_raw_transaction(provider._raw_tx(acct.sign_transaction(t)))
                  for t in txs]
        w3.provider.make_request('evm_mine', [])
    finally:
        w3.provider.make_request('evm_setAutomine', [True])
    receipts = [w3.eth.wait_for_transaction_receipt(h) for h in hashes]
    assert [r.status for r in receipts] == [1, 1]
    assert receipts[0].blockNumber == receipts[1].blockNumber

    provider.vehicles[vid]['private_key'] = new_key
    provider.vehicles[vid]['public_key'] = new_key.public_key()
    data, _ = provider.resolve_identity(vid)
    assert data['public_key'] == new_pub.hex(), "precondition: a key must still resolve"
    assert data['is_revoked'] is True
    assert provider.verify_message(provider.sign_message(vid, make_bsm(17)))[0] is False


def test_verify_uses_no_isRevoked_call(provider, vid):
    """T-5: one eth_call (getIdentityInfo) + one eth_getLogs (+ web3's eth_chainId)."""
    rc = RPCCounter(provider.w3)
    try:
        for i in range(3):
            signed = provider.sign_message(vid, make_bsm(10 + i))
            rc.reset()
            assert provider.verify_message(signed)[0] is True
            registry = [m for m in rc.methods if m != 'eth_chainId']
            assert registry == ['eth_call', 'eth_getLogs'], rc.methods
    finally:
        provider.w3.provider.make_request = rc._orig
        if hasattr(provider.w3.provider, '_request_func_cache'):
            provider.w3.provider._request_func_cache = (None, None)


def test_abi_loads_independent_of_cwd(provider, tmp_path, monkeypatch):
    """T-12: the event ABI is found from any working directory."""
    monkeypatch.chdir(tmp_path)
    p = ERC1056Provider(provider.w3.provider.endpoint_uri, contract_address=provider.contract_address)
    assert hasattr(p.contract.events, 'DIDAttributeChanged')
