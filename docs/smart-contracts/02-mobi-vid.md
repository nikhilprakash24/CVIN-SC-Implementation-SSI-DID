# 02 — MOBI VID (Vehicle Identity I / II) on an ERC-1056 base

This group holds the repo's application-profile implementation of the MOBI (Mobility Open Blockchain
Initiative) Vehicle Identity standards. It is three contracts in a single inheritance chain:
`ERC1056Registry` (a trimmed ERC-1056 "vehicle profile" DID registry with terminal revocation),
then `MOBIVIDRegistry` (VID I: manufacturer-issued birth certificates, salted VIN-hash lookup,
recorded ownership transfers, on-chain key anchoring, stored delegations), then
`MOBIVIDRegistryV2` (VID II: role-gated lifecycle events and multi-party attestations checked with
EIP-191 signatures). All three are shared single-instance registries: one deployment serves every
vehicle, and a vehicle is identified by an address rendered as `did:ethr:0x<chainId>:0x<addr>`.
The repo uses V2 as the "MOBI-VID-V2" option in the cross-standard gas, scaling, security and
lifecycle-parity comparisons. The Python layers wrap it in a W3C VC issuance and verification
pipeline (`2_w3c-ssi-layer/mobi-vid/`) and in the testbed's `IdentityProvider`
(`cv2x-testbed/identity/mobi_vid_provider.py`).

Source files (canonical paths; the byte-identical copies are covered in section 5):

| Contract | Path | Lines | pragma |
|---|---|---|---|
| ERC1056Registry | `1_blockchain-identity/contracts/MOBI/ERC1056Registry.sol` | 342 | `^0.8.0` |
| MOBIVIDRegistry | `1_blockchain-identity/contracts/MOBI/MOBIVIDRegistry.sol` | 662 | `^0.8.0` |
| MOBIVIDRegistryV2 | `1_blockchain-identity/contracts/MOBI/MOBIVIDRegistryV2.sol` | 601 | `^0.8.0` |

Inheritance: `MOBIVIDRegistryV2 is MOBIVIDRegistry is ERC1056Registry`. V2 also imports
OpenZeppelin `ECDSA` and `MessageHashUtils`.

---

## 1. Standards & protocols

### 1.1 ERC-1056: Ethereum Lightweight Identity (uPort `EthereumDIDRegistry`)

- **What it is:** EIP-1056 (Pelle Braendgaard, Joel Torstensson, 2018). It is a Draft that the EIP
  site now lists as Stagnant. It defines one shared registry where any Ethereum address is an
  identity, with no creation transaction. The canonical interface:
  `identityOwner(address)`, `owners`, `delegates[identity][type][delegate]`, `changed`, `nonce`,
  `validDelegate(identity,type,delegate)`, `changeOwner`/`changeOwnerSigned`,
  `addDelegate`/`addDelegateSigned`, `revokeDelegate`/`revokeDelegateSigned`,
  `setAttribute`/`setAttributeSigned`, `revokeAttribute`/`revokeAttributeSigned`, plus the events
  `DIDOwnerChanged`, `DIDDelegateChanged` and `DIDAttributeChanged`, each carrying
  `previousChange` so a resolver can walk the per-identity change list backwards. It underlies
  the `did:ethr` DID method.
- **How faithful `ERC1056Registry.sol` is:** the header says it is "Based on uport-project/ethr-did-registry" (L8).
  - *Kept:* the storage `owners`, `changed` and `nonce` (L59–61). The three events have the
    canonical field layout (L24–44). `identityOwner` falls back to the identity itself (L91–97).
    Each mutator emits an event with `previousChange = changed[identity]` and then sets
    `changed = block.number`. The internal `(identity, actor, …)` / public `(identity, …)` split
    is kept. Revoking a delegate or attribute emits `validTo = block.timestamp` (L177, L243), as
    canonical does.
  - *Removed:* every `*Signed` meta-transaction variant. `nonce` is declared (L61) but never read
    or written, which the sandbox adapter header also notes. The `delegates` mapping and
    `validDelegate` are also missing, so in the base contract delegations exist only as events;
    `MOBIVIDRegistry` adds them back (section 3.2).
  - *Extended (CVIN):* `revoked`/`revokedAt` storage (L62–65). A terminal
    `revokeIdentity` (L264) that emits a new `DIDRevoked(identity, revokedAt, previousChange)`
    event (L52–56). That event carries `previousChange`, so the change list stays walkable through
    the revocation (defect D21). A `notRevoked` modifier (L81) freezes every mutator after
    revocation (D16/D21, REVIEW_02 K-3). Convenience functions `registerVehicle` (L285) and
    `updateVehicleKey` (L306), plus the views `isRevoked`, `lastChanged` and `getIdentityInfo`.
  - *Naming deviation:* the vehicle key attribute name is `keccak256("did/pub/secp256k1/veriKey/base64")`
    (L293, L310; `MOBIVIDRegistry.VEHICLE_KEY_ATTRIBUTE` L321). The did:ethr convention stores the
    name as the ASCII string right-padded into `bytes32`. A stock `ethr-did-resolver` therefore
    does not recognise this attribute as a verification method. The repo's own resolvers
    (`mobi_vid_provider._resolve_key_on_chain`, `erc1056_provider._resolve_key_from_events`) match
    the keccak name instead.
  - `changeOwner(address,address)` is `virtual` (L122), so MOBI can block it for born vehicles.
    The internal `addDelegate` and `revokeDelegate` are `virtual` too, so MOBI can store delegations.

### 1.2 MOBI VID I (Vehicle Birth Certificate) and VID II (Vehicle Lifecycle)

- **What it is:** MOBI's Vehicle Identity working-group standards. VID I (2019) defines an
  immutable birth record anchoring a vehicle's identity. VID II (2020/21) covers lifecycle events
  such as registration, maintenance and ownership history. They are consortium documents, not
  EIPs, and they define no Solidity ABI. The repo's reading of them is in `MOBI_VID_RESEARCH.md`,
  `MOBI_VID1_TECHNICAL_SPEC.md` and `MOBI_VID2_SSI_DESIGN.md` (repo root). Every interface below
  is the repo's own design, labelled "CVIN extension / MOBI profile" in the tables.
- **How the code relates to the repo's own spec docs.** Both docs are dated 2025-11-10 and marked
  "Design Phase"; the code has moved past them:
  - `MOBI_VID1_TECHNICAL_SPEC.md` §2 embeds a full draft `MOBIVIDRegistry` (from about L155). This
    is a **stale copy**. It writes birth attributes with `type(uint256).max` validity (spec L299).
    That overflows `block.timestamp + validity` and reverts, the "V1 overflow bug" the code fixes
    with `PERMANENT_ATTRIBUTE_VALIDITY = 100 * 365 days` (MOBIVIDRegistry L65). The draft also
    names the lookup `findVehicleByVINHash` (spec L380); the code has `lookupByVINHash` (L506).
    Its `VehicleBirth` struct has no `blockNumber`. Its VIN privacy section promises a
    zero-knowledge VIN proof tier, which was never built (see the
    `2_w3c-ssi-layer/mobi-vid/README.md` status table).
  - `MOBI_VID2_SSI_DESIGN.md` "Lifecycle Events" (L37ff) lists an `OWNERSHIP_TRANSFER` event type
    and puts `bytes32[] attestations` inside the event struct. Its `IssuerRole` has no `NONE`. The
    code (V2 L35–62) has no `OWNERSHIP_TRANSFER`, adds `REGISTRATION` and `DECOMMISSION`
    (11 types), adds `NONE` (9 roles), and keeps attestations in a separate
    `eventAttestations[eventId]` array plus a `credentialHash` field.
  - Both docs call `birthCertHash`/`dataHash` "IPFS hashes". The SSI layer README says these are
    keccak256 content hashes of the canonicalised, signed VC, and that no IPFS exists in the repo.
  - The VIN-hash formula differs from one caller to the next, and the contract does not enforce
    any of them:

    | Where | Formula |
    |---|---|
    | Contract comment (V1 L33) | `SHA256(VIN + salt + vehicleDID)` |
    | `mobi_vid_provider._hash_vin` | the same, with a random 16-byte hex salt |
    | `2_w3c-ssi-layer/mobi-vid` | `SHA256(VIN ‖ ":" ‖ salt)` with a 32-byte salt |
    | `deploy_mobi_vid.js` | `keccak256(VIN+"salt"+identity)` |
    | `benchmark_gas.js` and the sandbox adapter | unsalted `keccak256(vin)` |

### 1.3 W3C DID Core v1.0 and did:ethr

- **W3C DID Core** became a Recommendation in July 2022. The contracts only *produce the
  identifier*: `getVehicleDID` (V1 L598) returns `did:ethr:0x<minimal chainId hex>:0x<40 lowercase hex>`.
  That matches the did:ethr method syntax with a hex chain id; it was fixed by D10 / Review-02 K-15
  and is tested in `MOBIVIDRegistry.regression.test.js`. The DID document is built off-chain
  by replaying the ERC-1056 events (`2_w3c-ssi-layer/did-resolution/did_resolver.py`, on-chain mode,
  `cvinResolutionMode: "mobi-vid-registry"`). The resolver also accepts `did:mobi:<salted VIN hash>`
  and maps it through `lookupByVINHash`, then `getVehicleDID`. The SSI layer README rejects
  `did:mobi:<VIN>`, with the raw VIN, on privacy grounds.

### 1.4 W3C Verifiable Credentials Data Model

- VC Data Model v1.1 is a W3C Recommendation, superseded by v2.0. V2's header claims "W3C
  Verifiable Credentials v1.1" (L16). On-chain this amounts to the opaque `bytes32` fields
  `credentialHash` (V2 L77) and `birthCertHash` (V1 L35), with no VC parsing. Issuance, the
  schemas and verification all live in `2_w3c-ssi-layer/mobi-vid/` together with
  `2_w3c-ssi-layer/verifiable-credentials/`.

### 1.5 EIP-191 signed data, EIP-2 low-s (via OpenZeppelin)

- EIP-191 (Final) defines the `"\x19Ethereum Signed Message:\n32"` prefix. `attestEvent`
  (V2 L338) recovers the signer of
  `toEthSignedMessageHash(keccak256(abi.encodePacked(address(this), block.chainid, vehicleIdentity, eventId)))`
  and requires it to equal `msg.sender` (L369–376). Binding the contract address and chain id is
  an ad-hoc domain separation, not EIP-712. OpenZeppelin `ECDSA.recover` rejects malleable high-s
  signatures and the zero address. Earlier revisions stored the signature without checking it.

---

## 2. Lifecycle at a glance

```
deploy MOBIVIDRegistry(V2)          deployer = registryAuthority + auto-authorised manufacturer
  (V2) authorizeIssuer(addr, role)  registry authority grants roles (SERVICE_CENTER, POLICE, ...)
  authorizeManufacturer(addr)       optional extra OEMs
registerVehicleBirth(...)           OEM: birth cert, vinHash->identity, owners[id]=firstOwner,
                                    optional birth attribute, DIDOwnerChanged
anchorVehicleKey(id, pubkey)        OEM once before first sale, or owner any time
addDelegate(id,"veriKey",d,ttl)     owner: stored delegation (needed for org attestations)
(V2) recordLifecycleEvent(...)      role-gated issuer -> eventId
(V2) attestEvent(eventId,id,sig)    role holder that is the owner or a veriKey delegate
transferVehicleOwnership(...)       owner -> OwnershipTransfer record + DIDOwnerChanged
resolve: getVehicleInfo / getVehicleDID / lookupByVINHash / getCompleteHistory / event walk from lastChanged
revokeIdentity(id)                  owner: terminal, DIDRevoked, everything frozen
```

---

## 3. Per-contract reference

### 3.1 `ERC1056Registry` — `1_blockchain-identity/contracts/MOBI/ERC1056Registry.sol`

**Purpose.** An event-only ERC-1056 DID registry, trimmed and extended for vehicles. The testbed
also deploys it on its own as the "ERC-1056 / vehicle profile" option (`cv2x-testbed/scripts/deploy.js`,
`erc1056_provider.py`, `sandbox/options/erc-1056-vehicle/`). In this group it is the base class.

**Inheritance/imports:** none.

**State variables**

| Name | Type | Line | Notes |
|---|---|---|---|
| `owners` | `mapping(address=>address)` public | 59 | 0 means self-owned |
| `changed` | `mapping(address=>uint)` public | 60 | block of the last change (head of the linked list) |
| `nonce` | `mapping(address=>uint)` public | 61 | **unused** (no signed variants) |
| `revoked` | `mapping(address=>bool)` public | 62 | CVIN extension |
| `revokedAt` | `mapping(address=>uint)` public | 65 | timestamp of the revocation, CVIN extension |

**Events:** `DIDOwnerChanged(identity indexed, owner, previousChange)` L24, ERC-1056.
`DIDDelegateChanged(identity indexed, delegateType, delegate, validTo, previousChange)` L30, ERC-1056.
`DIDAttributeChanged(identity indexed, name, value, validTo, previousChange)` L38, ERC-1056.
`DIDRevoked(identity indexed, revokedAt, previousChange)` L52, CVIN extension.

**Modifiers:** `onlyOwner(identity, actor)` L67 requires `actor == identityOwner(identity)`.
`notRevoked(identity)` L81.

**Functions**

| Signature | Vis / mut | What it does | Access control | Events | Origin |
|---|---|---|---|---|---|
| `identityOwner(address identity) returns (address)` L91 | public view | Returns `owners[identity]`, or `identity` if unset | — | — | ERC-1056 |
| `isRevoked(address) returns (bool)` L102 | public view | Returns the `revoked` flag | — | — | CVIN extension |
| `changeOwner(address identity, address actor, address newOwner)` L110 | internal | Sets `owners`, emits, bumps `changed` | `onlyOwner(identity, actor)`, `notRevoked` | DIDOwnerChanged | ERC-1056 |
| `changeOwner(address identity, address newOwner)` L122 | public **virtual** | Calls the internal version with `msg.sender` | owner | DIDOwnerChanged | ERC-1056 |
| `addDelegate(identity, actor, bytes32 delegateType, address delegate, uint validity)` L135 | internal virtual | Emits a delegate event with `validTo = now + validity`; nothing stored | onlyOwner, notRevoked | DIDDelegateChanged | ERC-1056 (event-only) |
| `addDelegate(identity, delegateType, delegate, validity)` L155 | public | Wrapper | owner | DIDDelegateChanged | ERC-1056 |
| `revokeDelegate(identity, actor, delegateType, delegate)` L167 | internal virtual | Emits with `validTo = now` | onlyOwner, notRevoked | DIDDelegateChanged | ERC-1056 |
| `revokeDelegate(identity, delegateType, delegate)` L184 | public | Wrapper | owner | DIDDelegateChanged | ERC-1056 |
| `setAttribute(identity, actor, bytes32 name, bytes value, uint validity)` L201 | internal | Emits an attribute event with `validTo = now + validity` (checked arithmetic) | onlyOwner, notRevoked | DIDAttributeChanged | ERC-1056 |
| `setAttribute(identity, name, bytes calldata value, validity)` L221 | public | Wrapper | owner | DIDAttributeChanged | ERC-1056 |
| `revokeAttribute(identity, actor, name, value)` L233 | internal | Emits with `validTo = now` | onlyOwner, notRevoked | DIDAttributeChanged | ERC-1056 |
| `revokeAttribute(identity, name, bytes calldata value)` L250 | public | Wrapper | owner | DIDAttributeChanged | ERC-1056 |
| `revokeIdentity(address identity)` L264 | public | Single-shot terminal revocation: sets `revoked` and `revokedAt`, emits, bumps `changed` | `onlyOwner(identity, msg.sender)`; reverts if already revoked | DIDRevoked | CVIN extension |
| `lastChanged(address) returns (uint)` L277 | public view | Returns `changed[identity]` | — | — | CVIN extension (canonical exposes `changed`) |
| `registerVehicle(address vehicleIdentity, bytes calldata publicKey)` L285 | public | Requires not revoked and self-owned, then `setAttribute(keccak("did/pub/secp256k1/veriKey/base64"), key, 1 year)` | effectively `msg.sender == vehicleIdentity`, because `setAttribute` is onlyOwner with `actor = msg.sender` | DIDAttributeChanged | CVIN extension |
| `updateVehicleKey(address vehicleIdentity, bytes calldata newPublicKey)` L306 | public | Writes a new key attribute (1 year); **does not revoke the old one** (comment L312–314) | onlyOwner, notRevoked | DIDAttributeChanged | CVIN extension |
| `getIdentityInfo(address) returns (owner, lastChangedBlock, isRevoked, revokedTimestamp)` L329 | public view | Aggregate read | — | — | CVIN extension |

**Design notes / caveats**
- `registerVehicle` only guards on "still self-owned" (L290), so the same identity can call it
  again and publish another key. "Already registered" really means "ownership was transferred".
- Without stored delegations there is no on-chain `validDelegate`. Off-chain consumers must
  replay events to learn delegate validity.
- Revocation can only be done by the identity owner. No authority can revoke a vehicle.
- `previousChange` uses the same block-number linked-list semantics as canonical ERC-1056.
  Several changes in one block produce several logs under one `changed` value; the resolvers
  handle this by taking the minimum `previousChange` per block (e.g. `mobi_vid_provider.py`).

### 3.2 `MOBIVIDRegistry` (VID I) — `1_blockchain-identity/contracts/MOBI/MOBIVIDRegistry.sol`

**Purpose.** MOBI VID I birth certificates on top of ERC-1056. It adds manufacturer authorisation,
VIN-hash lookup, an ownership-transfer log that records odometer and authority, anchoring of the
vehicle key, stored delegations (needed for V2 attestation consent) and a `did:ethr` string helper.

**Inheritance/imports:** `import "./ERC1056Registry.sol"`; `contract MOBIVIDRegistry is ERC1056Registry` (L24).

**Structs:**
- `VehicleBirth` (L32): `vinHash`, `encryptedVIN` (string), `birthCertHash`, `timestamp`,
  `manufacturer`, `firstOwner`, `blockNumber`, `exists`.
- `OwnershipTransfer` (L46): `from`, `to`, `timestamp`, `blockNumber`, `odometer`,
  `registrationAuthority` (string).

**State variables / constants**

| Name | Type | Line | Notes |
|---|---|---|---|
| `PERMANENT_ATTRIBUTE_VALIDITY` | `uint256 constant` = `100*365 days` | 65 | replaces the overflowing `type(uint256).max` |
| `registryAuthority` | `address` public | 70 | set to the deployer |
| `authorizedManufacturers` | `mapping(address=>bool)` public | 73 | |
| `vinHashToIdentity` | `mapping(bytes32=>address)` public | 76 | |
| `vehicleBirths` | `mapping(address=>VehicleBirth)` public | 79 | |
| `ownershipHistory` | `mapping(address=>OwnershipTransfer[])` public | 82 | the first owner is *not* an entry; history starts at the first transfer |
| `VEHICLE_KEY_ATTRIBUTE` | `bytes32 constant` = `keccak256("did/pub/secp256k1/veriKey/base64")` | 321 | same name the base convenience functions use |
| `vehicleKeyAnchored` | `mapping(address=>bool)` public | 324 | |
| `delegates` | `mapping(address=>mapping(bytes32=>mapping(address=>uint)))` public | 331 | identity ⇒ type ⇒ delegate ⇒ validTo, as in canonical ERC-1056 (WM-2 C2 / D54) |

**Events:**
- `VehicleBirthRegistered(vehicleIdentity indexed, vinHash indexed, manufacturer indexed, firstOwner, birthCertHash, timestamp)` L89
- `VehicleOwnershipTransferred(vehicleIdentity indexed, from indexed, to indexed, odometer, timestamp)` L101
- `ManufacturerAuthorized(manufacturer indexed, timestamp)` L112
- `ManufacturerAuthorizationRevoked(manufacturer indexed, timestamp)` L120
- `VehicleKeyAnchored(vehicleIdentity indexed, keyHash indexed, anchoredBy indexed, validTo)` L364
- Inherited: `DIDOwnerChanged`, `DIDAttributeChanged` and `DIDDelegateChanged` from the base.

**Modifiers:** `onlyRegistryAuthority` L127, `onlyAuthorizedManufacturer` L135,
`vehicleNotRegistered(id)` L143, `vehicleRegistered(id)` L151, plus the inherited
`onlyOwner` and `notRevoked`.

**Constructor** (L161): `registryAuthority = msg.sender`. It also authorises the deployer as a
manufacturer ("for testing", L163) and emits `ManufacturerAuthorized`.

**Functions**

| Signature | Vis / mut | What it does | Access control | Events | Origin |
|---|---|---|---|---|---|
| `authorizeManufacturer(address)` L174 | external | Grants manufacturer status; rejects the zero address and duplicates | onlyRegistryAuthority | ManufacturerAuthorized | CVIN ext. (MOBI profile) |
| `revokeManufacturerAuthorization(address)` L189 | external | Removes the grant | onlyRegistryAuthority | ManufacturerAuthorizationRevoked | CVIN ext. |
| `transferRegistryAuthority(address newAuthority)` L203 | external | One-step authority hand-over (non-zero check) | onlyRegistryAuthority | **none** | CVIN ext. |
| `registerVehicleBirth(address vehicleIdentity, bytes32 vinHash, string encryptedVIN, bytes32 birthCertHash, address firstOwner, bytes birthAttributes)` L227 | external | Rejects zero values, duplicate VIN hashes and any identity with DID history (`changed == 0`, K-4, L250). Stores the birth, maps the VIN hash, sets `owners[id] = firstOwner` **directly**, writes optional `mobi/vid/birth/attributes` with `firstOwner` as the ERC-1056 actor (L288–297), then emits | onlyAuthorizedManufacturer, vehicleNotRegistered | VehicleBirthRegistered, DIDOwnerChanged, (DIDAttributeChanged) | MOBI VID I |
| `addDelegate(identity, actor, type, delegate, validity)` L333 | internal override | Calls super (event), then stores `delegates[...] = now + validity` | inherited onlyOwner, notRevoked | DIDDelegateChanged | ERC-1056 (canonical storage restored) |
| `revokeDelegate(identity, actor, type, delegate)` L344 | internal override | Calls super, then sets the stored validTo to `now` | inherited | DIDDelegateChanged | ERC-1056 |
| `validDelegate(address identity, bytes32 delegateType, address delegate) returns (bool)` L356 | public view | `!revoked && delegates[..] > now` | — | — | ERC-1056 (plus a revocation check) |
| `anchorVehicleKey(address vehicleIdentity, bytes publicKey)` L389 | external | Accepts a 65- or 33-byte secp256k1 key. Writes the `VEHICLE_KEY_ATTRIBUTE` attribute with 100-year validity, using the owner as actor | vehicleRegistered, notRevoked; caller is the owner (any time) **or** the registering manufacturer, once, only while `ownershipHistory` is empty | DIDAttributeChanged, VehicleKeyAnchored | CVIN ext. (D11b) |
| `changeOwner(address identity, address newOwner)` L429 | public override | Reverts for born vehicles ("use transferVehicleOwnership"); otherwise plain ERC-1056 | owner (via super) | DIDOwnerChanged | ERC-1056, restricted (K-3) |
| `transferVehicleOwnership(address vehicleIdentity, address newOwner, uint256 odometer, string authority)` L448 | external | Pushes an `OwnershipTransfer`, then calls the internal `changeOwner` | vehicleRegistered, onlyOwner(msg.sender), not revoked, non-zero newOwner | DIDOwnerChanged, VehicleOwnershipTransferred | MOBI VID I/II |
| `getVehicleBirth(address) returns (VehicleBirth)` L492 | external view | Reverts if unregistered | — | — | MOBI VID I |
| `lookupByVINHash(bytes32) returns (address)` L506 | external view | Returns 0 if unknown | — | — | MOBI VID I |
| `getOwnershipHistory(address) returns (OwnershipTransfer[])` L519 | external view | | vehicleRegistered | — | CVIN ext. |
| `getOwnershipHistoryCount(address) returns (uint256)` L533 | external view | | — | — | CVIN ext. |
| `vehicleExists(address) returns (bool)` L546 | external view | | — | — | CVIN ext. |
| `getVehicleInfo(address) returns (birth, currentOwner, isRevoked, transferCount)` L562 | external view | Combined read | vehicleRegistered | — | CVIN ext. |
| `getVehicleDID(address) returns (string)` L598 | external view | `did:ethr:0x<chainid>:0x<addr>` | — | — | W3C DID / did:ethr helper |
| `_toHexString(uint256)` L622 | internal pure | Minimal lowercase hex ("0" for 0) | — | — | helper |
| `_toHexString(uint256, uint256 length)` L650 | internal pure | Zero-padded hex; reverts if it does not fit | — | — | helper |

**Design notes / security caveats**
- **Writes with the owner as actor, without the owner's signature.** `registerVehicleBirth` and
  `anchorVehicleKey` (manufacturer path) pass `firstOwner`/`owner` as the `actor` of the internal
  `setAttribute`. The ERC-1056 event then looks owner-authored even though the manufacturer sent
  it. This is intentional (comment L273–287) but weakens what an attribute event proves about
  consent.
- **Key-less vehicle identities.** The manufacturer picks `vehicleIdentity`. Callers derive it
  from the VIN (`mobi_vid_provider._generate_vehicle_identity` uses the first 20 bytes of
  `sha256(vin)`; the sandbox adapter uses `keccak256("cvin-mobi-vid:"+vin)`), so nobody holds its
  private key. Control comes only through `owners[]`.
- **The registering manufacturer keeps its rights after de-authorisation.** `anchorVehicleKey`
  checks `vehicleBirths[id].manufacturer`, not `authorizedManufacturers`. A de-authorised OEM can
  still anchor the first key before the first sale.
- **Single-EOA registry authority**, auto-authorised as a manufacturer. The authority transfer is
  one-step and emits no event.
- **`encryptedVIN` is public ciphertext** in contract storage; its confidentiality rests entirely
  on the off-chain AEAD (AES-256-GCM in the Python layers). `vinHash` is unsalted in
  `benchmark_gas.js` and the sandbox adapter, which makes it dictionary-attackable there. The
  contract cannot tell the difference.
- **Revocation is owner-only and terminal.** It is inherited unchanged, so an authority cannot
  decommission a vehicle. Once revoked, `transferVehicleOwnership` and `changeOwner` revert
  (tested in `MOBIVIDRegistry.regression.test.js`).
- The birth "immutability" means there is no update path for `vehicleBirths`. K-4 (L250) stops a
  manufacturer from re-birthing or taking over an identity that already has DID history.

### 3.3 `MOBIVIDRegistryV2` (VID II) — `1_blockchain-identity/contracts/MOBI/MOBIVIDRegistryV2.sol`

**Purpose.** Adds MOBI VID II lifecycle events: 11 event types issued under a role ⇒ event-type
permission matrix, each recorded with a VC hash, plus multi-party attestations that need the
owner's consent and an on-chain EIP-191 signature check.

**Inheritance/imports:** `MOBIVIDRegistry`; OpenZeppelin `ECDSA`, `MessageHashUtils` (L4–6).

**Enums:**
- `EventType` (L35): MAINTENANCE, REPAIR, ACCIDENT, RECALL, INSPECTION, MODIFICATION,
  THEFT_REPORT, RECOVERY, INSURANCE_CLAIM, REGISTRATION, DECOMMISSION (ordinals 0–10).
- `IssuerRole` (L52): NONE, MANUFACTURER, DEALER, SERVICE_CENTER, INSURANCE_COMPANY,
  GOVERNMENT_DMV, POLICE, INSPECTION_STATION, OWNER (ordinals 0–8).
- Note: `IssuerRole.MANUFACTURER` is separate from `authorizedManufacturers` in V1.

**Structs:**
- `LifecycleEvent` (L70): `eventId`, `eventType`, `issuer`, `timestamp`, `odometer`, `dataHash`,
  `credentialHash`, `verified`, `jurisdiction`, `blockNumber`.
- `EventAttestation` (L87): `attester`, `role`, `signature` (bytes), `timestamp`.

**State variables**

| Name | Type | Line |
|---|---|---|
| `authorizedIssuers` | `mapping(address=>IssuerRole)` public (one role per address) | 97 |
| `lifecycleEvents` | `mapping(address=>mapping(bytes32=>LifecycleEvent))` public | 100 |
| `vehicleEventIds` | `mapping(address=>bytes32[])` public | 103 |
| `eventAttestations` | `mapping(bytes32=>EventAttestation[])` public | 106 |
| `hasAttested` | `mapping(bytes32=>mapping(address=>bool))` public (D54) | 109 |
| `vehicleEventCount` | `mapping(address=>uint256)` public | 112 |
| `eventTypeCount` | `mapping(address=>mapping(EventType=>uint256))` public | 115 |
| `allowedIssuers` | `mapping(EventType=>mapping(IssuerRole=>bool))` public | 118 |

**Permission matrix** (`_initializeAllowedIssuers`, L539–582; no setter exists, so it is fixed at deploy):

| EventType | Allowed roles |
|---|---|
| MAINTENANCE | DEALER, SERVICE_CENTER, OWNER |
| REPAIR | DEALER, SERVICE_CENTER |
| ACCIDENT | POLICE, INSURANCE_COMPANY, OWNER |
| RECALL | MANUFACTURER |
| INSPECTION | INSPECTION_STATION, GOVERNMENT_DMV |
| MODIFICATION | SERVICE_CENTER, OWNER |
| THEFT_REPORT | POLICE, OWNER |
| RECOVERY | POLICE |
| INSURANCE_CLAIM | INSURANCE_COMPANY, OWNER |
| REGISTRATION | GOVERNMENT_DMV |
| DECOMMISSION | MANUFACTURER, GOVERNMENT_DMV |

"Verified" roles (`_isVerifiedIssuer` L589) are MANUFACTURER, GOVERNMENT_DMV, POLICE, DEALER and
INSPECTION_STATION. Events from SERVICE_CENTER, INSURANCE_COMPANY and OWNER are stored with
`verified = false`.

**Events:**
- `LifecycleEventRecorded(vehicleIdentity indexed, eventId indexed, eventType indexed, issuer, odometer, timestamp)` L125
- `EventAttested(eventId indexed, attester indexed, role, timestamp)` L137
- `IssuerAuthorized(issuer indexed, role, timestamp)` L147
- `IssuerAuthorizationRevoked(issuer indexed, timestamp)` L156

**Modifier:** `onlyAuthorizedIssuer(eventType)` L163. **Constructor** L173: calls the V1
constructor, then `_initializeAllowedIssuers()`.

**Functions**

| Signature | Vis / mut | What it does | Access control | Events | Origin |
|---|---|---|---|---|---|
| `authorizeIssuer(address issuer, IssuerRole role)` L185 | external | Sets or overwrites the role (not NONE) | onlyRegistryAuthority | IssuerAuthorized | MOBI VID II (CVIN design) |
| `revokeIssuerAuthorization(address)` L200 | external | Sets the role to NONE | onlyRegistryAuthority | IssuerAuthorizationRevoked | MOBI VID II |
| `isAuthorizedIssuer(address, EventType) returns (bool)` L218 | public view | Role-matrix check only | — | — | MOBI VID II |
| `recordLifecycleEvent(address vehicleIdentity, EventType, uint256 odometer, bytes32 dataHash, bytes32 credentialHash, string jurisdiction) returns (bytes32 eventId)` L244 | external | Rejects revoked vehicles. An OWNER-role caller must be the current owner (K-15, L266). Computes `eventId = keccak(vehicle, type, sender, timestamp, count)`, stores the struct, appends the id, bumps the counters | vehicleRegistered, onlyAuthorizedIssuer | LifecycleEventRecorded | MOBI VID II |
| `attestEvent(bytes32 eventId, address vehicleIdentity, bytes signature)` L338 | external | Requires that the event exists, the caller's role is not NONE, the caller is the owner **or** `validDelegate(id,"veriKey",caller)`, and the caller has not attested yet. Recovers the EIP-191 signature over (contract, chainid, vehicle, eventId) and requires it to equal the caller, then stores the attestation | as described (L345–376) | EventAttested | MOBI VID II + EIP-191 |
| `getVehicleEvents(address) returns (bytes32[])` L403 | external view | | vehicleRegistered | — | MOBI VID II |
| `getEvent(address, bytes32) returns (LifecycleEvent)` L418 | external view | Reverts if missing | — | — | MOBI VID II |
| `getEventAttestations(bytes32) returns (EventAttestation[])` L435 | external view | | — | — | MOBI VID II |
| `getEventTypeCount(address, EventType) returns (uint256)` L449 | external view | | — | — | CVIN ext. |
| `getCompleteHistory(address) returns (birth, eventCount, lastEvent)` L464 | external view | VID I + II summary | vehicleRegistered | — | CVIN ext. |
| `getEventsByType(address, EventType) returns (bytes32[])` L490 | external view | O(n) filter over all events | — | — | CVIN ext. |
| `getOdometerHistory(address) returns (uint256[], uint256[])` L516 | external view | O(n) readings and timestamps | — | — | CVIN ext. |
| `_initializeAllowedIssuers()` L539 | internal | Fills the matrix | constructor | — | CVIN ext. |
| `_isVerifiedIssuer(address) returns (bool)` L589 | internal view | | — | — | CVIN ext. |

**Design notes / security caveats**
- **Roles apply registry-wide.** Organisational roles can file events against *any* vehicle;
  that is by design (L264–265). OWNER is also a global grant from the authority, scoped at use
  time to the current owner. One address holds only one role.
- **Attestation needs both authority and consent (D54).** An organisational attester must hold a
  `veriKey` delegation from the owner. Only `veriKey` counts; a `sigAuth` delegation does not.
  Without one, even the issuer of the event cannot attest. A current owner without a role cannot
  attest either. `hasAttested` is set before the signature check, but a revert rolls it back
  (tested: "a reverted attempt does not consume the attester's slot").
- The signature is stored on-chain even though it has already been checked. That costs gas: the
  sandbox manifest records `attestEvent` at about 192,749 gas, and
  `4_comparison-framework/results/gas_benchmark.json` notes 222,070.
- **Events are append-only.** They cannot be revoked or corrected. De-authorising an issuer does
  not invalidate its past events. `DECOMMISSION` and `THEFT_REPORT` are plain records: they do not
  call `revokeIdentity` or freeze anything.
- **Odometer values are not checked on-chain** for monotonicity. Rollback detection is off-chain
  (`2_w3c-ssi-layer/mobi-vid/lifecycle_events.py: VehicleHistoryAggregator.detect_odometer_rollback`).
- `getEventsByType` and `getOdometerHistory` are unbounded view loops. They are fine for `eth_call`
  but cannot be used inside transactions on large histories.
- `jurisdiction` and `registrationAuthority` are free-form strings with no validation.
- The `"veriKey"` literal (L358) converts to an ASCII-padded `bytes32`. Callers must pass
  `ethers.encodeBytes32String("veriKey")` (as `benchmark_gas.js` does), not keccak.

---

## 4. Where / when / how it is used

### 4.1 Deploy scripts
- `cv2x-testbed/scripts/deploy_mobi_vid.js` deploys `MOBIVIDRegistry`, or `MOBIVIDRegistryV2` when
  `MOBI_VID_CONTRACT=MOBIVIDRegistryV2` is set. It writes `cv2x-testbed/deployments/mobi_vid_<network>.json`
  and, if artifacts exist, `contracts/<Name>_abi.json` / `_bytecode.txt`. It then runs a smoke
  test: `registryAuthority`, `authorizedManufacturers`, then `registerVehicleBirth` for the
  hard-coded Hardhat account #1 (`0x7099…79C8`) with firstOwner account #2, using a VIN hash of
  `keccak(VIN+"salt"+identity)`, a hex placeholder for `encryptedVIN` and JSON birth attributes.
  After that come `getVehicleInfo`, `lookupByVINHash` and `getVehicleDID`. Its closing banner
  points to `scripts/test_mobi_vid.py` and claims "On-chain revocation", but the smoke test never
  exercises revocation. The fixed vehicle address only works on a fresh chain, because K-4
  rejects an identity that already has history.
- `cv2x-testbed/scripts/deploy.js` deploys the stand-alone `ERC1056Registry`. It is the base
  contract only, and belongs to the ERC-1056 vehicle-profile option.
- No deploy script exists in `1_blockchain-identity/scripts/`; the benchmarks and tests deploy
  in-process with `getContractFactory`.

### 4.2 Hardhat tests (`1_blockchain-identity/test/L2-identity-system/`)
- `per-option/MOBIVID/MOBIVIDRegistry.test.js` (831 lines) is the main suite. For V1 it covers
  the regression where birth registration with manufacturer ≠ firstOwner and attributes used to
  revert, finite validity, unauthorised OEMs, duplicate VIN hashes and identities, VIN lookup,
  transfers and history, K-3 (no `changeOwner` bypass, a revoked vehicle is frozen), K-15 DID
  format and K-4 (pristine identity). For V2 it covers lifecycle recording for 5 types, role
  gating, K-15 OWNER scoping, issuer management, `attestEvent` signature verification
  (forged, invalid and replayed signatures), the WM-2 C2 owner/delegate rule, one attestation
  per attester, and the history and odometer queries.
- `per-option/MOBIVID/MOBIVIDRegistry.regression.test.js` covers D10 (the did:ethr regex and zero
  padding) and D16 (terminal revocation).
- `per-option/MOBIVID/anchorVehicleKey.regression.test.js` covers D11b: a one-time anchor by the
  manufacturer, owner rotation, the refusal cases, and key resolution from the event walk alone.
- `per-option/MOBIVID/attestEventRegression.test.js` covers M3 (the forged-signature path is
  closed and execution gas is pinned) and the D54 cases (non-owner, double attestation,
  expired or revoked delegation).
- `per-option/ERC1056/ERC1056Registry.regression.test.js` covers D21 (`DIDRevoked.previousChange`,
  walking through the revocation, every mutator frozen).
- `security/securityScenarios.test.js` (about L1176, "Security / MOBI-VID-V2") runs the shared
  attack scenarios against V2.
- CI: `.github/workflows/test-contracts.yml` runs the suites and has a step that `cmp`s the three
  MOBI files between the two trees (about L63–71).
- None of `cv2x-testbed/tests`, `5_zkp-agent-identity` or `phase2/` references these
  contracts by name, apart from the Python cv2x tests listed in 4.5. (`phase2/` holds only
  `idtx/`; CI paths under `phase2/backends/...` do not exist.)

### 4.3 Sandbox
- `sandbox/options/mobi-vid/adapter.js` wraps **V2** behind the uniform `IdentityOption`. Its
  header maps each method to a contract call:

  | Method | Contract call |
  |---|---|
  | deploy | constructor, plus `authorizeIssuer(deployer, SERVICE_CENTER)` |
  | create | `registerVehicleBirth` (vinHash = `keccak256(vin)`, empty attributes) |
  | changeController / transfer | `transferVehicleOwnership(…, 0, "SANDBOX")` |
  | addKeyOrDelegate | `addDelegate` |
  | setAttribute | `setAttribute` |
  | addClaim | `recordLifecycleEvent` |
  | revoke | `revokeIdentity` / `revokeDelegate` |
  | resolve | getters plus a replay of the logs |
  | signedOp, revokeEvent | NotApplicable |

  Two notes in the header are stale. "addDelegate … (event-only)" no longer holds, because
  `MOBIVIDRegistry` now stores delegations. The changeController line says "DIDOwnerChanged only;
  no ownership-history record", which contradicts the line above it: `transferVehicleOwnership`
  does append a record.
- `sandbox/options/mobi-vid/manifest.yaml` lists the contracts (V1 and V2), the provider and
  `benchmark_key: MOBI-VID-V2`, describes each benchmark op, and groups the functions into
  families with a stance (measured / implemented). It is generated by
  `sandbox/grand/make_manifests.py` (L33).
- `sandbox/options/mobi-vid/demos/*.js` exercise:

  | Demo | Calls |
  |---|---|
  | `creation.js` | registerVehicleBirth, lookupByVINHash, getVehicleBirth, AES-GCM VIN |
  | `vin-linkage.js` | lookup and AES-GCM decrypt |
  | `authorisation-roles.js` | authorizeManufacturer, authorizeIssuer, isAuthorizedIssuer, revokeIssuerAuthorization |
  | `claims.js` | recordLifecycleEvent, attestEvent, getEventAttestations |
  | `keys-delegates.js` | anchorVehicleKey, addDelegate/revokeDelegate, validDelegate |
  | `controller.js` | changeOwner revert vs transferVehicleOwnership |
  | `lifecycle-history.js` | getCompleteHistory, getEventsByType, getOdometerHistory |
  | `did-resolution.js` | getVehicleDID, getIdentityInfo, event replay |
  | `revocation.js` | revokeIdentity, then every mutator reverts |
  | `attributes.js`, `offchain-messaging.js` | attributes; off-chain messaging |

- `sandbox/options/erc-1056-vehicle/` is the same `ERC1056Registry` deployed on its own (create
  = `registerVehicle` sent by the owner).
- `sandbox/py-suites/L3-ssi/test_mobi_provider_onchain_key.py` is the D11b regression through
  `MOBIVIDProvider`.

### 4.4 Benchmarks / comparison framework (`1_blockchain-identity/scripts`, `4_comparison-framework`)
- `scripts/benchmark_gas.js` → `benchmarkMOBIVIDV2` (about L298). It measures deploy,
  `registerVehicleBirth` (attributes `"0x"`), `recordLifecycleEvent` (MAINTENANCE, by
  SERVICE_CENTER), `addDelegate`, `attestEvent` (with a `veriKey` delegation and a
  domain-separated signature), `transferVehicleOwnership` and `revokeIdentity`. Results go to
  `4_comparison-framework/results/gas_benchmark.json` / `gas_benchmark_stats.json` under the key
  `MOBI-VID-V2`. The recorded values are: deploy 4,370,878; create 299,165; lifecycle event
  307,254; addDelegate 57,667; transfer 200,155; revoke 75,404. Its comment at L317–319 ("Known
  V1 bug, worked around here") is stale, because the overflow is fixed.
- `scripts/benchmark_scaling.js` (L168) runs scaling and lifetime sweeps for V2 and writes
  `results/scaling_*.{json,csv,tex}` and `sensitivity.*`.
- `scripts/mobi_vid_backend_sweep.js` (H4) maps the three MOBI operations (birth, lifecycle,
  third-party attestation) onto every backend and uses V2 as the purpose-built reference
  (L366ff). It writes `results/mobi_vid_backends.json`.
- `scripts/security_scenarios.js` (L716ff) writes `security-analysis/results/attack_results.json`
  and `onchain_security.json`.
- `4_comparison-framework/feature-matrix/make_feature_matrix.py` generates
  `docs/FEATURE_ASYMMETRY_MATRIX.md`; the prepush hook and CI check that it is up to date.
- `scripts/experiment_pseudonym_pool.js` uses the cv2x `ERC1056Registry` (K-5) for the M5
  pseudonym-pool experiment.

### 4.5 Python layers
- **`2_w3c-ssi-layer/mobi-vid/`**
  - `mobi_vid_registry.py` is a typed web3.py v7 client for V2. It loads ABI and bytecode from
    `1_blockchain-identity/artifacts/contracts/MOBI/`, and its Python `EventType`/`IssuerRole`
    enums mirror the contract's. Methods: `deploy`, `connect`, `vehicle_did`,
    `authorize_manufacturer`/`authorize_issuer`/`revoke_issuer`, `register_vehicle_birth`,
    `get_vehicle_birth`, `lookup_by_vin_hash`, `record_lifecycle_event`, `add_delegate`,
    `attest_event`, `get_event`, `get_events_by_type`, `get_complete_history`,
    `get_odometer_history`, and log queries.
  - `birth_certificate.py` (VID I) issues a schema-enforced `VehicleBirthCertificate` VC and
    anchors `keccak256(canonical VC)` as `birthCertHash`. It uses the salted SHA-256 VIN hash and
    AES-256-GCM `encryptedVIN`, and verifies in two layers (VC plus chain).
  - `lifecycle_events.py` (VID II) mirrors the permission matrix in Python (about L82). It
    issues event VCs, builds the attestation digest exactly as the contract does
    (`attestation_digest`, about L238) with `solidity_keccak`, and runs `VehicleHistoryAggregator`
    (re-verifying VCs, checking attestations, detecting odometer rollback).
  - `tests/test_mobi_vid_layer.py` starts its own Hardhat node; `test_vin_cipher.py` and
    `test_aggregator_checks.py` are the other tests here.
  - The README's statement that the canonical source is `cv2x-testbed/contracts/` and the copy
    in `1_blockchain-identity` is the "compiled copy" is inconsistent with the client loading
    artifacts from `1_blockchain-identity`. The two are byte-identical either way. The README
    also says the attestation signature is "stored on-chain, recovered off-chain", which predates
    the on-chain `ECDSA.recover`.
- **`2_w3c-ssi-layer/did-resolution/did_resolver.py`** (on-chain mode, `mobi_registry=`) resolves
  `did:mobi:<salted VIN hash>` via `lookupByVINHash`, then `getVehicleDID`, then an ERC-1056 event
  replay in the MOBI registry. It is tested by `tests/test_did_resolver_onchain_mobi.py`, with
  helpers in `tests/resolver_chain_helpers.py` that load the V2 artifact. It is also used by
  `docs/conformance/generate_implementations_onchain.py` for the W3C DID test-suite run.
- **`cv2x-testbed/identity/mobi_vid_provider.py`** (`MOBIVIDProvider(IdentityProvider)`):
  - `register_vehicle_birth` derives the identity, salts and hashes the VIN, encrypts it
    (HKDF + AES-256-GCM), hashes the birth certificate with SHA-256, generates a secp256k1 key,
    calls `registerVehicleBirth` and then `_anchor_vehicle_key` (which calls `anchorVehicleKey`).
  - `verify_message` resolves the key through `_registered_key_for`. That method is **defined
    twice** (about L659 and L703). Python keeps the second definition, so the first, which
    calls `getVehicleInfo`, is dead code. The live one checks the local record, then
    `isRevoked`, then the on-chain key found by walking back from `lastChanged`
    (`_resolve_key_on_chain`, L525).
  - `revoke_credential` calls `revokeIdentity`.
  - Related files: `cv2x-testbed/identity/erc1056_provider.py` (stand-alone `ERC1056Registry`:
    `registerVehicle`, `updateVehicleKey`, `revokeIdentity`, `getIdentityInfo`, event walk) and
    `cv2x-testbed/identity/lifecycle_backends.py` (`MOBIVIDV2LifecycleBackend`:
    `authorizeIssuer`, birth via the provider, `recordLifecycleEvent`,
    `transferVehicleOwnership`, `identityOwner`; centralized-registry parity).
- **`cv2x-testbed/scripts/`**:
  - `test_mobi_vid.py` exercises the provider.
  - `experiment_lifecycle_parity.py` (M4, centralized registry vs MOBI-VID-V2) writes
    `results/lifecycle_parity.{json,md}`.
  - `experiment_pki_vs_erc1056.py` and `experiment_freshness_k.py` work on the ERC-1056 vehicle
    registry and the MOBI provider and write the `results/freshness_k*` and `pki_vs_erc1056.*`
    files.
  - `check_artifacts_fresh.js` recompiles all three contracts and compares them against the
    committed `contracts/ERC1056Registry_{abi.json,bytecode.txt}`.
  - The tests are `cv2x-testbed/tests/test_mobi_vid_verify.py` (T-4: no self-supplied key,
    `receipt.status` checked), `test_lifecycle_parity.py`, `test_erc1056_key_resolution.py`,
    `test_revocation_sanity_reason.py`, `test_d51_chain_time.py`, `test_t9_freshness.py`,
    `test_experiment_harness.py`, `test_freshness_k*.py`.
- **`cv2x-testbed/protocols/cv2x_stack.py` does not touch the chain.** `CV2XStack(vehicle_id,
  identity_manager=None, …)` (L370) calls `identity_manager.sign_message(message_dict)` in
  `send_bsm`/`send_denm` (L411, L464). In receive it calls
  `identity_manager.verify_message(message_data, crl)` (L519) and gates `success` on the result
  (T-9, L536–539). That is the duck-typed interface of `identity/standard/pki_identity.py:
  VehiclePKIIdentity`. `MOBIVIDProvider` and `ERC1056Provider` use a different signature
  (`sign_message(vehicle_id, message)`, `verify_message(signed_message)`), so they cannot be
  passed in directly. In the repo, the stack is driven only with PKI identities
  (`scenarios/basic_v2v_scenario.py`, `tests/test_t9_freshness.py`) or with `None`
  (`scenarios/cv2x_identity_integration.py` L167, "Would pass identity manager"). On-chain
  identity reaches V2X messaging only through the provider-level experiments
  (`experiment_pki_vs_erc1056.py`, `experiment_freshness_k.py`), not through `CV2XStack`.

### 4.6 Docs
- The repo-root `MOBI_VID_RESEARCH.md`, `MOBI_VID1_TECHNICAL_SPEC.md` and `MOBI_VID2_SSI_DESIGN.md`
  are design-phase documents; see 1.2 for where they diverge from the code.
- `docs/DEFECT_LOG.md` covers D10, D11b, D16, D21 and D54.
- `docs/REVIEW_02_CODEBASE.md` and `docs/review02/*` cover K-3, K-4 and K-15.
- `docs/MOBI_VID_CHECKLIST.md`, `docs/PLAN_MOBI_SUMO.md` (M4/M5),
  `docs/FEATURE_ASYMMETRY_MATRIX.md` and `docs/tdp/TDP-003_INTERFACE_CONTROL_DOCUMENT.md`
  also cover this group.
- So do `docs/testing/GAS_CHARTER.md`, the thesis chapters under `docs/thesis/` and
  `cv2x-testbed/V2_IMPLEMENTATION_STATUS.md` / `QUICKSTART.md`.

---

## 5. Duplicates / copies

| Canonical | Copy | Status |
|---|---|---|
| `1_blockchain-identity/contracts/MOBI/ERC1056Registry.sol` | `cv2x-testbed/contracts/ERC1056Registry.sol` | byte-identical (md5 `49eac56b…`) |
| `1_blockchain-identity/contracts/MOBI/MOBIVIDRegistry.sol` | `cv2x-testbed/contracts/MOBIVIDRegistry.sol` | byte-identical (md5 `089792b8…`) |
| `1_blockchain-identity/contracts/MOBI/MOBIVIDRegistryV2.sol` | `cv2x-testbed/contracts/MOBIVIDRegistryV2.sol` | byte-identical (md5 `5484d7d5…`) |

- Two guards keep the copies identical: `tools/prepush_check.sh` (L21–24, with a self-test probe
  at L60–63) and the CI step in `.github/workflows/test-contracts.yml`. The comments disagree on
  which tree is the source. `benchmark_gas.js` says "copied from cv2x-testbed, unmodified"; the
  SSI README calls cv2x-testbed canonical.
- **Stale copies:**
  - The draft `MOBIVIDRegistry` embedded in `MOBI_VID1_TECHNICAL_SPEC.md` §2 (overflowing
    validity, `findVehicleByVINHash`, no K-3/K-4/D11b/D54 changes).
  - The Solidity fragments in `MOBI_VID2_SSI_DESIGN.md`.
  - `cv2x-testbed/contracts/ERC1056Registry_abi.json` / `_bytecode.txt` are generated files whose
    freshness is checked by `check_artifacts_fresh.js`. No MOBI ABI is committed;
    `deploy_mobi_vid.js` writes one when it runs.
  - `CVINVehicleDIDRegistry.sol` (ERC1056 folder) only references
    `MOBIVIDRegistry.PERMANENT_ATTRIBUTE_VALIDITY` in a comment; it is not a copy.
  - Old experiment drivers live under `cv2x-testbed/scripts/archive-2026-10-03/`.
