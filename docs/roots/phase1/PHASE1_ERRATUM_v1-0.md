# Roots Thread G-R1 · Phase 1 Erratum v1.0

**The corrections Phase 2 made to Phase 1, recorded at source so that no chapter cites a superseded Phase 1 value.**

v1.0 · 2026-10-23 · Closes PN-33 / CA-21 (R9 v0-2 §1, §6). The Phase 1 documents themselves are left unchanged, as dated records; this note is the authority wherever it and they differ.
Source of each ruling: R9 v0-1 §3.4 (X-1..X-9), confirmed in R9 v0-2. Evidence: R6 v0-2, R7 v0-2, and the repository files named.

`Progress ▓▓▓▓▓▓▓▓▓▓ 100 %`

---

## 1. The one sentence to carry

Every Phase 1 figure that depends on a **block interval Δ** (R4 PF-24, PF-25, PF-28, and R4 §3's Option A finality) describes the **designed** Besu/QBFT consortium, not anything executed. The repository's executed chain is a single automining Hardhat node (*N_v* = 1), which has no block interval and no consensus round (R7 v0-2 PF-39; `1_blockchain-identity/results/metrics/latest/meta.json`). Gas carries across chains; latency and finality do not.

## 2. The corrections

| # | Phase 1 location | Phase 1 said | Correct statement | Ruling | Evidence |
|---|---|---|---|---|---|
| X-1 | R4 PF-24, PF-25, PF-28; R4 §3 SOL-01/02 rows | Δ = 2 s as the "Besu QBFT sandbox default"; rotation window ≈ 3 s; W ≈ 3 s + σ under Option A | No executed source for Δ exists. These rows are **DESIGN**, parametrised by Δ (PAR, owned by R8 v0-2). On the executed instrument, inclusion and "finality" are effectively immediate and mean nothing about consensus | ACCEPT (KD-R7-02, absorbing KD-R6-02, KD-R7-07) | `meta.json`; R7 v0-2 PF-39 |
| X-2 | R4 SYM-22, PF-24 table | Block gas limit *G* = 30 M / 100 M | The instrument's limit is **60,000,000** (Hardhat setting). 30 M / 100 M remain valid **design scenarios**. Quote each as what it is | QUALIFY (KD-R7-01) | `meta.json`; R7 v0-2 PF-49/50 |
| X-3 | R4 SYM-23, PF-24 | Per-operation gas *g_op* 50k–180k, ESTIMATED | Use the **measured per-function gas vector**: ERC-1056 functions 32,868–76,830 gas; other standards up to 1,757,881 (ERC-735 create); quote each with its gas-charter class and register row | ACCEPT (KD-R7-03) | `docs/MEASUREMENT_CONDITIONS.md` rows #29, #34, #54; R7 v0-2 §5 |
| X-4 | R4 PF-24 fleet conclusion | Fleet write rate "two orders above any row" | At the measured gas the gap is **54×–181×** depending on *G* (100 M / 60 M / 30 M at Δ = 2 s), and creating a did:ethr identity costs **0 gas** (#47). The sized design (on-chain pseudonym anchoring) is also the one register #38 shows to be linkable, so the figure sizes a design the thesis should not recommend | QUALIFY (KD-R7-04) | R7 v0-2 PF-50; register #38, #47 |
| X-5 | R4 PF-11 | Trusted-setup failure *p_s*^*t_s* ≈ 10⁻⁶ (multi-party ceremony) | The repository's ZK-VIN setup is **single-party and marked insecure**; soundness rests on trusting one machine | ACCEPT (KD-R7-05) | register #57; R6 v0-2 BP-L1.2-04 |
| X-6 | R4 PF-15, PF-28 (σ) | Cache staleness σ is a time, illustratively 5 s | The repository bounds staleness **in messages** (at most *k_f* − 1), which becomes a time only if the sender rate is known; there is **no TTL** on cached state. The thesis states both units and adds a TTL rule | ACCEPT (KD-R7-06) | register #32, #46; `cv2x-testbed/identity/freshness.py`; R7 v0-2 §6; R6 v0-2 BP-L7.2-03 |
| X-7 | R2 §2 SOL-01; R2 HANDOFF | SOL-01 = "Hardhat + Foundry harness with a single-validator Besu QBFT node" | SOL-01 is a **Hardhat** harness. No Foundry and no Besu/QBFT configuration exists in the tree; Besu appears only in `cv2x-testbed/V2_DESIGN.md` as a design note. Lineage: the Besu sandbox described in earlier project notes (`cvin-sandbox-v1.x`) was not found on any remote | ACCEPT (KD-R6-01, absorbing KD-R6-05) | repository tree; R6 v0-2 §2.L3 |
| X-8 | R3, R1 §10.1 T-I05 usage; thesis drafts | "IEEE 1609.2 PKI baseline" | Name it **"X.509 P-256 pseudonym-certificate baseline (1609.2-style)"**: certificates are X.509 carried in JSON, with no 1609.2 encodings | ACCEPT (KD-R6-03) | `cv2x-testbed/identity/` PKI provider; R6 v0-2 §2.L7 |
| X-9 | R3 Part IV flows (implicit) | SSI safety-message signature implied as EIP-191 / keccak | The ERC-1056 testbed provider signs messages with **ECDSA secp256k1 over SHA-256** (Python `cryptography`), not EIP-191; the on-chain and message signature paths differ | ACCEPT (KD-R6-04, clarification) | `cv2x-testbed/identity/erc1056_provider.py`; R6 v0-2 §6 |

Phase 1 values confirmed unchanged by recomputation (no correction): R4 PF-02, PF-04, PF-16, PF-19 (CEV-R7-01/02), and R4 PF-31's order of magnitude for reads (consistent with register #21, #31; R4 missed that read cost grows with identity history).

## 3. What a chapter must do

Any chapter citing R4 PF-24, PF-25 or PF-28, or R2 SOL-01, cites this erratum alongside, uses the corrected statement above, and labels consensus-dependent figures **DESIGN**. This is thesis-blocking for those citations (R9 v0-2 CA-21).
