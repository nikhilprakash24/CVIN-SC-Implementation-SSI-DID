'use strict';
/**
 * erc-725 / signed-execution — execute() in the basic proxy: owner-gated by msg.sender, no
 * signature, and it only EMITS Executed — no call is performed (proved against a real target).
 * approve() is an unimplemented no-op stub (public write not covered by any measured family).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-725/demos/signed-execution.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-725';
const FAMILY = 'signed-execution';
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
  const [deployer, vehicleOwner, newOwner, delegate, stranger] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, vehicleOwner)).deploy();
  out('deploy-identity', `${CONTRACT}.constructor`, true, (await c.deploymentTransaction().wait()).gasUsed, 'per-vehicle proxy');
  const id = await c.getAddress();
  const target = await (await ethers.getContractFactory('CVINExecuteTarget', deployer)).deploy();
  out('deploy-target', 'CVINExecuteTarget.constructor', true, (await target.deploymentTransaction().wait()).gasUsed, 'observable target (from the ERC-725xy test helpers) to prove whether execute really calls');
  const targetAddr = await target.getAddress();

  const data = target.interface.encodeFunctionData('setValue', [42]);
  await reverts('execute-by-stranger', `${CONTRACT}.execute`, c.connect(stranger).execute(0, targetAddr, 0, data), 'Only owner can execute operations', 'authorisation = msg.sender == owner; no signature parameter exists at all');
  const r = await tx('execute-CALL', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(0, targetAddr, 0, data),
    'execute(operationType=0 CALL, target, 0, setValue(42)): emits Executed(0, target, 0, data) — L1 signed-op measured this at 28,358 gas, which is the cost of an EVENT, not of a call');
  const ev = eventsOf(r, c, 'Executed');
  assert(ev.length === 1 && ev[0].args.to === targetAddr && ev[0].args.operationType === 0n, 'Executed event');
  const v = await view('target-unchanged', 'CVINExecuteTarget.value', target.value(), (x) => `target.value() == ${x} after execute: POTENTIAL DEFECT / stub — the basic proxy performs NO low-level call, so the identity cannot act on-chain at all (contrast erc-725xy where lastCaller == identity)`);
  assert(v === 0n, 'no call performed');
  assert((await view('target-lastCaller', 'CVINExecuteTarget.lastCaller', target.lastCaller(), (x) => `target.lastCaller() == ${x} (never called)`)) === ethers.ZeroAddress, 'never called');
  await tx('execute-self-transferOwnership', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(0, id, 0, c.interface.encodeFunctionData('transferOwnership', [newOwner.address])),
    'what the adapter\'s signedOp("changeOwner") sends: transferOwnership calldata against itself');
  assert((await view('owner-unchanged', `${CONTRACT}.owner`, c.owner(), (x) => `owner still == ${short(x)}: the encoded operation was not applied`)) === vehicleOwner.address, 'not applied');
  await tx('execute-DELEGATECALL-type', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(1, targetAddr, 0, data), 'any operationType is accepted (1 = DELEGATECALL by the ERC-725 draft numbering) and merely echoed in the event');
  await tx('execute-with-value-field', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(0, stranger.address, ethers.parseEther('1'), '0x'), 'value=1 ETH in the event while the contract holds 0 ETH: no transfer, no revert — the field is decorative');
  const r2 = await tx('approve-stub', `${CONTRACT}.approve`, c.connect(stranger).approve(1, true), 'approve(id, true) callable by ANYONE: empty body, no event, no state (the ERC-725v1 execution-approval flow is unimplemented; manifest: token-economics N/A)');
  assert(r2.logs.length === 0, 'approve emits nothing');
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(id);
  const s = await ad.signedOp(id, 'changeOwner', '0x');
  out('adapter-signedOp', `${CONTRACT}.execute`, true, s.gasUsed, `adapter: ${s.note}`);
  out('automation-note', `${CONTRACT}.execute`, true, 0, 'automation/veracity: nothing is verified or enforced by execute; the Executed log is an intent record a verifier cannot trust — the measured "signed-op" column for erc-725 compares an event emission with real ERC-1056 signature verification');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
