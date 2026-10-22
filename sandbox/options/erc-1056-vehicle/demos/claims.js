'use strict';
/**
 * erc-1056-vehicle / claims — credentials are OFF-CHAIN by design: the chain only anchors the
 * vehicle's verification key (registerVehicle) that the off-chain W3C VC verifier resolves.
 * The Python provider's update/get/revoke_credential are recorded as off-chain steps.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-vehicle/demos/claims.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-vehicle';
const FAMILY = 'claims';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
const tx = async (step, fn, p, note) => { const r = await (await p).wait(); out(step, fn, true, r.gasUsed, note); return r; };
const view = async (step, fn, p, note) => { const v = await p; out(step, fn, true, 0, typeof note === 'function' ? note(v) : note); return v; };
const assert = (c, m) => { if (!c) throw new Error(`assertion failed: ${m}`); };
const h = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));
const short = (a) => `${String(a).slice(0, 10)}…`;

const VIN = '1HGCM82633A004352';
const PROVIDER = 'cv2x-testbed/identity/erc1056_provider.py';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  const d = await ad.deploy();
  out('deploy-registry', 'ERC1056Registry.constructor', true, d.gasUsed, 'shared registry');
  const registry = ad.registry;
  const id = vehicleOwner.address;
  const c = await ad.create({ vin: VIN, owner: id });
  out('registerVehicle-anchor', 'ERC1056Registry.registerVehicle', true, c.gasUsed, 'the ONLY on-chain part of the Claims family: the verification key a VC verifier resolves to check the vehicle\'s signature');
  const na = await ad.addClaim(id, 1, VIN);
  assert(na.notApplicable === true, 'adapter addClaim is N/A');
  out('adapter-addClaim', 'adapter.addClaim', true, 0, `adapter.addClaim -> NotApplicable: ${na.reason}`);
  assert(typeof registry.addClaim === 'undefined' && typeof registry.getClaim === 'undefined', 'no claim functions');
  out('no-claim-functions', 'ERC1056Registry.identityOwner', true, 0, 'the ABI has no addClaim/getClaim: an on-chain verifier (another contract) cannot check a credential at all — the on/off-chain asymmetry versus ERC-735 / CVIN-Combined');

  // the off-chain credential lifecycle, as the provider implements it
  out('offchain-update_credential', `offchain:${PROVIDER}#update_credential`, false, 0, `update_credential(vehicle_id, updates) (line 668): rewrites the off-chain VehicleCredential (VIN ${VIN}, make, model …) and re-signs it; no transaction`);
  out('offchain-get_credential', `offchain:${PROVIDER}#get_credential`, false, 0, 'get_credential(vehicle_id) (line 704): returns the stored W3C VC; verification = check the issuer signature against the key resolved from DIDAttributeChanged events');
  out('offchain-revoke_credential', `offchain:${PROVIDER}#revoke_credential`, false, 0, 'revoke_credential(vehicle_id, reason) (line 618): marks the VC revoked in the provider store AND calls revokeIdentity on-chain (see revocation demo) — the one place the two layers meet');
  out('offchain-vc-stack', 'offchain:2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py#issue_credential', false, 0, 'the generic SSI layer (vc_issuer.issue_credential / vc_verifier.verify_credential) issues the same kind of credential for any did:ethr subject; verifying it costs 0 gas but requires the verifier to run an event-replay resolver');
  assert((await view('key-still-resolvable', 'ERC1056Registry.identityOwner', registry.identityOwner(id), (v) => `identityOwner == ${short(v)}: the verifier\'s on-chain anchor for the subject DID`)) === id, 'anchor');
  const ev = await registry.queryFilter(registry.filters.DIDAttributeChanged(id), 0, 'latest');
  assert(ev.length === 1 && ev[0].args.name === h('did/pub/secp256k1/veriKey/base64'), 'key event');
  out('verifier-replays-key', 'ERC1056Registry.registerVehicle', true, 0, `verifier replays ${ev.length} DIDAttributeChanged event(s) to obtain the vehicle key (validTo=${ev[0].args.validTo}); automation: the chain enforces nothing about the credential itself`);
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
