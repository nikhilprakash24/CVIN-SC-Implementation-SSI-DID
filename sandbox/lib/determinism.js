// Seeded randomness for the sandbox's L1 mechanism tests and demos (WM-2 step B1; N-18; audit T-F13).
//
// Loaded with `NODE_OPTIONS=--require <this file>` and active only when CVIN_SEED is set: the grand runner sets
// CVIN_SEED=1 for its L1 and demo stages. Fixture keys and random bytes are incidental to what those stages
// measure, so they are seeded (the rule of guide 1.1.10 and register §1): the same seed gives the same keys,
// the same calldata, and so the same gas, run after run. Unset, nothing changes.
//
// What it seeds: ethers.Wallet.createRandom (a fixture key) and ethers.randomBytes (nonces, salts, claim ids).
// What it does not touch: block timestamps and the system clock (Hardhat needs real time), and the metrics
// harness (1_blockchain-identity/benchmarks), which has its own fixed dataset seed and whose tree hash
// identifies its run of record.
const SEED = process.env.CVIN_SEED;

if (SEED !== undefined && SEED !== "") {
  // resolved from the working directory (the Hardhat project), since sandbox/lib has no node_modules of its own
  const ethers = require(require.resolve("ethers", { paths: [process.cwd()] }));
  let counter = 0;
  const block = (tag) => ethers.getBytes(ethers.keccak256(ethers.toUtf8Bytes(`cvin-seed:${SEED}:${tag}:${counter++}`)));

  ethers.Wallet.createRandom = function createRandomSeeded(provider) {
    return new ethers.Wallet(ethers.hexlify(block("wallet")), provider || null);
  };

  const seededBytes = (length) => {
    const out = new Uint8Array(length);
    for (let i = 0; i < length; i += 32) out.set(block("bytes").slice(0, Math.min(32, length - i)), i);
    return out;
  };
  // ethers v6 exposes its API twice: the module and the `ethers` namespace object (which Hardhat copies from)
  for (const target of [ethers, ethers.ethers].filter(Boolean)) {
    Object.defineProperty(target, "randomBytes", { configurable: true, enumerable: true, get: () => seededBytes });
  }

  module.exports = { seed: SEED, active: true };
} else {
  module.exports = { seed: null, active: false };
}
