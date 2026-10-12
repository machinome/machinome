## 1. Lock the breaking contract

- [x] 1.1 Add and run focused tests proving Hermes is rejected by backend selection and no longer required by profile manifests; retain the red result as evidence before implementation.

## 2. Remove the Hermes runtime surface

- [x] 2.1 Remove Hermes from CLI choices, backend/profile registries, strict profile validation, and built-in profile manifests.
- [x] 2.2 Delete the Hermes ACP adapter and remove Hermes-specific commentary from the remaining backend seam.

## 3. Remove Hermes test infrastructure

- [x] 3.1 Delete the fake ACP server and Hermes-only acceptance, factory, product-identity, and runtime-profile tests without weakening shared backend coverage.
- [x] 3.2 Run the focused backend, profile, orchestrator, lifecycle, and product-identity suites.

## 4. Record the current product and architecture

- [x] 4.1 Add ADR 0016, supersede ADR 0007, amend ADRs 0006 and 0011, and update the ADR index.
- [x] 4.2 Update the reference architecture, README, running-shop guidance, reference design, and remaining active source commentary to describe only Codex, Claude, and OpenCode.
- [x] 4.3 Sync all four delta specifications into their baseline specifications.

## 5. Validate and close the implementation

- [x] 5.1 Run the complete automated test suite and strict OpenSpec validation.
- [x] 5.2 Scan tracked active product surfaces for Hermes references and verify every survivor is an intentional historical record.
