// O2_ERC721 native-pattern checks beyond the 12-test compliance suite:
// the token really is minted, it is soulbound, and deactivation keeps it resolvable (no burn).
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("O2_ERC721 — native soulbound token semantics", function () {
  let ssi, a, b, did;
  beforeEach(async () => {
    [a, b] = await ethers.getSigners();
    ssi = await (await ethers.getContractFactory("O2_ERC721")).deploy();
    const rc = await (await ssi.connect(a).createDID(a.address)).wait();
    did = rc.logs.map(l => { try { return ssi.interface.parseLog(l); } catch { return null; } }).find(e => e && e.name === "DIDCreated").args.did;
  });

  it("createDID mints: ownerOf(tokenId) is the controller; balance is 1; Locked emitted", async () => {
    expect(await ssi.ownerOf(BigInt(did))).to.equal(a.address);
    expect(await ssi.balanceOf(a.address)).to.equal(1);
    await expect(ssi.connect(b).createDID(b.address)).to.emit(ssi, "Locked");
  });

  it("transfers revert (EIP-5192 soulbound); approvals cannot move it", async () => {
    await expect(ssi.connect(a).transferFrom(a.address, b.address, BigInt(did))).to.be.revertedWithCustomError(ssi, "Soulbound");
    await ssi.connect(a).approve(b.address, BigInt(did));
    await expect(ssi.connect(b).transferFrom(a.address, b.address, BigInt(did))).to.be.revertedWithCustomError(ssi, "Soulbound");
    expect(await ssi.ownerOf(BigInt(did))).to.equal(a.address);
  });

  it("deactivateDID keeps the token and the DID resolvable with the flag set (DID Core §7.3; no burn)", async () => {
    await ssi.connect(a).deactivateDID(did);
    expect(await ssi.ownerOf(BigInt(did))).to.equal(a.address);
    const [doc, meta] = await ssi.resolveDID(did);
    expect(doc.length).to.be.greaterThan(2);
    const m = ethers.AbiCoder.defaultAbiCoder().decode(["tuple(uint256,uint256,bool,uint256)"], meta)[0];
    expect(m[2]).to.equal(true);
    await expect(ssi.connect(a).addDelegate(did, ethers.id("sigAuth"), b.address, 10)).to.be.revertedWithCustomError(ssi, "DIDAlreadyDeactivated");
  });

  it("governance adapter works on O2 unchanged (same document layout as O1)", async () => {
    const adapter = await (await ethers.getContractFactory("O1ControllerAdapter")).deploy(await ssi.getAddress());
    expect(await adapter.controllerOf(did)).to.equal(a.address);
    expect(await adapter.isActive(did)).to.equal(true);
    await ssi.connect(a).deactivateDID(did);
    expect(await adapter.isActive(did)).to.equal(false);
  });
});
