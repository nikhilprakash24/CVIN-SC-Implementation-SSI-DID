#!/usr/bin/env python3
"""Mutation test of the infrastructure verifier against its L3 tests (committed at the close of WM-1,
after-action report 12; audit findings B2-F1 and B4-F12: the pass-11 mutant set had not been committed).

Each mutant changes one check in `cv2x-testbed/sumo/infrastructure_layer.py` (or the freshness policy it
uses). The L3 file must fail on every mutant. Mutants listed under EQUIVALENT cannot change behaviour and
are reported, not required to fail.

    python3 sandbox/py-suites/L3-ssi/mutation/mutate_infrastructure_layer.py      # exit 1 if any survives
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[4]
LAYER = ROOT / "cv2x-testbed/sumo/infrastructure_layer.py"
FRESH = ROOT / "cv2x-testbed/identity/freshness.py"
TESTS = ROOT / "sandbox/py-suites/L3-ssi/test_infrastructure_layer.py"
FP = "FreshnessPolicy(replay_cache=True, clock=clock)"

# name -> (file, old, new)
MUTANTS = {
    "warm_permitted_removed": (LAYER, 'elif msg_type not in entry["permitted"]:', "elif False:"),
    "cold_permitted_removed": (LAYER, "elif msg_type not in permitted:", "elif False:"),
    "freshness_removed": (LAYER, "if fresh is not None:", "if False:"),
    "future_unbounded": (LAYER, FP, FP[:-1] + ", max_future_s=1e9)"),
    "stale_window_huge": (LAYER, FP, FP[:-1] + ", max_age_s=1e9)"),
    "replay_cache_off": (LAYER, "replay_cache=True", "replay_cache=False"),
    "replay_key_global": (LAYER, 'replay_key = f"{receiver_id}|{sender_did}"', "replay_key = sender_did"),
    "accept_before_checks": (LAYER, "            if ok:\n                self.freshness.accept", "            if True:\n                self.freshness.accept"),
    "replay_cached_on_cold_only": (LAYER, "            if ok:\n                self.freshness.accept", "            if ok and cold:\n                self.freshness.accept"),
    "unsigned_check_removed": (LAYER, 'elif not package.get("signature"):', "elif False:"),
    "warm_key_check_removed": (LAYER, 'if recovered.lower() != entry["address"].lower():', "if False:"),
    "cold_key_check_removed": (LAYER, 'elif recovered.lower() != sender_did.rsplit(":", 1)[-1].lower():', "elif False:"),
    "subject_mismatch_removed": (LAYER, 'elif subject.get("id") != sender_did:', "elif False:"),
    "credential_invalid_ignored": (LAYER, "if not valid:", "if False:"),
    "warm_binding_removed": (LAYER, 'elif not _binding_ok(message, entry["binding"]):', "elif False:"),
    "cold_binding_removed": (LAYER, "elif not _binding_ok(message, binding):", "elif False:"),
    "binding_station_ignored": (LAYER, 'and "rsu" in message and message["rsu"] != binding["stationId"]', "and False"),
    "warm_expiry_removed": (LAYER, 'elif entry["expires"] is not None and time.time() > entry["expires"]:', "elif False:"),
    "expired_entry_kept": (LAYER, '                            del cache[sender_did]\n                            reason = "expired"', '                            reason = "expired"'),
    "revocation_refresh_removed": (LAYER, 'if self.refresh_every is not None and entry["seen"] % self.refresh_every == 0:', "if False:"),
    "refresh_off_by_one": (LAYER, 'entry["seen"] % self.refresh_every == 0', '(entry["seen"]+1) % self.refresh_every == 0'),
    "refresh_every_message": (LAYER, 'entry["seen"] % self.refresh_every == 0', "True"),
    "seen_not_counted": (LAYER, 'entry["seen"] += 1', "pass"),
    "revoked_entry_kept": (LAYER, '                            del cache[sender_did]\n                            reason = "revoked"', '                            reason = "revoked"'),
    "trusts_any_issuer": (LAYER, "CredentialVerifier(trusted_issuers=[self.authority])", "CredentialVerifier(trusted_issuers=[self.authority, self.rogue_authority])"),
    "no_credential_accept": (LAYER, 'reason = "no_credential"', "ok = True"),
    "cache_poison": (LAYER, 'cache[sender_did] = {"address": recovered,', 'cache[sender_did] = {"address": "0x"+"0"*40,'),
    "exception_accepts": (LAYER, "            ok = False\n        return", "            ok = True\n        return"),
    "age_boundary_inclusive": (FRESH, "if now - t > self.max_age_s:", "if now - t >= self.max_age_s:"),
    "future_boundary_inclusive": (FRESH, "if t - now > self.max_future_s:", "if t - now >= self.max_future_s:"),
}
EQUIVALENT = {}


def run(tree):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                        str(tree / TESTS.relative_to(ROOT))], cwd=tree, capture_output=True, text=True, env=env)
    return p.returncode


def main():
    survived = []
    with tempfile.TemporaryDirectory() as td:
        tree = pathlib.Path(td) / "t"
        for sub in ("cv2x-testbed", "2_w3c-ssi-layer", "sandbox/py-suites/L3-ssi"):
            shutil.copytree(ROOT / sub, tree / sub, ignore=shutil.ignore_patterns("node_modules", "results", "__pycache__", "artifacts"))
        assert run(tree) == 0, "the unmutated tests must pass"
        for name, (f, old, new) in MUTANTS.items():
            target = tree / f.relative_to(ROOT)
            src = target.read_text()
            assert old in src, f"{name}: anchor not found (the layer changed; update the mutant)"
            target.write_text(src.replace(old, new, 1))
            killed = run(tree) != 0
            target.write_text(src)
            print(f"{name:30s} {'killed' if killed else 'SURVIVED'}", flush=True)
            if not killed and name not in EQUIVALENT:
                survived.append(name)
    print(f"\n{len(MUTANTS) - len(survived)}/{len(MUTANTS)} killed; survived: {survived}")
    sys.exit(1 if survived else 0)


if __name__ == "__main__":
    main()
