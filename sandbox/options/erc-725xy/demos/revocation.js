'use strict';
/**
 * erc-725xy / revocation — no identity-level revocation primitive: a data key can be cleared
 * with setData(key, 0x) (DataChanged with empty value, storage refund) and control can be
 * renounced; neither is a status a verifier can query as "revoked".
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-725xy/demos/revocation.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-725xy';
const FAMILY = 'revocation';
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

const CONTRACT = 'CVINVehicleERC725XY';
const VIN = '1HGCM82633A004352';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy(vehicleOwner.address);
  out('deploy-identity', `${CONTRACT}.constructor`, true, (await c.deploymentTransaction().wait()).gasUsed, 'per-vehicle account');
  const id = await c.getAddress();
  const INSP = h('cvin:inspection');
  await tx('setData-VIN', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(await c.VIN_KEY(), b(VIN)), 'VIN anchored');
  const r0 = await tx('setData-inspection', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(INSP, b('APK:2026-03-14:PASS')), 'inspection record to be "revoked"');

  const r1 = await tx('setData-clear', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(INSP, '0x'),
    'MEASURED-as-revoke by L1 (33,870): setData(key, 0x) — a non-standard attribute clear; DataChanged(key, 0x) and an SSTORE refund (compare with the write cost above)');
  const ev = eventsOf(r1, c, 'DataChanged');
  assert(ev.length === 1 && ev[0].args.dataValue === '0x', 'cleared event');
  assert(r1.gasUsed < r0.gasUsed, 'refund makes clearing cheaper than writing');
  assert((await view('getData-cleared', `${CONTRACT}.getData`, c.getData(INSP), (v) => `getData(inspection) == ${v}: "cleared" is indistinguishable from "never set" — no tombstone, no reason, no timestamp`)) === '0x', 'cleared');
  assert(typeof c.isRevoked === 'undefined', 'no status');
  out('no-identity-revocation', `${CONTRACT}.owner`, true, 0, 'the ABI has no revoke/isRevoked: identity-level decommissioning is not expressible; verifiers would need a convention (e.g. a "cvin:status" data key) that the contract does not enforce');
  await tx('setData-status-convention', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(h('cvin:status'), b('DECOMMISSIONED')), 'such a convention costs one ordinary write and binds nobody: the owner can still change every other key afterwards');
  await tx('still-writable', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(INSP, b('APK:2026-09-01:PASS')), 'proof: data writes continue after the self-declared decommissioning');

  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(id);
  const na = await ad.revoke(id);
  assert(na.notApplicable === true, 'bare revoke N/A');
  out('adapter-revoke-bare', 'adapter.revoke', true, 0, `adapter.revoke(id) -> NotApplicable: ${na.reason}`);
  const rv = await ad.revoke({ id, key: 'cvin:inspection' });
  out('adapter-revoke-key', `${CONTRACT}.setData`, true, rv.gasUsed, `adapter.revoke({ id, key }) -> ${rv.note}`);

  await tx('renounceOwnership', `${CONTRACT}.renounceOwnership`, c.connect(vehicleOwner).renounceOwnership(), 'the only irreversible exit: freezes the account; the VIN and status keys stay readable forever');
  await reverts('frozen', `${CONTRACT}.setData`, c.connect(vehicleOwner).setData(INSP, '0x'), 'caller is not the owner', 'nothing can be cleared any more either');
  assert((await view('vin-still-readable', `${CONTRACT}.getVehicleVIN`, c.getVehicleVIN(), (v) => `getVehicleVIN() == ${v} after renounce: a frozen identity still asserts its VIN — verifiers must check owner()==0 themselves`)) === VIN, 'frozen but readable');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
