# WP 1.6 — The Benchmark Gap: Evidence For and Against "No Benchmark Exists for SSI / IDTx"

**Home:** Appendix G-F (evidence table) · **Lead section:** companion paper SP-9.
**Produced:** 2026-10-24 by Literature Scout (Explore). **Status:** draft; evidence-first.
**Binds:** `docs/idtx_core/DETAILED_PLAN.md` §3 (WP 1.6 done-condition: ≥ 20 sources, each classified on the
five axes, claim worded to fit the evidence) and the risk register row "the claim is wrong or overclaimed".
**Reads first:** `DETAILED_PLAN.md` §4.5-claims; `docs/phase2/focus/F1_onchain_storage_idtx/ANALYSIS.md` §4.1
(IDTx definition, quoted verbatim, AR-2), §4.3 (prior art), §4.4 (three-axis taxonomy).

**Sourcing note (Convention §2).** Every cited paper was retrieved through Consensus, alphaXiv or Firecrawl and
is named by DOI or arXiv ID. The W3C DID Method Rubric and DID Core were read **at source**. The Satybaldy et
al. 2026 benchmarking study (the strongest counter-example) was read **in full**. All other papers are classified
from their abstracts and are marked accordingly in the reading log (§5); an entry classified from abstract only
cannot support a claim about internal detail it does not state, and none is used that way here.

---

## 0. What counts as a benchmark (the five axes)

A *benchmark* is more than a measurement. Following the blockchain-benchmarking literature (BLOCKBENCH
[Dinh17a; Dinh17b], DIABLO [Gramoli23], BBSF/Blockbench v3 [Ren23]), an artefact is a benchmark when it fixes a
workload, states how a result is admitted, defines metrics with the conditions under which they are measured,
ships a harness others can run, and has been run by someone other than its authors. The five axes below are the
done-condition of WP 1.6; each artefact in §1 is scored on all five.

| Axis | Question | ✓ means |
|---|---|---|
| **A1 Fixed workload** | Is there a defined, shared set of operations every implementation must run? | a named, reusable workload spec, not an ad-hoc set chosen per paper |
| **A2 Admission / conformance rule** | Is there a pass/fail or admit/reject rule for a result or an implementation? | an explicit rule (conformance pass, SLA threshold, validity gate) |
| **A3 Metrics + measurement conditions** | Are the metrics defined *with* the conditions (hardware, network, load, sample size)? | metrics and conditions both stated and pinned |
| **A4 Public reusable harness** | Is there code others can pick up and run unchanged? | a released, runnable harness, not screenshots of one-off scripts |
| **A5 Independent reproduction** | Has anyone other than the authors run it and reported? | ≥ 1 independent re-run on record |

The sixth property that matters for this thesis is **not** one of the five axes but the thing the thesis contributes:
**IDTx-level dependency semantics** — a workload in which a transaction's *admissibility or effect depends on the
state of another named identity* (ANALYSIS.md §4.1), evaluated in the transaction, at admission, or off-chain then
re-checked (§4.4). No artefact below carries this, and that is the crux of the argument in §2.

---

## 1. Evidence table

Legend: ✓ present · ◐ partial · ✗ absent. "IDTx?" = does the workload express identity-dependency semantics in the
sense of ANALYSIS.md §4.1 (not merely identity *administration* — create/update/resolve a record — or sender
*authentication*).

### 1a. The artefacts named in the WP brief

| Artefact | What it is | A1 workload | A2 admission | A3 metrics+cond. | A4 harness | A5 indep. repro | IDTx? | Citation |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|---|
| **W3C DID Method Rubric** | qualitative evaluation *aid*: a registry of subjective criteria; "rather than reducing this Evaluation to a single number"; "no requirement to answer all the questions"; examples "not presented as objective fact" | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | [W3C-Rubric] |
| **W3C DID Core test suite / impl. report** | *conformance* suite: "determines whether or not a given implementation is conformant"; interop = can create/parse DIDs & documents; 46 implementations submitted | ◐ (conformance inputs) | ✓ (spec pass/fail) | ✗ (no latency/throughput/cost) | ✓ (suite) | ✓ (46 impls) | ✗ | [W3C-DIDCore] |
| **W3C VC test suite / DIF interop suites** | conformance + interoperability of VC issue/verify and protocol profiles; not a performance measure | ◐ | ✓ | ✗ | ✓ | ◐ | ✗ | [W3C-DIDCore] (same class; VC/DIF read as conformance per survey [Mazzocca24]) |
| **NIST SP 800-63(-4)** | identity-assurance *assessment framework*: defines IAL/AAL/FAL requirement levels for proofing/authn/federation; a risk-and-requirements model, not a measured workload | ✗ | ◐ (assurance-level criteria, assessed by an auditor, not a run) | ✗ | ✗ | ✗ | ✗ | [NIST-80063b] |
| **eIDAS 2.0 / EUDI Wallet conformance (ARF, FCAF) & Large-Scale Pilots** | *functional conformance* assessment + certification against the Architecture & Reference Framework; pilots are deployments, not a shared measured workload; "Functional Conformance Assessment Framework provide[s] increasingly structured wallet-side evidence" but no rerunnable performance object | ◐ (conformance scenarios) | ✓ (certification) | ✗ | ◐ | ✗ | ✗ | [Sokolov26] |
| **BLOCKBENCH** [Dinh] | blockchain data-processing benchmark; workloads = YCSB/Smallbank + micro (CPU/IO/analytics) on Ethereum/Parity/Fabric | ✓ | ◐ | ✓ | ✓ | ✓ | ✗ (no identity workload) | [Dinh17a; Dinh17b] |
| **Hyperledger Caliper** | benchmarking *tool/harness*: user supplies the workload; measures TPS/latency/resource use | ✗ (BYO workload) | ✗ | ◐ (metrics defined; conditions user-set) | ✓ | ✓ (widely used, e.g. [Mazzoni21], [Vidal25]) | ✗ | [Mazzoni21] |
| **DIABLO** | blockchain benchmark suite of realistic DApp workloads (6 chains, 4–5 DApps); stresses from distributed load | ✓ | ◐ | ✓ | ✓ | ✓ ([Lebedev23] bare-metal re-run) | ✗ (no identity DApp) | [Gramoli23; Lebedev23] |
| **Gromit / GFBE / BBSF / DLPS / BlockCompass / bBench** | further blockchain benchmarking frameworks; generic workloads, chain-selection focus | ✓/◐ | ◐ | ✓ | ✓ | ◐ | ✗ | [Ren23; Ma24; Sedlmeir21; Rasolroveicy24; Vidal25] |

### 1b. The nearest academic SSI / DID / VC evaluation artefacts (the real counter-examples)

| Artefact | What it is | A1 | A2 | A3 | A4 | A5 | IDTx? | Citation |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|---|
| **Satybaldy et al. 2026 — "Decentralized Identity in Practice: Benchmarking Latency, Cost, and Privacy"** | the closest thing to an SSI benchmark: unified cross-platform study of did:ethr / did:hedera / did:xrpl over the **DID lifecycle** (Create/Resolve/Update/Revoke/Deactivate); latency, relative cost, Metadata-Leakage Score (bits/op); 100 iterations/op, pinned VM, testnets; open replication package | ◐ (fixed op set, but tied to 3 SDKs; self-authored, not a standard) | ✗ (descriptive; no pass/fail) | ✓ (metrics + conditions pinned) | ◐ (replication package released, not a maintained community harness) | ✗ (single study, newly published) | ✗ (lifecycle = identity *administration*, not dependency on another named identity) | [Satybaldy26] |
| **Lagos et al. 2026 — EUDI candidate VC schemes** | extendable benchmarking suite for end-to-end wallet ops (SD-JWT vs BBS variants) across desktop/phone/watch/SBC; open-source | ◐ | ✗ | ✓ | ✓ (open-source suite) | ✗ | ✗ (credential presentation, not IDTx) | [Lagos26] |
| **Buldini et al. 2025 — selective-disclosure benchmark** | open-source benchmark of SD mechanisms for VCs; latency/bandwidth/storage KPIs + a formal threat/property comparison | ◐ | ◐ (property satisfaction) | ✓ | ✓ (open-source) | ✗ | ✗ | [Buldini25] |
| **De Salve et al. 2026 — SD experimental comparison** | reference implementations of 5 SD approaches; same ops on same credentials; create/verify time + size | ◐ | ✗ | ✓ | ◐ | ✗ | ✗ | [DeSalve26] |
| **Siqueira et al. 2023 (×2)** | empirical perf. of Hyperledger Indy/Aries healthcare SSI; concurrent-user load; bottleneck analysis | ◐ (one use case) | ✗ | ✓ | ✗ | ✗ | ✗ | [Siqueira23a; Siqueira23b] |
| **Buran et al. 2025** | Walt.id stack across DID methods (CHEQD/WEB/KEY/JWK) on Pi vs PC; latency/CPU/memory | ◐ | ✗ | ✓ | ✗ | ✗ | ✗ | [Buran25] |
| **Alizadeh et al. 2022** | comparative execution-time/throughput of decentralized-ID approaches (uPort/ShoCard/BBID/BioIPFS) | ◐ | ✗ | ◐ | ✗ | ✗ | ✗ | [Alizadeh22] |
| **Satybaldy et al. (SSI Evaluation Framework)** | *qualitative* criteria framework comparing uPort/Sovrin/ShoCard/Civic/Blockstack | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | [Satybaldy-EF] |
| **Čučko21 / Schardong21 / Satybaldy24 (reviews & taxonomies)** | systematic maps/taxonomies; Čučko explicitly notes "hardly any studies researching usability, user experience, patterns" | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | [Cucko21; Schardong21; Satybaldy24] |
| **Mazzocca et al. 2024 — DID/VC survey** | comprehensive survey; catalogues implementations but defines no benchmark | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | [Mazzocca24] |

### 1c. ERC-3643 / ONCHAINID and identity-gated tokens (closest *mechanism* prior art, per ANALYSIS.md §4.3)

| Artefact | What it is | A1 | A2 | A3 | A4 | A5 | IDTx? | Citation |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|---|
| **Frutuoso et al. 2026 — ERC-3643 + ONCHAINID academic credentials** | repurposes T-REX/ONCHAINID (ERC-734/735/3643) as an issuer-accreditation whitelist; reference impl. evaluated on gas/scalability/latency/security vs a hash-anchoring baseline | ◐ (bespoke lifecycle) | ✗ | ✓ | ◐ (public repo DiGo-certify-app) | ✗ | ◐ (**corrected WP 3.1, read in full:** issuer *accreditation* is checked **off-chain at the client**; on-chain `addClaim` is gated only on the sender's **own** key `onlyClaimKey` + signature validity, not on another named identity's registry state, and **no token transfer is measured** — closest *mechanism*, not a true in-transaction identity-gating workload) | [Frutuoso26] |
| **RandX [Zondi26]; SBT access control [Madhwal25]; Web3ID [Hao25]** | identity/credential-gated token ops; each reports its own gas/latency numbers | ◐ | ✗ (revert-on-unverified is a contract check, not a benchmark rule) | ◐ | ✗ | ✗ | ◐/✓ (gating present) | [Zondi26; Madhwal25; Hao25] |

**No shared evaluation across the ERC-3643/ONCHAINID family exists.** Each paper rolls its own workload, metrics and
harness; there is no common identity-gating benchmark they are run against.

---

## 2. The argument, worded to fit the evidence

The blunt claim "no benchmark exists for SSI / decentralized identity" is **not** defensible as stated: performance
benchmarking artefacts for decentralized identity now exist, and at least one — Satybaldy et al. 2026 [Satybaldy26] —
names itself a benchmark, measures latency/cost/privacy over the DID lifecycle across three ledgers with pinned
conditions, and ships a replication package. There are also open-source benchmarking suites for the *credential*
layer (selective disclosure [Buldini25; DeSalve26], EUDI wallet schemes [Lagos26]). To claim none exists would not
survive an examiner holding any of these papers.

The claim **is** defensible, and survives, in the following exact form:

> **No benchmark exists that provides a shared, reusable workload AND an admission/conformance rule AND
> IDTx-level dependency semantics for decentralized-identity systems.** Every artefact found satisfies at most two
> of these three. The qualitative aids (W3C DID Method Rubric [W3C-Rubric], SSI evaluation frameworks
> [Satybaldy-EF]) provide neither a workload nor metrics — by their own statements they are not benchmarks and
> decline to score. The conformance suites (W3C DID/VC, DIF interop [W3C-DIDCore], eIDAS/EUDI FCAF [Sokolov26])
> provide a workload and an admission rule but measure *spec conformance, not performance*, and carry no identity-
> dependency semantics. The assurance frameworks (NIST SP 800-63 [NIST-80063b], eIDAS LoA) are assessment
> models, not measured workloads. The general blockchain benchmarks (BLOCKBENCH [Dinh17a], DIABLO [Gramoli23],
> Caliper [Mazzoni21], and the rest) satisfy all five axes but carry **no identity workload at all**. And the genuine
> SSI/DID performance studies ([Satybaldy26; Lagos26; Buldini25; Siqueira23a; Alizadeh22]) measure the identity
> *lifecycle* — create, resolve, update, revoke a record, or issue/verify/present a credential — which is identity
> *administration* and *authentication* in the sense of ANALYSIS.md §4.1, **not** a transaction whose admissibility
> depends on the state of another named identity. None defines an admission rule, and none has an independent
> reproduction on record.

**The strongest single counter-example is Satybaldy et al. 2026 [Satybaldy26].** It is the artefact to position
against explicitly. What it covers, exactly: a fixed operation set (the 5 DID lifecycle operations) over three
ledger-based DID methods, with latency, relative transaction cost and an entropy-based Metadata-Leakage Score, 100
iterations per operation on a pinned VM against public testnets, plus an open replication package. What it does **not**
cover — and precisely where this thesis contributes: (i) no admission/conformance rule (it is descriptive, A2 ✗);
(ii) no independent reproduction (single, newly published study, A5 ✗); (iii) crucially, **no IDTx semantics** — its
workload is DID-document administration, so by ANALYSIS.md §4.2 it sits entirely in the *excluded* classes
(administration/authentication), with none of the four true IDTx (MOBI birth, the two `addClaim` variants, `payToll`)
represented. The ERC-3643/ONCHAINID work [Frutuoso26] is the closest prior art, but reading it in full (WP 3.1)
shows its identity-dependency is enforced **off-chain at the client** — on-chain `addClaim` gates only on the sender's
own key and signature, and no token transfer is measured — so it does not actually measure an *in-transaction*
identity-gating (IDTx) workload; it is a single bespoke study with no shared workload, no admission rule and no
reusable harness — it confirms the mechanism is prior art
(as ANALYSIS.md §4.3 already concedes) while leaving the benchmark gap open.

**Net.** The contribution survives if and only if it is framed as "no benchmark unifies a reusable identity workload,
an admission rule, and IDTx dependency semantics" — not as "no SSI benchmark exists". Use the first wording in Ch 2
§2.6, Ch 7 and SP-9; never the second. This matches the DETAILED_PLAN risk-mitigation directive ("reword to 'no
benchmark covering X, Y, Z' if needed").

---

## 3. "What would make this a benchmark" — the missing-ingredients checklist

Against the five axes plus the IDTx property, the gap to close is:

- [ ] **A1 — A shared, named identity workload.** Not a per-paper op set. Candidate (from DETAILED_PLAN Phase 3.3):
  the minimal function set F1–F12 + the four IDTx classes + the 17-event lifecycle, published as a fixed spec other
  groups can target. *Today:* every SSI study picks its own ops; only the conformance suites share a workload, and
  theirs is non-performance.
- [ ] **A2 — An admission / conformance rule.** A pass/fail gate tying a result to a stated condition (e.g. the
  12-test conformance suite as the admission gate; validity re-checked in chain time per the D51 fix). *Today:* no SSI
  performance study has one; only spec-conformance suites do.
- [ ] **A3 — Metrics with pinned measurement conditions.** Already strong in the nearest artefacts; adopt the
  register's M-conditions (`docs/MEASUREMENT_CONDITIONS.md`) so numbers are comparable, including the freshness/
  staleness bound (k−1 messages, in chain time) that ANALYSIS.md §4.5 shows is specific to identity dependency and is
  *absent from every artefact surveyed*.
- [ ] **A4 — A public, reusable harness.** A runnable kit, not a replication snapshot. Candidate: this repo's
  10-substrate adapter/conformance harness (`adapters.conformance.test.js`). *Today:* Caliper/DIABLO are reusable but
  identity-blind; Satybaldy/Lagos/Buldini ship code but tied to their own op sets.
- [ ] **A5 — At least one independent reproduction.** The thing no SSI benchmark has yet. Needs a reproduction kit and
  a call for external runs (DETAILED_PLAN Phase 3.4). This is the single axis on which *even the strongest*
  counter-example fails, and the cleanest statement of the gap.
- [ ] **IDTx dependency semantics.** The workload must include transactions whose admissibility depends on another
  named identity's state, across the three-axis taxonomy (dependency kind × locus/encoding × evaluation point), with
  the ordering-race and stale-dependency threats (§4.5) as explicit measured conditions. *Today:* measured only once,
  never, in-transaction — the closest, [Frutuoso26], enforces its identity check off-chain at the client (WP 3.1); never as a benchmark.

A benchmark exists when all six boxes are ticked by **one** artefact that someone other than its author has run. No
surveyed artefact ticks more than four, and none ticks A5 together with the IDTx row.

---

## 4. Headline

The "no benchmark" claim is defensible **only in its narrow form** (no benchmark unifying a reusable identity
workload + an admission rule + IDTx dependency semantics, with an independent reproduction). It is **not** defensible
as "no SSI/DID benchmark exists at all" — performance benchmarking artefacts for the DID lifecycle and the credential
layer now exist. Frame the contribution accordingly.

---

## 5. Sources read (reading log and count)

**Count: 31 distinct sources examined.** Read in full / at source: 3 (Satybaldy26 in full; W3C DID Method Rubric and
W3C DID Core at source). Classified from abstract (via Consensus / alphaXiv / Firecrawl): 28. The done-condition
(≥ 20 sources, each classified on the five axes) is met.

**Primary artefacts (read at source):**
- [W3C-Rubric] W3C, *DID Method Rubric v1.0*, W3C Group Note. https://www.w3.org/TR/did-rubric/ — read; self-described
  qualitative aid, declines to score.
- [W3C-DIDCore] W3C, *Decentralized Identifiers (DIDs) v1.0* + Implementation Report/test suite.
  https://www.w3.org/TR/did-core/ — read; conformance/interop, not performance (46 impls submitted).
- [NIST-80063b] Grassi et al., *NIST SP 800-63B Digital Identity Guidelines*, 2017. DOI 10.6028/nist.sp.800-63b (and
  the 800-63-4 revision line) — assurance-level assessment framework.

**Academic — SSI/DID/VC performance & evaluation:**
- [Satybaldy26] Satybaldy et al., *Decentralized Identity in Practice: Benchmarking Latency, Cost, and Privacy*, arXiv
  2601.20716, 2026. DOI 10.48550/arxiv.2601.20716 — **read in full; strongest counter-example.**
- [Lagos26] Lagos et al., *Measuring the Performance of Candidate Verifiable Credential Schemes for the EU Digital
  Identity Wallet*, ACM SAC 2026. DOI 10.1145/3748522.3779904.
- [Buldini25] Buldini et al., *Benchmarking Selective Disclosure Mechanisms for Verifiable Credentials*, IEEE TIFS,
  2025. DOI 10.1109/tifs.2025.3636051.
- [DeSalve26] De Salve et al., *Selective Disclosure Approaches in SSI: An Experimental Comparison*, IEEE Access, 2026.
  DOI 10.1109/access.2025.3649167.
- [Siqueira23a] Siqueira et al., *Performance Evaluation of SSI Use Cases*, IEEE DAPPS 2023. DOI
  10.1109/dapps57946.2023.00026.
- [Siqueira23b] Siqueira et al., *Empirical Evaluation of SSI Technology*, IEEE ICBC 2023. DOI
  10.1109/icbc56567.2023.10174979.
- [Buran25] Buran et al., *Performance Evaluation of Self-Sovereign Identity* (Walt.id across DID methods), 2025.
- [Alizadeh22] Alizadeh et al., *Comparative Analysis of Decentralized Identity Approaches*, IEEE Access, 2022. DOI
  10.1109/access.2022.3202553.
- [Satybaldy-EF] Satybaldy et al., *Self-Sovereign Identity Systems Evaluation Framework* (uPort/Sovrin/ShoCard/
  Civic/Blockstack) — qualitative.
- [Mazzocca24] Mazzocca et al., *A Survey on Decentralized Identifiers and Verifiable Credentials*, IEEE COMST, 2024/25.
  DOI 10.1109/comst.2025.3543197.
- [Cucko21] Čučko et al., *Decentralized and Self-Sovereign Identity: Systematic Mapping Study*, IEEE Access, 2021. DOI
  10.1109/access.2021.3117588.
- [Schardong21] Schardong & Custode, *SSI: A Systematic Review, Mapping and Taxonomy*, Sensors, 2021. DOI
  10.3390/s22155641.
- [Satybaldy24] Satybaldy et al., *A Taxonomy of Challenges for SSI Systems*, IEEE Access, 2024. DOI
  10.1109/access.2024.3357940.
- [Papatheodorou25] Papatheodorou et al., *YouGovern*, Applied Sciences, 2025. DOI 10.3390/app15126437.
- (alphaXiv) *Are We There Yet? A Study of Decentralized Identity Applications*, arXiv 2503.15964, 2025.
- (alphaXiv) *Functional Requirements for Decentralized and Self-Sovereign Identities*, arXiv 2603.24250, 2026.

**Academic — general blockchain benchmarking:**
- [Dinh17a] Dinh et al., *BLOCKBENCH: A Framework for Analyzing Private Blockchains*, ACM SIGMOD 2017. DOI
  10.1145/3035918.3064033.
- [Dinh17b] Dinh et al., *Untangling Blockchain: A Data Processing View*, IEEE TKDE, 2017. DOI
  10.1109/tkde.2017.2781227.
- [Gramoli23] Gramoli et al., *Diablo: A Benchmark Suite for Blockchains*, ACM EuroSys 2023. DOI
  10.1145/3552326.3567482.
- [Lebedev23] Lebedev et al., *On the Relevance of Blockchain Evaluations on Bare Metal*, arXiv, 2023. DOI
  10.48550/arxiv.2311.09440 — independent Diablo re-run.
- [Ren23] Ren et al., *BBSF: Blockchain Benchmarking Standardized Framework* (Blockbench v3), 2023. DOI
  10.1145/3595647.3595649.
- [Ma24] Ma et al., *GFBE: A Generalized and Fine-Grained Blockchain Evaluation Framework*, IEEE TC, 2024. DOI
  10.1109/tc.2024.3349654.
- [Sedlmeir21] Sedlmeir et al., *The DLPS: A New Framework for Benchmarking Blockchains*, HICSS 2021. DOI
  10.24251/hicss.2021.822.
- [Rasolroveicy24] Rasolroveicy et al., *BlockCompass*, IEEE TC, 2024. DOI 10.1109/tc.2024.3404103.
- [Vidal25] Vidal et al., *bBench*, IEEE ISSRE 2025. DOI 10.1109/issre66568.2025.00046.
- [Mazzoni21] Mazzoni et al., *Performance evaluation of permissioned blockchains ... Quorum* (uses Hyperledger
  Caliper), Blockchain: Research and Applications, 2021. DOI 10.1016/j.bcra.2021.100026.
- [Touloupou22] Touloupou et al., *A Systematic Literature Review Toward a Blockchain Benchmarking Framework*, IEEE
  Access, 2022. DOI 10.1109/access.2022.3188123.

**Academic — ERC-3643 / ONCHAINID / identity-gating & on-chain identity:**
- [Frutuoso26] Frutuoso et al., *Identity-Bound Academic Credentials on Blockchain: On-Chain Issuer Accreditation with
  ERC-3643 and OnchainID*, arXiv 2607.16383, 2026. DOI 10.48550/arxiv.2607.16383 — closest IDTx mechanism; identity check enforced off-chain (WP 3.1), not a measured in-transaction workload.
- [Zondi26] Zondi et al., *RandX: Decentralizing the South African Rand through Blockchain* (VC-gated ERC-20),
  IST-Africa 2026.
- [Madhwal25] Madhwal et al., *A Blockchain-Based Access Control Architecture Using Non-Transferable NFTs*, IEEE
  Blockchain 2025. DOI 10.1109/blockchain67634.2025.00025.
- [Hao25] Hao et al., *Web3ID*, ACM Transactions on the Web, 2025. DOI 10.1145/3771556.
- [Vaziry24] Vaziry et al., *SoK: Bridging Trust into the Blockchain — A Systematic Review on On-Chain Identity*, IEEE
  BRAINS 2024. DOI 10.1109/brains63024.2024.10732621.

**Standards / eIDAS-EUDI conformance & assurance:**
- [Sokolov26] Sokolov, *Who Assures the Verifier? An Executable Assurance-Locus Audit of the EUDI Wallet*, arXiv
  2609.26220, 2026. DOI 10.48550/arxiv.2609.26220 — documents the EUDI Functional Conformance Assessment Framework
  (FCAF) as conformance, and the absence of a rerunnable evidence object.
- [AbellanAlvarez25] Abellán Álvarez et al., *Privacy evaluation of the EUDI Wallet ARF*, Computers & Security, 2025.
  DOI 10.1016/j.cose.2025.104707 — qualitative privacy, not a performance benchmark.
