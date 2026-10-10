## MODIFIED Requirements

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

The command needs the STEP reader, `machinome.node.step`, which the `step`
extra installs, in the distribution `machinome-node-step`. When that module
refuses because its kernel cannot be found, or because no installed
distribution ships it, the CLI SHALL answer `import-step` before the command parses its arguments or
runs: it SHALL print one line on standard error naming `import-step`, the
`step` extra and the install line `pip install "machinome[step]"`, write
nothing, and exit 1, rather than fail with an import traceback or report an
unknown command. A STEP reader whose kernel is found but fails to import SHALL
report its own import error.

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

- **WHEN** `machinome import-step vendor/actuator.step --into sim` is run in
  an installation without the `step` extra's kernel
- **THEN** standard error names `import-step` and `pip install
  "machinome[step]"`, nothing is created or written, no traceback is printed,
  and the command exits 1

#### Scenario: The STEP package is missing

- **WHEN** `machinome import-step vendor/actuator.step --into sim` is run in
  an installation without `machinome-node-step`
- **THEN** standard error names `import-step`, `machinome.node.step` and
  `pip install "machinome[step]"`, nothing is created or written, no
  traceback is printed, and the command exits 1

#### Scenario: Help for the command is answered the same way

- **WHEN** `machinome import-step -h` is run in an installation without the
  `step` extra's kernel
- **THEN** the same refusal is printed and the command exits 1

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
