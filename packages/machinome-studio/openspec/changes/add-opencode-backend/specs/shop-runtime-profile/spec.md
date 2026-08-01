## MODIFIED Requirements

### Requirement: Backend runtime choices are explicit per agent
Each profile agent SHALL declare a model, effort, and tool policy for Codex,
Claude, Hermes, and OpenCode. Each setting SHALL be either a value the backend
can enforce or the literal `inherit`. Selecting a backend SHALL fail validation
if an agent lacks that backend entry, names an unsupported concrete value, or
requests a control that backend cannot enforce. A backend MUST NOT silently
substitute an inherited or differently configured model for a concrete profile
declaration.

The initial profiles SHALL explicitly inherit Hermes model, effort, and tools.
They SHALL explicitly inherit OpenCode model and effort and SHALL declare
concrete OpenCode tool policy for every agent.

#### Scenario: A complete backend mapping is selected
- **WHEN** the Builder profile is selected with the Codex backend
- **THEN** Builder opens with the model, effort, and tool policy declared for Codex by that profile

#### Scenario: Hermes intentionally inherits process configuration
- **WHEN** either initial profile is selected with the Hermes backend
- **THEN** every agent explicitly inherits model, effort, and tools from the configured ACP process

#### Scenario: OpenCode intentionally inherits provider choice
- **WHEN** either initial profile is selected with the OpenCode backend
- **THEN** every agent uses the isolated OpenCode runtime's authenticated default model and effort while enforcing its profile-declared OpenCode tool policy

#### Scenario: A concrete control cannot be enforced
- **WHEN** the selected backend cannot enforce a concrete model, effort, or tool value declared for an agent
- **THEN** the runtime rejects that profile/backend combination rather than silently inheriting

### Requirement: The shop ships Builder and Fordesmac profiles
The `builder` profile SHALL declare one user-facing Builder in direct mode. The
`fordesmac` profile SHALL declare standing Foreman, Designer, Machinist, and
Librarian agents in delegated mode; Foreman SHALL be user-facing, SHALL be the
only agent permitted to assign the three specialists, and SHALL be the only
recipient of their reports. Both profiles SHALL use `Maker` as their initial
human display label and SHALL be valid with Codex, Claude, Hermes, and OpenCode.

#### Scenario: Builder topology is loaded
- **WHEN** the `builder` profile is validated
- **THEN** its complete standing roster contains only user-facing Builder

#### Scenario: Fordesmac topology is loaded
- **WHEN** the `fordesmac` profile is validated
- **THEN** its complete standing roster contains Foreman, Designer, Machinist, and Librarian with only the declared Foreman-specialist assignment and report edges
