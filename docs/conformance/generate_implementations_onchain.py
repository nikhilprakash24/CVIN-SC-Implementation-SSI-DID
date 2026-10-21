#!/usr/bin/env python3
"""
Generate a SEPARATE W3C DID Test Suite implementation set from the resolver's
ON-CHAIN mode (stream H-R, 2026-10-15).

The offline set (generate_implementations.py, unchanged) registers documents
the resolver synthesises from the DID string. This script instead deploys
the repository's EthereumDIDRegistry and MOBIVIDRegistryV2 on a local
Hardhat node, writes registry state, and records what
    DIDResolver(rpc_url=..., ethr_registry=..., mobi_registry=...)
returns via .resolve(did).to_dict() and .resolve_representation(did).to_dict().
Every value written is taken unchanged from the resolver; the input format and
mapping are those of generate_implementations.py (its method_file /
resolver_file are reused), with extra executions for the outcomes only an
on-chain resolver can produce (notFound, deactivated).

The two sets are reported separately (W3C_DID_TEST_SUITE.md section 10); the
file names carry an `onchain-` prefix so both can sit in the suite's
implementations directory, and run-cvin-cli.js has an `onchain` mode.

Registry state written (did:ethr, chain 31337 = 0x7a69):
  * subject: owner changed to account 2, a sigAuth delegate, a veriKey
    delegate, a did/pub/Secp256k1/veriKey/hex attribute and a did/svc
    service attribute;
  * deactivated: changeOwner(identity, 0x0).
did:mobi: one vehicle born (manufacturer = deployer, first owner =
account 4) under salted_vin_hash(VIN, salt), plus a second vehicle whose
identity was revoked (revokeIdentity).

Usage (a node must be listening; this script does not start one):
    python3 docs/conformance/generate_implementations_onchain.py \
        <rpc-url> <output-dir>
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "2_w3c-ssi-layer", "did-resolution"))
sys.path.insert(0, os.path.join(REPO, "2_w3c-ssi-layer", "mobi-vid"))

from web3 import Web3  # noqa: E402
from did_resolver import DIDResolver  # noqa: E402
from birth_certificate import salted_vin_hash  # noqa: E402
import generate_implementations as offline  # noqa: E402  (unchanged module)

ARTIFACTS = os.path.join(REPO, "1_blockchain-identity", "artifacts",
                         "contracts")
CHAIN = "0x7a69"
NULL = "0x" + "0" * 40
VIN = "5YJ3E1EA0PF123456"


def b32(text):
    return text.encode("ascii").ljust(32, b"\0")


def deploy(w3, rel, sender):
    with open(os.path.join(ARTIFACTS, rel)) as f:
        data = json.load(f)
    c = w3.eth.contract(abi=data["abi"], bytecode=data["bytecode"])
    rcpt = w3.eth.wait_for_transaction_receipt(
        c.constructor().transact({"from": sender}))
    return w3.eth.contract(address=rcpt.contractAddress, abi=data["abi"])


def send(w3, fn, sender):
    rcpt = w3.eth.wait_for_transaction_receipt(fn.transact({"from": sender}))
    assert rcpt.status == 1, rcpt
    return rcpt


def setup(w3):
    acc = w3.eth.accounts
    reg = deploy(w3, "ERC1056/EthereumDIDRegistry.sol/EthereumDIDRegistry.json",
                 acc[0])
    subject, deactivated = acc[1], acc[5]
    send(w3, reg.functions.changeOwner(subject, acc[2]), subject)
    owner = acc[2]
    send(w3, reg.functions.addDelegate(subject, b32("sigAuth"), acc[3],
                                       10 * 365 * 86400), owner)
    send(w3, reg.functions.addDelegate(subject, b32("veriKey"), acc[6],
                                       10 * 365 * 86400), owner)
    send(w3, reg.functions.setAttribute(
        subject, b32("did/pub/Secp256k1/veriKey/hex"),
        bytes.fromhex("02" + "11" * 32), 10 * 365 * 86400), owner)
    send(w3, reg.functions.setAttribute(
        subject, b32("did/svc/LinkedDomains"),
        b"https://cvin.example.com", 10 * 365 * 86400), owner)
    send(w3, reg.functions.changeOwner(deactivated, NULL), deactivated)

    mobi = deploy(w3, "MOBI/MOBIVIDRegistryV2.sol/MOBIVIDRegistryV2.json",
                  acc[0])
    vin_hash = salted_vin_hash(VIN, "onchain-conformance-salt")
    vehicle = Web3.to_checksum_address("0x" + "5e" * 20)
    send(w3, mobi.functions.registerVehicleBirth(
        vehicle, vin_hash, "ciphertext", b"\x01" * 32, acc[4], b""), acc[0])
    revoked_hash = salted_vin_hash(VIN, "onchain-revoked-salt")
    send(w3, mobi.functions.registerVehicleBirth(
        acc[7], revoked_hash, "ciphertext", b"\x02" * 32, acc[7], b""),
        acc[0])
    send(w3, mobi.functions.revokeIdentity(acc[7]), acc[7])
    return {
        "ethr_registry": reg.address,
        "mobi_registry": mobi.address,
        "ethr_did": f"did:ethr:{CHAIN}:{subject}",
        "ethr_deactivated": f"did:ethr:{CHAIN}:{deactivated}",
        "ethr_other_chain": f"did:ethr:0x1:{subject}",
        "mobi_did": f"did:mobi:0x{vin_hash.hex()}",
        "mobi_deactivated": f"did:mobi:0x{revoked_hash.hex()}",
        "mobi_unknown": "did:mobi:0x" + "ab" * 32,
    }


def main():
    rpc, out_dir = sys.argv[1], sys.argv[2]
    w3 = Web3(Web3.HTTPProvider(rpc))
    s = setup(w3)
    resolver = DIDResolver(rpc_url=rpc, ethr_registry=s["ethr_registry"],
                           mobi_registry=s["mobi_registry"])
    plan = {
        "ethr": (s["ethr_did"], "ERC-1056, on-chain", [
            ("did:ethr_0x1234", "invalidDidErrorOutcome"),
            ("did:web:example.com", "methodNotSupportedErrorOutcome"),
            (s["ethr_other_chain"], "notFoundErrorOutcome"),
            (s["ethr_deactivated"], "deactivatedOutcome"),
        ]),
        "mobi": (s["mobi_did"], "MOBI VID, on-chain", [
            ("did:mobi:", "invalidDidErrorOutcome"),
            (s["mobi_unknown"], "notFoundErrorOutcome"),
            (s["mobi_deactivated"], "deactivatedOutcome"),
        ]),
    }
    os.makedirs(out_dir, exist_ok=True)
    for method, (did, label, cases) in plan.items():
        # reuse the offline generator's mapping unchanged
        offline.METHODS[method] = {"did": did, "label": label,
                                   "error_cases": cases}
        result = resolver.resolve(did).to_dict()
        assert "error" not in result["didResolutionMetadata"], result
        rep = resolver.resolve_representation(did).to_dict()
        assert "error" not in rep["didResolutionMetadata"], rep
        for name, data in (
            (f"onchain-cvin-did-{method}.json",
             offline.method_file(method, did, result, rep)),
            (f"onchain-cvin-resolver-{method}.json",
             offline.resolver_file(method, did, result, rep, resolver)),
        ):
            path = os.path.join(out_dir, name)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
                f.write("\n")
            print("wrote", path)
    with open(os.path.join(out_dir, "onchain-setup.json"), "w") as f:
        json.dump(s, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
