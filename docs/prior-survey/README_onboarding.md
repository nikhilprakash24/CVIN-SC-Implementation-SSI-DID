<!-- Source: branch origin/sandbox-onboarding (tip 96bb269), path README.md, last changed in commit b5bd0bc, blob f56c111. Imported 2026-10-09 as provenance; not maintained. -->
# CVIN-ID/TEST — Connected-Vehicle Identity Standards Testbed

> **Status: pre-sandbox raw material under gated onboarding** (WO-S0 complete · Provisional) — this repo is a *survey* of three blockchain-identity standards for connected vehicles, assembled from canonical upstream reference implementations. It is **not a built CVIN system**. The onboarding pass that characterises, triages, and consolidates it into `cvin-sandbox-v1.x` is in progress; see [Onboarding artifacts](#onboarding-artifacts--methodology).

## What this repo is

**CVIN** (≈ *Connected Vehicle Information Network*) explores giving each vehicle a decentralized, on-chain identity — a DID-based identifier bound to its VIN via verifiable credentials, so that C-V2X message receivers can verify a vehicle's claims (VIN, type-approval, authority attestations) against a registry instead of a centralized PKI in the hot path.

This repo is the **earliest testing ground** for that idea: three parallel implementation families, each a self-contained exploration of a candidate identity anchor:

| Track | Standard family | Identity model | Maps to |
|---|---|---|---|
| **I** — `CVIN-Implementation-I-ERC725-735` | ERC-725 / ERC-735 | One smart-contract account per identity; keys-by-purpose + on-chain claims | **SP-2** anchor & claims pattern |
| **II** — `CVIN-Implementation-II-ERC1056` | ERC-1056 / `did:ethr` | One shared lightweight registry; gas-free identity creation, key rotation, delegates | **SP-1** control |
| **III** — `CVIN-Implementation-III-LSP0` | LUKSO LSP0/LSP2/LSP3 | Universal-Profile-style account (modern ERC-725 descendant) | Frontier branch (parked) |

## Repo map (as-found state, verified at WO-S0)

| Path | What it actually is | Build state |
|---|---|---|
| `…I-ERC725-735/Build-0-…CVINModified/` | Single `CVIN_ERC725.sol` — **byte-identical to the standard ERC-725 v1 interface**; the "CVIN-modified" label is a filename prefix only, no vehicle logic | Interface only; solc 0.4.24 |
| `…I-ERC725-735/Build-II-AlternateImplementation/erc725-master/` | Origin-Protocol/Fractal ERC-725+735 demo: `KeyHolder`, `ClaimHolder`, `ClaimVerifier` + KYC-gated sample token | 2018 stack (web3 1.0-beta, Babel 6, solc 0.4.24); local `ganache` demo; native install unrecoverable as-pinned (dead `git://` dep) |
| `…I-ERC725-735/Build-III-…/ERC725-develop/implementations/` | Official **ERC725Alliance `@erc725/smart-contracts` v6** (ERC725X executor + ERC725Y store) with TS/Hardhat test suite; Node 16.19.0 pinned | **Won't compile as checked in** — `custom/`, `interfaces/`, `helpers/` dirs missing (hazard H3); restore from upstream is provenance-pinned in the plan |
| `…I-ERC725-735/Build-III-…/SmartContracts/` | Flat byte-identical duplicate of the above 13 contracts | Reference only — do not double-evaluate (H4) |
| `…II-ERC1056/…-1056Testbed-V6/cvin-v6/` | `ethr-did` quick-start: DID creation + resolution + owner lookup | Runs (creation offline); resolution targets **deprecated Goerli**; contained a leaked RPC credential (see Safety) |
| `…II-ERC1056/…-1056Testbed-V7/cvin-v7/` | Hardhat scaffold + CRA `react-dapp` — **stock `Lock.sol` sample, no ERC-1056 contract yet**; intended future SP-1 on-chain registry host | Compiles only after adding the missing `hardhat-toolbox` dep (H6); dApp non-functional (H7) |
| `…III-LSP0/` | `LSP2Utils.sol` + `LSP3Constants.sol` verbatim LUKSO snippets; `LSP0ERC725Account/` **empty** | No build system; reference snippets only |

The repo's git history is a single squashed commit; the untouched baseline is tagged **`asfound/pre-onboarding`**.

## Onboarding artifacts & methodology

The repo is being onboarded under the **CVIN-SC gated methodology** (work orders WO-S0 → WO-S4, mapped to gates pre-G0 → G2, with typed placeholder tokens `[TS-1..7]` that graduate only on captured evidence):

- **[FINDINGS.md](FINDINGS.md)** — hazards register (H1–H10), deviations, token register, compatibility table (filled at WO-S2)
- **[docs/UNDERSTANDING_TEST_REPO.md](docs/UNDERSTANDING_TEST_REPO.md)** — Provisional per-build characterisation report
- **[docs/PROGRESS_AND_CHANGE_REPORT_v1.0.md](docs/PROGRESS_AND_CHANGE_REPORT_v1.0.md)** — WO-S0 outcome + startup guide
- **[docs/NEXT_STEPS_PLAN_v1.0.md](docs/NEXT_STEPS_PLAN_v1.0.md)** — phased plan P0–P5, decision register D1–D6, risk register
- **`evidence/`** — immutable, timestamped logs backing every empirical claim (append-only; a new run is a new file)

Standing rules (binding): no interface alteration of any evaluated standard; real measurements only — no fabricated compile/test/gas numbers; deviations are logged, not smoothed; secrets referenced by location only; **offline local EVM only — no live/public testnet transactions**; evaluation compiler pinned at **solc 0.8.24, offline-vendored**.

## Safety notices

- ⚠️ **Do not run `cvin-v6/index.js`** — it makes live RPC calls to the deprecated Goerli testnet. An Infura credential was found embedded at `cvin-v6/index.js:19` (hazard H1, token [TS-4]): treat it as compromised/rotated; never commit or print credential values.
- ⚠️ **Do not `npm install` at the repo root or in Build-II** — the sub-projects are five *independent* dependency trees, several years old; the onboarding plan installs only Build-III and V7, with lifecycle scripts disabled (`--ignore-scripts`) and lockfile-strict `npm ci`.
- All chain interaction happens on a **local in-process EVM** (Hardhat Network); no accounts, keys, or funds are ever configured against a public network.

## What actually runs today

| Component | Runs? | How (see plan docs for the safe procedure) |
|---|---|---|
| Build-III compile + X/Y test suite | After provenance-pinned source restore | Node **16.19.0**, `npm ci`, `npm run build && npm test` |
| V7 Hardhat scaffold | After adding `@nomicfoundation/hardhat-toolbox@^2` | Node 18, `npx hardhat compile / test` (stock `Lock` sample only) |
| V6 DID creation (offline portion) | Yes | Node 18, `node index.js` — **resolution steps intentionally not run** |
| Build-II demo, react-dapp, LSP0 | No (out of scope this pass) | — |

## Provenance & attribution

Tracks vendor code from public upstreams, unmodified except as logged in FINDINGS: [ERC725Alliance/ERC725](https://github.com/ERC725Alliance/ERC725) (Build-III; Apache-2.0), Origin-Protocol/Fractal ERC-725/735 demo lineage (Build-II; MIT), [uport/ethr-did](https://github.com/uport-project/ethr-did) + [ethr-did-resolver](https://github.com/decentralized-identity/ethr-did-resolver) (V6 client stack), [lukso-network/lsp-smart-contracts](https://github.com/lukso-network/lsp-smart-contracts) (Track III snippets). Each sub-project retains its own upstream README and license; nothing in this repo asserts original authorship of the vendored standards code.

---

*Maintained under the CVIN-SC research programme. The onboarding pass records reality over expectation: where this README and the code diverge, [FINDINGS.md](FINDINGS.md) is the source of truth.*
