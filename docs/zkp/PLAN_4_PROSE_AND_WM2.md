# Plan 4: Chapter Prose for Layer 5, Chapter 2, and WM-2 Resumed

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-22, before execution. **Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`.
**Brief (the author):** after PR #4, do all three: the layer-5 chapter prose, chapter 2, and the WM-2 steps.

## Track P — layer-5 chapter prose (the ▫️ sections of `docs/thesis/SCAFFOLD.md`)
New sections, appended to the existing chapter files without rewriting their drafted text:
3.9 pre-registration Z-E1..Z-E7 with amendments A1, A2, and conditions M0/M1/Sim/E; 4.8 the ZK-VIN tier and the
Steward; 5.10 RQ5 results (H6); 6.8 on-chain reality, SSI as a spectrum, the agent wrapper; 7.x additions to 7.2,
7.3, 7.5, 7.6 and a closing paragraph on the closed loop. **Sources:** Reports A–C, register #55–#61 only. Every
number must be in a V row (or labelled E). Plan 2's W-4 later refines this text; it is a first draft, not the series.

## Track L — chapter 2 (literature review)
Drafted only from registered sources: `SOURCES.md` and `docs/zkp/SOURCES_ZKP.md` (205 verified). A claim that needs a
source not in either register is either verified now (primary URL opened, added to the register with the date) or
left as a marked gap `[SOURCE NEEDED: …]`. No citation is written from memory. The researcher's own reference set
is still wanted; the chapter states which parts await it.

## Track W — WM-2 resumed at C3
The clone lineage merged in PR #3 carries work that matches three WM-2 steps: C3 (same-host freshness, register
#54), C1 (on-chain `did:ethr` resolution, H-R) and C2 (attestEvent scope, H-A). Each is checked against its gate in
`docs/PLAN_WM-2.md` §3 and marked done, done-with-a-gap, or open, with evidence. Then the next open step in §4's order
is executed in the same way as earlier passes (tests failing on old code, re-runs on a clean tree).

## Order and safety
P and L run in parallel (separate chapter files; no register edits, no git); W runs alongside in the main tree.
Every CI document check before each commit. One after-action report (22) and a handback addendum at the close.
