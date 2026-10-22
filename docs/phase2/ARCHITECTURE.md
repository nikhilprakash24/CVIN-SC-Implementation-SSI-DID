# Phase 2 Architecture — Reference Model, Interfaces and Structural Options (Sketch)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, P2.0, session 1). **State:** sketch for discussion; P2.2 turns the parts
the chosen programme needs into ADRs (`DECISIONS.md` §2). **Binds:** `docs/phase2/README.md`.

## 1. The reference model: seven planes
Phase 1's code already falls into planes. Naming them lets each Phase 2 idea say which plane it changes and
which interfaces it must not break.

```
 ┌──────────────────────────────────────────────────────────────────────────────────────────┐
 │ P6 Presentation   dashboard · presentation report · thesis tables      (generated only)  │
 ├──────────────────────────────────────────────────────────────────────────────────────────┤
 │ P5 Evidence       run stamps (per-producer scope) · runs/ + promote · claim register ·   │
 │                   stale-figure check · test register · audits           (every plane writes here)
 ├──────────────────────────────────────────────────────────────────────────────────────────┤
 │ P4 Trust          freshness policy (k) · revocation status · RSU cache · trust lists      │
 │                   [Phase 2: time-bounded caches, I2I propagation, misbehaviour → revoke]  │
 ├──────────────────────────────────────────────────────────────────────────────────────────┤
 │ P3 Credential     W3C VC issue/verify · DID resolution · MOBI VID I/II · PKI certificates │
 │                   [Phase 2: SD-JWT VC / BBS, ZK VIN proofs, hybrid 1609.2 + DID]          │
 ├──────────────────────────────────────────────────────────────────────────────────────────┤
 │ P2 Ledger         nine standards + baselines behind IdentityAdapter (JS) and              │
 │                   IdentityProvider / lifecycle backends (Python) · Hardhat (M1)           │
 │                   [Phase 2: public testnet, rollups, chain-bound variants]                │
 ├──────────────────────────────────────────────────────────────────────────────────────────┤
 │ P1 Messaging      BSM · SPaT · MAP signing and verification · in-process back-haul        │
 │                   [Phase 2: radio/MAC coupling, RSU-to-RSU channel]                       │
 ├──────────────────────────────────────────────────────────────────────────────────────────┤
 │ P0 Mobility       MockMobility (positions, neighbours, contact times)                    │
 │                   [Phase 2: SUMO/TraCI, recorded traces, hardware]                        │
 └──────────────────────────────────────────────────────────────────────────────────────────┘
```

| Plane | Phase 1 code today | Ideas that change it |
|---|---|---|
| P0 Mobility | `MockMobility` in `cv2x-testbed/sumo/sumo_identity_integration.py`; a TraCI branch that falls back to mock when SUMO is absent | I-01, I-11, I-23 |
| P1 Messaging | `PKIIdentityLayer`, `SSIIdentityLayer` (same file); `cv2x-testbed/sumo/infrastructure_layer.py` | I-02, I-04 |
| P2 Ledger | `1_blockchain-identity/contracts`, `benchmarks/adapters/IdentityAdapter.js`, `sandbox/options/*/adapter.js`, `cv2x-testbed/identity/base.py` (`IdentityProvider`), `lifecycle_backends.py` | I-03, I-08, I-12 |
| P3 Credential | `2_w3c-ssi-layer/verifiable-credentials`, `did-resolution`, `mobi-vid`; `cv2x-testbed/identity/standard/pki_identity.py` | I-06, I-09, I-10, I-15, I-16, I-17 |
| P4 Trust | `cv2x-testbed/identity/freshness.py`; the RSU cache in `infrastructure_layer.py` | I-04, I-05, I-07, I-13 |
| P5 Evidence | `tools/run_identity/`, `docs/testing/`, `docs/MEASUREMENT_CONDITIONS.md`, `sandbox/grand/run.py` | I-18, I-22 (reads it); every idea writes to it |
| P6 Presentation | `docs/figures/`, `docs/presentation/` | I-19 |

**One rule across planes:** a plane may depend only on the planes below it and on P5. P5 depends on none
(it reads files). This is how Phase 1 already behaves. The rule is written down so that Phase 2 keeps it.

## 2. The interfaces Phase 2 would add
Each interface keeps the Phase 1 implementation as its first, reference implementation, so every Phase 1
result stays reproducible through it ("the mock is an adapter, not a special case").

| Interface | Plane | Contract (sketch) | Reference implementation (Phase 1) | Phase 2 implementations |
|---|---|---|---|---|
| `MobilitySource` | P0 | `step(t) → positions`; `neighbours(v, radius)`; `contacts(v, rsu)`; deterministic for a seed | `MockMobility` | TraCI (I-01); recorded trace replay |
| `Channel` | P1 | `send(msg, from, to, t) → deliveries[(to, t_arrive)]` or loss; carries no identity logic | in-process, zero delay | simulator coupling (I-02); a calibrated loss/delay model (I-02 fallback) |
| `LedgerTarget` | P2 | deploy, transact and read for one network, with the condition tag (M1, HTTP, testnet, rollup) recorded in the stamp | Hardhat in-process (M1) | public testnet, rollup testnet (I-03) |
| `CredentialSuite` | P3 | `issue`, `present(disclose)`, `verify` with a cost record; the suite id goes into every result | the current VC suite | SD-JWT VC, BBS (I-10); hybrid certificate (I-06); ZK proof (I-09) |
| `RevocationPolicy` | P4 | `must_recheck(cache_entry, now, msg_count) → bool`; `on_status(…)`; time and count both visible | `FreshnessPolicy` (message-bounded k) | time-bounded and hybrid caches (I-05); I2I-fed cache (I-04) |
| `Detector` | P4 | `observe(msg) → suspicion`; `decide → revoke request` | none | rule-based detector (I-07) |
| Producer manifest | P5 | already exists: stamp + `runs/<name>/<run-id>/manifest.json` + promote (WM-2 A2, A4) | `tools/run_identity/` | every Phase 2 producer registers in `producers.json` from its first line of code |

Two contracts every interface keeps: (1) the reference implementation reproduces the Phase 1 numbers
byte-for-byte or within the register's tolerance; (2) the implementation in use is recorded in the result's
stamp, so no result can be read without knowing which mobility, channel, ledger, suite and policy produced it.

## 3. Three structural options for where Phase 2 code lives
| Option | What | For | Against |
|---|---|---|---|
| **A. In place** | Phase 2 extends the existing directories; new interfaces are carved out of the current files | least movement; Phase 1 machinery applies at once; one CI | the testbed files are already large (`sumo_identity_integration.py`); Phase 2 edits would mark Phase 1 results "code changed since" and churn the register |
| **B. Plug-in layer** | a new top-level `phase2/` package that implements the interfaces of §2; Phase 1 files change only to accept an injected implementation (with the Phase 1 one as default) | Phase 1 results stay stable; Phase 2 work is isolated and reviewable; the pattern already exists (`sandbox/options/*/adapter.js`, `IdentityAdapter`) | one up-front refactor per interface, each a Phase 1 change with a regression run |
| **C. Separate repository** | Phase 2 in its own repository, consuming Phase 1 as a pinned dependency | cleanest separation; its own release cadence | the evidence machinery and the register would be split or duplicated; the thesis cites one artefact more naturally than two |

**Orchestrator default (ADR-0001, proposed): option B.** Reasons: Phase 1's results of record stay
untouched by Phase 2 code; each interface carve-out is a small Phase 1 step with a regression gate, which is
how WM-2 already works; and the plug-in pattern exists twice in the codebase already. Decided at P2.2 (G2),
after the programme is chosen, because the programme decides which interfaces are needed at all.

## 4. Cross-cutting architecture questions (for P2.2)
| # | Question | Why it matters | First evidence to collect |
|---|---|---|---|
| AQ-1 | Does the scope resolver (`tools/run_identity/stamp.py`) need to understand injected implementations (a Phase 2 module chosen at run time is not in the static import closure)? | a run of record must name all code it ran (D49's lesson) | list which interfaces are chosen dynamically; consider a declared-implementation field in `producers.json` |
| AQ-2 | Time model: one simulation clock shared by mobility, channel, ledger and revocation, or per-plane clocks with explicit conversions? | D51 is a clock disagreement; I-05 and I-13 are about time | inventory every `time.time()` and block-time read in P1–P4 |
| AQ-3 | Determinism: which planes can be seeded byte-for-byte, and which report ranges (guide 1.1.10)? | B1 (N-18) in WM-2 makes gas seeded or ranged; Phase 2 adds randomness in P0 and P1 | per-interface determinism class written into each ADR |
| AQ-4 | Scale: how many vehicles and RSUs must a build wave support, and does the in-process Hardhat chain stay the ledger at that scale? | I-01, I-07 at corridor scale | a sizing note from the chosen programme |
| AQ-5 | Where do pre-registrations for Phase 2 live: `docs/design/` beside Phase 1's, or `docs/phase2/prereg/`? | one review protocol | decide with WM-P2-1's plan (P2.3) |
