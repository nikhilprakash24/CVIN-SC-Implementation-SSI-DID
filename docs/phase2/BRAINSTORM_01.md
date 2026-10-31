# Phase 2 Brainstorm, Session 1 — Method, Divergent List, Parked Ideas, Open Questions

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Session:** 2026-10-14 (Phase 2, P2.0, session 1). **Binds:** `docs/phase2/README.md`.
**State:** divergent first pass by the orchestrator. Nothing here is decided. Converged ideas moved into
`ideas.yaml`; the rest is kept here so it is not lost or silently re-invented.

## 1. Method
1. **Inventory first.** Every open item in Phase 1's registers (cruxes, defects, deferred items, scope changes,
   chapter 7 future work, side papers, the original direction) was listed as a seed (`EVIDENCE_BASE.md` §2).
   This is so that ideas grow from evidence, not from a blank page.
2. **Diverge per plane.** For each plane of the reference model (`ARCHITECTURE.md` §1), ask what would change
   if that plane became real, adversarial, larger, private or provable. The answers are in §2.
3. **Converge by anchor.** An item became an idea (I-nn) only if it had a Phase 1 anchor, a first step of one
   or two sessions and a kill criterion. Items without one are parked (§3), with what they lack.
4. **Bundle.** Ideas that share an interface or a crux were bundled into candidate programmes (PG-…), so that
   the author chooses a direction, not a list.
5. **Look for gaps in the register itself** (§4). The register is checked for what it does not cover.

## 2. Divergent list (by plane)
| # | Plane | Prompt | Item | Went to |
|---|---|---|---|---|
| B1-01 | P0 | real | SUMO/TraCI mobility instead of the mock | I-01 |
| B1-02 | P0 | larger | corridor and city scale (thousands of vehicles, tens of RSUs) | I-01 + AQ-4 |
| B1-03 | P0 | adversarial | adversarial density: Sybil swarms concentrated on one RSU | I-07 (detector input), parked as its own (§3) |
| B1-04 | P1 | real | channel access via a network simulator | I-02 |
| B1-05 | P1 | real | hardware radio, real RSU | I-23 |
| B1-06 | P1 | new link | RSU-to-RSU channel | I-04 |
| B1-07 | P2 | real | public testnet and rollups | I-03 |
| B1-08 | P2 | provable | formal properties of the contracts | I-12 |
| B1-09 | P2 | adversarial | chain-id binding of signed operations | I-08 |
| B1-10 | P2 | larger | state growth: registry storage at a national fleet size, and what pruning or archival would cost | parked (§3) |
| B1-11 | P3 | private | selective disclosure; ZK VIN | I-10, I-09 |
| B1-12 | P3 | new frame | the veracity-versus-automation asymmetry (C8) as a credential property: who attests that an automated report is true | gap (§4) |
| B1-13 | P3 | hybrid | 1609.2 certificates anchored to DIDs | I-06 |
| B1-14 | P3 | regulatory | EU digital identity wallet mapping | I-17 |
| B1-15 | P4 | theory | an optimal re-check policy | I-05 |
| B1-16 | P4 | provable | model checking caches and clocks | I-13 |
| B1-17 | P4 | end-to-end | misbehaviour detection to exclusion | I-07 |
| B1-18 | P4 | governance | who may revoke: a revocation authority's own key compromise and its recovery | parked (§3) |
| B1-19 | P5 | reuse | the evidence machinery as a toolkit | I-18 |
| B1-20 | P5 | interface | an explainer that answers only from V rows | I-22 |
| B1-21 | P6 | release | open testbed, newcomer reproduction | I-19 |
| B1-22 | all | people | the author's notebook threads | I-20 |
| B1-23 | all | dissemination | side papers | I-21 |
| B1-24 | P3 | user | the trust user study (original RQ5, "future work") | parked (§3) |
| B1-25 | P2 | economics | fee markets: who pays for a vehicle's identity operations (manufacturer, owner, operator), and what does each payer model change | parked (§3); partly inside I-03 |

## 3. Parked items (not ideas yet), with what each lacks
| # | Item | Lacks | Would be unparked by |
|---|---|---|---|
| B1-03 | Adversarial density (Sybil swarms) as its own study | a Phase 1 anchor beyond the 43-cell harness; needs real mobility | I-01 done; a detector from I-07 |
| B1-10 | State growth at fleet scale | a measurement plan and a fleet size the author accepts | P2-D2 (scale) and I-03 |
| B1-18 | Revocation-authority compromise and recovery | a threat model in Phase 1 (the threat model covers vehicles and RSUs, not the authority) | a threat-model extension written first |
| B1-24 | Trust user study (original RQ5) | ethics approval, participants, a design | the author's decision; outside an engineering programme |
| B1-25 | Payer models for identity fees | fee data (I-03) and a stakeholder model | I-03's rollup arm |

## 4. Gaps in the register itself
- **C8 (veracity versus automation) has no idea that moves it directly** (`EVIDENCE_BASE.md` §4). B1-12 is
  the nearest: treating "this automated report is true" as an attested claim with an attester and a cost.
  It needs the author's framing of C8 before it can be an idea. Asked as Q-P2-4.
- **No idea measures human or organisational cost** (operator burden, governance latency). B1-18 and B1-24 are
  where it would come from.
- **Two tracks hold most of the top of the ranking** (T and R). This may be the evidence or a bias of the scorer.
  The adversarial brainstorm (P2.1c) is asked to test it.

## 5. Questions for the author (answer any; defaults hold otherwise)
| # | Question | Default if unanswered |
|---|---|---|
| Q-P2-1 | Is Phase 2 meant to extend the MASc thesis (a chapter or more evidence before the defence), to follow it (a PhD proposal, papers, a lab platform), or both? | both: P2.1–P2.3 are planned so that the first build wave can feed the thesis, and the rest follows it (P2-D2) |
| Q-P2-2 | Which notebook threads should enter the register first? | none until given; I-20's intake template is ready |
| Q-P2-3 | Is installing SUMO (N-4) and running on Sepolia (N-11) now acceptable for Phase 2 work? | no change to the Phase 1 defaults; ideas that need them are planned but wait |
| Q-P2-4 | How do you frame C8 (veracity versus automation), and should Phase 2 give it a hypothesis? | C8 stays as it is; B1-12 stays parked |
| Q-P2-5 | Any idea to add, drop or re-score now? | the session-1 scores stand as orchestrator estimates |
