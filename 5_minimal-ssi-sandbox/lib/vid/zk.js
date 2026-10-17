// Groth16 range-predicate layer (HDA doc 02 §10 stage c): AgeGate circuit.
// commitment = Poseidon(birthYear, salt) — the circuit-friendly commitment. The hash-anchored
// credential in lib/vid/credentials.js uses a keccak commitment; a credential that must support
// this proof carries the Poseidon commitment instead (design note recorded in FINDINGS).
const path = require("path");
const snarkjs = require("snarkjs");

const WASM = path.join(__dirname, "../../circuits/AgeGate_js/AgeGate.wasm");
const ZKEY = path.join(__dirname, "../../zk/AgeGate_final.zkey");
const VKEY = path.join(__dirname, "../../zk/AgeGate_vkey.json");

let _poseidon;
async function poseidon() {
  if (!_poseidon) { const { buildPoseidon } = require("circomlibjs"); _poseidon = await buildPoseidon(); }
  return _poseidon;
}

async function commit(birthYear, salt) {
  const p = await poseidon();
  return p.F.toObject(p([BigInt(birthYear), BigInt(salt)]));
}

async function prove({ birthYear, salt, commitment, maxBirthYear }) {
  const { proof, publicSignals } = await snarkjs.groth16.fullProve(
    { birthYear: BigInt(birthYear), salt: BigInt(salt), commitment, maxBirthYear: BigInt(maxBirthYear) }, WASM, ZKEY);
  return { proof, publicSignals };
}

async function verifyOffChain({ proof, publicSignals }) {
  const vkey = require(VKEY);
  return snarkjs.groth16.verify(vkey, publicSignals, proof);
}

// Solidity calldata shape for Groth16Verifier.verifyProof.
async function calldata({ proof, publicSignals }) {
  const s = await snarkjs.groth16.exportSolidityCallData(proof, publicSignals);
  const [a, b, c, pub] = JSON.parse("[" + s + "]");
  return { a, b, c, pub, bytes: Buffer.byteLength(s) };
}

module.exports = { commit, prove, verifyOffChain, calldata };
