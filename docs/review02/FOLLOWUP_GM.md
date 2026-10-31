# Follow-up stream G-M: MOBI quick fixes (K-15)

**Date:** 2026-10-04 · **Author:** Nikhil Prakash
**Input:** `docs/review02/AAR_REVIEW2_05.md` (stream G-M); `docs/MOBI_VID_CHECKLIST.md` VID-R1, UC2-BR2,
§5.2 and §6; `docs/REVIEW_02_CODEBASE.md` K-15; `docs/review02/PASS1_K.md` and `PASS2_K.md` (how gas
results and testbed artifacts are regenerated).
**Base:** `f73e81e`. Local commits, not pushed. The shared docs (register, README, handoffs, index,
after-action reports, MOBI checklist) are not edited here. §5 and §6 hold the text to apply.

## 1. Commits

| Commit | Scope |
|---|---|
| `27a2184` | `getVehicleDID` emits a well-formed `did:ethr` (both contract copies, Hardhat + Python tests, testbed artifacts) |
| `d5320b2` | V2: OWNER-role events only on the issuer's own vehicle (both contract copies, Hardhat tests, testbed artifacts) |
| `4573ee3` | Nine-standard gas results (`gas_benchmark.json`, `gas_benchmark_stats.json`, `gas_comparison.{csv,tex}`) |
| `191b920` | MOBI VID backend sweep (`mobi_vid_backends.{json,csv,tex}`) |
| (this file) | report |

Each code commit leaves `cv2x-testbed/contracts/{MOBIVIDRegistry,MOBIVIDRegistryV2}.sol` byte-identical
to `1_blockchain-identity/contracts/MOBI/`. The testbed artifacts were rebuilt with the testbed's own
`hardhat.config.js` (solc 0.8.20, optimizer 200, no viaIR, evm paris; `npx hardhat compile --force`
in `cv2x-testbed/`), and `node scripts/check_artifacts_fresh.js` passes after each commit.
`ERC1056Registry.dbg.json` changes only because its build-info pointer is shared. The ERC-1056 ABI,
bytecode and flat `ERC1056Registry_{abi.json,bytecode.txt}` files are unchanged.

## 2. Changes

**Fix 1: `getVehicleDID`** (`MOBIVIDRegistry.sol`, inherited by V2). The function returned
`did:ethr:0x7a69:70997970c5…`, with no `0x` before the address. `did_resolver.py` (`_ETH_ADDRESS_RE`,
`0x[0-9a-fA-F]{40}`) rejects that DID as `invalidDid`. It now returns
`did:ethr:0x<chainId hex>:0x<40 lowercase hex>`, for example
`did:ethr:0x7a69:0x70997970c51812dc3a010c7d01b50e0d17dc79c8`. The resolver's `parse_chain_id` accepts
hex chain ids and the address regex is case-insensitive, so the on-chain DID now resolves. It equals
the Python layer's `vehicle_did()` (`did:ethr:0x7a69:<EIP-55 address>`) up to address case. The Python
MOBI layer does not call `getVehicleDID`; it builds the DID itself. The Python test therefore checks
that the on-chain DID resolves and matches the VC-subject DID. Only callers that print the DID are
affected: `cv2x-testbed/scripts/deploy_mobi_vid.js` and the `security_scenarios.js` note.

**Fix 2: OWNER-role scope** (`MOBIVIDRegistryV2.recordLifecycleEvent`). The role matrix
(`_initializeAllowedIssuers`) lets `IssuerRole.OWNER` issue **MAINTENANCE, ACCIDENT, MODIFICATION,
THEFT_REPORT and INSURANCE_CLAIM**. OWNER is a global role (`authorizedIssuers[address]`), so any
OWNER-role address could file these event types against any vehicle. After the existing role and
revocation checks, the function now runs:

```solidity
if (authorizedIssuers[msg.sender] == IssuerRole.OWNER) {
    require(identityOwner(vehicleIdentity) == msg.sender,
            "OWNER role: not the current owner of this vehicle");
}
```

`identityOwner` is the ERC-1056 owner, which `transferVehicleOwnership` updates. A previous owner
therefore loses the right as soon as the vehicle is transferred. Service centres, police, insurers,
the DMV, inspection stations, dealers and manufacturers keep their registry-wide scope, which is by
design. `isAuthorizedIssuer(issuer, type)` is unchanged: it is still a role-only view, and its NatSpec
now says so.

**Not changed** (author decisions, per the brief): owner consent for service-centre events
(UC2-BR2 / P-6), the `did:mobi` placeholder resolver, and the chain read in `_resolve_ethr`
(VID-R1(b)). The following residual is also out of scope: `attestEvent` still accepts any non-NONE
role, so an OWNER-role address can **attest** (not record) an event on another owner's vehicle. The
attestation is signed and stored with role OWNER, so it is visible and attributable. The fix would be
the same owner check in `attestEvent`, and it would move the attestEvent figure in register #28.

## 3. Tests

| Suite | Before | After |
|---|---|---|
| `npx hardhat test` (1_blockchain-identity) | 353 passing / 23 pending | **361 passing / 23 pending** (+8, none removed or skipped) |
| `python3 -m pytest 2_w3c-ssi-layer -q` | 178 passed | **179 passed** (MOBI tests ran on their own node on 8547, no skips) |
| cv2x-testbed `test_lifecycle_parity`, `test_mobi_vid_verify`, `test_t9_freshness` (node on 8556) | — | 52 passed on the rebuilt artifacts |

New tests (`test/MOBIVID/MOBIVIDRegistry.test.js`):
- "K-15: getVehicleDID emits a well-formed did:ethr": the exact string
  `did:ethr:0x7a69:${addr.toLowerCase()}`, a regex, and the length; a zero-padded address
  (`0x0000…beef`).
- "K-15: OWNER-role events are limited to the vehicle's current owner". The owner of A cannot file
  THEFT_REPORT on B (specific revert reason, B's event count stays 0). The same holds for all five
  OWNER-gated types on B. The owner of A can file all five on A. After a transfer, the previous owner
  gets the specific revert and the buyer succeeds. The role matrix still applies first: OWNER filing
  RECALL on its own vehicle gets "Not authorized to issue this event type". Police and service centre
  can still file on any vehicle.
- Python (`mobi-vid/tests/test_mobi_vid_layer.py::TestBirthCertificate::test_onchain_vehicle_did_resolves_and_matches_python_did`):
  reads `getVehicleDID` from the deployed V2, asserts the exact string, resolves it with
  `did_resolver.DIDResolver` (no error, `didDocument.id` equals the DID), and checks it equals
  `vehicle_did()` case-insensitively.

**Regression check on the old contracts** (sources reverted to `f73e81e`, tests kept): 5 Hardhat tests
fail. Both DID tests fail with the missing `0x`, and three OWNER tests fail with "didn't revert". The
Python DID test also fails. The other three new tests are positive or control cases and pass on both
versions, as intended.

## 4. Gas: before / after

`gas_benchmark.json`, `f73e81e` → `4573ee3`. The conditions are unchanged (solc 0.8.24, optimizer 200
+ viaIR, evm cancun, OZ 5.0.2, Hardhat in-process). **2 of 55 gated cells move**, both in MOBI-VID-V2.

| Standard | Operation | Before | After | Δ | Δ % | Cause |
|---|---|---:|---:|---:|---:|---|
| MOBI-VID-V2 | deployRegistry | 4,025,159 | 4,058,713 | +33,554 | +0.83 | OWNER check + revert string; `":0x"` literal |
| MOBI-VID-V2 | updateAttribute (`recordLifecycleEvent` MAINTENANCE, SERVICE_CENTER) | 306,941 | 307,166 | +225 | +0.07 | warm SLOAD of the issuer role + compare (the non-OWNER path) |

Relative-cost columns that moved: MOBI deploy 8.82× → 8.89×, MOBI update 8.74× → 8.75×. No other
cell or ratio changed. `getVehicleDID` is a view and is not measured.

**Determinism.** `run_gas_stats.py --runs 30` gives `all_deterministic: true`, and
`gas_benchmark_stats.json` is regenerated. A fresh `benchmark_gas.js` + `generate_tables.py` run
compared against the committed JSON with the CI gate's logic reports **55 committed cells, 0 differ,
0 missing, 0 new**. The un-gated `attestEvent` note in the MOBI delegate cell reads 192,683 (it varies
from 192,659 to 192,683; register #28).

**MOBI VID backend sweep** (`191b920`; `mobi_vid_backend_sweep.js` → `generate_mobi_backend_table.py`).
The MOBI-VID-V2 lifecycle event moved from 306,941 to 307,166. The P2-K fixes never regenerated this
table, so this run also picks up their drift: ERC-735 +22 on each of its three operations; CVIN-Combined
birth 51,742 → 51,766 and event 34,666 → 34,690 (+24 dispatch); CVIN-Combined attestation (addClaim)
337,323 → 332,527 (K-6). The fidelity scores (all 5/5 where they were) are unchanged.

**Not regenerated, but affected:**
- `scaling_marginal.*` (Experiment A) still carries MOBI `recordLifecycleEvent` at 306,941 per event.
  The expected change is +225 per event. The slope and R² should not move, because the delta is a
  constant. Re-run `benchmark_scaling.js` if the scaling tables must match the current contracts.
  Experiment B's MOBI lifetime then moves by about +225 per lifecycle event in the profile.
- cv2x-testbed M4 (register #33; testbed build, 0.8.20, no viaIR). I measured the testbed adapter
  directly on both artifacts with the same seed: lifecycle event 306,567 → 306,790 (+223), birth −12
  (calldata spread), transfer unchanged. #33's 255,267 comes from the experiment's own run conditions,
  so expect about +223 when #33 is re-run. The latency verdicts are unaffected.
- The metrics harness (#29/#30/#35) does not deploy MOBIVIDRegistryV2, so it is unaffected.

## 5. Proposed register text

**Row #25 (nine-standard gas):** append:

> … **Re-executed 2026-10-04 after G-M (K-15 MOBI fixes)**: 2 of 55 gated cells move, both in
> MOBI-VID-V2: deploy 4,025,159 → **4,058,713** (+0.8 %), lifecycle event (update column) 306,941 →
> **307,166** (+225; OWNER-role issuers must now own the vehicle). All other standards unchanged;
> 30/30 runs byte-identical; determinism gate 55/55. The previous MOBI values become **S** (an
> OWNER-role address could file theft/accident reports against any vehicle).

**H4 / MOBI backend table row (`mobi_vid_backends.*`, wherever it is cited):** MOBI-VID-V2 lifecycle
event 306,941 → 307,166. CVIN-Combined attestation 337,323 → 332,527 and ERC-735 +22 per operation are
P2-K drift committed here for the first time. The fidelity scores are unchanged.

**Row #33 (M4):** the lifecycle-event gas is **S** until re-run on `d5320b2` or later. The expected
change is about +223 gas. Latency is unaffected.

**Row #26 (scaling):** Experiment A/B MOBI figures are pending a re-run. The expected change is
+225 gas per MOBI lifecycle event, with no change in slope or ranking.

## 6. Checklist status changes to apply (`docs/MOBI_VID_CHECKLIST.md`)

- **VID-R1:** delete defect (a). Replace it with: "`getVehicleDID` returns
  `did:ethr:0x7a69:0x<lowercase address>` and resolves with the repo resolver; it equals the Python
  DID up to EIP-55 case (fixed in `27a2184`; tested by `JS::K-15: getVehicleDID…` and
  `PY::TestBirthCertificate::test_onchain_vehicle_did_resolves_and_matches_python_did`)." The status
  stays **Partial** because of (b): `_resolve_ethr` still does not read the chain, so the controller is
  wrong after birth.
- **UC2-BR2:** in the Code column, replace "(or any `OWNER`-role address)" with "(an `OWNER`-role
  address only on a vehicle it currently owns, since `d5320b2`)". The status stays **Not impl.**:
  service-centre writes still need no owner consent (P-6, author decision).
- **§5.2, last bullet:** replace it with: "The `OWNER` role is now scoped to the vehicle's current
  ERC-1056 owner in `recordLifecycleEvent` (K-15, `d5320b2`). `attestEvent` still accepts any
  authorised role on any vehicle (attestation only, attributable)."
- **§6:** delete "The `getVehicleDID` 0x-prefix bug (R1) should be fixed before any figure or listing
  shows an on-chain DID." (fixed).
- **§7 P-6 → SC-19:** delete "and a global `OWNER` role can write to any vehicle" from the rationale.
  The OWNER part is fixed and the consent part is still pending.
- **Summary table (§6):** no count changes. R1 stays Partial and UC2-BR2 stays Not impl.
