#!/usr/bin/env bash
# Probe that the producing-code "dirty" flags can fire (after-action report 11; WM-2 step A2, D49).
# 1. scopes.json is current and every producer's import closure lies inside its scope.
# 2. Both stamp helpers (tools/run_identity/stamp.py, 1_blockchain-identity/scripts/lib/run_stamp.js), for
#    every producer of record: clean on the tree; dirty on an edit to a tracked imported file and on a new
#    file in an input directory; clean on a new results file (tools/run_identity/probe.py).
# 3. The headers the Python producers write carry the helper's flag: an edit to imported code that is not
#    in the producer's directory (cv2x-testbed/identity/freshness.py) flips them.
# Run from the repository root on a tree whose producing paths are clean (CI checkout). Files touched
# are restored on exit.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python3 tools/run_identity/stamp.py --check
python3 tools/run_identity/probe.py

LIB=cv2x-testbed/identity/freshness.py
ORIG=$(mktemp)
cp "$LIB" "$ORIG"
trap 'cp "$ORIG" "$LIB"; rm -f "$ORIG"' EXIT
py() { (cd cv2x-testbed/sumo && python3 -c 'import sumo_identity_integration as s, run_v2v_stats as r; print(s._environment()["code_dirty"], r.environment_header()["code_clean"])'); }

fail=0
[ "$(py)" = "False True" ] || { echo "FAIL python headers on a clean tree: $(py)"; fail=1; }
printf '\n' >> "$LIB"
[ "$(py)" = "True False" ] || { echo "FAIL python headers: an edit to imported code ($LIB) does not mark the code dirty: $(py)"; fail=1; }

[ $fail -eq 0 ] && echo "run-identity headers: OK (the SUMO headers fire on an edit to imported code outside their directory)"
exit $fail
