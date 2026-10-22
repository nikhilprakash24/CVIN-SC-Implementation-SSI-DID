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
# ICD gate: a fake backticked identifier appended to section 7 must be reported as not in source
cp docs/tdp/TDP-003_INTERFACE_CONTROL_DOCUMENT.md docs/tdp/TDP-003.probe
python3 - <<'PY'
import pathlib
p = pathlib.Path("docs/tdp/TDP-003_INTERFACE_CONTROL_DOCUMENT.md"); s = p.read_text()
i = s.index("## 8.")
p.write_text(s[:i] + "Probe token: `no_such_identifier_xyz`.\n\n" + s[i:])
PY
if python3 docs/tdp/check_icd.py --check >/dev/null 2>&1; then echo "PROBE FAILED: check_icd.py passed on a fake identifier"; fail=1; else echo "probe ok: check_icd.py fails on a fake identifier"; fi
mv docs/tdp/TDP-003.probe docs/tdp/TDP-003_INTERFACE_CONTROL_DOCUMENT.md
python3 docs/tdp/check_icd.py --check >/dev/null || { echo "PROBE: check_icd.py fails on the restored document"; fail=1; }
exit $fail
