# CVIN-SC Identity Sandbox — System Bring-Up and Experimental Environment

**Build Stage: Environment Bring-Up · v1.1 · June 2026**
*Registry classification: Type B (bring-up sequence) + Type A (§1, §6 prose) → Ch. 4 (reproducibility), Appendix*

This document specifies the experimental environment in which the eight candidate identity systems (O1–O8) are deployed, tested for compliance against the twelve-function minimal SSI specification (IMinimalSSI), and exercised in identity-based transaction scenarios — including the end-to-end secure identity-to-identity (I2I) communication scenario that constitutes the core demonstration of this work. It is written in the style of a repository README so that every result in the evaluation chapter is reproducible from a clean machine, but its substance serves as the reproducibility section of the thesis: the environment, the bring-up sequence, the trace format, and the criteria for admitting an implementation into the evaluation are all normative here.

---

## 1. Purpose and design rationale

The sandbox is a two-layer, trace-driven environment:

**Layer 1 — Execution sandbox (ground truth).** A single Hardhat project in which all eight implementations are deployed against the shared `IMinimalSSI` interface. Scenario scripts execute real transactions against a local EVM and emit structured JSONL execution traces (`traces/SCHEMA.md`): transaction hash, minimal-function ID (F1–F12), acting identity, gas used, events, and revert reasons. Traces are the evidentiary artifacts of the thesis — every quantitative claim in Chapter 4 is reproducible by re-running a scenario and diffing the trace.

**Layer 2 — Identity Sandbox Explorer (visualization).** A React artifact that replays traces rather than simulating, rendering identity cards (DID, keys, delegates, credentials with revocation state), a transaction timeline, the I2I secure-channel handshake, and a 12-function coverage tracker. Built in the next pass; the trace schema is the contract between the layers.

The separation exists because a pure visualization sandbox cannot defend gas or ordering claims, and a pure execution sandbox produces nothing demonstrable. Decoupling via traces makes Layer 1 citable and Layer 2 presentable without either blocking the other.

## 2. Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Node.js | ≥ 20 | LTS recommended |
| npm | ≥ 10 | bundled with Node |
| Hardhat | 2.x | installed locally by Step 1 |
| solc | 0.8.24 (solc-js) | installed via npm; no binary download needed |

No global installs and no network access beyond the npm registry are required. In restricted networks where `binaries.soliditylang.org` is unreachable, `hardhat.config.js` already overrides the compiler-acquisition subtask to use the npm-installed solc-js — this keeps the environment fully reproducible inside CI sandboxes and air-gapped lab machines.

## 3. Repository layout

```
cvin-sandbox/
├── contracts/
│   ├── interfaces/
│   │   ├── IMinimalSSI.sol        # the 12-function spec (normative)
│   │   └── ISetA/ISetB/ISetC.sol  # Set decomposition (compile-checked coverage)
│   ├── implementations/
│   │   ├── O1_ERC1056.sol         # reference implementation (complete, 12/12 passing)
│   │   └── O2..O8_*.sol           # port targets (headers in place; see §5)
│   └── credentials/               # Set B pairing adapters (AnonCreds/SD-JWT anchors; Stage 19)
├── test/
│   └── compliance.js              # unified 12-test suite, parameterized over O1–O8
├── scenarios/
│   └── run_i2i.js                 # S1: E2E secure I2I channel, 12/12 function coverage
├── traces/
│   └── SCHEMA.md                  # JSONL trace format (Layer 1 → Layer 2 contract)
├── explorer/                      # Layer 2 visualizer (next pass)
├── BUILD_DIRECTIONS/              # CLAUDE.md companion: BUILD_PLAN, BUILD_LOG
├── CLAUDE.md                      # standing instructions for the Claude Code CLI agent
├── docs/
│   ├── ARCHITECTURE.md            # architect reference (sets, families, scenarios)
│   ├── FINDINGS.md                # measured deviations log
│   └── BRINGUP.md                 # this document
└── hardhat.config.js              # incl. offline solc-js override
```

## 4. Bring-up sequence

Each step lists the command and the expected output, README-style. A clean machine reaching Step 5's output reproduces the environment exactly.

**Step 1 — Install.**
```
npm install
```
Expected: hardhat 2.x, @nomicfoundation/hardhat-toolbox, solc 0.8.24 installed; no audit failures relevant to the toolchain.

**Step 2 — Compile.**
```
npx hardhat compile
```
Expected: `Compiled 9 Solidity files successfully (evm target: paris)`.

**Step 3 — Port implementations.** O2–O8 are ported from the Build Stage 12 session outputs into `contracts/implementations/`, one contract per standard, each implementing `IMinimalSSI` with the native patterns of its standard (soulbound mint for ERC-721, key-value store for ERC-725, validation-key promotion for ERC-4337, registry pattern for ERC-8004, nymTx adapter for LFDT/Indy-on-Besu). An implementation is admitted to the evaluation when, and only when, it passes Step 4 unmodified — functions must not be stubbed to pass.

**Step 4 — Compliance.**
```
npx hardhat test
```
Expected (per implementation enabled in `test/compliance.js`):
```
O1_ERC1056 — IMinimalSSI compliance
  ✔ test_01 createDID returns non-zero id; DID resolvable
  ✔ test_02 resolveDID returns empty for non-existent DIDs (no revert)
  ...
  ✔ test_12 validDelegate false after expiration
12 passing
```
The twelve tests implement §4.1 of the formal specification verbatim. The suite is implementation-agnostic: adding a contract name to `IMPLEMENTATIONS` runs the identical tests against it, which is what makes the cross-option comparison in Chapter 4 a controlled experiment.

**Step 5 — Scenario S1: end-to-end secure I2I communication.**
```
IMPL=O1_ERC1056 npx hardhat run scenarios/run_i2i.js
```
Expected output (abridged; gas figures from the verified v1.0 run):
```
[1]  deploy: O1_ERC1056
[2]  createDID: gas=178935            (Registry)
[5]  issueCredential: gas=130163      (MOBI VID → IdentityA)
[9]  addDelegate: gas=54227           (OBU, sigAuth, 3600s)
[11] verifyCredential: valid=true     (mutual auth, B checks A)
[15] createPresentation: gas=62441    (VP challenge binds channel payload)
[16] secure-channel: ECDH P-256 + AES-256-GCM (off-chain; VP anchors payload)
[17] revokeCredential: gas=32980      (Registry revokes A mid-session)
[18] verifyCredential: valid=false revoked=true → channel torn down
[21] deactivateDID: gas=55127
[22] done: functions covered: 12/12
Trace written: traces/i2i_O1_ERC1056_<ts>.jsonl
```
S1 extends the Stage 14 pipeline (which exercised 8/12 functions in the positive lifecycle) with the four negative-lifecycle functions — `revokeCredential`, `removeVerificationMethod`, `updateDID`, `deactivateDID` — by injecting a mid-session trust break: the issuer revokes IdentityA's credential while the AEAD channel is open, and IdentityB's next verification rejects the sender. One scenario therefore covers 12/12 minimal functions, the hybrid on/off-chain transport stance (only lifecycle events and anchors on-chain; ECDH key agreement and AES-256-GCM payload exchange off-chain), and the revocation-propagation failure mode flagged in the threat model.

**Step 6 — Visualize.** Load the trace into the explorer (next pass). Until then, traces are inspectable directly; the schema is stable.

**Known deviation (recorded honestly).** The verified O1 run shows `createDID` at ≈162–179K gas, above the formal spec's <100K ERC-1056 target. The cause is the explicit-DID adaptation (storage write of the Identity struct) versus pure event-sourced ERC-1056 where identity creation is implicit and free. This is an optimization item for the Stage 15 benchmark pass, and a finding in itself: interface uniformity has a measurable gas cost on the lightest standard. The spec's event-name collision (`CredentialRevoked` declared as both error and event) was also corrected to `CredentialRevokedEvent` — log as a spec erratum for the formal document's v1.1.

## 5. The eight implementations and their function sets

| # | Standard | Identity model | Set A (8 fns) | Set B (4 fns) | Status |
|---|---|---|---|---|---|
| O1 | ERC-1056 | Address/event-sourced DID (did:ethr) | Native | Anchor pattern | **12/12 passing** |
| O2 | ERC-721 | Soulbound NFT | Native-partial | Anchor pattern | Port (Stage 12) |
| O3 | ERC-725 | Proxy account, key-value | Native | Anchor pattern | Port (Stage 12) |
| O4 | ERC-725xy | + ERC-735 claims (LUKSO) | Native | Claims-assisted | Port (Stage 12) |
| O5 | ERC-1155 | Multi-token soulbound | Partial | Anchor pattern | Port (Stage 12) |
| O6 | ERC-4337 | Smart account | Native + recovery | Anchor pattern | Port (Stage 12) |
| O7 | ERC-8004 | Agent identity + registries | Native + trust | Anchor pattern | Build (new) |
| O8 | LFDT | Indy-on-Besu adapter | Adapter | AnonCreds-native | Build (new) |

Set A = DID lifecycle + key management (F1–F4, F9–F12), directly evaluable against ERC standards. Set B = credential layer (F5–F8), which no ERC natively provides — the central finding driving the hybrid architecture. In the sandbox, Set B is satisfied by the shared on-chain anchor pattern (content hash on-chain, credential off-chain), with format-specific adapters (`contracts/credentials/`) added in Stage 19.

## 6. LFDT integration: graduated base and incubation projects

The O8 lane and the Set B credential layer are where LF Decentralized Trust projects enter the sandbox. The division of labor matters architecturally: **graduated LFDT projects supply infrastructure under Set A; incubating projects supply the credential, privacy, and agent layers above it.** None of the incubation projects competes with the eight options as a Set A identity anchor — they are Set B/Set C suppliers, which is itself evidence for the extension-not-replacement thesis.

**Graduated base.** Indy (identity ledger; source of the nymTx pattern O8 adapts), Besu (the EVM client targeted for Stage 18's Tier-2 latency runs; the Indy-on-Besu convergence is the bridge argument from RPart #4), Fabric, and Trust over IP (governance architecture).

**Incubating projects mapped to sandbox roles:**

| Project | What it is | Sandbox role | Stage |
|---|---|---|---|
| **AnonCreds** | Most widely used VC format; ZKP-capable (CL, BBS+ direction) | Primary Set B pairing for O8; selective-disclosure baseline for `createPresentation` | 19 |
| **Identus** | SSI platform (ex-Atala PRISM); DIDComm v2 agents, AnonCreds, Cardano VDR | Issuer/holder/verifier agent roles in I2I scenarios; the non-EVM-VDR adapter case for the ledger-agnostic claim | 19 / inventory v3 |
| **CREDEBL** | DID/VC management platform (AYANWORKS); integrates ToIP, Indy, Aries lineage | Platform-layer reference; its national-scale deployments (Bhutan NDI, Papua New Guinea SevisPass) are production evidence for the Ch. 4 real-world section | 17 update / Ch. 4 |
| **Paladin** | Programmable privacy for EVM | Privacy-layer candidate where ZKP presentations must verify on-chain on Besu | 19 |
| **Caliper** | Blockchain benchmark framework | The throughput/latency harness for Stages 15/18 — the memos already commit to "Caliper-style harnesses"; using LFDT's own tool strengthens the methodology section | 15 / 18 |
| **Minokawa** | ZK-native smart contract language | Watchlist; relevant if on-chain ZKP verification costs dominate in Stage 19 | watch |

**Adjacent ecosystem notes for the inventory v3.** Aries agent code now lives at the OpenWallet Foundation as ACA-Py (production SSI agent; Indy/AnonCreds lineage) — the inventory's Aries row needs this organizational correction. Two new efforts are directly relevant to the agentic chapter: the Hiero Heka identity platform (LFDT-hosted, explicitly targeting decentralized identity for agentic AI) and the First Person Project (verifiable relationship credentials / proof-of-personhood across LFDT, ToIP, DIF, OWF). Both belong in Chapter 5's positioning of the Stage 31 agent identity wrapper: they confirm the agent-identity direction is becoming an ecosystem priority, and they sharpen the novelty claim — the thesis contribution is the *minimal-function compliance and benchmark layer* beneath such platforms, which none of them specifies.

## 7. Roadmap from this environment

The roadmap is now formalized as work orders WO-0–WO-9 in `BUILD_DIRECTIONS/BUILD_PLAN.md` (the CLI handoff). Summary view:

| Next | Work | Output |
|---|---|---|
| 1 | Port O2–O6 from Stage 12; build O7 (ERC-8004), O8 (Indy-on-Besu adapter); enable all in `compliance.js` | 8 × 12 compliance matrix |
| 2 | Identity Sandbox Explorer (Layer 2) replaying `traces/*.jsonl` | React artifact |
| 3 | Stage 15 benchmarks: run S1 across all 8, gas table per function per option (Caliper harness where applicable) | Ch. 4 tables |
| 4 | Stage 19 credential adapters (`contracts/credentials/`): AnonCreds, SD-JWT, BBS+ anchoring | Set B analysis |
| 5 | Stage 18 latency: S1 against Besu QBFT vs local vs L2 targets, three-tier mapping | Ch. 4 |

## 8. Registry entry (for Content Block Registry v1.1)

| Content Block | Type | Source | Chapter | Readiness | ~Words |
|---|---|---|---|---|---|
| Environment Bring-Up doc (§1, §6 prose; §4 sequence) | A/B | This stage | Ch. 4, App. | 75% | ~1,900 |
| Sandbox scaffold + O1 reference + compliance suite + S1 scenario | B | This stage | Ch. 4 | 80% | code |
| S1 execution trace (12/12, real gas) | B | traces/ | Ch. 4 App. | 85% | data |
| LFDT incubation mapping (§6) | A | This stage | Ch. 3, 5 | 80% | ~600 |
