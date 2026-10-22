# PLAN — Research Expansion (composed scenarios, primitive upgrades, moonshots)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-10-15
**Status:** OPEN. Phase 0 item X1 is CLOSED (built, tested, pushed on `claude/cvin-research-improvements-559o01`).
**Inputs:**
- `docs/research-expansion/IDEAS.md` (what)
- `docs/research-expansion/WHY.md` (why)
- `docs/research-expansion/SOURCES.md` (evidence)
- `docs/research-expansion/PROMPT_PACK.md` (the same plan as copy-paste prompts, one per work package)

---

## 1. Goal

Move the thesis from *"each primitive measures well"* to *"the primitives compose into real vehicle services, and here is what composition costs, reveals and requires during the transition from today's systems"*. This must not disturb any existing result, register row or chapter claim.

## 2. Tracks

The catalogue holds about 35 items. They split into three tracks so that scope is the author's explicit choice:

| Track | Purpose | Phases | Default |
|---|---|---|---|
| **T — thesis** | Evidence that enters chapters 4–7 | 0, 1, 2 (+ P14 from 4) | recommended |
| **S — side papers** | Separable publishable results | 2 (P5), 4, 6 (M4) | optional |
| **F — future work** | Prototype or paragraph for chapter 7 | 3, 5, 6 | optional |

## 3. Standing rules (inherited from the repo)

- Commits are author-attributed, with no AI co-author trailers. Commit and push at every work-package boundary.
- No test is skipped, weakened or deleted. CI fails on any Python skip.
- A number enters a chapter only with a V-status row in `docs/MEASUREMENT_CONDITIONS.md`. Next free row on the merged tree: **#55** (#40–#54 are taken). Fetch before numbering; parallel sessions have collided before.
- Pre-register any new hypothesis threshold **before** building the thing it tests. Report PASS/FAIL as observed and label post-hoc explanations as post hoc.
- Author framing decisions are listed, not taken.
- New canonical docs get a row in `docs/INDEX.md`.

## 4. Phases and work packages

Each work package (WP) lists its inputs, deliverables and acceptance criteria. "DoD" means definition of done.

### Phase 0 — Foundation (T) — target: 1–2 sessions

| WP | Item | Deliverables | DoD |
|---|---|---|---|
| 0.1 | **X1 toll corridor** | Contracts, 20 Hardhat + 4 pytest tests, results JSON, docs | ✅ CLOSED in this session. Hardhat 389/23 pending, Python 362, compliance 94.3% |
| 0.2 | X1 register rows | Proposed #55 (X1 gas: `payToll`, batch 1/10/25) and #56 (X1 gate read, M1-H/HTTP), with the condition caveat that fresh keys change calldata | Rows added with V status after a clean-tree run; or an author decision to defer |
| 0.3 | P6 on-chain `_resolve_ethr` | `did_resolver.py` reads ERC-1056 logs when a provider is given; offline mode unchanged | New tests against a node; DID suite re-run; checker re-run, delta recorded |
| 0.4 | P1 EIP-712 migration | Typed-data variants of CVIN-Combined `addClaim`, ERC-735 `addClaim`, MOBI `attestEvent`; old paths kept | New attack cell "cross-contract replay" DEFENDED on the new paths and demonstrated on the old ones; gas delta table |
| 0.5 | P2 Bitstring Status List | `BitstringStatusListRegistry` beside the existing registry; verifier supports both | W3C structure tests; verify ms and bytes at 131,072 entries; checker delta |
| 0.6 | P7 trust-registry contract | TRQP-shaped `isAuthorized`; the corridor can read it | Gas per query; federation (scoped recognition) tests |
| 0.7 | Scope-log repair | `docs/SCOPE_CHANGES.md` was truncated by commit `760913c` (SC-01…SC-13 removed); the full table is at `d53126e` | **Author decision.** Restore by appending, never by rewriting history |

### Phase 1 — Transition and legacy (T) — target: 2–3 sessions

| WP | Item | Deliverables | DoD |
|---|---|---|---|
| 1.1 | **X4 dual-stack intersection** | `DualStackIdentityLayer`; policies accept-either / shadow / cut-over; adoption sweep 0, 10, …, 100% | Migration-curve figure (verify ms, bytes per BSM, % actionable); shadow-mode disagreement detection with injected faults; pre-registered H7 verdict |
| 1.2 | P13 legacy bridge | `did:web` + `did:x509`-shaped resolution; X.509 → VC bridge-credential issuer using the existing `pki_identity.py` CA | Bridge credential verifies; trust-path length reported; did:x509 adaptation caveat for the 1609.2 format stated |
| 1.3 | P9 VIN oracle | `VINOracle.sol` (m-of-n EIP-712 reports, replay set, staleness); recorded vPIC/NMVTIS-shaped fixtures; optional live vPIC script outside CI | Collusion matrix (k−1 lying oracles fail, k pass); fixtures documented as synthetic |
| 1.4 | **X3 used-car sale** | Consistency engine (vPIC vs birth certificate, NMVTIS vs MOBI odometer, title brand vs events); atomic settlement (4337 batch or settlement contract); paper-title bridge path | Fraud matrix: rollback, washed title, cloned VIN, oracle quorum−1. Atomic all-or-nothing tested |

### Phase 2 — Privacy (T + S) — target: 2–4 sessions

| WP | Item | Deliverables | DoD |
|---|---|---|---|
| 2.0 | Pre-register H8 | Threshold for unlinkable-toll gas (proposed ≤ 10× X1 `payToll` = 1.106M) and proof time | Written before 2.1 starts |
| 2.1 | **P5 unlinkable passage** | Circom group-membership + nullifier circuit (Semaphore or a minimal custom one); Groth16 verifier; `CVINTollCorridorZK` | Linkability test: no on-chain field links two trips of one vehicle; double-spend via nullifier blocked; gas and proving time on laptop + ARM-class; H8 verdict |
| 2.2 | P3 SD-JWT VC | RFC 9901 issuer, holder and verifier with key binding | Size/latency against DI-SD; negative tests |
| 2.3 | P4 BBS evaluation | Library survey (Python/WASM), then the minimal `bbs-2023` path if a maintained library exists | Proof size against hidden messages; verify ms; or a written "not feasible because…" |
| 2.4 | X11 parking inversion | City policy VC, car receipts, officer check | Exposure comparison against the plate-photo lane |

### Phase 3 — Human credentials and accounts (F, or T if chosen) — target: 2–3 sessions

| WP | Item | Deliverables | DoD |
|---|---|---|---|
| 3.1 | P8 4337 hardening | Guardian threshold + timelock recovery; session keys with policy; sponsoring paymaster | Recovery attack cells; a closed caveat at `scripts/security_scenarios.js:619`; paymaster gas overhead |
| 3.2 | **X2 rental handoff** | Licence credential (ISO 18013-5 elements as claims, `age_over_25`); session-key unlock; status-list suspension mid-rental; MOBI damage event; 2-of-3 escrow | Time from flip to refusal; disclosed bytes vs full licence; all negative paths |
| 3.3 | P11 mdoc | CBOR/COSE MSO issue and verify; roadside licence check | mdoc vs VC latency; interop caveats |
| 3.4 | P10 OpenID4VC | OID4VCI issuance + OID4VP presentation over a local HTTP server | Protocol round-trip latency; HAIP gaps listed |

### Phase 4 — Economics (T for P14; S for the rest) — target: 2 sessions

| WP | Item | Deliverables | DoD |
|---|---|---|---|
| 4.1 | **P14 fiat cost model** | Gas → USD on L1 + 3 L2s from recorded fee snapshots (dated); per-vehicle-per-year totals for H1 lifecycles and X1 tolls | Sensitivity table; snapshot provenance; chapter 6 §6.6.3 closed |
| 4.2 | P15 anchoring | `AnchorLog.sol` per-minute Merkle roots; inclusion proofs | Gas per anchored item vs N |
| 4.3 | X6 Plug & Charge | Battery passport VC; mutual auth; payment channel with EIP-712 vouchers | Break-even curve (events per session) against X1 settlement |
| 4.4 | X8 black box | Per-minute telemetry anchoring; consent VP over time ranges; staged-crash detection | Fraud matrix; proof size per revealed second |

### Phase 5 — Safety and regulation (F) — target: 2 sessions

| WP | Item | DoD |
|---|---|---|
| 5.1 | X7 recall → OTA | Uptane-shaped metadata verify; firmware anchor; R156 evidence VP; evidence-pack size against fleet size |
| 5.2 | X5 ambulance green wave | Delegation chain verify; nullifier per (incident, intersection); 2-of-3 audit opening; latency against the budget |
| 5.3 | P12 formal and fuzz | Invariants for corridor escrow conservation (`sum(escrow) + treasury == token balance`), nonce uniqueness and 4337 recovery; fuzz campaign report |

### Phase 6 — Moonshots (F / S) — target: timeboxed, 1 session each

| WP | Item | Minimum publishable result |
|---|---|---|
| 6.1 | M1 PQ hybrid BSM | Bytes and verify ms for ECDSA+ML-DSA-44 on the SUMO path; fits or does not fit the payload budget |
| 6.2 | M4 ZK usage-based insurance | A circuit proving a distance bound over anchored telemetry (X8); proving time; SP-9 outline |
| 6.3 | M9 fifteen-year identity | A rotation ceremony secp256k1 → hybrid PQ key via ERC-1056 attributes; MOBI history intact; list of what breaks |
| 6.4 | X10 robotaxi agent | Agent registry + model-provenance VC + spending policy, composed with X1 and X6 |
| 6.5 | M2, M3, M5–M8, M10 | One-page future-work notes, each with a sourced obstacle |

### Phase 7 — Thesis integration (T) — continuous

- A chapter 4 section on the scenario architecture (X1 first) and a chapter 5 subsection on composed-scenario results (the gas, latency, exposure triple).
- Chapter 6 discussion: split-brain revocation, rotation ≠ unlinkability, migration curve.
- Chapter 7: moonshot future work with prototype evidence.
- `SIDE_PAPERS.md`: propose SP-9 (ZK UBI), SP-10 (split-brain revocation in composed SSI services) and SP-11 (unlinkable tolling cost).
- `docs/INDEX.md` rows; a `CHANGELOG.md` entry under the next version.

## 5. Dependency graph

```
0.3 P6 ──┐
0.4 P1 ──┼──> 1.3 P9 ──> 1.4 X3
0.6 P7 ──┼──> 1.1 X4 <── 1.2 P13
0.5 P2 ──┼──> 3.2 X2 <── 3.1 P8, 3.3 P11
         └──> 2.1 P5 (needs 2.0 pre-registration) ──> 6.2 M4
4.2 P15 ──> 4.4 X8 ──> 6.2 M4
4.1 P14 consumes all gas rows
```

## 6. Author decisions required

| # | Decision | Recommendation |
|---|---|---|
| AD-1 | Which tracks to adopt (T only, T+S, all) | T plus P5 from S |
| AD-2 | Adopt RQ5–RQ7 / H6–H8 (`WHY.md` §7)? | Adopt RQ5 + H6 (X1 already supports it); decide RQ6/RQ7 after Phase 1 |
| AD-3 | Register #55/#56 for X1 now, or after P14 | Now, so chapters can cite X1 |
| AD-4 | Restore `docs/SCOPE_CHANGES.md` SC-01…SC-13 by appending from `d53126e` | Yes, append-only |
| AD-5 | Add a ZK toolchain (circom, snarkjs) to CI, or keep ZK tests opt-in | Commit the verifier and keep proof generation out of CI; CI verifies committed proofs |
| AD-6 | Live network calls (vPIC) | Never in CI; a recorded-fixture lane only |

## 7. Risks

| Risk | Mitigation |
|---|---|
| Scope creep dilutes the thesis | Tracks plus AD-1; Phase 6 timeboxed |
| Demo-ware (prints success) | Every WP needs negative tests and computed verdicts (X1 sets the bar: 14 attack cells) |
| Toolchain weight (circom, liboqs, cbor) | Isolate per package; keep CI green without optional tools; never skip tests (separate opt-in suites) |
| Register collisions with parallel sessions | Fetch before numbering; propose rows as "P-#n" in docs until merged |
| Prior-art overlap (S31, S85) | Read before claiming novelty; keep the SC-04 wording |

## 8. Progress log

| Date | WP | Result | Commit |
|---|---|---|---|
| 2026-10-15 | 0.1 X1 | CLOSED. 20 Hardhat + 4 pytest. `payToll` 110.6k gas; 56.2k/ticket at batch 25; gate read ≈21–23 ms (M1-H/HTTP, one host). Findings: split-brain revocation, DID-level linkability | `1133737` |
| 2026-10-22 | Merge + re-run | Merged the default branch (`claude/clone-cvin-id-scs-…`, incl. PR #3 layer 5) into this branch, no conflicts. Merged tree: Hardhat 579 passing / 34 pending, Python 431, layer 5 49, compliance 94.3%. X1 fix: deadlines now use chain time (a shared node is fast-forwarded by other suites; wall-clock deadlines expired every ticket). X1 re-run: 4 admitted, the same two denials, 56.2k gas/ticket at batch 25, gate read 26 ms (one run). X1 rows renumbered to proposed #55/#56 (#40–#54 are taken on the merged register) | this commit |

## 9. Status against work on other branches (survey 2026-10-22)

| Catalogue item | Status elsewhere | Effect on this plan |
|---|---|---|
| P5 unlinkable passage | Layer 5 (`5_zkp-agent-identity/`, merged) has a Groth16 verifier, nullifiers, a Merkle library and `ZkVinGate` (301,163 gas; ZK-VIN prove 398.6 ms, verify 18.42 ms; single-party setup, insecure) | WP 2.1 builds on layer 5's verifier and nullifier code instead of starting from Semaphore |
| P6 on-chain resolution | Done on other lines: H-R (on-chain did:ethr + did:mobi; `simulation-visual-plan`) and WM-2 C1 (`cv2x-testbed-setup`). Not yet on the default branch | WP 0.3 becomes "merge or port H-R", not new work |
| X10 robotaxi agent, M7 | Layer 5 `steward/` (agent-wrapped identity, leakage ≤3.0 bits on 90/90 runs; Z-E6 honest service ≥90% NOT met); `vid-build` ports VID to ERC-8004 | WP 6.4 composes these instead of new registries |
| X3 / P9 VIN oracle | Layer 5 defect D64: an unsalted VIN hash reverses in 3.58 s per 10⁶ | Oracle reports must carry salted VIN hashes; add as a WP 1.3 attack cell |
| P3, P15 | `vid-build` has SD-JWT-style digests and `PresentationAnchor.sol` | Reuse in WP 2.2 / 4.2 |
| X4, X5 presentation | `simulation-visual-plan` has trace replay and real SUMO 1.28 + TraCI | Use for migration-curve figures |
| P12 | Layer 5 has 5 mutants; `testing-suite-organization` has a 1,505-row test register | Extend rather than restart |

Naming clash: the default branch's register #53 measures a basic-set item it also calls "X1". This plan's X1 is the toll corridor; cite it as "X1 (toll corridor)". `vid-build`'s `5_minimal-ssi-sandbox/` also clashes with `5_zkp-agent-identity/` on the layer number.
