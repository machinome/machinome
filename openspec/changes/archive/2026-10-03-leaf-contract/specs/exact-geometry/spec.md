## MODIFIED Requirements

### Requirement: Exact geometry is persisted and reloaded

An exact rigid node's shape SHALL be persisted as a build artifact and
reloaded from it, so that consumers do not re-run the project's geometry
backend to obtain it. A shape reloaded from a current artifact SHALL be
equivalent to the shape the node would render.

Loaded shapes SHALL be cached in memory per artifact observation: the
artifact's path together with the device, inode, size, modification time and
status-change time a `stat` of it reports. A request whose observation differs
from the cached one SHALL load the file again and evict every entry cached for
that path, in the manner of the existing base-mesh cache. Because every
artifact the framework publishes replaces its predecessor by renaming a newly
written file into place, a replaced `.brep` is a different observation even
when its stamped modification time is equal to its predecessor's, so a shape
SHALL never be served from a replaced artifact, and no node SHALL need to
evict the cache itself.

The observation the shape was loaded from SHALL be recorded beside it only
when the file was the same observation before and after the read; the
persistent verdict store (ADR-156) digests the bytes of exactly that
observation, and a shape loaded incoherently has no persistent identity.

Measurements DERIVED from a loaded shape and independent of where it is
placed — its own bounding box, and the bounding boxes of its faces — SHALL be
cached under that same shape identity, computed at most once per identity, and
evicted with it when its artifact is rebuilt. A shape with no such identity —
one composed for a single comparison, or read from a node whose artifact is
not current — SHALL be measured directly and SHALL NOT be cached, so a stale
identity can never serve another shape's measurement.

Because such a measurement is served under an identity that names only the
artifact and its observation, it SHALL be a function of the shape's EXACT
geometry alone. A face's cached bounding box SHALL enclose that face's exact
surface and SHALL NOT be derived from any triangulation the shape may carry,
so that attaching, replacing or discarding a tessellation cannot change a
measurement already served under that identity.

#### Scenario: A current artifact is reused

- **WHEN** an exact node's shape is requested and its artifact is current
- **THEN** the shape is read from the artifact and the geometry backend does
  not render the node

#### Scenario: A rebuilt artifact replaces its cached shape

- **WHEN** an exact node's source changes and its artifact is rebuilt
- **THEN** the next request returns the new shape and the entry cached under
  the previous observation is evicted

#### Scenario: A replacement under an unchanged source mtime is not served stale

- **WHEN** an exact leaf's shape has been loaded from its `.brep`, and the
  `.brep` is then published again with different geometry stamped with the
  same source mtime, as a node declaring a changed `source_recipe` does
- **THEN** the next `shape()` returns the new geometry, the old entry and its
  derived measurements and placements are evicted, and the node called
  nothing to invalidate them

#### Scenario: A repeated request costs no reload

- **WHEN** the same current `.brep` is requested twice and nothing has
  replaced it
- **THEN** the second request returns the very object the first returned,
  without reading the file

#### Scenario: A shape's face bounds are measured once and evicted with it

- **WHEN** the bounding boxes of a loaded shape's faces are requested
  repeatedly, and then its artifact is rebuilt
- **THEN** they are computed once for that identity and served from the cache
  afterwards, and the rebuild drops the entry so the next request measures the
  new shape

#### Scenario: A shape with no identity is measured directly

- **WHEN** the bounding boxes of the faces of a shape with no cache identity
  are requested
- **THEN** they are computed from that shape and no cache entry is created

#### Scenario: A triangulation does not shrink a face's bounds

- **WHEN** a curved exact shape carries a triangulation whose vertices lie on
  its surface, and its faces' bounding boxes are requested
- **THEN** each box still encloses the exact surface, reaching the true extent
  of the curved face rather than the tessellation's inscribed extent

### Requirement: An exact render is admitted by its kernel object

An exact leaf SHALL convert its render result to its exact geometry at the
adapter boundary, through its declared conversion hook
`shape_from_rendered(rendered)`, and the conversion SHALL be a rewrap of the
kernel object the result already holds, never a translation: no tessellation,
tolerance or healing SHALL occur in it. A subclass overriding the hook SHALL
keep that promise.

The hook's default SHALL accept a render result the exact engine admits as
its currency, by the engine's own admission rule, which the `occt-engine`
capability states. On top of that, `CadQueryNode` and `StepNode` SHALL accept
a CadQuery `Workplane`, taking its values and composing several into one
compound, and `Build123dNode` SHALL accept a build123d builder, taking its
finished part, as they do today. A result none of these describes SHALL be
refused naming the node and the result's type.

The conversion SHALL run only where a stale artifact is about to be written
or a stale node's `shape()` is read, so a leaf whose artifacts are current
never resolves the exact engine to convert.

Admission SHALL NOT require a `namespace`: an exact leaf whose render returns
the engine's currency declares none, and the `leaf-contract` capability's
namespace guard, when a leaf declares one, is only an earlier refusal by
module.

#### Scenario: A render in the engine's currency is accepted

- **WHEN** an exact leaf with no `namespace` whose render returns the
  engine's currency itself is built
- **THEN** its `.brep` and `.stl` are written and its `shape()` is that solid

#### Scenario: A front-end render is rewrapped

- **WHEN** an exact leaf whose render returns a CadQuery `Shape` or a
  build123d `Part` is built
- **THEN** its `shape()` holds the very kernel object the render held, with
  the same volume

#### Scenario: A workplane of several solids becomes one compound

- **WHEN** a `CadQueryNode` renders a `Workplane` holding two disjoint solids
- **THEN** its `shape()` is one compound holding both

#### Scenario: An unconvertible render is refused naming the node

- **WHEN** an exact leaf with no `namespace` renders an object the engine
  does not admit and its hook does not convert
- **THEN** building it raises naming the node and the object's type, and no
  `.brep` or `.stl` is written
