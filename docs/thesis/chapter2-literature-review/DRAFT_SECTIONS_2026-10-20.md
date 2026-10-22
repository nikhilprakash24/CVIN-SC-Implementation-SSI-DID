# Chapter 2, Draft Sections: Revocation Freshness (2.4a) and the Identity-Dependent Transaction (2.6)

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-20 (after-action report 26), **draft 1**, under
scope decision D-15's default (write chapter 2 next, with IDTx positioned inside it). D-15 is not yet adopted by the
author (`docs/DECISION_SHEET_2026-10-20.md` §A); this draft is written so that the decision can be taken on a text
rather than on a plan.
**Citations.** Every source below was fetched at its origin and quoted in `docs/phase2/briefs/I-24_sources.json`
(keys A-*) or `docs/phase2/briefs/I-05_sources.json` (keys F-*); the citation key maps to the brief's id in §B.
No other source is cited. The chapter's remaining sections (2.1 to 2.3, 2.5) still wait on the author's reference
set, as `README.md` says.
**Numbers.** Every number carries its register row (`docs/MEASUREMENT_CONDITIONS.md`), status V only.

---

## 2.4a Revocation freshness: the cost of knowing

A verifier that accepts a message must decide whether the sender's credential is still good. Every revocation scheme
answers the same question in a different place on one trade: how much the verifier pays per check against how long a
revoked credential keeps working.

**The PKI debate.** Rivest asked whether certificate revocation lists could be eliminated in favour of other
mechanisms and answered that in most cases they could [F-S01]. McDaniel and Rubin replied that the right mechanism
depends on the environment, and proposed revocation on demand, a CRL-based scheme that still gives timely
information [F-S02]. OCSP settled the online side of the argument: a status response carries `thisUpdate` and
`nextUpdate`, and the relying party judges them against its own clock [F-S03]. That judgement in the verifier's time
is the same question the testbed met as defect D51, where a verifier's clock, not the chain's, decided whether a key
was still valid (`docs/DEFECT_LOG.md`). Measurement of the web's PKI found both that revocation is common (8 % of
served certificates in one scan set) and that fetching status is often expensive enough that clients skip it
[F-S05]. CRLite's answer was to change the direction of the traffic: push a compact aggregate of all revocations to
every client on a period, so the per-check cost is local and the staleness is a time bound set by the update period
[F-S04].

**Vehicular revocation.** The V2X security credential management system enforces revocation by periodically
distributing a CRL that devices use to reject messages from revoked senders [F-S06]; an earlier vehicular scheme
showed such lists reaching a region within minutes over road-side units at a few kilobits per second [F-S07]. Both
are push schemes with a time bound. The testbed's verifier is a pull scheme with a message bound: it re-reads the
sender's state every k messages, so a revoked sender is accepted for at most k − 1 further messages (#46, #32). The
guide's rule 1.1.9 that a message bound is not a time bound is the difference between these two families, stated
once.

**The credential layer's own parameter.** The W3C status method for verifiable credentials expresses freshness as a
time to live in milliseconds, optional and without a default, and tells verifiers to cache the status list [F-S08,
F-S09]. A W3C verifier therefore has a time bound available in the credential itself; whether to honour it is a
verifier policy, which is exactly what this thesis measures.

**Caches and polled copies as the formal setting.** HTTP caching gives the vocabulary: a response is fresh while its
age has not exceeded its freshness lifetime [F-S11]. The hit rate of a TTL cache has a closed form when request
inter-arrivals are independent [F-S10], and the freshness of a polled copy of a source that changes as a Poisson
process decays as e^(−λt) between polls [F-S12]. The verifier is the copy and the chain is the source; the chain-read
cost per poll is the testbed's t_chain and the budget is the V2V latency budget.

**Age of information.** The vehicular networking literature introduced age of information for status messages and
showed the optimum lies between maximum throughput and minimum delay [F-S13]; the survey frames timeliness at a
monitor under a resource budget [F-S14]; and the age of incorrect information refines it to penalise only the time
the monitor's copy is wrong [F-S15]. Revocation exposure has that last shape: a cached identity state is harmless
until a revocation makes it wrong. The Phase 2 brief on freshness theory derives, in that frame, the cache setting
that is freshest within a capacity budget and an exposure cap, k_min = ceil(t_chain / (B − t_local)), and shows why
the measured knee moves between hosts: its sensitivity to t_local is t_local / (B − t_local)
(`docs/phase2/briefs/I-05_FRESHNESS.md` §7). That derivation is a prediction, not a result; the measurement that
tests it is a Phase 2 item.

**What this thesis adds.** The prior work states the trade in time and measures it for web and V2X PKI. This thesis
measures it for a chain-read verifier in message units on one testbed (#32, #37), reports the k − 1 bound as it fell
in 280 of 280 trials (#37), and shows with a same-host re-run that the absolute knee is a property of the host, not
of the policy (#52).

## 2.6 The identity-dependent transaction, positioned

**Definition.** This thesis uses one definition, adopted from the academic review of its Phase 2 packages
(`docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md` §3.3): an identity-dependent transaction (IDTx) is a transaction whose
admissibility or effect is a function of the state of an identity that the transaction names, evaluated during
execution from ledger state or from an attestation the transaction carries and verifies; authentication of the
sender and administration of the identity record itself are excluded. An off-chain decision with the same dependency,
such as a verifier accepting a message, is an identity-dependent decision, which shares the freshness dimension but is
not a transaction.

**The mechanism is prior art, and the thesis says so.** A transaction that re-checks a condition on current state
before it takes effect is the guarded transaction of Luu et al., who proposed that a transaction carry a guard g and
be dropped if the current state does not satisfy it [A-S01]. A transfer that executes only if the *receiver* holds
the required identity claims from trusted issuers is standardised in ERC-3643, whose `isVerified` runs inside
`transfer`, `transferFrom`, `mint` and `forcedTransfer` [A-S09]. Under the definition above, a T-REX transfer is an
IDTx: its admissibility depends on a named identity other than the sender. The thesis therefore does not claim the
mechanism. It claims a taxonomy and a measurement.

**What access control already covers.** Attribute-based access control evaluates attributes of the subject, the
object, the operation and the environment against policy [A-S05]. "The predicate is about the named identity, not the
caller" is ABAC with the named identity as object; it does not distinguish an IDTx from ABAC. The distinction rests on
the ledger-specific axes: where the identity state is held (storage locus), how it is encoded, when it is evaluated,
and how fresh it is. Role modifiers in contract libraries gate on the caller [A-T01] and are the excluded case.

**Why the storage locus is an axis.** The standards constrain each cell separately. ERC-1056 keeps attributes in
events, which the standard itself says are stored "exclusively for off-chain use", and exposes `validDelegate` as a
view [A-S06]: an attribute is not a contract-readable dependency, a delegation is. This thesis measured the
consequence across nine standards: what each stores, what each emits, and what a resolver must do to read it back
(#49, #51), and what the cheapest standard's history costs a reader at depth 50 (#31). `eth_getProof` gives storage a
proof form for off-chain verification but covers storage, not logs [A-S10]; a historical block-hash service bounds how
old a block can be for a contract to check a carried proof against it [A-S11]. The oracle literature frames the
carried-attestation locus: a contract sees only data already on chain or fed into it, and an oracle mediates the rest
[A-S12]. Zero-knowledge credential on-chaining gives the committed locus a published design for a hidden attribute
[A-S13]; a vehicle-domain system that has a contract verify issuer and holder signatures against another ledger is the
closest prior deployment, framed by neither locus nor freshness [A-S14].

**Why the evaluation point is an axis.** Account abstraction evaluates a user operation's validity against mutable
state, and its standard introduces simulation because another operation can change that state before inclusion
[A-S07]; its validation-scope rules limit what storage a validation may read, so that an account's validation cannot
read a registry slot keyed by another identity while a staked paymaster can [A-S08]. Admission-time evaluation of a
named identity's state is therefore constrained by a standard, not only by cost, and the thesis prices the EntryPoint
indirection it implies (+46,830 gas per operation, #25).

**Why freshness is an axis, and the race.** The dependency between an identity change and a transaction that
depends on it is a transaction-ordering dependence: the final state depends on the order the block builder chooses
[A-S01], a class measured in the wild as front-running [A-S02] and catalogued with its mitigations [A-S03]. In
software terms it is a time-of-check-to-time-of-use flaw: a check, then an action that assumes the check still holds
[A-S04]. Phase 1 holds the off-chain half of this race in message units (#32, #37, #46) and the credential layer's
time-to-live in time units [A-S15]; the on-chain half, the exposure window of an identity dependency, is not measured
by any fetched source and is the Phase 2 experiment E-F1-3 (`docs/phase2/focus/F1_onchain_storage_idtx/PLAN.md`).

**What is new, stated narrowly.** No fetched source names "identity-dependent transaction" or defines it; the
search was open-web only, so this is a negative result, not proof of absence (`docs/phase2/briefs/I-24_IDTX.md`
§3.4). What the thesis adds is: one definition that separates the dependency on a named identity from sender
authentication and identity administration; a four-axis taxonomy (locus, encoding, evaluation point, continuation)
into which the nine standards and the testbed's gates are classified from existing evidence (4 of 26 Phase 1 gates
qualify, `docs/phase2/reviews/DISPOSITIONS_F1-F3.md`); and the measured cost of each storage locus on one testbed. The
claim stops there. Whether the taxonomy earns a paper depends on E-F1-2 and E-F1-3, after the defence (scope decision
D-7).

---

## B. Citation keys
| Key | Brief id | Short form |
|---|---|---|
| A-S01 | I-24 S01 | Luu et al., Making Smart Contracts Smarter, CCS 2016 |
| A-S02 | I-24 S02 | Daian et al., Flash Boys 2.0, arXiv:1904.05234, 2019 |
| A-S03 | I-24 S03 | Eskandari, Moosavi, Clark, SoK: Transparent Dishonesty, FC 2019 |
| A-S04 | I-24 S04 | Bishop and Dilger, Checking for Race Conditions in File Accesses, Computing Systems 1996 |
| A-S05 | I-24 S05 | Hu et al., NIST SP 800-162, 2014 (updated 2019) |
| A-S06 | I-24 S06 | ERC-1056, Ethereum Lightweight Identity |
| A-S07 | I-24 S07 | ERC-4337, Account Abstraction Using Alt Mempool |
| A-S08 | I-24 S08 | ERC-7562, Account Abstraction Validation Scope Rules |
| A-S09 | I-24 S09 | ERC-3643, T-REX |
| A-S10 | I-24 S10 | EIP-1186, eth_getProof |
| A-S11 | I-24 S11 | EIP-2935, Serve historical block hashes from state |
| A-S12 | I-24 S12 | Eskandari et al., SoK: Oracles, ACM AFT 2021 |
| A-S13 | I-24 S13 | Heiss et al., Non-Disclosing Credential On-chaining, arXiv:2209.09584, 2022 |
| A-S14 | I-24 S14 | Naghmouchi, Kaffel, Laurent, arXiv:2201.00231, 2022 |
| A-S15 | I-24 S15 | W3C Bitstring Status List v1.0, 2025 |
| A-T01 | I-24 T01 | OpenZeppelin Contracts 5.x, Access Control |
| F-S01 | I-05 S01 | Rivest, Can we eliminate certificate revocation lists?, FC '98 (abstract only; not re-verifiable from the build container) |
| F-S02 | I-05 S02 | McDaniel and Rubin, A Response to ..., FC 2000 (abstract only; same note) |
| F-S03 | I-05 S03 | RFC 6960, OCSP, 2013 |
| F-S04 | I-05 S04 | Larisch et al., CRLite, IEEE S&P 2017 |
| F-S05 | I-05 S05 | Liu et al., An End-to-End Measurement of Certificate Revocation, IMC 2015 |
| F-S06 | I-05 S06 | Brecht et al., A Security Credential Management System for V2X, arXiv:1802.05323, 2018 |
| F-S07 | I-05 S07 | Papadimitratos, Mezzour, Hubaux, CRL Distribution in Vehicular Communication Systems, VANET 2008 |
| F-S08, F-S09 | I-05 S08, S09 | W3C Bitstring Status List v1.0, 2025 (ttl; validation) |
| F-S10 | I-05 S10 | Jung, Berger, Balakrishnan, Modeling TTL-based Internet Caches, INFOCOM 2003 |
| F-S11 | I-05 S11 | RFC 9111, HTTP Caching, 2022 |
| F-S12 | I-05 S12 | Cho and Garcia-Molina, Synchronizing a database to Improve Freshness, 1999 preprint |
| F-S13 | I-05 S13 | Kaul et al., Minimizing Age of Information in Vehicular Networks, SECON 2011 (venue from the author's CV) |
| F-S14 | I-05 S14 | Yates et al., Age of Information: An Introduction and Survey, arXiv:2007.08564, 2020 |
| F-S15 | I-05 S15 | Maatouk et al., The Age of Incorrect Information, arXiv:1907.06604, 2019 |

**Not cited, because not read at origin:** IEEE 1609.2 itself, Status List 2021, Kaul et al. INFOCOM 2012, the
published versions of the arXiv items, Rivest's full text, and the scholarly-database search for the term (see the
briefs' §8). These are the first items for the author's reference set.
