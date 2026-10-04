'use strict';
/**
 * ERC-1155 — family "Lifecycle events / history" (manifest: implemented, not measured — the only
 * listed function is the RoleAdminChanged event). There is no on-chain history on this option:
 * balances are the only state. A vehicle's lifecycle must be REPLAYED from logs
 * (VehicleRegistered, CredentialIssued, CredentialRevoked, TransferSingle/TransferBatch,
 * RoleGranted/RoleRevoked). This demo builds that timeline and shows which facts the balances
 * alone cannot answer.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1155/demos/lifecycle-history.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, VINS } = require('./_lib');

const d = demo('erc-1155', 'lifecycle-history');

d.run(async () => {
  const [issuer, vehicleA, buyer, issuer2] = await ethers.getSigners();
  const { assert } = d;
  const c = await (await ethers.getContractFactory('CVINVehicleCredential1155', issuer)).deploy();
  await c.waitForDeployment();
  const ISSUER_ROLE = await c.ISSUER_ROLE();

  await d.tx('register', 'CVINVehicleCredential1155.registerVehicle', c.registerVehicle(vehicleA.address, VINS.volvo), 'lifecycle: birth');
  await d.tx('grant-issuer-2', 'CVINVehicleCredential1155.grantRole', c.grantRole(ISSUER_ROLE, issuer2.address), 'lifecycle: a second issuer appears (RoleGranted)');
  await d.tx('inspection-1', 'CVINVehicleCredential1155.issueCredential', c.connect(issuer2).issueCredential(vehicleA.address, 3, 1), 'lifecycle: inspection by issuer 2');
  await d.tx('insurance', 'CVINVehicleCredential1155.issueCredential', c.issueCredential(vehicleA.address, 4, 1), 'lifecycle: insurance');
  await d.tx('inspection-revoked', 'CVINVehicleCredential1155.revokeCredential', c.revokeCredential(vehicleA.address, 3, 1), 'lifecycle: inspection revoked by issuer 1');
  await d.tx('inspection-2', 'CVINVehicleCredential1155.issueCredential', c.connect(issuer2).issueCredential(vehicleA.address, 3, 1), 'lifecycle: re-inspection');
  await d.tx('sale', 'CVINVehicleCredential1155.issuerTransferCredential', c.issuerTransferCredential(vehicleA.address, buyer.address, 1), 'lifecycle: identity re-bound to the buyer');
  await d.tx('issuer-2-revoked', 'CVINVehicleCredential1155.revokeRole', c.revokeRole(ISSUER_ROLE, issuer2.address), 'lifecycle: issuer 2 loses its role (RoleRevoked)');

  await d.view('final-balances', 'CVINVehicleCredential1155.balanceOfBatch', c.balanceOfBatch([vehicleA.address, vehicleA.address, buyer.address, buyer.address], [3, 4, 1, 3]),
    'state after the story: A still holds the inspection+insurance (not moved with the birth cert), buyer holds only the identity', (v) => assert.deepEqual([...v], [1n, 1n, 1n, 0n]));

  const [reg, issued, revoked, single, batch, granted, roleRevoked, adminChanged] = await Promise.all([
    c.queryFilter(c.filters.VehicleRegistered(), 0, 'latest'),
    c.queryFilter(c.filters.CredentialIssued(), 0, 'latest'),
    c.queryFilter(c.filters.CredentialRevoked(), 0, 'latest'),
    c.queryFilter(c.filters.TransferSingle(), 0, 'latest'),
    c.queryFilter(c.filters.TransferBatch(), 0, 'latest'),
    c.queryFilter(c.filters.RoleGranted(), 0, 'latest'),
    c.queryFilter(c.filters.RoleRevoked(), 0, 'latest'),
    c.queryFilter(c.filters.RoleAdminChanged(), 0, 'latest'),
  ]);
  assert.equal(reg.length, 1); assert.equal(issued.length, 4); assert.equal(revoked.length, 1); assert.equal(single.length, 6); assert.equal(batch.length, 0);
  assert.equal(granted.length, 3); assert.equal(roleRevoked.length, 1); assert.equal(adminChanged.length, 0);
  d.offchain('replay-app-events', 'CVINVehicleCredential1155.VehicleRegistered+CredentialIssued+CredentialRevoked', `${reg.length} registration, ${issued.length} issuances (incl. the BIRTH_CERT), ${revoked.length} revocation — the app-level logs name the issuer, which balances do not`);
  d.offchain('replay-standard-events', 'CVINVehicleCredential1155.TransferSingle+TransferBatch', `${single.length} TransferSingle (mints/burn/sale), ${batch.length} TransferBatch — a generic ERC-1155 indexer sees the same story without the VIN`);
  d.offchain('replay-role-events', 'CVINVehicleCredential1155.RoleGranted+RoleRevoked+RoleAdminChanged', `${granted.length} RoleGranted (2 in the constructor), ${roleRevoked.length} RoleRevoked, ${adminChanged.length} RoleAdminChanged (declared, never emitted — the manifest's only "history" function)`);

  const timeline = [...reg.map((l) => ({ b: l.blockNumber, i: l.index, t: 'registered' })), ...issued.filter((l) => l.args.credentialType !== 1n).map((l) => ({ b: l.blockNumber, i: l.index, t: `issued(type=${l.args.credentialType},by=${l.args.issuer === issuer2.address ? 'issuer2' : 'issuer1'})` })),
    ...revoked.map((l) => ({ b: l.blockNumber, i: l.index, t: `revoked(type=${l.args.credentialType})` })), ...single.filter((l) => l.args.from !== ethers.ZeroAddress && l.args.to !== ethers.ZeroAddress).map((l) => ({ b: l.blockNumber, i: l.index, t: `moved(type=${l.args.id})` })),
    ...roleRevoked.map((l) => ({ b: l.blockNumber, i: l.index, t: 'issuer2-revoked' }))].sort((a, b) => a.b - b.b || a.i - b.i).map((x) => x.t);
  assert.deepEqual(timeline, ['registered', 'issued(type=3,by=issuer2)', 'issued(type=4,by=issuer1)', 'revoked(type=3)', 'issued(type=3,by=issuer2)', 'moved(type=1)', 'issuer2-revoked']);
  d.offchain('timeline', 'CVINVehicleCredential1155 (logs)', `reconstructed: ${timeline.join(' -> ')}`);
  d.offchain('unanswerable-from-state', 'CVINVehicleCredential1155', 'from balances alone a verifier cannot tell that the current inspection was issued by a since-revoked issuer, nor when; the chain stores no timestamps or issuer per credential');
});
