# Staged patch series — TSR Phase 3 (register) and Phase 6 (charters) for the trunk

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-22. **Plan:** `docs/planning/TESTING_SUITE_REPLAN_2026-10-22.md`.
**Base:** trunk `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy` at `87334d6`. **Not applied anywhere yet.**

## Why it is staged and not merged
A merge of the trunk into this branch was refused by the session's permission policy, and the trunk's status note of
2026-10-22 asks that nothing land on it while the cross-model check runs. The series is therefore built and verified
in a local checkout of the trunk and kept here, where it survives the container.

## Contents
| Patch | Effect on the trunk |
|---|---|
| `0001-Test-register-…patch` | `docs/testing/build_register.py` gains a static source parser and `--check-complete`; new `docs/testing/unit_rules.yaml`; regenerated `test_register.yaml` and `coverage_matrix.md` |
| `0002-Test-family-charters-…patch` | `docs/testing/charters/` (index + nine charters); `docs/testing/check_charters.py` with `--probe` |

No test, contract, result of record or register row is changed by either patch.

## Gates (run on a fresh checkout of `87334d6` with the series applied, 2026-10-22)
| Gate | Result |
|---|---|
| Existing 305 register entries | carried byte-identical |
| New entries | 675; the four main bodies hold 639 tests; Python test functions 333 = pytest's 333 distinct collected functions (476 items with parameters) |
| Unmapped tests / duplicate identifiers | 0 / 0 |
| `build_register.py --check` | current |
| `build_register.py --check-complete` | pass; probes: an unregistered test file and an unparseable `it(` both fail it (`gate_probe_check_complete.txt`) |
| `check_charters.py` and `--probe` | pass; probe fires on a non-existent row |
| `tools/prepush_check.sh` (all CI document guards, incl. the stale-number scan over the charters) | PREPUSH OK (`gate_prepush.txt`) |
| `git am` onto `87334d6` | applies cleanly |
| Mapping accuracy | hand-graded random sample of 50: 43 right on function, 41 on function and class, before three substring fixes ("representation", "timestamp", "remove a claim"); the rules file is the author's review point |

Not run: the Hardhat suite and the Python suites themselves (no test changed), and CI (nothing pushed to the trunk).

## To apply (the author's call; replan §7)
```bash
git checkout claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy   # after the check pass has reported
git am docs/planning/testing_suite/staged/*.patch                # from a checkout of this branch's files
python3 docs/testing/build_register.py --check && python3 docs/testing/build_register.py --check-complete
python3 docs/testing/check_charters.py && bash tools/prepush_check.sh
```
If the trunk has moved, the register file conflicts by design: drop the generated `test_register.yaml` and
`coverage_matrix.md` hunks and regenerate with `build_register.py`.
