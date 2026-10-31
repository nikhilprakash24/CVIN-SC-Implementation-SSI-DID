# WP 2.1–2.3 — Comparison of Identity Substrates Against Real-World ID Systems

**Home:** Appendix G-G · lead section of companion paper SP-9.
**Produced:** 2026-10-31 (Phase 2, Standards Scholar pass).
**Builds on (seed, tags carried forward):** `p1/ANALOGIES.md` (three-worlds matrix), `p1/THESIS_DRAFT.md` §3.x
(the function set as a *capability surface for comparison*, **not** a proven-minimal set), `p1/PRIMITIVES.md`
(mechanism column), `DETAILED_PLAN.md` §3 Phase 2 (WP 2.1–2.3).

**Evidence discipline (unchanged from Phase 1).** Every claim carries a tag. **[src]** = read at a primary source
(this pass or Phase 1). **[sec]** = corroborated from a technical secondary source only (primary paywalled/unreached).
**[recalled]** = general knowledge, **not** verified at source — never stated as fact. `n-a` = the function has no
counterpart in that paradigm (and the cell says why). This pass upgraded the free IETF/OASIS/OpenID primaries that
`ANALOGIES.md` left open (OIDC Core, SAML 2.0 Core, OCSP RFC 6960, LDAP RFC 4511, SCIM RFC 7644); the paywalled specs
(ISO 18013-5, IEEE 1609.2, ETSI TS 102 941) stay **[sec]** as the seed required.

---

## §1 — Selection criterion and the ten systems (WP 2.1)

**Selection criterion (stated so an examiner cannot call the set arbitrary).**
Each system is the *canonical, standardized* realization of a distinct point on a **two-dimensional plane** — not a
single ordered axis (obj. M3). The two dimensions are **(x) trust centralization** (one live authority holds everything
→ no authority, state is a public ledger write) and **(y) presentation / evaluation locus** (where identity state is
read: live authority call · holder-present device exchange · public/append-only lookup · in-transaction read). A single
line through these systems would be **non-monotonic**, so the set is *not* claimed to be a clean ordering; it is claimed
to **cover the plane** with no gap and (per point below) with the trust-locus duplicates made explicit.

Honest adjacencies the one-axis framing hid:
- **S1 (OIDC) and S2 (SAML) occupy the same trust-locus point** (a live federated IdP mints and vouches for the
  identifier). S2 is retained not as a distinct trust locus but as the **pre-OIDC incumbent on the same point** — it
  shows the paradigm predates OIDC, and it is dropped from any claim of "distinct axis point."
- **S4 (eIDAS), S5 (mDL), and S6 (V2X) all have a central issuing authority**; they differ on the *y* dimension
  (wallet-held online vs device-held offline vs pseudonym-rotated offline), **not** on trust locus. They are kept
  separate because §3 measures the presentation/offline-freshness dimension, which genuinely separates them.
- **S9 (FIDO2) and S10 (ledgerless SSI)** are the two comparators this pass adds: both are **authority-independent at
  the identifier** (no issuer mints it) yet **non-ledger**, so they land at a trust-locus point the original eight left
  empty between "central authority" and "public ledger."

The ten are chosen so that (i) **the trust-locus duplicates are named, not hidden** (S1≈S2), (ii) together they **span
the plane** from "one authority holds everything" to "no authority, state is a public ledger write," with the
authority-independent-but-ledgerless region now populated (S9/S10), and (iii) each is a *deployed standard with a
readable specification*, not a research prototype. The thesis's own substrates (DID+VC SSI and the on-chain-gated token)
sit at the decentralized end, so the set places the contribution **against the strongest comparator at every other point
on the plane** — including, now, the non-ledger self-created-key comparators that most directly contest §4's old
"uniquely" claim. This is the same organizing idea as the Phase-1 three-"worlds" analogy matrix; Phase 2 widens it to
ten named standards on a two-dimensional plane.

| # | System | What it is (one sentence) | Why it earns its place (axis point) |
|---|---|---|---|
| S1 | **OAuth 2.0 / OpenID Connect** | A federated authentication layer over OAuth 2.0 where an OpenID Provider issues a signed ID Token asserting a subject (`sub`) to a relying party **[src: OIDC Core §2, §1.2]**. | The **centralized/federated IdP** point: one live authority mints and vouches for the identifier. |
| S2 | **SAML 2.0** | An OASIS XML framework where a SAML authority (IdP) issues signed `<Assertion>`s carrying authentication and attribute statements to a service provider **[src: SAML Core §2.3.3, §2.7]**. | The **enterprise-federation** point: assertion-based SSO, the pre-OIDC incumbent; shows the paradigm is older than OIDC. |
| S3 | **X.509 PKI (+ OCSP / CRL)** | A certificate-authority hierarchy binding a public key to a subject in a signed certificate, with revocation served by CRLs or the OCSP responder **[src: RFC 5280 §4.1/§5; OCSP RFC 6960 §2.2]**. | The **PKI/CA** point: the root of trust is a certificate chain, not an account; the original of "issue → verify → revoke." |
| S4 | **eIDAS 2.0 / EUDI Wallet** | The EU regulation (Reg (EU) 2024/1183 amending 910/2014) and its Architecture Reference Framework, issuing Person Identification Data and (Q)EAAs into a holder-controlled wallet **[src: ARF implements Reg 2024/1183]**. | The **national/government digital-ID** point: identifier bound to a *legally proofed natural person*, wallet-held. |
| S5 | **ISO/IEC 18013-5 mDL** | The mobile driving-licence / mdoc standard: an issuing authority provisions an MSO-signed credential a holder presents device-to-device with selective disclosure **[sec]**. | The **device-held national credential** point: offline, holder-present, no live lookup — the sharpest contrast to a ledger read. |
| S6 | **V2X PKI (IEEE 1609.2 / ETSI TS 102 941 / SCMS)** | The vehicular security stack: an enrollment CA bootstraps a device, a pseudonym CA issues short-lived unlinkable certs (SCMS butterfly keys), receivers verify in-message at line rate **[src: SCMS Brecht et al. 2018; 1609.2/102 941 sec]**. | The **V2X pseudonym-authority** point: the thesis's own CAV domain; privacy-by-pseudonymity with CA-side revocation. |
| S7 | **SSI — DID + VC (this thesis's substrates)** | `did:ethr` over ERC-1056 with W3C VC Data Model 2.0 credentials: every key is an identifier, the document is event-sourced, credentials are signed off-chain with issuer key/status anchored on-chain **[src: ERC-1056; DID Core 1.0; VC DM 2.0]**. | The **decentralized self-sovereign** point: no authority creates the identifier; the substrate under the whole thesis. |
| S8 | **ERC-3643 / ONCHAINID** | A permissioned-token standard where transfers are gated by a compliance contract that reads claims on an on-chain ONCHAINID identity contract **[src ERC-3643 isVerified/Compliance; closest prior art THESIS_DRAFT §6.8.4]**. | The **on-chain-gated** point: identity used as a *transaction precondition* — the closest deployed prior art to the IDTx. |
| S9 | **WebAuthn / FIDO2 passkeys** | A W3C/FIDO authentication standard: the authenticator generates a credential key pair on-device at registration and the relying party stores the public key; authentication proves possession of the private key **[src WebAuthn §1/§4; FIDO CTAP2.1 §6.1.2]**. | The **self-created-key, no-issuer, no-ledger** point: holder-generated key-identity — the property §4 wrongly called S7-unique — realized with no authority and no chain. |
| S10 | **Ledgerless SSI (did:key / did:web + VC DM 2.0)** | The full W3C DID+VC surface with no ledger: did:key derives the DID directly from a generated key (purely generative), did:web hosts a `did.json` over HTTPS, and VC DM 2.0 provides off-ledger issuance/verification/presentation **[src did:key Create/Read; did:web Create/Read; VC DM 2.0 §4.7/§7.1/§4.13]**. | The **authority-independent-but-ledgerless** point: the direct control on T1 — full self-sovereign identity with none of the public/ordered/costly write. |

The plane is populated densely, so adjacent systems share features (S1/S2 same trust locus; S4/S5/S6 same issuing
authority, different presentation locus; S7/S8 both on-chain; S9/S10 both self-created-key-but-ledgerless). They are
kept separate (except that S1/S2 are declared the *same* trust-locus point) because each pins a *different* trust locus
**or** evaluation/presentation locus on the plane, which is exactly what §3's trade-off matrix measures.

---

## §2 — Function × system matrix (WP 2.2)

Rows are the Phase-1 function set (`THESIS_DRAFT.md` §3.x.2) plus the IDTx concept. Cell value is **Native** /
**Composed** (built from named primitives) / **Absent** / **n-a** (function does not apply to the paradigm), with a
3–6-word mechanism note and a source tag. "Composed" names the primitive(s) from `PRIMITIVES.md` or the analogue's
own building block.

**Coding rule (restated at the matrix head, author's own convention).** `n-a` = **the function has no counterpart in
that paradigm** (the cell says why); `Absent` = the paradigm **has the concept but this realization lacks it**
(tried-and-failed, a genuine deficiency). The two are not interchangeable: an `Absent` cell counts against a system, an
`n-a` cell does not.

Reminder from `THESIS_DRAFT.md` §3.x.2: `execute` and the relayed/sponsored meta-transaction are **blockchain-account
capabilities with no identity-world analogue** — so their cells across S1–S6 and S9 are **`n-a`** (recoded this pass
from `Absent`, which had wrongly implied a deficiency; obj. M1): those paradigms authenticate and present, they do not
*act* as a first-class identity primitive. Likewise `delegate` is **`n-a`** for S5/S6/S9 (V2X pseudonyms are self-held,
none delegated; a FIDO2 authenticator is scoped to one RP) — recoded from `Absent` for the same reason. The
relayed/meta-tx operation is not given its own row (it is `n-a` everywhere but S7/S8, where it is a gas-sponsorship
pattern over `execute`); it is noted here and in §4.

**Two deployed non-ledger comparators added this pass (obj. F2):** **S9 = WebAuthn/FIDO2 passkeys** (W3C Web
Authentication Level 2, FIDO CTAP2.1) — the authenticator self-generates the credential key pair on-device, **no
issuing authority mints the identifier**, the RP stores the public key; it is an *authenticator*, not a credential
system, so most Set-B rows are `n-a`. **S10 = ledgerless SSI (did:key / did:web + VC DM 2.0)** — the *full* DID+VC
capability surface (createDID/resolve/issue/verify/present) with **no ledger**; it is the direct control on T1's claim
that authority-independence must be bought with a public, ordered, costly write.

| Function | S1 OIDC | S2 SAML 2.0 | S3 X.509 PKI | S4 eIDAS/EUDI | S5 mDL | S6 V2X/SCMS | S7 SSI (DID+VC) | S8 ERC-3643 | S9 FIDO2/WebAuthn | S10 ledgerless SSI (did:key/web) |
|---|---|---|---|---|---|---|---|---|---|---|
| **createDID** | n-a — IdP provisions `sub` **[src §1.2]** | n-a — IdP-managed NameID **[recalled]** | Composed — CA issues cert, CSR+sig **[src §4.1]** | Composed — PID issued to wallet **[src]** | Composed — authority provisions mdoc **[sec]** | Composed — SCMS enrollment cert **[src]** | **Native** — key-is-DID; VIN L3 commit **[src]** | Composed — deploy ONCHAINID, `registerIdentity` **[src ERC-3643 §Identity Registry]** | **Native** — authenticator self-generates key pair, no issuer **[src WebAuthn §4; CTAP2 §6.1.2]** | **Native** — key-is-DID (did:key) / host `did.json` (did:web), no ledger **[src did:key Create; did:web Create]** |
| **resolve** | Native — UserInfo, live IdP **[src §5.3]** | Composed — IdP metadata + query **[recalled]** | Composed — chain building, AIA fetch **[src cert; §6 recalled]** | n-a — wallet presents to RP, no public lookup **[src Reg 2024/1183 Art 5a]** | Composed — device engagement, holder-present **[sec §8.2]** | Composed — in-message cert validation **[sec]** | **Native** — event-sourced log replay⁴ **[src]** | Native — on-chain claim/key reads **[src ERC-3643 isVerified]** | Composed — RP-side credential-ID→pubkey lookup⁴ **[src WebAuthn §1/§4]** | Native — did:key deterministic expand / did:web HTTPS GET⁴ **[src did:key Read; did:web Read]** |
| **rotate (changeOwner)** | n-a — IdP account reset, no controller key **[recalled]** | n-a — IdP-side, no holder key **[recalled]** | Composed — CA rekey / re-issuance **[src cert]** | Composed — wallet rebinding ceremony **[src 800-63B §2.3]** | Composed — issuer re-provisions device **[sec]** | Composed — SCMS re-enrollment **[sec]** | **Native** — self-signed `changeOwner` tx **[src]** | Composed — ERC-734 key management **[recalled: ERC-734-unpublished]** | n-a — re-register credential, no in-place rotation **[recalled]** | Composed — did:web re-publish `did.json`; did:key immutable **[src did:web Create]** |
| **delegate** | Composed — OAuth access token to client **[src §1.3]** | Composed — delegated assertion to SP **[recalled]** | Composed — subordinate / proxy cert **[recalled]** | Composed — representation; consent to RP, no standing key **[src Reg 2024/1183 def(5a) representation]** | n-a — pseudonyms self-held, none delegated **[sec]** | n-a — pseudonyms self-held, none delegated **[sec]** | **Native** — `addDelegate`, on-chain TTL **[src]** | Composed — ERC-734 purpose-scoped keys **[recalled: ERC-734-unpublished]** | n-a — authenticator scoped to one RP, no delegation **[src WebAuthn §4]** | Composed — DID-doc verification relationships / `capabilityDelegation` **[recalled]** |
| **attribute (set/revoke)** | Composed — IdP claims; SCIM PATCH **[src §3.5.2]** | Composed — AttributeStatement, authority-written **[src §2.7]** | Composed — subject DN / extensions **[src §4.1.2/§4.2]** | Composed — (Q)EAA attribute attestation **[src Reg 2024/1183 def(44)/(45), §9 Art 45b]** | Composed — issuer-signed mdoc data elements **[sec §8.3]** | Composed — PSID/SSP permissions in cert **[sec]** | Native (write) — `setAttribute`; **write-only, no on-chain contract read (AR-1)** **[src]** | Native — ERC-735 `addClaim`, readable **[src ERC-3643 §Claims/ONCHAINID]** | n-a — authenticator, not a credential/attribute system **[src WebAuthn §4]** | Composed — self-asserted service/key entries in DID doc **[src did:key Doc Creation; DID Core]** |
| **execute (agent proxy)** | n-a — identities authenticate only **[src]** | n-a — SSO only **[recalled]** | n-a — keys sign, don't act **[recalled]** | n-a — wallet stores/presents, not executor **[src Reg 2024/1183 def EUDI Wallet]** | n-a — presented only **[sec]** | n-a — signs messages only **[sec]** | **Native** — ERC-4337/725x `execute` **[src]** | Composed — ERC-725X `execute` call **[src ERC-725 §ERC725X]** | n-a — authenticate only, not an executor **[src WebAuthn §4]** | n-a — no execution substrate (not a chain account) **[recalled]** |
| **deactivate** | Composed — SCIM DELETE / `active:false` **[src §3.6]** | Composed — IdP disables principal **[recalled]** | Composed — CRL/OCSP revoke at EOL **[src §5]** | Composed — wallet revocation, legal effect **[src 800-63 §2.2]** | Composed — issuer revokes mdoc **[sec]** | Composed — SCMS CRL revocation **[src]** | **Native** — owner→0; history persists **[src]** | Composed — registry delist (`deleteIdentity`) **[src ERC-3643 §Identity Registry]** | Composed — RP deletes stored credential **[recalled]** | Composed — did:web remove/empty `did.json`; did:key n-a **[recalled]** |
| **issueCredential** | Composed — signed ID Token (JWS) **[src §2]** | **Native** — signed `<Assertion>` **[src §2.3.3]** | **Native** — CA issues signed cert **[src §4.1]** | Native — QTSP (Q)EAA issuance **[src Reg 2024/1183 def(45), §9 Art 45b]** | **Native** — MSO-signed mdoc **[sec]** | **Native** — pseudonym cert bulk issuance **[src]** | Composed — off-chain VC; on-chain key/status anchor **[src §4.7]** | Native — trusted claim issuer `addClaim` **[src ERC-3643 §Trusted Issuers Registry]** | n-a — proves key possession, no third-party credential **[src WebAuthn §4]** | **Native** — VC issuer signs off-ledger **[src VC DM 2.0 §4.7]** |
| **verifyCredential** | Composed — validate sig+iss+aud+exp **[src §3.1.3.7]** | Composed — sig + SubjectConfirmation check **[src §2.4.1.1]** | Composed — path validation + OCSP **[src OCSP §2.2]** | Composed — verify issuer sig + status **[src Reg 2024/1183 §9 Art 45b; Annex V status]** | Composed — reader checks MSO sig, offline **[sec §9]** | Composed — offline in-message cert verify **[sec]** | Composed — off-chain proof + on-chain status read (V6) **[src]** | Composed — `isVerified` claim check at transfer **[src ERC-3643 isVerified]** | Composed — authentication-ceremony assertion signature check **[src WebAuthn §4]** | Composed — verify VC proof + resolve issuer DID, no ledger **[src VC DM 2.0 §7.1]** |
| **revokeCredential** | Composed — token revocation (RFC 7009) **[recalled]** | Composed — short validity window (`NotOnOrAfter`) **[recalled]** | **Native** — CRL / OCSP revoked **[src §5; OCSP §2.2]** | Composed — status-list revocation **[src Bitstring §2]** | Composed — issuer status list **[sec]** | **Native** — linkage-value CRL revokes all pseudonyms **[src]** | Composed — on-chain status write (V5) **[src]** | Composed — `removeClaim` / `removeTrustedIssuer` **[src ERC-3643 §Trusted Issuers Registry]** | n-a — no credential; RP removes registration **[recalled]** | Composed — status-list (Bitstring), hosted off-ledger **[recalled]** |
| **createPresentation** | n-a — token presentation to RS, no VP **[src §1.4]** | Composed — bearer / holder-of-key assertion to SP **[src §2.4.1.1]** | n-a — cert in TLS handshake, no holder VP **[recalled]** | Native — wallet selective-disclosure VP **[src Reg 2024/1183 Art 5a selective disclosure]** | **Native** — mdoc selective disclosure **[sec §8.2]** | Absent — cert travels in every message **[sec]** | Composed — on-chain replay-protected anchor (P1) **[src; no native ERC]** | n-a — claims read on-chain, no presentation step **[src ERC-3643 isVerified]** | n-a — assertion to RP, no VP **[src WebAuthn §4]** | **Native** — VC DM 2.0 Verifiable Presentation, holder-assembled **[src VC DM 2.0 §4.13]** |
| **IDTx (concept)** | Absent on-chain — off-chain RP decision **[src; ABAC SP 800-162 §3.2]** | Absent on-chain — off-chain SP decision **[recalled]** | Absent on-chain — off-chain RP decision on OCSP **[src]** | Absent on-chain — off-chain RP admission **[src Reg 2024/1183 Art 5a — relying-party model]** | Absent on-chain — off-chain verifier decision **[sec]** | Absent on-chain — off-chain receiver decision, *k*−1 staleness **[sec]** | **Native** — in-contract guard on named identity **[src]** | **Native** — transfer gated on identity claims **[src §6.8.4]** | n-a — authentication / off-chain decision, no transaction **[src]** | **n-a — full DID+VC but no ledger ⇒ off-chain decision, not in-tx evaluation (tests T1)** **[src]** |

> **Footnote 4 (`resolve`, obj. m4).** "Native" resolve is not one operation. S7 (did:ethr) and S8 resolve by **replaying
> an append-only on-chain log** (grows with history, `ANALYSIS.md` §3 #31); S10 did:web and S9 resolve by a **single
> endpoint call** (one HTTPS GET of `did.json`; one RP-side credential-ID lookup), and S10 did:key by **deterministic
> expansion** with no call at all. Same label, three very different freshness/cost/availability profiles — the
> distinction §3 T1 and §4 turn on.

### Per-cell notes that carry weight

- **createDID is `n-a`, not `Absent`, for S1/S2.** An IdP-issued account has no self-created identifier bound to a
  controlling key the subject holds — the authority *is* the creator (`ANALOGIES.md` F1). Saying `Absent` would imply
  the paradigm tried and failed; `n-a` records that the primitive does not apply.
- **The "most functions are patterns" finding (THESIS_DRAFT §3.x.2) appears across the row totals.** On S7 the Set-B
  functions and `createPresentation` are Composed over one generic write (`setAttribute`/`addClaim`), and `createPresentation`
  has **no native ERC** anywhere — it is realized as a replay-protected anchor. This is why the function set, not any
  one standard's surface, is the comparison axis.
- **S7 `attribute` read limitation (AR-1).** `setAttribute` writes natively, but ERC-1056 exposes **no attribute-value
  read to a contract** (`idtx.test.js:138`); this is precisely what forces the IDTx's separate commitment store and is
  the one place S8 (ONCHAINID claims are contract-readable) is *more* capable than the thesis's own base registry.
- **revokeCredential: the two `Native` cells (S3, S6) are the mature revocation designs.** X.509 publishes a
  CA-signed CRL / OCSP status [src]; SCMS can revoke *all* of a device's unlinkable pseudonyms from one linkage-value
  CRL entry [src]. S7's on-chain status write (V5) is Composed and trades query-privacy for direct contract-readability
  — the pivot §4 returns to.
- **IDTx row is the contribution boundary — and S9/S10 sharpen it.** Only S7 and S8 can evaluate an identity dependency
  *inside a transaction*; S1–S6, S9, and S10 all make an off-chain **identity-dependent decision** (`ANALYSIS.md` §4.1),
  which shares the freshness dimension but is not a transaction. S10 is the decisive control: it carries the *entire*
  authority-independent DID+VC surface (createDID/resolve/issue/verify/present all Native or Composed, no issuer) yet its
  IDTx cell is **`n-a` because it has no ledger** — so the in-transaction evaluation, not authority-independence, is what
  requires the chain. S8 is the closest prior art; the thesis's claim over it is the **storage-locus × encoding ×
  evaluation-point taxonomy** and the **on-chain freshness/ordering analysis**, not the guard mechanism (THESIS_DRAFT §6.8.4).
- **S9/S10 load-bearing cells.** S9 `createDID` is **Native** — the authenticator generates the key pair on-device and
  no authority mints the identifier (WebAuthn §4; CTAP2 §6.1.2): this is exactly the "self-created key-identity" §4 used
  to call S7-unique, and it exists here with no ledger at all. S10 `createDID` is **Native** by a different route
  (did:key is purely generative; did:web hosts `did.json`), again no issuer, no ledger. Both therefore sit at a distinct
  trust-locus point from S1–S8 and both have IDTx `n-a`.
- **m2 — S7>S8 on delegate/rotate rests on a `[recalled]` S8 cell; the comparison is dropped.** S8's `rotate` and
  `delegate` are keyed on **ERC-734** (unpublished draft, 404 at eips.ethereum.org this pass), so those two S8 cells are
  `[recalled: ERC-734-unpublished]`. §4 therefore makes **no** "S7 beats S8 on delegate/rotate" claim — the S8 side is
  unverified at primary.

---

## §3 — Trade-off matrix and axis-level analysis (WP 2.3)

Eight axes, one row per system. Cells are compressed; the prose below states the genuine tradeoffs.

| Axis | S1 OIDC | S2 SAML | S3 X.509 PKI | S4 eIDAS/EUDI | S5 mDL | S6 V2X/SCMS | S7 SSI (DID+VC) | S8 ERC-3643 | S9 FIDO2 | S10 ledgerless SSI |
|---|---|---|---|---|---|---|---|---|---|---|
| **Trust locus** (root of trust) | OpenID Provider **[src]** | SAML IdP/authority **[src]** | CA chain to root **[src]** | Member-state QTSP + EU trust list **[src]** | Issuing authority (IACA) **[sec]** | SCMS root + pseudonym CA **[src]** | Controlling key + ledger consensus **[src]** | Compliance contract + claim issuers **[src ERC-3643 Compliance + Trusted Issuers]** | Holder-generated key; RP stores pubkey (no authority) **[src WebAuthn §4]** | Controlling key; did:web adds DNS/host trust **[src did:web]** |
| **Availability dependence** (auth needs it live?) | **IdP must be live** **[src §5.3]** | IdP must be live for SSO **[recalled]** | OCSP responder live, **or stapled at handshake (RFC 6066 §8) ⇒ none live** **[src RFC 6066 §8]** | Issuer for issuance; presentation offline **[src Reg 2024/1183 Art 5a]** | **Fully offline** at presentation **[sec]** | **Fully offline** at receive **[sec]** | Ledger node / RPC for reads **[src]** | Ledger live for every transfer **[src ERC-3643 transfer]** | RP live at auth; no third-party authority **[src WebAuthn §4]** | did:key none at resolve; did:web HTTPS host live **[src did:key/did:web Read]** |
| **Revocation / freshness latency** | token TTL; revoke via RFC 7009 **[recalled]** | assertion `NotOnOrAfter` window **[recalled]** | CRL period / OCSP real-time; short-lived certs ⇒ TTL freshness **[src]** | status-list refresh interval **[src]** | status list; stale if offline **[sec]** | CRL distribution; cached ⇒ *k*−1 msgs **[sec]** | on-chain write ⇒ next-block, public **[src]** | on-chain claim ⇒ next-block **[src ERC-3643 isVerified]** | RP deletes credential; no global revocation list **[recalled]** | status-list refresh; no ledger **[recalled]** |
| **Privacy & linkability** | IdP sees every login (NASCAR problem) **[recalled]** | IdP sees every SSO **[recalled]** | cert is public, linkable **[src]** | selective disclosure, unlinkability goal **[src Reg 2024/1183 Art 5a selective disclosure]** | **selective disclosure** per presentation **[sec]** | **pseudonym rotation**, unlinkable by design **[src]** | public ledger, **inherently linkable** **[src]** | public ledger + claims, linkable **[src ERC-3643 §Claims on-chain]** | **per-RP scoped keys**, non-correlatable across RPs **[src WebAuthn §4]** | did:key per-use unlinkable + VC selective disclosure; **did:web is a fixed correlator** **[src VC DM 2.0 §4.13]** |
| **Cost model** | infra / per-IdP, no per-op fee **[recalled]** | infra, no per-op fee **[recalled]** | CA fee per cert; OCSP infra **[recalled]** | national infra; wallet free to holder **[src Reg 2024/1183 Art 5a]** | provisioning infra **[sec]** | SCMS infra; bulk pseudonyms **[sec]** | **gas per write**; reads growth-priced **[src #31/#49]** | **gas per transfer** (compliance check) **[src ERC-3643 transfer]** | no per-op fee; authenticator hardware **[recalled]** | **no gas**; did:web hosting infra only **[src did:key Intro]** |
| **Governance** (who changes the rules) | OpenID Foundation + each OP **[recalled]** | OASIS + each deployment **[recalled]** | CA/Browser Forum + root programs **[recalled]** | EU law + member states **[src]** | ISO + issuing authorities **[sec]** | IEEE/ETSI + SCMS manager **[sec]** | W3C/EIP + chain governance **[src]** | token issuer + ERC authors **[recalled: off-spec]** | W3C + FIDO Alliance **[recalled]** | W3C + DNS/registrar (did:web) **[recalled]** |
| **Offline operation** | No — needs IdP **[src]** | No — needs IdP **[recalled]** | Partial — cached CRL / stapled status **[src]** | Yes at presentation **[src Reg 2024/1183 Art 5a]** | **Yes — designed offline** **[sec]** | **Yes — designed offline** **[sec]** | No — needs ledger read **[src]** | No — needs ledger **[src ERC-3643 transfer]** | No — RP online at auth **[recalled]** | **did:key yes** (deterministic); did:web no **[src did:key Intro]** |
| **Recovery / key rotation** | IdP account recovery **[recalled]** | IdP-side reset **[recalled]** | CA rekey / re-issue **[src]** | wallet rebinding ceremony **[src]** | issuer re-provision **[sec]** | SCMS re-enrollment **[sec]** | self-signed `changeOwner`; **lost key = lost identity** **[src]** | ERC-734 key management contract **[recalled: ERC-734-unpublished]** | re-register; multi-device passkey sync **[recalled]** | did:web re-publish; **did:key lost key = lost identity** **[src did:web]** |

### The genuine axis-level tradeoffs

**T1 — The ledger removes the *live-CA-at-decision* dependency (relative to S1/S2), but does not beat offline freshness, and pays a public, ordered, costly write (the headline — restated, obj. F1).**
The property S7/S8 genuinely remove is a **live authority *at the moment of decision*** of the S1/S2 kind: OIDC queries
the live UserInfo endpoint [src §5.3], a classic SAML/IdP SSO needs the IdP live. For these, S7/S8 read status (V6)
directly from ledger state — no responder to be down, no CA to trust at decision time. **But the claim is narrower than
the earlier draft's "across S1–S4," for two reasons an examiner will press.** (i) **X.509 (S3) already achieves
status-at-handshake with no responder live at decision:** OCSP **stapling** (RFC 6066 §8 Certificate Status Request
[src]) delivers a CA-signed status inside the TLS handshake, **short-lived certificates** make the certificate's own TTL
the freshness bound, and a **cached CRL** serves offline — so S3 is *partial-offline*, not live-authority-bound, and the
headline does not apply to it cleanly. (ii) **S5/S6 and the new S10 are decision-time authority-independent with no
ledger at all:** mDL and V2X verify offline against a device-held signature [sec], and **did:key/did:web (S10)** resolve
and verify VCs with no live issuer and no chain. So the honest statement is: **S7/S8 remove the live-CA-at-decision
dependency relative to S1/S2, and *match* — do not beat — the offline freshness-independence of S5/S6/S10, while paying
a cost those systems do not.** That cost is exact and three-fold, the Phase-1 finding (`THESIS_DRAFT` §6.8.3,
`ANALYSIS.md` §5): the revocation that OCSP/status-list serves as a *private, cacheable pull* becomes an **on-chain
write** that is (a) **public** — every revocation is visible and linkable, losing the Bitstring Status List's
query-privacy; (b) **ordered** — it takes a block position, opening the **mempool ordering race** between a dependency's
change and the dependent transaction that a later re-check (`fulfil`) closes *inside execution* but not in the mempool
(AR-10); and (c) **costly** — gas per write (#49) and reads priced in history growth (#31).

**S7's residual availability dependency (named, obj. F1).** "No live authority at decision" does **not** mean "no live
dependency": S7/S8 reads require a **ledger node or RPC provider to be live and in sync** at decision time (§3
availability row [src]). The thesis trades a trusted CA/IdP for an *untrusted-but-still-live* ledger endpoint; it does
not eliminate the liveness requirement, only moves it off the authority and onto consensus infrastructure. S10 did:key
has no such dependency; S10 did:web depends on an HTTPS host.

**T2 — Offline operation and on-chain freshness are mutually exclusive, and the CAV domain sits on the wrong side for S7.** *(Provisional — contingent on `[sec]` cells, obj. M4: the S5 mDL and S6 V2X offline-verification cells this tradeoff rests on are corroborated from secondary sources only; the primary standards (ISO/IEC 18013-5, IEEE 1609.2) remain paywalled and unread this pass. The shape of the tradeoff is firm; the S5/S6 specifics are down-stated from settled to provisional pending a primary read. Free SD-JWT-VC / mdoc material can carry much of this in Phase 3.)*
S5 (mDL) and S6 (V2X) are *designed offline*: a receiver verifies an mdoc or a 1609.2 message with no network call,
which is non-negotiable for a vehicle verifying a safety message at line rate [sec]. The price is staleness: a cached
V2X verifier accepts at most **k−1 messages after a revocation** (`ANALYSIS.md` §3, #32/#37, pre-D51-fix and
provisional). S7's on-chain read gives *next-block* freshness but **requires the ledger live** — it cannot make the
offline, line-rate decision V2X needs. This is the sharpest cross-domain tension for a thesis sited in CAV: the
substrate that best solves freshness is the one least able to operate in the vehicle's offline reality. The thesis's
honest position (THESIS_DRAFT §6.8) is that the on-chain IDTx governs *transactions* (tolls, claim anchoring,
ownership transfer), not the safety-message path, where the off-chain identity-dependent *decision* with its k−1 bound
remains the right tool.

**T3 — Privacy is bought three different ways, and the ledger forecloses all three.** *(Provisional — contingent on `[sec]` cells, obj. M4: the S5 selective-disclosure and S6 pseudonym-rotation privacy cells are `[sec]` (ISO/IEC 18013-5, IEEE 1609.2 / ETSI TS 102 941 paywalled, unread this pass); the SCMS linkage-value mechanism is `[src]` via Brecht et al. 2018, but the mDL selective-disclosure detail is not. Down-stated from settled to provisional; free SD-JWT-VC / mdoc primaries can firm this in Phase 3.)*
S4/S5 buy unlinkability with **selective disclosure** (reveal only the needed attribute per presentation); S6 buys it
with **pseudonym rotation** (many short-lived unlinkable certs, revocable en masse by linkage value — the one design
that gets privacy *and* efficient revocation together) [src]. Both rest on the credential staying off the public record.
S7 and S8 publish to a shared ledger, so admissions and status are **inherently linkable** — and the Phase-1 ZK tier
(`ZkVinGate`) hides *which VIN* but still emits the identity address in clear (`ZkVinGate.sol:113`), so it does not
recover cross-scope unlinkability (PRIMITIVES card 7). The commitment pattern is **equality-only** (AR-5): it hides the
VIN's value but supports no predicate over it. So the ledger's contract-readability — the very property that *enables*
the IDTx — is in direct tension with every off-ledger system's privacy mechanism.

**T4 — Governance mobility tracks the trust locus, inversely to recovery safety.**
Where one authority is the root (S1–S3, S6), the rules change fast (an OP, a CA program, an SCMS manager decides) and
recovery is easy (the authority re-issues). Where trust is decentralized (S7), no one can unilaterally change the rules
*or* recover a lost key: `changeOwner` is self-signed, so **a lost controlling key is a lost identity** with history
frozen on chain [src]. S4 (eIDAS) is the deliberate middle: EU law changes the rules slowly and deliberately, and a
wallet rebinding ceremony recovers the holder — buying both governance legitimacy and recovery at the cost of national
infrastructure. The thesis substrate is at the extreme: maximal self-sovereignty, minimal recovery and governance
recourse.

**T5 — The Cost row is marginal-only, which flatters the authority systems and penalizes SSI (obj. M6).** The §3 Cost
axis measures **marginal per-operation cost**, on which S7/S8 look expensive ("gas per write") and eIDAS/SCMS look cheap
("no per-op fee"). This is a measurement artifact of the axis, not a true economic ranking. **S4 (eIDAS) and S6 (SCMS)
each carry a large one-time / ongoing capital cost the marginal axis hides**: eIDAS presupposes national QTSP and
trust-list PKI infrastructure and member-state wallet programs; SCMS presupposes a multi-tier CA hierarchy (root,
enrollment, pseudonym, linkage authorities) with butterfly-key provisioning at fleet scale. **S7/S8 externalize their
capital cost onto a shared public ledger** (no bespoke PKI to stand up) and pay it back as marginal gas. The honest
comparison therefore needs **two cost views**: a *marginal* view (gas-per-write, where SSI is High and authority
systems Low) and an *amortized-capital* view (national PKI / SCMS infrastructure, where the authority systems carry
large sunk and ongoing cost and SSI carries little). A claim that "SSI is costly" is true only on the marginal axis and
is not a total-cost-of-ownership statement — §4 carries this caveat forward. S9 (hardware authenticators) and S10
did:key (free, no infra) sit at the low-capital end of both views.

---

## §4 — Where the thesis's on-chain SSI sits (honest placement)

**What S7 (and the IDTx over it) genuinely wins — the *combination*, not any single Native cell (obj. F1/F2/M2).**
The headline is **not** "S7 uniquely does X." It is:

> **S7's distinction is that it combines FIDO2-like self-created key-identity (S9) *with* ERC-3643/S8-like
> contract-readable on-chain evaluation (S8) inside a single EVM-derived function set — the *combination* within this
> function set, not any single Native cell, and not a property no other system has.**

Each half of that combination exists elsewhere, which is exactly why the two new comparators were added. **The
self-created key-identity is not unique to S7:** S9 (FIDO2) generates the key pair on-device with no issuer, and S10
(did:key/did:web) carries the full authority-independent DID+VC surface — both with **no ledger** (§2 `createDID` all
Native). **The in-transaction evaluation is not unique to S7 either:** S8 (ERC-3643) reads claims on-chain to gate a
transfer. What no *other* single system does is hold **both** at once on one substrate. Relatedly, the earlier
"S7 is the only column with `createDID`/`resolve`/`rotate`/`delegate`/`execute` all Native" line is **withdrawn as
tautological (obj. M2):** those are EVM-substrate operations, so an EVM-native identity is Native on them *by
construction*; "Native within the EVM-derived function set by construction" is the honest phrasing, and it carries no
contribution weight. The contribution weight sits on the **taxonomy and freshness analysis**, not the row-count.

On the trade-off matrix S7/S8 **remove the live-CA-at-decision dependency** relative to S1/S2 (T1) — a revocation is
reflected at the next block with no responder to query — but they **match, not beat**, the offline freshness-independence
of S5/S6/S10, and they retain a residual **ledger-node/RPC liveness** dependency. Against the closest prior art,
S8/ERC-3643, the thesis does **not** claim the guard mechanism, and makes **no** "beats S8 on delegate/rotate" claim
(those S8 cells are `[recalled: ERC-734-unpublished]`, obj. m2). It claims the **storage-locus × encoding ×
evaluation-point taxonomy** and the **on-chain freshness/ordering analysis** (THESIS_DRAFT §6.8.4): object-attribute
ABAC (NIST SP 800-162 §3.2 [src]) realized on a public ledger, with the dimension ABAC's PDP model never needed —
*where* the depended-on state lives and *when* it is read.

**One concession the completeness narrative owes (obj. m3).** On `createPresentation` the thesis substrate is
**Composed** — a replay-protected on-chain anchor (P1) with **no native ERC** — whereas S4 (eIDAS), S5 (mDL), and the
new S10 (VC DM 2.0) each have a **native verifiable-presentation primitive**. The EVM substrate lacks a presentation
primitive that three comparators have natively; the thesis realizes presentation as a pattern, not a primitive.

**The costs Phase 1 established, carried forward unsoftened.** The seed is explicit that these are not closed:

1. **ABAC-on-chain predicate, not a new access-control concept.** The IDTx *is* object-attribute ABAC on-chain
   (THESIS_DRAFT §6.8.4); the earlier "ABAC gates the caller, IDTx names another identity" framing is **withdrawn** as a
   mischaracterization of ABAC. The contribution is the taxonomy and the ledger-specific freshness/ordering analysis,
   stated narrowly.
2. **Equality-only commitments (AR-5).** The L3 salted-hash commitment binds a VIN without disclosing it but gates by
   **equality only** — no range, knowledge, or computation predicate over the hidden value without disclosing the
   opening or a ZK proof (PRIMITIVES card 6). The ZK tier that would lift this (`ZkVinGate`) is outside the 10-adapter
   conformance gate and still emits the identity in clear.
3. **Replay exposure on `addClaim`/`attestEvent` (D52).** The two carried-signature paths that are *half of the measured
   "true IDTx"* recover a **raw keccak digest** — no EIP-191, no chain-id, no nonce (`CVINCombinedIdentity.sol`;
   PRIMITIVES card 1 item e′). They carry a cross-chain replay exposure the thesis does **not** claim to have closed,
   and an old never-revoked claim can be re-anchored.
4. **Ordering race (AR-10).** `fulfil` re-checks on-chain and so closes the time-of-check/time-of-use gap *inside
   execution*, but **not** the mempool ordering race between the dependency's change and the dependent transaction
   (single automine node, not measured). This is exactly the risk the off-chain comparators (S1–S6) do not have, because
   their PDP call has no block-ordering semantics (T1). It is the price of making the PDP itself a public-ledger
   transaction.
5. **Freshness numbers are pre-fix and provisional.** The k−1 staleness bound (#32/#37) predates the D51 chain-time fix
   (`ANALYSIS.md` §3, A3b); cited for its *shape*, not its superseded values. Clean measurement is post-thesis (P5).

**Net placement.** S7 is the right substrate for identity used as an *on-chain transaction precondition* with next-block
freshness and no live authority at decision (its home: tolls, claim anchoring, ownership transfer), and its distinction
is the **combination** of self-created key-identity with contract-readable in-transaction evaluation on one EVM-derived
substrate — not sole possession of either half (S9/S10 have the first, S8 the second). It is the *wrong* substrate for
the offline, line-rate, privacy-by-pseudonymity path that V2X (S6) occupies — and the thesis says so. On cost, "SSI is
costly" holds only on the **marginal** (gas-per-write) axis; on an **amortized-capital** axis the authority systems
(eIDAS national PKI, SCMS multi-tier CA) carry large sunk infrastructure that SSI externalizes onto a shared ledger
(obj. M6), so the cost claim is not a total-cost-of-ownership verdict. The honest summary: the IDTx buys **in-transaction
freshness** and **decision-time authority-independence** (the latter shared with S5/S6/S10) by paying in publicity, a
residual ledger-liveness dependency, marginal cost, an unresolved ordering race, and (on the two measured paths) an open
replay exposure.

---

## Closing ledger — cells still `[recalled]` or `[sec]` (unverified at primary this pass)

**Matrix dimensions after this pass: 12 function rows × 10 systems = 120 cells** (was 12 × 8 = 96; the WP-F2 pass added
the **S9 FIDO2/WebAuthn** and **S10 ledgerless-SSI** columns, 24 new cells).

**Count of function×system cells (§2) not at `[src]`: 42 of 120** — the 35 of 96 carried from the prior pass (the
Absent→n-a recode in obj. M1 changes cell *values*, not evidence tags, so that subtotal is unchanged) **plus 7 of the 24
new cells**: S9 `rotate`, `deactivate`, `revokeCredential` and S10 `delegate`, `execute`, `deactivate`,
`revokeCredential` are `[recalled]` (lifecycle/relationship specifics not pinned to a section read this pass); the other
17 new cells are `[src]`, read this pass at **W3C WebAuthn Level 2** (§1 Introduction, §4 Terminology), **FIDO CTAP2.1**
(§6.1.2 `authenticatorMakeCredential`), **W3C did:key** (Abstract/Introduction/Operations/Create/Read), **W3C did:web**
(Target system / Create / Read), **W3C VC Data Model 2.0** (§4.7 Issuer, §7.1 Verification, §4.13 Verifiable
Presentations), and **RFC 6066** (§8 Certificate Status Request, for the T1 stapling note). All six are free primaries.

WP 2.3b upgraded 17 §2 cells: the whole **S8 ERC-3643 /
ONCHAINID** column except `rotate`/`delegate` (ERC-734 is an unpublished draft, not an EIP — unreachable at primary),
read at **ERC-3643** (eips.ethereum.org/EIPS/eip-3643: `isVerified`, Identity Registry, Trusted Issuers Registry,
Claim Topics Registry) and **ERC-725** (eip-725 §ERC725X `execute`); and seven **S4 eIDAS/EUDI** cells, read at
**Regulation (EU) 2024/1183** (EUR-Lex eli/reg/2024/1183: Art 5a wallet + selective disclosure, §9 Art 45b and
definitions (42) PID / (44) EAA / (45) QEAA). Earlier upgrades to `[src]` this pass from `ANALOGIES.md`'s open cells:
**OIDC Core 1.0** (sub §1.2, UserInfo §5.3, ID Token §2, validation §3.1.3.7), **SAML 2.0 Core** (Assertion §2.3.3,
Issuer §2.2.5, SubjectConfirmation §2.4.1.1, statements §2.7), **OCSP RFC 6960** (status model §2.2, responder §4.2.2.2,
freshness §2.4), **LDAP RFC 4511** (Search §4.5, Modify §4.6, Bind §4.2), **SCIM RFC 7644** (create §3.3, PATCH §3.5.2,
DELETE §3.6).

**Still `[sec]` — paywalled, to stay `[sec]` until the standard is purchased/accessed (seed directive):**
- **ISO/IEC 18013-5 (mDL):** every S5 cell — createDID, resolve (§8.2), attribute (§8.3), issue, verify (§9),
  revoke, createPresentation, deactivate, and the S5 IDTx/decision cell (~12 cells).
- **IEEE 1609.2 / ETSI TS 102 941 (V2X):** S6 attribute (PSID/SSP), resolve (in-message validation), verify, and the
  S6 IDTx/decision cell where not covered by the SCMS primary (Brecht et al. 2018, which *is* [src]).

**Still `[recalled]` — reachable free primaries NOT chased this pass (candidates to upgrade next pass):**
- **ERC-3643 / ONCHAINID (S8):** `rotate` and `delegate` only — both rest on **ERC-734** (purpose-scoped key manager:
  MANAGEMENT/ACTION/CLAIM keys, `addKey`/`execute`), which remained a draft and is **not published at
  eips.ethereum.org** (eip-734/eip-735 both 404 this pass); the ONCHAINID docs landing page carries no function-level
  detail. The rest of the S8 column was upgraded to `[src]` at ERC-3643 / ERC-725 (WP 2.3b). ERC-735 `addClaim`/`removeClaim`
  semantics are nonetheless corroborated indirectly by ERC-3643's claim/Trusted-Issuers description.
- **eIDAS/EUDI (S4):** resolve, delegate, attribute, execute, issue, verify, createPresentation, and the S4 IDTx cell
  were upgraded to `[src]` at **Reg (EU) 2024/1183** (WP 2.3b). The **EUDI ARF** GitHub repo
  (github.com/eu-digital-identity-wallet/eudi-doc-architecture-and-reference-framework) **was reachable** this pass
  (README + docs tree load), but its deep ISO-mdoc / SD-JWT-VC *format-mandate* identifiers were not transcribed — the
  Regulation text carried every S4 cell, so the ARF annex detail is the remaining open item if an examiner presses the
  exact credential-format requirement.
- **SAML 2.0 (S2):** rotate, delegate (delegation restriction), deactivate, revoke, IDTx — not covered by the four
  Core sections read this pass.
- **OIDC (S1):** rotate (`n-a`), revoke (RFC 7009 not re-read).
- **X.509 (S3):** resolve (§6 path-validation section number), delegate (proxy-cert RFC 3820), createPresentation
  (`n-a`).

All five Phase-1 open items named in `THESIS_DRAFT.md` "Open items" (OIDC, SAML, OCSP, LDAP/SCIM) are now read; WP 2.3b
additionally closed the ERC-3643/ONCHAINID (ERC-734 key-management residual aside) and eIDAS/EUDI primaries. The only
spec still wholly unread is the MOBI VID external spec (not in this comparison set).
