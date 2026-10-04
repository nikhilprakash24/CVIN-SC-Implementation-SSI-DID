const { expect } = require("chai");
const { ethers } = require("hardhat");

// Regression for defect D13 (docs/DEFECT_LOG.md), found by the S7 vin-linkage demo
// (2026-10-04): CVINVehicleNFT keyed vinToTokenId by the raw VIN string, so the
// lower-cased form of an already-minted VIN minted a SECOND identity for the same
// vehicle, and the only ISO 3779 check was the 17-character length. mintVehicle and
// getTokenIdFromVIN now upper-case the VIN and reject I/O/Q and any non [A-Z0-9]
// character before touching the index. The check digit is deliberately not enforced.
describe("ERC-721 CVINVehicleNFT — VIN normalisation regression (D13)", function () {
  const VIN = "1HGBH41JXMN109186";
  const VIN_LOWER = VIN.toLowerCase();
  const OTHER_VIN_LOWER = "wba3a5c55cf256789"; // a second vehicle, supplied in lower case
  const MINT_ARGS = ["Honda", "Accord", 2021, "Blue", "ipfs://cvin/accord.json"];

  let nft, manufacturer, owner;

  beforeEach(async function () {
    [manufacturer, owner] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("CVINVehicleNFT", manufacturer);
    nft = await Factory.deploy();
    await nft.waitForDeployment();
  });

  it("minting the lower-cased form of an already-minted VIN reverts as a duplicate (one identity per vehicle)", async function () {
    const receipt = await (await nft.mintVehicle(owner.address, VIN, ...MINT_ARGS)).wait();
    console.log(`        [gas] ERC-721 mintVehicle (create identity, post-D13): ${receipt.gasUsed.toString()}`);

    await expect(nft.mintVehicle(owner.address, VIN_LOWER, ...MINT_ARGS))
      .to.be.revertedWith("CVINVehicleNFT: VIN already minted");
    expect(await nft.getTotalVehicles()).to.equal(1);
  });

  it("rejects VINs containing I, O or Q (upper or lower case) with 'invalid VIN character'", async function () {
    for (const bad of ["1HGBH41JXMN10918I", "1HGBH41JXMN10918O", "1HGBH41JXMN10918Q", "1hgbh41jxmn10918i", "1HGBH41JXMN10918-"]) {
      await expect(nft.mintVehicle(owner.address, bad, ...MINT_ARGS), bad)
        .to.be.revertedWith("CVINVehicleNFT: invalid VIN character");
    }
    expect(await nft.getTotalVehicles()).to.equal(0);
  });

  it("rejects VINs whose length is not 17 with 'invalid VIN length'", async function () {
    for (const bad of ["", "1HGBH41JXMN10918", "1HGBH41JXMN1091860"]) {
      await expect(nft.mintVehicle(owner.address, bad, ...MINT_ARGS), JSON.stringify(bad))
        .to.be.revertedWith("CVINVehicleNFT: invalid VIN length");
    }
  });

  it("a lower-cased lookup finds the upper-cased identity (getTokenIdFromVIN normalises; the raw mapping is keyed by the normalised VIN)", async function () {
    await (await nft.mintVehicle(owner.address, VIN, ...MINT_ARGS)).wait();

    expect(await nft.getTokenIdFromVIN(VIN_LOWER)).to.equal(1);
    expect(await nft.getTokenIdFromVIN(VIN)).to.equal(1);
    // The auto-generated getter of the public mapping cannot normalise: it is keyed by the
    // normalised (upper-case) VIN only, and a lower-cased key returns the 0 sentinel.
    expect(await nft.vinToTokenId(VIN)).to.equal(1);
    expect(await nft.vinToTokenId(VIN_LOWER)).to.equal(0);
    // Lookups validate the shape too.
    await expect(nft.getTokenIdFromVIN("1HGBH41JXMN10918Q"))
      .to.be.revertedWith("CVINVehicleNFT: invalid VIN character");
  });

  it("stores and emits the VIN in upper case when it was supplied in lower case", async function () {
    const upper = OTHER_VIN_LOWER.toUpperCase();
    const tx = await nft.mintVehicle(owner.address, OTHER_VIN_LOWER, ...MINT_ARGS);
    await expect(tx).to.emit(nft, "VehicleMinted").withArgs(1, upper, owner.address, manufacturer.address);

    expect(await nft.tokenIdToVIN(1)).to.equal(upper);
    expect(await nft.getVINFromTokenId(1)).to.equal(upper);
    expect((await nft.vehicleMetadata(1)).vin).to.equal(upper);
    expect(await nft.vinToTokenId(upper)).to.equal(1);
    expect(await nft.getTokenIdFromVIN(OTHER_VIN_LOWER)).to.equal(1);
  });
});
