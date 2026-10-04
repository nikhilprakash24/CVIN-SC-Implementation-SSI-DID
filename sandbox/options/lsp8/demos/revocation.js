'use strict';
/**
 * LSP8 — family "Revocation / status" (manifest: measured-in-comparison via revokeVehicle).
 * revokeVehicle burns the token (Transfer to 0 + VehicleRevoked); callable by the issuing
 * authority OR the token owner. Status afterwards = exists()==false. The per-token data store is
 * NOT cleared, and the same VIN can be minted again, inheriting the stale data.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/lsp8/demos/revocation.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('lsp8', 'revocation');

d.run(async () => {
  const [authority, vehicleOwner, stranger, buyer] = await ethers.getSigners();
  const { assert } = d;
  const c = await (await ethers.getContractFactory('CVINVehicleLSP8', authority)).deploy('CVIN Vehicle Identity LSP8', 'CVIN-LSP8');
  await c.waitForDeployment();
  await c.mintVehicle(vehicleOwner.address, VINS.renault);
  await c.mintVehicle(vehicleOwner.address, VINS.fiat);
  const t1 = await c.tokenIdForVIN(VINS.renault);
  const t2 = await c.tokenIdForVIN(VINS.fiat);
  const [K_VIN, K_INSP] = await Promise.all([c.DATA_KEY_VIN(), c.DATA_KEY_INSPECTION()]);
  await c.setDataForTokenId(t1, K_INSP, ethers.toUtf8Bytes('PASS 2026-10-04'));
  d.offchain('setup', 'CVINVehicleLSP8.mintVehicle+setDataForTokenId', 'two vehicles; vehicle 1 carries an inspection attestation');

  await d.reverts('revoke-unauthorised', 'CVINVehicleLSP8.revokeVehicle', () => c.connect(stranger).revokeVehicle(t1, '0x'), 'caller is not authority nor token owner', 'third parties cannot revoke');
  await d.reverts('revoke-nonexistent', 'CVINVehicleLSP8.revokeVehicle', () => c.connect(authority).revokeVehicle(ethers.id('nope'), '0x'), 'tokenId does not exist', 'existence check');
  const r1 = await d.tx('revoke-by-authority', 'CVINVehicleLSP8.revokeVehicle', c.connect(authority).revokeVehicle(t1, ethers.toUtf8Bytes('total loss 2026-10-04')),
    'MEASURED (revoke): authority burns vehicle 1 -> Transfer(authority, owner, 0, tokenId, force=true, data) + VehicleRevoked(tokenId, previousOwner)');
  const tr = eventArgs(c, r1, 'Transfer'); assert.equal(tr.to, ethers.ZeroAddress); assert.equal(ethers.toUtf8String(tr.data), 'total loss 2026-10-04');
  assert.equal(eventArgs(c, r1, 'VehicleRevoked').previousOwner, vehicleOwner.address);
  await d.view('exists-after', 'CVINVehicleLSP8.exists', c.exists(t1), 'status = does not exist (no "revoked" flag, no tombstone)', (v) => assert.equal(v, false));
  await d.reverts('owner-of-after', 'CVINVehicleLSP8.tokenOwnerOf', () => c.tokenOwnerOf(t1), 'tokenId does not exist', 'revoked and never-minted are indistinguishable from state');
  await d.view('supply-and-balance', 'CVINVehicleLSP8.totalSupply+balanceOf+tokenIdsOf', Promise.all([c.totalSupply(), c.balanceOf(vehicleOwner.address), c.tokenIdsOf(vehicleOwner.address)]), 'supply 1, balance 1, only vehicle 2 enumerated', (v) => { assert.equal(v[0], 1n); assert.equal(v[1], 1n); assert.deepEqual([...v[2]], [t2]); });
  await d.view('data-not-cleared', 'CVINVehicleLSP8.getDataForTokenId', Promise.all([c.getDataForTokenId(t1, K_VIN), c.getDataForTokenId(t1, K_INSP)]).then((v) => v.map(ethers.toUtf8String)),
    'OBSERVATION: the burned token\'s data store is intact (VIN and inspection still readable by tokenId)', (v) => assert.deepEqual(v, [VINS.renault, 'PASS 2026-10-04']));
  await d.reverts('write-after-revoke', 'CVINVehicleLSP8.setDataForTokenId', () => c.connect(authority).setDataForTokenId(t1, K_INSP, '0x'), 'tokenId does not exist', 'but it can no longer be cleared (exists() gate) — the stale data is frozen');
  await d.tx('remint-same-vin', 'CVINVehicleLSP8.mintVehicle', c.connect(authority).mintVehicle(buyer.address, VINS.renault),
    'POTENTIAL DEFECT: the same VIN can be minted again after revocation (same tokenId) and INHERITS the old inspection attestation');
  await d.view('inherited-attestation', 'CVINVehicleLSP8.getDataForTokenId', c.getDataForTokenId(t1, K_INSP).then(ethers.toUtf8String), 'the "new" vehicle 1 shows PASS 2026-10-04 that it never earned', (v) => assert.equal(v, 'PASS 2026-10-04'));
  await d.tx('revoke-by-owner', 'CVINVehicleLSP8.revokeVehicle', c.connect(vehicleOwner).revokeVehicle(t2, '0x'), 'self-revocation: the token owner may burn its own identity (sovereign exit) — the authority is not needed');
  await d.view('supply-0', 'CVINVehicleLSP8.totalSupply', c.totalSupply(), 'vehicle 2 gone; only the re-minted vehicle 1 remains', (v) => assert.equal(v, 1n));
  await d.tx('revoke-again-by-authority', 'CVINVehicleLSP8.revokeVehicle', c.connect(authority).revokeVehicle(t1, '0x'), 'authority revokes the re-minted token');
  await d.reverts('revoke-twice', 'CVINVehicleLSP8.revokeVehicle', () => c.connect(authority).revokeVehicle(t1, '0x'), 'tokenId does not exist', 'no double burn');
  d.offchain('no-granular-revocation', 'CVINVehicleLSP8', 'asymmetry: revocation is all-or-nothing (burn); per-attribute "revocation" is a data clear (see attributes/claims demos); there is no suspended state');
});
