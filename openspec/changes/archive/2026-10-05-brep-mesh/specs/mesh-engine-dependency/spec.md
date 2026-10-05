## MODIFIED Requirements

### Requirement: The mesh engine is required only by the paths that use it

The system SHALL treat the mesh engine, which builds, places, intersects,
unites, measures and meshes back the solids mesh geometry is decided on, as
a conditional dependency of the paths that perform that work, resolved on
first use and not at import. Its provider is the module
`machinome.engine.mesh`, over `manifold3d`, installed by the `mesh`
extra (the `kernel-extras` and `mesh-engine` capabilities).

Importing `machinome`, `machinome.engine`, `machinome.node.fusion` or
`machinome.test`, declaring a `TestCase`, binding a node to it, building a
project, and starting the test runner on the B-rep engine SHALL NOT resolve the
mesh engine, and SHALL NOT import `machinome.engine.mesh`.

The paths that require it are exactly:

- producing a stale mesh `FusionNode` artifact by directly unioning its
  children's meshes;
- evaluating an intersection between two nodes that do not both carry B-rep
  geometry, or any two nodes on the mesh engine — the mesh fast path
  and the `.mesh` fallback of the shared intersection helper, and therefore
  `assertNotIntersecting`, `assertIntersecting`, `assertIntersectVolumeAbove`,
  `assertIntersectVolumeBelow`, `assertBlockedBeyond`, `assertFreeWithin`,
  `assertJoined` and `assertNoPairwiseIntersections` whenever the pair they
  compare is not a pair of B-rep nodes on the B-rep engine;
- `assertJoined`'s union of two nodes that are not a pair of B-rep nodes on the
  B-rep engine;
- evaluating a candidate pair of `assertNoSolidInterference` in which at least
  one of the two solids has no B-rep geometry, or any candidate pair on the mesh
  engine;
- `assertAssemblySupported` over two or more selected solids, whose
  frictionless-statics phase extracts contact patches from meshed intersections
  for every body — B-rep solids included — and builds a meshed virtual floor;
- `machinome test` whose comparison engine is `mesh`, at its start.

No other operation SHALL require it. In particular, a project whose model is
entirely B-rep under the `brep-geometry` capability SHALL be built, and SHALL
run `assertNoSolidInterference`, `assertNoDisconnectedSolids`, `assertJoined`,
and every intersection-volume and perturbation assertion on the B-rep engine,
without the mesh engine and without asking for it.

The extraction of the engine into its provider SHALL NOT change any assertion's
behaviour when the mesh engine is present: same verdicts, bit for bit, same
messages, same broad-phase candidate sets, the same number of solids built.
B-rep fusion and assembly grouping SHALL NOT resolve the mesh engine merely to
prepare or produce geometry.

The system SHALL NOT substitute a different engine, degrade a verdict, skip an
assertion, or emit a warning in place of a result when the mesh engine is
unavailable. An unavailable mesh engine means the operation cannot be performed.

The core SHALL NOT reach the mesh engine's kernel through another library:
`assertJoined`'s union and the `.mesh` fallback SHALL go through the mesh
engine, not through `trimesh.boolean`. Assertions whose geometry is reached
through libraries that select their own backends — the proximity queries behind
`assertInside`, `assertClose` and `assertFar` — SHALL report through those
libraries' own dependency contracts. This capability does not describe them.

#### Scenario: An all-exact project asserts with no mesh engine installed

- **WHEN** a project whose every selected solid has B-rep geometry is tested on the B-rep
  engine on a machine where neither `manifold3d` nor `machinome.engine.mesh` can be
  imported
- **THEN** `machinome.test` imports, the runner starts,
  `assertNoSolidInterference` reaches the same verdict it reaches with the mesh
  engine installed, and `machinome.engine.mesh` is never asked for

#### Scenario: The assertion module imports without the mesh engine

- **WHEN** `machinome.test` is imported in an interpreter where neither
  `manifold3d` nor `machinome.engine.mesh` can be imported
- **THEN** the import succeeds, `machinome.engine.mesh` is not among the
  imported modules, and no error is raised until an operation that needs the
  mesh engine is reached

#### Scenario: A faceted comparison still requires it

- **WHEN** an assertion compares a pair in which at least one node has no B-rep geometry
  and the mesh engine is available
- **THEN** the comparison is evaluated through the mesh engine's cached solids,
  with the verdict it had before the engine became a provider

#### Scenario: Faceted fusion names its missing engine

- **WHEN** a mesh fusion needs to produce its artifact and the mesh engine
  is absent
- **THEN** it fails naming the mesh engine, the fusion operation and
  `pip install "machinome[mesh]"`, without trying OpenSCAD, publishing
  concatenated geometry, or silently retaining a stale STL

#### Scenario: Current fusion does not resolve its engine

- **WHEN** a fusion's artifact and producer recipe are current
- **THEN** artifact reuse performs no mesh-engine resolution or new union

#### Scenario: A weld check on meshes goes through the engine

- **WHEN** `assertJoined` compares two nodes that do not both have B-rep geometry, with the
  mesh engine available
- **THEN** the union whose components it counts is computed by the mesh engine,
  `trimesh.boolean` is not called, and the count is the one it was before

### Requirement: An unavailable mesh engine fails actionably at the point of use

When a requiring path is reached and the mesh engine's provider module cannot
be found, or is found but refuses because `manifold3d`, which its `mesh`
extra installs, cannot be found, the system SHALL raise one error that names the
mesh engine, the operation that needed it, why that operation needs it, and the
install line `pip install "machinome[mesh]"`, before any geometry work is
attempted. The error SHALL be raised at the requiring operation, not at module
import, and it SHALL NOT surface as a bare `ModuleNotFoundError` from framework
internals.

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

The framework SHALL declare the `mesh` extra, so the install line it names
installs the engine's kernel.

#### Scenario: A faceted interference check names the missing dependency

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

#### Scenario: A faceted run refuses at its start

- **WHEN** `machinome test --mesh`, or `machinome test` with
  `SOLID_TEST_ENGINE=mesh`, runs where the mesh engine is absent
- **THEN** it exits with status 1 and an error naming `machinome test on the
  mesh engine`, the mesh engine and `pip install "machinome[mesh]"`,
  before any node is built and before the mesh engine's line is printed

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
- **THEN** it declares a `mesh` extra

### Requirement: The core declares the mesh engine contract and checks the provider's

The core SHALL declare, in its mesh engine seam in the engine package
`machinome.engine`, one integer, `MESH_CONTRACT`, the mesh engine contract
version it speaks, beside the operations that
contract comprises, named as the provider defines them. The provider declares
the version it implements under the `mesh-engine` capability.

When the engine is resolved, the system SHALL compare the two by equality. When
they differ, or the provider declares none, both `mesh_engine()` and
`require_mesh_engine()` SHALL refuse with one error naming the provider module,
the contract version the core speaks, and the version the provider declares or
that it declares none. No mesh operation SHALL run against a provider that was
refused.

`require_mesh_engine(needed_by, reason)` SHALL return the resolved provider,
whose operations the core calls by name.

#### Scenario: A matching engine is resolved

- **WHEN** the provider declares the contract version the core speaks
- **THEN** `mesh_engine()` returns the provider, and it offers every operation
  the contract names

#### Scenario: A mismatched engine is refused naming both versions

- **WHEN** the provider declares contract version 2 and the core speaks 1
- **THEN** resolving the engine raises an error naming
  `machinome.engine.mesh`, version 1 and version 2, and no mesh operation
  runs

#### Scenario: An engine that declares no version is refused

- **WHEN** the provider module declares no contract version
- **THEN** resolving the engine raises an error naming the core's version and
  stating that the provider declares none

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

Outside the provider module `machinome/engine/mesh.py`, no core module SHALL
import `manifold3d` or call `trimesh.boolean`.

#### Scenario: The core imports no mesh kernel

- **WHEN** every module under `machinome/` is scanned for imports of
  `manifold3d` and for references to `trimesh.boolean`
- **THEN** `manifold3d` is imported only in `machinome/engine/mesh.py`, and
  `trimesh.boolean` is referenced by no module

#### Scenario: The test framework orders, the engine operates

- **WHEN** a mesh pair is compared by an intersection assertion
- **THEN** every solid built, every admission judged, every placement,
  intersection, emptiness and volume it uses is an operation of the mesh engine,
  directly or through a core cache

### Requirement: The core names its mesh engine in one place

The mesh engine's provider SHALL be the module `machinome.engine.mesh`. The
core SHALL name that provider in exactly one module, the engine package's
`__init__` (`machinome/engine/__init__.py`), which holds the seam; every
other core path SHALL reach the engine through the seam. The seam's names
SHALL be `mesh_engine`, `require_mesh_engine`, `MeshEngineUnavailable`,
`MeshEngineIncompatible`, `MESH_CONTRACT` and `MESH_PROVIDER`, none of which
is the provider module's own name, so resolving the provider never rebinds
a seam name on the package.

#### Scenario: The seam is the only place the provider is named

- **WHEN** every module under `machinome/` outside the provider module itself
  is scanned for imports and whole-string spellings of `machinome.engine.mesh`
- **THEN** the only module that names it is `machinome/engine/__init__.py`

#### Scenario: Resolving the provider leaves the seam callable

- **WHEN** `mesh_engine()` has resolved the provider and set the attribute
  `mesh` of the package `machinome.engine` to the provider module
- **THEN** `machinome.engine.mesh_engine` is still the seam function and a
  second call returns the same provider

