'use strict';
/**
 * MOBI VID — family "DID / resolution helpers" (manifest: measured-in-comparison via
 * getIdentityInfo). On-chain helpers for a did:ethr resolver: getVehicleDID (string), identityOwner
 * (controller), getIdentityInfo (owner, lastChanged, revoked, revokedAt), getVehicleInfo, plus the
 * adapter's resolve() which replays ERC-1056 logs into a DID document with delegates, attributes,
 * birth certificate, ownership history and lifecycle event ids.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/mobi-vid/demos/did-resolution.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, VINS } = require('./_lib');
const MobiVidAdapter = require('../adapter');

const d = demo('mobi-vid', 'did-resolution');

d.run(async () => {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const { assert } = d;
  const adapter = new MobiVidAdapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  const dep = await adapter.deploy();
  const reg = adapter.contract;
  const created = await adapter.create({ vin: VINS.volvo, owner: vehicleOwner.address });
  const id = created.id;
  d.offchain('setup', 'adapter.deploy + adapter.create', `registry (gas ${dep.gasUsed}, setup ${dep.setupGasUsed}); identity ${id} derived by the adapter from the VIN (key-less DID) owned by vehicleOwner`);

  const chainId = (await ethers.provider.getNetwork()).chainId;
  const didOnChain = await d.view('get-vehicle-did', 'MOBIVIDRegistryV2.getVehicleDID', reg.getVehicleDID(id),
    'POTENTIAL DEFECT: returns did:ethr:0x<chainId hex>:<40 hex chars> WITHOUT the 0x prefix on the address (_toHexString(value,20) adds none), which is not a conformant did:ethr identifier; the adapter\'s resolve() copies it verbatim',
    (v) => assert.equal(v, `did:ethr:0x${chainId.toString(16)}:${id.toLowerCase().slice(2)}`));
  await d.view('get-vehicle-did-any-address', 'MOBIVIDRegistryV2.getVehicleDID', reg.getVehicleDID(delegate.address), 'OBSERVATION: any address resolves to a DID string, registered or not (ERC-1056 semantics: every address is an identity)', (v) => assert.ok(v.startsWith('did:ethr:')));
  await d.view('identity-owner', 'MOBIVIDRegistryV2.identityOwner', reg.identityOwner(id), 'controller', (v) => assert.equal(v, vehicleOwner.address));
  await d.view('get-identity-info', 'MOBIVIDRegistryV2.getIdentityInfo', reg.getIdentityInfo(id), 'MEASURED (resolve): (owner, lastChangedBlock, isRevoked, revokedTimestamp)', (v) => { assert.equal(v.owner, vehicleOwner.address); assert.ok(v.lastChangedBlock > 0n); assert.equal(v.isRevoked, false); });
  await d.view('get-identity-info-unregistered', 'MOBIVIDRegistryV2.getIdentityInfo', reg.getIdentityInfo(delegate.address), 'an unknown address resolves to itself as owner with lastChanged 0', (v) => { assert.equal(v.owner, delegate.address); assert.equal(v.lastChangedBlock, 0n); });
  await d.view('get-vehicle-info', 'MOBIVIDRegistryV2.getVehicleInfo', reg.getVehicleInfo(id), 'VID view: birth + owner + revoked + transfer count', (v) => { assert.equal(v.birth.exists, true); assert.equal(v.transferCount, 0n); });

  await adapter.addKeyOrDelegate(id, delegate.address, 'sigAuth', 3600);
  await adapter.setAttribute(id, 'did/svc/telematics', 'https://telematics.example/v/1');
  await adapter.addClaim(id, 'MAINTENANCE', '0x01', '0x');
  await adapter.transfer(id, newOwner.address);
  d.offchain('populate', 'adapter.addKeyOrDelegate+setAttribute+addClaim+transfer', 'delegate, service attribute, one lifecycle event, one sale');
  const res = await adapter.resolve(id);
  const doc = res.value;
  assert.equal(doc.id, didOnChain);
  assert.equal(doc.controller, newOwner.address);
  assert.equal(doc.verificationMethod.length, 2);
  assert.equal(doc.verificationMethod[1].blockchainAccountId, `eip155:${chainId}:${delegate.address}`);
  assert.equal(doc.service.length, 1);
  assert.equal(doc.ownershipHistory.length, 1);
  assert.equal(doc.lifecycleEventIds.length, 1);
  assert.equal(doc.birthCertificate.firstOwner, vehicleOwner.address);
  d.offchain('resolve-via-adapter', 'adapter.resolve (getIdentityInfo, getVehicleDID, vehicleExists, getVehicleBirth, getOwnershipHistory, getVehicleEvents, DIDDelegateChanged/DIDAttributeChanged logs)',
    `DID document: controller=${doc.controller.slice(0, 10)}…, ${doc.verificationMethod.length} verification methods (controller + sigAuth delegate), ${doc.service.length} service, birth certificate, ${doc.ownershipHistory.length} transfer, ${doc.lifecycleEventIds.length} event id; MEASURED as resolve (gas 0)`);
  await adapter.revoke(id);
  const res2 = await adapter.resolve(id);
  assert.equal(res2.value.status.revoked, true);
  assert.ok(res2.value.status.revokedAt > 0);
  d.offchain('resolve-after-revoke', 'adapter.resolve', 'status.revoked=true with revokedAt: the resolver can state deactivation precisely (ERC-1056 extension; uPort\'s original has no revocation)');
});
