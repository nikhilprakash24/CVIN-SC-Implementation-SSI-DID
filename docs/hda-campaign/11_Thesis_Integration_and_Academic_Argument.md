CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**Thesis Integration and Academic Argument**

**How the Hybrid Data Architecture campaign, the endorsement pattern and the VID reference build fold into the five thesis chapters, with draft-ready prose, registry rows and corrections**

Document 12 of 16 · Hybrid Data Architecture (HDA) Campaign · Primary deliverable · Suite v1.0 · September 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 00 Master Plan · 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 10 VID Build Documentation · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: Type A prose → Chapter 1, §1.1, §1.3; Chapter 2, §2.3, §2.5 (new); Chapter 3, §3.1, §3.3 (new); Chapter 4, §4.5 (new); Chapter 5, §5.1, §5.5 (new)*

> **Post-build note (2026-10-04).** This document was drafted before the VID layer was executed. Scenarios S7 and S8 have since run and produced traces; where the text below says that only the S1 trace is measured, or labels S7/S8 quantities as pending, read it together with document 10 §5 (measured gas for F1–F12, G0–G4, T1–T2; the 11:1 Merkle-batch result; findings F-VID-1 to F-VID-7) and the reconciliation table in S3 §3. Canonical scenario identifiers are fixed in document 00 §6; where this document uses a different S-number for a proposed script, the register in 00 governs.

---

## 0. What this document is for

Every other primary document in this suite argues a design or documents a build. This one argues where those arguments *land*. Its claim is simple: the campaign does not add a sixth chapter or a new phase to the thesis; it supplies one design axis that the existing five chapters already presuppose but have not yet written up as a unified argument (where identity data lives and how it is proven), and one trust-framework primitive that the twelve functions presuppose but do not contain (endorsement). Both are folded into the thesis in the thesis's own register, at the contribution numbers the draft already uses, with one proposed new contribution left for the researcher to accept or decline.

Two constraints govern everything below. First, the only measured numbers are those in the brief's §5 and the O1 trace file `traces/i2i_O1_ERC1056_1780620182135.jsonl` (22 entries, 12/12 functions), from which this document additionally cites the three gas values not tabulated in the brief: updateDID (F3) 44,760; addVerificationMethod (F9) 59,607; removeVerificationMethod (F10) 36,478. Every number from the VID build itself is pending 10 (VID Build Documentation) and is labelled so. Second, `IMinimalSSI` is normative; nothing here changes a signature, error or event, and the endorsement layer is argued precisely as something that lives *beside* the interface.

---

## 1. Where the campaign lands: the chapter map

The thesis draft (Narrative Synthesis v11.3) is organised as Ch.1 Introduction, Ch.2 Background and Methodology, Ch.3 Standards Inventory, Ch.4 Evaluation and Results, Ch.5 Discussion. The campaign touches all five, but unevenly: it adds motivation to Ch.1, an evaluation axis to Ch.2, a cross-family property to Ch.3, a results section and Stage 1 evidence to Ch.4, and the Family F data architecture to Ch.5. Table 1.1 gives the map; the subsections that follow say what each entry is and which contribution it attaches to.

| Chapter · section | What the campaign adds | Source document(s) | Contributions touched |
|---|---|---|---|
| 1 §1.1 Motivation | Two sentences on the placement axis (the accountability gap is a *placement* problem: SCMS keeps history nowhere; a DID keeps key history on-chain and content off-chain); one paragraph on endorsement as the missing "who may issue" question | 01 §1, this doc §2 | C1 framing |
| 1 §1.3 Contributions | C16 proposed (or folded into C4/C12); C3, C12–C13 descriptions re-worded to name placement | this doc §1.6, §5 | C3, C4, C12, C13, C16 |
| 2 §2.3 Derivation | One paragraph: the twelve functions are placement-agnostic by construction (F5 anchors a hash; F2/F6/F12 are reads); orthogonality is unaffected by extended functions | spec §6, this doc §2.3 | C1, C2 |
| 2 **§2.5 (new)** "Data placement as an evaluation axis" | The four placement classes, the read/write path distinction, and the cost model as variables; the extended-function and governance framing from spec §6 | 01 §2–§4, this doc §3 | C3, C6 |
| 3 §3.1 Six families | Endorsement/governance as a cross-family property: every family has some answer to "who may issue" (Indy roles, ERC-735/740 registries, ERC-8004 validation registry, none for ERC-1056), and the answer is orthogonal to coverage | this doc §2.4–§2.5 | C7 |
| 3 §3.2 createPresentation gap | Re-stated as a placement instance (see §3.2 of this document), not a new finding | 01 §5, 02 §3 | C3, C8 |
| 3 **§3.3 (new)** MOBI VID conformance with roles | The conformance mapping gains an issuer-role column (OEM, DMV, service centre, ministry as endorser) and an endorsement column | 10, this doc §2.6 | C4 |
| 4 **§4.5 (new)** "Data placement, anchoring and cost" | Per-function placement table for O1 with measured gas; formulas with variables for everything else; the VID build as Stage 1 evidence that the layer sits above the interface | 01 §6–§7, 10, this doc §4.1 | C8, C9, C12 |
| 4 §4.4 Real-world concerns | GDPR paragraph tightened (per-credential hash may be PII; definition hashes and accumulators are not) | 01 §8, 02 §6 | C10 |
| 5 §5.1 Structural insight | Placement reframing folded in | this doc §3 | C3 |
| 5 **§5.5 (new)** Family F as a data architecture | Tiered placement, anchor/cache/attest, degraded modes; explicitly a Stage 3 design | 03, this doc §4.2 | C12, C13 |
| 5 **§5.6 (new)** Reputation and collective computation | Why reputation needs identity and identity needs endorsement; federated learning and cooperative perception as the agent-side motivation | 09, 06 | C14 |

*Table 1.1. Chapter map for the HDA campaign. Bold = new section. Document numbers refer to the suite map in the brief.*

### 1.1 Chapter 1: motivation additions

The introduction currently motivates SSI from the accountability gap and the extension-not-replacement principle. The campaign adds one move: the accountability gap is, at bottom, a data-placement gap. SCMS pseudonymity means that the history of a vehicle's credentials is held nowhere that an investigator may later read; the DID model answers this not by putting *content* on-chain but by putting *key-material history and anchors* on-chain and content off-chain. Stating this in §1.1 makes the placement axis a first-page concept rather than a Chapter 4 afterthought. A second short addition introduces endorsement: "validly issued" and "issued by a party entitled to issue it" are different questions, and only the second closes the gap the introduction opens. Both additions are under 200 words and cite [5], [6], [8], [9].

### 1.2 Chapter 2: §2.5 and the extended-function framing

Chapter 2 gains a new §2.5 whose argument is developed in §3 of this document: the functions are placement-agnostic by construction, so a comparative evaluation must score placement separately from coverage. The section also introduces spec §6 (extended functions) formally, because the draft currently mentions extended functions only in passing (Phase 1 Formal §2.3 "sufficiency"). The governance category (registerIssuer, endorseIssuer, proposeChange) is named here and argued in §2 of this document; the privacy category (createSelectivePresentation, verifyZKProof) is pointed to 02.

### 1.3 Chapter 3: endorsement as a cross-family property

The six-family inventory characterises options by coverage and lineage. The campaign adds one row to every family profile: how the option answers "who may issue this credential type". This is a cross-family property in the same sense that "block finality as immutability" is in the Building Paths preface: every option instantiates it differently, and the instantiation is independent of the option's F/P/X coverage. The MOBI VID conformance mapping (C4) is extended with issuer roles and an endorsement column in a new §3.3.

### 1.4 Chapter 4: §4.5 and the VID build as Stage 1 evidence

Chapter 4 gains a results section, §4.5 "Data placement, anchoring and cost", whose opening is drafted in §4.1 of this document. It presents the per-function placement of O1 with the measured gas of the S1 trace, states the write-path and read-path cost model as formulas with variables, and reports the VID build (10) as Stage 1 evidence for one specific claim: that a credential-type and endorsement layer can be built above `IMinimalSSI` on O1 without altering the interface, with the layer's own gas measured separately from the twelve functions' gas. Nothing else about the VID build may be claimed in Chapter 4 until 10 reports it.

### 1.5 Chapter 5: Family F as a data architecture

Chapter 5 currently describes Family F as "the minimum-cost composite architecture ... assembled from the best-validated components of all five implementation families" (v11.3 §3.1). The campaign's hybrid design (03) reframes this: Family F is a *data architecture* (which data class lives in which placement, proven by which mechanism, read by which path) that can be realised over more than one contract set, not a contract composition. New §5.5 makes this argument, drafted in §4.2 below; new §5.6 carries 09's reputation and collective-computation chain.

### 1.6 Contributions touched and the C16 proposal

The campaign touches C3 (Set A/Set B is re-read as a placement decomposition), C4 (the VID conformance mapping gains roles and endorsement), C8–C9 (placement-labelled gas; the VID build's Stage 1 evidence), C10 (the GDPR hash nuance and the anchor-only placement for ZKP artefacts, via 02), C12–C13 (the intersectional benchmark gains a placement dimension; Family F becomes a data architecture) and C14 (the agent wrapper inherits endorsement and reputation, via 09).

It also proposes one new contribution, stated here as a proposal for the researcher to accept, rename, or fold:

> **C16 (proposed) Endorsement-gated credential architecture and the VID reference layer.** A governance extension beside `IMinimalSSI` (registerIssuer, endorseIssuer, revokeEndorsement, isEndorsed) that answers "was the issuer entitled to issue this credential type at issuance time", evaluated by a behavioural test series, and a reference VID layer (birth certificate, registration, driver's licence, eleven lifecycle event types) built above the interface on O1 as Stage 1 evidence that the twelve functions plus endorsement are sufficient for the MOBI VID I–II lifecycle without interface change.

The case for a separate number is that C4 is a *mapping* and C12 is a *benchmark*, whereas C16 is a built artefact with its own test series and its own academic lineage (§2.2). The case against is contribution inflation: fifteen is already many for an MASc, and the endorsement registry can be described as the mechanism by which C4's mapping is *realised* and C12's composite is *governed*. If folded, C4's title becomes "MOBI VID conformance mapping and endorsement-gated reference layer" and C12 absorbs the placement dimension. This document does not decide; §7.3 lists it as the first load-bearing decision.

---

## 2. The endorsement argument (thesis prose)

*Target: Chapter 2 §2.5 (second half) and Chapter 3 §3.1/§3.3. Register: thesis. Citations: thesis numbering plus NEW-n.*

### 2.1 The question verifyCredential does not answer

The twelve-function specification answers, through verifyCredential (F6), the question "is this credential validly issued?" — it exists, it is unrevoked, it is unexpired, and its issuer DID is not deactivated. It does not answer the question every real credential ecosystem asks first: "was this issuer entitled to issue a credential of this type?" A driver's licence anchored by a DID that no licensing authority has ever recognised passes F6. A vehicle birth certificate anchored by any DID that chooses to call itself a manufacturer passes F6. The specification is correct not to answer the second question: it is a *trust-framework* question, not an identity-function question, and the derivation in §2.3 was deliberately confined to what the W3C data models and Allen's principles [1], [8], [9] require of any implementation. But the question does not go away. It is presupposed by every verifier in every scenario in Chapter 4, and the thesis must say where it is answered.

The claim of this section is that the minimal trust-framework primitive that the twelve functions presuppose is an *issuer registry with endorsement*: a mapping from (issuer DID, credential type) to a time-bounded assertion, made by an endorser DID, that the issuer may issue that type; together with the ability to revoke the assertion, and a view that reports whether it held at a given time. The specification already names this primitive under its governance extension (registerIssuer, endorseIssuer; spec §6). What the specification does not do, and what this section supplies, is the argument that this primitive is minimal, that it belongs beside rather than inside the interface, and that it is evaluable by the same behavioural method as the twelve functions.

### 2.2 Lineage

Endorsement is not an invention of this thesis; it is the one idea that every deployed SSI trust framework has converged on under different names, and the thesis's contribution is to isolate it as a primitive and place it in relation to the minimal interface.

In Hyperledger Indy, the ledger admits writes only from DIDs holding a role — trustee, steward, endorser — and an ordinary issuer's schema and credential-definition transactions must be co-signed by an endorser DID; the "trust anchor" role of earlier Indy versions is the same idea under its older name (DIGEST-LEVEL; NEW-1). Kortesniemi et al. [17] identify the absence of exactly such governance in the did:ethr registry contract as a deployment risk of ERC-1056, and Dunphy [22], reflecting on Indy experiments, locates the permissioned endorser layer as the point where Indy trades decentralisation for governability. In the EVM ecosystem, the ERC-725/ERC-735 claim model reserved the issuer field of a claim for a contract that could be checked against a registry, and the draft ERC-740 proposed a claim-issuer registry for precisely this check (DIGEST-LEVEL; NEW-2); the sandbox's existing T-740 registry-gating tests exercise that pattern for O4. ERC-8004 [19] generalises the idea to agents through its validation registry, in which a third party attests that an agent's claim was checked. At the governance layer proper, the Trust over IP dual stack places "who may issue what" in an ecosystem governance framework that sits above the technical stack (DIGEST-LEVEL; NEW-3), and eIDAS realises it as trusted lists of qualified trust-service providers, which eIDAS 2.0 extends to the providers of electronic attestations of attributes for the European Digital Identity Wallet (DIGEST-LEVEL; NEW-4). Mühle et al. [2] anticipate all of this in identifying "a mechanism for establishing trust" as one of the four essential components of SSI, distinct from the identifier and from the claim registry.

The lineage has a shape. Indy puts endorsement *in* the ledger's write path; ERC-735/740 put it in a *registry beside* the identity contract; ToIP and eIDAS put it in a *list above* the technical layer. The thesis's position is the middle one, and the reason is the next subsection.

### 2.3 Why beside, not inside

An endorsement registry could be folded into the interface by adding an issuer-entitlement check to issueCredential (F5) or to verifyCredential (F6). The thesis argues that it must not be, for two reasons that are also the two criteria of the derivation.

The first is *orthogonality*. The derivation admitted a function only if its removal lost coverage of an Allen principle no other function covered. Endorsement does not change the coverage matrix (spec App. B): every cell that is satisfied without endorsement is satisfied with it. What endorsement changes is *who may satisfy* the cell — which DIDs may occupy the issuer position in F5 for a given type. That is a constraint on the *population* of the interface, not on its *functions*. Folding it in would make F5 or F6 cover the same principles twice, which the orthogonality criterion forbids, and would silently make every existing implementation non-compliant because none carries a type registry.

The second is *sufficiency with respect to standards*. The W3C VC Data Model [9], [10] explicitly leaves issuer trust to out-of-band policy: verification (§5) establishes that the proof is valid, and *trust* in the issuer is a verifier decision informed by a trust framework. A specification that hard-wired one trust framework into verifyCredential would over-specify what W3C leaves open and would be false to the derivation's claim that the twelve functions are the *minimum* the standards require. Hence the correct relationship is composition at the verifier: the verification policy of the VID layer is "F6 valid **and** isEndorsed(issuer, type) held at issuance time". The conjunction is evaluated off-chain by the verifier (or on-chain by a wrapper, at a cost that 01 §6 budgets), and the interface is untouched.

This placement has a consequence the thesis should state plainly: endorsement is a *read-path* primitive. Its one on-chain write (endorseIssuer, and its revocation) is rare and administrative (Tier 3); its reads (isEndorsed) are frequent and, like F2, F6 and F12, gas-free views that a verifier may cache with the same staleness discipline as revocation state. That is why it fits the hybrid design of 03 without adding to Tier 2 latency: an RSU that already caches revocation state for the vehicles it expects can cache the small endorsement set for the issuers it recognises.

### 2.4 How it is evaluated

The twelve functions are evaluated behaviourally, by a parameterised compliance suite that any implementation must pass unmodified. Endorsement is evaluated the same way, by a test series analogous to the sandbox's T-740 registry-gating tests, run beside the untouched twelve-test suite. The series (planned in `test/vid.js`; status pending 10) asserts at minimum: an endorsed issuer's F5 credential verifies under the VID policy; the same issuer's credential of a *different* type does not; an unendorsed issuer's F5 call succeeds at the interface (proving the interface is untouched) but the credential fails the VID policy; endorsement revocation causes subsequent policy failure without touching the credential's F6 state; an endorsement that expired *after* issuance leaves the credential valid (issuance-time semantics), while one that expired *before* issuance does not; and the endorser itself must be a resolvable, non-deactivated DID. Each assertion is a trace entry with a governance fnId (G1 registerIssuer, G2 endorseIssuer, G3 revokeEndorsement, G4 isEndorsed) so that the coverage matrix of Stage 2 can be extended with a governance column programmatically, as WO-5 requires for the twelve functions.

### 2.5 Role in the MOBI VID conformance mapping

MOBI VID I is an immutable birth certificate issued by the manufacturer; VID II is a mutable, multi-issuer lifecycle [27]. The existing conformance mapping (C4) relates the twelve functions to these requirements. Endorsement supplies the column it lacks: the *role* entitled to issue each credential type. In the reference layer, the type VID_BIRTH is issuable only by a DID endorsed as MANUFACTURER (in practice, an OEM endorsing its plants); VEHICLE_REGISTRATION and DRIVER_LICENCE only by a DID endorsed as GOVERNMENT_DMV by a ministry-level endorser; MAINTENANCE and REPAIR by SERVICE_CENTER DIDs endorsed by an OEM network or a regulator; INSPECTION by GOVERNMENT_INSPECTION; THEFT_REPORT and RECOVERY by POLICE; INSURANCE_CLAIM by INSURANCE_COMPANY; REGISTRATION and DECOMMISSION by the DMV. The eight issuer roles of the existing MOBIVIDRegistry contract in `cv2x-testbed/` are thus not discarded but *re-expressed*: what that contract enforced inside one purpose-built registry, the VID layer enforces through a generic endorsement registry beside a generic interface. That re-expression is the Stage 1 evidence the campaign contributes to C4, and it is testable: the same lifecycle that `cv2x-testbed/` runs against its own registry must run, event for event, against `IMinimalSSI` plus `EndorsementRegistry` on O1 (scenario S8, pending 10).

---

## 3. The data-placement argument (thesis prose)

*Target: Chapter 2 §2.5 (first half), Chapter 3 §3.2 (re-statement), Chapter 5 §5.1 and §5.5. Register: thesis.*

### 3.1 One axis, two findings

The thesis reports two findings that it currently presents separately: the EVM/LFDT divergence (EVM options anchor identity on-chain and defer selective disclosure to off-chain middleware; LFDT/AnonCreds generates presentations off-chain and anchors only credential definitions and revocation accumulators) and the createPresentation gap (no EVM standard natively implements F8). The claim of this section is that these are not two findings but two instances of one design axis: *where each datum of the identity system lives, and how a verifier proves something about it*. Once the axis is named, the divergence is a difference of default placement, the gap is a difference of where a presentation's *proof* is computed, and both become scoreable rather than merely observable.

The four placement classes the evaluation needs are: **on-chain state** (a storage slot readable by any contract and any node: F1's controller, F7's revocation flag, an endorsement); **event log** (emitted, not stored; readable only by an indexer: ERC-1056's attribute history, every `Credential*` event); **anchor-only** (a hash or accumulator on-chain whose pre-image is elsewhere: F5's credentialHash, an AnonCreds credential definition, a revocation accumulator, a presentation commitment); and **off-chain-native** (data that never touches the chain and is proven by signature or by zero-knowledge proof over an anchor: credential content, the VP itself, the ECDH/AES channel of scenario S1). The classes differ in three things: who can read them without trusting anyone (a contract, an indexer, a holder of the pre-image, nobody but the parties), what it costs to write them, and what it costs to prove a statement about them.

### 3.2 Reframing Set A and Set B

The Set A / Set B decomposition (C3) was derived from Allen's principles: Set A satisfies Existence through Interoperability with the DID model alone, Set B adds Consent and Minimization through credentials. Placement gives the decomposition a second reading that the thesis should state alongside the first. Set A is the *on-chain-state and event-log set*: its writes create or change what the chain itself holds, and its reads (F2, F12) are answered by the chain alone. Set B is the *anchor-only set*: F5 writes a hash whose content is elsewhere, F7 flips a flag about that hash, F6 reads the flag, and F8 commits to a presentation whose content is elsewhere. The createPresentation gap is then exactly what one would predict: F8 is the one function whose *proof* (that the holder controls the credentials and discloses only what it consents to) is expensive to compute in the placement where EVM standards keep everything else. EVM standards did not "forget" F8; they stopped at the boundary of the placement class they had optimised. AnonCreds started from the other side of the boundary. The sandbox's anchor-implementation of F8 (challenge-bound, replay-protected, measured at 62,441 gas on O1) is a third point on the same axis: the *commitment* is on-chain, the *proof* is off-chain, and the thesis's finding that no EVM standard natively implements F8 is unaffected, because native support means the proof, not the commitment.

This reframing also disciplines the coverage matrix. An F/P/X score records whether a function exists; it does not record where the function puts its data or what a read costs. Two options can both score F on issueCredential while one stores the credential on-chain (as ERC-735 claims do) and the other anchors a hash; they are not equivalent for privacy, for GDPR, or for cost, and the intersectional benchmark (C12) that treats them as equivalent would mislead the composite. The evaluation should therefore carry, beside the coverage matrix, a *placement matrix* (function × option → placement class) and a *path-cost table* (function × option → write gas measured, read cost as view/indexer/pre-image). 01 §3–§7 supplies both for O1 and states the columns for O2–O8 as pending.

### 3.3 Read paths, write paths and the tiers

The three-tier latency framework (C6) classifies *operations*; placement classifies *data*. They meet at the read/write distinction. Every Tier 2 operation in the thesis's list — charging session initiation, toll authorisation, parking credential exchange, V2I service registration, manoeuvre negotiation — is, on the identity side, a *read*: resolve a DID, check a credential, check a delegate, check an endorsement, verify a presentation. None of them needs to write. The S1 trace makes this concrete: of its 22 entries, the six views (F2 twice, F6 three times, F12 once) and the one off-chain channel step are the interaction; the transactions are set-up and tear-down. It follows that Tier 2 viability is a *read-path* property, and that the design question for Tier 2 is not "is the chain fast enough" but "can the read be answered without the chain on the critical path" — from a cached DID document, a cached revocation state with a bounded staleness window, and a signature or proof over an anchor the verifier already holds. That is the supervisor memos' stance ("off-chain verification avoids block-time delays; only lifecycle events and anchors on-chain; cache invalidation synchronised with revocation state") stated as a consequence of placement. Tier 3 operations are the writes, and they may take a block time. Tier 1 remains out of scope for both.

The cost side follows the same split. Write cost is measured gas: on O1, createDID 161,823–178,935; issueCredential 130,163; addDelegate 54,227; createPresentation 62,441; revokeCredential 32,980; deactivateDID 55,127; updateDID 44,760; addVerificationMethod 59,607; removeVerificationMethod 36,478 (all from the S1 trace, Hardhat local EVM, solc 0.8.24). Read cost is not gas but *path*: a view answered by a node (free, but requires a node), an indexer query over the event log (requires an indexer one trusts or verifies), or a pre-image check against an anchor (requires possession of the content). The hybrid's central cleverness (03) is to convert as many reads as possible into the third kind, which needs no network at all, and to state exactly which assumption that rests on: that the anchor the verifier holds is fresh enough, which is a revocation-staleness bound the verifier chooses. Where that bound is violated — a credential revoked within the window — the read is wrong, and the design must say so rather than hide it.

### 3.4 What this sets up

If Set A and Set B are placement classes, if the tiers are read/write classes, and if the gap is a proof-placement difference, then the minimum-cost composite the thesis calls Family F cannot be a set of contracts. It must be a specification of which data class goes in which placement, proven by which mechanism, read by which path, at which staleness bound — and that specification can be met by several contract sets (O1 plus an endorsement registry plus off-chain VC tooling; Indy-on-Besu with its native accumulators; an ERC-4337 account for agents with the same off-chain layer). Chapter 5 §5.5 makes that argument (§4.2 below). The academic value of the reframing is that it turns the thesis's central finding from a fact about 2026's standards into a prediction: any identity standard, present or future, that keeps its data in on-chain state and event log will lack native F8, and any that keeps content off-chain-native will implement it, because F8 is the function whose proof lives on the other side of the boundary.

---

## 4. Draft prose for the new sections

Both drafts cite only measured numbers from the S1 trace and label everything else as pending or as a target. They are written to be pasted into the thesis with citation numbers unchanged.

### 4.1 Chapter 4 §4.5 opening: "Data placement, anchoring and cost"

The preceding sections reported *whether* each option implements each function and, for O1, *what* each write costs. This section reports *where* each function puts its data and what that placement implies for the cost of reading it back, because two options with identical coverage can differ entirely in what a verifier must trust and pay to use them. The analysis uses four placement classes — on-chain state, event log, anchor-only and off-chain-native (§2.5) — and separates write cost, which is measured in gas, from read cost, which is measured by path: a node view, an indexer query, or a local check against an anchor already held.

Table 4.5 gives the placement of every function on O1 (ERC-1056 pattern) as implemented in sandbox v1.3, with the write gas measured in the S1 end-to-end trace (Hardhat local EVM, solc 0.8.24, optimiser 200 runs; trace `i2i_O1_ERC1056_1780620182135.jsonl`, 22 entries, 12/12 functions). The Set A writes are on-chain state with event emission: createDID 161,823–178,935 gas across three identities, updateDID 44,760, deactivateDID 55,127, addVerificationMethod 59,607, removeVerificationMethod 36,478, addDelegate 54,227. The Set B writes are anchor-only: issueCredential stores a 32-byte credential hash and a validity bound at 130,163 gas, with the credential content never on-chain; revokeCredential flips the flag for that hash at 32,980; createPresentation records a challenge-bound commitment at 62,441, the presentation itself being off-chain-native. The three reads (resolveDID, verifyCredential, validDelegate) are gas-free views; in the trace, resolveDID returns a 96-byte document, and the secure-channel step (ECDH P-256 with AES-256-GCM, 42-byte ciphertext, 16-byte tag) is recorded as off-chain and touches no contract.

Two observations follow, and both are findings rather than targets. First, the createDID cost exceeds the specification's ERC-1056 target (<100K) by 62–79K gas; the cause, recorded in the sandbox findings, is the explicit-DID storage the uniform interface requires, which the reference ERC-1056 registry avoids by treating addresses as implicit identities. Interface uniformity has a measurable price on the lightest standard, and that price is a placement cost — state written that the native pattern would have left implicit. Second, the only Set B function whose gas approaches a Set A write is issueCredential, and the whole of its cost is anchoring: the hash, the bound, the event. Every byte of credential *content* costs nothing on-chain because it is not there. This is the placement decision the remaining EVM options must be measured against, and the columns for O2–O8 in Table 4.5 are pending the WO-1 through WO-3 ports (see 01 §7 for the pending column set).

Read-path cost is stated as a model rather than a measurement. For a verifier holding a cached DID document and revocation state of age *s*, a Tier 2 check of a presentation over *k* credentials requires *k* signature verifications and *k* anchor comparisons locally, zero chain reads if *s* is within the verifier's staleness bound σ, and one view per stale item otherwise. The design variable is σ; the measured quantity that would fix it, revocation-propagation latency on the target chain, is pending Stage 18. The vehicle identity layer built in this campaign (§4.6, pending 10) is the first evidence that this model can be instantiated above the interface without changing it: its credential-type and endorsement registries add writes whose gas is measured separately from the twelve functions, and its verifier performs exactly the local check described here, consulting the chain only for F6, F12 and endorsement state.

### 4.2 Chapter 5 §5.5 opening: "Family F as a data architecture"

Family F was introduced in Chapter 3 as the Stage 3 synthesis output: the minimum-cost composite achieving full IMinimalSSI compliance. Chapter 4's placement analysis (§4.5) changes what "composite" must mean. A composite of *contracts* — the DID registry of one option, the claim store of another, the presentation logic of a third — would inherit the placement of each part, and the parts disagree: ERC-735-style claims live on-chain, AnonCreds credentials live off-chain, ERC-1056 attributes live in the event log. Full coverage assembled that way would be coverage without a coherent answer to where a verifier looks or what it must trust. Family F is therefore specified in this thesis as a *data architecture*: a mapping from each data class of the identity system to a placement, a proof mechanism, a read path and a staleness bound, which any contract set that realises the mapping satisfies. It remains a Stage 3 output; no Family F sandbox exists or is proposed as a Stage 1 artefact.

The mapping is tiered. Identity roots and their key history — the controller of a DID, its verification methods, its delegates and their expiries, its deactivation — are on-chain state, because the accountability argument of Chapter 1 requires that their history be readable by anyone, later, without trusting an indexer. Credential existence, revocation state and presentation commitments are anchor-only: a hash and a flag, never content, because Chapter 4 §4.4 shows that content on-chain is a privacy liability under GDPR even when hashed, whereas a credential-definition hash and a revocation accumulator are not personal data. Credential content, presentations, proofs and channels are off-chain-native, signed or proven against the anchors. Endorsements — who may issue which type — are on-chain state, small, rarely written and cached beside revocation state, because they are a read-path primitive (Chapter 2 §2.5). Reputation attestations (Set C) are anchor-only with the evidence off-chain, for the same reason as credentials.

Three properties of this architecture are claims the thesis can defend now, and one is not. First, it is *realisable* on O1 today: every placement above is already the placement O1 uses in sandbox v1.3, and the endorsement and credential-type registries of the VID layer add the two missing classes without interface change (pending 10 for the measured cost of those additions). Second, its *Tier 2 read path requires no chain access* under a stated assumption: that the verifier's cached revocation and endorsement state is younger than its staleness bound; the design fails, and says so, for a credential revoked inside that window. Third, it *degrades* rather than fails under low connectivity: reads continue from cache, writes queue as signed intents and land as Tier 3 transactions when connectivity returns, with the ordering hazards that 03 §6 enumerates. What the thesis cannot yet claim is any *measured* Tier 2 latency, any cost for O2–O8, or any figure for the ZKP variant of the presentation path; those are Stage 18, WO-1 through WO-3, and Stage 19 respectively, and the sentences that would report them are written in §4.5 and §5.5 as pending.

---

## 5. Integration mechanics

### 5.1 Registry rows the campaign adds (S2 schema)

| Content Block | T | Source | Ch. | Ready % | Notes |
|---|---|---|---|---|---|
| Placement axis argument (four classes, read/write, Set A/B reframing) | A | HDA 11 §3; 01 §2–§5 | 2 (§2.5), 5 (§5.1) | 80 | Thesis prose; cites only S1 trace numbers |
| Endorsement argument (minimal trust-framework primitive, lineage, beside-not-inside) | A | HDA 11 §2 | 2 (§2.5), 3 (§3.1) | 80 | NEW-1..NEW-4 need S1 verification labels |
| Ch.4 §4.5 opening prose | A | HDA 11 §4.1 | 4 | 75 | O2–O8 columns pending WO-1–3; σ pending Stage 18 |
| Ch.5 §5.5 opening prose | A | HDA 11 §4.2 | 5 | 75 | Realisability claim gated on 10 |
| Per-function placement matrix, O1 | B | 01 §6 | 4 | 85 | Programmatic from trace; other options pending |
| Read-path cost model (formulas with σ, k, s) | B | 01 §7; 03 §4 | 4, 5 | 70 | No measurement; model only |
| Family F data-architecture specification (tiered mapping) | A | 03 | 5 (§5.5) | 70 | Stage 3 design; never a sandbox |
| Endorsement test series specification (G1–G4 assertions) | B | HDA 11 §2.4; 10 | 4 | 60 | Ready % rises when test/vid.js is green |
| MOBI VID conformance mapping with roles and endorsement column | B | HDA 11 §2.5; 10 | 3 (§3.3) | 65 | Re-expression of cv2x-testbed roles |
| Reputation-identity-endorsement chain (FL, cooperative perception) | A | 09 | 5 (§5.6) | pending 09 | Word count set by 09 |
| Ch.1 motivation additions (placement gap; who-may-issue) | A | HDA 11 §1.1 | 1 | 85 | <200 words |
| C16 proposal text | C | HDA 11 §1.6 | 1 (§1.3) | n/a | Decision owed |
| K-corrections K-HDA-1..K-HDA-7 | B | HDA 11 §5.2 | 2, 3, 4 | n/a | To S3 K-ledger |

### 5.2 K-corrections the campaign triggers in existing documents

These are numbered provisionally K-HDA-n; S3 renumbers them into the programme's K-ledger.

**K-HDA-1 (Family F as contract composition).** v11.3 §3.1 states that Family F is "assembled from the best-validated components of all five implementation families", and the registry's Ch.5 focus names a "Family F CVIN Combined specification". Correct to: Family F is a Stage 3 data-architecture specification (placement, proof, read path, staleness per data class) realisable over more than one contract set; it is never built as a Stage 1 sandbox.

**K-HDA-2 (gas targets stated as results).** v11.3 §4.4 states "createDID ≈ 75,000 gas for attribute set" as O1's cost profile. The 75K figure is the ERC-1056 reference registry's setAttribute cost (DIGEST-LEVEL) and is a *target*; the measured O1 createDID under the uniform interface is 161,823–178,935 gas. Correct the sentence and keep the Canadian-scale estimate as a formula in vehicles × gas × price, not as a dollar figure.

**K-HDA-3 (mixed O-numbering).** The thesis draft numbers options O1 ERC-1056, O2 ERC-1155, O3 ERC-721, O4 ERC-6551, O5 ERC-725, O6 ERC-725xy, O7 ERC-4337, O8 EIP-7702, O9 ERC-8004, O10–O17 Family E, O18 Family F; Table 4.1 additionally labels LFDT as "E2 O11". The sandbox numbers O1 ERC-1056 · O2 ERC-721 · O3 ERC-725 · O4 ERC-725xy · O5 ERC-1155 · O6 ERC-4337 · O7 ERC-8004 · O8 LFDT/Indy-on-Besu. Decide one scheme (§7.3); until then, every campaign document names the standard, and the thesis should too.

**K-HDA-4 (AnonCreds proof system).** v11.3 §2.3 says Family E satisfies createPresentation "through AnonCreds' Groth16-based proof generation"; §3.2 correctly says CL signatures [12]. AnonCreds v1 uses CL; Groth16 is the VehiclePassport and general zk-SNARK reference. Correct §2.3.

**K-HDA-5 (trace length).** The registry lists the O1 trace as an "18-step execution trace"; the committed file has 22 entries (one deploy, thirteen transactions, six views, one off-chain step, one summary). Correct the row.

**K-HDA-6 (Groth16 gas).** v11.3 §3.2 states "approximately 350,000 gas" for Groth16 verification as a fact. Label DIGEST-LEVEL with a range (≈200–350K) and a source; 02 carries the citation.

**K-HDA-7 (endorser requirement as LFDT-only).** v11.3 §4.4 attributes Sybil resistance to "endorser requirements for DID creation in LFDT options" and to gas in EVM options. After this campaign, endorsement is a cross-family property available beside any option; reword so that Indy is the *native* instance, not the only one.

### 5.3 Narrowed-claim sentences (K14 style) for what is not yet measured

For each claim the campaign makes that depends on evidence not yet produced, the thesis carries the narrowed form until the evidence exists:

- *Realisability of the VID layer.* "A credential-type and endorsement layer has been designed to sit above IMinimalSSI on O1 without interface change; its compliance and gas are reported in §4.6 once the build's traces exist." (Replaces any sentence asserting the layer *works*.)
- *Tier 2 read path.* "Under the stated caching assumption, the Tier 2 read path requires no chain access; the revocation-propagation latency that fixes the staleness bound is pending Stage 18." (Replaces any latency figure.)
- *Cross-option placement.* "The placement and path-cost columns for O2–O8 are pending WO-1 through WO-3; the argument of §2.5 is made on O1 and on the standards' documented designs." (Replaces any cross-option comparison stated as measured.)
- *ZKP presentation cost.* "On-chain proof verification costs are cited at digest level from the literature; no proof has been generated or verified in this evaluation. Pending Stage 19." (Replaces the 350K sentence.)
- *Endorsement gating.* "The endorsement test series is specified in §4.5; its pass/fail record on O1 is pending 10." (Replaces any claim that gating *has been* verified.)
- *Scale.* "At *N* vehicles and measured gas *g* per operation, annual anchoring cost is *N·f·g·p* for operation frequency *f* and gas price *p*; no dollar figure is claimed." (Replaces the §4.4 dollar range.)

### 5.4 Demonstration evidence: today versus after the build

What the defence can show today, from committed artefacts: the O1 sandbox compiling and passing the 12-test suite; the S1 trace with 12/12 coverage and the gas table above; the createDID deviation and its recorded cause; the placement matrix for O1 derived from that trace; the EndorsementRegistry and CredentialTypeRegistry *designs* (interfaces, policy, test assertions) as documents; the S7/S8 scenario *designs*; and the existing `cv2x-testbed/` MOBIVIDRegistry lifecycle as the baseline the VID layer re-expresses.

What it can show only after 10 reports: the endorsement test series green beside the untouched suite; S7 and S8 traces with G1–G4 entries and measured governance gas; a side-by-side of the same lifecycle on the purpose-built registry and on the generic interface plus endorsement; and, if WO-1 through WO-3 land, the same layer running unchanged on a second option, which is the strongest single piece of evidence for the "beside, not inside" argument.

---

## 6. Academic positioning

### 6.1 Related work the argument must engage

The placement argument stands on Mühle et al. [2], whose identifier-registry / claim-registry split is the ancestor of Set A / Set B; the thesis should say explicitly that its placement classes refine that split by asking, for each registry, *what* is registered (state, log, anchor) rather than only *that* it is. Dunphy [22] adapts the blockchain trilemma to decentralised identity from Indy experience; the thesis engages it by showing that the trilemma's tension is largely a placement tension (what must be on-ledger for decentralised verification versus what must not for privacy and scale) and that the hybrid's answer is to put anchors, not content, on-ledger. Kortesniemi et al. [17] evaluate DID methods on governance and recovery; the endorsement registry answers the governance risk they identify for did:ethr without altering the registry contract. The GDPR treatment must engage the hash-as-personal-data guidance (the European Data Protection Board's blockchain guidelines of 2025 and the earlier EU Blockchain Observatory reports; DIGEST-LEVEL, not read at source; NEW-5) to justify the anchor-only rule that per-credential content hashes are minimised or salted while definition hashes and accumulators are public. Trust over IP (NEW-3) and eIDAS 2.0 trusted lists (NEW-4) position endorsement as the on-chain instance of governance-layer constructs already deployed at continental scale, which is the strongest external warrant for calling it minimal. ERC-8004 [19] provides the agent-side instance and the reputation and validation registries that 09 builds on; Rodriguez Garzon et al. [11] supply the peer-reviewed agent-DID model the I2I chapter already cites. Flamini et al. [13] and RFC 9901 [14] remain the selective-disclosure spine, carried by 02.

### 6.2 Sentence-level claims the thesis can defend after this campaign

1. The EVM/LFDT divergence and the createPresentation gap are instances of one design axis, data placement, and F8 is the function whose proof lies across the placement boundary EVM standards optimised for. (Defensible now: argument plus O1 trace.)
2. Set A is the on-chain-state and event-log set; Set B is the anchor-only set; the decomposition derived from Allen's principles coincides with the decomposition by placement. (Defensible now.)
3. Interface uniformity has a measurable placement cost on the lightest standard: 62–79K gas above the createDID target on O1, caused by explicit-DID storage. (Defensible now; measured.)
4. Tier 2 viability is a read-path property; under a stated staleness assumption the Tier 2 identity path requires no chain access. (Defensible as a design claim now; as a measured claim after Stage 18.)
5. An issuer registry with endorsement is the minimal trust-framework primitive the twelve functions presuppose; it is orthogonal to Allen coverage and belongs beside the interface. (Defensible now: argument plus lineage.)
6. The MOBI VID I–II lifecycle, including its eight issuer roles, can be expressed as IMinimalSSI plus endorsement without a purpose-built registry. (Defensible as a design now; as evidence after 10.)
7. Family F is a data architecture realisable over more than one contract set, not a contract composition. (Defensible now as a definition; its minimum-cost property after WO-1 through WO-3 and Stage 3.)
8. Reputation for collective computation requires identity, identity requires endorsement to bound Sybil cost, and both are placement decisions (anchor-only attestations, on-chain endorsements). (Defensible after 09 is integrated.)

---

## 7. Writing plan

### 7.1 Order and budgets

| Order | Section | Words | Gate |
|---|---|---|---|
| 1 | Ch.2 §2.5 Data placement as an evaluation axis (from §3 here) | 1,400 | none; O1 trace only |
| 2 | Ch.2 §2.5 second half / Ch.3 §3.1 endorsement (from §2 here) | 1,200 | S1 labels on NEW-1..4 |
| 3 | Ch.4 §4.5 opening and placement table | 900 | 01 final; O2–O8 columns marked pending |
| 4 | Ch.3 §3.3 VID conformance with roles | 500 | 10 for status column |
| 5 | Ch.5 §5.5 Family F as data architecture | 900 | 03 final |
| 6 | Ch.5 §5.6 Reputation and collective computation | set by 09 | 09 final |
| 7 | Ch.1 additions and C16 decision text | 300 | researcher decision |
| 8 | K-corrections applied; narrowed sentences inserted | — | S3 ledger |

Items 1, 2 and 7 have no build dependency and can be written this week. Items 3–6 are gated on their source documents; item 3 is the only one gated on a *measurement* (pending columns are acceptable, but the O1 column must come from the trace, not from this document).

### 7.2 Which support documents gate which prose

S1 (Weighted Reference Index) gates every sentence that cites NEW-1 through NEW-5: until S1 assigns a verification state, the lineage paragraph (§2.2) carries DIGEST-LEVEL labels inline and the thesis may not cite the Indy role model, ERC-740, ToIP or eIDAS trusted lists as verified. S2 gates nothing directly but must carry the rows of §5.1 before the registry's chapter-coverage analysis is updated. S3 gates the application of K-HDA-1 through K-HDA-7 to the existing draft; corrections are applied only after they are ledgered. 10 gates every sentence about the VID build beyond "designed"; 01 and 03 gate the tables in §4.5 and §5.5 respectively.

### 7.3 Load-bearing decisions before prose is frozen

1. Whether C16 is a separate contribution or is folded into C4 and C12 (§1.6).
2. Which O-numbering the thesis adopts (K-HDA-3); the sandbox scheme is the one traces are tagged with.
3. Whether endorsement semantics are issuance-time (an endorsement valid when the credential was issued suffices, as this document assumes) or presentation-time (it must also hold when verified); the test series and the VID policy differ under the two.
4. Whether the placement matrix becomes a formal Chapter 4 table beside the coverage matrix, or a Chapter 5 discussion device.
5. Whether §5.6 (reputation) is a Chapter 5 section or is deferred to the I2I bridging paper (C15).

---

## Sources used in this document

| Ref | Source | Verification state | How used |
|---|---|---|---|
| [1] | Allen, The Path to SSI, 2016 | VERIFIED AT SOURCE (thesis list) | Orthogonality argument (§2.3) |
| [2] | Mühle et al., Computer Science Review 2018 | VERIFIED AT SOURCE (thesis list) | Identifier/claim registry split; trust-establishment component (§2.2, §6.1) |
| [5] | Prakash, Michelson, Feng, CVIN, VTC2020-Spring | VERIFIED AT SOURCE (thesis list) | Lineage; Ch.1 additions |
| [6] | Brecht et al., SCMS, IEEE T-ITS 2018 | VERIFIED AT SOURCE (thesis list) | Accountability gap as placement gap (§1.1) |
| [8] | W3C DID Core 1.0 | VERIFIED AT SOURCE (thesis list) | Set A basis |
| [9], [10] | W3C VC Data Model 1.1 / 2.0 | VERIFIED AT SOURCE (thesis list) | Issuer trust as out-of-band policy (§2.3) |
| [11] | Rodriguez Garzon et al., ICAART 2026 | VERIFIED AT SOURCE (thesis list) | Agent-side positioning (§6.1) |
| [12] | Camenisch & Lysyanskaya, CRYPTO 2004 | VERIFIED AT SOURCE (thesis list) | K-HDA-4 |
| [13] | Flamini et al., JISA 2024 | VERIFIED AT SOURCE (thesis list) | Selective-disclosure spine (§6.1) |
| [14] | SD-JWT RFC 9901 | VERIFIED AT SOURCE (thesis list) | Selective-disclosure spine |
| [17] | Kortesniemi et al., DID methods evaluation | VERIFIED AT SOURCE (thesis list) | did:ethr governance risk (§2.2, §6.1) |
| [19] | De Rossi et al., ERC-8004 | VERIFIED AT SOURCE (thesis list) | Validation/reputation registries (§2.2, §6.1) |
| [22] | Dunphy, blockchain trilemma for decentralised identity | VERIFIED AT SOURCE (thesis list) | Indy endorser layer; trilemma as placement (§2.2, §6.1) |
| [23] | ERC-1056 | VERIFIED AT SOURCE (thesis list) | O1 pattern; 75K reference cost (DIGEST-LEVEL figure) |
| [27] | MOBI VID I–II | VERIFIED AT SOURCE (thesis list) | Conformance mapping roles (§2.5) |
| — | SSI Minimal Function Specification (Formal), §2.3, §5.3, §6, App. B | VERIFIED AT SOURCE | Derivation criteria; gas targets; governance extension; coverage matrix |
| — | Thesis Narrative Synthesis v11.3; Content Block Registry v11.3 | VERIFIED AT SOURCE | Chapter map; K-corrections |
| — | `traces/i2i_O1_ERC1056_1780620182135.jsonl` (22 entries) | VERIFIED AT SOURCE | All measured gas and step counts |
| — | Context Brief §5 | VERIFIED AT SOURCE | Measured table; DIGEST-LEVEL external figures |
| NEW-1 | Hyperledger Indy ledger roles (trustee, steward, endorser; former trust anchor) | DIGEST-LEVEL; not read at source | Lineage (§2.2) |
| NEW-2 | ERC-735 claim holder / ERC-740 claim-issuer registry drafts | DIGEST-LEVEL; not read at source | Lineage (§2.2) |
| NEW-3 | Trust over IP governance stack | DIGEST-LEVEL; not read at source | Lineage; positioning (§2.2, §6.1) |
| NEW-4 | eIDAS trusted lists; eIDAS 2.0 / EUDI attestation providers | DIGEST-LEVEL; not read at source | Lineage; positioning |
| NEW-5 | EDPB blockchain guidelines 2025; EU Blockchain Observatory GDPR reports | DIGEST-LEVEL; not read at source | Hash-as-personal-data rule (§6.1) |
| — | Groth16 on-chain verification ≈200–350K gas | DIGEST-LEVEL (brief §5) | K-HDA-6 only |

## Registry delta rows

The thirteen rows of §5.1 are the S2 delta for this document; they are not repeated here. Two administrative rows are added: "HDA 11 Thesis Integration (this document)" · A · HDA campaign · Ch. 1–5 · 80% · primary integration map; and "C16 decision record" · C · researcher · Ch. 1 · n/a · pending decision.

## Open questions for the researcher

1. **C16.** Accept as a sixteenth contribution, or fold into C4 (mapping realised by the reference layer) and C12 (composite governed by endorsement)? The prose of Ch.1 §1.3 cannot be frozen until this is decided.
2. **Endorsement time semantics.** Issuance-time (assumed here) or presentation-time? This changes the VID verification policy, the test series, and whether an endorsement revocation retroactively invalidates credentials — a policy with legal consequences for driver's licences and registrations that only the researcher can set.
3. **O-numbering.** Thesis scheme or sandbox scheme? Traces are tagged with the sandbox scheme; changing the thesis is cheaper than re-tagging evidence, but the thesis scheme is what the supervisors have read.
4. **Placement matrix status.** Formal Chapter 4 table with the same programmatic-extraction rule as the coverage matrix (no hand entry), or a Chapter 5 discussion device? The former is stronger but commits WO-5 to a second extractor.
5. **Scope of the GDPR claim.** Should the thesis assert that salted per-credential hashes are *not* personal data (a legal position), or only that the architecture *minimises* on-chain personal data (a design position)? The second is defensible with DIGEST-LEVEL sources; the first needs a source read at source and possibly legal advice.
