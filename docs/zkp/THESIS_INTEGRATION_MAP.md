# Thesis Integration Map for the ZKP and Agent-Wrapped Identity Work

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-15, at the close of Plan 1's execution. **Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`.
**Status:** proposals only. Nothing here edits a chapter or the claim register; every item is the author's decision,
listed with the default this session would take. Plan 2 (`PLAN_2_FULL_CIRCLE_WRITING.md`, piece W-4) develops the
chapter plan in prose.

---

## 1. What goes where

| Chapter | Section to add or extend | Take from | Pages (est.) |
|---|---|---|---|
| 1 Introduction | one paragraph on privacy as the deferred thread; one on agents as the closing thread; RQ5 if adopted | Report C §0–§1 | 1 |
| 2 Literature review | §2.x Zero-knowledge proofs and anonymous credentials (history, families, identity standards); §2.y Agent identity and prompt-injection defences | Report B §2, §10; Report C §5, §8 | 6–8 |
| 3 Methodology | pre-registration Z-E1..Z-E7 with amendments A1 (prior) and A2 (post hoc); conditions M0/M1/Sim/E; the manual-burden method (measured counts, cited rates) | Plan 1 §1.1, Amendments; Report A header | 2 |
| 4 Implementation | §4.x The ZK VIN tier (closes SC-12): ZK-VIN circuit, `ZkVinGate`; §4.y The Steward | Report A §2–§5; Report B §5, §13.9 | 5–6 |
| 5 Results | §5.x ZK costs (Table A-6); gas (Table A-4); attack results (Table A-5); verdict table A-1 | Report A §1, §4, §6, §8 | 4 |
| 6 Discussion | §6.x On-chain reality (Report B §9); SSI as a spectrum with tables C-1, C-2, C-3; the agent wrapper and its risks | Report B §9; Report C §9–§11 | 5 |
| 7 Conclusion | §7.x The closed loop (identity for machines, machines for identity); update 7.6 Future Work (anonymity set, ceremony, BBS, PLONK/Halo 2, live red team) | Report C §13; Report A §11 | 2 |
| Appendix | ZK-VIN constraints; verbose technical exposition; the demo transcript | Report B §13; `results/demo_transcript.txt` | 6 |

## 2. Proposed RQ5 and H6 (author's decision; default: adopt as an extension, not a retitle)

- **RQ5.** Can zero-knowledge proofs provide the deferred VIN privacy tier and identity-dependent knowledge checks within
  the budgets used for RQ1 and RQ4, and what does operating them safely require?
- **H6.** Zero-knowledge vehicle identity is feasible at registration and session time but not per V2V message, and its
  safe operation requires a bounded, adaptive custodian whose own trust rests on the same decentralised identity stack.
  *Measurable part:* Z-E1..Z-E7 (six PASS, Z-E6 FAIL). *Verdict if adopted:* **partly supported**: feasibility and the
  custodian's necessity are supported; the pre-registered service level of the bounded custodian was not met.

## 3. Proposed claim-register rows (not added; status would be V on acceptance)

| # | Claim | Cond. | Source | Proposed status |
|---|---|---|---|---|
| Z1 | ZK-VIN Groth16 circuit: 3,498 constraints (1,667 non-linear, 1,831 linear), 3,505 wires | — | `5_zkp-agent-identity/artifacts/circuit_info.txt` | V |
| Z2 | ZK-VIN prove median 398.6 ms (N=10, min 360.2, max 431.5); verify median 18.42 ms (N=30, min 15.45, max 26.59) | M0 | `results/zkvin_bench.json` @ `978988e` | V |
| Z3 | `ZkVinGate.admit` with on-chain Groth16 verification 301,163 gas; anchor 51,558; `verifyProof` estimate 256,038; Schnorr PoK transaction 28,775 | M1 | `results/gas_zk.json` @ `978988e` | V |
| Z4 | zkid sigma timings and exact operation counts (Table A-3) | M0 | `results/sigma_bench.json` @ `978988e` | V |
| Z5 | Unsalted SHA-256 of a VIN with only the serial unknown reversed in 3.58 s (10⁶ candidates, 279,587/s, one core) | M0 | `results/vin_bruteforce.json` @ `978988e` | V; extrapolations E |
| Z6 | Narrowing attack and defences over seeds 1–30 (Table A-5); Z-E5 PASS; Z-E6 FAIL | Sim | `results/attacks.json` @ `978988e` | V (simulation) |
| Z7 | Manual-burden inventory: counts measured; hand times and error probabilities | E | `results/manual_burden.json` @ `978988e` | counts V; times E |

## 4. Scope changes to record (author's decision; default: record)

- **SC-12** (ZK VIN tier, deferred 2026-09-25): reopened and built as a measured prototype (Report A §3–§4); the
  production gap is the setup ceremony.
- **I-09** (rank 25): first step done (tooling and measurement); kill criterion not triggered for registration and
  session time; triggered for per-message use, as the idea anticipated.
- **I-10**: partly addressed (threshold proofs); the SD-JWT/BBS hot-path measurement remains.

## 5. Open decisions, with defaults

| Decision | Default |
|---|---|
| Adopt RQ5/H6 | adopt as an extension of the existing RQs |
| Add rows Z1–Z7 to the register | add after review, as V (Z7 split V/E) |
| Where the agent argument lives | chapter 6 discussion plus chapter 7 closing, not a new chapter |
| Retitle the thesis | no |
| Treat Plan 2's series as thesis content | no; it is the narrative and structural companion, from which W-4 drives chapter edits |
