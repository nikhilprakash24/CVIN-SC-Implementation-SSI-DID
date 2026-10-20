"use strict";
// Fixed actor set (framework §3). Wallets are derived from Hardhat's default
// mnemonic so they are the pre-funded accounts *and* expose signing keys
// (needed for raw-ecrecover meta-transactions, which HardhatEthersSigner cannot sign).

const ROLES = ["deployer", "manufacturer", "vehicleOwner", "newOwner", "thirdOwner", "issuer", "verifier", "serviceCenter", "attacker", "delegateKey"];
const MNEMONIC = "test test test test test test test test test test test junk";

function makeActors(ethers, count = 20) {
  const provider = ethers.provider;
  const mnemonic = ethers.Mnemonic.fromPhrase(MNEMONIC);
  const wallets = [];
  for (let i = 0; i < count; i++) {
    const w = ethers.HDNodeWallet.fromMnemonic(mnemonic, `m/44'/60'/0'/0/${i}`).connect(provider);
    wallets.push(w);
  }
  const actors = { all: wallets, extras: wallets.slice(ROLES.length) };
  ROLES.forEach((r, i) => (actors[r] = wallets[i]));
  return actors;
}

module.exports = { makeActors, ROLES };
