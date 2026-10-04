"""
M4 lifecycle parity (PLAN_MOBI_SUMO.md §A.2; after-action report 04 stream
F-D): the two backend adapters in identity/lifecycle_backends.py and the
verdict rule of scripts/experiment_lifecycle_parity.py.

The centralized-adapter and verdict tests run offline; the MOBI-VID-V2
adapter tests deploy MOBIVIDRegistryV2 from $CV2X_TEST_ARTIFACTS_DIR on the
node at $CV2X_TEST_RPC_URL (skipped only when no node answers).
"""

import time

import pytest
from eth_account import Account

from conftest import DEPLOYER_KEY, deploy, load_artifact
from experiment_lifecycle_parity import EQUAL_BAND, WRITE_SPEEDUP_THRESHOLD, verdicts
from identity.lifecycle_backends import (
    CentralizedLifecycleBackend, MOBIVIDV2LifecycleBackend, event_payload)


# ---------------------------------------------------------------- offline --
def test_centralized_adapter_operations():
    c = CentralizedLifecycleBackend()
    v = c.birth(f"VIN-C-{time.time_ns()}")
    assert c.current_owner(v) == 'OWNER-A'
    c.lifecycle_event(v, 1000, event_payload(1000))
    c.transfer(v, 1100)
    assert c.current_owner(v) == 'OWNER-B'
    c.transfer(v, 1200)
    assert c.current_owner(v) == 'OWNER-A'
    h = c.history(v)
    assert (h['event_count'], h['transfer_count']) == (1, 2)
    assert h['lifecycle_events'][0]['odometer'] == 1000
    d = c.history_unserialised(v)
    assert (d['event_count'], d['transfer_count']) == (1, 2)
    assert d['current_owner'] == h['current_owner']


def test_centralized_duplicate_vin_rejected():
    c = CentralizedLifecycleBackend()
    c.birth('VIN-DUP')
    with pytest.raises(ValueError):
        c.birth('VIN-DUP')


def _row(m):
    return {'median_ms': m, 'p95_ms': m * 1.2}


def test_verdict_rule():
    central = {'birth': _row(0.01), 'lifecycle_event': _row(0.01), 'ownership_transfer': _row(0.01),
               'history_query': _row(0.2), 'history_query_unserialised_diagnostic': _row(0.001)}
    mobi = {'birth': _row(0.1), 'lifecycle_event': _row(0.099), 'ownership_transfer': _row(5.0),
            'history_query': _row(80.0), 'history_query_cached': _row(0.39),
            'history_query_cached_validated': _row(10.0)}
    v = {x['operation']: x for x in verdicts(central, mobi)}
    assert WRITE_SPEEDUP_THRESHOLD == 10.0 and EQUAL_BAND == (0.5, 2.0)
    assert v['birth']['verdict'] == 'PASS'                 # exactly 10x
    assert v['lifecycle_event']['verdict'] == 'FAIL'       # 9.9x
    assert v['ownership_transfer']['verdict'] == 'PASS'
    assert v['history_query_cached']['verdict'] == 'PASS'  # 1.95x, inside [0.5, 2]
    assert v['history_query']['verdict'] == '(outside band)'
    mobi['history_query_cached'] = _row(0.05)               # 0.25x: MOBI faster -> not "equal"
    v = {x['operation']: x for x in verdicts(central, mobi)}
    assert v['history_query_cached']['verdict'] == 'FAIL'


# --------------------------------------------------------------- on chain --
@pytest.fixture(scope='module')
def mobi(rpc_url):
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    art = load_artifact('MOBIVIDRegistryV2')
    address = deploy(w3, Account.from_key(DEPLOYER_KEY), art)
    return MOBIVIDV2LifecycleBackend(rpc_url, address, art['abi'], seed=f"test-{time.time_ns()}")


def test_mobi_adapter_writes_and_gas(mobi):
    v = mobi.birth(f"VIN-M-{time.time_ns()}")
    assert mobi.birth_receipt().status == 1 and mobi.birth_receipt().gasUsed > 100_000
    assert mobi.current_owner(v) == mobi.owners[0].address
    r = mobi.lifecycle_event(v, 1000, event_payload(1000))
    assert r.status == 1 and mobi.last_receipt is r and r.gasUsed > 50_000
    mobi.transfer(v, 1100)
    assert mobi.current_owner(v) == mobi.owners[1].address
    mobi.transfer(v, 1200)
    assert mobi.current_owner(v) == mobi.owners[0].address
    h = mobi.history(v)
    assert (h['event_count'], h['transfer_count']) == (1, 2)
    assert h['lifecycle_events'][0]['odometer'] == 1000
    assert h['ownership_history'][0]['to_owner'] == mobi.owners[1].address


def test_mobi_cached_history_equals_chain_and_validation_detects_change(mobi):
    v = mobi.birth(f"VIN-H-{time.time_ns()}")
    mobi.lifecycle_event(v, 10, event_payload(10))
    mobi.refresh_history_cache(v)
    assert mobi.history_cached(v) == mobi.history(v)
    mobi.lifecycle_event(v, 20, event_payload(20))
    assert mobi.history_cached(v)['event_count'] == 1          # stale by construction
    assert mobi.history_cached_validated(v)['event_count'] == 2
    assert mobi.history_cached(v)['event_count'] == 2          # cache was refreshed


def test_mobi_unauthorised_issuer_cannot_record(mobi):
    """The adapter's service centre is authorised in setup; a stranger is not."""
    v = mobi.birth(f"VIN-U-{time.time_ns()}")
    stranger = Account.create()
    assert mobi.contract.functions.isAuthorizedIssuer(stranger.address, 0).call() is False
    assert mobi.contract.functions.isAuthorizedIssuer(mobi.service_center.address, 0).call() is True
    assert v
