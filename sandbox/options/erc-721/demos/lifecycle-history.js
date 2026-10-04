'use strict';
/**
 * ERC-721 — family "Lifecycle events / history" (manifest: implemented, not measured). The
 * on-chain TransferRecord[] (getTransferHistory / transferHistory getter / getOwnershipChain),
 * the service-record list as a lifecycle log, event replay (VehicleTransferred, ServiceRecordAdded,
 * EntryRecorded) and the single-slot toll entry history on CVIN_NFT_DID_ERC721.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-721/demos/lifecycle-history.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, VINS } = require('./_lib');

const d = demo('erc-721', 'lifecycle-history');

d.run(async () => {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const { assert } = d;
  const nft = await (await ethers.getContractFactory('CVINVehicleNFT', deployer)).deploy();
  await nft.waitForDeployment();
  await nft.grantServiceCenterRole(deployer.address);
  const mintBlock = (await (await nft.mintVehicle(vehicleOwner.address, VINS.hyundai, 'Hyundai', 'Elantra', 2017, 'Grey', 'ipfs://el')).wait()).blockNumber;
  d.offchain('setup', 'CVINVehicleNFT.mintVehicle', `vehicle minted in block ${mintBlock}; the mint itself is recorded as TransferRecord(from=0)`);

  await d.tx('service-1', 'CVINVehicleNFT.addServiceRecord', nft.addServiceRecord(1, 'ipfs://service/10k-km.json'), 'lifecycle entry 1 (service)');
  await d.tx('transfer-1', 'CVINVehicleNFT.transferFrom', nft.connect(vehicleOwner).transferFrom(vehicleOwner.address, newOwner.address, 1), 'lifecycle entry: first sale (TransferRecord appended by the _update override)');
  await d.tx('service-2', 'CVINVehicleNFT.addServiceRecord', nft.addServiceRecord(1, 'ipfs://service/30k-km.json'), 'lifecycle entry 2 (service)');
  await d.tx('transfer-2', 'CVINVehicleNFT.transferFrom', nft.connect(newOwner).transferFrom(newOwner.address, delegate.address, 1), 'lifecycle entry: second sale');

  const hist = await d.view('get-transfer-history', 'CVINVehicleNFT.getTransferHistory', nft.getTransferHistory(1),
    'full TransferRecord[] (from,to,timestamp,blockNumber) readable in one call — stored on-chain, not reconstructed from logs',
    (h) => { assert.equal(h.length, 3); assert.equal(h[0].from, ethers.ZeroAddress); assert.equal(h[1].from, vehicleOwner.address); assert.equal(h[2].to, delegate.address); assert.equal(Number(h[0].blockNumber), mintBlock); });
  await d.view('transfer-history-getter', 'CVINVehicleNFT.transferHistory', nft.transferHistory(1, 2), 'raw public-mapping getter (tokenId, index) returns the struct fields', (t) => assert.equal(t.to, delegate.address));
  await d.view('ownership-chain', 'CVINVehicleNFT.getOwnershipChain', nft.getOwnershipChain(1), 'projection of the history onto `to` addresses', (v) => assert.deepEqual([...v], [vehicleOwner.address, newOwner.address, delegate.address]));
  await d.view('service-records', 'CVINVehicleNFT.getServiceRecords', nft.getServiceRecords(1), 'service lifecycle (no timestamps on-chain — those are only in the ServiceRecordAdded log)', (v) => assert.equal(v.length, 2));
  await d.view('service-records-getter', 'CVINVehicleNFT.serviceRecords', nft.serviceRecords(1, 0), 'raw getter', (v) => assert.equal(v, 'ipfs://service/10k-km.json'));

  const tlogs = await nft.queryFilter(nft.filters.VehicleTransferred(1), 0, 'latest');
  assert.equal(tlogs.length, 2);
  d.offchain('replay-transfer-events', 'CVINVehicleNFT.VehicleTransferred', `${tlogs.length} VehicleTransferred logs (mint excluded) agree with the stored history: the same facts are kept twice (storage + log)`);
  const slogs = await nft.queryFilter(nft.filters.ServiceRecordAdded(1), 0, 'latest');
  assert.equal(slogs.length, 2);
  d.offchain('replay-service-events', 'CVINVehicleNFT.ServiceRecordAdded', `${slogs.length} ServiceRecordAdded logs carry addedBy + block (the storage list does not): ordering/time must come from the log`);
  const interleaved = [...tlogs.map((l) => ({ b: l.blockNumber, k: 'transfer' })), ...slogs.map((l) => ({ b: l.blockNumber, k: 'service' }))].sort((a, b) => a.b - b.b).map((x) => x.k);
  assert.deepEqual(interleaved, ['service', 'transfer', 'service', 'transfer']);
  d.offchain('interleaved-timeline', 'CVINVehicleNFT', `a verifier merges both logs by block to get the vehicle timeline: ${interleaved.join(' -> ')}`);
  d.offchain('role-admin-changed', 'CVINVehicleNFT.RoleAdminChanged', 'manifest lists RoleAdminChanged under history: it is declared by AccessControl but never emitted by this contract (no _setRoleAdmin call)');

  // ---- toll entries on the DID variant: latest-only storage, history in logs ----
  const did = await (await ethers.getContractFactory('CVIN_NFT_DID_ERC721', deployer)).deploy('CVIN Vehicle DID', 'CVIN-DID', deployer.address, 250);
  await did.waitForDeployment();
  await did.mint(vehicleOwner.address, 1, 'h.json');
  const t0 = (await ethers.provider.getBlock('latest')).timestamp;
  await d.tx('record-entry-a', 'CVIN_NFT_DID_ERC721.recordEntry', did.recordEntry(1, t0), 'toll zone entry A');
  await d.tx('record-entry-b', 'CVIN_NFT_DID_ERC721.recordEntry', did.recordEntry(1, t0 + 600), 'toll zone entry B overwrites A in storage');
  await d.view('entry-latest', 'CVIN_NFT_DID_ERC721.getEntryTimestamp', did.getEntryTimestamp(1), 'storage keeps only B', (v) => assert.equal(v, BigInt(t0 + 600)));
  const elogs = await did.queryFilter(did.filters.EntryRecorded(1), 0, 'latest');
  assert.equal(elogs.length, 2);
  d.offchain('replay-entry-events', 'CVIN_NFT_DID_ERC721.EntryRecorded', `${elogs.length} EntryRecorded logs = the full entry history; on-chain only the latest is queryable`);
});
