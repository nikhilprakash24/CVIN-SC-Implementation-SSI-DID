"""
Review 02, T-4: MOBIVIDProvider.verify_message trusted the public key carried
in the message (reviewer PoC poc_mobi_selfkey.py: any unregistered key
verified), and revoke_credential reported success without checking
receipt.status.

Unit tests run without a chain; the last two tests use a Hardhat node
(skipped only when none is reachable, see conftest.py).
"""

import hashlib
import json
import time

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from conftest import deploy, load_artifact
from identity.mobi_vid_provider import MOBIVIDProvider

FAKE_BRAKE = {'msgID': 'BSM', 'speed': 0, 'event': 'fake-hard-brake'}


def _pub_hex(key):
    return key.public_key().public_bytes(serialization.Encoding.X962,
                                         serialization.PublicFormat.UncompressedPoint).hex()


def _sign(key, msg):
    h = hashlib.sha256(json.dumps(msg, sort_keys=True).encode()).digest()
    return key.sign(h, ec.ECDSA(hashes.SHA256())).hex()


@pytest.fixture
def offline():
    """A provider with one registered vehicle record and no chain."""
    p = object.__new__(MOBIVIDProvider)
    p.vehicles = {}
    p.contract = None
    identity = '0x' + 'ab' * 20
    key = ec.generate_private_key(ec.SECP256K1())
    p.vehicles[identity] = {'private_key': key, 'public_key': _pub_hex(key)}
    return p, identity, key


def test_poc_unregistered_attacker_key_rejected(offline):
    """The PoC verbatim: attacker key, attacker-supplied public key, unknown identity."""
    p, _, _ = offline
    k = ec.generate_private_key(ec.SECP256K1())
    pkt = {'message': FAKE_BRAKE, 'signature': _sign(k, FAKE_BRAKE), 'public_key': _pub_hex(k),
           'vehicle_identity': '0x' + '00' * 20}
    assert p.verify_message(pkt)[0] is False


def test_poc_on_bare_instance_rejected():
    """The PoC used object.__new__ with no state at all: must fail closed."""
    p = object.__new__(MOBIVIDProvider)
    k = ec.generate_private_key(ec.SECP256K1())
    pkt = {'message': FAKE_BRAKE, 'signature': _sign(k, FAKE_BRAKE), 'public_key': _pub_hex(k),
           'vehicle_identity': '0x' + '00' * 20}
    assert p.verify_message(pkt)[0] is False


def test_impersonating_registered_vehicle_with_own_key_rejected(offline):
    p, identity, _ = offline
    k = ec.generate_private_key(ec.SECP256K1())
    pkt = {'message': FAKE_BRAKE, 'signature': _sign(k, FAKE_BRAKE), 'public_key': _pub_hex(k),
           'vehicle_identity': identity}
    assert p.verify_message(pkt)[0] is False
    del pkt['public_key']
    assert p.verify_message(pkt)[0] is False


def test_registered_key_accepted_by_identity_and_did(offline):
    p, identity, key = offline
    base = {'message': FAKE_BRAKE, 'signature': _sign(key, FAKE_BRAKE)}
    assert p.verify_message(dict(base, vehicle_identity=identity))[0] is True
    assert p.verify_message(dict(base, vehicle_did=f"did:ethr:0x539:{identity}"))[0] is True
    assert p.verify_message(dict(base, vehicle_identity=identity.upper().replace('0X', '0x')))[0] is True


def test_sign_message_output_verifies(offline):
    p, identity, _ = offline
    p.metrics = type('M', (), {})()
    signed = p.sign_message(identity, FAKE_BRAKE)
    assert signed['vehicle_identity'] == identity
    assert p.verify_message(signed)[0] is True
    signed['message'] = dict(FAKE_BRAKE, speed=50)
    assert p.verify_message(signed)[0] is False


def test_locally_revoked_vehicle_rejected(offline):
    p, identity, key = offline
    p.vehicles[identity]['revoked'] = True
    pkt = {'message': FAKE_BRAKE, 'signature': _sign(key, FAKE_BRAKE), 'vehicle_identity': identity}
    assert p.verify_message(pkt)[0] is False


class _FakeEth:
    def __init__(self, status):
        self.status = status
        self.gas_price = 1

    def get_transaction_count(self, _):
        return 0

    def send_raw_transaction(self, _):
        return b'\x00' * 32

    def wait_for_transaction_receipt(self, _):
        return {'status': self.status, 'gasUsed': 21000}


class _FakeFn:
    def build_transaction(self, tx):
        return dict(tx, to='0x' + '11' * 20, data='0x', chainId=1337)


class _FakeContract:
    class functions:  # noqa: N801
        @staticmethod
        def revokeIdentity(_):
            return _FakeFn()


@pytest.mark.parametrize('status,expected', [(0, False), (1, True)])
def test_revoke_credential_checks_receipt_status(offline, status, expected):
    from eth_account import Account
    p, identity, _ = offline
    p.account = Account.create()
    p.contract = _FakeContract()
    p.w3 = type('W3', (), {'eth': _FakeEth(status)})()
    assert p.revoke_credential(identity) is expected
    assert p.vehicles[identity].get('revoked', False) is expected


# ------------------------------------------------------------------ on-chain

@pytest.fixture(scope='module')
def chain_provider(rpc_url):
    p = MOBIVIDProvider(rpc_url)
    address = deploy(p.w3, p.account, load_artifact('MOBIVIDRegistry'))
    p._load_contract(address)
    p.contract_address = address
    return p


def test_onchain_register_verify_revoke(chain_provider):
    p = chain_provider
    cred = p.register_vehicle(f"T4-{time.time_ns()}", {'vin': f"VIN-T4-{time.time_ns()}"})
    did = cred.vehicle_id
    signed = p.sign_message(did, FAKE_BRAKE)
    assert p.verify_message(signed)[0] is True
    assert p.revoke_credential(did) is True
    assert p.verify_message(signed)[0] is False


def test_onchain_revocation_seen_without_local_flag(chain_provider):
    """A second verifier instance's local flag is stale; the registry still says revoked."""
    p = chain_provider
    cred = p.register_vehicle(f"T4b-{time.time_ns()}", {'vin': f"VIN-T4b-{time.time_ns()}"})
    did = cred.vehicle_id
    signed = p.sign_message(did, FAKE_BRAKE)
    assert p.revoke_credential(did) is True
    identity = p._vehicle_id_to_identity(did)
    p.vehicles[identity]['revoked'] = False          # simulate a verifier that missed the event
    assert p.verify_message(signed)[0] is False


def test_onchain_unauthorised_revoke_reports_failure(chain_provider, rpc_url):
    """revokeIdentity from a non-owner reverts; the provider must return False."""
    p = chain_provider
    cred = p.register_vehicle(f"T4c-{time.time_ns()}", {'vin': f"VIN-T4c-{time.time_ns()}"})
    did = cred.vehicle_id
    other = MOBIVIDProvider(rpc_url, contract_address=p.contract_address,
                            private_key="0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d")
    identity = p._vehicle_id_to_identity(did)
    other.vehicles[identity] = dict(p.vehicles[identity])
    assert other.revoke_credential(did) is False
    assert other.vehicles[identity].get('revoked', False) is False
    assert p.verify_message(p.sign_message(did, FAKE_BRAKE))[0] is True
