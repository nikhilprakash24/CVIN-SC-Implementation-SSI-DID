# F1 Analysis — On-Chain Storage Versus Not, and the Identity-Dependent Transaction (IDTx)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, focus F1, analysis). **Builds on:** `CAPTURE.md` (Phase 1 evidence, verified),
`docs/phase2/SCOPE_RECONCILIATION.md` §4. **Binds:** `docs/phase2/README.md` (principles), `docs/STYLE_AND_RIGOUR_GUIDE.md`.
**Numbers:** every number below is a register row (`docs/MEASUREMENT_CONDITIONS.md`) or a cell of the harness run of
record `7a9a996` named by its table; no Phase 2 measurement is reported (principle 4).

## 1. The question
Where should a connected vehicle's identity data live, and what does each choice buy, cost and forbid? Phase 1
answered the cost half for nine Ethereum standards. It did not ask the third half: **what a choice forbids**. A datum
that is not in contract state cannot be a condition of an on-chain action. The identity-dependent transaction
(IDTx) makes that half explicit. That is why F1 treats storage and IDTx together.

## 2. A taxonomy of storage loci
Six places an identity datum can live, ordered from most to least "on chain". Each row says who can read the datum,
whether a contract can act on it, and where Phase 1 has it.

| Locus | What it is | Readable by | Usable as an in-contract IDTx condition | Write cost driver | Read cost driver | Phase 1 instances |
|---|---|---|---|---|---|---|
| **L0 contract state** | the value in a storage slot | anyone; any contract | **yes** | new slots (zero→nonzero SSTORE) | one call, flat in history | ERC-1056 owner and delegates; ERC-735 claims; ERC-721 ownership; MOBI V2 events and roles |
| **L1 event log** | the value only in a log | anyone off chain; **no contract** | **no** | log bytes (cheap) | replaying history: grows with h | ERC-1056 attributes (`DIDAttributeChanged`) |
| **L2 calldata only** | the value only in transaction input | anyone off chain, by re-reading transactions | no | calldata bytes | transaction scan | none on purpose; every write's input |
| **L3 commitment in state** | a hash of a plaintext with a salt, or of a ciphertext | anyone, as an opaque value | **equality only** | one new slot per commitment | one call | MOBI `vinHash`; the IDTx prototype's `IdentityCommitments` |
| **L4 off chain, anchored** | the datum off chain; its issuer's key, status or digest on chain | the holder and verifiers it shows it to | through the anchor only (status, digest) | the anchor's write | verifier-side computation plus an anchor read | W3C credentials with an issuer DID; the revocation registry; the RSU credentials |
| **L5 off chain, unanchored** | a database or a certificate directory | its operator, and whoever it serves | no | none on chain | a service call | centralized registry baseline; the PKI baseline |

## 3. What Phase 1 measured about the loci
**Writing state is what costs gas.** Over the same 17-event lifecycle, the standards range from 8 new storage
slots (ERC-1056) to 149 (ERC-735), and lifetime gas from 1,050,809 to 5,797,549 (register #49, #35; figure F1-1).
ERC-1056 writes almost nothing to state because its attributes go to the event log (L1). An attribute update is one
storage write that creates no slot, plus 288 log bytes. In ERC-735 the same update is 13 storage writes, 12 of them
new slots, plus 1,024 log bytes (#49).

**Not writing state moves the cost to every read.** Resolving an ERC-1056 document at history h = 50 takes 112 RPC
calls and 87 KB, a median of 103.177 ms in-process, growing with history (#31; figure F1-2). A state-heavy design
reads in a flat number of calls (ERC-735: 3 calls at every h), but the bytes it returns grow too (180,558 B at h = 50
in the run of record's `scale.csv`; no register row yet). So the choice is not "cheap or expensive". It decides who
pays and when: the writer once, in gas, or every reader, in calls and bytes, for the life of the vehicle.

**Caching recovers most of the read cost, at a bounded staleness.** A verifier that re-checks every k-th message
pays the chain cost only every k-th time, and accepts at most k − 1 messages after a revocation (#32, #37, #46).
That bound is a message count, not a time (guide rule 1.1.9). It also assumes the verifier's clock agrees with the
chain's, which defect D51 showed it need not. The D51 fix now decides validity in chain time.

**An off-chain database is three to four orders of magnitude faster and offers no third-party verification.**
Against the in-process centralized registry, the on-chain lifecycle backend's writes are between about 1,600 and
6,000 times slower, and a cached on-chain history matches the database only when served from the cache (#33;
figure F2-1). The F2 analysis takes this comparison further.

## 4. The identity-dependent transaction (IDTx)
### 4.1 Definition
> An **identity-dependent transaction** is a state transition whose execution is conditioned on a predicate over
> identity state held by a ledger, evaluated at execution time. The predicate is evaluated either inside the
> transaction (in-contract), or by an agent that then submits the transaction, which must re-evaluate it before
> acting.

Three things make a transaction an IDTx and not an ordinary access check:
1. the condition is about an **identity** (a DID, a vehicle record, a credential's status), not about the caller alone;
2. the identity state is **held by a ledger** that the parties do not control unilaterally;
3. the condition is **evaluated at execution time**, so a change of identity state between decision and execution
   changes the outcome.

The scope reconciliation (§4) asks for one name. This document uses **IDTx** and retires IDDTx and IDBTx (decision
P2-D8, default as stated).

### 4.2 Position against known patterns (to be confirmed against sources in chapter 2)
IDTx is both a re-framing and an extension. The guard-on-execution mechanism is old; the contribution is the
definition, the taxonomy and one evaluation dimension Phase 1 already measures. The patterns an examiner will name,
each to be read at its source before the thesis cites it (the scope reconciliation flags these as recalled, not
checked):

| Pattern | What it shares with IDTx | What IDTx adds or makes explicit |
|---|---|---|
| Contract access control (`onlyOwner`, roles) | a guard before an action | the guard's subject is a *third-party identity's* state, not the caller's |
| Permissioned tokens with on-chain identity claims (ERC-3643 with ONCHAINID) | transfers conditioned on identity claims | storage locus of the condition (L0 vs L1 vs L3), its freshness, and the next-transaction continuation |
| Account abstraction validation (ERC-4337 `validateUserOp`) | execution conditioned on the account's own logic | a condition on identity state *outside* the account |
| Oracle-conditioned execution | an off-chain fact gates an on-chain action | the fact is ledger-held identity state, so it can be re-evaluated on chain instead of trusted |
| Attribute-based access control (policy engines) | a predicate over attributes | a ledger as the attribute store, with its cost and staleness profile |

### 4.3 The taxonomy: five axes
| Axis | Values | Phase 1 instance (CAPTURE.md §5) |
|---|---|---|
| **Dependency** (what is depended on) | existence or ownership; delegate or key validity; attribute or claim value; revocation status; history property (odometer monotone, event count) | ERC-1056 `identityOwner`, `validDelegate`; ERC-735 claim checks; MOBI V2 role checks; the odometer aggregator check |
| **Locus of the dependency** | L0 state; L3 commitment; L1 event (off-chain only); L4 anchored credential | owner and delegates L0; VIN hash L3; ERC-1056 attributes L1; RSU credentials L4 |
| **Encoding** | plaintext; salted hash; ciphertext digest; zero-knowledge proof | plaintext and salted hash only; no encrypted dependency anywhere in Phase 1 |
| **Evaluation** | in-contract, same transaction; off-chain agent then on-chain re-check; off-chain only (message acceptance) | in-contract for every contract gate; off-chain only for V2V and V2I verification |
| **Continuation** | same transaction; next transaction (intent then fulfilment); message acceptance; report | same transaction in every contract; message acceptance in the testbed; the prototype adds next transaction |

The axes are not independent, and that is the analysis:
- **L1 rules out in-contract evaluation.** ERC-1056 attributes can be a dependency only off chain (the prototype's
  test makes this mechanical: the registry exposes no view that returns an attribute). So the cheapest standard is
  cheap partly because no contract can depend on its attributes.
- **Encrypted dependencies are equality-only on chain.** A ciphertext's digest (L3) can gate an action by equality,
  never by content, unless a zero-knowledge proof is added (Phase 2 idea I-09).
- **Off-chain evaluation opens a time-of-check to time-of-use gap.** It is closed only if the transaction
  re-evaluates on chain. The prototype's `fulfil` does this. Phase 1's message verification cannot: it has no
  transaction. So it bounds the gap instead (k − 1 messages, #46; chain time, D51).

### 4.4 Threats specific to IDTx
| Threat | Mechanism | Phase 1 evidence | Mitigation |
|---|---|---|---|
| Stale dependency | the predicate was true when read, false at use | k − 1 bound (#32, #46); D51 clock skew (fixed); D63 residual on the probe path | re-evaluate in the transaction; bound staleness in time, not only in count |
| Time-of-check to time-of-use | an agent decides off chain, the state changes before its transaction | the prototype's TOCTOU tests (owner transfer, commitment revocation between intent and fulfilment) | on-chain re-check at fulfilment |
| Ordering and front-running | a dependent transaction and a state change race in the same block | not measured (local automine chain, F2) | commit-reveal; deadlines; block-number guards |
| Cross-chain replay of the dependency's authorisation | a signed identity update valid on another chain | D52 (ERC-1056 digest lacks the chain id) | chain-bound digests (idea I-08) |
| Weak authority behind the dependency | anyone can create the state the IDTx trusts | D54 (any role holder can attest any vehicle); D53 (owner-0) | restrict who can write the depended-on state (WM-2 C2) |
| Leakage through the dependency | the condition reveals the identity it checks | D64: a VIN-derived identity makes a VIN-hash dependency a VIN oracle | salted, non-derivable identifiers; commitments with private openings |

### 4.5 Cost model (the shape of it; no measured numbers yet)
For an in-contract IDTx, the cost is the action's own gas plus the reads of the dependency: one external call per
dependency to the registry (a cold storage read the first time in a transaction), plus the comparison. For a
next-transaction IDTx, add the intent's storage write (new slots) and a second transaction's base cost, paid by
whoever fulfils it (a Mode B-submit party in F3's terms). The F1 plan pre-registers these as predictions before the
prototype is measured.

## 5. Benefits, costs and what each choice forbids
| Choice | Buys | Costs | Forbids |
|---|---|---|---|
| Identity state on chain (L0) | anyone can verify it; any contract can depend on it (IDTx); no single operator can rewrite it | gas per new slot (#49); state that grows for the vehicle's life; permanence (no erasure) | privacy of the stored value; cheap correction of mistakes |
| Events only (L1) | cheap writes (#49); a public history | reads that grow with history (#31); a resolver that must be trusted or re-run | in-contract IDTx on that datum |
| Commitment on chain (L3) | public, verifiable binding without disclosure; equality IDTx | one slot per commitment; salt and key management off chain | computation on the hidden value (without ZK); linkability if the identifier itself is derived (D64) |
| Off chain, anchored (L4) | privacy; fast in-process verification (#27) | anchor maintenance; freshness management (#32) | contract-side dependency on the content |
| Off chain, unanchored (L5) | speed (#33); flexible queries; erasure | trust in the operator; no third-party audit (F2) | any IDTx |

## 6. What this means for the thesis and beyond
- **Thesis (concept only, existing evidence).** The storage-locus table (§2), the measured trade-off (§3,
  #49 #35 #31), the IDTx definition and taxonomy (§4.1, §4.3) and the threat table (§4.4) fit a discussion section
  of chapter 6 without a new experiment. This placement is the academic adviser's recommendation (scope
  reconciliation §4).
- **Paper after the thesis.** A measured IDTx study, the pre-registered experiments of `PLAN.md`.
- **For others.** The prototype (`phase2/idtx/`), its tests and the plan let someone else run the study if the
  author does not.
