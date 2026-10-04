# After-Action Report 04 — Review-2 follow-up: the next-session list (2026-10-04)

**Opened:** before the pass ran. **Status:** CLOSED 2026-10-04; results are in `docs/HANDBACK_2026-10-04.md` §4.
**Input:** `docs/HANDBACK_2026-10-04.md` §4, "Next session (executable now)". The author decisions in
the same section are **not** taken here.
**Base:** `ff38d76`. It includes a parallel session's `erc1056w` adapter and the toolchain-pinning
rule (`MEASUREMENT_CONDITIONS.md` §5.E). That session also writes to this branch, so this pass
fetches before every push and stays off its files (harness, `HANDOFF-DATA-COLLECTION-FRAMEWORK.md`,
register §5).

## Plan

| Stream | Items | Output | Gate |
|---|---|---|---|
| **F-A** status-B re-runs | #27 V2V latency (N=30, `--simulate`), #26 scaling Exp. C/D (verify scaling, V2V saturation) on this trunk | regenerated `4_comparison-framework/results/` files + old→new table + proposed register text | clean tree, N as pre-registered |
| **F-B** external conformance | #24: re-run w3c/did-test-suite against the current resolver | `docs/conformance/` report + raw jest output | the six R5 failures cleared, as predicted? |
| **F-C** security matrix and #1 | Regenerate the Sybil-cost matrix; add the S-1 thief-with-own-DID cell; re-measure #1 `createVehicleDID` in test context; check that M3 (attestEvent regression pinned) holds | `security-analysis/results`, tests | outcomes, with any change explained |
| **F-D** experiments | freshness-k sweep (k ∈ {1, 5, 25, ∞}, review §5.1, `LATENCY_BUDGET.md` §4) and M4 lifecycle parity (pre-registered in `PLAN_MOBI_SUMO.md` A.2) | `cv2x-testbed/results/{freshness_k,lifecycle_parity}.*` | pre-registered hypothesis reported as-is, pass or fail |
| **F-E** MOBI clause checklist | M1: VID I preview PDF → clause → element → test → status | `docs/MOBI_VID_CHECKLIST.md` | every clause has a status; out-of-scope clauses get an SC entry proposal |
| session | register #29 attribution (toolchain, not wallets, per §5.E); CI check that the testbed artifacts are fresh; merge, verify, register, handback | | CI green |

## Phase log

| Phase | Commit | Result |
|---|---|---|
| Open | `d2e6a58` | Plan; #29 U1/U4 attribution corrected (toolchain, §5.E) |
| CI | `a712cb7` | The testbed artifact-freshness check now runs in the `python-full-suite` job |
| F-B | `6a73c6d`, `62d5c46` | External W3C DID suite **336/441** (was 328); R5 cleared, no regressions; #24 |
| F-C | merge + `910e5e8` | Security matrix current (outcomes unchanged); S-1 own-DID thief cell; #1 → 78,090; M3 attestEvent regression pinned at 169,295 execution gas; #1/#2/#19/#28 |
| F-E | `565e53d` | `MOBI_VID_CHECKLIST.md`: 29 clauses; "MOBI VID compliant" unsupported. Framing and SC-14 to SC-20 left to the author |
| F-D | merge + `d53126e` | Freshness-k (#32): P*=100 knee at k≈146; staleness k−1. M4 (#33): writes PASS, cached history FAIL as pre-registered; SC-13 closed; LATENCY_BUDGET §4 note |
| F-A | `2e41ee2`, `3076251` | #27 → V (0.153 ms); #26 C/D → V (O(1); 0.164 ms/neighbour; P*≈609, extrapolated). Same-host A/B: the movement is environmental |
| Fix | after `2e41ee2` | The Exp C table printed "O(N)" from one noisy run; the generator now states the pre-declared confirmation verdict (O(1)) and gives the single run's reading beside it |
| Merge | `4f2ead3` | The parallel session's six new adapters (all nine standards in the harness) merged without conflict; **Hardhat 353 / 23 pending** |
| Close | this commit | README, register #5, handback |

## Notes in flight
- **H-3 attribution corrected.** The parallel session showed that the ERC-721 U1/U4 +12/+25 shift
  between the original run and review 2's runs was a **toolchain** difference (unpinned Hardhat
  2.29.1 vs lockfile 2.28.6), not the random wallets that review 2's H-3 blamed. H-3's fix (seeded
  wallets) is still right: it removed the batch-cell drift. But register #29's sentence about
  U1/U4 was wrong and is corrected in this pass.
- **Parallel session.** A second session pushed to this branch three times during the pass. Each
  time the local branch was fetched and merged (fast-forward, or one conflict-free merge) before
  pushing, and its files (harness, `HANDOFF`, register §5) were not edited here.
- **A misleading generated label caught at merge.** F-A committed a regenerated Exp C table whose
  caption said "O(N)", from a single noisy run. Its own pre-declared confirmation block said O(1). It
  was fixed in the generator rather than by hand-editing the output, so the next regeneration stays
  correct.
- **Wording correction.** The SC-13 closure note F-D proposed said "Chapter 5 reports both
  verdicts". No chapter has been edited, so it now says "should report", pending the author.
- **Scratchpad sharing.** F-A noted that it ran `rm -rf old` in a scratch directory shared with
  other agents. No committed work was affected (every stream committed in its own worktree), but
  future agents should use per-agent scratch subdirectories.

## Closing summary
- Every item on the handback's next-session list is done. Each moved number has a register row with
  its old value and reason.
- Status-B rows are now V: #26 C/D, #27. New rows: #32, #33.
- Four new author decisions (handback items 9–12), and a new next-session list of five items.
