'use strict';
/**
 * ERC-721 — family "Attributes / data store" (manifest: implemented, not measured; the comparison's
 * updateAttribute analogue is addServiceRecord). Exercises the append-only service-record list,
 * the raw public getters, ERC721URIStorage tokenURI (with the ERC-4906 MetadataUpdate event),
 * the metadata struct, and the toll-scenario entry record on CVIN_NFT_DID_ERC721
 * (recordEntry / getEntryTimestamp), plus baseURI concatenation on both DID variants.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-721/demos/attributes.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, eventCount, VINS } = require('./_lib');

const d = demo('erc-721', 'attributes');

d.run(async () => {
  const [deployer, vehicleOwner, newOwner, serviceCenter] = await ethers.getSigners();
  const { assert } = d;
  const nft = await (await ethers.getContractFactory('CVINVehicleNFT', deployer)).deploy();
  await nft.waitForDeployment();
  const rm = await (await nft.mintVehicle(vehicleOwner.address, VINS.vw, 'Volkswagen', 'Golf', 1999, 'Blue', `ipfs://cvin/${VINS.vw}.json`)).wait();
  assert.equal(eventCount(nft, rm, 'MetadataUpdate'), 1);
  d.offchain('setup', 'CVINVehicleNFT.mintVehicle', 'vehicle minted; _setTokenURI emitted ERC-4906 MetadataUpdate(tokenId) inside the mint tx');

  await d.tx('grant-service-center', 'CVINVehicleNFT.grantServiceCenterRole', nft.connect(deployer).grantServiceCenterRole(serviceCenter.address), 'setup: only SERVICE_CENTER_ROLE may append records (the vehicle owner cannot write its own attributes)');
  const r1 = await d.tx('add-service-record', 'CVINVehicleNFT.addServiceRecord', nft.connect(serviceCenter).addServiceRecord(1, 'ipfs://service/2024-03-01-oil-change.json'),
    'MEASURED as updateAttribute analogue: append-only string list, no key, no overwrite, no validity');
  const ev = eventArgs(nft, r1, 'ServiceRecordAdded'); assert.equal(ev.addedBy, serviceCenter.address);
  await d.tx('add-service-record-2', 'CVINVehicleNFT.addServiceRecord', nft.connect(serviceCenter).addServiceRecord(1, 'ipfs://service/2024-09-15-brake-pads.json'), 'second record (list grows; nothing can be removed)');
  await d.reverts('add-record-unauthorised', 'CVINVehicleNFT.addServiceRecord', () => nft.connect(vehicleOwner).addServiceRecord(1, 'ipfs://owner-claim'), 'AccessControlUnauthorizedAccount', 'veracity rests on the role grant, not on a signature: the chain checks WHO wrote, never WHAT');
  await d.reverts('add-record-nonexistent', 'CVINVehicleNFT.addServiceRecord', () => nft.connect(serviceCenter).addServiceRecord(42, 'ipfs://x'), 'token does not exist', 'existence check');
  await d.view('get-service-records', 'CVINVehicleNFT.getServiceRecords', nft.getServiceRecords(1), 'whole list in one read', (v) => assert.deepEqual([...v], ['ipfs://service/2024-03-01-oil-change.json', 'ipfs://service/2024-09-15-brake-pads.json']));
  await d.view('service-records-getter', 'CVINVehicleNFT.serviceRecords', nft.serviceRecords(1, 1), 'raw public-mapping getter (tokenId, index)', (v) => assert.equal(v, 'ipfs://service/2024-09-15-brake-pads.json'));
  await d.view('token-uri', 'CVINVehicleNFT.tokenURI', nft.tokenURI(1), 'per-token metadata URI (no baseURI on this contract); content is off-chain and unverified', (v) => assert.equal(v, `ipfs://cvin/${VINS.vw}.json`));
  await d.view('vehicle-metadata', 'CVINVehicleNFT.vehicleMetadata', nft.vehicleMetadata(1), 'typed struct written once at mint; no setter exists, so make/model/color are immutable', (m) => { assert.equal(m.model, 'Golf'); assert.equal(m.color, 'Blue'); });
  await d.reverts('token-uri-nonexistent', 'CVINVehicleNFT.tokenURI', () => nft.tokenURI(42), 'ERC721NonexistentToken', 'URI of a missing token reverts');
  d.offchain('no-keyed-store', 'CVINVehicleNFT', 'asymmetry: no setAttribute(key,value), no validity, no revocation of a record — a verifier must parse the free-form string list');

  // ---- CVIN_NFT_DID_ERC721: toll entry record + baseURI ----
  const did = await (await ethers.getContractFactory('CVIN_NFT_DID_ERC721', deployer)).deploy('CVIN Vehicle DID', 'CVIN-DID', deployer.address, 250);
  await did.waitForDeployment();
  const rmint = await d.tx('did-mint', 'CVIN_NFT_DID_ERC721.mint', did.connect(deployer).mint(vehicleOwner.address, 1, `${VINS.vw}.json`), 'mint with a relative URI');
  assert.equal(eventCount(did, rmint, 'MetadataUpdate'), 1);
  await d.view('did-token-uri', 'CVIN_NFT_DID_ERC721.tokenURI', did.tokenURI(1), 'ERC721URIStorage concatenates the hard-coded _baseURI with the stored suffix', (v) => assert.equal(v, `https://baseuri.example.com/${VINS.vw}.json`));
  const now = (await ethers.provider.getBlock('latest')).timestamp;
  const r2 = await d.tx('record-entry', 'CVIN_NFT_DID_ERC721.recordEntry', did.connect(deployer).recordEntry(1, now), 'toll operator (contract owner) stamps the zone-entry time on the identity (EntryRecorded)');
  assert.equal(eventArgs(did, r2, 'EntryRecorded').timestamp, BigInt(now));
  await d.view('get-entry-timestamp', 'CVIN_NFT_DID_ERC721.getEntryTimestamp', did.getEntryTimestamp(1), 'latest entry only (single slot; history is in events)', (v) => assert.equal(v, BigInt(now)));
  await d.tx('record-entry-overwrite', 'CVIN_NFT_DID_ERC721.recordEntry', did.connect(deployer).recordEntry(1, now + 3600), 'second entry overwrites the first');
  await d.view('get-entry-timestamp-2', 'CVIN_NFT_DID_ERC721.getEntryTimestamp', did.getEntryTimestamp(1), 'only the newest value survives on-chain', (v) => assert.equal(v, BigInt(now + 3600)));
  await d.view('get-entry-timestamp-none', 'CVIN_NFT_DID_ERC721.getEntryTimestamp', did.getEntryTimestamp(2), 'zero for a token without entries (and for nonexistent tokens: no existence check in the getter)', (v) => assert.equal(v, 0n));
  await d.reverts('record-entry-unauthorised', 'CVIN_NFT_DID_ERC721.recordEntry', () => did.connect(vehicleOwner).recordEntry(1, now), 'OwnableUnauthorizedAccount', 'only the operator writes; the vehicle cannot self-report');
  await d.reverts('record-entry-nonexistent', 'CVIN_NFT_DID_ERC721.recordEntry', () => did.connect(deployer).recordEntry(42, now), 'ERC721NonexistentToken', '_requireOwned');

  // ---- Monolithic tokenURI composition ----
  const mono = await (await ethers.getContractFactory('CVIN_NFT_DID_ERC721_Monolithic', deployer)).deploy('CVIN Mono', 'MONO', deployer.address, 500);
  await mono.waitForDeployment();
  await mono.mint(vehicleOwner.address, 1, `${VINS.vw}.json`);
  await mono.mint(newOwner.address, 2, '');
  await d.view('mono-token-uri', 'CVIN_NFT_DID_ERC721_Monolithic.tokenURI', mono.tokenURI(1), 'base + stored suffix', (v) => assert.equal(v, `https://baseuri.example.com/${VINS.vw}.json`));
  await d.view('mono-token-uri-default', 'CVIN_NFT_DID_ERC721_Monolithic.tokenURI', mono.tokenURI(2), 'empty suffix -> base + decimal tokenId', (v) => assert.equal(v, 'https://baseuri.example.com/2'));
  await d.reverts('mono-token-uri-nonexistent', 'CVIN_NFT_DID_ERC721_Monolithic.tokenURI', () => mono.tokenURI(3), 'URI query for nonexistent token', 'existence check');
});
