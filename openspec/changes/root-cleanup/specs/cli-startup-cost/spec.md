## RENAMED Requirements

- FROM: `### Requirement: Node backend exports resolve on first use`
- TO: `### Requirement: Importing the node package imports no backend`

## MODIFIED Requirements

### Requirement: Importing the node package imports no backend

The system SHALL expose from the root of `machinome.node` no name of its
own, under the `node-model` requirement "The node package's root exports
nothing": the node classes and the declarative structure helpers are imported
from the modules that define them. The build-parameter kinds, the `Quantity`
base and the parameter enumerator belong to the dedicated build-parameter
module and SHALL be reachable only from there; the port kinds, the port
declaration enumerator and the time-base declaration belong to the dedicated
motion module and SHALL be reachable only from there. Importing
`machinome.node`, or any module beneath it,
SHALL NOT import a backend the caller has not named.

In particular, importing `machinome.node` SHALL NOT import `cadquery`,
`build123d`, `molejo` or the kernel binding `OCP`, and SHALL NOT import a
module of a node type. A node type is reached by importing the leaf module that
defines it (the `node-model` capability's table), which imports what that
module needs and nothing else:
`StepNode` imports CadQuery and the kernel's STEP reader, `MolejoNode` imports
molejo, and `CadQueryNode`, `Build123dNode` and `Build123dSheetNode` import
no CAD front end, since a project's own module imports it to render.

Attribute access SHALL resolve submodules of `machinome.node`, imported
when first read, so a consumer reading `machinome.node.<submodule>` after
importing only the package keeps working.

A name that is neither a submodule nor refused SHALL raise `AttributeError`.
A name that has moved to another module, or that the root resolved until the
OpenSpec change `root-cleanup`, SHALL raise `ImportError` whose message names
the module that now answers for it: an `ImportError` rather than an
`AttributeError` because `from machinome.node import <name>` discards an
`AttributeError`'s message and substitutes its own generic text, so only an
`ImportError` carries the redirect to the failing import line. A submodule
that refuses an absent kernel SHALL raise that refusal, which is an
`ImportError`, for the same reason.

#### Scenario: An OpenSCAD-only project imports no B-rep stack

- **WHEN** a project whose model uses only `Solid2Node` is built
- **THEN** the build produces the same artifacts as before and `cadquery` is
  absent from the build process's imported modules

#### Scenario: A named backend is resolved

- **WHEN** a module runs `from machinome.node.cadquery import CadQueryNode`
- **THEN** it receives the class `machinome.node.cadquery` defines, and
  `cadquery` is not imported by the import

#### Scenario: The STEP reader is not imported by the node package

- **WHEN** `machinome.node` is imported in a fresh interpreter
- **THEN** the kernel's STEP reader and every node type's module are absent
  from the process's imported modules, and the reader is imported when
  `machinome.node.step` is first imported

#### Scenario: A submodule is reached through the package

- **WHEN** a consumer imports `machinome.node` and then reads
  `machinome.node.assembly` or `machinome.node.cadquery`
- **THEN** the submodule is returned

#### Scenario: An unknown name still fails

- **WHEN** a consumer reads a name that is neither a submodule of
  `machinome.node` nor a refused name
- **THEN** `AttributeError` is raised

#### Scenario: A parameter kind is not a node export

- **WHEN** a consumer reads a build-parameter name off `machinome.node`
- **THEN** `AttributeError` is raised naming it, so
  `from machinome.node import Length` fails at the import, and the
  package's export list is empty

#### Scenario: A port kind is not a node export

- **WHEN** a consumer reads `RotationalPort`, `SignalPort`,
  `TranslationalPort`, `Port`, `declared_ports` or `Time` off
  `machinome.node`
- **THEN** `ImportError` is raised naming `machinome.motion.ports`, so
  `from machinome.node import RotationalPort` fails at the import with
  that message, and the package's export list is empty

### Requirement: Deferred imports do not hide a broken installation

When a deferred import fails because something installed is broken, the
system SHALL raise the underlying import error at the point the deferred name
is first used, naming that name. It SHALL NOT be swallowed, retried against a
substitute, or reported as a missing attribute. The node package's deferred
names are its submodules, imported when first read through the package
(`machinome.node.step`, `from machinome.node import step`); its root resolves
no other name.

An extra that is not installed is not a broken installation. When the deferred
import fails with a kernel module's absent-kernel refusal (the `kernel-extras`
capability), the system SHALL raise that refusal unmodified, so its message
names the node types and the install line and nothing suggests a broken
install. It SHALL NOT be reported as a missing attribute either.

#### Scenario: A broken backend reports its own failure

- **WHEN** a node type's submodule whose kernel is found but fails to import
  is read through `machinome.node` (`machinome.node.step`)
- **THEN** the underlying import error is raised, naming the requested
  submodule, rather than an `AttributeError`

#### Scenario: An absent extra is reported by its install line

- **WHEN** `from machinome.node.step import StepNode` or
  `from machinome.node import step` runs where `cadquery` cannot be found
- **THEN** the raised error is the `step` module's refusal, unmodified: it
  names `StepNode` and `pip install "machinome[step]"`, and `hasattr` on
  `machinome.node` for `step` raises it rather than answering `False`
