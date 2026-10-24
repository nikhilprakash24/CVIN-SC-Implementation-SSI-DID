# CVIN-SC · R3 — The I2I and Identity Stack: Requirements, Breaking Points, and the Programme's Solutions, Tied to the Roots

**What a secure and private identity-to-identity transaction needs, which layer of the stack delivers each need, where every layer breaks, and which of the programme's built or specified solutions closes each break — every "X is secured by Y" carrying a tag pair back to the Roots lineage.**

Document 3 of the Roots suite (thread G-R1, provisional) · v0.1 · 2026-09-15 · CVIN-SC Research Programme · UBC ECE MASc
Consumes: R1 v1.1 (L0–L7; T-01–T-24; T-I01–T-I22) · R2 v0.1 (SOL-01–SOL-09; the "secured by below" column; gaps §4) · G-C1 (adversaries A1–A6, W, SR- register) · Building Paths v1.1 preface · P2/P3 (placement, HAA-1, settlement spectrum) · Pass 4 (tiers, 1609.2) · Crux Compendium X1–X6.
Assigns: `BP-L0-01`…`BP-L7-07`; figures `FIG-R1`…`FIG-R6`. **No numeric bound appears in this document**: every quantity is written `PF-⟦n⟧` and specified for R4 in the HANDOFF.
Open inputs: Q-R1 (SCMS unlinkability at Tier 1), Q-R2 (`ISetC.sol` scope), Q-R3 (Certificate Transparency in Related Work) — carried as ⟦placeholders⟧ where they bite.

---

## Part I · The crux

### I.1 What "a secure and private I2I transaction" means, as requirements

Two endpoints, each an *identity* — a vehicle, a roadside unit, a person's wallet, a software agent — exchange either a **message** (no global order needed; e.g., a cooperative-manoeuvre request, a credential presentation) or a **transaction** (a global order is needed; e.g., a key rotation, a credential anchor, a revocation). The security literature's properties, restated for this setting:

| # | Requirement | Meaning here | Message | Transaction |
|---|---|---|---|---|
| R1 | **Authenticity** | the receiver knows which identity sent it | ✓ | ✓ |
| R2 | **Integrity** | it was not altered in transit or at rest | ✓ | ✓ |
| R3 | **Confidentiality** | third parties cannot read it | ✓ | policy (content off-chain; anchor only) |
| R4 | **Non-repudiation** *or* **deniability** | either the sender cannot later deny it (audit), or the transcript proves nothing to a third party (privacy) — a policy choice, not a default | policy | non-repudiation, always |
| R5 | **Unlinkability** | two messages from one identity cannot be tied together by an observer who is not the intended receiver | ✓ where the credential family supports it | anchors are commitments; the *writer* may still be linkable |
| R6 | **Availability / liveness** | the exchange completes within its tier budget | Tier 1/2 | Tier 3 |
| R7 | **Ordering / non-equivocation** | there is one history of key and status changes that every verifier sees the same way | (reads cached state) | ✓ — the ledger's job |
| R8 | **Freshness / replay resistance** | an old message or presentation cannot be re-used | ✓ | ✓ (nonces, chain ID) |

An identity system adds, over and above the channel:

| # | Requirement | Meaning | Set |
|---|---|---|---|
| I1 | **Binding** | a public key is bound to a subject in a way others can resolve | Set A `createDID`, `resolveDID` |
| I2 | **Control proof** | the subject can prove it holds the key without the key leaving it | Set A (signature over challenge) |
| I3 | **Key lifecycle** | rotation, addition, removal, deactivation, with a history no one can rewrite | Set A `updateDID`, `add/removeVerificationMethod`, `deactivateDID` |
| I4 | **Delegation** | a subject can authorise another key or identity to act, scoped and revocable | Set A `addDelegate`, `validDelegate`; Set C |
| I5 | **Attribute issuance** | a trusted issuer signs claims about the subject | Set B `issueCredential` |
| I6 | **Selective disclosure** | the holder shows some claims, or predicates over them, not all | Set B `createPresentation` |
| I7 | **Verification** | a verifier checks issuer signature, holder binding, and status | Set B `verifyCredential` |
| I8 | **Revocation with a bound** | status can change and the change reaches verifiers within a stated window *W* | Set B `revokeCredential` |
| I9 | **Recovery** | key loss does not equal identity loss | Set A controllers / ERC-4337 social recovery |

### I.2 The spine: requirement → layer → root primitive

This table is the document's load-bearing claim. Every later section either derives a breaking point from one of its rows (Part II) or shows a solution restoring one (Part III).

| Requirement | Delivered at | By primitive (tag) | Assumes from below | Programme realisation |
|---|---|---|---|---|
| R1 authenticity | L7 ← L6 ← L1 | signature (T-04/T-05/T-06) over a channel handshake (T-I07/T-I08) with the key resolved at L6 (T-I17) | key↔subject binding (I1); ECDLP | DIDComm v2 (O16) sender-authenticated envelope |
| R2 integrity | L7 ← L1 | AEAD / MAC; hash (T-07) | collision resistance | JWE envelope (T-I09) |
| R3 confidentiality | L7 ← L1 | DH key agreement (T-04) → AEAD; forward secrecy (T-I06/T-I07) | ECDLP; ephemeral-key entropy | DIDComm ECDH-1PU; Paladin private groups (O15) for on-ledger content |
| R4 non-repudiation | L7 ← L5 ← L1 | signature + global order (T-13/T-12) | one history | ledger anchor as audit artefact (G-C1) |
| R4′ deniability | L7 ← L1 | OTR/Signal-style MAC-based authentication (T-I06/T-I07) | — | ⟦not adopted; DIDComm is signature-authenticated⟧ |
| R5 unlinkability | L6 ← L1 | pseudonym rotation (T-I05); unlinkable multi-show (T-I11/T-I13/T-I20); commitment anchors (T-I15) | q-SDH/LRSW; anonymity set | AnonCreds (O12) presentations; SCMS butterfly keys at Tier 1 ⟦Q-R1⟧ |
| R6 availability | L7 ← L0, L3 | gossip/DHT (T-02); consensus liveness (T-11/T-12) | honest majority reachable; partial synchrony | HAA-1 read-path completeness: Tier 1/2 never touch the ledger |
| R7 ordering | L5 ← L3 ← L2 | chain of blocks (T-10) under agreement (T-12/T-13) | ≤ f_B faulty; ≥ honest work | Besu QBFT (SOL-02); public anchor (SOL-03) |
| R8 freshness | L7 ← L5 | nonces; chain ID; block height in presentation | monotone clock / height | replay fields in DIDComm; EIP-155-style domain separation |
| I1 binding | L6 ← L5 | DID document in a verifiable data registry (T-I17) | registry non-equivocation (R7) | `createDID` on O1/O11; Plane A |
| I2 control | L6 ← L1 | Schnorr-type proof or plain signature (T-I10/T-05) | — | signed challenge; `validDelegate` |
| I3 lifecycle | L6 ← L5 ← L2 | ordered, hash-linked key history (T-09/T-10) | R7 | `updateDID` etc.; the archival guarantee R-R3 |
| I4 delegation | L6 | scoped delegate records (T-I17 controllers; ERC-1056 delegates) | I3 | `addDelegate`; Set C ⟦Q-R2⟧ |
| I5 issuance | L6 ← L1 | issuer signature on attributes; CL/BBS+ on committed attributes (T-I11) | issuer key integrity | `issueCredential`; content off-chain, anchor on-chain (formal spec) |
| I6 selective disclosure | L6 ← L1 | ZKP (T-I10), pairings (T-I11), SNARK predicates (T-I14) | assumption class per scheme | `createPresentation` — native only in O12 (X2) |
| I7 verification | L6 ← L7, L2 | signature check + status check against list/accumulator (T-I12) | status freshness within W | `verifyCredential` against σ-bounded cache (HAA-1 Plane V) |
| I8 revocation | L6 ← L2 ← L5 | status list root or accumulator on-chain (T-I12; SOL-09) | anchoring interval; propagation | `revokeCredential`; profiles SL / AC |
| I9 recovery | L6 ← L5 | controller change; multi-key DID documents; account abstraction (O7) | I3 | ⟦programme choice per option⟧ |

**One sentence to carry forward.** Everything above the ledger borrows *ordering* from it and *nothing else*; everything above L1 borrows *unforgeability* from it and nothing else; the identity layer's own contribution is *binding* and *disclosure discipline*; the channel's own contribution is *confidentiality with freshness*. A breaking point is a place where a layer's borrowed property fails to arrive.

*FIG-R1 (stack with requirement arrows) accompanies this section.*

---

## Part II · Layer by layer: what each layer delivers, and where it breaks

Format for every breaking point: **attack** · **precondition** (what must already be true) · **consequence upward** (which requirement or function in Part I fails, and at which higher layer it is felt) · **closed by** (the primitive or SOL- that restores it; "accepted" if the programme carries it as residual) · **bound** (the R4 placeholder). Adversary labels A1–A6 are G-C1's.

### II.0 L0 — Communication substrate

**Delivers upward:** delivery of transactions to a proposer, of blocks to validators, of status updates to verifiers, and of I2I messages to endpoints — with no authenticity, integrity or confidentiality of its own (T-01). Everything a higher layer needs from L0 is *liveness* and *non-partition*.

| BP | Attack | Precondition | Consequence upward | Closed by | Bound |
|---|---|---|---|---|---|
| BP-L0-01 | **Eclipse** — an endpoint's peers are all adversarial | attacker controls the victim's peer table (T-02 open discovery) | victim sees a forked view: stale keys (I3), stale status (I8), or an unconfirmed transaction reported final (R7) | diverse peer selection; authenticated peers in a consortium (SOL-02 removes open discovery); verifier reads from ≥ k independent Plane-V sources | PF-⟦1⟧ |
| BP-L0-02 | **Partition** | network split ≥ liveness threshold duration | consensus stalls (L3) → no Tier-3 writes; revocation cannot propagate → *W* grows unbounded (I8) | HAA-1 read path: Tier 1/2 operate on cached state within σ; QBFT liveness bound (T-12) | PF-⟦2⟧ |
| BP-L0-03 | **Sybil at the network layer** — peer flooding | open membership (T-02), no admission cost | eclipse becomes cheap; gossip degraded; (at L3) any identity-count vote is void (T-03) | permissioned validator set (SOL-02); PoW/PoS cost at L4 for public settlement (SOL-04) | PF-⟦3⟧ |
| BP-L0-04 | **Metadata leakage** — who submitted what, when | a public mempool or observable gossip (Options B/C) | linkability of the *writer* even when the payload is a commitment (R5 partially fails for transactions) | no public mempool under Option A (SOL-02); relay/mixing path for Option B submissions (P3); batch anchoring so one writer covers many subjects (SOL-03, T-I19) | PF-⟦4⟧ (anonymity set of a batch) |
| BP-L0-05 | **Off-chain data unavailability** — the content behind an anchor cannot be fetched | Plane-D owner fails; CAS unpinned; issuer archive lost | anchor verifies but nothing to verify against: I5/I7 fail; forensic reconstruction (R-R3) fails | named availability owner per class (SOL-05 Plane D); consortium archive-node ring; wallet primary custody for S5 | PF-⟦5⟧ (replication factor vs loss probability) |

### II.1 L1 — Cryptographic primitives

**Delivers upward:** unforgeability (T-05), integrity (T-07), key agreement (T-04), and proof-without-disclosure (T-I10/T-I11/T-I14). Every layer above borrows exactly these. L1 has no liveness property; it cannot "fail slowly", it fails by assumption collapse or by implementation error.

| BP | Attack | Precondition | Consequence upward | Closed by | Bound |
|---|---|---|---|---|---|
| BP-L1-01 | **Weak key generation** — low-entropy or predictable keys | poor RNG on the device (the 2013 Android wallet failures; embedded ECUs) | private key recoverable → I2 fails for that identity; every signature forgeable | hardware RNG / HSM (EVITA/SAE J3101 in the CAV domain, T-I05 context); key-generation attestation | PF-⟦6⟧ (effective entropy κ vs nominal k) |
| BP-L1-02 | **ECDSA nonce reuse or bias** | two signatures with the same or biased *k* (the PlayStation 3 and 2013 Bitcoin incidents) | private key recovered from two signatures → same as BP-L1-01 | deterministic nonces (RFC 6979); Schnorr/EdDSA where the option allows; QBFT commit seals use ECDSA — validator keys at risk too | PF-⟦7⟧ |
| BP-L1-03 | **Hash function break** — collision or second preimage | cryptanalytic advance (MD5 2004, SHA-1 2017) | Merkle proofs forgeable (L2), commitments no longer binding (SOL-03), tx IDs colliding (L5) | SHA-256 with no known attack; algorithm agility in DID documents (T-I17 allows multiple verification methods); two-family addressing (T-07) | PF-⟦8⟧ (generic birthday bound at h bits) |
| BP-L1-04 | **Quantum** — Shor on ECDLP/RSA; Grover on hashes | cryptographically relevant quantum computer | every public key with an exposed key is forgeable (Shor); hash security halved (Grover) | migration path: FIPS 203–205 (not deployed in any evaluated option); hash-based commitments and Merkle structures survive with doubled parameters; "harvest now, decrypt later" applies to confidentiality (R3), not to signatures already verified | PF-⟦9⟧ (Grover-adjusted h; Shor exposure window) |
| BP-L1-05 | **Pairing-assumption failure** — q-SDH / LRSW weaker than believed | cryptanalytic advance on pairing-friendly curves (the 2016 kappa-TNFS results reduced BN-254 security) | CL/BBS+ credentials forgeable → I5/I6 fail for AnonCreds (O12) but not for ECDSA-based options; the 12/12 ranking carries this assumption class (R2 decision 5) | curve upgrade (BLS12-381); the interface is scheme-agnostic; ECDSA fallback for I5 with loss of R5 | PF-⟦10⟧ (security level of the deployed curve) |
| BP-L1-06 | **Trusted-setup compromise** (Groth16) | toxic waste retained by a setup participant | false proofs accepted by the on-chain verifier (O15) → I6/I7 fail silently | MPC ceremonies; transparent systems (Bulletproofs, STARKs) at higher verification cost (U-17 trade-off) | PF-⟦11⟧ |
| BP-L1-07 | **Side-channel key extraction** — timing, power, fault | physical or co-tenant access to the signer | I2 fails for that identity | constant-time implementations; HSM (T-I05 domain); rotation (I3) limits the window | accepted at the interface level; bounded by rotation period, PF-⟦12⟧ |

### II.2 L2 — Authenticated data structures

**Delivers upward:** tamper-evidence of an ordered history (T-09/T-10), membership proofs (T-08), non-membership proofs (T-I12), and constant-size commitments to large sets — the properties that make a *registry* auditable and a *status* checkable.

| BP | Attack | Precondition | Consequence upward | Closed by | Bound |
|---|---|---|---|---|---|
| BP-L2-01 | **Merkle proof forgery** | BP-L1-03 (second preimage) or a leaf/node domain-confusion bug (the 2012 Bitcoin CVE-2012-2459 class) | a verifier accepts a credential/status not in the committed set → I7 fails | domain-separated leaf hashing; sorted-leaf or fixed-depth trees; SHA-256 | PF-⟦8⟧ (same as L1) |
| BP-L2-02 | **History rewrite / deep reorg** of the private chain | the L3 safety bound violated (BP-L3-01) *and* no external anchor | key history (I3) and status history (I8) rewritten; forensic record (R-R3) falsified | public anchoring in commitment form + checkpoint (SOL-03): a rewrite after the checkpoint is *detectable* by anyone holding the public root; not *preventable* | PF-⟦13⟧ (detection latency = anchoring interval τ_a + public finality) |
| BP-L2-03 | **Accumulator witness staleness** | set changed; holder's witness not updated (T-I12 cost) | holder cannot prove non-revocation → false negative (I8 blocks a valid credential); or verifier accepts an old accumulator value → false positive | witness distribution via Plane D/V (SOL-09 Profile AC); `ttl` on accumulator reads set from W; Profile SL as the alternative with no per-holder update | PF-⟦14⟧ (witness-update cost vs set churn) |
| BP-L2-04 | **Batch content unavailability** (Sidetree pattern) | the CAS behind an anchored batch is lost | the anchored DID operations exist but cannot be resolved → I1/I3 fail for that batch | = BP-L0-05; Sidetree's answer is replication; HAA-1's is the Plane-D owner | PF-⟦5⟧ |
| BP-L2-05 | **Registry equivocation** — different verifiers shown different DID documents or status roots | a registry server (Plane V) that is not bound to Plane A; or an eclipsed verifier | I1/I7/I8 fail selectively; targeted acceptance of a revoked credential | every Plane-V response carries the Plane-A root it was derived from; verifier checks root against its own Plane-A view (the "equivocation hole closed by anchoring", P3 §2.2) | PF-⟦15⟧ (cache-staleness σ) |

### II.3 L3 — Distributed agreement

**Delivers upward:** one history (R7), with finality that is deterministic (QBFT/RBFT, T-12), probabilistic (PoW, T-13), or economic (PoS). Liveness and safety are the two properties; every consensus breaking point is a failure of one, and FLP (T-11) says you cannot have both without a timing assumption.

| BP | Attack | Precondition | Consequence upward | Closed by | Bound |
|---|---|---|---|---|---|
| BP-L3-01 | **Safety loss in BFT** — conflicting blocks both finalised | > f_B of N_v validators Byzantine, with N_v ≥ 3f_B+1 assumed (T-12) | R7 fails: two key histories; BP-L2-02 becomes possible | governance-diverse validator set (SOL-02 requirement); public checkpoint makes the fork *visible* (SOL-03) | PF-⟦16⟧ (collusion probability for N_v validators with independence model) |
| BP-L3-02 | **Liveness loss in BFT** | ≥ f_B+1 validators offline or partitioned (BP-L0-02) | no new blocks: Tier-3 writes stall; revocation propagation halts → W unbounded | QBFT round-change; Tier 1/2 independence from the ledger (HAA-1); the residual is a *safety-preserving* stall, which is the right failure direction for identity | PF-⟦2⟧ |
| BP-L3-03 | **Timing-assumption failure** | partial synchrony violated for longer than the round timeout | QBFT may lose liveness (not safety); PoW may see elevated orphan rate | timeout tuning; bounded by BP-L3-02 | PF-⟦17⟧ (round timeout vs propagation) |
| BP-L3-04 | **Long-range attack** (PoS / historical keys) | old validator keys leaked; a client syncing from genesis | a fabricated alternative history looks valid → I3 rewritten for a new verifier | weak subjectivity checkpoints; for HAA-1: the *public* checkpoint (SOL-03) is the weak-subjectivity anchor; not applicable to QBFT with a known current set if clients pin the set | PF-⟦18⟧ |
| BP-L3-05 | **Probabilistic-finality reversal** (PoW, Option C) | attacker with hashpower fraction (1−α) mining a competing chain from depth z | a credential anchor or key rotation "finalised" at depth z is reverted → R7 briefly fails; the C16 variance finding | wait depth z chosen for the required reversal probability; use Option A/B for identity writes | PF-⟦19⟧ (Nakamoto §11 catch-up probability at z, α) |
| BP-L3-06 | **Sequencer censorship / admissibility** (Option B) | a single rollup sequencer | Tier-3 writes delayed or excluded; revocation delayed (I8) | forced-inclusion via L1; SR-16 in the security thread | PF-⟦20⟧ (forced-inclusion delay) |

### II.4 L4 — Economic and governance mechanisms

**Delivers upward:** the cost that makes L3's honest-majority assumption *true in practice*: proof-of-work cost (T-14/T-15/T-18) on public chains, stake and slashing on PoS, and *governance plus accountability* on permissioned chains — where there is no cost function and the substitute is that misbehaviour is attributable to a named validator (Family E v2.0 finality comparison).

| BP | Attack | Precondition | Consequence upward | Closed by | Bound |
|---|---|---|---|---|---|
| BP-L4-01 | **51% attack** (PoW) | attacker hashpower ≥ honest hashpower | BP-L3-05 at any depth; double-spend of anchors; R7 fails | not applicable to Option A; Option C carries it; bounded by the cost of hashpower | PF-⟦21⟧ (cost to reach (1−α) for T) |
| BP-L4-02 | **Selfish mining** | hashpower ≥ ~1/3 with good network position (Eyal–Sirer 2014) | reduced effective honest fraction; BP-L3-05 bound weakens | as above; note the *effective* α in PF-⟦19⟧ | PF-⟦22⟧ |
| BP-L4-03 | **Fee-market failure / variance** (Options B/C) | congestion | Tier-3 writes priced out; revocation delayed (I8); the U-17 finding that *variance*, not level, is the problem | Option A free-gas (SOL-02); batching (SOL-03) amortises; L2 sub-cent cost | PF-⟦23⟧ (cost distribution; percentile at which W is exceeded) |
| BP-L4-04 | **Validator collusion** (permissioned) | ≥ f_B+1 validators share an interest — the *correlated validator–issuer* row in G-C1 | BP-L3-01 with a motive: rewrite a competitor's key history, suppress a revocation | governance diversity requirement (SOL-02); public checkpoint (SOL-03) converts collusion from *undetectable* to *provable*; on-chain validator signing history (O11 advantage over O10) | PF-⟦16⟧ |
| BP-L4-05 | **Capacity exhaustion** (free-gas) | no fee → no back-pressure; a flood of valid transactions | block budget consumed; Tier-3 writes delayed; the M-T2 ceiling | per-class capacity governance (M-T2 from the genesis manifest, WO-P4); admission control at Plane A's RPC — the permissioned analogue of T-18 | PF-⟦24⟧ (M-T2 ceiling per class mix) |
| BP-L4-06 | **Governance capture** | the validator-admission process itself controlled by one party | BP-L4-04 becomes structural | out of the technical scope; stated as a trust-base assumption of Option A; Option B/C as the alternative with a larger trust base | accepted; documented in SR- register |

### II.5 L5 — Ledger semantics

**Delivers upward:** a global order over state transitions with no equivocation (T-24 generalised), executed by contracts whose code is itself part of the ordered state.

| BP | Attack | Precondition | Consequence upward | Closed by | Bound |
|---|---|---|---|---|---|
| BP-L5-01 | **Double-spend / conflicting update** — two key rotations for one DID in the same interval | absence of R7 (BP-L3-01) or a race at the RPC | I3 ambiguous | ordering by consensus; per-DID nonce in the contract (ERC-1056 signed-variant nonces) | — (structural once R7 holds) |
| BP-L5-02 | **Replay across chains or contracts** | same signed payload valid on two chains (pre-EIP-155 pattern) or two registry deployments | a key change intended for the sandbox replayed on production | chain-ID and contract-address domain separation in every signed identity operation (R8) | — |
| BP-L5-03 | **Transaction malleability** | signature encoding not canonical | anchors referenced by tx hash break | canonical encoding (low-s); reference anchors by content commitment, not by tx hash (SOL-03) | — |
| BP-L5-04 | **Contract defect or upgrade-key compromise** | a bug in the registry contract; or an upgradeable proxy with a privileged admin | every identity on that registry is at the admin's mercy → I1–I4 fail | immutable registries (ERC-1056 has no admin); audited upgrade paths with time-locks; the sandbox's T-series tests as the *evidence* (SOL-01) | accepted; evidence-tier statement per option (P6 field) |
| BP-L5-05 | **Front-running / reordering of identity ops** | a proposer sees a pending key rotation | a compromised old key races the rotation (BP-L6-02 amplifier) | no public mempool (SOL-02); commit-reveal for rotations if on Option B/C | PF-⟦25⟧ (race window = inclusion delay) |

### II.6 L6 — Identity

**Delivers upward:** I1–I9. This is the layer the programme evaluates; every breaking point here maps to a function of `IMinimalSSI` and to an adversary in G-C1.

| BP | Attack | Precondition | Consequence upward | Closed by | Bound |
|---|---|---|---|---|---|
| BP-L6-01 | **Key loss** | single key, no controller, no delegate | identity unrecoverable; credentials orphaned (I9 fails) | multi-key DID documents (T-I17); controller DIDs; ERC-4337 social recovery (O7); `addDelegate` as pre-registered recovery (Set A) | — |
| BP-L6-02 | **Key compromise and the rotation race** | attacker holds the key; subject rotates via `updateDID` | between compromise and rotation-finality, attacker signatures are valid; if the attacker rotates *first*, the subject is locked out | rotation finality time = inclusion + finality (Option A ≈ block period); pre-authorised recovery key; the archival record shows *which* rotation came first (R-R3, non-repudiation) | PF-⟦26⟧ (rotation window under each settlement option) |
| BP-L6-03 | **Issuer key compromise** | issuer signing key exposed | forged credentials valid until issuer key rotated *and* verifiers learn of it (I5/I7) | issuer DID key rotation (I3) propagates via the registry; credential-definition versioning (AnonCreds `CRED_DEF`); mass revocation via status list (SOL-09 SL) | PF-⟦27⟧ (issuer-rotation propagation = W) |
| BP-L6-04 | **Revocation-latency window W** | verifier reads cached status; revocation is a Tier-3 write | a revoked credential is accepted for up to W (I8) | W engineered per manoeuvre class: `t_include + t_finalise + t_propagate + t_cache + t_poll` (G-C1 §2.7); `ttl` from W not convenience; Profile SL/AC choice (SOL-09) | PF-⟦28⟧ (W under Options A/B/C and each profile) |
| BP-L6-05 | **Correlation / linkability** | same identifier, same signature, or same revocation-check index used at two verifiers | R5 fails: tracking; GDPR exposure | pseudonymous DIDs per relationship; unlinkable presentations (O12, T-I11); herd privacy in status lists (SOL-09; ⟦anonymity-set bound⟧); pseudonym certificates at Tier 1 (T-I05, ⟦Q-R1⟧) | PF-⟦29⟧ (anonymity set / k-anonymity of status list) |
| BP-L6-06 | **Confused deputy in delegation** | a delegate (agent, Set C) holds authority for two principals, or an unscoped delegate | actions attributed to the wrong principal; over-broad authority | scoped delegates (`addDelegate` with type and expiry); per-principal agent keys; capability-based delegation in ERC-8004 / Set C ⟦Q-R2⟧ | — |
| BP-L6-07 | **Issuer-side equivocation** | issuer publishes different schemas / status to different verifiers | selective acceptance | schema and CRED_DEF anchored on Plane A (O10/O11 transaction types); Profile SL root anchored each epoch | PF-⟦15⟧ |
| BP-L6-08 | **The createPresentation gap (X2)** | an EVM option (O1–O9) used alone | I6 absent → either full disclosure (R5 fails) or off-chain middleware with its own trust | native presentation in O12; Family F composition (SOL-08: E2 + E6 + O12 pattern) | — (coverage, not a bound) |
| BP-L6-09 | **Schema / credential-definition poisoning** | write access to the schema registry | verifiers accept malformed or attacker-defined credentials | endorser/steward write permissions (O10); contract access control (O11); anchoring for audit | — |
| BP-L6-10 | **Recovery abuse** | the recovery path (social, delegate) is easier to attack than the key | BP-L6-02 via the back door | threshold recovery; time-locks on recovery; the recovery path recorded on-chain (non-repudiation) | PF-⟦30⟧ (threshold vs collusion) |

### II.7 L7 — Application / I2I

**Delivers upward:** R1–R8 to the use case, over an authenticated channel between two L6 identities.

| BP | Attack | Precondition | Consequence upward | Closed by | Bound |
|---|---|---|---|---|---|
| BP-L7-01 | **Endpoint compromise** | malware on the wallet / ECU | everything: the channel is secure between the attacker and the peer | out of cryptographic scope; hardware isolation (T-I05 domain); rotation and revocation limit blast radius (I3/I8) | accepted |
| BP-L7-02 | **Metadata leakage — who talks to whom** | observable transport; mediator logs | R5 fails at the *communication* level even with unlinkable credentials | mediators (DIDComm Mediation protocol); onion/relay for Option B submissions; batching | PF-⟦4⟧ |
| BP-L7-03 | **Stale cached state at the verifier** | verifier's Plane-V cache older than σ | BP-L6-04 realised at the application; a rotated-out key accepted | σ-bounded reads with root check (BP-L2-05 closer); `ttl` from W | PF-⟦15⟧ |
| BP-L7-04 | **Presentation replay** | no verifier nonce or expiry in the presentation | a captured presentation re-used | verifier-supplied nonce and domain in every presentation request (Present Proof); expiry | — |
| BP-L7-05 | **Handshake downgrade / MITM** | key resolution (L6) not authenticated, or weak-suite negotiation | R1/R3 fail | DID resolution over the anchored registry; fixed Noise pattern / DIDComm v2 fixed suites (T-I08) | — |
| BP-L7-06 | **Non-repudiation / deniability mismatch** | a flow that legally needs audit is deniable, or a privacy flow leaves a signed transcript | either forensic failure or GDPR exposure | policy per message class: signed (auditable) vs MAC-authenticated (deniable) — DIDComm supports `authcrypt` vs `anoncrypt`; ⟦programme must choose per class⟧ | — |
| BP-L7-07 | **Tier-budget violation** | any ledger touch on the Tier 1/2 path | the safety application misses its deadline (X4) | HAA-1 read-path rule: Tier 1/2 read cached L6 state only; Tier 3 is the only ledger tier | PF-⟦31⟧ (latency budget vs read-path cost) |

*FIG-R2 (breaking-point heat-map) and FIG-R6 (who-secures-whom graph) accompany this part.*

---

## Part III · The trilemma and the programme's solutions

### III.1 The cost surface

The "blockchain trilemma" — decentralisation, security, scalability, choose two — is a slogan; stated as a cost surface it becomes usable. Fix the *security* axis at the level identity requires (R7 non-equivocation, I8 bounded revocation, R5 unlinkability). Then the remaining two axes trade off through three knobs the settlement spectrum exposes:

| Knob | Decentralisation ↑ means | Scalability ↑ means | Root of the trade-off |
|---|---|---|---|
| **Trust base** — who must collude to break R7 | larger, more anonymous validator/miner set | smaller, known set with deterministic finality | T-03 (Sybil) forces cost or identity; T-12 needs identity, T-13 needs cost |
| **Finality latency** — how long until a write is safe | probabilistic (T-13), depth z | deterministic at quorum (T-12), one block period | FLP (T-11): deterministic finality needs a timing assumption and a known set |
| **Cost per write** — what a Tier-3 operation costs | fee market, variance (BP-L4-03) | free-gas with capacity governance (BP-L4-05) | T-14/T-18: cost is the Sybil defence; remove it and you need admission control |

Zooko's triangle (T-I16) is the same surface for *naming*: decentralised, secure, human-meaningful — DIDs give up the third.

### III.2 The solutions placed on the surface

| SOL | Position | Closes | Accepts as residual | Cost |
|---|---|---|---|---|
| **SOL-01** local sandbox | off the surface — a *measurement* point with N_v = 1 | nothing at L0/L3/L4 (R2 decision 4); measures L5/L6 execution and coverage | all consensus and network breaking points, by construction | zero consensus latency (G-B §1.4 caveat) |
| **SOL-02** consortium QBFT (Option A) | small trust base, deterministic finality, free-gas | BP-L0-03, BP-L0-04, BP-L3-05, BP-L4-01/02/03, BP-L5-05 | BP-L4-04 (collusion), BP-L4-06 (capture), BP-L4-05 (capacity) | governance; M-T2 capacity ceiling |
| **SOL-03** public anchoring + checkpoint | adds *detectability* without moving the trust base | BP-L2-02, BP-L2-05, BP-L6-07 (equivocation → provable); converts BP-L4-04 from undetectable to detectable | prevention of collusion (still governance) | one A2-rung tx per interval τ_a; detection latency PF-⟦13⟧ |
| **SOL-04** public L2/L1 (Options B/C) | maximal trust base; probabilistic or batch finality; fee market | BP-L4-04/06 by dilution | BP-L0-04 (mempool), BP-L3-05/06, BP-L4-03 (variance) | latency and cost variance; PF-⟦19/20/23⟧ |
| **SOL-05** HAA-1 | the *composition*: Option A or B for Plane A + SOL-03 + Plane V/D | the union above plus BP-L6-04 (W engineered), BP-L7-03/07 (σ-bounded reads, tiers) | BP-L4-04 as governance; BP-L0-05 as an ownership obligation | four planes to operate; named owners |
| **SOL-06** `IMinimalSSI` | orthogonal — the ruler | BP-L6-08 by *naming* the gap | — | — |
| **SOL-07** LFDT stack | L6/L7 realisation on SOL-02 | BP-L6-05 (unlinkable presentations), BP-L6-08 (native I6), BP-L7-05 (fixed suites) | BP-L1-05 (pairing assumptions), BP-L2-03 (witness churn) | anoncreds-rs FFI; stronger assumption class |
| **SOL-08** Family F (O18) | L5–L7 composition | BP-L6-08 at minimum cost | inherits its components' residuals | derived, not measured |
| **SOL-09** profiles SL / AC | the two engineerable forms of BP-L6-04 | BP-L6-04 with a stated W; BP-L6-05 via herd privacy (SL) or holder-side proof (AC) | SL: linkable index unless list large; AC: BP-L2-03 witness churn | WO-P3 prices the crossover |

### III.3 The analytical centre: why the hybrid, stated in trilemma terms

**Local sandbox (SOL-01) is the lower bound on cost and the origin of the axes** — it tells us what an identity operation costs when consensus costs nothing. **Public chain (SOL-04, Option C) is the upper bound on trust base** — it tells us what non-equivocation costs when nobody is trusted. Neither is deployable for the vehicular tiers: the sandbox has no security, the public chain has variance (BP-L4-03) and probabilistic finality (BP-L3-05) that cannot be reconciled with a bounded W.

The hybrid moves along the surface in two steps. **Step 1 (SOL-02):** shrink the trust base to a governance-diverse consortium and buy deterministic finality and no mempool. This *creates* BP-L4-04 and BP-L4-06 — a small set can collude, and the admission process can be captured. **Step 2 (SOL-03):** rather than enlarge the trust base again (which would reintroduce variance), anchor the consortium's state root to a public chain in commitment form. This does not prevent collusion; it makes collusion *provable after the fact* by anyone holding the public root, at a cost that is negligible because one transaction covers an interval of consortium activity. The residual is honest: **the hybrid trades prevention for detection at L4**, and the thesis should say so in those words. What the detection buys is the forensic property the CAV domain actually needs (R-R3, Building Paths preface): not that a rewrite is impossible, but that a rewrite cannot be *hidden*.

The E2 + E6 four-way separation — public anchoring, public status, private content, provable claims — is the same move at L6: the *registry* is public and non-equivocable, the *content* is private, and the *proof* is what crosses the boundary (T-I14 on-chain verification in O15, T-I15 commitments as anchors). EDPB v2.0 ¶52–54 (P4 KD-P1) is the regulatory statement of exactly this separation.

*FIG-R3 (trilemma surface with SOL points) and FIG-R4 (HAA-1 with the trust boundary) accompany this part.*

---

## Part IV · From roots to identity transactions: three flows down the stack

Each flow is traced on the HAA-1 default (Plane A = Option A Besu QBFT, registry = O11, credentials = O12, channel = O16) with the O1 EVM-baseline counter-trace noted where it differs. Every step names its layer and its tag.

### IV.1 Flow 1 — `createDID` and first key rotation

| # | Step | Layer | Tag | What it borrows from below |
|---|---|---|---|---|
| 1 | Wallet generates key pair *(pk, sk)* on secp256k1 (O1/O11) or the option's curve | L1 | T-06; BP-L1-01 | RNG entropy κ (PF-⟦6⟧) |
| 2 | DID derived: O1 — the account address `RIPEMD-160(SHA-256(pk))`-style / EVM `keccak(pk)[12:]`, so `createDID` is zero-gas (K-19); O11 — a `NYM`-equivalent Solidity write | L1→L6 | T-07; T-I17 | collision-free address space (PF-⟦1–4 of R4 §1⟧) |
| 3 | (O11 only) transaction signed with *sk*, submitted to Plane A's RPC | L1, L0 | T-05; BP-L0-04 | no public mempool (SOL-02) |
| 4 | QBFT proposer includes it; quorum of commit seals; block final | L3 | T-12; BP-L3-01/02 | N_v ≥ 3f_B+1, partial synchrony (PF-⟦16, 17⟧) |
| 5 | Block header's state root now commits to the DID document | L2 | T-08/T-10 | SHA-256/keccak second-preimage (PF-⟦8⟧) |
| 6 | At the next interval τ_a, Plane A's root is checkpointed to the public chain | L2→L5 (public) | SOL-03; T-I15 | public-chain finality (PF-⟦13, 19⟧) |
| 7 | **Rotation:** wallet signs `updateDID` (new pk) with the *old* sk; steps 3–6 repeat | L6 | Set A; BP-L6-02 | rotation window = inclusion + finality (PF-⟦26⟧) |
| 8 | Plane V refreshes its cache from the new root; verifiers reading within σ see the new key; a verifier eclipsed (BP-L0-01) or stale (BP-L7-03) may still see the old one for ≤ σ | L2/L7 | BP-L2-05; SOL-05 | σ (PF-⟦15⟧) |
| 9 | Archive ring retains both DID-document versions with block heights — the forensic record of *which* rotation came first | L2 (Plane D) | R-R3; BP-L0-05 | availability owner (PF-⟦5⟧) |

**Counter-trace (O1 baseline):** step 2 costs nothing and step 7 is `changeOwner` / `addDelegate` on the ERC-1056 registry; there is no schema layer and no native presentation, so flows 2 and 3 cannot run on O1 alone (BP-L6-08).

### IV.2 Flow 2 — issue → present → verify with selective disclosure

| # | Step | Layer | Tag | What it borrows from below |
|---|---|---|---|---|
| 1 | Issuer's DID, schema, and credential definition already on Plane A (O10/O11 `SCHEMA`, `CRED_DEF`) | L6 ← L5 | T-I20; BP-L6-09 | write permission; anchoring |
| 2 | Issuer and holder open a DIDComm v2 channel: DIDs resolved via Plane V (root-checked), ECDH-1PU envelope | L7 ← L6 ← L1 | T-I18; T-I09; T-04 | BP-L7-05 closed by anchored resolution |
| 3 | Issuer signs the attribute bundle with a CL signature over committed attributes; credential content travels in the channel, **never** to the ledger; only its commitment may be anchored (formal spec; EDPB ¶53) | L1, L6 | T-I11; T-I15; Set B `issueCredential` | q-SDH (PF-⟦10⟧) |
| 4 | Issuer adds the credential's revocation index to the accumulator (Profile AC) or status list (Profile SL); Plane A write; witness/ list distributed via Plane D/V | L2 ← L5 | T-I12; SOL-09 | BP-L2-03 |
| 5 | Verifier sends a Present Proof request with nonce, domain, and the predicate ("licence class ∈ {C,D}", "not revoked at root *r*") | L7 | BP-L7-04 | freshness (R8) |
| 6 | Holder constructs the presentation: ZK proof of signature knowledge + predicate + non-revocation, bound to the nonce | L1 → L6 | T-I10; T-I11; T-I14; Set B `createPresentation` | this is the step absent in O1–O9 (X2) |
| 7 | Verifier checks: proof validity, issuer key via Plane V (σ-bounded, root-checked), accumulator/list root against its own Plane-A view | L6 ← L2 ← L7 | Set B `verifyCredential`; BP-L2-05; BP-L7-03 | σ, W (PF-⟦15, 28⟧) |
| 8 | (Optional, Tier 3) verifier anchors a commitment to the presentation as an audit artefact — not for real-time decision (G-C1) | L5 | SOL-03; R4 non-repudiation | anonymity of the anchor batch (PF-⟦4⟧) |

Steps 5–7 are the unlinkable path: two verifiers cannot correlate presentations (BP-L6-05 closed) *provided* the status check itself is not a linkable index — Profile AC gives this by construction, Profile SL by herd size (PF-⟦29⟧).

### IV.3 Flow 3 — revoke and observe the window W

| # | Step | Layer | Tag | Contributes to W |
|---|---|---|---|---|
| 1 | Issuer decides to revoke (compromise reported, licence suspended) — *t₀* | L6 | Set B `revokeCredential` | — |
| 2 | Issuer signs the accumulator update / list-root update; submits to Plane A | L1, L0 | T-05 | `t_include`: RPC + wait for proposal (M-L2, half a block period on average) |
| 3 | QBFT finality | L3 | T-12 | `t_finalise` (Option A ≈ block period; B batch; C depth z — PF-⟦28⟧) |
| 4 | New root propagates to Plane V instances; witnesses / list re-published to Plane D | L0, L2 | T-02; SOL-09 | `t_propagate` — an L0 gossip property (R2 gap 4.2) |
| 5 | Verifier caches expire and re-poll | L7 | SOL-05 | `t_cache + t_poll` — set from the W budget, not from load |
| 6 | First verifier that would have accepted the credential now rejects it — *t₁*; **W = t₁ − t₀** | L6 | BP-L6-04 | the sum of 2–5 |
| 7 | Checkpoint to the public chain at the next τ_a — this does **not** shorten W; it makes the revocation's *timing* provable (forensic) | L5 (public) | SOL-03 | detection, not reduction (PF-⟦13⟧) |

What each settlement option buys: Option A makes `t_finalise` deterministic and small; Option B makes it soft-seconds with an L1-hard tail; Option C makes it probabilistic and large. The hybrid's value for W is therefore in steps 2–3; its value for *accountability* is in step 7; and steps 4–5 are the programme's to engineer regardless of chain — which is why W decomposes into named terms with owners (G-C1 §2.7).

*FIG-R5 (the three flows as sequence diagrams) accompanies this part.*

---

## Closing: the narrative in one paragraph

Bitcoin solved one problem — non-equivocation of a ledger without an owner — by composing forty years of primitives (R1). Identity needs that property for its *registry* and five more it never needed for cash: binding, disclosure discipline, unlinkability, bounded revocation, and an authenticated channel (R1 §10.5). Each of those is borrowed from a specific lower layer and fails at a specific breaking point when the borrowed property does not arrive (Part II). The programme's solutions are not a single architecture but a set of positions on the trilemma's cost surface (Part III): a sandbox to measure, a consortium chain to get deterministic finality, a public anchor to make the consortium's failures provable, a hybrid to compose them with the read-path discipline the vehicular tiers demand, and a credential stack that supplies the one function the EVM options lack. The three flows (Part IV) show the same stack traversed in practice; the quantities left as `PF-⟦n⟧` are what R4 must now bound.

---

## HANDOFF (paste at the top of Prompt 3)

**Thread:** G-R1 (provisional), Prompt 2 complete, 2026-09-15.
**Files issued:** `claude_CVIN_SC_Roots_I2I_Identity_Stack_R3_v0-1.md`; `FIG-R1_stack_requirements.svg`; `FIG-R2_breaking_point_heatmap.svg`; `FIG-R3_trilemma_solutions.svg`; `FIG-R4_HAA1_trust_boundary.svg`; `FIG-R5_three_flows.svg`; `FIG-R6_secured_by_graph.svg`.
**BP- ranges assigned:** L0-01…05 · L1-01…07 · L2-01…05 · L3-01…06 · L4-01…06 · L5-01…05 · L6-01…10 · L7-01…07 (51 total).
**SOL → BP closure (compact):** SOL-02 closes L0-03/04, L3-05, L4-01/02/03, L5-05; accepts L4-04/05/06. SOL-03 closes L2-02/05, L6-07 (as detection); converts L4-04 to detectable. SOL-04 closes L4-04/06 by dilution; introduces L0-04, L3-05/06, L4-03. SOL-05 = union + L6-04, L7-03/07. SOL-07 closes L6-05/08, L7-05; accepts L1-05, L2-03. SOL-08 closes L6-08. SOL-09 closes L6-04 (stated W), L6-05 (SL herd / AC holder-proof); accepts L2-03. SOL-01 closes nothing; measures L5/L6.
**PF-⟦n⟧ placeholders R4 must fill (quantity — variables):**
1 eclipse: P(all peers adversarial) — peer count, adversary fraction · 2 partition/liveness: max stall before W exceeded — f_B, N_v, round timeout · 3 network-Sybil cost — admission cost · 4 anonymity set of an anchor batch / relay — batch size, submitters · 5 off-chain loss probability — replication r, per-node loss · 6 key-pair collision & effective entropy — κ, n · 7 nonce-reuse recovery — (qualitative bound; sample count) · 8 hash collision / second-preimage — h, number of objects · 9 quantum: Grover-adjusted h; Shor exposure window — h, key exposure time · 10 pairing-curve security level — curve · 11 trusted-setup — participants t, honest ≥ 1 · 12 side-channel window — rotation period · 13 rewrite detection latency — τ_a, public finality · 14 witness-update cost — churn rate, holders · 15 cache staleness σ — poll interval · 16 BFT collusion probability — N_v, f_B, independence p · 17 timeout vs propagation — Δ, gossip diameter · 18 long-range — key-leak probability × client sync age · 19 PoW reversal at depth z — α, z (Nakamoto §11) · 20 forced-inclusion delay — L2 parameter · 21 51% cost — hashpower price, T · 22 selfish-mining threshold — network position γ · 23 fee percentile vs W — cost distribution · 24 M-T2 capacity ceiling — block gas, class mix · 25 rotation race window — inclusion delay · 26 rotation window per option — A/B/C · 27 issuer-rotation propagation — = W · 28 W under A/B/C × SL/AC — the five terms · 29 status-list anonymity set / k — list size, revoked fraction · 30 recovery threshold vs collusion — t-of-m · 31 Tier budget vs read-path cost — tier, cache read latency.
**Five load-bearing decisions:** (1) the hybrid trades *prevention for detection* at L4 — say it in those words; (2) SOL-01 is credited with no closure; (3) W is not shortened by public checkpointing, only made provable; (4) AnonCreds' unlinkability is conditional on the status-check path (AC by construction, SL by herd size); (5) non-repudiation vs deniability is a per-message-class policy the programme has not yet chosen (BP-L7-06).
**Symbol collisions:** as R2 §4.3 — reuse W, σ; use f_B, N_v; avoid bare A, f, N; new symbols proposed for R4: κ (effective entropy), τ_a (anchoring interval), α (honest work fraction), z (depth), Δ (block interval), r (replication factor), γ (selfish-mining network share).
**Open Q-R#:** Q-R1–Q-R3 unchanged; Q-R4 — which message classes are deniable vs auditable (BP-L7-06)? Q-R5 — for PF-28, which manoeuvre-class W budgets from G-C1 §2.7 should R4 use as targets?
**Corrections:** KD-R none. Observation: Part II cites Eyal–Sirer 2014 (selfish mining) and CVE-2012-2459 (Merkle domain confusion) — both absent from the reference index; add at harvest.
