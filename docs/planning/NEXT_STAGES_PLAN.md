# Next Stages Plan — v0.7.0 → Defense-Ready

**Status**: Strategic plan written against the verified on-disk state at
git HEAD `be32c6e` (tag `v0.7.0`, "Integration & Verification Milestone").
**Date**: 2026-07-15
**Verified this session** (not asserted from memory):
- `npx hardhat test` in `1_blockchain-identity/` → **201 passing, 0 failing** (includes the 54-scenario security suite; regenerates `attack_results.json`)
- `pytest 2_w3c-ssi-layer/verifiable-credentials/tests/` → **28 passing**
- `pytest 2_w3c-ssi-layer/mobi-vid/tests/` → **21 passing** (on-chain, self-managed Hardhat node)
- Tag `v0.7.0` and HEAD `be32c6e` confirmed present on the **`github`** remote (`nikhilprakash-cvin/2_miniature-waffle-CV2X-Testbed-MOBI-VID`); the designated **`origin`** remote (`nikhilprakash24/CVIN-SC-Implementation-SSI-DID`) is stale at `c444e99` — its push endpoint has returned 403 all session. See Risk R-A.

Supersedes any earlier planning pass that analyzed the stale pre-integration clone.

---

## 1. Where We Actually Are (per thrust, measured numbers only)

### Thrust 1 — Comparative performance (RQ1, H1)
**Substantially done; statistically thin.** `4_comparison-framework/results/gas_benchmark.json` + `gas_comparison.csv` hold exact `receipt.gasUsed` for an identical operation set (create / update / delegate-or-claim / revoke / transfer) across nine implementations. Identity creation spans **27×**: 52,178 gas (CVIN-Combined) to 1,404,108 (ERC-735); ERC-1056 at 52,612 vs ERC-721 at 542,429 is a measured **10.3×** gap, which **supports H1** ("≥10× cheaper"). The 4337 indirection tax is isolated: `setAttribute` 49,366 direct vs 96,228 through the EntryPoint = **46,862 gas overhead per op**. Two honest caveats: (a) every cell is a **single transaction** (`txCount: 1` throughout the JSON) — gas is deterministic on the EVM, but that determinism is currently asserted, not demonstrated; (b) the benchmark's ninth column is **MOBI-VID-V2, not ERC-725xy** — see §2 and Decision D1. Storage-overhead and throughput sub-metrics named in the RQ are unmeasured.

### Thrust 2 — W3C compliance (RQ3, H2)
**Done and defensible.** `cv2x-testbed/scripts/w3c_compliance_checker.py` executes 44 real checks (including negative/attack checks) and measures **93.2%** aggregate (DID Core 13/15 = 93.3%; VC DM v2.0 27/29 = 93.1%), CI-gated at ≥90%. The two failures are *documented deliberate deviations* (sorted-key JSON canonicalization instead of URDNA2015; thesis-defined `eip191-secp256k1-recovery-2024` cryptosuite) — counted as failures, not hidden. **H2 supported.** Residual softness: the checklist is self-derived (risk R4 in `docs/RESEARCH_THRUSTS_REPORT.md`).

### Thrust 3 — Real-time V2V viability (RQ4, H3)
**Crypto-cost question answered; network stack explicitly out of scope.** `cv2x-testbed/sumo/results/v2v_latency.json` (50 vehicles, 10 Hz, real ECDSA/VC crypto, injected-attack controls): SSI **warm-verify p95 0.27 ms** (n=18,796), cold-verify p95 0.63 ms (n=203), sign p95 0.36 ms — vs the ~100 ms V2V budget, ~370× headroom; PKI baseline warm p95 0.14 ms. All 3 injected attacks (tampered SSI/PKI BSM, uncredentialed sender) were the only verification failures — no false positives/negatives across 27,752 verifications. **H3 supported** *as scoped* (off-chain verification of pre-issued credentials, no chain read at message time). Honest limits, already in Ch5 §5.8: `mode: "simulate"` (no SUMO binary exercised), in-process delivery (no radio/MAC/channel), single simulation run.

### Thrust 4 — MOBI VID alignment (RQ, H4)
**Implemented on one backend; the cross-backend sweep is open.** VID I birth certificates + all 11 VID II lifecycle event types run as W3C VCs with keccak256 content-hash anchoring against `MOBIVIDRegistryV2.sol` — 21 on-chain tests green; measured gas: V1 birth 283,895 / V2 `recordLifecycleEvent` ~292.5k / `attestEvent` 188,480. **H4 "partially demonstrated"** (Ch5 §5.7's own verdict): realizability shown, but the hypothesis is about *which backend fits best*, and only the MOBI registry backend is measured. Demo-grade residue: VIN "encryption" is an **XOR keystream** (README line 96: "NOT production crypto (no AEAD)"), and `attestEvent` stores a 65-byte attestation signature that is **never verified on-chain** (no `ecrecover`; also accepts `bytes32(0)` event ids) — recorded as a finding in Ch5 §5.6(5), currently a known vulnerability we ship.

### Thrust 5 — Security trade-offs (RQ2, H5)
**Two-lens analysis complete and CI-enforced.** Lens 1: 54 Mocha adversarial scenarios (`1_blockchain-identity/test/security/securityScenarios.test.js`), **43/43 applicable attack cells DEFENDED** with differential controls, re-verified green this session. Lens 2: `security-analysis/results/security_matrix.json` grades Sybil economics, recovery, and PII leakage — plaintext VIN on-chain proven for ERC-721/735/1155/LSP8; only ERC-4337 has genuine key recovery (guardian `recoverOwner`, executed); ERC-1155's soulbound `_update` uniquely blocks identity theft-by-transfer. **H5 supported**: no standard dominates; CVIN-Combined sits on the cost/capability frontier (identity ops at ERC-1056 cost — 52,178 vs 52,612 create — plus on-chain claims at 289,923), *and* the matrix honestly shows its cost: Sybil ✗, recovery ✗.

### Genuinely-done vs representative/demo-grade (the honesty ledger)
| Component | Grade | Evidence |
|---|---|---|
| ERC-1056, ERC-721, ERC-725, ERC-735, ERC-1155, CVIN-Combined contracts | Full implementations, tested | 201-test suite |
| ERC-4337 `CVINMinimalEntryPoint` | **Representative research harness** — header enumerates omissions (no bundler/paymaster/aggregation/deposits/initCode) | contract header |
| LSP8 `CVINVehicleLSP8` | **Representative** — LSP8-conformant signatures, no LUKSO package, omissions in header | contract header |
| **ERC-725xy** | **README only — no contract, no tests, not in the benchmark** (`1_blockchain-identity/ERC725xy/` contains `README.md` + an empty-of-code `contracts_all/README.md`; the README's install instructions point at a *different repo*, CVIN-ID-SCs, with Truffle/Ganache) | on-disk inspection |
| MOBI VIN encryption | Demo-grade (XOR keystream) | `mobi-vid/README.md` |
| MOBI `attestEvent` | Signature stored, not verified on-chain | Ch5 §5.6(5) |
| Gas numbers | Real, but n=1 per cell | `gas_benchmark.json` |
| V2V latency | Real crypto, simulated mobility, single run | `v2v_latency.json` |

### Hypothesis scoreboard
| H | Verdict today | Gap to "clean" |
|---|---|---|
| H1 | **Supported** (10.3× measured) | n≥30 determinism demonstration; ERC-725xy cell |
| H2 | **Supported** (93.2% measured) | external-checklist cross-validation (nice-to-have) |
| H3 | **Supported as scoped** (0.27 ms p95) | multi-run CIs; explicit network-budget framing; SUMO decision |
| H4 | **Partial** | cross-backend sweep (≥3 backends) |
| H5 | **Supported** (frontier measured) | none blocking; optional CVIN-Combined issuer-gating variant |

Overall: **~70% complete** (CHANGELOG's own estimate, and it survives audit).

---

## 2. The Gap to a Defensible Thesis

What a MASc examiner will attack, ranked. Items 1–5 are **thesis-critical**; 6–8 are **strengthening**.

1. **"You claim nine standards; show me the ninth."** (Thesis-critical, and currently the sharpest factual exposure.) The title/RQ set names ERC-725xy, but the repo has no ERC-725xy contract, no tests, and the "9/9 benchmarked" gas table fills the ninth slot with MOBI-VID-V2. This is not a threats-to-validity footnote — it is a claims-inventory mismatch an examiner can find in five minutes. Must be resolved by Decision D1 (build minimal-but-real, or re-scope to 8+MOBI honestly) before any external presentation of the gas table.

2. **"Single-run measurements with no dispersion."** (Thesis-critical, cheap to fix.) Every gas cell is `txCount: 1`; the V2V numbers, while built from 18,796+ per-message samples, come from **one** simulation run/seed. An examiner asks: run-to-run variance? seed sensitivity? For gas, EVM determinism means N=30 runs should produce zero variance — *demonstrating* that is itself a nice methodological point. For latency, N≥30 independent seeded runs with per-run medians/p95 and 95% CIs across runs is the standard expected of empirical systems work (this is the repo's own risk R2: "report medians + p95" — half done).

3. **"Everything ran on a local Hardhat node."** (Thesis-critical; documented as risk R3 and Ch5 §5.8 bullet 1.) The defense that gas is opcode-deterministic is correct but must be *shown*, not argued: one Sepolia run per standard per operation, with committed tx hashes matching local gasUsed, converts the whole RQ1 chapter from "simulated" to "publicly verifiable". No Sepolia artifacts exist yet.

4. **"Your V2V latency excludes the network."** (Thesis-critical to *frame*, not to fix.) Ch5 §5.4 already scopes the claim to cryptographic cost, and H3 was deliberately formulated about off-chain verification. The gap is rhetorical robustness: the thesis needs (a) a literature-anchored budget decomposition (C-V2X PC5 / DSRC latency figures from published measurements) showing crypto at 0.27 ms is negligible against the stack, and (b) a clear decision record on real-SUMO (Decision D2). An examiner accepts a scoped claim; they punish a scoped claim presented as an unscoped one.

5. **"You found a vulnerability in your own artifact and shipped it."** (Thesis-critical, small.) MOBI `attestEvent` not verifying its stored signature is currently a *finding*; leaving it unfixed at defense invites "why didn't you fix a 10-line bug?" Fix it, re-measure the gas delta (ecrecover ≈ +3–6k gas on the 188,480 baseline), and turn the finding into a before/after result — strictly better narrative.

6. **Representative contracts (ERC-4337 EntryPoint, LSP8).** (Strengthening.) Already documented in-header and in §5.8 as gas lower bounds. Sufficient defense: quantify the direction of the bound (cite canonical EntryPoint deployment gas / LUKSO LSP8 gas from public deployments) in one paragraph. Do not rebuild them.

7. **Demo-grade VIN crypto.** (Strengthening, tiny.) Ch5 §5.8 correctly claims the *architecture* (hash-on-chain), not the cipher. Still, swapping XOR for AES-GCM via the already-imported `cryptography` package is ~an afternoon and deletes the caveat entirely.

8. **H4 cross-backend sweep + storage/throughput metrics.** (Strengthening.) H4 stays "partial" without parameterizing MOBI VID events over ≥3 backends; Thrust 1's RQ mentions storage overhead and throughput that were never measured. Both are contained, well-scoped experiments on existing infrastructure.

---

## 3. Sequenced Work Plan

Ordering principle: **defense-readiness per unit effort, unblocking first**. Stage 0.8 removes the two attacks an examiner wins outright (missing ninth standard; n=1 stats) plus the durability risk; 0.9 buys external validity; 1.0-rc completes the comparison; 1.0 is freeze + packaging.

### Stage 0.8 — "Rigor & Ground-Truth Hardening" (target: ~3 weeks)
**Objective**: every headline number gains dispersion statistics; the nine-standard claim becomes literally true; the shipped vulnerability is fixed; the work is durable.

| # | Item | Closes | Effort | Notes |
|---|---|---|---|---|
| 0.8.0 | **Durability**: `git bundle create` full backup off-container; verify `github` remote has HEAD+tags after every session; resolve or replace the 403ing `origin` (see R-A). Also: delete/ignore the stray untracked `CVIN-ID-SCs/` build-junk dir at repo root; refresh the stale (June 21) `INVENTORY.md`. | R-A | **S** | Do first, ~1 hour |
| 0.8.1 | **ERC-725xy resolution** per Decision D1 (recommended: build). Minimal-but-real combined ERC725X (`execute`) + ERC725Y (`setData`/`getData`) vehicle account — the `@erc725/smart-contracts` package is already vendored in `node_modules`. Tests (~15–20), add to `benchmark_gas.js` operation set, add to security suite (both lenses), regenerate all tables. | Gap #1; H1/H5 completeness | **M** | 2–4 days; blocks table freeze |
| 0.8.2 | **Gas benchmark N≥30**: loop `benchmark_gas.js` over 30 fresh-state deployments; emit per-cell `{median, min, max, n}`; expected zero variance → state that as a methodological result; if any cell varies (state-dependent SSTORE pricing), investigate and document. | Gap #2 (gas half) | **S/M** | Independent of 0.8.1 but rerun after it |
| 0.8.3 | **V2V latency N≥30 seeded runs**: wrap `sumo_identity_integration.py --simulate` in a runner varying RNG seed; aggregate per-run medians/p95 into `v2v_latency_agg.json` with 95% CIs; update Ch5 §5.4 table to "median of run-medians [CI]". | Gap #2 (latency half); R2 | **M** | ~30 × 6.5 s wall-clock — trivially cheap to run |
| 0.8.4 | **MOBI `attestEvent` fix**: on-chain `ecrecover` of the attestation signature against the attester role-holder; revert on `bytes32(0)` event id; new adversarial tests (forged attestation reverts); re-measure gas delta vs 188,480; update `security_matrix.json` cell and Ch5 §5.6(5) to before/after. | Gap #5 | **S** | ~1 day |
| 0.8.5 | **AES-GCM VIN encryption** replacing the XOR keystream (off-chain layer only; on-chain hash unchanged). | Gap #7 | **S** | ~½ day |

**Dependencies**: 0.8.0 first; 0.8.1 before final table regeneration; rest parallel.
**Definition of done**: `gas_benchmark.json` cells carry `n ≥ 30` metadata including an ERC-725xy row; `v2v_latency_agg.json` committed with CIs; forged-attestation test green; all suites still green (expect ~220+ Hardhat tests); backup bundle exists outside the container; tag `v0.8.0`.

### Stage 0.9 — "External Validity" (target: ~2–3 weeks)
**Objective**: retire the local-chain and simulated-mobility threats to validity, or convert them into explicitly-scoped, literature-anchored claims.

| # | Item | Closes | Effort | Notes |
|---|---|---|---|---|
| 0.9.1 | **Sepolia validation run** per Decision D3: deploy all 9 (+MOBI registry) and execute the full operation set once per standard; commit `sepolia_validation.json` with tx hashes and gasUsed; assert equality with local medians in a CI-checkable script; note any divergence (there should be none). | Gap #3; R3; Ch5 §5.8 bullet 1 | **M** | Faucet logistics is the long pole; needs an RPC key + funded key — the only stage item requiring external accounts |
| 0.9.2 | **Real-SUMO decision executed** per Decision D2. If GO: `apt install sumo` + run the existing TraCI path, one comparison run showing crypto latencies are mobility-invariant. If NO-GO: commit a one-page decision record + strengthen §5.8 wording. | Gap #4 (part) | **S–M** | Timebox to 3 days; the TraCI code path already exists |
| 0.9.3 | **Network-budget framing**: half-page analysis in Ch5/Ch6 decomposing the 100 ms budget using published C-V2X PC5 / IEEE 1609 latency measurements, situating the 0.27 ms crypto term. | Gap #4 (part) | **S** | Literature work, no code |
| 0.9.4 | **Representative-contract bounding paragraph**: cite canonical ERC-4337 EntryPoint and LUKSO LSP8 public-deployment gas to bound the underestimate direction. | Gap #6 | **S** | Prose only |

**Dependencies**: none on each other; 0.9.1 should follow 0.8.1 so Sepolia includes ERC-725xy.
**Definition of done**: tx hashes on a public explorer reproduce local gas; SUMO decision recorded either way; Ch5 §5.8 has no unaddressed bullet; tag `v0.9.0`.

### Stage 1.0-rc — "Comparison Completeness & Freeze" (target: ~3 weeks)
**Objective**: H4 moves from partial to supported (or explicitly re-scoped); Thrust 1's secondary metrics exist; results directory frozen.

| # | Item | Closes | Effort |
|---|---|---|---|
| 1.0rc.1 | **H4 backend sweep**: parameterize MOBI VID I/II issuance+anchoring over ≥3 backends (ERC-1056 events, ERC-735 claims, CVIN-Combined) reusing the existing lifecycle layer; per-backend cost/fidelity table — this is the fidelity-per-gas frontier H4 predicts. | H4 → supported | **M/L** |
| 1.0rc.2 | **Storage overhead + throughput**: bytes-on-chain per identity/credential per standard (from receipts + state reads); ops/s under Hardhat as an upper-bound note. | Thrust 1 RQ completeness | **M** |
| 1.0rc.3 | **Regenerate every LaTeX/CSV artifact from frozen data; freeze `results/`**; reproducibility runner (`make reproduce` or one script) that regenerates all numbers end-to-end; pin dependency versions. | R5 | **S/M** |
| 1.0rc.4 | Optional (Decision D4): CVIN-Combined issuer-gating flag experiment showing the Sybil cell is tunable. | H5 polish | **S** |

**Definition of done**: H4 verdict updated with data; `results/` tagged and treated read-only; one-command reproduction verified from clean clone; tag `v1.0.0-rc`.

### Stage 1.0 — "Defense-Ready" (target: ~2 weeks + writing tail)
**Objective**: no open experimental items; thesis text is the only remaining work.

- All chapters drafted (see §4), Ch5 regenerated from frozen artifacts.
- Committee package: repo access instructions, reproduction guide, data provenance table (every thesis number → file path + command).
- Dry-run defense deck of the five thrust results.
- **Definition of done**: an independent person can clone, run three commands, and reproduce §5.2/§5.4/§5.5 headline numbers; tag `v1.0.0`.

---

## 4. Thesis-Writing Track (parallel, starts now)

Ch5 already exists as a data-faithful draft (`docs/thesis/chapter5-results/README.md`). Writing must not wait for 1.0 — most chapters depend on *decisions already made*, not on pending data.

| Chapter | Can draft now? | Needs before final |
|---|---|---|
| 1 Introduction | **Yes** — thrusts/RQs/H1–H5 are stable in `docs/RESEARCH_THRUSTS_REPORT.md` | Final contribution list after H4 verdict |
| 2 Literature review | **Yes** — fully independent; also feeds 0.9.3/0.9.4 citations | Nothing |
| 3 Methodology | **Yes, ~80%** — operation-set design, two-lens security method, compliance-checker method all implemented and documented | N≥30 protocol + Sepolia protocol text (0.8/0.9) |
| 4 Implementation | **Yes, ~90%** — nine contracts, VC/DID/MOBI layers exist; the honesty ledger (§1) is the "limitations of implementation" section | ERC-725xy section (0.8.1) |
| 5 Results | **Drafted** — regenerate tables after 0.8 (CIs), 0.9 (Sepolia), 1.0-rc (H4, storage) | Freeze |
| 6 Discussion | Partial — frontier/trade-off narrative is writable from the current matrix | Sepolia + H4 results |
| 7 Conclusion | No | Everything |

**Proposed timeline** (no defense date exists anywhere in the repo — the following is *proposed*, not found; the only related marker is INVENTORY.md's "thesis writing target: December 2026"):
- 0.8 done ~Aug 8, 2026 · 0.9 done ~Aug 31 · 1.0-rc (experimental freeze) ~Sep 25 · v1.0 ~Oct 9
- Full thesis draft to supervisor ~Nov 30, 2026 · committee review Dec–Jan · **defense target: Feb–Mar 2027** (UBC ECE typically wants the examinable copy ~4–6 weeks before defense; confirm actual G+PS deadlines with the supervisor — that constraint is not in this repo).
This leaves ~5 weeks of slack before the writing tail; if experiments slip past mid-October, cut 1.0rc.2 (storage/throughput) first, then 1.0rc.1 (re-scope H4 honestly) — never cut 0.8/0.9.

---

## 5. Risks & Decision Points

### Top completion risks

| # | Risk | Likelihood × Impact | Mitigation |
|---|---|---|---|
| **R-A** | **Repository durability**: the designated `origin` (`nikhilprakash24/CVIN-SC-Implementation-SSI-DID`) rejects pushes (403 all session) and sits at stale `c444e99`; all real work lives only on the secondary `github` remote (`nikhilprakash-cvin/2_miniature-waffle-CV2X-Testbed-MOBI-VID`, verified holding `be32c6e` + tag `v0.7.0`) and in an ephemeral container. A container reset plus any secondary-remote mishap loses the thesis. | Med × **Catastrophic** | *This week*: `git bundle` to external storage; end-of-session push checklist; fix `origin` permissions or formally designate the secondary remote as canonical and update INVENTORY/README; consider a third mirror. |
| R-B | ERC-725xy stays unresolved and leaks into a committee draft as a false "9 implemented" claim | Med × High | Decision D1 executed in 0.8; until then, all documents say "8 + MOBI registry" |
| R-C | Sepolia logistics stall (faucet limits, RPC keys) push 0.9 past the freeze | Med × Med | Start faucet acquisition during 0.8; the run itself is a day; fallback: any public EVM testnet — the claim is chain-independence, not Sepolia specifically |
| R-D | Real-SUMO / network-stack scope creep consumes the schedule for a result H3 doesn't need | Med × Med | Decision D2 with a hard 3-day timebox; the 0.27 ms result already answers the crypto question |
| R-E | Single-author self-scored rigor challenged (compliance checklist, security grading) — repo risk R4/R5 | Low × Med | Committed test vectors; CI enforcement (already in place); cross-check a sample of compliance items against the W3C test-suite descriptions; supervisor review of the 44-check list |

### Strategic decisions (the student's call; recommendations with reasoning)

**D1 — ERC-725xy: build or cut to 8?**
*Recommend: build minimal-but-real (0.8.1, ~2–4 days).* The nine-standard framing is load-bearing in the title, RQs, and every table; re-scoping to eight forces rewriting the framing everywhere and invites "why was it dropped?" The build cost is genuinely small: ERC-725xy is compositionally ERC725X (execute) + ERC725Y (data), the audited `@erc725/smart-contracts` package is already vendored, and the existing ERC-725 tests/benchmark slots are templates. The honest alternative — redefine the set as "8 ERC standards + MOBI registry" and discuss 725xy qualitatively as a 725 variant — is defensible but strictly weaker, and the current state (benchmark silently substituting MOBI-VID-V2 in the ninth slot) is the worst of both and cannot stand either way.

**D2 — Real SUMO binary: worth it?**
*Recommend: one timeboxed confirmatory run, then stop; do not pursue network-stack simulation.* H3 is a claim about cryptographic verification cost, and 0.27 ms p95 with ~370× budget headroom answers it; vehicle mobility patterns cannot plausibly change `time.perf_counter` measurements of ECDSA verification, and an examiner knows that. The value of a real-SUMO run is purely rhetorical (deletes the "no SUMO binary" bullet from §5.8 for ~2 days of work since the TraCI path exists). ns-3/radio simulation would be a second thesis — decline it and rely on 0.9.3's literature-anchored budget decomposition instead.

**D3 — Sepolia validation depth?**
*Recommend: full operation set, one run per standard, tx hashes committed — no more.* Gas is opcode-deterministic, so N=1 on Sepolia against N=30 local medians is the *correct* design (the public run is a witness, not a sample); deeper Sepolia benchmarking would cost real ETH-equivalent time for zero statistical gain. The deliverable is a table mapping every local gas number to a public explorer link — that single artifact neutralizes the "toy local chain" attack for the entire RQ1 chapter.

**D4 — CVIN-Combined scope?**
*Recommend: freeze the design; add at most the S-sized issuer-gating flag (1.0rc.4) if the schedule holds.* The hybrid's thesis role — H5's frontier point — is already measured (identity at 52,178 gas ≈ ERC-1056's 52,612, claims at 289,923 ≈ ERC-735's 290,249), and its Sybil ✗ / recovery ✗ cells are *evidence for* the trade-off narrative, not defects to engineer away. The optional issuer-gating variant is attractive only because it demonstrates the frontier is tunable (one flag moves the Sybil cell at a measurable gas premium) — a nice discussion-chapter figure, not a requirement. Resist adding 4337-style recovery: it would blur the hybrid's identity as the *minimal* frontier point.

---

## 6. Next Session Starter

**Single highest-leverage stage: 0.8.** Exact opening sequence:

1. **(15 min) Durability first**: `git bundle create ../cvin-thesis-$(date +%Y%m%d).bundle --all`, move it off-container; confirm `git ls-remote github` still shows `be32c6e` + `v0.7.0`; delete the stray `CVIN-ID-SCs/` junk directory (untracked node_modules/artifacts from another session) or add it to `.gitignore`.
2. **(Core of the session) Execute D1 — build ERC-725xy** (`0.8.1`): create `1_blockchain-identity/contracts/ERC725xy/CVINVehicleERC725XY.sol` (combined X+Y account: `execute`, `setData`/`getData` batch variants, owner + operator permissioning), mirror the ERC-725 test file structure (~15–20 tests), wire the create/update/delegate/revoke/transfer operation set into `scripts/benchmark_gas.js`, add both security-lens entries, regenerate `gas_benchmark.json` / `gas_comparison.csv` / `.tex`.
3. **(If time remains) `0.8.2`**: wrap the benchmark in an N=30 loop emitting median/min/max/n per cell — this is mostly a harness change and immediately upgrades every RQ1 number.

Success criteria for that session: 9 real standards in a regenerated gas table, all suites green (~220+ tests), work pushed to the `github` remote *and* bundled off-container.

---

*Every number above is traceable: gas → `4_comparison-framework/results/gas_benchmark.json`; latency → `cv2x-testbed/sumo/results/v2v_latency.json`; compliance → `cv2x-testbed/scripts/w3c_compliance_checker.py` output; security → `4_comparison-framework/security-analysis/results/security_matrix.json` + `attack_results.json`; verdicts → `docs/thesis/chapter5-results/README.md` §5.7.*
