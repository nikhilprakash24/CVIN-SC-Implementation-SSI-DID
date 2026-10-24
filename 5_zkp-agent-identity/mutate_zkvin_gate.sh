#!/usr/bin/env bash
# Mutation probe of ZkVinGate (Phase 3 of the smart-contract annotation work; same pattern as
# phase2/idtx/mutate_idtx.sh): each mutant removes one guard of admit()/anchorCommitment()/setService(),
# and the layer-5 Hardhat suite (5_zkp-agent-identity/test-contracts/zkvin_gate.test.js) must fail on every
# one. The contract is restored on exit. Run from anywhere inside the repository.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
F=5_zkp-agent-identity/contracts/ZkVinGate.sol
ORIG=$(mktemp); cp "$F" "$ORIG"; trap 'cp "$ORIG" "$F"; rm -f "$ORIG"' EXIT
mutate() { python3 - "$F" "$1" "$2" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text(); old, new = sys.argv[2], sys.argv[3]
assert s.count(old) == 1, "anchor not found exactly once: " + old
p.write_text(s.replace(old, new, 1))
PY
}
run() { (cd 1_blockchain-identity && npx hardhat --config hardhat.zkp.config.js test >/dev/null 2>&1); }
survived=0
while IFS='|' read -r name old new; do
  [ -z "$name" ] && continue
  cp "$ORIG" "$F"; mutate "$old" "$new"
  if run; then echo "SURVIVED $name"; survived=$((survived+1)); else echo "killed   $name"; fi
done <<'LIST'
anchor_any_caller|        if (registry.identityOwner(identity) != msg.sender) revert NotIdentityOwner();|
register_any_caller|        if (msg.sender != governor) revert NotGovernor();|
inactive_service|        if (!s.active) revert UnknownService();|
commitment_unchecked|        if (anchored == 0 || pub[COMMITMENT] != anchored) revert SignalMismatch(COMMITMENT);|
mfr_root_unchecked|        if (pub[MFR_ROOT] != mfrRoot) revert SignalMismatch(MFR_ROOT);|
min_year_unchecked|        if (pub[MIN_YEAR] != s.minModelYear) revert SignalMismatch(MIN_YEAR);|
region_unchecked|        if (pub[REGION] != s.region) revert SignalMismatch(REGION);|
scope_unchecked|        if (pub[SCOPE] != s.scope) revert SignalMismatch(SCOPE);|
challenge_unchecked|        if (pub[CHALLENGE] != s.challenge) revert SignalMismatch(CHALLENGE);|
nullifier_reuse|        if (nullifierUsed[s.scope][pub[NULLIFIER]]) revert NullifierUsed();|
proof_unchecked|        if (!verifier.verifyProof(a, b, c, pub)) revert InvalidProof();|
nullifier_not_spent|        nullifierUsed[s.scope][pub[NULLIFIER]] = true;|
LIST
cp "$ORIG" "$F"
echo "ZkVinGate mutants: $survived survived"
exit $survived
