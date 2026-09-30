"use strict";
const fs = require("fs");
const path = require("path");
const { summarize, mode } = require("./stats");

const TX_BASE_GAS = 21000n;
const CREATE_BASE_GAS = 32000n;

function calldataGas(data) {
  const bytes = Buffer.from(data.replace(/^0x/, ""), "hex");
  let zeros = 0n, nonzeros = 0n;
  for (const b of bytes) if (b === 0) zeros++; else nonzeros++;
  return { bytes: bytes.length, gas: zeros * 4n + nonzeros * 16n };
}

function intrinsicGas(tx) {
  const { bytes, gas } = calldataGas(tx.data || "0x");
  let g = TX_BASE_GAS + gas;
  if (!tx.to) g += CREATE_BASE_GAS + 2n * BigInt(Math.ceil(bytes / 32)); // EIP-3860 initcode word cost
  return { calldataBytes: bytes, gasIntrinsic: g };
}

function logStats(receipt) {
  let logBytes = 0;
  for (const log of receipt.logs) {
    logBytes += 32 * log.topics.length + (log.data.length - 2) / 2;
  }
  return { logCount: receipt.logs.length, logBytes };
}

/**
 * Measures identity operations on a Hardhat network.
 * Every measured tx yields one row in raw.jsonl; every semantic op yields one
 * aggregated row (sum over its txs) tagged with adapter/scenario/op.
 */
class MetricsCollector {
  constructor({ hre, runDir, trace = true }) {
    this.hre = hre;
    this.provider = hre.ethers.provider;
    this.runDir = runDir;
    this.trace = trace;
    this.rawPath = path.join(runDir, "raw.jsonl");
    this._rawFd = fs.openSync(this.rawPath, "a");
    this._readCounter = null;
    this._installRpcCounter();
  }

  close() {
    fs.closeSync(this._rawFd);
  }

  // ---- RPC accounting for read-path measurement -------------------------
  _installRpcCounter() {
    // hardhat-ethers dispatches through provider.send(method, params); the
    // EIP-1193 request() path is patched too for completeness.
    const np = this.hre.network.provider;
    if (np.__metricsPatched) return;
    const self = this;
    const count = (method, res) => {
      if (!self._readCounter) return;
      self._readCounter.calls++;
      self._readCounter.methods[method] = (self._readCounter.methods[method] || 0) + 1;
      try { self._readCounter.bytes += JSON.stringify(res ?? null).length; } catch { /* ignore */ }
    };
    const origSend = np.send.bind(np);
    np.send = async function (method, params) { const res = await origSend(method, params); count(method, res); return res; };
    const origRequest = np.request.bind(np);
    np.request = async function (args) { const res = await origRequest(args); count(args.method, res); return res; };
    np.__metricsPatched = true;
  }

  // ---- Per-transaction analysis ------------------------------------------
  async analyzeTx(txResponse, receipt) {
    const { calldataBytes, gasIntrinsic } = intrinsicGas(txResponse);
    const { logCount, logBytes } = logStats(receipt);
    const row = {
      hash: receipt.hash,
      to: txResponse.to || null,
      isCreate: !txResponse.to,
      gasUsed: Number(receipt.gasUsed),
      gasIntrinsic: Number(gasIntrinsic),
      gasExecution: Number(receipt.gasUsed - gasIntrinsic),
      calldataBytes,
      logCount,
      logBytes,
      blockNumber: receipt.blockNumber,
    };
    if (this.trace) {
      try {
        const t = await this.hre.network.provider.send("debug_traceTransaction", [
          receipt.hash,
          { disableMemory: true, disableStack: true, disableStorage: true },
        ]);
        let sstore = 0, sload = 0, logs = 0, newSlots = 0, maxDepth = 1, calls = 0;
        for (const s of t.structLogs) {
          switch (s.op) {
            case "SSTORE": sstore++; if (s.gasCost >= 20000) newSlots++; break;
            case "SLOAD": sload++; break;
            case "LOG0": case "LOG1": case "LOG2": case "LOG3": case "LOG4": logs++; break;
            case "CALL": case "STATICCALL": case "DELEGATECALL": case "CALLCODE": case "CREATE": case "CREATE2": calls++; break;
          }
          if (s.depth > maxDepth) maxDepth = s.depth;
        }
        Object.assign(row, { evmSteps: t.structLogs.length, sstoreCount: sstore, sloadCount: sload, newSlotsEstimate: newSlots, internalCalls: calls, maxCallDepth: maxDepth });
      } catch (e) {
        row.traceError = String(e.message || e).slice(0, 120);
      }
    }
    return row;
  }

  /**
   * Execute a mutating semantic op. `fn` must return { txs: TransactionResponse[] }.
   * Returns the aggregated row (and records it). Latency covers send→receipt of all txs.
   */
  async measureTx(tags, fn) {
    const t0 = process.hrtime.bigint();
    const out = await fn();
    const txs = out.txs || [];
    const receipts = [];
    for (const tx of txs) receipts.push(await tx.wait());
    const t1 = process.hrtime.bigint();
    const latencyMs = Number(t1 - t0) / 1e6;

    const txRows = [];
    for (let i = 0; i < txs.length; i++) txRows.push(await this.analyzeTx(txs[i], receipts[i]));

    const agg = {
      ...tags,
      kind: "tx",
      txCount: txs.length,
      latencyMs,
      gasUsed: sum(txRows, "gasUsed"),
      gasIntrinsic: sum(txRows, "gasIntrinsic"),
      gasExecution: sum(txRows, "gasExecution"),
      calldataBytes: sum(txRows, "calldataBytes"),
      logCount: sum(txRows, "logCount"),
      logBytes: sum(txRows, "logBytes"),
      sstoreCount: sum(txRows, "sstoreCount"),
      sloadCount: sum(txRows, "sloadCount"),
      newSlotsEstimate: sum(txRows, "newSlotsEstimate"),
      evmSteps: sum(txRows, "evmSteps"),
      deploysContract: txRows.some((r) => r.isCreate),
      txs: txRows,
      result: out.result,
    };
    this._write(agg);
    return agg;
  }

  /** Execute a read-path op; counts JSON-RPC calls and returned bytes. */
  async measureRead(tags, fn) {
    this._readCounter = { calls: 0, bytes: 0, methods: {} };
    const t0 = process.hrtime.bigint();
    const result = await fn();
    const t1 = process.hrtime.bigint();
    const c = this._readCounter;
    this._readCounter = null;
    const row = {
      ...tags,
      kind: "read",
      latencyMs: Number(t1 - t0) / 1e6,
      readRpcCalls: c.calls,
      readBytes: c.bytes,
      readMethods: c.methods,
      resultSize: safeLen(result),
    };
    this._write(row);
    return { row, result };
  }

  /** Deployment accounting (gas + bytecode size). */
  async measureDeploy(tags, contract) {
    const tx = contract.deploymentTransaction();
    const receipt = await tx.wait();
    const code = await this.provider.getCode(await contract.getAddress());
    const row = {
      ...tags,
      kind: "deploy",
      gasUsed: Number(receipt.gasUsed),
      bytecodeBytes: (code.length - 2) / 2,
      initcodeBytes: (tx.data.length - 2) / 2,
    };
    this._write(row);
    return row;
  }

  /**
   * Repeat a measured tx op: 1 exact + warmup + N latency samples.
   * `iteration(i)` must return { fn } for a fresh precondition each time.
   */
  async repeatTx(tags, iteration, { n = 30, warmup = 5 } = {}) {
    const rows = [];
    const total = 1 + warmup + n;
    for (let i = 0; i < total; i++) {
      const { fn } = await iteration(i);
      const row = await this.measureTx({ ...tags, iteration: i }, fn);
      rows.push(row);
    }
    // Execution gas must be identical across iterations (EVM is deterministic);
    // total gas may differ by a few units through calldata zero-byte pricing
    // of freshly generated addresses, so gasUsed is reported as the mode.
    const gasMode = mode(rows.map((r) => r.gasUsed));
    const execMode = mode(rows.map((r) => r.gasExecution));
    const latencySamples = rows.slice(1 + warmup).map((r) => r.latencyMs);
    const first = rows[0];
    return {
      ...tags,
      kind: "tx",
      txCount: first.txCount,
      gasUsed: gasMode.value,
      gasUsedRange: [Math.min(...gasMode.distinct), Math.max(...gasMode.distinct)],
      gasDeterministic: execMode.distinct.length === 1,
      gasExecutionDistinct: execMode.distinct,
      gasIntrinsic: first.gasIntrinsic,
      gasExecution: execMode.value,
      calldataBytes: first.calldataBytes,
      logCount: first.logCount,
      logBytes: first.logBytes,
      sstoreCount: first.sstoreCount,
      sloadCount: first.sloadCount,
      newSlotsEstimate: first.newSlotsEstimate,
      stateFootprintBytes: (first.newSlotsEstimate || 0) * 32,
      evmSteps: first.evmSteps,
      deploysContract: first.deploysContract,
      latency: summarize(latencySamples),
      latencySamples,
    };
  }

  async repeatRead(tags, fn, { n = 30, warmup = 5 } = {}) {
    const rows = [];
    for (let i = 0; i < warmup + n; i++) {
      const { row } = await this.measureRead({ ...tags, iteration: i }, fn);
      rows.push(row);
    }
    const kept = rows.slice(warmup);
    return {
      ...tags,
      kind: "read",
      readRpcCalls: kept[0].readRpcCalls,
      readBytes: kept[0].readBytes,
      readMethods: kept[0].readMethods,
      resultSize: kept[0].resultSize,
      latency: summarize(kept.map((r) => r.latencyMs)),
      latencySamples: kept.map((r) => r.latencyMs),
    };
  }

  _write(row) {
    fs.writeSync(this._rawFd, JSON.stringify(row, bigintReplacer) + "\n");
  }
}

function sum(rows, k) {
  return rows.reduce((a, r) => a + (r[k] || 0), 0);
}
function safeLen(x) {
  try { return JSON.stringify(x, bigintReplacer).length; } catch { return null; }
}
function bigintReplacer(_, v) {
  return typeof v === "bigint" ? v.toString() : v;
}

module.exports = { MetricsCollector, bigintReplacer, intrinsicGas };
