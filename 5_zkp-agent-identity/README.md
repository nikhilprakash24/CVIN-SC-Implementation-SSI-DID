# Layer 5 — Zero-Knowledge Proofs and the Agent-Wrapped Identity

**Author:** Nikhil Prakash (MASc, UBC ECE) · **Written:** 2026-10-15 · **Plan:** `docs/zkp/PLAN_1_ZKP_AND_AGENT_IDENTITY.md`
**Reports:** `docs/zkp/REPORT_A_ZKP_INTEGRATION.md` (build and verdicts), `REPORT_B_ZKP_AND_IDENTITY.md` (the paper),
`REPORT_C_AGENT_WRAPPED_IDENTITY.md` (the full-circle argument).

A vehicle proves facts about its VIN without revealing it, on chain and off; an agent (the Steward) wraps the vehicle's
identity, turns the owner's plain-English rules into a signed policy, computes the proofs, bounds what any set of
verifiers can learn, and presents its own delegated identity. Research code: the Groth16 keys come from an INSECURE
single-party setup, and `zkid` is not constant time.

| Path | What |
|---|---|
| `zkid/` | secp256k1, Keccak-256, Fiat–Shamir, Schnorr, Pedersen, Chaum–Pedersen, CDS OR, range and threshold proofs, Merkle, nullifiers |
| `circuits/zkvin.circom`, `circuits/build_circuit.sh` | the ZK-VIN circuit (3,498 constraints) and its reproducible, insecure dev setup |
| `artifacts/` | wasm, r1cs, zkey, verification key, `MANIFEST.json` (SHA-256 of each) |
| `contracts/` | generated `Groth16Verifier.sol`, `ZkVinGate.sol` (IDTx with a knowledge-of-opening dependency), `SchnorrEcrecoverVerifier.sol` |
| `steward/` | the agent: policy, compiler, kernel, leakage audit, learner, vault, audit log, delegation, agent |
| `attacks/` | the twenty-questions attack, Sybil and insider variants, defences, training, evaluation |
| `bench/` | sigma timings, VIN brute force, manual-burden inventory, `run_all.sh` (runs of record) |
| `figures/` | 12 figures from committed results; `make_figures.py --check` |
| `demos/full_circle_demo.py` | the whole story in one terminal session (transcript in `results/demo_transcript.txt`) |
| `tests/`, `test-contracts/`, `mutate_zkid.sh`, `mutate_zkvin_gate.sh` | 49 Python tests, 9 contract tests, 5 Python mutants and 12 ZkVinGate mutants that must be caught |

```bash
pip install pytest eth-account coincurve matplotlib && npm ci
python3 -m pytest                          # 49 tests
python3 demos/full_circle_demo.py          # the story
node scripts/prove_and_verify.js           # Groth16 ZK-VIN: honest proof + five false statements
(cd ../1_blockchain-identity && npm ci && npx hardhat compile && npx hardhat --config hardhat.zkp.config.js test)
bash bench/run_all.sh                      # runs of record, from a clean tree
```

| Headline (commit of record in each results file) | Value | Condition |
|---|---|---|
| ZK-VIN prove / verify (median) | 398.6 ms / 18.42 ms | M0 |
| `ZkVinGate.admit` with Groth16 verification | 301,163 gas | M1 |
| Unsalted VIN hash reversed (serial unknown) | 3.58 s for 10⁶ | M0 |
| Undefended twenty-questions attack | exact on 30/30 seeds | Sim |
| Steward under single, Sybil and insider attacks | ≤ 3.0 bits on 90/90 runs | Sim |
| Honest service ≥ 90 % on every seed (Z-E6) | **not met** (25/60 runs below) | Sim |
| One ZK-VIN proof by hand | ≈ 124,500 working years | E |
