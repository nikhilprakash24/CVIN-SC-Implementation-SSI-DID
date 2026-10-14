// IDTx prototype tests (Phase 2, focus F1, start of execution). Behaviour only: no gas or latency here is
// a result (Phase 2 principle 4). The ERC-1056 registry is Phase 1's EthereumDIDRegistry, deployed from the
// Phase 1 build's artifact so the prototype runs against the unmodified contract.
//   cd 1_blockchain-identity && npx hardhat compile && npx hardhat --config hardhat.phase2.config.js test
const fs = require("fs");
const path = require("path");
// Modules come from the Phase 1 project's node_modules: phase2/ has none of its own.
const req = require("module").createRequire(path.resolve(__dirname, "../../../1_blockchain-identity/package.json"));
const { expect } = req("chai");
const { ethers, network } = req("hardhat");

const ARTIFACT = path.resolve(__dirname, "../../../1_blockchain-identity/artifacts/contracts/ERC1056/EthereumDIDRegistry.sol/EthereumDIDRegistry.json");
const OWNER = 0, DELEGATE = 1, COMMITMENT = 2;
const VERIKEY = ethers.encodeBytes32String("veriKey");
const KEY = ethers.encodeBytes32String("vin-commitment");
const ZERO32 = ethers.ZeroHash;

async function increase(seconds) {
  await network.provider.send("evm_increaseTime", [seconds]);
  await network.provider.send("evm_mine", []);
}

describe("IDTx prototype (F1)", function () {
  let registry, commitments, exec, owner, buyer, keeper, other, vehicle;

  beforeEach(async function () {
    [owner, buyer, keeper, other] = await ethers.getSigners();
    const art = JSON.parse(fs.readFileSync(ARTIFACT, "utf8"));
    registry = await new ethers.ContractFactory(art.abi, art.bytecode, owner).deploy();
    commitments = await (await ethers.getContractFactory("IdentityCommitments")).deploy(await registry.getAddress());
    exec = await (await ethers.getContractFactory("IdtxExecutor")).deploy(await registry.getAddress(), await commitments.getAddress());
    vehicle = owner.address;   // an ERC-1056 identity is an address; its initial owner is itself
  });

  const dep = (kind, fields) => ({ kind, identity: vehicle, key: ZERO32, expected: ZERO32, party: ethers.ZeroAddress, ...fields });

  describe("same-transaction IDTx", function () {
    it("Owner: executes only when the named party is the identity's current owner", async function () {
      await expect(exec.execute(dep(OWNER, { party: owner.address }), ethers.id("unlock"))).to.emit(exec, "Executed");
      await expect(exec.execute(dep(OWNER, { party: buyer.address }), ethers.id("unlock")))
        .to.be.revertedWith("identity dependency not met");
    });

    it("the caller is not part of the predicate: a third party (a keeper, an insurer) may submit the IDTx (AR-4)", async function () {
      await expect(exec.connect(other).execute(dep(OWNER, { party: owner.address }), ethers.id("insure")))
        .to.emit(exec, "Executed").withArgs(ethers.id("insure"), vehicle, OWNER, other.address);
      await expect(exec.connect(other).execute(dep(OWNER, { party: other.address }), ethers.id("insure")))
        .to.be.revertedWith("identity dependency not met");
    });

    it("Delegate: valid while the delegation lasts, not after revocation or expiry", async function () {
      const d = dep(DELEGATE, { key: VERIKEY, party: keeper.address });
      await expect(exec.execute(d, ethers.id("service"))).to.be.revertedWith("identity dependency not met");
      await registry.addDelegate(vehicle, VERIKEY, keeper.address, 3600);
      await expect(exec.execute(d, ethers.id("service"))).to.emit(exec, "Executed");
      await increase(3601);
      await expect(exec.execute(d, ethers.id("service"))).to.be.revertedWith("identity dependency not met");
      await registry.addDelegate(vehicle, VERIKEY, keeper.address, 3600);
      await registry.revokeDelegate(vehicle, VERIKEY, keeper.address);
      await expect(exec.execute(d, ethers.id("service"))).to.be.revertedWith("identity dependency not met");
    });

    it("registered-commitment validity over a plaintext: the VIN is not on chain; the registered commitment gates the action (AR-5: no proof of knowledge)", async function () {
      const salt = ethers.hexlify(ethers.randomBytes(32));
      const c = ethers.keccak256(ethers.solidityPacked(["bytes32", "string"], [salt, "1HGBH41JXMN109186"]));
      const until = (await ethers.provider.getBlock("latest")).timestamp + 3600;
      await commitments.setCommitment(vehicle, KEY, c, until);
      await expect(exec.execute(dep(COMMITMENT, { key: KEY, expected: c }), ethers.id("register"))).to.emit(exec, "Executed");
      const wrong = ethers.keccak256(ethers.solidityPacked(["bytes32", "string"], [salt, "1HGBH41JXMN109187"]));
      await expect(exec.execute(dep(COMMITMENT, { key: KEY, expected: wrong }), ethers.id("register")))
        .to.be.revertedWith("identity dependency not met");
    });

    it("registered-commitment validity over a ciphertext: an encrypted value gates an action by its registered digest, never by content", async function () {
      const ciphertext = ethers.randomBytes(48);                 // stands for AES-GCM output held off chain
      const c = ethers.keccak256(ciphertext);
      const until = (await ethers.provider.getBlock("latest")).timestamp + 60;
      await commitments.setCommitment(vehicle, KEY, c, until);
      await expect(exec.execute(dep(COMMITMENT, { key: KEY, expected: c }), ethers.id("a"))).to.emit(exec, "Executed");
      await increase(61);                                        // the commitment's own validity is chain time
      await expect(exec.execute(dep(COMMITMENT, { key: KEY, expected: c }), ethers.id("a")))
        .to.be.revertedWith("identity dependency not met");
    });

    it("a commitment stops counting when its setter no longer owns the identity (AR-6)", async function () {
      const until = (await ethers.provider.getBlock("latest")).timestamp + 3600;
      const c = ethers.id("set-by-first-owner");
      await commitments.setCommitment(vehicle, KEY, c, until);
      await expect(exec.execute(dep(COMMITMENT, { key: KEY, expected: c }), ethers.id("a"))).to.emit(exec, "Executed");
      await registry.changeOwner(vehicle, buyer.address);
      await expect(exec.execute(dep(COMMITMENT, { key: KEY, expected: c }), ethers.id("a")))
        .to.be.revertedWith("identity dependency not met");
    });

    it("only the identity's current owner can set or revoke a commitment", async function () {
      const until = (await ethers.provider.getBlock("latest")).timestamp + 3600;
      await expect(commitments.connect(other).setCommitment(vehicle, KEY, ethers.id("x"), until))
        .to.be.revertedWith("not the identity owner");
      await registry.changeOwner(vehicle, buyer.address);
      await expect(commitments.setCommitment(vehicle, KEY, ethers.id("x"), until)).to.be.revertedWith("not the identity owner");
      await expect(commitments.connect(buyer).setCommitment(vehicle, KEY, ethers.id("x"), until)).to.emit(commitments, "CommitmentSet");
    });
  });

  describe("next-transaction IDTx (an agent fulfils later)", function () {
    it("fulfils when the dependency still holds at fulfilment", async function () {
      const deadline = (await ethers.provider.getBlock("latest")).timestamp + 600;
      await exec.createIntent(dep(OWNER, { party: owner.address }), ethers.id("insure"), deadline);
      await expect(exec.connect(keeper).fulfil(0)).to.emit(exec, "IntentFulfilled").withArgs(0, keeper.address);
      await expect(exec.connect(keeper).fulfil(0)).to.be.revertedWith("already fulfilled");
    });

    it("an ownership transfer between intent and fulfilment makes fulfilment fail (no TOCTOU on chain)", async function () {
      const deadline = (await ethers.provider.getBlock("latest")).timestamp + 600;
      await exec.createIntent(dep(OWNER, { party: owner.address }), ethers.id("insure"), deadline);
      await registry.changeOwner(vehicle, buyer.address);
      await expect(exec.connect(keeper).fulfil(0)).to.be.revertedWith("identity dependency not met");
    });

    it("a revoked commitment between intent and fulfilment makes fulfilment fail", async function () {
      const now = (await ethers.provider.getBlock("latest")).timestamp;
      const c = ethers.id("commit");
      await commitments.setCommitment(vehicle, KEY, c, now + 3600);
      await exec.createIntent(dep(COMMITMENT, { key: KEY, expected: c }), ethers.id("x"), now + 600);
      await commitments.revokeCommitment(vehicle, KEY);
      await expect(exec.connect(keeper).fulfil(0)).to.be.revertedWith("identity dependency not met");
    });

    it("an expired intent cannot be fulfilled", async function () {
      const deadline = (await ethers.provider.getBlock("latest")).timestamp + 60;
      await exec.createIntent(dep(OWNER, { party: owner.address }), ethers.id("x"), deadline);
      await increase(61);
      await expect(exec.connect(keeper).fulfil(0)).to.be.revertedWith("deadline passed");
    });
  });

  describe("what the storage choice allows (the F1 link)", function () {
    it("ERC-1056 exposes no function that returns an attribute value: a contract cannot read its attributes directly (only through a proof the transaction carries, AR-1)", async function () {
      const readers = registry.interface.fragments.filter((f) => f.type === "function" && /attribute/i.test(f.name) &&
        f.stateMutability === "view" && f.outputs.length > 0);
      expect(readers.map((f) => f.name)).to.deep.equal([]);
      // owner and delegates are in state, so they can be dependencies
      expect(registry.interface.getFunction("identityOwner").stateMutability).to.equal("view");
      expect(registry.interface.getFunction("validDelegate").stateMutability).to.equal("view");
    });
  });
});
