// BatchAnchorRegistry (S17) and the offline/merkle libraries (S14).
const { expect } = require("chai");
const { ethers } = require("hardhat");
const M = require("../lib/vid/merkle");
const O = require("../lib/vid/offline");

describe("BatchAnchorRegistry + merkle/offline libraries", function () {
  let ssi, adapter, bar, a, b, didA;

  beforeEach(async () => {
    [a, b] = await ethers.getSigners();
    ssi = await (await ethers.getContractFactory("O1_ERC1056")).deploy();
    adapter = await (await ethers.getContractFactory("O1ControllerAdapter")).deploy(await ssi.getAddress());
    bar = await (await ethers.getContractFactory("BatchAnchorRegistry")).deploy(await adapter.getAddress());
    const rc = await (await ssi.connect(a).createDID(a.address)).wait();
    didA = rc.logs.map(l => { try { return ssi.interface.parseLog(l); } catch { return null; } }).find(e => e && e.name === "DIDCreated").args.did;
  });

  it("merkle: JS proofs verify on-chain for every leaf, odd and even counts", async () => {
    for (const n of [1, 2, 5, 11]) {
      const leaves = Array.from({ length: n }, (_, i) => ethers.id(`leaf-${n}-${i}`));
      const tree = M.buildTree(leaves);
      const id = ethers.id(`batch-${n}`);
      await bar.connect(a).anchorBatch(didA, id, tree.root, n);
      for (let i = 0; i < n; i++) {
        const p = M.proofFor(tree, i);
        expect(M.verify(tree.root, leaves[i], p)).to.equal(true);
        const [inc] = await bar.verifyInclusion(id, leaves[i], p);
        expect(inc).to.equal(true);
      }
      const [bad] = await bar.verifyInclusion(id, ethers.id("nope"), M.proofFor(tree, 0));
      expect(bad).to.equal(false);
    }
  });

  it("anchorBatch: only the issuer's controller; no duplicate ids; unknown batch reads false", async () => {
    const tree = M.buildTree([ethers.id("x")]);
    await expect(bar.connect(b).anchorBatch(didA, ethers.id("b1"), tree.root, 1)).to.be.revertedWithCustomError(bar, "NotAuthorized");
    await expect(bar.connect(a).anchorBatch(didA, ethers.id("b1"), tree.root, 1)).to.emit(bar, "BatchAnchored");
    await expect(bar.connect(a).anchorBatch(didA, ethers.id("b1"), tree.root, 1)).to.be.revertedWithCustomError(bar, "BatchExists");
    const [inc, rev, iss] = await bar.verifyInclusion(ethers.id("unknown"), ethers.id("x"), []);
    expect(inc).to.equal(false); expect(rev).to.equal(false); expect(iss).to.equal(ethers.ZeroHash);
    await ssi.connect(a).deactivateDID(didA);
    await expect(bar.connect(a).anchorBatch(didA, ethers.id("b2"), tree.root, 1)).to.be.revertedWithCustomError(bar, "NotAuthorized");
  });

  it("revokeBatch: issuer only; idempotent; inclusion still true but flagged revoked", async () => {
    const tree = M.buildTree([ethers.id("x")]);
    await bar.connect(a).anchorBatch(didA, ethers.id("b1"), tree.root, 1);
    await expect(bar.connect(b).revokeBatch(ethers.id("b1"))).to.be.revertedWithCustomError(bar, "NotAuthorized");
    await expect(bar.connect(a).revokeBatch(ethers.id("b1"))).to.emit(bar, "BatchRevoked");
    await expect(bar.connect(a).revokeBatch(ethers.id("b1"))).to.not.emit(bar, "BatchRevoked");
    const [inc, rev] = await bar.verifyInclusion(ethers.id("b1"), ethers.id("x"), []);
    expect(inc).to.equal(true); expect(rev).to.equal(true);
  });

  it("offline: queue orders by local time then counter; reconcile rejects on dead dependency; signatures recover", async () => {
    const q = new O.WriteQueue(a, didA);
    const i1 = await q.enqueue("A", { n: 1 }, ["dep-dead"]);
    const i2 = await q.enqueue("B", { n: 2 }, []);
    const i3 = await q.enqueue("C", { n: 3 }, ["dep-live"]);
    const items = q.drain();
    expect(items.map(i => i.counter)).to.deep.equal([1, 2, 3]);
    expect(q.items.length).to.equal(0);
    const { accepted, rejected } = await O.reconcile(items, async (d) => d === "dep-live");
    expect(rejected.map(i => i.kind)).to.deep.equal(["A"]);
    expect(accepted.map(i => i.kind)).to.deep.equal(["B", "C"]);
    for (const it of [i1, i2, i3]) expect(ethers.verifyMessage(ethers.getBytes(it.digest), it.sig)).to.equal(a.address);
    const link = new O.Link();
    expect(link.canWrite()).to.equal(true);
    link.set(O.MODE.READ_ONLY); expect(link.canRead()).to.equal(true); expect(link.canWrite()).to.equal(false);
    link.set(O.MODE.PARTITIONED); expect(link.canRead()).to.equal(false);
  });
});
