const { expect } = require("chai");
const { ethers } = require("hardhat");

// Regression for defects D7 and D8 (docs/DEFECT_LOG.md, found by the S7 feature demos,
// fixed 2026-10-04):
//   D7  an issuer that was also an approved operator could move the BIRTH_CERT through the
//       standard safeTransferFrom, which does not re-bind vehicleVIN / vinHashToVehicle; a
//       later issuerTransferCredential then propagated an empty VIN (keccak256("")).
//   D8  standard transfers reached unregistered addresses; burning the BIRTH_CERT orphaned
//       the vehicle's other credentials; the standard URI event was never emitted.
// Fix: the standard entry points always revert; the issuer paths keep three invariants
// (non-BIRTH credentials only on registered vehicles; the BIRTH_CERT never leaves an
// address that still holds credentials unless the whole identity moves atomically through
// issuerTransferIdentity; credential types bounded to 1..255 so the held set is enumerable).
describe("ERC-1155 CVINVehicleCredential1155 — soulbound re-binding regression (D7/D8)", function () {
  const VIN = "1HGBH41JXMN109186";
  const BIRTH_CERT = 1n, REGISTRATION = 2n, INSPECTION_CERT = 3n, INSURANCE_CERT = 4n, MAINTENANCE_BADGE = 5n;
  let c, issuer, vehicle, buyer, other, vinHash;

  beforeEach(async function () {
    [issuer, vehicle, buyer, other] = await ethers.getSigners();
    const C = await ethers.getContractFactory("CVINVehicleCredential1155", issuer);
    c = await C.deploy();
    await c.waitForDeployment();
    vinHash = ethers.keccak256(ethers.toUtf8Bytes(VIN));
    await (await c.registerVehicle(vehicle.address, VIN)).wait();
    await (await c.issueCredential(vehicle.address, INSPECTION_CERT, 1)).wait();
    await (await c.issueCredential(vehicle.address, MAINTENANCE_BADGE, 3)).wait();
  });

  describe("D7 — the standard transfer path is closed for everyone", function () {
    it("an issuer that is also an approved operator cannot move the BIRTH_CERT through safeTransferFrom", async function () {
      await (await c.connect(vehicle).setApprovalForAll(issuer.address, true)).wait();
      await expect(
        c.connect(issuer).safeTransferFrom(vehicle.address, buyer.address, BIRTH_CERT, 1, "0x")
      ).to.be.revertedWith("CVIN1155: credentials are soulbound (issuer-mediated transfer only)");
      expect(await c.balanceOf(vehicle.address, BIRTH_CERT)).to.equal(1n);
      expect(await c.vehicleVIN(vehicle.address)).to.equal(VIN);
      expect(await c.vinHashToVehicle(vinHash)).to.equal(vehicle.address);
    });

    it("the batch entry point is closed identically, even for an approved issuer", async function () {
      await (await c.connect(vehicle).setApprovalForAll(issuer.address, true)).wait();
      await expect(
        c.connect(issuer).safeBatchTransferFrom(vehicle.address, buyer.address, [INSPECTION_CERT, MAINTENANCE_BADGE], [1, 1], "0x")
      ).to.be.revertedWith("CVIN1155: credentials are soulbound (issuer-mediated transfer only)");
      expect(await c.balanceOf(buyer.address, INSPECTION_CERT)).to.equal(0n);
    });

    it("holder and non-issuer operator are still refused", async function () {
      await expect(
        c.connect(vehicle).safeTransferFrom(vehicle.address, buyer.address, MAINTENANCE_BADGE, 1, "0x")
      ).to.be.revertedWith("CVIN1155: credentials are soulbound (issuer-mediated transfer only)");
      await (await c.connect(vehicle).setApprovalForAll(other.address, true)).wait();
      await expect(
        c.connect(other).safeTransferFrom(vehicle.address, buyer.address, MAINTENANCE_BADGE, 1, "0x")
      ).to.be.revertedWith("CVIN1155: credentials are soulbound (issuer-mediated transfer only)");
    });
  });

  describe("D8 — invariants on the issuer paths", function () {
    it("a non-BIRTH credential cannot be moved to an unregistered address", async function () {
      await expect(
        c.issuerTransferCredential(vehicle.address, buyer.address, MAINTENANCE_BADGE)
      ).to.be.revertedWith("CVIN1155: recipient not registered");
    });

    it("the BIRTH_CERT cannot be moved on its own while the vehicle holds other credentials", async function () {
      await expect(
        c.issuerTransferCredential(vehicle.address, buyer.address, BIRTH_CERT)
      ).to.be.revertedWith("CVIN1155: identity holds other credentials (use issuerTransferIdentity)");
    });

    it("the BIRTH_CERT cannot be moved onto an address that is already a registered vehicle", async function () {
      await (await c.registerVehicle(buyer.address, "2HGBH41JXMN109187")).wait();
      await (await c.revokeCredential(vehicle.address, INSPECTION_CERT, 1)).wait();
      await (await c.revokeCredential(vehicle.address, MAINTENANCE_BADGE, 3)).wait();
      await expect(
        c.issuerTransferCredential(vehicle.address, buyer.address, BIRTH_CERT)
      ).to.be.revertedWith("CVIN1155: recipient already registered");
      await expect(c.issuerTransferIdentity(vehicle.address, buyer.address))
        .to.be.revertedWith("CVIN1155: recipient already registered");
    });

    it("issuerTransferCredential of the BIRTH_CERT alone still works for a vehicle with nothing else (the benchmark path)", async function () {
      await (await c.revokeCredential(vehicle.address, INSPECTION_CERT, 1)).wait();
      await (await c.revokeCredential(vehicle.address, MAINTENANCE_BADGE, 3)).wait();
      const tx = await c.issuerTransferCredential(vehicle.address, buyer.address, BIRTH_CERT);
      const receipt = await tx.wait();
      console.log(`        [gas] ERC-1155 issuerTransferCredential(BIRTH_CERT) after D7/D8: ${receipt.gasUsed.toString()}`);
      expect(await c.vehicleVIN(buyer.address)).to.equal(VIN);
      expect(await c.vinHashToVehicle(vinHash)).to.equal(buyer.address);
      expect(await c.vehicleVIN(vehicle.address)).to.equal("");
    });

    it("burning the BIRTH_CERT is refused while other credentials are held, and deregisters once they are revoked", async function () {
      await expect(c.revokeCredential(vehicle.address, BIRTH_CERT, 1))
        .to.be.revertedWith("CVIN1155: revoke the vehicle's other credentials first");
      await (await c.revokeCredential(vehicle.address, INSPECTION_CERT, 1)).wait();
      await (await c.revokeCredential(vehicle.address, MAINTENANCE_BADGE, 3)).wait();
      await (await c.revokeCredential(vehicle.address, BIRTH_CERT, 1)).wait();
      expect(await c.isRegistered(vehicle.address)).to.be.false;
      expect(await c.vinHashToVehicle(vinHash)).to.equal(ethers.ZeroAddress);
      expect(await c.credentialTypesOf(vehicle.address)).to.deep.equal([]);
    });

    it("credential types are bounded to 1..255 so the held set is enumerable", async function () {
      expect(await c.MAX_CREDENTIAL_TYPE()).to.equal(255n);
      await expect(c.issueCredential(vehicle.address, 256, 1))
        .to.be.revertedWith("CVIN1155: credential type out of range");
      await (await c.issueCredential(vehicle.address, 255, 1)).wait();
      expect(await c.credentialTypesOf(vehicle.address)).to.deep.equal([INSPECTION_CERT, MAINTENANCE_BADGE, 255n]);
    });

    it("credentialTypesOf follows issue, partial burn and full burn", async function () {
      expect(await c.credentialTypesOf(vehicle.address)).to.deep.equal([INSPECTION_CERT, MAINTENANCE_BADGE]);
      await (await c.revokeCredential(vehicle.address, MAINTENANCE_BADGE, 2)).wait(); // 3 -> 1: still held
      expect(await c.credentialTypesOf(vehicle.address)).to.deep.equal([INSPECTION_CERT, MAINTENANCE_BADGE]);
      await (await c.revokeCredential(vehicle.address, MAINTENANCE_BADGE, 1)).wait(); // 1 -> 0: cleared
      expect(await c.credentialTypesOf(vehicle.address)).to.deep.equal([INSPECTION_CERT]);
      await (await c.issueCredential(vehicle.address, REGISTRATION, 1)).wait();
      expect(await c.credentialTypesOf(vehicle.address)).to.deep.equal([REGISTRATION, INSPECTION_CERT]);
    });

    it("setTokenURI emits the standard URI(value, id) event as well as CredentialURIUpdated", async function () {
      await expect(c.setTokenURI(INSURANCE_CERT, "ipfs://insurance/v2.json"))
        .to.emit(c, "URI").withArgs("ipfs://insurance/v2.json", INSURANCE_CERT)
        .and.to.emit(c, "CredentialURIUpdated").withArgs(INSURANCE_CERT, "ipfs://insurance/v2.json");
    });
  });

  describe("issuerTransferIdentity — the whole identity moves atomically (D7 fix)", function () {
    it("moves the BIRTH_CERT and every held credential, re-binds the VIN and emits IdentityRebound (gas sanity)", async function () {
      const tx = await c.issuerTransferIdentity(vehicle.address, buyer.address);
      const receipt = await tx.wait();
      console.log(`        [gas] ERC-1155 issuerTransferIdentity (BIRTH_CERT + 2 types): ${receipt.gasUsed.toString()}`);
      await expect(tx).to.emit(c, "IdentityRebound").withArgs(vehicle.address, buyer.address, vinHash, 2n);
      await expect(tx).to.emit(c, "TransferBatch");

      expect(await c.isRegistered(vehicle.address)).to.be.false;
      expect(await c.isRegistered(buyer.address)).to.be.true;
      expect(await c.vehicleVIN(buyer.address)).to.equal(VIN);
      expect(await c.vehicleVIN(vehicle.address)).to.equal("");
      expect(await c.vinHashToVehicle(vinHash)).to.equal(buyer.address);
      expect(await c.vinHashToVehicle(ethers.keccak256("0x"))).to.equal(ethers.ZeroAddress); // no keccak("") alias (the D7 symptom)

      const [bA, bB] = await Promise.all([
        c.balanceOfBatch([vehicle.address, vehicle.address, vehicle.address], [BIRTH_CERT, INSPECTION_CERT, MAINTENANCE_BADGE]),
        c.balanceOfBatch([buyer.address, buyer.address, buyer.address], [BIRTH_CERT, INSPECTION_CERT, MAINTENANCE_BADGE]),
      ]);
      expect([...bA]).to.deep.equal([0n, 0n, 0n]);
      expect([...bB]).to.deep.equal([1n, 1n, 3n]);
      expect(await c.credentialTypesOf(vehicle.address)).to.deep.equal([]);
      expect(await c.credentialTypesOf(buyer.address)).to.deep.equal([INSPECTION_CERT, MAINTENANCE_BADGE]);
    });

    it("refuses an unregistered source, a self-transfer and a non-issuer caller", async function () {
      await expect(c.issuerTransferIdentity(buyer.address, other.address)).to.be.revertedWith("CVIN1155: vehicle not registered");
      await expect(c.issuerTransferIdentity(vehicle.address, vehicle.address)).to.be.revertedWith("CVIN1155: transfer to same holder");
      await expect(c.connect(vehicle).issuerTransferIdentity(vehicle.address, buyer.address))
        .to.be.revertedWithCustomError(c, "AccessControlUnauthorizedAccount");
    });

    it("after the move the new holder can receive, and the old address cannot, further credentials", async function () {
      await (await c.issuerTransferIdentity(vehicle.address, buyer.address)).wait();
      await (await c.issueCredential(buyer.address, INSURANCE_CERT, 1)).wait();
      await expect(c.issueCredential(vehicle.address, INSURANCE_CERT, 1)).to.be.revertedWith("CVIN1155: vehicle not registered");
      expect(await c.credentialTypesOf(buyer.address)).to.deep.equal([INSPECTION_CERT, INSURANCE_CERT, MAINTENANCE_BADGE]);
    });
  });
});
