'use strict';
/**
 * erc-725 / revocation — sub-identity revocation only: removeKey revokes a key; the only
 * identity-level exit is renounceOwnership (irreversible, no status flag for verifiers).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-725/demos/revocation.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-725';
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
const short = (a) => `${String(a).slice(0, 10)}…`;

const CONTRACT = 'CVIN_SCBasedAccOrID_DID_ERC725Basic';
const keyIdOf = (addr) => ethers.keccak256(ethers.AbiCoder.defaultAbiCoder().encode(['address'], [addr]));

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate, , inspector] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, vehicleOwner)).deploy();
  out('deploy-identity', `${CONTRACT}.constructor`, true, (await c.deploymentTransaction().wait()).gasUsed, 'per-vehicle proxy');
  const id = await c.getAddress();
  for (let i = 0; i < 6; i++) {
    await tx(`addKey-${i}`, `${CONTRACT}.addKey`, c.connect(vehicleOwner).addKey(keyIdOf(ethers.Wallet.createRandom().address), 2, 1), `filler ACTION key #${i} so removeKey has to scan a 7-element array`);
  }
  await tx('addKey-inspector', `${CONTRACT}.addKey`, c.connect(vehicleOwner).addKey(keyIdOf(inspector.address), 3, 1), 'CLAIM key to revoke (appended last, so the scan walks all entries)');
  assert((await view('getKeys-before', `${CONTRACT}.getKeys`, c.getKeys(), (v) => `${v.length} keys`)).length === 7, '7 keys');

  const r = await tx('removeKey', `${CONTRACT}.removeKey`, c.connect(vehicleOwner).removeKey(keyIdOf(inspector.address)),
    'MEASURED (benchmark revoke; L1 revoke 41,399 with 1 key): linear scan over allKeys + delete; cost grows with key count — compare the L1 figure');
  const g = await view('getKey-after', `${CONTRACT}.getKey`, c.getKey(keyIdOf(inspector.address)), (v) => `getKey -> purpose=${v[0]}: revoked key reads as zeros; an on-chain verifier checks revocation with ONE view (vs event replay in ERC-1056)`);
  assert(g[0] === 0n, 'removed');
  assert((await c.getKeys()).length === 6, 'compacted');
  void r;

  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(id);
  const na = await ad.revoke(id);
  assert(na.notApplicable === true, 'adapter N/A for bare id');
  out('adapter-revoke-bare-id', 'adapter.revoke', true, 0, `adapter.revoke(id) -> NotApplicable: ${na.reason}`);
  const k = await ad.addKeyOrDelegate(id, delegate.address, 'action');
  const rv = await ad.revoke({ id, key: delegate.address });
  out('adapter-revoke-key', `${CONTRACT}.removeKey`, true, rv.gasUsed, `adapter.revoke({ id, key }) -> ${rv.note} (added for ${k.gasUsed} gas)`);

  // identity-level: nothing but renounce
  assert(typeof c.isRevoked === 'undefined' && typeof c.revokeIdentity === 'undefined', 'no identity revocation');
  out('no-identity-revocation', `${CONTRACT}.owner`, true, 0, 'the ABI has no revokeIdentity/isRevoked: a decommissioned vehicle cannot be flagged; verifiers cannot distinguish "active" from "abandoned" except by owner() == 0');
  await tx('renounceOwnership', `${CONTRACT}.renounceOwnership`, c.connect(vehicleOwner).renounceOwnership(), 'the only identity-level exit: owner -> 0; the contract and its keys persist on-chain forever; irreversible; not measured');
  assert((await view('owner-after-renounce', `${CONTRACT}.owner`, c.owner(), (v) => `owner == ${v}: a verifier may treat owner()==0 as "revoked" by convention — the contract does not say so`)) === ethers.ZeroAddress, 'renounced');
  const keysLeft = await view('keys-survive-renounce', `${CONTRACT}.getKeys`, c.getKeys(), (v) => `getKeys() still returns ${v.length} keys after renounce: OBSERVATION — the keys are not cleared, so a naive resolver keeps presenting them as valid verification methods`);
  assert(keysLeft.length === 6, 'keys persist');
  await reverts('removeKey-after-renounce', `${CONTRACT}.removeKey`, c.connect(vehicleOwner).removeKey(keysLeft[0]), 'Only owner can remove keys', 'nobody can clean up afterwards');
  out('revocation-asymmetry', `${CONTRACT}.renounceOwnership`, true, 0, `summary: key revocation (${short(id)}: removeKey) is on-chain checkable in O(1); identity revocation does not exist (vs ERC1056Registry.revokeIdentity / isRevoked)`);
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
