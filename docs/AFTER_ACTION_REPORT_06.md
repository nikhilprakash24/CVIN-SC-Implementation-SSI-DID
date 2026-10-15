# After-Action Report 06 — Third next-session list (2026-10-15)

**Opened:** before the pass ran. **Status:** OPEN.
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

## Notes in flight
