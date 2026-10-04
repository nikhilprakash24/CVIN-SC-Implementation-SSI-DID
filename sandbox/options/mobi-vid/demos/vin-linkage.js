'use strict';
/**
 * MOBI VID — family "VIN linkage" (manifest: implemented via lookupByVINHash / vinHashToIdentity,
 * plus the provider's export_vin_key). The VIN never reaches the chain: only a hash (whose
 * construction — SHA-256 with salt in the provider, keccak256 in the adapter — is an off-chain
 * convention the contract cannot check) and an opaque encrypted copy. Shows lookup, uniqueness
 * only at hash level, and decryption with the owner's key (export_vin_key analogue).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/mobi-vid/demos/vin-linkage.js
 */
const crypto = require('node:crypto');
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, VINS } = require('./_lib');

const d = demo('mobi-vid', 'vin-linkage');

d.run(async () => {
  const [authority, owner] = await ethers.getSigners();
  const { assert } = d;
  const reg = await (await ethers.getContractFactory('MOBIVIDRegistryV2', authority)).deploy();
  await reg.waitForDeployment();
  const vehicle = ethers.Wallet.createRandom().address;
  const salt = crypto.randomBytes(16);
  const vinHashSha = ethers.sha256(ethers.concat([ethers.toUtf8Bytes(VINS.renault), salt, vehicle]));
  const vinHashKeccak = ethers.keccak256(ethers.toUtf8Bytes(VINS.renault));
  const key = crypto.randomBytes(32), iv = crypto.randomBytes(12);
  const c = crypto.createCipheriv('aes-256-gcm', key, iv);
  const ct = Buffer.concat([c.update(VINS.renault, 'utf8'), c.final()]);
  const encryptedVIN = `aes-256-gcm:${iv.toString('hex')}:${ct.toString('hex')}:${c.getAuthTag().toString('hex')}`;
  d.offchain('hash-choices', 'off-chain SHA-256 vs keccak256', `provider convention: SHA-256(VIN || salt || identity) = ${vinHashSha.slice(0, 12)}…; adapter convention: keccak256(VIN) = ${vinHashKeccak.slice(0, 12)}…; the contract accepts any non-zero bytes32`);
  await d.tx('register-birth', 'MOBIVIDRegistryV2.registerVehicleBirth', reg.registerVehicleBirth(vehicle, vinHashSha, encryptedVIN, ethers.id('cert'), owner.address, '0x'), 'birth with the salted SHA-256 hash and the AES-GCM ciphertext');
  await d.view('lookup-by-vin-hash', 'MOBIVIDRegistryV2.lookupByVINHash', reg.lookupByVINHash(vinHashSha), 'hash -> identity (someone who knows VIN + salt + identity can confirm the binding; nobody can enumerate VINs)', (v) => assert.equal(v, vehicle));
  await d.view('vin-hash-to-identity-raw', 'MOBIVIDRegistryV2.vinHashToIdentity', reg.vinHashToIdentity(vinHashSha), 'raw mapping getter', (v) => assert.equal(v, vehicle));
  await d.view('lookup-unsalted', 'MOBIVIDRegistryV2.lookupByVINHash', reg.lookupByVINHash(vinHashKeccak), 'the plain keccak of the same VIN finds nothing: linkage is only as good as the shared hashing convention', (v) => assert.equal(v, ethers.ZeroAddress));
  await d.tx('register-same-vin-other-salt', 'MOBIVIDRegistryV2.registerVehicleBirth', reg.registerVehicleBirth(ethers.Wallet.createRandom().address, vinHashKeccak, 'enc2', ethers.id('cert2'), owner.address, '0x'), 'OBSERVATION: the SAME VIN under another hash convention registers a second identity — uniqueness exists only per hash, so a salted scheme forfeits on-chain VIN uniqueness');
  await d.view('both-exist', 'MOBIVIDRegistryV2.lookupByVINHash', Promise.all([reg.lookupByVINHash(vinHashSha), reg.lookupByVINHash(vinHashKeccak)]), 'two identities for one physical vehicle', (v) => { assert.notEqual(v[0], ethers.ZeroAddress); assert.notEqual(v[1], ethers.ZeroAddress); assert.notEqual(v[0], v[1]); });
  const birth = await reg.getVehicleBirth(vehicle);
  const [, ivHex, ctHex, tagHex] = birth.encryptedVIN.split(':');
  const dec = crypto.createDecipheriv('aes-256-gcm', key, Buffer.from(ivHex, 'hex')); dec.setAuthTag(Buffer.from(tagHex, 'hex'));
  const plain = Buffer.concat([dec.update(Buffer.from(ctHex, 'hex')), dec.final()]).toString('utf8');
  assert.equal(plain, VINS.renault);
  d.offchain('export-vin-key-analogue', 'off-chain AES-256-GCM decrypt of getVehicleBirth().encryptedVIN', 'the owner decrypts the on-chain ciphertext back to the VIN (provider: export_vin_key hands the key to a buyer); the chain cannot verify that the ciphertext matches the hash');
  assert.equal(ethers.sha256(ethers.concat([ethers.toUtf8Bytes(plain), salt, vehicle])), vinHashSha);
  d.offchain('verify-binding-offchain', 'off-chain SHA-256', 'with VIN + salt + identity in hand, a verifier recomputes the hash and compares with the birth certificate: this is the only VIN check that exists');
  const logs = await reg.queryFilter(reg.filters.VehicleBirthRegistered(null, vinHashSha), 0, 'latest');
  assert.equal(logs.length, 1);
  d.offchain('vin-hash-indexed-in-event', 'MOBIVIDRegistryV2.VehicleBirthRegistered', 'vinHash is an indexed topic: an indexer can find a vehicle by hash without the mapping (no plain VIN anywhere — contrast ERC-721/1155/LSP8)');
});
