'use strict';
/**
 * erc-735 / authorisation-roles — who may do what: the owner (MANAGEMENT-key role) anchors
 * and removes, an issuer may only withdraw its own claim, MANUFACTURER_CERT is the
 * manufacturer's role expressed as a claim topic, and (D25a) the owner keeps a per-topic
 * issuer registry — authorizeIssuer / revokeIssuer / isAuthorizedIssuer — that addClaim
 * enforces (self-issued claims, issuer == owner, are exempt).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-735/demos/authorisation-roles.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-735';
const FAMILY = 'authorisation-roles';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
const tx = async (step, fn, p, note) => { const r = await (await p).wait(); out(step, fn, true, r.gasUsed, note); return r; };
const view = async (step, fn, p, note) => { const v = await p; out(step, fn, true, 0, typeof note === 'function' ? note(v) : note); return v; };
const reverts = async (step, fn, p, reason, note) => {
  let msg = null;
  try { const t = await p; if (t && typeof t.wait === 'function') await t.wait(); } catch (e) { msg = String(e.message || e); const d = e.data || (e.error && e.error.data); if (typeof d === 'string' && d.startsWith('0x08c379a0')) { try { msg += ' | ' + ethers.AbiCoder.defaultAbiCoder().decode(['string'], '0x' + d.slice(10))[0]; } catch (_) { /* not Error(string) */ } } }
  if (msg === null) throw new Error(`${step}: expected revert "${reason}" but the call succeeded`);
  if (!msg.includes(reason)) throw new Error(`${step}: expected revert "${reason}", got: ${msg}`);
  out(step, fn, true, 0, `reverted as expected ("${reason}"): ${note}`);
};
const assert = (c, m) => { if (!c) throw new Error(`assertion failed: ${m}`); };
const b = (s) => ethers.hexlify(ethers.toUtf8Bytes(s));
const short = (a) => `${String(a).slice(0, 10)}…`;

const CONTRACT = 'CVINVehicleClaimHolder';
const VIN = '1HGCM82633A004352';

async function main() {
  const [, vehicleOwner, , , stranger, manufacturer] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, vehicleOwner)).deploy(VIN);
  out('deploy-identity', `${CONTRACT}.constructor`, true, (await c.deploymentTransaction().wait()).gasUsed, 'per-vehicle claim holder');
  const id = await c.getAddress();
  const sign = (signer, topic, data) => signer.signMessage(ethers.getBytes(ethers.solidityPackedKeccak256(['address', 'uint256', 'bytes'], [id, topic, data])));
  const claimId = (issuer, topic) => ethers.solidityPackedKeccak256(['address', 'uint256'], [issuer, topic]);

  const MC = await view('MANUFACTURER_CERT', `${CONTRACT}.MANUFACTURER_CERT`, c.MANUFACTURER_CERT(), (v) => `MANUFACTURER_CERT == ${v}: the manufacturer "role" is a claim TOPIC, not an access-control role`);
  assert((await view('owner-is-management-key', `${CONTRACT}.owner`, c.owner(), (v) => `owner == ${short(v)}: plays the ERC-734 MANAGEMENT key — the only privileged role in the contract (no CLAIM keys, no ACTION keys, no admin)`)) === vehicleOwner.address, 'owner');
  const cert = b(JSON.stringify({ vin: VIN, make: 'Honda', model: 'Accord', year: 2003 }));
  const sig = await sign(manufacturer, MC, cert);

  // --- issuer registry (D25a): the owner decides which authorities this vehicle recognises ---
  assert((await view('isAuthorizedIssuer-before', `${CONTRACT}.isAuthorizedIssuer`, c.isAuthorizedIssuer(manufacturer.address, MC), (v) => `isAuthorizedIssuer(manufacturer, MANUFACTURER_CERT) == ${v}: the registry is empty at birth — no issuer may anchor anything until the owner admits it`)) === false, 'empty registry');
  await reverts('authorizeIssuer-by-stranger', `${CONTRACT}.authorizeIssuer`, c.connect(stranger).authorizeIssuer(stranger.address, MC), 'caller is not the owner', 'the registry is MANAGEMENT-key state: only the owner admits issuers (an issuer cannot admit itself)');
  await reverts('authorizeIssuer-zero', `${CONTRACT}.authorizeIssuer`, c.connect(vehicleOwner).authorizeIssuer(ethers.ZeroAddress, MC), 'issuer is zero address', 'guard');
  await tx('authorizeIssuer-manufacturer', `${CONTRACT}.authorizeIssuer`, c.connect(vehicleOwner).authorizeIssuer(manufacturer.address, MC), 'D25: issuers must be authorised per topic — the owner admits the OEM for MANUFACTURER_CERT only (IssuerAuthorized event; one cold SSTORE)');
  assert((await view('isAuthorizedIssuer-after', `${CONTRACT}.isAuthorizedIssuer`, c.isAuthorizedIssuer(manufacturer.address, MC), (v) => `isAuthorizedIssuer(manufacturer, MANUFACTURER_CERT) == ${v}`)) === true, 'authorised');
  assert((await view('isAuthorizedIssuer-other-topic', `${CONTRACT}.isAuthorizedIssuer`, c.isAuthorizedIssuer(manufacturer.address, 3), (v) => `isAuthorizedIssuer(manufacturer, INSPECTION) == ${v}: authorisation is (issuer, topic)-scoped — an OEM is not thereby an inspector`)) === false, 'scoped');
  await reverts('authorizeIssuer-twice', `${CONTRACT}.authorizeIssuer`, c.connect(vehicleOwner).authorizeIssuer(manufacturer.address, MC), 'issuer already authorized', 'idempotence guard: every IssuerAuthorized event marks a real state change');

  await reverts('issuer-cannot-self-anchor', `${CONTRACT}.addClaim`, c.connect(manufacturer).addClaim(MC, 1, manufacturer.address, sig, cert, ''), 'caller is not the owner', 'a valid signature from an AUTHORISED issuer still does not grant write access: anchoring is the holder\'s decision (consent)');
  await tx('owner-anchors-manufacturer-cert', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(MC, 1, manufacturer.address, sig, cert, 'ipfs://QmBirthCert'), 'the owner anchors the manufacturer certificate; the chain checks the signature AND that the signer is on the holder\'s registry for this topic (D25a)');
  const fakeCert = b(JSON.stringify({ vin: VIN, make: 'Ferrari', model: 'F8', year: 2023 }));
  await reverts('anyone-can-be-a-manufacturer', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(MC, 1, stranger.address, await sign(stranger, MC, fakeCert), fakeCert, ''), 'issuer not authorized for topic',
    'FIXED (D25a): a second MANUFACTURER_CERT validly signed by a random address is REJECTED — formerly it was accepted and two competing certificates coexisted; the signature check passes (who signed) but the registry check fails (may they sign). Whether a registered issuer is a REAL OEM remains the owner\'s decision when admitting it');
  const ids = await view('getClaimIdsByTopic-manufacturer', `${CONTRACT}.getClaimIdsByTopic`, c.getClaimIdsByTopic(MC), (v) => `getClaimIdsByTopic(MANUFACTURER_CERT) -> ${v.length} certificate: a verifier no longer has to pick between competing issuers by address`);
  assert(ids.length === 1, 'one cert');

  // --- self-issued claims are exempt (issuer == owner) ---
  const selfCert = b(JSON.stringify({ vin: VIN, note: 'owner-asserted: imported grey-market, no OEM paperwork' }));
  await tx('self-issued-claim', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(MC, 1, vehicleOwner.address, await sign(vehicleOwner, MC, selfCert), selfCert, ''),
    'D25a exemption: a claim signed by the OWNER about its own vehicle needs no registry entry (the ERC-735 draft lets an identity issue claims about itself); a verifier sees issuer == owner and reads it as SELF-ASSERTED, not attested');
  assert((await view('isAuthorizedIssuer-owner', `${CONTRACT}.isAuthorizedIssuer`, c.isAuthorizedIssuer(vehicleOwner.address, MC), (v) => `isAuthorizedIssuer(owner, MANUFACTURER_CERT) == ${v}: the exemption is NOT reflected in the registry — isAuthorizedIssuer answers only "is this address whitelisted"`)) === false, 'owner not in registry');
  assert((await c.getClaimIdsByTopic(MC)).length === 2, 'oem + self');
  await tx('owner-removes-self-issued', `${CONTRACT}.removeClaim`, c.connect(vehicleOwner).removeClaim(claimId(vehicleOwner.address, MC)), 'the owner withdraws its self-asserted certificate (owner-side removal)');
  await reverts('stranger-cannot-remove-oem-cert', `${CONTRACT}.removeClaim`, c.connect(stranger).removeClaim(claimId(manufacturer.address, MC)), 'caller is not owner nor issuer', 'issuer role is per-claim: a third party cannot touch the OEM claim');

  // --- revokeIssuer: forward-looking withdrawal of the right to issue ---
  await reverts('revokeIssuer-by-stranger', `${CONTRACT}.revokeIssuer`, c.connect(stranger).revokeIssuer(manufacturer.address, MC), 'caller is not the owner', 'owner-only, like authorizeIssuer');
  await reverts('revokeIssuer-unknown', `${CONTRACT}.revokeIssuer`, c.connect(vehicleOwner).revokeIssuer(stranger.address, MC), 'issuer not authorized', 'guard: cannot revoke an issuer that was never admitted (every IssuerRevoked event marks a real state change)');
  await tx('revokeIssuer-manufacturer', `${CONTRACT}.revokeIssuer`, c.connect(vehicleOwner).revokeIssuer(manufacturer.address, MC), 'the owner withdraws the OEM\'s right to issue MANUFACTURER_CERT (IssuerRevoked; storage refund)');
  assert((await view('isAuthorizedIssuer-revoked', `${CONTRACT}.isAuthorizedIssuer`, c.isAuthorizedIssuer(manufacturer.address, MC), (v) => `isAuthorizedIssuer(manufacturer, MANUFACTURER_CERT) == ${v}`)) === false, 'revoked');
  assert((await view('claim-survives-revokeIssuer', `${CONTRACT}.claimExists`, c.claimExists(manufacturer.address, MC), (v) => `claimExists(manufacturer, MANUFACTURER_CERT) == ${v}: revoking an ISSUER is forward-looking — the certificate it already issued stays until removeClaim (contrast: removeClaim revokes a CLAIM)`)) === true, 'claim stays');
  const cert2 = b(JSON.stringify({ vin: VIN, make: 'Honda', model: 'Accord', year: 2003, rev: 2 }));
  await reverts('addClaim-after-revokeIssuer', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(MC, 1, manufacturer.address, await sign(manufacturer, MC, cert2), cert2, ''), 'issuer not authorized for topic', 'a LATER claim (here: the in-place update of the same (issuer, topic)) by the revoked OEM is rejected even though its signature is valid');
  await tx('oem-withdraws-own', `${CONTRACT}.removeClaim`, c.connect(manufacturer).removeClaim(claimId(manufacturer.address, MC)), 'issuer-side withdrawal by the (now revoked) OEM: the per-claim removal right is tied to the CLAIM\'s issuer field, not to the registry');
  await reverts('transfer-by-stranger', `${CONTRACT}.transferOwnership`, c.connect(stranger).transferOwnership(stranger.address), 'caller is not the owner', 'MANAGEMENT role transfer is owner-only');
  out('roles-summary', `${CONTRACT}.claimExists`, true, 0, 'roles on-chain: owner (anchor/remove/transfer, admit/revoke issuers per topic), registered issuer (sign claims on its topic), issuer-of-claim (remove own), owner-as-issuer (self-asserted claims without registry entry). Not on-chain: whether a registered issuer is an accredited OEM/inspector — the owner\'s admission decision replaces the verifier\'s address-picking; the comparison measures none of this family');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
