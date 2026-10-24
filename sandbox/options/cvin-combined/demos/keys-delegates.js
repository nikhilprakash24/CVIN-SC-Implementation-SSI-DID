'use strict';
/**
 * cvin-combined / keys-delegates — stored, time-bound delegates (addDelegate / delegates /
 * validDelegate / revokeDelegate) with on-chain expiry; revokeDelegate writes validity =
 * block.timestamp (not 0).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/cvin-combined/demos/keys-delegates.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers, network } = hre;

const OPTION = 'cvin-combined';
const FAMILY = 'keys-delegates';
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

const CONTRACT = 'CVINCombinedIdentity';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate, stranger] = await ethers.getSigners();
  const reg = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy();
  out('deploy-registry', `${CONTRACT}.constructor`, true, (await reg.deploymentTransaction().wait()).gasUsed, 'shared hybrid registry');
  const id = vehicleOwner.address;
  const SIGAUTH = h('sigAuth');
  const VERIKEY = h('veriKey');

  await reverts('addDelegate-by-stranger', `${CONTRACT}.addDelegate`, reg.connect(stranger).addDelegate(id, SIGAUTH, stranger.address, 60), 'CVINCombined: unauthorized', 'owner-gated');
  const r1 = await tx('addDelegate-session-key', `${CONTRACT}.addDelegate`, reg.connect(vehicleOwner).addDelegate(id, SIGAUTH, delegate.address, 900),
    'MEASURED (benchmark_ops: event-only addDelegate 55,162; L1 key-or-delegate 72,262): telematics session key valid 15 min; SSTORE validTo + DIDDelegateChanged + changed');
  const validTo = eventsOf(r1, reg, 'DIDDelegateChanged')[0].args.validTo;
  assert((await view('delegates-mapping', `${CONTRACT}.delegates`, reg.delegates(id, SIGAUTH, delegate.address), (v) => `delegates[id][sigAuth][delegate] == ${v} (== event validTo ${validTo}): STORED, so an RSU contract can check it`)) === validTo, 'stored');
  assert((await view('validDelegate-true', `${CONTRACT}.validDelegate`, reg.validDelegate(id, SIGAUTH, delegate.address), (v) => `validDelegate == ${v}`)) === true, 'valid');
  await network.provider.send('evm_increaseTime', [1800]);
  await network.provider.send('evm_mine');
  assert((await view('validDelegate-expired', `${CONTRACT}.validDelegate`, reg.validDelegate(id, SIGAUTH, delegate.address), (v) => `after +1800 s: validDelegate == ${v} — session keys expire on-chain with no transaction (the V2X rotation pattern)`)) === false, 'expired');
  await tx('addDelegate-veriKey-1y', `${CONTRACT}.addDelegate`, reg.connect(vehicleOwner).addDelegate(id, VERIKEY, delegate.address, 31536000), 'long-lived assertion key (1 year), what the comparison measures');
  const r2 = await tx('revokeDelegate', `${CONTRACT}.revokeDelegate`, reg.connect(vehicleOwner).revokeDelegate(id, VERIKEY, delegate.address),
    'MEASURED (benchmark revoke = revokeDelegate; L1 revoke 71,322): writes validity = block.timestamp (NOT 0 as in the uPort registry) and emits DIDDelegateChanged(validTo = now)');
  const rv = eventsOf(r2, reg, 'DIDDelegateChanged')[0].args.validTo;
  const blk = await ethers.provider.getBlock(r2.blockNumber);
  assert(rv === BigInt(blk.timestamp), 'validTo == now');
  assert((await view('delegates-after-revoke', `${CONTRACT}.delegates`, reg.delegates(id, VERIKEY, delegate.address), (v) => `delegates[...] == ${v} == revocation timestamp: OBSERVATION — the slot is not cleared (no refund) and a resolver must treat validTo <= now as revoked rather than looking for 0`)) === rv, 'timestamp stored');
  assert((await view('validDelegate-after-revoke', `${CONTRACT}.validDelegate`, reg.validDelegate(id, VERIKEY, delegate.address), (v) => `validDelegate == ${v} (> block.timestamp is false)`)) === false, 'revoked');
  await tx('re-add-after-revoke', `${CONTRACT}.addDelegate`, reg.connect(vehicleOwner).addDelegate(id, VERIKEY, delegate.address, 3600), 'warm SSTORE: re-adding after revocation is cheaper than the first add');
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(await reg.getAddress());
  const k = await ad.addKeyOrDelegate(id, newOwner.address, 'sigAuth', 120);
  out('adapter-addKeyOrDelegate', `${CONTRACT}.addDelegate`, true, k.gasUsed, `adapter: ${k.note}`);
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve-delegates', 'adapter.resolve', true, 0, `resolve: verificationMethod=${doc.verificationMethod.length} authentication=${doc.authentication.length} assertionMethod=${doc.assertionMethod.length} (expired/revoked delegates filtered by validDelegate)`);
  assert(doc.assertionMethod.length === 1 && doc.authentication.length === 2, 'doc');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
