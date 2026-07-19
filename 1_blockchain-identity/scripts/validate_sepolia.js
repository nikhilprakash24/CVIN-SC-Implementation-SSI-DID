/**
 * validate_sepolia.js
 *
 * PUBLIC-TESTNET VALIDATION HARNESS ("witness", not a benchmark).
 *
 * Purpose: confirm that the Hardhat-local gas measurements in
 *   4_comparison-framework/results/gas_benchmark.json
 * REPRODUCE on a real Ethereum network (Sepolia), recording real transaction
 * hashes that anyone can independently verify on a public block explorer.
 *
 * Gas is deterministic across EVM networks for identical bytecode + calldata,
 * so a matching gasUsed on-chain is evidence the local numbers are real. This
 * validates the MEASUREMENTS, it is NOT a performance/latency sample.
 *
 * NETWORK-AGNOSTIC: the same script runs on
 *   - the in-process Hardhat network (default)  -> dry-run self-test, deltas ~0
 *   - a running localhost node                   -> dry-run self-test
 *   - Sepolia (chainId 11155111)                 -> real validation with tx hashes
 *
 * Run:
 *   npx hardhat run scripts/validate_sepolia.js                       # hardhat (dry-run)
 *   npx hardhat run scripts/validate_sepolia.js --network localhost   # localhost node
 *   npx hardhat run scripts/validate_sepolia.js --network sepolia     # real validation
 *
 * By default it validates a thesis-critical SUBSET of 3 standards:
 *   ERC-1056     (cheapest event-based registry)
 *   ERC-725xy    (full ERC-725 X+Y smart account)
 *   CVIN-Combined (the ERC-1056 + ERC-735 hybrid)
 * Extend by editing DEFAULT_STANDARDS below or setting
 *   VALIDATE_STANDARDS="ERC-1056,CVIN-Combined" (comma-separated names from STANDARDS).
 *
 * Output: 4_comparison-framework/results/sepolia_validation.json
 */

const fs = require("fs");
const path = require("path");
const hre = require("hardhat");
const { ethers } = hre;

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

// Thesis-critical default subset. Add any key of STANDARDS (defined below) to
// validate more standards, or override at runtime with VALIDATE_STANDARDS.
const DEFAULT_STANDARDS = ["ERC-1056", "ERC-725xy", "CVIN-Combined"];

// Minimum signer balance required on a public network (ETH).
const MIN_BALANCE_ETH = 0.05;

// Confirmations to wait per transaction. 1 is enough for validation on Sepolia.
const CONFIRMATIONS = 1;

// A |delta| at or below this is treated as calldata-only noise, not an
// execution-gas discrepancy. Intrinsic calldata cost is 4 gas per zero byte vs
// 16 per non-zero byte, so a differing 20-byte target address or 65-byte
// signature moves gasUsed by at most a few dozen gas. A real execution-path
// mismatch would be hundreds to thousands of gas, far above this.
const CALLDATA_TOLERANCE = 100;

// Chain ids / names treated as local dry-run networks (no env/balance gate).
const LOCAL_CHAIN_IDS = new Set([31337n, 1337n]);
const LOCAL_NETWORK_NAMES = new Set(["hardhat", "localhost"]);

// Block-explorer base URLs keyed by chainId (for building tx links).
const EXPLORERS = {
  11155111: "https://sepolia.etherscan.io/tx/",
  1: "https://etherscan.io/tx/",
  5: "https://goerli.etherscan.io/tx/",
  137: "https://polygonscan.com/tx/",
  80001: "https://mumbai.polygonscan.com/tx/",
};

// Deterministic FALLBACK addresses used only for pure "target" roles (a
// delegate/newOwner that never has to sign) when the network exposes just one
// funded signer (e.g. Sepolia). On the Hardhat network all roles map to the
// real default signers so calldata - and therefore gasUsed - matches the
// committed baseline exactly (delta 0).
const FALLBACK_ADDRS = [
  "0x1111111111111111111111111111111111111111",
  "0x2222222222222222222222222222222222222222",
  "0x3333333333333333333333333333333333333333",
  "0x4444444444444444444444444444444444444444",
];

// ---------------------------------------------------------------------------
// Baseline
// ---------------------------------------------------------------------------

const BASELINE_PATH = path.resolve(
  __dirname,
  "../../4_comparison-framework/results/gas_benchmark.json"
);
const OUTPUT_PATH = path.resolve(
  __dirname,
  "../../4_comparison-framework/results/sepolia_validation.json"
);

function loadBaseline() {
  try {
    return JSON.parse(fs.readFileSync(BASELINE_PATH, "utf8"));
  } catch (e) {
    console.warn(
      `WARN: could not read local baseline at ${BASELINE_PATH} (${e.message}). ` +
        "Deltas will be recorded as null."
    );
    return {};
  }
}

/** gasUsed baseline for (standard, operation), or null if absent. */
function baselineGas(baseline, standard, operation) {
  const s = baseline[standard];
  if (!s || !s[operation] || s[operation].gasUsed == null) return null;
  return Number(s[operation].gasUsed);
}

// ---------------------------------------------------------------------------
// Execution context
// ---------------------------------------------------------------------------

/**
 * Build the runtime context shared by every standard runner.
 * `signerAt(i)` returns a real signer for signing roles (falls back to the
 * primary funded signer when only one account exists). `addrAt(i)` returns an
 * address for pure target roles (falls back to a fixed FALLBACK address).
 */
function makeContext({ signers, explorerBase, baseline, results }) {
  const primary = signers[0];
  return {
    explorerBase,
    baseline,
    results,
    signerAt(i) {
      return signers[i] || primary;
    },
    addrAt(i) {
      return signers[i] ? signers[i].address : FALLBACK_ADDRS[i] || FALLBACK_ADDRS[0];
    },
  };
}

/**
 * Record one operation. `send` is a zero-arg function returning a tx (or a
 * deployment transaction) exposing `.hash` and `.wait()`. Any error is caught
 * and recorded in the cell so a single failure never aborts the run.
 * Returns the receipt on success, or null on failure.
 */
async function record(ctx, standard, operation, send) {
  const localBaseline = baselineGas(ctx.baseline, standard, operation);
  const cell = {
    standard,
    operation,
    txHash: null,
    gasUsed: null,
    localBaseline,
    delta: null,
    blockNumber: null,
    status: null,
    explorerUrl: null,
    error: null,
  };
  try {
    const tx = await send();
    const receipt = await tx.wait(CONFIRMATIONS);
    cell.txHash = tx.hash;
    cell.gasUsed = Number(receipt.gasUsed);
    cell.blockNumber = receipt.blockNumber;
    cell.status = Number(receipt.status);
    cell.delta = localBaseline == null ? null : cell.gasUsed - localBaseline;
    cell.explorerUrl = ctx.explorerBase ? ctx.explorerBase + tx.hash : null;
    const deltaStr =
      cell.delta == null ? "(no baseline)" : `delta ${cell.delta >= 0 ? "+" : ""}${cell.delta}`;
    console.log(
      `  ok  ${standard}/${operation}  gas=${cell.gasUsed}  ${deltaStr}  tx=${tx.hash}`
    );
  } catch (e) {
    cell.error = e.shortMessage || e.message || String(e);
    console.log(`  FAIL ${standard}/${operation}  ${cell.error}`);
  }
  ctx.results.push(cell);
  return cell;
}

/** Deploy a contract; returns { contract, deployTx } (deployTx has .hash/.wait). */
async function deploy(factory, ...args) {
  const contract = await factory.deploy(...args);
  const deployTx = contract.deploymentTransaction();
  await contract.waitForDeployment();
  return { contract, deployTx };
}

// ---------------------------------------------------------------------------
// Standard runners (mirror scripts/benchmark_gas.js operation-for-operation)
// ---------------------------------------------------------------------------

// ERC-1056 (EthereumDIDRegistry): shared event-based DID registry.
async function validateERC1056(ctx) {
  const std = "ERC-1056";
  const deployer = ctx.signerAt(0);
  const identityOwner = ctx.signerAt(1);
  const delegateAddr = ctx.addrAt(2);
  const newOwnerAddr = ctx.addrAt(3);

  const Factory = await ethers.getContractFactory(
    "contracts/ERC1056/EthereumDIDRegistry.sol:EthereumDIDRegistry",
    deployer
  );

  let registry;
  const dep = await record(ctx, std, "deployRegistry", async () => {
    const r = await deploy(Factory);
    registry = r.contract;
    return r.deployTx;
  });
  if (!registry) return; // deploy failed; nothing else to run

  const identity = identityOwner.address; // every address is a DID
  const attrName = ethers.encodeBytes32String("did/pub/Secp256k1/veriKey");
  const attrValue = ethers.toUtf8Bytes(
    "0x02b97c30de767f084ce3080168ee293053ba33b235d7116a3263d29f1450936b71"
  );
  const oneYear = 365 * 24 * 60 * 60;
  const reg = registry.connect(identityOwner);

  await record(ctx, std, "createIdentity", () =>
    reg.setAttribute(identity, attrName, attrValue, oneYear)
  );

  const newValue = ethers.toUtf8Bytes(
    "0x03c1d5e8f2a9b4c7d0e3f6a9b2c5d8e1f4a7b0c3d6e9f2a5b8c1d4e7f0a3b6c9d2"
  );
  await record(ctx, std, "updateAttribute", () =>
    reg.setAttribute(identity, attrName, newValue, oneYear)
  );

  const delegateType = ethers.encodeBytes32String("veriKey");
  await record(ctx, std, "addDelegateOrClaim", () =>
    reg.addDelegate(identity, delegateType, delegateAddr, oneYear)
  );

  await record(ctx, std, "revoke", () =>
    reg.revokeAttribute(identity, attrName, newValue)
  );

  // transferOwnership LAST: changeOwner hands control to newOwnerAddr (which we
  // may not control on a public net), so no further owner-only ops after it.
  await record(ctx, std, "transferOwnership", () =>
    reg.changeOwner(identity, newOwnerAddr)
  );
}

// ERC-725xy (CVINVehicleERC725XY): full ERC-725 X+Y smart account.
async function validateERC725XY(ctx) {
  const std = "ERC-725xy";
  const identityOwner = ctx.signerAt(1);
  const newOwnerAddr = ctx.addrAt(3);

  const Factory = await ethers.getContractFactory("CVINVehicleERC725XY", identityOwner);

  // createIdentity IS the per-vehicle account deployment for ERC-725.
  let account;
  await record(ctx, std, "createIdentity", async () => {
    const r = await deploy(Factory, identityOwner.address);
    account = r.contract;
    return r.deployTx;
  });
  if (!account) return;

  const vinKey = await account.VIN_KEY();
  const vinValue = ethers.toUtf8Bytes("1HGCM82633A004352"); // 17 bytes
  await record(ctx, std, "updateAttribute", () => account.setData(vinKey, vinValue));

  await record(ctx, std, "transferOwnership", () =>
    account.transferOwnership(newOwnerAddr)
  );
}

// CVIN-Combined (CVINCombinedIdentity): ERC-1056 + ERC-735 hybrid registry.
async function validateCVINCombined(ctx) {
  const std = "CVIN-Combined";
  const deployer = ctx.signerAt(0);
  const identityOwner = ctx.signerAt(1);
  const delegateAddr = ctx.addrAt(2);
  const newOwnerAddr = ctx.addrAt(3);

  const CLAIM_TOPIC_VIN = 1;
  const SCHEME_ECDSA = 1;
  const ATTR_NAME = ethers.keccak256(ethers.toUtf8Bytes("did/pub/Secp256k1/veriKey"));

  const Factory = await ethers.getContractFactory("CVINCombinedIdentity", deployer);

  let registry;
  await record(ctx, std, "deployRegistry", async () => {
    const r = await deploy(Factory);
    registry = r.contract;
    return r.deployTx;
  });
  if (!registry) return;

  const identity = identityOwner.address;
  const reg = registry.connect(identityOwner);
  const oneDay = 86400;

  await record(ctx, std, "createIdentity", () =>
    reg.setAttribute(
      identity,
      ATTR_NAME,
      ethers.toUtf8Bytes(
        "0x02b97c30de767f084ce3080168ee293053ba33b235d7116a3263d29f1450936b71"
      ),
      oneDay
    )
  );

  await record(ctx, std, "updateAttribute", () =>
    reg.setAttribute(
      identity,
      ATTR_NAME,
      ethers.toUtf8Bytes(
        "0x03c1d5e8f2a9b4c7d0e3f6a9b2c5d8e1f4a7b0c3d6e9f2a5b8c1d4e7f0a3b6c9d2"
      ),
      oneDay
    )
  );

  // Fixed issuer wallet (NOT a node default account) so the ecrecover-verified
  // signature - and thus calldata/gas - is deterministic across runs/networks.
  const issuerWallet = new ethers.Wallet(
    "0x1f2e3d4c5b6a79881726354453627181920a1b2c3d4e5f60718293a4b5c6d7e8"
  );
  const vinData = ethers.toUtf8Bytes("1HGCM82633A004352");
  const digest = ethers.solidityPackedKeccak256(
    ["address", "address", "uint256", "bytes"],
    [await registry.getAddress(), identity, CLAIM_TOPIC_VIN, vinData]
  );
  const signature = ethers.Signature.from(issuerWallet.signingKey.sign(digest)).serialized;

  await record(ctx, std, "addDelegateOrClaim", () =>
    reg.addClaim(
      identity,
      CLAIM_TOPIC_VIN,
      SCHEME_ECDSA,
      issuerWallet.address,
      signature,
      vinData,
      "ipfs://QmVinAttestation"
    )
  );

  const claimId = ethers.solidityPackedKeccak256(
    ["address", "uint256"],
    [issuerWallet.address, CLAIM_TOPIC_VIN]
  );
  await record(ctx, std, "revoke", () => reg.removeClaim(identity, claimId));

  await record(ctx, std, "transferOwnership", () =>
    reg.changeOwner(identity, newOwnerAddr)
  );

  // Keep delegateAddr referenced (addDelegate is measured in the pure benchmark;
  // here the claim path is the representative addDelegateOrClaim operation).
  void delegateAddr;
}

// Registry of validatable standards. Extend this map to cover more standards.
const STANDARDS = {
  "ERC-1056": validateERC1056,
  "ERC-725xy": validateERC725XY,
  "CVIN-Combined": validateCVINCombined,
};

// ---------------------------------------------------------------------------
// Preflight
// ---------------------------------------------------------------------------

/**
 * Decide if this is a local dry-run network using ONLY static config (never the
 * live provider), so we can gate on env vars before any RPC/provider access.
 */
function isLocalNetwork(networkName, configChainId) {
  if (LOCAL_NETWORK_NAMES.has(networkName)) return true;
  if (configChainId != null && LOCAL_CHAIN_IDS.has(BigInt(configChainId))) return true;
  return false;
}

/**
 * Returns { ok, signers } on success. On a failed public-network gate it prints
 * clear, actionable guidance and returns { ok:false } (caller exits non-zero
 * WITHOUT throwing a stack trace).
 *
 * IMPORTANT: for public networks the env-var check happens BEFORE any provider
 * access, because Hardhat throws HH117 the moment the provider is used with an
 * empty RPC URL (which is exactly the misconfiguration we want to catch cleanly).
 */
async function preflight(networkName, local) {
  if (!local) {
    // Public network: require RPC + key BEFORE touching the provider.
    const missing = [];
    if (!process.env.SEPOLIA_RPC_URL) missing.push("SEPOLIA_RPC_URL");
    if (!process.env.PRIVATE_KEY) missing.push("PRIVATE_KEY");
    if (missing.length > 0) {
      printPublicGuidance(networkName, missing, "missing-config");
      return { ok: false };
    }
  }

  // Provider is now safe to use.
  const signers = await ethers.getSigners();

  if (local) {
    if (signers.length === 0) {
      console.error("No signers available on the local network. Cannot continue.");
      return { ok: false };
    }
    console.log(`Local dry-run: ${signers.length} signer(s) available, env/balance gate skipped.`);
    return { ok: true, signers };
  }

  if (signers.length === 0) {
    printPublicGuidance(networkName, [], "missing-config");
    return { ok: false };
  }

  const signer = signers[0];
  let balanceWei;
  try {
    balanceWei = await ethers.provider.getBalance(signer.address);
  } catch (e) {
    console.error("");
    console.error(`Could not reach the RPC endpoint (SEPOLIA_RPC_URL): ${e.shortMessage || e.message}`);
    console.error("Check that SEPOLIA_RPC_URL is a valid, reachable HTTPS endpoint.");
    return { ok: false };
  }

  const balanceEth = Number(ethers.formatEther(balanceWei));
  console.log(`Signer: ${signer.address}`);
  console.log(`Balance: ${balanceEth} ETH (minimum required: ${MIN_BALANCE_ETH} ETH)`);

  if (balanceEth < MIN_BALANCE_ETH) {
    printPublicGuidance(networkName, [], "low-balance", signer.address, balanceEth);
    return { ok: false };
  }

  return { ok: true, signers };
}

function printPublicGuidance(networkName, missing, reason, address, balanceEth) {
  const line = "=".repeat(72);
  console.error("");
  console.error(line);
  console.error(`  Cannot run validation on public network "${networkName}".`);
  console.error(line);
  if (reason === "low-balance") {
    console.error(`  Signer ${address} has only ${balanceEth} ETH.`);
    console.error(`  It needs at least ${MIN_BALANCE_ETH} ETH to pay for validation gas.`);
    console.error("");
    console.error("  Fund this address from a free Sepolia faucet, e.g.:");
    console.error("    - https://sepoliafaucet.com  (Alchemy)");
    console.error("    - https://www.infura.io/faucet/sepolia");
    console.error("    - https://faucet.quicknode.com/ethereum/sepolia");
  } else {
    if (missing.length > 0) {
      console.error(`  Missing required environment variable(s): ${missing.join(", ")}`);
    } else {
      console.error("  No usable signer was derived (is PRIVATE_KEY set correctly?).");
    }
    console.error("");
    console.error("  To run real Sepolia validation you must set, in 1_blockchain-identity/.env:");
    console.error("");
    console.error("    SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/<YOUR_KEY>");
    console.error("        (free key from https://alchemy.com or https://infura.io)");
    console.error("    PRIVATE_KEY=<0x-prefixed private key of a TEST-ONLY account>");
    console.error("        (never a key that holds real funds)");
    console.error("");
    console.error("  Then fund that account's address from a free Sepolia faucet:");
    console.error("    - https://sepoliafaucet.com");
    console.error("    - https://www.infura.io/faucet/sepolia");
  }
  console.error("");
  console.error("  Then re-run:");
  console.error("    npx hardhat run scripts/validate_sepolia.js --network sepolia");
  console.error(line);
  console.error("");
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const networkName = hre.network.name;
  // Determine mode from STATIC config only (no provider access yet), so a
  // missing RPC URL is reported cleanly instead of triggering HH117.
  const configChainId = hre.network.config.chainId;
  const local = isLocalNetwork(networkName, configChainId);

  console.log("CVIN public-testnet validation harness (gas-measurement witness)");
  console.log(`Network: ${networkName}  mode: ${local ? "local dry-run" : "public validation"}`);
  console.log("");

  const pf = await preflight(networkName, local);
  if (!pf.ok) {
    process.exitCode = 1;
    return;
  }
  const signers = pf.signers;

  // Provider is reachable now; get the authoritative chainId from it.
  const net = await ethers.provider.getNetwork();
  const chainId = net.chainId; // bigint
  const explorerBase = EXPLORERS[Number(chainId)] || null;
  console.log(`Chain id (from RPC): ${chainId}`);

  const selected = (process.env.VALIDATE_STANDARDS
    ? process.env.VALIDATE_STANDARDS.split(",").map((s) => s.trim()).filter(Boolean)
    : DEFAULT_STANDARDS
  ).filter((name) => {
    if (STANDARDS[name]) return true;
    console.warn(`WARN: unknown standard "${name}" requested; skipping. Known: ${Object.keys(STANDARDS).join(", ")}`);
    return false;
  });

  const baseline = loadBaseline();
  const results = [];
  const ctx = makeContext({ signers, explorerBase, baseline, results });

  console.log(`Validating standards: ${selected.join(", ")}`);
  console.log(`Comparing against baseline: ${path.relative(process.cwd(), BASELINE_PATH)}`);
  console.log("");

  // Sequential per standard AND per operation. Every tx is awaited before the
  // next is sent, so the signer's nonce advances naturally (no manual nonce
  // bookkeeping needed) and one failing op cannot corrupt later ones.
  for (const name of selected) {
    console.log(`--- ${name} ---`);
    try {
      await STANDARDS[name](ctx);
    } catch (e) {
      // A runner-level (non per-op) failure: record it and continue.
      console.log(`  FAIL ${name} (runner): ${e.shortMessage || e.message}`);
      results.push({
        standard: name,
        operation: "(runner)",
        txHash: null,
        gasUsed: null,
        localBaseline: null,
        delta: null,
        blockNumber: null,
        status: null,
        explorerUrl: null,
        error: e.shortMessage || e.message || String(e),
      });
    }
    console.log("");
  }

  // Summary: did every SUCCESSFUL, baselined tx match the local baseline?
  const succeeded = results.filter((r) => r.error == null && r.gasUsed != null);
  const withBaseline = succeeded.filter((r) => r.localBaseline != null);
  const maxAbsDelta = withBaseline.reduce((m, r) => Math.max(m, Math.abs(r.delta)), 0);
  const exactMatches = withBaseline.filter((r) => r.delta === 0).length;
  // Headline boolean: measurements reproduce if every baselined op matches
  // within calldata-only tolerance (exact for on-chain execution gas).
  const gasMatches = withBaseline.length > 0 && maxAbsDelta <= CALLDATA_TOLERANCE;
  const anyFailure = results.some((r) => r.error != null);

  const output = {
    network: networkName,
    chainId: Number(chainId),
    timestamp: new Date().toISOString(),
    signer: signers[0] ? signers[0].address : null,
    mode: local ? "local-dry-run" : "public-validation",
    baselineFile: path.relative(path.resolve(__dirname, "../.."), BASELINE_PATH),
    results,
    summary: {
      total_txs: succeeded.length,
      failed_ops: results.length - succeeded.length,
      compared_against_baseline: withBaseline.length,
      gas_matches_local: gasMatches,
      exact_matches: exactMatches,
      max_abs_delta: maxAbsDelta,
      calldata_tolerance: CALLDATA_TOLERANCE,
    },
  };

  fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true });
  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(output, null, 2));

  console.log("=== Validation summary ===");
  console.log(`Successful txs:            ${output.summary.total_txs}`);
  console.log(`Failed operations:         ${output.summary.failed_ops}`);
  console.log(`Compared against baseline: ${output.summary.compared_against_baseline}`);
  console.log(`Exact-match ops (delta 0): ${output.summary.exact_matches}/${output.summary.compared_against_baseline}`);
  console.log(`Gas matches local (<=${CALLDATA_TOLERANCE} gas calldata tol.): ${output.summary.gas_matches_local}`);
  console.log(`Max |delta| vs baseline:   ${output.summary.max_abs_delta}`);
  console.log(`Results written to ${path.relative(process.cwd(), OUTPUT_PATH)}`);

  if (!local) {
    console.log("");
    console.log("Verify these transactions independently on the explorer:");
    for (const r of succeeded) {
      if (r.explorerUrl) console.log(`  ${r.standard}/${r.operation}: ${r.explorerUrl}`);
    }
  }

  // Non-zero exit if anything failed, so CI/users notice.
  if (anyFailure) process.exitCode = 1;
}

main().catch((error) => {
  // Unexpected error path only (preflight guidance already handles the common
  // misconfiguration cases cleanly). Keep it readable.
  console.error("Unexpected error:", error.shortMessage || error.message || error);
  process.exitCode = 1;
});
