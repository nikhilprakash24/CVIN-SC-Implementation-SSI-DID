'use strict';
/**
 * cvin-combined / offchain-creation — the ERC-1056 base makes every address an identity before
 * any transaction: a fresh, unfunded address already owns itself, holds no claims, and its first
 * transaction can be a claim anchoring (no registration step exists).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/cvin-combined/demos/offchain-creation.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'cvin-combined';
const FAMILY = 'offchain-creation';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
const tx = async (step, fn, p, note) => { const r = await (await p).wait(); out(step, fn, true, r.gasUsed, note); return r; };
const view = async (step, fn, p, note) => { const v = await p; out(step, fn, true, 0, typeof note === 'function' ? note(v) : note); return v; };
const assert = (c, m) => { if (!c) throw new Error(`assertion failed: ${m}`); };
const h = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));
const b = (s) => ethers.hexlify(ethers.toUtf8Bytes(s));
const short = (a) => `${String(a).slice(0, 10)}…`;

const CONTRACT = 'CVINCombinedIdentity';
const VIN = '1HGCM82633A004352';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const reg = await (await ethers.getContractFactory(CONTRACT, deployer)).deploy();
  out('deploy-registry', `${CONTRACT}.constructor`, true, (await reg.deploymentTransaction().wait()).gasUsed, 'shared hybrid registry');
  const regAddr = await reg.getAddress();
  const A = ethers.Wallet.createRandom(); // the vehicle key, generated in the factory, never seen by the chain
  const oem = ethers.Wallet.createRandom();
  out('keygen', 'offchain:secp256k1-keygen', false, 0, `vehicle key pair generated offline -> identity ${short(A.address)}; no transaction`);
  assert((await view('identityOwner-fresh', `${CONTRACT}.identityOwner`, reg.identityOwner(A.address), (v) => `identityOwner(fresh) == ${short(v)} (itself)`)) === A.address, 'self');
  assert((await view('changed-fresh', `${CONTRACT}.changed`, reg.changed(A.address), (v) => `changed == ${v}`)) === 0n, 'no history');
  assert((await view('hasValidClaim-fresh', `${CONTRACT}.hasValidClaim`, reg.hasValidClaim(A.address, 1, oem.address), (v) => `hasValidClaim(fresh, VIN, oem) == ${v}: an identity with no claims is still a valid identity — "exists" and "is trusted" are separate questions`)) === false, 'no claims');
  assert((await view('getClaimIdsByTopic-fresh', `${CONTRACT}.getClaimIdsByTopic`, reg.getClaimIdsByTopic(A.address, 1), (v) => `getClaimIdsByTopic(fresh, VIN) -> ${v.length}`)).length === 0, 'empty');
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(regAddr);
  const c = await ad.create({ vin: VIN, owner: A.address });
  out('adapter-create-implicit', 'adapter.create', true, c.gasUsed, `adapter: implicit=${c.implicit} gasUsed=${c.gasUsed} — L1 "create ✓ 0" (manifest note: the auto-generated stance for this family was not-applicable; the contract and the adapter say implicit)`);
  assert(c.implicit === true && c.gasUsed === 0n, 'implicit');

  // the OEM can even sign the VIN claim before the vehicle ever touches the chain
  const sig = ethers.Signature.from(oem.signingKey.sign(ethers.solidityPackedKeccak256(['address', 'address', 'uint256', 'bytes'], [regAddr, A.address, 1, b(VIN)]))).serialized;
  out('oem-presigns-claim', 'offchain:issuer-signing', false, 0, 'the OEM signs the VIN claim for the not-yet-active identity at the factory (digest binds registry + identity + topic + data); the vehicle carries it until it first goes online');
  const W = A.connect(ethers.provider);
  await (await deployer.sendTransaction({ to: A.address, value: ethers.parseEther('1') })).wait();
  const r1 = await tx('first-tx-is-addClaim', `${CONTRACT}.addClaim`, reg.connect(W).addClaim(A.address, 1, 1, oem.address, sig, b(VIN), ''), 'the identity\'s FIRST transaction anchors the pre-signed VIN claim: no registration precedes it');
  assert((await reg.hasValidClaim(A.address, 1, oem.address)) === true, 'anchored');
  const r2 = await tx('comparison-create-proxy', `${CONTRACT}.setAttribute`, reg.connect(W).setAttribute(A.address, h('did/pub/secp256k1/veriKey'), ethers.hexlify(ethers.randomBytes(33)), 31536000), 'what the comparison labels createIdentity for the hybrid (first setAttribute)');
  out('creation-ladder', `${CONTRACT}.identityOwner`, true, 0, `creation cost ladder: implicit 0 | first setAttribute ${r2.gasUsed} (the comparison's "create") | first addClaim ${r1.gasUsed} (a trusted identity) — only the middle is measured`);
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
