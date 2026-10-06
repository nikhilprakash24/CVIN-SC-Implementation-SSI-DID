"use strict";
// Analysis layer over a run directory (framework §6a): ratios vs the ERC-1056 baseline,
// capability matrix (which catalogue ops each substrate lacks), and the H5 dominance /
// Pareto analysis over explicit criteria. Pure function of the run's JSON files.
// `node analysis/analysis.js [runDir]` — defaults to results/metrics/latest.
const fs = require("fs");
const path = require("path");
const { OPERATIONS } = require("../benchmarks/lib/operations");
const { ALL_SUBSTRATES } = require("../benchmarks/adapters");
const { writeCSV, writeText, markdownMatrix, latexMatrix } = require("../benchmarks/lib/exporters");

const BASELINE = "erc1056";

function load(runDir, name) {
  const f = path.join(runDir, `${name}.json`);
  return fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, "utf8")) : null;
}

function emit(runDir, name, spec, footer) {
  const dir = path.join(runDir, "tables");
  writeText(path.join(dir, `${name}.md`), markdownMatrix({ ...spec, footer: `_${footer}_` }));
  writeText(path.join(dir, `${name}.tex`), latexMatrix({ ...spec, caption: spec.title, label: `tab:${name}`, footer }));
  const rows = spec.rowKeys.map((r) => { const o = { [spec.rowLabel]: spec.rowLabels ? spec.rowLabels[r] || r : r }; for (const c of spec.colKeys) o[c] = spec.cellFn(r, c); return o; });
  writeCSV(path.join(dir, `${name}.csv`), rows);
  return markdownMatrix(spec);
}

const ratio = (a, b) => (a == null || b == null || b === 0 ? null : Math.round((a / b) * 100) / 100);

function buildAnalysis(runDir) {
  const meta = JSON.parse(fs.readFileSync(path.join(runDir, "meta.json"), "utf8"));
  const crud = load(runDir, "crud") || [];
  const life = load(runDir, "lifecycle") || [];
  const scale = load(runDir, "scale") || [];
  const resolve = load(runDir, "resolve") || [];
  const adapters = meta.adapters;
  const colLabels = Object.fromEntries(ALL_SUBSTRATES.map((s) => [s.id, s.label]));
  const footer = `Run ${meta.runId} · computed from crud/lifecycle/scale/resolve.json · baseline ${colLabels[BASELINE]}`;
  const out = [`# Analysis — ${meta.runId}`, "", `_${footer}_`, ""];

  const crudIdx = new Map(crud.map((r) => [`${r.adapter}|${r.op}`, r]));
  const lifeIdx = Object.fromEntries(life.map((l) => [l.adapter, l]));
  const resIdx = new Map(resolve.map((r) => [`${r.adapter}|${r.op}`, r]));
  const h50 = new Map(scale.filter((r) => r.axis === "h" && r.op === "R3_resolve_document").map((r) => [`${r.adapter}|${r.value}`, r]));
  const maxH = Math.max(...scale.filter((r) => r.axis === "h").map((r) => r.value));
  const gas = (a, op) => { const r = crudIdx.get(`${a}|${op}`); return r && r.supported !== false ? r.gasUsed : null; };

  // ---- 1. Ratios vs baseline -------------------------------------------------
  const ratioOps = ["C1_create_identity", "C2_create_with_attributes", "U3_set_attribute", "U4_transfer_vehicle", "V3_anchor_status", "V5_revoke_credential"];
  const ratioRows = [...ratioOps, "LIFETIME", "Z2NZ", "TXCOUNT"];
  const ratioLabels = Object.fromEntries(ratioOps.map((o) => [o, `${o} (× baseline)`]));
  Object.assign(ratioLabels, { LIFETIME: "Lifetime gas (× baseline)", Z2NZ: "Zero→nonzero SSTOREs (× baseline)", TXCOUNT: "Lifetime transactions (× baseline)" });
  const spec1 = { title: "A1 — Cost relative to the ERC-1056 baseline (ratio; >1 = more expensive; n/a = no primitive; † = lifetime excludes n/a events)", rowLabel: "Quantity", rowKeys: ratioRows, rowLabels: ratioLabels, colKeys: adapters, colLabels,
    cellFn: (r, a) => {
      const b = lifeIdx[BASELINE], l = lifeIdx[a];
      if (r === "LIFETIME") return l ? `${ratio(l.lifetimeGas, b.lifetimeGas)}${l.skippedEvents && l.skippedEvents.length ? "†" : ""}` : null;
      if (r === "Z2NZ") return l ? ratio(l.lifetimeZeroToNonzeroSstores, b.lifetimeZeroToNonzeroSstores) : null;
      if (r === "TXCOUNT") return l ? ratio(l.lifetimeTxCount, b.lifetimeTxCount) : null;
      const g = gas(a, r); return g == null ? "n/a" : ratio(g, gas(BASELINE, r));
    } };
  out.push(emit(runDir, "analysis_ratios", spec1, footer));

  // ---- 2. Capability matrix ---------------------------------------------------
  const coreOps = OPERATIONS.filter((o) => o.core).map((o) => o.id);
  const supported = (a, op) => { const r = crudIdx.get(`${a}|${op}`); return r ? r.supported !== false : null; };
  const capRows = [...OPERATIONS.map((o) => o.id), "SUPPORTED_CORE", "UNSUPPORTED_LIST"];
  const capLabels = Object.fromEntries(OPERATIONS.map((o) => [o.id, `${o.id}${o.core ? "" : " (optional)"}`]));
  Object.assign(capLabels, { SUPPORTED_CORE: "**Core ops supported**", UNSUPPORTED_LIST: "Missing primitives" });
  const spec2 = { title: "A2 — Capability matrix: ✓ primitive present, ✗ none (reportable finding)", rowLabel: "Operation", rowKeys: capRows, rowLabels: capLabels, colKeys: adapters, colLabels,
    cellFn: (r, a) => {
      if (r === "SUPPORTED_CORE") return `${coreOps.filter((o) => supported(a, o)).length}/${coreOps.length}`;
      if (r === "UNSUPPORTED_LIST") { const m = OPERATIONS.filter((o) => supported(a, o.id) === false).map((o) => o.id.split("_")[0]); return m.length ? m.join(" ") : "—"; }
      const s = supported(a, r); return s === null ? "?" : s ? "✓" : "✗";
    } };
  out.push(emit(runDir, "analysis_capabilities", spec2, footer));

  // ---- 3. H5 dominance / Pareto ---------------------------------------------
  // Criteria (framework §8, H5): lower is better unless noted.
  const crit = [
    { id: "lifetime", label: "Lifetime gas", lower: true, get: (a) => lifeIdx[a]?.lifetimeGas },
    { id: "z2nz", label: "Zero→nonzero SSTOREs", lower: true, get: (a) => lifeIdx[a]?.lifetimeZeroToNonzeroSstores },
    { id: "r3rpc", label: `R3 RPC calls at h=${maxH}`, lower: true, get: (a) => h50.get(`${a}|${maxH}`)?.readRpcCalls },
    { id: "r3ms", label: "R3 median ms after lifecycle", lower: true, get: (a) => resIdx.get(`${a}|R3_resolve_document`)?.latency?.median },
    { id: "caps", label: "Core ops supported", lower: false, get: (a) => coreOps.filter((o) => supported(a, o)).length },
    { id: "onchainVerify", label: "O(1) on-chain credential check (view)", lower: false, get: (a) => (["erc735", "erc1155", "erc725", "erc725xy", "lsp8", "erc4337", "cvin", "erc721"].includes(a) ? 1 : 0) },
  ];
  const vals = Object.fromEntries(adapters.map((a) => [a, Object.fromEntries(crit.map((c) => [c.id, c.get(a)]))]));
  const better = (c, x, y) => (c.lower ? x < y : x > y);
  const notWorse = (c, x, y) => (c.lower ? x <= y : x >= y);
  const dominates = (a, b, ids) => ids.every((id) => notWorse(crit.find((c) => c.id === id), vals[a][id], vals[b][id])) && ids.some((id) => better(crit.find((c) => c.id === id), vals[a][id], vals[b][id]));
  const sets = {
    cost: ["lifetime", "z2nz"],
    costRead: ["lifetime", "z2nz", "r3rpc", "r3ms"],
    all: crit.map((c) => c.id),
  };
  const dom = {};
  for (const [name, ids] of Object.entries(sets)) {
    dom[name] = Object.fromEntries(adapters.map((a) => [a, adapters.filter((b) => b !== a && dominates(b, a, ids))]));
  }
  const paretoRows = [...crit.map((c) => c.id), "DOM_COST", "DOM_COSTREAD", "DOM_ALL"];
  const paretoLabels = Object.fromEntries(crit.map((c) => [c.id, c.label + (c.lower ? " ↓" : " ↑")]));
  Object.assign(paretoLabels, { DOM_COST: "**Dominated by** (cost axes: lifetime, SSTOREs)", DOM_COSTREAD: "**Dominated by** (cost + read path)", DOM_ALL: "**Dominated by** (all six criteria)" });
  const spec3 = { title: "A3 — H5 dominance analysis: a substrate is dominated if another is at least as good on every listed criterion and better on one. '—' = on the Pareto frontier for that criterion set", rowLabel: "Criterion", rowKeys: paretoRows, rowLabels: paretoLabels, colKeys: adapters, colLabels,
    cellFn: (r, a) => {
      if (r.startsWith("DOM_")) { const key = { DOM_COST: "cost", DOM_COSTREAD: "costRead", DOM_ALL: "all" }[r]; const d = dom[key][a]; return d.length ? d.map((x) => colLabels[x]).join(", ") : "—"; }
      const v = vals[a][r]; return v == null ? null : r === "onchainVerify" ? (v ? "yes" : "no") : v;
    } };
  out.push(emit(runDir, "analysis_pareto", spec3, footer));

  // ---- 4. Frontier summary ----------------------------------------------------
  const frontier = Object.fromEntries(Object.entries(dom).map(([k, d]) => [k, adapters.filter((a) => d[a].length === 0)]));
  const lifeComparable = adapters.filter((a) => !(lifeIdx[a]?.skippedEvents || []).length);
  out.push("### A4 — Frontier summary", "",
    `- Pareto frontier on cost axes (lifetime gas, zero→nonzero SSTOREs): **${frontier.cost.map((a) => colLabels[a]).join(", ")}**`,
    `- Pareto frontier on cost + read path: **${frontier.costRead.map((a) => colLabels[a]).join(", ")}**`,
    `- Pareto frontier on all six criteria: **${frontier.all.map((a) => colLabels[a]).join(", ")}**`,
    `- Substrates whose lifetime total covers all 17 events (no n/a exclusions): ${lifeComparable.map((a) => colLabels[a]).join(", ")}; the others' totals are lower bounds (†).`,
    `- Baseline ${colLabels[BASELINE]} lifetime ${lifeIdx[BASELINE].lifetimeGas.toLocaleString("en-US")} gas; cheapest-to-dearest lifetime order: ${adapters.slice().sort((x, y) => lifeIdx[x].lifetimeGas - lifeIdx[y].lifetimeGas).map((a) => `${colLabels[a]} (${ratio(lifeIdx[a].lifetimeGas, lifeIdx[BASELINE].lifetimeGas)}×)`).join(" < ")}`,
    "", "Criterion 'O(1) on-chain credential check' is a design property (a contract can verify a credential with one view call), not a measurement; it is the axis on which the CVIN-Combined hybrid and the storage-based substrates beat the event-log substrates. It is assigned per adapter in `analysis/analysis.js` and must be stated with the table.", "");

  // ---- 5. W3C DID Method Rubric — measured inputs (docs/DID_METHOD_RUBRIC.md §1a) -------
  const eventLog = { erc1056: true, erc1056w: true, cvin: true };
  const txc = (a, op) => { const r = crudIdx.get(`${a}|${op}`); return r && r.supported !== false ? r.txCount : null; };
  const fmtGas = (a, op) => { const g = gas(a, op); return g == null ? "n/a" : `${g.toLocaleString("en-US")}${txc(a, op) > 1 ? ` (${txc(a, op)} tx)` : ""}`; };
  const rubricRows = ["R_3_2_5", "R_3_2_7", "R_3_2_7b", "R_3_2_8a", "R_3_2_8b", "R_3_2_8c", "R_3_3_2a", "R_3_3_2b", "R_3_4_1", "R_3_4_7", "R_3_4_8", "R_3_7_2"];
  const rubricLabels = {
    R_3_2_5: "3.2.5 Offline creation (identity exists before any tx?)",
    R_3_2_7: "3.2.7 ▲ Creation cost: C1 bind VIN (gas)",
    R_3_2_7b: "3.2.7 ▲ Creation incl. VID-I attributes: C2 (gas)",
    R_3_2_8a: "3.2.8 ▲ Update cost: U3 attribute (gas)",
    R_3_2_8b: "3.2.8 ▲ Controller rotation: U1 (gas)",
    R_3_2_8c: "3.2.8 ▲ Deletion: D3 deactivate (gas)",
    R_3_3_2a: `3.3.2 ▲ Limited-resource resolution: R3 RPC calls at h=${maxH}`,
    R_3_3_2b: "3.3.2 ▲ Resolution median ms after lifecycle",
    R_3_4_1: "3.4.1 Auditability: linked event chain vs state snapshot",
    R_3_4_7: "3.4.7 Verification relationships: delegate keys",
    R_3_4_8: "3.4.8 Relayed / signed operations (meta-tx)",
    R_3_7_2: "3.7.2 ▲ Incentive for many DIDs: lifetime gas × baseline",
  };
  const spec5 = { title: "A5 — W3C DID Method Rubric: measured inputs per criterion (▲ = quantitative cell fed by this run)", rowLabel: "Rubric criterion", rowKeys: rubricRows, rowLabels: rubricLabels, colKeys: adapters, colLabels,
    cellFn: (r, a) => {
      switch (r) {
        case "R_3_2_5": return eventLog[a] ? "yes (implicit identity; C1 only binds the VIN)" : "no (mint / deploy / register tx)";
        case "R_3_2_7": return fmtGas(a, "C1_create_identity");
        case "R_3_2_7b": return fmtGas(a, "C2_create_with_attributes");
        case "R_3_2_8a": return fmtGas(a, "U3_set_attribute");
        case "R_3_2_8b": return fmtGas(a, "U1_rotate_controller");
        case "R_3_2_8c": return fmtGas(a, "D3_deactivate_identity");
        case "R_3_3_2a": return h50.get(`${a}|${maxH}`)?.readRpcCalls ?? null;
        case "R_3_3_2b": return resIdx.get(`${a}|R3_resolve_document`)?.latency?.median ?? null;
        case "R_3_4_1": return eventLog[a] ? "full linked history (previousChange chain)" : (a === "erc735" || a === "erc721") ? "events + current state (no chain pointer)" : "current state (events unlinked)";
        case "R_3_4_7": return supported(a, "U2_add_delegate") ? (a === "erc4337" ? "recovery guardian only" : a === "erc721" ? "approval (no expiry)" : "delegates with TTL") : "none";
        case "R_3_4_8": return supported(a, "U5_meta_tx") ? "yes" : "no";
        case "R_3_7_2": { const l = lifeIdx[a]; return l ? `${ratio(l.lifetimeGas, lifeIdx[BASELINE].lifetimeGas)}${l.skippedEvents && l.skippedEvents.length ? "†" : ""}` : null; }
        default: return null;
      }
    } };
  out.push(emit(runDir, "analysis_rubric_inputs", spec5, footer));

  const json = { runId: meta.runId, baseline: BASELINE, criteria: crit.map(({ id, label, lower }) => ({ id, label, lower })), values: vals, dominatedBy: dom, frontier };
  fs.writeFileSync(path.join(runDir, "analysis.json"), JSON.stringify(json, null, 2));
  writeText(path.join(runDir, "ANALYSIS.md"), out.join("\n"));
  console.log(`analysis: ${path.join(runDir, "ANALYSIS.md")}`);
  console.log(`frontier (all six): ${frontier.all.join(", ")}`);
  return json;
}

if (require.main === module) buildAnalysis(process.argv[2] || path.join("results", "metrics", "latest"));
module.exports = { buildAnalysis };
