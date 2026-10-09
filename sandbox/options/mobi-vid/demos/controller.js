'use strict';
/**
 * MOBI VID — family "Ownership / controller change" (manifest: measured-in-comparison via
 * transferVehicleOwnership). Since the merge (K-3, 2026-10-06) a BORN vehicle has exactly one
 * controller-change path: the VID II transferVehicleOwnership (odometer-stamped
 * OwnershipTransfer record + changeOwner + VehicleOwnershipTransferred); the inherited public
 * ERC-1056 changeOwner reverts "MOBIVID: use transferVehicleOwnership" for every caller, so a
 * sale can no longer bypass the ownership history (D16 rest). A non-born identity (ERC-1056
 * self-registration via registerVehicle) keeps plain changeOwner — shown as the contrast. Plus
 * the owner views (identityOwner / owners), the history getters and the guards.
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

  // ---- K-3: the public ERC-1056 changeOwner is closed for born vehicles, whoever calls ----
  await d.reverts('change-owner-unauthorised', 'MOBIVIDRegistryV2.changeOwner', () => reg.connect(stranger).changeOwner(vehicle, stranger.address), 'MOBIVID: use transferVehicleOwnership',
    'FIXED (K-3): the override reverts BEFORE the ERC-1056 onlyOwner check — a stranger is turned away with the routing reason, not "Only owner can perform this action"');
  await d.reverts('change-owner-by-owner-closed', 'MOBIVIDRegistryV2.changeOwner', () => reg.connect(firstOwner).changeOwner(vehicle, buyer.address), 'MOBIVID: use transferVehicleOwnership',
    'FIXED (K-3 / D16 rest): even the legitimate owner cannot use plain changeOwner on a born vehicle — formerly this moved the controller with only a DIDOwnerChanged, NO OwnershipTransfer record and no odometer (OBSERVATION "changeOwner bypasses the VID II ownership history" in the pre-merge run)');
  await d.view('no-bypass-possible', 'MOBIVIDRegistryV2.getOwnershipHistoryCount+identityOwner', Promise.all([reg.getOwnershipHistoryCount(vehicle), reg.identityOwner(vehicle)]),
    'nothing moved: history count still 0 and firstOwner still controls — every controller change of a born vehicle must leave an odometer-stamped record', (v) => assert.deepEqual(v, [0n, firstOwner.address]));

  // ---- contrast: a non-born identity (ERC-1056 self-registration) keeps plain changeOwner ----
  await d.tx('register-vehicle-erc1056', 'MOBIVIDRegistryV2.registerVehicle', reg.connect(stranger).registerVehicle(stranger.address, ethers.toUtf8Bytes('pubkey-placeholder')), 'the stranger self-registers as a bare ERC-1056 identity (veriKey attribute; no birth certificate)');
  const r1 = await d.tx('change-owner-non-born', 'MOBIVIDRegistryV2.changeOwner', reg.connect(stranger).changeOwner(stranger.address, buyer.address),
    'plain ERC-1056 changeOwner still works for an identity WITHOUT a birth certificate: only DIDOwnerChanged, no ownership record — K-3 gates on vehicleBirths[identity].exists, not on the caller');
  assert.equal(eventArgs(reg, r1, 'DIDOwnerChanged').owner, buyer.address);
  assert.equal(eventCount(reg, r1, 'VehicleOwnershipTransferred'), 0);
  await d.view('owner-after-change-non-born', 'MOBIVIDRegistryV2.identityOwner', reg.identityOwner(stranger.address), 'buyer controls the bare identity', (v) => assert.equal(v, buyer.address));
  await d.reverts('old-owner-locked-out', 'MOBIVIDRegistryV2.changeOwner', () => reg.connect(stranger).changeOwner(stranger.address, stranger.address), 'Only owner can perform this action', 'ERC-1056 onlyOwner on the non-born identity: the previous owner is powerless');

  // ---- the only path for born vehicles: transferVehicleOwnership ----
  await d.reverts('transfer-unauthorised', 'MOBIVIDRegistryV2.transferVehicleOwnership', () => reg.connect(stranger).transferVehicleOwnership(vehicle, stranger.address, 1, 'X'), 'Only owner can perform this action', 'only the current owner sells');
  await d.reverts('transfer-zero', 'MOBIVIDRegistryV2.transferVehicleOwnership', () => reg.connect(firstOwner).transferVehicleOwnership(vehicle, ethers.ZeroAddress, 1, 'X'), 'Invalid new owner', 'guard');
  await d.reverts('transfer-unregistered', 'MOBIVIDRegistryV2.transferVehicleOwnership', () => reg.connect(buyer).transferVehicleOwnership(stranger.address, buyer2.address, 1, 'X'), 'Vehicle not registered', 'needs a birth certificate (the bare ERC-1056 identity, even by its current owner, cannot use VID II transfers): the two paths are disjoint in both directions');
  const r2 = await d.tx('transfer-vehicle-ownership', 'MOBIVIDRegistryV2.transferVehicleOwnership', reg.connect(firstOwner).transferVehicleOwnership(vehicle, buyer.address, 48210, 'KBA Flensburg'),
    'MEASURED (transferOwnership / controller-change): appends OwnershipTransfer{from,to,timestamp,block,odometer,authority}, then the INTERNAL changeOwner -> VehicleOwnershipTransferred + DIDOwnerChanged (the override only closes the public entry point)');
  const te = eventArgs(reg, r2, 'VehicleOwnershipTransferred'); assert.equal(te.from, firstOwner.address); assert.equal(te.to, buyer.address); assert.equal(te.odometer, 48210n);
  assert.equal(eventCount(reg, r2, 'DIDOwnerChanged'), 1);
  await d.view('history-count-1', 'MOBIVIDRegistryV2.getOwnershipHistoryCount', reg.getOwnershipHistoryCount(vehicle), 'the sale is in the history (FIXED K-3: no other way to move a born vehicle exists)', (v) => assert.equal(v, 1n));
  await d.tx('transfer-again', 'MOBIVIDRegistryV2.transferVehicleOwnership', reg.connect(buyer).transferVehicleOwnership(vehicle, buyer2.address, 61000, 'KBA Flensburg'), 'second sale, higher odometer');
  await d.tx('transfer-rollback', 'MOBIVIDRegistryV2.transferVehicleOwnership', reg.connect(buyer2).transferVehicleOwnership(vehicle, firstOwner.address, 30000, 'DMV-CA'), 'OBSERVATION: a LOWER odometer than the previous transfer is accepted (no monotonicity check) — fraud detection is left to the verifier');
  await d.view('get-ownership-history', 'MOBIVIDRegistryV2.getOwnershipHistory', reg.getOwnershipHistory(vehicle), 'full on-chain record list (unique among the compared options together with ERC-721) — and since K-3 it is COMPLETE for a born vehicle',
    (h) => { assert.equal(h.length, 3); assert.equal(h[0].from, firstOwner.address); assert.equal(Number(h[2].odometer), 30000); assert.equal(h[1].registrationAuthority, 'KBA Flensburg'); });
  await d.view('history-count', 'MOBIVIDRegistryV2.getOwnershipHistoryCount', reg.getOwnershipHistoryCount(vehicle), '3 VID II transfers = 3 controller changes (nothing is missing)', (v) => assert.equal(v, 3n));
  await d.view('ownership-history-raw', 'MOBIVIDRegistryV2.ownershipHistory', reg.ownershipHistory(vehicle, 1), 'raw getter (identity, index)', (t) => { assert.equal(t.to, buyer2.address); assert.equal(Number(t.odometer), 61000); });
  await d.view('owner-final', 'MOBIVIDRegistryV2.identityOwner', reg.identityOwner(vehicle), 'firstOwner again', (v) => assert.equal(v, firstOwner.address));
  await d.reverts('get-history-unregistered', 'MOBIVIDRegistryV2.getOwnershipHistory', () => reg.getOwnershipHistory(stranger.address), 'Vehicle not registered', 'checked getter (the count getter is unchecked and returns 0)');
  await d.tx('revoke-identity', 'MOBIVIDRegistryV2.revokeIdentity', reg.connect(firstOwner).revokeIdentity(vehicle), 'owner decommissions the identity');
  await d.reverts('transfer-after-revoke', 'MOBIVIDRegistryV2.transferVehicleOwnership', () => reg.connect(firstOwner).transferVehicleOwnership(vehicle, buyer2.address, 1, 'X'), 'Vehicle identity is revoked', 'FIXED (D21): the VID II transfer is blocked on a revoked identity — the only controller-change path of a born vehicle is closed, so the ownership record is frozen');
  await d.reverts('change-owner-after-revoke', 'MOBIVIDRegistryV2.changeOwner', () => reg.connect(firstOwner).changeOwner(vehicle, buyer2.address), 'MOBIVID: use transferVehicleOwnership', 'K-3 fires first for a born vehicle (the D21 revoked-flag check sits behind it; revocation.js shows it on a non-born identity)');
  await d.view('owner-frozen-after-revoke', 'MOBIVIDRegistryV2.identityOwner', reg.identityOwner(vehicle), 'the owner at decommissioning time is frozen', (v) => assert.equal(v, firstOwner.address));
});
