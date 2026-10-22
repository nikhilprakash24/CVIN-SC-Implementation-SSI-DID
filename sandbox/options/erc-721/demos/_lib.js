'use strict';
/**
 * Shared helper for the per-option feature demos (plan S7). NOT a demo itself (underscore
 * prefix); running it under `hardhat run` prints nothing and exits 0.
 *
 * Every demo step prints exactly one JSON line to stdout:
 *   {"option","family","step","fn","onchain":true|false,"gasUsed":"<decimal>","note"}
 * and the run ends with {"option","family","summary":true,"steps":N,"ok":true|false}.
 * `onchain` is true only for a mined state-changing transaction (gasUsed is the receipt's
 * exact value); views, off-chain computations and expected reverts are `onchain:false, gasUsed:"0"`.
 * Any thrown error (failed assertion, unexpected revert, missing revert) sets a non-zero exit code.
 */
const assert = require('node:assert/strict');

function demo(option, family) {
  let steps = 0;
  const emit = (o) => console.log(JSON.stringify(o));
  const line = (step, fn, onchain, gasUsed, note) => {
    steps++;
    emit({ option, family, step, fn, onchain, gasUsed: String(gasUsed), note });
  };

  /** Send a transaction (promise of a ContractTransactionResponse); returns the receipt. */
  async function tx(step, fn, promise, note) {
    const receipt = await (await promise).wait();
    line(step, fn, true, receipt.gasUsed, note);
    return receipt;
  }

  /** A view/pure read; `check(value)` may assert on it. Returns the value. */
  async function view(step, fn, promise, note, check) {
    const value = await promise;
    if (check) check(value);
    line(step, fn, false, 0, note);
    return value;
  }

  /** Expect `thunk()` (a call or a tx) to revert with a message containing `match`. */
  async function reverts(step, fn, thunk, match, note) {
    let msg = null;
    try {
      const r = await thunk();
      if (r && typeof r.wait === 'function') await r.wait();
    } catch (e) {
      msg = [e.shortMessage, e.message, e.reason, e.data && e.data.message].filter(Boolean).join(' | ');
    }
    if (msg === null) throw new Error(`${step}: expected a revert containing "${match}" but the call succeeded`);
    if (match && !msg.includes(match)) throw new Error(`${step}: expected a revert containing "${match}", got: ${msg}`);
    line(step, fn, false, 0, `reverts "${match}" — ${note}`);
  }

  /** A purely off-chain step (signing, hashing, log replay already fetched, a documented observation). */
  function offchain(step, fn, note) { line(step, fn, false, 0, note); }

  function run(main) {
    main()
      .then(() => emit({ option, family, summary: true, steps, ok: true }))
      .catch((e) => {
        emit({ option, family, summary: true, steps, ok: false, error: e.message });
        console.error(e);
        process.exitCode = 1;
      });
  }

  return { tx, view, reverts, offchain, run, assert };
}

/** Args of the first `name` event in `receipt` emitted by `contract` (throws if absent). */
function eventArgs(contract, receipt, name) {
  for (const log of receipt.logs) {
    try {
      const p = contract.interface.parseLog(log);
      if (p && p.name === name) return p.args;
    } catch (_) { /* foreign log */ }
  }
  throw new Error(`event ${name} not found in receipt`);
}

/** Count of `name` events in `receipt`. */
function eventCount(contract, receipt, name) {
  let n = 0;
  for (const log of receipt.logs) {
    try { const p = contract.interface.parseLog(log); if (p && p.name === name) n++; } catch (_) { /* foreign */ }
  }
  return n;
}

/**
 * Deploy an "echo-selector" receiver: 20 bytes of runtime that return the function selector
 * that was called (first calldata word masked to its top 4 bytes, so the ABI decoder's
 * bytes4 padding check passes). Any onERC721Received / onERC1155Received /
 * onERC1155BatchReceived probe therefore sees its own selector echoed back and accepts the
 * token. Used to exercise safeTransfer hooks without adding a Solidity contract to the repo.
 * Runtime: PUSH1 0 CALLDATALOAD PUSH4 0xffffffff PUSH1 0xe0 SHL AND PUSH1 0 MSTORE PUSH1 32 PUSH1 0 RETURN.
 */
async function deployEchoReceiver(signer) {
  // init (11 bytes): PUSH1 0x14 DUP1 PUSH1 0x0b PUSH1 0 CODECOPY PUSH1 0 RETURN — copies the 20-byte runtime.
  const initCode = '0x601480600b6000396000f3' + '60003563ffffffff60e01b1660005260206000f3';
  const resp = await signer.sendTransaction({ data: initCode });
  const receipt = await resp.wait();
  return { address: receipt.contractAddress, gasUsed: receipt.gasUsed };
}

/** ISO 3779 17-character VINs used across the demos (realistic make/model mix). */
const VINS = Object.freeze({
  bmw: 'WBA3A5C55CF256789',
  honda: '1HGCM82633A004352',
  acura: 'JH4KA7532NC036794',
  vw: 'WVWZZZ1JZXW000001',
  tesla: '5YJ3E1EA7KF317000',
  ford: '1FTFW1ET5DFC10312',
  hyundai: 'KMHD84LF1HU123456',
  fiat: 'ZFA19200000123456',
  renault: 'VF1RFB00X59012345',
  toyota: 'JTDKN3DU0A0123456',
  volvo: 'YV1MS672092123456',
});
for (const [k, v] of Object.entries(VINS)) assert.equal(v.length, 17, `VIN ${k} must be 17 chars`);

/** ERC-165 interface ids used in the demos. */
const IFACE = Object.freeze({
  ERC165: '0x01ffc9a7',
  ERC721: '0x80ac58cd',
  ERC721Metadata: '0x5b5e139f',
  ERC721Enumerable: '0x780e9d63',
  ERC1155: '0xd9b67a26',
  ERC1155MetadataURI: '0x0e89341c',
  ERC2981: '0x2a55205a',
  AccessControl: '0x7965db0b',
});

module.exports = { demo, eventArgs, eventCount, deployEchoReceiver, VINS, IFACE, assert };
