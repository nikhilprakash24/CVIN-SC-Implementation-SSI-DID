#!/usr/bin/env bash
# Pre-push guard (after-action report 24): the document and copy guards CI runs, run locally and unpiped,
# so a push never leaves CI red on something that takes seconds to check here.
#
#   tools/prepush_check.sh          # run every guard; exit 1 on the first failure
#   tools/prepush_check.sh --probe  # also show the guard fires: break one copy, expect failure, restore
#
# It does not run the test suites or the grand runner (those take minutes); it mirrors the steps of
# .github/workflows/test-contracts.yml "Check ... up to date", "MOBI contract copies", "feature-asymmetry matrix",
# and the testbed artifact freshness step of w3c-compliance.yml when the testbed's node_modules link exists.
set -u
cd "$(dirname "$0")/.."

# The stale-figure checker scans tracked files only: stage new files before running this (report 24 learned it).
if [ -n "$(git ls-files --others --exclude-standard -- docs | head -1)" ]; then
  echo "PREPUSH NOTE: untracked files under docs/ are not scanned by the document checks; git add them first:"; git ls-files --others --exclude-standard -- docs | head -5
fi

fail() { echo "PREPUSH FAIL: $1"; exit 1; }

echo "== MOBI contract copies byte-identical"
for c in ERC1056Registry MOBIVIDRegistry MOBIVIDRegistryV2; do
  cmp -s "1_blockchain-identity/contracts/MOBI/$c.sol" "cv2x-testbed/contracts/$c.sol" || fail "$c.sol differs between 1_blockchain-identity/contracts/MOBI and cv2x-testbed/contracts"
done

echo "== feature-asymmetry matrix up to date"
python3 4_comparison-framework/feature-matrix/make_feature_matrix.py > /dev/null || fail "feature matrix generator"
git diff --quiet -- docs/FEATURE_ASYMMETRY_MATRIX.md || fail "docs/FEATURE_ASYMMETRY_MATRIX.md is stale: commit the regenerated file"

CHECKS=(
  "docs/figures/make_dashboard_data.py --check"
  "docs/testing/build_register.py --check"
  "docs/testing/check_docs_numbers.py"
  "docs/testing/check_claims.py --check"
  "docs/presentation/make_presentation.py --check"
  "docs/testing/check_stamps.py --check-coverage"
  "docs/phase2/build_phase2.py --check"
  "docs/phase2/focus/make_focus_figures.py --check"
  "docs/phase2/focus/F3_interaction_modes/classify_modes.py --check"
  "docs/testing/gas_charter.py --check"
  "docs/testing/latency_charter.py --check"
  "docs/figures/make_result_cards.py --check"
  "docs/tdp/make_vcrm.py --check"
  "docs/tdp/make_fmeca.py --check"
  "docs/tdp/make_blueprints.py --check"
)
for c in "${CHECKS[@]}"; do
  echo "== $c"
  python3 $c > /dev/null || fail "$c"
done

if [ -L cv2x-testbed/node_modules ] || [ "${PREPUSH_TESTBED:-}" = "1" ]; then
  echo "== testbed artifacts match a fresh compile (CI's node_modules)"
  (cd cv2x-testbed && node scripts/check_artifacts_fresh.js > /dev/null) || fail "cv2x-testbed artifacts are stale; rebuild with cv2x-testbed/node_modules linked to 1_blockchain-identity/node_modules"
else
  echo "== testbed artifact check skipped (link cv2x-testbed/node_modules -> ../1_blockchain-identity/node_modules, or set PREPUSH_TESTBED=1, to run it)"
fi

if [ "${1:-}" = "--probe" ]; then
  echo "== probe: break a MOBI copy and expect the guard to fire"
  cp cv2x-testbed/contracts/MOBIVIDRegistryV2.sol /tmp/prepush_probe.sol
  echo "// probe" >> cv2x-testbed/contracts/MOBIVIDRegistryV2.sol
  if bash "$0" > /dev/null 2>&1; then cp /tmp/prepush_probe.sol cv2x-testbed/contracts/MOBIVIDRegistryV2.sol; fail "probe: the guard did not fire"; fi
  cp /tmp/prepush_probe.sol cv2x-testbed/contracts/MOBIVIDRegistryV2.sol
  echo "probe: guard fired and the copy is restored"
fi

echo "PREPUSH OK"
