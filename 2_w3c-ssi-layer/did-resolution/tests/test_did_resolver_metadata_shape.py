#!/usr/bin/env python3
"""
Stream G-R: resolution-metadata shape, root causes R1-R4 of the external
W3C DID test suite run (docs/conformance/W3C_DID_TEST_SUITE.md section 8.4).
Each test fails on the resolver at f73e81e.

  R1  error / errorMessage ABSENT (not null) on success
  R2  contentType absent on resolve(); present on a successful
      resolveRepresentation() and matching the didDocumentStream
  R3  no null-valued keys in either metadata structure; didDocumentMetadata
      empty when resolution fails
  R4  created / updated / retrieved are XML datetimes in UTC ('Z') without
      fractional seconds

Run:  python3 -m pytest 2_w3c-ssi-layer -q
"""

import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from did_resolver import DIDResolver  # noqa: E402

ADDRESS = "0x1234567890abcdef1234567890abcdef12345678"
GOOD = [
    f"did:ethr:0x1:{ADDRESS}",
    "did:nft:0x1:0xabc:123",
    f"did:key:0x1:{ADDRESS}",
    "did:mobi:5YJ3E1EA0PF123456",
]
BAD = ["not-a-did", "did:ethr_0x1234", "did:mobi:", "did:nft:0x1:0xabc",
       "did:web:example.com", "did:example:123"]

# DID Core 7.1.3: XML Datetime normalised to UTC, no sub-second precision
XML_DATETIME_UTC = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")


def _no_nulls(obj):
    if isinstance(obj, dict):
        return all(v is not None and _no_nulls(v) for v in obj.values())
    if isinstance(obj, list):
        return all(_no_nulls(v) for v in obj)
    return True


@pytest.fixture
def resolver():
    return DIDResolver()


@pytest.mark.parametrize("did", GOOD)
class TestSuccess:

    def test_r1_no_error_keys(self, resolver, did):
        meta = resolver.resolve(did).to_dict()["didResolutionMetadata"]
        assert "error" not in meta, meta
        assert "errorMessage" not in meta, meta

    def test_r2_resolve_has_no_content_type(self, resolver, did):
        meta = resolver.resolve(did).to_dict()["didResolutionMetadata"]
        assert "contentType" not in meta, meta

    def test_r2_resolve_representation_has_content_type(self, resolver, did):
        rep = resolver.resolve_representation(did).to_dict()
        meta = rep["didResolutionMetadata"]
        assert "error" not in meta
        assert meta["contentType"] == "application/did+ld+json"
        doc = json.loads(rep["didDocumentStream"])
        assert doc["id"] == did and "@context" in doc
        assert doc == resolver.resolve(did).to_dict()["didDocument"]

    def test_r3_no_null_keys(self, resolver, did):
        out = resolver.resolve(did).to_dict()
        assert _no_nulls(out["didResolutionMetadata"]), out
        assert _no_nulls(out["didDocumentMetadata"]), out
        rep = resolver.resolve_representation(did).to_dict()
        assert _no_nulls(rep["didResolutionMetadata"]), rep
        assert _no_nulls(rep["didDocumentMetadata"]), rep

    def test_r3_document_metadata_keeps_present_values(self, resolver, did):
        meta = resolver.resolve(did).to_dict()["didDocumentMetadata"]
        assert "created" in meta
        assert meta.get("deactivated", False) is False
        for absent in ("updated", "nextUpdate", "nextVersionId",
                       "canonicalId", "equivalentId"):
            assert absent not in meta, meta

    def test_r4_xml_datetime(self, resolver, did):
        out = resolver.resolve(did).to_dict()
        for key in ("created", "updated"):
            if key in out["didDocumentMetadata"]:
                assert XML_DATETIME_UTC.fullmatch(
                    out["didDocumentMetadata"][key]), out
        assert XML_DATETIME_UTC.fullmatch(
            out["didResolutionMetadata"]["retrieved"]), out
        # a cache hit re-stamps 'retrieved' in the same format
        again = resolver.resolve(did).to_dict()
        assert XML_DATETIME_UTC.fullmatch(
            again["didResolutionMetadata"]["retrieved"]), again

    def test_dataclass_attributes_still_readable(self, resolver, did):
        res = resolver.resolve(did)
        assert res.didResolutionMetadata.error is None
        assert res.didDocument is not None


@pytest.mark.parametrize("did", BAD)
class TestError:

    def test_r1_error_present(self, resolver, did):
        meta = resolver.resolve(did).to_dict()["didResolutionMetadata"]
        assert isinstance(meta["error"], str) and meta["error"]
        assert not re.search(r"\s", meta["error"])

    def test_r2_no_content_type_on_error(self, resolver, did):
        meta = resolver.resolve(did).to_dict()["didResolutionMetadata"]
        assert "contentType" not in meta, meta
        rep = resolver.resolve_representation(did).to_dict()
        assert "contentType" not in rep["didResolutionMetadata"], rep
        assert rep["didDocumentStream"] == ""

    def test_r3_empty_document_metadata(self, resolver, did):
        out = resolver.resolve(did).to_dict()
        assert out["didDocument"] is None
        assert out["didDocumentMetadata"] == {}, out
        assert _no_nulls(out["didResolutionMetadata"]), out


def test_representation_not_supported(resolver):
    rep = resolver.resolve_representation(
        GOOD[0], accept="image/jpeg").to_dict()
    assert rep["didResolutionMetadata"]["error"] == "representationNotSupported"
    assert "contentType" not in rep["didResolutionMetadata"]
    assert rep["didDocumentStream"] == ""
    assert rep["didDocumentMetadata"] == {}
