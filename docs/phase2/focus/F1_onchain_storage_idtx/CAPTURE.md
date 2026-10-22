# F1 Capture — On-Chain Storage and Identity-Dependent Transactions in Phase 1

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-14 (Phase 2, focus F1, capture; research agent draft, verified by the orchestrator)
**Binds:** docs/phase2/README.md

Scope. This file captures what Phase 1 already contains about two linked questions: where identity data is
stored (contract storage, event log, calldata, hashed or encrypted on chain, or off chain) and what that
placement costs; and the **identity-dependent transaction (IDTx; also IDDTx / IDBTx)**, an automated process
or next transaction whose execution depends on a value of an identity referenced on chain. It adds no
measurement. Every number is copied from a committed file or a claim-register row (`#n` =
`docs/MEASUREMENT_CONDITIONS.md`). Derived statements say so.

## What Phase 1 already shows

1. Storage placement is a per-adapter realisation, not a property of the standard alone (#34 note; framework §2.1).
2. The event-only design is cheapest to write: ERC-1056 U3 costs 35,024 gas with 1 SSTORE and 0 zero→nonzero writes; ERC-735 U3 costs 318,054 gas with 13 / 12 (`crud_gas.csv:6`, `crud_storage.csv:6`).
3. Over the 17-event lifecycle ERC-1056 is cheapest (1,050,809 gas, 8 zero→nonzero SSTOREs); ERC-735 is dearest (5,797,549 excl. 3 n/a, 149) (#35).
4. The saving moves to the read side: ERC-1056 resolution grows with history to 112 RPC calls / 87,033 B at h = 50, while ERC-1155 stays at 3 / 908 B (`scale.csv:22`; #31).
5. Contracts cannot read event logs. So an in-contract IDTx can depend only on stored state; the analysis assigns "O(1) on-chain credential check" to every substrate except the two ERC-1056 columns (`1_blockchain-identity/analysis/analysis.js:85`).
6. IDTx instances already exist in Phase 1 in three continuation forms: same-transaction `require` gates, read-then-send next transactions, and V2X message acceptance after a chain read.
7. The off-chain IDTx path is where the defects sit: D51 (clock skew accepts a revoked key), staleness ≤ k − 1 messages (#32, #37, #46), D52/D53 (signed-operation gates), D54 (role-only attestation gate).
8. VIN privacy is the only encrypted on-chain datum (MOBI VID: salted SHA-256 plus AES-256-GCM). The testbed derives the vehicle identity from an unsalted SHA-256 of the VIN, which this capture flags as unreviewed.
9. Phase 1 does not measure state growth, cross-transaction TOCTOU, keeper cost, or any computation over encrypted on-chain values (§6).

## 1. Where each standard puts each data item

Legend. **S** contract storage (SSTORE). **E** event log only (the value travels in calldata and is emitted;
storage holds at most a pointer). **C** calldata only. **H** hashed on chain. **X** encrypted on chain.
**O** off chain. **n/a** no primitive. "+E" means the stored item is also emitted.

### 1.1 Harness substrates (the ten columns of #34 / #35)

| Standard (adapter) | Identity record | Owner / controller | Attributes (VID-I) | Delegates / keys | Claims / credential status | Lifecycle events (harness) | VIN |
|---|---|---|---|---|---|---|---|
| ERC-1056 pure (`erc1056.adapter.js:10-14`) | implicit: the address is the DID; no registry write | S `owners`, only on change (`EthereumDIDRegistry.sol:71,105-111,136-142`) +E | **E** `DIDAttributeChanged`; S holds only the `changed` block pointer (`:314-323`) | S validity per (identity, type, delegate) (`:80-81,190-205`) +E | E: status attribute keyed by credential hash on the issuer DID (`erc1056.adapter.js:199-209`) | E, as attributes (`scenarios/lifecycle.js:19-21`) | S plaintext `didToVIN` + S `keccak256(VIN)` index (`CVINVehicleDIDRegistry.sol:25-28,170-178`); E `VehicleDIDCreated` carries the VIN (`:187`) |
| ERC-1056 wrapper (`erc1056w.adapter.js:7-18`) | as pure; DID control handed to the wrapper | S `vehicleOwners` (`CVINVehicleDIDRegistry.sol:40,389-396`) | E via `setVehicleAttributes` / `setServiceEndpoint` (`:218-245`) | S (registry) | E (inherited) | E | as pure |
| ERC-721 (`erc721.adapter.js:4-8`) | S token + metadata struct | S owner + S `transferHistory` append (`CVINVehicleNFT.sol:63,168-186`) | S `VehicleMetadata` struct (`:42-53`); post-mint S `serviceRecords` append (`:66,197-203`) | S one approval slot (`erc721.adapter.js:90-92`) | S append-only strings `vc:active:` / `vc:revoked:` (`:129-136`) | S service-record append | S plaintext three times: `vinToTokenId`, `tokenIdToVIN`, `metadata.vin` (`CVINVehicleNFT.sol:36-39,134-147`) +E |
| ERC-725 (`erc725.adapter.js:7-11`) | per-identity contract (code deposit) + S `_owner` | S | **H**: key = `keccak256("attr:name:value")` stored as a key struct + list (`CVIN_DID_ERC725.sol:22-24,59-64`; `erc725.adapter.js:88-91`) | S key, purpose ACTION (`:84-87`) | S key, purpose STATUS, on the issuer's contract (`:125-129`) | S, as hashed keys | **H** `keccak256("vin:"+VIN)`, unsalted (`:43`); no on-chain VIN index (`:19`) |
| ERC-725xy (`erc725xy.adapter.js:4-11`) | per-identity contract + S owner | S | S plaintext ERC-725Y store (`CVINVehicleERC725XY.sol:79,159-181`) +E | n/a | S on the issuer's account (`erc725xy.adapter.js:114-118`) | S | S plaintext `cvin:vin` (`:51`) |
| ERC-735 (`erc735.adapter.js:8-20`) | per-identity contract + S `vin`, `vinHash`, `owner` (`CVINVehicleClaimHolder.sol:154-160`) | S | S self-issued claims: full struct with signature, data, uri, plus topic index (`:162-175,252-283`) +E twice (`ClaimRequested`, `ClaimAdded`) | n/a | S issuer-signed claim; S issuer registry; S sticky `revokedClaims` (`:178-185`) | S | S plaintext `string public vin` (`:154`) |
| ERC-1155 (`erc1155.adapter.js:7-23`) | S BIRTH_CERT balance; vehicle = address | the address itself; transfer re-binds tokens and VIN | **O** (per-type metadata URI; C2 = C1) (`:11-13,67-69`) | n/a | S token balance per type + S held-type bitmap (`CVINVehicleCredential1155.sol:73,121-135`) | S badge balance; payload not stored (`erc1155.adapter.js:117-121`) | S plaintext `vehicleVIN` + S `keccak256` index (`CVINVehicleCredential1155.sol:60-63,104-108`) +E |
| LSP8 (`lsp8.adapter.js:4-15`) | S token record; tokenId = `keccak256(VIN)` (`CVINVehicleLSP8.sol:72-78,182`) | S | S per-token key/value (`:88,297-307`) +E twice | n/a | S per-token data written by the single authority (`lsp8.adapter.js:111-118`) | S | S plaintext `DATA_KEY_VIN` + unsalted hash as tokenId (`CVINVehicleLSP8.sol:182-193`) +E |
| ERC-4337 (`erc4337.adapter.js:7-20`) | per-account contract + S owner, entry point, guardian | S | S plaintext `_attributes` (`CVINVehicleAccount.sol:81,90,239-242`) +E | S single guardian slot (`:86-87`) | S on the issuer's account (`erc4337.adapter.js:149-158`) | S | S plaintext `cvin:vin` (`:65`) |
| CVIN-Combined (`cvin.adapter.js:8-24`) | implicit address; C1 stores a VIN attestation claim | S `_owners` +E | **E** (only the `changed` pointer is stored) (`CVINCombinedIdentity.sol:218-233`) | S +E (`:67,185-196`) | **S** full claim struct, verified by `ecrecover` at add time (`:254-298`) +E | E, as attributes | S plaintext, inside the VIN-claim data (`cvin.adapter.js:58-62`) +E |

### 1.2 Application profile, testbed registry, VC layer and baseline

| System | Identity record | Owner | Attributes | Keys | Credentials | Lifecycle events | VIN |
|---|---|---|---|---|---|---|---|
| MOBI VID V2 (`MOBIVIDRegistryV2.sol`, extends `MOBIVIDRegistry.sol`, extends `ERC1056Registry.sol`) | S `VehicleBirth` struct: vinHash, encryptedVIN, birthCertHash, manufacturer, firstOwner (`MOBIVIDRegistry.sol:32-41,252-261`) | S `owners` + S `ownershipHistory` with odometer and authority (`:82,410-445`) | E: birth attributes JSON (make, model, year) as an ERC-1056 attribute (`:285-293`; `mobi_vid_provider.py:388-393`) | E vehicle key attribute (`MOBIVIDRegistry.sol:351-372`) | **H** `credentialHash` in the stored event; the VC is off chain (`MOBIVIDRegistryV2.sol:70-81`) | **S** full event struct + id list + counters (`:100-112,276-298`); S attestations incl. signature (`:87-92,365-373`) | **H** salted SHA-256 + **X** AES-256-GCM ciphertext, both S (`mobi_vid_provider.py:241-263,284-300`) |
| cv2x `ERC1056Registry` (vehicle profile, K-5) | as ERC-1056 | S | E | S | O (VCs) | E | not stored by this contract |
| cv2x `ERC1056Registry`, revocation | S whole-identity `revoked` + `revokedAt` (`ERC1056Registry.sol:59-65,264-275`) | | | | | | |
| W3C VC layer (`2_w3c-ssi-layer/verifiable-credentials`) | n/a | n/a | O (credential subject; SD-JWT-style digests) | O (key taken from the DID address by default) | **O** JSON credentials; **O** status registry, in memory or JSON file (`vc_issuer.py:20-21,108-114`) | n/a | O |
| Centralized baseline (`centralized_vehicle_registry.py:15-18`) | O in-process dict | O | O | O (PKI) | O | O | O plaintext, uniqueness by plaintext lookup (`:229-231`) |

Observations (from the tables, not measured).
- Eight of the ten harness realisations put a plaintext VIN in contract storage; ERC-725 stores an unsalted hash. `SIDE_PAPERS.md:40` (SP-3) says "4 of the compared standards leak plaintext VINs on-chain"; which four it counts is unverified against this matrix.
- In MOBI VID the VIN is hashed and encrypted, but the testbed derives the vehicle identity address as the first 20 bytes of an **unsalted** SHA-256 of the VIN (`cv2x-testbed/identity/mobi_vid_provider.py:360,576-584`). Anyone holding a candidate VIN can therefore compute the identity. No defect row covers this (unverified whether it was reviewed).
- The salt is random per registration (`mobi_vid_provider.py:252-253`). The on-chain `vinHash` uniqueness check (`MOBIVIDRegistry.sol:242`) therefore cannot catch a second registration of one VIN; duplicates are caught only because the identity is VIN-derived (`vehicleNotRegistered`, `:143-149`).

## 2. What on-chain storage costs, measured

Source: metrics harness, run of record `2026-10-09T02-09-36Z_7a9a996` (`1_blockchain-identity/results/metrics/latest/meta.json`,
dirty false; M1-H, Hardhat 2.28.6, solc 0.8.24, cancun). Register rows #34 (per-op gas), #35 (lifecycle), #36 (derived
frontier); context #25 (nine-standard benchmark), #26 (15-year lifetime, a different definition; never mixed with #30/#35).

### 2.1 Column definitions (verified in code)

| Column | Definition | Source |
|---|---|---|
| `crud_storage` cell `a / b` | `a` = number of SSTORE opcodes executed in the op's transactions (rewrites and clears included); `b` = SSTOREs whose trace `gasCost >= 20000`, i.e. zero→nonzero (SSTORE_SET) | `benchmarks/lib/MetricsCollector.js:94-104`; `benchmarks/report.js:62` |
| `crud_logbytes` | Σ over logs of 32 × topics + data bytes | `MetricsCollector.js:23-29`; `report.js:63` |
| `crud_calldata` | bytes of `tx.data` (deploy init code included) | `MetricsCollector.js:9-21`; `report.js:64` |
| `crud_gas` | receipt `gasUsed`, summed over the op's transactions | `MetricsCollector.js:128-133` |
| `lifecycle_totals` | lifetime tx count / log bytes / zero→nonzero SSTOREs over the 17 events | `report.js:104-106` |

Two caveats follow from the definitions. Counts are opcodes, not distinct or net slots (#30: "writes, not net state").
Per-identity contract code (ERC-725, ERC-735, ERC-725xy, ERC-4337) is state growth that no SSTORE counter sees; its
deploy gas is reported separately (`lifecycle_gas.csv:21`: 519,384 / 1,757,881 / 1,680,804 / 759,076).

### 2.2 Per operation (gas; SSTOREs total / zero→nonzero; log bytes; calldata bytes)

Files: `results/metrics/latest/tables/crud_gas.csv`, `crud_storage.csv`, `crud_logbytes.csv`, `crud_calldata.csv`;
rows C1 = line 2, C2 = line 3, U3 = line 6.

| Standard | C1 gas | C1 SST | C1 log | C1 cd | C2 gas | C2 SST | C2 log | C2 cd | U3 gas | U3 SST | U3 log | U3 cd |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ERC-1056 | 76,830 | 2 / 2 | 224 | 516 | 367,000 | 10 / 3 | 2,272 | 2,244 | 35,024 | 1 / 0 | 288 | 228 |
| ERC-1056 (wrapper) | 145,684 | 4 / 4 | 352 | 584 | 234,631 | 12 / 4 | 2,400 | 1,164 | 44,677 | 1 / 0 | 288 | 228 |
| ERC-721 | 402,567 | 24 / 15 | 416 | 420 | 570,797 | 27 / 23 | 416 | 612 | 120,061 | 4 / 4 | 224 | 164 |
| ERC-725 | 656,480 | 6 / 6 | 224 | 2,226 | 1,496,440 | 41 / 34 | 1,120 | 2,926 | 119,996 | 5 / 4 | 128 | 100 |
| ERC-735 | 1,757,881 | 3 / 3 | 288 | 8,402 | 2,558,484 | 35 / 35 | 2,560 | 9,498 | 318,054 | 13 / 12 | 1,024 | 452 |
| ERC-1155 | 107,729 | 3 / 3 | 544 | 132 | 107,729 | 3 / 3 | 544 | 132 | 80,131 | 2 / 2 | 352 | 100 |
| ERC-725xy | 1,730,753 | 2 / 2 | 256 | 7,817 | 1,963,543 | 11 / 11 | 1,376 | 8,841 | 95,334 | 3 / 3 | 192 | 164 |
| LSP8 | 135,544 | 6 / 5 | 800 | 132 | 373,187 | 13 / 11 | 3,264 | 1,448 | 100,574 | 3 / 3 | 416 | 196 |
| ERC-4337 | 808,431 | 2 / 2 | 288 | 3,749 | 1,153,124 | 9 / 9 | 1,408 | 4,673 | 94,651 | 3 / 3 | 192 | 164 |
| CVIN-Combined | 271,402 | 11 / 10 | 704 | 452 | 1,015,730 | 42 / 41 | 2,016 | 1,512 | 51,742 | 1 / 1 | 288 | 228 |

Reading notes.
- ERC-1056 U3 writes one slot that is already nonzero (the `changed` pointer); the attribute exists only in calldata and the log. This is the event-only design in one row.
- ERC-1056 C2 (10 / 3) is the wrapper's VIN mapping (2) plus eight `setAttribute` calls that rewrite `changed` (`erc1056.adapter.js:60-73`).
- The large C1 values of ERC-735, ERC-725xy, ERC-4337 and ERC-725 come with only 2 to 6 SSTOREs: they are contract deployments, so their cost is code, not slots.
- ERC-1155 C2 equals C1 because the attributes are not stored at all (O in §1).
- CVIN-Combined C1 writes 11 / 10 slots for one VIN claim: the claim struct with signature and data is stored, not emitted only.

### 2.3 The 17-event lifecycle

Files: `lifecycle_gas.csv:19` (lifetime total), `lifecycle_totals.csv:2-4`. Register #35 (all ten columns), #30 (three columns).

| Standard | Lifetime gas | Transactions | Log bytes | Zero→nonzero SSTOREs |
|---|---:|---:|---:|---:|
| ERC-1056 | 1,050,809 | 26 | 6,464 | 8 |
| ERC-1056 (wrapper) | 1,025,469 | 20 | 6,592 | 9 |
| ERC-1155 | 1,261,575 (excl. 2 n/a) | 18 | 6,944 | 21 |
| LSP8 | 1,508,413 (excl. 3 n/a) | 15 | 8,288 | 42 |
| ERC-4337 | 2,221,290 | 25 | 3,968 | 37 |
| CVIN-Combined | 2,559,537 | 19 | 7,648 | 81 |
| ERC-721 | 2,706,685 | 17 | 4,288 | 92 |
| ERC-725xy | 2,956,507 (excl. 2 n/a) | 16 | 3,744 | 38 |
| ERC-725 | 3,155,103 | 26 | 3,072 | 83 |
| ERC-735 | 5,797,549 (excl. 3 n/a) | 19 | 12,960 | 149 |

- The two event-only columns have the fewest zero→nonzero writes (8, 9) and the lowest lifetime gas (#35).
- Log bytes do not track storage: ERC-735 both stores and double-emits each claim, so it is highest on both axes.
- The hybrid's extra cost is claim storage: register #35 cites event 3 at 294,157 (CVIN-Combined) vs 33,918 (ERC-1056) (`lifecycle_gas.csv:4`).
- "excl. k n/a" totals omit events whose primitive is absent and are not comparable with full totals (#35).
- Write cost is flat in history: ERC-1056 U3 is 35,028 gas at h = 1, 10 and 50 (`scale.csv:14,17,20`; #31).

## 3. Event-only versus state storage: the read side

Contracts cannot read logs. An off-chain resolver must replay them. The harness measures that replay.

### 3.1 Document resolution (R3) against history h

Files: `scale.csv:16,19,22` (RPC / bytes, deterministic), `scale_latency.csv:5-7` (median / p95 ms, n = 10, in-process).

| Standard | h = 1 RPC / B | h = 10 RPC / B | h = 50 RPC / B | h = 50 median / p95 ms | Resolution method |
|---|---|---|---|---|---|
| ERC-1056 | 14 / 10,005 | 32 / 24,153 | 112 / 87,033 | 103.177 / 134.283 | `changed` linked list + one `getLogs` per block (`erc1056.adapter.js:88-136`) |
| ERC-1056 (wrapper) | 6 / 9,404 | 15 / 18,203 | 55 / 57,323 | 37.601 / 46.428 | same walk |
| CVIN-Combined | 9 / 8,962 | 27 / 23,102 | 107 / 85,978 | 83.872 / 102.616 | walk + two claim log queries (`cvin.adapter.js:79-137`) |
| ERC-725 | 12 / 2,800 | 21 / 5,140 | 61 / 15,540 | 56.532 / 72.51 | one `getKey` call per key (`erc725.adapter.js:62-77`) |
| ERC-4337 | 12 / 2,288 | 21 / 5,204 | 61 / 18,164 | 30.12 / 40.1 | one `getAttribute` per key |
| ERC-735 | 3 / 13,774 | 3 / 44,398 | 3 / 180,558 | 47.252 / 58.315 | one full-range `getLogs` (`erc735.adapter.js:80-107`) |
| ERC-721 | 7 / 3,164 | 7 / 8,348 | 7 / 31,388 | 21.869 / 54.697 | state views returning growing arrays |
| ERC-725xy | 2 / 2,312 | 2 / 5,192 | 2 / 17,992 | 31.04 / 51.289 | `getDataBatch` |
| LSP8 | 3 / 2,380 | 3 / 5,260 | 3 / 18,060 | 29.036 / 51.063 | `getDataBatchForTokenIds` |
| ERC-1155 | 3 / 908 | 3 / 908 | 3 / 908 | 3.267 / 4.03 | balances only (no attributes stored) |

- Register #31 states the ERC-1056 h = 50 figure as "112 RPC calls / 87 KB, median ≈65–71 ms". RPC calls and bytes match the committed file. The committed median is 103.177 ms (`scale_latency.csv:7`). The orchestrator should reconcile the latency wording.
- Event-log substrates need O(h) calls; storage substrates need O(1) calls but may return O(h) bytes (ERC-721, ERC-735).
- Under HTTP RPC the gap widens (ERC-1056 R3 at h = 50: 203 / 238 ms vs ERC-1155 5.3 / 6.4 ms), but #39 is **U** (pre-merge contracts).

### 3.2 Point reads after the lifecycle (`resolve.csv:2-5`, L6; RPC / bytes / median / p95 ms)

| Read | ERC-1056 | CVIN-Combined | ERC-735 | ERC-1155 | ERC-725 |
|---|---|---|---|---|---|
| R3 document | 22 / 16,936 / 16.704 / 21.302 | 17 / 20,662 / 13.303 / 17.876 | 3 / 36,525 / 10.417 / 16.037 | 3 / 844 / 3.566 / 4.366 | 17 / 4,100 / 15.963 / 32.217 |
| V6 credential status | 1 / 3,395 / 1.76 / 2.854 (log scan) | 1 / 68 / 0.934 / 1.116 (`hasValidClaim`) | 1 / 68 / 0.889 / 1.425 (`claimExists`) | 1 / 68 / 0.944 / 1.565 | 1 / 196 / 0.975 / 1.15 |
| R4 delegate | 1 / 68 / 1.115 / 1.469 (`validDelegate`, stored) | 1 / 68 / 0.898 / 1.609 | n/a | n/a | 1 / 196 / 0.947 / 1.298 |

- ERC-1056 status checks scan the issuer's full attribute log (`erc1056.adapter.js:210-222`); the response grows with issuance (852 B in `crud_reads.csv:6`, 3,395 B after the lifecycle).
- Delegates are the one ERC-1056 item kept in storage, so R4 is O(1) on both designs.

### 3.3 Verifier-side consequences already measured

| Row | What | Number |
|---|---|---|
| #21 | V2V verify, ERC-1056 uncached (4 RPC) vs PKI | 9.654 / 15.984 ms vs 0.253 / 0.329 ms (median / p95) |
| #32 | freshness-k, full refresh, mean ms | k = 1 11.76; k = 5 2.38; k = 25 0.85; k = ∞ 0.45 |
| #37 | one-call probe refresh (`getIdentityInfo`) vs full refresh | t_chain 2.76 / 2.89 ms vs 14.38 / 10.28 ms (replicates r1 / r2) |
| #33 (re-run file) | MOBI history query, uncached / cached / cached + 2-call probe | 114.222 ms, 39 RPC / 0.011 ms, 0 RPC / 15.403 ms, 6 RPC (`cv2x-testbed/results/lifecycle_parity.md:58-60`) |
| #33 | centralized history query | 0.2627 ms; "equal once cached" FAIL, ratio 0.0414 (`lifecycle_parity.md:41`) |

The read-side implication of not storing state: the verifier must either replay history (cost O(h)) or cache it,
and a cache converts the cost into a staleness window (§5, failure modes).

## 4. Off-chain and hybrid storage in Phase 1

| Mechanism | What is on chain | What is off chain | Evidence | What it shows about on-chain storage |
|---|---|---|---|---|
| W3C VC layer | per adapter: a status anchor (V3) or nothing | credential JSON; status registry (memory or file) | `vc_issuer.py:20-21,108-114`; V3 gas in `crud_gas.csv:13` | Verification is offline by default: the key is the DID's address, so rotation, delegates and deactivation on chain are invisible (`vc_verifier.py:12-20`). Off-chain storage buys speed and loses on-chain freshness |
| MOBI event anchoring | `credentialHash`, `dataHash` in the stored event | the VC and event detail | `MOBIVIDRegistryV2.sol:70-81`; aggregator check `lifecycle_events.py:381-410` | A 32-byte commitment is enough for an off-chain integrity IDTx; the stored event still costs 255,490 gas (`lifecycle_parity.md:56`) |
| VIN hash-and-encrypt (SP-3) | salted SHA-256 + AES-256-GCM ciphertext (identity bound as AAD) | salt, master key (HKDF custody) | `mobi_vid_provider.py:103-110,241-300`; tests `cv2x-testbed/scripts/test_vin_encryption.py:10-17,65-96` | The plaintext never reaches the chain (test at `:65-69`). Nothing on chain can evaluate the VIN; any VIN-dependent step is off chain. Gas of the encrypted field is not isolated (unverified) |
| Centralized baseline | nothing | everything, in process | `centralized_vehicle_registry.py:15-18`; `lifecycle_backends.py:1-27` | #33: writes are ≥10× faster for every operation (PASS ×3, about 1,850–5,930×); cached on-chain history beats the baseline (ratio 0.072, original run) because the baseline's cost is serialisation. The centralized side is an in-process lower bound |
| Pseudonym pool (M5) | 20 delegates per epoch in ERC-1056 storage and log | nothing | #38; `4_comparison-framework/results/pseudonym_pool.md:39,58` | 1,113,456 gas first epoch, 1,096,368 after; one `eth_getLogs` links 60/60 pseudonyms; each epoch leaves 20 slots never cleared. On-chain key storage gives key rotation, not unlinkability |
| ERC-1155 attributes | none | metadata URI per credential type | `erc1155.adapter.js:11-13` | The cheapest storage substrate on reads (§3) partly because it stores no VID-I attributes (#35 note) |

## 5. IDTx instances already present in Phase 1

Definition used here. An IDTx is a step whose execution depends on an identity value read from chain.
"Continuation" is what the read gates: **same tx** (a `require` in the contract; failure reverts), **next tx**
(an off-chain read whose result decides or shapes a later transaction), or **accept** (a V2X or verifier decision).

### 5.1 In-contract (same transaction)

| # | Where | Identity value read | Encoding | Continuation | Failure modes | Gas or latency measured |
|---|---|---|---|---|---|---|
| T1 | ERC-1056 `onlyOwner` on every write (`EthereumDIDRegistry.sol:90-96`) | `identityOwner(identity)` (default: self) | plaintext address | same tx | none listed for the unsigned path | gate cost not isolated; U3 35,024 (#34) |
| T2 | ERC-1056 `*Signed` writes (`:153-178,328-358`) | `ecrecover` signer == `identityOwner` | plaintext | same tx (relayed) | **D52** digest omits chain id (cross-chain replay); **D53** for identity 0x0, `ecrecover` = 0 = `identityOwner(0)` passes (`docs/DEFECT_LOG.md:154-155`) | U5 62,646 (`crud_gas.csv:8`) |
| T3 | ERC-1056 `validDelegate` (`:120-127`) | stored delegate validity vs `block.timestamp` | plaintext | view; any contract could gate on it | chain time only (no skew in-contract) | R4 1 / 68 B / 0.682 ms (`crud_reads.csv:5`) |
| T4 | Wrapper `onlyVehicleOwner`, `setVehicleAttributes` (`CVINVehicleDIDRegistry.sol:115-121,228-233`) | `vehicleOwnerOf`, `identityOwner == wrapper`, VIN registered | plaintext | same tx | K-1 reverted on every call before review 02 (`:204` comment) | not isolated |
| T5 | MOBI `registerVehicleBirth` (`MOBIVIDRegistry.sol:237-250`) | `vehicleBirths.exists`, `vinHashToIdentity[vinHash]`, `changed == 0` (K-4) | **hashed** VIN; plaintext pointer | same tx | salted hash cannot catch a duplicate VIN (§1.2 observation) | birth 398,298 gas (`lifecycle_parity.md:55`) |
| T6 | MOBI `anchorVehicleKey` (`:351-372`) | owner, or registering manufacturer with no ownership history | plaintext | same tx | D11b (two transactions per birth) | ≈69.7 k more per birth (#41 note) |
| T7 | MOBI `recordLifecycleEvent` (`MOBIVIDRegistryV2.sol:241-273`) | vehicle registered, not revoked, issuer role; OWNER role must be current owner (K-15) | plaintext | same tx | odometer not checked on chain (no monotonic `require` in `:241-310`) | 255,490 gas; the owner check +223 (#33 re-run) |
| T8 | MOBI `attestEvent` (`:335-381`) | event exists; attester role ≠ NONE; signature recovers to sender | plaintext | same tx | **D54**: any role-holder attests any vehicle, twice (`DEFECT_LOG.md:156`) | 169,361 execution gas (#28) |
| T9 | MOBI `transferVehicleOwnership` (`MOBIVIDRegistry.sol:410-421`) | registered, owner, not revoked | plaintext | same tx | none listed | 182,144 gas (`lifecycle_parity.md:57`) |
| T10 | ERC-735 `addClaim` (`CVINVehicleClaimHolder.sol:225-249`) | issuer signature; issuer authorised for topic (D25a); not in `revokedClaims` (K-2); VIN attestation must match stored VIN | plaintext VIN; hashed revocation key | same tx | none open | U3 318,054; V3 345,920 (`crud_gas.csv:6,13`) |
| T11 | CVIN-Combined `addClaim` / `hasValidClaim` (`CVINCombinedIdentity.sol:254-298,395-407`) | owner; issuer signature; sticky revocation | plaintext | same tx; view is O(1) for other contracts | K-11 empty slot was valid before review 02 (`:394` comment) | V3 294,195 (`crud_gas.csv:13`); V6 1 / 68 B (`resolve.csv:5`) |
| T12 | ERC-4337 `handleOp` → `validateUserOp` (`CVINMinimalEntryPoint.sol:69-91`; `CVINVehicleAccount.sol:136-168`) | nonce; recovered signer == stored `owner` | plaintext | same tx | none listed | U5 141,767 = U3 + 47,116 (#34); +46,830 in #25 |
| T13 | ERC-721 transfer / approve (OpenZeppelin) and `addServiceRecord` exists check (`CVINVehicleNFT.sol:197-203`) | token owner / approval; token exists | plaintext | same tx | none listed | U4 182,374 (`crud_gas.csv:7`) |
| T14 | ERC-1155 `issueCredential` (`CVINVehicleCredential1155.sol:121-128`) | BIRTH_CERT balance > 0 | plaintext | same tx | none listed | V3 80,131 |
| T15 | LSP8 `setDataForTokenId`, `transfer` (`CVINVehicleLSP8.sol:244-257,297-307`) | token exists; token owner | plaintext | same tx | none listed | U3 100,574 |
| T16 | ERC-725 / ERC-725xy owner gates (`CVIN_DID_ERC725.sol:60,67`; `CVINVehicleERC725XY.sol:102`) | `_owner` | plaintext | same tx | none listed | U3 119,996 / 95,334 |

No in-contract IDTx in Phase 1 reads an **encrypted** value. The only hashed dependencies are T5 (VIN hash) and the
revocation keys of T10 / T11. ERC-1056 attributes cannot be an in-contract dependency at all (`analysis.js:85`).

### 5.2 Off chain (next transaction or message acceptance)

| # | Where | Identity value read | Encoding | Continuation | Failure modes | Measured |
|---|---|---|---|---|---|---|
| T17 | ERC-1056 meta-tx client (`erc1056.adapter.js:158-176`) | `identityOwner`, `nonce` | plaintext | next tx (signed with the read nonce) | read-to-send gap; a change in between makes the relayed tx revert (fails closed; not measured) | U5 62,646 |
| T18 | ERC-4337 client (`erc4337.adapter.js:129-142`) | `entryPoint.nonces(sender)` | plaintext | next tx | as T17 | U5 141,767 |
| T19 | V2V verify, `ERC1056Provider.verify_message` (`cv2x-testbed/identity/erc1056_provider.py:600-716`) | `getIdentityInfo` (owner, `changed`, revoked flag) + key attribute walk | plaintext | accept | **D51**: `_ValidityClock` uses the wall clock beyond 900 s, so a verifier > 15 min behind chain accepts a revoked key (`:44-50,965-984`; `DEFECT_LOG.md:153`); latest state used, not state at generation time (`:622-628`) | #21 9.654 ms uncached |
| T20 | Freshness-k cache in the same provider (`:202-246`) | cached identity state, refreshed every k messages, or probe on `changed` | plaintext | accept | staleness ≤ k − 1 messages for revocation and rotation (#32, #37: 280/280 trials); unbounded at k = ∞ | #32, #37 |
| T21 | `freshness.py` window and replay cache (`cv2x-testbed/identity/freshness.py:155-176`) | none (time and digest) | n/a | accept, before any chain read | not an IDTx itself; it bounds how long a T19 decision can be replayed (1.0 s / 0.1 s, `:61-62`) | inside #21, #27 |
| T22 | RSU / SPaT verify (`cv2x-testbed/sumo/infrastructure_layer.py:144-217`) | VC subject, permitted types, binding; revocation re-check every k (`:170-174`) | plaintext, **off-chain** registry (in process) | accept | staleness ≤ k − 1 (#46); the dependency is not on chain, so it is an IDTx only in the VC sense | #44 warm 0.182 ms, cold 0.477 ms |
| T23 | `VehicleHistoryAggregator` (`2_w3c-ssi-layer/mobi-vid/lifecycle_events.py:302-445`) | on-chain `credentialHash`, event issuer, attestations, odometer history | **hashed** commitment (`keccak256(VC)`) | report (flags; does not gate a tx) | odometer rollback is flagged after the fact, not prevented (`:431-444`); tests added for D55 (`tests/test_aggregator_checks.py:1-5`) | not measured |
| T24 | History cache with probe (`cv2x-testbed/identity/lifecycle_backends.py:244-252`) | `vehicleEventCount`, `getOwnershipHistoryCount` | plaintext | read (re-read if changed) | a change that keeps both counts equal is missed (inferred from the code, not tested) | 15.403 ms, 6 RPC (`lifecycle_parity.md:60`) |
| T25 | Linkability query (M5) | `DIDDelegateChanged` logs by identity topic | plaintext | analysis | the dependency is the privacy leak | #38 60/60 |

## 6. Gaps: what Phase 1 does not measure

| Gap | Why it matters for F1 | Nearest Phase 1 evidence |
|---|---|---|
| State growth and storage rent | SSTORE counts are opcode counts, not net slots; per-identity contract code is not counted; no fleet-scale state size | §2.1 caveats; #38 "20 slots never cleared"; parked as B1-10 (`docs/phase2/BRAINSTORM_01.md:32,53`) |
| Log retention | event-only designs assume full history is served forever; no history-expiry or archive-node cost is considered (no Phase 1 document found that addresses it) | #31, #39 (U) |
| Encrypted on-chain data | no contract evaluates an encrypted or committed identity value; no proof (ZK, Merkle) checked in-contract; gas of the encrypted VIN field not isolated | T5; `test_vin_encryption.py` is chain-free |
| VIN-derived identity | the testbed identity is an unsalted VIN hash; linkability against a VIN guess is not measured | `mobi_vid_provider.py:576-584` |
| Cross-transaction TOCTOU | no experiment opens a gap between an identity read and the dependent tx (owner change, revocation, reorg); automine on one node hides mempool ordering and reorgs | T17, T18, T19 (`erc1056_provider.py:622-628`) |
| Cross-contract IDTx gas | no contract calls `validDelegate` / `hasValidClaim` from another contract; "O(1) on-chain credential check" is a design property, not a measurement (`analysis.js:119`) | #36 |
| Cost of the gate itself | isolated only for the K-15 owner check (+223, #33) and `attestEvent` (#28) | §5.1 |
| Keeper / automation cost | no automated process submits transactions on an identity condition; no keeper, oracle or scheduler cost | none |
| Atomicity of multi-step IDTx | ERC-1155 deactivation and resale, ERC-735 issuer authorisation and MOBI birth + key anchor (D11b) are multi-transaction; partial failure is not measured | `erc1155.adapter.js:127-134`; `erc735.adapter.js:144-149` |
| Public-network conditions | every number is Hardhat local (M1 / M1-H); the HTTP-RPC run #39 is U | `docs/MEASUREMENT_CONDITIONS.md:22-24` |
| Clock and freshness of the off-chain IDTx | D51 is open; #21, #32, #37 carry the assumption "verifier clock within 900 s of chain time" | `DEFECT_LOG.md:153` |

## 7. Notes for the orchestrator (discrepancies found while capturing)

| Item | Register or document says | Committed file says | Action suggested |
|---|---|---|---|
| ERC-1056 R3 latency at h = 50 | #31: "median ≈65–71 ms" | 103.177 ms (`scale_latency.csv:7`, run of record `7a9a996`); RPC 112 and bytes 87,033 agree | reconcile #31 wording (latency only) |
| Plaintext-VIN count | SP-3: "4 of the compared standards" (`SIDE_PAPERS.md:40`) | eight of ten harness realisations store a plaintext VIN (§1.1) | state which set SP-3 counts |
| MOBI identity derivation | SP-3 presents MOBI VID as the private pattern | identity = first 20 bytes of unsalted SHA-256(VIN) (`mobi_vid_provider.py:576-584`) | author review; candidate defect row (unverified) |
