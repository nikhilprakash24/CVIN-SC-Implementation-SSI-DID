/**
 * Regression test for defect D18 in CVINVehicleDIDRegistry:
 * setVehicleAttributes passed type(uint256).max as validity and the inner
 * EthereumDIDRegistry.setAttribute computed block.timestamp + validity, which
 * panicked (0x11) under Solidity 0.8 checked arithmetic. The eight-attribute
 * birth record (DID_VIN .. DID_AUTONOMY_LEVEL) was therefore unreachable
 * through the wrapper.
 *
 * Fix: a bounded PERMANENT_ATTRIBUTE_VALIDITY (100 years), the same constant
 * MOBIVIDRegistry already uses for its "permanent" birth attribute.
 */

const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-toolbox/network-helpers");

const TEST_VIN = "1HGBH41JXMN109186";
const CAR = {
  make: "Honda",
  model: "Accord",
  year: 2024,
  color: "Silver",
  engineNumber: "ENG-12345-XYZ",
  manufacturingDate: 1700000000,
  autonomyLevel: "SAE Level 3",
};
const HUNDRED_YEARS = 100n * 365n * 24n * 60n * 60n;

describe("CVINVehicleDIDRegistry — D18 regression (setVehicleAttributes reachable)", function () {
  async function deployFixture() {
    const [owner, manufacturer, vehicleOwner] = await ethers.getSigners();
    const didRegistry = await (await ethers.getContractFactory("EthereumDIDRegistry")).deploy();
    await didRegistry.waitForDeployment();
    const wrapper = await (await ethers.getContractFactory("CVINVehicleDIDRegistry")).deploy(await didRegistry.getAddress());
    await wrapper.waitForDeployment();
    await wrapper.connect(owner).setAuthorizedManufacturer(manufacturer.address, true);
    await wrapper.connect(manufacturer).createVehicleDID(
      TEST_VIN, vehicleOwner.address, CAR.make, CAR.model, CAR.year, CAR.color,
      CAR.engineNumber, CAR.manufacturingDate, CAR.autonomyLevel
    );
    // The wrapper writes attributes on the DID's behalf, so it must hold
    // ERC-1056 control of the DID (see vehicleOwnerOf).
    await didRegistry.connect(vehicleOwner).changeOwner(vehicleOwner.address, await wrapper.getAddress());
    return { didRegistry, wrapper, owner, manufacturer, vehicleOwner };
  }

  it("exposes a bounded PERMANENT_ATTRIBUTE_VALIDITY of 100 years", async function () {
    const { wrapper } = await loadFixture(deployFixture);
    expect(await wrapper.PERMANENT_ATTRIBUTE_VALIDITY()).to.equal(HUNDRED_YEARS);
  });

  it("createVehicleDID then setVehicleAttributes succeeds and the eight attributes resolve from events", async function () {
    const { didRegistry, wrapper, vehicleOwner } = await loadFixture(deployFixture);
    const did = vehicleOwner.address;

    const tx = await wrapper.connect(vehicleOwner).setVehicleAttributes(
      CAR.make, CAR.model, CAR.year, CAR.color, CAR.engineNumber, CAR.manufacturingDate, CAR.autonomyLevel
    );
    const receipt = await tx.wait();
    console.log("       Gas setVehicleAttributes (8 attributes, fixed validity):", receipt.gasUsed.toString());

    const blk = await ethers.provider.getBlock(receipt.blockNumber);
    const events = await didRegistry.queryFilter(didRegistry.filters.DIDAttributeChanged(did), receipt.blockNumber, receipt.blockNumber);
    expect(events).to.have.lengthOf(8);

    // Resolve name -> value like an off-chain did:ethr resolver would.
    const attrs = new Map();
    for (const ev of events) {
      expect(ev.args.validTo).to.equal(BigInt(blk.timestamp) + HUNDRED_YEARS);
      attrs.set(ev.args.name, ev.args.value);
    }
    const str = (name) => ethers.toUtf8String(attrs.get(name));
    expect(str(await wrapper.DID_VIN())).to.equal(TEST_VIN);
    expect(str(await wrapper.DID_MAKE())).to.equal(CAR.make);
    expect(str(await wrapper.DID_MODEL())).to.equal(CAR.model);
    expect(str(await wrapper.DID_COLOR())).to.equal(CAR.color);
    expect(str(await wrapper.DID_ENGINE())).to.equal(CAR.engineNumber);
    expect(str(await wrapper.DID_AUTONOMY_LEVEL())).to.equal(CAR.autonomyLevel);
    expect(attrs.get(await wrapper.DID_YEAR())).to.equal(ethers.solidityPacked(["uint16"], [CAR.year]));
    expect(attrs.get(await wrapper.DID_MANUFACTURING_DATE())).to.equal(ethers.solidityPacked(["uint256"], [CAR.manufacturingDate]));

    // the identity's change pointer now heads at the birth-record block
    expect(await didRegistry.changed(did)).to.equal(BigInt(receipt.blockNumber));
  });

  it("still rejects an unregistered DID and a DID whose ERC-1056 control was not handed to the wrapper", async function () {
    const { didRegistry, wrapper, manufacturer } = await loadFixture(deployFixture);
    const [, , , other] = await ethers.getSigners();
    await expect(
      wrapper.connect(other).setVehicleAttributes(CAR.make, CAR.model, CAR.year, CAR.color, CAR.engineNumber, CAR.manufacturingDate, CAR.autonomyLevel)
    ).to.be.revertedWith("CVINRegistry: DID not registered");

    await wrapper.connect(manufacturer).createVehicleDID(
      "2HGBH41JXMN109187", other.address, CAR.make, CAR.model, CAR.year, CAR.color, CAR.engineNumber, CAR.manufacturingDate, CAR.autonomyLevel
    );
    expect(await didRegistry.identityOwner(other.address)).to.equal(other.address);
    await expect(
      wrapper.connect(other).setVehicleAttributes(CAR.make, CAR.model, CAR.year, CAR.color, CAR.engineNumber, CAR.manufacturingDate, CAR.autonomyLevel)
    ).to.be.revertedWith("DIDRegistry: unauthorized");
  });
});
