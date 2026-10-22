# X-Series — Exploratory Figures and Tables (Claude-initiated)

## The line

This set was **proposed, designed and drawn by Claude without direction from the author**. It is kept separate from author-directed work on purpose.

| | Author-directed | X-series (this folder) |
|---|---|---|
| Who chose what to show | the author | Claude |
| Where | `docs/blueprints/` (BP-xxx), future A-series | `docs/figures/x_series/` only |
| Names | `BP-…`, `A-…` | `X-…` figures, `XT-…` tables |
| Marking | blueprint frame | red stamp on every figure and table: *X-SERIES · EXPLORATORY · CLAUDE-INITIATED, NOT AUTHOR-DIRECTED* |
| Citable in a chapter | yes, per the register rule | **no, until promoted** |

**Promotion rule.** An X item enters the thesis only when the author decides it should. Promotion means it is copied into an author-directed series under a new number, with the stamp removed and a line in `docs/SCOPE_CHANGES.md`. Until then, nothing here is evidence. Each item only shows a way of looking at evidence the repository already holds.

**Data rule.** Every value is read from a result-of-record file when the figures are generated. Nothing is typed in by hand. `SOURCES.txt` lists the files the last run read. Regenerate with:

```bash
python3 docs/figures/x_series/make_x_series.py
```

## What is here and why

Each item complements a sheet in the blueprint set. The blueprint sheets show the structure; these show the trade-offs.

| Item | Question it answers | Complements |
|---|---|---|
| X-01 operation gas heatmap | Where do the standards differ: at create, or everywhere? | BP-501 (create only) |
| X-02 fleet amortisation | Does contract-per-identity ever catch up as the fleet grows? | BP-106 |
| X-03 rank reversal | Is the cheapest to create also the cheapest to own? | BP-501, BP-304 |
| X-04 security–cost frontier | What does each step of threat coverage cost over a life? | BP-403 (H5) |
| X-05 freshness trade-off | How many neighbours does each second of revocation lag buy? | BP-302, BP-502 (H3) |
| X-06 read path | Why does resolve latency differ by 10×? | BP-201 |
| X-07 state vs history | What does each identity leave in permanent chain state? | BP-102, BP-103 |
| XT-01 gas ratios vs ERC-1056 | Per-operation multiples in one table | X-01 |
| XT-02 lifetime footprint | Gas, transactions, log bytes, new slots, gas per tx | X-02, X-07 |
| XT-03 requirement → substrate | If a designer needs X, which standard, and at what cost | BP-104, BP-403 (**interpretation**) |

## Observations worth the author's attention

These are observations, not claims.

1. **The wrapper is cheaper than pure ERC-1056 over a life.** XT-02 shows 1,025,381 against 1,050,787, because it uses fewer transactions (20 against 26). Register #35 lists both, but the "ERC-1056 cheapest" phrasing should name the mode.
2. **CVIN-Combined is the cheapest create on #25 but the fifth-cheapest C1 in the harness** (266,995). The harness C1 anchors a manufacturer-signed VIN claim; #25's create does not. X-03 uses one harness definition throughout so the two are never mixed.
3. **X-04's score weights all six Lens 2 threats equally.** That is Claude's choice. A different weighting moves the frontier. The figure says so on its face.
4. **X-05 is host-bound** to the #32 run. On the #37 host no finite k reaches P*(0.5) = 100.
