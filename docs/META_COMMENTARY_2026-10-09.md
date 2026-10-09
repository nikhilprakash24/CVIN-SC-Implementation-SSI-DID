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
