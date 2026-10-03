# Side-Papers Register

Self-contained results and methods that could stand alone as a short paper or
technical note **separate from the core comparative thesis**. Each entry: premise,
target venue type, supporting material, and why it is a side-paper rather than a
core chapter. Several draw on the same measured artifacts as the thesis — the note
"overlap" flags where a result is *also* reported in a thesis chapter (to avoid
double-counting a single contribution as two).

| # | Working title | Type |
|---|---|---|
| SP-1 | A Silent Signature: finding & fixing an unverified on-chain attestation | Security note |
| SP-2 | Measuring the account-abstraction tax (ERC-4337 EntryPoint overhead) | Measurement note |
| SP-3 | Hash-and-encrypt: an on-chain VIN privacy pattern | Applied-crypto note |
| SP-4 | Portability of a vehicle-identity profile (MOBI VID fidelity-per-gas) | Study (H4) |
| SP-5 | Blockchain-credential V2V verification fits the safety budget | Feasibility study (H3) |
| SP-6 | CVIN-Combined: a Pareto-optimal hybrid on the fidelity-per-gas frontier | Design paper (H5) |
| SP-7 | Two lenses for smart-contract identity security | Methodology |
| SP-8 | An executable W3C DID/VC compliance checker | Methodology/tools |

---

### SP-1 — "A Silent Signature"
**Premise.** MOBI VID's `attestEvent` stored an attestation signature it never
verified on-chain (role-gated only) — a forgery/replay gap — fixed with a
domain-separated EIP-191 `ecrecover` and a before/after revert test, at a measured
121,110 → 192,718 gas cost. **Material:** `contracts/MOBI/MOBIVIDRegistryV2.sol`,
`test/MOBIVID/MOBIVIDRegistry.test.js`, gas in `gas_benchmark.json`; Ch5 §5.6.
**Why side-paper:** a found-and-fixed vulnerability is a crisp standalone
contribution; the thesis reports it only as one security finding. **Overlap:** §5.6.

### SP-2 — "The Account-Abstraction Tax"
**Premise.** The same `setAttribute` costs 49,366 gas direct vs 96,228 through a
minimal EntryPoint — a cleanly isolated **46,862-gas/op** indirection overhead
(bundler/paymaster excluded). **Material:** `contracts/ERC4337/*`, `gas_benchmark.json`;
Ch5 §5.2. **Why side-paper:** a focused ERC-4337-costing result of interest beyond
vehicles. **Overlap:** §5.2 finding 3.

### SP-3 — "Hash-and-Encrypt VIN Privacy"
**Premise.** Where 4 of the compared standards leak plaintext VINs on-chain, MOBI
VID stores only a salted hash + AES-256-GCM ciphertext (HKDF key custody) and
resolves via `did:ethr` (avoiding the VIN-embedding `did:mobi:<VIN>` footgun).
**Material:** `MOBIVIDRegistryV2.sol`, VIN-cipher tests, `security_matrix.json`
privacy rows; Ch5 §5.6. **Why side-paper:** a reusable on-chain PII pattern.
**Overlap:** §5.6 finding 4.

### SP-4 — "Portability of a Vehicle-Identity Profile" (H4)
**Premise.** MOBI VID's 3 canonical operations mapped onto 5 native backends;
real gas + honest fidelity (5/5 vs 3/5). **Material:** `mobi_vid_backends.*`,
`scripts/mobi_vid_backend_sweep.js`; Ch5 §5.3.1. **Why side-paper:** a standalone
"can an application profile port across substrates" study. **Overlap:** §5.3.1.

### SP-5 — "V2V Verification Fits the Safety Budget" (H3)
**Premise.** Real secp256k1/P-256 crypto, N=30 seeded runs, 1.65M verifications:
SSI warm verify 0.165 ms [0.162, 0.168] vs a ~100 ms budget (~600× margin), attacks
caught with zero false pos/neg. **Material:** `v2v_latency_stats.json`,
`run_v2v_stats.py`, `sumo_identity_integration.py`; Ch5 §5.4. **Why side-paper:** a
self-contained feasibility result for the V2X community. **Overlap:** §5.4.

### SP-6 — "CVIN-Combined" (H5)
**Premise.** An ERC-1056 + ERC-735 hybrid reaches 5/5 fidelity at the lowest total
gas of any 5/5 backend (421,263 vs 798,621 / 870,577). **Material:**
`contracts/CVINCombined/CVINCombinedIdentity.sol`, `gas_benchmark.json`,
`mobi_vid_backends.json`; Ch5 §5.3/§5.3.1. **Why side-paper:** the novel-artifact
design paper. **Overlap:** §5.3. **Note:** this is the thesis's central design
contribution — a side-paper would be a condensed version, not a competing claim.

### SP-7 — "Two Lenses for Smart-Contract Identity Security" (methodology)
**Premise.** Combining a 54-scenario executable revert suite (43/43 defended,
differential controls) with a threat matrix for what revert-tests cannot express
(Sybil economics, recovery, PII leakage). **Material:** `test/security/securityScenarios.test.js`,
`security-analysis/{attack_scenarios.py, EXECUTABLE_ATTACK_SCENARIOS.md}`; Ch3 §3.5.
**Why side-paper:** a reusable methodology. **Overlap:** §5.6, Ch3.

### SP-8 — "An Executable W3C Compliance Checker" (methodology/tools)
**Premise.** A runnable checker that executes positive + negative checks against a
live VC/DID layer, CI-gated ≥90%, yielding a measured 93.2% with two documented
deviations counted as failures — not a self-graded checklist. **Material:**
`cv2x-testbed/scripts/w3c_compliance_checker.py`; Ch3 §3.6, Ch5 §5.5. **Why
side-paper:** a tool/method others can adopt. **Overlap:** §5.5.

---

**Guidance.** SP-4/5/6 are the strongest standalone results but are also core to the
thesis — if published separately they should be *condensed companions*, with the
thesis remaining the system-of-record. SP-1/2/3/7/8 are the most cleanly separable.
