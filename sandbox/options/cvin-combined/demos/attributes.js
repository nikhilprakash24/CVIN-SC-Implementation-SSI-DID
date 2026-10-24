'use strict';
/**
 * cvin-combined / attributes — the cheap half of the hybrid: event-only setAttribute /
 * revokeAttribute (validTo = 0) with only the changed pointer as storage; contrasted with a
 * stored claim for the same payload.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/cvin-combined/demos/attributes.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'cvin-combined';
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

const CONTRACT = 'CVINCombinedIdentity';
const VIN = '5YJ3E1EA7KF317000';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate, stranger] = await ethers.getSigners();
  const reg = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy();
  out('deploy-registry', `${CONTRACT}.constructor`, true, (await reg.deploymentTransaction().wait()).gasUsed, 'shared hybrid registry');
  const id = vehicleOwner.address;
  const KEY = h('did/pub/secp256k1/veriKey');
  const pub = ethers.hexlify(ethers.randomBytes(33));

  const r1 = await tx('setAttribute-veriKey', `${CONTRACT}.setAttribute`, reg.connect(vehicleOwner).setAttribute(id, KEY, pub, 31536000),
    'MEASURED (benchmark createIdentity = first setAttribute, and updateAttribute): DIDAttributeChanged + changed pointer only; nothing else is stored');
  const e1 = eventsOf(r1, reg, 'DIDAttributeChanged')[0];
  assert(e1.args.value === pub && e1.args.previousChange === 0n, 'event');
  const r2 = await tx('setAttribute-rotate', `${CONTRACT}.setAttribute`, reg.connect(vehicleOwner).setAttribute(id, KEY, ethers.hexlify(ethers.randomBytes(33)), 31536000), 'key rotation = publish the next value; the previous one stays valid until its validTo or an explicit revoke');
  assert(eventsOf(r2, reg, 'DIDAttributeChanged')[0].args.previousChange === BigInt(r1.blockNumber), 'linked');
  const FW = h('did/vehicle/firmwareHash');
  const fw = ethers.keccak256(b('fw-2025.09.1'));
  await tx('setAttribute-firmware', `${CONTRACT}.setAttribute`, reg.connect(vehicleOwner).setAttribute(id, FW, fw, 86400 * 90), 'firmware hash with 90-day validity: the thesis\' example of data that only needs a tamper-evident history, not on-chain readability');
  await reverts('setAttribute-by-stranger', `${CONTRACT}.setAttribute`, reg.connect(stranger).setAttribute(id, FW, fw, 60), 'CVINCombined: unauthorized', 'owner-gated');
  assert(typeof reg.getAttribute === 'undefined', 'no getter');
  out('no-getter', `${CONTRACT}.changed`, true, 0, `no attribute getter; changed[id] == ${await reg.changed(id)}; an on-chain verifier CANNOT read attributes — that is exactly why safety-critical data goes into claims (see claims demo)`);
  const r3 = await tx('revokeAttribute', `${CONTRACT}.revokeAttribute`, reg.connect(vehicleOwner).revokeAttribute(id, KEY, pub),
    'MEASURED-family (benchmark: "event-only revokeAttribute also supported"): DIDAttributeChanged(validTo = 0) for name+value (uPort convention, unlike the vehicle profile\'s validTo = now)');
  assert(eventsOf(r3, reg, 'DIDAttributeChanged')[0].args.validTo === 0n, 'validTo 0');
  await tx('revokeAttribute-never-set', `${CONTRACT}.revokeAttribute`, reg.connect(vehicleOwner).revokeAttribute(id, h('did/svc/none'), b('x')), 'OBSERVATION: revoking a never-published attribute succeeds (event-only model cannot know)');

  // same payload as attribute vs as claim
  const issuer = ethers.Wallet.createRandom();
  const sig = ethers.Signature.from(issuer.signingKey.sign(ethers.solidityPackedKeccak256(['address', 'address', 'uint256', 'bytes'], [await reg.getAddress(), id, 1, b(VIN)]))).serialized;
  const ra = await tx('vin-as-attribute', `${CONTRACT}.setAttribute`, reg.connect(vehicleOwner).setAttribute(id, h('did/vehicle/vin'), b(VIN), 31536000 * 20), 'the VIN published as an event-only attribute …');
  const rc = await tx('vin-as-claim', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, 1, 1, issuer.address, sig, b(VIN), ''), '… versus anchored as an issuer-signed, stored claim: the hybrid lets the owner choose per datum');
  out('cost-asymmetry', `${CONTRACT}.setAttribute`, true, 0, `same 17-byte VIN: attribute ${ra.gasUsed} gas (unreadable on-chain, no issuer) vs claim ${rc.gasUsed} gas (${(Number(rc.gasUsed) / Number(ra.gasUsed)).toFixed(1)}x; O(1) readable, issuer-verified) — the trade-off the hybrid is built on`);
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(await reg.getAddress());
  const a = await ad.setAttribute(id, 'did/svc/telematics', 'mqtts://v2x.example/' + VIN, 86400);
  out('adapter-setAttribute', `${CONTRACT}.setAttribute`, true, a.gasUsed, `adapter: ${a.note}`);
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve-attributes', 'adapter.resolve', true, 0, `resolve: service=${doc.service.length} vehicle.attributes=${JSON.stringify(doc.vehicle.attributes)} vin(from claim)=${doc.vehicle.vin}`);
  assert(doc.service.length === 1 && doc.vehicle.vin === VIN, 'doc');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
