#!/usr/bin/env python3
"""Probe that every producer's code flag can fire, in both helpers (WM-2 step A2; after-action report 11).

For each producer of record in scopes.json, the Python helper (stamp.py) and the JS helper
(run_stamp.js) must both report:
  1. clean on the starting tree (the probe refuses to run on a dirty scope: it restores files byte for byte);
  2. dirty after a one-byte edit to a *tracked file the producer imports* (not the producer itself where
     the closure has another file: an edit to imported code is the case D49 found unflagged);
  3. dirty after an untracked file appears in a declared input directory (contracts, artifacts);
  4. clean with an untracked file in each of the producer's results directories.
Every file the probe touches is restored or removed before the next check.

    python3 tools/run_identity/probe.py                       # CI, on a clean checkout
    python3 tools/run_identity/probe.py --py-helper X.py --js-helper Y.js   # probe a candidate helper
Exit 1 on any failed expectation.
"""
import argparse
import importlib.util
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HELPERS = {HERE / "stamp.py", ROOT / "1_blockchain-identity/scripts/lib/run_stamp.js"}


def load_py(path):
    spec = importlib.util.spec_from_file_location("stamp_under_probe", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def js_dirty(helper, producer, cwd):
    # started from a subdirectory on purpose: the flag must not depend on the caller's cwd
    code = (f"const s=require({json.dumps(str(helper))}).runStamp({json.dumps(str(ROOT / producer))});"
            "process.stdout.write(String(s.dirty))")
    out = subprocess.run(["node", "-e", code], cwd=cwd, capture_output=True, text=True)
    return {"true": True, "false": False}.get(out.stdout.strip(), f"error: {out.stderr.strip()[-200:]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--py-helper", default=str(HERE / "stamp.py"))
    ap.add_argument("--js-helper", default=str(ROOT / "1_blockchain-identity/scripts/lib/run_stamp.js"))
    a = ap.parse_args()
    py = load_py(a.py_helper)
    scopes = json.loads((HERE / "scopes.json").read_text())["scopes"]
    tracked = set(subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split())
    failures, checks = [], 0

    def expect(producer, what, want):
        nonlocal checks
        import os
        cwd = ROOT / pathlib.PurePosixPath(producer).parent
        here = os.getcwd()
        os.chdir(cwd)                       # the Python helper, too, is called from the producer's directory
        try:
            got_py = py.stamp(producer)["code_dirty"]
        except Exception as e:  # noqa: BLE001
            got_py = f"error: {e}"
        finally:
            os.chdir(here)
        got_js = js_dirty(a.js_helper, producer, cwd)
        checks += 2
        for name, got in (("py", got_py), ("js", got_js)):
            if got != want:
                failures.append(f"{producer}: {what}: {name} helper says dirty={got}, expected {want}")

    for producer, sc in sorted(scopes.items()):
        paths = sc["paths"]
        files = [p for p in paths if p in tracked and (ROOT / p).is_file()]
        expect(producer, "clean tree", False)
        if failures and failures[-1].startswith(producer + ": clean tree"):
            continue                        # nothing below is meaningful on a dirty scope
        # 2. an edit to a tracked imported file
        imported = [p for p in files if p != producer and (ROOT / p) not in HELPERS and p.endswith((".py", ".js"))]
        target = ROOT / (imported[-1] if imported else producer)
        original = target.read_bytes()
        try:
            target.write_bytes(original + b"\n")
            expect(producer, f"edit to {target.relative_to(ROOT)}", True)
        finally:
            target.write_bytes(original)
        # 3. an untracked file in a declared input directory
        for d in [p for p in paths if (ROOT / p).is_dir()][:1]:
            probe = ROOT / d / "zz_identity_probe.txt"
            try:
                probe.write_text("probe\n")
                expect(producer, f"untracked file in {d}", True)
            finally:
                probe.unlink(missing_ok=True)
        # 4. a results file must not count
        for r in sc["results"]:
            rdir = ROOT / (r if r.endswith("/") else str(pathlib.PurePosixPath(r).parent))
            if not rdir.is_dir():
                continue
            probe = rdir / "zz_identity_probe.json"
            try:
                probe.write_text("{}\n")
                expect(producer, f"untracked result in {rdir.relative_to(ROOT)}", False)
            finally:
                probe.unlink(missing_ok=True)
    for f in failures:
        print("FAIL", f)
    if not failures:
        print(f"run-identity probe: OK ({len(scopes)} producers, {checks} helper checks: both helpers clean on the "
              "tree, dirty on an edit to imported code and on a new input file, clean on a new results file)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
