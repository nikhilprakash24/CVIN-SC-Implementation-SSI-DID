# Crux Register

**Generated** by `docs/figures/make_dashboard_data.py` from `docs/thesis/cruxes.yaml` and the claim register (`docs/MEASUREMENT_CONDITIONS.md`). Do not edit by hand; edit the YAML and regenerate.

A crux is a question the thesis must answer for an examiner. State: **evidenced** = every evidence row is status V and no gap is open; **partial** = some evidence, or an open gap; **gap** = no evidence row.

| Crux | State | Hypotheses | Evidence rows (status) | Open gaps |
|---|---|---|---|---|
| C1 CAV identity substrate | **partial** | H1, H5 | #25 (V), #26 (V), #34 (V), #35 (V), #36 (V), #42 (V), #43 (V) | 2 |
| C2 Secure V2V messaging | **partial** | H3 | #21 (V), #27 (V), #32 (V), #37 (V), #39 (V) | 2 |
| C3 Infrastructure messaging (V2I and infrastructure-to-infrastructure) | **gap** | — | none | 1 |
| C4 Revocation freshness | **partial** | H3 | #32 (V), #37 (V), #40 (S) | 1 |
| C5 W3C conformance | **partial** | H2 | #4 (V), #24 (V) | 2 |
| C6 MOBI VID lifecycle | **partial** | H4 | #30 (V), #33 (V), #41 (S) | 1 |
| C7 Privacy and linkability | **partial** | — | #38 (V) | 1 |
| C8 Veracity versus automation asymmetry | **partial** | H5 | #28 (V), #42 (V), #43 (V) | 1 |

## C1 — CAV identity substrate

**Question.** On which blockchain identity standard should a connected or autonomous vehicle's DID be anchored?

**Claim.** Minimal-state standards are an order of magnitude cheaper to create an identity on; the hybrid sits on the cost/capability frontier at creation and over a vehicle's lifetime.

**Thrusts:** 1, 5 · **Hypotheses:** H1, H5 · **Defects bearing on it:** D7, D13, D25

| Row | Status | Claim (from the register) |
|---|---|---|
| #25 | V | Nine-standard gas table (deploy / create / update / delegate-or-claim / revoke / transfer per standard; MOBI-VID-V2 as application profile; ERC-4337 EntryPoint indirection +46,830 gas/op; create-identity spread 52,216 (C… |
| #26 | V | Scaling: marginal cost O(1) in history; lifetime ranking reversal (ERC-1056 cheapest over 15 years, 1,450,824 gas); verify O(1) in claim count; V2V saturation P*≈772 at 0.130 ms/neighbour (R²=0.9999) |
| #34 | V | Harness L1 per-op gas, all nine standards (ten columns; ERC-1056 in pure and wrapper mode). C1 create: 76,808 / 145,662 / 399,844 / 656,480 / 1,535,776 (ERC-735) / 103,913 (ERC-1155) / 1,730,753 (ERC-725xy) / 132,515 (LS… |
| #35 | V | Harness L2 lifecycle (17 MOBI VID events), all nine standards: ERC-1056 1,050,787 (wrapper 1,025,381) · ERC-1155 1,150,981 (excl. 2 n/a; no attributes stored, no delegates) · LSP8 1,505,258 (excl. 3 n/a) · ERC-4337 2,221… |
| #36 | V | H5 dominance analysis over six declared criteria (lifetime gas ↓, zero→nonzero SSTOREs ↓, R3 RPC at h=50 ↓, R3 median ms after lifecycle ↓, core ops supported ↑, O(1) on-chain credential check ↑ [design property, assigne… |
| #42 | V | (sandbox lineage, was #31; history row for the pre-merge contracts) Gas moved by the 2026-10-04 defect fixes (D13 VIN normalisation on three mint paths; D21 `revoked` check and `previousChange` on the vehicle-profile reg… |
| #43 | V | (sandbox lineage, was #32; history row for the pre-merge contracts) Gas moved by the 2026-10-04 pass-06 fixes (D7/D8 ERC-1155: standard transfers closed, held-type bitmap, `issuerTransferIdentity`; D11b MOBI `anchorVehic… |

**Open gaps:**
- After the 2026-10 fixes ERC-735 is the heaviest create (veracity has a deployment price); chapters 5 and 6 need the sentence.
- The harness analysis (#36) finds CVIN-Combined dominated by ERC-4337 on six criteria; H5's wording must reconcile with it.

**The examiner will ask:** Is "cheaper" robust to the operation definition, and does the frontier survive the harness's six criteria?

**Artefacts:** `4_comparison-framework/results/gas_benchmark.json`, `4_comparison-framework/results/scaling_lifetime.json`, `docs/FEATURE_ASYMMETRY_MATRIX.md`, `sandbox/grand/report/L1-asymmetry.md`

## C2 — Secure V2V messaging

**Question.** Does blockchain-rooted identity verification fit the V2V safety-message budget?

**Claim.** Off-chain verification of pre-issued credentials adds well under a millisecond per message; uncached on-chain resolution does not fit and needs a freshness policy.

**Thrusts:** 3 · **Hypotheses:** H3 · **Defects bearing on it:** D11, D11b

| Row | Status | Claim (from the register) |
|---|---|---|
| #21 | V | PKI vs ERC-1056 identical operations, n=50 (median / p95 ms): verify 0.253 / 0.329 PKI (pki_standard; pki_centralized 0.254 / 0.325; CA signature + issuer + validity + CRL + message signature) vs 9.654 / 15.984 ERC-1056 … |
| #27 | V | V2V SSI verify warm 0.153 ms [0.151, 0.154] (median of 30 seeded-run medians, 95 % bootstrap CI; p95 of run medians 0.158), cold 0.399 [0.381, 0.411]; PKI warm 0.094 [0.093, 0.095], cold 0.220 [0.218, 0.223]; 1,650,318 v… |
| #32 | V | Freshness-k ERC-1056 verify, n=250 per k, mean (amortised) / median / p95 ms: k=1 11.76 / 10.95 / 16.15; k=5 2.38 / 0.46 / 10.48; k=25 0.85 / 0.43 / 0.76; k=∞ 0.45 / 0.43 / 0.63; P*(0.5) = 4 / 21 / 58 / 110. Means fit t_… |
| #37 | V | Freshness-k with a one-call (probe) refresh, cv2x ERC-1056 verify: a refresh is one `getIdentityInfo` eth_call, with full resolution only if the identity moved. t_chain_probe 2.76 / 2.89 ms vs 14.38 / 10.28 ms for the fu… |
| #39 | V | HTTP-RPC condition, all ten columns (N=30): every gas table byte-identical to #34/#35; latency ≈2–2.5× the in-process figures (U3 tx median 8.0 → 18.1 ms ERC-1056; R1 0.9 → 2.0 ms). R3 resolve at history h=50, median / p… |

**Open gaps:**
- Mobility is simulated (no SUMO run); radio, MAC and channel are out of scope.
- The freshness knee is host-dependent (#37).

**The examiner will ask:** What part of the 100 ms budget did you measure, and on which host?

**Artefacts:** `cv2x-testbed/sumo/results/v2v_latency_stats.json`, `cv2x-testbed/results/pki_vs_erc1056.json`, `cv2x-testbed/results/freshness_k.json`

## C3 — Infrastructure messaging (V2I and infrastructure-to-infrastructure)

**Question.** Does the same identity layer secure roadside-unit and infrastructure messages (SPaT/MAP, RSU-to-RSU, RSU-to-traffic-management)?

**Claim.** An RSU is a DID with a road-authority issuer; signed SPaT reuses the BSM path; revocation of a compromised RSU key is observed within a bounded number of messages.

**Thrusts:** 3 · **Hypotheses:** none yet · **Defects bearing on it:** none

_No evidence row exists._

**Open gaps:**
- No implementation and no measurement exist; design note written 2026-10-09, code waits for audit.

**The examiner will ask:** Your title says connected vehicles; where is the infrastructure?

**Artefacts:** `cv2x-testbed/V2_DESIGN.md`, `docs/design/INFRASTRUCTURE_MESSAGING.md`

## C4 — Revocation freshness

**Question.** How quickly does a verifier stop trusting a revoked vehicle key, and at what latency cost?

**Claim.** A cached verifier honours a revoked key for at most k-1 further messages; the k that meets the neighbour-saturation target depends on the host and on the refresh mode.

**Thrusts:** 3, 5 · **Hypotheses:** H3 · **Defects bearing on it:** D21

| Row | Status | Claim (from the register) |
|---|---|---|
| #32 | V | Freshness-k ERC-1056 verify, n=250 per k, mean (amortised) / median / p95 ms: k=1 11.76 / 10.95 / 16.15; k=5 2.38 / 0.46 / 10.48; k=25 0.85 / 0.43 / 0.76; k=∞ 0.45 / 0.43 / 0.63; P*(0.5) = 4 / 21 / 58 / 110. Means fit t_… |
| #37 | V | Freshness-k with a one-call (probe) refresh, cv2x ERC-1056 verify: a refresh is one `getIdentityInfo` eth_call, with full resolution only if the identity moved. t_chain_probe 2.76 / 2.89 ms vs 14.38 / 10.28 ms for the fu… |
| #40 | S | (sandbox lineage, was #29; S by instrument — superseded by #32/#37, kept for the k=100 point and as the first measurement behind `LATENCY_BUDGET.md` §3) Freshness-k cached verifier, ERC-1056 (n=200, one sender, warm): k=… |

**Open gaps:**
- Choose the k the thesis defends (review-2 decisions 10 and 14).

**The examiner will ask:** Is k-1 messages of revocation staleness at 10 Hz acceptable for a safety system?

**Artefacts:** `cv2x-testbed/results/freshness_k.json`, `cv2x-testbed/results/freshness_k_probe.json`

## C5 — W3C conformance

**Question.** Can blockchain identities be lifted to W3C DID and VC conformance?

**Claim.** The executable checker clears the 90 % target and the external W3C DID test suite passes all but one generated test, also on a registry-minted did:ethr.

**Thrusts:** 2 · **Hypotheses:** H2 · **Defects bearing on it:** D10, D27

| Row | Status | Claim (from the register) |
|---|---|---|
| #4 | V | W3C compliance, internal checker: 94.3% on the review-02 tree (executable score = PASS + 0.5×PARTIAL over 44 executed checks: 41 PASS, 1 PARTIAL, 2 FAIL; DID Core v1.0, VC Data Model v2.0; the 10 SSI-principle items are … |
| #24 | V | External W3C DID test suite: 335/336 generated tests (also 335/336 on a `did:ethr` minted by `MOBIVIDRegistry.getVehicleDID` on Hardhat, sandbox lineage 2026-10-04, `docs/conformance/W3C_DID_TEST_SUITE.md` §8 of the sand… |

**Open gaps:**
- The DID Core checks test a synthesised document; label them structural (review-2 decision 2).
- The resolver builds did:ethr documents from the identifier, not from chain state.

**The examiner will ask:** Does conformance of the document shape say anything about the chain state behind it?

**Artefacts:** `4_comparison-framework/results/w3c_compliance.json`, `docs/conformance/W3C_DID_TEST_SUITE.md`

## C6 — MOBI VID lifecycle

**Question.** Is the MOBI VID birth certificate and lifecycle realisable across substrates?

**Claim.** Birth and lifecycle are native on all five backends; multi-party attestation on three; the profile is MOBI-VID-inspired, checked against the public texts.

**Thrusts:** 4 · **Hypotheses:** H4 · **Defects bearing on it:** D16

| Row | Status | Claim (from the register) |
|---|---|---|
| #30 | V | Harness L2 MOBI-VID lifecycle (17 events, including the delegate add that the rotation retires): 1,050,787 / 2,701,239 / 3,155,103 gas, ERC-1056 cheapest by 2.57× / 3.00×; zero→nonzero SSTOREs 8 / 92 / 83 (writes, not ne… |
| #33 | V | M4 lifecycle parity (pre-registered, `PLAN_MOBI_SUMO.md` §A.2), n=50, median / p95 ms, centralized vs MOBI-VID-V2: birth 0.0028 / 0.0076 vs 14.13 / 20.77 (398,298 gas); lifecycle event 0.0064 / 0.0109 vs 11.86 / 14.88 (2… |
| #41 | S | (sandbox lineage, was #30; S by instrument — superseded by #33; its `attest_event` row, which #33 lacks, is kept here) Lifecycle parity, centralized registry vs MOBI VID V2 (n=50, median / p95 ms): register_birth 0.004 /… |

**Open gaps:**
- Few of the VID I MUSTs are met and the birth certificate lacks mandatory fields (checklist §1; SC-17, SC-18 pending).

**The examiner will ask:** Why call it MOBI if most normative requirements are unmet?

**Artefacts:** `4_comparison-framework/results/mobi_vid_backends.json`, `docs/MOBI_VID_CHECKLIST.md`

## C7 — Privacy and linkability

**Question.** What does pseudonymity cost on a public identity registry, and is it effective?

**Claim.** A delegate pool is fully linkable by one log query; per-pseudonym DIDs are unlinkable only while attribute-free or relayed.

**Thrusts:** 5 · **Hypotheses:** none yet · **Defects bearing on it:** none

| Row | Status | Claim (from the register) |
|---|---|---|
| #38 | V | M5 pseudonym pool on `EthereumDIDRegistry` (pre-registered, `PLAN_MOBI_SUMO.md` §A.2): 20 `addDelegate` per 5-min epoch cost 1,113,456 gas (first epoch), then 1,096,368 (71,919 for the identity's first write, then 54,807… |

**Open gaps:**
- Radio, timing and position linkability are future work (SC-02).

**The examiner will ask:** Is a public chain compatible with V2X pseudonymity at all?

**Artefacts:** `4_comparison-framework/results/pseudonym_pool.json`

## C8 — Veracity versus automation asymmetry

**Question.** What does implemented-but-uncompared surface cost in correctness and security?

**Claim.** Exercising every public function found latent defects the comparison never priced; fixing them moved the gas table.

**Thrusts:** 5 · **Hypotheses:** H5 · **Defects bearing on it:** D7, D11b, D13, D21, D22, D25

| Row | Status | Claim (from the register) |
|---|---|---|
| #28 | V | Security: 43/43 attacks defended; DEFENDED = reverted with the documented expected reason (strict harness, review 02 Q-8). attestEvent found-and-fixed 121,110 → 192,718 gas (July build); on the current build the fixed pa… |
| #42 | V | (sandbox lineage, was #31; history row for the pre-merge contracts) Gas moved by the 2026-10-04 defect fixes (D13 VIN normalisation on three mint paths; D21 `revoked` check and `previousChange` on the vehicle-profile reg… |
| #43 | V | (sandbox lineage, was #32; history row for the pre-merge contracts) Gas moved by the 2026-10-04 pass-06 fixes (D7/D8 ERC-1155: standard transfers closed, held-type bitmap, `issuerTransferIdentity`; D11b MOBI `anchorVehic… |

**Open gaps:**
- The chapter-6 section is a draft.

**The examiner will ask:** Would a different implementation of the same standard have different defects, and does that undermine the comparison?

**Artefacts:** `docs/DEFECT_LOG.md`, `sandbox/grand/report/demos.md`, `docs/thesis/chapter6-discussion/section-feature-asymmetry.md`
