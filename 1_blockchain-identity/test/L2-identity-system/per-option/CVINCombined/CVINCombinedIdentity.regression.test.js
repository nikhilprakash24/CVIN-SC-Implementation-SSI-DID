/**
 * Regression test for defect D22 in CVINCombinedIdentity (the thesis hybrid):
 * addClaim / removeClaim advanced `changed[identity]` without emitting an
 * ERC-1056-style event carrying previousChange, so a did:ethr pointer walk
 * (changed -> previousChange -> ... -> 0) was cut at every claim operation and
 * the S2 adapter had to fall back to a range scan.
 *
 * Fix: both claim operations now emit
 *   DIDClaimChanged(identity, claimId, topic, removed, previousChange)
 * with previousChange = the `changed` value before the operation.
 */

const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-toolbox/network-helpers");

const TOPIC_MANUFACTURER = 2;
const ATTR_NAME = ethers.keccak256(ethers.toUtf8Bytes("did/svc/TelemetryService"));
const ATTR_VALUE = ethers.hexlify(ethers.toUtf8Bytes("https://telemetry.example/v1"));
const CLAIM_DATA = ethers.hexlify(ethers.toUtf8Bytes("TYPE-APPROVAL:EU-2024"));

/** Raw-digest issuer signature, as the contract's _recoverRawDigest expects. */
function signClaim(issuerWallet, registryAddress, identity, topic, data) {
  const digest = ethers.solidityPackedKeccak256(
    ["address", "address", "uint256", "bytes"],
    [registryAddress, identity, topic, data]
  );
  return issuerWallet.signingKey.sign(digest).serialized;
}

/**
 * did:ethr-style pointer walk over all four change events. Returns the visited
 * blocks (newest first), the event names, the number of visited blocks that
 * held no event for the identity (gaps) and where the walk stopped.
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
        registry.queryFilter(registry.filters.DIDClaimChanged(identity), n, n),
      ])
    ).flat();
    visited.push(n);
    if (logs.length === 0) gaps += 1;
    let prev = block;
    for (const ev of logs) {
      names.push(`${ev.fragment.name}@${n}`);
      if (ev.args.previousChange < prev) prev = ev.args.previousChange;
    }
    if (prev === block) break;
    block = prev;
  }
  return { visited, names, gaps, stoppedAt: block };
}

describe("CVINCombinedIdentity — D22 regression (claim ops stay on the previousChange list)", function () {
  async function deployFixture() {
    const [deployer, vehicleOwner, newOwner] = await ethers.getSigners();
    const issuer = ethers.Wallet.createRandom();
    const registry = await (await ethers.getContractFactory("CVINCombinedIdentity", deployer)).deploy();
    await registry.waitForDeployment();
    const id = vehicleOwner.address;
    const sig = signClaim(issuer, await registry.getAddress(), id, TOPIC_MANUFACTURER, CLAIM_DATA);
    const claimId = ethers.solidityPackedKeccak256(["address", "uint256"], [issuer.address, TOPIC_MANUFACTURER]);
    return { registry, deployer, vehicleOwner, newOwner, issuer, id, sig, claimId };
  }

  /** setAttribute -> addClaim -> removeClaim -> setAttribute, one block each */
  async function historyFixture() {
    const f = await deployFixture();
    const { registry, vehicleOwner, issuer, id, sig, claimId } = f;
    const r1 = await (await registry.connect(vehicleOwner).setAttribute(id, ATTR_NAME, ATTR_VALUE, 3600)).wait();
    const r2 = await (await registry.connect(vehicleOwner).addClaim(id, TOPIC_MANUFACTURER, 1, issuer.address, sig, CLAIM_DATA, "")).wait();
    const r3 = await (await registry.connect(vehicleOwner).removeClaim(id, claimId)).wait();
    const r4 = await (await registry.connect(vehicleOwner).setAttribute(id, ATTR_NAME, ATTR_VALUE, 7200)).wait();
    return { ...f, r1, r2, r3, r4 };
  }

  it("addClaim emits DIDClaimChanged(identity, claimId, topic, removed=false, previousChange) next to ClaimAdded", async function () {
    const { registry, vehicleOwner, issuer, id, sig, claimId } = await loadFixture(deployFixture);
    await registry.connect(vehicleOwner).setAttribute(id, ATTR_NAME, ATTR_VALUE, 3600);
    const previousChange = await registry.changed(id);
    const tx = registry.connect(vehicleOwner).addClaim(id, TOPIC_MANUFACTURER, 1, issuer.address, sig, CLAIM_DATA, "");
    await expect(tx).to.emit(registry, "DIDClaimChanged").withArgs(id, claimId, TOPIC_MANUFACTURER, false, previousChange);
    await expect(tx).to.emit(registry, "ClaimAdded");
    const receipt = await (await tx).wait();
    // merge decision M-A (2026-10-06): claim ops no longer advance changed[] (review-2 K-6); the event keeps the history indexable
    expect(await registry.changed(id)).to.equal(previousChange);
    console.log("       Gas addClaim (with DIDClaimChanged, changed[] untouched):", receipt.gasUsed.toString());
  });

  it("removeClaim emits DIDClaimChanged(..., removed=true, previousChange) next to ClaimRemoved", async function () {
    const { registry, vehicleOwner, issuer, id, sig, claimId } = await loadFixture(deployFixture);
    await registry.connect(vehicleOwner).addClaim(id, TOPIC_MANUFACTURER, 1, issuer.address, sig, CLAIM_DATA, "");
    const previousChange = await registry.changed(id);
    const tx = registry.connect(vehicleOwner).removeClaim(id, claimId);
    await expect(tx).to.emit(registry, "DIDClaimChanged").withArgs(id, claimId, TOPIC_MANUFACTURER, true, previousChange);
    await expect(tx).to.emit(registry, "ClaimRemoved");
    const receipt = await (await tx).wait();
    expect(await registry.changed(id)).to.equal(previousChange); // M-A / K-6
    console.log("       Gas removeClaim (with DIDClaimChanged, changed[] untouched):", receipt.gasUsed.toString());
  });

  it("a walk from changed() after addClaim + removeClaim + setAttribute reaches genesis without gaps and never visits a claim block (K-6 / M-A)", async function () {
    const { registry, id, r1, r2, r3, r4 } = await loadFixture(historyFixture);
    const w = await walk(registry, id);
    expect(w.stoppedAt).to.equal(0n, "walk must terminate at genesis, not at a cut");
    expect(w.gaps).to.equal(0, "every previousChange must point at a block in which the identity emitted an event");
    // merge decision M-A (2026-10-06): claim ops do not advance changed[] (review-2 K-6), so the DID-event
    // chain skips the two claim blocks entirely; the claim history is reached through DIDClaimChanged's own filter
    expect(w.visited).to.deep.equal([r4.blockNumber, r1.blockNumber]);
    expect(w.names).to.deep.equal([`DIDAttributeChanged@${r4.blockNumber}`, `DIDAttributeChanged@${r1.blockNumber}`]);
    const last = await registry.queryFilter(registry.filters.DIDAttributeChanged(id), r4.blockNumber, r4.blockNumber);
    expect(last[0].args.previousChange).to.equal(BigInt(r1.blockNumber));
    const claims = await registry.queryFilter(registry.filters.DIDClaimChanged(id), r2.blockNumber, r3.blockNumber);
    expect(claims.map((e) => e.args.removed)).to.deep.equal([false, true]);
  });

  it("a walk over the three classic ERC-1056 events is NOT cut by claim operations (K-6 / M-A): the attribute after the claims links to the attribute before them", async function () {
    const { registry, id, r1, r3, r4 } = await loadFixture(historyFixture);
    let block = await registry.changed(id);
    const n = Number(block);
    expect(n).to.equal(r4.blockNumber);
    const a = await registry.queryFilter(registry.filters.DIDAttributeChanged(id), n, n);
    block = a[0].args.previousChange; // -> the attribute before the claim ops, not the removeClaim block
    const m = Number(block);
    expect(m).to.equal(r1.blockNumber);
    // the claim block carries no classic event and is not on the chain; its DIDClaimChanged is found by its own filter
    const classicAtClaim = (
      await Promise.all([
        registry.queryFilter(registry.filters.DIDOwnerChanged(id), r3.blockNumber, r3.blockNumber),
        registry.queryFilter(registry.filters.DIDDelegateChanged(id), r3.blockNumber, r3.blockNumber),
        registry.queryFilter(registry.filters.DIDAttributeChanged(id), r3.blockNumber, r3.blockNumber),
      ])
    ).flat();
    expect(classicAtClaim).to.have.lengthOf(0);
    const claim = await registry.queryFilter(registry.filters.DIDClaimChanged(id), r3.blockNumber, r3.blockNumber);
    expect(claim).to.have.lengthOf(1);
    expect(claim[0].args.removed).to.be.true;
  });
});
