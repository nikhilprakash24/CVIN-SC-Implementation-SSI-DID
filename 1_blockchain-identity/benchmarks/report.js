"use strict";
// Builds comparison tables (md / csv / tex) from a run directory.
// `node benchmarks/report.js [runDir]` — defaults to results/metrics/latest.
const fs = require("fs");
const path = require("path");
const { OPERATIONS } = require("./lib/operations");
const { ALL_SUBSTRATES } = require("./adapters");
const { writeCSV, writeText, markdownMatrix, latexMatrix } = require("./lib/exporters");

const NOT_IMPL = "not impl.";

function load(runDir, name) {
  const f = path.join(runDir, `${name}.json`);
  return fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, "utf8")) : null;
}

function footerFor(meta) {
  return `Run ${meta.runId} · commit ${meta.commitShort}${meta.dirty ? " (dirty)" : ""} · solc ${meta.solc} target ${meta.evmVersion} runs=${meta.optimizerRuns} viaIR=${meta.viaIR} · Hardhat in-process automine${meta.network && meta.network.hardfork ? ", executes " + meta.network.hardfork : ""} · N=${meta.conditions.repetitions}`;
}

function cellFactory(rows, adaptersRun, pick) {
  const idx = new Map(rows.map((r) => [`${r.adapter}|${r.op}`, r]));
  return (op, adapter) => {
    if (!adaptersRun.includes(adapter)) return NOT_IMPL;
    const r = idx.get(`${adapter}|${op}`);
    if (!r) return null;
    if (r.supported === false) return "n/a";
    return pick(r);
  };
}

function emit(runDir, name, spec, meta) {
  const dir = path.join(runDir, "tables");
  const footer = footerFor(meta);
  writeText(path.join(dir, `${name}.md`), markdownMatrix({ ...spec, footer: `_${footer}_` }));
  writeText(path.join(dir, `${name}.tex`), latexMatrix({ ...spec, caption: spec.title, label: `tab:${name}`, footer }));
  const csvRows = [];
  for (const r of spec.rowKeys) {
    const row = { [spec.rowLabel]: spec.rowLabels ? spec.rowLabels[r] || r : r };
    for (const c of spec.colKeys) row[c] = spec.cellFn(r, c);
    csvRows.push(row);
  }
  writeCSV(path.join(dir, `${name}.csv`), csvRows);
}

function buildReport(runDir) {
  const meta = JSON.parse(fs.readFileSync(path.join(runDir, "meta.json"), "utf8"));
  const adaptersRun = meta.adapters;
  const colKeys = ALL_SUBSTRATES.map((s) => s.id);
  const colLabels = Object.fromEntries(ALL_SUBSTRATES.map((s) => [s.id, s.label]));
  const opLabels = Object.fromEntries(OPERATIONS.map((o) => [o.id, o.id]));
  const summary = [`# CVIN metrics report — ${meta.runId}`, "", `_${footerFor(meta)}_`, "",
    "Cells: exact gas for tx ops; `n/a` = substrate has no primitive (reportable finding); `not impl.` = adapter not on trunk yet.", ""];

  const crud = load(runDir, "crud");
  if (crud) {
    const txOps = OPERATIONS.filter((o) => o.kind === "tx").map((o) => o.id);
    const readOps = OPERATIONS.filter((o) => o.kind === "read").map((o) => o.id);
    const specs = [
      ["crud_gas", { title: "L1 — Gas per catalogue operation (exact)", rowLabel: "Operation", rowKeys: txOps, colKeys, colLabels, rowLabels: opLabels, cellFn: cellFactory(crud, adaptersRun, (r) => r.gasUsed) }],
      ["crud_txcount", { title: "L1 — Transactions per semantic operation", rowLabel: "Operation", rowKeys: txOps, colKeys, colLabels, cellFn: cellFactory(crud, adaptersRun, (r) => r.txCount) }],
      ["crud_storage", { title: "L1 — Storage writes per operation (SSTORE count / zero→nonzero SSTOREs)", rowLabel: "Operation", rowKeys: txOps, colKeys, colLabels, cellFn: cellFactory(crud, adaptersRun, (r) => `${r.sstoreCount} / ${r.zeroToNonzeroSstores}`) }],
      ["crud_logbytes", { title: "L1 — Event-log bytes per operation", rowLabel: "Operation", rowKeys: txOps, colKeys, colLabels, cellFn: cellFactory(crud, adaptersRun, (r) => r.logBytes) }],
      ["crud_calldata", { title: "L1 — Calldata bytes per operation", rowLabel: "Operation", rowKeys: txOps, colKeys, colLabels, cellFn: cellFactory(crud, adaptersRun, (r) => r.calldataBytes) }],
      ["crud_latency_tx", { title: "L1 — Tx latency, median / p95 ms (local node, N=" + meta.conditions.repetitions + ")", rowLabel: "Operation", rowKeys: txOps, colKeys, colLabels, cellFn: cellFactory(crud, adaptersRun, (r) => `${r.latency.median} / ${r.latency.p95}`) }],
      ["crud_reads", { title: "L1 — Read ops: RPC calls / bytes / median ms", rowLabel: "Operation", rowKeys: readOps, colKeys, colLabels, cellFn: cellFactory(crud, adaptersRun, (r) => `${r.readRpcCalls} / ${r.readBytes} / ${r.latency.median}`) }],
    ];
    for (const [name, spec] of specs) { emit(runDir, name, spec, meta); summary.push(markdownMatrix(spec)); }
    const deploys = crud.filter((r) => r.kind === "deploy");
    summary.push("### Deployment (shared contracts)", "", "| Substrate | Contract | Deploy gas | Bytecode bytes |", "|---|---|---:|---:|");
    for (const d of deploys) summary.push(`| ${colLabels[d.adapter]} | ${d.contract} | ${d.gasUsed.toLocaleString("en-US")} | ${d.bytecodeBytes.toLocaleString("en-US")} |`);
    summary.push("");
    const det = crud.filter((r) => r.kind === "tx" && r.supported && r.gasDeterministic === false);
    if (det.length) { summary.push("**Non-deterministic execution gas detected** (distinct values across iterations):", ...det.map((r) => `- ${r.adapter} ${r.op}: ${r.gasExecutionDistinct.join(", ")}`), ""); }
    // long-format CSV for statistics
    writeCSV(path.join(runDir, "tables", "crud_long.csv"), crud.filter((r) => r.kind !== "deploy").map((r) => ({
      adapter: r.adapter, op: r.op, kind: r.kind, supported: r.supported, txCount: r.txCount, gasUsed: r.gasUsed, gasIntrinsic: r.gasIntrinsic, gasExecution: r.gasExecution,
      calldataBytes: r.calldataBytes, logCount: r.logCount, logBytes: r.logBytes, sstoreCount: r.sstoreCount, sloadCount: r.sloadCount, zeroToNonzeroSstores: r.zeroToNonzeroSstores,
      readRpcCalls: r.readRpcCalls, readBytes: r.readBytes, lat_n: r.latency?.n, lat_median: r.latency?.median, lat_p95: r.latency?.p95, lat_mean: r.latency?.mean, lat_sd: r.latency?.sd,
    })));
    const samples = [];
    for (const r of crud) if (r.latencySamples) r.latencySamples.forEach((v, i) => samples.push({ adapter: r.adapter, op: r.op, sample: i, latencyMs: v }));
    writeCSV(path.join(runDir, "tables", "crud_latency_samples.csv"), samples, ["adapter", "op", "sample", "latencyMs"]);
  }

  const life = load(runDir, "lifecycle");
  if (life) {
    const events = life[0] ? life[0].events.map((e) => e.eventNo) : [];
    const labels = Object.fromEntries((life[0] ? life[0].events : []).map((e) => [e.eventNo, `${e.eventNo}. ${e.event}`]));
    const idx = Object.fromEntries(life.map((l) => [l.adapter, l]));
    const rowKeys = [...events, "TOTAL", "SHARED_DEPLOY", "PER_IDENTITY_DEPLOY", "FLEET_1", "FLEET_1000", "FLEET_1000000"];
    const rowLabels = { ...labels, TOTAL: "**Lifetime total**", SHARED_DEPLOY: "Shared deploy gas", PER_IDENTITY_DEPLOY: "Per-identity deploy gas (in total)", FLEET_1: "Lifetime + shared/1", FLEET_1000: "Lifetime + shared/1 000", FLEET_1000000: "Lifetime + shared/1 000 000" };
    const cellFn = (r, a) => {
      if (!adaptersRun.includes(a)) return NOT_IMPL;
      const l = idx[a]; if (!l) return null;
      if (r === "TOTAL") return l.lifetimeGas;
      if (r === "SHARED_DEPLOY") return l.sharedDeployGas;
      if (r === "PER_IDENTITY_DEPLOY") return l.perIdentityDeployGas;
      if (String(r).startsWith("FLEET_")) return l.apportioned[r.slice(6)];
      const e = l.events.find((x) => x.eventNo === r); return e ? e.gasUsed : null;
    };
    const spec = { title: "L2 — MOBI VID lifecycle gas per event", rowLabel: "Event", rowKeys, rowLabels, colKeys, colLabels, cellFn };
    emit(runDir, "lifecycle_gas", spec, meta); summary.push(markdownMatrix(spec));
    const spec2 = { title: "L2 — Lifecycle totals: tx count / log bytes / zero→nonzero SSTOREs", rowLabel: "Metric", rowKeys: ["tx", "log", "z2nz"], rowLabels: { tx: "Transactions", log: "Log bytes", z2nz: "Zero→nonzero SSTOREs" }, colKeys, colLabels,
      cellFn: (r, a) => !adaptersRun.includes(a) ? NOT_IMPL : !idx[a] ? null : r === "tx" ? idx[a].lifetimeTxCount : r === "log" ? idx[a].lifetimeLogBytes : idx[a].lifetimeZeroToNonzeroSstores };
    emit(runDir, "lifecycle_totals", spec2, meta); summary.push(markdownMatrix(spec2));
  }

  const scale = load(runDir, "scale");
  if (scale) {
    const keys = [...new Set(scale.map((r) => `${r.axis}=${r.value}|${r.op}`))];
    const idx = new Map(scale.map((r) => [`${r.adapter}|${r.axis}=${r.value}|${r.op}`, r]));
    // Deterministic quantities only (gas; reads: RPC calls / bytes), so scale.csv is
    // byte-identical across runs of one commit; read latency is in scale_latency.
    const spec = { title: "L3 — Marginal cost vs population N and history h (gas; reads: RPC calls / bytes)", rowLabel: "Axis | op", rowKeys: keys, colKeys, colLabels,
      cellFn: (k, a) => { if (!adaptersRun.includes(a)) return NOT_IMPL; const r = idx.get(`${a}|${k}`); if (!r) return null; return r.kind === "read" ? `${r.readRpcCalls} RPC / ${r.readBytes} B` : r.gasUsed; } };
    emit(runDir, "scale", spec, meta); summary.push(markdownMatrix(spec));
    const readKeys = keys.filter((k) => scale.some((r) => r.kind === "read" && `${r.axis}=${r.value}|${r.op}` === k));
    const specLat = { title: "L3 — Read latency vs N and h: median / p95 ms (in-process, 2 warm-up + 10 samples)", rowLabel: "Axis | op", rowKeys: readKeys, colKeys, colLabels,
      cellFn: (k, a) => { if (!adaptersRun.includes(a)) return NOT_IMPL; const r = idx.get(`${a}|${k}`); if (!r) return null; return `${r.latency.median} / ${r.latency.p95}`; } };
    emit(runDir, "scale_latency", specLat, meta); summary.push(markdownMatrix(specLat));
  }

  const batch = load(runDir, "batch");
  if (batch) {
    const sizes = [...new Set(batch.map((r) => r.batchSize))];
    const idx = new Map(batch.map((r) => [`${r.adapter}|${r.batchSize}`, r]));
    const spec = { title: "L4 — Create k identities: total gas (per item) [mode]", rowLabel: "k", rowKeys: sizes, colKeys, colLabels,
      cellFn: (k, a) => { if (!adaptersRun.includes(a)) return NOT_IMPL; const r = idx.get(`${a}|${k}`); return r ? `${r.gasUsed.toLocaleString("en-US")} (${r.gasPerItem.toLocaleString("en-US")}) [${r.mode}]` : null; } };
    emit(runDir, "batch", spec, meta); summary.push(markdownMatrix(spec));
  }

  const tp = load(runDir, "throughput");
  if (tp) {
    const idx = Object.fromEntries(tp.map((r) => [r.adapter, r]));
    const spec = { title: "L5 — Single-node throughput for U3 (median of 3 bursts of 200 tx)", rowLabel: "Metric", rowKeys: ["tps", "mps", "gps"], rowLabels: { tps: "tx / s (queue + mine)", mps: "tx / s (mine only)", gps: "gas / s" }, colKeys, colLabels,
      cellFn: (r, a) => !adaptersRun.includes(a) ? NOT_IMPL : !idx[a] ? null : r === "tps" ? idx[a].txPerSec.median : r === "mps" ? idx[a].mineTxPerSec.median : Math.round(idx[a].gasPerSec.median) };
    emit(runDir, "throughput", spec, meta); summary.push(markdownMatrix(spec));
  }

  const res = load(runDir, "resolve");
  if (res) {
    const ops = [...new Set(res.map((r) => r.op))];
    const idx = new Map(res.map((r) => [`${r.adapter}|${r.op}`, r]));
    const spec = { title: "L6 — Verifier read path after lifecycle: RPC calls / bytes / median ms / p95 ms", rowLabel: "Operation", rowKeys: ops, colKeys, colLabels,
      cellFn: (o, a) => { if (!adaptersRun.includes(a)) return NOT_IMPL; const r = idx.get(`${a}|${o}`); if (!r) return null; if (r.supported === false) return "n/a"; return `${r.readRpcCalls} / ${r.readBytes} / ${r.latency.median} / ${r.latency.p95}`; } };
    emit(runDir, "resolve", spec, meta); summary.push(markdownMatrix(spec));
  }

  writeText(path.join(runDir, "REPORT.md"), summary.join("\n"));
  console.log(`report: ${path.join(runDir, "REPORT.md")}`);
}

if (require.main === module) {
  buildReport(process.argv[2] || path.join("results", "metrics", "latest"));
}

module.exports = { buildReport };
