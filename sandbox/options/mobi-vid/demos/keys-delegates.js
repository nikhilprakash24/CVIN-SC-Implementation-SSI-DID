'use strict';
/**
 * MOBI VID — family "Key / delegate management" (manifest: measured-in-comparison via addDelegate).
 * Inherited ERC-1056 delegates: addDelegate / revokeDelegate are EVENT-ONLY (DIDDelegateChanged
 * with validTo); the registry keeps no delegate table and this profile omits validDelegate(), so a
 * verifier must replay logs. Also updateVehicleKey (veriKey attribute rotation), the `changed`
 * linked-list pointer, and the never-incremented `nonce`.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/mobi-vid/demos/keys-delegates.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('mobi-vid', 'keys-delegates');

d.run(async () => {
  const [authority, owner, telematicsKey, backupKey, stranger] = await ethers.getSigners();
  const { assert } = d;
  const reg = await (await ethers.getContractFactory('MOBIVIDRegistryV2', authority)).deploy();
  await reg.waitForDeployment();
  const vehicle = ethers.Wallet.createRandom().address;
  await reg.registerVehicleBirth(vehicle, ethers.sha256(ethers.toUtf8Bytes(VINS.tesla)), 'enc:placeholder', ethers.id('cert'), owner.address, '0x');
  const SIG_AUTH = ethers.encodeBytes32String('sigAuth');
  const VERI_KEY = ethers.encodeBytes32String('veriKey');
  const YEAR = 365n * 24n * 3600n;
  d.offchain('setup', 'MOBIVIDRegistryV2.registerVehicleBirth', `vehicle ${vehicle.slice(0, 10)}… owned by ${owner.address.slice(0, 10)}…`);

  assert.equal(reg.interface.hasFunction('validDelegate(address,bytes32,address)'), false);
  d.offchain('no-valid-delegate-view', 'MOBIVIDRegistryV2 (ABI)', 'OBSERVATION: the canonical ERC-1056 validDelegate(identity,type,delegate) view is NOT implemented; delegate validity exists only in logs');
  await d.view('changed-before', 'MOBIVIDRegistryV2.changed', reg.changed(vehicle), 'block of the last change (set by the birth) — the ERC-1056 linked-list head for log replay', (v) => assert.ok(v > 0n));
  await d.reverts('add-delegate-unauthorised', 'MOBIVIDRegistryV2.addDelegate', () => reg.connect(stranger).addDelegate(vehicle, SIG_AUTH, stranger.address, YEAR), 'Only owner can perform this action', 'owner-only');
  const r1 = await d.tx('add-delegate-sigauth', 'MOBIVIDRegistryV2.addDelegate', reg.connect(owner).addDelegate(vehicle, SIG_AUTH, telematicsKey.address, YEAR),
    'MEASURED (addDelegateOrClaim): telematics unit key authorised as sigAuth for 1 year -> DIDDelegateChanged(identity, type, delegate, validTo, previousChange); nothing stored but `changed`');
  const e1 = eventArgs(reg, r1, 'DIDDelegateChanged'); assert.equal(e1.delegate, telematicsKey.address); assert.equal(e1.delegateType, SIG_AUTH);
  const t1 = (await ethers.provider.getBlock(r1.blockNumber)).timestamp;
  assert.equal(e1.validTo, BigInt(t1) + YEAR);
  await d.view('changed-after', 'MOBIVIDRegistryV2.changed', reg.changed(vehicle), 'pointer advanced to this block; previousChange in the event points back to the birth block', (v) => assert.equal(v, BigInt(r1.blockNumber)));
  await d.tx('add-delegate-verikey', 'MOBIVIDRegistryV2.addDelegate', reg.connect(owner).addDelegate(vehicle, VERI_KEY, backupKey.address, 30n * 24n * 3600n), 'second delegate, different type (veriKey), 30 days');
  await d.tx('add-delegate-short', 'MOBIVIDRegistryV2.addDelegate', reg.connect(owner).addDelegate(vehicle, SIG_AUTH, stranger.address, 1n), 'a 1-second delegation: expires on its own (validTo = now+1)');
  await d.reverts('revoke-delegate-unauthorised', 'MOBIVIDRegistryV2.revokeDelegate', () => reg.connect(telematicsKey).revokeDelegate(vehicle, VERI_KEY, backupKey.address), 'Only owner can perform this action', 'a delegate cannot revoke other delegates (no capabilityDelegation)');
  const r2 = await d.tx('revoke-delegate', 'MOBIVIDRegistryV2.revokeDelegate', reg.connect(owner).revokeDelegate(vehicle, VERI_KEY, backupKey.address), 'MEASURED-adjacent: revocation = DIDDelegateChanged with validTo = now (the same event shape; "revoked" is just "expired")');
  const e2 = eventArgs(reg, r2, 'DIDDelegateChanged'); assert.equal(e2.validTo, BigInt((await ethers.provider.getBlock(r2.blockNumber)).timestamp));
  await d.tx('revoke-never-added', 'MOBIVIDRegistryV2.revokeDelegate', reg.connect(owner).revokeDelegate(vehicle, SIG_AUTH, owner.address), 'OBSERVATION: revoking a delegate that was never added succeeds (event-only, no state to check)');

  const now = BigInt((await ethers.provider.getBlock('latest')).timestamp);
  const logs = await reg.queryFilter(reg.filters.DIDDelegateChanged(vehicle), 0, 'latest');
  const latest = new Map();
  for (const l of logs) latest.set(`${l.args.delegateType}:${l.args.delegate}`, l.args.validTo);
  const valid = [...latest.entries()].filter(([, v]) => v > now).map(([k]) => k.split(':')[1]);
  assert.deepEqual(valid, [telematicsKey.address]);
  d.offchain('replay-delegates', 'MOBIVIDRegistryV2.DIDDelegateChanged (logs)', `${logs.length} delegate events; latest validTo per (type, delegate) wins: currently valid = [telematics sigAuth]; backup revoked, 1-second one expired — this replay IS the verifier's "is this key authorised" check`);

  const newPub = ethers.toUtf8Bytes('BASE64PUBKEY-ROTATED-2026-10-04');
  await d.reverts('update-key-unauthorised', 'MOBIVIDRegistryV2.updateVehicleKey', () => reg.connect(stranger).updateVehicleKey(vehicle, newPub), 'Only owner can perform this action', 'owner-only');
  const r3 = await d.tx('update-vehicle-key', 'MOBIVIDRegistryV2.updateVehicleKey', reg.connect(owner).updateVehicleKey(vehicle, newPub), 'key rotation helper: publishes a new did/pub/secp256k1/veriKey/base64 attribute (1 year); the old key attribute is NOT revoked (comment in source: "for simplicity")');
  assert.equal(eventArgs(reg, r3, 'DIDAttributeChanged').name, ethers.id('did/pub/secp256k1/veriKey/base64'));
  await d.view('last-changed', 'MOBIVIDRegistryV2.lastChanged', reg.lastChanged(vehicle), 'view alias of changed()', (v) => assert.equal(v, BigInt(r3.blockNumber)));
  await d.view('nonce', 'MOBIVIDRegistryV2.nonce', reg.nonce(owner.address), 'OBSERVATION: ERC-1056 meta-tx nonce is declared but never incremented (no *Signed functions): always 0', (v) => assert.equal(v, 0n));
  await d.tx('revoke-identity', 'MOBIVIDRegistryV2.revokeIdentity', reg.connect(owner).revokeIdentity(vehicle), 'decommission');
  await d.reverts('add-delegate-after-revoke', 'MOBIVIDRegistryV2.addDelegate', () => reg.connect(owner).addDelegate(vehicle, SIG_AUTH, backupKey.address, YEAR), 'Identity is revoked', 'no new keys for a revoked identity');
  await d.reverts('update-key-after-revoke', 'MOBIVIDRegistryV2.updateVehicleKey', () => reg.connect(owner).updateVehicleKey(vehicle, newPub), 'Identity is revoked', 'no key rotation for a revoked identity');
  await d.tx('revoke-delegate-after-revoke', 'MOBIVIDRegistryV2.revokeDelegate', reg.connect(owner).revokeDelegate(vehicle, SIG_AUTH, telematicsKey.address), 'revocations stay possible after decommissioning (sensible: cleanup)');
});
