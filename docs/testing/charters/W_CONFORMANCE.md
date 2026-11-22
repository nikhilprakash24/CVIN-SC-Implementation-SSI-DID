# Charter W — Conformance tests

**Status:** draft, 2026-10-22. **Binds:** guide 1.2.2 ("compliant" needs clause-level evidence).

## 1. What a passing test establishes
That one normative statement of an external text (W3C DID Core, VC Data Model 2.0, the public MOBI VID texts, an ERC)
or of the project's adapter contract holds for the implementation. It does not establish conformance to the whole
text; a score is the fraction of the statements checked.

## 2. Oracle
- **External suite:** the W3C DID test suite's own assertions (#24). Both denominators are reported, with the
  matched-pair table, because the generated test count depends on which keys the resolver emits.
- **Internal checker:** each check executes the resolver or VC stack and returns PASS, PARTIAL or FAIL (#4). It is
  self-written and checks document structure for DID Core; it is labelled internal and structural.
- **Adapter conformance:** every catalogue operation leaves the identity in the expected state, or is declared not
  supported (harness gate).
- **MOBI clauses:** `docs/MOBI_VID_CHECKLIST.md`, clause by clause.

## 3. Design
Each check names the clause it tests. A check that cannot fail (a hard-coded PASS, a printed percentage) is not
conformance evidence and is excluded (see the exclusion list in `unit_rules.yaml`).

## 4. Falsifiers it carries
| Hypothesis | Refuting observation | Where |
|---|---|---|
| H2 (≥ 90 % W3C conformance achievable) | external-suite pass fraction below the threshold on either denominator, or the internal score below it | #24, #4 |
| "MOBI VID compliant" | any MUST clause not met | checklist (the thesis wording is "inspired by", per guide 1.2.2) |

## 5. Threats to validity
| Type | Threat | Control |
|---|---|---|
| Construct | the internal checker is self-scored and structural | reported beside the external suite; labelled |
| Construct | denominator moves with resolver output | both denominators and matched pairs |
| Internal | checker drift against the spec (the 7.1.2 correction, #4) | corrections disclosed in the row |
| External | conformance of synthesised documents differs from on-chain resolution | on-chain resolution set reported separately (#24) |

## 6. Reporting
Fraction with numerator, denominator and the instrument; never a bare percentage.

## 7. Replication
Internal checker in CI with a floor; external suite run manually with dated reports in `docs/conformance/reports/`.

## 8. Limits
VC Data Model coverage depends on the internal checker only; no external VC suite run exists.
