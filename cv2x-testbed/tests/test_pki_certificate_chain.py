"""
Review 02, T-1: both PKI verifiers must verify the certificate's signature
against the CA public key (and issuer name), plus validity window and CRL,
before verifying the message.

Based on the reviewer PoC poc_pki_forged_cert.py: an attacker self-signs a
certificate (copying the CA subject as issuer, or not) and signs a forged
hard-brake BSM with its own key. Before the fix both verifiers accepted it.
"""

import json
from datetime import datetime, timedelta

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

from identity.centralized_provider import CentralizedIdentityProvider
from identity.standard.pki_identity import VehiclePKI_CA, VehiclePKIIdentity
from experiment_pki_vs_erc1056 import StandardPKIAdapter, make_bsm

HARD_BRAKE = {'msgID': 'BasicSafetyMessage', 'speed': 99.9, 'brakes': 'hard'}


def _cert(subject_cn, issuer_name, subject_key, signing_key, not_before=None, not_after=None):
    now = datetime.utcnow()
    return (x509.CertificateBuilder()
            .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject_cn)]))
            .issuer_name(issuer_name)
            .public_key(subject_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(not_before or now - timedelta(minutes=1))
            .not_valid_after(not_after or now + timedelta(hours=1))
            .sign(signing_key, hashes.SHA256()))


def _package(cert, key, msg=HARD_BRAKE):
    sig = key.sign(json.dumps(msg, sort_keys=True).encode(), ec.ECDSA(hashes.SHA256()))
    return {'message': msg, 'signature': sig.hex(),
            'certificate': cert.public_bytes(serialization.Encoding.PEM).decode(),
            'timestamp': datetime.utcnow().isoformat()}


def forge_self_signed(issuer_name, msg=HARD_BRAKE):
    """PoC: attacker key, attacker-signed certificate naming `issuer_name`."""
    k = ec.generate_private_key(ec.SECP256R1())
    return _package(_cert("Pseudonym-evil", issuer_name, k, k), k, msg)


# ----------------------------------------------------------------- standard PKI

@pytest.fixture
def standard():
    ca = VehiclePKI_CA("CVIN-Standard-CA")
    sender = VehiclePKIIdentity("SENDER")
    sender.generate_keypair()
    sender.request_enrollment_certificate(ca)
    sender.request_pseudonym_certificates(ca, count=2)
    verifier = VehiclePKIIdentity("VERIFIER")
    verifier.trust_ca(ca.ca_certificate)
    return ca, sender, verifier


def test_standard_accepts_legitimate_message(standard):
    ca, sender, verifier = standard
    assert verifier.verify_message(sender.sign_message(make_bsm(1)), ca.get_crl())[0] is True


def test_standard_rejects_forged_cert_copying_ca_subject(standard):
    ca, _, verifier = standard
    forged = forge_self_signed(ca.ca_certificate.subject)
    assert verifier.verify_message(forged, ca.get_crl())[0] is False


def test_standard_rejects_forged_cert_with_any_issuer(standard):
    ca, _, verifier = standard
    forged = forge_self_signed(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "EVIL")]))
    assert verifier.verify_message(forged, ca.get_crl())[0] is False


def test_standard_rejects_cert_from_other_ca_with_same_name(standard):
    ca, _, verifier = standard
    rogue_ca = VehiclePKI_CA("CVIN-Standard-CA")   # same subject, different key
    k = ec.generate_private_key(ec.SECP256R1())
    cert = _cert("Pseudonym-x", rogue_ca.ca_certificate.subject, k, rogue_ca.ca_private_key)
    assert verifier.verify_message(_package(cert, k), ca.get_crl())[0] is False


def test_standard_rejects_expired_ca_signed_cert(standard):
    ca, _, verifier = standard
    k = ec.generate_private_key(ec.SECP256R1())
    now = datetime.utcnow()
    cert = _cert("Pseudonym-old", ca.ca_certificate.subject, k, ca.ca_private_key,
                 not_before=now - timedelta(hours=3), not_after=now - timedelta(hours=2))
    assert verifier.verify_message(_package(cert, k), ca.get_crl())[0] is False


def test_standard_rejects_revoked_cert(standard):
    ca, sender, verifier = standard
    signed = sender.sign_message(make_bsm(2))
    serial = x509.load_pem_x509_certificate(signed['certificate'].encode()).serial_number
    ca.revoke_certificate(serial)
    assert verifier.verify_message(signed, ca.get_crl())[0] is False


def test_standard_rejects_tampered_message(standard):
    ca, sender, verifier = standard
    signed = sender.sign_message(make_bsm(3))
    signed['message'] = dict(signed['message'], speed=99.9)
    assert verifier.verify_message(signed, ca.get_crl())[0] is False


def test_standard_without_trust_anchor_fails_closed(standard):
    ca, sender, _ = standard
    no_anchor = VehiclePKIIdentity("NO-ANCHOR")
    assert no_anchor.verify_message(sender.sign_message(make_bsm(4)), ca.get_crl())[0] is False


def test_enrolled_vehicle_trusts_its_ca(standard):
    ca, sender, _ = standard
    peer = VehiclePKIIdentity("PEER")
    peer.generate_keypair()
    peer.request_enrollment_certificate(ca)          # enrollment installs the anchor
    assert peer.verify_message(sender.sign_message(make_bsm(5)), ca.get_crl())[0] is True
    assert peer.verify_message(forge_self_signed(ca.ca_certificate.subject), ca.get_crl())[0] is False


def test_experiment_adapter_checks_ca_signature():
    a = StandardPKIAdapter()
    a.register_vehicle("S")
    assert a.verify_message(a.sign_message("S", make_bsm(6)))[0] is True
    assert a.verify_message(forge_self_signed(a.ca.ca_certificate.subject))[0] is False


# ----------------------------------------------------------- centralized PKI

@pytest.fixture
def central():
    p = CentralizedIdentityProvider("CVIN-Central-CA")
    p.register_vehicle("A")
    return p


def test_centralized_accepts_legitimate_message(central):
    assert central.verify_message(central.sign_message("A", make_bsm(1)))[0] is True


def test_centralized_rejects_forged_cert_copying_ca_subject(central):
    """The exact PoC case: issuer name copied from the CA, signed by the attacker."""
    assert central.verify_message(forge_self_signed(central.ca_certificate.subject))[0] is False


def test_centralized_rejects_cert_from_other_ca_with_same_name(central):
    rogue = CentralizedIdentityProvider("CVIN-Central-CA")
    rogue.register_vehicle("R")
    assert central.verify_message(rogue.sign_message("R", make_bsm(2)))[0] is False


def test_centralized_rejects_expired_ca_signed_cert(central):
    k = ec.generate_private_key(ec.SECP256R1())
    now = datetime.utcnow()
    cert = _cert("Pseudonym-old", central.ca_certificate.subject, k, central.ca_private_key,
                 not_before=now - timedelta(hours=3), not_after=now - timedelta(hours=2))
    assert central.verify_message(_package(cert, k))[0] is False


def test_centralized_rejects_revoked_vehicle(central):
    signed = central.sign_message("A", make_bsm(3))
    central.revoke_credential("A", "test")
    assert central.verify_message(signed)[0] is False
