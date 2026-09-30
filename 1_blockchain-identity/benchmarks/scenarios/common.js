"use strict";
const { makeActors } = require("../lib/actors");

async function resetChain(hre) {
  await hre.network.provider.send("hardhat_reset");
}

/** Fresh chain + fresh adapter + deployment accounting. */
async function freshAdapter(ctx, adapterId, scenario) {
  await resetChain(ctx.hre);
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

function credHash(ctx, ...parts) {
  return ctx.ethers.keccak256(ctx.ethers.toUtf8Bytes(parts.join("|")));
}

function freshKey(ctx) {
  return ctx.ethers.Wallet.createRandom();
}

/** Fresh funded wallet: every identity gets its own controller address (ERC-1056: address == DID). */
async function freshOwner(ctx) {
  const w = ctx.ethers.Wallet.createRandom().connect(ctx.ethers.provider);
  await ctx.hre.network.provider.send("hardhat_setBalance", [w.address, "0x3635C9ADC5DEA00000"]); // 1000 ETH
  return w;
}

function log(ctx, ...args) {
  if (!ctx.opts.quiet) console.log("  ", ...args);
}

module.exports = { resetChain, freshAdapter, credHash, freshKey, freshOwner, log };
