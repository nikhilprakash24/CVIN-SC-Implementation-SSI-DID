# Python layers L3 and L4

Run everything on the Python side with one command from the repository root:

    sandbox/py-suites/run.sh

- `L3-ssi/` — the external W3C DID test-suite record regression (335/336 floor) and the
  internal compliance checker as a test (94.3 floor), alongside the existing SSI-layer
  suites in `2_w3c-ssi-layer/` (VC 28, MOBI VID 23, VIN cipher 9) which the ini collects.
- `L4-exemplar-interactions/` — experiment records of record checked for presence,
  environment header and row structure (numbers are never asserted across hosts);
  the lifecycle use cases as tests and the V2V harness smoke follow (plan S6).
