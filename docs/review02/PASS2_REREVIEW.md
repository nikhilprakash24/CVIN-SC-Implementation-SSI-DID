# Pass 2 — Adversarial re-review of Pass 1 (`d0fe9f0` → `4d3dcfa`)

A fresh, read-only reviewer tried to break the Pass 1 diff: bypasses around the new checks,
regressions in callers and entry scripts, vacuous tests (by mutation), the fairness of the
re-runs, and CI. PoCs and mutation copies were kept outside the tree. Every result file a
script rewrote was restored.

## Findings and disposition

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| R2-H1 | **High** (PoC) | **K-2 bypass.** `revokedClaims` is written only inside `removeClaim`, which needs the claim to be anchored. An owner who removes the claim first leaves the issuer with nothing to revoke, and can later re-add the old signature (ERC-735 and CVIN-Combined) | **Pass 3** (stream P2-K): issuer-only `revokeClaimContent` that records the revocation whether or not the claim is anchored |
| R2-H2 | **High** (PoC) | **#21/#22 measured stale bytecode.** The tracked `cv2x-testbed/artifacts` predate K-3/K-4. `--deploy` and the conftest default load them: deploy 878,509 tracked vs 927,756 fresh; `changeOwner` after revoke succeeds on the tracked artifact | **Pass 3** (streams P2-K and P2-T): rebuild the artifacts from current sources, re-run #21 on them, re-state #22. CI was not affected (it uses a fresh compile) |
| R2-M1 | Med | HANDOFF §3.2 shared deployment 2,673,900 (pre-K-1 value) vs run of record 2,709,021; "7 vs 79–91 slots" vs 8 / 83–92 | **Fixed** in this commit |
| R2-M2 | Med (PoC) | K-4 residual: an authorised manufacturer can still "birth" a did:ethr that has never been used on-chain (`changed == 0`), locking out the real key holder | **Author decision:** the full fix needs a consent signature from `vehicleIdentity`, which changes `registerVehicleBirth`'s API and the backend sweep. Until then, documented as a residual risk (manufacturer is a trusted role) |
| R2-M3 | Med | `test_revoked_identity_rejected` passes with the `is_revoked` check removed: `DIDRevoked` cuts the event chain, so no key resolves anyway | **Pass 3** (stream P2-T) |
| R2-L1 | Low | `attack_scenarios.py`, `sumo_identity_integration.py --simulate` and `run_verify_richness.py` rewrite tracked result files | Noted in the handback. Run them with a scratch output path or restore afterwards |
| R2-L2 | Low | Sybil-cost gas in `security_matrix.json` / `CAPABILITIES.md` is stale (e.g. ERC-735 1,404,108 vs 1,466,088). Attack outcomes are unchanged | Handback follow-up: regenerate the matrix after Pass 3's gas re-run |
| R2-L3 | Low | `docs/conformance/implementations/*.json` predated S-10 | **Fixed** in this commit (regenerated: `eip155:1`, `invalidDid`). The external suite itself still needs a re-run (#24) |
| R2-L4 | Low | Thesis chapters still say 93.2 % (now 94.3 %) and 46,862 (now 46,830) | Author's chapter pass (listed in the handback) |
| R2-L5 | Low | The identity-theft cell in `attack_scenarios.py` still uses the weaker same-DID thief, so it doesn't exercise S-1 | Handback follow-up |
| R2-L6 | Low | `add_status_registry` silently overwrites a duplicate id (fails closed: DoS, not acceptance) | **Pass 3** (stream P2-T): raise |
| R2-L7 | Low | Demo-only `SHARED_HOLDER_KEYS` is first-binding-wins; T-1 does not check the anchor's own validity window or basicConstraints; `run_all_demos.py` needs stdin (pre-existing) | Noted |

## Verified OK (selected)
- **K-2, K-3, K-4, S-5, S-6, S-7, T-1, T-2:** removing each guard makes the matching
  test fail (mutation M1–M11, except M11 = R2-M3).
- **K-3/K-4:** every inherited path on a revoked identity is blocked.
- **K-2:** a malleated signature is rejected.
- **K-13:** no other transfer path exists.
- **S-1:** the binding option is verifier configuration only; no attacker input reaches it.
- **S-2:** the registry→issuer binding holds.
- **Within-block event order:** replayed correctly.
- **CI:** a clean venv with exactly the CI pip set gives 195 passed, 0 skipped; checker 94.3 %.
- **Entry scripts:** `run_all_demos.py` (with stdin), `test_use_cases.py`,
  `attack_scenarios.py`, the checker, SUMO `--simulate`, `basic_v2v_scenario.py` (98/98),
  `run_verify_richness.py` and `generate_implementations.py` all run.
- **Run of record:** `results/metrics/latest/meta.json` is clean at `59405ff`.
- **Fresh-issuer change:** no new bias. V1 is a second anchor on every substrate, and both
  ERC-1056 and ERC-725 differ from the lifecycle first-anchor cost by exactly 17,100.
- **#21 register row:** matches `pki_vs_erc1056.json`. The 4 ERC-1056 RPCs are
  `eth_chainId, eth_call, eth_chainId, eth_getLogs`; two of them are web3 client overhead,
  and the caveat states this.
