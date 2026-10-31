'use strict';
/**
 * erc-1056-vehicle / controller — owners / identityOwner / changeOwner; no signed variant;
 * changeOwner(id, 0x0) restores self-control.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-vehicle/demos/controller.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-vehicle';
const FAMILY = 'controller';
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

async function main() {
  const [deployer, vehicleOwner, newOwner, , stranger] = await ethers.getSigners();
  const registry = await (await ethers.getContractFactory('ERC1056Registry', deployer)).deploy();
  out('deploy-registry', 'ERC1056Registry.constructor', true, (await registry.deploymentTransaction().wait()).gasUsed, 'shared registry');
  const id = vehicleOwner.address;
  await tx('registerVehicle', 'ERC1056Registry.registerVehicle', registry.connect(vehicleOwner).registerVehicle(id, '0x04' + 'ab'.repeat(64)), 'vehicle registers itself');

  assert((await view('owners-default', 'ERC1056Registry.owners', registry.owners(id), (v) => `owners[id] == ${v} (zero: self-owned)`)) === ethers.ZeroAddress, 'default');
  assert((await view('identityOwner', 'ERC1056Registry.identityOwner', registry.identityOwner(id), (v) => `identityOwner == ${short(v)}`)) === id, 'self');
  await reverts('changeOwner-by-stranger', 'ERC1056Registry.changeOwner', registry.connect(stranger).changeOwner(id, stranger.address), 'Only owner can perform this action', 'only the current controller rotates');
  const r = await tx('changeOwner', 'ERC1056Registry.changeOwner', registry.connect(vehicleOwner).changeOwner(id, newOwner.address),
    'controller rotation (vehicle sale / key compromise): 1 SSTORE + DIDOwnerChanged; the identifier (vehicle address) is unchanged; not measured by #21/#29 (L1 controller-change: 51,669 gas)');
  const e = eventsOf(r, registry, 'DIDOwnerChanged');
  assert(e.length === 1 && e[0].args.owner === newOwner.address, 'DIDOwnerChanged');
  assert((await view('owners-after', 'ERC1056Registry.owners', registry.owners(id), (v) => `owners[id] == ${short(v)}`)) === newOwner.address, 'stored');
  assert((await view('identityOwner-after', 'ERC1056Registry.identityOwner', registry.identityOwner(id), (v) => `identityOwner == ${short(v)} (new controller)`)) === newOwner.address, 'rotated');
  await reverts('old-controller-locked-out', 'ERC1056Registry.changeOwner', registry.connect(vehicleOwner).changeOwner(id, id), 'Only owner can perform this action', 'the vehicle account itself can no longer act for its DID');
  await reverts('setAttribute-by-old-controller', 'ERC1056Registry.setAttribute', registry.connect(vehicleOwner).setAttribute(id, ethers.id('x'), '0x01', 60), 'Only owner can perform this action', 'all mutations follow the controller');
  await tx('changeOwner-to-zero', 'ERC1056Registry.changeOwner', registry.connect(newOwner).changeOwner(id, ethers.ZeroAddress), 'setting the owner to address(0) …');
  assert((await view('identityOwner-after-zero', 'ERC1056Registry.identityOwner', registry.identityOwner(id), (v) => `… identityOwner == ${short(v)} (the vehicle itself again): OBSERVATION — zero-owner restores self-control; to decommission use revokeIdentity instead`)) === id, 'self again');
  assert(typeof registry.changeOwnerSigned === 'undefined', 'no signed variant');
  out('no-signed-variant', 'ERC1056Registry.nonce', true, 0, `nonce[id] == ${await registry.nonce(id)} and the ABI has no changeOwnerSigned: this profile dropped the ERC-1056 meta-transactions (signed-execution N/A), so the vehicle must pay its own gas`);
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
