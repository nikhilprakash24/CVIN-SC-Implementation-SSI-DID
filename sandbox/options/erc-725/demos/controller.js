'use strict';
/**
 * erc-725 / controller — owner / transferOwnership / renounceOwnership: the account address is
 * the stable identifier, the owner is the rotating controlling key; renouncing bricks the
 * identity (no key can act afterwards).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-725/demos/controller.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-725';
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

const CONTRACT = 'CVIN_SCBasedAccOrID_DID_ERC725Basic';

async function main() {
  const [, vehicleOwner, newOwner, , stranger] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, vehicleOwner)).deploy();
  out('deploy-identity', `${CONTRACT}.constructor`, true, (await c.deploymentTransaction().wait()).gasUsed, 'per-vehicle proxy; vehicleOwner is owner');
  const id = await c.getAddress();
  const keyId = ethers.keccak256(ethers.AbiCoder.defaultAbiCoder().encode(['address'], [vehicleOwner.address]));
  await tx('addKey-management', `${CONTRACT}.addKey`, c.connect(vehicleOwner).addKey(keyId, 1, 1), 'owner registers itself as a MANAGEMENT key (purpose 1) for the record');

  assert((await view('owner', `${CONTRACT}.owner`, c.owner(), (v) => `owner == ${short(v)}; identity (account) == ${short(id)} stays fixed`)) === vehicleOwner.address, 'owner');
  await reverts('transferOwnership-by-stranger', `${CONTRACT}.transferOwnership`, c.connect(stranger).transferOwnership(stranger.address), 'Only owner can transfer ownership', 'owner-gated');
  const r = await tx('transferOwnership', `${CONTRACT}.transferOwnership`, c.connect(vehicleOwner).transferOwnership(newOwner.address),
    'MEASURED (benchmark transferOwnership; L1 controller-change 28,378): one warm SSTORE + OwnershipTransferred; the ERC-734 keys array is NOT touched — the old owner\'s MANAGEMENT key remains listed');
  const ev = eventsOf(r, c, 'OwnershipTransferred');
  assert(ev.length === 1 && ev[0].args.previousOwner === vehicleOwner.address && ev[0].args.newOwner === newOwner.address, 'event');
  assert((await view('owner-after', `${CONTRACT}.owner`, c.owner(), (v) => `owner == ${short(v)} (new controlling key)`)) === newOwner.address, 'rotated');
  await reverts('old-owner-locked-out', `${CONTRACT}.addKey`, c.connect(vehicleOwner).addKey(keyId, 2, 1), 'Only owner can add keys', 'the previous owner cannot act; but …');
  const k = await view('stale-management-key', `${CONTRACT}.getKey`, c.getKey(keyId), (v) => `getKey(oldOwnerKey) still returns purpose=${v[0]}: OBSERVATION — authorisation is decided by owner(), not by the key store; keys are descriptive, not authoritative (ERC-734 semantics are not enforced)`);
  assert(k[0] === 1n, 'stale key still present');
  await tx('transferOwnership-to-zero', `${CONTRACT}.transferOwnership`, c.connect(newOwner).transferOwnership(ethers.ZeroAddress), 'OBSERVATION: no zero-address guard on transferOwnership — this is equivalent to renounceOwnership');
  assert((await c.owner()) === ethers.ZeroAddress, 'zero owner');
  // fresh instance for renounceOwnership proper
  const c2 = await (await ethers.getContractFactory(CONTRACT, vehicleOwner)).deploy();
  out('deploy-identity-2', `${CONTRACT}.constructor`, true, (await c2.deploymentTransaction().wait()).gasUsed, 'second vehicle to demonstrate renounceOwnership');
  await reverts('renounceOwnership-by-stranger', `${CONTRACT}.renounceOwnership`, c2.connect(stranger).renounceOwnership(), 'Only owner can renounce ownership', 'owner-gated');
  await tx('renounceOwnership', `${CONTRACT}.renounceOwnership`, c2.connect(vehicleOwner).renounceOwnership(), 'owner -> address(0), OwnershipTransferred(owner, 0); not measured');
  assert((await view('owner-renounced', `${CONTRACT}.owner`, c2.owner(), (v) => `owner == ${v}`)) === ethers.ZeroAddress, 'renounced');
  await reverts('bricked-identity', `${CONTRACT}.transferOwnership`, c2.connect(vehicleOwner).transferOwnership(vehicleOwner.address), 'Only owner can transfer ownership', 'after renounce nobody can ever control the identity again — the closest thing to identity-level revocation, and it is irreversible');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
