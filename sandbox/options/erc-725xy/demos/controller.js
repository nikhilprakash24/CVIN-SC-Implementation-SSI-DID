'use strict';
/**
 * erc-725xy / controller — owner / transferOwnership / renounceOwnership on the smart account:
 * the account address is the identity, the owner is the rotating controlling key.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-725xy/demos/controller.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-725xy';
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

const CONTRACT = 'CVINVehicleERC725XY';
const VIN = '1HGCM82633A004352';

async function main() {
  const [deployer, vehicleOwner, newOwner, , stranger] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy(vehicleOwner.address);
  out('deploy-identity', `${CONTRACT}.constructor`, true, (await c.deploymentTransaction().wait()).gasUsed, 'per-vehicle account owned by vehicleOwner');
  const id = await c.getAddress();
  await tx('setData-VIN', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(await c.VIN_KEY(), ethers.toUtf8Bytes(VIN)), 'VIN anchored by the first owner');

  assert((await view('owner', `${CONTRACT}.owner`, c.owner(), (v) => `owner == ${short(v)}; identity == ${short(id)}`)) === vehicleOwner.address, 'owner');
  await reverts('transferOwnership-by-stranger', `${CONTRACT}.transferOwnership`, c.connect(stranger).transferOwnership(stranger.address), 'caller is not the owner', 'owner-gated');
  await reverts('transferOwnership-to-zero', `${CONTRACT}.transferOwnership`, c.connect(vehicleOwner).transferOwnership(ethers.ZeroAddress), 'new owner is the zero address', 'zero guard (the basic ERC-725 proxy lacks it)');
  const r = await tx('transferOwnership', `${CONTRACT}.transferOwnership`, c.connect(vehicleOwner).transferOwnership(newOwner.address),
    'MEASURED (benchmark transferOwnership; L1 controller-change 28,822): vehicle sale = controlling-key rotation; the account address, its ETH and its data store stay');
  assert(eventsOf(r, c, 'OwnershipTransferred')[0].args.newOwner === newOwner.address, 'event');
  assert((await view('owner-after', `${CONTRACT}.owner`, c.owner(), (v) => `owner == ${short(v)}`)) === newOwner.address, 'rotated');
  assert((await view('data-survives', `${CONTRACT}.getVehicleVIN`, c.getVehicleVIN(), (v) => `getVehicleVIN() == ${v}: the data store travels with the identity, not with the key`)) === VIN, 'data persists');
  await reverts('old-owner-locked-out', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(ethers.id('x'), '0x01'), 'caller is not the owner', 'previous owner cannot write');
  await reverts('renounce-by-stranger', `${CONTRACT}.renounceOwnership`, c.connect(stranger).renounceOwnership(), 'caller is not the owner', 'owner-gated');
  await tx('renounceOwnership', `${CONTRACT}.renounceOwnership`, c.connect(newOwner).renounceOwnership(), 'owner -> 0: the account becomes ownerless but keeps its data (frozen identity); irreversible; not measured');
  assert((await view('owner-renounced', `${CONTRACT}.owner`, c.owner(), (v) => `owner == ${v}`)) === ethers.ZeroAddress, 'renounced');
  await reverts('frozen', `${CONTRACT}.setData`, c.connect(newOwner).setData(ethers.id('x'), '0x01'), 'caller is not the owner', 'no one can ever write or execute again; the VIN remains readable');
  assert((await c.getVehicleVIN()) === VIN, 'still readable');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
