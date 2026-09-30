# benchmarks/ — CRUD-and-beyond measurement harness

Implements `docs/CVIN-DATA-COLLECTION-FRAMEWORK.md`. One operation catalogue
(`lib/operations.js`), one adapter per substrate (`adapters/`), six scenarios
(`scenarios/`), one collector (`lib/MetricsCollector.js`), tables in md/csv/tex.

```bash
npm run metrics                       # everything → results/metrics/latest/
METRICS_SCENARIOS=crud,lifecycle METRICS_ADAPTERS=erc1056,erc721 npm run metrics
METRICS_N=10 METRICS_SCALE_N=0,100 npm run metrics     # quick run
npm run metrics:report                # rebuild tables from results/metrics/latest
npm run test:conformance              # adapter gate (every core op must pass)
```

Output: `results/metrics/latest/{meta.json, raw.jsonl, <scenario>.json, tables/*.{md,csv,tex}, REPORT.md}`.
Only `latest/` is committed; `runs/` is local history.

Adding a substrate: write `adapters/<id>.adapter.js` extending `IdentityAdapter`,
register it in `adapters/index.js`, make `npm run test:conformance` pass, run.
Declare missing primitives in `this.unsupported[opId] = reason` — they print as
`n/a` and are themselves a result.
