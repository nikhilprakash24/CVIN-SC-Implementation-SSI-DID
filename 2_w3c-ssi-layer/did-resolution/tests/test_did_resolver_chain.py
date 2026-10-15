"""
WM-2 C1: did:ethr resolution reads the ERC-1056 registry (after-action report 21).

Before C1, `_resolve_ethr` built the same static document whatever the chain
held, even when the resolver was given a provider: an owner change, a delegate,
an attribute, a revocation or a deactivation never reached the document. The
tests that assert chain state failed on that code (report 21 §2); the others
pin behaviour that must not change.

Chain: CV2X_TEST_RPC_URL if set (the all-suites CI job shares a node on 8548);
otherwise the module starts its own Hardhat node on OWN_PORT, as the MOBI suites
do, because the L3 + L4 job fails on any skip.
"""

import json
import os
import pathlib
import signal
import socket
import subprocess
import sys
import time

import pytest

web3 = pytest.importorskip("web3")
from web3 import Web3  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from did_resolver import DIDResolver  # noqa: E402

ROOT = HERE.parents[2]
ARTIFACT = ROOT / "1_blockchain-identity/artifacts/contracts/ERC1056/EthereumDIDRegistry.sol/EthereumDIDRegistry.json"
HARDHAT_DIR = ROOT / "1_blockchain-identity"
OWN_PORT = 8563


def _port_open(port):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


@pytest.fixture(scope="module")
def rpc_url():
    url = os.environ.get("CV2X_TEST_RPC_URL")
    if url:
        yield url
        return
    if not (HARDHAT_DIR / "node_modules").exists():
        pytest.skip("1_blockchain-identity/node_modules missing; run npm install")
    if _port_open(OWN_PORT):
        pytest.skip(f"port {OWN_PORT} already in use; refusing to reuse an unknown node")
    proc = subprocess.Popen(["npx", "hardhat", "node", "--port", str(OWN_PORT)], cwd=str(HARDHAT_DIR),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        deadline = time.time() + 60
        while not _port_open(OWN_PORT):
            if proc.poll() is not None or time.time() > deadline:
                pytest.skip("hardhat node did not start")
            time.sleep(0.5)
        time.sleep(1.0)
        yield f"http://127.0.0.1:{OWN_PORT}"
    finally:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=10)
        except Exception:
            proc.kill()


def b32(text):
    return text.encode().ljust(32, b"\0")


@pytest.fixture(scope="module")
def chain(rpc_url):
    if not ARTIFACT.exists():
        pytest.skip(f"compile 1_blockchain-identity first: {ARTIFACT} missing")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    art = json.loads(ARTIFACT.read_text())
    deployer = w3.eth.accounts[0]
    tx = w3.eth.contract(abi=art["abi"], bytecode=art["bytecode"]).constructor().transact({"from": deployer})
    address = w3.eth.wait_for_transaction_receipt(tx)["contractAddress"]
    reg = w3.eth.contract(address=address, abi=art["abi"])
    return w3, reg, int(w3.eth.chain_id)


_next = iter(range(10, 19))   # Hardhat's unlocked accounts 10..18, one fresh identity per test


@pytest.fixture
def ident(chain):
    w3, reg, cid = chain
    who = w3.eth.accounts[next(_next)]
    return who, f"did:ethr:{hex(cid)}:{who}"


def send(w3, fn, sender):
    w3.eth.wait_for_transaction_receipt(fn.transact({"from": sender}))


def resolve(chain, did):
    w3, reg, cid = chain
    r = DIDResolver(blockchain_provider=w3)
    r.registries = {cid: reg.address}   # set after construction so the old resolver accepts it too
    return r.resolve(did)


def vm_accounts(result):
    return [vm.blockchainAccountId for vm in result.didDocument.verificationMethod]


def test_identity_without_events_resolves_to_the_default_document(chain, ident):
    who, did = ident
    res = resolve(chain, did)
    assert res.didResolutionMetadata.error is None
    assert vm_accounts(res) == [f"eip155:{chain[2]}:{who}"]
    assert res.didDocument.authentication == [f"{did}#controller"]


def test_owner_change_moves_the_controller_key(chain, ident):
    w3, reg, cid = chain
    who, did = ident
    new_owner = w3.eth.accounts[1]
    send(w3, reg.functions.changeOwner(who, new_owner), who)
    res = resolve(chain, did)
    assert vm_accounts(res)[0] == f"eip155:{cid}:{new_owner}", "the owner change did not reach the document"
    assert res.didDocumentMetadata.versionId == str(reg.functions.changed(who).call())


def test_delegates_appear_while_valid_and_go_when_revoked(chain, ident):
    w3, reg, cid = chain
    who, did = ident
    veri, auth = w3.eth.accounts[2], w3.eth.accounts[3]
    send(w3, reg.functions.addDelegate(who, b32("veriKey"), veri, 86400), who)
    send(w3, reg.functions.addDelegate(who, b32("sigAuth"), auth, 86400), who)
    doc = resolve(chain, did).didDocument
    by_acct = {vm.blockchainAccountId: vm.id for vm in doc.verificationMethod}
    assert by_acct[f"eip155:{cid}:{veri}"] in doc.assertionMethod
    assert by_acct[f"eip155:{cid}:{veri}"] not in doc.authentication
    assert by_acct[f"eip155:{cid}:{auth}"] in doc.authentication
    send(w3, reg.functions.revokeDelegate(who, b32("veriKey"), veri), who)
    accts = vm_accounts(resolve(chain, did))
    assert f"eip155:{cid}:{veri}" not in accts, "a revoked delegate still resolves"
    assert f"eip155:{cid}:{auth}" in accts


def test_key_and_service_attributes_set_and_revoked(chain, ident):
    w3, reg, cid = chain
    who, did = ident
    key = bytes.fromhex("02" + "ab" * 32)
    send(w3, reg.functions.setAttribute(who, b32("did/pub/Secp256k1/sigAuth/hex"), key, 86400), who)
    send(w3, reg.functions.setAttribute(who, b32("did/svc/VehicleRegistry"), b"https://rsu.example/v1", 86400), who)
    doc = resolve(chain, did).didDocument
    keys = [vm for vm in doc.verificationMethod if vm.publicKeyHex == key.hex()]
    assert len(keys) == 1 and keys[0].id in doc.authentication
    assert [(s.type, s.serviceEndpoint) for s in doc.service] == [("VehicleRegistry", "https://rsu.example/v1")]
    send(w3, reg.functions.revokeAttribute(who, b32("did/pub/Secp256k1/sigAuth/hex"), key), who)
    doc = resolve(chain, did).didDocument
    assert not [vm for vm in doc.verificationMethod if vm.publicKeyHex == key.hex()], "a revoked key still resolves"
    assert len(doc.service) == 1


def test_attribute_expires_in_chain_time(chain, ident):
    w3, reg, cid = chain
    who, did = ident
    send(w3, reg.functions.setAttribute(who, b32("did/svc/Short"), b"https://x.example", 60), who)
    assert [s.type for s in resolve(chain, did).didDocument.service] == ["Short"]
    w3.provider.make_request("evm_increaseTime", [120])
    w3.provider.make_request("evm_mine", [])
    assert resolve(chain, did).didDocument.service == [], "an expired attribute still resolves"


def test_owner_zero_is_deactivated(chain, ident):
    w3, reg, cid = chain
    who, did = ident
    send(w3, reg.functions.changeOwner(who, "0x" + "0" * 40), who)
    res = resolve(chain, did)
    assert res.didDocumentMetadata.deactivated is True
    assert res.didDocument.verificationMethod == []


def test_chain_without_a_registry_is_not_found(chain):
    w3, reg, cid = chain
    r = DIDResolver(blockchain_provider=w3)
    r.registries = {cid: reg.address}
    res = r.resolve("did:ethr:0x1:0x" + "11" * 20)
    assert res.didResolutionMetadata.error == "notFound"


def test_a_resolver_with_a_provider_does_not_serve_a_stale_cached_document(chain, ident):
    w3, reg, cid = chain
    who, did = ident
    r = DIDResolver(blockchain_provider=w3)
    r.registries = {cid: reg.address}
    assert vm_accounts(r.resolve(did))[0] == f"eip155:{cid}:{who}"
    send(w3, reg.functions.changeOwner(who, w3.eth.accounts[4]), who)
    assert vm_accounts(r.resolve(did))[0] == f"eip155:{cid}:{w3.eth.accounts[4]}"


def test_without_a_provider_the_document_is_unchanged(ident):
    who, did = ident
    res = DIDResolver().resolve(did)
    assert [vm.id for vm in res.didDocument.verificationMethod] == [f"{did}#controller"]
    assert res.didDocumentMetadata.versionId == "1"
