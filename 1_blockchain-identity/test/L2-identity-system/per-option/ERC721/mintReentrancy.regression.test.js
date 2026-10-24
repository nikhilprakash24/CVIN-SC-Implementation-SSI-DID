const { expect } = require("chai");
const { ethers } = require("hardhat");

// Regression for the mintVehicle re-entrancy window (Phase 3 of the smart-contract annotation work,
// docs/smart-contracts/03-token-standards-erc721-erc1155-lsp8.md): mintVehicle called _safeMint, which
// calls the recipient's onERC721Received, BEFORE writing vinToTokenId. A recipient holding
// MANUFACTURER_ROLE could re-enter mintVehicle from the callback with the same VIN, pass the
// "VIN already minted" check and mint a second identity for one vehicle. The VIN index is now written
// before _safeMint (checks-effects-interactions), so the re-entrant mint reverts.
describe("ERC-721 CVINVehicleNFT — mintVehicle re-entrancy regression", function () {
  const VIN = "1HGBH41JXMN109186";

  it("a manufacturer-role receiver cannot mint the same VIN twice from onERC721Received", async function () {
    const [admin] = await ethers.getSigners();
    const nft = await (await ethers.getContractFactory("CVINVehicleNFT", admin)).deploy();
    const attacker = await (await ethers.getContractFactory("ReentrantVinReceiver")).deploy(await nft.getAddress());
    await nft.grantRole(await nft.MANUFACTURER_ROLE(), await attacker.getAddress());

    await attacker.attack(VIN);

    expect(await attacker.attempted()).to.equal(true);
    expect(await attacker.reentrySucceeded()).to.equal(false);
    expect(await nft.getTotalVehicles()).to.equal(1);
    expect(await nft.balanceOf(await attacker.getAddress())).to.equal(1);
  });
});
