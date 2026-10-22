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
- **F2, F3, F4, F6 done** (ERC-1056 family and MOBI): `ERC1056Registry` emits `previousChange` on `DIDRevoked`, rejects a second revocation and gates every mutator on `notRevoked` (D21); `CVINCombinedIdentity` emits `DIDClaimChanged(…, previousChange)` on claim ops (D22); `CVINVehicleDIDRegistry` uses a 100-year attribute validity instead of `type(uint256).max` — the birth record is reachable at 83,290 gas (D18); `MOBIVIDRegistry.getVehicleDID` emits `0x` (D10). 18 regression tests; MOBI copies byte-identical; provider ABI/bytecode regenerated. Gas moved: revokeIdentity +547, changeOwner +2,213 (the `revoked` SLOAD), addClaim +2,328 — recorded for the benchmark re-execution. Not fixed (D16): the inherited `changeOwner` bypasses MOBI's ownership history — needs odometer/authority inputs, left for the author. Eight demos that asserted the old behaviour now fail and will be updated after the token group lands.
- **F5 (D13) done**: identical `_normalizeVIN` helpers (17 bytes; a–z upper-cased; bitmap check against 0–9/A–Z minus I/O/Q; check digit deliberately not enforced) in `CVINVehicleNFT`, `CVINVehicleCredential1155` (plus `vinHashOf`/`vehicleForVIN` views) and `CVINVehicleLSP8`; lookups normalise too. 15 regression tests. Gas on mint +2.7k/+3.4k/+3.0k (bitmap version chosen after measuring a +9k compare-chain). Fallout fixed here: the L1 helper and the smoke runner built test VINs beginning with "VIN" — the **I** is an invalid ISO 3779 character — prefix changed to "CVN"; the ERC-1155 adapter now upper-cases before hashing. Four token demos that asserted the old behaviour are queued with group 1's eight.

## 3. Decisions
- **D-E** — contract fixes are allowed to move gas; the results of record are regenerated
  and the register says which rows changed and why, rather than freezing numbers that
  no longer describe the code.

- **D-F** — revocation is terminal: every mutator, including `revokeDelegate`/`revokeAttribute`, reverts for a revoked identity (the agent offered a looser variant; rejected — clean-up after revocation would re-open the change list a resolver relies on).

- **F7 (D25) done**: `CVINVehicleClaimHolder` gains `authorizeIssuer`/`revokeIssuer`/`isAuthorizedIssuer` (owner-only; the owner is exempt as self-issuer); `addClaim` checks signature → issuer authorised → topic-1 VIN binding (`_encodesHolderVin`). 14 regression tests. Every caller updated (ERC-735 adapter appends the VIN to topic-1 data before signing and authorises a non-owner issuer; security fixture; gas and scaling benchmarks; security-scenario script). Deploy +227,534 gas; D25c (raw-digest vs EIP-191) recorded in the NatSpec as the author's decision, recommendation EIP-191.
- **Results of record re-executed** (`2b38536`): nine-standard gas table, feature matrix and manifests regenerated from the fixed ABIs; 22 of 55 cells moved, each listed with its delta in `gas_moved_by_defect_fixes_2026-10-04.json`; register #25 annotated, #31 added; README and thesis-README figures refreshed (`3a7a4ec`). CI green.
- **Demos updated** (`5778651` ERC-735 by me; `eed6bfc` the other seven options, delegated): 16 demos had asserted the defective behaviour (step ids ending `-DEFECT`, `-CUT`, `not-blocked-*`); each now asserts the fix and is labelled "FIXED (Dnn)". One stale narrative found beyond the list: the JS mirror of `verify_message` in `mobi-vid/demos/offchain-messaging.js` still accepted an impostor — corrected to the D11 semantics. Acceptance: 67/67 demos under those options exit 0 with `ok:true`.
- **Grand run on the fixed trunk** (`eed6bfc`): ALL OK — smoke 11/11 adapters, L1 99, L1+L2 366, L3+L4 87, demos 92/92 with 1,688 steps and 66 flagged observations (was 319 / 81 / 1,625 steps / 87 flagged before the pass: +47 Hardhat and +6 Python regression tests, +63 demo steps, 21 fewer flags because the flagged defects are now asserted reverts).
- Defect log updated (§B statuses with commits; new §C: every open item with the decision it needs); session manifest Pass 6; handback addendum 0c.

## 4. Closing

**What was fixed.** Seven of the nine high-severity defects: D10, D11, D13, D18, D21, D22,
D25a/b. Each landed under rule §0: 47 Hardhat + 6 Python regression tests, demos green,
grand runner green, results of record re-executed. D16 is partly fixed as a consequence of
D21. Two high items remain open and are now unblocked: **D7** (ERC-1155 BIRTH_CERT moved by
a standard transfer, mechanical fix) and **D11b** (the vehicle key is never anchored
on-chain; it needed the D21 registry first).

**What the fixes cost, and why that is a result.** The chain-side fixes moved 22 of the
55 gas cells; the largest is ERC-735's deployment (+227,534 for the issuer registry) and the
smallest the +2.7–3.4k a VIN alphabet check adds to a mint. The pre-fix table priced a
surface that accepted impostor issuers, duplicate VINs and severed resolution lists. The
comparison chapter should say so: *veracity has a gas price, and the nine-standard table
now includes it.* That is the asymmetry section's security column made numerical.

**What I changed my mind about.** The agent that fixed D21 proposed letting `revokeDelegate`
and `revokeAttribute` run after revocation ("clean-up"). I rejected it (D-F): any mutation
after `DIDRevoked` re-opens the `changed()` list a resolver follows, and the revocation
record would no longer be the list's head. The cost is that a revoked identity is frozen with
whatever attributes it had; the resolver reports it as deactivated, which is the DID Core
semantics anyway.

**What I did not do.** No open **M** item was touched; they need author decisions and are
tabulated in `DEFECT_LOG.md` §C with the decision each one needs. The external W3C DID
test suite was not re-run against a registry-minted `did:ethr` (D10 follow-up); the resolver
fixtures it runs on were already conformant and the fix is in the registry's string builder,
but the claim "conformant end to end from this registry" is not yet evidenced. The
chapter-5 tables still quote July gas values (known since Pass 3).

**Trunk at close:** `eed6bfc` + this closing commit; tree clean after push; CI to be
confirmed on the closing commit (read below in the handback).
