# Public-Testnet Validation (Sepolia)

This harness confirms that the Hardhat-local gas measurements in
`4_comparison-framework/results/gas_benchmark.json` **reproduce on a real
Ethereum network** (Sepolia), recording real, independently verifiable
transaction hashes.

## What this is (and is not)

- **It is a _witness_.** Gas is deterministic across EVM networks for identical
  bytecode + calldata. Deploying the same contracts and sending the same
  operations to a public chain and getting the **same `gasUsed`** is evidence
  that the thesis's local numbers are real, not an artifact of the in-process
  Hardhat VM. Each recorded transaction hash can be checked by anyone on
  [Sepolia Etherscan](https://sepolia.etherscan.io).
- **It is _not_ a performance / latency / throughput sample.** A public testnet
  says nothing meaningful about production TPS or confirmation time. The claim
  being validated is strictly: *the gas costs are genuine and reproducible.*

By default it validates a thesis-critical subset of **3 standards**:

| Standard        | Why it's in the subset                         |
| --------------- | ---------------------------------------------- |
| `ERC-1056`      | cheapest event-based DID registry              |
| `ERC-725xy`     | full ERC-725 X+Y on-chain smart account        |
| `CVIN-Combined` | the ERC-1056 + ERC-735 hybrid (this thesis)    |

The runner is **network-agnostic**: the exact same script runs on the in-process
Hardhat network (as a zero-cost dry-run self-test), on a `localhost` node, or on
Sepolia.

## Dry-run (no setup, no ETH required)

```bash
cd 1_blockchain-identity
npx hardhat run scripts/validate_sepolia.js
```

This deploys the 3 standards on the in-process Hardhat network, runs each
operation, records real local transaction hashes + `gasUsed`, and compares each
against the committed baseline. On Hardhat almost every operation reproduces the
baseline **exactly (delta 0)**; see the note on deltas below for the one small,
explainable exception. Results land in
`4_comparison-framework/results/sepolia_validation.json`.

## Real Sepolia validation

### 1. Get a free RPC endpoint

Create a free account at **[Alchemy](https://alchemy.com)** or
**[Infura](https://infura.io)**, create an app on the **Ethereum Sepolia**
network, and copy the HTTPS URL, e.g.
`https://eth-sepolia.g.alchemy.com/v2/<YOUR_KEY>`.

### 2. Create a test-only key and fund it

Generate a throwaway key (e.g. `node -e "console.log(require('ethers').Wallet.createRandom().privateKey)"`
or use MetaMask) that you will **never** use for real funds. Copy its address
and request test ETH from a free faucet:

- https://sepoliafaucet.com  (Alchemy)
- https://www.infura.io/faucet/sepolia
- https://faucet.quicknode.com/ethereum/sepolia

You need only a small amount; the harness checks for at least **0.05 ETH**.

### 3. Set environment variables

Copy `.env.example` to `.env` (the same directory) and fill in:

```dotenv
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/<YOUR_KEY>
PRIVATE_KEY=<0x-prefixed private key of the funded test account>
```

`.env` is git-ignored. **Never commit a private key.**

### 4. Run

```bash
cd 1_blockchain-identity
npx hardhat run scripts/validate_sepolia.js --network sepolia
```

The harness runs a preflight (RPC reachable, key present, balance above the
threshold), then deploys and exercises each standard **sequentially** (one
transaction confirmed before the next is sent). For every transaction it records
`{ standard, operation, txHash, gasUsed, blockNumber, status }`, builds a
`https://sepolia.etherscan.io/tx/<hash>` link, and compares `gasUsed` to the
local baseline.

If `SEPOLIA_RPC_URL` / `PRIVATE_KEY` are missing or the account is underfunded,
it prints clear guidance and exits non-zero **without** a stack trace.

## Where results land

`4_comparison-framework/results/sepolia_validation.json`:

```jsonc
{
  "network": "sepolia",
  "chainId": 11155111,
  "timestamp": "2026-...T...Z",
  "signer": "0x...",
  "mode": "public-validation",
  "results": [
    {
      "standard": "ERC-1056",
      "operation": "createIdentity",
      "txHash": "0x...",
      "gasUsed": 52612,
      "localBaseline": 52612,
      "delta": 0,
      "blockNumber": 1234567,
      "status": 1,
      "explorerUrl": "https://sepolia.etherscan.io/tx/0x..."
    }
    // ...
  ],
  "summary": {
    "total_txs": 11,
    "failed_ops": 0,
    "compared_against_baseline": 11,
    "gas_matches_local": true,   // all baselined ops match within calldata tolerance
    "exact_matches": 10,         // ops that matched the baseline to the gas
    "max_abs_delta": 12,         // largest calldata-only difference observed
    "calldata_tolerance": 100
  }
}
```

### A note on deltas

Gas differences here are pure **calldata** artifacts (intrinsic cost: 4 gas per
zero byte vs 16 per non-zero byte), never differences in contract execution.
Two sources exist:

1. **Signature over the contract address (Hardhat and Sepolia).** The
   `CVIN-Combined/addDelegateOrClaim` operation submits a 65-byte issuer
   signature computed over the deployed registry's address. Because this
   validation run deploys only a 3-standard subset, the `CVINCombinedIdentity`
   contract lands at a different address than in the full 10-standard benchmark
   (lower deployer nonce), which changes the signature's zero-byte count. The
   dry-run therefore shows a small `delta` (about **+12 gas** on ~289,900) for
   this one operation. The contract logic and its execution gas are identical.

2. **Fallback target addresses (Sepolia only).** On Sepolia there is a single
   funded account, so pure "target" roles (a delegate or new-owner address that
   never signs) fall back to fixed placeholder addresses with a different
   zero-byte count than the Hardhat default signers. A couple of operations may
   differ by a **handful of gas units**.

All such differences are recorded in `delta` and `summary.max_abs_delta` so they
are visible and auditable rather than hidden.

## Extending to more standards

Edit `DEFAULT_STANDARDS` in `scripts/validate_sepolia.js`, or override at
runtime without editing the file:

```bash
VALIDATE_STANDARDS="ERC-1056,CVIN-Combined" \
  npx hardhat run scripts/validate_sepolia.js --network sepolia
```

Only the standards registered in the `STANDARDS` map are available. Add a new
`validate<Standard>` runner (mirroring `scripts/benchmark_gas.js`) and register
it there to cover more.
