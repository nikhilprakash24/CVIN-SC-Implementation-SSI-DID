#!/usr/bin/env bash
# Mutation probe of the D54 fix (WM-2 C2; after-action report 36; guide rule 1.3.11): each mutant weakens one guard of
# the attestation consent rule or of the MOBI registry's stored delegations, and attestEventRegression.test.js must
# fail on every one. Both contracts are restored on exit. Run from the repository root.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
V2=1_blockchain-identity/contracts/MOBI/MOBIVIDRegistryV2.sol
REG=1_blockchain-identity/contracts/MOBI/MOBIVIDRegistry.sol
O2=$(mktemp); OR=$(mktemp); cp "$V2" "$O2"; cp "$REG" "$OR"
trap 'cp "$O2" "$V2"; cp "$OR" "$REG"; rm -f "$O2" "$OR"' EXIT
mutate() { python3 - "$1" "$2" "$3" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text(); old, new = sys.argv[2], sys.argv[3]
assert s.count(old) == 1, f"anchor found {s.count(old)} times: {old}"
p.write_text(s.replace(old, new, 1))
PY
}
# Behaviour tests only: the file's gas-pin test would kill almost any mutant by its gas change alone, which proves
# nothing about behaviour (report 36 found that first).
run() { (cd 1_blockchain-identity && npx hardhat test --grep "D54|vulnerable path" test/L2-identity-system/per-option/MOBIVID/attestEventRegression.test.js >/dev/null 2>&1); }
survived=0
while IFS='|' read -r name file old new; do
  [ -z "$name" ] && continue
  cp "$O2" "$V2"; cp "$OR" "$REG"
  if ! mutate "$file" "$old" "$new"; then echo "ANCHOR   $name"; survived=$((survived+1)); continue; fi
  if run; then echo "SURVIVED $name"; survived=$((survived+1)); else echo "killed   $name"; fi
done <<LIST
consent_delegate_always|$V2|validDelegate(vehicleIdentity, "veriKey", msg.sender),|true,
consent_wrong_type|$V2|validDelegate(vehicleIdentity, "veriKey", msg.sender),|validDelegate(vehicleIdentity, "sigAuth", msg.sender),
duplicate_check_removed|$V2|require(!hasAttested[eventId][msg.sender], "Already attested");|
duplicate_not_recorded|$V2|hasAttested[eventId][msg.sender] = true;|
delegation_not_stored|$REG|delegates[identity][delegateType][delegate] = block.timestamp + validity;|
revocation_not_stored|$REG|delegates[identity][delegateType][delegate] = block.timestamp;|
expiry_ignored|$REG|delegates[identity][delegateType][delegate] > block.timestamp;|delegates[identity][delegateType][delegate] > 0;
revoked_identity_ignored|$REG|!revoked[identity] && |
LIST
cp "$O2" "$V2"; cp "$OR" "$REG"
run || { echo "BASELINE FAILS after restore"; exit 99; }
echo "D54 mutants: $survived of 8 survived"
exit $survived
