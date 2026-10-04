'use strict';
/**
 * cvin-combined / authorisation-roles — roles are claim topics: CLAIM_TOPIC_MANUFACTURER is the
 * OEM's role, checked by verifiers with hasValidClaim(identity, topic, trustedIssuer); the
 * contract has no issuer registry and only one privileged role (identityOwner).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/cvin-combined/demos/authorisation-roles.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'cvin-combined';
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

const CONTRACT = 'CVINCombinedIdentity';
const VIN = '1HGCM82633A004352';

async function main() {
  const [deployer, vehicleOwner, , , stranger] = await ethers.getSigners();
  const reg = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy();
  out('deploy-registry', `${CONTRACT}.constructor`, true, (await reg.deploymentTransaction().wait()).gasUsed, 'shared hybrid registry: no admin, no roles, no issuer list');
  const id = vehicleOwner.address;
  const regAddr = await reg.getAddress();
  const oem = ethers.Wallet.createRandom();
  const impostor = ethers.Wallet.createRandom();
  const raw = (w, topic, data) => ethers.Signature.from(w.signingKey.sign(ethers.solidityPackedKeccak256(['address', 'address', 'uint256', 'bytes'], [regAddr, id, topic, data]))).serialized;

  const MT = await view('CLAIM_TOPIC_MANUFACTURER', `${CONTRACT}.CLAIM_TOPIC_MANUFACTURER`, reg.CLAIM_TOPIC_MANUFACTURER(), (v) => `CLAIM_TOPIC_MANUFACTURER == ${v}: the manufacturer role is a claim topic`);
  assert((await view('only-privileged-role', `${CONTRACT}.identityOwner`, reg.identityOwner(id), (v) => `identityOwner == ${short(v)}: the ONLY privileged role in the contract; everything else is a claim`)) === id, 'owner');
  const cert = b(JSON.stringify({ vin: VIN, typeApproval: 'e4*2007/46*0123*05' }));
  await reverts('oem-cannot-self-anchor', `${CONTRACT}.addClaim`, reg.connect(stranger).addClaim(id, MT, 1, oem.address, raw(oem, MT, cert), cert, ''), 'CVINCombined: unauthorized', 'holding a valid OEM signature grants no write access');
  await tx('owner-anchors-oem-claim', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, MT, 1, oem.address, raw(oem, MT, cert), cert, 'ipfs://QmTypeApproval'), 'type approval anchored under the OEM\'s address');
  await tx('owner-anchors-impostor-claim', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, MT, 1, impostor.address, raw(impostor, MT, cert), cert, ''), 'OBSERVATION: a second MANUFACTURER claim from a random key is accepted — the contract validates signatures, not authority');
  assert((await view('hasValidClaim-oem', `${CONTRACT}.hasValidClaim`, reg.hasValidClaim(id, MT, oem.address), (v) => `hasValidClaim(id, MANUFACTURER, OEM) == ${v}: the verifier supplies the issuer it trusts — authority lives in the verifier\'s allow-list, not on-chain`)) === true, 'oem');
  assert((await view('hasValidClaim-impostor', `${CONTRACT}.hasValidClaim`, reg.hasValidClaim(id, MT, impostor.address), (v) => `hasValidClaim(id, MANUFACTURER, impostor) == ${v} as well: both "roles" coexist; without an issuer registry an RSU must hard-code OEM addresses`)) === true, 'impostor');
  const ids = await view('getClaimIdsByTopic', `${CONTRACT}.getClaimIdsByTopic`, reg.getClaimIdsByTopic(id, MT), (v) => `getClaimIdsByTopic(MANUFACTURER) -> ${v.length} claims`);
  assert(ids.length === 2, 'two');
  await reverts('impostor-cannot-remove-oem', `${CONTRACT}.removeClaim`, reg.connect(stranger).removeClaim(id, ethers.solidityPackedKeccak256(['address', 'uint256'], [oem.address, MT])), 'CVINCombined: unauthorized', 'per-claim issuer role: only the OEM (or owner) may withdraw the OEM claim');
  await tx('owner-removes-impostor', `${CONTRACT}.removeClaim`, reg.connect(vehicleOwner).removeClaim(id, ethers.solidityPackedKeccak256(['address', 'uint256'], [impostor.address, MT])), 'the holder curates its own claim set');
  out('hasValidClaim-semantics', `${CONTRACT}.hasValidClaim`, true, 0, 'OBSERVATION: hasValidClaim checks existence only (issuer and topic match) — there is no expiry, no issuer status, no revocation list; "valid" means "present"');
  out('roles-summary', `${CONTRACT}.hasValidClaim`, true, 0, 'on-chain roles: identityOwner (anchor/remove/rotate), claim issuer (remove own). Off-chain: OEM accreditation, inspector licensing, verifier trust lists — the comparison measures none of this family');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
