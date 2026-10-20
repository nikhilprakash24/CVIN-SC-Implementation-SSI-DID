/**
 * experiment_pseudonym_pool.js — M5, pseudonym pool on ERC-1056
 * (PLAN_MOBI_SUMO.md M5 and its pre-registration in §A.2; review §5.4;
 * after-action report 05, stream G-K).
 *
 * Registry: the standard EthereumDIDRegistry (contracts/ERC1056/), NOT the
 * cv2x ERC1056Registry (K-5). Hardhat in-process network (M1).
 *
 * Pre-registered (verbatim, PLAN_MOBI_SUMO §A.2):
 *   hypothesis: "a 20-delegate pseudonym pool costs ≈20 × addDelegate (≈1.44 M gas)
 *   per rotation epoch and is fully linkable from chain data (all delegates hang off
 *   one identity) — i.e. ERC-1056 delegates give *key* rotation, not *identity*
 *   unlinkability, unlike SCMS pseudonyms"; metric: gas; linkability as a yes/no
 *   with the linking query shown; consequence: the privacy section states that
 *   SSI-on-Ethereum needs per-pseudonym identities (cheap, since creation is
 *   implicit) rather than delegates to match SCMS.
 *
 * Operationalisation, fixed in this file BEFORE the first run:
 *   "≈1.44 M"   the measured gas of one rotation epoch (20 addDelegate receipts)
 *               lies within ±10 % of 20 × 72,219 = 1,444,380 (72,219 = register
 *               row #2's addDelegate). Judged for every epoch; the verdict is
 *               PASS only if all epochs are inside the band.
 *   "linkable"  YES if ONE eth_getLogs query (DIDDelegateChanged, topic1 =
 *               the vehicle's identity) returns all 20 pseudonyms of every
 *               epoch, and if an observer holding only ONE pseudonym address
 *               reaches the other 19 of its epoch from chain data (two steps:
 *               scan DIDDelegateChanged for that delegate -> its identity ->
 *               the identity query).
 *
 * Schemes:
 *   A  delegate pool: one vehicle identity (did:ethr:<V>); each epoch
 *      (EPOCH_S = 300 s of simulated time, evm_increaseTime) V calls
 *      addDelegate(V, veriKey, P_i, EPOCH_S) for 20 fresh pseudonym addresses.
 *   B  per-pseudonym identities (the pre-registration's alternative): each
 *      pseudonym is its own did:ethr:<P_i>; creation is implicit (0 gas, no tx).
 *      B0 no attributes needed: no transaction at all.
 *      B1 an attribute per pseudonym (e.g. a veriKey), self-sent: P_i must hold
 *         ETH, so V funds it (21,000-gas transfer) and P_i calls setAttribute.
 *      B2 an attribute per pseudonym via a shared relayer: P_i signs
 *         setAttributeSigned off-chain, the relayer submits it and pays.
 *   The same identity-topic query is run per pseudonym, and the remaining
 *   chain-level linkage (funding transfers, tx sender, timing) is measured.
 *
 * Output: ../4_comparison-framework/results/pseudonym_pool.{json,md}
 * Run:    npx hardhat run scripts/experiment_pseudonym_pool.js
 */

const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");
const { ethers, network } = require("hardhat");

const POOL = 20;
const EPOCH_S = 300;
const EPOCHS = 3;
const ROW2_ADD_DELEGATE_GAS = 72219;
let regIface = null; // EthereumDIDRegistry interface, set by deployRegistry
const PREREG_EPOCH_GAS = POOL * ROW2_ADD_DELEGATE_GAS; // 1,444,380
const BAND = 0.10;
const VERIKEY = ethers.encodeBytes32String("veriKey");
const ATTR_NAME = ethers.encodeBytes32String("did/pub/Secp256k1/veriKey/hex");
const FUND_WEI = ethers.parseEther("0.01");

/** Deterministic pseudonym wallet (reproducible addresses across runs). */
function pseudonymWallet(tag, epoch, i) {
  return new ethers.Wallet(ethers.id(`m5-pseudonym:${tag}:${epoch}:${i}`), ethers.provider);
}

async function advance(seconds) {
  await network.provider.send("evm_increaseTime", [seconds]);
  await network.provider.send("evm_mine", []);
}

async function deployRegistry() {
  const F = await ethers.getContractFactory("EthereumDIDRegistry");
  const reg = await F.deploy();
  const r = await reg.deploymentTransaction().wait();
  regIface = reg.interface;
  return { reg, deployGas: Number(r.gasUsed) };
}

function identityTopic(addr) {
  return ethers.zeroPadValue(addr, 32);
}

/** The linking query: every DIDDelegateChanged log with topic1 = identity. */
async function delegateLogsByIdentity(reg, identity) {
  const ev = reg.interface.getEvent("DIDDelegateChanged");
  const logs = await ethers.provider.getLogs({
    address: await reg.getAddress(),
    fromBlock: 0,
    toBlock: "latest",
    topics: [ev.topicHash, identityTopic(identity)],
  });
  return logs.map((l) => reg.interface.parseLog(l));
}

/** Any registry event (all three types) whose topic1 is `identity`. */
async function anyLogsByIdentity(reg, identity) {
  const logs = await ethers.provider.getLogs({
    address: await reg.getAddress(),
    fromBlock: 0,
    toBlock: "latest",
    topics: [null, identityTopic(identity)],
  });
  return logs.map((l) => reg.interface.parseLog(l));
}

/** Step 1 of the reverse link: scan every DIDDelegateChanged for one delegate address. */
async function identityOfDelegate(reg, delegate) {
  const ev = reg.interface.getEvent("DIDDelegateChanged");
  const logs = await ethers.provider.getLogs({
    address: await reg.getAddress(), fromBlock: 0, toBlock: "latest", topics: [ev.topicHash],
  });
  const ids = new Set();
  for (const l of logs) {
    const p = reg.interface.parseLog(l);
    if (p.args.delegate.toLowerCase() === delegate.toLowerCase()) ids.add(p.args.identity);
  }
  return [...ids];
}

// ---------------------------------------------------------------- scheme A --
async function runDelegatePool(reg, vehicle, { pool = POOL, epochs = EPOCHS, epochS = EPOCH_S, tag = "A" } = {}) {
  const out = { epochs: [] };
  for (let e = 0; e < epochs; e++) {
    const startBlock = await ethers.provider.getBlock("latest");
    const pseudonyms = [];
    const gas = [];
    for (let i = 0; i < pool; i++) {
      const p = pseudonymWallet(tag, e, i).address;
      const tx = await reg.connect(vehicle).addDelegate(vehicle.address, VERIKEY, p, epochS);
      const r = await tx.wait();
      gas.push(Number(r.gasUsed));
      pseudonyms.push(p);
    }
    const validNow = [];
    for (const p of pseudonyms) validNow.push(await reg.validDelegate(vehicle.address, VERIKEY, p));
    let prevExpired = null;
    if (e > 0) {
      prevExpired = true;
      for (const p of out.epochs[e - 1].pseudonyms) {
        if (await reg.validDelegate(vehicle.address, VERIKEY, p)) prevExpired = false;
      }
    }
    out.epochs.push({
      epoch: e,
      start_timestamp: startBlock.timestamp,
      pseudonyms,
      gas_per_add_delegate: gas,
      epoch_gas: gas.reduce((a, b) => a + b, 0),
      all_current_valid: validNow.every(Boolean),
      previous_epoch_expired: prevExpired,
    });
    await advance(epochS); // rotation: the epoch's delegates expire (validTo = start + epochS)
  }
  // after the last epoch the last pool has expired too
  let lastExpired = true;
  for (const p of out.epochs[epochs - 1].pseudonyms) {
    if (await reg.validDelegate(vehicle.address, VERIKEY, p)) lastExpired = false;
  }
  out.last_epoch_expired_after_rotation = lastExpired;
  return out;
}

async function linkabilityDelegatePool(reg, vehicle, result) {
  const logs = await delegateLogsByIdentity(reg, vehicle.address);
  const returned = new Set(logs.map((l) => l.args.delegate));
  const perEpoch = result.epochs.map((ep) => ({
    epoch: ep.epoch,
    pseudonyms_returned: ep.pseudonyms.filter((p) => returned.has(p)).length,
    of: ep.pseudonyms.length,
  }));
  // reverse link from ONE pseudonym (epoch 1, index 7 — any would do)
  const probe = result.epochs[Math.min(1, result.epochs.length - 1)].pseudonyms[7 % result.epochs[0].pseudonyms.length];
  const ids = await identityOfDelegate(reg, probe);
  const siblings = ids.length === 1 ? (await delegateLogsByIdentity(reg, ids[0])).map((l) => l.args.delegate) : [];
  const linkable = perEpoch.every((x) => x.pseudonyms_returned === x.of) && ids.length === 1 &&
    ids[0] === vehicle.address && result.epochs.every((ep) => ep.pseudonyms.every((p) => siblings.includes(p)));
  return {
    query: {
      method: "eth_getLogs",
      params: { address: await reg.getAddress(), fromBlock: 0, toBlock: "latest",
        topics: [reg.interface.getEvent("DIDDelegateChanged").topicHash, identityTopic(vehicle.address)] },
    },
    logs_returned: logs.length,
    distinct_pseudonyms_returned: returned.size,
    per_epoch: perEpoch,
    reverse_link_from_one_pseudonym: {
      pseudonym: probe,
      step1: "eth_getLogs topics=[DIDDelegateChanged] (all identities), filter data.delegate == pseudonym",
      identities_found: ids,
      step2: "the identity query above",
      siblings_reached: siblings.length,
    },
    linkable,
  };
}

// ---------------------------------------------------------------- scheme B --
async function signSetAttribute(reg, wallet, identity, name, value, validity) {
  const nonce = await reg.nonce(identity);
  const hash = ethers.solidityPackedKeccak256(
    ["bytes1", "bytes1", "address", "uint256", "address", "string", "bytes32", "bytes", "uint256"],
    ["0x19", "0x00", await reg.getAddress(), nonce, identity, "setAttribute", name, value, validity]);
  return ethers.Signature.from(wallet.signingKey.sign(hash));
}

async function runPerPseudonym(reg, vehicle, relayer, mode, { pool = POOL, epochs = EPOCHS, epochS = EPOCH_S, tag } = {}) {
  const out = { mode, epochs: [] };
  for (let e = 0; e < epochs; e++) {
    const pseudonyms = [];
    const gas = { funding: [], set_attribute: [] };
    const txs = [];
    for (let i = 0; i < pool; i++) {
      const w = pseudonymWallet(tag || mode, e, i);
      pseudonyms.push(w.address);
      const value = w.signingKey.compressedPublicKey; // the pseudonym's own key as the attribute value
      if (mode === "B1") {
        const f = await (await vehicle.sendTransaction({ to: w.address, value: FUND_WEI })).wait();
        gas.funding.push(Number(f.gasUsed));
        txs.push({ hash: f.hash, from: f.from, to: f.to, kind: "funding" });
        const r = await (await reg.connect(w).setAttribute(w.address, ATTR_NAME, value, epochS)).wait();
        gas.set_attribute.push(Number(r.gasUsed));
        txs.push({ hash: r.hash, from: r.from, to: r.to, kind: "setAttribute" });
      } else if (mode === "B2") {
        const sig = await signSetAttribute(reg, w, w.address, ATTR_NAME, value, epochS);
        const r = await (await reg.connect(relayer).setAttributeSigned(
          w.address, sig.v, sig.r, sig.s, ATTR_NAME, value, epochS)).wait();
        gas.set_attribute.push(Number(r.gasUsed));
        txs.push({ hash: r.hash, from: r.from, to: r.to, kind: "setAttributeSigned" });
      }
      // B0: nothing on chain. did:ethr:<P> resolves to its implicit document (owner = P).
    }
    const ownerOk = [];
    for (const p of pseudonyms) ownerOk.push((await reg.identityOwner(p)) === p);
    const sum = (a) => a.reduce((x, y) => x + y, 0);
    out.epochs.push({
      epoch: e, pseudonyms,
      gas_funding: gas.funding, gas_set_attribute: gas.set_attribute,
      epoch_gas: sum(gas.funding) + sum(gas.set_attribute),
      implicit_owner_is_self: ownerOk.every(Boolean),
      txs,
    });
    await advance(epochS);
  }
  return out;
}

/** Scan all blocks' transactions for funding of / registry writes by the pseudonyms. */
async function txLayerScan(registryAddr, pseudonymSet) {
  const latest = await ethers.provider.getBlockNumber();
  const funders = {};
  const registrySenders = {};
  let touching = 0;
  for (let n = 0; n <= latest; n++) {
    const b = await ethers.provider.getBlock(n, true);
    for (const tx of b.prefetchedTransactions) {
      const to = (tx.to || "").toLowerCase();
      const from = tx.from;
      if (pseudonymSet.has(to)) { touching++; funders[from] = (funders[from] || 0) + 1; }
      if (to === registryAddr.toLowerCase()) {
        const d = regIface.parseTransaction({ data: tx.data });
        const id = d && d.args && d.args[0] ? String(d.args[0]).toLowerCase() : null;
        if (id && pseudonymSet.has(id)) { touching++; registrySenders[from] = (registrySenders[from] || 0) + 1; }
      }
    }
  }
  return { blocks_scanned: latest + 1, txs_touching_pseudonyms: touching, funders, registry_senders: registrySenders };
}

/** Same identity-topic query per pseudonym, plus the residual linkage observed at the transaction layer. */
async function linkabilityPerPseudonym(reg, vehicle, relayer, result) {
  const all = result.epochs.flatMap((ep) => ep.pseudonyms);
  const allSet = new Set(all.map((a) => a.toLowerCase()));
  let maxOtherPseudonymsReached = 0;
  let delegateLogsTotal = 0;
  const perPseudonymEventCounts = [];
  for (const p of all) {
    const dl = await delegateLogsByIdentity(reg, p);
    delegateLogsTotal += dl.length;
    const any = await anyLogsByIdentity(reg, p);
    perPseudonymEventCounts.push(any.length);
    // does anything returned for p mention another pseudonym of this vehicle?
    const mentioned = new Set();
    for (const l of any) {
      for (const v of Object.values(l.args.toObject())) {
        if (typeof v === "string" && allSet.has(v.toLowerCase()) && v.toLowerCase() !== p.toLowerCase()) mentioned.add(v);
      }
    }
    maxOtherPseudonymsReached = Math.max(maxOtherPseudonymsReached, mentioned.size);
  }
  const vehicleDelegateLogs = await delegateLogsByIdentity(reg, vehicle.address);
  // transaction-layer linkage, from chain data only: scan every block's full
  // transactions; group the txs that fund a pseudonym, and the registry txs
  // that write a pseudonym's identity, by sender.
  const scan = await txLayerScan(await reg.getAddress(), allSet);
  const fundingSenders = Object.keys(scan.funders);
  const registrySenders = Object.keys(scan.registry_senders);
  const nonSelfRegistry = registrySenders.filter((s) => !allSet.has(s.toLowerCase()));
  let residual;
  if (scan.txs_touching_pseudonyms === 0) {
    residual = "none at the chain layer: no transaction touches any pseudonym. Linkage, if any, is off-chain (radio, timing, position).";
  } else if (fundingSenders.length > 0) {
    const max = Math.max(...Object.values(scan.funders));
    residual = `LINKABLE by funding pattern: ${max} of ${all.length} pseudonyms were funded by one address ` +
      `(${fundingSenders.join(", ")}); query: every block's transactions, filter to ∈ pseudonym set, group by from.`;
  } else {
    residual = `linked to the RELAYER, not to the vehicle: ${scan.registry_senders[nonSelfRegistry[0]]} registry writes for ` +
      `${all.length} pseudonyms were sent by ${nonSelfRegistry.join(", ")}; the anonymity set is the relayer's client ` +
      "population (1 vehicle in this simulation, so here it is trivially linkable by sender + timing).";
  }
  return {
    query: "the same eth_getLogs (DIDDelegateChanged, topic1 = identity), run for each pseudonym identity; " +
      "also all registry events with topic1 = pseudonym",
    pseudonyms: all.length,
    delegate_logs_total_over_pseudonym_queries: delegateLogsTotal,
    registry_events_per_pseudonym: { min: Math.min(...perPseudonymEventCounts), max: Math.max(...perPseudonymEventCounts) },
    max_other_pseudonyms_reached_by_one_query: maxOtherPseudonymsReached,
    vehicle_identity_delegate_logs: vehicleDelegateLogs.length,
    linkable_by_identity_query: maxOtherPseudonymsReached > 0 || vehicleDelegateLogs.length > 0,
    tx_layer_scan: scan,
    funding_senders: fundingSenders,
    registry_tx_senders_other_than_pseudonym: nonSelfRegistry,
    registry_tx_sender_is_vehicle: registrySenders.some((s) => s === vehicle.address),
    residual_linkage: residual,
  };
}

// --------------------------------------------------------------------- run --
function gitInfo() {
  const repo = path.resolve(__dirname, "..", "..");
  try {
    const commit = execFileSync("git", ["rev-parse", "--short", "HEAD"], { cwd: repo }).toString().trim();
    const dirty = execFileSync("git", ["status", "--porcelain"], { cwd: repo }).toString().trim().length > 0;
    return { git_commit: commit, git_dirty: dirty };
  } catch (e) {
    return { git_commit: null, git_dirty: null };
  }
}

async function runAll() {
  const signers = await ethers.getSigners();
  const vehicle = signers[1];
  const relayer = signers[2];
  const vehicleB1 = signers[3];

  const A = await deployRegistry();
  const pool = await runDelegatePool(A.reg, vehicle);
  const poolLink = await linkabilityDelegatePool(A.reg, vehicle, pool);

  const per = {};
  for (const mode of ["B0", "B1", "B2"]) {
    const d = await deployRegistry();
    const funder = mode === "B1" ? vehicleB1 : vehicle;
    const r = await runPerPseudonym(d.reg, funder, relayer, mode);
    r.linkability = await linkabilityPerPseudonym(d.reg, funder, relayer, r);
    per[mode] = r;
  }

  const epochGas = pool.epochs.map((e) => e.epoch_gas);
  const lo = PREREG_EPOCH_GAS * (1 - BAND);
  const hi = PREREG_EPOCH_GAS * (1 + BAND);
  const gasPass = epochGas.every((g) => g >= lo && g <= hi);
  const verdict = {
    gas: {
      claim: "≈20 × addDelegate (≈1.44 M gas) per rotation epoch",
      prereg_value: PREREG_EPOCH_GAS, band: [Math.round(lo), Math.round(hi)],
      measured_epoch_gas: epochGas,
      ratio_to_prereg: epochGas.map((g) => g / PREREG_EPOCH_GAS),
      verdict: gasPass ? "PASS" : "FAIL",
    },
    linkability: {
      claim: "fully linkable from chain data (all delegates hang off one identity)",
      measured: poolLink.linkable ? "YES" : "NO",
      verdict: poolLink.linkable ? "PASS" : "FAIL",
    },
    alternative: {
      claim: "per-pseudonym identities are cheap (creation implicit) and not linkable by the same query",
      creation_gas: 0,
      linkable_by_same_query: Object.fromEntries(Object.entries(per).map(([k, v]) => [k, v.linkability.linkable_by_identity_query])),
    },
  };
  return { pool, poolLink, per, verdict, deployGas: A.deployGas };
}

function env(deployGas) {
  const hh = require("hardhat/package.json").version;
  const ethersV = ethers.version;
  return {
    date_utc: new Date().toISOString(), ...gitInfo(), node_version: process.version, hardhat_version: hh,
    ethers_version: ethersV, network: network.name, chain_id: network.config.chainId || 31337,
    contract: "contracts/ERC1056/EthereumDIDRegistry.sol (standard ERC-1056)",
    compiler: "solc 0.8.24, optimizer 200, viaIR, evm cancun (hardhat.config.js; pragma ^0.8.20 selects 0.8.24)",
    registry_deploy_gas: deployGas, cpu_model: os.cpus()[0] && os.cpus()[0].model, cpu_count: os.cpus().length,
    os: `${os.type()} ${os.release()}`,
  };
}

function writeMd(file, out) {
  const { environment: E, config: C, delegate_pool: P, per_pseudonym: B, verdicts: V } = out;
  const L = [];
  L.push("# M5 — Pseudonym pool on ERC-1056 (pre-registered, PLAN_MOBI_SUMO §A.2)\n");
  L.push("Generated by `1_blockchain-identity/scripts/experiment_pseudonym_pool.js` on the standard " +
    "`EthereumDIDRegistry` (not the cv2x registry, K-5), Hardhat in-process network (M1). Gas is the receipt's " +
    "`gasUsed` (deterministic: one run is exact).\n");
  L.push("## Environment\n", "| Item | Value |", "|---|---|");
  for (const [k, v] of Object.entries(E)) L.push(`| ${k} | ${v} |`);
  L.push(`| config | pool ${C.pool}, epoch ${C.epoch_s} s (evm_increaseTime), ${C.epochs} epochs, delegate type veriKey, validity = epoch |`);
  L.push("");
  L.push("## Pre-registration and operationalisation\n");
  L.push("> **M5 hypothesis:** a 20-delegate pseudonym pool costs ≈20 × addDelegate (≈1.44 M gas) per rotation epoch " +
    "and is fully linkable from chain data (all delegates hang off one identity) — i.e. ERC-1056 delegates give *key* " +
    "rotation, not *identity* unlinkability, unlike SCMS pseudonyms; **metric:** gas; linkability as a yes/no with the " +
    "linking query shown; **consequence:** the privacy section states that SSI-on-Ethereum needs per-pseudonym identities " +
    "(cheap, since creation is implicit) rather than delegates to match SCMS.\n");
  L.push(`Fixed in the script before the first run: "≈1.44 M" = every epoch within ±${C.band * 100} % of ` +
    `20 × 72,219 = ${C.prereg_epoch_gas.toLocaleString("en-US")} (72,219 = register row #2's addDelegate); "linkable" = one ` +
    "identity-topic `eth_getLogs` returns all 20 pseudonyms of every epoch AND one pseudonym address alone leads to the " +
    "other pseudonyms.\n");
  L.push("## A. Delegate pool (20 × addDelegate per 5-min epoch)\n");
  L.push("| epoch | addDelegate gas (first / others / last) | epoch gas | ratio to 1,444,380 | all 20 valid during epoch | previous epoch expired |");
  L.push("|---:|---|---:|---:|:---:|:---:|");
  for (const ep of P.epochs) {
    const g = ep.gas_per_add_delegate;
    const others = [...new Set(g.slice(1, -1))].map((x) => x.toLocaleString("en-US")).join(", ");
    L.push(`| ${ep.epoch} | ${g[0].toLocaleString("en-US")} / ${others} / ${g[g.length - 1].toLocaleString("en-US")} | ` +
      `**${ep.epoch_gas.toLocaleString("en-US")}** | ${(ep.epoch_gas / C.prereg_epoch_gas).toFixed(3)} | ` +
      `${ep.all_current_valid} | ${ep.previous_epoch_expired === null ? "–" : ep.previous_epoch_expired} |`);
  }
  L.push("");
  L.push(`After the last rotation the last pool had expired too: ${P.last_epoch_expired_after_rotation}. ` +
    `Per vehicle and day (288 epochs) the pool costs ≈${(P.epochs[P.epochs.length - 1].epoch_gas * 288 / 1e6).toFixed(0)} M gas ` +
    "(steady-state epoch × 288), and each epoch leaves 20 new non-zero storage slots that are never cleared.\n");
  L.push("### The linking query\n");
  L.push("```json\n" + JSON.stringify(P.linkability.query, null, 2) + "\n```\n");
  L.push(`It returned **${P.linkability.logs_returned} logs = ${P.linkability.distinct_pseudonyms_returned} distinct pseudonyms**; ` +
    "per epoch: " + P.linkability.per_epoch.map((x) => `epoch ${x.epoch}: ${x.pseudonyms_returned}/${x.of}`).join(", ") + ".\n");
  const R = P.linkability.reverse_link_from_one_pseudonym;
  L.push(`Reverse link from ONE pseudonym (\`${R.pseudonym}\`): step 1, ${R.step1}, finds identity ` +
    `${R.identities_found.join(", ")}; step 2, the identity query, reaches **${R.siblings_reached}** pseudonyms ` +
    "(every pseudonym of every epoch). Off chain the link is even more direct: a message signed by a delegate is " +
    "verified against the identity's DID, which the message must name.\n");
  L.push(`**Linkable: ${P.linkability.linkable ? "YES" : "NO"}.**\n`);
  L.push("## B. Per-pseudonym identities (the pre-registration's alternative)\n");
  L.push("| variant | what goes on chain per pseudonym | epoch gas (20 pseudonyms) | per pseudonym | same query links pseudonyms? | residual chain-layer linkage |");
  L.push("|---|---|---:|---|:---:|---|");
  const desc = { B0: "nothing (implicit did:ethr document; creation 0 gas)",
    B1: "vehicle funds P (transfer) + P.setAttribute(veriKey)",
    B2: "relayer submits P's setAttributeSigned(veriKey)" };
  for (const k of ["B0", "B1", "B2"]) {
    const r = B[k];
    const ep = r.epochs[r.epochs.length - 1];
    const per = k === "B0" ? "0" : k === "B1"
      ? `transfer ${ep.gas_funding[0].toLocaleString("en-US")} + setAttribute ${[...new Set(ep.gas_set_attribute)].map((x) => x.toLocaleString("en-US")).join("/")}`
      : `setAttributeSigned ${[...new Set(ep.gas_set_attribute)].map((x) => x.toLocaleString("en-US")).join("/")}`;
    L.push(`| ${k} | ${desc[k]} | ${r.epochs.map((e) => e.epoch_gas.toLocaleString("en-US")).join(" / ")} | ${per} | ` +
      `${r.linkability.linkable_by_identity_query ? "YES" : "NO"} (max other pseudonyms reached: ${r.linkability.max_other_pseudonyms_reached_by_one_query}) | ` +
      `${r.linkability.residual_linkage} |`);
  }
  L.push("");
  L.push("For every pseudonym P the identity query (and a query for all registry events with topic1 = P) returns only " +
    "P's own events (registry events per pseudonym: " +
    ["B0", "B1", "B2"].map((k) => `${k} ${B[k].linkability.registry_events_per_pseudonym.min}–${B[k].linkability.registry_events_per_pseudonym.max}`).join(", ") +
    "); none mentions another pseudonym. Every pseudonym's `identityOwner` is itself (implicit document).\n");
  L.push("## Verdicts (as measured)\n");
  L.push("| Pre-registered claim | Measured | Verdict |", "|---|---|---|");
  L.push(`| Gas ≈ 20 × addDelegate ≈ 1.44 M per epoch (±${C.band * 100} %) | ` +
    `${V.gas.measured_epoch_gas.map((g) => g.toLocaleString("en-US")).join(" / ")} (ratio ${V.gas.ratio_to_prereg.map((x) => x.toFixed(3)).join(" / ")}) | **${V.gas.verdict}** |`);
  L.push(`| Fully linkable from chain data | ${V.linkability.measured} (one query, all ${P.linkability.distinct_pseudonyms_returned}) | **${V.linkability.verdict}** |`);
  L.push(`| Consequence: per-pseudonym identities, creation implicit | creation 0 gas; same query links: ` +
    Object.entries(V.alternative.linkable_by_same_query).map(([k, v]) => `${k} ${v ? "yes" : "no"}`).join(", ") +
    " | supported, with the residual linkage above |");
  L.push("");
  L.push("## Caveats\n");
  L.push("1. **M1 only.** Gas is exact for this compiler/config (solc 0.8.24, viaIR, cancun); a public chain charges the same gas.");
  L.push("2. **Linkability is chain-layer only.** Radio identifiers, message timing and position traces are outside this " +
    "test; SCMS addresses those with its own rules (e.g. change-of-pseudonym policies) that ERC-1056 does not define.");
  L.push("3. **SCMS comparison is structural.** SCMS pseudonym certificates are unlinkable to outsiders by construction " +
    "(butterfly keys, linkage values held by two linkage authorities); nothing is measured for SCMS here.");
  L.push("4. **B2's anonymity set** is the relayer's client population; with one simulated vehicle it is trivially 1.");
  L.push("5. **Calldata spread.** addDelegate gas moves by multiples of 12 with the number of zero bytes in the pseudonym " +
    "address (EIP-2028); the pseudonym keys are derived deterministically (`ethers.id(\"m5-pseudonym:<tag>:<epoch>:<i>\")`) " +
    "so the run is exactly reproducible. Register row #2's 72,219 was measured by `benchmark_gas.js` with other inputs; " +
    "the first addDelegate here (identity's first change, `changed` 0 → non-zero) is 71,919, every later one ≈54.8 k " +
    "(`changed` non-zero → non-zero). The pre-registered ≈1.44 M assumed every addDelegate costs the first-change price.");
  L.push("6. **Not measured:** clearing expired delegates (revokeDelegate) is not needed for validity (validTo expires " +
    "them) and was not run; without it registry state grows by 20 slots per epoch per vehicle.");
  L.push("");
  fs.writeFileSync(file, L.join("\n"));
}

async function main() {
  const res = await runAll();
  const outDir = path.resolve(__dirname, "..", "..", "4_comparison-framework", "results");
  const out = {
    environment: env(res.deployGas),
    config: { pool: POOL, epoch_s: EPOCH_S, epochs: EPOCHS, band: BAND, prereg_epoch_gas: PREREG_EPOCH_GAS,
      row2_add_delegate_gas: ROW2_ADD_DELEGATE_GAS, delegate_type: "veriKey (bytes32)", fund_wei: FUND_WEI.toString() },
    delegate_pool: { ...res.pool, linkability: res.poolLink },
    per_pseudonym: res.per,
    verdicts: res.verdict,
  };
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, "pseudonym_pool.json"), JSON.stringify(out, null, 2));
  writeMd(path.join(outDir, "pseudonym_pool.md"), out);
  console.log("epoch gas (pool):", out.verdicts.gas.measured_epoch_gas, "verdict", out.verdicts.gas.verdict);
  console.log("linkable (pool):", out.verdicts.linkability.measured);
  console.log("per-pseudonym linkable by same query:", out.verdicts.alternative.linkable_by_same_query);
  console.log(`wrote ${path.join(outDir, "pseudonym_pool.{json,md}")}`);
}

module.exports = {
  POOL, EPOCH_S, EPOCHS, PREREG_EPOCH_GAS, VERIKEY, deployRegistry, runDelegatePool, linkabilityDelegatePool,
  runPerPseudonym, linkabilityPerPseudonym, delegateLogsByIdentity, identityOfDelegate,
};

if (require.main === module) {
  main().then(() => process.exit(0)).catch((e) => { console.error(e); process.exit(1); });
}
