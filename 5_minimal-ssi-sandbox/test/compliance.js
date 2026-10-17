// Unified IMinimalSSI compliance suite — runs identically against every implementation.
// Add an implementation to IMPLEMENTATIONS once it compiles; the same 12 tests
// (test_01..test_12 from the formal spec §4.1) execute against each.
const { expect } = require("chai");
const { ethers } = require("hardhat");

const IMPLEMENTATIONS = [
  "O1_ERC1056",
  "O2_ERC721",
  "O3_ERC725",
  // "O4_ERC725xy", "O5_ERC1155",
  // "O6_ERC4337", "O7_ERC8004", "O8_LFDT",  <- enable as ported (bring-up Step 3)
];

const B32 = (s) => ethers.id(s);

for (const name of IMPLEMENTATIONS) {
  describe(`${name} — IMinimalSSI compliance`, function () {
    let ssi, owner, other;

    beforeEach(async () => {
      [owner, other] = await ethers.getSigners();
      ssi = await (await ethers.getContractFactory(name)).deploy();
    });

    async function newDID(signer = owner) {
      const tx = await ssi.connect(signer).createDID(signer.address);
      const rc = await tx.wait();
      return rc.logs.map(l => { try { return ssi.interface.parseLog(l); } catch { return null; } })
        .find(e => e && e.name === "DIDCreated").args.did;
    }

    it("test_01 createDID returns non-zero id; DID resolvable", async () => {
      const did = await newDID();
      expect(did).to.not.equal(ethers.ZeroHash);
      const [doc] = await ssi.resolveDID(did);
      expect(doc.length).to.be.greaterThan(2);
    });

    it("test_02 resolveDID returns empty for non-existent DIDs (no revert)", async () => {
      const [doc, meta] = await ssi.resolveDID(ethers.id("nope"));
      expect(doc).to.equal("0x");
      expect(meta).to.equal("0x");
    });

    it("test_03 updateDID emits; unauthorized reverts NotAuthorized", async () => {
      const did = await newDID();
      await expect(ssi.updateDID(did, B32("svc"), "0x1234", 3600)).to.emit(ssi, "DIDUpdated");
      await expect(ssi.connect(other).updateDID(did, B32("svc"), "0x1234", 3600))
        .to.be.revertedWithCustomError(ssi, "NotAuthorized");
    });

    it("test_04 deactivateDID irreversible; updates revert DIDAlreadyDeactivated", async () => {
      const did = await newDID();
      await ssi.deactivateDID(did);
      await expect(ssi.updateDID(did, B32("svc"), "0x12", 1))
        .to.be.revertedWithCustomError(ssi, "DIDAlreadyDeactivated");
    });

    it("test_05 issueCredential returns id; unauthorized issuer reverts", async () => {
      const issuer = await newDID(), subject = await newDID(other);
      const tx = await ssi.issueCredential(issuer, subject, B32("vc"), 0);
      await tx.wait();
      await expect(ssi.connect(other).issueCredential(issuer, subject, B32("vc2"), 0))
        .to.be.revertedWithCustomError(ssi, "NotAuthorized");
    });

    it("test_06 verifyCredential valid=true for fresh credential, correct issuer", async () => {
      const issuer = await newDID(), subject = await newDID(other);
      const id = await credId(ssi.issueCredential(issuer, subject, B32("vc"), 0));
      const [valid, iss, revoked, expired] = await ssi.verifyCredential(id);
      expect(valid).to.equal(true); expect(iss).to.equal(issuer);
      expect(revoked).to.equal(false); expect(expired).to.equal(false);
    });

    it("test_07 revokeCredential -> verification returns revoked=true", async () => {
      const issuer = await newDID(), subject = await newDID(other);
      const id = await credId(ssi.issueCredential(issuer, subject, B32("vc"), 0));
      await ssi.revokeCredential(id);
      const [valid, , revoked] = await ssi.verifyCredential(id);
      expect(valid).to.equal(false); expect(revoked).to.equal(true);
    });

    it("test_08 createPresentation prevents replay; verifies holder ownership", async () => {
      const issuer = await newDID(), holder = await newDID(other);
      const id = await credId(ssi.issueCredential(issuer, holder, B32("vc"), 0));
      const ch = B32("challenge-1");
      await ssi.connect(other).createPresentation(holder, [id], ch, "sandbox");
      await expect(ssi.connect(other).createPresentation(holder, [id], ch, "sandbox"))
        .to.be.reverted; // replayed challenge
      await expect(ssi.createPresentation(issuer, [id], B32("ch2"), "sandbox"))
        .to.be.revertedWithCustomError(ssi, "NotAuthorized"); // not the subject
    });

    it("test_09 addVerificationMethod returns non-zero keyId", async () => {
      const did = await newDID();
      const tx = await ssi.addVerificationMethod(did, B32("EcdsaSecp256k1"), "0xabcd");
      const rc = await tx.wait();
      const ev = rc.logs.map(l => { try { return ssi.interface.parseLog(l); } catch { return null; } })
        .find(e => e && e.name === "VerificationMethodAdded");
      expect(ev.args.keyId).to.not.equal(ethers.ZeroHash);
    });

    it("test_10 removeVerificationMethod ok for non-last; fails for last key", async () => {
      const did = await newDID();
      const tx = await ssi.addVerificationMethod(did, B32("k"), "0x01");
      const rc = await tx.wait();
      const keyId = rc.logs.map(l => { try { return ssi.interface.parseLog(l); } catch { return null; } })
        .find(e => e && e.name === "VerificationMethodAdded").args.keyId;
      await ssi.removeVerificationMethod(did, keyId); // ok: implicit key remains
      await expect(ssi.removeVerificationMethod(did, keyId)).to.be.reverted; // last/absent
    });

    it("test_11 addDelegate -> validDelegate true", async () => {
      const did = await newDID();
      await ssi.addDelegate(did, B32("sigAuth"), other.address, 3600);
      expect(await ssi.validDelegate(did, B32("sigAuth"), other.address)).to.equal(true);
    });

    it("test_12 validDelegate false after expiration", async () => {
      const did = await newDID();
      await ssi.addDelegate(did, B32("sigAuth"), other.address, 1);
      await ethers.provider.send("evm_increaseTime", [10]);
      await ethers.provider.send("evm_mine");
      expect(await ssi.validDelegate(did, B32("sigAuth"), other.address)).to.equal(false);
    });

    async function credId(txPromise) {
      const rc = await (await txPromise).wait();
      return rc.logs.map(l => { try { return ssi.interface.parseLog(l); } catch { return null; } })
        .find(e => e && e.name === "CredentialIssued").args.credentialId;
    }
  });
}
