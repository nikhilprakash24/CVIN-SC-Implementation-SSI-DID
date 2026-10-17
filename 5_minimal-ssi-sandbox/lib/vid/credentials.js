// VID credential layer — off-chain objects, on-chain anchors.
//
// Every credential here is a W3C-shaped JSON object that lives OFF-chain (holder
// wallet, issuer store). The chain sees only:
//   * the typed anchor passed to F5:  keccak256(abi.encode(typeId, schemaHash, contentHash))
//   * revocation state (F7) and status reads (F6)
//   * presentation commitments (F8) bound to a verifier challenge
//   * issuer entitlement (EndorsementRegistry, G1–G4)
//
// Off-chain verification = (1) canonical JSON → contentHash; (2) issuer's EIP-191
// signature over the typed hash recovers to the issuer DID's controller (cached DID
// document or adapter read); (3) optional chain status read (F6) and entitlement
// read (G4), or a cached copy within a staleness window. Steps (1)–(2) need no
// chain access at all — this is the read path that serves Tier 2 and offline modes
// (HDA campaign doc 01 §4, doc 06 §5).
const { ethers } = require("ethers");

// ---- canonicalisation + hashing ----

function canonicalize(obj) {
  // Deterministic JSON: sorted keys, no whitespace. Same rule as the Python VC layer
  // in 2_w3c-ssi-layer (documented deviation from JSON-LD URDNA2015).
  if (Array.isArray(obj)) return "[" + obj.map(canonicalize).join(",") + "]";
  if (obj && typeof obj === "object") {
    return "{" + Object.keys(obj).sort().map(k => JSON.stringify(k) + ":" + canonicalize(obj[k])).join(",") + "}";
  }
  return JSON.stringify(obj);
}
const contentHash = (obj) => ethers.keccak256(ethers.toUtf8Bytes(canonicalize(obj)));
const typeId = (name) => ethers.id(name);
const schemaHash = (schemaObj) => contentHash(schemaObj);
function typedHash(tId, sHash, cHash) {
  return ethers.keccak256(ethers.AbiCoder.defaultAbiCoder().encode(["bytes32", "bytes32", "bytes32"], [tId, sHash, cHash]));
}

// ---- credential types (must match contracts/credentials/CredentialTypes.sol) ----
const TYPES = {
  VID_BIRTH: typeId("cvin.vid.birth.v1"),
  VEHICLE_REGISTRATION: typeId("cvin.vid.registration.v1"),
  DRIVER_LICENCE: typeId("cvin.person.driver-licence.v1"),
  EV_MAINTENANCE: typeId("cvin.vid.event.maintenance.v1"),
  EV_REPAIR: typeId("cvin.vid.event.repair.v1"),
  EV_ACCIDENT: typeId("cvin.vid.event.accident.v1"),
  EV_RECALL: typeId("cvin.vid.event.recall.v1"),
  EV_INSPECTION: typeId("cvin.vid.event.inspection.v1"),
  EV_MODIFICATION: typeId("cvin.vid.event.modification.v1"),
  EV_THEFT_REPORT: typeId("cvin.vid.event.theft-report.v1"),
  EV_RECOVERY: typeId("cvin.vid.event.recovery.v1"),
  EV_INSURANCE_CLAIM: typeId("cvin.vid.event.insurance-claim.v1"),
  EV_REGISTRATION: typeId("cvin.vid.event.registration.v1"),
  EV_DECOMMISSION: typeId("cvin.vid.event.decommission.v1"),
};
const TYPE_NAME = Object.fromEntries(Object.entries(TYPES).map(([k, v]) => [v, k]));

// Issuer roles (issuerRole in EndorsementRegistry) — the MOBI VID II role set.
const ROLES = {
  ROOT_MINISTRY: ethers.id("role.ministry-of-transport"),
  OEM_ROOT: ethers.id("role.oem-root"),
  MANUFACTURER: ethers.id("role.manufacturer"),
  SERVICE_CENTER: ethers.id("role.service-center"),
  GOVERNMENT_DMV: ethers.id("role.government-dmv"),
  GOVERNMENT_INSPECTION: ethers.id("role.government-inspection"),
  INSURANCE_COMPANY: ethers.id("role.insurance-company"),
  POLICE: ethers.id("role.police"),
  OWNER: ethers.id("role.owner"),
  FLEET_MANAGER: ethers.id("role.fleet-manager"),
};

// Minimal schemas. The schemaHash binds the credential to a schema version in the anchor.
const SCHEMAS = {
  [TYPES.VID_BIRTH]: { $id: "cvin/vid/birth/v1", required: ["vehicleDid", "vinHash", "make", "model", "modelYear", "productionDate", "manufacturerDid", "plantCode"] },
  [TYPES.VEHICLE_REGISTRATION]: { $id: "cvin/vid/registration/v1", required: ["vehicleDid", "plate", "jurisdiction", "ownerDid", "validFrom", "validUntil", "registrarDid"] },
  [TYPES.DRIVER_LICENCE]: { $id: "cvin/person/driver-licence/v1", required: ["holderDid", "licenceClass", "restrictions", "jurisdiction", "validFrom", "validUntil", "issuerDid", "birthYearCommitment"] },
  // one lifecycle schema shared by all 11 event types; `eventType` names the type
  LIFECYCLE: { $id: "cvin/vid/event/v1", required: ["vehicleDid", "eventType", "issuerDid", "issuerRole", "occurredAt", "odometerKm", "detailsHash"] },
};
for (const k of Object.keys(TYPES)) if (k.startsWith("EV_")) SCHEMAS[TYPES[k]] = SCHEMAS.LIFECYCLE;

const W3C_CONTEXT = ["https://www.w3.org/ns/credentials/v2", "https://cvin.ubc.ca/credentials/automotive/v1"];

// ---- builders (all off-chain; no chain interaction) ----

function buildCredential({ tId, issuerDid, subjectDid, claims, validUntil = 0 }) {
  const schema = SCHEMAS[tId];
  for (const r of schema.required) if (!(r in claims)) throw new Error(`missing claim ${r} for ${TYPE_NAME[tId]}`);
  const body = {
    "@context": W3C_CONTEXT,
    type: ["VerifiableCredential", TYPE_NAME[tId]],
    issuer: issuerDid,
    credentialSubject: { id: subjectDid, ...claims },
    validUntil: validUntil || null,
    credentialSchema: { id: schema.$id, digest: schemaHash(schema) },
  };
  const cHash = contentHash(body);
  const sHash = schemaHash(schema);
  return { body, typeId: tId, schemaHash: sHash, contentHash: cHash, anchor: typedHash(tId, sHash, cHash), validUntil };
}

const vinHash = (vin, salt) => ethers.keccak256(ethers.toUtf8Bytes(`${vin}|${salt}`)); // VIN never leaves the holder in clear
const commitment = (value, salt) => ethers.keccak256(ethers.toUtf8Bytes(`${value}|${salt}`));

function vidBirth({ oemDid, vehicleDid, vin, vinSalt, make, model, modelYear, productionDate, plantCode }) {
  return buildCredential({ tId: TYPES.VID_BIRTH, issuerDid: oemDid, subjectDid: vehicleDid,
    claims: { vehicleDid, vinHash: vinHash(vin, vinSalt), make, model, modelYear, productionDate, manufacturerDid: oemDid, plantCode } });
}
function vehicleRegistration({ dmvDid, vehicleDid, plate, jurisdiction, ownerDid, validFrom, validUntil }) {
  return buildCredential({ tId: TYPES.VEHICLE_REGISTRATION, issuerDid: dmvDid, subjectDid: vehicleDid, validUntil,
    claims: { vehicleDid, plate, jurisdiction, ownerDid, validFrom, validUntil, registrarDid: dmvDid } });
}
function driverLicence({ dmvDid, holderDid, licenceClass, restrictions, jurisdiction, validFrom, validUntil, birthYear, birthSalt }) {
  return buildCredential({ tId: TYPES.DRIVER_LICENCE, issuerDid: dmvDid, subjectDid: holderDid, validUntil,
    claims: { holderDid, licenceClass, restrictions, jurisdiction, validFrom, validUntil, issuerDid: dmvDid,
              birthYearCommitment: commitment(birthYear, birthSalt) } }); // age predicates proven off-chain (doc 02)
}
function lifecycleEvent({ tId, issuerDid, issuerRole, vehicleDid, occurredAt, odometerKm, details }) {
  return buildCredential({ tId, issuerDid, subjectDid: vehicleDid,
    claims: { vehicleDid, eventType: TYPE_NAME[tId], issuerDid, issuerRole, occurredAt, odometerKm, detailsHash: contentHash(details) } });
}

// ---- issuer signature (off-chain proof of issuance; verifiable without the chain) ----

async function signCredential(signer, cred) {
  // EIP-191 personal-sign over the typed anchor — same posture as the Python VC layer.
  const sig = await signer.signMessage(ethers.getBytes(cred.anchor));
  return { ...cred, proof: { type: "DataIntegrityProof", cryptosuite: "eip191-secp256k1-recovery-2024", proofValue: sig } };
}
function recoverIssuerAddress(cred) {
  return ethers.verifyMessage(ethers.getBytes(cred.anchor), cred.proof.proofValue);
}

// ---- holder wallet + verifier (off-chain) ----

class Wallet {
  constructor(did) { this.did = did; this.creds = new Map(); }
  store(credentialId, signedCred) { this.creds.set(credentialId, signedCred); }
  get(credentialId) { return this.creds.get(credentialId); }
  list(tId) { return [...this.creds.entries()].filter(([, c]) => !tId || c.typeId === tId); }
}

// A verifier's local cache of identity state: DID controller addresses and status
// reads, each stamped with the time it was fetched. `staleness` is the window in ms
// within which the cache is trusted without a chain read (the security parameter of
// the read-only / low-connectivity modes).
class VerifierCache {
  constructor(staleness = 60_000) { this.staleness = staleness; this.controllers = new Map(); this.status = new Map(); this.endorsed = new Map(); }
  putController(did, addr) { this.controllers.set(did, { addr, at: Date.now() }); }
  putStatus(credentialId, s) { this.status.set(credentialId, { ...s, at: Date.now() }); }
  putEndorsed(issuerDid, tId, e) { this.endorsed.set(issuerDid + tId, { ...e, at: Date.now() }); }
  fresh(entry) { return entry && Date.now() - entry.at <= this.staleness; }
}

// Fully offline verification: integrity + issuer signature against the cached controller.
// Returns structured results (never throws for a bad credential).
function verifyOffline(signedCred, cache) {
  const recomputed = contentHash(signedCred.body);
  const integrity = recomputed === signedCred.contentHash
    && typedHash(signedCred.typeId, signedCred.schemaHash, signedCred.contentHash) === signedCred.anchor;
  let signer = null, issuerBound = false, cacheFresh = false;
  try { signer = recoverIssuerAddress(signedCred); } catch { signer = null; }
  const c = cache.controllers.get(signedCred.body.issuer);
  if (c) { cacheFresh = cache.fresh(c); issuerBound = signer && signer.toLowerCase() === c.addr.toLowerCase(); }
  const expired = signedCred.validUntil ? Math.floor(Date.now() / 1000) > Number(signedCred.validUntil) : false;
  return { integrity, issuerBound, cacheFresh, expired, ok: integrity && issuerBound && !expired };
}

// Presentation request → challenge bound into F8. The verifier constructs the request;
// the holder signs the F8 transaction with that challenge; replay is prevented on-chain.
function presentationChallenge({ verifierDid, holderDid, credentialIds, purpose, nonce, domain }) {
  return contentHash({ verifierDid, holderDid, credentialIds, purpose, nonce, domain });
}

// Selective disclosure (SD-JWT-style): salted digests per claim; holder discloses a subset.
function disclosureDigests(claims, salts) {
  const out = {};
  for (const [k, v] of Object.entries(claims)) out[k] = ethers.keccak256(ethers.toUtf8Bytes(`${salts[k]}|${k}|${canonicalize(v)}`));
  return out;
}

module.exports = {
  canonicalize, contentHash, typedHash, typeId, schemaHash, TYPES, TYPE_NAME, ROLES, SCHEMAS,
  buildCredential, vidBirth, vehicleRegistration, driverLicence, lifecycleEvent, vinHash, commitment,
  signCredential, recoverIssuerAddress, Wallet, VerifierCache, verifyOffline, presentationChallenge, disclosureDigests,
};
