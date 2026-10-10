## ADDED Requirements

### Requirement: The engine is one module under a package that exports nothing

The OCCT exact engine SHALL be the module `machinome.occt.engine`. It SHALL be
both the provider the core's exact engine seam resolves and the module that
defines the exact operations a project calls directly. Every operation SHALL be
defined once, in that module, under one name; the engine SHALL NOT define a
second function for an operation it already offers, and no other module SHALL
re-export one. Its package `machinome.occt` SHALL export no name of its own.

#### Scenario: The package exports nothing

- **WHEN** a consumer reads an engine operation off `machinome.occt`
- **THEN** `AttributeError` is raised, and `machinome.occt.engine` is the only
  path to it

#### Scenario: One name per operation

- **WHEN** the operations the core's contract names are read off
  `machinome.occt.engine`
- **THEN** each is a function defined in that module, and the five
  project-facing operations are among them under the same names

### Requirement: The engine's currency is the kernel's own shape

The engine SHALL pass exact geometry around as the OCCT kernel's own object,
an `OCP.TopoDS.TopoDS_Shape` or one of its subtypes, and SHALL add no type of
its own around it. Every operation that returns geometry SHALL return that
type; every operation that takes geometry SHALL accept it.

`as_shape(obj)` SHALL return `obj` itself when it is a `TopoDS_Shape`, else
the `TopoDS_Shape` it carries as its `.wrapped` attribute, the convention
CadQuery and build123d objects share, and SHALL otherwise raise `TypeError`
naming the type it was given. It SHALL NOT copy, heal, tessellate or
otherwise translate the shape. `compound(shapes)` SHALL return one compound
holding every shape given, in order.

#### Scenario: A bare shape is its own currency

- **WHEN** `as_shape` is given a `TopoDS_Shape`
- **THEN** it returns that very object

#### Scenario: A front-end object is unwrapped

- **WHEN** `as_shape` is given a CadQuery `Shape` or a build123d `Part`
- **THEN** it returns the very `TopoDS_Shape` that object holds as `.wrapped`

#### Scenario: Anything else is refused

- **WHEN** `as_shape` is given an object that is neither
- **THEN** it raises `TypeError` naming that object's type

### Requirement: The engine declares the contract version it implements

The engine SHALL declare, as the module attribute `CONTRACT` and as its own
integer literal, the version of the core's exact engine contract it
implements, and SHALL never compute it from the core's declaration. This
engine implements version 1.

#### Scenario: The declaration is a literal

- **WHEN** the engine module's source is read
- **THEN** `CONTRACT` is assigned an integer literal, and its value is 1

### Requirement: The engine imports the kernel and nothing above it

The engine SHALL perform every operation on the OCCT kernel through OCP, with
numpy for arrays. Importing it, and running any of its operations, SHALL NOT
import `cadquery`, `build123d` or `trimesh`. From the framework it SHALL import
only the core's exact engine contract module, for the error types it raises,
and never a framework internal such as artifact publication, currency or a
cache.

The engine SHALL keep no state between calls: every operation is a function of
its arguments, and caching the results is its caller's choice.

#### Scenario: The engine runs without a front end

- **WHEN** a fresh interpreter imports the engine and reads, places, fuses,
  intersects, measures and writes a shape with it
- **THEN** neither `cadquery`, `build123d` nor `trimesh` is among the imported
  modules

### Requirement: Direct exact operations

The engine SHALL provide the exact operations a project or a test may call
directly on exact shapes, with these signatures:

- `intersect_shapes(first, second, first_name, second_name)`, the native
  common of two placed shapes;
- `fuse_shapes(first, second, first_name, second_name)`, their native fuse;
- `placed_shape(shape, matrix)`, the shape placed by a framework composed 4×4
  matrix;
- `solid_count(shape)`, the number of solids;
- `solid_volume(shape)`, the sum of the solids' volumes.

Each SHALL accept the currency or an object `as_shape` admits, SHALL return the
currency or a plain number, and SHALL keep no cache. A project imports them
from `machinome.occt.engine`, the one path; the core reaches the same
functions through its seam.

#### Scenario: A project intersects two placed shapes

- **WHEN** a project calls `intersect_shapes` on two overlapping placed
  `shape()` results
- **THEN** it returns a `TopoDS_Shape` whose `solid_volume` is the overlap
  volume

#### Scenario: A front-end shape is accepted as an argument

- **WHEN** a project passes a CadQuery `Shape` to `solid_volume`
- **THEN** it returns the volume of the kernel object that shape wraps

### Requirement: Booleans copy their operands and report failure

`intersect_shapes` and `fuse_shapes` SHALL run OCCT's default Common and Fuse
on private exact copies of both operands, in parallel mode, so that the
caller's shapes keep their subshape tolerances and topology for later
operations. When the kernel reports the operation not done, or raises, the
engine SHALL raise a `RuntimeError` naming the operation and both names it was
given. It SHALL NOT substitute a mesh result, heal, or apply a fuzzy
tolerance.

#### Scenario: Operands survive a Boolean

- **WHEN** one shape is intersected with several others in turn
- **THEN** its subshape tolerances are unchanged after each operation

#### Scenario: A failed Boolean names both shapes

- **WHEN** the kernel reports a Common not done for shapes named `Frame` and
  `Ball`
- **THEN** the engine raises an error naming the intersection, `Frame` and
  `Ball`

### Requirement: An empty common is verified before it is returned

When the Common of `intersect_shapes` holds no solid, the engine SHALL search,
within a finite budget, for one point classified inside a solid of each
operand by zero-tolerance solid classifiers and separated from every boundary
face of those solids by more than that face's native tolerance, starting from
points on the operands' native section. Neither operand SHALL be modified by
the search.

- When such a point is found, the engine SHALL raise
  `ExactCommonInconsistency` naming both shapes and the point, and SHALL NOT
  infer an overlap volume.
- When the section, a classifier, a face distance or a face tolerance cannot
  be evaluated, it SHALL raise `ExactCommonVerificationError` naming both
  shapes.
- When the search ends without such a point, it SHALL return the empty
  Common, without claiming that the emptiness is certified.

Both error types SHALL be those the core's exact engine contract module
defines, so a caller catches them without importing the engine.

#### Scenario: A witnessed false empty is refused

- **WHEN** the Common of two solids is empty but a point lies inside both
  beyond their native face tolerances
- **THEN** `intersect_shapes` raises `ExactCommonInconsistency` and returns no
  shape

#### Scenario: Boundary contact is not a witness

- **WHEN** two solids only touch on a face and every candidate point lies
  within a face's native tolerance
- **THEN** `intersect_shapes` returns the empty Common

#### Scenario: A failed check refuses

- **WHEN** the section used to verify an empty Common cannot be built
- **THEN** `intersect_shapes` raises `ExactCommonVerificationError`

### Requirement: Placement uses the exact matrix values

`placed_shape(shape, matrix)` SHALL place the shape by the upper three rows of
the 4×4 matrix, sent to the kernel as the exact IEEE-754 values the matrix
holds, with no tolerance or rounding of its own, and SHALL return a new shape
leaving its argument unchanged.

#### Scenario: A translation places the shape

- **WHEN** a unit cube at the origin is placed by a matrix translating it by
  (10, 0, 0)
- **THEN** the result's bounds run from x = 10 to x = 11 and the argument's are
  unchanged

### Requirement: Measurements are functions of the exact geometry

`bounds(shape)` SHALL return the shape's optimal axis-aligned bounding box as
`((xmin, ymin, zmin), (xmax, ymax, zmax))`. `face_bounds(shape)` SHALL return
one axis-aligned box per face, in the kernel's face order, as an `(F, 2, 3)`
float64 array, each box enclosing its face's exact surface with OCCT's own
tolerance enlargement and taken without reading any triangulation the shape
carries; a shape with no faces gives a `(0, 2, 3)` array.

`mutually_outside(first, second)` SHALL answer `True` only when one vertex of
every solid of each placed shape classifies strictly outside every solid of
the other, at the kernel's confusion tolerance, in both directions. It SHALL
answer `False`, declining, for a shape with no solid, a solid with no vertex,
a classification refused or failed, and any state other than outside.

#### Scenario: A triangulation does not change a face box

- **WHEN** a curved shape's face bounds are read before and after a
  tessellation is attached to it
- **THEN** both arrays are equal and enclose the exact curved surface

#### Scenario: A contained solid is not mutually outside

- **WHEN** a small solid lies wholly inside a larger one
- **THEN** `mutually_outside` answers `False` in either argument order

### Requirement: The engine reads and writes exact artifacts byte for byte

`read_brep(path)` SHALL read a BREP file into the currency and raise
`ValueError` naming the path when the result is null. `write_brep(shape,
path)` SHALL write the shape's BREP to `path`. `write_stl(shape, path,
linear_deflection, angular_deflection)` SHALL tessellate the shape at those
deflections and write a binary STL to `path`, and nothing else: the
degenerate-triangle cleanup and the publication of the artifact are the
caller's.

For the same shape and parameters, `write_brep` and `write_stl` SHALL write
the same bytes CadQuery 2.7's `exportBrep` and `exportStl(tolerance,
angularTolerance)` write, so artifacts built before the engine and after it
are interchangeable.

#### Scenario: A BREP round-trips

- **WHEN** a shape is written with `write_brep` and read back with
  `read_brep`
- **THEN** the read shape has the same solid count and volume

#### Scenario: The bytes match CadQuery's exporters

- **WHEN** a fused solid is written by the engine and by CadQuery's exporters
  at the same deflections, in separate processes
- **THEN** the BREP and STL files have the same SHA-256 each way
