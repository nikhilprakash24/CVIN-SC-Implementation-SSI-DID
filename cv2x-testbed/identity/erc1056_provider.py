"""
ERC-1056 DID Provider for Connected Vehicles

Lightweight Ethereum-based Decentralized Identifier system.

Features:
- Real blockchain interaction (not simulated)
- Gas cost tracking
- Event-based DID document resolution
- Key rotation support
- Revocation on-chain
"""

import time
import json
import hashlib
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
from eth_account import Account
from web3 import Web3

try:  # web3 >= 7 renamed the PoA middleware
    from web3.middleware import ExtraDataToPOAMiddleware as _poa_middleware
except ImportError:  # web3 < 7
    from web3.middleware import geth_poa_middleware as _poa_middleware

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

from identity.base import (
    IdentityProvider,
    IdentityType,
    IdentityMetrics,
    VehicleCredential
)


class ERC1056Provider(IdentityProvider):
    """
    ERC-1056 Decentralized Identity Provider.

    This provider interacts with a real ERC-1056 smart contract
    deployed on Ethereum (or compatible chain).
    """

    def __init__(
        self,
        web3_provider_url: str = "http://127.0.0.1:8545",
        contract_address: Optional[str] = None,
        private_key: Optional[str] = None
    ):
        super().__init__(IdentityType.ERC1056_DID)

        # Connect to blockchain
        self.w3 = Web3(Web3.HTTPProvider(web3_provider_url))

        # Add PoA middleware for some chains (Ganache, etc.)
        try:
            self.w3.middleware_onion.inject(_poa_middleware, layer=0)
        except Exception:
            pass

        if not self.w3.is_connected():
            raise ConnectionError(f"Cannot connect to blockchain at {web3_provider_url}")

        # Account for transactions
        if private_key:
            self.account = Account.from_key(private_key)
        else:
            # Use first account from local node
            self.account = Account.from_key(
                "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"  # Hardhat default
            )

        # Contract
        self.contract_address = contract_address
        self.contract = None

        if contract_address:
            self._load_contract(contract_address)

        # Local storage (for performance)
        self.vehicles = {}  # vehicle_id -> vehicle data
        self.did_cache = {}  # DID -> resolved document (TTL cache)

        # Receipt of the most recent state-changing transaction (exact gasUsed,
        # tx hash, block number). Set by register/revoke/update; None otherwise.
        self.last_receipt = None

        # ERC-1056 attribute name under which registerVehicle() stores the key
        self.KEY_ATTRIBUTE_NAME = bytes(Web3.keccak(text="did/pub/secp256k1/veriKey/base64"))

        # Update metrics
        self.metrics.signature_algorithm = "ECDSA-secp256k1"
        self.metrics.key_size_bits = 256
        self.metrics.revocation_mechanism = "blockchain_registry"
        self.metrics.pseudonymity_support = False  # Can be added with multiple DIDs
        self.metrics.single_point_of_failure = False  # Decentralized
        self.metrics.availability_percentage = 99.0  # Blockchain uptime

    def _load_contract(self, address: str):
        """Load contract ABI and create contract instance"""
        # Load ABI from compiled contract
        try:
            with open('contracts/ERC1056Registry_abi.json', 'r') as f:
                abi = json.load(f)
        except FileNotFoundError:
            # Inline ABI for bootstrapping
            abi = self._get_inline_abi()

        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=abi
        )

    def _get_inline_abi(self) -> list:
        """Get inline ABI (simplified)"""
        return [
            {
                "inputs": [{"internalType": "address", "name": "vehicleIdentity", "type": "address"},
                          {"internalType": "bytes", "name": "publicKey", "type": "bytes"}],
                "name": "registerVehicle",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "address", "name": "identity", "type": "address"}],
                "name": "revokeIdentity",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "address", "name": "identity", "type": "address"}],
                "name": "isRevoked",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "address", "name": "identity", "type": "address"}],
                "name": "getIdentityInfo",
                "outputs": [
                    {"internalType": "address", "name": "owner", "type": "address"},
                    {"internalType": "uint256", "name": "lastChangedBlock", "type": "uint256"},
                    {"internalType": "bool", "name": "isRevoked", "type": "bool"},
                    {"internalType": "uint256", "name": "revokedTimestamp", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "identity", "type": "address"},
                    {"internalType": "bytes32", "name": "name", "type": "bytes32"},
                    {"internalType": "bytes", "name": "value", "type": "bytes"},
                    {"internalType": "uint256", "name": "validity", "type": "uint256"}
                ],
                "name": "setAttribute",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

    # ------------------------------------------------------------------
    # Transaction helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _raw_tx(signed):
        """eth-account >= 0.13 renamed rawTransaction -> raw_transaction."""
        raw = getattr(signed, 'raw_transaction', None)
        if raw is None:
            raw = signed.rawTransaction
        return raw

    @staticmethod
    def vehicle_account(vehicle_id: str):
        """
        Deterministic Ethereum account for a vehicle (the DID subject / controller).

        ERC1056Registry guards registerVehicle/updateVehicleKey/revokeIdentity with
        onlyOwner(identity, msg.sender); identityOwner() defaults to the identity
        itself, so these transactions must be signed by this account.
        """
        return Account.from_key(hashlib.sha256(vehicle_id.encode()).digest())

    def _send_tx(self, contract_fn, sender, gas: int):
        """
        Build, sign, send and confirm a contract call from `sender` (an eth_account
        LocalAccount). Raises if the transaction reverted. Stores the receipt in
        self.last_receipt (exact gasUsed from the receipt).
        """
        nonce = self.w3.eth.get_transaction_count(sender.address)
        transaction = contract_fn.build_transaction({
            'from': sender.address,
            'nonce': nonce,
            'gas': gas,
            'gasPrice': self.w3.eth.gas_price
        })
        signed = sender.sign_transaction(transaction)
        tx_hash = self.w3.eth.send_raw_transaction(self._raw_tx(signed))
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status != 1:
            raise RuntimeError(f"Transaction {tx_hash.hex()} reverted (status={receipt.status})")
        self.last_receipt = receipt
        return transaction, receipt

    def fund_vehicle_account(self, vehicle_id: str, wei: int) -> dict:
        """
        Transfer `wei` from the provider's funding account to the vehicle's account
        so the vehicle can pay gas for its own registration/rotation/revocation.
        Provisioning step; not part of any identity operation.
        """
        vehicle = self.vehicle_account(vehicle_id)
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        tx = {
            'to': vehicle.address,
            'value': wei,
            'gas': 21000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': nonce,
            'chainId': self.w3.eth.chain_id,
        }
        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(self._raw_tx(signed))
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status != 1:
            raise RuntimeError(f"Funding transaction {tx_hash.hex()} failed")
        return receipt

    def deploy_contract(self) -> str:
        """
        Deploy ERC-1056 registry contract.

        Returns contract address.
        """
        print("Deploying ERC-1056 Registry contract...")

        # Load bytecode
        try:
            with open('contracts/ERC1056Registry_bytecode.txt', 'r') as f:
                bytecode = f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(
                "Contract bytecode not found. Please compile contract first:\n"
                "  npx hardhat compile"
            )

        # Create contract
        Contract = self.w3.eth.contract(
            abi=self._get_inline_abi(),
            bytecode=bytecode
        )

        # Build transaction
        transaction = Contract.constructor().build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 3000000,
            'gasPrice': self.w3.eth.gas_price
        })

        # Sign and send
        signed = self.account.sign_transaction(transaction)
        tx_hash = self.w3.eth.send_raw_transaction(self._raw_tx(signed))

        # Wait for receipt
        print(f"Transaction sent: {tx_hash.hex()}")
        print("Waiting for confirmation...")

        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        contract_address = receipt.contractAddress
        print(f"✓ Contract deployed at: {contract_address}")
        print(f"  Gas used: {receipt.gasUsed}")

        # Load contract
        self._load_contract(contract_address)
        self.contract_address = contract_address

        return contract_address

    def register_vehicle(self, vehicle_id: str, metadata: Dict = None) -> VehicleCredential:
        """Register vehicle on blockchain"""
        start_time = time.time()

        if not self.contract:
            raise ValueError("Contract not deployed or loaded")

        # Generate keypair
        private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
        public_key = private_key.public_key()

        # Derive Ethereum address from vehicle_id (deterministic for testing)
        vehicle_account = self.vehicle_account(vehicle_id)
        vehicle_address = vehicle_account.address

        # Get public key bytes
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )

        # registerVehicle() is onlyOwner(identity, msg.sender): the vehicle
        # registers itself, so the tx is signed by the vehicle account (which
        # must hold ETH for gas; see fund_vehicle_account()).
        transaction, receipt = self._send_tx(
            self.contract.functions.registerVehicle(
                Web3.to_checksum_address(vehicle_address),
                public_key_bytes
            ),
            vehicle_account,
            gas=200000,
        )
        tx_hash = receipt.transactionHash

        # Calculate gas cost (in ETH)
        gas_used = receipt.gasUsed
        gas_price = transaction['gasPrice']
        cost_wei = gas_used * gas_price
        cost_eth = self.w3.from_wei(cost_wei, 'ether')

        # Create DID
        chain_id = self.w3.eth.chain_id
        did = f"did:ethr:0x{chain_id:x}:{vehicle_address}"

        # Store locally
        self.vehicles[vehicle_id] = {
            'did': did,
            'address': vehicle_address,
            'private_key': private_key,
            'public_key': public_key,
            'metadata': metadata or {},
            'registered_at': datetime.utcnow().isoformat(),
            'tx_hash': tx_hash.hex(),
            'block_number': receipt.blockNumber
        }

        # Create credential
        credential = VehicleCredential(
            vehicle_id=vehicle_id,
            public_key=public_key_bytes.hex(),
            credential_data={
                'did': did,
                'address': vehicle_address,
                'chain_id': chain_id,
                'contract_address': self.contract_address
            },
            signature="",
            issuer=f"ERC1056Registry@{self.contract_address}",
            issued_at=int(time.time()),
            expires_at=int((datetime.utcnow() + timedelta(days=365)).timestamp())
        )

        # Update metrics
        elapsed = (time.time() - start_time) * 1000
        self.metrics.registration_time_ms = (
            (self.metrics.registration_time_ms * self._operation_count + elapsed) /
            (self._operation_count + 1)
        )
        self.metrics.registration_cost = float(cost_eth)
        self.metrics.gas_used = gas_used
        self._operation_count += 1

        return credential

    def sign_message(self, vehicle_id: str, message: Dict) -> Dict:
        """Sign message with vehicle's private key"""
        start_time = time.time()

        if vehicle_id not in self.vehicles:
            raise ValueError(f"Vehicle {vehicle_id} not registered")

        vehicle = self.vehicles[vehicle_id]

        # Serialize message
        message_bytes = json.dumps(message, sort_keys=True).encode()

        # Sign with private key
        signature = vehicle['private_key'].sign(
            message_bytes,
            ec.ECDSA(hashes.SHA256())
        )

        # Create signed message
        signed_message = {
            'message': message,
            'signature': signature.hex(),
            'did': vehicle['did'],
            'timestamp': datetime.utcnow().isoformat(),
            'identity_type': 'erc1056_did'
        }

        # Update metrics
        elapsed = (time.time() - start_time) * 1000
        self.metrics.authentication_time_ms = elapsed
        self.metrics.signature_size = len(signature)

        return signed_message

    def verify_message(self, signed_message: Dict) -> Tuple[bool, IdentityMetrics]:
        """Verify signed message"""
        start_time = time.time()
        metrics = IdentityMetrics()

        try:
            # Extract components
            message = signed_message['message']
            signature = bytes.fromhex(signed_message['signature'])
            did = signed_message['did']

            # Parse DID to get address
            # Format: did:ethr:0x{chain_id}:{address}
            parts = did.split(':')
            if len(parts) != 4 or parts[0] != 'did' or parts[1] != 'ethr':
                return False, metrics

            vehicle_address = parts[3]

            # Resolve DID (get public key from blockchain)
            resolution_start = time.time()
            identity_data, resolution_time = self.resolve_identity_from_address(vehicle_address)
            metrics.resolution_time_ms = resolution_time

            if not identity_data:
                return False, metrics

            # Check revocation
            is_revoked, check_time = self.check_revocation_status_by_address(vehicle_address)
            if is_revoked:
                metrics.verification_time_ms = (time.time() - start_time) * 1000
                return False, metrics

            # Get public key (resolved from DIDAttributeChanged events)
            if not identity_data.get('public_key'):
                metrics.verification_time_ms = (time.time() - start_time) * 1000
                return False, metrics
            public_key_bytes = bytes.fromhex(identity_data['public_key'])
            public_key = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256K1(),
                public_key_bytes
            )

            # Verify signature
            message_bytes = json.dumps(message, sort_keys=True).encode()
            public_key.verify(
                signature,
                message_bytes,
                ec.ECDSA(hashes.SHA256())
            )

            # Success
            elapsed = (time.time() - start_time) * 1000
            metrics.verification_time_ms = elapsed
            self.metrics.verification_time_ms = (
                (self.metrics.verification_time_ms * self._operation_count + elapsed) /
                (self._operation_count + 1)
            )

            return True, metrics

        except Exception as e:
            print(f"Verification error: {e}")
            metrics.verification_time_ms = (time.time() - start_time) * 1000
            return False, metrics

    def revoke_credential(self, vehicle_id: str, reason: str = "") -> bool:
        """Revoke vehicle identity on blockchain"""
        start_time = time.time()

        if vehicle_id not in self.vehicles:
            return False

        vehicle = self.vehicles[vehicle_id]
        vehicle_address = vehicle['address']

        # revokeIdentity() is onlyOwner(identity, msg.sender): signed by the
        # vehicle (identity owner) account.
        transaction, receipt = self._send_tx(
            self.contract.functions.revokeIdentity(
                Web3.to_checksum_address(vehicle_address)
            ),
            self.vehicle_account(vehicle_id),
            gas=100000,
        )

        # Update metrics
        gas_used = receipt.gasUsed
        gas_price = transaction['gasPrice']
        cost_eth = self.w3.from_wei(gas_used * gas_price, 'ether')

        elapsed = (time.time() - start_time) * 1000
        self.metrics.revocation_time_ms = elapsed
        self.metrics.revocation_cost = float(cost_eth)

        return receipt.status == 1

    def check_revocation_status(self, vehicle_id: str) -> Tuple[bool, float]:
        """Check if vehicle is revoked"""
        if vehicle_id not in self.vehicles:
            return True, 0.0

        vehicle_address = self.vehicles[vehicle_id]['address']
        return self.check_revocation_status_by_address(vehicle_address)

    def check_revocation_status_by_address(self, address: str) -> Tuple[bool, float]:
        """Check revocation by Ethereum address"""
        start_time = time.time()

        is_revoked = self.contract.functions.isRevoked(
            Web3.to_checksum_address(address)
        ).call()

        elapsed = (time.time() - start_time) * 1000
        return is_revoked, elapsed

    def update_credential(self, vehicle_id: str, updates: Dict) -> bool:
        """
        Update credential.

        `{'rotate_key': True}` publishes a fresh secp256k1 verification key for
        the vehicle on-chain via ERC1056Registry.updateVehicleKey() (a
        DIDAttributeChanged event, signed by the identity owner). This is the
        ERC-1056 counterpart of a CA issuing a new certificate: a new key is
        bound to the identity. Any other keys are stored as local metadata only.
        """
        if vehicle_id not in self.vehicles:
            return False

        vehicle = self.vehicles[vehicle_id]
        updates = dict(updates or {})

        if updates.pop('rotate_key', False):
            new_private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
            new_public_key_bytes = new_private_key.public_key().public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            )
            self._send_tx(
                self.contract.functions.updateVehicleKey(
                    Web3.to_checksum_address(vehicle['address']),
                    new_public_key_bytes
                ),
                self.vehicle_account(vehicle_id),
                gas=200000,
            )
            vehicle['private_key'] = new_private_key
            vehicle['public_key'] = new_private_key.public_key()

        vehicle['metadata'].update(updates)
        return True

    def get_credential(self, vehicle_id: str) -> Optional[VehicleCredential]:
        """Get vehicle credential"""
        if vehicle_id not in self.vehicles:
            return None

        vehicle = self.vehicles[vehicle_id]

        public_key_bytes = vehicle['public_key'].public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )

        return VehicleCredential(
            vehicle_id=vehicle_id,
            public_key=public_key_bytes.hex(),
            credential_data={
                'did': vehicle['did'],
                'address': vehicle['address'],
            },
            signature="",
            issuer=f"ERC1056Registry@{self.contract_address}",
            issued_at=int(datetime.fromisoformat(vehicle['registered_at']).timestamp()),
            expires_at=0,  # No expiration for DID
            revoked=False  # Would check blockchain in production
        )

    def resolve_identity(self, vehicle_id: str) -> Tuple[Optional[Dict], float]:
        """Resolve DID to get identity document"""
        if vehicle_id not in self.vehicles:
            return None, 0.0

        vehicle_address = self.vehicles[vehicle_id]['address']
        return self.resolve_identity_from_address(vehicle_address)

    def resolve_identity_from_address(self, address: str) -> Tuple[Optional[Dict], float]:
        """Resolve identity from Ethereum address"""
        start_time = time.time()

        try:
            checksum = Web3.to_checksum_address(address)

            # 1 eth_call: registry state for this identity
            owner, last_changed, is_revoked, revoked_at = self.contract.functions.getIdentityInfo(
                checksum
            ).call()

            # ERC-1056 resolution: walk the `previousChange` linked list of
            # blocks (1 eth_getLogs per hop) until the current verification key
            # attribute is found. Same algorithm as ethr-did-resolver.
            public_key_hex, valid_to, hops = self._resolve_key_from_events(checksum, last_changed)

            identity_data = {
                'address': address,
                'owner': owner,
                'last_changed': last_changed,
                'is_revoked': is_revoked,
                'revoked_at': revoked_at,
                'public_key': public_key_hex,   # hex (no 0x), None if not found
                'public_key_valid_to': valid_to,
                'resolution_hops': hops,
            }

            elapsed = (time.time() - start_time) * 1000
            return identity_data, elapsed

        except Exception as e:
            print(f"Resolution error: {e}")
            return None, (time.time() - start_time) * 1000

    def _resolve_key_from_events(self, checksum_address: str, last_changed: int,
                                 max_hops: int = 64):
        """
        Follow the ERC-1056 change chain backwards from block `last_changed`
        and return (public_key_hex, valid_to, hops) for the newest still-valid
        key attribute, or (None, None, hops) if none exists.
        """
        identity_topic = '0x' + checksum_address[2:].lower().rjust(64, '0')
        events = {
            self.contract.events.DIDOwnerChanged().topic: self.contract.events.DIDOwnerChanged(),
            self.contract.events.DIDDelegateChanged().topic: self.contract.events.DIDDelegateChanged(),
            self.contract.events.DIDAttributeChanged().topic: self.contract.events.DIDAttributeChanged(),
            self.contract.events.DIDRevoked().topic: self.contract.events.DIDRevoked(),
        }
        now = int(time.time())

        block = int(last_changed)
        hops = 0
        while block > 0 and hops < max_hops:
            hops += 1
            logs = self.w3.eth.get_logs({
                'address': self.contract.address,
                'fromBlock': block,
                'toBlock': block,
                'topics': [None, identity_topic],
            })

            previous_change = None
            found_key = None
            found_valid_to = None
            for raw in logs:
                event = events.get(Web3.to_hex(raw['topics'][0]))
                if event is None:
                    continue
                args = event.process_log(raw)['args']
                if 'previousChange' in args:
                    prev = int(args['previousChange'])
                    previous_change = prev if previous_change is None else min(previous_change, prev)
                if (event.event_name == 'DIDAttributeChanged'
                        and bytes(args['name']) == self.KEY_ATTRIBUTE_NAME
                        and int(args['validTo']) > now):
                    # later logs in the same block supersede earlier ones
                    found_key = bytes(args['value']).hex()
                    found_valid_to = int(args['validTo'])

            if found_key is not None:
                return found_key, found_valid_to, hops

            # DIDRevoked carries no previousChange, so the chain ends there.
            if previous_change is None or previous_change >= block:
                break
            block = previous_change

        return None, None, hops


if __name__ == "__main__":
    print("=== ERC-1056 DID Provider Test ===\n")

    # Note: Requires local blockchain (Hardhat, Ganache, etc.)
    print("Connecting to local blockchain...")

    try:
        provider = ERC1056Provider("http://127.0.0.1:8545")
        print(f"✓ Connected to chain ID: {provider.w3.eth.chain_id}")
        print(f"✓ Account: {provider.account.address}")
        print(f"✓ Balance: {provider.w3.from_wei(provider.w3.eth.get_balance(provider.account.address), 'ether')} ETH")

        # Deploy contract
        print("\nDeploying contract...")
        # contract_address = provider.deploy_contract()

        print("\nTest complete. To run full test, deploy contract first.")

    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nMake sure local blockchain is running:")
        print("  npx hardhat node")
