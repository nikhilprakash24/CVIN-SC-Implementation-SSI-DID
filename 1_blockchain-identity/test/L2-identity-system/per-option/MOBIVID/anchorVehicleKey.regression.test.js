/**
 * Regression tests for defect D11b (docs/DEFECT_LOG.md, fixed 2026-10-04):
 * the MOBI provider generated the vehicle's signing key off-chain AFTER the birth
 * transaction and never published it, so a verifier without the provider's local
 * registration record had no authoritative key to bind a V2X signature to.
 *
 * Fix: MOBIVIDRegistry.anchorVehicleKey publishes the key as the ERC-1056 attribute
 * `did/pub/secp256k1/veriKey/base64` (the name updateVehicleKey and the resolvers
 * already use) with the vehicle-lifetime validity. The registering manufacturer may
 * anchor once, only before the first sale; the identity owner may anchor at any time.
 *
 * Contracts under test live in contracts/MOBI/ (byte-identical to cv2x-testbed/contracts/).
 */
const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-toolbox/network-helpers");

const V1_FQN = "contracts/MOBI/MOBIVIDRegistry.sol:MOBIVIDRegistry";
const V2_FQN = "contracts/MOBI/MOBIVIDRegistryV2.sol:MOBIVIDRegistryV2";
const KEY_NAME = ethers.id("did/pub/secp256k1/veriKey/base64");
const VIN_HASH = ethers.keccak256(ethers.toUtf8Bytes("WBA3A5C50CF123456:salt"));
const CERT_HASH = ethers.keccak256(ethers.toUtf8Bytes("signed-birth-vc"));
const HUNDRED_YEARS = 100n * 365n * 24n * 3600n;

// 65-byte uncompressed secp256k1 point (0x04 || X || Y) and a 33-byte compressed one
const KEY65 = ethers.hexlify(ethers.concat(["0x04", ethers.randomBytes(64)]));
const KEY33 = ethers.hexlify(ethers.concat(["0x02", ethers.randomBytes(32)]));
const KEY_ROTATED = ethers.hexlify(ethers.concat(["0x04", ethers.randomBytes(64)]));

/** Walk the ERC-1056 changed() list backwards and return the newest still-valid veriKey value. */
async function resolveKeyFromEvents(reg, identity) {
  const now = BigInt((await ethers.provider.getBlock("latest")).timestamp);
  let block = await reg.lastChanged(identity);
  let hops = 0;
  while (block > 0n && hops < 64) {
    hops += 1;
    const logs = await reg.queryFilter(reg.filters.DIDAttributeChanged(identity), Number(block), Number(block));
    let found = null;
    for (const l of logs) {
      if (l.args.name === KEY_NAME && l.args.validTo > now) found = l.args.value;
    }
    if (found !== null) return { key: found, hops };
    const all = [
      ...(await reg.queryFilter(reg.filters.DIDOwnerChanged(identity), Number(block), Number(block))),
      ...(await reg.queryFilter(reg.filters.DIDDelegateChanged(identity), Number(block), Number(block))),
      ...logs,
      ...(await reg.queryFilter(reg.filters.DIDRevoked(identity), Number(block), Number(block))),
    ];
    const prev = all.map((l) => l.args.previousChange).reduce((a, b) => (a === null || b < a ? b : a), null);
    if (prev === null || prev >= block) break;
    block = prev;
  }
  return { key: null, hops };
}

describe("MOBIVIDRegistry — D11b regression: anchorVehicleKey", function () {
  async function deployFixture() {
    const [manufacturer, firstOwner, buyer, stranger] = await ethers.getSigners();
    const vehicle = ethers.Wallet.createRandom().address;
    const v1 = await (await ethers.getContractFactory(V1_FQN, manufacturer)).deploy();
    await v1.waitForDeployment();
    const v2 = await (await ethers.getContractFactory(V2_FQN, manufacturer)).deploy();
    await v2.waitForDeployment();
    for (const reg of [v1, v2]) {
      await reg.connect(manufacturer).registerVehicleBirth(vehicle, VIN_HASH, "enc:vin", CERT_HASH, firstOwner.address, "0x1234");
    }
    return { v1, v2, manufacturer, firstOwner, buyer, stranger, vehicle };
  }

  it("the registering manufacturer anchors the birth key once: attribute event, lifetime validity, list pointer kept (gas sanity)", async function () {
    const { v1, v2, manufacturer, vehicle } = await loadFixture(deployFixture);
    for (const reg of [v1, v2]) {
      const before = await reg.changed(vehicle);
      const tx = await reg.connect(manufacturer).anchorVehicleKey(vehicle, KEY65);
      const receipt = await tx.wait();
      const ts = BigInt((await ethers.provider.getBlock(receipt.blockNumber)).timestamp);
      console.log(`        [gas] MOBI anchorVehicleKey (manufacturer, birth session): ${receipt.gasUsed.toString()}`);
      await expect(tx).to.emit(reg, "DIDAttributeChanged").withArgs(vehicle, KEY_NAME, KEY65, ts + HUNDRED_YEARS, before);
      await expect(tx).to.emit(reg, "VehicleKeyAnchored").withArgs(vehicle, ethers.keccak256(KEY65), manufacturer.address, ts + HUNDRED_YEARS);
      expect(await reg.vehicleKeyAnchored(vehicle)).to.be.true;
      expect(await reg.changed(vehicle)).to.equal(BigInt(receipt.blockNumber));
      expect(await reg.VEHICLE_KEY_ATTRIBUTE()).to.equal(KEY_NAME);

      await expect(reg.connect(manufacturer).anchorVehicleKey(vehicle, KEY33))
        .to.be.revertedWith("Vehicle key already anchored");
    }
  });

  it("a verifier with no off-chain record resolves the anchored key from the event walk (the D11b property)", async function () {
    const { v1, manufacturer, firstOwner, vehicle } = await loadFixture(deployFixture);
    expect((await resolveKeyFromEvents(v1, vehicle)).key).to.equal(null); // before the fix there was nothing to find
    await (await v1.connect(manufacturer).anchorVehicleKey(vehicle, KEY65)).wait();
    expect((await resolveKeyFromEvents(v1, vehicle)).key).to.equal(KEY65);
    // a later unrelated change does not hide the key: the walk follows previousChange
    await (await v1.connect(firstOwner).setAttribute(vehicle, ethers.encodeBytes32String("odometer"), "0x01", 3600)).wait();
    const r = await resolveKeyFromEvents(v1, vehicle);
    expect(r.key).to.equal(KEY65);
    expect(r.hops).to.equal(2);
  });

  it("the identity owner may anchor at any time (rotation): the newest valid key wins", async function () {
    const { v1, manufacturer, firstOwner, vehicle } = await loadFixture(deployFixture);
    await (await v1.connect(manufacturer).anchorVehicleKey(vehicle, KEY65)).wait();
    await (await v1.connect(firstOwner).anchorVehicleKey(vehicle, KEY_ROTATED)).wait();
    expect((await resolveKeyFromEvents(v1, vehicle)).key).to.equal(KEY_ROTATED);
  });

  it("refuses strangers, a manufacturer after the first sale, bad key lengths, unregistered and revoked identities", async function () {
    const { v1, manufacturer, firstOwner, buyer, stranger, vehicle } = await loadFixture(deployFixture);
    await expect(v1.connect(stranger).anchorVehicleKey(vehicle, KEY65))
      .to.be.revertedWith("Only the identity owner or the registering manufacturer");
    await expect(v1.connect(manufacturer).anchorVehicleKey(vehicle, "0x0102"))
      .to.be.revertedWith("Invalid secp256k1 public key length");
    await expect(v1.connect(manufacturer).anchorVehicleKey(ethers.Wallet.createRandom().address, KEY65))
      .to.be.revertedWith("Vehicle not registered");

    // first sale: the manufacturer's one-time power is gone even though it never used it
    await (await v1.connect(firstOwner).transferVehicleOwnership(vehicle, buyer.address, 12000, "BC ICBC")).wait();
    await expect(v1.connect(manufacturer).anchorVehicleKey(vehicle, KEY65))
      .to.be.revertedWith("Vehicle has changed hands: only the owner can anchor");
    await expect(v1.connect(firstOwner).anchorVehicleKey(vehicle, KEY65))
      .to.be.revertedWith("Only the identity owner or the registering manufacturer");
    await (await v1.connect(buyer).anchorVehicleKey(vehicle, KEY33)).wait();
    expect((await resolveKeyFromEvents(v1, vehicle)).key).to.equal(KEY33);

    await (await v1.connect(buyer).revokeIdentity(vehicle)).wait();
    await expect(v1.connect(buyer).anchorVehicleKey(vehicle, KEY65)).to.be.revertedWith("Identity is revoked");
  });
});
