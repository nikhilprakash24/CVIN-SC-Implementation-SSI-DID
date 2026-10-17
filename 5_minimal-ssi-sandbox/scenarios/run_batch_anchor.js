// Scenario S17 — Batch anchor with on-chain inclusion verification.
//
// Compares three ways to make eleven lifecycle credentials verifiable:
//   (A) eleven F5 anchors                      — per-leaf status and revocation (from S8)
//   (B) one F5 anchor carrying the Merkle root — cheapest write, no on-chain inclusion (from S8)
//   (C) BatchAnchorRegistry.anchorBatch        — one write, on-chain inclusion proofs, batch-level revocation
// and measures the inclusion check as a view (gas-free), plus the proof size.
//
// Run: IMPL=O1_ERC1056 npx hardhat run scenarios/run_batch_anchor.js
const { ethers } = require("hardhat");
const { makeTrace } = require("../lib/vid/trace");
const V = require("../lib/vid/credentials");
const M = require("../lib/vid/merkle");

const IMPL = process.env.IMPL || "O1_ERC1056";

async function main() {
  const T = makeTrace(IMPL);
  const [dmvS, svcS, vehicleS, buyerS] = await ethers.getSigners();
  const ssi = await (await ethers.getContractFactory(IMPL)).deploy();
  const adapter = await (await ethers.getContractFactory("O1ControllerAdapter")).deploy(await ssi.getAddress());
  const bar = await (await ethers.getContractFactory("BatchAnchorRegistry")).deploy(await adapter.getAddress());
  T.log({ kind: "deploy", phase: "deploy", note: `${IMPL} + O1ControllerAdapter + BatchAnchorRegistry` });

  const mk = async (s, l) => T.parseEvent(ssi, await T.tx("createDID", "F1", l, ssi.connect(s).createDID(s.address)), "DIDCreated").did;
  const dmv = await mk(dmvS, "DMV"), svc = await mk(svcS, "ServiceCenter"), vehicle = await mk(vehicleS, "Vehicle");

  // Eleven maintenance-style events from the service centre (off-chain objects).
  const creds = [];
  for (let i = 0; i < 11; i++) {
    creds.push(await V.signCredential(svcS, V.lifecycleEvent({ tId: V.TYPES.EV_MAINTENANCE, issuerDid: svc, issuerRole: V.ROLES.SERVICE_CENTER, vehicleDid: vehicle,
      occurredAt: `2027-0${1 + (i % 9)}-15`, odometerKm: 10_000 * (i + 1), details: { visit: i + 1 } })));
  }
  T.off("build", "ServiceCenter", `11 lifecycle credentials signed off-chain`);

  // (A) per-leaf anchors
  let gasA = 0n;
  for (const c of creds) { const rc = await T.tx("issueCredential", "F5", "ServiceCenter", ssi.connect(svcS).issueCredential(svc, vehicle, c.anchor, 0), { note: "pattern A: per-leaf" }); gasA += rc.gasUsed; }

  // (B) root through F5
  const tree = M.buildTree(creds.map(c => c.anchor));
  const rcB = await T.tx("issueCredential", "F5", "ServiceCenter", ssi.connect(svcS).issueCredential(svc, vehicle, tree.root, 0), { note: "pattern B: Merkle root via F5" });

  // (C) dedicated batch anchor
  const batchId = ethers.id(`svc-batch-2027-Q1`);
  const rcC = await T.tx("anchorBatch", "B1", "ServiceCenter", bar.connect(svcS).anchorBatch(svc, batchId, tree.root, creds.length), { note: "pattern C: BatchAnchorRegistry" });
  // unauthorised anchor attempt
  try { await bar.connect(dmvS).anchorBatch(svc, ethers.id("x"), tree.root, 1); throw new Error("should revert"); }
  catch (e) { T.off("negative", "DMV", `anchorBatch as svc by DMV → ${/NotAuthorized/.test(e.message) ? "reverted (NotAuthorized)" : e.message}`); }

  // Buyer verifies inclusion of leaf 6 on-chain (view), and a tampered leaf.
  const idx = 6, proof = M.proofFor(tree, idx);
  const [inc, rev, iss] = await bar.verifyInclusion(batchId, creds[idx].anchor, proof);
  T.view("verifyInclusion", "B2", "Buyer", `leaf ${idx}: included=${inc} batchRevoked=${rev} issuer=${iss === svc ? "ServiceCenter" : "?"} proof=${proof.length} hashes (${proof.length * 32}B)`);
  const [incBad] = await bar.verifyInclusion(batchId, ethers.id("tampered"), proof);
  T.view("verifyInclusion", "B2", "Buyer", `tampered leaf: included=${incBad}`);
  T.off("verify-offline", "Buyer", `same proof verified off-chain: ${M.verify(tree.root, creds[idx].anchor, proof)}`);

  // Batch-level revocation: the only granularity pattern C offers.
  await T.tx("revokeBatch", "B3", "ServiceCenter", bar.connect(svcS).revokeBatch(batchId));
  const [inc2, rev2] = await bar.verifyInclusion(batchId, creds[idx].anchor, proof);
  T.view("verifyInclusion", "B2", "Buyer", `after revokeBatch: included=${inc2} batchRevoked=${rev2} — all 11 leaves revoked together (granularity cost of batching)`);

  T.off("summary", "Buyer", `gas A (11×F5)=${gasA} · B (root via F5)=${rcB.gasUsed} · C (anchorBatch)=${rcC.gasUsed} · ratio A/B=${(Number(gasA) / Number(rcB.gasUsed)).toFixed(2)} A/C=${(Number(gasA) / Number(rcC.gasUsed)).toFixed(2)}`);
  T.write("batch_anchor");
}
main().catch(e => { console.error(e); process.exit(1); });
