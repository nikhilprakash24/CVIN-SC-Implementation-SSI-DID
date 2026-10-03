"use strict";
const { makeActors } = require("../lib/actors");

/**
 * Deterministic "fresh" key material (review 02, H-3).
 *
 * Every fresh controller / delegate / issuer key is derived as
 *   sk_i = keccak256(abi.encode("cvin-bench/fresh-key/v1", seed, i))
 * with `seed` = the dataset seed (42) and `i` a counter that restarts at 0 on
 * every chain reset (freshAdapter), so each (scenario, adapter) cell sees the
 * same key sequence whatever scenarios or adapters were selected for the run.
 * The keccak domain is disjoint from the HD-derived actor accounts.
 *
 * Candidates whose address contains a 0x00 byte are skipped: calldata prices a
 * zero byte at 4 gas and a non-zero byte at 16, so this keeps calldata gas equal
 * across iterations and substrates (framework §3, equal payload sizes) and
 * makes every iteration of a repeated op cost the same.
 */
const KEY_DOMAIN = "cvin-bench/fresh-key/v1";
const KEY_SEED = 42; // = dataset seed (meta.conditions.datasetSeed)

function hasZeroByte(hex) {
  const h = hex.replace(/^0x/, "");
  for (let i = 0; i < h.length; i += 2) if (h.slice(i, i + 2) === "00") return true;
  return false;
}

function resetKeys(ctx) {
  ctx.keyCounter = 0;
}

function nextWallet(ctx) {
  const { ethers } = ctx;
  const coder = ethers.AbiCoder.defaultAbiCoder();
  if (ctx.keyCounter === undefined) ctx.keyCounter = 0;
  for (;;) {
    const i = ctx.keyCounter++;
    const sk = ethers.keccak256(coder.encode(["string", "uint256", "uint256"], [KEY_DOMAIN, KEY_SEED, i]));
    let w;
    try { w = new ethers.Wallet(sk); } catch { continue; } // sk >= n (negligible)
    if (!hasZeroByte(w.address)) return w;
  }
}

async function resetChain(hre) {
  await hre.network.provider.send("hardhat_reset");
}

/** Fresh chain + fresh adapter + deployment accounting. Restarts the key counter. */
async function freshAdapter(ctx, adapterId, scenario) {
  await resetChain(ctx.hre);
  resetKeys(ctx);
  const actors = makeActors(ctx.ethers);
  const Adapter = ctx.ADAPTERS[adapterId];
  const adapter = new Adapter({ ethers: ctx.ethers, actors, dataset: ctx.dataset, payloads: ctx.payloads });
  const deployed = await adapter.deploy();
  const deployRows = [];
  for (const { name, contract } of deployed) {
    deployRows.push(await ctx.collector.measureDeploy({ adapter: adapterId, scenario, contract: name }, contract));
  }
  return { adapter, actors, deployRows };
}

/**
 * Deterministic credential hash. A zero byte in the hash would make its calldata
 * 12 gas cheaper than another iteration's, so a deterministic salt is appended
 * until the hash has none (same rule as for keys).
 */
function credHash(ctx, ...parts) {
  const { keccak256, toUtf8Bytes } = ctx.ethers;
  for (let salt = 0; ; salt++) {
    const h = keccak256(toUtf8Bytes(parts.join("|") + (salt ? `#${salt}` : "")));
    if (!hasZeroByte(h)) return h;
  }
}

/** Fresh unfunded key (delegate / signing key). */
function freshKey(ctx) {
  return nextWallet(ctx);
}

/** Fresh funded wallet: every identity gets its own controller address (ERC-1056: address == DID). */
async function freshOwner(ctx) {
  const w = nextWallet(ctx).connect(ctx.ethers.provider);
  await ctx.hre.network.provider.send("hardhat_setBalance", [w.address, "0x3635C9ADC5DEA00000"]); // 1000 ETH
  return w;
}

/**
 * Fresh credential issuer for one V-op iteration (review 02, H-1): a funded key
 * whose issuer identity is created and whose signing key is anchored, both
 * unmeasured. This reproduces the state the shared issuer had before the first
 * V-op iteration, so every iteration (and every N) starts from the same state.
 */
async function freshIssuer(ctx, adapter) {
  const issuer = await freshOwner(ctx);
  await adapter.prepareIssuer(issuer);
  const signingKey = freshKey(ctx);
  const r = await adapter.anchorIssuerKey(issuer, signingKey);
  for (const t of r.txs) await t.wait();
  return issuer;
}

function log(ctx, ...args) {
  if (!ctx.opts.quiet) console.log("  ", ...args);
}

module.exports = { resetChain, freshAdapter, credHash, freshKey, freshOwner, freshIssuer, log, hasZeroByte, KEY_DOMAIN, KEY_SEED };
