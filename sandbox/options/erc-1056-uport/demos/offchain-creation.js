'use strict';
/**
 * erc-1056-uport / offchain-creation — an identity exists before any transaction: a freshly
 * generated, never-funded address already resolves (identityOwner == itself), and its FIRST
 * transaction is a mutation of the DID document, not a registration.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-uport/demos/offchain-creation.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-uport';
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
const short = (a) => `${String(a).slice(0, 10)}…`;

const VIN = '1HGCM82633A004352';

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate] = await ethers.getSigners();
  const registry = await (await ethers.getContractFactory('EthereumDIDRegistry', deployer)).deploy();
  out('deploy-registry', 'EthereumDIDRegistry.constructor', true, (await registry.deploymentTransaction().wait()).gasUsed, 'shared did:ethr registry');
  const wrapper = await (await ethers.getContractFactory('CVINVehicleDIDRegistry', deployer)).deploy(await registry.getAddress());
  out('deploy-wrapper', 'CVINVehicleDIDRegistry.constructor', true, (await wrapper.deploymentTransaction().wait()).gasUsed, 'VIN wrapper (only needed for the explicit path)');

  const A = ethers.Wallet.createRandom(); // generated off-chain, never funded, never seen by the chain
  out('keygen', 'offchain:secp256k1-keygen', false, 0, `vehicle generates a secp256k1 key pair offline -> address ${short(A.address)}; this address IS the DID (did:ethr:…:${short(A.address)}); no transaction, no gas`);
  assert((await view('identityOwner-fresh', 'EthereumDIDRegistry.identityOwner', registry.identityOwner(A.address), (v) => `identityOwner(fresh) == ${short(v)} (itself): the registry answers for an address it has never seen`)) === A.address, 'self-owned');
  assert((await view('changed-fresh', 'EthereumDIDRegistry.changed', registry.changed(A.address), (v) => `changed == ${v}`)) === 0n, 'no history');
  assert((await view('owners-fresh', 'EthereumDIDRegistry.owners', registry.owners(A.address), (v) => `owners[fresh] == ${v} (no storage was ever written)`)) === ethers.ZeroAddress, 'no owner slot');
  assert((await view('validDelegate-fresh', 'EthereumDIDRegistry.validDelegate', registry.validDelegate(A.address, h('veriKey'), delegate.address), (v) => `validDelegate == ${v} (empty document, but a VALID one: resolvers return a minimal did:ethr doc whose only verification method is the address itself)`)) === false, 'no delegates');
  assert((await view('nonce-fresh', 'EthereumDIDRegistry.nonce', registry.nonce(A.address), (v) => `nonce == ${v}: the fresh identity could already authorise a relayed meta-transaction (see signed-execution)`)) === 0n, 'nonce 0');

  const Adapter = require('../adapter');
  const ad = new Adapter({ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } });
  await ad.attach({ registry: await registry.getAddress(), wrapper: await wrapper.getAddress() });
  const c = await ad.create({ vin: VIN, owner: A.address, implicit: true });
  out('adapter-implicit-create', 'adapter.create', true, c.gasUsed, `adapter: implicit=${c.implicit}, gasUsed=${c.gasUsed} — the L1 table shows "create ✓ 0" for implicit options`);
  assert(c.implicit === true && c.gasUsed === 0n, 'implicit 0 gas');

  // first transaction is a mutation, not a creation
  const W = A.connect(ethers.provider);
  await (await deployer.sendTransaction({ to: A.address, value: ethers.parseEther('1') })).wait();
  const r = await tx('first-tx-is-a-mutation', 'EthereumDIDRegistry.addDelegate', registry.connect(W).addDelegate(A.address, h('sigAuth'), delegate.address, 3600),
    'the never-registered identity adds a delegate as its very first transaction: no create step exists in ERC-1056; the comparison instead measures a first setAttribute (77,792 gas in L1) and calls it "create"');
  assert(r.status === 1, 'first mutation ok');
  const r2 = await tx('comparison-create-proxy', 'EthereumDIDRegistry.setAttribute', registry.connect(W).setAttribute(A.address, h('did/pub/secp256k1/veriKey'), ethers.hexlify(ethers.randomBytes(33)), 31536000),
    'the operation the comparison labels createIdentity for ERC-1056 (first key publication) — a convention, not a contract requirement');
  const r3 = await tx('explicit-alternative', 'CVINVehicleDIDRegistry.createVehicleDID', wrapper.connect(deployer).createVehicleDID(VIN, A.address, 'Honda', 'Accord', 2003, 'Silver', 'K24A4', 1041379200, 'L0'),
    `explicit VIN-bound alternative for contrast: ${0} vs setAttribute-as-create vs createVehicleDID`);
  out('asymmetry-summary', 'EthereumDIDRegistry.identityOwner', true, 0, `creation cost ladder for the same identity: implicit 0 | first setAttribute ${r2.gasUsed} | createVehicleDID ${r3.gasUsed} (wrapper storage) — only the middle one is in the comparison`);
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
