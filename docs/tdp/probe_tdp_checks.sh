#!/usr/bin/env bash
# Probe that the three TDP document checks fire (guide rule 1.3.11: a guard never seen to trip is not evidence).
# After-action report 20, step T7. Run from the repository root, on a tree where the generated documents are current.
# For each generator: tamper one byte of its output, expect --check to exit 1, restore the file from git, expect 0.
set -u
cd "$(dirname "$0")/../.."
fail=0
probe() {
  local script="$1" target="$2"
  python3 "$script" --check >/dev/null || { echo "PROBE: $script --check fails on a clean tree; fix that first"; fail=1; return; }
  cp "$target" "$target.probe"
  printf '\n<!-- tamper -->\n' >> "$target"
  if python3 "$script" --check >/dev/null 2>&1; then
    echo "PROBE FAILED: $script --check passed on a tampered $target"; fail=1
  else
    echo "probe ok: $script --check fails on a tampered $target"
  fi
  mv "$target.probe" "$target"
  python3 "$script" --check >/dev/null || { echo "PROBE: restore of $target did not return a clean check"; fail=1; }
}
probe docs/tdp/make_vcrm.py docs/tdp/TDP-005_VERIFICATION_CROSS_REFERENCE_MATRIX.md
probe docs/tdp/make_fmeca.py docs/tdp/TDP-006_FMECA.md
probe docs/tdp/make_blueprints.py docs/tdp/drawings/DWG-003.svg
exit $fail
