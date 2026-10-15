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

Two resolution modes (stream H-R, 2026-10-15):

* **offline** (default, no RPC configured): the document is synthesised from
  the DID string alone; nothing is read from a chain. Every such result
  carries the non-standard resolution-metadata property
  ``cvinResolutionMode: "offline-synthesized"`` so that a consumer can tell
  it apart from a registry read.
* **on-chain** (``DIDResolver(rpc_url=..., ethr_registry=...,
  mobi_registry=...)``): did:ethr is resolved from an ERC-1056
  (EthereumDIDRegistry) contract by walking the ``changed[]`` /
  ``previousChange`` chain and replaying ``DIDOwnerChanged`` /
  ``DIDDelegateChanged`` / ``DIDAttributeChanged`` forward, following
  ethr-did-resolver's mapping; did:mobi:<salted VIN hash> is resolved through
  ``MOBIVIDRegistry.lookupByVINHash`` -> ``getVehicleDID`` and the vehicle's
  ERC-1056 state in the MOBI registry. On-chain mode fails closed: an RPC
  failure or an inconsistent registry gives ``internalError`` with no
  document, a DID for another chain gives ``notFound``; a document is never
  synthesised. Results carry ``cvinResolutionMode: "erc1056-registry"`` or
  ``"mobi-vid-registry"``.

Author: Nikhil Prakash
Thesis: MASc, UBC ECE
"""

import base64
import copy
import json
import hashlib
import re
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum


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


@dataclass
class VerificationMethod:
    """W3C DID Core Verification Method"""
    id: str
    type: str  # e.g., "EcdsaSecp256k1VerificationKey2019"
    controller: str
    publicKeyHex: Optional[str] = None
    publicKeyBase58: Optional[str] = None
    publicKeyBase64: Optional[str] = None  # ethr-did-resolver did/pub/.../base64
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


# Media type of the only representation this resolver produces
DID_LD_JSON = "application/did+ld+json"
SUPPORTED_CONTENT_TYPES = (DID_LD_JSON,)


def xml_datetime(dt: Optional[datetime] = None) -> str:
    """
    DID Core 7.1.3 datetime: XML Datetime normalised to UTC, without
    sub-second precision, e.g. ``2026-10-04T05:23:42Z`` (stream G-R, R4;
    was ``datetime.isoformat()`` with microseconds and ``+00:00``).
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class DIDResolutionMetadata:
    """
    W3C DID Resolution metadata (DID Core 7.1.2).

    Serialised by ``to_dict()``, which omits every property whose value is
    absent (stream G-R): ``error`` / ``errorMessage`` appear only when
    resolution failed (R1), ``contentType`` only on a successful
    ``resolve_representation()`` (R2: it MUST NOT be present for
    ``resolve()``), and no key is ever emitted with a null value (R3).

    ``cvinResolutionMode`` (stream H-R) is a NON-STANDARD extension property
    (DID Core 7.1.2 lets a resolver add properties beyond the common ones;
    it is not in the DID Specification Registries). It is set on every
    successful resolution: ``offline-synthesized`` (document built from the
    DID string, no chain read), ``erc1056-registry`` or ``mobi-vid-registry``
    (document built from registry state).
    """
    contentType: Optional[str] = None
    retrieved: Optional[str] = None
    error: Optional[str] = None
    errorMessage: Optional[str] = None
    cvinResolutionMode: Optional[str] = None

    def to_dict(self) -> Dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class DIDDocumentMetadata:
    """
    W3C DID Document metadata (DID Core 7.1.3).

    ``to_dict()`` omits absent properties (stream G-R, R3): ``None`` values,
    an empty ``equivalentId`` and ``deactivated`` unless it is ``True``
    (the property is OPTIONAL for a DID that is not deactivated). A failed
    resolution therefore serialises to the empty structure the spec requires.
    """
    created: Optional[str] = None
    updated: Optional[str] = None
    deactivated: bool = False
    versionId: Optional[str] = None
    nextUpdate: Optional[str] = None
    nextVersionId: Optional[str] = None
    equivalentId: List[str] = field(default_factory=list)
    canonicalId: Optional[str] = None

    def to_dict(self) -> Dict:
        out = {}
        for k, v in asdict(self).items():
            if v is None or v == []:
                continue
            if k == "deactivated" and v is not True:
                continue
            out[k] = v
        return out


@dataclass
class DIDResolutionResult:
    """W3C DID Resolution Result (output of resolve())"""
    didResolutionMetadata: DIDResolutionMetadata
    didDocument: Optional[DIDDocument]
    didDocumentMetadata: DIDDocumentMetadata

    def to_dict(self) -> Dict:
        """Convert to dictionary (absent properties omitted, see above)"""
        return {
            "didResolutionMetadata": self.didResolutionMetadata.to_dict(),
            "didDocument": self.didDocument.to_dict() if self.didDocument else None,
            "didDocumentMetadata": self.didDocumentMetadata.to_dict()
        }


@dataclass
class DIDRepresentationResult:
    """W3C DID Resolution Result (output of resolveRepresentation())"""
    didResolutionMetadata: DIDResolutionMetadata
    didDocumentStream: str
    didDocumentMetadata: DIDDocumentMetadata

    def to_dict(self) -> Dict:
        return {
            "didResolutionMetadata": self.didResolutionMetadata.to_dict(),
            "didDocumentStream": self.didDocumentStream,
            "didDocumentMetadata": self.didDocumentMetadata.to_dict()
        }


class DIDResolutionError(ValueError):
    """A resolution failure carrying a DID Core 7.1.2 error code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


# DID Core 3.1 ABNF:  did = "did:" method-name ":" method-specific-id
#   method-name        = 1*method-char ; %x61-7A / DIGIT
#   method-specific-id = *( *idchar ":" ) 1*idchar
#   idchar             = ALPHA / DIGIT / "." / "-" / "_" / pct-encoded
_IDCHAR = r"(?:[A-Za-z0-9._-]|%[0-9A-Fa-f]{2})"
_DID_RE = re.compile(
    rf"did:([a-z0-9]+):((?:{_IDCHAR}*:)*{_IDCHAR}+)")
_ETH_ADDRESS_RE = re.compile(r"0x[0-9a-fA-F]{40}")
_ETH_PUBKEY_RE = re.compile(r"0x0[23][0-9a-fA-F]{64}")
# did:ethr network names accepted by ethr-did-resolver -> EIP-155 chain id
_ETHR_NETWORKS = {
    "mainnet": 1, "ropsten": 3, "rinkeby": 4, "goerli": 5,
    "sepolia": 11155111, "dev": 1337, "development": 1337,
}


def parse_chain_id(chain: str, did: str) -> int:
    """
    Chain-id component of a did:ethr / did:key / did:nft DID -> decimal
    EIP-155 chain id, as CAIP-10 requires (``eip155:<decimal>:<address>``;
    review 02, S-10). Accepts hex (``0x7a69``), decimal (``31337``) or a
    did:ethr network name.
    """
    if re.fullmatch(r"0x[0-9a-fA-F]+", chain):
        return int(chain, 16)
    if re.fullmatch(r"[0-9]+", chain):
        return int(chain)
    if chain in _ETHR_NETWORKS:
        return _ETHR_NETWORKS[chain]
    raise DIDResolutionError("invalidDid",
                             f"invalid chain id {chain!r} in {did}")


# ============ On-chain (ERC-1056 / MOBI VID) support, stream H-R ============

MODE_OFFLINE = "offline-synthesized"
MODE_ERC1056 = "erc1056-registry"
MODE_MOBI = "mobi-vid-registry"

NULL_ADDRESS = "0x" + "0" * 40
SECP256K1_RECOVERY_CONTEXT = \
    "https://w3id.org/security/suites/secp256k1recovery-2020/v2"
SECP256K1_2019_CONTEXT = "https://w3id.org/security/suites/secp256k1-2019/v1"
RECOVERY_METHOD = "EcdsaSecp256k1RecoveryMethod2020"
_VINHASH_RE = re.compile(r"0x[0-9a-fA-F]{64}")

# The subset of the ERC-1056 ABI the resolver reads. Identical in
# 1_blockchain-identity/contracts/ERC1056/EthereumDIDRegistry.sol and
# contracts/MOBI/ERC1056Registry.sol (which adds DIDRevoked).
_ERC1056_ABI = [
    {"type": "function", "name": "identityOwner", "stateMutability": "view",
     "inputs": [{"name": "identity", "type": "address"}],
     "outputs": [{"name": "", "type": "address"}]},
    {"type": "function", "name": "changed", "stateMutability": "view",
     "inputs": [{"name": "", "type": "address"}],
     "outputs": [{"name": "", "type": "uint256"}]},
    {"type": "event", "name": "DIDOwnerChanged", "anonymous": False,
     "inputs": [
         {"name": "identity", "type": "address", "indexed": True},
         {"name": "owner", "type": "address", "indexed": False},
         {"name": "previousChange", "type": "uint256", "indexed": False}]},
    {"type": "event", "name": "DIDDelegateChanged", "anonymous": False,
     "inputs": [
         {"name": "identity", "type": "address", "indexed": True},
         {"name": "delegateType", "type": "bytes32", "indexed": False},
         {"name": "delegate", "type": "address", "indexed": False},
         {"name": "validTo", "type": "uint256", "indexed": False},
         {"name": "previousChange", "type": "uint256", "indexed": False}]},
    {"type": "event", "name": "DIDAttributeChanged", "anonymous": False,
     "inputs": [
         {"name": "identity", "type": "address", "indexed": True},
         {"name": "name", "type": "bytes32", "indexed": False},
         {"name": "value", "type": "bytes", "indexed": False},
         {"name": "validTo", "type": "uint256", "indexed": False},
         {"name": "previousChange", "type": "uint256", "indexed": False}]},
    {"type": "event", "name": "DIDRevoked", "anonymous": False,
     "inputs": [
         {"name": "identity", "type": "address", "indexed": True},
         {"name": "revokedAt", "type": "uint256", "indexed": False}]},
]
_ERC1056_EVENT_SIGS = {
    "DIDOwnerChanged": "DIDOwnerChanged(address,address,uint256)",
    "DIDDelegateChanged":
        "DIDDelegateChanged(address,bytes32,address,uint256,uint256)",
    "DIDAttributeChanged":
        "DIDAttributeChanged(address,bytes32,bytes,uint256,uint256)",
    "DIDRevoked": "DIDRevoked(address,uint256)",
}
_MOBI_ABI = [
    {"type": "function", "name": "lookupByVINHash", "stateMutability": "view",
     "inputs": [{"name": "vinHash", "type": "bytes32"}],
     "outputs": [{"name": "", "type": "address"}]},
    {"type": "function", "name": "getVehicleDID", "stateMutability": "view",
     "inputs": [{"name": "vehicleIdentity", "type": "address"}],
     "outputs": [{"name": "", "type": "string"}]},
]

# ethr-did-resolver (src/helpers.ts) attribute-name mapping:
#   did/pub/<algorithm>/<purpose>/<encoding>   purpose: veriKey|sigAuth|enc
#   did/svc/<serviceType>
_ATTR_NAME_RE = re.compile(r"^did/(pub|svc)/(\w+)(/(\w+))?(/(\w+))?$")
_LEGACY_ATTR_TYPES = {
    "sigAuth": "SignatureAuthentication2018",
    "veriKey": "VerificationKey2018",
    "enc": "KeyAgreementKey2019",
}
_LEGACY_ALGO_MAP = {
    "Secp256k1VerificationKey2018": "EcdsaSecp256k1VerificationKey2019",
    "Ed25519SignatureAuthentication2018": "Ed25519VerificationKey2018",
    "Secp256k1SignatureAuthentication2018":
        "EcdsaSecp256k1VerificationKey2019",
    "RSAVerificationKey2018": "RSAVerificationKey2018",
    "Ed25519VerificationKey2018": "Ed25519VerificationKey2018",
    "X25519KeyAgreementKey2019": "X25519KeyAgreementKey2019",
}
# Upper bound on the change-chain walk (one getLogs per changed block)
MAX_CHANGE_BLOCKS = 10_000

_B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _base58(data: bytes) -> str:
    n = int.from_bytes(data, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = _B58_ALPHABET[r] + out
    pad = len(data) - len(data.lstrip(b"\0"))
    return "1" * pad + out


def _bytes32_to_str(value: bytes) -> Optional[str]:
    try:
        return bytes(value).rstrip(b"\0").decode("ascii")
    except UnicodeDecodeError:
        return None


@dataclass
class ERC1056State:
    """Registry state of one identity, after forward replay of its events."""
    identity: str
    owner: str
    deactivated: bool
    delegates: List[Dict[str, Any]]        # veriKey/sigAuth, ordered
    keys: List[Dict[str, Any]]             # did/pub attributes, ordered
    services: List[Dict[str, Any]]         # did/svc attributes, ordered
    version_block: int                     # latest change block (0 = none)
    version_time: Optional[str]            # its timestamp, XML datetime


class ERC1056Reader:
    """
    Reads an identity's state from an ERC-1056 registry: one
    ``eth_getLogs`` per block of the ``changed[identity]`` /
    ``previousChange`` chain, then a forward replay (ethr-did-resolver
    semantics: the latest event per (delegateType, delegate) or
    (name, value) wins; an entry with ``validTo <= block.timestamp`` of the
    head block is removed; ``DIDOwnerChanged`` to 0x0 deactivates and stops
    the replay). All calls are pinned to one head block.
    """

    def __init__(self, w3, registry: str):
        from web3 import Web3
        self.w3 = w3
        self.address = Web3.to_checksum_address(registry)
        self.contract = w3.eth.contract(address=self.address,
                                        abi=_ERC1056_ABI)
        self.topics = {name: "0x" + Web3.keccak(text=sig).hex().removeprefix("0x")
                       for name, sig in _ERC1056_EVENT_SIGS.items()}
        self._by_topic = {t: n for n, t in self.topics.items()}

    def _decode(self, log) -> Tuple[str, Dict[str, Any]]:
        topic0 = log["topics"][0]
        topic0 = topic0.hex() if not isinstance(topic0, str) else topic0
        topic0 = "0x" + topic0.removeprefix("0x").lower()
        name = self._by_topic[topic0]
        ev = getattr(self.contract.events, name)().process_log(log)
        return name, dict(ev["args"])

    def read(self, identity: str, head: Dict[str, Any]) -> ERC1056State:
        from web3 import Web3
        identity = Web3.to_checksum_address(identity)
        block_id = head["number"]
        now = int(head["timestamp"])
        last = int(self.contract.functions.changed(identity)
                   .call(block_identifier=block_id))
        chain_owner = self.contract.functions.identityOwner(identity) \
            .call(block_identifier=block_id)

        history: List[Tuple[str, Dict[str, Any]]] = []
        revoked = False
        seen = set()
        current = last
        while current:
            if current in seen or len(seen) >= MAX_CHANGE_BLOCKS:
                raise DIDResolutionError(
                    "internalError",
                    f"ERC-1056 change chain of {identity} does not terminate "
                    f"(block {current})")
            seen.add(current)
            logs = self.w3.eth.get_logs({
                "address": self.address,
                "fromBlock": current, "toBlock": current,
                "topics": [list(self.topics.values()),
                           "0x" + identity[2:].lower().rjust(64, "0")],
            })
            if not logs:
                raise DIDResolutionError(
                    "internalError",
                    f"registry reports a change of {identity} in block "
                    f"{current} but that block has no ERC-1056 event")
            logs = sorted(logs, key=lambda lg: int(lg["logIndex"]))
            block_events = [self._decode(lg) for lg in logs]
            # previousChange values that point strictly backwards; a later
            # tx in the same block references this block (changed[] was
            # already advanced), MOBI's birth registration does the same.
            back = [int(a["previousChange"]) for n, a in block_events
                    if "previousChange" in a
                    and int(a["previousChange"]) < current]
            if any(n == "DIDRevoked" for n, _ in block_events):
                revoked = True
            history = block_events + history
            current = min(back) if back else 0

        owner = identity
        deactivated = revoked
        # Keyed like ethr-did-resolver's eventIndex. An entry keeps its
        # position and takes a new #delegate-N / #service-N number when it is
        # re-set while valid; it is dropped when an event makes it invalid.
        # N is the running count of valid delegate/pub (resp. svc) events,
        # so ids are stable when an unrelated entry is revoked.
        delegate_count = 0
        service_count = 0
        delegates: Dict[str, Dict[str, Any]] = {}
        keys: Dict[str, Dict[str, Any]] = {}
        services: Dict[str, Dict[str, Any]] = {}
        for name, a in history:
            if deactivated:
                break
            if name == "DIDOwnerChanged":
                owner = a["owner"]
                if int(owner, 16) == 0:
                    deactivated = True
            elif name == "DIDDelegateChanged":
                dtype = _bytes32_to_str(a["delegateType"])
                key = f"{dtype}-{a['delegate'].lower()}"
                if int(a["validTo"]) <= now:
                    delegates.pop(key, None)
                    continue
                delegate_count += 1
                if dtype in ("veriKey", "sigAuth"):
                    delegates[key] = {"type": dtype, "address": a["delegate"],
                                      "n": delegate_count}
            elif name == "DIDAttributeChanged":
                attr = _bytes32_to_str(a["name"]) or ""
                value = bytes(a["value"])
                key = f"{attr}-{value.hex()}"
                match = _ATTR_NAME_RE.match(attr)
                if match is None:
                    continue
                if int(a["validTo"]) <= now:
                    keys.pop(key, None)
                    services.pop(key, None)
                    continue
                entry = {"algorithm": match.group(2),
                         "purpose": match.group(4),
                         "encoding": match.group(6),
                         "value": value}
                if match.group(1) == "pub":
                    delegate_count += 1
                    entry["n"] = delegate_count
                    keys[key] = entry
                else:
                    service_count += 1
                    entry["n"] = service_count
                    services[key] = entry

        if not deactivated and Web3.to_checksum_address(owner) != chain_owner:
            raise DIDResolutionError(
                "internalError",
                f"registry inconsistent for {identity}: replayed owner "
                f"{owner} != identityOwner() {chain_owner}")

        version_time = None
        if last:
            blk = self.w3.eth.get_block(last)
            version_time = xml_datetime(
                datetime.fromtimestamp(int(blk["timestamp"]), timezone.utc))
        return ERC1056State(
            identity=identity, owner=Web3.to_checksum_address(owner),
            deactivated=deactivated,
            delegates=list(delegates.values()),
            keys=list(keys.values()), services=list(services.values()),
            version_block=last, version_time=version_time)


def erc1056_document(did: str, state: ERC1056State, chain_id: int,
                     controller_did: str,
                     controller_key_hex: Optional[str] = None
                     ) -> Tuple[DIDDocument, DIDDocumentMetadata]:
    """
    DID document for ``did`` from ERC-1056 state, following
    ethr-did-resolver (``#controller`` recovery method for the owner,
    ``#delegate-N`` for veriKey / sigAuth delegates and did/pub attributes,
    ``#service-N`` for did/svc attributes). ``controller_did`` is the DID
    of the current owner.
    """
    meta = DIDDocumentMetadata()
    if state.version_block:
        meta.versionId = str(state.version_block)
        meta.updated = state.version_time
    if state.deactivated:
        meta.deactivated = True
        return DIDDocument(id=did, context=["https://www.w3.org/ns/did/v1"]), \
            meta

    context = ["https://www.w3.org/ns/did/v1", SECP256K1_RECOVERY_CONTEXT]
    controller_id = f"{did}#controller"
    vms = [VerificationMethod(
        id=controller_id, type=RECOVERY_METHOD, controller=did,
        blockchainAccountId=f"eip155:{chain_id}:{state.owner}")]
    auth, assertion, key_agreement = [controller_id], [controller_id], []
    if controller_key_hex and state.owner == state.identity:
        key_id = f"{did}#controllerKey"
        vms.append(VerificationMethod(
            id=key_id, type="EcdsaSecp256k1VerificationKey2019",
            controller=did, publicKeyHex=controller_key_hex.removeprefix("0x")))
        auth.append(key_id)
        assertion.append(key_id)

    entries = [("delegate", d) for d in state.delegates] + \
        [("pub", k) for k in state.keys]
    entries.sort(key=lambda e: e[1]["n"])
    for kind, e in entries:
        vm_id = f"{did}#delegate-{e['n']}"
        if kind == "delegate":
            vms.append(VerificationMethod(
                id=vm_id, type=RECOVERY_METHOD, controller=did,
                blockchainAccountId=f"eip155:{chain_id}:{e['address']}"))
            assertion.append(vm_id)
            if e["type"] == "sigAuth":
                auth.append(vm_id)
            continue
        purpose = e["purpose"] or ""
        legacy = f"{e['algorithm']}{_LEGACY_ATTR_TYPES.get(purpose, purpose)}"
        vm_type = _LEGACY_ALGO_MAP.get(legacy, e["algorithm"])
        vm = VerificationMethod(id=vm_id, type=vm_type, controller=did)
        encoding = e["encoding"]
        if encoding in (None, "hex"):
            vm.publicKeyHex = e["value"].hex()
        elif encoding == "base58":
            vm.publicKeyBase58 = _base58(e["value"])
        elif encoding == "base64":
            vm.publicKeyBase64 = base64.b64encode(e["value"]).decode("ascii")
        else:
            continue  # unknown encoding: no key property to put it in
        vms.append(vm)
        if vm_type == "EcdsaSecp256k1VerificationKey2019" and \
                SECP256K1_2019_CONTEXT not in context:
            context.append(SECP256K1_2019_CONTEXT)
        if purpose == "enc":
            key_agreement.append(vm_id)
        else:
            assertion.append(vm_id)
            if purpose == "sigAuth":
                auth.append(vm_id)
    services = []
    for svc in state.services:
        raw = svc["value"].decode("utf-8", errors="replace")
        try:
            endpoint = json.loads(raw)
        except ValueError:
            endpoint = raw
        services.append(Service(id=f"{did}#service-{svc['n']}",
                                type=svc["algorithm"],
                                serviceEndpoint=endpoint))

    doc = DIDDocument(
        context=context, id=did,
        controller=controller_did,
        verificationMethod=vms, authentication=auth,
        assertionMethod=assertion, keyAgreement=key_agreement,
        service=services,
        updated=meta.updated, versionId=meta.versionId)
    return doc, meta


class DIDResolver:
    """
    Universal DID Resolver for all thesis blockchain identity standards

    Implements W3C DID Core Resolution specification:
    https://www.w3.org/TR/did-core/#resolution
    """

    def __init__(self, blockchain_provider=None,
                 cache_ttl_s: Optional[float] = None,
                 rpc_url: Optional[str] = None,
                 ethr_registry: Optional[str] = None,
                 mobi_registry: Optional[str] = None,
                 chain_id: Optional[int] = None,
                 rpc_timeout_s: float = 10.0):
        """
        Initialize DID Resolver

        Args:
            blockchain_provider: a web3 ``Web3`` instance (or a web3 provider)
                to read registries through; alternative to ``rpc_url``
            cache_ttl_s: cache lifetime in seconds (None = never expires).
                In on-chain mode results are cached only when this is set,
                so a registry change is never hidden by a stale entry.
            rpc_url: JSON-RPC endpoint. Together with ``ethr_registry`` and /
                or ``mobi_registry`` it switches the resolver to on-chain
                mode. Without any of them the resolver is offline (default).
            ethr_registry: ERC-1056 (EthereumDIDRegistry) address for did:ethr
            mobi_registry: MOBIVIDRegistry address for did:mobi
            chain_id: EIP-155 chain id the registries live on. If given, the
                node's ``eth_chainId`` must match (else internalError);
                otherwise it is taken from the node.
            rpc_timeout_s: HTTP timeout per JSON-RPC request
        """
        self.blockchain_provider = blockchain_provider
        self.cache_ttl_s = cache_ttl_s
        # did -> (stored_at_monotonic, private copy of the result). Callers
        # only ever receive deep copies, so mutating a returned result
        # cannot poison later resolutions (review 02, S-10).
        self.cache: Dict[str, Tuple[float, "DIDResolutionResult"]] = {}

        self.ethr_registry = ethr_registry
        self.mobi_registry = mobi_registry
        self.configured_chain_id = chain_id
        self.w3 = None
        has_node = rpc_url is not None or blockchain_provider is not None
        has_registry = ethr_registry is not None or mobi_registry is not None
        if has_node != has_registry:
            raise ValueError(
                "on-chain mode needs an RPC (rpc_url or blockchain_provider) "
                "and at least one registry address (ethr_registry / "
                "mobi_registry); pass neither for offline mode")
        if has_node:
            from web3 import Web3
            if rpc_url is not None:
                self.w3 = Web3(Web3.HTTPProvider(
                    rpc_url, request_kwargs={"timeout": rpc_timeout_s}))
            elif isinstance(blockchain_provider, Web3):
                self.w3 = blockchain_provider
            else:
                self.w3 = Web3(blockchain_provider)
            for addr in (ethr_registry, mobi_registry):
                if addr is not None and not _ETH_ADDRESS_RE.fullmatch(addr):
                    raise ValueError(f"invalid registry address {addr!r}")

    @property
    def on_chain(self) -> bool:
        """True when the resolver reads registries (not offline mode)."""
        return self.w3 is not None

    # ---- on-chain helpers ----

    def _chain_head(self, did: str, did_chain_id: int) -> Dict[str, Any]:
        """
        eth_chainId check and the head block all reads are pinned to.
        A DID for another chain -> notFound; RPC failure -> internalError.
        """
        try:
            node_chain = int(self.w3.eth.chain_id)
        except Exception as e:
            raise DIDResolutionError(
                "internalError",
                f"RPC failure reading eth_chainId: {type(e).__name__}: {e}"
            ) from None
        if self.configured_chain_id is not None and \
                node_chain != int(self.configured_chain_id):
            raise DIDResolutionError(
                "internalError",
                f"node reports chain {node_chain}, resolver is configured "
                f"for chain {self.configured_chain_id}")
        if did_chain_id != node_chain:
            raise DIDResolutionError(
                "notFound",
                f"{did} names chain {did_chain_id}; this resolver reads the "
                f"registry on chain {node_chain} only")
        try:
            return dict(self.w3.eth.get_block("latest"))
        except Exception as e:
            raise DIDResolutionError(
                "internalError",
                f"RPC failure reading the head block: {type(e).__name__}: {e}"
            ) from None

    def _read_erc1056(self, registry: str, identity: str,
                      head: Dict[str, Any]) -> ERC1056State:
        try:
            return ERC1056Reader(self.w3, registry).read(identity, head)
        except DIDResolutionError:
            raise
        except Exception as e:
            raise DIDResolutionError(
                "internalError",
                f"ERC-1056 registry read failed: {type(e).__name__}: {e}"
            ) from None

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
            # Parse DID
            method, identifier = self._parse_did(did)

            # Check cache
            if did in self.cache:
                stored_at, cached = self.cache[did]
                if self.cache_ttl_s is None or \
                        time.monotonic() - stored_at <= self.cache_ttl_s:
                    result = copy.deepcopy(cached)
                    result.didResolutionMetadata.retrieved = \
                        xml_datetime()
                    return result
                del self.cache[did]

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
                # Method not supported
                result = DIDResolutionResult(
                    didResolutionMetadata=DIDResolutionMetadata(
                        error="methodNotSupported",
                        errorMessage=f"DID method '{method.value}' is not supported"
                    ),
                    didDocument=None,
                    didDocumentMetadata=DIDDocumentMetadata()
                )

            # Set retrieval time
            result.didResolutionMetadata.retrieved = xml_datetime()

            # Cache successful resolutions (a private copy). On-chain
            # results only with an explicit TTL: registry state changes.
            if not result.didResolutionMetadata.error and \
                    (self.cache_ttl_s is not None or
                     result.didResolutionMetadata.cvinResolutionMode
                     == MODE_OFFLINE):
                self.cache[did] = (time.monotonic(), copy.deepcopy(result))

            # Log resolution time
            elapsed_ms = (time.time() - start_time) * 1000
            print(f"✅ Resolved {did} in {elapsed_ms:.2f}ms")

            return result

        except DIDResolutionError as e:
            # invalidDid / methodNotSupported (DID Core 7.1.2). Before
            # review 02 every parse failure surfaced as internalError and
            # the methodNotSupported branch above was unreachable.
            return DIDResolutionResult(
                didResolutionMetadata=DIDResolutionMetadata(
                    error=e.code,
                    errorMessage=str(e)
                ),
                didDocument=None,
                didDocumentMetadata=DIDDocumentMetadata()
            )
        except Exception as e:
            return DIDResolutionResult(
                didResolutionMetadata=DIDResolutionMetadata(
                    error="internalError",
                    errorMessage=str(e)
                ),
                didDocument=None,
                didDocumentMetadata=DIDDocumentMetadata()
            )

    def resolve_representation(self, did: str,
                               accept: str = DID_LD_JSON
                               ) -> DIDRepresentationResult:
        """
        DID Core 7.1 ``resolveRepresentation(did, resolutionOptions)``.

        Resolves ``did`` with ``resolve()`` and serialises the document in
        the representation named by ``accept`` (only
        ``application/did+ld+json`` is produced). On success the resolution
        metadata carries ``contentType``; on failure it carries ``error`` and
        the stream is empty.
        """
        if accept not in SUPPORTED_CONTENT_TYPES:
            return DIDRepresentationResult(
                didResolutionMetadata=DIDResolutionMetadata(
                    retrieved=xml_datetime(),
                    error="representationNotSupported",
                    errorMessage=f"representation {accept!r} is not supported"
                ),
                didDocumentStream="",
                didDocumentMetadata=DIDDocumentMetadata()
            )
        result = self.resolve(did)
        meta = result.didResolutionMetadata
        if meta.error or result.didDocument is None:
            return DIDRepresentationResult(
                didResolutionMetadata=meta,
                didDocumentStream="",
                didDocumentMetadata=DIDDocumentMetadata()
            )
        meta.contentType = accept
        return DIDRepresentationResult(
            didResolutionMetadata=meta,
            didDocumentStream=json.dumps(result.didDocument.to_dict()),
            didDocumentMetadata=result.didDocumentMetadata
        )

    def _parse_did(self, did: str) -> Tuple[DIDMethod, str]:
        """
        Parse DID into method and identifier.

        Raises DIDResolutionError("invalidDid") for strings that violate
        the DID Core 3.1 ABNF, and DIDResolutionError("methodNotSupported")
        for a syntactically valid DID of a method this resolver lacks.
        """
        if not isinstance(did, str):
            raise DIDResolutionError("invalidDid", "DID must be a string")
        match = _DID_RE.fullmatch(did)
        if match is None:
            raise DIDResolutionError("invalidDid",
                                     f"Invalid DID format: {did}")
        method, identifier = match.group(1), match.group(2)

        try:
            method_enum = DIDMethod(method)
        except ValueError:
            raise DIDResolutionError(
                "methodNotSupported",
                f"DID method '{method}' is not supported") from None

        return method_enum, identifier

    def _resolve_ethr(self, did: str, identifier: str) -> DIDResolutionResult:
        """
        Resolve did:ethr (ERC-1056 Lightweight Identity)

        Format: did:ethr:<chainId>:<address>
        Example: did:ethr:0x1:0x1234567890abcdef1234567890abcdef12345678
        """
        # Parse chain ID and address (or compressed public key, which the
        # did:ethr spec also allows as the identifier)
        parts = identifier.split(":")
        if len(parts) == 2:
            chain, address = parts
            did_prefix = f"did:ethr:{chain}:"
        elif len(parts) == 1:
            # Default to mainnet
            chain = "0x1"
            address = identifier
            did_prefix = "did:ethr:"
        else:
            raise DIDResolutionError(
                "invalidDid", f"did:ethr takes [<chainId>:]<address>: {did}")
        chain_id = parse_chain_id(chain, did)

        public_key_hex = None
        if _ETH_PUBKEY_RE.fullmatch(address):
            public_key_hex = address
            address = self._address_from_compressed_key(address, did)
        elif not _ETH_ADDRESS_RE.fullmatch(address):
            raise DIDResolutionError(
                "invalidDid",
                f"did:ethr identifier must be a 0x-prefixed 20-byte address "
                f"or 33-byte compressed public key: {did}")

        if self.on_chain:
            # Stream H-R: read the ERC-1056 registry; fail closed.
            if self.ethr_registry is None:
                raise DIDResolutionError(
                    "methodNotSupported",
                    "this on-chain resolver has no ERC-1056 registry "
                    "configured for did:ethr (ethr_registry)")
            head = self._chain_head(did, chain_id)
            state = self._read_erc1056(self.ethr_registry, address, head)
            controller_did = did if state.owner == state.identity else \
                f"{did_prefix}{state.owner.lower()}"
            doc, meta = erc1056_document(did, state, chain_id,
                                         controller_did, public_key_hex)
            return DIDResolutionResult(
                didResolutionMetadata=DIDResolutionMetadata(
                    cvinResolutionMode=MODE_ERC1056),
                didDocument=doc,
                didDocumentMetadata=meta)

        # Offline mode (default): no registry read. The document below is
        # synthesised from the DID string and labelled as such.

        verification_method_id = f"{did}#controller"

        verification_method = VerificationMethod(
            id=verification_method_id,
            type="EcdsaSecp256k1VerificationKey2019",
            controller=did,
            publicKeyHex=public_key_hex,
            # CAIP-10: eip155:<decimal chain id>:<address>
            blockchainAccountId=f"eip155:{chain_id}:{address}"
        )

        did_document = DIDDocument(
            id=did,
            controller=did,
            verificationMethod=[verification_method],
            authentication=[verification_method_id],
            assertionMethod=[verification_method_id],
            created=xml_datetime(),
            versionId="1"
        )

        return DIDResolutionResult(
            didResolutionMetadata=DIDResolutionMetadata(
                cvinResolutionMode=MODE_OFFLINE),
            didDocument=did_document,
            didDocumentMetadata=DIDDocumentMetadata(
                created=did_document.created,
                versionId=did_document.versionId
            )
        )

    @staticmethod
    def _address_from_compressed_key(key_hex: str, did: str) -> str:
        """Ethereum address of a compressed secp256k1 public key."""
        try:
            from eth_keys import keys
            return keys.PublicKey.from_compressed_bytes(
                bytes.fromhex(key_hex[2:])).to_checksum_address()
        except Exception:
            raise DIDResolutionError(
                "invalidDid",
                f"identifier is not a valid secp256k1 public key: {did}"
            ) from None

    def _resolve_nft(self, did: str, identifier: str) -> DIDResolutionResult:
        """
        Resolve did:nft (ERC-721 NFT-based Identity)

        Format: did:nft:<chainId>:<contractAddress>:<tokenId>
        """
        parts = identifier.split(":")
        if len(parts) != 3:
            raise DIDResolutionError("invalidDid",
                                     f"Invalid did:nft format: {did}")

        chain, contract_address, token_id = parts
        chain_id = parse_chain_id(chain, did)

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
            created=xml_datetime(),
            versionId="1"
        )

        return DIDResolutionResult(
            didResolutionMetadata=DIDResolutionMetadata(
                cvinResolutionMode=MODE_OFFLINE),
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
            chain, proxy_address = parts
        elif len(parts) == 1:
            chain = "0x1"
            proxy_address = identifier
        else:
            raise DIDResolutionError("invalidDid",
                                     f"Invalid did:key format: {did}")
        chain_id = parse_chain_id(chain, did)

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
            created=xml_datetime()
        )

        return DIDResolutionResult(
            didResolutionMetadata=DIDResolutionMetadata(
                cvinResolutionMode=MODE_OFFLINE),
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
            created=xml_datetime(),
            alsoKnownAs=[f"vin:{vin}"]
        )

        return DIDResolutionResult(
            didResolutionMetadata=DIDResolutionMetadata(
                cvinResolutionMode=MODE_OFFLINE),
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
