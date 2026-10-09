// I4 of the infrastructure-messaging pre-registration (docs/design/INFRASTRUCTURE_PREREG.md):
// what an RSU identity costs on chain, on the upstream ERC-1056 registry (EthereumDIDRegistry).
// Reported, no verdict. Exact receipt.gasUsed on the Hardhat in-process network (condition M1).
//
//   npx hardhat run scripts/infrastructure_gas.js
//   -> ../4_comparison-framework/results/infrastructure_gas.json
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

async function main() {
  const [deployer, authority] = await ethers.getSigners();
  const F = await ethers.getContractFactory("contracts/ERC1056/EthereumDIDRegistry.sol:EthereumDIDRegistry", deployer);
  const reg = await F.deploy();
  await reg.waitForDeployment();

  // an RSU is a fresh key; its did:ethr exists implicitly (no transaction)
  const rsu = ethers.Wallet.createRandom().connect(ethers.provider);
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
  const newPub = ethers.Wallet.createRandom().signingKey.publicKey;
  out.rotate_key_by_authority = { gasUsed: await gas(reg.connect(authority).setAttribute(rsu.address, KEY_ATTR, newPub, YEAR)),
    note: "authority rotates the RSU key (new attribute; the old one stays until it expires or is revoked)" };
  out.revoke_old_key = { gasUsed: await gas(reg.connect(authority).revokeAttribute(rsu.address, KEY_ATTR, pub)),
    note: "revokeAttribute of the old key (ERC-1056 has no identity-level revocation; the credential registry is the revocation path for messages)" };

  const net = await ethers.provider.getNetwork();
  const result = {
    metadata: {
      experiment: "I4 infrastructure identity gas", prereg: "docs/design/INFRASTRUCTURE_PREREG.md",
      contract: "contracts/ERC1056/EthereumDIDRegistry.sol:EthereumDIDRegistry", network: "hardhat-local",
      chainId: Number(net.chainId), solcVersion: "0.8.24", date: new Date().toISOString(), condition: "M1", ...runStamp(),
    },
    operations: out,
  };
  const file = path.resolve(__dirname, "../../4_comparison-framework/results/infrastructure_gas.json");
  fs.writeFileSync(file, JSON.stringify(result, null, 2));
  for (const [k, v] of Object.entries(out)) console.log(`${k.padEnd(28)} ${String(v.gasUsed).padStart(8)}`);
  console.log("written", file);
}

main().catch((e) => { console.error(e); process.exit(1); });
