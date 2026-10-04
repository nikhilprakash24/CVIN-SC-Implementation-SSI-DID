/**
 * Regression tests for defect D21 (and the D16 items it covers) in the
 * vehicle-profile ERC1056Registry (contracts/MOBI/ERC1056Registry.sol, kept
 * byte-identical to cv2x-testbed/contracts/ERC1056Registry.sol).
 *
 *   D21  DIDRevoked carried no previousChange, so revokeIdentity severed the
 *        changed() -> previousChange linked list that did:ethr resolution walks
 *        (the Python provider's _resolve_key_from_events and the S2 adapter).
 *        revokeIdentity was repeatable (moved revokedAt) and changeOwner was
 *        not gated by the revoked flag.
 *
 * The walk below is the same algorithm as erc1056_provider._resolve_key_from_events:
 * one per-block log query per hop, following the smallest previousChange seen
 * in the block, until 0.
 */

const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-toolbox/network-helpers");

const FQN = "contracts/MOBI/ERC1056Registry.sol:ERC1056Registry";
const KEY_NAME = ethers.keccak256(ethers.toUtf8Bytes("did/pub/secp256k1/veriKey/base64"));
const SVC_NAME = ethers.keccak256(ethers.toUtf8Bytes("did/svc/TelemetryService"));
const PUBLIC_KEY = "0x04" + "ab".repeat(64);
const SVC_VALUE = ethers.hexlify(ethers.toUtf8Bytes("https://telemetry.example/v1"));

/**
 * did:ethr-style pointer walk: from changed(identity) follow previousChange
 * block by block. Returns the visited blocks (newest first), the event names
 * seen, and whether any visited block held no event for the identity (a gap).
 */
async function walk(registry, identity) {
  const visited = [];
  const names = [];
  let gaps = 0;
  const seen = new Set();
  let block = await registry.changed(identity);
  while (block !== 0n && !seen.has(block)) {
    seen.add(block);
    const n = Number(block);
    const logs = (
      await Promise.all([
        registry.queryFilter(registry.filters.DIDOwnerChanged(identity), n, n),
        registry.queryFilter(registry.filters.DIDDelegateChanged(identity), n, n),
        registry.queryFilter(registry.filters.DIDAttributeChanged(identity), n, n),
        registry.queryFilter(registry.filters.DIDRevoked(identity), n, n),
      ])
    ).flat();
    visited.push(n);
    if (logs.length === 0) gaps += 1;
    let prev = block;
    for (const ev of logs) {
      names.push(`${ev.fragment.name}@${n}`);
      if (ev.args.previousChange < prev) prev = ev.args.previousChange;
    }
    if (prev === block) break; // no pointer in this block: the list is cut
    block = prev;
  }
  return { visited, names, gaps, stoppedAt: block };
}

describe("ERC1056Registry (vehicle profile) — D21 regression", function () {
  async function deployFixture() {
    const [deployer, vehicle, newOwner, stranger, delegate] = await ethers.getSigners();
    const registry = await (await ethers.getContractFactory(FQN, deployer)).deploy();
    await registry.waitForDeployment();
    return { registry, deployer, vehicle, newOwner, stranger, delegate };
  }

  /** register -> setAttribute -> changeOwner -> revokeIdentity, each in its own block */
  async function lifecycleFixture() {
    const f = await deployFixture();
    const { registry, vehicle, newOwner } = f;
    const id = vehicle.address;
    const rReg = await (await registry.connect(vehicle).registerVehicle(id, PUBLIC_KEY)).wait();
    const rAttr = await (await registry.connect(vehicle).setAttribute(id, SVC_NAME, SVC_VALUE, 3600)).wait();
    const rOwner = await (await registry.connect(vehicle).changeOwner(id, newOwner.address)).wait();
    const rRevoke = await (await registry.connect(newOwner).revokeIdentity(id)).wait();
    return { ...f, id, rReg, rAttr, rOwner, rRevoke };
  }

  it("DIDRevoked carries previousChange pointing at the previous change block", async function () {
    const { registry, id, rOwner, rRevoke } = await loadFixture(lifecycleFixture);
    const revoked = await registry.queryFilter(registry.filters.DIDRevoked(id), rRevoke.blockNumber, rRevoke.blockNumber);
    expect(revoked).to.have.lengthOf(1);
    expect(revoked[0].args.previousChange).to.equal(BigInt(rOwner.blockNumber));
    const blk = await ethers.provider.getBlock(rRevoke.blockNumber);
    expect(revoked[0].args.revokedAt).to.equal(BigInt(blk.timestamp));
    expect(await registry.changed(id)).to.equal(BigInt(rRevoke.blockNumber));
  });

  it("walking changed() -> previousChange from the latest block visits every change including the revocation", async function () {
    const { registry, id, rReg, rAttr, rOwner, rRevoke } = await loadFixture(lifecycleFixture);
    const w = await walk(registry, id);
    expect(w.stoppedAt).to.equal(0n, "walk must terminate at genesis, not at a cut");
    expect(w.gaps).to.equal(0, "every visited block must hold an event for the identity");
    expect(w.visited).to.deep.equal([rRevoke.blockNumber, rOwner.blockNumber, rAttr.blockNumber, rReg.blockNumber]);
    expect(w.names).to.deep.equal([
      `DIDRevoked@${rRevoke.blockNumber}`,
      `DIDOwnerChanged@${rOwner.blockNumber}`,
      `DIDAttributeChanged@${rAttr.blockNumber}`,
      `DIDAttributeChanged@${rReg.blockNumber}`,
    ]);
  });

  it("the provider-style key walk still reaches the verification key through the revocation", async function () {
    // Mirrors erc1056_provider._resolve_key_from_events: hop until the key
    // attribute is found. Before the fix the walk stopped at the revoke block
    // (hop 1) with no key; now it needs 4 hops and finds the registered key.
    const { registry, id } = await loadFixture(lifecycleFixture);
    const [, lastChanged] = await registry.getIdentityInfo(id);
    let block = lastChanged;
    let hops = 0;
    let found = null;
    while (block !== 0n && hops < 64) {
      hops += 1;
      const n = Number(block);
      const logs = (
        await Promise.all([
          registry.queryFilter(registry.filters.DIDOwnerChanged(id), n, n),
          registry.queryFilter(registry.filters.DIDAttributeChanged(id), n, n),
          registry.queryFilter(registry.filters.DIDRevoked(id), n, n),
        ])
      ).flat();
      let prev = null;
      for (const ev of logs) {
        if (prev === null || ev.args.previousChange < prev) prev = ev.args.previousChange;
        if (ev.fragment.name === "DIDAttributeChanged" && ev.args.name === KEY_NAME) found = ev.args.value;
      }
      if (found !== null) break;
      if (prev === null || prev >= block) break;
      block = prev;
    }
    expect(found).to.equal(PUBLIC_KEY);
    expect(hops).to.equal(4);
  });

  it("a second revokeIdentity reverts and revokedAt is not overwritten", async function () {
    const { registry, id, newOwner, rRevoke } = await loadFixture(lifecycleFixture);
    const before = await registry.revokedAt(id);
    expect(before).to.equal(BigInt((await ethers.provider.getBlock(rRevoke.blockNumber)).timestamp));
    await expect(registry.connect(newOwner).revokeIdentity(id)).to.be.revertedWith("Identity already revoked");
    expect(await registry.revokedAt(id)).to.equal(before);
    expect(await registry.changed(id)).to.equal(BigInt(rRevoke.blockNumber));
  });

  it("changeOwner (and every other mutator) reverts for a revoked identity", async function () {
    const { registry, id, newOwner, stranger, delegate } = await loadFixture(lifecycleFixture);
    await expect(registry.connect(newOwner).changeOwner(id, stranger.address)).to.be.revertedWith("Identity is revoked");
    await expect(registry.connect(newOwner).addDelegate(id, ethers.id("sigAuth"), delegate.address, 60)).to.be.revertedWith("Identity is revoked");
    await expect(registry.connect(newOwner).revokeDelegate(id, ethers.id("sigAuth"), delegate.address)).to.be.revertedWith("Identity is revoked");
    await expect(registry.connect(newOwner).setAttribute(id, SVC_NAME, SVC_VALUE, 60)).to.be.revertedWith("Identity is revoked");
    await expect(registry.connect(newOwner).revokeAttribute(id, SVC_NAME, SVC_VALUE)).to.be.revertedWith("Identity is revoked");
    await expect(registry.connect(newOwner).updateVehicleKey(id, PUBLIC_KEY)).to.be.revertedWith("Identity is revoked");
    await expect(registry.connect(newOwner).registerVehicle(id, PUBLIC_KEY)).to.be.revertedWith("Identity already revoked");
    // the ownership record is frozen at decommissioning
    const [owner, , isRevoked] = await registry.getIdentityInfo(id);
    expect(owner).to.equal(newOwner.address);
    expect(isRevoked).to.be.true;
    expect(await registry.isRevoked(id)).to.be.true;
  });

  it("revocation is still owner-gated and the unchanged read surface is intact", async function () {
    const { registry, vehicle, stranger } = await loadFixture(deployFixture);
    const id = vehicle.address;
    await registry.connect(vehicle).registerVehicle(id, PUBLIC_KEY);
    await expect(registry.connect(stranger).revokeIdentity(id)).to.be.revertedWith("Only owner can perform this action");
    const info = await registry.getIdentityInfo(id);
    expect(info.length).to.equal(4);
    expect(info[0]).to.equal(id);
    expect(info[1]).to.equal(await registry.lastChanged(id));
    expect(info[2]).to.be.false;
    expect(info[3]).to.equal(0n);
    const tx = await registry.connect(vehicle).revokeIdentity(id);
    const receipt = await tx.wait();
    console.log("       Gas revokeIdentity (with previousChange + single-shot guard):", receipt.gasUsed.toString());
  });
});
