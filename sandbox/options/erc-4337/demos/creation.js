'use strict';
/**
 * ERC-4337 — family "Identity creation (explicit)" (manifest: implemented; the comparison measures
 * the account deployment as createIdentity). Identity = one CVINVehicleAccount contract; its
 * address is the stable identifier. This harness has no AccountFactory and the minimal entry
 * point rejects initCode, so creation is an explicit CREATE deployment, not the counterfactual
 * CREATE2 of canonical 4337. Exercises the constructor (VehicleAccountCreated), its guards, the
 * immutable entryPoint binding, receive() funding, the initial nonce and the initCode rejection.
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-4337/demos/creation.js
 */
const { ethers } = global; // injected by `hardhat run` (the demos live outside the Hardhat project)
const { demo, eventArgs, VINS } = require('./_lib');

const d = demo('erc-4337', 'creation');

d.run(async () => {
  const [bundler, vehicleOwner] = await ethers.getSigners();
  const { assert } = d;
  const EP = await ethers.getContractFactory('CVINMinimalEntryPoint', bundler);
  const ep = await EP.deploy();
  await ep.waitForDeployment();
  const epDep = await ep.deploymentTransaction().wait();
  const epAddr = await ep.getAddress();
  d.offchain('deploy-entrypoint', 'CVINMinimalEntryPoint.constructor', `shared minimal entry point deployed, gasUsed=${epDep.gasUsed} (measured as deployRegistry; NOT the canonical v0.7 EntryPoint)`);

  const vehicleKey = ethers.Wallet.createRandom().connect(ethers.provider);
  d.offchain('vehicle-key', 'off-chain keygen', `vehicle signing key ${vehicleKey.address} generated off-chain; it holds no ETH and never sends a transaction itself`);
  const A = await ethers.getContractFactory('CVINVehicleAccount', bundler);
  const acct = await A.deploy(epAddr, vehicleKey.address);
  await acct.waitForDeployment();
  const dep = await acct.deploymentTransaction().wait();
  const acctAddr = await acct.getAddress();
  const ev = eventArgs(acct, dep, 'VehicleAccountCreated');
  assert.equal(ev.account, acctAddr); assert.equal(ev.owner, vehicleKey.address); assert.equal(ev.entryPoint, epAddr);
  d.offchain('deploy-account', 'CVINVehicleAccount.constructor', `MEASURED (createIdentity): account ${acctAddr} deployed by the bundler/manufacturer, gasUsed=${dep.gasUsed}; VehicleAccountCreated(account, owner, entryPoint); VIN ${VINS.bmw} is NOT bound on-chain`);

  await d.view('owner', 'CVINVehicleAccount.owner', acct.owner(), 'signing key installed by the constructor', (v) => assert.equal(v, vehicleKey.address));
  await d.view('entry-point', 'CVINVehicleAccount.entryPoint', acct.entryPoint(), 'immutable: the account trusts exactly one entry point for life', (v) => assert.equal(v, epAddr));
  await d.view('guardian-initial', 'CVINVehicleAccount.guardian', acct.guardian(), 'no recovery guardian at creation', (v) => assert.equal(v, ethers.ZeroAddress));
  await d.view('nonce-initial', 'CVINMinimalEntryPoint.nonces', ep.nonces(acctAddr), 'per-account UserOperation sequence starts at 0', (v) => assert.equal(v, 0n));
  await d.reverts('deploy-zero-entrypoint', 'CVINVehicleAccount.constructor', () => A.deploy(ethers.ZeroAddress, vehicleKey.address), 'zero entryPoint', 'constructor guard');
  await d.reverts('deploy-zero-owner', 'CVINVehicleAccount.constructor', () => A.deploy(epAddr, ethers.ZeroAddress), 'zero owner', 'constructor guard');

  await d.tx('fund-account', 'CVINVehicleAccount.receive', bundler.sendTransaction({ to: acctAddr, value: ethers.parseEther('1') }), 'receive(): the account itself can hold ETH (it will pay for execute() value transfers; the key never needs gas)');
  await d.view('account-balance', 'provider.getBalance', ethers.provider.getBalance(acctAddr), '1 ETH held by the identity contract', (v) => assert.equal(v, ethers.parseEther('1')));

  const userOp = { sender: acctAddr, nonce: 0, initCode: ethers.concat([epAddr, '0x1234']), callData: '0x', accountGasLimits: ethers.ZeroHash, preVerificationGas: 0, gasFees: ethers.ZeroHash, paymasterAndData: '0x', signature: '0x' };
  await d.reverts('initcode-rejected', 'CVINMinimalEntryPoint.handleOp', () => ep.connect(bundler).handleOp(userOp), 'initCode unsupported', 'counterfactual (factory + initCode) creation is NOT available in this harness: the identity must be deployed before any UserOperation');
  d.offchain('creation-mode', 'CVINVehicleAccount', 'asymmetry: canonical 4337 creates the identity lazily on first use (CREATE2 address known in advance); here creation is an explicit deployment, so the comparison counts the constructor as the creation cost');
  const second = await A.deploy(epAddr, vehicleOwner.address);
  await second.waitForDeployment();
  assert.notEqual(await second.getAddress(), acctAddr);
  d.offchain('one-contract-per-identity', 'CVINVehicleAccount.constructor', `second vehicle = second contract (${(await second.getAddress()).slice(0, 10)}…); there is no shared registry of identities, only the entry point`);
});
