// LIM-R7-08: does the executed instrument (Hardhat 2.28.6, default hardfork) apply the EIP-7623 calldata floor?
// Run from 1_blockchain-identity/:  npx hardhat run ../docs/roots/phase2/70_R7_theory_ece_bounds/measure/lim_r7_08_receipt.js
// Two measurements, each predicted under both pricing rules before it is sent:
//   A. 1,024 non-zero calldata bytes to an account with no code (execution gas 0): the floor must bind if EIP-7623 is active.
//   B. A bare LOG3 of B bytes of calldata (raw-bytecode contract, no Solidity): R7 PF-52's "log-only" case.
// Pricing: tokens = zero + 4*nonzero; standard = 21000 + 4*tokens + exec; floor = 21000 + 10*tokens;
// gasUsed = max(standard, floor) under EIP-7623, = standard without it.
const hre = require("hardhat");

function tokens(hex) {
  const b = Buffer.from(hex.replace(/^0x/, ""), "hex");
  let z = 0, n = 0;
  for (const x of b) (x === 0 ? z++ : n++);
  return { z, n, tokens: z + 4 * n };
}

async function main() {
  const [s] = await hre.ethers.getSigners();
  const hardfork = hre.config.networks.hardhat.hardfork || "(Hardhat default)";
  const block = await hre.ethers.provider.getBlock("latest");
  const out = { hardhat: require("hardhat/package.json").version, hardfork, blockGasLimit: block.gasLimit.toString(), rows: [] };

  // A: plain calldata to a codeless address
  const data = "0x" + "ab".repeat(1024);
  const t = tokens(data);
  const rA = await (await s.sendTransaction({ to: "0x000000000000000000000000000000000000dEaD", data })).wait();
  out.rows.push({ case: "A calldata-only 1024 nonzero bytes", ...t, exec: 0,
    predicted_standard: 21000 + 4 * t.tokens, predicted_floor: 21000 + 10 * t.tokens, gasUsed: Number(rA.gasUsed) });

  // B: deploy runtime 365f5f37600360026001365fa300 = CALLDATACOPY all calldata to memory, LOG3(0, size, 1, 2, 3), STOP
  const init = "0x600e600a5f39600e5ff3" + "365f5f37600360026001365fa300";
  const dep = await (await s.sendTransaction({ data: init })).wait();
  const logger = dep.contractAddress;
  for (const B of [128, 1024, 2048]) {
    const d = "0x" + "ab".repeat(B);
    const tk = tokens(d);
    const r = await (await s.sendTransaction({ to: logger, data: d })).wait();
    // execution: CALLDATASIZE 2, PUSH0 2 x2, CALLDATACOPY 3 + 3*words + memory, PUSH1 3 x3, CALLDATASIZE 2, PUSH0 2, LOG3 375*4 + 8B + memory (charged once), STOP 0
    const words = Math.ceil(B / 32);
    const mem = 3 * words + Math.floor(words * words / 512);
    const exec = 2 + 2 + 2 + (3 + 3 * words) + mem + 3 * 3 + 2 + 2 + (375 + 3 * 375 + 8 * B);
    out.rows.push({ case: `B LOG3 ${B} bytes`, ...tk, exec_predicted: exec,
      predicted_standard: 21000 + 4 * tk.tokens + exec, predicted_floor: 21000 + 10 * tk.tokens,
      gasUsed: Number(r.gasUsed), logs: r.logs.length });
  }
  for (const row of out.rows) {
    row.matches = row.gasUsed === Math.max(row.predicted_standard, row.predicted_floor) ? "max(standard, floor) — EIP-7623 ACTIVE"
      : row.gasUsed === row.predicted_standard ? "standard — EIP-7623 NOT active" : "neither (see exec model)";
  }
  console.log(JSON.stringify(out, null, 2));
}
main().catch((e) => { console.error(e); process.exit(1); });
