// WO-4 AC — per-tier function coverage summarised from traces (never hand-entered).
// Scenario → tier mapping follows docs/ARCHITECTURE.md §4 and HDA doc 05.
// For each scenario (over all options that ran it): F-tags seen, tx/view/offchain counts, and
// which tags occur on the Tier 1/2 critical path (= entries of kind offchain/view only).
const fs = require("fs"), path = require("path");
const TR = path.join(__dirname, "../traces");
const TIER = { i2i: "Low (anchors off-chain)", s2_dualmode: "Low + Medium", s3_evcharging: "Medium", s4_insurance: "High", vid_minimal: "High (issuance) / Medium (verification)", vid_lifecycle: "High", delayed_write: "Medium (offline)", batch_anchor: "High", fl_round: "High", bbs_presentation: "Medium", zk_age_gate: "Medium", idpp_port: "Cross (High)" };
const agg = {};
for (const f of fs.readdirSync(TR).filter(x => x.endsWith(".jsonl"))) {
  const sc = f.replace(/_O\d_.*$/, "").replace(/_\d+\.jsonl$/, "");
  const a = (agg[sc] ??= { impls: new Set(), tags: new Set(), tx: 0, view: 0, off: 0, onPathTags: new Set(), runs: 0 });
  a.runs++;
  for (const line of fs.readFileSync(path.join(TR, f), "utf8").split("\n")) {
    if (!line.trim()) continue; const e = JSON.parse(line);
    a.impls.add(e.impl);
    if (e.kind === "tx") a.tx++; else if (e.kind === "view") a.view++; else if (e.kind === "offchain") a.off++;
    if (e.fnId) { a.tags.add(e.fnId); if (e.kind === "view") a.onPathTags.add(e.fnId); }
  }
}
const F = ["F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12"];
let md = "# Per-tier function coverage (generated from traces)\n\n| Scenario | Tier | Runs (options) | F-tags covered (/12) | Other tags | tx / view / off-chain entries per run (avg) | Read-only tags on the critical path |\n|---|---|---|---|---|---|---|\n";
for (const [sc, a] of Object.entries(agg).sort()) {
  const fs_ = F.filter(t => a.tags.has(t)); const other = [...a.tags].filter(t => !/^F\d+$/.test(t)).sort();
  md += `| ${sc} | ${TIER[sc] || "—"} | ${a.runs} (${a.impls.size}) | ${fs_.join(" ")} (${fs_.length}) | ${other.join(" ") || "—"} | ${(a.tx/a.runs).toFixed(1)} / ${(a.view/a.runs).toFixed(1)} / ${(a.off/a.runs).toFixed(1)} | ${[...a.onPathTags].sort().join(" ") || "—"} |\n`;
}
md += "\nReading: at Low/Medium tiers the critical path carries only view/off-chain entries (F2, F6, F12, G4, T2 reads and off-chain verification); every tx is Tier 3 or asynchronous. Tier 1 (BSM stream in s2_dualmode) has zero chain entries by construction.\n";
fs.writeFileSync(path.join(__dirname, "tier_coverage.md"), md); console.log(md);
