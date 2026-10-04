const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ERC721 Identity-Based Transaction Test Suite", function () {
    let CVIN_NFT_DID_ERC721, cvin_nft_did_erc721;
    let owner, addr1, addr2;

    beforeEach(async function () {
        [owner, addr1, addr2, _] = await ethers.getSigners();

        CVIN_NFT_DID_ERC721 = await ethers.getContractFactory("CVIN_NFT_DID_ERC721");
        cvin_nft_did_erc721 = await CVIN_NFT_DID_ERC721.deploy("CVIN", "CVN", owner.address, 500);
        await cvin_nft_did_erc721.waitForDeployment();
    });

    it("Should verify identity and pay toll", async function () {
        await cvin_nft_did_erc721.mint(addr1.address, 1, "Toyota Corolla Hatchback LE 2023");

        // Verify the identity of the car
        const tokenURI = await cvin_nft_did_erc721.tokenURI(1);
        const isVerified = tokenURI.includes("Toyota") && tokenURI.includes("2023");
        expect(isVerified).to.be.true;

        // Pay the toll after verification. The toll is debited from the vehicle
        // owner and credited to the receiving entity (the toll operator, i.e.
        // the contract owner). Balance deltas are asserted rather than the
        // operator's absolute balance, since the operator is a pre-funded
        // Hardhat account that also paid the deployment gas.
        const tollAmount = ethers.parseEther("0.1");
        await expect(() =>
            cvin_nft_did_erc721.connect(addr1).payToll(1, { value: tollAmount })
        ).to.changeEtherBalances([addr1, owner], [-tollAmount, tollAmount]);
    });
});
