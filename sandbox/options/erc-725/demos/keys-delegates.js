'use strict';
/**
 * erc-725 / keys-delegates — ERC-734-style key store: addKey with the four purposes
 * (MANAGEMENT=1, ACTION=2, CLAIM=3, ENCRYPTION=4) and key types (ECDSA=1, RSA=2), getKey,
 * getKeys, removeKey with array compaction; keys carry no expiry; duplicate addKey corrupts
 * the index.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-725/demos/keys-delegates.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-725';
const FAMILY = 'keys-delegates';
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
const short = (a) => `${String(a).slice(0, 10)}…`;

const CONTRACT = 'CVIN_SCBasedAccOrID_DID_ERC725Basic';
const keyIdOf = (addr) => ethers.keccak256(ethers.AbiCoder.defaultAbiCoder().encode(['address'], [addr]));
const PURPOSE = { 1: 'MANAGEMENT', 2: 'ACTION', 3: 'CLAIM', 4: 'ENCRYPTION' };

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate, stranger, inspector] = await ethers.getSigners();
  const c = await (await ethers.getContractFactory(CONTRACT, vehicleOwner)).deploy();
  out('deploy-identity', `${CONTRACT}.constructor`, true, (await c.deploymentTransaction().wait()).gasUsed, 'per-vehicle proxy');
  const id = await c.getAddress();

  const keys = [
    [keyIdOf(vehicleOwner.address), 1, 1, 'owner EOA as MANAGEMENT key'],
    [keyIdOf(delegate.address), 2, 1, 'telematics unit as ACTION key (closest analogue to an ERC-1056 veriKey delegate)'],
    [keyIdOf(inspector.address), 3, 1, 'inspection authority as CLAIM signer key (what benchmark addDelegateOrClaim measures)'],
    [ethers.keccak256(ethers.toUtf8Bytes('rsa:2048:' + ethers.hexlify(ethers.randomBytes(8)))), 4, 2, 'RSA ENCRYPTION key identified by hash (keyType 2)'],
  ];
  let first = null;
  for (const [k, p, t, why] of keys) {
    const r = await tx(`addKey-${PURPOSE[p]}`, `${CONTRACT}.addKey`, c.connect(vehicleOwner).addKey(k, p, t), `${why}; purpose=${p} type=${t}; ${p === 1 ? 'MEASURED (benchmark updateAttribute = addKey purpose 1, L1 key-or-delegate 137,096)' : p === 3 ? 'MEASURED (benchmark addDelegateOrClaim = addKey purpose 3)' : 'not measured'}`);
    const ev = eventsOf(r, c, 'KeyAdded');
    assert(ev.length === 1 && ev[0].args.purpose === BigInt(p) && ev[0].args.keyType === BigInt(t), 'KeyAdded');
    if (first === null) first = r.gasUsed;
  }
  await reverts('addKey-by-stranger', `${CONTRACT}.addKey`, c.connect(stranger).addKey(keyIdOf(stranger.address), 1, 1), 'Only owner can add keys', 'owner-gated (not the MANAGEMENT keys: owner() decides)');
  const all = await view('getKeys', `${CONTRACT}.getKeys`, c.getKeys(), (v) => `getKeys() -> ${v.length} key ids (stored array; readable by any contract — unlike ERC-1056 attributes)`);
  assert(all.length === 4, 'four keys');
  const g = await view('getKey-claim', `${CONTRACT}.getKey`, c.getKey(keyIdOf(inspector.address)), (v) => `getKey(inspector) -> purpose=${v[0]} (${PURPOSE[Number(v[0])]}) keyType=${v[1]} key=${short(v[2])}; NO validity/expiry field: keys live until removed (ERC-1056 delegates expire)`);
  assert(g[0] === 3n && g[1] === 1n, 'claim key');
  const gu = await view('getKey-unknown', `${CONTRACT}.getKey`, c.getKey(keyIdOf(stranger.address)), (v) => `getKey(unknown) -> purpose=${v[0]} keyType=${v[1]} key=${v[2]} (zeros, no revert)`);
  assert(gu[0] === 0n, 'unknown zero');

  // removeKey compacts the array (swap-and-pop)
  const rr = await tx('removeKey-middle', `${CONTRACT}.removeKey`, c.connect(vehicleOwner).removeKey(keyIdOf(delegate.address)),
    'MEASURED (benchmark revoke = removeKey; L1 revoke 41,399): delete struct + swap-and-pop of the ids array (cost grows with the number of keys); KeyRemoved');
  assert(eventsOf(rr, c, 'KeyRemoved').length === 1, 'KeyRemoved');
  const after = await view('getKeys-compacted', `${CONTRACT}.getKeys`, c.getKeys(), (v) => `getKeys() -> ${v.length}; order after swap-and-pop: ${v.map(short).join(', ')} (last element moved into the hole: enumeration order is not stable)`);
  assert(after.length === 3 && after[1] === keys[3][0], 'compacted');
  await reverts('removeKey-by-stranger', `${CONTRACT}.removeKey`, c.connect(stranger).removeKey(keyIdOf(inspector.address)), 'Only owner can remove keys', 'owner-gated');

  // duplicate addKey corrupts the index
  await tx('addKey-duplicate', `${CONTRACT}.addKey`, c.connect(vehicleOwner).addKey(keyIdOf(inspector.address), 2, 1), 'OBSERVATION: re-adding an existing key id overwrites the struct (purpose 3 -> 2) AND pushes the id a second time');
  const dup = await view('getKeys-duplicate', `${CONTRACT}.getKeys`, c.getKeys(), (v) => `getKeys() -> ${v.length} entries for 3 distinct keys (inspector listed twice)`);
  assert(dup.length === 4 && dup.filter((k) => k === keyIdOf(inspector.address)).length === 2, 'duplicate entry');
  await tx('removeKey-duplicate-once', `${CONTRACT}.removeKey`, c.connect(vehicleOwner).removeKey(keyIdOf(inspector.address)), 'removeKey deletes the struct but pops only ONE array entry …');
  const dangling = await view('getKeys-dangling', `${CONTRACT}.getKeys`, c.getKeys(), (v) => `… getKeys() still lists ${v.filter((k) => k === keyIdOf(inspector.address)).length} inspector id whose getKey() is now zeros: POTENTIAL DEFECT — a dangling index entry; resolvers must tolerate getKey() == (0,0,0) for listed ids`);
  assert(dangling.includes(keyIdOf(inspector.address)) && (await c.getKey(keyIdOf(inspector.address)))[0] === 0n, 'dangling');
  await tx('removeKey-nonexistent', `${CONTRACT}.removeKey`, c.connect(vehicleOwner).removeKey(keyIdOf(stranger.address)), 'OBSERVATION: removing a key that never existed succeeds and emits KeyRemoved (no existence check)');

  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach(id);
  const k = await ad.addKeyOrDelegate(id, newOwner.address, 'sigAuth', 3600);
  out('adapter-addKeyOrDelegate', `${CONTRACT}.addKey`, true, k.gasUsed, `adapter maps 'sigAuth' -> purpose 2 and IGNORES validitySeconds: ${k.note}`);
  const doc = (await ad.resolve(id)).value;
  out('adapter-resolve-keys', 'adapter.resolve', true, 0, `resolve lists keys=${doc.keys.length} (incl. the dangling id) from getKeys()+getKey(): ${doc.keys.map((x) => x.purposeName).join(', ')}`);
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
