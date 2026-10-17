# BUILD_PLAN — Ordered Work Orders for the CLI Build Agent

Execute in order; each WO has explicit acceptance criteria (AC). Dependencies
are strict unless marked parallelizable. Per-WO closeout per CLAUDE.md
"Definition of done". Stage labels refer to the v2-0 three-stage methodology
(Stage 1 Native Sandbox → Stage 2 SSI Overlay → Stage 3 Gap Analysis).

---

## WO-0 — Ingest authoritative plan documents  [BLOCKING]
The 14-option family map in `docs/ARCHITECTURE.md` §2.2 has gaps marked ⊕
because it was reconstructed from session search snippets. Before any
family-dependent work:
- Obtain from the user (or project files) the **v2-0 Implementation Plan** DOCX
  and the **LFDT Integration Addendum**; extract to `docs/source/` as markdown.
- Reconcile the full 14-option member list; update ARCHITECTURE.md §2.2,
  removing all ⊕ marks; record any conflicts in FINDINGS.md (notably the
  "Family E" label collision with the building-paths document — carry the
  v2-0 meaning).
- Also request: Stage 12 session contract code (O2–O6), Identity Standard
  Inventory v2 DOCX, Stage 16/17 documents.
**AC:** ARCHITECTURE.md §2.2 complete with zero ⊕; `docs/source/` populated;
discrepancy notes filed.

## WO-1 — Port O2–O6 from Stage 12  [Stage 1]
Port the five completed implementations (ERC-721, ERC-725, ERC-725xy,
ERC-1155, ERC-4337) into `contracts/implementations/`, adapting to the current
interface set (IMinimalSSI + ISetA/ISetB/ISetC where applicable). Native
patterns per CLAUDE.md rule 2. If Stage 12 source is unavailable after WO-0,
implement fresh from the per-option NatSpec descriptions in the placeholder
headers + ARCHITECTURE.md §2.1.
**AC:** each option compiles, passes 12/12 in `test/compliance.js`; gas snapshot
committed; deviations vs §2.1 scoring anchors noted in FINDINGS.md.

## WO-2 — Build O7 (ERC-8004)  [Stage 1]
Three registries: Identity (ERC-721 base, CAIP-10 identifiers, tokenURI →
agent capability JSON), Reputation (0–100 scores, evidence URIs), Validation
(request/status hooks). Implements IMinimalSSI + ISetC (the reference Set C
implementation).
**AC:** 12/12 compliance + ISetC exercised by a unit test; mainnet-deployed
ERC-8004 consulted for fidelity (cite addresses in NatSpec).

## WO-3 — Build O8/E1 (Indy-on-Besu adapter)  [Stage 1]
Indy semantics in Solidity: nym registration (nymTx → createDID), attrib
(updateDID), schema + cred-def registries (issueCredential anchoring),
revocation registry entry (revokeCredential). Reference the indy-besu
(did:indy:besu, Oct 2024) repo structure.
**AC:** 12/12 compliance; mapping table Indy-tx-type → IMinimalSSI function in
NatSpec + docs.

## WO-4 — Scenario catalog S2–S4  [Stage 1; parallelizable with WO-2/3 after WO-1]
Implement `scenarios/run_s2_dualmode.js`, `run_s3_evcharging.js`,
`run_s4_insurance.js` per ARCHITECTURE.md §4 (tier mapping, function lists,
ICBC example in S4). Each parameterized by IMPL like S1.
**AC:** all three run against every enabled option; traces committed; per-tier
function coverage summarized in docs.

## WO-5 — Benchmark extraction  [Stage 1 → outputs feed Stage 3]
Port/rebuild the Stage 15 extraction: run S1–S4 across all enabled options;
emit `benchmarks/gas_matrix.csv` (option × function), `coverage_matrix.csv`
(option × F1–F12 × {native|assisted|absent}), and a markdown report comparing
against spec §5.3 targets and the /24 anchors.
**AC:** matrices generated from traces (not hand-entered); report flags every
target miss; FINDINGS.md updated.

## WO-6 — Identity Sandbox Explorer (Layer 2)
React artifact per `explorer/README.md`: trace upload/paste → identity cards,
tx timeline (F-tags + gas), I2I channel pane with revocation teardown, 12-function
coverage tracker, option selector when multiple traces loaded. No simulated
data — renders traces only.
**AC:** S1 trace renders all panels; a malformed trace fails gracefully with a
schema error message.

## WO-7 — S5 IDPP port scenario  [after WO-3]
Port an identity + credential set O1 → O8/E1 within one script: create on O1,
issue VID, export state, re-anchor on E1, verify continuity (old DID
deactivated with pointer, credential re-anchored, verification passes on
target). This operationalizes the 2020 paper's ID Porting Protocol.
**AC:** trace shows the full port; continuity assertions pass; write-up stub
in docs (this is a thesis finding candidate).

## WO-8 — Caliper harness  [Stage 3 instrumentation; after WO-5]
Caliper workload modules for the 12 functions against the Hardhat network
(and Besu QBFT when available, per Stage 18 plan). Output TPS, p50/p95
latency, gas/op per option → `benchmarks/caliper/`.
**AC:** modules run for ≥2 options end-to-end; results format matches the
Stage 18 three-tier analysis needs (<100ms / 100–500ms / >500ms mapping).

## WO-9 — Set B overlay adapters  [Stage 2; coordinates with Stage 19]
`contracts/credentials/` anchor adapters for SD-JWT and AnonCreds/BBS+
presentation anchoring (hash + status on-chain, proof off-chain). AnonCreds is
the coverage ceiling reference — document each ERC option's Set B path as
{native | anchor | Aries-assisted} in the coverage matrix.
**AC:** at least one adapter wired into S2/S4 scenarios; coverage matrix gains
the Set B path column.

---

## Out of scope (do not build; propose only)
Family F synthesis (Stage 3 output), E2 Identus deployment (non-EVM; analysis
doc only unless directed), Stage 31 agent wrapper (S6) beyond ISetC, mainnet
deployments of any kind.

## Standing questions for the user (ask when hit, don't guess)
1. v2-0 plan DOCX + Stage 12 code availability (WO-0/WO-1).
2. Besu QBFT target: local container vs hosted (WO-8).
3. OpenZeppelin version pin preference (WO-1).
4. Whether E3 AnonCreds harness (anoncreds-rs, Python) should live in this repo
   or a sibling (it is non-Solidity).

---

## v3-0 Addendum Work Orders (Solution Paths SP-1 / SP-2)

## WO-1a — SP-2 composite contracts  [Stage 1; after WO-0 package check]
Implement `contracts/implementations/SP2_ERC725_735.sol` (identity proxy with
purpose-typed keys + ERC-735 claims) and `contracts/implementations/ClaimIssuerRegistry.sol`
(trusted-issuer/topic registry — role attributed to ERC-740 [R1]; cite verified
EIP number in NatSpec once token resolves). Native patterns per CLAUDE.md rule 2.
**AC:** compiles at 0.8.24 alongside existing contracts; 12/12 compliance enabled.

## WO-1b — SP-2 behavioural test series  [Gates G3–G5]
Implement test series T-725-01..04, T-735-01..03, T-740-01..03 per v3-0 §4.
Each test logs its verdict (F/P/×) into traces/sp2_verdicts.json.
**AC:** all tests run; verdict file generated; FINDINGS.md updated with any
expectation deviations from v3-0 Table 3.2.

## WO-R — Placeholder resolution pass
When research results arrive: resolve [R1]–[R5] in the v3-0 document source,
update Table 3.1 repository rows, and regenerate the DOCX. [R6] resolves only
from WO-1b verdict output.
**AC:** zero unresolved tokens; v3-0 status flips Provisional → Final.
