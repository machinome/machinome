## ADDED Requirements

### Requirement: A session announces the skills its agent holds
Every role session SHALL receive, as session-level instructions, a catalogue of
exactly the skills its profile agent declares: each skill's name, its
self-described purpose, and the instruction to load a skill before doing work
that skill covers. The catalogue SHALL name the tool that loads a skill. It
SHALL NOT carry a skill's instructions and SHALL NOT name a filesystem path the
session cannot read.

A session whose agent declares no skill SHALL receive no catalogue.

#### Scenario: A role holding skills opens
- **WHEN** a role whose profile agent declares `solid-node-api` and
  `solid-node` opens on any backend
- **THEN** its session contract lists both skills by name with their
  descriptions and states how to load one, and contains neither skill's
  instructions

#### Scenario: A role holding no skill opens
- **WHEN** a role whose profile agent declares no skill opens
- **THEN** its session contract announces no skill catalogue

#### Scenario: A role does not learn another role's skills
- **WHEN** two roles of the same profile declare different skills
- **THEN** each session's catalogue lists only the skills its own agent
  declares

### Requirement: An agent loads a skill's instructions on demand
The floor tool set SHALL provide `load_skill`, taking a skill name and
returning that skill's full instructions. It SHALL resolve the name against a
registry supplied when the tool server is launched and SHALL reject any name
absent from that registry, reporting the names it does hold.

`load_skill` SHALL accept an optional `resource` naming a file bundled beside
the skill's `SKILL.md`, returning that file's content. Without a `resource`, the
result SHALL list the bundled files the skill carries, so an agent can discover
them without a directory listing.

`load_skill` SHALL NOT accept a filesystem path in place of a skill name.

#### Scenario: An agent loads an announced skill
- **WHEN** an agent calls `load_skill` with a name from its catalogue
- **THEN** the tool returns that skill's instructions and names the resource
  files bundled with it, if any

#### Scenario: An agent names a skill it does not hold
- **WHEN** an agent calls `load_skill` with a name absent from the session's
  registry
- **THEN** the call fails, naming the skills the session can load, and reads
  nothing

#### Scenario: An agent loads a bundled resource
- **WHEN** an agent calls `load_skill` with a skill name and a `resource` the
  skill bundles
- **THEN** the tool returns that file's content

#### Scenario: A resource argument escapes the skill directory
- **WHEN** a `resource` argument resolves outside its named skill's directory
- **THEN** the call fails and reads nothing

### Requirement: Skill loading is available whenever a session holds skills
A session's access to `load_skill` SHALL follow the skills its profile agent
declares, not the tool capabilities its profile declares. A session whose agent
declares at least one skill SHALL be able to call `load_skill` whatever its
declared tool capabilities are. A session whose agent declares no skill SHALL
NOT have `load_skill` available.

#### Scenario: A role with narrow tool capability holds skills
- **WHEN** a role declaring skills opens with a tool policy that grants no
  filesystem read capability
- **THEN** `load_skill` is still reachable in that session

#### Scenario: A role with no skill
- **WHEN** a role declaring no skill opens
- **THEN** `load_skill` is not among its reachable tools

### Requirement: A registered skill directory is the only readable location outside the project
`load_skill` SHALL read only within the skill directories registered for that
session, and those directories SHALL be supplied by the shop when the tool
server is launched, never chosen by the calling agent. No other floor tool
SHALL read a registered skill directory, and `load_skill` SHALL NOT read the
active project.

#### Scenario: A skill directory is not reachable through the file tools
- **WHEN** an agent calls a filesystem read tool with a path inside a
  registered skill directory
- **THEN** the call is rejected as outside the active project, unchanged by
  the presence of the skill registry

#### Scenario: The registry is fixed at launch
- **WHEN** a session's tool server is running
- **THEN** no tool call can add, replace, or repoint a registered skill
  directory
