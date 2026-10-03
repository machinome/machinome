## MODIFIED Requirements

### Requirement: The test framework does not import the exact-geometry stack

The system SHALL resolve the exact engine, and through it the
boundary-representation stack, at the exact path's first use rather than at
`machinome.test` module scope. Importing `machinome.test` in a fresh
interpreter SHALL NOT import `cadquery`, `OCP` or the exact engine.

This completes the deferral the loader requirement already states from the
other side: loading a node imports neither the test framework nor cadquery,
and importing the test framework imports neither cadquery nor the kernel. A
project that models entirely in solid2 and asserts entirely over meshes
therefore runs its tests without ever loading the exact stack.

The deferral SHALL NOT make exact geometry optional or change any exact
verdict. A comparison between two exact nodes SHALL resolve the exact engine
through the seam the `exact-engine-dependency` capability specifies and
produce the same result as before; only the moment of the import moves.

The exact path SHALL look up each name it calls where that name is defined,
at the moment of the call: an engine operation (`intersect_shapes`,
`fuse_shapes`, `placed_shape`, `solid_count`, `solid_volume`, `bounds`,
`face_bounds`, `mutually_outside`) as an attribute of the resolved engine, and
a core memo (`cached_bounding_box`, `cached_face_boxes`, `cached_placement`,
`shape_identity`, `shape_load_observation`) as an attribute of the core module
that defines it. A caller that patches a name in its defining module SHALL
therefore be honoured whether or not an exact comparison has yet run.
`machinome.test` SHALL NOT bind those names as attributes of its own, so each
keeps one path.

A failure to import the exact engine SHALL surface under the existing
deferred-import requirement and the `exact-engine-dependency` capability: an
absent engine is refused naming its install, a broken one raises its own
import error at first use, and neither is swallowed or substituted.

#### Scenario: Importing the test framework loads no exact stack

- **WHEN** `machinome.test` is imported in a fresh interpreter
- **THEN** `cadquery`, `OCP` and the exact engine module are absent from
  `sys.modules`

#### Scenario: A faceted project's test run loads no exact stack

- **WHEN** a project whose nodes are all faceted runs its tests to completion
- **THEN** the run reports the same results as today and `cadquery`, `OCP` and
  the exact engine module are absent from `sys.modules`

#### Scenario: An exact comparison still loads the stack

- **WHEN** two exact nodes are compared by an intersection assertion
- **THEN** the exact engine is resolved and the comparison returns the verdict
  it returns today

#### Scenario: A name patched where it is defined is used

- **WHEN** a caller patches `intersect_shapes` on the engine module, or
  `cached_face_boxes` on the core module that defines it, before any exact
  comparison has run
- **THEN** the exact path uses the patched object
