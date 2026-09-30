# Plan — MOBI VID Work and SUMO Work

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-09-25
**Inputs:** `docs/REVIEW_CV2X_TESTBED_LINEAGE.md` (what exists and what drifted),
`docs/LATENCY_BUDGET.md` (the budget the SUMO experiments must answer to),
`docs/MEASUREMENT_CONDITIONS.md` (how results are reported).

Every experiment below is **pre-registered** here: hypothesis, metric, N, environment
header, stopping rule. Results go to the claim register with status V only if the
script on the trunk produced them.

---

## Part A — MOBI VID

### A.0 Where it stands
Contracts: `MOBIVIDRegistry.sol` (VID I), `MOBIVIDRegistryV2.sol` (VID II: 11 event
types, 9 issuer roles, attestations), both under `1_blockchain-identity/contracts/MOBI/`
and mirrored in `cv2x-testbed/contracts/`. Python: `2_w3c-ssi-layer/mobi-vid/`
(birth certificate, lifecycle events, registry client; 32 tests). Results:
five-backend realisation sweep (`4_comparison-framework/results/mobi_vid_backends.*`)
with gas and a fidelity grade per backend; the attestEvent found-and-fixed gas change
(121,110 → 192,718). Open: no clause-by-clause reconciliation with the standard text;
the ZK VIN tier from the VID I spec is unbuilt; the centralized lifecycle-parity
comparison is unrun.

### A.1 Steps

| # | Step | Method | Output | Effort |
|---|---|---|---|---|
| M1 | **Clause-level reconciliation with the MOBI text** | Fetch the VID I preview PDF (linked in `MOBI_VID_RESEARCH.md`) and any public VID II material; build a checklist table: clause → contract/Python element → test → status | `docs/MOBI_VID_CHECKLIST.md` (to be created by this step; does not exist yet); SC entry if any clause is out of scope | 1 day |
| M2 | **Fidelity gradient into chapter 5** | Turn `mobi_vid_backends.csv` into the chapter table and one figure (gas vs fidelity, five backends); state the "native=no" approximations per cell | figure + table; register row | ½ day |
| M3 | **Regression test for the attestEvent fix** | A Hardhat test that asserts the vulnerable path is closed and pins the gas of the fixed path (192,718 ± 0) | test file; CI covers it | ½ day |
| M4 | **Lifecycle-parity comparison (review §3.3)** | Extend `experiment_pki_vs_erc1056.py` with a `centralized_registry` backend for birth / lifecycle-event / ownership-transfer / history-query; n=50; same reporting | `cv2x-testbed/results/lifecycle_parity.*`; register row; SC-13 closed | 1 day |
| M5 | **Pseudonym pool on ERC-1056 (review §5.4)** | 20 `addDelegate` with `validTo`, rotation every 5 min of simulated time; measure gas per rotation and linkability (can an observer link two pseudonyms of one vehicle from chain data alone?); compare with SCMS's design | results + a bounded privacy section (SC-02 partially closed) | 1–2 days |
| M6 | **VIN privacy: record the ZK tier as future work** | SC-12 entry; one paragraph in chapter 7 | scope log | ½ hour |
| M7 | **MOBI on Sepolia (M2 condition)** | When RPC + funded key exist as environment secrets: deploy VID I/II, run birth + one event + one attestation, confirm gas equals Hardhat to the unit, record block-inclusion latency | register rows with tag M2; `v0.9.0` cut | ½ day once credentials exist |

### A.2 Pre-registration for M4 and M5
- **M4 hypothesis:** the centralized registry is ≥10× faster than MOBI-VID-V2 for
  birth and lifecycle writes (local), equal for history queries once the chain
  history is cached; **metric:** median/p95 ms, n=50, plus gas for chain writes;
  **stopping rule:** none — a single full run; **threat:** the centralized registry is
  in-process (no network), so its figures are a lower bound, stated.
- **M5 hypothesis:** a 20-delegate pseudonym pool costs ≈20 × addDelegate (≈1.44 M gas)
  per rotation epoch and is fully linkable from chain data (all delegates hang off one
  identity) — i.e. ERC-1056 delegates give *key* rotation, not *identity* unlinkability,
  unlike SCMS pseudonyms; **metric:** gas; linkability as a yes/no with the linking
  query shown; **consequence:** the privacy section states that SSI-on-Ethereum needs
  per-pseudonym identities (cheap, since creation is implicit) rather than delegates
  to match SCMS.

---

## Part B — SUMO

### B.0 Where it stands
`cv2x-testbed/sumo/`: highway-intersection network, routes, `simulation.sumocfg`,
`sumo_identity_integration.py` (TraCI mode and `--simulate` mock-mobility mode; PKI
and SSI identity layers; `run_attack_tests`), `run_verify_scaling.py`,
`run_v2v_stats.py`. Results exist for `--simulate` only: 50 vehicles (35 SSI, 15 PKI),
10 Hz, 300 m radius, 30 seeds, sign/verify cold and warm. No SUMO binary has been
available in any session; `pip index versions eclipse-sumo` is checked in the
after-action report §3 (S7).

### B.1 Prerequisite
**S0 — install SUMO.** `pip install eclipse-sumo` (provides `sumo`, `sumo-gui`,
`netconvert` and the `traci`/`sumolib` Python packages) or the OS package. Needs
the author's go-ahead for the session (it is a ~100 MB install) or a local run on
the author's machine. Verify with `sumo --version` and a 10 s headless run of the
existing `simulation.sumocfg`.

### B.2 Experiments (in order; each is one script invocation plus the report step)

| # | Experiment | Hypothesis | Metric | Design | Output |
|---|---|---|---|---|---|
| S1 | **TraCI mode vs mock mobility** | The identity-layer latencies do not depend on the mobility model (mock ≈ TraCI within p95 overlap); neighbour counts do | sign/verify median/p95; neighbours per vehicle per step | same network, 50 vehicles, 30 seeds, both modes | validates the existing `--simulate` results or replaces them |
| S2 | **Full pipeline timing** | receive → resolve → verify → trust decision fits the J2945/1 identity budget for the off-chain design and not for the per-message chain read | per-message pipeline ms, median/p95, N ≥ 30 seeds; P*(0.5) empirical | instrument the harness at the four stage boundaries; run SSI with k = ∞ (cached) and k = 1 (chain per message) | `LATENCY_BUDGET.md` §3 rows move from E to V |
| S3 | **Freshness sweep** | P*(0.5) vs k follows t_eff = 0.4 + 2.5/k ms; the knee is at k ≈ 25 | P* per k | k ∈ {1, 5, 25, 100, ∞} | the design-frontier figure for chapter 6 |
| S4 | **Density scaling** | Verify cost is linear in neighbours; saturation P* matches the analytic figure within 10 % | messages verified per 100 ms vs vehicles in range | 50 → 100 → 200 vehicles on the existing network (extend routes), 30 seeds each | replaces bundle-lineage #26/#27 with trunk-verified rows |
| S5 | **Mixed fleet trust** | SSI and PKI vehicles interoperate with no added latency beyond the verify cost difference | cross-type verify latency; failed verifications = 0 | 50 % / 50 % fleet | answers roadmap Test 3 |
| S6 | **VeReMi replay (review §5.2)** | Identity catches 100 % of forged *senders* and 0 % of forged *payloads* | detection rate by attack class | replay VeReMi attack traces through `SSIIdentityLayer.verify` | SC-01 revived in bounded form; a chapter-6 division-of-labour argument |
| S7 | **Attack tests under mobility** | Sybil and replay are rejected at the identity layer in motion as they are in the contract harness | rejection rate, added latency | `run_attack_tests` in TraCI mode | roadmap Phase 7 at the SUMO level |
| S8 | **MOSAIC coupling (stretch)** | A channel model changes delivered-message counts, not identity cost per message | delivered messages, verify cost | Eclipse MOSAIC + SNS; port the identity step as a MOSAIC app | future work unless time permits |

### B.3 Reporting rules for every SUMO result
Environment header (SUMO version, network file hash, step length, BSM rate, radius,
receiver cap, seeds, CPU, commit); mobility mode stated in the first sentence; N and
median/p95 for latency; condition tag M0 for the identity path (no chain) and M1 where
the chain is read; results files under `cv2x-testbed/sumo/results/` with the run tag
in the filename; register rows added before chapter text cites them.

### B.4 Risks
- SUMO install blocked in the session → run locally and commit the results files with
  the header; the analysis scripts are deterministic on the JSON.
- The existing network is small (one intersection); density scaling to 200 vehicles
  may need a longer highway segment — `netconvert` from an OSM extract is the standard
  route.
- VeReMi traces are Veins-formatted; a 50-line adapter to the harness's BSM structure
  is needed.

---

## Part C — Order of execution and what needs the author

1. S0 needs a **go-ahead** (install in session) or a **local run**.
2. M7 needs **Sepolia RPC + key** as environment secrets.
3. Everything else is executable now: M1–M6, S1–S7 in the order listed; S1–S3 first
   because they convert the largest number of estimate rows to verified rows.
