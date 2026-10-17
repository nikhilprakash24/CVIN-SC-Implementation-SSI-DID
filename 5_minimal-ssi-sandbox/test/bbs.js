// BBS+ selective disclosure over VID credential objects (off-chain; no chain interaction).
const { expect } = require("chai");
const { ethers } = require("hardhat");
const V = require("../lib/vid/credentials");
const B = require("../lib/vid/bbs");

describe("BBS+ layer (lib/vid/bbs.js)", function () {
  this.timeout(60000);
  let kp, lic, signed;
  before(async () => {
    const [dmvS] = await ethers.getSigners();
    kp = await B.issuerKeyPair();
    lic = V.driverLicence({ dmvDid: ethers.id("dmv"), holderDid: ethers.id("drv"), licenceClass: "5", restrictions: [], jurisdiction: "CA-BC", validFrom: "2026-09-01", validUntil: "2031-09-01", birthYear: 1995, birthSalt: "s" });
    signed = await B.sign(kp, lic.body);
    void dmvS;
  });

  it("signature over the ordered claim vector verifies; a changed claim does not", async () => {
    expect(await B.verifySignature(signed)).to.equal(true);
    const bad = { ...signed, messages: signed.messages.map(m => (m.startsWith("licenceClass=") ? 'licenceClass="1"' : m)) };
    expect(await B.verifySignature(bad)).to.equal(false);
  });

  it("derived proof reveals only the chosen claims, is nonce-bound, and verifies with the public key alone", async () => {
    const d = await B.createProof(signed, ["licenceClass", "validUntil"], "n1");
    expect(d.revealedMessages.length).to.equal(2);
    expect(d.revealedMessages.every(m => /^(licenceClass|validUntil)=/.test(m))).to.equal(true);
    expect(await B.verifyProof(signed.publicKey, d, "n1")).to.equal(true);
    expect(await B.verifyProof(signed.publicKey, d, "n2")).to.equal(false);
    const tampered = { ...d, revealedMessages: d.revealedMessages.map(m => (m.startsWith("licenceClass=") ? 'licenceClass="1"' : m)) };
    expect(await B.verifyProof(signed.publicKey, tampered, "n1")).to.equal(false);
  });

  it("proofs are unlinkable across presentations and the anchor is unchanged", async () => {
    const a = await B.createProof(signed, ["jurisdiction"], "x"), b = await B.createProof(signed, ["jurisdiction"], "y");
    expect(Buffer.from(a.proof).equals(Buffer.from(b.proof))).to.equal(false);
    expect(lic.anchor).to.equal(V.typedHash(lic.typeId, lic.schemaHash, V.contentHash(lic.body)));
  });
});
