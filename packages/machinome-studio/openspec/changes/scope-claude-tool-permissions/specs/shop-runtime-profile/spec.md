## MODIFIED Requirements

### Requirement: Backend runtime choices are explicit per agent
Each profile agent SHALL declare a model, effort, and tool policy for Claude.
Model and effort SHALL be defaults: they supply the model and effort for any
agent whose active-project selection does not name one. The tool policy SHALL
apply always. Model and effort SHALL be either a value the backend can enforce
or the literal `inherit`.

Each Claude runtime table SHALL declare a concrete tool list. `inherit` SHALL be
rejected for a Claude tool policy, because a session whose tool set the backend
does not bound cannot satisfy `scoped-agent-tools`.

A Claude runtime table SHALL NOT declare a permission policy. The declared tool
list is the entire authority a role session holds, and no profile declaration
SHALL be able to disable the runtime's permission checking.

The loader SHALL validate every declared backend table on every run rather than
only the table for one selected backend, because a run may open several
backends. Validation SHALL fail if an agent lacks a Claude entry, names an
unsupported concrete value, declares a field the backend does not accept, or
requests a control that backend cannot enforce. A backend MUST NOT silently
substitute an inherited or differently configured model, effort, or tool policy
for a concrete resolved declaration.

A profile SHALL NOT declare an OpenCode runtime table. OpenCode has no profile
default: an agent runs on OpenCode only when the active project selects it, and
its provider and model come from that selection or from the adapter's bounded
compatibility policy. A profile SHALL reject runtime tables for unsupported or
retired backends, including Hermes, Codex, and OpenCode.

#### Scenario: A complete backend mapping is selected
- **WHEN** the Builder profile is loaded and the project selects no runtime for Builder
- **THEN** Builder opens on Claude with the model, effort, and tool policy that profile declares for Claude

#### Scenario: A project model overrides a profile default
- **WHEN** the active project selects a Claude model without a reasoning level for an agent whose profile declares a different Claude model
- **THEN** the agent opens with the project's model and the profile's effort and tool policy

#### Scenario: A project reasoning level overrides a profile default
- **WHEN** the active project selects a model and reasoning level for an agent whose profile declares a different effort
- **THEN** the agent opens with the project's model and reasoning level and the profile's tool policy

#### Scenario: A Claude tool policy is concrete
- **WHEN** a shipped profile agent resolves to the Claude backend
- **THEN** it resolves a concrete declared tool list alongside its model and
  effort, and holds no authority beyond the floor tools that list resolves to

#### Scenario: A Claude tool policy is inherited
- **WHEN** a Claude runtime table declares `tools = "inherit"`
- **THEN** profile validation fails before any project or runtime side effect

#### Scenario: A Claude runtime table declares a permission policy
- **WHEN** a Claude runtime table declares `permission`, whether `manual`,
  `autonomous`, or any other value
- **THEN** profile validation fails before any project or runtime side effect

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
- **WHEN** a backend cannot enforce a concrete model, effort, or tool value resolved for an agent
- **THEN** the runtime rejects that combination rather than silently inheriting
