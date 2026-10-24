# TDP-009 — Risk Register

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-15 (after-action report 20). **Revision:** B.
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
| R-04 | If the A3b re-runs (#21, #27, #32, #33, #37, #38) move a number on the trunk, then the chapter sentences that quote them are wrong until regenerated | 3 | 3 | **retired 2026-10-24** | run A3b after C1 and C2 per the plan order; old values kept as history; the stale-figure checker catches a stale quote (orchestrator) | A3b closed. Retired: the risk occurred; A3b moved #21, #27 and #44 and the old values are kept as history; the chapter fixes are WM-2 D1 (report 37 found 0.153 still in chapters 6 and 7), carried by R-03 |
| R-05 | If the parallel pass (report 21, C1) regenerates the snapshot without regenerating the TDP documents, then CI fails on the TDP checks | 4 | 1 | **retired 2026-10-24** | the handback gotcha names the three TDP generators beside the others; the failure is a regeneration, not a loss (both sessions) | first CI run after C1's close. Retired: C1 closed 2026-10-15 (`7ae268a`) |
| R-06 | If D54 stays open, then G4 is not met for attestations and the "43 of 43" sentence is read as covering authority | 3 | 3 | **retired 2026-10-24** | C2 restricts attestEvent; until then the threat model and TDP-002 SEC-05 state the gap (contracts engineer) | C2 closed with its regression test. Retired: D54 fixed 2026-10-17 (WM-2 C2); the threat model states G4 is met for attestations within that rule; #28 (198,694 execution gas) |
| R-07 | If the resolver re-run under C1 changes #4 or #24 downward, then H2's sentence must change | 2 | 3 | **retired 2026-10-24** | report as it falls; the register keeps history; the structural wording already limits the claim (SSI specialist) | C1's re-run recorded. Retired: the trigger fired with no change; #4 (94.3 percent) and #24 (335 of 336) are unchanged |
| R-08 | If no AI-use statement is added (N-23), then the attribution question (examiner question 15) is answered only by `PROVENANCE.md` | 3 | 4 | high | the author decides the statement's wording under the university's policy; nothing else can close it (author) | N-23 decided |
| R-09 | If the Infura credential on the onboarding lineage is not rotated (N-1), then a credential found in history remains live | 2 | 1 | low | rotate outside the repository; the finding is recorded (author) | rotation confirmed |
| R-10 | If the harness flag stays inert until A6 (D33), then a measured-code edit between runs is caught only by the whole-tree flag | 2 | 2 | low | `benchmarks/` is frozen until A6; the tree hash is checked against `meta.json` (orchestrator) | A6 closed: **closed 2026-10-23** (pass 33, `1f4ace0`) |
| R-11 | If the unsalted VIN hash in the testbed (D64) is read as the MOBI design, then G7 is overclaimed for the testbed path | 2 | 3 | moderate | TDP-002 SEC-06 names it; the MOBI registry's salted hash and AES-GCM path is the one the matrix row scores (security specialist) | D64 fixed or documented in chapter 4 |
| R-12 | If the thesis attaches post-hoc hypotheses to C3 and C7, then guide 1.2.1 is violated at the defence | 2 | 3 | moderate | treat them as pre-registered questions without hypotheses (D-5) (thesis methodologist) | chapter 1 section 1.3 revised |
| R-13 | If the demo count has no CI gate, then a demo silently dropped from the manifest is not noticed | 2 | 2 | low | plan G adds the gate; until then the grand report records the count each pass (CI engineer) | gate added |
| R-14 | If the layer-5 results (#56 to #62) are read as deployable, then the thesis claims a zero-knowledge identity that its own setup rules out: the Groth16 keys come from a single-party setup that is insecure for deployment (#57), and the proving time has N = 10 and is descriptive only | 2 | 4 | moderate | every mention of layer 5 states the insecure single-party setup and that it is research code; #57 is quoted as descriptive only (LATENCY_CHARTER) (ZKP specialist) | a multi-party setup, or chapter text checked against #57 |
| R-15 | If a chapter compares descriptive-only latencies (#26, #31, #39, #57) across runs or hosts, then the comparison claims more than the class allows | 3 | 3 | moderate | `docs/testing/LATENCY_CHARTER.md` classes each row; quote these rows as descriptive only, within one run (measurement methodologist) | WM-2 D1 chapter check |
| R-16 | If I1 (#44) is quoted as PASS, then the text contradicts the register: the ratio sits at the band's upper edge and lands on either side of it between runs (1.226 on the run of record, 1.197 on the A3b re-run) | 3 | 3 | moderate | quote "at the edge of the band, not falsified" with both values; the verdict is not re-rolled (thesis methodologist) | WM-2 D1 chapter check |
| R-17 | If D52 (the signed digest of `EthereumDIDRegistry` binds the registry address and nonce but not the chain id; severity M) stays as upstream behaviour, then a signed operation is replayable on another chain with the same registry address and signer nonce | 2 | 3 | moderate | documented, threat model G3 narrowed; a fix departs from the upstream bytecode (N-9), so it is an author decision (author) | author decision on D52 |
| R-18 | If D53 (`changeOwnerSigned` for identity 0x0 accepts a zero signature; severity L) stays open, then `owners[address(0)]` can be seized; impact limited to DID 0x0 | 1 | 2 | low | open under WM-2 C2 (require a non-zero signer) and the upstream-fidelity question N-9 (contracts engineer) | D53 fixed or decided |

## 3. Issues (certain, not probabilistic)

| ID | Issue | Consequence | Treatment |
|---|---|---|---|
| I-01 | D51 was found: a revoked key verified when the verifier's clock lagged the chain by more than 900 s | rows #32 and #37 were re-run on the fixed provider at A3b (the D51 block-time read); D63 is the residual | fixed in code at C0 with tests that fail on the old code; stated in TDP-002 SEC-04 and DWG-004 |
| I-02 | Two pins in `2_w3c-ssi-layer/requirements.txt` differ from the runs of record (web3, cryptography) | a reader installing from the file does not get the measured toolchain | TDP-008 section 4 states both; plan G makes the file complete; CI now pins its Python packages through `ci/requirements-ci.txt` |
| I-03 | 2 of 8 MOBI VID I MUSTs are met | "MOBI VID" reads as more than the profile is | every mention bounded to "MOBI-VID-inspired, checked against the public texts" (SC-14a); SC-17, SC-18, SC-20 recorded as deviations (D-11) |
| I-04 | The hybrid is dominated on all six harness criteria (#36) | H5 as first stated is not supported | split verdict (D-4); CVIN-Combined demoted to one measured candidate (D-14 list) |
| I-05 | The layer-5 Steward failed its pre-registered honest-service test: it holds adversary leakage to 3.0 bits or less on all runs but serves fewer than 90 percent of honest requests on 25 of 60 runs (minimum 70.0 percent), so Z-E6 FAILed (#61) | the Steward cannot be presented as a working defence at its stated service level; a global budget alone bounds leakage as well as the Steward does | report the FAIL as it fell (guide 1.2.1); the claim is the comparison, as a simulation result, not a deployable defence |
| I-06 | RSU-to-RSU messaging is out of scope (author decision D2, 2026-10-24, SC-24) | crux C3 has no RSU-to-RSU evidence | a single RSU-to-RSU hop uses the check #45 already verifies; relaying is future work shared with the V2V relay gap; stated in chapter 6 section 6.6.3 and crux C3 (`docs/design/RSU_TO_RSU_NOTE.md`) |

## 4. Review cadence

The register is re-rated at each work-milestone close and whenever a trigger in section 2 fires. A risk that
becomes an issue moves to section 3 with its treatment. A risk retired is kept with its retirement reason.

## Revision history

| Rev | Date | Change |
|---|---|---|
| B | 2026-10-24 | corrected from docs/tdp/REVIEW_2026-10.md (after-action report 38): R-04 to R-07 retired; R-14 to R-18 and I-05, I-06 added (layer 5 read as deployable, latency classes, I1 quoted as PASS, D52, D53, Z-E6 FAIL, RSU-to-RSU out of scope); I-01 and I-02 brought current |
