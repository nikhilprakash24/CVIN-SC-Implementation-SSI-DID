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
| Presentation | draft 2 per `docs/presentation/EXPANSION_PLAN_DRAFT2.md` | which audience first (supervisor, committee) |

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
| A2 | A Python stamp helper (`docs/testing/stamp.py` or `cv2x-testbed/lib/run_stamp.py`) with the same fields and pathspec rule as `run_stamp.js`; the CI probe extended to it | probe fails on a broken helper |
| A3 | N-20: the five *stamp producer* files: stamp the producer, re-run on a clean tree; any moved number re-registered with the old value as history | each re-run stamped `dirty: false` with a live flag; moved cells listed |
| A4 | Promote step, piloted on one producer: write to `runs/<id>/`, promote copies to the result path only if the stamp is clean | a dirty run refuses to promote (test) |
| A5 | P3.2 `claims.yaml`: stable string ids for every register row, generated from or checked against the register; every V row names an existing source file | CI fails on a V row without a source or a source without a row |
| A6 | N-19 with the next harness run of record: root-anchor `dirtyMeasured`, re-run the harness on a clean tree, re-stamp #34–#36 | measured-code hashes recorded; cells moved listed |

### B. Determinism and statistics (TSR P4-3, phase 6). *Owner: measurement methodologist.*
| Step | Work | Gate |
|---|---|---|
| B1 | N-18 and the I4 range: seed the random inputs of the L1 mechanism tests and of `infrastructure_gas.js`; or, where a seeded input would hide a real cost, report min–max by rule | two runs byte-identical where seeded; rule written |
| B2 | Charter for class G (gas): exact vs range, the 14 non-deterministic harness cells root-caused (calldata zero bytes, address-dependent storage) | every gas row says exact or range |
| B3 | Charter for class L (latency): within-run comparison, host and library record, N ≥ 30 or "descriptive only" | every latency row conforms or is relabelled |

### C. Carried fixes from review-2. *Owner: SSI/W3C specialist; contracts engineer; V2X specialist.*
| Step | Work | Gate |
|---|---|---|
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

### G. Hygiene.
N-2 (`npm ci` without SSH) and N-3 (unused `goerli` entries), each with its CI evidence.

## 4. Order and dependencies
A1 → A2 → A3 → A5 → B1 → B2 → C3 → C1 → C2 → A6 (the harness re-run comes after C2, which moves gas)
→ B3 → D1 → D2 → F1 → E1/E2. A4 can run beside A3. G any time.

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
- 2026-10-10 (initial) — written before the WM-1 audit; to be revised with the audit's carried items.
