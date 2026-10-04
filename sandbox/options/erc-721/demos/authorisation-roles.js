'use strict';
/**
 * ERC-721 — family "Authorisation / roles" (manifest: implemented, not measured; the comparison
 * excludes role grants as setup). The full OZ AccessControl surface on CVINVehicleNFT: the four
 * role constants, hasRole / getRoleAdmin, the three convenience granters, raw grantRole,
 * revokeRole, renounceRole (with the self-confirmation check) and the gates they enforce.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-721/demos/authorisation-roles.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('erc-721', 'authorisation-roles');

d.run(async () => {
  const [deployer, vehicleOwner, manufacturer2, inspector, serviceCenter] = await ethers.getSigners();
  const { assert } = d;
  const nft = await (await ethers.getContractFactory('CVINVehicleNFT', deployer)).deploy();
  await nft.waitForDeployment();
  d.offchain('setup', 'CVINVehicleNFT.constructor', 'constructor grants DEFAULT_ADMIN_ROLE and MANUFACTURER_ROLE to the deployer');

  const [ADMIN, MANU, INSP, SC] = await Promise.all([nft.DEFAULT_ADMIN_ROLE(), nft.MANUFACTURER_ROLE(), nft.INSPECTOR_ROLE(), nft.SERVICE_CENTER_ROLE()]);
  await d.view('role-constants', 'CVINVehicleNFT.DEFAULT_ADMIN_ROLE/MANUFACTURER_ROLE/INSPECTOR_ROLE/SERVICE_CENTER_ROLE', Promise.resolve([ADMIN, MANU, INSP, SC]),
    'role ids: 0x00 for admin, keccak256("<NAME>_ROLE") for the three business roles',
    (v) => { assert.equal(v[0], ethers.ZeroHash); assert.equal(v[1], ethers.id('MANUFACTURER_ROLE')); assert.equal(v[2], ethers.id('INSPECTOR_ROLE')); assert.equal(v[3], ethers.id('SERVICE_CENTER_ROLE')); });
  await d.view('has-role-admin', 'CVINVehicleNFT.hasRole', nft.hasRole(ADMIN, deployer.address), 'deployer is admin', (v) => assert.equal(v, true));
  await d.view('has-role-manufacturer', 'CVINVehicleNFT.hasRole', nft.hasRole(MANU, deployer.address), 'deployer is also a manufacturer', (v) => assert.equal(v, true));
  await d.view('get-role-admin', 'CVINVehicleNFT.getRoleAdmin', Promise.all([nft.getRoleAdmin(MANU), nft.getRoleAdmin(INSP), nft.getRoleAdmin(SC)]), 'every business role is administered by DEFAULT_ADMIN_ROLE (flat hierarchy, never changed -> RoleAdminChanged never fires)', (v) => assert.deepEqual(v, [ADMIN, ADMIN, ADMIN]));

  const r1 = await d.tx('grant-manufacturer', 'CVINVehicleNFT.grantManufacturerRole', nft.connect(deployer).grantManufacturerRole(manufacturer2.address), 'convenience granter (admin-only) -> RoleGranted');
  assert.equal(eventArgs(nft, r1, 'RoleGranted').role, MANU);
  await d.tx('grant-inspector', 'CVINVehicleNFT.grantInspectorRole', nft.connect(deployer).grantInspectorRole(inspector.address), 'convenience granter for INSPECTOR_ROLE');
  await d.tx('grant-service-center', 'CVINVehicleNFT.grantServiceCenterRole', nft.connect(deployer).grantServiceCenterRole(serviceCenter.address), 'convenience granter for SERVICE_CENTER_ROLE');
  await d.tx('grant-role-raw', 'CVINVehicleNFT.grantRole', nft.connect(deployer).grantRole(SC, inspector.address), 'raw AccessControl.grantRole (same effect as the convenience function; an account may hold several roles)');
  await d.view('has-roles-after', 'CVINVehicleNFT.hasRole', Promise.all([nft.hasRole(MANU, manufacturer2.address), nft.hasRole(INSP, inspector.address), nft.hasRole(SC, serviceCenter.address), nft.hasRole(SC, inspector.address)]), 'all four grants visible', (v) => assert.deepEqual(v, [true, true, true, true]));
  await d.reverts('grant-unauthorised', 'CVINVehicleNFT.grantManufacturerRole', () => nft.connect(manufacturer2).grantManufacturerRole(vehicleOwner.address), 'AccessControlUnauthorizedAccount', 'a manufacturer cannot grant roles; only the admin');
  await d.tx('new-manufacturer-mints', 'CVINVehicleNFT.mintVehicle', nft.connect(manufacturer2).mintVehicle(vehicleOwner.address, VINS.fiat, 'Fiat', '500', 2015, 'Red', 'ipfs://500'), 'the gate works: freshly granted manufacturer creates an identity');
  await d.tx('service-center-writes', 'CVINVehicleNFT.addServiceRecord', nft.connect(serviceCenter).addServiceRecord(1, 'ipfs://svc'), 'SERVICE_CENTER_ROLE gate on addServiceRecord');
  d.offchain('inspector-role-gates-nothing', 'CVINVehicleNFT.INSPECTOR_ROLE', 'OBSERVATION: INSPECTOR_ROLE is declared and grantable, but no function in the contract is gated by it (dead role: an inspection cannot be written on-chain by an inspector)');

  await d.reverts('renounce-bad-confirmation', 'CVINVehicleNFT.renounceRole', () => nft.connect(inspector).renounceRole(INSP, deployer.address), 'AccessControlBadConfirmation', 'renounceRole(role, callerConfirmation) requires callerConfirmation == msg.sender');
  const r2 = await d.tx('renounce-role', 'CVINVehicleNFT.renounceRole', nft.connect(inspector).renounceRole(INSP, inspector.address), 'the holder gives a role up itself (self-revocation) -> RoleRevoked');
  assert.equal(eventArgs(nft, r2, 'RoleRevoked').sender, inspector.address);
  const r3 = await d.tx('revoke-role', 'CVINVehicleNFT.revokeRole', nft.connect(deployer).revokeRole(MANU, manufacturer2.address), 'admin revokes a role -> RoleRevoked');
  assert.equal(eventArgs(nft, r3, 'RoleRevoked').account, manufacturer2.address);
  await d.reverts('revoked-manufacturer-mint', 'CVINVehicleNFT.mintVehicle', () => nft.connect(manufacturer2).mintVehicle(vehicleOwner.address, VINS.renault, 'Renault', 'Clio', 2009, 'Yellow', 'ipfs://clio'), 'AccessControlUnauthorizedAccount', 'revoked manufacturer can no longer create identities (its past mints stand)');
  await d.reverts('revoke-unauthorised', 'CVINVehicleNFT.revokeRole', () => nft.connect(serviceCenter).revokeRole(SC, inspector.address), 'AccessControlUnauthorizedAccount', 'only the role admin revokes');
  await d.tx('admin-renounce', 'CVINVehicleNFT.renounceRole', nft.connect(deployer).renounceRole(ADMIN, deployer.address), 'OBSERVATION: the sole admin can renounce; afterwards nobody can grant/revoke roles or deactivate vehicles (no guard against locking the collection)');
  await d.reverts('grant-after-admin-renounce', 'CVINVehicleNFT.grantInspectorRole', () => nft.connect(deployer).grantInspectorRole(vehicleOwner.address), 'AccessControlUnauthorizedAccount', 'governance is now frozen');
  await d.view('manufacturer-survives', 'CVINVehicleNFT.hasRole', nft.hasRole(MANU, deployer.address), 'deployer keeps MANUFACTURER_ROLE (roles are independent)', (v) => assert.equal(v, true));
});
