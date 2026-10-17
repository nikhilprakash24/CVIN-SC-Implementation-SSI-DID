require("@nomicfoundation/hardhat-toolbox");
const path = require("path");
const { subtask } = require("hardhat/config");
const { TASK_COMPILE_SOLIDITY_GET_SOLC_BUILD } = require("hardhat/builtin-tasks/task-names");

// Offline/sandboxed compilation: use the npm-installed solc-js instead of
// downloading binaries from binaries.soliditylang.org (blocked in restricted nets).
subtask(TASK_COMPILE_SOLIDITY_GET_SOLC_BUILD, async (args, hre, runSuper) => {
  if (args.solcVersion === "0.8.24") {
    return {
      compilerPath: path.join(__dirname, "node_modules", "solc", "soljson.js"),
      isSolcJs: true,
      version: "0.8.24",
      longVersion: "solc-js 0.8.24 (local)",
    };
  }
  return runSuper(args);
});

const BASE = { version: "0.8.24", settings: { optimizer: { enabled: true, runs: 200 } } };
// Per-file deviation (FINDINGS F-O7-1): the ERC-8004 reputation interface (8-argument giveFeedback
// with four dynamic strings; 11-argument NewFeedback event) exceeds the legacy codegen stack, as the
// public reference implementations also find. Only the two ERC-8004 files use the IR pipeline;
// every other contract keeps the global envelope (no viaIR). O7 gas is measured under viaIR and
// is labelled so wherever it is reported.
const VIA_IR = { version: "0.8.24", settings: { optimizer: { enabled: true, runs: 200 }, viaIR: true } };

module.exports = {
  solidity: {
    compilers: [BASE],
    overrides: {
      "contracts/implementations/ERC8004Registries.sol": VIA_IR,
      "contracts/implementations/O7_ERC8004.sol": VIA_IR,
    },
  },
};
