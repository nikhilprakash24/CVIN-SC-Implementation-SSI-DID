'use strict';
/**
 * ERC-1155 — family "Authorisation / roles" (manifest: implemented, not measured). The OZ
 * AccessControl surface: DEFAULT_ADMIN_ROLE / ISSUER_ROLE, getRoleAdmin, grantRole, hasRole,
 * revokeRole, renounceRole, and the single gate (ISSUER_ROLE) that every write and every
 * non-mint/burn transfer passes through — including issuerTransferIdentity (the only way to move
 * an identity that still holds credentials since the D8 fix).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1155/demos/authorisation-roles.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('erc-1155', 'authorisation-roles');

d.run(async () => {
  const [admin, vehicleA, vehicleB, dmv, insurer] = await ethers.getSigners();
  const { assert } = d;
  const c = await (await ethers.getContractFactory('CVINVehicleCredential1155', admin)).deploy();
  await c.waitForDeployment();
  const [ADMIN, ISSUER] = await Promise.all([c.DEFAULT_ADMIN_ROLE(), c.ISSUER_ROLE()]);
  await d.view('role-constants', 'CVINVehicleCredential1155.DEFAULT_ADMIN_ROLE+ISSUER_ROLE', Promise.resolve([ADMIN, ISSUER]), 'only two roles exist: admin and ONE issuer role for all credential types', (v) => { assert.equal(v[0], ethers.ZeroHash); assert.equal(v[1], ethers.id('ISSUER_ROLE')); });
  await d.view('deployer-roles', 'CVINVehicleCredential1155.hasRole', Promise.all([c.hasRole(ADMIN, admin.address), c.hasRole(ISSUER, admin.address)]), 'constructor grants both to the deployer', (v) => assert.deepEqual(v, [true, true]));
  await d.view('get-role-admin', 'CVINVehicleCredential1155.getRoleAdmin', c.getRoleAdmin(ISSUER), 'ISSUER_ROLE is administered by DEFAULT_ADMIN_ROLE', (v) => assert.equal(v, ADMIN));

  const r1 = await d.tx('grant-dmv', 'CVINVehicleCredential1155.grantRole', c.connect(admin).grantRole(ISSUER, dmv.address), 'admin grants the DMV the issuer role -> RoleGranted');
  assert.equal(eventArgs(c, r1, 'RoleGranted').account, dmv.address);
  await d.tx('grant-insurer', 'CVINVehicleCredential1155.grantRole', c.connect(admin).grantRole(ISSUER, insurer.address), 'and the insurer');
  await d.reverts('grant-unauthorised', 'CVINVehicleCredential1155.grantRole', () => c.connect(dmv).grantRole(ISSUER, vehicleA.address), 'AccessControlUnauthorizedAccount', 'issuers cannot mint new issuers');
  await d.tx('dmv-registers', 'CVINVehicleCredential1155.registerVehicle', c.connect(dmv).registerVehicle(vehicleA.address, VINS.acura), 'gate 1: registerVehicle is onlyRole(ISSUER_ROLE)');
  await d.tx('insurer-issues', 'CVINVehicleCredential1155.issueCredential', c.connect(insurer).issueCredential(vehicleA.address, 4, 1), 'gate 2: issueCredential');
  await d.tx('insurer-sets-uri', 'CVINVehicleCredential1155.setTokenURI', c.connect(insurer).setTokenURI(4, 'ipfs://insurer/policy-template.json'), 'gate 3: setTokenURI');
  await d.tx('dmv-moves-identity', 'CVINVehicleCredential1155.issuerTransferIdentity', c.connect(dmv).issuerTransferIdentity(vehicleA.address, vehicleB.address), 'gate 4: issuerTransferIdentity (the DMV re-binds the identity — BIRTH_CERT plus the insurer\'s INSURANCE_CERT — to a new owner address; since D8 the BIRTH_CERT alone cannot leave while a credential is held)');
  await d.tx('dmv-revokes-insurance', 'CVINVehicleCredential1155.revokeCredential', c.connect(dmv).revokeCredential(vehicleB.address, 4, 1), 'gate 5: revokeCredential — OBSERVATION: the DMV can revoke what the insurer issued (single flat role, documented not changed by the D8 fix); the credential now lives at B');
  await d.view('vehicle-cannot-act', 'CVINVehicleCredential1155.hasRole', c.hasRole(ISSUER, vehicleB.address), 'the vehicle address itself holds no role: it can only receive', (v) => assert.equal(v, false));

  await d.reverts('renounce-bad-confirmation', 'CVINVehicleCredential1155.renounceRole', () => c.connect(insurer).renounceRole(ISSUER, admin.address), 'AccessControlBadConfirmation', 'renounceRole requires callerConfirmation == msg.sender');
  const r2 = await d.tx('insurer-renounces', 'CVINVehicleCredential1155.renounceRole', c.connect(insurer).renounceRole(ISSUER, insurer.address), 'self-revocation -> RoleRevoked');
  assert.equal(eventArgs(c, r2, 'RoleRevoked').account, insurer.address);
  const r3 = await d.tx('revoke-dmv', 'CVINVehicleCredential1155.revokeRole', c.connect(admin).revokeRole(ISSUER, dmv.address), 'admin revokes the DMV -> RoleRevoked');
  assert.equal(eventArgs(c, r3, 'RoleRevoked').account, dmv.address);
  await d.reverts('revoked-dmv-blocked', 'CVINVehicleCredential1155.registerVehicle', () => c.connect(dmv).registerVehicle(dmv.address, VINS.fiat), 'AccessControlUnauthorizedAccount', 'revoked issuer locked out');
  await d.tx('admin-renounces-admin', 'CVINVehicleCredential1155.renounceRole', c.connect(admin).renounceRole(ADMIN, admin.address), 'OBSERVATION: the sole admin can renounce; the issuer set is then frozen forever (no guard)');
  await d.reverts('grant-after-admin-gone', 'CVINVehicleCredential1155.grantRole', () => c.connect(admin).grantRole(ISSUER, insurer.address), 'AccessControlUnauthorizedAccount', 'governance frozen');
  await d.view('admin-still-issuer', 'CVINVehicleCredential1155.hasRole', c.hasRole(ISSUER, admin.address), 'the deployer keeps ISSUER_ROLE', (v) => assert.equal(v, true));
});
