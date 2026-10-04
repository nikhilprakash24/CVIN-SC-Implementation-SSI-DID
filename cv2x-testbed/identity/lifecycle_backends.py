"""
Lifecycle-parity backends (PLAN_MOBI_SUMO.md step M4; review §3.3).

Two adapters with one interface, so the M4 experiment can run the SAME four
operations, with the same inputs, through the centralized vehicle registry
(the VID II design's control) and through MOBI-VID-V2 on chain:

    birth(vin, first_owner_index)        -> vehicle handle
    lifecycle_event(handle, odometer, data)
    transfer(handle, odometer)           (alternates between two owners)
    history(handle)                      -> dict (birth, current owner, events, transfers, counts)

and, for MOBI-VID-V2 only, two history variants:

    history(handle)                      uncached: every field read from the chain
    history_cached(handle)               served from a local copy of the chain history
                                         (fill it with refresh_history_cache first)
    history_cached_validated(handle)     the cached copy after a 2-eth_call staleness probe
                                         (vehicleEventCount, getOwnershipHistoryCount)

The adapters only forward to the existing code: `CentralizedVehicleRegistry`
(identity/centralized_vehicle_registry.py) and `MOBIVIDProvider`
(identity/mobi_vid_provider.py, VID I birth incl. VIN hash + AES-GCM VIN
encryption) plus direct `MOBIVIDRegistryV2` calls for the VID II operations
that the provider does not wrap (recordLifecycleEvent,
transferVehicleOwnership, the history getters). Chain writes leave their
receipt in `last_receipt` (exact gasUsed).
"""

import hashlib
import json
from typing import Any, Dict, List, Optional

from identity.centralized_vehicle_registry import (
    CentralizedVehicleRegistry,
    EventType as CEventType,
    IssuerRole as CIssuerRole,
)

# MOBIVIDRegistryV2 enum ordinals (contracts/MOBIVIDRegistryV2.sol)
V2_EVENT_MAINTENANCE = 0
V2_ROLE_SERVICE_CENTER = 3

MANUFACTURER = {'name': 'Testbed Motors', 'plant': 'Plant-1'}
VEHICLE = {'make': 'Testbed', 'model': 'BSM-Vehicle', 'year': 2026, 'color': 'grey'}
JURISDICTION = 'CA-BC'
AUTHORITY = 'BC-DMV'


def event_payload(odometer: int) -> Dict[str, Any]:
    """The lifecycle event body both backends receive (MAINTENANCE)."""
    return {'service': 'oil change', 'odometer': odometer, 'technician': 'T-1', 'parts': ['filter', 'oil']}


# ----------------------------------------------------------------------------
# Centralized registry (in-process)
# ----------------------------------------------------------------------------
class CentralizedLifecycleBackend:
    name = 'centralized_registry'
    is_chain = False

    def __init__(self):
        self.registry = CentralizedVehicleRegistry("Central Vehicle Registry (M4)")
        self.registry.authorize_issuer('MFR-1', MANUFACTURER['name'], CIssuerRole.MANUFACTURER, 'LIC-MFR-1')
        self.registry.authorize_issuer('SVC-1', 'Service Center 1', CIssuerRole.SERVICE_CENTER, 'LIC-SVC-1')
        self.owners = ['OWNER-A', 'OWNER-B']
        self.last_receipt = None

    def birth(self, vin: str, first_owner_index: int = 0) -> str:
        cert = self.registry.register_vehicle_birth(
            vin=vin, manufacturer=MANUFACTURER['name'], make=VEHICLE['make'], model=VEHICLE['model'],
            year=VEHICLE['year'], color=VEHICLE['color'], first_owner=self.owners[first_owner_index],
            manufacturer_id='MFR-1')
        return f"vehicle_{cert.certificate_id}"

    def lifecycle_event(self, handle: str, odometer: int, data: Dict[str, Any]):
        return self.registry.record_lifecycle_event(
            handle, CEventType.MAINTENANCE, 'SVC-1', odometer, data, JURISDICTION)

    def transfer(self, handle: str, odometer: int):
        current = self.registry.current_owners[handle]
        new = self.owners[1] if current == self.owners[0] else self.owners[0]
        return self.registry.transfer_ownership(handle, new, odometer, 0.0, AUTHORITY)

    def history(self, handle: str) -> Dict[str, Any]:
        return self.registry.get_vehicle_history(handle)

    def history_unserialised(self, handle: str) -> Dict[str, Any]:
        """
        POST-HOC DIAGNOSTIC (M4): the same history as `history` but returning the
        registry's record objects instead of `to_dict()` copies, to separate
        the cost of `dataclasses.asdict` serialisation from the lookup itself.
        Not a registry API; not part of the pre-registered comparison.
        """
        r = self.registry
        events = r.lifecycle_events[handle]
        transfers = r.ownership_history[handle]
        return {'birth_certificate': r.birth_certificates[handle], 'current_owner': r.current_owners[handle],
                'lifecycle_events': list(events), 'ownership_history': list(transfers),
                'event_count': len(events), 'transfer_count': len(transfers)}

    def current_owner(self, handle: str) -> str:
        return self.registry.current_owners[handle]


# ----------------------------------------------------------------------------
# MOBI-VID-V2 (on chain)
# ----------------------------------------------------------------------------
class MOBIVIDV2LifecycleBackend:
    name = 'mobi_vid_v2'
    is_chain = True

    def __init__(self, rpc_url: str, contract_address: str, abi: List[Dict[str, Any]],
                 seed: str = 'm4', fund_wei: int = 10 ** 19):
        from eth_account import Account
        from web3 import Web3
        from identity.mobi_vid_provider import MOBIVIDProvider

        self.Web3 = Web3
        # The provider's own birth path; deployer (Hardhat #0) = registry authority
        # and the constructor-authorised manufacturer.
        self.provider = MOBIVIDProvider(rpc_url)
        self.w3 = self.provider.w3
        self.provider.contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)
        self.provider.contract_address = self.provider.contract.address
        self.contract = self.provider.contract
        self.authority = self.provider.account

        def acct(tag):
            return Account.from_key(hashlib.sha256(f"{seed}:{tag}".encode()).digest())

        # Test-only deterministic accounts (seeded, as in the harness): one
        # service centre (event issuer) and two owners that hand the vehicle back
        # and forth.
        self.service_center = acct('service-center')
        self.owners = [acct('owner-a'), acct('owner-b')]
        for a in [self.service_center] + self.owners:
            if self.w3.eth.get_balance(a.address) < fund_wei // 2:
                self._send_value(a.address, fund_wei)
        if not self.contract.functions.isAuthorizedIssuer(self.service_center.address,
                                                          V2_EVENT_MAINTENANCE).call():
            self._send(self.contract.functions.authorizeIssuer(self.service_center.address,
                                                               V2_ROLE_SERVICE_CENTER),
                       self.authority, 200_000)
        self._owner_of: Dict[str, int] = {}
        self._history_cache: Dict[str, Dict[str, Any]] = {}
        self.last_receipt = None

    # -- transactions (same pattern as ERC1056Provider._send_tx) ------------
    @staticmethod
    def _raw(signed):
        raw = getattr(signed, 'raw_transaction', None)
        return raw if raw is not None else signed.rawTransaction

    def _send(self, fn, sender, gas: int):
        tx = fn.build_transaction({'from': sender.address,
                                   'nonce': self.w3.eth.get_transaction_count(sender.address),
                                   'gas': gas, 'gasPrice': self.w3.eth.gas_price})
        receipt = self.w3.eth.wait_for_transaction_receipt(
            self.w3.eth.send_raw_transaction(self._raw(sender.sign_transaction(tx))))
        if receipt.status != 1:
            raise RuntimeError(f"transaction reverted: {receipt.transactionHash.hex()}")
        self.last_receipt = receipt
        return receipt

    def _send_value(self, to: str, wei: int):
        a = self.authority
        tx = {'to': to, 'value': wei, 'gas': 21000, 'gasPrice': self.w3.eth.gas_price,
              'nonce': self.w3.eth.get_transaction_count(a.address), 'chainId': self.w3.eth.chain_id}
        r = self.w3.eth.wait_for_transaction_receipt(self.w3.eth.send_raw_transaction(self._raw(a.sign_transaction(tx))))
        if r.status != 1:
            raise RuntimeError("funding failed")

    # -- the four operations -----------------------------------------------
    def birth(self, vin: str, first_owner_index: int = 0) -> str:
        """MOBIVIDProvider.register_vehicle_birth (VIN hash + AES-GCM VIN, one tx)."""
        cred = self.provider.register_vehicle_birth(
            vin=vin, manufacturer_data=MANUFACTURER, vehicle_data=VEHICLE,
            first_owner_address=self.owners[first_owner_index].address)
        identity = self.Web3.to_checksum_address(cred.credential_data['vehicle_identity'])
        self._owner_of[identity] = first_owner_index
        self.last_receipt = None
        self._birth_tx = cred.credential_data['blockchain_tx']
        return identity

    def birth_receipt(self):
        """Receipt of the last birth (the provider does not expose it; fetched untimed)."""
        return self.w3.eth.get_transaction_receipt(self._birth_tx)

    def lifecycle_event(self, handle: str, odometer: int, data: Dict[str, Any]):
        body = json.dumps(data, sort_keys=True).encode()
        data_hash = hashlib.sha256(body).digest()
        credential_hash = hashlib.sha256(b'vc:' + body).digest()
        return self._send(self.contract.functions.recordLifecycleEvent(
            handle, V2_EVENT_MAINTENANCE, int(odometer), data_hash, credential_hash, JURISDICTION),
            self.service_center, 400_000)

    def transfer(self, handle: str, odometer: int):
        cur = self._owner_of.get(handle, 0)
        new = 1 - cur
        r = self._send(self.contract.functions.transferVehicleOwnership(
            handle, self.owners[new].address, int(odometer), AUTHORITY),
            self.owners[cur], 400_000)
        self._owner_of[handle] = new
        return r

    # -- history ----------------------------------------------------------
    def _read_chain_history(self, handle: str) -> Dict[str, Any]:
        c = self.contract.functions
        birth, owner, revoked, transfer_count = c.getVehicleInfo(handle).call()
        event_ids = c.getVehicleEvents(handle).call()
        events = [c.getEvent(handle, eid).call() for eid in event_ids]
        transfers = c.getOwnershipHistory(handle).call() if transfer_count else []
        return {'birth': birth, 'owner': owner, 'revoked': revoked, 'events': events, 'transfers': transfers}

    @staticmethod
    def _render(handle: str, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Same shape as CentralizedVehicleRegistry.get_vehicle_history."""
        b = raw['birth']   # VehicleBirth tuple
        birth = {'vehicle_identity': handle, 'vin_hash': bytes(b[0]).hex(), 'encrypted_vin': b[1],
                 'birth_cert_hash': bytes(b[2]).hex(), 'timestamp': int(b[3]), 'manufacturer': b[4],
                 'first_owner': b[5], 'block_number': int(b[6])}
        events = [{'event_id': bytes(e[0]).hex(), 'event_type': int(e[1]), 'issuer': e[2],
                   'timestamp': int(e[3]), 'odometer': int(e[4]), 'data_hash': bytes(e[5]).hex(),
                   'credential_hash': bytes(e[6]).hex(), 'verified': bool(e[7]), 'jurisdiction': e[8],
                   'block_number': int(e[9])} for e in raw['events']]
        transfers = [{'from_owner': t[0], 'to_owner': t[1], 'timestamp': int(t[2]), 'block_number': int(t[3]),
                      'odometer': int(t[4]), 'authority': t[5]} for t in raw['transfers']]
        return {'birth_certificate': birth, 'current_owner': raw['owner'], 'revoked': bool(raw['revoked']),
                'lifecycle_events': events, 'ownership_history': transfers,
                'event_count': len(events), 'transfer_count': len(transfers)}

    def history(self, handle: str) -> Dict[str, Any]:
        """Uncached: every field read from the chain (3 + events eth_calls)."""
        return self._render(handle, self._read_chain_history(handle))

    def refresh_history_cache(self, handle: str) -> None:
        self._history_cache[handle] = self._read_chain_history(handle)

    def history_cached(self, handle: str) -> Dict[str, Any]:
        """Served from the local copy of the chain history; no chain contact."""
        return self._render(handle, self._history_cache[handle])

    def history_cached_validated(self, handle: str) -> Dict[str, Any]:
        """Local copy after a staleness probe (2 eth_calls); re-reads the chain if it changed."""
        raw = self._history_cache.get(handle)
        c = self.contract.functions
        n_events = c.vehicleEventCount(handle).call()
        n_transfers = c.getOwnershipHistoryCount(handle).call()
        if raw is None or n_events != len(raw['events']) or n_transfers != len(raw['transfers']):
            raw = self._history_cache[handle] = self._read_chain_history(handle)
        return self._render(handle, raw)

    def current_owner(self, handle: str) -> str:
        return self.contract.functions.identityOwner(handle).call()
