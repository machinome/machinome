## MODIFIED Requirements

### Requirement: The shop floor builds the selected functional model before opening
When opening a named project shop floor, the system SHALL use a solid-node CLI
one-shot build of the project's default `root` functional model before starting
the Floor service or agent runtime. The build SHALL produce a complete
`_build` viewer snapshot and all referenced model files before Floor can be
declared open. The floor service SHALL serve only that completed snapshot and
its referenced model files. It SHALL NOT import, execute, reload, inspect, or
serve project Python source.

#### Scenario: A named project has a buildable default model
- **WHEN** the maker opens the shop for a named project whose default `root` model builds successfully
- **THEN** the system completes one solid-node CLI build and makes the complete `_build` model artifacts available before starting Floor

#### Scenario: The build command succeeds without a complete publication
- **WHEN** the initial build does not leave a readable viewer snapshot and every referenced model artifact
- **THEN** the system treats preparation as failed and does not start Floor or its agents

#### Scenario: The maker first opens the reported browser location
- **WHEN** the system has reported a named project shop as open
- **THEN** the browser can retrieve the already-validated initial viewer snapshot rather than receiving a no-build response
