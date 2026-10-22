# Why: The Reasoning Behind the Research Expansion

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-10-15
**Companion to:** `IDEAS.md` (what), `../PLAN_RESEARCH_EXPANSION.md` (when and how), `SOURCES.md` (evidence)

This document explains *why* each proposal exists: what question it answers, what result would change the thesis, and why it is worth the time. It also records the method used to generate the ideas, so the method can be reused.

---

## 1. The argument in one paragraph

The thesis has shown, carefully and reproducibly, that each blockchain-identity primitive can be measured, and that the light ones are cheap and fast enough for vehicles. A reader who accepts all five hypotheses can still ask: *does it work when a car actually uses it?* Real use is never one primitive. A single toll gantry needs:

- identity (who is this car?), endorsement (who vouches for it?), and privacy (what does the gantry learn?);
- revocation (is the vouching still true?), payment (who pays, in what, with what gas?), and a legacy path (what about the 95% of cars with no wallet?).

The expansion turns the thesis from "the parts are good" into "the parts compose, and here is what composition costs and reveals". It does that with a small number of relatable scenarios that each exercise many primitives at once, plus the primitive upgrades those scenarios turn out to need.

## 2. Why composition is a research contribution, not a demo

**Unit results do not imply system results.** H3 says verifying a message takes 0.153 ms. H1 says creating an identity costs 52k gas. Neither says what happens when a revocation lives in two places, or when a privacy-preserving pseudonym is used to pay a bill that names the owner. Those are emergent properties of the composition, and they are where real systems fail.

**X1 already proved this.** Building the toll corridor surfaced two findings that no per-primitive measurement in the repo could have produced:

1. **Split-brain revocation.**
   - The DMV's registration revocation lives in an off-chain status registry.
   - The ministry's endorsement revocation lives in an on-chain bit.
   - A gate that checks only the VP admits the car whose endorsement was revoked on-chain. A gate that checks only the chain admits the car whose registration was suspended off-chain.
   - The test suite pins both cases (`test_x1_toll_corridor.py::test_mixed_fleet_admits_valid_and_denies_revoked`). This becomes a design rule: *every layer that can hold revocation state must be consulted on the decision path*, with a measurable cost.
2. **Rotation is not unlinkability.**
   - Register #38 showed that ERC-1056 pseudonym delegates are linkable through the identity's event topic.
   - X1 shows the same thing from the application side: the ticket must name the DID that holds the escrow, so every `TollPaid` event links trips together.
   - The gap now has a concrete, testable target: P5, unlinkable passage with nullifiers.

**Examiners ask integration questions.** "How would this be deployed?" and "What about cars that are not upgraded?" are standard questions at a defence. A scenario chapter answers them with code and numbers rather than prose.

## 3. Why the toll corridor came first

The toll corridor is the cleanest possible bridge between the thesis's two halves:

| Thesis half | Property | Toll corridor phase |
|---|---|---|
| H3 (latency) | Reads are off-chain, fast, private | Gate: VP verify + `checkTicket` |
| H1 (gas) | Writes are on-chain, costly, public | Toll: `settleBatch` |

A toll is the most familiar everyday *write* a vehicle makes. The read/write asymmetry the thesis measures in the abstract becomes something a non-specialist understands immediately: you pass the gate (read), then you pay (write).

It also exercises the official-party pattern the domain needs. A government DID **issues** and **sponsors**; the vehicle DID **holds** and **signs**; an operator **verifies** and **settles**. Those are the three roles of the SSI triangle, plus a sponsor role (the DMV relaying `addDelegateSigned` and paying gas) that the literature rarely models but deployments always need: cars do not hold ETH.

Finally, it is grounded:

- every primitive in it is a finished standard (EIP-712, ERC-2612, ERC-1056, W3C VC 2.0);
- it runs on the existing Hardhat and Python stacks with no new dependencies;
- it produced measurable results on day one (gas per ticket, gate latency, exposure list).

## 4. Why each scenario

Each entry below states the question, the result that would change something, and the reason now.

**X2 — Rental handoff (driving licence + session keys)**
- *Question.* Can a car be the verifier of a human credential, and enforce a revocation that happens mid-session?
- *Result that matters.* If the time from a status-list flip to refusal is dominated by when the car checks rather than by crypto cost, the design rule is "check at ignition and at every toll", not "check faster". That is a policy finding.
- *Why now.* Mobile driving licences are being deployed: AAMVA guidelines v1.6, ISO 18013-5/-7, the EU directive tying licences to the EUDI wallet (S10–S15). The thesis is the right place to show where the licence meets the car.

**X3 — Used-car sale (oracle + legacy title + atomic swap)**
- *Question.* What is the trust surface of letting legacy government data into the chain, and can a sale be atomic across identity, money and registration?
- *Result that matters.* A collusion threshold, "k oracles must lie to wash a title", turns "oracle risk" from a hand-wave into a number. An atomic swap that costs less than the sum of its parts would be a positive design result.
- *Why now.* MOBI VID's value proposition is fraud reduction in resale. The repo already detects odometer rollback (`lifecycle_events.py:431`), but only against its own data. Cross-checking against NMVTIS (S50) is the realistic version.

**X4 — Dual-stack intersection (PKI + SSI migration curve)**
- *Question.* What does the transition cost, in bytes, CPU and actionable safety messages, as adoption rises from 0% to 100%?
- *Result that matters.* If dual-signing at 30% adoption pushes BSMs over the payload budget, migration needs a different design (bridge attestations at the RSU rather than dual signatures). If shadow mode catches revocation disagreements cheaply, it is the recommended rollout path.
- *Why now.* Every deployed V2X system is PKI (IEEE 1609.2, ETSI CCMS: S20–S23). An SSI thesis that never meets PKI on the road leaves its most important deployment question open. The repo already has both identity layers side by side in `sumo_identity_integration.py`; only the policy and the sweep are missing.

**X5 — Ambulance green wave (accountable anonymity)**
- *Question.* Can a privilege be pseudonymous on the road yet auditable afterwards, without one party able to de-anonymise alone?
- *Result that matters.* A working 2-of-3 audit opening plus nullifier-bounded abuse is a clean demonstration of "privacy with accountability". That is the line regulators draw (GDPR plus law enforcement).
- *Why now.* Signal pre-emption is one of the oldest connected-vehicle applications. It shows delegation chains: health authority → dispatch → vehicle. The repo's VC layer does not exercise those yet.

**X6 — Sovereign Plug & Charge (battery passport + payment channel)**
- *Question.* Above how many events per session does a payment channel beat per-event settlement (X1), and can the car act as an issuer (V2G receipts)?
- *Result that matters.* A break-even curve, combined with P14 fiat costs, gives a design rule for which vehicle payments should be channels.
- *Why now.* EU battery passports apply from 2027 (S52), and MOBI has a Battery Birth Certificate (S53). ISO 15118-20 Plug & Charge already runs a multi-root PKI (S41): a real precedent for the trust-federation problem SSI claims to solve.

**X7 — Recall to OTA (chain of custody)**
- *Question.* Can UN R156 software-update evidence be a verifiable presentation instead of a document dump?
- *Result that matters.* If the evidence-pack size is constant in fleet size (Merkle aggregation), compliance auditing scales. That is a direct regulator-facing contribution.
- *Why now.* R155/R156 are mandatory for type approval in UNECE markets (S55–S56). Uptane (S58) is the OTA security standard. Neither speaks VC.

**X8 — Consent-scoped black box**
- *Question.* Can crash evidence be both tamper-evident (anchored before the incident) and minimally disclosed (only the seconds that matter)?
- *Result that matters.* Staged-crash detection with only per-minute anchoring would be a strong fraud result, at near-zero gas once batched (P15).
- *Why now.* EDPB guidance (S60) pushes personal data off-chain. This design keeps raw data off-chain and puts only commitments on-chain, which is the compliant pattern made concrete.

**X9 — Border crossing (federated trust registries)**
- *Question.* How do two jurisdictions' issuer lists recognise each other partially ("title history yes, registration no")?
- *Why now.* The thesis is one-jurisdiction by its own admission (chapter 7 §7.5). BC ↔ Washington is the most natural cross-border pair for a UBC thesis.

**X10 — Robotaxi as an economic agent**
- *Question.* What identity does an autonomous agent need: its own, its operator's, its model's, or all three?
- *Why now.* Agent-identity standards are forming (ERC-8004, S83). An empirical study already finds most agent registrations are not live, which is a warning that identity without liveness or provenance is hollow. AVs are the highest-stakes agents there are.

**X11 — Parking-enforcement inversion; X12 — Proof of not-stolen**
- These are small and grounded. They show the same machinery transferring to new domains cheaply: a generality argument for the thesis's H4.

## 5. Why the primitive upgrades

The P-series exists because the X-series needs it. Each P item is justified by the scenarios it unblocks (the "Needed by" column in `IDEAS.md` §2), not by novelty for its own sake. Three clusters:

**Rigor upgrades: P1 EIP-712, P2 Bitstring Status List, P6 on-chain resolution, P12 formal/fuzz.**
- These close known gaps.
- The repo uses three different signing schemes: ERC-191 v0, EIP-191 personal-sign, and a raw digest. Only domain separation stops a signature made for one contract from being replayed at another.
- Revocation is a custom JSON registry, not a W3C status list.
- The resolver synthesises documents instead of reading the chain.
- Each one raises the credibility of every existing number. P2 and P6 may also move the compliance score; that is a reason to re-run the checker, not to chase the score.

**Standards-alignment upgrades: P3 SD-JWT, P10 OpenID4VC, P11 mdoc, P13 did:web/did:x509.**
- These connect the thesis to the stack governments are actually deploying: EUDI ARF, AAMVA mDL, OpenID4VC Final (S14, S13, S18).
- Without them, a reader can fairly say the thesis built a parallel universe. With even a minimal version of each, the thesis can say "our results transfer to the deployed protocols, at this measured overhead".

**Capability upgrades: P4 BBS, P5 unlinkable passage, P7 trust registry, P8 4337 hardening, P9 oracle, P14 fiat cost, P15 anchoring.**
- These are the new capabilities the scenarios demand.
- P5 matters most scientifically. It is the only way to resolve the X1 and #38 linkability findings, and the result would be a clear statement: "unlinkable toll passage costs N gas and M ms of proof generation on an ECU-class device."

## 6. Why moonshots at all

A master's thesis does not need to land a moonshot. It benefits from *pointing at them with evidence*. Chapter 7's future work is stronger when each item carries a prototype result, a measured obstacle, or a precise reason it fails. Three moonshots are especially worth even a partial attempt:

- **M1 post-quantum hybrid BSMs.** A one-afternoon size and latency measurement answers "does PQ fit in a BSM?" with a number. Vehicles built today will still be on the road when PQ migration is mandatory (S74–S77).
- **M4 ZK usage-based insurance.** The literature sweep found **no peer-reviewed ZK-telematics UBI paper** (S89). A credible gap like that is a publishable side paper (proposed SP-9).
- **M9 fifteen-year identity.** Vehicles outlive cryptosystems. Showing that a DID-anchored key rotation keeps the MOBI history intact through an algorithm change is a direct argument *for* DIDs over certificates.

## 7. How this maps onto the thesis

### Existing questions strengthened

| RQ / H | Strengthened by |
|---|---|
| RQ1 / H1 (cost) | X1 per-ticket and batch gas; X6 channel break-even; P14 fiat costs per vehicle per year |
| RQ2 / H5 (security) | 14 composite X1 attack cells; P1 cross-contract replay cells; P8 recovery cells; X3 oracle collusion threshold |
| RQ3 / H2 (compliance) | P2 Bitstring Status List; P3 SD-JWT; P10 OpenID4VC; P11 mdoc (standards a regulator recognises) |
| RQ4 / H3 (real time) | X4 migration curve on the BSM path; M1 PQ sizes; X1 gate-read latency |
| H4 (portability) | X11, X12, X9 (same machinery, new domains and jurisdictions) |

### Proposed new questions (author decision; not adopted)

- **RQ5 (composition).** Do per-primitive security guarantees survive composition into end-to-end vehicle services, and what new failure modes appear?
  - Candidate H6: every composite service has at least one revocation-consistency requirement not visible at the primitive level. X1 is the first instance.
- **RQ6 (transition).** What are the cost, privacy and safety curves of migrating a road network from PKI and plate-based systems to SSI?
  - Candidate H7: a shadow-mode dual stack detects all injected revocation disagreements at under 2× per-message verification cost.
- **RQ7 (privacy-preserving payment).** Can a vehicle pay for road use without becoming linkable across sites, at a gas cost within an order of magnitude of a linkable toll?
  - Candidate H8: P5 settles an unlinkable toll at ≤ 10× X1's 110.6k gas.

The repo's culture is pre-registration with PASS/FAIL reported as observed (#33, #37, #38). If adopted, H6–H8 should be pre-registered with their thresholds **before** P5 and X4 are built.

## 8. What could go wrong (threats to validity and to the thesis)

- **Scope creep.** This catalogue holds about 35 items. A thesis needs perhaps 4. The plan (`../PLAN_RESEARCH_EXPANSION.md`) separates a thesis track (Phases 0–3) from side-paper and future-work tracks. Choosing the cut is the author's decision.
- **Demo-ware.** A scenario that prints success is not evidence; the repo's own review 02 found use cases that asserted nothing. Every X scenario must carry negative tests (X1 has 14 attack cells and an off-chain/on-chain revocation pair), computed pass/fail, and a stated condition tag.
- **Mocked legacy systems.** The oracle, the CAD system and ANPR are simulated. Results about them are architecture results, not field results, and must say so. X1 already declines to report a legacy-lane latency because there is no ANPR model.
- **Measurement condition.** X1 latency is M1 over HTTP on one host. Gas is deterministic per input but varies by about 12 gas run to run, because fresh keys change calldata zero bytes. Those numbers need register rows with that caveat before entering a chapter (proposed #55/#56).
- **Novelty claims.** S31 (zero-trust DID for AVs, 2025) and S85 (DID benchmarking, 2026) are close prior art. Read both before writing "first". Use the repo's existing SC-04 rewording: "measured, domain-constrained, reproducible".

## 9. The method: how the ideas were generated (reusable)

These are the prompts used to turn a primitive into a scenario. Apply them to any new primitive.

1. **Find its everyday act.** What does a driver, owner, mechanic, officer or toll operator *do* that this primitive is secretly part of? (Pay a toll, rent a car, sell a car, get a recall fixed.)
2. **Pair every read with a write.** Verification is cheap and private; settlement is costly and public. A scenario that has both measures both halves of the thesis at once.
3. **Pair every new thing with an old thing.** For each scenario, ask what happens to the car with no wallet, and the agency with only X.509. The legacy lane is never optional.
4. **Count what the counterparty learns.** List the identifiers the verifier sees and whether they link across sites. This produced the X1 linkability finding.
5. **Ask who pays the gas.** Cars hold no ETH. Sponsorship, paymasters, permits and relayers are always in the design.
6. **Revoke something mid-story.** Then ask which layer notices first, and whether every layer notices at all. This produced the split-brain finding.
7. **Ask what an attacker would edit.** Class, subject, digest, nonce, gantry, signer, batch. Each becomes a test cell.
8. **Push one step past comfortable.** For every grounded scenario, write the moonshot version (PQ, ZK, agents, markets), even if it only becomes a paragraph of future work.

## 10. What was executed in this session

- X1 was designed, built and tested:
  - contracts `CVINTollCorridor.sol` and `CVINTestStable.sol`, with 20 Hardhat tests;
  - a Python scenario with a mixed SSI/legacy fleet, and 4 pytest cases;
  - a committed results file.
- Totals after the build: Hardhat 389 passing / 23 pending (was 369 / 23); Python 362 (was 358); compliance 94.3% (unchanged).
- This catalogue, its sources, the execution plan and the phased prompt pack were written.
- Nothing in the existing contracts, tests, register or chapters was changed.
