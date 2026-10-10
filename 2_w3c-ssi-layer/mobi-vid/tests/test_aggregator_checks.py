"""Chain-free checks of the history aggregator's two fraud signals (WM-1 audit, finding U-F3b/c).

The odometer-rollback detector had only a negative test (`== []`), and no test exercised an attestation
whose signature does not recover to its attester; mutants that never flag a rollback, or mark every
attestation valid, passed all tests. A stub registry stands in for the chain.
"""
import sys
from pathlib import Path

from eth_account import Account

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifecycle_events import LifecycleEventRecorder, VehicleHistoryAggregator  # noqa: E402


class _Role:
    def __init__(self, name):
        self.name = name


class StubRegistry:
    address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

    def __init__(self, odometer=(), attestations=()):
        self._odo = list(odometer)
        self._att = list(attestations)

    def chain_id(self):
        return 31337

    def get_odometer_history(self, vehicle):
        return self._odo

    def get_event_attestations(self, event_id):
        return self._att


VEHICLE = Account.create().address
EVENT = b"\x11" * 32


def test_rollback_is_flagged():
    reg = StubRegistry(odometer=[{"eventId": "e1", "odometer": 10_000}, {"eventId": "e2", "odometer": 25_000},
                                 {"eventId": "e3", "odometer": 12_000}, {"eventId": "e4", "odometer": 30_000}])
    anomalies = VehicleHistoryAggregator(reg).detect_odometer_rollback(VEHICLE)
    assert [a["eventId"] for a in anomalies] == ["e3"]
    assert anomalies[0]["expectedAtLeast"] == 25_000


def test_equal_reading_is_not_a_rollback():
    reg = StubRegistry(odometer=[{"eventId": "e1", "odometer": 10_000}, {"eventId": "e2", "odometer": 10_000}])
    assert VehicleHistoryAggregator(reg).detect_odometer_rollback(VEHICLE) == []


def _signed(attester, signer):
    from eth_account.messages import encode_defunct
    digest = LifecycleEventRecorder.attestation_digest(StubRegistry.address, 31337, VEHICLE, EVENT)
    sig = Account.sign_message(encode_defunct(digest), signer.key).signature
    return {"attester": attester.address, "role": _Role("SERVICE_CENTER"), "timestamp": 1, "signature": bytes(sig)}


def test_genuine_attestation_is_valid_and_forged_one_is_not():
    honest, impostor = Account.create(), Account.create()
    reg = StubRegistry(attestations=[_signed(honest, honest), _signed(honest, impostor)])
    out = VehicleHistoryAggregator(reg)._verified_attestations(VEHICLE, EVENT)
    assert [a["signatureValid"] for a in out] == [True, False]


def test_malformed_signature_is_invalid_not_a_crash():
    honest = Account.create()
    bad = dict(_signed(honest, honest), signature=b"\x00" * 10)
    out = VehicleHistoryAggregator(StubRegistry(attestations=[bad]))._verified_attestations(VEHICLE, EVENT)
    assert out[0]["signatureValid"] is False
