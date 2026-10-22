# Lineage Relation, 2026-10-22: this branch and the trunk have diverged again

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written under:** `docs/STYLE_AND_RIGOUR_GUIDE.md` rule 1.3.6
(write down the relation between two branches before any merge). **This note merges nothing and changes no
result.**

## 1. The two branches
| Branch | Head | Holds | Last activity |
|---|---|---|---|
| `claude/clone-cvin-id-scs-011CUyxScetMdSQFkuQUNLTt` (this one) | `bc4618f` | The clone lineage (review-02 follow-ups H-R, H-A, H-K, H-L), merged with the cv2x lineage and layer 5 (ZKP, agent-wrapped identity) through PR #3 (after-action report 20) | 2026-10-21 |
| `claude/cv2x-testbed-setup-011CUz5ay5VfEAsZzv5cexDy` (the trunk named by every handback) | `87334d6` | WM-2 passes 19–26: C3, C1, C2, the Technical Data Package, the progress report, drafts of chapters 2 and 6, `docs/STATUS_2026-10-22.md` | today |

- Merge base `b7997f8` (2026-10-15).
- The trunk does **not** contain PR #3's merge; this branch does not contain the trunk's 46 newer commits.
- A trial merge reports about 124 conflicting paths.

## 2. The same work, done twice
WM-2 steps C1, C2 and C3 were executed on **both** lines, independently:

| WM-2 step | This branch | Trunk | Which to keep (recommendation) |
|---|---|---|---|
| C1: `_resolve_ethr` reads the chain | H-R: forward replay, fails closed, `did:mobi` via `lookupByVINHash`; external suite offline 335/336 plus a separate on-chain set 311/311 (#24 note) | Pass 21: reads the registry when given a provider, chain-time validity; 11 tests | **Trunk's as the base**, porting H-R's `did:mobi` resolution and its on-chain conformance set if the author wants them (the trunk does not resolve did:mobi from the registry) |
| C2: `attestEvent` scope | H-A: OWNER-role attesters owner-only (the registry had no delegate record), duplicate guard; pin 192,040 after merge | Pass 22: the MOBI registry **stores delegations** (`validDelegate`); owner or `veriKey` delegate, once per event; D54 fixed | **Trunk's.** It does what H-A could not (delegates). H-A's duplicate guard is covered by the trunk's "once per event" |
| C3: #32 and #37 on one host | H-K: 12 alternating replicates, register #54 (was #42) | Pass 19: two replicates in opposite order, register #52 | **Both are valid measurements**; keep #52 as the row of record (the trunk's numbering) and add H-K's 12-replicate result as supporting data, or retire one with a note |

Work only this branch has: H-L (#21 rejection-reason check, revert-origin check in the security harness, SUMO
replay cache), the P1/X1 harness operations and the basic digital-ID set framing, layer 5 (ZKP), and PR #3's
merged-tree re-runs. Work only the trunk has: passes 23–26 (briefs, decision sheet, progress report, chapter
drafts, TDP runbook phase 10), and the cross-model check brief.

## 3. Why this session did not merge
- `docs/STATUS_2026-10-22.md` §4 on the trunk asks that nothing be pushed there while the cross-model check of
  passes 16–22 runs. WM-2 A3 onward waits on that check.
- The overlapping implementations differ in design (owner-only vs delegates; two resolvers), so a merge is a
  choice, not a mechanical union.

## 4. What the author needs to decide
1. **Which branch is the trunk from here** (the trunk session's position: `cv2x-testbed-setup`).
2. **When to reconcile:** after the cross-model check reports (recommended), by merging this branch into the trunk
   and taking the trunk's side for C1/C2/C3 as in §2, then porting the items in the "only this branch" list.
3. Whether layer 5 (ZKP) and the PR #3 merge belong on the trunk now, or stay on this branch until the writing
   series (`docs/zkp/PLAN_2_PHASED_PROMPTS.md`) is scheduled.
