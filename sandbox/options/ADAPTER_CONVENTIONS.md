# Adapter conventions (plan S2)

- One `adapter.js` per on-chain option directory, exporting a class constructed with
  `{ ethers, signers: { deployer, vehicleOwner, newOwner, delegate } }` (Hardhat's `ethers`).
- Implements every method in `sandbox/lib/identity_option.js` (`METHODS`). Unsupported
  capabilities return `new NotApplicable(reason)` — the reason must match the option's
  `manifest.yaml` stance/reason for that family; never throw for them.
- Load contracts from the compiled artifacts (`ethers.getContractFactory(name)` under
  the Hardhat runtime); never copy Solidity.
- `create` returns the option's identity id as a string (address / token id / contract
  address) and the exact `gasUsed` (BigInt) from the receipt — or `implicit: true, gasUsed: 0n`.
- `resolve` returns a DID-document-like plain object: `{ id, controller, verificationMethod: [...], ... }`
  built from on-chain reads only (no caching), so L1/L3 can compare options.
- Record, in a short header comment, which contract functions each method maps to —
  that mapping is the per-option asymmetry note the thesis cites.
- Acceptance: `cd 1_blockchain-identity && npx hardhat run ../sandbox/grand/smoke.js` prints
  one block per adapter with no `FAILED` and no `??` rows.
