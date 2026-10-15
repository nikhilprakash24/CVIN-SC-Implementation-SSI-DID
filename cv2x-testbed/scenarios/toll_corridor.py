#!/usr/bin/env python3
"""
Scenario X1: "Endorsed passage, paid write" (docs/research-expansion/IDEAS.md).

One drive through one tolled corridor, end to end, with a mixed fleet:

  SSI lane (DID vehicles)
    1. DMV (official party) issues a RegistrationCredential with selective
       disclosure, and SPONSORS the vehicle's on-chain pseudonym: it relays the
       vehicle's signed ERC-1056 addDelegateSigned(veriKey) meta-transaction and
       pays the gas (the car holds no ETH).
    2. The Transport Ministry issues a CorridorAccessEndorsement VC and signs the
       matching EIP-712 Endorsement whose credentialHash = keccak(canonical VC).
    3. READ at the gantry: the RSU sends a challenge; the vehicle presents a VP
       disclosing only vehicleClass/corridorId and jurisdiction (VIN and plate
       stay hidden); the RSU runs the full W3C verify pipeline offline, binds the
       VC to the on-chain endorsement digest, then calls checkTicket (eth_call).
    4. WRITE: the vehicle's pseudonym key signs an EIP-712 TollTicket; the RSU
       batches tickets into one settleBatch transaction against a stablecoin
       escrow.

  Legacy lane (vehicles without a wallet; the transition period)
    ANPR camera reads the plate; a back-office ledger debits a plate account.
    The same corridor contract is not touched; the operator reconciles both
    lanes into one revenue report.

Outputs per-lane latency, gas, and an exposure count: which identifiers each
lane revealed to the roadside (the privacy cost of staying legacy).

Run as a script against a Hardhat node with compiled artifacts:
    (cd 1_blockchain-identity && npx hardhat compile && npx hardhat node --port 8548 &)
    python3 cv2x-testbed/scenarios/toll_corridor.py --rpc http://127.0.0.1:8548
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from eth_account import Account
from eth_utils import keccak
from web3 import Web3

ROOT = Path(__file__).resolve().parents[2]
VC_DIR = ROOT / "2_w3c-ssi-layer" / "verifiable-credentials"
if str(VC_DIR) not in sys.path:
    sys.path.insert(0, str(VC_DIR))

from vc_issuer import CredentialIssuer, canonicalize  # noqa: E402
from vc_holder import HolderWallet  # noqa: E402
from vc_schemas import PropertySpec, CredentialSchema  # noqa: E402
from vc_verifier import CredentialVerifier, NonceStore, TrustedIssuerRegistry  # noqa: E402

ARTIFACTS = Path(os.environ.get("X1_ARTIFACTS_DIR", ROOT / "1_blockchain-identity" / "artifacts" / "contracts"))

# Hardhat default accounts #0-#4 (public test keys).
HARDHAT_KEYS = [
    "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
    "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
    "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",
    "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6",
    "0x47e179ec197488593b187f80a8eb0da91f1b9813b9f3d1a4d0b7d9f6e2c3e7f9",
]

VERIKEY = b"veriKey".ljust(32, b"\0")
CLASS = {"emergency": 0, "car": 1, "ev": 2, "truck": 3}
FEE = {0: 0, 1: 2_500_000, 2: 1_250_000, 3: 9_000_000}  # 6-decimal cUSD
CORRIDOR_ID = "BC-HWY-99-NB"
ENDORSEMENT_TYPE = "CorridorAccessEndorsement"

# Scenario-local schema; not added to the core 10-schema registry.
ENDORSEMENT_SCHEMA = CredentialSchema(
    ENDORSEMENT_TYPE,
    "Ministry endorsement admitting a vehicle DID to a tolled corridor at a class.",
    [
        PropertySpec("vehicleClass", (str,), True, lambda v: v in CLASS),
        PropertySpec("corridorId", (str,), True),
        PropertySpec("sponsorDid", (str,), True),
    ],
)

ENDORSEMENT_TYPES = {
    "Endorsement": [
        {"name": "subject", "type": "address"},
        {"name": "vehicleClass", "type": "uint8"},
        {"name": "validUntil", "type": "uint64"},
        {"name": "credentialHash", "type": "bytes32"},
    ]
}
TICKET_TYPES = {
    "TollTicket": [
        {"name": "identity", "type": "address"},
        {"name": "gantry", "type": "address"},
        {"name": "nonce", "type": "uint64"},
        {"name": "maxFee", "type": "uint128"},
        {"name": "deadline", "type": "uint64"},
        {"name": "endorsementHash", "type": "bytes32"},
    ]
}


def _artifact(name: str) -> dict:
    for p in ARTIFACTS.rglob(f"{name}.json"):
        if not p.name.endswith(".dbg.json"):
            return json.loads(p.read_text())
    raise FileNotFoundError(f"{name}.json under {ARTIFACTS} (run `npx hardhat compile` in 1_blockchain-identity)")


def _sign_hash(key: str, digest: bytes):
    fn = getattr(Account, "unsafe_sign_hash", None) or getattr(Account, "signHash")
    return fn(digest, private_key=key)


@dataclass
class Vehicle:
    name: str
    vehicle_class: str
    plate: str
    vin: str
    legacy: bool = False
    account: Any = None          # DID controller key (did:ethr address)
    pseudonym: Any = None        # rotating veriKey delegate
    wallet: Optional[HolderWallet] = None
    endorsement_cid: Optional[str] = None
    registration_cid: Optional[str] = None
    endorsement: Optional[dict] = None
    endorsement_sig: Optional[bytes] = None


@dataclass
class LaneReport:
    vehicles: int = 0
    admitted: int = 0
    denied: Dict[str, str] = field(default_factory=dict)
    read_ms: List[float] = field(default_factory=list)
    identifiers_exposed: Dict[str, List[str]] = field(default_factory=dict)
    revenue: int = 0


class TollCorridorScenario:
    def __init__(self, rpc_url: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 30}))
        if not self.w3.is_connected():
            raise ConnectionError(f"no node at {rpc_url}")
        self.authority, self.ministry_key, self.dmv_key, self.gantry_key, _ = (
            Account.from_key(k) for k in HARDHAT_KEYS)
        self.chain_id = self.w3.eth.chain_id
        did_chain = hex(self.chain_id)
        # Off-chain issuers share their on-chain keys (one DID, two proof formats).
        self.ministry = CredentialIssuer.with_ethr_did(private_key=self.ministry_key.key, chain_id=did_chain)
        self.dmv = CredentialIssuer.with_ethr_did(private_key=self.dmv_key.key, chain_id=did_chain)
        self.gas: Dict[str, int] = {}
        self.legacy_ledger: Dict[str, int] = {}
        self.legacy_revenue = 0

    # ------------------------------------------------------------ chain I/O
    def _send(self, acct, fn, label: Optional[str] = None):
        tx = fn.build_transaction({
            "from": acct.address, "nonce": self.w3.eth.get_transaction_count(acct.address),
            "gas": 8_000_000, "gasPrice": self.w3.eth.gas_price, "chainId": self.chain_id})
        signed = acct.sign_transaction(tx)
        raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
        rc = self.w3.eth.wait_for_transaction_receipt(self.w3.eth.send_raw_transaction(raw))
        if rc.status != 1:
            raise RuntimeError(f"tx reverted: {label}")
        if label:
            self.gas[label] = self.gas.get(label, 0) + rc.gasUsed
        return rc

    def _deploy(self, name: str, *args):
        art = _artifact(name)
        c = self.w3.eth.contract(abi=art["abi"], bytecode=art["bytecode"])
        rc = self._send(self.authority, c.constructor(*args), f"deploy:{name}")
        return self.w3.eth.contract(address=rc.contractAddress, abi=art["abi"])

    def deploy(self):
        self.registry = self._deploy("EthereumDIDRegistry")
        self.stable = self._deploy("CVINTestStable")
        self.corridor = self._deploy("CVINTollCorridor", self.stable.address, self.registry.address)
        self.domain = {"name": "CVINTollCorridor", "version": "1",
                       "chainId": self.chain_id, "verifyingContract": self.corridor.address}
        f = self.corridor.functions
        self._send(self.authority, f.setIssuer(self.ministry_key.address, True))
        self._send(self.authority, f.setGantry(self.gantry_key.address, True))
        for cls, fee in FEE.items():
            self._send(self.authority, f.setFee(cls, fee))
        # The operator pre-funds escrow for the demo fleet (stands in for card top-ups / permits).
        self._send(self.authority, self.stable.functions.mint(self.authority.address, 10**12))
        self._send(self.authority, self.stable.functions.approve(self.corridor.address, 2**256 - 1))

    # ------------------------------------------------------------ onboarding
    def onboard(self, v: Vehicle, escrow: int = 20_000_000, pseudonym_ttl_s: int = 300):
        if v.legacy:
            self.legacy_ledger[v.plate] = escrow
            return
        v.account = Account.create()
        v.pseudonym = Account.create()
        did = f"did:ethr:{hex(self.chain_id)}:{v.account.address}"
        v.wallet = HolderWallet(did, private_key=v.account.key)

        # DMV registration VC (selective disclosure: VIN/plate hidden by default).
        reg = self.dmv.issue_credential("RegistrationCredential", did, {
            "vin": v.vin, "registrationAuthorityDid": self.dmv.issuer_did, "ownerDid": did,
            "jurisdiction": "BC-CAN", "plateNumber": v.plate, "registrationDate": "2026-01-15",
        }, selective_disclosure=True)
        v.registration_cid = v.wallet.store_credential(reg)

        # DMV sponsors the pseudonym delegate: vehicle signs, DMV relays and pays.
        reg_addr = Web3.to_checksum_address(self.registry.address)
        nonce = self.registry.functions.nonce(v.account.address).call()
        digest = keccak(b"\x19\x00" + bytes.fromhex(reg_addr[2:]) + nonce.to_bytes(32, "big")
                        + bytes.fromhex(v.account.address[2:]) + b"addDelegate" + VERIKEY
                        + bytes.fromhex(v.pseudonym.address[2:]) + pseudonym_ttl_s.to_bytes(32, "big"))
        s = _sign_hash(v.account.key, digest)
        self._send(self.dmv_key, self.registry.functions.addDelegateSigned(
            v.account.address, s.v, s.r.to_bytes(32, "big"), s.s.to_bytes(32, "big"),
            VERIKEY, v.pseudonym.address, pseudonym_ttl_s), "sponsor:addDelegateSigned")

        # Ministry endorsement: VC off-chain + EIP-712 twin on-chain-verifiable.
        claims = {"vehicleClass": v.vehicle_class, "corridorId": CORRIDOR_ID, "sponsorDid": self.dmv.issuer_did}
        ok, errs = ENDORSEMENT_SCHEMA.validate(claims)
        assert ok, errs
        env = self.ministry.issue_credential(ENDORSEMENT_TYPE, did, claims, validity_days=30,
                                             selective_disclosure=True, enforce_schema=False)
        v.endorsement_cid = v.wallet.store_credential(env)
        vc = env["verifiableCredential"]
        v.endorsement = {
            "subject": v.account.address, "vehicleClass": CLASS[v.vehicle_class],
            "validUntil": int(time.time()) + 30 * 86400,
            "credentialHash": keccak(canonicalize(vc)),
        }
        v.endorsement_sig = Account.sign_typed_data(
            self.ministry_key.key, self.domain, ENDORSEMENT_TYPES, v.endorsement).signature

        self._send(self.authority, self.corridor.functions.deposit(v.account.address, escrow), "escrow:deposit")

    # ------------------------------------------------------------ gate
    def _endorsement_tuple(self, v: Vehicle):
        e = v.endorsement
        return (e["subject"], e["vehicleClass"], e["validUntil"], e["credentialHash"])

    def gate_read(self, v: Vehicle, verifier: CredentialVerifier, nonces: NonceStore,
                  rep: LaneReport, ticket_nonce: int):
        """Off-chain VP verify + VC↔endorsement binding + on-chain checkTicket. Returns a ticket or None."""
        t0 = time.perf_counter()
        challenge = nonces.issue()
        vp = v.wallet.create_presentation(
            [v.endorsement_cid, v.registration_cid], challenge, CORRIDOR_ID,
            disclose_claims={v.endorsement_cid: ["vehicleClass", "corridorId"],
                             v.registration_cid: ["jurisdiction"]})
        ok, report = verifier.verify_presentation(vp, challenge, CORRIDOR_ID)
        if not ok:
            rep.denied[v.name] = "vp_invalid"
            return None
        creds = vp["verifiableCredential"]
        endo_vc = next(c for c in creds if ENDORSEMENT_TYPE in c["type"])
        disclosed_class = endo_vc["disclosedClaims"]["vehicleClass"]["value"]
        signed_vc = {k: val for k, val in endo_vc.items() if k != "disclosedClaims"}
        if keccak(canonicalize(signed_vc)) != v.endorsement["credentialHash"] \
                or CLASS[disclosed_class] != v.endorsement["vehicleClass"]:
            rep.denied[v.name] = "vc_endorsement_mismatch"
            return None

        ticket = {"identity": v.account.address, "gantry": self.gantry_key.address, "nonce": ticket_nonce,
                  "maxFee": 10_000_000, "deadline": int(time.time()) + 600,
                  "endorsementHash": self.corridor.functions.hashEndorsement(self._endorsement_tuple(v)).call()}
        sig = Account.sign_typed_data(v.pseudonym.key, self.domain, TICKET_TYPES, ticket).signature
        t_tuple = tuple(ticket[k["name"]] for k in TICKET_TYPES["TollTicket"])
        code, fee, _ = self.corridor.functions.checkTicket(
            self._endorsement_tuple(v), v.endorsement_sig, t_tuple, sig, self.gantry_key.address).call()
        rep.read_ms.append((time.perf_counter() - t0) * 1000)
        if code != 0:
            rep.denied[v.name] = f"onchain_code_{code}"
            return None
        # The DID address is in the ticket and in the TollPaid event: trips stay linkable
        # across gantries even though the signing pseudonym rotates (open problem -> Phase 2 ZK).
        rep.identifiers_exposed[v.name] = ["did_address(linkable, on-chain)", "pseudonym_address", "vehicleClass", "jurisdiction"]
        return (self._endorsement_tuple(v), v.endorsement_sig, t_tuple, sig, fee)

    def legacy_gate(self, v: Vehicle, rep: LaneReport):
        # No ANPR model is run, so no legacy read latency is reported (would be a dict lookup).
        bal = self.legacy_ledger.get(v.plate)
        fee = FEE[CLASS[v.vehicle_class]]
        rep.identifiers_exposed[v.name] = ["plate", "image", "vehicleClass(camera)", "timestamp+location"]
        if bal is None or bal < fee:
            rep.denied[v.name] = "no_plate_account"
            return
        self.legacy_ledger[v.plate] = bal - fee
        rep.revenue += fee
        rep.admitted += 1

    # ------------------------------------------------------------ run
    def run(self, fleet: List[Vehicle], revoke_offchain: Optional[str] = None,
            revoke_onchain: Optional[str] = None) -> Dict[str, Any]:
        for v in fleet:
            self.onboard(v)
        if revoke_offchain:
            v = next(x for x in fleet if x.name == revoke_offchain)
            self.dmv.revoke_credential(v.wallet.get_credential(v.registration_cid)["id"], "registration suspended")
        if revoke_onchain:
            v = next(x for x in fleet if x.name == revoke_onchain)
            self._send(self.authority, self.corridor.functions.revokeEndorsement(
                self._endorsement_tuple(v), v.endorsement_sig), "revokeEndorsement")

        tir = TrustedIssuerRegistry()
        for iss in (self.ministry, self.dmv):
            tir.register(iss.issuer_did, iss.address)
        nonces = NonceStore(ttl_s=60)
        verifier = CredentialVerifier(
            revocation_registry=[self.ministry.revocation_registry, self.dmv.revocation_registry],
            trusted_issuers=tir, nonce_store=nonces)

        ssi, legacy = LaneReport(), LaneReport()
        batch = []
        for i, v in enumerate(fleet):
            if v.legacy:
                legacy.vehicles += 1
                self.legacy_gate(v, legacy)
                continue
            ssi.vehicles += 1
            item = self.gate_read(v, verifier, nonces, ssi, ticket_nonce=i + 1)
            if item:
                batch.append(item)

        settle_gas = None
        if batch:
            es, isg, ts, vs, fees = zip(*batch)
            rc = self._send(self.gantry_key, self.corridor.functions.settleBatch(
                list(es), list(isg), list(ts), list(vs)), "settleBatch")
            settle_gas = rc.gasUsed
            ssi.admitted = len(batch)
            ssi.revenue = sum(fees)

        treasury = self.corridor.functions.treasury().call()
        assert treasury == ssi.revenue, (treasury, ssi.revenue)

        def lane(r: LaneReport):
            return {
                "vehicles": r.vehicles, "admitted": r.admitted, "denied": r.denied,
                "read_ms_median": round(statistics.median(r.read_ms), 3) if r.read_ms else None,
                "revenue_cusd": r.revenue / 1e6,
                "identifiers_exposed": r.identifiers_exposed,
            }

        return {
            "scenario": "X1 endorsed passage, paid write",
            "corridor": CORRIDOR_ID,
            "condition": "M1 Hardhat node over HTTP; read_ms includes VP verify + eth_call; host-dependent",
            "ssi_lane": lane(ssi),
            "legacy_lane": lane(legacy),
            "reconciled_revenue_cusd": (ssi.revenue + legacy.revenue) / 1e6,
            "gas": {"settleBatch": settle_gas,
                    "settle_per_ticket": round(settle_gas / len(batch)) if batch else None,
                    "sponsor_addDelegateSigned_total": self.gas.get("sponsor:addDelegateSigned"),
                    "escrow_deposit_total": self.gas.get("escrow:deposit")},
        }


def demo_fleet() -> List[Vehicle]:
    return [
        Vehicle("ev-1", "ev", "BC-EV-001", "5YJ3E1EA0PF000001"),
        Vehicle("car-2", "car", "BC-CAR-002", "1HGCM82633A000002"),
        Vehicle("truck-3", "truck", "BC-TRK-003", "1FUJGLDR0CL000003"),
        Vehicle("ambulance-4", "emergency", "BC-EMS-004", "1FDXE45P05H000004"),
        Vehicle("suspended-5", "car", "BC-CAR-005", "2T1BURHE0JC000005"),
        Vehicle("revoked-6", "car", "BC-CAR-006", "3VWFE21C04M000006"),
        Vehicle("legacy-7", "car", "BC-OLD-007", "1G1ZT51816F000007", legacy=True),
        Vehicle("legacy-8", "truck", "BC-OLD-008", "1M2AX07C5EM000008", legacy=True),
    ]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--rpc", default=os.environ.get("CV2X_TEST_RPC_URL", "http://127.0.0.1:8545"))
    ap.add_argument("--out", default=str(ROOT / "cv2x-testbed" / "results" / "x1_toll_corridor.json"))
    args = ap.parse_args(argv)
    sc = TollCorridorScenario(args.rpc)
    sc.deploy()
    result = sc.run(demo_fleet(), revoke_offchain="suspended-5", revoke_onchain="revoked-6")
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
