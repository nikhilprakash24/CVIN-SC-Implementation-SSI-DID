# Follow-up stream F-C: security matrix, S-1 theft cell, register #1/#2, M3

**Input:** `docs/review02/AAR_REVIEW2_04.md` (stream F-C), `docs/review02/PASS2_REREVIEW.md`
(R2-L2, R2-L5), `docs/review02/PASS2_K.md`, register rows #1, #2, #19 and #28, and
`docs/PLAN_MOBI_SUMO.md` M3.
**Base:** `d2e6a58`. **Toolchain:** Hardhat 2.28.6 (lockfile), solc 0.8.24, viaIR, optimizer 200,
evm cancun, OZ 5.0.2.
**Gates:** the Hardhat suite has **304 passing, 6 pending** (was 302 / 6; +2 tests, none
removed, skipped or weakened). `python3 -m pytest 2_w3c-ssi-layer cv2x-testbed/tests` gives
**239 passed, 19 skipped**. All 19 skips need a node at :8545, which CI provides.

| Item | Commit |
|---|---|
| 1. Sybil-cost gas regenerated; strict DEFENDED legend | `bdc0b9f` |
| 2. S-1 thief-with-own-DID cell plus its pytest | `980c8c1` |
| 1b. Stale hard-coded gas removed from mechanism strings; on-chain JSON regenerated | `5717cd5` |
| 3. Register #1/#2 re-measured | no commit (see §3) |
| 4. M3 attestEvent regression test with pinned gas | `14bc80a` |

## 1. Security matrix (R2-L2)

**How the files are produced.**
- `attack_scenarios.py` runs the off-chain VC attacks.
- It then runs `npx hardhat run scripts/security_scenarios.js`, which writes `onchain_security.json`.
- It reads `createIdentity.gasUsed` from `4_comparison-framework/results/gas_benchmark.json` as
  the Sybil-cost proxy.
- From these it writes `security_matrix.json` and `security_comparison.tex`.
- `generate_attack_tables.py` turns `attack_results.json` (from the Hardhat security test) into
  `attack_results.{csv,tex}`.
- **`security_matrix.csv` had no producer.** The committed file was one stray header row
  (from `e06a976`). `attack_scenarios.py` now writes it: one outcome per category, `*` marks a
  reasoned cell, plus a `sybil_cost_proxy_gas` column.

**Old → new: `cost_proxy_gas` in the sybil cell (and the matching sentence in its evidence).**

| Standard | Old (July run) | New (`gas_benchmark.json`) | Δ |
|---|---:|---:|---:|
| ERC-1056 | 52,612 | 52,594 | −18 |
| ERC-721 | 542,429 | 542,378 | −51 |
| ERC-725 | 528,647 | 519,384 | −9,263 |
| ERC-735 | 1,404,108 | 1,535,776 | +131,668 |
| ERC-1155 | 103,905 | 103,913 | +8 |
| ERC-4337 | 768,204 | 759,088 | −9,116 |
| LSP8 | 149,352 | 149,615 | +263 |
| MOBI-VID-V2 | 298,923 | 299,143 | +220 |
| CVIN-Combined | 52,178 | 52,216 | +38 |

All of these deltas are already in the benchmark (cancun re-run and the review-02 fixes). None
is new here.

**Other changed content.**
- `scripts/security_scenarios.js` (and therefore `onchain_security.json` /
  `security_matrix.json`): four `mechanism` strings had hard-coded July approximations. They now
  point to the exact `cost_proxy_gas` instead:
  - ERC-725 "~529k"
  - ERC-735 "~1.40M"
  - ERC-4337 "~768k"
  - MOBI "highest per-identity cost (~299k gas)". This one was also wrong: ERC-721 and ERC-735
    cost more.
- `security-analysis/README.md`: ERC-725 ~529k → ~519k, ERC-735 ~1.40M → ~1.54M.
- The off-chain evidence strings contain fresh random addresses on every run. That is
  unavoidable, because the keys are generated per run.
- `security_comparison.tex` is **byte-identical**, so it was not committed.
- **`attack_results.{csv,tex}`.** The legend is now "DEFENDED = malicious tx reverted with the
  documented expected reason/custom error of the named defense", with UNEXPECTED-REVERT and
  FAILED-TO-RUN added. The TeX caption says the same. The docstring and display maps in
  `generate_attack_tables.py` were updated to match. The "measured" date was 2026-07-14 and is
  now 2026-07-19, which matches `attack_results.json`; the old CSV/TeX were older than their
  input.

**Outcomes: unchanged.** All 54 matrix cells (9 standards × 6 categories) and the W3C row have
the same outcome and method as before. The flat matrix is unchanged too: 43/43 DEFENDED, 11 N/A.

**Not edited (flagged).** `CAPABILITIES.md` §gas table and prose still carry the July create
gas (R2-L2 names it). `QUICKSTART.md:180`, `INVENTORY.md:251` and the chapter-5 tables do too.
These belong to the author's chapter and doc pass.

## 2. S-1 identity-theft cell (R2-L5)

`attack_scenarios.identity_theft_attacks()` runs both thieves against the verifier:
- **(a) same DID, wrong key (kept).** The verifier rejects it at `vp_signature`.
- **(b) own DID (new).** The thief takes the victim's credential, makes its own
  `HolderWallet.with_ethr_did()` and presents the credential with a VP it signs correctly. The VP
  proof is valid, and only the S-1 check rejects it:
  `[holder_binding] presentation holder did:ethr:…(thief) is not the credential subject [victim]`.

The cell is DEFENDED only if both thieves are rejected. Both variants are stored under
`identity_theft.variants`. The outcome is unchanged (DEFENDED).

**Test.** `cv2x-testbed/tests/test_attack_scenarios_identity_theft.py` has 4 tests:
- the genuine-holder control;
- (b) is rejected by `holder_binding` while its VP proof is valid;
- (a) is rejected by the VP proof;
- the full matrix cell.

It is collected by the existing CI command `python -m pytest 2_w3c-ssi-layer cv2x-testbed/tests`
(`w3c-compliance.yml`), so **no CI change is needed**. **Mutation check:** with
`_check_holder_binding` forced to pass, 2 of the 4 tests fail.

## 3. Register #1 / #2 re-measured

**How the figures are produced.** `results_snapshot.json` is **hand-assembled** from the test
logs. `make_verification_figure.py` only *reads* it, and no script writes it.
- #1 comes from the `console.log` in `test/ERC1056/CVINVehicleDIDRegistry.test.js:81`.
- #2 comes from `test/ERC1056/EthereumDIDRegistry.test.js:259/271/285`.

Both run during `npx hardhat test`. The gas reporter is not involved.

**Re-measurement on this tree.** Run as the full suite and as the two files alone; both runs give
identical figures.

| Row | Operation | Old | New | Δ |
|---|---|---:|---:|---:|
| #1 | createVehicleDID | 78,068 | **78,090** | **+22** |
| #2 | changeOwner | 68,854 | 68,854 | 0 |
| #2 | addDelegate | 72,219 | 72,219 | 0 |
| #2 | setAttribute | 51,126 | 51,126 | 0 |

The +22 is the K-1 selector-set shift in `CVINVehicleDIDRegistry` dispatch. It matches the
harness C1 move (76,786 → 76,808, row #29), as predicted. #2 runs on the bare
`EthereumDIDRegistry`, whose selectors did not change, so 0 is expected. Because no script
produces the snapshot, it was **not** edited; it still documents commit `708302a`.

## 4. M3: attestEvent regression

**Was it already covered?** Partly.
- `test/MOBIVID/MOBIVIDRegistry.test.js` already asserted forged, garbage and replayed
  signatures revert.
- `test/security/securityScenarios.test.js:1184` covers the unauthorized attester.
- **Nothing pinned gas.** The existing test only logs it.

**Added: `test/MOBIVID/attestEventRegression.test.js`.**
1. **Vulnerable path closed.** A role-holder (dmv) submits another attester's valid signature, a
   placeholder blob or a random 65-byte signature. Each reverts with its expected reason, and
   no attestation is stored. The genuine attester's signature is accepted (control).
2. **Gas pin.** `receipt.gasUsed` is not deterministic. `eventId` depends on
   `block.timestamp`, the signature depends on `eventId` and the registry address, and both are
   calldata (4 or 16 gas per byte). Over six event ids it measured 192,659–192,683, in
   12-gas steps. The test therefore pins **execution gas = gasUsed − 21,000 − calldataGas(tx.data)
   = 169,295 ± 0** for every event id, and checks `gasUsed` against that formula exactly.

**Mutation check:** with the `recovered == msg.sender` require removed, both tests fail. CI runs
it through `npx hardhat test`.

**Compared with 192,718.** On the current build the largest possible `gasUsed` is 169,295 +
21,000 + 2,388 (all-non-zero calldata) = **192,683**. That is below 192,718, so the register
figure cannot recur. Swapping the MOBI sources back to `c376c2f` (pre-K-3/K-4) still gives
169,295, so the source changes since then are not the cause. The run of record
(`gas_benchmark.json`) shows 192,671. The 35–59 gas difference from the July measurement is
therefore a build/toolchain difference (compare §5.E). It was not attributed further.

## 5. Proposed register text

- **#1:** "createVehicleDID **78,090** gas (test-suite context, `CVINVehicleDIDRegistry.test.js`,
  re-measured 2026-10-04 on the post-review-02 tree, Hardhat 2.28.6). Was 78,068 at `708302a`;
  the +22 is K-1's selector-set shift in dispatch, the same as harness C1 76,786 → 76,808 (#29).
  `results_snapshot.json` is a hand-assembled snapshot of `708302a` and keeps 78,068." **V**.
- **#2:** "changeOwner 68,854 · addDelegate 72,219 · setAttribute 51,126. Re-measured
  2026-10-04: unchanged (the bare ERC-1056 registry's selectors did not move)." **V**.
- **#19:** unchanged status (**S**, superseded). Append: "The superseding matrix
  (`security_matrix.json`) was regenerated 2026-10-04 with current Sybil-cost gas. Outcomes are
  unchanged, and the W3C identity-theft cell now also executes the S-1 own-DID thief."
- **#28:** "Security: 43/43 attacks defended. DEFENDED = reverted with the documented expected
  reason (strict harness, Q-8). attestEvent found-and-fixed 121,110 → 192,718 gas (July build).
  On the current build the fixed path costs **169,295 execution gas ± 0** (pinned in
  `test/MOBIVID/attestEventRegression.test.js`, M3). `receipt.gasUsed` is 192,659–192,683
  depending on calldata zero bytes (run of record: 192,671). 192,718 is not reachable on this
  build." **V**.
