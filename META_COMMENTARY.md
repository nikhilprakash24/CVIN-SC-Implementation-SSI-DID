# Meta-Commentary & Handoff

**Purpose.** A living handoff document. It always reflects the true current state
so that any stopping point is a clean handoff, not an abrupt one. Updated at every
deliverable boundary.

**Last updated:** during the Consolidation & Provenance Pass (see plan in
`/root/.claude/plans/wild-jumping-gosling.md`, mirrored below).

---

## Why this pass exists
The researcher confirmed that the sub-hypothesis, the thrusts/hypotheses (H1–H5),
and the core design decisions (e.g. ERC-1056 as the base substrate) are **theirs
from the outset**. Confirming a core sub-hypothesis only recently is the signal to
**freeze and correctly source the intellectual record before expanding**. This pass
establishes the "provenance spine": corrected attribution, a full source register,
a project genealogy, per-source artifacts, a thesis scaffold, a side-papers
register, some written content blocks — and, last, an expansion plan.

## Deliverable status
| ID | Deliverable | Status |
|---|---|---|
| D1 | Attribution correction → `docs/DEVELOPMENT_HISTORY.md`; 4 `AUTONOMOUS_*` logs removed | ✅ done |
| D2 | `SOURCES.md` master source register | ✅ done |
| D3 | `PROVENANCE.md` project genealogy | ✅ done |
| D4 | Published artifacts — one per source/material (waves A–D) + `docs/ARTIFACTS_MANIFEST.md` | 🔄 starting (hybrid) |
| D5 | `docs/thesis/SCAFFOLD.md` + `appendices/` index + Ch. 2 stub | ✅ done |
| D6 | `SIDE_PAPERS.md` register (8 candidates) | ✅ done |
| D7 | Content blocks (attribution statement, Ch1/Ch3 blocks, side-paper abstracts) | ⏳ pending |
| D8 | This handoff doc — kept live | 🔄 ongoing |
| D9 | `EXPANSION_PLAN.md` — produced LAST | ⏳ pending |

## What needs the researcher (not blocking this pass)
- **Push access** — both remotes 403 all session; work is committed locally + in
  the git bundles sent to you. Push tomorrow when access is restored.
- **Chapter 2 (Literature Review)** — needs your citation/reference set.
- **Sepolia run** — needs an RPC URL + a funded test-only key to turn the
  validation harness into a real public-testnet witness (then cut `v0.9.0`).

## Decisions taken this pass
- Artifacts: **one per source/material** (max granularity), produced in paced waves.
- `AUTONOMOUS_*` logs: **consolidated + corrected** into `DEVELOPMENT_HISTORY.md`.

## Durability & pacing
Push is blocked, so every deliverable is committed and the git bundle refreshed;
bundles are sent to the researcher at checkpoints. Work is paced in waves with a
clean handoff at each boundary (per the researcher's token-usage / no-abrupt-stop
instruction). The current code and the ~295-test suite are untouched by this pass.

## Current repo markers
- Version `0.9.0-dev`; tags `v0.7.0`, `v0.8.0`.
- All five hypotheses H1–H5 supported by measured data.
- No committed secrets; artifacts are private-by-default and secret-free.
