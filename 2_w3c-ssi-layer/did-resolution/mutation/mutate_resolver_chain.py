#!/usr/bin/env python3
"""Mutation probe of the chain-reading did:ethr resolver (WM-2 C1 tests; after-action report 36; guide 1.3.11).

Each mutant weakens one guard of `did_resolver.py`'s ERC-1056 path; the resolver's chain tests and the two MOBI
resolution tests must fail on every one. The file is restored on exit, also on error or interrupt.

    python3 2_w3c-ssi-layer/did-resolution/mutation/mutate_resolver_chain.py     # exit = number of survivors

Needs `1_blockchain-identity` compiled (the tests start their own Hardhat node, or use CV2X_TEST_RPC_URL).
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
F = ROOT / "2_w3c-ssi-layer/did-resolution/did_resolver.py"
TESTS = ["2_w3c-ssi-layer/did-resolution/tests/test_did_resolver_chain.py",
         "2_w3c-ssi-layer/did-resolution/tests/test_did_resolver_onchain_ethr.py",
         "2_w3c-ssi-layer/mobi-vid/tests/test_mobi_vid_layer.py::TestBirthCertificate::"
         "test_onchain_vehicle_did_resolves_from_the_chain_to_its_first_owner",
         "2_w3c-ssi-layer/mobi-vid/tests/test_mobi_vid_layer.py::TestBirthCertificate::"
         "test_revoked_identity_resolves_as_deactivated"]

# name, old, new: each old string must occur exactly once
MUTANTS = [
    ("delegate_expiry_ignored",
     "                    delegates.pop(key, None)\n                    continue\n",
     "                    pass\n"),
    ("attribute_expiry_ignored",
     "                    keys.pop(key, None)\n                    services.pop(key, None)\n                    continue\n",
     "                    pass\n"),
    ("owner_change_ignored",
     '                owner = a["owner"]\n',
     "                pass\n"),
    ("owner_zero_not_deactivation",
     "                if int(owner, 16) == 0:\n                    deactivated = True\n",
     "                if False:\n                    deactivated = True\n"),
    ("didrevoked_ignored",
     "                revoked = True\n",
     "                revoked = False\n"),
    ("sigauth_dropped",
     '                if dtype in ("veriKey", "sigAuth"):\n',
     '                if dtype in ("veriKey",):\n'),
    ("event_order_reversed",
     "            history = block_events + history\n",
     "            history = history + block_events\n"),
    ("head_time_ignored",
     '        now = int(head["timestamp"])\n',
     "        now = 0\n"),
    ("registry_lookup_dropped",
     "                registry = self.registries.get(chain_id)\n",
     "                registry = None\n"),
]


def run_tests():
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", *TESTS],
                       cwd=ROOT, capture_output=True, text=True)
    return r.returncode == 0


def main():
    orig = F.read_text()
    survived = 0
    try:
        for name, old, new in MUTANTS:
            if orig.count(old) != 1:
                print(f"ANCHOR {name}: found {orig.count(old)} times, expected 1")
                survived += 1
                continue
            F.write_text(orig.replace(old, new, 1))
            if run_tests():
                print(f"SURVIVED {name}")
                survived += 1
            else:
                print(f"killed   {name}")
    finally:
        F.write_text(orig)
    if not run_tests():
        print("BASELINE FAILS after restore")
        return 99
    print(f"resolver chain mutants: {survived} of {len(MUTANTS)} survived")
    return survived


if __name__ == "__main__":
    sys.exit(main())
