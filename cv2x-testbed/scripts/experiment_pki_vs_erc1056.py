#!/usr/bin/env python3
"""
PKI vs ERC-1056 identity experiment (thesis hypothesis: ERC-1056 identity is a
viable alternative to centralized PKI for connected vehicles).

Runs an IDENTICAL operation set through every identity backend that exposes the
IdentityProvider interface (identity/base.py), timing each operation with
time.perf_counter_ns and, for on-chain operations, recording the exact gasUsed
from the transaction receipt and the number of JSON-RPC round trips.

Backends
  pki_standard     identity/standard/pki_identity.py (VehiclePKIIdentity + VehiclePKI_CA)
                   wrapped by a thin adapter (no identity logic of its own)
  pki_centralized  identity/centralized_provider.py (CentralizedIdentityProvider)
  erc1056_did      identity/erc1056_provider.py (ERC1056Provider) against a
                   deployed ERC1056Registry on a local Hardhat node

Operation set (same order, same inputs, same checks for every backend)
  register_identity   create identity + issue its initial credential
  issue_credential    bind a new verification key to an existing identity
  sign_message        sign a BSM-like message
  verify_message      verify a peer's signed message (the V2X hot path)
  resolve_identity    look up identity -> public key
  check_revocation    query revocation status of a live identity
  revoke_credential   revoke a (freshly registered) identity

Outputs (cv2x-testbed/results/)
  pki_vs_erc1056.csv   one row per backend x operation (summary statistics)
  pki_vs_erc1056.json  environment header, config, per-row raw samples, sanity checks
  pki_vs_erc1056.md    results table + caveats

Usage
  # start chain + deploy first (optional; without it only the PKI backends run):
  #   npx hardhat node &
  #   npx hardhat run scripts/deploy.js --network localhost
  python3 scripts/experiment_pki_vs_erc1056.py [--n 50] [--warmup 3] [--no-chain]
"""

import argparse
import csv
import json
import os
import platform
import re
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from identity.standard.pki_identity import VehiclePKIIdentity, VehiclePKI_CA  # noqa: E402
from identity.centralized_provider import CentralizedIdentityProvider  # noqa: E402

PSEUDONYM_POOL = 20          # pseudonym certificates issued at PKI registration (provider default)
FUND_WEI = 10 ** 18          # 1 ETH per vehicle account (local chain provisioning, untimed)
VEHICLE_METADATA = {"make": "Testbed", "model": "BSM-Vehicle"}


# --------------------------------------------------------------------------
# Standard-PKI adapter: maps identity/standard/pki_identity.py onto the
# IdentityProvider method names. It only forwards calls.
# --------------------------------------------------------------------------
class StandardPKIAdapter:
    """VehiclePKIIdentity/VehiclePKI_CA exposed with IdentityProvider method names."""

    def __init__(self, ca_name: str = "CVIN-Standard-CA"):
        self.ca = VehiclePKI_CA(ca_name)
        self.vehicles: Dict[str, VehiclePKIIdentity] = {}
        # Any vehicle can act as verifier; verify_message() uses no per-vehicle state.
        self.peer = VehiclePKIIdentity("PEER-VERIFIER")

    def register_vehicle(self, vehicle_id: str, metadata: Dict = None):
        v = VehiclePKIIdentity(vehicle_id)
        v.generate_keypair()
        v.request_enrollment_certificate(self.ca)
        v.request_pseudonym_certificates(self.ca, count=PSEUDONYM_POOL)
        self.vehicles[vehicle_id] = v
        return v.long_term_certificate

    def update_credential(self, vehicle_id: str, updates: Dict) -> bool:
        v = self.vehicles[vehicle_id]
        if updates.get('rotate_key'):
            existing = v.pseudonym_certificates
            issued = v.request_pseudonym_certificates(self.ca, count=1)  # CA issues one cert
            v.pseudonym_certificates = existing + issued                 # keep the pool
        return True

    def sign_message(self, vehicle_id: str, message: Dict) -> Dict:
        return self.vehicles[vehicle_id].sign_message(message)

    def verify_message(self, signed_message: Dict):
        # The verifier's CRL copy is the CA's live revocation set (no copy per call).
        return self.peer.verify_message(signed_message, self.ca.certificate_revocation_list)

    def revoke_credential(self, vehicle_id: str, reason: str = "") -> bool:
        v = self.vehicles[vehicle_id]
        self.ca.revoke_certificate(v.long_term_certificate.serial_number)
        for p in v.pseudonym_certificates:
            self.ca.revoke_certificate(p['certificate'].serial_number)
        return True

    def check_revocation_status(self, vehicle_id: str):
        serial = self.vehicles[vehicle_id].long_term_certificate.serial_number
        return serial in self.ca.certificate_revocation_list, 0.0

    def resolve_identity(self, vehicle_id: str):
        serial = self.vehicles[vehicle_id].long_term_certificate.serial_number
        cert = self.ca.issued_certificates.get(serial)
        if cert is None:
            return None, 0.0
        return {'vehicle_id': vehicle_id, 'public_key': cert.public_key(),
                'serial': serial, 'issuer': self.ca.name}, 0.0


# --------------------------------------------------------------------------
# Measurement helpers
# --------------------------------------------------------------------------
class RPCCounter:
    """Counts JSON-RPC requests made through a web3 HTTP provider."""

    def __init__(self, w3):
        self.count = 0
        self.methods: List[str] = []
        self._orig = w3.provider.make_request
        w3.provider.make_request = self._wrapped
        # web3 caches the middleware-wrapped request function on first use;
        # drop it so the cache is rebuilt around the counting wrapper.
        if hasattr(w3.provider, '_request_func_cache'):
            w3.provider._request_func_cache = (None, None)

    def _wrapped(self, method, params):
        self.count += 1
        self.methods.append(str(method))
        return self._orig(method, params)

    def reset(self):
        self.count = 0
        self.methods = []


@dataclass
class Sample:
    elapsed_ms: float
    gas_used: Optional[int] = None
    rpc_calls: int = 0
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Backend:
    name: str
    provider: Any
    is_chain: bool
    rpc: Optional[RPCCounter] = None

    def fund(self, vehicle_ids: List[str]):
        if self.is_chain:
            for vid in vehicle_ids:
                self.provider.fund_vehicle_account(vid, FUND_WEI)


def make_bsm(i: int) -> Dict:
    """SAE J2735-like Basic Safety Message payload (distinct per repetition)."""
    return {
        'msgID': 'BasicSafetyMessage',
        'msgCnt': i % 128,
        'secMark': (i * 100) % 60000,
        'position': {'lat': 49.2827, 'long': -123.1207, 'elev': 70},
        'speed': 13.9,
        'heading': 90.0,
        'accel': {'long': 0.2, 'lat': 0.0, 'vert': 0.0, 'yaw': 0.0},
        'brakes': 'unavailable',
        'size': {'width': 180, 'length': 450},
    }


def measure(backend: Backend, op: str, n: int, warmup: int,
            prepare: Callable[[int], Any],
            run: Callable[[Any], Any],
            check: Callable[[Any, Any], Dict[str, Any]],
            chain_write: bool = False) -> List[Sample]:
    """
    Executes warmup + n repetitions. prepare(i) is untimed; run(ctx) is timed with
    perf_counter_ns; check(ctx, result) raises on a wrong result and may return
    extra per-sample data. Only the last n repetitions are kept.
    """
    samples: List[Sample] = []
    prov = backend.provider
    for i in range(warmup + n):
        ctx = prepare(i)
        if backend.rpc is not None:
            backend.rpc.reset()
        if backend.is_chain:
            prov.last_receipt = None

        t0 = time.perf_counter_ns()
        result = run(ctx)
        t1 = time.perf_counter_ns()

        extra = check(ctx, result) or {}
        gas = None
        if chain_write:
            receipt = prov.last_receipt
            if receipt is None:
                raise RuntimeError(f"{backend.name}/{op}: no receipt captured for chain write")
            gas = int(receipt.gasUsed)
        rpc_calls = backend.rpc.count if backend.rpc is not None else 0
        if backend.rpc is not None and i == warmup:
            extra['rpc_methods'] = list(backend.rpc.methods)
        if i >= warmup:
            samples.append(Sample((t1 - t0) / 1e6, gas, rpc_calls, extra))
    return samples


def summarize(samples: List[Sample]) -> Dict[str, Any]:
    xs = [s.elapsed_ms for s in samples]
    arr = np.array(xs, dtype=float)
    out = {
        'n': len(xs),
        'mean_ms': float(arr.mean()),
        'median_ms': float(np.median(arr)),
        'p95_ms': float(np.percentile(arr, 95)),   # numpy 'linear' interpolation
        'min_ms': float(arr.min()),
        'max_ms': float(arr.max()),
        'stdev_ms': float(statistics.stdev(xs)) if len(xs) > 1 else 0.0,
    }
    gas = [s.gas_used for s in samples if s.gas_used is not None]
    if gas:
        out['gas_used'] = gas[0] if min(gas) == max(gas) else None  # single exact value if constant
        out['gas_min'] = min(gas)
        out['gas_max'] = max(gas)
        out['gas_median'] = int(np.median(gas))
        out['gas_samples'] = gas
    else:
        out['gas_used'] = None
        out['gas_min'] = None
        out['gas_max'] = None
        out['gas_median'] = None
    rpc = [s.rpc_calls for s in samples]
    out['rpc_calls_median'] = float(np.median(rpc)) if rpc else 0.0
    for s in samples:
        if 'rpc_methods' in s.extra:
            out['rpc_methods'] = s.extra['rpc_methods']
            break
    sizes = [s.extra['signed_message_bytes'] for s in samples if 'signed_message_bytes' in s.extra]
    if sizes:
        out['signed_message_bytes_median'] = float(np.median(sizes))
    res = [s.extra['resolution_ms'] for s in samples if 'resolution_ms' in s.extra]
    if res:
        out['resolution_ms_median'] = float(np.median(res))
    return out


# --------------------------------------------------------------------------
# The identical operation set
# --------------------------------------------------------------------------
OPERATIONS = [
    ('register_identity', 'create identity and issue its initial credential'),
    ('issue_credential', 'bind a new verification key to an existing identity'),
    ('sign_message', 'sign a BSM-like message'),
    ('verify_message', 'verify a signed message from a peer (hot path)'),
    ('resolve_identity', 'look up identity -> public key'),
    ('check_revocation', 'query revocation status of a live identity'),
    ('revoke_credential', 'revoke a freshly registered identity'),
]


def run_backend(backend: Backend, n: int, warmup: int, run_tag: str) -> Dict[str, Any]:
    prov = backend.provider
    # Vehicle ids carry a per-run tag: the ERC-1056 vehicle address is derived
    # deterministically from the id, and the registry on a long-running node
    # remembers revoked identities across runs.
    name = f"{backend.name}_{run_tag}"
    total = warmup + n
    print(f"\n=== {backend.name} (n={n}, warmup={warmup}, run_tag={run_tag}) ===")

    v_sign = f"{name}_SIGNER"
    v_issue = f"{name}_ISSUER"
    backend.fund([v_sign, v_issue])
    prov.register_vehicle(v_sign, VEHICLE_METADATA)
    prov.register_vehicle(v_issue, VEHICLE_METADATA)

    results: Dict[str, Dict[str, Any]] = {}

    def record(op, samples, chain_round_trip):
        s = summarize(samples)
        s['chain_round_trip'] = chain_round_trip
        s['samples_ms'] = [round(x.elapsed_ms, 4) for x in samples]
        results[op] = s
        gas = f" gas={s['gas_used']}" if s['gas_used'] is not None else (
            f" gas={s['gas_min']}..{s['gas_max']}" if s['gas_min'] is not None else "")
        print(f"  {op:<18} median={s['median_ms']:.3f} ms  p95={s['p95_ms']:.3f} ms{gas}")

    # 1. register_identity
    reg_ids = [f"{name}_REG_{i}" for i in range(total)]
    backend.fund(reg_ids)
    record('register_identity', measure(
        backend, 'register_identity', n, warmup,
        prepare=lambda i: reg_ids[i],
        run=lambda vid: prov.register_vehicle(vid, VEHICLE_METADATA),
        check=lambda vid, r: {} if r is not None else _fail("register returned None"),
        chain_write=backend.is_chain), backend.is_chain)

    # 2. issue_credential
    record('issue_credential', measure(
        backend, 'issue_credential', n, warmup,
        prepare=lambda i: v_issue,
        run=lambda vid: prov.update_credential(vid, {'rotate_key': True}),
        check=lambda vid, r: {} if r is True else _fail("issue_credential returned False"),
        chain_write=backend.is_chain), backend.is_chain)

    # 3. sign_message
    def check_sign(ctx, r):
        if not r or 'signature' not in r:
            _fail("sign returned no signature")
        return {'signed_message_bytes': len(json.dumps(r).encode())}
    record('sign_message', measure(
        backend, 'sign_message', n, warmup,
        prepare=lambda i: make_bsm(i),
        run=lambda bsm: prov.sign_message(v_sign, bsm),
        check=check_sign), False)

    # 4. verify_message (hot path)
    def check_verify(ctx, r):
        ok = r[0]
        if ok is not True:
            _fail("verify_message returned False for a genuine message")
        extra = {}
        m = r[1]
        if backend.is_chain and hasattr(m, 'resolution_time_ms'):
            extra['resolution_ms'] = float(m.resolution_time_ms)  # provider-internal DID resolution share
        return extra
    record('verify_message', measure(
        backend, 'verify_message', n, warmup,
        prepare=lambda i: prov.sign_message(v_sign, make_bsm(1000 + i)),
        run=lambda signed: prov.verify_message(signed),
        check=check_verify), backend.is_chain)

    # 5. resolve_identity
    def check_resolve(ctx, r):
        data = r[0]
        if not data or not data.get('public_key'):
            _fail("resolve_identity returned no public key")
        return {}
    record('resolve_identity', measure(
        backend, 'resolve_identity', n, warmup,
        prepare=lambda i: v_sign,
        run=lambda vid: prov.resolve_identity(vid),
        check=check_resolve), backend.is_chain)

    # 6. check_revocation (live identity -> must be False)
    record('check_revocation', measure(
        backend, 'check_revocation', n, warmup,
        prepare=lambda i: v_sign,
        run=lambda vid: prov.check_revocation_status(vid),
        check=lambda vid, r: {} if r[0] is False else _fail("live identity reported revoked")),
        backend.is_chain)

    # 7. revoke_credential (fresh identity per repetition; post-condition checked untimed)
    def prepare_revoke(i):
        vid = f"{name}_REV_{i}"
        backend.fund([vid])
        prov.register_vehicle(vid, VEHICLE_METADATA)
        return vid

    def check_revoke(vid, r):
        if r is not True:
            _fail("revoke_credential returned False")
        if prov.check_revocation_status(vid)[0] is not True:
            _fail("identity not revoked after revoke_credential")
        return {}
    record('revoke_credential', measure(
        backend, 'revoke_credential', n, warmup,
        prepare=prepare_revoke,
        run=lambda vid: prov.revoke_credential(vid, "experiment"),
        check=check_revoke,
        chain_write=backend.is_chain), backend.is_chain)

    # Untimed sanity checks: revocation is enforced, tampering is detected.
    v_rev = f"{name}_SANITY_REVOKED"
    backend.fund([v_rev])
    prov.register_vehicle(v_rev, VEHICLE_METADATA)
    signed_before = prov.sign_message(v_rev, make_bsm(7))
    prov.revoke_credential(v_rev, "sanity")
    tampered = dict(prov.sign_message(v_sign, make_bsm(8)))
    tampered['message'] = dict(tampered['message'], speed=99.9)
    sanity = {
        'verify_after_revocation_is_false': bool(prov.verify_message(signed_before)[0]) is False,
        'verify_tampered_message_is_false': bool(prov.verify_message(tampered)[0]) is False,
        'verify_genuine_message_is_true': bool(prov.verify_message(prov.sign_message(v_sign, make_bsm(9)))[0]) is True,
    }
    print(f"  sanity: {sanity}")
    return {'operations': results, 'sanity': sanity}


def _fail(msg: str):
    raise AssertionError(msg)


# --------------------------------------------------------------------------
# Environment header
# --------------------------------------------------------------------------
def _sh(cmd: List[str], cwd: str = ROOT) -> Optional[str]:
    try:
        return subprocess.check_output(cmd, cwd=cwd, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return None


def _pkg_version(pkg: str) -> Optional[str]:
    try:
        with open(os.path.join(ROOT, 'node_modules', pkg, 'package.json')) as f:
            return json.load(f).get('version')
    except Exception:
        return None


def cpu_model() -> Optional[str]:
    try:
        with open('/proc/cpuinfo') as f:
            for line in f:
                if line.lower().startswith('model name'):
                    return line.split(':', 1)[1].strip()
    except Exception:
        pass
    return platform.processor() or None


def solc_version() -> Optional[str]:
    try:
        import glob
        files = glob.glob(os.path.join(ROOT, 'artifacts', 'build-info', '*.json'))
        if files:
            with open(files[0]) as f:
                return json.load(f).get('solcLongVersion')
    except Exception:
        pass
    return None


def environment(chain_info: Optional[Dict[str, Any]], n: int, warmup: int) -> Dict[str, Any]:
    import cryptography
    env = {
        'date_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'git_commit': _sh(['git', 'rev-parse', '--short', 'HEAD']),
        'git_dirty': bool(_sh(['git', 'status', '--porcelain'])),
        'python_version': platform.python_version(),
        'node_version': _sh(['node', '--version']),
        'hardhat_version': _pkg_version('hardhat'),
        'ethers_version': _pkg_version('ethers'),
        'solc_version': solc_version(),
        'cryptography_version': cryptography.__version__,
        'os': platform.platform(),
        'cpu_model': cpu_model(),
        'cpu_count': os.cpu_count(),
        'timer': 'time.perf_counter_ns',
        'repetitions_per_op': n,
        'discarded_warmup_runs': warmup,
        'p95_method': 'numpy.percentile(samples, 95), linear interpolation',
    }
    try:
        import web3
        env['web3_version'] = web3.__version__
    except Exception:
        env['web3_version'] = None
    env.update(chain_info or {
        'chain_id': None, 'block_gas_limit': None, 'automine': None,
        'contract_address': None, 'contract_deploy_gas': None, 'rpc_url': None})
    return env


# --------------------------------------------------------------------------
# Output writers
# --------------------------------------------------------------------------
CSV_COLUMNS = ['provider', 'operation', 'chain_round_trip', 'n', 'mean_ms', 'median_ms',
               'p95_ms', 'min_ms', 'max_ms', 'stdev_ms', 'gas_used', 'gas_median', 'gas_min',
               'gas_max', 'rpc_calls_median', 'signed_message_bytes_median', 'resolution_ms_median']


def write_csv(path: str, rows: List[Dict[str, Any]]):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            out = {k: r.get(k) for k in CSV_COLUMNS}
            for k in ('mean_ms', 'median_ms', 'p95_ms', 'min_ms', 'max_ms', 'stdev_ms',
                      'resolution_ms_median'):
                if out.get(k) is not None:
                    out[k] = f"{out[k]:.4f}"
            w.writerow(out)


def fmt(x, digits=3):
    return "-" if x is None else f"{x:.{digits}f}"


def write_md(path: str, env: Dict[str, Any], rows: List[Dict[str, Any]],
             sanity: Dict[str, Dict[str, bool]], skipped: Dict[str, str], n: int, warmup: int):
    backends = []
    for r in rows:
        if r['provider'] not in backends:
            backends.append(r['provider'])
    L = []
    L.append("# PKI vs ERC-1056 identity: identical operation set, measured\n")
    L.append("Generated by `scripts/experiment_pki_vs_erc1056.py`. "
             "Every backend runs the same seven operations with the same inputs and the same "
             f"result checks; each figure is over n={n} warm repetitions after {warmup} discarded "
             "warm-up runs, timed with `time.perf_counter_ns`. Gas is the exact `gasUsed` from the "
             "transaction receipt.\n")
    L.append("## Environment\n")
    L.append("| Item | Value |\n|---|---|")
    for k in ('date_utc', 'git_commit', 'git_dirty', 'python_version', 'node_version', 'hardhat_version',
              'ethers_version', 'web3_version', 'solc_version', 'cryptography_version', 'chain_id',
              'block_gas_limit', 'automine', 'contract_address', 'contract_deploy_gas',
              'cpu_model', 'cpu_count', 'os'):
        L.append(f"| {k} | {env.get(k)} |")
    L.append("")
    if skipped:
        L.append("## Backends not run\n")
        for k, v in skipped.items():
            L.append(f"- **{k}**: {v}")
        L.append("")

    L.append("## Results (milliseconds; gas in units)\n")
    L.append("| Backend | Operation | Chain round trip | n | median | p95 | mean | min | max | gas (receipt) | RPC calls/op |")
    L.append("|---|---|:---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        gas = r['gas_used'] if r['gas_used'] is not None else (
            f"{r['gas_median']} ({r['gas_min']}..{r['gas_max']})" if r['gas_min'] is not None else "-")
        rpc = int(r['rpc_calls_median']) if r['chain_round_trip'] else "-"
        L.append(f"| {r['provider']} | {r['operation']} | {'yes' if r['chain_round_trip'] else 'no'} | "
                 f"{r['n']} | {fmt(r['median_ms'])} | {fmt(r['p95_ms'])} | {fmt(r['mean_ms'])} | "
                 f"{fmt(r['min_ms'])} | {fmt(r['max_ms'])} | {gas} | {rpc} |")
    L.append("")

    # side-by-side median/p95
    L.append("### Side-by-side (median / p95, ms)\n")
    L.append("| Operation | " + " | ".join(backends) + " |")
    L.append("|---|" + "---|" * len(backends))
    for op, _ in OPERATIONS:
        cells = []
        for b in backends:
            r = next((x for x in rows if x['provider'] == b and x['operation'] == op), None)
            cells.append(f"{fmt(r['median_ms'])} / {fmt(r['p95_ms'])}" if r else "-")
        L.append(f"| {op} | " + " | ".join(cells) + " |")
    L.append("")

    sizes = [(r['provider'], r.get('signed_message_bytes_median')) for r in rows
             if r['operation'] == 'sign_message' and r.get('signed_message_bytes_median')]
    if sizes:
        L.append("Signed-message size (JSON bytes, median): " +
                 ", ".join(f"{p}={int(s)}" for p, s in sizes) + ".\n")
    rpc_rows = [r for r in rows if r.get('rpc_methods')]
    if rpc_rows:
        L.append("JSON-RPC methods issued per ERC-1056 operation (first warm run):\n")
        for r in rpc_rows:
            L.append(f"- `{r['operation']}`: {', '.join(r['rpc_methods'])}")
        L.append("")

    L.append("## Sanity checks (untimed, must all be True)\n")
    L.append("| Backend | verify after revocation is False | tampered message rejected | genuine message accepted |")
    L.append("|---|:---:|:---:|:---:|")
    for b, s in sanity.items():
        L.append(f"| {b} | {s['verify_after_revocation_is_false']} | {s['verify_tampered_message_is_false']} | "
                 f"{s['verify_genuine_message_is_true']} |")
    L.append("")

    L.append("## What each operation actually does per backend\n")
    L.append("| Operation | pki_standard / pki_centralized (X.509, ECDSA P-256) | erc1056_did (ERC1056Registry, ECDSA secp256k1) |")
    L.append("|---|---|---|")
    L.append(f"| register_identity | generate P-256 key; CA issues 1 enrollment certificate + {PSEUDONYM_POOL} pseudonym certificates (all in-process) | "
             "generate secp256k1 key; vehicle account sends `registerVehicle(addr, pubkey)` (1 tx, wait for receipt) |")
    L.append("| issue_credential | CA issues 1 additional pseudonym certificate (new key, CA-signed) | "
             "vehicle sends `updateVehicleKey(addr, newPubkey)` (1 tx; emits DIDAttributeChanged) |")
    L.append("| sign_message | ECDSA-SHA256 over canonical JSON with current pseudonym key; message carries the PEM certificate | "
             "ECDSA-SHA256 over canonical JSON with the vehicle key; message carries only the `did:ethr` string |")
    L.append("| verify_message | parse PEM cert, CRL set lookup, validity window, issuer name check, ECDSA verify (no network) | "
             "`getIdentityInfo` (eth_call) + event walk (eth_getLogs) to resolve the key + `isRevoked` (eth_call), then ECDSA verify |")
    L.append("| resolve_identity | in-memory lookup of the enrollment certificate / public key | "
             "`getIdentityInfo` (eth_call) + `previousChange` event walk (eth_getLogs per hop) |")
    L.append("| check_revocation | in-memory CRL/flag lookup | `isRevoked` (eth_call) |")
    L.append(f"| revoke_credential | add enrollment + {PSEUDONYM_POOL} pseudonym serials to the CA's CRL set (in-memory) | "
             "vehicle sends `revokeIdentity(addr)` (1 tx) |")
    L.append("")

    L.append("## Caveats (read before quoting any number)\n")
    L.append("1. **What the PKI baseline is.** Both PKI backends are *in-process* Python implementations "
             "(`cryptography` X.509/ECDSA P-256): the CA, the CRL and the vehicles live in the same "
             "process. There is no CA network round trip for enrollment, no OCSP responder, no CRL "
             "download, no certificate-chain building beyond an issuer-name comparison, and the CRL is a "
             "Python `set` whose size during this run is at most a few hundred serial numbers "
             f"({PSEUDONYM_POOL + 1} per revoked vehicle). Real IEEE 1609.2 / ETSI PKI adds network latency "
             "to enrollment, pseudonym provisioning and CRL/OCSP freshness that this baseline does not model. "
             "The PKI numbers are therefore a *lower bound* on real PKI cost, not a measurement of a deployed PKI.")
    L.append("2. **Hardhat local latency is not public-network latency.** The ERC-1056 chain is a single "
             "Hardhat node on localhost with automine (a transaction is mined the instant it is received). "
             "The chain round-trip figures measure web3.py + HTTP JSON-RPC + Hardhat's EVM on this machine; "
             "compare `check_revocation` (exactly one `eth_call`) to see the per-round-trip floor of this "
             "stack, which is the dominant term in every ERC-1056 read. A production client (Geth/Erigon RPC, "
             "keep-alive connection, or an in-process light client) has a different floor. On a public "
             "or consortium network, write operations (register, issue, revoke) take one block interval or "
             "more (seconds to minutes) plus confirmation depth, and reads depend on the RPC endpoint's "
             "latency. Only the *shape* of the comparison (which operations need a chain round trip and how "
             "many) transfers; the millisecond values do not.")
    verify_row = next((r for r in rows if r['provider'] == 'erc1056_did' and r['operation'] == 'verify_message'), None)
    if verify_row and verify_row.get('rpc_methods'):
        methods = verify_row['rpc_methods']
        redundant = sum(1 for m in methods if m == 'eth_chainId')
        L.append(f"   The RPC call lists above show that web3.py {env.get('web3_version')} issues an "
                 f"`eth_chainId` request around most calls ({redundant} of the {len(methods)} round trips in "
                 "`verify_message`). These are client-side redundancy, not registry work: enabling web3's "
                 "request caching (`w3.provider.cache_allowed_requests = True`) or pinning the chain id "
                 "removes them, leaving 3 registry round trips per uncached verification (2 `eth_call` + "
                 "1 `eth_getLogs`). The provider is measured as shipped, without that tuning.")
    L.append("3. **Gas is deterministic; latency is not.** `gasUsed` depends only on the contract code, the "
             "EVM version and the transaction inputs, so the receipt value is exact and re-running with the "
             "same inputs reproduces it; no confidence interval is needed for gas. The small spread the table "
             "shows within one operation (a `min..max` range, at most a few tens of gas) is *not* measurement "
             "noise: it is EIP-2028 calldata pricing (4 gas per zero byte vs 16 per non-zero byte) applied to "
             "the randomly generated public-key / address bytes of each repetition. Latency, by contrast, "
             "varies with scheduling, GC, RPC and EVM state, hence n repetitions, the median (robust) and "
             "p95 (tail) rather than a single run.")
    L.append("4. **Where the backends are not equivalent.**")
    L.append(f"   - `register_identity` does far more work on the PKI side ({PSEUDONYM_POOL + 1} certificate "
             "issuances, each an ECDSA sign by the CA) than on the ERC-1056 side (one transaction storing one "
             "key). ERC-1056 has no pseudonym pool; adding pseudonymity would require one DID per pseudonym "
             "(one registration each).")
    L.append("   - `verify_message` on the PKI side is self-contained because the certificate travels with the "
             "message; on the ERC-1056 side the message carries only the DID, so the verifier must resolve the "
             "key and revocation status from the registry (3 RPC calls per verification in this provider, no "
             "caching). A production verifier would cache resolved DID documents and re-validate with a single "
             "`changed(identity)` call; that optimisation is not implemented here, so the ERC-1056 verify figure "
             "is the *uncached, worst-case* cost.")
    L.append("   - `revoke_credential` on the PKI side revokes every certificate of the vehicle; on the "
             "ERC-1056 side one flag revokes the identity. Checking revocation is an in-memory lookup vs. an "
             "`eth_call`.")
    L.append("   - `issue_credential` compares a CA-signed pseudonym certificate with an owner-signed on-chain "
             "key attribute: different trust anchors (CA vs. identity owner) doing analogous work (bind a new key).")
    L.append("   - The ERC-1056 write operations are signed by the vehicle's own account "
             "(`ERC1056Registry` is `onlyOwner`); funding that account with ETH is a provisioning step done "
             "before the timer starts and is excluded from the measurements. Signature curves also differ "
             "(P-256 for PKI, secp256k1 for ERC-1056), both with SHA-256.")
    L.append("5. **Provider bugs fixed to make the experiment possible** (see the diff): the ERC-1056 provider "
             "previously returned a placeholder public key (`\"0x04...\"`) from resolution, so its "
             "`verify_message` could never succeed, and it signed `registerVehicle`/`revokeIdentity` with the "
             "deployer account, which the contract rejects (`Only owner can perform this action`). The deploy "
             "script's smoke test had the same bug. These fixes affect correctness, not the measured algorithm.")
    L.append("6. **Single machine, single process, no concurrency.** Throughput under load, RPC contention "
             "and multi-vehicle broadcast scenarios are out of scope here.")
    L.append("")
    with open(path, 'w') as f:
        f.write("\n".join(L))


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--n', type=int, default=50, help='warm repetitions per operation (>= 30)')
    ap.add_argument('--warmup', type=int, default=3, help='discarded warm-up runs per operation')
    ap.add_argument('--rpc-url', default='http://127.0.0.1:8545')
    ap.add_argument('--contract-address', default=None,
                    help='ERC1056Registry address (default: deployments/localhost.json)')
    ap.add_argument('--no-chain', action='store_true', help='skip the ERC-1056 backend')
    ap.add_argument('--out-dir', default=os.path.join(ROOT, 'results'))
    ap.add_argument('--render-only', action='store_true',
                    help='do not measure; re-write the .csv/.md from the existing .json in --out-dir')
    args = ap.parse_args()
    if args.n < 30:
        ap.error('--n must be >= 30')

    if args.render_only:
        json_path = os.path.join(args.out_dir, 'pki_vs_erc1056.json')
        with open(json_path) as f:
            saved = json.load(f)
        write_csv(os.path.join(args.out_dir, 'pki_vs_erc1056.csv'), saved['results'])
        write_md(os.path.join(args.out_dir, 'pki_vs_erc1056.md'), saved['environment'], saved['results'],
                 saved['sanity'], saved.get('backends_skipped', {}),
                 saved['config']['n'], saved['config']['warmup'])
        print(f"Re-rendered .csv/.md from {json_path}")
        return

    backends: List[Backend] = [
        Backend('pki_standard', StandardPKIAdapter(), False),
        Backend('pki_centralized', CentralizedIdentityProvider("CVIN-Central-CA"), False),
    ]
    skipped: Dict[str, str] = {}
    chain_info: Optional[Dict[str, Any]] = None

    if args.no_chain:
        skipped['erc1056_did'] = 'skipped by --no-chain'
    else:
        try:
            from identity.erc1056_provider import ERC1056Provider
            address = args.contract_address
            deploy_gas = None
            if address is None:
                with open(os.path.join(ROOT, 'deployments', 'localhost.json')) as f:
                    dep = json.load(f)
                address = dep['contractAddress']
                deploy_gas = int(dep.get('gasUsed')) if dep.get('gasUsed') else None
            erc = ERC1056Provider(args.rpc_url, contract_address=address)
            w3 = erc.w3
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
            backends.append(Backend('erc1056_did', erc, True, RPCCounter(w3)))
        except Exception as e:  # never fabricate: record precisely why the chain backend is absent
            skipped['erc1056_did'] = f'not run: {type(e).__name__}: {e}'
            print(f"WARNING: ERC-1056 backend not run: {e}")

    env = environment(chain_info, args.n, args.warmup)
    print("Environment:", json.dumps(env, indent=2))

    run_tag = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    rows: List[Dict[str, Any]] = []
    sanity: Dict[str, Dict[str, bool]] = {}
    per_backend: Dict[str, Any] = {}
    for b in backends:
        out = run_backend(b, args.n, args.warmup, run_tag)
        per_backend[b.name] = out
        sanity[b.name] = out['sanity']
        for op, _ in OPERATIONS:
            r = dict(out['operations'][op])
            r['provider'] = b.name
            r['operation'] = op
            rows.append(r)

    os.makedirs(args.out_dir, exist_ok=True)
    csv_path = os.path.join(args.out_dir, 'pki_vs_erc1056.csv')
    json_path = os.path.join(args.out_dir, 'pki_vs_erc1056.json')
    md_path = os.path.join(args.out_dir, 'pki_vs_erc1056.md')

    write_csv(csv_path, rows)
    with open(json_path, 'w') as f:
        json.dump({
            'environment': env,
            'config': {'n': args.n, 'warmup': args.warmup, 'pseudonym_pool': PSEUDONYM_POOL,
                       'vehicle_funding_wei': FUND_WEI, 'run_tag': run_tag,
                       'operations': [{'name': o, 'description': d} for o, d in OPERATIONS]},
            'backends_skipped': skipped,
            'results': rows,
            'sanity': sanity,
        }, f, indent=2, default=str)
    write_md(md_path, env, rows, sanity, skipped, args.n, args.warmup)

    print(f"\nWrote:\n  {csv_path}\n  {json_path}\n  {md_path}")
    failed = [b for b, s in sanity.items() if not all(s.values())]
    if failed:
        print(f"SANITY FAILURES: {failed}")
        sys.exit(2)


if __name__ == '__main__':
    main()
