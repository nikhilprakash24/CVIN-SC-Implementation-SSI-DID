#!/usr/bin/env python3
"""
M4 lifecycle parity: centralized vehicle registry vs MOBI-VID-V2
(PLAN_MOBI_SUMO.md step M4, pre-registered in §A.2; review §3.3; SC-13).

A sibling of experiment_pki_vs_erc1056.py: it imports that script's harness
(measure / summarize / RPCCounter / environment) and leaves the #21 run of
record untouched.

PRE-REGISTERED (PLAN_MOBI_SUMO.md §A.2, quoted):
  hypothesis  the centralized registry is >= 10x faster than MOBI-VID-V2 for
              birth and lifecycle writes (local), equal for history queries
              once the chain history is cached;
  metric      median/p95 ms, n = 50, plus gas for chain writes;
  stopping    none: a single full run;
  threat      the centralized registry is in-process (no network), so its
              figures are a lower bound, stated.

OPERATIONALISATION (fixed in this file BEFORE the run; not in the
pre-registration, which gives no numeric test for "equal"):
  * ">= 10x faster": median(MOBI) / median(centralized) >= 10, per write
    operation. "Lifecycle writes" = lifecycle event AND ownership transfer
    (both are VID II writes); each gets its own verdict.
  * "equal ... once cached": 0.5 <= median(MOBI cached) / median(centralized)
    <= 2.0, where "cached" = the MOBI history served from a local copy of the
    chain history with no chain contact. Two further MOBI variants are
    REPORTED but carry no verdict: uncached (every field from the chain) and
    cached + validated (2 eth_calls to detect a change).

Operations (same inputs on both backends; identity/lifecycle_backends.py)
  birth               register a vehicle birth certificate (MOBI: VIN hash +
                      AES-GCM VIN + registerVehicleBirth tx by the manufacturer)
  lifecycle_event     MAINTENANCE event by an authorised service centre, on
                      one vehicle (MOBI: recordLifecycleEvent tx)
  ownership_transfer  alternate the vehicle between two owners (MOBI:
                      transferVehicleOwnership tx signed by the current owner)
  history_query       full history of a vehicle with H lifecycle events and
                      T transfers (birth, current owner, events, transfers)

Outputs (cv2x-testbed/results/)
  lifecycle_parity.{json,csv,md}

Usage
  python3 scripts/experiment_lifecycle_parity.py --rpc-url http://127.0.0.1:8554 --deploy
"""

import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import experiment_pki_vs_erc1056 as H  # noqa: E402  (the #21 harness, imported read-only)
from identity.lifecycle_backends import (  # noqa: E402
    CentralizedLifecycleBackend, MOBIVIDV2LifecycleBackend, event_payload)

V2_ARTIFACT = os.path.join(ROOT, 'artifacts', 'contracts', 'MOBIVIDRegistryV2.sol', 'MOBIVIDRegistryV2.json')

# Operationalisation, fixed before the run (see module docstring)
WRITE_SPEEDUP_THRESHOLD = 10.0
EQUAL_BAND = (0.5, 2.0)
HISTORY_EVENTS = 10
HISTORY_TRANSFERS = 2

OPERATIONS = [
    ('birth', 'register a vehicle birth certificate', 'write'),
    ('lifecycle_event', 'record a MAINTENANCE lifecycle event', 'write'),
    ('ownership_transfer', 'transfer ownership to the other owner', 'write'),
    ('history_query', f'full history, {HISTORY_EVENTS} events + {HISTORY_TRANSFERS} transfers; MOBI uncached', 'read'),
    ('history_query_cached', 'MOBI only: history from the local copy of the chain history (no RPC)', 'read'),
    ('history_query_cached_validated', 'MOBI only: local copy after a 2-eth_call staleness probe', 'read'),
    ('history_query_unserialised_diagnostic', 'centralized only, POST-HOC diagnostic: history without '
     'dataclasses.asdict serialisation', 'read'),
]


def artifact_info(path: str) -> Dict[str, Any]:
    with open(path) as f:
        art = json.load(f)
    info = {'mobi_artifact': os.path.relpath(path, ROOT) if path.startswith(ROOT) else path,
            'mobi_bytecode_sha256': hashlib.sha256(art['bytecode'].encode()).hexdigest(),
            'mobi_compiler': None}
    try:
        with open(os.path.join(os.path.dirname(path), 'MOBIVIDRegistryV2.dbg.json')) as f:
            bi_path = os.path.normpath(os.path.join(os.path.dirname(path), json.load(f)['buildInfo']))
        with open(bi_path) as f:
            bi = json.load(f)
        st = bi['input']['settings']
        info['mobi_compiler'] = (f"solc {bi.get('solcLongVersion')}, optimizer {st.get('optimizer')}, "
                                 f"evmVersion {st.get('evmVersion')}, viaIR {bool(st.get('viaIR'))}")
    except Exception:
        pass
    return info, art


def deploy_v2(rpc_url: str, art: Dict[str, Any]):
    from eth_account import Account
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    a = Account.from_key("0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
    tx = w3.eth.contract(abi=art['abi'], bytecode=art['bytecode']).constructor().build_transaction({
        'from': a.address, 'nonce': w3.eth.get_transaction_count(a.address), 'gas': 8_000_000,
        'gasPrice': w3.eth.gas_price})
    signed = a.sign_transaction(tx)
    raw = getattr(signed, 'raw_transaction', None) or signed.rawTransaction
    r = w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(raw))
    if r.status != 1:
        raise RuntimeError("MOBIVIDRegistryV2 deployment reverted")
    return r.contractAddress, int(r.gasUsed)


def run_backend(adapter, rpc: Optional[H.RPCCounter], n: int, warmup: int, run_tag: str) -> Dict[str, Any]:
    b = H.Backend(adapter.name, adapter, adapter.is_chain, rpc)
    chain = adapter.is_chain
    total = n + warmup
    res: Dict[str, Dict[str, Any]] = {}
    print(f"\n=== {adapter.name} ===")

    def record(op, samples):
        s = H.summarize(samples)
        s['samples_ms'] = [round(x.elapsed_ms, 4) for x in samples]
        s.pop('gas_samples', None)
        res[op] = s
        g = f" gas={s['gas_used'] if s['gas_used'] is not None else str(s['gas_min']) + '..' + str(s['gas_max'])}" \
            if s.get('gas_min') is not None else ''
        print(f"  {op:<32} median={s['median_ms']:.4f} p95={s['p95_ms']:.4f} ms rpc={s['rpc_calls_median']}{g}")

    # 1. birth
    vins = [f"M4-{run_tag}-{adapter.name}-BIRTH-{i:04d}" for i in range(total)]

    def check_birth(vin, handle):
        if not handle:
            H._fail("birth returned no handle")
        if chain:
            adapter.last_receipt = adapter.birth_receipt()   # untimed; provider does not expose it
            if adapter.last_receipt.status != 1:
                H._fail("birth reverted")
        return {}
    record('birth', H.measure(b, 'birth', n, warmup, prepare=lambda i: vins[i],
                              run=lambda vin: adapter.birth(vin, 0), check=check_birth, chain_write=chain))

    # 2. lifecycle_event (one vehicle, odometer increasing)
    v_event = adapter.birth(f"M4-{run_tag}-{adapter.name}-EVENTS", 0)

    def check_event(ctx, r):
        if r is None:
            H._fail("lifecycle_event returned None")
        return {}
    record('lifecycle_event', H.measure(
        b, 'lifecycle_event', n, warmup,
        prepare=lambda i: (10_000 + 100 * i, event_payload(10_000 + 100 * i)),
        run=lambda ctx: adapter.lifecycle_event(v_event, ctx[0], ctx[1]),
        check=check_event, chain_write=chain))
    h = adapter.history(v_event)
    if h['event_count'] != total:
        H._fail(f"expected {total} events, history has {h['event_count']}")

    # 3. ownership_transfer (alternating between two owners)
    v_xfer = adapter.birth(f"M4-{run_tag}-{adapter.name}-TRANSFERS", 0)
    state = {'owner': adapter.current_owner(v_xfer)}

    def check_xfer(ctx, r):
        new = adapter.current_owner(v_xfer)          # untimed (eth_call on chain)
        if new == state['owner']:
            H._fail("owner did not change")
        state['owner'] = new
        return {}
    record('ownership_transfer', H.measure(
        b, 'ownership_transfer', n, warmup, prepare=lambda i: 50_000 + 10 * i,
        run=lambda odo: adapter.transfer(v_xfer, odo), check=check_xfer, chain_write=chain))

    # 4. history_query on a vehicle with HISTORY_EVENTS events and HISTORY_TRANSFERS transfers
    v_hist = adapter.birth(f"M4-{run_tag}-{adapter.name}-HISTORY", 0)
    for j in range(HISTORY_EVENTS):
        adapter.lifecycle_event(v_hist, 1_000 * (j + 1), event_payload(1_000 * (j + 1)))
    for j in range(HISTORY_TRANSFERS):
        adapter.transfer(v_hist, 20_000 + j)

    def check_hist(ctx, r):
        if r.get('event_count') != HISTORY_EVENTS or r.get('transfer_count') != HISTORY_TRANSFERS:
            H._fail(f"history shape wrong: {r.get('event_count')} events, {r.get('transfer_count')} transfers")
        return {}
    record('history_query', H.measure(b, 'history_query', n, warmup, prepare=lambda i: v_hist,
                                      run=adapter.history, check=check_hist))
    if chain:
        adapter.refresh_history_cache(v_hist)          # untimed: the "once cached" condition
        record('history_query_cached', H.measure(b, 'history_query_cached', n, warmup, prepare=lambda i: v_hist,
                                                 run=adapter.history_cached, check=check_hist))
        record('history_query_cached_validated', H.measure(
            b, 'history_query_cached_validated', n, warmup, prepare=lambda i: v_hist,
            run=adapter.history_cached_validated, check=check_hist))
        if adapter.history_cached(v_hist) != adapter.history(v_hist):
            H._fail("cached history differs from the chain history")
    else:
        # POST-HOC DIAGNOSTIC (added after a discarded n=30 development run showed the
        # cached MOBI history far below the centralized one): the centralized history
        # without dataclasses.asdict serialisation. No verdict attaches to it.
        record('history_query_unserialised_diagnostic', H.measure(
            b, 'history_query_unserialised_diagnostic', n, warmup, prepare=lambda i: v_hist,
            run=adapter.history_unserialised, check=check_hist))
    return res


def verdicts(central: Dict[str, Any], mobi: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for op in ('birth', 'lifecycle_event', 'ownership_transfer'):
        r = mobi[op]['median_ms'] / central[op]['median_ms']
        r95 = mobi[op]['p95_ms'] / central[op]['p95_ms']
        out.append({'operation': op, 'claim': 'centralized >= 10x faster (median)',
                    'mobi_median_ms': mobi[op]['median_ms'], 'central_median_ms': central[op]['median_ms'],
                    'ratio_median': r, 'ratio_p95': r95,
                    'verdict': 'PASS' if r >= WRITE_SPEEDUP_THRESHOLD else 'FAIL'})
    c = central['history_query']
    for op, pre in (('history_query_cached', True), ('history_query', False), ('history_query_cached_validated', False)):
        r = mobi[op]['median_ms'] / c['median_ms']
        r95 = mobi[op]['p95_ms'] / c['p95_ms']
        within = EQUAL_BAND[0] <= r <= EQUAL_BAND[1]
        out.append({'operation': op, 'claim': ('equal once cached (median ratio in [0.5, 2.0])' if pre
                                               else 'reported, no pre-registered verdict'),
                    'mobi_median_ms': mobi[op]['median_ms'], 'central_median_ms': c['median_ms'],
                    'ratio_median': r, 'ratio_p95': r95,
                    'verdict': ('PASS' if within else 'FAIL') if pre else ('(within band)' if within else '(outside band)')})
    d = central.get('history_query_unserialised_diagnostic')
    if d:
        r = mobi['history_query_cached']['median_ms'] / d['median_ms']
        within = EQUAL_BAND[0] <= r <= EQUAL_BAND[1]
        out.append({'operation': 'history_query_cached vs centralized unserialised (post-hoc diagnostic)',
                    'claim': 'post-hoc diagnostic, no verdict',
                    'mobi_median_ms': mobi['history_query_cached']['median_ms'], 'central_median_ms': d['median_ms'],
                    'ratio_median': r, 'ratio_p95': mobi['history_query_cached']['p95_ms'] / d['p95_ms'],
                    'verdict': '(within band)' if within else '(outside band)'})
    return out


CSV_COLUMNS = ['backend', 'operation', 'n', 'median_ms', 'p95_ms', 'mean_ms', 'min_ms', 'max_ms', 'stdev_ms',
               'gas_used', 'gas_median', 'gas_min', 'gas_max', 'rpc_calls_median']


def fmt(x, d=3):
    if x is None:
        return '-'
    return f"{x:.{d}f}" if isinstance(x, float) else str(x)


def write_md(path, env, cfg, rows, ver):
    L = ["# M4 lifecycle parity: centralized vehicle registry vs MOBI-VID-V2\n",
         "Generated by `scripts/experiment_lifecycle_parity.py` (sibling of `experiment_pki_vs_erc1056.py`, "
         "reusing its harness). Pre-registered in `docs/PLAN_MOBI_SUMO.md` §A.2; single full run, no stopping "
         f"rule. n = {cfg['n']} per operation after {cfg['warmup']} discarded warm-ups, `time.perf_counter_ns`; "
         "gas is the receipt `gasUsed`.\n",
         "## Environment\n", "| Item | Value |", "|---|---|"]
    for k in ('date_utc', 'git_commit', 'git_dirty', 'python_version', 'node_version', 'hardhat_version',
              'web3_version', 'cryptography_version', 'chain_id', 'automine', 'mining_mode', 'rpc_url',
              'contract_address', 'contract_deploy_gas', 'mobi_artifact', 'mobi_bytecode_sha256', 'mobi_compiler',
              'cpu_model', 'cpu_count', 'os'):
        L.append(f"| {k} | {env.get(k)} |")
    L.append("")
    L.append("## Pre-registered hypothesis and verdicts\n")
    L.append("> the centralized registry is ≥10× faster than MOBI-VID-V2 for birth and lifecycle writes (local), "
             "equal for history queries once the chain history is cached (PLAN_MOBI_SUMO.md §A.2)\n")
    L.append(f"Operationalisation fixed in the script before the run: ≥10× = median ratio ≥ "
             f"{WRITE_SPEEDUP_THRESHOLD:g} per write (lifecycle writes = lifecycle event and ownership transfer, "
             f"judged separately); equal = median ratio in [{EQUAL_BAND[0]}, {EQUAL_BAND[1]}], with \"cached\" = "
             "MOBI history served from a local copy of the chain history.\n")
    L.append("| Operation | Claim | MOBI median (ms) | centralized median (ms) | ratio MOBI / central (median) | "
             "ratio (p95) | Verdict |")
    L.append("|---|---|---:|---:|---:|---:|:---:|")
    for v in ver:
        L.append(f"| {v['operation']} | {v['claim']} | {fmt(v['mobi_median_ms'])} | {fmt(v['central_median_ms'], 4)} | "
                 f"{v['ratio_median']:.3g}× | {v['ratio_p95']:.3g}× | **{v['verdict']}** |")
    L.append("")
    L.append("## Results (ms; gas in units)\n")
    L.append("| Backend | Operation | n | median | p95 | mean | min | max | gas (receipt) | RPC calls/op |")
    L.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        gas = r['gas_used'] if r.get('gas_used') is not None else (
            f"{r['gas_median']} ({r['gas_min']}..{r['gas_max']})" if r.get('gas_min') is not None else '-')
        rpc = int(r['rpc_calls_median']) if r['backend'] == 'mobi_vid_v2' else '-'
        d = 4 if r['backend'] == 'centralized_registry' else 3
        L.append(f"| {r['backend']} | {r['operation']} | {r['n']} | {fmt(r['median_ms'], d)} | {fmt(r['p95_ms'], d)} | "
                 f"{fmt(r['mean_ms'], d)} | {fmt(r['min_ms'], d)} | {fmt(r['max_ms'], d)} | {gas} | {rpc} |")
    L.append("")
    L.append(f"MOBIVIDRegistryV2 deploy gas: {env.get('contract_deploy_gas')}. Setup (untimed, not in the table): "
             "fund the service-centre and two owner accounts, `authorizeIssuer(serviceCentre, SERVICE_CENTER)`.\n")
    L.append("## What each operation does\n")
    L.append("| Operation | centralized_registry (in-process Python dicts) | mobi_vid_v2 (MOBIVIDRegistryV2 via local RPC) |")
    L.append("|---|---|---|")
    L.append("| birth | `register_vehicle_birth`: authorisation check, plain-VIN index, birth record | "
             "`MOBIVIDProvider.register_vehicle_birth`: salted VIN hash, HKDF + AES-256-GCM VIN encryption, "
             "birth-certificate hash, `registerVehicleBirth` tx (manufacturer account), receipt awaited; "
             "the provider also generates a secp256k1 key pair |")
    L.append("| lifecycle_event | `record_lifecycle_event` (role check, append) | SHA-256 data and credential hashes, "
             "`recordLifecycleEvent` tx by the authorised service centre, receipt awaited |")
    L.append("| ownership_transfer | `transfer_ownership` (append, set owner) | `transferVehicleOwnership` tx signed "
             "by the current owner, receipt awaited |")
    L.append(f"| history_query | `get_vehicle_history` ({HISTORY_EVENTS} events, {HISTORY_TRANSFERS} transfers, "
             "serialised to dicts) | uncached: `getVehicleInfo` + `getVehicleEvents` + "
             f"{HISTORY_EVENTS}× `getEvent` + `getOwnershipHistory` (eth_calls), rendered to the same dict shape; "
             "cached: the same rendering from a local copy; cached + validated: `vehicleEventCount` + "
             "`getOwnershipHistoryCount` first |")
    L.append("")
    L.append("## Threats to validity\n")
    L.append("1. **Pre-registered threat: the centralized registry is in-process** (Python dicts, no database, no "
             "network, no authentication of the caller). Its figures are a *lower bound* on a deployed "
             "centralized registry (a REST call to a database is typically 1–10+ ms), so every ratio above is an "
             "*upper bound* on the real advantage of a centralized registry.")
    L.append("2. **Hardhat local (M1), automine.** A MOBI write here is sign + send + one mined block + receipt on "
             "localhost; on a public chain a write waits one block interval or more (seconds), which would "
             "make the write ratios larger, not smaller.")
    L.append("3. **Work is not identical.** MOBI birth also encrypts the VIN and hashes the birth certificate "
             "(privacy the centralized baseline does not provide: it stores the plain VIN) and generates a key "
             "pair; MOBI lifecycle events store hashes, not the event body. The comparison is of the two "
             "implementations as shipped.")
    L.append("4. **\"Cached\" is a condition, not a mechanism of the provider.** The cached MOBI history is the "
             "rendering of a local copy of data previously read from the chain; it does not detect later "
             "changes. The validated variant shows the cost of detecting them (2 eth_calls).")
    L.append("5. **Centralized event IDs** are `sha256(vehicle, type, int(time.time()))[:16]`, so two events of one "
             "type on one vehicle within a second share an ID (the baseline does not enforce uniqueness). The "
             "timing is unaffected; noted as a defect of the baseline.")
    L.append("6. **Single machine, serial, one run** (pre-registered: no stopping rule). Development runs of the "
             "script (n = 30, written to a scratch directory, not committed) preceded this run; the "
             "operationalisation constants were fixed before them and were not changed. One post-hoc *diagnostic* "
             "row (centralized history without `dataclasses.asdict`) was added after a development run showed "
             "the cached MOBI history far *below* the centralized one; it carries no verdict and changes none.")
    L.append("")
    with open(path, 'w') as f:
        f.write("\n".join(L))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--n', type=int, default=50)
    ap.add_argument('--warmup', type=int, default=3)
    ap.add_argument('--rpc-url', default='http://127.0.0.1:8545')
    ap.add_argument('--contract-address', default=None, help='existing MOBIVIDRegistryV2 (else --deploy)')
    ap.add_argument('--deploy', action='store_true', help='deploy MOBIVIDRegistryV2 from the tracked artifact')
    ap.add_argument('--artifact', default=V2_ARTIFACT)
    ap.add_argument('--out-dir', default=os.path.join(ROOT, 'results'))
    ap.add_argument('--out-name', default='lifecycle_parity')
    args = ap.parse_args()
    if args.n < 30:
        ap.error('--n must be >= 30')

    info, art = artifact_info(args.artifact)
    deploy_gas = None
    address = args.contract_address
    if args.deploy:
        address, deploy_gas = deploy_v2(args.rpc_url, art)
    if address is None:
        ap.error('--deploy or --contract-address is required')

    run_tag = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    mobi = MOBIVIDV2LifecycleBackend(args.rpc_url, address, art['abi'], seed=f"m4-{run_tag}")
    w3 = mobi.w3
    try:
        automine = w3.provider.make_request('hardhat_getAutomine', []).get('result')
    except Exception:
        automine = None
    chain_info = {'rpc_url': args.rpc_url, 'chain_id': int(w3.eth.chain_id),
                  'block_gas_limit': int(w3.eth.get_block('latest')['gasLimit']), 'automine': automine,
                  'mining_mode': 'automine (no interval mining)' if automine else 'unknown/interval',
                  'contract_address': address, 'contract_deploy_gas': deploy_gas,
                  'client_version': w3.client_version, **info}
    env = H.environment(chain_info, args.n, args.warmup)
    print("Environment:", json.dumps(env, indent=2, default=str))

    central = CentralizedLifecycleBackend()
    results = {
        'centralized_registry': run_backend(central, None, args.n, args.warmup, run_tag),
        'mobi_vid_v2': run_backend(mobi, H.RPCCounter(w3), args.n, args.warmup, run_tag),
    }
    rows = []
    for backend, ops in results.items():
        for op, _, _ in OPERATIONS:
            if op in ops:
                rows.append({'backend': backend, 'operation': op, **ops[op]})
    ver = verdicts(results['centralized_registry'], results['mobi_vid_v2'])
    for v in ver:
        print(f"  {v['operation']:<32} ratio {v['ratio_median']:.3g}x  -> {v['verdict']}")

    cfg = {'n': args.n, 'warmup': args.warmup, 'run_tag': run_tag,
           'history_events': HISTORY_EVENTS, 'history_transfers': HISTORY_TRANSFERS,
           'write_speedup_threshold': WRITE_SPEEDUP_THRESHOLD, 'equal_band': list(EQUAL_BAND),
           'operations': [{'name': o, 'description': d, 'kind': k} for o, d, k in OPERATIONS],
           'preregistration': 'docs/PLAN_MOBI_SUMO.md §A.2 (M4)'}
    os.makedirs(args.out_dir, exist_ok=True)
    base = os.path.join(args.out_dir, args.out_name)
    with open(base + '.json', 'w') as f:
        json.dump({'environment': env, 'config': cfg, 'results': rows, 'verdicts': ver}, f, indent=2, default=str)
    with open(base + '.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            out = {c: r.get(c) for c in CSV_COLUMNS}
            for c in out:
                if isinstance(out[c], float):
                    out[c] = f"{out[c]:.4f}" if c != 'rpc_calls_median' else out[c]
            w.writerow(out)
    write_md(base + '.md', env, cfg, rows, ver)
    print(f"\nWrote {base}.{{json,csv,md}}")


if __name__ == '__main__':
    main()
