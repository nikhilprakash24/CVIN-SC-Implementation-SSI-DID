'use strict';
/**
 * erc-1056-vehicle / did-resolution — getIdentityInfo (the measured one-call status read),
 * identityOwner, the adapter's event-replay document, and the provider's off-chain
 * resolve_identity / resolve_identity_from_address.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-vehicle/demos/did-resolution.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers, network } = hre;

const OPTION = 'erc-1056-vehicle';
const FAMILY = 'did-resolution';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
const view = async (step, fn, p, note) => { const v = await p; out(step, fn, true, 0, typeof note === 'function' ? note(v) : note); return v; };
const assert = (c, m) => { if (!c) throw new Error(`assertion failed: ${m}`); };
const short = (a) => `${String(a).slice(0, 10)}…`;

const VIN = '1HGCM82633A004352';
const PROVIDER = 'cv2x-testbed/identity/erc1056_provider.py';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  const d = await ad.deploy();
  out('deploy-registry', 'ERC1056Registry.constructor', true, d.gasUsed, 'shared registry');
  const registry = ad.registry;
  const id = vehicleOwner.address;

  const i0 = await view('getIdentityInfo-fresh', 'ERC1056Registry.getIdentityInfo', registry.getIdentityInfo(id), (v) => `before registration: owner=${short(v[0])} lastChanged=${v[1]} isRevoked=${v[2]} revokedAt=${v[3]} — a never-seen address already resolves (ERC-1056 base)`);
  assert(i0[0] === id && i0[1] === 0n, 'fresh');
  const c = await ad.create({ vin: VIN, owner: id });
  out('registerVehicle', 'ERC1056Registry.registerVehicle', true, c.gasUsed, c.note);
  const k = await ad.addKeyOrDelegate(id, delegate.address, 'sigAuth', 600);
  out('addDelegate-10min', 'ERC1056Registry.addDelegate', true, k.gasUsed, 'authentication delegate valid 600 s (event-only)');
  const a = await ad.setAttribute(id, 'did/svc/telematics', 'mqtts://v2x.example/' + VIN, 86400);
  out('setAttribute-service', 'ERC1056Registry.setAttribute', true, a.gasUsed, 'service endpoint');
  const i1 = await view('getIdentityInfo', 'ERC1056Registry.getIdentityInfo', registry.getIdentityInfo(id), (v) => `MEASURED (#21/#29 resolve): one call -> owner=${short(v[0])} lastChanged=${v[1]} isRevoked=${v[2]} revokedAt=${v[3]}; the on-chain part of resolution is O(1) and gives status + head-of-history, not the document`);
  assert(i1[2] === false && i1[1] > 0n, 'info');
  assert((await view('identityOwner', 'ERC1056Registry.identityOwner', registry.identityOwner(id), (v) => `identityOwner == ${short(v)}`)) === id, 'owner');
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve', 'adapter.resolve', true, 0, `document: id=${doc.id} controller=${short(doc.controller)} verificationMethod=${doc.verificationMethod.length} authentication=${doc.authentication.length} service=${doc.service.length} revoked=${doc.status.revoked} events=${doc.meta.events}; built from getIdentityInfo + event replay (delegates/attributes exist only as events in this profile)`);
  assert(doc.verificationMethod.length === 3 && doc.authentication.length === 2 && doc.service.length === 1, 'doc shape');
  await network.provider.send('evm_increaseTime', [1200]);
  await network.provider.send('evm_mine');
  const doc2 = (await ad.resolve(id)).value;
  out('adapter-resolve-after-expiry', 'adapter.resolve', true, 0, `after +1200 s: authentication=${doc2.authentication.length}, verificationMethod=${doc2.verificationMethod.length}: the delegate expired in the RESOLVER (validTo filter) — the chain cannot answer validDelegate for this profile`);
  assert(doc2.authentication.length === 1 && doc2.verificationMethod.length === 2, 'expired in resolver');
  out('offchain-resolve_identity', `offchain:${PROVIDER}#resolve_identity`, false, 0, 'resolve_identity(vehicle_id) (line 730): provider-side DID document from getIdentityInfo + event replay + the off-chain VC; returns (document, latency_ms) — the latency the thesis reports is this off-chain path');
  out('offchain-resolve_identity_from_address', `offchain:${PROVIDER}#resolve_identity_from_address`, false, 0, 'resolve_identity_from_address(address) (line 738): same for peers known only by address (V2X receiver side)');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
