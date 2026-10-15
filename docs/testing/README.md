# docs/testing — the organised testing suite and results (TSR Plan, Phase 1 v0)

**Plan of record:** `docs/planning/TESTING_SUITE_RESULTS_PLAN.md` · **Second pass:** `docs/planning/TESTING_SUITE_SECOND_PASS_SHEET.md` · **As-found survey:** `docs/planning/testing_suite/INVENTORY_AS_FOUND_2026-10-04.md`

This directory answers one question: *for each implementation option, which basic identity functions are tested, how, to what evidence level, under which conditions, and where is the number?*

## Three clicks

1. `COVERAGE_MATRIX.md` — Function × Subject per property class (F functional, N negative, A adversarial, W conformance, G cost, L latency, D determinism, I integration). A cell is `T<n>` (n asserting tests/measurements), `N` (declared no primitive), or `·` (no row yet).
2. `test_register.csv` — one row per (test, subject): ID, subject, function, class, evidence level (E1 exists … E5 register V), condition tag, tier, hypothesis, file:line, title.
3. `results_register.csv` (result files of record → producer, stamp, gate, claim rows, tables) and `claims.csv` (machine mirror of the claim register in `docs/MEASUREMENT_CONDITIONS.md` §3; the prose stays canonical).

## How these files are made

| File | Made by | Hand-edited? |
|---|---|---|
| `test_register.csv/.json`, `COVERAGE_MATRIX.md`, `UNTAGGED.md`, `UNMAPPED.md` | `python3 tools/testing/build_register.py` | never |
| `tools/testing/mapping_rules.json` | hand | yes — the only place a wrong mapping is corrected (Phase 2) |
| `results_register.csv`, `claims.csv` | hand (Phase 1 v0); Phase 5 generates `results_register` from `meta.json` stamps | yes |
| `BASELINE_2026-10.md` | hand, from the Phase 0 runs | yes |

Phase 1 v0 maps tests by **path and title rules**; it is a heuristic first pass and is reviewed in Phase 2. Phase 3 puts an explicit `[TC-<sut>-<op>-<cls>]` tag in every test title (Mocha) or `@pytest.mark.tc` marker (pytest), after which `UNTAGGED.md` must be empty and `build_register.py --strict` gates CI.

## Identifiers

`TC-<sut>-<op>-<cls>[-<nn>]`, e.g. `TC-erc1056-U2-N-0017`. Subjects, functions and classes are defined in the plan §3. Harness rows are `TC-<adapter>-<op>-{G,L}-harness` and read the run of record (`1_blockchain-identity/results/metrics/latest/`).

## Tiers

`smoke` (not yet defined), `full` (every functional/security/conformance suite; CI on push), `measure` (metrics harness, N = 30 latency, scaling, V2V; nightly or on demand), `none` (script-style tests outside CI, to be converted in Phase 3).

## Standing rules

S1–S13 in the plan §0.1. In particular: no test is skipped or weakened; a number enters a chapter only with a register row of status V; a result without a stamp is not of record.
