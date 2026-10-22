#!/usr/bin/env bash
# Mutation probe of the IDTx gate (Phase 2 F1; academic review AR-14; guide rule 1.3.11): each mutant weakens one
# guard, and the behaviour suite must fail on every one. The contract is restored on exit.
# Run from the repository root after `cd 1_blockchain-identity && npx hardhat compile`.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
F=phase2/idtx/contracts/IdtxExecutor.sol
ORIG=$(mktemp); cp "$F" "$ORIG"; trap 'cp "$ORIG" "$F"; rm -f "$ORIG"' EXIT
mutate() { python3 - "$F" "$1" "$2" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text(); old, new = sys.argv[2], sys.argv[3]
assert old in s, "anchor not found: " + old
p.write_text(s.replace(old, new, 1))
PY
}
run() { (cd 1_blockchain-identity && npx hardhat --config hardhat.phase2.config.js test >/dev/null 2>&1); }
survived=0
while IFS='|' read -r name old new; do
  [ -z "$name" ] && continue
  cp "$ORIG" "$F"; mutate "$old" "$new"
  if run; then echo "SURVIVED $name"; survived=$((survived+1)); else echo "killed   $name"; fi
done <<'LIST'
holds_always_true|        if (d.kind == Kind.Owner) return registry.identityOwner(d.identity) == d.party;|        return true;
no_recheck_at_fulfil|        require(holds(it.dep), "identity dependency not met");|
commitment_validity_ignored|        if (validUntil[identity][key] <= block.timestamp) return bytes32(0);|
commitment_setter_ignored|        if (registry.identityOwner(identity) != setBy[identity][key]) return bytes32(0);|
deadline_ignored|        require(block.timestamp <= it.deadline, "deadline passed");|
LIST
cp "$ORIG" "$F"
echo "IDTx gate mutants: $survived survived"
exit $survived
