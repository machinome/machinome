# scad-engine-dependency Specification

## Purpose

The OpenSCAD engine as a conditional, versioned provider of the core, resolved through the seam `machinome.scad_engine`: its one provider, the contract version check and its refusal, what an absent engine means for a value SolidPython built, that a plain number never consults it, and that the seam is the one core module naming the provider (ADR-171).
## Requirements
### Requirement: The OpenSCAD engine is resolved through one seam

The system SHALL resolve the OpenSCAD engine through one module of the core,
`machinome.scad_engine`, which names one provider, `machinome.openscad.engine`,
in its constant `PROVIDER`, and SHALL NOT name that provider in any other core
module. `scad_engine()` SHALL return the provider module when it is
importable, and SHALL return `None` when the import fails with a
`ModuleNotFoundError` whose missing module is `machinome.openscad`, the
provider itself, or `solid2`, the provider's kernel; the seam SHALL remember
which of them was missing, for the refusal below. Any other error raised
while importing the provider SHALL propagate unchanged. The resolution SHALL
happen at most once per process for a provider that resolves or is absent.

Importing `machinome.scad_engine` SHALL NOT import the provider or `solid2`.

Outside the package `machinome/openscad/` itself, the only modules of the
framework's own source that import `machinome.openscad` or any module beneath
it SHALL be `machinome.scad_engine` and the `Solid2Node` leaf module
`machinome/node/solid2.py`, which the campaign's next cycle moves over the
engine.

#### Scenario: The provider is installed

- **WHEN** `scad_engine()` is called in an installation carrying
  `machinome.openscad.engine`
- **THEN** it returns that module, and a second call returns the same module
  without importing again

#### Scenario: The provider is absent

- **WHEN** `machinome.openscad` cannot be found, or `solid2` cannot be found
  when the provider imports it
- **THEN** `scad_engine()` returns `None`

#### Scenario: The provider is broken

- **WHEN** importing the provider raises an error other than a missing
  `machinome.openscad`, provider or `solid2` module
- **THEN** that error propagates from `scad_engine()` unchanged

#### Scenario: The engine's package is reached only through the seam

- **WHEN** every module under `machinome/` outside `machinome/openscad/` is
  read for imports of `machinome.openscad` and its submodules
- **THEN** the importers are exactly `machinome/scad_engine.py` and
  `machinome/node/solid2.py`

### Requirement: The OpenSCAD engine's contract version is checked when it resolves

The seam SHALL declare the OpenSCAD engine contract version the core speaks as
`machinome.scad_engine.CONTRACT`, which is `2`. Version 2 is the operations
the core calls on the provider: `adopt(value)` (since version 1),
`scad_text(description, fn=None)` and `require_binary(needed_by, reason,
alternative=None)`. A resolved provider whose own `CONTRACT` is absent or
differs SHALL be refused with `ScadEngineIncompatible`, whose message names the
provider module, the version the provider declares (or that it declares none)
and the version the core speaks. The refusal SHALL NOT be cached: every
resolution of a mismatched provider raises it.

#### Scenario: A provider declaring another version

- **WHEN** the provider declares `CONTRACT = 1`
- **THEN** `scad_engine()` raises `ScadEngineIncompatible` naming
  `machinome.openscad.engine`, `1` and `2`

#### Scenario: A provider declaring no version

- **WHEN** the provider declares no `CONTRACT`
- **THEN** `scad_engine()` raises `ScadEngineIncompatible` saying the provider
  declares none and naming `2`

### Requirement: A SolidPython value is an expression only through the engine

The core SHALL recognise a value as symbolic when it is the framework's own
symbolic value, an expression graph node, or a value the resolved OpenSCAD
engine adopts; it SHALL consult the engine only for a value that is none of
the first two and not a plain number. When the engine is absent, no other
value is symbolic: a SolidPython value reaching `machinome.math`, a law, a
bound, a chain or a profile contact SHALL be treated as a non-number,
non-expression value and SHALL meet the refusal that path already gives such a
value, with its existing wording. Recognising a value SHALL NOT require the
engine to be present and SHALL raise no install refusal; the paths that do
require the engine are those of "SCAD text requires the OpenSCAD engine".

#### Scenario: Native values need no engine

- **WHEN** the engine is absent and a project composes time, drivers and
  `machinome.math` functions, compiles its laws and publishes its document
- **THEN** every result, every refusal and every published byte is the one an
  installation with the engine produces

#### Scenario: A SolidPython value without the engine

- **WHEN** the engine is absent and a running law returns a value SolidPython
  built
- **THEN** simulation construction refuses it as "neither a number nor an
  expression over its sources", as it refuses any other non-expression value

#### Scenario: Numbers never consult the engine

- **WHEN** a `machinome.math` function or an operator receives a plain `int`
  or `float`
- **THEN** the OpenSCAD engine is not consulted

### Requirement: The core composes no SCAD text

No module of the core SHALL import SolidPython or write SCAD syntax for its
presentation. The core SHALL describe a node's SCAD presentation as a
presentation description it owns (`machinome.node.presentation`), built from
what it already holds: the build-directory-relative path of each artifact
import, each colour, each rotation and translation with the values the
operation holds, each union, and the opaque geometry a SCAD-presented leaf
authored itself. It SHALL obtain SCAD text only by asking the resolved engine
for `scad_text` of such a description. Outside `machinome/openscad/`, the only
modules of the framework's own source that import `solid2` SHALL be the two
OpenSCAD leaf modules, `machinome/node/solid2.py` and
`machinome/node/openscad.py`, and the project template
`machinome/manager/templates/project/root/__init__.py`.

#### Scenario: The core's SolidPython importers

- **WHEN** every module under `machinome/` outside `machinome/openscad/` is
  read for imports of `solid2`
- **THEN** the importers are exactly `machinome/node/solid2.py`,
  `machinome/node/openscad.py` and
  `machinome/manager/templates/project/root/__init__.py`

#### Scenario: A node is assembled with SolidPython absent

- **WHEN** `solid2` cannot be found and an assembly of `StlNode` leaves is
  constructed and `assemble()` is called on it
- **THEN** the call returns its presentation description, every child is
  linked and prepared, `mesh` of a child is its world-placed geometry, and no
  module imported `solid2`

### Requirement: SCAD text requires the OpenSCAD engine

The seam SHALL provide `require_scad_engine(needed_by, reason,
alternative=None)`, returning the resolved provider, or raising
`ScadEngineUnavailable` when the engine is absent. The message SHALL name what
needed the engine, why, the module that could not be found, and the install
that provides it: for `solid2`, installing SolidPython with `pip install
solidpython2`; for `machinome.openscad` or its provider, reinstalling machinome,
whose distribution carries the engine; and, when given, the alternative. It
SHALL NOT name an extra that does not exist. `OpenScadUnavailable`, the
binary's refusal, SHALL be a subclass of `ScadEngineUnavailable`, with its
message unchanged, so a caller catches either through the seam.

The paths that require the engine SHALL be exactly: reading a node's
`scad_code`; a node's `generate_scad()`; the materialization of a leaf whose
geometry is authored in SCAD (a `Solid2Node`, an `OpenScadNode`, or a project
leaf overriding `as_scad`); and `machinome snapshot --renderer openscad`, whose
refusal SHALL name `--renderer web` as the alternative. When the path is a
node's, what needed it SHALL be named as the node's name and its own class.
Each check SHALL be made where the path is attempted, before any file is
written or any process launched.

`assemble()` and an ordinary `machinome build` SHALL NOT require the engine.
Neither asks for SCAD text except through the materialization of a leaf whose
geometry is authored in SCAD, under the `backend-neutral-materialization`
capability; without the engine, therefore, a build of a tree holding no such
leaf writes no `.scad` and logs nothing about SCAD presentation, since nothing
is skipped, and a tree holding one is refused by that leaf's requiring path,
naming the leaf, before any `.scad` is written.

#### Scenario: SCAD text of a node without the engine

- **WHEN** `solid2` cannot be found and `scad_code` is read on an `StlNode`
  subclass `Bracket` named `bracket`
- **THEN** `ScadEngineUnavailable` is raised naming `node bracket (Bracket)`,
  that its SCAD text is written by the OpenSCAD engine, `solid2` and `pip
  install solidpython2`

#### Scenario: The engine's own package is missing

- **WHEN** `machinome.openscad` cannot be found and `generate_scad()` is
  called on a node
- **THEN** `ScadEngineUnavailable` names `machinome.openscad` and reinstalling
  machinome, and names no extra

#### Scenario: A build without the engine completes

- **WHEN** a project whose leaves are exact and imported STL is built with
  `machinome build` and `solid2` cannot be found
- **THEN** the build succeeds, every STL and BREP and the published document
  are written, no `.scad` file exists under the build directory, and nothing
  is logged about SCAD presentation

#### Scenario: A SCAD-authored leaf is refused without the engine

- **WHEN** `machinome.openscad` cannot be found and a project whose tree holds
  a project leaf `Bracket`, named `bracket`, overriding `as_scad`, is built
- **THEN** the build fails with `ScadEngineUnavailable` naming `node bracket
  (Bracket)`, `machinome.openscad` and reinstalling machinome, and no `.scad`
  file is written

#### Scenario: The binary's refusal is caught through the seam

- **WHEN** the OpenSCAD binary is missing on a path that requires it
- **THEN** the error raised is an `OpenScadUnavailable` whose message is the
  one the `openscad-dependency` capability states, and it is an instance of
  `machinome.scad_engine.ScadEngineUnavailable`

