# Charter A — Adversarial tests

**Status:** draft, 2026-10-22. **Binds:** `docs/THREAT_MODEL.md` (A1–A4, G1–G8, T1–T4); guide 1.2.4, 1.3.13.

## 1. What a passing test establishes
That a named attack, by a named adversary class, against a named security goal, was rejected on that option, and that
the honest version of the same action succeeded (differential control). It does not establish that the option is
"secure": only the registered attacks were tried (guide 1.3.13: "the 13 registered attacks were rejected").

## 2. Oracle
The strict security harness classifies each cell as DEFENDED only when the attack reverts with the documented
expected reason and the control succeeds; otherwise VULNERABLE, UNEXPECTED-REVERT or FAILED-TO-RUN, or N/A with a
reason (`test/L2-identity-system/security/attackHarness.js`). Off-chain attacks (VC/VP replay, holder binding,
tampering, malleability) assert the exact rejection reason in the Python suites. Results of record: #28.

## 3. Design
- Each attack is traceable to an adversary (A1 network, A2 malicious registered party, A3 key compromise, A4 passive
  observer) and a goal (G1–G8).
- N/A cells state why the primitive is absent; an N/A cell is a finding, not a pass.
- Every attack has a mutant or old-code run showing it would succeed without the guard (guide 1.3.11).

## 4. Falsifiers it carries
| Hypothesis | Refuting observation | Where |
|---|---|---|
| H5 (no option dominates on security) | one option DEFENDED on every applicable cell where every other option fails one | `attack_results.json`, `security_matrix.json` |
| G3 replay resistance | a captured signed operation accepted out of context | signatureReplay cells; v2v-path and infrastructure replay tests (#45) |
| G7 PII confidentiality | VIN recoverable from on-chain state | on-chain footprint (#49); VIN cipher tests |

## 5. Threats to validity
| Type | Threat | Control |
|---|---|---|
| Construct | the six-attack grid under-samples the threat model (no front-running, griefing, DoS on event walks) | listed as gaps; paper intake asks for further attack ideas |
| Internal | representative implementations lack production guards | stated per cell |
| External | Hardhat local chain; no mempool adversary | condition M1 stated with every security claim |
| Coverage | ERC-725xy is not in the strict harness grid | gap in `coverage_matrix.md`; TSR P4-1 |

## 6. Reporting
Cell table option × attack, with outcome and expected reason; counts as "k of n applicable cells defended", never
as a percentage of security.

## 7. Replication
CI; the security matrix is produced through the promote step (WM-2 A4) so a test run does not rewrite it.

## 8. Limits
Lens 2 cells marked `*` are reasoned, not executed, and are reported separately from lens 1.
