## MODIFIED Requirements

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

The B-rep engine's provider module is not part of the core: it is shipped by
the distribution `machinome-engine-brep`. No core module SHALL import `OCP`,
`cadquery` or `build123d` for B-rep geometry. The STEP adapter's reader and
the markings' SVG reducer are outside this requirement until their packages
are cut.

#### Scenario: The core imports no kernel for B-rep geometry

- **WHEN** the core's source is scanned for imports of `OCP` and `cadquery`
- **THEN** none is found except in the STEP adapter, and the core holds no
  `machinome/engine/brep.py`

#### Scenario: The test framework orders, the engine operates

- **WHEN** a B-rep pair is compared by an intersection assertion
- **THEN** every bound, face box, placement, containment classification,
  Common, solid count and volume it uses is computed by an engine operation,
  directly or through a core memo

### Requirement: An unavailable B-rep engine fails actionably at the point of use

When a path that needs the B-rep engine is reached and its provider module
cannot be found, because the distribution `machinome-engine-brep` is not
installed, or is found but refuses because the kernel it requires cannot be
found (the `kernel-extras` capability), the system SHALL raise one error that
names the B-rep engine, the operation that needed it, why that operation
needs it, and the install line `pip install "machinome[brep]"`, before any
geometry work is attempted. It SHALL be raised at the requiring operation,
not at import, and SHALL NOT surface as a bare `ModuleNotFoundError` from
framework internals.

`brep_engine()` SHALL answer `None` in both cases, without raising, so a
caller may ask whether B-rep geometry is available.

A provider module that is found but fails to import for another reason, such
as its kernel being found and failing to load, SHALL NOT be reported as
absent: the underlying import error SHALL be raised at the point of use, as
the `cli-startup-cost` capability requires of every deferred import.

The system SHALL NOT substitute the mesh engine, degrade a B-rep question to
a mesh one, or skip an operation when the B-rep engine is unavailable.

The framework SHALL declare the `brep` extra, which installs the engine's
distribution, `machinome-engine-brep`, and through it the engine's kernel, so
the install line it names installs the engine.

#### Scenario: A missing engine names the install

- **WHEN** `require_brep_engine('B-rep fusion Bracket', 'fusing its B-rep
  children')` is called in an interpreter where the engine's provider module
  cannot be imported
- **THEN** it raises `BrepEngineUnavailable`, whose message names the B-rep
  engine, `B-rep fusion Bracket`, `fusing its B-rep children` and `pip
  install "machinome[brep]"`

#### Scenario: An absent engine distribution is an absent engine

- **WHEN** the framework is installed without `machinome-engine-brep`, the
  OCCT binding being installed, and `require_brep_engine('B-rep fusion
  Bracket', 'fusing its B-rep children')` is called
- **THEN** `brep_engine()` answers `None` and the call raises the same
  error naming `pip install "machinome[brep]"`

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
- **THEN** it declares a `brep` extra requiring `machinome-engine-brep`
