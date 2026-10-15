# TDP-005 — Verification Cross-Reference Matrix

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Generated** by `docs/tdp/make_vcrm.py` from `docs/tdp/requirements.yaml`, the claim register (`docs/MEASUREMENT_CONDITIONS.md`), `docs/figures/dashboard_snapshot.json`, the tracked tree and `.github/workflows`. Do not edit by hand; edit the YAML and regenerate. Checked in CI.
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`; `docs/tdp/README.md` (TDP-000) for conventions.
**Format:** MIL-STD-961E section order (1 scope, 2 applicable documents, 3 requirements, 4 verification, 5 packaging, 6 notes). Format only; no certification is claimed.

## 0. Totals

| Status | Count | Meaning |
|---|---|---|
| VERIFIED | 27 | every evidence row V; files and CI present; threshold met; nothing pending |
| PARTIAL | 8 | some evidence V; at least one row non-V, a threshold unmet, an item missing, or a named trunk item still open |
| OPEN | 1 | no V evidence |

Register at generation: E 7, S 10, U 1, V 34 (52 rows).

## 1. Matrix

| Req | Title | Method | Evidence rows (status) | Threshold / verdict | Inspection | Status | Not met |
|---|---|---|---|---|---|---|---|
| SYS-01 | Identical operation set across substrates | Inspection | #25 (V), #34 (V) | — | 2/2 files | **VERIFIED** | — |
| SYS-02 | One evidence register for every number | Inspection | — | — | 3/3 files; CI step found | **VERIFIED** | — |
| SYS-03 | Declared conditions per measurement | Inspection | #25 (V), #27 (V), #34 (V) | — | 1/1 files | **VERIFIED** | — |
| PRF-01 | Nine-standard gas table, deterministic | Test | #25 (V) | 30/30 runs byte-identical: actual `True` → met | 2/2 files; CI step found | **VERIFIED** | — |
| PRF-02 | Create-identity ratio stated under its definition | Analysis | #6 (V), #25 (V) | — | — | **VERIFIED** | — |
| PRF-03 | Lifecycle gas over seventeen events | Test | #30 (V), #35 (V) | — | 2/2 files | **PARTIAL** | pending: WM-2 A6 (open) |
| PRF-04 | Lifetime cost model with sensitivity band | Analysis | #26 (V) | — | 1/1 files | **VERIFIED** | — |
| PRF-05 | On-chain footprint and read cost against history | Test | #31 (V), #49 (V), #51 (V) | — | — | **VERIFIED** | — |
| PRF-07 | Relayed and account-abstracted write cost | Test | #34 (V), #50 (V) | — | — | **VERIFIED** | — |
| PRF-06 | Dominance analysis on declared criteria | Analysis | #36 (V) | — | 1/1 files | **VERIFIED** | — |
| SEC-01 | Executable revert harness, strict reasons | Test | #28 (V) | 43 applicable cells DEFENDED: actual `43` → met | 1/1 files | **VERIFIED** | — |
| SEC-02 | Signed generation time, freshness window and replay cache | Test | #21 (V), #45 (V) | — | 2/2 files | **VERIFIED** | — |
| SEC-03 | Revocation staleness bounded by the re-check cadence | Test | #32 (V), #37 (V), #46 (V) | I3 at k=25 PASS (bound 24): actual `PASS` → met | — | **VERIFIED** | — |
| SEC-04 | Revoked key under clock skew | Test | #32 (V), #37 (V) | — | 1/1 files | **PARTIAL** | pending: WM-2 A3b (open) |
| SEC-05 | Attestation authority | Test | #28 (V) | — | — | **PARTIAL** | pending: D54 (open), WM-2 C2 (open) |
| SEC-06 | VIN confidentiality on chain | Inspection | #28 (V) | — | 2/2 files | **PARTIAL** | pending: D64 (open) |
| SEC-07 | Pseudonym pool observability | Test | #38 (V) | pre-registered verdict as it fell: **FAIL** | — | **PARTIAL** | pending: WM-2 A3b (open) |
| STD-01 | Internal structural checker at or above ninety percent | Test | #4 (V) | score >= 90: actual `94.3` → met | 1/1 files; CI step found | **PARTIAL** | pending: WM-2 C1 (open) |
| STD-02 | External DID test suite | Test | #24 (V) | 335 of 336 generated tests: actual `335` → met | 1/1 files | **VERIFIED** | — |
| STD-03 | MOBI-VID-inspired lifecycle on several backends | Demonstration | #30 (V), #33 (V) | — | 2/2 files | **VERIFIED** | — |
| STD-04 | Database parity for lifecycle writes | Test | #33 (V) | pre-registered verdict as it fell: **FAIL** | — | **VERIFIED** | — |
| RTV-01 | Warm credential verification inside the identity budget share | Test | #27 (V) | SSI warm verify median <= 0.5 ms: actual `0.1528` → met | 1/1 files | **PARTIAL** | pending: WM-2 A3b (open) |
| RTV-02 | Uncached chain read at message time reported | Test | #21 (V) | — | — | **VERIFIED** | — |
| RTV-03 | Freshness-k curve with both refresh modes | Test | #32 (V), #37 (V), #52 (V) | — | 1/1 files | **VERIFIED** | — |
| RTV-04 | Signed message size | Test | #23 (V) | — | — | **VERIFIED** | — |
| INF-01 | SPaT verification cost against BSM (I1) | Test | #44 (V) | pre-registered verdict as it fell: **outside band, not falsified** | — | **VERIFIED** | — |
| INF-02 | Registered attacks rejected for their reasons (I2) | Test | #45 (V) | 30/30 runs, all 15 checks as expected: actual `30` → met | 1/1 files | **VERIFIED** | — |
| INF-03 | Revoked roadside unit trusted for at most k minus 1 messages (I3) | Test | #46 (V) | pre-registered verdict as it fell: **PASS** | — | **VERIFIED** | — |
| INF-04 | Roadside unit identity cost on chain (I4) | Test | #47 (V) | — | 1/1 files | **VERIFIED** | — |
| INF-05 | Back-haul operation cost (I5) | Test | #48 (V) | — | — | **VERIFIED** | — |
| EVD-01 | Run stamp with per-producer scope | Inspection | — | — | 3/3 files; CI step found | **PARTIAL** | pending: WM-2 A6 (open) |
| EVD-02 | Promotion only from a clean run | Test | — | — | 2/2 files | **VERIFIED** | — |
| EVD-03 | Pre-registration before any run, amendments dated | Inspection | #44 (V), #45 (V), #46 (V), #47 (V), #48 (V), #33 (V), #38 (V) | — | 2/2 files | **VERIFIED** | — |
| EVD-04 | Generated documents regenerated and checked | Inspection | — | — | 4/4 files; CI step found | **VERIFIED** | — |
| EVD-05 | Every guard shown to fire | Demonstration | — | — | 2/3 files; CI step MISSING | **OPEN** | missing file: docs/tdp/probe_tdp_checks.sh; CI step not found: probe_tdp_checks.sh |
| EVD-06 | Full suite with no skips | Test | — | — | 2/2 files; CI step found | **VERIFIED** | — |

## 2. Reverse index: register row → requirements

| Row | Status | Requirements |
|---|---|---|
| #4 | V | STD-01 |
| #6 | V | PRF-02 |
| #21 | V | SEC-02, RTV-02 |
| #23 | V | RTV-04 |
| #24 | V | STD-02 |
| #25 | V | SYS-01, SYS-03, PRF-01, PRF-02 |
| #26 | V | PRF-04 |
| #27 | V | SYS-03, RTV-01 |
| #28 | V | SEC-01, SEC-05, SEC-06 |
| #30 | V | PRF-03, STD-03 |
| #31 | V | PRF-05 |
| #32 | V | SEC-03, SEC-04, RTV-03 |
| #33 | V | STD-03, STD-04, EVD-03 |
| #34 | V | SYS-01, SYS-03, PRF-07 |
| #35 | V | PRF-03 |
| #36 | V | PRF-06 |
| #37 | V | SEC-03, SEC-04, RTV-03 |
| #38 | V | SEC-07, EVD-03 |
| #44 | V | INF-01, EVD-03 |
| #45 | V | SEC-02, INF-02, EVD-03 |
| #46 | V | SEC-03, INF-03, EVD-03 |
| #47 | V | INF-04, EVD-03 |
| #48 | V | INF-05, EVD-03 |
| #49 | V | PRF-05 |
| #50 | V | PRF-07 |
| #51 | V | PRF-05 |
| #52 | V | RTV-03 |

V rows cited by no requirement: #1, #2, #3, #22, #29, #42, #43. A V row no requirement cites is evidence without a stated purpose; TDP-PLAN phase 3 decides whether to add a requirement or leave the row as supporting data.

## 3. Limits carried

| Req | Declared limit |
|---|---|
| SYS-01 | Minimal representative implementations of ERC-4337 and LSP8 (chapter 4 caveats); "excl. n/a" totals are not comparable with full totals (#35). |
| SYS-02 | The checker scans tracked Markdown only; HTML and SVG outputs are held by their generators' --check instead. |
| SYS-03 | No M2 (public testnet) measurement exists on the trunk (N-11). |
| PRF-01 | M1 only (local Hardhat, cancun); operation definitions differ per standard and are declared per row. |
| PRF-02 | H1's update and lifetime halves are not supported (#35); the split verdict is the one to report. |
| PRF-03 | Run of record 2026-10-09T02-09-36Z_7a9a996; the harness flag that marks measured-code dirtiness is inert until A6 (D33, N-19). |
| PRF-04 | A model over an assumed profile, not a measurement of a fleet. |
| PRF-05 | SSTORE opcodes counted, not net slots; per-identity contract code not counted (#49). |
| PRF-07 | Gas only; who pays and who is trusted are not measured; the ERC-1056 signed digest omits the chain id (D52). |
| PRF-06 | The O(1) on-chain credential check is a design property assigned per adapter, not a measurement; CVIN-Combined is dominated by ERC-4337 on all six criteria (#36). |
| SEC-01 | 11 cells are declared not applicable; the on-chain script accepts any revert, so "43/43" refers to the strict harness only (#28). |
| SEC-02 | A fresh message relayed inside the window to a receiver that never heard it is not detected (#45); ERC-1056 signed operations do not bind the chain id (D52, G3 narrowed). |
| SEC-03 | A message count, not a time; the verifier cache does not expire; the registry is in-process for I3 (#46). |
| SEC-04 | Rows |
| SEC-05 | The signature check is in place; the authority restriction is open (D54); any role-holder may attest any vehicle, and twice (WM-2 C2 pending). |
| SEC-06 | The cv2x testbed derives a vehicle identity from an unsalted VIN hash (D64, open); the matrix row is structural, not a measurement of linkability. |
| SEC-07 | Chain-layer linkability only; radio, timing and position linkability are out of scope (SC-02). |
| STD-01 | Self-scored and structural; the DID Core checks test a synthesised document (C5 gap; WM-2 C1 pending). |
| STD-02 | The denominator is 336 generated tests, not 441; DID-URL dereferencing is not run. |
| STD-03 | 2 of 8 VID I MUSTs met; the profile is "MOBI-VID-inspired, checked against the public texts" (SC-14a). |
| STD-04 | Writes PASS (at least 10x); "equal once cached" FAIL (ratio set by the baseline's serialisation); the baseline is a lower bound. |
| RTV-01 | M0, mock mobility, one host; the pre-merge measurement is scheduled for a trunk re-run (A3b). |
| RTV-02 | The ERC-1056 column is the cv2x registry, not EthereumDIDRegistry (K-5); the PKI baseline is in-process, a lower bound on deployed PKI. |
| RTV-03 | The knee is the most host-sensitive figure; no finite k reached P*(0.5)=100 on |
| RTV-04 | Bytes only; no channel model, so no airtime or loss figure follows from it. |
| INF-01 | The ratio moved outside its band on verifier v3 and the cause is not isolated (different host builds); not falsified. |
| INF-02 | Not covered - a fresh message relayed to a receiver that never saw it within the 1 s window. |
| INF-03 | In-process registry; message count, not time; no cache expiry. |
| INF-04 | Per-credential issuance costs no gas in this design and is not measured. |
| INF-05 | The harness does not chain the SPaT to the controller update; queuing, network and tail are excluded. |
| EVD-01 | The metrics harness switches to the shared helper at A6; until then its own flag is inert (D33). |
| EVD-02 | A run at an earlier commit cannot pass the promote step and is copied with a manifest as a declared deviation (report 19). |
| EVD-03 | Amendments A1-A3 were post hoc and are marked so. |
| EVD-04 | The contribution record depends on git history and is regenerated at each pass's close, not checked in CI. |
| EVD-05 | A probe proves the guard can trip, not that it trips on every fault class. |
| EVD-06 | Three MOBI demo steps hash block.timestamp and are declared timestamp-dependent (B1). |
