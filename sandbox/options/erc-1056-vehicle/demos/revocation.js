'use strict';
/**
 * erc-1056-vehicle / revocation — the one ERC-1056 variant WITH identity-level revocation:
 * revokeIdentity / isRevoked / revoked / revokedAt / DIDRevoked, what it gates afterwards, plus
 * attribute/delegate revocation and the off-chain status checks of the provider.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-vehicle/demos/revocation.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-vehicle';
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
const short = (a) => `${String(a).slice(0, 10)}…`;

const PROVIDER = 'cv2x-testbed/identity/erc1056_provider.py';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate, stranger] = await ethers.getSigners();
  const registry = await (await ethers.getContractFactory('ERC1056Registry', deployer)).deploy();
  out('deploy-registry', 'ERC1056Registry.constructor', true, (await registry.deploymentTransaction().wait()).gasUsed, 'shared registry');
  const id = vehicleOwner.address;
  const pk = '0x04' + 'ab'.repeat(64);
  await tx('registerVehicle', 'ERC1056Registry.registerVehicle', registry.connect(vehicleOwner).registerVehicle(id, pk), 'vehicle registers');
  const SVC = h('did/svc/telematics');
  const url = b('mqtts://v2x.example');
  await tx('setAttribute', 'ERC1056Registry.setAttribute', registry.connect(vehicleOwner).setAttribute(id, SVC, url, 86400), 'something to revoke');
  await tx('addDelegate', 'ERC1056Registry.addDelegate', registry.connect(vehicleOwner).addDelegate(id, h('sigAuth'), delegate.address, 86400), 'something to revoke');

  // sub-identity revocation
  await tx('revokeAttribute', 'ERC1056Registry.revokeAttribute', registry.connect(vehicleOwner).revokeAttribute(id, SVC, url), 'attribute revocation (validTo = now); listed under the measured Revocation family');
  await tx('revokeDelegate', 'ERC1056Registry.revokeDelegate', registry.connect(vehicleOwner).revokeDelegate(id, h('sigAuth'), delegate.address), 'delegate revocation (validTo = now)');

  // identity-level revocation
  assert((await view('isRevoked-before', 'ERC1056Registry.isRevoked', registry.isRevoked(id), (v) => `isRevoked == ${v}`)) === false, 'not revoked');
  await reverts('revokeIdentity-by-stranger', 'ERC1056Registry.revokeIdentity', registry.connect(stranger).revokeIdentity(id), 'Only owner can perform this action', 'only the controller decommissions');
  const rr = await tx('revokeIdentity', 'ERC1056Registry.revokeIdentity', registry.connect(vehicleOwner).revokeIdentity(id),
    'MEASURED (#21/#29 revoke): 2 SSTOREs (revoked flag + revokedAt) + DIDRevoked + changed pointer; the identity-level kill switch the uPort registry lacks');
  const ev = eventsOf(rr, registry, 'DIDRevoked');
  const blk = await ethers.provider.getBlock(rr.blockNumber);
  assert(ev.length === 1 && ev[0].args.revokedAt === BigInt(blk.timestamp), 'DIDRevoked');
  assert((await view('isRevoked-after', 'ERC1056Registry.isRevoked', registry.isRevoked(id), (v) => `isRevoked == ${v}: MEASURED (#21/#29 status check) — an O(1) on-chain read any contract or RSU can make`)) === true, 'revoked');
  assert((await view('revoked-mapping', 'ERC1056Registry.revoked', registry.revoked(id), (v) => `revoked[id] == ${v} (public mapping behind isRevoked)`)) === true, 'mapping');
  assert((await view('revokedAt', 'ERC1056Registry.revokedAt', registry.revokedAt(id), (v) => `revokedAt == ${v} (block timestamp of decommissioning)`)) === BigInt(blk.timestamp), 'revokedAt');
  const info = await view('getIdentityInfo', 'ERC1056Registry.getIdentityInfo', registry.getIdentityInfo(id), (v) => `getIdentityInfo -> owner=${short(v[0])} lastChanged=${v[1]} isRevoked=${v[2]} revokedAt=${v[3]}`);
  assert(info[2] === true && info[3] === BigInt(blk.timestamp), 'info');

  // what the flag gates
  await reverts('addDelegate-after-revoke', 'ERC1056Registry.addDelegate', registry.connect(vehicleOwner).addDelegate(id, h('sigAuth'), delegate.address, 60), 'Identity is revoked', 'new delegates blocked');
  await reverts('setAttribute-after-revoke', 'ERC1056Registry.setAttribute', registry.connect(vehicleOwner).setAttribute(id, SVC, url, 60), 'Identity is revoked', 'new attributes blocked');
  await reverts('updateVehicleKey-after-revoke', 'ERC1056Registry.updateVehicleKey', registry.connect(vehicleOwner).updateVehicleKey(id, pk), 'Identity is revoked', 'key rotation blocked');
  await reverts('registerVehicle-after-revoke', 'ERC1056Registry.registerVehicle', registry.connect(vehicleOwner).registerVehicle(id, pk), 'Identity already revoked', 'resurrection blocked: revocation is permanent');
  await tx('changeOwner-after-revoke', 'ERC1056Registry.changeOwner', registry.connect(vehicleOwner).changeOwner(id, newOwner.address),
    'OBSERVATION: changeOwner is NOT gated by the revoked flag — a decommissioned identity can still be transferred (and the new owner can revoke it again)');
  const r2 = await tx('revokeIdentity-again', 'ERC1056Registry.revokeIdentity', registry.connect(newOwner).revokeIdentity(id),
    'OBSERVATION: revokeIdentity is not idempotent-guarded: a second call succeeds and OVERWRITES revokedAt with a later timestamp (audit trail of the original decommissioning time survives only in the first DIDRevoked event)');
  const ra2 = await registry.revokedAt(id);
  assert(ra2 > BigInt(blk.timestamp), 'revokedAt overwritten');
  void r2;

  // off-chain status checks of the provider
  out('offchain-check_revocation_status', `offchain:${PROVIDER}#check_revocation_status`, false, 0, 'check_revocation_status(vehicle_id) (line 649): looks the vehicle up in the provider store and calls isRevoked(address) — the one on-chain read in the V2X hot path');
  out('offchain-check_revocation_status_by_address', `offchain:${PROVIDER}#check_revocation_status_by_address`, false, 0, 'check_revocation_status_by_address(address) (line 657): same for a peer whose credential you only know by address (RSU / other vehicle)');
  out('offchain-revoke_credential', `offchain:${PROVIDER}#revoke_credential`, false, 0, 'revoke_credential(vehicle_id, reason) (line 618): marks the off-chain VC revoked, then sends revokeIdentity — both layers must agree; the chain only knows the flag');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
