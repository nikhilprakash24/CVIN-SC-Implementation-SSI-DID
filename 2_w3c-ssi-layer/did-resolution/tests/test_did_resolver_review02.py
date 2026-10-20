#!/usr/bin/env python3
"""
Review 02, S-10 — DID resolver: cache isolation, error codes, identifier
validation and CAIP-10 chain ids. Each test fails on the pre-fix resolver
(merge 434669d); /tmp/review_c/poc.py #7 and /tmp/review_d/poc_resolver.py
are reproduced here.

Run:  python3 -m pytest 2_w3c-ssi-layer -q
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from did_resolver import DIDResolver  # noqa: E402

ADDRESS = "0x1234567890abcdef1234567890abcdef12345678"
ETHR = f"did:ethr:0x1:{ADDRESS}"


@pytest.fixture
def resolver():
    return DIDResolver()


def error_of(resolver, did):
    return resolver.resolve(did).didResolutionMetadata.error


class TestCacheIsolation:

    def test_mutating_a_result_does_not_poison_the_cache(self, resolver):
        first = resolver.resolve(ETHR)
        first.didDocument.verificationMethod[0].blockchainAccountId = \
            "eip155:1:0xEVIL"
        first.didDocument.authentication.append("did:example:evil#k")
        again = resolver.resolve(ETHR)
        assert again.didDocument.verificationMethod[0].blockchainAccountId \
            == f"eip155:1:{ADDRESS}"
        assert "did:example:evil#k" not in again.didDocument.authentication

    def test_cached_results_are_distinct_objects(self, resolver):
        a, b = resolver.resolve(ETHR), resolver.resolve(ETHR)
        assert a is not b
        assert a.didDocument is not b.didDocument
        assert a.to_dict()["didDocument"] == b.to_dict()["didDocument"]

    def test_cache_ttl_expires(self):
        resolver = DIDResolver(cache_ttl_s=0)
        resolver.resolve(ETHR)
        stored = resolver.cache[ETHR]
        resolver.resolve(ETHR)
        assert resolver.cache[ETHR] is not stored   # re-resolved


class TestErrorCodes:

    @pytest.mark.parametrize("did", ["did:foo:bar", "did:example:12345",
                                     "did:web:example.com"])
    def test_unknown_method_is_method_not_supported(self, resolver, did):
        result = resolver.resolve(did)
        assert result.didResolutionMetadata.error == "methodNotSupported"
        assert result.didDocument is None

    @pytest.mark.parametrize("did", [
        "did:ethr:not-an-address",
        "did:ethr:0x1:NOT_AN_ADDRESS",
        "did:ethr:zzz",
        "did:ethr:0x1:0xabc",
        "did:ethr:0x1:0xabc:extra",
        f"did:ethr:0x1:{ADDRESS}:extra",
        f"did:ethr:notachain:{ADDRESS}",
        "did:ethr:0x02" + "ff" * 32,           # not a curve point
        "did:ethr_0x1234",
        "did:mobi:",
        "did:nft:0x1:0xabc",
        "not-a-did",
        "did::x",
        "DID:ethr:" + ADDRESS,
    ])
    def test_malformed_identifiers_are_invalid_did(self, resolver, did):
        result = resolver.resolve(did)
        assert result.didResolutionMetadata.error == "invalidDid", \
            result.didResolutionMetadata
        assert result.didDocument is None


class TestCaip10:

    @pytest.mark.parametrize("did,chain", [
        (f"did:ethr:0x1:{ADDRESS}", 1),
        (f"did:ethr:{ADDRESS}", 1),
        (f"did:ethr:0x7a69:{ADDRESS}", 31337),
        (f"did:ethr:31337:{ADDRESS}", 31337),
        (f"did:ethr:sepolia:{ADDRESS}", 11155111),
        (f"did:key:0x7a69:{ADDRESS}", 31337),
        (f"did:nft:0xaa36a7:{ADDRESS}:42", 11155111),
    ])
    def test_blockchain_account_id_uses_decimal_chain_id(self, resolver, did,
                                                         chain):
        doc = resolver.resolve(did).didDocument
        account = doc.verificationMethod[0].blockchainAccountId
        assert account == f"eip155:{chain}:{ADDRESS}"

    def test_compressed_public_key_identifier_resolves(self, resolver):
        from eth_keys import keys
        key = keys.PrivateKey(b"\x01" * 32).public_key
        did = "did:ethr:0x1:0x" + key.to_compressed_bytes().hex()
        doc = resolver.resolve(did).didDocument
        vm = doc.verificationMethod[0]
        assert vm.blockchainAccountId == \
            f"eip155:1:{key.to_checksum_address()}"
        assert vm.publicKeyHex == did.rsplit(":", 1)[-1]
