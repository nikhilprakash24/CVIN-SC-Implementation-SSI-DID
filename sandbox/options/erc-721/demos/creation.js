'use strict';
/**
 * ERC-721 — family "Identity creation (explicit)" (manifest: measured-in-comparison via mintVehicle).
 * Exercises all three contracts' creation surface: CVINVehicleNFT.mintVehicle (VIN-bound, role-gated,
 * metadata struct + initial transfer record), CVIN_NFT_DID_ERC721.mint and the Monolithic mint
 * (owner-only, caller-chosen tokenId, no VIN binding on-chain). Also the ERC-165/ERC-721 metadata
 * and enumeration views that describe what was created.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-721/demos/creation.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS, IFACE } = require('./_lib');

const d = demo('erc-721', 'creation');

d.run(async () => {
  const [deployer, vehicleOwner, newOwner] = await ethers.getSigners();
  const { assert } = d;

  // ---- CVINVehicleNFT (the comparison's contract) ----
  const NFT = await ethers.getContractFactory('CVINVehicleNFT', deployer);
  const nft = await NFT.deploy();
  await nft.waitForDeployment();
  const dep = await nft.deploymentTransaction().wait();
  d.offchain('deploy-nft', 'CVINVehicleNFT.constructor', `shared collection deployed, gasUsed=${dep.gasUsed}; deployer gets DEFAULT_ADMIN_ROLE + MANUFACTURER_ROLE (measured as deployRegistry)`);

  await d.view('name', 'CVINVehicleNFT.name', nft.name(), 'ERC-721 metadata name of the collection', (v) => assert.equal(v, 'CVIN Vehicle Identity'));
  await d.view('symbol', 'CVINVehicleNFT.symbol', nft.symbol(), 'ERC-721 metadata symbol', (v) => assert.equal(v, 'CVIN-VID'));
  await d.view('supports-erc721', 'CVINVehicleNFT.supportsInterface', nft.supportsInterface(IFACE.ERC721), 'ERC-165: declares ERC-721 (0x80ac58cd)', (v) => assert.equal(v, true));
  await d.view('supports-enumerable', 'CVINVehicleNFT.supportsInterface', nft.supportsInterface(IFACE.ERC721Enumerable), 'ERC-165: declares ERC-721 Enumerable (0x780e9d63)', (v) => assert.equal(v, true));
  await d.view('supports-metadata', 'CVINVehicleNFT.supportsInterface', nft.supportsInterface(IFACE.ERC721Metadata), 'ERC-165: declares ERC-721 Metadata (0x5b5e139f)', (v) => assert.equal(v, true));
  await d.view('supports-accesscontrol', 'CVINVehicleNFT.supportsInterface', nft.supportsInterface(IFACE.AccessControl), 'ERC-165: declares AccessControl (0x7965db0b)', (v) => assert.equal(v, true));

  const r1 = await d.tx('mint-vehicle', 'CVINVehicleNFT.mintVehicle',
    nft.connect(deployer).mintVehicle(vehicleOwner.address, VINS.bmw, 'BMW', '320d', 2012, 'Alpine White', `ipfs://cvin/${VINS.bmw}.json`),
    'MEASURED (createIdentity): manufacturer mints tokenId 1, binds VIN both ways, stores metadata struct + initial transfer record');
  const ev = eventArgs(nft, r1, 'VehicleMinted');
  assert.equal(ev.tokenId, 1n); assert.equal(ev.vin, VINS.bmw); assert.equal(ev.owner, vehicleOwner.address); assert.equal(ev.manufacturer, deployer.address);
  d.offchain('event-vehicle-minted', 'CVINVehicleNFT.VehicleMinted', 'event carries tokenId, VIN, owner, manufacturer (an indexer can build the identity from this log alone)');

  await d.tx('mint-second', 'CVINVehicleNFT.mintVehicle',
    nft.connect(deployer).mintVehicle(newOwner.address, VINS.honda, 'Honda', 'Accord', 2003, 'Silver', `ipfs://cvin/${VINS.honda}.json`),
    'second identity (tokenId 2) so the enumeration views have two entries');

  await d.reverts('mint-short-vin', 'CVINVehicleNFT.mintVehicle',
    () => nft.connect(deployer).mintVehicle(vehicleOwner.address, VINS.bmw.slice(0, 16), 'BMW', '320d', 2012, 'White', 'ipfs://x'),
    'invalid VIN length', 'chain enforces ISO 3779 length (17) but not the check digit or the character set');
  await d.reverts('mint-duplicate-vin', 'CVINVehicleNFT.mintVehicle',
    () => nft.connect(deployer).mintVehicle(vehicleOwner.address, VINS.bmw, 'BMW', '320d', 2012, 'White', 'ipfs://x'),
    'VIN already minted', 'VIN uniqueness enforced on-chain (string-keyed mapping)');
  await d.reverts('mint-unauthorised', 'CVINVehicleNFT.mintVehicle',
    () => nft.connect(vehicleOwner).mintVehicle(vehicleOwner.address, VINS.acura, 'Acura', 'Legend', 1992, 'Red', 'ipfs://x'),
    'AccessControlUnauthorizedAccount', 'only MANUFACTURER_ROLE can create identities (not self-sovereign creation)');
  await d.reverts('mint-to-zero', 'CVINVehicleNFT.mintVehicle',
    () => nft.connect(deployer).mintVehicle(ethers.ZeroAddress, VINS.acura, 'Acura', 'Legend', 1992, 'Red', 'ipfs://x'),
    'mint to zero address', 'zero-address owner rejected');

  await d.view('total-vehicles', 'CVINVehicleNFT.getTotalVehicles', nft.getTotalVehicles(), 'counter-based total (_nextTokenId-1); not reduced by anything since there is no burn', (v) => assert.equal(v, 2n));
  await d.view('total-supply', 'CVINVehicleNFT.totalSupply', nft.totalSupply(), 'ERC-721 Enumerable totalSupply (not measured)', (v) => assert.equal(v, 2n));
  await d.view('token-by-index', 'CVINVehicleNFT.tokenByIndex', nft.tokenByIndex(1), 'ERC-721 Enumerable global index -> tokenId 2', (v) => assert.equal(v, 2n));
  await d.view('owner-of', 'CVINVehicleNFT.ownerOf', nft.ownerOf(1), 'token owner == vehicle owner (ownership is control)', (v) => assert.equal(v, vehicleOwner.address));
  await d.view('metadata-struct', 'CVINVehicleNFT.vehicleMetadata', nft.vehicleMetadata(1),
    'on-chain struct: vin, make, model, year, color, manufacturer, mintTimestamp, active=true',
    (m) => { assert.equal(m.vin, VINS.bmw); assert.equal(m.make, 'BMW'); assert.equal(Number(m.year), 2012); assert.equal(m.manufacturer, deployer.address); assert.equal(m.active, true); });
  await d.view('token-uri', 'CVINVehicleNFT.tokenURI', nft.tokenURI(1), 'ERC721URIStorage per-token URI set at mint', (v) => assert.equal(v, `ipfs://cvin/${VINS.bmw}.json`));

  // ---- CVIN_NFT_DID_ERC721 (Ownable + ERC-2981; not used by the comparison) ----
  const DID = await ethers.getContractFactory('CVIN_NFT_DID_ERC721', deployer);
  const did = await DID.deploy('CVIN Vehicle DID', 'CVIN-DID', deployer.address, 250);
  await did.waitForDeployment();
  const dep2 = await did.deploymentTransaction().wait();
  d.offchain('deploy-did', 'CVIN_NFT_DID_ERC721.constructor', `Ownable + ERC-2981 variant deployed, gasUsed=${dep2.gasUsed}; default royalty 250 bps to deployer; NOT measured by the comparison`);
  const didTokenId = BigInt(ethers.keccak256(ethers.toUtf8Bytes(VINS.tesla)));
  await d.tx('did-mint', 'CVIN_NFT_DID_ERC721.mint', did.connect(deployer).mint(vehicleOwner.address, didTokenId, `${VINS.tesla}.json`),
    'owner-only mint with CALLER-CHOSEN tokenId (here uint256(keccak256(VIN)) by off-chain convention): no VIN binding or metadata on-chain');
  await d.reverts('did-mint-unauthorised', 'CVIN_NFT_DID_ERC721.mint', () => did.connect(vehicleOwner).mint(vehicleOwner.address, 7n, 'x.json'),
    'OwnableUnauthorizedAccount', 'single Ownable owner instead of AccessControl roles');
  await d.reverts('did-mint-duplicate', 'CVIN_NFT_DID_ERC721.mint', () => did.connect(deployer).mint(newOwner.address, didTokenId, 'y.json'),
    'ERC721InvalidSender', 'tokenId uniqueness enforced by OZ _mint, VIN uniqueness is not (the VIN never reaches the chain)');
  await d.view('did-name', 'CVIN_NFT_DID_ERC721.name', did.name(), 'constructor-supplied name', (v) => assert.equal(v, 'CVIN Vehicle DID'));
  await d.view('did-symbol', 'CVIN_NFT_DID_ERC721.symbol', did.symbol(), 'constructor-supplied symbol', (v) => assert.equal(v, 'CVIN-DID'));
  await d.view('did-owner-of', 'CVIN_NFT_DID_ERC721.ownerOf', did.ownerOf(didTokenId), 'token owner after mint', (v) => assert.equal(v, vehicleOwner.address));
  await d.view('did-supports-2981', 'CVIN_NFT_DID_ERC721.supportsInterface', did.supportsInterface(IFACE.ERC2981), 'ERC-165: declares ERC-2981 royalties (0x2a55205a)', (v) => assert.equal(v, true));

  // ---- CVIN_NFT_DID_ERC721_Monolithic (hand-rolled ERC-721 + ERC-2981) ----
  const MONO = await ethers.getContractFactory('CVIN_NFT_DID_ERC721_Monolithic', deployer);
  const mono = await MONO.deploy('CVIN Vehicle DID (monolithic)', 'CVIN-MONO', deployer.address, 500);
  await mono.waitForDeployment();
  const dep3 = await mono.deploymentTransaction().wait();
  d.offchain('deploy-mono', 'CVIN_NFT_DID_ERC721_Monolithic.constructor', `hand-rolled ERC-721 (no OZ inheritance) deployed, gasUsed=${dep3.gasUsed}; royalty 500 bps; NOT measured`);
  await d.tx('mono-mint', 'CVIN_NFT_DID_ERC721_Monolithic.mint', mono.connect(deployer).mint(vehicleOwner.address, didTokenId, `${VINS.tesla}.json`),
    'owner-only mint; _mint does NOT probe onERC721Received (unlike OZ _safeMint used by CVINVehicleNFT)');
  await d.reverts('mono-mint-duplicate', 'CVIN_NFT_DID_ERC721_Monolithic.mint', () => mono.connect(deployer).mint(newOwner.address, didTokenId, 'y.json'),
    'Token already minted', 'hand-rolled uniqueness check (string reason, not a custom error)');
  await d.reverts('mono-mint-zero', 'CVIN_NFT_DID_ERC721_Monolithic.mint', () => mono.connect(deployer).mint(ethers.ZeroAddress, 9n, 'y.json'),
    'Mint to the zero address', 'zero-address mint rejected');
  await d.reverts('mono-mint-unauthorised', 'CVIN_NFT_DID_ERC721_Monolithic.mint', () => mono.connect(vehicleOwner).mint(vehicleOwner.address, 9n, 'y.json'),
    'OwnableUnauthorizedAccount', 'Ownable gate');
  await d.view('mono-name', 'CVIN_NFT_DID_ERC721_Monolithic.name', mono.name(), 'name()', (v) => assert.equal(v, 'CVIN Vehicle DID (monolithic)'));
  await d.view('mono-symbol', 'CVIN_NFT_DID_ERC721_Monolithic.symbol', mono.symbol(), 'symbol()', (v) => assert.equal(v, 'CVIN-MONO'));
  await d.view('mono-owner-of', 'CVIN_NFT_DID_ERC721_Monolithic.ownerOf', mono.ownerOf(didTokenId), 'owner after mint', (v) => assert.equal(v, vehicleOwner.address));
  await d.view('mono-balance', 'CVIN_NFT_DID_ERC721_Monolithic.balanceOf', mono.balanceOf(vehicleOwner.address), 'balance moves by 1 per token (fixed from the original draft that added the tokenId)', (v) => assert.equal(v, 1n));
  await d.view('mono-supports', 'CVIN_NFT_DID_ERC721_Monolithic.supportsInterface', Promise.all([mono.supportsInterface(IFACE.ERC721), mono.supportsInterface(IFACE.ERC2981), mono.supportsInterface(IFACE.ERC721Enumerable)]),
    'ERC-165: ERC-721 + ERC-2981 yes, Enumerable no (hand-rolled list)', (v) => assert.deepEqual(v, [true, true, false]));
});
