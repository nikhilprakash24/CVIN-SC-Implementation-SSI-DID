# F1 Analysis: On-Chain Storage Versus Not, and the Identity-Dependent Transaction (IDTx)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, focus F1, analysis). **Revised:** 2026-10-14 after the academic review
(`docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md`), findings AR-1, AR-2, AR-3, AR-7, AR-8, AR-9, AR-10, AR-15, AR-16,
AR-17, AR-19, AR-41. **Builds on:** `CAPTURE.md` (Phase 1 evidence, verified); `docs/phase2/SCOPE_RECONCILIATION.md`
§3.1. **Binds:** `docs/phase2/README.md` (principles), `docs/STYLE_AND_RIGOUR_GUIDE.md`.
**Numbers:** every number below is a register row (`docs/MEASUREMENT_CONDITIONS.md`) or a cell of the harness run of
record `7a9a996` named by its table; no Phase 2 measurement is reported (principle 4).

**Terms used below.**

| Term | Meaning |
|---|---|
| register row (#n) | a row of the claim register, `docs/MEASUREMENT_CONDITIONS.md` |
| SSTORE | the EVM opcode that writes a contract storage slot; a zero→nonzero SSTORE is the expensive case |
| event log | data a contract emits into a transaction's receipt. Nodes keep it and anyone off chain can read it. A contract cannot read it directly |
| h | the length of an identity's history, in lifecycle events |
| k | the re-check interval of a caching verifier: it asks the chain on every k-th message |
| TOCTOU | time-of-check to time-of-use: the gap between reading a condition and acting on it |

## 1. The question
A storage choice decides two things: what a datum costs to keep and read, and what a contract can depend on. Phase 1
measured the first for nine Ethereum standards. F1 adds the second, and the identity-dependent transaction (IDTx) is
the concept that makes it precise. A datum that a contract cannot read directly can still condition an on-chain
action, but only through a proof the transaction carries, at a cost Phase 1 did not measure (AR-1).

## 2. A taxonomy of storage loci
An identity datum can live in six places, ordered from most to least "on chain". The table says who can read the
datum, how a contract can depend on it, and where Phase 1 has it. Placement of data on or off chain is an established
architectural design decision; this table specialises it to vehicle identity and is to be positioned against that
literature in chapter 2 (review §3.1: Xu et al.; Eberhardt and Tai).

| Locus | What it is | Readable by | How a contract can depend on it | Write cost driver | Read cost driver | Phase 1 instances |
|---|---|---|---|---|---|---|
| **L0 contract state** | the value in a storage slot | anyone; any contract | directly | zero→nonzero SSTOREs | one call, flat in history | ERC-1056 owner and delegates; ERC-735 claims; ERC-721 ownership; MOBI V2 stored event structs and roles |
| **L1 event log** | the value only in a log | anyone off chain | not directly; only through a receipt proof the transaction carries, against a block hash the contract can reach (not measured; review §3.1, EIP-1186 and EIP-2935, to check) | log bytes | replaying history: grows with h | ERC-1056 attributes (`DIDAttributeChanged`) |
| **L2 calldata only** | the value only in transaction input | anyone off chain, by re-reading transactions | only within the transaction that carries it | calldata bytes | transaction scan | none on purpose; every write's input |
| **L3 commitment in state** | a hash of a plaintext with a salt, or of a ciphertext | anyone, as an opaque value | equality with a registered value (registered-commitment validity, AR-5) | one new slot per commitment | one call | MOBI `vinHash`; the IDTx prototype's `IdentityCommitments` |
| **L4 off chain, anchored** | the datum off chain; its issuer's key, status or digest on chain | the holder and the verifiers it shows it to | when the content and its issuer signature are carried in the transaction; the anchor then supplies issuer status (AR-8) | the anchor's write | verifier-side computation plus an anchor read | W3C credentials with an issuer DID; the revocation registry; the RSU credentials; `attestEvent` and `addClaim` verify carried signatures in the transaction |
| **L5 off chain, unanchored** | a database or a certificate directory | its operator, and whoever it serves | not at all | none on chain | a service call | the centralized registry baseline; the PKI baseline |

## 3. What Phase 1 measured about the loci
**Writing state is the part of gas that storage choice controls.**
- Over the same 17-event lifecycle, zero→nonzero SSTOREs range from 8 (ERC-1056) to 149 (ERC-735), and lifetime gas
  from 1,050,809 to 5,797,549 (register #49, #35).
- The association is not a cause on its own. ERC-735's and ERC-725xy's creation cost is mostly contract code
  deployed per identity (C1 1,757,893 and 1,730,753 with 3 and 2 SSTOREs; CAPTURE §2.2).
- In ERC-1056 an attribute update is one storage write that creates no slot, plus 288 log bytes. In ERC-735 it is
  13 storage writes, 12 of them new slots, plus 1,024 log bytes (#49).

**Not writing state moves the cost to every read.**
- Resolving an ERC-1056 document at h = 50 takes 112 RPC calls and 87 KB, a median of 103.177 ms in-process,
  growing with history (#31).
- A state-storing standard reads in a flat number of calls, but the bytes it returns can still grow:
  - ERC-735: 3 calls and 180,558 B at h = 50;
  - ERC-725xy: 2 calls and 17,992 B (#51).
- So the choice is not "cheap or expensive". It decides who pays and when: the writer once, in gas, or every reader,
  in calls and bytes, for the life of the vehicle.

**Caching recovers read cost at a bounded staleness.**
- A verifier that re-checks every k-th message pays the chain cost only every k-th time. It accepts at most k − 1
  messages after a revocation (#32, #37 for the ERC-1056 verifier; #46 for the RSU path).
- That bound is a message count, not a time (guide rule 1.1.9).
- Rows #32 and #37 also assume the verifier's clock is within 900 s of chain time (D51). The D51 fix (WM-2 C0) now
  decides validity in chain time. #32 and #37 predate it and are due for re-run (A3b). #46 is unrelated to D51 (AR-9).

**A database is faster, and Phase 1 reports where the cache failed to match it.**
- Against the in-process centralized registry, on-chain lifecycle writes were between about 1,600 and 6,000 times
  slower in the 2026-10-04 re-run (≈1,850 to 5,930 in the first run; #33, D60).
- The pre-registered "equal once cached" test **failed**. The cached history query took 0.011 ms against the
  database's 0.2627 ms, a ratio of 0.041 outside the [0.5, 2] band.
- The explanation that the database's serialisation dominates is **post hoc**.
- Keeping the cache fresh costs a probe: 15.403 ms and 6 RPC calls per validated read (#33,
  `cv2x-testbed/results/lifecycle_parity.md`) (AR-19).

## 4. The identity-dependent transaction (IDTx)
### 4.1 Definition (the academic review's §3.3, adopted as the default of decision P2-D8)
> An **identity-dependent transaction (IDTx)** is a transaction whose admissibility or effect is a function of the
> state of an identity that the transaction names. That state is evaluated during execution, either from ledger
> state or from an attestation or proof that the transaction carries and verifies. Two cases are excluded:
> authentication of the transaction's own sender, and a check whose only subject is the identity record that the
> transaction itself modifies (identity administration).
>
> An off-chain decision that depends on identity state, such as a verifier accepting a message, is an
> **identity-dependent decision**. It shares the freshness dimension but is not a transaction.

This is the one definition. Every other wording in the Phase 2 documents, including CAPTURE.md §5's working
definition, is superseded by it (AR-2). The name is IDTx; IDDTx and IDBTx are retired (P2-D8).

### 4.2 The Phase 1 inventory, re-classified (AR-3)
Under §4.1 the 25 instances of CAPTURE.md §5, plus `payToll` (`CVIN_NFT_DID_ERC721.sol:71`), which the capture
missed, fall into six classes. Only four are IDTx.

| Class | Instances | Count | Why |
|---|---|---:|---|
| **IDTx (cross-dependent)** | T5 MOBI birth (VIN uniqueness against other identities); T10 ERC-735 `addClaim` (the issuer's authorisation and claim status); T11 CVIN-Combined `addClaim` (issuer and sticky revocation); **`payToll`** (a payment whose admissibility depends on the named vehicle's owner) | 4 | the admissibility depends on an identity other than the record modified, or the effect lies outside the identity record |
| **Identity administration or sender authorisation** (excluded) | T1, T4, T6, T7, T8, T9, T13, T14, T15, T16 | 10 | the check's subject is the record being modified, or the sender's own role |
| **Admission-time authentication** (excluded) | T2 ERC-1056 signed writes; T12 ERC-4337 `validateUserOp`; T17, T18 clients reading their own nonce | 4 | authentication of the sender, at admission |
| **Enabling view** (no transaction) | T3 ERC-1056 `validDelegate` | 1 | state any contract could depend on; no gate by itself |
| **Identity-dependent decision** (off chain) | T19 V2V verify; T20 freshness-k cache; T22 RSU verify; T23 history aggregator; T24 history cache with probe | 5 | a verifier's or reporter's decision, not a transaction |
| **Not a dependency** | T21 freshness window and replay cache; T25 linkability analysis | 2 | no identity state is depended on |

In Phase 1, then, true IDTx are few. The mechanism is mostly used for administration and authentication, and the
interesting dependencies sit off chain, as decisions. That count is itself a finding for the thesis.

> **Correction (2026-10-24, examiner obj. 3 — see `docs/idtx_core/p1/EXAMINER_REVIEW.md`).** The headcount "four" is
> boundary-sensitive and two of the four (`payToll`, the MOBI birth) lie *outside* the ten measured substrates. The
> thesis (Ch 6 §6.8.2) no longer presents a precise count as a result: over the measured ten the count is **2** (the
> two `addClaim` paths), with `payToll`/MOBI as out-of-set exemplars, and the robust claim is the weaker qualitative
> one (administration/authentication dominate; the richest dependencies are off-chain). This note supersedes "that
> count is itself a finding" for thesis purposes.

### 4.3 Position against known patterns (to be confirmed at source in chapter 2)
The guard-on-execution mechanism is not new, and the thesis says so first. The contribution is three things:
- the definition, which separates dependence on another identity's lifecycle state from administration and
  authentication;
- a taxonomy keyed to storage locus;
- the freshness dimension, which Phase 1 measured for decisions.

The review's §3.1 is the reading list, every entry marked recalled until read. Its §3.2 is a related-work paragraph to
adapt.

| Pattern | What it shares with IDTx | What IDTx distinguishes |
|---|---|---|
| Contract access control (owner and role modifiers; ABAC, NIST SP 800-162) | a guard on attributes | the dependency is on an identity the transaction *names*, not on the caller |
| Permissioned tokens over an identity registry (ERC-3643 with ONCHAINID), the closest prior art | a transfer gated on claims from trusted issuers | position explicitly; claim the taxonomy, the vehicle domain and freshness, not the mechanism |
| Account-abstraction validation (ERC-4337) | admission decided by programmable validation | the admission-time class above; excluded as sender authentication |
| Oracle-conditioned execution | an off-chain fact gates execution | one locus (L4, carried attestation), not the concept |
| Transaction-order dependence and front-running | a race between a state change and a dependent transaction | the ordering race the on-chain re-check leaves open (§4.5) |

### 4.4 The taxonomy: three axes (AR-7)
Each axis classifies a different property, and every IDTx falls in exactly one cell:
1. **Dependency kind:** ownership; delegate or key validity; attribute or claim value; revocation status; history
   property.
2. **Locus with encoding:**
   - L0 plaintext state;
   - L3 registered commitment (salted hash or ciphertext digest);
   - L4 carried attestation with an anchored issuer;
   - L1 carried receipt proof (unmeasured).
3. **Evaluation point:** in the transaction; at admission; off chain then re-checked in a later transaction.

Continuation (same or next transaction) and initiation (owner, keeper, third party) are attributes, not axes.

| IDTx | Dependency kind | Locus with encoding | Evaluation point |
|---|---|---|---|
| T5 MOBI birth | attribute (VIN uniqueness) | L3 salted hash | in the transaction |
| T10 ERC-735 `addClaim` | claim value and issuer status | L4 carried attestation, L0 issuer authorisation | in the transaction |
| T11 CVIN-Combined `addClaim` | claim value and issuer status | L4 carried attestation, L0 sticky revocation | in the transaction |
| `payToll` | ownership | L0 plaintext | in the transaction |
| prototype `execute` | ownership, delegate, or registered commitment | L0 or L3 | in the transaction |
| prototype `createIntent` and `fulfil` | the same | the same | off chain then re-checked in a later transaction |

Three constraints connect the axes:
- **L1 rules out direct evaluation.** An ERC-1056 attribute can be depended on in a transaction only through a carried
  receipt proof, which Phase 1 never built. The prototype's test 12 shows only that the registry exposes no view that
  returns an attribute. The cheapest standard is cheap partly because a contract cannot depend on its attributes
  without that extra proof.
- **A commitment is equality-only.** A registered commitment (L3) gates an action by equality with a public value.
  It proves no knowledge of what it commits to (AR-5); a knowledge dependency would need the opening disclosed or a
  zero-knowledge proof (idea I-09).
- **A later re-check leaves an ordering race (AR-10).** A transaction that re-evaluates on chain, as `fulfil` does,
  closes the gap inside execution. It does not close the ordering race between the dependency's change and the
  dependent transaction (§4.5). Phase 1's message verification has no transaction at all, so it bounds staleness
  instead: k − 1 messages (#32, #37), now in chain time (D51 fix).

### 4.5 Threats specific to IDTx

| Threat | Mechanism | Phase 1 evidence | Mitigation |
|---|---|---|---|
| Stale dependency (decisions) | the predicate was true when read, false at use | k − 1 bound (#32, #37); D51 (fixed in code; rows await A3b); D63 residual on the probe path | bound staleness in time, not only in count |
| TOCTOU (transactions) | an agent decides off chain, the state changes before its transaction | the prototype's tests 9 and 10 (owner transfer, commitment revocation between intent and fulfilment) | re-evaluate at execution |
| Ordering race | a dependent transaction and the dependency's change race for block order | not measured (single automine node, F2) | deadlines; commit-reveal; the ordering literature (review §3.1) |
| Stale authority | a commitment outlives its setter's ownership | the prototype's AR-6 test | bind commitments to the setter's continued ownership (done in the prototype) |
| Cross-chain replay | a signed identity update valid on another chain | D52 | chain-bound digests (idea I-08) |
| Weak authority behind the dependency | anyone can create the state the IDTx trusts | D54; D53 | restrict who writes the depended-on state (WM-2 C2) |
| Leakage through the dependency | the condition reveals the identity it checks | D64: a VIN-derived identity makes a VIN-hash dependency a VIN oracle | non-derived identifiers with a uniqueness mechanism designed first (AR-13) |

### 4.6 Cost model (its shape only; no measured numbers yet)
An in-contract IDTx costs the action's own gas plus the dependency's reads. For the prototype's kinds that is one
cold account access to the registry and one or two cold storage reads, plus the comparison. A next-transaction IDTx
adds the intent's storage write and a second transaction, paid by whoever fulfils it. The F1 plan states point
predictions with bands for each kind before anything is measured.

## 5. Benefits, costs and what each choice forbids

| Choice | Buys | Costs | Forbids |
|---|---|---|---|
| Identity state on chain (L0) | anyone can verify it; any contract can depend on it directly; no single operator can rewrite it (a design argument; M1 has one operator) | zero→nonzero SSTOREs (#49); state that grows for the vehicle's life; permanence (no erasure) | privacy of the stored value; cheap correction of mistakes |
| Events only (L1) | cheap writes (#49); a public history | reads that grow with history (#31); a resolver that must be trusted or re-run | direct contract dependency (a carried receipt proof is the only route) |
| Commitment on chain (L3) | public binding without disclosure; equality dependencies | one slot per commitment; salt and key management off chain | knowledge or computation on the hidden value without ZK; privacy if the identifier itself is derived (D64) |
| Off chain, anchored (L4) | privacy; fast in-process verification (#27) | anchor maintenance; freshness management (#32) | dependency on content not carried in the transaction |
| Off chain, unanchored (L5) | speed (#33); flexible queries; erasure | trust in the operator; no third-party audit | any IDTx |

## 6. What this means for the thesis and beyond (the review's §4.1)
| Item | Placement |
|---|---|
| storage-locus table (§2), with locus and encoding merged as in §4.4 | thesis, chapter 6, one section with the IDTx |
| IDTx definition (§4.1), three-axis taxonomy (§4.4), re-classified inventory (§4.2) | the same section, labelled conceptual; no number attached |
| threat table (§4.5), rows with defect evidence | chapter 6 |
| cost model, the F1 plan's experiments, the prototype | **cut** from the thesis: one future-work paragraph; the prototype cited as an artefact |
| a measured IDTx study | paper P5 after the thesis (review §4.2) |
