# Charter N — Negative and revert tests

**Status:** draft, 2026-10-22. **Binds:** guide 1.2.5, 1.2.6; review 02 Q-8 (exact reverts).

## 1. What a passing test establishes
That an invalid input or an unauthorised caller is refused, **for the stated reason**, and that the refusal leaves
state unchanged. It does not establish that every invalid input is refused; it covers the inputs listed.

## 2. Oracle
The exact expected revert (custom error with arguments, or the revert string), or the exact Python exception type and
message fragment. "Any revert" and "any exception" are not oracles: a test that passes on an unrelated failure
(an ABI error, a missing fixture) proves nothing (review 02, Q-8; harness classifier, `attackHarness.js`).
A regression test (`*.regression.test.js`) additionally fails on the code before its fix (guide 1.2.5).

## 3. Design
- Pair every negative with a positive control in the same fixture, so the refusal is attributable to the guard.
- After a refusal, read back the state the call would have changed.
- For validation of formats (VIN, DID syntax, chain id), cover the boundary values, not only a far-off invalid one.

## 4. Falsifiers it carries
| Claim | Refuting observation | Where |
|---|---|---|
| G4 authorisation integrity (`docs/THREAT_MODEL.md`) | a role acts beyond its authority without a revert | per-option N tests; D54 regression in `MOBIVID/attestEventRegression.test.js` |
| "a fixed defect stays fixed" (`docs/DEFECT_LOG.md`) | a regression test passes on the pre-fix code | the mutant or old-code run recorded in the fix's report |

## 5. Threats to validity
| Type | Threat | Control |
|---|---|---|
| Construct | a revert for the wrong reason counted as a defence | exact expected revert required |
| Internal | the positive control is missing, so a broken fixture reads as a defence | pair rule (§3) |
| Conclusion | negatives cover chosen inputs only | boundary values; property-style generation is future work |

## 6. Reporting
Counts per subject (`coverage_matrix.md`). A defect found by a negative test enters `docs/DEFECT_LOG.md` before it is fixed.

## 7. Replication
CI on every push.

## 8. Limits
Several older per-option suites (ERC-721 legacy files) assert truthiness rather than exact values; they are
counted, and listed for strengthening, not relied on for a claim.
