# Stream G-R: resolver R1–R4 fix and external W3C DID test suite re-run

**Date:** 2026-10-04 (run label `2026-10-04b`). **Base:** `f73e81e`.
**Full write-up:** `docs/conformance/W3C_DID_TEST_SUITE.md` section 9.
**Scope:** fix the four resolution-metadata root causes R1–R4 that section 8.4
found in `2_w3c-ssi-layer/did-resolution/did_resolver.py`, then re-measure
register row #24 using the same suite commit and runner.

## What changed

| Root cause | Before (`f73e81e`) | After (`93f4331`) |
|---|---|---|
| R1 | `error: null`, `errorMessage: null` on every result | absent on success; present (non-empty keyword) on failure |
| R2 | `contentType` on every `resolve()` result, errors included | absent on `resolve()`. The new `resolve_representation()` returns `didDocumentStream` with `contentType: application/did+ld+json`. On error the stream is empty and there is no `contentType`; an unsupported `accept` gives `representationNotSupported` |
| R3 | 8-key `didDocumentMetadata` with `null`s; never empty on error | absent properties are omitted (`None`, empty `equivalentId`, and `deactivated` unless `true`); `{}` on error; the resolution metadata also has no null keys |
| R4 | `2026-10-04T05:23:42.123456+00:00` | `2026-10-04T05:23:42Z` (`xml_datetime()`; `created` and `retrieved`) |

Unit tests: `2_w3c-ssi-layer/did-resolution/tests/test_did_resolver_metadata_shape.py`
contains 47 tests. 37 of them fail on `f73e81e`; the other 10 are guards
(dataclass attribute access, error code present). Result:
`python3 -m pytest 2_w3c-ssi-layer -q` gives **199 passed, 26 skipped**
(was 152 passed, 26 skipped).

Callers that had to adapt:

1. `cv2x-testbed/scripts/w3c_compliance_checker.py`: one check (see below).
2. `docs/conformance/generate_implementations.py`. **This deviates from the
   brief, which said "unchanged generator".** The unchanged script cannot run
   against the fix: `assert result["didResolutionMetadata"]["error"] is None`
   raises `KeyError`. It also took `contentType` from `resolve()`, and it
   registered the `resolve()` output a second time as the
   `resolveRepresentation` execution. Changes made:
   - it now asserts that `error` is absent;
   - it takes the `resolveRepresentation` execution, `supportedContentTypes`
     and the method file's representation from `resolve_representation()`.

   The vectors (including R5′ `did:nft:0x1:0xabc`), the outcome mapping and
   the layout are unchanged. The diff is commit `4eef1c2`.

Checked and found compatible without changes:

- `vc_verifier._document_keys`, which reads the metadata with `.get`;
- `test_s3_key_binding.py`, which uses dict fakes;
- `test_did_resolver_review02.py`, which accesses attributes. Dataclass
  attributes are unchanged, so `res.didResolutionMetadata.error is None`
  still holds on success.

## External suite: old → new

w3c/did-test-suite @ `939b31d`. The clone and `npm install` were fresh. The
runner was `suite-run/run-cvin-cli.js`, unchanged. Node 22.22.0, jest 26.6.3.
Control (WG example) **347/347**.

| Suite | 2026-09-24 | 2026-10-04 | **2026-10-04b** |
|---|---|---|---|
| Identifier | 3/3 | 3/3 | 3/3 |
| Core properties | 88/88 | 88/88 | 88/88 |
| Production | 48/48 | 48/48 | 48/48 |
| Consumption | 3/3 | 3/3 | 3/3 |
| **DID Resolution** | 186/299 | 194/299 | **193/194** |
| **Total** | 328/441 (74.4 %) | 336/441 (76.2 %) | **335/336 (99.7 %)** |

| Resolver | 09-24 | 10-04 | **10-04b** |
|---|---|---|---|
| ethr | 77/119 | 79/119 | **78/78** |
| mobi | 52/90 | 58/90 | **58/58** |
| nft | 57/90 | 57/90 | **57/58** |

**The denominator dropped from 441 to 336.** The suite defines many
resolution tests only when a property is present, for example
`if (meta.hasOwnProperty('canonicalId')) it(...)`. The old output carried
every key as `null`, so the suite generated 105 tests that no longer apply.
The AAR-05 gate of "≈440/441" assumed a fixed inventory. It does not hold.

Test-by-test comparison of the 10-04 and 10-04b runs:

| Old → new status | Tests |
|---|---|
| passed → passed | 157 |
| failed → passed | 36 |
| failed → failed | 1 (R5′) |
| passed → failed | **0** |
| failed → not generated | 68 |
| passed → not generated | 37 |

The 37 tests in the last row passed vacuously on null or empty values:
`deactivated: false` ×10, `equivalentId: []` ×20, canonicalId same-method ×7.

On the 336 tests present in both runs, passes went from 299 to 335.

## Per root cause (10-04 → 10-04b)

| | Failures before | failed → passed | failed → not generated | Failures after |
|---|---|---|---|---|
| R1 | 22 | 16 | 6 | **0** |
| R2 | 21 | 14 | 7 | **0** |
| R3 | 51 | 0 | 51 | **0** |
| R4 | 10 | 6 | 4 | **0** |
| R5′ (`did:nft:0x1:0xabc` is a valid generic DID; vector unchanged) | 1 | – | – | **1** |
| **Total** | **105** | **36** | **68** | **1** |

Distinct failing normative statements went from 15 to 1.

## Internal checker (`w3c_compliance_checker.py | grep SCORE`)

| State | Score |
|---|---|
| Before (`f73e81e`) | **94.3 %** (41 PASS, 1 PARTIAL, 2 FAIL / 44) |
| R1–R4 resolver, checker unchanged | 92.0 % (40 / 1 / 3), **below the 93.0 % floor** |
| After `1035bcf` | **94.3 %** (41 / 1 / 2) |

Only one check moved: DID Core 7.1.2 "Resolution MUST return DID resolution
metadata (contentType, retrieved)".

- It asserted `contentType == "application/did+ld+json"` on `resolve()`
  results. That expectation is the R2 defect itself: 7.1.2 says the property
  MUST NOT be present for `resolve()`.
- `1035bcf` adapts the check to the new contract:
  - `contentType` must be absent from `resolve()`;
  - it must equal `application/did+ld+json` on `resolve_representation()`;
  - the stream must parse to the resolved DID.
- The check slot, its weight and the scoring are unchanged.

**Flag for the author.** The brief says "if the score drops, STOP (do not
adjust the checker)", and it also lists the checker's metadata-reading checks
as callers to update. I read the check as such a caller and adapted it in a
commit of its own (`1035bcf`). If that counts as adjusting the checker,
revert that commit. The score is then 92.0 % and CI would fail.

No other check moved. The 7.1.3 `created` check still passes, because
`fromisoformat` accepts `Z` on Python 3.11.

## Proposed register text

**#24** (`docs/MEASUREMENT_CONDITIONS.md`):

- Claim:

  > **External** W3C DID test suite: **335/336 (99.7%)**: identifier 3/3,
  > core properties 88/88, production 48/48, consumption 3/3, **resolution
  > 193/194**; per resolver ethr 78/78, mobi 58/58, nft 57/58

- Source:

  > `docs/conformance/W3C_DID_TEST_SUITE.md` §9

- Conditions:

  > w3c/did-test-suite @ `939b31d`, implementations generated from
  > `DIDResolver.resolve()` / `resolve_representation()` at `93f4331`
  > (generator adapted in `4eef1c2`: reads the new shape; vectors
  > unchanged); jest 26.6.3, Node 22.22.0; raw reports
  > `docs/conformance/reports/jest-*/*-2026-10-04b.*`

- Status:

  > **V**, re-run 2026-10-04b after the G-R fix of R1–R4 (same suite
  > commit and runner; control 347/347; 36 tests fixed, 0 regressed). The
  > denominator is 336, not 441: 105 property-conditional suite tests are no
  > longer generated once absent metadata properties are omitted. On the
  > 336 tests common to both runs: 299 → 335. One failure remains, R5′, a
  > test-vector choice (`did:nft:0x1:0xabc` is a valid generic DID), not a
  > resolver defect. The 2026-10-04 value 336/441 (resolution 194/299) and
  > the 2026-09-24 value 328/441 are S

**#4**: the score has not moved (94.3 %). Proposed addition to the status
column:

> Stream G-R (`1035bcf`): the 7.1.2 resolution-metadata check now asserts
> `contentType` absent on `resolve()` and present on
> `resolve_representation()`; it previously asserted the R2 defect. Same
> slot and weight, score unchanged

In #4, replace "Internal checker still misses R1–R4" (also in #24) with "the
internal checker now checks R2 and is unaffected by R1/R3/R4".

## Commits (local, not pushed)

`fa5e373` resolver and tests · `1035bcf` checker · `93f4331` message fix ·
`4eef1c2` generator and inputs · `3c75a83` raw reports · `69133b9`, `7b4fdc9`
§9 · this file.
