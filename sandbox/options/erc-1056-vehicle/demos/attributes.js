'use strict';
/**
 * erc-1056-vehicle / attributes — event-only setAttribute / revokeAttribute (validTo = now on
 * revocation), both gated by the revoked flag (revocation is terminal since the D21 fix).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-vehicle/demos/attributes.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-vehicle';
const FAMILY = 'attributes';
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
const h = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));
const b = (s) => ethers.hexlify(ethers.toUtf8Bytes(s));

const VIN = '5YJ3E1EA7KF317000';

async function main() {
  const [deployer, vehicleOwner, , , stranger] = await ethers.getSigners();
  const registry = await (await ethers.getContractFactory('ERC1056Registry', deployer)).deploy();
  out('deploy-registry', 'ERC1056Registry.constructor', true, (await registry.deploymentTransaction().wait()).gasUsed, 'shared registry');
  const id = vehicleOwner.address;
  await tx('registerVehicle', 'ERC1056Registry.registerVehicle', registry.connect(vehicleOwner).registerVehicle(id, '0x04' + 'ab'.repeat(64)), 'vehicle registers');

  const SVC = h('did/svc/telematics');
  const url = b('mqtts://v2x.example:8883/' + VIN);
  const rs = await tx('setAttribute-service', 'ERC1056Registry.setAttribute', registry.connect(vehicleOwner).setAttribute(id, SVC, url, 86400 * 30),
    'event-only (DIDAttributeChanged + changed pointer); not measured by #21/#29 (L1 attribute: 37,180 gas)');
  const e = eventsOf(rs, registry, 'DIDAttributeChanged')[0];
  assert(e.args.name === SVC && e.args.value === url, 'event');
  await tx('setAttribute-vin-offchain-style', 'ERC1056Registry.setAttribute', registry.connect(vehicleOwner).setAttribute(id, h('did/vehicle/vin'), b(VIN), 31536000 * 20),
    `the VIN can be published as an attribute by convention (not by the provider, which keeps it in the off-chain VC) — no uniqueness or format check, any string goes`);
  await reverts('setAttribute-by-stranger', 'ERC1056Registry.setAttribute', registry.connect(stranger).setAttribute(id, SVC, url, 60), 'Only owner can perform this action', 'owner-gated');
  assert(typeof registry.getAttribute === 'undefined', 'no getter');
  out('no-getter', 'ERC1056Registry.changed', true, 0, `no attribute getter in the ABI; changed[id] == ${await registry.changed(id)} is the only storage; the value is readable by replaying events only`);
  const rr = await tx('revokeAttribute', 'ERC1056Registry.revokeAttribute', registry.connect(vehicleOwner).revokeAttribute(id, SVC, url),
    'emits DIDAttributeChanged(validTo = block.timestamp) ("expired now"), not validTo = 0 as in the uPort registry; measured under #21/#29 revoke family');
  const rev = eventsOf(rr, registry, 'DIDAttributeChanged')[0];
  const blk = await ethers.provider.getBlock(rr.blockNumber);
  assert(rev.args.validTo === BigInt(blk.timestamp), 'validTo == now');
  await tx('revokeIdentity', 'ERC1056Registry.revokeIdentity', registry.connect(vehicleOwner).revokeIdentity(id), 'decommission the vehicle');
  await reverts('setAttribute-after-revoke', 'ERC1056Registry.setAttribute', registry.connect(vehicleOwner).setAttribute(id, SVC, url, 60), 'Identity is revoked', 'the revoked flag gates new attributes (the chain enforces decommissioning for writes)');
  await reverts('revokeAttribute-after-revoke', 'ERC1056Registry.revokeAttribute', registry.connect(vehicleOwner).revokeAttribute(id, h('did/vehicle/vin'), b(VIN)), 'Identity is revoked',
    'FIXED (D21, decision D-F): revocation is terminal — attribute revocation is blocked too (formerly clean-up stayed possible after identity revocation); a resolver treats every attribute of a revoked identity as void via isRevoked');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
