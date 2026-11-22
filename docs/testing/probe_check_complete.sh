#!/usr/bin/env bash
# Probe for `build_register.py --check-complete` (guide rule 1.3.11): show the guard fires.
# Works in a throwaway git worktree of HEAD, so the real checkout is never touched.
#   probe 1: a new test file in a directory the register does not know        -> must fail
#   probe 2: an it( whose title the parser cannot read (title on the next line) -> must fail
#   control: the unmodified worktree                                           -> must pass
set -u
cd "$(git rev-parse --show-toplevel)"
W=$(mktemp -d)/probe
git worktree add -q --detach "$W" HEAD || { echo "PROBE ERROR: cannot create worktree"; exit 2; }
trap 'git worktree remove --force "$W" >/dev/null 2>&1' EXIT
cd "$W"
python3 docs/testing/build_register.py --check-complete > /dev/null || { echo "PROBE ERROR: control failed on an unmodified tree"; exit 1; }
mkdir -p probe_unregistered && printf 'def test_probe():\n    assert True\n' > probe_unregistered/test_probe.py
git add -N probe_unregistered/test_probe.py
if python3 docs/testing/build_register.py --check-complete > /dev/null; then echo "PROBE FAIL: an unregistered test file passed"; exit 1; fi
git rm -q --cached probe_unregistered/test_probe.py && rm -r probe_unregistered
F=1_blockchain-identity/test/L2-identity-system/per-option/LSP8/CVINVehicleLSP8.test.js
printf '\ndescribe("probe", function () {\n  it(\n    "multi-line title", async function () {});\n});\n' >> "$F"
if python3 docs/testing/build_register.py --check-complete > /dev/null; then echo "PROBE FAIL: an unparseable it( passed"; exit 1; fi
echo "probe ok: --check-complete fails on an unregistered test file and on an unparseable it(, and passes on the unmodified tree"
