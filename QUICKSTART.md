# Quickstart Guide - 5 Minutes to Running

**Get the thesis implementation up and running, and verify it, in about 5 minutes.**

This guide targets the *current* repository (v0.8.0 tagged, `0.9.0-dev` in
`VERSION`). Everything below has been run against the repo as written; the
outputs shown are real.

---

## Time Estimate

- **Prerequisites**: 2 minutes (if not already installed)
- **Install**: 1 minute
- **Verify**: 2 minutes
- **Total**: ~5 minutes

---

## Prerequisites

### Required

**Node.js 18** (for the Hardhat smart-contract project):
```bash
node --version   # v18+ (developed on 18/20/22)
npm --version    # v9+
```
Install on Ubuntu/Debian if needed:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Python 3.11** (for the W3C SSI layer, MOBI VID, use cases):
```bash
python3 --version   # 3.11 recommended
pip3 --version
```

**Git**:
```bash
git --version
```

### NOT required

- **SUMO** is **not** required. The V2V testbed runs in **simulate mode**
  (built-in mobility), so no SUMO binary is needed to reproduce the results.
  A real-SUMO run is optional/future work.
- No external RPC, funded key, or paid service is needed for any of the
  verification steps below. (A public-testnet/Sepolia run is optional — see
  the end of this guide.)

---

## Installation

### Step 1: Get the repository

Clone the repository and `cd` into it. The designated origin is
`nikhilprakash24/CVIN-SC-Implementation-SSI-DID`:
```bash
git clone https://github.com/nikhilprakash24/CVIN-SC-Implementation-SSI-DID.git
cd CVIN-SC-Implementation-SSI-DID
```
(If you already have the repo, just `cd` into it.)

### Step 2: Install blockchain dependencies

```bash
cd 1_blockchain-identity
npm ci        # reproducible install from the committed package-lock.json
# or: npm install
```
This installs Hardhat, OpenZeppelin Contracts 5.0.2, and the test tooling.
The `package-lock.json` is committed, so `npm ci` gives a reproducible,
pinned install (the same versions the 217-test suite passes against).

### Step 3: Install Python dependencies

The W3C layer ships a pinned `requirements.txt`, or you can install the core
set directly:
```bash
# From the repo root:
pip3 install -r 2_w3c-ssi-layer/requirements.txt
# — or the minimal core set —
pip3 install web3 eth-account cryptography pytest coincurve
```

---

## Verify Installation

Run these from the repo root (paths are shown relative to it). All five pass
against the current repo.

### 1. Smart-contract test suite — 217 passing

```bash
cd 1_blockchain-identity
npx hardhat test
```
Expected tail:
```
=== Security matrix (attack outcomes) ===
attack	ERC-1056	ERC-721	ERC-725	ERC-735	ERC-1155	ERC-4337	LSP8	MOBI-VID-V2	CVIN-Combined
...
  217 passing (10s)
```

### 2. W3C Verifiable Credentials — 28 passing

```bash
cd ..
python3 -m pytest 2_w3c-ssi-layer/verifiable-credentials/tests/
```
Expected:
```
============================== 28 passed in 2.65s ==============================
```

### 3. MOBI VID (VID I + VID II, incl. VIN cipher) — 32 passing

```bash
cd 2_w3c-ssi-layer/mobi-vid
python3 -m pytest tests/
cd ../..
```
Expected:
```
======================== 32 passed, 1 warning in 4.76s =========================
```

### 4. Lifecycle use cases — 12/12 passing

Real cryptographic verification end-to-end (forged/replayed credentials fail;
pass/fail is computed, not hardcoded):
```bash
python3 cv2x-testbed/scripts/test_use_cases.py
```
Expected tail:
```
12/12 use cases passed

✅ All use cases passed (result computed from actual runs)
```

### 5. W3C compliance checker — 93.2%

Executable checker (CI-gated at ≥90%):
```bash
python3 cv2x-testbed/scripts/w3c_compliance_checker.py
```
Expected tail:
```
Result: 93.2% ≥ 90% — exit 0
```
The 2 documented deviations (canonical JSON vs URDNA2015, thesis-defined
cryptosuite) are counted as failures by design and reported honestly.

---

## First Example: Reproduce the gas benchmark (RQ1)

The single most representative artifact is the on-chain gas benchmark, which
deploys and exercises all nine standards plus the MOBI VID V2 profile and
writes a results file.

```bash
cd 1_blockchain-identity
npx hardhat run scripts/benchmark_gas.js
```

**Real output (createIdentity row is the headline metric):**
```
=== Gas benchmark summary (gasUsed) ===
operation	ERC-1056	ERC-721	ERC-725	ERC-725xy	ERC-735	ERC-1155	ERC-4337	LSP8	MOBI-VID-V2	CVIN-Combined
...
createIdentity	52612	542429	528647	1704992	1404108	103905	768204	149352	298923	52178
...
Results written to .../4_comparison-framework/results/gas_benchmark.json
```

Reading it: the thesis's hybrid **CVIN-Combined (52,178 gas)** and **ERC-1056
(52,612)** are ~10× cheaper to create than ERC-721/725, with a ~33× spread up
to the full **ERC-725xy** account deploy (1,704,992). This is the evidence for
H1 (minimal DID standards are ≥10× cheaper). Numbers are Hardhat-local, solc
0.8.24, OZ 5.0.2, and are deterministic (byte-identical across N=30 runs).

### Alternative first example: resolve a DID (no compile needed)

```bash
cd 2_w3c-ssi-layer/did-resolution
python3 did_resolver.py did:ethr:0x1:0x1234567890abcdef1234567890abcdef12345678
```
Real output (abridged):
```
🔍 Resolving DID: did:ethr:0x1:0x1234567890abcdef1234567890abcdef12345678

✅ Resolved did:ethr:0x1:0x1234567890abcdef1234567890abcdef12345678 in 0.07ms
✅ DID Document:
{
  "didResolutionMetadata": { "contentType": "application/did+ld+json", ... },
  "didDocument": {
    "@context": ["https://www.w3.org/ns/did/v1", ...],
    "id": "did:ethr:0x1:0x1234567890abcdef1234567890abcdef12345678",
    "verificationMethod": [{ "type": "EcdsaSecp256k1VerificationKey2019", ... }],
    "authentication": [ ... ]
  }
}
```
The resolver supports four methods: `did:ethr`, `did:nft`, `did:key`,
`did:mobi`.

---

## What You Can Do Now

All of the following are **built and tested** in the current repo:

1. **Benchmark all 9 standards on-chain** — ERC-1056, ERC-721, ERC-725,
   ERC-725xy, ERC-735, ERC-1155, ERC-4337, LSP8, and the thesis's own
   **CVIN-Combined** hybrid (`scripts/benchmark_gas.js`). MOBI VID V2 is
   measured alongside as an application profile.
   *(The ERC-4337 EntryPoint and LSP8 are deliberately minimal
   representative implementations — their gas is a lower bound.)*
2. **Issue & verify W3C Verifiable Credentials** — issuer, holder wallet, and a
   6-stage offline verifier, with 10 automotive schemas, selective disclosure
   (SD-JWT-style salted digests), a revocation registry, and EIP-191
   secp256k1 Data Integrity proofs (`2_w3c-ssi-layer/verifiable-credentials/`,
   28 tests).
3. **Resolve DIDs** across 4 methods (`2_w3c-ssi-layer/did-resolution/`).
4. **Run MOBI VID** — VID I birth certificate (W3C VC + on-chain content-hash
   anchoring) and VID II (11 lifecycle event types) with on-chain `attestEvent`
   signature verification and **AES-256-GCM VIN encryption**
   (`2_w3c-ssi-layer/mobi-vid/`, 32 tests).
5. **Run the 12 lifecycle use cases** end-to-end with real crypto
   (`cv2x-testbed/scripts/test_use_cases.py`).
6. **Reproduce the V2V latency study** — SUMO-style simulation with real ECDSA
   (PKI) and real W3C VC (SSI) verification in the message path, 10 Hz BSM:
   ```bash
   python3 cv2x-testbed/sumo/sumo_identity_integration.py --simulate
   python3 cv2x-testbed/sumo/run_v2v_stats.py     # N=30 seeded stats
   ```
   Headline: SSI warm verify ~0.165 ms median (~600× margin to the 100 ms V2V
   budget, H3). *Caveat: excludes the radio/MAC/network stack; mobility is
   simulated (no SUMO binary).*
7. **Run the security suites** — 54 Mocha attack scenarios (43/43 applicable
   cells defended), emitted as part of `npx hardhat test`.
8. **Regenerate results tables** for the thesis:
   ```bash
   python3 4_comparison-framework/performance-metrics/generate_tables.py
   ```

### Genuine next steps (not yet run)

1. **Public-testnet (Sepolia) validation** — the harness is committed
   (`1_blockchain-identity/scripts/validate_sepolia.js`, see
   `1_blockchain-identity/SEPOLIA_VALIDATION.md`), but the real run needs an
   RPC URL + a funded test key, which have not been supplied yet.
2. **Real-SUMO run** — optional; the current results use simulate mode.

---

## Troubleshooting

### `npm install` fails
```bash
npm cache clean --force
npm install
# or pin the Node version
nvm use 18 && npm install
```

### `npm` install issues
The `package-lock.json` is committed, so `npm ci` should work on a fresh
clone. If a dependency resolution error appears, fall back to `npm install`,
then `npx hardhat clean && npx hardhat compile`.

### Solidity / compiler notes
The project compiles with **solc 0.8.24** against **OpenZeppelin Contracts
5.0.2** (both pinned in `hardhat.config.js` / `package.json`). If contracts
appear stale after pulling, force a clean build:
```bash
cd 1_blockchain-identity
npx hardhat clean && npx hardhat compile
```

### `pip install` cryptography error
```
ModuleNotFoundError: No module named '_cffi_backend'
```
Install the system build deps, then reinstall:
```bash
sudo apt-get install python3-dev libffi-dev libssl-dev
pip3 install --upgrade cryptography
```

### Python import errors when running scripts
Run the commands from the repo root (as shown above) so the layer packages
resolve. A virtual environment (`python3 -m venv .venv && source .venv/bin/activate`)
is recommended to isolate the pinned dependencies.

---

## Common Tasks

### Run a subset of contract tests
```bash
cd 1_blockchain-identity
npx hardhat test --grep "ERC1056"      # match by name
REPORT_GAS=true npx hardhat test        # with gas reporting
```

### Deploy to a public testnet (optional)
```bash
# In 1_blockchain-identity/.env:
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_KEY
PRIVATE_KEY=your_funded_test_key

# Then, e.g.:
npx hardhat run scripts/validate_sepolia.js --network sepolia
```
See `1_blockchain-identity/SEPOLIA_VALIDATION.md` for the full procedure.

---

## Where to Read Next

- **`README.md`** — project overview.
- **`CHANGELOG.md`** — what changed in v0.8.0 and `0.9.0-dev`.
- **`docs/RESEARCH_THRUSTS_REPORT.md`** — research thrusts and results.
- **`docs/thesis/chapter5-results/`** — measured-results draft.
- **`1_blockchain-identity/CVIN-SSI-ARCHITECTURE.md`** — architecture.
- **`CAPABILITIES.md`** / **`INVENTORY.md`** — feature and file inventory.

---

## Success Checklist

After this quickstart you should have:

- [x] Cloned the repo and installed Node + Python dependencies
- [x] Run `npx hardhat test` — **217 passing**
- [x] Run the VC (28), MOBI VID (32), and use-case (12/12) suites
- [x] Confirmed **93.2%** W3C compliance
- [x] Reproduced the gas benchmark (and/or resolved a DID)

---

**Maintainer**: Nikhil Prakash (UBC MASc thesis)
**Questions**: nikhil.prakash1995@gmail.com
