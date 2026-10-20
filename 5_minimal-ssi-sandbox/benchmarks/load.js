// WO-8 — Throughput / latency harness (Hardhat-local stand-in for the Caliper + Besu QBFT plan).
//
// Caliper against Besu QBFT needs a Besu node (binary or Docker), neither of which is on this
// machine; this script produces the SAME result shape Caliper would (per function per option:
// ops, TPS, p50/p95 submit→receipt latency, gas/op) against the Hardhat network with INTERVAL
// mining (a block every BLOCK_MS, like a QBFT round) so that latency has a block-time component
// instead of the automine zero. Every number here is a LOWER BOUND on any real network and is
// labelled "hardhat-interval" in the output; it fills the Stage 18 table's cells with the
// correct units and lets the three-tier mapping (<100 ms / 100–500 ms / >500 ms) be exercised.
//
// Run: BLOCK_MS=1000 N=50 IMPLS=O1_ERC1056,O2_ERC721 npx hardhat run benchmarks/load.js
const { ethers, network } = require("hardhat");
const fs = require("fs"), path = require("path");

const BLOCK_MS = Number(process.env.BLOCK_MS || 1000);
const N = Number(process.env.N || 40);
const IMPLS = (process.env.IMPLS || "O1_ERC1056,O2_ERC721").split(",");
const B32 = s => ethers.id(s);
const pct = (a, p) => { const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; };

async function bench(impl) {
  const [a, b] = await ethers.getSigners();
  const ssi = await (await ethers.getContractFactory(impl)).deploy();
  await ssi.waitForDeployment();
  const res = {};
  const run = async (fnId, fn, mk) => {
    const lat = [], gas = [];
    const t0 = performance.now();
    // submit all, then await receipts (Caliper-style open-loop send, bounded by N)
    const sent = [];
    for (let i = 0; i < N; i++) { const s = performance.now(); sent.push(mk(i).then(tx => ({ tx, s }))); }
    const txs = await Promise.all(sent);
    for (const { tx, s } of txs) { const rc = await tx.wait(); lat.push(performance.now() - s); gas.push(Number(rc.gasUsed)); }
    const wall = (performance.now() - t0) / 1000;
    res[fnId] = { fn, ops: N, tps: +(N / wall).toFixed(2), p50_ms: +pct(lat, 0.5).toFixed(1), p95_ms: +pct(lat, 0.95).toFixed(1), gas_avg: Math.round(gas.reduce((x, y) => x + y, 0) / gas.length) };
    console.log(`${impl} ${fnId} ${fn}: tps=${res[fnId].tps} p50=${res[fnId].p50_ms}ms p95=${res[fnId].p95_ms}ms gas=${res[fnId].gas_avg}`);
  };
  // F1 createDID ×N (independent)
  const dids = [];
  await run("F1", "createDID", async () => { const tx = await ssi.connect(a).createDID(a.address); return tx; });
  // collect N dids for subsequent ops
  const filter = ssi.filters.DIDCreated();
  for (const ev of await ssi.queryFilter(filter)) dids.push(ev.args.did);
  const subj = dids[0];
  await run("F5", "issueCredential", (i) => ssi.connect(a).issueCredential(dids[i], subj, B32("vc" + i), 0));
  await run("F11", "addDelegate", (i) => ssi.connect(a).addDelegate(dids[i], B32("sigAuth"), b.address, 3600));
  await run("F3", "updateDID", (i) => ssi.connect(a).updateDID(dids[i], B32("svc"), "0x01", 60));
  // views: latency only (gas 0)
  const vl = [];
  for (let i = 0; i < N; i++) { const s = performance.now(); await ssi.verifyCredential(B32("x" + i)); vl.push(performance.now() - s); }
  res.F6 = { fn: "verifyCredential(view)", ops: N, tps: null, p50_ms: +pct(vl, 0.5).toFixed(2), p95_ms: +pct(vl, 0.95).toFixed(2), gas_avg: 0 };
  console.log(`${impl} F6 view: p50=${res.F6.p50_ms}ms p95=${res.F6.p95_ms}ms`);
  return res;
}

async function main() {
  await network.provider.send("evm_setAutomine", [false]);
  await network.provider.send("evm_setIntervalMining", [BLOCK_MS]);
  const out = { harness: "hardhat-interval (NOT Caliper, NOT Besu) — lower bound", blockMs: BLOCK_MS, n: N, generatedAt: new Date().toISOString(), results: {} };
  for (const impl of IMPLS) out.results[impl] = await bench(impl);
  await network.provider.send("evm_setIntervalMining", [0]); await network.provider.send("evm_setAutomine", [true]);
  const dir = path.join(__dirname, "caliper"); fs.mkdirSync(dir, { recursive: true });
  const f = path.join(dir, `load_${BLOCK_MS}ms_${Date.now()}.json`); fs.writeFileSync(f, JSON.stringify(out, null, 2));
  // tier mapping summary
  let md = `# Load results (${out.harness}; block ${BLOCK_MS} ms; N=${N})\n\n| Option | Fn | TPS | p50 ms | p95 ms | gas/op | Tier by p95 |\n|---|---|---|---|---|---|---|\n`;
  for (const [impl, r] of Object.entries(out.results)) for (const [k, v] of Object.entries(r)) md += `| ${impl} | ${k} ${v.fn} | ${v.tps ?? "—"} | ${v.p50_ms} | ${v.p95_ms} | ${v.gas_avg} | ${v.p95_ms < 100 ? "1 (<100)" : v.p95_ms <= 500 ? "2 (100–500)" : "3 (>500)"} |\n`;
  md += `\nTier column applies the thesis's three-tier framework to p95 submit→receipt latency on this harness only; it is a lower bound and NOT a claim about any real network. Views carry no block-time term and sit at Tier 1 by construction; every write carries at least one block interval (${BLOCK_MS} ms here).\n`;
  fs.writeFileSync(f.replace(/\.json$/, ".md"), md);
  console.log("\n" + md + `\nwritten: ${path.relative(process.cwd(), f)}`);
}
main().then(() => process.exit(0)).catch(e => { console.error(e); process.exit(1); });
