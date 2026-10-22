'use strict';
/**
 * ERC-1155 — family "Claims / credentials" (manifest: measured-in-comparison via issueCredential
 * and revokeCredential). A claim is a fungible credential-type balance minted by an ISSUER_ROLE
 * holder: no issuer signature, no subject, no data on-chain beyond (address, type, amount).
 * Exercises issueCredential (single and multi-unit), hasCredential, every credential type, the
 * BIRTH_CERT exclusion, the 1..255 type range (MAX_CREDENTIAL_TYPE, D8) and credentialTypesOf,
 * issuerTransferCredential of a credential (registered recipients only, D8), revokeCredential and
 * the ISSUER_ROLE / INSPECTION_CERT constants.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1155/demos/claims.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('erc-1155', 'claims');

d.run(async () => {
  const [issuer, vehicleA, vehicleB, inspector] = await ethers.getSigners();
  const { assert } = d;
  const c = await (await ethers.getContractFactory('CVINVehicleCredential1155', issuer)).deploy();
  await c.waitForDeployment();
  await c.registerVehicle(vehicleA.address, VINS.hyundai);
  d.offchain('setup', 'CVINVehicleCredential1155.registerVehicle', 'vehicle A registered');

  const [ISSUER_ROLE, INSPECTION_CERT] = await Promise.all([c.ISSUER_ROLE(), c.INSPECTION_CERT()]);
  await d.view('constants', 'CVINVehicleCredential1155.ISSUER_ROLE+INSPECTION_CERT', Promise.resolve([ISSUER_ROLE, INSPECTION_CERT]), 'issuer role id and the inspection credential type', (v) => { assert.equal(v[0], ethers.id('ISSUER_ROLE')); assert.equal(v[1], 3n); });
  await d.view('has-credential-before', 'CVINVehicleCredential1155.hasCredential', c.hasCredential(vehicleA.address, INSPECTION_CERT), 'no inspection yet', (v) => assert.equal(v, false));

  const r1 = await d.tx('issue-inspection', 'CVINVehicleCredential1155.issueCredential', c.connect(issuer).issueCredential(vehicleA.address, INSPECTION_CERT, 1),
    'MEASURED (addDelegateOrClaim): mint 1 INSPECTION_CERT -> CredentialIssued + TransferSingle; the chain records WHO issued, not what was inspected');
  const ev = eventArgs(c, r1, 'CredentialIssued'); assert.equal(ev.issuer, issuer.address); assert.equal(ev.credentialType, 3n);
  await d.view('has-credential-after', 'CVINVehicleCredential1155.hasCredential', c.hasCredential(vehicleA.address, INSPECTION_CERT), 'balance > 0', (v) => assert.equal(v, true));
  await d.tx('issue-registration', 'CVINVehicleCredential1155.issueCredential', c.connect(issuer).issueCredential(vehicleA.address, 2, 1), 'REGISTRATION credential');
  await d.tx('issue-insurance', 'CVINVehicleCredential1155.issueCredential', c.connect(issuer).issueCredential(vehicleA.address, 4, 1), 'INSURANCE_CERT credential');
  await d.tx('issue-badges-multi', 'CVINVehicleCredential1155.issueCredential', c.connect(issuer).issueCredential(vehicleA.address, 5, 4), 'FUNGIBLE claim: 4 MAINTENANCE_BADGE units in one mint (ERC-1155 amount semantics; a count, not four distinct records)');
  await d.tx('issue-inspection-again', 'CVINVehicleCredential1155.issueCredential', c.connect(issuer).issueCredential(vehicleA.address, INSPECTION_CERT, 1), 'a second inspection just increments the balance to 2 — no date, no expiry, no per-inspection identity');
  await d.tx('issue-custom-type', 'CVINVehicleCredential1155.issueCredential', c.connect(issuer).issueCredential(vehicleA.address, 7, 1), 'OBSERVATION: undeclared type 7 is accepted (open type space within 1..255; no registry of types)');
  await d.reverts('issue-type-out-of-range', 'CVINVehicleCredential1155.issueCredential', () => c.connect(issuer).issueCredential(vehicleA.address, 256, 1), 'credential type out of range', 'FIXED (D8): type 256 is rejected — the type space is bounded so the held set is a 256-bit bitmap');
  await d.view('max-credential-type', 'CVINVehicleCredential1155.MAX_CREDENTIAL_TYPE', c.MAX_CREDENTIAL_TYPE(), 'the highest issuable credential type', (v) => assert.equal(v, 255n));
  await d.view('holdings', 'CVINVehicleCredential1155.balanceOfBatch', c.balanceOfBatch(Array(6).fill(vehicleA.address), [1, 2, 3, 4, 5, 7]), 'the whole credential set in one read', (v) => assert.deepEqual([...v], [1n, 1n, 2n, 1n, 4n, 1n]));
  await d.view('credential-types-of', 'CVINVehicleCredential1155.credentialTypesOf', c.credentialTypesOf(vehicleA.address), 'FIXED (D8): the held non-BIRTH types are enumerable on-chain (ascending, bitmap-backed) — no more guessing which ids to put in balanceOfBatch', (v) => assert.deepEqual([...v], [2n, 3n, 4n, 5n, 7n]));

  await d.reverts('issue-birth-cert', 'CVINVehicleCredential1155.issueCredential', () => c.connect(issuer).issueCredential(vehicleA.address, 1, 1), 'use registerVehicle for BIRTH_CERT', 'BIRTH_CERT is reserved for identity creation');
  await d.reverts('issue-unregistered', 'CVINVehicleCredential1155.issueCredential', () => c.connect(issuer).issueCredential(vehicleB.address, INSPECTION_CERT, 1), 'vehicle not registered', 'credentials need an existing identity (and since D8 no transfer can deliver one to an unregistered address either)');
  await d.reverts('issue-zero', 'CVINVehicleCredential1155.issueCredential', () => c.connect(issuer).issueCredential(vehicleA.address, INSPECTION_CERT, 0), 'amount must be positive', 'zero mint rejected');
  await d.reverts('issue-unauthorised', 'CVINVehicleCredential1155.issueCredential', () => c.connect(inspector).issueCredential(vehicleA.address, INSPECTION_CERT, 1), 'AccessControlUnauthorizedAccount', 'a real inspector must first be granted ISSUER_ROLE: ONE role for every credential type (no per-type issuer scoping)');
  await d.tx('grant-inspector-issuer', 'CVINVehicleCredential1155.grantRole', c.connect(issuer).grantRole(ISSUER_ROLE, inspector.address), 'admin grants the inspector the (global) issuer role');
  await d.tx('inspector-issues-insurance', 'CVINVehicleCredential1155.issueCredential', c.connect(inspector).issueCredential(vehicleA.address, 4, 1), 'OBSERVATION: the inspector can now also issue INSURANCE_CERT — the chain cannot tell issuers apart by competence');

  await d.reverts('issuer-transfer-to-unregistered', 'CVINVehicleCredential1155.issuerTransferCredential', () => c.connect(issuer).issuerTransferCredential(vehicleA.address, vehicleB.address, 5), 'recipient not registered', 'FIXED (D8): a credential cannot be moved to an address that is not a registered vehicle (B has no BIRTH_CERT yet)');
  await c.registerVehicle(vehicleB.address, VINS.fiat);
  await d.tx('issuer-transfer-credential', 'CVINVehicleCredential1155.issuerTransferCredential', c.connect(issuer).issuerTransferCredential(vehicleA.address, vehicleB.address, 5),
    'once B is registered the issuer moves ALL 4 badges to vehicle B; non-BIRTH types do not touch the VIN maps');
  await d.view('badges-moved', 'CVINVehicleCredential1155.balanceOfBatch', c.balanceOfBatch([vehicleA.address, vehicleB.address], [5, 5]), 'A: 0, B: 4', (v) => assert.deepEqual([...v], [0n, 4n]));

  const r2 = await d.tx('revoke-one-inspection', 'CVINVehicleCredential1155.revokeCredential', c.connect(issuer).revokeCredential(vehicleA.address, INSPECTION_CERT, 1),
    'MEASURED (revoke): burn 1 unit -> CredentialRevoked + TransferSingle(to=0); one of the two inspections is gone, which one is undefined');
  assert.equal(eventArgs(c, r2, 'CredentialRevoked').amount, 1n);
  await d.view('still-has-one', 'CVINVehicleCredential1155.hasCredential', c.hasCredential(vehicleA.address, INSPECTION_CERT), 'balance 1 remains', (v) => assert.equal(v, true));
  await d.reverts('revoke-too-many', 'CVINVehicleCredential1155.revokeCredential', () => c.connect(issuer).revokeCredential(vehicleA.address, INSPECTION_CERT, 5), 'insufficient credential balance', 'cannot burn more than held');
  await d.tx('any-issuer-revokes', 'CVINVehicleCredential1155.revokeCredential', c.connect(inspector).revokeCredential(vehicleA.address, 2, 1), 'OBSERVATION: any ISSUER_ROLE holder can revoke credentials issued by another issuer (no issuer binding per credential)');
  d.offchain('veracity', 'CVINVehicleCredential1155', 'asymmetry: a verifier learns only "address X holds N units of type T"; who issued it, when, and what it attests must be recovered from CredentialIssued logs and off-chain documents');
});
