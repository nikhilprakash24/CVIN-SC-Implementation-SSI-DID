'use strict';
/**
 * erc-735 / claims — on-chain claims with on-chain signature verification: the four vehicle
 * topics, ECDSA scheme, EIP-191 signing over keccak256(identity, topic, data), ClaimRequested +
 * ClaimAdded / ClaimChanged / ClaimRemoved, getClaim / getClaimIdsByTopic / claimExists, the
 * per-topic issuer registry that addClaim enforces since D25a (authorizeIssuer first; self-issued
 * claims exempt), and the validation negatives (wrong signer, unauthorised issuer, raw-digest
 * signature — D25c, documented not changed —, high-s, scheme, zero issuer, access).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-735/demos/claims.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-735';
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

const CONTRACT = 'CVINVehicleClaimHolder';
const VIN = '1HGCM82633A004352';
const SECP256K1_N = BigInt('0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141');

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate, stranger, manufacturer, inspector, insurer] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, vehicleOwner)).deploy(VIN);
  out('deploy-identity', `${CONTRACT}.constructor`, true, (await c.deploymentTransaction().wait()).gasUsed, 'per-vehicle claim holder');
  const id = await c.getAddress();
  const digest = (topic, data) => ethers.solidityPackedKeccak256(['address', 'uint256', 'bytes'], [id, topic, data]);
  const sign = (signer, topic, data) => signer.signMessage(ethers.getBytes(digest(topic, data))); // EIP-191 prefixed
  const claimId = (issuer, topic) => ethers.solidityPackedKeccak256(['address', 'uint256'], [issuer, topic]);

  const T = {};
  for (const n of ['VIN_ATTESTATION', 'MANUFACTURER_CERT', 'INSPECTION', 'INSURANCE']) T[n] = await view(`const-${n}`, `${CONTRACT}.${n}`, c[n](), (v) => `${n} == ${v}`);
  assert((await view('ECDSA_SCHEME', `${CONTRACT}.ECDSA_SCHEME`, c.ECDSA_SCHEME(), (v) => `ECDSA_SCHEME == ${v}: the only accepted scheme (contract-account / ERC-1271 issuers unsupported)`)) === 1n, 'scheme');
  out('signing-scheme', 'offchain:issuer-signing', false, 0, 'issuer signs keccak256(abi.encodePacked(identity, topic, data)) WITH the EIP-191 "\\x19Ethereum Signed Message:\\n32" prefix (personal_sign-compatible: any wallet can issue); the chain prefixes again and ecrecovers');

  // issuer registry (D25a): the owner admits each authority for the topic it may attest
  const mData = b(JSON.stringify({ vin: VIN, make: 'Honda', model: 'Accord', year: 2003, plant: 'Marysville' }));
  const mSig = await sign(manufacturer, T.MANUFACTURER_CERT, mData);
  await reverts('addClaim-unauthorised-issuer', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(T.MANUFACTURER_CERT, 1, manufacturer.address, mSig, mData, ''), 'issuer not authorized for topic', 'FIXED (D25a): a validly signed claim from an issuer the owner has not admitted for this topic is rejected — formerly any key could sign a MANUFACTURER_CERT');
  for (const [who, name, topic, tname] of [[manufacturer, 'manufacturer', T.MANUFACTURER_CERT, 'MANUFACTURER_CERT'], [inspector, 'inspector', T.INSPECTION, 'INSPECTION'], [insurer, 'insurer', T.INSURANCE, 'INSURANCE'], [manufacturer, 'manufacturer', T.VIN_ATTESTATION, 'VIN_ATTESTATION']]) {
    await tx(`authorizeIssuer-${name}-${tname}`, `${CONTRACT}.authorizeIssuer`, c.connect(vehicleOwner).authorizeIssuer(who.address, topic), `D25: issuers must be authorised per topic — owner admits ${name} for ${tname} (IssuerAuthorized)`);
  }
  const inspectorOnInsurance = await c.isAuthorizedIssuer(inspector.address, T.INSURANCE);
  assert((await view('isAuthorizedIssuer', `${CONTRACT}.isAuthorizedIssuer`, c.isAuthorizedIssuer(inspector.address, T.INSPECTION), (v) => `isAuthorizedIssuer(inspector, INSPECTION) == ${v}; (inspector, INSURANCE) == ${inspectorOnInsurance}: the whitelist is (issuer, topic)-scoped`)) === true && inspectorOnInsurance === false, 'registry');

  // manufacturer birth certificate
  await reverts('addClaim-by-non-owner', `${CONTRACT}.addClaim`, c.connect(manufacturer).addClaim(T.MANUFACTURER_CERT, 1, manufacturer.address, mSig, mData, ''), 'caller is not the owner', 'even the (authorised) ISSUER cannot push a claim: the holder (owner) anchors it — self-sovereign consent');
  const r1 = await tx('addClaim-MANUFACTURER_CERT', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(T.MANUFACTURER_CERT, 1, manufacturer.address, mSig, mData, 'ipfs://QmBirthCert'),
    `MEASURED (benchmark addDelegateOrClaim; L1 claim 314,543, pre-D25): ecrecover at add time + registry SLOAD (D25a) + full claim stored (${mData.length / 2 - 1} bytes data + 65-byte sig + uri)`);
  assert(eventsOf(r1, c, 'ClaimRequested').length === 1 && eventsOf(r1, c, 'ClaimAdded').length === 1, 'ClaimRequested + ClaimAdded');
  out('events-first-add', `${CONTRACT}.addClaim`, true, 0, 'first add emits ClaimRequested(uint256(claimId), …) AND ClaimAdded: the draft\'s async request/approve flow is collapsed into one synchronous call (event-shape compatibility only)');
  const mId = claimId(manufacturer.address, T.MANUFACTURER_CERT);
  const g = await view('getClaim', `${CONTRACT}.getClaim`, c.getClaim(mId), (v) => `getClaim(${short(mId)}) -> topic=${v[0]} scheme=${v[1]} issuer=${short(v[2])} sig=${v[3].length / 2 - 1}B data=${v[4].length / 2 - 1}B uri=${v[5]}: O(1) read for any on-chain verifier, no re-verification needed`);
  assert(g[2] === manufacturer.address && g[5] === 'ipfs://QmBirthCert', 'stored');
  assert((await view('claimExists', `${CONTRACT}.claimExists`, c.claimExists(manufacturer.address, T.MANUFACTURER_CERT), (v) => `claimExists(manufacturer, MANUFACTURER_CERT) == ${v}`)) === true, 'exists');

  // inspection + insurance
  const iData = b('APK:2026-03-14:PASS:odo=182340');
  await tx('addClaim-INSPECTION', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(T.INSPECTION, 1, inspector.address, await sign(inspector, T.INSPECTION, iData), iData, ''), 'periodic inspection by a second issuer');
  const sData = b('POLICY:NL-4471-2026');
  await tx('addClaim-INSURANCE', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(T.INSURANCE, 1, insurer.address, await sign(insurer, T.INSURANCE, sData), sData, 'https://insurer.example/p/4471'), 'insurance cover by a third issuer');
  const ids = await view('getClaimIdsByTopic', `${CONTRACT}.getClaimIdsByTopic`, c.getClaimIdsByTopic(T.INSPECTION), (v) => `getClaimIdsByTopic(INSPECTION) -> ${v.length} id(s): topic index for "show me all inspections"`);
  assert(ids.length === 1 && ids[0] === claimId(inspector.address, T.INSPECTION), 'topic index');

  // update in place
  const iData2 = b('APK:2027-03-10:PASS:odo=201115');
  const r2 = await tx('addClaim-INSPECTION-update', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(T.INSPECTION, 1, inspector.address, await sign(inspector, T.INSPECTION, iData2), iData2, ''),
    'MEASURED (benchmark updateAttribute = re-add same (issuer, topic)): warm rewrite, ClaimChanged instead of ClaimAdded, topic index unchanged');
  assert(eventsOf(r2, c, 'ClaimChanged').length === 1 && eventsOf(r2, c, 'ClaimAdded').length === 0, 'ClaimChanged');
  assert((await c.getClaimIdsByTopic(T.INSPECTION)).length === 1, 'index unchanged');
  assert(r2.gasUsed < 200000n, 'update cheaper than first add');

  // validation negatives
  await reverts('wrong-signer', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(T.VIN_ATTESTATION, 1, manufacturer.address, await sign(stranger, T.VIN_ATTESTATION, b(VIN)), b(VIN), ''), 'invalid issuer signature', 'signature by someone else than the declared issuer');
  await reverts('tampered-data', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(T.VIN_ATTESTATION, 1, manufacturer.address, await sign(manufacturer, T.VIN_ATTESTATION, b(VIN)), b('1HGCM82633A004353'), ''), 'invalid issuer signature', 'data altered after signing');
  const rawWallet = ethers.Wallet.createRandom();
  const rawSig = ethers.Signature.from(rawWallet.signingKey.sign(digest(T.VIN_ATTESTATION, b(VIN)))).serialized;
  await reverts('raw-digest-signature', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(T.VIN_ATTESTATION, 1, rawWallet.address, rawSig, b(VIN), ''), 'invalid issuer signature', 'a RAW secp256k1 signature over the digest (no EIP-191 prefix, the CVIN-Combined convention) is rejected here — D25c: documented in _recoverSigner, NOT changed by the D25 fix');
  out('signature-scheme-D25c', 'offchain:issuer-signing', false, 0, 'D25c (recorded, not fixed): this contract ecrecovers the EIP-191-prefixed digest and rejects a raw one; CVINCombinedIdentity._recoverRawDigest does the opposite, so one issuer signature is not portable between the two claim contracts. Unifying the scheme (AFTER_ACTION_REPORT_05 §1 F7 recommends EIP-191, matching the VC layer and the ERC-4337 account) is a design decision left to the author');
  const good = ethers.Signature.from(await sign(manufacturer, T.VIN_ATTESTATION, b(VIN)));
  // ethers refuses to construct a non-canonical signature, so assemble the complementary (r, N-s, v') bytes by hand
  const highS = ethers.concat([good.r, ethers.toBeHex(SECP256K1_N - BigInt(good.s), 32), new Uint8Array([good.v === 27 ? 28 : 27])]);
  await reverts('malleable-high-s', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(T.VIN_ATTESTATION, 1, manufacturer.address, highS, b(VIN), ''), 'invalid signature s value', 'EIP-2 malleability guard: the complementary (high-s) signature is rejected even though ecrecover would accept it');
  await reverts('short-signature', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(T.VIN_ATTESTATION, 1, manufacturer.address, '0x1234', b(VIN), ''), 'invalid signature length', '65 bytes required');
  await reverts('unsupported-scheme', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(T.VIN_ATTESTATION, 2, manufacturer.address, good.serialized, b(VIN), ''), 'unsupported signature scheme', 'scheme must be 1 (ECDSA)');
  await reverts('zero-issuer', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(T.VIN_ATTESTATION, 1, ethers.ZeroAddress, good.serialized, b(VIN), ''), 'issuer is zero address', 'guard');
  await tx('addClaim-VIN_ATTESTATION', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(T.VIN_ATTESTATION, 1, manufacturer.address, good.serialized, b(VIN), ''), 'the valid VIN attestation finally anchored (authorised issuer, payload ends in this holder\'s VIN — D25b, see vin-linkage)');

  // self-issued claim: exempt from the registry
  const selfData = b('OWNER-NOTE:garage-kept');
  await tx('addClaim-self-issued', `${CONTRACT}.addClaim`, c.connect(vehicleOwner).addClaim(T.INSURANCE, 1, vehicleOwner.address, await sign(vehicleOwner, T.INSURANCE, selfData), selfData, ''),
    'D25a exemption: issuer == owner needs no registry entry (the ERC-735 draft lets an identity issue claims about itself); a verifier reads issuer == owner as self-asserted');
  assert((await c.isAuthorizedIssuer(vehicleOwner.address, T.INSURANCE)) === false, 'owner not whitelisted');
  await tx('removeClaim-self-issued', `${CONTRACT}.removeClaim`, c.connect(vehicleOwner).removeClaim(claimId(vehicleOwner.address, T.INSURANCE)), 'and withdraws it again');

  // removal
  await reverts('removeClaim-by-stranger', `${CONTRACT}.removeClaim`, c.connect(stranger).removeClaim(claimId(insurer.address, T.INSURANCE)), 'caller is not owner nor issuer', 'access');
  await reverts('removeClaim-nonexistent', `${CONTRACT}.removeClaim`, c.connect(vehicleOwner).removeClaim(claimId(stranger.address, T.INSURANCE)), 'claim does not exist', 'guard');
  const r3 = await tx('removeClaim-by-owner', `${CONTRACT}.removeClaim`, c.connect(vehicleOwner).removeClaim(claimId(insurer.address, T.INSURANCE)), 'MEASURED (benchmark revoke; L1 revoke 69,438): delete + topic-index compaction, storage refund; ClaimRemoved carries the full claim');
  assert(eventsOf(r3, c, 'ClaimRemoved').length === 1, 'ClaimRemoved');
  await tx('removeClaim-by-issuer', `${CONTRACT}.removeClaim`, c.connect(inspector).removeClaim(claimId(inspector.address, T.INSPECTION)), 'issuer-side revocation: the inspection authority withdraws its own attestation without the owner');
  assert((await view('claimExists-after', `${CONTRACT}.claimExists`, c.claimExists(inspector.address, T.INSPECTION), (v) => `claimExists(inspector, INSPECTION) == ${v}`)) === false, 'removed');
  out('automation-note', `${CONTRACT}.getClaim`, true, 0, 'automation: the chain verifies issuer signatures at anchoring time AND (D25a) that the issuer is on the holder\'s per-topic registry — or is the owner itself —, so later verifiers trust getClaim without crypto and without re-checking the issuer against a whitelist; what it still cannot check: that a registered issuer is a genuinely accredited authority (the owner decides whom to admit — there is no global/OEM-level registry) or that the claim is still current (no expiry field) — those stay off-chain');
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(id);
  const a = await ad.addClaim(id, 3, 'APK:2028', '0x', { issuerSigner: inspector });
  out('adapter-addClaim', `${CONTRACT}.addClaim`, true, a.gasUsed, `adapter: ${a.note}`);
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve-claims', 'adapter.resolve', true, 0, `resolve lists ${doc.claims.length} claims: ${doc.claims.map((x) => x.topicName).join(', ')}`);
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
