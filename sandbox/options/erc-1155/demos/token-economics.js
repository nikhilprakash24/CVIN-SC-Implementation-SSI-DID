'use strict';
/**
 * ERC-1155 — family "Token economics (approvals, royalties, payments)" (manifest: implemented, not
 * measured). The ERC-1155 balance/approval surface: balanceOf, balanceOfBatch (incl. its
 * length-mismatch and zero-address guards), setApprovalForAll / isApprovedForAll and what an
 * operator approval is worth under the soulbound entry points (nothing: since the D7 fix the
 * standard transfer functions revert for everyone, issuers included). No royalties and no
 * payments exist on this option.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1155/demos/token-economics.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS, IFACE } = require('./_lib');

const d = demo('erc-1155', 'token-economics');

d.run(async () => {
  const [issuer, vehicleA, vehicleB, operator] = await ethers.getSigners();
  const { assert } = d;
  const c = await (await ethers.getContractFactory('CVINVehicleCredential1155', issuer)).deploy();
  await c.waitForDeployment();
  await c.registerVehicle(vehicleA.address, VINS.ford);
  await c.registerVehicle(vehicleB.address, VINS.tesla);
  await c.issueCredential(vehicleA.address, 5, 3);
  d.offchain('setup', 'CVINVehicleCredential1155.registerVehicle+issueCredential', 'A: BIRTH_CERT + 3 badges; B: BIRTH_CERT');

  await d.view('balance-of', 'CVINVehicleCredential1155.balanceOf', c.balanceOf(vehicleA.address, 5), 'fungible balance per (address, type)', (v) => assert.equal(v, 3n));
  await d.view('balance-of-batch', 'CVINVehicleCredential1155.balanceOfBatch', c.balanceOfBatch([vehicleA.address, vehicleA.address, vehicleB.address, vehicleB.address], [1, 5, 1, 5]), 'ERC-1155 batch read across addresses and types in one call', (v) => assert.deepEqual([...v], [1n, 3n, 1n, 0n]));
  await d.reverts('balance-of-batch-mismatch', 'CVINVehicleCredential1155.balanceOfBatch', () => c.balanceOfBatch([vehicleA.address], [1, 5]), 'ERC1155InvalidArrayLength', 'arrays must align');
  await d.view('balance-of-zero-address', 'CVINVehicleCredential1155.balanceOf', c.balanceOf(ethers.ZeroAddress, 1), 'OBSERVATION: OZ 5.x balanceOf returns 0 for address(0) instead of reverting as the ERC-1155 text requires', (v) => assert.equal(v, 0n));
  const r = await d.tx('set-approval-for-all', 'CVINVehicleCredential1155.setApprovalForAll', c.connect(vehicleA).setApprovalForAll(operator.address, true), 'standard operator approval -> ApprovalForAll');
  assert.equal(eventArgs(c, r, 'ApprovalForAll').approved, true);
  await d.view('is-approved-for-all', 'CVINVehicleCredential1155.isApprovedForAll', c.isApprovedForAll(vehicleA.address, operator.address), 'readable', (v) => assert.equal(v, true));
  await d.reverts('operator-cannot-move', 'CVINVehicleCredential1155.safeTransferFrom', () => c.connect(operator).safeTransferFrom(vehicleA.address, vehicleB.address, 5, 1, '0x'), 'credentials are soulbound', 'the overridden safeTransferFrom reverts before the ERC-1155 approval rule is even consulted (D7: closed for holders, operators and issuers alike): approvals have no economic effect here');
  await d.reverts('approve-zero-operator', 'CVINVehicleCredential1155.setApprovalForAll', () => c.connect(vehicleA).setApprovalForAll(ethers.ZeroAddress, true), 'ERC1155InvalidOperator', 'the only operator OZ 5.x rejects is address(0)');
  await d.tx('approve-self', 'CVINVehicleCredential1155.setApprovalForAll', c.connect(vehicleA).setApprovalForAll(vehicleA.address, true), 'OBSERVATION: OZ 5.x accepts a self-approval (the ERC-721 Monolithic variant rejects "Approve to caller"); harmless here because approvals are inert');
  await d.tx('clear-approval', 'CVINVehicleCredential1155.setApprovalForAll', c.connect(vehicleA).setApprovalForAll(operator.address, false), 'approval cleared');
  await d.view('no-royalty', 'CVINVehicleCredential1155.supportsInterface', c.supportsInterface(IFACE.ERC2981), 'no ERC-2981, no payable function: the credentials carry no economics (asymmetry vs ERC-721 DID variants)', (v) => assert.equal(v, false));
  d.offchain('no-market', 'CVINVehicleCredential1155', 'asymmetry: soulbound credentials cannot be traded, so approvals/royalties/payments are structurally absent — the only "economics" is the issuer paying gas');
});
