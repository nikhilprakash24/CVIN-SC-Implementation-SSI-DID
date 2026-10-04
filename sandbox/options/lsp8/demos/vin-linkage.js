'use strict';
/**
 * LSP8 — family "VIN linkage" (manifest: implemented via DATA_KEY_VIN and tokenIdForVIN). The VIN
 * is linked twice: structurally (tokenId = keccak256(VIN), computable by anyone, pure) and as
 * plain text under DATA_KEY_VIN in the token's data store (written at mint, but overwritable by
 * the authority like any other key). Shows both links, the D13 case-insensitivity (the VIN is
 * upper-cased before hashing, so a lower-cased twin cannot be minted), and that the two links
 * can be made to disagree.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/lsp8/demos/vin-linkage.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('lsp8', 'vin-linkage');

d.run(async () => {
  const [authority, vehicleOwner] = await ethers.getSigners();
  const { assert } = d;
  const c = await (await ethers.getContractFactory('CVINVehicleLSP8', authority)).deploy('CVIN Vehicle Identity LSP8', 'CVIN-LSP8');
  await c.waitForDeployment();
  const K_VIN = await d.view('data-key-vin', 'CVINVehicleLSP8.DATA_KEY_VIN', c.DATA_KEY_VIN(), 'well-known key keccak256("CVIN_VIN")', (v) => assert.equal(v, ethers.id('CVIN_VIN')));
  const expected = ethers.keccak256(ethers.toUtf8Bytes(VINS.tesla));
  const t = await d.view('token-id-for-vin', 'CVINVehicleLSP8.tokenIdForVIN', c.tokenIdForVIN(VINS.tesla), 'structural link: tokenId = keccak256(bytes(normalised VIN)), a pure function — any verifier can derive the identifier from the VIN without a lookup table (an off-chain verifier must upper-case before hashing, as the contract does since D13)', (v) => assert.equal(v, expected));
  const r = await d.tx('mint', 'CVINVehicleLSP8.mintVehicle', c.mintVehicle(vehicleOwner.address, VINS.tesla), 'mint stores the plain-text VIN under DATA_KEY_VIN (second link)');
  assert.equal(eventArgs(c, r, 'VehicleMinted').vin, VINS.tesla);
  d.offchain('vin-in-event', 'CVINVehicleLSP8.VehicleMinted', 'the plain VIN is also in the VehicleMinted log (and in TokenIdDataChanged): no privacy');
  await d.view('vin-from-store', 'CVINVehicleLSP8.getDataForTokenId', c.getDataForTokenId(t, K_VIN).then(ethers.toUtf8String), 'tokenId -> VIN (reverse direction)', (v) => assert.equal(v, VINS.tesla));
  await d.view('exists-by-vin', 'CVINVehicleLSP8.exists', c.exists(await c.tokenIdForVIN(VINS.tesla)), 'VIN -> exists? without storing a VIN index', (v) => assert.equal(v, true));
  await d.view('unknown-vin', 'CVINVehicleLSP8.exists', c.exists(await c.tokenIdForVIN(VINS.volvo)), 'unknown VIN -> false', (v) => assert.equal(v, false));
  await d.view('case-sensitive', 'CVINVehicleLSP8.tokenIdForVIN', c.tokenIdForVIN(VINS.tesla.toLowerCase()), 'FIXED (D13): tokenIdForVIN upper-cases before hashing, so the lower-cased VIN derives the SAME tokenId (formerly a different one)', (v) => assert.equal(v, t));
  await d.reverts('mint-lowercase-twin', 'CVINVehicleLSP8.mintVehicle', () => c.mintVehicle(vehicleOwner.address, VINS.tesla.toLowerCase()), 'tokenId already minted', 'FIXED (D13): the same physical VIN in lower case collides with the minted tokenId and cannot mint a second identity');
  await d.reverts('invalid-char-vin', 'CVINVehicleLSP8.tokenIdForVIN', () => c.tokenIdForVIN('5YJ3E1EA7KF31700O'), 'invalid VIN character', 'FIXED (D13): even the pure derivation rejects an ISO 3779-invalid VIN (I/O/Q), so no tokenId exists for it');
  await d.tx('overwrite-vin-key', 'CVINVehicleLSP8.setDataForTokenId', c.setDataForTokenId(t, K_VIN, ethers.toUtf8Bytes(VINS.honda)), 'POTENTIAL DEFECT: DATA_KEY_VIN is an ordinary key — the authority can overwrite it, so the stored VIN no longer hashes to the tokenId');
  await d.view('links-disagree', 'CVINVehicleLSP8.getDataForTokenId+tokenIdForVIN', Promise.all([c.getDataForTokenId(t, K_VIN).then(ethers.toUtf8String), c.tokenIdForVIN(VINS.honda)]),
    'store says Honda VIN, but keccak(Honda VIN) != tokenId: a verifier must re-hash the stored VIN and compare to the tokenId to detect this', (v) => { assert.equal(v[0], VINS.honda); assert.notEqual(v[1], t); });
});
