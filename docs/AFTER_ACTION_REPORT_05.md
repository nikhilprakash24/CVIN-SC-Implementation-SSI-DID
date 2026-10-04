# After-Action Report 05 — Fixing the High-Severity Defects the Sandbox Found

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-04, before any fix; updated per fix; closed at the end
**Trunk at start:** `b6b887f`, clean, CI green
**Input:** `docs/DEFECT_LOG.md` §B (high-severity items) — the author confirmed the three
plan defaults and said "continue"; the proposed order was D11, D21/D22, D18, D13, D10, D25.

## 0. Rule for every fix
A fix lands only with (a) a regression test in the layer that owns the path (L2 per-option
suite, security harness, or L3 pytest), (b) the affected demos still green, (c) the grand
runner green, and (d) every result of record the fix moves regenerated or annotated:
contract changes move gas, so the nine-standard table is re-executed (deterministic,
CI-checked) and the register rows that predate the fix are annotated rather than silently
left stale.

## 1. Plan

| # | Defect | Fix | Owner of the regression test | Results moved |
|---|---|---|---|---|
| F1 | D11 — MOBI provider verifies against the key inside the message | resolve the key from the registry (as `erc1056_provider` does since D4); reject impostors | L3 pytest (in-process with a fake registry) + an L4 harness scenario if cheap | none (off-chain) |
| F2 | D21 — `ERC1056Registry.revokeIdentity` severs the `changed()` list; `changeOwner` ignores the revoked flag; repeatable revoke | emit `previousChange` on `DIDRevoked`; gate `changeOwner` on revoked; make revoke idempotent-reject | L2 MOBIVID/ERC1056 suite + provider event walk | gas on the vehicle-profile and MOBI rows (#21/#29/#30 gas columns, #25 MOBI column) |
| F3 | D22 — `CVINCombinedIdentity` claim ops bump `changed` without an event | emit a change event carrying `previousChange` on `addClaim`/`removeClaim` | L2 CVINCombined suite (resolver walk completes) | #25 CVIN-Combined claim rows |
| F4 | D18 — `CVINVehicleDIDRegistry.setVehicleAttributes` overflows on `type(uint256).max` validity | bounded validity; regression test that the birth record is reachable | L2 ERC1056 wrapper suite | wrapper gas (#1) if the fixed path is measured |
| F5 | D13 — VIN case-sensitivity mints duplicate identities (ERC-721, ERC-1155, LSP8) | normalise to upper case and validate ISO 3779 shape (17 chars, no I/O/Q) in every mint path | each L2 per-option suite: lower-cased VIN resolves to the same identity / is rejected | create gas on three options (#25, #3) |
| F6 | D10 — `MOBIVIDRegistry.getVehicleDID` lacks `0x` | string builder fix | L2 MOBIVID suite + the did:ethr ABNF check | none |
| F7 | D25 — ERC-735 claim holder: no issuer whitelist; VIN attestation not bound; signature scheme differs from CVIN-Combined | issuer registry + VIN binding now; the scheme unification is a design decision recorded for the author (recommendation: EIP-191, matching the VC layer and ERC-4337) | L2 ERC735 suite | claim gas (#25 ERC-735 rows) |

Order of execution: F1 directly (Python, no chain); F2–F4 and F6 delegated as one group
(the ERC-1056 family and MOBI registries; the MOBI copies must stay byte-identical — CI
checks it); F5 delegated as a second group (three token contracts); F7 after, by me.
Then: re-execute the nine-standard gas benchmark, run the grand runner, annotate the
register, update the defect log, close.

## 2. Execution log
- 2026-10-04 — report opened; state check and the D11 code read requested.
- **F1 (D11) done**: `verify_message` now binds verification to the key registered for the vehicle (record lookup by `vehicle_did`; embedded key must match; unknown/revoked rejected; on-chain `isRevoked` when attached). Six chain-free regression tests (the provider's constructor probes the chain, so the test initialises the base class directly); Python side **87 passed**. Finding while reading the code: the vehicle key is generated *after* the birth transaction and never anchored on-chain — recorded as **D11b**, to land after the D21 registry changes. Confirmed the SUMO harness verifies through the VC layer, so the V2V results never ran on the defective path.
- F2–F4, F6 (ERC-1056 family, MOBI) and F5 (token VINs) delegated as two groups with disjoint files; running.

## 3. Decisions
- **D-E** — contract fixes are allowed to move gas; the results of record are regenerated
  and the register says which rows changed and why, rather than freezing numbers that
  no longer describe the code.

## 4. Closing — *(written last)*
