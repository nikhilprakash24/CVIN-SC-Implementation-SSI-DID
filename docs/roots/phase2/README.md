# Roots Thread G-R1 · Phase 2 — Full-Stack Depth and the Reverse Direction

**What Phase 2 is, every file it produced and why, what it found, what to lock in the thesis, and where each open item goes next.**

v1.0 · 2026-10-23 · Branch `roots/G-R1-phase2` · Builds on Phase 1 (`../phase1/README.md`) · Progress `▓▓▓▓▓▓▓▓▓░ 90 %` (v0-3 sweep and Phase 3 measurements outstanding)

---

## 1. What Phase 2 set out to do

Phase 1 traced decentralised identity and secure I2I communication back to their roots — Bitcoin's ledger lineage and the parallel identity/cryptography lineage — and organised everything on an eight-layer stack (L0 network … L7 application), with 51 breaking points and 31 numeric bounds. It stayed at the level of primitives and architectures.

Phase 2 asked for two more things:

1. **Go deeper and more complete, bottom-up** — from hardware and silicon through radios, operating systems, node clients, P2P and RPC, storage engines, consensus implementations, the EVM, transaction formats, *the actual smart-contract code in this repository*, credential formats, wallets and V2X message standards — and tie every piece back to the Phase 1 roots in the same "enabled by / secured by" discipline.
2. **Then go top-down** — start from the programme's own functionality (a transaction, a VC endorsement, a read, a signature, the IDTX functions, smart-contract functions, the network, the DLT and its implementation) and anchor each item down to its roots, with the dimensions it can be measured on (time to confirm, decentralisation confidence, trilemma position, smart-contract and protocol security …) and parameters declared for later.

It was run as a multi-agent task with four roles: a **cybersecurity and distributed-systems engineer** (R6), a **theoretical-CS and ECE engineer** (R7), a **technical writer and information architect** (R8) with a **visual designer** (figures), and **the professors as one combined panel** (R9) who reviewed everything, ruled on disputes and issued the solidify list. Every document has a first pass (v0-1) and a second pass (v0-2) that applies the panel's findings; both are kept.

## 2. The four things Phase 2 established

These are the conclusions that change how the thesis should be written. Each is ruled on in R9 v0-2.

1. **The executed system is a single automining Hardhat node.** Besu/QBFT, public anchoring and the HAA-1 hybrid exist only as design. Gas measured on Hardhat carries across EVM chains; latency and finality do not. Every consensus-dependent figure is DESIGN (SLD-01, SLD-13; Phase 1 erratum X-1).
2. **On the safety-message path, the ledger is not the bottleneck — the vehicle's verifier and the radio channel are.** At 10 Hz, verification hardware saturates at tens to hundreds of neighbours depending on class; the repository's JSON message format costs 2.9×–5.0× the airtime of a compact 1609.2 digest-signed message (R7 PF-43/44; SLD-03, SLD-04; FIG-R15).
3. **The code carries real security findings that the design documents did not.** Signed registry operations are replayable across chains (D52 — structural, because both chains deploy from Hardhat's default accounts); the on-chain pseudonym pool is fully linkable (register #38), and changing pseudonym without changing radio resource leaves a vehicle linkable at the radio layer with probability ≈ 0.14–0.80; unsalted VIN hashes are enumerable in seconds; the ZK-VIN trusted setup is single-party; 20 of 44 state-changing functions lack a negative access-control test (R6 v0-2; SLD-06/07/08/09/16).
4. **Only 77 of 418 functionality × dimension cells are actually measured today (18 %).** Eight dimensions — including finality, decentralisation confidence, trilemma position and availability — have no measured cell at all, because those require a multi-node run nobody has scheduled (R8 v0-2 §5; FIG-R11). This is the map of where future measurement must go.

## 3. Every file, and what it is for

### 3.1 Control

| File | What it is | Why it exists |
|---|---|---|
| `00_control/PHASE2_SHARED_BRIEF.md` | The single brief every agent read first: goals, the extended stack (LH + sub-layers L0.1–L7.3), tag namespaces and owners, honesty statuses, file names, house style | So four independent agents produced documents that fit together and never redefined each other's tags |

### 3.2 R6 — Full-Stack Atlas (forward, bottom-up) · cybersecurity and distributed-systems engineer

| File | Explanation |
|---|---|
| `60_R6_full_stack_atlas/…R6_v0-1.md` | First pass, ≈ 13.7k words. Extends the stack with a hardware layer **LH** (CPU and RNG, secure elements, vehicle E/E, radios and GNSS, node hosts) and sub-layers inside L0–L7. A register per layer of every component — hardware (`HW-`), protocols (`PRO-`), algorithms (`ALG-`), implementations (`IMP-`) — each with what it does, what secures it (down to Phase 1 roots), what it enables, and its status *in this programme*. A full **smart-contract function register for this repository** (117 `SCF-` rows across 22 contracts: ERC-1056, ERC-721, ERC-725/725xy, ERC-735, ERC-1155, ERC-4337, LSP8, MOBI VID v1/v2, CVIN-Combined, IdtxExecutor, the Groth16 verifier, the steward). 39 new breaking points (`BP-LH-`, `BP-Lx.y-`). New solutions SOL-10..17. Worked "secured-by" traces from a repo function down to silicon. A measured-vs-designed table for the whole stack. |
| `60_R6_full_stack_atlas/…R6_v0-2.md` | Second pass, ≈ 15.6k words. Applies all 11 panel findings against R6: defect statuses now match `docs/DEFECT_LOG.md` (D18/D21/D22 shown fixed, with what remains open), D52 explained as structural, a reentrancy audit of four surfaces (no checks-effects-interactions violation), a negative-test check of 44 state-changing functions (20 lack an unauthorised-caller test), message freshness separated from state freshness, three new breaking points (radio-resource linkability, no TTL on cached state, JSON size vs channel capacity). Every layer opens with an "elevator" paragraph and ↑/↓ cross-links. SOL-12/15/17 demoted to mechanisms; SOL-16 kept as a solution (the panel accepted, counted with SOL-05). **Use this version.** |

### 3.3 R7 — Theory and ECE Bounds · theoretical-CS and ECE engineer

| File | Explanation |
|---|---|
| `70_R7_theory_ece_bounds/…R7_v0-1.md` + `r7_calc.py` | First pass, ≈ 10.6k words, with a script that computes every number. Extends Phase 1's notation (SYM-25..58) and standard results (SR-L..T: ECDSA in the generic group model, sponge/ROM, Groth16/AGM, Pedersen, QBFT, DLS, CAP/PACELC, renewal theory, EIP-1108). Security reductions; a composition lemma (identity binding is as strong as the weakest of signature, registry non-equivocation and resolver integrity); QBFT message complexity; hardware RNG, HSM/ECU verification load, 802.11p/PC5 airtime, GNSS time error, RSU backhaul intermittency; per-function gas from the claim register turned into capacity; freshness formalised; metric definitions for every measurement dimension. Converted several Phase 1 estimates into measured or derived values. |
| `70_R7_theory_ece_bounds/…R7_v0-2.md` + `r7_calc_v0-2.py` | Second pass, ≈ 13.1k words. Fixes the panel's findings: a units error in the "ledger is not the bottleneck" condition (threshold 27.9, not 278.8, at 100 neighbours), the radio-persistence probabilities recomputed exactly (0.136 / 0.449 / 0.805), the event-log cost (375-gas base added; storage-vs-log 18–28× depending on whether the EIP-7623 calldata floor applies — disputed with the panel by arithmetic and accepted), script labels made identical to the document's PF numbering with a self-check, PF-45/46 filled, and **PF-63..66** added at R8's request (test-key entropy, lying RPC endpoints vs proof-backed reads, client-monoculture correlated failure, single-key governance roles). Every bound has a "So what" line. **Use this version; run the script to reproduce.** |

### 3.4 R8 — Reverse Anchor Register (top-down) · technical writer and information architect

| File | Explanation |
|---|---|
| `80_R8_reverse_register/…R8_v0-1.md` | First pass. Starts from what the programme *does* and anchors each item down. 19 categories (`RV-TX` transactions, `RV-IDTX` identity transactions and the IMinimalSSI functions, `RV-VC` credentials incl. endorsement, `RV-SIG` signatures and keys, `RV-READ` reads and resolution, `RV-PRIM` primitives, `RV-ALG` algorithms, `RV-PROT` protocols, `RV-SC` contracts, `RV-SCF` contract functions, `RV-NET` network and nodes, `RV-DLT` the ledger as a system, `RV-IMPL` implementations of the DLT, `RV-HW` hardware, `RV-SVC` off-chain services, `RV-SCN` scenarios, `RV-GOV` governance, `RV-MET` evaluation artefacts, `RV-THR` attacks as measurable operations), 301 short rows. 22 measurement dimensions (`MD-`), 30 declared parameters (`PAR-`, not filled — "parameter after"), five worked anchor chains, a coverage matrix and a "where to deepen" routing table. |
| `80_R8_reverse_register/…R8_v0-2.md` + `r8_coverage.py` | Second pass. 311 rows, zero placeholders (all resolved to real R6/R7 tags). Option mapping corrected to Phase 1 R2; overclaimed rows downgraded (the ERC-725 `execute` stub; pseudonymity rows now record the measured *negative* result). R8 now **owns `PAR-01..43`** (R7's parameters merged in), every dimension cites its R7 formula, the coverage matrix is recomputed by script in four states (77 measured · 3 derived-only · 115 design · 223 empty), each category ends with a "Deepen next" line naming the chat and the first question, and **§7 is the DID / DID-system primitives lock list** (21 rows with blocking questions as checkboxes). **Use this version.** |

### 3.5 R9 — Professors' Panel Review · the combined panel

| File | Explanation |
|---|---|
| `90_R9_panel_review/…R9_v0-1.md` | Examiner-grade review of R6/R7/R8 v0-1 by seven voices (distributed systems, cryptography, theory, ECE/V2X, CAV/ITS, identity standards and policy, research methods). 33 findings (6 HIGH), each with evidence — including two arithmetic errors found by re-running R7's script and a units error. The re-keying scheme that fixed all tag collisions. 16 solidify directives, drop/demote and do-not-claim lists, 18 code actions mapped to the repo's defect numbers, the DID-primitives checklist, and instructions to each second-pass writer. |
| `90_R9_panel_review/…R9_v0-2.md` | Disposition pass. 26 findings closed, 4 partly closed, 2 disputes accepted, 0 rejected, 1 open (PN-33 — closed afterwards by the Phase 1 erratum). Six new findings (PN-34..39, none high; register row #26 was re-stated on 2026-10-23, moving R7's lead verification figure from 305 to 320 neighbours). **The final solidify list SLD-01..18**, final DROP and DO-NOT-CLAIM lists, code actions CA-01..24 with the thesis-blocking ones marked, the final primitives lock checklist, and the Phase 3 list. **This is the document to act on.** |

### 3.6 Figures · visual designer

| Figure (v0-2) | What it shows |
|---|---|
| FIG-R7 full-stack atlas | LH + every sub-layer as bands, key components with status markers |
| FIG-R8 measured vs designed | The honesty map: which sub-layers are measured, implemented-unmeasured, or design only (consensus and finality layers outlined) |
| FIG-R9 secured-by chains | Four vertical traces from a repo function, a V2X message and a ZK proof down to silicon, each ending at its weakest link |
| FIG-R10 reverse anchor categories | The 19 top-down categories by the level they start from, and where they anchor |
| FIG-R11 coverage matrix | 19 categories × 22 dimensions, four-state heat-map (77 / 3 / 115 / 223) |
| FIG-R12 anchor chain (revocation) | R8's lead worked chain: revoke a credential and observe W, step by step down the stack |
| FIG-R13 new breaking points | R6's 42 new breaking points by sub-layer × attack class (attack classes proposed by the designer — confirm) |
| FIG-R14 Phase 1 ↔ Phase 2 map | All nine documents, forward vs reverse direction, who owns which tags (README hero image) |
| FIG-R15 V2X bottleneck (new) | Verification load vs neighbours for hardware classes and the measured software verifier against the 100 ms Tier-1 budget |
| FIG-R16 revocation tail (new) | Revocation latency with intermittent RSU backhaul: mean vs tail quantiles — why W must be quoted as a tail |

`FIGURES_INDEX_v0-2.md` explains how to read each one and its caveats; `make_phase2_figures_v0-2.py` regenerates all of them and refuses to print any tag not found in the documents. The v0-1 figures and index are kept.

## 4. What to solidify for the thesis (R9 v0-2 §4, titles)

SLD-01 executed system is single-node Hardhat automine · 02 per-function gas vector · 03 Tier-1 bottleneck is verifier hardware (lead figure 320 neighbours) · 04 message size drives airtime · 05 freshness bounded in messages, not seconds (add a TTL) · 06 signature schemes and replay scope · 07 pseudonymity fails on chain and on the radio · 08 VIN enumerability · 09 ZK-VIN cost model with the setup caveat · 10 composition lemma (blocked until a blind re-derivation agrees) · 11 repository-to-option mapping · 12 measured-vs-designed table with 77/3/115/223 · 13 consensus bounds, design-only, in a new appendix · 14 revocation latency as tail quantiles · 15 primitives lock · 16 contract security vector · 17 event-log vs storage trade-off · 18 contribution list of five solutions.

## 5. Tag namespaces after Phase 2

| Owner | Tags |
|---|---|
| Phase 1 (frozen) | L0–L7, T-01..24, T-I01..22, SOL-01..09, BP-L0-01..BP-L7-07, SYM-01..24, PF-01..31, FIG-R1..R6 |
| R6 | LH and sub-layers, HW-, PRO-, ALG-, IMP-, SCF- (117), BP-LH-, BP-Lx.y-, SOL-10..17, Q-R6-, KD-R6- |
| R7 | SYM-25..58, SR-L..T, PF-32..66, Q-R7-, KD-R7-, CEV-R7-, LIM-R7- |
| R8 | RV-<CAT>- (311), MD-01..22, **PAR-01..43**, Q-R8-, KD-R8- |
| R9 | PN-01..39, SLD-01..18, DRP-, NC-, CA-01..24, RL- |
| Figures | FIG-R7..R16 |

Record keys are namespaced by issuing document (the panel's re-keying); every retired key has a strike-through line in its document's "Key changes v0-1 → v0-2" table.

## 6. What is left (Phase 3) and where it goes

| Item | Fills | Best chat |
|---|---|---|
| Multi-node Besu/QBFT run with a committed genesis | MD-01/02/03/10 (finality, decentralisation, trilemma, availability) | Scale thread |
| One measured log receipt | LIM-R7-08 (the 18× end of the storage-vs-log ratio) | Cost thread |
| Two-chain replay test for D52; 20 negative access-control tests | SLD-06, SLD-16 | Security campaign G-C1 |
| Radio reselection counter and TTL measurement | SLD-05, SLD-07 | Latency thread |
| E-F1-1 IDTX gas measurement | RV-IDTX executor rows | IDTX work chats |
| Commit the Sepolia witness as a register row, or drop it | RV-IMPL Sepolia rows | Scale thread |
| Primary sources for eight unfetched citations (incl. HSM verify times) | R7 LIM-R7-01..08 | Accuracy Ledger / Latency |
| ~~Blind re-derivation of the composition lemma~~ | SLD-10 | **done 2026-10-24** (§6b) |
| ~~R6/R8 v0-3 cross-reference sweep; R7 v0-3 (lead figure 320)~~ | PN-34..39 | **done 2026-10-24** (§6b); λ and δ for ε_K still to be declared as PAR by R8 |
| Ruling on SOL-16 (Q-R9-01) and on FIG-R13's attack classes | — | Author — **deferred 2026-10-24**; until ruled, SOL-16 is cited only together with SOL-05, and FIG-R13 carries its "classes proposed, not confirmed" flag |

## 6a. Author decisions

| Date | Decision |
|---|---|
| 2026-10-24 | SOL-16 as a standalone contribution: **deferred** |
| 2026-10-24 | FIG-R13 attack classes: **deferred** (designer's proposal stands, flagged) |
| 2026-10-24 | PR #14: **merged** (`4c3c248`) |

## 6b. Follow-ups done on 2026-10-24 (branch `roots/G-R1-phase2-v0-3`)

| Item | Result |
|---|---|
| v0-3 consistency sweep of R6, R7, R8 (PN-34..39) | Stale cross-references fixed; R7 lead verification figure now **320** neighbours at half budget (register #26 re-stated: 0.156 ms/neighbour, *P*\* ≈ 641); EIP-7623 floor condition derived (binds iff execution gas < 6z + 24n); coverage unchanged at 77 / 3 / 115 / 223 |
| SLD-10 blind re-derivation of the composition lemma (PF-36), written by a fresh agent that never saw R7 | **Passed with corrections** (`70_R7_theory_ece_bounds/blind/`): revocation term replaced by a key-theft-in-window term ε_K ≈ λ(σ+δ); multi-user loss stated inside the bound; hash term restricted to the document commitment; concrete security 6.16 bits (*N_v* = 4) and 4.32 bits (*N_v* = 1), not 4.16 (KD-R7-08). The 36.7-orders gap between ledger and cryptographic terms reproduced exactly. SLD-10 may now enter a chapter |
| CI note | The "Nine-standard gas benchmark" determinism failure on PR #14 predates it: it also fails on the base at `554a094` (PR #15). Not caused by documents |

## 7. How to pick this up in another chat

Paste the HANDOFF block at the end of the document you are continuing (R9 v0-2's for anything about what to lock; R8 v0-2's for deepening a category; R7 v0-2's for a bound; R6 v0-2's for a layer or a contract). Cite tags rather than restating. A new chat that finds a better value changes the input and cites the PF tag; it does not re-derive.
