const { expect } = require("chai");
const hre = require("hardhat");
const { ADAPTERS } = require("../../benchmarks/adapters");
const { makeActors } = require("../../benchmarks/lib/actors");
const { makeDataset, PAYLOADS } = require("../../benchmarks/lib/dataset");

// Gate for entering the comparative study (framework §5): every core catalogue
// op must execute on the substrate and leave the identity in the expected state.
describe("Benchmark adapter conformance", function () {
  const dataset = makeDataset(20, 42);

  for (const [id, Adapter] of Object.entries(ADAPTERS)) {
    describe(id, function () {
      let adapter, actors, h, key;
      const wait = async (r) => { for (const t of r.txs) await t.wait(); return r; };

      before(async function () {
        await hre.network.provider.send("hardhat_reset");
        actors = makeActors(hre.ethers);
        adapter = new Adapter({ ethers: hre.ethers, actors, dataset, payloads: PAYLOADS });
        const deployed = await adapter.deploy();
        expect(deployed.length).to.be.greaterThan(0);
      });

      it("C1/C2 create identity", async function () {
        const r1 = await wait(await adapter.createIdentity(dataset[0], actors.vehicleOwner));
        expect(r1.txs.length).to.be.greaterThan(0);
        const r2 = await wait(await adapter.createIdentityWithAttributes(dataset[1], actors.vehicleOwner));
        h = r2.result;
        expect(await adapter.resolveOwner(h)).to.equal(actors.vehicleOwner.address);
      });

      it("R2 resolve by VIN (or declared n/a)", async function () {
        if (!adapter.supports("R2_resolve_by_vin")) return this.skip();
        const v = await adapter.resolveByVin(dataset[1].vin);
        expect(v).to.not.equal(hre.ethers.ZeroAddress);
      });

      it("U2/R4/D1 delegate lifecycle", async function () {
        key = hre.ethers.Wallet.createRandom();
        expect(await adapter.verifyDelegate(h, key)).to.equal(false);
        await wait(await adapter.addDelegate(h, key, PAYLOADS.ttlSeconds));
        expect(await adapter.verifyDelegate(h, key)).to.equal(true);
        await wait(await adapter.revokeDelegate(h, key));
        expect(await adapter.verifyDelegate(h, key)).to.equal(false);
      });

      it("U3/R3 attribute appears in resolved document", async function () {
        await wait(await adapter.setAttribute(h, PAYLOADS.attributeName, PAYLOADS.attributeValue));
        const doc = await adapter.resolveDocument(h);
        expect(doc.id).to.be.a("string");
        expect(JSON.stringify(doc)).to.include("did:");
      });

      it("D2 revoke attribute (or declared n/a)", async function () {
        if (!adapter.supports("D2_revoke_attribute")) return this.skip();
        await wait(await adapter.revokeAttribute(h, PAYLOADS.attributeName));
      });

      it("U5 meta-tx (or declared n/a)", async function () {
        if (!adapter.supports("U5_meta_tx")) return this.skip();
        await wait(await adapter.metaTxSetAttribute(h, PAYLOADS.attributeName, PAYLOADS.attributeValue, actors.verifier));
      });

      it("V1/V3/V6/V5 credential anchor + status", async function () {
        await wait(await adapter.anchorIssuerKey(actors.issuer, actors.delegateKey));
        const c = hre.ethers.keccak256(hre.ethers.toUtf8Bytes("cred-" + id));
        await wait(await adapter.anchorStatus(h, c));
        expect(await adapter.statusCheck(h, c)).to.equal("active");
        await wait(await adapter.revokeCredential(h, c));
        expect(await adapter.statusCheck(h, c)).to.equal("revoked");
      });

      it("V1/V3/V5 with a separate issuer (prepareIssuer) do not touch the default issuer", async function () {
        const iss = actors.extras[0];
        await adapter.prepareIssuer(iss);
        await wait(await adapter.anchorIssuerKey(iss, actors.extras[1]));
        const c = hre.ethers.keccak256(hre.ethers.toUtf8Bytes("cred2-" + id));
        await wait(await adapter.anchorStatus(h, c, iss));
        expect(await adapter.statusCheck(h, c, iss)).to.equal("active");
        await wait(await adapter.revokeCredential(h, c, iss));
        expect(await adapter.statusCheck(h, c, iss)).to.equal("revoked");
      });

      it("U1/U4 controller rotation and transfer", async function () {
        await wait(await adapter.rotateController(h, actors.newOwner));
        expect(await adapter.resolveOwner(h)).to.equal(actors.newOwner.address);
        await wait(await adapter.transferVehicle(h, actors.thirdOwner));
        expect(await adapter.resolveOwner(h)).to.equal(actors.thirdOwner.address);
      });

      it("D3 deactivate", async function () {
        await wait(await adapter.deactivate(h));
      });
    });
  }
});
