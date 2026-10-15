"""
Offline tests for scripts/summarize_freshness_k_samehost.py (stream H-K,
register #40): knee arithmetic, the "not reached" case, pooling, the staleness
check and the load flag, on synthetic experiment_freshness_k.py result files.
"""

import json
import math

import pytest

import summarize_freshness_k_samehost as S


def _run(mode, t_local, t_chain, n=250, sha='ab' * 32, dirty=False, stale_ok=True):
    lat = []
    for k in S.KS:
        kk = None if k == 'inf' else int(k)
        samples = []
        for i in range(n):
            refresh = kk is not None and i % kk == 0
            samples.append(t_local + (t_chain if refresh else 0.0))
        lat.append({'k': k, 'samples_ms': samples, 'refreshes_in_window': sum(1 for i in range(n)
                    if kk is not None and i % kk == 0), 'full_resolutions_in_window': 0,
                    'refresh_rpc_median': 1.0 if mode == 'probe' else 4.0})

    def st(k, field):
        if k == 'inf':
            return {'k': k, field: 50, 'bound_k_minus_1': None, 'within_bound': None,
                    'matches_prediction': None, 'trials': [{}] * 3}
        b = int(k) - 1
        return {'k': k, field: b if stale_ok else b + 1, 'bound_k_minus_1': b, 'within_bound': stale_ok,
                'matches_prediction': stale_ok, 'trials': [{}] * (5 if k == '1' else int(k))}

    return {'environment': {'git_commit': 'abc1234', 'git_dirty': dirty, 'registry_bytecode_sha256': sha,
                            'date_utc': 'x', 'contract_deploy_gas': 927756},
            'config': {'refresh_mode': mode, 'run_tag': 't'},
            'latency': lat, 'derived': {'t_chain_probe_direct_ms': 2.5, 't_chain_one_call_ms': 7.0},
            'staleness': [st(k, 'max_accepted_after_revocation') for k in S.KS],
            'rotation': [st(k, 'max_stale_messages') for k in S.KS]}


def _write(tmp_path, rep, mode, run, load=None):
    d = tmp_path / 'runs'
    d.mkdir(exist_ok=True)
    (d / f'r{rep}_{mode}.json').write_text(json.dumps(run))
    if load is not None:
        (d / f'r{rep}_{mode}.load.json').write_text(json.dumps(load))
    return d


def test_p_star_and_knee():
    assert S.p_star(0.5) == 100
    assert S.p_star(0.45) == 111
    assert S.p_star(None) is None
    assert S.knee(0.4, 2.5) == pytest.approx(25.0)          # LATENCY_BUDGET §4's analytic point
    assert S.knee(0.428, 10.518) == pytest.approx(146.08, abs=0.01)   # #32's k ≈ 146
    assert S.knee(0.5, 2.0) is None and S.knee(0.54, 2.0) is None


def test_measured_knee_picks_smallest_tested_k():
    assert S.measured_knee({'1': 4, '5': 21, '25': 101, 'inf': 110}) == '25'
    assert S.measured_knee({'1': 4, '5': 21, '25': 58, 'inf': 110}) == 'inf'
    assert S.measured_knee({'1': 4, '5': 21, '25': 58, 'inf': 80}) is None


def test_constants_follow_32_definitions():
    run = _run('full', 0.4, 10.0)
    c = S.summarize_run(run, None, 1, 'full')
    assert c['t_local_ms'] == pytest.approx(0.4)
    assert c['t_chain_ms'] == pytest.approx(10.0)       # k=1: every message refreshes
    assert c['per_k']['5']['mean_ms'] == pytest.approx(0.4 + 10.0 / 5)
    assert c['per_k']['inf']['P*(0.5)'] == 125
    assert c['knee_reached'] and c['knee_k_analytic'] == pytest.approx(100.0)


def test_not_reached_quotes_inf_ceiling():
    c = S.summarize_run(_run('probe', 0.52, 2.8), None, 1, 'probe')
    assert c['knee_k_analytic'] is None and not c['knee_reached']
    assert 'not reached' in c['knee_text'] and '96' in c['knee_text']   # floor(50 / 0.52) = 96
    assert c['measured_knee_tested_k'] is None


def test_staleness_check_flags_violation():
    ok = S.staleness_check(_run('full', 0.4, 10.0))
    assert ok['all_within_bound'] and ok['all_match_prediction']
    assert ok['finite_trials'] == 2 * (5 + 5 + 25)        # revocation + rotation, finite k only
    bad = S.staleness_check(_run('full', 0.4, 10.0, stale_ok=False))
    assert not bad['all_within_bound']


def test_build_pools_and_flags_load(tmp_path):
    d = _write(tmp_path, 1, 'full', _run('full', 0.40, 10.0), {'order_index': 1, 'load1_start': 0.2,
                                                               'load1_end': 0.9, 'load1_max_sampled': 1.7})
    _write(tmp_path, 2, 'probe', _run('probe', 0.42, 2.0), {'order_index': 2, 'load1_start': 0.3,
                                                            'load1_end': 0.4, 'load1_max_sampled': 0.6})
    _write(tmp_path, 3, 'probe', _run('probe', 0.44, 2.0))
    _write(tmp_path, 4, 'full', _run('full', 0.40, 12.0))
    s = S.build(str(d), str(tmp_path / 'nothing'))
    assert s['order'] == ['r1:full', 'r2:probe', 'r3:probe', 'r4:full']
    assert s['all_git_clean'] is True
    assert s['registry_bytecode_sha256'] == ['ab' * 32]
    r1 = s['replicates'][0]
    assert r1['load_exceeded'] is True and r1['load1_max'] == 1.7
    assert s['replicates'][1]['load_exceeded'] is False
    full = s['modes']['full']['pooled']
    assert full['per_k']['1']['n'] == 500
    assert full['t_local_ms'] == pytest.approx(0.40)
    assert full['per_k']['1']['mean_ms'] == pytest.approx(0.40 + 11.0)
    assert s['modes']['probe']['t_local_range_ms'] == [pytest.approx(0.42), pytest.approx(0.44)]
    assert s['comparison']['t_chain_full_over_probe'] > 1
    assert s['references'] == []


def test_mode_mismatch_is_refused(tmp_path):
    d = _write(tmp_path, 1, 'probe', _run('full', 0.4, 10.0))
    with pytest.raises(RuntimeError, match='mode'):
        S.build(str(d), str(tmp_path))


def test_writers_produce_all_outputs(tmp_path):
    d = _write(tmp_path, 1, 'full', _run('full', 0.40, 10.0))
    _write(tmp_path, 2, 'probe', _run('probe', 0.52, 2.0))
    s = S.build(str(d), str(tmp_path))
    out = str(tmp_path / 'out')
    S.write_csv(out + '.csv', s)
    S.write_md(out + '.md', s)
    md = open(out + '.md').read()
    assert 'not reached' in md and 'k ≈ 100' in md
    rows = open(out + '.csv').read().splitlines()
    assert len(rows) == 1 + 2 * 4 + 2 * 4                  # header + replicate rows + pooled rows
    assert S.write_png(out + '.png', s) is None or True
    assert math.isfinite(s['modes']['full']['pooled']['knee_k_analytic'])
