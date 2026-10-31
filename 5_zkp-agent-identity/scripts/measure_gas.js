// Gas of the layer 5 contracts, condition M1 (Hardhat in-process EVM, solc 0.8.24, optimizer 200 + viaIR, cancun).
// Exact receipt.gasUsed from committed fixtures, so every value is deterministic (guide rule 1.1.8).
//   cd 1_blockchain-identity && npx hardhat --config hardhat.zkp.config.js run ../5_zkp-agent-identity/scripts/measure_gas.js
const fs = require("fs");
const path = require("path");
const req = require("module").createRequire(path.resolve(__dirname, "../../1_blockchain-identity/package.json"));
const hre = req("hardhat");
const { ethers } = hre;
const { runIdentity } = require("./zkvin_lib");

const ROOT = path.resolve(__dirname, "..");
const FIX = JSON.parse(fs.readFileSync(path.join(ROOT, "fixtures/zkvin_proof.json"), "utf8"));
const SCH = JSON.parse(fs.readFileSync(path.join(ROOT, "fixtures/schnorr_evm.json"), "utf8")).proof;
const ARTIFACT = path.resolve(ROOT, "../1_blockchain-identity/artifacts/contracts/ERC1056/EthereumDIDRegistry.sol/EthereumDIDRegistry.json");

async function gasOf(txPromise) {
  const tx = await txPromise;
  const r = await (tx.deploymentTransaction ? tx.deploymentTransaction().wait() : tx.wait());
  return Number(r.gasUsed);
}

async function main() {
  const [owner, agent] = await ethers.getSigners();
  const art = JSON.parse(fs.readFileSync(ARTIFACT, "utf8"));
  const registry = await new ethers.ContractFactory(art.abi, art.bytecode, owner).deploy();
  await registry.waitForDeployment();
  const g = {};
  const verifier = await (await ethers.getContractFactory("Groth16Verifier")).deploy();
  g.deploy_groth16_verifier = await gasOf(verifier);
  const gate = await (await ethers.getContractFactory("ZkVinGate")).deploy(
    await registry.getAddress(), await verifier.getAddress(), FIX.mfrRoot);
  g.deploy_zkvin_gate = await gasOf(gate);
  g.anchor_commitment = await gasOf(gate.anchorCommitment(owner.address, FIX.vehicle.commitment));
  const INS = ethers.id("insurer:acme");
  g.set_service = await gasOf(gate.setService(INS, FIX.request.scope, FIX.request.minModelYear, FIX.vehicle.region, FIX.request.challenge));
  const P = FIX.insurer;
  g.verify_proof_view_estimate = Number(await verifier.verifyProof.estimateGas(P.a, P.b, P.c, P.pub));
  g.admit_with_groth16 = await gasOf(gate.connect(agent).admit(owner.address, INS, P.a, P.b, P.c, P.pub, ethers.id("issue-policy-quote")));
  const sv = await (await ethers.getContractFactory("SchnorrEcrecoverVerifier")).deploy();
  g.deploy_schnorr_verifier = await gasOf(sv);
  g.schnorr_prove_tx = await gasOf(sv.prove(SCH.parity, SCH.px, SCH.message, SCH.e, SCH.s));
  g.schnorr_verify_view_estimate = Number(await sv.verify.estimateGas(SCH.parity, SCH.px, SCH.message, SCH.e, SCH.s));

  const out = {
    condition: "M1 (Hardhat in-process EVM, chain 31337, solc 0.8.24, optimizer 200 + viaIR, evm cancun); exact receipt.gasUsed; view figures are eth_estimateGas and include the 21,000 base",
    run: runIdentity(),
    hardhat: req("hardhat/package.json").version,
    gas: g,
    expectations: { "Z-E3 admit (on-chain Groth16 verification in the gate) < 350,000 gas": g.admit_with_groth16 < 350000 ? "PASS" : "FAIL" },
    reference: "Phase 1 ERC-1056 createIdentity 52,594 gas (register #6, M1) for scale",
  };
  fs.mkdirSync(path.join(ROOT, "results"), { recursive: true });
  fs.writeFileSync(path.join(ROOT, "results/gas_zk.json"), JSON.stringify(out, null, 2) + "\n");
  console.log(JSON.stringify(out.gas, null, 1), out.expectations);
}

main().catch((e) => { console.error(e); process.exit(1); });
