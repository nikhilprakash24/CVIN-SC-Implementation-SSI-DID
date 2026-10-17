// Native-pattern checks for O5 (ERC-1155 credential tokens) and O6 (ERC-4337 validateUserOp).
const { expect } = require("chai");
const { ethers } = require("hardhat");

const did = (c, rc) => rc.logs.map(l => { try { return c.interface.parseLog(l); } catch { return null; } }).find(e => e && e.name === "DIDCreated").args.did;
const cred = (c, rc) => rc.logs.map(l => { try { return c.interface.parseLog(l); } catch { return null; } }).find(e => e && e.name === "CredentialIssued").args.credentialId;

describe("O5_ERC1155 — credentials are soulbound tokens", function () {
  let ssi, a, b, issuer, subject;
  beforeEach(async () => {
    [a, b] = await ethers.getSigners();
    ssi = await (await ethers.getContractFactory("O5_ERC1155")).deploy();
    issuer = did(ssi, await (await ssi.connect(a).createDID(a.address)).wait());
    subject = did(ssi, await (await ssi.connect(b).createDID(b.address)).wait());
  });
  it("identity token minted (balance 1); issueCredential mints a credential token to the subject; revoke burns it", async () => {
    expect(await ssi.balanceOf(a.address, BigInt(issuer))).to.equal(1);
    const id = cred(ssi, await (await ssi.connect(a).issueCredential(issuer, subject, ethers.id("vc"), 0)).wait());
    expect(await ssi.balanceOf(b.address, BigInt(id))).to.equal(1);
    await ssi.connect(a).revokeCredential(id);
    expect(await ssi.balanceOf(b.address, BigInt(id))).to.equal(0);
    const [valid, , revoked] = await ssi.verifyCredential(id);
    expect(valid).to.equal(false); expect(revoked).to.equal(true);
  });
  it("tokens are soulbound; the identity token cannot be burned; deactivation keeps it", async () => {
    await expect(ssi.connect(a).safeTransferFrom(a.address, b.address, BigInt(issuer), 1, "0x")).to.be.revertedWithCustomError(ssi, "Soulbound");
    await ssi.connect(a).deactivateDID(issuer);
    expect(await ssi.balanceOf(a.address, BigInt(issuer))).to.equal(1);
    const [doc] = await ssi.resolveDID(issuer); expect(doc.length).to.be.greaterThan(2);
  });
});

describe("O6_ERC4337 — validateUserOp and session keys", function () {
  let ssi, acct, a, b, s, d;
  beforeEach(async () => {
    [a, b, s] = await ethers.getSigners();
    ssi = await (await ethers.getContractFactory("O6_ERC4337")).deploy();
    d = did(ssi, await (await ssi.connect(a).createDID(a.address)).wait());
    acct = await ethers.getContractAt("SmartAccount", ethers.getAddress("0x" + d.slice(26)));
  });
  const op = (sig = "0x") => ({ sender: acct.target, nonce: 0, initCode: "0x", callData: "0x", accountGasLimits: ethers.ZeroHash, preVerificationGas: 0, gasFees: ethers.ZeroHash, paymasterAndData: "0x", signature: sig });
  it("a signed op from the owner validates (0); from a stranger fails (1); from a session key returns packed validUntil", async () => {
    const h = ethers.id("userop-1");
    expect(await acct.validateUserOp(op(await a.signMessage(ethers.getBytes(h))), h, 0)).to.equal(0);
    expect(await acct.validateUserOp(op(await b.signMessage(ethers.getBytes(h))), h, 0)).to.equal(1);
    await ssi.connect(a).addDelegate(d, ethers.id("sigAuth"), s.address, 1000); // session key via F11
    const v = await acct.validateUserOp(op(await s.signMessage(ethers.getBytes(h))), h, 0);
    const validUntil = (v >> 160n) & ((1n << 48n) - 1n), validAfter = v >> 208n;
    const now = BigInt((await ethers.provider.getBlock("latest")).timestamp);
    expect(validUntil).to.equal(now + 1000n); expect(validAfter).to.equal(now);
  });
  it("direct path agrees with validateUserOp: session key acts via the registry until expiry, then is refused", async () => {
    await ssi.connect(a).addDelegate(d, ethers.id("sigAuth"), s.address, 100);
    await expect(ssi.connect(s).updateDID(d, ethers.id("svc"), "0x01", 1)).to.emit(ssi, "DIDUpdated"); // session key authorised
    expect(await ssi.validDelegate(d, ethers.id("sigAuth"), s.address)).to.equal(true);
    await ethers.provider.send("evm_increaseTime", [200]); await ethers.provider.send("evm_mine");
    expect(await ssi.validDelegate(d, ethers.id("sigAuth"), s.address)).to.equal(false);
    await expect(ssi.connect(s).updateDID(d, ethers.id("svc"), "0x01", 1)).to.be.revertedWithCustomError(ssi, "NotAuthorized");
  });
  it("a 20-byte verification method is a validation key with full authority; the last one cannot be removed", async () => {
    const rc = await (await ssi.connect(a).addVerificationMethod(d, ethers.id("EcdsaSecp256k1"), b.address)).wait();
    const keyId = rc.logs.map(l => { try { return ssi.interface.parseLog(l); } catch { return null; } }).find(e => e && e.name === "VerificationMethodAdded").args.keyId;
    expect(await acct.isValidationKey(b.address)).to.equal(true);
    await expect(ssi.connect(b).deactivateDID(d)).to.not.be.reverted; // b now controls
    const d2 = did(ssi, await (await ssi.connect(a).createDID(a.address)).wait());
    const rc2 = await (await ssi.connect(a).addVerificationMethod(d2, ethers.id("k"), b.address)).wait();
    const k2 = rc2.logs.map(l => { try { return ssi.interface.parseLog(l); } catch { return null; } }).find(e => e && e.name === "VerificationMethodAdded").args.keyId;
    await ssi.connect(a).removeVerificationMethod(d2, k2);
    await expect(ssi.connect(a).removeVerificationMethod(d2, k2)).to.be.reverted;
    void keyId;
  });
});
