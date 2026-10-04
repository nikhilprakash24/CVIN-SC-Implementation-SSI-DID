# MOBI VID Checklist: clause-by-clause reconciliation (plan step M1)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-10-04
**Plan step:** `docs/PLAN_MOBI_SUMO.md` Part A, M1
**Code base checked:** trunk at `d2e6a58`

## 0. Sources, and what they leave out

| # | Document (as published by MOBI) | URL | Retrieved | Public content | Used here as |
|---|---|---|---|---|---|
| S1 | *Vehicle Identity Standard*, Version 1.0, **Preview** (2019), 8 pp. | <https://dlt.mobi/wp-content/uploads/2019/09/MOBI-Vehicle-Identity-Standard-v1.0-Preview.pdf> | 2026-10-04, HTTP 200, 218,804 B, sha256 `2eb7f679f3d8db26…` | Cover, table of contents, working-group list, foreword, introduction (pp. II–VIII). **No normative clause is public.** The copyright notice forbids reproduction outside MOBI. | Section headings only (§4) and the informative introduction (§3) |
| S2 | *MOBI VID0002/TS/2024 Version 2.0 (Version 1.0 © 2019)*, VID I Technical Specifications, 23 pp. | <https://dlt.mobi/wp-content/uploads/2024/04/MOBI-VID0002TS2024-Version-2.0.pdf> | 2026-10-04, HTTP 200, sha256 `e88e29d98e2face8…` | **Full text** under the Apache License 2.0, with numbered requirements VID-R1…R8 and VID-D1…D5 (RFC 2119 levels). Its changelog says v2.0 (03/2024) is a "full rewrite" that "removed all system-level requirements" and made VID I "a data specification". | **The normative VID I source** (§1) |
| S3 | *MOBI VID0002/UC/2021 Version 1.2*, VID II Use Cases and Business Requirements | <https://dlt.mobi/wp-content/uploads/2024/03/MOBI-VID0002UC2021-Version-1.2-.pdf> | 2026-10-04, HTTP 200, sha256 `ac4e35e8ea5dac26…` | Full text (Apache 2.0). Two prioritised use cases: Vehicle Registration (UC1, BR1–BR10) and Maintenance Traceability (UC2, BR1–BR6). | **The normative VID II source** at the business-requirement level (§2) |
| S4 | *MOBI VID0004/RI/2021*, VID II Reference Implementation Architecture: v2.0 (May 2024) and the earlier v2.0 file | <https://dlt.mobi/wp-content/uploads/2024/05/MOBI-VID0004RI2024-Version-2.0.pdf>, <https://dlt.mobi/wp-content/uploads/2024/10/MOBI-VID0004_RI_2021-Version-2.0.pdf> | 2026-10-04, both HTTP 200 | **Preview only.** Front matter, the table of contents and the glossary, then "Full access to this Standard … available to MOBI members". The technical workflows (§§5–6) are not public. | Glossary only (no clauses) |
| S5 | *MOBI VID0001/WP/2021 v2.1*, white paper | <https://dlt.mobi/wp-content/uploads/2023/05/MOBI-VID0001WP2021_Version-2.1.pdf> | 2026-10-04 | Non-normative overview | Context only |
| S6 | *MOBI GitHub Standardized Schemas 2025* (index) | <https://dlt.mobi/wp-content/uploads/2025/02/MOBI-Github-Standardized-Schemas-2025.pdf> | 2026-10-04 | Schema **titles** only, e.g. `VehicleBirthCertificate` v1.1, `UniqueVehicleIdentifier.json`, `RevocationCertificate.json`, eleven VID II VC schemas (`VcSchemaForMileage.json`, `VcSchemaForInspectionsReport.json`, …). The schemas are in a GitHub repository open only to members. | Shows that machine-readable VID schemas exist and are not public (§4) |

Index pages: <https://dlt.mobi/standards/>; VID I announcement:
<https://dlt.mobi/mobi-announces-the-first-vehicle-identity-vid-standard-on-blockchain-in-collaboration-with-groupe-renault-ford-and-bmw-among-others/>.
None of the PDFs are committed to the repository.

**Limits on the conclusions.**
1. The 2019 VID I v1.0, the version the repository's design documents cite, is **not public beyond its preview**. Its clauses (UVI/VBC formats in v1.0 §4, the Certificate API and Roles 1–4 in §5, the DVM in §7) **cannot be checked**. They are listed in §4 as *Not assessable*.
2. VID I is therefore checked against **S2 (v2.0, 2024)**, the public successor. v2.0 dropped the system-level requirements, so an implementation that meets v2.0 has said nothing about the v1.0 API or system requirements.
3. VID II is checked at the **business-requirement** level (S3). The VID II technical reference implementation (S4) and the VID II VC schemas (S6) are members-only. No claim about VID II *technical* conformance is possible from public material.
4. MOBI publishes no conformance test suite or certification procedure in any of these documents. Every status below is this author's reading of the code against the clause text. None is a MOBI determination.

**Status vocabulary.** **I+T**: implemented and exercised by a test that passes on this trunk. **I-U**: implemented, but no test exercises it. **Partial**: part of the clause is met, and the row says what is missing. **Not impl.**: nothing in the code meets it. **OOS**: out of scope for this thesis, with an SC entry proposed in §7. **N/A-text**: not assessable because the clause text is not public. A code element counts as present only if it was found in the code. A design document saying so does not count.

**Test runs used as evidence** (2026-10-04, this worktree):

| Suite | Command | Result |
|---|---|---|
| `1_blockchain-identity/test/MOBIVID/MOBIVIDRegistry.test.js` | `npx hardhat test` on that file | 24 passing |
| Security scenarios, MOBI-VID-V2 block | `npx hardhat test test/security/securityScenarios.test.js --grep MOBI-VID` | 6 passing (5 DEF, 1 n/a) |
| `2_w3c-ssi-layer/mobi-vid/tests/` | `python3 -m pytest` | 36 passed (`PLAN_MOBI_SUMO.md` and `README.md` still say 32) |
| `cv2x-testbed/tests/test_mobi_vid_verify.py` | `python3 -m pytest` | 8 passed, 3 skipped (the on-chain cases need a node) |

Short names used in the tables:
`V1` = `1_blockchain-identity/contracts/MOBI/MOBIVIDRegistry.sol`,
`V2` = `…/MOBIVIDRegistryV2.sol`, `E` = `…/ERC1056Registry.sol`,
`BC` = `2_w3c-ssi-layer/mobi-vid/birth_certificate.py`,
`LE` = `…/mobi-vid/lifecycle_events.py`, `RC` = `…/mobi-vid/mobi_vid_registry.py`,
`SCH` = `2_w3c-ssi-layer/verifiable-credentials/vc_schemas.py`,
`RES` = `2_w3c-ssi-layer/did-resolution/did_resolver.py`,
`JS` = `1_blockchain-identity/test/MOBIVID/MOBIVIDRegistry.test.js`,
`SEC` = `1_blockchain-identity/test/security/securityScenarios.test.js`,
`PY` = `2_w3c-ssi-layer/mobi-vid/tests/test_mobi_vid_layer.py`,
`CIPH` = `…/mobi-vid/tests/test_vin_cipher.py`.

---

## 1. VID I: MOBI VID0002/TS/2024 v2.0 (S2), 13 requirements

| ID (S2 page) | Clause (short quote) | Implementing element | Test | Status |
|---|---|---|---|---|
| **VID-R1** (p. 6) | Vehicle IDs "MUST follow the W3C DID standard" | `RC:140-142` `vehicle_did()` → `did:ethr:<0xchain>:<0x checksummed addr>`, used as the VC subject in `BC:252,266`. On-chain `V1:484-498` `getVehicleDID()`. Resolver `RES:342-404` `_resolve_ethr`. | The Python DID is exercised as the birth-VC subject (`PY::TestBirthCertificate::test_vc_is_schema_valid_and_anchored`). `getVehicleDID` has **no test**. Resolver syntax tests in `2_w3c-ssi-layer/did-resolution/tests/`. | **Partial.** (a) **Bug:** `getVehicleDID` leaves out the `0x` before the address (probe on 2026-10-04 returned `did:ethr:0x7a69:70997970c5…`, 56 chars). The repo's own resolver rejects that DID as `invalidDid` (`RES:185`). The Python and Solidity DIDs for the same vehicle therefore differ. (b) `_resolve_ethr` does not read the chain ("In production, would query ERC-1056 registry", `RES:373`). It returns the default document whose controller is the vehicle address. After `registerVehicleBirth` the on-chain owner is `firstOwner` (`V1:268`), so the resolved document names the wrong controller. The DID *syntax* conforms. Resolution of a MOBI vehicle DID to a correct DID document is not implemented. |
| **VID-R2** (p. 6) | "A vehicle MUST be assigned a Vehicle ID" (in the S2 glossary, a VID is the VC issued by the manufacturer) | `V1:227-311` `registerVehicleBirth`. `BC:221-311` `issue_birth_certificate` (issues the `VehicleBirthCertificate` VC and anchors its keccak hash as `birthCertHash`). | `JS::registerVehicleBirth … succeeds with manufacturer != firstOwner and non-empty attributes`; `PY::TestBirthCertificate::test_birth_succeeds_with_distinct_manufacturer_and_owner`; `PY::…::test_vc_is_schema_valid_and_anchored` | **I+T** |
| **VID-D1** (p. 6) | Every entity "SHOULD use different DIDs for each relationship" (Note2.D1 allows long-lived DIDs where correlation is wanted) | None. Each vehicle has one `did:ethr` identity. The ERC-1056 delegates (`E:117-149`) rotate keys under the same DID and do not give per-relationship DIDs (`PLAN_MOBI_SUMO.md` M5 hypothesis). | — | **Not impl.** Pseudonymous V2X use (SC-02) and M5 are the related open items. SC proposed (§7, P-5). |
| **VID-R3** (p. 6) | "A DID, combined with an entity certificate, is required to form an authoritative identity" | No Entity Certificate object exists. A functional stand-in: the on-chain role registries `V1:73` `authorizedManufacturers` and `V2:97` `authorizedIssuers`, set by `registryAuthority` (`V1:174-183`, `V2:182-191`), plus `TrustedIssuerRegistry` in the VC verifier (`BC:332-345`). | Role gating: `JS::rejects unauthorized manufacturers`, `JS::recordLifecycleEvent rejects issuers whose role is not allowed…`, `SEC::Security / MOBI-VID-V2 unauthorizedIssuance` | **Partial.** Authority is bound to a bare address through a role mapping, not to a DID plus EC pair. See R8. |
| **VID-R4** ("VIDI-R4" in the source, p. 6) | All cryptographic services "MUST be cryptographically sound" | secp256k1 ECDSA (OpenZeppelin `ECDSA.recover` with low-s check, `V2:340-347`; eth-account for VC proofs). AES-256-GCM with an HKDF-SHA256 key (`BC:112-157`). Salted SHA-256 VIN commitment (`BC:82-90`). keccak256 anchors (`BC:160-166`, `LE:104-106`). | `CIPH::*` (9 tests: round trip, tamper, wrong secret/salt/AAD, nonce freshness, key length); `PY::TestNegativePaths::test_forged_attestation_signature_rejected_on_chain`; `JS::attestEvent verifies the attestation signature on-chain…` | **I+T** (bounded). Only standard primitives are used, and the negative paths are tested. Soundness is inherited from those primitives and was not proved here. |
| **VID-D2** (p. 6) | Key lifecycle management "SHOULD follow … NIST SP 800-57, ISO/IEC 11770" | None. `BC:39` and `BC:104-105` declare key distribution and HSM custody out of scope. Tests use the Hardhat well-known keys. | — | **OOS.** SC proposed (P-1). |
| **VID-D3** (p. 7) | Key management "SHOULD follow … FIPS 200, ISO/IEC 27001" | None (these are organisational ISMS controls) | — | **OOS.** SC proposed (P-1). |
| **VID-R5** (p. 7) | "All URIs MUST have a max length of 1024 characters" | No length check anywhere (`grep 1024` finds nothing in the MOBI or SSI code). The URIs the code generates are short: vehicle DID about 58 chars; VC id `urn:uuid:…` 45 chars (`2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py:267`). | — | **Partial.** The generated URIs comply by construction, but nothing enforces the limit on URIs supplied from outside (VC `id`, `issuer`, service endpoints). |
| **VID-R6** (p. 7) | The UVI "MUST be compliant with the JSON-LD 1.1 schema" (64-character alphanumeric `UVI`) | None. No UVI is defined in any `.sol` or `.py` file. The vehicle is indexed by a 20-byte address and by `vinHash` (`V1:76`, `V1:399-405`). | — | **Not impl.** The 32-byte salted `vinHash` is already 64 hex characters and unique per registry (`V1:242`), so it could serve as the UVI, but nothing names or publishes it as one. SC or fix proposed (P-3). |
| **VID-D4** (pp. 8–12) | The VBC "SHOULD be compliant with the JSON-LD 1.1 schema" (15 mandatory and 5 optional fields; Note1.D4: dates are millisecond Unix timestamps, Fuel Type is an enum 0–6) | `SCH:131-146` `VehicleBirthCertificate` schema, enforced at issuance (`BC:264-270`, `enforce_schema=True`). The repo's own context is `https://cvin.ubc.ca/credentials/automotive/v1` (`SCH:34`), not the S2 `schema.org` typed object. | `PY::TestBirthCertificate::test_vc_is_schema_valid_and_anchored` (checks the 6 repo-required fields); `PY::…::test_invalid_vin_rejected_before_chain` | **Partial.** Of the 15 mandatory fields: **present (7)**: Certificate URI (as the VC `id`), VIN (`vin`, ISO 3779 structure check `SCH:40-46`), Model, Model Year (`year`, an *int*, where S2 says TEXT/ISO 3779 VIS), Manufacturer (`make`, free text, where S2 says ISO 3779 WMI), Date of Production (`manufacturingDate`, an ISO string, where S2 says a ms timestamp), Manufacturer EID (`manufacturerDid`). **Optional in the repo but mandatory in S2 (1):** Color. **Missing (7):** Country of Origin, Engine Code, Engine Serial Number, Fuel Type (enum), Transmission Serial Number, Trim Type, UVI. Optional fields: Plant Code is present (`plantCode`). Previous VBC, Electric Motor SN, Battery ID and Battery Installed Date are missing. SC or fix proposed (P-4). |
| **VID-R7** (p. 12) | A valid VBC "MUST be issued by the legal identity of an Original Equipment Manufacturer" | On-chain: `V1:135-141` `onlyAuthorizedManufacturer` on `registerVehicleBirth` (`V1:236`). Off-chain: `BC:385-395` requires the VC issuer address to equal the on-chain `manufacturer`. | `JS::rejects unauthorized manufacturers`; `SEC::Security / MOBI-VID-V2 unauthorizedIssuance`; `PY::TestBirthCertificate::test_full_verification_report` (asserts `issuerMatchesManufacturer`) | **Partial.** The *issuer is an authorised manufacturer* mechanism is implemented and tested. The *legal identity* part is reduced to the `registryAuthority`'s say-so: there is no EC or trust-anchor credential (see R3, R8). The constructor also auto-authorises the deployer as a manufacturer "(for testing)" (`V1:163-165`) in the production contract. |
| **VID-D5** (p. 12; a D-level ID worded with "MUST" in the source) | Entity actions "MUST be cryptographically authenticated by one of the Verification Methods … referenced in the authentication" property of the entity's DID Document | On-chain writes are authenticated by the transaction signature (`msg.sender`) against the role mappings or the ERC-1056 owner (`E:59-65`). VC proofs are recovered to the issuer's `did:ethr` address (`BC:343-345`, `LE:327-329` via `CredentialVerifier`). Attestations are recovered on-chain (`V2:340-347`). | `JS::attestEvent … rejects forged / invalid / replayed signatures`; `PY::TestNegativePaths::test_tampered_vc_fails_verification`, `…::test_unauthorized_attester_rejected_on_chain` | **Partial.** Authentication by the *implicit* `#controller` key works. Nothing resolves the entity's DID Document, so an ERC-1056 `veriKey`/`sigAuth` delegate or a changed owner is never consulted (see R1(b)). |
| **VID-R8** (pp. 12–13) | The Entity Certificate "MUST be compliant with the JSON-LD 1.1 schema" (EID, Type 1–5, PubKey; Note2.R8: Users, Physical Assets, Service Providers, Data Hosts, Trust Anchors) | None. No EC data structure exists. `IssuerRole` (`V2:52-62`: NONE plus 8 roles) is a different, repo-defined taxonomy and does not map onto the five S2 entity types. | — | **Not impl.** SC or fix proposed (P-3). |

**VID I subtotal (13):** I+T 2 · Partial 6 · Not impl. 3 · OOS 2. **Of the 8 MUST-level
requirements (R1–R8): 2 met (R2, R4), 4 partial (R1, R3, R5, R7), 2 not implemented (R6, R8).**

---

## 2. VID II: MOBI VID0002/UC/2021 v1.2 (S3), 16 business requirements

S3 numbers UC2's requirements "VID II-UC1-BR1…BR6" on pp. 36–37. This looks like a
copy-paste error in the source, so they are called UC2-BRn here. The repository's on-chain event model
(11 `EventType`s, 8 `IssuerRole`s, attestations; `V2:35-115`) is a **repository
design**. S3 does not prescribe event types, roles or an on-chain record format, and
the VID II technical material that might (S4, S6) is members-only.

| ID (S3 page) | Clause (short quote) | Implementing element | Test | Status |
|---|---|---|---|---|
| **UC1-BR1** (p. 31) | Owner "shall be able to electronically register a vehicle after purchase…" without visiting a VRA | `V1:341-376` `transferVehicleOwnership` (owner-initiated; `authority` is a free-text string). `V2:239-294` `recordLifecycleEvent(REGISTRATION)`, which only `GOVERNMENT_DMV` may issue (`V2:548`). `SCH:226-239` `RegistrationCredential`. | `JS::ownership transfer transfers ownership, records history…`; `JS::recordLifecycleEvent records … REGISTRATION` | **Partial.** Transfer and a DMV registration event exist, but no flow lets the owner register, and the Python layer has no transfer wrapper (none in `RC`). |
| **UC1-BR2** (p. 31) | Owner's wallet "shall be tied to a government provided identity", previous registration, VIN, VID and new registration | None. The owner is a bare Ethereum address with no KYC or government-ID binding. | — | **OOS.** SC proposed (P-2). |
| **UC1-BR3** (p. 31) | Prove registration to third parties "without producing personal information" | Generic VP machinery in the VC layer (`vc_holder.py:115` `create_presentation`, selective-disclosure envelopes; `vc_verifier.py:805` `verify_presentation`). Nothing in `mobi-vid` uses it. `RegistrationCredential` requires `ownerDid` and `plateNumber` (`SCH:230-235`). | No MOBI-VID registration-presentation test | **Partial.** The building blocks exist. A registration proof without personal data was not built or tested. |
| **UC1-BR4** (p. 31) | VRA "shall be able to digitally verify if the vehicle is legally registered" | `V2:461-480` `getEventsByType(REGISTRATION)`; VC verification with revocation status (`LE:381-410`) | `JS::recordLifecycleEvent records … REGISTRATION events` (writes it). No test reads registration status. | **Partial.** Registration *records* exist. Nothing decides whether a vehicle is registered *now* (expiry, revocation, jurisdiction). |
| **UC1-BR5** (p. 30) | VRA "shall be able to digitally transfer the registration from one vehicle owner to another" | `V1:341-376` is `onlyOwner(vehicleIdentity, msg.sender)`. A VRA cannot start or co-sign it, and `authority` is an unauthenticated string. | `JS::rejects transfers not initiated by the current owner` | **Partial.** Ownership transfer exists, but it is owner-only. Fix or SC proposed (P-6). |
| **UC1-BR6** (p. 30) | VRA can "renew or revoke the registration" at the owner's request; multiple owners in future | Renewal: a new `REGISTRATION` event. Revocation: the issuer's off-chain `RevocationRegistry` (`LE:149-152`). Identity revocation `E:250-259` is owner-only. | `PY::TestRevocationStatus::test_revoked_event_credential_rejected_in_history` (MAINTENANCE VC, same mechanism) | **Partial.** Renewal and VC revocation work. There is no on-chain registration status. Multi-party ownership is not implemented (single `owners[]` entry). |
| **UC1-BR7** (p. 30) | OEM "shall be able to create a VID for each vehicle using VIN, vehicle birth certificate…" and provide it downstream | `BC:221-311` `issue_birth_certificate`, `V1:227-311` | `PY::TestBirthCertificate::*` (7 tests); `JS::registerVehicleBirth …` (4 tests) | **I+T** |
| **UC1-BR8** (p. 30) | VID "persistent enough to prove existence, manage access control, confirm product definition and ownership history, and track events" | Existence `V1:439-445`; ownership history `V1:412-419`; events `V2:374-399`, `V2:435-453`; product definition = VBC claims (see D4) | `JS::transfers ownership, records history…`; `JS::getCompleteHistory…`; `PY::TestLifecycleEvents::*` | **Partial.** Existence, ownership history and events are covered. *Access control* over VBC data is absent (all on-chain records are public; privacy rests on keeping the VC off-chain). Product definition is thin (D4). |
| **UC1-BR9** (p. 30) | Third parties "shall be able to digitally verify the ownership of a vehicle" | `E:72-78` `identityOwner`; `V1:455-472` `getVehicleInfo`; `RC:208-210` | `JS::transfers ownership … updates ERC-1056 owner`; `PY::…::test_birth_succeeds_with_distinct_manufacturer_and_owner` | **I+T.** Ownership is by address only, with no tie to a legal person (UC1-BR2). `getVehicleInfo` itself is untested. |
| **UC1-BR10** (p. 30) | VID "robust enough for other vehicles and infrastructure in the V2X environment to verify the identity" | Outside the M1 directories: `cv2x-testbed/identity/mobi_vid_provider.py:501` `sign_message`, `:587` `verify_message` | `cv2x-testbed/tests/test_mobi_vid_verify.py::test_impersonating_registered_vehicle_with_own_key_rejected`, `::test_registered_key_accepted_by_identity_and_did` and 6 more (8 pass; the 3 `test_onchain_*` were skipped in this run) | **I+T** for the off-chain path only. The on-chain path was not exercised in this run. |
| **UC2-BR1** (p. 37) | Owner can "verify to a repair service that the vehicle is indeed registered to the owner" | Ownership is readable on-chain (`E:72-78`). The VP machinery is generic (see UC1-BR3). | No owner-to-shop proof test | **Partial.** No challenge-response or presentation flow for this exists in `mobi-vid`. |
| **UC2-BR2** (p. 37) | Owner can "tie their wallet to the vehicle's wallet so that the repair shop can obtain permission" | None. A `SERVICE_CENTER` (or any `OWNER`-role address) authorised by the registry authority can record events on **any** vehicle (`V2:239-250`, `V2:510-553`). The vehicle owner gives no consent, and the ERC-1056 delegates are not consulted. | `JS::rejects issuers whose role is not allowed…` (tests role gating, not owner consent) | **Not impl.** This is a design deviation, not just a missing feature. Fix or SC proposed (P-6). |
| **UC2-BR3** (p. 37) | Owner can provide "a link or an electronic source" so others can verify maintenance was performed | `LE:302-410` `VehicleHistoryAggregator` (on-chain record + VC anchor + signature + issuer-consistency + revocation) | `PY::TestHistoryAggregation::test_aggregated_history_verifies_all_vcs`; `PY::TestNegativePaths::test_tampered_vc_fails_verification`; `PY::TestRevocationStatus::test_revoked_event_credential_rejected_in_history` | **I+T** |
| **UC2-BR4** (p. 37) | OEM can obtain "from a repair shop a verification that it performed service" | `LE:159-231` `record_event` (VC signed by the shop and anchored on-chain); `V2:389-399` `getEvent` | `PY::TestLifecycleEvents::test_event_records_match_inputs`; `PY::TestHistoryAggregation::test_aggregated_history_verifies_all_vcs` | **I+T** |
| **UC2-BR5** (p. 37) | Repair shop can "provide verification that it did perform a repair service" | Same path with `EventType.REPAIR` (`V2:37`, allowed for DEALER and SERVICE_CENTER, `V2:517-518`; VC type `RepairRecord`, which has no registered schema, `LE:70`) | None. No JS or Python test records a `REPAIR` event (tests use MAINTENANCE, INSPECTION, ACCIDENT, RECALL, REGISTRATION). | **I-U.** The mechanism is tested through MAINTENANCE. The REPAIR role matrix and VC type are not. |
| **UC2-BR6** (p. 37) | Repair shop can "transmit maintenance records along with the service verification request" | Claims travel inside the VC. `dataHash = keccak256(canonical claims)` is anchored (`LE:208-209`). | `PY::TestLifecycleEvents::test_event_records_match_inputs` | **Partial.** The record and its integrity anchor exist. There is no transport (no messaging, DIDComm or endpoint), and the "request" flow is not modelled. |

**VID II subtotal (16):** I+T 5 · I-U 1 · Partial 8 · Not impl. 1 · OOS 1.

---

## 3. Informative statements (not counted)

The 2019 preview introduction (S1 pp. VII–VIII) and S2 §1 and §5.1 make descriptive statements.
They are not requirements, but the repository's documents echo them, so they are listed here.

| Statement | Repository |
|---|---|
| "At the birth event, the VID consists of the vehicle birth certificate (VBC) and is indexed by a unique vehicle identifier (UVI)" (S1 p. VII) | VBC: yes (VC). UVI: no (see R6). |
| Vehicle wallet "contains digital certificates for things such as vehicle identity, ownership, warranties, and mileage" (S1 p. VII) | The VC holder wallet exists (`vc_holder.py`). Identity: yes. Mileage: odometer per event (`V2:487-503`). Warranty: no credential type. |
| "data can be securely stored on a decentralized infrastructure with permissioned entity access" (S1 p. VIII; S2 p. 1: "access granted only to authorized entities") | Writes are permissioned. **Reads are not**: every birth, event and attestation record is publicly readable on-chain. |
| "Relationships between users regulate API access privileges to the VBC data" (S2 p. 6) | Not modelled |

---

## 4. 2019 v1.0 sections whose text is not public (not counted)

| v1.0 section (S1 p. III) | What is publicly knowable | Nearest repository element | Status |
|---|---|---|---|
| §3.3 Key Management and Key Rotation Concepts | Heading only. v2.0 kept only D2 and D3 (§1). | `E:117-183` add/revoke delegate, `E:291-313` `updateVehicleKey` | **N/A-text** |
| §4.3 Enum and Time Definitions | Heading only. v2.0 Note1.D4 gives ms timestamps and the Fuel Type enum (assessed under D4). | — | **N/A-text** |
| §4.5 Revocation Certificate | Heading only. A `RevocationCertificate.json` schema exists, members-only (S6). | `E:250-259` `revokeIdentity` (owner-only); off-chain VC `RevocationRegistry`. Neither is a revocation *certificate*. | **N/A-text** |
| §5 Certificate API (5.1–5.2.6, Roles 1–4 APIs) | Headings only. S2 says v2.0 "removed all system-level requirements". | Role-gated contract functions (`V2:52-62`, `V2:510-553`). Whether these match Roles 1–4 is unknown. | **N/A-text** |
| §7 System Requirements (7.2 Distributed Virtual Machine) | Headings only. Removed in v2.0. | EVM (Hardhat, solc 0.8.x) | **N/A-text** |

---

## 5. Repository spec documents compared with the code

### 5.1 Claims in the design documents that the code does not support

| Document claim | Code | Where |
|---|---|---|
| `MOBI_VID1_TECHNICAL_SPEC.md` §1: `vinHash = SHA256(VIN + salt + vehicleDID)`; also the contract comment `V1:33` | `sha256(vin ":" salt)`, with no DID in the hash | `BC:82-90` |
| `MOBI_VID1_TECHNICAL_SPEC.md` §1: encrypted VIN "encrypted with owner's public key" | Symmetric AES-256-GCM, key from HKDF over an owner-held *secret*; no public-key encryption | `BC:128-140` |
| `MOBI_VID1_TECHNICAL_SPEC.md` §1 tier 3: ZK proof of VIN ownership | Not built (already logged as SC-12) | — |
| `MOBI_VID1_TECHNICAL_SPEC.md`: `birthCertHash` = IPFS hash, `certificateOfOrigin: ipfs://…`; contract comments `V1:35`, `V2:76` ("IPFS hash") | keccak256 of the canonical VC; "No IPFS node is involved anywhere" | `BC:12-16`, `BC:160-166` |
| `MOBI_VID1_TECHNICAL_SPEC.md` architecture: `revokeVehicle()` | No such function. Only the inherited owner-only `revokeIdentity`; neither manufacturer nor authority can revoke | `E:250-259` |
| `MOBI_VID1_TECHNICAL_SPEC.md` §3: `resolve_vid_did()` reading `getVehicleBirth` with an `https://dlt.mobi/ns/vid/v1` context | Not in `mobi-vid`. `RES:_resolve_ethr` reads no chain state. `RES:_resolve_mobi` (`RES:510-560`) is a placeholder: VIN *in* the DID (`did:mobi:<VIN>`, which `BC:18-22` rejects for privacy), `publicKeyHex="0x..."`, `ipfs://Qm...` | `RES:342-404`, `RES:510-560` |
| `MOBI_VID1_TECHNICAL_SPEC.md` success criteria: "MOBI VID I requirements checklist 100%" and "Birth certificate contains all required fields" | 2 of 8 VID I MUSTs fully met, and 7 of 15 S2-mandatory VBC fields present (§1) | this file |
| Contract headers `V1:10-14`, `V2:12-18`: "Standards Compliance: MOBI VID I … MOBI VID II … W3C Verifiable Credentials v1.1" | Partial VID I (§1). VID II is a repo-defined model. The VC layer emits the **VC DM 2.0** context (`SCH:32`; see SC-06), and the contracts verify no VC (they store a hash) | `SCH:32`, `V2:77` |
| `MOBI_VID2_SSI_DESIGN.md` UC 9: after a theft report "any attempt to transfer ownership blocked" | `THEFT_REPORT` has no effect on `transferVehicleOwnership` | `V1:341-376`, `V2:239-294` |
| `MOBI_VID2_SSI_DESIGN.md` UC 5: recall "issued to all affected vehicles (by VIN range)", "blockchain automatically notifies all owners" | One event per vehicle per transaction; no batch or notification | `V2:239-294` |
| `DECOMMISSION` event (V2 enum; design "Vehicle scrapped/totaled") | Records an event only. The identity is neither revoked nor frozen, and later events and transfers are still accepted | `V2:46`, `V2:239-294` |
| `MOBI_VID2_SSI_DESIGN.md` SSI table: "Privacy by Design ✅ … 3-tier VIN privacy" | 2 of 3 tiers (SC-12) | — |
| `MOBI_VID_RESEARCH.md` §VID I "Core Requirements" and §VID II "Key Lifecycle Events" | Paraphrases of press material, not of the standard. S3 prioritises only registration and maintenance. Accidents, end of life, odometer fraud, etc. are listed as "Other Use Cases Considered", without requirements. | S3 TOC |
| Security matrix `SEC` row for MOBI-VID-V2: "signatureReplay: N/A (no signed/relayed operation in this implementation)" | Out of date: `attestEvent` takes and verifies a domain-separated signature (`V2:319-365`), and replay is tested in `JS::attestEvent verifies the attestation signature on-chain…` | `SEC` (MOBI-VID-V2 block) |
| `PLAN_MOBI_SUMO.md` A.0 and `README.md`: "32 tests" for the Python MOBI layer | 36 collected and passing | test run above |

### 5.2 Code the design documents and MOBI text do not mention (repository additions)
- K-3 and K-4 hardening: the public `changeOwner` is blocked for born vehicles (`V1:322-328`), and only a pristine identity can be born (`V1:250`). Tested in `JS` "K-3" and "K-4" blocks.
- On-chain, domain-separated attestation signature verification (`V2:319-365`), byte-compatible with the Python digest (`LE:237-253`).
- Fail-closed revocation status for birth and event VCs (`BC:331-345`; `PY::TestRevocationStatus` ×4).
- Odometer-rollback heuristic `LE:431-444`. Only the *no-anomaly* case is tested (`PY::TestHistoryAggregation::test_no_odometer_rollback_detected`). No test injects a rollback (**I-U** for the detection branch).
- The global `OWNER` role (`V2:61`) lets one `OWNER`-role address report MAINTENANCE, ACCIDENT, MODIFICATION, THEFT_REPORT and INSURANCE_CLAIM events on any vehicle, not only its own. Neither the design document nor MOBI mentions this, and it matters for UC2-BR2.

---

## 6. Summary

| Status | VID I v2.0 (S2) | VID II UC (S3) | Total (29 counted) |
|---|---|---|---|
| Implemented + tested | 2 | 5 | **7** |
| Implemented, untested | 0 | 1 | **1** |
| Partial | 6 | 8 | **14** |
| Not implemented | 3 | 1 | **4** |
| Out of scope | 2 | 1 | **3** |
| *Not assessable (v1.0 text not public; not counted)* | 5 | — | *5* |

**What this means for the thesis's MOBI-conformance claim.** The repository does
**not** conform to MOBI VID, and the thesis should not say "MOBI VID compliant" (as the
contract headers do now) or "meets MOBI VID" (RQ3). Against the only public normative text:
- **VID I v2.0:** it meets 2 of the 8 MUST requirements outright. Two MUSTs (UVI, Entity Certificate) are absent, and the VBC carries 7 of the 15 mandatory fields.
- **VID I v1.0:** the version the design documents cite cannot be checked at all, because its clauses are members-only.
- **VID II:** it meets 5 of the 16 business requirements fully. The on-chain lifecycle model (event types, roles, attestations) is the author's own design, not a MOBI specification.

What the evidence *does* support is a narrower, defensible claim: *a MOBI-VID-inspired
application profile that implements the VID I birth-registration concept (OEM-issued,
on-chain-anchored VBC credential with a W3C DID) and the VID II maintenance-traceability
requirements, checked clause-by-clause against the public MOBI texts with the gaps
listed.* H4 ("MOBI VID generalizes across identity backends") should be read as
statements about *this profile*, not about the MOBI standard. The two cheapest gaps to close
before chapter 4 is frozen are:
- **R6 (UVI)**: publish the existing 64-hex `vinHash` as the UVI.
- **D4 (VBC fields)**: add the seven missing fields to the `VehicleBirthCertificate` schema.

The `getVehicleDID` 0x-prefix bug (R1) should be fixed before any figure or listing shows an on-chain DID.

---

## 7. Proposed scope-change entries (text only; not yet in `docs/SCOPE_CHANGES.md`)

The numbers are provisional: append them after the last entry at the time of merge.

| ID | Date | Item | Change | Reason | Evidence | Thesis treatment |
|---|---|---|---|---|---|---|
| P-1 → SC-14 | 2026-10-04 | MOBI VID I v2.0 VID-D2 / VID-D3 (key-lifecycle and key-management best practice: NIST SP 800-57, ISO/IEC 11770, FIPS 200, ISO/IEC 27001) | **Out of scope** | Organisational and operational controls (HSM custody, key ceremonies, ISMS). They cannot be shown by a research prototype that uses test keys, and they do not discriminate between the identity standards compared. `birth_certificate.py` already declares key distribution and HSM custody out of scope. | `docs/MOBI_VID_CHECKLIST.md` §1 | One sentence in ch. 4 (threat-model assumptions): keys are assumed to be managed per D2/D3 |
| P-2 → SC-15 | 2026-10-04 | MOBI VID II UC1-BR2 (owner wallet tied to a government-provided identity) | **Out of scope** | It needs a government identity source or KYC provider. Owners are pseudonymous addresses throughout the testbed. | checklist §2 | Ch. 7 future work, with VC-based government ID (e.g. a mobile driving licence) as the route |
| P-3 → SC-16 | 2026-10-04 | MOBI VID I v2.0 VID-R6 (UVI) and VID-R8 / R3 (Entity Certificate) | **Decision pending:** implement or record as a deviation | Neither exists. The UVI could be the existing 64-hex `vinHash` with a JSON-LD wrapper (small). An EC could be a VC issued by the registry authority (moderate). Without them, 2 of 8 VID I MUSTs are unmet by design. | checklist §1 | Either implement before ch. 4 is frozen, or state both as recorded deviations next to every MOBI mention |
| P-4 → SC-17 | 2026-10-04 | VBC field set (VID-D4) | **Decision pending** | The `VehicleBirthCertificate` schema has 7 of 15 mandatory fields, and 3 differ in type or format (year int vs TEXT, make free text vs WMI, date string vs ms timestamp). Adding the fields is a schema-only change, but it would re-baseline the birth-VC size and gas (claim register rows on birth cost). | checklist §1, `vc_schemas.py:131-146` | Extend and re-measure, or report the reduced field set as a deviation |
| P-5 → SC-18 | 2026-10-04 | VID-D1 (different DIDs per relationship) | **Deferred**, linked to SC-02 and M5 | One long-lived DID per vehicle. Note2.D1 permits this for data collection, but not for V2X unlinkability. M5 measures what per-pseudonym DIDs would cost. | checklist §1; `PLAN_MOBI_SUMO.md` M5 | Bounded privacy section (SC-02); ch. 7 |
| P-6 → SC-19 | 2026-10-04 | VID II UC2-BR2 (owner-consented repair access) and UC1-BR5 (VRA-initiated transfer) | **Decision pending:** fix or record as a design deviation | Lifecycle writes are gated by globally assigned roles, not by owner consent, and a global `OWNER` role can write to any vehicle. Transfers are owner-only, so a VRA cannot start one. A fix (require an owner-granted ERC-1056 delegate for event writes; add a VRA co-signature path) changes the gas of `recordLifecycleEvent`, which affects claim rows and the M3 pinned gas figure. | checklist §2, §5.2 | If not fixed: name it in ch. 4 as a deviation and in the threat model as a write-authorisation gap |
| P-7 → SC-20 | 2026-10-04 | MOBI VID I v1.0 (2019) §3.3, §4.3, §4.5, §5, §7, and the VID II technical reference implementation | **Not assessable:** clause text members-only | The only public v1.0 text is an 8-page preview. MOBI replaced v1.0 with v2.0 (2024), which drops the system-level requirements. The VID II RI and its schemas are members-only. | checklist §0, §4 | Bound every MOBI statement to "the public MOBI VID I v2.0 and VID II UC texts". Name v1.0 only as the historical origin. |
