// Layer 5 contract tests: the Groth16 ZK-VIN verifier, the ZkVinGate IDTx, and the Schnorr ecrecover verifier.
// The ERC-1056 registry is Phase 1's EthereumDIDRegistry, deployed from the Phase 1 build's artifact, unmodified.
//   cd 1_blockchain-identity && npx hardhat compile && npx hardhat --config hardhat.zkp.config.js test
const fs = require("fs");
const path = require("path");
const req = require("module").createRequire(path.resolve(__dirname, "../../1_blockchain-identity/package.json"));
const { expect } = req("chai");
const { ethers } = req("hardhat");

const ARTIFACT = path.resolve(__dirname, "../../1_blockchain-identity/artifacts/contracts/ERC1056/EthereumDIDRegistry.sol/EthereumDIDRegistry.json");
const FIX = JSON.parse(fs.readFileSync(path.resolve(__dirname, "../fixtures/zkvin_proof.json"), "utf8"));
const SCH = JSON.parse(fs.readFileSync(path.resolve(__dirname, "../fixtures/schnorr_evm.json"), "utf8")).proof;
const INSURER = ethers.id("insurer:acme"), TOLL = ethers.id("toll:A");
const ACTION = ethers.id("issue-policy-quote");

async function deployAll() {
  const [owner, agent, stranger] = await ethers.getSigners();
  const art = JSON.parse(fs.readFileSync(ARTIFACT, "utf8"));
  const registry = await new ethers.ContractFactory(art.abi, art.bytecode, owner).deploy();
  const verifier = await (await ethers.getContractFactory("Groth16Verifier")).deploy();
  const gate = await (await ethers.getContractFactory("ZkVinGate")).deploy(
    await registry.getAddress(), await verifier.getAddress(), FIX.mfrRoot);
  const vehicle = owner.address; // an ERC-1056 identity is an address, initially its own owner
  await gate.connect(owner).anchorCommitment(vehicle, FIX.vehicle.commitment);
  await gate.setService(INSURER, FIX.request.scope, FIX.request.minModelYear, FIX.vehicle.region, FIX.request.challenge);
  await gate.setService(TOLL, FIX.toll.scope, FIX.request.minModelYear, FIX.vehicle.region, FIX.request.challenge);
  return { owner, agent, stranger, registry, verifier, gate, vehicle };
}
const P = FIX.insurer;

describe("ZK-VIN on chain (layer 5)", function () {
  it("the generated verifier accepts the fixture proof and rejects a tampered one", async function () {
    const { verifier } = await deployAll();
    expect(await verifier.verifyProof(P.a, P.b, P.c, P.pub)).to.equal(true);
    const badC = [P.c[0], (BigInt(P.c[1]) + 1n).toString()];
    expect(await verifier.verifyProof(P.a, P.b, badC, P.pub)).to.equal(false);
    const badPub = [...P.pub]; badPub[3] = "2019";
    expect(await verifier.verifyProof(P.a, P.b, P.c, badPub)).to.equal(false);
  });

  it("admits a valid proof submitted by anyone (here the owner's agent), once per scope", async function () {
    const { gate, agent, vehicle } = await deployAll();
    await expect(gate.connect(agent).admit(vehicle, INSURER, P.a, P.b, P.c, P.pub, ACTION))
      .to.emit(gate, "Admitted").withArgs(vehicle, INSURER, P.pub[0], ACTION);
    await expect(gate.connect(agent).admit(vehicle, INSURER, P.a, P.b, P.c, P.pub, ACTION))
      .to.be.revertedWithCustomError(gate, "NullifierUsed");
  });

  it("the same vehicle has a different, unlinkable nullifier in another scope", async function () {
    const { gate, vehicle } = await deployAll();
    const T = FIX.toll;
    expect(T.pub[0]).to.not.equal(P.pub[0]);
    await expect(gate.admit(vehicle, TOLL, T.a, T.b, T.c, T.pub, ACTION)).to.emit(gate, "Admitted");
    await expect(gate.admit(vehicle, INSURER, P.a, P.b, P.c, P.pub, ACTION)).to.emit(gate, "Admitted");
  });

  it("a proof made for one service cannot be used at another (scope bound)", async function () {
    const { gate, vehicle } = await deployAll();
    await expect(gate.admit(vehicle, TOLL, P.a, P.b, P.c, P.pub, ACTION))
      .to.be.revertedWithCustomError(gate, "SignalMismatch").withArgs(5);
  });

  it("rejects a proof against another identity's commitment, a changed root, threshold or challenge", async function () {
    const { gate, stranger, vehicle } = await deployAll();
    await expect(gate.admit(stranger.address, INSURER, P.a, P.b, P.c, P.pub, ACTION))
      .to.be.revertedWithCustomError(gate, "SignalMismatch").withArgs(1);
    const s = (i, v) => { const p = [...P.pub]; p[i] = v; return p; };
    await expect(gate.admit(vehicle, INSURER, P.a, P.b, P.c, s(2, "1"), ACTION)).to.be.revertedWithCustomError(gate, "SignalMismatch").withArgs(2);
    await expect(gate.admit(vehicle, INSURER, P.a, P.b, P.c, s(3, "2019"), ACTION)).to.be.revertedWithCustomError(gate, "SignalMismatch").withArgs(3);
    await gate.setService(INSURER, FIX.request.scope, FIX.request.minModelYear, FIX.vehicle.region, 12345);
    await expect(gate.admit(vehicle, INSURER, P.a, P.b, P.c, P.pub, ACTION)).to.be.revertedWithCustomError(gate, "SignalMismatch").withArgs(6);
  });

  it("rejects a tampered proof whose signals all match", async function () {
    const { gate, vehicle } = await deployAll();
    const badA = [P.a[0], (BigInt(P.a[1]) + 1n).toString()];
    await expect(gate.admit(vehicle, INSURER, badA, P.b, P.c, P.pub, ACTION)).to.be.reverted;
  });

  it("only the identity's ERC-1056 owner anchors; after an ownership transfer the old owner cannot", async function () {
    const { gate, registry, owner, stranger, vehicle } = await deployAll();
    await expect(gate.connect(stranger).anchorCommitment(vehicle, 1)).to.be.revertedWithCustomError(gate, "NotIdentityOwner");
    await registry.connect(owner).changeOwner(vehicle, stranger.address);
    await expect(gate.connect(owner).anchorCommitment(vehicle, 1)).to.be.revertedWithCustomError(gate, "NotIdentityOwner");
    await expect(gate.connect(stranger).anchorCommitment(vehicle, 1)).to.emit(gate, "CommitmentAnchored");
  });

  it("Schnorr proof of key knowledge verifies on chain through ecrecover; tampering fails", async function () {
    const v = await (await ethers.getContractFactory("SchnorrEcrecoverVerifier")).deploy();
    expect(await v.verify(SCH.parity, SCH.px, SCH.message, SCH.e, SCH.s)).to.equal(true);
    expect(await v.verify(SCH.parity, SCH.px, ethers.id("other"), SCH.e, SCH.s)).to.equal(false);
    const s2 = ethers.toBeHex((BigInt(SCH.s) + 1n), 32);
    expect(await v.verify(SCH.parity, SCH.px, SCH.message, SCH.e, s2)).to.equal(false);
    expect(await v.verify(1 - SCH.parity, SCH.px, SCH.message, SCH.e, SCH.s)).to.equal(false);
  });
});
