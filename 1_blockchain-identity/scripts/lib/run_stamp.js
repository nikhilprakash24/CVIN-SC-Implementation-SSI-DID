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

// The code that produces a number: if any of these paths differs from the commit, the run is not
// a run of record. Results files are excluded on purpose, so a producer's own output (or an
// earlier producer's in the same session) does not mark the next run dirty. Same rule as the
// metrics harness's `dirtyMeasured` (1_blockchain-identity/benchmarks/run.js).
const MEASURED = ["1_blockchain-identity/contracts", "1_blockchain-identity/scripts", "1_blockchain-identity/hardhat.config.js",
  "1_blockchain-identity/package-lock.json", "cv2x-testbed/contracts"];

// Pathspecs are anchored at the repository root with :(top). git runs with cwd 1_blockchain-identity,
// where a plain "1_blockchain-identity/contracts" would resolve to a path that does not exist and the
// flag could never be true (the fault found in after-action report 11; stamps written before the fix
// carry an inert `dirty` and are vouched for by `dirtyAnyFile` or by hand).
const PATHSPECS = MEASURED.map((p) => `':(top)${p}'`).join(" ");

function runStamp() {
  const status = git("status --porcelain -- " + PATHSPECS);
  const whole = git("status --porcelain");
  return {
    commit: git("rev-parse --short HEAD"),
    dirty: status === null ? null : status.length > 0,
    dirtyAnyFile: whole === null ? null : whole.length > 0,
    node: process.version,
    hardhat: (() => { try { return require("hardhat/package.json").version; } catch (e) { return null; } })(),
  };
}

module.exports = { runStamp, MEASURED };
