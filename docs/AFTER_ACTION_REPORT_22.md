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
