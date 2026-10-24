#!/usr/bin/env node
/**
 * bytecode_manifest.js — pin the executable bytecode of every project contract, ignoring the CBOR
 * metadata tail that comment edits change (docs/smart-contracts/00-architecture.md §5).
 *
 * A comment-only edit (NatSpec, typo fixes) changes only the metadata hash, so --check still passes.
 * Any edit that changes behaviour (code, constants, compiler settings) changes the stripped
 * bytecode or the ABI and fails --check until the manifest is regenerated with --write. That makes
 * "this PR changed contract code" an explicit, reviewable diff of the manifest, next to the gas
 * results that may need re-measuring.
 *
 *   node tools/bytecode_manifest.js --write   # after compiling all three Hardhat configs
 *   node tools/bytecode_manifest.js --check
 *
 * Exit: 0 = matches, 1 = differs or an artifact is missing.
 */
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const MANIFEST = path.join(ROOT, "docs/smart-contracts/bytecode-manifest.json");
// Artifact trees of the three Hardhat configs in 1_blockchain-identity (main, phase2, zkp).
const TREES = [
  "1_blockchain-identity/artifacts/contracts",
  "phase2/idtx/artifacts/phase2",
  "5_zkp-agent-identity/hh-artifacts/5_zkp-agent-identity",
];
// solc appends a2 64 'ipfs' <34-byte multihash> 64 'solc' <3-byte version> 0033; creation code also
// embeds the runtime code, so every occurrence is removed.
const METADATA = /a264697066735822[0-9a-f]{68}64736f6c6343[0-9a-f]{6}0033/g;

const sha = (s) => crypto.createHash("sha256").update(s).digest("hex");

function collect() {
  const out = {};
  for (const tree of TREES) {
    const abs = path.join(ROOT, tree);
    if (!fs.existsSync(abs)) throw new Error(`${tree}: missing; compile first`);
    (function walk(d) {
      for (const f of fs.readdirSync(d)) {
        const p = path.join(d, f);
        if (fs.statSync(p).isDirectory()) walk(p);
        else if (f.endsWith(".json") && !f.endsWith(".dbg.json")) {
          const a = JSON.parse(fs.readFileSync(p, "utf8"));
          if (!a.bytecode || a.bytecode === "0x") continue; // interfaces, abstract contracts
          out[`${a.sourceName}:${a.contractName}`] = {
            creation: sha(a.bytecode.replace(METADATA, "")),
            runtime: sha(a.deployedBytecode.replace(METADATA, "")),
            abi: sha(JSON.stringify(a.abi)),
          };
        }
      }
    })(abs);
  }
  return Object.fromEntries(Object.entries(out).sort(([a], [b]) => a.localeCompare(b)));
}

const mode = process.argv[2];
const now = collect();
if (mode === "--write") {
  fs.writeFileSync(MANIFEST, JSON.stringify(now, null, 1) + "\n");
  console.log(`wrote ${path.relative(ROOT, MANIFEST)} (${Object.keys(now).length} contracts)`);
} else if (mode === "--check") {
  const pinned = JSON.parse(fs.readFileSync(MANIFEST, "utf8"));
  const problems = [];
  for (const k of new Set([...Object.keys(pinned), ...Object.keys(now)])) {
    if (!pinned[k]) problems.push(`${k}: new contract (not in the manifest)`);
    else if (!now[k]) problems.push(`${k}: in the manifest but not compiled`);
    else for (const f of ["creation", "runtime", "abi"]) if (pinned[k][f] !== now[k][f]) problems.push(`${k}: ${f} changed`);
  }
  if (problems.length) {
    console.error("Contract code changed (not just comments):\n  " + problems.join("\n  ") +
      "\nIf intended: re-measure affected gas results, then run node tools/bytecode_manifest.js --write.");
    process.exit(1);
  }
  console.log(`bytecode manifest matches (${Object.keys(now).length} contracts; metadata ignored)`);
} else {
  console.error("usage: bytecode_manifest.js --write | --check");
  process.exit(2);
}
