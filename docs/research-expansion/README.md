# Research Expansion

Composed CAV scenarios, primitive upgrades and moonshots that extend the thesis beyond per-primitive measurement. Started 2026-10-15.

| File | Read it for |
|---|---|
| `IDEAS.md` | The catalogue: 12 composed scenarios (X), 15 primitive upgrades (P), 10 moonshots (M), each with tier, touched code, measures and sources |
| `WHY.md` | Why each idea exists, the results that would change the thesis, the mapping to RQ1–RQ4 and proposed RQ5–RQ7, threats, and the method used to generate ideas |
| `SOURCES.md` | About 95 sources from the sweep (S1–S94), the quantitative anchors, and what could not be verified |
| `PROMPT_PACK.md` | Plan 2: every work package as a self-contained prompt for a fresh session |
| `../PLAN_RESEARCH_EXPANSION.md` | Plan 1: phases, work packages, definitions of done, dependency graph, author decisions, progress log |
| `results/` | One results note per completed work package (created by the prompts) |

**Built so far:** scenario X1, the toll corridor (endorsed DID passage plus a stablecoin toll, with a legacy plate lane).

```bash
cd 1_blockchain-identity && npm run test:scenarios          # 20 Hardhat tests
python3 cv2x-testbed/scenarios/toll_corridor.py --rpc http://127.0.0.1:8548   # needs a node + compile
```
