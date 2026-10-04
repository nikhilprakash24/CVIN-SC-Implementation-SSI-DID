'use strict';
/**
 * erc-725xy / vin-linkage — VIN_KEY and getVehicleVIN: the VIN lives in the identity's own
 * store (forward link identity -> VIN, on-chain readable); there is no VIN -> identity index
 * and the owner can overwrite the VIN at will.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-725xy/demos/vin-linkage.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-725xy';
const FAMILY = 'vin-linkage';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
const tx = async (step, fn, p, note) => { const r = await (await p).wait(); out(step, fn, true, r.gasUsed, note); return r; };
const view = async (step, fn, p, note) => { const v = await p; out(step, fn, true, 0, typeof note === 'function' ? note(v) : note); return v; };
const assert = (c, m) => { if (!c) throw new Error(`assertion failed: ${m}`); };
const h = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));
const b = (s) => ethers.hexlify(ethers.toUtf8Bytes(s));
const utf8 = (x) => ethers.toUtf8String(x);
const short = (a) => `${String(a).slice(0, 10)}…`;

const CONTRACT = 'CVINVehicleERC725XY';
const VIN = '1HGCM82633A004352';
const VIN2 = 'WBA3A5C58DF586741';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy(vehicleOwner.address);
  out('deploy-identity', `${CONTRACT}.constructor`, true, (await c.deploymentTransaction().wait()).gasUsed, 'per-vehicle account');
  const id = await c.getAddress();

  const VIN_KEY = await view('VIN_KEY', `${CONTRACT}.VIN_KEY`, c.VIN_KEY(), (v) => `VIN_KEY = keccak256("cvin:vin") = ${short(v)}`);
  assert(VIN_KEY === h('cvin:vin'), 'VIN_KEY');
  assert((await view('getVehicleVIN-empty', `${CONTRACT}.getVehicleVIN`, c.getVehicleVIN(), (v) => `getVehicleVIN() == "${v}" before anchoring`)) === '', 'empty');
  await tx('setData-VIN', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(VIN_KEY, b(VIN)), `MEASURED (benchmark updateAttribute = setData(VIN_KEY)): VIN ${VIN} anchored in the identity's own store`);
  assert((await view('getVehicleVIN', `${CONTRACT}.getVehicleVIN`, c.getVehicleVIN(), (v) => `getVehicleVIN() == ${v} (string view; any contract can read it)`)) === VIN, 'vin');
  assert(utf8(await view('getData-VIN', `${CONTRACT}.getData`, c.getData(VIN_KEY), (v) => `getData(VIN_KEY) == "${utf8(v)}" (raw bytes)`)) === VIN, 'raw');
  await tx('setData-VIN-overwrite', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(VIN_KEY, b(VIN2)), `OBSERVATION: the owner can overwrite the VIN (now ${VIN2}) — no immutability, no format check (17 chars not enforced), no uniqueness across identities`);
  assert((await c.getVehicleVIN()) === VIN2, 'overwritten');
  await tx('setData-VIN-garbage', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(VIN_KEY, b('not-a-vin')), 'any bytes are accepted as "VIN"');
  await tx('setData-VIN-restore', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(VIN_KEY, b(VIN)), 'restored');
  const c2 = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy(newOwner.address);
  await c2.deploymentTransaction().wait();
  await tx('second-identity-same-VIN', `${CONTRACT}.setData`, c2.connect(newOwner).setData(VIN_KEY, b(VIN)), `a second account claims the SAME VIN ${VIN}: nothing prevents it — uniqueness/veracity must come from an off-chain registry or a signed claim (ERC-735)`);
  assert((await c2.getVehicleVIN()) === VIN, 'duplicate VIN');
  out('no-reverse-index', `${CONTRACT}.getVehicleVIN`, true, 0, 'there is no VIN -> identity lookup (per-vehicle contracts have no shared index): resolving a VIN requires an off-chain index built from DataChanged(VIN_KEY) events across all accounts');
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(id);
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve-vin', 'adapter.resolve', true, 0, `resolve -> vehicle.vin=${doc.vehicle.vin} (from getDataBatch); the did:erc725 document carries the VIN as data, not as an attestation`);
  assert(doc.vehicle.vin === VIN, 'resolve vin');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
