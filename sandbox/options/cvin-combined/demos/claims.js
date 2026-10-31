'use strict';
/**
 * cvin-combined / claims — the ERC-735 half of the hybrid: addClaim with RAW-digest ECDSA
 * (keccak256(registry, identity, topic, data), no EIP-191), the three safety-critical topics,
 * getClaim / getClaimIdsByTopic / hasValidClaim (O(1) on-chain verification), removeClaim by
 * owner or issuer, in-place re-add, and the validation negatives.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/cvin-combined/demos/claims.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'cvin-combined';
const FAMILY = 'claims';
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
  const [deployer, vehicleOwner, newOwner, delegate, stranger, inspectorSigner] = await ethers.getSigners();
  const reg = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy();
  out('deploy-registry', `${CONTRACT}.constructor`, true, (await reg.deploymentTransaction().wait()).gasUsed, 'shared hybrid registry');
  const id = vehicleOwner.address;
  const regAddr = await reg.getAddress();
  const manufacturer = ethers.Wallet.createRandom(); // off-chain issuer: signs only
  const inspector = ethers.Wallet.createRandom();
  const digest = (identity, topic, data) => ethers.solidityPackedKeccak256(['address', 'address', 'uint256', 'bytes'], [regAddr, identity, topic, data]);
  const raw = (w, identity, topic, data) => ethers.Signature.from(w.signingKey.sign(digest(identity, topic, data))).serialized;
  const claimId = (issuer, topic) => ethers.solidityPackedKeccak256(['address', 'uint256'], [issuer, topic]);

  const T = {};
  for (const n of ['CLAIM_TOPIC_VIN', 'CLAIM_TOPIC_MANUFACTURER', 'CLAIM_TOPIC_INSPECTION']) T[n] = await view(`const-${n}`, `${CONTRACT}.${n}`, reg[n](), (v) => `${n} == ${v}`);
  assert((await view('SCHEME_ECDSA', `${CONTRACT}.SCHEME_ECDSA`, reg.SCHEME_ECDSA(), (v) => `SCHEME_ECDSA == ${v} (only scheme)`)) === 1n, 'scheme');
  out('signing-scheme', 'offchain:issuer-signing', false, 0, 'issuer signs the RAW keccak256(abi.encodePacked(registry, identity, topic, data)) with secp256k1 — NO EIP-191 envelope (mirrors ERC-1056 signed ops); binds the claim to this registry AND the subject; personal_sign wallets cannot produce it, an HSM / signingKey can');

  const mData = b(JSON.stringify({ vin: VIN, make: 'Honda', model: 'Accord', year: 2003 }));
  await reverts('addClaim-by-non-owner', `${CONTRACT}.addClaim`, reg.connect(stranger).addClaim(id, T.CLAIM_TOPIC_MANUFACTURER, 1, manufacturer.address, raw(manufacturer, id, 2, mData), mData, ''), 'CVINCombined: unauthorized', 'holder consent: only identityOwner anchors (the issuer cannot push)');
  const r1 = await tx('addClaim-MANUFACTURER', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, T.CLAIM_TOPIC_MANUFACTURER, 1, manufacturer.address, raw(manufacturer, id, 2, mData), mData, 'ipfs://QmTypeApproval'),
    `MEASURED (benchmark addDelegateOrClaim; L1 claim 331,461): ecrecover at add time + full claim stored under claims[identity][claimId] + topic index + changed pointer; ClaimAdded`);
  const ev = eventsOf(r1, reg, 'ClaimAdded');
  assert(ev.length === 1 && ev[0].args.identity === id && ev[0].args.issuer === manufacturer.address, 'ClaimAdded');
  const mId = claimId(manufacturer.address, 2);
  const g = await view('getClaim', `${CONTRACT}.getClaim`, reg.getClaim(id, mId), (v) => `getClaim(identity, ${short(mId)}) -> topic=${v[0]} scheme=${v[1]} issuer=${short(v[2])} data=${v[4].length / 2 - 1}B uri=${v[5]}: O(1), no re-verification`);
  assert(g[2] === manufacturer.address, 'stored');
  assert((await view('hasValidClaim', `${CONTRACT}.hasValidClaim`, reg.hasValidClaim(id, T.CLAIM_TOPIC_MANUFACTURER, manufacturer.address), (v) => `hasValidClaim(identity, MANUFACTURER, issuer) == ${v}: the single call an RSU / toll contract makes before trusting the vehicle`)) === true, 'valid');
  assert((await view('hasValidClaim-other-issuer', `${CONTRACT}.hasValidClaim`, reg.hasValidClaim(id, T.CLAIM_TOPIC_MANUFACTURER, stranger.address), (v) => `hasValidClaim(…, stranger) == ${v}: the verifier names the issuer it trusts — no on-chain issuer registry`)) === false, 'other issuer');

  const iData = b('APK:2026-03-14:PASS:odo=182340');
  await tx('addClaim-INSPECTION', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, T.CLAIM_TOPIC_INSPECTION, 1, inspector.address, raw(inspector, id, 3, iData), iData, ''), 'periodic inspection by a second issuer');
  const iData2 = b('APK:2027-03-10:PASS:odo=201115');
  const r2 = await tx('addClaim-INSPECTION-update', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, T.CLAIM_TOPIC_INSPECTION, 1, inspector.address, raw(inspector, id, 3, iData2), iData2, ''),
    'MEASURED (benchmark updateAttribute analogue): re-add for the same (issuer, topic) overwrites in place; topic index not duplicated; emits ClaimAdded again (the hybrid has no ClaimChanged event)');
  assert(eventsOf(r2, reg, 'ClaimAdded').length === 1 && (await reg.getClaimIdsByTopic(id, 3)).length === 1, 'in-place');
  const ids = await view('getClaimIdsByTopic', `${CONTRACT}.getClaimIdsByTopic`, reg.getClaimIdsByTopic(id, T.CLAIM_TOPIC_INSPECTION), (v) => `getClaimIdsByTopic(identity, INSPECTION) -> ${v.length} (per-identity topic index)`);
  assert(ids[0] === claimId(inspector.address, 3), 'index');
  const vData = b(VIN);
  await tx('addClaim-VIN', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, T.CLAIM_TOPIC_VIN, 1, manufacturer.address, raw(manufacturer, id, 1, vData), vData, ''), 'VIN attestation (topic 1) by the manufacturer');

  // negatives
  const eip191 = await inspectorSigner.signMessage(ethers.getBytes(digest(id, 3, iData)));
  await reverts('eip191-signature-rejected', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, 3, 1, inspectorSigner.address, eip191, iData, ''), 'invalid claim signature', 'an EIP-191 personal_sign signature (the ERC-735 claim holder\'s convention) recovers to a different address here — the two claim contracts are signature-incompatible');
  await reverts('wrong-identity-binding', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, 3, 1, inspector.address, raw(inspector, newOwner.address, 3, iData), iData, ''), 'invalid claim signature', 'a claim signed for ANOTHER identity cannot be replayed onto this one (identity is in the digest)');
  await reverts('tampered-data', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, 3, 1, inspector.address, raw(inspector, id, 3, iData), b('APK:2026-03-14:FAIL'), ''), 'invalid claim signature', 'data altered after signing');
  await reverts('short-signature', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, 3, 1, inspector.address, '0x' + 'ab'.repeat(64), iData, ''), 'invalid claim signature', '64-byte signature -> recover returns address(0) -> mismatch (no length error, same revert)');
  await reverts('unsupported-scheme', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, 3, 2, inspector.address, raw(inspector, id, 3, iData), iData, ''), 'unsupported scheme', 'scheme must be 1');
  await reverts('zero-issuer', `${CONTRACT}.addClaim`, reg.connect(vehicleOwner).addClaim(id, 3, 1, ethers.ZeroAddress, raw(inspector, id, 3, iData), iData, ''), 'zero issuer', 'guard');
  out('no-malleability-guard', `${CONTRACT}.addClaim`, true, 0, 'OBSERVATION: unlike CVINVehicleClaimHolder there is no EIP-2 high-s check; harmless here because claimId = keccak(issuer, topic) is signature-independent, but a malleated signature is stored verbatim');

  // removal
  await reverts('removeClaim-by-stranger', `${CONTRACT}.removeClaim`, reg.connect(stranger).removeClaim(id, mId), 'CVINCombined: unauthorized', 'owner or issuer only');
  await reverts('removeClaim-nonexistent', `${CONTRACT}.removeClaim`, reg.connect(vehicleOwner).removeClaim(id, claimId(stranger.address, 2)), 'claim not found', 'guard');
  const r3 = await tx('removeClaim-by-owner', `${CONTRACT}.removeClaim`, reg.connect(vehicleOwner).removeClaim(id, claimId(inspector.address, 3)), 'MEASURED (benchmark revoke = removeClaim): delete + topic-index swap-and-pop + changed pointer; storage refund; ClaimRemoved');
  assert(eventsOf(r3, reg, 'ClaimRemoved').length === 1, 'ClaimRemoved');
  assert((await view('hasValidClaim-after-remove', `${CONTRACT}.hasValidClaim`, reg.hasValidClaim(id, 3, inspector.address), (v) => `hasValidClaim(INSPECTION) == ${v}`)) === false, 'removed');
  out('issuer-side-removal', `${CONTRACT}.removeClaim`, true, 0, 'issuer-side revocation (msg.sender == claim.issuer) exists but needs the issuer to hold ETH and send a tx; our issuers are off-chain wallets (signing only), so it is exercised in the revocation demo with a funded issuer');
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(regAddr);
  const a = await ad.addClaim(id, 3, 'APK:2028', '0x');
  out('adapter-addClaim', `${CONTRACT}.addClaim`, true, a.gasUsed, `adapter (own random issuer wallet, raw digest): ${a.note}`);
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve-claims', 'adapter.resolve', true, 0, `resolve: claims=${doc.claims.length} [${doc.claims.map((x) => `${x.topicName}:${x.valid}`).join(', ')}] vin=${doc.vehicle.vin}`);
  assert(doc.claims.length === 3 && doc.vehicle.vin === VIN, 'doc');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
