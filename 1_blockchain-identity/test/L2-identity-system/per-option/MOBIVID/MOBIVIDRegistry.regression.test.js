/**
 * Regression tests for the MOBI VID registries:
 *
 *   D10  getVehicleDID returned did:ethr:0x<chainId>:<40 hex> WITHOUT the 0x
 *        prefix on the address — not a conformant did:ethr identifier (the
 *        adapter's resolve() copied it verbatim).
 *   D16  (via the D21 fix in the inherited ERC1056Registry) revokeIdentity was
 *        repeatable and changeOwner ignored the revoked flag.
 *
 * Contracts under test live in contracts/MOBI/ (byte-identical to
 * cv2x-testbed/contracts/).
 */

const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-toolbox/network-helpers");

const V1_FQN = "contracts/MOBI/MOBIVIDRegistry.sol:MOBIVIDRegistry";
const V2_FQN = "contracts/MOBI/MOBIVIDRegistryV2.sol:MOBIVIDRegistryV2";
const DID_ETHR = /^did:ethr:0x[0-9a-f]+:0x[0-9a-f]{40}$/;

const VIN_HASH = ethers.keccak256(ethers.toUtf8Bytes("WBA3A5C50CF123456:salt"));
const BIRTH_CERT_HASH = ethers.keccak256(ethers.toUtf8Bytes("signed-birth-vc"));

describe("MOBIVIDRegistry — D10 / D16 regression", function () {
  async function deployFixture() {
    const [manufacturer, firstOwner, buyer, stranger] = await ethers.getSigners();
    const vehicleKey = ethers.Wallet.createRandom().connect(ethers.provider);
    const v1 = await (await ethers.getContractFactory(V1_FQN, manufacturer)).deploy();
    await v1.waitForDeployment();
    const v2 = await (await ethers.getContractFactory(V2_FQN, manufacturer)).deploy();
    await v2.waitForDeployment();
    for (const reg of [v1, v2]) {
      await reg.connect(manufacturer).registerVehicleBirth(
        vehicleKey.address, VIN_HASH, "enc:vin", BIRTH_CERT_HASH, firstOwner.address, "0x"
      );
    }
    return { v1, v2, manufacturer, firstOwner, buyer, stranger, vehicle: vehicleKey.address };
  }

  describe("D10 — getVehicleDID is a conformant did:ethr identifier", function () {
    it("matches ^did:ethr:0x[0-9a-f]+:0x[0-9a-f]{40}$ with the lowercased vehicle address", async function () {
      const { v1, v2, vehicle } = await loadFixture(deployFixture);
      const chainId = (await ethers.provider.getNetwork()).chainId;
      for (const reg of [v1, v2]) {
        const did = await reg.getVehicleDID(vehicle);
        expect(did).to.match(DID_ETHR);
        const [, , chainPart, addressPart] = did.split(":");
        expect(chainPart).to.equal("0x" + chainId.toString(16)); // unpadded hex chain id, as before
        expect(addressPart).to.equal(vehicle.toLowerCase());
        expect(ethers.getAddress(addressPart)).to.equal(vehicle); // round-trips to the checksummed address
      }
    });

    it("zero-pads the address to 40 hex characters", async function () {
      const { v1 } = await loadFixture(deployFixture);
      const small = "0x" + "00".repeat(19) + "2a";
      const did = await v1.getVehicleDID(small);
      expect(did).to.match(DID_ETHR);
      expect(did.split(":")[3]).to.equal(small);
    });
  });

  describe("D16 — revocation is terminal on the MOBI registries", function () {
    it("a second revokeIdentity reverts and revokedAt stays at the first decommissioning", async function () {
      const { v2, firstOwner, vehicle } = await loadFixture(deployFixture);
      const r = await (await v2.connect(firstOwner).revokeIdentity(vehicle)).wait();
      const ts = BigInt((await ethers.provider.getBlock(r.blockNumber)).timestamp);
      expect(await v2.revokedAt(vehicle)).to.equal(ts);
      await expect(v2.connect(firstOwner).revokeIdentity(vehicle)).to.be.revertedWith("Identity already revoked");
      expect(await v2.revokedAt(vehicle)).to.equal(ts);
      // DIDRevoked links back to the birth block (DIDOwnerChanged emitted by registerVehicleBirth)
      const ev = await v2.queryFilter(v2.filters.DIDRevoked(vehicle), r.blockNumber, r.blockNumber);
      const birth = await v2.queryFilter(v2.filters.DIDOwnerChanged(vehicle), 0, r.blockNumber - 1);
      expect(ev[0].args.previousChange).to.equal(BigInt(birth[birth.length - 1].blockNumber));
    });

    it("changeOwner and transferVehicleOwnership revert for a revoked vehicle; the owner record is frozen", async function () {
      const { v2, firstOwner, buyer, vehicle } = await loadFixture(deployFixture);
      await v2.connect(firstOwner).revokeIdentity(vehicle);
      await expect(v2.connect(firstOwner).changeOwner(vehicle, buyer.address)).to.be.revertedWith("MOBIVID: use transferVehicleOwnership"); // K-3 (merge 2026-10-06): the public changeOwner is closed for born vehicles before the revoked check is reached
      await expect(
        v2.connect(firstOwner).transferVehicleOwnership(vehicle, buyer.address, 1000, "CA DMV")
      ).to.be.revertedWith("Vehicle identity is revoked");
      const [, currentOwner, isRevoked, transfers] = await v2.getVehicleInfo(vehicle);
      expect(currentOwner).to.equal(firstOwner.address);
      expect(isRevoked).to.be.true;
      expect(transfers).to.equal(0n);
    });

    it("a non-revoked vehicle still changes hands (control case for the gate)", async function () {
      const { v2, firstOwner, buyer, vehicle } = await loadFixture(deployFixture);
      // K-3 (merge 2026-10-06): born vehicles change hands only through transferVehicleOwnership
      await expect(v2.connect(firstOwner).changeOwner(vehicle, buyer.address)).to.be.revertedWith("MOBIVID: use transferVehicleOwnership");
      await expect(v2.connect(firstOwner).transferVehicleOwnership(vehicle, buyer.address, 1000, "CA DMV")).to.emit(v2, "DIDOwnerChanged");
      expect(await v2.identityOwner(vehicle)).to.equal(buyer.address);
    });
  });
});
