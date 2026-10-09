# Meta-Commentary — 2026-10-09 (thinking out loud, after a change of assistant)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Follows:** `docs/META_COMMENTARY_2026-10.md`. Unfiltered by design; the plan
(`docs/PLAN_2026-10-09.md`) is the filtered version.

## 1. What it is like to pick this up cold
The repository carried me. Every decision since 2026-09-24 has a file, a commit and a reason:
the after-action reports, the register, the defect log, the reconciliation analyses. I could
reconstruct the state in about twenty commands without relying on the conversation summary.
That is the strongest argument yet for the discipline the author imposed: it makes a change of
hands survivable. The weak spot was the one place with no file: an agent's unfinished edits,
which existed only in the working tree.

## 2. The repository is now four repositories, not three
The October commentary said the repository had become three (two lineages plus the bundle).
The merge folded two of them together. The fetch found the fourth: the onboarding survey, with
unrelated history and its own method (gated work orders, typed placeholder tokens, an evidence
log). It is the oldest layer of the project's thinking about the same question, and it already
had a hazards register before the trunk had a defect log. It belongs in the thesis as provenance
("what the first survey found and why the trunk chose ERC-1056"), not as code.

## 3. Concerns, said plainly
- **I2I is the crux the thesis cannot evidence today.** The message-path results are all V2V.
  If the examiner reads "connected and autonomous vehicles" as including infrastructure, the
  absence of any RSU identity is a visible hole. Either build a small, pre-registered V2I
  experiment, or narrow the claim in chapter 1. I lean to building it: the identity layer is
  substrate-agnostic, so an RSU is just another DID with a road-authority issuer, and SPaT
  signing reuses the BSM path.
- **The dashboard can mislead if it is hand-assembled.** The 2026-09-24 one is now wrong in at
  least six numbers. The only safe dashboard is generated from the result files and checked
  against them in CI.
- **SUMO visualisation risks becoming the thesis's most persuasive figure while carrying its
  weakest evidence** (mock mobility, no channel). Every visual must say what is mock in the
  frame itself.
- **The change of assistant is a validity question, not just a logistics one.** Work done by
  two configurations should be reviewable as such. The after-action reports already record who
  accepted what; a later adversarial review by the other configuration would turn the switch
  into a strength.

## 4. Brainstorm
- A crux register is the missing spine. The thrusts organise the work; the cruxes organise the
  argument. The dashboard's first panel should be the cruxes, not the gas table.
- The TSR plan's coverage matrix and the sandbox's asymmetry matrix are the same object seen
  from two sides. Generate both from one source and the "what was tested vs what was claimed"
  question answers itself.
- A trace recorder for the V2V harness also gives the thesis a replay tool for the defence:
  pick a message, show its signature, its DID, its verification path and its latency.
- For infrastructure messaging, the interesting experiment is not latency (it will be like V2V)
  but revocation of an RSU key: how fast do vehicles stop trusting a compromised traffic light?

## 5. What I would do first after the audit
Close the merge pass, because an open pass is debt. Then the generated dashboard, because it
forces every number through the register one more time. Then the crux register, because it
tells us whether the infrastructure experiment is in or out.

## 6. After the pass (same day, after executing the plan under its defaults)
- **The generators were the best reviewers of the day.** Five register rows contradicted themselves,
  82 superseded figures sat in the documents a reader actually opens, and the crux register quoted two
  stale numbers because the register itself did. No human reading caught these in five passes. The
  lesson for the thesis: the claim register is only as good as the thing that reads it mechanically.
- **The agents caught the orchestrator.** The sheet agent found that my coverage matrix and test
  register had borrowed letters the TSR plan had already assigned other meanings (X, S). My own first
  stamping helper marked clean runs dirty. Small, but it is exactly the class of slip that makes the
  adversarial review worth keeping for a different configuration.
- **The thesis's hole is now one red tile.** Seven cruxes are partial and one is a gap: infrastructure
  messaging. Building it is a contained piece of work (an RSU is a DID; SPaT reuses the BSM path), and
  the design is waiting for audit. Of everything open, approving that design changes the thesis most.
- **ERC-735 being the heaviest create is a finding, not a footnote.** The two lineages each added
  veracity to the claim holder (an issuer registry, VIN binding, sticky revocation), and its create cost
  rose by a quarter since July (1,404,108 → 1,757,881 gas, register #25). Chapter 6 can say plainly that making a claim trustworthy on chain has a
  deployment price, and the asymmetry section now has its sharpest example.

## 7. After pass 10 (the infrastructure experiment)
- **The red tile is amber now, and it says something.** An RSU is a DID with a road-authority
  credential. Its SPaT costs exactly what a vehicle's BSM costs (ratio 0.996). Every forged
  infrastructure message is rejected. A revoked RSU is honoured for at most k − 1 messages by vehicles
  that already trusted it. None of this is surprising, and that is the point: the identity layer needed
  no new mechanism for infrastructure, only a different issuer and a permitted-message list. For the
  thesis, "the same layer secures V2I and I2I" is now a measured sentence and no longer a promise.
- **The bound is reached, not just respected.** At k = 25 a vehicle accepted 24 messages from a
  revoked RSU, which at 10 Hz is 2.4 s of accepting signal timing from a compromised roadside unit. I3 turns the
  freshness-k choice from an abstract latency trade-off into a safety-relevant number. It should be
  chosen once for vehicles and RSUs alike (N-17).
- **The same slip, twice.** Pass 9 fixed a run stamp that counted results files as dirty code. Pass 10
  found the same fault in the Python environment header, because the earlier fix had been made in one
  place and not as a rule. Rule 1.1.6 caught it by hand. N-14 makes the fix structural.
- **Pre-registration earned its keep in a small way.** It named an ERC-1056 operation that does not
  exist ("revoke the RSU identity"). Writing the claims before the code made that mismatch visible and
  disclosable, instead of something quietly redefined after the fact.
- **What is still thin.** The mobility is mock, there is no radio, the back-haul is a function call,
  and RSU-to-RSU messaging is not modelled. These are the same limits as for V2V, stated in the same
  words. An examiner who asks "where is the infrastructure?" now gets an answer with five register
  rows behind it, and the scope that goes with it.
