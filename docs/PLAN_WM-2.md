# Plan — Work Milestone WM-2: Results Pipeline of Record, Determinism, Carried Fixes, Thesis Readiness

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-10 at the close of work milestone WM-1 (after-action report 12, step W2), against
trunk `291bbca` plus pass 12. **Revised** after the WM-1 audit (§7).
**Supersedes:** `docs/PLAN_2026-10-09.md` as the current plan (its status table, §5, records what WM-1
did with each item). **Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md` (amended 2026-10-10),
`docs/TEAM_STRUCTURE.md` §4a (review protocol), `docs/milestones/README.md` (what closes a work milestone).
**Status:** the author said "accept defaults and continue"; WM-2 starts under the defaults in §5.

## 1. What WM-1 left, in one table
| Source | Open executable items | Open author decisions |
|---|---|---|
| Plan of 2026-10-09 (§5) | P3.2 `claims.yaml` (never done, never reported); P3.3 promote step and 9 unstamped files; P2b.1 TraCI path; P2b.2 network drawing | Q2 (SUMO), Q5 (M-A…M-L), Q6 (default branch), Q7 (review, narrowed) |
| TSR plan (`docs/planning/TESTING_SUITE_RESULTS_PLAN.md` §8) | phase 4 (P4-3 non-deterministic gas, P4-5 resolver), phase 5 (stamp, promote, `run_all`, `claims.yaml` cross-check), phase 6 (charters, pre-registration v2), phase 7 (review) | sheet AUTHOR decisions (N-5) |
| Deferred list (`docs/MILESTONE_NEXT.md`) | N-2, N-3, N-15, N-16 (design), N-18, N-19, N-20, N-21, N-22 | N-1, N-4, N-5…N-12, N-17 |
| Review-2 executable list (handback 2026-10-09 §4 item 4) | resolver reads the chain in `_resolve_ethr`; restrict `attestEvent` to owner and delegates; re-run #32 and #37 back to back on one host | — |
| Defect log | D33 rest (harness flag, = N-19) | §C policy calls (N-8) |
| Presentation | draft 2 per `docs/presentation/EXPANSION_PLAN_DRAFT2.md` (written in pass 12) | which audience first (supervisor, committee) |

## 2. Goal
At WM-2's close, every result of record is produced by a stamped producer through one entry point,
reproduces from a clean checkout within stated tolerance, and is mirrored in a machine-readable claim
list that CI cross-checks against the register; the gas cells that depend on random inputs are either
made deterministic or reported as ranges by rule; the review-2 carried fixes are in; and the thesis
chapters cite only V rows. No new experiment is started in WM-2 except re-runs forced by these fixes.

## 3. Workstreams, steps and gates
### A. Results pipeline of record (TSR phase 5). *Owner: reproducibility engineer; measurement methodologist.*
| Step | Work | Gate |
|---|---|---|
| A1 | **done (pass 13, report 13):** N-21: `check_stamps.py` accounts for every tracked result file (161; 0 uncovered); `--check-coverage` in CI | inventory lists every result directory; each new row classified |
| A2 | **done (pass 14, report 14):** one scope table read by both helpers, each producer's import closure resolved (`tools/run_identity/`); 14 of 20 producers converted (the harness at A6; four stamp producers at A3; `render_trace.py` writes derived figures); D49 fixed; `stamp.py --check` and the extended probe in CI. One stamp helper for JS and Python with **per-producer scope** (each producer names the code it imports: the security harness, `cv2x-testbed/scripts`, post-processing scripts; D49); the CI probe extended to it | probe fails on a broken helper and on an edit to an imported file |
| A3 | **done with a gap (pass 31, report 31):** the W3C checker, the gas-stats driver and the security-matrix producer call the shared stamp; runs of record at `96044b9`/`b8d5ba0` (code clean): #4 94.3 % unchanged, every security-matrix verdict unchanged, 30/30 gas runs identical; the scenario matrix promoted through A4 from a clean run (`036b6e4`). **Gap:** `sensitivity.json` (optimizer sweep, July) has no producer in the tree; classed, not re-run. N-20: the five *stamp producer* files (scopes registered in A2; the stamp call is added here, with the promote step, because `attackHarness.js` writes a tracked file on every `npx hardhat test`, D56): stamp the producer, re-run on a clean tree; any moved number re-registered with the old value as history. **Runs after C1 and C2**, which move W3C, gas and security results (audit P-F20) | each re-run stamped `dirty: false` with a live flag; moved cells listed |
| A3b | **done (pass 33, report 33, plan `docs/PLAN_WM-2_A3B.md`):** every family flagged "code changed since" re-run on the one trunk from clean commits: gas, sweep, scaling, infrastructure gas and pseudonym pool reproduce; #21, #26 D, #27, #44–#48, #32, #37 restated with history (I1 at the band edge; freshness knee set by t_local); the Exp. D driver fixed (replay cache) with a test. Not re-run, disclosed: `infrastructure_gas_run1.json` (pre-seeding history) and Exp. C (`scaling_verify.json` shares Exp. D's stamp; producer unchanged). Re-run the seven V rows whose producing code changed since their stamp (#21, #26 verify part, #27, #32, #33, #37, #38; D50); old values kept as history | stamp inventory column "code changed since" reads `no` for every V row |
| A4 | **done (pass 15, report 15):** `tools/run_identity/promote.py`, piloted on the security matrix (D56 in part); 13 refusal tests in CI; a clean run's dry-run shows all 54 cells identical to the committed matrix (not promoted: A3 promotes it after C2). Promote step, piloted on one producer: write to `runs/<id>/`, promote copies to the result path only if the stamp is clean | a dirty run refuses to promote (test) |
| A5 | **done (pass 34, report 34, plan `docs/PLAN_WM-2_A5.md`):** `docs/testing/claims.yaml` (62 ids, every V row's result files) and `check_claims.py --check` in CI and the pre-push check, with a probe (fails on an edited bold number, a V row without sources, an unknown row); nine stale claim cells rewritten to their result files with history (#21, #22, #26, #27, #31, #32, #37, #44, #48); 5 derived values declared with their arithmetic. Limits: only bold numbers in the claim cell are checked; #1–#3 rest on hand-assembled files. P3.2 `claims.yaml`: stable string ids for every register row, generated from or checked against the register; every V row names an existing source file; **the numbers quoted in each V row are checked against their result file** (audit T-F3: an edited #44 passed every guard) | CI fails on a V row without a source, a source without a row, or a quoted number that differs from the file |
| A6 | **done (pass 33, report 33):** `dirtyMeasured` from the shared helper (`1f4ace0`); harness re-run `2026-10-23T00-49-12Z_1f4ace0` and HTTP-RPC `2026-10-23T00-59-31Z_1f4ace0`, every gas cell identical, frontiers unchanged; #39 had already returned to V (2026-10-21). N-19 with the next harness run of record: switch `dirtyMeasured` to the shared helper (one line; scope already registered in A2), re-run the harness on a clean tree, re-stamp #29, #30, #34–#36; **re-run the HTTP-RPC condition on the merged contracts (#39, now U)** | measured-code hashes recorded; cells moved listed; #39 back to V or rewritten |
| A7 | **done (pass 35, report 35):** the grand runner keeps `py_layers.json`; 376 Python tests in the test register (L3 78, L4 19, SSI 279). N-15: the Python suites (L3, L4, SSI layer) in the TSR test register (audit P-F8) | every Python test has a TC entry |

### B. Determinism and statistics (TSR P4-3, phase 6). *Owner: measurement methodologist.*
| Step | Work | Gate |
|---|---|---|
| B1 | **done (pass 17, report 17):** incidental randomness seeded (L1 99/99 cells and demos 1,749/1,752 steps identical across seeded runs; 3 MOBI steps declared timestamp-dependent); I4 over declared seeds 1–30, reproducible; rule in guide 1.1.10; #47 re-stated. N-18 and the I4 range: seed the random inputs of the L1 mechanism tests and of `infrastructure_gas.js`; or, where a seeded input would hide a real cost, report min–max by rule | two runs byte-identical where seeded; rule written |
| B2 | **done (pass 18, report 18):** `docs/testing/GAS_CHARTER.md`, generated and CI-checked; 27 varying cells root-caused (the harness flag marks 14, execution only); 20 V gas rows classified; "address-dependent storage" not borne out. Charter for class G (gas): exact vs range, the 14 non-deterministic harness cells root-caused (calldata zero bytes, address-dependent storage) | every gas row says exact or range |
| B3 | **done (pass 35, report 35):** `docs/testing/LATENCY_CHARTER.md`, CI-checked; 14 rows classed, 4 relabelled descriptive only; the harness records no CPU (N-26). Charter for class L (latency): within-run comparison, host and library record, N ≥ 30 or "descriptive only" | every latency row conforms or is relabelled |

### C. Carried fixes from review-2, and the infrastructure verifier. *Owner: SSI/W3C specialist; contracts engineer; V2X specialist; security specialist.*
| Step | Work | Gate |
|---|---|---|
| C0 | **done (pass 16, report 16):** amendment A6 first; verifier v3 (D37–D41 fixed or documented, D42 gate) and the D51 provider fix, each with tests failing on the old code (26 v3 tests; 2 D51 tests); mutation script 39/39; I1–I3, I5 re-run at `7d08dce` in a clean worktree: I1 1.226, **outside band, not falsified** (as it fell); I2 PASS (15 checks); I3 PASS; register #44–#46, #48 re-stated with history. **Verifier v3** (WM-1 audit, D37–D42): bound message size and depth before canonicalising; binding claims mandatory for RSU and controller credentials and `rsu` required in SPaT; integer-only `refresh_every` and a CLI parser error; credential validity against the injected clock; DID method and chain validated; the I2 gate asserts the warm variants are warm. A dated pre-registration amendment first; then re-run I1–I3 as runs of record | each fix has a test that fails on the old code; the committed mutation script extended; I1–I3 re-run on a clean tree |
| C1 | **done (pass 21, report 21):** with a provider and the registry address, `_resolve_ethr` reads the ERC-1056 registry (owner, delegates, attributes, deactivation, chain-time validity); 11 new tests, 9 fail on the old code (7 on behaviour, 2 on its missing parameter); #4 and #24 unchanged (inputs resolve without a provider); chain-backed suite run and chain-path latency deferred (N-24). `_resolve_ethr` reads the chain (owner, attributes, `changed`) instead of the static document *Trunk lineage (merged 2026-10-22, Plan 5):* the clone lineage's H-R adds on-chain did:mobi and the full change-chain walk; the external suite scores 311/311 on that on-chain set (#24); the checker (#4) still scores offline documents. | external DID suite re-run (#24); checker (#4); moved numbers re-registered |
| C2 | **done (pass 22, report 22):** the MOBI registry stores delegations (`validDelegate`); `attestEvent` requires the owner or a `veriKey` delegate, once per event (D54 fixed); 4 regression tests, 3 fail on the old code; producers re-run, only MOBI cells move; testbed copies synced and recompiled (CI requires them byte-identical; N-25 opened and closed). `attestEvent` restricted to the vehicle's owner and delegates (review-2 K-4 follow-up) *Trunk lineage (merged 2026-10-22, Plan 5):* the clone lineage's H-A (OWNER-role owner check) is superseded by this design (`docs/LINEAGE_RELATION_2026-10-22.md` §3). | regression test fails on the old code; gas re-run of record for the moved cells |
| C3 | **done (pass 19, report 19):** both rows' configurations at their own code, one host, two replicates in opposite order; the host, not the code, explains their difference (#52); #32 and #37 carry a note. #32 and #37 re-run back to back on one host *Trunk lineage (merged 2026-10-22, Plan 5):* the clone lineage's same-host comparison of both refresh modes (#55, 12 replicates in alternating blocks) corroborates the host explanation. | the host-dependence note in C4 replaced by a measured comparison |

### D. Thesis readiness. *Owner: thesis methodology specialist.*
| Step | Work | Gate |
|---|---|---|
| D1 | Chapters 1, 4, 6, 7 checked against the register and the crux register; C3 and C8 sentences written where the cruxes say they are missing | every number a V row; stale check clean |
| D2 | **note written (pass 37, report 37):** `docs/design/RSU_TO_RSU_NOTE.md`; recommendation D2-a (scope out); waits on the author's D2 | author decides build or scope out |

### E. Review. *Owner: orchestrator; reviewers per `docs/TEAM_STRUCTURE.md` §4a.*
| Step | Work | Gate |
|---|---|---|
| E1 | N-22: a review whose briefs are written outside the session (the author, or a separate session given only `docs/milestones/` and this plan) | findings register |
| E2 | WM-2 close audit as for WM-1 | `docs/milestones/README.md` closing conditions |

### F. Presentation. *Owner: visualisation engineer; thesis methodologist.*
| Step | Work | Gate |
|---|---|---|
| F1 | Draft 2 of the presentation report per its expansion plan | numbers checked against the register by script |
| F2 | A slide deck derived from draft 2, if the author wants one | — |

### G. Hygiene and reproducibility (WM-1 audit).
N-2 (`npm ci` without SSH) and N-3 (unused `goerli` entries), each with its CI evidence. Also: make
`2_w3c-ssi-layer/requirements.txt` installable and complete (T-F7); pin OpenZeppelin identically in both Node
projects (T-F6); pin matplotlib and Pillow for the figures (T-F15); a demo-count gate in CI (rest of D47); compare
steps for the run-only CI jobs or label them run-only (T-F12); scan non-Markdown tracked text for superseded
figures (T-F16); record load average in environment headers (T-F8).

## 4. Order and dependencies
A1 → A2 → A4 → C0 → B1 → B2 → C3 → C1 → C2 → A3 → A3b → A6 → A5 → A7 → B3 → D1 → D2 → G → F1 → E1/E2.
Revised after the WM-1 audit (P-F20): the promote step (A4) comes before the re-runs it gates; the stamped
re-runs (A3, A3b) and the harness run of record (A6) come after the fixes that would move them (C0, C1, C2);
the claim cross-check (A5) comes after the numbers settle. P2b.1/P2b.2 (TraCI path, network drawing,
inspector) are **out of WM-2**: they need real mobility (N-4).

## 5. Author decisions (defaults taken; overturn any)
| # | Decision | Default |
|---|---|---|
| W2-a | Start WM-2 now under these defaults | yes ("accept defaults and continue") |
| W2-b | C1 and C2 change behaviour the thesis measures; re-run the affected results of record | yes, old values kept as history |
| W2-c | B1: seed inputs (exact gas) or report ranges | seed where the input is incidental; range where it is the thing measured |
| W2-d | Everything in §1's "author decisions" column | unchanged defaults (`docs/MILESTONE_NEXT.md`) |

## 6. What WM-2 does not do
No SUMO install (N-4), no Sepolia run (N-11), no new pre-registered experiment, no change to the
nine-standard contract set beyond C2, no chapter prose beyond the sentences D1 finds missing.

## 7. Revisions
- 2026-10-23 (pass 35) — B3 and A7 done (report 35). Next: D1 (needs D-1), D2, and the read-only chapter audit.
- 2026-10-23 (pass 34) — A5 done (report 34). Next: A7 (Python suites in the test register), B3, D1.
- 2026-10-23 (pass 33) — on the one trunk (Plan 5): A3b and A6 done (report 33). Next: A5 (claims.yaml with number checks), then A7, B3, D1.
- 2026-10-22 (pass 31) — C3, C1 (gap: checker offline) and C2 (D54 open) recognised as done by the clone lineage merged in PR #3; A6 largely done by the merge re-runs (harness run `2026-10-21T03-28-59Z_a9e2a28`, #39 re-run `2026-10-21T09-02-58Z_bd55af2`); A3b partly (#33). Next: A3.
- 2026-10-22 (pass 31, later) — A3 done with a gap (sensitivity.json has no producer). Next: A3b (15 result families flagged "code changed since" in `STAMP_INVENTORY.md`).
- 2026-10-10 (initial) — written before the WM-1 audit.
- 2026-10-17 (pass 22) — C2 done (report 22). Next: A3, after the hand-off and the check by the other model.
- 2026-10-15 (pass 21) — C1 done (report 21; report 20 is the parallel TDP pass). Next: C2.
- 2026-10-15 (pass 19) — C3 done (report 19). Next: C1.
- 2026-10-15 (pass 18) — B2 done (report 18). Next: C3.
- 2026-10-14 (pass 17) — B1 done (report 17). Next: B2.
- 2026-10-14 (pass 16) — C0 done (report 16). Phase 2 focus work alongside (`docs/phase2/PHASE2_PROGRAMME.md`). Next: B1.
- 2026-10-14 (pass 15) — A4 done. The security-matrix producer is `securityScenarios.test.js` (A2 had registered `attackHarness.js`, which left the scenario file out of scope; corrected). Phase 2 opened beside WM-2 (`docs/phase2/`). Source: after-action report 15.
- 2026-10-12 (pass 14) — A2 done; A3 and A6 notes updated (A3 adds the stamp calls the five producers still lack; A6's harness switch is one line). Source: after-action report 14.
- 2026-10-10 (after the WM-1 audit) — added C0 (verifier v3), A3b (seven re-runs), A7 (N-15), A5's number cross-check, A6's HTTP re-run, G's reproducibility items; reordered §4; P2b items marked out of WM-2. Source: after-action report 12 §4.
