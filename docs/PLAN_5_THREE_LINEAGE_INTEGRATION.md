# Plan 5: One Trunk — Integrating the cv2x-testbed Workspace as the Primary Lineage

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-22, before execution. **Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md` (rule 1.3.6 first).
**Brief (the author):** merge PR #5, then make a deeper, phased plan and continue; the `cv2x-testbed-setup` workspace
(the one run from many windows) is the lineage to integrate with most.

## 0. The situation (read before acting)

| Lineage | Branch | Since the common base `b7997f8` (report 18) |
|---|---|---|
| **Primary (W)** | `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy` | 49 commits, still active (last 22:05 UTC today): WM-2 C1 (resolver reads ERC-1056 when given a provider), **C2 redesign** (MOBI registry stores delegations; attester = owner or `veriKey` delegate, once; D54 **fixed**), **C3** (#32/#37 on one host, register **#52**), the Technical Data Package (TDP-001…010, ICD gate `check_icd.py`, requirement-to-test trace), Phase 2 session 3 briefs (I-24, I-05), chapter 2 §2.4a/§2.6 and chapter 6 §6.8 (IDTx) drafts, contribution record, progress report, decision sheet, `tools/prepush_check.sh`, reports **19–27** |
| **This trunk (T)** | `claude/zkp-ai-identity-research-n5uho9` → default branch | 82 commits: layer 5 (ZKP + Steward), the clone lineage (H-A, H-K, H-L, H-R, basic-set P1/X1), register #52–#61, Plan 3/4 prose, chapter 2 full draft, WM-2 A3, reports 19–22 |

Both carry the same WM-2 steps done twice in different ways (C1 ≈ H-R, C2 ≠ H-A, C3 ≈ H-K/#54), the same report
numbers (19–22), the same register number (#52), and the same section numbers (ch. 2, ch. 6 §6.8).

## 1. Decisions (defaults; the author can overturn any)

| # | Decision | Default |
|---|---|---|
| I-a | Which side wins where both did the same step | **W wins** (primary): its C2 design (owner or delegate) replaces H-A's (OWNER-role owner check); its C1 resolver API is kept, H-R's on-chain tests and did:mobi resolution are ported onto it; its #52 (C3) stays, T's #54 becomes corroborating evidence |
| I-b | Numbering | W keeps its numbers. T's reports 19–22 → **28–31**; T's register #52–#61 → **#53–#62**; T's §6.8 → §6.9; chapter 2: W's draft sections merged into T's full draft by topic, both kept |
| I-c | Direction | merge W into T on T's branch (W's history untouched), PR into the default branch; then a PR from T's branch into W's branch so the workspace receives the integrated trunk |
| I-d | W's live session | do not push to W's branch; the PR into W is merged only when W's head has not moved since the merge was prepared (else re-merge) |
| I-e | Results | everything a code change moves is re-run on the integrated tree from a clean tree; old values kept as history |

## 2. Phases (each ends with CI green and a commit; one after-action report, 32, opened at phase 1)

**Phase 1 — Relation record (rule 1.3.6).** Write `docs/LINEAGE_RELATION_2026-10-22.md`: the three-way inventory
(file overlap: 53 files changed on both sides), the duplicate-work map (C1, C2, C3; reports; rows; sections), the
renumbering table, and what each side's tests assert that the other's code may break. *Gate:* every overlapping file
has a planned resolution.

**Phase 2 — Textual merge.** Merge W into T. Resolve by the map: generated files take either side and are regenerated
later; register rows and reports renumbered with notes; DEFECT_LOG merged (D54 "fixed" per W, H-A recorded as the
superseded design); PLAN_WM-2 merged (W's C1/C2/C3 entries, T's A3 and pass-22 notes); handbacks merged by section.
*Gate:* the tree builds; no conflict markers; a list of every renumbered reference.

**Phase 3 — Code reconciliation.** Contracts: W's C2 design in all MOBI copies (1_blockchain-identity and the
testbed, byte-identical as CI demands), H-A's tests rewritten to W's rule where they encode the old rule (never
deleted; each change explained). Resolver: W's API plus H-R's on-chain did:ethr/did:mobi paths and tests; the D21
three-argument `DIDRevoked` decoding. *Gate:* Hardhat, Python layers, resolver, sandbox, layer-5 suites all pass,
0 skipped; every guard still shown to fire.

**Phase 4 — Re-runs on the integrated tree (clean tree, one at a time, no concurrent load).** Nine-standard gas
(#25) and its 30-run determinism; MOBI sweep; attestEvent pin (#28); metrics harness (#29–#31, #34–#36, #49–#51,
#53→#54) and HTTP-RPC (#39); M4 parity (#33); security matrix and scenarios (A3 producers); W3C (#4) and the external
suite (#24, offline and on-chain); layer-5 gas (#57→#58) only if its contracts' inputs moved. *Gate:* each row
restated with moved cells listed.

**Phase 5 — Generated documents and W's gates.** Regenerate the register views, cards, gas charter, dashboard,
presentation, Phase 2, TDP generators (TDP-002/005/006), ICD gate, requirement-to-test trace, contribution record;
run `tools/prepush_check.sh`. *Gate:* every CI `--check` and W's prepush check clean.

**Phase 6 — Chapters.** Chapter 2: merge W's §2.4a (revocation freshness) and §2.6 (IDTx) into the full draft
without losing sources; chapter 6: W's §6.8 IDTx stays, layer-5 becomes §6.9; chapters 1, 3, 5, 7 cross-references
updated. *Gate:* docs-number and citation checks clean.

**Phase 7 — PRs.** PR T → default branch; merge when green. PR T → W's branch; merge per I-d. *Gate:* both green.

**Phase 8 — Resume WM-2 on the one trunk:** A3b (the 15 families flagged "code changed since"), then A6's remaining
one-line switch, A5, A7, B3, D1. Each step as before: plan, tests failing on old code, clean re-runs, report.

## 3. Risks
- W's session pushes during phases 2–7 → re-merge W's new head before each PR (I-d).
- The C2 swap moves MOBI gas everywhere → phase 4 is not optional.
- Report-number collisions recur → reports take the next free number at opening, checked against both branches.
