# WP 3.1 — In-Depth Profiles of the Nearest Existing Benchmark Artefacts

**Home:** companion paper SP-9 + Ch 7 (Phase 3). **Produced:** 2026-10-31 by Literature Scout (Explore) + Standards Scholar.
**Binds:** `DETAILED_PLAN.md` §3 Phase 3 WP 3.1. **Builds on (do not re-summarize):** `p1/BENCHMARK_GAP.md`
(31 sources; the five axes A1–A5 defined in §0), `p2/COMPARISON.md` §3 (the eight trade-off axes, S1–S10).

**What this pass adds over Phase 1.** Phase-1 WP 1.6 scored 31 sources on the five axes, but its own reading log (§5)
recorded only **3 read in full / at source** (Satybaldy26 in full; W3C DID Method Rubric and W3C DID Core at source);
the other 28 were classified **from abstracts**. This WP goes deeper on the *nearest* artefacts: it reads the actual
artefact where it is free (the test-suite reports, the benchmark repositories and their shipped workload lists, the two
measured papers in full, the NIST guideline text, the EUDI conformance framework), and upgrades the abstract-only ✗/◐
judgements accordingly. §3 is the explicit read-in-full-vs-abstract provenance list that closes the Phase-1 "obj.11"
concern as far as free sources allow.

**The five axes (verbatim from `BENCHMARK_GAP.md` §0).** A1 fixed, shared, reusable workload · A2 admission /
conformance rule (pass/fail or admit/reject) · A3 metrics defined *with* measurement conditions · A4 public reusable
harness (code others run unchanged) · A5 independent reproduction (≥ 1 non-author re-run on record). The sixth,
non-axis property the thesis contributes — **IDTx dependency semantics**: a transaction whose admissibility/effect
depends on *another named identity's state*, evaluated in-transaction (ANALYSIS.md §4.1) — is tracked in its own column.

Legend: ✓ present · ◐ partial · ✗ absent. Each cell carries a one-clause justification tied to a **specific feature
read this pass**. Evidence tag: **[src]** read at the artefact this pass · **[full]** paper read in full this pass ·
**[sec]** secondary only · **[abs]** abstract only (flagged, not upgradable from a free source).

---

## §1 — Per-artefact profiles

### Artefact 1 — W3C DID Method Rubric v1.0 (W3C Group Note) — **[src, read 100k/137k chars this pass]**

**What it is, resolved:** an *evaluation aid*, not a benchmark, and it says so. It exists to "evaluate multiple DID
methods on a feature-to-feature basis"; it is "not intended to be exhaustive" and is "a starting point rather than the
final say." **What it outputs:** a set of *per-criterion response labels* (letters A–D with modifiers like "A-", plus a
free-text note) — deliberately **not** a single number: it avoids "reducing this Evaluation to a single number." The
responses "are not necessarily good or bad," "many of the criteria are subjective," and contributor example figures
"are not presented as objective fact." Example criteria read like a questionnaire: *"Does the Method require network
communications to create a DID?"*, *"How much memory is required for DID resolution?"*, *"How open is participation in
governance decisions?"* Some criteria do ask about throughput/latency, but using **response bins citing other people's
evaluations** (e.g. "Updates on Veres One have been demonstrated at >100 TPS"), not a measurement the rubric performs.

| A1 | A2 | A3 | A4 | A5 | IDTx |
|:--:|:--:|:--:|:--:|:--:|:--:|
| ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

- **A1 ✗** — no fixed operation set; the evaluator picks the use case and which questions to answer ("no requirement to answer all the questions").
- **A2 ✗** — explicitly declines a verdict; the only "MUST reject" language governs registry *submissions*, not DID methods.
- **A3 ✗** — the performance bins quote third-party figures and state measurement conditions nowhere; "not presented as objective fact."
- **A4 ✗** — the registry is JSON files on GitHub; no test harness of any kind is described.
- **A5 ✗** — responses are contributor judgements; no re-run is defined or possible (nothing is run).
- **IDTx ✗** — it is a governance/feature questionnaire about one method; no notion of a transaction gated on another identity.

**obj.11 status:** confirms and sharpens the Phase-1 ✗ row from the full text (the "declines to score" framing is the artefact's own wording).

---

### Artefact 2 — W3C DID Core test suite + VC Data Model 2.0 test suite + DIF interop — **[src, both suites read this pass]**

**DID Core test suite (`w3c.github.io/did-test-suite`) — resolved:** a *conformance/interoperability* report. It maps
normative spec statements to tests and aims to show "all such language has been tested, and is supported by at least 2
independent implementations." The real suites (did-core-properties, did-identifier, did-production, did-resolution,
did-url-dereferencing) check **syntax, document properties, JSON/JSON-LD production (media types e.g.
`application/did+ld+json`), resolution outputs/metadata/errors, and DID-URL dereferencing** — i.e. *can an implementation
create/parse/resolve DIDs and documents per spec*. Admission rule exists: "A suite is considered passing when all
associated tests are passing," with the ≥2-independent-implementations goal. Run time ("Time: 0.899 s") appears but is
incidental, **not** a performance metric.

**VC Data Model 2.0 test suite (`github.com/w3c/vc-data-model-2.0-test-suite`) — resolved:** "interoperability tests for
verifiable credential processors (issuers/verifiers)." It POSTs to live endpoints — `POST /credentials/issue`,
`POST /credentials/verify`, `POST /presentations/verify` — and asserts implementations "do not error" on the VC 2.0
contexts and process `eddsa-rdfc-2022` proofs (Mocha runner). Only **HTTP response codes are checked**; no latency,
throughput, or cost; no explicit numeric threshold beyond "do not error." DIF interop suites sit in the same class
(protocol-profile interoperability), confirmed from the survey framing in `BENCHMARK_GAP` [Mazzocca24] — not re-read
this pass.

| A1 | A2 | A3 | A4 | A5 | IDTx |
|:--:|:--:|:--:|:--:|:--:|:--:|
| ◐ | ✓ | ✗ | ✓ | ✓ (DID Core) / ◐ (VC/DIF) | ✗ |

- **A1 ◐** — a *shared* input set exists (spec statements; issue/verify/present calls) but it is a **conformance** workload, not a performance workload.
- **A2 ✓** — explicit pass rule: DID Core "passing when all associated tests are passing"; VC suite checks HTTP-code conformance of issue/verify/present.
- **A3 ✗** — no latency/throughput/cost and no measurement conditions; only spec-correctness is asserted.
- **A4 ✓** — both suites are public, runnable harnesses (`npx mocha tests/`; the DID-Core runner).
- **A5 ✓ / ◐** — DID Core had **46 implementations** submitted (strong independent participation); VC/DIF interop is ongoing but less consolidated.
- **IDTx ✗** — the nearest properties (`canonicalId`, `equivalentId`, `nextVersionId`) are checked as spec fields, **not** cross-transaction identity dependencies.

**obj.11 status:** upgraded from Phase-1 secondary/spec-level to a direct read of the *actual test-suite reports* — confirms conformance-not-performance and pins the A3 ✗ to "only HTTP response codes are checked."

---

### Artefact 3 — NIST SP 800-63-4 (Digital Identity Guidelines) — **[src, read 100k/191k chars this pass]**

**Resolved:** an *assessment and risk-management requirements framework*, not a measured workload. IAL/AAL/FAL are
**assurance levels** ("Identity Assurance Level (IAL) refers to identity proofing functions"), each mapping to baseline
controls in the companion volumes (-63A proofing, -63B authentication, -63C federation). Compliance is determined by a
**five-step Digital Identity Risk Management process** that organizations "SHALL execute and document," with authorizing
officials requiring "documentation that demonstrates adherence" — i.e. an **auditor/assessor against requirements**, not
a benchmark run. Step 5's "outcomes are performance metrics" but the document "SHOULD adapt and modify this overall
approach" and specifies **no** metric, harness, or workload.

| A1 | A2 | A3 | A4 | A5 | IDTx |
|:--:|:--:|:--:|:--:|:--:|:--:|
| ✗ | ◐ | ✗ | ✗ | ✗ | ✗ |

- **A1 ✗** — no fixed operation set every implementation runs; organizations tailor the DIRM process to themselves.
- **A2 ◐** — an assurance-level *criteria* model exists (IAL/AAL/FAL), but it is satisfied by **documented assessment**, not a pass/fail on a run.
- **A3 ✗** — "the outcomes of this step are performance metrics" is left unspecified; the quantified thresholds are *impact levels*, not latency/throughput/cost.
- **A4 ✗** — a requirements document; no runnable harness.
- **A5 ✗** — nothing is run, so nothing is reproduced; independent *assessments* are per-organization, not a shared re-run.
- **IDTx ✗** — proofing/authn/federation of a subject; no transaction gated on another named identity's state.

**obj.11 status:** upgraded from a DOI/abstract-level mark on SP 800-63B to a direct read of the SP 800-63-4 guideline text; confirms "assessment framework, not measured workload."

---

### Artefact 4 — eIDAS 2.0 / EUDI Wallet conformance (FCAF, ARF) + Large-Scale Pilots — **[src ARF/FCAF page; abs Sokolov full]**

**Resolved from `eudi.dev/latest` + the Sokolov26 abstract:** the EUDI conformance surface is **functional conformance
only**. The ARF landing page describes "Functional Conformance" as *"the conformance assessment framework"* and the
Technical Specifications as "the normative specifications for **interoperability**"; the Reference Implementation is to
"build, test and explore working components." **No performance workload, latency/throughput/cost metric, or benchmark
harness is defined.** Sokolov26 (which audits "FCAF scope") states FCAF/certification "provide increasingly structured
wallet-side evidence" but identifies the gap that there is "no single audited evidence object joining RP registration
and purpose" — i.e. **no rerunnable performance object**; the paper's own 36 frozen synthetic transactions + 17-rule
profile are its *research* artefact and are self-described as "not product conformance or certification." The **Large
Scale Pilots are deployments**, not a shared measured workload (BENCHMARK_GAP [Sokolov26]; not independently re-run).

| A1 | A2 | A3 | A4 | A5 | IDTx |
|:--:|:--:|:--:|:--:|:--:|:--:|
| ◐ | ✓ | ✗ | ◐ | ✗ | ✗ |

- **A1 ◐** — shared functional conformance scenarios against the ARF exist, but there is **no performance workload**.
- **A2 ✓** — certification / functional-conformance assessment is an explicit admit/reject gate (wallet certification).
- **A3 ✗** — conformance is interoperability/compliance; no latency/throughput/cost with pinned conditions.
- **A4 ◐** — a Reference Implementation and conformance tooling exist, but as compliance tooling, not a reusable *performance* harness.
- **A5 ✗** — LSPs are national deployments; no independent re-run of a shared measured object (Sokolov26's own point).
- **IDTx ✗** — RP makes an off-chain, risk-based status decision on a presented credential; no in-transaction gate on another identity.

**obj.11 status:** FCAF/ARF conformance framing upgraded to a source read (confirms functional-not-performance); **Sokolov26 full text remains abstract-only** (free on arXiv but not read in full this pass) — flagged, mark retained.

---

### Artefact 5 — Blockchain benchmarking frameworks (BLOCKBENCH, Caliper, DIABLO) — **[src, repos/docs read this pass]**

**BLOCKBENCH (`github.com/ooibc88/blockbench`) — resolved workload list:** macro-benchmarks **YCSB** (key-value) and
**SmallBank** (OLTP); micro-benchmarks **DoNothing** (consensus), **IOHeavy** and **Analytics** (data-model layer),
**CPUHeavy** (execution). Chains: Ethereum/geth, Parity, Hyperledger Fabric (v0.6/1.4/2.2), Quorum. **No identity,
DID, VC, or identity-gating workload — none of the six touches identity.**

**Hyperledger Caliper (docs v0.7.1) — resolved:** a **bring-your-own-workload** benchmarking *tool*: the user supplies a
workload module via configuration ("Workload Configuration", "Declarative Workloads"); sample benchmarks live in a
separate companion repo. Metrics: transaction/read **throughput**, transaction/read **latency** (min/max/avg/percentile),
and **resource consumption** (CPU/memory/network I/O). **No identity/DID/VC workload shipped; no pass/fail rule** — it
measures and reports only.

**DIABLO (`diablobench.github.io`) — resolved workload list:** six realistic DApp workloads — **Dota 2, FIFA, NASDAQ,
Twitter, Uber, YouTube** — evaluating performance and fault tolerance "on the same ground" (Sydney CSRG + EPFL DCL).
**None involves identity, DID, VC, or identity-gating.** (Gromit/GFBE/BBSF etc. are the same class; not re-read this pass.)

| Artefact | A1 | A2 | A3 | A4 | A5 | IDTx |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| **BLOCKBENCH** | ✓ | ◐ | ✓ | ✓ | ✓ | ✗ |
| **Caliper** | ✗ | ✗ | ◐ | ✓ | ✓ | ✗ |
| **DIABLO** | ✓ | ◐ | ✓ | ✓ | ✓ | ✗ |

- **A1** — BLOCKBENCH/DIABLO ✓ ship *named, fixed* workloads (6 DApps / YCSB+SmallBank+4 micro); Caliper ✗ because the workload is user-supplied.
- **A2** — ◐ for BLOCKBENCH/DIABLO (a run completes/compares but no formal admit/reject gate); ✗ for Caliper (pure measurement).
- **A3** — ✓ BLOCKBENCH/DIABLO define metrics with pinned conditions; Caliper ◐ (metrics defined, conditions user-set).
- **A4 ✓ (all three)** — all are released, runnable harnesses — the strongest axis for this family.
- **A5 ✓ (all three)** — widely re-run; DIABLO has an explicit independent bare-metal re-run [Lebedev23]; Caliper used across many papers [Mazzoni21].
- **IDTx ✗ (all three)** — **confirmed at source: not one of these ships any identity workload, let alone an identity-gating one.** This is the decisive finding for the family.

**obj.11 status:** upgraded from Phase-1 abstract/secondary marks to **direct reads of the shipped workload lists** — the "no identity workload" claim is now evidenced by the enumerated workloads themselves, not inferred from abstracts.

---

### Artefact 6 — SSI/DID performance papers: Satybaldy et al. 2026 (+ nearest others) — **[full, Satybaldy re-read in full this pass]**

**Satybaldy et al. 2026, arXiv 2601.20716 — resolved from full text:** a self-described, **unified cross-platform DID
benchmark** over **Ethereum (ERC-1056/ethr-did), Hedera, XRP Ledger** via reference SDKs. **Workload = the DID lifecycle:**
Create, Resolve, Update, Revoke, Deactivate (Table 1), plus a composite **Full Cycle Operation** aggregating their latency
and cost. **Metrics + conditions (pinned):** latency **normalized by each platform's block/consensus interval**; cost
**normalized by the native value-transfer fee** (mean fees quoted: ETH \$0.04, XRPL \$0.000021, Hedera \$0.0001);
**Metadata-Leakage Score (MLS)**, an entropy-based measure in **bits/operation** under a public-ledger passive-observer
model (sampling 100 transactions). **100 iterations per operation** on a pinned **AWS EC2 c5.4xlarge (16 vCPU Xeon
@3.0 GHz, 32 GiB, Amazon Linux 2023)**, all on **testnets**. **No admission rule** (descriptive/comparative: aims to
"support informed selection and configuration of DID systems"). **Replication package** at
`anonymous.4open.science/r/DID-Research-C147` (scripts, raw results, notebooks) — an **anonymous review-time snapshot,
not a maintained community harness**. **No independent reproduction** (single v1, Jan 2026). **Crucially: every operation
is single-DID lifecycle *administration* — no operation gates a transaction on another named identity's state.**

Nearest others (from `BENCHMARK_GAP` §1b; **abstract-only**, not upgraded — see §3): **Lagos26** (EUDI candidate VC
schemes, open-source suite; credential presentation, not IDTx); **Buldini25** / **DeSalve26** (selective-disclosure
benchmarks; create/verify time + size; no IDTx); **Siqueira23** (Indy/Aries healthcare load; one use case).

| Artefact | A1 | A2 | A3 | A4 | A5 | IDTx |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| **Satybaldy26** | ◐ | ✗ | ✓ | ◐ | ✗ | ✗ |
| **Lagos26 / Buldini25 / DeSalve26** | ◐ | ✗ | ✓ | ◐/✓ | ✗ | ✗ |

- **A1 ◐** — a fixed 5-op lifecycle workload, but tied to **3 specific SDKs** and self-authored, not a published standard others target.
- **A2 ✗** — purely descriptive; no pass/fail or admit/reject threshold anywhere in the full text.
- **A3 ✓** — metrics *and* conditions pinned (100 iters, named EC2 instance, testnets, normalization rules) — the strongest axis for this artefact.
- **A4 ◐** — replication package released, but at an **anonymous 4open.science** URL (review snapshot), not a maintained reusable harness.
- **A5 ✗** — single newly-published study; no non-author re-run on record.
- **IDTx ✗** — Create/Resolve/Update/Revoke/Deactivate is identity *administration*; nothing depends on another identity's state in-transaction.

**obj.11 status:** Satybaldy was already "read in full" in Phase 1; this pass **deepened** it — pinned the exact VM, the
100-iteration conditions, and (new) that the "replication package" is an *anonymous review snapshot*, which is why A4
stays ◐ rather than ✓. Lagos/Buldini/DeSalve/Siqueira **remain abstract-only** (paywalled or not chased) — flagged.

---

### Artefact 7 — Frutuoso et al. 2026 (ERC-3643 / ONCHAINID academic credentials), arXiv 2607.16383 — **[full, read in full this pass — MAJOR upgrade]**

**Resolved from full text — this is the Phase-1 "only measured IDTx-class workload," and the full read materially
refines that mark.** The design composes ONCHAINID (ERC-734/735) with T-REX (ERC-3643); the trusted-issuer registry
becomes an on-chain issuer-accreditation whitelist, and each certificate is "a signed, updatable claim bound to a
student's identity." **Measured operations (Table 4):** deployIdentity, deployClaimIssuer, identity-proxy onboarding,
addTrustedIssuer, addKeyToIdentity, **addClaim** (cold 355,409 gas / warm 122,105), composite issue (518,927), and
**off-chain validation**. **The decisive detail:** the identity-dependency that would make this a true in-transaction
IDTx — the trusted-issuer *accreditation* check — is enforced **off-chain at the client**: *"Accreditation is thus
checked at the client while key authorisation and signature validity are enforced on-chain."* On-chain, `addClaim` is
gated only on the **sender holding an authorised claim key (`onlyClaimKey`)** and the issuer **signature being valid
(`isClaimValid`)** — i.e. on the sender's *own* key/signature, **not** on another named identity's registry state. **No
token-transfer workload is measured** ("uses only the identity, claim, and trusted-issuer components, and no token
transfers"). Latency (Sepolia, n=30): issue median 11.91 s / p95 24.68 s; validate 0.10 s. Baseline: a Blockcerts-style
hash-anchoring registry (45,542 gas), issuance ≈ 11× baseline. **Public repo exists:** `github.com/DiGo-Certify/DiGo-certify-app`
(harness + raw data). No independent reproduction; Slither on 131 contracts is the authors' own.

| A1 | A2 | A3 | A4 | A5 | IDTx |
|:--:|:--:|:--:|:--:|:--:|:--:|
| ◐ | ✗ | ✓ | ◐ | ✗ | ◐ (down from ✓) |

- **A1 ◐** — a bespoke credential lifecycle (deploy/onboard/addClaim/validate), single use case, not a shared spec.
- **A2 ✗** — negative tests exist (issuance by an unaccredited/de-accredited issuer *expected to fail*) but no reported per-test admission rule; the only on-chain `require` quoted caps registry size (`< 50`).
- **A3 ✓** — gas (medians over 30 runs), latency (Sepolia n=30), scalability sweeps and a baseline comparison, all with stated Solidity/optimizer settings.
- **A4 ◐** — a **public repo** (`DiGo-Certify/DiGo-certify-app`) ships the harness + data — this **upgrades the Phase-1 A4 ✗ to ◐** — but it is a one-off app, not a reusable community harness.
- **A5 ✗** — single study; authors' own measurements only.
- **IDTx ◐ (downgraded from the Phase-1 ✓)** — the on-chain gate is on the sender's *own* key/signature; the real identity-dependency (issuer accreditation) is a **client-side** check, so it is **not** an in-transaction gate on another named identity's state. It is the closest *mechanism* to an IDTx but, as measured, the dependency is evaluated off-chain.

**obj.11 status:** **the single most important upgrade this pass.** Phase-1 §5 listed Frutuoso26 as abstract-only yet
scored it IDTx ✓. Reading the full text shows (i) the identity-dependency check is **off-chain at the client**, so the
IDTx mark is **◐ not ✓**; (ii) **no token transfer** is measured (Phase-1 BENCHMARK_GAP §1c said "transfer/claim gated");
(iii) a **public harness repo exists**, upgrading A4 from ✗ to ◐. Three cells corrected from one full read.

---

### Artefact 8 — ERC-3643 / T-REX reference implementation (EIP-3643 + github.com/TokenySolutions/T-REX) — **[src EIP-3643 spec read at source this pass; sec T-REX repo via EIP + public listing]**

**Resolved from the EIP-3643 spec at source — this artefact FALSIFIES the Phase-1/WP-3.1 "absolute absence" claim and
is the reason this pass retracts it.** ERC-3643's `transfer(_to, _amount)` runs, **in the same transaction before value
moves**, `require(_tokenIdentityRegistry.isVerified(_to))` and `require(_tokenCompliance.canTransfer(from, to, amount))`
(spec §Main functions, `transfer` reference body, read at source). `isVerified(_to)` instructs the on-chain Identity
Registry to check that the **receiver's** on-chain Identity (ONCHAINID ERC-734/735) holds the claims required by the
Claim Topics Registry, signed by an issuer in the Trusted Issuers Registry — i.e. the admissibility of the transfer is
**a function of the state of another named identity (the receiver), evaluated in-transaction**, which is the IDTx
definition (`ANALYSIS.md` §4.1) verbatim, enforced **on-chain**. Unlike Frutuoso26 (where accreditation is a client-side
check), here the identity dependency is on-chain. It is **shipped**: the T-REX reference implementation is a public repo
(`github.com/TokenySolutions/T-REX`) with a public functional/unit test suite (Hardhat), audited (Kaspersky, Hacken per
EIP §Security Considerations); the mechanism is deployed at scale (see note on a16z RWA hooks below). **But as a
*benchmark* it is not one:** its test suite is a **functional/conformance unit suite**, not a reusable *performance*
workload — it asserts correctness of eligibility/compliance behaviour, not latency/throughput/cost under pinned
conditions.

| A1 | A2 | A3 | A4 | A5 | IDTx (Id-gate) |
|:--:|:--:|:--:|:--:|:--:|:--:|
| ✗ | ✗ | ✗ | ✓ | ✓ | ✓ (on-chain, shipped) |

- **A1 ✗** — ships a functional/unit test suite, **not** a named, fixed *performance* workload others run to compare cost; no reusable operation set with measurement intent. [src]
- **A2 ✗** — unit tests have correctness pass/fail, but there is **no benchmark admission rule** over performance results (same category as the BENCHMARK_GAP §1c "revert-on-unverified is a contract check, not a benchmark rule"). [src]
- **A3 ✗** — no latency/throughput/cost metric defined with pinned measurement conditions; the suite asserts behaviour, not performance. [src]
- **A4 ✓** — a public, runnable reference implementation + test suite others execute unchanged (`github.com/TokenySolutions/T-REX`). **The harness exists.** [sec]
- **A5 ✓** — the reference suite is run by many independent integrators and the standard is independently deployed at scale; this is a runnable, independently-exercised artefact (not a reproduction of a performance *result*, because no performance benchmark is defined). [sec]
- **IDTx ✓ (on-chain, shipped)** — `isVerified(_to)` + `canTransfer(from,to,amount)` gate the transfer on the receiver's on-chain identity state, in-transaction, before value moves (EIP-3643 spec at source). **This is an in-transaction identity-gated-transfer workload mechanism, shipped.**

**obj.11 status:** **new artefact, read at source this pass (EIP-3643 spec).** This is the decisive correction: the
in-transaction, on-chain identity-gated transfer the thesis targets **exists and is shipped**. What T-REX does *not*
provide is a complete A1–A5 *benchmark* packaging it as a reusable, admission-gated, metric-defined performance workload.

---

### Artefact 9 — ERC-1404 / CMTAT (restricted-transfer security tokens; github.com/CMTA/CMTAT) — **[sec ERC-1404 mechanism; src Taurus/CMTA Sepolia measurement read at source this pass]**

**Resolved — a second on-chain identity/allowlist-gated-transfer example, independent of ERC-3643.** ERC-1404 (Simple
Restricted Token Standard) exposes `detectTransferRestriction(from, to, value)`, called **on-chain inside the transfer
path**, which returns a restriction code unless the counterparties satisfy the token's allowlist/eligibility rules;
CMTAT (CMTA Token, `github.com/CMTA/CMTAT`) implements this as a modular validation/allowlist layer with conditional
transfer. Taurus (with CMTA) built and **measured** a CMTAT + ERC-1404 restricted-transfer proof-of-concept **on the
Sepolia Ethereum testnet** (Taurus blog, read at source: "The tests were conducted on the Sepolia Ethereum testnet").
The transfer is gated on the counterparties' allowlist/identity state — an in-transaction identity-gated transfer — but
the PoC is a demonstration, not a reusable named performance workload with pinned, reproducible conditions.

| A1 | A2 | A3 | A4 | A5 | IDTx (Id-gate) |
|:--:|:--:|:--:|:--:|:--:|:--:|
| ✗ | ✗ | ◐ | ✓ | ✓ | ✓ (on-chain, shipped) |

- **A1 ✗** — CMTAT ships a functional implementation + test suite and Taurus a PoC; neither is a named, reusable *performance* workload others target. [sec]
- **A2 ✗** — the on-chain `detectTransferRestriction` restriction code is a contract check, not a benchmark admission rule over results. [sec]
- **A3 ◐** — Taurus reported Sepolia measurements of the restricted-transfer PoC [src], but not a pinned, reusable metric set with stated conditions (demonstration, not benchmark-grade conditions). [src]
- **A4 ✓** — CMTAT is a public, runnable implementation + test suite (`github.com/CMTA/CMTAT`); the harness exists. [sec]
- **A5 ✓** — CMTAT is independently deployed and used across CMTA members; runnable and independently exercised (not a reproduction of a defined performance benchmark). [sec]
- **IDTx ✓ (on-chain, shipped)** — the allowlist/eligibility gate runs on-chain inside the transfer, gating on counterparty identity state. [sec mechanism / src measured on Sepolia]

**Deployment-scale note (a16z RWA allowlist transfer hooks) — [sec].** Production RWA tokens (BlackRock BUIDL, Apollo
ACRED, Ondo OUSG/USTB and peers) enforce allowlist/identity-gated transfers via on-chain transfer hooks, a pattern a16z
has documented as standard RWA practice. This is deployed, multi-billion-dollar evidence that the on-chain
identity-gated-transfer *mechanism* is production-scale, **not** a lab curiosity — it is cited here only as corroboration
of the F1 retraction, not scored as a benchmark artefact.

**obj.11 status:** **new artefact; the ERC-1404 mechanism is secondary, the Sepolia measurement read at source (Taurus
blog) this pass.** Second independent on-chain identity-gated-transfer example; reinforces that the mechanism (and a
runnable, measured harness) already exists.

---

## §2 — Synthesis

**Which axis is the common failure.** Partition the artefacts and the picture is sharp. The *general blockchain
benchmarks* (BLOCKBENCH, DIABLO) are the **most complete benchmarks** on the five axes — each satisfies A1, A3, A4 and A5
solidly (A2 only partial) — but they carry **no identity workload at all**, confirmed this pass from their enumerated
shipped workloads (YCSB/SmallBank/4-micro; Dota2/FIFA/NASDAQ/Twitter/Uber/YouTube). The *identity-relevant* artefacts are
the mirror image: they have identity content but fail as benchmarks, and they fail on the **same two axes every time —
A2 (admission rule) and A5 (independent reproduction)**. A2 is absent from *every* performance-measuring identity
artefact (Satybaldy26, Frutuoso26, Lagos26, Buldini25, DeSalve26, Siqueira23): each is descriptive/comparative, none
states a pass/fail gate. A5 is absent from *every* identity artefact including the conformance/assurance frameworks
(NIST, EUDI LSPs) — no SSI/DID performance study has a non-author re-run on record. **So the common failure splits by
family: A5-as-benchmark-reproduction is the universal gap across the identity *benchmark/performance* artefacts (the
cleanest single statement of the benchmark gap, matching BENCHMARK_GAP §3 — and note A5 is a maturity property, not a
Gray/TPC defining axis, BENCHMARK_V0 §3.2), while A2 is universal among the identity *performance* studies
specifically. (T-REX/CMTAT are independently *deployed/run* as shipped code — A5 ✓ in that sense — but neither is a
performance benchmark whose *result* is reproduced.)**

**RETRACTION (F1, examiner pass).** An earlier version of this synthesis claimed the **non-axis IDTx property is the
single thing absent from every artefact without exception**. **That claim is false and is withdrawn.** Artefacts 8–9,
read this pass, show the on-chain in-transaction identity-gated-transfer mechanism **exists and is shipped**: ERC-3643 /
T-REX runs `isVerified(_to)` + `canTransfer(from,to,amount)` on-chain before value moves (EIP-3643 spec at source), and
ERC-1404 / CMTAT gates transfers on counterparty allowlist/identity state on-chain (measured by Taurus on Sepolia). The
mechanism is deployed at multi-billion-dollar scale (a16z-documented RWA transfer hooks). What the general benchmarks
(BLOCKBENCH/DIABLO) lack is an identity workload; what the SSI *performance* studies measure is lifecycle administration
or credential presentation; and Frutuoso26 checks its dependency off-chain. But the gate itself is **present, on-chain
and shipped** in ERC-3643/T-REX and ERC-1404/CMTAT. The defensible claim is therefore narrow: see the narrowed gap claim
below and in `BENCHMARK_V0.md` §3.2.

**Which comes closest, and why it still falls short.** Two different "closest" answers, depending on the question. (a)
*Closest to a complete benchmark on the five axes:* **BLOCKBENCH / DIABLO at 4 of 5** (A1, A3, A4, A5; A2 partial) — but
they fall short absolutely on identity: zero identity workload, so they are irrelevant to the thesis's object except as
the methodological template. (b) *Closest identity-relevant benchmark:* **Satybaldy et al. 2026** — it is the only
artefact that calls itself a benchmark, pins A3 fully (100 iterations, named EC2 instance, testnets, normalized
latency/cost + an entropy MLS) and ships a replication package. It still falls short on **four of five**: A1 ◐ (fixed op
set but tied to 3 SDKs, self-authored, not a standard), A2 ✗ (no admission rule), A4 ◐ (an *anonymous* review snapshot,
not a maintained harness), A5 ✗ (no independent re-run) — and, decisively, **IDTx ✗**: its five operations are
single-DID lifecycle administration, none gated on another identity. (c) *Closest to the IDTx mechanism:* **Frutuoso et
al. 2026** — the full read this pass shows its identity-dependency (issuer accreditation) is enforced **client-side,
off-chain**. (c′) *Closest shipped on-chain gate:* **ERC-3643 / T-REX** (Artefact 8) and **ERC-1404 / CMTAT**
(Artefact 9) — these **do** ship the in-transaction, on-chain identity-gated transfer, but neither packages it as a
complete A1–A5 *benchmark* (A1/A2/A3-as-benchmark ✗; they are functional suites and a measured PoC, not reusable
admission-gated metric-defined performance workloads).

**Net (NARROWED, F1 examiner pass).** The on-chain identity-gated-transfer mechanism **exists, is shipped (T-REX), and
is deployed at scale**; what does not exist is a **complete A1–A5 benchmark** that packages it as a reusable,
admission-gated, metric-defined performance workload — and no artefact packages the thesis's broader IDTx taxonomy (the
full dependency-kind × locus × evaluation-point space, not just receiver-allowlist transfer) as a workload. The
mechanism, the on-chain gate, and runnable harnesses already exist (conceded); the **complete benchmark** and the
**taxonomy-as-workload** do not. Within EVM substrates (m9: the surveyed scope is EVM-only), no artefact is both a
complete benchmark *and* a packaged IDTx-taxonomy workload — which is the honest residual, not an "unoccupied cell /
absolute absence."

---

## §3 — Read-in-full vs abstract-only provenance (closing obj.11)

**Sources read in full / at source THIS pass (free artefacts, directly inspected): 10.**

| # | Artefact | How read this pass | Phase-1 status | obj.11 action |
|---|---|---|---|---|
| 1 | W3C DID Method Rubric | [src] 100k/137k chars | at source (P1) | deepened; ✗ row confirmed from the artefact's own wording |
| 2 | W3C DID Core **test suite** report | [src] | spec read, suite not | **upgraded** (suite itself, not just DID Core spec); A3 ✗ pinned |
| 3 | W3C VC Data Model 2.0 test suite | [src] GitHub | [abs]/[sec] via Mazzocca24 | **upgraded**; conformance-not-performance confirmed |
| 4 | Hyperledger Caliper docs (v0.7.1) | [src] | [sec] via Mazzoni21 | **upgraded**; BYO-workload + no-identity + no-pass/fail confirmed |
| 5 | BLOCKBENCH repo (shipped workloads) | [src] GitHub | [abs] Dinh17 | **upgraded**; "no identity workload" now evidenced by the workload list |
| 6 | DIABLO site (shipped workloads) | [src] | [abs] Gramoli23 | **upgraded**; 6 DApps enumerated, none identity |
| 7 | NIST SP 800-63-4 guideline | [src] 100k/191k chars | [abs] DOI (800-63B) | **upgraded**; assurance framework, no workload, confirmed |
| 8 | EUDI ARF / FCAF conformance page | [src] eudi.dev | [sec] via Sokolov26 | **upgraded**; functional-conformance-only confirmed at source |
| 9 | Satybaldy et al. 2026 | [full] alphaXiv full text | [full] (P1) | deepened; VM/iterations pinned, anonymous-snapshot ⇒ A4 ◐ |
| 10 | Frutuoso et al. 2026 | [full] arXiv HTML | **[abs]** (P1) | **upgraded**; 3 cells corrected (IDTx ✓→◐, A4 ✗→◐, no token transfer) |
| 11 | ERC-3643 / T-REX (EIP-3643 spec) | [src] eips.ethereum.org, `transfer` body read at source | not profiled (P1 §1c mentioned Frutuoso only) | **new; the F1 falsifier** — IDTx ✓ on-chain shipped, A4/A5 ✓ (harness exists), A1/A2/A3-as-benchmark ✗ |
| 12 | ERC-1404 / CMTAT (Taurus Sepolia PoC) | [src] taurushq.com measurement read at source; [sec] ERC-1404 mechanism | not profiled (P1) | **new; second on-chain gate** — IDTx ✓, measured on Sepolia, not a complete benchmark |

**New artefacts profiled at source this pass (F1): 2** (#11 ERC-3643/T-REX via the EIP-3643 spec at source; #12
ERC-1404/CMTAT via the Taurus Sepolia measurement at source + the ERC-1404 mechanism [sec]).

**Count of abstract-only artefacts upgraded to read-in-full/at-source this pass: 7** (#2 DID Core test suite, #3 VC test
suite, #4 Caliper, #5 BLOCKBENCH, #6 DIABLO, #7 NIST 800-63-4, #10 Frutuoso26) — plus #8 EUDI upgraded from secondary to a
source read, and #1/#9 deepened. The headline obj.11 upgrade is **#10 Frutuoso26** (abstract-only → full), which
corrected the one artefact Phase 1 had scored IDTx ✓.

**Still abstract-only / not upgradable from a free source (flagged, marks retained from `BENCHMARK_GAP`):**
- **Lagos et al. 2026** — ACM SAC 2026, DOI 10.1145/3748522.3779904 (paywalled). [abs]
- **Buldini et al. 2025** — IEEE TIFS, DOI 10.1109/tifs.2025.3636051 (paywalled). [abs]
- **De Salve et al. 2026** — IEEE Access, DOI 10.1109/access.2025.3649167 (open-access but not chased this pass). [abs]
- **Siqueira et al. 2023 ×2** — IEEE DAPPS / ICBC (paywalled). [abs]
- **Buran 2025, Alizadeh 2022** — not re-read this pass. [abs]
- **Sokolov et al. 2026** — arXiv 2609.26220, **free but only the abstract was read this pass**; the FCAF *conformance* framing was instead confirmed at the EUDI ARF source (#8). Full-text read is a candidate for the next pass. [abs] **(m10) The EUDI reproduction cells (Artefact 4 A5, and the eIDAS/EUDI A5 cell in `BENCHMARK_V0.md` §3.2) are marked PROVISIONAL** — they rest on Sokolov26 abstract-only.
- **DIF interop suites** — framed from the survey [Mazzocca24], not re-read as individual suites this pass. [sec]
- **Gromit / GFBE / BBSF / DLPS / BlockCompass / bBench** — same class as BLOCKBENCH/DIABLO; not individually re-read. [abs]

obj.11 is closed **as far as free sources allow**: every free artefact among the WP-brief targets has been read at source
or in full; the residual abstract-only cells are paywalled (IEEE/ACM) or deliberately deferred, and are explicitly
flagged so no claim rests on an unread internal detail.

---

## §4 — Headline (for SP-9 / Ch 7)

Reading the artefacts rather than their abstracts **strengthens** the Phase-1 gap statement. The most complete
benchmarks (BLOCKBENCH, DIABLO, 4/5 axes) are identity-blind by construction; the only self-described SSI benchmark
(Satybaldy26) is strong on metrics-with-conditions but fails A2/A4/A5 and measures identity *administration*, not
identity *dependency*; and the one artefact nearest the IDTx mechanism (Frutuoso26) turns out, on a full read, to check
its identity-dependency **off-chain at the client** and to ship no transfer workload. **A5 (independent reproduction) is
the cleanest universal failure across the identity *benchmark* artefacts; A2 (admission rule) is universal among the
identity performance studies.**

**But the in-transaction identity-gating *mechanism* is NOT absent (F1 retraction):** ERC-3643 / T-REX and
ERC-1404 / CMTAT ship it on-chain, and it is deployed at scale. The narrowed, defensible headline for SP-9 / Ch 7 is:
**the on-chain identity-gated-transfer mechanism exists, is shipped (T-REX), and is deployed at scale; what does not
exist is a complete A1–A5 benchmark packaging it as a reusable, admission-gated, metric-defined performance workload —
and no artefact packages the thesis's broader IDTx taxonomy (dependency-kind × locus × evaluation-point, not just
receiver-allowlist transfer) as a workload.** The contribution is a **new workload class**, not the discovery of an
empty benchmark cell.
