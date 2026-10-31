#!/usr/bin/env bash
# One command for the Python side: L3 + L4 layers plus the existing SSI-layer suites.
set -euo pipefail
cd "$(dirname "$0")/../.."
exec python3 -m pytest -c sandbox/py-suites/pytest.ini \
  sandbox/py-suites/L3-ssi sandbox/py-suites/L4-exemplar-interactions 2_w3c-ssi-layer "$@"
