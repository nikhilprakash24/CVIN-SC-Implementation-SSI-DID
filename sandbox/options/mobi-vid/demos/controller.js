'use strict';
/**
 * MOBI VID — family "Ownership / controller change" (manifest: measured-in-comparison via
 * transferVehicleOwnership). Two controller-change paths: the inherited ERC-1056 changeOwner
 * (owner pointer only, DIDOwnerChanged) and the VID II transferVehicleOwnership (odometer-
 * stamped OwnershipTransfer record + changeOwner + VehicleOwnershipTransferred). Plus the
 * owner views (identityOwner / owners), the history getters and the guards.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/mobi-vid/demos/controller.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, eventCount, VINS } = require('./_lib');

const d = demo('mobi-vid', 'controller');

d.run(async () => {
  const [authority, firstOwner, buyer, buyer2, stranger] = await ethers.getSigners();
  const { assert } = d;
  const reg = await (await ethers.getContractFactory('MOBIVIDRegistryV2', authority)).deploy();
  await reg.waitForDeployment();
  const vehicle = ethers.Wallet.createRandom().address;
  await reg.registerVehicleBirth(vehicle, ethers.sha256(ethers.toUtf8Bytes(VINS.vw)), 'enc:placeholder', ethers.id('cert'), firstOwner.address, '0x');
  d.offchain('setup', 'MOBIVIDRegistryV2.registerVehicleBirth', `vehicle ${vehicle.slice(0, 10)}… born to firstOwner`);

  await d.view('identity-owner', 'MOBIVIDRegistryV2.identityOwner', reg.identityOwner(vehicle), 'controller = ERC-1056 owner', (v) => assert.equal(v, firstOwner.address));
  await d.view('owners-raw', 'MOBIVIDRegistryV2.owners', reg.owners(vehicle), 'raw mapping (zero means "self-owned" in identityOwner)', (v) => assert.equal(v, firstOwner.address));
  await d.view('owners-raw-unregistered', 'MOBIVIDRegistryV2.owners', reg.owners(stranger.address), 'zero for an address never touched', (v) => assert.equal(v, ethers.ZeroAddress));
  await d.view('history-count-0', 'MOBIVIDRegistryV2.getOwnershipHistoryCount', reg.getOwnershipHistoryCount(vehicle), 'birth is not an ownership transfer record', (v) => assert.equal(v, 0n));

  await d.reverts('change-owner-unauthorised', 'MOBIVIDRegistryV2.changeOwner', () => reg.connect(stranger).changeOwner(vehicle, stranger.address), 'Only owner can perform this action', 'ERC-1056 onlyOwner');
  const r1 = await d.tx('change-owner', 'MOBIVIDRegistryV2.changeOwner', reg.connect(firstOwner).changeOwner(vehicle, buyer.address),
    'MEASURED as controller-change: plain ERC-1056 changeOwner — only DIDOwnerChanged, NO OwnershipTransfer record, no odometer');
  assert.equal(eventArgs(reg, r1, 'DIDOwnerChanged').owner, buyer.address);
  assert.equal(eventCount(reg, r1, 'VehicleOwnershipTransferred'), 0);
  await d.view('history-count-still-0', 'MOBIVIDRegistryV2.getOwnershipHistoryCount', reg.getOwnershipHistoryCount(vehicle), 'OBSERVATION: changeOwner bypasses the VID II ownership history — a sale recorded this way is invisible to getOwnershipHistory', (v) => assert.equal(v, 0n));
  await d.view('owner-after-change', 'MOBIVIDRegistryV2.identityOwner', reg.identityOwner(vehicle), 'buyer controls', (v) => assert.equal(v, buyer.address));
  await d.reverts('old-owner-locked-out', 'MOBIVIDRegistryV2.changeOwner', () => reg.connect(firstOwner).changeOwner(vehicle, firstOwner.address), 'Only owner can perform this action', 'previous owner powerless');

  await d.reverts('transfer-unauthorised', 'MOBIVIDRegistryV2.transferVehicleOwnership', () => reg.connect(stranger).transferVehicleOwnership(vehicle, stranger.address, 1, 'X'), 'Only owner can perform this action', 'only the current owner sells');
  await d.reverts('transfer-zero', 'MOBIVIDRegistryV2.transferVehicleOwnership', () => reg.connect(buyer).transferVehicleOwnership(vehicle, ethers.ZeroAddress, 1, 'X'), 'Invalid new owner', 'guard');
  await d.reverts('transfer-unregistered', 'MOBIVIDRegistryV2.transferVehicleOwnership', () => reg.connect(stranger).transferVehicleOwnership(stranger.address, buyer.address, 1, 'X'), 'Vehicle not registered', 'needs a birth certificate (a registerVehicle-only identity cannot use VID II transfers)');
  const r2 = await d.tx('transfer-vehicle-ownership', 'MOBIVIDRegistryV2.transferVehicleOwnership', reg.connect(buyer).transferVehicleOwnership(vehicle, buyer2.address, 48210, 'KBA Flensburg'),
    'MEASURED (transferOwnership): appends OwnershipTransfer{from,to,timestamp,block,odometer,authority}, then changeOwner -> VehicleOwnershipTransferred + DIDOwnerChanged');
  const te = eventArgs(reg, r2, 'VehicleOwnershipTransferred'); assert.equal(te.from, buyer.address); assert.equal(te.to, buyer2.address); assert.equal(te.odometer, 48210n);
  assert.equal(eventCount(reg, r2, 'DIDOwnerChanged'), 1);
  await d.tx('transfer-again', 'MOBIVIDRegistryV2.transferVehicleOwnership', reg.connect(buyer2).transferVehicleOwnership(vehicle, firstOwner.address, 61000, 'KBA Flensburg'), 'second sale, higher odometer');
  await d.tx('transfer-rollback', 'MOBIVIDRegistryV2.transferVehicleOwnership', reg.connect(firstOwner).transferVehicleOwnership(vehicle, buyer.address, 30000, 'DMV-CA'), 'OBSERVATION: a LOWER odometer than the previous transfer is accepted (no monotonicity check) — fraud detection is left to the verifier');
  await d.view('get-ownership-history', 'MOBIVIDRegistryV2.getOwnershipHistory', reg.getOwnershipHistory(vehicle), 'full on-chain record list (unique among the compared options together with ERC-721)',
    (h) => { assert.equal(h.length, 3); assert.equal(h[0].from, buyer.address); assert.equal(Number(h[2].odometer), 30000); assert.equal(h[1].registrationAuthority, 'KBA Flensburg'); });
  await d.view('history-count', 'MOBIVIDRegistryV2.getOwnershipHistoryCount', reg.getOwnershipHistoryCount(vehicle), '3 VID II transfers (the earlier changeOwner is missing)', (v) => assert.equal(v, 3n));
  await d.view('ownership-history-raw', 'MOBIVIDRegistryV2.ownershipHistory', reg.ownershipHistory(vehicle, 1), 'raw getter (identity, index)', (t) => { assert.equal(t.to, firstOwner.address); assert.equal(Number(t.odometer), 61000); });
  await d.view('owner-final', 'MOBIVIDRegistryV2.identityOwner', reg.identityOwner(vehicle), 'buyer again', (v) => assert.equal(v, buyer.address));
  await d.reverts('get-history-unregistered', 'MOBIVIDRegistryV2.getOwnershipHistory', () => reg.getOwnershipHistory(stranger.address), 'Vehicle not registered', 'checked getter (the count getter is unchecked and returns 0)');
  await d.tx('revoke-identity', 'MOBIVIDRegistryV2.revokeIdentity', reg.connect(buyer).revokeIdentity(vehicle), 'owner decommissions the identity');
  await d.reverts('transfer-after-revoke', 'MOBIVIDRegistryV2.transferVehicleOwnership', () => reg.connect(buyer).transferVehicleOwnership(vehicle, buyer2.address, 1, 'X'), 'Vehicle identity is revoked', 'VID II transfer blocked');
  await d.reverts('change-owner-after-revoke', 'MOBIVIDRegistryV2.changeOwner', () => reg.connect(buyer).changeOwner(vehicle, buyer2.address), 'Identity is revoked', 'FIXED (D21): the inherited changeOwner now checks the revoked flag — a decommissioned identity cannot change hands at the ERC-1056 level either (formerly it could)');
  await d.view('owner-frozen-after-revoke', 'MOBIVIDRegistryV2.identityOwner', reg.identityOwner(vehicle), 'the owner at decommissioning time is frozen', (v) => assert.equal(v, buyer.address));
});
