CVIN-SC Research Programme · UBC Electrical and Computer Engineering

**Zero-Knowledge Proofs and Verifiable Data in a Hybrid Identity Architecture**

**Selective disclosure, unlinkability, predicate and non-revocation proofs, verification placement, revocation privacy, cost, and a staged build plan for connected vehicles and AI agents**

Document 3 of 16 · Hybrid Data Architecture (HDA) Campaign · Primary deliverable · Suite v1.0 · September 2026 · General pass (angle passes follow)

**Nikhil Prakash** · MASc Candidate, Electrical and Computer Engineering, The University of British Columbia · Supervisors: Dr. Chen Feng (UBC Okanagan, Blockchain@UBC), Dr. David G. Michelson (UBC Vancouver)

Companions: 00 Master Plan · 01 On/Off-Chain Data Architecture · 02 ZKP and Verifiable Data · 03 Best-of-Both-Worlds Hybrid Design · 04 Full-Coverage Scenarios · 05 Latency-Tier Scenarios · 06 Reputation/Payment/Gated-Access/Low-Connectivity Scenarios · 07 Beyond-CAV Back-End Scenarios · 08 I2I Secure Communication · 09 Reputation, Identity and Federated Learning · 10 VID Build Documentation · 11 Thesis Integration · S1 Weighted Reference Index · S2 Registry Delta · S3 Change Log and Meta Commentary · 99 Chat Primers

*Registry classification: Type A prose → Chapter 4, Stage 19 (C10 ZKP and selective-disclosure analysis); Chapter 5, §5.1 (createPresentation as structural insight)*

> **Post-build note (2026-10-04).** This document was drafted before the VID layer was executed. Scenarios S7 and S8 have since run and produced traces; where the text below says that only the S1 trace is measured, or labels S7/S8 quantities as pending, read it together with document 10 §5 (measured gas for F1–F12, G0–G4, T1–T2; the 11:1 Merkle-batch result; findings F-VID-1 to F-VID-7) and the reconciliation table in S3 §3. Canonical scenario identifiers are fixed in document 00 §6; where this document uses a different S-number for a proposed script, the register in 00 governs.

---

## 0. How to read this document

This document is the campaign's treatment of the second half of the thesis's central question: not only *where identity data lives* (01) but *how identity claims are proven* without disclosing more than the verifier needs. It argues one thesis-level claim and then works it through mechanisms, placement, applications, revocation, integrity, threats, cost, and a build plan. The claim is this: **in a system whose specification already deliberately confines credential content off-chain and anchors only hashes (F5), zero-knowledge and selective-disclosure proofs are not a privacy feature bolted on afterwards but the only way the specification's own verification path (F6, F8) can be exercised at Tier 2 without turning the anchoring layer into a correlation log.** Everything that follows is evidence for, or a test of, that claim.

Numbers are handled under the campaign's rule (brief §9.1). The only measured numbers in this document come from the sandbox v1.3 trace `traces/i2i_O1_ERC1056_1780620182135.jsonl`, which the author read for this document. All external figures carry the label DIGEST-LEVEL (widely reported, source named, not re-derived here) or UNVERIFIED (source named, not read at source). Design quantities are formulas with variables or stated targets, never results. Every element of the build plan in §10 is **pending**.

## 1. Why ZKP is not an add-on in this thesis

### 1.1 The claim

The thesis's central empirical finding is that no Ethereum Virtual Machine (EVM) identity standard natively implements `createPresentation` (F8); EVM standards optimise identity anchoring (Set A) and defer selective disclosure to off-chain middleware, whereas the LFDT/AnonCreds lineage implements native zero-knowledge presentations off-chain and anchors only credential definitions and revocation accumulators [25]. The sandbox declares and *anchor-implements* F8 — challenge-bound and replay-protected, 62,441 gas measured on O1 — but the anchor records only a commitment to a presentation, not the presentation's disclosure semantics. That gap is not an omission in the standards; it is the boundary of what a public ledger can do. The moment one asks what a presentation *is* rather than *that* it happened, the question becomes cryptographic, and the cryptography is the subject of this document.

### 1.2 Four pressures that converge on the same requirement

**The createPresentation gap.** F8's signature, `createPresentation(bytes32 holder, bytes32[] credentialIds, bytes32 challenge, string domain) → bytes32 presentationId`, takes the *holder's DID* and the *credential identifiers* as arguments and emits `PresentationCreated(presentationId indexed, holder indexed, challenge)`. Read literally as the presentation mechanism, every Tier 2 interaction would write the holder's DID and the credential set it presented into an indexed, permanent event log. The sandbox uses F8 correctly — as an anchor for a challenge that an off-chain channel later binds to (S1 trace seq 15–16: the presentation commitment anchors the ECDH/AES-GCM payload) — but a naive reading of the specification is the linkability problem in its purest form. This document's §3 resolves how F8 anchoring and unlinkable presentation coexist.

**Allen's Consent and Minimization.** Two of the ten principles in [1] are directly cryptographic obligations. *Minimization* — "disclosure of claims must be minimized" — is satisfied only by a mechanism that lets a holder reveal a predicate ("over 18", "licence class C valid today") rather than an attribute. *Consent* requires that the holder, not the issuer or the verifier, decide what is disclosed at each presentation. A credential whose entire content is signed as one blob fails both unless the verifier is trusted to look away; the thesis's Chapter 2 compliance scoring treats these principles as testable, and this document supplies the test.

**The SCMS linkability problem.** The Security Credential Management System (SCMS) of IEEE 1609.2 [6], [28] issues short-lived pseudonym certificates so that basic safety messages (BSMs) at Tier 1 cannot be trivially chained into trajectories; two linkage authorities hold the linkage values that reconnect the pseudonyms for misbehaviour revocation. That design is the thesis's model for "privacy by default, accountability on demand". The accountability gap the thesis names is that SCMS pseudonymity precludes answering "what is the history of actions taken by vehicle V?" for Tier 2/3 purposes. The extension the thesis proposes must therefore reproduce SCMS's unlinkability property *at the Tier 2 credential layer* — otherwise the DID layer re-introduces exactly the trajectory correlation SCMS was designed to prevent — while adding the forensic history SCMS lacks. Reproducing unlinkability above SCMS is a ZKP problem.

**Data minimisation as law.** The General Data Protection Regulation's data-minimisation principle (Art. 5(1)(c)) and privacy-by-design obligation (Art. 25) (NEW-1, DIGEST-LEVEL) make disclosure of a full credential when a predicate would suffice a compliance defect, not merely a design choice. The Building Paths preface already records the consequence for anchoring: per-credential content hashes may themselves be personal data, whereas credential-definition hashes and accumulators are safely public. That distinction, as §6 shows, is itself an argument for accumulator-based revocation.

### 1.3 Definitions used throughout

The following five properties are distinct, and the mechanism landscape in §2 is best read as a matrix of which mechanism offers which.

*Selective disclosure* is the ability of a holder to reveal a subset of the claims in a credential while the verifier can still check that the revealed subset was signed by the issuer. It says nothing about whether two presentations can be correlated.

*Unlinkability* is the property that two presentations from the same credential cannot be recognised as coming from the same credential (or holder) by verifiers who compare notes — *multi-show unlinkability* — and, in its stronger form, that even the issuer cannot recognise a presentation of a credential it issued — *issuer unlinkability*. Unlinkability is always relative to what is disclosed: a presentation that reveals a VIN is linkable by the VIN regardless of the signature scheme.

*Predicate proofs* prove that a hidden attribute satisfies a relation — a range (`odometer ≤ 80,000`), an inequality with the current date (`validUntil ≥ today`), set membership (`jurisdiction ∈ {BC, AB}`) — without revealing the attribute.

*Non-revocation proofs* prove that a credential is not in the issuer's revoked set at a stated time without revealing which credential it is. This is the property that distinguishes a status list (verifier looks up a specific index) from an accumulator (holder proves membership in the accumulated non-revoked set).

*Proof of possession* proves that the presenter controls the key the credential was bound to, so that a stolen credential cannot be replayed. In the sandbox this is the challenge/domain binding of F8 and the holder signature over the verifiable presentation (VP); in anonymous-credential systems it is a proof of knowledge of a hidden link secret.

A sixth term is used in §7: *attestation of computation* (a proof that a stated function was correctly evaluated on stated inputs) as opposed to *attestation of data* (a signature or hash that data has not changed). ZK proofs can do the former; signatures and anchors can only do the latter.

## 2. The mechanism landscape

### 2.1 Method of comparison

Each mechanism is assessed on the same eleven axes: what it proves; proof size; prover cost; verifier cost off-chain; verifier cost on-chain; trusted setup; quantum posture; standardisation maturity; tooling; linkability properties; and the specific role it can play in the CVIN-SC hybrid. Where a figure is an order-of-magnitude figure from the literature it is marked DIGEST-LEVEL with the source. None of the figures below were measured in the sandbox; §10 states what will be.

### 2.2 Hash-based selective disclosure (SD-JWT and salted digests)

*What the repository already has.* `2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py` implements an SD-JWT-style scheme: when `selective_disclosure=True` the issuer replaces each claim with `sha256(salt ‖ name ‖ canonical({"v": value}))`, with a fresh 16-byte salt per claim, and signs the credential containing only the `claimDigests` map (EIP-191 secp256k1 Data Integrity proof over canonical JSON). The holder receives the `{claim: {value, salt}}` disclosure map; `vc_holder.py` builds a VP that includes only the requested `disclosedClaims`, and the verifier recomputes each digest against the issuer-signed map. This is the mechanism RFC 9901 [14] standardised in November 2025, with two differences that matter for the analysis: the repository keys the digest map by claim *name* (RFC 9901 places unordered digests in an `_sd` array and permits decoy digests), so the *set of claim names* and their count are visible even when values are hidden; and the repository's key binding is the holder's EIP-191 signature over the VP, whereas RFC 9901 defines a Key Binding JWT. Neither difference changes the security argument; the first slightly weakens minimisation (the schema is revealed) and is trivially fixed.

*What it proves.* Selective disclosure and proof of possession. Nothing else.

*Costs.* Proof size is the credential plus one (value, salt) pair per disclosed claim — hundreds of bytes to a few kilobytes. Prover cost is nil (no computation beyond selecting disclosures and one signature). Verifier cost is one hash per disclosed claim plus two signature verifications, sub-millisecond on any platform. On-chain verification of a disclosure is possible in principle (`keccak256`/`sha256` precompile plus `ecrecover`, on the order of tens of thousands of gas — DIGEST-LEVEL from EVM opcode pricing, NEW-2) but there is rarely a reason to do it; the disclosed *values* would enter calldata and thus the public record.

*Setup, quantum, maturity, tooling.* No trusted setup. Post-quantum posture is that of the signature scheme; the digest construction itself is hash-based and survives, so SD-JWT with a post-quantum signature is the simplest quantum-safe selective disclosure available. Standardisation is the most mature in the landscape: RFC 9901, the SD-JWT VC profile in the IETF OAuth working group (NEW-3, DIGEST-LEVEL), and adoption in the EU Digital Identity Architecture Reference Framework (NEW-4, DIGEST-LEVEL). Tooling exists in every mainstream language.

*Linkability.* Fully linkable. The issuer's signature value, the digest map, and the holder key are all constant across presentations; two verifiers who compare notes, or a verifier and the issuer, link every presentation of the credential trivially. In the repository's form, `credentialSubject.id` — the holder DID — is present in the signed credential and therefore in every presentation. SD-JWT is selective disclosure *without* unlinkability, and the only mitigations are batch issuance of many single-use credentials (which pushes the linkability problem to issuance and costs an F5 anchor per credential, 130,163 gas measured on O1 if each is anchored individually) or pairwise DIDs per verifier (the 2020 paper's dual-mode identity [5], which limits linkability to one verifier's view).

### 2.3 BBS+ signatures

*What it is.* A pairing-based multi-message signature scheme (Boneh–Boyen–Shacham lineage, formalised for anonymous credentials by Au, Susilo and Mu and later by Camenisch, Drijvers and Lehmann; NEW-5, DIGEST-LEVEL) over BLS12-381 in current standardisation. The issuer signs a vector of messages with one short signature; the holder later derives a *fresh, randomised* proof of knowledge of that signature that reveals any chosen subset of messages and hides the rest. Standardised in the IETF CFRG BBS Signature Scheme draft (NEW-6, DIGEST-LEVEL) and bound to W3C Data Integrity as the `bbs-2023` cryptosuite (NEW-7, DIGEST-LEVEL, W3C Candidate Recommendation track). AnonCreds v2 is moving to BBS+ from CL signatures (NEW-8, DIGEST-LEVEL).

*What it proves.* Selective disclosure and multi-show unlinkability, with proof of possession via a hidden holder-bound message (the AnonCreds "link secret" pattern). Predicate proofs are not native; range proofs require an additional ZK component (Bulletproofs or a SNARK) composed with the BBS+ proof of knowledge — AnonCreds v2 is adding this composition (NEW-8, DIGEST-LEVEL).

*Costs.* Signature: two group elements, roughly 80–112 bytes compressed (DIGEST-LEVEL, NEW-6). Proof size grows linearly in the number of *undisclosed* messages (one scalar each) plus a constant of a few group elements — hundreds of bytes for a ten-claim credential (DIGEST-LEVEL). Prover cost: one multi-scalar multiplication over the undisclosed messages, single-digit to tens of milliseconds on a laptop and reported in the tens-to-hundreds of milliseconds range on constrained ARM devices in the literature surveyed by [13] (DIGEST-LEVEL); the OBU figure is a §10 measurement target. Verifier cost off-chain: two pairings plus a multi-scalar multiplication, low single-digit milliseconds on a laptop (DIGEST-LEVEL). On-chain verification: BLS12-381 pairing precompiles landed in the EVM with EIP-2537 (NEW-9, DIGEST-LEVEL); a BBS+ proof verifier on EVM is uncommon and the gas has not been measured by this programme — UNVERIFIED, not to be cited as a number.

*Setup, quantum, maturity, tooling.* No trusted setup (public parameters are generators derived by hashing). Not post-quantum (pairing-based). Maturity: IETF draft and W3C CR-track; production use in MATTR's platform and in the AnonCreds v2 effort. Tooling: `@mattrglobal/bbs-signatures` (JavaScript/WebAssembly over a Rust core) and `pairing_crypto` (Rust) (NEW-10, DIGEST-LEVEL); `anoncreds-rs` for the AnonCreds v2 path.

*Linkability.* The signature itself is never shown; each presentation is a fresh randomisation, so verifiers cannot link presentations by cryptographic material and the issuer cannot recognise its own signature. Linkability then depends only on what is disclosed and on transport metadata (§8). This is the property the thesis needs at Tier 2, and it is why BBS+ is the pivot of the build plan in §10(b).

### 2.4 CL signatures and AnonCreds v1 (with the v2 transition)

*What it is.* Camenisch–Lysyanskaya signatures [12] over RSA groups underpin AnonCreds v1 as used in Hyperledger Indy: the issuer signs the attribute vector; the holder proves knowledge of the signature in zero knowledge, disclosing a subset, and proves predicates (`p_gte`, `p_lte`, `p_gt`, `p_lt`) over integer attributes; non-revocation is proven against a bilinear accumulator published in a revocation registry on the ledger (§6). This is the "AnonCreds is the Set B coverage ceiling (12/12)" finding of the thesis: every Set B function has a native, privacy-preserving realisation.

*Costs.* Keys and signatures are large — issuer public keys of kilobytes per attribute and proofs of several kilobytes (DIGEST-LEVEL, [12], [13], [22]). Prover cost is hundreds of milliseconds to seconds on constrained devices (DIGEST-LEVEL; the thesis's own AnonCreds-on-Besu timing is a §10(d) measurement, not yet made). Verifier cost off-chain is tens of milliseconds (DIGEST-LEVEL). On-chain verification is not attempted in any deployment the author knows of; RSA-group arithmetic in the EVM is prohibitively expensive without a `modexp`-based special-purpose verifier (UNVERIFIED as to cost).

*Setup, quantum, maturity, tooling.* No trusted setup beyond per-issuer key generation (though the RSA modulus must be generated honestly). Not post-quantum. Maturity: deployed at scale in Indy networks and in Canadian provincial credentials (British Columbia's Verifiable Organizations Network is the canonical example, NEW-11, DIGEST-LEVEL); AnonCreds specification v1.0 under Linux Foundation Decentralized Trust (LFDT). Tooling: `anoncreds-rs` (Rust with Python/JS bindings), ACA-Py and Credo-TS agents; Aries was archived in April 2025 and the work continues under LFDT.

*Linkability.* Multi-show and issuer unlinkable, as BBS+, plus native predicates and non-revocation. The price is proof size and prover time, which is precisely why v2 is moving to BBS+ [NEW-8].

### 2.5 zk-SNARKs (Groth16, PLONK) and zk-STARKs

*What they are.* General-purpose succinct arguments: a prover shows that it knows a witness satisfying an arithmetic circuit (R1CS for Groth16, PLONKish gates for PLONK/Halo2, AIR for STARKs). Anything computable can be a predicate over a credential: a range proof, a Merkle-membership proof, a signature verification (expensive), a hash pre-image, or the correct execution of a small program. Groth16 (NEW-12, DIGEST-LEVEL) has the smallest proofs and cheapest verifier but needs a per-circuit trusted setup; PLONK (NEW-13, DIGEST-LEVEL) has a *universal* setup reusable across circuits at some verifier cost; STARKs (NEW-14, DIGEST-LEVEL) need no setup and rest on hashes only, at the cost of proof size.

*Costs.* Groth16 proof: three group elements on BN254, on the order of 128–256 bytes depending on compression (DIGEST-LEVEL, NEW-12). Verifier: three pairings plus a multi-scalar multiplication over public inputs; **on-chain ≈200–350K gas** (DIGEST-LEVEL; the thesis draft uses ~350K; the lower bound reflects EIP-1108 precompile repricing, NEW-15). Off-chain verification: single-digit milliseconds (DIGEST-LEVEL). Prover cost scales with constraint count: a few hundred constraints for a 32-bit range check, tens of thousands for a Poseidon-hashed Merkle path of depth 20, tens of thousands *per block* for SHA-256, and on the order of a million or more for an in-circuit ECDSA verification (DIGEST-LEVEL, from circomlib and community circuit benchmarks, NEW-16). This is why §10(c) designs the circuit to keep the issuer's signature *outside* the circuit. PLONK proofs are several hundred bytes to about a kilobyte and on-chain verification is commonly reported higher than Groth16 (DIGEST-LEVEL, NEW-13; no figure asserted). STARK proofs are tens to hundreds of kilobytes; on-chain verification runs to millions of gas unless proofs are recursively wrapped in a SNARK, which is what production STARK-based rollups do (DIGEST-LEVEL, NEW-14). VehiclePassport (arXiv:2509.06133) reports 22 ms proof generation and sub-5 ms verification for vehicular attribute proofs (DIGEST-LEVEL, NEW-17), which is the nearest published reference point to the §10(c) target.

*Setup, quantum, maturity, tooling.* Groth16: per-circuit trusted setup (two phases; the Powers-of-Tau ceremony is reusable, phase 2 is circuit-specific). PLONK: universal setup. STARK: none. Quantum posture: SNARKs over pairings are not post-quantum; STARKs are (hash-based). Maturity: production in rollups and privacy protocols; no identity-specific standard, though the W3C VC Data Integrity model can carry a SNARK proof as a custom cryptosuite. Tooling: `circom` + `snarkjs` (Groth16/PLONK, Solidity verifier export), `noir` (Aztec's language with Barretenberg/UltraPLONK backend and Solidity verifier export), `gnark` (Go), `halo2`, `arkworks` (NEW-16, DIGEST-LEVEL).

*Linkability.* A SNARK proof reveals nothing beyond its public inputs and is fresh per proof, so unlinkability is entirely a matter of *what is made public*. If the public input is a per-credential commitment, the proof is linkable by that commitment; if it is a Merkle root of many commitments (Semaphore pattern, §2.6) or an issuer public key with the signature verified in-circuit, it is unlinkable. Circuit design, not the proof system, determines linkability.

### 2.6 Semaphore-style group membership

*What it is.* Semaphore (NEW-18, DIGEST-LEVEL) is a Groth16 circuit and Solidity verifier in which a member proves, without revealing which member, that their identity commitment is a leaf of a Merkle tree (the group), and emits a *nullifier* derived from their secret and an external scope so that the same member cannot signal twice in the same scope. Tree depth 20 (about a million members) is the common configuration; proof generation in the browser is reported in the low seconds and on-chain verification is in the Groth16 range plus nullifier storage (DIGEST-LEVEL, NEW-18).

*Role here.* It is the natural primitive for "member of fleet X" (depot access), "registered in jurisdiction J" (Local CVIN gate), and "agent authorised by principal P" without revealing which vehicle or agent. The on-chain nullifier gives a Sybil-resistance property that pure BBS+ presentations do not: one signal per scope, which matters for reputation and federated learning (09). Its weakness is group management: adding or removing a member changes the root, and a removed member's old proofs remain valid against old roots unless the verifier insists on the current root — which is the revocation staleness question of §6 in another guise.

### 2.7 Accumulator-based non-revocation (RSA and bilinear)

*What it is.* A cryptographic accumulator represents a set by one short value; each member holds a *witness*; a membership proof can be made in zero knowledge. RSA accumulators (Camenisch–Lysyanskaya 2002, NEW-19, DIGEST-LEVEL) use a strong-RSA modulus; bilinear accumulators (Nguyen 2005, NEW-20, DIGEST-LEVEL) use pairings and are what AnonCreds v1 revocation registries use. Revocation removes an element; every remaining holder must update its witness (the "tails file" in Indy, which pre-publishes the values needed for updates and is large — megabytes for registries of tens of thousands of credentials, DIGEST-LEVEL, NEW-8).

*Costs.* Accumulator value: one group element. Witness: one group element. Non-revocation proof: a few group elements plus the ZK proof of knowledge, hundreds of bytes (DIGEST-LEVEL). Prover cost: a witness update is a scalar multiplication per revocation event since last update; a fresh proof is a small constant. Verifier: a pairing check. On-chain: the accumulator value is the only thing anchored — 32 to 96 bytes per update, a single SSTORE (20,000 gas for a new slot, DIGEST-LEVEL, NEW-2) or one overwrite — which is *cheaper* than a per-credential F7 revocation (32,980 gas measured on O1) once revocations are batched.

*Setup, quantum, maturity.* RSA accumulators need an honestly generated modulus (trusted setup unless class groups are used); bilinear accumulators do not. Neither is post-quantum. Maturity: deployed in AnonCreds; no W3C profile.

*Linkability.* This is the point of accumulators: the verifier never learns which credential index was checked. §6 develops the trade with status lists.

### 2.8 Status-list revocation

*What it is.* W3C Bitstring Status List v1.0 (NEW-21, DIGEST-LEVEL) publishes a compressed bitstring (minimum 131,072 entries, roughly 16 KB uncompressed and much smaller compressed) as a signed credential; each issued credential carries `credentialStatus` with an index into the list. The repository's `RevocationRegistry` and `CvinRevocationRegistry2024` status entry is a registry-keyed precursor to this; the sandbox's F6/F7 is its on-chain form (per-credential revocation flag, 32,980 gas to set on O1; gas-free to read).

*Costs.* Verifier fetches the list (or, on-chain, calls F6 for free) and reads a bit. No prover cost. Proof size: nil beyond the status entry.

*Linkability.* Two distinct leaks. First, the verifier learns the credential's index, which is a stable correlator across all verifiers who see the same credential — status lists are compatible with SD-JWT's linkability level but destroy BBS+'s unlinkability unless the status index is itself hidden and proven in zero knowledge (which is a Merkle-membership SNARK over the list, §6). Second, the *issuer* observes which lists are fetched and when, which "herd privacy" (large lists, many credentials per list) mitigates but does not eliminate; on-chain F6 reads through a node the verifier controls remove the issuer-observation leak entirely, at the cost of the verifier needing chain access — the read-path question of 01.

### 2.9 Master comparison table

Abbreviations: SD = selective disclosure; UL-ms = multi-show unlinkability; UL-iss = issuer unlinkability; PP = predicate proofs; NR = non-revocation proof with privacy; PoP = proof of possession. All quantitative cells are DIGEST-LEVEL order-of-magnitude figures with sources named in §2.2–§2.8; "n/m" = not measured by this programme and not asserted.

| Mechanism | Proves | Proof size | Prover cost | Verifier off-chain | Verifier on-chain (gas) | Trusted setup | Post-quantum | Standard maturity | Tooling | Linkability |
|---|---|---|---|---|---|---|---|---|---|---|
| SD-JWT / salted digests (in repo) | SD, PoP | credential + (value, salt) per disclosed claim; 0.5–5 KB | nil | sub-ms | tens of K (hash + ecrecover); rarely done | none | with PQ signature | RFC 9901; EUDI ARF | universal; repo `vc_issuer.py` | fully linkable (signature, digests, holder key) |
| BBS+ (Data Integrity `bbs-2023`) | SD, UL-ms, UL-iss, PoP | ~100 B sig; proof hundreds of B, linear in hidden claims | ms (laptop); tens–hundreds ms ARM (target §10) | low ms (2 pairings) | n/m (EIP-2537 makes it possible) | none | no | IETF CFRG draft; W3C CR track | mattrglobal bbs-signatures; pairing_crypto; anoncreds-rs (v2) | unlinkable except via disclosed values / metadata |
| CL / AnonCreds v1 | SD, UL-ms, UL-iss, PP (int), NR, PoP | several KB | 100s ms – s on constrained | tens ms | not practical | honest RSA modulus | no | AnonCreds v1.0 (LFDT); deployed | anoncreds-rs, ACA-Py, Credo-TS | unlinkable; Set B ceiling 12/12 |
| Groth16 | any circuit predicate | ~128–256 B | scales with constraints; ms–s | ms | ≈200–350K | per-circuit (phase 2) | no | none identity-specific | circom/snarkjs, gnark, arkworks | by public inputs only |
| PLONK / UltraPLONK | any circuit predicate | ~0.5–1 KB | ms–s | ms | higher than Groth16 (no figure) | universal | no | none identity-specific | snarkjs, noir/Barretenberg, halo2 | by public inputs only |
| zk-STARK | any predicate | tens–hundreds KB | s | tens ms | millions unless SNARK-wrapped | none | yes | none identity-specific | Cairo, Winterfell, RISC Zero, SP1 | by public inputs only |
| Semaphore | group membership + nullifier | Groth16 | seconds in browser (depth 20) | ms | Groth16 + nullifier SSTORE | Groth16 ceremony (done) | no | community standard; PSE | semaphore-protocol JS/Solidity | unlinkable within group; one signal per scope |
| RSA / bilinear accumulator | NR | hundreds of B | witness update per revocation; small proof | pairing | one SSTORE per accumulator update | RSA: yes; bilinear: no | no | AnonCreds registries | anoncreds-rs (bilinear); libraries for RSA | verifier learns nothing about index |
| Bitstring Status List / F6-F7 | revocation status | nil | nil | fetch + bit read; F6 free | F7 write 32,980 (measured, O1) | none | yes | W3C v1.0; VC DM 2.0 | universal; repo `RevocationRegistry`; sandbox F6/F7 | index is a correlator; issuer sees fetches |

The table supports one reading that the rest of the document develops: **no single mechanism spans the matrix.** The hybrid must compose at least three — a hash-based selective-disclosure baseline for Tier 3 and audit (already built), an unlinkable multi-show signature for Tier 2 (BBS+), and a general-purpose ZK layer for the handful of predicates and on-chain gates that need it (Groth16 today, with a documented path to PLONK/STARK for setup-freedom and quantum posture). Revocation privacy follows the same composition: F6/F7 status flags for audit-tier credentials, accumulators for Tier 2 credentials that are presented unlinkably.

## 3. On-chain versus off-chain verification of proofs

### 3.1 The claim

Verification placement should be decided by a single question: *does the outcome of verifying this proof have to change ledger state atomically with the verification?* If yes, the verifier must be on-chain. If no, the proof should be verified off-chain and only the *fact* of verification anchored, if anything at all. This is the ZKP-specific instance of the placement taxonomy in 01 (on-chain / anchored / off-chain, per object and per function), and it lands almost every CAV and agent presentation off-chain.

### 3.2 When on-chain verification is required

Three cases require the proof and the state transition to be in the same transaction. A **gated state transition**: an on-chain registry write that is permitted only if a predicate holds — a `VEHICLE_REGISTRATION` transfer allowed only if the buyer proves "licensed in jurisdiction J", or a Set C `attestReputation` accepted only from a prover who holds an unrevealed attester credential. A **payment release**: a toll or charging settlement executed by a contract that releases escrowed funds against a proof that the service was rendered to an eligible holder. A **registry write with a privacy predicate**: a Semaphore-style signal that must be de-duplicated by nullifier on-chain, because the nullifier set *is* the Sybil defence and must be global. In each, off-chain verification would require trusting whoever reports the verification result — which is the verifier-as-oracle pattern of §3.4, and acceptable only where that trust already exists.

### 3.3 When off-chain verification with anchoring suffices

The I2I handshake (08), gate access, Tier 2 tolling authorisation, charging-session initiation and parking credential exchange all have the same shape: two parties establish a channel, one proves eligibility, the other grants a service *off-chain*, and settlement or audit happens later. The proof's verifier is the RSU, the depot controller, the charger, or the counterpart agent. Nothing on-chain needs to change at the instant of verification. Off-chain verification is milliseconds (§2), fits the Tier 2 budget of 100–500 ms with margin, and — critically — keeps the proof out of calldata. What may be anchored afterwards is a *verification event*: a hash of (proof, public inputs, verifier DID, timestamp, outcome) written by the verifier, or batched into a Merkle root and written once per interval, or placed in an EIP-4844 blob (ephemeral, roughly 18 days, DIGEST-LEVEL, NEW-22) if only short-term dispute evidence is needed.

The trust assumption of "verify off-chain, anchor the event" is explicit: the anchor proves that the verifier *claimed* a verification with those inputs at that time; it does not prove the verifier verified correctly or honestly. That is acceptable when (i) the verifier is an accountable party whose DID is endorsed (G4 `isEndorsed` on the verifier's operator role — the endorsement layer of the VID build makes verifiers accountable identities, not just holders and issuers), (ii) the proof bytes are retained off-chain by the verifier and are re-verifiable by an auditor against the anchored hash, and (iii) a dispute path exists in which the holder can produce the proof transcript. What breaks it: a verifier that anchors an event for a proof it never checked, or that discards proof bytes; both are detected only at audit, which is the forensic tier of §8.

### 3.4 Verifier-as-oracle

When an on-chain contract needs a verification result but on-chain verification is too expensive or the proof system has no EVM verifier (BBS+, CL), the pattern is a *verifier oracle*: one or more endorsed verifier DIDs verify off-chain and submit a signed attestation that the contract checks with `ecrecover` (a few thousand gas, DIGEST-LEVEL, NEW-2) instead of a pairing-based verifier (hundreds of thousands). The 2020 CVIN paper's distributed oracles [5] are exactly this with a quorum: the contract accepts the result if *k* of *n* endorsed verifiers attest. The security reduces to the endorsement set and the quorum, which is a governance question (endorsement registry, G1–G4) rather than a cryptographic one. The design rule this document adopts for 03: use a verifier oracle only where the endorsement set is small, stable, and itself auditable (transport authorities, tolling operators, fleet operators), never for open peer-to-peer verification.

### 3.5 Gas: on-chain Groth16 versus measured anchors

Against the measured O1 anchors — F8 `createPresentation` 62,441 gas, F5 `issueCredential` 130,163, F7 `revokeCredential` 32,980 — an on-chain Groth16 verification at ≈200–350K gas (DIGEST-LEVEL) is three to six times the cost of anchoring a presentation commitment and roughly two to three times the cost of anchoring a credential. The comparison is stated as a ratio deliberately: it is robust to gas-price movements and to which L1/L2 hosts the registry, and it says that *on-chain ZK verification is a Tier 3 or gated-transition expense, not a per-interaction one*. A Tier 2 interaction that verified on-chain would pay for the verification, the block-time delay (which alone breaks the 500 ms budget on most chains — Memo A's "off-chain verification avoids block-time delays" is a hard constraint here, not a preference), and the calldata for the proof (16 gas per non-zero byte, DIGEST-LEVEL, NEW-2: roughly 3–4K gas for a 256-byte proof, minor next to the pairing cost).

### 3.6 zkEVM and L2 as a cost lever

Where on-chain verification is genuinely required, the lever is where "on-chain" is. A rollup that itself proves EVM execution (a zkEVM) amortises L1 cost across thousands of transactions, so the *marginal* L1 cost of a Groth16 verification inside the rollup is the rollup's per-transaction share of the batch proof plus calldata or blob cost — orders of magnitude below L1 execution (DIGEST-LEVEL, rollup cost literature, NEW-23; no figure asserted). The CVIN sidechain-anchored-to-backbone architecture [5] predates rollups but is the same shape: most transactions in the sidechain, few on-chain. The Memo A stance "EVM-first, L2/zkEVM-extensible" therefore maps directly: Local CVINs are L2s (or app-chains) where on-chain verification is affordable, and the Global CVIN backbone receives only their state roots. The consequence for §9 is that the on-chain verification cost in the parametric model is a variable, `G_on × g_L`, with `g_L` a chain-specific gas price that is small on an L2 and large on L1.

### 3.7 The F8 anchoring resolution

Returning to §1.2: how does F8 anchoring coexist with unlinkable presentation? The answer is that F8 anchors *a commitment*, and the holder DID it takes can be a pairwise DID. Concretely, for a Tier 2 unlinkable presentation the hybrid (03) does the following. The holder creates a BBS+ derived proof off-chain and sends it over the I2I channel. The `challenge` bound into the proof is `keccak256(verifierDID ‖ nonce ‖ sessionParameters)`. If an anchor is wanted at all, the *verifier* (not the holder) anchors a verification event as in §3.3, or the holder calls F8 from a pairwise DID created for that verifier (F1, one-time cost, 161–179K gas measured on O1 — expensive enough that pairwise DIDs are provisioned per long-lived relationship, e.g., per tolling operator, not per interaction). What is *never* done is calling F8 from the holder's public DID with the real credential identifiers for a routine Tier 2 interaction; that turns the ledger into a trajectory log. The sandbox's S1 already respects this in spirit (the F8 call is made by IdentityA in a two-party channel), and the campaign's S7 scenario script will make it explicit by tagging which DID mode is used in each F8 call.

## 4. CAV applications

### 4.1 Method

Each application states the credential, the predicate, the tier, the verifier, the disclosure minimised, and the mechanism chosen from §2. All are designs; none has been run. The table gives the summary; the prose that follows argues the non-obvious choices.

| # | Application | Credential (VID build name) | Predicate proven | Tier | Verifier | Disclosure minimised | Mechanism |
|---|---|---|---|---|---|---|---|
| C-1 | VIN privacy | `VID_BIRTH` | "I hold a birth certificate whose VIN hashes to a registered `vinHash`" or "…whose issuer is an endorsed OEM" | 2/3 | service centre, RSU, buyer | VIN itself | Groth16 hash pre-image (tier 3 of VIN scheme); BBS+ hide-VIN |
| C-2 | Driver age / licence class | `DRIVER_LICENCE` | `class ∈ {C, …}` ∧ `expiry ≥ today` ∧ `birthdate ≤ today − 18 y` | 2 | rental kiosk, car-share vehicle, enforcement | name, DOB, licence number, address | BBS+ + range (AnonCreds v2) or Groth16 |
| C-3 | Insurance valid today | `INSURANCE_CLAIM` family / insurance policy VC | `validFrom ≤ today ≤ validUntil` ∧ issuer endorsed as INSURANCE_COMPANY | 2 | RSU at border/toll, rental, police stop | policy number, insurer identity, premium class | BBS+ with disclosed issuer key hidden behind endorsement-set membership |
| C-4 | Emissions compliant at LEZ | `EmissionsCompliance` (schema exists in repo) | `euroClass ≥ 6` or `co2 ≤ threshold(zone)` | 2 | LEZ gantry RSU | exact emissions figure, vehicle identity | BBS+ + range proof |
| C-5 | Registered in jurisdiction J | `VEHICLE_REGISTRATION` | `jurisdiction = J` ∧ not revoked | 2 | Local CVIN gate | plate, owner DID, VIN | Semaphore membership in J's registered set, or BBS+ disclosing only `jurisdiction` |
| C-6 | Odometer range at resale | latest `MAINTENANCE`/`INSPECTION` event VC | `odometer ≤ X` ∧ event ≤ 90 days old ∧ issuer endorsed SERVICE_CENTER | 3 | buyer, marketplace | exact reading, service history detail | Groth16 range over committed attribute (§10(c)) |
| C-7 | BSM-adjacent pseudonym derivation | SCMS pseudonym certificate (not a VC) | — | 1 | other vehicles | — | **stays with SCMS** (see text) |
| C-8 | Fleet membership for depot access | fleet membership VC issued by FLEET_MANAGER | "member of fleet F" | 2 | depot gate controller | which vehicle | Semaphore (nullifier per gate per day) or BBS+ |
| C-9 | Toll payment without location trail | toll account/prepaid VC + `VEHICLE_REGISTRATION` class | "holder has valid account with balance ≥ tariff" ∧ vehicle class | 2 | gantry RSU; settlement contract | account identity, trajectory | BBS+ presentation off-chain; blind-token or nullifier settlement |

### 4.2 VIN privacy and the three-tier VIN scheme

The repository's `MOBIVIDRegistry.sol` stores a `vinHash` (`SHA256(VIN ‖ salt ‖ vehicleDID)`, "for searchability") and an `encryptedVIN` ("only owner can decrypt") in the birth certificate; the mobi-vid README lists "zero-knowledge VIN proofs" as an unbuilt item. The three tiers are therefore: (1) *hash* — anyone who knows the VIN and the salt can look up the vehicle, which supports authorised lookup by parties the owner has given the salt to; (2) *encrypted* — the owner alone recovers the VIN from chain; (3) *zero-knowledge* — the holder proves a statement about the VIN without revealing it or the salt.

The ZK tier's predicate is the hash pre-image: "I know (VIN, salt) such that `H(VIN ‖ salt ‖ vehicleDID) = vinHash`" for a `vinHash` the verifier can see on-chain, optionally composed with "VIN's WMI prefix is in the OEM's WMI set" to prove make without revealing the serial. Two design consequences follow, both load-bearing for 10. First, `SHA256` is expensive in R1CS (tens of thousands of constraints per block, DIGEST-LEVEL, NEW-16); the ZK tier is practical on an OBU only if the committed digest is ZK-friendly (Poseidon), which means the VID build's `credentialHash` and any attribute commitments should be computed with a hash the circuit can afford *or* a dual commitment (SHA-256 for the SD-JWT path and Poseidon for the ZK path) should be recorded in the credential. This is stated as an open question in §13 because it changes an on-chain schema. Second, proving VIN-holding against the *on-chain* `vinHash` makes the proof linkable by that hash; the unlinkable variant proves "the VIN in my BBS+-signed `VID_BIRTH` has WMI prefix W" without touching the on-chain hash at all, and only the forensic tier (§8) ever connects the two.

### 4.3 Driver age and licence class

The `DRIVER_LICENCE` credential (holder DID, class, restrictions, expiry; content off-chain, anchor on-chain) is presented at Tier 2 to a rental kiosk or a car-share vehicle. The predicate composes a set-membership on `class`, an inequality on `expiry` against the verifier's date, and an age inequality on `birthdate`. With BBS+ alone the holder must *disclose* `class` and `expiry` (acceptable: neither is identifying on its own) but cannot hide `birthdate` while proving age — that needs a range proof, which AnonCreds v2 composes with BBS+ (NEW-8) and which a Groth16 circuit does directly. The disclosure minimised is the full identity page of a licence: name, date of birth, licence number, and address, all of which today's rental counter photographs. The issuer (a DMV, endorsed by the ministry for `DRIVER_LICENCE` via G2) is disclosed by public key; where the set of DMVs is public that is harmless, and where it would reveal province of residence, the presentation proves "issuer ∈ endorsed set for DRIVER_LICENCE" via Merkle membership over the endorsement registry's current set (which the endorsement registry can expose as a root — a 03 design item).

### 4.4 Insurance-valid-today and emissions compliance

Both are the same pattern — a date-range or threshold predicate over one attribute plus an endorsed-issuer check — and both run at Tier 2 against an RSU. The disclosure minimised is the policy or the exact emissions figure, and, for insurance, the insurer's identity (which correlates with risk class and is commercially sensitive). For emissions the verifier is a low-emission-zone gantry; the interaction is drive-through, so the proof must be generated *before* the vehicle enters range (pre-computed from the zone's published policy, valid for the day) and verified within the RSU's contact window. That pre-computation is the proof-caching pattern of §9.4. The `EmissionsCompliance` schema already exists in `2_w3c-ssi-layer` and is the natural first target for the range circuit in §10(c) because its attribute is a bounded integer.

### 4.5 "Registered in J" and Local CVIN gates

The 2020 paper's Local CVINs are jurisdiction-specific shards derived from the Global CVIN via ID Porting Protocols [5]. A Local CVIN gate (a jurisdiction's on-ramp to its own services) needs to know that a vehicle is registered in J, or is a visitor with a ported identity, and nothing else. Two mechanisms fit. A BBS+ presentation of `VEHICLE_REGISTRATION` disclosing only `jurisdiction` is the simplest and is unlinkable across gates. A Semaphore group whose leaves are the registration commitments of J's vehicles gives the same with an on-chain nullifier, which J may want if gate entries feed a per-vehicle daily quota or a congestion charge — the nullifier scope `(gateId, day)` then enforces "one charge per vehicle per day" without the gate learning which vehicle. Group maintenance is the cost: every new registration adds a leaf, every de-registration must be reflected, and the gate must verify against a recent root; the staleness window is the §6 question again.

### 4.6 Odometer range proofs at resale

The VID II lifecycle produces a sequence of `MAINTENANCE` and `INSPECTION` event credentials, each carrying an odometer reading, issued by endorsed `SERVICE_CENTER` and `GOVERNMENT_INSPECTION` DIDs; the S8 scenario checks odometer monotonicity off-chain. At resale a buyer wants "odometer ≤ X and the reading is recent and from an endorsed issuer" without the seller handing over the full service history before a price is agreed. This is a Tier 3 interaction with no latency pressure, a bounded-integer attribute, and a single verifier — the ideal case for the Groth16 range circuit in §10(c): the credential carries a Poseidon commitment to `(odometer, salt)`, the issuer's EIP-191 signature covers the commitment (verified off-chain, outside the circuit), F6 confirms non-revocation, and the circuit proves `lo ≤ odometer ≤ hi` against the public commitment. Linkability by the commitment is acceptable here because the buyer will, on purchase, receive the full history anyway; the proof protects the pre-agreement negotiation, which is the disclosure that matters.

### 4.7 Why Tier 1 pseudonym derivation stays with SCMS

It would be tempting to derive BSM pseudonyms from the vehicle's DID via a ZK scheme, unifying the layers. This document argues against it, for three reasons that 03 should treat as settled. First, latency: Tier 1 is under 100 ms and BSMs are signed at 10 Hz; the SCMS design [6] uses batches of pre-issued short-lived certificates precisely so that no per-message proof is needed, and no ZK mechanism in §2 approaches that budget on an OBU for per-message use. Second, the SCMS linkage-authority split already provides the accountability escrow that §8 argues for, with a deployed governance structure (SCMS Manager, misbehaviour authority) that the thesis's "extension, not replacement" stance keeps. Third, the ecosystem: 1609.2 [28] is the interoperability baseline for every V2X radio; the DID layer *binds* to it — the vehicle's DID holds, as a verification method (F9), the enrolment-certificate public key or a commitment to the SCMS enrolment, so that Tier 2/3 history can be connected to Tier 1 behaviour *only* through the SCMS misbehaviour process. What ZK adds at the boundary is "BSM-adjacent": proving, at Tier 2, that a Tier 2 credential holder is the same entity as an SCMS-enrolled vehicle without revealing which enrolment — a proof of knowledge of an enrolment-certificate key bound to the DID. That is a §10 stretch item, not a Tier 1 change.

### 4.8 Fleet membership and toll payment without location trails

Depot access (C-8) is the cleanest Semaphore case: the fleet manager (an endorsed `FLEET_MANAGER`) maintains the group; the gate verifies membership and a nullifier scoped to `(gate, shift)`; the fleet learns which gates were used (from nullifier counts) but not which vehicle, unless the forensic tier is invoked. BBS+ presentation of a fleet-membership VC achieves the same without a nullifier and without on-chain group management, and is preferred where double-entry is not a concern.

Toll payment (C-9) is the hardest, because it combines an eligibility proof, a payment, and the strongest location-privacy requirement (a toll record is a location record). The design this document hands to 06 and 03: the vehicle presents, off-chain at the gantry, a BBS+ proof of "valid toll account, vehicle class K" that discloses nothing identifying; the gantry issues a signed *charge token* for tariff(K) bound to a nullifier the vehicle derives from its account secret and the `(gantry, period)` scope; settlement happens later, in batch, when the vehicle (or its wallet) redeems charge tokens against its account through a settlement contract or the operator's back end that checks nullifier uniqueness — a blind-signature or Semaphore-style flow in which the operator learns *how much* each account owes per period but not *where* the charges arose, because the charge tokens are not linked to the gantry at redemption. The trust assumption: the operator must not be able to correlate redemption timing with gantry passage timing (batching and delay defend this), and the gantry must not record transport metadata that identifies the vehicle (§8). What breaks it: an operator that runs both the gantries and the settlement and colludes with itself on timing; the mitigation is a mandated redemption delay and randomised batch windows, which are policy, not cryptography. Payment release on-chain, if the settlement contract is on-chain, is a §3.2 gated transition and pays the Groth16 or oracle cost once per batch, not per gantry.

## 5. AI-agent applications

### 5.1 The claim

The I2I generalisation (C14, C15) holds for ZK exactly as for channels: every CAV application in §4 has an agent twin in which the "vehicle" is an agent holding a DID (via ERC-4337/ERC-7579 account abstraction or a plain key), the "credential" is a capability or delegation credential, and the "RSU" is a counterpart agent or a tool endpoint. The additional properties agents need — bounded authority, provenance of action traces, and model provenance — are where ZK moves from disclosure minimisation to *attestation of computation* (§7).

### 5.2 Capability proofs without revealing the principal

An agent acting for a principal P holds a capability VC issued by P (or by P's delegate via F11 `addDelegate` with `delegateType = sigAuth`, validity-bounded) that says "may negotiate charging contracts up to value V on behalf of P". Presented to a charging operator's agent, the minimal disclosure is "an endorsed principal has granted this agent capability class *charging-negotiation*"; P's identity is commercially sensitive (a fleet's charging pattern is its route plan). BBS+ hides P's DID as an undisclosed message; the endorsement check on P becomes a membership proof over the endorsement registry's set of endorsed fleet operators, as in §4.3. F12 `validDelegate` cannot be used by the verifier directly without revealing P (it takes P's DID as argument); instead the *agent* proves, in zero knowledge, knowledge of a valid delegation — either by holding a delegation VC that P issued (F5-anchored, F6-checkable by credential id, which is a per-relationship pairwise id) or, for on-chain checks, by the verifier-oracle pattern where P's own agent attests. This is a real limitation of F12 as a privacy primitive and is recorded as a finding for 11: *Set A delegation is public by construction; private delegation lives in Set B credentials.*

### 5.3 Budget and limit predicate proofs

"My remaining budget is at least the quoted price" is a range proof over an attribute that changes with every spend, which makes it different from the static attributes of §4: the credential must be re-issued (or the commitment updated) after each transaction, or the budget must be held as an on-chain balance in the agent's account and the proof made against a chain state root (a Merkle-membership proof of the balance slot against a recent block's state root — a light-client proof in a SNARK, feasible but heavy, DIGEST-LEVEL, NEW-24). For Tier 2 agent negotiation the practical design is a *session budget credential* issued by the principal's wallet at session start with a short validity, presented with BBS+ disclosing only `budgetClass` (a coarse bucket) and proving `validUntil ≥ now`; exact budgets are never disclosed and the counterpart learns only that the agent is within a bucket. The disclosure minimised is the principal's willingness to pay.

### 5.4 Reputation-above-threshold without revealing the score

Set C `getReputation(did) → (meanScore, attestationCount)` is a public view, so an agent's reputation is public wherever its DID is. Unlinkable sessions (§5.7) mean the counterpart does not know the DID. The agent must therefore prove "reputation ≥ θ" for a hidden DID: a proof that (i) the hidden DID's reputation record, as of block B, has `meanScore ≥ θ` and `attestationCount ≥ n_min`, against the reputation registry's state (a Merkle/state-proof in a SNARK against block B's root), or (ii) the agent holds a *reputation snapshot VC* issued by an endorsed reputation oracle at time t stating the values, presented with BBS+ plus a range proof. Option (ii) is the realisable one at Tier 2; option (i) is the trust-minimised one. 09 §4 develops why reputation needs identity in the first place; this section supplies the mechanism by which reputation can be *used* without collapsing the identity's privacy, which is the missing link between 09's argument and 05's tiers.

### 5.5 Proof of non-revocation of delegation

Delegations end: a principal revokes an agent's capability (F7 on the delegation VC, or expiry of the F11 delegate). A counterpart mid-session needs to know the delegation is still live without the agent revealing which delegation it is. This is precisely the accumulator case of §6: the principal (or the endorsed delegation issuer) maintains a non-revocation accumulator for its issued delegations, the agent holds a witness, and each presentation includes a non-revocation proof against the accumulator value as of a block the counterpart accepts as fresh. The staleness window the counterpart tolerates is a session-policy parameter — the A2A "session policy" phase of Memo B — and it is the same parameter as the cache-invalidation rule of Memo A: a verifier that caches "delegation valid at block B" must invalidate when the accumulator changes, and the accumulator's on-chain update event is the invalidation signal.

### 5.6 Provenance of action traces and model provenance (zkML)

Agents leave signed execution traces (Memo B). A signature proves *who* asserts the trace; it does not prove the trace is *what happened*. Two levels of ZK attestation apply. At the first level, a proof that a trace is *consistent* — that each logged action is signed by a key valid (F12) at the logged time and that the log is a hash chain anchored at intervals — is a Merkle/signature circuit and gives tamper-evidence with privacy (the auditor sees the proof, not the actions). At the second level, *zkML* proves that a stated model, identified by a commitment to its weights, produced a stated output from a stated input (NEW-25, DIGEST-LEVEL: EZKL, zkML literature; proving cost today is seconds to hours depending on model size, far above Tier 2 budgets). The thesis's placement for zkML is therefore as a *validation hook*: ERC-8004's validation registry [19] and the sandbox's Set C `requestValidation(did, validationType, payload) → requestId` / `validationStatus(requestId)` are designed exactly for asynchronous, third-party validation of an agent's claim about its own behaviour. A `validationType = zkml-inference` request carries the input/output commitments; a validator (an endorsed DID) produces or checks the zkML proof off-chain and sets the status; the status is the anchor. This matches Memo A's "operational transparency rather than algorithmic transparency": the proof shows that a *committed* model was run, not what the model is. 09 §6 takes this up for federated-learning update provenance.

### 5.7 Unlinkable agent sessions

An agent that negotiates with many counterparts under one DID is trivially profiled. The 2020 dual-mode identity [5] applies unchanged: a public DID for discovery and reputation accrual; pairwise DIDs (F1 per relationship, or, cheaper, derived keys added via F9/F11 under a pairwise-looking DID) for sessions; BBS+ presentations of the agent's capability and reputation-snapshot credentials so that sessions cannot be linked by credential material. Reputation then poses a genuine tension: attestations (C1 `attestReputation`) must land on the *public* DID to accrue, but the counterpart only knows the pairwise DID. Resolution: the counterpart attests to the pairwise DID's session, and the agent later proves, in zero knowledge, ownership of *n* pairwise DIDs with attestations to aggregate them into a claim on the public DID — a Semaphore-like "I control these leaves" proof — or the reputation oracle of §5.4 performs the aggregation under escrow. This is an open design item for 09 and 03 and is listed in §13.

## 6. Revocation and ZKP

### 6.1 The claim

Revocation is where privacy and freshness collide, and the collision is quantitative: every revocation mechanism trades verifier-side privacy against holder-side work and against the staleness window a verifier accepts. The hybrid must offer both status-list (F6/F7) and accumulator revocation, choose per credential type, and expose the staleness window as a policy parameter rather than hiding it.

### 6.2 Status lists versus accumulators, with holder privacy

Memo A already frames the pair: status lists give simpler proofs, accumulators give holder privacy. Against the §2 properties, the trade is: with a status list (or on-chain F6), the verifier's check is free and instantaneous and always current (F6 reads the chain's current state), but the check *identifies the credential* (its index or id) to whoever serves the check — the chain node (public, if the verifier uses a public RPC) or the issuer (if the list is fetched from the issuer). With an accumulator, the verifier learns nothing about which credential was checked, the check is a pairing (milliseconds), and the *holder* bears the cost: it must keep a witness current, which requires knowing every revocation since its last update — the "tails" data in AnonCreds, a download proportional to the registry's revocation history (DIGEST-LEVEL, NEW-8). A middle path is a ZK Merkle-membership proof over a status list's *non-revoked* set (or a non-membership proof over the revoked set), which keeps the list's simplicity for the issuer and moves the privacy cost into a SNARK on the holder — realisable with the §10(c) toolchain, at Groth16 prover cost per presentation.

The GDPR nuance of the Building Paths preface decides the placement: per-credential status flags keyed by credential id (F6/F7 as the sandbox implements them) are personal data if the id is linkable to a person; an accumulator value is not. So credentials whose ids are pairwise or whose subjects are vehicles and organisations may use F6/F7 freely; credentials about natural persons (`DRIVER_LICENCE`) presented at Tier 2 should use accumulator or ZK-over-list revocation, with F7 retained for the audit tier where the credential id is legitimately known.

### 6.3 Staleness windows

Define the staleness window `W` as the maximum age of revocation state a verifier accepts. For on-chain F6 reads, `W` is bounded by block time plus finality — seconds on an L2, minutes on L1 — and no holder work is needed. For accumulators, `W` is the age of the accumulator value the proof was made against; a verifier that demands the *current* accumulator forces the holder to update its witness immediately before every presentation, which requires connectivity and defeats the low-connectivity scenarios of 06. The design choice this document proposes for 03: verifiers publish `W` per credential type and tier (e.g., `W = 24 h` for `DRIVER_LICENCE` at a rental kiosk, `W = 1 block` for a payment-release gate), holders refresh witnesses opportunistically when connected, and the accumulator update *event* on-chain is the invalidation signal for every cache in the system — which is the cache-invalidation rule of Memo A, now with a concrete mechanism: a verifier subscribes to `AccumulatorUpdated(registryId, newValue, block)` (a proposed extension event, beside IMinimalSSI, never altering it) and drops cached "valid" results for that registry.

### 6.4 Witness updates and revocation storms

The cost of accumulators is concentrated in the *revocation storm*: a mass revocation (a compromised issuer key, a recall affecting a model year, a fleet's insurer withdrawing cover) revokes thousands of credentials in one update, and every remaining holder must process thousands of witness updates. For bilinear accumulators each update is a group operation — cheap individually, but an OBU that has been offline through a storm faces a backlog on reconnection. Three mitigations, all with parameters for §9: partition registries so that storms are contained (per model-year, per fleet — the Local CVIN shard again); issue short-lived credentials so that expiry does most of the revocation work (a `validUntil` check is free in F6 and needs no witness); and let an endorsed *witness service* (an RSU role) precompute updated witnesses for holders in its cell, which trades a little privacy (the service learns which credentials are active in its area) for offline resilience. The last is the kind of clever-but-conditional design the brief asks to be stated honestly: it works if the witness service is endorsed and its logs are audit-tier; it breaks privacy if it is not.

### 6.5 Interplay with F7 and the sandbox

The measured F7 `revokeCredential` on O1 is 32,980 gas per credential, idempotent and irreversible. An accumulator update is one storage write per *batch* regardless of how many credentials are revoked — so for any batch larger than a few credentials the accumulator is cheaper on-chain by a factor of the batch size (a formula, not a measurement: `gas_acc ≈ 1 SSTORE + event` versus `gas_F7 × n`). The trade-off in Memo A's terms — "measured revocation latency, staleness windows, verification cost" — becomes a three-column table that §10 will fill: F7 per-credential (latency = block time; W = 0; verify = free view; privacy = none), accumulator (latency = batch interval; W = policy; verify = pairing; privacy = full), ZK-over-list (latency = list republish; W = list age; verify = Groth16; privacy = full at holder cost).

## 7. Verifiable data beyond ZKP

### 7.1 The claim

Most of the data that flows through a CAV or agent system is not a credential and does not need zero knowledge; it needs *integrity* — the assurance that what the verifier sees is what the source produced — and, for some data, *computation attestation*. Conflating the two wastes ZK budget on data that only needs a signature and a hash anchor.

### 7.2 Oracle-fed data: road conditions and telemetry

Road-condition reports, weather, traffic state, and vehicle telemetry enter the system through oracles [5]. The integrity proofs needed are: source authentication (the reporter signs with a key resolvable via F2, and its role is endorsed, G4), freshness (a timestamp bound into the signature, and for high-value data an anchor of the report hash in a block, which gives the report an upper bound on its creation time — hash-on-chain as integrity-without-disclosure), and aggregation integrity (when *n* reports are combined, a Merkle root of the inputs is anchored with the aggregate so that any input can be audited). None of this is ZK; all of it is the anchor pattern of 01. Where ZK enters is *reporter privacy*: a vehicle reporting an ice patch should not reveal its trajectory; a Semaphore signal ("some member of the registered-vehicle group reports condition X at cell Y") with a nullifier per `(cell, epoch)` gives Sybil-resistant anonymous reporting. That is the road/traffic reporting tail the brief asks for in every scenario, and 09 §5 argues why the reputation of reporters must nevertheless be computable — which brings back §5.4's reputation-above-threshold proof as the reconciling mechanism.

### 7.3 Execution traces

A signed execution trace (Memo B) needs: per-entry signatures under keys valid at the time (F12 history is on-chain, so validity-at-time is auditable), a hash chain so that deletion is detectable, and periodic anchoring of the chain head (an F3 `updateDID` attribute or a dedicated log-anchor contract; the sandbox's F3 measured 44,760 gas on O1 for one attribute update, which bounds the per-anchor cost if F3 were used). Selective *revelation* of a trace to an auditor uses SD-JWT-style salted digests per entry — the repository's existing mechanism generalises directly from claims to log entries — so that a dispute can reveal entries 40–45 without revealing the rest. ZK appears only in §5.6's consistency proof, for the case where even the auditor should see nothing but "the trace is well-formed".

### 7.4 Federated-learning updates

Pointer to 09 §6: a federated-learning update needs source authentication (identity), a bound on its influence (reputation-weighted aggregation), and, for Byzantine robustness, either the aggregator's inspection of the update or a proof that the update was computed honestly from the claimed data and model. The last is zkML again, and today it is far too expensive per round for vehicle-scale participation (DIGEST-LEVEL, NEW-25); the realisable design is signed, reputation-weighted updates with anchored aggregation roots, and zkML reserved for *challenges* — a participant suspected of poisoning is asked, via Set C `requestValidation`, to prove its update, and failure to do so is the reputation signal. That converts an impossibly expensive per-round proof into an occasional, dispute-driven one.

### 7.5 Attesting computation versus attesting data

The distinction to carry into 03: a signature or anchor attests that *data* existed in a state at a time; a ZK proof attests that a *computation* was performed on data. The hybrid uses the former everywhere and the latter in exactly four places: predicates over credential attributes (§4), non-revocation (§6), consistency of traces (§5.6), and dispute-driven model/update provenance (§5.6, §7.4). Everything else is signatures and Merkle roots, which the sandbox already anchors at measured cost.

## 8. Threat analysis and the "privacy when required" principle

### 8.1 What ZKP protects against

Against the Memo A threat model: *impersonation* — proof of possession (challenge-bound F8, holder-bound BBS+ link secret) prevents replay of another's credential; *replay* — the challenge/domain binding of F8 and the nonce in every presentation; *credential theft* — a stolen credential without the holder's link secret or key is unusable, and F10/F7 revoke compromised keys and credentials; *over-disclosure to honest-but-curious verifiers* — selective disclosure; *cross-verifier correlation* — unlinkability (BBS+/CL/SNARK), which SD-JWT does not provide; *issuer surveillance of usage* — issuer unlinkability plus on-chain F6 reads via the verifier's own node (no fetch to the issuer).

### 8.2 What ZKP does not protect against

*Issuer collusion in issuance.* An issuer that embeds a covert identifier in an attribute (a unique `restrictions` string, a fine-grained `validUntil` timestamp) makes every disclosure of that attribute a correlator. Mitigation: schema discipline — coarse-grained attributes, quantised dates — enforced by the credential-type registry's schema hashes; a §13 question is whether the registry should mandate quantisation.

*Verifier collusion on disclosed attributes.* If two verifiers each receive `jurisdiction = BC, class = 5, expiry = 2027-03`, their intersection is small; add a coarse location and time and the holder is identified. Unlinkability protects the *cryptographic* layer only; disclosure policy protects the *semantic* layer, and the presentation-request language (which attributes a verifier may ask for, per tier, per role) is governance, to be set in the endorsement layer's verifier-role definitions.

*Metadata leakage.* IP address, radio MAC, DSRC/C-V2X layer-2 identifiers, TLS session resumption, and the timing and cell of RSU contact leak identity regardless of the proof. The SCMS layer randomises layer-2 identifiers with pseudonym changes [6]; the DID layer inherits that only if Tier 2 sessions rotate transport identifiers on the same schedule. 08 owns the channel; this document's requirement to 08 is that I2I channel establishment must not carry a stable identifier in the clear before the presentation is verified.

*Timing correlation.* A toll charge redeemed at 09:02 for a gantry passed at 09:00 is linked by time. Batching and randomised delay (§4.8) are the only defences and are policy.

*Key compromise.* A ZK proof made with a compromised holder key is valid. Detection is behavioural (reputation, anomaly screens); response is F10 key removal and F7 credential revocation, propagated through the revocation mechanism with its staleness window `W` — during which the compromised key remains usable. The exposure is `W × (interactions per unit time)`, which is a §9 quantity.

*Trusted-setup compromise (Groth16).* A party holding the toxic waste of a circuit's phase-2 setup can forge proofs for that circuit. The mitigation is a multi-party ceremony with at least one honest participant, or PLONK's universal setup, or STARKs; the §10(c) build will use a local single-party setup and must label its proofs as *demonstration only, forgeable by the author* — a required honesty note for 10.

### 8.3 Privacy when required: where the thesis deliberately does not use ZKP

The thesis's third framework property is the forensic audit trail: blockchain "makes attacks permanently visible and attributable". That property is *in tension* with unlinkability, and the resolution is not to choose but to *tier*. Routine Tier 2 presentations are unlinkable. The audit and forensic tier — misbehaviour investigation, insurance-claim adjudication, recall traceability, regulatory reporting, legal discovery — uses linkable, fully disclosed credentials and the on-chain history of F1–F12 events, and does so *by design and with authorisation*. The mechanism that connects the two is the 2020 paper's dual-mode identity [5]: a verinym (the public DID with its permanent, tamper-evident key-material and credential-anchor history) and pseudonymous streams (pairwise DIDs and unlinkable presentations) that are linkable to the verinym *only* through an escrow. Three escrow designs are available, in increasing decentralisation: (i) the SCMS pattern of split linkage authorities [6], where two independent authorities each hold half of the linkage seed and both must act; (ii) a threshold-encrypted linkage record (the holder encrypts the mapping pairwise-DID → verinym under a *t*-of-*n* key held by endorsed authorities and anchors the ciphertext hash via F3 as a DID attribute, so that the *existence* of an escrow record is public and its *opening* requires *t* authorities); (iii) a ZK-verifiable escrow, in which every unlinkable presentation carries a verifiable encryption of the holder's verinym under the escrow key (the "Camenisch–Shoup" pattern, DIGEST-LEVEL, NEW-26), so that a verifier can check the escrow is well-formed without opening it and an authority can open it later. Option (iii) is the cryptographically cleanest and the most expensive per presentation; option (ii) is the realisable one and is what this document recommends to 03, with the F3-anchored escrow record as the "two-key" bridge between the pseudonymous stream and the verinym. What breaks it: collusion of *t* authorities, which is the same governance assumption SCMS makes with two.

The principle stated for 11: **privacy is a property of the routine path, accountability a property of the audited path, and the architecture's job is to make the crossing between them expensive, logged, and authorised** — never impossible (which would defeat the accountability gap the thesis exists to close) and never cheap (which would make unlinkability decorative).

## 9. Cost and realisability

### 9.1 A parametric model of ZK presentations per vehicle-year at Tier 2

The model is stated as a formula with named variables; no variable is assigned a measured value here. For a vehicle *v* over a year:

```
N_v  = Σ_c  f_c × 365                    presentations per year, summing over interaction classes c
       (c ∈ {toll, charging, parking, gate, LEZ, service, insurance-check, …}, f_c per day)

T_prove,v = Σ_c f_c × 365 × t_p(m_c)     OBU prover time, t_p a function of mechanism m_c
T_verify  = Σ_c f_c × 365 × t_v(m_c)     verifier (RSU) time per vehicle, aggregated over cells
B_v  = Σ_c f_c × 365 × s(m_c)            bytes over the air, s = proof size
G_v  = Σ_c f_c × 365 × [ ρ_c × G_on(m_c) + (1 − ρ_c) × G_anchor / k_c ]
       ρ_c   = fraction of class-c presentations verified on-chain
       G_on  = on-chain verification gas (Groth16 ≈ 200–350K DIGEST-LEVEL)
       G_anchor = gas for anchoring a verification event (F8-class anchor 62,441 measured, O1)
       k_c   = batch factor (presentations per anchor; 1 for per-event, large for Merkle batches)
Cost_v = G_v × g_L × price_native         with g_L the chain's gas price (L1 ≫ L2)
R_v  = Σ_c f_c × 365 × u_c × w(m_c)       witness-update work, u_c = revocation events per presentation
                                          interval, w = per-update cost of mechanism
```

The model makes three things visible. On-chain verification cost is linear in `ρ_c`, so the design lever is to drive `ρ_c` to zero for every class except gated transitions and batched settlements. Anchoring cost is divided by `k_c`, so batching turns a per-presentation anchor into a per-interval one — and blobs (EIP-4844) take it further for evidence that need not persist. Prover time is the OBU's constraint and depends entirely on the mechanism: BBS+ at milliseconds-to-tens-of-milliseconds is per-presentation affordable; Groth16 with a small circuit is affordable if the proof can be *pre-computed* (§9.4); Groth16 with a signature-in-circuit or a STARK is not per-presentation affordable on an OBU today (DIGEST-LEVEL judgement from §2 figures, to be tested).

Scale check, as a formula only: with Canada's ≈33 M registered vehicles (DIGEST-LEVEL) and `Σ_c f_c` presentations per vehicle-day, national Tier 2 presentation volume is `33 × 10^6 × Σ_c f_c` per day; at even `Σ_c f_c = 2` that is 66 M presentations a day, which settles beyond doubt that `ρ_c ≈ 0` for routine classes and that verification is an edge (RSU) function, not a chain function — which is the 2020 paper's RSUs-as-edge-servers stance [5] restated in ZK terms.

### 9.2 Prover on an OBU: constraints

The OBU is a constrained device with scarce compute, variable load, and intermittent links [5]. The mechanisms that fit are those whose prover cost is a small constant (BBS+ derived proof; accumulator non-revocation proof) or whose proofs can be generated ahead of need and cached. Circuit-based proofs must be kept to hundreds or low thousands of constraints (range checks, Poseidon Merkle paths of modest depth) and must never include signature verification or SHA-256 in-circuit. Memory is a constraint too: Groth16 proving keys grow with circuit size (megabytes for small circuits, DIGEST-LEVEL, NEW-16), and a witness-update backlog after a revocation storm competes with them. The measurement target in §10 is a Raspberry-Pi-class or equivalent ARM board as an OBU proxy; results will be labelled as proxy measurements.

### 9.3 Verifier at an RSU

The RSU's budget is the Tier 2 window minus channel establishment (08) minus radio contact time. Verifier costs in §2 are milliseconds for every mechanism except STARKs, so the RSU is not the bottleneck at the cryptographic level; the bottleneck is *revocation state freshness* — the RSU must have the current accumulator or status data locally (edge caching per Memo A, invalidated by the on-chain update event of §6.3), because a chain read inside the contact window is a latency risk on a variable link. This is the read-path argument of 01 applied to ZK: the RSU's read path must be satisfiable from local state, and the chain is the source of *invalidation*, not of *verification*.

### 9.4 Proof caching

Predicates whose public inputs are predictable — "insurance valid today", "emissions ≤ zone threshold", "licence class C" — can be proven once per validity period (daily) when the vehicle is parked and connected, and the proof cached for presentation. Caching is safe when the proof is *not* bound to a verifier challenge (the challenge binding then happens at the BBS+ or signature layer around the cached proof) and when the predicate's public inputs are stable for the period. It is unsafe for anything with a nonce in the public inputs (nullifier-scoped signals) and for non-revocation proofs against a current accumulator, which must be fresh within `W`. The design rule for 03: split every presentation into a *cacheable predicate proof* and a *fresh possession-and-freshness envelope*.

### 9.5 Where on-chain verification is affordable

From §3 and the model: on-chain verification is affordable where `f_c` is small (once per registration transfer, once per settlement batch, once per validation request) or where the chain is an L2 whose `g_L` is small. It is affordable *per interaction* nowhere at Tier 2 on L1, and it is not needed there. The Set C `requestValidation` path is the one place where an on-chain Groth16 verifier earns its cost per call: a validation request is infrequent, valuable, and its outcome (status) must be on-chain to be trusted by third parties without re-verification.

## 10. Build and demonstration plan (all items pending)

### 10.1 Principle

Each stage adds one mechanism on the *same* credential objects the VID build already produces, so that every measurement is a like-for-like column in one metrics table. Nothing here alters IMinimalSSI; on-chain additions are extension contracts beside it (spec §6 privacy extension names `verifyZKProof`; the build will use that name for the verifier adapter). No number in this section exists yet.

### 10.2 Stage (a) — SD-JWT-style disclosure (exists; to be re-traced)

Already implemented in `2_w3c-ssi-layer/verifiable-credentials/` (issuer digests, holder subset disclosure, verifier digest recomputation). Work: port the digest scheme to `lib/vid/` (JS) so that a `DRIVER_LICENCE` issued in S7 can be presented with only `class` and `expiry` disclosed; anchor the credential via F5 and the presentation via F8; emit the trace. Assertions: A-a1 verifier accepts a presentation disclosing a subset and rejects one with a tampered value; A-a2 the F8 anchor gas is recorded (expected to match the O1 measured 62,441 within the variation of a different `credentialIds` length — a hypothesis, not a result); A-a3 two presentations of the same credential to two verifiers share the issuer `proofValue` byte-for-byte (the linkability demonstration). Status: pending.

### 10.3 Stage (b) — BBS+ on the same credential objects, anchored through F5/F8

Use `@mattrglobal/bbs-signatures` (or `pairing_crypto` via a Rust binding) to sign the canonical claim vector of a `DRIVER_LICENCE` and `EmissionsCompliance` credential with BBS+ over BLS12-381; issuer's BLS public key registered as a verification method via F9 (`keyType = BLS12381G2`); `credentialHash` for F5 computed over the BBS+-signed credential; holder derives proofs disclosing subsets; verifier checks the derived proof off-chain, then F6 for status and G4 for endorsement. Assertions: A-b1 derived proof verifies with the issuer key resolved via F2; A-b2 two derived proofs from the same credential to two verifiers share *no* common bytes other than the disclosed values and issuer key (unlinkability demonstration, the counterpart of A-a3); A-b3 a proof over a revoked credential still verifies cryptographically but the composite verification fails on F6 (`revoked = true`) — demonstrating that unlinkability and revocation are separate layers; A-b4 proof size and prover/verifier wall-clock recorded on laptop and on the ARM proxy. Status: pending.

### 10.4 Stage (c) — circom/snarkjs range proof with an on-chain verifier compiled alongside the sandbox

Circuit `AttributeRange.circom`: private inputs `value`, `salt`; public inputs `commitment = Poseidon(value, salt)`, `lo`, `hi`; constraints: Poseidon(2) (≈ a few hundred constraints, DIGEST-LEVEL, NEW-16) plus two 32-bit comparisons via bit decomposition. The credential (e.g., an `INSPECTION` event with `odometer`, or `EmissionsCompliance` with a bounded integer) carries `commitment` as a claim; the issuer's EIP-191 signature covers it (verified off-chain, outside the circuit); the F5 anchor covers the credential hash. Groth16 setup: local Powers-of-Tau + phase 2, labelled *demonstration only, forgeable by the author* (§8.2). Export the Solidity verifier with `snarkjs zkey export solidityverifier`, wrap it in `contracts/privacy/ZKRangeVerifier.sol` exposing `verifyZKProof(bytes32 credentialId, uint256[] publicInputs, bytes proof) → bool` that (i) calls the Groth16 verifier and (ii) calls F6 on the sandbox registry, returning true only if both pass — the composition that makes the on-chain check a *complete* verification. Scenario `run_zk_range.js` (S9): issue, prove in-range, verify off-chain (snarkjs), verify on-chain (tx), prove out-of-range (must fail), revoke, verify on-chain (must fail on F6). Trace entries: `kind: "tx", fn: "verifyZKProof", fnId: "P2"` with `gasUsed`; `kind: "offchain"` entries for prove/verify timings. Assertions: A-c1 in-range proof accepted on-chain and off-chain; A-c2 out-of-range proof rejected by the circuit (witness generation fails or verifier returns false); A-c3 revoked-credential proof rejected by the composite verifier while the raw Groth16 verifier alone accepts it; A-c4 `gasUsed` recorded and compared, as a ratio, with the measured F8 62,441 and the DIGEST-LEVEL 200–350K expectation — any deviation is a finding for `docs/FINDINGS.md`; A-c5 calldata bytes of the proof recorded. Status: pending. A second circuit, `VinPreimage.circom` (Poseidon pre-image of the VIN commitment with a WMI-prefix check), is a stretch item for the three-tier VIN scheme of §4.2.

### 10.5 Stage (d) — anoncreds-rs comparison as the Set B ceiling

With `anoncreds-rs` (Python or Node bindings), define a schema and credential definition matching the `DRIVER_LICENCE` claims, issue with a revocation registry, and produce a presentation with `p_gte` on an integer attribute and a non-revocation proof; anchor the credential definition hash and the accumulator value on the sandbox via F5 (as a "credential definition anchor" credential) and a proposed `AccumulatorRegistry` extension contract. Record proof size, prover/verifier time, tails-file size, and witness-update time after 1, 100, and 1,000 simulated revocations. Assertions: A-d1 predicate presentation verifies; A-d2 non-revocation proof fails after revocation once the verifier holds the updated accumulator, and *succeeds* against the stale accumulator within `W` (the staleness-window demonstration); A-d3 metrics recorded in the table. Status: pending.

### 10.6 The metrics table to fill

Every cell is empty until a trace or a timing log exists; the table is reproduced in 10 once filled.

| Metric | (a) SD-JWT | (b) BBS+ | (c) Groth16 range | (d) AnonCreds v1 |
|---|---|---|---|---|
| Proof / presentation size (bytes) | pending | pending | pending | pending |
| Prover time, laptop (ms) | pending | pending | pending | pending |
| Prover time, ARM proxy (ms) | pending | pending | pending | pending |
| Verifier time off-chain (ms) | pending | pending | pending | pending |
| On-chain verification gas | n/a | n/a | pending (trace S9) | n/a |
| Anchor gas (F5 / F8 / extension) | pending | pending | pending | pending |
| Constraints / circuit size | n/a | n/a | pending | n/a |
| Setup artefact size (zkey / tails) | n/a | n/a | pending | pending |
| Witness update time after 1 / 100 / 1,000 revocations | n/a | n/a | n/a | pending |
| Unlinkability demonstrated (A-a3 vs A-b2) | linkable (expected) | unlinkable (expected) | by commitment | unlinkable (expected) |
| Revocation-layer separation (A-b3 / A-c3 / A-d2) | pending | pending | pending | pending |

### 10.7 How the demonstrations map to the thesis

Stage (a) evidences C10's baseline and the createPresentation-gap discussion (Chapter 5 §5.1). Stage (b) evidences the Tier 2 unlinkability claim of Chapter 4 Stage 19 and the extension of SCMS-style privacy above Tier 1. Stage (c) supplies the first *measured* on-chain ZK verification gas in the programme, replacing the DIGEST-LEVEL ~350K in the thesis draft with a traced number and a ratio to F8. Stage (d) evidences the "AnonCreds as Set B ceiling" claim with proof-level metrics rather than coverage counts, and feeds C11–C13.

## 11. Sources used in this document

| Ref | Source | Verification state | How used |
|---|---|---|---|
| [1] | Allen, The Path to Self-Sovereign Identity, 2016 | VERIFIED AT SOURCE (thesis list) | Consent and Minimization principles, §1.2 |
| [5] | Prakash, Michelson, Feng, CVIN, VTC2020-Spring | VERIFIED AT SOURCE (programme's own) | Dual-mode identity, Local CVINs, oracles, RSUs as edge, sidechains; §1, §3, §4, §8, §9 |
| [6] | Brecht et al., SCMS, IEEE T-ITS 2018 | DIGEST-LEVEL | Pseudonym certificates, linkage authorities; §1.2, §4.7, §8 |
| [8] | W3C DID Core 1.0 | VERIFIED AT SOURCE (thesis list) | Verification methods (F9 key types), §10 |
| [9], [10] | W3C VC Data Model 1.1 / 2.0 | VERIFIED AT SOURCE (thesis list) | credentialStatus, proof model; §2, §6 |
| [12] | Camenisch & Lysyanskaya, CRYPTO 2004 | DIGEST-LEVEL | CL signatures, §2.4 |
| [13] | Flamini et al., selective disclosure mechanisms, JISA 2024 | DIGEST-LEVEL | Comparative framing and constrained-device cost ranges, §2 |
| [14] | Fett, Yasuda, Campbell, SD-JWT, RFC 9901 | DIGEST-LEVEL | §2.2 comparison with the repo's scheme |
| [19] | De Rossi et al., ERC-8004 | DIGEST-LEVEL | Validation registry as zkML hook, §5.6 |
| [22] | Dunphy, blockchain trilemma / Indy, arXiv:2204.05784 | DIGEST-LEVEL | AnonCreds proof-size context, §2.4 |
| [25] | LFDT, Indy on Besu joins did:indy | DIGEST-LEVEL | AnonCreds anchoring model, §1.1 |
| [28] | IEEE 1609.2-2022 | DIGEST-LEVEL | Tier 1 baseline, §4.7 |
| Repo | `2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py`, `vc_holder.py` | VERIFIED AT SOURCE (read for this document) | SD-JWT-style digest construction, §2.2, §10.2 |
| Repo | `5_minimal-ssi-sandbox/contracts/interfaces/IMinimalSSI.sol` | VERIFIED AT SOURCE (read) | F8 signature and PresentationCreated event, §1.2, §3.7 |
| Repo | `5_minimal-ssi-sandbox/traces/i2i_O1_ERC1056_1780620182135.jsonl` | VERIFIED AT SOURCE (read) | All measured gas: F1, F3 44,760, F5, F7, F8, F9 59,607, F10 36,478, F11 |
| Repo | `cv2x-testbed/contracts/MOBIVIDRegistry.sol`; `2_w3c-ssi-layer/mobi-vid/README.md` | VERIFIED AT SOURCE (read) | vinHash / encryptedVIN / ZK-VIN to-do, §4.2 |
| NEW-1 | GDPR Art. 5(1)(c), Art. 25 | DIGEST-LEVEL | Data minimisation, §1.2 |
| NEW-2 | EVM gas schedule: EIP-2929, calldata pricing, precompiles | DIGEST-LEVEL | SSTORE/SLOAD/calldata/ecrecover costs, §2, §3, §6 |
| NEW-3 | IETF OAuth WG, SD-JWT VC profile | DIGEST-LEVEL | §2.2 maturity |
| NEW-4 | EU Digital Identity Architecture Reference Framework | DIGEST-LEVEL | §2.2 adoption |
| NEW-5 | Au, Susilo, Mu (2006); Camenisch, Drijvers, Lehmann (2016), BBS+ | DIGEST-LEVEL | §2.3 |
| NEW-6 | IETF CFRG, The BBS Signature Scheme (draft) | DIGEST-LEVEL | §2.3 sizes |
| NEW-7 | W3C Data Integrity BBS Cryptosuites v1.0 (`bbs-2023`) | DIGEST-LEVEL | §2.3 standardisation |
| NEW-8 | LFDT AnonCreds v1.0 spec; AnonCreds v2 (BBS+) working documents | DIGEST-LEVEL | §2.4, §2.7, §6 |
| NEW-9 | EIP-2537, BLS12-381 precompiles | DIGEST-LEVEL | §2.3 on-chain possibility |
| NEW-10 | mattrglobal/bbs-signatures; pairing_crypto | DIGEST-LEVEL | §2.3 tooling, §10.3 |
| NEW-11 | BC Verifiable Organizations Network | DIGEST-LEVEL | §2.4 deployment |
| NEW-12 | Groth, On the size of pairing-based non-interactive arguments, EUROCRYPT 2016 | DIGEST-LEVEL | §2.5 |
| NEW-13 | Gabizon, Williamson, Ciobotaru, PLONK, 2019 | DIGEST-LEVEL | §2.5 |
| NEW-14 | Ben-Sasson et al., STARKs, 2018 | DIGEST-LEVEL | §2.5 |
| NEW-15 | EIP-1108, pairing precompile repricing | DIGEST-LEVEL | §2.5 lower bound |
| NEW-16 | circom / circomlib / snarkjs documentation and community circuit benchmarks | UNVERIFIED (constraint counts not re-derived) | §2.5, §4.2, §9.2, §10.4 |
| NEW-17 | VehiclePassport, arXiv:2509.06133 | DIGEST-LEVEL | §2.5 reference point |
| NEW-18 | Semaphore protocol (PSE) documentation | DIGEST-LEVEL | §2.6 |
| NEW-19 | Camenisch & Lysyanskaya, dynamic accumulators, CRYPTO 2002 | DIGEST-LEVEL | §2.7 |
| NEW-20 | Nguyen, accumulators from bilinear pairings, CT-RSA 2005 | DIGEST-LEVEL | §2.7 |
| NEW-21 | W3C Bitstring Status List v1.0 | DIGEST-LEVEL | §2.8 |
| NEW-22 | EIP-4844, blob transactions | DIGEST-LEVEL | §3.3, §9 |
| NEW-23 | Rollup / zkEVM cost literature (e.g., L2 fee analyses) | UNVERIFIED | §3.6, qualitative only |
| NEW-24 | Storage-proof / light-client-in-SNARK literature (e.g., Axiom, Herodotus docs) | UNVERIFIED | §5.3, qualitative only |
| NEW-25 | zkML literature and tooling (EZKL; Kang et al., 2022) | DIGEST-LEVEL | §5.6, §7.4 |
| NEW-26 | Camenisch & Shoup, verifiable encryption, CRYPTO 2003 | DIGEST-LEVEL | §8.3 escrow option (iii) |

## 12. Registry delta rows

| Content Block | T | Source | Ch. | Ready % | Notes |
|---|---|---|---|---|---|
| ZKP-as-structural-requirement argument (createPresentation gap + Allen + SCMS + GDPR) | A | 02 §1 | 5 §5.1 | 80 | Reuses thesis framing; new synthesis of four pressures |
| Five-property taxonomy (SD, unlinkability, predicate, non-revocation, PoP) + computation vs data attestation | A | 02 §1.3, §7.5 | 2 | 85 | Definitions to reuse across suite |
| Mechanism master comparison table (9 mechanisms × 11 axes) | B | 02 §2.9 | 4 Stage 19 | 70 | All cells DIGEST-LEVEL; to be partially replaced by §10 measurements |
| SD-JWT repo scheme vs RFC 9901 deviations (name-keyed digests; EIP-191 key binding) | A | 02 §2.2 | 4 | 90 | Verified against source code |
| Verification placement rule (atomic state change ⇒ on-chain) + verify-off-chain/anchor-event trust assumptions + verifier-oracle | A | 02 §3 | 4, 5 | 80 | Links to 01 taxonomy |
| F8 anchoring resolution (commitment + pairwise DID; never public DID for routine Tier 2) | A | 02 §3.7 | 5 §5.1 | 85 | Load-bearing for 03 and 08 |
| CAV ZK application matrix (9 applications) | B | 02 §4.1 | 4 | 75 | Designs; each maps to a scenario in 04–07 |
| Three-tier VIN scheme with ZK tier and Poseidon-commitment implication | A | 02 §4.2 | 4 | 70 | Raises schema question (§13) |
| Tier 1 stays with SCMS: three reasons | A | 02 §4.7 | 1, 5 | 90 | Settled position for 03 |
| Toll payment without location trail (charge-token/nullifier flow) | A | 02 §4.8 | 4 | 65 | Handed to 06 |
| Agent ZK applications incl. F12-is-public finding and zkML-as-validation-hook | A | 02 §5 | 5 | 75 | Feeds 09, 11 |
| Revocation privacy trade (status list / accumulator / ZK-over-list) with staleness window W and AccumulatorUpdated invalidation event | A/B | 02 §6 | 4 | 75 | Extension event proposed, not spec change |
| Verifiable data beyond ZK: four places for computation attestation | A | 02 §7 | 4, 5 | 80 | Pointer to 09 §6 |
| Threat analysis: ZK protects / does not protect; privacy-when-required tiering; escrow options (i)–(iii) | A | 02 §8 | 4, 5 | 80 | Escrow option (ii) recommended to 03 |
| Parametric ZK cost model per vehicle-year | B | 02 §9.1 | 4 | 70 | Formula only; variables to be bound by 10 |
| Staged ZK build plan (a)–(d) with assertions A-a1…A-d3 and metrics table | B | 02 §10 | 4, 10 | 60 | All pending |

## 13. Open questions for the researcher

1. **ZK-friendly commitments in the VID schema.** Should `lib/vid/` compute attribute commitments (and possibly `credentialHash`) with Poseidon, or carry a dual SHA-256/Poseidon commitment, so that stage (c) circuits are OBU-affordable? This changes the credential object shape that F5 anchors and must be decided before S7 is finalised.
2. **Which mechanism is the Tier 2 default in Family F?** This document argues BBS+ (multi-show unlinkable, no setup, W3C-track); the alternative is AnonCreds v2 (BBS+ plus native predicates and accumulators, but heavier tooling). The choice fixes 03's composite and the thesis's "extension" claim above SCMS.
3. **Escrow design for the forensic crossing.** Option (ii) (threshold-encrypted linkage record anchored via F3) is recommended; option (iii) (verifiable encryption per presentation) is cleaner but costlier. Which does the thesis defend, and who are the *t*-of-*n* authorities in the Canadian setting?
4. **Staleness windows as published policy.** Is the thesis prepared to state per-credential-type `W` values as design parameters (and defend them), or should `W` remain a variable in the model?
5. **Schema quantisation as a registry rule.** Should `CredentialTypeRegistry` schema hashes enforce coarse attributes (quantised dates, bucketed values) to defeat issuer-embedded correlators (§8.2)? This is a governance rule with a privacy rationale and a usability cost.
6. **Reputation aggregation across pairwise DIDs (§5.7).** Is the ZK "I control these leaves" aggregation, or an escrowed reputation oracle, the thesis's answer? It determines whether 09's reputation argument survives unlinkable sessions.
7. **Trusted-setup honesty in 10.** Stage (c) will use a single-party local setup. Is a demonstration-only label sufficient for the thesis, or should the build run a small multi-party ceremony (two or three participants) so that the on-chain verifier's proofs are not trivially forgeable by the author?
8. **The ARM proxy for the OBU.** Which board (and which reference in the thesis) stands in for the OBU for prover timings, and is a proxy measurement acceptable to the committee as evidence for §9.2?
