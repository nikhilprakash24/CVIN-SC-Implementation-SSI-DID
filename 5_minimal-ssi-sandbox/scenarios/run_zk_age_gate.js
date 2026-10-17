// Scenario S20 — Age-gate range predicate with a Groth16 proof, verified on-chain and off-chain
// (HDA doc 02 §3, §4 case C-2, §10 stage c).
//
// The driver's licence carries a Poseidon commitment to the birth year. At an age-gated venue
// the driver proves birthYear <= currentYear - 18 without revealing the year:
//   off-chain path — venue verifies the proof with the verification key (gas-free);
//   on-chain path  — venue (or the driver) submits the proof to ZKAgeGate.admit, which calls the
//                    snarkjs-exported Groth16Verifier; this is the first MEASURED on-chain proof
//                    verification in the sandbox.
// A proof for an under-age birth year cannot be generated (constraint fails); a proof against
// the wrong commitment is rejected on-chain.
//
// Run: IMPL=O1_ERC1056 npx hardhat run scenarios/run_zk_age_gate.js
const { ethers } = require("hardhat");
const crypto = require("crypto");
const { makeTrace } = require("../lib/vid/trace");
const V = require("../lib/vid/credentials");
const Z = require("../lib/vid/zk");

const IMPL = process.env.IMPL || "O1_ERC1056";
const ms = (t0) => +(performance.now() - t0).toFixed(2);

async function main() {
  const T = makeTrace(IMPL);
  const [adminS, dmvS, driverS, venueS, minorS] = await ethers.getSigners();
  const ssi = await (await ethers.getContractFactory(IMPL)).deploy();
  const verifier = await (await ethers.getContractFactory("Groth16Verifier")).deploy();
  const gate = await (await ethers.getContractFactory("ZKAgeGate")).deploy(await verifier.getAddress());
  T.log({ kind: "deploy", phase: "deploy", note: `${IMPL} + Groth16Verifier (snarkjs export, AgeGate 256 constraints) + ZKAgeGate` });
  void adminS;

  const mk = async (s, l) => T.parseEvent(ssi, await T.tx("createDID", "F1", l, ssi.connect(s).createDID(s.address)), "DIDCreated").did;
  const dmv = await mk(dmvS, "DMV"), driver = await mk(driverS, "Driver"), venue = await mk(venueS, "AgeGatedVenue"), minor = await mk(minorS, "Minor");

  // Issuance (Tier 3): licence with a Poseidon commitment to birthYear.
  const birthYear = 1995, salt = BigInt("0x" + crypto.randomBytes(16).toString("hex"));
  const commitment = await Z.commit(birthYear, salt);
  const lic = await V.signCredential(dmvS, V.buildCredential({ tId: V.TYPES.DRIVER_LICENCE, issuerDid: dmv, subjectDid: driver,
    claims: { holderDid: driver, licenceClass: "5", restrictions: [], jurisdiction: "CA-BC", validFrom: "2026-09-01", validUntil: "2031-09-01", issuerDid: dmv, birthYearCommitment: commitment.toString() } }));
  const rcL = await T.tx("issueCredential", "F5", "DMV", ssi.connect(dmvS).issueCredential(dmv, driver, lic.anchor, 0), { note: "licence anchor; Poseidon commitment inside the signed credential" });
  const licId = T.parseEvent(ssi, rcL, "CredentialIssued").credentialId;
  T.off("commitment", "DMV", `birthYearCommitment = Poseidon(birthYear, salt); salt held by the driver; year never leaves the wallet`);

  // Presentation (Tier 2): proof that birthYear <= 2026 - 18.
  const maxBirthYear = 2026 - 18;
  let t0 = performance.now();
  const pr = await Z.prove({ birthYear, salt, commitment, maxBirthYear });
  const tProve = ms(t0);
  t0 = performance.now();
  const okOff = await Z.verifyOffChain(pr);
  const tVerify = ms(t0);
  const cd = await Z.calldata(pr);
  T.off("zk-prove", "Driver", `Groth16 proof generated in ${tProve} ms (laptop, WASM witness); public signals=[commitment, ${maxBirthYear}]; calldata ${cd.bytes}B`);
  T.off("zk-verify-offchain", "AgeGatedVenue", `verification key check: ${okOff} in ${tVerify} ms (no chain access)`);

  // F8 commitment to the presentation, then the on-chain verification path.
  const nonce = crypto.randomBytes(8).toString("hex");
  const ch = V.presentationChallenge({ verifierDid: venue, holderDid: driver, credentialIds: [licId], purpose: "age-gate", nonce, domain: "cvin-sandbox" });
  const rcP = await T.tx("createPresentation", "F8", "Driver", ssi.connect(driverS).createPresentation(driver, [licId], ch, "cvin-sandbox"));
  const presId = T.parseEvent(ssi, rcP, "PresentationCreated").presentationId;
  T.view("check", "Z2", "AgeGatedVenue", `on-chain view verification: ${await gate.check(cd.a, cd.b, cd.c, cd.pub[0], cd.pub[1])} (gas-free read path)`);
  await T.tx("admit", "Z1", "AgeGatedVenue", gate.connect(venueS).admit(presId, cd.a, cd.b, cd.c, cd.pub[0], cd.pub[1]), { note: "on-chain Groth16 verification + admission record" });
  try { await gate.connect(venueS).admit(presId, cd.a, cd.b, cd.c, cd.pub[0], cd.pub[1]); throw new Error("should revert"); }
  catch (e) { T.off("negative", "AgeGatedVenue", `replayed admission → ${/Replay/.test(e.message) ? "reverted (Replay)" : e.message.slice(0, 80)}`); }
  // Wrong commitment (someone else's) with a valid-looking proof → InvalidProof
  const other = await Z.commit(1990, 1n);
  try { await gate.connect(venueS).admit(ethers.id("p2"), cd.a, cd.b, cd.c, other, cd.pub[1]); throw new Error("should revert"); }
  catch (e) { T.off("negative", "AgeGatedVenue", `proof against another commitment → ${/InvalidProof/.test(e.message) ? "reverted (InvalidProof)" : e.message.slice(0, 80)}`); }

  // A minor cannot produce a proof at all (constraint birthYear <= maxBirthYear fails in witness generation).
  const mSalt = 7n, mCommit = await Z.commit(2012, mSalt);
  try { await Z.prove({ birthYear: 2012, salt: mSalt, commitment: mCommit, maxBirthYear }); T.off("negative", "Minor", "UNEXPECTED: proof generated for an under-age year"); }
  catch (e) { T.off("negative", "Minor", `birthYear 2012 > ${maxBirthYear}: witness generation fails (${e.message.split("\n")[0].slice(0, 60)}) — no proof exists`); }
  void minor;

  // Compare with the BBS+ path (S19) and the hash path (S7): what the venue learns.
  T.off("comparison", "Analyst", `venue learns: hash path = whole credential; BBS+ (S19) = chosen claims incl. the birth year if asked; Groth16 (this) = only the predicate result. On-chain: hash/BBS+ paths cost F8 only; this path adds one admit() tx (see trace) or a free check() view`);
  T.write("zk_age_gate");
}
// snarkjs keeps bn128 worker threads alive; exit explicitly once the trace is written.
main().then(() => process.exit(0)).catch(e => { console.error(e); process.exit(1); });
