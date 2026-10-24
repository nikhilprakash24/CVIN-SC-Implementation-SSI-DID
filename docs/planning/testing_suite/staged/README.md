# Staged patch series v2 — TSR Phase 3 (register) and Phase 6 (charters) for the trunk

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-24. **Supersedes:** v1 of 2026-10-22 (based on `87334d6`).
**Plan:** `docs/planning/TESTING_SUITE_REPLAN_2026-10-22.md` §9. **Base:** trunk
`claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy` at `1fba094`. **Not applied anywhere yet.**

## Why v2
The trunk's branch review of 2026-10-24 (`docs/planning/BRANCH_REVIEW_2026-10-24.md`, T-12) says of this branch:
do not merge the branch, whose harness results predate A6's run of record; review the staged series and take the parts
that A5 and A7 did not already cover. Between v1 and v2 the trunk did WM-2 A7 (376 Python tests registered from the grand
runner's per-test record, covering `2_w3c-ssi-layer` and `sandbox/py-suites`) and B3 (`LATENCY_CHARTER.md`). v2 therefore:
- registers only the bodies A7 does not: per-option contract tests, harness/stats tests, the testbed's Python tests,
  Phase 2 prototypes, promote-step tests and layer 5 (which reached the trunk with the lineage merge);
- treats A7's files as results-derived in the completeness guard;
- drops this branch's latency charter and links the trunk's.

## Contents
| Patch | Effect on the trunk |
|---|---|
| `0001-Test-register-…patch` | `build_register.py` gains a static source parser and `--check-complete`; new `unit_rules.yaml`; regenerated `test_register.yaml` and `coverage_matrix.md` |
| `0002-Test-family-charters-…patch` | `docs/testing/charters/` (index + F, N, A, W, S, D, I, Q); `check_charters.py` with `--probe` |

No test, contract, result of record or register row is changed.

## Gates (fresh checkout of `1fba094` with the series applied, 2026-10-24)
| Gate | Result |
|---|---|
| Existing 681 register entries | carried byte-identical |
| New entries | 529 for 527 tests |
| Python per directory vs pytest's distinct collected functions | testbed 127 = 127, Phase 2 backends 9 = 9, promote step 13 = 13, layer 5 40 = 40 |
| Unmapped / duplicate ids | 0 / 0 (two new trunk files were refused until mapped: the SUMO replay-cache tests and layer 5) |
| `build_register.py --check`, `--check-complete` | current; pass; both probes fail as intended (`gate_probe_check_complete.txt`) |
| `check_charters.py`, `--probe` | pass (15 rows cited, all exist); probe fires |
| `tools/prepush_check.sh` | PREPUSH OK (`gate_prepush.txt`) |
| `git am` onto `1fba094` | clean |

Not run: the test suites themselves (no test changed) and CI (nothing pushed to the trunk).

## To apply (the author's call)
```bash
git checkout claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy
git am <this branch>/docs/planning/testing_suite/staged/*.patch
python3 docs/testing/build_register.py --check && python3 docs/testing/build_register.py --check-complete
python3 docs/testing/check_charters.py && bash tools/prepush_check.sh
```
If the trunk has moved, regenerate `test_register.yaml` and `coverage_matrix.md` with `build_register.py` instead of
resolving their hunks by hand. A trunk session adding these checks to CI should also add `--check-complete` and
`check_charters.py` to `tools/prepush_check.sh`.
