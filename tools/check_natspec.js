#!/usr/bin/env node
/**
 * check_natspec.js — fail if a project contract lacks NatSpec (docs/smart-contracts/00-architecture.md §4).
 *
 * Reads the solc AST from Hardhat build-info files (compile first) and checks, for every source file
 * under the given source roots:
 *   - each contract / interface / library has a doc block with @title or @notice;
 *   - each public/external function, constructor, event, modifier and public state variable has a doc
 *     block (or @inheritdoc);
 *   - every named parameter is covered by an `@param <name>` and every function with return values has
 *     at least one `@return` (a doc block using @inheritdoc is exempt).
 *
 *   node tools/check_natspec.js <build-info dir> <source-key prefix>[,<prefix>...] [<build-info dir> <prefixes> ...]
 *
 *   e.g. node tools/check_natspec.js 1_blockchain-identity/artifacts/build-info contracts/ \
 *          phase2/idtx/artifacts/build-info phase2/idtx/contracts/ \
 *          5_zkp-agent-identity/hh-artifacts/build-info 5_zkp-agent-identity/contracts/
 *
 * Exempt: 5_zkp-agent-identity/contracts/Groth16Verifier.sol (snarkjs output, pinned by sha256 in
 * 5_zkp-agent-identity/artifacts/MANIFEST.json). Exit 0 = complete, 1 = gaps (listed).
 */
const fs = require("fs");
const path = require("path");

const EXEMPT = new Set(["5_zkp-agent-identity/contracts/Groth16Verifier.sol"]);

function docText(node) {
  const d = node.documentation;
  if (!d) return null;
  return typeof d === "string" ? d : d.text || "";
}

function checkParams(where, node, text, problems) {
  if (/@inheritdoc\b/.test(text)) return;
  for (const p of (node.parameters && node.parameters.parameters) || []) {
    if (p.name && !new RegExp(`@param\\s+${p.name}\\b`).test(text)) problems.push(`${where}: no @param ${p.name}`);
  }
  const rets = (node.returnParameters && node.returnParameters.parameters) || [];
  if (rets.length && !/@return\b/.test(text)) problems.push(`${where}: no @return`);
}

function checkSource(file, ast, problems) {
  for (const c of ast.nodes.filter((n) => n.nodeType === "ContractDefinition")) {
    const ctext = docText(c);
    if (!ctext || !/@(title|notice)\b/.test(ctext)) problems.push(`${file}: ${c.contractKind} ${c.name}: no @title/@notice`);
    for (const n of c.nodes) {
      const where = `${file}: ${c.name}.${n.name || n.kind}`;
      if (n.nodeType === "FunctionDefinition") {
        const exposed = n.visibility === "public" || n.visibility === "external" || n.kind === "constructor";
        if (!exposed || n.kind === "receive" || n.kind === "fallback") continue;
        const t = docText(n);
        if (t === null) { problems.push(`${where}: undocumented`); continue; }
        checkParams(where, n, t, problems);
      } else if (n.nodeType === "EventDefinition" || n.nodeType === "ModifierDefinition") {
        const t = docText(n);
        if (t === null) { problems.push(`${where}: undocumented`); continue; }
        checkParams(where, n, t, problems);
      } else if (n.nodeType === "VariableDeclaration" && n.visibility === "public") {
        if (docText(n) === null) problems.push(`${where}: undocumented public state variable`);
      }
    }
  }
}

function repoRelative(dir, src) {
  const repo = path.resolve(__dirname, "..");
  for (let d = path.resolve(dir); d.startsWith(repo); d = path.dirname(d)) {
    const f = path.join(d, src);
    if (fs.existsSync(f) && fs.statSync(f).isFile()) return path.relative(repo, f);
  }
  return null;
}

function main(argv) {
  if (argv.length < 2 || argv.length % 2) {
    console.error("usage: check_natspec.js <build-info dir> <prefix[,prefix]> [...]");
    process.exit(2);
  }
  const problems = [];
  const seen = new Set();
  for (let i = 0; i < argv.length; i += 2) {
    const dir = argv[i];
    const prefixes = argv[i + 1].split(",");
    const files = fs.readdirSync(dir).filter((f) => f.endsWith(".json"))
      .map((f) => path.join(dir, f)).sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
    for (const f of files) {
      const out = JSON.parse(fs.readFileSync(f, "utf8")).output;
      for (const [src, { ast }] of Object.entries(out.sources || {})) {
        // build-info keys are relative to the Hardhat root (an ancestor of the build-info dir)
        if (!prefixes.some((p) => src.startsWith(p))) continue;
        const rel = repoRelative(dir, src);
        if (!rel || seen.has(rel) || EXEMPT.has(rel)) continue;
        seen.add(rel); // newest build-info wins
        checkSource(rel, ast, problems);
      }
    }
  }
  if (!seen.size) { console.error("no matching sources: compile first"); process.exit(1); }
  if (problems.length) {
    console.error(`NatSpec gaps (${problems.length}):\n  ` + problems.join("\n  "));
    process.exit(1);
  }
  console.log(`NatSpec complete for ${seen.size} source files.`);
}

main(process.argv.slice(2));
