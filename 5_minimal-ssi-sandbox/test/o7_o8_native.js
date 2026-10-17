// O7: the three ERC-8004 registries and ISetC over them (WO-2 AC). O8: Indy-on-Besu semantics (WO-3 AC).
const { expect } = require("chai");
const { ethers } = require("hardhat");

const ev = (c, rc, name) => rc.logs.map(l => { try { return c.interface.parseLog(l); } catch { return null; } }).find(e => e && e.name === name).args;

describe("O7_ERC8004 — registries + ISetC", function () {
  let ssi, idr, rep, val, owner, client1, client2, validator, did;
  beforeEach(async () => {
    [owner, client1, client2, validator] = await ethers.getSigners();
    ssi = await (await ethers.getContractFactory("O7_ERC8004")).deploy();
    idr = await ethers.getContractAt("IdentityRegistry8004", await ssi.identity());
    rep = await ethers.getContractAt("ReputationRegistry8004", await ssi.reputation());
    val = await ethers.getContractAt("ValidationRegistry8004", await ssi.validation());
    did = ev(ssi, await (await ssi.connect(owner).createDID(owner.address)).wait(), "DIDCreated").did;
  });

  it("createDID mints an agent NFT; owner is controller; registries are wired to the identity registry", async () => {
    expect(await idr.ownerOf(BigInt(did))).to.equal(owner.address);
    expect(await rep.getIdentityRegistry()).to.equal(await idr.getAddress());
    expect(await val.getIdentityRegistry()).to.equal(await idr.getAddress());
    expect(await idr.getAgentWallet(BigInt(did))).to.equal(owner.address);
  });

  it("C1/C2: clients give feedback; owner cannot self-attest; mean over clients; revocation drops it", async () => {
    await expect(ssi.connect(owner).attestReputation(did, 90, "ipfs://x")).to.be.revertedWithCustomError(rep, "SelfFeedback");
    await expect(ssi.connect(client1).attestReputation(did, 80, "ipfs://a")).to.emit(ssi, "ReputationAttested");
    await ssi.connect(client2).attestReputation(did, 60, "ipfs://b");
    let [mean, count] = await ssi.getReputation(did);
    expect(mean).to.equal(70); expect(count).to.equal(2);
    await rep.connect(client2).revokeFeedback(BigInt(did), 1); // native revoke
    [mean, count] = await ssi.getReputation(did);
    expect(mean).to.equal(80); expect(count).to.equal(1);
    const [v, d, t1] = await rep.readFeedback(BigInt(did), client1.address, 1);
    expect(v).to.equal(80); expect(d).to.equal(0); expect(t1).to.equal("starred");
  });

  it("C3/C4: owner requests validation naming a validator; only that validator responds; status maps 1→2/3", async () => {
    const payload = ethers.concat([validator.address, "0xdeadbeef"]);
    await expect(ssi.connect(client1).requestValidation(did, ethers.id("zkml"), payload)).to.be.revertedWithCustomError(ssi, "NotAuthorized");
    const rc = await (await ssi.connect(owner).requestValidation(did, ethers.id("zkml"), payload)).wait();
    const reqId = ev(ssi, rc, "ValidationRequested").requestId;
    expect(await ssi.validationStatus(reqId)).to.equal(1);
    await expect(val.connect(client1).validationResponse(reqId, 100, "", ethers.ZeroHash, "")).to.be.revertedWithCustomError(val, "NotValidator");
    await val.connect(validator).validationResponse(reqId, 100, "ipfs://proof", ethers.ZeroHash, "hard");
    expect(await ssi.validationStatus(reqId)).to.equal(2);
    await val.connect(validator).validationResponse(reqId, 10, "", ethers.ZeroHash, "re-run");
    expect(await ssi.validationStatus(reqId)).to.equal(3);
    expect(await ssi.validationStatus(ethers.id("none"))).to.equal(0);
    const [count, avg] = await val.getSummary(BigInt(did), [], "");
    expect(count).to.equal(1); expect(avg).to.equal(10);
  });

  it("agents are transferable: transfer changes the controller (recorded ERC-8004 semantics)", async () => {
    await idr.connect(owner).transferFrom(owner.address, client1.address, BigInt(did));
    await expect(ssi.connect(owner).updateDID(did, ethers.id("k"), "0x01", 1)).to.be.revertedWithCustomError(ssi, "NotAuthorized");
    await expect(ssi.connect(client1).updateDID(did, ethers.id("k"), "0x01", 1)).to.emit(ssi, "DIDUpdated");
    expect(await idr.getAgentWallet(BigInt(did))).to.equal(ethers.ZeroAddress); // cleared on transfer
  });
});

describe("O8_LFDT — Indy-on-Besu semantics", function () {
  let ssi, a, b, issuer, subject;
  beforeEach(async () => {
    [a, b] = await ethers.getSigners();
    ssi = await (await ethers.getContractFactory("O8_LFDT")).deploy();
    issuer = ev(ssi, await (await ssi.connect(a).createDID(a.address)).wait(), "DIDCreated").did;
    subject = ev(ssi, await (await ssi.connect(b).createDID(b.address)).wait(), "DIDCreated").did;
  });

  it("nym record resolvable by identity address with Indy metadata; document rewritten on update", async () => {
    const nym = ethers.getAddress("0x" + issuer.slice(26));
    let [doc, meta] = await ssi.resolveDid(nym);
    expect(meta.owner).to.equal(a.address); expect(meta.versionId).to.equal(1); expect(doc.length).to.be.greaterThan(2);
    await ssi.connect(a).updateDID(issuer, ethers.id("endpoint"), ethers.toUtf8Bytes("https://x"), 10);
    [doc, meta] = await ssi.resolveDid(nym);
    expect(meta.versionId).to.equal(2);
  });

  it("first issuance creates schema + cred-def + revocation registry; the credential hash is NOT stored; revoke = registry entry", async () => {
    expect(await ssi.issuerCredDef(issuer)).to.equal(ethers.ZeroHash);
    const rc = await (await ssi.connect(a).issueCredential(issuer, subject, ethers.id("vc"), 0)).wait();
    const names = rc.logs.map(l => { try { return ssi.interface.parseLog(l)?.name; } catch { return null; } }).filter(Boolean);
    expect(names).to.include.members(["SchemaCreated", "CredentialDefinitionCreated", "RevocationRegistryDefinitionCreated", "RevocationRegistryEntryCreated", "CredentialIssued"]);
    const cd = await ssi.issuerCredDef(issuer);
    expect(cd).to.not.equal(ethers.ZeroHash);
    const rc2 = await (await ssi.connect(a).issueCredential(issuer, subject, ethers.id("vc2"), 0)).wait();
    const names2 = rc2.logs.map(l => { try { return ssi.interface.parseLog(l)?.name; } catch { return null; } }).filter(Boolean);
    expect(names2).to.not.include("SchemaCreated"); // second issuance reuses the definition
    const id = ev(ssi, rc, "CredentialIssued").credentialId;
    const rr = ethers.keccak256(ethers.concat([ethers.toUtf8Bytes("revreg"), cd]));
    const acc0 = await ssi.currentAccumulator(rr);
    await expect(ssi.connect(a).revokeCredential(id)).to.emit(ssi, "RevocationRegistryEntryCreated");
    expect(await ssi.currentAccumulator(rr)).to.not.equal(acc0);
    const [valid, , revoked] = await ssi.verifyCredential(id);
    expect(valid).to.equal(false); expect(revoked).to.equal(true);
  });
});
