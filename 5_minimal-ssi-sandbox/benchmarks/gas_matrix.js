// WO-5 — Benchmark extraction from traces (never hand-entered).
// Reads every traces/*.jsonl, aggregates gasUsed per (impl, fnId/fn) over kind=tx entries,
// writes benchmarks/gas_matrix.csv (option × function: min, max, n) and
// benchmarks/gas_report.md (table against spec §5.3 targets; extension tags without targets).
//
// Run: node benchmarks/gas_matrix.js
const fs = require("fs");
const path = require("path");

const TR = path.join(__dirname, "../traces");
const OUT_CSV = path.join(__dirname, "gas_matrix.csv");
const OUT_MD = path.join(__dirname, "gas_report.md");

// Spec §5.3 targets. ERC-1056 column applies to the event-sourced/lightweight options (O1, O2, O5);
// ERC-725 column to contract-account options (O3, O4, O6). Recorded as the hypothesis under test.
const TARGET = {
  F1: [100e3, 600e3], F2: [10e3, 20e3], F3: [80e3, 100e3], F4: [50e3, 60e3], F5: [120e3, 150e3], F6: [10e3, 15e3],
  F7: [50e3, 60e3], F8: [150e3, 200e3], F9: [100e3, 120e3], F10: [50e3, 60e3], F11: [60e3, 70e3], F12: [5e3, 10e3],
};
const LIGHT = new Set(["O1_ERC1056", "O2_ERC721", "O5_ERC1155"]);
const ORDER = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "G0", "G1", "G2", "G3", "T1", "B1", "B3", "C1", "C3", "Z1"];

const agg = {}; // impl -> tag -> {fn, min, max, n, files:Set}
const files = fs.readdirSync(TR).filter(f => f.endsWith(".jsonl")).sort();
for (const f of files) {
  for (const line of fs.readFileSync(path.join(TR, f), "utf8").split("\n")) {
    if (!line.trim()) continue;
    const e = JSON.parse(line);
    if (e.kind !== "tx" || !e.gasUsed) continue;
    const tag = e.fnId || e.fn;
    const impl = e.impl;
    const g = Number(e.gasUsed);
    const a = (agg[impl] ??= {});
    const r = (a[tag] ??= { fn: e.fn, min: Infinity, max: -Infinity, n: 0, files: new Set() });
    r.min = Math.min(r.min, g); r.max = Math.max(r.max, g); r.n++; r.files.add(f);
  }
}
const impls = Object.keys(agg).sort();
const tags = [...new Set(impls.flatMap(i => Object.keys(agg[i])))].sort((x, y) => (ORDER.indexOf(x) + 1 || 99) - (ORDER.indexOf(y) + 1 || 99));

// CSV
const rows = [["impl", "tag", "fn", "gas_min", "gas_max", "n", "traces"]];
for (const i of impls) for (const t of tags) { const r = agg[i][t]; if (r) rows.push([i, t, r.fn, r.min, r.max, r.n, [...r.files].join(";")]); }
fs.writeFileSync(OUT_CSV, rows.map(r => r.join(",")).join("\n") + "\n");

// Markdown report
const fmt = n => n.toLocaleString("en-US");
let md = `# Gas report (generated from traces; do not edit)\n\nGenerated ${new Date().toISOString()} from ${files.length} trace files. Values are min–max of \`gasUsed\` over kind=tx entries, Hardhat network, solc 0.8.24 / optimizer 200 / paris. Spec §5.3 targets: ERC-1056 column for ${[...LIGHT].join(", ")}; ERC-725 column for the rest. ✗ marks a miss by the minimum observed value.\n\n`;
md += "| Tag | Function | " + impls.map(i => i.replace(/^O\d_/, "")).join(" | ") + " |\n|---|---|" + impls.map(() => "---").join("|") + "|\n";
for (const t of tags) {
  const fn = impls.map(i => agg[i][t]?.fn).find(Boolean) || "";
  md += `| ${t} | ${fn} | ` + impls.map(i => {
    const r = agg[i][t]; if (!r) return "—";
    const tgt = TARGET[t]?.[LIGHT.has(i) ? 0 : 1];
    const miss = tgt && r.min >= tgt ? " ✗" : "";
    return (r.min === r.max ? fmt(r.min) : `${fmt(r.min)}–${fmt(r.max)}`) + miss;
  }).join(" | ") + " |\n";
}
md += "\n## Target misses (minimum observed ≥ target)\n\n";
for (const i of impls) {
  const m = tags.filter(t => { const r = agg[i][t]; const tgt = TARGET[t]?.[LIGHT.has(i) ? 0 : 1]; return r && tgt && r.min >= tgt; });
  md += `- ${i}: ${m.length ? m.map(t => `${t} (${fmt(agg[i][t].min)} vs <${fmt(TARGET[t][LIGHT.has(i) ? 0 : 1])})`).join(", ") : "none"}\n`;
}
md += "\nView functions (F2, F6, F12, G4, T2, B2, C2, C4, Z2) cost no gas and do not appear. Extension tags: G governance, T typing, B batch anchor, C Set C harness (not O7), Z Groth16 gate.\n";
fs.writeFileSync(OUT_MD, md);
console.log(`impls=${impls.length} tags=${tags.length} traces=${files.length} -> ${path.relative(process.cwd(), OUT_CSV)}, ${path.relative(process.cwd(), OUT_MD)}`);
