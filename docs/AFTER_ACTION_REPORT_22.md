# After-Action Report 22 — WM-2 C2: Attestation Restricted to the Vehicle's Owner and Delegates (D54)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-17, after report 21 closed at `916f349` (CI 8/8 green on `f61ed34`); closed at the end of this pass
**Brief (the author, 2026-10-17):** continue (WM-2 C2, then the hand-off and the check brief for the other model).

## 1. Finding that shapes the step
D54 (WM-1 audit U-F10): any role-holder can attest any vehicle's lifecycle event, and the same attester can attest
twice. The plan's fix is "restrict `attestEvent` to the vehicle's owner and delegates". **The MOBI `ERC1056Registry`
stores no delegations.** Its `addDelegate` and `revokeDelegate` only emit `DIDDelegateChanged`; it has no
`delegates` mapping and no `validDelegate`, unlike the canonical ERC-1056 `EthereumDIDRegistry`. No contract can
therefore ask whether an address is a vehicle's delegate, and the plan's fix cannot be written against the current
registry.

## 2. Plan
| Step | Work | Owner | Gate |
|---|---|---|---|
| C2-a | MOBI `ERC1056Registry`: store delegations as the canonical registry does (`delegates[identity][type][delegate] = validTo`; revocation sets it to `block.timestamp`) and add `validDelegate`. `MOBIVIDRegistryV2.attestEvent`: the attester must hold a role (as now) **and** be the vehicle's current owner or a valid `veriKey` delegate of it; a second attestation by the same attester of the same event reverts. The testbed's identical copies change with them, and its tracked artifacts are recompiled | contracts engineer; security specialist | regression tests that fail on the old code: a role-holder that is not owner or delegate is rejected; a duplicate is rejected; a revoked or expired delegation is rejected; the owner and a delegate are accepted. Every existing test passes after its callers set up the delegation the new rule needs |
| C2-b | Callers: tests, scripts, sandbox adapter and demos, the Python MOBI layer | contracts engineer | the full Hardhat tree, the Python layers and the demos pass |
| C2-c | Gas re-runs of record for the cells that move (MOBI `addDelegate` / `revokeDelegate`, `attestEvent`), through the registered producers; registry rows re-stated with old values kept as history | measurement methodologist | each moved number re-registered from its run, or stated unchanged |
| R | Records, grand run last, CI; then the hand-off and the check brief for the other model | orchestrator | CI green on the closing commit |

**Defaults (the author may overturn).**
| # | Decision | Default |
|---|---|---|
| C2-d1 | Which fix | the plan's (owner and delegates), not review-02's narrower one (the owner check for the OWNER role only), which leaves every other role able to attest any vehicle and so does not close D54 |
| C2-d2 | How delegation is checked | store delegations in the MOBI registry, as the canonical registry does; not a separate attester list in `MOBIVIDRegistryV2`, which would be a second, non-standard consent mechanism |
| C2-d3 | Delegate type | `veriKey`. A `veriKey` delegate appears in the DID document's `assertionMethod`, which is what an attestation is |
| C2-d4 | Role still required | yes. The attestation records the attester's role, and the role list is the existing authority model; the owner's delegation adds consent, it does not replace authority |
| C2-d5 | Cost | storing a delegation adds a storage write to every MOBI `addDelegate`, so cells beyond `attestEvent` move. They are re-run and stated as they fall |

## 3. Execution log
- 2026-10-17 — report opened.
- **C2-a, contracts.** MOBI `ERC1056Registry` stores `delegates[identity][type][delegate] = validTo` in `addDelegate`.
  `revokeDelegate` sets it to `block.timestamp`, and a new `validDelegate` returns false for a revoked identity.
  `MOBIVIDRegistryV2.attestEvent` keeps the role check and adds two rules: the attester must be `identityOwner(vehicle)`
  or a valid `veriKey` delegate, and `hasAttested[eventId][attester]` blocks a second attestation. The consent and
  duplicate checks run before the signature check (cheap checks first).
- **The testbed copies are not changed (a declared deviation).** `cv2x-testbed/contracts/MOBIVIDRegistryV2.sol` was
  identical to the main project's, but it compiles against the testbed's own `ERC1056Registry`, a different contract
  with `updateVehicleKey` and `getIdentityInfo`. Giving that registry delegate storage would change its bytecode and
  so #22's deploy gas. No testbed code calls `attestEvent`, and the testbed's MOBI tests already load the main
  project's artifacts. The copies now differ, logged as **N-25**: sync them at A3b, when the testbed's results are
  re-run anyway.
- **C2-a, tests.** Four D54 tests in `attestEventRegression.test.js`: a role-holder without consent is rejected; a
  duplicate is rejected; a revoked and an expired delegation are rejected; the owner holding a role is accepted. On the
  old contracts, written from git and checked by grep, 3 of the 4 fail. The owner test passes on both, because it pins
  behaviour that must not change. The fixed-path gas pin is re-pinned: **attestEvent execution gas 169,361 → 198,694**
  (+29,333: one new storage write and four cold reads), 0 spread over 6 event ids. Total gas is 222,058–222,082 from
  calldata zero bytes.
- **C2-b, callers.**
  - **Tests:** three Hardhat fixtures now have the owner delegate the attester. The security scenario's control, a
    dealer attesting, needs the owner's delegation; its attack, an attester with no role, is still refused by the role
    check with the same reason, so the matrix's verdict does not change. One test was reordered: its valid
    attestation now comes after the bad-signature cases, which would otherwise hit "Already attested" first.
  - **Python MOBI layer:** the client gained `add_delegate`, and the lifecycle fixture delegates the DMV.
  - **Demos:**
    - `claims.js`: the owner delegates three attesters, and a new step shows a role-holder without consent being
      refused. "Attest twice" is now an expected revert (it was an observation). The malformed-signature step moved
      to an attester that has not yet attested.
    - `keys-delegates.js`: its assertion that `validDelegate` does not exist is now the opposite. Two notes that
      said delegations store nothing were corrected, and a step checks the stored state against the log replay.
    - `lifecycle-history.js`: the current owner, the buyer after the sale, delegates the station. The ERC-1056 event
      chain is now three links long.
  - **Producers** (`benchmark_gas.js`, `mobi_vid_backend_sweep.js`): the owner's delegation is uncounted setup, as
    issuer authorisation already is.
- **C2-b, records.** D54 is marked fixed. The threat model's G4 note and the MOBI sandbox README are updated. The
  feature matrix was regenerated (MOBI gains `delegates`, `validDelegate` and `hasAttested`). Report 20's SEC-05 is
  no longer pending, and its TDP-002, TDP-005 and TDP-006 were regenerated with its own generators. The dashboard and
  presentation were regenerated (Medium defects: 17 fixed, 9 open).
- **Results so far:** Hardhat **541** (537 + 4); Python MOBI 43; all 11 MOBI demos pass; 13 document checks pass.
- **C2-c, re-runs of record** at `92cc4d5` (clean tree, stamped): `benchmark_gas.js` with `generate_tables.py`,
  `mobi_vid_backend_sweep.js`, `benchmark_scaling.js` and `security_scenarios.js`. Every changed field was compared
  with the committed results. **Only MOBI-VID-V2 cells move:**

  | Cell | Before | After | Change | Why |
  |---|---:|---:|---:|---|
  | deploy | 4,225,285 | 4,366,383 | +141,098 | larger contract |
  | addDelegate | 35,321 | 57,649 | +22,328 | the stored delegation |
  | third-party attestation (sweep) | 192,749 | 222,082 | +29,333 | consent and duplicate checks |
  | create / birth | 299,143 | 299,165 | +22 | dispatch offset (new selectors) |
  | update (`recordLifecycleEvent`), first / marginal | 307,210 / 255,910 | 307,254 / 255,954 | +44 | dispatch offset |
  | revoke | 75,382 | 75,404 | +22 | dispatch offset |
  | transfer | 200,089 | 200,155 | +66 | dispatch offset |
  | 15-year lifetime | 9,856,260 | 9,858,020 | +1,760 | the offsets above |

  The lifetime ranking is unchanged. The on-chain security results did not change in any number.
- **A slip in my own comparison, caught.** My first diff script skipped any key containing "date", to drop
  timestamps. That also skipped `updateAttribute`, which contains "date", so the +44 on the update cell went
  unreported, and my first #25 note missed it. I found it when chapter 5's 307,210 did not match the file. The
  re-diff skips exact key names only, and the table above is from it.
- **Comparative claims re-checked against the new values; all still hold.**
  - Chapter 5 says event-log backends are "roughly 6–9× cheaper" than MOBI: 5.8× and 8.9×.
  - It calls `attestEvent` "the cheapest native attestation": 222,082 is below 295,289 (ERC-735) and 336,896
    (CVIN-Combined). The sentence now says "still", and names the C2 check.
  - CVIN-Combined at f = 1 (9.84 M) still dominates MOBI (9.86 M) over a lifetime.
- **C2-c, records.**
  - **Register:** #28's claim re-stated from the new pin (198,694; total 222,058–222,082), with 169,295 and 169,361
    kept as history. #25 and #26 have dated notes listing every moved cell.
  - **Stale-figure list:** eleven superseded values added. The checker found 21 quotes in five files: chapter 5,
    chapter 6, README, CAPABILITIES and QUICKSTART. Each was updated, history lines with an arrow to the new value.
  - **Generated documents:** card #28's caption now says 198,694; it had quoted the review-2 value, which the check
    allowed because the number is still in the row as history. The dashboard, presentation, result cards and DWG-002
    were regenerated. All 13 document checks pass.
- **Hand-off and check brief.** `docs/HANDOFF_2026-10-17.md` covers where things stand, passes 16–22 with their
  closing commits, the rules that matter most, open decisions, and N-24 and N-25. It names no model.
  `docs/milestones/check_passes_16-22/CHECK_BRIEF.md` has 13 claims (K1–K13), each with its command, expected result
  and falsifier. It names the places where judgement was used, and gives a findings format. Every path it names was
  checked to exist. K4's command was corrected before commit: `infrastructure_gas.js` writes to the tracked results,
  so the brief now says to diff and restore them.
