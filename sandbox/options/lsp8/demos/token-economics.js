'use strict';
/**
 * LSP8 — family "Token economics (approvals, royalties, payments)" (manifest: implemented via
 * balanceOf / totalSupply only). This representative LSP8 implements no operators
 * (authorizeOperator / revokeOperator / isOperatorFor / getOperatorsOf are absent), no royalties
 * and no payments; the economic surface is the supply/balance bookkeeping across mint, transfer
 * and burn, demonstrated here together with proof that the operator functions do not exist.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/lsp8/demos/token-economics.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, VINS } = require('./_lib');

const d = demo('lsp8', 'token-economics');

d.run(async () => {
  const [authority, vehicleOwner, buyer, operator] = await ethers.getSigners();
  const { assert } = d;
  const c = await (await ethers.getContractFactory('CVINVehicleLSP8', authority)).deploy('CVIN Vehicle Identity LSP8', 'CVIN-LSP8');
  await c.waitForDeployment();
  await d.view('supply-0', 'CVINVehicleLSP8.totalSupply', c.totalSupply(), 'empty collection', (v) => assert.equal(v, 0n));
  await d.view('balance-0', 'CVINVehicleLSP8.balanceOf', c.balanceOf(vehicleOwner.address), 'no identities held', (v) => assert.equal(v, 0n));
  await d.tx('mint-1', 'CVINVehicleLSP8.mintVehicle', c.mintVehicle(vehicleOwner.address, VINS.acura), 'supply +1');
  await d.tx('mint-2', 'CVINVehicleLSP8.mintVehicle', c.mintVehicle(vehicleOwner.address, VINS.hyundai), 'supply +1');
  await d.view('supply-2', 'CVINVehicleLSP8.totalSupply', c.totalSupply(), 'two identities', (v) => assert.equal(v, 2n));
  await d.view('balance-2', 'CVINVehicleLSP8.balanceOf', c.balanceOf(vehicleOwner.address), 'balanceOf == tokenIdsOf(owner).length', (v) => assert.equal(v, 2n));
  const t1 = await c.tokenIdForVIN(VINS.acura);
  await d.tx('transfer', 'CVINVehicleLSP8.transfer', c.connect(vehicleOwner).transfer(vehicleOwner.address, buyer.address, t1, true, '0x'), 'a transfer moves a balance unit, supply unchanged');
  await d.view('balances-after-transfer', 'CVINVehicleLSP8.balanceOf', Promise.all([c.balanceOf(vehicleOwner.address), c.balanceOf(buyer.address), c.totalSupply()]), '1 / 1 / 2', (v) => assert.deepEqual(v, [1n, 1n, 2n]));
  await d.tx('burn', 'CVINVehicleLSP8.revokeVehicle', c.revokeVehicle(t1, '0x'), 'a burn decrements supply and the holder balance');
  await d.view('balances-after-burn', 'CVINVehicleLSP8.balanceOf', Promise.all([c.balanceOf(buyer.address), c.totalSupply()]), '0 / 1', (v) => assert.deepEqual(v, [0n, 1n]));
  await d.view('balance-zero-address', 'CVINVehicleLSP8.balanceOf', c.balanceOf(ethers.ZeroAddress), 'no revert for address(0) (0)', (v) => assert.equal(v, 0n));
  assert.equal(c.interface.hasFunction('authorizeOperator(address,bytes32,bytes)'), false);
  assert.equal(c.interface.hasFunction('revokeOperator(address,bytes32,bool,bytes)'), false);
  assert.equal(c.interface.hasFunction('isOperatorFor(address,bytes32)'), false);
  assert.equal(c.interface.hasFunction('getOperatorsOf(bytes32)'), false);
  d.offchain('no-operators', 'CVINVehicleLSP8 (ABI)', 'LSP8 operator functions authorizeOperator/revokeOperator/isOperatorFor/getOperatorsOf are NOT in the ABI: no delegated transfers, no marketplace pattern (why the manifest marks keys/delegates not-applicable)');
  const t2 = await c.tokenIdForVIN(VINS.hyundai);
  await d.reverts('operator-cannot-move', 'CVINVehicleLSP8.transfer', () => c.connect(operator).transfer(vehicleOwner.address, buyer.address, t2, true, '0x'), 'caller is not the token owner', 'confirms: only the token owner moves it');
  assert.equal(c.interface.hasFunction('royaltyInfo(uint256,uint256)'), false);
  d.offchain('no-royalties-no-payments', 'CVINVehicleLSP8 (ABI)', 'no ERC-2981 royaltyInfo and no payable function: the identity carries no economics (asymmetry vs the ERC-721 DID variants)');
});
