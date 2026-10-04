'use strict';
/**
 * ERC-721 — family "Token economics (approvals, royalties, payments)" (manifest: measured-in-
 * comparison via approve only). Everything else here the comparison never touches: operator
 * approvals and approved-party transfers on all three contracts, ERC-2981 royaltyInfo on the two
 * DID variants, and the toll settlement (payToll) with real ether on CVIN_NFT_DID_ERC721 —
 * including the consequence of renounceOwnership on where the toll goes.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-721/demos/token-economics.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS, IFACE } = require('./_lib');

const d = demo('erc-721', 'token-economics');

d.run(async () => {
  const [deployer, vehicleOwner, newOwner, operator, stranger] = await ethers.getSigners();
  const { assert } = d;
  const nft = await (await ethers.getContractFactory('CVINVehicleNFT', deployer)).deploy();
  await nft.waitForDeployment();
  await nft.mintVehicle(vehicleOwner.address, VINS.toyota, 'Toyota', 'Prius', 2010, 'White', 'ipfs://p1');
  await nft.mintVehicle(vehicleOwner.address, VINS.volvo, 'Volvo', 'V70', 2009, 'Blue', 'ipfs://v70');
  d.offchain('setup', 'CVINVehicleNFT.mintVehicle', 'two vehicles minted to vehicleOwner');

  // ---- CVINVehicleNFT approvals ----
  const r1 = await d.tx('approve', 'CVINVehicleNFT.approve', nft.connect(vehicleOwner).approve(operator.address, 1), 'MEASURED as addDelegateOrClaim analogue: single-token transfer approval (Approval event); it delegates the right to MOVE the identity, not to act for it');
  assert.equal(eventArgs(nft, r1, 'Approval').approved, operator.address);
  await d.view('get-approved', 'CVINVehicleNFT.getApproved', nft.getApproved(1), 'approved party readable', (v) => assert.equal(v, operator.address));
  await d.tx('approved-transfer', 'CVINVehicleNFT.transferFrom', nft.connect(operator).transferFrom(vehicleOwner.address, newOwner.address, 1), 'the approved party moves the token (sale via marketplace pattern)');
  await d.view('approval-cleared', 'CVINVehicleNFT.getApproved', nft.getApproved(1), 'approval is consumed by the transfer', (v) => assert.equal(v, ethers.ZeroAddress));
  await d.reverts('approve-unauthorised', 'CVINVehicleNFT.approve', () => nft.connect(stranger).approve(stranger.address, 2), 'ERC721InvalidApprover', 'only owner/operator may approve');
  const r2 = await d.tx('set-approval-for-all', 'CVINVehicleNFT.setApprovalForAll', nft.connect(vehicleOwner).setApprovalForAll(operator.address, true), 'operator approval over ALL of an owner\'s vehicles (fleet-manager pattern) -> ApprovalForAll');
  assert.equal(eventArgs(nft, r2, 'ApprovalForAll').approved, true);
  await d.view('is-approved-for-all', 'CVINVehicleNFT.isApprovedForAll', nft.isApprovedForAll(vehicleOwner.address, operator.address), 'operator status readable', (v) => assert.equal(v, true));
  await d.tx('operator-approve', 'CVINVehicleNFT.approve', nft.connect(operator).approve(stranger.address, 2), 'an operator may also issue per-token approvals on the owner\'s behalf');
  await d.tx('operator-safe-transfer', 'CVINVehicleNFT.safeTransferFrom(address,address,uint256)', nft.connect(operator)['safeTransferFrom(address,address,uint256)'](vehicleOwner.address, newOwner.address, 2), 'operator moves vehicle 2');
  await d.tx('clear-operator', 'CVINVehicleNFT.setApprovalForAll', nft.connect(vehicleOwner).setApprovalForAll(operator.address, false), 'operator approval revoked');
  await d.view('balances', 'CVINVehicleNFT.balanceOf', Promise.all([nft.balanceOf(vehicleOwner.address), nft.balanceOf(newOwner.address)]), 'balances after the two approved transfers', (v) => assert.deepEqual(v, [0n, 2n]));
  await d.view('total-supply', 'CVINVehicleNFT.totalSupply', nft.totalSupply(), 'supply unchanged by transfers', (v) => assert.equal(v, 2n));
  await d.view('no-royalty-on-nft', 'CVINVehicleNFT.supportsInterface', nft.supportsInterface(IFACE.ERC2981), 'the comparison contract has NO ERC-2981 royalty and no payment function', (v) => assert.equal(v, false));

  // ---- CVIN_NFT_DID_ERC721: royalties + toll with real ether ----
  const did = await (await ethers.getContractFactory('CVIN_NFT_DID_ERC721', deployer)).deploy('CVIN Vehicle DID', 'CVIN-DID', deployer.address, 250);
  await did.waitForDeployment();
  await did.mint(vehicleOwner.address, 1, 't.json');
  await d.view('royalty-info', 'CVIN_NFT_DID_ERC721.royaltyInfo', did.royaltyInfo(1, ethers.parseEther('40000')), 'ERC-2981: 250 bps of a 40000 ETH resale goes to the deployer (manufacturer resale royalty on a vehicle identity — advisory, enforced only by cooperating marketplaces)',
    (v) => { assert.equal(v[0], deployer.address); assert.equal(v[1], ethers.parseEther('1000')); });
  await d.tx('did-approve', 'CVIN_NFT_DID_ERC721.approve', did.connect(vehicleOwner).approve(operator.address, 1), 'OZ approve on the DID variant');
  await d.view('did-get-approved', 'CVIN_NFT_DID_ERC721.getApproved', did.getApproved(1), 'read back', (v) => assert.equal(v, operator.address));
  await d.tx('did-set-approval-for-all', 'CVIN_NFT_DID_ERC721.setApprovalForAll', did.connect(vehicleOwner).setApprovalForAll(operator.address, true), 'OZ operator approval');
  await d.view('did-is-approved-for-all', 'CVIN_NFT_DID_ERC721.isApprovedForAll', did.isApprovedForAll(vehicleOwner.address, operator.address), 'read back', (v) => assert.equal(v, true));
  await d.view('did-balance-of', 'CVIN_NFT_DID_ERC721.balanceOf', did.balanceOf(vehicleOwner.address), 'one identity held', (v) => assert.equal(v, 1n));

  const toll = ethers.parseEther('0.0125');
  const before = await ethers.provider.getBalance(deployer.address);
  const r3 = await d.tx('pay-toll', 'CVIN_NFT_DID_ERC721.payToll', did.connect(vehicleOwner).payToll(1, { value: toll }), 'identity-bound payment: only ownerOf(tokenId) may pay; 0.0125 ETH forwarded to owner() (toll operator) -> TollPaid');
  const tp = eventArgs(did, r3, 'TollPaid'); assert.equal(tp.payer, vehicleOwner.address); assert.equal(tp.amount, toll);
  const after = await ethers.provider.getBalance(deployer.address);
  assert.equal(after - before, toll);
  d.offchain('toll-received', 'CVIN_NFT_DID_ERC721.payToll', `operator balance grew by exactly ${ethers.formatEther(toll)} ETH (operator was not the tx sender, so no gas noise)`);
  await d.reverts('pay-toll-not-owner', 'CVIN_NFT_DID_ERC721.payToll', () => did.connect(stranger).payToll(1, { value: toll }), 'caller is not vehicle owner', 'the identity token authorises the payment');
  await d.reverts('pay-toll-zero', 'CVIN_NFT_DID_ERC721.payToll', () => did.connect(vehicleOwner).payToll(1, { value: 0 }), 'toll must be greater than zero', 'no zero-value settlement');
  await d.reverts('pay-toll-nonexistent', 'CVIN_NFT_DID_ERC721.payToll', () => did.connect(vehicleOwner).payToll(9, { value: toll }), 'ERC721NonexistentToken', 'ownerOf reverts');
  await d.tx('did-renounce', 'CVIN_NFT_DID_ERC721.renounceOwnership', did.connect(deployer).renounceOwnership(), 'operator renounces: owner() == address(0)');
  const zeroBefore = await ethers.provider.getBalance(ethers.ZeroAddress);
  await d.tx('pay-toll-after-renounce', 'CVIN_NFT_DID_ERC721.payToll', did.connect(vehicleOwner).payToll(1, { value: toll }), 'POTENTIAL DEFECT: payToll still succeeds after renounceOwnership and forwards the ether to address(0) (burned) — no owner()!=0 guard');
  assert.equal((await ethers.provider.getBalance(ethers.ZeroAddress)) - zeroBefore, toll);
  d.offchain('toll-burned', 'CVIN_NFT_DID_ERC721.payToll', `address(0) balance grew by ${ethers.formatEther(toll)} ETH: the vehicle paid a toll nobody can collect`);

  // ---- Monolithic: hand-rolled approvals + royalty ----
  const mono = await (await ethers.getContractFactory('CVIN_NFT_DID_ERC721_Monolithic', deployer)).deploy('CVIN Mono', 'MONO', deployer.address, 500);
  await mono.waitForDeployment();
  await mono.mint(vehicleOwner.address, 1, 'm.json');
  await mono.mint(vehicleOwner.address, 2, 'n.json');
  await d.view('mono-royalty-info', 'CVIN_NFT_DID_ERC721_Monolithic.royaltyInfo', mono.royaltyInfo(1, 10_000n), 'hand-rolled ERC-2981: 500 bps default (per-token override exists internally but has no public setter)', (v) => { assert.equal(v[0], deployer.address); assert.equal(v[1], 500n); });
  await d.reverts('mono-approve-owner', 'CVIN_NFT_DID_ERC721_Monolithic.approve', () => mono.connect(vehicleOwner).approve(vehicleOwner.address, 1), 'Approval to current owner', 'ERC-721 reference behaviour (OZ v5 dropped this check)');
  const r4 = await d.tx('mono-approve', 'CVIN_NFT_DID_ERC721_Monolithic.approve', mono.connect(vehicleOwner).approve(operator.address, 1), 'per-token approval -> Approval');
  assert.equal(eventArgs(mono, r4, 'Approval').approved, operator.address);
  await d.view('mono-get-approved', 'CVIN_NFT_DID_ERC721_Monolithic.getApproved', mono.getApproved(1), 'read back', (v) => assert.equal(v, operator.address));
  await d.reverts('mono-get-approved-nonexistent', 'CVIN_NFT_DID_ERC721_Monolithic.getApproved', () => mono.getApproved(9), 'Approved query for nonexistent token', 'existence check');
  await d.tx('mono-approved-transfer', 'CVIN_NFT_DID_ERC721_Monolithic.transferFrom', mono.connect(operator).transferFrom(vehicleOwner.address, newOwner.address, 1), 'approved party moves; _transfer clears the approval');
  await d.view('mono-approval-cleared', 'CVIN_NFT_DID_ERC721_Monolithic.getApproved', mono.getApproved(1), 'cleared', (v) => assert.equal(v, ethers.ZeroAddress));
  await d.reverts('mono-approve-self-operator', 'CVIN_NFT_DID_ERC721_Monolithic.setApprovalForAll', () => mono.connect(vehicleOwner).setApprovalForAll(vehicleOwner.address, true), 'Approve to caller', 'cannot be one\'s own operator');
  await d.tx('mono-set-approval-for-all', 'CVIN_NFT_DID_ERC721_Monolithic.setApprovalForAll', mono.connect(vehicleOwner).setApprovalForAll(operator.address, true), 'operator approval -> ApprovalForAll');
  await d.view('mono-is-approved-for-all', 'CVIN_NFT_DID_ERC721_Monolithic.isApprovedForAll', mono.isApprovedForAll(vehicleOwner.address, operator.address), 'read back', (v) => assert.equal(v, true));
  await d.tx('mono-operator-approve', 'CVIN_NFT_DID_ERC721_Monolithic.approve', mono.connect(operator).approve(stranger.address, 2), 'operator issues a per-token approval');
  await d.tx('mono-operator-transfer', 'CVIN_NFT_DID_ERC721_Monolithic.safeTransferFrom(address,address,uint256)', mono.connect(stranger)['safeTransferFrom(address,address,uint256)'](vehicleOwner.address, newOwner.address, 2), 'the per-token approvee moves vehicle 2');
  await d.view('mono-balances', 'CVIN_NFT_DID_ERC721_Monolithic.balanceOf', Promise.all([mono.balanceOf(vehicleOwner.address), mono.balanceOf(newOwner.address)]), 'balances after the moves', (v) => assert.deepEqual(v, [0n, 2n]));
  await d.reverts('mono-balance-zero-address', 'CVIN_NFT_DID_ERC721_Monolithic.balanceOf', () => mono.balanceOf(ethers.ZeroAddress), 'Balance query for the zero address', 'reference ERC-721 behaviour');
  d.offchain('mono-no-payments', 'CVIN_NFT_DID_ERC721_Monolithic', 'asymmetry: the Monolithic variant has royaltyInfo but NO toll/payment function');
});
