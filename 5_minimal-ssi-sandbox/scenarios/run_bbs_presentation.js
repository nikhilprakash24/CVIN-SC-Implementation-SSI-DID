// Scenario S19 — Policy-selected disclosure with BBS+ (HDA doc 02 §10 stage b; 03 §7).
//
// The same DRIVER_LICENCE credential is presented to three verifier classes under three
// disclosure policies, each as an unlinkable BBS+ proof bound to the verifier's nonce:
//   police           — full disclosure (verinym; forensic tier)
//   car-share kiosk  — licenceClass + validUntil only
//   age-gated venue  — nothing from the subject but the jurisdiction (and, in a later stage,
//                      a range predicate on the birth-year commitment; see 02 §4)
// On-chain, the hash anchor and F8 presentation record are unchanged by the proof system: the
// F8 challenge commits to the proof nonce so the chain records *that* a presentation happened
// without learning what was revealed. Off-chain proof sizes and laptop timings are recorded
// as instrumentation (lower bounds for an OBU are NOT implied).
//
// Run: IMPL=O1_ERC1056 npx hardhat run scenarios/run_bbs_presentation.js
const { ethers } = require("hardhat");
const crypto = require("crypto");
const { makeTrace } = require("../lib/vid/trace");
const V = require("../lib/vid/credentials");
const B = require("../lib/vid/bbs");

const IMPL = process.env.IMPL || "O1_ERC1056";
const YEAR = 365 * 24 * 3600;
const ms = (t0) => +(performance.now() - t0).toFixed(2);

async function main() {
  const T = makeTrace(IMPL);
  const [adminS, ministryS, dmvS, driverS, policeS, kioskS, venueS] = await ethers.getSigners();
  const ssi = await (await ethers.getContractFactory(IMPL)).deploy();
  const adapter = await (await ethers.getContractFactory("O1ControllerAdapter")).deploy(await ssi.getAddress());
  const reg = await (await ethers.getContractFactory("EndorsementRegistry")).connect(adminS).deploy(await ssi.getAddress(), await adapter.getAddress());
  T.log({ kind: "deploy", phase: "deploy", note: `${IMPL} + adapter + EndorsementRegistry` });

  const mk = async (s, l) => T.parseEvent(ssi, await T.tx("createDID", "F1", l, ssi.connect(s).createDID(s.address)), "DIDCreated").did;
  const ministry = await mk(ministryS, "Ministry"), dmv = await mk(dmvS, "DMV"), driver = await mk(driverS, "Driver");
  const police = await mk(policeS, "Police"), kiosk = await mk(kioskS, "CarShareKiosk"), venue = await mk(venueS, "AgeGatedVenue");
  await T.tx("addRoot", "G0", "RegistryAdmin", reg.addRoot(ministry));
  await T.tx("registerIssuer", "G1", "DMV", reg.connect(dmvS).registerIssuer(dmv, V.ROLES.GOVERNMENT_DMV));
  await T.tx("endorseIssuer", "G2", "Ministry", reg.connect(ministryS).endorseIssuer(ministry, dmv, V.TYPES.DRIVER_LICENCE, YEAR, false));

  // Issuer: BBS+ key published as a DID verification method (F9) — the key the verifier needs.
  const kp = await B.issuerKeyPair();
  await T.tx("addVerificationMethod", "F9", "DMV", ssi.connect(dmvS).addVerificationMethod(dmv, ethers.id("Bls12381G2Key2020"), kp.publicKey), { note: `BBS+ public key ${kp.publicKey.length}B published` });

  // Credential: same object as S7, hash-anchored via F5, plus a BBS+ signature over its claims.
  const lic = await V.signCredential(dmvS, V.driverLicence({ dmvDid: dmv, holderDid: driver, licenceClass: "5", restrictions: [], jurisdiction: "CA-BC", validFrom: "2026-09-01", validUntil: "2031-09-01", birthYear: 1995, birthSalt: crypto.randomBytes(8).toString("hex") }));
  const rcL = await T.tx("issueCredential", "F5", "DMV", ssi.connect(dmvS).issueCredential(dmv, driver, lic.anchor, 0), { note: "typed hash anchor (unchanged by BBS+)" });
  const licId = T.parseEvent(ssi, rcL, "CredentialIssued").credentialId;
  let t0 = performance.now();
  const signed = await B.sign(kp, lic.body);
  T.off("bbs-sign", "DMV", `BBS+ signature over ${signed.messages.length} claim messages: ${signed.signature.length}B, laptop ${ms(t0)} ms (issuance-time, Tier 3)`);
  t0 = performance.now();
  T.off("bbs-verify", "Driver", `holder checks full signature: ${await B.verifySignature(signed)} in ${ms(t0)} ms`);

  const policies = [
    ["Police", policeS, police, signed.messages.map(m => m.split("=")[0]), "full disclosure (forensic tier, verinym)"],
    ["CarShareKiosk", kioskS, kiosk, ["licenceClass", "validUntil"], "class + validity only"],
    ["AgeGatedVenue", venueS, venue, ["jurisdiction"], "jurisdiction only (age predicate = stage c)"],
  ];
  for (const [label, vS, vDid, reveal, why] of policies) {
    const nonce = crypto.randomBytes(16).toString("hex");
    t0 = performance.now();
    const derived = await B.createProof(signed, reveal, nonce);
    const tProve = ms(t0);
    t0 = performance.now();
    const ok = await B.verifyProof(signed.publicKey, derived, nonce);
    const tVerify = ms(t0);
    T.off("bbs-proof", "Driver→" + label, `${why}: reveals ${derived.revealedIndices.length}/${derived.messageCount} claims; proof ${derived.proof.length}B; prove ${tProve} ms, verify ${tVerify} ms (laptop); verified=${ok}; no chain access`);
    // wrong nonce / replay must fail off-chain
    T.off("negative", label, `same proof under a different nonce: verified=${await B.verifyProof(signed.publicKey, derived, nonce + "x")}`);
    // F8 commits that a presentation happened, bound to the nonce — content not on chain
    const ch = V.presentationChallenge({ verifierDid: vDid, holderDid: driver, credentialIds: [licId], purpose: "bbs-" + label, nonce, domain: "cvin-sandbox" });
    await T.tx("createPresentation", "F8", "Driver", ssi.connect(driverS).createPresentation(driver, [licId], ch, "cvin-sandbox"), { note: `commitment to the ${label} presentation (proof stays off-chain)` });
    const [valid] = await ssi.verifyCredential(licId);
    const [en] = await reg.isEndorsed(dmv, V.TYPES.DRIVER_LICENCE);
    T.view("verifyCredential+isEndorsed", "F6", label, `status valid=${valid} issuer endorsed=${en} (the only chain reads the verifier makes)`);
  }

  // Unlinkability check: two proofs for the same verifier policy are byte-different.
  const n1 = crypto.randomBytes(16).toString("hex"), n2 = crypto.randomBytes(16).toString("hex");
  const p1 = await B.createProof(signed, ["licenceClass"], n1), p2 = await B.createProof(signed, ["licenceClass"], n2);
  T.off("unlinkability", "Analyst", `two proofs, same disclosure, different nonces: identical=${Buffer.from(p1.proof).equals(Buffer.from(p2.proof))} (expected false); the hash-anchor path by contrast re-sends the same credential bytes every time`);

  // Revocation still flows through the chain: after F7, the proof still verifies but F6 says no.
  await T.tx("revokeCredential", "F7", "DMV", ssi.connect(dmvS).revokeCredential(licId), { note: "licence suspended" });
  const [v2, , r2] = await ssi.verifyCredential(licId);
  const still = await B.verifyProof(signed.publicKey, p1, n1);
  T.view("verifyCredential", "F6", "CarShareKiosk", `after F7: BBS+ proof still verifies=${still} but chain status valid=${v2} revoked=${r2} — the proof proves issuance, not currency; revocation is a status read or an accumulator (02 §6)`);

  T.write("bbs_presentation");
}
main().catch(e => { console.error(e); process.exit(1); });
