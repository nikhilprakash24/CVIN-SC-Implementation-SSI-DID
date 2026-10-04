'use strict';
/**
 * ERC-1155 — family "Identity creation (explicit)" (manifest: measured-in-comparison via
 * registerVehicle). Identity = the address that holds one soulbound BIRTH_CERT (token id 1).
 * Exercises registerVehicle, the credential-type constants, isRegistered, the two VIN indexes
 * written at registration, ERC-165 introspection and every creation guard (including the D13
 * ISO 3779 normalisation: 17 chars, no I/O/Q, upper-cased before hashing).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1155/demos/creation.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, eventCount, VINS, IFACE } = require('./_lib');

const d = demo('erc-1155', 'creation');

d.run(async () => {
  const [issuer, vehicleA, vehicleB, stranger] = await ethers.getSigners();
  const { assert } = d;
  const F = await ethers.getContractFactory('CVINVehicleCredential1155', issuer);
  const c = await F.deploy();
  await c.waitForDeployment();
  const dep = await c.deploymentTransaction().wait();
  d.offchain('deploy', 'CVINVehicleCredential1155.constructor', `shared multi-token registry deployed, gasUsed=${dep.gasUsed}; deployer = DEFAULT_ADMIN + ISSUER (measured as deployRegistry)`);

  await d.view('credential-types', 'CVINVehicleCredential1155.BIRTH_CERT/REGISTRATION/INSPECTION_CERT/INSURANCE_CERT/MAINTENANCE_BADGE',
    Promise.all([c.BIRTH_CERT(), c.REGISTRATION(), c.INSPECTION_CERT(), c.INSURANCE_CERT(), c.MAINTENANCE_BADGE()]),
    'token id == credential TYPE (1..5); a vehicle is an address with balances, not a token', (v) => assert.deepEqual(v, [1n, 2n, 3n, 4n, 5n]));
  await d.view('supports', 'CVINVehicleCredential1155.supportsInterface', Promise.all([c.supportsInterface(IFACE.ERC1155), c.supportsInterface(IFACE.ERC1155MetadataURI), c.supportsInterface(IFACE.AccessControl), c.supportsInterface(IFACE.ERC721)]),
    'ERC-165: ERC-1155 + MetadataURI + AccessControl, not ERC-721', (v) => assert.deepEqual(v, [true, true, true, false]));
  await d.view('registered-before', 'CVINVehicleCredential1155.isRegistered', c.isRegistered(vehicleA.address), 'identity does not exist until the BIRTH_CERT is minted', (v) => assert.equal(v, false));

  const r = await d.tx('register-vehicle', 'CVINVehicleCredential1155.registerVehicle', c.connect(issuer).registerVehicle(vehicleA.address, VINS.bmw),
    'MEASURED (createIdentity): issuer mints 1 BIRTH_CERT to the vehicle address and writes vehicleVIN + vinHashToVehicle');
  const ev = eventArgs(c, r, 'VehicleRegistered');
  assert.equal(ev.vehicle, vehicleA.address); assert.equal(ev.vinHash, ethers.keccak256(ethers.toUtf8Bytes(VINS.bmw))); assert.equal(ev.vin, VINS.bmw);
  assert.equal(eventCount(c, r, 'CredentialIssued'), 1); assert.equal(eventCount(c, r, 'TransferSingle'), 1);
  d.offchain('events', 'CVINVehicleCredential1155.VehicleRegistered+CredentialIssued+TransferSingle', 'one registration emits three logs: the app-level VehicleRegistered (with plain-text VIN), CredentialIssued(BIRTH_CERT) and the standard TransferSingle(0 -> vehicle)');
  await d.view('registered-after', 'CVINVehicleCredential1155.isRegistered', c.isRegistered(vehicleA.address), 'balanceOf(vehicle, BIRTH_CERT) > 0', (v) => assert.equal(v, true));
  await d.view('birth-cert-balance', 'CVINVehicleCredential1155.balanceOf', c.balanceOf(vehicleA.address, 1), 'exactly one BIRTH_CERT unit', (v) => assert.equal(v, 1n));
  await d.view('vehicle-vin', 'CVINVehicleCredential1155.vehicleVIN', c.vehicleVIN(vehicleA.address), 'plain-text VIN stored per address', (v) => assert.equal(v, VINS.bmw));
  await d.view('vin-hash-index', 'CVINVehicleCredential1155.vinHashToVehicle', c.vinHashToVehicle(ethers.keccak256(ethers.toUtf8Bytes(VINS.bmw))), 'keccak256(VIN) -> vehicle address (uniqueness index; the adapter uses this hash as the identity id)', (v) => assert.equal(v, vehicleA.address));

  await d.reverts('register-twice', 'CVINVehicleCredential1155.registerVehicle', () => c.connect(issuer).registerVehicle(vehicleA.address, VINS.honda), 'vehicle already registered', 'one BIRTH_CERT per address');
  await d.reverts('register-duplicate-vin', 'CVINVehicleCredential1155.registerVehicle', () => c.connect(issuer).registerVehicle(vehicleB.address, VINS.bmw), 'VIN already registered', 'VIN uniqueness via the hash index');
  await d.reverts('register-empty-vin', 'CVINVehicleCredential1155.registerVehicle', () => c.connect(issuer).registerVehicle(vehicleB.address, ''), 'empty VIN', 'the emptiness guard fires first; the ISO 3779 shape check (17 chars, no I/O/Q, upper-cased) follows it since the D13 fix');
  await d.reverts('register-short-vin', 'CVINVehicleCredential1155.registerVehicle', () => c.connect(issuer).registerVehicle(vehicleB.address, 'SHORT'), 'invalid VIN length', 'FIXED (D13): a 5-character "VIN" is rejected — ISO 3779 length is enforced on this option too (formerly accepted)');
  await d.reverts('register-invalid-char', 'CVINVehicleCredential1155.registerVehicle', () => c.connect(issuer).registerVehicle(vehicleB.address, 'WBA3A5C55CF25678O'), 'invalid VIN character', 'FIXED (D13): the letters I, O and Q are rejected (check digit intentionally not enforced)');
  await d.reverts('register-lowercase-twin', 'CVINVehicleCredential1155.registerVehicle', () => c.connect(issuer).registerVehicle(vehicleB.address, VINS.bmw.toLowerCase()), 'VIN already registered', 'FIXED (D13): the VIN is upper-cased before hashing, so the lower-cased twin collides with the registered VIN');
  await d.reverts('register-zero-address', 'CVINVehicleCredential1155.registerVehicle', () => c.connect(issuer).registerVehicle(ethers.ZeroAddress, VINS.honda), 'vehicle is zero address', 'zero-address guard');
  await d.reverts('register-unauthorised', 'CVINVehicleCredential1155.registerVehicle', () => c.connect(stranger).registerVehicle(stranger.address, VINS.honda), 'AccessControlUnauthorizedAccount', 'only ISSUER_ROLE creates identities (not self-sovereign)');
  await d.tx('register-second', 'CVINVehicleCredential1155.registerVehicle', c.connect(issuer).registerVehicle(stranger.address, VINS.honda), 'a second real vehicle');
  await d.view('balance-of-batch', 'CVINVehicleCredential1155.balanceOfBatch', c.balanceOfBatch([vehicleA.address, vehicleB.address, stranger.address], [1, 1, 1]), 'ERC-1155 batch read: two identities exist (vehicleB holds none — every one of its malformed registrations was rejected)', (v) => assert.deepEqual([...v], [1n, 0n, 1n]));
});
