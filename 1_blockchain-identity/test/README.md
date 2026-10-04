# Layered test suites (plan S3–S6) — Hardhat layers

Hardhat collects every `*.js` under this directory (`paths.tests: ./test`). The files
must live inside the project so they can resolve `chai`/Hardhat; `sandbox/suites` is a
symlink to this directory so the sandbox sees the same layers.

- `L1-identity-mechanisms/` — the uniform cross-option suite driven by the sandbox
  adapters (S3; run alone with `npx hardhat test test/L1-identity-mechanisms/*.test.js` —
  Hardhat's test task takes files, not a directory): create, controller change, key/delegate, attribute, claim, revoke,
  transfer, signed op — asserting behaviour where an option supports it and *recording*
  `NotApplicable` otherwise. Its N/A table is the asymmetry table produced by tests.
- `L2-identity-system/per-option/` — the per-contract suites, moved here unchanged on
  2026-10-04 (S4); `L2-identity-system/security/` — the 68-scenario harness. Registries,
  roles, lookups, history, signed operations and attacks, per option.
- L3 (SSI, pytest) and L4 (exemplar interactions, pytest) live under `sandbox/suites/`'s
  Python siblings — see `sandbox/README.md`.
