// ZK-VIN end to end: honest proof, false statements, timings, and the fixture the contract tests use.
//
//   node scripts/prove_and_verify.js            # correctness + negative cases (fast; CI)
//   node scripts/prove_and_verify.js --bench    # + Groth16 timings (prove N=10, verify N=30) -> results/zkvin_bench.json
//   node scripts/prove_and_verify.js --fixture  # + write fixtures/zkvin_proof.json (calldata for the gate tests)
//
// Condition M0 (in-process, no chain). Expectations Z-E1, Z-E2, Z-E4 are pre-registered in
// docs/zkp/PLAN_1_ZKP_AND_AGENT_IDENTITY.md §1.1 and evaluated here by rule, not by eye.
const fs = require("fs");
const path = require("path");
const snarkjs = require("snarkjs");
const { ROOT, toField, context, runIdentity } = require("./zkvin_lib");

const WASM = path.join(ROOT, "artifacts/zkvin.wasm");
const ZKEY = path.join(ROOT, "artifacts/zkvin_final.zkey");
const VKEY = JSON.parse(fs.readFileSync(path.join(ROOT, "artifacts/verification_key.json")));

const VEHICLE = { vin: "1HGCM82633A004352", modelYear: 2022, region: 59, salt: toField("vehicle-salt|1HGCM82633A004352|demo") };
const REQUEST = { minModelYear: 2020, scope: toField("scope|insurer:acme|2026"), challenge: toField("challenge|acme|nonce-0001") };

async function prove(input) {
  return snarkjs.groth16.fullProve(input, WASM, ZKEY);
}
async function proves(input) {
  try { await prove(input); return true; } catch (_) { return false; }
}
const median = (xs) => { const s = [...xs].sort((a, b) => a - b); const m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };

async function main() {
  const args = new Set(process.argv.slice(2));
  const ctx = await context();
  const honest = ctx.input({ ...VEHICLE, ...REQUEST });
  const { proof, publicSignals } = await prove(honest);
  const ok = await snarkjs.groth16.verify(VKEY, publicSignals, proof);
  const expectedNf = ctx.nullifier(VEHICLE.salt, REQUEST.scope).toString();
  const checks = [
    ["honest proof verifies", ok === true],
    ["nullifier is Poseidon(salt, scope)", publicSignals[0] === expectedNf],
    ["public signals are [nullifier, commitment, mfrRoot, minModelYear, region, scope, challenge]",
      publicSignals[1] === honest.commitment && publicSignals[3] === "2020" && publicSignals[4] === "59"],
    ["a changed public signal fails verification",
      !(await snarkjs.groth16.verify(VKEY, [publicSignals[0], publicSignals[1], publicSignals[2], "2023", ...publicSignals.slice(4)], proof))],
    ["another scope gives another nullifier",
      ctx.nullifier(VEHICLE.salt, toField("scope|toll:A")).toString() !== expectedNf],
  ];
  // False statements: witness generation must fail (the constraints are unsatisfiable).
  const negatives = {
    unauthorised_manufacturer: { ...VEHICLE, vin: "XXX" .replace(/X/g, "2") + "CM82633A004352" },
    model_year_below_minimum: { ...VEHICLE, modelYear: 2018 },
    wrong_region_claimed: { ...VEHICLE, claim: { region: 60 } },
    wrong_salt: { ...VEHICLE, claim: { salt: toField("guess") } },
    different_vin_than_committed: { ...VEHICLE, claim: { vin: "5YJ3E1EA7KF317000" } },
  };
  for (const [name, v] of Object.entries(negatives)) {
    checks.push([`false statement rejected: ${name}`, !(await proves(ctx.input({ ...v, ...REQUEST })))]);
  }
  let failed = 0;
  for (const [name, pass] of checks) { console.log(`${pass ? "PASS" : "FAIL"}  ${name}`); if (!pass) failed++; }

  const calldata = await snarkjs.groth16.exportSolidityCallData(proof, publicSignals);
  const proofBytes = 8 * 32; // a, b (2x2), c: eight 32-byte field elements in the Solidity ABI

  if (args.has("--fixture")) {
    const argv = JSON.parse("[" + calldata + "]");
    const wrongScope = ctx.input({ ...VEHICLE, ...REQUEST, scope: toField("scope|toll:A") });
    const p2 = await prove(wrongScope);
    const argv2 = JSON.parse("[" + (await snarkjs.groth16.exportSolidityCallData(p2.proof, p2.publicSignals)) + "]");
    fs.mkdirSync(path.join(ROOT, "fixtures"), { recursive: true });
    fs.writeFileSync(path.join(ROOT, "fixtures/zkvin_proof.json"), JSON.stringify({
      note: "Groth16 ZK-VIN proofs against the INSECURE dev keys in artifacts/; regenerate with --fixture",
      vehicle: { region: VEHICLE.region, commitment: honest.commitment }, request: { minModelYear: 2020,
        scope: REQUEST.scope.toString(), challenge: REQUEST.challenge.toString() },
      mfrRoot: honest.mfrRoot, insurer: { a: argv[0], b: argv[1], c: argv[2], pub: argv[3] },
      toll: { scope: toField("scope|toll:A").toString(), a: argv2[0], b: argv2[1], c: argv2[2], pub: argv2[3] },
    }, null, 2) + "\n");
    console.log("wrote fixtures/zkvin_proof.json");
  }

  if (args.has("--bench")) {
    const N_PROVE = 10, N_VERIFY = 30;
    const proveMs = [], verifyMs = [];
    await prove(honest); // warm-up, discarded and disclosed
    for (let i = 0; i < N_PROVE; i++) {
      const t0 = process.hrtime.bigint(); await prove(honest); proveMs.push(Number(process.hrtime.bigint() - t0) / 1e6);
    }
    await snarkjs.groth16.verify(VKEY, publicSignals, proof);
    for (let i = 0; i < N_VERIFY; i++) {
      const t0 = process.hrtime.bigint(); await snarkjs.groth16.verify(VKEY, publicSignals, proof);
      verifyMs.push(Number(process.hrtime.bigint() - t0) / 1e6);
    }
    const info = fs.readFileSync(path.join(ROOT, "artifacts/circuit_info.txt"), "utf8");
    const out = {
      condition: "M0 (in-process snarkjs, no chain); one warm-up of each discarded",
      run: runIdentity(),
      circuit: Object.fromEntries(info.split("\n").filter((l) => l.includes(":")).map((l) => l.split(":").map((s) => s.trim()))),
      prove_ms: { n: N_PROVE, median: median(proveMs), min: Math.min(...proveMs), max: Math.max(...proveMs), samples: proveMs },
      verify_ms: { n: N_VERIFY, median: median(verifyMs), min: Math.min(...verifyMs), max: Math.max(...verifyMs), samples: verifyMs },
      proof_calldata_bytes: proofBytes,
      proof_json_bytes: Buffer.byteLength(JSON.stringify(proof)),
      public_signals: publicSignals.length,
      expectations: {
        "Z-E1 verify median < 100 ms": median(verifyMs) < 100 ? "PASS" : "FAIL",
        "Z-E2 prove median < 10 s": median(proveMs) < 10000 ? "PASS" : "FAIL",
        "Z-E4 proof calldata < 1024 bytes": proofBytes < 1024 ? "PASS" : "FAIL",
      },
      sample_proof: proof,
      sample_public_signals: publicSignals,
    };
    fs.mkdirSync(path.join(ROOT, "results"), { recursive: true });
    fs.writeFileSync(path.join(ROOT, "results/zkvin_bench.json"), JSON.stringify(out, null, 2) + "\n");
    console.log(`prove median ${out.prove_ms.median.toFixed(1)} ms, verify median ${out.verify_ms.median.toFixed(2)} ms`);
    console.log(out.expectations);
  }
  if (typeof globalThis.curve_bn128 !== "undefined") await globalThis.curve_bn128.terminate();
  process.exit(failed ? 1 : 0);
}

main().catch((e) => { console.error(e); process.exit(1); });
