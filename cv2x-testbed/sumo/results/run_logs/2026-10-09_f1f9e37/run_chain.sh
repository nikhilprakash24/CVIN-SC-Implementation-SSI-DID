#!/usr/bin/env bash
set -u
W=$SCRATCH/run11
cd $W/cv2x-testbed/sumo
echo "I1 start $(date -u +%FT%TZ)"
python3 run_infra_stats.py --runs 30 --duration 20 > $SCRATCH/r11_i1.log 2>&1; echo "I1 rc $? $(date -u +%FT%TZ)"
python3 run_infra_stats.py --runs 30 --duration 20 --revocation > $SCRATCH/r11_i3.log 2>&1; echo "I3 rc $? $(date -u +%FT%TZ)"
python3 sumo_identity_integration.py --simulate --rsu --seed 1 --duration 20 --results $SCRATCH/r11_trace_rsu.json --trace results/traces/trace_rsu_seed1.jsonl.gz > /dev/null 2>&1; echo "trace1 rc $?"
python3 sumo_identity_integration.py --simulate --rsu --seed 1 --duration 20 --refresh-k 5 --revoke-rsu-at 10 --results $SCRATCH/r11_trace_rev.json --trace results/traces/trace_revocation_k5_seed1.jsonl.gz > /dev/null 2>&1; echo "trace2 rc $?"
cd $W/1_blockchain-identity
npx hardhat run scripts/infrastructure_gas.js > $SCRATCH/r11_i4a.log 2>&1; echo "I4a rc $?"; cp ../4_comparison-framework/results/infrastructure_gas.json $SCRATCH/r11_i4a.json
npx hardhat run scripts/infrastructure_gas.js > $SCRATCH/r11_i4b.log 2>&1; echo "I4b rc $?"; cp ../4_comparison-framework/results/infrastructure_gas.json $SCRATCH/r11_i4b.json
echo DONE
