## MODIFIED Requirements

### Requirement: Backend runtime choices are explicit per agent
Each profile agent SHALL declare a model, effort, tool policy, and permission
for Claude. These SHALL be defaults: they supply the model and effort for any
agent whose active-project selection does not name one, and they supply tool
policy always. Each setting SHALL be either a value the backend can enforce or
the literal `inherit`. Each Claude runtime table SHALL declare `permission` as
either `manual` or `autonomous`.

The loader SHALL validate every declared backend table on every run rather than
only the table for one selected backend, because a run may open several
backends. Validation SHALL fail if an agent lacks a Claude entry, names an
unsupported concrete value, or requests a control that backend cannot enforce. A
backend MUST NOT silently substitute an inherited or differently configured
model, effort, tool, or Claude permission policy for a concrete resolved
declaration.

A profile SHALL NOT declare an OpenCode runtime table. OpenCode has no profile
default: an agent runs on OpenCode only when the active project selects it, and
its provider and model come from that selection or from the adapter's bounded
compatibility policy. A profile SHALL reject runtime tables for unsupported or
retired backends, including Hermes, Codex, and OpenCode.

Every shipped Claude role SHALL explicitly declare `permission = "autonomous"`.

#### Scenario: A complete backend mapping is selected
- **WHEN** the Builder profile is loaded and the project selects no runtime for Builder
- **THEN** Builder opens on Claude with the model, effort, tool policy, and permission that profile declares for Claude

#### Scenario: A project model overrides a profile default
- **WHEN** the active project selects a Claude model without a reasoning level for an agent whose profile declares a different Claude model
- **THEN** the agent opens with the project's model and the profile's effort, tool policy, and permission

#### Scenario: A project reasoning level overrides a profile default
- **WHEN** the active project selects a model and reasoning level for an agent whose profile declares a different effort
- **THEN** the agent opens with the project's model and reasoning level and the profile's tool policy and permission

#### Scenario: A Claude profile selects autonomous execution
- **WHEN** a shipped profile agent resolves to the Claude backend
- **THEN** it resolves its explicit `autonomous` permission policy along with its model, effort, and available tools

#### Scenario: Every declared table is validated
- **WHEN** a profile declares an unsupported Claude value and the run selects OpenCode for every agent
- **THEN** profile validation fails rather than passing because no agent resolved to Claude

#### Scenario: An OpenCode table is rejected
- **WHEN** a profile agent declares an OpenCode runtime table
- **THEN** profile validation rejects the unsupported backend key

#### Scenario: OpenCode uses adapter-owned compatibility policy
- **WHEN** the active project selects OpenCode for an agent
- **THEN** the profile is valid without an OpenCode runtime table and the adapter applies its bounded compatibility policy

#### Scenario: A retired backend table is rejected
- **WHEN** a profile agent declares a Hermes or Codex runtime table
- **THEN** profile validation rejects the unsupported backend key

#### Scenario: A concrete control cannot be enforced
- **WHEN** a backend cannot enforce a concrete model, effort, tool, or Claude permission value resolved for an agent
- **THEN** the runtime rejects that combination rather than silently inheriting

#### Scenario: A Claude permission policy is omitted or invalid
- **WHEN** a Claude runtime table omits `permission` or names a value other than `manual` or `autonomous`
- **THEN** profile validation fails before any project or runtime side effect

### Requirement: The shop ships Builder and Fordesmac profiles
The `builder` profile SHALL declare one user-facing Builder in direct mode. The
`fordesmac` profile SHALL declare standing Foreman, Designer, Machinist, and
Librarian agents in delegated mode; Foreman SHALL be user-facing, SHALL be the
only agent permitted to assign the three specialists, and SHALL be the only
recipient of their reports. Both profiles SHALL use `Maker` as their initial
human display label and SHALL be valid with Claude and OpenCode.

#### Scenario: Builder topology is loaded
- **WHEN** the `builder` profile is validated
- **THEN** its complete standing roster contains only user-facing Builder

#### Scenario: Fordesmac topology is loaded
- **WHEN** the `fordesmac` profile is validated
- **THEN** its complete standing roster contains Foreman, Designer, Machinist, and Librarian with only the declared Foreman-specialist assignment and report edges
