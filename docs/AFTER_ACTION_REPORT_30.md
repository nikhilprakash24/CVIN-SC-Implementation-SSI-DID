# After-Action Report 30 — ZKP Work Entered into the Thesis Record (Plan 3)

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Opened and closed:** 2026-10-22. **Brief (the author):** after the merge of PR #3, continue with thesis integration
on the defaults of `docs/zkp/THESIS_INTEGRATION_MAP.md` §5. **Plan:** `docs/zkp/PLAN_3_THESIS_INTEGRATION.md`,
written before execution. **Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`.

## 1. Precondition (rule 1.1.4)
The layer-5 rows were measured at `978988e` (Z7 at `e780d40`), each run stamped `code_clean` true. Between those
commits and the merged trunk (`bc4618f`) the producers under `5_zkp-agent-identity/` changed only by a citation-key
comment in `bench/vin_bruteforce.py`; the lineage merge touched neither layer 5 nor the VC layer it imports. No re-run
was needed. Five of the six runs had uncommitted documents in the tree (`tree_clean` false); each row says so.

## 2. What was done

| Step | Change |
|---|---|
| Condition tag | **Sim** (seeded in-process simulation) added to register §1 |
| Register | rows **#56–#62** = Z1–Z7: circuit size; prove/verify time; on-chain gas; sigma primitives; VIN brute force (extrapolations E); narrowing attack (Z-E5 PASS, Z-E6 FAIL); manual burden (counts V, hand times E) |
| Generated documents | seven result cards in a new group *Zero-knowledge identity and the agent wrapper*; #58 classed G-exact in the gas charter; dashboard, presentation report and register figure regenerated |
| Thesis | RQ5 and H6 (verdict: partly supported) in `docs/thesis/README.md` and chapter 1, marked as an extension; the sections of the map §1 listed in `SCAFFOLD.md` as ▫️ |
| Scope | "SC-12 reopened" and **SC-23** (layer 5, bounded) appended to `docs/SCOPE_CHANGES.md`; a dated note in `docs/phase2/SCOPE_RECONCILIATION.md` |
| Ideas | `build_phase2.py` gains an optional, append-only `status` list per idea; I-09 and I-10 carry 2026-10-22 entries |
| Map | `THESIS_INTEGRATION_MAP.md` records the adoption and the Z → # mapping; its proposals are kept as written |

## 3. Checks
Every CI document check passes (`build_register`, result cards, gas charter, dashboard, presentation, Phase 2 build
and focus figures, F3 modes, docs numbers, stamp coverage, layer-5 figures, citations).

## 4. Findings
- **Generated idea register.** The first edit went into `IDEA_REGISTER.md`, which `build_phase2.py` overwrites from
  `ideas.yaml`; the regeneration silently discarded it. The status notes now live in the YAML and the generator.
- **Card checks bind headlines to row text.** Each card's numbers had to appear in the claim or status cell, not only
  in the source column; the Z rows state their key figures in the claim for that reason.

## 5. Not done, and the author's decisions
- **Chapter prose** for §2.x–§7.x is owed (Plan 2, W-4); only the scaffold and chapter 1's questions and hypotheses
  were written here.
- **Overturnable defaults:** RQ5/H6 as an extension rather than a retitle; agent argument in chapters 6–7.
- **Still open:** D54 (organisational attesters keep registry-wide scope by design).
