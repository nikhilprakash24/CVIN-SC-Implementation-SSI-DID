# After-Action Report 20 — Merging the Clone Lineage into the ZKP Branch (PR #3)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened and closed:** 2026-10-21. **Brief (the author):** "continue but resolve the conflicts to merge" PR #3
(head `claude/zkp-ai-identity-research-n5uho9`, base `claude/clone-cvin-id-scs-011CUyxScetMdSQFkuQUNLTt`).
**Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`, in particular rule 1.3.6 (read another branch and write down its relation
before merging) and rules 1.1.4–1.1.6 (results re-executed on the code they describe, from a clean tree).

## 1. The relation between the two lineages (rule 1.3.6)

Both lineages left `fa6188e`. The **cv2x lineage** (this branch: `cv2x-testbed-setup` plus Plan 1) carries 131
commits: the sandbox and suites, the lineage merge of 2026-10-06 (sandbox contracts D7, D8, D11b, D13, D18, D21, D22,
D25), WM-1 and WM-2, infrastructure messaging (I1–I5), Phase 2 (F1–F3) and layer 5. The **clone lineage** carries 45:
the review-02 follow-up streams **H-A** (attestEvent: OWNER-role scope and one attestation per attester), **H-K**
(same-host freshness-k, full against probe refresh), **H-L** (Pass 3 Lows: revocation reason, revert origin in the
security harness, SUMO replay cache) and **H-R** (on-chain did:ethr and did:mobi resolution), the basic digital-ID set
framing with two new harness operations (P1 createPresentation, X1 execute), and its own after-action report 06.

Neither lineage contains the other's work; both numbered new register rows from #40 and both opened a report 06. The
clone lineage's code was written against the pre-lineage-merge contracts, which matters in three places (§3).

## 2. Conflicts (81 files) and resolutions

| Group | Files | Resolution |
|---|---|---|
| Generated results and compiled artifacts | 73 | cv2x side provisionally, then regenerated on the merged tree (§4) |
| SUMO integration result dict | 1 | both keys kept |
| Security scenario (ERC-1155 hijack) | 1 | cv2x D7 reason, with the H-L harness's mandatory `target` |
| attestEvent regression pin | 1 | measured on the merged bytecode: **192,040** = 169,361 (cv2x dispatch +66) + 22,679 (H-A) |
| Claim register | 1 | cv2x rows kept; clone #40–#42 → **#52–#54**; clone notes on #4, #24, #25, #33 appended; #28 rewritten; merge note with the re-run list |
| Two reports numbered 06 | 1 (add/add) | clone report moved to `AFTER_ACTION_REPORT_06_CLONE_LINEAGE.md`; notes in both |
| Handback next-session list | 1 | clone list (it executed the cv2x list's items); note |
| W3C suite document | 1 | both sections; clone §10 is §13 here |
| README | 1 | cv2x wording (counts from the grand report) |

## 3. What the suites found after the textual merge

1. **On-chain did:mobi resolution of a revoked identity failed.** The clone lineage's resolver decoded
   `DIDRevoked(address,uint256)`; the merged contract emits the D21 three-argument form (it links back to the previous
   change). The topic filter found no event in the revocation block. Fixed in `did_resolver.py`; the resolver suites
   pass (109).
2. **Stamp coverage.** The same-host freshness replicates and summary (clone) and the layer-5 results (cv2x, pass 19)
   were not declared to `check_stamps.py`. Declared; 209 tracked result files, 0 uncovered. The layer-5 gap predates
   the merge and would have failed CI on this branch alone.
3. **Generated documents.** Rows #52–#54 needed a gas class (#53) and result cards; card #28's caption carried the old
   pin. Added and regenerated; every CI `--check` current.

## 4. Re-execution on the merged tree

| Result | Producer | Outcome |
|---|---|---|
| Nine-standard gas table (#25) | `benchmark_gas.js` + `generate_tables.py` | 2 of 55 cells moved, both MOBI-VID-V2: deploy 4,225,285 → **4,309,419**, transfer 200,089 → **200,111** |
| MOBI backend sweep (H4) | `mobi_vid_backend_sweep.js` + table | attestEvent 192,749 → **215,428** (+22,679, H-A); nothing else moved |
| Gas determinism (30 runs) | `run_gas_stats.py --runs 30` | 30 runs, every cell byte-identical (`gas_benchmark_stats.json`) |
| Metrics harness (#29–#31, #34–#36, #49–#51, #53) | `npm run metrics` + `metrics:analyze` | run `2026-10-21T03-28-59Z_a9e2a28`, clean: all 130 earlier per-operation gas cells unchanged; P1 and X1 added (as the clone lineage measured them, except ERC-735 P1 294,868, +240 from D25); dominance re-derived: cost-only and all-six frontiers unchanged, CVIN-Combined additionally dominated by the ERC-1056 wrapper on cost + read path through a run-dependent latency axis (#36) |
| M4 parity (#33) | `experiment_lifecycle_parity.py --deploy` | **not re-run** (needs the testbed on a live node; #33 marked re-run due) |

## 5. Checks
Hardhat 559 passing / 34 pending; Phase 2 12; layer 5 contracts 8; Python 427 with a node (0 skipped); sandbox suites
365; layer 5 49; resolver 109; every CI document check current; citations 0 unresolved.

## 6. Not done, and the author's decisions
- **Not re-run:** M4 parity (#33) and the HTTP-RPC condition (#39). Both rows say so.
- **A harness run was discarded.** The first post-merge harness run overlapped a full Hardhat test run on the same
  host, which can perturb its latency columns; it was stopped and its output deleted, and the harness was re-run alone.
- **Two more fixes found by CI after the first push:** the feature-asymmetry matrix (the merged contract gained
  `hasAttested`) and the testbed's compiled MOBIVIDRegistryV2 artifact (taken provisionally from the cv2x side) were
  stale; both regenerated. Running the rest of that CI job locally also found the grand report's test count (537 against
  559), the claims demo asserting the pre-H-A duplicate attestation as an observation (now a revert), two superseded
  figures in the clone lineage's basic-set document, and the `1.096` stale-number pattern matching inside an arXiv id
  (anchored; shown to fire on the real value and not on the id).
- **Defect D54 narrowed, not closed.** H-A scopes OWNER-role attesters and stops duplicates; organisational roles keep
  registry-wide scope by design. Whether that meets threat-model goal G4 is the author's decision (default: accept as
  designed, keep D54 open on that point).
- **Register numbering.** Clone #40–#42 are #52–#54; the generated freshness summary still prints "#40" (its producer
  is unchanged); the register's merge note is the mapping. Default: leave the producer as is.
- **CI:** all 22 checks green on `a9e2a28`.
