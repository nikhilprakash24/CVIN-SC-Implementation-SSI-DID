# Decision Sheet, 2026-10-20: Every Open Decision on One Page

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-20 (after-action report 24).
**What this is:** every decision that is the author's and still open, gathered from the five files that hold them,
with what each blocks, the default in force, and the orchestrator's recommendation. **Nothing here is decided by this
sheet.** An answer is recorded in the file named in the "Lives in" column, with the date; the defaults stand until then.
Ordered by what an answer unblocks.

## A. Decisions that block the thesis text
| Id | Question | Lives in | Blocks | Default in force | Recommendation |
|---|---|---|---|---|---|
| N-23 | AI-use statement: in the README and the thesis front matter, and whether reports keep the first person | `docs/MILESTONE_NEXT.md` | the contribution record and any hand-over document (the progress report, report 24); the front matter | none added | **Decide first.** Add a short statement in both places, in the wording the university's policy requires; say what the assistant did (code, measurement runs, reports under direction) and what the author did (direction, decisions, review). Keep the reports' first person, with the statement saying whose voice it is. Nothing else on this sheet can be shown outside the project until this exists |
| D-1, P2-D10 | Adopt Scope v3 and its decisions D-2 to D-15 | `docs/phase2/SCOPE_RECONCILIATION.md` §6; `docs/phase2/DECISIONS.md` | WM-2 D1 (chapters 1, 4, 6, 7); the title; chapter 2 | as recommended there | **Adopt as a block**, with the exceptions below taken one by one. The reconciliation was written by the academic adviser against the register; every placement cites a row |
| D-15 | Write chapter 2 next, with IDTx positioned inside it | same | Phase 2 design beyond documents | yes | **Yes, and the I-24 brief changes what it says:** ERC-3643 and guarded transactions (Luu et al. 2016) are prior work the chapter must cite; the IDTx is then a taxonomy and a measurement of storage locus and staleness, not a new mechanism (`docs/phase2/briefs/I-24_IDTX.md` §3, §6) |
| D-7 | IDTx and F1–F3 in the thesis: definition and taxonomy only, no pre-defence experiment | same | WM-2 §6 freeze | (a) only | **Keep (a).** The brief's finding strengthens it: without E-F1-2 and E-F1-3 the experiment cannot pass its own kill criterion, and those are post-defence work |
| D-12 | The k the thesis defends | same | chapter 5's freshness section; N-9, N-17 | the one-call probe at k = 1, host dependence stated | **Keep, with #52 cited:** on a host with t_local near 0.33 ms the probe reaches P*(0.5) ≥ 100 at k = 25, so the thesis can state the policy and the host condition together. The I-05 brief gives the formula (k_min = ceil(t_chain / (B − t_local))) to put beside it |
| D-14 | Title | same | front matter | add "measured" or use the §2.1 title | **The §2.1 title.** The current one promises a comparison of systems; the work compares substrates on one lifecycle |
| D-2 to D-6, D-8, D-11 | Wording and placement items | same | chapter edits in D1 | as recommended | **Adopt with D-1** |

## B. Decisions that block a run or a build
| Id | Question | Lives in | Blocks | Default in force | Recommendation |
|---|---|---|---|---|---|
| D-10 | Sepolia witness before the defence (N-11) | `SCOPE_RECONCILIATION.md` | the most visible open item | run if the author supplies a funded key and an endpoint | **Supply them if you can within a day; otherwise state the limitation.** One run of an existing harness |
| P2-D9 | Install a permissioned EVM client for F2 | `docs/phase2/DECISIONS.md` | E-F2-1 | no, until after the defence | **No until after the defence** (D-13) |
| P2-D4 | SUMO install (N-4) and Sepolia for Phase 2 | same | I-01, I-03 | no | **No; D-10 covers the one Sepolia run** |

## C. Decisions on the Phase 1 defaults taken in passes 21 and 22
These stand unless overturned; each is reversible, and the cost of reversal is stated.
| Id | Default taken | Lives in | If reversed |
|---|---|---|---|
| C1-d1 | Without a provider the resolver returns the default document, stated as not read from a chain | report 21 | every current caller and #4, #24 move; a chain-backed suite run (N-24) first |
| C1-d2 | `notFound` for a chain with no configured registry | report 21 | one error code; trivial |
| C1-d3 | Verification method type unchanged | report 21 | the suite inputs change; re-run #24 |
| C1-d4 | Chain-backed suite run deferred (N-24) | report 21 | a session of work |
| C2-d1 | Owner-or-delegate (the plan's fix), not the OWNER-role-only check | report 22 | D54 reopens for every other role |
| C2-d2 | Delegations stored in the MOBI registry (`MOBIVIDRegistry`), overriding the base's delegate functions; the base stays event-only | report 22 | the vehicle-profile column changes, as the first design showed |
| C2-d3 | `veriKey` as the consent delegation type | report 22 | tests, demos and the Python client change the type string; gas unchanged |
| C2-d4 | A role is still required to attest | report 22 | authority model changes; threat model G4 rewritten |
| C2-d5 | Moved MOBI cells re-run and stated as they fell | report 22 | none |
**Recommendation:** accept all nine as taken. C2-d1 and C2-d2 are the two with substance; both follow the plan's words
and the canonical registry.

## D. Phase 2 programme decisions
| Id | Question | Lives in | Blocks | Default in force | Recommendation |
|---|---|---|---|---|---|
| P2-D1 | Which programme and which ideas | `docs/phase2/DECISIONS.md` | gate G1; everything after P2.1 | none chosen | **PG-focus (the author's three focuses) with I-05 added**, because the I-05 brief gives F3's freshness work a formal frame and two pre-stated predictions, and I-24's value now depends on its experiments rather than its definition. Defer the rest |
| P2-D2, D-13 | Time box: documents only until the defence | both files | build waves | documents only | **Yes** |
| P2-D7, D-9 | The three modes of F3 | both files | chapter 6's F3 section | the adviser's six cells for the thesis; the single axis for Phase 2 | **Adopt both as stated**: the six-cell frame in the thesis (all six measured), the single axis as Phase 2's analytic frame |
| P2-D8, D-6 | The name and definition of the IDTx | both files | any writing that names it | IDTx; the review's §3.3 definition | **Keep the name; keep the definition; add the brief's finding that it is not new as a mechanism** |
| P2-D3, P2-D5, P2-D6 | Session-1 scores as the starting register; C8 framing; where Phase 2 code lives (plug-in layer) | `DECISIONS.md` | little | as stated | **Accept the defaults** |
| I-24 finding | Keep the IDTx paper, or keep IDTx as a taxonomy in chapter 6 | `docs/phase2/briefs/I-24_IDTX.md` §6 | the F1 plan's kill criterion | the brief proposes tying the criterion to E-F1-2 and E-F1-3 before the plan is locked | **Tie the criterion to E-F1-2 and E-F1-3**, and decide the paper after they run, post-defence |

## E. How to answer
Reply with the ids and a word each ("D-1 yes", "D-14 §2.1 title", "N-23 add, first person stays"). The next pass
records each answer in its file with the date, and the defaults it overturns are listed in the report with their cost.

## F. Answers recorded
| Id | Answer | Date | Recorded in | Default overturned? |
|---|---|---|---|---|
| D2 | D2-a: RSU-to-RSU messaging is out of scope, and the thesis says so | 2026-10-24 | SC-24; chapter 6 §6.6.3; crux C3 gap; `docs/PLAN_WM-2.md` D2; N-16 closed; report 38 | no (the recommendation) |
| B-1 to B-4 | not answered; the author's "integrate with the other code sessions" is read as approval of the recommended integration steps only, as report 38 records | 2026-10-24 | `docs/planning/BRANCH_REVIEW_2026-10-24.md` | — |
