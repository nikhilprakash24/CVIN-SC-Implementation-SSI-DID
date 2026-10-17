// SetCHarness — a harness for C1–C4, NOT option O7.
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("SetCHarness (C1–C4 harness, endorsement-gated attesters)", function () {
  let ssi, adapter, reg, harness, open, admin, ministryS, aggS, xS, ministry, agg, x;
  const YEAR = 365 * 24 * 3600;
  const mk = async (s) => (await (await ssi.connect(s).createDID(s.address)).wait()).logs
    .map(l => { try { return ssi.interface.parseLog(l); } catch { return null; } }).find(e => e && e.name === "DIDCreated").args.did;

  beforeEach(async () => {
    [admin, ministryS, aggS, xS] = await ethers.getSigners();
    ssi = await (await ethers.getContractFactory("O1_ERC1056")).deploy();
    adapter = await (await ethers.getContractFactory("O1ControllerAdapter")).deploy(await ssi.getAddress());
    reg = await (await ethers.getContractFactory("EndorsementRegistry")).connect(admin).deploy(await ssi.getAddress(), await adapter.getAddress());
    harness = await (await ethers.getContractFactory("SetCHarness")).deploy(await adapter.getAddress(), await reg.getAddress(), true);
    open = await (await ethers.getContractFactory("SetCHarness")).deploy(await adapter.getAddress(), await reg.getAddress(), false);
    ministry = await mk(ministryS); agg = await mk(aggS); x = await mk(xS);
    await reg.addRoot(ministry);
  });

  it("gated: unendorsed attester cannot score; endorsed one can; one score per (subject, attester)", async () => {
    await expect(harness.connect(aggS).attestReputationAs(agg, x, 90, "u")).to.be.revertedWithCustomError(harness, "NotEntitled");
    await reg.connect(aggS).registerIssuer(agg, ethers.id("r"));
    await reg.connect(ministryS).endorseIssuer(ministry, agg, await harness.REPUTATION_ATTESTER(), YEAR, false);
    await expect(harness.connect(aggS).attestReputationAs(agg, x, 90, "u")).to.emit(harness, "ReputationAttested");
    await harness.connect(aggS).attestReputationAs(agg, x, 10, "u2"); // ignored for the mean (already scored)
    const [mean, count] = await harness.getReputation(x);
    expect(mean).to.equal(90); expect(count).to.equal(1);
    await expect(harness.connect(xS).attestReputationAs(agg, x, 1, "u")).to.be.revertedWithCustomError(harness, "NotAuthorized"); // not agg's controller
    await expect(harness.connect(aggS).attestReputation(x, 5, "u")).to.be.revertedWithCustomError(harness, "NotEntitled"); // plain C1 unusable when gated
  });

  it("ungated: plain C1 works from any address (the Sybil control)", async () => {
    await open.connect(xS).attestReputation(x, 100, "self");
    const [mean, count] = await open.getReputation(x);
    expect(mean).to.equal(100); expect(count).to.equal(1);
    const [m0, c0] = await open.getReputation(ethers.id("nobody"));
    expect(m0).to.equal(0); expect(c0).to.equal(0);
  });

  it("validation: request → pending; only endorsed validator resolves; status readable; unknown = 0", async () => {
    const rc = await (await harness.connect(xS).requestValidation(x, ethers.id("zkml"), "0x1234")).wait();
    const id = rc.logs.map(l => { try { return harness.interface.parseLog(l); } catch { return null; } }).find(e => e && e.name === "ValidationRequested").args.requestId;
    expect(await harness.validationStatus(id)).to.equal(1);
    await expect(harness.connect(aggS).resolveValidationAs(agg, id, true)).to.be.revertedWithCustomError(harness, "NotEntitled");
    await reg.connect(aggS).registerIssuer(agg, ethers.id("r"));
    await reg.connect(ministryS).endorseIssuer(ministry, agg, await harness.REPUTATION_ATTESTER(), YEAR, false);
    await expect(harness.connect(aggS).resolveValidationAs(agg, id, true)).to.emit(harness, "ValidationResolved");
    expect(await harness.validationStatus(id)).to.equal(2);
    await expect(harness.connect(aggS).resolveValidationAs(agg, id, false)).to.be.revertedWithCustomError(harness, "NotAuthorized"); // already resolved
    expect(await harness.validationStatus(ethers.id("none"))).to.equal(0);
  });
});
