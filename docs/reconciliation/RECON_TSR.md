<!-- Read-only analysis produced 2026-10-06 for docs/REVIEW_03_PARALLEL_LINEAGES.md; branches compared: claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy @ b70081c (ours) vs origin/claude/clone-cvin-id-scs-011CUyxScetMdSQFkuQUNLTt @ fa6188e (theirs) and origin/claude/testing-suite-organization-z5j7dc @ ef2c851; merge base 3203ee8. Every number carries its source path. -->

# Recon — TSR Plan v1.0 (branch `claude/testing-suite-organization-z5j7dc`) against the grand sandbox built on this branch

**Read-only.** Branch under study: `origin/claude/testing-suite-organization-z5j7dc`, head `ef2c851` (2026-10-06 02:10 UTC), one commit on top of `origin/claude/clone-cvin-id-scs-011CUyxScetMdSQFkuQUNLTt` (`fa6188e`). This branch: `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy`, head `b70081c`.

## 0. Lineage fact that frames everything below

- `git merge-base HEAD fa6188e` = `3203ee8` (2026-09-30, "Verification pass clean; add the original prompt-and-direction record and the 2026-09-30 handback"). `fa6188e` is **not** an ancestor of this branch.
- Commits since the merge base: this branch **35**; the TSR lineage **155** (+1 for `ef2c851`).
- Paths the TSR Plan relies on that are **absent on this branch**: `1_blockchain-identity/benchmarks/` (the 18-op metrics harness), `1_blockchain-identity/test/benchmarks/` (`adapters.conformance.test.js`, `stats.test.js`), `1_blockchain-identity/results/metrics/latest/`, `1_blockchain-identity/analysis/`, `docs/CVIN-DATA-COLLECTION-FRAMEWORK.md`, `docs/HANDOFF-DATA-COLLECTION-FRAMEWORK.md`, `docs/HANDBACK_2026-10-04.md`, `docs/review02/`, `docs/REVIEW_02_CODEBASE.md`, `docs/PLAN_REVIEW_02.md`, `cv2x-testbed/tests/` (11 pytest files), `cv2x-testbed/tests/test_freshness_k.py`, `test_lifecycle_parity.py`, `1_blockchain-identity/scripts/experiment_pseudonym_pool.js`, `test/ERC1056/PseudonymPool.test.js`.
- Paths this branch has that are **absent on the TSR lineage** (`fa6188e`): `sandbox/`, `docs/PLAN_SANDBOX_AND_SUITES.md`, `docs/DEFECT_LOG.md`, `docs/FEATURE_ASYMMETRY_MATRIX.md`, `1_blockchain-identity/test/L1-identity-mechanisms/`, `1_blockchain-identity/_research-copies/`, `4_comparison-framework/feature-matrix/`.
- Same-named, different-content files on both: `docs/AFTER_ACTION_REPORT_03.md`, `_04.md`, `_05.md`; `docs/MEASUREMENT_CONDITIONS.md` register rows **#29–#32 here** (freshness-k, lifecycle parity, two "gas moved by defect fixes" rows) vs **#29–#39 there** (harness L1/L2/L3, freshness-k knee, M4 parity, ten-column tables, H5 dominance, probe, M5 pool, HTTP). `docs/AFTER_ACTION_REPORT_07.md` §1.1 on this branch already records this collision.

So the TSR Plan is an organisation plan for the *other* trunk's test body (369 Hardhat + 358 Python, harness-centred). Its as-found inventory describes a tree layout (`test/<Standard>/`, `test/security/`, `test/benchmarks/`) that this branch has already re-homed into `test/L1-identity-mechanisms/` and `test/L2-identity-system/{per-option,security}/`.

---

## 1. What the TSR Plan v1.0 proposes

Files added by `ef2c851` (`git show --stat ef2c851`):

```
docs/INDEX.md                                      |   1 +
docs/planning/TESTING_SUITE_RESULTS_PLAN.md        | 681 +++
docs/planning/TESTING_SUITE_SECOND_PASS_SHEET.md   | 257 +++
docs/planning/testing_suite/INVENTORY_AS_FOUND_2026-10-04.md | 290 +++
```

Header of `docs/planning/TESTING_SUITE_RESULTS_PLAN.md`:

> **Status:** v1.0 — plan of record for the "organised testing suite and results" work. Awaiting the author's second pass (`docs/planning/TESTING_SUITE_SECOND_PASS_SHEET.md`) before Phase 0 starts.
> **Companions:** `docs/MEASUREMENT_CONDITIONS.md` (claim register, condition tags), `docs/CVIN-DATA-COLLECTION-FRAMEWORK.md` (18-op catalogue, L1–L8 levels, falsifiers), `docs/THREAT_MODEL.md` (A1–A4, G1–G8), `docs/DID_METHOD_RUBRIC.md` (qualitative axis), `docs/HANDBACK_2026-10-04.md` (state of the trunk), `docs/INDEX.md`

### 1.1 Purpose (§0)

> *For each implementation option, which basic identity functions are tested, how (functional, adversarial, conformance, cost, latency, scale), to what evidence level, under which conditions, and where is the number?*

Six deliverables (§0, verbatim list heads): "a five-dimension **taxonomy** … and a stable **identifier scheme**"; "a machine-readable **Test Case Register** and **Coverage Matrix**, generated from the code"; "a **results pipeline** with one entry point, one results schema, run stamping, and a register check"; "an **academic-rigour layer** per test family"; "an **intake protocol** for the author's paper notebooks"; "a **multi-agent, multi-phase execution plan**".

Explicit non-goals: "it does not change any result of record, does not move files whose import paths other code depends on, does not weaken or skip any test, and does not decide the author's open framing questions".

### 1.2 Standing rules (§0.1) — inherited S1–S9, new S10–S13

| # | Rule | Why |
|---|---|---|
| S10 | Every test carries a taxonomy tag resolvable to a Test Case Register row; an untagged test fails the register build | makes the matrix generated, not typed |
| S11 | A result file carries `meta.json` (or an equivalent header) with commit, dirty flag, toolchain versions, condition tag and dataset seed, or it is not a result of record | extends the harness's run identity to every producer |
| S12 | A coverage-matrix cell has one of exactly five values: `T` tested, `N` n/a (no primitive, documented), `G` gap (primitive exists, no test), `P` paper (author's notes, not yet in repo), `X` out of scope (SC-nn) | makes gaps and paper material first-class |
| S13 | Redundancy by design: every item on paper gets a repo row with `source: paper` before it is reconciled; the paper copy is never the only copy | author's request |

### 1.3 Design principles (§2, abbreviated to the headings)

"1. **Tag, do not relocate.** Tests stay where their imports, fixtures and CI jobs expect them. … Relocation is permitted only where nothing imports the file (decided per file in Phase 3)." · "2. **Generated over typed.**" · "3. **The matrix is the finding.**" · "4. **Exact vs statistical, always labelled.**" · "5. **Falsifiable by construction.**" · "6. **Conditions travel with numbers.**" · "7. **Three tiers, one suite.** `smoke` (minutes; CI on every push), `full` (…), `measure` (metrics harness, N = 30 latency, scaling, V2V; nightly or on demand …). The tier is a tag, not a separate directory." · "8. **Redundancy with the paper.**" · "9. **Reviewable by an examiner in ten minutes.** From `docs/testing/README.md`, an examiner reaches any number's test, result file, conditions, and register row in at most three clicks."

### 1.4 Taxonomy (§3) — five dimensions + conditions

**A — Subjects under test** (§3.1): 21 rows, IDs `erc1056`, `erc1056w`, `erc721`, `erc725`, `erc725xy`, `erc735`, `erc1155`, `erc4337`, `lsp8`, `cvin`, `mobi-v1`, `mobi-v2`, `mobi-backends`, `cv2x-erc1056`, `pki`, `central`, `did-resolver`, `vc-layer`, `v2v-path`, `use-cases`, `pipeline`. "Sub-IDs are allowed where a subject has internal options that are compared (`did-resolver/ethr`, `v2v-path/ssi-warm`, `mobi-backends/erc1155`)." Appendix B gives the consolidated list (23 with sub-IDs).

**B — Basic identity functions** (§3.2): four groups. "Group B1 is the harness's 18-op catalogue verbatim (`benchmarks/lib/operations.js`), so chain SUTs need no new naming."

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

"Plus the two off-chain credential ops … **V2** issue credential … and **V4** verify credential". B2 = lifecycle events L01–L16. B3 = credential-layer K1–K12 (issue VC, presentation, selective disclosure, verify VC, verify VP, revoke/status list, schema validation, DID resolve, dereference, error handling, VIN confidentiality, freshness-k). B4 = V2V message-path M1–M8 (enrol, sign BSM, verify warm, verify cold, check revocation, resolve at message time, pseudonym rotation, revocation propagation). §7.1 proposes a new op **U6_recover_controller**.

**C — Property / test classes** (§3.3):

| Class | Name | What a test in this class establishes | Exact or statistical |
|---|---|---|---|
| **F** | Functional (positive) | the function does what the spec says on valid input | exact |
| **N** | Negative / revert | invalid input or unauthorised caller is rejected with the **exact** expected error (review 02 standard) | exact |
| **A** | Adversarial / security | an attack from the threat model (A1–A4 against G1–G8) fails; differential control shows the honest path succeeds | exact |
| **W** | Conformance | the behaviour satisfies a normative statement of an external spec … or the adapter contract (`test:conformance`) | exact |
| **G** | Cost (exact) | gas, calldata bytes, log bytes, SSTORE/SLOAD counts, bytecode size; asserted byte-identical across runs | exact |
| **L** | Latency / throughput (statistical) | N ≥ 30, median, p95, bootstrap CI, Mann–Whitney for comparisons | statistical |
| **S** | Scale | marginal cost or latency as N or history h grows; slope and O(·) class | mixed |
| **D** | Determinism / reproducibility | re-run equality gate; artifact freshness; run identity | exact |
| **I** | Integration / lifecycle | multi-party, end-to-end, computed pass/fail with forged and replayed controls (the 12 use cases, lifecycle parity) | exact |
| **Q** | Qualitative / analysis | rubric cells, capability matrix, dominance/Pareto, ratios — pure functions of results of record | derived |

**D — Evidence ladder** (§3.4): E0 "asserted in prose only" · E1 "a test exists" · E2 "the test asserts the exact expected outcome" · E3 "the test runs in CI with no skips" · E4 "a result file of record is committed with run stamp and conditions" · E5 "claim register row with status **V**" · E6 "externally validated" · E7 "replicated". "The thesis cites at E5 or above (S1)."

**E — Research mapping** (§3.5): RQ1–RQ4; H1, H1′, H2, H3, H4, H5, PKI-alternative.

**Conditions** (§3.6): "M0, M1, M1-H, M1-H/HTTP, M2 as defined; this plan adds no tag but requires every L/S/G result to carry one."

### 1.5 Identifier scheme and registers (§4)

```
TC-<SUT>-<OP>-<CLASS>[-<nn>]
TC-erc1056-U2-N-01     ERC-1056, add delegate, negative test, first of several
TC-vc-layer-K3-F       VC layer, selective disclosure, functional
TC-v2v-path-M3-L       V2V path, warm verify, latency study
TC-pipeline-*-D        determinism gates
```

Tagging: "**Mocha/Hardhat:** the `it()` title ends with ` [TC-erc1056-U2-N-01]`, or a `describe` block carries a tag that its `it()`s inherit"; "**pytest:** a marker `@pytest.mark.tc("TC-vc-layer-K3-F")` registered in `conftest.py`, or a docstring first line `TC: …`"; "**Result producers:** `meta.json` gains `"tcs": [...]`". "Untagged tests are listed in `docs/testing/UNTAGGED.md` and fail the build once Phase 3 declares the suite tagged."

Test Case Register schema (§4.2, `docs/testing/test_register.yaml` → `.csv`): fields `id, sut, op, cls, evidence (computed), condition, tier, rq, hyp, location (path:line, framework), title, guards, source (repo / paper / review-02 / audit-01), status (active / gap / n-a / scope-change(SC-nn) / paper-pending), notes`.

Results Register schema (§4.3, `docs/testing/results_register.yaml`): `id RR-<producer>-<nn>, path, producer, condition, stamp (commit, dirty, date, toolchain, seed), claims (#nn), tcs, tables, figures, chapter, status (V/S/B/E)`.

Coverage Matrix (§4.4): "`COVERAGE_MATRIX.md` is three generated views of the same register: 1. **Function × SUT** … one page per property class (F, N, A, W, G, L, S), cells `T/N/G/P/X` with TC counts and evidence level. 2. **SUT × property class** roll-up … 3. **Hypothesis × evidence**".

Claim register relationship (§4.5): "Phase 5 adds a machine-readable mirror (`docs/testing/claims.yaml`: `id, claim, tag, source, status, rrs, tcs`) … The prose row stays authoritative when they disagree".

### 1.6 Target layout (§5, "additive; nothing moves in Phases 0–2")

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

"Existing test and result locations are unchanged."

### 1.7 Definition of done (§1.2) — the acceptance criteria

1. "`docs/testing/COVERAGE_MATRIX.md` is generated by `tools/testing/build_register.py` from tags in the test code and prints, for every (subject, function, property) cell, exactly one of `T/N/G/P/X`".
2. "Every test in the repository has a register row … CI fails if a test is untagged or a row is orphaned."
3. "Every result file of record has a `meta.json`/header (S11) and a row in `docs/testing/results_register.{yaml,csv}`".
4. "One command (`make results` or `tools/testing/run_all.sh --tier=<smoke|full|measure>`) runs the suite tier, regenerates results and tables, rebuilds the two registers and the matrix, and fails on any register/CI rule violation."
5. "Each test family has a one-page **Test Family Charter**".
6. "The author's paper material has been taken in through the second-pass sheet".
7. "Chapter 5 tables and figures are listed in `docs/testing/RESULTS_PRESENTATION_PLAN.md` … and the stale-figure list in `HANDBACK_2026-10-04.md` §4.7/§4.12 is empty."

### 1.8 Phases (§8) and CI

Phase 0 freeze/baseline/re-run (`docs/testing/BASELINE_2026-10.md`, `results/superseded/<date>/`, harness re-run on HEAD) → Phase 1 inventory + taxonomy (registers v0, hand-mapped) → Phase 2 gap analysis + paper intake (sheet filled) → Phase 3 "Suite restructuring: tags, tiers, fixtures, CI" (W3-A Mocha tags + reporter hook `tc-results.json`, remove security `after()` side effect via `runs/` + `npm run security:promote`; W3-B pytest markers, pin deps, seed `cv2x_stack.py`; W3-C convert script tests, `test_use_cases.py` gains computed oracles; W3-D `run_all.sh --tier`, `testing-suite.yml`, fix stale CI headers and TARGET/FLOOR inversion) → Phase 4 fill `G` cells (P4-1 … P4-6) → Phase 5 results pipeline (`stamp.py`, producers write to `runs/<runId>/` + `promote`, harness determinism gate, `claims.yaml` cross-check) → Phase 6 rigour layer (charters, bootstrap CI + Mann–Whitney in latency tables, `PREREGISTRATION_v2.md`, rubric scored) → Phase 7 adversarial review (`docs/review03/`, `check_docs_numbers.py`) → Phase 8 external validation (Sepolia, real SUMO; author-gated).

Dependency graph (§8.1): `P0 ──► P1 ──► P2 ──┬──► P3 ──► P4 ──┐ … ├──► P5 ──► P6 ──► P7 ──► (P8)`; "Total: 10–14 agent-sessions plus author time at P2 and P7."

Agent roles (§8.2): Owner/integrator "must not … measure (owners read results, never produce them)"; Worker "only its listed paths"; Reviewer "read + report … `docs/review03/`".

### 1.9 Academic-rigour protocol (§9) and presentation plan (§10)

§9.1 statistical rules (8): N ≥ 30 after ≥ 3 warm-ups; percentile-bootstrap CI on the median, 10 000 resamples, fixed seed; "Mann–Whitney U, two-sided, with Cliff's δ as effect size; Holm correction"; exact metrics "report `mode [min, max]` and the cause" when iteration variation exists; "Every table footer: run-id, commit, condition tag, N, toolchain hash"; pre-registration before the run; replication at E7 "reported side by side, never averaged".

§9.2 charter template (8 numbered sections: establishes / oracle / design / falsifiers / threats / reporting / replication / limitations). §9.3 reporting standards: "ACM SIGSOFT Empirical Standards — *Benchmarking* … and *Engineering Research*"; "ACM Artifact Review and Badging v1.1 — … *Artifacts Available*, *Artifacts Evaluated – Functional*, and *Results Reproduced*". §9.4 threats-to-validity seed table per family G/L/A/W/I/Q.

§10 seed list of Chapter 5 artefacts T5.1–T5.16, F5.1–F5.6, App. A–C, each with source file, register rows and class; "Rule: a table in this list is regenerated by `run_all.sh --tier measure`; one that is not is not in Chapter 5."

### 1.10 Gap analysis as the plan sees it (§7.1, §7.2)

Function × SUT gaps proposed as `G`: `erc725xy × {6 attacks}` (A); `mobi-v2 × C1…V6` (no harness adapter); `U6_recover_controller` new op and ERC-4337 R4/U2/D1 re-mapped to `N` ("guardian ≠ delegate"); "Declared-unsupported ops are never asserted to throw `NotSupported` | 23 cells"; "C1 never checks R1 on its own result; U1 and U4 are the same call in 9/10 adapters"; unit files for `CVINVehicleNFT`, `CVIN_DID_ERC725`, `MOBI/ERC1056Registry`; "ERC-721 legacy tests (`regularExtended.js`, `identityBased.js`): no negatives"; "13 N/A security cells with no assertion"; "Use cases 1, 2, 4, 5, 7, 8, 9 have no explicit check; suite runs on `central`, not a chain backend"; `vc-layer × K1/K4` at M1-H/HTTP; `did-resolver × K8` ("`_resolve_ethr` synthesises offline"); `all × Q` rubric; Sepolia/real SUMO as `X`.

Rigour gaps R1–R14 (§7.2) include: R1 "No single regeneration path"; R2 "Scripts overwrite tracked results"; R3 "Stale result files presented alongside current ones: `w3c_compliance.json` (July), `sensitivity.*` (July, paris, no generator), `results_snapshot.json` (708302a)"; R4 "Statistics implemented, not used"; R7 "Claims surface hand-typed and drifted … test counts appear as 47/147/201/217/295/353/369/739"; R8 "M1–M7 work items collide with M0–M2 condition tags"; R9 "`test-contracts.yml` header says 47 tests; compliance TARGET (90) below FLOOR (93)"; R10 "Python deps unpinned"; R11 unseeded `random`; R13 "`hardhat_version` null in 5/7 testbed JSONs; short commits only".

---

## 2. The second-pass sheet and the as-found inventory

### 2.1 `docs/planning/TESTING_SUITE_SECOND_PASS_SHEET.md` (257 lines, "Sheet version: 1.0 (blank)")

Purpose: "the author's second pass over the plan, done from chat. Every item has an ID; answer by ID in any order … Items left blank take the stated default. The filled sheet is the input to Phase 2". Cell legend: "**T** tested · **N** n/a, no primitive (give the reason) · **G** gap, add it · **P** on paper, intake · **X** out of scope".

Sections and counts:

| Section | Items | Content |
|---|---|---|
| D — Decisions | D-01…D-17 + D-20…D-32 (30) | D-01 "Where the organised suite lives: a) `docs/testing/` + `tools/testing/` (additive; nothing moves) · b) new top-level `5_testing-suite/` to match `1_…4_` · c) inside `4_comparison-framework/`" default **a**; D-02 tagging mechanism (default a: tags in titles, registers generated); D-03 add `W` weak cell value ("**b** is recommended if ERC-721 legacy tests stay"); D-04 tiers (default **c**: add `external`); D-05 U6 recover op (default a); D-06 MOBI harness adapter (default a); D-07 14 non-deterministic gas cells (default **c**: fix fixture where cause is fixture, report `mode [min,max]` where it is the standard); D-08 use-case backend (default a: keep `central` + add MOBI V2); D-09 stats columns (default a: bootstrap CI + MW/Cliff's δ, Holm); D-10 producers write to `runs/` and promote (default a: all); D-11 `claims.yaml` mirror (default a); D-12 rename work items M1–M7 → W1–W7; D-13 ACM SIGSOFT + badging; D-14 replication target (default b); D-15 Phase 8 after 7; D-16 author-attributed commits, no AI trailers; D-17 version bump 0.9.0 only with Sepolia witness. D-20…D-32 = pending handback decisions (H1 wording, checker strictness, K-4, attestEvent, K-5, K-12, MOBI wording, H3 design point, M4 verdict, privacy framing, stale figures, tags/SUMO/Sepolia). |
| V — Verify the plan's reading | V-01…V-15 | e.g. V-05 "Run of record ≠ HEAD (contracts tree `6c58b31` vs `04c33c2`) should be fixed by re-running on HEAD in Phase 0"; V-07 "`test_use_cases.py` running on the centralised backend and passing on 'no exception' is a gap"; V-08 hardcoded "100 % compliance" and `COMPLIANCE_CHECKLIST` (85.7 %) "should be removed or replaced, never cited"; V-09 stale artefacts quarantined to `results/superseded/`; V-10 security `after()` side effect to remove; V-11 both external-suite denominators (336/441 and 335/336); V-14 "three-click rule"; V-15 TEST-repo onboarding stream (`TEST_ONBOARDING.md`: IMinimalSSI F1–F12, gates G0–G6) as 24th SUT or separate. |
| P — Paper-notes intake | P-01…P-20 blank rows + 9 checklist prompts | kinds `function · test-idea · result-table · figure · hypothesis · threat · scope-note · definition · other`; columns `Kind, SUT(s), Function(s), Class, One-line content / page ref, Already in repo?`. Prompts include "the 'basic identity functions' list from the sandbox guide / IMinimalSSI F1–F12". |
| C — Cell triage | 13 proposed `G`/`N`/`X` cells + free rows | `C-erc725xy-{all 6 attacks}` G; `C-mobi-v2-{C1…V6}` G; `C-{all}-U6` G cond.; `C-erc4337-{R4,U2,D1}` re-map to N; `C-{all}-{declared n/a} NotSupported assertion` G; `C-erc721-{N class, legacy files}` G; unit files G; `C-use-cases-{1,2,4,5,7,8,9} oracles` G; `C-vc-layer-K4 …` G; `C-did-resolver/ethr-K8 chain read; did:mobi` G or X; `C-{all}-Q` G; Sepolia and real-SUMO cells X pending. |
| Q — Per-phase questions | Q-0.1…Q-7.2 (17) | e.g. Q-1.1 YAML vs CSV-first; Q-1.2 one test several rows; Q-3.2 "Keep the three CI workflows and add a fourth, or consolidate into one with jobs?"; Q-5.1 `make` vs `run_all.sh`; Q-5.2 retire `benchmark_gas.js` after the harness covers MOBI? |
| R — Priorities | 9 items to rank | matrix generated; gap cells for nine chain standards; results pipeline; stats and charters; docs reconciliation; use cases on chain backend; resolver chain read; external validation; paper intake |
| O — Survey findings to triage | O-01…O-20 | Accept/Defer/Reject on the inventory's reviewer flags (I.6, II.8, III.8) |
| S — Standing rules to confirm | S10–S13 | Keep / change |
| L — Change log | 1 row | "1.0 · 2026-10-04 · session · blank sheet issued with TSR Plan v1.0" |

Nothing in the sheet is filled.

### 2.2 `docs/planning/testing_suite/INVENTORY_AS_FOUND_2026-10-04.md` (290 lines; HEAD `fa6188e`)

"Three read-only surveys (one per layer), consolidated … Nothing was executed; counts are static (`it()` / `def test_` / parametrize decorators) unless a CI total is quoted."

**Part I — `1_blockchain-identity/`**: "18 files; 293 static `it()`; ≈392 at runtime because the conformance file expands ×10". Per-file table with `it`/`expect`/revert counts and categories, e.g. `test/MOBIVID/MOBIVIDRegistry.test.js` 32/92/37; `test/security/securityScenarios.test.js` 60/119/55 "6 self-checks + 9 standards × 6 attacks with differential control; 13 N/A cells without assertion; `after()` writes to `4_comparison-framework/security-analysis/results/`"; "Security matrix standards: … **ERC-725xy absent.**" Harness: "Registered adapters (10): `erc1056, erc1056w, erc721, erc725, erc735, erc1155, erc725xy, lsp8, erc4337, cvin`. **MOBI-VID has no adapter.**"; a full adapter × op realisation table (N native / E emulated / – n/a); "Not covered by the harness: recovery (4337 `recover`), a generic add-claim op, ERC-725X `execute`, MOBI-VID." Harness mechanics (`METRICS_N` 30, run id → `results/metrics/runs/<id>/`, `gasUsed` as **mode** with `gasUsedRange`/`gasDeterministic`). Verified findings: "`HEAD:1_blockchain-identity/contracts` = `04c33c2…` ≠ `meta.measured.contractsTree` `6c58b31…`"; "**14 crud cells `gasDeterministic:false`**: cvin C1 [266945,266995], C2 [1006855,1006919], V3 [289738,289788], V5 [89962,89972]; erc721 C1 [397044,399844], U1 [176670,179470]; erc735 C2, U3, D2, V3, V5; lsp8 C1 [132515,149615], U1 [80612,83412], D2." Reviewer-flag list I.6, 11 items.

**Part II — `2_w3c-ssi-layer/`, `cv2x-testbed/`**: pytest table (8 SSI files, 11 testbed files, with node requirements); "All report via pytest only; none writes JSON." Script-style tests: "`test_use_cases.py` (1663 lines): 12 use cases on `CentralizedVehicleRegistry` (in-memory) + VC shim; 'pass' = no exception; 8 `raise RuntimeError` checks, all in use cases 3, 6, 10, 11, 12; use cases 1, 2, 4, 5, 7, 8, 9 have no explicit check"; "`test_mobi_vid.py` … `test_mobi_vid_compliance` is a **hardcoded dict printing '100%'**"; "`test_vin_encryption.py`: 6 real pytest tests, **outside CI**"; "`test_comparison.py`: blockchain numbers 'ASSUMED public-mainnet estimates — NOT measured'". Checker: "44 executed checks (DID Core 15, VC DM 17, presentations 7, selective disclosure 3, securing-mechanism deviations 2 forced FAIL) … Score = (PASS + 0.5·PARTIAL)/44: 94.3 % = 41/1/2. Writes `w3c_compliance_report.json` to **CWD**"; "`vc_verifier.py:947 COMPLIANCE_CHECKLIST` is a second hardcoded self-score (85.7 %)". External suite history "328/441 (09-24) → 336/441 (10-04 …) → **335/336** (10-04b after R1–R4) … matched pairs: 157 P→P, 36 F→P, 1 F→F, 0 P→F". SUMO: `--simulate` MockMobility, `run_v2v_stats.py` 30 seeds, "No chain involved". Reviewer-flag list II.8, 11 items.

**Part III — `4_comparison-framework/`, `docs/`, CI**: claim register summary table rows #1–#39 with tag and status; "Naming collision: `PLAN_MOBI_SUMO.md` §A.1 M1–M7 are work items"; review-02 process (64 + 2 + 1 findings); three gas instruments; CI: "`test-contracts.yml`: compile + test; header '47 tests'. `w3c-compliance.yml`: … `compliance-score` (FLOOR 93.0 enforced; TARGET 90.0 printed, below floor …)"; hypotheses drift table (H1 ratios "10.3× / ~10× / 6.9× / 2.57× / 2.63× / 3.00× / 1.10×"; H2 "93.2 % … vs 94.3 % vs 92.0 % vs 90.9 % vs 89.6 %"; "Test counts: 47 / 147 / 201 / 217 / ~295 / 302 / 351 / 353 / 369 Hardhat; 286 / 358 Python; 739 README"). Reviewer-flag list III.8, 9 items.

---

## 3. Mapping: TSR element → what exists on this branch

Legend for the right column: **built here** (with path) · **partly** · **not built here** · **built here, not in TSR**.

| TSR element | TSR location | On this branch | Status |
|---|---|---|---|
| Organising question "for each implementation option, which basic identity functions are tested, how, to what evidence level" | Plan §0 | `sandbox/grand/report/L1-asymmetry.md` (9 mechanisms × 11 options, observed, exact gas) + `sandbox/grand/report/asymmetry.md` (14 families × 13 options, declared M/I/—) + `docs/FEATURE_ASYMMETRY_MATRIX.md` (ABI counts). Answers "which function, on which option, with what gas"; does **not** carry property class, evidence level or condition tag. | partly |
| Dim A — SUT IDs (`erc1056`, `erc1056w`, …, `pipeline`) | §3.1, App. B | `sandbox/options/<slug>/` — 13 option dirs: `baseline-centralized`, `baseline-pki`, `cvin-combined`, `erc-1056-uport`, `erc-1056-vehicle`, `erc-1155`, `erc-4337`, `erc-721`, `erc-725`, `erc-725xy`, `erc-735`, `lsp8`, `mobi-vid`. Each on-chain one has `manifest.yaml`, `adapter.js`, `demos/`, `README.md`; the two baselines have `manifest.yaml` only. The two ERC-1056 variants are named in `docs/MEASUREMENT_CONDITIONS.md` §1.1 ("ERC-1056 / uPort-style" / "ERC-1056 / vehicle profile"). No option dir for `did-resolver`, `vc-layer`, `v2v-path`, `use-cases`, `pipeline`, `mobi-backends`. | partly (different IDs; see §4) |
| Dim B — 18-op catalogue C1…V6 (+V2/V4, U6) | §3.2 B1, `benchmarks/lib/operations.js` | **Absent** (no `1_blockchain-identity/benchmarks/`). The function axis here is the 9 L1 mechanisms in `1_blockchain-identity/test/L1-identity-mechanisms/_l1.js`: `create, controller-change, key-or-delegate, attribute, claim, revoke, transfer, signed-op, resolve`; and the `IdentityOption` interface in `sandbox/lib/identity_option.js` (`deploy, create, changeController, addKeyOrDelegate, setAttribute, addClaim, revoke, transfer, resolve, signedOp, capabilities`). | not built here (different, coarser axis) |
| Dim B — B2 lifecycle L01–L16, B3 K1–K12, B4 M1–M8 | §3.2 | No named catalogue. L3/L4 pytest here test records and use cases, not per-function ops. | not built here |
| Dim C — property classes F/N/A/W/G/L/S/D/I/Q | §3.3 | Not named. Implicitly: L1 = F + G (single exact sample); L2 per-option = F/N; L2 security = A (`test/L2-identity-system/security/securityScenarios.test.js`, 9 standards; `grep -c "725xy"` = 0 → ERC-725xy absent here too); L3 = W (`test_external_did_conformance_regression.py` floor 335/1; `test_internal_compliance_checker.py` floor 94.3); L4 records = D ("check the records are present, carry an environment header … They deliberately do not assert numbers"); L4 use cases = I. | not built here (layers are the organising axis instead) |
| Dim D — evidence ladder E0–E7 | §3.4 | Not built. Nearest: register status V/E/S/B in `MEASUREMENT_CONDITIONS.md`; `DEFECT_LOG.md` severity H/M/L and `reviewed: false` flags in manifests (172/182 unreviewed). | not built here |
| Dim E — RQ/H mapping per test | §3.5 | Not built. | not built here |
| Conditions M0/M1/M1-H/M1-H/HTTP/M2 | §3.6 | M0/M1/M2 exist here (`MEASUREMENT_CONDITIONS.md` §1); **M1-H and M1-H/HTTP do not** (harness absent). | partly |
| TC IDs in `it()` titles / `@pytest.mark.tc` | §4.1 | `grep -rln "TC-\|tc(" sandbox/py-suites 1_blockchain-identity/test` → no files. | not built here |
| `docs/testing/test_register.{yaml,csv}` | §4.2 | Not built. The per-option `manifest.yaml` is a register of *features* (family → stance, functions, measured, reason, reviewed), not of tests. | not built here |
| `docs/testing/results_register.{yaml,csv}` | §4.3 | Not built. | not built here |
| `docs/testing/claims.yaml` | §4.5 | Not built. | not built here |
| `COVERAGE_MATRIX.md` T/N/G/P/X, three views | §4.4 | Three different generated tables: `sandbox/grand/report/asymmetry.md` (M/I/—; "Options: 13 · families: 14 · cells: 182 · empty: 0 · unreviewed: 172/182"), `sandbox/grand/report/L1-asymmetry.md` (✓ gas / — NotApplicable / ✗ / ·; "99 records"; "N/A reasons" section; manifest agreement), `docs/FEATURE_ASYMMETRY_MATRIX.md` §2 (function counts per family). `sandbox/grand/run.py check` "fail if any option x family has no stance" ≈ TSR "no cell is blank". | partly (different vocabulary and axis) |
| `NotSupported` must be asserted for declared-unsupported ops (TSR gap, 23 cells) | §7.1 | **Built**: `NotApplicable(reason)` is "a first-class result: L1 records it, never skips silently" (`PLAN_SANDBOX_AND_SUITES.md` §1); `ADAPTER_CONVENTIONS.md`: "the reason must match the option's `manifest.yaml` stance/reason for that family; never throw for them"; AAR04: "L1 re-run **99 passing, 88/88 agreements, 0 disagreements**". | built here, not in TSR |
| Layout `docs/testing/` + `tools/testing/` | §5, D-01 | Neither exists. Equivalents: `sandbox/grand/` (`run.py`, `make_manifests.py`, `smoke.js`, `manifest.yaml`, `report/`), `sandbox/py-suites/` (`run.sh`, `pytest.ini`, `L3-ssi/`, `L4-exemplar-interactions/`), `sandbox/suites` → symlink to `1_blockchain-identity/test`. | built here under a different root |
| `run_all.sh --tier smoke|full|measure` | §5, §8 P5 | `sandbox/grand/run.py` subcommands `matrix check smoke l1 l2 py demos all`; `sandbox/py-suites/run.sh`. No tier concept; no `measure` (no N=30 producers orchestrated). `smoke` here = adapter conformance (`smoke.js`, "all 11 adapter(s) conform"). | partly |
| `build_register.py`, `stamp.py`, `check_docs_numbers.py` | §5 | Not built. `make_manifests.py` generates manifests from ABIs/benchmark notes/provider methods (a generator, not a register builder). | not built here |
| `.github/workflows/testing-suite.yml` (register gate, nightly measure) | §5 | Not built. Existing: `test-contracts.yml` runs `npx hardhat test` (collects L1+L2) and two S0 gates — "Check the MOBI contract copies are byte-identical (plan S0)" and "Check the feature-asymmetry matrix is up to date (plan S0)" (`git diff --exit-code -- docs/FEATURE_ASYMMETRY_MATRIX.md`); `w3c-compliance.yml` job `python-layers` "Python layers L3 + L4 (sandbox/py-suites/run.sh)". | partly |
| S2 "no test is skipped" | §0.1 | Honoured: L1 records N/A instead of skipping. The TSR lineage's `adapters.conformance.test.js` with "23 `this.skip()` = declared n/a" is not on this branch. | built here |
| S11 `meta.json` on every result of record | §0.1 | Partly: `sandbox/py-suites/L4-exemplar-interactions/test_experiment_records_are_well_formed.py` asserts `HEADER_KEYS = {"date_utc", "git_commit", "python_version", "cpu_model", "chain_id"}` on `pki_vs_erc1056.json`, `freshness_k.json`, `lifecycle_parity.json`; `GRAND_REPORT.md` header "Generated … at commit `7404e94`"; `L1-asymmetry.md` header carries timestamp and command. No seed, dirty flag, toolchain hash, condition tag. | partly |
| Phase 0 "Run of record ≠ HEAD → re-run" | §6.4, §8 P0 | Done in substance for this tree: AAR06 "Results of record re-executed on the final contracts"; deltas committed as `4_comparison-framework/results/gas_moved_by_defect_fixes_2026-10-04.json` and `…_pass06.json`; register #31/#32 list moved cells. No `BASELINE_*.md`, no `results/superseded/`. | partly |
| `runs/<runId>/` + explicit promote; `results/superseded/` | §8 P5, R2, R3 | Not built. Stale files TSR names are present here too: `4_comparison-framework/results/sensitivity.{json,csv,tex}` and `w3c_compliance.json`. Mitigation built for one producer: V2V smoke uses `--results` to a temp dir ("committed results are never rewritten", `sandbox/py-suites/README.md`). | partly |
| Gap `erc725xy × 6 attacks` (A) | §7.1 | Same gap here (0 matches for 725xy in `securityScenarios.test.js`; 9 `describe` blocks). | not built here (gap shared) |
| Gap "unit files for `CVINVehicleNFT`, `CVIN_DID_ERC725`, `MOBI/ERC1056Registry`" | §7.1 | Partly closed: `test/L2-identity-system/per-option/ERC1056/ERC1056Registry.regression.test.js` exists; ERC-725 and `CVINVehicleNFT` have no dedicated L2 unit file, but `sandbox/options/erc-725/demos/*.js` and `erc-721/demos/*.js` exercise every public function with assertions (AAR04 S7: "every public function of every contract exercised (coverage computed from the ABIs)"). | partly |
| Gap "ERC-721 legacy tests … no negatives" | §7.1 | Still present: `per-option/ERC721/regularExtended.js`, `identityBased.js`, `combined.js` moved unchanged (S4). Regressions added: `payTollAfterRenounce.regression.test.js`, `vinNormalisation.regression.test.js`. | gap shared |
| Gap "use cases 1,2,4,5,7,8,9 no explicit check; central backend" | §7.1, V-07 | Same here: `sandbox/py-suites/L4-exemplar-interactions/test_lifecycle_use_cases.py` — "Its pass criterion per use case is 'the function returns without raising'" … "Success == returns normally." The use cases now run in CI as 12 pytest cases (an improvement TSR's lineage lacks: there "none (not in CI)"). | partly |
| Gap "recovery (4337 `recover`) not a catalogue op" | §7.1 | Exercised by `sandbox/options/erc-4337/demos/keys-delegates.js` ("set / read / replace / clear of the guardian, recovery"); defect D15 recorded. Not a test row. | partly |
| Gap "ERC-725X `execute` not covered" | Inventory I.2 | Exercised by `sandbox/options/erc-725/demos/signed-execution.js` with an observable `CVINExecuteTarget`; found to be a stub (D23). | built here, not in TSR |
| Gap "a generic add-claim op" | Inventory I.2 | L1 mechanism `claim` (`05-claim.test.js`): "claim ok 5 / na 6". | built here, not in TSR |
| Gap "MOBI-VID has no adapter" | §7.1 | `sandbox/options/mobi-vid/adapter.js` exists and is in L1 (11 options); TSR's D-06 `mobi.adapter.js` is for the harness, which is absent here. | built here (different harness) |
| Charters per class (`docs/testing/charters/`) | §9.2 | Not built. Per-option `README.md` under `sandbox/options/<slug>/` have "Asymmetry notes" (identity model, veracity/automation, cryptography/hashing, implemented-but-not-compared, observed defects) — per option, not per property class. | not built here |
| Statistical rules (bootstrap CI, MW U, Cliff's δ, Holm) | §9.1 | Not built; no N≥30 producers are orchestrated here. | not built here |
| Pre-registration v2, falsifier checks `TC-pipeline-H<n>-D` | §8 P6 | Not built. | not built here |
| `RESULTS_PRESENTATION_PLAN.md` (T5.1–T5.16) | §10 | Not built; chapter 5 tables were regenerated by script in pass 06 (AAR06 G5) without a presentation register. | not built here |
| `PAPER_INTAKE.md`, second-pass sheet | §11 | Not built. | not built here |
| `check_docs_numbers.py` | §5, R7 | Not built. Hand-typed counts present here too: `.github/workflows/test-contracts.yml` header "47 tests pass"; `1_blockchain-identity/test/README.md` "68-scenario harness" vs 69 `it(` lines; AAR04 "400 automated tests" vs GRAND_REPORT 386+94. | not built here |
| Three-click rule / `docs/testing/README.md` entry point | §2.9 | `sandbox/README.md`, `1_blockchain-identity/test/README.md`, `sandbox/py-suites/README.md`, `docs/INDEX.md` rows for `FEATURE_ASYMMETRY_MATRIX.md` and `PLAN_SANDBOX_AND_SUITES.md`. No single "which test covers what, where is the number" entry. | partly |
| `docs/INDEX.md` canonical row for the suite question | `ef2c851` diff | Not present here (INDEX here still says register "#1–#28" and names `HANDBACK_2026-09-30.md`). | not built here |
| Defect register | — (TSR has none; its lineage has `REVIEW_02_CODEBASE.md` K/H/S/T/Q findings) | `docs/DEFECT_LOG.md` D1–D27 with severity, commit, regression-test owner, §C "still open" table, §D usage rule ("A defect with severity **H** blocks any chapter claim that depends on the affected path"). | built here, not in TSR |
| Feature manifests (per option, reviewed flag, generator rules) | — | `sandbox/options/*/manifest.yaml` (13), `sandbox/grand/manifest.yaml` (union, 14 families), `sandbox/grand/make_manifests.py` with `REVIEW` rules; "Regeneration preserves any family a human has marked `reviewed: true`". | built here, not in TSR |
| 92 feature demos, 1,722 steps, one JSON per step with gas + on/off-chain flag | — | `sandbox/options/<slug>/demos/*.js`; `sandbox/grand/report/demos.{json,md}` ("Totals: 92 demos · 1722 steps · 62 flagged · failures: 0"). | built here, not in TSR |
| Generated ABI feature matrix with CI staleness gate | — | `4_comparison-framework/feature-matrix/make_feature_matrix.py` → `docs/FEATURE_ASYMMETRY_MATRIX.md`; gate in `test-contracts.yml`. | built here, not in TSR |
| MOBI contract byte-identity CI check (K-5/K-12 in TSR terms) | TSR D-24/D-25 pending | `test-contracts.yml` step "Check the MOBI contract copies are byte-identical (plan S0)". | built here, not in TSR |
| Conformance *record* regression as a test | — | `L3-ssi/test_external_did_conformance_regression.py` (`FLOOR_PASSED, MAX_FAILED = 335, 1`, reads `docs/conformance/reports/rerun-2026-10-03/jest-cvin/*.json`); `test_internal_compliance_checker.py` (94.3 floor). | built here, not in TSR |
| Grand runner report | — | `sandbox/grand/report/GRAND_REPORT.md`: stage table (smoke ✓; L1 99/0; L1+L2 386/0; L3+L4 94; demos 92 / 1722 steps / 62 flagged / 0 failures). | built here, not in TSR |

---

## 4. Conflicts of naming and layout, with a recommendation each

| # | Conflict | TSR side | This branch | Recommendation |
|---|---|---|---|---|
| 1 | **Where Hardhat tests live** | Principle 2.1 "Tag, do not relocate"; inventory and §6.1 assume `1_blockchain-identity/test/<Std>/*.js`, `test/security/`, `test/benchmarks/`. | S4 already moved them with `git mv`: `test/L2-identity-system/per-option/<Std>/` (24 files incl. regressions) and `test/L2-identity-system/security/`; `test/L1-identity-mechanisms/` added; `sandbox/suites` symlink. AAR04: a first attempt to move files out of the Hardhat project was reverted because "Node resolves `chai`/Hardhat relative to each file". | Keep the layered layout (done, CI green, imports intact). TSR's `location` field is `path:line`, so tagging works on either layout; update TSR §6.1 and the inventory paths when the lineages merge. Give the TSR lineage's `test/benchmarks/*` a home as `test/L2-identity-system/harness/` (class W/pipeline) rather than leaving a third top-level test dir. |
| 2 | **Where the organised suite lives** (D-01) | default a) `docs/testing/` (generated registers, matrix, charters) + `tools/testing/` (builder, runner, stamp, docs-number check). | `sandbox/grand/` (runner, generator, report), `sandbox/py-suites/` (L3/L4), `sandbox/options/` (per-option). No `docs/testing/`, no `tools/`. | Adopt a split by kind: *generated documents* (coverage matrix, registers, charters, presentation plan) in `docs/testing/` as TSR proposes; *executables* stay under `sandbox/grand/` (already the one entry point) — i.e. answer D-01 with "a, but `tools/testing/` = `sandbox/grand/`". Make `build_register.py` read the sandbox manifests and `report/L1-asymmetry.json` as inputs so the two matrices share one source. |
| 3 | **"L1–L4" / "L1–L8" collision** | TSR companions list "`CVIN-DATA-COLLECTION-FRAMEWORK.md` (18-op catalogue, L1–L8 levels)"; inventory I.3 "Scenarios: `crud` (L1), `lifecycle` (L2), `scale` (L3), `batch` (L4), `throughput` (L5), `resolve` (L6)"; register #29–#31 there say "harness L1 / L2 / L3/L6". | L1–L4 are the **suite layers** (`L1-identity-mechanisms`, `L2-identity-system`, `L3-ssi`, `L4-exemplar-interactions`), directory names and CI job names. | A second collision of exactly the kind TSR's D-12 addresses for M-numbers. Since the suite layers are paths, rename the harness scenario levels in prose (e.g. "scenario S-crud … S-resolve" or "H1–H6") and add a D-row to the sheet. Never both meanings in one table. |
| 4 | **Matrix cell vocabulary** | S12: `T/N/G/P/X` (+`W` weak, D-03) = *test coverage* per (SUT, function, class). | Manifests: `measured-in-comparison` / `implemented` / `not-applicable` (M/I/—) = *declared stance*; L1 report: ✓ gas / — / ✗ / · = *observed outcome*; ABI matrix = counts. | They answer different questions; keep all, but define the derivation once: manifest `not-applicable` ⇒ TSR `N` (reason copied); L1 ✓ ⇒ `T` at ≥E3 for classes F and G(single-sample); manifest `implemented` with no L1/L2/demo row ⇒ `G`. Add TSR's `W` for the ERC-721 legacy files, which are still here unchanged. |
| 5 | **SUT identifiers** | `erc1056`, `erc1056w` (wrapper mode), `cv2x-erc1056`, `mobi-v1`, `mobi-v2`, `mobi-backends`, `cvin`, `pki`, `central`. | Directory slugs `erc-1056-uport`, `erc-1056-vehicle`, `mobi-vid`, `cvin-combined`, `baseline-pki`, `baseline-centralized`. `MEASUREMENT_CONDITIONS.md` §1.1 here names the two ERC-1056 variants with their provenance rows. | Use the sandbox slugs as TC `<SUT>` tokens (they resolve to a directory with manifest, adapter, demos, README — the three-click rule for free). Map TSR `erc1056`+`erc1056w` → `erc-1056-uport` (wrapper is a sub-ID `erc-1056-uport/w`), `cv2x-erc1056` → `erc-1056-vehicle`, `mobi-v1`/`mobi-v2` → `mobi-vid/v1`, `mobi-vid/v2`. Keep TSR's non-option SUTs (`did-resolver`, `vc-layer`, `v2v-path`, `use-cases`, `pipeline`) as IDs without option dirs. |
| 6 | **Function axis** | 18-op C1…V6 (+K, M, L groups), finer than mechanisms; TSR §7.1 notes U1≡U4 in 9/10 adapters. | 9 L1 mechanisms; 14 capability families; `IdentityOption` 10 methods. | Use C1…V6 as the TSR function axis (it is finer and already names the measured ops) and publish a fixed mechanism→op map in `_l1.js`'s header: create→C1/C2, controller-change→U1, key-or-delegate→U2(+R4), attribute→U3, claim→(no harness op; propose **V7 add-claim** alongside TSR's U6), revoke→D1/D2/V5, transfer→U4, signed-op→U5, resolve→R3. The families stay the manifest axis (they cover things no op has: token economics, roles, VIN linkage, off-chain creation). |
| 7 | **Results organisation** | `runs/<runId>/` then explicit `promote` to `latest/`; `results/superseded/<date>/`; `meta.json` with `tcs`. | Reports regenerated in place under `sandbox/grand/report/`; producers under `4_comparison-framework/results/` overwrite tracked files (TSR R2 applies here: `sensitivity.*`, `w3c_compliance.json` present and stale); delta files `gas_moved_by_defect_fixes_*.json` record moves. | Adopt `runs/`+promote and `superseded/` for *results of record*. Treat `sandbox/grand/report/*` as *derived reports* (regenerable, already commit-stamped) — exempt from promote but given a `meta.json` (commit, dirty, node/hardhat versions) so S11 holds. Keep the `gas_moved_by_*` delta-file practice; it is the concrete form of TSR's "old value kept as S". |
| 8 | **Claim register numbering** | Rows #29–#39 (harness, knee, parity, dominance, probe, pool, HTTP). | Rows #29–#32 (freshness-k, parity, two gas-moved rows). | Renumber one side on merge; TSR R8 already proposes `claims.yaml` — the merge is the moment to introduce it with stable string IDs (`CL-freshness-k`) instead of ordinals. AAR07 §1.1 here flags the collision; TSR V-05/§6.4 does not know of it. |
| 9 | **Same-named after-action reports** | `AFTER_ACTION_REPORT_03/04/05.md` (review-2 passes). | `AFTER_ACTION_REPORT_03/04/05.md` (sandbox passes) + `_06`, `_07`. | Suffix by lineage on merge (`_04_sandbox.md` / `_04_review2.md`) and let `docs/INDEX.md` list both; do not merge content. |
| 10 | **Hand-typed test totals** | "369 Hardhat / 358 Python" (TSR §6), with R7 listing nine historical Hardhat counts. | "386 Hardhat + 94 Python" (GRAND_REPORT), "400 automated tests" (AAR04 §3b, pre-pass-06), "68-scenario harness" (`test/README.md`) vs 69 `it(`, "47 tests pass" (`test-contracts.yml` header, also flagged by TSR R9). | Adopt TSR's `check_docs_numbers.py`; make `sandbox/grand/run.py all` the only emitter of totals (it already prints them) and have READMEs cite `GRAND_REPORT.md` instead of numbers. |
| 11 | **Tiers vs layers** | smoke / full / measure (+`external`, D-04) as *tags*, orthogonal to location. | Layers L1–L4 are *directories*; `run.py smoke` is adapter conformance, not a quick CI tier. | Keep layers as the content axis and add TSR tiers as tags: today L1+L2+L3+L4 are all `full`; `measure` is empty on this branch until the harness arrives; `external` = the manual external-suite run that `test_external_did_conformance_regression.py` guards. |
| 12 | **Sandbox README path claim** | — | `sandbox/README.md`: "`suites/L1..L4` — the layered test suites", but `sandbox/suites` symlinks only to `1_blockchain-identity/test` (L1, L2); L3/L4 live in `sandbox/py-suites/`. `1_blockchain-identity/test/README.md` says "L3 … and L4 … live under `sandbox/suites/`'s Python siblings". | Internal inconsistency on this branch; fix the README wording when the TSR entry-point README is written. |
| 13 | **Commit attribution** | D-16 "author-attributed, no AI trailers (repo standing rule B.1)". | This branch's commits are author-attributed (`git log` shows "Nikhil Prakash"); the session reminder here asks for `Co-Authored-By`/`Claude-Session` trailers. | Follow the repository rule (TSR D-16 / S6) if it is confirmed in the sheet; it is the author's standing instruction. Note it for whoever commits a merge. |

---

## 5. What to take from each side

### 5.1 TSR elements this branch lacks and should adopt

1. **TC identifiers and tagging in test titles/markers** (§4.1) plus the generated `test_register` — nothing here can answer "which tests guard this cell" without reading files. The L1 files are already parameterised per option, so a `describe("L1-01 create [TC-<slug>-C1-F]")` pattern is a mechanical change.
2. **Property-class and evidence-level columns** on the existing matrices. `L1-asymmetry.json` already holds `(option, mechanism, outcome, gasUsed, reason)`; adding `cls` and `evidence` fields makes it a TSR register fragment.
3. **S11 run stamping for every producer** and `runs/`→`promote` (§8 P5, D-10): `4_comparison-framework/results/*` is still overwritten in place here; `sensitivity.*` has no generator and `w3c_compliance.json` is the July file, exactly as TSR R3 says.
4. **`results/superseded/<date>/` quarantine** (Phase 0, V-09).
5. **Charters per class** (§9.2), particularly G (what number is reported when gas varies — this branch reports single exact samples in L1 and never states iteration variance) and I (the use-case oracle rule; the L4 docstring itself documents the "returns without raising" criterion).
6. **Statistical rules §9.1** for the latency rows this branch carries (#21 PKI vs ERC-1056 n=50, #27 V2V N=30 marked **B**, #29 freshness-k, #30 parity): CI columns, Mann–Whitney/Cliff's δ, footer fields.
7. **`claims.yaml` mirror** (§4.5, D-11) — needed anyway to resolve the #29–#39 vs #29–#32 collision.
8. **`check_docs_numbers.py`** (R7) — see §4 row 10 for the drifted counts on this branch.
9. **Three-click entry README** (`docs/testing/README.md`) and the `docs/INDEX.md` row from `ef2c851`.
10. **`W` cell value** (D-03) for `per-option/ERC721/regularExtended.js` and `identityBased.js`, which TSR correctly calls weak and which were moved here unchanged.
11. **The paper-intake protocol and the second-pass sheet** (§11, sheet section P) — the author's notebooks are "not in the repository" on both lineages (AAR04 §0 note; TSR §1.1).
12. **Inventory findings that hold on this branch and have no counter-measure here**: `test_mobi_vid.py` hardcoded "100%" compliance (file present under `cv2x-testbed/scripts/`); `test_comparison.py` "ASSUMED" figures; `test_vin_encryption.py` outside CI; `requirements.txt`/unpinned deps (`python-layers` job runs `pip install eth-account coincurve cryptography web3 pytest` with the comment "Unpinned: see the header note"); `test-contracts.yml` header "47 tests pass"; compliance TARGET/FLOOR inversion in `w3c-compliance.yml`; unseeded `random` in `cv2x_stack.py`.
13. **ERC-725xy in the security matrix** (TSR §7.1 first row) — the gap is identical here.

### 5.2 What this branch has that the TSR Plan should reference (and currently cannot, since its lineage lacks `sandbox/`)

1. **`NotApplicable` as a recorded, manifest-checked result** — closes TSR's "declared-unsupported ops are never asserted" gap by construction and satisfies S2 better than the TSR lineage's 23 `this.skip()`. TSR's `N` cell should be *derived from* the manifest stance and the L1 reason text.
2. **Per-option manifests with `reviewed` flags and generator `REVIEW` rules** (`sandbox/grand/make_manifests.py`) — the "generated over typed" principle already applied to the feature axis; 182 cells, 0 empty, 172 awaiting the author's review (a ready-made section for the second-pass sheet).
3. **L1 cross-option table with exact gas per mechanism** (`report/L1-asymmetry.md`, 99 records, 11 options) — a class-G/F sheet for the function × SUT view that the harness-centred TSR seeds only for its 10 adapters (App. C) and without MOBI.
4. **92 demos / 1,722 steps with ABI-computed 100 % public-surface coverage** (`report/demos.md`) — evidence for TSR's "unit files missing" cells (`CVINVehicleNFT`, `CVIN_DID_ERC725`) and for the ops TSR says the harness does not cover (4337 `recover`, ERC-725X `execute`, add-claim). They are not TC rows yet, but each JSON step is a candidate E1/E2 record.
5. **`docs/DEFECT_LOG.md` D1–D27** with §D's rule that an **H** defect blocks dependent chapter claims — a register TSR has no analogue for; it is the natural `source: sandbox` for register rows and for TSR's "falsifiable by construction" principle (each fixed defect has a regression test in the owning layer).
6. **Two CI gates TSR's pending decisions need**: MOBI copies byte-identical (TSR K-5/K-12 → D-24/D-25) and feature-matrix freshness (`test-contracts.yml`).
7. **Conformance record regressions as tests** (L3: 335/336 floor, 94.3 floor) — the executable form of TSR's "guards" field for register rows #4 and #24.
8. **L4 schema tests with the explicit cross-host rule** ("numbers are never asserted across hosts") — a working precedent for TSR's E7 replication caveat and for its D class.
9. **Use cases in CI as 12 pytest cases** with a collection-time guard (`assert [n for n, _, _ in uc.USE_CASES] == [str(i) for i in range(1, 13)]`) — TSR's lineage still has them "not in CI".
10. **Results re-executed after every fix pass with committed delta files** (`gas_moved_by_defect_fixes_2026-10-04.json`, `…_pass06.json`; register #31/#32) and the external DID suite re-run on a registry-minted DID (335/336) — concrete Phase-0-style practice TSR describes but has not started.
11. **The ERC-1056 fork named as two sub-options** (`MEASUREMENT_CONDITIONS.md` §1.1) and the `_research-copies/` archive — TSR's SUT table lists `cv2x-erc1056` with the K-5 caveat but has no name for the vehicle-profile variant.
12. **One-command grand runner with a stage table** (`sandbox/grand/run.py all` → `GRAND_REPORT.md`) — the skeleton of TSR's `run_all.sh`; it lacks tiers, stamping and register building, but it already orchestrates smoke → L1 → L1+L2 → L3+L4 → demos → matrix.

### 5.3 Bottom line for the merge

TSR is a taxonomy-and-register plan written for the harness trunk; this branch is an executed layered suite written for the sandbox trunk. They do not contradict each other on principle (both: generated over typed, no skips, n/a is a result, conditions travel with numbers), but they conflict on five names (test location, suite root, L-levels, cell vocabulary, SUT IDs) and on the claim-register numbering. The cheapest reconciliation is: keep this branch's layout and runner as the executable half, adopt TSR's identifiers, registers, stamping, charters and statistics as the documentation half, and feed `build_register.py` from the sandbox manifests and L1/demos JSON so the coverage matrix and the asymmetry matrix are two views of one source.
