# shop-runtime-profile Specification

## Purpose

Define trusted declarative packages that select shop runtime topology, prompts, skills, and enforceable backend policy before project or runtime side effects.
## Requirements
### Requirement: A run selects one trusted runtime profile
The shop SHALL resolve the profile for a session from exactly one of two
sources, in this order of precedence: the project's declared profile when it
declares one, and otherwise the shop default `fordesmac`. It SHALL resolve a
selected profile only from `profiles/<profile-id>/profile.toml` beneath the
primary shop checkout. The broker-only and orchestrated entry points SHALL use
the same profile selection contract. A project's declaration SHALL govern every
session of that project; the shop SHALL provide no way to open a project under a
profile it does not declare.

#### Scenario: The default profile is selected
- **WHEN** a project that declares no profile is opened
- **THEN** the shop selects the repository-owned `fordesmac` profile

#### Scenario: The project's declared profile is selected
- **WHEN** a project that declares a profile is opened
- **THEN** the shop selects the profile that project declares

#### Scenario: An unknown or escaping profile is declared
- **WHEN** a project's declared profile does not identify a valid lowercase kebab-case directory directly beneath `profiles/`
- **THEN** the shop refuses to open that project with an error, before preparing it or starting a backend, and remains available for every other project

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

Every allowlisted skill SHALL describe itself: its `SKILL.md` frontmatter
SHALL declare a `name` equal to the allowlisted skill name and a non-empty
`description`, and the loader SHALL resolve that name, description, and
directory together. A skill whose frontmatter is missing, unterminated,
mismatched, or without a description SHALL fail profile validation, because a
skill that cannot be announced cannot be chosen.

#### Scenario: A profile exposes a shared shop skill
- **WHEN** `profiles/builder/skills/machinome` is an individual symlink resolving to `shop-skills/machinome`
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

### Requirement: Profile validation precedes every project side effect
The launcher SHALL complete profile filesystem, schema, prompt, skill, topology,
and runtime-table validation before it creates or validates a project
repository, invokes `solid`, binds an HTTP listener, or starts an agent backend.

Because both the profile's identity and the per-agent runtime selections live in
the project, the launcher SHALL first perform a bounded, side-effect-free read of
the project's `pyproject.toml`: resolving and containment-checking the project
path and parsing that one file. That read SHALL NOT create, scaffold, initialize,
modify, or build anything, and SHALL tolerate a project that does not yet exist.
Profile resolution, profile validation, and runtime resolution SHALL all
complete before any project side effect follows. A validation error SHALL
identify the profile or project file and the invalid field or path.

#### Scenario: An invalid profile is used with a missing project
- **WHEN** the selected profile is invalid and the named project does not exist
- **THEN** the runtime reports the profile error and does not scaffold or initialize the project

#### Scenario: Reading project configuration creates nothing
- **WHEN** the launcher reads the profile and runtime selection for a project that does not yet exist
- **THEN** no directory, repository, scaffold, or build is produced by that read, the profile resolves from `--profile` or the default, and runtime resolution falls back to the profile defaults

#### Scenario: An invalid runtime selection stops the run early
- **WHEN** a project's runtime selection is malformed and the named project exists
- **THEN** the runtime reports the offending project file and value and does not invoke `solid`, bind a listener, or start a backend

#### Scenario: An unresolvable project-declared profile stops the run early
- **WHEN** a project declares a profile that does not resolve and no `--profile` is given
- **THEN** the runtime reports the offending project file and value and does not invoke `solid`, bind a listener, or start a backend

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

### Requirement: A released drawing states continuity, transmission, and body counts
Within the `fordesmac` profile, a drawing Designer releases SHALL name every
separately manufactured item the slice releases together with the number of
printed bodies it must resolve to, normally one. Wherever a component is built
from several features, the drawing SHALL state material continuity as a
contract: which named features fuse into one printed body, and the minimum weld
at each junction. For a pair that transmits motion, the drawing SHALL state the
pitch geometry, the tooth phase relation, and the backlash window; ratio and
centre distance alone MUST NOT stand as the specification of a driving pair.

#### Scenario: A component is built from several features
- **WHEN** Designer releases a drawing for a component whose features are manufactured separately, such as blades on a hub or a boss on a plate
- **THEN** the drawing names which features fuse into one printed body and the minimum overlap at each junction

#### Scenario: A drawing releases a driving pair
- **WHEN** Designer releases a drawing specifying a pair that transmits motion
- **THEN** the drawing states the pitch geometry, the backlash window, and which tooth of one member sits in which gap of the other at a named instant

#### Scenario: A drawing releases manufactured items
- **WHEN** Designer releases any drawing
- **THEN** each separately manufactured item it releases is named with the number of printed bodies it must resolve to

### Requirement: Geometric defects are caught by contracts, not by snapshots
Within the `fordesmac` profile, before declaring an increment done Machinist
SHALL render and inspect an isometric of the assembly and a view aligned with
the slice's important interface. A defect below the scale a snapshot resolves,
such as an unmade junction or a mesh whose members never touch, SHALL be
covered by a deterministic contract rather than by rendering the interface more
closely; snapshot inspection stands as evidence that the component is wired and
posed as intended.

#### Scenario: The slice delivers a junction or a mesh
- **WHEN** Machinist finishes building an increment whose interface is a gear mesh, a weld, or a similar small feature
- **THEN** that interface is held by connectivity and engagement contracts that fail deterministically, and the snapshot evidence remains the isometric and axis views

### Requirement: Machining guidance requires both geometric discipline safety nets
The shared machining skill exposed to runtime agents SHALL state connectivity
discipline alongside adjacency discipline and SHALL treat neither as optional
nor as a substitute for the other: every project root carries both a sweep
asserting that no two parts intersect and a sweep asserting that every part is
one connected body. It SHALL state that a rigid part is exactly one connected
solid, that watertightness does not imply connectedness, that a backend union
of solids that do not overlap yields a compound rather than failing, that
features which must be one piece interpenetrate by a stated weld, and that a
part deliberately made of several bodies declares that count.

#### Scenario: An agent follows the machining skill on a new project
- **WHEN** a runtime agent sets up a project's root contracts from the shared machining skill
- **THEN** the skill requires both the pairwise non-intersection sweep and the tree-wide connectivity sweep at the project root

#### Scenario: A part is built from separately rendered features
- **WHEN** a runtime agent builds one printed part from several solids
- **THEN** the skill requires them to overlap by a stated weld and the junction to be asserted, rather than relying on watertightness or a backend union

### Requirement: Machining guidance requires proven transmission and measured contracts
The shared machining skill SHALL require a driving pair to be shown to drive
rather than inferred from a tooth-count ratio and non-interference: engagement
is a paired perturbation contract in which the driven member fouls its mate
just past the backlash in both directions and stays free within it, with the
backlash angle derived in the test from the drawing rather than from the node.
It SHALL require meshing geometry to be sampled over one tooth pitch rather
than over the animation cycle, and SHALL require a contract to assert measured
geometry rather than an attribute the node code sets.

#### Scenario: A project contracts a gear pair
- **WHEN** a runtime agent writes the contracts for a pair that transmits motion
- **THEN** the skill requires the paired blocked-beyond and free-within engagement contracts and a phase relation taken from the drawing, not a ratio computed from tooth counts

#### Scenario: A contract is written against node metadata
- **WHEN** a runtime agent asserts an attribute the node code itself sets
- **THEN** the skill treats that as no contract at all, since it cannot fail for any reason a maker cares about

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

