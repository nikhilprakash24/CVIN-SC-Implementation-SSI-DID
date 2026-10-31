const { expect } = require("chai");
const { ethers } = require("hardhat");

// Regression for defect D9 (docs/DEFECT_LOG.md, found by the S7 token-economics demo, fixed
// 2026-10-04): after renounceOwnership, CVIN_NFT_DID_ERC721.payToll forwarded the toll to
// address(0) — the vehicle paid a toll nobody could collect.
describe("ERC-721 CVIN_NFT_DID_ERC721 — payToll after renounceOwnership regression (D9)", function () {
  let nft, operator, vehicleOwner;
  const toll = ethers.parseEther("0.0125");

  beforeEach(async function () {
    [operator, vehicleOwner] = await ethers.getSigners();
    const F = await ethers.getContractFactory("CVIN_NFT_DID_ERC721", operator);
    nft = await F.deploy("CVIN Vehicle DID", "CVIN", operator.address, 500);
    await nft.waitForDeployment();
    await (await nft.mint(vehicleOwner.address, 1, "ipfs://vehicle/1")).wait();
  });

  it("forwards the toll to the operator while there is one", async function () {
    const before = await ethers.provider.getBalance(operator.address);
    await expect(nft.connect(vehicleOwner).payToll(1, { value: toll }))
      .to.emit(nft, "TollPaid").withArgs(1, vehicleOwner.address, toll);
    expect((await ethers.provider.getBalance(operator.address)) - before).to.equal(toll);
  });

  it("refuses the toll once ownership is renounced instead of burning it", async function () {
    await (await nft.renounceOwnership()).wait();
    expect(await nft.owner()).to.equal(ethers.ZeroAddress);
    const zeroBefore = await ethers.provider.getBalance(ethers.ZeroAddress);
    const payerBefore = await ethers.provider.getBalance(vehicleOwner.address);
    await expect(nft.connect(vehicleOwner).payToll(1, { value: toll }))
      .to.be.revertedWith("CVIN_NFT: no toll operator (ownership renounced)");
    expect(await ethers.provider.getBalance(ethers.ZeroAddress)).to.equal(zeroBefore);
    // only gas left the payer; the toll itself was returned by the revert
    expect(payerBefore - (await ethers.provider.getBalance(vehicleOwner.address))).to.be.lessThan(toll);
  });
});
