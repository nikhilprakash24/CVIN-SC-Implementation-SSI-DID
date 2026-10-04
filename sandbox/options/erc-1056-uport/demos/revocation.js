'use strict';
/**
 * erc-1056-uport / revocation — sub-identity revocation only: attributes and delegates can be
 * revoked (direct and signed, plus the wrapper's revokeVerificationDelegate); there is no
 * identity-level revocation, and changeOwner(did, 0x0) silently restores self-control.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-uport/demos/revocation.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-uport';
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
const eventsOf = (receipt, c, name) => receipt.logs.map((l) => { try { return c.interface.parseLog(l); } catch (_) { return null; } }).filter((e) => e && e.name === name);
const h = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));
const b = (s) => ethers.hexlify(ethers.toUtf8Bytes(s));
const short = (a) => `${String(a).slice(0, 10)}…`;

const VIN = '5YJ3E1EA7KF317000';
const CAR = ['Tesla', 'Model 3', 2019, 'White', 'EM3-2019-7731', 1546300800, 'L2'];
const ONE_YEAR = 31536000;

async function main() {
  const [deployer, , , delegate, stranger] = await ethers.getSigners();
  const W = ethers.Wallet.createRandom().connect(ethers.provider);
  await (await deployer.sendTransaction({ to: W.address, value: ethers.parseEther('5') })).wait();
  const registry = await (await ethers.getContractFactory('EthereumDIDRegistry', deployer)).deploy();
  out('deploy-registry', 'EthereumDIDRegistry.constructor', true, (await registry.deploymentTransaction().wait()).gasUsed, 'shared did:ethr registry');
  const wrapper = await (await ethers.getContractFactory('CVINVehicleDIDRegistry', deployer)).deploy(await registry.getAddress());
  out('deploy-wrapper', 'CVINVehicleDIDRegistry.constructor', true, (await wrapper.deploymentTransaction().wait()).gasUsed, 'VIN wrapper');
  const regAddr = await registry.getAddress();
  await tx('createVehicleDID', 'CVINVehicleDIDRegistry.createVehicleDID', wrapper.connect(deployer).createVehicleDID(VIN, W.address, ...CAR), `vehicle ${VIN} -> DID ${short(W.address)}`);
  const sign = async (op, types, values) => {
    const n = await registry.nonce(await registry.identityOwner(W.address));
    const d = ethers.solidityPackedKeccak256(['bytes1', 'bytes1', 'address', 'uint256', 'address', 'string', ...types], ['0x19', '0x00', regAddr, n, W.address, op, ...values]);
    return W.signingKey.sign(d);
  };

  // ---- set up things to revoke ----
  const KEY = h('did/pub/secp256k1/veriKey');
  const pub = ethers.hexlify(ethers.randomBytes(33));
  const SVC = h('did/svc/telematics');
  const url = b('https://telematics.example/v1/' + VIN);
  await tx('setAttribute-key', 'EthereumDIDRegistry.setAttribute', registry.connect(W).setAttribute(W.address, KEY, pub, ONE_YEAR), 'publish the verification key (MEASURED as createIdentity)');
  await tx('setAttribute-service', 'EthereumDIDRegistry.setAttribute', registry.connect(W).setAttribute(W.address, SVC, url, ONE_YEAR), 'publish a service endpoint');
  const VERIKEY = h('veriKey');
  const SIGAUTH = h('sigAuth');
  await tx('addDelegate-veriKey', 'EthereumDIDRegistry.addDelegate', registry.connect(W).addDelegate(W.address, VERIKEY, delegate.address, ONE_YEAR), 'veriKey delegate for 1 year');
  await tx('addDelegate-sigAuth', 'EthereumDIDRegistry.addDelegate', registry.connect(W).addDelegate(W.address, SIGAUTH, delegate.address, ONE_YEAR), 'sigAuth delegate for 1 year');

  // ---- attribute revocation: direct and signed ----
  const ra = await tx('revokeAttribute', 'EthereumDIDRegistry.revokeAttribute', registry.connect(W).revokeAttribute(W.address, KEY, pub),
    'MEASURED (benchmark revoke = revokeAttribute of the published key): DIDAttributeChanged(validTo=0); name AND value must match the attribute being revoked');
  assert(eventsOf(ra, registry, 'DIDAttributeChanged')[0].args.validTo === 0n, 'validTo 0');
  await reverts('revokeAttribute-by-stranger', 'EthereumDIDRegistry.revokeAttribute', registry.connect(stranger).revokeAttribute(W.address, SVC, url), 'DIDRegistry: unauthorized', 'only the controller revokes');
  let s = await sign('revokeAttribute', ['bytes32', 'bytes'], [SVC, url]);
  await tx('revokeAttributeSigned', 'EthereumDIDRegistry.revokeAttributeSigned', registry.connect(deployer).revokeAttributeSigned(W.address, s.v, s.r, s.s, SVC, url), 'signed revocation relayed by deployer; not measured');
  await tx('revokeAttribute-nonexistent', 'EthereumDIDRegistry.revokeAttribute', registry.connect(W).revokeAttribute(W.address, h('did/svc/never-set'), b('x')),
    'OBSERVATION: revoking an attribute that was never set succeeds (event-only model: the chain cannot know what exists; the resolver ignores the orphan revocation)');

  // ---- delegate revocation: direct, signed, wrapper ----
  const rd = await tx('revokeDelegate', 'EthereumDIDRegistry.revokeDelegate', registry.connect(W).revokeDelegate(W.address, VERIKEY, delegate.address), 'delegates[...] = 0 + DIDDelegateChanged(validTo=0); manifest: "also supported at similar cost"');
  assert(eventsOf(rd, registry, 'DIDDelegateChanged')[0].args.validTo === 0n, 'delegate validTo 0');
  assert((await view('validDelegate-after', 'EthereumDIDRegistry.validDelegate', registry.validDelegate(W.address, VERIKEY, delegate.address), (v) => `validDelegate(veriKey) == ${v} — revocation is on-chain checkable (unlike attributes)`)) === false, 'revoked');
  s = await sign('revokeDelegate', ['bytes32', 'address'], [SIGAUTH, delegate.address]);
  await tx('revokeDelegateSigned', 'EthereumDIDRegistry.revokeDelegateSigned', registry.connect(deployer).revokeDelegateSigned(W.address, s.v, s.r, s.s, SIGAUTH, delegate.address), 'signed revocation relayed by deployer; not measured');
  assert((await registry.validDelegate(W.address, SIGAUTH, delegate.address)) === false, 'sigAuth revoked');

  // ---- no identity-level revocation ----
  await tx('changeOwner-to-zero', 'EthereumDIDRegistry.changeOwner', registry.connect(W).changeOwner(W.address, ethers.ZeroAddress), 'the only candidate for "revoking the identity" is to set the owner to address(0) …');
  const io = await view('identityOwner-after-zero', 'EthereumDIDRegistry.identityOwner', registry.identityOwner(W.address),
    (v) => `… but identityOwner falls back to the DID itself (${short(v)}): OBSERVATION — changeOwner(did, 0) RESTORES self-control instead of locking the identity; ERC-1056 has no identity-level revocation (the comparison's "revoke" is attribute revocation)`);
  assert(io === W.address, 'self-control restored');
  await tx('still-mutable', 'EthereumDIDRegistry.setAttribute', registry.connect(W).setAttribute(W.address, KEY, pub, ONE_YEAR), 'proof: the DID address can keep mutating its document after the "zero-owner" transaction');

  // ---- wrapper-mediated delegate revocation ----
  await tx('hand-control-to-wrapper', 'EthereumDIDRegistry.changeOwner', registry.connect(W).changeOwner(W.address, await wrapper.getAddress()), 'wrapper becomes ERC-1056 owner');
  await tx('addVerificationDelegate', 'CVINVehicleDIDRegistry.addVerificationDelegate', wrapper.connect(W).addVerificationDelegate(W.address, delegate.address, VERIKEY, 86400), 'wrapper-mediated add');
  await tx('revokeVerificationDelegate', 'CVINVehicleDIDRegistry.revokeVerificationDelegate', wrapper.connect(W).revokeVerificationDelegate(W.address, delegate.address, VERIKEY), 'wrapper-mediated revokeDelegate; not measured');
  assert((await wrapper.isValidDelegate(W.address, VERIKEY, delegate.address)) === false, 'wrapper revoke applied');
  await reverts('revokeVerificationDelegate-by-stranger', 'CVINVehicleDIDRegistry.revokeVerificationDelegate', wrapper.connect(stranger).revokeVerificationDelegate(W.address, delegate.address, VERIKEY), 'not vehicle owner', 'wrapper authorises via vehicleOwnerOf');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
