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

Mapping rules (see the script's docstring):

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

## 3. Results

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
| `implementations/cvin-resolver-{ethr,mobi,nft}.json` | resolver entries (registered in did-resolution) |
| `suite-run/run-cvin-cli.js` | jest-CLI runner used for the reported numbers (CVIN and control modes) |
| `suite-run/run-cvin.js` | runner through the suite's `services/runSuite.js` (`globals` path; affected by the `toBeInfraMap` realm artifact, kept for transparency) |
| `suite-run/cli-to-report.js` | converts jest `--json` output into the suite's report input format |
| `suite-run/default.js-registration.diff` | the registration edit to the suite's `default.js` files |
| `reports/jest-cvin/cvin-cli-<suite>.json` / `.txt` | raw jest `--json` results and verbose transcripts for the five suites (CVIN) |
| `reports/jest-control/control-cli-<suite>.json` | raw jest results for the WG example implementation on the same harness |
| `reports/did-implementation-report.html` | the suite's own HTML report (`report/generate-report.js`) built from the CVIN jest-CLI results (identifier, core-properties, production, resolution) |
| `reports/did-spec-test-run.latest.json` | sanitized result set that the HTML report was generated from |
| `reports/globals-path-run-cvin-detailed-results.json` | the discarded `globals`-path run, with failure messages |
| `internal/w3c_compliance_report.json` | output of `cv2x-testbed/scripts/w3c_compliance_checker.py` for the comparison in section 5 |
