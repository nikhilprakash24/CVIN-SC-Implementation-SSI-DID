"use strict";
// Entry point: `npm run metrics` (hardhat run benchmarks/run.js).
// Configuration is by environment variable because `hardhat run` does not forward CLI flags:
//   METRICS_SCENARIOS=crud,lifecycle,scale,batch,throughput,resolve
//   METRICS_ADAPTERS=erc1056,erc721,erc725
//   METRICS_N=30 METRICS_WARMUP=5 METRICS_SCALE_N=0,100,1000 METRICS_SCALE_H=1,10,50
//   METRICS_TRACE=1 METRICS_QUIET=0 METRICS_OUT=results/metrics
const hre = require("hardhat");
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const { MetricsCollector } = require("./lib/MetricsCollector");
const { makeDataset, PAYLOADS } = require("./lib/dataset");
const { ADAPTERS } = require("./adapters");
const { writeJSON } = require("./lib/exporters");
const { buildReport } = require("./report");

const SCENARIOS = {
  crud: require("./scenarios/crud"),
  lifecycle: require("./scenarios/lifecycle"),
  scale: require("./scenarios/scale"),
  batch: require("./scenarios/batch"),
  throughput: require("./scenarios/throughput"),
  resolve: require("./scenarios/resolve"),
};

function env(name, dflt) { return process.env[name] !== undefined && process.env[name] !== "" ? process.env[name] : dflt; }
function list(name, dflt) { return env(name, dflt).split(",").map((s) => s.trim()).filter(Boolean); }
function ints(name, dflt) { return list(name, dflt).map(Number); }

function git(cmd) { try { return execSync(`git ${cmd}`, { stdio: ["ignore", "pipe", "ignore"] }).toString().trim(); } catch { return null; } }

async function main() {
  const opts = {
    scenarios: list("METRICS_SCENARIOS", "crud,lifecycle,scale,batch,throughput,resolve"),
    adapters: list("METRICS_ADAPTERS", Object.keys(ADAPTERS).join(",")),
    n: Number(env("METRICS_N", 30)),
    warmup: Number(env("METRICS_WARMUP", 5)),
    scaleN: ints("METRICS_SCALE_N", "0,100,1000"),
    scaleH: ints("METRICS_SCALE_H", "1,10,50"),
    burstSenders: 10, burstPerSender: 20, bursts: 3,
    trace: env("METRICS_TRACE", "1") !== "0",
    quiet: env("METRICS_QUIET", "0") === "1",
    out: env("METRICS_OUT", "results/metrics"),
  };
  for (const a of opts.adapters) if (!ADAPTERS[a]) throw new Error(`unknown adapter ${a}`);
  for (const s of opts.scenarios) if (!SCENARIOS[s]) throw new Error(`unknown scenario ${s}`);

  const sha = git("rev-parse --short HEAD");
  const runId = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19) + "Z_" + (sha || "nogit");
  const runDir = path.join(opts.out, "runs", runId);
  fs.mkdirSync(runDir, { recursive: true });

  const solc = hre.config.solidity.compilers[0];
  const meta = {
    runId, commit: git("rev-parse HEAD"), commitShort: sha, branch: git("rev-parse --abbrev-ref HEAD"),
    dirty: (git("status --porcelain") || "").length > 0,
    date: new Date().toISOString(),
    node: process.version, hardhat: require("hardhat/package.json").version, ethers: hre.ethers.version,
    solc: solc.version, evmVersion: solc.settings.evmVersion || "default", optimizerRuns: solc.settings.optimizer.runs, viaIR: !!solc.settings.viaIR,
    network: { name: hre.network.name, chainId: hre.network.config.chainId, automine: true, blockGasLimit: hre.network.config.blockGasLimit || 30000000 },
    conditions: { repetitions: opts.n, warmup: opts.warmup, scaleN: opts.scaleN, scaleH: opts.scaleH, throughput: { senders: opts.burstSenders, perSender: opts.burstPerSender, bursts: opts.bursts }, trace: opts.trace, datasetSeed: 42 },
    scenarios: opts.scenarios, adapters: opts.adapters,
    derivedCostParams: { gasPriceGweiL1: 20, gasPriceGweiL2: 0.05, ethUSD: 3000 },
  };
  writeJSON(path.join(runDir, "meta.json"), meta);
  console.log(`\n=== CVIN metrics run ${runId} ===`);
  console.log(`commit ${sha}${meta.dirty ? " (dirty)" : ""} · solc ${meta.solc}/${meta.evmVersion} runs=${meta.optimizerRuns} viaIR=${meta.viaIR} · N=${opts.n}`);
  console.log(`scenarios: ${opts.scenarios.join(", ")} · adapters: ${opts.adapters.join(", ")}\n`);

  const collector = new MetricsCollector({ hre, runDir, trace: opts.trace });
  const ctx = { hre, ethers: hre.ethers, collector, dataset: makeDataset(1000, 42), payloads: PAYLOADS, ADAPTERS, adapterIds: opts.adapters, opts };

  const timings = {};
  for (const s of opts.scenarios) {
    console.log(`--- scenario: ${s}`);
    const t0 = Date.now();
    const rows = await SCENARIOS[s].run(ctx);
    timings[s] = (Date.now() - t0) / 1000;
    writeJSON(path.join(runDir, `${s}.json`), rows);
    console.log(`    ${s} done in ${timings[s].toFixed(1)}s\n`);
  }
  collector.close();
  meta.scenarioSeconds = timings;
  writeJSON(path.join(runDir, "meta.json"), meta);

  buildReport(runDir);

  // Promote to results/metrics/latest (copy, not symlink — portable and git-friendly)
  const latest = path.join(opts.out, "latest");
  fs.rmSync(latest, { recursive: true, force: true });
  fs.cpSync(runDir, latest, { recursive: true });
  console.log(`results: ${runDir}\nlatest:  ${latest}`);
}

main().catch((e) => { console.error(e); process.exit(1); });
