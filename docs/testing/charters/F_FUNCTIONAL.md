# Charter F — Functional tests

**Status:** draft, 2026-10-22. **Binds:** guide 1.2.5, 1.2.6.

## 1. What a passing test establishes
That one operation of one implementation option does what its specification or the option's manifest says, on
valid input, in the stated environment. It does **not** establish that the operation is secure, conformant to an
external standard, cheap, or fast; those are classes A, W, G and L.

## 2. Oracle
An exact expected state or return value read back after the call: an owner, a resolved attribute, an event with its
arguments, a balance. A test that only checks "did not revert" is a smoke test and is labelled as such in its title or
moved to class D. A demo step (`sandbox/options/*/demos/*.js`) counts as functional evidence only when it asserts a
read-back; demo steps flagged OBSERVATION are not evidence of correctness (`coverage_matrix.md`, T*).

## 3. Design
- One subject per test. A cross-option claim needs the same test on every option (the L1 mechanism layer), not
  a per-option test repeated by hand.
- Fresh state per test (`loadFixture` or a reset); no order dependence.
- Incidental randomness seeded (guide 1.1.10; `CVIN_SEED`).
- Every functional test of a privileged operation has a class-N partner that shows the operation refuses the
  wrong caller.

## 4. Falsifiers it carries
| Hypothesis or claim | Observation that refutes it | Where it would show |
|---|---|---|
| H4 (MOBI VID realisable across backends) | a lifecycle event the manifest declares implemented has no passing functional test on that backend | L1 cells, `coverage_matrix.md` G cells |
| "n/a means no primitive" (TSR S5) | a functional test passes for a cell a manifest declares not applicable | the builder's manifest/demo mismatch list |

## 5. Threats to validity
| Type | Threat | Control |
|---|---|---|
| Construct | per-option tests are written against each contract's own vocabulary, so "the same function" differs between options | cross-option functional claims come only from the L1 mechanism layer and the harness catalogue |
| Internal | adapter or test realises an operation with a cheaper path than intended | harness adapter conformance (class W) and the realisation tables in `docs/CVIN-DATA-COLLECTION-FRAMEWORK.md` §2 |
| External | representative implementations (minimal EntryPoint, LSP8 stand-in) | manifest notes; stated with every cross-option result |
| Coverage | ERC-725 has no per-option unit file; its functional evidence is the L1 layer, the harness and the demos | `coverage_matrix.md`, unit table |

## 6. Reporting
Counted in the register (`class: F`); reported as counts per subject, never as a percentage of "functions tested"
without a denominator from the manifests.

## 7. Replication
Re-run in CI on every push; no host dependence expected.

## 8. Limits
The unit-test mapping is rule-based (`unit_rules.yaml`); a hand-graded audit sample of 50 entries found 43 with the right function before three
substring fixes to the rules (testing-suite replan, staged record). Function counts are indicative until the author reviews the rules.
