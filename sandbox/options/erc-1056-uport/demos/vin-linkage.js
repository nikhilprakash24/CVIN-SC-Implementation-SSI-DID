'use strict';
/**
 * erc-1056-uport / vin-linkage — vinToDID / didToVIN / getDIDFromVIN / getVINFromDID and the
 * DID_VIN attribute name; shows the one-address-one-VIN limitation of the reverse map.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-uport/demos/vin-linkage.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-uport';
const FAMILY = 'vin-linkage';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
const tx = async (step, fn, p, note) => { const r = await (await p).wait(); out(step, fn, true, r.gasUsed, note); return r; };
const view = async (step, fn, p, note) => { const v = await p; out(step, fn, true, 0, typeof note === 'function' ? note(v) : note); return v; };
const assert = (c, m) => { if (!c) throw new Error(`assertion failed: ${m}`); };
const h = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));
const b = (s) => ethers.hexlify(ethers.toUtf8Bytes(s));
const short = (a) => `${String(a).slice(0, 10)}…`;

const VIN = '1HGCM82633A004352';
const VIN2 = 'WBA3A5C58DF586741';
const CAR = ['Honda', 'Accord', 2003, 'Silver', 'K24A4-2003-0471', 1041379200, 'L0'];
const CAR2 = ['BMW', '328i', 2013, 'Black', 'N20B20-2013-8841', 1356998400, 'L1'];

async function main() {
  const [deployer, vehicleOwner, , , stranger] = await ethers.getSigners();
  const registry = await (await ethers.getContractFactory('EthereumDIDRegistry', deployer)).deploy();
  out('deploy-registry', 'EthereumDIDRegistry.constructor', true, (await registry.deploymentTransaction().wait()).gasUsed, 'shared did:ethr registry: knows nothing about VINs');
  const wrapper = await (await ethers.getContractFactory('CVINVehicleDIDRegistry', deployer)).deploy(await registry.getAddress());
  out('deploy-wrapper', 'CVINVehicleDIDRegistry.constructor', true, (await wrapper.deploymentTransaction().wait()).gasUsed, 'VIN wrapper holds the two mappings');
  const id = vehicleOwner.address;

  const DID_VIN = await view('DID_VIN', 'CVINVehicleDIDRegistry.DID_VIN', wrapper.DID_VIN(), (v) => `DID_VIN = keccak256("did/vehicle/vin") = ${short(v)} — attribute name for publishing the VIN inside the DID document`);
  assert(DID_VIN === h('did/vehicle/vin'), 'DID_VIN');
  await tx('createVehicleDID', 'CVINVehicleDIDRegistry.createVehicleDID', wrapper.connect(deployer).createVehicleDID(VIN, id, ...CAR), `binds ${VIN} <-> ${short(id)} (2 SSTOREs: vinToDID + didToVIN)`);
  assert((await view('vinToDID', 'CVINVehicleDIDRegistry.vinToDID', wrapper.vinToDID(h(VIN)), (v) => `vinToDID[keccak256("${VIN}")] == ${short(v)} (keyed by hash of the VIN string)`)) === id, 'vinToDID');
  assert((await view('didToVIN', 'CVINVehicleDIDRegistry.didToVIN', wrapper.didToVIN(id), (v) => `didToVIN[${short(id)}] == ${v}`)) === VIN, 'didToVIN');
  assert((await view('getDIDFromVIN', 'CVINVehicleDIDRegistry.getDIDFromVIN', wrapper.getDIDFromVIN(VIN), (v) => `getDIDFromVIN("${VIN}") == ${short(v)} (hashes the string for the caller)`)) === id, 'getDIDFromVIN');
  assert((await view('getVINFromDID', 'CVINVehicleDIDRegistry.getVINFromDID', wrapper.getVINFromDID(id), (v) => `getVINFromDID(${short(id)}) == ${v}`)) === VIN, 'getVINFromDID');
  assert((await view('getDIDFromVIN-unknown', 'CVINVehicleDIDRegistry.getDIDFromVIN', wrapper.getDIDFromVIN('00000000000000000'), (v) => `unknown VIN -> ${v} (zero address)`)) === ethers.ZeroAddress, 'unknown VIN');
  assert((await view('getVINFromDID-unknown', 'CVINVehicleDIDRegistry.getVINFromDID', wrapper.getVINFromDID(stranger.address), (v) => `unknown DID -> "${v}" (empty string)`)) === '', 'unknown DID');

  await tx('publish-DID_VIN-attribute', 'EthereumDIDRegistry.setAttribute', registry.connect(vehicleOwner).setAttribute(id, DID_VIN, b(VIN), 31536000 * 30),
    'the VIN can additionally be published into the DID document as an event-only attribute (what a resolver would show); the wrapper mapping is the on-chain-queryable index');

  // one address, many VINs: the reverse map is overwritten
  await tx('createVehicleDID-same-owner', 'CVINVehicleDIDRegistry.createVehicleDID', wrapper.connect(deployer).createVehicleDID(VIN2, id, ...CAR2),
    'a second VIN bound to the SAME owner address succeeds (VIN uniqueness is checked, DID uniqueness is not)');
  const vNow = await view('didToVIN-overwritten', 'CVINVehicleDIDRegistry.didToVIN', wrapper.didToVIN(id), (v) => `didToVIN[owner] == ${v}: OBSERVATION — the reverse map was silently overwritten (was ${VIN})`);
  assert(vNow === VIN2, 'reverse overwritten');
  const stillFirst = await view('vinToDID-first-still-points', 'CVINVehicleDIDRegistry.getDIDFromVIN', wrapper.getDIDFromVIN(VIN), (v) => `getDIDFromVIN("${VIN}") still == ${short(v)}: forward map keeps BOTH VINs on one DID; because in ERC-1056 the DID is the owner address, one owner = one DID, so a fleet owner cannot have one DID per vehicle (potential design defect: didToVIN is not one-to-one)`);
  assert(stillFirst === id, 'forward map kept');
  out('vin-veracity', 'CVINVehicleDIDRegistry.getDIDFromVIN', false, 0, 'veracity: the chain only enforces 17 characters, uniqueness and the manufacturer role; whether the VIN exists, has a valid check digit or matches the physical vehicle is the manufacturer\'s off-chain responsibility');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
