CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**Scenarios Beyond CAVs: Back-End Registries and Legacy System Integration**

**Showing that the identity substrate built for vehicles (IMinimalSSI, endorsement governance, off-chain credentials with on-chain anchors) serves driver's licences, property deeds and repair history, for human, vehicle and AI-agent principals, without displacing the register of record**

Document 8 of 16 · Hybrid Data Architecture (HDA) Campaign · Primary deliverable · Suite v1.0 · September 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 00 Master Plan · 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 10 VID Build Documentation · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: Type A prose / Type B tables-data → Chapter 5, §5.2 (generalisation beyond CAVs) and Chapter 4, §4.4 (real-world concerns)*

> **Post-build note (2026-10-04).** This document was drafted before the VID layer was executed. Scenarios S7 and S8 have since run and produced traces; where the text below says that only the S1 trace is measured, or labels S7/S8 quantities as pending, read it together with document 10 §5 (measured gas for F1–F12, G0–G4, T1–T2; the 11:1 Merkle-batch result; findings F-VID-1 to F-VID-7) and the reconciliation table in S3 §3. Canonical scenario identifiers are fixed in document 00 §6; where this document uses a different S-number for a proposed script, the register in 00 governs.

---

## 0. Scope and claim

This document makes one claim and tests it three times. The claim is that the identity system specified by the thesis (the twelve-function IMinimalSSI interface, the governance extension of registerIssuer/endorseIssuer, and the placement rule "content off-chain, anchor on-chain" argued in 01 and synthesised in 03) is not a vehicle-specific design that happens to generalise, but a *registry-agnostic* design whose vehicle instantiation (MOBI Vehicle Identity, VID [27]) is only the first. The three tests are the three back-end registries the campaign brief names: the driver's licence, the property deed or title, and the repair and maintenance history. Each is run twice, once with a human or vehicle principal adjacent to the connected and autonomous vehicle (CAV) setting, and once with an artificial-intelligence (AI) agent as the principal, following the identity-to-identity (I2I) generalisation of Chapter 5.

The document also answers the question the thesis's Chapter 4 §4.4 ("real-world concerns") owes: how does any of this coexist with the systems that actually hold these records today, the Department of Motor Vehicles (DMV) database, the land registry, the dealer management system (DMS), the insurer's claims system? The answer developed in §5 is an adapter pattern in which the legacy system remains the register of record, signs and anchors, and never places personally identifiable information (PII) on-chain.

Two rules from the campaign brief govern everything below. Nothing in this document is a measurement; the only measured figures in the campaign are the eight gas values of the S1 trace summarised in the brief §5, and they are cited here only where a function of the same signature is invoked. Second, the interface is normative: every scenario below is expressed in F1–F12, Set C (C1–C4) and the governance extension (G1 registerIssuer, G2 endorseIssuer, G3 revokeEndorsement, G4 isEndorsed), and no scenario asks for a new function on IMinimalSSI. Where a registry needs something new, it is a new *credential type*, never a new interface method; §8 shows that this is exactly what makes the deed demonstration cheap.

## 1. The back-end problem: registries of record today

### 1.1 What a register of record is

A register of record is a database whose contents are, by statute or contract, the legally authoritative statement of some fact: that person P holds a class-5 licence until date D; that parcel L is owned by P subject to lien N; that vehicle V was serviced at odometer reading O on date D by centre S. The register has three properties that any replacement or supplement must respect. It is *authoritative*: a court asks the registrar, not the citizen's wallet. It is *correctable*: registrars fix clerical errors, rectify fraud, and give effect to court orders, and they do so by editing the record, not by appending a contradiction. And it is *bounded in disclosure*: the registrar decides who may read what, under privacy law and under the registry's own access rules.

The technical shapes these registers take today are three, often layered: an authoritative relational database behind an application (the DMV system, the land titles system, the DMS); a paper or card artefact issued from the database and carried by the holder (the plastic licence, the certificate of title, the stamped service book); and, increasingly, a public-key infrastructure (PKI) that signs digital extracts (a signed PDF title search, an mDL issued under ISO/IEC 18013-5 [NEW-3], a signed inspection certificate).

### 1.2 What these registers cannot do

The claim of this section is that the four capabilities the campaign is built around are exactly the four these registers lack, and that the lack is structural rather than incidental.

*Portable proof.* A holder cannot carry a proof that a relying party in another system can check without calling the registrar. The card is proof only to a human who trusts the card's physical security features; the signed PDF is proof only to a party that has the registrar's certificate and a reason to trust it. In the World Wide Web Consortium (W3C) Verifiable Credentials (VC) model [9], [10], the holder carries an issuer-signed credential and the verifier checks the signature against a resolvable issuer identifier; the resolvable identifier is the decentralised identifier (DID) [8], and the resolution is F2. Legacy registers have no F2: the issuer's key is distributed out of band or not at all.

*Selective disclosure.* The plastic licence discloses everything on its face to everyone who looks at it. A car-share kiosk that needs only "class B, valid today" learns the holder's name, address, date of birth and licence number. Selective disclosure (02 treats the mechanisms; the repository's VC layer already implements SD-JWT-style salted claim digests [14]) is not a feature a register can add without changing what it issues, because the artefact it issues is monolithic.

*Cross-jurisdiction verification.* A verifier in jurisdiction B receiving a licence from jurisdiction A must either trust the physical artefact or have a bilateral integration with A's registrar. Mutual recognition treaties exist at the legal level, but they have no technical substrate: there is no chain of signatures from a root B already trusts down to A's issuing office. The endorsement pattern (G2, G4) is precisely that substrate, and §2.6 argues it in detail.

*Tamper-evident history.* A register's history is whatever the register says it is. Audit logs exist, but they are held by the same party whose actions they audit. The Building Paths preface's third framework property, the forensic audit trail as an accountability primitive (brief §2), is exactly the missing piece: not that a chain prevents a registrar from altering a record, but that it makes the alteration permanently visible, because the anchored hash no longer matches.

### 1.3 What must not change: authority stays with the registrar

Here the argument must be made carefully, because the naive blockchain proposal ("put the land registry on-chain") fails for reasons that are legal before they are technical, and a thesis that generalises identity to back-end registries without confronting them would be vulnerable at examination.

The chain in this design is *an anchor and a verification substrate, not the register of record*. Three arguments support this and none of them is a concession.

First, the *correctability* argument. Registers must be correctable; chains are append-only. A design that made the chain authoritative would have to model every correction as a new transaction that a court is then asked to treat as overriding an earlier one. That is exactly the append-only semantics of F7 (revokeCredential, irreversible) followed by F5 (issueCredential): the *credential* is corrected by revoke-and-reissue, but the *authority* to decide that a correction is warranted stays with the registrar, who is the only DID endorsed (G2) to issue that type. The chain records that the registrar changed its mind and when; it does not decide whether the registrar was right.

Second, the *privacy* argument. A register of record contains PII by definition. The placement rule of 01 (content off-chain; only the hash, validity, revocation state and presentation commitment on-chain) is what makes it possible for a public or consortium chain to participate at all. The register's contents never leave the registrar's control; what the chain holds is a commitment that lets anyone verify a document the registrar or holder chooses to show them.

Third, the *institutional* argument. Registrars will not adopt, and legislatures will not authorise, a system that removes their authority. A system that leaves their authority intact and adds portable proof, selective disclosure, cross-jurisdiction verification and tamper evidence is a system they can adopt incrementally (§5.4 shows that migration needs no per-record chain cost). This is the same "extension, not replacement" stance the thesis takes toward the Security Credential Management System (SCMS) [6], [28] in Chapter 1, applied to civil registries instead of vehicular PKI.

### 1.4 The GDPR hash nuance and the eIDAS 2.0 direction

The privacy argument has a subtlety the brief flags (§2, Building Paths property two) and which this document must not paper over. A hash of a credential's content is a commitment to that content. If the content is a driver's licence for a named person, and the hash is on a public chain, then anyone who later obtains the credential can prove that this exact licence was anchored at block *b*. Under the General Data Protection Regulation (GDPR) [NEW-4], data that can be linked to an identifiable natural person by anyone holding additional information is personal data (Recital 26's "means reasonably likely to be used"), and personal data on an append-only public ledger collides with the right to erasure (Article 17). The thesis's framework property therefore distinguishes: *per-credential content hashes may themselves be personal data*, whereas *credential-definition hashes and revocation accumulators are safely public* because they commit to schemas and to set membership, not to any one person's attributes.

The design response, which 01 and 02 develop and which this document applies to registries, is threefold. The anchored hash is computed over a *salted* canonical form (the repository's VC layer already salts claim digests in the SD-JWT style [14]), so that possession of the plaintext attributes without the salt does not reproduce the hash; erasure is then effected by revoking on-chain (F7) and deleting the salted credential object and its salt off-chain, after which the residual on-chain hash is a random-looking 32-byte value with no reasonably likely means of linkage. Second, where a registry's regulator judges that even a salted hash is too much, the credential is anchored *only through a batch Merkle root* (§5.4) whose leaves are never individually published, so that the on-chain datum commits to a set and not to a person. Third, revocation state is expressed as a status-list position or accumulator membership (Bitstring Status List [NEW-5]; the accumulator alternative in 02) rather than as a per-person flag, following the supervisor memo's revocation-models stance.

This is also the direction of the European Union's eIDAS 2.0 regulation and the European Digital Identity (EUDI) wallet architecture reference framework [NEW-1], [NEW-2] (both DIGEST-LEVEL; the author has read the regulation's summary and the ARF's public overview, not the full texts at source). The EUDI model is holder-held attestations issued by qualified or registered issuers, presented with selective disclosure, against issuer trust lists maintained by member states; the registries remain the authoritative source and no personal data is placed on any ledger. The HDA design is compatible with that direction and adds what the ARF leaves open: a tamper-evident, cross-border-verifiable *substrate* for the trust lists (the endorsement registry) and for issuance and revocation ordering (the anchors). The mobile driver's licence standard ISO/IEC 18013-5 [NEW-3] plays the same role for licences specifically: it fixes the data model and the device-to-reader presentation, and says nothing about where issuer trust is rooted. §2 treats the licence credential as compatible with the mDL data element namespace, with the DID and endorsement chain supplying the trust root.

## 2. Driver's licence

### 2.1 Actors and objects

The scenario has five DIDs and a sixth in the agent variant. The *ministry* (transport ministry or provincial equivalent) is the root endorser; its DID is the trust anchor foreign verifiers configure. The *DMV* is the issuer, endorsed by the ministry for the credential type `DRIVER_LICENCE`. The *holder* is a natural person with a wallet. The three verifier classes are *police* (full disclosure, verinym), a *car-share operator* (predicate-only), and an *insurer* (attribute subset with a stable pairwise identifier). The objects are: the `DRIVER_LICENCE` credential (content off-chain, anchor on-chain); the endorsement (ministry → DMV, type-scoped, with validity); three presentations, one per verifier class; and, in the agent variant, a delegation (F11) and a derived `LICENSED_OPERATOR` credential.

The tier is Tier 3 (administrative) for issuance, renewal and suspension; the roadside police check and the car-share unlock are Tier 2 interactions in the 2020 framework's sense (gated access, [5]) and are served by the cached read path of 03 rather than by a synchronous chain call.

### 2.2 Issuance

The function sequence is the same as the vehicle registration issuance of 04, with the roles renamed, which is the point. The ministry and DMV create DIDs (F1). The ministry registers the DMV as an issuer (G1 `registerIssuer(dmvDid, ROLE_DMV)`) and endorses it for the licence type with a validity window (G2 `endorseIssuer(ministryDid, dmvDid, DRIVER_LICENCE, validUntil)`). The holder creates a DID (F1) or, more realistically for a citizen, has a wallet that creates one and registers a verification method (F9). The DMV, which continues to hold the authoritative licence record in its own database, builds the credential object of §2.3, canonicalises and salts it, hashes it, and anchors it: F5 `issueCredential(dmvDid, holderDid, credentialHash, expiry)`. The credential object, with the DMV's off-chain signature over it, goes to the holder's wallet over an authenticated channel (08 designs the channel); the DMV's database stores the credentialId returned by F5 next to the licence row.

On-chain: the DMV's DID document entries, the endorsement, the credential hash, the validity, the issuer and subject DIDs. Off-chain: the licence attributes, the photo, the address, the DMV signature, the salt. The only measured cost the campaign may cite for this sequence is the S1 issueCredential figure of 130,163 gas (brief §5, O1 on Hardhat local EVM); the G1 and G2 costs will be measured by the S7 trace when it exists and are not stated here.

### 2.3 The minimal licence credential object

The brief §7 fixes the content of `DRIVER_LICENCE` as holder DID, class, restrictions, expiry, with content off-chain and only the anchor on-chain. The object below is the W3C-shaped form the `lib/vid` builders are planned to produce; field names are chosen to be mappable onto the ISO/IEC 18013-5 mDL namespace so that a wallet that speaks mDL can present the same data.

```json
{
  "@context": ["https://www.w3.org/ns/credentials/v2"],
  "type": ["VerifiableCredential", "DriverLicenceCredential"],
  "issuer": "did:ethr:0x1:0xDMV...",
  "validFrom": "2026-09-03T00:00:00Z",
  "validUntil": "2031-09-03T00:00:00Z",
  "credentialSubject": {
    "id": "did:ethr:0x1:0xHOLDER...",
    "licenceClass": "5",
    "restrictions": ["corrective-lenses"],
    "jurisdiction": "CA-BC",
    "givenName": "…", "familyName": "…", "birthDate": "…",
    "portrait": "…"
  },
  "credentialStatus": { "type": "RegistryStatus", "credentialId": "0x…" },
  "credentialSchema": { "id": "urn:cvin:schema:DRIVER_LICENCE:v1", "hash": "0x…" },
  "proof": { "type": "DataIntegrityProof", "cryptosuite": "eip191-secp256k1", "…": "…" }
}
```

Two design decisions carry weight. `credentialStatus.credentialId` is the F5 return value, so that any verifier can call F6 without a status-list server; this is the "registry-based credentialStatus" the repository's VC layer already uses. And the claim digests are salted per claim, so that the holder can disclose `licenceClass` and `validUntil` to the car-share while withholding name and portrait, and the verifier can still check that the disclosed claims are the ones the DMV signed. Which claims are disclosed to whom is the subject of §2.4; the on-chain anchor is the same for every presentation.

### 2.4 Three presentations, three disclosure profiles

*Police, roadside.* The officer's device sends a challenge and domain; the holder's wallet produces a full-disclosure presentation. The wallet calls F8 `createPresentation(holderDid, [licenceCredentialId], challenge, "police.bc.ca")`, which verifies holder ownership and binds the challenge on-chain (replay prevention), then hands the officer the full credential plus the F8 presentationId. The officer's device verifies the DMV signature off-chain, checks F6 (valid, not revoked, not expired, issuer not deactivated), checks G4 `isEndorsed(dmvDid, DRIVER_LICENCE)` as of the issuance time, and confirms the presentationId's challenge matches. This is the *verinym* mode of the 2020 dual-identity model [5]: the holder's public DID, full attributes, for a legally privileged verifier. The clever part, and its assumption: the officer's device can do all of the verification from a cached copy of the chain state that is at most one revocation-propagation window old (03 defines the window; 06 treats the low-connectivity variant), so the roadside check needs no live chain access. What breaks it is a suspension issued inside that window; §2.5 addresses it.

*Car-share, kiosk.* The operator needs only "holds a licence of class ≥ B, valid today, issued by an issuer my policy endorses". The wallet produces a selective-disclosure presentation revealing `licenceClass`, `validUntil` and `jurisdiction` only, plus the salted digests of the undisclosed claims so the DMV signature still verifies. Whether the F8 commitment is written on-chain for a car-share unlock is a cost decision 03 takes per verifier class; the design allows an off-chain presentation (holder signature over challenge) with F8 reserved for presentations that must be auditable. In the 2020 model this is the *pseudonymous* mode: the holder can use a pairwise DID for the car-share relationship, with the DMV's credential bound to the holder's public DID and a ZK proof of control linking the two (02 treats the linkage proof; the AnonCreds link-secret pattern is the reference). With a plain SD-JWT-style presentation the car-share still learns the holder's public DID; with the ZK linkage it learns only a pairwise identifier. The document states this as a two-level design, not as a resolved choice, because the ZK path's cost is unmeasured.

*Insurer, underwriting.* The insurer needs class, restrictions, issuance date (as a proxy for experience) and a *stable* identifier so that it can correlate with claims history over time; the holder consents to a pairwise DID that is stable for that insurer only. The presentation discloses those attributes and is signed by the pairwise DID; the linkage from pairwise to public DID is by delegation (F11 `addDelegate(publicDid, sigAuth, pairwiseAddress, validity)`), so that the insurer can check F12 `validDelegate` to confirm the pairwise key is authorised by the credential's subject without learning any other pairwise identifier. This use of F11/F12 to implement the 2020 model's pairwise DIDs on top of a single anchored public DID is one of the reuses that 11 will argue is evidence of the interface's sufficiency.

### 2.5 Renewal, suspension, reinstatement

Renewal is F5 of a new credential followed by F7 of the old; the wallet keeps both until the old one's F6 reports revoked, at which point the old object is deleted (and, for erasure, its salt). Suspension is F7 alone: the DMV revokes, and every F6 thereafter reports `revoked = true`; the S1 trace measured F7 at 32,980 gas on O1 (brief §5). Reinstatement, because F7 is irreversible by specification, is reissue: a new F5 with the same content and a new salt, giving a new credentialId. This is not a limitation to apologise for; it is the correctability argument of §1.3 realised. The register of record shows one licence with a suspension period; the chain shows two credentials with a gap between them; the two views reconcile (§5.5) because the DMV's row stores both credentialIds.

The propagation problem is the real one. A suspension issued at time *t* is visible to a verifier with a live chain read at *t* plus block time; to a verifier reading a cache, at *t* plus the cache's invalidation interval. The supervisor memo's rule (cache invalidation synchronised with revocation state) becomes a per-verifier-class policy: police devices subscribe to `CredentialRevokedEvent` for the licence type and invalidate on receipt; car-share kiosks may accept a staleness window of hours because the harm of a stale acceptance is bounded and insurable. 08 treats propagation as a crux; 05 gives the tier-by-tier consequences.

### 2.6 Cross-jurisdiction recognition via endorsement chains

The claim is that endorsement chains give mutual recognition a technical substrate that requires no bilateral integration. A verifier in jurisdiction B configures one trust root per foreign jurisdiction it recognises: the ministry DID of A. When presented with a licence issued by A's DMV, it resolves the DMV DID (F2), checks F6, and then walks the endorsement: G4 `isEndorsed(dmvDid_A, DRIVER_LICENCE)` on A's endorsement registry, and confirms the endorser is the ministry DID it trusts. If A's structure is deeper (ministry endorses regional offices, offices issue), the walk is two steps; the verifier's policy states the maximum depth and the acceptable endorser roles, in the manner of the Trust over IP governance stack's trust-registry layer [NEW-6].

Where the two jurisdictions run different chains, the 2020 architecture's Local CVIN / ID Porting Protocol (IDPP) concept [5] is the mechanism: a Local CVIN for jurisdiction A holds A's endorsement registry; the Global CVIN holds the ministry roots and a pointer to each Local CVIN's registry contract. A foreign verifier reads the Global CVIN for the root and the Local CVIN for the endorsement. The honest statement of the assumption: this works when the verifier can read both chains (or a trusted relay of them). When it cannot, the fallback is the verifier accepting a *signed endorsement extract* from A's ministry carried in the presentation, verified against the ministry key resolved from the Global CVIN; that reduces the cross-chain dependency to a single root lookup at the cost of trusting the extract's freshness. The abridged endorsement-extract object is a candidate registry delta row (§10).

### 2.7 Agent variant: the licensed operator and the confused deputy

An *operator agent* is software that drives, dispatches, or otherwise exercises a privilege that the law grants to a licensed human. The principal is the human licence-holder; the agent must be able to prove, to a gate, a car-share, or a road authority, that it acts under a valid licence, with a scope no wider than the human intended and an expiry no later than the human's own licence.

The mechanism is delegation. The human's wallet calls F11 `addDelegate(holderDid, sigAuth, agentAddress, validity)` with `validity` no later than the licence's `validUntil`. The agent holds its own DID (F1) and, in Family D terms, may be registered in an agent registry (ERC-8004 [19]; Set C), but the *licensed-operator* status is not a credential the agent holds independently. It is a credential the human's wallet issues to the agent (F5 `issueCredential(holderDid, agentDid, hash(LICENSED_OPERATOR{scope, validUntil}), validUntil)`), whose content references the human's `DRIVER_LICENCE` credentialId and states a scope (`"vehicleClass": "B"`, `"geofence": "…"`, `"purposes": ["car-share-pickup"]`). A verifier presented with the agent's credential checks three things: F6 on the operator credential; F6 on the referenced human licence (so that suspension of the human suspends the agent transitively, without any action by the human); and F12 `validDelegate(holderDid, sigAuth, agentAddress)` (so that the human can cut the agent off instantly by letting the delegation lapse, or by F10 on a key, without revoking the credential).

The confused-deputy guard is the scope check, and it deserves stating precisely because it is the failure mode the I2I generalisation most needs to avoid. The confused deputy [NEW-7] is a program that holds authority for one purpose and is induced by a third party to exercise it for another. An agent holding a bare delegation from a licensed human is a confused deputy waiting to happen: any counterparty that can drive the agent's decision loop can cause it to exercise the human's licence. The guard is that the *authority is never the bare delegation*: it is the delegation *and* the scoped operator credential, and the verifier enforces the scope, not the agent. A car-share kiosk that receives a presentation of the operator credential for a purpose outside `purposes`, or a vehicle outside `vehicleClass`, rejects it regardless of what the agent believes it has been told. Enforcement lives with the verifier because the agent's judgement is exactly the thing under attack. The supervisor memo's signed execution traces (agents "leave signed execution traces") then make any attempted out-of-scope presentation attributable; F8's on-chain commitment is the trace.

What breaks it: a scope expressed in terms the verifier cannot evaluate (a geofence the kiosk cannot locate itself in), or a human who issues an over-broad scope out of convenience. The first is a schema-design problem for the `LICENSED_OPERATOR` type; the second is the same problem as over-broad OAuth scopes and is mitigated by wallets defaulting to narrow scopes and short expiries.

### 2.8 Failure modes

The failure modes are: DMV key compromise (mitigated by F9/F10 rotation and by G3 revokeEndorsement, after which credentials issued after the revocation time fail the endorsement check while earlier ones stand); a holder's wallet loss (recovery is a spec §6 extension and out of this document's scope; the interim answer is DMV reissue to a new DID, which the register of record supports because it, not the chain, is authoritative); presentation replay (prevented by F8's challenge binding for on-chain presentations and by verifier-side nonce tracking for off-chain ones); and a verifier's stale cache (§2.5).

## 3. Property deeds and titles

### 3.1 Actors and objects

The *land registry* is the issuer of the `PROPERTY_DEED` credential and is endorsed for that type by the *ministry* (the attorney-general or lands ministry, as the jurisdiction has it). The *owner* holds the deed credential. A *lender* is the issuer of a `LIEN` credential that references the deed. The verifier classes are a *purchaser* (or their conveyancer), a *lender* assessing security, and a *municipality* checking ownership for tax or permit purposes. In the agent variant the purchaser's conveyancer is an agent.

The tier is Tier 3 throughout. Nothing in conveyancing is latency-sensitive in the CAV sense; the design goal is instead correctness, ordering and non-repudiation.

### 3.2 The deed as an anchored credential

The claim is that a title register of the Torrens type [NEW-8] (in which the register itself, not the chain of historical deeds, is conclusive of ownership, as in British Columbia and most of Canada and Australia) maps cleanly onto revoke-and-reissue, and that the chain adds to it the two things a Torrens register lacks: independently verifiable ordering, and cross-registry verification.

The deed object's content is off-chain: parcel identifier, legal description, owner DID, tenure, registered charges, the registry's signature. On-chain: F5 anchor with `issuer = registryDid`, `subject = ownerDid`, `credentialHash`, `validUntil = 0` or a far-future sentinel for an indefinite estate (the interface takes a `uint256`; the type-registry schema states the convention). The registry remains the register of record; the credential is a portable extract of it, the way a certified copy of title is today, with the difference that the extract can be verified by anyone without calling the registry.

### 3.3 Transfer as revoke-and-reissue with an ordering proof

Transfer of parcel L from seller S to buyer B is: the registry revokes S's deed (F7, `credentialId_S`) and issues B's deed (F5, `subject = buyerDid`) whose content carries `previousCredentialId = credentialId_S` and `previousCredentialHash`. The *ordering proof* is the chain's own event log: `CredentialRevokedEvent(credentialId_S)` and `CredentialIssued(credentialId_B)` are in the same or consecutive blocks, and B's credential content commits to S's credentialId. A verifier can therefore establish, without trusting the registry's database, that B's deed was issued after S's was revoked, that B's deed claims descent from S's, and that no other unrevoked deed for the parcel was issued in between (by scanning `CredentialIssued` events with `issuer = registryDid` and a type-tagged subject; the type registry of brief §7 supplies the tag).

Atomicity is the honest gap. F7 and F5 are separate transactions on IMinimalSSI; a crash between them leaves the parcel with no unrevoked deed, which is a safe failure (nobody can prove ownership) but an inconvenient one. The spec §6 names batch operations as an extension; a registry adapter that wraps F7 + F5 in one transaction is such an extension and does not alter the interface. Until it is built, the adapter's issuance queue (§5.3) simply retries the F5 and the register of record, which is authoritative, shows the transfer as complete throughout.

### 3.4 Liens as credentials referencing the deed

A lien is a `LIEN` credential issued by the lender (endorsed by the registry, or by a financial regulator, for that type; jurisdictions differ and the endorsement structure encodes the difference) whose content includes `deedCredentialHash` and `deedCredentialId`. Discharge is F7 by the lender. A purchaser verifying title enumerates `CredentialIssued` events whose off-chain content references the deed hash, or, more practically, asks the registry's read API (§5.2) for the lien credentialIds it has recorded against the parcel, then checks F6 on each. On transfer, unrevoked liens are carried into the new deed's content as `registeredCharges`, so the ordering proof covers them.

The lien is where the placement rule's benefit is sharpest: a mortgage amount is sensitive commercial information, and it never touches the chain. What the chain shows is that some endorsed lender anchored something referencing this parcel's deed at block *b* and has not revoked it.

### 3.5 Why title stays off-chain and what the chain adds

Title stays off-chain for privacy (owner names, addresses, mortgage terms are PII and commercial data; §1.4), for legal reasons (the register is conclusive by statute and the chain is not, and a chain that was conclusive would have to be correctable, which it is not), and for practical ones (a title register holds decades of instruments; anchoring their existence is cheap, replicating their content is not).

The chain adds *ordering* (which of two competing instruments came first, established by block inclusion rather than by the registry's own timestamp), *non-repudiation* (the registry cannot later deny having issued a deed whose hash it anchored under its endorsed DID, nor a lender deny a lien), and *cross-registry verification* (a lender in another province, or an insurer, verifies a deed against the ministry root without an integration to the land titles system). It also adds a defence the register of record itself benefits from: an insider altering a row in the registry database produces a row whose hash no longer matches the anchor, which the reconciliation job of §5.5 detects.

### 3.6 Agent variant: the conveyancing agent

A conveyancing agent acting for a purchaser must establish that the seller holds good title, that the chain of title is unbroken back to a point the purchaser's policy accepts, and that no undischarged lien exists, and it must do so without being given read access to the registry database, because the registry will not grant a purchaser's software such access.

The agent's procedure uses only F2, F6, G4 and off-chain objects. It receives the seller's current deed credential from the seller's wallet (a presentation, F8-committed so that the seller cannot later deny having presented it). It verifies the registry's signature off-chain, resolves the registry DID (F2), checks F6 on the credentialId, checks G4 that the registry was endorsed for `PROPERTY_DEED` at issuance time by the ministry root the purchaser's policy names. It then walks back: the deed content's `previousCredentialId` is queried with F6 (expected: exists, revoked; a prior deed that is *not* revoked is a red flag meaning two live deeds exist), and the previous deed's content is requested from the registry's read API or from the seller if held; its hash is compared with `previousCredentialHash`. The walk continues to the policy's depth. For liens, the agent checks F6 on each `registeredCharges` entry and on any credentialId the read API returns for the parcel; every one must be revoked (discharged) or accepted by the purchaser.

The assumption that makes this work is that the off-chain content of *historical* deeds is obtainable: the chain proves existence, ordering and revocation state, but the hash links can only be walked with the content. Where the registry serves historical instruments through its read API (as title-search services do today, for a fee), the agent needs no database access; where it does not, the agent can verify the *current* deed fully and the chain of title only as far as the seller's wallet retains prior deeds. This is a deliberate degradation, and the purchaser's policy states the acceptable depth.

## 4. Repair and maintenance history

### 4.1 The MOBI VID II lifecycle set as the model

MOBI VID II [27] defines the vehicle's mutable history as a set of issuer-attested lifecycle events, and the repository's `MOBIVIDRegistryV2.sol` (verified at source for this document) implements eleven event types (MAINTENANCE, REPAIR, ACCIDENT, RECALL, INSPECTION, MODIFICATION, THEFT_REPORT, RECOVERY, INSURANCE_CLAIM, REGISTRATION, DECOMMISSION) with a role-per-event-type authorisation matrix (`_initializeAllowedIssuers`) and a per-event `verified` flag that is true for MANUFACTURER, GOVERNMENT_DMV, POLICE, DEALER and INSPECTION_STATION roles and false for OWNER and others. That contract is the *pre-campaign* design and it stores the odometer reading, a jurisdiction string, the issuer address and a timestamp on-chain per event.

The HDA design keeps the event taxonomy and the role matrix and relocates the data. Each lifecycle event becomes a credential of the corresponding type in the type registry (brief §7), issued by an issuer whose DID is endorsed (G2) for that event type by the appropriate root: the OEM for its dealers and service network, the ministry for the DMV and inspection stations, the police service for its officers, the insurer's regulator for insurers. The role matrix of `MOBIVIDRegistryV2` becomes an endorsement policy: "who may issue a RECALL" is "who is endorsed for RECALL", and the MANUFACTURER-only rule is the OEM endorsing only itself. On-chain per event: the F5 anchor (issuer DID, subject = vehicle DID, hash, validity). Off-chain: odometer, jurisdiction, services performed, parts, cost, technician, the issuer's signature. The odometer moves off-chain because it is the field the second-hand market most wants to check, and the check (§4.3) does not need it on-chain.

The multi-party attestation of the V2 contract (`attestEvent`, several roles co-signing one event) maps to two mechanisms depending on the party: a second endorsed issuer co-signs the same off-chain event object (its signature is part of the content, and both issuers anchor the same hash with F5, giving two credentialIds for one event), or, for reputation-style attestations by parties that are not issuers, Set C `attestReputation` on the vehicle DID with the event's credentialId in the evidence URI (06 treats reputation).

### 4.2 Actors and objects

The vehicle holds a DID (F1, controller = the owner's wallet or the fleet manager's). Issuers: OEM, dealer, independent service centre, inspection station, DMV, police, insurer, owner, fleet manager, each with a DID and an endorsement for the event types they may issue. Verifier classes: a *buyer* in the second-hand market, an *insurer* pricing a policy, the *OEM* targeting a recall, a *fleet manager* scheduling service. Objects: the `VID_BIRTH` credential (MOBI VID I; issued by the OEM at production, the immutable root the lifecycle hangs from) and the lifecycle event credentials.

Tier: Tier 3 for every event, with one exception: a THEFT_REPORT and its RECOVERY affect gated access (06) and are read on the Tier 2 path.

### 4.3 Odometer monotonicity, completeness and absence of tampering

Three properties are what a buyer wants, and they are produced by three different mechanisms.

*Absence of tampering* of any one event is the hash match: the event object the seller presents hashes to the anchored `credentialHash`, and the issuer's signature verifies against the issuer DID's key at issuance time (F2 resolution, with the DID document's key history). An event with an altered odometer hashes to a different value and fails.

*Odometer monotonicity* is an off-chain check across the presented events sorted by their attested date: each reading must be at least the previous one, with a tolerance for instrument replacement events (a MODIFICATION event of a defined subtype). The V2 contract offered `getOdometerHistory` as an on-chain view; the HDA design performs the identical check in the verifier from the off-chain objects, which is possible precisely because each object's integrity is anchored. Nothing is lost and the per-event storage cost of a `uint256` odometer, a `string` jurisdiction and a struct is not paid.

*Completeness* is the hard one, and this is where the design must be clever and honest. Selective disclosure is a feature for privacy and a defect for completeness: a seller can present the maintenance events and omit the ACCIDENT. Two mechanisms address it and they trade against each other.

The first is the *public anchor count*. Every event is F5-anchored with `subject = vehicleDid`; the chain's `CredentialIssued` events indexed by subject are a public list of how many events exist, of which types (the type registry tags them), from which issuer DIDs, and when. A buyer who is shown twelve event objects but counts thirteen anchors knows one is withheld, and knows its type and issuer. The seller cannot suppress an anchor because the seller did not write it. What this costs is privacy: the event count, types and issuers per vehicle DID are public, and issuer DIDs are in general resolvable to businesses. The 2020 dual-identity mode mitigates it at the price of completeness: if the vehicle uses a pairwise DID per service relationship, the anchors no longer aggregate under one subject, and the buyer must be given the pairwise DIDs (and proofs of their linkage, F12) to count them. The design states this trade-off as a policy choice per jurisdiction, and notes that for vehicles, unlike persons, regulators have historically chosen disclosure (the vehicle history report industry exists because of it).

The second is the *periodic Merkle root*. A party with a complete view (the DMV at registration renewal; a fleet manager for its fleet; the OEM for warranty vehicles) computes a Merkle root [NEW-9] over all event credentialIds it knows for the vehicle at time *t* and anchors the root as a `HISTORY_SNAPSHOT` credential (F5, `subject = vehicleDid`). The buyer verifies Merkle inclusion of every presented event in the latest snapshot and compares the snapshot's leaf count (in the content) with the number presented. This gives completeness *as of the snapshot* from a party the buyer trusts, at one anchor per snapshot instead of relying on the public anchor count, and it is the mechanism that survives pairwise DIDs. What breaks it: events after the last snapshot, and the snapshotter's own honesty (it is an endorsed issuer, so its dishonesty is attributable).

### 4.4 Recall targeting, insurance pricing, the second-hand market

*Recall targeting.* The OEM knows which VINs are affected; it needs to reach current owners, whom it does not know. With the VID layer the OEM issues a RECALL event (F5, `subject = vehicleDid`) for each affected vehicle; the current controller of the vehicle DID (F2 resolution gives the controller) is the notified party, and the completion of the recall is a REPAIR event by an endorsed service centre referencing the RECALL credentialId. An open recall is then a public, verifiable fact (RECALL anchor with no referencing REPAIR anchor) that a buyer or inspector can check with no access to the OEM's system. The 2020 paper's distributed-oracle concept [5] fits here for the reverse flow: an oracle attesting a physical inspection result into a credential.

*Insurance pricing.* The insurer requests a presentation of ACCIDENT, INSURANCE_CLAIM, THEFT_REPORT and INSPECTION events plus the latest snapshot; the holder discloses those types and withholds MAINTENANCE detail (the mobi-vid README's "insurance sees claims, not maintenance" profile), and the insurer verifies completeness by the snapshot. Pricing on verified rather than self-reported history is the "problem solved"; 06 develops the payment side.

*Second-hand market.* The buyer's procedure is §4.3 in full: birth certificate (VID I) hash and OEM endorsement; every lifecycle event's hash, signature, F6 and G4; odometer monotonicity; completeness by anchor count or snapshot; open recalls; and, from the DMV's REGISTRATION events, the ownership sequence. The vehicle history report becomes a verifier-side computation over holder-presented, issuer-signed, chain-anchored objects rather than a product purchased from an aggregator that holds everyone's data.

### 4.5 Agent variant: the fleet-maintenance agent

A fleet-maintenance agent schedules service for a fleet of vehicles based on verified history, and reports events itself. The agent holds a DID delegated by the fleet manager (F11, `sigAuth`, scoped and time-limited as in §2.7) and is endorsed, through the fleet manager's own endorsement, for the OWNER or FLEET_MANAGER role only.

For scheduling, the agent verifies each vehicle's history exactly as the buyer does in §4.3, computes the next due service from the last MAINTENANCE event's odometer and date and the OEM's schedule (itself publishable as a credential), and books it with an endorsed service centre through an I2I channel (08). The agent's *own* reports (telematics-derived mileage, a self-diagnosed fault) are issued as events with the agent's DID as issuer (F5), and, because the agent's endorsement is for the OWNER role, the verifier treats them exactly as `MOBIVIDRegistryV2` treats OWNER events: `verified = false`, unverified until an endorsed service centre issues a corresponding REPAIR or MAINTENANCE event that references the agent's credentialId. The self-report is therefore useful (it gives the service centre the reason for the visit and gives the history a timestamped symptom) without being trusted (no buyer's verifier counts it toward monotonicity or completeness unless attested). This is the OWNER/attested distinction of VID II carried unchanged into the agent setting, and it is the same "unverified until attested" rule that 09 argues reputation systems need in order to bound what a single self-interested participant can inject.

The confused-deputy guard applies again: the agent's F11 delegation and its role endorsement bound it to *reporting*; it cannot issue a REPAIR event however it is prompted, because G4 will report it not endorsed for REPAIR.

## 5. Integration with legacy back ends

### 5.1 The adapter pattern

The claim of this section is that every legacy register can participate through one adapter shape, and that the adapter's invariants are what make the §1.3 argument true in practice. The adapter has four parts, and the register of record is not one of them: it stays exactly where it is.

The *signer/anchor service* holds the registrar's issuing key (in an HSM or equivalent, as its PKI key is held today) and the mapping from that key to the registrar's DID (registered as a verification method by F9). It receives a record extract from the registrar's application, builds the credential object with the type registry's schema, salts and canonicalises it, signs it, hashes it, submits F5, and returns credentialId, hash and salt to the registrar's application, which stores them beside the row. Invariant one: *the adapter never places PII on-chain*; the only chain-bound payloads it constructs are DIDs, hashes, validities and type tags.

The *issuance queue* (§5.3) sits between the application and the signer, and applies the endorsement policy. The *read API* (§5.2) serves resolver and status queries. The *reconciliation job* (§5.5) compares the register with the anchors.

### 5.2 Read APIs: resolver and status

Verifiers, wallets and agents need three reads: resolve an issuer DID (F2), check a credential's status (F6), check an endorsement (G4). All three are gas-free view functions and can be served by a cached replica of chain state, with invalidation driven by the `CredentialRevokedEvent`, `DIDUpdated`, `DIDDeactivated` and endorsement-revocation events (the supervisor memo's rule). The registrar's read API exposes exactly these, plus a fourth that is the registrar's own: *retrieve credential object by credentialId*, access-controlled as the registrar's extracts are today (free to the holder, fee-based or authorised for title searches, restricted for licences). This fourth endpoint is how a conveyancing agent walks the chain of title (§3.6) and how a buyer's verifier obtains a snapshot. It is not part of the identity system; it is the registrar's existing extract service returning a different format.

### 5.3 Write APIs: the issuance queue with endorsement policy

Every write goes through a queue that enforces one check before F5: G4 `isEndorsed(issuerDid, credentialType)` must be true for the type being issued, as of now. This is the same check verifiers perform after the fact, performed before the fact, so that a registrar whose endorsement has lapsed (or a regional office whose endorsement has been revoked by G3) cannot anchor a credential that no verifier will accept. The queue also serialises revoke-and-reissue pairs (§3.3) and retries on chain faults (reorgs, delayed finality; the threat model of brief §2), treating an anchor as confirmed only at the finality depth 03 sets per chain profile. Throughput is bounded by the chain's block gas budget divided by the per-anchor cost; the campaign has one measured per-anchor figure (F5 at 130,163 gas on O1, brief §5) and the queue's design parameter is stated as a formula, anchors per block ≤ block gas limit ÷ gas(F5), not as a number.

### 5.4 Migration: bulk Merkle anchoring

A land registry holds millions of live titles; a DMV holds millions of licences (Canada has roughly 33 million registered vehicles, DIGEST-LEVEL, brief §5, and a comparable order of licence-holders). Anchoring each existing record individually with F5 would cost millions of transactions and, at O1's measured F5 cost, a gas budget the campaign will not pretend to price. It is also unnecessary.

The migration pattern is *bulk Merkle anchoring*: the registrar's adapter builds credential objects for all existing records (or for a partition of them), computes their salted hashes as leaves, builds a Merkle tree, and anchors the root once as a `MIGRATION_BATCH` credential (F5, `issuer = registrarDid`, `subject = registrarDid`, `credentialHash = root`, content = batch descriptor with leaf count, partition, and date). Each record's row stores its leaf hash, salt and Merkle inclusion path. A verifier presented with a migrated credential verifies the registrar's signature, computes the leaf, checks the inclusion path against the anchored root, and checks F6 on the batch credential and G4 on the registrar. Individual revocation of a migrated credential is then handled by the registrar issuing it anew (F5, individually) at the next touch (renewal, transfer, first presentation that needs individual revocability) and by the batch being *superseded*: a `MIGRATION_BATCH` is never revoked wholesale, but a per-record revocation list keyed by leaf hash is published by the registrar as a Bitstring Status List [NEW-5] whose own hash is anchored (F5) and re-anchored on change. The cost driver becomes one anchor per batch plus one per status-list update, independent of record count; this is the "no per-record chain cost" the brief asks for, and it is an application of the GDPR-safe placement of §1.4 (the root commits to a set, not a person).

The honest assumption: migrated credentials have coarser revocation (status-list update interval) than natively issued ones (F7, immediate), so the verifier's policy must treat a `MIGRATION_BATCH`-backed credential as valid only up to the status list's staleness window. 02 discusses status list versus accumulator trade-offs; the choice here is status list because holder privacy is not the migration's constraint.

### 5.5 Reconciliation with the register of record

The register of record is authoritative; the chain is evidence. The two can diverge in exactly two ways. The registrar corrected a record (legitimately) and the anchor has not been updated: the reconciliation job detects a row whose current hash does not match its stored anchor and enqueues a revoke-and-reissue. Or a row was altered without the adapter's involvement, whether by an insider, a bug, or an intrusion: the same mismatch is detected, but no correction is found in the registrar's own change log, and the case is escalated. The reconciliation job runs on the registrar's side, over the registrar's data, against a cached chain replica; it is the forensic-audit-trail property of the Building Paths preface applied to the registrar's own integrity. The design does not make the chain override the register; it makes disagreement between them visible and attributable, which is the thesis's stated claim for the accountability primitive.

## 6. Comparison table

The table places every registry type treated in this document, plus the two CAV types from 04 for comparison, on the same axes. "Cost driver" names the quantity a cost model would multiply; no cost is stated as a number.

| Registry type | On-chain | Off-chain | Who issues (F5) | Who endorses (G2) | Verifier classes | Tier | Cost driver |
|---|---|---|---|---|---|---|---|
| Driver's licence (`DRIVER_LICENCE`) | Anchor (hash, validity, issuer/subject DIDs); revocation (F7); F8 commitment for auditable presentations; DMV endorsement | Attributes, portrait, salts, DMV signature; SD digests | DMV | Ministry (root) | Police (full); car-share (predicate); insurer (subset, pairwise) | 3 issue; 2 check | Issuances + suspensions per year; F8 only for police-class presentations |
| Licensed operator (agent) (`LICENSED_OPERATOR`) | F11 delegation; anchor of operator credential | Scope, purposes, reference to human licence | Human licence-holder's wallet | None (derives validity from referenced licence + F12) | Any verifier accepting the human licence | 2/3 | Delegations per agent lifetime; F11 measured 54,227 gas on O1 (S1) |
| Vehicle registration (`VEHICLE_REGISTRATION`, from 04) | Anchor; revocation; DMV endorsement | Plate, jurisdiction, owner DID, validity | DMV | Ministry | Police, tolling, parking, insurers | 3 issue; 2 check | Registrations + renewals per year |
| Property deed (`PROPERTY_DEED`) | Anchor; revocation on transfer; ordering by event log; registry endorsement | Parcel, legal description, owner DID, charges, registry signature, previous-deed link | Land registry | Ministry / attorney-general | Purchaser (conveyancer or agent), lender, municipality | 3 | Transfers per year (two anchors each: F7 + F5) |
| Lien (`LIEN`) | Anchor; revocation on discharge | Amount, terms, deed reference, lender signature | Lender | Registry or financial regulator | Purchaser, other lenders | 3 | Registrations + discharges |
| Vehicle birth certificate (`VID_BIRTH`, MOBI VID I) | Anchor; OEM endorsement (per plant) | VIN (encrypted), make, model, year, first owner, OEM signature | OEM plant | OEM (root) | Everyone downstream | 3 | Production volume (one anchor per vehicle, once) |
| Lifecycle event (11 types, MOBI VID II) | Anchor per event; optional `HISTORY_SNAPSHOT` root | Odometer, services, parts, cost, jurisdiction, issuer signature | Role-appropriate issuer per type | OEM / ministry / police service / insurer regulator, per type | Buyer, insurer, OEM (recall), fleet manager, inspector | 3 (theft/recovery read at 2) | Events per vehicle per year; snapshot interval |
| Migrated legacy record (`MIGRATION_BATCH`) | One root per batch; status-list hash per update | All record content; leaf, salt, inclusion path per row | Registrar (batch) | Ministry | As per underlying type | 3 | Batches + status-list updates, independent of record count |

Two observations from the table earn their place. Every row has the same on-chain column up to the presence of F11 and the optional snapshot: the on-chain footprint is *type-invariant*, which is the concrete form of the claim that the system is registry-agnostic. And the cost driver is in every case an *event rate* of the registry's own business (issuances, transfers, services) rather than a function of record count, which is the concrete form of the scalability claim 03 makes.

## 7. Problems solved, further functionality, and the agent economy

The brief asks that every scenario carry a tail connecting it to problems solved and to further functionality, including toll payment, pay-as-you-use roads, road-condition reporting and federated learning. For back-end registries the tails are as follows, and the last subsection gathers them into the agent economy that sits on top.

### 7.1 Driver's licence

Solved: licence checks without a call to the DMV; predicate-only proofs to commercial verifiers; cross-border recognition without bilateral integrations; instant, propagating suspension. Further: a licence credential is the natural *authorisation* object for pay-as-you-use road schemes and tolling (06), because a toll authority charging by driver rather than by vehicle (a car-share, a rental) can bind the charge to a pairwise licence presentation; it is the eligibility credential for any road-condition reporting scheme that wants to weight reports by licensed drivers (09); and, through the licensed-operator delegation, it is what lets an agent be admitted to those schemes at all.

### 7.2 Property deeds

Solved: title verification without registry access; ordering and non-repudiation of transfers; insider-alteration detection for the registrar; lien discovery across lenders. Further: a verified deed is an authorisation credential for *gated access* to the property's connected infrastructure (a private EV charger, a gate, a parking allocation; 06's gated-access pattern with a deed instead of a fleet credential); it is the settlement precondition for property-linked payments; and a verifiable, cross-registry title is the input a mortgage-pricing model or an insurer's federated risk model needs without any registry disclosing its database (09).

### 7.3 Repair and maintenance history

Solved: verifiable, complete, tamper-evident history; odometer fraud detection at the verifier; recall targeting to current controllers; pricing on verified rather than self-reported history. Further: the lifecycle set is the *training-data provenance* layer for the 2020 paper's high-latency tier use case, "driving data for neural-network and autonomous-driving training" [5]: a vehicle's contribution to a federated model (09) is weighted by a reputation that is itself derived from a verified history (inspection currency, absence of tampering events), and the contribution is signed by a DID whose history the aggregator can check. Road- and traffic-condition reports from a vehicle with a verified sensor-calibration INSPECTION event are worth more than reports from one without; 09 argues the full chain from identity to reputation to collective computation.

### 7.4 The agent economy on top

The three agent variants of this document (licensed operator, conveyancing agent, fleet-maintenance agent) share one structure: an agent with its own DID, a scoped and expiring delegation from a human or organisational principal (F11), a credential whose validity derives transitively from the principal's (F6 on the referenced credential), and a role endorsement that bounds what the agent may issue (G4). On that structure, agents *transact on verified licences, titles and histories*: an agent can rent a vehicle on a licence, purchase a property against a verified title, or schedule and pay for service on a verified history, with every action attributable (signed traces, F8 commitments) and every authority bounded (scope, expiry, transitive revocation). This is the Chapter 5 I2I generalisation made economic: the same twelve functions that give a vehicle an accountable identity give an agent an accountable *mandate*, and the endorsement extension gives the mandate a verifiable root. 11 develops the academic argument; 04 gives the full-coverage agent scenario; this document's contribution is to show that the mandate pattern is the same across three unrelated registries.

## 8. Demonstration plan

### 8.1 What runs on the planned VID layer today

The brief §7 states that S7 (`scenarios/run_vid_minimal.js`) issues `VID_BIRTH`, `VEHICLE_REGISTRATION` and `DRIVER_LICENCE` with endorsement, verifies off- and on-chain, presents with a challenge, revokes one, and re-verifies; and that S8 (`scenarios/run_vid_lifecycle.js`) issues the eleven lifecycle event credentials with endorsement gating, checks odometer monotonicity off-chain, runs a theft-to-recovery chain and a decommission. At the time of writing neither script exists in the sandbox (the `scenarios/` directory holds `run_i2i.js` only, and `contracts/credentials/` is empty); the status is "under construction" per the brief, and 10 will report what was built.

When S7 runs, it demonstrates §2.2 (issuance), §2.4's police profile (full-disclosure presentation with F8), §2.5's suspension (F7 and re-verification), and the endorsement check of §2.6 within one jurisdiction. When S8 runs, it demonstrates §4.1 (typed events, role-appropriate issuers, endorsement gating), §4.3's odometer monotonicity and the OWNER-unverified rule of §4.5, and §4.4's recall-and-repair pairing if the script issues a RECALL followed by a referencing REPAIR. What neither demonstrates is the selective-disclosure profiles of §2.4 (car-share, insurer), which need the VC layer's SD digests wired to the `lib/vid` presentation builder and are a candidate S7 extension, and the snapshot mechanism of §4.3, which is a `HISTORY_SNAPSHOT` type and a Merkle builder.

### 8.2 What a deed demonstration adds

A deed demonstration, proposed as S9 `scenarios/run_vid_deed.js` (name proposed here, not yet in the brief), adds *two credential types and no interface change*: `PROPERTY_DEED` and `LIEN` in the type registry with their schema hashes, and two builders in `lib/vid`. The script would create ministry, registry, lender, seller and buyer DIDs (F1); register and endorse the registry for `PROPERTY_DEED` and the lender for `LIEN` (G1, G2); issue the seller's deed (F5); issue a lien referencing it (F5); transfer by revoke-and-reissue (F7, F5) with the new deed's content linking the old; discharge the lien (F7); and run the conveyancing-agent walk of §3.6 as an off-chain verifier that calls only F2, F6 and G4. The `MIGRATION_BATCH` pattern of §5.4 is a further small addition: a Merkle builder and one F5 of a root, with inclusion-proof verification off-chain. The point to make in 10 and 11 is that the entire extension from vehicles to land is *credential types plus off-chain verifier logic*; the chain-side surface is unchanged, which is the strongest form of the registry-agnostic claim and is directly testable.

### 8.3 Trace assertions

The traces (JSONL per `traces/SCHEMA.md`) support the following assertions, each mapped to a section of this document. They are stated as assertions the scripts should emit and the tests should check, not as results.

1. Every `CredentialIssued` in S7/S8/S9 is preceded in the trace by a `G4` view entry returning true for `(issuer, type)`; an attempted issuance by a non-endorsed DID yields a `G4` false and no `CredentialIssued` (§2.2, §4.1, §5.3).
2. After `F7` on the licence, an `F6` view entry reports `revoked = true` and the off-chain verifier entry (`kind: offchain`) reports rejection; a subsequent `F5` reissue produces a new credentialId and `F6` valid (§2.5).
3. The `F8` entry's challenge equals the challenge recorded in the preceding verifier `offchain` entry, and a second `F8` with the same challenge reverts (replay; §2.4).
4. In the agent variant, `F12` returns true within the delegation validity and false after it; `F6` on the referenced human licence returning `revoked = true` causes the operator verifier entry to reject (§2.7).
5. In S9, the trace order is `F7(deed_S)` before `F5(deed_B)`, `F6(deed_S)` reports revoked, and the conveyancing verifier entry records a walk of depth ≥ 2 with every hash link matching (§3.3, §3.6).
6. In S8, the off-chain monotonicity entry records the sorted odometer sequence and flags an injected non-monotonic OWNER event; the same event carries `verified = false` until a `SERVICE_CENTER` event references it (§4.3, §4.5).
7. The count of `CredentialIssued` entries with `subject = vehicleDid` equals the number of event objects the S8 holder wallet holds (public-anchor-count completeness; §4.3).
8. Gas: every `tx` entry carries `gasUsed`; the assertion is only that G1, G2, G3 and each typed F5 are *recorded*, so that 10 can report them. This document states no expected value.

The metrics 10 may then report are: gas per function including the governance extension; the number of chain reads a verifier needs per presentation (target: F2 once per issuer, cached; F6 once per credential; G4 once per issuer-type pair, cached); and the off-chain verification time as measured by the script's own timing, labelled as Hardhat-local and not representative.

## 9. Sources used in this document

| Ref | Source | Verification state | How used |
|---|---|---|---|
| [1] | Allen, 'The Path to Self-Sovereign Identity,' 2016 | VERIFIED AT SOURCE (thesis list) | Portability and control principles behind §1.2 |
| [5] | Prakash, Michelson, Feng, CVIN, IEEE VTC2020-Spring | VERIFIED AT SOURCE | Dual identity modes (§2.4), Local CVIN / IDPP (§2.6), oracles (§4.4), high-latency-tier use cases (§7.3) |
| [6], [28] | Brecht et al., SCMS, IEEE T-ITS 2018; IEEE 1609.2-2022 | VERIFIED AT SOURCE (thesis list) | "Extension, not replacement" analogy in §1.3 |
| [8] | W3C DID Core 1.0 | VERIFIED AT SOURCE | F2 resolution as the missing primitive in legacy registers (§1.2) |
| [9], [10] | W3C VC Data Model 1.1 / 2.0 | VERIFIED AT SOURCE | Credential object shape (§2.3), holder/issuer/verifier roles throughout |
| [14] | Fett, Yasuda, Campbell, SD-JWT, RFC 9901 | VERIFIED AT SOURCE (thesis list) | Salted claim digests for selective disclosure and the GDPR hash argument (§1.4, §2.4) |
| [19] | De Rossi et al., ERC-8004 Trustless Agents | VERIFIED AT SOURCE (thesis list) | Agent registry as optional Set C context (§2.7) |
| [23] | ERC-1056 | VERIFIED AT SOURCE | O1 delegation semantics underlying F11/F12 (§2.4, §2.7) |
| [27] | MOBI VID I–II | VERIFIED AT SOURCE (via repository README, `2_w3c-ssi-layer/mobi-vid/README.md`) | Lifecycle event taxonomy and issuer roles (§4) |
| — | `cv2x-testbed/contracts/MOBIVIDRegistryV2.sol` | VERIFIED AT SOURCE | Role matrix, `verified` flag, on-chain odometer storage that the HDA design relocates (§4.1, §4.3) |
| — | S1 trace `traces/i2i_O1_ERC1056_1780620182135.jsonl`, via brief §5 | VERIFIED AT SOURCE (brief §5 summary) | F5 130,163; F7 32,980; F11 54,227 gas, cited only where the same function is invoked (§2.2, §2.5, §6) |
| NEW-1 | Regulation (EU) 2024/1183 (eIDAS 2.0) | DIGEST-LEVEL (summary read; full text not read at source) | Direction of holder-held attestations with registries authoritative (§1.4) |
| NEW-2 | EUDI Wallet Architecture and Reference Framework | DIGEST-LEVEL | Trust lists, selective disclosure, no PII on ledger (§1.4) |
| NEW-3 | ISO/IEC 18013-5 mobile driving licence | DIGEST-LEVEL | Data-element compatibility of the licence credential (§1.1, §2.3) |
| NEW-4 | GDPR, Regulation (EU) 2016/679, Art. 17 and Recital 26 | DIGEST-LEVEL | Personal-data status of content hashes; erasure by revoke-and-delete (§1.4) |
| NEW-5 | W3C Bitstring Status List v1.0 | DIGEST-LEVEL | Status-list revocation for migrated records (§1.4, §5.4) |
| NEW-6 | Trust over IP governance stack | DIGEST-LEVEL | Trust-registry layer analogy for endorsement walks (§2.6) |
| NEW-7 | Hardy, 'The Confused Deputy,' ACM SIGOPS OSR 1988 | DIGEST-LEVEL | Confused-deputy guard for delegated agents (§2.7, §4.5) |
| NEW-8 | Torrens title system (general legal reference) | DIGEST-LEVEL | Register-conclusive title as the model for revoke-and-reissue (§3.2) |
| NEW-9 | Merkle, 'A Digital Signature Based on a Conventional Encryption Function,' CRYPTO 1987 | DIGEST-LEVEL | Merkle inclusion for snapshots and bulk migration (§4.3, §5.4) |

The repository README's performance table (birth certificate 50 ms, ~$0.50; lifecycle event 20 ms, ~$0.10) is not trace-backed and is deliberately not used anywhere in this document.

## 10. Registry delta rows

| Content Block | T | Source | Ch. | Ready % | Notes |
|---|---|---|---|---|---|
| Register-of-record principle: chain as anchor and verification substrate, never the authoritative register; correctability, privacy, institutional arguments | A | 07 §1.3 | 5 §5.2; 4 §4.4 | 85 | Needs supervisor view on how strongly to state the legal argument |
| GDPR hash nuance applied to registries: salted content hashes, erasure by revoke-and-delete, batch roots as set commitments | A | 07 §1.4; 01; 02 | 4 §4.4 | 75 | eIDAS 2.0 / EUDI ARF citations DIGEST-LEVEL; verify at source before submission |
| Minimal `DRIVER_LICENCE` credential object (mDL-compatible field naming) | B | 07 §2.3; brief §7 | 4 §4.3; 5 §5.2 | 80 | Field names to be confirmed against `lib/vid` builders when built |
| Three-verifier disclosure profiles for one anchored licence (police / car-share / insurer) with F8, SD digests, pairwise delegation | A/B | 07 §2.4 | 5 §5.2 | 80 | ZK linkage path unmeasured; stated as two-level design |
| Cross-jurisdiction recognition by endorsement walk; Local CVIN / IDPP mapping; signed endorsement-extract fallback | A | 07 §2.6; [5] | 5 §5.2 | 70 | Endorsement-extract object schema not yet specified |
| Licensed-operator delegation pattern with transitive revocation and confused-deputy guard (verifier-enforced scope) | A | 07 §2.7, §4.5 | 5 §5.2 (I2I) | 85 | Feeds 11 endorsement argument and 04 agent scenario |
| Deed transfer as revoke-and-reissue with event-log ordering proof; lien as referencing credential; atomicity gap and batch extension | A | 07 §3.3–3.5 | 5 §5.2 | 80 | Torrens mapping DIGEST-LEVEL |
| Conveyancing-agent chain-of-title walk using only F2/F6/G4 plus off-chain objects; declared degradation when historical content unavailable | A | 07 §3.6 | 5 §5.2 | 80 | Demonstrable by proposed S9 |
| Completeness mechanisms for lifecycle history: public anchor count vs `HISTORY_SNAPSHOT` Merkle root; privacy trade-off with pairwise DIDs | A | 07 §4.3 | 4 §4.4; 5 §5.2 | 75 | Policy choice left to researcher (§11 Q3) |
| Relocation of `MOBIVIDRegistryV2` on-chain fields (odometer, jurisdiction) to off-chain credential content with verifier-side monotonicity | A/B | 07 §4.1, §4.3; V2 contract | 4 §4.4 | 85 | Directly contrasts pre-campaign contract with HDA placement |
| Legacy adapter pattern: signer/anchor, issuance queue with G4 pre-check, read API, reconciliation job; invariant "no PII on-chain" | A | 07 §5.1–5.5 | 4 §4.4 | 85 | Throughput stated as formula only |
| Bulk Merkle migration: one root per batch, status-list revocation for migrated records, no per-record chain cost | A/B | 07 §5.4 | 4 §4.4; 5 §5.2 | 80 | Staleness-window policy for migrated credentials to be set in 03 |
| Registry comparison table (8 rows × 8 axes); type-invariant on-chain footprint; cost driver as event rate | B | 07 §6 | 5 §5.2 | 90 | No numbers; ready for direct inclusion |
| Demonstration plan and trace assertions for S7/S8/proposed S9 | B | 07 §8 | 4 §4.3 | 70 | Contingent on build; 10 reports |

## 11. Open questions for the researcher

1. *Public anchor count versus pairwise privacy for vehicles.* §4.3 shows completeness and unlinkability trade directly: per-vehicle anchors under one DID give a buyer completeness for free but expose event count, types and issuers publicly. Should the thesis take the position that vehicles (unlike persons) default to a single public DID for lifecycle anchoring, with pairwise DIDs reserved for Tier 2 interactions, or should the `HISTORY_SNAPSHOT` mechanism be the default and the public count be treated as a privacy defect? This determines what S8 anchors and what 11 argues.

2. *How hard to state the legal argument in §1.3.* The document argues that the chain must not be the register of record on legal grounds (correctability, conclusiveness by statute). This is a claim about law, not engineering, and the examining committee may include a lawyer or may not. Should Chapter 4 §4.4 carry this argument with legal citations (which would require sourcing eIDAS 2.0, GDPR and a Torrens-system authority at source rather than DIGEST-LEVEL), or should it be stated as a design constraint adopted from practice with the legal detail left to the discussion?

3. *Whether the deed demonstration (proposed S9) is in scope for this pass.* §8.2 argues it is cheap (two types, two builders, one script) and that it is the strongest test of the registry-agnostic claim because it is the registry furthest from vehicles. Building it costs build time in a pass whose build target is the VID layer. Is the generalisation claim important enough to the thesis's Chapter 5 to justify it now, or is a design-only §8.2 sufficient for the general pass?

4. *Verifier-enforced scope as the confused-deputy guard.* §2.7 places scope enforcement with the verifier rather than the agent, on the argument that the agent's judgement is the attack surface. This is a design stance with consequences for 04's agent scenario and 11's I2I argument: it means the "agent identity wrapper" of contribution C14 must standardise a scope vocabulary that verifiers can evaluate. Does the researcher accept that consequence, and should the scope vocabulary be a registry-delta item for this pass or deferred to the I2I bridging paper (C15)?

5. *Migrated-credential staleness policy.* §5.4 gives migrated records status-list revocation with an update interval rather than immediate F7. The acceptable interval is a per-registry policy that 03 must set for its degraded modes. Should the thesis state a single default (for example, the status list is re-anchored at least daily) as a design parameter, or leave it as a variable with the observation that it bounds the harm of a stale acceptance?
