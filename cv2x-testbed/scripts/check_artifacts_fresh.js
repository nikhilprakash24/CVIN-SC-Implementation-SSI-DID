#!/usr/bin/env node
/**
 * check_artifacts_fresh.js — fail if the tracked cv2x-testbed artifacts are
 * stale (REVIEW_02 Q-9).
 *
 * The Python providers, tests/conftest.py and experiment_pki_vs_erc1056.py
 * --deploy load artifacts/contracts/** and contracts/ERC1056Registry_{abi.json,
 * bytecode.txt} WITHOUT a compile step, so a source change that is not
 * followed by a recompile silently deploys old bytecode. This script compiles
 * the current contracts/*.sol with the testbed's own hardhat.config.js
 * (solc 0.8.20, optimizer 200, evm paris) into a scratch directory and compares
 * abi + bytecode + deployedBytecode with the tracked copies.
 *
 * Run:  cd cv2x-testbed && npm run check:artifacts
 * Fix:  cd cv2x-testbed && npx hardhat compile, then write the ABI/bytecode
 *       files (scripts/deploy.js does this) and commit.
 * Exit: 0 = fresh, 1 = stale or missing.
 */
const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");

const ROOT = path.resolve(__dirname, "..");
const CONTRACTS = ["ERC1056Registry", "MOBIVIDRegistry", "MOBIVIDRegistryV2"];

function load(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function main() {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "cv2x-artifacts-"));
  try {
    execFileSync("npx", ["hardhat", "compile", "--force", "--quiet"], {
      cwd: ROOT,
      stdio: ["ignore", "ignore", "inherit"],
      env: {
        ...process.env,
        CV2X_ARTIFACTS_DIR: path.join(tmp, "artifacts"),
        CV2X_CACHE_DIR: path.join(tmp, "cache"),
      },
    });
    const problems = [];
    for (const name of CONTRACTS) {
      const rel = path.join("artifacts", "contracts", `${name}.sol`, `${name}.json`);
      const trackedPath = path.join(ROOT, rel);
      if (!fs.existsSync(trackedPath)) {
        problems.push(`${rel}: missing`);
        continue;
      }
      const tracked = load(trackedPath);
      const fresh = load(path.join(tmp, rel));
      for (const field of ["bytecode", "deployedBytecode"]) {
        if (tracked[field] !== fresh[field]) problems.push(`${rel}: ${field} differs from a fresh compile`);
      }
      if (JSON.stringify(tracked.abi) !== JSON.stringify(fresh.abi)) {
        problems.push(`${rel}: abi differs from a fresh compile`);
      }
    }
    // Flat copies read by identity/erc1056_provider.py.
    const fresh1056 = load(path.join(tmp, "artifacts", "contracts", "ERC1056Registry.sol", "ERC1056Registry.json"));
    const bc = fs.readFileSync(path.join(ROOT, "contracts", "ERC1056Registry_bytecode.txt"), "utf8").trim();
    if (bc !== fresh1056.bytecode) problems.push("contracts/ERC1056Registry_bytecode.txt differs from a fresh compile");
    const abi = load(path.join(ROOT, "contracts", "ERC1056Registry_abi.json"));
    if (JSON.stringify(abi) !== JSON.stringify(fresh1056.abi)) problems.push("contracts/ERC1056Registry_abi.json differs from a fresh compile");

    if (problems.length) {
      console.error("STALE cv2x-testbed artifacts:\n  " + problems.join("\n  "));
      process.exit(1);
    }
    console.log(`cv2x-testbed artifacts are fresh (${CONTRACTS.join(", ")} + ERC1056Registry_{abi,bytecode}).`);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
}

main();
