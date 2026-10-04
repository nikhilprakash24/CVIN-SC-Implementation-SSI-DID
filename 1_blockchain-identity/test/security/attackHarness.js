/**
 * attackHarness.js
 *
 * Shared harness for the Thrust 5 security analysis of the CVIN vehicle-identity
 * standards. Mirrors the structure of scripts/benchmark_gas.js: instead of
 * recording the REAL gasUsed of a legitimate lifecycle operation, it EXECUTES a
 * concrete attack transaction against each standard's real contract on the
 * in-process Hardhat network and records the REAL observed outcome — never a
 * hard-coded verdict.
 *
 * Outcome model (one per (standard, attack) cell of the security matrix):
 *   "DEFENDED"   — the malicious transaction reverted WITH THE REVERT REASON /
 *                  CUSTOM ERROR OF THE NAMED DEFENSE (every attempt() states
 *                  it; REVIEW_02 Q-8). A revert for any other reason is
 *                  "UNEXPECTED-REVERT", and an error that is not an EVM revert
 *                  at all (TypeError, ABI/argument error) is "FAILED-TO-RUN";
 *                  neither counts as defended.
 *   "VULNERABLE" — the malicious transaction was mined successfully (the attack
 *                  achieved its effect; a real finding to surface).
 *   "N/A"        — the attack is not applicable to this standard's identity
 *                  model (e.g. no gated issuance to bypass on a self-sovereign
 *                  registry, or no signed/relayed operation to replay).
 *
 * Differential rigor: most scenarios also run a CONTROL — the SAME operation
 * performed by the legitimately authorized party — and assert it SUCCEEDS. A
 * cell is only trustworthy as "DEFENDED" when (a) the attacker's call reverts
 * AND (b) the authorized call of the very same operation succeeds, proving the
 * revert is due to authorization/verification and not an unrelated malformed
 * call. Where relevant we also assert the protected state was not mutated.
 *
 * The accumulated matrix is written to
 *   ../../../4_comparison-framework/security-analysis/results/attack_results.json
 * by the after() hook in securityScenarios.test.js.
 */

const fs = require("fs");
const path = require("path");
const { ethers } = require("ethers");

// Ordered attack set (parallels the gas benchmark's lifecycle operation set:
// createIdentity, updateAttribute, addDelegateOrClaim, revoke, transferOwnership,
// plus the cross-cutting cryptographic replay attack).
const ATTACKS = [
  "unauthorizedIssuance", // attacker mints/registers an identity without the required role
  "unauthorizedAttributeWrite", // attacker rewrites a victim identity's attributes/keys/metadata
  "unauthorizedDelegateOrClaim", // attacker adds a delegate / anchors a (possibly forged) claim
  "unauthorizedRevocation", // attacker revokes/burns/deactivates a victim's identity or credential
  "identityHijack", // attacker seizes ownership/control of a victim's identity
  "signatureReplay", // attacker replays a consumed signed/relayed operation
];

const ATTACK_LABELS = {
  unauthorizedIssuance: "Unauthorized issuance",
  unauthorizedAttributeWrite: "Unauthorized attribute write",
  unauthorizedDelegateOrClaim: "Unauthorized delegate/claim",
  unauthorizedRevocation: "Unauthorized revocation",
  identityHijack: "Identity hijack",
  signatureReplay: "Signature replay",
};

// Accumulator: RESULTS[standard][attack] = { outcome, threat, attack, defense, revertReason, control }
const RESULTS = {};

function record(standard, attack, data) {
  if (!ATTACKS.includes(attack)) {
    throw new Error(`Unknown attack key: ${attack}`);
  }
  RESULTS[standard] = RESULTS[standard] || {};
  RESULTS[standard][attack] = data;
}

/** Best-effort human-readable message from an ethers/hardhat error. */
function reasonOf(err) {
  if (!err) return null;
  return (
    err.shortMessage ||
    err.reason ||
    (err.info && err.info.error && err.info.error.message) ||
    (err.message ? String(err.message).split("\n")[0] : String(err))
  );
}

const ERROR_STRING_SELECTOR = "0x08c379a0"; // Error(string)
const PANIC_SELECTOR = "0x4e487b71"; // Panic(uint256)

function isHexData(x) {
  return typeof x === "string" && /^0x([0-9a-fA-F]{2})*$/.test(x);
}

/**
 * ABI revert data carried by an error, or null when the error is not an EVM
 * revert at all (TypeError, ethers argument/ABI errors, provider errors...).
 *
 * Hardhat's in-process network throws its own error class (SolidityError /
 * ProviderError) with the raw revert payload in `err.data`; ethers'
 * CALL_EXCEPTION carries it in `err.data` too, sometimes nested under
 * `err.info.error.data` / `err.error.data`. Hardhat's human-readable message is
 * NOT relied on: for contracts compiled with solc 0.8.20 + viaIR (the ERC-725
 * baseline) its stack-trace engine cannot map the bytecode and the message
 * reads "Transaction reverted and Hardhat couldn't infer the reason", although
 * `err.data` still holds the ABI-encoded Error(string).
 */
function revertDataOf(err) {
  if (!err || typeof err !== "object") return null;
  const candidates = [
    err.data,
    err.info && err.info.error && err.info.error.data,
    err.error && err.error.data,
    err.data && err.data.data,
  ];
  for (const c of candidates) {
    if (isHexData(c)) return c;
  }
  // An ethers CALL_EXCEPTION with no payload (e.g. bare `revert()`).
  if (err.code === "CALL_EXCEPTION") return "0x";
  return null;
}

/**
 * Decode raw revert data into {kind, name, args, text}.
 *   kind: "reason" (Error(string)) | "panic" | "customError" | "empty" | "unknown"
 * `ifaces` are ethers Interfaces used to decode custom errors.
 */
function decodeRevert(data, ifaces = []) {
  const coder = ethers.AbiCoder.defaultAbiCoder();
  if (data === "0x") return { kind: "empty", name: null, args: [], text: "revert() with no data" };
  const sel = data.slice(0, 10).toLowerCase();
  if (sel === ERROR_STRING_SELECTOR) {
    const [msg] = coder.decode(["string"], "0x" + data.slice(10));
    return { kind: "reason", name: "Error", args: [msg], text: `Error(${JSON.stringify(msg)})` };
  }
  if (sel === PANIC_SELECTOR) {
    const [code] = coder.decode(["uint256"], "0x" + data.slice(10));
    return { kind: "panic", name: "Panic", args: [code], text: `Panic(0x${code.toString(16)})` };
  }
  for (const iface of ifaces) {
    if (!iface) continue;
    let parsed = null;
    try {
      parsed = iface.parseError(data);
    } catch (_) {
      parsed = null;
    }
    if (parsed) {
      const args = Array.from(parsed.args);
      return {
        kind: "customError",
        name: parsed.name,
        args,
        text: `${parsed.name}(${args.map((a) => a.toString()).join(", ")})`,
      };
    }
  }
  return { kind: "unknown", name: null, args: [], text: `unrecognised revert data ${data}` };
}

/** Normalise an expectation to {reason} | {customError, args?} | {panic}. */
function describeExpected(expected) {
  if (!expected) return null;
  if (expected.reason !== undefined) return `Error(${JSON.stringify(expected.reason)})`;
  if (expected.panic !== undefined) return `Panic(0x${BigInt(expected.panic).toString(16)})`;
  if (expected.customError) {
    const args = expected.args ? expected.args.map((a) => a.toString()).join(", ") : "...";
    return `${expected.customError}(${args})`;
  }
  throw new Error("attempt(): expected must give reason, panic or customError");
}

function eqArg(a, b) {
  if (typeof a === "string" && typeof b === "string") return a.toLowerCase() === b.toLowerCase();
  try {
    return BigInt(a) === BigInt(b);
  } catch (_) {
    return String(a) === String(b);
  }
}

function matchesExpected(decoded, expected) {
  if (expected.reason !== undefined) {
    return decoded.kind === "reason" && decoded.args[0] === expected.reason;
  }
  if (expected.panic !== undefined) {
    return decoded.kind === "panic" && BigInt(decoded.args[0]) === BigInt(expected.panic);
  }
  if (decoded.kind !== "customError" || decoded.name !== expected.customError) return false;
  if (!expected.args) return true;
  return (
    expected.args.length === decoded.args.length &&
    expected.args.every((a, i) => eqArg(a, decoded.args[i]))
  );
}

/**
 * Execute a malicious transaction and classify the outcome against the revert
 * the defense is expected to produce.
 *
 * @param {() => Promise<any>} txThunk a thunk returning a tx-sending promise
 * @param {{reason?: string, customError?: string, args?: any[], panic?: number|bigint,
 *          iface?: import("ethers").Interface}} expected
 *        the revert that proves the NAMED defense fired: an Error(string)
 *        reason, a custom error name (decoded with `iface`, optionally with
 *        exact args), or a panic code.
 * @returns {Promise<{outcome: string, revertReason: string|null, expectedRevert: string}>}
 *   outcome:
 *     "DEFENDED"          the tx reverted with exactly the expected reason/error;
 *     "VULNERABLE"        the tx was mined;
 *     "UNEXPECTED-REVERT" it reverted, but for another reason (the named
 *                         defense was not what stopped it);
 *     "FAILED-TO-RUN"     the attack never reached the EVM as a revert
 *                         (TypeError, ethers ABI/argument error, provider error).
 */
async function attempt(txThunk, expected) {
  const expectedRevert = describeExpected(expected);
  if (!expectedRevert) {
    throw new Error("attempt(): every attack must name its expected revert");
  }
  try {
    const tx = await txThunk();
    if (tx && typeof tx.wait === "function") {
      await tx.wait();
    }
    return { outcome: "VULNERABLE", revertReason: null, expectedRevert };
  } catch (err) {
    const data = revertDataOf(err);
    if (data === null) {
      return {
        outcome: "FAILED-TO-RUN",
        revertReason: `${(err && err.constructor && err.constructor.name) || "Error"}: ${reasonOf(err)}`,
        expectedRevert,
      };
    }
    const decoded = decodeRevert(data, expected.iface ? [expected.iface] : []);
    return {
      outcome: matchesExpected(decoded, expected) ? "DEFENDED" : "UNEXPECTED-REVERT",
      revertReason: decoded.text,
      expectedRevert,
    };
  }
}

/**
 * Execute a legitimate control transaction (the authorized party performing the
 * same operation the attacker attempted) and classify it.
 * @returns {Promise<string>} "PASS" or "FAIL: <reason>"
 */
async function control(txThunk) {
  try {
    const tx = await txThunk();
    if (tx && typeof tx.wait === "function") {
      await tx.wait();
    }
    return "PASS";
  } catch (err) {
    const data = revertDataOf(err);
    return "FAIL: " + (data === null ? reasonOf(err) : decodeRevert(data).text);
  }
}

function naCell(standard, attack, threat, note) {
  record(standard, attack, {
    outcome: "N/A",
    threat,
    attack: note,
    defense: null,
    revertReason: null,
    expectedRevert: null,
    control: null,
  });
}

/** Serialize the accumulated matrix to the comparison-framework results dir. */
function writeMatrix(metadata) {
  const output = { ...RESULTS, metadata: { ...metadata, attacks: ATTACKS } };
  const outDir = path.resolve(
    __dirname,
    "../../../4_comparison-framework/security-analysis/results"
  );
  fs.mkdirSync(outDir, { recursive: true });
  const outFile = path.join(outDir, "attack_results.json");
  // Preserve the previously committed `date` so an unchanged security
  // outcome re-run produces a byte-identical file (no wall-clock churn
  // dirtying the tree on every `npx hardhat test`). The provenance of a
  // real regeneration lives in git history.
  try {
    const prior = JSON.parse(fs.readFileSync(outFile, "utf8"));
    if (prior && prior.metadata && prior.metadata.date) {
      output.metadata.date = prior.metadata.date;
    }
  } catch (_) {
    /* first run: keep the fresh date */
  }
  fs.writeFileSync(outFile, JSON.stringify(output, null, 2));
  return outFile;
}

module.exports = {
  ATTACKS,
  ATTACK_LABELS,
  RESULTS,
  record,
  attempt,
  control,
  naCell,
  reasonOf,
  revertDataOf,
  decodeRevert,
  writeMatrix,
};
