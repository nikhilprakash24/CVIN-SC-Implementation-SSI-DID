/**
 * M5 pseudonym pool on the standard EthereumDIDRegistry (PLAN_MOBI_SUMO §A.2;
 * scripts/experiment_pseudonym_pool.js). Pins the gas per rotation epoch and
 * demonstrates the linking query: one eth_getLogs (DIDDelegateChanged,
 * topic1 = identity) returns every pseudonym of the delegate pool, while the
 * same query on per-pseudonym identities links nothing.
 */
const { expect } = require("chai");
const { ethers } = require("hardhat");
const M5 = require("../../scripts/experiment_pseudonym_pool.js");

describe("M5 pseudonym pool (EthereumDIDRegistry)", function () {
  this.timeout(120000);

  let reg, vehicle, relayer, pool;

  before(async function () {
    [, vehicle, relayer] = await ethers.getSigners();
    ({ reg } = await M5.deployRegistry());
    // tag "A" = the experiment's pseudonym addresses, so the calldata (EIP-2028 zero bytes) and gas match it exactly
    pool = await M5.runDelegatePool(reg, vehicle, { epochs: 3, tag: "A" });
  });

  it("pins addDelegate gas: 71,919 for the identity's first change, then 54,807-54,819", async function () {
    const g = pool.epochs.map((e) => e.gas_per_add_delegate);
    expect(g[0][0]).to.equal(71919);
    for (const [e, epoch] of g.entries()) {
      for (const [i, x] of epoch.entries()) {
        if (e === 0 && i === 0) continue;
        expect([54807, 54819]).to.include(x);
      }
    }
  });

  it("pins gas per rotation epoch (20 delegates): 1,113,456 then 1,096,368", async function () {
    expect(pool.epochs.map((e) => e.epoch_gas)).to.deep.equal([1113456, 1096368, 1096368]);
    // pre-registered ≈1.44 M (20 × 72,219) is outside ±10 % of what is measured
    expect(pool.epochs[1].epoch_gas / M5.PREREG_EPOCH_GAS).to.be.lessThan(0.9);
  });

  it("rotates: each epoch's 20 delegates are valid during it and expired after evm_increaseTime(300)", async function () {
    expect(pool.epochs.every((e) => e.all_current_valid)).to.equal(true);
    expect(pool.epochs.slice(1).every((e) => e.previous_epoch_expired === true)).to.equal(true);
    expect(pool.last_epoch_expired_after_rotation).to.equal(true);
  });

  it("links: one identity-topic getLogs returns all 20 pseudonyms of every epoch", async function () {
    const logs = await M5.delegateLogsByIdentity(reg, vehicle.address);
    const returned = new Set(logs.map((l) => l.args.delegate));
    expect(logs.length).to.equal(60);
    for (const ep of pool.epochs) {
      expect(ep.pseudonyms.filter((p) => returned.has(p)).length).to.equal(20);
    }
  });

  it("links from ONE pseudonym: delegate -> identity -> all siblings", async function () {
    const one = pool.epochs[2].pseudonyms[13];
    const ids = await M5.identityOfDelegate(reg, one);
    expect(ids).to.deep.equal([vehicle.address]);
    const link = await M5.linkabilityDelegatePool(reg, vehicle, pool);
    expect(link.linkable).to.equal(true);
    expect(link.reverse_link_from_one_pseudonym.siblings_reached).to.equal(60);
  });

  it("per-pseudonym identities (no attributes): 0 gas, and the same query links nothing", async function () {
    const { reg: r2 } = await M5.deployRegistry();
    const res = await M5.runPerPseudonym(r2, vehicle, relayer, "B0", { epochs: 1, tag: "test-b0" });
    expect(res.epochs[0].epoch_gas).to.equal(0);
    expect(res.epochs[0].implicit_owner_is_self).to.equal(true);
    const link = await M5.linkabilityPerPseudonym(r2, vehicle, relayer, res);
    expect(link.linkable_by_identity_query).to.equal(false);
    expect(link.tx_layer_scan.txs_touching_pseudonyms).to.equal(0);
  });

  it("per-pseudonym identities with a relayed attribute: unlinkable by the query, linked only to the relayer", async function () {
    const { reg: r3 } = await M5.deployRegistry();
    const res = await M5.runPerPseudonym(r3, vehicle, relayer, "B2", { epochs: 1, tag: "test-b2" });
    for (const p of res.epochs[0].pseudonyms) {
      expect((await M5.delegateLogsByIdentity(r3, p)).length).to.equal(0);
    }
    const link = await M5.linkabilityPerPseudonym(r3, vehicle, relayer, res);
    expect(link.linkable_by_identity_query).to.equal(false);
    expect(link.max_other_pseudonyms_reached_by_one_query).to.equal(0);
    expect(link.registry_tx_senders_other_than_pseudonym).to.deep.equal([relayer.address]);
    expect(link.registry_tx_sender_is_vehicle).to.equal(false);
  });

  it("per-pseudonym identities funded by the vehicle: the funding transfers link them", async function () {
    const { reg: r4 } = await M5.deployRegistry();
    const res = await M5.runPerPseudonym(r4, vehicle, relayer, "B1", { epochs: 1, tag: "test-b1" });
    const link = await M5.linkabilityPerPseudonym(r4, vehicle, relayer, res);
    expect(link.linkable_by_identity_query).to.equal(false);
    expect(link.tx_layer_scan.funders[vehicle.address]).to.equal(20);
  });
});
