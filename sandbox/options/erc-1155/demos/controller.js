'use strict';
/**
 * ERC-1155 — family "Ownership / controller change" (manifest: implemented, not measured; the
 * comparison measures issuerTransferCredential(BIRTH_CERT) as "transfer"/"controller-change").
 * The identity is the holder ADDRESS, so a controller change means moving the soulbound
 * BIRTH_CERT to another address. This demo exercises the standard safeTransferFrom /
 * safeBatchTransferFrom paths under the soulbound _update override (holder-initiated transfers
 * revert; an ISSUER who is also an approved operator may use them), the receiver hook on contract
 * recipients, the issuer-mediated issuerTransferCredential with its VIN re-binding, and the
 * self-transfer guard added on 2026-10-04.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1155/demos/controller.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, deployEchoReceiver, VINS } = require('./_lib');

const d = demo('erc-1155', 'controller');

d.run(async () => {
  const [issuer, vehicleA, vehicleB, buyer, operator] = await ethers.getSigners();
  const { assert } = d;
  const c = await (await ethers.getContractFactory('CVINVehicleCredential1155', issuer)).deploy();
  await c.waitForDeployment();
  const vinHash = ethers.keccak256(ethers.toUtf8Bytes(VINS.vw));
  await c.registerVehicle(vehicleA.address, VINS.vw);
  await c.issueCredential(vehicleA.address, 3, 1); // INSPECTION_CERT
  await c.issueCredential(vehicleA.address, 5, 3); // MAINTENANCE_BADGE x3
  const receiver = await deployEchoReceiver(issuer);
  d.offchain('setup', 'CVINVehicleCredential1155.registerVehicle+issueCredential', `vehicle A holds BIRTH_CERT, INSPECTION_CERT and 3 MAINTENANCE_BADGEs; echo receiver at ${receiver.address}`);

  // ---- soulbound: holder cannot move its own credentials ----
  await d.reverts('holder-self-transfer', 'CVINVehicleCredential1155.safeTransferFrom', () => c.connect(vehicleA).safeTransferFrom(vehicleA.address, vehicleB.address, 1, 1, '0x'),
    'credentials are soulbound', 'the _update override blocks every holder-initiated transfer between non-zero addresses');
  await d.reverts('holder-self-batch-transfer', 'CVINVehicleCredential1155.safeBatchTransferFrom', () => c.connect(vehicleA).safeBatchTransferFrom(vehicleA.address, vehicleB.address, [3, 5], [1, 1], '0x'),
    'credentials are soulbound', 'batch path blocked identically');
  await d.tx('approve-operator', 'CVINVehicleCredential1155.setApprovalForAll', c.connect(vehicleA).setApprovalForAll(operator.address, true), 'holder names a (non-issuer) operator');
  await d.reverts('operator-transfer', 'CVINVehicleCredential1155.safeTransferFrom', () => c.connect(operator).safeTransferFrom(vehicleA.address, vehicleB.address, 5, 1, '0x'),
    'credentials are soulbound', 'OBSERVATION: an approved operator without ISSUER_ROLE still cannot move anything — ERC-1155 operator approval is inert on this option');

  // ---- standard path by an issuer: needs BOTH the role and the holder's approval ----
  await d.reverts('issuer-std-transfer-unapproved', 'CVINVehicleCredential1155.safeTransferFrom', () => c.connect(issuer).safeTransferFrom(vehicleA.address, vehicleB.address, 5, 1, '0x'),
    'ERC1155MissingApprovalForAll', 'the standard function first applies the ERC-1155 approval rule: the issuer is not the holder nor its operator');
  await d.tx('approve-issuer', 'CVINVehicleCredential1155.setApprovalForAll', c.connect(vehicleA).setApprovalForAll(issuer.address, true), 'holder approves the issuer as operator');
  const r1 = await d.tx('issuer-std-transfer', 'CVINVehicleCredential1155.safeTransferFrom', c.connect(issuer).safeTransferFrom(vehicleA.address, vehicleB.address, 5, 1, '0x'),
    'issuer (role + operator) moves one MAINTENANCE_BADGE via the STANDARD function -> TransferSingle');
  assert.equal(eventArgs(c, r1, 'TransferSingle').operator, issuer.address);
  await d.tx('issuer-std-batch-transfer', 'CVINVehicleCredential1155.safeBatchTransferFrom', c.connect(issuer).safeBatchTransferFrom(vehicleA.address, vehicleB.address, [3, 5], [1, 1], '0x'),
    'batch move of INSPECTION_CERT + another badge in one tx -> TransferBatch (note: vehicle B is NOT registered, yet it now holds credentials)');
  await d.view('balances-after-std', 'CVINVehicleCredential1155.balanceOfBatch', c.balanceOfBatch([vehicleA.address, vehicleA.address, vehicleB.address, vehicleB.address], [3, 5, 3, 5]), 'A: 0 inspection, 1 badge; B: 1 inspection, 2 badges', (v) => assert.deepEqual([...v], [0n, 1n, 1n, 2n]));
  await d.view('b-unregistered-but-credentialed', 'CVINVehicleCredential1155.isRegistered', c.isRegistered(vehicleB.address), 'OBSERVATION: standard transfers do not check that the recipient is a registered vehicle', (v) => assert.equal(v, false));
  await d.tx('std-transfer-to-contract', 'CVINVehicleCredential1155.safeTransferFrom', c.connect(issuer).safeTransferFrom(vehicleA.address, receiver.address, 5, 1, '0xc0ffee'),
    'contract recipient: OZ calls onERC1155Received and requires the selector back (echo receiver accepts)');
  const cAddr = await c.getAddress();
  await d.tx('approve-issuer-b', 'CVINVehicleCredential1155.setApprovalForAll', c.connect(vehicleB).setApprovalForAll(issuer.address, true), 'B approves the issuer as operator too');
  await d.reverts('std-transfer-to-non-receiver', 'CVINVehicleCredential1155.safeTransferFrom', () => c.connect(issuer).safeTransferFrom(vehicleB.address, cAddr, 5, 1, '0x'),
    'ERC1155InvalidReceiver', 'a contract without onERC1155Received (the registry itself) is refused by the receiver hook');

  // ---- standard transfer of the BIRTH_CERT does NOT re-bind the VIN (potential defect) ----
  await d.tx('std-transfer-birth-cert', 'CVINVehicleCredential1155.safeTransferFrom', c.connect(issuer).safeTransferFrom(vehicleA.address, buyer.address, 1, 1, '0x'),
    'POTENTIAL DEFECT: the identity token moves through the standard path, but vehicleVIN/vinHashToVehicle are only updated in issuerTransferCredential');
  await d.view('vin-desync', 'CVINVehicleCredential1155.vehicleVIN+vinHashToVehicle+isRegistered', Promise.all([c.vehicleVIN(buyer.address), c.vinHashToVehicle(vinHash), c.isRegistered(vehicleA.address), c.isRegistered(buyer.address)]),
    'buyer is "registered" (holds BIRTH_CERT) with an EMPTY VIN; the VIN index still points at A, which no longer holds anything',
    (v) => assert.deepEqual(v, ['', vehicleA.address, false, true]));
  await d.reverts('reregister-buyer-same-vin', 'CVINVehicleCredential1155.registerVehicle', () => c.connect(issuer).registerVehicle(buyer.address, VINS.vw), 'vehicle already registered', 'cannot repair the binding by re-registering');
  await d.tx('move-back-issuer-mediated', 'CVINVehicleCredential1155.issuerTransferCredential', c.connect(issuer).issuerTransferCredential(buyer.address, vehicleA.address, 1),
    'repair path: issuerTransferCredential re-binds vehicleVIN[to]=vehicleVIN[from] (empty!) and vinHashToVehicle[keccak("")]=A — the original VIN is NOT restored');
  await d.view('vin-after-repair', 'CVINVehicleCredential1155.vehicleVIN+vinHashToVehicle', Promise.all([c.vehicleVIN(vehicleA.address), c.vinHashToVehicle(vinHash), c.vinHashToVehicle(ethers.keccak256('0x'))]),
    'A holds the BIRTH_CERT again but with VIN ""; the real VIN hash still maps to A only by accident of the earlier state; keccak("") now also maps to A',
    (v) => assert.deepEqual(v, ['', vehicleA.address, vehicleA.address]));

  // ---- the measured path: issuer-mediated re-binding on a clean vehicle ----
  const c2 = await (await ethers.getContractFactory('CVINVehicleCredential1155', issuer)).deploy();
  await c2.waitForDeployment();
  await c2.registerVehicle(vehicleA.address, VINS.ford);
  await c2.issueCredential(vehicleA.address, 2, 1);
  const fordHash = ethers.keccak256(ethers.toUtf8Bytes(VINS.ford));
  d.offchain('setup-2', 'CVINVehicleCredential1155.registerVehicle', 'fresh registry: A holds BIRTH_CERT + REGISTRATION');
  await d.reverts('issuer-transfer-self', 'CVINVehicleCredential1155.issuerTransferCredential', () => c2.connect(issuer).issuerTransferCredential(vehicleA.address, vehicleA.address, 1),
    'transfer to same holder', 'self-transfer guard added 2026-10-04 (a from==to call used to delete the VIN mapping after re-writing it)');
  await d.reverts('issuer-transfer-nothing', 'CVINVehicleCredential1155.issuerTransferCredential', () => c2.connect(issuer).issuerTransferCredential(vehicleA.address, vehicleB.address, 4),
    'nothing to transfer', 'zero balance of that type');
  await d.reverts('issuer-transfer-unauthorised', 'CVINVehicleCredential1155.issuerTransferCredential', () => c2.connect(vehicleA).issuerTransferCredential(vehicleA.address, vehicleB.address, 1),
    'AccessControlUnauthorizedAccount', 'ISSUER_ROLE only; no holder approval needed on this path');
  const r2 = await d.tx('issuer-transfer-birth-cert', 'CVINVehicleCredential1155.issuerTransferCredential', c2.connect(issuer).issuerTransferCredential(vehicleA.address, buyer.address, 1),
    'MEASURED (transferOwnership/controller-change): BIRTH_CERT moves and vehicleVIN + vinHashToVehicle are re-bound to the buyer (identity address changes)');
  assert.equal(eventArgs(c2, r2, 'TransferSingle').to, buyer.address);
  await d.view('rebound', 'CVINVehicleCredential1155.vehicleVIN+vinHashToVehicle+isRegistered', Promise.all([c2.vehicleVIN(buyer.address), c2.vehicleVIN(vehicleA.address), c2.vinHashToVehicle(fordHash), c2.isRegistered(vehicleA.address)]),
    'buyer owns the VIN; A is cleared', (v) => assert.deepEqual(v, [VINS.ford, '', buyer.address, false]));
  await d.tx('issuer-transfer-registration', 'CVINVehicleCredential1155.issuerTransferCredential', c2.connect(issuer).issuerTransferCredential(vehicleA.address, buyer.address, 2),
    'other credential types move separately (whole balance of that type); the sale needs one tx per held type');
  await d.view('buyer-holdings', 'CVINVehicleCredential1155.balanceOfBatch', c2.balanceOfBatch([buyer.address, buyer.address], [1, 2]), 'buyer holds BIRTH_CERT + REGISTRATION', (v) => assert.deepEqual([...v], [1n, 1n]));
});
