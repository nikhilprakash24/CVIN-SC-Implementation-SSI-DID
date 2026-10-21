# After-Action Report 06 — Third next-session list (2026-10-15)

> **Lineage merge note (2026-10-21, PR #3).** This report was `docs/AFTER_ACTION_REPORT_06.md` on the
> `claude/clone-cvin-id-scs-…` lineage. The `cv2x-testbed-setup` lineage had already used number 06 for a different
> pass (`docs/AFTER_ACTION_REPORT_06.md`), so on the merged trunk this one lives here. Its register rows #40–#42 are
> renumbered #52–#54 (`docs/MEASUREMENT_CONDITIONS.md`, merge note). The text below is unchanged.


**Opened:** before the pass ran. **Status:** CLOSED 2026-10-15; results are in `docs/HANDBACK_2026-10-04.md` §4.
**Input:** `docs/HANDBACK_2026-10-04.md` §4, the third "Next session (executable now)" list. Author
decisions (handback items 1–15) are **not** taken here.
**Base:** `fa6188e`. The register runs to #39 (the parallel harness session's HTTP-RPC row), so this
pass numbers new rows from **#40**. It fetches before every push and stays off
`1_blockchain-identity/benchmarks/**`, `results/metrics*/**`, `analysis/**`,
`HANDOFF-DATA-COLLECTION-FRAMEWORK.md` and register §5.
**Host:** Intel Xeon @ 2.80 GHz × 4 (the same class as #37's host; #32 ran on a 2.10 GHz host).

## Plan

| Stream | Item | Output | Gate |
|---|---|---|---|
| **H-R** resolver on-chain | `_resolve_ethr` reads the ERC-1056 registry when it is configured with an RPC URL and registry address (owner, delegates, attributes from `DIDOwnerChanged`/`DIDDelegateChanged`/`DIDAttributeChanged`, forward replay; `deactivated` when the owner is 0x0). It fails closed on RPC error (an error result, never a silently synthesised document). The offline mode stays the default and is labelled in metadata. `did:mobi`: replace the placeholder with resolution from the MOBI registry (`getVehicleDID` → `did:ethr`, VIN only as a hashed `alsoKnownAs`), or record it as out of scope | resolver + tests; external suite and checker re-run | suite ≥ 335/336, checker ≥ 94.3 %, VID-R1 re-graded |
| **H-A** attestEvent | Restrict `MOBIVIDRegistryV2.attestEvent` to the vehicle's current owner and its valid ERC-1056 delegates (plus the event's own issuer roles, if the design needs them, stated); duplicate-attestation guard (handback item 4, if in scope without a framing change; otherwise left) | contracts + tests; gas regenerated; #28 pinned figure re-pinned | Hardhat green; determinism 55/55; the M3 regression test updated, not weakened |
| **H-K** same-host re-run | #32 (full refresh) and #37 (probe) back to back on this host, same node, same n, interleaved order | `cv2x-testbed/results/freshness_k_samehost.*`, register #40 | both modes on one host; knee per mode with t_local |
| **H-L** Pass 3 Lows | #21 revocation sanity check asserts the rejection *reason*; the security harness also checks the reverting contract address; a SUMO replay cache (with the same policy object as the providers) | code + tests | no number moves, or the move is reported |

## Phase log

| Phase | Commit | Result |
|---|---|---|
| Open | `ffb71b0` | Plan |
| H-A | merge + register | attestEvent owner-scoped for OWNER roles, duplicate guard; M3 re-pinned 191,974; 2/55 gas cells |
| H-L | `c0d436a` | Pass 3 Lows fixed; no number moved |
| H-R | merge + register | On-chain did:ethr, did:mobi via the MOBI registry; suite offline 335/336, on-chain 311/311; checker 94.3 % (84.1 % if the placeholder is retired) |
| H-K | merge | Same-host freshness, both modes: probe better at every k, no knee on this host |
| M4 | (session) | Re-run on the post-H-A bytecode on a quiet host; verdicts unchanged; event gas 255,556 |
| Close | this commit | #42, #33, LATENCY_BUDGET, README, handback |

## Notes in flight
- **I contaminated a parallel measurement, and caught it.** I started an M4 latency run while H-K was
  measuring latency on the same host. I discarded my run, sent H-K the exact time window, and H-K
  excluded the overlapping replicate (r4) and added replicates under its load rule. The M4 re-run waited
  until the host was quiet. A later quiet-host M4 run showed the same MOBI latencies, so the slower
  numbers come from the host, not the contention; discarding was still the right call while H-K ran.
- **Orphaned node.** H-A left a Hardhat node running on 8561 from its deleted worktree (killing the
  `npx` wrapper doesn't kill the child). It was found before the Python run and stopped. Agent prompts
  should say "kill the node process itself, not the npx wrapper".
- **Register collisions (#40, #41).** The parallel session added rows while this pass was running; mine
  were renumbered to #42 and every reference updated. A convention is proposed in the handback.
- **The placeholder finding.** H-R correctly stopped rather than retire the did:mobi placeholder: doing
  so drops the checker to 84.1 %. The headline 94.3 % therefore depends on a vector that puts the raw
  VIN in the DID, and that is now disclosed in #4 and is author decision 16.

## Closing summary
- All four streams are done. New row #42; #4, #24, #25, #28 and #33 updated; LATENCY_BUDGET §4 now
  quotes knees with their t_local.
- Two new author decisions (16, 17) and a new next-session list.
