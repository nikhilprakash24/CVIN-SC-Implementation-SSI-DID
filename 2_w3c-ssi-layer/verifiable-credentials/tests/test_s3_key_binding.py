#!/usr/bin/env python3
"""
Review 02, S-3 — key binding in vc_verifier.py.

Before the fix the verifier bound a did:ethr DID to "the address in the DID"
and ignored the chain id, so did:ethr:0x1:A and did:ethr:0x7a69:A were the
same identity to every verifier, and there was no way to bind the key to a
resolved DID document. The chain-id and resolver tests fail on the pre-fix
code; the offline, non-rotating default is documented, not changed.
"""

import importlib.util
import os
import sys
from pathlib import Path

import pytest
from eth_account import Account

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from vc_issuer import CredentialIssuer  # noqa: E402
from vc_holder import HolderWallet  # noqa: E402
import vc_verifier  # noqa: E402
from vc_verifier import CredentialVerifier  # noqa: E402

CHALLENGE, DOMAIN = "nonce-s3", "rsu.example"


def _load_resolver_module():
    path = HERE.parents[1] / "did-resolution" / "did_resolver.py"
    spec = importlib.util.spec_from_file_location("did_resolver_s3", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


did_resolver = _load_resolver_module()


def claims(issuer):
    return {"vin": "5YJ3E1EA0PF123456", "make": "Tesla", "model": "Model 3",
            "year": 2024, "manufacturingDate": "2024-01-15",
            "manufacturerDid": issuer.issuer_did}


def vc_from(issuer, subject="did:ethr:0x7a69:0x" + "11" * 20):
    return issuer.issue_credential("VehicleBirthCertificate", subject,
                                   claims(issuer), revocable=False
                                   )["verifiableCredential"]


def errors(result):
    return " ".join(result.errors)


# --------------------------------------------------------------- chain id

class TestChainId:

    def test_verifier_for_chain_x_rejects_issuer_on_other_chain(self):
        mainnet_issuer = CredentialIssuer.with_ethr_did(chain_id="0x1")
        verifier = CredentialVerifier(chain_id=31337)
        result = verifier.verify_credential(vc_from(mainnet_issuer))
        assert not result.valid
        assert "chain 1" in errors(result) and "31337" in errors(result)

    def test_same_address_on_two_chains_is_two_identities(self):
        """did:ethr:0x1:A and did:ethr:0x7a69:A, same key: only the configured chain verifies."""
        key = Account.create().key.hex()
        on_1 = CredentialIssuer.with_ethr_did(private_key=key, chain_id="0x1")
        on_hh = CredentialIssuer.with_ethr_did(private_key=key, chain_id="0x7a69")
        verifier = CredentialVerifier(chain_id=0x7a69)
        assert verifier.verify_credential(vc_from(on_hh)).valid
        assert not verifier.verify_credential(vc_from(on_1)).valid

    def test_matching_chain_accepted_hex_decimal_and_name(self):
        key = Account.create().key.hex()
        for chain in ("0x7a69", "31337"):
            issuer = CredentialIssuer.with_ethr_did(private_key=key, chain_id=chain)
            assert CredentialVerifier(chain_id=31337).verify_credential(
                vc_from(issuer)).valid, chain
        dev = CredentialIssuer.with_ethr_did(private_key=key, chain_id="dev")
        assert CredentialVerifier(chain_id=1337).verify_credential(vc_from(dev)).valid

    def test_bare_did_ethr_is_mainnet_like_the_resolver(self):
        acct = Account.create()
        bare = CredentialIssuer(f"did:ethr:{acct.address}", acct.key.hex())
        assert CredentialVerifier(chain_id=1).verify_credential(vc_from(bare)).valid
        assert not CredentialVerifier(chain_id=31337).verify_credential(vc_from(bare)).valid
        # the resolver treats it the same way
        doc = did_resolver.DIDResolver().resolve(bare.issuer_did).didDocument.to_dict()
        assert doc["verificationMethod"][0]["blockchainAccountId"].startswith("eip155:1:")

    def test_chain_id_parsing_agrees_with_did_resolver(self):
        addr = "0x" + "ab" * 20
        for chain in ("0x1", "0x7a69", "31337", "1", "mainnet", "sepolia", "dev"):
            did = f"did:ethr:{chain}:{addr}"
            assert vc_verifier.chain_id_of(did) == did_resolver.parse_chain_id(chain, did)
        assert vc_verifier.chain_id_of(f"did:ethr:{addr}") == 1
        assert vc_verifier.chain_id_of("did:mobi:VIN123") is None
        with pytest.raises(ValueError):
            vc_verifier.chain_id_of(f"did:ethr:notachain:{addr}")

    def test_malformed_chain_rejected_when_chain_configured(self):
        acct = Account.create()
        issuer = CredentialIssuer(f"did:ethr:bogus:{acct.address}", acct.key.hex())
        assert not CredentialVerifier(chain_id=1).verify_credential(vc_from(issuer)).valid

    def test_presentation_holder_on_other_chain_rejected(self):
        issuer = CredentialIssuer.with_ethr_did(chain_id="0x7a69")
        holder = HolderWallet.with_ethr_did(chain_id="0x1")
        cid = holder.store_credential(issuer.issue_credential(
            "VehicleBirthCertificate", holder.holder_did, claims(issuer), revocable=False))
        vp = holder.create_presentation([cid], CHALLENGE, DOMAIN)
        ok, report = CredentialVerifier(chain_id=0x7a69).verify_presentation(vp, CHALLENGE, DOMAIN)
        assert not ok
        assert not report["presentation"]["valid"]
        # control: without a chain restriction the same VP verifies
        ok, _ = CredentialVerifier().verify_presentation(vp, CHALLENGE, DOMAIN)
        assert ok

    def test_no_chain_configured_keeps_previous_behaviour(self):
        issuer = CredentialIssuer.with_ethr_did(chain_id="0x5")
        assert CredentialVerifier().verify_credential(vc_from(issuer)).valid

    def test_chain_id_must_be_int(self):
        with pytest.raises(TypeError):
            CredentialVerifier(chain_id="0x1")


# --------------------------------------------------- DID resolver hook

class RotatedResolver:
    """Stub resolver: the DID's current assertion key is a DIFFERENT address
    (the original key, embedded in the DID, was rotated out on-chain)."""

    def __init__(self, new_address):
        self.new_address = new_address

    def resolve(self, did):
        vm = f"{did}#controller"
        return {
            "didResolutionMetadata": {},
            "didDocument": {
                "id": did,
                "verificationMethod": [{
                    "id": vm, "type": "EcdsaSecp256k1RecoveryMethod2020",
                    "controller": did,
                    "blockchainAccountId": f"eip155:1:{self.new_address}"}],
                "assertionMethod": [vm], "authentication": [vm],
            },
        }


class TestResolverHook:

    def test_genuine_issuer_accepted_with_did_resolver(self):
        issuer = CredentialIssuer.with_ethr_did()
        verifier = CredentialVerifier(did_resolver=did_resolver.DIDResolver())
        assert verifier.verify_credential(vc_from(issuer)).valid

    def test_rotated_out_key_rejected_with_resolver(self):
        issuer = CredentialIssuer.with_ethr_did()
        vc = vc_from(issuer)
        # Offline default (documented limitation): the original key still verifies.
        assert CredentialVerifier().verify_credential(vc).valid
        # With a resolver reporting the rotation, it no longer does.
        verifier = CredentialVerifier(
            did_resolver=RotatedResolver(Account.create().address))
        result = verifier.verify_credential(vc)
        assert not result.valid
        assert "not a assertionMethod key" in errors(result)

    def test_resolution_error_fails_closed(self):
        class Broken:
            def resolve(self, did):
                return {"didResolutionMetadata": {"error": "notFound"},
                        "didDocument": None}
        result = CredentialVerifier(did_resolver=Broken()).verify_credential(
            vc_from(CredentialIssuer.with_ethr_did()))
        assert not result.valid and "notFound" in errors(result)

    def test_resolver_exception_fails_closed(self):
        class Raises:
            def resolve(self, did):
                raise RuntimeError("rpc down")
        result = CredentialVerifier(did_resolver=Raises()).verify_credential(
            vc_from(CredentialIssuer.with_ethr_did()))
        assert not result.valid

    def test_verification_method_must_be_listed_in_document(self):
        issuer = CredentialIssuer.with_ethr_did()

        class OtherFragment(RotatedResolver):
            def resolve(self, did):
                r = super().resolve(did)
                r["didDocument"]["verificationMethod"][0]["id"] = f"{did}#key-2"
                r["didDocument"]["assertionMethod"] = [f"{did}#key-2"]
                return r
        result = CredentialVerifier(
            did_resolver=OtherFragment(issuer.address)).verify_credential(vc_from(issuer))
        assert not result.valid and "verificationMethod" in errors(result)

    def test_presentation_uses_authentication_keys(self):
        issuer = CredentialIssuer.with_ethr_did()
        holder = HolderWallet.with_ethr_did()
        cid = holder.store_credential(issuer.issue_credential(
            "VehicleBirthCertificate", holder.holder_did, claims(issuer), revocable=False))
        vp = holder.create_presentation([cid], CHALLENGE, DOMAIN)
        ok, _ = CredentialVerifier(did_resolver=did_resolver.DIDResolver()
                                   ).verify_presentation(vp, CHALLENGE, DOMAIN)
        assert ok


def test_limitation_is_documented():
    doc = vc_verifier.__doc__
    assert "OFFLINE AND NON-ROTATING" in doc
    readme = (HERE.parent / "README.md").read_text()
    assert "offline, non-rotating" in readme.lower()


# ------------------------------------- duplicate status registry id (Pass 2)

def test_duplicate_status_registry_id_raises():
    from vc_issuer import RevocationRegistry
    first = RevocationRegistry(registry_id="urn:cvin:status:dup")
    second = RevocationRegistry(registry_id="urn:cvin:status:dup")
    verifier = CredentialVerifier(revocation_registry=first)
    verifier.add_status_registry(first)          # same object: idempotent
    with pytest.raises(ValueError):
        verifier.add_status_registry(second)
    with pytest.raises(ValueError):
        CredentialVerifier(revocation_registry=[first, second])
    assert verifier.revocation_registry is first
