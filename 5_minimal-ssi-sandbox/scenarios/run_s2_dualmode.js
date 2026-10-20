// Scenario S2 — Dual-mode identity (the SCMS differentiator from the 2020 CVIN paper).
//
// One vehicle, two identities in one system:
//   verinym  — the vehicle's long-lived DID, holding the MOBI VID credential; used for Tier 2/3
//              commercial transactions (charging, tolling, registration).
//   pseudonym pool — short-lived DIDs for the Tier 1 BSM stream, each AUTHORISED by a credential
//              issued from the verinym ("may transmit BSMs as pseudonym k"), rotated per epoch,
//              never linked on-chain to each other (only to the verinym through the credential,
//              which is disclosed only to the misbehaviour authority).
// What touches the chain: verinym lifecycle and VID anchor (Tier 3); pseudonym creation and
// authorisation credentials once per epoch (Tier 3, batched off the BSM path); nothing at
// message time — BSMs are signed by the pseudonym's delegate key and verified against a cached
// authorisation. Revocation: the authority revokes the epoch credential; the next cache refresh
// drops the pseudonym; the verinym is untouched.
//
// Run: IMPL=O1_ERC1056 npx hardhat run scenarios/run_s2_dualmode.js
const { ethers } = require("hardhat");
const crypto = require("crypto");
const { makeTrace } = require("../lib/vid/trace");
const V = require("../lib/vid/credentials");

const IMPL = process.env.IMPL || "O1_ERC1056";
const B32 = (s) => ethers.id(s);
const EPOCHS = 3;

async function main() {
  const T = makeTrace(IMPL);
  const [oemS, authS, vehicleS, ...obuS] = await ethers.getSigners();
  const ssi = await (await ethers.getContractFactory(IMPL)).deploy();
  T.log({ kind: "deploy", phase: "deploy", note: `${IMPL}` });
  const mk = async (s, l) => T.parseEvent(ssi, await T.tx("createDID", "F1", l, ssi.connect(s).createDID(s.address)), "DIDCreated").did;

  // Tier 3: verinym and VID
  const oem = await mk(oemS, "OEM"), authority = await mk(authS, "MisbehaviourAuthority"), verinym = await mk(vehicleS, "Vehicle(verinym)");
  const vid = await V.signCredential(oemS, V.vidBirth({ oemDid: oem, vehicleDid: verinym, vin: "1FTFW1E55MFA00001", vinSalt: "s", make: "Ford", model: "F-150", modelYear: 2026, productionDate: "2026-01-10", plantCode: "DEARBORN" }));
  const rcV = await T.tx("issueCredential", "F5", "OEM", ssi.connect(oemS).issueCredential(oem, verinym, vid.anchor, 0), { note: "MOBI VID on the verinym (Tier 3)" });
  const vidId = T.parseEvent(ssi, rcV, "CredentialIssued").credentialId;

  // Tier 3, per epoch: a fresh pseudonym DID + an authorisation credential from the verinym,
  // countersigned (anchored) by the authority. The verinym→pseudonym link lives ONLY in this
  // credential, held by the vehicle and disclosed only under the escrow policy (doc 02 §8).
  const pseudonyms = [];
  for (let e = 0; e < EPOCHS; e++) {
    const pS = obuS[e];
    const pseud = await mk(pS, `Pseudonym#${e}`);
    const auth = await V.signCredential(vehicleS, V.buildCredential({ tId: V.TYPES.VEHICLE_REGISTRATION, issuerDid: verinym, subjectDid: pseud,
      claims: { vehicleDid: pseud, plate: `EPOCH-${e}`, jurisdiction: "CA-BC", ownerDid: verinym, validFrom: `2026-11-0${e + 1}`, validUntil: `2026-11-0${e + 2}`, registrarDid: authority } }));
    // The AUTHORITY anchors the epoch authorisation (it vouches that pseud is backed by some valid VID without naming it on-chain)
    const rc = await T.tx("issueCredential", "F5", "MisbehaviourAuthority", ssi.connect(authS).issueCredential(authority, pseud, auth.anchor, Math.floor(Date.now() / 1000) + 86400 * (e + 1)), { note: `epoch ${e} BSM authorisation for Pseudonym#${e} (verinym link off-chain only)` });
    const authId = T.parseEvent(ssi, rc, "CredentialIssued").credentialId;
    // The pseudonym's BSM signing key is a sigAuth delegate of the pseudonym DID (F11)
    const bsmKey = ethers.Wallet.createRandom();
    await T.tx("addDelegate", "F11", `Pseudonym#${e}`, ssi.connect(pS).addDelegate(pseud, B32("sigAuth"), bsmKey.address, 86400), { note: "BSM signing key for the epoch" });
    pseudonyms.push({ e, pseud, authId, auth, bsmKey, pS });
  }
  T.off("pseudonym-pool", "Vehicle", `${EPOCHS} pseudonyms provisioned at Tier 3; on-chain there is no link between them or to the verinym (DIDs created by unrelated signers; only the authority's anchors)`);

  // Tier 1: BSM stream — no chain access. Receiver verifies BSM signature against the cached
  // delegate validity and cached authorisation status.
  const cache = new V.VerifierCache(300_000);
  for (const p of pseudonyms) {
    const [valid] = await ssi.verifyCredential(p.authId); cache.putStatus(p.authId, { valid });
    const del = await ssi.validDelegate(p.pseud, B32("sigAuth"), p.bsmKey.address);
    T.view("validDelegate+verifyCredential", "F12", "RSU", `epoch ${p.e}: delegate=${del} authorisation valid=${valid} → cached`);
  }
  let verified = 0, t0 = performance.now();
  for (let i = 0; i < 100; i++) {
    const p = pseudonyms[i % EPOCHS];
    const bsm = JSON.stringify({ id: p.pseud.slice(0, 10), lat: 49.2827 + i * 1e-5, lon: -123.1207, speed: 12.3, ts: Date.now() });
    const sig = await p.bsmKey.signMessage(bsm);
    const signer = ethers.verifyMessage(bsm, sig);
    if (signer === p.bsmKey.address && cache.fresh(cache.status.get(p.authId)) && cache.status.get(p.authId).valid) verified++;
  }
  T.off("bsm-stream", "RSU", `100 BSMs signed by pseudonym keys and verified with ZERO chain reads: ${verified}/100 ok in ${(performance.now() - t0).toFixed(1)} ms laptop (sig + cache; not a Tier 1 timing claim)`);

  // Tier 2: a commercial transaction uses the VERINYM, not a pseudonym (presentation of the VID)
  const ch = V.presentationChallenge({ verifierDid: authority, holderDid: verinym, credentialIds: [vidId], purpose: "charging", nonce: crypto.randomBytes(8).toString("hex"), domain: "cvin-sandbox" });
  const rcP = await T.tx("createPresentation", "F8", "Vehicle(verinym)", ssi.connect(vehicleS).createPresentation(verinym, [vidId], ch, "cvin-sandbox"), { note: "verinym presents the VID for a commercial session (Tier 2)" });
  // WO-9 overlay adapter: the presentation is an SD-JWT-style selective disclosure (salted digests);
  // its proof hash and format are anchored beside the F8 record; the disclosed claims stay off-chain.
  const pa = await (await ethers.getContractFactory("PresentationAnchor")).deploy(await ssi.getAddress());
  const salts = Object.fromEntries(Object.keys(vid.body.credentialSubject).map(k => [k, crypto.randomBytes(8).toString("hex")]));
  const sdProof = { format: "sd-jwt-vc/rfc9901", digests: V.disclosureDigests(vid.body.credentialSubject, salts), disclosed: { make: vid.body.credentialSubject.make, modelYear: vid.body.credentialSubject.modelYear } };
  const presId = T.parseEvent(ssi, rcP, "PresentationCreated").presentationId;
  await T.tx("anchorPresentation", "A1", "Vehicle(verinym)", pa.connect(vehicleS).anchorPresentation(verinym, await pa.FMT_SD_JWT(), V.contentHash(sdProof), presId), { note: "SD-JWT presentation anchored: format + proof hash (2 claims disclosed off-chain)" });
  const [anch, wd] = await pa.verifyAnchored(verinym, await pa.FMT_SD_JWT(), V.contentHash(sdProof), presId);
  T.view("verifyAnchored", "A2", "ChargingOperator", `proof I hold matches an anchored SD-JWT presentation: ${anch}, withdrawn=${wd}`);
  T.view("resolveDID", "F2", "ChargingOperator", `verinym resolvable: ${(await ssi.resolveDID(verinym))[0].length > 2}; pseudonyms never presented here`);

  // Misbehaviour: the authority revokes epoch 1's authorisation; the verinym and other epochs continue.
  const bad = pseudonyms[1];
  await T.tx("revokeCredential", "F7", "MisbehaviourAuthority", ssi.connect(authS).revokeCredential(bad.authId), { note: "epoch 1 authorisation revoked after misbehaviour report" });
  const stale = cache.status.get(bad.authId).valid;
  const [nowValid] = await ssi.verifyCredential(bad.authId); cache.putStatus(bad.authId, { valid: nowValid });
  T.view("verifyCredential", "F6", "RSU", `epoch 1 after revocation: cached=${stale} → refreshed=${nowValid}; other epochs and the verinym unaffected (${(await ssi.verifyCredential(vidId))[0]})`);
  // Escrowed linkage: only the authority, holding the off-chain authorisation credential, can map pseudonym→verinym
  T.off("escrow", "MisbehaviourAuthority", `linkage pseudonym#1 → verinym recovered from the off-chain authorisation credential (ownerDid=${bad.auth.body.credentialSubject.ownerDid === verinym}); never readable from chain state`);
  // Epoch rotation: the retired pseudonym is deactivated (history kept)
  await T.tx("deactivateDID", "F4", "Pseudonym#1", ssi.connect(bad.pS).deactivateDID(bad.pseud), { note: "retired pseudonym; DID stays resolvable for forensics" });

  T.write("s2_dualmode");
}
main().catch(e => { console.error(e); process.exit(1); });
