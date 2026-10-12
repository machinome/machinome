## ADDED Requirements

### Requirement: A successful observed build refreshes the project screenshot
After a shop-owned project build succeeds, the shop SHALL request a best-effort
refresh of the canonical project screenshot. While a project session is open,
the shop SHALL also request that refresh after observing the successful
published document from a build owned by another process. Screenshot refresh
failure SHALL NOT alter build status or be represented as a model-build
failure.

#### Scenario: The source watcher builds successfully
- **WHEN** a source-triggered build exits successfully
- **THEN** the shop requests a refresh of `<project>/screenshot.png`

#### Scenario: The scoped build tool builds successfully
- **WHEN** `solid_build` reports a successful project build
- **THEN** the shop requests a refresh of `<project>/screenshot.png` before returning its result

#### Scenario: An external build publishes successfully
- **WHEN** a build not owned by the shop publishes `viewer.json` while the project session is open
- **THEN** the shop requests a refresh of `<project>/screenshot.png`

#### Scenario: A build fails
- **WHEN** a project build fails
- **THEN** the failure retains its existing build-reporting semantics and the shop does not replace the prior screenshot with output for that failed build
