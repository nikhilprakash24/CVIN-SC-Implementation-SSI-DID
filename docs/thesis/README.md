# Thesis Chapters

This directory contains the MASc thesis chapters and supporting documentation.

## Structure

```
thesis/
├── 01-introduction.md          # Research problem and objectives
├── 02-literature-review.md     # Survey of SSI and vehicle identity
├── 03-methodology.md           # Research design and approach
├── 04-implementation.md        # System implementation details
├── 05-results.md               # Experimental results
├── 06-discussion.md            # Analysis and interpretation
├── 07-conclusion.md            # Conclusions and future work
└── appendices/                 # Code listings, data tables
```

## Chapter Status

| Chapter | Title | Status | Pages |
|---------|-------|--------|-------|
| 1 | Introduction | 🔄 Draft | 15 |
| 2 | Literature Review | 🔄 Draft | 30 |
| 3 | Methodology | ✅ Complete | 25 |
| 4 | Implementation | ✅ Complete | 40 |
| 5 | Results | 🔄 In Progress | 35 |
| 6 | Discussion | ⏳ Planned | 20 |
| 7 | Conclusion | ⏳ Planned | 10 |

**Total**: ~175 pages (target: 150-200)

## Key Contributions (Chapter 4-5)

### Implementation Contributions
1. **Blockchain Identity Standards, measured under automotive constraints** - identical operation sets, exact gas, latency with N/median/p95 (three standards on this branch, nine after merge — SC-07)
2. **W3C-aligned System** - 89.6% on the internal 67-check list (self-scored; external W3C test-suite result pending, audit F5). "Exceeds industry average" has no source and is withdrawn.
3. **Reproducible V2V Integration** - blockchain identity in the message path, measured against a PKI baseline (not claimed as "first"; see SC-04)
4. **MOBI VID Compliance** - Reference implementation

### Experimental Results (Chapter 5)
1. **Performance Comparison** - Detailed gas costs, latency measurements
2. **Security Analysis** - Threat modeling and attack scenario testing
3. **Usability Study** - 10 complete use case implementations
4. **Scalability Testing** - SUMO simulation with 50 vehicles (configured in `cv2x-testbed/sumo/`; not yet run to a results file — see `docs/MEASUREMENT_CONDITIONS.md` #15)

## Research Questions Addressed

### RQ1: Performance
**Question**: How do different blockchain identity standards compare in transaction cost, latency, and throughput?

**Answer (trunk-measured, condition M1, commit 708302a)**: For the create-equivalent operation, ERC-1056 vehicle-DID creation costs 78,068 gas against 102,804 gas (avg) for an ERC-721 vehicle-NFT mint — a 1.32× saving, not an order of magnitude. Order-of-magnitude gaps arise only against rich-state standards (ERC-725xy, bundle lineage, unverified on trunk). In-process DID resolution (M0, N=30, commit f602fdf) is 0.009 ms median / 0.013 ms p95 cold and 0.002 ms warm (cache hit), for each of `did:ethr`, `did:mobi`, `did:nft` — i.e. resolution is not on the critical path; the hot-path cost is signature verification, which the PKI-vs-ERC-1056 experiment measures. Resolution with a blockchain lookup (M2) has not been measured. See `docs/MEASUREMENT_CONDITIONS.md`.

### RQ2: Security
**Question**: Which architecture provides strongest security guarantees for V2X communication?

**Answer**: Hybrid approach (ERC-1056 + ERC-735 claims) provides optimal balance of security and performance.

### RQ3: W3C Compliance
**Question**: Can blockchain identity achieve W3C SSI compliance while meeting automotive requirements?

**Answer**: Yes. Achieved 89.6% W3C compliance (DID Core: 75%, VC: 100%, SSI: 100%).

### RQ4: Real-Time Feasibility
**Question**: Are blockchain identities viable for real-time safety-critical V2V?

**Answer**: Partial. Suitable for non-critical V2V (BSM broadcasts). Safety-critical applications require hybrid PKI/blockchain approach.

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

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Chapter 1-3 Draft | 2025-12-15 | 🔄 |
| Implementation Complete | 2026-01-31 | ✅ |
| Experimental Results | 2026-03-15 | 🔄 |
| Full Draft | 2026-04-30 | ⏳ |
| Committee Review | 2026-05-15 | ⏳ |
| Final Defense | 2026-06-30 | ⏳ |

## Thesis Metrics (Target)

- **Pages**: 150-200
- **References**: 100+ (currently ~60)
- **Figures**: 30-40
- **Tables**: 20-30
- **Code Files**: 50+ (currently 35)
- **Test Cases**: 200+ (currently 150)
- **Lines of Code**: 15,000+ (currently 12,000)

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
