## ADDED Requirements

### Requirement: The B-rep engine is resolved only by the paths that use it

The system SHALL treat the B-rep engine, which reads, places, fuses, compares,
measures and writes boundary-representation shapes, as a dependency of the
paths that perform that work, resolved on first use and not at import.

Importing `machinome`, `machinome.node`, `machinome.node.brep_leaf`,
`machinome.node.fusion`, `machinome.engine`, `machinome.brep_cache`,
`machinome.brep_artifacts` or `machinome.test`, and building or testing a
project none of whose nodes declares `brep`, SHALL NOT import the B-rep
engine, and the framework SHALL NOT import `OCP` on those paths.

The core paths that resolve it are exactly:

- converting a B-rep leaf's render result to B-rep geometry, and writing a
  B-rep node's `.brep` or tessellated `.stl` artifact;
- reading a B-rep node's `shape()`, including loading a current `.brep`;
- composing a B-rep `FusionNode`'s shape;
- the B-rep path of the test framework's comparisons, which runs only for a
  pair of B-rep nodes in a run comparing on the B-rep engine.

A node whose artifacts are current SHALL be reused without resolving the
engine: a B-rep leaf or B-rep fusion whose `.brep` and `.stl` are current
SHALL NOT resolve it to prepare geometry for a build.

The system SHALL resolve the engine at most once per process and reuse that
resolution for every path.

#### Scenario: Importing the framework loads no engine

- **WHEN** a fresh interpreter imports `machinome.engine`,
  `machinome.node.fusion`, `machinome.node.brep_leaf`, `machinome.brep_cache`,
  `machinome.brep_artifacts` and `machinome.test`
- **THEN** neither the B-rep engine module `machinome.engine.brep` nor `OCP`
  is among the imported modules

#### Scenario: A project of mesh parts never resolves the engine

- **WHEN** a project none of whose nodes declares `brep` is built and its
  tests run
- **THEN** the results are those it produced before, and the B-rep engine is
  never imported

#### Scenario: A current B-rep fusion does not resolve the engine

- **WHEN** a B-rep fusion's `.brep` and `.stl` are current and the project is
  built again
- **THEN** the fusion's artifacts are reused and the B-rep engine is not
  resolved to produce them

#### Scenario: A B-rep comparison resolves the engine once

- **WHEN** a test run compares several pairs of B-rep nodes
- **THEN** the engine is resolved at the first B-rep comparison and that one
  resolution serves every later one

### Requirement: The core holds no kernel code

The core SHALL hold no code that reads, places, fuses, intersects, measures,
tessellates or writes a B-rep shape itself. It SHALL treat a B-rep shape as
an opaque handle: it passes the handle between nodes, caches and the test
framework, keys caches on the handle's identity, and asks the B-rep engine for
every operation on it through the contract the seam declares.

The core SHALL keep the parts of the B-rep path that are not operations on a
shape: the B-rep leaf and fusion nodes, the seam and its contract, the order
in which the test framework culls and compares, the memos over handles and
artifact files, artifact publication, and the verdict memo.

Outside the B-rep engine's provider module, no core module SHALL import
`OCP`, `cadquery` or `build123d` for B-rep geometry. The STEP adapter's reader
and the markings' SVG reducer are outside this requirement until their
packages are cut.

#### Scenario: The core imports no kernel for B-rep geometry

- **WHEN** the core's source is scanned for imports of `OCP` and `cadquery`
- **THEN** none is found outside `machinome/engine/brep.py` except in the
  STEP adapter

#### Scenario: The test framework orders, the engine operates

- **WHEN** a B-rep pair is compared by an intersection assertion
- **THEN** every bound, face box, placement, containment classification,
  Common, solid count and volume it uses is computed by an engine operation,
  directly or through a core memo

### Requirement: An unavailable B-rep engine fails actionably at the point of use

When a path that needs the B-rep engine is reached and its provider module
cannot be found, or is found but refuses because the kernel its `brep` extra
installs cannot be found (the `kernel-extras` capability), the system SHALL
raise one error that names the B-rep engine, the operation that needed it, why
that operation needs it, and the install line `pip install "machinome[brep]"`,
before any geometry work is attempted. It SHALL be raised at the requiring
operation, not at import, and SHALL NOT surface as a bare
`ModuleNotFoundError` from framework internals.

`brep_engine()` SHALL answer `None` in both cases, without raising, so a
caller may ask whether B-rep geometry is available.

A provider module that is found but fails to import for another reason, such
as its kernel being found and failing to load, SHALL NOT be reported as
absent: the underlying import error SHALL be raised at the point of use, as
the `cli-startup-cost` capability requires of every deferred import.

The system SHALL NOT substitute the mesh engine, degrade a B-rep question to
a mesh one, or skip an operation when the B-rep engine is unavailable.

The framework SHALL declare the `brep` extra, so the install line it names
installs the engine's kernel.

#### Scenario: A missing engine names the install

- **WHEN** `require_brep_engine('B-rep fusion Bracket', 'fusing its B-rep
  children')` is called in an interpreter where the engine's provider module
  cannot be imported
- **THEN** it raises `BrepEngineUnavailable`, whose message names the B-rep
  engine, `B-rep fusion Bracket`, `fusing its B-rep children` and `pip
  install "machinome[brep]"`

#### Scenario: An absent OCP binding is an absent engine

- **WHEN** `require_brep_engine('B-rep fusion Bracket', 'fusing its B-rep
  children')` is called in an interpreter where the provider module exists
  and `OCP` cannot be found
- **THEN** it raises the same error naming `pip install "machinome[brep]"`,
  and `brep_engine()` answers `None`

#### Scenario: Asking about availability does not raise

- **WHEN** `brep_engine()` is called in an interpreter where the provider
  module cannot be imported
- **THEN** it returns `None`

#### Scenario: A broken engine reports its own failure

- **WHEN** the provider module is present but importing it raises an import
  error from inside, its kernel having been found
- **THEN** that import error is raised at the point of use, rather than the
  engine being reported as not installed

#### Scenario: The extra the refusal names exists

- **WHEN** the framework's package metadata is read
- **THEN** it declares a `brep` extra

### Requirement: The core declares the contract it speaks and checks the engine's

The core SHALL declare one integer, the B-rep engine contract version it
speaks (`machinome.engine.BREP_CONTRACT`), beside the operations that contract
comprises, named as the engine defines them, and the error types the engine
raises (`BrepCommonInconsistency`, `BrepCommonVerificationError`). The
provider declares the version it implements under the `brep-engine`
capability.

When the engine is resolved, the system SHALL compare the two. When they
differ, or the provider declares none, both `brep_engine()` and
`require_brep_engine()` SHALL refuse with one error, `BrepEngineIncompatible`,
naming the contract version the core speaks, the version the provider
declares (or that it declares none), and the provider module. No B-rep
operation SHALL run against a provider that was refused.

#### Scenario: A matching engine is resolved

- **WHEN** the provider declares the contract version the core speaks
- **THEN** `brep_engine()` returns the provider and it offers every operation
  the contract names

#### Scenario: A mismatched engine is refused naming both versions

- **WHEN** the provider declares contract version 3 and the core speaks 2
- **THEN** resolving the engine raises an error naming version 2, version 3
  and the provider module, and no B-rep operation runs

#### Scenario: An engine that declares no version is refused

- **WHEN** the provider module declares no contract version
- **THEN** resolving the engine raises an error naming the core's version and
  stating that the provider declares none

### Requirement: The core names its B-rep engine in one place

The B-rep engine's provider SHALL be the module `machinome.engine.brep`. The
core SHALL name that provider in exactly one module, the engine package's
`__init__` (`machinome/engine/__init__.py`), which holds the seam that
resolves it; every other core path SHALL reach the engine through the seam.
The seam's names SHALL be `brep_engine`, `require_brep_engine`,
`BrepEngineUnavailable`, `BrepEngineIncompatible`, `BREP_CONTRACT` and
`BREP_PROVIDER`, none of which is the provider module's own name, so
resolving the provider never rebinds a seam name on the package.

#### Scenario: The seam is the only place the provider is named

- **WHEN** the core's source is scanned for imports and string spellings of
  `machinome.engine.brep`
- **THEN** the only module that names it is `machinome/engine/__init__.py`

#### Scenario: Resolving the provider leaves the seam callable

- **WHEN** `brep_engine()` has resolved the provider and set the attribute
  `brep` of the package `machinome.engine` to the provider module
- **THEN** `machinome.engine.brep_engine` is still the seam function and a
  second call returns the same provider
