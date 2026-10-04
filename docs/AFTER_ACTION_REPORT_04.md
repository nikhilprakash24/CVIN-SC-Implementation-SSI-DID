# After-Action Report 04 — Review-2 follow-up: the next-session list (2026-10-04)

**Opened:** before the pass ran. **Status:** OPEN.
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

## Notes in flight
- **H-3 attribution corrected.** The parallel session showed that the ERC-721 U1/U4 +12/+25 shift
  between the original run and review 2's runs was a **toolchain** difference (unpinned Hardhat
  2.29.1 vs lockfile 2.28.6), not the random wallets that review 2's H-3 blamed. H-3's fix (seeded
  wallets) is still right: it removed the batch-cell drift. But register #29's sentence about
  U1/U4 was wrong and is corrected in this pass.
