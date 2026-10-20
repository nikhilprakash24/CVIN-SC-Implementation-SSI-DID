/**
 * benchmark_scaling.js
 *
 * Scaling & lifetime-cost study for the connected-vehicle identity standards
 * (design: docs/SCALING_EXPERIMENTS.md, addresses RESEARCH_AUDIT.md §4.8).
 *
 * Experiment A — Marginal-cost stationarity (RQ-S1)
 *   On a FRESH deployment of each standard, perform K = 50 sequential same-type
 *   "append to history" operations with a FIXED-SIZE payload and the SAME actor;
 *   record the exact receipt.gasUsed for every i in [1, 50]. Fit a least-squares
 *   line of gasUsed vs operation index; report slope (gas/op) and R^2. Slope ~= 0
 *   (or negative) => O(1) marginal cost; a sustained positive slope with high R^2
 *   => history-dependent degradation (disqualifying at automotive lifetimes).
 *
 *   Per-standard append operation (grounded in the real contract ABI):
 *     ERC-1056       : setAttribute            (event-log; no array growth)
 *     ERC-735        : addClaim                (mapping + topic-id array push)
 *     ERC-1155       : issueCredential         (mint a credential token)
 *     CVIN-Combined  : addClaim                (mapping + per-identity topic array push)
 *     MOBI-VID-V2    : recordLifecycleEvent    (events array append + counters)
 *
 * Experiment B — Lifetime cost model (RQ-S2)
 *   Integrate the measured per-op costs (Experiment A steady-state marginals +
 *   the birth/transfer costs from results/gas_benchmark.json) over the canonical
 *   15-year vehicle profile from the design:
 *     1 birth + 30 maintenance + 3 transfers + 4 inspections + 1 recall = 39 events.
 *   Report a per-standard lifetime total, decomposed by event class where the
 *   standard distinguishes them (else the generic append cost), with a +/-50%
 *   event-frequency sensitivity band. This is explicitly a MODEL over an assumed
 *   profile (see docs/SCALING_EXPERIMENTS.md "Validity notes").
 *
 * Outputs:
 *   ../4_comparison-framework/results/scaling_marginal.json   (Experiment A)
 *   ../4_comparison-framework/results/scaling_lifetime.json   (Experiment B)
 *
 * Run:  npx hardhat run scripts/benchmark_scaling.js
 */

const fs = require("fs");
const path = require("path");
const { ethers } = require("hardhat");

const K = 50; // sequential append operations per standard (Experiment A)

// ---------------------------------------------------------------------------
// Helpers (mirroring scripts/benchmark_gas.js)
// ---------------------------------------------------------------------------

/** Execute a tx-returning promise and return its gasUsed as a Number. */
async function gasOf(txPromise) {
  const tx = await txPromise;
  const receipt = await tx.wait();
  return Number(receipt.gasUsed);
}

/** Deploy a contract and return { contract, gasUsed }. */
async function deployWithGas(factory, ...args) {
  const contract = await factory.deploy(...args);
  await contract.waitForDeployment();
  const receipt = await contract.deploymentTransaction().wait();
  return { contract, gasUsed: Number(receipt.gasUsed) };
}

/**
 * Least-squares fit of y (indexed x = 1..n). Returns exact/deterministic
 * slope (gas per op), intercept, R^2, mean, first, last, delta.
 * These are deterministic gas figures, so slope/R^2 are exact, not estimates.
 */
function linregStats(ys) {
  const n = ys.length;
  const xs = Array.from({ length: n }, (_, i) => i + 1);
  let sx = 0, sy = 0, sxy = 0, sxx = 0;
  for (let i = 0; i < n; i++) {
    sx += xs[i];
    sy += ys[i];
    sxy += xs[i] * ys[i];
    sxx += xs[i] * xs[i];
  }
  const denom = n * sxx - sx * sx;
  const slope = denom === 0 ? 0 : (n * sxy - sx * sy) / denom;
  const intercept = (sy - slope * sx) / n;
  const mean = sy / n;
  let ssTot = 0, ssRes = 0;
  for (let i = 0; i < n; i++) {
    const pred = slope * xs[i] + intercept;
    ssRes += (ys[i] - pred) ** 2;
    ssTot += (ys[i] - mean) ** 2;
  }
  // ssTot == 0 => perfectly flat series => O(1) with a perfect (degenerate) fit.
  const r2 = ssTot === 0 ? 1 : 1 - ssRes / ssTot;
  const first = ys[0];
  const last = ys[n - 1];
  return {
    first,
    last,
    delta: last - first,
    slope,
    intercept,
    r2,
    mean,
    min: Math.min(...ys),
    max: Math.max(...ys),
  };
}

/**
 * Classify marginal cost. History-dependent degradation requires a POSITIVE
 * slope that is (a) meaningful relative to the per-op cost and (b) explains a
 * real fraction of the variance. A zero/negative slope (e.g. a one-off cold
 * first-write that is cheaper thereafter) is O(1): cost does not grow with
 * history. Small positive slopes from per-op calldata-byte jitter (low R^2)
 * are noise, not growth.
 */
function classify(stats) {
  const relDriftPerOp = stats.mean !== 0 ? stats.slope / stats.mean : 0;
  const totalRelDrift = relDriftPerOp * (K - 1); // projected drift across the run
  const degrading = stats.slope > 0 && totalRelDrift > 0.02 && stats.r2 > 0.5;
  return {
    constantMarginalCost: !degrading,
    order: degrading ? "O(n) (history-dependent)" : "O(1)",
    relDriftPerOp, // slope as a fraction of mean per op
    totalRelDrift, // projected relative change over the 50-op run
  };
}

// ---------------------------------------------------------------------------
// Experiment A — per-standard append sequences
// ---------------------------------------------------------------------------

// ---- ERC-1056: setAttribute (event-log, no array growth) ----
async function scaleERC1056(signers) {
  const [deployer, identityOwner] = signers;
  const Factory = await ethers.getContractFactory(
    "contracts/ERC1056/EthereumDIDRegistry.sol:EthereumDIDRegistry",
    deployer
  );
  const { contract: registry } = await deployWithGas(Factory);
  const reg = registry.connect(identityOwner);

  const identity = identityOwner.address; // every address is a DID
  const attrName = ethers.encodeBytes32String("did/pub/Secp256k1/veriKey");
  const attrValue = ethers.toUtf8Bytes(
    "0x02b97c30de767f084ce3080168ee293053ba33b235d7116a3263d29f1450936b71"
  ); // fixed 68-byte payload, identical every op
  const oneYear = 365 * 24 * 60 * 60;

  const gas = [];
  const revert = null;
  for (let i = 0; i < K; i++) {
    gas.push(await gasOf(reg.setAttribute(identity, attrName, attrValue, oneYear)));
  }
  return {
    op: "setAttribute",
    contract: "contracts/ERC1056/EthereumDIDRegistry.sol:EthereumDIDRegistry",
    actor: "identityOwner (fixed)",
    payload: "fixed bytes32 name + 68-byte value + 1-year validity, identical each op",
    historyStructure:
      "event-only (DIDAttributeChanged); the only storage write is the per-identity `changed` block pointer, so no on-chain array grows.",
    gas,
    revert,
  };
}

// ---- MOBI-VID-V2: recordLifecycleEvent (events array append + counters) ----
async function scaleMOBIVIDV2(signers) {
  const [deployer, , serviceCenter, , vehicleWallet, firstOwner] = signers;
  const Factory = await ethers.getContractFactory("MOBIVIDRegistryV2", deployer);
  const { contract: registry } = await deployWithGas(Factory);

  const vehicleIdentity = vehicleWallet.address;
  const vin = "5YJSA1E26MF123456";
  const vinHash = ethers.keccak256(ethers.toUtf8Bytes(vin));

  // Setup (not part of the measured sequence): birth certificate + issuer role.
  // birthAttributes MUST be "0x" (non-empty triggers the known inherited V1
  // validity-overflow revert; see benchmark_gas.js).
  await (
    await registry.registerVehicleBirth(
      vehicleIdentity,
      vinHash,
      "encrypted:AES256:VINCIPHERTEXT==",
      ethers.keccak256(ethers.toUtf8Bytes("ipfs://QmBirthCertificate")),
      firstOwner.address,
      "0x"
    )
  ).wait();
  await (await registry.authorizeIssuer(serviceCenter.address, 3 /* SERVICE_CENTER */)).wait();

  // recordLifecycleEvent does NOT require a signature (only attestEvent does),
  // so the append op is a plain authorized-issuer call with a fixed payload.
  const dataHash = ethers.keccak256(ethers.toUtf8Bytes("ipfs://QmMaintenanceRecord"));
  const credHash = ethers.keccak256(ethers.toUtf8Bytes("vc:jwt:maintenance-credential"));
  const svc = registry.connect(serviceCenter);

  const gas = [];
  let revert = null;
  for (let i = 0; i < K; i++) {
    try {
      gas.push(
        await gasOf(
          svc.recordLifecycleEvent(
            vehicleIdentity,
            0, // EventType.MAINTENANCE (fixed)
            15000, // odometer (fixed)
            dataHash,
            credHash,
            "BC-CAN"
          )
        )
      );
    } catch (e) {
      revert = { atIndex: i + 1, reason: (e && e.message) || String(e) };
      break;
    }
  }
  return {
    op: "recordLifecycleEvent",
    contract: "contracts/MOBI/MOBIVIDRegistryV2.sol:MOBIVIDRegistryV2",
    actor: "authorized SERVICE_CENTER issuer (fixed)",
    payload: "fixed EventType.MAINTENANCE + odometer + dataHash + credentialHash + jurisdiction, identical each op",
    historyStructure:
      "per-vehicle vehicleEventIds[] array push + full LifecycleEvent struct at a fresh unique eventId + eventCount/eventTypeCount increments. Array push is O(1); recordLifecycleEvent does not iterate history.",
    gas,
    revert,
  };
}

// ---- ERC-1155: issueCredential (mint a credential token) ----
async function scaleERC1155(signers) {
  const [deployer, vehicle] = signers;
  const Factory = await ethers.getContractFactory("CVINVehicleCredential1155", deployer);
  const { contract: credential } = await deployWithGas(Factory);

  const VIN = "1HGBH41JXMN109186";
  const INSPECTION_CERT = 3;

  // Setup: register the vehicle identity (mints its BIRTH_CERT).
  await (await credential.registerVehicle(vehicle.address, VIN)).wait();

  const gas = [];
  const revert = null;
  for (let i = 0; i < K; i++) {
    // Same actor (ISSUER_ROLE = deployer), same credential type + amount each op.
    gas.push(await gasOf(credential.issueCredential(vehicle.address, INSPECTION_CERT, 1)));
  }
  return {
    op: "issueCredential",
    contract: "contracts/ERC1155/CVINVehicleCredential1155.sol:CVINVehicleCredential1155",
    actor: "ISSUER_ROLE holder (fixed)",
    payload: "fixed credentialType=INSPECTION_CERT, amount=1, identical each op",
    historyStructure:
      "ERC-1155 stores balances only (no per-event history array): issuance is a single _balances[id][holder] += amount SSTORE. Inherently O(1); the first mint pays the cold-slot (0->1) cost, later mints are warm.",
    gas,
    revert,
  };
}

// ---- ERC-735: addClaim (mapping + topic-id array push) ----
async function scaleERC735(signers) {
  const [, vehicleOwner] = signers;
  const VIN = "1HGBH41JXMN109186";
  const ECDSA_SCHEME = 1;
  const TOPIC = 1; // VIN_ATTESTATION (fixed topic => a single topic array grows to K)

  const Factory = await ethers.getContractFactory("CVINVehicleClaimHolder", vehicleOwner);
  const { contract: holder } = await deployWithGas(Factory, VIN);
  const identityAddress = await holder.getAddress();

  // Fixed-size claim payload. Issuer varies across 50 deterministic wallets so
  // each addClaim inserts a NEW claim (distinct claimId = keccak(issuer,topic))
  // and pushes onto the SAME claimIdsByTopic[TOPIC] array -- i.e. the array
  // under test grows 1..K. The transaction actor (owner) is held constant.
  const data = ethers.toUtf8Bytes("VIN:1HGBH41JXMN109186"); // fixed size every op
  const uri = "ipfs://vin-attestation-fixed"; // fixed size every op

  const gas = [];
  const revert = null;
  for (let i = 0; i < K; i++) {
    const issuer = new ethers.Wallet(
      ethers.keccak256(ethers.toUtf8Bytes("cvin-scaling-erc735-issuer-" + i))
    );
    // ERC-735 verifies an EIP-191 (eth_sign) signature over
    // keccak256(abi.encodePacked(address(this), topic, data)).
    const messageHash = ethers.solidityPackedKeccak256(
      ["address", "uint256", "bytes"],
      [identityAddress, TOPIC, data]
    );
    const signature = await issuer.signMessage(ethers.getBytes(messageHash));
    gas.push(
      await gasOf(holder.addClaim(TOPIC, ECDSA_SCHEME, issuer.address, signature, data, uri))
    );
  }
  return {
    op: "addClaim",
    contract: "contracts/ERC735/CVINVehicleClaimHolder.sol:CVINVehicleClaimHolder",
    actor: "identity owner (fixed); issuer varies to grow the topic array",
    payload:
      "fixed topic + fixed-size data + fixed-size URI + fixed-length 65-byte issuer signature; issuer address/signature bytes vary per op (unavoidable to create distinct claims), a few gas of calldata jitter.",
    historyStructure:
      "full Claim struct stored at a fresh claimId + push onto claimIdsByTopic[topic] (a single array grown to K). addClaim does not iterate; only removeClaim scans.",
    gas,
    revert,
  };
}

// ---- CVIN-Combined: addClaim (mapping + per-identity topic array push) ----
async function scaleCVINCombined(signers) {
  const [deployer, identityOwner] = signers;
  const CLAIM_TOPIC_VIN = 1;
  const SCHEME_ECDSA = 1;

  const Factory = await ethers.getContractFactory("CVINCombinedIdentity", deployer);
  const { contract: registry } = await deployWithGas(Factory);
  const reg = registry.connect(identityOwner);
  const registryAddress = await registry.getAddress();
  const identity = identityOwner.address;

  // Fixed-size payload; issuer varies across 50 deterministic wallets so each
  // addClaim inserts a NEW claim and pushes onto the SAME
  // _claimIdsByTopic[identity][TOPIC] array (grows 1..K). Actor (owner) fixed.
  const vinData = ethers.toUtf8Bytes("1HGCM82633A004352"); // fixed size every op
  const uri = "ipfs://QmVinAttestation-fixed"; // fixed size every op

  const gas = [];
  const revert = null;
  for (let i = 0; i < K; i++) {
    const issuer = new ethers.Wallet(
      ethers.keccak256(ethers.toUtf8Bytes("cvin-scaling-combined-issuer-" + i))
    );
    // CVIN-Combined verifies a RAW (non-EIP-191) ecrecover over
    // keccak256(abi.encodePacked(address(this), identity, topic, data)).
    const digest = ethers.solidityPackedKeccak256(
      ["address", "address", "uint256", "bytes"],
      [registryAddress, identity, CLAIM_TOPIC_VIN, vinData]
    );
    const signature = ethers.Signature.from(issuer.signingKey.sign(digest)).serialized;
    gas.push(
      await gasOf(
        reg.addClaim(
          identity,
          CLAIM_TOPIC_VIN,
          SCHEME_ECDSA,
          issuer.address,
          signature,
          vinData,
          uri
        )
      )
    );
  }
  return {
    op: "addClaim",
    contract: "contracts/CVINCombined/CVINCombinedIdentity.sol:CVINCombinedIdentity",
    actor: "identity owner (fixed); issuer varies to grow the topic array",
    payload:
      "fixed topic + fixed-size data + fixed-size URI + fixed-length 65-byte issuer signature; issuer address/signature bytes vary per op (unavoidable to create distinct claims), a few gas of calldata jitter.",
    historyStructure:
      "full Claim struct stored at a fresh claimId + push onto _claimIdsByTopic[identity][topic] (a single array grown to K) + `changed` pointer bump. addClaim does not iterate.",
    gas,
    revert,
  };
}

// ---------------------------------------------------------------------------
// Experiment B — lifetime cost model
// ---------------------------------------------------------------------------

/**
 * Canonical 15-year vehicle profile (docs/SCALING_EXPERIMENTS.md). Stated as an
 * assumption and varied +/-50% for the sensitivity band. birth is exactly once
 * per vehicle (its frequency does not vary); the recurring classes scale.
 */
const LIFETIME_PROFILE = {
  birth: 1,
  maintenance: 30, // 2/yr x 15
  inspection: 4,
  recall: 1,
  transfer: 3,
};

function buildLifetimeModel(marginalStandards, gasBenchmark) {
  // append classes recorded via the standard's generic "append" op
  const appendCount =
    LIFETIME_PROFILE.maintenance + LIFETIME_PROFILE.inspection + LIFETIME_PROFILE.recall; // 35
  const transferCount = LIFETIME_PROFILE.transfer; // 3
  const birthCount = LIFETIME_PROFILE.birth; // 1

  const standards = {};
  for (const [name, m] of Object.entries(marginalStandards)) {
    const gb = gasBenchmark[name];
    // Steady-state append marginal = mean of ops 2..K (excludes the one-off cold
    // first write, which is already charged separately as the birth op).
    const tail = m.gas.slice(1);
    const appendMarginal = Math.round(tail.reduce((a, b) => a + b, 0) / tail.length);
    // Birth = the standard's identity-creation cost (a distinct on-chain event class).
    const birthUnit = gb.createIdentity.gasUsed;
    // Transfer = the standard's ownership-transfer cost (a distinct event class).
    const transferUnit = gb.transferOwnership.gasUsed;

    const birthSubtotal = birthCount * birthUnit;
    const appendSubtotal = appendCount * appendMarginal;
    const transferSubtotal = transferCount * transferUnit;
    const total = birthSubtotal + appendSubtotal + transferSubtotal;

    // +/-50% event-frequency sensitivity: scale recurring (append + transfer)
    // load; birth is fixed (exactly one per vehicle). Model => fractional counts.
    const lifetimeAt = (f) =>
      Math.round(
        birthSubtotal + f * appendCount * appendMarginal + f * transferCount * transferUnit
      );

    standards[name] = {
      appendOp: m.op,
      decomposition: {
        birth: { count: birthCount, unitGas: birthUnit, subtotalGas: birthSubtotal, source: "gas_benchmark.createIdentity" },
        appends: {
          classes: ["maintenance", "inspection", "recall"],
          count: appendCount,
          unitGas: appendMarginal,
          subtotalGas: appendSubtotal,
          source: `Experiment A steady-state marginal of ${m.op} (mean of ops 2..${K})`,
        },
        transfers: { count: transferCount, unitGas: transferUnit, subtotalGas: transferSubtotal, source: "gas_benchmark.transferOwnership" },
      },
      distinguishesEventClasses:
        name === "MOBI-VID-V2"
          ? "yes: birth (registerVehicleBirth), lifecycle events (recordLifecycleEvent, class-independent cost), transfer (transferVehicleOwnership)"
          : "partial: birth (createIdentity) and transfer (ownership op) are distinct on-chain ops; maintenance/inspection/recall collapse to the generic append op (the standard does not type them on-chain)",
      totalLifetimeGas: total,
      sensitivityBand: {
        note: "+/-50% event frequency on the recurring (append + transfer) load; birth fixed at 1.",
        low: lifetimeAt(0.5),
        base: total,
        high: lifetimeAt(1.5),
      },
    };
  }
  return { appendCount, transferCount, birthCount, standards };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const signers = await ethers.getSigners();
  const network = await ethers.provider.getNetwork();

  console.log("CVIN scaling & lifetime-cost study (Experiments A + B)");
  console.log(`Network: ${network.name} (chainId ${network.chainId}); K = ${K}\n`);

  const runners = {
    "ERC-1056": scaleERC1056,
    "ERC-735": scaleERC735,
    "ERC-1155": scaleERC1155,
    "CVIN-Combined": scaleCVINCombined,
    "MOBI-VID-V2": scaleMOBIVIDV2,
  };

  const marginalStandards = {};
  for (const [name, fn] of Object.entries(runners)) {
    process.stdout.write(`Experiment A: ${name} ... `);
    const raw = await fn(signers);
    const stats = linregStats(raw.gas);
    const cls = classify(stats);
    marginalStandards[name] = { ...raw, ...stats, ...cls };
    console.log(
      `op=${raw.op} first=${stats.first} 50th=${stats.last} ` +
        `delta=${stats.delta} slope=${stats.slope.toFixed(2)} gas/op ` +
        `R2=${stats.r2.toFixed(4)} -> ${cls.order}` +
        (raw.revert ? ` [REVERT @${raw.revert.atIndex}]` : "")
    );
  }

  const chainId = Number((await ethers.provider.getNetwork()).chainId);
  const metadata = {
    experiment: "A -- marginal-cost stationarity (RQ-S1)",
    design: "docs/SCALING_EXPERIMENTS.md",
    solcVersion: "0.8.24",
    solcSettings: { optimizer: { enabled: true, runs: 200 }, viaIR: true },
    ozVersion: "5.0.2",
    K,
    date: new Date().toISOString(),
    network: "hardhat-local",
    chainId,
    note:
      "gasUsed is the exact receipt.gasUsed of each sequential append op on a fresh in-process Hardhat chain per standard. Slope/R^2 are exact least-squares fits of gasUsed vs op index (deterministic, not statistical estimates). A one-off higher first op that is flat thereafter is O(1) (a cold-slot first write), not degradation. For ERC-735/CVIN-Combined the issuer varies to create distinct claims that grow the topic array; payload sizes are held fixed, so only a few gas of per-op calldata jitter results.",
  };

  const outDir = path.resolve(__dirname, "../../4_comparison-framework/results");
  fs.mkdirSync(outDir, { recursive: true });

  const marginalOut = { metadata, standards: marginalStandards };
  const marginalFile = path.join(outDir, "scaling_marginal.json");
  fs.writeFileSync(marginalFile, JSON.stringify(marginalOut, null, 2));
  console.log(`\nExperiment A written to ${marginalFile}`);

  // ---- Experiment B: lifetime model over gas_benchmark.json + A marginals ----
  const gasBenchmarkPath = path.join(outDir, "gas_benchmark.json");
  const gasBenchmark = JSON.parse(fs.readFileSync(gasBenchmarkPath, "utf-8"));
  const model = buildLifetimeModel(marginalStandards, gasBenchmark);

  const ranked = Object.entries(model.standards)
    .map(([name, s]) => ({ name, total: s.totalLifetimeGas }))
    .sort((a, b) => a.total - b.total);

  const lifetimeOut = {
    metadata: {
      experiment: "B -- lifetime cost MODEL (RQ-S2)",
      design: "docs/SCALING_EXPERIMENTS.md",
      disclaimer:
        "This is a MODEL over an ASSUMED event profile, not a measurement. Totals integrate measured per-op gas (Experiment A steady-state append marginals + gas_benchmark.json birth/transfer costs) across the canonical profile. Gas is relative on-chain work, not fiat (RESEARCH_AUDIT.md §4.1). The profile is an assumption; the +/-50% band varies recurring event frequency.",
      solcVersion: "0.8.24",
      ozVersion: "5.0.2",
      date: new Date().toISOString(),
      network: "hardhat-local",
      chainId,
      profile: LIFETIME_PROFILE,
      profileTotalEvents:
        LIFETIME_PROFILE.birth +
        LIFETIME_PROFILE.maintenance +
        LIFETIME_PROFILE.inspection +
        LIFETIME_PROFILE.recall +
        LIFETIME_PROFILE.transfer,
      counts: {
        birth: model.birthCount,
        appends: model.appendCount,
        transfers: model.transferCount,
      },
      sources: {
        appendMarginal: "scaling_marginal.json (mean of ops 2..K per standard)",
        birth: "gas_benchmark.json createIdentity",
        transfer: "gas_benchmark.json transferOwnership",
      },
    },
    ranking: ranked,
    standards: model.standards,
  };
  const lifetimeFile = path.join(outDir, "scaling_lifetime.json");
  fs.writeFileSync(lifetimeFile, JSON.stringify(lifetimeOut, null, 2));
  console.log(`Experiment B written to ${lifetimeFile}`);

  // Console summaries
  console.log("\n=== Experiment A: marginal-cost stationarity ===");
  console.log(["standard", "op", "first", "50th", "delta", "slope(gas/op)", "R2", "order"].join("\t"));
  for (const [name, s] of Object.entries(marginalStandards)) {
    console.log(
      [name, s.op, s.first, s.last, s.delta, s.slope.toFixed(2), s.r2.toFixed(4), s.order].join("\t")
    );
  }

  console.log("\n=== Experiment B: lifetime cost model (ranked, ascending gas) ===");
  console.log(["rank", "standard", "birth", "35xappend", "3xtransfer", "TOTAL", "band[-50%,+50%]"].join("\t"));
  ranked.forEach((r, idx) => {
    const s = model.standards[r.name];
    const d = s.decomposition;
    console.log(
      [
        idx + 1,
        r.name,
        d.birth.subtotalGas,
        d.appends.subtotalGas,
        d.transfers.subtotalGas,
        s.totalLifetimeGas,
        `[${s.sensitivityBand.low}, ${s.sensitivityBand.high}]`,
      ].join("\t")
    );
  });
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
