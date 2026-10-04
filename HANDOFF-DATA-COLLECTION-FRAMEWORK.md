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

## 3. Headline results (run of record now `2026-10-04T05-41-19Z_bca0899`, clean tree, locked toolchain; its ERC-1056 / ERC-721 / ERC-725 columns are byte-identical to `59405ff` quoted below, and it adds the ERC-1056 wrapper column of §3.6; full tables in `results/metrics/latest/`)

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

---

## 4. Audit F-items status (from `docs/AUDIT_01_ORIGINAL_GOALS.md`)

| Item | Status after this session |
|---|---|
| F1 nine standards claimed, three on trunk | unchanged in substance; tables now print `not impl.` cells explicitly so the gap is visible, not hidden |
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
3. **ERC-735 adapter + contract** (claims on top of the ERC-725 identity; next in the roadmap). Then ERC-1155 (first substrate with a *native batch* primitive — the `batch` scenario will finally have a `native` row), ERC-725xy, LSP8, ERC-4337, CVIN-Combined (ERC-1056 anchor + Status List + ERC-1155 credential tokens).
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
- 2026-10-04: added `erc1056w` on top of the review-02 harness; its conformance run exposed the one-address-one-DID collision in the test's C1/C2 (fixed: C1 uses its own wallet) and that "expire now" cannot stand in for attribute revocation (D2 declared n/a). Re-ran all six scenarios for four substrates; found and documented the toolchain-pinning effect (§3.5.5); `results/metrics/latest` is run `bca0899`.
