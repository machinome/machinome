# exact-engine-dependency Specification

## Purpose

The exact engine as a conditional, versioned dependency of the core: which paths resolve it, that the core holds no kernel code and treats exact shapes as opaque handles, the actionable refusal when the engine is absent, the contract version check, and the one place the core names its provider.
## Requirements
### Requirement: The exact engine is resolved only by the paths that use it

The system SHALL treat the exact engine, the boundary-representation kernel
that reads, places, fuses, compares, measures and writes exact shapes, as a
dependency of the paths that perform that work, resolved on first use and not
at import.

Importing `machinome`, `machinome.node`, `machinome.node.exact_leaf`,
`machinome.node.fusion`, `machinome.exact_engine`, `machinome.exact_cache`,
`machinome.exact_artifacts` or `machinome.test`, and building or testing a
project none of whose nodes is exact, SHALL NOT import the exact engine, and
the framework SHALL NOT import `OCP` on those paths.

The core paths that resolve it are exactly:

- converting an exact leaf's render result to exact geometry, and writing an
  exact node's `.brep` or tessellated `.stl` artifact;
- reading an exact node's `shape()`, including loading a current `.brep`;
- composing an exact `FusionNode`'s shape;
- the exact path of the test framework's comparisons, which runs only for a
  pair of exact nodes under the exact kernel.

A node whose artifacts are current SHALL be reused without resolving the
engine: an exact leaf or exact fusion whose `.brep` and `.stl` are current
SHALL NOT resolve it to prepare geometry for a build.

The system SHALL resolve the engine at most once per process and reuse that
resolution for every path.

#### Scenario: Importing the framework loads no engine

- **WHEN** a fresh interpreter imports `machinome.node.fusion`,
  `machinome.node.exact_leaf`, `machinome.exact_cache`,
  `machinome.exact_artifacts` and `machinome.test`
- **THEN** neither the exact engine module nor `OCP` is among the imported
  modules

#### Scenario: A faceted project never resolves the engine

- **WHEN** a project whose nodes are all faceted is built and its tests run
- **THEN** the results are those it produced before, and the exact engine is
  never imported

#### Scenario: A current exact fusion does not resolve the engine

- **WHEN** an exact fusion's `.brep` and `.stl` are current and the project is
  built again
- **THEN** the fusion's artifacts are reused and the exact engine is not
  resolved to produce them

#### Scenario: An exact comparison resolves the engine once

- **WHEN** a test run compares several pairs of exact nodes
- **THEN** the engine is resolved at the first exact comparison and that one
  resolution serves every later one

### Requirement: The core holds no kernel code

The core SHALL hold no code that reads, places, fuses, intersects, measures,
tessellates or writes an exact shape itself. It SHALL treat an exact shape as
an opaque handle: it passes the handle between nodes, caches and the test
framework, keys caches on the handle's identity, and asks the exact engine for
every operation on it through the contract the seam declares.

The core SHALL keep the parts of the exact path that are not operations on a
shape: the exact leaf and fusion nodes, the seam and its contract, the order
in which the test framework culls and compares, the memos over handles and
artifact files, artifact publication, and the verdict memo.

Outside the engine's own package, no core module SHALL import `OCP`,
`cadquery` or `build123d` for exact geometry. The STEP adapter's reader and
the markings' SVG reducer are outside this requirement until their packages
are cut.

#### Scenario: The core imports no kernel for exact geometry

- **WHEN** the core's source is scanned for imports of `OCP` and `cadquery`
- **THEN** none is found outside `machinome/occt/` except in the STEP adapter

#### Scenario: The test framework orders, the engine operates

- **WHEN** an exact pair is compared by an intersection assertion
- **THEN** every bound, face box, placement, containment classification,
  Common, solid count and volume it uses is computed by an engine operation,
  directly or through a core memo

### Requirement: An unavailable exact engine fails actionably at the point of use

When a path that needs the exact engine is reached and its provider module
cannot be found, or is found but refuses because the kernel its `occt` extra
installs cannot be found (the `kernel-extras` capability), the system SHALL
raise one error that names the exact engine, the operation that needed it, why
that operation needs it, and the install line `pip install "machinome[occt]"`,
before any geometry work is attempted. It SHALL be raised at the requiring
operation, not at import, and SHALL NOT surface as a bare
`ModuleNotFoundError` from framework internals.

`exact_engine()` SHALL answer `None` in both cases, without raising, so a
caller may ask whether exact geometry is available.

A provider module that is found but fails to import for another reason, such
as its kernel being found and failing to load, SHALL NOT be reported as
absent: the underlying import error SHALL be raised at the point of use, as
the `cli-startup-cost` capability requires of every deferred import.

The system SHALL NOT substitute the mesh engine, degrade an exact question to
a faceted one, or skip an operation when the exact engine is unavailable.

The framework SHALL declare the `occt` extra, so the install line it names
installs the engine's kernel.

#### Scenario: A missing engine names the install

- **WHEN** `require_exact_engine('exact fusion Bracket', 'fusing its exact
  children')` is called in an interpreter where the engine's provider module
  cannot be imported
- **THEN** it raises an error whose message names the exact engine, `exact
  fusion Bracket`, `fusing its exact children` and `pip install
  "machinome[occt]"`

#### Scenario: An absent OCCT binding is an absent engine

- **WHEN** `require_exact_engine('exact fusion Bracket', 'fusing its exact
  children')` is called in an interpreter where the provider module exists
  and `OCP` cannot be found
- **THEN** it raises the same error naming `pip install "machinome[occt]"`,
  and `exact_engine()` answers `None`

#### Scenario: Asking about availability does not raise

- **WHEN** `exact_engine()` is called in an interpreter where the provider
  module cannot be imported
- **THEN** it returns `None`

#### Scenario: A broken engine reports its own failure

- **WHEN** the provider module is present but importing it raises an import
  error from inside, its kernel having been found
- **THEN** that import error is raised at the point of use, rather than the
  engine being reported as not installed

#### Scenario: The extra the refusal names exists

- **WHEN** the framework's package metadata is read
- **THEN** it declares an `occt` extra

### Requirement: The core declares the contract it speaks and checks the engine's

The core SHALL declare one integer, the exact engine contract version it
speaks, beside the operations that contract comprises, named as the engine
defines them. The provider declares the version it implements under the
`occt-engine` capability.

When the engine is resolved, the system SHALL compare the two. When they
differ, or the provider declares none, both `exact_engine()` and
`require_exact_engine()` SHALL refuse with one error naming the contract
version the core speaks, the version the provider declares (or that it
declares none), and the provider module. No exact operation SHALL run against
a provider that was refused.

#### Scenario: A matching engine is resolved

- **WHEN** the provider declares the contract version the core speaks
- **THEN** `exact_engine()` returns the provider and it offers every operation
  the contract names

#### Scenario: A mismatched engine is refused naming both versions

- **WHEN** the provider declares contract version 2 and the core speaks 1
- **THEN** resolving the engine raises an error naming version 1, version 2
  and the provider module, and no exact operation runs

#### Scenario: An engine that declares no version is refused

- **WHEN** the provider module declares no contract version
- **THEN** resolving the engine raises an error naming the core's version and
  stating that the provider declares none

### Requirement: The core names its exact engine in one place

The exact engine's provider SHALL be the module `machinome.occt.engine`. The
core SHALL name that provider in exactly one module, the seam that resolves
it; every other core path SHALL reach the engine through the seam.

#### Scenario: The seam is the only place the provider is named

- **WHEN** the core's source is scanned for imports of `machinome.occt`
- **THEN** the only module that names it is the exact engine seam

