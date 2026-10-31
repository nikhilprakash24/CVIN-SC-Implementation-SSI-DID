#!/usr/bin/env node
/**
 * make_contract_api_docs.js — generate the contract API reference from NatSpec
 * (docs/smart-contracts/api/, one page per source file plus an index).
 *
 * Reads the solc AST from Hardhat build-info files (compile all three configs first), so the pages
 * are exactly what the compiler parsed: signatures, visibility, mutability, events, modifiers,
 * public state variables, and their @notice / @dev / @param / @return / @custom:* text.
 * The hand-written context (standards fidelity, usage, diagrams) stays in docs/smart-contracts/0*.md.
 *
 *   node tools/make_contract_api_docs.js           # write docs/smart-contracts/api/
 *   node tools/make_contract_api_docs.js --check   # exit 1 if any page is stale or missing
 */
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "docs/smart-contracts/api");
// [build-info dir, source-key prefix] for the three Hardhat configs in 1_blockchain-identity
const TREES = [
  ["1_blockchain-identity/artifacts/build-info", "contracts/"],
  ["phase2/idtx/artifacts/build-info", "phase2/idtx/contracts/"],
  ["5_zkp-agent-identity/hh-artifacts/build-info", "5_zkp-agent-identity/contracts/"],
];

function repoRelative(dir, src) {
  for (let d = path.resolve(ROOT, dir); d.startsWith(ROOT); d = path.dirname(d)) {
    const f = path.join(d, src);
    if (fs.existsSync(f) && fs.statSync(f).isFile()) return path.relative(ROOT, f);
  }
  return null;
}

function loadSources() {
  const out = new Map();
  for (const [dir, prefix] of TREES) {
    const abs = path.join(ROOT, dir);
    if (!fs.existsSync(abs)) throw new Error(`${dir}: missing; compile all three Hardhat configs first`);
    const files = fs.readdirSync(abs).filter((f) => f.endsWith(".json")).map((f) => path.join(abs, f))
      .sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
    for (const f of files) {
      const { output } = JSON.parse(fs.readFileSync(f, "utf8"));
      for (const [src, { ast }] of Object.entries(output.sources || {})) {
        if (!src.startsWith(prefix)) continue;
        const rel = repoRelative(dir, src);
        if (rel && !out.has(rel)) out.set(rel, ast); // newest build-info wins
      }
    }
  }
  return new Map([...out].sort(([a], [b]) => a.localeCompare(b)));
}

// Split a NatSpec text into { notice, dev, params: {name: text}, returns: [text], custom: [[tag, text]] }.
function parseDoc(node) {
  const raw = node.documentation ? (typeof node.documentation === "string" ? node.documentation : node.documentation.text) : "";
  const doc = { notice: [], dev: [], params: {}, returns: [], custom: [], title: [], author: [], inheritdoc: [] };
  let cur = null;
  for (const line of raw.split("\n")) {
    const m = line.match(/^\s*@(\S+)\s?(.*)$/);
    if (m) {
      const [, tag, rest] = m;
      if (tag === "param") { const [n, ...t] = rest.split(/\s+/); doc.params[n] = [t.join(" ")]; cur = doc.params[n]; }
      else if (tag === "return") { doc.returns.push([rest]); cur = doc.returns[doc.returns.length - 1]; }
      else if (tag === "notice" || tag === "dev") { doc[tag].push(rest); cur = doc[tag]; }
      else if (tag === "title" || tag === "author" || tag === "inheritdoc") { doc[tag].push(rest); cur = doc[tag]; }
      else if (tag.startsWith("custom:")) { doc.custom.push([tag.slice(7), [rest]]); cur = doc.custom[doc.custom.length - 1][1]; }
      else cur = null;
    } else if (cur) cur.push(line.trim());
    else if (line.trim()) { doc.notice.push(line.trim()); cur = doc.notice; } // untagged text is @notice; later lines continue it
  }
  const j = (a) => a.join(" ").replace(/\s+/g, " ").trim();
  // notice/dev keep "- item" lines as a markdown list (blank line before the first item)
  const jl = (a) => a.reduce((acc, l) => {
    if (/^[-*] /.test(l)) return acc + (acc && !/\n- [^\n]*$/.test(acc) ? "\n\n" : "\n") + "- " + l.slice(2).trim();
    if (!l) return acc;
    return acc + (/\n- [^\n]*$/.test(acc) ? "\n\n" : acc ? " " : "") + l.trim();
  }, "").trim();
  return {
    title: j(doc.title), author: j(doc.author), inheritdoc: j(doc.inheritdoc),
    notice: jl(doc.notice), dev: jl(doc.dev),
    params: Object.fromEntries(Object.entries(doc.params).map(([k, v]) => [k, j(v)])),
    returns: doc.returns.map(j), custom: doc.custom.map(([t, v]) => [t, j(v)]),
  };
}

const typeOf = (p) => (p.typeName && p.typeName.typeDescriptions ? p.typeName.typeDescriptions.typeString : p.typeDescriptions.typeString)
  .replace(/^contract /, "").replace(/^struct /, "").replace(/^enum /, "").replace(/ (storage|memory|calldata) pointer$/, "").replace(/ (storage|memory|calldata)$/, "");
const paramList = (ps) => ps.map((p) => `${typeOf(p)}${p.indexed ? " indexed" : ""}${p.name ? " " + p.name : ""}`).join(", ");
const esc = (s) => s.replace(/\|/g, "\\|");

function docBlock(d, lines) {
  if (d.notice) lines.push(d.notice, "");
  if (d.dev) lines.push(`*Dev:* ${d.dev}`, "");
  if (d.inheritdoc) lines.push(`*Inherits documentation from* \`${d.inheritdoc}\`.`, "");
  for (const [tag, text] of d.custom) lines.push(`- **${tag}:** ${text}`);
  if (d.custom.length) lines.push("");
}

function memberSection(heading, nodes, render, lines) {
  if (!nodes.length) return;
  lines.push(`### ${heading}`, "");
  for (const n of nodes) render(n, lines);
}

function renderFunctionLike(kindLabel) {
  return (n, lines) => {
    const d = parseDoc(n);
    const name = n.kind === "constructor" ? "constructor" : n.name;
    const params = n.parameters ? n.parameters.parameters : [];
    const rets = n.returnParameters ? n.returnParameters.parameters : [];
    const mods = (n.modifiers || []).filter((m) => m.kind !== "baseConstructorSpecifier").map((m) => m.modifierName.name);
    const quals = [n.nodeType === "FunctionDefinition" ? n.visibility : null,
      n.stateMutability && n.stateMutability !== "nonpayable" ? n.stateMutability : null, ...mods].filter(Boolean).join(" ");
    lines.push(`#### \`${name}\``, "",
      "```solidity", `${name === "constructor" ? "constructor" : `${kindLabel} ${name}`}(${paramList(params)})${quals ? " " + quals : ""}${rets.length ? ` returns (${paramList(rets)})` : ""}`, "```", "");
    docBlock(d, lines);
    const named = params.filter((p) => p.name);
    if (named.length) {
      lines.push("| Parameter | Type | Description |", "|---|---|---|");
      for (const p of named) lines.push(`| \`${p.name}\` | \`${esc(typeOf(p))}\` | ${esc(d.params[p.name] || "")} |`);
      lines.push("");
    }
    if (rets.length && d.returns.length) {
      lines.push("**Returns:** " + d.returns.map((r) => esc(r)).join("; "), "");
    }
  };
}

function renderSource(rel, ast) {
  const lines = [`# \`${path.basename(rel)}\``, "",
    `Source: \`${rel}\` · generated by \`tools/make_contract_api_docs.js\` from the compiler's NatSpec — do not edit by hand.`, ""];
  for (const c of ast.nodes.filter((n) => n.nodeType === "ContractDefinition")) {
    const d = parseDoc(c);
    const bases = (c.baseContracts || []).map((b) => b.baseName.name || b.baseName.namePath).filter(Boolean);
    lines.push(`## ${c.contractKind} \`${c.name}\`${bases.length ? ` is ${bases.map((b) => `\`${b}\``).join(", ")}` : ""}`, "");
    if (d.title) lines.push(`**${d.title}**${d.author ? ` · ${d.author}` : ""}`, "");
    docBlock(d, lines);
    const of = (t, pred = () => true) => c.nodes.filter((n) => n.nodeType === t && pred(n));
    const exposed = (n) => n.visibility === "public" || n.visibility === "external";
    memberSection("Constructor", of("FunctionDefinition", (n) => n.kind === "constructor"), renderFunctionLike("constructor"), lines);
    memberSection("Functions", of("FunctionDefinition", (n) => n.kind === "function" && exposed(n)), renderFunctionLike("function"), lines);
    memberSection("Events", of("EventDefinition"), renderFunctionLike("event"), lines);
    memberSection("Errors", of("ErrorDefinition"), renderFunctionLike("error"), lines);
    memberSection("Modifiers", of("ModifierDefinition"), renderFunctionLike("modifier"), lines);
    const vars = of("VariableDeclaration", (n) => n.visibility === "public");
    if (vars.length) {
      lines.push("### Public state variables", "", "| Name | Type | Description |", "|---|---|---|");
      for (const v of vars) {
        const d2 = parseDoc(v);
        lines.push(`| \`${v.name}\`${v.constant ? " (constant)" : v.mutability === "immutable" ? " (immutable)" : ""} | \`${esc(typeOf(v))}\` | ${esc([d2.notice, d2.dev].filter(Boolean).join(" "))} |`);
      }
      lines.push("");
    }
  }
  return lines.join("\n").replace(/\n{3,}/g, "\n\n").trimEnd() + "\n";
}

function main() {
  const check = process.argv.includes("--check");
  const sources = loadSources();
  const pages = new Map();
  const index = ["# Contract API reference", "",
    "Generated by `tools/make_contract_api_docs.js` from the NatSpec in the sources, as the compiler parsed it.",
    "Context, standards fidelity, usage and diagrams: [the catalog](../README.md).", "",
    "| Source | Contracts / interfaces |", "|---|---|"];
  for (const [rel, ast] of sources) {
    const page = rel.replace(/\.sol$/, ".md").replace(/\//g, "__");
    pages.set(page, renderSource(rel, ast));
    const names = ast.nodes.filter((n) => n.nodeType === "ContractDefinition").map((c) => `\`${c.name}\``).join(", ");
    index.push(`| [${rel}](${page}) | ${names} |`);
  }
  pages.set("README.md", index.join("\n") + "\n");
  const stale = [];
  if (!check) fs.mkdirSync(OUT, { recursive: true });
  const existing = fs.existsSync(OUT) ? fs.readdirSync(OUT) : [];
  for (const [name, text] of pages) {
    const p = path.join(OUT, name);
    if (check) { if (!fs.existsSync(p) || fs.readFileSync(p, "utf8") !== text) stale.push(name); }
    else fs.writeFileSync(p, text);
  }
  for (const f of existing) if (!pages.has(f)) { if (check) stale.push(`${f} (no longer generated)`); else fs.rmSync(path.join(OUT, f)); }
  if (check) {
    if (stale.length) { console.error(`STALE contract API docs (run node tools/make_contract_api_docs.js): ${stale.join(", ")}`); process.exit(1); }
    console.log(`contract API docs current (${pages.size - 1} source pages)`);
  } else console.log(`wrote ${path.relative(ROOT, OUT)}/ (${pages.size - 1} source pages + index)`);
}

main();
