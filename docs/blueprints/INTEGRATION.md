# Where the Blueprint Set Integrates

**Author:** Nikhil Prakash · **Date:** 2026-10-22

The set should go in three places: the thesis chapters, the repository's documentation index, and the defence. Each sheet below has one home where it carries the argument, and optional secondary homes where it is a pointer.

## 1. Thesis chapters

| Chapter | Sheets | What the sheet does there |
|---|---|---|
| Ch. 1 Introduction | BP-001 | One figure that shows the whole system and what it rests on. Introduces the waterline. |
| Ch. 3 Methodology | BP-401, BP-104, BP-106 | The threat model as a drawing; the basic-set admission gate and the catalogue that extends it; the nine substrates side by side before any number is shown. |
| Ch. 3 Methodology | BP-102 | Why gas is exact and what it measures. Supports the "exact where the EVM is exact" rule. |
| Ch. 4 Implementation | BP-101, BP-103, BP-105, BP-201 … BP-205, BP-601 | The primitives, the two engine sections, the SSI assemblies and the shipyard. This chapter is the natural home for most of the set. |
| Ch. 5 Results | BP-501, BP-502, BP-403 | The instrument panels and the attack matrix, each pointing at its register rows. |
| Ch. 6 Discussion | BP-402, BP-302, BP-304 | Security inheritance and its limits; the freshness trade-off; lifetime cost over the state machine. |
| Appendix | the full set, BP-000 first | The drawing index and every sheet at full size. |

Write one sentence of prose per figure that says what to look at. The figure carries the detail.

## 2. Repository documentation

- **`docs/INDEX.md`:** add a row: *"What does the system look like, end to end?" → `docs/blueprints/` (BP-000 is the index).*
- **`README.md`:** add BP-001 under Repository Structure as the system picture.
- **`COMPOSITION.md` Part III:** add the sheets as the visual form of each ledger row.
- **`SIDE_PAPERS.md`:** add the methods paper from Plan 3 L7.

These edits are not made in this change, so the existing documents stay untouched until you decide. Plan 2 P9 makes them.

## 3. Defence and talks

Open with BP-001 for the system and the waterline. Use BP-101 or the BP-100 atlas for "what it is made of". Use BP-402 for why a public ledger, BP-403 for "is it secure", and BP-501 with BP-502 for "what does it cost and is it fast enough". Five sheets cover the whole argument in five minutes.

## 4. One caution

The sheets carry a classification band and a programme name in military style. Both are the thesis's own. Keep them that way. Never add real service insignia, agency names or contract numbers, and keep the band text honest: `UNCLASSIFIED // THESIS RESEARCH — MEASURED`.
