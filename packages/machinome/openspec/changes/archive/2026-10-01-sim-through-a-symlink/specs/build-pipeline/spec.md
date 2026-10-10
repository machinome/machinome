## MODIFIED Requirements

### Requirement: Project root discovery and model reference

The system SHALL determine a project's root by walking upward from a discovery
origin to the nearest ancestor `pyproject.toml` containing a
`[tool.machinome]` table, and SHALL treat the directory holding that file as
the project root.

When the table has no `models` sub-table, its `model` key SHALL hold an
entry-point object reference naming the project's model node, in the form
`package.module:ClassName`, and the project SHALL have that one model.

When the table has a `models` sub-table (`[tool.machinome.models]`), each of
its keys SHALL be a model name and each value an entry-point object reference
in the form `package.module:ClassName`. A model name SHALL be one word of
letters, digits, underscores and hyphens, starting with a letter or underscore,
and SHALL NOT equal the name of a directory at the project root, because that
directory's artifacts mirror into the same place. The table SHALL NOT be
empty. The `model` key MAY then name the project's default model and, when
present, SHALL equal one of the table's keys; a manifest whose `model` holds
anything else beside a `models` table is malformed. A project with the table
and no `model` key has no default model.

A manifest that violates any of these rules SHALL cause a command that needs a
node to fail with an actionable error naming the manifest and the rule.

The discovery origin SHALL be the referenced file when the reference names a
path, because a path identifies a project as surely as it identifies a file.
It SHALL be the working directory when there is no reference, or when the
reference is a qualifier or a declared model name, which carry no location.

The discovered root — never the working directory — SHALL anchor the import
path used to load project modules, the dotted module name computed for a file
loaded by path, the boundary of a node's tracked source closure, and the
project's build root. A command SHALL therefore resolve the same node, the
same source closure, and the same artifact paths from any directory.

The discovered root and every source path measured against it — a node's own
source file, the directory its artifacts mirror, and its tracked source
closure — SHALL be resolved paths, with every symbolic link followed,
whichever path the module was imported through. No artifact path SHALL be
computed between a resolved path and an unresolved one. A project reached
through a symbolic link SHALL therefore have the same root, the same source
closure and the same artifact paths as the project reached by its resolved
path, so an artifact built through either is current through the other, and
a node constructed through any path — by a command or by a Python caller such
as `Sim` — SHALL place its build directory under its project's build root.

When no ancestor `pyproject.toml` carries the table, a command that needs a
node SHALL fail with an actionable error naming the origin it searched from.

#### Scenario: Command run from a subdirectory

- **WHEN** a user runs a node-scoped command from a subdirectory of a project
  whose `pyproject.toml` declares `[tool.machinome] model`
- **THEN** the project root is discovered from that manifest
- **AND** the node's tracked source closure is the same set it would be from
  the project root

#### Scenario: A project reached through a symbolic link

- **WHEN** a Python caller imports a project's node class through a path that
  contains a symbolic link to the project, with the working directory on that
  path and `SOLID_BUILD_DIR` unset, and constructs the node and a `Sim` over
  it
- **THEN** construction succeeds and the node's build directory lies under
  the project's build root, `<resolved project root>/_build`
- **AND** it equals the build directory of the same node class imported
  through the project's resolved path
- **AND** nothing is created outside the project's build root

#### Scenario: A path outside the working directory's project

- **WHEN** a user names a path in a different project from the one containing
  the working directory
- **THEN** the root is discovered from that path, and the node is resolved
  against its own project

#### Scenario: No manifest above the origin

- **WHEN** a node-scoped command runs with no argument and no ancestor
  `pyproject.toml` carries a `[tool.machinome]` table
- **THEN** the command exits nonzero with an error naming the search origin

#### Scenario: A manifest declares several models and a default

- **WHEN** a manifest declares `[tool.machinome.models]` with
  `wall_clock_01 = "design.wall_clock_01.clock:WallClock01"` and
  `wall_clock_02 = "design.wall_clock_02.clock:WallClock02"`, and
  `model = "wall_clock_01"`
- **THEN** the project has two models named `wall_clock_01` and
  `wall_clock_02`, and its default model is `wall_clock_01`

#### Scenario: The default must be a declared name

- **WHEN** a manifest declares a `models` table and
  `model = "design.wall_clock_01.clock:WallClock01"`
- **THEN** a command that needs a node fails naming the manifest and stating
  that `model` must name one of the declared models

#### Scenario: A model name that shadows a source directory

- **WHEN** a manifest declares a model named `design` and the project root
  contains a directory `design/`
- **THEN** a command that needs a node fails naming the manifest, the name and
  the directory

#### Scenario: A single-model manifest is unchanged

- **WHEN** a manifest declares only `model = "windmill.windmill:Windmill"`
- **THEN** the project has one model, that reference, exactly as before
