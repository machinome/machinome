## MODIFIED Requirements

### Requirement: What a leaf provides, by kind

A subclass SHALL provide its geometry through the members of its kind, and
the core SHALL do everything else:

- **Every leaf** implements `render()`, returning one geometry object, never a
  list and never `None`. It MAY extend `validate(rendered)`, calling the
  base's first. Its exactness is fixed by its type.
- **A faceted leaf presented as SCAD** implements `as_scad(rendered)`,
  returning a solid2 object. The core has the OpenSCAD engine write that SCAD
  as the leaf's own `.scad` (the `scad-engine-dependency` capability), the
  one kind of leaf whose `.scad` a build writes and keeps, and OpenSCAD
  produces the STL from it.
- **A faceted leaf that produces its own STL** implements
  `materialize(rendered)` and writes `stl_file` through `publish_artifact`.
  It need not implement `as_scad`: the core presents its artifact. A leaf
  that does implement it to present its own artifact returns
  `artifact_import(local_path)` as it is: the core's description of an import
  of that artifact, which is not a solid2 object and is not composed into
  one.
- **An exact leaf** returns from `render()` an object its conversion hook
  `shape_from_rendered(rendered)` turns into the exact engine's currency; the
  default hook admits whatever the engine admits as its currency, and a
  subclass whose front end returns something else overrides the hook. It MAY
  declare `linear_deflection` and `angular_deflection` as class attributes.
  The core writes its `.brep` and `.stl` and serves `shape()`.
- **A sheet leaf** implements `profile()` and the four backend hooks
  `profile_faces(profile)`, `lies_on_xy_plane(face)`, `extrude(face)` and
  `write_dxf(face, path)`, the last writing the cut file to the path it is
  given. `render()` is the base's and SHALL NOT be overridden.
- **A flexible leaf** declares one port per shape parameter, declares `tech`,
  returns its backend's shape object from `render()`, and implements the five
  backend hooks `shape_parameters(rendered)`, `shape_spec(rendered)`,
  `snapshot_mesh(rendered, values)`, `snapshot_stl(rendered, values)` and,
  when it declares `exact` true, `snapshot_shape(rendered, values)`.

A subclass MAY extend `materialize(rendered)` on any base by calling the
base's implementation; the artifacts it then holds are the ones the base
published.

A subclass that declares its own metaclass SHALL derive it from the metaclass
of the base it subclasses (`NodeMeta`, at `machinome.node.declarative`).

#### Scenario: A SCAD-presented faceted leaf needs no producer of its own

- **WHEN** a `LeafNode` subclass implements only `render()` and `as_scad()`
  returning a solid2 object, and is built with OpenSCAD available
- **THEN** its `.scad` is written by the core and its STL is rendered by
  OpenSCAD from it

#### Scenario: A leaf presents its own artifact by artifact_import

- **WHEN** a `LeafNode` subclass implements `materialize()` publishing its
  STL and `as_scad()` returning `self.artifact_import(self.local_stl)`
- **THEN** it is assembled, and when its parent's `.scad` is generated with
  the OpenSCAD engine installed, that SCAD imports the artifact by a path that
  resolves from the parent's `.scad` directory, exactly as a core adapter's
  does; a build writes no `.scad` for the leaf itself

#### Scenario: A self-materializing faceted leaf needs no SCAD hook

- **WHEN** a `LeafNode` subclass implements `render()` and `materialize()`
  publishing its STL, and no `as_scad()`
- **THEN** it is assembled, and its SCAD presentation imports its STL artifact

#### Scenario: A sheet leaf supplies the four hooks

- **WHEN** a `SheetLeafNode` subclass implements `profile()` and the four
  backend hooks by their public names
- **THEN** it builds its STL, BREP and DXF, and the sheet rules of the
  `sheet-parts` capability refuse its authoring mistakes as they refuse
  `Build123dSheetNode`'s

#### Scenario: A flexible leaf supplies the five hooks

- **WHEN** a `FlexibleNode` subclass declares a port per parameter, its `tech`,
  and implements the five backend hooks by their public names
- **THEN** it is published in the document as a flexible object, its snapshot
  STL is written per binding, and its `shape()` is evaluated at the bound
  instant, as `MolejoNode`'s are under the `flexible-parts` capability

#### Scenario: Extending materialize keeps the base's artifacts

- **WHEN** an `ExactLeafNode` subclass extends `materialize()` and calls the
  base's implementation inside it
- **THEN** the `.brep` and `.stl` written are those the base would have
  written, with the same stamps and source records
