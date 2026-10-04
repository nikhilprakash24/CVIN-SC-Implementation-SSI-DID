#!/usr/bin/env python3
"""
Freshness-k sweep for the ERC-1056 verifier (review §5.1, LATENCY_BUDGET.md §4,
after-action report 04 stream F-D).

A sibling of experiment_pki_vs_erc1056.py: it imports that script's harness
(measure / summarize / RPCCounter / environment / registry deploy / T-9
freshness configuration / BSM payload) and leaves the #21 run of record and its
results files untouched.

What is varied
  ERC1056Provider(refresh_every=k): the verifier re-reads the sender's key and
  revocation state from the registry every k messages PER SENDER (k = 1 is the
  uncached #21 behaviour; k = inf resolves once). The T-9 freshness / replay
  policy (BENCHMARK_FRESHNESS) is installed identically for every k and runs
  before the cache.

Part 1, latency: for each k, a fresh verifier verifies n consecutive genuine
  messages from one registered sender (after `warmup` discarded ones). Median,
  p95 and the MEAN (the amortised per-message cost, which is what
  t_eff = t_local + t_chain / k models) are reported, with the number of chain
  refreshes and RPC calls in the measured window. n defaults to 250 so that
  every k in {1, 5, 25} divides it: the window then holds exactly n/k refreshes
  whatever the warm-up phase.

  Constants recomputed from this run:
    t_local = median verify on the cached path (all samples of k = inf),
    t_chain = median verify at k = 1 minus t_local (the added cost of one
              refresh, freshness check and ECDSA verify being common to both).
  The analytic curve t_eff(k) = t_local + t_chain / k is compared with the
  measured mean per k, alongside LATENCY_BUDGET.md §4's 0.4 + 2.5 / k ms.
  P*(f) = floor(f * 100 ms / t) (LATENCY_BUDGET.md §2).

Part 2, staleness bound: for each k, fresh senders are registered, a verifier
  with refresh k accepts m_pre messages from the sender, the sender's identity
  is revoked on chain (receipt awaited), and fresh messages are then verified
  until the first rejection (cap: k + 5, or `--inf-cap` for k = inf). The count
  of messages accepted AFTER the revocation was mined is recorded per trial and
  compared with the prediction k - 1 - ((m_pre - 1) mod k), whose maximum over
  the phases is k - 1 (0 for k = 1). Two further messages after the first
  rejection must also be rejected.

Outputs (cv2x-testbed/results/)
  freshness_k.json  environment, config, raw samples, staleness trials
  freshness_k.csv   one row per k
  freshness_k.md    tables + caveats
  freshness_k.png   P*(0.5) and t vs k, measured and analytic (if matplotlib)

Usage
  python3 scripts/experiment_freshness_k.py --rpc-url http://127.0.0.1:8554 --deploy
"""

import argparse
import csv
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import experiment_pki_vs_erc1056 as H  # noqa: E402  (the #21 harness, imported read-only)
from identity.erc1056_provider import ERC1056Provider  # noqa: E402

BUDGET_MS = 100.0                     # SAE J2945/1 10 Hz BSM interval
FRACTIONS = (0.25, 0.5, 1.0)
LB_T_LOCAL_MS = 0.4                   # LATENCY_BUDGET.md §4 constants
LB_T_CHAIN_MS = 2.5
DEFAULT_KS = (1, 5, 25, None)         # None = infinity


def k_label(k: Optional[int]) -> str:
    return 'inf' if k is None else str(k)


def parse_ks(text: str) -> List[Optional[int]]:
    out: List[Optional[int]] = []
    for tok in text.split(','):
        tok = tok.strip().lower()
        out.append(None if tok in ('inf', 'infinity', '∞') else int(tok))
    return out


def p_star(t_ms: Optional[float], f: float) -> Optional[int]:
    if t_ms is None or t_ms <= 0:
        return None
    return int(math.floor(f * BUDGET_MS / t_ms))


def t_eff(t_local: float, t_chain: float, k: Optional[int]) -> float:
    return t_local if k is None else t_local + t_chain / k


def make_verifier(rpc_url: str, address: str, k: Optional[int]) -> ERC1056Provider:
    v = ERC1056Provider(rpc_url, contract_address=address, refresh_every=k)
    H.configure_freshness(v)          # identical T-9 policy for every k
    return v


# --------------------------------------------------------------------------
# Part 1: latency per k
# --------------------------------------------------------------------------
def run_latency(signer: ERC1056Provider, sender: str, rpc_url: str, address: str,
                k: Optional[int], n: int, warmup: int) -> Dict[str, Any]:
    verifier = make_verifier(rpc_url, address, k)
    backend = H.Backend(f'erc1056_k{k_label(k)}', verifier, True, H.RPCCounter(verifier.w3))
    counter = {'i': 0}

    def prepare(i):
        counter['i'] = i
        return (signer.sign_message(sender, H.make_bsm(5000 + i)), verifier.chain_refreshes)

    def run(ctx):
        return verifier.verify_message(ctx[0])

    def check(ctx, r):
        if r[0] is not True:
            H._fail(f"k={k_label(k)}: genuine message rejected")
        return {'refreshed': verifier.chain_refreshes > ctx[1],
                'resolution_ms': float(r[1].resolution_time_ms or 0.0)}

    samples = H.measure(backend, 'verify_message', n, warmup, prepare, run, check)
    s = H.summarize(samples)
    refreshed = [x for x in samples if x.extra.get('refreshed')]
    cached = [x for x in samples if not x.extra.get('refreshed')]
    s.update({
        'k': k_label(k),
        'refreshes_in_window': len(refreshed),
        'cached_in_window': len(cached),
        'refresh_median_ms': float(np.median([x.elapsed_ms for x in refreshed])) if refreshed else None,
        'cached_median_ms': float(np.median([x.elapsed_ms for x in cached])) if cached else None,
        'cached_p95_ms': float(np.percentile([x.elapsed_ms for x in cached], 95)) if cached else None,
        'refresh_rpc_median': float(np.median([x.rpc_calls for x in refreshed])) if refreshed else None,
        'cached_rpc_max': max((x.rpc_calls for x in cached), default=None),
        'rpc_calls_mean': float(np.mean([x.rpc_calls for x in samples])),
        'refresh_resolution_ms_median': (float(np.median([x.extra['resolution_ms'] for x in refreshed]))
                                         if refreshed else None),
        'samples_ms': [round(x.elapsed_ms, 4) for x in samples],
        'refreshed_flags': [bool(x.extra.get('refreshed')) for x in samples],
    })
    s.pop('gas_samples', None)
    print(f"  k={k_label(k):>4}: median={s['median_ms']:.3f} p95={s['p95_ms']:.3f} mean={s['mean_ms']:.3f} ms; "
          f"refreshes {len(refreshed)}/{len(samples)}; cached median={s['cached_median_ms']}")
    return s


# --------------------------------------------------------------------------
# Part 2: staleness bound (revocation mid-stream)
# --------------------------------------------------------------------------
def predicted_after(k: Optional[int], m_pre: int) -> Optional[int]:
    """Messages still accepted after a revocation that follows m_pre accepted ones."""
    if k is None:
        return None   # unbounded
    return k - 1 - ((m_pre - 1) % k)


def run_staleness(signer: ERC1056Provider, rpc_url: str, address: str, k: Optional[int],
                  run_tag: str, inf_cap: int, trials_min: int = 5) -> Dict[str, Any]:
    verifier = make_verifier(rpc_url, address, k)
    if k is None:
        phases = [1, 5, 25]
    else:
        phases = [r + 1 for r in range(max(k, trials_min))]
    cap = inf_cap if k is None else k + 5
    trials = []
    seq = 0
    for m_pre in phases:
        vid = f"FK_STALE_{run_tag}_k{k_label(k)}_m{m_pre}"
        signer.fund_vehicle_account(vid, H.FUND_WEI)
        signer.register_vehicle(vid, H.VEHICLE_METADATA)
        for _ in range(m_pre):
            seq += 1
            if verifier.verify_message(signer.sign_message(vid, H.make_bsm(seq)))[0] is not True:
                H._fail(f"k={k_label(k)}: pre-revocation message rejected")
        signer.revoke_credential(vid, 'staleness-test')        # mined (receipt awaited)
        revoke_block = int(signer.last_receipt.blockNumber)
        accepted_after = 0
        first_reject_at = None
        for j in range(cap):
            seq += 1
            ok = verifier.verify_message(signer.sign_message(vid, H.make_bsm(seq)))[0]
            if ok:
                accepted_after += 1
            else:
                first_reject_at = j + 1
                break
        stays_rejected = None
        if first_reject_at is not None:
            later = []
            for _ in range(2):
                seq += 1
                later.append(verifier.verify_message(signer.sign_message(vid, H.make_bsm(seq)))[0])
            stays_rejected = not any(later)
        pred = predicted_after(k, m_pre)
        trials.append({'m_pre': m_pre, 'revoke_block': revoke_block, 'accepted_after_revocation': accepted_after,
                       'predicted': pred, 'first_reject_at_message': first_reject_at,
                       'cap': cap, 'capped': first_reject_at is None,
                       'stays_rejected': stays_rejected})
    observed = [t['accepted_after_revocation'] for t in trials]
    bound = None if k is None else k - 1
    out = {
        'k': k_label(k),
        'trials': trials,
        'max_accepted_after_revocation': max(observed),
        'min_accepted_after_revocation': min(observed),
        'bound_k_minus_1': bound,
        'within_bound': (bound is not None and max(observed) <= bound),
        'matches_prediction': (k is not None and all(t['accepted_after_revocation'] == t['predicted']
                                                      for t in trials)),
        'all_stay_rejected': all(t['stays_rejected'] for t in trials if t['stays_rejected'] is not None),
    }
    print(f"  staleness k={k_label(k):>4}: accepted after revocation {observed} "
          f"(bound {bound if bound is not None else 'none'})")
    return out


# --------------------------------------------------------------------------
# Derived figures
# --------------------------------------------------------------------------
def derive(rows: List[Dict[str, Any]], one_call: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    by_k = {r['k']: r for r in rows}
    if 'inf' not in by_k or '1' not in by_k:
        raise RuntimeError("constants need both k=1 and k=inf")
    t_local = float(by_k['inf']['median_ms'])
    t_chain = float(by_k['1']['median_ms']) - t_local
    # alternative estimate of t_chain: median of the provider's internal resolution time at k=1
    t_chain_resolution = by_k['1'].get('refresh_resolution_ms_median')
    knee = None
    if t_local < 0.5 * BUDGET_MS / 100:
        knee = t_chain / (0.5 * BUDGET_MS / 100 - t_local)
    lb_knee = LB_T_CHAIN_MS / (0.5 * BUDGET_MS / 100 - LB_T_LOCAL_MS)
    table = []
    for r in rows:
        k = None if r['k'] == 'inf' else int(r['k'])
        a_run = t_eff(t_local, t_chain, k)
        a_lb = t_eff(LB_T_LOCAL_MS, LB_T_CHAIN_MS, k)
        a_one = t_eff(t_local, float(one_call['median_ms']), k) if one_call else None
        entry = {
            'k': r['k'],
            'measured_mean_ms': r['mean_ms'], 'measured_median_ms': r['median_ms'], 'measured_p95_ms': r['p95_ms'],
            'analytic_this_run_ms': a_run, 'analytic_latency_budget_ms': a_lb,
            'analytic_one_call_refresh_ms': a_one,
            'P*(0.5)_analytic_one_call_refresh': p_star(a_one, 0.5),
            'mean_minus_analytic_ms': r['mean_ms'] - a_run,
            'mean_over_analytic': r['mean_ms'] / a_run if a_run else None,
        }
        for f in FRACTIONS:
            tag = str(f)
            entry[f'P*({tag})_measured_mean'] = p_star(r['mean_ms'], f)
            entry[f'P*({tag})_measured_median'] = p_star(r['median_ms'], f)
            entry[f'P*({tag})_measured_p95'] = p_star(r['p95_ms'], f)
            entry[f'P*({tag})_analytic_this_run'] = p_star(a_run, f)
            entry[f'P*({tag})_analytic_latency_budget'] = p_star(a_lb, f)
        table.append(entry)
    return {
        't_local_ms': t_local, 't_chain_ms': t_chain,
        't_chain_from_resolution_ms': t_chain_resolution,
        'one_eth_call_reference': one_call,
        't_chain_one_call_ms': float(one_call['median_ms']) if one_call else None,
        'k_for_Pstar_0.5_ge_100_one_call_refresh': (float(one_call['median_ms']) / (0.5 - t_local)
                                                   if one_call and t_local < 0.5 else None),
        't_local_definition': 'median verify_message at k=inf (cached path: T-9 check + ECDSA verify, 0 RPCs)',
        't_chain_definition': 'median verify_message at k=1 minus t_local (added cost of one refresh)',
        'latency_budget_constants': {'t_local_ms': LB_T_LOCAL_MS, 't_chain_ms': LB_T_CHAIN_MS},
        'k_for_Pstar_0.5_ge_100_this_run': knee,
        'k_for_Pstar_0.5_ge_100_latency_budget': lb_knee,
        'per_k': table,
    }


CSV_COLUMNS = ['k', 'n', 'median_ms', 'p95_ms', 'mean_ms', 'min_ms', 'max_ms', 'stdev_ms',
               'refreshes_in_window', 'cached_in_window', 'refresh_median_ms', 'cached_median_ms',
               'refresh_rpc_median', 'cached_rpc_max', 'rpc_calls_mean',
               'analytic_this_run_ms', 'analytic_latency_budget_ms',
               'P*(0.5)_measured_mean', 'P*(0.5)_measured_median', 'P*(0.5)_analytic_this_run',
               'P*(0.5)_analytic_latency_budget',
               'staleness_max_accepted_after_revocation', 'staleness_bound_k_minus_1', 'staleness_within_bound']


def write_csv(path, rows, derived, stale):
    d = {e['k']: e for e in derived['per_k']}
    st = {s['k']: s for s in stale}
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            out = {c: r.get(c) for c in CSV_COLUMNS}
            out.update({c: d[r['k']].get(c) for c in CSV_COLUMNS if c in d[r['k']]})
            s = st.get(r['k'])
            if s:
                out['staleness_max_accepted_after_revocation'] = s['max_accepted_after_revocation']
                out['staleness_bound_k_minus_1'] = s['bound_k_minus_1']
                out['staleness_within_bound'] = s['within_bound'] if s['bound_k_minus_1'] is not None else 'unbounded'
            for c in out:
                if isinstance(out[c], float):
                    out[c] = f"{out[c]:.4f}"
            w.writerow(out)


def fmt(x, d=3):
    return '-' if x is None else (f"{x:.{d}f}" if isinstance(x, float) else str(x))


def write_md(path, env, cfg, rows, derived, stale):
    L = ["# Freshness-k: ERC-1056 verify with the sender's chain state refreshed every k messages\n",
         "Generated by `scripts/experiment_freshness_k.py` (a sibling of `experiment_pki_vs_erc1056.py`, reusing its "
         "harness; the #21 results are untouched). Verifier: `ERC1056Provider(refresh_every=k)`; k = 1 is the "
         "uncached #21 path, k = inf resolves once per sender. The T-9 freshness/replay policy is installed "
         "identically for every k and runs before the cache. "
         f"n = {cfg['n']} measured verifies per k after {cfg['warmup']} discarded warm-ups, one sender, "
         "a fresh verifier per k, timed with `time.perf_counter_ns`.\n",
         "## Environment\n", "| Item | Value |", "|---|---|"]
    for k in ('date_utc', 'git_commit', 'git_dirty', 'python_version', 'node_version', 'hardhat_version',
              'web3_version', 'cryptography_version', 'numpy_version', 'matplotlib_version', 'chain_id', 'automine',
              'mining_mode', 'rpc_url', 'contract_address', 'contract_deploy_gas', 'registry_artifact',
              'registry_bytecode_sha256', 'registry_compiler', 'cpu_model', 'cpu_count', 'os'):
        L.append(f"| {k} | {env.get(k)} |")
    fr = env.get('freshness', {})
    L.append(f"| freshness (T-9) | {fr} |")
    L.append("")
    L.append("## 1. Latency per k (ms)\n")
    L.append("| k | n | median | p95 | mean (amortised) | min | max | refreshes in window | cached median | "
             "refresh median | RPCs per refresh | RPCs per cached verify (max) |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        L.append(f"| {r['k']} | {r['n']} | {fmt(r['median_ms'])} | {fmt(r['p95_ms'])} | {fmt(r['mean_ms'])} | "
                 f"{fmt(r['min_ms'])} | {fmt(r['max_ms'])} | {r['refreshes_in_window']} | "
                 f"{fmt(r['cached_median_ms'])} | {fmt(r['refresh_median_ms'])} | "
                 f"{fmt(r['refresh_rpc_median'], 0)} | {fmt(r['cached_rpc_max'])} |")
    L.append("")
    L.append("## 2. Measured vs analytic t_eff = t_local + t_chain / k\n")
    L.append(f"Constants recomputed from this run: **t_local = {derived['t_local_ms']:.3f} ms** "
             f"({derived['t_local_definition']}); **t_chain = {derived['t_chain_ms']:.3f} ms** "
             f"({derived['t_chain_definition']}; the provider-internal resolution time at k = 1 has median "
             f"{fmt(derived['t_chain_from_resolution_ms'])} ms). LATENCY_BUDGET.md §4 used "
             f"{LB_T_LOCAL_MS} + {LB_T_CHAIN_MS}/k ms.\n")
    L.append("| k | measured mean | measured median | measured p95 | analytic (this run) | mean / analytic | "
             "analytic (LATENCY_BUDGET 0.4 + 2.5/k) | P*(0.5) mean | P*(0.5) median | P*(0.5) p95 | "
             "P*(0.5) analytic, this run | P*(0.5) analytic, LATENCY_BUDGET |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for e in derived['per_k']:
        L.append(f"| {e['k']} | {fmt(e['measured_mean_ms'])} | {fmt(e['measured_median_ms'])} | "
                 f"{fmt(e['measured_p95_ms'])} | {fmt(e['analytic_this_run_ms'])} | {fmt(e['mean_over_analytic'], 2)} | "
                 f"{fmt(e['analytic_latency_budget_ms'])} | {e['P*(0.5)_measured_mean']} | "
                 f"{e['P*(0.5)_measured_median']} | {e['P*(0.5)_measured_p95']} | "
                 f"{e['P*(0.5)_analytic_this_run']} | {e['P*(0.5)_analytic_latency_budget']} |")
    L.append("")
    oc = derived.get('one_eth_call_reference')
    if oc:
        L.append(f"**Why the constants differ from LATENCY_BUDGET.md §4.** Its 2.5 ms was the cost of *one* registry "
                 "`eth_call` (a `changed()`/`isRevoked` freshness probe). This provider's refresh is a full "
                 "resolution (`getIdentityInfo` + `eth_getLogs` + web3's `eth_chainId` calls, see RPCs per refresh). "
                 f"Measured here, one `isRevoked` eth_call costs **{oc['median_ms']:.3f} / {oc['p95_ms']:.3f} ms** "
                 f"(median / p95, n = {oc['n']}, {fmt(oc['rpc_calls_median'], 0)} RPCs). A hypothetical one-call refresh "
                 "gives t_eff = t_local + that / k:\n")
        L.append("| k | analytic, one-call refresh (ms) | P*(0.5) |")
        L.append("|---|---:|---:|")
        for e in derived['per_k']:
            L.append(f"| {e['k']} | {fmt(e['analytic_one_call_refresh_ms'])} | {e['P*(0.5)_analytic_one_call_refresh']} |")
        L.append("")
        L.append(f"With a one-call refresh, analytic P*(0.5) reaches 100 at k ≈ "
                 f"{fmt(derived['k_for_Pstar_0.5_ge_100_one_call_refresh'], 1)} (not measured: that verifier is not "
                 "implemented).\n")
    L.append("P*(f) = floor(f · 100 ms / t) (LATENCY_BUDGET.md §2). The **mean** is the amortised per-message cost "
             "(one refresh every k messages), which is the quantity the analytic curve and P* (a throughput "
             "bound) refer to; the median of a k > 1 run is the cached cost because most messages are cached, "
             "and the p95 shows the refresh tail a single message can hit.\n")
    L.append("| f | " + " | ".join(f"P*(f), k={e['k']} (mean)" for e in derived['per_k']) + " |")
    L.append("|---|" + "---:|" * len(derived['per_k']))
    for f in FRACTIONS:
        L.append(f"| {f} | " + " | ".join(str(e[f'P*({f})_measured_mean']) for e in derived['per_k']) + " |")
    L.append("")
    knee = derived['k_for_Pstar_0.5_ge_100_this_run']
    L.append(f"k at which the analytic P*(0.5) reaches 100 (t_eff ≤ 0.5 ms): this run "
             f"**{fmt(knee, 1)}**; LATENCY_BUDGET constants {derived['k_for_Pstar_0.5_ge_100_latency_budget']:.1f}.\n")
    L.append("## 3. Staleness bound: revocation mid-stream\n")
    L.append("For each trial a fresh sender is registered; a verifier with refresh k accepts m_pre messages; the "
             "sender's identity is revoked (`revokeIdentity`, receipt awaited, so the revocation is on chain); then "
             "fresh, genuine, in-window messages are verified until the first rejection. **Accepted after "
             "revocation** counts the messages that still verified although the revocation was already mined. "
             "Prediction: k − 1 − ((m_pre − 1) mod k); its maximum over phases is the bound k − 1.\n")
    L.append("| k | trials | accepted after revocation, per trial (m_pre = 1, 2, ...) | max | bound k − 1 | "
             "within bound | equals prediction | rejected thereafter |")
    L.append("|---|---:|---|---:|---:|:---:|:---:|:---:|")
    for s in stale:
        obs = ", ".join(str(t['accepted_after_revocation']) + ("+ (cap)" if t['capped'] else "")
                        for t in s['trials'])
        bound = s['bound_k_minus_1']
        L.append(f"| {s['k']} | {len(s['trials'])} | {obs} | {s['max_accepted_after_revocation']} | "
                 f"{bound if bound is not None else 'none (unbounded)'} | "
                 f"{s['within_bound'] if bound is not None else 'n/a'} | "
                 f"{s['matches_prediction'] if bound is not None else 'n/a'} | {s['all_stay_rejected']} |")
    L.append("")
    if any(s['k'] == 'inf' for s in stale):
        s = next(s for s in stale if s['k'] == 'inf')
        L.append(f"For k = inf the trials used m_pre = {[t['m_pre'] for t in s['trials']]} and stopped at the cap "
                 f"of {s['trials'][0]['cap']} post-revocation messages, every one of which verified: a verifier "
                 "that never refreshes never sees the revocation.\n")
    L.append("**Security trade-off.** With k > 1 a revocation (or key rotation) takes effect at the sender's next "
             "refresh, i.e. up to k − 1 messages late; at 10 Hz BSMs that is up to (k − 1) × 100 ms of a revoked "
             "vehicle's messages being accepted (0.4 s at k = 5, 2.4 s at k = 25). With k = 1 none are. "
             "With k = inf a revocation is never seen by a verifier that has already cached the sender. The T-9 "
             "freshness window (1.0 s) bounds message *age*, not state staleness: the two are independent.\n")
    L.append("## Caveats\n")
    L.append("1. **Hardhat local (M1).** The refresh cost t_chain is a localhost JSON-RPC + Hardhat EVM round "
             "trip set (see `refresh_rpc_median`); on a public network a refresh costs tens of ms or more, so "
             "t_chain and the k needed to reach a given P* grow accordingly; t_local (no RPC) does not change.")
    L.append("2. **K-5.** The registry is the cv2x `ERC1056Registry` (whole-identity revoked flag, `getIdentityInfo`), "
             "not `EthereumDIDRegistry`; the refresh cost corresponds to one resolution of an identity with a "
             "single key event (1 `eth_getLogs` hop).")
    L.append("3. **One sender, serial, one core.** Per-sender caching means a verifier with P neighbours "
             "refreshes P identities per k messages each; the amortised per-message cost is the same, which is "
             "what P* uses. Cache memory and its eviction policy are not modelled.")
    L.append("4. **k order.** The k values were run in the order listed, each with a fresh verifier (own HTTP "
             "session); node-state drift across the sweep is not randomised.")
    L.append("5. **Revocation semantics.** The staleness test revokes the whole identity (`revokeIdentity`). A key "
             "rotation is subject to the same bound (the cached key is used until the next refresh); it was not "
             "measured separately.")
    L.append("6. **k = 1 path.** The k = 1 verify is the #21 code path plus one counter increment and one "
             "comparison (the cache dispatch), i.e. nanoseconds against milliseconds.")
    L.append("")
    with open(path, 'w') as f:
        f.write("\n".join(L))


def write_png(path, derived) -> Optional[str]:
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except Exception as e:  # pragma: no cover
        return f"matplotlib unavailable: {e}"
    per = derived['per_k']
    finite = [e for e in per if e['k'] != 'inf']
    xs = [int(e['k']) for e in finite]
    inf_x = max(xs) * 4 if xs else 100
    allx = xs + ([inf_x] if any(e['k'] == 'inf' for e in per) else [])
    order = finite + [e for e in per if e['k'] == 'inf']
    grid = np.logspace(0, math.log10(inf_x), 200)
    tl, tc = derived['t_local_ms'], derived['t_chain_ms']
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
    a1.plot(grid, tl + tc / grid, color='#4269d0', label=f'analytic, this run ({tl:.2f} + {tc:.2f}/k)')
    a1.plot(grid, LB_T_LOCAL_MS + LB_T_CHAIN_MS / grid, color='#9a9a9a', ls='--',
            label='analytic, LATENCY_BUDGET (0.4 + 2.5/k)')
    a1.scatter(allx, [e['measured_mean_ms'] for e in order], color='#ff725c', zorder=3, label='measured mean')
    a1.scatter(allx, [e['measured_median_ms'] for e in order], color='#3ca951', marker='x', zorder=3,
               label='measured median')
    a1.set_xscale('log'); a1.set_yscale('log')
    a1.set_xlabel('k (messages per refresh; rightmost = ∞)'); a1.set_ylabel('per-message verify cost t (ms)')
    a1.set_xticks(allx); a1.set_xticklabels([str(x) for x in xs] + (['∞'] if len(allx) > len(xs) else []))
    a1.legend(fontsize=7)
    a2.plot(grid, [math.floor(50 / (tl + tc / g)) for g in grid], color='#4269d0', label='analytic, this run')
    a2.plot(grid, [math.floor(50 / (LB_T_LOCAL_MS + LB_T_CHAIN_MS / g)) for g in grid], color='#9a9a9a', ls='--',
            label='analytic, LATENCY_BUDGET')
    a2.scatter(allx, [e['P*(0.5)_measured_mean'] for e in order], color='#ff725c', zorder=3,
               label='measured (mean)')
    a2.axhline(100, color='#555', lw=0.8, ls=':'); a2.text(1.05, 104, 'dense-traffic threshold (100)', fontsize=7)
    a2.set_xscale('log'); a2.set_yscale('log')
    a2.set_xlabel('k (rightmost = ∞)'); a2.set_ylabel('P*(0.5) neighbours per 100 ms')
    a2.set_xticks(allx); a2.set_xticklabels([str(x) for x in xs] + (['∞'] if len(allx) > len(xs) else []))
    a2.legend(fontsize=7)
    fig.suptitle('Freshness-k: ERC-1056 verify, Hardhat local (M1)', fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--n', type=int, default=250, help='measured verifies per k (>= 50)')
    ap.add_argument('--warmup', type=int, default=3)
    ap.add_argument('--ks', default='1,5,25,inf')
    ap.add_argument('--rpc-url', default='http://127.0.0.1:8545')
    ap.add_argument('--contract-address', default=None)
    ap.add_argument('--deploy', action='store_true', help='deploy a fresh ERC1056Registry (tracked artifact)')
    ap.add_argument('--registry-artifact', default=os.environ.get('CV2X_REGISTRY_ARTIFACT'))
    ap.add_argument('--inf-cap', type=int, default=50, help='post-revocation messages tried for k = inf')
    ap.add_argument('--out-dir', default=os.path.join(ROOT, 'results'))
    ap.add_argument('--out-name', default='freshness_k')
    args = ap.parse_args()
    if args.n < 50:
        ap.error('--n must be >= 50')
    ks = parse_ks(args.ks)

    deploy_gas = None
    artifact_info = {'registry_artifact': None, 'registry_bytecode_sha256': None, 'registry_compiler': None}
    address = args.contract_address
    if args.deploy:
        address, deploy_gas = H.deploy_registry(args.rpc_url, args.registry_artifact)
        artifact_info = H.registry_artifact_info(args.registry_artifact or H.TRACKED_REGISTRY_ARTIFACT)
    if address is None:
        ap.error('--deploy or --contract-address is required')
    signer = ERC1056Provider(args.rpc_url, contract_address=address)
    w3 = signer.w3
    try:
        automine = w3.provider.make_request('hardhat_getAutomine', []).get('result')
    except Exception:
        automine = None
    chain_info = {'rpc_url': args.rpc_url, 'chain_id': int(w3.eth.chain_id),
                  'block_gas_limit': int(w3.eth.get_block('latest')['gasLimit']), 'automine': automine,
                  'mining_mode': 'automine (no interval mining)' if automine else 'unknown/interval',
                  'contract_address': address, 'contract_deploy_gas': deploy_gas,
                  'client_version': w3.client_version, **artifact_info}
    env = H.environment(chain_info, args.n, args.warmup)
    env['freshness'] = dict(H.BENCHMARK_FRESHNESS)
    env['numpy_version'] = np.__version__
    try:
        import matplotlib
        env['matplotlib_version'] = matplotlib.__version__
    except Exception:
        env['matplotlib_version'] = None
    print("Environment:", json.dumps(env, indent=2, default=str))

    run_tag = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    sender = f"FK_SENDER_{run_tag}"
    signer.fund_vehicle_account(sender, H.FUND_WEI)
    signer.register_vehicle(sender, H.VEHICLE_METADATA)

    print("\n=== Part 1: latency ===")
    rows = [run_latency(signer, sender, args.rpc_url, address, k, args.n, args.warmup) for k in ks]
    # Reference: one registry eth_call (isRevoked), the refresh cost LATENCY_BUDGET §4 assumed
    # ("one changed() freshness call per message"); not what this provider's refresh does.
    ref_p = make_verifier(args.rpc_url, address, 1)
    ref_b = H.Backend('erc1056_one_call', ref_p, True, H.RPCCounter(ref_p.w3))
    sender_addr = signer.vehicles[sender]['address']
    ref = H.summarize(H.measure(
        ref_b, 'isRevoked', args.n, args.warmup, prepare=lambda i: sender_addr,
        run=lambda a: ref_p.check_revocation_status_by_address(a),
        check=lambda a, r: {} if r[0] is False else H._fail("live sender reported revoked")))
    ref.pop('gas_samples', None)
    print(f"  one eth_call (isRevoked): median={ref['median_ms']:.3f} p95={ref['p95_ms']:.3f} ms")
    derived = derive(rows, ref)
    print("\n=== Part 2: staleness ===")
    stale = [run_staleness(signer, args.rpc_url, address, k, run_tag, args.inf_cap) for k in ks]

    cfg = {'n': args.n, 'warmup': args.warmup, 'ks': [k_label(k) for k in ks], 'run_tag': run_tag,
           'budget_ms': BUDGET_MS, 'fractions': list(FRACTIONS), 'inf_cap': args.inf_cap,
           'refresh_semantics': 'per sender (canonical DID); message 1 resolves, messages 2..k cached, k+1 resolves'}
    os.makedirs(args.out_dir, exist_ok=True)
    base = os.path.join(args.out_dir, args.out_name)
    with open(base + '.json', 'w') as f:
        json.dump({'environment': env, 'config': cfg, 'latency': rows, 'derived': derived,
                   'staleness': stale}, f, indent=2, default=str)
    write_csv(base + '.csv', rows, derived, stale)
    write_md(base + '.md', env, cfg, rows, derived, stale)
    png_err = write_png(base + '.png', derived)
    print(f"\nWrote {base}.{{json,csv,md}}" + ("" if png_err else " and .png") + (f" ({png_err})" if png_err else ""))

    bad = [s['k'] for s in stale if s['bound_k_minus_1'] is not None and not s['within_bound']]
    if bad:
        print(f"STALENESS BOUND VIOLATED for k={bad}")
        sys.exit(2)


if __name__ == '__main__':
    main()
