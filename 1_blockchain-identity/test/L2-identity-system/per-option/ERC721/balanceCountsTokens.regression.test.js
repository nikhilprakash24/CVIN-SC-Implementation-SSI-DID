// D2 regression (DEFECT_LOG D2, fixed 708302a): the monolithic ERC-721 added the tokenId to the balance
// instead of 1. Until the WM-1 audit (finding U-F3d) only the sandbox demos caught a revert of the fix,
// because every Hardhat test minted tokenId 1, for which `+= tokenId` and `+= 1` coincide.
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CVIN_NFT_DID_ERC721_Monolithic — balance counts tokens, not token ids (D2 regression)", function () {
  it("two mints with ids 5 and 7 give a balance of 2, and a transfer moves exactly 1", async function () {
    const [owner, a, b] = await ethers.getSigners();
    const F = await ethers.getContractFactory("CVIN_NFT_DID_ERC721_Monolithic");
    const nft = await F.deploy("CVIN", "CVN", owner.address, 500);
    await nft.waitForDeployment();
    await (await nft.mint(a.address, 5, "ipfs://five")).wait();
    await (await nft.mint(a.address, 7, "ipfs://seven")).wait();
    expect(await nft.balanceOf(a.address)).to.equal(2n);
    await (await nft.connect(a).transferFrom(a.address, b.address, 7)).wait();
    expect(await nft.balanceOf(a.address)).to.equal(1n);
    expect(await nft.balanceOf(b.address)).to.equal(1n);
  });
});
