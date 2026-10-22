#!/usr/bin/env bash
# Guard probe (guide rule 1.3.11): break a verifier in a scratch copy and require the tests to fail.
# Each mutant must be caught; a mutant that survives fails this script.
set -uo pipefail
cd "$(dirname "$0")"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
declare -a NAMES=("schnorr challenge not checked" "range proof sum not checked" "nullifier ignores scope"
                  "kernel ignores the leakage budget" "transcript drops the context")
declare -a FILES=("zkid/sigma.py" "zkid/sigma.py" "zkid/nullifier.py" "steward/kernel.py" "zkid/transcript.py")
declare -a FROM=("return scalar_mult(s, G) == R + scalar_mult(e, P)" "    if acc != C:" "+ secret + scope)"
                 "            if g > lim[\"global_budget_bits\"] + 1e-9:" "        self._absorb(b\"ctx\", context)")
declare -a TO=("return scalar_mult(s, G) == scalar_mult(s, G)" "    if False:" "+ secret)"
               "            if False:" "        pass")
fail=0
for i in "${!NAMES[@]}"; do
  rm -rf "$WORK/m"; mkdir -p "$WORK/m"
  cp -r zkid steward attacks tests figures results pytest.ini "$WORK/m/"
  python3 - "$WORK/m/${FILES[$i]}" "${FROM[$i]}" "${TO[$i]}" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text()
assert sys.argv[2] in s, f"mutation anchor not found in {p}: {sys.argv[2]!r}"
p.write_text(s.replace(sys.argv[2], sys.argv[3], 1))
PY
  if (cd "$WORK/m" && CVIN_ZKID_MUTANT=1 python3 -m pytest -q -x -p no:cacheprovider tests/test_zkid.py tests/test_steward.py tests/test_attacks.py > /dev/null 2>&1); then
    echo "SURVIVED: ${NAMES[$i]}"; fail=1
  else
    echo "caught:   ${NAMES[$i]}"
  fi
done
exit $fail
