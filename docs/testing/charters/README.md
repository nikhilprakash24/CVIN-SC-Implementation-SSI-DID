# Test-Family Charters

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-22 (testing-suite replan §4, TSR Phase 6).
**Status:** drafts for the author's review, except classes G and L, which are generated and of record.
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`; `docs/MEASUREMENT_CONDITIONS.md` for every number; TSR plan §9.2 template.

A charter says, for one class of test, what a passing test establishes and what it cannot, how pass and fail are
computed, which observation would refute the hypotheses the class bears on, and what threatens the conclusion.
It quotes no measured number of its own (design parameters and published budgets excepted): where a measured figure matters it names the register row (`#nn`) that holds it.
`check_charters.py` fails if a charter cites a row that does not exist.

| Class | Name | Charter | Where the tests are (register `class`) |
|---|---|---|---|
| F | Functional | `F_FUNCTIONAL.md` | per-option tests, L1 mechanisms, demos, Python suites |
| N | Negative / revert | `N_NEGATIVE.md` | per-option and regression tests, Python negative suites |
| A | Adversarial | `A_ADVERSARIAL.md` | strict security harness, review-02 PoC suites, infrastructure verifier |
| W | Conformance | `W_CONFORMANCE.md` | internal checker, external DID suite, resolver shape tests, adapter conformance |
| G | Gas | `../GAS_CHARTER.md` (generated, WM-2 B2) | L1 gas cells, harness, nine-standard table |
| L | Latency | `../LATENCY_CHARTER.md` (generated, WM-2 B3) | freshness, PKI vs ERC-1056, V2V, HTTP condition |
| S | Scale | `S_SCALE.md` | scaling experiments A–D, harness scale scenario |
| D | Determinism and run identity | `D_DETERMINISM.md` | seeding, stamps, promote, gas determinism gate |
| I | Integration and lifecycle | `I_INTEGRATION.md` | use cases, lifecycle parity, infrastructure I1–I5 |
| Q | Analysis | `Q_ANALYSIS.md` | analysis layer, dominance, rubric, feature matrix |

Counts of tests per subject and class: `../coverage_matrix.md` (generated).
