# External W3C DID Test Suite Result for `did_resolver.py`

Audit finding F5 noted that the project's "75 % DID Core" figure comes from a
self-scored script (`cv2x-testbed/scripts/w3c_compliance_checker.py`) whose
PASS/FAIL values are hard-coded. This document records the result of running
the **official W3C DID Working Group test suite** against the project's
resolver output, so that the claim can be checked against an external oracle.

Summary: the resolver's DID identifiers and DID documents pass every test the
suite applies to them (identifier syntax, core properties, JSON-LD production
and consumption: 142/142). Its **resolution result** (metadata structures) does
not: 113 of 299 DID Resolution assertions fail, all traceable to five defects
in `DIDResolutionMetadata` / `DIDDocumentMetadata` and in error handling. DID
URL dereferencing could not be tested because the project has no dereferencer.

**Update 2026-10-03.** The five defects were fixed in `did_resolver.py` and
the suite was re-run on the same commit and harness: 335/336 (resolution
193/194, the other suites unchanged at 142/142). Sections 1-5 are kept as the
record of the 2026-09-24 run; section 7 has the re-run.

**Update 2026-10-04.** The suite was run a third time with the `did:ethr`
entry replaced by an identifier minted by the project's `MOBIVIDRegistry`
contract on a Hardhat chain (D10 follow-up in `docs/DEFECT_LOG.md`):
335/336, the same result and the same single failure as section 7. Section 8.

**Merge note (2026-10-06).** Two lineages re-ran this suite independently in
October 2026. Sections 7–8 below are the sandbox lineage's record; sections 9–11
are the review-2 lineage's record (its sections 7–9, renumbered at the merge;
their internal cross-references to "section 7/8/9" mean 9/10/11). Both end at
335/336 on the same denominator with the same single failure.

**Update 2026-10-04 (review-2 lineage, now section 10).** Re-run on the same suite commit after the
review-02 S-10 resolver fix: **336/441** (was 328/441); DID Resolution
**194/299** (was 186/299), 105 failures. R5 is cleared in the resolver (one
residual failure is a test-vector issue, R5'); R1-R4 remain. No new failures.
Sections 3-5 describe the 2026-09-24 run and are kept as recorded.

## 1. Suite under test

| Item | Value |
|---|---|
| Repository | https://github.com/w3c/did-test-suite |
| Commit | `939b31d07d5b1699340ac0702ec0fa46ffcdef0a` (2026-08-18T09:45:01-04:00, `main`, depth-1 clone) |
| Runtime | Node v22.22.2, npm 10.9.7, jest 26.6.3, jest-did-matcher 0.0.1 (from the suite's lockfile) |
| Project resolver | `2_w3c-ssi-layer/did-resolution/did_resolver.py`, `DIDResolver.resolve()` (Python 3.11.15) |
| Run date | 2026-09-24 (UTC) |

The suite is a static-vector suite: an implementation is registered as a JSON
file containing recorded DIDs, DID documents, representations and
resolution/document metadata; jest then checks those values against the
normative statements of DID Core v1.0 (sections 3, 5, 6, 7). It does not call
the resolver at run time.

## 2. How the implementation files were generated and registered

### 2.1 Generation (no hand edits)

`docs/conformance/generate_implementations.py` imports `DIDResolver` from the
project, calls `resolve()` for the three DIDs and writes the suite's input
format directly from `DIDResolutionResult.to_dict()`:

```bash
cd /path/to/CVIN-SC-Implementation-SSI-DID
python3 docs/conformance/generate_implementations.py docs/conformance/implementations
```

| File | Content | Source of every value |
|---|---|---|
| `implementations/cvin-did-ethr.json` | DID method entry for `did:ethr:0x1:0x1234567890abcdef1234567890abcdef12345678` | `resolve()` output |
| `implementations/cvin-did-mobi.json` | DID method entry for `did:mobi:5YJ3E1EA0PF123456` | `resolve()` output |
| `implementations/cvin-did-nft.json` | DID method entry for `did:nft:0x1:0xabc:123` | `resolve()` output |
| `implementations/cvin-resolver-ethr.json` | resolver executions: `resolve`, `resolveRepresentation`, `did:ethr_0x1234` (malformed), `did:web:example.com` (unsupported method) | `resolve()` output |
| `implementations/cvin-resolver-mobi.json` | resolver executions: `resolve`, `resolveRepresentation`, `did:mobi:` (trailing colon, invalid per ABNF) | `resolve()` output |
| `implementations/cvin-resolver-nft.json` | resolver executions: `resolve`, `resolveRepresentation`, `did:nft:0x1:0xabc` (missing tokenId) | `resolve()` output |

Mapping rules as of the 2026-09-24 run (the generator was updated for the
re-run; section 7.2 lists what changed):

* `didDocumentDataModel.properties` = `didDocument` minus `@context`;
  `representationSpecificEntries` = `{"@context": ...}`;
  `representation` / `didDocumentStream` = `json.dumps(didDocument)` (the same
  serialisation the resolver CLI prints).
* `supportedContentTypes` = `["application/did+ld+json"]`, the only
  `contentType` the resolver ever reports. `application/did+json` was **not**
  registered, so the 6.2.x JSON production/consumption tests did not run.
* `didResolutionMetadata` and `didDocumentMetadata` are copied verbatim,
  including `"error": null`, `"errorMessage": null`, `"retrieved"`, the
  ISO-8601 timestamps with microseconds/`+00:00`, and the `null` metadata
  fields. These are what cause the failures in section 4.
* The project has no `resolveRepresentation()`; its `resolve()` output already
  carries a `contentType`, so the same output is registered under both
  function names (`resolve` with the data model, `resolveRepresentation` with
  the document serialised to a string). Without a `resolveRepresentation`
  execution the suite's first test ("MUST be able to return a DID document in
  at least one conformant representation") cannot pass.
* Not registered because the project has no such functionality: `didParameters`
  (no DID URL query handling), `conformingConsumers` (no consumer function),
  and a dereferencer file (no `dereference()` anywhere in the repository; the
  only mentions are in `MOBI_VID2_SSI_DESIGN.md` and the internal checker).

### 2.2 Registration in the suite

```bash
SUITE=<scratch>/did-test-suite/packages/did-core-test-server
cp docs/conformance/implementations/cvin-*.json $SUITE/suites/implementations/
# add require('../implementations/cvin-did-*.json') to
#   suites/did-identifier/default.js, did-core-properties/default.js,
#   did-production/default.js, did-consumption/default.js
# add require('../implementations/cvin-resolver-*.json') to
#   suites/did-resolution/default.js
```

The exact edit is `suite-run/default.js-registration.diff`. Nothing else in
the suite (test code, matchers) was modified.

### 2.3 Running

```bash
cd did-test-suite && npm install            # lerna bootstrap, ~2 min
cd packages/did-core-test-server
cp <repo>/docs/conformance/suite-run/*.js .
node run-cvin-cli.js cvin                    # authoritative run (section 3)
node run-cvin-cli.js control                 # WG example implementation, harness sanity check
node cli-to-report.js && node report/generate-report.js   # -> report/index.html
```

`run-cvin-cli.js` follows the path documented in the suite's README
(`npm test`, i.e. the jest CLI) but temporarily narrows each suite's
`default.js` to the CVIN files so the report is not diluted by the ~130 other
registered implementations; the originals are restored afterwards.

**Harness caveat (why two runners exist).** The suite's own report script
(`report/generate-test-data.js` -> `services/runSuite.js`) passes the
implementation config through jest `globals`, which JSON-serialises it into a
different VM realm. On Node 22 every `toBeInfraMap()` assertion
(`expected instanceof Object`) then fails for *any* implementation: the WG's
own `did-example-didwg` / `resolver-example-didwg` fail 4/58 and 23/135 that
way, all `toBeInfraMap`. Through the jest-CLI path the same example passes
347/347. The `globals`-path run of the CVIN files (`run-cvin.js`; results in
`reports/globals-path-run-cvin-detailed-results.json`: core-properties 80/88,
resolution 166/299) is therefore **not** used; every extra failure in it is a
`toBeInfraMap` artifact. All numbers below are from the jest-CLI run.

## 3. Results (2026-09-24 run)

Per suite (jest-CLI run, `reports/jest-cvin/cvin-cli-<suite>.json`):

| DID Core section / suite | Registered | Tests | Passed | Failed | Skipped / not run |
|---|---|---|---|---|---|
| 3.1 Identifier syntax (`did-identifier`) | 3 DIDs | 3 | 3 | 0 | 3.2 DID-parameter tests not run (no `didParameters`) |
| 5.x Core properties + 7.3 metadata structure (`did-core-properties`) | 3 DIDs, `application/did+ld+json` | 88 | 88 | 0 | none |
| 6.1 / 6.3.1 Production (`did-production`) | 3 DIDs x (DID v1.0, DID v1.1 context variant) | 48 | 48 | 0 | 6.2.1 JSON production not run (`did+json` not supported) |
| 6.3.2 Consumption (`did-consumption`)* | 3 DIDs | 3 | 3 | 0 | 6.1 consumer and 6.2.2 JSON consumption not run (no consumer, no `did+json`) |
| 7.1 DID Resolution (`did-resolution`) | 3 resolvers, 10 executions | 299 | 186 | 113 | none |
| 7.2 DID URL Dereferencing (`did-url-dereferencing`) | nothing (no dereferencer in project) | - | - | - | suite not run |
| **Total** | | **441** | **328** | **113** | |

\* `did-consumption` is not part of the suite's report configuration
(`suites/suite-config.js`) and does not appear in the HTML report; it is
included here from its jest output.

Per implementation, DID Resolution suite:

| Resolver file | Executions | Tests | Passed | Failed |
|---|---|---|---|---|
| `cvin-resolver-ethr.json` | 4 | 119 | 77 | 42 |
| `cvin-resolver-mobi.json` | 3 | 90 | 52 | 38 |
| `cvin-resolver-nft.json` | 3 | 90 | 57 | 33 |

Control (WG example implementation, same harness): identifier 6/6, core
properties 58/58, production 106/106, consumption 42/42, resolution 135/135
(`reports/jest-control/`).

Reading the resolution numbers: many of the 186 passes are conditional tests
whose guard did not fire (e.g. "if the resolution is successful, `didDocument`
MUST be a conformant DID document" is only evaluated when `didResolutionMetadata`
has no `error` key, and the resolver always emits one). The 113 failures are
the reliable signal.

## 4. Failing tests (DID Resolution suite)

17 distinct normative statements fail; 113 failures in total. Grouped by
root cause in the resolver:

**R1 - `didResolutionMetadata` always contains `"error": null` and
`"errorMessage": null`.** DID Core 7.1.2 makes `error` present *only* when
resolution failed; the suite (like any consumer) treats the key's presence as
failure, so successful resolutions are judged as errors.

| x | Test (DID Core 7.1 / 7.1.2) | Assertion |
|---|---|---|
| 4 | If the resolution is unsuccessful, this value [didDocument] MUST be empty. | `expect(didDocument).toBeFalsy()` - received the full DID document |
| 3 | If the resolution is unsuccessful, this value [didDocumentStream] MUST be an empty stream. | expected `""`, received the serialised document |
| 7 | The value of this property [error] MUST be a single keyword ASCII string. | received `null` |
| 10 | If the resolution is unsuccessful, this output [didDocumentMetadata] MUST be an empty metadata structure. | expected length 0, received 8 keys (also R3) |

**R2 - `contentType` is emitted for `resolve()`.** DID Core 7.1.2:
`contentType` MUST NOT be present when `resolve` (as opposed to
`resolveRepresentation`) was called. `DIDResolutionMetadata` defaults it to
`"application/did+ld+json"` unconditionally, including on error results.

| x | Test (DID Core 7.1.2) | Assertion |
|---|---|---|
| 7 | This property MUST NOT be present if the resolve function was called. | received `["contentType","retrieved","error","errorMessage"]` |
| 7 | The value of this property MUST be an ASCII string that is the Media Type of the conformant representations. | `SyntaxError: "undefined" is not valid JSON` (a `contentType` on `resolve` makes the suite try to parse a `didDocumentStream` that does not exist) |
| 7 | The caller of the resolveRepresentation function MUST use this value when determining how to parse ... the didDocumentStream. | `expect(didDocumentStream).not.toBeFalsy()` - received `undefined` |

**R3 - `didDocumentMetadata` is a fixed 8-key dataclass with `null`
placeholders, never empty.** DID Core 7.1.3 defines each property only "if
present"; a present property with value `null` violates its type rule, and on
error the structure MUST be empty.

| x | Test (DID Core 7.1.3) | Assertion |
|---|---|---|
| 10 | updated - MUST follow the same formatting rules as created. | received `null` |
| 10 | nextUpdate - MUST follow the same formatting rules as created. | received `null` |
| 10 | nextVersionId - MUST be an ASCII string. | received `null` |
| 8 | versionId - MUST be an ASCII string. | received `null` (`did:mobi`, `did:nft` and all error results; `did:ethr` sets `"1"`) |
| 10 | canonicalId - MUST be a string that conforms to 3.1 DID Syntax. | received `null` |
| 4 | canonicalId - MUST be produced by, and a form of, the same DID Method as the id. | `TypeError: Cannot read properties of null (reading 'split')` |

**R4 - `created` is not an XML Datetime.** The resolver uses
`datetime.now(timezone.utc).isoformat()` -> `2026-09-24T23:32:46.715115+00:00`;
DID Core requires `YYYY-MM-DDTHH:MM:SSZ` (UTC, no sub-second precision).

| x | Test (DID Core 7.1.3) | Assertion |
|---|---|---|
| 10 | created - MUST be a string formatted as an XML Datetime normalized to UTC 00:00:00 and without sub-second decimal precision. | received `"2026-09-24T23:32:46.715115+00:00"` (6 cases) / `null` (4 error cases) |

**R5 - Syntax errors are not reported as `invalidDid`, and one invalid DID
resolves.** `_parse_did` raises `ValueError`, which `resolve()` maps to
`internalError`; `did:mobi:` (empty method-specific-id, forbidden by the DID
ABNF) is accepted and resolved to a document with `id: "did:mobi:"`.

| x | Test (DID Core 7.1 / 7.1.2) | Assertion |
|---|---|---|
| 3 | invalidDid - The DID supplied ... does not conform to valid syntax. | expected `"invalidDid"`, received `"internalError"` (`did:ethr_0x1234`, `did:nft:0x1:0xabc`) / `null` (`did:mobi:`) |
| 2 | This input is REQUIRED and the value MUST be a conformant DID as defined in 3.1 DID Syntax. | `toBeValidDid()` failed for `"did:ethr_0x1234"`, `"did:mobi:"` (the resolver did not flag them as `invalidDid`) |
| 1 | If the resolution is not successful, this structure MUST contain an error property describing the error. | `did:mobi:` resolved "successfully" - `error` is `null` |

Full assertion messages, stack locations and the per-execution breakdown are
in `reports/jest-cvin/cvin-cli-did-resolution.json` (`assertionResults[].failureMessages`)
and the verbose transcript `reports/jest-cvin/cvin-cli-did-resolution.txt`.

## 5. Comparison with the internal checker (75 % DID Core)

`w3c_compliance_checker.py` scores 28 hard-coded DID Core items: 19 PASS,
4 PARTIAL, 5 FAIL -> (19 + 0.5 x 4) / 28 = 75.0 % (`internal/w3c_compliance_report.json`).
It never calls the resolver. Mapping its non-PASS items to the external result:

| Internal item | Internal status / note | External finding |
|---|---|---|
| 3.2 DID URL path / query component | PARTIAL, "not yet implemented" | Consistent: no `didParameters` could be registered and no DID URL handling exists; the 3.2 tests did not run. |
| 4.4 `assertionMethod` | PARTIAL, "to be added" | **Stale.** `did:ethr` (and `did:key`) documents already emit `assertionMethod`; it passes 5.3.2 (88/88 core-property tests). |
| 4.4 `keyAgreement`, `capabilityInvocation`, `capabilityDelegation` | FAIL, "not implemented" | **No corresponding external failure.** These are OPTIONAL (MAY) properties; DID Core imposes no requirement to emit them and the suite passes 5.3.3-5.3.5 when they are absent. The internal checker penalises optional features, which depresses its score in a way the spec does not. |
| 5.1 Resolution metadata SHOULD be provided | FAIL, "metadata not yet implemented" | Metadata **is** emitted, but non-conformant: R1 + R2 above (45 failures under 7.1 / 7.1.2). Direction of the verdict agrees; the reason does not. |
| 5.2 Document metadata SHOULD include created/updated | FAIL, "timestamps not yet included" | `created` **is** emitted but in the wrong format (R4, 10 failures); `updated` and five other properties are emitted as `null` (R3, 52 failures). Direction agrees; reason does not. |
| 6 Fragment dereferencing MUST work for keys | **PASS**, "can dereference #keys-1" | **Not supported by the code.** No `dereference()` exists in `did_resolver.py` or elsewhere in the repository, so nothing could be registered for the 7.2 suite. This PASS is unsubstantiated. |
| 6 Service endpoint dereferencing SHOULD work | PARTIAL, "basic implementation" | Same: untestable, no implementation found. |

External failures the internal checker does not detect at all:

* **`error: null` / `errorMessage: null` always present** (R1) - the checker has no item for the presence semantics of `error`.
* **`contentType` on `resolve()`** (R2) - not covered; the checker's 5.1 item says metadata is absent.
* **`null`-valued metadata properties and non-empty metadata on error** (R3) - not covered.
* **`internalError` instead of `invalidDid`, and acceptance of `did:mobi:`** (R5) - the checker marks 3.1 "Method-specific identifier MUST be valid" as PASS, but the resolver performs no ABNF validation (`_parse_did` only splits on `:`).

Items neither test covers (noted for completeness): the verification material
property `publicKeyHex` (used for `did:mobi` with the placeholder value
`"0x..."`) is not one of the DID Core 5.2.1 material properties
(`publicKeyJwk`, `publicKeyMultibase`); the suite's 5.2.1 checks only examine
those two and `publicKeyBase58`, so `publicKeyHex` passes vacuously. Similarly,
the DID documents are constructed by the resolver without any registry lookup
(see the "would query ..." comments in `did_resolver.py`), so this result
certifies the shape of the produced documents, not any on-chain state.

### What the external result supports

* Identifier syntax, DID document core properties, JSON-LD production and
  consumption of the three methods: **142/142 external assertions pass**.
  On these sections the project is more conformant than the 75 % self-score
  suggests (the score's FAIL items in 4.4 are optional features).
* DID Resolution (7.1): **186/299, 113 failures**, all from the five defects
  R1-R5 in `DIDResolutionMetadata` / `DIDDocumentMetadata` / error handling.
  On this section the project is *less* conformant than the checker implies,
  and the checker's stated reasons are wrong.
* DID URL Dereferencing (7.2): **not testable**; the internal PASS has no
  implementation behind it.

A single-number "DID Core %" is not something the W3C suite produces, and the
internal 75 % should not be presented as if it were an external result.

## 6. Files in this directory

| Path | Description |
|---|---|
| `W3C_DID_TEST_SUITE.md` | this document |
| `generate_implementations.py` | generates the suite input files from `did_resolver.py` |
| `implementations/cvin-did-{ethr,mobi,nft}.json` | DID method entries (registered in did-identifier, did-core-properties, did-production, did-consumption) |
| `implementations/cvin-resolver-{ethr,mobi,nft}.json` | resolver entries (registered in did-resolution). Since `f646e88` / 2026-10-04 these are the post-S-10 inputs of the section 8 run; the 2026-09-24 inputs are at `ed62314` |
| `suite-run/run-cvin-cli.js` | jest-CLI runner used for the reported numbers (CVIN and control modes) |
| `suite-run/run-cvin.js` | runner through the suite's `services/runSuite.js` (`globals` path; affected by the `toBeInfraMap` realm artifact, kept for transparency) |
| `suite-run/cli-to-report.js` | converts jest `--json` output into the suite's report input format |
| `suite-run/default.js-registration.diff` | the registration edit to the suite's `default.js` files |
| `reports/jest-cvin/cvin-cli-<suite>.json` / `.txt` | raw jest `--json` results and verbose transcripts for the five suites (CVIN) |
| `reports/jest-control/control-cli-<suite>.json` | raw jest results for the WG example implementation on the same harness |
| `reports/did-implementation-report.html` | the suite's own HTML report (`report/generate-report.js`) built from the CVIN jest-CLI results (identifier, core-properties, production, resolution) |
| `reports/did-spec-test-run.latest.json` | sanitized result set that the HTML report was generated from |
| `reports/globals-path-run-cvin-detailed-results.json` | the discarded `globals`-path run, with failure messages |
| `reports/jest-cvin/cvin-cli-<suite>-2026-10-04.{json,txt}` | raw jest results of the section 8 re-run (CVIN) |
| `reports/jest-control/control-cli-<suite>-2026-10-04.json` | control run on the section 8 harness (347/347) |
| `reports/did-implementation-report-2026-10-04.html`, `reports/did-spec-test-run-2026-10-04.json` | suite HTML report and its sanitized input for the section 8 re-run |
| `internal/w3c_compliance_report.json` | output of `cv2x-testbed/scripts/w3c_compliance_checker.py` for the comparison in section 5 |
| `reports/rerun-2026-10-03/jest-cvin/cvin-cli-<suite>.json` / `.txt` | raw jest `--json` results and verbose transcripts of the re-run (section 7) |
| `reports/rerun-2026-10-03/did-implementation-report.html`, `did-spec-test-run.latest.json` | the suite's HTML report and its sanitized input, re-run |
| `reports/rerun-2026-10-03/internal/w3c_compliance_report.json` | output of the (now executable) internal checker after the fixes (section 7.4) |
| `implementations-registry-did/cvin-*.json` | the six implementation files with the registry-minted `did:ethr` (section 8; `generate_implementations.py --ethr-did ...`) |
| `reports/registry-did-2026-10-04/mint_did.js`, `mint_did.out.txt` | Hardhat script that deployed `MOBIVIDRegistry`, registered the vehicle and printed the DID, and its output |
| `reports/registry-did-2026-10-04/jest-cvin/cvin-cli-<suite>.json` / `.txt` | raw jest `--json` results and verbose transcripts of the registry-minted run (section 8.3) |
| `reports/registry-did-2026-10-04/did-implementation-report.html`, `did-spec-test-run.latest.json` | the suite's HTML report and its sanitized input, registry-minted run |
| `reports/registry-did-2026-10-04/baseline-default-fixtures/jest-cvin/` | raw jest results of the default-fixture run made on the same day, clone and commit (section 8.4 baseline) |

## 7. Re-run after fixes (2026-10-03)

### 7.1 What was changed in `did_resolver.py`

All five root causes of section 4 were addressed in
`2_w3c-ssi-layer/did-resolution/did_resolver.py`; nothing else in the
resolver's public API changed (`resolve(did)` still returns a
`DIDResolutionResult` with `.didDocument` / `.didResolutionMetadata` /
`.didDocumentMetadata` and `to_dict()`, the cache and `create_did()` are
unchanged).

| Root cause | Fix |
|---|---|
| R1 `error` / `errorMessage` always present | `DIDResolutionMetadata.to_dict()` emits only populated properties. Failures are raised internally as `DIDResolutionError(code, message)` and turned into a result with a single-keyword `error` (`invalidDid`, `methodNotSupported`, `representationNotSupported`, `internalError`), `didDocument: null` and empty `didDocumentMetadata`. |
| R2 `contentType` on `resolve()` | `DIDResolutionResult.to_dict()` drops `contentType` unless the result came from the new `resolve_representation(did, accept=None)` (alias `resolveRepresentation`), which serialises the document (`didDocumentStream`, `json.dumps` of the data model) and sets `contentType: application/did+ld+json`; any other `accept` is `representationNotSupported` with an empty stream. The in-process attribute `didResolutionMetadata.contentType` is kept on successful `resolve()` results (the internal checker reads it) but is never serialised for `resolve()`. |
| R3 null-placeholder document metadata | `DIDDocumentMetadata.to_dict()` omits `None`, empty `equivalentId` and `deactivated == False`, so an untouched instance serialises to `{}`; successful results carry `created` (and `versionId` for `did:ethr`) only. No `canonicalId` is emitted. |
| R4 timestamp format | `created` and `retrieved` are produced by `xml_datetime_now()` -> `YYYY-MM-DDTHH:MM:SSZ` (UTC, no sub-seconds). |
| R5 no syntax validation | `_parse_did` matches the DID Core 3.1 ABNF (`did:` + `[a-z0-9]+` method-name + `method-specific-id = *( *idchar ":" ) 1*idchar`, `idchar = ALPHA / DIGIT / "." / "-" / "_" / pct-encoded`) before dispatch: non-matching input (`did:ethr_0x1234`, `did:mobi:`, `not-a-did`, DID URLs with `#`/`?`/`/`) is `invalidDid`; a valid DID with an unimplemented method (`did:web:...`, `did:example:...`) is `methodNotSupported`. Method-specific rules (`did:nft` needs chainId:contract:tokenId, `did:mobi` a single VIN segment, `did:ethr`/`did:key` one or two segments) are also reported as `invalidDid`. |

### 7.2 Generator and run

`generate_implementations.py` now records the `resolveRepresentation`
executions and the method files' per-content-type block from
`resolve_representation()` (stream + `contentType`), and the `resolve`
executions from `resolve()`; the success check tests for the *absence* of
`error`. The three DIDs, the four error inputs and the ten executions are the
same as on 2026-09-24. Suite commit, Node/jest versions, registration and
runner are unchanged (sections 1, 2.2, 2.3); Python 3.11.15.

### 7.3 Results

Per suite (jest-CLI run, `reports/rerun-2026-10-03/jest-cvin/cvin-cli-<suite>.json`):

| DID Core section / suite | Tests | Passed | Failed | 2026-09-24 (passed/tests) |
|---|---|---|---|---|
| 3.1 Identifier syntax (`did-identifier`) | 3 | 3 | 0 | 3/3 |
| 5.x Core properties + 7.3 metadata structure (`did-core-properties`) | 88 | 88 | 0 | 88/88 |
| 6.1 / 6.3.1 Production (`did-production`) | 48 | 48 | 0 | 48/48 |
| 6.3.2 Consumption (`did-consumption`) | 3 | 3 | 0 | 3/3 |
| 7.1 DID Resolution (`did-resolution`) | 194 | 193 | 1 | 186/299 |
| 7.2 DID URL Dereferencing | - | - | - | not run (no dereferencer, unchanged) |
| **Total** | **336** | **335** | **1** | **328/441** |

Per implementation, DID Resolution suite:

| Resolver file | Executions | Tests | Passed | Failed | 2026-09-24 |
|---|---|---|---|---|---|
| `cvin-resolver-ethr.json` | 4 | 78 | 78 | 0 | 77/119 |
| `cvin-resolver-mobi.json` | 3 | 58 | 58 | 0 | 52/90 |
| `cvin-resolver-nft.json` | 3 | 58 | 57 | 1 | 57/90 |

The number of resolution tests fell from 299 to 194 because the suite
registers several `it()` blocks only when the corresponding key is present
in the recorded output (`error` -> "single keyword" test; `contentType` ->
two media-type tests; each `didDocumentMetadata` property -> its format
test). On 2026-09-24 every execution carried `error`, `contentType` and all
eight metadata keys, so every one of those tests was instantiated (and most
failed); now they are instantiated only where the key legitimately appears.
The 17 normative statements that failed in section 4 all pass wherever they
are now evaluated: the "if the resolution is successful ..." tests that were
previously skipped because `error` was always present (section 3, last
paragraph) are now actually exercised and pass.

### 7.4 Remaining failure

One test fails, in `cvin-resolver-nft.json`, execution `did:nft:0x1:0xabc`
(registered as `invalidDidErrorOutcome`):

| Test (DID Core 7.1.2) | Assertion |
|---|---|
| invalidDid - The DID supplied to the DID resolution function does not conform to valid syntax. | `expect(did).not.toBeValidDid()` - received `"did:nft:0x1:0xabc"` |

The resolver's output for this input is conformant (`error: "invalidDid"`,
`didDocument: null`, `didDocumentMetadata: {}`; the first two assertions of
the same test pass). The suite's third assertion requires the *input* to
violate the generic 3.1 ABNF, and `did:nft:0x1:0xabc` does not: it violates
only the `did:nft` method rule (missing tokenId). DID Core 7.1.2 defines
`invalidDid` as "does not conform to valid syntax" and the DID Resolution
specification applies it to method-specific syntax as well, so the resolver
keeps reporting `invalidDid` for this case. This is a mismatch between the
registered vector and the suite's narrower test, not a resolver defect; the
vector was kept so that the executions are identical to the 2026-09-24 run.
(Replacing it with an input that is invalid under the generic ABNF, for
example the trailing-colon form `did:nft:0x1:0xabc:`, would remove the
failure; the generic-ABNF path is already covered by `did:ethr_0x1234` and
`did:mobi:`, both of which pass.)

No other failures remain: R1-R5 produce zero failures.

### 7.5 Project checks after the fixes

| Check | Before | After |
|---|---|---|
| `cv2x-testbed/scripts/w3c_compliance_checker.py` (executable score) | 93.2 % (40 PASS / 2 FAIL / 2 PARTIAL of 44) | **94.3 %** (41 PASS / 2 FAIL / 1 PARTIAL of 44); DID Core 14/15 (96.7 %). The 7.1.2 "unsupported method -> `methodNotSupported`" item moved from PARTIAL to PASS. Remaining PARTIAL: `did:mobi` placeholder key material; remaining FAILs: the two documented VC deviations (canonicalization, cryptosuite). Report: `reports/rerun-2026-10-03/internal/w3c_compliance_report.json`. |
| `python -m pytest 2_w3c-ssi-layer -q` | 60 passed | 60 passed |
| `docs/conformance/generate_implementations.py` | - | regenerates the six `implementations/cvin-*.json` files from the fixed resolver (the registered inputs of section 7.3) |

The internal checker's 7.1.2 metadata item still reads
`didResolutionMetadata.contentType` on `resolve()` results; it passes because
the attribute is kept in-process (section 7.1, R2) even though it is no
longer serialised for `resolve()`.

## 8. Re-run on a registry-minted did:ethr (2026-10-04)

Sections 1-7 register `did:ethr:0x1:0x1234567890abcdef1234567890abcdef12345678`,
a static fixture in `generate_implementations.py`; no contract was involved
in producing it. Defect D10 (`docs/DEFECT_LOG.md`: `MOBIVIDRegistry.getVehicleDID`
emitted the address without `0x`, fixed in `65a143f`) left one follow-up:
run the suite on a `did:ethr` that the registry contract actually mints. This
section records that run.

### 8.1 The identifier

| Item | Value |
|---|---|
| DID | `did:ethr:0x7a69:0x2244c598f83916430028a1b3c438c640ca0e0375` |
| Produced by | `1_blockchain-identity/contracts/MOBI/MOBIVIDRegistry.sol:MOBIVIDRegistry.getVehicleDID(vehicle)` |
| Repository commit | `d941ad5` (`git rev-parse --short HEAD`; the contract is unchanged since `65a143f`) |
| Chain | Hardhat in-process network, `chainId` 31337 = `0x7a69` (`hardhat.config.js`) |
| Script | `reports/registry-did-2026-10-04/mint_did.js`, run with `npx hardhat run` from `1_blockchain-identity`; output in `mint_did.out.txt` |

The script deploys `MOBIVIDRegistry` (deployer `0xf39F...2266` is auto-authorised
as manufacturer by the constructor), draws a fresh vehicle address with
`ethers.Wallet.createRandom()` (`0x2244C598F83916430028A1B3C438C640ca0e0375`),
calls `registerVehicleBirth(vehicle, keccak256("1HGBH41JXMN109186:salt"),
"enc:vin", keccak256("cert"), deployer, "0x")` (tx `0xa721fc...bfb8`, block 2,
registry at `0x5FbD...0aa3`) and then `getVehicleDID(vehicle)`. The contract
returns the chain id as minimal lowercase hex and the address as 0x-prefixed,
zero-padded, lowercase 40-hex, which is the string above.

### 8.2 Generator and run

`generate_implementations.py` gained an optional `--ethr-did <did>` flag
(environment variable `CVIN_ETHR_DID`) that replaces the did:ethr identifier
in `METHODS` before generation; the did:ethr error cases (`did:ethr_0x1234`,
`did:web:example.com`) and the did:mobi / did:nft entries are unchanged.
Without the flag the output is the same as before: the default set was
regenerated into a scratch directory and compared with the committed
`implementations/cvin-*.json`; the only differences are the per-run
`created` / `retrieved` timestamps. The committed default files were not
touched.

```bash
python3 docs/conformance/generate_implementations.py \
    docs/conformance/implementations-registry-did \
    --ethr-did did:ethr:0x7a69:0x2244c598f83916430028a1b3c438c640ca0e0375
```

The resolver resolves the minted DID without error (`did:ethr` with an
explicit chain id is parsed as `<chainId>:<address>`); the recorded
`resolve` / `resolveRepresentation` outputs carry `id`, `controller`,
`verificationMethod[0].id` / `.controller` equal to the minted DID,
`blockchainAccountId: "eip155:0x7a69:0x2244...0375"`, `created` and
`versionId: "1"`.

Suite: a fresh clone of `w3c/did-test-suite` at the same commit
`939b31d07d5b1699340ac0702ec0fa46ffcdef0a` (still the head of `main`),
`npm install` (lerna bootstrap), Node v22.22.2, npm 10.9.7, jest 26.6.3,
jest-did-matcher 0.0.1, Python 3.11.15. The six files from
`implementations-registry-did/` were copied to `suites/implementations/`
under the same names, registered with `suite-run/default.js-registration.diff`
(applies cleanly, 5 files, 15 insertions) and run with
`node run-cvin-cli.js cvin` (section 2.3), then `cli-to-report.js` and
`report/generate-report.js` for the HTML report. Before that, on the same
clone, the default `implementations/cvin-*.json` were run the same way as a
baseline for this commit (`reports/registry-did-2026-10-04/baseline-default-fixtures/`).

### 8.3 Results

Per suite (jest-CLI run, `reports/registry-did-2026-10-04/jest-cvin/cvin-cli-<suite>.json`):

| DID Core section / suite | Tests | Passed | Failed | 2026-10-03, section 7.3 (passed/tests) |
|---|---|---|---|---|
| 3.1 Identifier syntax (`did-identifier`) | 3 | 3 | 0 | 3/3 |
| 5.x Core properties + 7.3 metadata structure (`did-core-properties`) | 88 | 88 | 0 | 88/88 |
| 6.1 / 6.3.1 Production (`did-production`) | 48 | 48 | 0 | 48/48 |
| 6.3.2 Consumption (`did-consumption`) | 3 | 3 | 0 | 3/3 |
| 7.1 DID Resolution (`did-resolution`) | 194 | 193 | 1 | 193/194 |
| 7.2 DID URL Dereferencing | - | - | - | not run (no dereferencer, unchanged) |
| **Total** | **336** | **335** | **1** | **335/336** |

Per implementation, DID Resolution suite:

| Resolver file | Executions | Tests | Passed | Failed | 2026-10-03 |
|---|---|---|---|---|---|
| `cvin-resolver-ethr.json` (minted DID) | 4 | 78 | 78 | 0 | 78/78 |
| `cvin-resolver-mobi.json` | 3 | 58 | 58 | 0 | 58/58 |
| `cvin-resolver-nft.json` | 3 | 58 | 57 | 1 | 57/58 |

Baseline on the same day, clone and commit with the default fixtures:
3/3, 88/88, 48/48, 3/3, 193/194 = **335/336**, identical to section 7.3.

### 8.4 Diff against section 7.3

* Totals, per-suite counts and per-resolver counts are identical:
  335/336 in both runs, 78/78 for the did:ethr resolver file in both.
* 87 assertions carry the DID in their title (1 identifier, 29
  core-properties, 16 production, 1 consumption, 40 resolution). In the
  2026-10-03 results every one of them names the static fixture; in this run
  every one of them names
  `did:ethr:0x7a69:0x2244c598f83916430028a1b3c438c640ca0e0375` and none
  names the fixture. All 87 pass.
* The one failure is the same assertion as in section 7.4:
  `cvin-resolver-nft.json`, execution `did:nft:0x1:0xabc`,
  "7.1.2 DID Resolution Metadata - invalidDid - The DID supplied to the DID
  resolution function does not conform to valid syntax",
  `expect(did).not.toBeValidDid()` on `"did:nft:0x1:0xabc"`. It does not
  involve did:ethr. The explanation in section 7.4 stands: the input is a
  valid generic DID that only violates the did:nft method rule, and the
  resolver's `invalidDid` outcome for it is kept.

### 8.5 What the result covers

The suite checks the identifier's syntax (3.1 ABNF, which does not
distinguish `0x1` from `0x7a69` or a padded from an unpadded address beyond
`idchar`), the DID document the resolver builds for it, its JSON-LD
representation and the resolution metadata. For the registry-minted
identifier all of that passes, so the string `getVehicleDID` produces after
the D10 fix is a conformant did:ethr identifier as far as the W3C suite can
tell, and the resolver produces a conformant document for it.

Two things the run does not establish, stated so that the number is not
read as more than it is:

* The document is still constructed by `did_resolver.py` from the identifier
  alone (section 5, last paragraph). The on-chain birth record (owner,
  `vinHash`, the ERC-1056 attribute) is not read and does not appear in the
  resolved document; the contract supplied the identifier, not the document.
* `blockchainAccountId` is emitted as `eip155:0x7a69:...` (hex chain id).
  The did:ethr method specification and CAIP-10 write the chain id in
  decimal (`eip155:31337:...`). The suite's 5.2.1 checks examine only
  `publicKeyJwk`, `publicKeyMultibase` and `publicKeyBase58`, so this value
  is not tested; it is a resolver detail outside the suite's reach and is
  recorded here, not fixed.


## 9. Review 02 (2026-10-03): S-10 and changes since this run

**Status: the external suite was NOT re-run.** It needs a clone of
`w3c/did-test-suite` plus its npm install, and neither is available offline in
the remediation session. The numbers in sections 3-5 still describe the
resolver at `434669d`. This section records what has changed since then and
what the changes are expected to do.

**S-10: a further root cause next to R1-R5.** `_parse_did` raised a bare
`ValueError` for every malformed DID *and* for every method missing from the
`DIDMethod` enum, and `resolve()` turned both into `internalError`. That left
the `methodNotSupported` branch reachable only for `did:web`, which is in the
enum but has no resolver. `did:example:12345` and `did:foo:bar` therefore came
back as `internalError`. The suite's own unsupported-method execution used
`did:web:example.com`, so this cause produced no failure in the run above. The
internal checker did catch it: item 7.1.2 was PARTIAL.

Fixed in `did_resolver.py` (commit "S-10: resolver returns cache copies and
correct DID error codes"):

| Input | Before | After |
|---|---|---|
| Violates the DID Core 3.1 ABNF (`did:ethr_0x1234`, `did:mobi:`, `not-a-did`) | `internalError`, or a document for `did:mobi:` | `invalidDid` |
| `did:nft` without a tokenId | `internalError` | `invalidDid` |
| `did:ethr` whose id is not a 20-byte address or a 33-byte compressed key (`did:ethr:not-an-address`), or has extra segments or a bad chain id | resolved to a document | `invalidDid` |
| Method not implemented (`did:foo:bar`, `did:example:…`) | `internalError` | `methodNotSupported` |
| `blockchainAccountId` (CAIP-10) | `eip155:0x1:<addr>` (hex chain id) | `eip155:1:<addr>` (decimal, as CAIP-2/10 require) |
| Cache | returned the cached object itself, so a caller's mutation poisoned later resolutions | private deep copies; optional TTL |

**Expected effect on the suite (a prediction, not a measurement).** The
`generate_implementations.py` output was regenerated into a scratch directory
and diffed against `implementations/`; the files committed here were left
unchanged so that they keep matching the reports. The diff is:

- the three invalid-DID executions (`did:ethr_0x1234`, `did:nft:0x1:0xabc`,
  `did:mobi:`) now carry `error: "invalidDid"`, and `did:mobi:` no longer
  yields a document;
- `blockchainAccountId` is in decimal CAIP-10 form.

R5's six failures should therefore clear. R1-R4 are untouched, so most of the
113 failures remain. A re-run may also *add* failures, because a guarded test
now fires on the error results, which still carry `contentType` and the
8-key `didDocumentMetadata` (R2/R3). The 142/142 on identifiers and documents
is not expected to change.

**Internal checker.** The S-10 fix moves exactly one item: DID Core 7.1.2
"Unsupported DID method MUST yield a resolution error ('methodNotSupported')"
goes from PARTIAL to PASS, and the executable score goes from 93.2 % to
94.3 % (41 PASS, 1 PARTIAL, 2 FAIL, out of 44). The checker's scoring was not
changed (T-7 is an author decision). With malformed DIDs now returning
`invalidDid`, the two malformed-DID checks that T-7 says "PASS on any error"
also return the right code.

**Correction (2026-10-04).** The sentence above that the committed files "were
left unchanged" stopped being true in commit `f646e88` (Pass 2 re-review),
which regenerated `implementations/` after S-10. From then until the re-run in
section 8 the committed inputs did not match the 2026-09-24 reports. The exact
inputs of the 2026-09-24 run are recoverable with
`git show ed62314:docs/conformance/implementations/<file>`.

## 10. Re-run 2026-10-04 (review 02 follow-up F-B): resolver after S-10

**Status: measured.** The suite was re-run against the current resolver
(`did_resolver.py` as of `bd18057`, "S-10: resolver returns cache copies and
correct DID error codes"; repository tree `d2e6a58`). Neither the resolver nor
the suite was changed for this run.

### 10.1 Conditions (identical procedure to sections 2-3)

| Item | 2026-09-24 run | 2026-10-04 re-run |
|---|---|---|
| Suite | `w3c/did-test-suite` @ `939b31d07d5b…` | same commit (fresh clone, `git checkout 939b31d`) |
| Install | `npm install` (lerna bootstrap) | same; jest 26.6.3, jest-did-matcher 0.0.1 resolved from the lockfile (npm rewrote the three `package-lock.json` files, as in any fresh install) |
| Runtime | Node v22.22.2, npm 10.9.7 | Node **v22.22.0**, npm **10.9.4** (container image; patch-level difference only) |
| Inputs | `generate_implementations.py` @ `ed62314` inputs | `python3 docs/conformance/generate_implementations.py docs/conformance/implementations` (same script, unchanged); diff to the `f646e88` files is timestamps only |
| Registration / runner | `suite-run/run-cvin-cli.js cvin` and `control` (jest CLI, narrowed `default.js`, restored afterwards) | same files, unchanged |
| Python | 3.11.15 | 3.11.15 |
| Harness check | control 347/347 | control **347/347** (identifier 6/6, core properties 58/58, production 106/106, consumption 42/42, resolution 135/135) |

The test inventory is identical: every one of the 441 CVIN tests in the new
run has the same ancestor path and title as a test in the old run, and vice
versa. The comparison below is therefore test-by-test.

Raw output: `reports/jest-cvin/cvin-cli-<suite>-2026-10-04.{json,txt}`,
`reports/jest-control/control-cli-<suite>-2026-10-04.json`,
`reports/did-spec-test-run-2026-10-04.json` and
`reports/did-implementation-report-2026-10-04.html` (suite HTML report built
with `cli-to-report.js` + `report/generate-report.js`). The 2026-09-24 files
are kept unchanged next to them.

### 10.2 Totals and per suite (old → new)

| DID Core section / suite | Tests | Passed 09-24 | Passed 10-04 | Failed 09-24 | Failed 10-04 |
|---|---|---|---|---|---|
| 3.1 Identifier syntax | 3 | 3 | 3 | 0 | 0 |
| 5.x Core properties + 7.3 | 88 | 88 | 88 | 0 | 0 |
| 6.1 / 6.3.1 Production | 48 | 48 | 48 | 0 | 0 |
| 6.3.2 Consumption | 3 | 3 | 3 | 0 | 0 |
| 7.1 DID Resolution | 299 | 186 | **194** | 113 | **105** |
| **Total** | **441** | **328 (74.4 %)** | **336 (76.2 %)** | **113** | **105** |

Per resolver (DID Resolution suite):

| Resolver file | Tests | 09-24 passed / failed | 10-04 passed / failed | Δ |
|---|---|---|---|---|
| `cvin-resolver-ethr.json` | 119 | 77 / 42 | **79 / 40** | +2 |
| `cvin-resolver-mobi.json` | 90 | 52 / 38 | **58 / 32** | +6 |
| `cvin-resolver-nft.json` | 90 | 57 / 33 | **57 / 33** | 0 |

Distinct failing normative statements: 17 → 15.

### 10.3 The eight tests that changed (all failed → passed; none passed → failed)

| Resolver | Execution | Test | Why it now passes |
|---|---|---|---|
| ethr | `did:ethr_0x1234` | 7.1 "This input is REQUIRED and the value MUST be a conformant DID" | error is now `invalidDid`, so the suite's guard (`did-resolution.js:10`: `error !== 'invalidDid'` ⇒ input must be a valid DID) no longer applies |
| ethr | `did:ethr_0x1234` | 7.1.2 invalidDid | `invalidDid` instead of `internalError` |
| mobi | `did:mobi:` | 7.1 "This input is REQUIRED …" | as for ethr |
| mobi | `did:mobi:` | 7.1.2 invalidDid | `invalidDid` instead of a resolved document |
| mobi | `did:mobi:` | 7.1 "If the resolution is not successful, this structure MUST contain an error property" | `error` is now a non-empty string |
| mobi | `did:mobi:` | 7.1 "If the resolution is unsuccessful, this value [didDocument] MUST be empty" | `didDocument` is now `null` (was counted under R1) |
| mobi | `did:mobi:` | 7.1.2 "The value of this property [error] MUST be a single keyword ASCII string" | `"invalidDid"` instead of `null` (was counted under R1) |
| mobi | `did:mobi:` | 7.1.3 canonicalId "MUST be produced by … the same DID Method" | no longer evaluated against a document whose `canonicalId` is `null` (was counted under R3) |

### 10.4 Root causes, updated

Counts are failures in the 2026-10-04 run; line numbers refer to
`2_w3c-ssi-layer/did-resolution/did_resolver.py` at `bd18057`.

| Root cause | Location | Failures 09-24 | Failures 10-04 | Status |
|---|---|---|---|---|
| **R1** `error: null` / `errorMessage: null` always present, so every successful resolution is judged unsuccessful | `DIDResolutionMetadata` defaults, lines 137-138; serialised unconditionally by `asdict()` in `to_dict()`, line 164 | 24 | **22** | open (−2: the `did:mobi:` execution is now a real error, so its two R1 failures went away. Remaining: 12 on the six successful executions (document not empty ×3, stream not empty ×3, `error` not a string ×6) and the 10 "MUST be an empty metadata structure" failures, of which the 4 on error executions are really R3, kept here for comparability with section 4) |
| **R2** `contentType` emitted on `resolve()`, including on errors | default `"application/did+ld+json"`, line 135 | 21 | **21** | open, unchanged |
| **R3** `didDocumentMetadata` is a fixed 8-key structure with `null` placeholders, never empty on error | `DIDDocumentMetadata` dataclass, lines 142-151; `asdict()` line 166; error paths build `DIDDocumentMetadata()` at lines 279, 305, 314 | 52 | **51** | open (−1, `did:mobi:` canonicalId, see 8.3) |
| **R4** `created` / `retrieved` not XML Datetime (`isoformat()` with microseconds and `+00:00`) | `created=` at lines 393, 455, 499, 550; `retrieved` at lines 258, 283 | 10 | **10** | open, unchanged |
| **R5** syntax errors not reported as `invalidDid`; `did:mobi:` resolved | was `_parse_did` → `internalError` | 6 | **1** | **cleared in the resolver** (S-10). The one remaining failure is R5′ below |
| **R5′** (new attribution, not a new failure) the `did:nft` invalid-DID test vector is syntactically valid DID | `docs/conformance/generate_implementations.py` line 76 (`"did:nft:0x1:0xabc"` registered as `invalidDidErrorOutcome`) | (1, counted in R5) | **1** | test-vector issue, not a resolver defect |
| **Total** | | **113** | **105** | |

**R5′ in detail.** For `did:nft:0x1:0xabc` the resolver now returns
`invalidDid` (`_resolve_nft`, lines 426-428: a `did:nft` needs three
segments). The suite's invalidDid test (`suites/did-resolution/did-resolution.js:157-160`
at `939b31d`) asserts three things: the code is `invalidDid` (now passes),
**and** `expect(did).not.toBeValidDid()`, **and** an empty document. The
second assertion fails because `did:nft:0x1:0xabc` conforms to the generic
DID Core 3.1 ABNF; it is only invalid under the `did:nft` method's own syntax.
The suite reads `invalidDid` as "violates the generic DID syntax"; the
resolver uses it for method-specific syntax as well (which the DID Resolution
specification permits). In the 2026-09-24 run the same test failed one
assertion earlier (`internalError` ≠ `invalidDid`), so it was counted under
R5. It is not a resolver defect. It would clear only if the registered vector
were changed to a DID that violates the generic ABNF; that was not done here,
because changing the test inputs would change what is measured.

**No new failures.** No test that passed on 2026-09-24 fails now, and no new
failure message appears in any suite.

### 10.5 Did the section 7 prediction hold?

| Prediction (section 7) | Outcome |
|---|---|
| "R5's six failures should therefore clear" | **Mostly.** 5 of 6 cleared. The sixth (`did:nft:0x1:0xabc`) now fails on a different assertion of the same test (R5′, a vector issue, not the resolver). |
| "R1-R4 are untouched, so most of the 113 failures remain" | **Held.** R2 and R4 are unchanged; R1 and R3 lost 2 and 1 failures as a side effect of `did:mobi:` becoming a real error. 105 of 113 remain. |
| "A re-run may also *add* failures" (guarded tests firing on error results carrying `contentType` and the 8-key metadata) | **Did not happen.** Because of R1, the suite already treated *every* execution, including the old `did:mobi:` "success", as unsuccessful (`hasOwnProperty('error')` is true for `error: null`), so the error-guarded tests were already firing on all 10 executions in the old run. There was nothing left to newly trigger. |
| "The 142/142 on identifiers and documents is not expected to change" | **Held.** 142/142. The CAIP-10 decimal chain-id change is not examined by any suite test (`blockchainAccountId` is not checked), so it moved no number. |

Net: **328/441 → 336/441** (74.4 % → 76.2 %); DID Resolution **186/299 →
194/299**; ethr 77 → 79/119, mobi 52 → 58/90, nft 57 → 57/90. 104 of the
105 remaining failures come from R1-R4 in the metadata dataclasses
(`DIDResolutionMetadata`, `DIDDocumentMetadata`) and the timestamp format;
the remaining one is the R5′ test vector. What a fix of R1-R4 would score is
not predicted here: removing `error: null` changes which guarded tests the
suite evaluates, so it has to be measured.

## 11. Re-run 2026-10-04b (stream G-R): resolver after the R1-R4 fix

**Status: measured.** The suite was re-run after R1-R4 were fixed in the
resolver (`fa5e373`, plus the message-only change `93f4331`). The suite and
the runner were not changed. The generator needed a small adaptation (9.1),
because the unchanged script cannot run against the fixed resolver.

### 11.1 What changed in the resolver, and the one change to the generator

| Root cause | Fix (`2_w3c-ssi-layer/did-resolution/did_resolver.py` @ `93f4331`) |
|---|---|
| **R1** | `DIDResolutionMetadata.to_dict()` (l. 164) omits `None` values. `error` / `errorMessage` appear only on failure. `DIDResolutionResult.to_dict()` no longer uses `asdict()` |
| **R2** | `contentType` defaults to `None` (l. 159), so `resolve()` never carries it. The new `resolve_representation(did, accept)` (l. 376) returns `didDocumentStream` = `json.dumps(didDocument)` with `contentType: application/did+ld+json`. On failure the stream is empty and `contentType` is absent. An unsupported `accept` returns `representationNotSupported` |
| **R3** | `DIDDocumentMetadata.to_dict()` (l. 187) omits `None`, an empty `equivalentId`, and `deactivated` unless it is `true`. A failed resolution gives `{}` |
| **R4** | `xml_datetime()` (l. 137): UTC, `Z`, no fractional seconds (`2026-10-04T22:08:15Z`). Used for `created` (l. 489/551/595/646) and `retrieved` (l. 317/342/391) |

The dataclass attributes are unchanged, so Python callers that read
`result.didResolutionMetadata.error` still see `None` on success. Only the
serialized form (`to_dict()`) changed. Unit tests:
`tests/test_did_resolver_metadata_shape.py` (37 R1-R4 tests that fail on
`f73e81e`, plus 10 guard tests).

**Generator (`4eef1c2`).** `generate_implementations.py` did not run
unchanged against the fixed resolver. Its success assertion
`result["didResolutionMetadata"]["error"] is None` raises `KeyError` once
`error` is absent. It also read `contentType` from the `resolve()` output, and
it registered that same output as the `resolveRepresentation` execution,
because the project had no resolveRepresentation function. The adaptation:

* asserts that `error` is absent;
* takes `supportedContentTypes`, the method file's representation entry and
  the `resolveRepresentation` execution from `resolve_representation()`.

The DIDs, the error vectors (including the R5′ vector `did:nft:0x1:0xabc`),
the outcome mapping and the file layout are unchanged. Every value in the
input files is still taken unchanged from the resolver.

### 11.2 Conditions

The procedure is the one in section 8.1, with these differences:

* A fresh clone at `939b31d`, then `npm install`. The F-B clone was moved
  aside, not reused.
* Inputs were generated from `4eef1c2`.
* Raw output is in the `*-2026-10-04b.*` files:
  - `reports/jest-cvin/cvin-cli-<suite>-2026-10-04b.{json,txt}`
  - `reports/jest-control/control-cli-<suite>-2026-10-04b.json`
  - `reports/did-spec-test-run-2026-10-04b.json`
  - `reports/did-implementation-report-2026-10-04b.html`

Node v22.22.0 / npm 10.9.4, jest 26.6.3, Python 3.11.15. Control (WG
example) **347/347**. The 09-24 and 10-04 files are kept unchanged.

### 11.3 Results (10-04 → 10-04b)

| Suite | 10-04 passed / tests | 10-04b passed / tests |
|---|---|---|
| 3.1 Identifier syntax | 3 / 3 | 3 / 3 |
| 5.x Core properties + 7.3 | 88 / 88 | 88 / 88 |
| 6.1 / 6.3.1 Production | 48 / 48 | 48 / 48 |
| 6.3.2 Consumption | 3 / 3 | 3 / 3 |
| 7.1 DID Resolution | 194 / 299 | **193 / 194** |
| **Total** | **336 / 441 (76.2 %)** | **335 / 336 (99.7 %)** |

| Resolver | 10-04 | 10-04b |
|---|---|---|
| `cvin-resolver-ethr.json` | 79 / 119 | **78 / 78** |
| `cvin-resolver-mobi.json` | 58 / 90 | **58 / 58** |
| `cvin-resolver-nft.json` | 57 / 90 | **57 / 58** (R5′) |

**The denominator changed, and that is expected.** The suite defines many
`it` blocks only when a property is present in the metadata, for example
`if (didDocumentMetadata.hasOwnProperty('canonicalId'))` or `if
(didResolutionMetadata.hasOwnProperty('error'))`. The old output emitted
every key, null or not, so the suite generated 105 tests that do not apply
once absent properties are omitted. The section 8.4 estimate of ≈440/441
assumed a fixed inventory and was therefore wrong in its denominator; section
8.5 had already warned that the effect had to be measured.

The comparison below is test by test. Tests are matched by ancestor path,
title and occurrence index, because a `resolve` and a
`resolveRepresentation` execution of the same DID share an ancestor path.
One test needed manual pairing: the `contentType` "ASCII media type" test.
It is now generated only for the `resolveRepresentation` execution, so it is
paired with the passing `resolveRepresentation` instance from the old run.

| Old → new status | Tests |
|---|---|
| passed → passed | 157 |
| failed → passed | **36** |
| failed → failed | 1 (R5′) |
| passed → failed | **0** |
| failed → not generated | 68 |
| passed → not generated | 37 |
| not generated → generated | 0 |

The non-resolution suites have the same inventory as before, with the same
results.

On the 336 tests present in both runs, the score went from 299 to 335.

The 37 passing tests that are no longer generated:

* 10 for `deactivated: false`;
* 20 for `equivalentId: []` (two tests per execution, passed vacuously on an
  empty list);
* 7 for "canonicalId same method" (passed vacuously when there is no
  document).

None of them is lost coverage of a property the resolver emits.

### 11.4 Root causes (10-04 → 10-04b)

| Root cause | 10-04 failures | failed → passed | failed → not generated | 10-04b failures |
|---|---|---|---|---|
| **R1** | 22 | 16 (document empty ×3, stream empty ×3, "empty metadata structure" ×10) | 6 ("`error` single keyword", success executions) | **0** |
| **R2** | 21 | 14 ("MUST NOT be present if resolve" ×7, "caller … MUST use this value" ×7) | 7 ("ASCII media type" on the 7 `resolve` executions, which have no stream) | **0** |
| **R3** | 51 | 0 | 51 (canonicalId ×13, nextUpdate ×10, nextVersionId ×10, updated ×10, versionId ×8) | **0** |
| **R4** | 10 | 6 (`created` on success executions) | 4 (`created: null` on error executions) | **0** |
| **R5′** | 1 | – | – | **1** (unchanged; test vector, section 8.4) |
| **Total** | **105** | **36** | **68** | **1** |

Distinct failing normative statements: 15 → 1.

The remaining failure is the
`did:nft:0x1:0xabc` invalidDid test. The resolver returns `invalidDid`, but
`expect(did).not.toBeValidDid()` fails because the vector is a valid generic
DID. The vector was left as it is.

### 11.5 Internal checker (register #4)

`python3 cv2x-testbed/scripts/w3c_compliance_checker.py`:

* 94.3 % before the fix (`f73e81e`).
* 92.0 % with the R1-R4 resolver and the unchanged checker.
* **94.3 % after `1035bcf`.**

Only one check moved: DID Core 7.1.2 "Resolution MUST return DID resolution
metadata (contentType, retrieved)". It asserted
`contentType == "application/did+ld+json"` on `resolve()` results, which is
the R2 defect. It went PASS → FAIL against the fixed resolver. `1035bcf`
adapts the check to the new contract: `contentType` must be absent from
`resolve()` and equal to `application/did+ld+json` on
`resolve_representation()`, whose stream must parse to the resolved DID. The
check slot, its weight and the scoring are unchanged. The 7.1.3 `created`
check still passes (`datetime.fromisoformat` accepts `Z` on Python 3.11).
