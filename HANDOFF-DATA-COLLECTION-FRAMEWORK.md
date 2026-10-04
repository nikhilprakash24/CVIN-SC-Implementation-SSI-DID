# HANDBACK — Data-Collection & Comparative-Analysis Framework ("CRUD and Beyond")

**Author:** Nikhil Prakash (MASc, UBC ECE) — nikhil.prakash1995@gmail.com
**Date:** 2026-10-04 (wrapper-mode addendum; body from 2026-09-30/10-03) · **Branch:** `claude/clone-cvin-id-scs-011CUyxScetMdSQFkuQUNLTt` (rebased on `084edfd`, the merged trunk)
**Replaces:** the v1 handoff of 2026-09-24 (which quoted un-sourced "~45–50K gas" figures; see `docs/MEASUREMENT_CONDITIONS.md` §D)
**Read next, in order:** `docs/CVIN-DATA-COLLECTION-FRAMEWORK.md` → `docs/MEASUREMENT_CONDITIONS.md` → `1_blockchain-identity/results/metrics/latest/REPORT.md` → `docs/AUDIT_01_ORIGINAL_GOALS.md`

---

## 0. One-paragraph state

The research objective is to show, through a fixed research process, that ERC-1056 is the right SSI substrate for CAVs. This session delivered the process: a written methodology (operation catalogue, scenarios, statistics, falsifiers, threats to validity), a measurement harness that runs the **same 18-operation catalogue on every substrate** through a per-standard adapter, and the **first trunk-traceable run** (`results/metrics/latest`, commit-stamped) for the three substrates that exist on the trunk — ERC-1056, ERC-721, ERC-725. The remaining six substrates plug in by writing one adapter each; the protocol does not change. The numbers already say something the thesis must take on board: ERC-1056 is the cheapest substrate on lifetime cost by **2.6× (vs ERC-721) and 3.0× (vs ERC-725)** (review-02 corrected run; first reported as 2.7×; **2.6× / 3.1× in its best, wrapper-controlled mode — §3.6**), not the ≥10× H1 currently asserts, and its event-log read path is the **most expensive to resolve** (linear in history). Both are defensible thesis results; the hypothesis text needs to follow the data, not the other way round.

---

## 1. What was built this session (all on the branch, all pushed)

| Artefact | Path | Purpose |
|---|---|---|
| Methodology | `docs/CVIN-DATA-COLLECTION-FRAMEWORK.md` | §2 catalogue (C1–C2, R1–R4, U1–U5, D1–D3, V1–V6) with each standard's realisation; §3 conditions; §4 scenarios S1–S6; §6 statistics; §7 rubric axis; §8 hypotheses→measurements→**falsifiers**; §9 PKI/centralised baseline commensurability; §11 threats to validity; §12 scope-change log |
| Conditions of record | `docs/MEASUREMENT_CONDITIONS.md` | the only conditions under which a number may enter a chapter; defines every reported quantity; lists superseded numbers |
| Harness | `1_blockchain-identity/benchmarks/` | `lib/MetricsCollector.js` (gas, intrinsic/execution split, calldata + log bytes, SSTORE/SLOAD/new-slot counts via `debug_traceTransaction`, RPC calls/bytes on reads, hrtime latency), `lib/stats.js` (median/p95, bootstrap CI, Mann–Whitney U), `lib/dataset.js` (seed-42, fixed-width payloads), `lib/exporters.js` (md/csv/tex), `adapters/` (interface + ERC-1056/721/725), `scenarios/` (crud, lifecycle, scale, batch, throughput, resolve), `run.js`, `report.js`, `rubric/did-method-rubric.json` |
| Conformance gate | `1_blockchain-identity/test/benchmarks/adapters.conformance.test.js` | 23 passing / 4 declared-n/a; an adapter enters the study only when green |
| npm scripts | `metrics`, `metrics:quick`, `metrics:report`, `test:conformance` | |
| CI | `.github/workflows/benchmark.yml` | runs the gate + harness, uploads `results/metrics/latest` (Node 22) |
| Results of record | `1_blockchain-identity/results/metrics/latest/` | `meta.json`, `raw.jsonl` (every tx/read), `<scenario>.json`, `tables/*.{md,csv,tex}`, `REPORT.md` |

Existing 47/47 contract tests are untouched; the conformance suite adds to them.

## 2. How to reproduce (5 minutes)

```bash
cd 1_blockchain-identity
npm install
npm run test:conformance          # gate: 23 passing, 4 pending (declared n/a)
npm run metrics                   # ~4 min → results/metrics/latest/REPORT.md
# subsets / quick:
METRICS_SCENARIOS=crud,lifecycle METRICS_ADAPTERS=erc1056 npm run metrics
npm run metrics:quick
```

Gas, bytes, slot counts and RPC counts are exact, and two runs of one commit give byte-identical gas tables. This has been true only since review 02 (H-1, H-3): before it, random wallets and a shared issuer moved some cells between runs. Latencies are in-process client + EVM and reproduce in distribution only.

## 3. Headline results (run of record: the ten-substrate run of §3.7; §3.1–3.6 quote the earlier three- and four-column runs `59405ff` / `bca0899`, whose cells are byte-identical in the current run; full tables in `results/metrics/latest/`)

> **Corrected in review 02** (`docs/REVIEW_02_CODEBASE.md` H-1–H-8, `docs/review02/PASS1_H.md`). The previous run `3b786c2` and the figures this section printed for it are superseded (`MEASUREMENT_CONDITIONS.md` §5.D).

### 3.1 L1 gas per catalogue operation (exact)

| Op | ERC-1056 | ERC-721 | ERC-725 | Reading |
|---|---:|---:|---:|---|
| C1 create identity | **76,808** | 399,844 | 656,480 (incl. per-identity deploy) | 5.2× / 8.5× |
| C2 create + VID-I attributes | **366,978** (9 tx) | 568,074 (1 tx) | 1,496,440 (9 tx) | 1.5× / 4.1× — ERC-1056 pays 8 × 21k base per attribute tx; no batch primitive |
| U1 rotate controller | 51,754 | 179,470 | **28,390** | ERC-725 cheapest: it prepaid with deployment |
| U2 add delegate | 55,143 | **48,314** | 119,852 | ERC-721 `approve` has no expiry — cheaper, weaker |
| U3 set attribute (64 B) | **35,024** | 120,061 | 119,996 | 3.4× |
| U4 transfer vehicle | 51,754 | 182,374 | **28,390** | as U1 |
| U5 meta-tx (relayed) | **62,646** | n/a | n/a | only ERC-1056 has the primitive |
| D1 revoke delegate | 32,868 | **26,174** | 57,200 | |
| D2 revoke attribute | **34,576** | n/a | 57,316 | ERC-721 service records are append-only |
| D3 deactivate | 34,230 | 27,689 | **23,091** | ERC-1056 has no deactivate primitive (attribute workaround) |
| V1 issuer key anchor | **55,143** | 419,990 | 119,852 | ERC-721 needs an issuer token |
| V3 anchor credential status | **33,918** | 142,909 | 119,996 | 4.2× / 3.5× |
| V5 revoke credential | **33,470** | 125,821 | 43,388 | 3.8× / 1.3× (fresh issuer per iteration; the old 214,099 depended on N) |

### 3.2 L2 MOBI VID lifecycle (17 events, one vehicle; event 11 is the delegate add that the rotation retires)

| | ERC-1056 | ERC-721 | ERC-725 |
|---|---:|---:|---:|
| Lifetime gas | **1,050,787** | 2,701,239 | 3,155,103 |
| Transactions | 26 | 17 | 26 |
| Zero→nonzero SSTOREs (writes, not net state) | **8** | 92 | 83 |
| Log bytes | 6,464 | 4,288 | 3,072 |
| Shared deployment (once) | 2,709,021 | 2,721,476 | 519,384 (+519,384 **per identity**) |

### 3.3 L3 scale, L5 throughput, L6 read path

- **Population N (0 → 1 000):** flat for all three on every op (mapping-based storage). H1' holds.
- **History h (1 → 50):** write cost flat; **read cost is the differentiator** — resolving the ERC-1056 DID Document walks the `previousChange` chain: 14 → 32 → **112 RPC calls, ≈65–71 ms median at h = 50**. ERC-721 stays at 7 calls (but returns 31 KB of history); ERC-725 grows with key count (61 calls).
- **Throughput (single node, 200-tx bursts):** 153–192 tx/s for all three over the runs (run of record 163 / 176 / 192). The standard is not the bottleneck at the node level; gas/s (5.3 M vs 22–23 M) is where they differ.
- **L6 after a full lifecycle:** R3 resolve = 22 / 7 / 17 RPC calls, ≈14–16 / 6–8 / 13 ms median for ERC-1056 / 721 / 725 across runs. R4 on the rotated-in delegate answers true / **false** / true: ERC-721's later transfers clear the approval.

### 3.4 What this means for the hypotheses (framework §8)

| Hyp. | Verdict on current data | Action for the thesis text |
|---|---|---|
| H1 "≥ 10× cheaper for create/update" | **Refuted as stated.** Lifetime 2.6× / 3.0×; C1 5.2× / 8.5×; U3 3.4×; ERC-1056 is *not* the minimum on U1/U4/D3 (ERC-725) or U2/D1 (ERC-721). | Restate H1 as "cheapest substrate on lifetime cost and on every CREATE/anchor op, with the fewest zero→nonzero storage writes (8 vs 83–92)"; drop the 10× figure — it holds for no op pair even in wrapper mode (§3.6: lifetime 2.6× / 3.1×, C2 2.4× / 6.4×). |
| H1' flat in N | Supported. | keep |
| H3 real-time | Read-side evidence now exists: on-chain resolution of an ERC-1056 identity with history costs ≈65–71 ms *in-process* — it will not fit 100 ms over a real RPC. Supports the second half of H3 (must pre-resolve). | cite `scale.md` h-axis and `resolve.md` |
| H4 event-log cheapest for VID-II events | Supported on 12/17 events. The exceptions are the k1 add and the rotation (ERC-721), the two ownership transfers (ERC-725) and the deactivation (ERC-725). | keep, with exceptions listed |
| H5 no single dominator | Supported already at n = 3: ERC-1056 dominates on write cost and footprint, ERC-721 dominates on read path, ERC-725 on rotation/transfer. | keep |

### 3.5 Artefacts to be aware of (not bugs, but must be stated)

1. **ERC-1056 is measured in two modes.** `erc1056` is pure did:ethr (owner sends 8 `setAttribute` txs for C2); `erc1056w` is the CVIN wrapper-controlled mode (`changeOwner(did, wrapper)` once, then `setVehicleAttributes` in one tx). Both are honest realisations and both are reported (§3.6). Wrapper mode loses meta-tx (U5) and attribute revocation (D2), and its ownership transfers are **invisible to a plain did:ethr resolver** — `transferVehicleOwnership` changes only the wrapper's `vehicleOwners` mapping, so no `DIDOwnerChanged` is emitted and the registry still names the wrapper as controller. Record as a fidelity gap under T2.
2. **ERC-1056 V6 status check** in `crud` scans `eth_getLogs` from block 0 (852 B since review 02 gave each iteration a fresh issuer; it was 92 KB when the issuer's history accumulated across iterations). That is the naive realisation; a Status List 2021 bitstring (one attribute) is the intended one and should be implemented in the CVIN-Combined adapter.
3. **Within-run execution-gas spreads (identical between runs):** ERC-721 U1 (154,730 vs 157,530, cold vs warm receiver balance slot) and ERC-721 C1 (iteration 0 is the contract's first mint, −2,800). The reported value is the mode; the REPORT lists every cell with more than one execution value.
4. Latencies are **in-process** Hardhat; they measure client + EVM only. Never compare them with the Python HTTP-RPC numbers without saying so.
5. **Toolchain must be the lockfile's.** A run with Hardhat 2.29.1 (unpinned `npm install`) moved two cells by +12 / +25 gas (ERC-721 U1, U4) against the run of record; `npm ci` (Hardhat 2.28.6) reproduced every shared cell byte-for-byte. Always `npm ci`; `meta.json` records the versions.

### 3.6 ERC-1056 wrapper-controlled mode (`erc1056w`, added 2026-10-04, run `bca0899`)

| Op | pure `erc1056` | wrapper `erc1056w` | vs ERC-721 / ERC-725 (wrapper) |
|---|---:|---:|---|
| C1 create identity | **76,808** (1 tx) | 145,662 (2 tx: register + hand-over) | 2.7× / 4.5× |
| C2 create + VID-I attributes | 366,978 (9 tx) | **234,587** (3 tx) | 2.4× / 6.4× |
| U1 / U4 rotate / transfer | 51,754 | 57,188 | 3.1× / 0.5× (ERC-725 cheaper) |
| U2 add delegate | 55,143 | 64,720 | 0.7× (ERC-721 cheaper) / 1.9× |
| U3 set attribute | **35,024** | 44,677 | 2.7× / 2.7× |
| U5 meta-tx | 62,646 | n/a | — |
| D1 revoke delegate | 32,868 | 41,888 | 0.6× / 1.4× |
| D2 revoke attribute | 34,576 | n/a (no entry point) | — |
| D3 deactivate | 34,230 | 43,809 | 0.6× / 0.5× |
| V1 / V3 / V5 | 55,143 / 33,918 / 33,470 | same (issuer uses the registry directly) | |
| **Lifetime (17 events)** | 1,050,787 (26 tx) | **1,025,381** (20 tx) | **2.63× / 3.08×** |
| Zero→nonzero SSTOREs | 8 | 9 | vs 92 / 83 |
| R3 resolve after lifecycle | 22 RPC / 13.5 ms | 14 RPC / 10.9 ms | vs 7 / 6.5 ms, 17 / 12.1 ms |
| R3 at history h = 50 | 112 RPC / 75 ms | 55 RPC / 39 ms | vs 7 / 16 ms, 61 / 44 ms |

Reading: the wrapper indirection costs ~9–10k gas per mutation (external call + `vehicleOwnerOf` gate) and pays back only where it collapses transactions (C2: −132k). Lifetime improves 2.4%, so the best-case ERC-1056 ratios are 2.6× / 3.1× — H1's verdict (§3.4) does not change. The cheaper resolution in wrapper mode is a side-effect of the fidelity gap in §3.5.1 (ownership transfers leave no registry event), not an efficiency gain. Conformance: `npm run test:conformance` 39 passing / 5 pending; full suite 302 passing / 6 pending.

### 3.7 All nine standards (added 2026-10-04; ten columns — run of record identified by the `meta.measured` code hashes in `results/metrics/latest/meta.json`, see `MEASUREMENT_CONDITIONS.md` §5.F; register rows #34–#35)

The six columns below that existed before are byte-identical to run `bca0899`. Realisations for the new substrates: framework §2.2a (ERC-735, ERC-1155) and §2.2b (ERC-725xy, LSP8, ERC-4337, CVIN-Combined). `n/a` = no primitive on that substrate (a result, not a gap in the harness).

**L1 gas (exact), catalogue ops × substrates**

| Op | ERC-1056 | 1056 wrapper | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Comb. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1 create | **76,808** | 145,662 | 399,844 | 656,480 | 1,535,776 | 103,913 | 1,730,753 | 132,515 | 808,431 | 266,995 |
| C2 create + VID-I | 366,978 (9 tx) | 234,587 (3) | 568,074 (1) | 1,496,440 (9) | 2,285,459 (2) | **103,913** (1, attrs off-chain) | 1,963,543 (2) | 370,025 (2) | 1,153,124 (9) | 1,006,919 (2) |
| U1 rotate / U4 transfer | 51,754 | 57,188 | 179,470 / 182,374 | 28,390 | 28,746 | 83,959 | 28,834 | 83,412 | 28,539 | 68,847 |
| U2 add delegate | 55,143 | 64,720 | 48,314 | 119,852 | n/a | n/a | n/a | n/a | 47,569 (guardian) | 72,308 |
| U3 set attribute | **35,024** | 44,677 | 120,061 | 119,996 | 317,814 | 57,147 (badge, no payload) | 95,334 | 100,573 | 94,651 | 51,742 |
| U5 meta-tx | 62,646 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | **141,767** (EntryPoint) | n/a |
| D1 revoke delegate | 32,868 | 41,888 | 26,174 | 57,200 | n/a | n/a | n/a | n/a | 25,429 | 37,742 |
| D2 revoke attribute | 34,576 | n/a | n/a | 57,316 | 96,611 | 30,625 | 33,880 | 37,806 | 33,469 | 34,198 |
| D3 deactivate | 34,230 | 43,809 | 27,689 | 23,091 | 28,530 | 37,443 | 23,182 | 43,076 | 28,323 | 51,016 |
| V1 issuer key anchor | 55,143 | 55,143 | 419,990 | 119,852 | n/a | 51,281 | 49,745 | n/a | 49,151 | 55,208 |
| V3 anchor credential | **33,918** | 33,918 | 142,909 | 119,996 | 294,628 | 57,519 | 49,805 | 54,874 | 49,211 | 289,788 |
| V5 revoke credential | 33,470 | 33,470 | 125,821 | 43,388 | 92,273 | 30,997 | **27,322** | 32,212 | 26,809 | 89,972 |

**L2 lifetime (17 MOBI VID events)**

| | ERC-1056 | 1056 wrapper | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Comb. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Lifetime gas | **1,050,787** | 1,025,381 | 2,701,239 | 3,155,103 | 5,369,010 (excl. 3 n/a) | 1,150,981 (excl. 2 n/a) | 2,956,507 (excl. 2 n/a) | 1,505,258 (excl. 3 n/a) | 2,221,290 | 2,533,978 |
| Per-identity deploy (in total) | 0 | 0 | 0 | 519,384 | 1,535,776 | 0 | 1,680,804 | 0 | 759,076 | 0 |
| Transactions | 26 | 20 | 17 | 26 | 15 | 21 | 16 | 15 | 25 | 19 |
| Zero→nonzero SSTOREs | **8** | 9 | 92 | 83 | 145 | 18 | 38 | 42 | 37 | 81 |
| Log bytes | 6,464 | 6,592 | 4,288 | 3,072 | 12,576 | 6,080 | 3,744 | 8,288 | 3,968 | 6,496 |
| R3 resolve after lifecycle (RPC / ms) | 22 / 16.5 | 14 / 12.6 | 7 / 6.9 | 17 / 15.5 | 3 / 7.4 | **3 / 2.7** | 2 / 4.3 | 2 / 4.4 | 16 / 8.0 | 17 / 13.0 |
| R3 at h = 50 (RPC / ms) | 112 / 77 | 55 / 51 | 7 / 40 | 61 / 48 | 3 / 39 | **3 / 2.9** | 2 / 37 | 3 / 22 | 61 / 30 | 107 / 84 |
| Throughput, queue+mine (tx/s) | 174 | 124 | 135 | 197 | 76 | 185 | 145 | 162 | 161 | 184 |

**Readings (facts, not conclusions)**

1. **ERC-1056 is the cheapest substrate on every lifetime figure and on C1, U3, V3**, but the margin is not uniform: 1.10× over ERC-1155, 1.43× over LSP8, 2.1× over ERC-4337, 2.4× over the CVIN-Combined hybrid, 2.6× over ERC-721, 3.0× over ERC-725, 5.1× over ERC-735. H1's "≥10×" holds for no pair; even "an order of magnitude cheaper than rich-state standards" is true only for ERC-735 on C2 and ERC-725xy/ERC-735 on C1 (contract-per-identity deployment).
2. **ERC-1155 is the only near-peer, and not like-for-like**: it stores no per-vehicle attributes (C2 = C1), has no delegate keys, and its lifetime excludes 2 n/a events. Its read path is the cheapest of all (3 RPC, 2.7 ms, flat in history). This is the substrate the thesis must argue against most carefully.
3. **The CVIN-Combined hybrid costs 2.4× its ERC-1056 base** because every credential is an on-chain claim with a stored signature (V3 289,788 vs 33,918; 81 vs 8 slots). What the hybrid buys is O(1) **on-chain** verifiability (`hasValidClaim`) for contracts; its off-chain resolution still walks the event chain (107 RPC at h = 50). H5's "hybrid on the Pareto frontier" needs the on-chain-verifiability axis to be stated explicitly, or the data refute it on cost alone.
4. **Contract-per-identity standards pay their identity up front**: ERC-735 1.54 M, ERC-725xy 1.73 M (incl. VIN write), ERC-4337 0.81 M, ERC-725 0.66 M per vehicle, then cheap rotation (28–29k). Over a 17-event life this is 2.1–5.1× ERC-1056; the apportioned fleet rows in `lifecycle_gas` show the shared-registry standards' deployment vanishing at 1 000 vehicles while per-identity deployment never does.
5. **Event-log resolution is the price of event-log cheapness**: the two event-based substrates (ERC-1056, CVIN) are the only ones whose read path grows linearly with history (112 / 107 RPC, 77 / 84 ms at h = 50); storage-based substrates stay at 2–7 RPC. This is H3's second half, measured.
6. **ERC-4337's meta-transaction costs +47,116 over the direct call** (141,767 vs 94,651), matching the nine-standard gas table's +46,830 (register #25) — an independent consistency check between the two instruments.
7. Within-run execution-gas spreads (all deterministic between runs): signature-bearing ops on ERC-735 and CVIN (±25 gas, ECDSA zero bytes), ERC-721 C1/U1 (first mint, cold receiver), LSP8 C1 (first mint pays the collection counter's cold slot, +17,100).

**Verdict update (framework §8).** H1 as written is refuted on the full set; the defensible statement is: *"ERC-1056 has the lowest lifetime cost and persistent footprint of the nine standards (1.1–5.1×), at the cost of a resolution path linear in identity history."* H4 (event-log cheapest for VID-II events) holds against every storage-based standard except ERC-1155's badge issuance (57k vs 35k for U3 — ERC-1155 wins none) — holds. H5 holds trivially (ERC-1155 dominates reads, ERC-1056 writes, ERC-725-family rotation) but the hybrid is not on the cost frontier.

Conformance gate: 87 passing / 23 declared n/a; full Hardhat suite 351 / 23.

---

## 4. Audit F-items status (from `docs/AUDIT_01_ORIGINAL_GOALS.md`)

| Item | Status after this session |
|---|---|
| F1 nine standards claimed, three on trunk | **closed for the harness (2026-10-04)**: all nine standards (ten adapters) run the identical catalogue; no `not impl.` cell remains in `results/metrics/latest` (§3.7) |
| F2 no PKI baseline number | **closed on the trunk**: `cv2x-testbed/scripts/experiment_pki_vs_erc1056.py`, register #21 (re-run in review 02) |
| F3 three values for one quantity | **closed**: `MEASUREMENT_CONDITIONS.md` + superseded-numbers table |
| F4 reproducibility asserted while broken | conformance gate + harness in CI (`benchmark.yml`, `metrics-harness` job), **green on GitHub** since review 02 enabled the workflow on `claude/**` pushes |
| F5 self-scored compliance | unchanged |
| F7/F8 latency budget, statistics | N = 30, median/p95, bootstrap CI and Mann–Whitney available in `lib/stats.js`; J2945/1 derivation still to write |
| F9 threats to validity after the fact | **closed**: pre-registered in framework §11 |
| F10 silent scope drops | **closed**: framework §12 scope-change log |

---

## 5. Next steps, in priority order

1. ~~`erc1056w` adapter~~ — **done** (`2439cd0`, §3.6). Follow-up decision: should the wrapper emit (or forward) `DIDOwnerChanged` on ownership transfer so did:ethr resolvers see the vehicle owner? Either implement, or document the gap in the T2 compliance discussion.
2. **PKI-vs-ERC-1056 script** (`cv2x-testbed/scripts/benchmark_pki_vs_erc1056.py`, closes F2; ~3 h). Map `C2→register_vehicle, V2→sign, V4→verify, V5→revoke, V6→check_revocation, R3→resolve`; N = 30; one CSV; label the HTTP-RPC condition.
3. ~~ERC-735, ERC-1155, ERC-725xy, LSP8, ERC-4337, CVIN-Combined adapters~~ — **done** (§3.7). Note: no substrate exposes a native batch *creation* primitive (ERC-1155's `mintBatch` is not surfaced by `registerVehicle`), so the `batch` table is sequential throughout — itself a finding. Follow-ups the data suggest: (a) a Status-List-2021 variant of CVIN-Combined so credential status is one bit, not a stored claim; (b) an ERC-1155 variant that binds VID-I attributes (per-vehicle URI) so C2 is like-for-like; (c) a delegate model for LSP8 (operators) and ERC-725xy (LSP6) if those columns are to be compared on U2/D1.
4. **Rewrite H1** in `README.md` / `docs/RESEARCH_THRUSTS_REPORT.md` / `docs/thesis/README.md` per §3.4 so one hypothesis structure appears everywhere (audit F6).
5. **Rubric scoring** (`benchmarks/rubric/did-method-rubric.json`): complete the empty criteria for the three substrates with file:line evidence; every substrate added later gets a column.
6. **Remote-RPC condition run**: `npm run node` + `METRICS_*` against `localhost` network to get latencies with a real JSON-RPC round-trip (a separate, labelled conditions block).
7. **Sepolia confirmation**: one `lifecycle` per substrate on a public testnet (needs `SEPOLIA_RPC_URL`, `PRIVATE_KEY` in `.env`).
8. Make `benchmark.yml` actually run on the branch (it triggers on `main` and cron); confirm green, add the badge.

## 6. Conventions to keep

- Commits are authored `Nikhil Prakash <nikhil.prakash1995@gmail.com>` with no AI co-author trailers — the standing decision recorded in `docs/AFTER_ACTION_REPORT.md` §1 (academic-integrity attribution). This session honoured it; if that decision changes, say so in that report.
- Only `results/metrics/latest/` is tracked; `results/metrics/runs/` is ignored.
- A number enters a chapter only with its run id. Old numbers are listed as superseded in `MEASUREMENT_CONDITIONS.md` §D — add to that table rather than deleting history.

## 7. Session log (what happened, for provenance)

- Rebased the v1 handoff commit onto the trunk that had moved (`084edfd`: build fixed to solc 0.8.24, tests 47/47, audit + project summary).
- Wrote methodology and conditions documents; built harness; three adapters passed conformance; smoke runs surfaced and fixed: `setVehicleAttributes` unreachable in direct mode (→ pure did:ethr C2), one-address-one-DID iteration collision (→ fresh funded owner per identity), Hardhat automine nonce rejection (→ queue-then-mine throughput), ethers `estimateGas` dominating the queue phase (→ fixed fee overrides), RPC counting through `provider.send`, dataset off-by-one at N = 1 000, varying string lengths (→ fixed-width payloads).
- Full run committed as `results/metrics/latest`; pushed.
- 2026-10-04 (later): added adapters for ERC-735, ERC-1155, ERC-725xy, LSP8, ERC-4337 and CVIN-Combined; the harness now records `n/a` lifecycle events and excludes them from totals, uses a fresh receiver where a substrate needs one (ERC-1155 K-13), keys throughput nonces by sender (LSP8's single authority) and stamps runs with the `1_blockchain-identity` tree hash (§5.F of the conditions). Gate 87 / 23, suite 351 / 23. Two adapter bugs found by the gate before any number was recorded: ERC-1155 transfer left credentials on the old address (now re-binds every held type), CVIN resolver dropped events with `previousChange = 0`.
- 2026-10-04: added `erc1056w` on top of the review-02 harness; its conformance run exposed the one-address-one-DID collision in the test's C1/C2 (fixed: C1 uses its own wallet) and that "expire now" cannot stand in for attribute revocation (D2 declared n/a). Re-ran all six scenarios for four substrates; found and documented the toolchain-pinning effect (§3.5.5); `results/metrics/latest` is run `bca0899`.
