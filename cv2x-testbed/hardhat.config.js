require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    hardhat: {
      chainId: 1337,
      mining: {
        auto: true,
        interval: 1000  // 1 second block time
      }
    },
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 1337
    },
    ganache: {
      url: "http://127.0.0.1:7545",
      chainId: 1337
    }
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    // Overridable so scripts/check_artifacts_fresh.js can compile into a
    // scratch dir and compare against the tracked artifacts (REVIEW_02 Q-9).
    cache: process.env.CV2X_CACHE_DIR || "./cache",
    artifacts: process.env.CV2X_ARTIFACTS_DIR || "./artifacts"
  }
};
