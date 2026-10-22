'use strict';
/**
 * ERC-721 — family "VIN linkage" (manifest: implemented, not measured). The bidirectional
 * VIN <-> tokenId index on CVINVehicleNFT (public mappings + checked getters), its sentinel, the
 * D13 normalisation (mint and the checked getter upper-case and ISO 3779-check the VIN; the raw
 * public mappings cannot), and the absence of any VIN binding on the two DID variants.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-721/demos/vin-linkage.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, VINS } = require('./_lib');

const d = demo('erc-721', 'vin-linkage');

d.run(async () => {
  const [deployer, vehicleOwner] = await ethers.getSigners();
  const { assert } = d;
  const nft = await (await ethers.getContractFactory('CVINVehicleNFT', deployer)).deploy();
  await nft.waitForDeployment();
  await d.tx('mint', 'CVINVehicleNFT.mintVehicle', nft.mintVehicle(vehicleOwner.address, VINS.acura, 'Acura', 'Legend', 1992, 'Red', 'ipfs://legend'), 'mint writes vinToTokenId[vin]=1 and tokenIdToVIN[1]=vin (plain-text VIN on-chain: no privacy)');

  await d.view('get-token-id-from-vin', 'CVINVehicleNFT.getTokenIdFromVIN', nft.getTokenIdFromVIN(VINS.acura), 'checked VIN -> tokenId lookup', (v) => assert.equal(v, 1n));
  await d.view('get-vin-from-token-id', 'CVINVehicleNFT.getVINFromTokenId', nft.getVINFromTokenId(1), 'checked tokenId -> VIN lookup', (v) => assert.equal(v, VINS.acura));
  await d.view('vin-to-token-id-raw', 'CVINVehicleNFT.vinToTokenId', nft.vinToTokenId(VINS.acura), 'raw mapping getter', (v) => assert.equal(v, 1n));
  await d.view('token-id-to-vin-raw', 'CVINVehicleNFT.tokenIdToVIN', nft.tokenIdToVIN(1), 'raw mapping getter', (v) => assert.equal(v, VINS.acura));
  await d.reverts('unknown-vin-checked', 'CVINVehicleNFT.getTokenIdFromVIN', () => nft.getTokenIdFromVIN(VINS.renault), 'VIN not found', 'checked getter reverts on an unknown VIN');
  await d.view('unknown-vin-raw', 'CVINVehicleNFT.vinToTokenId', nft.vinToTokenId(VINS.renault), 'raw getter returns the 0 sentinel (why tokenIds start at 1)', (v) => assert.equal(v, 0n));
  await d.reverts('unknown-token-checked', 'CVINVehicleNFT.getVINFromTokenId', () => nft.getVINFromTokenId(99), 'token does not exist', 'checked getter reverts on an unknown tokenId');
  await d.view('unknown-token-raw', 'CVINVehicleNFT.tokenIdToVIN', nft.tokenIdToVIN(99), 'raw getter returns an empty string', (v) => assert.equal(v, ''));
  await d.view('case-sensitive', 'CVINVehicleNFT.vinToTokenId', nft.vinToTokenId(VINS.acura.toLowerCase()), 'the RAW public mapping getter is still case-sensitive: Solidity auto-generated getters cannot normalise, and the mapping is keyed by the normalised (upper-case) VIN only — read through getTokenIdFromVIN, which normalises (next steps)', (v) => assert.equal(v, 0n));
  await d.reverts('mint-lowercase-twin', 'CVINVehicleNFT.mintVehicle', () => nft.mintVehicle(vehicleOwner.address, VINS.acura.toLowerCase(), 'Acura', 'Legend', 1992, 'Red', 'ipfs://legend-dup'), 'VIN already minted', 'FIXED (D13): mintVehicle upper-cases the VIN before the uniqueness check, so the same physical VIN in lower case is the SAME identity and cannot be minted twice (formerly it minted tokenId 2)');
  await d.view('twin-exists', 'CVINVehicleNFT.getTokenIdFromVIN', nft.getTokenIdFromVIN(VINS.acura.toLowerCase()), 'FIXED (D13): the checked getter normalises too — the lower-cased lookup finds the ORIGINAL token (1), so one vehicle has one token', (v) => assert.equal(v, 1n));
  await d.reverts('mint-invalid-char', 'CVINVehicleNFT.mintVehicle', () => nft.mintVehicle(vehicleOwner.address, 'JH4KA7532NC03679I', 'Acura', 'Legend', 1992, 'Red', 'ipfs://x'), 'invalid VIN character', 'FIXED (D13): ISO 3779 shape is enforced — I, O and Q are rejected (17-char length was already checked; the check digit is intentionally not enforced)');
  await d.view('total-after', 'CVINVehicleNFT.totalSupply', nft.totalSupply(), 'still exactly one token for the one vehicle', (v) => assert.equal(v, 1n));
  d.offchain('did-variants', 'CVIN_NFT_DID_ERC721 / Monolithic', 'asymmetry: neither DID variant stores a VIN; the caller picks the tokenId (e.g. uint256(keccak256(VIN)) by convention), so VIN linkage is an off-chain promise the chain cannot check');
});
