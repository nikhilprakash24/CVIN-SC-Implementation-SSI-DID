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
| # | Source | Wave | File | External URL |
|---|---|---|---|---|
| 1 | ERC-1056 (Lightweight Identity / did:ethr) | A | `docs/artifacts/erc-1056.html` | — (local) |

_Remaining Wave A–D entries produced in paced batches; this table grows as they land._
