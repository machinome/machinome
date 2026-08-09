# shop-runtime-profile Specification

## Purpose

Define trusted declarative packages that select shop runtime topology, prompts, skills, and enforceable backend policy before project or runtime side effects.

## Requirements

### Requirement: A run selects one trusted runtime profile
The shop launcher SHALL accept `--profile <profile-id>` and SHALL select
`builder` when the option is omitted. It SHALL resolve a selected profile only
from `profiles/<profile-id>/profile.toml` beneath the primary shop checkout.
The broker-only and orchestrated entry points SHALL use the same profile
selection contract. A project repository MUST NOT supply or override a runtime
profile.

#### Scenario: The default profile is selected
- **WHEN** the user opens a shop without `--profile`
- **THEN** the runtime selects the repository-owned `builder` profile

#### Scenario: The delegated profile is selected
- **WHEN** the user opens a shop with `--profile fordesmac`
- **THEN** the runtime selects the repository-owned `fordesmac` profile

#### Scenario: An unknown or escaping profile is selected
- **WHEN** `--profile` does not identify a valid lowercase kebab-case directory directly beneath `profiles/`
- **THEN** the runtime exits with an error before preparing a project, binding a listener, or starting a backend

### Requirement: A profile explicitly declares its complete standing topology
A profile SHALL use the supported strict TOML schema to declare its schema
version, human display label, exactly one user-facing agent, work mode, and all
standing agents. Each agent SHALL have a unique stable ID, unique display
label, contained prompt path, assignment targets, reporting parent when
applicable, and runtime settings for every supported backend. The loader SHALL
reject unknown schema keys, undeclared references, inconsistent assignment and
report edges, cycles, more or fewer than one user-facing agent, and topology
that is invalid for the declared work mode.

Every declared agent SHALL be standing. The profile schema SHALL NOT provide
optional, ephemeral, or dynamically spawned agents.

#### Scenario: A valid direct profile is loaded
- **WHEN** a profile declares one user-facing agent in direct mode with no assignment or report edges
- **THEN** validation returns that one-agent standing topology

#### Scenario: A valid delegated profile is loaded
- **WHEN** a profile declares one root user-facing agent and internally consistent assign/report edges to standing specialists in delegated mode
- **THEN** validation returns that complete standing topology

#### Scenario: An authority edge is inconsistent
- **WHEN** an agent reports to another agent that is not declared to assign it
- **THEN** profile validation fails before any project or runtime side effect

#### Scenario: An unknown key is present
- **WHEN** a profile contains a misspelled or unsupported schema key
- **THEN** profile validation fails rather than ignoring the key

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

#### Scenario: A profile exposes a shared shop skill
- **WHEN** `profiles/builder/skills/solid-node` is an individual symlink resolving to `shop-skills/solid-node`
- **THEN** a Builder prompt that declares `solid-node` passes skill validation

#### Scenario: A prompt names an unavailable skill
- **WHEN** an agent prompt declares a skill not present in its profile's `skills/` directory
- **THEN** profile validation fails before starting the project or runtime

#### Scenario: A skill link escapes its runtime namespace
- **WHEN** a profile skill link resolves into repository `skills/`, another profile, or any location outside `shop-skills/<one-skill>`
- **THEN** profile validation fails

### Requirement: Backend runtime choices are explicit per agent
Each profile agent SHALL declare a model, effort, and tool policy for Codex,
Claude, and Hermes. Each setting SHALL be either a value the backend can
enforce or the literal `inherit`. Each Claude runtime table SHALL additionally
declare `permission` as either `manual` or `autonomous`; no Codex or Hermes
runtime table SHALL declare that field. Selecting a backend SHALL fail
validation if an agent lacks that backend entry, names an unsupported concrete
value, or requests a control that backend cannot enforce. A backend MUST NOT
silently substitute an inherited or differently configured model, effort,
tool, or Claude permission policy for a concrete profile declaration.

The initial profiles SHALL explicitly inherit Hermes model, effort, and tools.
Every shipped Claude role SHALL explicitly declare `permission =
"autonomous"`.

#### Scenario: A complete backend mapping is selected
- **WHEN** the Builder profile is selected with the Codex backend
- **THEN** Builder opens with the model, effort, and tool policy declared for Codex by that profile

#### Scenario: A Claude profile selects autonomous execution
- **WHEN** a shipped profile is selected with the Claude backend
- **THEN** every declared role resolves its explicit `autonomous` permission
  policy along with its model, effort, and available tools

#### Scenario: Hermes intentionally inherits process configuration
- **WHEN** either initial profile is selected with the Hermes backend
- **THEN** every agent explicitly inherits model, effort, and tools from the configured ACP process

#### Scenario: A concrete control cannot be enforced
- **WHEN** the selected backend cannot enforce a concrete model, effort, tool,
  or Claude permission value declared for an agent
- **THEN** the runtime rejects that profile/backend combination rather than
  silently inheriting

#### Scenario: A Claude permission policy is omitted or invalid
- **WHEN** a Claude runtime table omits `permission` or names a value other
  than `manual` or `autonomous`
- **THEN** profile validation fails before any project or runtime side effect

### Requirement: Profile validation precedes every project side effect
The launcher SHALL complete profile filesystem, schema, prompt, skill,
topology, and selected-backend validation before it creates or validates a
project repository, invokes `solid`, binds an HTTP listener, or starts an agent
backend. A validation error SHALL identify the profile and invalid field or
path.

#### Scenario: An invalid profile is used with a missing project
- **WHEN** the selected profile is invalid and the named project does not exist
- **THEN** the runtime reports the profile error and does not scaffold or initialize the project

### Requirement: The shop ships Builder and Fordesmac profiles
The `builder` profile SHALL declare one user-facing Builder in direct mode. The
`fordesmac` profile SHALL declare standing Foreman, Designer, Machinist, and
Librarian agents in delegated mode; Foreman SHALL be user-facing, SHALL be the
only agent permitted to assign the three specialists, and SHALL be the only
recipient of their reports. Both profiles SHALL use `Maker` as their initial
human display label and SHALL be valid with Codex, Claude, and Hermes.

#### Scenario: Builder topology is loaded
- **WHEN** the `builder` profile is validated
- **THEN** its complete standing roster contains only user-facing Builder

#### Scenario: Fordesmac topology is loaded
- **WHEN** the `fordesmac` profile is validated
- **THEN** its complete standing roster contains Foreman, Designer, Machinist, and Librarian with only the declared Foreman-specialist assignment and report edges

### Requirement: Builder tests a new leaf only after that leaf exists
Builder SHALL use a disassembled-leaf-first workflow for each new leaf. It
SHALL first create and wire the leaf into the model in a deliberately
disassembled position, then write the first red fit or assembly test against
that existing leaf, and then assemble or refine the leaf until the test turns
green. The first red state MUST be the existing leaf's incorrect relationship;
it MUST NOT be a missing class, node, function, or artifact. The workflow MUST
NOT require a separate visual-inspection action between creating the
disassembled leaf and writing that first test; visual evidence remains part of
completion.

#### Scenario: An existing disassembled leaf produces the first red result
- **WHEN** Builder adds a new leaf to a project slice
- **THEN** the leaf exists and is wired in a disassembled position before Builder runs the first fit or assembly test that fails on its relationship

#### Scenario: Missing implementation is not accepted as the first red state
- **WHEN** the first new test fails because the leaf class, node, function, or artifact does not exist
- **THEN** Builder has not satisfied the profile's required first-red workflow

#### Scenario: No inspection gate interrupts the red-first sequence
- **WHEN** Builder has created and wired the disassembled leaf
- **THEN** Builder may immediately write and run its first fit or assembly test without a mandatory visual-inspection action
