# Phase 3 Examiner Pass — Objections and Dispositions

**Produced:** 2026-10-31. Blind examiner, checked against EIP-3643 / T-REX / ERC-1404/CMTAT / a16z RWA allowlist hooks.
**Verdict:** **not defensible as-is.** The load-bearing "absolute absence" claim is falsified by ERC-3643's own
on-chain `transfer()` gate. The contribution survives as a **new workload class**, not a "missing benchmark."

## Disposition key: REVISION (handled in the coherent rewrite) · FIXED (mechanical) · CONCEDE (accept + restate)

| # | Severity | Objection | Disposition |
|---|---|---|---|
| **F1** | FATAL | "in-transaction identity-gating absent from every artefact without exception" is **false** — ERC-3643 `transfer()` runs `isVerified(_to)` + `canTransfer(from,to,amount)` on-chain before moving value (the IDTx definition verbatim), shipped in the public T-REX reference suite, ~$28bn deployed; the absence result is an artefact of profiling ERC-3643 only through Frutuoso26 (which measured no transfers) | **REVISION.** Profile the T-REX reference transfer suite + ERC-1404/CMTAT directly. **Retract "without exception."** Narrow to the only defensible claim: *"no artefact that is also a complete A1–A5 benchmark has packaged an on-chain identity-gated-transfer workload"* — explicitly conceding the mechanism, the on-chain gate, and runnable harnesses already exist. Back-propagate to `p1/BENCHMARK_GAP.md` and `p1/THESIS_DRAFT.md`. |
| **M2** | MAJOR | The gap is carried entirely by "Id-gate," the thesis's own non-axis; the five axes do no gap-defining work → Phase-1 gerrymandering re-dressed | **CONCEDE + REVISION.** State plainly the contribution is a **new workload class**, not a missing benchmark; demote the "unoccupied cell" framing to motivation. |
| **M3** | MAJOR | BLOCKBENCH/DIABLO/Caliper ✗ "identity-blind" conflates "ships no identity workload" with "cannot host one" — Caliper is bring-your-own-workload | **FIXED.** Split "ships identity workload" from "can host one"; note v0's W3 is implementable as a Caliper workload module. |
| **M4** | MAJOR | A5 (independent reproduction) is non-standard (not a Gray/TPC criterion), manufactures the universal gap, and is then waived for v0 — used to fail others, excused for us | **CONCEDE + REVISION.** Demote A5 to a *maturity* property applied symmetrically to v0; add the Gray/TPC criteria (relevance, portability, scalability, simplicity) or argue their omission. |
| **M5** | MAJOR | Silent scoring drift PROFILES→V0 (NIST A2 ◐→✓; Rubric A5 ✗→n/a; DID/VC/DIF collapsed to A5 ✓ hiding VC/DIF ◐; Caliper collapsed hiding A1 ✗) | **FIXED.** Reconcile the two tables cell-by-cell with a changelog; keep collapsed families disaggregated. |
| **M6** | MAJOR | v0 is circular — workload, admission rule, metrics all in-house | **REVISION.** Anchor at least the workload or admission rule to an external referent (ERC-3643 compliance semantics; EUDI conformance scenarios). |
| **M7** | MAJOR | §3.3.2 admission admits everyone (implement OR justified-n-a, no reject) → not an A2 gate | **CONCEDE.** Define a genuine reject condition, or concede v0 is A1/A3/A4(partial) with **A2 and A5 open** and restate the §3.4 claim. |
| **m8** | MINOR | W3 tier rests on emit-only prototype + superseded #32/#37 | **FIXED.** Label W3 "specified, not yet measured"; do not count toward "singly run." |
| **m9** | MINOR | Cross-paradigm absence claim outruns EVM-only scope | **FIXED.** Scope the absence claim to EVM (now moot given F1 narrowing, but state it). |
| **m10** | MINOR | EUDI reproduction cells rest on abstract-only Sokolov26 | **FIXED.** Mark EUDI reproduction cells provisional. |

**Single most important fix (examiner):** profile T-REX/ERC-3643 + ERC-1404/CMTAT directly; narrow to "no complete
A1–A5 benchmark has packaged an on-chain identity-gated-transfer workload"; concede the mechanism and harnesses exist.
The honest contribution: a **new workload class** (the IDTx taxonomy as a measurable workload) + the thesis's measured
substrate breadth — not the discovery of an empty benchmark cell.
