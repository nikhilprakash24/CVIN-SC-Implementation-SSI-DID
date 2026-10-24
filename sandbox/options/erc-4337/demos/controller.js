'use strict';
/**
 * ERC-4337 — family "Ownership / controller change" (manifest: measured-in-comparison via
 * recoverOwner; transferOwnership is the benchmark's transferOwnership op). Controller change =
 * signing-key rotation; the identity (account address) never changes. Three ways to rotate:
 * transferOwnership called directly by the owner key, transferOwnership carried inside a
 * UserOperation (owner signs, bundler pays), and recoverOwner by the guardian. Also the self-call
 * path through execute() and the guards.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-4337/demos/controller.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs } = require('./_lib');

const d = demo('erc-4337', 'controller');

async function signedOp(ep, acct, signer, callData) {
  const sender = await acct.getAddress();
  const op = { sender, nonce: await ep.nonces(sender), initCode: '0x', callData, accountGasLimits: ethers.ZeroHash, preVerificationGas: 0, gasFees: ethers.ZeroHash, paymasterAndData: '0x', signature: '0x' };
  const hash = await ep.getUserOpHash(op);
  op.signature = await signer.signMessage(ethers.getBytes(hash));
  return op;
}

d.run(async () => {
  const [bundler, guardian, stranger] = await ethers.getSigners();
  const { assert } = d;
  const ep = await (await ethers.getContractFactory('CVINMinimalEntryPoint', bundler)).deploy();
  await ep.waitForDeployment();
  const key1 = ethers.Wallet.createRandom().connect(ethers.provider);
  const key2 = ethers.Wallet.createRandom().connect(ethers.provider);
  const key3 = ethers.Wallet.createRandom().connect(ethers.provider);
  const key4 = ethers.Wallet.createRandom().connect(ethers.provider);
  await (await bundler.sendTransaction({ to: key1.address, value: ethers.parseEther('1') })).wait();
  const acct = await (await ethers.getContractFactory('CVINVehicleAccount', bundler)).deploy(await ep.getAddress(), key1.address);
  await acct.waitForDeployment();
  const id = await acct.getAddress();
  d.offchain('setup', 'CVINVehicleAccount.constructor', `account ${id} with owner key1 (funded with 1 ETH only for the direct-call steps)`);

  await d.view('owner-0', 'CVINVehicleAccount.owner', acct.owner(), 'controller = owner key', (v) => assert.equal(v, key1.address));
  await d.reverts('rotate-unauthorised', 'CVINVehicleAccount.transferOwnership', () => acct.connect(stranger).transferOwnership(stranger.address), 'not owner or entryPoint', 'onlyOwnerOrEntryPoint gate');
  await d.reverts('rotate-to-zero', 'CVINVehicleAccount.transferOwnership', () => acct.connect(key1).transferOwnership(ethers.ZeroAddress), 'zero owner', 'cannot orphan the identity');
  const r1 = await d.tx('rotate-direct', 'CVINVehicleAccount.transferOwnership', acct.connect(key1).transferOwnership(key2.address), 'MEASURED (transferOwnership): direct call by the owner key; identity address unchanged -> OwnershipTransferred');
  const e1 = eventArgs(acct, r1, 'OwnershipTransferred'); assert.equal(e1.previousOwner, key1.address); assert.equal(e1.newOwner, key2.address);
  await d.view('owner-1', 'CVINVehicleAccount.owner', acct.owner(), 'key2 now controls; key1 is dead', (v) => assert.equal(v, key2.address));
  await d.reverts('old-key-locked-out', 'CVINVehicleAccount.transferOwnership', () => acct.connect(key1).transferOwnership(key1.address), 'not owner or entryPoint', 'the rotated-out key has no power left');

  const op = await signedOp(ep, acct, key2, acct.interface.encodeFunctionData('transferOwnership', [key3.address]));
  const r2 = await d.tx('rotate-via-userop', 'CVINMinimalEntryPoint.handleOp -> CVINVehicleAccount.validateUserOp -> transferOwnership', ep.connect(bundler).handleOp(op),
    'key2 signs (EIP-191 over userOpHash) and holds NO ETH; the bundler pays gas; the entry point is the msg.sender the account trusts');
  assert.equal(eventArgs(acct, r2, 'OwnershipTransferred').newOwner, key3.address);
  await d.view('owner-2', 'CVINVehicleAccount.owner', acct.owner(), 'key3 controls', (v) => assert.equal(v, key3.address));
  await d.view('key2-never-paid', 'provider.getBalance', ethers.provider.getBalance(key2.address), 'the signing key paid nothing (0 ETH before and after)', (v) => assert.equal(v, 0n));

  const op2 = await signedOp(ep, acct, key3, acct.interface.encodeFunctionData('execute', [id, 0, acct.interface.encodeFunctionData('transferOwnership', [key4.address])]));
  const r3 = await d.tx('rotate-via-execute-selfcall', 'CVINMinimalEntryPoint.handleOp -> execute(self) -> transferOwnership', ep.connect(bundler).handleOp(op2),
    'canonical 4337 shape: callData = execute(target=self, 0, transferOwnership(key4)); the account calls itself (msg.sender == address(this) branch of the modifier) -> Executed + OwnershipTransferred');
  assert.equal(eventArgs(acct, r3, 'Executed').target, id);
  await d.view('owner-3', 'CVINVehicleAccount.owner', acct.owner(), 'key4 controls', (v) => assert.equal(v, key4.address));

  await d.reverts('recover-no-guardian', 'CVINVehicleAccount.recoverOwner', () => acct.connect(guardian).recoverOwner(guardian.address), 'not guardian', 'no guardian set: recovery impossible');
  const op3 = await signedOp(ep, acct, key4, acct.interface.encodeFunctionData('setGuardian', [guardian.address]));
  await d.tx('set-guardian-via-userop', 'CVINMinimalEntryPoint.handleOp -> setGuardian', ep.connect(bundler).handleOp(op3), 'key4 designates the manufacturer/fleet operator as guardian');
  d.offchain('key-lost', 'off-chain', 'scenario: key4 is lost (ECU replaced); the vehicle identity must survive');
  const r4 = await d.tx('recover-owner', 'CVINVehicleAccount.recoverOwner', acct.connect(guardian).recoverOwner(stranger.address), 'MEASURED (recoverOwner): guardian installs a new signing key without any signature from the lost key -> OwnerRecovered');
  const e4 = eventArgs(acct, r4, 'OwnerRecovered'); assert.equal(e4.guardian, guardian.address); assert.equal(e4.previousOwner, key4.address); assert.equal(e4.newOwner, stranger.address);
  await d.view('owner-4', 'CVINVehicleAccount.owner', acct.owner(), 'recovered key controls', (v) => assert.equal(v, stranger.address));
  await d.reverts('recover-unauthorised', 'CVINVehicleAccount.recoverOwner', () => acct.connect(bundler).recoverOwner(bundler.address), 'not guardian', 'only the guardian');
  await d.reverts('recover-to-zero', 'CVINVehicleAccount.recoverOwner', () => acct.connect(guardian).recoverOwner(ethers.ZeroAddress), 'zero owner', 'guard');
  assert.equal(await acct.getAddress(), id);
  d.offchain('identity-stable', 'CVINVehicleAccount', `after 4 rotations + 1 recovery the identity is still ${id}: credentials issued to the address stay valid (asymmetry vs ERC-721/1155 where the holder address IS the identity)`);
  d.offchain('transfer-vs-recover', 'CVINVehicleAccount.transferOwnership vs recoverOwner', 'transferOwnership needs the CURRENT key (or a UserOp it signed); recoverOwner needs only the guardian and emits a different event so a verifier can see the key was replaced without the old key\'s consent');
});
