# CVIN-SC: The Thesis on One Page — the research side

Nov 5, 2026 · Nikhil Prakash · **Companion to the code-side one-pager of the same date; the two are halves of one picture (see "How this page joins the other one", at the end).**

## The thesis

**Towards a Minimal Function Specification for Blockchain-Based Self-Sovereign Identity in Connected and Autonomous Systems.** Working title; see decision 5. MASc, Electrical and Computer Engineering, UBC. Nikhil Prakash.

Vehicles that talk to each other authenticate under a pseudonym scheme that is unlinkable by design, so no persistent identity history can be attributed to a vehicle. That is a correct design decision with a structural consequence: the registration, authorisation, delegation and revocation operations that cooperative and administrative vehicular services need have no identity layer to run on. This thesis derives the smallest interface such a layer must expose — twelve functions, `IMinimalSSI`, derived from the normative operations of the W3C DID and Verifiable Credential models together with Allen's ten principles of self-sovereign identity — and shows it to be a sufficient and irredundant cover of that requirement set under a published clustering rule (not the unique minimum). It then asks which currently specified blockchain identity standards provide those functions natively, finds that none provides presentation construction (`createPresentation`, the one function that discharges Consent and Minimization), evaluates eight implementations against the interface under a pre-registered protocol, and shows what does and does not transfer when the principal is an autonomous software agent rather than a vehicle.

## Research questions and what the evidence currently supports

The thesis carries no hypotheses; it carries three questions, each answered in a stated form at a stated evidence status (verdict · expectation · analysis). The research-side numbers below are the hub's numbers of record (sandbox `cvin-sc`, solc 0.8.24, Hardhat in-process; protocol gas at N = 5 per cell under ruling D-R8).

| RQ | Question | Answer as it stands | Status · evidence |
| --- | --- | --- | --- |
| RQ1 | What operations must an identity interface expose to satisfy the W3C DID/VC normative operations and Allen's principles, and can it be stated as a sufficient and irredundant cover under a declared clustering rule? | Twelve functions in two sets: Set A (eight identifier and key functions) and Set B (four credential functions). Three functions are principle-necessary, five operation-necessary, four conventionally necessary. The set is closed under the stated lifecycle transitions over the exhibited object set, with a falsification condition; the closure analysis found one gap (early delegate revocation) and amended the specification (F11). | **analysis**, mechanically checkable (29-operation universe, two elimination tests, graded principle matrix) · §2.3 v2.0, App. M-1, M-2 |
| RQ2 | Which blockchain identity standards provide those operations natively, and where one does not, is the shortfall implementation or specification? | Set A is fully native on ERC-1056 only; Set B is native on no EVM standard except as claims or tokens without expiry; `createPresentation` is an anchor on every EVM option and off-ledger on Indy. Eight options pass the same twelve-test suite unmodified. Gas and coverage rank the options differently. A provisional census of 30 ERCs found none specifying holder-side presentation (N = 0, P = 17, X = 13; single rater, not yet official). | **verdict** for ERC-1056 (12/12; eleven of twelve gas values reproduce to the digit across three runs over four and a half months); **protocol gas** on eight options (128/128 cells, N = 5, all repetitions identical); coverage **declared classes, pre-protocol** (D-R7); census **expectation** until executed with a date |
| RQ3 | Does the interface transfer to autonomous software agents, and what does not transfer with it? | The interface transfers; the trust model does not. Five functions transfer exactly, seven modified, none absent; nine non-correspondences named. The specification bounds authority, not intent. A smart-account wrapper is specified, not built. | **analysis** · §5.2, Appendix I (wrapper at Version 2, no validation rung reached) |

Two supporting results worth a paragraph each: an independent on-chain/off-chain placement procedure lands on exactly the Set A / Set B boundary; and "Tier-2 compliance is not a ledger property" — in every scenario the Tier-2 critical path carries only reads and off-chain steps, every write is Tier 3.

## The chapters

Under ruling D-R9 (30 October 2026) the hub's five drafted chapters (≈60,200 prose words) and the code-side's seven (≈45,000) become **one seven-chapter thesis** of about 68,000 words, on the hub spine, with the applied system as Chapter 6. The hub side of each chapter and what it rests on:

| Chapter | What it argues | What it rests on (research side) |
| --- | --- | --- |
| 1 Introduction | The accountability gap is structural; the 2020 CVIN architecture assumed the layer this thesis supplies; contributions C1–C14 with their evidence states | Ch. 1 v1-1 (repo); Table 1.1 audited against the corpus |
| 2 Background and related work | SSI principles at definitional strength; W3C standards with a version freeze; V2X and the three-tier latency framework; agent identity | §2.0/2.1/2.2/2.4/2.6 drafts; reservoirs CB-TL / CB-IG; K-15 correction (BSM 10 Hz nominal) |
| 3 The IMinimalSSI specification | The derivation as an irredundant cover under CR-1…CR-3; necessity partition; closure relation and Amendment F11 | §2.3 v2.0 — the strongest material in the corpus |
| 4 Methodology | The pre-registered protocol (commit `0a10831`, 15 Oct): N = 5 gas / N = 30 timing, seven void rules, F/P/X rubric, self-audit; disclosure of the eleven runs that pre-date it | §2.5 v1-1 with its dated deviation note |
| 5 Standards inventory and specification evaluation | Seventeen options in six families; Family E decomposed; the `createPresentation` gap; coverage, protocol gas and deployment gas on eight options | Ch. 3 v0-9; Ch. 4 §4.2–4.4 v1-2; Phase 1 record; D-R7/D-R8 |
| 6 Vehicular instantiation | The code side's applied system (W3C layer, V2V, MOBI VID, security, ZK, Steward), labelled by its own measurement regime | Code-side one-pager; spoke import `docs/12_spoke_import/` |
| 7 Discussion and conclusions | The gap as structural; agents; convergence as corroboration; concession-set limitations; RQ answers in the "cover, not minimum" form | Ch. 5 v1-0 §5.1–§5.6 |

The research side also holds a complete lift-and-assemble draft of the hub thesis in my voice (Take 1, 4 November, ≈27,000 body words) and two further drafting programmes planned and ready to run: a panel rewrite (Take 2) and a provenance-tagged supervisor draft (G-SD1, ten stages) in which every paragraph carries an origin tag so you can see which words are mine.

## Decisions I'd like your view on

1. **Admissibility (R-ADM-1 / R-ADM-2).** The eight-option runs of 17–19 October were made after the protocol was pre-registered but not under it; by ruling D-R7 they are admitted with the deviation disclosed, and the gas was re-measured under the protocol (D-R8). Should coverage stay reported as declared classes, or be re-run to rubric verdicts before the defence?
2. **One thesis, one spine (D-R9).** The hub absorbs the applied system as Chapter 6 and keeps RQ1–RQ3 as principal, with the code-side's questions as sub-questions (gas, conformance, security, MOBI VID, V2V feasibility). Confirm, or prefer the alternative where the benchmark questions lead?
3. **Contribution count.** C15 (a planned paper) is withdrawn from the table; C16 (revocation latency as a safety budget) and C17 (ordering authority) are proposed; a second "C16" (endorsement-gated credential architecture) from the hybrid-data campaign must be folded or renumbered.
4. **AI assistance.** The drafting programme has used an AI assistant substantively since early 2026 to organise the corpus, structure my results into prose, cross-check numbers against traces and act as a reviewer panel. UBC asks that this be disclosed and approved in writing before drafts are relied on. I would like to send you a one-page disclosure and agreement, with the authorship timeline attached, before any chapter.
5. **The title.** The hub title promises a *minimal* specification; the answer the thesis gives is a sufficient and irredundant cover. The code-side title promises a comparison of SSI systems. One title must serve the unified thesis; the candidates are the hub title with "minimal" kept and qualified in §1, or *Measured Trade-offs of Ethereum Identity Standards for Connected Vehicles*. Keep, replace, or something between?

## How this page joins the other one

The code-side page describes the applied system by its own five research questions and six hypotheses. Under D-R9 those are not a second thesis; they are sub-questions of this page's RQ2 and RQ3 and one cross-cutting feasibility question answered in Chapter 6. The labels differ on purpose, because the same labels mean different things on the two sides (the code side's RQ1 is gas; this page's RQ1 is the interface):

| Code-side question | Where it sits in the unified thesis |
| --- | --- |
| RQ1 gas (H1) | RQ2a — what each provision costs, under the protocol (hub) and as native analogues (code side, indicative, different toolchain) |
| RQ3 W3C conformance (H2) | RQ2b — how far a resolution and issuance layer lifts an on-chain identity to DID Core / VC DM conformance |
| RQ2 security (H5) | RQ2c — security and recovery properties under the V2X threat model |
| RQ4 industry / MOBI VID (H4) | RQ2d — realisability of the MOBI VID model across backends |
| RQ4 real time (H3) | RQ-V — does verification of pre-issued credentials fit the V2V per-message budget (scoped to the verification step) |
| RQ5 ZK and the Steward (H6) | RQ-V2 (feasibility at registration and session time) and RQ3a (what operating the proofs safely requires of a custodian) |

The two sides' gas numbers are never put in one table: the hub measures `IMinimalSSI` functions under a pre-registered protocol on a legacy/paris toolchain; the code side measures native analogues on viaIR/cancun. Both are kept, each in its own table with its toolchain in the caption.
