'use strict';
/**
 * erc-725 / creation — the identity IS a contract: deploying CVIN_SCBasedAccOrID_DID_ERC725Basic
 * is the creation (constructor makes msg.sender the owner / MANAGEMENT key). No registry, no
 * VIN storage, one deployment per vehicle.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-725/demos/creation.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-725';
const FAMILY = 'creation';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
const view = async (step, fn, p, note) => { const v = await p; out(step, fn, true, 0, typeof note === 'function' ? note(v) : note); return v; };
const assert = (c, m) => { if (!c) throw new Error(`assertion failed: ${m}`); };
const eventsOf = (receipt, c, name) => receipt.logs.map((l) => { try { return c.interface.parseLog(l); } catch (_) { return null; } }).filter((e) => e && e.name === name);
const short = (a) => `${String(a).slice(0, 10)}…`;

const CONTRACT = 'CVIN_SCBasedAccOrID_DID_ERC725Basic';
const VIN = '1HGCM82633A004352';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  const d = await ad.deploy();
  out('deploy-registry', 'adapter.deploy', true, d.gasUsed, `no shared registry: ${d.note}`);

  const F = await ethers.getContractFactory(CONTRACT, vehicleOwner);
  const c = await F.deploy();
  const r = await c.deploymentTransaction().wait();
  const id = await c.getAddress();
  out('deploy-identity', `${CONTRACT}.constructor`, true, r.gasUsed, `MEASURED (createIdentity = proxy deployment, L1 create 519,384): identity id = contract address ${short(id)}; constructor stores msg.sender as owner and emits OwnershipTransferred(0 -> owner)`);
  const ev = eventsOf(r, c, 'OwnershipTransferred');
  assert(ev.length === 1 && ev[0].args.previousOwner === ethers.ZeroAddress && ev[0].args.newOwner === vehicleOwner.address, 'OwnershipTransferred');
  assert((await view('owner', `${CONTRACT}.owner`, c.owner(), (v) => `owner == ${short(v)} (deployer of the proxy = vehicle owner / MANAGEMENT key)`)) === vehicleOwner.address, 'owner');
  assert((await view('getKeys-empty', `${CONTRACT}.getKeys`, c.getKeys(), (v) => `getKeys() -> ${v.length} keys: the fresh identity has NO verification material except the owner EOA`)) .length === 0, 'no keys');
  const code = await ethers.provider.getCode(id);
  out('bytecode-size', `${CONTRACT}.constructor`, true, 0, `runtime bytecode ${(code.length - 2) / 2} bytes deployed per vehicle — the cost scales with the fleet, unlike a shared registry`);
  out('no-vin-storage', `${CONTRACT}.owner`, true, 0, `VIN ${VIN} is NOT stored anywhere: the basic ERC-725 proxy has no data store (VIN linkage N/A); a VIN<->identity index must live off-chain or in ERC-725Y (erc-725xy option)`);

  const c2 = await ad.create({ vin: VIN, owner: newOwner.address });
  out('adapter-create', `${CONTRACT}.constructor`, true, c2.gasUsed, `adapter.create for a second vehicle: ${c2.note}`);
  assert(c2.id !== id, 'distinct contract per vehicle');
  const c3 = await ad.create({ vin: VIN, owner: ethers.Wallet.createRandom().address });
  out('adapter-create-foreign-owner', `${CONTRACT}.transferOwnership`, true, c3.gasUsed, `owner without a local signer: deploy by deployer + transferOwnership: ${c3.note}`);
  out('creation-asymmetry', `${CONTRACT}.constructor`, true, 0, 'creation is DEPLOYED (not implicit, not minted): the comparison counts the full deployment under createIdentity, so ERC-725 pays ~7x the ERC-1056 "create" but owns an on-chain account afterwards');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
