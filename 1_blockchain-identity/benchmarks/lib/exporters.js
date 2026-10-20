"use strict";
const fs = require("fs");
const path = require("path");
const { bigintReplacer } = require("./MetricsCollector");

function writeJSON(file, obj) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(obj, bigintReplacer, 2));
}

function csvEscape(v) {
  if (v === null || v === undefined) return "";
  const s = typeof v === "object" ? JSON.stringify(v) : String(v);
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}

function writeCSV(file, rows, columns) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const cols = columns || [...new Set(rows.flatMap((r) => Object.keys(r)))];
  const lines = [cols.join(",")];
  for (const r of rows) lines.push(cols.map((c) => csvEscape(flatten(r, c))).join(","));
  fs.writeFileSync(file, lines.join("\n") + "\n");
}

function flatten(row, col) {
  // supports dotted paths like latency.median
  return col.split(".").reduce((o, k) => (o == null ? undefined : o[k]), row);
}

function fmt(v) {
  if (v === null || v === undefined) return "n/a";
  if (typeof v === "number") return Number.isInteger(v) ? v.toLocaleString("en-US") : v.toFixed(2);
  return String(v);
}

/**
 * Matrix: rows = rowKeys (ordered), columns = colKeys (ordered), cell = cellFn(row, col) → string|null.
 */
function markdownMatrix({ title, rowLabel, rowKeys, rowLabels, colKeys, colLabels, cellFn, footer }) {
  const out = [];
  if (title) out.push(`### ${title}`, "");
  out.push(`| ${rowLabel} | ${colKeys.map((c) => colLabels[c] || c).join(" | ")} |`);
  out.push(`|---|${colKeys.map(() => "---:").join("|")}|`);
  for (const r of rowKeys) {
    out.push(`| ${rowLabels ? rowLabels[r] || r : r} | ${colKeys.map((c) => fmt(cellFn(r, c))).join(" | ")} |`);
  }
  if (footer) out.push("", footer);
  return out.join("\n") + "\n";
}

function latexMatrix({ caption, label, rowLabel, rowKeys, rowLabels, colKeys, colLabels, cellFn, footer }) {
  const esc = (s) => String(s).replace(/([_%&#])/g, "\\$1");
  const out = [];
  out.push("\\begin{table}[ht]", "\\centering", "\\small");
  out.push(`\\begin{tabular}{l${"r".repeat(colKeys.length)}}`, "\\toprule");
  out.push(`${esc(rowLabel)} & ${colKeys.map((c) => esc(colLabels[c] || c)).join(" & ")} \\\\`, "\\midrule");
  for (const r of rowKeys) {
    out.push(`${esc(rowLabels ? rowLabels[r] || r : r)} & ${colKeys.map((c) => esc(fmt(cellFn(r, c)))).join(" & ")} \\\\`);
  }
  out.push("\\bottomrule", "\\end{tabular}");
  if (caption) out.push(`\\caption{${esc(caption)}${footer ? " " + esc(footer) : ""}}`);
  if (label) out.push(`\\label{${label}}`);
  out.push("\\end{table}");
  return out.join("\n") + "\n";
}

function writeText(file, text) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, text);
}

module.exports = { writeJSON, writeCSV, writeText, markdownMatrix, latexMatrix, fmt };
