// Scenario S16 — Reputation-weighted federated-learning round over CVIN identities,
// with a Sybil-injection experiment (HDA doc 09 §6, §9).
//
// The model is a toy (one scalar per client, "estimated mean free-flow speed on a road
// segment") so that the aggregation effect is visible without an ML stack. Each honest
// participant contributes a noisy estimate around the true value; Sybil participants
// contribute a poisoned value. The aggregator (an endorsed REPUTATION_ATTESTER) weights
// contributions by on-chain reputation (C2). Two configurations run:
//   GATED   — only endorsed attesters may score (SetCHarness gated=true): the Sybils have no
//             reputation and are weighted at the floor, so the aggregate stays near truth.
//   UNGATED — anyone may score anyone (gated=false): the Sybils score each other, acquire
//             reputation, and drag the aggregate.
// Every contribution is a signed off-chain object whose digest is Merkle-anchored once per
// round (B1); the round record (model hash, contributor-set root) is the only per-round write.
//
// Run: IMPL=O1_ERC1056 npx hardhat run scenarios/run_fl_round.js
const { ethers } = require("hardhat");
const { makeTrace } = require("../lib/vid/trace");
const V = require("../lib/vid/credentials");
const M = require("../lib/vid/merkle");

const IMPL = process.env.IMPL || "O1_ERC1056";
const YEAR = 365 * 24 * 3600;
const TRUE_VALUE = 80; // km/h, the quantity the round estimates
const N_HONEST = 6, N_SYBIL = 4, POISON = 20, FLOOR_WEIGHT = 0.05;

function weightedMean(items) {
  const w = items.reduce((s, i) => s + i.weight, 0);
  return items.reduce((s, i) => s + i.weight * i.value, 0) / w;
}

async function runConfig(T, gated, signers) {
  const label = gated ? "GATED" : "UNGATED";
  const [adminS, ministryS, aggS, ...clients] = signers;
  const ssi = await (await ethers.getContractFactory(IMPL)).deploy();
  const adapter = await (await ethers.getContractFactory("O1ControllerAdapter")).deploy(await ssi.getAddress());
  const reg = await (await ethers.getContractFactory("EndorsementRegistry")).connect(adminS).deploy(await ssi.getAddress(), await adapter.getAddress());
  const setc = await (await ethers.getContractFactory("SetCHarness")).deploy(await adapter.getAddress(), await reg.getAddress(), gated);
  const bar = await (await ethers.getContractFactory("BatchAnchorRegistry")).deploy(await adapter.getAddress());
  T.log({ kind: "deploy", phase: "deploy", note: `[${label}] ${IMPL} + adapter + EndorsementRegistry + SetCHarness(gated=${gated}) + BatchAnchorRegistry` });

  const mk = async (s, l) => T.parseEvent(ssi, await T.tx("createDID", "F1", l, ssi.connect(s).createDID(s.address)), "DIDCreated").did;
  const ministry = await mk(ministryS, "Ministry"), agg = await mk(aggS, "Aggregator");
  const honest = [], sybil = [];
  for (let i = 0; i < N_HONEST; i++) honest.push({ s: clients[i], did: await mk(clients[i], `Vehicle${i + 1}`), label: `Vehicle${i + 1}` });
  for (let i = 0; i < N_SYBIL; i++) sybil.push({ s: clients[N_HONEST + i], did: await mk(clients[N_HONEST + i], `Sybil${i + 1}`), label: `Sybil${i + 1}` });
  const all = [...honest, ...sybil];

  // Governance: ministry endorses the aggregator as a reputation attester.
  await T.tx("addRoot", "G0", "RegistryAdmin", reg.addRoot(ministry));
  await T.tx("registerIssuer", "G1", "Aggregator", reg.connect(aggS).registerIssuer(agg, ethers.id("role.aggregator")));
  await T.tx("endorseIssuer", "G2", "Ministry", reg.connect(ministryS).endorseIssuer(ministry, agg, await setc.REPUTATION_ATTESTER(), YEAR, false), { note: "aggregator entitled to score" });

  // Prior round history: aggregator scored honest vehicles on past contribution quality (C1).
  for (const h of honest) await T.tx("attestReputationAs", "C1", "Aggregator", setc.connect(aggS).attestReputationAs(agg, h.did, 80, `ipfs://prior/${h.label}`), { note: `${h.label} prior=80` });
  // Sybils try to acquire reputation by scoring each other.
  let sybilScored = 0;
  for (const a of sybil) for (const b of sybil) if (a !== b) {
    try { await T.tx("attestReputationAs", "C1", a.label, setc.connect(a.s).attestReputationAs(a.did, b.did, 100, "ipfs://fake"), { note: `${a.label}→${b.label} collusion score` }); sybilScored++; }
    catch (e) { T.off("negative", a.label, `${a.label} scoring ${b.label} → ${/NotEntitled/.test(e.message) ? "reverted (NotEntitled: not an endorsed attester)" : e.message.slice(0, 60)}`); break; }
  }
  if (!gated) T.off("collusion", "Sybils", `${sybilScored} mutual scores accepted (ungated harness)`);

  // Round: each client signs a contribution; the aggregator reads reputation (C2) and weights.
  const contributions = [];
  for (const c of all) {
    const isSybil = sybil.includes(c);
    const value = isSybil ? POISON : +(TRUE_VALUE + (Math.random() * 6 - 3)).toFixed(2);
    const payload = { round: 1, clientDid: c.did, value, norm: Math.abs(value - TRUE_VALUE) };
    const digest = V.contentHash(payload);
    const sig = await c.s.signMessage(ethers.getBytes(digest));
    const [mean, count] = await setc.getReputation(c.did);
    const weight = count === 0n ? FLOOR_WEIGHT : Math.max(FLOOR_WEIGHT, Number(mean) / 100);
    contributions.push({ ...c, value, digest, sig, weight, mean: Number(mean), count: Number(count) });
  }
  T.view("getReputation ×" + all.length, "C2", "Aggregator", contributions.map(c => `${c.label}:${c.mean}/${c.count}→w=${c.weight.toFixed(2)}`).join(" "));
  T.off("contributions", "Clients", `${all.length} signed updates (${N_HONEST} honest ≈${TRUE_VALUE}, ${N_SYBIL} Sybil =${POISON}); digests only go on-chain`);

  const unweighted = contributions.reduce((s, c) => s + c.value, 0) / contributions.length;
  const weighted = weightedMean(contributions);
  T.off("aggregate", "Aggregator", `[${label}] unweighted mean=${unweighted.toFixed(2)} · reputation-weighted mean=${weighted.toFixed(2)} · truth=${TRUE_VALUE} · error unweighted=${Math.abs(unweighted - TRUE_VALUE).toFixed(2)} weighted=${Math.abs(weighted - TRUE_VALUE).toFixed(2)}`);

  // Anchor the round: contributor-set root + model hash in one write; validation request for the model.
  const tree = M.buildTree(contributions.map(c => c.digest));
  const modelHash = V.contentHash({ round: 1, value: +weighted.toFixed(4), contributors: tree.root });
  await T.tx("anchorBatch", "B1", "Aggregator", bar.connect(aggS).anchorBatch(agg, ethers.id(`fl-round-1-${label}`), tree.root, contributions.length), { note: "contributor-set root (one write per round)" });
  const rcV = await T.tx("requestValidation", "C3", "Aggregator", setc.connect(aggS).requestValidation(agg, ethers.id("model-provenance"), ethers.getBytes(modelHash)), { note: "zkML/TEE hook: model hash submitted" });
  const reqId = T.parseEvent(setc, rcV, "ValidationRequested").requestId;
  await T.tx("resolveValidationAs", "C3", "Aggregator", setc.connect(aggS).resolveValidationAs(agg, reqId, true), { note: "harness resolution (no real proof)" });
  T.view("validationStatus", "C4", "Auditor", `round-1 model validation status=${await setc.validationStatus(reqId)} (2=valid; harness, no proof verified)`);

  // Post-round scoring: aggregator updates reputation by contribution norm (C1), gated by entitlement.
  for (const c of contributions) {
    const score = Math.max(0, Math.min(100, Math.round(100 - 2 * Math.abs(c.value - TRUE_VALUE))));
    await T.tx("attestReputationAs", "C1", "Aggregator", setc.connect(aggS).attestReputationAs(agg, c.did, score, `ipfs://round1/${c.label}`), { note: `${c.label} score=${score}` });
  }
  return { label, unweighted, weighted };
}

async function main() {
  const T = makeTrace(IMPL);
  const signers = await ethers.getSigners();
  const gated = await runConfig(T, true, signers);
  const ungated = await runConfig(T, false, signers);
  T.off("experiment", "Analyst", `Sybil suppression: GATED weighted error=${Math.abs(gated.weighted - TRUE_VALUE).toFixed(2)} vs UNGATED weighted error=${Math.abs(ungated.weighted - TRUE_VALUE).toFixed(2)} (unweighted both ≈${Math.abs(gated.unweighted - TRUE_VALUE).toFixed(2)}). Toy model, harness Set C; see HDA doc 09 §9`);
  T.write("fl_round");
}
main().catch(e => { console.error(e); process.exit(1); });
