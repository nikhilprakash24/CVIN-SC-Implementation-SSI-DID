'use strict';
/**
 * ERC-1155 — family "Revocation / status" (manifest: measured-in-comparison via revokeCredential).
 * Two revocation levels: burning a credential unit, and burning the BIRTH_CERT, which deregisters
 * the identity (VIN maps deleted) — allowed only once the vehicle holds no other credential, so
 * nothing is orphaned on the address (D8 fix, 2026-10-04); plus issuer-side revocation with
 * revokeRole and the documented (unchanged) flat issuer model.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1155/demos/revocation.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('erc-1155', 'revocation');

d.run(async () => {
  const [issuer, vehicleA, issuer2] = await ethers.getSigners();
  const { assert } = d;
  const c = await (await ethers.getContractFactory('CVINVehicleCredential1155', issuer)).deploy();
  await c.waitForDeployment();
  const vinHash = ethers.keccak256(ethers.toUtf8Bytes(VINS.renault));
  await c.registerVehicle(vehicleA.address, VINS.renault);
  await c.issueCredential(vehicleA.address, 3, 1);
  await c.issueCredential(vehicleA.address, 4, 1);
  d.offchain('setup', 'CVINVehicleCredential1155.registerVehicle+issueCredential', 'vehicle A: BIRTH_CERT + INSPECTION_CERT + INSURANCE_CERT');

  const r1 = await d.tx('revoke-credential', 'CVINVehicleCredential1155.revokeCredential', c.connect(issuer).revokeCredential(vehicleA.address, 3, 1),
    'MEASURED (revoke): burn the inspection credential -> CredentialRevoked; status = balance now 0 (no tombstone, no reason, no timestamp on-chain)');
  assert.equal(eventArgs(c, r1, 'CredentialRevoked').credentialType, 3n);
  await d.view('status-after', 'CVINVehicleCredential1155.hasCredential', c.hasCredential(vehicleA.address, 3), 'a verifier checks status by balance; "never issued" and "revoked" look identical', (v) => assert.equal(v, false));
  await d.reverts('revoke-unauthorised', 'CVINVehicleCredential1155.revokeCredential', () => c.connect(vehicleA).revokeCredential(vehicleA.address, 4, 1), 'AccessControlUnauthorizedAccount', 'the holder cannot even give a credential up (no burn for holders)');
  await d.reverts('revoke-none', 'CVINVehicleCredential1155.revokeCredential', () => c.connect(issuer).revokeCredential(vehicleA.address, 3, 1), 'insufficient credential balance', 'double revocation fails');

  await d.reverts('revoke-birth-cert-blocked', 'CVINVehicleCredential1155.revokeCredential', () => c.connect(issuer).revokeCredential(vehicleA.address, 1, 1),
    "revoke the vehicle's other credentials first", 'FIXED (D8): the BIRTH_CERT cannot be burned while the INSURANCE_CERT is still held — deregistration used to leave it orphaned on an address that is no longer a vehicle');
  await d.view('credential-types-held', 'CVINVehicleCredential1155.credentialTypesOf', c.credentialTypesOf(vehicleA.address), 'the guard reads the per-vehicle held-type bitmap: [4] (INSURANCE_CERT) is still there', (v) => assert.deepEqual([...v], [4n]));
  await d.tx('revoke-insurance', 'CVINVehicleCredential1155.revokeCredential', c.connect(issuer).revokeCredential(vehicleA.address, 4, 1), 'the issuer first burns the remaining credential');
  const r2 = await d.tx('revoke-birth-cert', 'CVINVehicleCredential1155.revokeCredential', c.connect(issuer).revokeCredential(vehicleA.address, 1, 1),
    'identity-level revocation: with nothing else held, burning the BIRTH_CERT deletes vinHashToVehicle + vehicleVIN (deregistration)');
  assert.equal(eventArgs(c, r2, 'CredentialRevoked').credentialType, 1n);
  await d.view('deregistered', 'CVINVehicleCredential1155.isRegistered+vehicleVIN+vinHashToVehicle', Promise.all([c.isRegistered(vehicleA.address), c.vehicleVIN(vehicleA.address), c.vinHashToVehicle(vinHash)]),
    'identity gone: not registered, VIN cleared, index cleared', (v) => assert.deepEqual(v, [false, '', ethers.ZeroAddress]));
  await d.view('no-orphan', 'CVINVehicleCredential1155.hasCredential+credentialTypesOf', Promise.all([c.hasCredential(vehicleA.address, 4), c.credentialTypesOf(vehicleA.address)]),
    'FIXED (D8): the deregistered address holds no credential at all (invariant ii) — the issuer no longer has to remember to burn an orphan', (v) => { assert.equal(v[0], false); assert.deepEqual([...v[1]], []); });
  await d.reverts('issue-after-deregistration', 'CVINVehicleCredential1155.issueCredential', () => c.connect(issuer).issueCredential(vehicleA.address, 2, 1), 'vehicle not registered', 'no new credentials for a deregistered address');
  await d.tx('reregister-same-vin', 'CVINVehicleCredential1155.registerVehicle', c.connect(issuer).registerVehicle(vehicleA.address, VINS.renault), 'OBSERVATION: the same VIN can be registered again after deregistration (no permanent tombstone); the "revocation" is reversible by the issuer');

  const ISSUER_ROLE = await c.ISSUER_ROLE();
  await d.tx('grant-issuer-2', 'CVINVehicleCredential1155.grantRole', c.connect(issuer).grantRole(ISSUER_ROLE, issuer2.address), 'second issuer');
  await d.tx('issuer-2-issues', 'CVINVehicleCredential1155.issueCredential', c.connect(issuer2).issueCredential(vehicleA.address, 3, 1), 'issuer 2 issues an inspection');
  const r3 = await d.tx('revoke-role', 'CVINVehicleCredential1155.revokeRole', c.connect(issuer).revokeRole(ISSUER_ROLE, issuer2.address), 'issuer-side revocation -> RoleRevoked');
  assert.equal(eventArgs(c, r3, 'RoleRevoked').account, issuer2.address);
  await d.reverts('revoked-issuer-blocked', 'CVINVehicleCredential1155.issueCredential', () => c.connect(issuer2).issueCredential(vehicleA.address, 3, 1), 'AccessControlUnauthorizedAccount', 'revoked issuer cannot issue');
  await d.view('issued-by-revoked-issuer-survives', 'CVINVehicleCredential1155.hasCredential', c.hasCredential(vehicleA.address, 3), 'OBSERVATION: credentials from a revoked issuer stay valid; the chain does not link a balance to its issuer', (v) => assert.equal(v, true));
});
