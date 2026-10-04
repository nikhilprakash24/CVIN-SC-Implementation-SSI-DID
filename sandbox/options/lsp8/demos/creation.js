'use strict';
/**
 * LSP8 — family "Identity creation (explicit)" (manifest: measured-in-comparison via mintVehicle).
 * Identity = one bytes32 token whose id is keccak256(VIN), minted by the issuing authority
 * (contract owner); the VIN is written into the token's LSP2-style data store at mint.
 * Exercises mintVehicle and its guards, tokenIdForVIN, exists, the collection views and the
 * three events one mint emits.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/lsp8/demos/creation.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, eventCount, VINS } = require('./_lib');

const d = demo('lsp8', 'creation');

d.run(async () => {
  const [authority, vehicleOwner, fleet, stranger] = await ethers.getSigners();
  const { assert } = d;
  const F = await ethers.getContractFactory('CVINVehicleLSP8', authority);
  const c = await F.deploy('CVIN Vehicle Identity LSP8', 'CVIN-LSP8');
  await c.waitForDeployment();
  const dep = await c.deploymentTransaction().wait();
  assert.equal(eventArgs(c, dep, 'OwnershipTransferred').newOwner, authority.address);
  d.offchain('deploy', 'CVINVehicleLSP8.constructor', `collection deployed, gasUsed=${dep.gasUsed}; deployer = issuing authority (owner), OwnershipTransferred(0, authority); measured as deployRegistry`);

  await d.view('name', 'CVINVehicleLSP8.name', c.name(), 'collection name', (v) => assert.equal(v, 'CVIN Vehicle Identity LSP8'));
  await d.view('symbol', 'CVINVehicleLSP8.symbol', c.symbol(), 'collection symbol', (v) => assert.equal(v, 'CVIN-LSP8'));
  await d.view('owner', 'CVINVehicleLSP8.owner', c.owner(), 'issuing authority', (v) => assert.equal(v, authority.address));
  await d.view('total-supply-0', 'CVINVehicleLSP8.totalSupply', c.totalSupply(), 'no identities yet', (v) => assert.equal(v, 0n));
  const tokenId = await d.view('token-id-for-vin', 'CVINVehicleLSP8.tokenIdForVIN', c.tokenIdForVIN(VINS.bmw), 'pure: tokenId = keccak256(bytes(VIN)) — the identifier is known before the mint (LSP8_TOKENID_FORMAT hash)', (v) => assert.equal(v, ethers.keccak256(ethers.toUtf8Bytes(VINS.bmw))));
  await d.view('exists-before', 'CVINVehicleLSP8.exists', c.exists(tokenId), 'not yet', (v) => assert.equal(v, false));
  await d.reverts('mint-unauthorised', 'CVINVehicleLSP8.mintVehicle', () => c.connect(stranger).mintVehicle(stranger.address, VINS.bmw), 'caller is not the contract owner', 'single authority mints (not self-sovereign)');
  await d.reverts('mint-zero', 'CVINVehicleLSP8.mintVehicle', () => c.connect(authority).mintVehicle(ethers.ZeroAddress, VINS.bmw), 'mint to zero address', 'guard');
  await d.reverts('mint-empty-vin', 'CVINVehicleLSP8.mintVehicle', () => c.connect(authority).mintVehicle(vehicleOwner.address, ''), 'empty VIN', 'only emptiness is checked, not the 17-char ISO length');

  const r = await d.tx('mint-vehicle', 'CVINVehicleLSP8.mintVehicle', c.connect(authority).mintVehicle(vehicleOwner.address, VINS.bmw),
    'MEASURED (createIdentity): mints tokenId=keccak(VIN) to the owner and stores the VIN under DATA_KEY_VIN');
  const vm = eventArgs(c, r, 'VehicleMinted'); assert.equal(vm.tokenId, tokenId); assert.equal(vm.vin, VINS.bmw); assert.equal(vm.vehicleOwner, vehicleOwner.address);
  const tr = eventArgs(c, r, 'Transfer'); assert.equal(tr.from, ethers.ZeroAddress); assert.equal(tr.to, vehicleOwner.address); assert.equal(tr.force, true); assert.equal(tr.operator, authority.address);
  assert.equal(eventCount(c, r, 'TokenIdDataChanged'), 1); assert.equal(eventCount(c, r, 'DataChanged'), 1);
  d.offchain('mint-events', 'CVINVehicleLSP8.VehicleMinted+Transfer+TokenIdDataChanged+DataChanged', 'one mint emits the LSP8 Transfer(operator, 0, to, tokenId, force=true, data), the per-token TokenIdDataChanged(VIN) plus a generic DataChanged, and the app-level VehicleMinted');
  await d.view('exists-after', 'CVINVehicleLSP8.exists', c.exists(tokenId), 'identity exists', (v) => assert.equal(v, true));
  await d.view('token-owner-of', 'CVINVehicleLSP8.tokenOwnerOf', c.tokenOwnerOf(tokenId), 'vehicle owner', (v) => assert.equal(v, vehicleOwner.address));
  await d.view('vin-stored', 'CVINVehicleLSP8.getDataForTokenId', c.getDataForTokenId(tokenId, await c.DATA_KEY_VIN()).then(ethers.toUtf8String), 'the VIN lives in the per-token data store (plain text)', (v) => assert.equal(v, VINS.bmw));
  await d.view('total-supply-1', 'CVINVehicleLSP8.totalSupply', c.totalSupply(), 'one identity', (v) => assert.equal(v, 1n));
  await d.view('balance-of', 'CVINVehicleLSP8.balanceOf', c.balanceOf(vehicleOwner.address), 'owner holds one', (v) => assert.equal(v, 1n));
  await d.view('token-ids-of', 'CVINVehicleLSP8.tokenIdsOf', c.tokenIdsOf(vehicleOwner.address), 'owner -> tokenIds (LSP8 enumeration, no index needed)', (v) => assert.deepEqual([...v], [tokenId]));
  await d.reverts('mint-duplicate', 'CVINVehicleLSP8.mintVehicle', () => c.connect(authority).mintVehicle(fleet.address, VINS.bmw), 'tokenId already minted', 'VIN uniqueness == tokenId uniqueness (same hash)');
  await d.tx('mint-fleet-1', 'CVINVehicleLSP8.mintVehicle', c.connect(authority).mintVehicle(fleet.address, VINS.ford), 'fleet vehicle 1');
  await d.tx('mint-fleet-2', 'CVINVehicleLSP8.mintVehicle', c.connect(authority).mintVehicle(fleet.address, VINS.tesla), 'fleet vehicle 2');
  await d.tx('mint-short-vin', 'CVINVehicleLSP8.mintVehicle', c.connect(authority).mintVehicle(fleet.address, 'SHORT'), 'OBSERVATION: a 5-character "VIN" is accepted (no ISO 3779 validation)');
  await d.view('fleet-token-ids', 'CVINVehicleLSP8.tokenIdsOf', c.tokenIdsOf(fleet.address), 'three ids for the fleet', (v) => assert.equal(v.length, 3));
  await d.view('total-supply-4', 'CVINVehicleLSP8.totalSupply', c.totalSupply(), 'four identities', (v) => assert.equal(v, 4n));
  await d.reverts('token-owner-of-missing', 'CVINVehicleLSP8.tokenOwnerOf', () => c.tokenOwnerOf(ethers.id('nope')), 'tokenId does not exist', 'checked getter');
});
