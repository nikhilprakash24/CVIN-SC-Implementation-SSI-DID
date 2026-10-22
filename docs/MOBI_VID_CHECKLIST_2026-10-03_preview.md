# MOBI VID I — Section-Level Reconciliation of the Implementation with the Standard

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-10-03 (plan step M1)
**Source examined:** *Vehicle Identity Standard, Version 1.0*, MOBI VID Working Group,
© 2019 — the **public preview** (front matter, table of contents, foreword,
introduction; 8,765 characters of text). The normative body (sections 1–7) is
restricted to MOBI members: *"MOBI standards are available to all MOBI members …
please fill out our membership inquiry form."*
**Implementation examined:** `1_blockchain-identity/contracts/MOBI/MOBIVIDRegistry.sol`
(VID I), `MOBIVIDRegistryV2.sol` (VID II), `2_w3c-ssi-layer/mobi-vid/` (birth
certificate, lifecycle events, registry client; 32 tests), the five-backend sweep
(`4_comparison-framework/results/mobi_vid_backends.csv`).

---

## 1. The finding that matters most

Every MOBI VID requirement in this repository's design documents
(`MOBI_VID_RESEARCH.md`, `MOBI_VID1_TECHNICAL_SPEC.md`, `MOBI_VID2_SSI_DESIGN.md`) was
derived from **announcements and secondary sources**, not from the standard's
normative text, which is member-only. The implementation therefore realises the
standard's *published concepts* (VBC, VIN linkage, immutability, lifecycle events,
entity roles) but **cannot claim clause-level conformance** to VID I. The standard's
own vocabulary — **UVI**, **Entity Certificate**, **Revocation Certificate**, the four
numbered **Roles** and their relationship APIs, the **Distributed Virtual Machine**
requirement — does not appear in the project at all, which is how an examiner would
discover the gap.

This is recorded as **SC-14**. The thesis must (a) say that MOBI VID conformance was
assessed against the public preview and public announcements, (b) use the standard's
vocabulary where a mapping exists (§3), and (c) either obtain the full text (MOBI
membership, or an academic request to vid@dlt.mobi) and complete this table, or state
the limitation in chapters 3 and 7.

## 2. Coverage map against the standard's table of contents

Status: **C** covered by implementation with a test · **P** partially covered ·
**N** not covered · **?** cannot assess — normative text not available.

| Standard section (from the TOC) | What the preview says | Implementation evidence | Status |
|---|---|---|---|
| 1 Scope | — (body restricted) | — | ? |
| 2 Terms, Acronyms, Definitions | VID, VBC, UVI defined in the Introduction: "At the birth event, the VID consists of the vehicle birth certificate (VBC) and is indexed by a unique vehicle identifier (UVI)"; VID is "an authoritative form of identity that can be cryptographically verified" | VID ↔ vehicle identity address + `did:ethr`; VBC ↔ `VehicleBirth` struct + birth-certificate VC; UVI ↔ no explicit element (see §3) | P |
| 3.1 System Overview | Vehicle with a securely stored wallet holding certificates (identity, ownership, warranties, mileage); entities (owner, lien-holder, OEM, DMV) with their own wallets/certificates and relationships to the vehicle; mobility networks and OEM data stores | Holder wallet (`vc_holder.py`); issuer roles MANUFACTURER, DEALER, SERVICE_CENTER, INSURANCE_COMPANY, GOVERNMENT_DMV, POLICE, INSPECTION_STATION, OWNER; no *lien-holder* role; no data-marketplace element | P |
| 3.2 System Security and Identity | "cryptographically verified"; "decentralized infrastructure with permissioned entity access" | secp256k1 signatures throughout; manufacturer/issuer authorisation (`authorizeManufacturer`, `authorizeIssuer`); permissioned writes, public reads | P (body restricted for specifics) |
| 3.3 Key Management and Key Rotation | — | ERC-1056 `changeOwner`/delegates give key rotation for the vehicle identity; no rotation defined for *entity* keys in the MOBI contracts | P / ? |
| 3.4 Addressing and URIs | — | `getVehicleDID` → `did:ethr:<chainId>:<address>`; W3C DID resolution | P / ? |
| 4.1 Unique Vehicle Identifier (UVI) | indexes the VID at birth | `vinHash` (salted) + `vinHashToVehicle` lookup serves as the index; whether UVI = VIN-derived or a separate identifier is unknown | ? |
| 4.2 Vehicle Birth Certificate (VBC) | the certificate at the birth event | `registerVehicleBirth` (vinHash, encrypted VIN, birthCertHash, firstOwner, attributes); `BirthCertificateIssuer.issue_birth_certificate` as a VC; tests `test_birth_succeeds_…`, `test_vc_is_schema_valid_and_anchored`, `test_tampered_birth_vc_fails_verification` | C (concept) / ? (fields) |
| 4.3 Enum and Time Definitions | — | `EventType` (11), `IssuerRole` (9); block timestamps; `test_enums_mirror_contract` | ? |
| 4.4 Entity Certificate | certificates held by entities asserting relationship to the vehicle | Issuer authorisation on-chain + VCs issued by entities; no standalone "entity certificate" object | P |
| 4.5 Revocation Certificate | — | identity revocation (ERC-1056 registry), VC `credentialStatus` revocation, issuer revocation (`revokeIssuerAuthorization`); no revocation *certificate* artefact | P |
| 5 Certificate API — 5.2.1–5.2.6 Role-to-Role relationship APIs (Roles 1–4) | the preview lists Role 4→4/3/2, 3→4, 3→create/revoke, 2→self, 1→4/3/2 | `allowedIssuersPerEventType` matrix (`test_allowed_roles_match_contract_matrix`) is a role-permission matrix, but the standard's four-role model is not mapped; the project uses nine application roles | N (mapping) / ? |
| 6 Entities, 6.2 Entity Structure | — | issuer registry (address → role) | P / ? |
| 7 System Requirements, 7.2 Distributed Virtual Machine | — | EVM (Hardhat local; Sepolia planned) — presumably satisfies a DVM requirement | ? |

## 3. Vocabulary mapping (to be used in chapter text)

| Standard term | Project term | Note |
|---|---|---|
| VID (Vehicle Identity) | vehicle DID / `did:ethr` identity | same concept |
| VBC (Vehicle Birth Certificate) | `VehicleBirth` on-chain + birth-certificate VC off-chain | the project splits the VBC into an anchor and a credential; state this |
| UVI (Unique Vehicle Identifier) | salted `vinHash` | **assumption** — the preview does not define the UVI's construction |
| Entity Certificate | issuer authorisation + entity-issued VCs | no single artefact; state the mapping |
| Revocation Certificate | revocation state (identity / VC status / issuer) | no artefact; state the mapping |
| Roles 1–4 | `IssuerRole` (9 application roles) | the standard's role numbering is unknown; do not claim equivalence |
| Wallet (data-store) | `vc_holder.py` holder wallet | same concept |
| Distributed Virtual Machine | EVM | likely the same; unverified |

## 4. What this changes

- `SCOPE_CHANGES.md` **SC-14**: MOBI VID conformance claims are limited to published
  concepts; clause-level conformance requires the member text.
- Chapter 3: one paragraph with the mapping table and the limitation.
- Chapter 4: use the standard's terms with the project's in parentheses.
- Chapter 7: obtaining the normative text and completing this table is future work —
  or, if the author can obtain it, this file is the place to finish the job.
- The five-backend "fidelity" grades (`mobi_vid_backends.csv`) remain valid as a
  comparison of *concept* support (birth anchoring, lifecycle events, multi-party
  attestation, verifiable claims, revocation); they are not clause conformance.
