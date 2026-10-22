# Chapter 6, Draft Section 6.8: The Identity-Dependent Transaction, What It Is and What It Is Not

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-20 (after-action report 26), **draft 1**. Answers
examiner question 12 of the scope reconciliation ("How does an identity-dependent transaction differ from access
control or from ERC-3643?", `docs/phase2/SCOPE_RECONCILIATION.md` §4) under scope decision D-7's default (definition,
taxonomy, mapping and classification from existing evidence; no pre-defence experiment). D-7 and D-15 are not yet
adopted (`docs/DECISION_SHEET_2026-10-20.md`).
**Citations** use the keys of the chapter 2 draft (`../chapter2-literature-review/DRAFT_SECTIONS_2026-10-20.md` §B),
every one a source fetched at origin. **Numbers** carry their register row, status V only.

---

## 6.8 The identity-dependent transaction, what it is and what it is not

### 6.8.1 Why a name was needed
Across the nine standards and the testbed, the same shape recurred without a name: a transaction whose admissibility
or effect depends on the state of an identity it names, a vehicle, an issuer, a road-side unit, where that state has
a lifecycle of its own and can change between the moment it is read and the moment the transaction takes effect.
Chapter 2 (§2.6) gives the definition this thesis adopted and positions it against prior work. This section says what
the definition does to the thesis's own evidence, and where its claim stops.

### 6.8.2 What it is not: three nearby things
**It is not access control.** A contract's `onlyOwner` or role modifier gates on the caller [A-T01]; the definition
excludes sender authentication. Attribute-based access control already evaluates attributes of the object as well as
the subject [A-S05], so "the predicate is about the identity the transaction names" is not, by itself, a new idea. The
IDTx differs from ABAC in what a ledger adds to the predicate: where the identity's state is held and how it is
encoded (the storage locus), when the predicate is evaluated relative to inclusion in a block, and how stale the
state may be when it is used. None of those is a dimension of ABAC's policy model; each is priced or bounded in this
thesis.

**It is not new as a mechanism.** ERC-3643 transfers execute only if the *receiver* holds the required claims from
trusted issuers, checked inside `transfer`, `transferFrom`, `mint` and `forcedTransfer` [A-S09]. Under the
definition a T-REX transfer is an IDTx, and the standard is at Final status. The guarded transaction of Luu et al.,
a transaction that carries a guard on current state and is dropped if the guard fails, is the same mechanism in
general form [A-S01]. The thesis does not claim the mechanism. What ERC-3643 does not do is frame the check by
locus, evaluation point or freshness, or measure it against alternatives on one lifecycle.

**It is not the testbed's message verification.** A verifier accepting or rejecting a V2V message depends on the
sender's identity state in the same way, but no transaction is involved. The definition calls that an
identity-dependent decision. It shares the freshness dimension (§6.8.5) and nothing else, and most of what Phase 1
measured about freshness is about decisions, not transactions (#32, #37, #46).

### 6.8.3 How many there are in this thesis
Applying the definition to every gate in the Phase 1 code gave a smaller count than the first draft of the Phase 2
analysis had claimed: of 26 gates inventoried, **4** are identity-dependent transactions, 14 are identity
administration or sender authentication, 1 is an enabling view, 5 are off-chain decisions and 2 depend on no identity
state at all (`docs/phase2/focus/F1_onchain_storage_idtx/ANALYSIS.md` §4.2, corrected under the academic review,
`docs/phase2/reviews/DISPOSITIONS_F1-F3.md` AR-3). The four: the MOBI birth registration, whose admissibility depends
on VIN uniqueness against every other registered identity; the ERC-735 and CVIN-Combined `addClaim`, whose
admissibility depends on the issuer's authorisation and revocation status; and the ERC-721 profile's `payToll`, a
payment whose admissibility depends on the named vehicle's current owner.

A fifth was added by this thesis's own hardening, after that count was made. Since the D54 fix, a MOBI attestation
is admissible only if the attester is the named vehicle's current owner or holds its owner's unexpired `veriKey`
delegation, checked on chain (`docs/DEFECT_LOG.md` D54; after-action report 22). That check is an IDTx of the
ownership-and-delegate kind at locus L0, and it cost 29,333 gas of execution per attestation to add (#28: execution gas 169,361 → 198,694). It is the clearest instance in the thesis of the trade the taxonomy is about: a consent dependency on a
named identity, paid for in storage reads and one storage write.

That true IDTx are few is itself a finding. The mechanism that gives a ledger-held identity its value is used, in
this code base and in the standards it implements, mostly for administration and authentication. The dependencies
that matter for a vehicle, whether a sender is still trusted at the moment its message arrives, sit off chain as
decisions, where the cost of reading the ledger is paid per check and bounded by a cache.

### 6.8.4 What the taxonomy's axes cost, from the thesis's own measurements
The taxonomy has three axes (dependency kind; storage locus with encoding; evaluation point). The thesis measured the
locus axis across the nine standards without having named it:

- **Plaintext state (L0)** is contract-readable and costs storage. ERC-735, which keeps claims in structs, pays 149
  new storage slots over the 17-event lifecycle where the event-log ERC-1056 pays 8 (#49), and is the most expensive
  of the nine to live with (#35), while its document reads back in a constant 3 RPC calls at any history depth
  (#51). Struct-keeping standards buy contract-readable state and constant-call reads with storage.
- **Event logs (L1)** are the cheapest to write and cannot be depended on by a contract at all: ERC-1056's own
  standard keeps attributes in events "exclusively for off-chain use" [A-S06], and reading them back grows linearly
  in history, 112 RPC calls and 87 KB at depth 50 (#31, #51). A contract that needs an L1 fact needs a carried proof,
  which `eth_getProof` gives for storage but not for logs [A-S10].
- **A registered commitment (L3)**, the salted VIN hash, gates by equality only; it proves nothing about what it
  commits to, and the testbed's unsalted variant of it is defect D64, to be fixed after the defence with a uniqueness
  mechanism designed first (dispositions AR-13).
- **A carried attestation (L4)** moves the dependency's trust to the issuer, which is the oracle problem with the
  issuer as oracle [A-S12]; the ERC-735 and CVIN-Combined claims live here.

On the evaluation-point axis, the thesis priced admission-time evaluation once: an ERC-4337 operation through the
EntryPoint costs +46,830 gas over the direct call (#25), and the standard's own validation-scope rules restrict what a
validation may read of another identity's state [A-S07, A-S08].

### 6.8.5 Freshness, the axis the ledger makes unavoidable
A dependency on identity state is a dependency on a moving target. Between the read and the use, the identity's owner
can change or its key can be revoked, and whoever orders the block decides which happens first: the
transaction-ordering dependence of Luu et al. [A-S01], seen in the wild as front-running [A-S02, A-S03], and in
software as the time-of-check-to-time-of-use flaw [A-S04]. The thesis measured the off-chain half of this window in
message units: a verifier that re-reads every k messages accepts at most k − 1 from a revoked sender, which held in
280 of 280 trials (#37) and in every pre-registered run of the infrastructure experiment (#46); and it showed that the
absolute cost of a re-read, and so the k at which the latency budget is met, is a property of the host, by re-running
two configurations on one machine (#52). The on-chain half, the exposure window of a transaction that depends on
identity state, this thesis does not measure; it is Phase 2 experiment E-F1-3.

### 6.8.6 What the thesis claims, stated narrowly
1. One definition, which separates a dependency on a named identity from sender authentication and identity
   administration, and names the off-chain counterpart. No fetched source names or defines the concept; the search was
   open-web only and is a negative result, not proof of absence (`docs/phase2/briefs/I-24_IDTX.md` §3.4).
2. A classification of this thesis's own gates under it, with the count above.
3. The measured cost of each storage locus on one lifecycle across nine standards (#49, #51, #31, #35), and of one
   admission-time path (#25), gathered under the taxonomy's axes for the first time in this work.
4. The freshness bound for the off-chain case, as it fell (#37, #46, #52).

The thesis does not claim the guard mechanism, a general theory of IDTx cost, or any on-chain exposure measurement.
Whether the taxonomy earns a paper depends on E-F1-2 and E-F1-3, after the defence (scope decision D-7).
