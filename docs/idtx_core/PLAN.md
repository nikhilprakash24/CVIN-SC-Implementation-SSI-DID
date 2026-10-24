# IDTx and the Minimal ID-System Function Set: Core-Contribution Plan (Phases 1–6)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Date:** 2026-10-24
**Status:** plan + Phase 1 kickoff. No new measured number appears in this document. Every number cited is from the
register (`docs/MEASUREMENT_CONDITIONS.md`) under its existing row and caveats.

**Grounding (read first):**
- IDTx definition, taxonomy, threats, cost-model shape: `docs/phase2/focus/F1_onchain_storage_idtx/ANALYSIS.md` §4
- Thesis draft: `docs/thesis/chapter6-discussion/DRAFT_6.8_IDTX_2026-10-20.md`; chapter 2 §2.6 in
  `docs/thesis/chapter2-literature-review/DRAFT_SECTIONS_2026-10-20.md`
- Basic ID set (IMinimalSSI F1–F12) and its catalogue extension: `docs/BASIC_ID_SET_EXTENSION.md`
- Code: `phase2/idtx/contracts/IdtxExecutor.sol` (+ `test/idtx.test.js`, `mutate_idtx.sh`);
  `5_zkp-agent-identity/contracts/ZkVinGate.sol`; `CVIN_NFT_DID_ERC721.sol` `payToll`
- Existing figure pipelines to reuse for visual consistency: `docs/phase2/focus/make_focus_figures.py`,
  `docs/figures/make_review_figures.py`

---

## 0. A decision this plan reopens — DECIDED 2026-10-24: A+ (thesis is home; overflow to Appendix G or companion SP-9, returnable). Detailed plan: `DETAILED_PLAN.md`

`ANALYSIS.md` §6 currently **cuts** the measured IDTx study from the thesis (one future-work paragraph; prototype
cited as artefact; measured study → paper P5). This request makes IDTx + the minimal function set a **core**
contribution. Those two positions conflict. Proposed resolution, for decision **P2-D8b**:

| Option | Thesis scope | Cost |
|---|---|---|
| **A (recommended)** | Phase 1 below enters the thesis as a *conceptual + specification* contribution (definition, minimal set, primitive diagrams, pseudocode, benchmark-gap argument). Measured IDTx study stays P5. | ~1 chapter section + figures; no new runs |
| B | Also measure the prototype (gas per IDTx class) in the thesis | needs a pre-registered run (F1 `PLAN.md`); delays chapter 5 |
| C | Keep the cut as is | contradicts this request |

---

## 1. Should this also run in chat (claude.ai Projects)? — the answer

**Run the build here, in Code. Use chat as a reviewer/ideation sidecar, not a parallel builder.**

| Concern | Code session (this) | Chat (Project) |
|---|---|---|
| Ground truth | reads the actual repo, contracts, register rows, tests; can run `npm test`, figure scripts | sees only uploaded files / project knowledge; drifts from the repo |
| Visuals | generates SVG via the existing Python figure pipeline → committed, reproducible, same style as earlier thesis figures | renders nice one-off artifacts, but not reproducible or versioned |
| Provenance rules (register, "V"/"recalled until read") | enforced by CI checks already in the repo | not enforced |
| Research breadth | web, Consensus, alphaXiv, Firecrawl available here too | same tools; nicer for long reading/discussion |
| Cost | one source of truth | two diverging drafts to reconcile |

**Recommendation:** don't duplicate Phase 1 in chat. When this session pushes the Phase 1 draft, put
`docs/idtx_core/` into the chat Project and use chat for: (a) an *unanchored* critique of the definition and
benchmark-gap argument, (b) analogy brainstorming for Phase 2 (centralized ID systems), (c) reading-heavy literature
digestion. Bring conclusions back here as review items. That gives you the independent second opinion without two
competing artefacts.

---

## 2. The agent team (and why each exists)

You asked to see the team chosen, not defined for me. Seven roles; each has one job, one output, and a known blind spot
that another role covers.

| # | Agent | Type | Strength | Output | Blind spot covered by |
|---|---|---|---|---|---|
| 1 | **Orchestrator / Editor** | main session | holds the thesis voice, register rules, decision log; integrates | section drafts, decisions | Skeptic |
| 2 | **Repo Cartographer** | Explore (read-only) | sweeps contracts/tests/register fast; returns *citations*, not dumps | function→file:line map, inventory re-check | Contracts Engineer |
| 3 | **Standards Scholar** | general-purpose + web/Firecrawl | reads W3C/IETF/ETSI/NIST/EUDI specs **at source**; marks anything unread as "recalled" | primitive definitions with spec section refs | Skeptic |
| 4 | **Literature Scout** | general-purpose + Consensus/alphaXiv | finds prior IDTx-like work, SSI benchmarks, ERC-3643, ABAC, ID-system evaluation frameworks | annotated bibliography, "does a benchmark exist?" evidence | Skeptic |
| 5 | **Contracts / Protocol Engineer** | general-purpose | writes pseudocode from the actual Solidity; checks the minimal set is implementable | pseudocode, interface sketch, test pointers | Cartographer |
| 6 | **Visual Architect** | general-purpose | turns primitives into SVG diagrams in the existing figure style (light/dark-safe, data table per figure) | `make_idtx_figures.py`, `figures/*.svg`, `FIGURES.md` | Editor |
| 7 | **Adversarial Skeptic (Examiner)** | fresh general-purpose, given *the draft only*, not my reasoning | attacks the "no benchmark exists" claim and the IDTx novelty claim like an external examiner | objections list with severity | — (it's the check) |

Rules for the team: Scholar and Scout run in parallel; Skeptic runs last on the finished draft with no hypothesis
supplied; nothing enters the thesis that Skeptic rated "fatal" without a written answer.

---

## 3. The six phases

| Phase | Question | Deliverable | Depends on | Benchmark status |
|---|---|---|---|---|
| **1** | What is the minimal ID-system function set, what are IDTx, and why is there no benchmark? | spec + diagrams + pseudocode + analogies + gap argument (§4 below) | existing repo | *defines* the candidate benchmark |
| **2** | How does this compare to other ID / digital-ID systems? | trade-off matrix: centralized (OAuth/OIDC, SAML, X.509 PKI), national eID / EUDI wallet (eIDAS 2.0 ARF), mDL (ISO/IEC 18013-5), V2X PKI (IEEE 1609.2, ETSI TS 102 941 / SCMS), SSI (DID+VC), ERC-3643/ONCHAINID | Phase 1 function set as the common axis | qualitative |
| **3** | What is the closest thing to a benchmark, and what's missing? | survey of nearest artefacts (W3C DID Method Rubric, DIF interop suites, VC test suites, NIST 800-63 assurance levels, EUDI conformance, SCMS performance studies); gap list; "what it would take" (reference workload, metrics, harness, admission rule = our 12-test compliance) | 1, 2 | proposes benchmark v0 |
| **4** | Phase 3 for AI agents | agent identity: ERC-8004 (Set C), delegation credentials, the Steward kernel, agent IDTx (`REPORT_C_AGENT_WRAPPED_IDENTITY.md`); argue a benchmark is more urgent and likely sooner here | 3, `5_zkp-agent-identity/` | proposes agent-ID benchmark v0 |
| **5** | Phase 2 across all implementation options | the 10-substrate matrix (ERC-1056 … CVIN-Combined) × minimal set × trade-offs, using measured register rows (#35, #49, #51 …) | 2, run of record | measured where the register has it |
| **6** | IDTx visualized, including compound scenarios | sequence/flow diagrams of single and compound IDTx: C-V2X (toll + ownership + revocation; RSU-gated access; transfer-then-pay race), agentic (agent pays on owner's behalf under delegation; reputation-gated action) | 1, 4 | scenario suite = benchmark workload candidates |

---

## 4. Phase 1 — started

### 4.1 Section outline (target: thesis chapter 6 §6.8 expanded, or new §3.x "The ID-system function set")

1. **Why a benchmark does not exist** (the justification) — §4.5
2. **The minimal function set** (IMinimalSSI F1–F12) — table, diagram per set, pseudocode — §4.2
3. **Primitives under the functions** — §4.3
4. **IDTx: definition, three-axis taxonomy, inventory** (adopt `ANALYSIS.md` §4.1, §4.4 verbatim; do not re-word — AR-2)
5. **Analogies to centralized / today's ID systems** — §4.4
6. **Extension to a full SSI ID system** (catalogue: lifecycle, read path, scale; Set C agents) — from
   `BASIC_ID_SET_EXTENSION.md` §2
7. **Protocols and algorithms used, and why** — per primitive
8. **Limits** — what the set leaves out (F8 has no native ERC; L1 receipt proofs unbuilt; equality-only commitments)

### 4.2 The minimal function set (draft; F-numbers only where sourced — **[B1]** = needs canon archive `cvin-sandbox-v1.3`)

| Set | Function | Plain-word purpose | Centralized analogy | CAV / C-V2X analogy |
|---|---|---|---|---|
| A | `createDID` | mint an identifier controlled by a key | account creation at an IdP; CA issues a cert | vehicle enrolment (SCMS enrolment cert); MOBI VID birth with VIN binding |
| A | resolve | identifier → current document (keys, services) | directory/LDAP lookup; OIDC discovery; OCSP for keys | resolving the pseudonym cert chain |
| A | `changeOwner` (rotate controller) | move control to a new key | password/key reset; account recovery | ownership transfer at sale; HSM key rollover |
| A | add/revoke delegate | time-boxed sub-keys | OAuth access tokens with expiry; sessions | short-lived pseudonym certs (1609.2) |
| A | set/revoke attribute | identity-document state | profile attributes, SCIM | VID-I attributes (make, model, recall status) |
| A | `execute` (agent proxy) | the identity acts | service account; OAuth client credentials | vehicle/agent pays a toll by itself |
| A | deactivate | end of life | account deletion; cert revocation | scrapping; CRL / misbehaviour revocation |
| B | `issueCredential` | issuer attests a claim | IdP issues an ID token / SAML assertion | inspection certificate, insurance proof |
| B | `verifyCredential` | check signature + status | token introspection; signature + OCSP | RSU/V2V message verification |
| B | `revokeCredential` | invalidate a claim | token revocation list | CRL distribution |
| B | `createPresentation` (F8) | holder discloses to a verifier, replay-protected | step-up auth; signed request | presenting proofs at a gate/toll |
| — | **IDTx** (not in F1–F12) | a transaction whose admissibility/effect depends on the state of a *named* identity | ABAC policy decision point gating an action on *another* subject's attributes | `payToll` gated on named vehicle's owner; claim gated on issuer status |

The key framing: F1–F12 are the **identity lifecycle**; IDTx is **identity used as a precondition by other
transactions**. Centralized systems implement the latter as a PDP/PEP call to a trusted server at decision time; the
ledger version evaluates it *inside execution*, which changes where trust, freshness and ordering risk live
(`ANALYSIS.md` §4.4–4.5).

### 4.3 Pseudocode (from `IdtxExecutor.sol` semantics; Engineer to verify line-by-line before thesis use)

```
IDTX_EXECUTE(tx):
  id      ← tx.namedIdentity                    # an identity OTHER than tx.sender's own record
  dep     ← tx.dependency                       # kind ∈ {ownership, delegate, attribute, revocation, history}
  state   ← LOAD(id, dep, locus)                # L0 plaintext | L3 commitment | L4 carried attestation | L1 receipt proof
  require PREDICATE(dep, state, tx.args)        # evaluated during execution, not at admission
  apply   tx.effect                             # effect outside id's own record

TWO_STEP (createIntent / fulfil):               # off-chain decision, on-chain re-check
  intent ← record(tx, snapshot(dep))
  ...later...
  require PREDICATE(dep, LOAD(id, dep, locus))  # re-check closes in-execution gap, NOT the ordering race (AR-10)
```

### 4.4 Figures to produce (Visual Architect; extend `make_focus_figures.py` style, one data table per figure)

| ID | Figure | Kind |
|---|---|---|
| P1-1 | The minimal set as a lifecycle ring (create → resolve → rotate/delegate/attribute → execute → deactivate), Set B as a side loop | structure |
| P1-2 | Primitive stack: keys/signatures → identifier → document → credential → presentation → IDTx | layered |
| P1-3 | IDTx three-axis cube (dependency kind × locus × evaluation point), the 4 Phase-1 IDTx plotted | taxonomy |
| P1-4 | Same decision, three worlds: centralized PDP call vs V2X PKI cert check vs on-chain IDTx (sequence diagrams side by side) | analogy |
| P1-5 | Inventory funnel: 26 gates → 6 classes → 4 IDTx | finding |
| P1-6 | Minimal set → full SSI extension (catalogue's added axes: cost, lifecycle, read path, scale, breadth) | extension |

### 4.5 Why no benchmark exists — the argument to build and then let the Skeptic attack

Claims (each needs evidence from Scout/Scholar before it is stated as fact):
1. **No agreed workload.** SSI evaluation papers measure their own operations on their own substrate; there is no
   common reference set of identity operations (the minimal set is our proposal for one).
2. **No agreed admission rule.** The W3C DID Method Rubric is a qualitative evaluation aid, not a performance or
   conformance benchmark; DID/VC test suites check *format conformance*, not lifecycle cost or dependency semantics.
3. **No unit for IDTx.** Prior art (ERC-3643/ONCHAINID, ABAC) implements identity-gated transfers but does not
   classify the dependency or its freshness, so results are not comparable.
4. **Cross-domain mismatch.** Centralized ID is assessed by assurance level (NIST SP 800-63), V2X PKI by latency/
   overhead, SSI by gas; no shared axis exists — the function set is that axis.

What would make it a benchmark (Phase 3 input): a fixed workload (F1–F12 + IDTx classes + lifecycle), a compliance
admission rule (the 12-test suite), a metric set with conditions (register M1-H etc.), a public harness, and at least
one independent reproduction.

### 4.6 Next actions in Phase 1

- [ ] Author decision on §0 (A/B/C)
- [ ] Recover verbatim F1–F12 from `cvin-sandbox-v1.3` to clear **[B1]** cells
- [ ] Scout + Scholar in parallel: benchmark-existence evidence; specs at source for §4.2 analogy column
- [ ] Engineer: verify §4.3 against `IdtxExecutor.sol` and tests
- [ ] Visual Architect: P1-1 … P1-6
- [ ] Skeptic pass on the assembled draft
