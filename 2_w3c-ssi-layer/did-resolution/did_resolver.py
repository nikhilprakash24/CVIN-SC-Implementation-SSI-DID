#!/usr/bin/env python3
"""
W3C DID Core v1.0 Compliant Resolver
====================================

Resolves Decentralized Identifiers (DIDs) to DID Documents for all 9 blockchain
identity standards implemented in this thesis.

W3C DID Core Specification: https://www.w3.org/TR/did-core/

Supported DID Methods:
- did:ethr: (ERC-1056 Lightweight Identity)
- did:nft:  (ERC-721 NFT-based Identity)
- did:key:  (ERC-725 Proxy Account)
- did:mobi: (MOBI VID compliant)

Resolution contract (DID Core 7.1, verified against the W3C DID test suite,
see docs/conformance/W3C_DID_TEST_SUITE.md):
- resolve(did)                -> didResolutionMetadata, didDocument, didDocumentMetadata
- resolve_representation(did) -> didResolutionMetadata (+contentType), didDocumentStream,
                                 didDocumentMetadata
- DIDs are validated against the DID Core 3.1 ABNF before dispatch; syntax
  errors yield error "invalidDid", unknown methods "methodNotSupported".
- Metadata structures contain only populated properties: no "error" key on
  success, no "contentType" for resolve(), no null placeholders, and an empty
  didDocumentMetadata on error. Timestamps are XML Datetime in UTC without
  sub-second precision (YYYY-MM-DDTHH:MM:SSZ).

Author: Nikhil Prakash
Thesis: MASc, UBC ECE
"""

import json
import hashlib
import re
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum


# DID Core 3.1 DID Syntax (ABNF):
#   did                = "did:" method-name ":" method-specific-id
#   method-name        = 1*method-char          ; method-char = %x61-7A / DIGIT
#   method-specific-id = *( *idchar ":" ) 1*idchar
#   idchar             = ALPHA / DIGIT / "." / "-" / "_" / pct-encoded
#   pct-encoded        = "%" HEXDIG HEXDIG
_IDCHAR = r"(?:[A-Za-z0-9._-]|%[0-9A-Fa-f]{2})"
DID_SYNTAX = re.compile(
    r"^did:(?P<method>[a-z0-9]+):"
    r"(?P<id>(?:" + _IDCHAR + r"*:)*" + _IDCHAR + r"+)$"
)

#: The only representation this resolver produces (DID Core 6.3, JSON-LD).
DID_LD_JSON = "application/did+ld+json"
SUPPORTED_CONTENT_TYPES = (DID_LD_JSON,)


def xml_datetime_now() -> str:
    """Current time as an XML Datetime normalised to UTC, no sub-seconds (DID Core 7.1.3)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class DIDMethod(str, Enum):
    """Supported DID methods"""
    ETHR = "ethr"  # ERC-1056
    NFT = "nft"    # ERC-721
    KEY = "key"    # ERC-725
    MOBI = "mobi"  # MOBI VID
    WEB = "web"    # did:web for testing


class VerificationRelationship(str, Enum):
    """W3C DID Core verification relationships"""
    AUTHENTICATION = "authentication"
    ASSERTION_METHOD = "assertionMethod"
    KEY_AGREEMENT = "keyAgreement"
    CAPABILITY_INVOCATION = "capabilityInvocation"
    CAPABILITY_DELEGATION = "capabilityDelegation"


class DIDResolutionError(Exception):
    """
    A resolution failure with a DID Core 7.1.2 error code.

    `code` is one of the registered single-keyword values: "invalidDid",
    "notFound", "methodNotSupported", "representationNotSupported" or
    "internalError". `str(exc)` is the human-readable errorMessage.
    """

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass
class VerificationMethod:
    """W3C DID Core Verification Method"""
    id: str
    type: str  # e.g., "EcdsaSecp256k1VerificationKey2019"
    controller: str
    publicKeyHex: Optional[str] = None
    publicKeyBase58: Optional[str] = None
    publicKeyJwk: Optional[Dict] = None
    blockchainAccountId: Optional[str] = None  # For ERC-1056


@dataclass
class Service:
    """W3C DID Core Service Endpoint"""
    id: str
    type: str  # e.g., "LinkedDomains", "CredentialRegistry"
    serviceEndpoint: str  # URL or blockchain address


@dataclass
class DIDDocument:
    """
    W3C DID Core v1.0 Compliant DID Document

    Reference: https://www.w3.org/TR/did-core/#core-properties
    """
    context: List[str] = field(default_factory=lambda: [
        "https://www.w3.org/ns/did/v1",
        "https://w3id.org/security/suites/secp256k1-2019/v1"
    ])
    id: str = ""  # DID
    controller: Optional[str] = None
    verificationMethod: List[VerificationMethod] = field(default_factory=list)
    authentication: List[str] = field(default_factory=list)
    assertionMethod: List[str] = field(default_factory=list)
    keyAgreement: List[str] = field(default_factory=list)
    capabilityInvocation: List[str] = field(default_factory=list)
    capabilityDelegation: List[str] = field(default_factory=list)
    service: List[Service] = field(default_factory=list)

    # Optional properties
    alsoKnownAs: List[str] = field(default_factory=list)

    # Metadata (not part of DID Document, but useful for resolution)
    created: Optional[str] = None
    updated: Optional[str] = None
    versionId: Optional[str] = None
    deactivated: bool = False

    def to_dict(self) -> Dict:
        """Convert to W3C compliant dictionary"""
        doc = {
            "@context": self.context,
            "id": self.id
        }

        if self.controller:
            doc["controller"] = self.controller

        if self.verificationMethod:
            doc["verificationMethod"] = [
                {k: v for k, v in asdict(vm).items() if v is not None}
                for vm in self.verificationMethod
            ]

        # Add verification relationships
        for rel in ["authentication", "assertionMethod", "keyAgreement",
                    "capabilityInvocation", "capabilityDelegation"]:
            val = getattr(self, rel)
            if val:
                doc[rel] = val

        if self.service:
            doc["service"] = [asdict(s) for s in self.service]

        if self.alsoKnownAs:
            doc["alsoKnownAs"] = self.alsoKnownAs

        return doc

    def to_representation(self, content_type: str = DID_LD_JSON) -> str:
        """Serialise to the JSON-LD representation (DID Core 6.3 production)."""
        if content_type not in SUPPORTED_CONTENT_TYPES:
            raise DIDResolutionError(
                "representationNotSupported",
                f"Representation '{content_type}' is not supported "
                f"(supported: {', '.join(SUPPORTED_CONTENT_TYPES)})")
        return json.dumps(self.to_dict())


@dataclass
class DIDResolutionMetadata:
    """
    W3C DID Resolution metadata (DID Core 7.1.2)

    `contentType` is the media type of the representation this resolver
    produces for the document. DID Core only allows it in the serialised
    structure when resolveRepresentation() was called, so
    DIDResolutionResult.to_dict() omits it for resolve() results; the
    attribute itself is kept on every successful result for callers that
    want to know how the document would be serialised. On error it is None.
    `error` / `errorMessage` are set only when resolution failed.
    """
    contentType: Optional[str] = DID_LD_JSON
    retrieved: Optional[str] = None
    error: Optional[str] = None
    errorMessage: Optional[str] = None

    def to_dict(self) -> Dict:
        """Metadata structure with only the populated properties."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class DIDDocumentMetadata:
    """W3C DID Document metadata (DID Core 7.1.3)"""
    created: Optional[str] = None
    updated: Optional[str] = None
    deactivated: bool = False
    versionId: Optional[str] = None
    nextUpdate: Optional[str] = None
    nextVersionId: Optional[str] = None
    equivalentId: List[str] = field(default_factory=list)
    canonicalId: Optional[str] = None

    def to_dict(self) -> Dict:
        """
        Metadata structure with only the populated properties.

        Each 7.1.3 property is defined "if present"; unset values (None, an
        empty equivalentId set, deactivated == False) are left out so an
        untouched instance serialises to the empty structure that DID Core
        requires on error.
        """
        out = {}
        for key, value in asdict(self).items():
            if value is None or value == [] or value is False:
                continue
            out[key] = value
        return out


@dataclass
class DIDResolutionResult:
    """
    W3C DID Resolution Result

    `didDocumentStream` is set only by resolve_representation(); it is the
    serialised document ("" on error). to_dict() produces the resolve()
    output (didDocument) or the resolveRepresentation() output
    (didDocumentStream + contentType) accordingly.
    """
    didResolutionMetadata: DIDResolutionMetadata
    didDocument: Optional[DIDDocument]
    didDocumentMetadata: DIDDocumentMetadata
    didDocumentStream: Optional[str] = None

    @property
    def is_representation(self) -> bool:
        return self.didDocumentStream is not None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        resolution_metadata = self.didResolutionMetadata.to_dict()
        if not self.is_representation:
            # 7.1.2: contentType MUST NOT be present if resolve() was called
            resolution_metadata.pop("contentType", None)

        result = {"didResolutionMetadata": resolution_metadata}
        if self.is_representation:
            result["didDocumentStream"] = self.didDocumentStream
        else:
            result["didDocument"] = self.didDocument.to_dict() if self.didDocument else None
        result["didDocumentMetadata"] = self.didDocumentMetadata.to_dict()
        return result


class DIDResolver:
    """
    Universal DID Resolver for all thesis blockchain identity standards

    Implements W3C DID Core Resolution specification:
    https://www.w3.org/TR/did-core/#resolution
    """

    def __init__(self, blockchain_provider=None):
        """
        Initialize DID Resolver

        Args:
            blockchain_provider: Web3 provider for blockchain lookups
        """
        self.blockchain_provider = blockchain_provider
        self.cache = {}  # Simple cache for resolved DIDs

    def resolve(self, did: str) -> DIDResolutionResult:
        """
        Resolve a DID to a DID Document

        Args:
            did: The DID to resolve (e.g., "did:ethr:0x123...")

        Returns:
            DIDResolutionResult with document or error
        """
        start_time = time.time()

        try:
            # Parse DID (raises DIDResolutionError on syntax / method errors)
            method, identifier = self._parse_did(did)

            # Check cache
            if did in self.cache:
                cached = self.cache[did]
                # Update retrieval time
                cached.didResolutionMetadata.retrieved = xml_datetime_now()
                return cached

            # Resolve based on method
            if method == DIDMethod.ETHR:
                result = self._resolve_ethr(did, identifier)
            elif method == DIDMethod.NFT:
                result = self._resolve_nft(did, identifier)
            elif method == DIDMethod.KEY:
                result = self._resolve_key(did, identifier)
            elif method == DIDMethod.MOBI:
                result = self._resolve_mobi(did, identifier)
            else:
                # Method known but not implemented by this resolver
                raise DIDResolutionError(
                    "methodNotSupported",
                    f"DID method '{method.value}' is not supported")

            # Set retrieval time
            result.didResolutionMetadata.retrieved = xml_datetime_now()

            # Cache successful resolutions
            self.cache[did] = result

            # Log resolution time
            elapsed_ms = (time.time() - start_time) * 1000
            print(f"✅ Resolved {did} in {elapsed_ms:.2f}ms")

            return result

        except DIDResolutionError as e:
            return self._error_result(e.code, str(e))

        except Exception as e:
            return self._error_result("internalError", str(e))

    def resolve_representation(self, did: str,
                               accept: Optional[str] = None) -> DIDResolutionResult:
        """
        Resolve a DID to a serialised DID Document (DID Core resolveRepresentation)

        Args:
            did: The DID to resolve
            accept: Requested media type (resolution option "accept");
                    defaults to application/did+ld+json

        Returns:
            DIDResolutionResult whose didDocumentStream holds the
            representation ("" on error) and whose didResolutionMetadata
            carries its contentType
        """
        content_type = accept or DID_LD_JSON
        if content_type not in SUPPORTED_CONTENT_TYPES:
            return self._error_result(
                "representationNotSupported",
                f"Representation '{content_type}' is not supported "
                f"(supported: {', '.join(SUPPORTED_CONTENT_TYPES)})",
                representation=True)

        resolved = self.resolve(did)
        if resolved.didResolutionMetadata.error:
            return self._error_result(
                resolved.didResolutionMetadata.error,
                resolved.didResolutionMetadata.errorMessage,
                representation=True)

        return DIDResolutionResult(
            didResolutionMetadata=DIDResolutionMetadata(
                contentType=content_type,
                retrieved=resolved.didResolutionMetadata.retrieved
            ),
            didDocument=resolved.didDocument,
            didDocumentMetadata=resolved.didDocumentMetadata,
            didDocumentStream=resolved.didDocument.to_representation(content_type)
        )

    # DID Core spelling of the function name
    resolveRepresentation = resolve_representation

    @staticmethod
    def _error_result(code: str, message: Optional[str],
                      representation: bool = False) -> DIDResolutionResult:
        """
        Build an error result (DID Core 7.1): a single-keyword `error`, no
        contentType, an empty document / stream and empty document metadata.
        """
        return DIDResolutionResult(
            didResolutionMetadata=DIDResolutionMetadata(
                contentType=None,
                error=code,
                errorMessage=message
            ),
            didDocument=None,
            didDocumentMetadata=DIDDocumentMetadata(),
            didDocumentStream="" if representation else None
        )

    def _parse_did(self, did: str) -> Tuple[DIDMethod, str]:
        """
        Parse DID into method and identifier

        Validates the DID Core 3.1 ABNF first: a string that is not a DID
        (missing scheme, bad method-name, empty or malformed
        method-specific-id, DID URL with path/query/fragment) is
        "invalidDid"; a syntactically valid DID whose method this resolver
        does not implement is "methodNotSupported".
        """
        match = DID_SYNTAX.match(did) if isinstance(did, str) else None
        if match is None:
            raise DIDResolutionError("invalidDid", f"Invalid DID format: {did}")

        method = match.group("method")
        identifier = match.group("id")  # Everything after method

        try:
            method_enum = DIDMethod(method)
        except ValueError:
            raise DIDResolutionError(
                "methodNotSupported", f"Unsupported DID method: {method}")

        return method_enum, identifier

    def _resolve_ethr(self, did: str, identifier: str) -> DIDResolutionResult:
        """
        Resolve did:ethr (ERC-1056 Lightweight Identity)

        Format: did:ethr:<chainId>:<address>
        Example: did:ethr:0x1:0x1234567890abcdef1234567890abcdef12345678
        """
        # Parse chain ID and address
        parts = identifier.split(":")
        if len(parts) == 2:
            chain_id, address = parts
        elif len(parts) == 1:
            # Default to mainnet
            chain_id = "0x1"
            address = identifier
        else:
            raise DIDResolutionError("invalidDid", f"Invalid did:ethr format: {did}")

        # In production, would query ERC-1056 registry on blockchain
        # For thesis demo, construct minimal valid DID document

        verification_method_id = f"{did}#controller"

        verification_method = VerificationMethod(
            id=verification_method_id,
            type="EcdsaSecp256k1VerificationKey2019",
            controller=did,
            blockchainAccountId=f"eip155:{chain_id}:{address}"
        )

        did_document = DIDDocument(
            id=did,
            controller=did,
            verificationMethod=[verification_method],
            authentication=[verification_method_id],
            assertionMethod=[verification_method_id],
            created=xml_datetime_now(),
            versionId="1"
        )

        return DIDResolutionResult(
            didResolutionMetadata=DIDResolutionMetadata(),
            didDocument=did_document,
            didDocumentMetadata=DIDDocumentMetadata(
                created=did_document.created,
                versionId=did_document.versionId
            )
        )

    def _resolve_nft(self, did: str, identifier: str) -> DIDResolutionResult:
        """
        Resolve did:nft (ERC-721 NFT-based Identity)

        Format: did:nft:<chainId>:<contractAddress>:<tokenId>
        """
        parts = identifier.split(":")
        if len(parts) != 3:
            raise DIDResolutionError("invalidDid", f"Invalid did:nft format: {did}")

        chain_id, contract_address, token_id = parts

        # Would query ERC-721 contract for token owner
        verification_method_id = f"{did}#owner"

        verification_method = VerificationMethod(
            id=verification_method_id,
            type="EcdsaSecp256k1VerificationKey2019",
            controller=did,
            blockchainAccountId=f"eip155:{chain_id}:{contract_address}"
        )

        # Add NFT metadata service
        service = Service(
            id=f"{did}#nft-metadata",
            type="NFTMetadata",
            serviceEndpoint=f"https://api.opensea.io/api/v1/asset/{contract_address}/{token_id}"
        )

        did_document = DIDDocument(
            id=did,
            verificationMethod=[verification_method],
            authentication=[verification_method_id],
            service=[service],
            created=xml_datetime_now(),
            versionId="1"
        )

        return DIDResolutionResult(
            didResolutionMetadata=DIDResolutionMetadata(),
            didDocument=did_document,
            didDocumentMetadata=DIDDocumentMetadata(
                created=did_document.created
            )
        )

    def _resolve_key(self, did: str, identifier: str) -> DIDResolutionResult:
        """
        Resolve did:key (ERC-725 Proxy Account)

        Format: did:key:<chainId>:<proxyAddress>
        """
        parts = identifier.split(":")
        if len(parts) == 2:
            chain_id, proxy_address = parts
        elif len(parts) == 1:
            chain_id = "0x1"
            proxy_address = identifier
        else:
            raise DIDResolutionError("invalidDid", f"Invalid did:key format: {did}")

        verification_method_id = f"{did}#keys-1"

        verification_method = VerificationMethod(
            id=verification_method_id,
            type="EcdsaSecp256k1VerificationKey2019",
            controller=did,
            blockchainAccountId=f"eip155:{chain_id}:{proxy_address}"
        )

        did_document = DIDDocument(
            id=did,
            verificationMethod=[verification_method],
            authentication=[verification_method_id],
            assertionMethod=[verification_method_id],
            capabilityInvocation=[verification_method_id],
            created=xml_datetime_now()
        )

        return DIDResolutionResult(
            didResolutionMetadata=DIDResolutionMetadata(),
            didDocument=did_document,
            didDocumentMetadata=DIDDocumentMetadata(
                created=did_document.created
            )
        )

    def _resolve_mobi(self, did: str, identifier: str) -> DIDResolutionResult:
        """
        Resolve did:mobi (MOBI VID compliant)

        Format: did:mobi:<vin>
        Example: did:mobi:5YJ3E1EA0PF123456
        """
        if ":" in identifier:
            raise DIDResolutionError("invalidDid", f"Invalid did:mobi format: {did}")

        vin = identifier

        # MOBI VID uses VIN as identifier
        # Would query MOBI VID registry for birth certificate

        verification_method_id = f"{did}#manufacturer-key"

        verification_method = VerificationMethod(
            id=verification_method_id,
            type="EcdsaSecp256k1VerificationKey2019",
            controller=did,
            publicKeyHex="0x..."  # Would be from birth certificate
        )

        # MOBI VID service endpoints
        services = [
            Service(
                id=f"{did}#birth-certificate",
                type="MobiVidBirthCertificate",
                serviceEndpoint="ipfs://Qm..."  # IPFS hash of birth cert
            ),
            Service(
                id=f"{did}#lifecycle-events",
                type="MobiVidLifecycleEvents",
                serviceEndpoint="https://mobi-vid-registry.example.com/events"
            )
        ]

        did_document = DIDDocument(
            id=did,
            verificationMethod=[verification_method],
            authentication=[verification_method_id],
            service=services,
            created=xml_datetime_now(),
            alsoKnownAs=[f"vin:{vin}"]
        )

        return DIDResolutionResult(
            didResolutionMetadata=DIDResolutionMetadata(),
            didDocument=did_document,
            didDocumentMetadata=DIDDocumentMetadata(
                created=did_document.created
            )
        )

    def create_did(self, method: DIDMethod, **kwargs) -> Tuple[str, DIDDocument]:
        """
        Create a new DID

        Args:
            method: DID method to use
            **kwargs: Method-specific parameters

        Returns:
            Tuple of (DID string, DID Document)
        """
        if method == DIDMethod.ETHR:
            address = kwargs.get("address")
            chain_id = kwargs.get("chain_id", "0x1")
            did = f"did:ethr:{chain_id}:{address}"

        elif method == DIDMethod.MOBI:
            vin = kwargs.get("vin")
            did = f"did:mobi:{vin}"

        elif method == DIDMethod.NFT:
            chain_id = kwargs.get("chain_id", "0x1")
            contract = kwargs.get("contract_address")
            token_id = kwargs.get("token_id")
            did = f"did:nft:{chain_id}:{contract}:{token_id}"

        else:
            raise ValueError(f"Unsupported DID method: {method}")

        # Resolve to get DID document
        result = self.resolve(did)

        return did, result.didDocument


# ============ CLI Interface ============

def main():
    """CLI for testing DID resolution"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python did_resolver.py <DID>")
        print("\nExamples:")
        print("  python did_resolver.py did:ethr:0x1:0x1234567890abcdef1234567890abcdef12345678")
        print("  python did_resolver.py did:mobi:5YJ3E1EA0PF123456")
        print("  python did_resolver.py did:nft:0x1:0xabc:123")
        sys.exit(1)

    did = sys.argv[1]

    print(f"🔍 Resolving DID: {did}\n")

    resolver = DIDResolver()
    result = resolver.resolve(did)

    if result.didResolutionMetadata.error:
        print(f"❌ Error: {result.didResolutionMetadata.error}")
        print(f"   {result.didResolutionMetadata.errorMessage}")
    else:
        print("✅ DID Document:")
        print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
