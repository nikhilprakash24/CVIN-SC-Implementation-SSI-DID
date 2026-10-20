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
 *                  The revert must also ORIGINATE in the named target
 *                  contract (`expected.target`, required): an identical
 *                  revert bubbled up from another contract is
 *                  "UNEXPECTED-REVERT" (review 02 Pass 3 Low; see
 *                  revertOriginOf for the method and its limits).
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

// ---------------------------------------------------------------------------
// Revert origin (review 02 Pass 3 Low): which contract's code produced the
// revert. matchesExpected() alone compares the revert DATA, so a defense in
// contract A "proved" a revert that actually came from contract B and was
// bubbled up unchanged (A.call(B) + `revert(add(ret,32), mload(ret))`, or a
// high-level call that re-raises) whenever both carry the same reason.
//
// Method: attempt() records the transaction the thunk sent (the last
// eth_estimateGas / eth_sendTransaction / eth_call request: ethers estimates
// before sending, and an attack reverts there, before mining), then
// re-executes exactly that request with `debug_traceCall` against the
// "pending" block (the context eth_estimateGas used) and walks the opcode
// trace (originFromStructLogs):
//   * every CALL / CALLCODE / DELEGATECALL / STATICCALL whose next step is one
//     level deeper opens a frame whose CODE address is the call's address
//     argument (for DELEGATECALL: the library/implementation whose code runs);
//     CREATE/CREATE2 frames are "create";
//   * a REVERT in a frame originates in that frame's code UNLESS the frame's
//     most recent child call reverted with byte-identical data, in which case
//     the frame is forwarding it and the origin is the child's origin
//     (recursively). A child that halted exceptionally (INVALID, out of gas)
//     counts as reverting with empty data in the child's code;
//   * the top frame's revert origin is compared with the target address.
// The replay must reproduce the observed revert data byte for byte; if it
// does not (or no request was captured, or tracing fails) the origin is
// "unverifiable" and the attack is UNEXPECTED-REVERT, never DEFENDED.
//
// Limits: (1) a frame that catches a child's revert and then reverts with
// byte-identical data of its own making is attributed to the child (the data
// cannot tell the two apart); this can make a target check fail, not pass
// wrongly, when the target is the outer frame. (2) The replay runs on the
// pending-block state at the time of the call; a thunk that sends several
// requests is replayed only for its LAST one. (3) A mined-and-reverted
// transaction (explicit gasLimit) is replayed on the post-block state, which
// differs only in the sender nonce; the byte-identical check guards against a
// divergence. (4) The origin is a CODE address: a target behind a proxy must
// be named by its implementation address. No contract in this suite uses one.
// ---------------------------------------------------------------------------

const TX_METHODS = new Set(["eth_estimateGas", "eth_sendTransaction", "eth_call"]);
const CALL_OPS = new Set(["CALL", "CALLCODE", "DELEGATECALL", "STATICCALL"]);
const CREATE_OPS = new Set(["CREATE", "CREATE2"]);
const END_OPS = new Set(["RETURN", "STOP", "SELFDESTRUCT", "REVERT"]);

function hreProvider() {
  // Lazily: decodeRevert() & co. are usable without a Hardhat runtime.
  return require("hardhat").network.provider;
}

/** Run `fn` while recording the last transaction-like request it sends. */
async function captureLastTx(fn) {
  const provider = hreProvider();
  const box = { tx: null };
  const origSend = provider.send;
  const origRequest = provider.request;
  const note = (method, params) => {
    if (TX_METHODS.has(method) && Array.isArray(params) && params[0] && typeof params[0] === "object") {
      box.tx = { ...params[0] };
    }
  };
  provider.send = function (method, params) {
    note(method, params);
    return origSend.call(this, method, params);
  };
  provider.request = function (args) {
    if (args) note(args.method, args.params);
    return origRequest.call(this, args);
  };
  try {
    return await fn();
  } catch (err) {
    if (err && typeof err === "object") err.__capturedTx = box.tx;
    throw err;
  } finally {
    provider.send = origSend;
    provider.request = origRequest;
  }
}

function wordToAddress(word) {
  return ethers.getAddress("0x" + word.slice(-40));
}

function memorySlice(memory, offsetHex, sizeHex) {
  const offset = Number(BigInt("0x" + offsetHex.replace(/^0x/, "")));
  const size = Number(BigInt("0x" + sizeHex.replace(/^0x/, "")));
  if (size === 0) return "0x";
  const hex = (memory || []).map((w) => w.replace(/^0x/, "")).join("");
  // memory is listed up to the words touched; anything past it reads as zero
  return "0x" + hex.slice(offset * 2, (offset + size) * 2).padEnd(size * 2, "0");
}

/**
 * Pure: the code address whose REVERT produced the top-level revert, from a
 * debug_trace structLogs array (with memory), or null if the top frame did
 * not revert. `to` is the transaction's target.
 */
function originFromStructLogs(structLogs, to) {
  const frames = [{ code: ethers.getAddress(to), lastChild: null, result: null }];
  for (let i = 0; i < structLogs.length; i++) {
    const log = structLogs[i];
    const next = structLogs[i + 1];
    const frame = frames[frames.length - 1];
    if (log.op === "REVERT") {
      const st = log.stack;
      const data = memorySlice(log.memory, st[st.length - 1], st[st.length - 2]);
      const origin =
        frame.lastChild && frame.lastChild.data === data ? frame.lastChild.origin : frame.code;
      frame.result = { data, origin };
    }
    if (CALL_OPS.has(log.op) || CREATE_OPS.has(log.op)) {
      if (next && next.depth === log.depth + 1) {
        const code = CALL_OPS.has(log.op) ? wordToAddress(log.stack[log.stack.length - 2]) : "create";
        frames.push({ code, lastChild: null, result: null });
      } else {
        frame.lastChild = null; // no code ran (EOA / precompile): nothing to forward
      }
      continue;
    }
    // Frame(s) ending: the next step is shallower than this one.
    let depth = log.depth;
    const nextDepth = next ? next.depth : 0;
    while (depth > nextDepth && frames.length > 0) {
      const ended = frames.pop();
      let res = ended.result;
      if (!res && !(depth === log.depth && END_OPS.has(log.op))) {
        res = { data: "0x", origin: ended.code }; // exceptional halt
      }
      if (frames.length === 0) return res ? res.origin : null;
      frames[frames.length - 1].lastChild = res; // null: the child succeeded
      depth -= 1;
    }
  }
  const top = frames[0];
  return top && top.result ? top.result.origin : null;
}

/** Re-execute `tx` with debug_traceCall: {origin, data} of its revert, or {error}. */
async function revertOriginOf(tx) {
  if (!tx || !tx.to) return { error: "no transaction captured" };
  const call = {};
  for (const k of ["from", "to", "data", "value", "gas", "gasPrice"]) {
    if (tx[k] !== undefined && tx[k] !== null) call[k] = tx[k];
  }
  if (call.data === undefined && tx.input !== undefined) call.data = tx.input;
  let trace;
  try {
    trace = await hreProvider().request({
      method: "debug_traceCall",
      params: [call, "pending", { enableMemory: true, disableStorage: true }],
    });
  } catch (e) {
    return { error: `debug_traceCall failed: ${reasonOf(e)}` };
  }
  if (!trace || !trace.failed) return { error: "replay did not revert" };
  const rv = trace.returnValue || "";
  const data = rv.startsWith("0x") ? rv : "0x" + rv;
  return { origin: originFromStructLogs(trace.structLogs || [], call.to), data };
}

async function addressOf(target) {
  if (typeof target === "string") return ethers.getAddress(target);
  if (target && typeof target.getAddress === "function") return ethers.getAddress(await target.getAddress());
  throw new Error("attempt(): expected.target must be a contract or an address");
}

/**
 * Execute a malicious transaction and classify the outcome against the revert
 * the defense is expected to produce.
 *
 * @param {() => Promise<any>} txThunk a thunk returning a tx-sending promise
 * @param {{reason?: string, customError?: string, args?: any[], panic?: number|bigint,
 *          iface?: import("ethers").Interface, target: any}} expected
 *        the revert that proves the NAMED defense fired: an Error(string)
 *        reason, a custom error name (decoded with `iface`, optionally with
 *        exact args), or a panic code; and `target` (required), the contract
 *        (or address) whose code must have produced that revert.
 * @returns {Promise<{outcome: string, revertReason: string|null, expectedRevert: string,
 *                    revertOrigin: string|null}>}
 *   outcome:
 *     "DEFENDED"          the tx reverted with exactly the expected reason/error,
 *                         and the revert originated in `target`'s code;
 *     "VULNERABLE"        the tx was mined;
 *     "UNEXPECTED-REVERT" it reverted, but for another reason, or with the
 *                         expected reason bubbled up from another contract,
 *                         or from an origin that could not be verified (the
 *                         named defense was not shown to be what stopped it);
 *     "FAILED-TO-RUN"     the attack never reached the EVM as a revert
 *                         (TypeError, ethers ABI/argument error, provider error).
 */
async function attempt(txThunk, expected) {
  const expectedRevert = describeExpected(expected);
  if (!expectedRevert) {
    throw new Error("attempt(): every attack must name its expected revert");
  }
  if (!expected.target) {
    throw new Error("attempt(): every attack must name the target contract of its expected revert");
  }
  const targetAddress = await addressOf(expected.target);
  try {
    await captureLastTx(async () => {
      const tx = await txThunk();
      if (tx && typeof tx.wait === "function") {
        await tx.wait();
      }
    });
    return { outcome: "VULNERABLE", revertReason: null, expectedRevert, revertOrigin: null };
  } catch (err) {
    const data = revertDataOf(err);
    if (data === null) {
      return {
        outcome: "FAILED-TO-RUN",
        revertReason: `${(err && err.constructor && err.constructor.name) || "Error"}: ${reasonOf(err)}`,
        expectedRevert,
        revertOrigin: null,
      };
    }
    const decoded = decodeRevert(data, expected.iface ? [expected.iface] : []);
    if (!matchesExpected(decoded, expected)) {
      return { outcome: "UNEXPECTED-REVERT", revertReason: decoded.text, expectedRevert, revertOrigin: null };
    }
    const traced = await revertOriginOf(err.__capturedTx);
    let revertOrigin;
    if (traced.error) {
      revertOrigin = `unverifiable (${traced.error})`;
    } else if (traced.data.toLowerCase() !== data.toLowerCase()) {
      revertOrigin = "unverifiable (replay produced different revert data)";
    } else {
      revertOrigin = traced.origin;
    }
    return {
      outcome: revertOrigin === targetAddress ? "DEFENDED" : "UNEXPECTED-REVERT",
      revertReason: decoded.text,
      expectedRevert,
      revertOrigin,
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
  originFromStructLogs,
  writeMatrix,
};
