# Follow-up stream H-A: `attestEvent` scope and duplicate attestations

**Date:** 2026-10-15 · **Author:** Nikhil Prakash
**Input:** `docs/AFTER_ACTION_REPORT_06.md` (stream H-A); `docs/HANDBACK_2026-10-04.md` §4 item 4 and
next-session item 2; `docs/review02/PASS2_K.md` (the duplicate finding); `docs/review02/FOLLOWUP_FC.md`
(M3 test, pinned 169,295); `docs/review02/FOLLOWUP_GM.md` (how gas, sweep and testbed artifacts are
regenerated); register #28.
**Base:** `ffb71b0`. Local commits, not pushed. The shared docs (register, README, handoffs, index,
after-action reports, MOBI checklist) are not edited here. §6 and §7 hold the text to apply.

## 1. Commits

| Commit | Scope |
|---|---|
| `ddd954e` | Fix 1: OWNER-role attesters must own the vehicle (both contract copies, Hardhat tests, M3 test, testbed artifacts) |
| `f01dd83` | Fix 2: one attestation per (event, attester) (both contract copies, Hardhat tests, M3 test, testbed artifacts) |
| `687c199` | Nine-standard gas results (`gas_benchmark.json`, `gas_benchmark_stats.json`, `gas_comparison.{csv,tex}`) |
| `cfd8c34` | MOBI VID backend sweep (`mobi_vid_backends.{json,csv,tex}`) |
| (this file) | report |

Each code commit leaves `cv2x-testbed/contracts/MOBIVIDRegistryV2.sol` byte-identical to
`1_blockchain-identity/contracts/MOBI/MOBIVIDRegistryV2.sol`. As in G-M, the testbed artifacts were
rebuilt with the testbed's own `hardhat.config.js` (solc 0.8.20, optimizer 200, no viaIR, evm paris;
`npx hardhat compile --force` in `cv2x-testbed/`). `node scripts/check_artifacts_fresh.js` passes after
each commit. The `*.dbg.json` files change only because their build-info pointer is shared. The ERC-1056
and MOBI V1 ABIs and bytecode, and the flat `ERC1056Registry_{abi.json,bytecode.txt}`, are unchanged.

## 2. Who can attest

**Delegates.** `ERC1056Registry` (the MOBI base, K-5) has no on-chain delegate record. `addDelegate`
emits `DIDDelegateChanged` and stores nothing, so no contract can check "valid, unexpired delegate of V".
The rule is therefore **owner only**: a delegate of V gets no attestation right. This is tested.

**Documented multi-party attesters.** The design names third-party organisations as co-signers. All of
these are on events the attester did not issue, and none is restricted to the event type's issuer roles:
- `MOBIVIDRegistry.test.js`: DMV and inspection station attest a service-centre MAINTENANCE event.
- `test_mobi_vid_layer.py`: the DMV attests the maintenance event as a "multi-party sign-off".
- `mobi_vid_backend_sweep.js`: "attestEvent by a second authorized party (DMV)" is the measured
  *third-party attestation* cell, and `multiPartyAttestation: true` is part of the 5/5 fidelity score.
- `benchmark_gas.js`: a DEALER attests a MAINTENANCE event.

A rule like "owner only" or "only roles allowed to issue that event type" would remove these: the DMV may
not issue MAINTENANCE. It would also break the documented design and the fidelity cell, which is a
framing change. So the organisational roles keep the registry-wide scope that G-M already confirmed as
by design for `recordLifecycleEvent`.

| | Before (`ffb71b0`) | After (`f01dd83`) |
|---|---|---|
| Role-less address (`NONE`), including a role-less current owner | rejected, "Not authorized to attest" | unchanged |
| Organisational role (MANUFACTURER, DEALER, SERVICE_CENTER, INSURANCE_COMPANY, GOVERNMENT_DMV, POLICE, INSPECTION_STATION) | any vehicle | any vehicle (unchanged, documented design) |
| `OWNER`-role address | **any vehicle** | only a vehicle whose current ERC-1056 owner (`identityOwner`) it is. Otherwise: **"OWNER role: not the current owner of this vehicle"** (the same reason as `recordLifecycleEvent`). A previous owner loses the right on transfer. |
| ERC-1056 delegate of V | only through its own role | unchanged: there is no on-chain delegate record, so being a delegate grants nothing |
| Same attester, same event, a second time | appended again (count inflated) | **"Already attested by this attester"** (`hasAttested[eventId][attester]`, public getter) |

Check order: event exists → role ≠ NONE → OWNER scope → signature (ecrecover == `msg.sender`) →
duplicate. The duplicate check runs after the signature check, so a forged or replayed signature still
reverts with "Invalid attestation signature". That keeps the existing forged-signature tests (JS and
`PY::test_forged_attestation_signature_rejected_on_chain`, which runs after the DMV has attested)
unchanged. A reverted attempt does not use up the attester's slot.

**Fix 2 is not a framing change.** The design describes "event attestations from multiple signers", so
the count should be the number of distinct attesters. The guard makes it so. The API, the role model, the
fidelity scores and the cross-backend ranking are unchanged: MOBI is still the cheapest native
attestation, at 215,362 against ERC-735's 292,730 and CVIN-Combined's 332,527.

**Not changed (flagged):**
- The issuer of an event can still attest its own event, so a one-party "multi-party" count is possible.
- `attestEvent(bytes32(0), …)` is still not rejected (the known quirk in the test file).
- A revoked vehicle's events can still be attested.

## 3. Tests

| Suite | Before | After |
|---|---|---|
| `npx hardhat test` (1_blockchain-identity) | 369 passing / 23 pending | **379 passing / 23 pending** (+10; none removed, skipped or weakened). 376 after `ddd954e` |
| `python3 -m pytest 2_w3c-ssi-layer -q` | — | **226 passed**, 0 skipped. The MOBI fixture started its own node on 8547. The first invocation reported 199 passed / 27 skipped (the node fixture skipped). Two later runs, the full suite and `mobi-vid` alone (37 passed), had no skips. The likely cause is a transient 8547 conflict on the shared host, but this was not verified. |
| cv2x-testbed `test_lifecycle_parity`, `test_mobi_vid_verify`, `test_t9_freshness` (node on 8561, killed by PID) | — | 52 passed on the rebuilt artifacts |
| `attack_results.json` (written by the Hardhat security test) | 43/43 DEFENDED, 11 N/A | byte-identical; outcomes unchanged |

New tests in `test/MOBIVID/MOBIVIDRegistry.test.js`:
- **"H-A: OWNER-role attestations are limited to the vehicle's current owner"**:
  - the OWNER-role owner of A attests B's event: reverts with the specific reason, and B's count stays 0;
  - the owner of B can (stored with role OWNER);
  - after a transfer the previous owner reverts and the buyer succeeds;
  - a `sigAuth` delegate of B (OWNER role) reverts;
  - a role-less current owner gets "Not authorized to attest";
  - DMV and inspection still attest B (control).
- **"H-A: one attestation per (event, attester)"**:
  - a second identical attestation reverts and the count stays 1;
  - distinct attesters are counted once each, and the same attester can attest another event;
  - a bad-signature attempt does not consume the slot.

**M3 (`test/MOBIVID/attestEventRegression.test.js`), updated, not weakened:**
- The forged, placeholder-blob and random-signature reverts are kept, as is the "no attestation stored"
  check.
- Added: the resubmitted valid attestation reverts.
- Added: a new access-control test (non-owner OWNER-role reverts, owner OK, previous owner reverts after
  transfer, DMV still OK).
- The pin is still exact (± 0) for six event ids, with `gasUsed == 21,000 + calldata + execution`.
  The pin history in the comment reads 169,295 (F-C) → 169,509 (fix 1) → **191,974** (fix 2).

**Regression check on old code** (sources swapped back, tests kept):
- On `ffb71b0` (base), 5 tests fail: three H-A access tests ("didn't revert"), the M3 access test, and
  the M3 pin.
- On the `ddd954e` contract, 4 tests fail: two duplicate tests, the M3 vulnerable-path test (duplicate
  assertion), and the M3 pin.
- The other new tests are positive or control cases and pass on both versions, as intended.

## 4. Gas: before / after

The conditions are unchanged (solc 0.8.24, optimizer 200 + viaIR, evm cancun, OZ 5.0.2, Hardhat
in-process). **2 of 55 gated cells move, both in MOBI-VID-V2.**

| Item | Before | After fix 1 | After fix 2 | Δ total | Cause |
|---|---:|---:|---:|---:|---|
| attestEvent **execution gas** (M3 pin, first attestation, DMV) | 169,295 | 169,509 | **191,974** | +22,679 | +214: warm SLOAD of the role + compare. +22,465: cold SLOAD + zero-to-non-zero SSTORE of `hasAttested` |
| attestEvent `gasUsed` (benchmark note, un-gated) | 192,683 (range 192,659–192,683) | — | **215,362** (range 215,350–215,362) | +22,679 | as above; spread is calldata zero bytes |
| MOBI-VID-V2 deployRegistry (gated) | 4,058,713 | — | **4,115,781** | +57,068 (+1.41 %) | owner check, mapping + getter, revert strings |
| MOBI-VID-V2 transferOwnership (gated) | 200,023 | — | **200,045** | +22 | selector-dispatch shift from the new `hasAttested` getter (same mechanism as K-1) |
| MOBI backend sweep, third-party attestation (DMV) | 192,683 | — | **215,362** | +22,679 | as above |

Relative-cost column that moved: MOBI deploy 8.89× → 9.02×. No other cell, ratio or standard changed.
MOBI birth 299,143 and lifecycle event 307,166 are unchanged. ERC-1056 addDelegate 35,277, revoke and
all sweep fidelity scores are unchanged.

**Determinism.**
- `run_gas_stats.py --runs 30`: `all_deterministic: true`. `gas_benchmark_stats.json` is regenerated.
- A fresh `benchmark_gas.js` + `generate_tables.py` run, compared against the committed JSON with the
  CI gate's logic: **55 committed cells, 0 differ, 0 missing, 0 new**.

**Security results.**
- `attack_scenarios.py` (and through it `security_scenarios.js`) was re-run. No outcome changed and no
  gas figure changed: the Sybil proxy is `createIdentity`, which is unchanged. The output was therefore
  **not** committed.
- The only content difference is pre-existing G-M drift: the `privacy` evidence string in
  `onchain_security.json` / `security_matrix.json` still shows the old `getVehicleDID` without `0x`.
  The rest is timestamps and per-run random addresses. Committing it belongs to whoever regenerates the
  security matrix next.

**Testbed build** (0.8.20, no viaIR). Measured directly on the old (`ffb71b0`) and new tracked artifacts,
same call sequence:

| Operation | Before | After | Δ |
|---|---:|---:|---:|
| deploy | 5,059,513 | 5,135,625 | +76,112 |
| registerVehicleBirth | 276,317 | 276,317 | 0 |
| recordLifecycleEvent | 306,802 | 306,868 | **+66** (dispatch shift; this build orders selectors differently) |
| attestEvent (execution) | 168,240 | 190,979 | +22,739 |
| transferVehicleOwnership | 199,196 | 199,196 | 0 |

**Not regenerated, and why it is not needed:**
- Scaling (#26): `benchmark_scaling.js` uses `recordLifecycleEvent` only, which is unchanged in the viaIR
  build.
- The metrics harness (#29/#30/#35) does not deploy `MOBIVIDRegistryV2` (G-M).

## 5. #33 (M4) impact

`attestEvent` is **not** in M4's operation set. `experiment_lifecycle_parity.py` measures birth,
lifecycle event, ownership transfer and history query, and nothing in `cv2x-testbed` calls `attestEvent`.
So #33 does not need a re-run for the attestEvent change.

The testbed bytecode did change, though: #33's second run was on the post-G-M bytecode, which is no
longer in the tree. On the new bytecode the lifecycle-event write costs about **+66 gas**, so 255,490
becomes about 255,556 in #33's own run conditions. Birth and transfer gas are unchanged, and no latency
verdict can move by 66 gas. I did not run M4. Whether the +66 needs a disclosed re-run or just a note is
the author's call.

## 6. Proposed register text

**Row #28.** Replace the attestEvent clause with:

> … attestEvent found-and-fixed 121,110 → 192,718 gas (July build). On the current build the fixed path
> costs **191,974 execution gas ± 0** (`receipt.gasUsed` 215,350–215,362 depending on calldata zero bytes;
> run of record 215,362). **Re-pinned 2026-10-15 after H-A:** an OWNER-role attester must be the
> vehicle's current owner (+214), and one attestation per (event, attester) (+22,465). The previous pin,
> 169,295 (192,659–192,683), is **S**: any OWNER-role address could attest any vehicle's events, and a
> role-holder could inflate an event's attestation count by resubmitting.

**Row #25 (nine-standard gas).** Append:

> … **Re-executed 2026-10-15 after H-A** (MOBI `attestEvent` scope + duplicate guard): 2 of 55 gated
> cells move, both MOBI-VID-V2: deploy 4,058,713 → **4,115,781** (+1.4 %), transfer 200,023 →
> **200,045** (+22, selector dispatch). The un-gated attestEvent note is 192,683 → 215,362. All other
> standards unchanged; 30/30 runs byte-identical; determinism gate 55/55.

**H4 / MOBI backend table (`mobi_vid_backends.*`).** MOBI-VID-V2 third-party attestation 192,683 →
**215,362**. Fidelity scores are unchanged, and MOBI is still the cheapest native attestation.

**Row #33 (M4).** Append:

> attestEvent is not in M4's operation set. After H-A (2026-10-15) the testbed bytecode changed again;
> the lifecycle-event gas is **S** until re-run (expected about +66, i.e. ≈255,556). Birth, transfer and
> latency are unaffected.

## 7. Checklist changes to apply (`docs/MOBI_VID_CHECKLIST.md`)

- **§5.2, the `OWNER` bullet (line 161):** replace "and `attestEvent` is still open to any authorised
  role." with: "`attestEvent` applies the same rule since H-A (`ddd954e`): an OWNER-role attester must be
  the current owner. Organisational roles attest on any vehicle (the documented multi-party design), and
  each attester counts once per event (`f01dd83`)."
- **§5.2, new bullet:** "One attestation per (event, attester) (`hasAttested`, H-A `f01dd83`), so the
  attestation count is a count of distinct attesters. Tested by `JS::H-A: one attestation per (event,
  attester)`."
- **VID-D5:** add `JS::H-A: OWNER-role attestations are limited to the vehicle's current owner` to the
  Tests column. The status stays **Partial**: ERC-1056 delegates are still never consulted, now
  explicitly so, because the base registry has no delegate record (K-5).
- **UC2-BR2:** no change. The status stays **Not impl.**: service-centre writes still need no owner
  consent.
- **Line references:** `V2:340-347` (VID-R4, VID-D5) is now `V2:387-391`, and `V2:319-365` (§5.1 SEC
  row, §5.2) is now `V2:316-417`.
- **Summary table (§6):** no count changes.

Also stale, but not in the do-not-edit list and not edited here: `2_w3c-ssi-layer/mobi-vid/README.md`
("V2 `attestEvent` 188,480"), and the ch. 4/5 attestEvent gas mentions. Both are for the author's
chapter and doc pass.
