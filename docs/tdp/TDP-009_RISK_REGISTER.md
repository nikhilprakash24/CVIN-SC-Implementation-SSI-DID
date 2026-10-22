# TDP-009 — Risk Register

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-15 (after-action report 20). **Revision:** A.
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`; `docs/tdp/README.md` (TDP-000). **Supersedes:** nothing; it ranks what
`docs/thesis/CRUX_REGISTER.md` (gaps), `docs/MILESTONE_NEXT.md` (deferred items) and `docs/DEFECT_LOG.md` (open
defects) already list. The ratings are the orchestrator's defaults; the author overturns any.
**Format:** the DoD Risk, Issue and Opportunity Management Guide: likelihood 1 to 5, consequence 1 to 5, level from
the five-by-five matrix (low, moderate, high). An issue is a risk whose occurrence is certain; issues are listed
separately. Consequence is rated on the programme's performance axis (the defence) since there is no cost or
schedule baseline to rate against.

## 1. Scales, as applied here

| Likelihood | Meaning here | Consequence | Meaning here |
|---|---|---|---|
| 1 | not expected before the defence | 1 | a sentence in a limitation |
| 2 | possible | 2 | a section rewritten |
| 3 | likely | 3 | a chapter claim narrowed or a row re-run |
| 4 | highly likely | 4 | a crux left without evidence |
| 5 | near certain | 5 | the defence cannot answer an expected question |

Level: high when likelihood x consequence places the risk in the red cells of the guide's matrix (consequence 4 or 5
with likelihood 3 or more; or consequence 3 with likelihood 5), moderate in the yellow band, low in the green.

## 2. Risks

| ID | Risk (if ... then ...) | L | C | Level | Mitigation (owner) | Trigger to re-rate |
|---|---|---|---|---|---|---|
| R-01 | If chapter 2 stays unwritten, then examiner question 1 (what is new against rubric-based DID evaluations and existing SSI V2V systems) has no answer in the text and the IDTx positioning rests on an unchecked list | 4 | 5 | high | write chapter 2 next, with the IDTx positioning table read at source (scope reconciliation D-15; chat-workspace brief for the literature work) (author) | a drafted chapter 2 with every entry cited |
| R-02 | If the message-path evidence stays on mock mobility with no channel, then the real-time claim is read as end-to-end when it is a computational share | 3 | 4 | high | every figure caption and TDP-002 RTV rows state the share and the host; chapter 7 states SC-22; no "end to end" wording (D-14 cut list) (orchestrator, thesis methodologist) | a SUMO run of record (N-4), or the defence passing without one |
| R-03 | If chapters 1 and 7 keep "first", "throughput", "compliant" and "all five supported", then the evidence contradicts the text at the defence | 4 | 4 | high | adopt Scope v3 and the cut list of the scope reconciliation section 2.5; D1 of WM-2 checks every chapter against the register (author decision D-1 to D-4) | chapters 1 and 7 regenerated against the register with the stale check clean |
| R-04 | If the A3b re-runs (#21, #27, #32, #33, #37, #38) move a number on the trunk, then the chapter sentences that quote them are wrong until regenerated | 3 | 3 | moderate | run A3b after C1 and C2 per the plan order; old values kept as history; the stale-figure checker catches a stale quote (orchestrator) | A3b closed |
| R-05 | If the parallel pass (report 21, C1) regenerates the snapshot without regenerating the TDP documents, then CI fails on the TDP checks | 4 | 1 | low | the handback gotcha names the three TDP generators beside the others; the failure is a regeneration, not a loss (both sessions) | first CI run after C1's close |
| R-06 | If D54 stays open, then G4 is not met for attestations and the "43 of 43" sentence is read as covering authority | 3 | 3 | moderate | C2 restricts attestEvent; until then the threat model and TDP-002 SEC-05 state the gap (contracts engineer) | C2 closed with its regression test |
| R-07 | If the resolver re-run under C1 changes #4 or #24 downward, then H2's sentence must change | 2 | 3 | moderate | report as it falls; the register keeps history; the structural wording already limits the claim (SSI specialist) | C1's re-run recorded |
| R-08 | If no AI-use statement is added (N-23), then the attribution question (examiner question 15) is answered only by `PROVENANCE.md` | 3 | 4 | high | the author decides the statement's wording under the university's policy; nothing else can close it (author) | N-23 decided |
| R-09 | If the Infura credential on the onboarding lineage is not rotated (N-1), then a credential found in history remains live | 2 | 1 | low | rotate outside the repository; the finding is recorded (author) | rotation confirmed |
| R-10 | If the harness flag stays inert until A6 (D33), then a measured-code edit between runs is caught only by the whole-tree flag | 2 | 2 | low | `benchmarks/` is frozen until A6; the tree hash is checked against `meta.json` (orchestrator) | A6 closed |
| R-11 | If the unsalted VIN hash in the testbed (D64) is read as the MOBI design, then G7 is overclaimed for the testbed path | 2 | 3 | moderate | TDP-002 SEC-06 names it; the MOBI registry's salted hash and AES-GCM path is the one the matrix row scores (security specialist) | D64 fixed or documented in chapter 4 |
| R-12 | If the thesis attaches post-hoc hypotheses to C3 and C7, then guide 1.2.1 is violated at the defence | 2 | 3 | moderate | treat them as pre-registered questions without hypotheses (D-5) (thesis methodologist) | chapter 1 section 1.3 revised |
| R-13 | If the demo count has no CI gate, then a demo silently dropped from the manifest is not noticed | 2 | 2 | low | plan G adds the gate; until then the grand report records the count each pass (CI engineer) | gate added |

## 3. Issues (certain, not probabilistic)

| ID | Issue | Consequence | Treatment |
|---|---|---|---|
| I-01 | D51 was found: a revoked key verified when the verifier's clock lagged the chain by more than 900 s | rows #32 and #37 hold under the old clock assumption until A3b | fixed in code at C0 with tests that fail on the old code; stated in TDP-002 SEC-04 and DWG-004 |
| I-02 | Two pins in `2_w3c-ssi-layer/requirements.txt` differ from the runs of record (web3, cryptography) | a reader installing from the file does not get the measured toolchain | TDP-008 section 4 states both; plan G makes the file complete |
| I-03 | 2 of 8 MOBI VID I MUSTs are met | "MOBI VID" reads as more than the profile is | every mention bounded to "MOBI-VID-inspired, checked against the public texts" (SC-14a); SC-17, SC-18, SC-20 recorded as deviations (D-11) |
| I-04 | The hybrid is dominated on all six harness criteria (#36) | H5 as first stated is not supported | split verdict (D-4); CVIN-Combined demoted to one measured candidate (D-14 list) |

## 4. Review cadence

The register is re-rated at each work-milestone close and whenever a trigger in section 2 fires. A risk that
becomes an issue moves to section 3 with its treatment. A risk retired is kept with its retirement reason.
