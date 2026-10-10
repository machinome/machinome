## MODIFIED Requirements

### Requirement: An unavailable mesh engine fails actionably at the point of use

When a requiring path is reached and the mesh engine's provider module cannot
be found, because the distribution `machinome-engine-mesh` is not installed,
or is found but refuses because `manifold3d`, which that distribution
requires, cannot be found, the system SHALL raise one error that names the
mesh engine, the operation that needed it, why that operation needs it, and
the install line `pip install "machinome[mesh]"`, before any geometry work is
attempted. The error SHALL be raised at the requiring operation, not at
module import, and it SHALL NOT surface as a bare `ModuleNotFoundError` from
framework internals.

`machinome test` whose comparison engine is `mesh`, from `--mesh` or from
`SOLID_TEST_ENGINE=mesh`, SHALL raise that error at its start, after the
comparison policy is resolved and before any node is loaded or built, and exit
with status 1, since every pair such a run compares needs the engine. A run on
the B-rep engine SHALL raise it at the first operation that needs the engine,
which it may never reach. Outside `machinome test`, a mesh run SHALL raise it
at its first mesh comparison.

`mesh_engine()` SHALL answer `None` when the provider is absent in either way,
without raising, so a caller may ask whether mesh geometry is available. A
provider module that is found but fails to import for another reason, such as
`manifold3d` being found and failing to load, SHALL NOT be reported as absent:
the underlying import error SHALL be raised at the point of use.

The system SHALL resolve the mesh engine at most once per process and reuse that
resolution for every requiring path.

Availability of the mesh engine SHALL be decided by the mesh engine alone.
Checks that do not need it — a solid's local bounding box, and the
watertightness validation that raises a `ValueError` naming a non-watertight
STL — SHALL continue to be performed from the cached base mesh whether or not
the mesh engine is present, and SHALL keep the timing and message they have
today.

The framework SHALL declare the `mesh` extra, which installs the engine's
distribution, `machinome-engine-mesh`, and through it `manifold3d`, so the
install line it names installs the engine.

#### Scenario: A mesh interference check names the missing dependency

- **WHEN** `assertNoSolidInterference` evaluates a candidate pair in which a
  solid has no B-rep geometry and the mesh engine is absent
- **THEN** the assertion raises an error naming the mesh engine,
  `assertNoSolidInterference`, the reason and `pip install
  "machinome[mesh]"`, rather than a bare import error

#### Scenario: The gravity support assertion names the missing dependency

- **WHEN** `assertAssemblySupported` is called on two or more selected solids,
  every one of them with B-rep geometry, and the mesh engine is absent
- **THEN** the assertion raises an error naming the mesh engine and
  `pip install "machinome[mesh]"` and stating that contact extraction for
  the statics phase is done on meshes, rather than a bare import error or a passing
  verdict

#### Scenario: A non-watertight STL is still reported by name

- **WHEN** an assertion selects a solid whose STL is not watertight
- **THEN** it raises a `ValueError` naming that STL file, whether or not the
  mesh engine is installed and whether or not that solid is ever compared

#### Scenario: A mesh run refuses at its start

- **WHEN** `machinome test --mesh`, or `machinome test` with
  `SOLID_TEST_ENGINE=mesh`, runs where the mesh engine is absent
- **THEN** it exits with status 1 and an error naming `machinome test on the
  mesh engine`, the mesh engine and `pip install "machinome[mesh]"`,
  before any node is built and before the mesh engine's line is printed

#### Scenario: An absent engine distribution is an absent engine

- **WHEN** the framework is installed without `machinome-engine-mesh`,
  `manifold3d` being installed, and a requiring path is reached
- **THEN** `mesh_engine()` answers `None` and the path raises the error
  naming the mesh engine and `pip install "machinome[mesh]"`

#### Scenario: An absent manifold3d is an absent engine

- **WHEN** the provider module exists, `manifold3d` cannot be found, and a
  requiring path is reached
- **THEN** it raises the same error naming `pip install "machinome[mesh]"`,
  and `mesh_engine()` answers `None`

#### Scenario: Asking about availability does not raise

- **WHEN** `mesh_engine()` is called in an interpreter where the provider
  module cannot be imported
- **THEN** it returns `None`

#### Scenario: A broken engine reports its own failure

- **WHEN** `manifold3d` is found but importing it raises an import error from
  inside
- **THEN** that import error is raised at the point of use, rather than the
  engine being reported as not installed

#### Scenario: The extra the refusal names exists

- **WHEN** the framework's package metadata is read
- **THEN** it declares a `mesh` extra requiring `machinome-engine-mesh`

### Requirement: The core holds no mesh engine code

The core SHALL hold no code that builds, judges, places, intersects, unites,
measures or meshes back a mesh-engine solid itself. It SHALL treat such a solid
as an opaque handle: it passes the handle between its caches, placement records
and comparisons, keys caches on files, artifact observations and snapshots, and
asks the mesh engine for every operation on it through the contract the seam
declares.

The core SHALL keep the parts of the mesh path that are not operations on a
solid: the order of culling and comparison, the caches over handles, the
decoding of STLs and the reading of meshes with trimesh, the statics program,
the mesh fusion's model facts and publication, and the verdict memo.

The mesh engine's provider module is not part of the core: it is shipped by
the distribution `machinome-engine-mesh`. No core module SHALL import
`manifold3d` or call `trimesh.boolean`.

#### Scenario: The core imports no mesh kernel

- **WHEN** every module under the core's `machinome/` is scanned for imports
  of `manifold3d` and for references to `trimesh.boolean`
- **THEN** no module imports `manifold3d`, `trimesh.boolean` is referenced by
  no module, and the core holds no `machinome/engine/mesh.py`; among the
  engine distributions' modules, only `machinome-engine-mesh`'s
  `machinome/engine/mesh.py` imports `manifold3d`

#### Scenario: The test framework orders, the engine operates

- **WHEN** a mesh pair is compared by an intersection assertion
- **THEN** every solid built, every admission judged, every placement,
  intersection, emptiness and volume it uses is an operation of the mesh engine,
  directly or through a core cache
