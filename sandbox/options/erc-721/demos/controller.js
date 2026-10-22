'use strict';
/**
 * ERC-721 — family "Ownership / controller change" (manifest: implemented, not measured; the
 * comparison measures transferFrom under "transfer"). For an NFT, token ownership IS control, so
 * every transfer function is a controller change: transferFrom, both safeTransferFrom overloads
 * (with the onERC721Received hook on contract recipients), owner-indexed enumeration
 * (getVehiclesByOwner / tokenOfOwnerByIndex) and the on-chain ownership chain. The Ownable
 * surface of the two DID variants (owner / transferOwnership / renounceOwnership) is a different
 * thing: it moves the COLLECTION's administrator, not a vehicle.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-721/demos/controller.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, deployEchoReceiver, VINS } = require('./_lib');

const d = demo('erc-721', 'controller');

d.run(async () => {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const { assert } = d;
  const nft = await (await ethers.getContractFactory('CVINVehicleNFT', deployer)).deploy();
  await nft.waitForDeployment();
  await nft.mintVehicle(vehicleOwner.address, VINS.bmw, 'BMW', '320d', 2012, 'White', 'ipfs://1');
  await nft.mintVehicle(vehicleOwner.address, VINS.honda, 'Honda', 'Accord', 2003, 'Silver', 'ipfs://2');
  const receiver = await deployEchoReceiver(deployer);
  d.offchain('setup', 'CVINVehicleNFT.mintVehicle', `two vehicles minted to the same owner; echo-selector receiver contract at ${receiver.address} (gas ${receiver.gasUsed}) for hook tests`);

  await d.view('owner-of', 'CVINVehicleNFT.ownerOf', nft.ownerOf(1), 'controller of a vehicle == ownerOf(tokenId)', (v) => assert.equal(v, vehicleOwner.address));
  await d.view('balance-of', 'CVINVehicleNFT.balanceOf', nft.balanceOf(vehicleOwner.address), 'vehicles controlled by an address', (v) => assert.equal(v, 2n));
  await d.view('vehicles-by-owner', 'CVINVehicleNFT.getVehiclesByOwner', nft.getVehiclesByOwner(vehicleOwner.address), 'owner -> tokenIds via Enumerable (reverse lookup absent in most DID registries)', (v) => assert.deepEqual([...v], [1n, 2n]));
  await d.view('token-of-owner-by-index', 'CVINVehicleNFT.tokenOfOwnerByIndex', nft.tokenOfOwnerByIndex(vehicleOwner.address, 1), 'ERC-721 Enumerable per-owner index', (v) => assert.equal(v, 2n));

  const r = await d.tx('transfer-from', 'CVINVehicleNFT.transferFrom', nft.connect(vehicleOwner).transferFrom(vehicleOwner.address, newOwner.address, 1),
    'MEASURED as "transfer"/"controller-change": plain transferFrom; _update override appends a TransferRecord and emits VehicleTransferred');
  const ev = eventArgs(nft, r, 'VehicleTransferred'); assert.equal(ev.from, vehicleOwner.address); assert.equal(ev.to, newOwner.address);
  await d.tx('safe-transfer', 'CVINVehicleNFT.safeTransferFrom(address,address,uint256)', nft.connect(newOwner)['safeTransferFrom(address,address,uint256)'](newOwner.address, delegate.address, 1),
    '3-arg safeTransferFrom to an EOA: no hook call (code.length == 0); what the adapter uses');
  await d.tx('safe-transfer-data-hook', 'CVINVehicleNFT.safeTransferFrom(address,address,uint256,bytes)', nft.connect(delegate)['safeTransferFrom(address,address,uint256,bytes)'](delegate.address, receiver.address, 1, '0xc0ffee'),
    '4-arg safeTransferFrom to a CONTRACT: OZ calls onERC721Received(operator,from,tokenId,data) and requires the selector back (receiver echoes it)');
  await d.view('owner-is-contract', 'CVINVehicleNFT.ownerOf', nft.ownerOf(1), 'a contract account can control a vehicle', (v) => assert.equal(v, receiver.address));
  const nftAddress = await nft.getAddress();
  await d.reverts('safe-transfer-non-receiver', 'CVINVehicleNFT.safeTransferFrom(address,address,uint256)', () => nft.connect(vehicleOwner)['safeTransferFrom(address,address,uint256)'](vehicleOwner.address, nftAddress, 2),
    'ERC721InvalidReceiver', 'safe transfer to a contract without onERC721Received (the collection itself) is refused — the hook guards against locking the identity');
  await d.reverts('transfer-unauthorised', 'CVINVehicleNFT.transferFrom', () => nft.connect(delegate).transferFrom(vehicleOwner.address, delegate.address, 2),
    'ERC721InsufficientApproval', 'neither owner nor approved: chain enforces control');
  await d.reverts('transfer-wrong-from', 'CVINVehicleNFT.transferFrom', () => nft.connect(vehicleOwner).transferFrom(newOwner.address, delegate.address, 2),
    'ERC721IncorrectOwner', '`from` must be the current owner');
  await d.view('ownership-chain', 'CVINVehicleNFT.getOwnershipChain', nft.getOwnershipChain(1), 'all controllers in order, derived from the on-chain TransferRecord[] (mint -> owner -> newOwner -> delegate -> receiver)',
    (v) => assert.deepEqual([...v], [vehicleOwner.address, newOwner.address, delegate.address, receiver.address]));
  await d.view('vehicles-by-owner-after', 'CVINVehicleNFT.getVehiclesByOwner', nft.getVehiclesByOwner(vehicleOwner.address), 'enumeration tracks the moves', (v) => assert.deepEqual([...v], [2n]));

  // ---- Ownable surface on the DID variant: collection admin, not vehicle control ----
  const did = await (await ethers.getContractFactory('CVIN_NFT_DID_ERC721', deployer)).deploy('CVIN Vehicle DID', 'CVIN-DID', deployer.address, 250);
  await did.waitForDeployment();
  await did.mint(vehicleOwner.address, 1, 'a.json');
  await d.view('did-owner', 'CVIN_NFT_DID_ERC721.owner', did.owner(), 'Ownable owner = collection administrator (toll operator), NOT a vehicle controller', (v) => assert.equal(v, deployer.address));
  const r2 = await d.tx('did-transfer-ownership', 'CVIN_NFT_DID_ERC721.transferOwnership', did.connect(deployer).transferOwnership(newOwner.address), 'moves the ADMIN role (mint/recordEntry/toll receiver), no vehicle changes hands');
  assert.equal(eventArgs(did, r2, 'OwnershipTransferred').newOwner, newOwner.address);
  await d.reverts('did-old-admin-mint', 'CVIN_NFT_DID_ERC721.mint', () => did.connect(deployer).mint(deployer.address, 2, 'b.json'), 'OwnableUnauthorizedAccount', 'old admin lost mint');
  await d.tx('did-new-admin-mint', 'CVIN_NFT_DID_ERC721.mint', did.connect(newOwner).mint(newOwner.address, 2, 'b.json'), 'new admin can mint');
  await d.tx('did-transfer-from', 'CVIN_NFT_DID_ERC721.transferFrom', did.connect(vehicleOwner).transferFrom(vehicleOwner.address, delegate.address, 1), 'vehicle (token) control change on the DID variant: plain OZ transferFrom, no history bookkeeping');
  await d.tx('did-safe-transfer', 'CVIN_NFT_DID_ERC721.safeTransferFrom(address,address,uint256)', did.connect(delegate)['safeTransferFrom(address,address,uint256)'](delegate.address, vehicleOwner.address, 1), '3-arg safe transfer to EOA');
  await d.tx('did-safe-transfer-hook', 'CVIN_NFT_DID_ERC721.safeTransferFrom(address,address,uint256,bytes)', did.connect(vehicleOwner)['safeTransferFrom(address,address,uint256,bytes)'](vehicleOwner.address, receiver.address, 1, '0x01'), '4-arg safe transfer to the echo receiver (hook accepted)');
  await d.view('did-owner-of', 'CVIN_NFT_DID_ERC721.ownerOf', did.ownerOf(1), 'token now held by the receiver contract', (v) => assert.equal(v, receiver.address));
  await d.tx('did-renounce', 'CVIN_NFT_DID_ERC721.renounceOwnership', did.connect(newOwner).renounceOwnership(), 'admin renounced: owner() becomes address(0); mint/recordEntry become impossible forever (see token-economics for the toll consequence)');
  await d.view('did-owner-zero', 'CVIN_NFT_DID_ERC721.owner', did.owner(), 'no administrator left', (v) => assert.equal(v, ethers.ZeroAddress));
  await d.reverts('did-mint-after-renounce', 'CVIN_NFT_DID_ERC721.mint', () => did.connect(newOwner).mint(newOwner.address, 3, 'c.json'), 'OwnableUnauthorizedAccount', 'collection is frozen for new identities');

  // ---- Monolithic: full hand-rolled transfer surface incl. hooks ----
  const mono = await (await ethers.getContractFactory('CVIN_NFT_DID_ERC721_Monolithic', deployer)).deploy('CVIN Mono', 'MONO', deployer.address, 500);
  await mono.waitForDeployment();
  await mono.mint(vehicleOwner.address, 1, 'a.json');
  await mono.mint(vehicleOwner.address, 2, 'b.json');
  await d.view('mono-owner', 'CVIN_NFT_DID_ERC721_Monolithic.owner', mono.owner(), 'Ownable admin', (v) => assert.equal(v, deployer.address));
  await d.tx('mono-transfer-from', 'CVIN_NFT_DID_ERC721_Monolithic.transferFrom', mono.connect(vehicleOwner).transferFrom(vehicleOwner.address, newOwner.address, 1), 'hand-rolled transferFrom: _isApprovedOrOwner + _transfer (clears approval, moves balances)');
  await d.tx('mono-safe-transfer', 'CVIN_NFT_DID_ERC721_Monolithic.safeTransferFrom(address,address,uint256)', mono.connect(newOwner)['safeTransferFrom(address,address,uint256)'](newOwner.address, delegate.address, 1), '3-arg overload forwards to the 4-arg one with empty data');
  await d.tx('mono-safe-transfer-hook', 'CVIN_NFT_DID_ERC721_Monolithic.safeTransferFrom(address,address,uint256,bytes)', mono.connect(delegate)['safeTransferFrom(address,address,uint256,bytes)'](delegate.address, receiver.address, 1, '0xbeef'), 'hand-rolled _checkOnERC721Received: try/catch around the hook, selector compared');
  const monoAddress = await mono.getAddress();
  await d.reverts('mono-safe-transfer-non-receiver', 'CVIN_NFT_DID_ERC721_Monolithic.safeTransferFrom(address,address,uint256)', () => mono.connect(vehicleOwner)['safeTransferFrom(address,address,uint256)'](vehicleOwner.address, monoAddress, 2),
    'Transfer to non ERC721Receiver implementer', 'contract without the hook is refused (the collection itself has no fallback -> empty revert data -> string reason)');
  await d.reverts('mono-transfer-wrong-from', 'CVIN_NFT_DID_ERC721_Monolithic.transferFrom', () => mono.connect(vehicleOwner).transferFrom(newOwner.address, delegate.address, 2), 'Transfer of token that is not own', '`from` must own the token');
  await d.reverts('mono-transfer-unauthorised', 'CVIN_NFT_DID_ERC721_Monolithic.transferFrom', () => mono.connect(delegate).transferFrom(vehicleOwner.address, delegate.address, 2), 'Caller is not owner nor approved', 'control enforced');
  await d.reverts('mono-transfer-to-zero', 'CVIN_NFT_DID_ERC721_Monolithic.transferFrom', () => mono.connect(vehicleOwner).transferFrom(vehicleOwner.address, ethers.ZeroAddress, 2), 'Transfer to the zero address', 'no public burn: cannot transfer to 0');
  await d.view('mono-balances', 'CVIN_NFT_DID_ERC721_Monolithic.balanceOf', Promise.all([mono.balanceOf(vehicleOwner.address), mono.balanceOf(receiver.address)]), 'balances after the moves', (v) => assert.deepEqual(v, [1n, 1n]));
  await d.tx('mono-transfer-ownership', 'CVIN_NFT_DID_ERC721_Monolithic.transferOwnership', mono.connect(deployer).transferOwnership(newOwner.address), 'collection admin moved');
  await d.tx('mono-renounce', 'CVIN_NFT_DID_ERC721_Monolithic.renounceOwnership', mono.connect(newOwner).renounceOwnership(), 'collection admin renounced (owner()==0)');
  await d.view('mono-owner-zero', 'CVIN_NFT_DID_ERC721_Monolithic.owner', mono.owner(), 'frozen collection', (v) => assert.equal(v, ethers.ZeroAddress));
});
