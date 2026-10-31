# Phase-2 comparison figures — data tables (P2-1, P2-2)

**Generated** by `docs/idtx_core/figures/make_p2_figures.py`; do not edit. Each table is the data behind one Phase-2 figure in this directory (the table view of the SVG). The script is Python-stdlib only (no matplotlib) and emits deterministic SVG. **Author:** Nikhil Prakash (MASc, UBC ECE).

**Source / run.** Transcribed from `docs/idtx_core/p2/COMPARISON.md` as of its stated *Produced: 2026-10-31* revision (§2 function x system matrix, §3 trade-off matrix). `COMPARISON.md` is being edited concurrently by another pass; if its matrices change, re-run this script and the tables below regenerate. This file is kept **separate from `FIGURES.md`** on purpose so the Phase-1 `make_idtx_figures.py --check` (which byte-compares `FIGURES.md`) stays green.

**Matrix coverage note.** `COMPARISON.md` §2 as read has **11 explicit function rows + the IDTx concept row**, not "12 functions + IDTx": it collapses `attribute (set / revoke)` into a single row, and gives the relayed / sponsored meta-transaction **no row of its own** (its §2 prose marks it `n-a`/`Absent` everywhere except S7/S8, where it is a gas-sponsorship `Composed` over `execute`). P2-1 therefore shows 12 rows and omits the meta-tx row rather than invent its eight cells.

## P2-1 Function x system heat map (`p2_1_function_system_heatmap.svg`)
Cell class: **Native** (built-in primitive) / **Composed** (built from named primitives) / **Absent** (paradigm lacks it) / **n-a** (does not apply). Source: COMPARISON.md §2.

| Function | S1 OAuth2/OIDC | S2 SAML2.0 | S3 X.509PKI | S4 eIDAS/EUDI | S5 ISO mDL18013-5 | S6 V2X PKI/SCMS | S7 SSI(thesis) | S8 ERC-3643ONCHAINID | S9 FIDO2/WebAuthn | S10 did:key/did:web |
|---|---|---|---|---|---|---|---|---|---|---|
| createDID | n-a — IdP provisions sub | n-a — IdP-managed NameID | Composed — CA issues cert (CSR+sig) | Composed — PID issued to wallet | Composed — authority provisions mdoc | Composed — SCMS enrollment cert | Native — key-is-DID; VIN L3 commit | Composed — deploy ONCHAINID contract | Native — self-gen key pair, no issuer | Native — key-is-DID/host did.json, no ledger |
| resolve | Native — UserInfo, live IdP | Composed — IdP metadata + query | Composed — chain build, AIA fetch | n-a — holder presents, no lookup | Composed — device engagement | Composed — in-message validation | Native — event-sourced replay | Native — on-chain claim/key reads | Composed — RP cred-ID->pubkey lookup | Native — did:key expand / did:web GET |
| rotate (changeOwner) | n-a — IdP reset, no ctrl key | n-a — IdP-side, no holder key | Composed — CA rekey / re-issue | Composed — wallet rebinding | Composed — issuer re-provisions | Composed — SCMS re-enrollment | Native — self-signed changeOwner | Composed — ERC-734 key mgmt | n-a — re-register, no in-place rot | Composed — did:web re-publish; key immut |
| delegate | Composed — OAuth access token | Composed — delegated assertion | Composed — subordinate / proxy cert | Composed — consent to RP, no key | n-a — pseudonyms self-held | n-a — pseudonyms self-held | Native — addDelegate, on-chain TTL | Composed — ERC-734 scoped keys | n-a — scoped to one RP, no deleg | Composed — DID-doc capabilityDelegation |
| attribute (set/revoke) | Composed — IdP claims; SCIM PATCH | Composed — AttributeStatement | Composed — subject DN / extensions | Composed — (Q)EAA attestation | Composed — issuer-signed elements | Composed — PSID/SSP in cert | Native — setAttribute; no read (AR-1) | Native — ERC-735 addClaim, readable | n-a — authenticator, not attr sys | Composed — self-asserted DID-doc entries |
| execute (agent proxy) | n-a — authenticate only | n-a — SSO only | n-a — keys sign, don't act | n-a — presented, not executor | n-a — presented only | n-a — signs messages only | Native — ERC-4337/725x execute | Composed — ERC-725X execute call | n-a — authenticate only, no exec | n-a — no exec substrate (not chain) |
| deactivate | Composed — SCIM DELETE/active:false | Composed — IdP disables principal | Composed — CRL/OCSP revoke at EOL | Composed — wallet revocation | Composed — issuer revokes mdoc | Composed — SCMS CRL revocation | Native — owner->0; history stays | Composed — registry delist (deleteId) | Composed — RP deletes stored cred | Composed — did:web empty json; key n-a |
| issueCredential | Composed — signed ID Token (JWS) | Native — signed <Assertion> | Native — CA issues signed cert | Native — QTSP (Q)EAA issuance | Native — MSO-signed mdoc | Native — pseudonym bulk issuance | Composed — off-chain VC; anchor | Native — claim issuer addClaim | n-a — proves key, no 3rd-party cred | Native — VC issuer signs off-ledger |
| verifyCredential | Composed — sig+iss+aud+exp | Composed — sig + SubjectConfirm | Composed — path valid. + OCSP | Composed — issuer sig + status | Composed — reader MSO sig, offline | Composed — offline in-message | Composed — proof + status read (V6) | Composed — on-chain claim at transfer | Composed — auth-ceremony sig check | Composed — VC proof + resolve iss, no ledger |
| revokeCredential | Composed — token revoke (RFC 7009) | Composed — short validity window | Native — CRL / OCSP revoked | Composed — status-list revocation | Composed — issuer status list | Native — linkage-value CRL (all) | Composed — on-chain status write (V5) | Composed — remove claim / revoke iss | n-a — no cred; RP removes reg | Composed — status-list (Bitstring) off-ledger |
| createPresentation | n-a — token to RS, no VP | Composed — bearer/HoK assertion | n-a — cert in TLS, no VP | Native — wallet SD presentation | Native — mdoc selective disclosure | Absent — cert in every message | Composed — replay-protected anchor (P1) | n-a — claims read, no present | n-a — assertion to RP, no VP | Native — VC DM 2.0 VP, holder-assembled |
| IDTx (concept) | Absent — off-chain RP (ABAC) | Absent — off-chain SP decision | Absent — off-chain RP on OCSP | Absent — off-chain RP admission | Absent — off-chain verifier | Absent — off-chain recv, k-1 stale | Native — in-contract guard, named id | Native — transfer gated on claims | n-a — auth/off-chain, no tx | n-a — DID+VC but no ledger (tests T1) |

Row-total reading (COMPARISON.md §2 notes): `createDID` is `Native` with no issuer on S7 **and** on S9 (FIDO2 self-generated key) and S10 (did:key/did:web, no ledger) — the self-created key-identity is **not** S7-unique (obj. F2). `createPresentation` has no native ERC (S7 `Composed` anchor, P1; S4/S5/S10 have it `Native`). The `IDTx` row is the contribution boundary — only S7/S8 are `Native`; S1–S6 are `Absent` on-chain (off-chain **identity-dependent decision**, ANALYSIS.md §4.1) and S9/S10 are `n-a` (authentication / no ledger — no transaction; S10 is the T1 control: full DID+VC surface yet no in-transaction evaluation).

## P2-2 Trade-off profile (`p2_2_tradeoff_profile.svg`)
Six **ordinal** axes (level 0/1/2 shown by position on a Low/Med/High track) and two **nominal** axes (trust locus, governance; text, not ranked). Source: COMPARISON.md §3 cells + the T1–T4 tradeoff prose.

Ordinal level words per axis (favourable end in **bold**):
- **Availability** (live-authority need (low=better)): Low = **offline**, Med = cacheable, High = must be live
- **Revocation** (freshness latency (low=better)): Low = **next-block**, Med = window, High = cache-stale
- **Privacy** (unlinkability (high=better)): Low = linkable, Med = mixed, High = **unlinkable**
- **Cost** (per-op cost (low=better)): Low = **no per-op**, Med = per-cert/infra, High = gas per op
- **Offline** (works offline (yes=better)): Low = No, Med = Partial, High = **Yes**
- **Recovery** (key recovery (easy=better)): Low = lost=lost, Med = ceremony, High = **easy**

| System | Availability | Revocation | Privacy | Cost | Offline | Recovery | Trust locus | Governance |
|---|---|---|---|---|---|---|---|---|
| S1 OAuth2/OIDC | must be live | window | linkable | no per-op | No | easy | OpenID Provider | OpenID Foundation + each OP |
| S2 SAML 2.0 | must be live | window | linkable | no per-op | No | easy | SAML IdP / authority | OASIS + each deployment |
| S3 X.509 PKI | cacheable | window | linkable | per-cert/infra | Partial | easy | CA chain to root | CA/Browser Forum + roots |
| S4 eIDAS/EUDI | offline | window | unlinkable | no per-op | Yes | ceremony | QTSP + EU trust list | EU law + member states |
| S5 ISO mDL | offline | cache-stale | unlinkable | no per-op | Yes | easy | Issuing authority (IACA) | ISO + issuing authorities |
| S6 V2X/SCMS | offline | cache-stale | unlinkable | per-cert/infra | Yes | easy | SCMS root + pseudonym CA | IEEE/ETSI + SCMS manager |
| S7 SSI (thesis) | must be live | next-block | linkable | gas per op | No | lost=lost | Controlling key + ledger | W3C/EIP + chain governance |
| S8 ERC-3643 | must be live | next-block | linkable | gas per op | No | ceremony | Compliance contract + iss. | token issuer + ERC authors |
| S9 FIDO2 | must be live | window | unlinkable | no per-op | No | easy | Holder key; RP stores pubkey (no authority) | W3C + FIDO Alliance |
| S10 ledgerless SSI | cacheable | window | mixed | no per-op | Partial | ceremony | Controlling key; did:web adds DNS/host trust | W3C + DNS/registrar (did:web) |

**Judged / ambiguous cells (so none is presented as a verbatim datum).** §3 gives compressed phrases, not level labels; the following ordinal placements are the figure author's reading and an examiner may reasonably differ:
- **Cost** is coded as *marginal per-operation* cost. S1/S2/S4/S5 are `no per-op` (Low) even though they carry real **capital / national-infrastructure** cost that this axis does not show; S3 = `per-cert fee`, S6 = `SCMS infra` (both Med); S7/S8 = `gas per op` (High). A capital-cost reading would rank S4/S6 higher.
- **Availability** for S4 (eIDAS) is coded Low because §3 says *presentation is offline*; **issuance** still needs the issuer live, which this single level does not capture.
- **Revocation** S1/S2/S3/S4 are all coded Med (`window`): token TTL (S1), `NotOnOrAfter` (S2), CRL period / OCSP real-time (S3 — OCSP alone would be Low), status-list interval (S4). S3's dual CRL+OCSP nature is flattened to one level.
- **Recovery** S8 coded Med (`ERC-734 key-management contract` enables recovery) vs S7 Low (`lost key = lost identity`); §3 states the S7 end sharply but leaves S8's recovery qualitative.
- **Privacy** Med is now used only for **S10** (did:key is per-use unlinkable but did:web is a fixed correlator — a split the single level flattens to Med). The other nine systems land at Low (linkable) or High (unlinkable).
- **S9 (FIDO2) Availability** coded High (`must be live`): §3 says *RP live at auth* — but it is the RP itself, **not a third-party authority** (FIDO2 has none), so the live-authority reading is softer than the S1/S2 High.
- **S9 (FIDO2) Revocation** coded Med (`window`): §3 says *RP deletes credential; no global revocation list* — there is no cross-RP revocation latency to place on the next-block/window/cache-stale track, so Med is a qualitative placeholder, not a measured latency.
- **S10 (ledgerless SSI) splits did:key vs did:web on four axes**, each flattened to the Med level the single track allows: **Availability** (did:key none / did:web HTTPS host live), **Offline** (did:key Yes-deterministic / did:web No), **Recovery** (did:web re-publish / did:key lost-key-lost), and **Privacy** (above). An examiner may reasonably read either end.

**Cells carrying lower evidence in COMPARISON.md itself (not re-judged here, carried as-is).** Per its closing ledger, §2 marks **35 of 120** function×system cells as not-`[src]` (WP 3.5 upgraded 7 S5/S6 cells — resolve/verify/present/revoke — via free AAMVA mDL v1.6 + RFC 9901/SD-JWT-VC + Brecht SCMS) — `[sec]` (paywalled wire-format/clause detail only: S5 mDL encoding, S6 V2X SPDU format) or `[recalled]` (free primaries not yet chased: `rotate`/`delegate` of S8 ERC-3643, parts of S4 eIDAS, and 7 of the 24 new S9/S10 cells — S9 `rotate`/`deactivate`/`revokeCredential` and S10 `delegate`/`execute`/`deactivate`/`revokeCredential`). These figures reproduce COMPARISON.md's classification verbatim; they do not upgrade or down-rank an evidence tag. Treat S5, the noted S8 cells, and those S9/S10 cells as `[sec]`/`[recalled]` pending the primary read noted in COMPARISON.md's closing ledger.
