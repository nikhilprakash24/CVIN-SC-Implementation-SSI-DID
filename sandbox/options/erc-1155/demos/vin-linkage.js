'use strict';
/**
 * ERC-1155 — family "VIN linkage" (manifest: implemented, not measured). Two indexes: vehicleVIN
 * (address -> plain-text VIN) and vinHashToVehicle (keccak256(normalised VIN) -> address), plus
 * the D13 case-insensitive helpers vinHashOf / vehicleForVIN. Shows the hash convention, the
 * plain-text leak through storage AND the VehicleRegistered event, and how the indexes follow
 * re-binding and deregistration.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1155/demos/vin-linkage.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, VINS } = require('./_lib');

const d = demo('erc-1155', 'vin-linkage');

d.run(async () => {
  const [issuer, vehicleA, buyer] = await ethers.getSigners();
  const { assert } = d;
  const c = await (await ethers.getContractFactory('CVINVehicleCredential1155', issuer)).deploy();
  await c.waitForDeployment();
  const vinHash = ethers.keccak256(ethers.toUtf8Bytes(VINS.hyundai));
  const r = await d.tx('register', 'CVINVehicleCredential1155.registerVehicle', c.registerVehicle(vehicleA.address, VINS.hyundai), 'registration writes both indexes');
  const log = r.logs.map((l) => { try { return c.interface.parseLog(l); } catch (_) { return null; } }).find((p) => p && p.name === 'VehicleRegistered');
  assert.equal(log.args.vin, VINS.hyundai);
  d.offchain('vin-in-event', 'CVINVehicleCredential1155.VehicleRegistered', 'the plain-text VIN is in the log (indexed vinHash + unindexed vin): no privacy, but any indexer can key vehicles by VIN');

  await d.view('vehicle-vin', 'CVINVehicleCredential1155.vehicleVIN', c.vehicleVIN(vehicleA.address), 'address -> VIN', (v) => assert.equal(v, VINS.hyundai));
  await d.view('vin-hash-to-vehicle', 'CVINVehicleCredential1155.vinHashToVehicle', c.vinHashToVehicle(vinHash), 'keccak256(bytes(VIN)) -> address; the adapter uses this hash as the stable identity id because the address changes on re-binding', (v) => assert.equal(v, vehicleA.address));
  await d.view('unknown-vin', 'CVINVehicleCredential1155.vinHashToVehicle', c.vinHashToVehicle(ethers.keccak256(ethers.toUtf8Bytes(VINS.volvo))), 'zero address for an unknown VIN', (v) => assert.equal(v, ethers.ZeroAddress));
  await d.view('unknown-address', 'CVINVehicleCredential1155.vehicleVIN', c.vehicleVIN(buyer.address), 'empty string for a non-vehicle address', (v) => assert.equal(v, ''));
  await d.view('case-sensitive', 'CVINVehicleCredential1155.vinHashToVehicle', c.vinHashToVehicle(ethers.keccak256(ethers.toUtf8Bytes(VINS.hyundai.toLowerCase()))), 'the RAW mapping getter is keyed by keccak256 of the NORMALISED (upper-case) VIN, so a caller who hashes the lower-cased string itself misses — auto-generated getters cannot normalise; use vinHashOf / vehicleForVIN (next steps), which do', (v) => assert.equal(v, ethers.ZeroAddress));
  await d.view('vin-hash-of-lowercase', 'CVINVehicleCredential1155.vinHashOf', c.vinHashOf(VINS.hyundai.toLowerCase()), 'FIXED (D13): the contract-side hash helper upper-cases first, so the lower-cased VIN hashes to the registered key', (v) => assert.equal(v, vinHash));
  await d.view('vehicle-for-vin-lowercase', 'CVINVehicleCredential1155.vehicleForVIN', c.vehicleForVIN(VINS.hyundai.toLowerCase()), 'FIXED (D13): case-insensitive VIN -> vehicle lookup finds the registered identity', (v) => assert.equal(v, vehicleA.address));
  await d.reverts('register-lowercase-twin', 'CVINVehicleCredential1155.registerVehicle', () => c.registerVehicle(buyer.address, VINS.hyundai.toLowerCase()), 'VIN already registered', 'FIXED (D13): the lower-cased VIN can no longer be registered as a second identity');
  await d.tx('rebind', 'CVINVehicleCredential1155.issuerTransferCredential', c.issuerTransferCredential(vehicleA.address, buyer.address, 1), 'issuer-mediated re-binding moves both indexes');
  await d.view('indexes-after-rebind', 'CVINVehicleCredential1155.vehicleVIN+vinHashToVehicle', Promise.all([c.vehicleVIN(buyer.address), c.vehicleVIN(vehicleA.address), c.vinHashToVehicle(vinHash)]), 'buyer owns the VIN, A cleared, hash -> buyer', (v) => assert.deepEqual(v, [VINS.hyundai, '', buyer.address]));
  await d.tx('deregister', 'CVINVehicleCredential1155.revokeCredential', c.revokeCredential(buyer.address, 1, 1), 'burning the BIRTH_CERT clears both indexes');
  await d.view('indexes-after-deregister', 'CVINVehicleCredential1155.vehicleVIN+vinHashToVehicle', Promise.all([c.vehicleVIN(buyer.address), c.vinHashToVehicle(vinHash)]), 'VIN free again', (v) => assert.deepEqual(v, ['', ethers.ZeroAddress]));
});
