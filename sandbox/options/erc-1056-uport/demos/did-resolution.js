'use strict';
/**
 * erc-1056-uport / did-resolution — building the did:ethr document from on-chain reads only:
 * identityOwner, the event walk, validDelegate, the wrapper's VIN and owner views and the
 * well-known name constants; expiry is applied by the resolver, not the chain.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-uport/demos/did-resolution.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers, network } = hre;

const OPTION = 'erc-1056-uport';
const FAMILY = 'did-resolution';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
const tx = async (step, fn, p, note) => { const r = await (await p).wait(); out(step, fn, true, r.gasUsed, note); return r; };
const view = async (step, fn, p, note) => { const v = await p; out(step, fn, true, 0, typeof note === 'function' ? note(v) : note); return v; };
const assert = (c, m) => { if (!c) throw new Error(`assertion failed: ${m}`); };
const h = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));
const short = (a) => `${String(a).slice(0, 10)}…`;

const VIN = '1HGCM82633A004352';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  const d = await ad.deploy();
  out('deploy', 'CVINVehicleDIDRegistry.constructor', true, d.gasUsed, `adapter.deploy: ${d.note}`);
  const registry = ad.registry;
  const wrapper = ad.wrapper;
  const id = vehicleOwner.address;

  assert((await view('didRegistry', 'CVINVehicleDIDRegistry.didRegistry', wrapper.didRegistry(), (v) => `wrapper -> registry ${short(v)}: a resolver needs BOTH addresses`)) === await registry.getAddress(), 'didRegistry link');
  const names = ['DID_VIN', 'DID_MAKE', 'DID_MODEL', 'DID_YEAR', 'DID_COLOR', 'DID_ENGINE', 'DID_MANUFACTURING_DATE', 'DID_AUTONOMY_LEVEL'];
  const dict = {};
  for (const n of names) dict[await wrapper[n]()] = n;
  out('name-dictionary', 'CVINVehicleDIDRegistry.DID_MAKE', true, 0, `resolver dictionary built from the ${names.length} DID_* constants (bytes32 -> label): without it, attribute names in events are opaque hashes`);

  const c = await ad.create({ vin: VIN, owner: id, make: 'Honda', model: 'Accord', year: 2003 });
  out('create', 'CVINVehicleDIDRegistry.createVehicleDID', true, c.gasUsed, c.note);
  const pub = ethers.hexlify(ethers.randomBytes(33));
  const a1 = await ad.setAttribute(id, 'did/pub/secp256k1/veriKey', pub, 31536000);
  out('setAttribute-veriKey', 'EthereumDIDRegistry.setAttribute', true, a1.gasUsed, 'verification key published (event-only)');
  const a2 = await ad.setAttribute(id, 'did/svc/CredentialService', 'https://vc.example/' + VIN, 31536000);
  out('setAttribute-service', 'EthereumDIDRegistry.setAttribute', true, a2.gasUsed, 'service endpoint published');
  const k1 = await ad.addKeyOrDelegate(id, delegate.address, 'sigAuth', 600);
  out('addDelegate-sigAuth-10min', 'EthereumDIDRegistry.addDelegate', true, k1.gasUsed, 'authentication delegate valid for 600 s');

  assert((await view('identityOwner', 'EthereumDIDRegistry.identityOwner', registry.identityOwner(id), (v) => `controller == ${short(v)}`)) === id, 'controller');
  const r1 = await ad.resolve(id);
  const doc = r1.value;
  out('resolve', 'adapter.resolve', true, 0, `did=${doc.id} controller=${short(doc.controller)} verificationMethod=${doc.verificationMethod.length} authentication=${doc.authentication.length} service=${doc.service.length} vin=${doc.vehicle.vin} events=${doc.meta.events}; built from identityOwner/changed/nonce/validDelegate + the event walk + getVINFromDID/vehicleOwnerOf — no caching`);
  assert(doc.id.endsWith(id) && doc.verificationMethod.length === 3 && doc.authentication.length === 2 && doc.service.length === 1 && doc.vehicle.vin === VIN, 'document shape');
  assert(doc.meta.events === 3, 'three events walked');

  await network.provider.send('evm_increaseTime', [1200]);
  await network.provider.send('evm_mine');
  const r2 = await ad.resolve(id);
  out('resolve-after-expiry', 'adapter.resolve', true, 0, `after +1200 s: verificationMethod=${r2.value.verificationMethod.length} authentication=${r2.value.authentication.length}: the expired sigAuth delegate disappeared without any transaction (validDelegate false + validTo filter)`);
  assert(r2.value.verificationMethod.length === 2 && r2.value.authentication.length === 1, 'expired delegate dropped');
  assert((await view('validDelegate-expired', 'EthereumDIDRegistry.validDelegate', registry.validDelegate(id, h('sigAuth'), delegate.address), (v) => `validDelegate == ${v}`)) === false, 'expired');
  assert((await view('vehicleOwnerOf', 'CVINVehicleDIDRegistry.vehicleOwnerOf', wrapper.vehicleOwnerOf(id), (v) => `vehicleOwnerOf == ${short(v)} (wrapper view used by resolve)`)) === id, 'vehicle owner');
  assert((await view('getVINFromDID', 'CVINVehicleDIDRegistry.getVINFromDID', wrapper.getVINFromDID(id), (v) => `getVINFromDID == ${v}`)) === VIN, 'vin');
  out('offchain-resolver', 'offchain:2_w3c-ssi-layer/did-resolution/did_resolver.py', false, 0, 'the production resolver (did_resolver.py) produces the same W3C DID document shape; resolution is never measured by the comparison (resolve gas = 0 in L1 because it is reads only)');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
