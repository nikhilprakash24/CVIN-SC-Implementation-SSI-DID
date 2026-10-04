const { expect } = require("chai");
const { ethers } = require("hardhat");

// Regression for defect D13 (docs/DEFECT_LOG.md), found by the S7 vin-linkage demo
// (2026-10-04): CVINVehicleCredential1155 indexed vinHashToVehicle by keccak256 of the
// raw VIN string and only checked that the VIN was non-empty, so the lower-cased form of
// a registered VIN (or a 5-character "VIN") registered a SECOND identity. registerVehicle
// now upper-cases the VIN and rejects I/O/Q, non [A-Z0-9] characters and any length other
// than 17 before hashing; vinHashOf / vehicleForVIN expose the same normalisation for
// lookups. The check digit is deliberately not enforced.
describe("ERC-1155 CVINVehicleCredential1155 — VIN normalisation regression (D13)", function () {
  const VIN = "1HGBH41JXMN109186";
  const VIN_LOWER = VIN.toLowerCase();
  const OTHER_VIN_LOWER = "wba3a5c55cf256789"; // a second vehicle, supplied in lower case
  const hashOf = (s) => ethers.keccak256(ethers.toUtf8Bytes(s));

  let c, issuer, vehicleA, vehicleB;

  beforeEach(async function () {
    [issuer, vehicleA, vehicleB] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("CVINVehicleCredential1155", issuer);
    c = await Factory.deploy();
    await c.waitForDeployment();
  });

  it("registering the lower-cased form of a registered VIN reverts as a duplicate (one identity per vehicle)", async function () {
    const receipt = await (await c.registerVehicle(vehicleA.address, VIN)).wait();
    console.log(`        [gas] ERC-1155 registerVehicle (create identity, post-D13): ${receipt.gasUsed.toString()}`);

    await expect(c.registerVehicle(vehicleB.address, VIN_LOWER))
      .to.be.revertedWith("CVIN1155: VIN already registered");
    expect(await c.isRegistered(vehicleB.address)).to.equal(false);
    expect(await c.vehicleVIN(vehicleB.address)).to.equal("");
  });

  it("rejects VINs containing I, O or Q (upper or lower case) with 'invalid VIN character'", async function () {
    for (const bad of ["1HGBH41JXMN10918I", "1HGBH41JXMN10918O", "1HGBH41JXMN10918Q", "1hgbh41jxmn10918i", "1HGBH41JXMN10918-"]) {
      await expect(c.registerVehicle(vehicleA.address, bad), bad)
        .to.be.revertedWith("CVIN1155: invalid VIN character");
    }
    expect(await c.isRegistered(vehicleA.address)).to.equal(false);
  });

  it("rejects VINs whose length is not 17 with 'invalid VIN length' (an empty VIN keeps its own reason)", async function () {
    for (const bad of ["SHORT", "1HGBH41JXMN10918", "1HGBH41JXMN1091860"]) {
      await expect(c.registerVehicle(vehicleA.address, bad), bad)
        .to.be.revertedWith("CVIN1155: invalid VIN length");
    }
    await expect(c.registerVehicle(vehicleA.address, "")).to.be.revertedWith("CVIN1155: empty VIN");
    // The address-level duplicate check runs before VIN validation (an already-registered
    // address is reported as such whatever VIN is offered).
    await c.registerVehicle(vehicleA.address, VIN);
    await expect(c.registerVehicle(vehicleA.address, "SHORT")).to.be.revertedWith("CVIN1155: vehicle already registered");
  });

  it("a lower-cased lookup finds the upper-cased identity (vinHashOf / vehicleForVIN normalise; the raw index is keyed by keccak256 of the normalised VIN)", async function () {
    await (await c.registerVehicle(vehicleA.address, VIN)).wait();

    expect(await c.vinHashOf(VIN_LOWER)).to.equal(hashOf(VIN));
    expect(await c.vinHashOf(VIN)).to.equal(hashOf(VIN));
    expect(await c.vehicleForVIN(VIN_LOWER)).to.equal(vehicleA.address);
    expect(await c.vehicleForVIN(VIN)).to.equal(vehicleA.address);
    // The bytes32-keyed public mapping cannot normalise: keccak256 of the raw lower-cased
    // string is a different key and returns the zero-address sentinel.
    expect(await c.vinHashToVehicle(hashOf(VIN))).to.equal(vehicleA.address);
    expect(await c.vinHashToVehicle(hashOf(VIN_LOWER))).to.equal(ethers.ZeroAddress);
    // Lookups validate the shape too.
    await expect(c.vehicleForVIN("1HGBH41JXMN10918Q")).to.be.revertedWith("CVIN1155: invalid VIN character");
  });

  it("stores, indexes and emits the VIN in upper case when it was supplied in lower case", async function () {
    const upper = OTHER_VIN_LOWER.toUpperCase();
    const tx = await c.registerVehicle(vehicleB.address, OTHER_VIN_LOWER);
    await expect(tx).to.emit(c, "VehicleRegistered").withArgs(vehicleB.address, hashOf(upper), upper);

    expect(await c.vehicleVIN(vehicleB.address)).to.equal(upper);
    expect(await c.vinHashToVehicle(hashOf(upper))).to.equal(vehicleB.address);
    expect(await c.vehicleForVIN(OTHER_VIN_LOWER)).to.equal(vehicleB.address);
    // Deregistration (burning the BIRTH_CERT) clears the normalised index entry.
    await c.revokeCredential(vehicleB.address, await c.BIRTH_CERT(), 1);
    expect(await c.vehicleForVIN(OTHER_VIN_LOWER)).to.equal(ethers.ZeroAddress);
  });
});
