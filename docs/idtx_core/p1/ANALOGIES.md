# WP 1.5 — Analogy Matrix

**Home:** Appendix G-E · **Produced:** 2026-10-24 by Explore (analogies pass)
**Scope:** each of the 12 `IMinimalSSI` functions + the IDTx concept, mapped to its closest analogue in three identity worlds, with the point where the analogy **breaks** stated per row.

**Columns.**
- **(A) Centralized / today's web ID:** OAuth 2.0 / OpenID Connect, SAML 2.0, X.509 PKI + OCSP/CRL, LDAP / SCIM directories, ABAC (NIST SP 800-162) PDP/PEP.
- **(B) National / digital ID:** eIDAS 2.0 (Reg (EU) 2024/1183 amending 910/2014) + EUDI Wallet ARF, ISO/IEC 18013-5 mobile driving licence (mDL/mdoc), NIST SP 800-63-4 assurance levels.
- **(C) CAV / C-V2X identity:** IEEE 1609.2 security services, ETSI TS 102 941 trust & privacy management, SCMS pseudonym certs, MOBI VID.

**Sourcing convention.** A cell marked **[src]** cites a section/claim read at the primary source this pass. **[sec]** = corroborated from a technical secondary source only (primary paywalled/unreached). **[recalled]** = from general knowledge, *not* verified at source — do not state as fact. `no analogue` = the function has no counterpart in that world.

**Functions** (per `BASIC_ID_SET_EXTENSION.md` §1–§2.1): F1 createDID · F2 resolve · F3 changeOwner/rotate · F4 delegates · F5 attributes · F6 execute/agent-proxy · F7 deactivate · F8 issueCredential · F9 verifyCredential · F10 revokeCredential · F11 createPresentation · F12 relayed/sponsored op (U5 meta-tx) · + IDTx concept.

---

## Matrix

### F1 — createDID (identifier creation + VIN binding)
| World | Closest analogue | Where it breaks |
|---|---|---|
| A | OIDC: provisioning a `sub` at the IdP / X.509: CA issuing an end-entity cert, RFC 5280 §4.1 **[src]** (SCIM `POST /Users`, RFC 7644 **[recalled]**) | The web analogue requires an authority (IdP/CA) to create the account; `did:ethr` needs no creation tx — every key is already an identity. |
| B | eIDAS/EUDI: issuing Person Identification Data (PID) into a wallet **[src: ARF implements Reg 2024/1183]**; NIST SP 800-63-4 identity proofing & enrollment §2.2 + [SP800-63A] **[src]** | National ID binds the identifier to a **proofed natural person** (IAL); createDID binds to a VIN with no proofing of a person. |
| C | SCMS enrollment-certificate provisioning (Brecht et al. 2018, arXiv 1802.05323) **[src]**; IEEE 1609.2 enrollment cert **[sec]**; MOBI VID "birth certificate" **[recalled]** (repo: MOBI `registerVehicleBirth`, `MOBIVIDRegistry.sol:227`) | SCMS enrollment is issued by a CA after device bootstrapping; createDID is self-asserted, VIN-uniqueness enforced by an L3 commitment, not a CA. |

### F2 — resolve (R1 owner / R2 by VIN / R3 document)
| World | Closest analogue | Where it breaks |
|---|---|---|
| A | OIDC UserInfo endpoint / Discovery; LDAP search (RFC 4511 **[recalled]**); X.509 chain building (RFC 5280 §6 path validation **[recalled]**) | Web resolution hits a live authoritative server; DID resolution replays an append-only on-chain log (grows with history, `ANALYSIS.md` §3, #31), no server to trust. |
| B | mDL data retrieval / device engagement, ISO 18013-5 §8.2–8.3 **[sec]**; EUDI wallet presentation of PID **[recalled]** | mDL "resolution" is a holder-to-verifier device exchange (holder present), not a public lookup; DID resolve is public and holder-absent. |
| C | SCMS/1609.2: validating a message's attached certificate chain **[sec]**; ETSI TS 102 941 trust-list distribution **[sec]** | V2X "resolution" is in-message cert validation at the receiver, offline; DID R3 is an on-chain/RPC rebuild. |

### F3 — changeOwner / rotate controller (U1/U4)
| World | Closest analogue | Where it breaks |
|---|---|---|
| A | X.509 key rollover / re-issuance by the CA (RFC 5280 **[src for cert model]**); account owner reset at IdP **[recalled]** | Web rotation is mediated by the CA/IdP; `changeOwner` is a self-signed on-chain tx (ERC-1056 §Identity ownership) with no authority. |
| B | eIDAS/EUDI wallet re-binding / device replacement **[recalled]**; SP 800-63-4 authenticator rebinding §2.3 + [SP800-63B] **[src]** | National rebinding re-runs proofing or binding ceremony; `changeOwner` transfers control with a single key, no re-proofing. |
| C | SCMS re-enrollment with a new enrollment key **[sec]**; 1609.2 cert reissue **[sec]** | V2X rotation is a CA-issued new credential; `changeOwner` mutates the same registry record, keeping the same identifier. |

### F4 — add / revoke delegate (U2/R4/D1)
| World | Closest analogue | Where it breaks |
|---|---|---|
| A | OAuth 2.0 delegated authorization — access token to a client, RFC 6749 §1.1 roles / §1.3 grant / §1.4 token **[src]**; LDAP/SCIM group membership **[recalled]** | OAuth delegates *access to resources* via a token to a third-party client; a DID delegate is a *key authorized to act for the identity* (authentication/assertion), time-boxed in the registry. |
| B | eIDAS: wallet authorizing a relying party to request attributes **[recalled]** | National-ID "delegation" is mostly consent to disclose, not a standing signing key for another party; no per-key TTL analogue. |
| C | no analogue — V2X devices do not delegate signing keys to third parties; pseudonym certs are self-held, not delegated **[sec reasoning]** | V2X privacy model gives one device many pseudonyms, never a key to another party; delegate concept is absent. |

### F5 — set / revoke attribute (U3/R3, D2)
| World | Closest analogue | Where it breaks |
|---|---|---|
| A | LDAP/SCIM attribute write (RFC 7644 PATCH **[recalled]**); OIDC claims at the IdP **[recalled]**; X.509 subject/extension fields RFC 5280 §4.1.2/§4.2 **[src]** | Directory/cert attributes are authority-written and queryable; ERC-1056 attributes are self-written and **not directly readable by a contract** (AR-1, `ANALYSIS.md` §2 L1 row). |
| B | mDL data elements (ISO 18013-5 §8.3 data model **[sec]**); EUDI (Q)EAA attestation of attributes **[recalled]** | mDL/EAA attributes are issuer-signed and selectively disclosed by the holder; DID attributes are self-asserted and public. |
| C | 1609.2 certificate App Permissions / PSID-SSP fields **[sec]**; ETSI TS 102 941 authorization-ticket permissions **[sec]** | V2X "attributes" are CA-granted permissions inside a cert; DID attributes are owner-set service/key entries, no CA. |

### F6 — execute / agent-proxy (X1)
| World | Closest analogue | Where it breaks |
|---|---|---|
| A | no analogue — web identities authenticate; they do not themselves *execute* actions as a first-class identity primitive (closest: a service account calling an API with its token, RFC 6749 **[src]**) | OAuth service account acts via a token at an API; ERC-4337/ERC-725 `execute` has the *identity contract itself* perform an on-chain call (`FM` X1: only ERC-4337/ERC-725xy native). |
| B | no analogue — national-ID holders present credentials; the ID does not act | mDL/eIDAS identities are presented, never executors. |
| C | no analogue — a V2X cert signs messages; it does not execute transactions | 1609.2/SCMS identity signs broadcasts; no agent-proxy execution concept. |

### F7 — deactivate (D3)
| World | Closest analogue | Where it breaks |
|---|---|---|
| A | account deactivation / cert revocation at end-of-life, X.509 CRL RFC 5280 §5 **[src]**; SCIM `DELETE` / `active:false` **[recalled]** | Web deactivation removes/flags a record an authority holds; DID deactivate sets owner→0 (`did:ethr` §Delete) — the history stays permanently on chain. |
| B | eIDAS wallet revocation / suspension **[recalled]**; SP 800-63-4 account suspension/termination §2.2 **[src]** | National deactivation is authority-driven with legal effect; DID deactivation is self-signed and irreversible-in-record. |
| C | SCMS revocation of a device's certificates (Brecht et al. 2018) **[src]**; 1609.2/ETSI CRL distribution **[sec]** | V2X deactivation is CA-side revocation propagated by CRL; DID deactivate is an on-chain record flag, no list to distribute. |

### F8 — issueCredential (V1 issuer-key anchor + V3 status anchor)
| World | Closest analogue | Where it breaks |
|---|---|---|
| A | OIDC ID Token issuance (signed JWT) **[recalled]**; X.509 CA issuing a cert, RFC 5280 §4.1 **[src]**; SAML 2.0 assertion issuance **[recalled]** | Web issuance delivers the signed artefact to the subject; here the VC is signed **off chain** (`2_w3c-ssi-layer`) and only the issuer key/status is anchored on chain (L4, `ANALYSIS.md` §2). |
| B | eIDAS (Q)EAA — qualified electronic attestation of attributes by a QTSP **[recalled]**; mDL issuance by the issuing authority, ISO 18013-5 **[sec]**; W3C VC Data Model 2.0 §4.7 Issuer **[src]** | National issuance carries legal/qualified status and strong issuer identity; repo issuance anchors an arbitrary issuer key with no trust framework. |
| C | SCMS Pseudonym CA issuing pseudonym certs via butterfly key expansion (Brecht et al. 2018) **[src]**; 1609.2 cert issuance **[sec]** | SCMS issues short-lived, unlinkable pseudonym certs in bulk; repo issues a single anchored, linkable credential. |

### F9 — verifyCredential (V6 status check + R4 issuer key)
| World | Closest analogue | Where it breaks |
|---|---|---|
| A | OIDC ID-Token validation (signature + `iss`/`aud`/`exp`) **[recalled]**; X.509 path validation + OCSP status (RFC 6960 **[recalled]**, status model RFC 5280 §5 **[src]**); SAML assertion validation **[recalled]** | Web verify queries a live OCSP responder / IdP; repo verify reads an on-chain status anchor (V6) + off-chain proof check (register #21/#27) — ERC-1056 pure has **no read primitive** (AR-1). |
| B | mDL verifier (reader) checking issuer signature + MSO, ISO 18013-5 §9 **[sec]**; SP 800-63-4 verifier/RP §2.4 federation + [SP800-63C] **[src]** | mDL verification is an offline device exchange with issuer-data authentication; repo verify needs a chain read for status. |
| C | 1609.2 receiver verifying message signature + cert chain **[sec]**; ETSI TS 102 941 trust-model validation **[sec]** | V2X verify is purely in-message/offline at line rate; repo verify is an on-chain (or cached, freshness-k) read, `ANALYSIS.md` §3. |

### F10 — revokeCredential (V5)
| World | Closest analogue | Where it breaks |
|---|---|---|
| A | X.509 CRL entry / OCSP revoked status, RFC 5280 §5 **[src]** (OCSP RFC 6960 **[recalled]**); OAuth token revocation (RFC 7009 **[recalled]**) | CRL/OCSP revocation is published by the CA and pulled by verifiers; repo revoke writes an on-chain status slot a contract reads directly (enables IDTx). |
| B | eIDAS attestation revocation via status list **[recalled]**; W3C Bitstring Status List v1.0 §2 **[src]** | National status lists are privacy-preserving off-chain bitstrings; on-chain revoke trades that query-privacy for direct contract-readability. |
| C | SCMS revocation via linkage values + Linkage Authorities, efficient CRL (Brecht et al. 2018) **[src]** | SCMS can revoke *all* of a device's unlinkable pseudonyms from linkage values in one CRL entry; repo revokes a single credential, no linkage structure. |

### F11 — createPresentation (F8 in canon numbering / P1)
| World | Closest analogue | Where it breaks |
|---|---|---|
| A | SAML 2.0 holder-of-key / bearer assertion presentation to an SP **[recalled]**; OAuth token presentation to a resource server, RFC 6749 §1.4 **[src]** | Web presentation hands a token/assertion to a server in one session; repo P1 anchors a replay-protected presentation hash on chain (no ERC provides it natively — canon structural finding). |
| B | mDL presentation (device engagement + selective disclosure), ISO 18013-5 §8.2 **[sec]**; EUDI wallet presentation with SD-JWT/mdoc **[recalled]**; W3C VC 2.0 §4.13 Verifiable Presentations **[src]** | mDL/EUDI presentation is holder-driven selective disclosure with unlinkability goals; repo P1 is a public on-chain anchor, inherently linkable. |
| C | no analogue — a V2X device broadcasts signed messages; there is no holder-assembled "presentation" of credentials to a verifier **[sec reasoning]** | V2X has no presentation step; the cert travels inside every message. |

### F12 — relayed / sponsored operation (U5 meta-transaction)
| World | Closest analogue | Where it breaks |
|---|---|---|
| A | OAuth client acting *on behalf of* a user with delegated authority, RFC 6749 §1.1/§1.3 **[src]**; SAML delegation **[recalled]** | OAuth delegation authorizes resource access; a meta-tx has a **relayer pay gas** to submit the user's signed intent — a fee/sponsorship concept with no web-ID counterpart. |
| B | no analogue — national-ID frameworks do not model a third party paying a transaction fee to submit a user's signed action **[recalled]** | The sponsored-gas economics are blockchain-specific. |
| C | no analogue — V2X messaging has no fee-relayer / sponsored-submission model **[sec reasoning]** | Broadcasts are not fee-metered transactions. |

### IDTx — identity-dependent transaction (concept)
| World | Closest analogue | Where it breaks |
|---|---|---|
| A | **ABAC PDP/PEP** (NIST SP 800-162 §3.2, Jan 2014): a Policy Decision Point evaluates attributes and a Policy Enforcement Point enforces, "render a decision / enforce the decision" **[src]** | ABAC gates on the *caller's* attributes at a trusted PDP; an IDTx gates on the state of an identity the transaction *names*, evaluated inside execution (`ANALYSIS.md` §4.4; closing section below). |
| B | eIDAS: a relying party admitting an action conditioned on a presented attestation's validity **[recalled]** | National-ID decisions are off-chain RP decisions (freshness via status list); an IDTx re-evaluates on chain, with an ordering race (§4.5). |
| C | 1609.2/ETSI TS 102 941: a receiver admitting a message conditioned on cert permissions/validity **[sec]** | V2X admission is an off-chain receiver decision at the message (an "identity-dependent decision", `ANALYSIS.md` §4.1), never an on-chain transaction. |

---

## Where the on-chain IDTx differs from an ABAC PDP call

ABAC (NIST SP 800-162 §3.2 **[src]**) is the closest web-world analogue to the IDTx, and the thesis's framing is precisely the three places they part (`ANALYSIS.md` §4.4–4.5):

1. **Trust locus.** An ABAC decision is rendered by a *trusted* Policy Decision Point against attributes it fetches, and gates on the **caller's** attributes. An IDTx has no PDP: the dependency is evaluated by the contract itself, inside the transaction, against the state of an identity the transaction **names** — not the sender (§4.4, and the P2-D8 definition in §4.1 that excludes sender authentication and identity-administration). The "guard on attributes" is shared with ABAC; the named-identity dependency is what distinguishes it (§4.3 patterns table).

2. **Freshness.** A PDP reads attributes and decides once; an off-chain identity-dependent *decision* (a verifier accepting a message, §4.1) carries the staleness bound the repo measured: at most k−1 messages after a revocation, now in chain time (#32, #37; §4.4). An in-contract IDTx closes the *in-execution* gap by re-evaluating at execution (`fulfil`), but only at the cost of a second transaction and live reads (§4.6 cost model).

3. **Ordering risk.** A PDP call has no block-ordering semantics. An IDTx that re-evaluates on chain still leaves the **ordering race** between the dependency's change and the dependent transaction open (§4.5 threat table: TOCTOU closed in-execution, ordering race *not* — single automine node, not measured). Mitigations named: deadlines, commit-reveal, the ordering literature (review §3.1). This is the risk an ABAC PDP call simply does not have.

The thesis positions the IDTx against ABAC, ERC-3643/ONCHAINID (the closest prior art, §4.3), account-abstraction validation and oracle-conditioned execution — claiming the *definition, storage-locus taxonomy and freshness dimension*, not the guard mechanism itself (`ANALYSIS.md` §4.3, §6).

---

## Status — sourced vs. [recalled] vs. [sec]

**[src] (read at primary source this pass):** RFC 6749 OAuth 2.0 §1.1/§1.3/§1.4 (Oct 2012); RFC 5280 X.509 §4.1/§4.1.2/§4.2 cert, §5 CRL (May 2008); NIST SP 800-162 ABAC §3.2 PDP/PEP (Jan 2014); NIST SP 800-63-4 §2.2/§2.3/§2.4 + [SP800-63A/B/C] (approved 2025-04-28); W3C VC Data Model 2.0 §4.7/§4.13 (15 May 2025); W3C Bitstring Status List v1.0 §2 (15 May 2025); SCMS Brecht et al. 2018 arXiv 1802.05323 (enrollment/pseudonym certs, butterfly keys, linkage-value revocation); EUDI ARF implements Reg (EU) 2024/1183 amending 910/2014.

**[sec] (corroborated secondary only — primary paywalled/unreached):** ISO/IEC 18013-5 section numbers (§8.2 device engagement, §8.3 data model, §9.1.1 — from a TOC reproduction and W3C-CCG/Pomcor analyses, not the ISO text); IEEE 1609.2 certificate types and message structure; ETSI TS 102 941 lifecycle/enrolment/authorization (TOC §6.1/§6.2.3.2/§6.2.3.3 from iteh.es sample + patent citations).

**[recalled] (NOT verified at source — do not state as fact):** OpenID Connect Core 1.0 section numbers; SAML 2.0 (OASIS) assertion/delegation section numbers; OCSP (RFC 6960) section numbers (RFC 5280 was confirmed to reference the older RFC 2560, not 6960); LDAP (RFC 4511) and SCIM (RFC 7644) operation section numbers; OAuth token-revocation RFC 7009; MOBI VID specification (no MOBI primary doc fetched — repo MOBI contracts were read, but the external MOBI VID standard was not); EUDI ARF exact topic/section numbers and its mandated mdoc/SD-JWT-VC format references; eIDAS (Q)EAA and PID exact article references.

**Specs I could not access at source:** ISO/IEC 18013-5 full text (paywalled); IEEE 1609.2 full text (paywalled); ETSI TS 102 941 normative body (only TOC/secondary reached — ETSI deliver PDFs were listed but not fetched); the MOBI VID standard document; NIST SP 800-63A/B/C companion volumes (base volume 800-63-4 read; companions referenced but not separately fetched). The two NIST PDFs (800-162, 800-63-4) were downloaded and read via local text extraction.
