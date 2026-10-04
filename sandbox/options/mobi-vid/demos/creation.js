'use strict';
/**
 * MOBI VID — family "Identity creation (explicit)" (manifest: measured-in-comparison via
 * registerVehicleBirth / registerVehicle). VID I birth certificate: an authorised manufacturer
 * anchors (vinHash, encryptedVIN, birthCertHash, firstOwner) to a vehicle identity ADDRESS (the
 * vehicle's own key) in an ERC-1056 registry. The chain never sees the VIN: hashing (SHA-256 +
 * salt, as the Python provider does) and encryption (AES-256-GCM) happen off-chain. Exercises
 * both creation paths, all getters and every guard, including the fixed birthAttributes path.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/mobi-vid/demos/creation.js
 */
const crypto = require('node:crypto');
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, eventCount, VINS } = require('./_lib');

const d = demo('mobi-vid', 'creation');

d.run(async () => {
  const [authority, firstOwner, manufacturer2, stranger] = await ethers.getSigners();
  const { assert } = d;
  const F = await ethers.getContractFactory('MOBIVIDRegistryV2', authority);
  const reg = await F.deploy();
  await reg.waitForDeployment();
  const dep = await reg.deploymentTransaction().wait();
  assert.equal(eventArgs(reg, dep, 'ManufacturerAuthorized').manufacturer, authority.address);
  d.offchain('deploy', 'MOBIVIDRegistryV2.constructor', `registry deployed, gasUsed=${dep.gasUsed}; deployer = registryAuthority + auto-authorised manufacturer (ManufacturerAuthorized); allowedIssuers matrix initialised; measured as deployRegistry`);

  // ---- off-chain preparation (what the Python provider does before the tx) ----
  const vehicleKey = ethers.Wallet.createRandom();
  const salt = crypto.randomBytes(16);
  const vinHash = ethers.sha256(ethers.concat([ethers.toUtf8Bytes(VINS.bmw), salt, vehicleKey.address]));
  const aesKey = crypto.randomBytes(32), iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', aesKey, iv);
  const ct = Buffer.concat([cipher.update(VINS.bmw, 'utf8'), cipher.final()]);
  const encryptedVIN = `aes-256-gcm:${iv.toString('hex')}:${ct.toString('hex')}:${cipher.getAuthTag().toString('hex')}`;
  const birthCert = { vin: VINS.bmw, make: 'BMW', model: '320d', year: 2012, plant: 'Munich', did: `did:ethr:0x7a69:${vehicleKey.address.toLowerCase()}` };
  const birthCertHash = ethers.sha256(ethers.toUtf8Bytes(JSON.stringify(birthCert)));
  d.offchain('prepare-birth', 'off-chain SHA-256 + AES-256-GCM', `vehicle identity = fresh secp256k1 key ${vehicleKey.address.slice(0, 10)}…; vinHash = SHA-256(VIN || 16-byte salt || identity); VIN encrypted with a random AES key (only the owner can decrypt); birthCertHash = SHA-256(certificate JSON)`);

  await d.view('exists-before', 'MOBIVIDRegistryV2.vehicleExists', reg.vehicleExists(vehicleKey.address), 'no birth certificate yet', (v) => assert.equal(v, false));
  await d.view('owner-before', 'MOBIVIDRegistryV2.identityOwner', reg.identityOwner(vehicleKey.address), 'ERC-1056 default: an unregistered identity is owned by itself (the key)', (v) => assert.equal(v, vehicleKey.address));
  const r = await d.tx('register-birth', 'MOBIVIDRegistryV2.registerVehicleBirth', reg.connect(authority).registerVehicleBirth(vehicleKey.address, vinHash, encryptedVIN, birthCertHash, firstOwner.address, '0x'),
    'MEASURED (createIdentity): manufacturer writes the VID I birth certificate struct, the vinHash index and owners[identity]=firstOwner -> VehicleBirthRegistered + DIDOwnerChanged');
  const ev = eventArgs(reg, r, 'VehicleBirthRegistered');
  assert.equal(ev.vehicleIdentity, vehicleKey.address); assert.equal(ev.vinHash, vinHash); assert.equal(ev.manufacturer, authority.address); assert.equal(ev.firstOwner, firstOwner.address);
  assert.equal(eventCount(reg, r, 'DIDOwnerChanged'), 1); assert.equal(eventCount(reg, r, 'DIDAttributeChanged'), 0);
  d.offchain('birth-events', 'MOBIVIDRegistryV2.VehicleBirthRegistered+DIDOwnerChanged', 'the ERC-1056 DIDOwnerChanged lets a did:ethr resolver see the owner without knowing MOBI; no DIDAttributeChanged because birthAttributes was empty');
  await d.view('exists-after', 'MOBIVIDRegistryV2.vehicleExists', reg.vehicleExists(vehicleKey.address), 'registered', (v) => assert.equal(v, true));
  await d.view('owner-after', 'MOBIVIDRegistryV2.identityOwner', reg.identityOwner(vehicleKey.address), 'OBSERVATION: the vehicle\'s own key is no longer its ERC-1056 owner — control moved to firstOwner at birth', (v) => assert.equal(v, firstOwner.address));
  await d.view('get-vehicle-birth', 'MOBIVIDRegistryV2.getVehicleBirth', reg.getVehicleBirth(vehicleKey.address), 'the struct: vinHash, encryptedVIN, birthCertHash, timestamp, manufacturer, firstOwner, blockNumber, exists',
    (b) => { assert.equal(b.vinHash, vinHash); assert.equal(b.encryptedVIN, encryptedVIN); assert.equal(b.birthCertHash, birthCertHash); assert.equal(b.manufacturer, authority.address); assert.equal(b.exists, true); });
  await d.view('vehicle-births-raw', 'MOBIVIDRegistryV2.vehicleBirths', reg.vehicleBirths(vehicleKey.address), 'raw public-mapping getter (same fields, no existence check)', (b) => assert.equal(b.firstOwner, firstOwner.address));
  await d.view('lookup-by-vin-hash', 'MOBIVIDRegistryV2.lookupByVINHash', reg.lookupByVINHash(vinHash), 'hash -> identity; only someone who knows VIN + salt can compute the key', (v) => assert.equal(v, vehicleKey.address));
  await d.view('get-vehicle-info', 'MOBIVIDRegistryV2.getVehicleInfo', reg.getVehicleInfo(vehicleKey.address), 'combined view: birth + currentOwner + isRevoked + transferCount', (v) => { assert.equal(v.currentOwner, firstOwner.address); assert.equal(v.isRevoked, false); assert.equal(v.transferCount, 0n); });
  const dec = crypto.createDecipheriv('aes-256-gcm', aesKey, iv); dec.setAuthTag(Buffer.from(encryptedVIN.split(':')[3], 'hex'));
  const plain = Buffer.concat([dec.update(Buffer.from(encryptedVIN.split(':')[2], 'hex')), dec.final()]).toString('utf8');
  assert.equal(plain, VINS.bmw);
  d.offchain('decrypt-vin', 'off-chain AES-256-GCM', 'the owner (key holder) recovers the VIN from the on-chain ciphertext; the chain stores it opaque (provider: export_vin_key)');

  // ---- birthAttributes path (previously overflowed with type(uint256).max validity) ----
  const vk2 = ethers.Wallet.createRandom();
  const vh2 = ethers.sha256(ethers.toUtf8Bytes(`${VINS.honda}|${salt.toString('hex')}`));
  const attrs = ethers.toUtf8Bytes(JSON.stringify({ make: 'Honda', model: 'Accord', year: 2003, engine: 'K24A4' }));
  const r2 = await d.tx('register-birth-with-attributes', 'MOBIVIDRegistryV2.registerVehicleBirth', reg.connect(authority).registerVehicleBirth(vk2.address, vh2, 'enc:placeholder', ethers.sha256(attrs), firstOwner.address, attrs),
    'non-empty birthAttributes: stored as an ERC-1056 attribute "mobi/vid/birth/attributes" with PERMANENT_ATTRIBUTE_VALIDITY (100y) written with firstOwner as actor (the fixed path: no overflow, no actor mismatch)');
  const ae = eventArgs(reg, r2, 'DIDAttributeChanged');
  assert.equal(ae.name, ethers.id('mobi/vid/birth/attributes'));
  const PERM = await reg.PERMANENT_ATTRIBUTE_VALIDITY();
  assert.equal(ae.validTo, BigInt((await ethers.provider.getBlock(r2.blockNumber)).timestamp) + PERM);
  await d.view('permanent-validity', 'MOBIVIDRegistryV2.PERMANENT_ATTRIBUTE_VALIDITY', Promise.resolve(PERM), '100 * 365 days: finite "permanent" to avoid the checked-arithmetic panic the benchmark note documents', (v) => assert.equal(v, 100n * 365n * 24n * 3600n));

  // ---- guards ----
  await d.reverts('register-unauthorised', 'MOBIVIDRegistryV2.registerVehicleBirth', () => reg.connect(stranger).registerVehicleBirth(ethers.Wallet.createRandom().address, ethers.id('x'), 'e', ethers.id('c'), firstOwner.address, '0x'), 'Only authorized manufacturers', 'birth is manufacturer-only');
  await d.reverts('register-duplicate-identity', 'MOBIVIDRegistryV2.registerVehicleBirth', () => reg.connect(authority).registerVehicleBirth(vehicleKey.address, ethers.id('other'), 'e', ethers.id('c'), firstOwner.address, '0x'), 'Vehicle already registered', 'one birth per identity');
  await d.reverts('register-duplicate-vin-hash', 'MOBIVIDRegistryV2.registerVehicleBirth', () => reg.connect(authority).registerVehicleBirth(ethers.Wallet.createRandom().address, vinHash, 'e', ethers.id('c'), firstOwner.address, '0x'), 'VIN hash already registered', 'VIN uniqueness only at the hash level: the same VIN with a different salt would pass (uniqueness depends on the off-chain hashing convention)');
  await d.reverts('register-zero-identity', 'MOBIVIDRegistryV2.registerVehicleBirth', () => reg.connect(authority).registerVehicleBirth(ethers.ZeroAddress, ethers.id('y'), 'e', ethers.id('c'), firstOwner.address, '0x'), 'Invalid vehicle identity', 'guard');
  await d.reverts('register-zero-vin-hash', 'MOBIVIDRegistryV2.registerVehicleBirth', () => reg.connect(authority).registerVehicleBirth(ethers.Wallet.createRandom().address, ethers.ZeroHash, 'e', ethers.id('c'), firstOwner.address, '0x'), 'Invalid VIN hash', 'guard');
  await d.reverts('register-zero-owner', 'MOBIVIDRegistryV2.registerVehicleBirth', () => reg.connect(authority).registerVehicleBirth(ethers.Wallet.createRandom().address, ethers.id('z'), 'e', ethers.id('c'), ethers.ZeroAddress, '0x'), 'Invalid first owner', 'guard');
  await d.reverts('get-birth-unregistered', 'MOBIVIDRegistryV2.getVehicleBirth', () => reg.getVehicleBirth(stranger.address), 'Vehicle not registered', 'checked getter');
  await d.tx('authorise-manufacturer-2', 'MOBIVIDRegistryV2.authorizeManufacturer', reg.connect(authority).authorizeManufacturer(manufacturer2.address), 'a second OEM is authorised by the registry authority');
  await d.tx('register-by-manufacturer-2', 'MOBIVIDRegistryV2.registerVehicleBirth', reg.connect(manufacturer2).registerVehicleBirth(ethers.Wallet.createRandom().address, ethers.sha256(ethers.toUtf8Bytes(VINS.toyota)), 'enc:placeholder', ethers.id('cert'), firstOwner.address, '0x'), 'the second OEM registers a birth (manufacturer recorded in the struct)');

  // ---- the ERC-1056 utility path: key-based self-registration ----
  const pubkey = ethers.toUtf8Bytes(Buffer.from(ethers.getBytes(ethers.SigningKey.computePublicKey(ethers.Wallet.createRandom().privateKey, true))).toString('base64'));
  const r3 = await d.tx('register-vehicle-erc1056', 'MOBIVIDRegistryV2.registerVehicle', reg.connect(stranger).registerVehicle(stranger.address, pubkey),
    'MEASURED (registerVehicle): the inherited ERC-1056 convenience path — the identity registers ITSELF by publishing a veriKey attribute (1-year validity); no birth certificate, no manufacturer');
  assert.equal(eventArgs(reg, r3, 'DIDAttributeChanged').name, ethers.id('did/pub/secp256k1/veriKey/base64'));
  await d.reverts('register-vehicle-for-other', 'MOBIVIDRegistryV2.registerVehicle', () => reg.connect(stranger).registerVehicle(firstOwner.address, pubkey), 'Only owner can perform this action', 'msg.sender must be the identity (its default owner): self-sovereign by construction');
  await d.tx('register-vehicle-again', 'MOBIVIDRegistryV2.registerVehicle', reg.connect(stranger).registerVehicle(stranger.address, pubkey), 'OBSERVATION: "Identity already registered" never triggers while the identity still owns itself (registerVehicle only sets an attribute), so it can be repeated');
  await d.view('erc1056-identity-no-birth', 'MOBIVIDRegistryV2.vehicleExists', reg.vehicleExists(stranger.address), 'a registerVehicle identity has no VID I birth certificate: the two creation paths are disjoint', (v) => assert.equal(v, false));
});
