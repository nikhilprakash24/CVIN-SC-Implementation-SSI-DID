"""L4 — the twelve lifecycle use cases as tests (plan S6, second part).

cv2x-testbed/scripts/test_use_cases.py runs twelve MOBI VID lifecycle scenarios against
the in-memory centralized registry and the W3C VC layer, in-process, no chain. Its
pass criterion per use case is "the function returns without raising": verification
failures and registry inconsistencies raise RuntimeError/ValueError inside the use
case. We parametrise over the script's own USE_CASES table, so these tests and the
CLI runner (which still prints 12/12) always execute the same functions.
"""
import pytest
import test_use_cases as uc  # sys.path set in conftest.py

# Collection-time guard: a shrunken table must fail loudly, not pass with fewer tests.
assert [n for n, _, _ in uc.USE_CASES] == [str(i) for i in range(1, 13)], \
    f"runner table is not use cases 1..12: {[n for n, _, _ in uc.USE_CASES]}"


@pytest.mark.parametrize("num,name,func", uc.USE_CASES,
                         ids=[f"uc{n}-{f.__name__}" for n, _, f in uc.USE_CASES])
def test_lifecycle_use_case_passes(num, name, func):
    # Each use case builds its own fresh CentralizedVehicleRegistry, issuer and
    # wallet, so order and isolation do not matter. Success == returns normally.
    func()
