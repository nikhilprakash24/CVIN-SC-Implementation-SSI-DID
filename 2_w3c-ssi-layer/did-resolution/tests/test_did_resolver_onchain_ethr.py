#!/usr/bin/env python3
"""
Stream H-R: did:ethr resolved from a deployed ERC-1056 EthereumDIDRegistry.

Runs against the Hardhat node started by conftest.py (port 8560 by default).
Every test in TestOnChainEthr fails on the resolver at ffb71b0, which never
read the chain (it had no rpc_url / ethr_registry parameters and returned the
same synthesised document for every did:ethr). TestOfflineLabel fails there
too (no cvinResolutionMode property).

Run:  python3 -m pytest 2_w3c-ssi-layer/did-resolution/tests -q
"""

import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from did_resolver import DIDResolver  # noqa: E402
from resolver_chain_helpers import (  # noqa: E402
    ERC1056_ARTIFACT, HARDHAT_CHAIN_ID, deploy, free_port, node_url, send,
    web3_for,
)

CHAIN = "0x7a69"
NULL = "0x" + "0" * 40
XML_DATETIME_UTC = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
# Hardhat account #6 (public test mnemonic; not a secret)
ACCOUNT6_KEY = \
    "0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e"


def b32(text: str) -> bytes:
    """ethr-did-resolver stringToBytes32: ASCII, right-padded with zeros."""
    return text.encode("ascii").ljust(32, b"\0")


def did_of(address: str) -> str:
    return f"did:ethr:{CHAIN}:{address}"


@pytest.fixture(scope="module")
def resolver_node():
    return node_url()


@pytest.fixture(scope="module")
def w3(resolver_node):
    return web3_for(resolver_node)


@pytest.fixture(scope="module")
def registry(w3):
    return deploy(w3, ERC1056_ARTIFACT, w3.eth.accounts[0])


@pytest.fixture(scope="module")
def resolver(w3, registry, resolver_node):
    return DIDResolver(rpc_url=resolver_node, ethr_registry=registry.address)


@pytest.fixture(scope="module")
def accounts(w3):
    return w3.eth.accounts


def resolve_ok(resolver, did):
    res = resolver.resolve(did)
    out = res.to_dict()
    assert "error" not in out["didResolutionMetadata"], out
    assert out["didResolutionMetadata"]["cvinResolutionMode"] == \
        "erc1056-registry"
    return out


def resolve_err(resolver, did):
    res = resolver.resolve(did)
    out = res.to_dict()
    assert out["didResolutionMetadata"].get("error"), out
    assert out["didDocument"] is None, out
    assert out["didDocumentMetadata"] == {}, out
    return out


class TestOnChainEthr:

    def test_untouched_identity_controls_itself(self, resolver):
        from eth_account import Account
        addr = Account.create().address
        out = resolve_ok(resolver, did_of(addr))
        doc = out["didDocument"]
        assert doc["controller"] == did_of(addr)
        vm = doc["verificationMethod"][0]
        assert vm["id"] == f"{did_of(addr)}#controller"
        assert vm["type"] == "EcdsaSecp256k1RecoveryMethod2020"
        assert vm["blockchainAccountId"] == f"eip155:{HARDHAT_CHAIN_ID}:{addr}"
        assert doc["authentication"] == [vm["id"]]
        # never changed: no version / updated
        assert out["didDocumentMetadata"] == {}

    def test_change_owner_moves_controller(self, w3, resolver, registry,
                                           accounts):
        identity, new_owner = accounts[1], accounts[2]
        rcpt = send(w3, registry.functions.changeOwner(identity, new_owner),
                    identity)
        out = resolve_ok(resolver, did_of(identity))
        doc = out["didDocument"]
        assert doc["controller"] == did_of(new_owner.lower())
        assert doc["verificationMethod"][0]["blockchainAccountId"] == \
            f"eip155:{HARDHAT_CHAIN_ID}:{new_owner}"
        meta = out["didDocumentMetadata"]
        assert meta["versionId"] == str(rcpt.blockNumber)
        assert XML_DATETIME_UTC.fullmatch(meta["updated"])
        assert "deactivated" not in meta

    def test_sigauth_delegate_appears_then_revoke_removes_it(
            self, w3, resolver, registry, accounts):
        identity, delegate = accounts[3], accounts[10]
        send(w3, registry.functions.addDelegate(
            identity, b32("sigAuth"), delegate, 3600), identity)
        doc = resolve_ok(resolver, did_of(identity))["didDocument"]
        dvm = [vm for vm in doc["verificationMethod"]
               if vm.get("blockchainAccountId") ==
               f"eip155:{HARDHAT_CHAIN_ID}:{delegate}"]
        assert len(dvm) == 1
        assert dvm[0]["id"] == f"{did_of(identity)}#delegate-1"
        assert dvm[0]["type"] == "EcdsaSecp256k1RecoveryMethod2020"
        assert dvm[0]["id"] in doc["authentication"]
        assert dvm[0]["id"] in doc["assertionMethod"]

        send(w3, registry.functions.revokeDelegate(
            identity, b32("sigAuth"), delegate), identity)
        doc = resolve_ok(resolver, did_of(identity))["didDocument"]
        assert [vm["id"] for vm in doc["verificationMethod"]] == \
            [f"{did_of(identity)}#controller"]
        assert doc["authentication"] == [f"{did_of(identity)}#controller"]

    def test_verikey_delegate_is_assertion_only(self, w3, resolver, registry,
                                                accounts):
        identity, delegate = accounts[4], accounts[11]
        send(w3, registry.functions.addDelegate(
            identity, b32("veriKey"), delegate, 3600), identity)
        doc = resolve_ok(resolver, did_of(identity))["didDocument"]
        vm_id = f"{did_of(identity)}#delegate-1"
        assert vm_id in doc["assertionMethod"]
        assert vm_id not in doc["authentication"]

    def test_delegate_ids_stable_when_another_is_revoked(
            self, w3, resolver, registry, accounts):
        identity, d1, d2 = accounts[5], accounts[12], accounts[13]
        for d in (d1, d2):
            send(w3, registry.functions.addDelegate(
                identity, b32("veriKey"), d, 3600), identity)
        send(w3, registry.functions.revokeDelegate(
            identity, b32("veriKey"), d1), identity)
        doc = resolve_ok(resolver, did_of(identity))["didDocument"]
        ids = {vm["id"]: vm.get("blockchainAccountId")
               for vm in doc["verificationMethod"]}
        assert ids == {
            f"{did_of(identity)}#controller":
                f"eip155:{HARDHAT_CHAIN_ID}:{identity}",
            f"{did_of(identity)}#delegate-2":
                f"eip155:{HARDHAT_CHAIN_ID}:{d2}",
        }

    def test_verikey_attribute_and_service(self, w3, resolver, registry,
                                           accounts):
        identity = accounts[7]
        key = bytes.fromhex(
            "02" + "11" * 32)  # 33-byte compressed-key-shaped value
        send(w3, registry.functions.setAttribute(
            identity, b32("did/pub/Secp256k1/veriKey/hex"), key, 3600),
            identity)
        send(w3, registry.functions.setAttribute(
            identity, b32("did/svc/HubService"),
            b"https://hubs.example.com/cvin", 3600), identity)
        doc = resolve_ok(resolver, did_of(identity))["didDocument"]
        vm = [v for v in doc["verificationMethod"] if "publicKeyHex" in v]
        assert vm == [{
            "id": f"{did_of(identity)}#delegate-1",
            "type": "EcdsaSecp256k1VerificationKey2019",
            "controller": did_of(identity),
            "publicKeyHex": key.hex(),
        }]
        assert vm[0]["id"] in doc["assertionMethod"]
        assert vm[0]["id"] not in doc["authentication"]
        assert "https://w3id.org/security/suites/secp256k1-2019/v1" in \
            doc["@context"]
        assert doc["service"] == [{
            "id": f"{did_of(identity)}#service-1",
            "type": "HubService",
            "serviceEndpoint": "https://hubs.example.com/cvin",
        }]

    def test_sigauth_attribute_and_revoke_attribute(self, w3, resolver,
                                                    registry, accounts):
        identity = accounts[8]
        key = bytes.fromhex("03" + "22" * 32)
        name = b32("did/pub/Secp256k1/sigAuth/hex")
        send(w3, registry.functions.setAttribute(identity, name, key, 3600),
             identity)
        doc = resolve_ok(resolver, did_of(identity))["didDocument"]
        assert f"{did_of(identity)}#delegate-1" in doc["authentication"]
        send(w3, registry.functions.revokeAttribute(identity, name, key),
             identity)
        doc = resolve_ok(resolver, did_of(identity))["didDocument"]
        assert len(doc["verificationMethod"]) == 1

    def test_expired_delegate_disappears(self, w3, resolver, registry,
                                         accounts):
        identity, delegate = accounts[9], accounts[14]
        send(w3, registry.functions.addDelegate(
            identity, b32("sigAuth"), delegate, 60), identity)
        doc = resolve_ok(resolver, did_of(identity))["didDocument"]
        assert len(doc["verificationMethod"]) == 2
        w3.provider.make_request("evm_increaseTime", [120])
        w3.provider.make_request("evm_mine", [])
        doc = resolve_ok(resolver, did_of(identity))["didDocument"]
        assert len(doc["verificationMethod"]) == 1
        assert doc["authentication"] == [f"{did_of(identity)}#controller"]

    def test_change_owner_to_zero_deactivates(self, w3, resolver, registry,
                                              accounts):
        identity = accounts[15]
        send(w3, registry.functions.addDelegate(
            identity, b32("sigAuth"), accounts[16], 3600), identity)
        rcpt = send(w3, registry.functions.changeOwner(identity, NULL),
                    identity)
        out = resolve_ok(resolver, did_of(identity))
        assert out["didDocumentMetadata"]["deactivated"] is True
        assert out["didDocumentMetadata"]["versionId"] == \
            str(rcpt.blockNumber)
        doc = out["didDocument"]
        assert doc["id"] == did_of(identity)
        assert "verificationMethod" not in doc
        assert "authentication" not in doc

    def test_public_key_did_has_controller_key(self, resolver):
        from eth_keys import keys
        pk = keys.PrivateKey(bytes.fromhex(ACCOUNT6_KEY[2:])).public_key
        compressed = "0x" + pk.to_compressed_bytes().hex()
        did = did_of(compressed)
        doc = resolve_ok(resolver, did)["didDocument"]
        ids = [vm["id"] for vm in doc["verificationMethod"]]
        assert ids == [f"{did}#controller", f"{did}#controllerKey"]
        assert doc["verificationMethod"][0]["blockchainAccountId"] == \
            f"eip155:{HARDHAT_CHAIN_ID}:{pk.to_checksum_address()}"
        assert doc["verificationMethod"][1]["publicKeyHex"] == compressed[2:]

    def test_registry_change_is_not_hidden_by_cache(self, w3, resolver,
                                                    registry, accounts):
        identity = accounts[17]
        before = resolve_ok(resolver, did_of(identity))["didDocument"]
        send(w3, registry.functions.changeOwner(identity, accounts[18]),
             identity)
        after = resolve_ok(resolver, did_of(identity))["didDocument"]
        assert before["controller"] == did_of(identity)
        assert after["controller"] == did_of(accounts[18].lower())

    def test_wrong_chain_is_an_error(self, resolver, accounts):
        out = resolve_err(resolver, f"did:ethr:0x1:{accounts[1]}")
        assert out["didResolutionMetadata"]["error"] == "notFound"
        assert "chain" in out["didResolutionMetadata"]["errorMessage"]
        # no chain segment = mainnet, also not this chain
        out = resolve_err(resolver, f"did:ethr:{accounts[1]}")
        assert out["didResolutionMetadata"]["error"] == "notFound"

    def test_configured_chain_id_must_match_node(self, registry,
                                                 resolver_node, accounts):
        r = DIDResolver(rpc_url=resolver_node, ethr_registry=registry.address,
                        chain_id=1)
        out = resolve_err(r, did_of(accounts[1]))
        assert out["didResolutionMetadata"]["error"] == "internalError"

    def test_rpc_down_is_an_error_not_a_document(self, registry, accounts):
        r = DIDResolver(rpc_url=f"http://127.0.0.1:{free_port()}",
                        ethr_registry=registry.address, rpc_timeout_s=2)
        out = resolve_err(r, did_of(accounts[1]))
        assert out["didResolutionMetadata"]["error"] == "internalError"
        assert "RPC" in out["didResolutionMetadata"]["errorMessage"]
        rep = r.resolve_representation(did_of(accounts[1])).to_dict()
        assert rep["didDocumentStream"] == ""
        assert rep["didResolutionMetadata"]["error"] == "internalError"

    def test_no_contract_at_registry_address_is_an_error(
            self, resolver_node, accounts):
        from eth_account import Account
        r = DIDResolver(rpc_url=resolver_node,
                        ethr_registry=Account.create().address)
        out = resolve_err(r, did_of(accounts[1]))
        assert out["didResolutionMetadata"]["error"] == "internalError"

    def test_invalid_did_still_invalid_on_chain(self, resolver):
        out = resolve_err(resolver, "did:ethr:0x7a69:0x1234")
        assert out["didResolutionMetadata"]["error"] == "invalidDid"


class TestConfiguration:

    def test_half_configuration_is_rejected(self):
        with pytest.raises(ValueError):
            DIDResolver(rpc_url="http://127.0.0.1:1")
        with pytest.raises(ValueError):
            DIDResolver(ethr_registry="0x" + "11" * 20)

    def test_mobi_only_resolver_does_not_synthesise_ethr(self):
        r = DIDResolver(rpc_url="http://127.0.0.1:1",
                        mobi_registry="0x" + "11" * 20)
        out = resolve_err(r, did_of("0x" + "22" * 20))
        assert out["didResolutionMetadata"]["error"] == "methodNotSupported"


class TestOfflineLabel:

    @pytest.mark.parametrize("did", [
        "did:ethr:0x1:0x1234567890abcdef1234567890abcdef12345678",
        "did:nft:0x1:0xabc:123",
        "did:key:0x1:0x1234567890abcdef1234567890abcdef12345678",
    ])
    def test_offline_results_say_they_are_synthesised(self, did):
        out = DIDResolver().resolve(did).to_dict()
        assert out["didResolutionMetadata"]["cvinResolutionMode"] == \
            "offline-synthesized"
        rep = DIDResolver().resolve_representation(did).to_dict()
        assert rep["didResolutionMetadata"]["cvinResolutionMode"] == \
            "offline-synthesized"

    def test_errors_carry_no_mode(self):
        out = DIDResolver().resolve("did:ethr_0x1234").to_dict()
        assert "cvinResolutionMode" not in out["didResolutionMetadata"]
