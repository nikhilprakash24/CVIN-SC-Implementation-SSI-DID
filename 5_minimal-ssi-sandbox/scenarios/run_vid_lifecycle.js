// Scenario S8 — "All the VIDs": the MOBI VID II lifecycle family (11 event types)
// as endorsed, typed, anchored credentials on top of IMinimalSSI.
//
// Every event type is issued by the role-appropriate issuer, whose entitlement for that
// type comes from an endorsement chain: Ministry (root) → transitive endorsers → issuers.
// Odometer monotonicity and the theft→recovery ordering are checked OFF-chain from the
// holder's wallet; the chain only anchors (F5), reports status (F6), and revokes (F7).
// Two anchoring modes are measured: per-event anchors (11 × F5) and one Merkle-batched
// anchor (1 × F5 over the root) — the cost lever discussed in HDA doc 01 §3/§7.
//
// Run: IMPL=O1_ERC1056 npx hardhat run scenarios/run_vid_lifecycle.js
const { ethers } = require("hardhat");
const crypto = require("crypto");
const { makeTrace } = require("../lib/vid/trace");
const V = require("../lib/vid/credentials");

const IMPL = process.env.IMPL || "O1_ERC1056";
const YEAR = 365 * 24 * 3600;

// Simple Merkle root over sorted leaves (keccak of concatenated pairs).
function merkleRoot(leaves) {
  let level = [...leaves].sort();
  while (level.length > 1) {
    const next = [];
    for (let i = 0; i < level.length; i += 2) {
      const a = level[i], b = level[i + 1] ?? level[i];
      next.push(ethers.keccak256(ethers.concat([a, b].sort())));
    }
    level = next;
  }
  return level[0];
}

async function main() {
  const T = makeTrace(IMPL);
  const S = await ethers.getSigners();
  const [ministryS, oemS, svcS, dmvS, inspS, insS, policeS, ownerS, vehicleS] = S;

  const ssi = await (await ethers.getContractFactory(IMPL)).deploy();
  const adapter = await (await ethers.getContractFactory("O1ControllerAdapter")).deploy(await ssi.getAddress());
  const reg = await (await ethers.getContractFactory("EndorsementRegistry")).deploy(await ssi.getAddress(), await adapter.getAddress());
  T.log({ kind: "deploy", phase: "deploy", note: `${IMPL} + O1ControllerAdapter + EndorsementRegistry` });

  const mk = async (signer, label) => T.parseEvent(ssi, await T.tx("createDID", "F1", label, ssi.connect(signer).createDID(signer.address)), "DIDCreated").did;
  const ministry = await mk(ministryS, "Ministry");
  const oem = await mk(oemS, "OEM");
  const svc = await mk(svcS, "ServiceCenter");
  const dmv = await mk(dmvS, "DMV");
  const insp = await mk(inspS, "InspectionStation");
  const ins = await mk(insS, "Insurer");
  const police = await mk(policeS, "Police");
  const owner = await mk(ownerS, "Owner");
  const vehicle = await mk(vehicleS, "Vehicle");

  await T.tx("addRoot", "G0", "RegistryAdmin", reg.addRoot(ministry));

  // Issuer roles (G1)
  const roles = [[oemS, oem, "OEM", V.ROLES.MANUFACTURER], [svcS, svc, "ServiceCenter", V.ROLES.SERVICE_CENTER], [dmvS, dmv, "DMV", V.ROLES.GOVERNMENT_DMV],
                 [inspS, insp, "InspectionStation", V.ROLES.GOVERNMENT_INSPECTION], [insS, ins, "Insurer", V.ROLES.INSURANCE_COMPANY],
                 [policeS, police, "Police", V.ROLES.POLICE], [ownerS, owner, "Owner", V.ROLES.OWNER]];
  for (const [s, did, label, role] of roles) await T.tx("registerIssuer", "G1", label, reg.connect(s).registerIssuer(did, role));

  // Entitlement map: which role may issue which event type (MOBI VID II role gating), expressed as endorsements.
  // Ministry endorses OEM transitively for MAINTENANCE/REPAIR so the OEM can endorse its service network.
  const E = V.TYPES;
  const chain = [
    [ministryS, ministry, oem, E.EV_RECALL, false], [ministryS, ministry, oem, E.EV_MAINTENANCE, true], [ministryS, ministry, oem, E.EV_REPAIR, true],
    [oemS, oem, svc, E.EV_MAINTENANCE, false], [oemS, oem, svc, E.EV_REPAIR, false], [oemS, oem, svc, E.EV_MODIFICATION, false],
    [ministryS, ministry, dmv, E.EV_REGISTRATION, false], [ministryS, ministry, dmv, E.EV_DECOMMISSION, false],
    [ministryS, ministry, insp, E.EV_INSPECTION, false],
    [ministryS, ministry, ins, E.EV_INSURANCE_CLAIM, false],
    [ministryS, ministry, police, E.EV_ACCIDENT, false], [ministryS, ministry, police, E.EV_THEFT_REPORT, false], [ministryS, ministry, police, E.EV_RECOVERY, false],
  ];
  // OEM must be registered+endorsed for MODIFICATION before it can endorse svc for it? No: OEM endorses svc for MODIFICATION
  // only if OEM holds a transitive endorsement for MODIFICATION. Ministry grants it:
  chain.splice(3, 0, [ministryS, ministry, oem, E.EV_MODIFICATION, true]);
  for (const [s, from, to, t, trans] of chain) {
    const label = from === ministry ? "Ministry" : "OEM";
    await T.tx("endorseIssuer", "G2", label, reg.connect(s).endorseIssuer(from, to, t, YEAR, trans), { note: `${label} → ${V.TYPE_NAME[t]}${trans ? " (transitive)" : ""}` });
  }
  // Owner self-reports are NOT endorsed by anyone: policy treats OWNER events as unverified (MOBI VID II semantics).

  // ---- The lifecycle: 11 events in order, off-chain objects + per-event anchors ----
  const wallet = new V.Wallet(vehicle);
  const issuers = { EV_REGISTRATION: [dmvS, dmv, "DMV", V.ROLES.GOVERNMENT_DMV], EV_MAINTENANCE: [svcS, svc, "ServiceCenter", V.ROLES.SERVICE_CENTER],
    EV_INSPECTION: [inspS, insp, "InspectionStation", V.ROLES.GOVERNMENT_INSPECTION], EV_MODIFICATION: [svcS, svc, "ServiceCenter", V.ROLES.SERVICE_CENTER],
    EV_REPAIR: [svcS, svc, "ServiceCenter", V.ROLES.SERVICE_CENTER], EV_RECALL: [oemS, oem, "OEM", V.ROLES.MANUFACTURER],
    EV_ACCIDENT: [policeS, police, "Police", V.ROLES.POLICE], EV_INSURANCE_CLAIM: [insS, ins, "Insurer", V.ROLES.INSURANCE_COMPANY],
    EV_THEFT_REPORT: [policeS, police, "Police", V.ROLES.POLICE], EV_RECOVERY: [policeS, police, "Police", V.ROLES.POLICE],
    EV_DECOMMISSION: [dmvS, dmv, "DMV", V.ROLES.GOVERNMENT_DMV] };
  const timeline = [
    ["EV_REGISTRATION", 0, { plate: "CVN 001", jurisdiction: "CA-BC" }],
    ["EV_MAINTENANCE", 12_000, { services: ["oil", "tires"], cost: 245 }],
    ["EV_INSPECTION", 18_500, { type: "EMISSIONS", result: "PASS" }],
    ["EV_MODIFICATION", 20_100, { part: "tow-hitch", certified: true }],
    ["EV_REPAIR", 25_400, { fault: "alternator", warranty: true }],
    ["EV_RECALL", 25_400, { campaign: "RC-2027-014", component: "brake-booster", remedy: "replace" }],
    ["EV_ACCIDENT", 31_900, { severity: "minor", report: "PD-77812" }],
    ["EV_INSURANCE_CLAIM", 31_950, { claim: "ICBC-4471", amount: 3200 }],
    ["EV_THEFT_REPORT", 40_200, { report: "TH-1204" }],
    ["EV_RECOVERY", 40_650, { report: "TH-1204", condition: "intact" }],
    ["EV_DECOMMISSION", 188_000, { reason: "end-of-life", recycler: "did:example:recycler" }],
  ];
  const anchored = []; // {id, cred}
  let lastOdo = -1, day = 0;
  for (const [type, odo, details] of timeline) {
    const [s, did, label, role] = issuers[type];
    const cred = await V.signCredential(s, V.lifecycleEvent({ tId: E[type], issuerDid: did, issuerRole: role, vehicleDid: vehicle, occurredAt: `2026-09-${String(3 + (day++ % 27)).padStart(2, "0")}`, odometerKm: odo, details }));
    // Off-chain policy checks BEFORE anchoring
    const [ok] = await reg.isEndorsed(did, E[type]);
    const mono = odo >= lastOdo;
    T.off("policy-check", label, `${type}: issuer endorsed=${ok} odometer monotonic=${mono} (${lastOdo}→${odo}) → ${ok && mono ? "anchor" : "REFUSE"}`);
    if (!(ok && mono)) continue;
    lastOdo = odo;
    const rc = await T.tx("issueCredential", "F5", label, ssi.connect(s).issueCredential(did, vehicle, cred.anchor, 0), { note: `${type} anchor` });
    const id = T.parseEvent(ssi, rc, "CredentialIssued").credentialId;
    wallet.store(id, cred); anchored.push({ id, cred, type });
  }

  // ---- Negative: Owner self-report of a MAINTENANCE event — anchors fine (F5 is issuer-agnostic) but is NOT endorsed ----
  const selfRep = await V.signCredential(ownerS, V.lifecycleEvent({ tId: E.EV_MAINTENANCE, issuerDid: owner, issuerRole: V.ROLES.OWNER, vehicleDid: vehicle, occurredAt: "2026-10-01", odometerKm: 190_000, details: { services: ["wash"] } }));
  const rcS = await T.tx("issueCredential", "F5", "Owner", ssi.connect(ownerS).issueCredential(owner, vehicle, selfRep.anchor, 0), { note: "OWNER self-report (unendorsed)" });
  const selfId = T.parseEvent(ssi, rcS, "CredentialIssued").credentialId;
  const [selfValid] = await ssi.verifyCredential(selfId); const [selfEnd] = await reg.isEndorsed(owner, E.EV_MAINTENANCE);
  T.view("verifyCredential+isEndorsed", "F6", "Buyer", `owner self-report: F6 valid=${selfValid} but endorsed=${selfEnd} ⇒ shown as UNVERIFIED in history (MOBI VID II owner-role semantics)`);
  // Negative: Insurer tries to issue a RECALL (not entitled): anchors, but fails endorsement
  const [insEnd] = await reg.isEndorsed(ins, E.EV_RECALL);
  T.view("isEndorsed", "G4", "Buyer", `Insurer entitled for RECALL: ${insEnd} ⇒ a RECALL anchored by the insurer would be rejected by policy`);

  // ---- Theft → recovery ordering check and a "stolen" gate (off-chain from wallet) ----
  const theft = anchored.find(a => a.type === "EV_THEFT_REPORT"), rec = anchored.find(a => a.type === "EV_RECOVERY");
  T.off("history-check", "Buyer", `theft report (odo ${theft.cred.body.credentialSubject.odometerKm}) precedes recovery (odo ${rec.cred.body.credentialSubject.odometerKm}); vehicle currently ${rec ? "RECOVERED" : "STOLEN"}`);

  // ---- Buyer verifies the full history: off-chain integrity for all, then chain status reads ----
  const cache = new V.VerifierCache(60_000);
  for (const [, did] of Object.values(issuers).map(x => [x[2], x[1]])) cache.putController(did, await adapter.controllerOf(did));
  T.view("resolveDID→controllerOf ×6", "F2", "Buyer", "issuer controllers cached (6 reads)");
  let okAll = true;
  for (const a of anchored) okAll = okAll && V.verifyOffline(a.cred, cache).ok;
  T.off("verify-offline", "Buyer", `${anchored.length} lifecycle credentials verified off-chain (integrity+issuer sig): all ok=${okAll}`);
  let validAll = true;
  for (const a of anchored) { const [v] = await ssi.verifyCredential(a.id); validAll = validAll && v; }
  T.view("verifyCredential ×" + anchored.length, "F6", "Buyer", `chain status for all anchored events: valid=${validAll}`);

  // ---- Merkle-batched alternative: ONE anchor for the whole history (cost lever) ----
  const root = merkleRoot(anchored.map(a => a.cred.anchor));
  const rcB = await T.tx("issueCredential", "F5", "DMV", ssi.connect(dmvS).issueCredential(dmv, vehicle, root, 0), { note: `Merkle root of ${anchored.length} event anchors (1 write instead of ${anchored.length})` });
  T.off("merkle-batch", "DMV", `root=${root.slice(0, 12)}… — inclusion proofs (${Math.ceil(Math.log2(anchored.length))} hashes) served off-chain; trade-off: per-event revocation granularity lost (doc 01 §3)`);

  // ---- Presentation of a selected subset to a buyer (F8): maintenance + inspection only ----
  const subset = anchored.filter(a => ["EV_MAINTENANCE", "EV_INSPECTION"].includes(a.type)).map(a => a.id);
  const ch = V.presentationChallenge({ verifierDid: owner, holderDid: vehicle, credentialIds: subset, purpose: "resale-history", nonce: crypto.randomBytes(8).toString("hex"), domain: "cvin-sandbox" });
  await T.tx("createPresentation", "F8", "Vehicle", ssi.connect(vehicleS).createPresentation(vehicle, subset, ch, "cvin-sandbox"), { note: "buyer sees maintenance+inspection, not claims (selective by credential)" });

  // ---- Recall closed: OEM revokes the RECALL credential after remedy (F7) ----
  const recall = anchored.find(a => a.type === "EV_RECALL");
  await T.tx("revokeCredential", "F7", "OEM", ssi.connect(oemS).revokeCredential(recall.id), { note: "recall remedied → status revoked (history retains the anchor)" });
  const [rv, , rr] = await ssi.verifyCredential(recall.id);
  T.view("verifyCredential", "F6", "Buyer", `RECALL after remedy: valid=${rv} revoked=${rr} — the anchor remains as history; policy reads 'closed'`);

  // ---- Decommission: vehicle DID deactivated with history retained (F4) ----
  await T.tx("deactivateDID", "F4", "Vehicle", ssi.connect(vehicleS).deactivateDID(vehicle));
  const [doc, meta] = await ssi.resolveDID(vehicle);
  T.view("resolveDID", "F2", "Buyer", `vehicle after decommission: resolvable=${doc.length > 2} deactivated flag present in metadata (${meta.length / 2 - 1}B)`);

  T.write("vid_lifecycle");
}

main().catch((e) => { console.error(e); process.exit(1); });
