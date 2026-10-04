'use strict';
/**
 * MOBI VID — family "Authorisation / roles" (manifest: implemented, not measured; the comparison
 * excludes issuer/manufacturer authorisation as setup). Three authorisation layers: the registry
 * authority (single address, transferable), authorised manufacturers (boolean set, VID I births)
 * and issuers with one of 8 roles (VID II events). Exercises every grant/revoke/view and guard,
 * authority hand-over and role re-assignment.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/mobi-vid/demos/authorisation-roles.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('mobi-vid', 'authorisation-roles');

d.run(async () => {
  const [authority, newAuthority, oem, dealer, owner, stranger] = await ethers.getSigners();
  const { assert } = d;
  const reg = await (await ethers.getContractFactory('MOBIVIDRegistryV2', authority)).deploy();
  await reg.waitForDeployment();
  d.offchain('setup', 'MOBIVIDRegistryV2.constructor', 'fresh registry');

  await d.view('registry-authority', 'MOBIVIDRegistryV2.registryAuthority', reg.registryAuthority(), 'root of trust = deployer', (v) => assert.equal(v, authority.address));
  await d.view('authorized-manufacturers-deployer', 'MOBIVIDRegistryV2.authorizedManufacturers', reg.authorizedManufacturers(authority.address), 'constructor auto-authorises the deployer as manufacturer "for testing"', (v) => assert.equal(v, true));
  await d.reverts('authorise-manufacturer-unauthorised', 'MOBIVIDRegistryV2.authorizeManufacturer', () => reg.connect(stranger).authorizeManufacturer(oem.address), 'Only registry authority', 'guard');
  await d.reverts('authorise-manufacturer-zero', 'MOBIVIDRegistryV2.authorizeManufacturer', () => reg.connect(authority).authorizeManufacturer(ethers.ZeroAddress), 'Invalid manufacturer address', 'guard');
  const r1 = await d.tx('authorise-manufacturer', 'MOBIVIDRegistryV2.authorizeManufacturer', reg.connect(authority).authorizeManufacturer(oem.address), 'OEM authorised -> ManufacturerAuthorized(manufacturer, timestamp)');
  assert.equal(eventArgs(reg, r1, 'ManufacturerAuthorized').manufacturer, oem.address);
  await d.reverts('authorise-manufacturer-twice', 'MOBIVIDRegistryV2.authorizeManufacturer', () => reg.connect(authority).authorizeManufacturer(oem.address), 'Manufacturer already authorized', 'idempotence guard');
  await d.view('authorized-manufacturers', 'MOBIVIDRegistryV2.authorizedManufacturers', reg.authorizedManufacturers(oem.address), 'boolean set', (v) => assert.equal(v, true));
  await d.tx('oem-registers-birth', 'MOBIVIDRegistryV2.registerVehicleBirth', reg.connect(oem).registerVehicleBirth(ethers.Wallet.createRandom().address, ethers.sha256(ethers.toUtf8Bytes(VINS.acura)), 'enc', ethers.id('c'), owner.address, '0x'), 'gate: births are manufacturer-only');
  const r2 = await d.tx('revoke-manufacturer', 'MOBIVIDRegistryV2.revokeManufacturerAuthorization', reg.connect(authority).revokeManufacturerAuthorization(oem.address), '-> ManufacturerAuthorizationRevoked');
  assert.equal(eventArgs(reg, r2, 'ManufacturerAuthorizationRevoked').manufacturer, oem.address);
  await d.reverts('revoked-oem-blocked', 'MOBIVIDRegistryV2.registerVehicleBirth', () => reg.connect(oem).registerVehicleBirth(ethers.Wallet.createRandom().address, ethers.id('v'), 'enc', ethers.id('c'), owner.address, '0x'), 'Only authorized manufacturers', 'locked out');

  const r3 = await d.tx('authorise-issuer', 'MOBIVIDRegistryV2.authorizeIssuer', reg.connect(authority).authorizeIssuer(dealer.address, 2), 'dealer gets role DEALER (2) -> IssuerAuthorized(issuer, role, timestamp)');
  assert.equal(Number(eventArgs(reg, r3, 'IssuerAuthorized').role), 2);
  await d.view('authorized-issuers', 'MOBIVIDRegistryV2.authorizedIssuers', reg.authorizedIssuers(dealer.address), 'address -> role', (v) => assert.equal(Number(v), 2));
  await d.view('is-authorized-issuer', 'MOBIVIDRegistryV2.isAuthorizedIssuer', Promise.all([reg.isAuthorizedIssuer(dealer.address, 1), reg.isAuthorizedIssuer(dealer.address, 3)]), 'DEALER may issue REPAIR (1) but not RECALL (3)', (v) => assert.deepEqual(v, [true, false]));
  await d.view('allowed-issuers', 'MOBIVIDRegistryV2.allowedIssuers', Promise.all([reg.allowedIssuers(3, 1), reg.allowedIssuers(3, 2)]), 'the static role matrix: RECALL x MANUFACTURER yes, RECALL x DEALER no (no setter: the matrix is immutable)', (v) => assert.deepEqual(v, [true, false]));
  assert.equal(reg.interface.fragments.filter((f) => f.type === 'function' && /setAllowed|allowIssuer/i.test(f.name)).length, 0);
  d.offchain('matrix-immutable', 'MOBIVIDRegistryV2 (ABI)', 'no function changes allowedIssuers after the constructor: adding an event type or a role needs a new deployment');
  await d.tx('reassign-role', 'MOBIVIDRegistryV2.authorizeIssuer', reg.connect(authority).authorizeIssuer(dealer.address, 3), 'OBSERVATION: re-authorising an address with another role silently overwrites (one role per address; no event for the role it lost)');
  await d.view('role-overwritten', 'MOBIVIDRegistryV2.authorizedIssuers', reg.authorizedIssuers(dealer.address), 'now SERVICE_CENTER (3)', (v) => assert.equal(Number(v), 3));
  await d.reverts('authorise-issuer-zero', 'MOBIVIDRegistryV2.authorizeIssuer', () => reg.connect(authority).authorizeIssuer(ethers.ZeroAddress, 2), 'Invalid issuer address', 'guard');
  await d.reverts('authorise-issuer-bad-enum', 'MOBIVIDRegistryV2.authorizeIssuer', () => reg.connect(authority).authorizeIssuer(dealer.address, 9), 'revert', 'enum out of range: Solidity panics on conversion (role 9 does not exist)');
  await d.tx('revoke-issuer', 'MOBIVIDRegistryV2.revokeIssuerAuthorization', reg.connect(authority).revokeIssuerAuthorization(dealer.address), '-> IssuerAuthorizationRevoked; role NONE');
  await d.reverts('revoke-issuer-unauthorised', 'MOBIVIDRegistryV2.revokeIssuerAuthorization', () => reg.connect(stranger).revokeIssuerAuthorization(dealer.address), 'Only registry authority', 'guard');

  await d.reverts('transfer-authority-unauthorised', 'MOBIVIDRegistryV2.transferRegistryAuthority', () => reg.connect(stranger).transferRegistryAuthority(stranger.address), 'Only registry authority', 'guard');
  await d.reverts('transfer-authority-zero', 'MOBIVIDRegistryV2.transferRegistryAuthority', () => reg.connect(authority).transferRegistryAuthority(ethers.ZeroAddress), 'Invalid authority address', 'guard');
  await d.tx('transfer-authority', 'MOBIVIDRegistryV2.transferRegistryAuthority', reg.connect(authority).transferRegistryAuthority(newAuthority.address), 'root of trust handed to e.g. a DAO/government; OBSERVATION: no event is emitted for this change');
  await d.view('registry-authority-new', 'MOBIVIDRegistryV2.registryAuthority', reg.registryAuthority(), 'new authority', (v) => assert.equal(v, newAuthority.address));
  await d.reverts('old-authority-powerless', 'MOBIVIDRegistryV2.authorizeIssuer', () => reg.connect(authority).authorizeIssuer(dealer.address, 2), 'Only registry authority', 'old authority locked out');
  await d.tx('new-authority-acts', 'MOBIVIDRegistryV2.authorizeIssuer', reg.connect(newAuthority).authorizeIssuer(dealer.address, 2), 'new authority appoints issuers');
  await d.view('old-authority-still-manufacturer', 'MOBIVIDRegistryV2.authorizedManufacturers', reg.authorizedManufacturers(authority.address), 'OBSERVATION: the old authority keeps its manufacturer status (the two layers are independent)', (v) => assert.equal(v, true));
});
