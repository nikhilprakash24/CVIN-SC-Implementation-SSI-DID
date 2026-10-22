'use strict';
/**
 * cvin-combined / controller — ERC-1056-side ownership in the hybrid: identityOwner defaults to
 * self, changeOwner rotates the controller for BOTH the event-based document and the stored
 * claims (one ownership model gates both halves); no signed variant. Since the merge (K-6 /
 * decision M-A, 2026-10-06) claim operations do not advance `changed`, so DIDOwnerChanged links
 * to the previous DID event (or 0), never to a claim block. The issuer-side sticky revocation
 * (K-2: revokeClaimContent / revokedClaims) is shown as the one claim power the controller does
 * not hold.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/cvin-combined/demos/controller.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'cvin-combined';
const FAMILY = 'controller';
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
const b = (s) => ethers.hexlify(ethers.toUtf8Bytes(s));
const short = (a) => `${String(a).slice(0, 10)}…`;

const CONTRACT = 'CVINCombinedIdentity';
const VIN = '1HGCM82633A004352';

async function main() {
  const [deployer, vehicleOwner, newOwner, , stranger] = await ethers.getSigners();
  const reg = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy();
  out('deploy-registry', `${CONTRACT}.constructor`, true, (await reg.deploymentTransaction().wait()).gasUsed, 'single shared hybrid registry (ERC-1056 events + ERC-735 claim storage)');
  const id = vehicleOwner.address;
  const regAddr = await reg.getAddress();
  const issuer = ethers.Wallet.createRandom().connect(ethers.provider);
  await (await deployer.sendTransaction({ to: issuer.address, value: ethers.parseEther('1') })).wait(); // funded so it can call revokeClaimContent itself
  const rawSig = (identity, topic, data) => ethers.Signature.from(issuer.signingKey.sign(ethers.solidityPackedKeccak256(['address', 'address', 'uint256', 'bytes'], [regAddr, identity, topic, data]))).serialized;
  const rc = await tx('addClaim-VIN', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, 1, 1, issuer.address, rawSig(id, 1, b(VIN)), b(VIN), ''), 'a stored claim, to show that ownership gates the claim side too');
  assert((await view('changed-after-claim', `${CONTRACT}.changed`, reg.changed(id), (v) => `changed == ${v}: FIXED (K-6 / M-A) — addClaim (block ${rc.blockNumber}) did not advance the ERC-1056 chain head; claims are not DID-document state`)) === 0n, 'changed untouched by addClaim');

  assert((await view('identityOwner-self', `${CONTRACT}.identityOwner`, reg.identityOwner(id), (v) => `identityOwner == ${short(v)} (self; the mapping has no public getter in the hybrid — only identityOwner)`)) === id, 'self');
  assert(typeof reg.owners === 'undefined', 'no owners getter');
  await reverts('changeOwner-by-stranger', `${CONTRACT}.changeOwner`, reg.connect(stranger).changeOwner(id, stranger.address), 'CVINCombined: unauthorized', 'only the controller rotates');
  const r = await tx('changeOwner', `${CONTRACT}.changeOwner`, reg.connect(vehicleOwner).changeOwner(id, newOwner.address),
    'MEASURED (benchmark transferOwnership; L1 controller-change 68,813): 1 SSTORE + DIDOwnerChanged + changed pointer; the identity (address) is unchanged');
  const ev = eventsOf(r, reg, 'DIDOwnerChanged');
  assert(ev.length === 1 && ev[0].args.owner === newOwner.address && ev[0].args.previousChange === 0n, 'DIDOwnerChanged links to the previous DID event (none), not to the addClaim block');
  out('event-not-linked-to-claim', `${CONTRACT}.changeOwner`, true, 0, `DIDOwnerChanged.previousChange == ${ev[0].args.previousChange} (genesis), not the addClaim block ${rc.blockNumber}: FIXED (K-6 / M-A) — the previousChange list links DID events only; the claim history is reached through its own DIDClaimChanged filter (see lifecycle-history)`);
  assert((await view('identityOwner-after', `${CONTRACT}.identityOwner`, reg.identityOwner(id), (v) => `identityOwner == ${short(v)} (new controller)`)) === newOwner.address, 'rotated');
  await reverts('old-controller-attribute', `${CONTRACT}.setAttribute`, reg.connect(vehicleOwner).setAttribute(id, ethers.id('x'), '0x01', 60), 'CVINCombined: unauthorized', 'ERC-1056 side follows the controller …');
  await reverts('old-controller-claim', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, 2, 1, issuer.address, rawSig(id, 2, b('x')), b('x'), ''), 'CVINCombined: unauthorized', '… and so does the ERC-735 side: ONE ownership model for both halves (in the separate-contract design the claim holder has its own owner)');
  const claimId = ethers.solidityPackedKeccak256(['address', 'uint256'], [issuer.address, 1]);
  await tx('new-controller-removes-old-claim', `${CONTRACT}.removeClaim`, reg.connect(newOwner).removeClaim(id, claimId), 'the new controller manages claims anchored under the previous one');
  // ---- the one claim power the controller does NOT hold: issuer-side sticky revocation (K-2) ----
  const digest = ethers.solidityPackedKeccak256(['address', 'address', 'uint256', 'bytes'], [regAddr, id, 1, b(VIN)]);
  const revKey = ethers.solidityPackedKeccak256(['address', 'bytes32'], [issuer.address, digest]);
  assert((await view('revokedClaims-after-owner-removal', `${CONTRACT}.revokedClaims`, reg.revokedClaims(revKey), (v) => `revokedClaims(keccak(issuer, digest)) == ${v}: an OWNER removal is not a revocation — the controller can re-anchor the OEM's old signature`)) === false, 'owner removal records nothing');
  await tx('re-anchor-after-owner-removal', `${CONTRACT}.addClaim`, reg.connect(newOwner).addClaim(id, 1, 1, issuer.address, rawSig(id, 1, b(VIN)), b(VIN), ''), 'the new controller re-adds the same signed content (the claim never left the issuer\'s hands)');
  await tx('issuer-revokeClaimContent', `${CONTRACT}.revokeClaimContent`, reg.connect(issuer).revokeClaimContent(id, 1, b(VIN)), 'K-2: the ISSUER revokes the signed content without needing the claim to be anchored (no access control: it can only block its own signatures); the anchored copy with exactly this data is removed as well');
  assert((await view('revokedClaims-after-issuer-revocation', `${CONTRACT}.revokedClaims`, reg.revokedClaims(revKey), (v) => `revokedClaims == ${v}: sticky — keyed on (issuer, raw digest), so a malleated copy of the signature is blocked too`)) === true, 'sticky revocation recorded');
  assert((await view('claim-gone-after-content-revocation', `${CONTRACT}.hasValidClaim`, reg.hasValidClaim(id, 1, issuer.address), (v) => `hasValidClaim == ${v} after revokeClaimContent`)) === false, 'claim removed by content revocation');
  await reverts('controller-cannot-re-anchor-revoked', `${CONTRACT}.addClaim`, reg.connect(newOwner).addClaim(id, 1, 1, issuer.address, rawSig(id, 1, b(VIN)), b(VIN), ''), 'CVINCombined: claim revoked by issuer', 'FIXED (K-2): controller rotation does not help — the controller gates WHO manages claims, the issuer decides WHICH signed content stays valid');
  await tx('changeOwner-to-zero', `${CONTRACT}.changeOwner`, reg.connect(newOwner).changeOwner(id, ethers.ZeroAddress), 'owner -> address(0) …');
  assert((await view('identityOwner-after-zero', `${CONTRACT}.identityOwner`, reg.identityOwner(id), (v) => `… identityOwner == ${short(v)} (self again): same ERC-1056 fallback — no identity-level revocation in the hybrid`)) === id, 'self again');
  assert(typeof reg.changeOwnerSigned === 'undefined', 'no signed variant');
  out('no-signed-variant', `${CONTRACT}.identityOwner`, true, 0, 'no changeOwnerSigned / nonce: the hybrid keeps the ERC-1056 ownership model but not its meta-transactions (signed-execution N/A); issuer signatures appear only in addClaim');
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate: stranger } });
  await ad.attach(regAddr);
  const cc = await ad.changeController(id, newOwner.address);
  out('adapter-changeController', `${CONTRACT}.changeOwner`, true, cc.gasUsed, `adapter.changeController -> ${cc.note}`);
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
