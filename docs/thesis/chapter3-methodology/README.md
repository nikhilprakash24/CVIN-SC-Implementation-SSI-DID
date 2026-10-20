# Chapter 3 — Methodology (Working Draft)

**Status**: working draft. This chapter describes *how* the study was
conducted — its research design, the comparative framework, and the exact
measurement procedures implemented in the repository. It deliberately states
no results (those belong to Chapter 5); every procedure below is tied to the
committed script that implements it so that the method is reproducible and
auditable. Where a method has a limitation, the limitation is stated in place
rather than deferred.

**Design stance**: the guiding principle throughout is *measure, do not
assert*. Each experimental claim in this thesis is produced by an executable
artifact that runs the real implementation and records the observed outcome;
nothing that can be measured is hand-entered, and nothing that is unsupported
is faked. Each section below therefore carries a **Provenance** pointer to the
script and output artifact that realize the method, mirroring the convention
used in Chapter 5.

---

## 3.1 Research Design and Questions

### 3.1.1 Overall design

The study is a **systematic, empirical, comparative evaluation** of nine
blockchain identity standards used as substrates for Self-Sovereign Identity
(SSI) in Connected and Autonomous Vehicles (CAVs). The design is *comparative*
(the same operations, threat model, and compliance checklist are applied to
every standard), *empirical* (conclusions are drawn from executed
measurements, not from specification reading), and *falsifiable* (each research
thrust carries a hypothesis stated so that the collected data can contradict
it).

The nine standards under comparison are ERC-1056, ERC-721, ERC-725,
ERC-725xy (full ERC-725 X+Y account), ERC-735, ERC-1155, ERC-4337, LSP8, and
the thesis's own **CVIN-Combined** hybrid (an ERC-1056 event identity fused
with ERC-735 on-chain claims). The **MOBI VID V2** application profile is
measured alongside the nine as a purpose-built reference, but is not counted as
one of the nine base standards.

### 3.1.2 Research questions, thrusts, and hypotheses

The work is organized around five research thrusts. Four principal research
questions (RQ1–RQ4) frame the headline contributions; a fifth thrust (industry
alignment via MOBI VID) supplies the cross-backend portability question. Each
thrust pairs a research question with a falsifiable hypothesis and a defined
data-collection method.

| Thrust | Research question | Hypothesis | Method (this chapter) |
|---|---|---|---|
| **T1 — Performance (RQ1)** | How do the nine standards compare on gas cost for identical vehicle-identity operations? | **H1**: minimal-state standards (ERC-1056) are ≥10× cheaper than rich-state standards (ERC-725/735) for identity creation/update, trading on-chain expressiveness. | §3.3 gas measurement |
| **T2 — W3C compliance (RQ3)** | Can blockchain-rooted identities be lifted to W3C DID Core v1.0 + VC Data Model v2.0 conformance, and where do structural mismatches remain? | **H2**: ≥90% aggregate compliance is achievable through a resolution/translation layer. | §3.6 compliance checker |
| **T3 — Real-time V2V (RQ4)** | Can identity establishment + credential verification fit the V2V safety latency envelope (~100 ms end-to-end)? | **H3**: off-chain verification of pre-issued credentials (signature check, no chain round-trip) meets the budget; designs needing on-chain reads at message time do not. | §3.4 V2V harness |
| **T4 — Industry alignment (MOBI VID)** | Can MOBI VID I (birth certificate) and VID II (lifecycle events) be realized on multiple standards, and which backend fits best? | **H4**: MOBI VID's event model maps most economically onto event-log standards and most faithfully onto claim-based standards; the hybrid dominates the fidelity-per-gas frontier. | §3.7 backend sweep |
| **T5 — Security (RQ2)** | Which architecture best resists the V2X threat model (Sybil, impersonation, replay, forgery, privacy leakage)? | **H5**: no single standard dominates; standards occupy a security/performance Pareto frontier, and the hybrid sits on it. | §3.5 security analysis |

The methods in §3.3–§3.7 are constructed so that each hypothesis is tested by a
concrete, re-runnable procedure whose output either supports or contradicts it.

### 3.1.3 Experimental platform

All on-chain measurements are produced on the **Hardhat in-process EVM network**
(`chainId 31337`) compiled with **solc 0.8.24**, the optimizer enabled (200
runs) and `viaIR` codegen, against **OpenZeppelin 5.0.2**. All off-chain
cryptographic measurements run under **Python 3.11** with `coincurve`-backed
secp256k1 (`eth-account`) and the `cryptography` library's NIST P-256
primitives. The rationale for a local, controlled EVM (rather than a public
chain) as the *primary* measurement environment, together with the design of
the public-testnet validation that witnesses it, is given in §3.3.3 and
revisited as a threat to validity in §3.8.

**Provenance**: `4_comparison-framework/results/gas_benchmark.json:metadata`
records the compiler, optimizer, library version, and network for every gas
run; `cv2x-testbed/sumo/results/v2v_latency.json:notes` records the crypto
backend and what is real versus simulated for the V2V runs.

---

## 3.2 The Comparative Framework: an Identical Operation Set

The central methodological device that makes nine heterogeneous standards
comparable is a **canonical operation set** — a fixed list of vehicle-identity
lifecycle operations that every standard must express, measured identically
across all of them. Without such a fixed set, a gas comparison would compare
different work on each standard and would be meaningless.

### 3.2.1 The canonical operations

Each standard is exercised over the same operation set:

1. **deployRegistry** — one-time shared-infrastructure deployment (where the
   standard uses a shared registry rather than per-identity contracts).
2. **createIdentity** — bring a vehicle identity into existence.
3. **updateAttribute** — mutate a vehicle attribute (e.g. rotate a key, write
   a VIN, append a service record).
4. **addDelegateOrClaim** — add a delegate (verification-key authorization) or
   anchor an on-chain claim, whichever the standard natively expresses.
5. **revoke** — revoke a key/claim/credential.
6. **transferOwnership** — transfer control of the identity to a new owner.

A seventh operation, **updateAttributeVia4337**, exists only for ERC-4337: it
routes the same `setAttribute` through the EntryPoint as a `UserOperation` so
that the account-abstraction *indirection overhead* can be isolated as a delta
against the direct call.

### 3.2.2 Mapping heterogeneous standards onto one operation set

Because the standards differ structurally (event-log registries, per-identity
proxy contracts, NFTs, multi-token credentials, smart accounts, claim
holders), the operation set is realized on each standard's **native primitive**
and the mapping is documented honestly per cell. For example, `createIdentity`
is an implicit zero-cost DID plus a first `setAttribute` on ERC-1056, a
`mintVehicle` on ERC-721/LSP8/ERC-1155, a full per-vehicle contract deployment
on ERC-725/ERC-725xy/ERC-735, and a smart-account deployment on ERC-4337.
`updateAttribute` on standards with no key/attribute model (ERC-721, ERC-735,
ERC-1155) is mapped to the *closest analogue* (a service record, a same-size
claim rewrite, a token-URI override) and the note field records that this is an
analogue, not a like-for-like operation.

### 3.2.3 Handling "not supported" — null, never faked

When a standard genuinely lacks an operation, the measurement records a
**null** gas value with a note explaining the structural absence — it is never
substituted with a fabricated number or a misleading proxy. In the code this is
the `unsupported(notes)` helper, which emits `{ gasUsed: null, txCount: 0,
notes }`. Examples that resolve to null include ERC-725xy `addDelegateOrClaim`
and `revoke` (ERC-725 has no native delegate/claim model and no identity-level
revocation primitive) and LSP8 `addDelegateOrClaim` (this representative LSP8
omits operator authorization and has no claim model). Setup transactions that
are prerequisites but not the operation under test (role grants, issuer
authorizations, wallet funding) are executed but **excluded** from the reported
operation gas, so each figure is the cost of the operation itself.

**Provenance**: the operation set, the per-standard mapping, and every note are
defined in `1_blockchain-identity/scripts/benchmark_gas.js`; the canonical
operation list and the "null = unsupported" contract are recorded in
`gas_benchmark.json:metadata.operations` and `:metadata.notes`.

---

## 3.3 Gas Measurement Method (T1 / RQ1 → H1)

### 3.3.1 Exact gasUsed, not estimates

Gas is measured as the **exact `receipt.gasUsed`** of a single representative
transaction per operation, obtained by awaiting the transaction receipt on the
in-process EVM (`gasOf()` in the benchmark). This is the ground-truth quantity
the EVM charges — not a gas-reporter estimate, not a static analysis, and not a
fiat cost. For deployment operations the `deploymentTransaction().wait()`
receipt supplies the deploy gas. The benchmark writes one JSON cell per
(standard, operation) carrying the gas value, the transaction count, and the
explanatory note.

### 3.3.2 Determinism and the N=30 reproducibility protocol

EVM gas is **deterministic**: for a fixed contract, fixed calldata, and fixed
pre-state, `gasUsed` is exactly reproducible from one execution to the next.
The statistical question is therefore not "what is the noise band" (there is
none in the usual sense) but "are the single-run point estimates stable, or
could a given figure be a one-off fluke of ordering or calldata?" The
reproducibility protocol answers this empirically:

- The full nine-standard benchmark is re-run **N = 30** times, each on a fresh
  in-process network.
- For every (standard, operation) the 30 `gasUsed` values are aggregated;
  min, max, median, and population standard deviation are recorded, and a cell
  is flagged `deterministic` iff min == max.
- For deterministic gas the 95% confidence interval **collapses to the point
  value** (CI width 0); the driver records the `[min, max]` envelope so that
  any cell exhibiting variance (which would necessarily be calldata- or
  state-ordering-driven) is surfaced explicitly rather than hidden.

To make this determinism argument airtight, the benchmark uses **fixed
signing keys** for any operation whose calldata depends on a signature (e.g.
the CVIN-Combined claim issuer and the MOBI attestation signer are constructed
from hard-coded private keys, *not* Hardhat's rotating default accounts), so
that the calldata zero-byte counts — and therefore `gasUsed` — are stable
across runs. Byte-identical `gasUsed` across all 30 runs is thus the *expected
and desired* result, and is itself the reproducibility evidence an examiner
would ask for.

### 3.3.3 Public-testnet (Sepolia) validation as a witness

A separate harness validates that the local numbers **reproduce on a real
public network**. Because gas is a function of the opcodes executed and is
identical across EVM chains for identical bytecode and calldata, a matching
`gasUsed` on Sepolia (chainId 11155111), recorded with a real transaction hash
that anyone can verify on a public block explorer, is evidence that the local
measurements are real rather than an artifact of the local network. This is
explicitly a **witness of the measurements, not a performance or latency
sample**.

The harness mirrors the benchmark operation-for-operation and, for each
operation, records the on-chain `gasUsed`, the committed local baseline, and
their delta. It is network-agnostic: on the Hardhat/localhost network it runs
as a delta-zero self-test; on Sepolia it performs the real validation. A
calldata tolerance of 100 gas absorbs the few-dozen-gas difference that a
differing 20-byte target address or 65-byte signature can introduce (intrinsic
calldata cost is 4 gas per zero byte versus 16 per non-zero byte), while a real
execution-path mismatch — which would be hundreds to thousands of gas — would
exceed it and fail the check. By default the harness validates a
thesis-critical subset of three standards (ERC-1056, ERC-725xy, CVIN-Combined),
extensible via an environment variable.

**Honest scope**: the Sepolia harness exists and is exercised in dry-run mode,
but the *real* public-network run requires a funded test key and an RPC
endpoint (gated in the preflight with actionable guidance) and has **not yet
been executed** at the time of writing; this is carried as a threat to
validity in §3.8 and as an open item in the project's risk register.

**Provenance**: gas benchmark —
`1_blockchain-identity/scripts/benchmark_gas.js` →
`4_comparison-framework/results/gas_benchmark.json`; determinism driver —
`4_comparison-framework/performance-metrics/run_gas_stats.py` →
`gas_benchmark_stats.json`; public-testnet witness —
`1_blockchain-identity/scripts/validate_sepolia.js` →
`sepolia_validation.json` (with `SEPOLIA_VALIDATION.md`).

---

## 3.4 Real-Time V2V Method (T3 / RQ4 → H3)

### 3.4.1 What is being measured

The V2V study measures the **real cryptographic cost of identity verification
inside a V2V message path**, for two populations running side by side:

- **PKI baseline** — IEEE 1609.2-style pseudonym certificates. Every Basic
  Safety Message (BSM) is signed at send and verified at receive with **real
  ECDSA over NIST P-256**. First contact additionally validates the pseudonym
  certificate chain against the CA (signature, validity window, CRL).
- **SSI population** — each vehicle holds an Ethereum secp256k1 key, a
  `did:ethr` DID, and a **W3C V2VSafetyCredential** issued through the
  canonical VC layer. BSMs are signed per-message with **EIP-191** personal
  signatures; first contact performs a full Verifiable Credential verification
  (structure, validity window, revocation, issuer-signature recovery,
  subject/DID binding).

All signing, signature verification, certificate-chain validation, and VC
verification are **real**; latencies are captured with `time.perf_counter()`
around the actual cryptographic calls. There are no simulated or injected
latencies anywhere in the message path.

### 3.4.2 Cold versus warm distinction

The method deliberately separates two verification regimes because they cost
very differently and only one recurs at message rate:

- **Cold** (first contact with a peer): the full path — VC verification (SSI)
  or certificate-chain + CRL validation (PKI) — after which the peer's signing
  key/address is cached.
- **Warm** (every subsequent message): a signature check against the cached
  peer — EIP-191 recovery + cached-address comparison (SSI) or an ECDSA verify
  against the cached certificate key (PKI).

Because a vehicle exchanges many messages with each neighbour over an
encounter, the **warm** figure is the one that must clear the per-message
budget, while the **cold** figure bounds the one-time establishment cost. The
verdict compares measured latency against a **100 ms** end-to-end V2V budget
(SAE J2945/1-derived) and a **10 ms** per-message signature-check target.

### 3.4.3 The seeded N=30 protocol with bootstrap confidence intervals

Unlike gas, wall-clock latency *is* noisy, so it is treated statistically:

- The core simulation (`sumo_identity_integration.py --simulate`) is driven
  **N = 30** times as **independent subprocesses**, one per seed 1..30 (fresh
  interpreter, fresh crypto state, fresh mobility RNG each run).
- Each run reports a per-population, per-metric (sign / cold / warm) **median**
  latency; the driver then aggregates **across** the 30 per-run medians,
  reporting the across-run median, mean, p95 (nearest-rank of the per-run
  medians), and a **95% confidence interval of the median via a 10,000-resample
  percentile bootstrap** with a fixed bootstrap seed for reproducibility.
- Integrity totals (messages sent/verified, verification failures) are summed
  across all runs.

Reporting a CI of the median over independent seeded runs turns the latency
claim from a single-sample assertion into a statistically defensible interval,
directly answering the "latency claims challenged at defense" risk.

### 3.4.4 Injected-attack validation

Correctness of the verification path is validated by **injecting attacks** each
run and asserting they are caught: (1) a tampered PKI BSM (payload modified
after signing), (2) a tampered SSI BSM (position falsified after signing), and
(3) an uncredentialed SSI sender (valid key, no credential). These are the
*only* verification failures the benign flow should ever produce, so the
aggregate failure count is expected to equal exactly 3 × N — a differential
check that simultaneously confirms zero false negatives (attacks always caught)
and zero false positives (benign messages never rejected).

### 3.4.5 Simulation model and honest scope

The V2V flow rides on a mobility model: with a SUMO binary present the code
drives real SUMO/TraCI mobility; in `--simulate` mode (used for the reported
runs) a persistent kinematic model places vehicles on a three-lane, 5 km
highway. BSMs broadcast at 10 Hz on a 100 ms step; a neighbour is any vehicle
within a 300 m reception radius (capped at the eight nearest receivers per
broadcast). Two safety applications (forward-collision warning; emergency
electronic brake light) ride on the verified message flow to exercise the path
under realistic event patterns.

The scope is stated honestly and is narrow by design. What is **real**: all
cryptography and its timing. What is **simulated / excluded**: vehicle mobility
(in `--simulate` mode, no SUMO binary), and — importantly — the **radio, MAC,
and network stack**. BSMs are delivered in-process; there is no channel loss,
propagation delay, MAC contention, or queueing. The reported figures therefore
bound the **cryptographic** verification cost — the open question this thrust
addresses — and are *not* an end-to-end network latency, in which the network
stack would be the dominant term. Runs are executed serially on a single
uncontended host, so absolute latencies are hardware-dependent.

**Provenance**: measurement core —
`cv2x-testbed/sumo/sumo_identity_integration.py` →
`results/v2v_latency.json`; multi-run statistics —
`cv2x-testbed/sumo/run_v2v_stats.py` → `results/v2v_latency_stats.json` (whose
`method` and `caveats` fields record this protocol and its limits verbatim).

---

## 3.5 Security-Analysis Method (T5 / RQ2 → H5)

The security analysis uses a deliberate **two-lens design** so that each lens
covers what the other cannot.

### 3.5.1 Lens 1 — executable revert suite

The first lens is an **executable attack suite** of Mocha scenarios
(`test/security/securityScenarios.test.js`). Each scenario deploys the real
contract on the in-process EVM, stands up a legitimate victim identity, then
fires a concrete **adversarial transaction** and asserts that it **reverts**
(is DEFENDED). Crucially, every offensive assertion is paired with a
**differential control**: the *same* operation performed by the *authorized*
party is asserted to **succeed** (PASS), and where meaningful a protected-state
invariant is checked (e.g. the attacker's delegate was never installed; the
owner is unchanged). This control rules out the trivial failure mode in which a
scenario "passes" only because the operation reverts for everyone.

These are ordinary green Mocha tests: the suite stays green *because* the
contracts defend, so a genuine regression would flip a cell to VULNERABLE and
**fail CI as a real finding**, never a faked one.

### 3.5.2 Attack taxonomy

Each standard is probed across a STRIDE-flavoured taxonomy of attack classes,
applied uniformly:

- **unauthorizedIssuance** — Spoofing: fabricate an identity without the
  issuing role/authority.
- **unauthorizedAttributeWrite** — Tampering: write attributes/records on an
  identity the attacker does not control.
- **unauthorizedDelegateOrClaim** — Spoofing/Elevation: install a forged
  delegate or anchor a claim with a forged issuer signature.
- **unauthorizedRevocation** — Denial of Service: revoke a victim's
  key/claim/credential.
- **identityHijack** — Elevation of Privilege: seize ownership/control (key
  rotation, token theft, recovery abuse).
- **signatureReplay** — Replay: reuse a consumed signed meta-transaction or
  `UserOperation`.

Where an attack class does not apply to a standard's surface (e.g.
`signatureReplay` on a standard exposing no signed/relayed operation, or
`unauthorizedIssuance` on a permissionless self-sovereign registry), the cell
is recorded as **N/A with a documented reason**, not silently omitted and not
counted as a defended cell.

### 3.5.3 Lens 2 — threat matrix

The second lens is an analytical **threat matrix** that extends beyond the
pass/fail dimensions a revert test can express, to properties that require
reasoning about economics and data exposure: **Sybil resistance** (using
`createIdentity` gas from the T1 benchmark as a Sybil-cost proxy), **key
compromise / recovery** availability, and **on-chain PII / VIN leakage**. Each
matrix cell records not only the outcome (DEFENDED / PARTIAL / VULNERABLE /
N/A) but the **method** by which it was reached: `executed` (a real transaction
or verification was run and observed) versus `reasoned` (a structural absence
argued from verified source, e.g. "no recovery primitive exists"). This keeps
the honest distinction between what was demonstrated on-chain and what was
established by source inspection.

The orchestrator also executes the **off-chain** counterpart attacks against
the W3C VC/VP layer (forged credential, replayed presentation, stolen-credential
replay by a non-holder, selective-disclosure privacy), merging that row into
the same matrix so the on-chain and off-chain surfaces are compared side by
side.

**Provenance**: Lens 1 —
`1_blockchain-identity/test/security/securityScenarios.test.js` (+ its
`attackHarness`), run under `npx hardhat test`; Lens 2 orchestrator —
`4_comparison-framework/security-analysis/attack_scenarios.py` (which invokes
the on-chain `scripts/security_scenarios.js`) →
`security-analysis/results/security_matrix.json` and `security_comparison.tex`.

---

## 3.6 W3C Compliance Method (T2 / RQ3 → H2)

### 3.6.1 An executable checker, not a self-scored checklist

Compliance is measured by an **executable checker**
(`w3c_compliance_checker.py`) in which *every* non-qualitative check runs the
actual DID resolver or VC stack and records the observed outcome — nothing is
hardcoded to PASS. A check function returns a notes string (⇒ PASS) or an
explicit `(status, notes)` tuple; a raised assertion or exception is recorded
as **FAIL**. This design forecloses the "compliance self-scored" criticism: a
check cannot pass unless the implementation actually exhibits the required
behaviour.

The checker exercises W3C **DID Core v1.0** against the four-method resolver
(`did:ethr`, `did:nft`, `did:key`, `did:mobi`) and W3C **VC Data Model v2.0**
against the issuer/holder/verifier pipeline, including verifiable presentations
and selective disclosure.

### 3.6.2 Negative checks are first-class

A property that cannot fail is not being tested, so the checker gives
**negative checks first-class status**: forged, tampered, expired, and revoked
credentials must be *rejected*; replayed, wrong-audience, and stolen (non-holder)
presentations must be *rejected*; malformed and unsupported-method DIDs must
produce resolution *errors*. Each such check asserts both that the bad input is
refused *and* that the rejection cites the correct reason (e.g. a tampered
claim fails specifically on signature recovery, an expired credential on the
temporal check).

### 3.6.3 The ≥90% gate and how deviations are counted

The executable score is `(PASS + 0.5·PARTIAL) / executed`, computed over the
executed checks only; the ten SSI-principle items are assessed **qualitatively
and explicitly excluded** from the numeric score. The checker exits 0 iff the
score is **≥ 90%**, so the compliance gate is enforceable in CI rather than
asserted in prose.

Known deviations are **executed and honestly counted as FAIL**, not hidden or
argued away. Two are built in as deliberate deviations: (1) proof
canonicalization uses deterministic sorted-key JSON rather than URDNA2015 /
RDFC-1.0 RDF canonicalization, and (2) the cryptosuite
(`eip191-secp256k1-recovery-2024`) is thesis-defined (Ethereum-native,
offline-verifiable) rather than a W3C-registered Data Integrity cryptosuite.
The corresponding checks actively prove which canonicalization and cryptosuite
the stack really uses and then return FAIL — so the headline percentage already
*charges* the thesis for these deviations rather than flattering itself.

**Provenance**: `cv2x-testbed/scripts/w3c_compliance_checker.py` →
`w3c_compliance_report.json`, exercising
`2_w3c-ssi-layer/verifiable-credentials/` and
`2_w3c-ssi-layer/did-resolution/`.

---

## 3.7 MOBI VID Multi-Backend Method (T4 → H4)

### 3.7.1 Three canonical operations on native primitives

H4 asks whether MOBI VID's application semantics are *portable* across
substrates. The method realizes MOBI VID's **three canonical operations** —
(1) **birth attestation** (VID I: anchor a birth record = VIN hash + cert
hash), (2) **lifecycle event** (VID II: record a maintenance/inspection
event), and (3) **third-party attestation** (a second authorized party attests
to an event) — on **every candidate backend** using that backend's **native
primitives** and the **already-deployed, unmodified contracts** (no new
Solidity is written for the sweep). For each (backend, operation) the real
`receipt.gasUsed` is recorded.

### 3.7.2 Honest fidelity scoring

Gas alone would reward a backend for doing *less*, so each cell also records
**fidelity**: whether the concept is **natively** supported or the mapping is a
**forced/approximate** analogue (`nativeSupport` and `approximate` flags plus a
per-cell note). A backend-level **fidelity score out of 5** counts native
support across five concepts — birth anchoring, lifecycle events, multi-party
attestation, verifiable on-chain claims, and revocation.

The honesty of this scoring is load-bearing and is documented per cell. For
instance, ERC-1056's third-party attestation is marked **non-native**: its
`setAttributeSigned` verifies a signature on-chain but the signer must be the
identity owner (a meta-transaction/relayer pattern), so it cannot express an
*independent* second party; the closest honest on-chain footprint is the owner
authorizing an attester via `addDelegate`, and the note says so. ERC-1155's
third-party attestation is likewise non-native: the measured figure is a second
authorized issuer minting a *parallel* corroborating credential, with no
signature and no linkage to a specific prior event. These approximations are
flagged (`approximate = true`) rather than presented as faithful realizations.

**Provenance**: `1_blockchain-identity/scripts/mobi_vid_backend_sweep.js` →
`4_comparison-framework/results/mobi_vid_backends.json`; tables regenerated by
`4_comparison-framework/performance-metrics/generate_mobi_backend_table.py`.

---

## 3.8 Threats to Validity

The methodology's limitations are stated here in full; several are also noted
in place above and carried in the project risk register.

- **Local versus public chain (T1).** Gas is measured on the Hardhat local
  EVM. Because `gasUsed` is a deterministic function of executed opcodes and is
  identical across EVM chains for identical bytecode and calldata, the
  *comparison* between standards is valid on any chain. Absolute fiat cost
  depends on live gas price and is *not* claimed. The Sepolia witness
  (§3.3.3) is designed to confirm the numbers on a public network but the
  real run has not yet been executed (a funded test key + RPC endpoint are
  required).

- **Network stack excluded from V2V latency (T3).** The measured quantity is
  cryptographic verification CPU time, delivered in-process. Radio propagation,
  channel loss, MAC-layer contention, and queueing are excluded and would
  dominate a real end-to-end budget. The V2V results therefore bound the
  identity-verification contribution, not full message latency.

- **Simulated mobility (T3).** The reported runs use `--simulate` mode with a
  synthetic three-lane-highway kinematic model; the SUMO/TraCI code path exists
  but was not exercised against the SUMO binary in the measurement environment.
  Mobility realism affects encounter patterns (hence the cold/warm mix), not
  the per-operation cryptographic cost.

- **Representative / minimal contracts (T1, T5).** The ERC-4337 EntryPoint and
  the LSP8 implementation are deliberately **minimal research implementations**
  (documented in their contract headers): the EntryPoint omits bundler
  batching, paymasters, deposits, and gas accounting, and this LSP8 omits
  operator authorization and LSP1 universal-receiver hooks. Their gas figures
  are therefore a **lower bound** on a fully featured implementation, and the
  ERC-4337 indirection delta explicitly excludes real-world bundler/mempool
  overhead.

- **Demo-scope items.** MOBI VID's on-chain privacy *architecture* (hash and
  encrypt the VIN on-chain, keep plaintext off-chain) is the thesis claim; the
  specific cipher and, in particular, **VIN-cipher key distribution / HSM
  custody** are out of scope for the testbed. The W3C compliance deviations
  (canonicalization, cryptosuite registration) are documented and counted as
  failures rather than waved away (§3.6.3). MOBI VID cross-backend evidence
  (T4/H4) is measured on the reference plus four alternative backends; where a
  backend cannot express a concept natively, the mapping is flagged approximate
  rather than treated as portability.

---

*Working draft. Every procedure above is realized by the cited script; the
methods are re-runnable with the commands documented in each Provenance note
and summarized in the project getting-started guide.*
