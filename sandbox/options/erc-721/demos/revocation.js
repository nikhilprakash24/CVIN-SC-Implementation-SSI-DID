'use strict';
/**
 * ERC-721 — family "Revocation / status" (manifest: implemented, not measured; the comparison
 * measures deactivateVehicle as "revoke"). Shows what deactivation does and does NOT do: the
 * active flag flips, the token is not burned, it remains transferable, there is no reactivation,
 * and a role revocation (revokeRole) is the other revocation primitive.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-721/demos/revocation.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('erc-721', 'revocation');

d.run(async () => {
  const [deployer, vehicleOwner, newOwner, serviceCenter] = await ethers.getSigners();
  const { assert } = d;
  const nft = await (await ethers.getContractFactory('CVINVehicleNFT', deployer)).deploy();
  await nft.waitForDeployment();
  await nft.mintVehicle(vehicleOwner.address, VINS.ford, 'Ford', 'F-150', 2013, 'Black', 'ipfs://f150');
  await nft.grantServiceCenterRole(serviceCenter.address);
  d.offchain('setup', 'CVINVehicleNFT.mintVehicle', 'vehicle 1 minted; service centre role granted');

  await d.view('active-before', 'CVINVehicleNFT.isVehicleActive', nft.isVehicleActive(1), 'status flag true after mint', (v) => assert.equal(v, true));
  await d.reverts('deactivate-unauthorised', 'CVINVehicleNFT.deactivateVehicle', () => nft.connect(vehicleOwner).deactivateVehicle(1), 'AccessControlUnauthorizedAccount', 'the owner cannot revoke its own identity; only DEFAULT_ADMIN_ROLE (not self-sovereign)');
  const r = await d.tx('deactivate', 'CVINVehicleNFT.deactivateVehicle', nft.connect(deployer).deactivateVehicle(1), 'MEASURED as "revoke": admin flips vehicleMetadata.active=false and emits VehicleDeactivated; token NOT burned');
  assert.equal(eventArgs(nft, r, 'VehicleDeactivated').by, deployer.address);
  await d.view('active-after', 'CVINVehicleNFT.isVehicleActive', nft.isVehicleActive(1), 'status flag false', (v) => assert.equal(v, false));
  await d.view('owner-survives', 'CVINVehicleNFT.ownerOf', nft.ownerOf(1), 'ownerOf still resolves: the identity persists, only its status changed', (v) => assert.equal(v, vehicleOwner.address));
  await d.tx('deactivated-still-transferable', 'CVINVehicleNFT.transferFrom', nft.connect(vehicleOwner).transferFrom(vehicleOwner.address, newOwner.address, 1),
    'OBSERVATION: nothing in _update checks `active`; a deactivated (end-of-life) vehicle can still be sold on-chain — the status is advisory, a verifier must read isVehicleActive');
  await d.tx('deactivated-still-serviceable', 'CVINVehicleNFT.addServiceRecord', nft.connect(serviceCenter).addServiceRecord(1, 'ipfs://service/after-eol'), 'OBSERVATION: service records can still be appended after deactivation');
  await d.tx('deactivate-idempotent', 'CVINVehicleNFT.deactivateVehicle', nft.connect(deployer).deactivateVehicle(1), 'second deactivation is accepted (no state guard); there is NO reactivate function');
  await d.reverts('deactivate-nonexistent', 'CVINVehicleNFT.deactivateVehicle', () => nft.connect(deployer).deactivateVehicle(42), 'token does not exist', 'existence check');
  await d.view('active-nonexistent', 'CVINVehicleNFT.isVehicleActive', nft.isVehicleActive(42), 'false for a token that never existed — indistinguishable from "deactivated" without ownerOf', (v) => assert.equal(v, false));

  const SC = await nft.SERVICE_CENTER_ROLE();
  const r2 = await d.tx('revoke-role', 'CVINVehicleNFT.revokeRole', nft.connect(deployer).revokeRole(SC, serviceCenter.address), 'the other revocation primitive: an issuer-side credential (role) is revoked by the admin (RoleRevoked)');
  assert.equal(eventArgs(nft, r2, 'RoleRevoked').account, serviceCenter.address);
  await d.view('has-role-after', 'CVINVehicleNFT.hasRole', nft.hasRole(SC, serviceCenter.address), 'role gone', (v) => assert.equal(v, false));
  await d.reverts('revoked-role-cannot-write', 'CVINVehicleNFT.addServiceRecord', () => nft.connect(serviceCenter).addServiceRecord(1, 'ipfs://x'), 'AccessControlUnauthorizedAccount', 'but records it already wrote stay (no per-record revocation)');
  await d.view('records-survive', 'CVINVehicleNFT.getServiceRecords', nft.getServiceRecords(1), 'earlier records are not invalidated by the role revocation', (v) => assert.equal(v.length, 1));
  d.offchain('did-variants', 'CVIN_NFT_DID_ERC721 / Monolithic', 'asymmetry: the two DID variants have NO revocation at all (no burn, no status flag); a verifier can only check ownerOf');
});
