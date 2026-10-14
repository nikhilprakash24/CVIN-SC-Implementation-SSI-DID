# Chat-Workspace Brief — Phase 2 Work to Run Outside the Code Repository

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (after-action report 16). **For:** a general-purpose assistant workspace with web search, document
reading and file tools, used by the author to run literature, standards and drafting work that a code session cannot
do well. **Revised:** 2026-10-14 after the academic review (IDTx definition; reading list in `docs/phase2/reviews/ACADEMIC_REVIEW_F1-F3.md` §3.1). **Returns to:** `docs/phase2/inbox/` in this repository, where the next code session verifies and weaves it in.

## 0. How to use this brief
1. Start a conversation in the chat workspace. Attach this file and `docs/phase2/PHASE2_PROGRAMME.md`. Attach the
   focus READMEs too if you have room: `docs/phase2/focus/F1_onchain_storage_idtx/README.md`, `.../F2_.../README.md`,
   `.../F3_.../README.md`.
2. Paste the **opening prompt** in §6. Then work through the packages in §3, one per conversation if they are long.
3. Save each package's output as one Markdown file named as §4 says. Put the files in `docs/phase2/inbox/` (commit
   them, or hand them to the next code session).
4. The next code session runs the intake in §5. Nothing from the chat side becomes a claim until it is checked there.

## 1. Context the assistant needs (one page)
**The project.** A UBC ECE MASc thesis on rooting connected-vehicle identity in blockchain identity standards. It
compares nine Ethereum standards on the same operations and a 17-event vehicle lifecycle:
- ERC-1056, ERC-721, ERC-725, ERC-725xy, ERC-735, ERC-1155, LSP8 and ERC-4337;
- a hybrid called CVIN-Combined;
- a MOBI VID-inspired profile.

It adds a W3C Verifiable Credentials layer, and a V2V and V2I message-verification testbed under simulated
mobility. Every number has a row in a claim register with a status, and only "V" (verified) numbers may be quoted.

**Phase 2** is the programme after the thesis core. It has three focuses the author designated:
- **F1, on-chain storage versus not, and the identity-dependent transaction (IDTx).** The author's term, with this
  working definition: a transaction whose admissibility or effect is a function of the state of an identity the
  transaction names, evaluated during execution from ledger state or from a carried attestation or proof. It
  excludes sender authentication and administration of the record being modified. The off-chain counterpart is an
  identity-dependent decision.
- **F2, public and private blockchains and other databases.**
- **F3, the modes of communicating with the chain.** Two candidate taxonomies are on the table:
  - write: direct, relayed, account-abstracted; read: on demand, cached, offline;
  - one axis for both: A direct, B mediated (B-submit / B-serve), C detached.

**Numbers you may quote, exactly as written, with their row:**

| Number | Row |
|---|---|
| Create-identity gas 52,216 to 1,757,881 (33.7×) across nine standards | #25 |
| Lifecycle gas: ERC-1056 1,050,809 (cheapest); ERC-735 5,797,549 (excl. 3 n/a) | #35 |
| New storage slots over the lifecycle: 8 (ERC-1056) to 149 (ERC-735) | #49 |
| Relayed write over direct: ERC-1056 +27,622 gas; ERC-4337 +47,116 | #50, #34 |
| V2V warm verification 0.153 ms [0.151, 0.154] (M0); uncached chain-backed verification 9.654 ms (M1, a different run: never form a ratio across them) | #27, #21 |
| A re-check every k messages accepts at most k − 1 messages after a revocation | #46 |
| ERC-1056 document resolution at history 50: 112 RPC calls, 87 KB | #31 |
| W3C structural self-score 94.3 %; external DID test suite 335/336 | #4, #24 |

Any other number about this project must come from the repository, not from the chat.

## 2. Rules for the chat side
1. **Never invent a result, a citation or a page number.** Mark every source either **checked** (you opened it and
   read the passage) or **recalled** (from memory, unverified). Recalled items are leads, not citations.
2. **Give retrieval dates** for anything online: specifications, call-for-papers deadlines, pricing.
3. **Do not quote numbers about this project** beyond §1's table.
4. **Keep the author's names.** IDTx (not IDDTx or IDBTx); focus ids F1 to F3; idea ids I-nn; decision ids P2-Dn.
5. **Plain style:** lead with the answer, one idea per sentence, tables for parallel facts, no em-dashes.

## 3. Work packages
### W1 Literature and positioning for IDTx and chapter 2 (highest priority)
**Find, read at source, and summarise.** For each item, return the exact citation (BibTeX), the passage that
matters, and one line on how it relates to F1, F2 or F3. The scope reconciliation names these as recalled leads:
- **Permissioned tokens over on-chain identity:** ERC-3643 (T-REX) and ONCHAINID; ERC-734/735.
- **Account abstraction:** ERC-4337 (`validateUserOp`, paymasters).
- **Oracle-conditioned execution:** Town Crier, and an oracle network's documentation.
- **Transaction-order dependence and front-running:** Luu et al., CCS 2016; the front-running SoKs.
- **Attribute-based access control:** NIST SP 800-162.
- **Credentials and private contracts:** anonymous credentials and ZK attribute proofs (Coconut; zk-creds);
  confidential contracts (Hawk); FHE-enabled EVMs.
- **Gas costs of storage:** the EIPs that set storage-write and access costs (EIP-2200, EIP-2929, EIP-3529), and the
  state-growth and state-expiry discussions.
- **Ledger performance methodology:** BLOCKBENCH.

**Then:** a one-paragraph related-work positioning of IDTx, and a list of what IDTx can and cannot claim as new.

### W2 Substrates and modes: specifications (F2, F3)
**Extract, with section numbers:**
- **Permissioned EVM consensus:** one permissioned client's BFT consensus (block time, finality, validator set) and
  its permissioning model.
- **Rollups:** one rollup stack's sequencer trust and data-availability model.
- **Verified reads:** `eth_getProof` (EIP-1186) and one light client, for verified reads (F3 B-serve).
- **Vehicle PKI:** IEEE 1609.2 and the SCMS architecture, for the PKI baseline; C-V2X sidelink Mode 3 and Mode 4
  (3GPP Release 14), for the radio coupling.
- **Credential formats:** SD-JWT VC and BBS signatures.
- **Regulatory frame:** the EU digital identity wallet architecture reference framework, for a vehicle as a
  credential holder (idea I-17).

### W3 Venues and dates for the paper map
**For the venues in the paper map, give the next deadline, page limit, scope fit and URL, with the retrieval date:**
IEEE ICBC, IEEE VTC (spring and fall), IEEE VNC, the ACM CCS workshops (security and privacy in blockchain; WPES),
IEEE Access, IEEE T-ITS and ACM REP.

### W4 Notebook intake (idea I-20)
**For each research thread in the author's notebooks, fill one row:**

| Thread | Claim or question | Evidence it needs | Phase 1 anchor (row, crux, defect) | Phase 2 idea it joins, or "new" |
|---|---|---|---|---|

### W5 Drafting help, bounded
Each item draws only on the numbers in §1 and on checked sources:
- an outline for chapter 2 (literature review);
- a related-work section draft for the IDTx paper;
- a one-page answer to each of the examiner questions in `docs/phase2/SCOPE_RECONCILIATION.md` §5.

### W6 Decisions worksheet
**List each open decision with the author's choice.** Use the default where the author does not decide:
- P2-D1, P2-D2, P2-D7, P2-D8, P2-D9 (`docs/phase2/DECISIONS.md` and `PHASE2_PROGRAMME.md` §6);
- the scope reconciliation's D-1 to D-15;
- Phase 1's N-23 (AI-use disclosure).

## 4. What to bring back, and in which format
| Package | File name in `docs/phase2/inbox/` | Must contain |
|---|---|---|
| W1 | `W1_LITERATURE_<date>.md` plus `W1_refs.bib` | per source: citation key, checked or recalled, the passage, relation to F1/F2/F3; the positioning paragraph |
| W2 | `W2_SPECS_<date>.md` | per specification: the section numbers and the facts extracted, each with its retrieval date |
| W3 | `W3_VENUES_<date>.md` | a venue table with deadlines and retrieval dates |
| W4 | `W4_NOTEBOOK_INTAKE_<date>.md` | the intake table; for new ideas, entries in the `ideas.yaml` schema (§4.1) |
| W5 | `W5_DRAFT_<topic>_<date>.md` | the draft, with every number tagged with its row and every citation with its key |
| W6 | `W6_DECISIONS_<date>.md` | decision id, choice, a one-line reason |

### 4.1 The `ideas.yaml` schema, for new ideas
```yaml
- id: I-NEW-1            # the code session assigns the real id
  track: T               # R realism, T trust, P privacy, A assurance, S standards, E evidence platform, W writing
  title: "..."
  question: "..."
  why: "..."             # the Phase 1 gap or result it starts from
  anchors: ["#27", C4]   # register rows, cruxes C1-C8, defects Dn, deferred items N-n, side papers SP-n, scope changes SC-nn
  builds_on: [path/in/the/repository]
  first_step: "..."      # one or two sessions
  kill: "..."            # written before the first step runs
  depends: []
  scores: {value: 3, novelty: 3, feasibility: 3, reuse: 3, risk: 3}   # 1-5, the author's estimate
```

## 5. Intake in the next code session (for the record)
1. Read each inbox file and check every "checked" citation against its source where it is reachable.
2. Move verified citations to the thesis bibliography. Keep recalled ones as leads in the file.
3. Merge new ideas into `docs/phase2/ideas.yaml`, run `python3 docs/phase2/build_phase2.py`, and fix any anchor the
   checker rejects.
4. Record decisions from W6 in `docs/phase2/DECISIONS.md` and `docs/MILESTONE_NEXT.md` before acting on them.
5. Log the intake in the session's after-action report and in `docs/phase2/sessions/SESSION_LOG.md`.

## 6. Opening prompt (paste into the chat workspace)
> You are helping me with Phase 2 of my MASc thesis on blockchain identity for connected vehicles. Attached are the
> brief and the consolidated Phase 2 document. Follow the brief's §2 rules exactly:
> - never invent results or citations;
> - mark every source checked or recalled;
> - give retrieval dates;
> - quote no project numbers except those in §1.
>
> Start with work package W1. Search for and read each source at its origin, then return the W1 file in the §4
> format. Before starting, ask me nothing unless a source cannot be found; in that case list it as "not found" and
> continue.
