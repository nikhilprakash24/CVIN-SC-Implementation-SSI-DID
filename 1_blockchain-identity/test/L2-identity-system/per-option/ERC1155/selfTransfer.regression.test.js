const { expect } = require("chai");
const { ethers } = require("hardhat");

// Regression for a defect found by the S2 sandbox smoke run (2026-10-04):
// issuerTransferCredential(from, to, BIRTH_CERT) with from == to re-wrote and then
// deleted the VIN mapping, silently destroying the vehicle's VIN linkage.
describe("ERC-1155 CVINVehicleCredential1155 — self-transfer regression", function () {
  it("rejects a transfer to the same holder and keeps the VIN mapping intact", async function () {
    const [issuer, vehicle] = await ethers.getSigners();
    const C = await ethers.getContractFactory("CVINVehicleCredential1155", issuer);
    const c = await C.deploy();
    await c.waitForDeployment();
    const vin = "1HGBH41JXMN109186";
    await (await c.registerVehicle(vehicle.address, vin)).wait();
    expect(await c.vehicleVIN(vehicle.address)).to.equal(vin);
    const birth = await c.BIRTH_CERT();
    await expect(c.issuerTransferCredential(vehicle.address, vehicle.address, birth))
      .to.be.revertedWith("CVIN1155: transfer to same holder");
    expect(await c.vehicleVIN(vehicle.address)).to.equal(vin);
  });
});
