#!/usr/bin/env bash
# Run every catalog scenario against every enabled option. Usage: bash scenarios/run_all.sh [scenario...]
# Each run writes its own trace file (immutable; new runs are new files).
set -u
export HARDHAT_DISABLE_TELEMETRY_PROMPT=true
OPTIONS="${OPTIONS:-O1_ERC1056 O2_ERC721 O3_ERC725 O4_ERC725xy O5_ERC1155 O6_ERC4337 O7_ERC8004 O8_LFDT}"
SCENARIOS="${*:-run_i2i run_vid_minimal run_vid_lifecycle run_s2_dualmode run_s3_evcharging run_s4_insurance}"
fail=0
for s in $SCENARIOS; do
  for o in $OPTIONS; do
    if out=$(IMPL=$o npx hardhat run "scenarios/$s.js" 2>&1); then
      echo "ok   $s $o  $(echo "$out" | grep -o 'Trace written: [^ ]*' | tail -1)"
    else
      echo "FAIL $s $o"; echo "$out" | tail -5; fail=1
    fi
  done
done
exit $fail
