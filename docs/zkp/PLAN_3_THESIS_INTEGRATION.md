# Plan 3: Integrating the ZKP and Agent-Identity Work into the Thesis Record

**Author:** Nikhil Prakash (MASc, UBC ECE)
**Written:** 2026-10-22, before execution. **Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`.
**Brief (the author):** continue with thesis integration, taking the defaults in `THESIS_INTEGRATION_MAP.md` §5.

## Defaults adopted (from the map, §5)
RQ5/H6 as an extension of the existing questions (no retitle); rows Z1–Z7 added to the register as V (Z7 split
V/E); the agent argument placed in chapters 6 and 7, not a new chapter; Plan 2's series stays a companion.

## Precondition (rule 1.1.4)
The Z rows were measured at `978988e` (Z7 at `e780d40`) with `code_clean` true. Their producers under
`5_zkp-agent-identity/` have not changed since, except a comment in `bench/vin_bruteforce.py` (a citation key); the
lineage merge touched neither layer 5 nor the VC layer it imports. So the rows describe the trunk and need no re-run.
`tree_clean` was false at those runs (uncommitted documents only); this is stated in each row.

## Steps
1. Register §1: add the condition tag **Sim** (seeded in-process simulation).
2. Register: rows **#56–#62** for Z1–Z7, each with tag, source, commit and status.
3. Generated documents: result cards for the new V rows, gas classes for the gas-bearing row, then every `--check`.
4. Thesis scaffolding: RQ5 and H6 in `docs/thesis/README.md` and chapter 1; pointers in chapters 2–7 per the map §1.
5. Scope and ideas: SC-12 reopened in `docs/phase2/SCOPE_RECONCILIATION.md`; I-09 and I-10 status in
   `docs/phase2/IDEA_REGISTER.md`.
6. `THESIS_INTEGRATION_MAP.md`: status changes from "proposals only" to "adopted on the defaults", with row numbers.
7. After-action report 30 and a handback addendum.

## Not in scope
Chapter prose (Plan 2, W-4, drives it); any new measurement.
