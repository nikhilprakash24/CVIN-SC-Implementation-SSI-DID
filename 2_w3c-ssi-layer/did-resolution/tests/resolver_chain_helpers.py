"""
Hardhat node and helpers for the on-chain resolver tests (stream H-R).

Same pattern as 2_w3c-ssi-layer/mobi-vid/tests/test_mobi_vid_layer.py: the
test process starts its own `npx hardhat node` (here on
$DID_RESOLVER_TEST_RPC_PORT, default 8560, so it never collides with the MOBI
suite's 8547 or the CI node on 8548) and stops it by process group at exit.
If the node cannot be started (no compiled artifacts, no node_modules, port
taken) the on-chain tests SKIP with the reason; the CI job "All Python suites
(no skips)" compiles the contracts first and fails on any skip.

Why not a conftest.py: cv2x-testbed/tests does `from conftest import deploy`,
and a second conftest module in the same pytest run shadows it. The node is
therefore a process-wide singleton here (`node_url()`), shared by the two
test modules through this uniquely named module.
"""

import atexit
import json
import os
import signal
import socket
import subprocess
import time
from pathlib import Path
from typing import Optional

import pytest

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

_proc: Optional[subprocess.Popen] = None
_skip_reason: Optional[str] = None


def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def free_port() -> int:
    """A local TCP port with nothing listening (for the RPC-down tests)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _stop() -> None:
    global _proc
    if _proc is None:
        return
    try:
        os.killpg(os.getpgid(_proc.pid), signal.SIGTERM)
        _proc.wait(timeout=10)
    except Exception:
        _proc.kill()
    _proc = None


def _start() -> Optional[str]:
    """Start the node; return a skip reason, or None when it is up."""
    global _proc
    for artifact in (ERC1056_ARTIFACT, MOBI_ARTIFACT):
        if not artifact.exists():
            return (f"Hardhat artifact missing ({artifact}); run "
                    "`npx hardhat compile` in 1_blockchain-identity/")
    if not (HARDHAT_DIR / "node_modules").exists():
        return "1_blockchain-identity/node_modules missing; run npm install"
    if _port_open(RPC_PORT):
        return (f"Port {RPC_PORT} already in use; refusing to reuse an "
                "unknown node (set DID_RESOLVER_TEST_RPC_PORT)")
    _proc = subprocess.Popen(
        ["npx", "hardhat", "node", "--port", str(RPC_PORT)],
        cwd=str(HARDHAT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    atexit.register(_stop)
    deadline = time.time() + 60
    while time.time() < deadline:
        if _proc.poll() is not None:
            _proc = None
            return "hardhat node exited immediately"
        if _port_open(RPC_PORT):
            time.sleep(1.0)  # JSON-RPC a moment after the socket opens
            return None
        time.sleep(0.5)
    _stop()
    return "hardhat node did not become ready within 60 s"


def node_url() -> str:
    """URL of the shared node, started on first use; skips if impossible."""
    global _skip_reason
    if _proc is None and _skip_reason is None:
        _skip_reason = _start()
    if _skip_reason is not None:
        pytest.skip(_skip_reason)
    return RPC_URL


def web3_for(url: str):
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider(url))
    assert w3.eth.chain_id == HARDHAT_CHAIN_ID
    return w3


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
