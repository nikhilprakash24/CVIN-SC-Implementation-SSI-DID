#!/usr/bin/env bash
# Probe for docs/testing/check_claims.py (WM-2 A5): the check must pass on the tree and fail on
# (i) a bold number edited in a V row's claim, (ii) a source removed from claims.yaml,
# (iii) an entry for a row that does not exist. Every edit is undone on exit.
set -u
cd "$(dirname "$0")/../.."
REG=docs/MEASUREMENT_CONDITIONS.md; CL=docs/testing/claims.yaml
cp "$REG" /tmp/probe_reg.md; cp "$CL" /tmp/probe_claims.yaml
restore() { cp /tmp/probe_reg.md "$REG"; cp /tmp/probe_claims.yaml "$CL"; }
trap restore EXIT
fail() { echo "PROBE FAIL: $1"; exit 1; }

python3 docs/testing/check_claims.py --check > /dev/null || fail "the check fails on the unmodified tree"

# (i) edit the first bold number of row #25's claim (the 33.7x spread's create value)
python3 - <<'EOF'
import re
p = "docs/MEASUREMENT_CONDITIONS.md"; L = open(p).read().split("\n")
for i, l in enumerate(L):
    if l.startswith("| 25 |"):
        L[i] = l.replace("**1,757,881**", "**1,757,882**", 1); break
open(p, "w").write("\n".join(L))
EOF
python3 docs/testing/check_claims.py --check > /dev/null && fail "(i) an edited bold number passed"
restore

# (ii) drop every source of row #27
python3 - <<'EOF'
import yaml
p = "docs/testing/claims.yaml"; d = yaml.safe_load(open(p))
for e in d["claims"]:
    if e["row"] == 27: e["sources"] = []
yaml.safe_dump(d, open(p, "w"), sort_keys=False, width=200, allow_unicode=True)
EOF
python3 docs/testing/check_claims.py --check > /dev/null && fail "(ii) a V row without sources passed"
restore

# (iii) an entry for a row that does not exist
printf -- "- id: c999-probe\n  row: 999\n" >> "$CL"
python3 docs/testing/check_claims.py --check > /dev/null && fail "(iii) an entry for a missing row passed"
restore

echo "probe ok: check_claims.py fails on an edited bold number, a V row without sources and an unknown row"
