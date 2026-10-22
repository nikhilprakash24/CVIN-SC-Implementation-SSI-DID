'use strict';
/**
 * erc-1056-uport / creation — implicit identity (0 gas) versus the explicit, VIN-bound
 * CVINVehicleDIDRegistry.createVehicleDID path the comparison never uses.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-uport/demos/creation.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-uport';
const FAMILY = 'creation';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
const tx = async (step, fn, p, note) => { const r = await (await p).wait(); out(step, fn, true, r.gasUsed, note); return r; };
const view = async (step, fn, p, note) => { const v = await p; out(step, fn, true, 0, typeof note === 'function' ? note(v) : note); return v; };
const reverts = async (step, fn, p, reason, note) => {
  let msg = null;
  try { const t = await p; if (t && typeof t.wait === 'function') await t.wait(); } catch (e) { msg = String(e.message || e); const d = e.data || (e.error && e.error.data); if (typeof d === 'string' && d.startsWith('0x08c379a0')) { try { msg += ' | ' + ethers.AbiCoder.defaultAbiCoder().decode(['string'], '0x' + d.slice(10))[0]; } catch (_) { /* not Error(string) */ } } }
  if (msg === null) throw new Error(`${step}: expected revert "${reason}" but the call succeeded`);
  if (!msg.includes(reason)) throw new Error(`${step}: expected revert "${reason}", got: ${msg}`);
  out(step, fn, true, 0, `reverted as expected ("${reason}"): ${note}`);
};
const assert = (c, m) => { if (!c) throw new Error(`assertion failed: ${m}`); };
const eventsOf = (receipt, c, name) => receipt.logs.map((l) => { try { return c.interface.parseLog(l); } catch (_) { return null; } }).filter((e) => e && e.name === name);
const short = (a) => `${String(a).slice(0, 10)}…`;

const VIN = '1HGCM82633A004352';
const CAR = ['Honda', 'Accord', 2003, 'Silver', 'K24A4-2003-0471', 1041379200, 'L0'];

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate, stranger] = await ethers.getSigners();

  const R = await ethers.getContractFactory('EthereumDIDRegistry', deployer);
  const registry = await R.deploy();
  const r1 = await registry.deploymentTransaction().wait();
  out('deploy-registry', 'EthereumDIDRegistry.constructor', true, r1.gasUsed, 'single shared did:ethr registry, deployed once per network (comparison: deployRegistry)');
  const W = await ethers.getContractFactory('CVINVehicleDIDRegistry', deployer);
  const wrapper = await W.deploy(await registry.getAddress());
  const r2 = await wrapper.deploymentTransaction().wait();
  out('deploy-wrapper', 'CVINVehicleDIDRegistry.constructor', true, r2.gasUsed, 'VIN wrapper; deployer becomes contract owner and first authorized manufacturer (not measured)');

  // ---- implicit creation: the identity exists before any transaction ----
  const o = await view('implicit-identity', 'EthereumDIDRegistry.identityOwner', registry.identityOwner(vehicleOwner.address),
    (v) => `identityOwner(${short(vehicleOwner.address)}) == ${short(v)} (itself) before any transaction: identity exists implicitly at 0 gas (comparison counts the first setAttribute as createIdentity)`);
  assert(o === vehicleOwner.address, 'implicit identity owns itself');
  const ch = await view('no-history-yet', 'EthereumDIDRegistry.changed', registry.changed(vehicleOwner.address), 'changed == 0: the implicit identity has no on-chain history, yet it is already a valid DID');
  assert(ch === 0n, 'changed is 0');

  // ---- the comparison's "createIdentity": first setAttribute publishing a verification key ----
  const pub = ethers.hexlify(ethers.randomBytes(33));
  await tx('first-setAttribute-as-creation', 'EthereumDIDRegistry.setAttribute',
    registry.connect(vehicleOwner).setAttribute(vehicleOwner.address, ethers.keccak256(ethers.toUtf8Bytes('did/pub/secp256k1/veriKey')), pub, 31536000),
    'what the comparison measures as createIdentity (benchmark_ops.createIdentity): publishing the first verification key; event-only');

  // ---- explicit VIN-bound creation (manifest: implemented, not measured) ----
  const rc = await tx('createVehicleDID', 'CVINVehicleDIDRegistry.createVehicleDID',
    wrapper.connect(deployer).createVehicleDID(VIN, vehicleOwner.address, ...CAR),
    'explicit creation by an authorized manufacturer: stores vin<->DID (2 SSTOREs) and emits VehicleDIDCreated; the DID is the owner address; NOT measured in the comparison');
  const ev = eventsOf(rc, wrapper, 'VehicleDIDCreated');
  assert(ev.length === 1 && ev[0].args.did === vehicleOwner.address && ev[0].args.vin === VIN && ev[0].args.manufacturer === deployer.address, 'VehicleDIDCreated args');
  out('event-VehicleDIDCreated', 'CVINVehicleDIDRegistry.createVehicleDID', true, 0, `VehicleDIDCreated(did=${short(ev[0].args.did)}, vin=${VIN}, owner=${short(ev[0].args.owner)}, manufacturer=${short(ev[0].args.manufacturer)}) decoded from the receipt`);
  const did = await view('getDIDFromVIN', 'CVINVehicleDIDRegistry.getDIDFromVIN', wrapper.getDIDFromVIN(VIN), (v) => `VIN ${VIN} -> DID ${short(v)} (vinToDID is keyed by keccak256(vin))`);
  assert(did === vehicleOwner.address, 'getDIDFromVIN');
  const vin = await view('didToVIN', 'CVINVehicleDIDRegistry.didToVIN', wrapper.didToVIN(vehicleOwner.address), (v) => `reverse mapping DID -> VIN = ${v}`);
  assert(vin === VIN, 'didToVIN');
  const ch2 = await view('changed-untouched-by-wrapper', 'EthereumDIDRegistry.changed', registry.changed(vehicleOwner.address),
    (v) => `changed == ${v}: createVehicleDID does not touch the ERC-1056 registry; the VIN mapping is wrapper state only and does not appear in the did:ethr event history (a resolver must query the wrapper separately)`);
  assert(ch2 > 0n && ch2 < BigInt(rc.blockNumber), 'changed reflects the earlier setAttribute only, not createVehicleDID');

  // ---- guards ----
  await reverts('reject-short-vin', 'CVINVehicleDIDRegistry.createVehicleDID',
    wrapper.connect(deployer).createVehicleDID('1HGCM82633A00435', newOwner.address, ...CAR), 'invalid VIN length', 'the chain enforces the 17-character VIN format (no check-digit validation)');
  await reverts('reject-duplicate-vin', 'CVINVehicleDIDRegistry.createVehicleDID',
    wrapper.connect(deployer).createVehicleDID(VIN, newOwner.address, ...CAR), 'VIN already registered', 'VIN uniqueness enforced on-chain');
  await reverts('reject-unauthorized-manufacturer', 'CVINVehicleDIDRegistry.createVehicleDID',
    wrapper.connect(stranger).createVehicleDID('WBA3A5C58DF586741', newOwner.address, ...CAR), 'not authorized manufacturer', 'only authorized manufacturers create VIN-bound DIDs (see authorisation-roles demo)');

  // ---- adapter view of both paths ----
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach({ registry: await registry.getAddress(), wrapper: await wrapper.getAddress() });
  const c1 = await ad.create({ vin: 'WBA3A5C58DF586741', owner: newOwner.address, implicit: true });
  out('adapter-create-implicit', 'adapter.create', true, c1.gasUsed, `adapter implicit path: ${c1.note}`);
  const c2 = await ad.create({ vin: 'WBA3A5C58DF586741', owner: newOwner.address });
  out('adapter-create-explicit', 'adapter.create', true, c2.gasUsed, `adapter explicit path (createVehicleDID): ${c2.note}`);
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
