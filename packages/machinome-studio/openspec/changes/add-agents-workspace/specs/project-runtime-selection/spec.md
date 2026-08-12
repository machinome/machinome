## ADDED Requirements

### Requirement: An idle session may override its selected model and reasoning
The maker MAY replace one manifested agent's model and reasoning level for its
current session only when the backend and provider remain unchanged and the
agent is authoritatively idle. Model and reasoning SHALL be applied as one
validated runtime value and SHALL affect the next delivery immediately without
changing the agent's session identity or conversation context. The shop SHALL
NOT offer a queued, next-assignment, backend-migration, or provider-migration
mode.

#### Scenario: An idle Codex agent changes model
- **WHEN** the maker applies a supported Codex model and reasoning level to an idle Codex agent
- **THEN** that agent's next turn uses both new values in its existing persistent thread

#### Scenario: An idle OpenCode agent changes model
- **WHEN** the maker applies a model and variant from the current OpenCode provider's catalogue to an idle OpenCode agent
- **THEN** that agent's next prompt uses both new values in its existing persistent session

#### Scenario: A request changes backend or provider
- **WHEN** a runtime update names a different backend or OpenCode provider from the active session
- **THEN** the shop rejects it without changing live or project runtime

#### Scenario: A Claude session cannot preserve context
- **WHEN** the active backend cannot prove a context-preserving in-session runtime change
- **THEN** the workspace displays its runtime read-only and the API rejects mutation

### Requirement: A live runtime update may be recorded in project configuration
The runtime control SHALL default to writing an accepted change to the active
project's `[tool.solid-node-studio.agents]` table and SHALL let the maker
explicitly uncheck that option for a session-only override. A persisted change
SHALL write the complete existing-backend/provider plus new-model/reasoning
selection using the accepted grammar, preserve unrelated TOML content and
comments, and atomically replace only an unchanged configuration revision. The
shop SHALL NOT read or write `[tool.solid-node]`.

#### Scenario: The default persisted update succeeds
- **WHEN** the maker applies an idle runtime update with the default persistence option
- **THEN** the live session changes immediately and the project agent key records the same complete selection in `pyproject.toml`

#### Scenario: The maker chooses a temporary override
- **WHEN** the maker unchecks persistence and applies an idle runtime update
- **THEN** the live session changes and reopening the project again resolves from the unchanged `pyproject.toml`

#### Scenario: Project configuration changed concurrently
- **WHEN** `pyproject.toml` no longer has the revision displayed with the controls
- **THEN** the shop rejects the update without overwriting the file or changing the live runtime

#### Scenario: Project and framework tables coexist
- **WHEN** persisted runtime is written beside an existing `[tool.solid-node]` table and other project configuration
- **THEN** only the selected `[tool.solid-node-studio.agents]` key changes and all unrelated content remains semantically and textually preserved
