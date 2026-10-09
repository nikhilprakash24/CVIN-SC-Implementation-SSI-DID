# After-Action Report 11 — Adversarial Review of Passes 9–10, and the Run-Identity Fixes

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-09, before any change; updated per step; closed at the end
**Trunk at start:** `0ba7c6c`, clean, CI green (8/8 on `94c2b7c`)
**Brief:** "accept F-C with defaults and continue to the next executable." F-C (the I3 run of record
with a false whole-tree flag) is accepted. Next executable per the handback §7: (1) the adversarial
review of passes 9–10 (N-10, Q7); (2) N-14, then the TSR phases; (3) review-2's executable list.

## 1. How "a different configuration" is met here, and how it is not
The plan reserved the adversarial review for "a different assistant configuration". This pass runs it
as read-only reviewer agents on a **different model** from the orchestrator's, each with a fresh
context, a fixed scope and a frozen checkout of `0ba7c6c` (a separate worktree, so the orchestrator's
edits cannot change what they read). That gives different priors and no shared working memory. It
does not give full independence: the orchestrator chose the scopes and briefs, and decides which
findings to accept. To limit that, **every finding is logged with its disposition** (confirmed,
rejected with the reason, or deferred), none is dropped, and each confirmed finding is re-checked
by the orchestrator before it is fixed. The session-level review by a different configuration that
the author may run later (N-10) remains open; this pass narrows it, it does not close it.

## 2. Plan
| Step | Work | Gate |
|---|---|---|
| R0 | Open this report; record F-C accepted; found before the review: `check_stamps.py` reports `tree_clean` under "dirty" without negating it (the pass-9 stamp inventory is inverted for every Python header) | committed first |
| R1 | Adversarial review, three reviewers in parallel on the frozen checkout: (a) claims and measurement (register #44–#48 and pass-9 changes, chapter 5 §5.4.1, pre-registration adherence, statistics); (b) code and security (infrastructure layer, harness flags, drivers, gas script, renderer, L3 tests); (c) generators, CI and process (dashboard, registers, checkers, run stamps, reports' claims about them) | each reviewer returns findings with file:line, evidence and severity |
| R2 | Disposition of every finding; fix the confirmed ones in scope; defects to `docs/DEFECT_LOG.md` where they are defects of the system under test; the rest to `docs/MILESTONE_NEXT.md` | each fix re-verified by the orchestrator; no finding without a disposition |
| R3 | N-14: a producing-code-scoped clean flag in the Python environment header (`code_clean`), kept beside `tree_clean`; `check_stamps.py` negation fixed and taught `code_clean` | inventory regenerated and read row by row against the files |
| R4 | TSR phase 5, first item: classify the result files without a complete stamp — re-runnable producers to be stamped, history files exempted with a reason | inventory states a class for every MISSING row |
| R5 | Grand run, CI, dashboard if a shown number moved, handback addendum, meta commentary, manifest, close | ALL OK; CI green |

## 3. Execution log
- 2026-10-09 — report opened. F-C accepted by the author.
- **R0 (before the review returned).** `check_stamps.py` showed `tree_clean` under "dirty" un-negated.
  Following that thread: the producing-code flags of `run_stamp.js` and of the harness header could
  never fire (relative pathspecs from a subdirectory) — probed with an untracked file in `contracts/`
  and `sumo/`. Fixed in R3 (`b1d3f72`).
- **R1.** Three reviewers on the frozen checkout (claims; code and security; tooling and process).
  33 findings, register §4. The orchestrator re-ran the security PoC (cross-intersection SPaT and
  replay both accepted) before acting on it.
- **R3 (`b1d3f72`).** Pathspecs root-anchored (`:(top)`), results excluded; `code_clean` beside
  `tree_clean`; inventory with both polarities, inert marks and recorded hand checks (four pass-9 JS
  producers: tree clean at 02:27:39, outputs-only commit `d54178e`; I4: producing paths unchanged
  since `1e690c3`, newest producer modified 03:47 before the 03:55 run); CI probe
  `docs/testing/probe_run_identity.sh`, shown to fail on the old code. No result number moved.
- **R2, verifier (`98e64e4` amendment first, then `f1f9e37`).** Binding, replay, warm expiry,
  distinct reasons; 13 I2 checks; 31 tests, 26/26 mutants killed; no-change gate holds. A two-seed
  dry run (disclosed, not a result) showed every check rejected for its expected reason and an I1
  ratio near 1.1, inside the band — the hardened SPaT path does work the BSM path does not, the bias
  A4 predicted. The verifier was not optimised after seeing it.
- **Registered re-run** started at `f1f9e37` in a separate worktree (I1 alone on the host; then I3,
  the two traces, I4 twice).

## 4. Findings register (every reviewer finding, with its disposition)
Reviewers ran on a different model from the orchestrator's, on the frozen checkout of `0ba7c6c`.
Severity is the reviewer's. **33 findings: 32 confirmed, 1 accepted as a judgement (A11); none
rejected.** Two (C1, C2) the orchestrator had found itself while the review ran.

| # | Reviewer | Finding (reviewer's severity in the full report) | Disposition | Commit |
|---|---|---|---|---|
| A1 | claims | F-A says the cost of re-checking is visible in I3; I3 counts messages and times nothing; the in-process re-check is ~free, a chain read is not (#37, #40) | **Confirmed.** Amendment A1; scope sentence in #44, #46, §5.4.1, C3; correction note in AAR-10 | `98e64e4`, docs |
| A2 | claims | Departures (F-A, I4 operation, I5 statistic) recorded only in AAR-10 and the register, not as dated amendments | **Confirmed.** Amendments A1–A3, marked post hoc | `98e64e4` |
| A3 | claims | I5 computed as a sum of four per-run medians, not the pre-registered per-message sum; it is not a path latency (the SPaT does not consume the controller update) | **Confirmed.** Amendment A3; #48 and §5.4.1 reworded; the driver states the definition | `98e64e4`, `f1f9e37` |
| A4 | claims | "(k − 1) × 0.1 s" and "2.4 s" read a message count as a time; the cache never expires | **Confirmed.** Reworded in §5.4.1, meta commentary, N-17 | docs |
| A5 | claims | "The bound is reached" holds for the maximum, not per run (k=25: 6 of 30); I3 checks the cadence, not a security property; "4–14 vehicles" includes cold receivers | **Confirmed.** Driver now records runs reaching the bound and receivers cached at revocation; #46 reworded | `f1f9e37`, docs |
| A6 | claims | Absolute-value offset attributed to `cryptography` 41 vs 49; the SSI path does not use `cryptography`, and the host differs (kernel fc-v64 vs fc-v80) | **Confirmed** (orchestrator: platform strings; `eth-account` requirements). Reworded: host and library set differ, cause not isolated | docs |
| A7 | claims | Overclaims: "clean tree" for both files; "costs exactly"; "secures"; "no new mechanism"; "free at this resolution" (payload size confounded) | **Confirmed.** Reworded to what was measured | docs |
| A8 | claims | I2 counted any rejection; 30/30 is a deterministic check repeated | **Confirmed** (same as B3). Fixed by A4; wording says repeated deterministic check | `f1f9e37` |
| A9 | claims | One bootstrap generator shared across quantities | **Confirmed.** One generator per quantity (A4) | `f1f9e37` |
| A10 | claims | I4 a single run; I4 overlapped I3; I1 ran while the renderer was being written | **Confirmed.** Re-run: I1 alone on the host, I4 twice | run log |
| A11 | claims | #46 is weak evidence for C4 (vehicle keys, latency) | **Accepted.** Removed from C4's evidence; named in its gaps | docs |
| B1 | code | Message fields not bound to the credential: a valid RSU can sign SPaT for another intersection | **Confirmed** (PoC re-run by the orchestrator: accepted). Binding to `intersectionId`/`stationId` on both paths; I2 check (h) | `f1f9e37` |
| B2 | code | Replay inside the window accepted (same and other receiver), though the design promised a replay check | **Confirmed** (PoC). Per-receiver replay cache; I2 check (i). Remaining, disclosed: a fresh message relayed to a receiver that never saw it inside 1 s is not detectable by a replay cache (same limit as V2V) | `f1f9e37` |
| B3 | code | All attacks against cold receivers; reasons not recorded | **Confirmed.** 13 checks incl. 3 warm; reasons in results and trace; verdict requires the expected reason | `f1f9e37` |
| B4 | code | Warm path never re-checks credential expiry | **Confirmed.** Warm expiry check. The new test then caught that the first fix read `expirationDate` while the VC layer writes `validUntil` | `f1f9e37` |
| B5 | code | 4 of 17 mutants survive (warm permitted, future bound, subject mismatch, missing credential); cadence untested | **Confirmed.** 31 tests; 26 of 26 mutants killed (orchestrator re-ran an extended mutation set) | `f1f9e37` |
| B6 | code | Unhashable `sender_did` raises outside the try | **Confirmed.** Rejection with `error:` | `f1f9e37` |
| B7 | code | `--refresh-k 0` silently meant infinity | **Confirmed.** Rejected by the CLI | `f1f9e37` |
| B8 | code | RSU label x-position from a leftover loop variable | **Confirmed.** Uses the last step's time | `f1f9e37` |
| B9 | code | Rejected BSM links drawn grey like accepted ones | **Confirmed.** Red | `f1f9e37` |
| B10 | code | Re-check counter counts presented (incl. forged) messages | **Confirmed, no code change.** Only makes the re-check sooner; documented in the module | `f1f9e37` |
| B11 | code | I4 key-anchor gas includes first-write costs; #47 said "dirty false" | **Confirmed.** Disclosed in #47; flag fixed (R3) | docs, `b1d3f72` |
| C1 | tooling | `run_stamp.js` scoped `dirty` can never be true (relative pathspecs from `1_blockchain-identity`) | **Confirmed; found independently by the orchestrator in R3 before this report arrived.** Fixed; CI probe; hand checks recorded. Same fault in `benchmarks/run.js` `dirtyMeasured` confirmed → N-19 | `b1d3f72` |
| C2 | tooling | `check_stamps.py` showed `tree_clean` under "dirty" un-negated; counts a dirty stamp as stamped; globs miss some result sets; report-only | **Confirmed** (found in R0). Two columns with correct polarity, inert and hand-check marks, classes. Wider globs → N-21; stays report-only by design, with the CI probe guarding the flags | `b1d3f72` |
| C3 | tooling | Stale-figure history markers are substrings ("old " in "cold "), masking live stale figures (`INVENTORY.md`) | **Confirmed** (to be re-verified on the fix). Word-boundary markers; masked lines fixed | R2 tooling |
| C4 | tooling | Formatting variants (`1404108`, `0.165ms`, `93.2%`) and unscanned files (`3_cv2x-testbed/README.md`, `MASTER_UPDATE.md`, `PROJECT_SUMMARY.md`) pass | **Confirmed.** Number normalisation; scope = all tracked Markdown minus a named history list | R2 tooling |
| C5 | tooling | `--check` does not cover `results_dashboard.html`; reports said "CI fails otherwise" | **Confirmed.** `--check` renders the page in memory and compares | R2 tooling |
| C6 | tooling | Template carries numbers of its own (15-year, 100 ms, ±10 %, row labels); experiments panel drops non-PASS/FAIL verdicts | **Confirmed.** Constants moved to the snapshot with sources; all verdicts shown | R2 tooling |
| C7 | tooling | Register status parser takes the first `**X**` anywhere in the cell | **Confirmed.** Anchored at the cell start; unparsed status fails the build | R2 tooling |
| C8 | tooling | Crux status not validated: missing or S rows count as evidence; "gap" nearly unreachable | **Confirmed.** Missing row fails the build; only V rows are evidence; gap = no V row | R2 tooling |
| C9 | tooling | Coverage matrix shows T for demos with flagged steps; a passing demo under an N family is silent | **Confirmed.** `T*` for flagged; mismatch listed | R2 tooling |
| C10 | tooling | Handback overstatements ("producers stamped", "all current", Python 260 next to 276) | **Confirmed.** Corrected in the handback | docs |
| C11 | tooling | A model name in `docs/PROJECT_SUMMARY.md`; historical commit authors and scratchpad paths in some results | **Confirmed for the model name** (reworded). Commit authorship is history (rewriting needs a force push; not done); scratchpad paths are not model identifiers (no change) | docs |

## 5. Decisions

## 6. Closing — *(written last)*
