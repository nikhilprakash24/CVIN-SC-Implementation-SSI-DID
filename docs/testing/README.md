# Testing — the organised suite, as it stands after the merge of 2026-10-06

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Status:** entry point. The *plan* is `docs/planning/TESTING_SUITE_RESULTS_PLAN.md` (TSR v1.0,
written on the review-2 trunk on 2026-10-06); the *executable half* already exists on this
trunk as the grand sandbox. This page says how the two fit, what is done, and what the TSR
plan still asks for. The 40-row mapping and the 13 naming conflicts with their resolutions
are in `docs/reconciliation/RECON_TSR.md` §3–§5.

## 1. Three clicks to any test

| What you want | Where it is | One command |
|---|---|---|
| Run everything, get one stage table | `sandbox/grand/run.py` → `sandbox/grand/report/GRAND_REPORT.md` | `python3 sandbox/grand/run.py all` |
| The uniform mechanisms, every option, one table of gas | `1_blockchain-identity/test/L1-identity-mechanisms/` → `sandbox/grand/report/L1-asymmetry.md` | `python3 sandbox/grand/run.py l1` |
| Per-option contract tests, regression tests and the strict security harness | `1_blockchain-identity/test/L2-identity-system/{per-option/<Std>,security}` | `cd 1_blockchain-identity && npx hardhat test` |
| The metrics harness (18-op catalogue, all nine standards) | `1_blockchain-identity/benchmarks/` → `results/metrics/latest/` | `cd 1_blockchain-identity && npm run metrics && npm run metrics:analyze` |
| SSI layer, resolver, VC verifier, testbed providers (Python) | `2_w3c-ssi-layer/**/tests`, `cv2x-testbed/tests` | see `.github/workflows/w3c-compliance.yml` `python-full-suite` (node on 8548) |
| Conformance records as tests, use cases, experiment schemas (Python) | `sandbox/py-suites/{L3-ssi,L4-exemplar-interactions}` | `bash sandbox/py-suites/run.sh` |
| Every public function of every contract exercised, with gas and observations | `sandbox/options/<slug>/demos/*.js` → `sandbox/grand/report/demos.md` | `python3 sandbox/grand/run.py demos` |
| What each option declares it can do (reviewed stances) | `sandbox/options/<slug>/manifest.yaml`, `docs/FEATURE_ASYMMETRY_MATRIX.md` | `python3 sandbox/grand/make_manifests.py` |
| What the sandbox found wrong, and its status | `docs/DEFECT_LOG.md` | — |
| Which number is cited where, under which condition | `docs/MEASUREMENT_CONDITIONS.md` | — |

## 2. How the TSR plan maps onto what exists

The TSR plan's five dimensions (subject, identity function, property class, evidence level,
condition) are the right description of this body of tests; its *names* differ from the
ones already in use. Resolution taken at the merge (RECON_TSR §4):

| TSR element | Here | Decision |
|---|---|---|
| Test location "tag, do not relocate" (`test/<Std>/`) | layered `test/L1-identity-mechanisms`, `test/L2-identity-system/per-option/<Std>`, `test/L2-identity-system/security`, `test/benchmarks` | keep the layered layout (imports intact, CI green); TSR tags go into test titles on either layout |
| Suite root `docs/testing/` + `tools/testing/` | documents here; executables in `sandbox/grand/` | adopt the split: generated documents under `docs/testing/`, `tools/testing/` ≡ `sandbox/grand/` |
| "L1–L8" harness scenario levels vs "L1–L4" suite layers | L1–L4 are directory and CI names | the harness levels are renamed in prose (crud / lifecycle / scale / batch / throughput / resolve); never both meanings in one table |
| Cell vocabulary `T/N/G/P/X(+W)` | manifests `M/I/—`; L1 report `✓/—/✗`; demos coverage | derive TSR cells from the manifests and the L1/demo JSON (manifest `not-applicable` ⇒ `N` with its reason; L1 `✓` ⇒ `T`; `implemented` with no test ⇒ `G`) |
| SUT ids `erc1056`, `erc1056w`, `cv2x-erc1056`, `mobi-v1/v2` | sandbox slugs `erc-1056-uport`, `erc-1056-vehicle`, `mobi-vid` | use the slugs (each resolves to a directory with manifest, adapter, demos, README) |
| Function axis: 18 ops C1…V6 | 9 L1 mechanisms; 14 manifest families | ops for the harness and TC tags; families for the manifests; a fixed mechanism→op map to be published in `_l1.js` |
| Results `runs/<id>/` → promote → `latest/`, `superseded/` | the harness already does it; `4_comparison-framework/results/*` are overwritten in place with `gas_moved_by_*` delta files | adopt promote/superseded for the results of record; keep the delta files |
| Register numbering | one register after the merge (#1–#43) | TSR's `claims.yaml` with stable string ids is the way out of ordinal collisions — next pass |
| Same-named after-action reports | resolved at the merge: `docs/review02/AAR_REVIEW2_0x.md` vs `docs/AFTER_ACTION_REPORT_0x.md` | — |
| Hand-typed totals | drift exists on both lineages | adopt `check_docs_numbers.py`; READMEs cite `GRAND_REPORT.md` |

## 3. What is done and what the plan still asks for

**Done (by the sandbox lineage, before the plan existed):** one entry point that orchestrates
smoke → L1 → L1+L2 → L3+L4 → demos → matrix; `NotApplicable` as a manifest-checked result;
per-option manifests with review flags; 100 % public-surface demo coverage; the defect log;
conformance records as tests; use cases in CI; delta files after every fix pass; MOBI
byte-identity and matrix-freshness CI gates.

**Done (by the review-2 lineage):** the metrics harness with its run identity and toolchain
pinning; the strict security harness with exact expected reverts; every Python suite in CI
with "a skip fails the job"; the artifact-freshness gate.

**Still to do (TSR phases 1–8, in the plan's order):** TC identifiers in test titles and
pytest markers; the generated test/results/claims registers and the coverage matrix fed from
the manifests and the L1/demo JSON; stamping of every producer (`meta.json` with commit,
dirty flag, toolchain) and `runs/`→promote for the results of record; charters per property
class (G: what is reported when gas varies; I: the use-case oracle); the statistical rules for
the latency rows; `check_docs_numbers.py`; the chapter-5 presentation plan; the paper-intake
protocol. The second-pass sheet (`docs/planning/TESTING_SUITE_SECOND_PASS_SHEET.md`) holds the
30 decisions the author owns before phase 1 starts.
