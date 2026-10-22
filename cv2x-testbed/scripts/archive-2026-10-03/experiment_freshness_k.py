#!/usr/bin/env python3
"""
Freshness sweep for the ERC-1056 verifier (docs/LATENCY_BUDGET.md section 3-4).

Measures verify_message for an ERC-1056 verifier that caches the resolved key
and revocation state of a sender and re-reads the chain only every k-th message
from that sender (ERC1056Provider(freshness_k=k)): one raw eth_call of
changed(identity) per refresh, full re-resolution only if that block differs.

Rows measured in one run, each over n warm verifications of messages from ONE
registered sender after `warmup` discarded warm-up runs (the first warm-up run
is the sender's first message, i.e. the full resolution that fills the cache):

  pki_standard        reference: X.509 certificate travels with the message (no network)
  erc1056 off         reference: current uncached provider (key + revocation read
                      from the registry on every message; 7 JSON-RPC round trips)
  erc1056 k=1         chain consulted on EVERY message, but via one changed() round trip
  erc1056 k=5,25,100  chain consulted on every k-th message
  erc1056 k=inf       never refreshed after the first resolution

Per row: median / p95 / mean ms, JSON-RPC calls per message (counted at the
web3 provider), neighbour saturation P*(f) = floor(f * 100 ms / t_median) for
f in {0.25, 0.5, 1.0}, and the analytic prediction t_eff(k) = 0.4 + 2.5 / k ms
from docs/LATENCY_BUDGET.md section 4 for comparison. An untimed revocation
check per k records after how many messages a revoked sender is rejected.

Outputs (cv2x-testbed/results/): freshness_k.csv, freshness_k.json, freshness_k.md

Usage
  # start chain + deploy first:
  #   npx hardhat node &
  #   npx hardhat run scripts/deploy.js --network localhost
  python3 scripts/experiment_freshness_k.py [--n 200] [--warmup 3] [--k 1,5,25,100,inf]
"""

import argparse
import csv
import json
import math
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from experiment_pki_vs_erc1056 import (  # noqa: E402
    Backend, RPCCounter, StandardPKIAdapter, FUND_WEI, VEHICLE_METADATA,
    environment, make_bsm, measure, summarize, _fail,
)

FRACTIONS = (0.25, 0.5, 1.0)
PRED_OFFCHAIN_MS = 0.4   # analytic: signature check only (LATENCY_BUDGET.md section 3)
PRED_ROUNDTRIP_MS = 2.5  # analytic: one local-Hardhat round trip (LATENCY_BUDGET.md section 4)


def parse_k(text: str) -> List[Optional[int]]:
    out: List[Optional[int]] = []
    for tok in text.split(','):
        tok = tok.strip().lower()
        if not tok:
            continue
        out.append(0 if tok in ('inf', 'infinity', '0') else int(tok))
    return out


def k_label(k) -> str:
    if k is None:
        return 'off'
    return 'inf' if k == 0 else str(k)


def predicted_t_eff(k) -> Optional[float]:
    """0.4 + 2.5/k ms; 0.4 for k=inf; None for rows the model does not cover."""
    if k is None:
        return None
    return PRED_OFFCHAIN_MS if k == 0 else PRED_OFFCHAIN_MS + PRED_ROUNDTRIP_MS / k


def saturation(t_ms: float, f: float) -> int:
    return int(math.floor(f * 100.0 / t_ms)) if t_ms > 0 else 0


def measure_verify(backend: Backend, sender: str, n: int, warmup: int) -> Dict[str, Any]:
    """n warm verify_message() calls of fresh messages from `sender`; prepare (signing) is untimed."""
    prov = backend.provider
    captured: Dict[str, Any] = {'calls': 0, 'first': None, 'warm_refresh': None}

    def check(ctx, r):
        if r[0] is not True:
            _fail("verify_message returned False for a genuine message")
        extra: Dict[str, Any] = {}
        if backend.is_chain:
            extra['resolution_ms'] = float(r[1].resolution_time_ms)
            idx = captured['calls']          # 0-based message index incl. warm-ups
            captured['calls'] += 1
            if backend.rpc.count > 0:
                methods = list(backend.rpc.methods)
                if idx == 0:
                    captured['first'] = methods            # sender's first message: full resolution
                elif idx >= warmup and captured['warm_refresh'] is None:
                    captured['warm_refresh'] = methods     # first warm message that touched the chain
        return extra

    samples = measure(backend, 'verify_message', n, warmup,
                      prepare=lambda i: prov.sign_message(sender, make_bsm(1000 + i)),
                      run=lambda signed: prov.verify_message(signed),
                      check=check)
    s = summarize(samples)
    s.pop('rpc_methods', None)
    rpc = np.array([x.rpc_calls for x in samples], dtype=float)
    s['rpc_calls_mean'] = float(rpc.mean()) if backend.is_chain else 0.0
    s['rpc_calls_max'] = int(rpc.max()) if backend.is_chain else 0
    s['messages_with_rpc'] = int((rpc > 0).sum()) if backend.is_chain else 0
    s['first_message_rpc_methods'] = captured.get('first')
    s['refresh_rpc_methods'] = captured.get('warm_refresh')
    s['samples_ms'] = [round(x.elapsed_ms, 4) for x in samples]
    s['samples_rpc'] = [int(x.rpc_calls) for x in samples]
    # mean over messages WITHOUT a chain read (the pure cached cost)
    cached = [x.elapsed_ms for x in samples if x.rpc_calls == 0]
    s['cached_only_median_ms'] = float(np.median(cached)) if cached else None
    for f in FRACTIONS:
        s[f'p_star_{f}'] = saturation(s['median_ms'], f)
        s[f'p_star_mean_{f}'] = saturation(s['mean_ms'], f)
    return s


def revocation_check(prov, sender: str, k, limit: int) -> Dict[str, Any]:
    """Untimed: revoke the sender, count messages until verify_message rejects (<= limit)."""
    before = prov.sign_message(sender, make_bsm(5000))
    tampered = dict(before)
    tampered['message'] = dict(before['message'], speed=99.9)
    tampered_rejected = prov.verify_message(tampered)[0] is False
    prov.revoke_credential(sender, "freshness experiment")
    detected_after = None
    for i in range(limit):
        if prov.verify_message(prov.sign_message(sender, make_bsm(6000 + i)))[0] is False:
            detected_after = i + 1
            break
    expected_max = None if k is None else (None if k == 0 else k)
    return {
        'tampered_message_rejected': tampered_rejected,
        'revocation_detected_after_messages': detected_after,
        'messages_tried': limit,
        'bound_k': expected_max,
        'within_bound': (detected_after is not None and detected_after <= expected_max) if expected_max else
                        (detected_after is None if k == 0 else detected_after == 1),
    }


# --------------------------------------------------------------------------
# Output writers
# --------------------------------------------------------------------------
CSV_COLUMNS = ['provider', 'freshness_k', 'n', 'median_ms', 'p95_ms', 'mean_ms', 'min_ms', 'max_ms',
               'stdev_ms', 'rpc_calls_mean', 'rpc_calls_median', 'rpc_calls_max', 'messages_with_rpc',
               'cached_only_median_ms', 'p_star_0.25', 'p_star_0.5', 'p_star_1.0',
               'p_star_mean_0.5', 'predicted_t_eff_ms', 'median_over_predicted', 'mean_over_predicted',
               'revocation_detected_after_messages', 'tampered_message_rejected']


def write_csv(path: str, rows: List[Dict[str, Any]]):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            out = {k: r.get(k) for k in CSV_COLUMNS}
            for k in ('median_ms', 'p95_ms', 'mean_ms', 'min_ms', 'max_ms', 'stdev_ms',
                      'cached_only_median_ms', 'predicted_t_eff_ms', 'median_over_predicted',
                      'mean_over_predicted', 'rpc_calls_mean'):
                if out.get(k) is not None:
                    out[k] = f"{out[k]:.4f}"
            w.writerow(out)


def fmt(x, digits=3):
    return "-" if x is None else f"{x:.{digits}f}"


ENV_KEYS = ('date_utc', 'git_commit', 'git_dirty', 'python_version', 'node_version', 'hardhat_version',
            'ethers_version', 'web3_version', 'solc_version', 'cryptography_version', 'chain_id',
            'block_gas_limit', 'automine', 'contract_address', 'contract_deploy_gas',
            'cpu_model', 'cpu_count', 'os')


def write_md(path: str, env: Dict[str, Any], rows: List[Dict[str, Any]], n: int, warmup: int,
             skipped: Optional[str]):
    L: List[str] = []
    L.append("# ERC-1056 verifier freshness sweep: t_eff(k), measured\n")
    L.append("Generated by `scripts/experiment_freshness_k.py`. Each row is `verify_message` over "
             f"n={n} warm messages from one registered sender after {warmup} discarded warm-up runs "
             "(the first warm-up run is the sender's first message, which fills the verifier cache), "
             "timed with `time.perf_counter_ns`. JSON-RPC calls are counted at the web3 HTTP provider. "
             "`k` is the freshness parameter of `ERC1056Provider(freshness_k=k)`: the cached key / "
             "revocation state of a sender is re-checked against the chain every k-th message with one "
             "`eth_call` of `changed(identity)` (full re-resolution only if that block number changed); "
             "`off` is the shipped uncached verifier (every message: `getIdentityInfo` + `eth_getLogs` + "
             "`isRevoked`, 7 round trips including web3's `eth_chainId` repeats); `inf` never refreshes.\n")
    L.append("## Environment\n")
    L.append("| Item | Value |\n|---|---|")
    for k in ENV_KEYS:
        L.append(f"| {k} | {env.get(k)} |")
    L.append("")
    if skipped:
        L.append(f"**ERC-1056 rows not run:** {skipped}\n")

    L.append("## Results (milliseconds; P*(f) = floor(f * 100 ms / median))\n")
    L.append("| Row | k | n | median | p95 | mean | RPC/msg (mean) | msgs with RPC | P*(0.25) | P*(0.5) | P*(1.0) | predicted t_eff = 0.4 + 2.5/k | median / predicted | mean / predicted |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        L.append(f"| {r['provider']} | {r['freshness_k']} | {r['n']} | {fmt(r['median_ms'])} | {fmt(r['p95_ms'])} | "
                 f"{fmt(r['mean_ms'])} | {fmt(r['rpc_calls_mean'], 2) if r['provider'] != 'pki_standard' else '-'} | "
                 f"{r['messages_with_rpc'] if r['provider'] != 'pki_standard' else '-'} | "
                 f"{r['p_star_0.25']} | **{r['p_star_0.5']}** | {r['p_star_1.0']} | "
                 f"{fmt(r['predicted_t_eff_ms'])} | {fmt(r['median_over_predicted'], 2)} | {fmt(r['mean_over_predicted'], 2)} |")
    L.append("")
    L.append("Because a refresh lands on only every k-th message, the median of a k >= 3 row is the cost "
             "of a cache hit, while the mean carries the amortised refresh cost. P*(0.5) from the mean "
             "(the amortised figure the analytic model actually predicts): " +
             ", ".join(f"{r['freshness_k']}={r['p_star_mean_0.5']}" for r in rows if r['provider'] != 'pki_standard') + ".\n")
    L.append("| Row | k | min | max | stdev | median of cache-hit messages (0 RPC) | RPC/msg median | RPC/msg max |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        L.append(f"| {r['provider']} | {r['freshness_k']} | {fmt(r['min_ms'])} | {fmt(r['max_ms'])} | {fmt(r['stdev_ms'])} | "
                 f"{fmt(r.get('cached_only_median_ms'))} | {fmt(r.get('rpc_calls_median'), 0)} | {r.get('rpc_calls_max')} |")
    L.append("")
    meth = [r for r in rows if r.get('refresh_rpc_methods') or r.get('first_message_rpc_methods')]
    if meth:
        L.append("JSON-RPC methods issued per row: on the sender's first message (full resolution, warm-up 0, "
                 "untimed here) and on the first *warm* message that touched the chain (a refresh):\n")
        for r in meth:
            first = ', '.join(r['first_message_rpc_methods']) if r.get('first_message_rpc_methods') else '-'
            warm = ', '.join(r['refresh_rpc_methods']) if r.get('refresh_rpc_methods') else 'none (no warm message touched the chain)'
            L.append(f"- k={r['freshness_k']}: first message: {first}; warm refresh: {warm}")
        L.append("")

    L.append("## Revocation / tampering checks (untimed)\n")
    L.append("After the timed run the sender is revoked on-chain (`revokeIdentity`, which also updates "
             "`changed(identity)`) and fresh messages are verified until one is rejected. A verifier with "
             "freshness k must reject within k messages; `inf` never re-reads and keeps accepting (by design).\n")
    L.append("| Row | k | tampered message rejected | revoked sender rejected after (messages) | bound | within bound |")
    L.append("|---|---:|:---:|---:|---:|:---:|")
    for r in rows:
        rc = r.get('revocation_check')
        if not rc:
            continue
        det = rc['revocation_detected_after_messages']
        det_text = str(det) if det is not None else "never (tried %d)" % rc['messages_tried']
        L.append(f"| {r['provider']} | {r['freshness_k']} | {rc['tampered_message_rejected']} | "
                 f"{det_text} | "
                 f"{rc['bound_k'] if rc['bound_k'] is not None else ('1 (every message)' if r['freshness_k'] in ('off', '1') else 'none')} | "
                 f"{rc['within_bound']} |")
    L.append("")

    L.append("## Caveats\n")
    L.append("1. **Local Hardhat round trip.** All chain reads go to a single Hardhat node on localhost; the "
             "per-refresh cost here is one HTTP JSON-RPC `eth_call` (~1.5-3 ms on this machine). A remote "
             "RPC endpoint adds its network latency to every refresh, i.e. to the `2.5/k` term only; the "
             "cache-hit cost (`inf` row) does not change.")
    L.append("2. **What the refresh is.** The cached verifier issues `changed(identity)` as a raw `eth_call` "
             "through the provider (one round trip). The shipped uncached path (`off`) goes through web3's "
             "contract wrapper, which adds an `eth_chainId` request around each call; its 7 round trips are "
             "therefore 3 registry reads + 4 client-side repeats, as in `pki_vs_erc1056.md`.")
    L.append("3. **The analytic model is for the mean.** `t_eff = 0.4 + 2.5/k` is an amortised (mean) cost; "
             "the task's P*(f) uses the median, which for k >= 3 is a cache hit. Both are reported.")
    L.append("4. **One sender, serial, single process.** With many senders the cache holds one entry per "
             "sender and refreshes are per sender; the per-message cost does not depend on the number of "
             "senders, but the first message from each new sender costs a full resolution "
             "(`getIdentityInfo` + `eth_getLogs`, the `resolve_identity` row of `pki_vs_erc1056.md`).")
    L.append("5. **Staleness is the price.** A verifier with freshness k accepts messages from a revoked or "
             "key-rotated sender for up to k messages (k/10 s at 10 Hz); `inf` never notices. The sweep "
             "measures the latency side of that trade-off only.")
    L.append("")
    with open(path, 'w') as f:
        f.write("\n".join(L))


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--n', type=int, default=200, help='warm verifications per row (>= 30)')
    ap.add_argument('--warmup', type=int, default=3, help='discarded warm-up runs per row')
    ap.add_argument('--k', default='1,5,25,100,inf', help='comma-separated freshness values (inf or 0 = never)')
    ap.add_argument('--rpc-url', default='http://127.0.0.1:8545')
    ap.add_argument('--contract-address', default=None,
                    help='ERC1056Registry address (default: deployments/localhost.json)')
    ap.add_argument('--out-dir', default=os.path.join(ROOT, 'results'))
    ap.add_argument('--render-only', action='store_true',
                    help='do not measure; re-write the .csv/.md from the existing .json in --out-dir')
    args = ap.parse_args()
    if args.n < 30:
        ap.error('--n must be >= 30')
    ks = parse_k(args.k)

    csv_path = os.path.join(args.out_dir, 'freshness_k.csv')
    json_path = os.path.join(args.out_dir, 'freshness_k.json')
    md_path = os.path.join(args.out_dir, 'freshness_k.md')

    if args.render_only:
        with open(json_path) as f:
            saved = json.load(f)
        write_csv(csv_path, saved['results'])
        write_md(md_path, saved['environment'], saved['results'], saved['config']['n'],
                 saved['config']['warmup'], saved.get('erc1056_skipped'))
        print(f"Re-rendered .csv/.md from {json_path}")
        return

    # Chain connection (never fabricate: if absent, record why and run the PKI row only)
    skipped: Optional[str] = None
    chain_info: Optional[Dict[str, Any]] = None
    make_provider = None
    try:
        from identity.erc1056_provider import ERC1056Provider
        address = args.contract_address
        deploy_gas = None
        if address is None:
            with open(os.path.join(ROOT, 'deployments', 'localhost.json')) as f:
                dep = json.load(f)
            address = dep['contractAddress']
            deploy_gas = int(dep.get('gasUsed')) if dep.get('gasUsed') else None
        probe = ERC1056Provider(args.rpc_url, contract_address=address)
        w3 = probe.w3
        latest = w3.eth.get_block('latest')
        try:
            automine = w3.provider.make_request('hardhat_getAutomine', []).get('result')
        except Exception:
            automine = None
        chain_info = {
            'rpc_url': args.rpc_url,
            'chain_id': int(w3.eth.chain_id),
            'block_gas_limit': int(latest['gasLimit']),
            'automine': automine,
            'contract_address': address,
            'contract_deploy_gas': deploy_gas,
            'client_version': w3.client_version if hasattr(w3, 'client_version') else None,
        }

        def make_provider(k):
            return ERC1056Provider(args.rpc_url, contract_address=address, freshness_k=k)
    except Exception as e:
        skipped = f'not run: {type(e).__name__}: {e}'
        print(f"WARNING: ERC-1056 rows not run: {e}")

    env = environment(chain_info, args.n, args.warmup)
    env['rows'] = 'verify_message only (one sender)'
    print("Environment:", json.dumps(env, indent=2))

    run_tag = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    rows: List[Dict[str, Any]] = []

    def finish_row(provider_name: str, k, s: Dict[str, Any], rev: Optional[Dict[str, Any]]):
        s['provider'] = provider_name
        s['freshness_k'] = k_label(k)
        s['predicted_t_eff_ms'] = predicted_t_eff(k)
        s['median_over_predicted'] = (s['median_ms'] / s['predicted_t_eff_ms']) if s['predicted_t_eff_ms'] else None
        s['mean_over_predicted'] = (s['mean_ms'] / s['predicted_t_eff_ms']) if s['predicted_t_eff_ms'] else None
        s['revocation_check'] = rev
        if rev:
            s['revocation_detected_after_messages'] = rev['revocation_detected_after_messages']
            s['tampered_message_rejected'] = rev['tampered_message_rejected']
        rows.append(s)
        print(f"  {provider_name:<13} k={s['freshness_k']:<4} median={s['median_ms']:.3f} ms  p95={s['p95_ms']:.3f} ms  "
              f"mean={s['mean_ms']:.3f} ms  rpc/msg={s['rpc_calls_mean']:.2f}  P*(0.5)={s['p_star_0.5']}  "
              f"pred={fmt(s['predicted_t_eff_ms'])}  revoked-detected-after={rev['revocation_detected_after_messages'] if rev else '-'}")

    # Reference: PKI (certificate travels with the message)
    print(f"\n=== pki_standard verify_message (n={args.n}, warmup={args.warmup}) ===")
    pki = StandardPKIAdapter()
    pki_sender = f"pki_{run_tag}_SENDER"
    pki.register_vehicle(pki_sender, VEHICLE_METADATA)
    b = Backend('pki_standard', pki, False)
    s = measure_verify(b, pki_sender, args.n, args.warmup)
    finish_row('pki_standard', None, s, revocation_check(pki, pki_sender, None, 5))

    # ERC-1056: uncached reference ('off') then the k sweep
    if make_provider is not None:
        for k in [None] + ks:
            label = k_label(k)
            print(f"\n=== erc1056_did verify_message, freshness k={label} (n={args.n}, warmup={args.warmup}) ===")
            prov = make_provider(k)
            b = Backend('erc1056_did', prov, True, RPCCounter(prov.w3))
            sender = f"erc_{run_tag}_k{label}_SENDER"
            prov.fund_vehicle_account(sender, FUND_WEI)
            prov.register_vehicle(sender, VEHICLE_METADATA)
            s = measure_verify(b, sender, args.n, args.warmup)
            limit = 5 if k is None else (max(3 * k, 10) if k > 0 else max(3 * max(ks), 50))
            rev = revocation_check(prov, sender, k, limit)
            if k is not None:
                s['cache_stats'] = prov.verifier_cache_stats()
            finish_row('erc1056_did', k, s, rev)

    os.makedirs(args.out_dir, exist_ok=True)
    write_csv(csv_path, rows)
    with open(json_path, 'w') as f:
        json.dump({
            'environment': env,
            'config': {'n': args.n, 'warmup': args.warmup, 'freshness_k': [k_label(k) for k in ks],
                       'fractions': list(FRACTIONS), 'run_tag': run_tag,
                       'prediction': f'{PRED_OFFCHAIN_MS} + {PRED_ROUNDTRIP_MS}/k ms (docs/LATENCY_BUDGET.md section 4)'},
            'erc1056_skipped': skipped,
            'results': rows,
        }, f, indent=2, default=str)
    write_md(md_path, env, rows, args.n, args.warmup, skipped)
    print(f"\nWrote:\n  {csv_path}\n  {json_path}\n  {md_path}")

    bad = [r for r in rows if r.get('revocation_check') and
           (not r['revocation_check']['tampered_message_rejected'] or not r['revocation_check']['within_bound'])]
    if bad:
        print(f"CHECK FAILURES: {[(r['provider'], r['freshness_k']) for r in bad]}")
        sys.exit(2)


if __name__ == '__main__':
    main()
