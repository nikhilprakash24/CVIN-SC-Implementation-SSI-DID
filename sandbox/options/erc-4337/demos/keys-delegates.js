'use strict';
/**
 * ERC-4337 — family "Key / delegate management" (manifest: measured-in-comparison via setGuardian,
 * guardian, recoverOwner). The only "delegate" is the social-recovery guardian: a single address
 * that can replace the signing key at any time (no delay, no quorum, no purpose/validity). This
 * demo shows set / read / replace / clear of the guardian, recovery, and what the guardian
 * can NOT do (sign UserOperations, write attributes).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-4337/demos/keys-delegates.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs } = require('./_lib');

const d = demo('erc-4337', 'keys-delegates');

async function signedOp(ep, acct, signer, callData) {
  const sender = await acct.getAddress();
  const op = { sender, nonce: await ep.nonces(sender), initCode: '0x', callData, accountGasLimits: ethers.ZeroHash, preVerificationGas: 0, gasFees: ethers.ZeroHash, paymasterAndData: '0x', signature: '0x' };
  op.signature = await signer.signMessage(ethers.getBytes(await ep.getUserOpHash(op)));
  return op;
}

d.run(async () => {
  const [bundler, owner, manufacturer, fleetOperator, stranger] = await ethers.getSigners();
  const { assert } = d;
  const ep = await (await ethers.getContractFactory('CVINMinimalEntryPoint', bundler)).deploy();
  await ep.waitForDeployment();
  const acct = await (await ethers.getContractFactory('CVINVehicleAccount', bundler)).deploy(await ep.getAddress(), owner.address);
  await acct.waitForDeployment();
  d.offchain('setup', 'CVINVehicleAccount.constructor', 'account with `owner` as signing key, no guardian');

  await d.view('guardian-none', 'CVINVehicleAccount.guardian', acct.guardian(), 'MEASURED (view): zero = no recovery delegate', (v) => assert.equal(v, ethers.ZeroAddress));
  await d.reverts('set-guardian-unauthorised', 'CVINVehicleAccount.setGuardian', () => acct.connect(stranger).setGuardian(stranger.address), 'not owner or entryPoint', 'only the owner key (or a UserOp it signed) designates a guardian');
  const r1 = await d.tx('set-guardian', 'CVINVehicleAccount.setGuardian', acct.connect(owner).setGuardian(manufacturer.address), 'MEASURED (addDelegateOrClaim): manufacturer becomes the recovery delegate -> GuardianChanged(0, manufacturer)');
  const e1 = eventArgs(acct, r1, 'GuardianChanged'); assert.equal(e1.previousGuardian, ethers.ZeroAddress); assert.equal(e1.newGuardian, manufacturer.address);
  await d.view('guardian-set', 'CVINVehicleAccount.guardian', acct.guardian(), 'read back', (v) => assert.equal(v, manufacturer.address));
  await d.tx('replace-guardian', 'CVINVehicleAccount.setGuardian', acct.connect(owner).setGuardian(fleetOperator.address), 'single slot: replacing the guardian is the same call (no list, no quorum)');
  await d.reverts('old-guardian-powerless', 'CVINVehicleAccount.recoverOwner', () => acct.connect(manufacturer).recoverOwner(manufacturer.address), 'not guardian', 'the replaced guardian cannot recover');

  const op = await signedOp(ep, acct, owner, acct.interface.encodeFunctionData('setGuardian', [manufacturer.address]));
  await d.tx('set-guardian-via-userop', 'CVINMinimalEntryPoint.handleOp -> setGuardian', ep.connect(bundler).handleOp(op), 'guardian designation can also ride a UserOperation (owner signs, bundler pays)');
  await d.view('guardian-via-userop', 'CVINVehicleAccount.guardian', acct.guardian(), 'manufacturer again', (v) => assert.equal(v, manufacturer.address));

  await d.reverts('guardian-cannot-write-attributes', 'CVINVehicleAccount.setAttribute', () => acct.connect(manufacturer).setAttribute(ethers.id('cvin/vehicle/vin'), '0x01'), 'not owner or entryPoint', 'the guardian is NOT a signing delegate: it cannot act for the vehicle, only replace its key');
  const badOp = await signedOp(ep, acct, manufacturer, acct.interface.encodeFunctionData('setAttribute', [ethers.id('cvin/vehicle/vin'), '0x01']));
  await d.reverts('guardian-cannot-sign-userops', 'CVINMinimalEntryPoint.handleOp', () => ep.connect(bundler).handleOp(badOp), 'signature validation failed', 'validateUserOp recovers the signer and compares with owner only — guardian signatures are rejected');
  await d.reverts('guardian-cannot-change-guardian', 'CVINVehicleAccount.setGuardian', () => acct.connect(manufacturer).setGuardian(manufacturer.address), 'not owner or entryPoint', 'no guardian self-perpetuation');

  const r2 = await d.tx('recover-owner', 'CVINVehicleAccount.recoverOwner', acct.connect(manufacturer).recoverOwner(stranger.address), 'MEASURED (recoverOwner): instant key replacement by the guardian -> OwnerRecovered; no timelock, no challenge window');
  assert.equal(eventArgs(acct, r2, 'OwnerRecovered').newOwner, stranger.address);
  await d.view('owner-after-recovery', 'CVINVehicleAccount.owner', acct.owner(), 'new key installed', (v) => assert.equal(v, stranger.address));
  await d.view('guardian-persists', 'CVINVehicleAccount.guardian', acct.guardian(), 'OBSERVATION: recovery does not clear the guardian; it can recover again at will (a guardian is effectively a super-owner)', (v) => assert.equal(v, manufacturer.address));
  await d.reverts('old-owner-locked-out', 'CVINVehicleAccount.setGuardian', () => acct.connect(owner).setGuardian(owner.address), 'not owner or entryPoint', 'the recovered-from key is dead');

  const r3 = await d.tx('clear-guardian', 'CVINVehicleAccount.setGuardian', acct.connect(stranger).setGuardian(ethers.ZeroAddress), 'MEASURED (revoke): the new owner revokes the recovery delegate (setGuardian(0), storage refund) -> GuardianChanged(manufacturer, 0)');
  assert.equal(eventArgs(acct, r3, 'GuardianChanged').newGuardian, ethers.ZeroAddress);
  await d.reverts('recover-after-clear', 'CVINVehicleAccount.recoverOwner', () => acct.connect(manufacturer).recoverOwner(manufacturer.address), 'not guardian', 'recovery disabled');
  d.offchain('no-key-model', 'CVINVehicleAccount', 'asymmetry: no key list, purposes, validity windows or ERC-1056-style delegates — one owner key + one guardian; a DID document can only list those two verification methods');
});
