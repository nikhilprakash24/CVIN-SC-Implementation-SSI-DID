# Charter I — Integration and lifecycle

**Status:** draft, 2026-10-22. **Binds:** guide 1.2.1, 1.2.7, 1.2.8 (pre-registered verdicts as they fell).

## 1. What a passing test establishes
That a multi-party sequence (a vehicle's lifecycle, a credential flow, an infrastructure exchange) completes with
the expected end state and that forged or replayed steps inside it are rejected. It does not establish that each
step is individually correct; that is classes F and N.

## 2. Oracle
- **Pre-registered experiments:** the verdict rule written before the run (M4 lifecycle parity, #33; infrastructure
  I1–I5, #44–#48). Verdicts are reported as they fell, including FAIL and "outside band, not falsified".
- **Use cases:** at present the oracle is "the function returns without raising"
  (`sandbox/py-suites/L4-exemplar-interactions/test_lifecycle_use_cases.py` says so in its docstring). Explicit
  end-state checks exist only in some use cases (as-found inventory II.2). This is the weakest oracle in the suite.

## 3. Design
A lifecycle test names its backend. The use cases run on the in-memory centralised registry with the VC layer, not on
a chain backend; they are evidence about the VC layer's integration, not about any on-chain option.

## 4. Falsifiers it carries
| Hypothesis | Refuting observation | Rows |
|---|---|---|
| M4: "writes at least 10× faster centralised" | ratio below 10 | #33 |
| M4: "equal once cached" | cached history slower beyond the declared band (it failed, as registered) | #33 |
| I2 attack battery | any of the registered checks accepted | #45 |

## 5. Threats to validity
| Type | Threat | Control |
|---|---|---|
| Construct | "no exception" is not an end-state oracle | TSR P4-4: one computed end-state assertion per use case |
| External | use cases on one backend | P4-4: second backend through `lifecycle_backends.py` |
| Conclusion | single full run for M4, no stopping rule | stated in #33 |

## 6. Reporting
Verdict tables with the rule quoted; use cases reported as "12 of 12 completed without error", never as "verified".

## 7. Replication
Pre-registered experiments are re-run when their code changes (WM-2 A3b).

## 8. Limits
Until P4-4 lands, no thesis claim rests on the use cases beyond "the VC layer integrates end to end on the
centralised baseline".
