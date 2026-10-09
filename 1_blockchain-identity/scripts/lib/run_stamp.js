// Run stamp for results of record (plan 2026-10-09 P3.3; TSR S11): which code, clean or not,
// which toolchain. Spread into a producer's `metadata`. A result written with dirty: true is not
// a run of record (docs/STYLE_AND_RIGOUR_GUIDE.md §1.1 rule 6).
const { execSync } = require("child_process");
const path = require("path");

function git(args) {
  try {
    return execSync(`git ${args}`, { cwd: path.resolve(__dirname, "../.."), stdio: ["ignore", "pipe", "ignore"] }).toString().trim();
  } catch (e) {
    return null;
  }
}

function runStamp() {
  const status = git("status --porcelain");
  return {
    commit: git("rev-parse --short HEAD"),
    dirty: status === null ? null : status.length > 0,
    node: process.version,
    hardhat: (() => { try { return require("hardhat/package.json").version; } catch (e) { return null; } })(),
  };
}

module.exports = { runStamp };
