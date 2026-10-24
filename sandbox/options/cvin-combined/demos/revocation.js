'use strict';
/**
 * cvin-combined / revocation — three sub-identity revocations (revokeAttribute: event only;
 * revokeDelegate: validity = now; removeClaim: delete + refund, by owner or issuer) and no
 * identity-level revocation.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/cvin-combined/demos/revocation.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'cvin-combined';
const FAMILY = 'revocation';
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
const eventsOf = (receipt, c, name) => receipt.logs.map((l) => { try { return c.interface.parseLog(l); } catch (_) { return null; } }).filter((e) => e && e.name === name);
const h = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));
const b = (s) => ethers.hexlify(ethers.toUtf8Bytes(s));

const CONTRACT = 'CVINCombinedIdentity';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate, stranger] = await ethers.getSigners();
  const reg = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy();
  out('deploy-registry', `${CONTRACT}.constructor`, true, (await reg.deploymentTransaction().wait()).gasUsed, 'shared hybrid registry');
  const id = vehicleOwner.address;
  const regAddr = await reg.getAddress();
  const issuer = ethers.Wallet.createRandom().connect(ethers.provider); // funded so it can send its own revocation
  await (await deployer.sendTransaction({ to: issuer.address, value: ethers.parseEther('1') })).wait();
  const raw = (w, topic, data) => ethers.Signature.from(w.signingKey.sign(ethers.solidityPackedKeccak256(['address', 'address', 'uint256', 'bytes'], [regAddr, id, topic, data]))).serialized;
  const claimId = (iss, topic) => ethers.solidityPackedKeccak256(['address', 'uint256'], [iss, topic]);

  const KEY = h('did/pub/secp256k1/veriKey');
  const pub = ethers.hexlify(ethers.randomBytes(33));
  await tx('setAttribute', `${CONTRACT}.setAttribute`, reg.connect(vehicleOwner).setAttribute(id, KEY, pub, 31536000), 'to revoke');
  await tx('addDelegate', `${CONTRACT}.addDelegate`, reg.connect(vehicleOwner).addDelegate(id, h('sigAuth'), delegate.address, 31536000), 'to revoke');
  await tx('addClaim-inspection', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, 3, 1, issuer.address, raw(issuer, 3, b('APK:2026:PASS')), b('APK:2026:PASS'), ''), 'to revoke (owner-side)');
  await tx('addClaim-manufacturer', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, 2, 1, issuer.address, raw(issuer, 2, b('TYPE-APPROVAL')), b('TYPE-APPROVAL'), ''), 'to revoke (issuer-side)');

  const r1 = await tx('revokeAttribute', `${CONTRACT}.revokeAttribute`, reg.connect(vehicleOwner).revokeAttribute(id, KEY, pub), 'event-only revocation: DIDAttributeChanged(validTo = 0); cheapest; nothing to refund');
  assert(eventsOf(r1, reg, 'DIDAttributeChanged')[0].args.validTo === 0n, 'validTo 0');
  const r2 = await tx('revokeDelegate', `${CONTRACT}.revokeDelegate`, reg.connect(vehicleOwner).revokeDelegate(id, h('sigAuth'), delegate.address), 'MEASURED (benchmark revoke = revokeDelegate; L1 revoke 71,322): validity := block.timestamp (slot stays non-zero) + DIDDelegateChanged');
  assert((await reg.validDelegate(id, h('sigAuth'), delegate.address)) === false, 'delegate revoked');
  const r3 = await tx('removeClaim-owner-side', `${CONTRACT}.removeClaim`, reg.connect(vehicleOwner).removeClaim(id, claimId(issuer.address, 3)), 'MEASURED (benchmark revoke = removeClaim): delete struct + index pop; refund makes it cheaper than revokeDelegate despite more work');
  assert(eventsOf(r3, reg, 'ClaimRemoved').length === 1, 'ClaimRemoved');
  await reverts('removeClaim-by-stranger', `${CONTRACT}.removeClaim`, reg.connect(stranger).removeClaim(id, claimId(issuer.address, 2)), 'CVINCombined: unauthorized', 'access');
  const r4 = await tx('removeClaim-issuer-side', `${CONTRACT}.removeClaim`, reg.connect(issuer).removeClaim(id, claimId(issuer.address, 2)), 'issuer-side revocation: the manufacturer withdraws its type approval without the owner (msg.sender == claim.issuer)');
  assert((await view('hasValidClaim-after', `${CONTRACT}.hasValidClaim`, reg.hasValidClaim(id, 2, issuer.address), (v) => `hasValidClaim(MANUFACTURER) == ${v}: O(1) revocation check for on-chain verifiers`)) === false, 'gone');
  out('gas-ladder', `${CONTRACT}.removeClaim`, true, 0, `revocation costs: attribute ${r1.gasUsed} | delegate ${r2.gasUsed} | claim(owner) ${r3.gasUsed} | claim(issuer) ${r4.gasUsed} — the comparison reports only revokeDelegate`);
  assert(typeof reg.revokeIdentity === 'undefined' && typeof reg.isRevoked === 'undefined', 'no identity revocation');
  out('no-identity-revocation', `${CONTRACT}.identityOwner`, true, 0, 'no revokeIdentity/isRevoked (the vehicle-profile registry has them): decommissioning = revoke every delegate/claim individually; a verifier has no single status bit — a gap in the hybrid the thesis should name');
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(regAddr);
  const na = await ad.revoke(id);
  assert(na.notApplicable === true, 'nothing tracked');
  out('adapter-revoke-bare', 'adapter.revoke', true, 0, `adapter.revoke(id) with nothing tracked -> NotApplicable: ${na.reason}`);
  await ad.addClaim(id, 3, 'APK:2027', '0x');
  const rv = await ad.revoke(id);
  out('adapter-revoke-last', `${CONTRACT}.removeClaim`, true, rv.gasUsed, `adapter.revoke(id) after an adapter addClaim -> ${rv.note}`);
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
