"""
Helpers for the on-chain resolver tests (stream H-R): artifact paths, the node
port, deploy/send. Fixtures live in conftest.py; test modules import these
helpers by this unique module name (two conftest modules exist in a full
`pytest 2_w3c-ssi-layer cv2x-testbed/tests` run, so `from conftest import`
would be ambiguous).
"""

import json
import os
import socket
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HARDHAT_DIR = REPO_ROOT / "1_blockchain-identity"
ARTIFACTS = HARDHAT_DIR / "artifacts" / "contracts"
ERC1056_ARTIFACT = ARTIFACTS / "ERC1056" / "EthereumDIDRegistry.sol" / \
    "EthereumDIDRegistry.json"
MOBI_ARTIFACT = ARTIFACTS / "MOBI" / "MOBIVIDRegistryV2.sol" / \
    "MOBIVIDRegistryV2.json"
RPC_PORT = int(os.environ.get("DID_RESOLVER_TEST_RPC_PORT", "8560"))
RPC_URL = f"http://127.0.0.1:{RPC_PORT}"
HARDHAT_CHAIN_ID = 31337  # 0x7a69


def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def free_port() -> int:
    """A local TCP port with nothing listening (for the RPC-down tests)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def deploy(w3, artifact: Path, sender: str):
    data = json.loads(artifact.read_text())
    factory = w3.eth.contract(abi=data["abi"], bytecode=data["bytecode"])
    tx = factory.constructor().transact({"from": sender})
    receipt = w3.eth.wait_for_transaction_receipt(tx)
    return w3.eth.contract(address=receipt.contractAddress, abi=data["abi"])


def send(w3, fn, sender: str):
    """Transact from an unlocked Hardhat account; return the receipt."""
    receipt = w3.eth.wait_for_transaction_receipt(
        fn.transact({"from": sender}))
    assert receipt.status == 1
    return receipt
