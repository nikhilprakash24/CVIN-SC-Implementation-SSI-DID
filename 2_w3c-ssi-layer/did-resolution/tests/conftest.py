"""
Shared fixtures for the on-chain resolver tests (stream H-R).

Same pattern as 2_w3c-ssi-layer/mobi-vid/tests/test_mobi_vid_layer.py: the
session starts its own `npx hardhat node` (here on $DID_RESOLVER_TEST_RPC_PORT,
default 8560, so it never collides with the MOBI suite's 8547 or the CI node on
8548) and stops it by process group at the end. If the node cannot be started
(no compiled artifacts, no node_modules, port taken) the on-chain tests SKIP
with the reason; the CI job "All Python suites (no skips)" compiles the
contracts first and fails on any skip.
"""

import os
import signal
import subprocess
import time

import pytest

from resolver_chain_helpers import (  # noqa: E402
    ERC1056_ARTIFACT, HARDHAT_CHAIN_ID, HARDHAT_DIR, MOBI_ARTIFACT, RPC_PORT,
    RPC_URL, _port_open,
)


@pytest.fixture(scope="session")
def resolver_node():
    """Start `npx hardhat node` for the session; skip cleanly if impossible."""
    for artifact in (ERC1056_ARTIFACT, MOBI_ARTIFACT):
        if not artifact.exists():
            pytest.skip(f"Hardhat artifact missing ({artifact}); run "
                        "`npx hardhat compile` in 1_blockchain-identity/")
    if not (HARDHAT_DIR / "node_modules").exists():
        pytest.skip("1_blockchain-identity/node_modules missing; run npm install")
    if _port_open(RPC_PORT):
        pytest.skip(f"Port {RPC_PORT} already in use; refusing to reuse an "
                    "unknown node (set DID_RESOLVER_TEST_RPC_PORT)")

    proc = subprocess.Popen(
        ["npx", "hardhat", "node", "--port", str(RPC_PORT)],
        cwd=str(HARDHAT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            if proc.poll() is not None:
                pytest.skip("hardhat node exited immediately")
            if _port_open(RPC_PORT):
                time.sleep(1.0)
                break
            time.sleep(0.5)
        else:
            pytest.skip("hardhat node did not become ready within 60 s")
        yield RPC_URL
    finally:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=10)
        except Exception:
            proc.kill()


@pytest.fixture(scope="session")
def w3(resolver_node):
    from web3 import Web3
    web3 = Web3(Web3.HTTPProvider(resolver_node))
    assert web3.eth.chain_id == HARDHAT_CHAIN_ID
    return web3
