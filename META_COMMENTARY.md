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
| D4 | Per-source artifacts — one HTML dossier per source, tracked in `docs/ARTIFACTS_MANIFEST.md` | 🔄 template + Wave-A item 1 done (local; external publish deferred by researcher) |
| D5 | `docs/thesis/SCAFFOLD.md` + `appendices/` index + Ch. 2 stub | ✅ done |
| D6 | `SIDE_PAPERS.md` register (8 candidates) | ✅ done |
| D7 | Content blocks (attribution statement, Ch1/Ch3 blocks, side-paper abstracts) | ⏳ pending |
| D8 | This handoff doc — kept live | 🔄 ongoing |
| D9 | `EXPANSION_PLAN.md` — produced LAST | ⏳ pending |

## ⏸ Gate: research audit pending review
`docs/RESEARCH_AUDIT.md` is a critical, research-grade self-assessment (validity
threats, honest claim boundaries, and a research program to close them). Per the
researcher's "have ALL possible information before we add more," **expansion is gated
on the researcher auditing §4 (threats) and deciding §7 (framing scope).** Several
validity threats genuinely narrow the headline claims (gas-determinism ≠ CIs; V2V
"600× margin" is a sub-component-vs-whole-budget scope mismatch; self-authored
compliance checker; implementation confounds; informal threat model; no scaling studies).

## What needs the researcher (not blocking this pass)
- **Push access** — both remotes 403 all session; work is committed locally + in
  the git bundles sent to you. Push tomorrow when access is restored.
- **Chapter 2 (Literature Review)** — needs your citation/reference set.
- **Sepolia run** — needs an RPC URL + a funded test-only key to turn the
  validation harness into a real public-testnet witness (then cut `v0.9.0`).

## Working mode (updated by researcher)
- **`COMPOSITION.md` tags along the whole time** — the master through-line, re-threaded
  each pass; read it for "what the thesis argues" end to end.
- **Alternate the flow**: interleave (a) code/execution/analysis, (b) per-source
  artifacts in batches, (c) thesis-writing passes — not one straight through. Other
  tasks between artifact batches strengthen the whole.
- **The priority gap is thesis writing** — the discipline/methodology of an ECE MASc
  thesis (Part II of `COMPOSITION.md`). Implementation is over-complete; more
  code/execution/analysis is welcome but the through-line goal is examiner-grade prose.
- **Have ALL possible information before adding more** (the researcher has much to add
  later) — hence the consolidation/provenance spine first.

## Decisions taken this pass
- Artifacts: **one per source/material**, produced **both** as local committed HTML
  and (on request) published externally; paced in batches, alternated with other work.
- `AUTONOMOUS_*` logs: **consolidated + corrected** into `DEVELOPMENT_HISTORY.md`.
- **Versioning/push:** version everything; full GitHub access is being granted (not a
  token). On access: `git push --all && git push --tags`; push milestone versions
  (`v0.7.0`, `v0.8.0`, later `v0.9.0`). See `COMPOSITION.md` Part V.

## Durability & pacing
Push is blocked, so every deliverable is committed and the git bundle refreshed;
bundles are sent to the researcher at checkpoints. Work is paced in waves with a
clean handoff at each boundary (per the researcher's token-usage / no-abrupt-stop
instruction). The current code and the ~295-test suite are untouched by this pass.

## Current repo markers
- Version `0.9.0-dev`; tags `v0.7.0`, `v0.8.0`.
- All five hypotheses H1–H5 supported by measured data.
- No committed secrets; artifacts are private-by-default and secret-free.
