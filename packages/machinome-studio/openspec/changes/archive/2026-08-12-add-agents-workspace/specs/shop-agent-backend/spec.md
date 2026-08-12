## ADDED Requirements

### Requirement: A backend exposes bounded runtime control for an existing role
The portable backend contract SHALL report whether a role supports a
context-preserving model-and-reasoning update, SHALL provide backend-owned model
choices for that role, and SHALL apply a supported update to the same persistent
role session. The operation SHALL preserve backend and provider and SHALL reject
unsupported model or reasoning combinations.

#### Scenario: Codex changes a later turn
- **WHEN** the orchestrator applies a supported runtime to an idle Codex role
- **THEN** Codex keeps the existing thread and supplies the new model and effort on every later turn start

#### Scenario: OpenCode changes a later prompt
- **WHEN** the orchestrator applies a supported runtime to an idle OpenCode role
- **THEN** OpenCode keeps the existing session and supplies the new provider-bounded model and variant on every later prompt

#### Scenario: Claude has only launch-time controls
- **WHEN** the Claude adapter has no verified context-preserving switch
- **THEN** it reports runtime mutation unsupported and does not restart the role process

### Requirement: OpenCode model choices come from the active provider catalogue
The OpenCode backend SHALL query the live authenticated server's provider/model
catalogue and expose only models belonging to the role's current provider. It
SHALL expose only reasoning variants supported by each choice and SHALL NOT use
catalogue selection to change the provider.

#### Scenario: The provider catalogue contains several providers
- **WHEN** an OpenCode role uses provider `anthropic` and the server reports Anthropic and OpenAI models
- **THEN** the role catalogue contains only Anthropic model choices and their reported variants

#### Scenario: The provider catalogue is unavailable
- **WHEN** OpenCode cannot retrieve its catalogue
- **THEN** the current runtime remains displayed, mutation is unavailable, and the role session continues running

### Requirement: Backends publish portable activity rather than native frames
Each backend SHALL convert the native events it can observe into the portable
agent activity contract and SHALL NOT expose backend-native session, message,
turn, tool-use, or part identifiers to the broker or browser.

#### Scenario: Native identifiers correlate a tool result
- **WHEN** an adapter uses native identifiers to join a tool start and result
- **THEN** it emits one stable portable activity identity and omits the native identifiers from browser state
