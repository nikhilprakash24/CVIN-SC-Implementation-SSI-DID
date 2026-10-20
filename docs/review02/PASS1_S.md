# Review 02, Pass 1, stream P1-S: SSI / VC layer

**Input:** `docs/REVIEW_02_CODEBASE.md` §S, T-3 and §2; `docs/PLAN_REVIEW_02.md` (P1-S).
**Base:** `d0fe9f0`. Four local commits, not pushed.
**Scope:** `2_w3c-ssi-layer/**` and `cv2x-testbed/identity/w3c_verifiable_credentials.py`, plus the verifier construction sites in
`cv2x-testbed/sumo/sumo_identity_integration.py` and `cv2x-testbed/scripts/test_use_cases.py`.
`docs/conformance/W3C_DID_TEST_SUITE.md` gets a new §7.

| Commit | Findings |
|---|---|
| S-10: resolver returns cache copies and correct DID error codes | S-10 |
| S-1 S-2 S-4 S-5 S-6 S-7 S-9: harden the canonical VC verifier | S-1, S-2, S-4, S-5, S-6, S-7, S-9, T-3 (canonical half) |
| S-2: MOBI VID verifiers check revocation against issuer-bound registries | S-2 (MOBI call sites) |
| T-3: explicit trusted-issuer allow-list in the testbed VC shim and SUMO | T-3, S-1/S-2 call sites |
| docs (this file, the READMEs, conformance §7) | — |

## 1. Gates

| Gate | Before | After |
|---|---|---|
| `python3 -m pytest 2_w3c-ssi-layer -q` | 60 passed (0 skipped once Hardhat artifacts are compiled; 22 skipped without them) | **161 passed, 0 skipped** |
| `python3 cv2x-testbed/scripts/test_use_cases.py` | 12/12 | **12/12** |
| `sumo_identity_integration.py --simulate --duration 5 --vehicles 10` | sent 500, verified 400, failures 3 | identical counts; "all injected bad messages rejected" |
| `sumo/run_v2v_stats.py --runs 3 --duration 5 --vehicles 10` | — | 3/3 runs ok (output written to a scratch path; `sumo/results/` untouched) |
| `w3c_compliance_checker.py` SCORE | 93.2 % | **94.3 %** (see §4) |
| `4_comparison-framework/security-analysis/attack_scenarios.py` off-chain cells | — | unchanged: DEFENDED ×4, PARTIAL ×2 |

New tests:
- `verifiable-credentials/tests/test_review02_negative.py`: 60 tests.
- `verifiable-credentials/tests/test_t3_testbed_trusted_issuers.py`: 9 tests.
- `did-resolution/tests/test_did_resolver_review02.py`: 28 tests.
- `mobi-vid/tests/test_mobi_vid_layer.py`: 4 tests in the new `TestRevocationStatus` class.

**Checked against the old code.** Each new file was copied into a `git archive` of `434669d` and run there.

| File | Fail on old code | Pass on old code | What passes, and why that is expected |
|---|---|---|---|
| `test_review02_negative.py` | 54 | 6 | Positive controls: the genuine holder, the correct registry, a genuine VP, the challenge mismatch, and `v=29`, which eth_account already rejected |
| `test_t3_testbed_trusted_issuers.py` | 7 | 2 | Positive controls |
| `test_did_resolver_review02.py` | 26 | 2 | `did:web` was already `methodNotSupported`; an already-decimal chain id |
| MOBI revocation tests | 4 | 0 | — |

Every reviewer PoC is one of the tests that fail on the old code:
- `/tmp/review_c/poc.py` items 1–7;
- `/tmp/review_d/poc_ssi_selfissued.py`;
- `/tmp/review_d/poc_resolver.py`.

**Changed existing tests (configuration only, no assertion weakened).** The MOBI integration tests now pass the issuers' status registries to `BirthCertificateVerifier` and `VehicleHistoryAggregator`. Without them the verifier now fails closed. Two tamper tests also gained an assertion that the error is a signature error.

## 2. Per-finding changes

**S-1: holder binding** (`vc_verifier.py`)
- `verify_presentation` checks every embedded credential: `credentialSubject.id` must equal `vp.holder`. With list subjects, the holder must be one of the ids.
- A holder may also present a credential through an explicit relation, `subject_holder_binding` (a mapping `{subject: {holders}}` or a callable).
- A credential whose subject has no `id` is rejected unless `allow_bearer_credentials=True`.
- The failure is recorded as `[holder_binding]` in that credential's report.
- The `vc_holder.py` docstring no longer claims that the VP signature alone stops a stolen credential. A second comment there was also wrong: the holder signature does cover `disclosedClaims`.

**S-2: fail-closed status** (`vc_issuer.py`, `vc_verifier.py`)
- A `RevocationRegistry` now has a unique `registry_id`. The old shared `…/status/default` id is gone.
- Each registry is bound to one `issuer_did`. An issuer adopts its registry and refuses one that is bound to another issuer.
- The verifier takes one registry or several, keyed by `registry_id`. For each `credentialStatus` it checks:
  1. the `type` is `CvinRevocationRegistry2024`;
  2. a registry with the credential's `statusListCredential` is configured;
  3. that registry is bound to the credential's issuer;
  4. `status.id == <list>#<vc.id>`;
  5. the credential is not revoked.
- If any of these fails, the credential is invalid.

**S-4: dates** (`vc_issuer.parse_datetime`)
- Dates are parsed as XML Schema dateTime with a required `Z` or `±hh:mm` zone and compared as UTC instants.
- `validFrom` and VC 1.1 `issuanceDate` are lower bounds; `validUntil` and `expirationDate` are upper bounds.
- An unparseable value (such as "never"), a naive value or a non-string value is invalid.

**S-5: proof metadata.** The verifier checks four proof fields:
- `type == DataIntegrityProof`;
- `cryptosuite == eip191-secp256k1-recovery-2024`;
- `proofPurpose` is `assertionMethod` for a VC and `authentication` for a VP;
- the DID of `verificationMethod` is the issuer's DID (holder's DID for a VP).

`created` must parse when it is present.

**S-6: challenge**
- `verify_presentation` raises `ValueError` if `expected_challenge` is `None` or empty.
- An optional `NonceStore` makes challenges single-use (`issue()` / `consume()`).
- An optional `max_proof_age_s` bounds the VP's `created`.
- Every call site in the repo already passed a literal challenge, so none needed a code change.

**S-7: canonical signatures** (`check_signature_encoding`). A signature must be exactly 65 bytes, with `v ∈ {27, 28}` and `1 ≤ s ≤ N/2`. This applies to both VC and VP proofs.

**S-9: malformed input**
- The structure of `disclosedClaims` is validated: it must be an object, each entry needs `value`, and `salt` must be a string.
- `verify_credential` and `verify_presentation` turn any other exception into an `[internal]` failure instead of raising.

**S-10: resolver.** See `docs/conformance/W3C_DID_TEST_SUITE.md` §7. In short:
- the cache returns deep copies and has an optional TTL;
- malformed DIDs return `invalidDid`, including a `did:ethr` id that is not an address or compressed key;
- unknown methods return `methodNotSupported`;
- CAIP-10 chain ids are decimal.

**T-3: trusted issuers**
- In the canonical verifier, passing `trusted_issuers` makes the registry an allow-list that also gates address-bearing `did:ethr` issuers. The registered address must match the address in the DID.
- `DIDKeyRegistry` keeps holder key bindings separate from issuer trust.
- In the shim, issuers and wallets no longer self-register. `CredentialVerifier(trusted_issuers=[issuer, …])` (or a registry) is the allow-list, and the issuers' revocation registries come with it. With no list, nobody is trusted.
- Wallets with demo DIDs (`did:ethr:0x1:0xTESLA123`) record a first-binding-wins key binding in `SHARED_HOLDER_KEYS`. It is used for VP holders only, and rebinding a DID to another key raises.
- `SSIIdentityLayer` trusts only the consortium issuer.

## 3. Behaviour changes callers must know

1. **A verifier without the issuer's registry rejects every revocable credential.** Every issued credential is revocable by default. Pass `revocation_registry=issuer.revocation_registry`, a list of registries, or (shim) `trusted_issuers=[issuer]`. In MOBI, pass `status_registries=[BirthCertificateIssuer.status_registry / LifecycleEventRecorder.status_registry]`; `issue_birth_certificate` also returns `statusRegistry`.
2. **Several issuers can no longer share one `RevocationRegistry`.** Construction raises. `SHARED_REVOCATION_REGISTRY` and `SHARED_TRUSTED_ISSUERS` are removed from the shim.
3. **A presentation fails when the holder is not the subject.** The use cases where an owner presents a vehicle's credential (UC 3, 6, 10) now configure `subject_holder_binding`. In a deployment this relation comes from the vehicle DID's controller or the on-chain owner.
4. **`verify_presentation(vp, None, …)` raises `ValueError`.**
5. **Shim `CredentialVerifier()` with no arguments trusts nobody.** `scenarios/cv2x_identity_integration.py` imports it but never constructs it, so it is unaffected.
6. **Non-canonical (high-s, or `v` in {0, 1}) signatures from external signers are rejected.** eth_account always produces canonical ones.
7. **Timing.** `verify_credential` does slightly more work: about +0.013 ms (≈ +6 %) in a 2000-iteration median on this machine. If a chapter cites `run_verify_richness.py` or the SUMO cold-verify figures, re-run them. Warm SUMO verification (signature recovery only) is unchanged.
8. **Resolver.** It no longer resolves malformed `did:ethr` ids. `blockchainAccountId` changes from `eip155:0x1:…` to `eip155:1:…`.

## 4. Compliance checker (T-7 untouched)

The score moves from 93.2 % to **94.3 %**. Exactly one check changed: DID Core 7.1.2 "Unsupported DID method MUST yield a resolution error ('methodNotSupported')" went from PARTIAL to PASS. The cause is the S-10 resolver fix (`did:example:12345` now returns `methodNotSupported`). That leaves 41 PASS, 1 PARTIAL and 2 FAIL out of 44. Every VC/VP check still passes. The CI floor (93.0 %) is met.

For T-7: the malformed-DID checks now get the correct `invalidDid` code. Tightening those checks would no longer cost score.

## 5. Doc text to update (not edited here: shared docs)

- **Register #24 / MEASUREMENT_CONDITIONS.** The S-10 root cause and its fix are recorded in `W3C_DID_TEST_SUITE.md` §7. The 328/441 figure was not re-run; R5 is expected to clear.
- **Register #4.** 93.2 % becomes 94.3 % after S-10, with the reason above.
- **README / HANDOFF.** The test count goes from 60 to 161 Python tests.
- **CI (Q-2).** `w3c-compliance.yml` runs only `test_vc_layer.py`, so the new files do not run in CI until Q-2 is done.
- **`attack_scenarios.py` identity-theft cell (outside this stream).** It still tests only the weaker same-DID attack. Add the thief-own-DID variant; it is now DEFENDED.

## 6. Not done / left open

- S-3: DID resolution, rotated keys and the chain id in the key binding. This is Pass 2.
- S-8: canonicalisation.
- `did:key` and `did:nft` address validation. The repo's `did:key` convention is not the multibase `did:key`.
- The external DID suite was not re-run (no offline clone).
