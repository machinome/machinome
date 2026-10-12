## MODIFIED Requirements

### Requirement: A run selects one trusted runtime profile
The shop SHALL resolve the profile for a session from exactly one of two
sources, in this order of precedence: the project's declared profile when it
declares one, and otherwise the shop default `openspec-builder`. It SHALL resolve a
selected profile only from `profiles/<profile-id>/profile.toml` beneath the
primary shop checkout. The broker-only and orchestrated entry points SHALL use
the same profile selection contract. A project's declaration SHALL govern every
session of that project; the shop SHALL provide no way to open a project under a
profile it does not declare.

#### Scenario: The default profile is selected
- **WHEN** a project that declares no profile is opened
- **THEN** the shop selects the repository-owned `openspec-builder` profile

#### Scenario: The project's declared profile is selected
- **WHEN** a project that declares a profile is opened
- **THEN** the shop selects the profile that project declares

#### Scenario: An unknown or escaping profile is declared
- **WHEN** a project's declared profile does not identify a valid lowercase kebab-case directory directly beneath `profiles/`
- **THEN** the shop refuses to open that project with an error, before preparing it or starting a backend, and remains available for every other project

### Requirement: Profile prompts and skills are contained and allowlisted
Each agent prompt SHALL be a regular file contained by its profile directory.
Its frontmatter SHALL identify the same agent ID and SHALL explicitly list the
skills that agent requires. Every listed skill SHALL resolve through that
profile's `skills/<skill>/SKILL.md` allowlist.

A profile-local skill SHALL be contained by the profile. A shared skill SHALL
be exposed by an individual symlink resolving to one skill directory directly
beneath `shop-skills/`. The loader MUST reject broken links, file links,
transitive filesystem escapes, links into repository `skills/`, links into
another profile, and prompt skill names absent from the profile allowlist.
Runtime agents MUST NOT resolve skills from the repository-development
`skills/` namespace.

Every allowlisted skill SHALL describe itself: its `SKILL.md` frontmatter
SHALL declare a `name` equal to the allowlisted skill name and a non-empty
`description`, and the loader SHALL resolve that name, description, and
directory together. A skill whose frontmatter is missing, unterminated,
mismatched, or without a description SHALL fail profile validation, because a
skill that cannot be announced cannot be chosen.

#### Scenario: A profile exposes a shared shop skill
- **WHEN** `profiles/openspec-builder/skills/machinome` is an individual symlink resolving to `shop-skills/machinome`
- **THEN** a Builder prompt that declares `machinome` passes skill validation

#### Scenario: A prompt names an unavailable skill
- **WHEN** an agent prompt declares a skill not present in its profile's `skills/` directory
- **THEN** profile validation fails before starting the project or runtime

#### Scenario: A skill link escapes its runtime namespace
- **WHEN** a profile skill link resolves into repository `skills/`, another profile, or any location outside `shop-skills/<one-skill>`
- **THEN** profile validation fails

#### Scenario: An allowlisted skill does not describe itself
- **WHEN** an allowlisted skill's `SKILL.md` has no frontmatter, a `name` other
  than the allowlisted skill name, or an empty or missing `description`
- **THEN** profile validation fails before starting the project or runtime

#### Scenario: A validated skill carries its announcement
- **WHEN** a profile agent's skills are resolved
- **THEN** each resolved skill carries the name and description its `SKILL.md`
  declares alongside its directory

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
- **WHEN** the `openspec-builder` profile is loaded and the project selects no runtime for Builder
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

### Requirement: The shop ships OpenSpec and Fordesmac profiles
The `openspec-builder` profile SHALL declare one user-facing agent in direct mode,
Builder, with the agent ID `builder` and the display label
`OpenSpec Builder`; the maker meets the profile and its agent under that one
name, while the agent ID stays `builder`. The
`fordesmac` profile SHALL declare standing Foreman, Designer, Machinist, and
Librarian agents in delegated mode; Foreman SHALL be user-facing, SHALL be the
only agent permitted to assign the three specialists, and SHALL be the only
recipient of their reports. Both profiles SHALL use `Maker` as their initial
human display label and SHALL be valid with Claude and OpenCode.

#### Scenario: OpenSpec topology is loaded
- **WHEN** the `openspec-builder` profile is validated
- **THEN** its complete standing roster contains only user-facing Builder, with agent ID `builder` and label `OpenSpec Builder`

#### Scenario: Fordesmac topology is loaded
- **WHEN** the `fordesmac` profile is validated
- **THEN** its complete standing roster contains Foreman, Designer, Machinist, and Librarian with only the declared Foreman-specialist assignment and report edges

### Requirement: The profile tool vocabulary names an OpenSpec capability

The profile tool vocabulary SHALL include `OpenSpec`, resolving to the floor's
OpenSpec tools. It SHALL be a capability of its own rather than a member of any
existing capability, so that a profile grants it only by naming it.

The `openspec-builder` profile SHALL declare `OpenSpec` for Builder. The `fordesmac`
profile SHALL NOT declare it for any agent, and no Fordesmac session SHALL
reach an OpenSpec tool.

#### Scenario: Builder opens with the OpenSpec capability

- **WHEN** a Builder session of the `openspec-builder` profile opens
- **THEN** the floor's OpenSpec tools are among its reachable tools

#### Scenario: A Fordesmac role opens

- **WHEN** any Fordesmac role session opens
- **THEN** no OpenSpec tool is advertised or callable in that session,
  including for roles that declare every other capability

#### Scenario: A profile names an unknown capability

- **WHEN** a profile declares a tool capability outside the vocabulary
- **THEN** profile validation fails before any project or runtime side effect

