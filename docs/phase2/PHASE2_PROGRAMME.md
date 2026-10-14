# Phase 2 Programme — The Consolidated Document

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (after-action report 16). **State:** Phase 2 at the end of P2.0 (ideation), with the three
author-designated focuses captured, analysed, planned and started. **Binds:** `docs/phase2/README.md` (charter and
session protocol), `docs/STYLE_AND_RIGOUR_GUIDE.md`. **Supersedes:** nothing; it gathers the Phase 2 documents into one
reading. Every number is a register row (`#n` = `docs/MEASUREMENT_CONDITIONS.md`).

## 1. Executive summary
**What Phase 2 is.** Phase 1 is the thesis artefact. It compares nine Ethereum identity standards on one vehicle
lifecycle, adds a W3C credential layer and a V2V/V2I verification testbed, and checks every claim against a register.
Phase 2 is the programme that grows from what Phase 1 measured and left open. It is built across sessions:
ideation, then architecture, then planning, then build waves, with the author choosing at each gate.

**Where it stands.**
- **P2.0 is complete.** The charter, evidence base, a 26-idea register checked in CI, an architecture sketch, a
  roadmap and the first brainstorm are written.
- **The three focuses you designated are each a complete package:** capture of Phase 1 evidence, analysis, a
  pre-registration draft, and a first executed step. F1 is on-chain storage and the identity-dependent transaction
  (IDTx); F2 is public and private chains and databases; F3 is the modes of communicating with the chain.

**The three findings that matter most.**
1. **Storage choice decides what can depend on identity, not only what it costs.** Writing identity state costs gas
   in proportion to new storage slots: 8 to 149 over one lifecycle, and 1.05 to 5.80 million gas (#49, #35). Keeping
   data in event logs is cheap to write, costly to read (112 RPC calls at history 50, #31), and invisible to every
   contract. The IDTx definition makes the second point formal.
2. **The chain's value is verification by parties who do not trust the operator, not speed.** A database is three to
   four orders of magnitude faster on writes (#33). A careful database with a hash-chained journal still cannot reveal
   a full rewrite by its own operator without an anchor kept outside, which the F2 prototype demonstrates.
3. **Only the detached mode fits the safety budget.** Verifying one vehicle message costs:
   - detached (cached credential, no chain contact): 0.153 ms (#27);
   - a direct probe: 2.76 ms (#37);
   - a direct full resolution: 9.654 ms (#21).

   On the autonomous radio sidelink a vehicle has no network path, so the detached mode is forced. That is why the
   cached, anchored design is the right one.

**What the review team recommends** (the career ECE academic's scope reconciliation):
- **Freeze the thesis on Scope v3.** It keeps the four research questions, restated so that each is answered by
  existing V rows, and reports H1 and H5 as split verdicts.
- **Put F1–F3 into the thesis as concepts on existing evidence.** That means the storage-locus table, the IDTx
  definition and taxonomy, and the mode taxonomy, with no new experiment.
- **Write chapter 2 next.**
- **Make the measured IDTx study the first paper after the thesis, under your name.**

## 2. Phase 1 in one table (the base Phase 2 stands on)
| Result | Value | Row |
|---|---|---|
| Create-identity gas across nine standards | 52,216 to 1,757,881 (33.7×) | #25 |
| Lifecycle gas, 17 events | ERC-1056 1,050,809 cheapest; ERC-735 5,797,549 (excl. 3 n/a) | #35 |
| New storage slots over the lifecycle | 8 (ERC-1056) to 149 (ERC-735) | #49 |
| Relayed write over direct | ERC-1056 +27,622 gas; ERC-4337 +47,116 | #50, #34 |
| V2V verification, warm SSI | 0.153 ms [0.151, 0.154] | #27 |
| Uncached chain-backed verification | 9.654 ms median | #21 |
| Staleness bound with a re-check every k messages | at most k − 1 messages | #46 |
| Attack harness | 43 of 43 applicable cells defended | #28 |
| W3C | structural self-score 94.3 %; external DID suite 335/336 | #4, #24 |
| Database vs chain lifecycle writes | about 1,600× to 6,000× slower on chain | #33 |

## 3. Scope: how Phase 2 joins the thesis
The scope has had two attempts:
- **First attempt:** the thesis statement with RQ1–RQ4 and H1–H5.
- **Second attempt:** the audit-era narrowing, with scope changes SC-01 to SC-22 and the crux register. It narrowed
  every claim but never rewrote the questions.

**Scope v3, the third attempt, restates the questions to the evidence** (`SCOPE_RECONCILIATION.md` §2):

| RQ | Restated | Rows |
|---|---|---|
| RQ1 Cost and storage locus | gas for an identical catalogue and lifecycle, and the on-chain state each standard keeps for that price | #6, #25, #26, #34, #35, #36 (and #49) |
| RQ2 Security and observability | what the executable harness shows each standard resists, and what a passive observer learns | #28, #38 |
| RQ3 Standards expression | how far identities are expressed in W3C and a MOBI-VID-inspired lifecycle, structurally and by the external suite | #4, #24, #30, #33 |
| RQ4 Real-time verification | whether verification fits the computational share of the safety budget, with revocation freshness priced | #21, #27, #32, #37, #44–#48 |

**Where the three focuses go:**

| Focus | In the thesis (existing evidence) | Before the defence (only if a bounded WM-3 is opened) | After the thesis |
|---|---|---|---|
| F1 storage and IDTx | storage-locus table; IDTx definition and taxonomy; the C8 observation (event-held attributes cannot condition a contract) | none recommended | paper P5: measured IDTx study (prototype ready) |
| F2 substrates | the transfer table; #33 and #21 as the two substrate comparisons | Sepolia witness (N-11) | paper P7: four-substrate study (database backend ready) |
| F3 modes | the mode taxonomy; measured write paths (#50) and read modes (#21, #37, #27) | one B-serve point through Sepolia | paper P4: interaction modes; mode selection per message class |

## 4. The three focus packages
| | F1 storage and IDTx | F2 chains and databases | F3 interaction modes |
|---|---|---|---|
| Question | where identity data lives, and what each choice buys, costs and forbids | which ledger or database, and which Phase 1 results transfer | who carries a request to the chain at the moment of use |
| Capture | 25 IDTx instances already in Phase 1; storage per standard and datum | one local chain; in-memory registry; no private chain, no public run | direct and relayed writes; three measured read modes; no provider-served read |
| Analysis | six storage loci; IDTx definition; five-axis taxonomy; threats; cost model | transfer table; substrate taxonomy; hybrid placement by data class | A direct, B-submit, B-serve, C detached; costs, trust, privacy, staleness; radio coupling |
| Plan (drafts) | E-F1-1 to E-F1-4 | E-F2-1 to E-F2-4 | E-F3-1 to E-F3-4 |
| Executed | IDTx prototype, 10 tests, 3 mutants caught | database backend with hash-chained journal, 6 tests | classification of all operations and 1,752 demo steps, in CI |
| Figures | F1-1 state vs gas; F1-2 read cost vs history | F2-1 lifecycle parity | F3-1 write paths; F3-2 read modes |
| Folder | `focus/F1_onchain_storage_idtx/` | `focus/F2_chains_and_databases/` | `focus/F3_interaction_modes/` |

## 5. The identity-dependent transaction, in brief
> An **identity-dependent transaction (IDTx)** is a state transition whose execution is conditioned on a predicate
> over identity state held by a ledger, evaluated at execution time, either inside the transaction or by an agent
> whose transaction re-evaluates it before acting.

It differs from an ordinary access check in three ways:
- the condition is about a third-party identity, not only the caller;
- the state is held by a ledger;
- a change between decision and execution changes the outcome.

**Five axes classify any instance:**
- dependency (ownership, delegate, attribute, status, history);
- locus (state, commitment, event, anchored credential);
- encoding (plaintext, salted hash, ciphertext digest, proof);
- evaluation (in-contract, agent then re-check, off-chain only);
- continuation (same transaction, next transaction, message acceptance).

**The analysis shows the axes constrain each other.**
- Event-held data rules out in-contract evaluation.
- Encrypted data allows equality only.
- Off-chain evaluation opens a time-of-check to time-of-use gap that only an on-chain re-check closes.

The prototype demonstrates each point in a test. The scope reconciliation names the prior art to position against,
to be confirmed at source: ERC-3643 with ONCHAINID, account-abstraction validation, oracle-conditioned execution, and
transaction-order dependence.

## 6. Decisions open for the author
| # | Decision | Default until decided |
|---|---|---|
| P2-D1 | Which programme | PG-focus (the three focuses) as the spine, documents-only until the defence |
| P2-D2 | Phase 2 time box | documents only until the defence; build waves after (academic's D-13) |
| P2-D7 | The three modes | two options on the table: the academic's (write: direct, relayed, account-abstracted; read: on demand, cached, offline; all six cells measured) for the thesis, and the orchestrator's single axis (A direct, B-submit / B-serve, C detached) as Phase 2's analytic frame; they map onto each other (`focus/F3_interaction_modes/ANALYSIS.md` §2) |
| P2-D8 | One name for the concept | IDTx; IDDTx and IDBTx retired |
| P2-D9 | Install a permissioned EVM client for F2 | no, until after the defence |
| D-1 … D-15 | The scope reconciliation's fifteen (Scope v3, "first", "throughput", split verdicts, title, chapter 2 next, …) | as recommended there |
| N-23 | AI-use disclosure | open (Phase 1) |

## 7. What happens next
**Phase 1, WM-2.** The next step is B1 (deterministic gas or ranges). Then B2, C3, C1, C2, the re-runs (A3, A3b, A6),
A5 and the chapter checks (D1).

**Phase 2 session 2:**
- apply the review team's findings;
- write deep-dive briefs for I-24 (IDTx) and I-05 (freshness theory);
- start chapter 2's positioning of IDTx, if the author adopts D-15.

**Chat-workspace hand-off.** `CHAT_WORKSPACE_BRIEF.md` lets the author run literature, standards and tool work in a
chat workspace with web and document tools. It says what to bring back and in which format, so the results can be
woven in here.
