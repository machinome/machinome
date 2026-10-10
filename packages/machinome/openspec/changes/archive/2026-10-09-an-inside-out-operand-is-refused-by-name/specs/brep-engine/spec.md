## MODIFIED Requirements

### Requirement: An empty common is verified before it is returned

When the Common of `intersect_shapes` holds no solid, the engine SHALL search,
within a finite budget, for one point classified inside a solid of each
operand by zero-tolerance solid classifiers and separated from every boundary
face of those solids by more than that face's native tolerance, starting from
points on the operands' native section. Such a point SHALL count only when the
six points at half its smaller distance to the two solids' faces, one along
each of ±x, ±y and ±z, are also classified inside those same two solids by
the same zero-tolerance classifiers; a point whose neighbours are not all
inside both SHALL be skipped and the search SHALL continue. Neither operand
SHALL be modified by the search.

- When such a point is found, the engine SHALL raise
  `BrepCommonInconsistency` naming both shapes and the point, and SHALL NOT
  infer an overlap volume.
- When the section, a classifier, a face distance or a face tolerance cannot
  be evaluated, it SHALL raise `BrepCommonVerificationError` naming both
  shapes.
- When the search ends without such a point, it SHALL return the empty
  Common, without claiming that the emptiness is certified.
- When a solid of either operand is inside out, its signed volume negative,
  the engine SHALL NOT consult a classifier on either operand and SHALL
  raise `BrepCommonVerificationError` naming that operand as inside out,
  with its signed volume, and SHALL NOT claim a shared point. The common
  itself, and a non-empty common's volume, are computed and returned as
  for any operand.

Both error types SHALL be those the engine package `machinome.engine`
defines, so a caller catches them without importing the engine.

#### Scenario: A witnessed false empty is refused

- **WHEN** the Common of two solids is empty but a point lies inside both
  beyond their native face tolerances
- **THEN** `intersect_shapes` raises `BrepCommonInconsistency` and returns no
  shape

#### Scenario: Boundary contact is not a witness

- **WHEN** two solids only touch on a face and every candidate point lies
  within a face's native tolerance
- **THEN** `intersect_shapes` returns the empty Common

#### Scenario: A failed check refuses

- **WHEN** the section used to verify an empty Common cannot be built
- **THEN** `intersect_shapes` raises `BrepCommonVerificationError`

#### Scenario: A lone inside reading is not a witness

- **WHEN** two solids only touch on a face, their Common is empty, and one
  solid's classifier reports inside at a single point beyond every face
  tolerance while reporting outside at that point's neighbours
- **THEN** `intersect_shapes` returns the empty Common

#### Scenario: An inside-out operand is refused by name

- **WHEN** the Common of a normal solid and an inside-out solid touching it
  is empty
- **THEN** `intersect_shapes` raises `BrepCommonVerificationError` naming the
  inside-out operand and its negative signed volume, and names no shared
  point

### Requirement: Measurements are functions of the B-rep geometry

`bounds(shape)` SHALL return the shape's optimal axis-aligned bounding box as
`((xmin, ymin, zmin), (xmax, ymax, zmax))`. `face_bounds(shape)` SHALL return
one axis-aligned box per face, in the kernel's face order, as an `(F, 2, 3)`
float64 array, each box enclosing its face's B-rep surface with OCCT's own
tolerance enlargement and taken without reading any triangulation the shape
carries; a shape with no faces gives a `(0, 2, 3)` array.

`mutually_outside(first, second)` SHALL answer `True` only when one vertex of
every solid of each placed shape classifies strictly outside every solid of
the other, at the kernel's confusion tolerance, in both directions. It SHALL
answer `False`, declining, for a shape with no solid, a solid with no vertex,
a classification refused or failed, and any state other than outside. For
an operand holding an inside-out solid, one of negative signed volume, it
SHALL decline without loading a classifier, since that classifier would read
every point as inside.

A distance the engine measures between two shapes SHALL be the kernel's
minimal distance, asked of an extrema that is told to run on every core the
host offers before it performs, so that the flag governs the computation
rather than being set on a finished one.

#### Scenario: A triangulation does not change a face box

- **WHEN** a curved shape's face bounds are read before and after a
  tessellation is attached to it
- **THEN** both arrays are equal and enclose the exact curved surface

#### Scenario: A contained solid is not mutually outside

- **WHEN** a small solid lies wholly inside a larger one
- **THEN** `mutually_outside` answers `False` in either argument order

#### Scenario: The distance is asked threaded

- **WHEN** the engine measures the distance between two shapes
- **THEN** the kernel's extrema is told to run multithreaded before it
  performs, and the value is the minimal distance between the shapes

#### Scenario: An inside-out operand declines the containment guard

- **WHEN** `mutually_outside` is asked about a normal solid and an inside-out
  solid far from it
- **THEN** it answers `False` in either argument order and constructs no
  classifier
