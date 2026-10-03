"""
Shared fixtures for the cv2x-testbed regression tests (review 02, P1-T).

On-chain tests use a Hardhat node at $CV2X_TEST_RPC_URL (default
http://127.0.0.1:8545) and are SKIPPED ONLY when no node answers there.
Start one with `npx hardhat node` in cv2x-testbed/ (or any directory with
the same hardhat.config.js) before running them.
"""

import json
import os
import sys
import warnings

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

warnings.filterwarnings('ignore', category=DeprecationWarning)

RPC_URL = os.environ.get('CV2X_TEST_RPC_URL', 'http://127.0.0.1:8545')
DEPLOYER_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"  # Hardhat account #0


def _node_reachable() -> bool:
    try:
        from web3 import Web3
        return Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={'timeout': 3})).is_connected()
    except Exception:
        return False


@pytest.fixture(scope='session')
def rpc_url():
    if not _node_reachable():
        pytest.skip(f"no Ethereum node reachable at {RPC_URL} (set CV2X_TEST_RPC_URL)")
    return RPC_URL


def load_artifact(name: str) -> dict:
    """
    Compiled contract from $CV2X_TEST_ARTIFACTS_DIR (default cv2x-testbed/artifacts).

    NOTE: the tracked artifacts/contracts/MOBIVIDRegistry.sol artifact predates
    the source fix in bddbc42 (registerVehicleBirth overflows with it; review
    02 Q-9), so the on-chain MOBI tests need a fresh `npx hardhat compile`
    output. The tracked ERC1056Registry artifact matches its source.
    """
    base = os.environ.get('CV2X_TEST_ARTIFACTS_DIR', os.path.join(ROOT, 'artifacts'))
    with open(os.path.join(base, 'contracts', f'{name}.sol', f'{name}.json')) as f:
        return json.load(f)


def deploy(w3, account, artifact: dict) -> str:
    """Deploy `artifact` from `account`; return the contract address."""
    tx = w3.eth.contract(abi=artifact['abi'], bytecode=artifact['bytecode']).constructor().build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 6_000_000,
        'gasPrice': w3.eth.gas_price,
    })
    signed = account.sign_transaction(tx)
    raw = getattr(signed, 'raw_transaction', None) or signed.rawTransaction
    receipt = w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(raw))
    assert receipt.status == 1
    return receipt.contractAddress
