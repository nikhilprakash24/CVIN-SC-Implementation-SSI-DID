'use strict';
/**
 * erc-1056-vehicle / keys-delegates — event-only delegates (no delegates mapping, no
 * validDelegate view), revokeDelegate with validTo = now, and updateVehicleKey (key rotation
 * as a fresh veriKey attribute; public write not listed in the manifest).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-vehicle/demos/keys-delegates.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-vehicle';
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
const short = (a) => `${String(a).slice(0, 10)}…`;

const KEY_NAME = 'did/pub/secp256k1/veriKey/base64';

async function main() {
  const [deployer, vehicleOwner, , delegate, stranger] = await ethers.getSigners();
  const registry = await (await ethers.getContractFactory('ERC1056Registry', deployer)).deploy();
  out('deploy-registry', 'ERC1056Registry.constructor', true, (await registry.deploymentTransaction().wait()).gasUsed, 'shared registry');
  const id = vehicleOwner.address;
  const pk1 = '0x04' + 'ab'.repeat(64);
  await tx('registerVehicle', 'ERC1056Registry.registerVehicle', registry.connect(vehicleOwner).registerVehicle(id, pk1), 'vehicle registers its first key');

  const SIGAUTH = h('sigAuth');
  const ra = await tx('addDelegate', 'ERC1056Registry.addDelegate', registry.connect(vehicleOwner).addDelegate(id, SIGAUTH, delegate.address, 3600),
    'EVENT-ONLY: DIDDelegateChanged(validTo = now+3600) + changed pointer; the uPort registry stores validTo, this profile does not (L1 key-or-delegate 35,044 vs 72,219 gas)');
  const ev = eventsOf(ra, registry, 'DIDDelegateChanged');
  assert(ev.length === 1 && ev[0].args.delegate === delegate.address && ev[0].args.validTo > 0n, 'event');
  assert(typeof registry.validDelegate === 'undefined' && typeof registry.delegates === 'undefined', 'no delegate views');
  out('no-delegate-view', 'ERC1056Registry.addDelegate', true, 0, 'the ABI has neither delegates(…) nor validDelegate(…): a verifier (or another contract) CANNOT check delegate validity on-chain; it must replay DIDDelegateChanged events off-chain and compare validTo with the clock');
  await reverts('addDelegate-by-stranger', 'ERC1056Registry.addDelegate', registry.connect(stranger).addDelegate(id, SIGAUTH, stranger.address, 60), 'Only owner can perform this action', 'owner-gated');
  const rr = await tx('revokeDelegate', 'ERC1056Registry.revokeDelegate', registry.connect(vehicleOwner).revokeDelegate(id, SIGAUTH, delegate.address),
    'emits DIDDelegateChanged(validTo = block.timestamp) — "expired now", unlike the uPort registry which emits validTo = 0; resolvers must treat validTo <= now as revoked');
  const rev = eventsOf(rr, registry, 'DIDDelegateChanged')[0];
  const blk = await ethers.provider.getBlock(rr.blockNumber);
  assert(rev.args.validTo === BigInt(blk.timestamp), 'validTo == block.timestamp');
  out('revoke-semantics', 'ERC1056Registry.revokeDelegate', true, 0, `revocation event validTo=${rev.args.validTo} == block.timestamp ${blk.timestamp}`);

  const pk2 = '0x04' + 'cd'.repeat(64);
  const rk = await tx('updateVehicleKey', 'ERC1056Registry.updateVehicleKey', registry.connect(vehicleOwner).updateVehicleKey(id, pk2),
    `key rotation: publishes a NEW "${KEY_NAME}" attribute (1 year) WITHOUT revoking the old one (comment in the contract admits it); the resolver sees two valid keys until the first expires — public write not listed in the manifest, not measured`);
  const kev = eventsOf(rk, registry, 'DIDAttributeChanged')[0];
  assert(kev.args.name === h(KEY_NAME) && kev.args.value === pk2, 'new key published');
  await reverts('updateVehicleKey-by-stranger', 'ERC1056Registry.updateVehicleKey', registry.connect(stranger).updateVehicleKey(id, pk2), 'Only owner can perform this action', 'owner-gated');
  const all = await registry.queryFilter(registry.filters.DIDAttributeChanged(id), 0, 'latest');
  const liveKeys = all.filter((e) => e.args.name === h(KEY_NAME) && e.args.validTo > BigInt(blk.timestamp));
  out('two-live-keys', 'ERC1056Registry.updateVehicleKey', true, 0, `off-chain replay shows ${liveKeys.length} live veriKey attributes (old + new): OBSERVATION — updateVehicleKey is an "add", not a "rotate"; the caller must revokeAttribute(old) separately`);
  assert(liveKeys.length === 2, 'two live keys');
  await tx('revokeAttribute-old-key', 'ERC1056Registry.revokeAttribute', registry.connect(vehicleOwner).revokeAttribute(id, h(KEY_NAME), pk1), 'the missing half of the rotation: revoke the previous key explicitly');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
