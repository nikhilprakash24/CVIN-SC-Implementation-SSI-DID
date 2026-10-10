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
| A1 | N-21: `check_stamps.py` globs widened (metrics-rpc, scaling repeats, conformance reports, grand report JSON) | inventory lists every result directory; each new row classified |
| A2 | One stamp helper for JS and Python with **per-producer scope** (each producer names the code it imports: the security harness, `cv2x-testbed/scripts`, post-processing scripts; D49); the CI probe extended to it | probe fails on a broken helper and on an edit to an imported file |
| A3 | N-20: the five *stamp producer* files: stamp the producer, re-run on a clean tree; any moved number re-registered with the old value as history. **Runs after C1 and C2**, which move W3C, gas and security results (audit P-F20) | each re-run stamped `dirty: false` with a live flag; moved cells listed |
| A3b | Re-run the seven V rows whose producing code changed since their stamp (#21, #26 verify part, #27, #32, #33, #37, #38; D50); old values kept as history | stamp inventory column "code changed since" reads `no` for every V row |
| A4 | Promote step, piloted on one producer: write to `runs/<id>/`, promote copies to the result path only if the stamp is clean | a dirty run refuses to promote (test) |
| A5 | P3.2 `claims.yaml`: stable string ids for every register row, generated from or checked against the register; every V row names an existing source file; **the numbers quoted in each V row are checked against their result file** (audit T-F3: an edited #44 passed every guard) | CI fails on a V row without a source, a source without a row, or a quoted number that differs from the file |
| A6 | N-19 with the next harness run of record: root-anchor `dirtyMeasured`, re-run the harness on a clean tree, re-stamp #29, #30, #34–#36; **re-run the HTTP-RPC condition on the merged contracts (#39, now U)** | measured-code hashes recorded; cells moved listed; #39 back to V or rewritten |
| A7 | N-15: the Python suites (L3, L4, SSI layer) in the TSR test register (audit P-F8) | every Python test has a TC entry |

### B. Determinism and statistics (TSR P4-3, phase 6). *Owner: measurement methodologist.*
| Step | Work | Gate |
|---|---|---|
| B1 | N-18 and the I4 range: seed the random inputs of the L1 mechanism tests and of `infrastructure_gas.js`; or, where a seeded input would hide a real cost, report min–max by rule | two runs byte-identical where seeded; rule written |
| B2 | Charter for class G (gas): exact vs range, the 14 non-deterministic harness cells root-caused (calldata zero bytes, address-dependent storage) | every gas row says exact or range |
| B3 | Charter for class L (latency): within-run comparison, host and library record, N ≥ 30 or "descriptive only" | every latency row conforms or is relabelled |

### C. Carried fixes from review-2, and the infrastructure verifier. *Owner: SSI/W3C specialist; contracts engineer; V2X specialist; security specialist.*
| Step | Work | Gate |
|---|---|---|
| C0 | **Verifier v3** (WM-1 audit, D37–D42): bound message size and depth before canonicalising; binding claims mandatory for RSU and controller credentials and `rsu` required in SPaT; integer-only `refresh_every` and a CLI parser error; credential validity against the injected clock; DID method and chain validated; the I2 gate asserts the warm variants are warm. A dated pre-registration amendment first; then re-run I1–I3 as runs of record | each fix has a test that fails on the old code; the committed mutation script extended; I1–I3 re-run on a clean tree |
| C1 | `_resolve_ethr` reads the chain (owner, attributes, `changed`) instead of the static document | external DID suite re-run (#24); checker (#4); moved numbers re-registered |
| C2 | `attestEvent` restricted to the vehicle's owner and delegates (review-2 K-4 follow-up) | regression test fails on the old code; gas re-run of record for the moved cells |
| C3 | #32 and #37 re-run back to back on one host | the host-dependence note in C4 replaced by a measured comparison |

### D. Thesis readiness. *Owner: thesis methodology specialist.*
| Step | Work | Gate |
|---|---|---|
| D1 | Chapters 1, 4, 6, 7 checked against the register and the crux register; C3 and C8 sentences written where the cruxes say they are missing | every number a V row; stale check clean |
| D2 | N-16 RSU-to-RSU messaging: design note only (what it adds to C3; whether the thesis needs it) | author decides build or scope out |

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
- 2026-10-10 (initial) — written before the WM-1 audit.
- 2026-10-10 (after the WM-1 audit) — added C0 (verifier v3), A3b (seven re-runs), A7 (N-15), A5's number cross-check, A6's HTTP re-run, G's reproducibility items; reordered §4; P2b items marked out of WM-2. Source: after-action report 12 §4.
