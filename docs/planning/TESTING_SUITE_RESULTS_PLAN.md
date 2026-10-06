# Testing Suite & Results Organisation Plan (TSR Plan) — v1.0

**Author:** Nikhil Prakash (MASc, UBC ECE) — nikhil.prakash1995@gmail.com
**Date:** 2026-10-04
**Branch:** `claude/testing-suite-organization-z5j7dc` (planning branch; no code changes in this pass)
**Status:** v1.0 — plan of record for the "organised testing suite and results" work. Awaiting the author's second pass (`docs/planning/TESTING_SUITE_SECOND_PASS_SHEET.md`) before Phase 0 starts.
**Companions:** `docs/MEASUREMENT_CONDITIONS.md` (claim register, condition tags), `docs/CVIN-DATA-COLLECTION-FRAMEWORK.md` (18-op catalogue, L1–L8 levels, falsifiers), `docs/THREAT_MODEL.md` (A1–A4, G1–G8), `docs/DID_METHOD_RUBRIC.md` (qualitative axis), `docs/HANDBACK_2026-10-04.md` (state of the trunk), `docs/INDEX.md` (which document is canonical for what).

---

## 0. Purpose and stance

The repository holds a large, verified body of tests and results: Hardhat suites per standard, a 54-scenario security suite, a nine-adapter metrics harness with six scenarios, Python suites for the VC layer, DID resolver, MOBI VID and the CV2X testbed, twelve lifecycle use cases, an internal W3C compliance checker, an external W3C DID test-suite run, N = 30 latency studies, scaling and freshness-k experiments, two security lenses, and a claim register of 38 rows. All of it is **organised by where the code lives** (directory, language, session that produced it) and **recorded by claim** (register row). What it is not organised by is the question an examiner, a reader of Chapter 5, or the author with a notebook asks first:

> *For each implementation option, which basic identity functions are tested, how (functional, adversarial, conformance, cost, latency, scale), to what evidence level, under which conditions, and where is the number?*

This plan turns the existing work into a **single, addressable testing suite and results structure** that answers that question cell by cell, without discarding or re-measuring anything that is already of record. Concretely it delivers:

1. a five-dimension **taxonomy** (subject × identity function × property class × evidence level × research mapping) and a stable **identifier scheme** for every test and every result;
2. a machine-readable **Test Case Register** and **Coverage Matrix**, generated from the code (not typed by hand) and checked in CI, so a cell that is empty is a visible finding;
3. a **results pipeline** with one entry point, one results schema, run stamping, and a register check, so a number reaches a chapter only through a path that can be replayed;
4. an **academic-rigour layer** per test family: pre-registered falsifiers, statistical protocol, threats to validity, reporting standard, replication protocol;
5. an **intake protocol** for the author's paper notebooks, so the material "on paper" becomes register rows and matrix cells (redundant with the paper, then extended), rather than staying in one copy;
6. a **multi-agent, multi-phase execution plan** with briefs, exit criteria, and the standing rules that bind every agent.

What this plan does **not** do: it does not change any result of record, does not move files whose import paths other code depends on, does not weaken or skip any test, and does not decide the author's open framing questions (H1 wording, MOBI claim, checker strictness). Those are routed to the second-pass sheet.

### 0.1 Standing rules (inherited, binding on every phase and agent)

| # | Rule | Source |
|---|---|---|
| S1 | A number enters a chapter only with a register row of status **V** and a source path | `docs/INDEX.md` §Rule |
| S2 | No test is skipped, weakened, or quarantined; a skip fails CI | `HANDBACK_2026-10-04.md` §7; `w3c-compliance.yml` |
| S3 | Exact where the EVM is exact (gas, bytes, slots: single value, equality asserted); statistical where it is not (N ≥ 30, median, p95, environment header) | `MEASUREMENT_CONDITIONS.md` §1 |
| S4 | Only trunk-generated numbers are reportable; session-log numbers are not evidence | `CVIN-DATA-COLLECTION-FRAMEWORK.md` §0 |
| S5 | One catalogue, one workload, all substrates; `n/a (no primitive)` is a result, not a blank | same, §2 |
| S6 | Author-attributed commits, no AI trailers; push at every step boundary | `ORIGINAL_PROMPT_AND_DIRECTION.md` §B.1–B.2 |
| S7 | After-action report opened at the start of a pass, closed at its end; hand back, never end abruptly | same, §B.7 |
| S8 | Scope changes are logged (SC-nn), never silent | `SCOPE_CHANGES.md` |
| S9 | Figures from a different condition tag are never placed in the same table | `MEASUREMENT_CONDITIONS.md` §1 |

New rules this plan adds (proposed; confirmed in the second pass):

| # | Rule | Why |
|---|---|---|
| S10 | Every test carries a taxonomy tag resolvable to a Test Case Register row; an untagged test fails the register build | makes the matrix generated, not typed |
| S11 | A result file carries `meta.json` (or an equivalent header) with commit, dirty flag, toolchain versions, condition tag and dataset seed, or it is not a result of record | extends the harness's run identity to every producer |
| S12 | A coverage-matrix cell has one of exactly five values: `T` tested, `N` n/a (no primitive, documented), `G` gap (primitive exists, no test), `P` paper (author's notes, not yet in repo), `X` out of scope (SC-nn) | makes gaps and paper material first-class |
| S13 | Redundancy by design: every item on paper gets a repo row with `source: paper` before it is reconciled; the paper copy is never the only copy | author's request |

---

## 1. Problem statement — what "organised" means here

### 1.1 Current organisation (as found 2026-10-04)

| Axis | How the repository is organised today | What is missing |
|---|---|---|
| **Tests** | by directory and language: `1_blockchain-identity/test/<Standard>/`, `test/security/`, `test/benchmarks/`; `2_w3c-ssi-layer/*/tests/`; `cv2x-testbed/tests/`; script-style tests in `cv2x-testbed/scripts/` | no cross-cutting index: which test covers which identity function on which substrate with which property; no stable test IDs; counts in docs drift (217 → 242 → 353 → 369 Hardhat; 60 → 286 → 358 Python) |
| **Results** | by producer: `4_comparison-framework/results/`, `1_blockchain-identity/results/metrics/latest/`, `cv2x-testbed/results/`, `cv2x-testbed/sumo/results/`, `docs/conformance/reports/`, `docs/figures/` | no single results index with schema; run stamping is complete only in the metrics harness; several scripts overwrite tracked results (`HANDBACK` §6) |
| **Claims** | the claim register, rows #1–#38, with tags M0/M1/M1-H/M1-H/HTTP/M2 and status V/E/S/U/B | the register is prose-heavy (one row can be a page); no machine-readable form; no link from a row to the test IDs that guard it |
| **Functions** | the 18-op catalogue (C1…V6) exists for the metrics harness only; the per-standard Hardhat suites test contract functions by their Solidity names; the Python providers test `register/sign/verify/revoke/check_revocation/resolve` | no one table that says, for every implementation option, which basic identity function is tested, measured, attacked, and conformance-checked |
| **Rigour** | strong, but distributed across audit, review, framework, threat model and register documents | no per-test-family statement of design, falsifier, threats and reporting standard; no replication protocol beyond "second host" notes |
| **Paper notes** | "a couple notebooks full" (B.3), not in the repository | no intake path; single copy |

### 1.2 Definition of done for "organised"

The work is done when all of the following hold on the trunk:

1. `docs/testing/COVERAGE_MATRIX.md` is generated by `tools/testing/build_register.py` from tags in the test code and prints, for every (subject, function, property) cell, exactly one of `T/N/G/P/X` with a link to the test IDs or the SC/paper row.
2. Every test in the repository has a register row (`docs/testing/test_register.{yaml,csv}`) with ID, subject, function, property, evidence level, condition tag, RQ/H mapping, and location; CI fails if a test is untagged or a row is orphaned.
3. Every result file of record has a `meta.json`/header (S11) and a row in `docs/testing/results_register.{yaml,csv}` that links it to its producer script, its register claim rows (#nn), and the test IDs that guard its determinism or regression.
4. One command (`make results` or `tools/testing/run_all.sh --tier=<smoke|full|measure>`) runs the suite tier, regenerates results and tables, rebuilds the two registers and the matrix, and fails on any register/CI rule violation.
5. Each test family has a one-page **Test Family Charter** (design, falsifier, N and statistics, threats to validity, reporting standard reference, replication status).
6. The author's paper material has been taken in through the second-pass sheet: every item has a row with `source: paper`, status P → (T | G | X).
7. Chapter 5 tables and figures are listed in `docs/testing/RESULTS_PRESENTATION_PLAN.md` with their producing file and register rows, and the stale-figure list in `HANDBACK_2026-10-04.md` §4.7/§4.12 is empty.

---

## 2. Design principles

1. **Tag, do not relocate.** Tests stay where their imports, fixtures and CI jobs expect them. Organisation is achieved by a taxonomy tag in the test name/docstring/`describe` title and by generated indices. Relocation is permitted only where nothing imports the file (decided per file in Phase 3).
2. **Generated over typed.** Every matrix, count and index in `docs/testing/` is produced by a script from the code and the result files. A hand-typed count is a drift waiting to happen (cf. the four Hardhat totals in the docs today).
3. **The matrix is the finding.** An empty cell is reported, never hidden: `N` (no primitive, with the §2.2a/b reason), `G` (gap), `X` (scope change). This extends the harness's `n/a` convention to the whole suite.
4. **Exact vs statistical, always labelled.** Inherits S3. A test family is either deterministic (asserts equality against a committed value) or statistical (asserts a bound on a distribution statistic with stated N) and says which in its charter.
5. **Falsifiable by construction.** Every hypothesis-bearing test family states the observation that would refute it (as `CVIN-DATA-COLLECTION-FRAMEWORK.md` §8 already does for H1/H3/H4/H5/PKI) and has at least one executable check that would go red on that observation.
6. **Conditions travel with numbers.** Inherits S9/S11. A result without a conditions block is not a result.
7. **Three tiers, one suite.** `smoke` (minutes; CI on every push), `full` (all functional/security/conformance tests; CI on every push today), `measure` (metrics harness, N = 30 latency, scaling, V2V; nightly or on demand; regenerates results of record and runs the determinism gates). The tier is a tag, not a separate directory.
8. **Redundancy with the paper.** Inherits S13. The repository is the durable copy; the paper is the source. Nothing is "integrated" until both agree.
9. **Reviewable by an examiner in ten minutes.** From `docs/testing/README.md`, an examiner reaches any number's test, result file, conditions, and register row in at most three clicks.

---

## 3. The taxonomy (five dimensions + conditions)

### 3.1 Dimension A — Subjects under test (implementation options)

| SUT ID | Subject | Layer | Where | Already an adapter/provider? |
|---|---|---|---|---|
| `erc1056` | ERC-1056 EthereumDIDRegistry (pure did:ethr mode) + CVINVehicleDIDRegistry | chain | `contracts/ERC1056/` | harness adapter ✓ |
| `erc1056w` | ERC-1056 wrapper-controlled mode | chain | same | harness adapter ✓ |
| `erc721` | ERC-721 CVINVehicleNFT (+ thin DID wrapper) | chain | `contracts/ERC721/` | ✓ |
| `erc725` | ERC-725 proxy account | chain | `contracts/ERC725/` | ✓ |
| `erc725xy` | ERC-725 X+Y smart account | chain | `contracts/ERC725xy/` | ✓ |
| `erc735` | ERC-735 claim holder | chain | `contracts/ERC735/` | ✓ |
| `erc1155` | ERC-1155 soulbound credential | chain | `contracts/ERC1155/` | ✓ |
| `erc4337` | ERC-4337 account + minimal EntryPoint (representative) | chain | `contracts/ERC4337/` | ✓ |
| `lsp8` | LSP8 identifiable asset (representative) | chain | `contracts/LSP8/` | ✓ |
| `cvin` | CVIN-Combined hybrid (ERC-1056 + ERC-735) | chain | `contracts/CVINCombined/` | ✓ |
| `mobi-v1` | MOBI VID I registry (birth certificate) | chain + Python | `contracts/MOBI/MOBIVIDRegistry.sol`, `2_w3c-ssi-layer/mobi-vid/birth_certificate.py` | application profile, measured alongside |
| `mobi-v2` | MOBI VID II registry V2 (lifecycle, attestEvent) | chain + Python | `MOBIVIDRegistryV2.sol`, `lifecycle_events.py`, `mobi_vid_registry.py` | application profile |
| `mobi-backends` | MOBI VID realised on five identity backends (the sweep) | chain + Python | `4_comparison-framework/results/mobi_backends*` | sweep output ✓ |
| `cv2x-erc1056` | cv2x testbed `ERC1056Registry` (not byte-identical to `EthereumDIDRegistry`; K-5) | chain + Python | `cv2x-testbed/contracts/`, `identity/` | provider ✓ |
| `pki` | Baseline A: IEEE 1609.2-style PKI (CA, enrollment/pseudonym certs, CRL) | off-chain Python | `cv2x-testbed/identity/standard/pki_identity.py` | provider ✓ |
| `central` | Baseline B: centralised vehicle registry | off-chain Python | `cv2x-testbed/identity/centralized_vehicle_registry.py` | provider ✓ |
| `did-resolver` | W3C DID resolver, methods `did:ethr`, `did:nft`, `did:key`, `did:mobi` | Python | `2_w3c-ssi-layer/did-resolution/did_resolver.py` | per-method SUT sub-IDs `did-resolver/ethr` etc. |
| `vc-layer` | VC issuer / holder / verifier / schemas / revocation / selective disclosure | Python | `2_w3c-ssi-layer/verifiable-credentials/` | — |
| `v2v-path` | V2V message path (BSM sign → verify → trust decision), PKI and SSI variants, warm/cold, freshness-k | Python | `cv2x-testbed/sumo/`, `cv2x-testbed/protocols/` | — |
| `use-cases` | the 12 lifecycle use cases (multi-party, end-to-end) | Python | `cv2x-testbed/scripts/test_use_cases.py` | — |
| `pipeline` | the results pipeline itself (generators, tables, determinism gates, register build) | JS + Python | `4_comparison-framework/`, `analysis/`, `tools/testing/` | — |

Sub-IDs are allowed where a subject has internal options that are compared (`did-resolver/ethr`, `v2v-path/ssi-warm`, `mobi-backends/erc1155`).

### 3.2 Dimension B — Basic identity functions (the function catalogue)

The catalogue has four groups. Group B1 is the harness's 18-op catalogue verbatim (`benchmarks/lib/operations.js`), so chain SUTs need no new naming. Groups B2–B4 extend the same naming style to the layers the harness does not cover.

**B1 — Identity and credential operations (chain substrates; existing)**

| Op | Class | Semantic | Core |
|---|---|---|---|
| C1 | CREATE | create identity bound to VIN | ✓ |
| C2 | CREATE | create + VID-I birth-certificate attributes | ✓ |
| R1 | READ | resolve controller/owner | ✓ |
| R2 | READ | VIN → identity | ✓ |
| R3 | READ | build full DID Document | ✓ |
| R4 | READ | is key an authorised delegate | ✓ |
| U1 | UPDATE | rotate controller | ✓ |
| U2 | UPDATE | add delegate (TTL) | ✓ |
| U3 | UPDATE | set attribute | ✓ |
| U4 | UPDATE | transfer vehicle (legal owner) | ✓ |
| U5 | UPDATE | meta-transaction (relayed, signed) | cond. |
| D1 | DELETE | revoke delegate | ✓ |
| D2 | DELETE | revoke attribute | ✓ |
| D3 | DELETE | deactivate identity | ✓ |
| V1 | CREATE | issuer key anchor | ✓ |
| V3 | CREATE | anchor credential status | ✓ |
| V5 | DELETE | revoke credential | ✓ |
| V6 | READ | credential status check | ✓ |

Plus the two off-chain credential ops the framework names but the harness does not execute: **V2** issue credential (sign VC off-chain) and **V4** verify credential (resolve key + status + signature). These belong to `vc-layer` and `v2v-path`.

**B2 — Lifecycle events (MOBI VID I + II; existing in the harness `lifecycle` scenario and the MOBI Python layer)**

L01 birth certificate (C2) · L02 issuer key anchor (V1) · L03 registration credential (V2+V3) · L04 insurance credential (V3) · L05 service endpoint (U3) · L06–L10 five service records (U3) · L11 key rotation (U2+D1) · L12 ownership transfer (U4) · L13 re-registration (V3) · L14 credential revocation (V5) · L15 second transfer (U4) · L16 end-of-life (D3). The eleven MOBI VID II event types and the eight issuer roles map onto these and are listed in `MOBI_VID_CHECKLIST.md`.

**B3 — Credential-layer functions (vc-layer, did-resolver)**

| Op | Semantic |
|---|---|
| K1 | issue VC (schema-validated, EIP-191 secp256k1 Data Integrity proof) |
| K2 | create presentation (challenge, domain) |
| K3 | selective disclosure (salted-digest, SD-JWT style) |
| K4 | verify VC (6-stage offline pipeline) |
| K5 | verify presentation |
| K6 | revoke / status list |
| K7 | schema validation (10 automotive schemas) |
| K8 | DID resolve (per method) → DID Document + resolution metadata |
| K9 | DID dereference / representation (`resolveRepresentation`, `contentType`) |
| K10 | error handling (`methodNotSupported`, `invalidDid`, `notFound`) |
| K11 | VIN confidentiality (hash on-chain; AES-256-GCM off-chain) |
| K12 | freshness-k cache refresh (full / probe) |

**B4 — V2V message-path functions (v2v-path, pki, central)**

| Op | Semantic |
|---|---|
| M1 | register vehicle / enrol |
| M2 | sign BSM |
| M3 | verify BSM (warm) |
| M4 | verify BSM (cold: full credential verify) |
| M5 | check revocation (CRL / status / chain) |
| M6 | resolve identity at message time |
| M7 | pseudonym change / rotation |
| M8 | revocation propagation (time from revoke to first negative answer) |

### 3.3 Dimension C — Property / test classes

| Class | Name | What a test in this class establishes | Exact or statistical |
|---|---|---|---|
| **F** | Functional (positive) | the function does what the spec says on valid input | exact |
| **N** | Negative / revert | invalid input or unauthorised caller is rejected with the **exact** expected error (review 02 standard) | exact |
| **A** | Adversarial / security | an attack from the threat model (A1–A4 against G1–G8) fails; differential control shows the honest path succeeds | exact |
| **W** | Conformance | the behaviour satisfies a normative statement of an external spec (DID Core, VC DM 2.0, MOBI VID clauses, ERC text) or the adapter contract (`test:conformance`) | exact |
| **G** | Cost (exact) | gas, calldata bytes, log bytes, SSTORE/SLOAD counts, bytecode size; asserted byte-identical across runs | exact |
| **L** | Latency / throughput (statistical) | N ≥ 30, median, p95, bootstrap CI, Mann–Whitney for comparisons | statistical |
| **S** | Scale | marginal cost or latency as N or history h grows; slope and O(·) class | mixed |
| **D** | Determinism / reproducibility | re-run equality gate; artifact freshness; run identity | exact |
| **I** | Integration / lifecycle | multi-party, end-to-end, computed pass/fail with forged and replayed controls (the 12 use cases, lifecycle parity) | exact |
| **Q** | Qualitative / analysis | rubric cells, capability matrix, dominance/Pareto, ratios — pure functions of results of record | derived |

### 3.4 Dimension D — Evidence ladder

| Level | Meaning | Example today |
|---|---|---|
| E0 | asserted in prose only | "50–100 ms resolution" (register #2 row: E) |
| E1 | a test exists | — |
| E2 | the test asserts the exact expected outcome (not "any error") | security suite after review 02 |
| E3 | the test runs in CI with no skips | all 369 + 358 today |
| E4 | a result file of record is committed with run stamp and conditions | `results/metrics/latest/meta.json` |
| E5 | claim register row with status **V** | #1–#4, #25, #27, … |
| E6 | externally validated (official W3C suite; public testnet; upstream byte-faithfulness) | #24 (335/336) |
| E7 | replicated (second host, second replicate, or independent re-implementation) | freshness-k r2; Exp. C 5-repeat |

A matrix cell's evidence level is the maximum over its tests and results. The thesis cites at E5 or above (S1).

### 3.5 Dimension E — Research mapping

RQ1–RQ4; H1, H1′(scale), H2, H3, H4, H5, PKI-alternative; the falsifier for each (`CVIN-DATA-COLLECTION-FRAMEWORK.md` §8, extended in §9 of this plan). Every register row carries zero or more of these.

### 3.6 Conditions (not a dimension; a label)

M0, M1, M1-H, M1-H/HTTP, M2 as defined; this plan adds no tag but requires every L/S/G result to carry one.

---

## 4. Identifier scheme and registers

### 4.1 Test Case IDs

```
TC-<SUT>-<OP>-<CLASS>[-<nn>]
TC-erc1056-U2-N-01     ERC-1056, add delegate, negative test, first of several
TC-vc-layer-K3-F       VC layer, selective disclosure, functional
TC-v2v-path-M3-L       V2V path, warm verify, latency study
TC-pipeline-*-D        determinism gates
```

Tagging in code (no file moves):

- **Mocha/Hardhat:** the `it()` title ends with ` [TC-erc1056-U2-N-01]`, or a `describe` block carries a tag that its `it()`s inherit (`describe("U2 add delegate [TC-erc1056-U2]", …)` with class suffix on each `it`).
- **pytest:** a marker `@pytest.mark.tc("TC-vc-layer-K3-F")` registered in `conftest.py`, or a docstring first line `TC: …`. Script-style tests (`test_use_cases.py`) carry the ID in each use-case's name string.
- **Result producers:** `meta.json` gains `"tcs": [...]` listing the determinism/regression TCs that guard the file.

The register builder parses all three forms. Untagged tests are listed in `docs/testing/UNTAGGED.md` and fail the build once Phase 3 declares the suite tagged.

### 4.2 Test Case Register schema (`docs/testing/test_register.yaml`, exported to `.csv`)

| Field | Values |
|---|---|
| `id` | TC-… |
| `sut`, `op`, `cls` | from §3.1–3.3 |
| `evidence` | E1–E7 (computed: E1 by existence, E2 by assertion audit flag, E3 by CI membership, E4/E5 by linked result/register rows) |
| `condition` | M0 / M1 / M1-H / M1-H/HTTP / M2 / none |
| `tier` | smoke / full / measure |
| `rq`, `hyp` | lists |
| `location` | path:line, framework (mocha/pytest/script) |
| `title` | the test's own title |
| `guards` | result files or register rows this test protects |
| `source` | repo / paper / review-02 / audit-01 … |
| `status` | active / gap / n-a / scope-change(SC-nn) / paper-pending |
| `notes` | free text (e.g. the §2.2a/b reason for an `N` cell) |

### 4.3 Results Register schema (`docs/testing/results_register.yaml`)

| Field | Values |
|---|---|
| `id` | RR-<producer>-<nn> |
| `path` | result file(s) of record |
| `producer` | script + invocation |
| `condition` | tag |
| `stamp` | commit, dirty, date, toolchain, seed (from `meta.json` or header) |
| `claims` | register rows #nn it feeds |
| `tcs` | TCs that guard it (determinism gate, regression pin) |
| `tables`, `figures` | downstream artefacts (tex/csv/png) |
| `chapter` | where it appears |
| `status` | V / S / B / E as in the claim register |

### 4.4 Coverage Matrix

`COVERAGE_MATRIX.md` is three generated views of the same register:

1. **Function × SUT** (the "basic identity functions for each implementation option" sheet): one page per property class (F, N, A, W, G, L, S), cells `T/N/G/P/X` with TC counts and evidence level.
2. **SUT × property class** roll-up: how deep is each option tested.
3. **Hypothesis × evidence**: for each H, the TCs and RRs that support it, the falsifier, and whether an executable check exists for the falsifier.

### 4.5 Relationship to the claim register

The claim register (`MEASUREMENT_CONDITIONS.md` §3) remains the canonical **prose** record and is not rewritten. Phase 5 adds a machine-readable mirror (`docs/testing/claims.yaml`: `id, claim, tag, source, status, rrs, tcs`) that the builder cross-checks: every V row must have at least one RR and one guarding TC, or the build warns. The prose row stays authoritative when they disagree, and the disagreement is a finding.

---

## 5. Target layout (additive; nothing moves in Phases 0–2)

```
docs/testing/                      # NEW — the organised suite, all generated except README and charters
  README.md                        # how to read; three-click rule; tiers; how to run
  COVERAGE_MATRIX.md               # generated (§4.4)
  test_register.yaml / .csv        # generated
  results_register.yaml / .csv     # generated from meta.json headers + claims.yaml
  claims.yaml                      # machine mirror of the claim register (hand-maintained, cross-checked)
  UNTAGGED.md                      # generated; must be empty after Phase 3
  charters/                        # one page per test family (§9.2)
    F-functional.md  N-negative.md  A-adversarial.md  W-conformance.md
    G-cost.md  L-latency.md  S-scale.md  D-determinism.md  I-integration.md  Q-analysis.md
  RESULTS_PRESENTATION_PLAN.md     # chapter 5 tables/figures ← RR/TC map
  PAPER_INTAKE.md                  # the author's notebook items as rows (S13)
tools/testing/                     # NEW
  build_register.py                # parses tags → registers + matrix; exit non-zero on rule violations
  run_all.sh                       # --tier smoke|full|measure ; stamps; regenerates; builds; checks
  stamp.py                         # writes/validates meta.json headers for Python producers (S11)
  check_docs_numbers.py            # finds hand-typed counts/figures in docs that disagree with registers
.github/workflows/testing-suite.yml  # NEW — builds registers, fails on untagged/orphan; nightly `measure`
```

Existing test and result locations are unchanged. `docs/testing/README.md` becomes the entry point named in `docs/INDEX.md` for the question "which test covers what, and where is the number".

---

## 6. Current-state inventory (as found, 2026-10-04, HEAD `fa6188e`)

Full as-found detail, per layer, is in `docs/planning/testing_suite/INVENTORY_AS_FOUND_2026-10-04.md` (three read-only surveys, one per layer). This section is the summary the plan acts on. Static counts are from the source; the CI totals (369 Hardhat / 358 Python) are the last recorded runs.

### 6.1 Tests by location → taxonomy

| Location | Static tests | Runtime tests | SUTs | Classes present | Tier today | Taxonomy gaps |
|---|---|---|---|---|---|---|
| `1_blockchain-identity/test/<Std>/*.js` (12 files) | 216 `it()` | same | all nine chain SUTs + `mobi-v1/v2` | F, N, some A (K-* regressions), 5 loose G tests (`lt(100000)`, log-only) | full (CI) | ERC-721 files weak (`tokenURI.includes("Toyota")`, no negatives); `CVINVehicleNFT.sol`, `CVIN_DID_ERC725.sol`, `MOBI/ERC1056Registry.sol` have no dedicated unit file |
| `test/security/securityScenarios.test.js` | 60 `it()` (6 self-checks + 9 std × 6 attacks) | same | nine (no `erc725xy`) | A (exact revert, differential control) | full (CI) | 13 N/A cells have no assertion; `after()` writes into `4_comparison-framework/` (test with side effect); `erc725xy` missing |
| `test/benchmarks/adapters.conformance.test.js` | 11 × 10 adapters | 110 (23 `this.skip()` = declared n/a) | ten adapters | W (adapter contract) | full (CI) | not an equivalence test (U1≡U4 in 9/10; payload inequality erc721 C2; LSP8 attributes written by authority; nothing asserts `NotSupported` on declared-unsupported ops; C1 never checks R1) |
| `test/benchmarks/stats.test.js` | 4 | 4 | pipeline | F | full | — |
| `test/ERC1056/PseudonymPool.test.js`, `test/MOBIVID/attestEventRegression.test.js` | 8 + 2 | — | erc1056, mobi-v2 | G (pinned exact gas), D | full | pins are undocumented as regression oracles |
| `2_w3c-ssi-layer/**/tests/*.py` (8 files) | 143 `def test_` + parametrize | ≈170 | did-resolver, vc-layer, mobi-v1/v2 | F, N, A (review-02 PoCs), W (R1–R4 shape) | full (CI, no-skip gate) | VC README says 28; VC job runs only `test_vc_layer.py` |
| `cv2x-testbed/tests/*.py` (11 files) | 105 + parametrize | ≈188 | cv2x-erc1056, pki, v2v-path, use-cases (M4), pipeline (T-6, T-12) | F, N, A, D | full (CI, on-chain via node 8548) | — |
| `cv2x-testbed/scripts/test_use_cases.py` | 12 use cases | 12 | use-cases (runs on `central` + VC shim, **not** on a MOBI chain) | I | none (not in CI) | pass = "no exception"; 7 of 12 have no explicit check; stdout only |
| `cv2x-testbed/scripts/test_mobi_vid.py`, `test_vin_encryption.py`, `test_comparison.py`, `test_identity_comparison.py`, `run_all_demos.py` | — | — | mobi-v2, pki, central | mixed | none | `test_mobi_vid_compliance` is a hardcoded 100 %; `test_comparison.py` blockchain figures are assumed, not measured; `test_vin_encryption.py` (6 real pytest tests) is outside CI |
| `cv2x-testbed/scripts/w3c_compliance_checker.py` | 44 executed checks + 10 qualitative | 44 | did-resolver, vc-layer | W | full (CI floor 93.0) | writes to CWD; committed copy `4_comparison-framework/results/w3c_compliance.json` is July/93.18 %; `vc_verifier.COMPLIANCE_CHECKLIST` is a second, hardcoded 85.7 % self-score |
| `docs/conformance/` (external W3C DID suite) | 336 generated (was 441) | 335/336 | did-resolver/{ethr,nft,mobi} | W (E6) | none (manual) | measures offline-synthesised documents; both denominators must be reported |

### 6.2 Result producers → results of record

| Producer | Output of record | Condition | Stamp (S11) | Determinism gate | Claims |
|---|---|---|---|---|---|
| `benchmarks/run.js` (`npm run metrics`) | `results/metrics/latest/*` | M1-H | full (`meta.measured` hashes, dirty flags, toolchain) | CI job uploads only, **no diff against committed run** | #29–#31, #34–#36 |
| same over `--network localhost` | `results/metrics-rpc/latest/*` | M1-H/HTTP | full (`dirty:true`, `dirtyMeasured:false`) | none | #39 |
| `analysis/analysis.js` | `latest/ANALYSIS.md`, `analysis_*` tables | derived | inherits | n/a | #36, rubric ▲ cells |
| `scripts/benchmark_gas.js` → `generate_tables.py` | `4_comparison-framework/results/gas_benchmark.{json,csv,tex}` | M1 | partial (date; no tree hash) | CI cell-by-cell diff ✓ (55/55) | #6, #25 |
| `run_gas_stats.py --runs 30` | `gas_benchmark_stats.json` | M1 | partial | `all_deterministic` | #25 |
| `benchmark_scaling.js` → `generate_scaling_tables.py` | `scaling_{marginal,lifetime}` | M1 | partial | none | #26 A/B (**B**) |
| `run_verify_richness.py`, `sumo/run_verify_scaling.py` | `scaling_verify*.json`, repeats, confirmation block | M0 | yes (env header) | 5-repeat pre-declared | #26 C/D (V) |
| `sumo/run_v2v_stats.py` (30 seeds × `--simulate`) | `sumo/results/v2v_latency_stats.json` | M0 | yes (commit, tree_clean, CPU, libs) | none; per-seed file overwritten | #27 |
| `mobi_vid_backend_sweep.js` → `generate_mobi_backend_table.py` | `mobi_vid_backends.*` | M1 | partial | none | H4 |
| `securityScenarios.test.js` `after()` → `generate_attack_tables.py` | `security-analysis/results/attack_results.*` | M1 | **metadata still says "measured 2026-07-19"** | CI (as tests) | #28 |
| `attack_scenarios.py` (+ `security_scenarios.js`) | `security_matrix.*`, `onchain_security.json`, `security_comparison.tex` | M1/M0 | partial | none; **not in CI** | #19, #28 |
| `experiment_pki_vs_erc1056.py` | `cv2x-testbed/results/pki_vs_erc1056.*` | M0/M1 | yes (no seed field; `hardhat_version` null) | none | #21, #22, #23 |
| `experiment_freshness_k.py` (full/probe, r1/r2) | `cv2x-testbed/results/freshness_k*` | M0/M1 | yes | two replicates | #32, #37 |
| `experiment_lifecycle_parity.py` | `lifecycle_parity.*` | M0/M1 | yes | pre-registered verdicts | #33 |
| `experiment_pseudonym_pool.js` | `pseudonym_pool.*` | M1 | yes | `PseudonymPool.test.js` pins | #38 |
| `w3c_compliance_checker.py` | CWD `w3c_compliance_report.json` (CI artifact only) | M0 | **none** | CI floor | #4 |
| `docs/conformance/suite-run/*` | `reports/*` (dated) | M0 | run date in filename | matched-pair table in §9 of the write-up | #24 |
| `docs/figures/make_verification_figure.py` | `verification_dashboard.*` from `results_snapshot.json` (**commit 708302a: 89.6 %, 47 tests**) | — | stale | — | register §1 still calls it "current" |
| `sensitivity.{json,csv,tex}` | — | M1 (**paris**, July) | **no generator in repo** | — | — |

### 6.3 The three "gas" instruments (must never share a table; no machine check exists)

| Instrument | Contracts | Op definitions | Tag | Rows |
|---|---|---|---|---|
| Hardhat test suite (`gas-report.txt`, pinned tests) | `1_blockchain-identity/contracts` | per-test | M1 | #1–#3 |
| `benchmark_gas.js` | same | lifecycle ops per standard (`op(...)` descriptions) | M1 | #6, #25 |
| metrics harness | same | 18-op catalogue | M1-H | #29–#36 |
| cv2x `ERC1056Registry` (K-5) | `cv2x-testbed/contracts` (solc 0.8.20, paris) | provider ops | M1 | #21, #22 |

### 6.4 Verified-this-pass findings that change Phase 0

1. **Run of record ≠ HEAD.** `HEAD:1_blockchain-identity/contracts` = `04c33c2…`; `results/metrics/latest/meta.json` records `contractsTree 6c58b31…`. The two intervening commits (`27a2184`, `d5320b2`) are MOBI-only, so the nine-standard cells are expected to be unchanged, but under the repository's own §5.F rule the run is not of record for HEAD until re-run or the gate says "measured tree unchanged for the adapters' contracts". Phase 0 re-runs and adds the gate.
2. **14 crud cells have `gasDeterministic: false`** (iteration-to-iteration ranges: `cvin` C1/C2/V3/V5, `erc721` C1/U1, `erc735` C2/U3/D2/V3/V5, `lsp8` C1/U1/D2). The tables report the mode. The run-to-run byte-identity claim is true and separate. Cause to confirm in Phase 4: calldata zero-byte variation in ECDSA signatures and minted IDs (4 vs 16 gas per byte) and address-dependent SSTORE patterns; the charter for class G must say which number is reported (mode, min, or range) and why.

---

## 7. Gap analysis

### 7.1 Function × SUT cells that are empty today (class F/N/A/W; the G/L cells are complete for the ten adapters)

| Gap | Cells | Class | Proposed cell value |
|---|---|---|---|
| ERC-725xy absent from the security matrix | `erc725xy × {6 attacks}` | A | **G** → Phase 4 |
| MOBI VID has no harness adapter (measured only by `benchmark_gas.js` and the sweep) | `mobi-v2 × C1…V6` | G, L, W(adapter) | **G** → Phase 4 (adapter `mobi.adapter.js`; declared n/a where VID II has no primitive) |
| Recovery (ERC-4337 guardian `recover`) is not a catalogue op; the 4337 adapter maps the guardian to R4/U2/D1 | all SUTs × new op **U6_recover_controller** | F, A, G | **G**: add U6 (cond.), re-map 4337 R4/U2/D1 to **N** with reason; this moves 4337's "16/17" |
| Declared-unsupported ops are never asserted to throw `NotSupported` | 23 cells | W | **G** → one parametrised test |
| C1 never checks R1 on its own result; U1 and U4 are the same call in 9/10 adapters | conformance | W | tighten conformance; keep U4 as a semantic alias where the standard has no separate primitive and say so in the cell |
| Contracts without a dedicated unit file: `CVINVehicleNFT`, `CVIN_DID_ERC725`, `MOBI/ERC1056Registry` | 3 SUTs × F/N | F, N | **G** → Phase 4 |
| ERC-721 legacy tests (`regularExtended.js`, `identityBased.js`): no negatives | `erc721 × N` | N | **G** |
| 13 N/A security cells with no assertion | — | A | assert the N/A reason (primitive absent) so the cell is `N`, not blank |
| Use cases 1, 2, 4, 5, 7, 8, 9 have no explicit check; suite runs on `central`, not a chain backend | `use-cases × I` | I | **G**: computed oracles per use case; a second backend (MOBI V2) via `lifecycle_backends.py` |
| V2 issue / V4 verify not in the harness; measured only in Python (M0) | `vc-layer × K1/K4` on chain-resolved keys | L | cell is **T** at M0; **G** at M1-H/HTTP (verify with chain-resolved key, per substrate) |
| `did-resolver/ethr` synthesises offline; `did:mobi` is a placeholder | `did-resolver × K8` | F, W | **G** (next-session item 1 in the handback); external-suite caveat stays in the cell note |
| Rubric JSON scored for 3 of 10 substrates; nothing `reviewed:true`; ledger envelope "to assess" | `all × Q` | Q | **G** → Phase 6 |
| Sepolia (M2) never run; real SUMO never run | all G/L cells at M2; `v2v-path` with mobility | G, L | **X** pending author go-ahead (SC-nn) — listed, not hidden |

### 7.2 Rigour gaps (cross-cutting)

| # | Gap | Phase |
|---|---|---|
| R1 | No single regeneration path; `make reproduce` (NEXT_STAGES 1.0rc.3) never built | 5 |
| R2 | Scripts overwrite tracked results (`attack_scenarios.py`, `--simulate`, `run_verify_richness.py`, `benchmark_gas.js` date) | 5 (write to `runs/`, promote explicitly) |
| R3 | Stale result files presented alongside current ones: `w3c_compliance.json` (July), `sensitivity.*` (July, paris, no generator), `results_snapshot.json` (708302a), `attack_results` date stamp | 0 (quarantine to `results/superseded/` with a README) |
| R4 | Statistics implemented, not used: `bootstrapMedianCI`, `mannWhitneyU` never called by a scenario; latency tables lack CIs/tests; throughput 3 bursts; lifecycle latency 1 sample | 6 |
| R5 | Host dependence of latency knees (#32 vs #37) with no replication protocol | 6 |
| R6 | Pre-registration drift: H5 criteria changed from framework §8 (4 criteria) to A3 (6 criteria); most hypotheses lack numeric thresholds and stopping rules | 6 (record as SC; pre-register v2 before any new measurement) |
| R7 | Claims surface hand-typed and drifted: README, COMPOSITION, thesis chapters, CAPABILITIES, INVENTORY, SIDE_PAPERS, security READMEs; test counts appear as 47/147/201/217/295/353/369/739 | 7 (`check_docs_numbers.py`) |
| R8 | Register is prose-only; non-monotonic numbering (#25–#28 before #24; #39 exists); M1–M7 work items collide with M0–M2 condition tags | 5 (`claims.yaml`; rename work items W1–W7 in a note, never the tags) |
| R9 | Harness CI job uploads but does not gate; `test-contracts.yml` header says 47 tests; compliance TARGET (90) below FLOOR (93) | 5 |
| R10 | Python deps unpinned; `2_w3c-ssi-layer/requirements.txt` not installable (`did-jwt==0.1.0`, web3 6.11 vs v7 code) | 3 |
| R11 | Seeds: `cv2x_stack.py`, scenarios, use cases use unseeded `random`; SUMO seeds mobility only; per-seed `v2v_latency.json` overwritten | 3/5 |
| R12 | `allowUnlimitedContractSize: true`; compile cancun / execute osaka (recorded, but a validity threat to state) | 6 (charter G) |
| R13 | `hardhat_version` null in 5/7 testbed JSONs; short commits only | 5 (`stamp.py`) |
| R14 | Reference to non-existent `sepolia_validation.json` in SOURCES/CAPABILITIES; `docs/conformance/internal/w3c_compliance_report.json` listed but absent | 7 |

### 7.3 Author decisions already pending (routed to the sheet, not decided here)

H1 wording (Q-3) · checker strictness (T-7/T-8) and the 7.1.2 correction (#4) · K-4 residual · attestEvent duplicates and owner restriction · K-5 · K-12 · MOBI "compliant" wording and SC-14–SC-20 · H3 design point (k, host, f) · M4 verdict wording · privacy framing (#38) · chapter stale-figure list · tags push · SUMO go-ahead · Sepolia secrets · SC-05/SC-06 · notebook index.

---

## 8. Phased, multi-agent execution plan

Conventions: each phase has an **owner** (the integrating agent), **workers** (parallel agents with isolated scope and a brief in Appendix D), **inputs**, **deliverables**, **exit criteria** (all must hold; checked by the owner, then by an adversarial re-review in Phase 7), and an **after-action report** opened at phase start (S7). Workers never edit the same file; the owner merges. Estimated effort is in agent-sessions (one focused session ≈ 2–4 h of work).

### Phase 0 — Freeze, baseline, re-run of record (1 owner, 2 workers; 1 session)

- **Goal:** a clean, stamped baseline that everything later is diffed against.
- **Workers:** W0-A runs every suite and producer on HEAD (`npx hardhat test`, pytest with node, use cases, checker, `npm run metrics`, `metrics:analyze`, `benchmark_gas.js`, sweep, attack lens 2, v2v stats) and records counts, durations, and output hashes in `docs/testing/BASELINE_2026-10.md`. W0-B quarantines stale artefacts (R3) into `*/results/superseded/<date>/` with a README naming the superseding file, and lists every doc that cites them.
- **Deliverables:** `BASELINE_*.md`; re-run harness promoted to `latest` on HEAD (closes §6.4 item 1); `results/superseded/`; a one-line SC entry if any artefact is retired rather than regenerated.
- **Exit:** all suites green with no skips; `meta.measured.contractsTree == HEAD tree`; baseline hashes recorded; register rows whose numbers moved are updated with the old value kept as S.
- **Risk:** the metrics re-run moves MOBI-adjacent cells → handled by the register rule (old row → S).

### Phase 1 — Inventory and taxonomy build (1 owner, 3 workers; 1–2 sessions)

- **Goal:** every existing test and result has a register row; the matrix exists with `T/N/G` cells (no code changes to tests yet).
- **Workers (by layer, read-only):** W1-A Hardhat + harness; W1-B Python SSI layer; W1-C testbed + scripts + producers. Each emits a CSV fragment `(location, title, sut, op, cls, evidence, condition, tier, rq/hyp, guards, notes)` for every test/producer, using the catalogue in §3 and the as-found inventory. Where a test covers several functions it gets several rows.
- **Owner:** writes `tools/testing/build_register.py` v0 (reads fragments, emits `test_register.yaml/csv`, `results_register.yaml/csv`, `COVERAGE_MATRIX.md`, `UNTAGGED.md`); hand-writes `claims.yaml` from the 39 register rows.
- **Deliverables:** registers v0; matrix v0 (hand-mapped, not yet tag-driven); `claims.yaml`; `docs/testing/README.md` skeleton.
- **Exit:** every `it()`/`def test_`/script test appears in exactly one or more rows; every result file of record appears in `results_register`; every V claim has ≥ 1 RR; the matrix prints the §7.1 gaps as `G`.

### Phase 2 — Gap analysis and paper intake (1 owner, 1 worker + the author; 1 session + author time)

- **Goal:** the target matrix (what *should* be tested) is agreed, including the author's paper material.
- **Inputs:** matrix v0; `TESTING_SUITE_SECOND_PASS_SHEET.md` filled by the author (decisions D-nn, verifications V-nn, paper items P-nn, cell triage).
- **Worker W2-A:** converts each P-nn into register rows with `source: paper, status: paper-pending` and a matrix cell `P`; converts each triage answer into `G` (accepted), `X` (scope change with SC-nn text), or `N` (reason).
- **Deliverables:** `PAPER_INTAKE.md`; matrix v1 with target cells; `SCOPE_CHANGES.md` entries drafted for the author; the Phase 3–6 work list derived from `G` and `P` cells, ranked by (hypothesis relevance, examiner risk, effort).
- **Exit:** no cell is blank; every `G`/`P` has an owner phase; the author has signed off the sheet (recorded in the after-action report).

### Phase 3 — Suite restructuring: tags, tiers, fixtures, CI (1 owner, 4 workers; 2 sessions)

- **Goal:** the matrix becomes tag-driven; three tiers exist; CI builds and gates the registers.
- **Workers (write access, disjoint paths):** W3-A tags every Mocha `it()`/`describe` (`[TC-…]`), adds the Mocha reporter hook that emits `tc-results.json`; removes the `after()` side effect by writing attack results to `runs/` and adding an explicit `npm run security:promote`. W3-B tags pytest tests (`@pytest.mark.tc`, registered in each `conftest.py`), pins Python deps (`requirements-test.txt` with hashes; fix `requirements.txt`), seeds `cv2x_stack.py` and scenarios. W3-C converts the script-style tests: `test_use_cases.py` gains computed oracles per use case and a pytest wrapper with JSON output; `test_vin_encryption.py` moves into `cv2x-testbed/tests/`; `test_mobi_vid.py`'s hardcoded compliance print is deleted or replaced by a real check; `test_comparison.py` assumed figures are labelled `E` or removed. W3-D writes `tools/testing/run_all.sh --tier`, `.github/workflows/testing-suite.yml` (register build + untagged gate + orphan gate; nightly `measure` tier with diff against `latest`), fixes the stale CI headers and the TARGET/FLOOR inversion.
- **Deliverables:** fully tagged suite; `UNTAGGED.md` empty; tiers; new workflow green; Hardhat/Python totals printed by the builder, and only there.
- **Exit:** `build_register.py` runs from tags alone with zero hand-mapped rows left; CI green; no test count hand-typed anywhere in `docs/testing/`.

### Phase 4 — Filling the matrix (1 owner, up to 6 workers by SUT group; 2–3 sessions)

- **Goal:** every `G` cell accepted in Phase 2 becomes `T` at E3.
- **Work packets (each a worker, each with its own brief):**
  - P4-1 `erc725xy` in the security matrix; assert the 13 N/A cells; `erc721` negatives; unit files for `CVINVehicleNFT`, `CVIN_DID_ERC725`, `MOBI/ERC1056Registry`.
  - P4-2 Harness: `mobi.adapter.js`; `U6_recover_controller` (cond.); 4337 re-mapping; `NotSupported` assertion; C1→R1 check; payload-equality assertion per C2; document U1/U4 aliasing per adapter.
  - P4-3 Non-deterministic gas cells: root-cause the 14 cells (calldata zero bytes, address-dependent SSTORE), decide per cell whether to fix the fixture (fixed-length signatures/IDs) or report `min/mode/max`, and write the class-G charter rule.
  - P4-4 Use cases: computed oracles; second backend (MOBI V2 via `lifecycle_backends.py`); JSON output with environment header; CI inclusion.
  - P4-5 Resolver: `_resolve_ethr` reads the chain (with the external suite re-run and the matched-pair table updated); `did:mobi` real or SC.
  - P4-6 VC verify with chain-resolved issuer keys per substrate at M1-H/HTTP (closes the V4 cell); uses the existing Python providers.
- **Exit:** matrix shows no `G` for accepted cells; every new test fails on the pre-change code where it is a fix (review-02 rule); numbers that moved are re-registered.

### Phase 5 — Results pipeline and registers of record (1 owner, 2 workers; 2 sessions)

- **Goal:** one entry point; every producer stamped; registers cross-checked in CI.
- **Workers:** W5-A `tools/testing/stamp.py` (shared `meta.json` writer/validator for Python and JS producers: full commit, dirty flags, measured-tree hashes where applicable, toolchain, seed, condition tag, `tcs`); retrofits every producer in §6.2; all producers write to `runs/<runId>/` and a `promote` step copies to `latest/`. W5-B `run_all.sh --tier measure` orchestrating producers → tables → figures → `metrics:analyze` → `build_register.py`; the harness determinism gate (diff `latest` vs fresh run, cell by cell, as `benchmark_gas` already does); `results_register` built from stamps; `claims.yaml` cross-check (every V row has RR + TC) with warnings as CI annotations.
- **Deliverables:** `run_all.sh`; stamped producers; `results_register`; `RESULTS_PRESENTATION_PLAN.md` v1 (every chapter-5 table/figure → RR → TC); the "three gas instruments" check (a producer refuses to emit a table mixing tags).
- **Exit:** `run_all.sh --tier measure` on a clean tree reproduces `latest` byte-identically for all exact metrics and within stated tolerance for statistical ones; CI nightly runs it.

### Phase 6 — Academic-rigour layer (1 owner, 3 workers; 2 sessions)

- **Goal:** each test family has a charter; statistics are applied where they exist; pre-registration v2; threats-to-validity per family; replication protocol.
- **Workers:** W6-A charters F/N/A/W/I/D (design, oracle, falsifier, threats, reporting). W6-B charters G/L/S/Q: apply `bootstrapMedianCI` and `mannWhitneyU` in the latency tables (with effect sizes and multiple-comparison note); raise throughput bursts and lifecycle latency samples to N ≥ 30 or label them; write the replication protocol (two hosts, back-to-back #32/#37, environment headers as inclusion criteria); the class-G rule from P4-3; the cancun/osaka and `allowUnlimitedContractSize` statements. W6-C pre-registration v2: for each H, numeric threshold, falsifier, stopping rule, and the executable check (`TC-pipeline-H<n>-D`) that goes red when the falsifier is observed; records the H5 criteria change as an SC; scores the rubric JSON for all ten substrates with evidence cells (`reviewed` flags set by a second agent).
- **Deliverables:** `docs/testing/charters/*.md`; `PREREGISTRATION_v2.md`; rubric JSON complete; `SCALING_EXPERIMENTS.md`/`LATENCY_BUDGET.md` cross-references; reporting-standard mapping (ACM SIGSOFT Empirical Standards: *Benchmarking* and *Engineering Research*; ACM artifact-badging terms *Available / Functional / Reproduced* as the targets for the suite).
- **Exit:** every class has a charter; every H has an executable falsifier check in the `measure` tier; every latency table of record carries CI and test columns or an explicit "descriptive only" footer.

### Phase 7 — Adversarial review, docs reconciliation, handback (1 owner, 2 reviewers; 1–2 sessions)

- **Goal:** the suite survives the repository's own review pattern (PASS1 → PASS2 re-review → PASS3 if new High).
- **Reviewers:** R7-A reviews registers and matrix against code (does every `T` cell really have an asserting test? sample 10 % of rows, all `N` reasons). R7-B reviews numbers: `check_docs_numbers.py` over README, COMPOSITION, thesis chapters, CAPABILITIES, INVENTORY, SIDE_PAPERS, security READMEs; produces the stale-figure diff for the author's framing approval (S1: chapter text changes are the author's).
- **Deliverables:** `docs/review03/` findings and fixes; updated `docs/INDEX.md` row for `docs/testing/`; `HANDBACK_<date>.md`; after-action report closed; CHANGELOG entry; version bump proposal.
- **Exit:** zero Critical/High open or every open one is an author decision listed in the handback; `check_docs_numbers.py` clean or every remaining mismatch is in the author's approval list.

### Phase 8 — External validation (author-gated; not scheduled)

Sepolia witness (`validate_sepolia.js`, 3 standards, then one lifecycle per substrate) → M2 rows; real-SUMO run (S0–S8 in `PLAN_MOBI_SUMO.md`); a second-host replication of every L/S result of record. Each becomes an `X → T` transition in the matrix with its own charter addendum.

### 8.1 Dependency graph and parallelism

```
P0 ──► P1 ──► P2 ──┬──► P3 ──► P4 ──┐
                   │                ├──► P5 ──► P6 ──► P7 ──► (P8)
                   └──► P6 charters (drafts can start after P2) ┘
```
P3 and P6-drafting run in parallel; P5 needs P3's tags and P4's new producers; P6-final needs P5's registers. Total: 10–14 agent-sessions plus author time at P2 and P7.

### 8.2 Agent roles, standing

| Role | Count | Tools | Writes to | Must not |
|---|---|---|---|---|
| Owner/integrator | 1 per phase | all | phase deliverables, after-action report | measure (owners read results, never produce them) |
| Worker | 2–6 per phase | all, scoped by path list in the brief | only its listed paths | touch another worker's paths; skip or weaken a test; edit the claim register prose (owner only) |
| Reviewer | 2 in P7 | read + report | `docs/review03/` | fix (reviewers report; owners fix) |

---

## 9. Academic-rigour protocol

### 9.1 Statistical rules (bind every L/S result)

1. N ≥ 30 after ≥ 3 discarded warm-ups; report n, median, p95, min, max, mean, sd; headline = median, budget argument = p95 (`CVIN-DATA-COLLECTION-FRAMEWORK.md` §6).
2. Confidence interval on the median by percentile bootstrap, 10 000 resamples, fixed resample seed (as `run_v2v_stats.py` does); never a parametric CI on N = 30 without a distribution statement.
3. Between-substrate latency comparisons: Mann–Whitney U, two-sided, with Cliff's δ as effect size; Holm correction when more than one comparison is reported in one table.
4. Exact metrics: single value, equality asserted across a fresh re-run; when iteration-to-iteration variation exists (§6.4 item 2) report `mode [min, max]` and the cause.
5. Ratios always carry the op ID and both operands.
6. Every table footer: run-id, commit, condition tag, N, toolchain hash.
7. Pre-registration: threshold, falsifier, stopping rule, and analysis script named **before** the run; deviations recorded as SC entries; failed pre-registered predictions reported as FAIL (as #33 and #38 already are).
8. Replication: a result of record at E7 needs a second run on a second host, or a second replicate on the same host with a stated reason; the two are reported side by side, never averaged.

### 9.2 Test-family charter template (one page each, `docs/testing/charters/`)

```
# Charter — class <X> (<name>)
1. What a test in this class establishes (one sentence) and what it cannot establish
2. Oracle: how pass/fail is computed (exact value, exact revert, spec clause, bound on statistic)
3. Design: fixtures, seeds, N, warm-ups, conditions tag(s), tier
4. Falsifiers: for each hypothesis this class bears on, the observation that refutes it and the TC that detects it
5. Threats to validity (construct / internal / external / conclusion) and the control for each
6. Reporting: table/figure formats, footer fields, which register rows it feeds
7. Replication status and protocol
8. Known limitations and scope changes (SC-nn)
```

### 9.3 Reporting standards used as checklists

- ACM SIGSOFT Empirical Standards — *Benchmarking* (workload definition, baseline, environment disclosure, variability) and *Engineering Research* (artifact evaluation, threats) — mapped item by item in each charter §6.
- ACM Artifact Review and Badging v1.1 — the suite targets *Artifacts Available*, *Artifacts Evaluated – Functional*, and *Results Reproduced* for the exact-metric families; *Results Replicated* only where a second host exists.
- W3C conformance reporting: both denominators and the matched-pair table (per `W3C_DID_TEST_SUITE.md` §9) are the model for every external-suite result.
- Pre-registration format: `PLAN_MOBI_SUMO.md` §A.2 (M4/M5) is the in-repo precedent and becomes the template.

### 9.4 Threats to validity — per family (seed list; charters complete it)

| Family | Construct | Internal | External | Conclusion |
|---|---|---|---|---|
| G cost | gas ≠ USD; op definition per instrument (§6.3) | representative implementations (K-9/K-10); compile cancun / run osaka; unlimited contract size | Hardhat ≠ mainnet; no M2 | iteration variation hidden by mode |
| L latency | in-process ≠ network; M0 vs M1-H/HTTP | warm cache; host; library versions (cryptography 41→49: 2–4×) | single host; simulated mobility | N = 30; no inferential test today |
| A security | threat model coverage (A1–A4 × G1–G8) vs 6 attack types | differential control present | representative implementations | exact revert ✓ |
| W conformance | self-scored structure (T-7/T-8); offline-synthesised documents | checker vs spec drift (#4 7.1.2) | denominator change (441→336) | report both |
| I integration | "pass = no exception"; central backend | unseeded randomness | one backend | — |
| Q analysis | criteria changed from pre-registration (H5) | derived from one run | — | dominance sensitive to `†` lower bounds |

---

## 10. Results presentation plan (Chapter 5 and appendices)

`RESULTS_PRESENTATION_PLAN.md` (Phase 5) lists every table and figure with: ID, caption, producing file, RR, TCs, register rows, condition tag, status. Seed list:

| ID | Artefact | Source of record | Rows | Class |
|---|---|---|---|---|
| T5.1 | Create-identity gas, nine standards + MOBI | `gas_comparison.tex` | #25, #6 | G |
| T5.2 | Operation-catalogue gas, ten columns (C1…V6) | `crud_gas.tex` | #34 | G |
| T5.3 | Lifecycle gas and lifetime totals (17 events; `†` lower bounds) | `lifecycle_gas.tex`, `lifecycle_totals.tex` | #30, #35 | G |
| T5.4 | Capability matrix (A2) | `analysis_capabilities.tex` | #36 | Q |
| T5.5 | Dominance / Pareto (A3/A4) three criterion sets | `analysis_pareto.tex` | #36 | Q |
| T5.6 | Read path: RPC calls, bytes, ms vs history h (in-process and HTTP) | `resolve.tex` (both conditions, two tables) | #31, #39 | L/S |
| T5.7 | Scale: marginal cost vs N and h | `scale.tex` | #31 | S |
| T5.8 | PKI vs ERC-1056 hot path | `pki_vs_erc1056.md/csv` | #21–#23 | L |
| T5.9 | V2V latency N = 30 seeds, PKI/SSI, warm/cold, with CI | `v2v_latency_stats.json` | #27 | L |
| T5.10 | Freshness-k (full and probe; two replicates; two hosts) | `freshness_k*.csv` | #32, #37 | L |
| T5.11 | Lifecycle parity M4 verdicts | `lifecycle_parity.csv` | #33 | I |
| T5.12 | Security lens 1 (43/43, exact reverts) and lens 2 matrix | `attack_results.tex`, `security_comparison.tex` | #28, #19 | A |
| T5.13 | W3C internal checker (44 checks) and external suite (both denominators, matched pairs) | checker JSON, `W3C_DID_TEST_SUITE.md` §9 | #4, #24 | W |
| T5.14 | MOBI VID backend sweep (fidelity gradient) and clause checklist counts | `mobi_vid_backends.tex`, `MOBI_VID_CHECKLIST.md` | H4 | G/W |
| T5.15 | Pseudonym pool M5 | `pseudonym_pool.md` | #38 | G/A |
| T5.16 | Rubric profile, ten columns, ▲ cells from A5 | `analysis_rubric_inputs.tex` + rubric JSON | — | Q |
| F5.1–F5.6 | figures: create-gas bar (log), lifetime stacked bars, resolve ms vs h, freshness-k knee, V2V CDFs, Pareto plot | `docs/figures/make_*.py` regenerated from `latest` | — | — |
| App. A | Coverage matrix (Function × SUT, three views) | `COVERAGE_MATRIX.md` | — | — |
| App. B | Test register (CSV) and results register (CSV) | `docs/testing/*.csv` | — | — |
| App. C | Charters | `docs/testing/charters/` | — | — |

Rule: a table in this list is regenerated by `run_all.sh --tier measure`; one that is not is not in Chapter 5.

---

## 11. Paper-notes intake protocol (S13)

1. The author lists each paper item in the second-pass sheet (section P): kind (function / test idea / result table / figure / hypothesis / threat / scope note), the SUT(s) and function(s) it concerns, the property class, and a one-line content note or photo reference.
2. Phase 2 worker W2-A creates one register row per item with `source: paper`, `status: paper-pending`, and the matrix cell `P`.
3. Reconciliation: if the repository already covers it, the row is linked to the existing TCs and becomes `T` (redundant by design: the paper note stays recorded in `PAPER_INTAKE.md` with "covered by TC-…"). If not, it becomes `G` and enters Phase 4/6 work. If out of scope, `X` with an SC entry.
4. `PAPER_INTAKE.md` keeps the full list with the reconciliation outcome, so the paper and the repository agree item by item.
5. A second intake pass is expected after Phase 4 ("after a few passes", per the author); the protocol is re-run, not redesigned.

---

## 12. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Tagging churn moves gas (selector shifts do not apply to tests, but fixtures might) | low | medium | tags live in titles/markers only; fixtures untouched in Phase 3; gates re-run |
| Re-running the harness on HEAD moves MOBI-adjacent cells | medium | low | expected; register rule (old → S) |
| Worker path collisions | medium | medium | disjoint path lists in briefs; owner merges; CI on every push |
| Over-organisation (registers nobody maintains) | medium | high | registers are generated; hand-maintained files limited to `claims.yaml`, charters, `PAPER_INTAKE.md` |
| Author decisions block Phase 2 | medium | medium | Phases 0–1 and P6 drafting proceed; the sheet lists defaults for each decision |
| Statistical additions change headline numbers | low | medium | CIs and tests are added as columns; medians unchanged |
| CI time grows (`measure` tier ≈ 4 min harness + v2v 30 seeds) | high | low | `measure` nightly; `smoke` on push |

---

## 13. Deliverables checklist and acceptance

- [ ] P0 `BASELINE_2026-10.md`; harness `latest` re-stamped on HEAD; `results/superseded/`
- [ ] P1 `test_register`, `results_register`, `claims.yaml`, `COVERAGE_MATRIX.md` v0, `docs/testing/README.md`
- [ ] P2 `PAPER_INTAKE.md`; matrix v1 with no blank cells; SC drafts; signed-off sheet
- [ ] P3 tags everywhere; `UNTAGGED.md` empty; tiers; `testing-suite.yml` green; deps pinned; seeds fixed; script tests converted
- [ ] P4 accepted `G` cells → `T`; MOBI adapter; U6; 4337 re-map; non-deterministic cells explained; use-case oracles; resolver chain read
- [ ] P5 `stamp.py`; `run_all.sh`; producers write to `runs/` and promote; harness determinism gate; `RESULTS_PRESENTATION_PLAN.md`
- [ ] P6 ten charters; `PREREGISTRATION_v2.md`; rubric scored and reviewed; CIs and tests in latency tables; replication protocol
- [ ] P7 `docs/review03/`; `check_docs_numbers.py` clean or listed; `INDEX.md` row; handback; CHANGELOG
- [ ] Acceptance (definition of done, §1.2, items 1–7) confirmed by the P7 reviewers and the author

---

## Appendix A — Function catalogue, consolidated (B1–B4)

B1 C1 C2 R1 R2 R3 R4 U1 U2 U3 U4 U5 D1 D2 D3 V1 V3 V5 V6 (+ V2 V4 off-chain; + proposed **U6_recover_controller**, cond.)
B2 L01–L16 (lifecycle events; MOBI VID II 11 event types × 8 roles via `MOBI_VID_CHECKLIST.md`)
B3 K1–K12 (credential layer and resolver)
B4 M1–M8 (V2V message path; `pki`, `central` baselines commensurable on latency, bytes, revocation propagation, infrastructure assumption)

## Appendix B — Subjects under test

`erc1056 erc1056w erc721 erc725 erc725xy erc735 erc1155 erc4337 lsp8 cvin mobi-v1 mobi-v2 mobi-backends cv2x-erc1056 pki central did-resolver{/ethr,/nft,/key,/mobi} vc-layer v2v-path{/pki,/ssi;/warm,/cold} use-cases pipeline`

## Appendix C — Coverage matrix seed (class G/L, ten adapters, from the run of record `2026-10-04T09-50-29Z_0eef6af`)

Legend: ✓ measured (T) · ✗ no primitive (N, reason in framework §2.2a/b) · the row "Core ops" is the harness's count.

| Op | erc1056 | erc1056w | erc721 | erc725 | erc735 | erc1155 | erc725xy | lsp8 | erc4337 | cvin |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| C2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R2 | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ |
| R3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R4 | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓* | ✓ |
| U1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| U2 | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓* | ✓ |
| U3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| U4 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| U5 | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| D1 | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓* | ✓ |
| D2 | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| D3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| V1 | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ |
| V3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| V5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| V6 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Core | 17/17 | 16/17 | 16/17 | 16/17 | 12/17 | 14/17 | 13/17 | 13/17 | 16/17 | 16/17 |

`*` ERC-4337 R4/U2/D1 are realised on the recovery guardian, not a signing delegate (§7.1); Phase 4 re-maps them to ✗ and adds U6, which changes this row to 13/17 + U6.

Class A (security lens 1), nine standards × six attacks: 43 applicable cells DEFENDED, 11 N/A, `erc725xy` absent (G). Class W (adapter conformance): 87 pass / 23 declared n/a across ten adapters. Class F/N per SUT and the Python layers: built in Phase 1 from the as-found inventory.

## Appendix D — Agent briefs (templates; the owner fills the path list and the exit criteria from §8)

Every brief contains, in this order: (1) phase and role; (2) the standing rules S1–S13 verbatim; (3) read-first list: `docs/HANDBACK_2026-10-04.md`, this plan §3–§4, the relevant charter; (4) exact path list the worker may write; (5) deliverable file names; (6) exit criteria copied from §8; (7) the gotchas from `HANDBACK_2026-10-04.md` §6 (ports 8547/8548, kill by PID, scripts that overwrite tracked results, selector shifts, library versions); (8) hand-back format: a `FOLLOWUP_<id>.md` in `docs/review03/` with before/after tables and the register rows touched.

Worker briefs needed: W0-A, W0-B · W1-A, W1-B, W1-C · W2-A · W3-A, W3-B, W3-C, W3-D · P4-1 … P4-6 · W5-A, W5-B · W6-A, W6-B, W6-C · R7-A, R7-B. Owner briefs: one per phase.

## Appendix E — Glossary

SUT subject under test · TC test case ID · RR results-register ID · E0–E7 evidence ladder · T/N/G/P/X matrix cell values · M0/M1/M1-H/M1-H/HTTP/M2 condition tags · V/E/S/U/B claim status · SC-nn scope change · `latest` the promoted run of record · `runs/` local run history · tier smoke/full/measure · charter one-page test-family specification.
