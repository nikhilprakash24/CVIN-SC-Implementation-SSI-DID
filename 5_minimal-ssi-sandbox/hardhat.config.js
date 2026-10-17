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

module.exports = {
  solidity: { version: "0.8.24", settings: { optimizer: { enabled: true, runs: 200 } } },
};
