<!-- Source: branch origin/sandbox-onboarding (tip 96bb269), path docs/UNDERSTANDING_TEST_REPO.md, last changed in commit 0272f81, blob 1d7fb67. Imported 2026-10-09 as provenance; not maintained. -->
# Understanding Report — CVIN-ID/TEST

**Status: PROVISIONAL** (Standing Rule 9 — holds until tokens resolved) · **Pass:** WO-S0 inventory · **Branch:** `sandbox-onboarding` · **Date:** 2026-06-20

> Empirical fields (compile/test state) carry tokens [TS-1]…[TS-3] and graduate **only** from an actual offline compile/test log in WO-S1/WO-S2 — never from docs (Standing Rule 5). IMinimalSSI cells are **expectation, not verdict**, and the precise F1–F12 numbering is deferred to WO-S3 (ISetA/B/C signatures not yet loaded into this pass). The single squashed commit (`0ab45bb first commit`) yields no CVIN-specific history.

---

## Inventory matrix (verified at WO-S0)

| Build | Path (repo-relative) | Standard / layer | Toolchain as found | Build state | SP role | Disposition |
|---|---|---|---|---|---|---|
| **Build-0** | `…/Build-0-…CVINModified/SmartContracts/CVIN_ERC725.sol` | ERC-725 v1 identity interface ("CVIN-modified" — **name only**) | solc `0.4.24`, loose `.sol` | abstract interface, not deployable alone | SP-2 anchor ancestor | **Port** (→0.8.24) |
| **Build-II** | `…/Build-II-AlternateImplementation/erc725-master/` | ERC-725 + ERC-735 (KeyHolder/ClaimHolder/ClaimVerifier) + demo token | solc `0.4.24`/`^0.4.22`, web3 1.0-beta, Babel 6, ganache | runnable-in-principle demo | SP-2 claims (T-735) | **Port / Reference** |
| **Build-III** | `…/Build-III-…/ERC725-develop/implementations/` | Official `@erc725/smart-contracts` v6 (ERC725X/Y) | Hardhat + TS, solc `0.8.17`, OZ 4.9.3, **Node 16.19.0** pinned | **broken as checked in** (missing `custom/`,`interfaces/`,`helpers/`) | SP-2 modern anchor | **Graduate** (after restore) |
| **Build-III (flat)** | `…/Build-III-…/SmartContracts/` | Flat duplicate of the 13 contracts | loose `.sol` | duplicate (byte-identical) | — | **Reference-only** (don't double-count) |
| **V6** | `…/Implementation-II-ERC1056/…-V6/cvin-v6/` | ERC-1056 / `did:ethr` off-chain demo | Node ESM, ethr-did + web3 v4, **Goerli** | runs (creation); resolve needs dead Goerli | SP-1 control (off-chain) | **Reference** (rotate key, retarget) |
| **V7** | `…/Implementation-II-ERC1056/…-V7/cvin-v7/` | ERC-1056 on-chain **shell** + CRA dApp | Hardhat 2.17, solc `0.8.19` | **empty Hardhat scaffold** (`Lock.sol` sample only) | SP-1 control (on-chain host) | **Park-as-host** ([TS-6]) |
| **LSP0** | `CVIN-Implementation-III-LSP0/` | LUKSO LSP0/LSP2/LSP3 fragments | none (no build system) | barely started; `LSP0ERC725Account/` empty | out-of-path | **Park** ([TS-7]) |

---

## Per-build characterisation

### Build-0 — `CVIN_ERC725.sol`
- **Standard & layer:** ERC-725 v1 identity interface (key-purpose constants MANAGEMENT/ACTION/CLAIM_SIGNER/ENCRYPTION = 1–4; `getKey`/`addKey`/`execute`/`approve` signatures; abstract).
- **Toolchain as found:** solc `0.4.24` fixed; no package manager, no tests.
- **Compile state (verified):** native — n/a (abstract, no harness). @0.8.24 offline — **[TS-3]** (expect a mechanical 0.4→0.8 port: constructor syntax, explicit visibility, `constant`→`view`, SPDX, storage-array returns).
- **Test state (verified):** none exist.
- **IMinimalSSI (expectation):** provides key-purpose + execute scaffolding → **Set A (agent-proxy/execute) native at interface level**; claims (Set B) **absent here** (lives in ERC-735); `createPresentation` **expected absent**. *Pattern-level; F1–F12 numbering → WO-S3.*
- **Solution-path role:** SP-2 anchor ancestor; **T-725** (key purposes, last-management-key guard, deactivation).
- **Deviations & risks:** "CVIN-modified" is a filename prefix only — byte-identical to standard ERC-725; no VIN/vehicle logic (see FINDINGS §B).
- **Recommended disposition:** **Port** to 0.8.24 as the historical key-purpose reference; do not treat as bespoke CVIN work.

### Build-II — `erc725-master` (Origin-Protocol / Fractal)
- **Standard & layer:** ERC-725 (keys) + ERC-735 (claims) with concrete `KeyHolder`, `ClaimHolder`, `ClaimVerifier` (ecrecover claim validation) + sample KYC-gated token/crowdsale; web3 demo (`src/main.js`) runs an issue-claim → add-claim → buy flow.
- **Toolchain as found:** solc `0.4.24` (ClaimHolder `^0.4.22`), web3 `^1.0.0-beta.34`, Babel 6, `openzeppelin-solidity ^1.10`, ganache; runs against `localhost:8545`.
- **Compile state (verified):** native — **[TS-2/related]** (2018 stack; fragile on modern Node). @0.8.24 — **[TS-2]** (expect non-trivial port).
- **Test state (verified):** no automated suite (`main.js` scenario only; carries FIXME/XXX).
- **IMinimalSSI (expectation):** ERC-735 claims → `issueCredential`/`verifyCredential`/`revokeCredential` **native**; key purposes → Set A **native**; `createPresentation` **expected absent**.
- **Solution-path role:** SP-2 **claims-as-credentials** pattern; **T-735** (issuer binding, revocation symmetry, holder-removal).
- **Deviations & risks:** ancient toolchain; unmodified upstream (no CVIN changes); `localhost:8545` only.
- **Recommended disposition:** **Port/Reference** — the canonical ERC-735 claims pattern source for SP-2.

### Build-III — `ERC725-develop/implementations`
- **Standard & layer:** Official `@erc725/smart-contracts` v6 — ERC725X (generic executor: CALL/CREATE/CREATE2/STATICCALL/DELEGATECALL + batch) and ERC725Y (`bytes32→bytes` store), Core/Init/InitAbstract variants; full TS Hardhat behaviour suite.
- **Toolchain as found:** Hardhat `^2.13.1` + hardhat-toolbox `^2.0.2` (ethers v5, typechain), solc `0.8.17`, OZ `^4.9.3`, `.tool-versions` → **Node 16.19.0**.
- **Compile state (verified):** native — **[TS-1]**; **expected ❌ as checked in** — every core contract imports `./custom/OwnableUnset.sol`, `./interfaces/IERC725X.sol`, `./interfaces/IERC725Y.sol`, and config references `contracts/helpers/`, but those dirs are **absent** (13 flat `.sol` only). @0.8.24 — **[TS-2]** (after restore).
- **Test state (verified):** **[TS-1]** — `.ts` tests import generated typechain `../types` (produced only after a successful compile); cannot run until imports resolve.
- **IMinimalSSI (expectation):** `execute()` → ACTION key → agent proxy → **Set A native**; Y store → DID-doc state → **Set A data native**; claims (Set B) **absent** (ERC725Y is a generic store, not ERC-735); `createPresentation` **expected absent**.
- **Solution-path role:** **SP-2 modern anchor**; informs **T-725**.
- **Deviations & risks:** missing-source gap (H3); flat `SmartContracts/` duplicate (H4 — evaluate one).
- **Recommended disposition:** **Graduate** as canonical SP-2 X/Y anchor **once missing sources are restored** from upstream `ERC725Alliance/ERC725` at the matching v6 tag ([TS-5]).

### V6 — `cvin-v6` (ERC-1056 off-chain)
- **Standard & layer:** `did:ethr` DID creation + resolution + owner lookup against the shared EthereumDIDRegistry (does **not** deploy/write the registry).
- **Toolchain as found:** Node ESM (`type:module`), `ethr-did`/`ethr-did-resolver`/`did-resolver`/`web3 v4`; targets **Goerli**.
- **Compile state (verified):** n/a (off-chain JS). **Runs:** keypair/DID creation offline; `resolve()`/`lookupOwner()` need live Goerli (dead).
- **IMinimalSSI (expectation):** registry-based DID → identifier + key rotation (`changeOwner`) + delegates/attributes → **Set A (identity/keys) native, gas-minimal**; VC issuance via did-jwt **partial/native off-chain**; `createPresentation` — **possible off-chain** (the one anchor where presentations may not be structurally absent — flag for WO-S3).
- **Solution-path role:** **SP-1 control** (off-chain resolution side).
- **Deviations & risks:** **leaked Infura key** (H1/[TS-4]) — location only; **deprecated Goerli** (H2); verbatim ethr-did quick-start (no CVIN logic).
- **Recommended disposition:** **Reference** — keep as SP-1 off-chain control; operator rotates key; retarget to Sepolia/local fork later (out of scope this pass).

### V7 — `cvin-v7` (ERC-1056 on-chain shell + react-dapp)
- **Standard & layer:** intended SP-1 on-chain ERC-1056 registry host; currently the stock Hardhat sample (`Lock.sol`) + CRA frontend.
- **Toolchain as found:** Hardhat `2.17`, solc `0.8.19`; **config/tests require `@nomicfoundation/hardhat-toolbox` (absent from `package.json`)**; `deploy.js` ethers-v6 syntax vs ethers-v5 pin (H6).
- **Compile state (verified):** **[TS-1]** — `npm install` then `hardhat compile` **fails** until toolbox added; then compiles only the `Lock` sample.
- **IMinimalSSI (expectation):** none yet (no DID-registry contract); **to be implemented later** under WO-1 ([TS-6]).
- **Solution-path role:** **SP-1 control (on-chain host)** — empty today.
- **Deviations & risks:** empty shell (H5); plugin/version mismatch (H6); non-functional dApp (H7).
- **Recommended disposition:** **Park-as-host** — confirm-empty this pass; scope the ERC-1056 registry build for a later WO ([TS-6]).

### LSP0 — `CVIN-Implementation-III-LSP0`
- **Standard & layer:** LUKSO fragments — `LSP2Utils.sol` (LSP2 data-key library), `LSP3Constants.sol` (profile-metadata constants); `LSP0ERC725Account/` **empty**.
- **Toolchain as found:** none (no package.json/config/tests).
- **Compile state (verified):** n/a — `LSP2Utils.sol` imports uninstalled `@erc725/smart-contracts` (won't compile standalone).
- **Solution-path role:** out-of-path frontier branch.
- **Recommended disposition:** **Park** with a tracked follow-up ([TS-7]).

---

## Coverage Note (Provisional)

This repo **strengthens both solution paths**: SP-2 (ERC-725/735 composite) via Build-III's modern X/Y anchor + the Build-0/Build-II key-and-claims patterns, and SP-1 (ERC-1056 lightweight DID) via the V6 off-chain control and the V7 on-chain host shell. **Gaps remaining:** no unified `IMinimalSSI` interface set is implemented against any contract yet (canonical WO-1/WO-3); no on-chain ERC-1056 registry exists (V7 empty); Build-III cannot build until missing sources are restored; LSP0 is unbuilt. **Nothing graduates to Final in this pass.**
