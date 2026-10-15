#!/usr/bin/env bash
# Build ZK-VIN: compile the circuit, run a LOCAL single-party Groth16 setup, export the verification key and the
# Solidity verifier, and write artifacts/MANIFEST.json (SHA-256 of every artefact).
#
#   bash circuits/build_circuit.sh            # needs `circom` (2.2.x) on PATH or CIRCOM=/path/to/circom
#
# INSECURE FOR PRODUCTION. The entropy below is fixed so the build is reproducible, which means the "toxic waste"
# is public. Anyone can forge proofs against these keys. A deployment needs a multi-party ceremony (Plan 1 to-do 11).
set -euo pipefail
cd "$(dirname "$0")/.."
CIRCOM="${CIRCOM:-circom}"
SNARKJS="node node_modules/snarkjs/build/cli.cjs"
OUT=artifacts
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$OUT"

"$CIRCOM" circuits/zkvin.circom --r1cs --wasm --sym -o "$TMP" > "$TMP/circom.log"
cat "$TMP/circom.log" | sed 's/\x1b\[[0-9;]*m//g' | grep -E "constraints|inputs|outputs|wires" > "$OUT/circuit_info.txt"
"$CIRCOM" --version >> "$OUT/circuit_info.txt"

# Phase 1 (powers of tau, 2^12 constraints) and phase 2 (circuit-specific), fixed entropy: reproducible, insecure.
$SNARKJS powersoftau new bn128 12 "$TMP/pot_0.ptau" > /dev/null
$SNARKJS powersoftau contribute "$TMP/pot_0.ptau" "$TMP/pot_1.ptau" --name="cvin-dev-1" -e="cvin zkvin dev ceremony phase1 INSECURE" > /dev/null
$SNARKJS powersoftau prepare phase2 "$TMP/pot_1.ptau" "$TMP/pot_final.ptau" > /dev/null
$SNARKJS groth16 setup "$TMP/zkvin.r1cs" "$TMP/pot_final.ptau" "$TMP/zkvin_0.zkey" > /dev/null
$SNARKJS zkey contribute "$TMP/zkvin_0.zkey" "$OUT/zkvin_final.zkey" --name="cvin-dev-2" -e="cvin zkvin dev ceremony phase2 INSECURE" > /dev/null
$SNARKJS zkey export verificationkey "$OUT/zkvin_final.zkey" "$OUT/verification_key.json" > /dev/null
$SNARKJS zkey export solidityverifier "$OUT/zkvin_final.zkey" contracts/Groth16Verifier.sol > /dev/null
cp "$TMP/zkvin_js/zkvin.wasm" "$OUT/zkvin.wasm"
cp "$TMP/zkvin.r1cs" "$OUT/zkvin.r1cs"

node -e '
const fs=require("fs"),crypto=require("crypto");
const files=["artifacts/zkvin.wasm","artifacts/zkvin.r1cs","artifacts/zkvin_final.zkey","artifacts/verification_key.json","contracts/Groth16Verifier.sol","circuits/zkvin.circom"];
const m={note:"Single-party local Groth16 setup with fixed entropy: reproducible and INSECURE for production.",
  snarkjs:require("./node_modules/snarkjs/package.json").version, circomlib:require("./node_modules/circomlib/package.json").version,
  files:Object.fromEntries(files.map(f=>[f,crypto.createHash("sha256").update(fs.readFileSync(f)).digest("hex")]))};
fs.writeFileSync("artifacts/MANIFEST.json", JSON.stringify(m,null,2)+"\n");'
echo "built: $(cat $OUT/circuit_info.txt | tr '\n' ' ')"
