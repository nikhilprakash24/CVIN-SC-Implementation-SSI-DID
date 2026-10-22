'use strict';
/**
 * erc-1056-uport / signed-execution — the five ERC-1056 meta-transaction entry points
 * (setAttributeSigned, addDelegateSigned, revokeDelegateSigned, revokeAttributeSigned,
 * changeOwnerSigned): raw-digest secp256k1 signatures (no EIP-191), per-owner nonce, replay and
 * forgery rejection, relayer pays the gas.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-uport/demos/signed-execution.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-uport';
const FAMILY = 'signed-execution';
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
const h = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));
const b = (s) => ethers.hexlify(ethers.toUtf8Bytes(s));
const short = (a) => `${String(a).slice(0, 10)}…`;

const VIN = 'JH4KA7561PC008269';
const ONE_YEAR = 31536000;

async function main() {
  const [deployer, , newOwner, delegate] = await ethers.getSigners();
  const W = ethers.Wallet.createRandom().connect(ethers.provider); // the vehicle's controller key (never sends a tx here)
  await (await deployer.sendTransaction({ to: W.address, value: ethers.parseEther('1') })).wait();
  const registry = await (await ethers.getContractFactory('EthereumDIDRegistry', deployer)).deploy();
  out('deploy-registry', 'EthereumDIDRegistry.constructor', true, (await registry.deploymentTransaction().wait()).gasUsed, 'shared did:ethr registry');
  const regAddr = await registry.getAddress();
  const relayer = deployer;

  out('digest-scheme', 'EthereumDIDRegistry.nonce', false, 0,
    'off-chain: the controller signs keccak256(abi.encodePacked(0x19, 0x00, registry, nonce[identityOwner(identity)], identity, "<op>", …args)) with raw secp256k1 (no "\\x19Ethereum Signed Message" prefix, so wallets that only expose personal_sign cannot produce it); the relayer submits and pays');
  const sign = async (op, types, values) => {
    const n = await registry.nonce(await registry.identityOwner(W.address));
    const d = ethers.solidityPackedKeccak256(['bytes1', 'bytes1', 'address', 'uint256', 'address', 'string', ...types], ['0x19', '0x00', regAddr, n, W.address, op, ...values]);
    const sg = W.signingKey.sign(d);
    return { v: sg.v, r: sg.r, s: sg.s, nonce: n };
  };
  assert((await view('nonce-initial', 'EthereumDIDRegistry.nonce', registry.nonce(W.address), (v) => `nonce[${short(W.address)}] == ${v}; the nonce is keyed by the OWNER address, not the identity`)) === 0n, 'nonce 0');

  const KEY = h('did/pub/secp256k1/veriKey');
  const pub = ethers.hexlify(ethers.randomBytes(33));
  let s = await sign('setAttribute', ['bytes32', 'bytes', 'uint256'], [KEY, pub, ONE_YEAR]);
  await tx('setAttributeSigned', 'EthereumDIDRegistry.setAttributeSigned', registry.connect(relayer).setAttributeSigned(W.address, s.v, s.r, s.s, KEY, pub, ONE_YEAR), `nonce ${s.nonce} consumed; vehicle key publication paid by the relayer (not measured)`);
  const VERIKEY = h('veriKey');
  s = await sign('addDelegate', ['bytes32', 'address', 'uint256'], [VERIKEY, delegate.address, ONE_YEAR]);
  const sigReplay = s;
  await tx('addDelegateSigned', 'EthereumDIDRegistry.addDelegateSigned', registry.connect(relayer).addDelegateSigned(W.address, s.v, s.r, s.s, VERIKEY, delegate.address, ONE_YEAR), `nonce ${s.nonce} consumed (not measured)`);
  assert(await registry.validDelegate(W.address, VERIKEY, delegate.address), 'delegate added');
  await reverts('replay-rejected', 'EthereumDIDRegistry.addDelegateSigned', registry.connect(relayer).addDelegateSigned(W.address, sigReplay.v, sigReplay.r, sigReplay.s, VERIKEY, delegate.address, ONE_YEAR), 'DIDRegistry: invalid signature', 'resubmitting the same signature fails because the nonce moved (replay protection)');
  const forged = ethers.Wallet.createRandom().signingKey.sign(ethers.keccak256(b('forged')));
  await reverts('forgery-rejected', 'EthereumDIDRegistry.setAttributeSigned', registry.connect(relayer).setAttributeSigned(W.address, forged.v, forged.r, forged.s, KEY, b('evil'), 60), 'DIDRegistry: invalid signature', 'a signature by any other key recovers to a different address');
  s = await sign('revokeDelegate', ['bytes32', 'address'], [VERIKEY, delegate.address]);
  await tx('revokeDelegateSigned', 'EthereumDIDRegistry.revokeDelegateSigned', registry.connect(relayer).revokeDelegateSigned(W.address, s.v, s.r, s.s, VERIKEY, delegate.address), `nonce ${s.nonce} consumed (not measured)`);
  s = await sign('revokeAttribute', ['bytes32', 'bytes'], [KEY, pub]);
  await tx('revokeAttributeSigned', 'EthereumDIDRegistry.revokeAttributeSigned', registry.connect(relayer).revokeAttributeSigned(W.address, s.v, s.r, s.s, KEY, pub), `nonce ${s.nonce} consumed (not measured)`);
  s = await sign('changeOwner', ['address'], [newOwner.address]);
  await tx('changeOwnerSigned', 'EthereumDIDRegistry.changeOwnerSigned', registry.connect(relayer).changeOwnerSigned(W.address, s.v, s.r, s.s, newOwner.address), `nonce ${s.nonce} consumed; the L1 suite measures this one as signed-op (96,053 gas in the asymmetry table)`);
  assert((await registry.identityOwner(W.address)) === newOwner.address, 'controller rotated');
  assert((await view('nonce-final', 'EthereumDIDRegistry.nonce', registry.nonce(W.address), (v) => `nonce[old controller] == ${v} after five signed operations`)) === 5n, 'nonce 5');
  assert((await view('nonce-new-owner', 'EthereumDIDRegistry.nonce', registry.nonce(newOwner.address), (v) => `nonce[new controller] == ${v}: after changeOwnerSigned further signed ops must be signed by the new controller and use ITS nonce`)) === 0n, 'new owner nonce 0');
  out('adapter-signedOp', 'adapter.signedOp', true, 0, 'the S2 adapter wires only changeOwnerSigned (signs with a key derived from the Hardhat mnemonic); the other four signed entry points are exercised only by this demo');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
