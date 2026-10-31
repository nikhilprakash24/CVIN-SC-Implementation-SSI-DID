// Shared helpers for ZK-VIN: VIN encoding, Poseidon commitment, manufacturer tree, inputs, run identity.
const crypto = require("crypto");
const path = require("path");
const { execSync } = require("child_process");
const { buildPoseidon } = require("circomlibjs");

const ROOT = path.resolve(__dirname, "..");
const R = 21888242871839275222987986231195775993180118865422559149641320095516671829249n; // BN254 scalar field order
// The 33 characters a VIN may use (no I, O, Q), coded 0..32.
const VIN_ALPHABET = "0123456789ABCDEFGHJKLMNPRSTUVWXYZ";
const DEPTH = 4;
// Sixteen authorised world manufacturer identifiers (illustrative list, public in the scenario).
const AUTHORISED_WMIS = ["1HG", "5YJ", "WBA", "JTD", "1FA", "2T1", "3VW", "WVW", "KMH", "SAL", "WDD", "1G1", "JHM", "YV1", "ZFA", "VF1"];

function vinCodes(vin) {
  if (vin.length !== 17) throw new Error("a VIN has 17 characters");
  return [...vin].map((ch) => {
    const i = VIN_ALPHABET.indexOf(ch);
    if (i < 0) throw new Error(`character ${ch} is not allowed in a VIN`);
    return BigInt(i);
  });
}
const pack = (codes) => codes.reduce((acc, c, i) => acc + c * 64n ** BigInt(i), 0n);
const wmiOf = (codes) => codes[0] + 64n * codes[1] + 4096n * codes[2];
const toField = (label) => BigInt("0x" + crypto.createHash("sha256").update(label).digest("hex")) % R;

async function context() {
  const poseidon = await buildPoseidon();
  const F = poseidon.F;
  const H = (xs) => F.toObject(poseidon(xs));
  // manufacturer tree: 2^DEPTH leaves, padded with zero
  const leaves = AUTHORISED_WMIS.map((w) => wmiOf(vinCodes(w + "00000000000000")));
  while (leaves.length < 2 ** DEPTH) leaves.push(0n);
  const levels = [leaves];
  while (levels[levels.length - 1].length > 1) {
    const cur = levels[levels.length - 1];
    const nxt = [];
    for (let i = 0; i < cur.length; i += 2) nxt.push(H([cur[i], cur[i + 1]]));
    levels.push(nxt);
  }
  const mfrRoot = levels[levels.length - 1][0];
  function mfrProof(wmi) {
    let idx = leaves.findIndex((l) => l === wmi);
    if (idx < 0) idx = 0; // a cheating prover uses some path; the circuit rejects it
    const path = [], bits = [];
    for (let d = 0; d < DEPTH; d++) {
      path.push(levels[d][idx ^ 1]);
      bits.push(BigInt(idx & 1));
      idx >>= 1;
    }
    return { path, bits };
  }
  function commitment(codes, modelYear, region, salt) {
    return H([pack(codes), BigInt(modelYear), BigInt(region), salt]);
  }
  // Build a full witness input. `claim` lets a test lie about one field while the rest stays honest.
  function input({ vin, modelYear, region, salt, minModelYear, scope, challenge, claim = {} }) {
    const codes = vinCodes(vin);
    const anchored = commitment(codes, modelYear, region, salt);
    const p = mfrProof(wmiOf(codes));
    return {
      vin: (claim.vin ? vinCodes(claim.vin) : codes).map(String),
      modelYear: String(claim.modelYear ?? modelYear),
      salt: String(claim.salt ?? salt),
      mfrPath: p.path.map(String),
      mfrIdx: p.bits.map(String),
      commitment: String(claim.commitment ?? anchored),
      mfrRoot: String(claim.mfrRoot ?? mfrRoot),
      minModelYear: String(minModelYear),
      region: String(claim.region ?? region),
      scope: String(scope),
      challenge: String(challenge),
    };
  }
  return { H, mfrRoot, commitment, input, nullifier: (salt, scope) => H([salt, scope]) };
}

function runIdentity(producing = ["5_zkp-agent-identity/circuits", "5_zkp-agent-identity/scripts",
  "5_zkp-agent-identity/contracts", "5_zkp-agent-identity/artifacts", "5_zkp-agent-identity/zkid",
  "5_zkp-agent-identity/steward", "5_zkp-agent-identity/attacks", "5_zkp-agent-identity/bench"]) {
  const sh = (c) => execSync(c, { cwd: path.resolve(ROOT, ".."), encoding: "utf8" }).trim();
  let commit = "unknown", codeClean = false, treeClean = false;
  try {
    commit = sh("git rev-parse --short HEAD");
    codeClean = sh(`git status --porcelain -- ${producing.join(" ")}`) === "";
    treeClean = sh("git status --porcelain") === "";
  } catch (_) { /* not a git checkout */ }
  const os = require("os");
  return { commit, code_clean: codeClean, tree_clean: treeClean, host: { platform: os.platform(), arch: os.arch(),
    cpus: os.cpus().length, cpu_model: os.cpus()[0]?.model, mem_gb: Math.round(os.totalmem() / 2 ** 30) },
    node: process.version, snarkjs: require(path.join(ROOT, "node_modules/snarkjs/package.json")).version,
    at: new Date().toISOString() };
}

module.exports = { ROOT, R, VIN_ALPHABET, DEPTH, AUTHORISED_WMIS, vinCodes, pack, wmiOf, toField, context, runIdentity };
