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

Determinism (review 02, H-1/H-3): every "fresh" key is derived from the dataset
seed (`scenarios/common.js`; the counter restarts on each chain reset; addresses
with a 0x00 byte are skipped), and credential ops (V1/V3/V5/V6) get a fresh issuer
per iteration. Two runs of the same commit therefore give byte-identical gas
tables, and a crud cell does not depend on `METRICS_N`. Statistics unit tests:
`npx hardhat test test/benchmarks/stats.test.js`.
