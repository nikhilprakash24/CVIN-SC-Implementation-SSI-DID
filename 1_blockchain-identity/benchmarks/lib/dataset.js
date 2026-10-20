"use strict";
// Deterministic workload dataset (seed 42). Payload sizes are fixed so calldata
// and log gas are equal across substrates for the same catalogue op.

const VIN_ALPHABET = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"; // no I, O, Q (ISO 3779)
const MAKES = ["Honda", "Toyota", "Ford", "Tesla", "BMW", "Volkswagen", "Hyundai", "Kia"];
const MODELS = ["Accord", "Camry", "F-150", "Model 3", "i4", "ID.4", "Ioniq 5", "EV6"];
const COLORS = ["Silver", "White", "Black", "Blue", "Red", "Grey"];
const AUTONOMY = ["SAE Level 2", "SAE Level 3", "SAE Level 4"];

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function makeDataset(count = 1000, seed = 42) {
  const rnd = mulberry32(seed);
  const pick = (arr) => arr[Math.floor(rnd() * arr.length)];
  const vehicles = [];
  const seen = new Set();
  while (vehicles.length < count) {
    let vin = "";
    for (let i = 0; i < 17; i++) vin += VIN_ALPHABET[Math.floor(rnd() * VIN_ALPHABET.length)];
    if (seen.has(vin)) continue;
    seen.add(vin);
    const i = vehicles.length;
    // String fields are padded to fixed widths so calldata/log/memory gas is
    // identical for every vehicle (framework §3: equal payload sizes).
    vehicles.push({
      index: i,
      vin,
      make: pick(MAKES).padEnd(10),
      model: pick(MODELS).padEnd(10),
      year: 2018 + Math.floor(rnd() * 8),
      color: pick(COLORS).padEnd(6),
      engineNumber: "ENG-" + String(100000 + Math.floor(rnd() * 900000)),
      manufacturingDate: 1_600_000_000 + Math.floor(rnd() * 200_000_000),
      autonomyLevel: pick(AUTONOMY),
      metadataURI: "ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi/" + String(i).padStart(4, "0"),
    });
  }
  return vehicles;
}

// Fixed-size payloads (bytes) shared by all substrates.
const PAYLOADS = {
  serviceEndpointURL: "https://telematics.example.org/v1/vehicles/0000000000000000/",  // 64 B
  serviceRecordURI: "ipfs://bafybeih5k2dfn6ydu6xuwq5ytkqxpvh2e4djhcjvf2h4v5tmjjl4lpv3ye", // 66 B
  attributeName: "did/svc/TelemetryService",
  attributeValue: "https://telematics.example.org/v1/vehicles/0000000000000000/",
  deactivatedName: "did/deactivated",
  credentialHashes: Array.from({ length: 16 }, (_, i) =>
    "0x" + (i + 1).toString(16).padStart(2, "0").repeat(32)
  ),
  ttlSeconds: 365 * 24 * 3600,
};

module.exports = { makeDataset, PAYLOADS, VIN_ALPHABET };
