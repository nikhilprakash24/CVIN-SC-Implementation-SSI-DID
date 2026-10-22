// Hardhat configuration for layer 5 (zero-knowledge proofs and the agent-wrapped identity; docs/zkp/).
// Like hardhat.phase2.config.js it lives here only to use this project's node_modules; sources, tests, cache and
// artifacts are under ../5_zkp-agent-identity/, so Phase 1 sources, scopes and results of record are untouched.
//   npx hardhat compile && npx hardhat --config hardhat.zkp.config.js test
require("@nomicfoundation/hardhat-toolbox");
const path = require("path");

module.exports = {
  solidity: {
    version: "0.8.24",
    settings: { optimizer: { enabled: true, runs: 200 }, viaIR: true, evmVersion: "cancun" },
  },
  paths: {
    root: path.resolve(__dirname, ".."),
    sources: "5_zkp-agent-identity/contracts",
    tests: "5_zkp-agent-identity/test-contracts",
    cache: "5_zkp-agent-identity/cache",
    artifacts: "5_zkp-agent-identity/hh-artifacts",
  },
};
