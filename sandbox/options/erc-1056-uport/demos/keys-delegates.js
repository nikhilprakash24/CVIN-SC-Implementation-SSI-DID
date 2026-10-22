'use strict';
/**
 * erc-1056-uport / keys-delegates — time-bound delegates (veriKey / sigAuth), expiry without a
 * transaction, signed variants, and the wrapper's addVerificationDelegate / revokeVerificationDelegate.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-uport/demos/keys-delegates.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers, network } = hre;

const OPTION = 'erc-1056-uport';
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
const h = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));
const short = (a) => `${String(a).slice(0, 10)}…`;

const VIN = '1HGCM82633A004352';
const CAR = ['Honda', 'Accord', 2003, 'Silver', 'K24A4-2003-0471', 1041379200, 'L0'];

async function main() {
  const [deployer, , , delegate, stranger] = await ethers.getSigners();
  const W = ethers.Wallet.createRandom().connect(ethers.provider);
  await (await deployer.sendTransaction({ to: W.address, value: ethers.parseEther('5') })).wait();
  const registry = await (await ethers.getContractFactory('EthereumDIDRegistry', deployer)).deploy();
  const r1 = await registry.deploymentTransaction().wait();
  out('deploy-registry', 'EthereumDIDRegistry.constructor', true, r1.gasUsed, 'shared did:ethr registry');
  const wrapper = await (await ethers.getContractFactory('CVINVehicleDIDRegistry', deployer)).deploy(await registry.getAddress());
  const r2 = await wrapper.deploymentTransaction().wait();
  out('deploy-wrapper', 'CVINVehicleDIDRegistry.constructor', true, r2.gasUsed, 'VIN wrapper');
  const regAddr = await registry.getAddress();
  await tx('createVehicleDID', 'CVINVehicleDIDRegistry.createVehicleDID', wrapper.connect(deployer).createVehicleDID(VIN, W.address, ...CAR), `vehicle ${VIN} -> DID ${short(W.address)}`);

  const VERIKEY = await view('DELEGATE_VERIKEY', 'CVINVehicleDIDRegistry.DELEGATE_VERIKEY', wrapper.DELEGATE_VERIKEY(), (v) => `keccak256("veriKey") = ${v} (did:ethr assertionMethod delegate type)`);
  assert(VERIKEY === h('veriKey'), 'VERIKEY constant');
  const SIGAUTH = await view('DELEGATE_SIGAUTH', 'CVINVehicleDIDRegistry.DELEGATE_SIGAUTH', wrapper.DELEGATE_SIGAUTH(), (v) => `keccak256("sigAuth") = ${v} (did:ethr authentication delegate type)`);
  assert(SIGAUTH === h('sigAuth'), 'SIGAUTH constant');

  // ---- direct delegate with 1h validity (the comparison measures addDelegate with 1y validity) ----
  const ra = await tx('addDelegate', 'EthereumDIDRegistry.addDelegate', registry.connect(W).addDelegate(W.address, VERIKEY, delegate.address, 3600),
    'MEASURED (benchmark addDelegateOrClaim): 1 SSTORE of validTo + DIDDelegateChanged; here validity 3600 s to demonstrate expiry');
  const ev = eventsOf(ra, registry, 'DIDDelegateChanged');
  assert(ev.length === 1 && ev[0].args.delegate === delegate.address, 'DIDDelegateChanged');
  const validTo = ev[0].args.validTo;
  const stored = await view('delegates-mapping', 'EthereumDIDRegistry.delegates', registry.delegates(W.address, VERIKEY, delegate.address), (v) => `delegates[did][veriKey][delegate] == ${v} == event validTo (${validTo}); unlike attributes, delegates ARE stored so other contracts can check them`);
  assert(stored === validTo, 'stored validTo');
  assert(await view('validDelegate-true', 'EthereumDIDRegistry.validDelegate', registry.validDelegate(W.address, VERIKEY, delegate.address), (v) => `validDelegate == ${v} (validTo > block.timestamp)`), 'valid now');
  assert(await view('isValidDelegate-wrapper', 'CVINVehicleDIDRegistry.isValidDelegate', wrapper.isValidDelegate(W.address, VERIKEY, delegate.address), (v) => `wrapper isValidDelegate == ${v} (pass-through to the registry)`), 'wrapper valid now');

  // ---- expiry: no transaction, the view flips ----
  await network.provider.send('evm_increaseTime', [7200]);
  await network.provider.send('evm_mine');
  const vd = await view('validDelegate-expired', 'EthereumDIDRegistry.validDelegate', registry.validDelegate(W.address, VERIKEY, delegate.address), (v) => `after +7200 s: validDelegate == ${v}; delegate validity EXPIRES on-chain without any revocation transaction (the comparison never exercises expiry)`);
  assert(vd === false, 'expired');

  // ---- signed (meta-transaction) add: controller signs the raw digest, deployer relays ----
  const signDel = async (op, types, values) => {
    const n = await registry.nonce(await registry.identityOwner(W.address));
    const d = ethers.solidityPackedKeccak256(['bytes1', 'bytes1', 'address', 'uint256', 'address', 'string', ...types], ['0x19', '0x00', regAddr, n, W.address, op, ...values]);
    return W.signingKey.sign(d);
  };
  let s = await signDel('addDelegate', ['bytes32', 'address', 'uint256'], [SIGAUTH, delegate.address, 31536000]);
  await tx('addDelegateSigned', 'EthereumDIDRegistry.addDelegateSigned', registry.connect(deployer).addDelegateSigned(W.address, s.v, s.r, s.s, SIGAUTH, delegate.address, 31536000),
    'sigAuth delegate for 1 year added by a relayer; raw-digest secp256k1 signature (no EIP-191), nonce consumed; not measured');
  assert(await view('validDelegate-sigAuth', 'EthereumDIDRegistry.validDelegate', registry.validDelegate(W.address, SIGAUTH, delegate.address), (v) => `sigAuth delegate valid == ${v}`), 'sigAuth valid');
  const bad = ethers.Wallet.createRandom().signingKey.sign(ethers.keccak256('0x1234'));
  await reverts('addDelegateSigned-bad-signature', 'EthereumDIDRegistry.addDelegateSigned', registry.connect(deployer).addDelegateSigned(W.address, bad.v, bad.r, bad.s, SIGAUTH, stranger.address, 3600), 'DIDRegistry: invalid signature', 'ecrecover result must equal identityOwner');

  // ---- revocation (direct and signed) ----
  const rr = await tx('revokeDelegate', 'EthereumDIDRegistry.revokeDelegate', registry.connect(W).revokeDelegate(W.address, VERIKEY, delegate.address), 'sets validTo = 0 and emits DIDDelegateChanged(validTo=0) (manifest: revoke "also supported at similar cost")');
  assert(eventsOf(rr, registry, 'DIDDelegateChanged')[0].args.validTo === 0n, 'validTo 0');
  s = await signDel('revokeDelegate', ['bytes32', 'address'], [SIGAUTH, delegate.address]);
  await tx('revokeDelegateSigned', 'EthereumDIDRegistry.revokeDelegateSigned', registry.connect(deployer).revokeDelegateSigned(W.address, s.v, s.r, s.s, SIGAUTH, delegate.address), 'signed revocation relayed by deployer');
  assert((await registry.validDelegate(W.address, SIGAUTH, delegate.address)) === false, 'sigAuth revoked');
  assert((await view('delegates-after-revoke', 'EthereumDIDRegistry.delegates', registry.delegates(W.address, SIGAUTH, delegate.address), (v) => `delegates[did][sigAuth][delegate] == ${v}`)) === 0n, 'cleared');

  // ---- wrapper path: requires the wrapper to be the ERC-1056 owner first ----
  await reverts('wrapper-delegate-before-handoff', 'CVINVehicleDIDRegistry.addVerificationDelegate', wrapper.connect(W).addVerificationDelegate(W.address, delegate.address, VERIKEY, 86400), 'DIDRegistry: unauthorized',
    'the wrapper passes its onlyVehicleOwner check but the inner registry call fails because the wrapper is not the ERC-1056 owner yet');
  await tx('hand-control-to-wrapper', 'EthereumDIDRegistry.changeOwner', registry.connect(W).changeOwner(W.address, await wrapper.getAddress()), 'vehicle owner makes the wrapper the ERC-1056 owner');
  await tx('addVerificationDelegate', 'CVINVehicleDIDRegistry.addVerificationDelegate', wrapper.connect(W).addVerificationDelegate(W.address, delegate.address, VERIKEY, 86400), 'wrapper-mediated addDelegate (one extra external call); not measured');
  assert(await view('isValidDelegate-after-wrapper-add', 'CVINVehicleDIDRegistry.isValidDelegate', wrapper.isValidDelegate(W.address, VERIKEY, delegate.address), (v) => `isValidDelegate == ${v}`), 'wrapper add applied');
  await reverts('wrapper-delegate-by-stranger', 'CVINVehicleDIDRegistry.addVerificationDelegate', wrapper.connect(stranger).addVerificationDelegate(W.address, stranger.address, VERIKEY, 86400), 'not vehicle owner', 'wrapper authorises via vehicleOwnerOf');
  await tx('revokeVerificationDelegate', 'CVINVehicleDIDRegistry.revokeVerificationDelegate', wrapper.connect(W).revokeVerificationDelegate(W.address, delegate.address, VERIKEY), 'wrapper-mediated revokeDelegate; not measured');
  assert((await wrapper.isValidDelegate(W.address, VERIKEY, delegate.address)) === false, 'wrapper revoke applied');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
