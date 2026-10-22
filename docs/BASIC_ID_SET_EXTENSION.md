# The Basic Digital-ID Set and Its Extension

> *Lineage merge note (2026-10-21, PR #3): register rows from the clone lineage were renumbered on the merged trunk (#40 is #53 and #41 is #54).*


**Author:** Nikhil Prakash (MASc, UBC ECE) — nikhil.prakash1995@gmail.com
**Date:** 2026-10-15
**Purpose:** state precisely how the measurement catalogue of this repository (`docs/CVIN-DATA-COLLECTION-FRAMEWORK.md`, 18 operations × 10 substrates) **extends** the programme's *basic digital-ID set* — the canonical sandbox's `IMinimalSSI` F1–F12 — and propose the reconciliation the onboarding stream left open (`TEST_ONBOARDING.md`: "this repo's suite + W3C checker vs. the canonical 12-test IMinimalSSI compliance regime are not yet mapped").
**Sources on the `sandbox-onboarding` branch:** `FINDINGS.md` §G (canon integration record), `docs/HANDOFF_TO_ARCHITECT_v1.0.md` (Set A/B/C split), `docs/PROGRESS_AND_CHANGE_REPORT_v1.0.md` §1 (the three streams and the open reconciliation item), `docs/UNDERSTANDING_TEST_REPO.md` (per-build IMinimalSSI expectations).
**Token:** the verbatim F1–F12 signatures are in the canon archive (`cvin-sandbox-v1.3`), which is not on any branch of this repository. Function *names* below are those the branch documents quote; F-numbers are given only where the source gives them. **[B1]** marks cells that need the archive to be stated exactly.

---

## 1. What the basic set is

The canonical sandbox (`cvin-sandbox-v1.3`, 2026-06-05) defines a **minimal self-sovereign-identity interface, `IMinimalSSI`, with twelve functions** and a **parameterised 12-test compliance suite**; a substrate is *admitted* to the comparison when it passes all twelve ("Admission = compliance"). The twelve split into:

| Set | F-numbers | Content (as quoted on the branch) | Named functions seen in sources |
|---|---|---|---|
| **Set A — identity and keys** (`ISetA`) | F1–F4, F9–F12 | identifier creation and resolution; controller/key rotation; delegates and attributes (DID-document state); agent-proxy `execute`; deactivation | `createDID` (S1 trace), `changeOwner` (key rotation), delegates/attributes, `execute` (ACTION key / agent proxy), deactivation **[B1]** for exact numbering |
| **Set B — credentials** (`ISetB`) | F5–F8 | issue, verify, revoke a credential; present it | `issueCredential`, `verifyCredential`, `revokeCredential` (F5–F7, order **[B1]**); **F8 = `createPresentation`** (sourced) |
| **Set C** (`ISetC`) | — | optional ERC-8004 agent layer; no F-numbers | out of scope here |

The canon's only baseline is **O1_ERC1056** (12/12), with one architect-pass S1 trace: `createDID` 178,935 gas, `issueCredential` 130,163, `createPresentation` 62,441 (2026-06-05). Its structural finding is that **no ERC provides F8 natively**: `createPresentation` is realised as a replay-protected on-chain anchor pattern, so SP-1 is "ERC-1056 anchor **+ credential-anchor pattern**", not bare ERC-1056.

## 2. How the catalogue extends it

The basic set asks *one* question per substrate — does it implement these twelve functions? — and admits or rejects. The catalogue keeps that question (as the **conformance gate**) and adds three things the thesis needs and the basic set does not give:

1. **Cost and footprint per function**, exact (gas, zero→nonzero storage writes, calldata, log bytes), for every substrate — L1 of the framework.
2. **Composition over a vehicle's life** — the MOBI VID I + II 17-event lifecycle (L2), the marginal-cost axes in population and history (L3), the read path a verifier actually pays (L6), and a transport-bound condition (M1-H/HTTP).
3. **Breadth** — the same functions on **ten substrates**, so the admitted set can be *ranked*, and the W3C DID Method Rubric's quantitative cells can be filled.

### 2.1 Function-level mapping

| Basic-set function (IMinimalSSI) | Set | Catalogue operation(s) | Measured where |
|---|---|---|---|
| `createDID` — identifier creation (+ VIN binding in the vehicle profile) | A | **C1** create identity; **C2** create + VID-I attributes | L1 crud, L2 event 1, L3 N-axis, L4 batch |
| resolve identifier / DID document | A | **R1** resolve owner; **R2** by VIN; **R3** full document | L1 reads, L3 h-axis, L6 resolve, HTTP condition |
| key / controller rotation (`changeOwner`) | A | **U1** rotate controller; **U4** ownership transfer | L1, L2 events 13 and 16 |
| delegates (session / verification keys) | A | **U2** add delegate (TTL); **D1** revoke; **R4** verify | L1, L2 events 11–12, L6 R4 |
| attributes / DID-document state | A | **U3** set attribute; **D2** revoke attribute | L1, L2 events 5–10, L5 throughput |
| agent proxy / `execute` | A | — **not a catalogue op** (ERC-725X/ERC-4337 `execute` is exercised only as the carrier of U5) | gap, §4 |
| deactivation | A | **D3** deactivate identity | L1, L2 event 17 |
| `issueCredential` | B | **V1** issuer key anchor + **V3** anchor credential status (the VC itself is signed off-chain by `2_w3c-ssi-layer`) | L1, L2 events 2–4, 14 |
| `verifyCredential` | B | **V6** status check (+ R4 for the issuer key); off-chain proof check in the VC layer (register #21/#27) | L1 reads, L6 |
| `revokeCredential` | B | **V5** revoke credential | L1, L2 event 15 |
| `createPresentation` (**F8**) | B | — **not a catalogue op** | gap, §4 |
| (programme addition) relayed / sponsored operation | — | **U5** meta-transaction (optional op) | L1 |

Every basic-set function except `execute` and `createPresentation` therefore has at least one measured catalogue operation on every substrate (or an explicit `n/a` where the standard lacks the primitive — `results/metrics/latest/tables/analysis_capabilities.*`), and the catalogue adds U5, the lifecycle, the read path and the batch/scale axes that the basic set does not contain.

### 2.2 Coverage of the basic set per substrate (from the run of record)

`npm run metrics:analyze` now emits **A6 — basic-set coverage**: for each substrate, how many Set-A-mapped and Set-B-mapped catalogue operations it supports natively. Reading from `results/metrics/latest/tables/analysis_basic_set.*` (run `0eef6af`):

With all twelve functions mapped (X1 `execute` in Set A, P1 `createPresentation` in Set B; run `9bdf451`):

| | Set A ops (12) | Set B ops (5) | **Natively** admitted (every mapped op is a native primitive) |
|---|---|---|---|
| ERC-4337 | 12/12 | 5/5 | **yes** — the only substrate whose identity can also *act* (`execute`) |
| ERC-1056 (pure), ERC-725, CVIN-Combined | 11/12 (no X1) | 5/5 | no — registries cannot act; everything else native |
| ERC-1056 wrapper, ERC-721 | 10/12 (no D2, X1) | 5/5 · 4/5 (ERC-721: no P1) | no |
| ERC-725xy | 9/12 (no U2/R4/D1) | 5/5 | no — has `execute` but no delegates |
| ERC-1155 | 8/12 | 4/5 (no P1) | no — soulbound: holder cannot present |
| ERC-735 | 8/12 | 4/5 (no V1) | no |
| LSP8 | 8/12 | 3/5 (no V1, P1) | no |

Two readings. First, the canon admitted **O1_ERC1056 12/12**, while this table admits only ERC-4337 natively: the difference is that the canon's SP-1 is "ERC-1056 anchor **+ credential-anchor pattern**" — functions a bare registry lacks (`execute`, `createPresentation`) are realised by a pattern layered on it. A6 therefore answers a stricter question (*native* primitives) than canon admission (*pattern-realised* compliance); which of the two the thesis should use for "admitted" is the architect ruling the reconciliation needs (**[B1]**, §3). Second, the delegate gap across the ERC-725 family is exactly what the canon's expectation column predicted ("claims absent", "Set A native at interface level"). Every non-admitted substrate remains measured here, with each gap carried as a finding rather than an exclusion.

## 3. Reconciling the two compliance regimes (the open architect item)

| | Canon (stream B) | This repository (stream C) |
|---|---|---|
| Instrument | 12-test `IMinimalSSI` suite, one parameter (`IMPL`) | adapter **conformance gate** (`test/benchmarks/adapters.conformance.test.js`, 87 passing / 23 declared-n/a across 10 adapters) + contract suites (351) + Python W3C checker (94.3 %) + external W3C DID test suite (335/336, register #24) |
| Verdict type | binary admission | per-op `supported` flag, then measured cost |
| Scope | O1_ERC1056 only (O2–O8 empty) | ten substrates |

**Proposal.** Treat the 12-test suite as the *admission layer* and the conformance gate as its *extension*: (a) each of the twelve canon tests maps to one or more gate tests via §2.1 (the gate already asserts post-state for C1/C2, R2, U2/R4/D1, U3/R3, D2, U5, V1/V3/V5/V6, U1/U4, D3 per substrate); (b) a substrate with any `n/a` on a Set-A or Set-B-mapped **core** op is *not admitted* in the canon's sense but **is still measured** here, with the `n/a` reported as a finding (the thesis compares cost only among admitted substrates on the full-coverage subset, as `ANALYSIS.md` A4 already does); (c) the two canon functions the catalogue lacks (§4) are added as catalogue ops before the mapping is called complete; (d) the canon's O1 S1 gas (createDID 178,935 at solc 0.8.24/paris, `cvin-sandbox` operation definition) and the harness's C1 (76,808 on the clone lineage's pre-merge contracts, superseded on the merged trunk by 76,830 (#34); cancun, `createVehicleDID`) are **different operation definitions on different EVM targets** and are listed in `MEASUREMENT_CONDITIONS.md` §5.D as non-comparable until one is re-run under the other's definition.

This keeps the canon's gate semantics intact (admission = all twelve), makes the harness the measured extension of it, and gives the architect a concrete mapping to rule on.

## 4. Gaps the extension exposes (to be added to the catalogue)

| Missing op | Basic-set function | Why it matters | Proposed catalogue op |
|---|---|---|---|
| presentation | F8 `createPresentation` | the canon's structural finding (no ERC provides it natively); the harness measures V-ops only up to status | `P1_create_presentation` — anchor a presentation nonce/hash with replay protection (the canon's O1 pattern, 62,441 gas there), realised per substrate like V3 |
| agent proxy | Set A `execute` | ERC-725X and ERC-4337 accounts can *act*; the other substrates cannot; today only U5 touches it | `X1_execute_call` — the identity performs one external call (n/a on registries without an executor) |

**Implemented 2026-10-15** as `P1_create_presentation` and `X1_execute_call` (framework §2.2c): P1 is holder-written on ERC-1056 (both modes), CVIN-Combined, ERC-735, ERC-725, ERC-725xy and ERC-4337 and n/a where the holder has no write path (ERC-721, ERC-1155, LSP8); X1 exists only where the identity is an account with an executor (ERC-725xy, ERC-4337) — ERC-725 basic's `execute` is a stub, and no registry substrate can act. The conformance gate asserts the anchor appears in R3 and that the call target sees the account as `msg.sender`. Both ops enter the L1 tables and A6 in the run of record that follows the change to the measured tree (register #54).

## 5. Status

- Mapping: **this document** (Set-level exact; F-numbers **[B1]** pending the canon archive).
- Coverage table: `analysis_basic_set` (A6) generated from the run of record, now over all twelve basic-set functions (X1 in Set A, P1 in Set B).
- Reconciliation: proposal in §3 for the architect; register row #53.
- Catalogue gaps: §4 **closed** — P1 and X1 implemented and gated; measured in the run of record (register #54).
