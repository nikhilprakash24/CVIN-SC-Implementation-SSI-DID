#!/usr/bin/env python3
"""
Same-host freshness-k comparison, full vs probe refresh (after-action report 06,
stream H-K; register #40).

Reads the per-replicate result files written by experiment_freshness_k.py into
one directory (default results/freshness_k_samehost/), each named
r<i>_<mode>.json, plus the sidecar r<i>_<mode>.load.json written by the run
driver (/proc/loadavg at the start and end of the replicate and sampled while it
ran). It does not re-measure anything.

Per replicate and per mode (pooled over replicates) it reports
  t_local  = median verify at k = inf,
  t_chain  = median verify at k = 1 - t_local          (definitions as #32/#37),
  P*(0.5)  = floor(50 ms / mean) per k,
  the knee = k with P*(0.5) = 100 on the curve t_local + t_chain / k, i.e.
             t_chain / (0.5 - t_local); "not reached" when t_local >= 0.5 ms
             (then the ceiling P*(0.5) at k = inf is quoted),
  the smallest tested k whose measured P*(0.5) >= 100 (or none),
  the staleness bound check (max accepted after revocation / max new-key
  messages rejected after rotation <= k - 1, and = the phase prediction).

Pooled figures concatenate the measured samples of all replicates of a mode
(each replicate holds n per k), so pooled medians/means weigh replicates equally.

Outputs <out>.{json,csv,md} and <out>.png (if matplotlib is available).

Usage
  python3 scripts/summarize_freshness_k_samehost.py \
      [--runs-dir results/freshness_k_samehost] [--out results/freshness_k_samehost]
"""

import argparse
import csv
import glob
import json
import math
import os
import re
from typing import Any, Dict, List, Optional

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BUDGET_MS = 100.0
F = 0.5
PER_MSG_MS = F * BUDGET_MS / 100      # 0.5 ms: P*(0.5) = 100
KS = ['1', '5', '25', 'inf']
LOAD_LIMIT = 1.5
RUN_RE = re.compile(r'^r(\d+)_(full|probe)\.json$')

# Earlier runs of record, quoted for comparison (read if present; never written).
REFERENCE_FILES = [
    ('#32', 'full', '2.10 GHz', 'freshness_k.json'),
    ('#37 r1', 'full', '2.80 GHz shared', 'freshness_k_probe_fullref.json'),
    ('#37 r1', 'probe', '2.80 GHz shared', 'freshness_k_probe.json'),
    ('#37 r2', 'probe', '2.80 GHz shared', 'freshness_k_probe_r2.json'),
    ('#37 r2', 'full', '2.80 GHz shared', 'freshness_k_probe_fullref_r2.json'),
]


def p_star(t_ms: Optional[float], f: float = F) -> Optional[int]:
    if t_ms is None or t_ms <= 0:
        return None
    return int(math.floor(f * BUDGET_MS / t_ms + 1e-9))


def knee(t_local: float, t_chain: float) -> Optional[float]:
    """k at which t_local + t_chain / k = 0.5 ms; None when t_local >= 0.5 ms (never reached)."""
    if t_local >= PER_MSG_MS:
        return None
    return t_chain / (PER_MSG_MS - t_local)


def measured_knee(pstar_by_k: Dict[str, Optional[int]]) -> Optional[str]:
    """Smallest tested k (in KS order, inf last) whose measured P*(0.5) >= 100."""
    for k in KS:
        v = pstar_by_k.get(k)
        if v is not None and v >= 100:
            return k
    return None


def _latency_by_k(run: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {r['k']: r for r in run['latency']}


def constants_from_samples(by_k_samples: Dict[str, List[float]]) -> Dict[str, Any]:
    t_local = float(np.median(by_k_samples['inf']))
    t_chain = float(np.median(by_k_samples['1'])) - t_local
    per_k = {}
    for k in KS:
        s = by_k_samples.get(k)
        if not s:
            continue
        mean = float(np.mean(s))
        per_k[k] = {'n': len(s), 'mean_ms': mean, 'median_ms': float(np.median(s)),
                    'p95_ms': float(np.percentile(s, 95)), 'P*(0.5)': p_star(mean)}
    kn = knee(t_local, t_chain)
    pst = {k: v['P*(0.5)'] for k, v in per_k.items()}
    return {'t_local_ms': t_local, 't_chain_ms': t_chain, 'knee_k_analytic': kn,
            'knee_reached': kn is not None,
            'knee_text': (f"k ≈ {kn:.0f}" if kn is not None
                          else f"not reached (t_local {t_local:.3f} ≥ 0.5 ms; k=∞ P*(0.5) = {pst.get('inf')})"),
            'Pstar_inf': pst.get('inf'), 'measured_knee_tested_k': measured_knee(pst), 'per_k': per_k}


def staleness_check(run: Dict[str, Any]) -> Dict[str, Any]:
    out = {'revocation': {}, 'rotation': {}, 'all_within_bound': True, 'all_match_prediction': True,
           'finite_trials': 0}
    for part, key, max_field in (('revocation', 'staleness', 'max_accepted_after_revocation'),
                                 ('rotation', 'rotation', 'max_stale_messages')):
        for s in run.get(key) or []:
            bound = s.get('bound_k_minus_1')
            out[part][s['k']] = {'max': s.get(max_field), 'bound': bound,
                                 'within_bound': s.get('within_bound') if bound is not None else None,
                                 'matches_prediction': s.get('matches_prediction') if bound is not None else None,
                                 'trials': len(s.get('trials') or [])}
            if bound is not None:
                out['finite_trials'] += len(s.get('trials') or [])
                if not s.get('within_bound'):
                    out['all_within_bound'] = False
                if not s.get('matches_prediction'):
                    out['all_match_prediction'] = False
    return out


def summarize_run(run: Dict[str, Any], load: Optional[Dict[str, Any]], rep: int, mode: str) -> Dict[str, Any]:
    by_k = _latency_by_k(run)
    c = constants_from_samples({k: by_k[k]['samples_ms'] for k in KS if k in by_k})
    env = run['environment']
    lmax = None
    if load:
        vals = [load.get('load1_start'), load.get('load1_end'), load.get('load1_max_sampled')]
        vals = [v for v in vals if v is not None]
        lmax = max(vals) if vals else None
    d = run.get('derived', {})
    return {
        'replicate': rep, 'mode': mode, 'order_index': (load or {}).get('order_index'),
        'run_tag': run['config'].get('run_tag'), 'date_utc': env.get('date_utc'),
        'git_commit': env.get('git_commit'), 'git_dirty': env.get('git_dirty'),
        'registry_bytecode_sha256': env.get('registry_bytecode_sha256'),
        'contract_deploy_gas': env.get('contract_deploy_gas'),
        'refreshes_in_window': {k: by_k[k].get('refreshes_in_window') for k in KS if k in by_k},
        'full_resolutions_in_window': {k: by_k[k].get('full_resolutions_in_window') for k in KS if k in by_k},
        'refresh_rpc_median': {k: by_k[k].get('refresh_rpc_median') for k in KS if k in by_k},
        't_chain_probe_direct_ms': d.get('t_chain_probe_direct_ms'),
        't_chain_one_call_ms': d.get('t_chain_one_call_ms'),
        'load': ({k: v for k, v in load.items() if k != 'samples'} if load else None), 'load1_max': lmax,
        'foreign_cpu_mean': (load or {}).get('foreign_cpu_mean'),
        'foreign_cpu_max': (load or {}).get('foreign_cpu_max'),
        'load_exceeded': (lmax is not None and lmax > LOAD_LIMIT),
        'staleness': staleness_check(run),
        **c,
    }


def pool(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    samples = {k: [] for k in KS}
    for r in runs:
        for k, row in _latency_by_k(r).items():
            samples[k].extend(row['samples_ms'])
    return constants_from_samples(samples)


def load_runs(runs_dir: str):
    out = []
    for path in sorted(glob.glob(os.path.join(runs_dir, 'r*_*.json'))):
        m = RUN_RE.match(os.path.basename(path))
        if not m:
            continue
        rep, mode = int(m.group(1)), m.group(2)
        with open(path) as f:
            run = json.load(f)
        if run['config'].get('refresh_mode') != mode:
            raise RuntimeError(f"{path}: file says mode {run['config'].get('refresh_mode')}, name says {mode}")
        lp = path[:-5] + '.load.json'
        load = json.load(open(lp)) if os.path.exists(lp) else None
        out.append((rep, mode, run, load))
    out.sort(key=lambda t: t[0])
    return out


def references(results_dir: str) -> List[Dict[str, Any]]:
    refs = []
    for row, mode, host, name in REFERENCE_FILES:
        p = os.path.join(results_dir, name)
        if not os.path.exists(p):
            continue
        run = json.load(open(p))
        by_k = _latency_by_k(run)
        c = constants_from_samples({k: by_k[k]['samples_ms'] for k in KS if k in by_k})
        refs.append({'row': row, 'mode': mode, 'host': host, 'file': f'results/{name}', **c})
    return refs


def build(runs_dir: str, results_dir: str) -> Dict[str, Any]:
    loaded = load_runs(runs_dir)
    if not loaded:
        raise RuntimeError(f"no r<i>_<mode>.json in {runs_dir}")
    reps = [summarize_run(run, load, rep, mode) for rep, mode, run, load in loaded]
    modes = {}
    for mode in ('full', 'probe'):
        rs = [run for rep, m, run, load in loaded if m == mode]
        if rs:
            mr = [r for r in reps if r['mode'] == mode]
            modes[mode] = {
                'replicates': [r['replicate'] for r in mr],
                'pooled': pool(rs),
                't_local_range_ms': [min(r['t_local_ms'] for r in mr), max(r['t_local_ms'] for r in mr)],
                't_chain_range_ms': [min(r['t_chain_ms'] for r in mr), max(r['t_chain_ms'] for r in mr)],
                'Pstar_range': {k: [min(r['per_k'][k]['P*(0.5)'] for r in mr),
                                    max(r['per_k'][k]['P*(0.5)'] for r in mr)] for k in KS},
                'staleness_all_within_bound': all(r['staleness']['all_within_bound'] for r in mr),
                'staleness_all_match_prediction': all(r['staleness']['all_match_prediction'] for r in mr),
                'staleness_finite_trials': sum(r['staleness']['finite_trials'] for r in mr),
            }
    if 'full' in modes and 'probe' in modes:
        pf, pp = modes['full']['pooled'], modes['probe']['pooled']
        ratio = {'t_chain_full_over_probe': pf['t_chain_ms'] / pp['t_chain_ms'] if pp['t_chain_ms'] else None,
                 't_local_probe_minus_full_ms': pp['t_local_ms'] - pf['t_local_ms'],
                 'Pstar_probe_over_full': {k: (pp['per_k'][k]['P*(0.5)'] / pf['per_k'][k]['P*(0.5)']
                                               if pf['per_k'][k]['P*(0.5)'] else None) for k in KS}}
    else:
        ratio = None
    shas = sorted({r['registry_bytecode_sha256'] for r in reps})
    return {
        'definitions': {
            't_local': 'median verify_message at k=inf', 't_chain': 'median verify at k=1 minus t_local',
            'P*(0.5)': 'floor(50 ms / mean verify) per k',
            'knee': 't_chain / (0.5 ms - t_local): k at which the curve t_local + t_chain/k gives P*(0.5)=100; '
                    'not reached when t_local >= 0.5 ms',
            'measured_knee_tested_k': 'smallest tested k whose measured P*(0.5) >= 100',
            'pooled': 'samples of all replicates of a mode concatenated per k',
            'load_limit': LOAD_LIMIT},
        'order': [f"r{r['replicate']}:{r['mode']}" for r in reps],
        'registry_bytecode_sha256': shas,
        'all_git_clean': all(r['git_dirty'] is False for r in reps),
        'replicates': reps, 'modes': modes, 'comparison': ratio,
        'references': references(results_dir),
    }


def f3(x, d=3):
    return '–' if x is None else (f"{x:.{d}f}" if isinstance(x, float) else str(x))


CSV_COLUMNS = ['scope', 'replicate', 'mode', 'k', 'n', 'mean_ms', 'median_ms', 'p95_ms', 'P*(0.5)',
               't_local_ms', 't_chain_ms', 'knee', 'load1_max', 'staleness_max_revocation',
               'staleness_max_rotation', 'bound_k_minus_1']


def write_csv(path: str, s: Dict[str, Any]):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        w.writeheader()
        for r in s['replicates']:
            for k in KS:
                pk = r['per_k'][k]
                rv, ro = r['staleness']['revocation'].get(k, {}), r['staleness']['rotation'].get(k, {})
                w.writerow({'scope': 'replicate', 'replicate': r['replicate'], 'mode': r['mode'], 'k': k,
                            'n': pk['n'], 'mean_ms': f"{pk['mean_ms']:.4f}", 'median_ms': f"{pk['median_ms']:.4f}",
                            'p95_ms': f"{pk['p95_ms']:.4f}", 'P*(0.5)': pk['P*(0.5)'],
                            't_local_ms': f"{r['t_local_ms']:.4f}", 't_chain_ms': f"{r['t_chain_ms']:.4f}",
                            'knee': f"{r['knee_k_analytic']:.1f}" if r['knee_reached'] else 'not reached',
                            'load1_max': r['load1_max'], 'staleness_max_revocation': rv.get('max'),
                            'staleness_max_rotation': ro.get('max'), 'bound_k_minus_1': rv.get('bound')})
        for mode, m in s['modes'].items():
            p = m['pooled']
            for k in KS:
                pk = p['per_k'][k]
                w.writerow({'scope': 'pooled', 'replicate': '+'.join(map(str, m['replicates'])), 'mode': mode,
                            'k': k, 'n': pk['n'], 'mean_ms': f"{pk['mean_ms']:.4f}",
                            'median_ms': f"{pk['median_ms']:.4f}", 'p95_ms': f"{pk['p95_ms']:.4f}",
                            'P*(0.5)': pk['P*(0.5)'], 't_local_ms': f"{p['t_local_ms']:.4f}",
                            't_chain_ms': f"{p['t_chain_ms']:.4f}",
                            'knee': f"{p['knee_k_analytic']:.1f}" if p['knee_reached'] else 'not reached'})


def write_md(path: str, s: Dict[str, Any]):
    L = []
    a = L.append
    a('# Freshness-k, full vs probe refresh, same host back to back (stream H-K, register #40)\n')
    a('Generated by `scripts/summarize_freshness_k_samehost.py` from `results/freshness_k_samehost/r*_*.json` '
      '(each written by `scripts/experiment_freshness_k.py --deploy --rotation --refresh-mode <mode>`, one fresh '
      'Hardhat node per replicate). Nothing is re-measured here.\n')
    a(f"- Order (interleaved): {', '.join(s['order'])}")
    a(f"- Registry bytecode sha256: {', '.join(s['registry_bytecode_sha256'])}")
    a(f"- All result files from a clean tree (git_dirty false): {s['all_git_clean']}\n")
    a('## Per replicate\n')
    a("load1 = /proc/loadavg 1-min value; it includes this replicate's own node + Python (≈1 CPU). Foreign CPU = "
      'CPUs busy outside this replicate (all busy jiffies minus the :8562 node and the experiment), mean / max of '
      f'2 s samples; r1 predates that sampler. **>{LOAD_LIMIT}** marks load1 above {LOAD_LIMIT}.\n')
    a('| rep | mode | commit | load1 start / end / max sampled | foreign CPU mean / max | t_local | t_chain '
      '| P*(0.5) k=1 / 5 / 25 / ∞ | knee (P*(0.5)=100) | refresh RPCs | staleness ≤ k−1 (= prediction) |')
    a('|---:|---|---|---|---|---:|---:|---|---|---:|---|')
    for r in s['replicates']:
        ld = r['load'] or {}
        flag = ' **>1.5**' if r['load_exceeded'] else ''
        ps = ' / '.join(str(r['per_k'][k]['P*(0.5)']) for k in KS)
        st = r['staleness']
        a(f"| {r['replicate']} | {r['mode']} | `{r['git_commit']}` | {f3(ld.get('load1_start'), 2)} / "
          f"{f3(ld.get('load1_end'), 2)} / {f3(ld.get('load1_max_sampled'), 2)}{flag} | "
          f"{f3(r['foreign_cpu_mean'], 2)} / {f3(r['foreign_cpu_max'], 2)} | {r['t_local_ms']:.3f} | "
          f"{r['t_chain_ms']:.3f} | {ps} | {r['knee_text']} | {r['refresh_rpc_median'].get('1')} | "
          f"{'yes' if st['all_within_bound'] else 'NO'} ({'yes' if st['all_match_prediction'] else 'NO'}), "
          f"{st['finite_trials']} trials |")
    a('\n## Pooled per mode\n')
    a('| mode | reps | t_local | t_chain | k | mean | median | p95 | P*(0.5) |')
    a('|---|---|---:|---:|---|---:|---:|---:|---:|')
    for mode, m in s['modes'].items():
        p = m['pooled']
        for k in KS:
            pk = p['per_k'][k]
            a(f"| {mode} | {'+'.join(map(str, m['replicates']))} | {p['t_local_ms']:.3f} | {p['t_chain_ms']:.3f} | "
              f"{k} | {pk['mean_ms']:.3f} | {pk['median_ms']:.3f} | {pk['p95_ms']:.3f} | {pk['P*(0.5)']} |")
    a('\n## Knee per mode\n')
    a('| mode | pooled t_local | pooled t_chain | knee (pooled) | per-replicate knees | smallest tested k with '
      'measured P*(0.5) ≥ 100 | P*(0.5) range k=1 / 5 / 25 / ∞ |')
    a('|---|---:|---:|---|---|---|---|')
    for mode, m in s['modes'].items():
        p = m['pooled']
        reps = [r for r in s['replicates'] if r['mode'] == mode]
        kn = '; '.join(f"r{r['replicate']}: " + (f"{r['knee_k_analytic']:.0f} (t_local {r['t_local_ms']:.3f})"
                                                if r['knee_reached'] else f"not reached (t_local {r['t_local_ms']:.3f})")
                       for r in reps)
        rng = ' / '.join(f"{m['Pstar_range'][k][0]}–{m['Pstar_range'][k][1]}" for k in KS)
        a(f"| {mode} | {p['t_local_ms']:.3f} | {p['t_chain_ms']:.3f} | {p['knee_text']} | {kn} | "
          f"{p['measured_knee_tested_k'] or 'none'} | {rng} |")
    if s['comparison']:
        c = s['comparison']
        a(f"\nPooled t_chain full / probe = {c['t_chain_full_over_probe']:.2f}×; t_local probe − full = "
          f"{c['t_local_probe_minus_full_ms']:+.3f} ms; P*(0.5) probe / full by k: "
          + ', '.join(f"k={k} {v:.2f}×" for k, v in c['Pstar_probe_over_full'].items() if v) + '.')
    a('\n## Staleness bound (max accepted after revocation | max new-key rejected after rotation)\n')
    a('| rep | mode | k=1 | k=5 | k=25 | k=∞ (cap) |')
    a('|---:|---|---|---|---|---|')
    for r in s['replicates']:
        st = r['staleness']
        cells = []
        for k in KS:
            rv, ro = st['revocation'].get(k, {}), st['rotation'].get(k, {})
            cells.append(f"{rv.get('max')} \\| {ro.get('max')}")
        a(f"| {r['replicate']} | {r['mode']} | " + ' | '.join(cells) + ' |')
    if s['references']:
        a('\n## Earlier runs, same definitions recomputed from their files (different hosts / sessions)\n')
        a('| row | mode | host | t_local | t_chain | P*(0.5) k=1 / 5 / 25 / ∞ | knee |')
        a('|---|---|---|---:|---:|---|---|')
        for r in s['references']:
            ps = ' / '.join(str(r['per_k'][k]['P*(0.5)']) for k in KS)
            a(f"| {r['row']} | {r['mode']} | {r['host']} | {r['t_local_ms']:.3f} | {r['t_chain_ms']:.3f} | {ps} | "
              f"{r['knee_text']} |")
    with open(path, 'w') as f:
        f.write('\n'.join(L) + '\n')


def write_png(path: str, s: Dict[str, Any]) -> Optional[str]:
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except Exception as exc:          # pragma: no cover
        return f'matplotlib unavailable: {exc}'
    fig, ax = plt.subplots(figsize=(7, 4.2))
    xs = list(range(len(KS)))
    colors = {'full': '#1f5fa8', 'probe': '#c2571a'}
    for r in s['replicates']:
        ax.plot(xs, [r['per_k'][k]['P*(0.5)'] for k in KS], color=colors[r['mode']], alpha=0.35, lw=1,
                marker='.', label=None)
    for mode, m in s['modes'].items():
        ax.plot(xs, [m['pooled']['per_k'][k]['P*(0.5)'] for k in KS], color=colors[mode], lw=2.2, marker='o',
                label=f"{mode} refresh (pooled; t_local {m['pooled']['t_local_ms']:.3f} ms)")
    ax.axhline(100, color='#555', ls='--', lw=1)
    ax.text(0.02, 101.5, 'P*(0.5) = 100', color='#555', fontsize=8)
    ax.set_xticks(xs)
    ax.set_xticklabels(['1', '5', '25', '∞'])
    ax.set_xlabel('refresh every k messages')
    ax.set_ylabel('P*(0.5) from mean verify')
    ax.set_title('Freshness-k, same host back to back (thin: replicates)', fontsize=10)
    ax.legend(fontsize=8, loc='upper left')
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--runs-dir', default=os.path.join(ROOT, 'results', 'freshness_k_samehost'))
    ap.add_argument('--results-dir', default=os.path.join(ROOT, 'results'),
                    help='where the #32/#37 reference files are read from')
    ap.add_argument('--out', default=os.path.join(ROOT, 'results', 'freshness_k_samehost'))
    args = ap.parse_args()
    s = build(args.runs_dir, args.results_dir)
    with open(args.out + '.json', 'w') as f:
        json.dump(s, f, indent=2, default=str)
    write_csv(args.out + '.csv', s)
    write_md(args.out + '.md', s)
    err = write_png(args.out + '.png', s)
    print(f"Wrote {args.out}.{{json,csv,md}}" + (f" ({err})" if err else " and .png"))
    for mode, m in s['modes'].items():
        p = m['pooled']
        print(f"  {mode}: t_local {p['t_local_ms']:.3f} t_chain {p['t_chain_ms']:.3f} "
              f"P* {[p['per_k'][k]['P*(0.5)'] for k in KS]} knee {p['knee_text']}")


if __name__ == '__main__':
    main()
