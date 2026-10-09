'use strict';
/**
 * MOBI VID — family "Revocation / status" (manifest: measured-in-comparison via revokeIdentity /
 * isRevoked / revoked). Four revocation levels: identity (revokeIdentity: permanent flag +
 * revokedAt + DIDRevoked), delegate and attribute (event-only validTo=now), issuer and
 * manufacturer authorisations. Shows that the revoked flag blocks every mutator (terminal since
 * the D21 fix: changeOwner, clean-up revocations and a second revokeIdentity revert, revokedAt is
 * frozen), and that the VID II DECOMMISSION event is NOT a revocation. Since the merge (K-3,
 * 2026-10-06) the public changeOwner of a BORN vehicle reverts "MOBIVID: use
 * transferVehicleOwnership" before the revoked check, so the D21 "Identity is revoked" path of
 * changeOwner is shown on a non-born (self-registered) identity.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/mobi-vid/demos/revocation.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('mobi-vid', 'revocation');

d.run(async () => {
  const [authority, owner, buyer, dmv, oem, stranger] = await ethers.getSigners();
  const { assert } = d;
  const reg = await (await ethers.getContractFactory('MOBIVIDRegistryV2', authority)).deploy();
  await reg.waitForDeployment();
  const vehicle = ethers.Wallet.createRandom().address;
  await reg.registerVehicleBirth(vehicle, ethers.sha256(ethers.toUtf8Bytes(VINS.fiat)), 'enc:placeholder', ethers.id('cert'), owner.address, '0x');
  await reg.authorizeIssuer(dmv.address, 5);
  await reg.authorizeManufacturer(oem.address);
  const SIG_AUTH = ethers.encodeBytes32String('sigAuth');
  d.offchain('setup', 'MOBIVIDRegistryV2.registerVehicleBirth+authorizeIssuer+authorizeManufacturer', 'vehicle born; DMV issuer; second OEM');

  await d.view('status-before', 'MOBIVIDRegistryV2.isRevoked+revoked+revokedAt', Promise.all([reg.isRevoked(vehicle), reg.revoked(vehicle), reg.revokedAt(vehicle)]), 'MEASURED (views): not revoked, revokedAt 0', (v) => assert.deepEqual(v, [false, false, 0n]));
  const r0 = await d.tx('decommission-event', 'MOBIVIDRegistryV2.recordLifecycleEvent', reg.connect(dmv).recordLifecycleEvent(vehicle, 10, 180000, ethers.id('scrap'), ethers.id('vc'), 'DE-BY'), 'VID II DECOMMISSION event recorded by the DMV');
  assert.equal(Number(eventArgs(reg, r0, 'LifecycleEventRecorded').eventType), 10);
  await d.view('decommission-is-not-revocation', 'MOBIVIDRegistryV2.isRevoked', reg.isRevoked(vehicle), 'OBSERVATION: a DECOMMISSION lifecycle event does not touch the ERC-1056 revoked flag — two unlinked notions of "end of life"', (v) => assert.equal(v, false));
  await d.reverts('revoke-unauthorised', 'MOBIVIDRegistryV2.revokeIdentity', () => reg.connect(stranger).revokeIdentity(vehicle), 'Only owner can perform this action', 'only the current owner (not the manufacturer, not the authority) can revoke the identity');
  const r1 = await d.tx('revoke-identity', 'MOBIVIDRegistryV2.revokeIdentity', reg.connect(owner).revokeIdentity(vehicle), 'MEASURED (revoke): revoked=true, revokedAt=now, DIDRevoked(identity, revokedAt), changed bumped');
  const ts1 = BigInt((await ethers.provider.getBlock(r1.blockNumber)).timestamp);
  assert.equal(eventArgs(reg, r1, 'DIDRevoked').revokedAt, ts1);
  await d.view('status-after', 'MOBIVIDRegistryV2.isRevoked+revoked+revokedAt', Promise.all([reg.isRevoked(vehicle), reg.revoked(vehicle), reg.revokedAt(vehicle)]), 'flag set with timestamp (a verifier gets a precise "valid until")', (v) => assert.deepEqual(v, [true, true, ts1]));
  await d.view('identity-info', 'MOBIVIDRegistryV2.getIdentityInfo', reg.getIdentityInfo(vehicle), '(owner, lastChangedBlock, isRevoked, revokedTimestamp) in one call', (v) => { assert.equal(v.isRevoked, true); assert.equal(v.revokedTimestamp, ts1); });
  await d.view('vehicle-info', 'MOBIVIDRegistryV2.getVehicleInfo', reg.getVehicleInfo(vehicle), 'VID view also reports isRevoked', (v) => assert.equal(v.isRevoked, true));
  await d.reverts('blocked-set-attribute', 'MOBIVIDRegistryV2.setAttribute', () => reg.connect(owner).setAttribute(vehicle, ethers.encodeBytes32String('x'), '0x01', 1n), 'Identity is revoked', 'blocked');
  await d.reverts('blocked-add-delegate', 'MOBIVIDRegistryV2.addDelegate', () => reg.connect(owner).addDelegate(vehicle, SIG_AUTH, buyer.address, 1n), 'Identity is revoked', 'blocked');
  await d.reverts('blocked-record-event', 'MOBIVIDRegistryV2.recordLifecycleEvent', () => reg.connect(dmv).recordLifecycleEvent(vehicle, 9, 1, ethers.id('x'), ethers.id('y'), 'DE'), 'Vehicle identity is revoked', 'blocked');
  await d.reverts('blocked-transfer', 'MOBIVIDRegistryV2.transferVehicleOwnership', () => reg.connect(owner).transferVehicleOwnership(vehicle, buyer.address, 1, 'X'), 'Vehicle identity is revoked', 'FIXED (D21): the ONLY controller-change path of a born vehicle (K-3) is blocked by the revoked flag — the ownership record is frozen');
  await d.reverts('blocked-register-vehicle', 'MOBIVIDRegistryV2.registerVehicle', () => reg.connect(stranger).registerVehicle(vehicle, '0x01'), 'Identity already revoked', 'blocked');
  await d.reverts('blocked-change-owner', 'MOBIVIDRegistryV2.changeOwner', () => reg.connect(owner).changeOwner(vehicle, buyer.address), 'MOBIVID: use transferVehicleOwnership', 'FIXED (K-3): for a born vehicle the public changeOwner is closed outright, revoked or not — the routing revert fires before the D21 revoked check (the pre-merge run asserted "Identity is revoked" here)');
  await d.reverts('blocked-rebirth', 'MOBIVIDRegistryV2.registerVehicleBirth', () => reg.connect(authority).registerVehicleBirth(vehicle, ethers.id('again'), 'e', ethers.id('c'), buyer.address, '0x'), 'Vehicle already registered', 'no second birth certificate for the revoked identity (and K-4 would refuse it anyway: changed != 0)');
  await d.reverts('blocked-revoke-delegate', 'MOBIVIDRegistryV2.revokeDelegate', () => reg.connect(owner).revokeDelegate(vehicle, SIG_AUTH, stranger.address), 'Identity is revoked', 'FIXED (D21, decision D-F): revocation is terminal — even delegate clean-up reverts (formerly allowed)');
  await d.reverts('blocked-revoke-attribute', 'MOBIVIDRegistryV2.revokeAttribute', () => reg.connect(owner).revokeAttribute(vehicle, ethers.encodeBytes32String('x'), '0x01'), 'Identity is revoked', 'FIXED (D21, decision D-F): attribute clean-up reverts too; isRevoked voids everything at once');
  await d.reverts('revoke-twice', 'MOBIVIDRegistryV2.revokeIdentity', () => reg.connect(owner).revokeIdentity(vehicle), 'Identity already revoked', 'FIXED (D21): a second revokeIdentity reverts (formerly it was accepted and OVERWROTE revokedAt, so the "permanent" timestamp could be moved forward)');
  await d.view('revoked-at-frozen', 'MOBIVIDRegistryV2.revokedAt', reg.revokedAt(vehicle), 'revokedAt is still the first (and only) revocation time', (v) => assert.equal(v, ts1));
  await d.view('owner-frozen', 'MOBIVIDRegistryV2.identityOwner', reg.identityOwner(vehicle), 'the last owner before decommissioning is frozen on-chain', (v) => assert.equal(v, owner.address));
  d.offchain('no-unrevoke', 'MOBIVIDRegistryV2', 'there is no un-revoke: the flag is one-way and terminal (unlike ERC-1155 deregistration which can be re-registered)');

  // ---- the D21 changeOwner gate, visible on a NON-born identity (K-3 does not apply there) ----
  await d.tx('bare-identity-self-register', 'MOBIVIDRegistryV2.registerVehicle', reg.connect(stranger).registerVehicle(stranger.address, '0x02'), 'a bare ERC-1056 identity (no birth certificate) publishes its key');
  await d.tx('bare-identity-revoke', 'MOBIVIDRegistryV2.revokeIdentity', reg.connect(stranger).revokeIdentity(stranger.address), 'and revokes itself');
  await d.reverts('bare-identity-blocked-change-owner', 'MOBIVIDRegistryV2.changeOwner', () => reg.connect(stranger).changeOwner(stranger.address, buyer.address), 'Identity is revoked', 'FIXED (D21): on an identity WITHOUT a birth certificate the public changeOwner is open (K-3 gates only born vehicles) and the revoked flag is what stops it — a decommissioned identity cannot change hands at the ERC-1056 level (formerly it could)');
  await d.reverts('bare-identity-blocked-rebirth', 'MOBIVIDRegistryV2.registerVehicleBirth', () => reg.connect(authority).registerVehicleBirth(stranger.address, ethers.id('late'), 'e', ethers.id('c'), buyer.address, '0x'), 'MOBIVID: identity already has DID history', 'FIXED (K-4): a manufacturer cannot give a revoked (or any already-used) did:ethr a birth certificate — registerVehicleBirth requires changed[identity] == 0');

  const r3 = await d.tx('revoke-issuer', 'MOBIVIDRegistryV2.revokeIssuerAuthorization', reg.connect(authority).revokeIssuerAuthorization(dmv.address), 'issuer-level revocation -> IssuerAuthorizationRevoked');
  assert.equal(eventArgs(reg, r3, 'IssuerAuthorizationRevoked').issuer, dmv.address);
  await d.view('issuer-role-none', 'MOBIVIDRegistryV2.authorizedIssuers', reg.authorizedIssuers(dmv.address), 'role reset to NONE (0)', (v) => assert.equal(Number(v), 0));
  const r4 = await d.tx('revoke-manufacturer', 'MOBIVIDRegistryV2.revokeManufacturerAuthorization', reg.connect(authority).revokeManufacturerAuthorization(oem.address), 'manufacturer-level revocation -> ManufacturerAuthorizationRevoked');
  assert.equal(eventArgs(reg, r4, 'ManufacturerAuthorizationRevoked').manufacturer, oem.address);
  await d.reverts('revoked-oem-cannot-register', 'MOBIVIDRegistryV2.registerVehicleBirth', () => reg.connect(oem).registerVehicleBirth(ethers.Wallet.createRandom().address, ethers.id('v'), 'e', ethers.id('c'), owner.address, '0x'), 'Only authorized manufacturers', 'locked out');
  await d.reverts('revoke-manufacturer-twice', 'MOBIVIDRegistryV2.revokeManufacturerAuthorization', () => reg.connect(authority).revokeManufacturerAuthorization(oem.address), 'Manufacturer not authorized', 'guard');
  await d.reverts('revoke-manufacturer-unauthorised', 'MOBIVIDRegistryV2.revokeManufacturerAuthorization', () => reg.connect(stranger).revokeManufacturerAuthorization(authority.address), 'Only registry authority', 'guard');
  await d.view('births-by-revoked-oem-survive', 'MOBIVIDRegistryV2.vehicleExists', reg.vehicleExists(vehicle), 'existing birth certificates are not invalidated by revoking their manufacturer', (v) => assert.equal(v, true));
});
