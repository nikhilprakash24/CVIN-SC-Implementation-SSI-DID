# XT-03 — Requirement → substrate decision table

*X-SERIES · EXPLORATORY · CLAUDE-INITIATED, NOT AUTHOR-DIRECTED · not cited until promoted.* This table is **interpretation**, not measurement. Each row reads the measured matrices (`security_matrix.csv`, `analysis_basic_set`, #25/#35) as a choice a system designer faces.

| If the requirement is… | Choose | Because (measured) | Cost of the choice |
|---|---|---|---|
| lowest cost over a vehicle's life | ERC-1056 | cheapest lifetime (#35), 8 new slots | Sybil-exposed: self-registration (matrix) |
| O(1) on-chain claim check by another contract | CVIN-Combined | claims verified at add time; getClaim O(1) | claim adds ≈287k gas each (#25) |
| key recovery after compromise | ERC-4337 | only DEFENDED recovery cell (matrix) | ≈2.2 M lifetime; +46,830 per routed op |
| identity that cannot be stolen by transfer | ERC-1155 (soulbound) | only DEFENDED identity-theft cell | no delegates; attributes off-chain |
| VIN never visible on-chain | MOBI VID profile | only family that hashes and encrypts (matrix privacy) | application profile on top of a substrate |
| agent that can act (execute) | ERC-725xy or ERC-4337 | only substrates with X1 (BASIC_ID_SET §4) | contract per identity; 1.68 M create |
| verifier with no chain access at message time | any, with a cache | 0.153 ms warm (#27) | revocation lag ≤ (k − 1)/10 s (#32) |
