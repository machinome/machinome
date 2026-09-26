## MODIFIED Requirements

### Requirement: Node path resolution

The system SHALL accept an optional `reference` positional for every command
that operates on a node (all except `new`, `viewer`, `models` and `vet`). When the
positional is given, it SHALL be a node reference in any of the four spellings
the loader accepts: a declared model name, `package.module:Class`,
`path/to/file.py`, or `path/to/file.py:Class`. A bare word that equals a name
declared in the project manifest's `[tool.machinome.models]` table SHALL
resolve to that model; a bare word that is not a declared name SHALL be read
as a module qualifier exactly as today, and a reference containing `:`, `/` or
`.` is never a model name.

When the positional is omitted, the command SHALL operate on the project's
default model: the model named by `[tool.machinome] model`, whether that key
holds a reference or, beside a `models` table, a declared name. When the
project declares models and no default, the command SHALL exit nonzero with an
error listing the declared names, and SHALL NOT pick one.

`machinome vet` SHALL take its own optional `reference` positional, which
accepts the same four spellings and resolves a declared name the same way.
It SHALL NOT take `--set`, because vet constructs no node. When that
positional is omitted, vet SHALL vet every model the project declares
rather than the default model, and a project that declares models and no
default SHALL NOT be an error for vet.

The system SHALL NOT rewrite a directory argument to `<dir>/__init__.py`. A
directory is not a node reference and SHALL be reported as an error naming the
accepted spellings.

#### Scenario: No argument uses the project model

- **WHEN** a user runs `machinome build` anywhere inside a project whose manifest
  declares `model = "windmill.windmill:Windmill"`
- **THEN** the command builds that node

#### Scenario: Any node by qualifier

- **WHEN** a user runs a node-scoped command with `windmill.windmill:Sail`
- **THEN** the command operates on `Sail`, not on the project model

#### Scenario: A directory is not a reference

- **WHEN** a user passes a directory to a node-scoped command
- **THEN** the command exits nonzero with an error naming the accepted
  reference spellings

#### Scenario: A command that operates on the installation

- **WHEN** a user runs `machinome viewer` with no further argument
- **THEN** the command runs and does not require or load a node

#### Scenario: A declared name is a reference

- **WHEN** a user runs `machinome build wall_clock_02` in a project whose manifest
  declares `wall_clock_02 = "design.wall_clock_02.clock:WallClock02"`
- **THEN** the command builds `WallClock02` into that model's build directory

#### Scenario: No argument uses the default among declared models

- **WHEN** a user runs `machinome develop` in a project declaring models and
  `model = "wall_clock_01"`
- **THEN** the session opens on `wall_clock_01`

#### Scenario: No argument and no default

- **WHEN** a user runs `machinome build` in a project declaring models and no
  `model` key
- **THEN** the command exits nonzero listing the declared model names and
  builds nothing

#### Scenario: A bare word that is not a declared name

- **WHEN** a user runs `machinome build sail` in a project whose `models` table
  has no `sail` key
- **THEN** the reference is read as the module qualifier `sail`, as before

#### Scenario: Vet with no argument vets every model

- **WHEN** a user runs `machinome vet` in a project declaring models and no
  `model` key
- **THEN** the command vets every declared model and does not fail for the
  missing default

#### Scenario: Vet takes no parameters

- **WHEN** a user runs `machinome vet -h`
- **THEN** the help lists `reference`, `--tests` and `--json`, and no
  `--set`

### Requirement: Import-step command

The system SHALL provide `machinome import-step FILE [--into PACKAGE_DIR]
[--model NAME]`, a one-shot scaffold that reads a STEP document's assembly
structure and writes project-owned source the pilot then edits. It SHALL
take no node reference and SHALL NOT load a node.

`--into` names the package directory the source is written into and SHALL
default to the current directory; the command SHALL create it when it does
not exist and SHALL write an `__init__.py` into it when it holds none, so
the generated modules are importable as a package. `--model` names the
model and SHALL default to a name derived from the document's root product,
or from the STEP file's stem when that product is unnamed.

The command SHALL write exactly two files into that directory, `parts.py`
and `assembly.py`, whose content is specified in the step-assembly
capability.

The command SHALL never overwrite. When either file already exists it SHALL
write nothing, report which file stopped it, and exit 1, so a pilot's edits
to generated source can never be lost.

The command SHALL write nothing when the reader reports any placement of
the document improper. It SHALL name each improper occurrence with its
determinant and scale factor and exit 1, because the framework's rest
operations cannot express that placement.

The command SHALL NOT modify `pyproject.toml`. It SHALL print the manifest
lines that declare the generated model, for the pilot to add, together with
the next steps for building it.

The command needs the exact-geometry kernel, as every exact path does. When
`cadquery` or the STEP reader cannot be imported it SHALL report that the
command needs them, name the extra that installs them, and exit 1, rather
than fail with an import traceback.

A `FILE` that does not exist, or that the STEP reader cannot read or
transfer, SHALL be reported on standard error with exit status 1 and no
file written.

When the `--into` directory lies in a project, meaning a `pyproject.toml`
with `[tool.machinome]` is found above it, the command SHALL refuse a
document whose real path is not under that project's real root, because
the adapters refuse a declared source outside its project and the
scaffold could not construct. It SHALL refuse before creating or writing
anything, naming the document, the project root and the remedy (copy the
document under the project root), and exit 1. When the `--into`
directory lies in no project, the document's location SHALL NOT be
judged.

#### Scenario: The command appears in CLI help

- **WHEN** a user runs `machinome -h`
- **THEN** the command list includes `import-step` with its docstring help

#### Scenario: A vendor assembly is scaffolded

- **WHEN** a user runs `machinome import-step vendor/actuator.stp --into
  actuator --model actuator` in an empty project
- **THEN** `actuator/parts.py` and `actuator/assembly.py` are written, one
  leaf class per part of the document and one assembly class per assembly
  product, and the command prints the manifest lines declaring the model
  and exits 0

#### Scenario: Generated source is never overwritten

- **WHEN** the command is run a second time into a directory that already
  holds `parts.py`
- **THEN** neither file is written, the message names `parts.py`, and the
  command exits 1

#### Scenario: An improper placement stops the scaffold

- **WHEN** the document places a product through a mirrored or scaled
  transform
- **THEN** no file is written, the message names that occurrence with its
  determinant and scale factor, and the command exits 1

#### Scenario: The manifest is printed, not edited

- **WHEN** the command completes in a project holding a `pyproject.toml`
- **THEN** the file is unchanged on disk and the lines that would declare
  the generated model are printed for the user to add

#### Scenario: The kernel is missing

- **WHEN** the command is run in an installation without the exact-geometry
  kernel
- **THEN** it reports that `import-step` needs it, names the extra that
  installs it, exits 1, and writes nothing

#### Scenario: An unreadable file is reported

- **WHEN** `FILE` does not exist or is not a STEP document the reader can
  transfer
- **THEN** the failure is reported on standard error, nothing is written,
  and the command exits 1

#### Scenario: A document outside the project is refused

- **WHEN** a user runs `machinome import-step /elsewhere/actuator.step
  --into sim` in a directory whose `pyproject.toml` declares
  `[tool.machinome]`
- **THEN** nothing is created or written, the message names the document,
  the project root and the remedy of copying the document under the
  root, and the command exits 1

#### Scenario: A document inside the project scaffolds

- **WHEN** a user runs `machinome import-step vendor/actuator.step --into
  sim` in that project, with the document under its root
- **THEN** `sim/parts.py` and `sim/assembly.py` are written and the
  command exits 0


## ADDED Requirements

### Requirement: Vet command

The system SHALL provide `machinome vet [reference] [--tests] [--json]`,
registered in the command registry after `import-step`, with the help text
taken from its docstring. Its behaviour is specified by the `vet`
capability. A directory given as its reference SHALL be refused naming the
accepted spellings, as it is for the node-scoped commands, but with exit
status 2 and nothing on standard output.

#### Scenario: Vet appears in CLI help

- **WHEN** a user runs `machinome -h`
- **THEN** the command list includes `vet`, after `import-step`

#### Scenario: A directory is refused

- **WHEN** a user runs `machinome vet sim/`, where `sim/` is a directory
- **THEN** the command writes an error naming the accepted reference
  spellings to standard error, prints nothing on standard output, and
  exits 2

