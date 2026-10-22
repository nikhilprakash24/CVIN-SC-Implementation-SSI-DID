"""The attack simulator's mechanics (the verdicts themselves are computed by attacks/run_attacks.py)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "attacks"))
from simulate import run_episode  # noqa: E402


def test_undefended_bisection_recovers_the_value():
    for s in (1, 2, 3):
        e = run_episode(s, "single", "none")
        assert e.adversary_exact and e.adversary_queries_to_exact <= 5


def test_static_cap_stops_one_identity_but_not_a_sybil_set():
    e1, e2 = run_episode(4, "single", "static_cap"), run_episode(4, "sybil", "static_cap")
    assert e1.adversary_bits <= 2.0 and not e1.adversary_exact
    assert e2.adversary_exact


def test_budget_bounds_leakage_for_every_variant_including_an_accredited_insider():
    for v in ("single", "sybil", "insider"):
        for s in (5, 6):
            assert run_episode(s, v, "steward").adversary_bits <= 3.0 + 1e-9


def test_a_learner_without_the_kernel_budget_is_broken_by_an_insider():
    assert run_episode(7, "insider", "steward_no_budget").adversary_exact


def test_episodes_are_deterministic():
    a, b = run_episode(9, "sybil", "steward"), run_episode(9, "sybil", "steward")
    assert (a.adversary_bits, a.honest_served) == (b.adversary_bits, b.honest_served)
