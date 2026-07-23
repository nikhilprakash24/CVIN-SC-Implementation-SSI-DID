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
- **Wave D — genealogy nodes:** the researcher's key inputs/decisions (from `PROVENANCE.md`).

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

_Ext URL stays "—" until external publishing is requested. Waves B (measured-data),
C (tools/prior-work), D (genealogy) follow in paced batches._
