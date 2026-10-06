# Review 02 follow-up F-B: external W3C DID test suite re-run

**Date:** 2026-10-04. **Scope:** re-measure register row #24 against the
resolver after review 02 S-10 (`did_resolver.py` @ `bd18057`; tree `d2e6a58`).
Nothing in the resolver or in the suite was changed. Full write-up:
`docs/conformance/W3C_DID_TEST_SUITE.md` section 8.

## What was run

Same procedure as the 2026-09-24 run of record:

```bash
git clone https://github.com/w3c/did-test-suite.git /tmp/did-test-suite
git -C /tmp/did-test-suite checkout 939b31d07d5b1699340ac0702ec0fa46ffcdef0a
cd /tmp/did-test-suite && npm install                    # lerna bootstrap
python3 docs/conformance/generate_implementations.py docs/conformance/implementations
cp docs/conformance/implementations/cvin-*.json \
   /tmp/did-test-suite/packages/did-core-test-server/suites/implementations/
cp docs/conformance/suite-run/*.js /tmp/did-test-suite/packages/did-core-test-server/
cd /tmp/did-test-suite/packages/did-core-test-server
node run-cvin-cli.js cvin && node run-cvin-cli.js control
node cli-to-report.js && node report/generate-report.js
```

jest 26.6.3 and jest-did-matcher 0.0.1 (from the lockfile, as before).
Node v22.22.0 / npm 10.9.4 (the original run used v22.22.2 / 10.9.7; patch
level only). Control (WG example implementation): 347/347, as before. The
441-test inventory is identical to the old run, test by test.

## Result

| | 2026-09-24 | 2026-10-04 |
|---|---|---|
| **Total** | 328/441 (74.4 %) | **336/441 (76.2 %)** |
| Identifier / core properties / production / consumption | 3/3, 88/88, 48/48, 3/3 | unchanged |
| **DID Resolution** | 186/299 (113 failed) | **194/299 (105 failed)** |
| ethr | 77/119 | **79/119** |
| mobi | 52/90 | **58/90** |
| nft | 57/90 | **57/90** |

Eight tests went failed → passed, none passed → failed.

Root causes (`did_resolver.py` lines at `bd18057`):

| | 09-24 | 10-04 | |
|---|---|---|---|
| R1 `error`/`errorMessage: null` always present (l. 137-138, `asdict` l. 164) | 24 | 22 | open |
| R2 `contentType` on `resolve()` (l. 135) | 21 | 21 | open |
| R3 8-key `didDocumentMetadata` with `null`s, non-empty on error (l. 142-151, 166; 279/305/314) | 52 | 51 | open |
| R4 `created` not XML Datetime (`isoformat()`, l. 393/455/499/550) | 10 | 10 | open |
| R5 malformed DID not `invalidDid` | 6 | 0 | **cleared** by S-10 |
| R5′ `did:nft:0x1:0xabc` is a valid generic DID, so the suite's `not.toBeValidDid()` fails although the resolver now returns `invalidDid` (vector at `generate_implementations.py:76`) | (in R5) | 1 | test-vector issue, not a resolver defect |

**Section 7 prediction:** R5 cleared (5 of 6; the sixth is R5′); R1-R4
remain (R1 −2 and R3 −1 as side effects of `did:mobi:` now being a real
error); **no new failures**, because R1 had already made the suite treat
every execution as unsuccessful, so the error-guarded tests were already
firing; 142/142 unchanged (CAIP-10 decimal chain id is not tested by the
suite).

## Proposed register text for #24 (`docs/MEASUREMENT_CONDITIONS.md`)

Claim column:

> **External** W3C DID test suite: **336/441 (76.2%)** — identifier 3/3, core
> properties 88/88, production 48/48, consumption 3/3, **resolution 194/299**;
> per resolver ethr 79/119, mobi 58/90, nft 57/90

Source column (unchanged): `docs/conformance/W3C_DID_TEST_SUITE.md` (§8)

Conditions / provenance column:

> w3c/did-test-suite @ `939b31d`, implementations generated from
> `DIDResolver.resolve()` at `bd18057`; jest 26.6.3, Node 22.22.0; raw jest
> reports `docs/conformance/reports/jest-*/*-2026-10-04.*`

Status column:

> **V**, re-run 2026-10-04 after review 02 S-10 (same suite commit, same
> generator and runner; control 347/347). 105 failures, all resolution
> metadata: R1-R4 (104) are open and fixable in `DIDResolutionMetadata` /
> `DIDDocumentMetadata`; R5 (`invalidDid`) is cleared, and its one residual
> failure is a test-vector choice (`did:nft:0x1:0xabc` is a valid generic DID),
> not a resolver defect. The §7 prediction held (R5 cleared, no new
> failures). Old value 328/441, resolution 186/299 (ethr 77, mobi 52, nft 57;
> run 2026-09-24) is **S**. Internal checker still misses R1-R4.

## Commits (local, not pushed)

1. Regenerated inputs and raw jest reports (`*-2026-10-04.*`).
2. Suite HTML report and sanitized result set for the re-run.
3. `W3C_DID_TEST_SUITE.md` section 8 (+ correction to section 7).
4. This file.

The register itself was not edited (out of scope for this stream).
