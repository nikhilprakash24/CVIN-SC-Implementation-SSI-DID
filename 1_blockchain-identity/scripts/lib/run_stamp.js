// Run stamp for results of record (plan 2026-10-09 P3.3; TSR S11; WM-2 step A2, defect D49): which
// code, clean or not, which toolchain. Spread into a producer's `metadata`. A result written with
// dirty: true is not a run of record (docs/STYLE_AND_RIGOUR_GUIDE.md §1.1 rule 6).
//
// The producing code is the producer's own scope, read from tools/run_identity/scopes.json (generated
// from producers.json by tools/run_identity/stamp.py, which the Python producers use too): the producer
// file, its relative-require closure, and its declared inputs (contracts, Hardhat config, lockfile).
// Results directories are excluded, so a producer's own output does not mark the next run dirty.
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "../../..");
const SCOPES = path.join(ROOT, "tools/run_identity/scopes.json");

function git(args) {
  try {
    // cwd is the repository root and every pathspec is :(top)-anchored, so the flag does not depend on
    // where the producer was started (the fault of after-action report 11).
    return execFileSync("git", args, { cwd: ROOT, stdio: ["ignore", "pipe", "ignore"] }).toString().trim();
  } catch (e) {
    return null;
  }
}

function scopeOf(producer) {
  const key = path.relative(ROOT, path.resolve(producer)).split(path.sep).join("/");
  const doc = JSON.parse(fs.readFileSync(SCOPES, "utf8"));
  const scope = doc.scopes[key];
  if (!scope) throw new Error(`${key} is not a producer of record (tools/run_identity/producers.json)`);
  return { key, paths: scope.paths, exclude: doc.exclude };
}

function pathspecs(paths, exclude) {
  return paths.map((p) => `:(top)${p}`).concat(exclude.map((g) => `:(top,exclude,glob)${g}`));
}

// `producer` is the producer's own file (pass __filename). Field names are kept from the first version
// so docs/testing/check_stamps.py reads old and new stamps alike; `scope*` are new.
function runStamp(producer) {
  if (!producer) throw new Error("runStamp(producer): pass the producer's __filename");
  const { key, paths, exclude } = scopeOf(producer);
  const status = git(["status", "--porcelain", "--", ...pathspecs(paths, exclude)]);
  const whole = git(["status", "--porcelain"]);
  return {
    commit: git(["rev-parse", "--short", "HEAD"]),
    dirty: status === null ? null : status.length > 0,
    dirtyAnyFile: whole === null ? null : whole.length > 0,
    scope: key,
    scopeFiles: paths.length,
    scopeSha: require("crypto").createHash("sha256").update(paths.join("\n")).digest("hex").slice(0, 12),
    node: process.version,
    hardhat: (() => { try { return require("hardhat/package.json").version; } catch (e) { return null; } })(),
  };
}

module.exports = { runStamp, scopeOf };
