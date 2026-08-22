## ADDED Requirements

### Requirement: The profile tool vocabulary names an OpenSpec capability

The profile tool vocabulary SHALL include `OpenSpec`, resolving to the floor's
OpenSpec tools. It SHALL be a capability of its own rather than a member of any
existing capability, so that a profile grants it only by naming it.

The `builder` profile SHALL declare `OpenSpec` for Builder. The `fordesmac`
profile SHALL NOT declare it for any agent, and no Fordesmac session SHALL
reach an OpenSpec tool.

#### Scenario: Builder opens with the OpenSpec capability

- **WHEN** a Builder session opens
- **THEN** the floor's OpenSpec tools are among its reachable tools

#### Scenario: A Fordesmac role opens

- **WHEN** any Fordesmac role session opens
- **THEN** no OpenSpec tool is advertised or callable in that session,
  including for roles that declare every other capability

#### Scenario: A profile names an unknown capability

- **WHEN** a profile declares a tool capability outside the vocabulary
- **THEN** profile validation fails before any project or runtime side effect
