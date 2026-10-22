'use strict';
/**
 * ERC-1155 — family "Ownership / controller change" (manifest: implemented, not measured; the
 * comparison measures issuerTransferCredential(BIRTH_CERT) on a vehicle holding nothing else as
 * "transfer"/"controller-change").
 * The identity is the holder ADDRESS, so a controller change means moving the soulbound
 * BIRTH_CERT to another address. Since the D7/D8 fix (2026-10-04) the standard safeTransferFrom /
 * safeBatchTransferFrom entry points revert for EVERYONE (holder, approved operator, issuer-as-
 * operator), so the only inter-address moves are the two issuer paths: issuerTransferCredential
 * (one type; non-BIRTH types only to a registered vehicle, the BIRTH_CERT only when the vehicle
 * holds nothing else) and the new issuerTransferIdentity (BIRTH_CERT + every held type in one
 * TransferBatch, VIN indexes re-bound, IdentityRebound event). This demo asserts both fixes,
 * exercises credentialTypesOf / MAX_CREDENTIAL_TYPE, the receiver hook on the issuer path, the
 * reverts of both issuer functions and the self-transfer guard added on 2026-10-04.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1155/demos/controller.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, eventCount, deployEchoReceiver, VINS } = require('./_lib');

const d = demo('erc-1155', 'controller');
const SOULBOUND = 'credentials are soulbound';

d.run(async () => {
  const [issuer, vehicleA, vehicleB, buyer, operator] = await ethers.getSigners();
  const { assert } = d;
  const c = await (await ethers.getContractFactory('CVINVehicleCredential1155', issuer)).deploy();
  await c.waitForDeployment();
  const cAddr = await c.getAddress();
  const vinHash = ethers.keccak256(ethers.toUtf8Bytes(VINS.vw));
  await c.registerVehicle(vehicleA.address, VINS.vw);
  await c.issueCredential(vehicleA.address, 3, 1); // INSPECTION_CERT
  await c.issueCredential(vehicleA.address, 5, 3); // MAINTENANCE_BADGE x3
  const receiver = await deployEchoReceiver(issuer);
  d.offchain('setup', 'CVINVehicleCredential1155.registerVehicle+issueCredential', `vehicle A holds BIRTH_CERT, INSPECTION_CERT and 3 MAINTENANCE_BADGEs; echo receiver at ${receiver.address}`);

  // ---- soulbound: holder cannot move its own credentials ----
  await d.reverts('holder-self-transfer', 'CVINVehicleCredential1155.safeTransferFrom', () => c.connect(vehicleA).safeTransferFrom(vehicleA.address, vehicleB.address, 1, 1, '0x'),
    SOULBOUND, 'the overridden entry point blocks every holder-initiated transfer');
  await d.reverts('holder-self-batch-transfer', 'CVINVehicleCredential1155.safeBatchTransferFrom', () => c.connect(vehicleA).safeBatchTransferFrom(vehicleA.address, vehicleB.address, [3, 5], [1, 1], '0x'),
    SOULBOUND, 'batch path blocked identically');
  await d.tx('approve-operator', 'CVINVehicleCredential1155.setApprovalForAll', c.connect(vehicleA).setApprovalForAll(operator.address, true), 'holder names a (non-issuer) operator');
  await d.reverts('operator-transfer', 'CVINVehicleCredential1155.safeTransferFrom', () => c.connect(operator).safeTransferFrom(vehicleA.address, vehicleB.address, 5, 1, '0x'),
    SOULBOUND, 'OBSERVATION: an approved operator without ISSUER_ROLE cannot move anything — ERC-1155 operator approval is inert on this option');

  // ---- the standard path is closed for issuers too (FIXED D7) ----
  await d.reverts('issuer-std-transfer-closed', 'CVINVehicleCredential1155.safeTransferFrom', () => c.connect(issuer).safeTransferFrom(vehicleA.address, vehicleB.address, 5, 1, '0x'),
    SOULBOUND, 'FIXED (D7): the issuer without operator approval is refused with the soulbound reason (before the fix the ERC-1155 approval rule ran first and reverted ERC1155MissingApprovalForAll)');
  await d.tx('approve-issuer', 'CVINVehicleCredential1155.setApprovalForAll', c.connect(vehicleA).setApprovalForAll(issuer.address, true), 'holder approves the issuer as operator (the pre-fix precondition for the issuer-as-operator path)');
  await d.reverts('issuer-std-transfer-approved', 'CVINVehicleCredential1155.safeTransferFrom', () => c.connect(issuer).safeTransferFrom(vehicleA.address, vehicleB.address, 5, 1, '0x'),
    SOULBOUND, 'FIXED (D7): role + operator approval no longer opens the STANDARD function (it used to move a badge with a TransferSingle)');
  await d.reverts('issuer-std-batch-transfer-approved', 'CVINVehicleCredential1155.safeBatchTransferFrom', () => c.connect(issuer).safeBatchTransferFrom(vehicleA.address, vehicleB.address, [3, 5], [1, 1], '0x'),
    SOULBOUND, 'FIXED (D7): the batch entry point is closed the same way (it used to deliver credentials to the unregistered vehicle B)');
  await d.view('balances-unchanged', 'CVINVehicleCredential1155.balanceOfBatch', c.balanceOfBatch([vehicleA.address, vehicleA.address, vehicleB.address, vehicleB.address], [3, 5, 3, 5]), 'A still holds 1 inspection + 3 badges; B holds nothing', (v) => assert.deepEqual([...v], [1n, 3n, 0n, 0n]));
  await d.view('b-unregistered-holds-nothing', 'CVINVehicleCredential1155.isRegistered+credentialTypesOf', Promise.all([c.isRegistered(vehicleB.address), c.credentialTypesOf(vehicleB.address)]),
    'FIXED (D8): no credential can reach an unregistered address any more (invariant i: a non-BIRTH credential is only ever held by a registered vehicle)', (v) => { assert.equal(v[0], false); assert.deepEqual([...v[1]], []); });
  await d.reverts('std-transfer-to-contract-closed', 'CVINVehicleCredential1155.safeTransferFrom', () => c.connect(issuer).safeTransferFrom(vehicleA.address, receiver.address, 5, 1, '0xc0ffee'),
    SOULBOUND, 'FIXED (D7): even a contract recipient with a valid onERC1155Received is unreachable through the standard function — its receiver hook is never consulted');

  // ---- receiver hook on the issuer path: contract recipients still need onERC1155Received ----
  await d.reverts('issuer-transfer-to-unregistered-contract', 'CVINVehicleCredential1155.issuerTransferCredential', () => c.connect(issuer).issuerTransferCredential(vehicleA.address, receiver.address, 5),
    'recipient not registered', 'FIXED (D8): a non-BIRTH credential may only go to a registered vehicle — the (unregistered) receiver contract is refused before any hook runs');
  await d.tx('register-receiver-contract', 'CVINVehicleCredential1155.registerVehicle', c.connect(issuer).registerVehicle(receiver.address, VINS.bmw), 'a contract address can be a vehicle (registerVehicle mints to it; OZ _mint calls onERC1155Received, the echo receiver accepts)');
  const r1 = await d.tx('issuer-transfer-to-receiver-contract', 'CVINVehicleCredential1155.issuerTransferCredential', c.connect(issuer).issuerTransferCredential(vehicleA.address, receiver.address, 5),
    'the issuer path uses the internal _safeTransferFrom: OZ calls onERC1155Received on the contract recipient and requires the selector back (echo receiver accepts) -> TransferSingle(operator=issuer)');
  assert.equal(eventArgs(c, r1, 'TransferSingle').operator, issuer.address);
  assert.equal(eventArgs(c, r1, 'TransferSingle').value, 3n);
  await d.view('receiver-holdings', 'CVINVehicleCredential1155.balanceOf+credentialTypesOf', Promise.all([c.balanceOf(receiver.address, 5), c.credentialTypesOf(receiver.address), c.credentialTypesOf(vehicleA.address)]),
    'all 3 badges moved (whole balance of the type); the held-type bitmaps follow: receiver [5], A [3]', (v) => { assert.equal(v[0], 3n); assert.deepEqual([...v[1]], [5n]); assert.deepEqual([...v[2]], [3n]); });
  await d.reverts('identity-transfer-to-non-receiver', 'CVINVehicleCredential1155.issuerTransferIdentity', () => c.connect(issuer).issuerTransferIdentity(vehicleA.address, cAddr),
    'ERC1155InvalidReceiver', 'a contract without onERC1155BatchReceived (the registry itself) is refused by the receiver hook on the identity path too');

  // ---- the BIRTH_CERT cannot leave through the standard path; issuerTransferIdentity re-binds (FIXED D7) ----
  await d.reverts('std-transfer-birth-cert', 'CVINVehicleCredential1155.safeTransferFrom', () => c.connect(issuer).safeTransferFrom(vehicleA.address, buyer.address, 1, 1, '0x'),
    SOULBOUND, 'FIXED (D7): the identity token can no longer move through the standard path (it used to, leaving vehicleVIN/vinHashToVehicle pointing at the old holder)');
  await d.view('vin-intact', 'CVINVehicleCredential1155.vehicleVIN+vinHashToVehicle+isRegistered', Promise.all([c.vehicleVIN(vehicleA.address), c.vinHashToVehicle(vinHash), c.isRegistered(vehicleA.address), c.isRegistered(buyer.address)]),
    'nothing desynchronised: A still owns the VIN, the index still points at A, the buyer is not registered', (v) => assert.deepEqual(v, [VINS.vw, vehicleA.address, true, false]));
  await d.tx('issue-registration', 'CVINVehicleCredential1155.issueCredential', c.connect(issuer).issueCredential(vehicleA.address, 2, 1), 'A now holds BIRTH_CERT + REGISTRATION + INSPECTION_CERT (two non-BIRTH types to carry along)');
  await d.view('credential-types-before', 'CVINVehicleCredential1155.credentialTypesOf', Promise.all([c.credentialTypesOf(vehicleA.address), c.credentialTypesOf(buyer.address)]),
    'bitmap-backed enumeration of the held non-BIRTH types (ascending): A [2,3], buyer []', (v) => { assert.deepEqual([...v[0]], [2n, 3n]); assert.deepEqual([...v[1]], []); });
  await d.view('max-credential-type', 'CVINVehicleCredential1155.MAX_CREDENTIAL_TYPE', c.MAX_CREDENTIAL_TYPE(), 'FIXED (D8): credential types are bounded to 1..255 so the held set fits one 256-bit word and can be moved atomically', (v) => assert.equal(v, 255n));

  await d.reverts('identity-transfer-unauthorised', 'CVINVehicleCredential1155.issuerTransferIdentity', () => c.connect(vehicleA).issuerTransferIdentity(vehicleA.address, buyer.address),
    'AccessControlUnauthorizedAccount', 'ISSUER_ROLE only — the holder cannot re-home its own identity');
  await d.reverts('identity-transfer-self', 'CVINVehicleCredential1155.issuerTransferIdentity', () => c.connect(issuer).issuerTransferIdentity(vehicleA.address, vehicleA.address),
    'transfer to same holder', 'self-transfer guard (same rule as issuerTransferCredential)');
  await d.reverts('identity-transfer-zero', 'CVINVehicleCredential1155.issuerTransferIdentity', () => c.connect(issuer).issuerTransferIdentity(vehicleA.address, ethers.ZeroAddress),
    'recipient is zero address', 'no re-binding to address(0)');
  await d.reverts('identity-transfer-unregistered-source', 'CVINVehicleCredential1155.issuerTransferIdentity', () => c.connect(issuer).issuerTransferIdentity(vehicleB.address, buyer.address),
    'vehicle not registered', 'B holds no BIRTH_CERT: there is no identity to move');
  await d.reverts('identity-transfer-to-registered', 'CVINVehicleCredential1155.issuerTransferIdentity', () => c.connect(issuer).issuerTransferIdentity(vehicleA.address, receiver.address),
    'recipient already registered', 'the recipient must be a fresh address (one BIRTH_CERT per address)');
  const r2 = await d.tx('identity-transfer', 'CVINVehicleCredential1155.issuerTransferIdentity', c.connect(issuer).issuerTransferIdentity(vehicleA.address, buyer.address),
    'FIXED (D7): BIRTH_CERT + REGISTRATION + INSPECTION_CERT move to the buyer in ONE TransferBatch, vehicleVIN/vinHashToVehicle are re-bound, IdentityRebound(from,to,vinHash,2) is emitted');
  const rb = eventArgs(c, r2, 'IdentityRebound');
  assert.equal(rb.from, vehicleA.address); assert.equal(rb.to, buyer.address); assert.equal(rb.vinHash, vinHash); assert.equal(rb.credentialTypesMoved, 2n);
  const tb = eventArgs(c, r2, 'TransferBatch');
  assert.deepEqual([...tb.ids], [1n, 2n, 3n]); assert.deepEqual([...tb[4]], [1n, 1n, 1n]); /* tb[4] = values ("values" collides with Result.prototype.values) */ assert.equal(tb.operator, issuer.address); assert.equal(tb.to, buyer.address);
  assert.equal(eventCount(c, r2, 'TransferSingle'), 0);
  d.offchain('identity-transfer-events', 'CVINVehicleCredential1155.IdentityRebound+TransferBatch', `IdentityRebound(from=A, to=buyer, vinHash=${vinHash.slice(0, 10)}…, credentialTypesMoved=2) + one TransferBatch(ids=[1,2,3], values=[1,1,1]) and no TransferSingle: a generic indexer sees the whole sale as one event`);
  await d.view('credential-types-after', 'CVINVehicleCredential1155.credentialTypesOf', Promise.all([c.credentialTypesOf(vehicleA.address), c.credentialTypesOf(buyer.address)]),
    'the bitmaps followed the batch: A [], buyer [2,3]', (v) => { assert.deepEqual([...v[0]], []); assert.deepEqual([...v[1]], [2n, 3n]); });
  await d.view('balances-after-identity-transfer', 'CVINVehicleCredential1155.balanceOfBatch', c.balanceOfBatch([buyer.address, buyer.address, buyer.address, vehicleA.address, vehicleA.address, vehicleA.address], [1, 2, 3, 1, 2, 3]),
    'buyer holds everything A held; A holds nothing', (v) => assert.deepEqual([...v], [1n, 1n, 1n, 0n, 0n, 0n]));
  await d.view('rebound-indexes', 'CVINVehicleCredential1155.vehicleVIN+vinHashToVehicle+isRegistered+vehicleForVIN', Promise.all([c.vehicleVIN(buyer.address), c.vehicleVIN(vehicleA.address), c.vinHashToVehicle(vinHash), c.isRegistered(vehicleA.address), c.isRegistered(buyer.address), c.vehicleForVIN(VINS.vw), c.vinHashToVehicle(ethers.keccak256('0x'))]),
    'FIXED (D7): buyer owns the VIN, A is cleared, the VIN hash and vehicleForVIN point at the buyer, and keccak("") maps to nobody (the pre-fix repair path aliased it)',
    (v) => assert.deepEqual(v, [VINS.vw, '', buyer.address, false, true, buyer.address, ethers.ZeroAddress]));
  await d.reverts('reregister-a-same-vin', 'CVINVehicleCredential1155.registerVehicle', () => c.connect(issuer).registerVehicle(vehicleA.address, VINS.vw), 'VIN already registered', 'the old address is free again but the VIN is still bound (to the buyer): the uniqueness index stayed coherent through the move');

  // ---- the measured path: one-type moves and the bare BIRTH_CERT re-binding ----
  const c2 = await (await ethers.getContractFactory('CVINVehicleCredential1155', issuer)).deploy();
  await c2.waitForDeployment();
  await c2.registerVehicle(vehicleA.address, VINS.ford);
  await c2.registerVehicle(vehicleB.address, VINS.honda);
  await c2.issueCredential(vehicleA.address, 2, 1);
  const fordHash = ethers.keccak256(ethers.toUtf8Bytes(VINS.ford));
  d.offchain('setup-2', 'CVINVehicleCredential1155.registerVehicle+issueCredential', 'fresh registry: A holds BIRTH_CERT + REGISTRATION; B holds a BIRTH_CERT (second registered vehicle); buyer and operator are unregistered');
  await d.reverts('issuer-transfer-self', 'CVINVehicleCredential1155.issuerTransferCredential', () => c2.connect(issuer).issuerTransferCredential(vehicleA.address, vehicleA.address, 1),
    'transfer to same holder', 'self-transfer guard added 2026-10-04 (a from==to call used to delete the VIN mapping after re-writing it)');
  await d.reverts('issuer-transfer-nothing', 'CVINVehicleCredential1155.issuerTransferCredential', () => c2.connect(issuer).issuerTransferCredential(vehicleA.address, vehicleB.address, 4),
    'nothing to transfer', 'zero balance of that type');
  await d.reverts('issuer-transfer-unauthorised', 'CVINVehicleCredential1155.issuerTransferCredential', () => c2.connect(vehicleA).issuerTransferCredential(vehicleA.address, vehicleB.address, 1),
    'AccessControlUnauthorizedAccount', 'ISSUER_ROLE only; no holder approval needed on this path');
  await d.reverts('issuer-transfer-birth-cert-with-credentials', 'CVINVehicleCredential1155.issuerTransferCredential', () => c2.connect(issuer).issuerTransferCredential(vehicleA.address, buyer.address, 1),
    'identity holds other credentials', 'FIXED (D8): the BIRTH_CERT may not leave on its own while A still holds REGISTRATION (invariant ii: no orphaned credentials on a non-vehicle address) — use issuerTransferIdentity');
  await d.reverts('issuer-transfer-registration-unregistered', 'CVINVehicleCredential1155.issuerTransferCredential', () => c2.connect(issuer).issuerTransferCredential(vehicleA.address, buyer.address, 2),
    'recipient not registered', 'FIXED (D8): a single non-BIRTH type can only move to a registered vehicle');
  const r3 = await d.tx('identity-transfer-2', 'CVINVehicleCredential1155.issuerTransferIdentity', c2.connect(issuer).issuerTransferIdentity(vehicleA.address, buyer.address),
    'the whole identity (BIRTH_CERT + REGISTRATION) moves to the buyer atomically; not benchmarked — its cost grows with the number of held types');
  assert.equal(eventArgs(c2, r3, 'IdentityRebound').credentialTypesMoved, 1n);
  await d.view('rebound-2', 'CVINVehicleCredential1155.vehicleVIN+vinHashToVehicle+isRegistered', Promise.all([c2.vehicleVIN(buyer.address), c2.vehicleVIN(vehicleA.address), c2.vinHashToVehicle(fordHash), c2.isRegistered(vehicleA.address)]),
    'buyer owns the VIN; A is cleared', (v) => assert.deepEqual(v, [VINS.ford, '', buyer.address, false]));
  await d.tx('issuer-transfer-registration', 'CVINVehicleCredential1155.issuerTransferCredential', c2.connect(issuer).issuerTransferCredential(buyer.address, vehicleB.address, 2),
    'one credential type moves separately between two REGISTERED vehicles (whole balance of that type); non-BIRTH types do not touch the VIN maps');
  await d.view('buyer-bare', 'CVINVehicleCredential1155.credentialTypesOf+balanceOfBatch', Promise.all([c2.credentialTypesOf(buyer.address), c2.balanceOfBatch([buyer.address, vehicleB.address], [2, 2])]),
    'buyer now holds only its BIRTH_CERT; B holds the REGISTRATION', (v) => { assert.deepEqual([...v[0]], []); assert.deepEqual([...v[1]], [0n, 1n]); });
  await d.reverts('issuer-transfer-birth-cert-to-registered', 'CVINVehicleCredential1155.issuerTransferCredential', () => c2.connect(issuer).issuerTransferCredential(buyer.address, vehicleB.address, 1),
    'recipient already registered', 'a BIRTH_CERT cannot land on an address that already is a vehicle');
  const r4 = await d.tx('issuer-transfer-birth-cert', 'CVINVehicleCredential1155.issuerTransferCredential', c2.connect(issuer).issuerTransferCredential(buyer.address, operator.address, 1),
    'MEASURED (transferOwnership/controller-change): the bare BIRTH_CERT moves (TransferSingle) and vehicleVIN + vinHashToVehicle are re-bound to the new address (identity address changes)');
  assert.equal(eventArgs(c2, r4, 'TransferSingle').to, operator.address);
  await d.view('rebound-single', 'CVINVehicleCredential1155.vehicleVIN+vinHashToVehicle+isRegistered', Promise.all([c2.vehicleVIN(operator.address), c2.vehicleVIN(buyer.address), c2.vinHashToVehicle(fordHash), c2.isRegistered(buyer.address), c2.isRegistered(operator.address)]),
    'the new address owns the VIN; the buyer is cleared', (v) => assert.deepEqual(v, [VINS.ford, '', operator.address, false, true]));
});
