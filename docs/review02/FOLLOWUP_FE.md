# Follow-up stream F-E: MOBI VID clause reconciliation (plan step M1)

**Input:** `docs/PLAN_MOBI_SUMO.md` Part A (M1), `MOBI_VID_RESEARCH.md`,
`MOBI_VID1_TECHNICAL_SPEC.md`, `MOBI_VID2_SSI_DESIGN.md`, `docs/SCOPE_CHANGES.md`, the
MOBI contracts, the Python layer and their tests. **Base:** `d2e6a58`.
**Output:** `docs/MOBI_VID_CHECKLIST.md`. No code, test or result file was changed.

## 1. Sources
- **VID I v1.0 preview (2019)** was fetched (HTTP 200, 8 pp.). It has **no normative clauses**: only the TOC, the member list, the foreword and the introduction. The full v1.0 text is members-only.
- **VID I v2.0 (MOBI VID0002/TS/2024)** is public in full under Apache 2.0. It has numbered requirements VID-R1…R8 and D1…D5, and the checklist uses it as the normative VID I source. It removed v1.0's system-level requirements (Certificate API and Roles 1–4, DVM).
- **VID II Use Cases and Business Requirements (VID0002/UC/2021 v1.2)** is public in full: UC1 Registration BR1–10 and UC2 Maintenance BR1–6.
- **VID II Reference Implementation (VID0004/RI)**: both public files are previews (glossary only, then "Full access … available to MOBI members").
- **VID II VC schemas**: titles only, in a members-only GitHub repository.
- Nothing was committed from any of these PDFs. URLs, retrieval date and hashes are in checklist §0.

## 2. Result (29 counted clauses; 5 v1.0 sections not assessable)

| Status | VID I v2.0 | VID II UC | Total |
|---|---|---|---|
| Implemented + tested | 2 | 5 | 7 |
| Implemented, untested | 0 | 1 | 1 |
| Partial | 6 | 8 | 14 |
| Not implemented | 3 | 1 | 4 |
| Out of scope | 2 | 1 | 3 |

**VID I MUSTs:** 2 of 8 met. UVI (R6) and Entity Certificate (R8) are absent. The VBC
schema carries 7 of the 15 mandatory fields.

## 3. Findings outside the status table
1. **Bug, untested:** `MOBIVIDRegistry.getVehicleDID` returns `did:ethr:0x7a69:<40 hex>` without the `0x` before the address. The repo's own resolver rejects it as `invalidDid`. The Python `vehicle_did()` is correct, so the two layers disagree for the same vehicle.
2. `did_resolver._resolve_ethr` never reads the chain. For a born vehicle it names the vehicle address as controller, but the on-chain owner is `firstOwner`. `_resolve_mobi` is a placeholder that puts the VIN in the DID, which contradicts the VIN-privacy design.
3. A global `SERVICE_CENTER` or `OWNER` role can write lifecycle events to **any** vehicle without the owner's consent (VID II UC2-BR2).
4. `THEFT_REPORT` and `DECOMMISSION` have no effect on transfers or identity status, although `MOBI_VID2_SSI_DESIGN.md` UC 9 says transfers are blocked after a theft report.
5. Spec-document claims the code does not support:
   - the VIN hash includes the DID;
   - the VIN is encrypted to the owner's public key;
   - IPFS anchoring (the stale comments are at `V1:35` and `V2:76`);
   - a `revokeVehicle()` function;
   - "MOBI VID I requirements checklist 100%".
6. The security matrix says MOBI-VID-V2 "signatureReplay: N/A". This is out of date: `attestEvent` is signed and replay-tested.
7. The Python MOBI test count is **36** (plan and README say 32).

## 4. Proposed claim-register row (for `docs/MEASUREMENT_CONDITIONS.md`)

| # | Claim | Location | Tag | Source on trunk | Status |
|---|---|---|---|---|---|
| next | MOBI VID reconciliation against the public texts: VID I v2.0 (TS/2024) 2/8 MUST met, 13 clauses → I+T 2, Partial 6, Not impl. 3, OOS 2; VID II UC/2021 16 BRs → I+T 5, I-U 1, Partial 8, Not impl. 1, OOS 1; v1.0 (2019) not assessable (members-only) | `docs/MOBI_VID_CHECKLIST.md` | — (static analysis) | checklist; test runs 2026-10-04: Hardhat MOBIVID 24 passing, security MOBI-VID 6 passing, pytest mobi-vid 36 passed | **V** for `d2e6a58` (author's reading, not a MOBI determination) |

## 5. Proposed scope-change entries
The full text is in checklist §7: P-1…P-7, provisionally SC-14…SC-20.
- **Out of scope:** D2/D3 key-management practice; UC1-BR2 government-ID binding.
- **Decisions pending:** UVI and Entity Certificate; the VBC field set; owner-consent and VRA transfer.
- **Deferred:** D1 per-relationship DIDs, linked to SC-02 and M5.
- **Not assessable:** the v1.0 clauses and the VID II RI.

## 6. Recommended wording change (thesis and contract headers)
Replace "MOBI VID compliant" / "meets MOBI VID" with: *"a MOBI-VID-inspired application
profile, checked clause by clause against the public MOBI VID I v2.0 and VID II UC texts
(docs/MOBI_VID_CHECKLIST.md)."*
