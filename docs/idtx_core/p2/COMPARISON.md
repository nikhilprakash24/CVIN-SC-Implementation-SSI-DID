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

## §1 — Selection criterion and the eight systems (WP 2.1)

**Selection criterion (stated so an examiner cannot call the set arbitrary).**
Each system is the *canonical, standardized* realization of **one distinct point on a single ordered axis — the locus
of the root of trust and of identity state** — running

> centralized IdP → federated IdP → PKI certificate authority → national/government digital ID → device-held
> credential → V2X pseudonym authority → decentralized self-sovereign ledger → on-chain-gated token.

The eight are chosen so that (i) **no two occupy the same point** on that axis, (ii) together they **span the full
range** from "one authority holds everything" to "no authority, state is public ledger write," and (iii) each is a
*deployed standard with a readable specification*, not a research prototype. The thesis's own substrates (DID+VC SSI
and the on-chain-gated token) sit at the decentralized end, so the set is built to place the contribution **against
the strongest comparator at every other point on the axis**, not against a strawman. This is the same axis the Phase-1
analogy matrix organized by three "worlds"; Phase 2 widens it to eight named standards.

| # | System | What it is (one sentence) | Why it earns its place (axis point) |
|---|---|---|---|
| S1 | **OAuth 2.0 / OpenID Connect** | A federated authentication layer over OAuth 2.0 where an OpenID Provider issues a signed ID Token asserting a subject (`sub`) to a relying party **[src: OIDC Core §2, §1.2]**. | The **centralized/federated IdP** point: one live authority mints and vouches for the identifier. |
| S2 | **SAML 2.0** | An OASIS XML framework where a SAML authority (IdP) issues signed `<Assertion>`s carrying authentication and attribute statements to a service provider **[src: SAML Core §2.3.3, §2.7]**. | The **enterprise-federation** point: assertion-based SSO, the pre-OIDC incumbent; shows the paradigm is older than OIDC. |
| S3 | **X.509 PKI (+ OCSP / CRL)** | A certificate-authority hierarchy binding a public key to a subject in a signed certificate, with revocation served by CRLs or the OCSP responder **[src: RFC 5280 §4.1/§5; OCSP RFC 6960 §2.2]**. | The **PKI/CA** point: the root of trust is a certificate chain, not an account; the original of "issue → verify → revoke." |
| S4 | **eIDAS 2.0 / EUDI Wallet** | The EU regulation (Reg (EU) 2024/1183 amending 910/2014) and its Architecture Reference Framework, issuing Person Identification Data and (Q)EAAs into a holder-controlled wallet **[src: ARF implements Reg 2024/1183]**. | The **national/government digital-ID** point: identifier bound to a *legally proofed natural person*, wallet-held. |
| S5 | **ISO/IEC 18013-5 mDL** | The mobile driving-licence / mdoc standard: an issuing authority provisions an MSO-signed credential a holder presents device-to-device with selective disclosure **[sec]**. | The **device-held national credential** point: offline, holder-present, no live lookup — the sharpest contrast to a ledger read. |
| S6 | **V2X PKI (IEEE 1609.2 / ETSI TS 102 941 / SCMS)** | The vehicular security stack: an enrollment CA bootstraps a device, a pseudonym CA issues short-lived unlinkable certs (SCMS butterfly keys), receivers verify in-message at line rate **[src: SCMS Brecht et al. 2018; 1609.2/102 941 sec]**. | The **V2X pseudonym-authority** point: the thesis's own CAV domain; privacy-by-pseudonymity with CA-side revocation. |
| S7 | **SSI — DID + VC (this thesis's substrates)** | `did:ethr` over ERC-1056 with W3C VC Data Model 2.0 credentials: every key is an identifier, the document is event-sourced, credentials are signed off-chain with issuer key/status anchored on-chain **[src: ERC-1056; DID Core 1.0; VC DM 2.0]**. | The **decentralized self-sovereign** point: no authority creates the identifier; the substrate under the whole thesis. |
| S8 | **ERC-3643 / ONCHAINID** | A permissioned-token standard where transfers are gated by a compliance contract that reads claims on an on-chain ONCHAINID identity contract **[recalled; established as closest prior art in THESIS_DRAFT §6.8.4 [src]]**. | The **on-chain-gated** point: identity used as a *transaction precondition* — the closest deployed prior art to the IDTx. |

The axis is continuous, so adjacent systems share features (S1/S2 both IdP-centric; S4/S5 both wallet/credential;
S7/S8 both on-chain). They are kept separate because each pins a *different* trust locus or evaluation point, which is
exactly what §3's trade-off matrix measures.

---

## §2 — Function × system matrix (WP 2.2)

Rows are the Phase-1 function set (`THESIS_DRAFT.md` §3.x.2) plus the IDTx concept. Cell value is **Native** /
**Composed** (built from named primitives) / **Absent** / **n-a** (function does not apply to the paradigm), with a
3–6-word mechanism note and a source tag. "Composed" names the primitive(s) from `PRIMITIVES.md` or the analogue's
own building block.

Reminder from `THESIS_DRAFT.md` §3.x.2: `execute` and the relayed/sponsored meta-transaction are **blockchain-account
capabilities with no identity-world analogue** — their `Absent` cells across S1–S6 are the expected result, not a
deficiency of those systems. The relayed/meta-tx operation is not given its own row (it is `n-a`/`Absent` everywhere
but S7/S8, where it is a gas-sponsorship pattern over `execute`); it is noted here and in §4.

| Function | S1 OIDC | S2 SAML 2.0 | S3 X.509 PKI | S4 eIDAS/EUDI | S5 mDL | S6 V2X/SCMS | S7 SSI (DID+VC) | S8 ERC-3643 |
|---|---|---|---|---|---|---|---|---|
| **createDID** | n-a — IdP provisions `sub` **[src §1.2]** | n-a — IdP-managed NameID **[recalled]** | Composed — CA issues cert, CSR+sig **[src §4.1]** | Composed — PID issued to wallet **[src]** | Composed — authority provisions mdoc **[sec]** | Composed — SCMS enrollment cert **[src]** | **Native** — key-is-DID; VIN L3 commit **[src]** | Composed — deploy ONCHAINID contract **[recalled]** |
| **resolve** | Native — UserInfo, live IdP **[src §5.3]** | Composed — IdP metadata + query **[recalled]** | Composed — chain building, AIA fetch **[src cert; §6 recalled]** | n-a — holder presents, no public lookup **[recalled]** | Composed — device engagement, holder-present **[sec §8.2]** | Composed — in-message cert validation **[sec]** | **Native** — event-sourced log replay **[src]** | Native — on-chain claim/key reads **[recalled]** |
| **rotate (changeOwner)** | n-a — IdP account reset, no controller key **[recalled]** | n-a — IdP-side, no holder key **[recalled]** | Composed — CA rekey / re-issuance **[src cert]** | Composed — wallet rebinding ceremony **[src 800-63B §2.3]** | Composed — issuer re-provisions device **[sec]** | Composed — SCMS re-enrollment **[sec]** | **Native** — self-signed `changeOwner` tx **[src]** | Composed — ERC-734 key management **[recalled]** |
| **delegate** | Composed — OAuth access token to client **[src §1.3]** | Composed — delegated assertion to SP **[recalled]** | Composed — subordinate / proxy cert **[recalled]** | Composed — consent to RP, no standing key **[recalled]** | Absent — no key delegation **[sec]** | Absent — pseudonyms self-held, none delegated **[sec]** | **Native** — `addDelegate`, on-chain TTL **[src]** | Composed — ERC-734 purpose-scoped keys **[recalled]** |
| **attribute (set/revoke)** | Composed — IdP claims; SCIM PATCH **[src §3.5.2]** | Composed — AttributeStatement, authority-written **[src §2.7]** | Composed — subject DN / extensions **[src §4.1.2/§4.2]** | Composed — (Q)EAA attribute attestation **[recalled]** | Composed — issuer-signed mdoc data elements **[sec §8.3]** | Composed — PSID/SSP permissions in cert **[sec]** | Native (write) — `setAttribute`; **no on-chain read, AR-1** **[src]** | Native — ERC-735 `addClaim`, readable **[recalled]** |
| **execute (agent proxy)** | Absent — identities authenticate only **[src]** | Absent — SSO only **[recalled]** | Absent — keys sign, don't act **[recalled]** | Absent — presented, not executor **[recalled]** | Absent — presented only **[sec]** | Absent — signs messages only **[sec]** | **Native** — ERC-4337/725x `execute` **[src]** | Composed — ERC-725X `execute` call **[recalled]** |
| **deactivate** | Composed — SCIM DELETE / `active:false` **[src §3.6]** | Composed — IdP disables principal **[recalled]** | Composed — CRL/OCSP revoke at EOL **[src §5]** | Composed — wallet revocation, legal effect **[src 800-63 §2.2]** | Composed — issuer revokes mdoc **[sec]** | Composed — SCMS CRL revocation **[src]** | **Native** — owner→0; history persists **[src]** | Composed — registry delist / key removal **[recalled]** |
| **issueCredential** | Composed — signed ID Token (JWS) **[src §2]** | **Native** — signed `<Assertion>` **[src §2.3.3]** | **Native** — CA issues signed cert **[src §4.1]** | Native — QTSP (Q)EAA issuance **[recalled; VC §4.7 src]** | **Native** — MSO-signed mdoc **[sec]** | **Native** — pseudonym cert bulk issuance **[src]** | Composed — off-chain VC; on-chain key/status anchor **[src §4.7]** | Native — claim issuer `addClaim` **[recalled]** |
| **verifyCredential** | Composed — validate sig+iss+aud+exp **[src §3.1.3.7]** | Composed — sig + SubjectConfirmation check **[src §2.4.1.1]** | Composed — path validation + OCSP **[src OCSP §2.2]** | Composed — verify issuer sig + status **[recalled; 800-63C src]** | Composed — reader checks MSO sig, offline **[sec §9]** | Composed — offline in-message cert verify **[sec]** | Composed — off-chain proof + on-chain status read (V6) **[src]** | Composed — on-chain claim check at transfer **[recalled]** |
| **revokeCredential** | Composed — token revocation (RFC 7009) **[recalled]** | Composed — short validity window (`NotOnOrAfter`) **[recalled]** | **Native** — CRL / OCSP revoked **[src §5; OCSP §2.2]** | Composed — status-list revocation **[src Bitstring §2]** | Composed — issuer status list **[sec]** | **Native** — linkage-value CRL revokes all pseudonyms **[src]** | Composed — on-chain status write (V5) **[src]** | Composed — remove claim / revoke issuer **[recalled]** |
| **createPresentation** | n-a — token presentation to RS, no VP **[src §1.4]** | Composed — bearer / holder-of-key assertion to SP **[src §2.4.1.1]** | n-a — cert in TLS handshake, no holder VP **[recalled]** | Native — wallet selective-disclosure VP **[recalled; VC §4.13 src]** | **Native** — mdoc selective disclosure **[sec §8.2]** | Absent — cert travels in every message **[sec]** | Composed — on-chain replay-protected anchor (P1) **[src; no native ERC]** | n-a — claims read on-chain, no presentation step **[recalled]** |
| **IDTx (concept)** | Absent on-chain — off-chain RP decision **[src; ABAC SP 800-162 §3.2]** | Absent on-chain — off-chain SP decision **[recalled]** | Absent on-chain — off-chain RP decision on OCSP **[src]** | Absent on-chain — off-chain RP admission **[recalled]** | Absent on-chain — off-chain verifier decision **[sec]** | Absent on-chain — off-chain receiver decision, *k*−1 staleness **[sec]** | **Native** — in-contract guard on named identity **[src]** | **Native** — transfer gated on identity claims **[src §6.8.4]** |

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
- **IDTx row is the contribution boundary.** Only S7 and S8 can evaluate an identity dependency *inside a transaction*;
  S1–S6 all make an off-chain **identity-dependent decision** (`ANALYSIS.md` §4.1), which shares the freshness
  dimension but is not a transaction. S8 is the closest prior art; the thesis's claim over it is the
  **storage-locus × encoding × evaluation-point taxonomy** and the **on-chain freshness/ordering analysis**, not the
  guard mechanism (THESIS_DRAFT §6.8.4).

---

## §3 — Trade-off matrix and axis-level analysis (WP 2.3)

Eight axes, one row per system. Cells are compressed; the prose below states the genuine tradeoffs.

| Axis | S1 OIDC | S2 SAML | S3 X.509 PKI | S4 eIDAS/EUDI | S5 mDL | S6 V2X/SCMS | S7 SSI (DID+VC) | S8 ERC-3643 |
|---|---|---|---|---|---|---|---|---|
| **Trust locus** (root of trust) | OpenID Provider **[src]** | SAML IdP/authority **[src]** | CA chain to root **[src]** | Member-state QTSP + EU trust list **[src]** | Issuing authority (IACA) **[sec]** | SCMS root + pseudonym CA **[src]** | Controlling key + ledger consensus **[src]** | Compliance contract + claim issuers **[recalled]** |
| **Availability dependence** (auth needs it live?) | **IdP must be live** **[src §5.3]** | IdP must be live for SSO **[recalled]** | OCSP responder live (CRL cacheable) **[src]** | Issuer for issuance; presentation offline **[recalled]** | **Fully offline** at presentation **[sec]** | **Fully offline** at receive **[sec]** | Ledger node / RPC for reads **[src]** | Ledger live for every transfer **[recalled]** |
| **Revocation / freshness latency** | token TTL; revoke via RFC 7009 **[recalled]** | assertion `NotOnOrAfter` window **[recalled]** | CRL period / OCSP real-time **[src]** | status-list refresh interval **[src]** | status list; stale if offline **[sec]** | CRL distribution; cached ⇒ *k*−1 msgs **[sec]** | on-chain write ⇒ next-block, public **[src]** | on-chain claim ⇒ next-block **[recalled]** |
| **Privacy & linkability** | IdP sees every login (NASCAR problem) **[recalled]** | IdP sees every SSO **[recalled]** | cert is public, linkable **[src]** | selective disclosure, unlinkability goal **[recalled]** | **selective disclosure** per presentation **[sec]** | **pseudonym rotation**, unlinkable by design **[src]** | public ledger, **inherently linkable** **[src]** | public ledger + claims, linkable **[recalled]** |
| **Cost model** | infra / per-IdP, no per-op fee **[recalled]** | infra, no per-op fee **[recalled]** | CA fee per cert; OCSP infra **[recalled]** | national infra; wallet free to holder **[recalled]** | provisioning infra **[sec]** | SCMS infra; bulk pseudonyms **[sec]** | **gas per write**; reads growth-priced **[src #31/#49]** | **gas per transfer** (compliance check) **[recalled]** |
| **Governance** (who changes the rules) | OpenID Foundation + each OP **[recalled]** | OASIS + each deployment **[recalled]** | CA/Browser Forum + root programs **[recalled]** | EU law + member states **[src]** | ISO + issuing authorities **[sec]** | IEEE/ETSI + SCMS manager **[sec]** | W3C/EIP + chain governance **[src]** | token issuer + ERC authors **[recalled]** |
| **Offline operation** | No — needs IdP **[src]** | No — needs IdP **[recalled]** | Partial — cached CRL **[src]** | Yes at presentation **[recalled]** | **Yes — designed offline** **[sec]** | **Yes — designed offline** **[sec]** | No — needs ledger read **[src]** | No — needs ledger **[recalled]** |
| **Recovery / key rotation** | IdP account recovery **[recalled]** | IdP-side reset **[recalled]** | CA rekey / re-issue **[src]** | wallet rebinding ceremony **[src]** | issuer re-provision **[sec]** | SCMS re-enrollment **[sec]** | self-signed `changeOwner`; **lost key = lost identity** **[src]** | ERC-734 key management contract **[recalled]** |

### The genuine axis-level tradeoffs

**T1 — The ledger trades a live-authority dependency for a public, ordered, costly write (the headline).**
Across S1–S4, *verifying* an identity's current status needs a live authority at decision time: OIDC queries the
UserInfo endpoint [src §5.3], X.509 the OCSP responder [src §2.2], eIDAS a status list. S7/S8 remove that dependency —
status (V6) is read directly from ledger state, so there is no responder to be down and no CA to trust at the moment of
decision. The cost is exact and three-fold, and it is the Phase-1 finding (`THESIS_DRAFT` §6.8.3, `ANALYSIS.md` §5):
the revocation that OCSP serves as a *private, cacheable pull* becomes an **on-chain write** that is (a) **public** —
every revocation is visible and linkable, losing the Bitstring Status List's query-privacy; (b) **ordered** — it takes
a block position, which opens the **mempool ordering race** between a dependency's change and the dependent transaction
that a later re-check (`fulfil`) closes *inside execution* but not in the mempool (AR-10); and (c) **costly** — gas per
write (#49) and reads priced in history growth (#31). S1–S4 have none of these three because their "write" is a private
update to an authority's own store.

**T2 — Offline operation and on-chain freshness are mutually exclusive, and the CAV domain sits on the wrong side for S7.**
S5 (mDL) and S6 (V2X) are *designed offline*: a receiver verifies an mdoc or a 1609.2 message with no network call,
which is non-negotiable for a vehicle verifying a safety message at line rate [sec]. The price is staleness: a cached
V2X verifier accepts at most **k−1 messages after a revocation** (`ANALYSIS.md` §3, #32/#37, pre-D51-fix and
provisional). S7's on-chain read gives *next-block* freshness but **requires the ledger live** — it cannot make the
offline, line-rate decision V2X needs. This is the sharpest cross-domain tension for a thesis sited in CAV: the
substrate that best solves freshness is the one least able to operate in the vehicle's offline reality. The thesis's
honest position (THESIS_DRAFT §6.8) is that the on-chain IDTx governs *transactions* (tolls, claim anchoring,
ownership transfer), not the safety-message path, where the off-chain identity-dependent *decision* with its k−1 bound
remains the right tool.

**T3 — Privacy is bought three different ways, and the ledger forecloses all three.**
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

---

## §4 — Where the thesis's on-chain SSI sits (honest placement)

**What S7 (and the IDTx over it) genuinely wins.** On the function matrix S7 is the **only system with `createDID`,
`resolve`, `rotate`, `delegate`, and `execute` all Native** (§2), because the identifier *is* a key and the registry is
contract-readable — no authority mediates creation, rotation, or delegation, and the identity can itself act
(`execute`). On the trade-off matrix it uniquely removes the **live-authority dependency** at decision time (T1): a
revocation is reflected at the next block with no responder to query, which is the freshness property the IDTx is built
to exploit. Against the closest prior art, S8/ERC-3643, the thesis does not claim the guard mechanism — it claims the
**storage-locus × encoding × evaluation-point taxonomy** and the **on-chain freshness/ordering analysis** (THESIS_DRAFT
§6.8.4): object-attribute ABAC (NIST SP 800-162 §3.2 [src]) realized on a public ledger, with the dimension ABAC's PDP
model never needed — *where* the depended-on state lives and *when* it is read.

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
freshness and no live authority (its home: tolls, claim anchoring, ownership transfer). It is the *wrong* substrate for
the offline, line-rate, privacy-by-pseudonymity path that V2X (S6) occupies — and the thesis says so. The honest
summary: the IDTx buys freshness and authority-independence by paying in publicity, cost, an unresolved ordering race,
and (on the two measured paths) an open replay exposure.

---

## Closing ledger — cells still `[recalled]` or `[sec]` (unverified at primary this pass)

**Count of function×system cells (§2) not at `[src]`: 52 of 96** — comprising **[sec]** cells blocked by paywalls and
**[recalled]** cells not reachable/not chased this pass. Upgraded to `[src]` this pass from `ANALOGIES.md`'s open cells:
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
- **ERC-3643 / ONCHAINID (S8):** createDID (deploy), resolve, rotate (ERC-734), delegate, attribute (ERC-735 addClaim),
  execute (ERC-725X), deactivate, issue, verify, revoke, createPresentation — the whole S8 column except the IDTx
  headline, which THESIS_DRAFT §6.8.4 already established as read prior art [src]. The EIPs (ERC-3643, ERC-734/735/725)
  are free and should be read to upgrade this column.
- **eIDAS/EUDI (S4):** (Q)EAA/PID exact article references, ARF mdoc/SD-JWT-VC format mandates, resolve, attribute,
  issue, verify, createPresentation — rest on the ARF/Reg-2024/1183 [src] umbrella and the Sokolov 2026 secondary; chase
  the ARF primary if the examiner presses (carried open from Phase 1).
- **SAML 2.0 (S2):** rotate, delegate (delegation restriction), deactivate, revoke, IDTx — not covered by the four
  Core sections read this pass.
- **OIDC (S1):** rotate (`n-a`), revoke (RFC 7009 not re-read).
- **X.509 (S3):** resolve (§6 path-validation section number), delegate (proxy-cert RFC 3820), createPresentation
  (`n-a`).

All five Phase-1 open items named in `THESIS_DRAFT.md` "Open items" (OIDC, SAML, OCSP, LDAP/SCIM) are now read **except**
the MOBI VID external spec (not in this comparison set) and the ERC-3643/eIDAS primaries above.
