## MODIFIED Requirements

### Requirement: Runtime controls expose provider before model
The Agents workspace SHALL present runtime selection in the order backend,
provider, model, and reasoning level. The provider control SHALL identify the
provider independently of the model control. Codex SHALL show `OpenAI` as its
single fixed provider, Claude SHALL show `Anthropic` as its single fixed
provider, and OpenCode SHALL show only the exact provider IDs in the live
endpoint's connected provider set. The shop SHALL NOT expose entries that exist
only in OpenCode's complete known-provider catalogue.

Changing a backend SHALL replace provider, model, and reasoning drafts with a
valid combination for that backend. Changing an OpenCode provider SHALL replace
the model and reasoning drafts with a valid combination for that provider. The
model control SHALL contain only models for the selected backend and provider.

The workspace SHALL NOT present profile-owned tools as a runtime-selection
control. Removing that presentation SHALL NOT make tool policy project- or
maker-selectable.

#### Scenario: A maker inspects a fixed-provider backend
- **WHEN** the maker selects the Codex or Claude backend
- **THEN** the provider control shows its single fixed OpenAI or Anthropic provider before the model control

#### Scenario: A maker selects an OpenCode provider
- **WHEN** a pristine agent's live OpenCode catalogue contains more than one connected provider and the maker selects one provider ID
- **THEN** the model control contains only models belonging to that exact connected provider ID

#### Scenario: OpenCode knows providers that are not configured
- **WHEN** OpenCode's live endpoint lists providers in its complete catalogue that are absent from its connected provider set
- **THEN** the provider control omits those unconnected providers and all of their models

#### Scenario: OpenCode has no configured provider
- **WHEN** OpenCode's live endpoint reports no connected providers
- **THEN** the OpenCode runtime catalogue is unavailable rather than exposing the complete known-provider catalogue

#### Scenario: An upstream selection changes
- **WHEN** the maker changes backend or OpenCode provider and the previous model or reasoning value is unavailable downstream
- **THEN** the workspace immediately selects a valid downstream model and reasoning combination

#### Scenario: A maker applies an OpenCode runtime
- **WHEN** the maker applies an OpenCode provider, model, and reasoning selection
- **THEN** the complete runtime mutation names the exact selected provider ID separately from its model ID

#### Scenario: Runtime tools are not presented as a choice
- **WHEN** the maker opens an agent's runtime controls
- **THEN** backend, provider, model, reasoning, and persistence are presented without a tools control
