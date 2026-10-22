#!/usr/bin/env python3
"""
Lifecycle-parity experiment: centralized vehicle registry vs MOBI VID V2 registry
(plan docs/PLAN_MOBI_SUMO.md step M4; scope entry SC-13).

The VID II design asked for a "fair comparison" between the MOBI VID blockchain
registry and a centralized vehicle registry with feature parity. This script runs
an IDENTICAL operation set, with the same inputs and the same result checks,
through both backends and reports latency (perf_counter_ns), exact gasUsed from
the receipt and JSON-RPC round trips per operation for the chain side.

Backends
  centralized_registry  identity/centralized_vehicle_registry.py (CentralizedVehicleRegistry,
                        in-process, in-memory "database")
  mobi_vid_v2           identity/mobi_vid_provider.py (MOBIVIDProvider) for VID I birth
                        registration + a thin adapter (below) for the VID II functions of
                        contracts/MOBIVIDRegistryV2.sol on a local Hardhat node

Operation set (same order, same inputs, same checks for both backends)
  register_birth          manufacturer registers a vehicle birth certificate
  record_lifecycle_event  authorised service centre records one MAINTENANCE event with an
                          odometer reading
  attest_event            a second authorised party (dealer) attests that event
                          (MOBI VID II only: the centralized registry has no equivalent;
                          recorded as not-equivalent, never substituted)
  transfer_ownership      current owner transfers the vehicle to a new owner (with odometer)
  query_history           full history for one vehicle (birth + events + attestations +
                          ownership transfers + current owner)

Write operations use a FRESH vehicle per repetition (one-shot per vehicle: first event /
first transfer on that vehicle). query_history repeats on one vehicle that holds the full
history. prepare() steps (registering the fresh vehicle, recording the event to attest)
are untimed.

Measurement helpers (measure, summarize, environment, RPCCounter, Backend) are imported
from experiment_pki_vs_erc1056.py so the two experiments report identically.

Outputs (cv2x-testbed/results/)
  lifecycle_parity.csv   one row per backend x operation (summary statistics)
  lifecycle_parity.json  environment header, config, per-row raw samples, sanity checks
  lifecycle_parity.md    results table, non-equivalences, caveats

Usage
  # start chain + deploy first (optional; without it only the centralized backend runs):
  #   npx hardhat node [--port 8547] &
  #   MOBI_VID_CONTRACT=MOBIVIDRegistryV2 npx hardhat run scripts/deploy_mobi_vid.js --network localhost
  python3 scripts/experiment_lifecycle_parity.py [--n 50] [--warmup 3] \
      [--rpc-url http://127.0.0.1:8545] [--deployment-file deployments/mobi_vid_localhost.json]
"""

import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from experiment_pki_vs_erc1056 import (  # noqa: E402
    Backend, RPCCounter, environment, measure, summarize, _fail,
)
from identity.centralized_vehicle_registry import (  # noqa: E402
    CentralizedVehicleRegistry, EventType as CEventType, IssuerRole as CIssuerRole,
)

# --------------------------------------------------------------------------
# Identical inputs for both backends
# --------------------------------------------------------------------------
VEHICLE_SPEC = {'manufacturer': 'Testbed Motors', 'make': 'Testbed', 'model': 'Lifecycle',
                'year': 2026, 'color': 'blue'}
EVENT_DATA = {'service': 'oil_change', 'parts': ['oil_filter', 'engine_oil_5w30'],
              'labour_hours': 0.5, 'cost_cad': 120.0}
ODOMETER_EVENT = 15_000        # km, at the MAINTENANCE event
ODOMETER_TRANSFER = 15_250     # km, at the ownership transfer
SALE_PRICE = 25_000.0          # centralized-only field (the contract has none); fixed input
JURISDICTION = 'BC-CA'
TRANSFER_AUTHORITY = 'BC-ICBC'
CHAIN_EVENT_MAINTENANCE = 0    # MOBIVIDRegistryV2.EventType.MAINTENANCE
CHAIN_ROLE_DEALER = 2          # MOBIVIDRegistryV2.IssuerRole.DEALER
CHAIN_ROLE_SERVICE_CENTER = 3  # MOBIVIDRegistryV2.IssuerRole.SERVICE_CENTER
TX_GAS_LIMIT = 500_000         # fixed gas limit, as in MOBIVIDProvider (no eth_estimateGas round trip)
HARDHAT_MNEMONIC = "test test test test test test test test test test test junk"
V2_ARTIFACT = os.path.join(ROOT, 'artifacts', 'contracts', 'MOBIVIDRegistryV2.sol', 'MOBIVIDRegistryV2.json')

OPERATIONS = [
    ('register_birth', 'manufacturer registers a vehicle birth certificate'),
    ('record_lifecycle_event', 'authorised service centre records one MAINTENANCE event with an odometer reading'),
    ('attest_event', 'a second authorised party (dealer) attests the recorded event'),
    ('transfer_ownership', 'current owner transfers the vehicle to a new owner (odometer recorded)'),
    ('query_history', 'full history of one vehicle: birth, events, attestations, transfers, current owner'),
]


def make_vin(tag: str, kind: str, i: int) -> str:
    # Distinct per backend, run and repetition: the centralized registry rejects duplicate
    # VINs and the MOBI vehicle identity is derived deterministically from the VIN.
    return f"VIN-{tag}-{kind}-{i:04d}"


# --------------------------------------------------------------------------
# Adapter 1: centralized registry (forwards calls; no registry logic of its own)
# --------------------------------------------------------------------------
class CentralizedRegistryAdapter:
    is_chain = False
    supports_attest = False
    attest_note = ("CentralizedVehicleRegistry has no multi-party attestation: an event carries a "
                   "single issuer and a `verified` flag derived from that issuer's role at record "
                   "time; a second party can only record its own separate event. No equivalent "
                   "operation exists, so nothing was measured for it.")

    def __init__(self):
        self.reg = CentralizedVehicleRegistry("Central Vehicle Registry")
        self.manufacturer_id = 'MFR-TESTBED'
        self.service_center_id = 'SVC-TESTBED'
        self.dealer_id = 'DLR-TESTBED'
        self.reg.authorize_issuer(self.manufacturer_id, VEHICLE_SPEC['manufacturer'], CIssuerRole.MANUFACTURER, 'MFR-LIC-1')
        self.reg.authorize_issuer(self.service_center_id, 'Testbed Service Centre', CIssuerRole.SERVICE_CENTER, 'SVC-LIC-1')
        self.reg.authorize_issuer(self.dealer_id, 'Testbed Dealer', CIssuerRole.DEALER, 'DLR-LIC-1')
        self.first_owner = 'OWNER-A'
        self.new_owner = 'OWNER-B'
        self.last_receipt = None

    def register_birth(self, vin: str) -> Dict[str, Any]:
        cert = self.reg.register_vehicle_birth(
            vin=vin, manufacturer=VEHICLE_SPEC['manufacturer'], make=VEHICLE_SPEC['make'],
            model=VEHICLE_SPEC['model'], year=VEHICLE_SPEC['year'], color=VEHICLE_SPEC['color'],
            first_owner=self.first_owner, manufacturer_id=self.manufacturer_id)
        # The registry keys its tables by vehicle_id = f"vehicle_{certificate_id}" (see
        # CentralizedVehicleRegistry.register_vehicle_birth); it returns only the certificate.
        return {'handle': f"vehicle_{cert.certificate_id}", 'vin': cert.vin}

    def record_event(self, handle: str, odometer: int, data: Dict[str, Any]) -> Dict[str, Any]:
        ev = self.reg.record_lifecycle_event(handle, CEventType.MAINTENANCE, self.service_center_id,
                                             odometer, data, JURISDICTION)
        return {'event_id': ev.event_id, 'odometer': ev.odometer}

    def attest_event(self, handle: str, event_id: Any) -> Dict[str, Any]:
        raise NotImplementedError(self.attest_note)

    def transfer_ownership(self, handle: str, odometer: int) -> Dict[str, Any]:
        t = self.reg.transfer_ownership(handle, self.new_owner, odometer, SALE_PRICE, TRANSFER_AUTHORITY)
        return {'to': t.to_owner, 'odometer': t.odometer}

    def query_history(self, handle: str) -> Dict[str, Any]:
        h = self.reg.get_vehicle_history(handle)
        if not h:
            return {}
        return {
            'vin': h['birth_certificate']['vin'],
            'current_owner': h['current_owner'],
            'event_count': h['event_count'],
            'events': [{'odometer': e['odometer'], 'type': e['event_type']} for e in h['lifecycle_events']],
            'transfer_count': h['transfer_count'],
            'transfers': [{'to': t['to_owner'], 'odometer': t['odometer']} for t in h['ownership_history']],
            'attestation_count': None,   # no such concept in this registry
        }

    # untimed sanity probes (same semantics on both sides)
    def unauthorized_event_rejected(self, handle: str) -> bool:
        try:
            self.reg.record_lifecycle_event(handle, CEventType.MAINTENANCE, 'NOBODY', 1, {}, JURISDICTION)
            return False
        except ValueError:
            return True

    def duplicate_vin_rejected(self, vin: str) -> bool:
        try:
            self.register_birth(vin)
            return False
        except ValueError:
            return True


# --------------------------------------------------------------------------
# Adapter 2: MOBI VID V2 on a local chain. Birth registration goes through the
# shipped MOBIVIDProvider (salted VIN hash, AES-GCM VIN encryption, key pair,
# registerVehicleBirth tx). The VID II functions are not wrapped by any provider
# in the testbed, so this adapter calls MOBIVIDRegistryV2 directly with the same
# transaction plumbing as the provider (fixed gas, legacy gasPrice, local signing,
# wait for receipt).
# --------------------------------------------------------------------------
class MOBIVIDV2Adapter:
    is_chain = True
    supports_attest = True

    def __init__(self, rpc_url: str, contract_address: str, artifact_path: str = V2_ARTIFACT):
        from eth_account import Account
        from web3 import Web3
        from identity.mobi_vid_provider import MOBIVIDProvider

        Account.enable_unaudited_hdwallet_features()

        def hh(i: int):  # Hardhat default, pre-funded test accounts (never use on a real network)
            return Account.from_mnemonic(HARDHAT_MNEMONIC, account_path=f"m/44'/60'/0'/0/{i}")

        self.prov = MOBIVIDProvider(rpc_url, contract_address=contract_address)  # account #0 = deployer
        self.w3 = self.prov.w3
        self.Web3 = Web3
        with open(artifact_path) as f:
            self.abi = json.load(f)['abi']
        self.contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=self.abi)
        self.chain_id = int(self.w3.eth.chain_id)
        self.manufacturer = self.prov.account            # registry authority + authorised manufacturer
        self.first_owner = hh(1)                         # signs transferVehicleOwnership (ERC-1056 onlyOwner)
        self.service_center = hh(2)                      # records MAINTENANCE events
        self.dealer = hh(3)                              # attests events
        self.new_owner = hh(4).address                   # receives ownership (never signs)
        assert self.manufacturer.address == hh(0).address, "MOBIVIDProvider default account is Hardhat #0"
        self.last_receipt = None

        # Capture the receipt of every transaction, including those sent inside
        # MOBIVIDProvider.register_vehicle_birth (which does not expose it).
        orig_wait = self.w3.eth.wait_for_transaction_receipt

        def wait_and_capture(tx_hash, *a, **k):
            r = orig_wait(tx_hash, *a, **k)
            self.last_receipt = r
            return r
        self.w3.eth.wait_for_transaction_receipt = wait_and_capture

    # ---- transaction plumbing (mirrors MOBIVIDProvider.register_vehicle_birth) ----
    def _send(self, fn, account):
        tx = fn.build_transaction({
            'from': account.address,
            'nonce': self.w3.eth.get_transaction_count(account.address),
            'gas': TX_GAS_LIMIT,
            'gasPrice': self.w3.eth.gas_price,
        })
        signed = account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        if receipt['status'] != 1:
            raise RuntimeError(f"transaction reverted: {tx_hash.hex()}")
        return receipt

    def _logs(self, receipt, event_name: str):
        from web3.logs import DISCARD
        return getattr(self.contract.events, event_name)().process_receipt(receipt, errors=DISCARD)

    def _addr(self, handle: str) -> str:
        return self.Web3.to_checksum_address(handle)

    # ---- setup (untimed) ----
    def setup_issuers(self):
        for acct, role in ((self.service_center, CHAIN_ROLE_SERVICE_CENTER), (self.dealer, CHAIN_ROLE_DEALER)):
            current = self.contract.functions.authorizedIssuers(acct.address).call()
            if current != role:
                self._send(self.contract.functions.authorizeIssuer(acct.address, role), self.manufacturer)

    # ---- the operation set ----
    def register_birth(self, vin: str) -> Dict[str, Any]:
        cred = self.prov.register_vehicle_birth(
            vin=vin,
            manufacturer_data={'name': VEHICLE_SPEC['manufacturer']},
            vehicle_data={'make': VEHICLE_SPEC['make'], 'model': VEHICLE_SPEC['model'],
                          'year': VEHICLE_SPEC['year'], 'color': VEHICLE_SPEC['color']},
            first_owner_address=self.first_owner.address)
        identity = cred.credential_data['vehicle_identity']   # lowercase 0x.. (also the AES-GCM AAD)
        return {'handle': identity, 'vin': vin, 'did': cred.vehicle_id}

    def record_event(self, handle: str, odometer: int, data: Dict[str, Any]) -> Dict[str, Any]:
        # Event payload stays off-chain (IPFS in the design); the chain anchors its hash
        # and the hash of a minimal W3C-VC-shaped credential for the event.
        data_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).digest()
        credential = {
            'type': ['VerifiableCredential', 'MOBIVehicleLifecycleEvent'],
            'issuer': self.service_center.address,
            'credentialSubject': {'id': f"did:ethr:0x{self.chain_id:x}:{handle}", 'eventType': 'MAINTENANCE',
                                  'odometer': odometer, 'dataHash': data_hash.hex(), 'jurisdiction': JURISDICTION},
        }
        cred_hash = hashlib.sha256(json.dumps(credential, sort_keys=True).encode()).digest()
        receipt = self._send(self.contract.functions.recordLifecycleEvent(
            self._addr(handle), CHAIN_EVENT_MAINTENANCE, odometer, data_hash, cred_hash, JURISDICTION),
            self.service_center)
        logs = self._logs(receipt, 'LifecycleEventRecorded')   # decoded locally from the receipt
        if not logs:
            raise RuntimeError("LifecycleEventRecorded log missing")
        return {'event_id': bytes(logs[0]['args']['eventId']), 'odometer': int(logs[0]['args']['odometer'])}

    def attest_event(self, handle: str, event_id: bytes) -> Dict[str, Any]:
        from eth_account.messages import encode_defunct
        # Digest the contract verifies: keccak256(abi.encodePacked(address(this), chainid, vehicle, eventId))
        # under the EIP-191 prefix, recovered on-chain and required to equal msg.sender.
        digest = self.Web3.solidity_keccak(['address', 'uint256', 'address', 'bytes32'],
                                           [self.contract.address, self.chain_id, self._addr(handle), event_id])
        signature = bytes(self.dealer.sign_message(encode_defunct(primitive=digest)).signature)
        receipt = self._send(self.contract.functions.attestEvent(event_id, self._addr(handle), signature), self.dealer)
        logs = self._logs(receipt, 'EventAttested')
        if not logs:
            raise RuntimeError("EventAttested log missing")
        return {'attester': logs[0]['args']['attester'], 'signature_bytes': len(signature)}

    def transfer_ownership(self, handle: str, odometer: int) -> Dict[str, Any]:
        receipt = self._send(self.contract.functions.transferVehicleOwnership(
            self._addr(handle), self.new_owner, odometer, TRANSFER_AUTHORITY), self.first_owner)
        logs = self._logs(receipt, 'VehicleOwnershipTransferred')
        if not logs:
            raise RuntimeError("VehicleOwnershipTransferred log missing")
        return {'to': logs[0]['args']['to'], 'odometer': int(logs[0]['args']['odometer'])}

    def query_history(self, handle: str) -> Dict[str, Any]:
        # Uncached full read: every call goes to the chain (no client-side cache, no multicall).
        addr = self._addr(handle)
        birth, current_owner, is_revoked, transfer_count = self.contract.functions.getVehicleInfo(addr).call()
        event_ids = self.contract.functions.getVehicleEvents(addr).call()
        events = [self.contract.functions.getEvent(addr, eid).call() for eid in event_ids]
        attestations = [self.contract.functions.getEventAttestations(eid).call() for eid in event_ids]
        transfers = self.contract.functions.getOwnershipHistory(addr).call()
        vin = self.prov._decrypt_vin(birth[1], handle)   # authorised party recovers the VIN (AES-256-GCM)
        return {
            'vin': vin,
            'current_owner': current_owner,
            'is_revoked': is_revoked,
            'event_count': len(event_ids),
            'events': [{'odometer': int(e[4]), 'type': int(e[1])} for e in events],
            'transfer_count': int(transfer_count),
            'transfers': [{'to': t[1], 'odometer': int(t[4])} for t in transfers],
            'attestation_count': sum(len(a) for a in attestations),
        }

    # untimed sanity probes
    def unauthorized_event_rejected(self, handle: str) -> bool:
        try:
            self._send(self.contract.functions.recordLifecycleEvent(
                self._addr(handle), CHAIN_EVENT_MAINTENANCE, 1, b'\0' * 32, b'\0' * 32, JURISDICTION),
                self.first_owner)   # funded account, but not an authorised issuer
            return False
        except Exception:
            return True

    def duplicate_vin_rejected(self, vin: str) -> bool:
        try:
            self.register_birth(vin)
            return False
        except Exception:
            return True


# --------------------------------------------------------------------------
# The identical operation set, measured
# --------------------------------------------------------------------------
def run_backend(backend: Backend, n: int, warmup: int, run_tag: str) -> Dict[str, Any]:
    ad = backend.provider
    tag = f"{backend.name}_{run_tag}"
    total = warmup + n
    is_chain = backend.is_chain
    print(f"\n=== {backend.name} (n={n}, warmup={warmup}, run_tag={run_tag}) ===")

    results: Dict[str, Dict[str, Any]] = {}
    not_run: Dict[str, str] = {}

    def record(op, samples, chain_round_trip):
        s = summarize(samples)
        s['chain_round_trip'] = chain_round_trip
        s['status'] = 'measured'
        s['samples_ms'] = [round(x.elapsed_ms, 4) for x in samples]
        sizes = [x.extra['history_json_bytes'] for x in samples if 'history_json_bytes' in x.extra]
        if sizes:
            s['history_json_bytes_median'] = float(np.median(sizes))
        results[op] = s
        gas = f" gas={s['gas_used']}" if s['gas_used'] is not None else (
            f" gas={s['gas_min']}..{s['gas_max']}" if s['gas_min'] is not None else "")
        rpc = f" rpc/op={s['rpc_calls_median']:.0f}" if is_chain else ""
        print(f"  {op:<23} median={s['median_ms']:.3f} ms  p95={s['p95_ms']:.3f} ms{gas}{rpc}")

    def fresh_vehicle(kind: str, i: int) -> str:
        return ad.register_birth(make_vin(tag, kind, i))['handle']

    # 1. register_birth (fresh VIN per repetition)
    def check_birth(vin, r):
        if not r or not r.get('handle') or r.get('vin') != vin:
            _fail("register_birth returned no handle / wrong VIN")
        return {}
    record('register_birth', measure(
        backend, 'register_birth', n, warmup,
        prepare=lambda i: make_vin(tag, 'B', i),
        run=lambda vin: ad.register_birth(vin),
        check=check_birth, chain_write=is_chain), is_chain)

    # 2. record_lifecycle_event (fresh vehicle per repetition; first event on that vehicle)
    def check_event(h, r):
        if not r or not r.get('event_id') or r.get('odometer') != ODOMETER_EVENT:
            _fail("record_lifecycle_event returned no event id / wrong odometer")
        return {}
    record('record_lifecycle_event', measure(
        backend, 'record_lifecycle_event', n, warmup,
        prepare=lambda i: fresh_vehicle('E', i),
        run=lambda h: ad.record_event(h, ODOMETER_EVENT, EVENT_DATA),
        check=check_event, chain_write=is_chain), is_chain)

    # 3. attest_event (fresh vehicle + fresh event per repetition)
    if ad.supports_attest:
        def prepare_attest(i):
            h = fresh_vehicle('A', i)
            ev = ad.record_event(h, ODOMETER_EVENT, EVENT_DATA)
            return (h, ev['event_id'])

        def check_attest(ctx, r):
            if not r or r.get('attester') != ad.dealer.address:
                _fail("attest_event: attester mismatch")
            return {}
        record('attest_event', measure(
            backend, 'attest_event', n, warmup,
            prepare=prepare_attest,
            run=lambda ctx: ad.attest_event(ctx[0], ctx[1]),
            check=check_attest, chain_write=is_chain), is_chain)
    else:
        not_run['attest_event'] = ad.attest_note
        print(f"  {'attest_event':<23} NOT RUN: no equivalent operation in this backend")

    # 4. transfer_ownership (fresh vehicle per repetition; first transfer on that vehicle)
    def check_transfer(h, r):
        if not r or r.get('to') != ad.new_owner or r.get('odometer') != ODOMETER_TRANSFER:
            _fail("transfer_ownership: wrong new owner / odometer")
        return {}
    record('transfer_ownership', measure(
        backend, 'transfer_ownership', n, warmup,
        prepare=lambda i: fresh_vehicle('T', i),
        run=lambda h: ad.transfer_ownership(h, ODOMETER_TRANSFER),
        check=check_transfer, chain_write=is_chain), is_chain)

    # 5. query_history: one vehicle carrying the full history (setup untimed)
    hist_vin = make_vin(tag, 'H', 0)
    hist = ad.register_birth(hist_vin)['handle']
    ev = ad.record_event(hist, ODOMETER_EVENT, EVENT_DATA)
    if ad.supports_attest:
        ad.attest_event(hist, ev['event_id'])
    ad.transfer_ownership(hist, ODOMETER_TRANSFER)

    def check_history(h, r):
        if not r or r.get('vin') != hist_vin:
            _fail("query_history: VIN not recovered")
        if r.get('event_count') != 1 or r['events'][0]['odometer'] != ODOMETER_EVENT:
            _fail("query_history: event missing / wrong odometer")
        if r.get('transfer_count') != 1 or r['transfers'][0]['to'] != ad.new_owner:
            _fail("query_history: transfer missing")
        if r.get('current_owner') != ad.new_owner:
            _fail("query_history: current owner not updated")
        if ad.supports_attest and r.get('attestation_count') != 1:
            _fail("query_history: attestation missing")
        return {'history_json_bytes': len(json.dumps(r, default=str).encode())}
    record('query_history', measure(
        backend, 'query_history', n, warmup,
        prepare=lambda i: hist,
        run=lambda h: ad.query_history(h),
        check=check_history), is_chain)

    # Untimed sanity: both registries enforce issuer authorisation and VIN uniqueness.
    sanity = {
        'unauthorized_issuer_rejected': bool(ad.unauthorized_event_rejected(hist)),
        'duplicate_vin_rejected': bool(ad.duplicate_vin_rejected(hist_vin)),
        'history_complete_after_all_operations': True,  # enforced by check_history above
    }
    print(f"  sanity: {sanity}")
    return {'operations': results, 'not_run': not_run, 'sanity': sanity}


# --------------------------------------------------------------------------
# Output writers
# --------------------------------------------------------------------------
CSV_COLUMNS = ['provider', 'operation', 'status', 'chain_round_trip', 'n', 'mean_ms', 'median_ms',
               'p95_ms', 'min_ms', 'max_ms', 'stdev_ms', 'gas_used', 'gas_median', 'gas_min',
               'gas_max', 'rpc_calls_median', 'note']
ENV_KEYS = ('date_utc', 'git_commit', 'git_dirty', 'python_version', 'node_version', 'hardhat_version',
            'ethers_version', 'web3_version', 'solc_version', 'cryptography_version', 'chain_id',
            'block_gas_limit', 'automine', 'contract_name', 'contract_address', 'contract_deploy_gas',
            'rpc_url', 'cpu_model', 'cpu_count', 'os')


def write_csv(path: str, rows: List[Dict[str, Any]]):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            out = {k: r.get(k) for k in CSV_COLUMNS}
            for k in ('mean_ms', 'median_ms', 'p95_ms', 'min_ms', 'max_ms', 'stdev_ms'):
                if out.get(k) is not None:
                    out[k] = f"{out[k]:.4f}"
            w.writerow(out)


def fmt(x, digits=3):
    return "-" if x is None else f"{x:.{digits}f}"


def write_md(path: str, env: Dict[str, Any], rows: List[Dict[str, Any]], sanity: Dict[str, Dict[str, bool]],
             skipped: Dict[str, str], n: int, warmup: int):
    backends: List[str] = []
    for r in rows:
        if r['provider'] not in backends:
            backends.append(r['provider'])

    def row_of(b, op):
        return next((x for x in rows if x['provider'] == b and x['operation'] == op), None)

    L: List[str] = []
    L.append("# Lifecycle parity: centralized vehicle registry vs MOBI VID V2, measured\n")
    L.append("Generated by `scripts/experiment_lifecycle_parity.py` (plan M4, scope entry SC-13). Both backends "
             "run the same operation set with the same inputs and the same result checks; each measured figure is "
             f"over n={n} warm repetitions after {warmup} discarded warm-up runs, timed with "
             "`time.perf_counter_ns`. Gas is the exact `gasUsed` from the transaction receipt; RPC calls are "
             "counted at the web3 HTTP provider. Write operations use a fresh vehicle per repetition; "
             "`query_history` repeats on one vehicle holding the full history. **Compare only within this run** "
             "(see `cpu_model`).\n")
    L.append("## Environment\n")
    L.append("| Item | Value |\n|---|---|")
    for k in ENV_KEYS:
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
        if r['status'] != 'measured':
            L.append(f"| {r['provider']} | {r['operation']} | - | 0 | not run | not run | - | - | - | - | - |")
            continue
        gas = r['gas_used'] if r['gas_used'] is not None else (
            f"{r['gas_median']} ({r['gas_min']}..{r['gas_max']})" if r['gas_min'] is not None else "-")
        rpc = int(r['rpc_calls_median']) if r['chain_round_trip'] else "-"
        L.append(f"| {r['provider']} | {r['operation']} | {'yes' if r['chain_round_trip'] else 'no'} | "
                 f"{r['n']} | {fmt(r['median_ms'])} | {fmt(r['p95_ms'])} | {fmt(r['mean_ms'])} | "
                 f"{fmt(r['min_ms'])} | {fmt(r['max_ms'])} | {gas} | {rpc} |")
    L.append("")

    L.append("### Side-by-side (median / p95, ms) and ratio of medians\n")
    L.append("| Operation | " + " | ".join(backends) + " | mobi_vid_v2 / centralized (median) |")
    L.append("|---|" + "---|" * len(backends) + "---:|")
    for op, _ in OPERATIONS:
        cells = []
        for b in backends:
            r = row_of(b, op)
            cells.append(f"{fmt(r['median_ms'])} / {fmt(r['p95_ms'])}" if r and r['status'] == 'measured'
                         else ("not equivalent" if r else "-"))
        c = row_of('centralized_registry', op)
        m = row_of('mobi_vid_v2', op)
        ratio = (f"{m['median_ms'] / c['median_ms']:.0f}x" if c and m and c['status'] == 'measured'
                 and m['status'] == 'measured' and c['median_ms'] > 0 else "-")
        L.append(f"| {op} | " + " | ".join(cells) + f" | {ratio} |")
    L.append("")

    sizes = [(r['provider'], r.get('history_json_bytes_median')) for r in rows
             if r['operation'] == 'query_history' and r.get('history_json_bytes_median')]
    if sizes:
        L.append("Normalised history record size returned by `query_history` (JSON bytes, median): " +
                 ", ".join(f"{p}={int(s)}" for p, s in sizes) + ".\n")
    rpc_rows = [r for r in rows if r.get('rpc_methods')]
    if rpc_rows:
        L.append("JSON-RPC methods issued per MOBI VID V2 operation (first warm run):\n")
        for r in rpc_rows:
            L.append(f"- `{r['operation']}`: {', '.join(r['rpc_methods'])}")
        L.append("")
        q = row_of('mobi_vid_v2', 'query_history')
        if q and q.get('rpc_methods'):
            methods = q['rpc_methods']
            chain_id_calls = sum(1 for m in methods if m == 'eth_chainId')
            calls = sum(1 for m in methods if m == 'eth_call')
            L.append(f"Of the {len(methods)} round trips in `query_history`, {calls} are registry reads (`eth_call`) "
                     f"and {chain_id_calls} are `eth_chainId` requests that web3.py {env.get('web3_version')} issues "
                     "around each call: client-side redundancy, removable by enabling web3's request cache or "
                     "pinning the chain id. The adapter is measured without that tuning, as the ERC-1056 "
                     "experiment was.\n")

    # Pre-registered M4 hypothesis (docs/PLAN_MOBI_SUMO.md A.2): centralized >= 10x faster than
    # MOBI-VID-V2 for birth and lifecycle writes (local); equal for history queries once cached.
    L.append("## Pre-registered M4 hypothesis, checked against this run\n")
    L.append("Hypothesis (docs/PLAN_MOBI_SUMO.md A.2): the centralized registry is >= 10x faster than MOBI VID V2 "
             "for birth and lifecycle writes (local), and equal for history queries once the chain history is cached.\n")
    L.append("| Operation | centralized median (ms) | mobi_vid_v2 median (ms) | ratio | >= 10x? |")
    L.append("|---|---:|---:|---:|:---:|")
    for op in ('register_birth', 'record_lifecycle_event', 'transfer_ownership', 'query_history'):
        c = row_of('centralized_registry', op)
        m = row_of('mobi_vid_v2', op)
        if c and m and c['status'] == 'measured' and m['status'] == 'measured' and c['median_ms'] > 0:
            ratio = m['median_ms'] / c['median_ms']
            verdict = ('yes' if ratio >= 10 else 'no') if op != 'query_history' else 'n/a (uncached read; cached case not measured)'
            L.append(f"| {op} | {fmt(c['median_ms'])} | {fmt(m['median_ms'])} | {ratio:.0f}x | {verdict} |")
        else:
            L.append(f"| {op} | {fmt(c['median_ms']) if c else '-'} | {fmt(m['median_ms']) if m else '-'} | - | not measured |")
    L.append("")
    L.append("The write part of the hypothesis is tested by the first three rows. The \"equal once cached\" part is "
             "**not tested**: `query_history` here is the uncached read, and no cached history client exists in the "
             "testbed. The ratios are between an in-process registry and a localhost chain (caveats 1-2); they bound "
             "the gap from below on the centralized side and do not transfer to a deployed service or a public network.\n")

    L.append("## Sanity checks (untimed, must all be True)\n")
    L.append("| Backend | unauthorised issuer rejected | duplicate VIN rejected | history complete after all operations |")
    L.append("|---|:---:|:---:|:---:|")
    for b, s in sanity.items():
        L.append(f"| {b} | {s['unauthorized_issuer_rejected']} | {s['duplicate_vin_rejected']} | "
                 f"{s['history_complete_after_all_operations']} |")
    L.append("")

    L.append("## What each operation actually does per backend\n")
    L.append("| Operation | centralized_registry (CentralizedVehicleRegistry, in-process) | mobi_vid_v2 (MOBIVIDRegistryV2 on Hardhat) |")
    L.append("|---|---|---|")
    L.append("| register_birth | issuer-role dict check, duplicate-VIN check, SHA-256 certificate id, plain-text VIN "
             "and dataclass stored in Python dicts | `MOBIVIDProvider.register_vehicle_birth`: salted SHA-256 VIN hash, "
             "AES-256-GCM VIN encryption (HKDF per-vehicle key), SHA-256 birth-certificate hash, "
             "`registerVehicleBirth` tx signed by the manufacturer (1 tx: birth struct + VIN-hash index + ERC-1056 "
             "owner + ERC-1056 attribute), wait for receipt, secp256k1 vehicle key pair, `did:ethr` credential |")
    L.append("| record_lifecycle_event | vehicle + issuer-role checks, SHA-256 event id, dataclass with the full event "
             "payload appended to a list | SHA-256 of the event payload and of a VC-shaped credential (payload stays "
             "off-chain), `recordLifecycleEvent` tx signed by the service centre (role check on-chain, event struct + "
             "id list + counters), wait for receipt, event id decoded from the receipt log |")
    L.append("| attest_event | **no equivalent** (single issuer per event; `verified` flag from the issuer's role) | "
             "dealer signs the EIP-191 digest of (contract, chainId, vehicle, eventId) off-chain, `attestEvent` tx "
             "(role check + `ecrecover` must equal msg.sender, attestation struct appended), wait for receipt |")
    L.append("| transfer_ownership | vehicle check, SHA-256 transfer id, dataclass appended, owner dict updated; "
             "**no caller authentication** (any caller may transfer any vehicle) | `transferVehicleOwnership` tx "
             "signed by the current owner's key (ERC-1056 `onlyOwner`), transfer struct appended, ERC-1056 "
             "`changeOwner`, wait for receipt |")
    L.append("| query_history | one dict lookup per table, dataclasses serialised to dicts (full event payloads) | "
             "`getVehicleInfo` + `getVehicleEvents` + `getEvent` x events + `getEventAttestations` x events + "
             "`getOwnershipHistory` (5 `eth_call` for one event, no caching, no multicall) + AES-GCM VIN decryption; "
             "returns hashes, not event payloads |")
    L.append("")

    L.append("## Caveats (read before quoting any number)\n")
    L.append("1. **The centralized registry is in-process.** `CentralizedVehicleRegistry` is a Python object in the "
             "measuring process: no HTTP/REST layer, no database engine, no network, no serialisation on the write "
             "path, and no cryptographic authentication of callers (issuer authorisation is a dictionary lookup; "
             "`transfer_ownership` does not authenticate the caller at all). Its figures are therefore the cost of "
             "the registry logic alone and a *lower bound* on a deployed centralized service (which adds at least "
             "one network round trip, TLS, authentication and a database commit per write). The comparison "
             "measures the *shape* of the gap, not a deployed service.")
    L.append("2. **Hardhat local is not a public network.** The MOBI VID side is a single Hardhat node on "
             "localhost with automine: a transaction is mined the instant it is received, so the chain figures are "
             "web3.py + HTTP JSON-RPC + Hardhat's EVM on this machine. On a public or consortium network every "
             "write (birth, event, attestation, transfer) takes at least one block interval plus confirmation depth "
             "(seconds to minutes) and reads depend on the RPC endpoint; `gasUsed` transfers unchanged, the "
             "milliseconds do not.")
    L.append("3. **Operations that are not strictly equivalent.**")
    L.append("   - `attest_event` exists only on the MOBI VID side; the centralized registry has no multi-party "
             "attestation, so the row is recorded as *not equivalent* and nothing was substituted for it.")
    L.append("   - `register_birth` does more on the MOBI side (VIN privacy: salted hash + AES-GCM; key-pair "
             "generation; an on-chain ERC-1056 attribute write) than on the centralized side (plain-text VIN in a "
             "dict).")
    L.append("   - `record_lifecycle_event` stores the full event payload in the centralized registry but only two "
             "32-byte hashes (payload + credential) on-chain; the payload would live off-chain (IPFS) in the design. "
             "The chain row also includes decoding the event id from the receipt log.")
    L.append("   - `transfer_ownership` is authenticated on-chain (the current owner's secp256k1 signature, checked "
             "by the node and by ERC-1056 `onlyOwner`) and unauthenticated in the centralized registry.")
    L.append("   - `query_history` on the MOBI side is the *uncached* full read (5 `eth_call` for one event plus "
             "web3's own `eth_chainId` traffic) and returns hashes where the centralized side returns payloads. "
             "The M4 pre-registration's \"equal once the chain history is cached\" case is not measured here: a "
             "client that caches a vehicle's history and re-validates with one `changed(identity)` call would pay "
             "one round trip, not five.")
    L.append("   - Each write is measured on a fresh vehicle (first event / first transfer / first attestation on "
             "that vehicle), so the chain gas includes zero-to-non-zero storage initialisation of the per-vehicle "
             "counters and arrays; a second event on the same vehicle costs less gas. The small `min..max` gas "
             "spread within one operation is EIP-2028 calldata pricing of the varying hash / ciphertext bytes, not "
             "measurement noise.")
    L.append("4. **Gas is deterministic; latency is not.** `gasUsed` is exact and reproducible for the same inputs; "
             "latency varies with scheduling, GC and RPC, hence n repetitions, median (robust) and p95 (tail).")
    L.append("5. **Single machine, single process, no concurrency; one run.** Throughput under load and multi-client "
             "contention are out of scope. The absolute values depend on `cpu_model`; only ratios measured within "
             "one run are meaningful, and even those only for the shapes described above.")
    L.append("6. **Deploy script change.** `scripts/deploy_mobi_vid.js` deployed only the VID I contract; it now "
             "takes `MOBI_VID_CONTRACT=MOBIVIDRegistryV2` to deploy V2 (default unchanged). No provider or contract "
             "was modified; the VID II calls live in the adapter inside this script.")
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
    ap.add_argument('--contract-address', default=None, help='MOBIVIDRegistryV2 address (default: from --deployment-file)')
    ap.add_argument('--deployment-file', default=os.path.join(ROOT, 'deployments', 'mobi_vid_localhost.json'),
                    help='deploy_mobi_vid.js output (contractAddress, gasUsed)')
    ap.add_argument('--no-chain', action='store_true', help='skip the MOBI VID V2 backend')
    ap.add_argument('--out-dir', default=os.path.join(ROOT, 'results'))
    ap.add_argument('--render-only', action='store_true',
                    help='do not measure; re-write the .csv/.md from the existing .json in --out-dir')
    args = ap.parse_args()
    if args.n < 30:
        ap.error('--n must be >= 30')

    base = os.path.join(args.out_dir, 'lifecycle_parity')
    if args.render_only:
        with open(base + '.json') as f:
            saved = json.load(f)
        write_csv(base + '.csv', saved['results'])
        write_md(base + '.md', saved['environment'], saved['results'], saved['sanity'],
                 saved.get('backends_skipped', {}), saved['config']['n'], saved['config']['warmup'])
        print(f"Re-rendered .csv/.md from {base}.json")
        return

    backends: List[Backend] = [Backend('centralized_registry', CentralizedRegistryAdapter(), False)]
    skipped: Dict[str, str] = {}
    chain_info: Optional[Dict[str, Any]] = None

    if args.no_chain:
        skipped['mobi_vid_v2'] = 'skipped by --no-chain'
    else:
        try:
            address = args.contract_address
            deploy_gas = None
            contract_name = 'MOBIVIDRegistryV2'
            if address is None:
                with open(args.deployment_file) as f:
                    dep = json.load(f)
                address = dep['contractAddress']
                deploy_gas = int(dep['gasUsed']) if dep.get('gasUsed') else None
                contract_name = dep.get('contractName', contract_name)
                if contract_name != 'MOBIVIDRegistryV2':
                    raise RuntimeError(f"{args.deployment_file} is a {contract_name} deployment, not MOBIVIDRegistryV2 "
                                       "(deploy with MOBI_VID_CONTRACT=MOBIVIDRegistryV2)")
            ad = MOBIVIDV2Adapter(args.rpc_url, address)
            ad.setup_issuers()
            w3 = ad.w3
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
                'contract_name': contract_name,
                'contract_address': address,
                'contract_deploy_gas': deploy_gas,
                'client_version': w3.client_version if hasattr(w3, 'client_version') else None,
            }
            backends.append(Backend('mobi_vid_v2', ad, True, RPCCounter(w3)))
        except Exception as e:  # never fabricate: record precisely why the chain backend is absent
            skipped['mobi_vid_v2'] = f'not run: {type(e).__name__}: {e}'
            print(f"WARNING: MOBI VID V2 backend not run: {e}")

    env = environment(chain_info, args.n, args.warmup)
    if chain_info is None:
        env['contract_name'] = None
    print("Environment:", json.dumps(env, indent=2))

    run_tag = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    rows: List[Dict[str, Any]] = []
    sanity: Dict[str, Dict[str, bool]] = {}
    not_equivalent: Dict[str, Dict[str, str]] = {}
    for b in backends:
        out = run_backend(b, args.n, args.warmup, run_tag)
        sanity[b.name] = out['sanity']
        not_equivalent[b.name] = out['not_run']
        for op, _ in OPERATIONS:
            if op in out['operations']:
                r = dict(out['operations'][op])
            else:
                r = {'status': 'not_equivalent', 'note': out['not_run'][op], 'n': 0, 'chain_round_trip': None,
                     'mean_ms': None, 'median_ms': None, 'p95_ms': None, 'min_ms': None, 'max_ms': None,
                     'stdev_ms': None, 'gas_used': None, 'gas_median': None, 'gas_min': None, 'gas_max': None,
                     'rpc_calls_median': None}
            r['provider'] = b.name
            r['operation'] = op
            rows.append(r)

    os.makedirs(args.out_dir, exist_ok=True)
    write_csv(base + '.csv', rows)
    with open(base + '.json', 'w') as f:
        json.dump({
            'environment': env,
            'config': {'n': args.n, 'warmup': args.warmup, 'run_tag': run_tag,
                       'vehicle_spec': VEHICLE_SPEC, 'event_data': EVENT_DATA,
                       'odometer_event': ODOMETER_EVENT, 'odometer_transfer': ODOMETER_TRANSFER,
                       'jurisdiction': JURISDICTION, 'transfer_authority': TRANSFER_AUTHORITY,
                       'tx_gas_limit': TX_GAS_LIMIT, 'fresh_vehicle_per_write_repetition': True,
                       'operations': [{'name': o, 'description': d} for o, d in OPERATIONS]},
            'backends_skipped': skipped,
            'not_equivalent': not_equivalent,
            'results': rows,
            'sanity': sanity,
        }, f, indent=2, default=str)
    write_md(base + '.md', env, rows, sanity, skipped, args.n, args.warmup)

    print(f"\nWrote:\n  {base}.csv\n  {base}.json\n  {base}.md")
    failed = [b for b, s in sanity.items() if not all(s.values())]
    if failed:
        print(f"SANITY FAILURES: {failed}")
        sys.exit(2)


if __name__ == '__main__':
    main()
