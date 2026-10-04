'use strict';
/**
 * erc-1056-uport / controller — the two ownership models: ERC-1056 changeOwner /
 * changeOwnerSigned (DID stable, controller rotates) and the wrapper's
 * transferVehicleOwnership / updateOwnershipMapping (VIN re-pointed to another DID).
 * Run: cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-1056-uport/demos/controller.js
 */
const hre = global.hre || require('hardhat'); // injected by `npx hardhat run`
const { ethers } = hre;

const OPTION = 'erc-1056-uport';
const FAMILY = 'controller';
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

const VIN = '1HGCM82633A004352';
const VIN2 = 'WBA3A5C58DF586741';
const CAR = ['Honda', 'Accord', 2003, 'Silver', 'K24A4-2003-0471', 1041379200, 'L0'];
const CAR2 = ['BMW', '328i', 2013, 'Black', 'N20B20-2013-8841', 1356998400, 'L1'];

async function main() {
  const [deployer, vehicleOwner, newOwner, delegate, stranger] = await ethers.getSigners();
  // the vehicle owner is a local wallet so it can sign the raw ERC-1056 meta-transaction digest
  const W = ethers.Wallet.createRandom().connect(ethers.provider);
  await (await deployer.sendTransaction({ to: W.address, value: ethers.parseEther('5') })).wait();

  const registry = await (await ethers.getContractFactory('EthereumDIDRegistry', deployer)).deploy();
  const r1 = await registry.deploymentTransaction().wait();
  out('deploy-registry', 'EthereumDIDRegistry.constructor', true, r1.gasUsed, 'shared did:ethr registry');
  const wrapper = await (await ethers.getContractFactory('CVINVehicleDIDRegistry', deployer)).deploy(await registry.getAddress());
  const r2 = await wrapper.deploymentTransaction().wait();
  out('deploy-wrapper', 'CVINVehicleDIDRegistry.constructor', true, r2.gasUsed, 'VIN wrapper');
  const regAddr = await registry.getAddress();
  const wrapAddr = await wrapper.getAddress();
  await tx('createVehicleDID', 'CVINVehicleDIDRegistry.createVehicleDID', wrapper.connect(deployer).createVehicleDID(VIN, W.address, ...CAR), `vehicle ${VIN} bound to DID ${short(W.address)}`);

  // ---- initial state ----
  const ow = await view('owners-default', 'EthereumDIDRegistry.owners', registry.owners(W.address), (v) => `owners[did] == ${v} (zero = no explicit owner; identityOwner falls back to the DID itself)`);
  assert(ow === ethers.ZeroAddress, 'owners default zero');
  await view('identityOwner-self', 'EthereumDIDRegistry.identityOwner', registry.identityOwner(W.address), (v) => `identityOwner == ${short(v)} (self)`);
  const wo = await view('wrapper-owner', 'CVINVehicleDIDRegistry.owner', wrapper.owner(), (v) => `wrapper contract owner == deployer (${short(v)}); immutable: the wrapper has no transferOwnership`);
  assert(wo === deployer.address, 'wrapper owner');
  await view('vehicleOwners-default', 'CVINVehicleDIDRegistry.vehicleOwners', wrapper.vehicleOwners(W.address), (v) => `vehicleOwners[did] == ${v} (zero = "the DID itself"; no SSTORE at creation)`);
  const vo1 = await view('vehicleOwnerOf', 'CVINVehicleDIDRegistry.vehicleOwnerOf', wrapper.vehicleOwnerOf(W.address), (v) => `vehicleOwnerOf == ${short(v)}: while the wrapper does not control the DID, the ERC-1056 identityOwner is authoritative`);
  assert(vo1 === W.address, 'vehicleOwnerOf self');
  await view('getVehicleOwner', 'CVINVehicleDIDRegistry.getVehicleOwner', wrapper.getVehicleOwner(W.address), (v) => `getVehicleOwner == ${short(v)} (alias of vehicleOwnerOf)`);

  // ---- ERC-1056 controller rotation: signed (meta-tx) then direct ----
  const nonce = await registry.nonce(W.address);
  const digest = ethers.solidityPackedKeccak256(['bytes1', 'bytes1', 'address', 'uint256', 'address', 'string', 'address'],
    ['0x19', '0x00', regAddr, nonce, W.address, 'changeOwner', newOwner.address]);
  const sig = W.signingKey.sign(digest); // raw secp256k1 over the ERC-1056 digest, no EIP-191 prefix
  const rs = await tx('changeOwnerSigned', 'EthereumDIDRegistry.changeOwnerSigned',
    registry.connect(deployer).changeOwnerSigned(W.address, sig.v, sig.r, sig.s, newOwner.address),
    `meta-transaction relayed by deployer (gas payer) and signed by the controller over keccak256(0x19||0x00||registry||nonce||identity||"changeOwner"||newOwner) with NO EIP-191 prefix; measured by L1 signed-op only`);
  const e1 = eventsOf(rs, registry, 'DIDOwnerChanged');
  assert(e1.length === 1 && e1[0].args.owner === newOwner.address && e1[0].args.previousChange === 0n, 'DIDOwnerChanged');
  const io = await view('identityOwner-after', 'EthereumDIDRegistry.identityOwner', registry.identityOwner(W.address), (v) => `identityOwner == ${short(v)} (newOwner); the DID (${short(W.address)}) is unchanged: controller rotation, not identifier change`);
  assert(io === newOwner.address, 'controller rotated');
  await view('owners-after', 'EthereumDIDRegistry.owners', registry.owners(W.address), (v) => `owners[did] == ${short(v)} (explicit owner now stored: 1 SSTORE)`);
  const vo2 = await view('vehicleOwnerOf-follows-controller', 'CVINVehicleDIDRegistry.vehicleOwnerOf', wrapper.vehicleOwnerOf(W.address), (v) => `vehicleOwnerOf == ${short(v)}: tracks the ERC-1056 controller automatically`);
  assert(vo2 === newOwner.address, 'wrapper follows controller');
  await reverts('old-controller-locked-out', 'EthereumDIDRegistry.changeOwner', registry.connect(W).changeOwner(W.address, W.address), 'DIDRegistry: unauthorized', 'the previous controller (the DID address itself) can no longer act');
  await tx('changeOwner-back', 'EthereumDIDRegistry.changeOwner', registry.connect(newOwner).changeOwner(W.address, W.address), 'direct changeOwner by the current controller (measured as transferOwnership / controller-change)');

  // ---- wrapper ownership model: hand ERC-1056 control to the wrapper, then transferVehicleOwnership ----
  await tx('hand-control-to-wrapper', 'EthereumDIDRegistry.changeOwner', registry.connect(W).changeOwner(W.address, wrapAddr),
    'prerequisite for every wrapper mutation: the vehicle owner makes the wrapper the ERC-1056 owner of the DID');
  const vo3 = await view('vehicleOwnerOf-while-wrapped', 'CVINVehicleDIDRegistry.vehicleOwnerOf', wrapper.vehicleOwnerOf(W.address), (v) => `vehicleOwnerOf == ${short(v)}: wrapper controls the DID, so vehicleOwners[did] (default: the DID itself) is authoritative`);
  assert(vo3 === W.address, 'wrapped owner default');
  const rt = await tx('transferVehicleOwnership', 'CVINVehicleDIDRegistry.transferVehicleOwnership', wrapper.connect(W).transferVehicleOwnership(W.address, newOwner.address),
    'single-step vehicle sale inside the wrapper: DID stays, vehicleOwners[did] moves, VehicleOwnershipTransferred emitted; not measured');
  const e2 = eventsOf(rt, wrapper, 'VehicleOwnershipTransferred');
  assert(e2.length === 1 && e2[0].args.previousOwner === W.address && e2[0].args.newOwner === newOwner.address, 'VehicleOwnershipTransferred');
  await view('vehicleOwners-after', 'CVINVehicleDIDRegistry.vehicleOwners', wrapper.vehicleOwners(W.address), (v) => `vehicleOwners[did] == ${short(v)}`);
  const gv = await view('getVehicleOwner-after', 'CVINVehicleDIDRegistry.getVehicleOwner', wrapper.getVehicleOwner(W.address), (v) => `getVehicleOwner == ${short(v)} (newOwner)`);
  assert(gv === newOwner.address, 'wrapper transfer applied');
  await reverts('transfer-by-previous-owner', 'CVINVehicleDIDRegistry.transferVehicleOwnership', wrapper.connect(W).transferVehicleOwnership(W.address, stranger.address), 'not vehicle owner', 'previous vehicle owner locked out of the wrapper');
  await reverts('transfer-to-zero', 'CVINVehicleDIDRegistry.transferVehicleOwnership', wrapper.connect(newOwner).transferVehicleOwnership(W.address, ethers.ZeroAddress), 'new owner is zero address', 'zero-address guard');
  const stillWrapped = await registry.identityOwner(W.address);
  assert(stillWrapped === wrapAddr, 'wrapper still controls');
  await reverts('new-owner-cannot-reclaim-erc1056-control', 'EthereumDIDRegistry.changeOwner', registry.connect(newOwner).changeOwner(W.address, newOwner.address), 'DIDRegistry: unauthorized',
    'OBSERVATION: after transferVehicleOwnership the wrapper remains the ERC-1056 owner and exposes no function that returns control; the new owner can only act through the wrapper (potential defect: control is captured)');

  // ---- wrapper alternative: updateOwnershipMapping re-points the VIN to a different DID ----
  await tx('createVehicleDID-2', 'CVINVehicleDIDRegistry.createVehicleDID', wrapper.connect(deployer).createVehicleDID(VIN2, vehicleOwner.address, ...CAR2), `second vehicle ${VIN2} -> DID ${short(vehicleOwner.address)}`);
  await tx('changeOwner-direct-to-buyer', 'EthereumDIDRegistry.changeOwner', registry.connect(vehicleOwner).changeOwner(vehicleOwner.address, delegate.address), 'seller hands ERC-1056 control of their DID to the buyer');
  const ru = await tx('updateOwnershipMapping', 'CVINVehicleDIDRegistry.updateOwnershipMapping', wrapper.connect(stranger).updateOwnershipMapping(vehicleOwner.address, delegate.address),
    'anyone may call it once identityOwner(old) == new: the VIN is re-pointed to the buyer\'s address, i.e. the vehicle gets a NEW DID (identifier not stable); not measured');
  const e3 = eventsOf(ru, wrapper, 'VehicleOwnershipTransferred');
  assert(e3.length === 1 && e3[0].args.newOwner === delegate.address, 'VehicleOwnershipTransferred (mapping)');
  const v2 = await view('didToVIN-buyer', 'CVINVehicleDIDRegistry.didToVIN', wrapper.didToVIN(delegate.address), (v) => `didToVIN(buyer) == ${v}`);
  assert(v2 === VIN2, 'VIN moved');
  const v1 = await view('didToVIN-seller-cleared', 'CVINVehicleDIDRegistry.didToVIN', wrapper.didToVIN(vehicleOwner.address), (v) => `didToVIN(seller) == "${v}" (cleared)`);
  assert(v1 === '', 'seller cleared');
  await reverts('mapping-unknown-did', 'CVINVehicleDIDRegistry.updateOwnershipMapping', wrapper.connect(stranger).updateOwnershipMapping(stranger.address, delegate.address), 'VIN not found', 'no VIN registered for that DID');
  await reverts('mapping-before-erc1056-transfer', 'CVINVehicleDIDRegistry.updateOwnershipMapping', wrapper.connect(stranger).updateOwnershipMapping(delegate.address, stranger.address), 'ownership not transferred in DID registry', 'the wrapper verifies the ERC-1056 state before re-pointing');
}

main().then(() => {
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: true }));
}).catch((e) => {
  console.error(e);
  console.log(JSON.stringify({ option: OPTION, family: FAMILY, summary: true, steps, ok: false, error: String(e.message || e) }));
  process.exit(1);
});
