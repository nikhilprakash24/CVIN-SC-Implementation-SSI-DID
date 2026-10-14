// I4 of the infrastructure-messaging pre-registration (docs/design/INFRASTRUCTURE_PREREG.md):
// what an RSU identity costs on chain, on the upstream ERC-1056 registry (EthereumDIDRegistry).
// Reported, no verdict. Exact receipt.gasUsed on the Hardhat in-process network (condition M1).
//
//   npx hardhat run scripts/infrastructure_gas.js                    # seed 1, the run of record
//   -> ../4_comparison-framework/results/infrastructure_gas.json
//   I4_SEEDS=1-30 npx hardhat run scripts/infrastructure_gas.js      # the range study, one run per seed
//   -> ../4_comparison-framework/results/infrastructure_gas_runs/run_<seed>.json and summary.json
//
// WM-2 B1 (N-18): the RSU keys come from a declared seed and are recorded with each result. The key changes
// calldata zero bytes and so gas (EIP-2028); that cost is the thing measured, so it is reported as a range over
// declared seeds, reproducible run after run (rule: register §1, guide 1.1.10). Before B1 the keys were random
// and unrecorded (#47).
const fs = require("fs");
const path = require("path");
const { ethers } = require("hardhat");
const { runStamp } = require("./lib/run_stamp");

const KEY_ATTR = ethers.encodeBytes32String("did/pub/Secp256k1/veriKey/hex");
const SVC_ATTR = ethers.encodeBytes32String("did/svc/SPaTService");
const YEAR = 365 * 24 * 3600;

async function gas(txp) {
  const r = await (await txp).wait();
  return Number(r.gasUsed);
}

function seeds() {
  const spec = process.env.I4_SEEDS || "1";
  const m = spec.match(/^(\d+)-(\d+)$/);
  if (m) return Array.from({ length: Number(m[2]) - Number(m[1]) + 1 }, (_, i) => Number(m[1]) + i);
  return spec.split(",").map((x) => Number(x.trim()));
}

async function runOnce(seed) {
  const [deployer, authority] = await ethers.getSigners();
  const F = await ethers.getContractFactory("contracts/ERC1056/EthereumDIDRegistry.sol:EthereumDIDRegistry", deployer);
  const reg = await F.deploy();
  await reg.waitForDeployment();

  // an RSU is a fresh key; its did:ethr exists implicitly (no transaction)
  const rsu = new ethers.Wallet(ethers.id(`I4-rsu-key:${seed}`), ethers.provider);
  await (await deployer.sendTransaction({ to: rsu.address, value: ethers.parseEther("1") })).wait();
  const pub = rsu.signingKey.publicKey; // 65-byte uncompressed point

  const out = {};
  out.create_identity = { gasUsed: 0, note: "did:ethr is implicit: identityOwner(rsu) = rsu until changed" };
  out.anchor_key_by_rsu = { gasUsed: await gas(reg.connect(rsu).setAttribute(rsu.address, KEY_ATTR, pub, YEAR)),
    note: "RSU publishes its verification key (setAttribute, 1 year)" };
  out.anchor_service_endpoint = { gasUsed: await gas(reg.connect(rsu).setAttribute(rsu.address, SVC_ATTR,
    ethers.toUtf8Bytes("https://rsu.example/int_1/spat"), YEAR)), note: "SPaT service endpoint attribute" };
  out.hand_control_to_authority = { gasUsed: await gas(reg.connect(rsu).changeOwner(rsu.address, authority.address)),
    note: "changeOwner: the road authority controls the RSU's identity from here on" };
  const newPub = new ethers.Wallet(ethers.id(`I4-rsu-rotated-key:${seed}`)).signingKey.publicKey;
  out.rotate_key_by_authority = { gasUsed: await gas(reg.connect(authority).setAttribute(rsu.address, KEY_ATTR, newPub, YEAR)),
    note: "authority rotates the RSU key (new attribute; the old one stays until it expires or is revoked)" };
  out.revoke_old_key = { gasUsed: await gas(reg.connect(authority).revokeAttribute(rsu.address, KEY_ATTR, pub)),
    note: "revokeAttribute of the old key (ERC-1056 has no identity-level revocation; the credential registry is the revocation path for messages)" };

  const net = await ethers.provider.getNetwork();
  return {
    metadata: {
      experiment: "I4 infrastructure identity gas", prereg: "docs/design/INFRASTRUCTURE_PREREG.md",
      contract: "contracts/ERC1056/EthereumDIDRegistry.sol:EthereumDIDRegistry", network: "hardhat-local",
      chainId: Number(net.chainId), solcVersion: "0.8.24", date: new Date().toISOString(), condition: "M1", ...runStamp(__filename),
      seed, inputs: { rsu_address: rsu.address, rsu_public_key: pub, rotated_public_key: newPub },
    },
    operations: out,
  };
}

async function main() {
  const list = seeds();
  const results = [];
  for (const seed of list) {
    results.push(await runOnce(seed));
    const ops = results[results.length - 1].operations;
    console.log(`seed ${seed}: ` + Object.entries(ops).map(([k, v]) => `${k}=${v.gasUsed}`).join(" "));
  }
  const dir = path.resolve(__dirname, "../../4_comparison-framework/results");
  if (list.length === 1) {
    const file = path.join(dir, "infrastructure_gas.json");
    fs.writeFileSync(file, JSON.stringify(results[0], null, 2));
    console.log("written", file);
    return;
  }
  const runs = path.join(dir, "infrastructure_gas_runs");
  fs.mkdirSync(runs, { recursive: true });
  for (const r of results) fs.writeFileSync(path.join(runs, `run_${String(r.metadata.seed).padStart(2, "0")}.json`), JSON.stringify(r, null, 2));
  const operations = {};
  for (const op of Object.keys(results[0].operations)) {
    const vals = results.map((r) => r.operations[op].gasUsed);
    const counts = {};
    for (const v of vals) counts[v] = (counts[v] || 0) + 1;
    const mode = Number(Object.entries(counts).sort((a, b) => b[1] - a[1] || Number(a[0]) - Number(b[0]))[0][0]);
    operations[op] = { min: Math.min(...vals), max: Math.max(...vals), values: [...new Set(vals)].sort((a, b) => a - b), mode, counts };
  }
  const summary = {
    about: "I4 over declared seeds (WM-2 B1): RSU keys derived from each seed and recorded per run; gas varies with the keys' calldata zero bytes (EIP-2028). A second run with the same seeds reproduces every value.",
    seeds: list, commit: [...new Set(results.map((r) => r.metadata.commit))], dirty: [...new Set(results.map((r) => r.metadata.dirty))],
    operations,
  };
  fs.writeFileSync(path.join(runs, "summary.json"), JSON.stringify(summary, null, 2));
  console.log("written", runs);
}

main().catch((e) => { console.error(e); process.exit(1); });
