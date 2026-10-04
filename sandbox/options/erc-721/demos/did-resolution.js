'use strict';
/**
 * ERC-721 — family "DID / resolution helpers" (manifest: implemented, not measured). The on-chain
 * DID string helper (getVehicleDID -> did:nft:erc721:<contract>:<tokenId>), the ERC-165
 * introspection a resolver uses to recognise the contract, and the adapter's resolve() that
 * assembles a DID-document-like object from views only (what the L1/L3 suites compare).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-721/demos/did-resolution.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, VINS, IFACE } = require('./_lib');
const Erc721Adapter = require('../adapter');

const d = demo('erc-721', 'did-resolution');

d.run(async () => {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const { assert } = d;
  const adapter = new Erc721Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  const dep = await adapter.deploy();
  d.offchain('setup', 'CVINVehicleNFT.constructor', `deployed through the adapter (gas ${dep.gasUsed}, setup ${dep.setupGasUsed})`);
  const nft = adapter.contract;
  const created = await adapter.create({ vin: VINS.tesla, owner: vehicleOwner.address });
  d.offchain('create-via-adapter', 'CVINVehicleNFT.mintVehicle', `adapter.create -> id ${created.id} (gas ${created.gasUsed})`);

  const addr = (await nft.getAddress()).toLowerCase();
  await d.view('get-vehicle-did', 'CVINVehicleNFT.getVehicleDID', nft.getVehicleDID(1), 'on-chain DID string did:nft:erc721:<contract lowercase hex>:<tokenId> (no DID document on-chain, only the identifier)', (v) => assert.equal(v, `did:nft:erc721:${addr}:1`));
  await d.reverts('get-vehicle-did-nonexistent', 'CVINVehicleNFT.getVehicleDID', () => nft.getVehicleDID(2), 'token does not exist', 'resolution of a missing identity reverts rather than returning a DID');
  await d.view('introspection', 'CVINVehicleNFT.supportsInterface', Promise.all([nft.supportsInterface(IFACE.ERC165), nft.supportsInterface(IFACE.ERC721), nft.supportsInterface('0xffffffff')]), 'a did:nft resolver first checks ERC-165/ERC-721 support (0xffffffff must be false)', (v) => assert.deepEqual(v, [true, true, false]));

  const res = await adapter.resolve(created.id);
  assert.equal(res.value.id, `did:nft:erc721:${addr}:1`);
  assert.equal(res.value.controller, vehicleOwner.address);
  assert.equal(res.value.verificationMethod[0].blockchainAccountId, `eip155:31337:${vehicleOwner.address}`);
  assert.equal(res.value.vin, VINS.tesla);
  d.offchain('resolve-via-adapter', 'adapter.resolve (ownerOf,getVehicleDID,tokenIdToVIN,vehicleMetadata,tokenURI,getApproved,getServiceRecords,getTransferHistory,getOwnershipChain,isVehicleActive)',
    `DID document synthesised from ${10} views: controller=${res.value.controller.slice(0, 10)}… vm=EcdsaSecp256k1RecoveryMethod2020 over the owner EOA; MEASURED as resolve (gas 0)`);
  await adapter.changeController(created.id, newOwner.address);
  const res2 = await adapter.resolve(created.id);
  assert.equal(res2.value.controller, newOwner.address);
  assert.equal(res2.value.ownershipChain.length, 2);
  d.offchain('resolve-after-transfer', 'adapter.resolve', 'controller follows ownerOf; the ownership chain is part of the document (unique to this option)');
  d.offchain('did-variants', 'CVIN_NFT_DID_ERC721 / Monolithic', 'asymmetry: the two DID variants have no DID helper despite their names; a resolver must form did:nft / did:pkh identifiers off-chain and has no VIN, status or history to put in the document');
});
