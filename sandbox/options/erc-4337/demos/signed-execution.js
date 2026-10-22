'use strict';
/**
 * ERC-4337 — family "Delegated / signed (off-chain-authorised) execution" (manifest: implemented,
 * not measured as such; the benchmark measures one handleOp as updateAttributeVia4337). The whole
 * UserOperation pipeline of this harness: getUserOpHash (v0.7-shaped hash, recomputed off-chain),
 * validateUserOp (EIP-191 envelope over the hash, SimpleAccount pattern, returns 1 instead of
 * reverting), handleOp (nonce check + bump, validation, inner call, UserOperationHandled), and
 * execute() both direct and inside a UserOperation. Negative cases: foreign signer, raw-digest
 * signature (no EIP-191 prefix), malformed length, nonce replay, direct validateUserOp call,
 * inner revert bubbling (nonce rolled back).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-4337/demos/signed-execution.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('erc-4337', 'signed-execution');

d.run(async () => {
  const [bundler, payee, stranger] = await ethers.getSigners();
  const { assert } = d;
  const ep = await (await ethers.getContractFactory('CVINMinimalEntryPoint', bundler)).deploy();
  await ep.waitForDeployment();
  const epAddr = await ep.getAddress();
  const vehicleKey = ethers.Wallet.createRandom().connect(ethers.provider); // off-chain key, never funded
  const acct = await (await ethers.getContractFactory('CVINVehicleAccount', bundler)).deploy(epAddr, vehicleKey.address);
  await acct.waitForDeployment();
  const id = await acct.getAddress();
  await (await bundler.sendTransaction({ to: id, value: ethers.parseEther('1') })).wait();
  const K = ethers.id('cvin/vehicle/vin');
  d.offchain('setup', 'CVINVehicleAccount.constructor', `account ${id} owned by an unfunded off-chain key ${vehicleKey.address}; account funded with 1 ETH; bundler = ${bundler.address}`);

  const mkOp = async (callData, nonce) => ({ sender: id, nonce: nonce ?? await ep.nonces(id), initCode: '0x', callData, accountGasLimits: ethers.ZeroHash, preVerificationGas: 0, gasFees: ethers.ZeroHash, paymasterAndData: '0x', signature: '0x' });

  // ---- hash: on-chain view vs off-chain recomputation ----
  const op = await mkOp(acct.interface.encodeFunctionData('setAttribute', [K, ethers.toUtf8Bytes(VINS.ford)]));
  const hash = await d.view('get-user-op-hash', 'CVINMinimalEntryPoint.getUserOpHash', ep.getUserOpHash(op), 'v0.7-style hash: keccak(abi.encode(keccak(packed fields), entryPoint, chainId)) — binds the op to this entry point and chain');
  const coder = ethers.AbiCoder.defaultAbiCoder();
  const packed = ethers.keccak256(coder.encode(['address', 'uint256', 'bytes32', 'bytes32', 'bytes32', 'uint256', 'bytes32', 'bytes32'],
    [op.sender, op.nonce, ethers.keccak256(op.initCode), ethers.keccak256(op.callData), op.accountGasLimits, op.preVerificationGas, op.gasFees, ethers.keccak256(op.paymasterAndData)]));
  const local = ethers.keccak256(coder.encode(['bytes32', 'address', 'uint256'], [packed, epAddr, (await ethers.provider.getNetwork()).chainId]));
  assert.equal(local, hash);
  d.offchain('recompute-hash-offchain', 'off-chain keccak256', 'a wallet can compute the exact digest without an RPC call: the hashing scheme is deterministic and public');

  // ---- signature scheme: EIP-191 over the hash ----
  op.signature = await vehicleKey.signMessage(ethers.getBytes(hash));
  d.offchain('sign-eip191', 'off-chain secp256k1 sign', 'owner signs keccak256("\\x19Ethereum Signed Message:\\n32" || userOpHash) — the SimpleAccount v0.7 envelope; 65-byte r||s||v');
  const r1 = await d.tx('handle-op', 'CVINMinimalEntryPoint.handleOp -> CVINVehicleAccount.validateUserOp -> setAttribute', ep.connect(bundler).handleOp(op),
    'happy path: nonce 0 checked+bumped, ecrecover == owner (returns 0), inner call executed -> UserOperationHandled(hash, sender, nonce, true) + AttributeChanged');
  const h = eventArgs(ep, r1, 'UserOperationHandled'); assert.equal(h.userOpHash, hash); assert.equal(h.nonce, 0n); assert.equal(h.success, true);
  await d.view('nonce-bumped', 'CVINMinimalEntryPoint.nonces', ep.nonces(id), 'plain sequential nonce (no v0.7 key||sequence split)', (v) => assert.equal(v, 1n));
  await d.view('attribute-written', 'CVINVehicleAccount.getAttribute', acct.getAttribute(K).then(ethers.toUtf8String), 'effect of the signed op', (v) => assert.equal(v, VINS.ford));
  await d.view('owner-key-unfunded', 'provider.getBalance', ethers.provider.getBalance(vehicleKey.address), 'the signer still holds 0 ETH: gas was paid by the bundler (gas abstraction)', (v) => assert.equal(v, 0n));

  // ---- negative cases ----
  await d.reverts('replay-same-nonce', 'CVINMinimalEntryPoint.handleOp', () => ep.connect(bundler).handleOp(op), 'invalid nonce', 'the same signed op cannot be replayed (nonce 0 already consumed)');
  const foreign = await mkOp(acct.interface.encodeFunctionData('setAttribute', [K, '0x00']));
  foreign.signature = await stranger.signMessage(ethers.getBytes(await ep.getUserOpHash(foreign)));
  await d.reverts('foreign-signature', 'CVINMinimalEntryPoint.handleOp', () => ep.connect(bundler).handleOp(foreign), 'signature validation failed', 'valid EIP-191 signature by the wrong key: validateUserOp returns SIG_VALIDATION_FAILED (1) and the entry point reverts');
  const raw = await mkOp(acct.interface.encodeFunctionData('setAttribute', [K, '0x00']));
  raw.signature = vehicleKey.signingKey.sign(await ep.getUserOpHash(raw)).serialized;
  await d.reverts('raw-digest-signature', 'CVINMinimalEntryPoint.handleOp', () => ep.connect(bundler).handleOp(raw), 'signature validation failed', 'the RIGHT key signing the RAW userOpHash (no EIP-191 prefix) is rejected: the envelope is part of the scheme (contrast ERC-1056 *Signed which hash raw bytes)');
  const short = await mkOp(acct.interface.encodeFunctionData('setAttribute', [K, '0x00']));
  short.signature = ethers.dataSlice(await vehicleKey.signMessage(ethers.getBytes(await ep.getUserOpHash(short))), 0, 64);
  await d.reverts('malformed-signature', 'CVINMinimalEntryPoint.handleOp', () => ep.connect(bundler).handleOp(short), 'signature validation failed', '64-byte signature: length check fails before ecrecover');
  const future = await mkOp(acct.interface.encodeFunctionData('setAttribute', [K, '0x00']), 5);
  future.signature = await vehicleKey.signMessage(ethers.getBytes(await ep.getUserOpHash(future)));
  await d.reverts('future-nonce', 'CVINMinimalEntryPoint.handleOp', () => ep.connect(bundler).handleOp(future), 'invalid nonce', 'nonce must equal the current sequence exactly (no gaps, no parallel keys)');
  await d.reverts('validate-direct-call', 'CVINVehicleAccount.validateUserOp', () => acct.connect(stranger).validateUserOp(op, hash, 0), 'not entryPoint', 'validateUserOp is callable only by the entry point');
  await d.reverts('stale-nonce-after-rotation', 'CVINMinimalEntryPoint.handleOp', async () => {
    const rot = await mkOp(acct.interface.encodeFunctionData('transferOwnership', [stranger.address]));
    rot.signature = await vehicleKey.signMessage(ethers.getBytes(await ep.getUserOpHash(rot)));
    await (await ep.connect(bundler).handleOp(rot)).wait(); // key rotated to `stranger` (nonce 1 -> 2)
    const old = await mkOp(acct.interface.encodeFunctionData('setAttribute', [K, '0x00']));
    old.signature = await vehicleKey.signMessage(ethers.getBytes(await ep.getUserOpHash(old)));
    return ep.connect(bundler).handleOp(old);
  }, 'signature validation failed', 'after a signed rotation (nonce 1) the old key\'s op on nonce 2 is rejected: validation reads the CURRENT owner');
  await d.view('nonce-after-rotation', 'CVINMinimalEntryPoint.nonces', ep.nonces(id), 'the rotation consumed nonce 1', (v) => assert.equal(v, 2n));

  // ---- execute(): direct and via UserOperation ----
  const owner = stranger; // current owner key after the rotation above (a funded Hardhat signer)
  await d.reverts('execute-unauthorised', 'CVINVehicleAccount.execute', () => acct.connect(bundler).execute(payee.address, 1, '0x'), 'not owner or entryPoint', 'execute is owner/entryPoint/self only');
  const before = await ethers.provider.getBalance(payee.address);
  const r2 = await d.tx('execute-direct-value', 'CVINVehicleAccount.execute', acct.connect(owner).execute(payee.address, ethers.parseEther('0.25'), '0x'), 'owner key calls execute directly: the ACCOUNT pays 0.25 ETH to a toll operator (identity-bound payment from contract funds) -> Executed');
  assert.equal(eventArgs(acct, r2, 'Executed').value, ethers.parseEther('0.25'));
  assert.equal((await ethers.provider.getBalance(payee.address)) - before, ethers.parseEther('0.25'));
  const exOp = await mkOp(acct.interface.encodeFunctionData('execute', [epAddr, 0, ep.interface.encodeFunctionData('nonces', [id])]));
  exOp.signature = await owner.signMessage(ethers.getBytes(await ep.getUserOpHash(exOp)));
  const r3 = await d.tx('execute-via-userop', 'CVINMinimalEntryPoint.handleOp -> execute(target)', ep.connect(bundler).handleOp(exOp), 'canonical shape: the op\'s callData is execute(target, value, data) — here the account calls an external contract (the entry point\'s nonces view) -> Executed');
  assert.equal(eventArgs(acct, r3, 'Executed').target, epAddr);
  const selfOp = await mkOp(acct.interface.encodeFunctionData('execute', [id, 0, acct.interface.encodeFunctionData('setAttribute', [ethers.id('cvin/vehicle/plate'), ethers.toUtf8Bytes('B-CV 1234')])]));
  selfOp.signature = await owner.signMessage(ethers.getBytes(await ep.getUserOpHash(selfOp)));
  await d.tx('execute-selfcall-via-userop', 'CVINMinimalEntryPoint.handleOp -> execute(self) -> setAttribute', ep.connect(bundler).handleOp(selfOp), 'self-call path (msg.sender == address(this)): how canonical accounts reach their own admin functions');
  await d.view('plate-written', 'CVINVehicleAccount.getAttribute', acct.getAttribute(ethers.id('cvin/vehicle/plate')).then(ethers.toUtf8String), 'effect of the self-call', (v) => assert.equal(v, 'B-CV 1234'));

  const nonceBefore = await ep.nonces(id);
  const failing = await mkOp(acct.interface.encodeFunctionData('transferOwnership', [ethers.ZeroAddress]));
  failing.signature = await owner.signMessage(ethers.getBytes(await ep.getUserOpHash(failing)));
  await d.reverts('inner-revert-bubbles', 'CVINMinimalEntryPoint.handleOp', () => ep.connect(bundler).handleOp(failing), 'zero owner', 'the inner call\'s reason bubbles up and the WHOLE tx reverts (canonical EntryPoint would instead emit UserOperationRevertReason and keep the nonce)');
  await d.view('nonce-rolled-back', 'CVINMinimalEntryPoint.nonces', ep.nonces(id), 'nonce unchanged after the failed op (harness simplification)', (v) => assert.equal(v, nonceBefore));
  const failingExec = await mkOp(acct.interface.encodeFunctionData('execute', [id, 0, acct.interface.encodeFunctionData('recoverOwner', [payee.address])]));
  failingExec.signature = await owner.signMessage(ethers.getBytes(await ep.getUserOpHash(failingExec)));
  await d.reverts('execute-inner-revert', 'CVINMinimalEntryPoint.handleOp -> execute(self) -> recoverOwner', () => ep.connect(bundler).handleOp(failingExec), 'not guardian', 'execute() re-raises the callee\'s revert data verbatim (assembly revert), so the outer reason is the inner one');
  d.offchain('harness-limits', 'CVINMinimalEntryPoint', 'asymmetry: no bundler mempool, no handleOps batching, no paymaster, no deposits/prefund, no validAfter/validUntil, no EIP-1271 — the measured overhead is a lower bound of real 4337');
});
