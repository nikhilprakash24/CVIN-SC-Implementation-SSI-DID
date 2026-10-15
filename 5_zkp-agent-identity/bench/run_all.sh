#!/usr/bin/env bash
# Layer 5 runs of record, in dependency order, from a clean tree (guide rule 1.1.6). Each result file carries its
# run identity (commit, code_clean, host, versions). The responder is retrained first and must reproduce the
# committed table byte for byte (deterministic training); otherwise the run stops.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest -q
python3 attacks/train_responder.py > /dev/null
git diff --quiet -- steward/learned_q.json || { echo "learned_q.json not reproduced"; exit 1; }
python3 attacks/run_attacks.py
node scripts/prove_and_verify.js --bench
( cd ../1_blockchain-identity && npx hardhat --config hardhat.zkp.config.js run ../5_zkp-agent-identity/scripts/measure_gas.js )
python3 bench/sigma_bench.py
python3 bench/vin_bruteforce.py
python3 bench/manual_burden.py
python3 demos/full_circle_demo.py > /dev/null
grep -h '"code_clean"' results/*.json | sort | uniq -c
