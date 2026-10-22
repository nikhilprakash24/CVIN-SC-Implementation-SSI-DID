# Plan 2 — Phases and Prompts (run one at a time in a fresh chat)

**Author:** Nikhil Prakash · **Date:** 2026-10-22
**How to use:** open a new Claude Code session on this repository, branch `claude/system-blueprint-diagrams-fd8apg` (or a fresh branch off it), and paste **one** prompt. Wait for it to commit and push. Then paste the next. Each prompt is self-contained: it names the files to read, the output, and the done-check. They build on each other in order, but any phase after P0 can be re-run on its own.

The set already exists (Rev A, 23 sheets, `docs/blueprints/sheets/`). These phases take it from Rev A to a thesis-grade Rev C, then extend it outward.

---

## P0 — Orientation (read-only, 10 minutes)

```
Read docs/blueprints/PLAN_1_BLUEPRINT_PROGRAMME.md, docs/blueprints/bplib.py and
docs/blueprints/make_blueprints.py, then open five PNGs in docs/blueprints/sheets/png/
(BP-001, BP-101, BP-104, BP-302, BP-402). Do not change anything.
Report: (1) every place a number on a sheet is NOT traceable to a row in
docs/MEASUREMENT_CONDITIONS.md or a file under a results/ directory; (2) any text that
overlaps or overflows the frame; (3) which sheets break convention §4 of Plan 1.
Output a punch list as docs/blueprints/PUNCHLIST_REV_B.md and commit it.
```

## P1 — Number audit and Rev B (the credibility pass)

```
Work through docs/blueprints/PUNCHLIST_REV_B.md. For every measured number drawn by
docs/blueprints/sheets_*.py, open the result-of-record file it claims (gas_benchmark.json,
v2v_latency_stats.json, freshness_k.json, attack_results.csv, security_matrix.csv,
metrics/latest/tables/*.md) and confirm the value byte for byte. Where a sheet copies a
number from a prose document instead, replace it with the result-file value and the
register row. Fix every overlap. Add a revision row "B | NUMBER AUDIT + LAYOUT" with
today's date to every sheet you touch (Sheet.revisions). Regenerate:
  python3 docs/blueprints/make_blueprints.py
  NODE_PATH=/opt/node-tools/node_modules node docs/blueprints/render_png.js
Look at every PNG you changed. Commit and push.
```

## P2 — Make the sheets read their data (no hand-copied numbers)

```
Refactor docs/blueprints so that measured values are loaded from the result files at
generation time, not typed into sheets_*.py. Add docs/blueprints/data.py with one
loader per result file and a function value(row_id) that returns (value, source_path).
Sheets call it. If a file is missing or a value changes, generation must print a
diff and exit non-zero. Add a GitHub Actions step (extend .github/workflows/benchmark.yml,
do not create a new workflow) that runs make_blueprints.py --check and fails if the
committed SVGs differ from regenerated ones. Run it locally, commit, push.
```

## P3 — The primitives poster (BP-100, the anchor figure)

```
Create one new large sheet BP-100 "Primitive and function atlas" in
docs/blueprints/sheets_100.py: a single drawing that shows every primitive on BP-101 and
BP-102 at the bottom, the twelve basic-set functions F1–F12 (BP-104) in the middle, and
the 18+2 catalogue ops at the top, with every edge drawn: which function uses which
primitive, which op realises which function. Use balloons that cross-reference the
existing parts lists (BP-101/③ style). Size 2400x1500 (add a size parameter to Sheet).
This sheet must be legible printed at A1 and readable as a slide at 1920 wide.
Render, inspect, commit, push.
```

## P4 — Per-substrate detail sheets (nine sections, one per standard)

```
BP-103 (ERC-1056) and BP-105 (CVIN-Combined) are section drawings of single contracts.
Add BP-107 … BP-113 in the same style for ERC-721, ERC-725, ERC-725xy, ERC-735,
ERC-1155, ERC-4337 (account + minimal EntryPoint, draw the UserOperation path), LSP8.
Read each contract in 1_blockchain-identity/contracts/ first; draw storage, functions,
events, the authorization gate, and the parts list with file paths. Mark every n/a
catalogue op hatched (BASIC_ID_SET_EXTENSION.md §2.2). Update BP-000's index. Commit, push.
```

## P5 — The remaining sequences (12 use cases as SV-10c)

```
cv2x-testbed/scripts/test_use_cases.py runs 12 lifecycle use cases. BP-301 and BP-303
draw two of them. Add one SV-10c sequence sheet for each remaining use case (insurance
claim, recall, cross-border import, fleet, emissions, theft & recovery, AV data sharing,
dealership resale, end-of-life, maintenance) as BP-305 … BP-314. Derive each message
from the code path the use case actually executes, not from the design documents.
Mark the step where a forged/replayed credential fails. Commit, push.
```

## P6 — Downward: the decks the system rests on (L0–L2)

```
BP-001 draws decks L0–L2 as an assumed trust base. Draw three sheets that open them up,
each clearly labelled "CONTEXT — NOT IMPLEMENTED OR MEASURED IN THIS REPOSITORY":
BP-701 consensus and finality (what T1 actually means on an EVM chain: block production,
fork choice, finality gadget, reorg depth; Hardhat automine vs a public network),
BP-702 the network and the people (p2p gossip, validators/operators, client diversity,
governance; who can halt or censor), BP-703 compute and energy (key generation entropy,
HSM, the computational-boundedness assumption and what quantum would change).
Cite primary sources only (Ethereum specs, client docs, NIST). Commit, push.
```

## P7 — The security-guarantee sheet set (drive the inheritance point home)

```
Read docs/blueprints/SECURITY_GUARANTEE_INHERITANCE.md and BP-402. Produce BP-404
"One guarantee, many assets": a single sheet that shows a value transfer, a token
transfer, a governance vote and a vehicle identity operation going through identical
L1–L3 machinery, with the application-layer barriers each one adds on top. Insert the
value-secured figures for the chains named, each with a dated source in a footnote, as
param values (never as thesis results). Then BP-405 "Where the inheritance stops": the
seven non-inherited obligations with the test or result that discharges each. Commit, push.
```

## P8 — Export pack

```
Produce docs/blueprints/export/: (1) a single multi-page PDF of the whole set in index
order (render each SVG with Chromium via Playwright page.pdf, landscape); (2) a
LaTeX include file blueprints.tex with one \begin{figure} per sheet (caption = title,
label = fig:bp-xxx) pointing at the PNGs, ready for docs/thesis/; (3) an HTML viewer
index.html with the drawing index, thumbnails and zoom. Commit, push.
```

## P9 — Thesis integration

```
Follow docs/blueprints/INTEGRATION.md. Insert the figure references it lists into the
chapter drafts under docs/thesis/ (chapter3-methodology, chapter4-implementation,
chapter5-results, chapter6-discussion), one sentence of prose per figure that points at
it, and add the set to docs/INDEX.md as the canonical answer to "what does the system
look like". Do not change any number in a chapter. Commit, push.
```

## P10 — Independent review (adversarial)

```
Act as an external examiner who did not build this. Review every sheet in
docs/blueprints/sheets/png/ against the repository. For each sheet: is every claim
true of the code today; is anything over-claimed (especially BP-402/BP-404 on security
inheritance); is anything that matters missing. Write docs/blueprints/REVIEW_REV_C.md
with findings ranked by severity, fix the Critical and High ones, add revision row
"C | EXAMINER REVIEW" to the affected sheets, regenerate, commit, push.
```

---

### Prompting notes

- If a session runs long, say "commit what is done, push, and write the remaining items into the punch list" rather than letting it stop mid-file.
- Keep the rule from Plan 1 §0 in every prompt you write yourself: *no number on a sheet without a register row or a result file*.
- Phases P3, P4, P5 and P6 are independent once P2 is done and can run in parallel sessions on separate branches.
