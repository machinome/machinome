# mesh-engine Specification

## Purpose
The manifold3d mesh engine, `machinome.engine.mesh`: the provider the core's
mesh engine seam resolves, the contract version it declares, what it imports
and how it refuses an absent `manifold3d`, and each operation it performs on
a mesh solid. It governs behaviour that leaves the core with the engine's
package at the cut. Encodes ADR-176 and ADR-180.
## Requirements
### Requirement: The engine is one module of the engine package

The manifold3d mesh engine SHALL be the module `machinome.engine.mesh`, a
module of the engine package `machinome.engine`, whose `__init__` holds the
core's seams and none of the engine's operations, and the provider the core's
mesh engine seam resolves. Every operation of the mesh engine contract SHALL
be defined once, in that module, under the name the contract uses. The module
SHALL offer no operation a project is meant to call: a project that wants
manifold3d imports it.

#### Scenario: The package holds no operation

- **WHEN** a consumer reads an engine operation, such as `intersect_solids`,
  off the package `machinome.engine`
- **THEN** `AttributeError` is raised, and `machinome.engine.mesh` is the
  only path to it

#### Scenario: One name per operation

- **WHEN** the operations the core's mesh engine contract names are read off
  `machinome.engine.mesh`
- **THEN** each is a function defined in that module

### Requirement: The engine declares the contract version it implements

The engine SHALL declare, as the module attribute `CONTRACT` and as its own
integer literal, the version of the core's mesh engine contract it implements,
and SHALL never compute it from the core's declaration. This engine implements
version 1.

#### Scenario: The declaration is a literal

- **WHEN** the engine module's source is read
- **THEN** `CONTRACT` is assigned an integer literal, and its value is 1

### Requirement: The engine imports its kernel and nothing above it

The engine SHALL perform every operation through `manifold3d`, with numpy for
arrays. Importing it, and running any of its operations, SHALL NOT import
`trimesh`, `OCP`, `cadquery` or `build123d`. From the framework it SHALL import
only the core's extras module, for the refusal it raises when `manifold3d`
cannot be found; never a cache, the verdict store or the test framework, and
none of the seams' names, although Python imports its package's `__init__`
before it.

Before it imports `manifold3d`, the engine SHALL check that `manifold3d` can be
found, without importing it, and refuse an absent `manifold3d` with the
`kernel-extras` capability's refusal naming the mesh engine
(`machinome.engine.mesh`) and `pip install "machinome[mesh]"`.

The engine SHALL keep no state between calls, read no file and write none:
every operation is a function of its arguments, and caching its results is its
caller's choice.

#### Scenario: The engine runs without the mesh library

- **WHEN** a fresh interpreter imports the engine and builds, admits, places,
  intersects, unites, measures and meshes back solids with it
- **THEN** neither `trimesh`, `OCP`, `cadquery` nor `build123d` is among the
  imported modules

#### Scenario: The engine without its kernel refuses by its extra

- **WHEN** `machinome.engine.mesh` is imported where `manifold3d` cannot be
  found
- **THEN** a `ModuleNotFoundError` is raised whose `name` is `manifold3d` and
  whose message names the mesh engine and `pip install "machinome[mesh]"`

### Requirement: Solids are built from triangle meshes and judged by the engine

The engine's solid SHALL be manifold3d's own object, passed to the core as an
opaque handle. `solid_from_mesh(vertices, faces)` SHALL build a solid from a
triangle mesh, its vertex positions taken as 32-bit floats and its triangle
indices as unsigned 32-bit integers, as the framework built them before the
engine was a provider. `fault(solid)` SHALL answer `None` when manifold3d
admits the solid it built, and otherwise manifold3d's own name for the fault,
such as `NotManifold`. `mesh_arrays(solid)` SHALL answer the solid's triangle
mesh as `(vertices, faces)`, the vertex positions and the triangle indices
manifold3d returns, unconverted. `centred_box(size)` SHALL build a box of the
three given extents centred on the origin.

#### Scenario: A box missing a triangle is refused by name

- **WHEN** `solid_from_mesh` is given a unit box with one triangle removed
- **THEN** `fault` of the result is `NotManifold`

#### Scenario: A closed mesh is admitted and read back

- **WHEN** `solid_from_mesh` is given a closed box mesh
- **THEN** `fault` of the result is `None`, and `mesh_arrays` of it answers
  vertex positions with three columns and triangles whose count is that of a
  closed box

### Requirement: Solids are placed and combined as the framework combined them

`placed_solid(solid, matrix)` SHALL return the solid placed by the upper three
rows of the framework's composed 4x4 matrix, sent as their exact values, and
SHALL re-mesh and re-judge nothing. `intersect_solids(first, second)` SHALL
return the intersection of two solids. `unite_solids(solids)` SHALL return their
union, folded left in the order given, one pair at a time; a single solid SHALL
be returned unchanged. `is_empty(solid)` and `volume(solid)` SHALL answer
manifold3d's own emptiness and volume of the solid; the engine SHALL NOT fold
a zero volume into emptiness.

Every operation SHALL compute what the framework computed before the engine
was a provider, from the same values, in the same order, so every verdict, every
refusal and every fused mesh is bit-identical.

#### Scenario: A flush contact stays non-empty

- **WHEN** two boxes that share one face exactly are placed and intersected
- **THEN** `is_empty` of the intersection is `False` and its `volume` is
  exactly `0.0`, as manifold3d reports it

#### Scenario: A union is the framework's own

- **WHEN** three solids are united
- **THEN** the result's `mesh_arrays` equal, byte for byte, those of the first
  solid united with the second and that result with the third

### Requirement: The engine names itself

`identity()` SHALL answer the engine's name and version as two strings: the
name `manifold3d` and the installed manifold3d distribution's version, read from
its metadata without importing anything further, or `None` for the version when
the metadata cannot be read.

#### Scenario: The identity names the installed kernel

- **WHEN** `identity()` is called with manifold3d installed from a wheel
- **THEN** it answers `('manifold3d', v)` where `v` is the version the
  distribution's metadata records

