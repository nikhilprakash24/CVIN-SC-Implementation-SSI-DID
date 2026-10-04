'use strict';
/**
 * erc-735 / authorisation-roles — who may do what: the owner (MANAGEMENT-key role) anchors
 * and removes, an issuer may only withdraw its own claim, and MANUFACTURER_CERT is the
 * manufacturer's role expressed as a claim topic — there is no issuer whitelist.
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
  await reverts('issuer-cannot-self-anchor', `${CONTRACT}.addClaim`, c.connect(manufacturer).addClaim(MC, 1, manufacturer.address, sig, cert, ''), 'caller is not the owner', 'a valid issuer signature does not grant write access: anchoring is the holder\'s decision (consent)');
  await tx('owner-anchors-manufacturer-cert', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(MC, 1, manufacturer.address, sig, cert, 'ipfs://QmBirthCert'), 'the owner anchors the manufacturer certificate; the chain checks the signature, NOT that the signer is a real OEM');
  const fakeCert = b(JSON.stringify({ vin: VIN, make: 'Ferrari', model: 'F8', year: 2023 }));
  await tx('anyone-can-be-a-manufacturer', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(MC, 1, stranger.address, await sign(stranger, MC, fakeCert), fakeCert, ''),
    'OBSERVATION: a second MANUFACTURER_CERT signed by a random address is accepted — no issuer registry/whitelist exists; veracity (is this issuer an OEM?) is entirely the verifier\'s off-chain trust decision');
  const ids = await view('getClaimIdsByTopic-manufacturer', `${CONTRACT}.getClaimIdsByTopic`, c.getClaimIdsByTopic(MC), (v) => `getClaimIdsByTopic(MANUFACTURER_CERT) -> ${v.length} competing certificates; a verifier must pick by issuer address`);
  assert(ids.length === 2, 'two certs');
  await reverts('stranger-cannot-remove-oem-cert', `${CONTRACT}.removeClaim`, c.connect(stranger).removeClaim(claimId(manufacturer.address, MC)), 'caller is not owner nor issuer', 'issuer role is per-claim: the fake issuer cannot touch the OEM claim');
  await tx('issuer-withdraws-own', `${CONTRACT}.removeClaim`, c.connect(stranger).removeClaim(claimId(stranger.address, MC)), 'but may withdraw its own');
  await tx('oem-withdraws-own', `${CONTRACT}.removeClaim`, c.connect(manufacturer).removeClaim(claimId(manufacturer.address, MC)), 'issuer-side withdrawal by the OEM');
  await reverts('transfer-by-stranger', `${CONTRACT}.transferOwnership`, c.connect(stranger).transferOwnership(stranger.address), 'caller is not the owner', 'MANAGEMENT role transfer is owner-only');
  out('roles-summary', `${CONTRACT}.claimExists`, true, 0, 'roles on-chain: owner (anchor/remove/transfer), issuer-of-claim (remove own). Not on-chain: issuer accreditation, manufacturer registry, inspector licensing — the comparison measures none of this family');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
