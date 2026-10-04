'use strict';
/**
 * erc-725xy / signed-execution — the ERC-725X generic executor: CALL with a real side effect
 * (msg.sender == identity), STATICCALL with return data, value transfer from the account's own
 * balance, executeBatch, revert bubbling (CVINExecuteTarget.willRevert), DELEGATECALL (and the
 * damage it can do), the operation-type constants and supportsInterface. Owner-gated by
 * msg.sender: no signature is verified anywhere.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-725xy/demos/signed-execution.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-725xy';
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

const CONTRACT = 'CVINVehicleERC725XY';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate, stranger] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy(vehicleOwner.address);
  out('deploy-identity', `${CONTRACT}.constructor`, true, (await c.deploymentTransaction().wait()).gasUsed, 'per-vehicle account');
  const id = await c.getAddress();
  const target = await (await ethers.getContractFactory('CVINExecuteTarget', deployer)).deploy();
  out('deploy-target', 'CVINExecuteTarget.constructor', true, (await target.deploymentTransaction().wait()).gasUsed, 'observable target: setValue records msg.sender; willRevert always reverts');
  const tAddr = await target.getAddress();

  const OPS = {};
  for (const n of ['OPERATION_CALL', 'OPERATION_CREATE', 'OPERATION_CREATE2', 'OPERATION_STATICCALL', 'OPERATION_DELEGATECALL']) {
    OPS[n] = await view(`const-${n}`, `${CONTRACT}.${n}`, c[n](), (v) => `${n} == ${v}`);
  }
  for (const [iid, name, exp] of [['0x01ffc9a7', 'ERC165', true], ['0x7545acac', 'ERC725X', true], ['0x629aa694', 'ERC725Y', true], ['0xffffffff', 'invalid', false], ['0x80ac58cd', 'ERC721', false]]) {
    assert((await view(`supportsInterface-${name}`, `${CONTRACT}.supportsInterface`, c.supportsInterface(iid), (v) => `supportsInterface(${iid} ${name}) == ${v}`)) === exp, name);
  }

  // CALL with a real side effect
  const data = target.interface.encodeFunctionData('setValue', [4711]);
  await reverts('execute-by-stranger', `${CONTRACT}.execute`, c.connect(stranger).execute(OPS.OPERATION_CALL, tAddr, 0, data), 'caller is not the owner', 'authorisation = msg.sender == owner; there is NO signature argument — "signed execution" here means the owner key signs the outer transaction');
  const r1 = await tx('execute-CALL', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(OPS.OPERATION_CALL, tAddr, 0, data),
    'L1 signed-op (76,352): a REAL low-level call from the identity; Executed(0, target, 0, selector)');
  const ex = eventsOf(r1, c, 'Executed');
  assert(ex.length === 1 && ex[0].args.selector === data.slice(0, 10), 'Executed selector');
  assert((await view('target-value', 'CVINExecuteTarget.value', target.value(), (v) => `target.value() == ${v}`)) === 4711n, 'value set');
  assert((await view('target-lastCaller', 'CVINExecuteTarget.lastCaller', target.lastCaller(), (v) => `target.lastCaller() == ${short(v)} == identity: the vehicle identity acted as msg.sender (the property ERC-1056/EOA identities cannot have)`)) === id, 'msg.sender is identity');
  const vs = eventsOf(r1, target, 'ValueSet');
  assert(vs.length === 1 && vs[0].args.caller === id, 'ValueSet(caller=identity)');
  out('target-event', 'CVINExecuteTarget.setValue', true, 0, `ValueSet(caller=${short(vs[0].args.caller)}, value=${vs[0].args.value}) emitted by the target inside the same receipt`);

  // STATICCALL with return data
  const sdata = target.interface.encodeFunctionData('value');
  const ret = await c.connect(vehicleOwner).execute.staticCall(OPS.OPERATION_STATICCALL, tAddr, 0, sdata);
  assert(ethers.AbiCoder.defaultAbiCoder().decode(['uint256'], ret)[0] === 4711n, 'staticcall return');
  await tx('execute-STATICCALL', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(OPS.OPERATION_STATICCALL, tAddr, 0, sdata), `STATICCALL value() returned ${ethers.AbiCoder.defaultAbiCoder().decode(['uint256'], ret)[0]} (checked via eth_call first); Executed(3, …)`);
  await reverts('staticcall-with-value', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(OPS.OPERATION_STATICCALL, tAddr, 1, sdata), 'msg.value disallowed in STATICCALL', 'spec guard');

  // revert bubbling
  await reverts('target-willRevert-direct', 'CVINExecuteTarget.willRevert', target.willRevert(), 'CVINExecuteTarget: forced revert', 'the target reverts when called directly (baseline for the next step)');
  await reverts('execute-willRevert', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(OPS.OPERATION_CALL, tAddr, 0, target.interface.encodeFunctionData('willRevert')), 'CVINExecuteTarget: forced revert',
    'the callee\'s revert data is bubbled up verbatim (_verifyCallResult), so the owner sees the real reason — proves the call is not fire-and-forget');
  await reverts('execute-unknown-op', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(7, tAddr, 0, data), 'unknown operation type', 'only the five canonical operation types');

  // value transfer from the account's own balance
  await (await deployer.sendTransaction({ to: id, value: ethers.parseEther('2') })).wait();
  out('fund-account', `${CONTRACT}.constructor`, true, 0, `receive() accepted 2 ETH: balance ${ethers.formatEther(await ethers.provider.getBalance(id))} ETH — the identity custodies funds (toll / charging payments)`);
  const before = await ethers.provider.getBalance(stranger.address);
  await tx('execute-CALL-value', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(OPS.OPERATION_CALL, stranger.address, ethers.parseEther('0.75'), '0x'), 'pays 0.75 ETH from the ACCOUNT (not from the owner EOA) to a toll operator; Executed(0, to, 0.75e18, 0x00000000)');
  assert((await ethers.provider.getBalance(stranger.address)) - before === ethers.parseEther('0.75'), 'paid');
  await reverts('execute-insufficient-balance', `${CONTRACT}.execute`, c.connect(vehicleOwner).execute(OPS.OPERATION_CALL, stranger.address, ethers.parseEther('5'), '0x'), 'insufficient balance for call', 'guard');

  // batch
  const r2 = await tx('executeBatch', `${CONTRACT}.executeBatch`, c.connect(vehicleOwner).executeBatch([OPS.OPERATION_CALL, OPS.OPERATION_CALL], [tAddr, stranger.address], [0, ethers.parseEther('0.25')], [target.interface.encodeFunctionData('setValue', [99]), '0x']),
    'two operations atomically (set a value AND pay): 2 Executed events; not measured');
  assert(eventsOf(r2, c, 'Executed').length === 2 && (await target.value()) === 99n, 'batch applied');
  await reverts('executeBatch-mismatch', `${CONTRACT}.executeBatch`, c.connect(vehicleOwner).executeBatch([0], [tAddr, tAddr], [0, 0], ['0x', '0x']), 'batch parameters length mismatch', 'guard');
  await reverts('executeBatch-empty', `${CONTRACT}.executeBatch`, c.connect(vehicleOwner).executeBatch([], [], [], []), 'empty batch', 'guard');

  // DELEGATECALL: runs the target's code in the identity's storage context
  const c2 = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy(vehicleOwner.address);
  out('deploy-throwaway-identity', `${CONTRACT}.constructor`, true, (await c2.deploymentTransaction().wait()).gasUsed, 'second account to demonstrate DELEGATECALL safely');
  await reverts('delegatecall-with-value', `${CONTRACT}.execute`, c2.connect(vehicleOwner).execute(OPS.OPERATION_DELEGATECALL, tAddr, 1, data), 'msg.value disallowed in DELEGATECALL', 'spec guard');
  await tx('execute-DELEGATECALL', `${CONTRACT}.execute`, c2.connect(vehicleOwner).execute(OPS.OPERATION_DELEGATECALL, tAddr, 0, target.interface.encodeFunctionData('setValue', [777])),
    'DELEGATECALL setValue(777): the target\'s code writes ITS slot 0/1 into the identity\'s storage — slot 0 is _owner');
  const clobbered = await view('owner-after-delegatecall', `${CONTRACT}.owner`, c2.owner(), (v) => `owner() == ${v}: POTENTIAL DEFECT (spec-conformant but dangerous) — an unrestricted DELEGATECALL let a benign-looking target overwrite the controlling key with uint160(777); the identity is now controlled by an address nobody holds`);
  assert(clobbered === ethers.getAddress('0x' + (777).toString(16).padStart(40, '0')), 'owner clobbered to 0x…309');
  await reverts('identity-bricked', `${CONTRACT}.setData`, c2.connect(vehicleOwner).setData(ethers.id('x'), '0x01'), 'caller is not the owner', 'the legitimate owner is locked out after the delegatecall');
  assert((await target.value()) === 99n, 'target storage untouched by delegatecall');

  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(id);
  const s = await ad.signedOp(id, 'execute', '0x');
  out('adapter-signedOp', `${CONTRACT}.execute`, true, s.gasUsed, `adapter: ${s.note}`);
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
