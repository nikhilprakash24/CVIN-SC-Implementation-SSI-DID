# CVIN-SC Identity Sandbox

Experimental environment for the CVIN-SC thesis: eight blockchain identity
systems (O1–O8) deployed against the 12-function IMinimalSSI specification,
tested by a unified compliance suite, and exercised in trace-emitting scenarios
including end-to-end secure I2I communication.

**Methodology: [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md)** · **Start here: [`docs/BRINGUP.md`](docs/BRINGUP.md)** — full bring-up sequence,
implementation status, trace schema pointer, and LFDT project integration.

Quick verify: `npm install && npx hardhat test && npx hardhat run scenarios/run_i2i.js`

## VID layer (2026-10-04)

Beside the unmodified interface: endorsement registry (`contracts/governance/`), typed credentials
(`contracts/credentials/`), off-chain credential library (`lib/vid/`), scenarios S7
(`scenarios/run_vid_minimal.js`) and S8 (`scenarios/run_vid_lifecycle.js`), tests (`test/vid.js`).
`npx hardhat test` → 19 passing. Documentation: `../docs/hda-campaign/10_VID_Build_Documentation.md`;
findings: `docs/FINDINGS.md` items 4–10.
