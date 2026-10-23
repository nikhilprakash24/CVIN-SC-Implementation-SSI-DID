# After-Action Report 36 — Mutation Probes for the C1 and C2 Tests

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened:** 2026-10-23, after report 35 closed at `55bf410` (CI 11/11 green on `09c5363`). **Brief:** the author's
"all" for `docs/planning/UNBLOCKED_WORK_2026-10-23.md`; this is item U4.

## 1. Plan
| Step | Work | Gate |
|---|---|---|
| M1 | `2_w3c-ssi-layer/did-resolution/mutation/mutate_resolver_chain.py`: nine mutants of the chain-reading did:ethr resolver (expiry, owner change, deactivation, `DIDRevoked`, sigAuth, event order, head time, registry lookup), each must be killed by the resolver's chain tests and the two MOBI resolution tests | every mutant killed, or each survivor reported as a finding about test strength |
| M2 | `1_blockchain-identity/test/L2-identity-system/per-option/MOBIVID/mutate_d54.sh`: eight mutants of the D54 fix (the consent rule, the duplicate rule, the stored delegation, revocation, expiry, revoked identity), each must be killed by `attestEventRegression.test.js` | as M1 |
| R | Both probes in CI; records; CI | CI green on the closing commit |

The resolver the mutants target is the merged implementation (`ERC1056Reader`, from the clone lineage, merged in PR
#3), not the one report 21 wrote; the C1 tests run against it.

## 2. Execution log
- 2026-10-23 — report opened.
