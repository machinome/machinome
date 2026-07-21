## ADDED Requirements

### Requirement: The shop validates the model before it becomes open
When Codex opens a project shop floor, the system SHALL build the project's
selected project-local functional model before making the shop floor available at its
browser location. If that build cannot produce a model, the system SHALL tell
the maker why the shop was not opened.

#### Scenario: The initial model build succeeds
- **WHEN** Codex opens a shop for a project with a buildable selected model path
- **THEN** Codex starts the shop-floor service and provides its browser location only after the model is ready for inspection

#### Scenario: The initial model build fails
- **WHEN** Codex opens a shop and the selected model is missing or cannot be built
- **THEN** Codex does not present the browser location as an open shop and reports the build failure
