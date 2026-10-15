#!/usr/bin/env python3
"""
Stream H-R: did:mobi:<salted VIN hash> resolved through a deployed
MOBIVIDRegistryV2 (lookupByVINHash -> getVehicleDID -> the vehicle's
ERC-1056 state in the MOBI registry).

Every test in TestOnChainMobi fails on the resolver at ffb71b0, whose
did:mobi resolver was a placeholder (VIN in the DID, publicKeyHex "0x...",
ipfs://Qm... endpoints, no registry read). TestOfflineLegacy documents the
offline placeholder, unchanged except for its new label, and the new
create_did(vin_hash=...) form; both fail at ffb71b0 too.
"""

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SSI = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(SSI, "mobi-vid"))

from did_resolver import DIDResolver  # noqa: E402
from resolver_chain_helpers import (  # noqa: E402
    HARDHAT_CHAIN_ID, MOBI_ARTIFACT, deploy, free_port, node_url, send,
    web3_for,
)
from birth_certificate import salted_vin_hash  # noqa: E402

VIN = "5YJ3E1EA0PF123456"
CHAIN = "0x7a69"


def b32(text: str) -> bytes:
    return text.encode("ascii").ljust(32, b"\0")


@pytest.fixture(scope="module")
def resolver_node():
    return node_url()


@pytest.fixture(scope="module")
def w3(resolver_node):
    return web3_for(resolver_node)


@pytest.fixture(scope="module")
def mobi(w3):
    # the deployer is authorised as the first manufacturer by the constructor
    return deploy(w3, MOBI_ARTIFACT, w3.eth.accounts[0])


@pytest.fixture(scope="module")
def resolver(mobi, resolver_node):
    return DIDResolver(rpc_url=resolver_node, mobi_registry=mobi.address)


def register(w3, mobi, salt: str, first_owner: str, attributes=b""):
    """Birth registration; returns (did:mobi, vehicle address)."""
    from eth_account import Account
    vehicle = Account.create().address
    vin_hash = salted_vin_hash(VIN, salt)
    send(w3, mobi.functions.registerVehicleBirth(
        vehicle, vin_hash, "ciphertext-not-the-vin", b"\x01" * 32,
        first_owner, attributes), w3.eth.accounts[0])
    return f"did:mobi:0x{vin_hash.hex()}", vehicle


def ok(resolver, did):
    out = resolver.resolve(did).to_dict()
    assert "error" not in out["didResolutionMetadata"], out
    assert out["didResolutionMetadata"]["cvinResolutionMode"] == \
        "mobi-vid-registry"
    assert VIN not in json.dumps(out), "raw VIN leaked into the resolution"
    return out


def err(resolver, did):
    out = resolver.resolve(did).to_dict()
    assert out["didResolutionMetadata"].get("error"), out
    assert out["didDocument"] is None and out["didDocumentMetadata"] == {}
    assert VIN not in json.dumps(out)
    return out


class TestOnChainMobi:

    def test_birth_resolves_to_first_owner(self, w3, mobi, resolver):
        owner = w3.eth.accounts[1]
        did, vehicle = register(w3, mobi, "salt-a", owner,
                                attributes=b'{"make":"Tesla"}')
        out = ok(resolver, did)
        doc = out["didDocument"]
        assert doc["id"] == did
        assert doc["controller"] == f"did:ethr:{CHAIN}:{owner.lower()}"
        assert doc["alsoKnownAs"] == [f"did:ethr:{CHAIN}:{vehicle.lower()}"]
        assert doc["verificationMethod"][0] == {
            "id": f"{did}#controller",
            "type": "EcdsaSecp256k1RecoveryMethod2020",
            "controller": did,
            "blockchainAccountId": f"eip155:{HARDHAT_CHAIN_ID}:{owner}",
        }
        assert out["didDocumentMetadata"]["versionId"].isdigit()

    def test_ownership_transfer_moves_controller(self, w3, mobi, resolver):
        a, b = w3.eth.accounts[2], w3.eth.accounts[3]
        did, vehicle = register(w3, mobi, "salt-b", a)
        send(w3, mobi.functions.transferVehicleOwnership(
            vehicle, b, 12000, "CA DMV"), a)
        doc = ok(resolver, did)["didDocument"]
        assert doc["controller"] == f"did:ethr:{CHAIN}:{b.lower()}"

    def test_delegate_add_and_revoke(self, w3, mobi, resolver):
        owner, delegate = w3.eth.accounts[4], w3.eth.accounts[5]
        did, vehicle = register(w3, mobi, "salt-c", owner)
        send(w3, mobi.functions.addDelegate(
            vehicle, b32("sigAuth"), delegate, 3600), owner)
        doc = ok(resolver, did)["didDocument"]
        assert f"{did}#delegate-1" in doc["authentication"]
        # MOBI ERC1056Registry.revokeDelegate emits validTo = block.timestamp
        send(w3, mobi.functions.revokeDelegate(
            vehicle, b32("sigAuth"), delegate), owner)
        doc = ok(resolver, did)["didDocument"]
        assert doc["authentication"] == [f"{did}#controller"]

    def test_revoked_identity_is_deactivated(self, w3, mobi, resolver):
        owner = w3.eth.accounts[6]
        did, vehicle = register(w3, mobi, "salt-d", owner)
        send(w3, mobi.functions.revokeIdentity(vehicle), owner)
        out = ok(resolver, did)
        assert out["didDocumentMetadata"]["deactivated"] is True
        assert set(out["didDocument"]) == {"@context", "id"}

    def test_same_state_as_did_ethr_on_the_mobi_registry(
            self, w3, mobi, resolver, resolver_node):
        owner = w3.eth.accounts[7]
        did, vehicle = register(w3, mobi, "salt-e", owner)
        ethr = DIDResolver(rpc_url=resolver_node, ethr_registry=mobi.address)
        ethr_did = f"did:ethr:{CHAIN}:{vehicle.lower()}"
        ethr_doc = ethr.resolve(ethr_did).to_dict()["didDocument"]
        mobi_doc = ok(resolver, did)["didDocument"]
        assert ethr_doc["controller"] == mobi_doc["controller"]

    def test_unknown_vin_hash_is_not_found(self, resolver):
        out = err(resolver, "did:mobi:0x" + "ab" * 32)
        assert out["didResolutionMetadata"]["error"] == "notFound"

    def test_raw_vin_is_rejected_without_echo(self, resolver):
        out = err(resolver, f"did:mobi:{VIN}")
        assert out["didResolutionMetadata"]["error"] == "invalidDid"

    def test_rpc_down_is_an_error(self, mobi):
        r = DIDResolver(rpc_url=f"http://127.0.0.1:{free_port()}",
                        mobi_registry=mobi.address, rpc_timeout_s=2)
        out = err(r, "did:mobi:0x" + "ab" * 32)
        assert out["didResolutionMetadata"]["error"] == "internalError"

    def test_no_contract_at_mobi_address_is_an_error(self, resolver_node):
        from eth_account import Account
        r = DIDResolver(rpc_url=resolver_node,
                        mobi_registry=Account.create().address)
        out = err(r, "did:mobi:0x" + "ab" * 32)
        assert out["didResolutionMetadata"]["error"] == "internalError"

    def test_ethr_only_resolver_does_not_synthesise_mobi(self, resolver_node,
                                                         mobi):
        r = DIDResolver(rpc_url=resolver_node, ethr_registry=mobi.address)
        out = err(r, "did:mobi:0x" + "ab" * 32)
        assert out["didResolutionMetadata"]["error"] == "methodNotSupported"


class TestOfflineLegacy:

    def test_offline_placeholder_is_labelled(self):
        out = DIDResolver().resolve(f"did:mobi:{VIN}").to_dict()
        assert out["didResolutionMetadata"]["cvinResolutionMode"] == \
            "offline-synthesized"

    def test_create_did_from_vin_hash(self):
        h = salted_vin_hash(VIN, "s")
        did, _ = DIDResolver().create_did(
            __import__("did_resolver").DIDMethod.MOBI, vin_hash=h)
        assert did == f"did:mobi:0x{h.hex()}" and VIN not in did
