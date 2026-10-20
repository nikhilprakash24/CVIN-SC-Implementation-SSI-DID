# Execution Trace Schema (JSONL)

One JSON object per line. Produced by `scenarios/*.js`; consumed by `explorer/`.
Traces are the evidentiary artifacts of the sandbox: every claim in Chapter 4
about gas, ordering, or revert behavior should be reproducible from a trace file.

| Field | Type | Notes |
|---|---|---|
| seq | int | Monotonic step number within the run |
| impl | string | Implementation under test (O1_ERC1056 ... O8_LFDT) |
| ts | int | Wall-clock ms |
| kind | enum | `tx`, `view`, `offchain`, `deploy`, `summary` |
| fn | string | Minimal-function name (e.g. `createDID`) |
| fnId | string | F1–F12, per the formal spec numbering |
| identity | string | Acting principal label (Registry, IdentityA, IdentityB, ...) |
| txHash | hex | Present for kind=tx |
| gasUsed | string | Present for kind=tx (decimal string) |
| events | int | Log count for kind=tx |
| note | string | Human-readable detail |

Off-chain steps (`kind=offchain`) capture the secure-channel operations (ECDH,
AEAD) that deliberately never touch the chain — their presence in the trace is
what demonstrates the hybrid on/off-chain architecture from Memo A §4.

## Extension tags (VID layer, 2026-10)

`fnId` may carry tags beyond F1–F12 for contracts beside the interface: `G0` addRoot · `G1` registerIssuer ·
`G2` endorseIssuer · `G3` revokeEndorsement · `G4` isEndorsed · `T1` declare · `T2` verifyTyped ·
`B1` anchorBatch · `B2` verifyInclusion · `B3` revokeBatch. Coverage counts in the `summary` entry report
F-tags separately. `kind=offchain` entries now also use `phase` values `queued`, `reconcile`, `link`,
`gate-decision`, `verify-offline`, `policy-check`, `merkle-batch`. No existing field changed (schema v1 intact).

## Schema v1.1 (2026-10-14, additive)

| Field | Type | Notes |
|---|---|---|
| latencyMs | number | Optional. Wall-clock milliseconds from submission to receipt (`tx`) or call to return (`view`), measured in the scenario process. On the Hardhat in-process network this is a **lower bound** and is never a latency result; it exists so the same scripts produce comparable numbers on Besu QBFT or a remote node. |

v1 consumers ignore unknown fields; no existing field changed.
Further tags: `Z1` ZKAgeGate.admit (on-chain Groth16 verification, tx) · `Z2` ZKAgeGate.check (view). `phase` values `zk-prove`, `zk-verify-offchain`, `bbs-sign`, `bbs-proof`, `commitment`, `unlinkability`, `comparison`.
Adapter tags: `A1` PresentationAnchor.anchorPresentation (tx) · `A2` PresentationAnchor.verifyAnchored (view) · `P1` IDPP continuity assertion (view).
