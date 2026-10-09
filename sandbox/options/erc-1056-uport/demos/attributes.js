'use strict';
/**
 * erc-1056-uport / attributes — event-only attributes (setAttribute / setAttributeSigned /
 * revokeAttribute / revokeAttributeSigned), the wrapper's vehicle attribute bundle
 * (setVehicleAttributes(did, …), 8 events — reachable since the D18 / K-1 fix bounded its
 * validity to VEHICLE_ATTRIBUTE_VALIDITY (= PERMANENT_ATTRIBUTE_VALIDITY, 100 y) and, since the
 * merge (K-1, 2026-10-06), takes the DID as its first argument guarded by onlyVehicleOwner(did)
 * and a registry-controls-DID check) and service endpoints (setServiceEndpoint), plus the
 * well-known attribute-name constants.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-uport/demos/attributes.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-uport';
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
const short = (a) => `${String(a).slice(0, 10)}…`;

const VIN = '1HGCM82633A004352';
const CAR = ['Honda', 'Accord', 2003, 'Silver', 'K24A4-2003-0471', 1041379200, 'L0'];
const ONE_YEAR = 31536000;

async function main() {
  const [deployer, , , , stranger] = await ethers.getSigners();
  const W = ethers.Wallet.createRandom().connect(ethers.provider);
  await (await deployer.sendTransaction({ to: W.address, value: ethers.parseEther('5') })).wait();
  const registry = await (await ethers.getContractFactory('EthereumDIDRegistry', deployer)).deploy();
  const r1 = await registry.deploymentTransaction().wait();
  out('deploy-registry', 'EthereumDIDRegistry.constructor', true, r1.gasUsed, 'shared did:ethr registry');
  const wrapper = await (await ethers.getContractFactory('CVINVehicleDIDRegistry', deployer)).deploy(await registry.getAddress());
  const r2 = await wrapper.deploymentTransaction().wait();
  out('deploy-wrapper', 'CVINVehicleDIDRegistry.constructor', true, r2.gasUsed, 'VIN wrapper');
  const regAddr = await registry.getAddress();
  await tx('createVehicleDID', 'CVINVehicleDIDRegistry.createVehicleDID', wrapper.connect(deployer).createVehicleDID(VIN, W.address, ...CAR), `vehicle ${VIN} -> DID ${short(W.address)}`);

  // ---- well-known attribute names (bytes32 constants) ----
  const consts = [
    ['DID_VIN', 'did/vehicle/vin'], ['DID_MAKE', 'did/vehicle/make'], ['DID_MODEL', 'did/vehicle/model'], ['DID_YEAR', 'did/vehicle/year'],
    ['DID_COLOR', 'did/vehicle/color'], ['DID_ENGINE', 'did/vehicle/engineNumber'], ['DID_MANUFACTURING_DATE', 'did/vehicle/manufacturingDate'],
    ['DID_AUTONOMY_LEVEL', 'did/vehicle/autonomyLevel'], ['SVC_CREDENTIAL_SERVICE', 'did/svc/CredentialService'],
    ['SVC_MESSAGING', 'did/svc/MessagingService'], ['SVC_TELEMETRY', 'did/svc/TelemetryService'],
  ];
  const K = {};
  for (const [name, str] of consts) {
    K[name] = await view(`const-${name}`, `CVINVehicleDIDRegistry.${name}`, wrapper[name](), (v) => `${name} = keccak256("${str}") = ${short(v)}; attribute names are hashed, so a resolver needs the dictionary to label them`);
    assert(K[name] === h(str), `${name} constant`);
  }

  // ---- direct attributes: event-only storage ----
  const pub = ethers.hexlify(ethers.randomBytes(33));
  const rs = await tx('setAttribute-veriKey', 'EthereumDIDRegistry.setAttribute', registry.connect(W).setAttribute(W.address, h('did/pub/secp256k1/veriKey'), pub, ONE_YEAR),
    'MEASURED (createIdentity / updateAttribute): DIDAttributeChanged only, no storage except the changed pointer; nothing on-chain can read the value back');
  const e = eventsOf(rs, registry, 'DIDAttributeChanged');
  assert(e.length === 1 && e[0].args.value === pub, 'attribute event');
  assert(typeof registry.getAttribute === 'undefined', 'no getter exists');
  out('no-attribute-getter', 'EthereumDIDRegistry.changed', true, 0, `the ABI has no attribute getter: the only on-chain trace is changed[did] = ${await registry.changed(W.address)}; a verifier must replay DIDAttributeChanged events and apply validTo`);

  const signAttr = async (op, types, values) => {
    const n = await registry.nonce(await registry.identityOwner(W.address));
    const d = ethers.solidityPackedKeccak256(['bytes1', 'bytes1', 'address', 'uint256', 'address', 'string', ...types], ['0x19', '0x00', regAddr, n, W.address, op, ...values]);
    return W.signingKey.sign(d);
  };
  const url = b('https://telematics.example/v1/' + VIN);
  let s = await signAttr('setAttribute', ['bytes32', 'bytes', 'uint256'], [h('did/svc/telematics'), url, ONE_YEAR]);
  await tx('setAttributeSigned', 'EthereumDIDRegistry.setAttributeSigned', registry.connect(deployer).setAttributeSigned(W.address, s.v, s.r, s.s, h('did/svc/telematics'), url, ONE_YEAR),
    'service endpoint published by a relayer with the controller\'s raw-digest signature (gasless for the vehicle); not measured');
  const rr = await tx('revokeAttribute', 'EthereumDIDRegistry.revokeAttribute', registry.connect(W).revokeAttribute(W.address, h('did/pub/secp256k1/veriKey'), pub),
    'MEASURED (revoke): emits DIDAttributeChanged(validTo=0) for the same name+value; the resolver drops the attribute');
  assert(eventsOf(rr, registry, 'DIDAttributeChanged')[0].args.validTo === 0n, 'revoked validTo 0');
  s = await signAttr('revokeAttribute', ['bytes32', 'bytes'], [h('did/svc/telematics'), url]);
  await tx('revokeAttributeSigned', 'EthereumDIDRegistry.revokeAttributeSigned', registry.connect(deployer).revokeAttributeSigned(W.address, s.v, s.r, s.s, h('did/svc/telematics'), url), 'signed revocation relayed; not measured');
  await tx('setAttribute-short-validity', 'EthereumDIDRegistry.setAttribute', registry.connect(W).setAttribute(W.address, h('did/svc/MessagingService'), b('mqtts://v2x.example:8883'), 60),
    'validity 60 s: expiry is encoded in the event (validTo) and enforced only by the resolver — no on-chain check exists for attributes (contrast validDelegate)');

  // ---- wrapper bundle: 8 attributes in one transaction, needs ERC-1056 control (K-1: setVehicleAttributes(did, …)) ----
  const wrapperAddr = await wrapper.getAddress();
  await reverts('setVehicleAttributes-by-stranger', 'CVINVehicleDIDRegistry.setVehicleAttributes', wrapper.connect(stranger).setVehicleAttributes(W.address, ...CAR), 'CVINRegistry: not vehicle owner',
    'FIXED (K-1): the DID is now an explicit first argument and the caller must be vehicleOwnerOf(did) — a stranger naming the vehicle\'s DID is refused first (formerly the function used msg.sender as the DID and could never succeed)');
  await reverts('setVehicleAttributes-before-handoff', 'CVINVehicleDIDRegistry.setVehicleAttributes', wrapper.connect(W).setVehicleAttributes(W.address, ...CAR), 'CVINRegistry: registry does not control DID',
    'FIXED (K-1): the owner itself is refused with the wrapper\'s own reason while the wrapper is not the ERC-1056 owner of the DID (formerly the inner EthereumDIDRegistry reverted "DIDRegistry: unauthorized")');
  await tx('stranger-hands-control-to-wrapper', 'EthereumDIDRegistry.changeOwner', registry.connect(stranger).changeOwner(stranger.address, wrapperAddr), 'a DID that is NOT VIN-registered hands ERC-1056 control to the wrapper (to reach the third guard)');
  await reverts('setVehicleAttributes-unregistered', 'CVINVehicleDIDRegistry.setVehicleAttributes', wrapper.connect(stranger).setVehicleAttributes(stranger.address, ...CAR), 'CVINRegistry: DID not registered',
    'the third guard: owner check and control check pass (vehicleOwners[did] defaults to the DID itself), but the DID has no VIN mapping — the bundle is only for createVehicleDID identities');
  // the vehicle vocabulary CAN also be published directly with a finite validity (while the owner still controls the DID)
  const rvDirect = await tx('setAttribute-DID_VIN-direct', 'EthereumDIDRegistry.setAttribute', registry.connect(W).setAttribute(W.address, K.DID_VIN, b(VIN), ONE_YEAR * 30),
    'the wrapper\'s DID_VIN name used directly with a finite 30-year validity: the owner can publish single birth attributes without the wrapper (the bundle below does all eight at once)');
  assert(ethers.toUtf8String(eventsOf(rvDirect, registry, 'DIDAttributeChanged')[0].args.value) === VIN, 'DID_VIN value');
  await tx('hand-control-to-wrapper', 'EthereumDIDRegistry.changeOwner', registry.connect(W).changeOwner(W.address, wrapperAddr), 'vehicle owner makes the wrapper the ERC-1056 owner');
  await reverts('setVehicleAttributes-by-stranger-after-handoff', 'CVINVehicleDIDRegistry.setVehicleAttributes', wrapper.connect(stranger).setVehicleAttributes(W.address, ...CAR), 'CVINRegistry: not vehicle owner',
    'after the hand-off the wrapper is the ERC-1056 owner, so vehicleOwnerOf(did) is the recorded vehicle owner (defaults to the DID): still W, still not the stranger');
  const PERM = await view('const-PERMANENT_ATTRIBUTE_VALIDITY', 'CVINVehicleDIDRegistry.PERMANENT_ATTRIBUTE_VALIDITY', wrapper.PERMANENT_ATTRIBUTE_VALIDITY(),
    (v) => `PERMANENT_ATTRIBUTE_VALIDITY = ${v} s (100 years): our D18 constant, kept by the merge (same constant as MOBIVIDRegistry)`);
  assert(PERM === BigInt(100 * 365 * 86400), 'PERMANENT_ATTRIBUTE_VALIDITY');
  const VAV = await view('const-VEHICLE_ATTRIBUTE_VALIDITY', 'CVINVehicleDIDRegistry.VEHICLE_ATTRIBUTE_VALIDITY', wrapper.VEHICLE_ATTRIBUTE_VALIDITY(),
    (v) => `VEHICLE_ATTRIBUTE_VALIDITY = ${v} s: the K-1 constant the bundle actually passes to EthereumDIDRegistry.setAttribute — identical to PERMANENT_ATTRIBUTE_VALIDITY (D18 ≡ K-1, same panic-0x11 root cause fixed on both lineages)`);
  assert(VAV === PERM, 'VEHICLE_ATTRIBUTE_VALIDITY == PERMANENT_ATTRIBUTE_VALIDITY');
  const rb = await tx('setVehicleAttributes-bundle', 'CVINVehicleDIDRegistry.setVehicleAttributes', wrapper.connect(W).setVehicleAttributes(W.address, ...CAR),
    'FIXED (D18 / K-1): setVehicleAttributes(did, make, model, year, color, engine, mfgDate, autonomy) by the vehicle owner with the wrapper in control passes validity = VEHICLE_ATTRIBUTE_VALIDITY (100 y) instead of type(uint256).max, so EthereumDIDRegistry.setAttribute\'s block.timestamp + validity no longer overflows (formerly panic 0x11 on every call and the 8-attribute birth record was unreachable through the wrapper); 8 DIDAttributeChanged events in one transaction — gasUsed recorded on this line');
  const bundle = eventsOf(rb, registry, 'DIDAttributeChanged');
  const blkB = await ethers.provider.getBlock(rb.blockNumber);
  const expectNames = ['DID_VIN', 'DID_MAKE', 'DID_MODEL', 'DID_YEAR', 'DID_COLOR', 'DID_ENGINE', 'DID_MANUFACTURING_DATE', 'DID_AUTONOMY_LEVEL'].map((n) => K[n]);
  assert(bundle.length === 8 && bundle.every((e, i) => e.args.name === expectNames[i] && e.args.validTo === BigInt(blkB.timestamp) + VAV), '8 birth attributes, validTo = now + 100 y');
  assert(ethers.toUtf8String(bundle[0].args.value) === VIN && ethers.toUtf8String(bundle[1].args.value) === CAR[0] && ethers.toUtf8String(bundle[7].args.value) === CAR[6], 'bundle values');
  out('bundle-events', 'EthereumDIDRegistry.DIDAttributeChanged', true, 0, `the bundle emitted ${bundle.length} DIDAttributeChanged events (DID_VIN … DID_AUTONOMY_LEVEL), each validTo = ${blkB.timestamp} + ${VAV}; year and manufacturingDate are abi.encodePacked integers, the rest UTF-8 strings`);
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer } });
  await ad.attach({ registry: regAddr, wrapper: wrapperAddr });
  const doc = (await ad.resolve(W.address)).value;
  const resolved = doc.vehicle.attributes;
  const names8 = ['did/vehicle/vin', 'did/vehicle/make', 'did/vehicle/model', 'did/vehicle/year', 'did/vehicle/color', 'did/vehicle/engineNumber', 'did/vehicle/manufacturingDate', 'did/vehicle/autonomyLevel'];
  assert(names8.every((n) => n in resolved), `all 8 attributes resolve: ${Object.keys(resolved).join(',')}`);
  assert(resolved['did/vehicle/vin'] === VIN && resolved['did/vehicle/make'] === CAR[0] && resolved['did/vehicle/model'] === CAR[1] && resolved['did/vehicle/color'] === CAR[3] && resolved['did/vehicle/engineNumber'] === CAR[4] && resolved['did/vehicle/autonomyLevel'] === CAR[6], 'resolved values');
  assert(resolved['did/vehicle/year'] === ethers.toBeHex(CAR[2], 2) && resolved['did/vehicle/manufacturingDate'] === ethers.toBeHex(CAR[5], 32), 'integer attributes resolve as packed hex');
  out('adapter-resolve-birth-record', 'adapter.resolve', true, 0, `adapter.resolve lists all 8 did/vehicle/* attributes in the DID document (vehicle.attributes): ${names8.map((n) => `${n.slice(12)}=${resolved[n]}`).join(', ')} — the birth record is reachable end to end`);
  await tx('setServiceEndpoint-credential', 'CVINVehicleDIDRegistry.setServiceEndpoint', wrapper.connect(W).setServiceEndpoint(W.address, K.SVC_CREDENTIAL_SERVICE, 'https://vc.example/credentials/' + VIN, ONE_YEAR),
    'SVC_CREDENTIAL_SERVICE endpoint: the ONLY on-chain trace of the Claims family for ERC-1056 — credentials themselves are off-chain W3C VCs (public write not listed in the manifest)');
  await reverts('setServiceEndpoint-by-stranger', 'CVINVehicleDIDRegistry.setServiceEndpoint', wrapper.connect(stranger).setServiceEndpoint(W.address, K.SVC_TELEMETRY, 'https://x', 60), 'not vehicle owner', 'wrapper authorises via vehicleOwnerOf');
  out('offchain-vc-issuance', 'offchain:2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py#issue_credential', false, 0,
    'credentials referenced by the service endpoint are issued and verified off-chain (vc_issuer.issue_credential / vc_verifier.verify_credential); the chain never sees them — the on/off-chain asymmetry versus ERC-735');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
