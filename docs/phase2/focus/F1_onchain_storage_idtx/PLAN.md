# F1 Plan — Experiments for On-Chain Storage and IDTx (Pre-Registration Draft)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, focus F1, plan). **Revised:** 2026-10-14 after the academic review
(`docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md`), findings AR-11, AR-12, AR-13, AR-41.
**State:** a **draft**, not locked; nothing has been run. It becomes a pre-registration only when committed under
`docs/phase2/prereg/` before the first run (Phase 2 principle 4; ROADMAP P2.3).
**Placement:** in the thesis this plan is one future-work paragraph (review §4.1). The experiments serve paper P5.
**Builds on:** `ANALYSIS.md` (the definition of §4.1); the prototype `phase2/idtx/` (`EXECUTION.md`).

## 1. Experiments
The predictions below are the orchestrator's reasoning from the EVM gas schedule, written before any measurement.

**Measure for E-F1-1 and E-F1-2.** Receipt `gasUsed` of the IDTx call minus that of a **control**: a new
`executePlain(action)` that emits the same event with no dependency, called with calldata of the same length.

**Conditions.** M1; solc 0.8.24, optimizer 200, viaIR. The compile target is `cancun`. The **execution hardfork**
reported by the node is recorded in the stamp (register §5.A notes that they differ).

| ID | Question | Design | Point prediction with band | Verdict rule | Kill criterion |
|---|---|---|---|---|---|
| **E-F1-1** | What does each dependency kind add, same transaction and next transaction? | the prototype; one dependency per call; Owner, Delegate, Commitment; N = 30 seeded calls per kind (gas is exact if inputs are seeded; otherwise a range, rule 1.1.10) | Owner 5,700–6,500 (one cold account, one cold slot); Delegate 6,000–7,000 (one cold account, one cold slot); Commitment 14,000–17,000 (two cold accounts, four cold slots); `createIntent` 150,000–200,000 (six to seven new slots); `fulfil` 35,000–50,000. "Dominated" is defined as: the intent's storage is more than 60 % of `createIntent` + `fulfil` | each kind PASS if inside its band; a miss is reported as a miss, with the opcode trace that explains it | none: the result is the cost table either way |
| **E-F1-2** | What does the storage locus change, holding the datum fixed? | one VIN-bound attribute stored at L0 (state), L1 (event), L3 (registered commitment), L4 (carried attestation); read with RPC calls and bytes at h ∈ {1, 10, 50}; whether an in-transaction dependency is possible (a test, not a measurement) | L1 cheapest to write and the only locus whose read grows in calls with h; L0 and L3 flat in calls; L4 adds a signature check (≈3,000 gas for ecrecover) per dependency | each prediction PASS or FAIL as stated | if L4 cannot be built without new issuer infrastructure, it is reported as not run |
| **E-F1-3** | How wide is the ordering window, and does the re-check close the TOCTOU gap? | the correctness half is already a test (tests 9 and 10). The measurement half runs under **interval mining** (block time 2 s): an agent reads, then submits; the dependency changes with probability p per block; variants with and without the on-chain re-check (the second is the `no_recheck_at_fulfil` mutant) | the re-check variant executes on a false dependency 0 times; without it, the count matches p times the window in blocks; the window is reported in blocks and seconds | PASS iff the re-check variant executes none; the window is reported, not judged | if interval mining cannot be scripted deterministically, report the correctness test only |
| **E-F1-4** | What does enumerating VINs cost an observer, given D64? | for one manufacturer code, model year and plant, enumerate the serial space (positions 12–17), hash each candidate as `_generate_vehicle_identity` does, and match against identities on chain | seconds on a laptop-class CPU for a 10⁶ space (a demonstration that D64 is exploitable, timed) | reported; feeds the D64 fix | none |

## 2. The D64 fix, designed before it is built (AR-13)
A non-derived identity removes the only duplicate-VIN check: the salted `vinHash` cannot catch a duplicate. The fix
is therefore pre-registered with a **uniqueness mechanism**. The candidate is a keyed blind index,
HMAC(registrar key, VIN), held by the registrar.

It states its trust: the registrar can test any candidate VIN, and nobody else can. The alternatives are a commitment
with a zero-knowledge proof of non-membership, or registration through an authority. They are written down and
compared before any code changes.

## 3. Steps, in order
| Step | Work | Gate | Depends on |
|---|---|---|---|
| F1-S1 | **done:** the prototype with 12 behaviour tests and 5 gate mutants, the mutants run in CI (`EXECUTION.md`) | tests pass; each mutant caught | — |
| F1-S2 | the author decides placement and the definition (P2-D1, P2-D8; review Q1–Q3) | decisions recorded | — |
| F1-S3 | design the D64 fix with its uniqueness mechanism (§2), then fix with a test that fails on the current derivation | design reviewed before code | WM-2 D1 |
| F1-S4 | add `executePlain`; lock this plan as a pre-registration | committed before any run | F1-S2 |
| F1-S5 | run E-F1-1 and E-F1-2 | clean runs promoted; register rows | F1-S4 |
| F1-S6 | run E-F1-3 and E-F1-4 | as above | F1-S5 |
| F1-S7 | write-up: paper P5 | academic review | F1-S5, F1-S6 |

## 4. Risks
| Risk | Mitigation |
|---|---|
| IDTx is judged a re-label of access control | the §4.1 definition excludes administration and authentication. The re-classified inventory shows only 4 of 26 Phase 1 instances are IDTx. Position against ERC-3643, ERC-4337 validation and oracles at their sources |
| The prototype is mistaken for the contribution | it is a measurement instrument; the contribution is the definition, taxonomy and evaluation dimensions |
| Gas varies with random keys (Phase 1 B1 issue) | seed inputs; report ranges where the input is the thing measured |
