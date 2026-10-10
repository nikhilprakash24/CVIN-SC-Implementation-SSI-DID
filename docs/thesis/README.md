# Thesis Chapters

This directory contains the MASc thesis chapters and supporting documentation.

## Structure

```
thesis/
├── chapter1-introduction/      # ✏️ Draft — motivation, RQs, contributions
├── 02-literature-review.md     # Survey of SSI and vehicle identity (planned; needs citations)
├── chapter3-methodology/       # ✏️ Draft — research design & measurement methods
├── chapter4-implementation/    # ✏️ Draft — system architecture & implementation
├── chapter5-results/           # ✏️ Draft from measured artifacts
├── chapter6-discussion/        # ✏️ Draft — interpretation of the results
├── chapter7-conclusion/        # ✏️ Draft — verdicts, contributions, future work
└── appendices/                 # Code listings, data tables
```

## Chapter Status

The implementation is largely complete and Chapter 5 is backed by **measured
data** (all figures traceable to committed artifacts): see the working draft
at [`chapter5-results/`](chapter5-results/). Remaining work is public-testnet
(Sepolia) validation, optional real-SUMO execution, and thesis writing.

| Chapter | Title | Status | Pages (est.) |
|---------|-------|--------|-------|
| 1 | Introduction | ✏️ Draft (`chapter1-introduction/`) | 15 |
| 2 | Literature Review | ⏳ Planned (needs citation set) | 30 |
| 3 | Methodology | ✏️ Draft (`chapter3-methodology/`) | 25 |
| 4 | Implementation | ✏️ Draft (`chapter4-implementation/`) | 40 |
| 5 | Results | ✏️ Draft from measured artifacts (`chapter5-results/`) | 35 |
| 6 | Discussion | ✏️ Draft (`chapter6-discussion/`) | 20 |
| 7 | Conclusion | ✏️ Draft (`chapter7-conclusion/`) | 10 |

**6 of 7 chapters drafted** (all but the Literature Review, which awaits the
citation set). Chapters 3–7 are grounded in the measured artifacts.

**Total**: ~175 pages (target: 150-200; page counts are estimates)

## Key Contributions (Chapter 4-5)

### Implementation Contributions
1. **9 Blockchain Identity Standards + MOBI VID profile** - all implemented, tested (Hardhat suite; current totals in `sandbox/grand/report/GRAND_REPORT.md`), and gas-benchmarked on-chain
2. **W3C Compliant System** - 94.3% (after the 2026-10-03 resolver fixes; 93.2% at the merge) measured compliance (executable checker, CI-gated ≥90%)
3. **Real-time V2V Integration** - blockchain identity verified in the V2V message path with real cryptography (SSI warm verify 0.153 ms)
4. **MOBI VID** - VID I birth certificate + VID II (11 lifecycle event types), on-chain `attestEvent` signature verification, AES-256-GCM VIN encryption
5. **Infrastructure identities (V2I/I2I)** - RSUs, signal controllers and a traffic-management centre as credentialed DIDs; signed SPaT and I2I messages with field binding, replay rejection and revocation re-check (`cv2x-testbed/sumo/infrastructure_layer.py`)

### Experimental Results (Chapter 5 — measured; see `chapter5-results/`)
1. **Performance Comparison** - exact gas costs across all 9 standards (N=30, byte-identical, σ=0); ~34× create spread
2. **Security Analysis** - two complementary lenses: 54-scenario revert suite (43/43 applicable cells defended) + threat matrix
3. **Use-Case Validation** - 12/12 lifecycle use cases with real cryptographic verification (forged/replayed credentials fail)
4. **V2V Latency** - N=30 seeded runs, 50 vehicles, 10 Hz BSM; 1.65 M verifications; mobility simulated (no SUMO binary)
5. **Infrastructure messaging** - pre-registered I1–I5 (register #44–#48, §5.4.1): warm SPaT verification 1.096× a warm BSM's; 13 registered checks (10 attacks, 3 warm variants) rejected for the expected reason in 30/30 runs; a revoked RSU honoured for at most k − 1 messages by a cached verifier (a conformance check of the re-check cadence, not a latency)

## Research Questions Addressed

### RQ1: Performance
**Question**: How do different blockchain identity standards compare in transaction cost, latency, and throughput?

**Answer (measured, H1 supported)**: identity-creation gas spans 33.7× across the nine standards (CVIN-Combined 52,216 to ERC-735 1,757,881; ERC-725xy 1,680,816 second; register #25), condition M1 (solc 0.8.24, optimizer 200 + viaIR, evm cancun, OpenZeppelin 5.0.2, Hardhat local, re-executed 2026-10-04 after the defect fixes). ERC-1056's bare `createIdentity` (52,594) is ~10× cheaper than ERC-721's VIN-bound `mintVehicle` (545,101) and ERC-725 (519,384); with the VIN bound on both sides (`createVehicleDID`, 78,068) the ratio is ≈7×. A bare ERC-721 `mint` on the lighter `CVIN_NFT_DID_ERC721` contract costs 102,804 and is *not* the create-identity operation (no VIN binding) — the two figures are reconciled in `docs/MEASUREMENT_CONDITIONS.md` #6/#25. ERC-4337 EntryPoint indirection adds 46,830 gas/op. Gas is deterministic (repeated runs byte-identical; N is a reproducibility check, not a confidence interval).

### RQ2: Security
**Question**: Which architecture provides strongest security guarantees for V2X communication?

**Answer (measured, H5 supported)**: no single standard dominates — standards occupy distinct points on the security/performance frontier. Only ERC-4337 offers genuine on-chain key recovery (with a caveat: the guardian keeps permanent control after a recovery, defect D15, open); ERC-1155 uniquely resists identity theft (soulbound); MOBI VID is the only family that hashes + encrypts the VIN. The 54-scenario revert suite defends 43/43 applicable attack cells.

### RQ3: W3C Compliance
**Question**: Can blockchain identity achieve W3C SSI compliance while meeting automotive requirements?

**Answer (measured, H2 supported)**: Yes — **94.3% (after the 2026-10-03 resolver fixes; 93.2% at the merge)** measured (executable checker): DID Core v1.0 96.7% (14/15), VC Data Model v2.0 93.1% (27/29) — a structural self-score on the internal checker, not conformance (register #4; WM-1 audit U-F4). The two deviations are documented and deliberate (canonical JSON vs URDNA2015; thesis-defined cryptosuite).

### RQ4: Real-Time Feasibility
**Question**: Are blockchain identities viable for real-time safety-critical V2V?

**Answer (measured, H3 supported)**: Yes for the cryptographic path. SSI warm verify is 0.153 ms [0.151, 0.154] (N=30, re-executed 2026-10-04, register #27) against the ~100 ms V2V budget (~650× margin); cold full-credential verify 0.399 ms. Caveat: excludes radio/MAC/network-stack latency; mobility is simulated.

## Writing Guidelines

### Academic Standards
- APA 7th edition citations
- IEEE formatting for technical sections
- Passive voice for methodology
- Active voice for results

### Figures and Tables
- All figures must be camera-ready (300 DPI minimum)
- Tables must be editable (LaTeX or CSV source)
- Captions below figures, above tables
- All data must be traceable to source code

### Code Listings
- Key algorithms in appendices
- Reference GitHub commit SHAs
- Include performance metrics as comments

## Timeline

Dates below are **proposed / TBD** — the earlier target dates have passed and
no revised defense date is fixed in the repository. Implementation and the
measured experimental results are done; remaining work is Sepolia validation,
optional real-SUMO, and thesis writing.

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Implementation complete (9 standards + MOBI VID + testbed) | — | ✅ Done |
| Experimental results (gas, V2V, W3C compliance, security) | — | ✅ Done (measured; `chapter5-results/`) |
| Sepolia public-testnet validation run | TBD | ⏳ Harness exists (`validate_sepolia.js`); not yet executed |
| Chapters 1-2 draft | TBD | 🔄 |
| Full draft | TBD | ⏳ |
| Committee review | TBD | ⏳ |
| Final defense | TBD | ⏳ |

## Thesis Metrics (Target)

- **Pages**: 150-200
- **References**: 100+ (currently ~60)
- **Figures**: 30-40
- **Tables**: 20-30
- **Test Cases**: 200+ — **met**: all automated suites green (Hardhat + VC + MOBI VID + 12/12 use cases; current totals in `sandbox/grand/report/GRAND_REPORT.md`)
- **W3C Compliance**: ≥90% target — **met**: 94.3% (after the 2026-10-03 resolver fixes; 93.2% at the merge) measured

## Committee

- **Supervisor**: [TBD]
- **Committee Member 1**: [TBD]
- **Committee Member 2**: [TBD]
- **External Examiner**: [TBD]

## LaTeX Template

Using UBC ECE thesis template: https://github.com/ubc-ece/ubc-thesis-template

Key packages:
- `algorithm2e` - For algorithms
- `listings` - For code
- `tikz` - For diagrams
- `pgfplots` - For performance graphs
- `biblatex` - For references
