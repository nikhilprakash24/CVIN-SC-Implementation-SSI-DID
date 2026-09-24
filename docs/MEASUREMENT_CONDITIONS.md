# Measurement Conditions and Claim Register

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-09-24
**Closes:** audit finding F3 (`docs/AUDIT_01_ORIGINAL_GOALS.md`)

Every quantitative claim in the thesis carries three things: a **condition
tag** (which environment produced it), a **source path** (the script and the
results file), and a **commit**. A number without all three is a *target* or
an *estimate* and is labelled as such. This file defines the tags and keeps
the register of claims found in the repository, with their status.

---

## 1. Condition tags

| Tag | Name | What it means | Use for |
|---|---|---|---|
| **M0** | In-process | Python or JS code path with **no chain access**: DID document construction from an address, signature verification, VC proof checks, cache hits. Timed with `perf_counter_ns`. | The V2V hot path (H3). Nothing here depends on a network. |
| **M1** | Hardhat local | Hardhat in-process EVM, chain id 31337, solc 0.8.24, optimizer 200 + viaIR, evm `cancun`, `allowUnlimitedContractSize`. Gas from the receipt. Latency includes the local JSON-RPC hop only. | All **gas** figures (deterministic, single run is exact). Latency here is *not* public-network latency and must not be presented as such. |
| **M2** | Public testnet | Sepolia (chain id 11155111) via an RPC provider. Latency includes network and block inclusion. | External-validity check of M1 gas (must match to the unit) and *the only* legitimate source of "resolution with blockchain lookup" latency. Not yet run on this trunk. |

Rules that follow from the tags:

- **Gas** (M1/M2) is deterministic for a fixed contract, compiler settings and
  input: report a single exact value, the compiler settings, and the commit.
  No confidence intervals.
- **Latency** (any tag) is not deterministic: report **N ≥ 30** warm
  repetitions after 3 discarded warm-ups, with **median and p95** (mean, min,
  max optional), and an environment header (CPU model, Python/Node versions,
  date, commit). Never a bare "~x ms".
- A figure produced by one tag must not be compared to a target set for
  another. The SAE J2945/1 budget constrains the **receive → verify → trust
  decision** path, which is M0; it does not constrain M2 resolution.
- Figures from the unmerged bundle lineage are cited as *"bundle lineage,
  unverified on trunk"* until re-executed here.

Current trunk results of record: `docs/figures/results_snapshot.json`
(commit `708302a`).

---

## 2. Reconciliation of the DID-resolution latency

The same quantity appears with four values in the repository. They are
different measurements, not disagreements, and only one is currently
evidenced:

| Value | Where it appears | What it actually is | Tag | Status |
|---|---|---|---|---|
| **0.009 ms cold / 0.002 ms warm** (median; p95 0.013 / 0.003) | `docs/figures/resolution_latency_M0.json`, commit `f602fdf` | Construct a DID document in-process, N=30 after 3 warm-ups, per method (`did:ethr`, `did:mobi`, `did:nft`). *Cold* = resolver cache cleared before each call; *warm* = cache hit. Intel Xeon 2.10 GHz, Python 3.11.15 | M0 | **verified** (chapter-grade) |
| 0.05 ms | CLI single run, 2026-09-24 | Same path plus CLI printing and metadata formatting, one sample | M0 | superseded by the row above |
| 0.23 ms | `QUICKSTART.md` example output | `did:mobi` example, same code path | M0 | example output, not a result |
| ~0.8 ms / "<1 ms" | `RESEARCH_THRUSTS_REPORT.md` | earlier session, different code state and hardware; no script on trunk | M0 | **superseded** |
| 50–100 ms | `README.md`, `CAPABILITIES.md`, `docs/thesis/README.md` | design-time estimate for resolution *with a blockchain RPC lookup* | M2 | **estimate / target — never measured** |

Chapter text may use the M0 figure (after an N≥30 re-run) for the hot path,
and must say "not yet measured" for M2 until a Sepolia run exists.

---

## 3. Claim register

Status key: **V** verified on trunk · **E** estimate/target (label as such) ·
**S** superseded (remove or re-measure) · **U** unsupported by trunk
evidence (rewrite) · **B** bundle lineage, unverified on trunk.

| # | Claim | Location | Tag | Source on trunk | Status |
|---|---|---|---|---|---|
| 1 | createVehicleDID 78,068 gas | `PROJECT_SUMMARY.md` §2.2 | M1 | `1_blockchain-identity` tests; `results_snapshot.json` | **V** |
| 2 | changeOwner 68,854 · addDelegate 72,219 · setAttribute 51,126 | same | M1 | same | **V** |
| 3 | ERC-721 mint 102,804 (avg) | same | M1 | `gas-report.txt` | **V** |
| 4 | W3C compliance 89.6% (DID 75 / VC 100 / SSI 100) | thesis README, summary | M0 | `w3c_compliance_checker.py` | **V** — internal, self-scored; external result is #24 |
| 24 | **External** W3C DID test suite: 328/441 (74.4%) — identifier 3/3, core properties 88/88, production 48/48, consumption 3/3, **resolution 186/299**; per resolver ethr 77/119, mobi 52/90, nft 57/90 | `docs/conformance/W3C_DID_TEST_SUITE.md` | M0 | w3c/did-test-suite @ `939b31d`, implementations generated from `DIDResolver.resolve()`; raw jest reports in `docs/conformance/reports/` | **V** — all 113 failures are resolution-metadata conformance (5 root causes, fixable); internal checker misses these categories |
| 5 | VC layer 28/28, contracts 47/47 | summary | — | pytest / hardhat | **V** |
| 6 | "ERC-1056 provides **10× gas savings over ERC-721**" | `docs/thesis/README.md` RQ1 answer | M1 | none | **U** — on the trunk the create-equivalents are 102,804 vs 78,068 = **1.32×**. The order-of-magnitude gaps in the bundle lineage are against ERC-725xy (1,704,992), not ERC-721. |
| 7 | DID creation ~45,000 gas · attribute 50,000 · delegate 55,000 | `CAPABILITIES.md` | M1 | none | **E** — design estimates; measured values in #1–2 differ (createVehicleDID also writes the VIN attribute) |
| 8 | NFT minting ~150,000 gas · transfer ~70,000 | `CAPABILITIES.md` | M1 | none | **E** — measured mint avg 102,804 |
| 9 | ERC-725 proxy creation ~350,000 gas | `CAPABILITIES.md` | M1 | none | **E** — ERC-725 has no test on the trunk |
| 10 | Resolution 50–100 ms "with blockchain lookup" | README, CAPABILITIES, thesis README | M2 | none | **E** |
| 11 | Resolution ~0.8 ms / <1 ms | `RESEARCH_THRUSTS_REPORT.md` | M0 | none | **S** |
| 12 | VC verification "5–10 ms (PKI) or 50–100 ms (blockchain)" | `CAPABILITIES.md` | M0/M2 | none | **E** — measured values are #21 (PKI 0.32 ms M0; ERC-1056 uncached 18.2 ms M1) |
| 13 | VC verify "median 7.5 ms / p95 8.9 ms (offline)" | `INVENTORY.md` | M0 | none (script not on trunk) | **S** — superseded by #21 |
| 14 | "<10 ms verification" | `README.md` | M0 | none | **E** (target from roadmap) |
| 15 | SUMO simulation "with 50 vehicles" | README, thesis README, thrusts report | — | `cv2x-testbed/sumo/` config exists; no results file | **E** — configured, not run |
| 16 | Nine standards compared | README, thesis README | M1 | 3 implemented on trunk | **B** (audit F1) |
| 17 | V2V SSI warm verify 0.165 ms [0.162, 0.168], N=30; saturation P*≈772 | bundle lineage | M0 | not on trunk | **B** |
| 18 | ERC-1056 createIdentity 52,612 · CVIN-Combined 52,178 · ERC-725xy 1,704,992 | bundle lineage | M1 | not on trunk | **B** |
| 19 | Security 43/43 attacks defended | bundle lineage | — | not on trunk | **B** |
| 20 | USD costs ("~$0.50 at 30 gwei") | `CAPABILITIES.md` | — | none | **E** — gas price and ETH price are dated; report gas units only, convert in one appendix table with the date |
| 21 | PKI vs ERC-1056 identical operations, n=50 (median / p95 ms): verify **0.321 / 0.366** PKI vs **18.158 / 23.741** ERC-1056 uncached (7 RPC calls); resolve 0.171 vs 10.058; check-revocation 0.001 vs 7.712; register 15.2 vs 16.9; issue 0.72 vs 13.5; revoke 0.02 vs 12.6 | `cv2x-testbed/results/pki_vs_erc1056.{csv,json,md}` | M0 (PKI, in-process) / M1 (ERC-1056 via local RPC) | `cv2x-testbed/scripts/experiment_pki_vs_erc1056.py`, commit `ed85dfd`+ | **V** — with the caveats in the .md: in-process PKI is a lower bound on real PKI; local RPC floor ≈2.5 ms per round trip; ERC-1056 verify measured uncached (worst case) |
| 22 | `cv2x-testbed` ERC1056Registry gas: register 54,860 · issue (attribute) 37,779 · revoke 75,044 · deploy 878,509 | same | M1 (solc 0.8.20) | same | **V** — a *different contract* from the `1_blockchain-identity` registries in #1–2; do not merge the two columns |
| 23 | Signed BSM-like message size: PKI ≈1.08–1.11 kB (carries PEM cert) vs ERC-1056 595 B (carries DID only) | same | — | same | **V** |

---

## 4. What changes in the drafts (done in the same commit as this file)

- `docs/thesis/README.md`: RQ1 answer rewritten to the measured ratio and the
  M0 figure; "SUMO with 50 vehicles" marked *configured, not run*.
- `README.md`: performance table rows marked as targets; "<10 ms
  verification" marked as target.
- `RESEARCH_THRUSTS_REPORT.md`: "~0.8 ms" and "<1 ms" replaced by the M0
  figure with its tag.
- `CAPABILITIES.md` and `INVENTORY.md`: banner added stating that their
  performance and gas figures are design-time estimates superseded by
  `docs/figures/results_snapshot.json`; the INVENTORY "measured" line
  re-labelled.

Numbers in session logs (`AUTONOMOUS_*`, `SESSION_*`) are left untouched as
historical record; nothing in a chapter may cite them.
