# TDP-001 — Programme Summary

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-15 (after-action report 20). **Revision:** A.
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`; `docs/tdp/README.md` (TDP-000). **Supersedes:** nothing.
**Format:** the eight questions of the DARPA Heilmeier Catechism, answered from register rows of status V; then a
technology readiness assessment per subsystem on the DoD scale; then the programme's exams. Every number carries
its register row (`#n`, `docs/MEASUREMENT_CONDITIONS.md`).

## 1. The catechism

### 1.1 What is the programme trying to do?

Measure, on one testbed and under declared conditions, what it costs and what it buys to root a connected vehicle's
identity in each of nine Ethereum identity standards, and whether the verification step of vehicle and roadside
messages fits the computational share of the safety budget when the chain is kept off the hot path. The statement
is Scope v3 (`docs/phase2/SCOPE_RECONCILIATION.md` section 2.1). It claims nothing about radio, real mobility,
public-network latency or fiat cost.

### 1.2 How is it done today, and what are the limits of current practice?

Deployed vehicle-to-everything security uses certificate-based public-key infrastructure: IEEE 1609.2 application
certificates in North America, ETSI TS 103 097 authorisation tickets in Europe, with revocation by certificate
revocation list and misbehaviour reporting (CAMP SCMS). The limits the testbed targets are three. Revocation
reaches a verifier only when a list reaches it. The credential model is closed to one trust hierarchy per region.
Published blockchain-identity comparisons for vehicles are rubric-based or single-standard; none measures nine
standards on one operation catalogue with exact gas (audit `docs/AUDIT_01_ORIGINAL_GOALS.md` section 4; the
literature review that positions this, chapter 2, is unwritten and is the programme's largest open risk, TDP-009
R-01).

### 1.3 What is new in the approach, and why will it work?

Three things, each with evidence already on the trunk.

1. **One operation catalogue over nine substrates, with the operation definitions declared.** The same seventeen
   lifecycle events and the same per-operation catalogue run on every standard; a substrate without a primitive is
   recorded as not applicable, never emulated (TDP-002 SYS-01). Creation gas spans 52,216 to 1,757,881, a factor of
   33.7 (#25); over the lifecycle the cheapest standard leads by between 1.20 and 5.52 times, not ten (#35). The
   ratio depends on the definition, and the register says which (#6).
2. **The chain off the hot path, with the price of freshness measured.** Warm verification of a safety message with a
   pre-issued credential takes 0.153 ms (#27); reading the key and revocation state from the chain at message time
   takes 9.654 ms against 0.253 ms for the in-process certificate baseline (#21). A verifier that re-checks every k
   messages honours a revoked key for at most k minus 1 further messages, measured as 0, 4 and 24 for k of 1, 5 and
   25 (#32), for vehicles and for roadside units (#46).
3. **An evidence line that a reviewer can re-run.** Every result of record carries a run stamp with a per-producer
   code scope, reaches its tracked path through a promote step that refuses dirty runs, and enters a chapter only
   through a register row of status V (DWG-005). Every guard has a probe in CI that shows it fires.

It works in the sense the register can show: the pre-registered verdicts fell as they fell, including two failures
(#33 "equal once cached" FAIL; #38 gas FAIL) and one ratio outside its band (#44, 1.226, not falsified).

### 1.4 Who cares? If successful, what difference does it make?

Three audiences, named with what each takes.

| Audience | What the result gives them |
|---|---|
| A fleet or road authority choosing a substrate | a cost table under declared operation definitions, a lifecycle total with the state each standard keeps for that price (#35, #49), and a dominance analysis that shows the hybrid dominated on six criteria (#36) |
| A V2X security engineer | the measured gap between credential verification and chain reads (#21, #27), the staleness bound a cached verifier buys (#32, #46), and the one-call probe refresh as the cheaper design (#37) |
| A standards body (MOBI, W3C DID working groups) | a MOBI-VID-inspired lifecycle realised on five backends with a fidelity score (#30, #33), a resolver that passes 335 of 336 generated external DID tests (#24), and a clause-level checklist of what the profile does not meet (`docs/MOBI_VID_CHECKLIST.md`) |

### 1.5 What are the risks and the payoffs?

Risks, ranked in TDP-009. The three that matter: the literature review is unwritten (R-01); the message testbed has
mock mobility, no radio and one host, so every latency figure is a computational share, not an end-to-end one (R-02);
and the thesis's own chapters still carry first-attempt words ("first", "throughput", "compliant") that the evidence
does not hold (R-03). The payoff is a defensible core of four cruxes with V evidence (C1, C2, C4, C5 in
`docs/thesis/CRUX_REGISTER.md`), and three papers whose evidence exists once WM-2 closes (P1, P2, P3 in the scope
reconciliation's paper map).

### 1.6 How much does it cost?

Not in currency: the project has no budget line and the register forbids a fiat figure without a source (#20 is an
estimate). In machine terms, one grand run of every suite takes the time recorded in the grand report, on one
four-core host; the metrics harness run of record is one command from a clean checkout (TDP-008). In effort, the
contribution record (`docs/figures/contribution_record.html`) counts commits per day across the branches, with the
statement that a commit count measures activity, not effort.

### 1.7 How long does it take?

The remaining Phase 1 steps are enumerated and ordered in `docs/PLAN_WM-2.md` section 4: C1 (in progress in the
parallel pass, report 21), C2, A3, A3b, A6, A5, A7, B3, D1, D2, G, F1, E1 and E2. Each is one pass. No date is
attached: the rule is one step per pass with a closing CI result, not a calendar.

### 1.8 What are the midterm and final exams?

| Exam | Pass condition | Where it is read |
|---|---|---|
| Every pass | grand run ALL OK; CI 8 of 8 green on the closing commit; every number in a changed document has a V row; every new guard shown to fire | the after-action report's closing section |
| WM-2 close (midterm) | the seven closing conditions of `docs/milestones/README.md`: plan status per item, milestone report, an audit by reviewers without the orchestrator's context, findings dispositioned, grand run and CI green, the next plan, a consolidated handback | `docs/milestones/WM-2_REPORT.md` (to be written) |
| Thesis freeze | Scope v3 adopted; H1 and H5 reported as split verdicts; every chapter number a V row; chapter 2 written | the scope reconciliation's decisions D-1 to D-15 |
| Defence (final) | the fifteen examiner questions of `docs/phase2/SCOPE_RECONCILIATION.md` section 5 each answered from a named file | the crux register: every crux "evidenced" or its gap stated as a limitation |

## 2. The full circle, stated once

The first brief of 2025-11-10 described the kernel as "read something like a credential or identity on- or off-chain
and then either do something on-chain or something off chain" (`docs/ORIGINAL_PROMPT_AND_DIRECTION.md` section A.1).
Eleven months of measurement narrowed every claim by subtraction. The Phase 2 focuses that then emerged, storage
locus (F1), the identity-dependent transaction (IDTx) and the interaction modes (F3), are that kernel restated with
evidence behind it: only 4 of 26 gates in the Phase 1 code are identity-dependent transactions under the strict
definition; event-held state is cheap to write and cannot be a dependency of any on-chain transaction (#49, #51);
six read and write modes are each a V row (`docs/phase2/PHASE2_PROGRAMME.md` section 1). The programme did not drift
and return. It measured its way back to its first question, and the question now has a definition, a taxonomy and a
price. The thesis states this in one paragraph and no more; the paper P5 carries the rest.

## 3. Technology readiness per subsystem

Scale: the DoD Technology Readiness Assessment Guidebook (February 2025), software definitions. TRL 3: analytical and
experimental critical function proof of concept. TRL 4: module or subsystem validation in a laboratory environment.
TRL 5: module or subsystem validation in a relevant environment. TRL 6: system or subsystem model or prototype
demonstration in a relevant end-to-end environment. A level is claimed only where the register holds the evidence; a
level is withheld where the environment condition is not met, whatever the code can do.

| Subsystem (plane) | TRL | Reason the level is met | Reason the next level is not |
|---|---|---|---|
| P2 Ledger: nine substrates and the MOBI profile behind one adapter | 4 | every substrate compiles, passes its suite and the strict revert harness (#28), and reproduces its gas byte for byte over 30 runs (#25) on the laboratory chain (M1) | no run on a public or permissioned network (N-11); the relevant environment for gas is any EVM network, but latency and fees do not transfer (scope reconciliation section 3.2) |
| P3 Credential: W3C VC layer, four-method resolver, MOBI VID I/II | 4 | 335 of 336 external DID tests (#24); 94.3 percent on the internal structural checker (#4); credentials signed off-chain verify with the primitive the EVM uses (chapter 4 section 4.1) | the resolver synthesised documents from the identifier until WM-2 C1 (in progress); one credential suite; 2 of 8 MOBI VID I MUSTs met (SC-14a) |
| P1 Messaging and P4 Trust: BSM and SPaT signing and verification, freshness, replay, revocation re-check | 3 | critical function proved: warm verify 0.153 ms (#27), 15 registered attacks rejected for their reasons in 30 of 30 runs (#45), staleness bounded at k minus 1 (#32, #46), D51 fail-open found and fixed | mock mobility, no radio, no channel, one host per run (SC-22); a laboratory environment for V2X would need a channel model at least; TRL 4 is withheld on that condition |
| P0 Mobility | 2 | MockMobility exists and is deterministic for a seed; the SUMO network and routes are committed | no SUMO run of record; the TraCI path falls back to mock when the binary is absent (N-4) |
| P5 Evidence: stamps, promote, register, checkers, generated documents | n/a (process) | the DoD scale rates technology, not procedure; the machinery is held instead by its probes in CI (TDP-002 EVD-01 to EVD-06) | — |

The system as a whole is at TRL 3: its lowest-rated plane on the message path bounds it. The statement "a research
testbed, not a prototype for fielding" follows from the table, not from modesty.

## 4. What the programme does not claim

- No "first". The claim is measured, same-testbed, domain-constrained, reproducible (SC-04).
- No throughput figure; the only one is register #39, status U (SC-05).
- No "compliant" or "conformant"; the internal score is structural and self-scored, the external suite is a test
  count (#4, #24; guide 1.2.2).
- No end-to-end latency; every latency figure is a computational share on a stated host (#27, #44 to #48).
- No k that "fits": zero staleness and 100 neighbours in half the interval were not achieved together on either
  measured host (#32, #37; D-12 withdrawn), though a third host reached 100 at k of 25 (#52).
- No fiat cost (#20, estimate).
