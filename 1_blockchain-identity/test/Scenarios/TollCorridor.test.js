const { expect } = require("chai");
const { ethers } = require("hardhat");
const { time } = require("@nomicfoundation/hardhat-network-helpers");

// Scenario X1: endorsed passage (read) + paid toll (write), docs/research-expansion/IDEAS.md §X1.
// Composes ERC-1056 (owner / veriKey delegate), EIP-712 issuer endorsements,
// EIP-712 vehicle tickets, an EIP-2612-funded stablecoin escrow and gantry batching.

const VERIKEY = ethers.encodeBytes32String("veriKey");
const CLASS = { EMERGENCY: 0, CAR: 1, EV: 2, TRUCK: 3 };
const FEE = { [CLASS.EMERGENCY]: 0n, [CLASS.CAR]: 2_500_000n, [CLASS.EV]: 1_250_000n, [CLASS.TRUCK]: 9_000_000n };
const CODE = {
  OK: 0, GANTRY: 1, EXPIRED_TICKET: 2, NONCE_USED: 3, ENDORSEMENT_MISMATCH: 4, UNTRUSTED_ISSUER: 5,
  ENDORSEMENT_EXPIRED: 6, ENDORSEMENT_REVOKED: 7, SUBJECT_MISMATCH: 8, UNKNOWN_CLASS: 9,
  BAD_VEHICLE_SIGNER: 10, FEE_ABOVE_MAX: 11, INSUFFICIENT_ESCROW: 12,
};

const ENDORSEMENT_TYPES = {
  Endorsement: [
    { name: "subject", type: "address" },
    { name: "vehicleClass", type: "uint8" },
    { name: "validUntil", type: "uint64" },
    { name: "credentialHash", type: "bytes32" },
  ],
};
const TICKET_TYPES = {
  TollTicket: [
    { name: "identity", type: "address" },
    { name: "gantry", type: "address" },
    { name: "nonce", type: "uint64" },
    { name: "maxFee", type: "uint128" },
    { name: "deadline", type: "uint64" },
    { name: "endorsementHash", type: "bytes32" },
  ],
};

describe("X1 toll corridor: endorsed DID passage + stablecoin toll", function () {
  let authority, ministry, rogueIssuer, gantry, gantry2, vehicle, vehicle2, pseudonym, relayer, newOwner;
  let registry, stable, corridor, domain;

  async function deployAll() {
    [authority, ministry, rogueIssuer, gantry, gantry2, vehicle, vehicle2, pseudonym, relayer, newOwner] =
      await ethers.getSigners();
    registry = await (await ethers.getContractFactory("EthereumDIDRegistry")).deploy();
    stable = await (await ethers.getContractFactory("CVINTestStable")).deploy();
    corridor = await (await ethers.getContractFactory("CVINTollCorridor"))
      .deploy(await stable.getAddress(), await registry.getAddress());
    const { chainId } = await ethers.provider.getNetwork();
    domain = { name: "CVINTollCorridor", version: "1", chainId, verifyingContract: await corridor.getAddress() };

    await corridor.setIssuer(ministry.address, true);
    await corridor.setGantry(gantry.address, true);
    await corridor.setGantry(gantry2.address, true);
    for (const [c, f] of Object.entries(FEE)) await corridor.setFee(Number(c), f);
    for (const v of [vehicle, vehicle2]) {
      await stable.mint(v.address, 100_000_000n);
      await stable.connect(v).approve(await corridor.getAddress(), ethers.MaxUint256);
      await corridor.connect(v).deposit(v.address, 50_000_000n);
    }
  }

  async function endorse(subject, vehicleClass, { signer = ministry, ttl = 86400, credentialHash } = {}) {
    const e = {
      subject,
      vehicleClass,
      validUntil: BigInt((await time.latest()) + ttl),
      credentialHash: credentialHash ?? ethers.keccak256(ethers.toUtf8Bytes(`vc:${subject}:${vehicleClass}`)),
    };
    const sig = await signer.signTypedData(domain, ENDORSEMENT_TYPES, e);
    return { e, sig, eh: ethers.TypedDataEncoder.hash(domain, ENDORSEMENT_TYPES, e) };
  }

  let nonceCounter = 1n;
  async function ticket(identity, endo, { signer, g = gantry, maxFee = 10_000_000n, ttl = 60, nonce } = {}) {
    const t = {
      identity,
      gantry: g.address,
      nonce: nonce ?? nonceCounter++,
      maxFee,
      deadline: BigInt((await time.latest()) + ttl),
      endorsementHash: endo.eh,
    };
    const sig = await signer.signTypedData(domain, TICKET_TYPES, t);
    return { t, sig };
  }

  const check = (endo, tk, g = gantry) => corridor.checkTicket(endo.e, endo.sig, tk.t, tk.sig, g.address);

  beforeEach(deployAll);

  describe("happy paths", function () {
    it("owner-signed ticket: read says OK, write debits the class fee and emits no PII", async function () {
      const endo = await endorse(vehicle.address, CLASS.CAR);
      const tk = await ticket(vehicle.address, endo, { signer: vehicle });
      const [code, fee] = await check(endo, tk);
      expect(code).to.equal(CODE.OK);
      expect(fee).to.equal(FEE[CLASS.CAR]);

      await expect(corridor.connect(gantry).payToll(endo.e, endo.sig, tk.t, tk.sig))
        .to.emit(corridor, "TollPaid")
        .withArgs(vehicle.address, gantry.address, CLASS.CAR, FEE[CLASS.CAR], await corridor.hashTicket(tk.t));
      expect(await corridor.escrowOf(vehicle.address)).to.equal(50_000_000n - FEE[CLASS.CAR]);
      expect(await corridor.treasury()).to.equal(FEE[CLASS.CAR]);
    });

    it("pseudonym path: a live ERC-1056 veriKey delegate pays for the DID (register #38 tie-in)", async function () {
      await registry.connect(vehicle).addDelegate(vehicle.address, VERIKEY, pseudonym.address, 300);
      const endo = await endorse(vehicle.address, CLASS.EV);
      const tk = await ticket(vehicle.address, endo, { signer: pseudonym });
      await corridor.connect(gantry).payToll(endo.e, endo.sig, tk.t, tk.sig);
      expect(await corridor.escrowOf(vehicle.address)).to.equal(50_000_000n - FEE[CLASS.EV]);
    });

    it("emergency class is endorsed at fee 0 and passes without escrow", async function () {
      await corridor.connect(vehicle2).withdraw(vehicle2.address, 50_000_000n, vehicle2.address);
      const endo = await endorse(vehicle2.address, CLASS.EMERGENCY);
      const tk = await ticket(vehicle2.address, endo, { signer: vehicle2 });
      expect((await check(endo, tk))[0]).to.equal(CODE.OK);
      await corridor.connect(gantry).payToll(endo.e, endo.sig, tk.t, tk.sig);
    });

    it("gasless top-up: a relayer submits the vehicle's EIP-2612 permit", async function () {
      const v = vehicle2;
      const value = 7_000_000n;
      const deadline = BigInt((await time.latest()) + 600);
      const nonce = await stable.nonces(v.address);
      const permitDomain = {
        name: "CVIN Test Stable", version: "1",
        chainId: domain.chainId, verifyingContract: await stable.getAddress(),
      };
      const sig = ethers.Signature.from(await v.signTypedData(permitDomain, {
        Permit: [
          { name: "owner", type: "address" }, { name: "spender", type: "address" },
          { name: "value", type: "uint256" }, { name: "nonce", type: "uint256" },
          { name: "deadline", type: "uint256" },
        ],
      }, { owner: v.address, spender: await corridor.getAddress(), value, nonce, deadline }));
      await stable.connect(v).approve(await corridor.getAddress(), 0);
      const before = await corridor.escrowOf(v.address);
      await corridor.connect(relayer).depositWithPermit(v.address, v.address, value, deadline, sig.v, sig.r, sig.s);
      expect(await corridor.escrowOf(v.address)).to.equal(before + value);
    });

    it("batch settlement across vehicles from one gantry", async function () {
      const e1 = await endorse(vehicle.address, CLASS.CAR);
      const e2 = await endorse(vehicle2.address, CLASS.TRUCK);
      const t1 = await ticket(vehicle.address, e1, { signer: vehicle });
      const t2 = await ticket(vehicle2.address, e2, { signer: vehicle2 });
      await corridor.connect(gantry).settleBatch([e1.e, e2.e], [e1.sig, e2.sig], [t1.t, t2.t], [t1.sig, t2.sig]);
      expect(await corridor.treasury()).to.equal(FEE[CLASS.CAR] + FEE[CLASS.TRUCK]);
    });
  });

  describe("attacks (each rejected with its reason code; read and write agree)", function () {
    async function expectRejected(endo, tk, code, g = gantry) {
      expect((await check(endo, tk, g))[0]).to.equal(code);
      await expect(corridor.connect(g).payToll(endo.e, endo.sig, tk.t, tk.sig))
        .to.be.revertedWithCustomError(corridor, "TicketRejected").withArgs(code);
    }

    it("replay of a settled ticket", async function () {
      const endo = await endorse(vehicle.address, CLASS.CAR);
      const tk = await ticket(vehicle.address, endo, { signer: vehicle });
      await corridor.connect(gantry).payToll(endo.e, endo.sig, tk.t, tk.sig);
      await expectRejected(endo, tk, CODE.NONCE_USED);
    });

    it("ticket bound to gantry A submitted by gantry B, and by a non-gantry", async function () {
      const endo = await endorse(vehicle.address, CLASS.CAR);
      const tk = await ticket(vehicle.address, endo, { signer: vehicle });
      await expectRejected(endo, tk, CODE.GANTRY, gantry2);
      await expectRejected(endo, tk, CODE.GANTRY, relayer);
    });

    it("self-endorsement by an untrusted issuer (e.g. to claim the emergency class)", async function () {
      const endo = await endorse(vehicle.address, CLASS.EMERGENCY, { signer: rogueIssuer });
      const tk = await ticket(vehicle.address, endo, { signer: vehicle });
      await expectRejected(endo, tk, CODE.UNTRUSTED_ISSUER);
    });

    it("class downgrade: edited vehicleClass breaks the issuer signature binding", async function () {
      const endo = await endorse(vehicle.address, CLASS.TRUCK);
      const forged = { ...endo, e: { ...endo.e, vehicleClass: CLASS.EV } };
      forged.eh = ethers.TypedDataEncoder.hash(domain, ENDORSEMENT_TYPES, forged.e);
      const tk = await ticket(vehicle.address, forged, { signer: vehicle });
      await expectRejected(forged, tk, CODE.UNTRUSTED_ISSUER);
    });

    it("stolen endorsement: another vehicle presents vehicle 1's endorsement", async function () {
      const endo = await endorse(vehicle.address, CLASS.EMERGENCY);
      const tk = await ticket(vehicle2.address, endo, { signer: vehicle2 });
      await expectRejected(endo, tk, CODE.SUBJECT_MISMATCH);
    });

    it("thief signs for a DID it does not control", async function () {
      const endo = await endorse(vehicle.address, CLASS.CAR);
      const tk = await ticket(vehicle.address, endo, { signer: vehicle2 });
      await expectRejected(endo, tk, CODE.BAD_VEHICLE_SIGNER);
    });

    it("revoked endorsement (issuer self-revokes; one-bit status list)", async function () {
      const endo = await endorse(vehicle.address, CLASS.CAR);
      await corridor.connect(ministry).revokeEndorsement(endo.e, endo.sig);
      const tk = await ticket(vehicle.address, endo, { signer: vehicle });
      await expectRejected(endo, tk, CODE.ENDORSEMENT_REVOKED);
    });

    it("a non-issuer cannot revoke someone's endorsement", async function () {
      const endo = await endorse(vehicle.address, CLASS.CAR);
      await expect(corridor.connect(vehicle2).revokeEndorsement(endo.e, endo.sig))
        .to.be.revertedWithCustomError(corridor, "NotAuthority");
    });

    it("expired endorsement and expired ticket", async function () {
      const endo = await endorse(vehicle.address, CLASS.CAR, { ttl: 100 });
      const tk = await ticket(vehicle.address, endo, { signer: vehicle, ttl: 1000 });
      await time.increase(200);
      await expectRejected(endo, tk, CODE.ENDORSEMENT_EXPIRED);
      const endo2 = await endorse(vehicle.address, CLASS.CAR);
      const tk2 = await ticket(vehicle.address, endo2, { signer: vehicle, ttl: 10 });
      await time.increase(20);
      await expectRejected(endo2, tk2, CODE.EXPIRED_TICKET);
    });

    it("price above the vehicle's cap, and an empty escrow", async function () {
      const endo = await endorse(vehicle.address, CLASS.TRUCK);
      const tk = await ticket(vehicle.address, endo, { signer: vehicle, maxFee: 1n });
      await expectRejected(endo, tk, CODE.FEE_ABOVE_MAX);
      await corridor.connect(vehicle).withdraw(vehicle.address, 50_000_000n, vehicle.address);
      const tk2 = await ticket(vehicle.address, endo, { signer: vehicle });
      await expectRejected(endo, tk2, CODE.INSUFFICIENT_ESCROW);
    });

    it("pseudonym after its epoch ends, and the old owner after a DID ownership change", async function () {
      await registry.connect(vehicle).addDelegate(vehicle.address, VERIKEY, pseudonym.address, 300);
      const endo = await endorse(vehicle.address, CLASS.CAR, { ttl: 86400 });
      await time.increase(301);
      const tk = await ticket(vehicle.address, endo, { signer: pseudonym });
      await expectRejected(endo, tk, CODE.BAD_VEHICLE_SIGNER);

      await registry.connect(vehicle).changeOwner(vehicle.address, newOwner.address);
      const tk2 = await ticket(vehicle.address, endo, { signer: vehicle });
      await expectRejected(endo, tk2, CODE.BAD_VEHICLE_SIGNER);
      const tk3 = await ticket(vehicle.address, endo, { signer: newOwner });
      expect((await check(endo, tk3))[0]).to.equal(CODE.OK);
    });

    it("only the DID's current owner can withdraw the escrow", async function () {
      await expect(corridor.connect(vehicle2).withdraw(vehicle.address, 1n, vehicle2.address))
        .to.be.revertedWithCustomError(corridor, "NotIdentityOwner");
    });

    it("endorsement digest swapped inside a ticket", async function () {
      const endo = await endorse(vehicle.address, CLASS.CAR);
      const other = await endorse(vehicle.address, CLASS.EV);
      const tk = await ticket(vehicle.address, other, { signer: vehicle });
      await expectRejected(endo, tk, CODE.ENDORSEMENT_MISMATCH);
    });

    it("a batch with one bad ticket settles nothing", async function () {
      const e1 = await endorse(vehicle.address, CLASS.CAR);
      const t1 = await ticket(vehicle.address, e1, { signer: vehicle });
      const t2 = await ticket(vehicle.address, e1, { signer: vehicle2 });
      await expect(corridor.connect(gantry).settleBatch([e1.e, e1.e], [e1.sig, e1.sig], [t1.t, t2.t], [t1.sig, t2.sig]))
        .to.be.revertedWithCustomError(corridor, "TicketRejected").withArgs(CODE.BAD_VEHICLE_SIGNER);
      expect(await corridor.treasury()).to.equal(0n);
    });
  });

  describe("gas profile (recorded, not pinned: no register row yet)", function () {
    it("single payToll and per-ticket cost in batches of 1, 10, 25", async function () {
      const rows = [];
      // Vehicles only sign typed data, so off-chain wallets suffice; the authority funds their escrow.
      const fleet = Array.from({ length: 25 }, () => ethers.Wallet.createRandom());
      await stable.mint(authority.address, 25n * 50_000_000n);
      await stable.approve(await corridor.getAddress(), ethers.MaxUint256);
      for (const v of fleet) await corridor.deposit(v.address, 50_000_000n);
      for (const n of [1, 10, 25]) {
        const es = [], is = [], ts = [], vs = [];
        for (const v of fleet.slice(0, n)) {
          const endo = await endorse(v.address, CLASS.CAR);
          const tk = await ticket(v.address, endo, { signer: v });
          es.push(endo.e); is.push(endo.sig); ts.push(tk.t); vs.push(tk.sig);
        }
        const rc = await (await corridor.connect(gantry).settleBatch(es, is, ts, vs)).wait();
        rows.push({ batch: n, gas: Number(rc.gasUsed), perTicket: Math.round(Number(rc.gasUsed) / n) });
      }
      // eslint-disable-next-line no-console
      console.log("      X1 settleBatch gas:", JSON.stringify(rows));
      expect(new Set(fleet.map((v) => v.address)).size).to.equal(25);
      expect(rows[2].gas).to.be.greaterThan(rows[1].gas);
      expect(rows[2].perTicket).to.be.lessThan(rows[0].perTicket);
    });
  });
});
