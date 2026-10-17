// Groth16 AgeGate: circuit, off-chain verification, and the exported on-chain verifier.
const { expect } = require("chai");
const { ethers } = require("hardhat");
const Z = require("../lib/vid/zk");

describe("ZK age gate (circuits/AgeGate.circom + contracts/zk)", function () {
  this.timeout(120000);
  let verifier, gate, venue, pr, cd, commitment;
  const salt = 123456789n, maxBirthYear = 2008;

  before(async () => {
    [, venue] = await ethers.getSigners();
    verifier = await (await ethers.getContractFactory("Groth16Verifier")).deploy();
    gate = await (await ethers.getContractFactory("ZKAgeGate")).deploy(await verifier.getAddress());
    commitment = await Z.commit(1995, salt);
    pr = await Z.prove({ birthYear: 1995, salt, commitment, maxBirthYear });
    cd = await Z.calldata(pr);
  });

  after(() => { if (globalThis.curve_bn128) globalThis.curve_bn128.terminate(); });

  it("a valid proof verifies off-chain and on-chain (view and tx), and replay is refused", async () => {
    expect(await Z.verifyOffChain(pr)).to.equal(true);
    expect(await gate.check(cd.a, cd.b, cd.c, cd.pub[0], cd.pub[1])).to.equal(true);
    await expect(gate.connect(venue).admit(ethers.id("p1"), cd.a, cd.b, cd.c, cd.pub[0], cd.pub[1])).to.emit(gate, "Admitted");
    await expect(gate.connect(venue).admit(ethers.id("p1"), cd.a, cd.b, cd.c, cd.pub[0], cd.pub[1])).to.be.revertedWithCustomError(gate, "Replay");
  });

  it("a proof is bound to its commitment and threshold", async () => {
    const other = await Z.commit(1995, 1n);
    expect(await gate.check(cd.a, cd.b, cd.c, other, cd.pub[1])).to.equal(false);
    expect(await gate.check(cd.a, cd.b, cd.c, cd.pub[0], 2000)).to.equal(false);
    await expect(gate.connect(venue).admit(ethers.id("p2"), cd.a, cd.b, cd.c, other, cd.pub[1])).to.be.revertedWithCustomError(gate, "InvalidProof");
  });

  it("no proof exists for a birth year above the threshold", async () => {
    const c = await Z.commit(2012, salt);
    let failed = false;
    try { await Z.prove({ birthYear: 2012, salt, commitment: c, maxBirthYear }); } catch { failed = true; }
    expect(failed).to.equal(true);
  });
});
