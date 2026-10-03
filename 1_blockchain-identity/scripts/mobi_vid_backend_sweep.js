/**
 * mobi_vid_backend_sweep.js
 *
 * H4 evidence: "MOBI VID realizable across backends."
 *
 * Realizes MOBI VID's THREE canonical operations on EVERY blockchain-identity
 * backend that could host them, using each backend's NATIVE primitives and the
 * ALREADY-DEPLOYED contracts (no contract is modified; deploy patterns reused
 * from scripts/benchmark_gas.js). For every backend x operation we record the
 * real receipt.gasUsed AND — crucially — the FIDELITY: whether the backend
 * natively supports the concept or the mapping is a forced/approximate one.
 *
 * MOBI VID canonical operations:
 *   1. birthAttestation      (VID I)  — anchor a vehicle birth record
 *                                       (VIN hash + credential/content hash).
 *   2. lifecycleEvent        (VID II) — record one lifecycle event
 *                                       (e.g. maintenance/inspection).
 *   3. thirdPartyAttestation          — a second AUTHORIZED party attests to
 *                                       an event/claim (multi-party is core to
 *                                       MOBI VID).
 *
 * Backends (existing contracts, native mapping):
 *   - ERC-1056     : birth/lifecycle = setAttribute (event log);
 *                    attestation = setAttributeSigned (meta-tx) — NOT native
 *                    multi-party (signer must be the owner), recorded honestly.
 *   - ERC-735      : birth/lifecycle = addClaim(topic); attestation = a claim
 *                    carrying a SECOND issuer's on-chain-verified signature
 *                    (NATIVE multi-party).
 *   - ERC-1155     : birth = registerVehicle (BIRTH_CERT mint);
 *                    lifecycle = issueCredential (event-type token, coarse);
 *                    attestation = NO native multi-party (approximation only).
 *   - CVIN-Combined: birth/lifecycle = setAttribute (event log);
 *                    attestation = addClaim (on-chain claim w/ issuer sig).
 *   - MOBI-VID-V2  : purpose-built reference — registerVehicleBirth /
 *                    recordLifecycleEvent / attestEvent (all native;
 *                    attestEvent verifies the attester on-chain).
 *
 * FIDELITY MATRIX (5 concepts, binary native support, summed to a score/5):
 *   birthAnchoring, lifecycleEvents, multiPartyAttestation,
 *   verifiableClaims (O(1) on-chain signed claim), revocation.
 *
 * Output: ../4_comparison-framework/results/mobi_vid_backends.json
 *
 * Run:  npx hardhat run scripts/mobi_vid_backend_sweep.js
 */

const fs = require("fs");
const path = require("path");
const { ethers } = require("hardhat");

// ---------------------------------------------------------------------------
// Fixed keys (deterministic addresses => deterministic calldata => stable gas).
// These are arbitrary valid secp256k1 keys, NOT funded mainnet keys.
// ---------------------------------------------------------------------------
const OWNER_KEY = "0x1111111111111111111111111111111111111111111111111111111111111111";
const MANU_KEY = "0x2222222222222222222222222222222222222222222222222222222222222222";
const INSPECTOR_KEY = "0x3333333333333333333333333333333333333333333333333333333333333333";
const SECOND_ISSUER_KEY = "0x4444444444444444444444444444444444444444444444444444444444444444";

// Shared, fixed test data.
const VIN = "5YJSA1E26MF123456";
const VIN_HASH = ethers.keccak256(ethers.toUtf8Bytes(VIN));
const BIRTH_CERT_HASH = ethers.keccak256(ethers.toUtf8Bytes("ipfs://QmBirthCertificate"));
const EVENT_DATA_HASH = ethers.keccak256(ethers.toUtf8Bytes("ipfs://QmMaintenanceRecord"));
const EVENT_VC_HASH = ethers.keccak256(ethers.toUtf8Bytes("vc:jwt:maintenance-credential"));
const ONE_YEAR = 365 * 24 * 60 * 60;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function gasOf(txPromise) {
  const tx = await txPromise;
  const receipt = await tx.wait();
  return Number(receipt.gasUsed);
}

async function deployWithGas(factory, ...args) {
  const contract = await factory.deploy(...args);
  await contract.waitForDeployment();
  const receipt = await contract.deploymentTransaction().wait();
  return { contract, gasUsed: Number(receipt.gasUsed) };
}

/** One backend x operation cell. */
function cell(gasUsed, nativeSupport, note, approximate = false) {
  return { gasUsed, nativeSupport, approximate, note };
}

// ---------------------------------------------------------------------------
// ERC-1056 (EthereumDIDRegistry) — event-log DID registry
// ---------------------------------------------------------------------------

async function sweepERC1056(signers) {
  const [deployer, funder] = signers;
  const out = {};

  const Factory = await ethers.getContractFactory(
    "contracts/ERC1056/EthereumDIDRegistry.sol:EthereumDIDRegistry",
    deployer
  );
  const { contract: registry } = await deployWithGas(Factory);
  const registryAddr = await registry.getAddress();

  // The vehicle identity is a controlled wallet (every address is a DID that
  // owns itself). Fund it so it can send its own setAttribute txs.
  const owner = new ethers.Wallet(OWNER_KEY, ethers.provider);
  await (await funder.sendTransaction({ to: owner.address, value: ethers.parseEther("1") })).wait();
  const identity = owner.address;
  const regAsOwner = registry.connect(owner);

  // 1. Birth attestation (VID I) -> setAttribute anchoring vinHash + certHash.
  const birthName = ethers.encodeBytes32String("mobi/vid/birth");
  const birthValue = ethers.concat([VIN_HASH, BIRTH_CERT_HASH]); // 64 bytes
  out.birthAttestation = cell(
    await gasOf(regAsOwner.setAttribute(identity, birthName, birthValue, ONE_YEAR)),
    true,
    "setAttribute anchors (vinHash || birthCertHash) as an event-log DID attribute. Native anchoring, but a GENERIC attribute — ERC-1056 has no purpose-built birth-certificate struct; the birth semantics live off-chain in the resolver."
  );

  // 2. Lifecycle event (VID II) -> setAttribute recording one maintenance event.
  const eventName = ethers.encodeBytes32String("mobi/vid/event/maint");
  const eventValue = ethers.concat([EVENT_DATA_HASH, EVENT_VC_HASH]); // 64 bytes
  out.lifecycleEvent = cell(
    await gasOf(regAsOwner.setAttribute(identity, eventName, eventValue, ONE_YEAR)),
    true,
    "Each lifecycle event is appended as a DIDAttributeChanged event (event-log history). Native, cheap, but untyped/unstructured — no odometer/jurisdiction/issuer-role model as in MOBI VID II; those are off-chain."
  );

  // 3. Third-party attestation -> setAttributeSigned (task-suggested mapping),
  //    plus addDelegate measured for context. NEITHER is native multi-party.
  //    setAttributeSigned verifies a signature on-chain, BUT the signer MUST be
  //    the identity owner (a relayer/meta-tx pattern) — it does NOT let an
  //    independent second party attest. Recorded honestly as non-native.
  const attrName = ethers.encodeBytes32String("mobi/vid/attest");
  const attrValue = ethers.toUtf8Bytes("attestation:inspection:pass");
  const signedNonce = await registry.nonce(identity);
  const signedDigest = ethers.solidityPackedKeccak256(
    ["bytes1", "bytes1", "address", "uint256", "address", "string", "bytes32", "bytes", "uint256"],
    ["0x19", "0x00", registryAddr, signedNonce, identity, "setAttribute", attrName, attrValue, ONE_YEAR]
  );
  const s = owner.signingKey.sign(signedDigest);
  const setAttrSignedGas = await gasOf(
    registry.connect(deployer).setAttributeSigned(identity, s.v, s.r, s.s, attrName, attrValue, ONE_YEAR)
  );

  // Context: addDelegate = the on-chain footprint of AUTHORIZING a second party
  // (the attester) to sign off-chain VCs. The attestation content stays off-chain.
  const secondParty = new ethers.Wallet(SECOND_ISSUER_KEY, ethers.provider);
  const delegateType = ethers.encodeBytes32String("sigAuth");
  const addDelegateGas = await gasOf(
    regAsOwner.addDelegate(identity, delegateType, secondParty.address, ONE_YEAR)
  );

  out.thirdPartyAttestation = cell(
    setAttrSignedGas,
    false,
    `NO native on-chain multi-party attestation. Measured (approximation): setAttributeSigned — a signature IS ecrecover-verified on-chain, but the signer MUST be the identity owner (meta-tx/relayer pattern), so it cannot represent an INDEPENDENT second party. Genuine third-party attestations in ERC-1056 are off-chain W3C VCs; the only on-chain step is the owner authorizing an attester via addDelegate (measured: ${addDelegateGas} gas).`,
    true
  );

  out.fidelity = fidelity({
    birthAnchoring: true,      // generic attribute anchor (event log)
    lifecycleEvents: true,     // event-log append
    multiPartyAttestation: false,
    verifiableClaims: false,   // nothing stored on-chain; claims are off-chain VCs
    revocation: true,          // revokeAttribute / revokeDelegate
  });
  return out;
}

// ---------------------------------------------------------------------------
// ERC-735 (CVINVehicleClaimHolder) — on-chain signed claims
// ---------------------------------------------------------------------------

async function sweepERC735(signers) {
  const [owner] = signers; // contract owner anchors claims (MANAGEMENT-key role)
  const out = {};

  const MANUFACTURER_CERT = 2;
  const INSPECTION = 3;
  const INSURANCE = 4;
  const ECDSA_SCHEME = 1;

  const Factory = await ethers.getContractFactory("CVINVehicleClaimHolder", owner);
  const { contract: holder } = await deployWithGas(Factory, VIN);
  const identityAddress = await holder.getAddress();

  // Issuer signs EIP-191 over keccak256(abi.encodePacked(identityAddress, topic, data)).
  async function signClaim(issuerWallet, topic, data) {
    const messageHash = ethers.solidityPackedKeccak256(
      ["address", "uint256", "bytes"],
      [identityAddress, topic, data]
    );
    return issuerWallet.signingKey.sign(
      ethers.hashMessage(ethers.getBytes(messageHash))
    ).serialized;
  }

  const manufacturer = new ethers.Wallet(MANU_KEY);
  const inspector = new ethers.Wallet(INSPECTOR_KEY);
  const insurer = new ethers.Wallet(SECOND_ISSUER_KEY);

  // 1. Birth attestation (VID I) -> manufacturer birth-certificate claim.
  const birthData = ethers.toUtf8Bytes(`birth:${VIN}`);
  const birthSig = await signClaim(manufacturer, MANUFACTURER_CERT, birthData);
  out.birthAttestation = cell(
    await gasOf(holder.addClaim(MANUFACTURER_CERT, ECDSA_SCHEME, manufacturer.address, birthSig, birthData, "ipfs://birth")),
    true,
    "addClaim(MANUFACTURER_CERT): a birth certificate is a first-class ERC-735 claim carrying the manufacturer's issuer signature, ecrecover-verified on-chain and stored O(1)-readable. High-fidelity native mapping."
  );

  // 2. Lifecycle event (VID II) -> periodic inspection claim.
  const inspData = ethers.toUtf8Bytes("inspection:2026-07:pass");
  const inspSig = await signClaim(inspector, INSPECTION, inspData);
  out.lifecycleEvent = cell(
    await gasOf(holder.addClaim(INSPECTION, ECDSA_SCHEME, inspector.address, inspSig, inspData, "ipfs://inspection")),
    true,
    "addClaim(INSPECTION): a lifecycle event modelled as an issuer-signed claim. Native, but claims are keyed by (issuer, topic) — re-issuing the same topic/issuer UPDATES in place rather than appending, so a rich multi-event history needs distinct topics/issuers (unlike MOBI VID II's per-event structs)."
  );

  // 3. Third-party attestation -> a SECOND, distinct issuer (insurer) anchors a
  //    claim carrying THEIR on-chain-verified signature. NATIVE multi-party.
  const insData = ethers.toUtf8Bytes("insurance:coverage:active");
  const insSig = await signClaim(insurer, INSURANCE, insData);
  out.thirdPartyAttestation = cell(
    await gasOf(holder.addClaim(INSURANCE, ECDSA_SCHEME, insurer.address, insSig, insData, "ipfs://insurance")),
    true,
    "addClaim by a SECOND, independent issuer (insurer != manufacturer): the claim carries the third party's ECDSA signature over (identity, topic, data), ecrecover-verified on-chain before storage. This IS native multi-party attestation — the core ERC-735 capability."
  );

  out.fidelity = fidelity({
    birthAnchoring: true,
    lifecycleEvents: true,
    multiPartyAttestation: true,
    verifiableClaims: true,    // on-chain signed claim, O(1) getClaim
    revocation: true,          // removeClaim (owner or issuer)
  });
  return out;
}

// ---------------------------------------------------------------------------
// ERC-1155 (CVINVehicleCredential1155) — multi-token credentials
// ---------------------------------------------------------------------------

async function sweepERC1155(signers) {
  const [deployer, vehicle, secondIssuer] = signers;
  const out = {};

  const MAINTENANCE_BADGE = 5;
  const INSPECTION_CERT = 3;

  const Factory = await ethers.getContractFactory("CVINVehicleCredential1155", deployer);
  const { contract: credential } = await deployWithGas(Factory);

  // 1. Birth attestation (VID I) -> registerVehicle mints one soulbound BIRTH_CERT.
  out.birthAttestation = cell(
    await gasOf(credential.registerVehicle(vehicle.address, VIN)),
    true,
    "registerVehicle mints a soulbound BIRTH_CERT token + binds VIN/vinHash. Holding the token IS the birth anchor. Native, high fidelity (though the on-chain anchor is a token balance, not a signed certificate — the cert hash/data live off-chain)."
  );

  // 2. Lifecycle event (VID II) -> mint an event-type credential token.
  out.lifecycleEvent = cell(
    await gasOf(credential.issueCredential(vehicle.address, MAINTENANCE_BADGE, 1)),
    true,
    "issueCredential(MAINTENANCE_BADGE): a lifecycle event is represented by minting an event-type credential token. Native but COARSE — records that an event-type occurred, with no on-chain odometer/timestamp/data-hash/issuer-role struct (only the Transfer log carries block/issuer); distinct repeated events collapse into a balance."
  );

  // 3. Third-party attestation -> NO native multi-party attestation.
  //    Approximation: authorize a SECOND issuer (setup, excluded) who mints a
  //    corroborating credential. This is a PARALLEL issuance, not an attestation
  //    bound to a specific prior event, and carries no signature/linkage.
  const ISSUER_ROLE = await credential.ISSUER_ROLE();
  await (await credential.grantRole(ISSUER_ROLE, secondIssuer.address)).wait(); // setup, not counted
  const approxGas = await gasOf(
    credential.connect(secondIssuer).issueCredential(vehicle.address, INSPECTION_CERT, 1)
  );
  out.thirdPartyAttestation = cell(
    approxGas,
    false,
    "NO native multi-party attestation. Measured (approximation, NOT a faithful mapping): a second authorized ISSUER_ROLE holder mints a corroborating INSPECTION_CERT. This is an independent parallel issuance — it is NOT bound to any specific prior event, carries no attester signature, and creates no on-chain linkage between the two parties' statements. ERC-1155 has no attest-to-an-event primitive.",
    true
  );

  out.fidelity = fidelity({
    birthAnchoring: true,
    lifecycleEvents: true,     // coarse credential-token issuance
    multiPartyAttestation: false,
    verifiableClaims: false,   // token balance, not a signed on-chain claim struct
    revocation: true,          // revokeCredential (burn)
  });
  return out;
}

// ---------------------------------------------------------------------------
// CVIN-Combined (CVINCombinedIdentity) — event log + on-chain claims hybrid
// ---------------------------------------------------------------------------

async function sweepCVINCombined(signers) {
  const [, identityOwner] = signers; // every address self-owns its DID
  const out = {};

  const CLAIM_TOPIC_MANUFACTURER = 2;
  const SCHEME_ECDSA = 1;

  const Factory = await ethers.getContractFactory("CVINCombinedIdentity", signers[0]);
  const { contract: registry } = await deployWithGas(Factory);
  const registryAddr = await registry.getAddress();
  const identity = identityOwner.address;
  const reg = registry.connect(identityOwner);

  // 1. Birth attestation (VID I) -> setAttribute (cheap event-log anchor).
  const birthName = ethers.keccak256(ethers.toUtf8Bytes("mobi/vid/birth"));
  const birthValue = ethers.concat([VIN_HASH, BIRTH_CERT_HASH]);
  out.birthAttestation = cell(
    await gasOf(reg.setAttribute(identity, birthName, birthValue, ONE_YEAR)),
    true,
    "setAttribute anchors (vinHash || birthCertHash) as an ERC-1056-style event (cheap common path). Native anchoring via the hybrid's event-log side."
  );

  // 2. Lifecycle event (VID II) -> setAttribute event-log append.
  const eventName = ethers.keccak256(ethers.toUtf8Bytes("mobi/vid/event/maint"));
  const eventValue = ethers.concat([EVENT_DATA_HASH, EVENT_VC_HASH]);
  out.lifecycleEvent = cell(
    await gasOf(reg.setAttribute(identity, eventName, eventValue, ONE_YEAR)),
    true,
    "Lifecycle events appended via the ERC-1056-style event log (cheap). Structured event semantics (odometer/role) remain off-chain, unlike MOBI VID II."
  );

  // 3. Third-party attestation -> addClaim: a second issuer's signature verified
  //    on-chain and stored O(1). NATIVE multi-party (the hybrid's ERC-735 side).
  const issuer = new ethers.Wallet(SECOND_ISSUER_KEY);
  const claimData = ethers.toUtf8Bytes(`manufacturer-attest:${VIN}`);
  const digest = ethers.solidityPackedKeccak256(
    ["address", "address", "uint256", "bytes"],
    [registryAddr, identity, CLAIM_TOPIC_MANUFACTURER, claimData]
  );
  const signature = ethers.Signature.from(issuer.signingKey.sign(digest)).serialized;
  out.thirdPartyAttestation = cell(
    await gasOf(
      reg.addClaim(identity, CLAIM_TOPIC_MANUFACTURER, SCHEME_ECDSA, issuer.address, signature, claimData, "ipfs://attest")
    ),
    true,
    "addClaim (hybrid's ERC-735 side): a second issuer's ECDSA signature over (registry, identity, topic, data) is ecrecover-verified on-chain and the claim is stored for O(1) verification. Native multi-party attestation — paid only when a safety-critical on-chain claim is actually needed."
  );

  out.fidelity = fidelity({
    birthAnchoring: true,
    lifecycleEvents: true,
    multiPartyAttestation: true,
    verifiableClaims: true,    // on-chain addClaim with issuer sig
    revocation: true,          // revokeAttribute + removeClaim
  });
  return out;
}

// ---------------------------------------------------------------------------
// MOBI-VID-V2 (MOBIVIDRegistryV2) — purpose-built reference (everything native)
// ---------------------------------------------------------------------------

async function sweepMOBIVIDV2(signers) {
  const [deployer, firstOwner, serviceCenter, dmv, vehicleWallet] = signers;
  const out = {};

  const Factory = await ethers.getContractFactory("MOBIVIDRegistryV2", deployer);
  const { contract: registry } = await deployWithGas(Factory);
  const vehicleIdentity = vehicleWallet.address;

  // 1. Birth attestation (VID I) -> registerVehicleBirth (purpose-built).
  //    birthAttributes left "0x" (documented V1 validity-overflow workaround in
  //    benchmark_gas.js; the birth anchor is vinHash + certHash regardless).
  out.birthAttestation = cell(
    await gasOf(
      registry.registerVehicleBirth(
        vehicleIdentity, VIN_HASH, "encrypted:AES256:VINCIPHERTEXT==", BIRTH_CERT_HASH,
        firstOwner.address, "0x"
      )
    ),
    true,
    "registerVehicleBirth (MOBI VID I): purpose-built birth certificate — salted VIN hash + encrypted VIN + cert hash + first owner + manufacturer, in a dedicated on-chain struct with VIN-hash lookup index. Highest-fidelity native mapping (the reference)."
  );

  // 2. Lifecycle event (VID II) -> recordLifecycleEvent (purpose-built).
  await (await registry.authorizeIssuer(serviceCenter.address, 3 /* SERVICE_CENTER */)).wait(); // setup
  const eventTx = registry.connect(serviceCenter).recordLifecycleEvent(
    vehicleIdentity, 0 /* MAINTENANCE */, 15000, EVENT_DATA_HASH, EVENT_VC_HASH, "BC-CAN"
  );
  const eventReceipt = await (await eventTx).wait();
  out.lifecycleEvent = cell(
    Number(eventReceipt.gasUsed),
    true,
    "recordLifecycleEvent (MOBI VID II, MAINTENANCE): dedicated event struct with eventType, issuer, timestamp, odometer, dataHash, W3C-VC hash, verified flag, jurisdiction, block number + per-type counters. Highest-fidelity native mapping (11 event types, issuer-role gating)."
  );
  const eventId = (await registry.getVehicleEvents(vehicleIdentity))[0];

  // 3. Third-party attestation -> attestEvent (on-chain signature verification).
  await (await registry.authorizeIssuer(dmv.address, 5 /* GOVERNMENT_DMV */)).wait(); // setup
  const chainId = (await ethers.provider.getNetwork()).chainId;
  const attestInner = ethers.solidityPackedKeccak256(
    ["address", "uint256", "address", "bytes32"],
    [await registry.getAddress(), chainId, vehicleIdentity, eventId]
  );
  const attestSig = await dmv.signMessage(ethers.getBytes(attestInner));
  out.thirdPartyAttestation = cell(
    await gasOf(registry.connect(dmv).attestEvent(eventId, vehicleIdentity, attestSig)),
    true,
    "attestEvent by a second authorized party (DMV): the attester's EIP-191 signature over a domain-separated digest (contract || chainId || vehicle || eventId) is ecrecover-verified on-chain (OZ ECDSA, low-s) and MUST match msg.sender; the verified attestation is appended to the event. Native, purpose-built multi-party attestation."
  );

  out.fidelity = fidelity({
    birthAnchoring: true,
    lifecycleEvents: true,
    multiPartyAttestation: true,
    verifiableClaims: true,    // verified attestations + on-chain VC hash + verified flag
    revocation: true,          // revokeIdentity + revokeIssuerAuthorization
  });
  return out;
}

// ---------------------------------------------------------------------------
// Fidelity scoring
// ---------------------------------------------------------------------------

const FIDELITY_CONCEPTS = [
  "birthAnchoring",
  "lifecycleEvents",
  "multiPartyAttestation",
  "verifiableClaims",
  "revocation",
];

function fidelity(flags) {
  const score = FIDELITY_CONCEPTS.reduce((n, c) => n + (flags[c] ? 1 : 0), 0);
  return { ...flags, score, outOf: FIDELITY_CONCEPTS.length };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const signers = await ethers.getSigners();
  const network = await ethers.provider.getNetwork();

  console.log("MOBI VID cross-backend realization sweep (H4)");
  console.log(`Network: ${network.name} (chainId ${network.chainId})\n`);

  const backends = {};
  console.log("Sweeping ERC-1056 ...");
  backends["ERC-1056"] = await sweepERC1056(signers);
  console.log("Sweeping ERC-735 ...");
  backends["ERC-735"] = await sweepERC735(signers);
  console.log("Sweeping ERC-1155 ...");
  backends["ERC-1155"] = await sweepERC1155(signers);
  console.log("Sweeping CVIN-Combined ...");
  backends["CVIN-Combined"] = await sweepCVINCombined(signers);
  console.log("Sweeping MOBI-VID-V2 ...");
  backends["MOBI-VID-V2"] = await sweepMOBIVIDV2(signers);

  const output = {
    backends,
    metadata: {
      title: "MOBI VID cross-backend realization (H4)",
      solcVersion: "0.8.24",
      solcSettings: { optimizer: { enabled: true, runs: 200 }, viaIR: true },
      ozVersion: "5.0.2",
      date: new Date().toISOString(),
      network: "hardhat-local",
      chainId: Number(network.chainId),
      operations: ["birthAttestation", "lifecycleEvent", "thirdPartyAttestation"],
      operationLabels: {
        birthAttestation: "Birth attestation (VID I)",
        lifecycleEvent: "Lifecycle event (VID II)",
        thirdPartyAttestation: "Third-party attestation",
      },
      fidelityConcepts: FIDELITY_CONCEPTS,
      contracts: {
        "ERC-1056": "contracts/ERC1056/EthereumDIDRegistry.sol:EthereumDIDRegistry",
        "ERC-735": "contracts/ERC735/CVINVehicleClaimHolder.sol:CVINVehicleClaimHolder",
        "ERC-1155": "contracts/ERC1155/CVINVehicleCredential1155.sol:CVINVehicleCredential1155",
        "CVIN-Combined": "contracts/CVINCombined/CVINCombinedIdentity.sol:CVINCombinedIdentity",
        "MOBI-VID-V2": "contracts/MOBI/MOBIVIDRegistryV2.sol:MOBIVIDRegistryV2",
      },
      notes:
        "gasUsed is the exact receipt.gasUsed of one representative transaction per (backend, operation) on a fresh Hardhat in-process network, using each backend's EXISTING contract and NATIVE primitives. nativeSupport=false + approximate=true marks a forced/approximate mapping where the backend genuinely lacks the concept (see per-cell note); its gas is the closest honest analogue, NOT a faithful realization. Setup txs (issuer authorization, role grants, wallet funding) are excluded from operation gas. Fidelity score = count of natively-supported concepts out of 5 (birthAnchoring, lifecycleEvents, multiPartyAttestation, verifiableClaims, revocation).",
    },
  };

  const outDir = path.resolve(__dirname, "../../4_comparison-framework/results");
  fs.mkdirSync(outDir, { recursive: true });
  const outFile = path.join(outDir, "mobi_vid_backends.json");
  fs.writeFileSync(outFile, JSON.stringify(output, null, 2));

  // Console summary
  console.log("\n=== MOBI VID x backend: gas (nativeSupport) ===");
  const ops = output.metadata.operations;
  console.log(["backend", ...ops, "fidelity"].join("\t"));
  for (const [name, b] of Object.entries(backends)) {
    const row = [name];
    for (const o of ops) {
      const c = b[o];
      const g = c.gasUsed === null ? "null" : String(c.gasUsed);
      row.push(`${g}${c.nativeSupport ? "" : c.approximate ? "~" : "(x)"}`);
    }
    row.push(`${b.fidelity.score}/${b.fidelity.outOf}`);
    console.log(row.join("\t"));
  }
  console.log("\n(~ = approximate/non-native mapping; see JSON notes)");
  console.log(`\nResults written to ${outFile}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
