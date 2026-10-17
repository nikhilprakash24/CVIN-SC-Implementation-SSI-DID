// Scenario S14 — Low connectivity: read-only mode, delayed write, reconciliation.
//
// A vehicle holds a registration (from the DMV) and a maintenance history. It goes through
// ONLINE → READ_ONLY → PARTITIONED → ONLINE. While it cannot write, its OBU queues signed
// events (a toll-gantry pass receipt and two self-reported telemetry summaries) and keeps
// acting on its cached view. During the partition the DMV revokes the registration on-chain.
// On reconnect, the queue is reconciled against current chain state: the toll pass, which
// depended on the registration being valid, is rejected ("revocation wins"); the telemetry
// events survive and are anchored in ONE batch write. The trace shows queued `offchain`
// entries followed by a single `tx`, as doc 06 §7 specifies.
//
// Run: IMPL=O1_ERC1056 npx hardhat run scenarios/run_delayed_write.js
const { ethers } = require("hardhat");
const { makeTrace } = require("../lib/vid/trace");
const V = require("../lib/vid/credentials");
const M = require("../lib/vid/merkle");
const O = require("../lib/vid/offline");

const IMPL = process.env.IMPL || "O1_ERC1056";
const YEAR = 365 * 24 * 3600;

async function main() {
  const T = makeTrace(IMPL);
  const [adminS, ministryS, dmvS, vehicleS, tollS] = await ethers.getSigners();
  const ssi = await (await ethers.getContractFactory(IMPL)).deploy();
  const adapter = await (await ethers.getContractFactory("O1ControllerAdapter")).deploy(await ssi.getAddress());
  const reg = await (await ethers.getContractFactory("EndorsementRegistry")).connect(adminS).deploy(await ssi.getAddress(), await adapter.getAddress());
  const bar = await (await ethers.getContractFactory("BatchAnchorRegistry")).deploy(await adapter.getAddress());
  T.log({ kind: "deploy", phase: "deploy", note: `${IMPL} + adapter + EndorsementRegistry + BatchAnchorRegistry` });

  const mk = async (s, l) => T.parseEvent(ssi, await T.tx("createDID", "F1", l, ssi.connect(s).createDID(s.address)), "DIDCreated").did;
  const ministry = await mk(ministryS, "Ministry"), dmv = await mk(dmvS, "DMV"), vehicle = await mk(vehicleS, "Vehicle"), toll = await mk(tollS, "TollOperator");
  await T.tx("addRoot", "G0", "RegistryAdmin", reg.addRoot(ministry));
  await T.tx("registerIssuer", "G1", "DMV", reg.connect(dmvS).registerIssuer(dmv, V.ROLES.GOVERNMENT_DMV));
  await T.tx("endorseIssuer", "G2", "Ministry", reg.connect(ministryS).endorseIssuer(ministry, dmv, V.TYPES.VEHICLE_REGISTRATION, YEAR, false));

  // Tier 3, online: registration issued and anchored.
  const regn = await V.signCredential(dmvS, V.vehicleRegistration({ dmvDid: dmv, vehicleDid: vehicle, plate: "CVN 014", jurisdiction: "CA-BC", ownerDid: vehicle, validFrom: "2026-10-01", validUntil: "2027-10-01" }));
  const rcR = await T.tx("issueCredential", "F5", "DMV", ssi.connect(dmvS).issueCredential(dmv, vehicle, regn.anchor, 0), { note: "registration anchor" });
  const regId = T.parseEvent(ssi, rcR, "CredentialIssued").credentialId;

  // Verifier (toll operator) and vehicle warm their caches while online.
  const link = new O.Link();
  const tollCache = new V.VerifierCache(120_000);
  tollCache.putController(dmv, await adapter.controllerOf(dmv));
  { const [valid, , revoked] = await ssi.verifyCredential(regId); tollCache.putStatus(regId, { valid, revoked }); }
  T.view("resolveDID+verifyCredential", "F6", "TollOperator", "cache warmed while ONLINE: registration valid=true");
  const queue = new O.WriteQueue(vehicleS, vehicle);

  // --- READ_ONLY: writes refused, reads fine ---
  link.set(O.MODE.READ_ONLY);
  T.off("link", "Vehicle", "mode=READ_ONLY (relayer refuses writes; chain readable)");
  const [v1] = await ssi.verifyCredential(regId);
  T.view("verifyCredential", "F6", "TollOperator", `live read in READ_ONLY: registration valid=${v1}`);
  const tollPass = await queue.enqueue("TOLL_PASS", { gantry: "HWY1-W-07", at: Date.now(), amount: 3.25, presentation: V.presentationChallenge({ verifierDid: toll, holderDid: vehicle, credentialIds: [regId], purpose: "toll", nonce: O.nonce(), domain: "cvin-sandbox" }) }, [regId]);
  T.off("queued", "Vehicle", `#${tollPass.counter} TOLL_PASS signed and queued (write refused; depends on registration ${regId.slice(0, 10)}…)`);
  T.off("gate-decision", "TollOperator", `admits vehicle on cached status (fresh=${tollCache.fresh(tollCache.status.get(regId))}) + off-chain VP; settlement deferred`);

  // --- PARTITIONED: no chain; act on cache only ---
  link.set(O.MODE.PARTITIONED);
  T.off("link", "Vehicle", "mode=PARTITIONED (no reads, no writes)");
  const r = V.verifyOffline(regn, tollCache);
  T.off("verify-offline", "TollOperator", `registration from cache: ok=${r.ok} cacheFresh=${r.cacheFresh} (no chain access)`);
  const t1 = await queue.enqueue("TELEMETRY_SUMMARY", { window: "h1", kmDriven: 42, roadCondition: "wet" }, []);
  const t2 = await queue.enqueue("TELEMETRY_SUMMARY", { window: "h2", kmDriven: 38, roadCondition: "dry" }, []);
  T.off("queued", "Vehicle", `#${t1.counter}, #${t2.counter} TELEMETRY_SUMMARY signed and queued (no dependencies)`);

  // Meanwhile, the DMV (online) revokes the registration.
  await T.tx("revokeCredential", "F7", "DMV", ssi.connect(dmvS).revokeCredential(regId), { note: "revoked DURING the vehicle's partition" });
  const r2 = V.verifyOffline(regn, tollCache);
  T.off("verify-offline", "TollOperator", `still partitioned: cache says ok=${r2.ok} — stale acceptance window open (F-VID-3)`);

  // --- ONLINE again: reconcile and batch-anchor ---
  link.set(O.MODE.ONLINE);
  T.off("link", "Vehicle", "mode=ONLINE (reconnect)");
  const items = queue.drain();
  const { accepted, rejected } = await O.reconcile(items, async (credId) => (await ssi.verifyCredential(credId))[0]);
  for (const it of rejected) T.off("reconcile", "Vehicle", `REJECT #${it.counter} ${it.kind}: ${it.reasons.join("; ")} (revocation wins)`);
  for (const it of accepted) T.off("reconcile", "Vehicle", `ACCEPT #${it.counter} ${it.kind}`);
  { const [valid, , revoked] = await ssi.verifyCredential(regId); tollCache.putStatus(regId, { valid, revoked });
    T.view("verifyCredential", "F6", "TollOperator", `cache refreshed on reconnect: valid=${valid} revoked=${revoked} → toll settlement for #${tollPass.counter} denied; dispute path (doc 06 §3)`); }

  const leaves = accepted.map(it => it.digest);
  const tree = M.buildTree(leaves);
  const batchId = ethers.id(`vehicle-queue-${Date.now()}`);
  await T.tx("anchorBatch", "B1", "Vehicle", bar.connect(vehicleS).anchorBatch(vehicle, batchId, tree.root, leaves.length), { note: `ONE write anchors ${leaves.length} queued events` });
  const [inc] = await bar.verifyInclusion(batchId, leaves[0], M.proofFor(tree, 0));
  T.view("verifyInclusion", "B2", "Auditor", `queued event #${accepted[0].counter} provably anchored: included=${inc}`);
  T.off("summary", "Vehicle", `queued=${items.length} accepted=${accepted.length} rejected=${rejected.length}; writes during outage=0; writes on reconnect=1`);
  T.write("delayed_write");
}
main().catch(e => { console.error(e); process.exit(1); });
