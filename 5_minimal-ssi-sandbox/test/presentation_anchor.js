// PresentationAnchor — Set B overlay adapter (WO-9).
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("PresentationAnchor (WO-9 adapter)", function () {
  let ssi, pa, a, b, did;
  beforeEach(async () => {
    [a, b] = await ethers.getSigners();
    ssi = await (await ethers.getContractFactory("O1_ERC1056")).deploy();
    pa = await (await ethers.getContractFactory("PresentationAnchor")).deploy(await ssi.getAddress());
    const rc = await (await ssi.connect(a).createDID(a.address)).wait();
    did = rc.logs.map(l => { try { return ssi.interface.parseLog(l); } catch { return null; } }).find(e => e && e.name === "DIDCreated").args.did;
  });
  it("holder anchors a format + proof hash; verifier matches it; duplicates and strangers rejected", async () => {
    const fmt = await pa.FMT_BBS(), h = ethers.id("proof-bytes");
    await expect(pa.connect(b).anchorPresentation(did, fmt, h, ethers.ZeroHash)).to.be.revertedWithCustomError(pa, "NotHolder");
    await expect(pa.connect(a).anchorPresentation(did, fmt, h, ethers.ZeroHash)).to.emit(pa, "PresentationAnchored");
    await expect(pa.connect(a).anchorPresentation(did, fmt, h, ethers.ZeroHash)).to.be.revertedWithCustomError(pa, "Exists");
    let [anch, wd] = await pa.verifyAnchored(did, fmt, h, ethers.ZeroHash); expect(anch).to.equal(true); expect(wd).to.equal(false);
    [anch] = await pa.verifyAnchored(did, fmt, ethers.id("other"), ethers.ZeroHash); expect(anch).to.equal(false);
    expect(await pa.countByFormat(fmt)).to.equal(1);
  });
  it("withdraw flags the anchor (status on-chain, proof off-chain)", async () => {
    const fmt = await pa.FMT_SD_JWT(), h = ethers.id("p");
    await pa.connect(a).anchorPresentation(did, fmt, h, ethers.ZeroHash);
    const id = ethers.solidityPackedKeccak256(["bytes32", "bytes32", "bytes32", "bytes32"], [did, fmt, h, ethers.ZeroHash]);
    await expect(pa.connect(b).withdraw(id)).to.be.revertedWithCustomError(pa, "NotHolder");
    await expect(pa.connect(a).withdraw(id)).to.emit(pa, "PresentationWithdrawn");
    const [, wd] = await pa.verifyAnchored(did, fmt, h, ethers.ZeroHash); expect(wd).to.equal(true);
  });
});
