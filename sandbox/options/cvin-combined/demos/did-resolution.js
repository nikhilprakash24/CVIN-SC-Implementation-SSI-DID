'use strict';
/**
 * cvin-combined / did-resolution — building a document that merges both halves: identityOwner +
 * the ERC-1056 event replay (delegates/attributes/services) + the stored claims
 * (getClaimIdsByTopic / getClaim / hasValidClaim); no caching, reads only.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/cvin-combined/demos/did-resolution.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers, network } = hre;

const OPTION = 'cvin-combined';
const FAMILY = 'did-resolution';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
const view = async (step, fn, p, note) => { const v = await p; out(step, fn, true, 0, typeof note === 'function' ? note(v) : note); return v; };
const assert = (c, m) => { if (!c) throw new Error(`assertion failed: ${m}`); };
const short = (a) => `${String(a).slice(0, 10)}…`;

const CONTRACT = 'CVINCombinedIdentity';
const VIN = '1HGCM82633A004352';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  const d = await ad.deploy();
  out('deploy-registry', `${CONTRACT}.constructor`, true, d.gasUsed, 'shared hybrid registry');
  const reg = ad.registry;
  const id = vehicleOwner.address;

  assert((await view('identityOwner-fresh', `${CONTRACT}.identityOwner`, reg.identityOwner(id), (v) => `identityOwner == ${short(v)} before any tx: resolvable from birth`)) === id, 'fresh');
  const r0 = await ad.resolve(id);
  out('resolve-empty', 'adapter.resolve', true, 0, `empty document: controller=${short(r0.value.controller)} verificationMethod=${r0.value.verificationMethod.length} claims=${r0.value.claims.length} events=${r0.value.meta.events}`);
  assert(r0.value.verificationMethod.length === 1 && r0.value.claims.length === 0, 'empty doc');
  const c = await ad.create({ vin: VIN, owner: id, anchorVin: true });
  out('create-anchorVin', `${CONTRACT}.addClaim`, true, c.gasUsed, 'VIN claim');
  const a1 = await ad.setAttribute(id, 'did/pub/secp256k1/veriKey', ethers.hexlify(ethers.randomBytes(33)), 31536000);
  out('setAttribute-veriKey', `${CONTRACT}.setAttribute`, true, a1.gasUsed, 'event-only key');
  const a2 = await ad.setAttribute(id, 'did/svc/telematics', 'mqtts://v2x.example/' + VIN, 86400);
  out('setAttribute-service', `${CONTRACT}.setAttribute`, true, a2.gasUsed, 'event-only service endpoint');
  const k = await ad.addKeyOrDelegate(id, delegate.address, 'sigAuth', 600);
  out('addDelegate-10min', `${CONTRACT}.addDelegate`, true, k.gasUsed, 'stored delegate, 600 s');
  const cl = await ad.addClaim(id, 2, JSON.stringify({ typeApproval: 'e4*2007/46*0123*05' }), '0x', { uri: 'ipfs://QmTypeApproval' });
  out('addClaim-manufacturer', `${CONTRACT}.addClaim`, true, cl.gasUsed, 'stored claim');

  const doc = (await ad.resolve(id)).value;
  out('resolve', 'adapter.resolve', true, 0, `did=${doc.id} controller=${short(doc.controller)} verificationMethod=${doc.verificationMethod.length} authentication=${doc.authentication.length} service=${doc.service.length} claims=${doc.claims.length} vin=${doc.vehicle.vin} events=${doc.meta.events}; sources: identityOwner + changed/event walk (+ range-scan fallback) + validDelegate + getClaimIdsByTopic/getClaim/hasValidClaim for topics 1..3`);
  assert(doc.verificationMethod.length === 3 && doc.service.length === 1 && doc.claims.length === 2 && doc.vehicle.vin === VIN, 'doc shape');
  assert(doc.claims.every((x) => x.valid === true), 'claims valid');
  const ids = await view('getClaimIdsByTopic-each', `${CONTRACT}.getClaimIdsByTopic`, reg.getClaimIdsByTopic(id, 2), (v) => `getClaimIdsByTopic(id, 2) -> ${v.length}: the claim half is enumerable per topic but there is no "all topics" enumeration — a resolver must know the topic vocabulary (1..3)`);
  assert(ids.length === 1, 'one');
  await network.provider.send('evm_increaseTime', [1200]);
  await network.provider.send('evm_mine');
  const doc2 = (await ad.resolve(id)).value;
  out('resolve-after-expiry', 'adapter.resolve', true, 0, `after +1200 s: authentication=${doc2.authentication.length} (delegate expired on-chain via validDelegate) claims=${doc2.claims.length} (claims never expire)`);
  assert(doc2.authentication.length === 1 && doc2.claims.length === 2, 'expiry asymmetry');
  out('onchain-vs-offchain-verification', `${CONTRACT}.hasValidClaim`, true, 0, 'two verification paths in one identity: a contract checks hasValidClaim/validDelegate in O(1) (safety-critical subset); an off-chain verifier additionally replays events for keys/services — the comparison measures neither path (resolve = 0 gas)');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
