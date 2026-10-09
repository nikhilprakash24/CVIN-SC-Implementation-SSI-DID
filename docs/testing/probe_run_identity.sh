#!/usr/bin/env bash
# Probe that the producing-code "dirty" flags can fire (after-action report 11). Each flag is read on
# the current tree, then with one untracked file placed in a producing path, then with one placed in
# a results path; the first two must differ and the results file must not count. The probe files are
# removed on exit. Run from the repository root on a tree whose producing paths are clean (CI checkout).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
JS_PROBE=1_blockchain-identity/contracts/zz_identity_probe.sol
PY_PROBE=cv2x-testbed/sumo/zz_identity_probe.py
RES_PROBE=cv2x-testbed/sumo/results/zz_identity_probe.json
trap 'rm -f "$JS_PROBE" "$PY_PROBE" "$RES_PROBE"' EXIT

js() { (cd 1_blockchain-identity && node -e 'process.stdout.write(String(require("./scripts/lib/run_stamp").runStamp().dirty))'); }
py() { (cd cv2x-testbed/sumo && python3 -c 'import sumo_identity_integration as s, run_v2v_stats as r; print(s._environment()["code_dirty"], r.environment_header()["code_clean"])'); }

fail=0
[ "$(js)" = "false" ] || { echo "FAIL run_stamp.js: dirty on a clean tree"; fail=1; }
touch "$JS_PROBE"
[ "$(js)" = "true" ] || { echo "FAIL run_stamp.js: an untracked contract does not mark the run dirty"; fail=1; }
rm -f "$JS_PROBE"

[ "$(py)" = "False True" ] || { echo "FAIL python headers on a clean tree: $(py)"; fail=1; }
touch "$RES_PROBE"
[ "$(py)" = "False True" ] || { echo "FAIL python headers: a results file marks the code dirty"; fail=1; }
touch "$PY_PROBE"
[ "$(py)" = "True False" ] || { echo "FAIL python headers: an untracked producer does not mark the code dirty: $(py)"; fail=1; }

[ $fail -eq 0 ] && echo "run-identity flags: OK (JS run stamp and both Python headers fire on producing code, ignore results)"
exit $fail
