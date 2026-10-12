## MODIFIED Requirements

### Requirement: Backend runtime choices are explicit per agent
Each profile agent SHALL declare a model, effort, and tool policy for Codex and
Claude. Each setting SHALL be either a value the backend can enforce or the
literal `inherit`. Each Claude runtime table SHALL additionally declare
`permission` as either `manual` or `autonomous`; Codex runtime tables SHALL NOT
declare that field. Selecting a profile-explicit backend SHALL fail validation
if an agent lacks that backend entry, names an unsupported concrete value, or
requests a control that backend cannot enforce. A backend MUST NOT silently
substitute an inherited or differently configured model, effort, tool, or
Claude permission policy for a concrete profile declaration.

OpenCode SHALL remain selectable without a profile runtime table under its
bounded adapter-owned compatibility policy. A profile SHALL reject runtime
tables for unsupported or retired backends, including Hermes.

Every shipped Claude role SHALL explicitly declare `permission =
"autonomous"`.

#### Scenario: A complete backend mapping is selected
- **WHEN** the Builder profile is selected with the Codex backend
- **THEN** Builder opens with the model, effort, and tool policy declared for Codex by that profile

#### Scenario: A Claude profile selects autonomous execution
- **WHEN** a shipped profile is selected with the Claude backend
- **THEN** every declared role resolves its explicit `autonomous` permission policy along with its model, effort, and available tools

#### Scenario: OpenCode uses adapter-owned compatibility policy
- **WHEN** either initial profile is selected with the OpenCode backend
- **THEN** the profile is valid without an OpenCode runtime table and the adapter applies its bounded compatibility policy

#### Scenario: A retired backend table is rejected
- **WHEN** a profile agent declares a Hermes runtime table
- **THEN** profile validation rejects the unsupported backend key

#### Scenario: A concrete control cannot be enforced
- **WHEN** the selected backend cannot enforce a concrete model, effort, tool, or Claude permission value declared for an agent
- **THEN** the runtime rejects that profile/backend combination rather than silently inheriting

#### Scenario: A Claude permission policy is omitted or invalid
- **WHEN** a Claude runtime table omits `permission` or names a value other than `manual` or `autonomous`
- **THEN** profile validation fails before any project or runtime side effect

### Requirement: The shop ships Builder and Fordesmac profiles
The `builder` profile SHALL declare one user-facing Builder in direct mode. The
`fordesmac` profile SHALL declare standing Foreman, Designer, Machinist, and
Librarian agents in delegated mode; Foreman SHALL be user-facing, SHALL be the
only agent permitted to assign the three specialists, and SHALL be the only
recipient of their reports. Both profiles SHALL use `Maker` as their initial
human display label and SHALL be valid with Codex, Claude, and OpenCode.

#### Scenario: Builder topology is loaded
- **WHEN** the `builder` profile is validated
- **THEN** its complete standing roster contains only user-facing Builder

#### Scenario: Fordesmac topology is loaded
- **WHEN** the `fordesmac` profile is validated
- **THEN** its complete standing roster contains Foreman, Designer, Machinist, and Librarian with only the declared Foreman-specialist assignment and report edges
