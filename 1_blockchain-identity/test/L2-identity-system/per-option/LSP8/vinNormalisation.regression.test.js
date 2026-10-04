const { expect } = require("chai");
const { ethers } = require("hardhat");

// Regression for defect D13 (docs/DEFECT_LOG.md), found by the S7 vin-linkage demo
// (2026-10-04): CVINVehicleLSP8 derived tokenId = keccak256(raw VIN) and only checked
// that the VIN was non-empty, so the lower-cased form of a minted VIN (or a 5-character
// "VIN") minted a SECOND identity. mintVehicle and tokenIdForVIN now upper-case the VIN
// and reject I/O/Q, non [A-Z0-9] characters and any length other than 17 before hashing,
// so the structural link tokenId = keccak256(normalised VIN) is case-insensitive. The
// check digit is deliberately not enforced.
describe("LSP8 CVINVehicleLSP8 — VIN normalisation regression (D13)", function () {
  const VIN = "1HGBH41JXMN109186";
  const VIN_LOWER = VIN.toLowerCase();
  const OTHER_VIN_LOWER = "wba3a5c55cf256789"; // a second vehicle, supplied in lower case
  const hashOf = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));

  let lsp8, authority, vehicleOwner, buyer;

  beforeEach(async function () {
    [authority, vehicleOwner, buyer] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("CVINVehicleLSP8", authority);
    lsp8 = await Factory.deploy("CVIN Vehicle Identity LSP8", "CVIN-LSP8");
    await lsp8.waitForDeployment();
  });

  it("minting the lower-cased form of a minted VIN reverts as a duplicate tokenId (one identity per vehicle)", async function () {
    const receipt = await (await lsp8.mintVehicle(vehicleOwner.address, VIN)).wait();
    console.log(`        [gas] LSP8 mintVehicle (create identity, post-D13): ${receipt.gasUsed.toString()}`);

    await expect(lsp8.mintVehicle(buyer.address, VIN_LOWER))
      .to.be.revertedWith("LSP8: tokenId already minted");
    expect(await lsp8.totalSupply()).to.equal(1);
    expect(await lsp8.balanceOf(buyer.address)).to.equal(0);
  });

  it("rejects VINs containing I, O or Q (upper or lower case) with 'invalid VIN character'", async function () {
    for (const bad of ["1HGBH41JXMN10918I", "1HGBH41JXMN10918O", "1HGBH41JXMN10918Q", "1hgbh41jxmn10918i", "1HGBH41JXMN10918-"]) {
      await expect(lsp8.mintVehicle(vehicleOwner.address, bad), bad)
        .to.be.revertedWith("LSP8: invalid VIN character");
      await expect(lsp8.tokenIdForVIN(bad), `tokenIdForVIN(${bad})`)
        .to.be.revertedWith("LSP8: invalid VIN character");
    }
    expect(await lsp8.totalSupply()).to.equal(0);
  });

  it("rejects VINs whose length is not 17 with 'invalid VIN length' (an empty VIN keeps its own reason)", async function () {
    for (const bad of ["SHORT", "1HGBH41JXMN10918", "1HGBH41JXMN1091860"]) {
      await expect(lsp8.mintVehicle(vehicleOwner.address, bad), bad)
        .to.be.revertedWith("LSP8: invalid VIN length");
      await expect(lsp8.tokenIdForVIN(bad), `tokenIdForVIN(${bad})`)
        .to.be.revertedWith("LSP8: invalid VIN length");
    }
    await expect(lsp8.mintVehicle(vehicleOwner.address, "")).to.be.revertedWith("LSP8: empty VIN");
  });

  it("a lower-cased lookup finds the upper-cased identity (tokenIdForVIN normalises before hashing)", async function () {
    await (await lsp8.mintVehicle(vehicleOwner.address, VIN)).wait();

    const idUpper = await lsp8.tokenIdForVIN(VIN);
    const idLower = await lsp8.tokenIdForVIN(VIN_LOWER);
    expect(idUpper).to.equal(hashOf(VIN));
    expect(idLower).to.equal(idUpper);
    expect(await lsp8.exists(idLower)).to.equal(true);
    expect(await lsp8.tokenOwnerOf(idLower)).to.equal(vehicleOwner.address);
    // keccak256 of the raw lower-cased string is NOT a token (the old, defective key).
    expect(await lsp8.exists(hashOf(VIN_LOWER))).to.equal(false);
  });

  it("stores and emits the VIN in upper case when it was supplied in lower case", async function () {
    const upper = OTHER_VIN_LOWER.toUpperCase();
    const tokenId = hashOf(upper);
    const tx = await lsp8.mintVehicle(vehicleOwner.address, OTHER_VIN_LOWER);
    await expect(tx).to.emit(lsp8, "VehicleMinted").withArgs(tokenId, upper, vehicleOwner.address);
    await expect(tx).to.emit(lsp8, "TokenIdDataChanged").withArgs(tokenId, await lsp8.DATA_KEY_VIN(), ethers.toUtf8Bytes(upper));

    expect(await lsp8.tokenIdForVIN(OTHER_VIN_LOWER)).to.equal(tokenId);
    expect(await lsp8.tokenOwnerOf(tokenId)).to.equal(vehicleOwner.address);
    const stored = await lsp8.getDataForTokenId(tokenId, await lsp8.DATA_KEY_VIN());
    expect(ethers.toUtf8String(stored)).to.equal(upper);
  });
});
