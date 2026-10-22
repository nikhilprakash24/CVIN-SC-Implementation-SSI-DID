# After-Action Report 32 — One Trunk: the cv2x-testbed Workspace Merged as the Primary Lineage (Plan 5)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened and closed:** 2026-10-22. **Brief (the author):** merge PR #5, then make a deeper, phased plan and continue;
the `cv2x-testbed-setup` workspace "should be the one integrated with the most". **Plan:**
`docs/PLAN_5_THREE_LINEAGE_INTEGRATION.md` (defaults I-a…I-e), written and pushed before execution. **Relation record:**
`docs/LINEAGE_RELATION_2026-10-22.md` (rule 1.3.6), written before the merge commit.

## 1. Phases

| Phase | Outcome |
|---|---|
| 1 Relation | 49 commits on W, 82 on the trunk since `b7997f8`; 53 files changed on both sides, 43 conflicted; C1, C2, C3 done twice; reports 19–22, row #52 and §6.8 collide |
| 2 Textual merge | W's head `ec7e19b` merged (`319fdaa`). W keeps its numbers; the trunk's reports 19–22 → **28–31**, rows #52–#61 → **#53–#62**, renumbered only in lines the trunk added since the base (the base stopped at #51, so no earlier text could mean the new numbers; hex colours excluded). Register rows edited on both sides merged word by word; three (#4, #24, #25) by appending the trunk's notes to W's text. Handback sections 11–14 of the trunk → 18–21 |
| 3 Code | **C2:** W's owner-or-`veriKey`-delegate rule in both contract copies (it implies H-A's). Five H-A tests failed as predicted; three kept with W's revert string, two rewritten to W's rule and labelled (a `sigAuth` delegate gains nothing; organisational roles need the owner's delegation). **Resolver:** the trunk's H-R engine (did:mobi, change walk, D21 event) now also accepts W's `registries={chain: address}` (constructor or attribute) and a bare provider; an `rpc_url` without a registry is still refused (the trunk's half-configuration test) |
| 4 Re-runs | Contracts byte-identical to W's, so W's C2 re-runs stand; confirmed on the merged commit: nine-standard gas reproduces W's table cell for cell; W3C 94.3 %; security matrix and scenarios unchanged except MOBI create 299,165 in the Sybil-cost column; **M4 parity re-run** (W had not re-run it after C2): verdicts unchanged, testbed deploy 5,435,562. Not re-run, with reason: the harness (no MOBI contract, code unchanged by W), layer 5 |
| 5 Generated and gates | grand run ALL OK (L1 99, Hardhat 562, Python layers 376, demos); every document `--check`, W's pre-push check, ICD gate (0 not found) and TDP probes pass |
| 6 Chapters | W's chapter-2 sections merged into the full draft; W's IDTx section is §6.8, layer 5 is §6.9 |
| 7 PRs | see §3 |

## 2. Findings
- **A generator that assumed a non-empty status.** `docs/tdp/make_blueprints.py` read `by_status['U']`; once the
  trunk's #39 re-run left no U row, it crashed. Fixed with a zero default.
- **The ICD quoted a superseded run id.** TDP-002/003/005/008 named the harness run of 2026-10-09; the run of record
  on the merged tree is `2026-10-21T03-28-59Z_a9e2a28`. Updated; the ICD gate also rejects a superseded id quoted in
  passing, so the old id is described, not quoted.
- **A blanket renumbering is dangerous.** The first pass also rewrote the two Plan 5 documents, which were already
  in merged numbering; restored from HEAD before the merge commit.

## 3. Not done, and the author's decisions
- **The organisational-role question is now settled by W's design** (D54 fixed): manufacturers, dealers, service
  centres, insurers, DMV, police and inspection stations attest only as the owner's `veriKey` delegate. Overturn if
  registry-wide co-signing was intended.
- **WM-2 continues on the one trunk:** A3b (families flagged "code changed since"), A6's one-line switch, A5, A7,
  B3, D1.
