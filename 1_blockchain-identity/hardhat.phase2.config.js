// Hardhat configuration for Phase 2 prototypes (docs/phase2/; ADR-0001 proposed: a plug-in layer outside the
// Phase 1 sources). It lives here only to use this project's node_modules; its sources, tests, cache and
// artifacts are under ../phase2/, so the Phase 1 contracts, their scopes (tools/run_identity/scopes.json) and
// their results of record are untouched.
//   npx hardhat compile && npx hardhat --config hardhat.phase2.config.js test
require("@nomicfoundation/hardhat-toolbox");
const path = require("path");

module.exports = {
  solidity: {
    version: "0.8.24",
    settings: { optimizer: { enabled: true, runs: 200 }, viaIR: true, evmVersion: "cancun" },
  },
  // Hardhat only compiles sources under its root, so the root is the repository; the Phase 2 paths are under it.
  paths: {
    root: path.resolve(__dirname, ".."),
    sources: "phase2/idtx/contracts",
    tests: "phase2/idtx/test",
    cache: "phase2/idtx/cache",
    artifacts: "phase2/idtx/artifacts",
  },
};
