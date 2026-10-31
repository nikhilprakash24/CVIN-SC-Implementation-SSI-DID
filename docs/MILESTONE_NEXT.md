# Next Milestone — Deferred Decisions

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-09. **Why:** the author approved the infrastructure-messaging and SUMO-visualisation
designs and asked that the Infura rotation "or other decisions that can be pushed" move to the next
milestone. This file is the list. Nothing here blocks the current work; each item keeps its default.
**Milestone:** v0.9.0 (cut on the merge with a Sepolia witness, per `ORIGINAL_PROMPT_AND_DIRECTION.md` §B.2),
or the next author checkpoint, whichever comes first.

**Status at the close of work milestone WM-1 (2026-10-10).** Closed: N-6, N-13, N-14, N-21. **The author's
decisions** (nothing executes until decided; the default stands): N-1, N-4 (go-ahead), N-5, N-7, N-8,
N-9, N-10, N-11, N-12, N-17, **N-23 (AI-use disclosure, raised by the WM-1 audit)**. **Executable without a decision**, scheduled in `docs/PLAN_WM-2.md`: N-2, N-3,
N-15, N-16 (design first), N-18, N-19, N-20, N-22.

| # | Item | Default until decided | Source |
|---|---|---|---|
| N-1 | Rotate the Infura credential exposed on the onboarding lineage's branches (H1) | not rotated; not on the trunk | `docs/prior-survey/README.md` |
| N-2 | Test a clean `npm ci` without SSH (`ethereumjs-abi` via `git+ssh://`, H9) | CI installs succeed today | same |
| N-3 | Remove the unused `goerli` network entries | left in place | same |
| N-4 | Install SUMO and run S1–S3 with real mobility (S-b) | mock mobility | `docs/PLAN_SUMO_VISUALISATION.md` |
| N-5 | TSR second-pass sheet: the 20 AUTHOR decisions, incl. D-02 (test ids by record vs title) | the sheet's defaults | `docs/planning/TESTING_SUITE_SECOND_PASS_SHEET.md` |
| N-6 | ~~Ch. 6 §6.4 wording on the 94.3 % residual~~ **closed in pass 12** (reworded to two failures and one PARTIAL, the `did:mobi` placeholder key; audit A-F12) | — | `docs/HANDBACK_2026-10-09.md` X-2 |
| N-7 | Confirm the five sentences naming ERC-735 the heaviest create | accepted | X-1 |
| N-8 | Defect-log policy calls: D8 rest, D12 rest, D15, D16 rest, D19, D20, D23, D24, D25c (EIP-191 recommended), D26 | documented, not fixed | `docs/DEFECT_LOG.md` §C |
| N-9 | Review-2 decisions 1–6, 9–11, 13–15 (H1 wording, checker strictness, K-4/K-5/K-12, attestEvent duplicates, MOBI wording, freshness k, M4 verdict, 7.1.2 correction, privacy scope) | review-2 defaults | `docs/HANDBACK_2026-10-04.md` §4 |
| N-10 | Merge decisions M-A…M-L: re-review by a different assistant configuration | stand | `docs/PLAN_MERGE_LINEAGES.md` |
| N-11 | Push tags v0.7.0/v0.8.0; Sepolia secrets; SC-05/SC-06; notebook index; chapter 2 citations | open | `docs/HANDBACK_2026-09-30.md` |
| N-12 | Default branch of the repository | unchanged | plan 2026-10-09 Q6 |
| N-13 | ~~`3_cv2x-testbed/README.md` July counts~~ **closed in pass 11**: the stale-figure checker now scans it | — | handback X-7 |
| N-14 | ~~Scope the Python header's `tree_clean`~~ **closed in pass 11**: `code_clean` added beside it, CI probe (`b1d3f72`; D33) | — | after-action report 10 |
| N-15 | Extend the TSR test register beyond L1, the security harness and the demos to the Python layers (L3/L4, incl. the 16 infrastructure tests) | Python layers counted in the grand report only | same |
| N-16 | RSU-to-RSU messaging (C3 gap): **closed 2026-10-24, out of scope** (author decision D2; SC-24) | stated in crux C3 and chapter 6 §6.6.3 | none |
| N-17 | Choose the k the thesis defends for RSUs (same decision as N-9's freshness k). I3 bounds a message count (k − 1), not a time: the cache does not expire, so a time bound also needs a cache lifetime | k open; no cache expiry | register #46 |
| N-18 | ~~Seed the random inputs of the L1 mechanism tests, the demos and `infrastructure_gas.js`, or report ranges by rule~~ **closed in pass 17** (WM-2 B1): incidental inputs seeded through `sandbox/lib/determinism.js` (`CVIN_SEED`, set by the grand runner); L1 identical in 99 of 99 cells across seeded runs; demos in 1,749 of 1,752 steps (the other 3 hash `block.timestamp` inside the MOBI V2 contract, declared); I4 a range over declared seeds 1–30, reproducible (#47); rule written into guide 1.1.10 | — | after-action report 17 |
| N-19 | Root-anchor the pathspecs of `dirtyMeasured` in `1_blockchain-identity/benchmarks/run.js` (same inert-flag fault as the run stamp); do it with the next harness run of record, because the change alters the harness's measured-code hash (§5.F). **Since WM-2 A2:** the harness is a registered producer with a resolved scope and a passing probe; the change at A6 is one line (`dirtyMeasured: runStamp(__filename).dirty`). A2 made it and reverted it in the same pass to keep HEAD's `benchmarksTree` equal to the run of record's (after-action report 14) | the run of record's whole-tree `dirty` is false, so it is unaffected | after-action report 11 |
| N-20 | Stamp the five producers classified *stamp producer* in `docs/testing/STAMP_INVENTORY.md` and re-run them (TSR phase 5) | classified; scopes registered (WM-2 A2); the security matrix now stamps itself and goes through the promote step (A4); stamp calls for `run_gas_stats.py`, `w3c_compliance_checker.py`, `attack_scenarios.py` and the `sensitivity` re-run remain (A3, after C1/C2) | same |
| N-21 | ~~Widen `check_stamps.py` globs~~ **closed in pass 13** (WM-2 A1): 161 tracked result files accounted for, 0 uncovered; `--check-coverage` in CI | — | after-action report 13 |
| N-22 | Brief a session-level adversarial review whose briefs are written outside this session: Python suites outside L3, the contracts, chapters 1–4 and 6–7 were not in pass 11's scope | pass 11 covered passes 9–10 only | same |
| N-23 | **AI-use disclosure.** The repository has no AI-use statement in the README, the thesis front matter or the author-bylined reports, although `PROVENANCE.md` states "AI tooling, under researcher direction" and several reports are written in the assistant's first person under the author's byline (WM-1 audit, finding P-F14). Decide: an AI-use statement in the README and thesis front matter (the university's policy governs the wording), and whether reports keep the first person | no statement added; nothing changed until decided | after-action report 12 §4 |
| N-24 | **Chain-backed resolution, measured.** WM-2 C1 made `_resolve_ethr` read the ERC-1056 registry when given a provider. Two follow-ups: (1) a W3C DID test-suite run whose did:ethr vectors are resolved from a chain (an identity with an owner change, a delegate, a service and a deactivation), beside the static run of #24; (2) re-measure resolution latency for the chain path (the M0 resolution-latency row is superseded and names C1) | not run in report 21: the suite's current inputs do not change, and a chain-backed run changes its denominator and needs a node in the suite harness | after-action report 21 |
| N-25 | ~~Testbed copies of the MOBI contracts~~ **closed in report 22.** CI's "MOBI contract copies are byte-identical" step (plan S0) failed on the first C2 commits, which had left `cv2x-testbed/contracts/` behind. The three files were synced and the testbed artifacts recompiled (solc 0.8.20, paris): the testbed `ERC1056Registry`'s compiled code differs only in its metadata hash (deploy gas identical), and its `MOBIVIDRegistry` / `MOBIVIDRegistryV2` artifacts now carry C2, so the testbed's MOBI re-runs at A3b measure it | closed | after-action report 22 |
| N-26 | **The metrics harness records no host.** `1_blockchain-identity/results/metrics{,-rpc}/latest/meta.json` names Node and the compiler but not the CPU, so the harness latency rows (#31, #39) are descriptive only under the latency charter (WM-2 B3). Add the CPU (and logical CPU count) to `meta.json` in `benchmarks/run.js`, at the next harness run of record | latency rows #31 and #39 descriptive only; gas rows unaffected | after-action report 35 |
