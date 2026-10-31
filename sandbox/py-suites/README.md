# Python layers L3 and L4

Run everything on the Python side with one command from the repository root:

    sandbox/py-suites/run.sh

- `L3-ssi/` — the external W3C DID test-suite record regression (335/336 floor) and the
  internal compliance checker as a test (94.3 floor), alongside the existing SSI-layer
  suites in `2_w3c-ssi-layer/` (VC 28, MOBI VID 23, VIN cipher 9) which the ini collects.
- `L4-exemplar-interactions/` — experiment records of record checked for presence,
  environment header and row structure (numbers are never asserted across hosts);
  the twelve lifecycle use cases of `cv2x-testbed/scripts/test_use_cases.py` run
  in-process as one test each (no chain); and a V2V harness smoke that runs
  `cv2x-testbed/sumo/sumo_identity_integration.py --simulate` for 10 vehicles / 2 s
  with `--results` pointed at a temp dir (committed results are never rewritten).
