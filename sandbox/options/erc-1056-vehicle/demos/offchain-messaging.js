'use strict';
/**
 * erc-1056-vehicle / offchain-messaging — the V2X hot path: a vehicle signs a safety message
 * off-chain (EIP-191 personal_sign, as erc1056_provider.sign_message does), the receiver
 * recovers the signer and makes exactly two on-chain reads (identityOwner, isRevoked). No gas.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-vehicle/demos/offchain-messaging.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-vehicle';
const FAMILY = 'offchain-messaging';
let steps = 0;
const out = (step, fn, onchain, gasUsed, note) => {
  steps += 1;
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, step, fn, onchain, gasUsed: String(gasUsed ?? 0), note }));
};
const tx = async (step, fn, p, note) => { const r = await (await p).wait(); out(step, fn, true, r.gasUsed, note); return r; };
const view = async (step, fn, p, note) => { const v = await p; out(step, fn, true, 0, typeof note === 'function' ? note(v) : note); return v; };
const assert = (c, m) => { if (!c) throw new Error(`assertion failed: ${m}`); };
const short = (a) => `${String(a).slice(0, 10)}…`;

const VIN = '1HGCM82633A004352';
const PROVIDER = 'cv2x-testbed/identity/erc1056_provider.py';

async function main() {
  const [deployer, vehicleOwner, , , stranger] = await ethers.getSigners();
  const registry = await (await ethers.getContractFactory('ERC1056Registry', deployer)).deploy();
  out('deploy-registry', 'ERC1056Registry.constructor', true, (await registry.deploymentTransaction().wait()).gasUsed, 'shared registry');
  const id = vehicleOwner.address;
  await tx('registerVehicle', 'ERC1056Registry.registerVehicle', registry.connect(vehicleOwner).registerVehicle(id, '0x04' + 'ab'.repeat(64)), 'vehicle registered once; everything below is gas-free');

  // sender side (sign_message, line 405)
  const bsm = { type: 'BSM', vin: VIN, lat: 51.4416, lon: 5.4697, speed_kmh: 48, heading: 92, ts: 1759564800 };
  const payload = JSON.stringify(bsm);
  const t0 = process.hrtime.bigint();
  const signature = await vehicleOwner.signMessage(payload);
  const signMs = Number(process.hrtime.bigint() - t0) / 1e6;
  out('sign_message', `offchain:${PROVIDER}#sign_message`, false, 0, `vehicle signs the BSM JSON with EIP-191 personal_sign (keccak256("\\x19Ethereum Signed Message:\\n" + len + msg)), 65-byte secp256k1 signature, ${signMs.toFixed(2)} ms in-process; mirrors sign_message (line 405)`);

  // receiver side (verify_message, line 439)
  const t1 = process.hrtime.bigint();
  const recovered = ethers.verifyMessage(payload, signature);
  const verifyMs = Number(process.hrtime.bigint() - t1) / 1e6;
  assert(recovered === id, 'recovered signer');
  out('verify_message-recover', `offchain:${PROVIDER}#verify_message`, false, 0, `receiver recovers signer ${short(recovered)} from the signature (${verifyMs.toFixed(2)} ms, no chain access); mirrors verify_message (line 439) step 1`);
  const owner = await view('verify_message-identityOwner', 'ERC1056Registry.identityOwner', registry.identityOwner(recovered), (v) => `on-chain read 1: identityOwner(signer) == ${short(v)} — the signer controls its DID (or is its controller)`);
  assert(owner === id, 'self-controlled');
  const rev = await view('verify_message-isRevoked', 'ERC1056Registry.isRevoked', registry.isRevoked(recovered), (v) => `on-chain read 2: isRevoked == ${v} — accept the message`);
  assert(rev === false, 'not revoked');

  // tampering and revocation both fail closed
  const tampered = JSON.stringify({ ...bsm, speed_kmh: 148 });
  const r2 = ethers.verifyMessage(tampered, signature);
  assert(r2 !== id, 'tamper detected');
  out('verify_message-tampered', `offchain:${PROVIDER}#verify_message`, false, 0, `altered payload recovers ${short(r2)} != ${short(id)}: rejected without any chain access`);
  const strangerSig = await stranger.signMessage(payload);
  const r3 = ethers.verifyMessage(payload, strangerSig);
  const strangerInfo = await registry.getIdentityInfo(r3);
  out('verify_message-unregistered-signer', 'ERC1056Registry.getIdentityInfo', true, 0, `a signature from an unregistered address ${short(r3)} still recovers fine and identityOwner == itself (lastChanged=${strangerInfo[1]}): OBSERVATION — the chain cannot distinguish "registered vehicle" from "any address"; the receiver must additionally require a registration event / credential (lastChanged > 0 or an off-chain VC)`);
  await tx('revokeIdentity', 'ERC1056Registry.revokeIdentity', registry.connect(vehicleOwner).revokeIdentity(id), 'vehicle decommissioned');
  assert((await view('verify_message-after-revoke', 'ERC1056Registry.isRevoked', registry.isRevoked(id), (v) => `isRevoked == ${v}: the same signature is now rejected by the receiver — revocation propagates with one chain read, no CRL`)) === true, 'revoked');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
