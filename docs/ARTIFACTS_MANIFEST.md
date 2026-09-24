# Artifacts Manifest

Per-source provenance **dossiers** — one self-contained HTML page per source /
material — for the thesis Source Register (`SOURCES.md`). Each is a theme-aware,
self-contained page (no external assets, no secrets) that states what a source is,
where it is used, its provenance/attribution, and — where relevant — the measured
result that confirms the associated hypothesis.

**Publishing status.** Artifacts are kept as **local committed HTML files** under
`docs/artifacts/` (open them in a browser to view; they travel in the git bundle).
External publishing to claude.ai is **available on request** — say the word and I
will publish any/all and record their URLs here. Until then this manifest tracks
local files only.

**Template.** `docs/artifacts/erc-1056.html` is the reference template; every other
dossier follows its structure and token palette (archival cool neutrals + one
indigo accent; system + monospace type; dual light/dark themes).

## Production waves
- **Wave A — standards the thesis evaluates:** ERC-721/725/725xy/735/1056/1155/4337,
  LSP8, CVIN-Combined; EIP-191, EIP-155; W3C DID Core v1.0, W3C VC DM v2.0; MOBI VID I,
  MOBI VID II; IEEE 1609.2, SAE J2735.
- **Wave B — measured-data artifacts:** gas benchmark, MOBI backends, security
  matrices, V2V latency, W3C compliance.
- **Wave C — tools / prior work:** Hardhat, OpenZeppelin, ethers, SUMO, web3,
  eth-account, coincurve, cryptography; CVIN-ID-SCs; repo/template URLs.
- **Wave D — genealogy nodes:** the researcher's key inputs/decisions — **covered by
  `PROVENANCE.md`; per-node artifacts optional** (not produced as standalone HTML).

## Register

**Wave A — complete (17 dossiers).** All local HTML in `docs/artifacts/`; secret-free;
style byte-verbatim with the template; grounded in `SOURCES.md` + committed measured data.

| # | Source | File | Ext URL |
|---|---|---|---|
| 1 | ERC-1056 — Lightweight Identity (did:ethr) | `erc-1056.html` | — |
| 2 | ERC-721 — NFT vehicle identity | `erc-721.html` | — |
| 3 | ERC-725 — proxy-account identity | `erc-725.html` | — |
| 4 | ERC-725xy — full X+Y smart account | `erc-725xy.html` | — |
| 5 | ERC-735 — on-chain claim holder | `erc-735.html` | — |
| 6 | ERC-1155 — soulbound credentials | `erc-1155.html` | — |
| 7 | ERC-4337 — account abstraction (min. repr.) | `erc-4337.html` | — |
| 8 | LSP8 — identifiable digital asset (min. repr.) | `lsp8.html` | — |
| 9 | CVIN-Combined — the researcher's hybrid | `cvin-combined.html` | — |
| 10 | EIP-191 — signed data standard | `eip-191.html` | — |
| 11 | EIP-155 — replay protection / chainId | `eip-155.html` | — |
| 12 | W3C DID Core v1.0 | `w3c-did-core.html` | — |
| 13 | W3C VC Data Model v2.0 | `w3c-vc-dm.html` | — |
| 14 | MOBI VID I — birth certificate | `mobi-vid-i.html` | — |
| 15 | MOBI VID II — lifecycle events | `mobi-vid-ii.html` | — |
| 16 | IEEE 1609.2 — V2X security (PKI baseline) | `ieee-1609-2.html` | — |
| 17 | SAE J2735 — V2X message set | `sae-j2735.html` | — |

**Wave B — complete (5 dossiers).** Measured-result dossiers (eyebrow _Source Register ·
Measured Result_), one per Chapter-5 dataset; every number grounded in the committed JSON
under `4_comparison-framework/results/`, `…/security-analysis/results/`, and
`cv2x-testbed/sumo/results/`; each carries its honesty caveat (V2V §4.4 crypto-only scope;
W3C §4.6 self-assessment; security §4.7 informal adversary model).

| # | Source | File | Ext URL |
|---|---|---|---|
| 18 | Gas benchmark — 9-standard cost register (H1/H5) | `result-gas-benchmark.html` | — |
| 19 | MOBI VID cross-backend sweep (H4) | `result-mobi-backends.html` | — |
| 20 | Security — two-lens adversarial register (H5) | `result-security.html` | — |
| 21 | V2V latency — credential verification, N=30 (H3) | `result-v2v-latency.html` | — |
| 22 | W3C compliance — DID + VC conformance (H2) | `result-w3c-compliance.html` | — |

**Wave C — complete (7 dossiers).** Toolchain dossiers (eyebrow _Source Register ·
Toolchain_) and one prior-work dossier (_· Prior Work_); versions from `SOURCES.md` §4/§5.

| # | Source | File | Ext URL |
|---|---|---|---|
| 23 | Hardhat — Solidity build & gas harness | `hardhat.html` | — |
| 24 | OpenZeppelin Contracts — audited ERC base | `openzeppelin.html` | — |
| 25 | ethers.js — contract interaction (v6) | `ethers.html` | — |
| 26 | SUMO — V2V traffic simulation | `sumo.html` | — |
| 27 | cryptography — AES-256-GCM VIN cipher & HKDF | `cryptography.html` | — |
| 28 | coincurve — native secp256k1 | `coincurve.html` | — |
| 29 | CVIN-ID-SCs — prior smart-contract groundwork | `cvin-id-scs.html` | — |

_Wave C libraries **web3.py** and **eth-account / eth-keys** and the **repo / thesis-template
URLs** remain register entries in `SOURCES.md` §4/§5; standalone dossiers for them are optional._

**Waves B + C complete (12 new dossiers, 29 total).** All local HTML in `docs/artifacts/`;
secret-free; `<style>` block and footer **byte-verbatim** with the `erc-1056.html` template;
dual light/dark themes; every figure grounded in committed `SOURCES.md` sources + measured
JSON. **Wave D** is covered by `PROVENANCE.md` — per-node genealogy artifacts are optional
and not produced.

_Ext URL stays "—" until external publishing is requested._
