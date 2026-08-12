## MODIFIED Requirements

### Requirement: An idle session may override its selected model and reasoning
The maker MAY replace one manifested agent's model and reasoning level for its
current session when the agent is authoritatively idle. When its backend and
provider remain unchanged, the shop SHALL apply both values as one validated
runtime value to the existing persistent session only when that backend proves
the change preserves context. Before the role has accepted any message,
delivery, or assignment or produced any activity, the maker MAY instead select
a different backend or provider together with its model and reasoning; the shop
SHALL immediately replace that unused standing session without migrating
context. First use SHALL permanently end backend/provider replacement for that
role even after it becomes idle again. The shop SHALL NOT offer a queued or
next-assignment runtime mode.

#### Scenario: An idle Codex agent changes model
- **WHEN** the maker applies a supported Codex model and reasoning level to an idle Codex agent
- **THEN** that agent's next turn uses both new values in its existing persistent thread

#### Scenario: An idle OpenCode agent changes model
- **WHEN** the maker applies a model and variant from the current OpenCode provider's catalogue to an idle OpenCode agent
- **THEN** that agent's next prompt uses both new values in its existing persistent session

#### Scenario: A pristine role changes backend
- **WHEN** the maker applies a supported backend, provider, model, and reasoning combination before the role has accepted a message, delivery, or assignment or produced activity
- **THEN** the shop closes the unused standing handle, immediately opens that role on the selected runtime, and migrates no session context

#### Scenario: A pristine role selects OpenCode
- **WHEN** the maker selects OpenCode for a pristine role
- **THEN** provider, model, and reasoning choices are limited to combinations in OpenCode's live catalogue

#### Scenario: A used role becomes idle again
- **WHEN** a role has accepted a message, delivery, or assignment or produced activity and later returns to an idle state
- **THEN** the shop rejects a backend or provider change without changing live or project runtime

#### Scenario: A pristine Claude role changes model
- **WHEN** the maker applies a supported Claude model and reasoning level before that role's first use
- **THEN** the shop replaces the unused Claude process and applies the selection immediately

#### Scenario: A used Claude session cannot preserve context
- **WHEN** a used Claude role is idle and the maker requests a model change
- **THEN** the workspace displays its runtime read-only and the API rejects mutation

### Requirement: A live runtime update may be recorded in project configuration
The runtime control SHALL default to writing an accepted change to the active
project's `[tool.solid-node-studio.agents]` table and SHALL let the maker
explicitly uncheck that option for a session-only override. A persisted change
SHALL write the complete selected backend/provider/model/reasoning value using
the accepted grammar, preserve unrelated TOML content and comments, and
atomically replace only an unchanged configuration revision. The shop SHALL NOT
read or write `[tool.solid-node]`.

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
