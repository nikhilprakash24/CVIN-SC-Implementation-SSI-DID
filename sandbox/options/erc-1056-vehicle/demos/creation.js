'use strict';
/**
 * erc-1056-vehicle / creation — explicit, self-sovereign registration: registerVehicle must be
 * sent from the vehicle's own account (identityOwner defaults to the identity) and is one
 * 1-year veriKey attribute; it refuses an already-owned or revoked identity.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-vehicle/demos/creation.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-vehicle';
const FAMILY = 'creation';
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

const VIN = '1HGCM82633A004352';
const KEY_NAME = 'did/pub/secp256k1/veriKey/base64';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate, stranger] = await ethers.getSigners();
  const registry = await (await ethers.getContractFactory('ERC1056Registry', deployer)).deploy();
  out('deploy-registry', 'ERC1056Registry.constructor', true, (await registry.deploymentTransaction().wait()).gasUsed, 'single shared registry (cv2x-testbed deploy.js deploys the same bytecode)');
  const id = vehicleOwner.address;

  assert((await view('implicit-before', 'ERC1056Registry.identityOwner', registry.identityOwner(id), (v) => `identityOwner(vehicle) == ${short(v)} (itself) before registration: the ERC-1056 base is still implicit, but this profile adds an explicit registration step`)) === id, 'self');
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(await registry.getAddress());
  const pk = ad._publicKeyFor(id) || ('0x04' + '00'.repeat(64));
  await reverts('registerVehicle-by-third-party', 'ERC1056Registry.registerVehicle', registry.connect(deployer).registerVehicle(id, pk), 'Only owner can perform this action',
    'registration is self-sovereign: the internal setAttribute is gated on actor == identityOwner(identity) == the vehicle itself, so no manufacturer/registrar can register on its behalf');
  const rc = await tx('registerVehicle', 'ERC1056Registry.registerVehicle', registry.connect(vehicleOwner).registerVehicle(id, pk),
    `MEASURED (#21/#29 create): sent by the vehicle account; = one setAttribute("${KEY_NAME}", 65-byte uncompressed secp256k1 key, 1 year) + changed pointer; VIN ${VIN} is NOT anchored (VIN linkage N/A)`);
  const ev = eventsOf(rc, registry, 'DIDAttributeChanged');
  assert(ev.length === 1 && ev[0].args.name === h(KEY_NAME) && ev[0].args.value === pk, 'key attribute event');
  out('event-decoded', 'ERC1056Registry.registerVehicle', true, 0, `DIDAttributeChanged(name=keccak256("${KEY_NAME}"), value=${pk.length / 2 - 1} bytes, validTo=${ev[0].args.validTo}, previousChange=0)`);
  assert((await view('changed-after', 'ERC1056Registry.changed', registry.changed(id), (v) => `changed == ${v} (registration block)`)) === BigInt(rc.blockNumber), 'changed set');
  await tx('registerVehicle-again-same-owner', 'ERC1056Registry.registerVehicle', registry.connect(vehicleOwner).registerVehicle(id, pk),
    'OBSERVATION: re-registering is allowed while the identity still owns itself (the "already registered" guard only checks for an explicit owner, not for a prior registration) — it simply publishes the key again');
  await tx('changeOwner', 'ERC1056Registry.changeOwner', registry.connect(vehicleOwner).changeOwner(id, newOwner.address), 'give the identity an explicit owner');
  await reverts('registerVehicle-after-changeOwner', 'ERC1056Registry.registerVehicle', registry.connect(newOwner).registerVehicle(id, pk), 'Identity already registered', 'an identity with an explicit owner cannot be (re)registered');
  await tx('revokeIdentity', 'ERC1056Registry.revokeIdentity', registry.connect(newOwner).revokeIdentity(id), 'decommission');
  await reverts('registerVehicle-after-revoke', 'ERC1056Registry.registerVehicle', registry.connect(newOwner).registerVehicle(id, pk), 'Identity already revoked', 'a revoked identity can never be registered again (permanent)');

  void stranger;
  const c = await ad.create({ vin: 'WBA3A5C58DF586741', owner: delegate.address }); // must be one of the adapter's signers: the vehicle signs its own registration
  out('adapter-create', 'ERC1056Registry.registerVehicle', true, c.gasUsed, `adapter.create for a second vehicle: ${c.note}`);
  out('offchain-register_vehicle', 'offchain:cv2x-testbed/identity/erc1056_provider.py#register_vehicle', false, 0,
    'the Python provider wraps this call (erc1056_provider.register_vehicle, line 321) and additionally issues an off-chain W3C VehicleCredential for the VIN — the VIN never reaches the chain');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
