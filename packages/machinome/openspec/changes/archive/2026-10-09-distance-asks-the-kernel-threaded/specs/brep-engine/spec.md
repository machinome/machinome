## MODIFIED Requirements

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
a classification refused or failed, and any state other than outside.

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
