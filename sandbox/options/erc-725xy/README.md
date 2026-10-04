# erc-725xy — ERC-725 X + Y smart account (plan S7 demos)

**Identity model.** Each vehicle is its own `CVINVehicleERC725XY` account: the contract address is the stable identifier, a single `owner` is the rotating controlling key, the ERC-725Y store (`setData`/`getData` + batch) holds on-chain-readable attributes such as the VIN, and the ERC-725X executor (`execute`/`executeBatch`: CALL, CREATE, CREATE2, STATICCALL, DELEGATECALL) lets the identity act, pay and deploy on-chain. `CVINExecuteTarget` is a test helper used to prove the calls are real.

Run: `cd 1_blockchain-identity && npx hardhat run ../sandbox/options/erc-725xy/demos/<family>.js`.

| Family | Demo | Functions exercised | Measured? (manifest) |
|---|---|---|---|
| creation | `demos/creation.js` | constructor(initialOwner) (zero-owner revert), `owner`, `setVehicleBirthAttributes`, `getVehicleVIN`, `OPERATION_CREATE/CREATE2`, `execute` CREATE + CREATE2 (`ContractCreated`, address checks) | implemented (deployment + VIN key counted as createIdentity) |
| controller | `demos/controller.js` | `owner`, `transferOwnership` (zero guard), `renounceOwnership`, data survives rotation | no (benchmark transferOwnership) |
| attributes | `demos/attributes.js` | `VIN_KEY/MAKE_KEY/MODEL_KEY/YEAR_KEY`, `setData` (cold/warm, payable), `getData`, `setDataBatch`, `getDataBatch`, `setVehicleBirthAttributes`, guards | **yes** (`setData`) |
| revocation | `demos/revocation.js` | `setData(key, 0x)` clear (refund), `getData`, `renounceOwnership`, `getVehicleVIN` after freeze | implemented (sub-identity only) |
| signed-execution | `demos/signed-execution.js` | `OPERATION_*` constants, `supportsInterface` ×5, `execute` CALL (`CVINExecuteTarget.setValue/value/lastCaller`), STATICCALL (return data), `willRevert` direct + bubbled, value transfer via `receive`, `executeBatch`, DELEGATECALL (owner clobbered), all guards | implemented (not measured; L1 signed-op uses CALL) |
| lifecycle-history | `demos/lifecycle-history.js` | event scan of `DataChanged`/`Executed`/`ContractCreated`/`OwnershipTransferred`; odometer history vs `getData` | implemented (not measured) |
| vin-linkage | `demos/vin-linkage.js` | `VIN_KEY`, `setData(VIN_KEY)`, `getVehicleVIN`, `getData`; overwrite / duplicate VIN probes | implemented (not measured) |

## Asymmetry notes

- **Creation: deployed** — the heaviest option (≈1.73M incl. the VIN write) but it buys an account that can custody ETH, call, and deploy children (CREATE/CREATE2 from the identity's own nonce/salt). The deployer may create an account owned by someone else (`constructor(initialOwner)`).
- **Veracity / automation.** Chain enforces: `msg.sender == owner` on every write/execute, the five canonical operation types and their guards, revert bubbling from callees, ERC-165 interface ids. Data values are readable on-chain by any contract (`getData`/`getVehicleVIN`) — no event replay needed for current state. It does **not** enforce: any VIN format/uniqueness/immutability (the owner can overwrite it; two accounts can claim the same VIN), expiry of data, issuer signatures (no claims), identity-level revocation (clearing a key is indistinguishable from never-set). No `changed` pointer: history is an O(chain) log scan, and `Executed` carries only the 4-byte selector.
- **Cryptography / hashing.** Data keys are `keccak256("cvin:…")`; no signature verification anywhere ("signed execution" = the owner EOA signs the outer transaction). CREATE2 addresses follow `keccak256(0xff ‖ account ‖ salt ‖ keccak256(initcode))` with the erc725 convention salt = last 32 bytes of `data`.
- **Implemented but not compared.** `executeBatch`, CREATE/CREATE2/STATICCALL/DELEGATECALL, value transfer, `setDataBatch`/`getDataBatch`, `setVehicleBirthAttributes`, `supportsInterface`, `renounceOwnership`, `receive()`.
- **Observed defects / surprises.** Unrestricted DELEGATECALL (spec-conformant) lets a benign-looking target overwrite slot 0 = `_owner`, bricking the identity; `setData` is payable so attribute writes can silently carry ETH into the account; the VIN is freely rewritable; `renounceOwnership` freezes an account that keeps asserting its VIN.

## Coverage check

ABI public/external functions: 25 (21 account + 4 `CVINExecuteTarget`). Covered: **25 / 25**. Uncovered: none.
