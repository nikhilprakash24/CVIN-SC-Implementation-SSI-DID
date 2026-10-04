'use strict';
/**
 * erc-1056-uport / authorisation-roles — the wrapper's manufacturer role: owner-only
 * setAuthorizedManufacturer, the authorizedManufacturers mapping, ManufacturerAuthorized events,
 * and the fact that the wrapper owner itself is immutable.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-uport/demos/authorisation-roles.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-uport';
const FAMILY = 'authorisation-roles';
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

const CAR = ['Honda', 'Civic', 2021, 'Red', 'L15B7-2021-5519', 1609459200, 'L2'];

async function main() {
  const [deployer, vehicleOwner, newOwner, , stranger, manufacturer] = await ethers.getSigners();
  const registry = await (await ethers.getContractFactory('EthereumDIDRegistry', deployer)).deploy();
  out('deploy-registry', 'EthereumDIDRegistry.constructor', true, (await registry.deploymentTransaction().wait()).gasUsed, 'shared did:ethr registry: NO roles at all — every address is its own authority');
  const wrapper = await (await ethers.getContractFactory('CVINVehicleDIDRegistry', deployer)).deploy(await registry.getAddress());
  out('deploy-wrapper', 'CVINVehicleDIDRegistry.constructor', true, (await wrapper.deploymentTransaction().wait()).gasUsed, 'VIN wrapper: constructor makes msg.sender owner AND first authorized manufacturer');

  assert((await view('owner', 'CVINVehicleDIDRegistry.owner', wrapper.owner(), (v) => `wrapper owner == ${short(v)} (deployer); the role administrator`)) === deployer.address, 'owner');
  assert((await view('authorizedManufacturers-deployer', 'CVINVehicleDIDRegistry.authorizedManufacturers', wrapper.authorizedManufacturers(deployer.address), (v) => `authorizedManufacturers[deployer] == ${v}`)) === true, 'deployer authorised');
  assert((await view('authorizedManufacturers-oem', 'CVINVehicleDIDRegistry.authorizedManufacturers', wrapper.authorizedManufacturers(manufacturer.address), (v) => `authorizedManufacturers[OEM ${short(manufacturer.address)}] == ${v} (not yet)`)) === false, 'OEM not authorised');
  await reverts('oem-create-before-grant', 'CVINVehicleDIDRegistry.createVehicleDID', wrapper.connect(manufacturer).createVehicleDID('2HGFC2F59MH501234', vehicleOwner.address, ...CAR), 'not authorized manufacturer', 'the role gates VIN-bound creation (the chain enforces WHO may bind a VIN; it cannot check the VIN is real)');
  const rg = await tx('setAuthorizedManufacturer-grant', 'CVINVehicleDIDRegistry.setAuthorizedManufacturer', wrapper.connect(deployer).setAuthorizedManufacturer(manufacturer.address, true), 'owner grants the OEM role; ManufacturerAuthorized(manufacturer, true); not measured');
  const e = eventsOf(rg, wrapper, 'ManufacturerAuthorized');
  assert(e.length === 1 && e[0].args.authorized === true, 'ManufacturerAuthorized');
  await tx('oem-create-after-grant', 'CVINVehicleDIDRegistry.createVehicleDID', wrapper.connect(manufacturer).createVehicleDID('2HGFC2F59MH501234', vehicleOwner.address, ...CAR), 'OEM creates the VIN-bound DID');
  await tx('setAuthorizedManufacturer-revoke', 'CVINVehicleDIDRegistry.setAuthorizedManufacturer', wrapper.connect(deployer).setAuthorizedManufacturer(manufacturer.address, false), 'owner revokes the OEM role; ManufacturerAuthorized(manufacturer, false)');
  await reverts('oem-create-after-revoke', 'CVINVehicleDIDRegistry.createVehicleDID', wrapper.connect(manufacturer).createVehicleDID('2HGFC2F59MH501235', newOwner.address, ...CAR), 'not authorized manufacturer', 'role revocation is immediate; DIDs already created are unaffected');
  await reverts('grant-by-stranger', 'CVINVehicleDIDRegistry.setAuthorizedManufacturer', wrapper.connect(stranger).setAuthorizedManufacturer(stranger.address, true), 'CVINRegistry: not owner', 'only the wrapper owner administers roles');
  assert(typeof wrapper.transferOwnership === 'undefined', 'no wrapper transferOwnership');
  out('owner-immutable', 'CVINVehicleDIDRegistry.owner', true, 0, 'OBSERVATION: the wrapper has no transferOwnership/renounce — the role administrator is fixed at deployment (single point of control for all VIN bindings)');
  out('registry-has-no-roles', 'EthereumDIDRegistry.identityOwner', true, 0, 'contrast: EthereumDIDRegistry has no roles — any address may mutate its own DID without permission; the manufacturer role exists only in the CVIN wrapper layer and is never measured by the comparison');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
