---
name: solid-node-api
description: Complete public API reference for solid-node. Use when designing a mechanical project against solid-node capabilities, specifying nodes and kinematics without inspecting framework implementation, or implementing nodes, tests, viewer wiring, snapshots, and exports through supported public interfaces.
---

# solid-node public API

Use this as the authoritative public contract. Design and project code may rely
on this surface, never on implementation details discovered in framework
source. A caller's role card decides whether narrowly targeted source
inspection is allowed for diagnosis.

## Imports

```python
from solid_node.node import (
    AssemblyNode, FusionNode,
    CadQueryNode, Solid2Node,
    OpenScadNode, JScadNode,
    property_as_number,
)
from solid_node.test import (
    TestCase, TestCaseMixin, testing_instant, testing_steps)
from solid_node.math import (
    sin, cos, tan, asin, acos, atan, atan2, sqrt)   # DEGREES
```

## Node classes

- `CadQueryNode` — `render()` returns a `cadquery` Workplane. The
  framework exports it to STL.
- `Solid2Node` — `render()` returns a solid2 object. `as_number()`
  resolves a solid2 expression by running OpenSCAD once per call, so
  keep ordinary dimensions in Python where possible.
- `OpenScadNode` — declare `scad_source = 'file.scad'`, relative to
  the node's Python file. The module named after the file, or the
  explicitly declared `module_name`, receives the constructor's
  `*args/**kwargs`.
- `JScadNode` — declare `jscad_source`; requires the `jscad` CLI.
- `AssemblyNode` — `render()` returns persistent child nodes;
  `self.time` is available; the assembly is not rigid.
- `FusionNode` — `render()` returns children that fuse into one rigid,
  inseparable printed part and one STL. It has no `self.time`.
- `property_as_number` — turns a solid2-expression-valued method into
  a numerically resolved property.

A file containing several node classes must select the main class with
module-level `NODE = MyClass`, where `MyClass` is defined in that file.

## Construction and identity

All nodes accept `__init__(self, *args, name=None, **kwargs)`. The artifact key
is derived from the class, args, and sorted kwargs. Store each model parameter
on the instance and pass it to `super().__init__()` so parameter variants do
not share stale artifacts. `name=` affects tree identity, not artifact identity.

Leaf `render()` methods return native backend geometry. Assembly and fusion
children must persist: create them as instance attributes in `__init__`, not in
`render()` and not as class attributes. Attribute names become child names
(`self.input_gear` becomes `input_gear`); list members become `attr-0`,
`attr-1`, and so on. Explicit `name=` overrides this.

Class attributes:

- `color = '#RRGGBB'`
- `fn = N`
- `optimize` — defaults true; false preserves unflattened OpenSCAD viewer data
- `rigid` — true for leaves and fusions, false for assemblies

Instance surface:

- `.rotate(angle, axis)` and `.translate([x, y, z])` append an
  operation, return the node, and may be chained.
- `.operations` is the ordered Rotation/Translation list.
- `.mesh` is a fresh trimesh copy in world coordinates, including all
  ancestor operations.
- `.stl_file` is the built artifact path.
- `.name`, `.children`, `.time` (assemblies only).
- `.set_keyframe(t)` propagates the numeric time through a tree.
- `.assemble()` then `.build_stls()` prepares an independently created
  node for mesh use.
- `.save_checkpoint()` and `.restore_checkpoint()` mark and roll back
  the operations list.

Builds go to `_build/`, or `SOLID_BUILD_DIR`, as parameter-keyed STLs. An
artifact rebuilds when its sources are newer.

## Placement and animation

Operations apply in order. A node's local operations apply before ancestor
placement, so spinning around a local axis before translating into place is the
normal sequence.

- Apply static placement once in an assembly's `__init__`.
- State time-dependent operations in `render()` using `self.time` from
  0 through 1. Rendering restores nodes to their pre-render operation
  checkpoints, so `render()` expresses the absolute pose at one instant.
- Use `solid_node.math`, never standard-library math, for kinematics.
  Its trigonometry uses degrees and supports both numeric test values
  and symbolic viewer expressions.
- A parent assembly may operate on a descendant leaf. Wrapper
  assemblies remain useful when static placement and local rotation
  need separate frames.

## Test surface

Tests for `root/foo.py` live in `root/test_foo.py`; a package rooted at
`root/__init__.py` uses `root/test.py`. Subclass `solid_node.test.TestCase`.
The runner exposes the built node as `self.node` and as the snake-case name of
the test class (`SpurGearTest` gives `self.spur_gear`).

```python
assertNotIntersecting(node1, node2)
assertIntersecting(node1, node2)
assertInside(outer, inner)
assertClose(node1, node2, max_distance)
assertFar(node1, node2, min_distance)
assertIntersectVolumeAbove(node1, node2, min_volume)
assertIntersectVolumeBelow(node1, node2, max_volume)
assertBlockedBeyond(node, amount, against, axis=None,
                    volume_epsilon=0.0, along=None, directions='both')
assertFreeWithin(node, amount, against, axis=None,
                 volume_epsilon=0.0, along=None, directions='both')
assertNoPairwiseIntersections(root, volume_epsilon=0.0)
```

`assertClose` bounds every vertex of the second node within a maximum distance
of the first; `assertFar` requires every vertex to remain at least the minimum
distance away. The perturbation assertions rotate locally by default; pass
`along=(x, y, z)` for linear displacement, `directions='forward'` for an
intentional one-sided constraint, and a sequence of amounts to
`assertFreeWithin` for a sweep. Directions are local and follow placement.

Use `@testing_instant(t)` to pin time and `@testing_steps(n, start=0, end=1)`
to sweep it. A node created inside a test needs `.assemble()` and
`.build_stls()` before `.mesh` is available. Intersection assertions use a
fast cached path for watertight built STLs. `mesh.contains` requires `rtree`;
`trimesh.proximity` requires `scipy`.

The test runner builds at keyframe 0 before tests, runs node mixin and test-case
methods alphabetically with `setUp`/`tearDown`, sets each requested keyframe,
and restores operation state between instants. Any failure exits nonzero;
`--failfast` stops at the first.

## CLI

```text
solid new <name>
solid build <path>
solid develop <path> [--web-dev] [--openscad] [--debug-builder] [--debug-web] [--callback URL]
solid test <path> [--failfast]
solid snapshot <path> -o out.png [--time 0..1] [--autocenter] [--viewall]
      [--camera tx,ty,tz,rx,ry,rz,dist | ex,ey,ez,cx,cy,cz]
      [--imgsize 1920x1080] [--projection ortho|perspective]
      [--colorscheme Cornfield|Metallic|...] [--preview]
      [--view axes,crosshairs,edges,scales,wireframe]
solid export <path> [-o export] [--fps 30] [--frames 360] [--no-widget]
```

The command comes first in the v0.4 grammar. The CLI loads `./.env` at
startup, with the real environment taking precedence:

- `SOLID_NODE_PORT` — viewer, default 8000
- `SOLID_NODE_FRONTEND_PORT` — frontend dev server, default 3000
- `SOLID_BUILD_DIR` — artifact directory, default `_build`

Snapshots self-wrap with `xvfb-run` when headless. Export writes
`manifest.json`, deduplicated models, and—unless `--no-widget`—a
self-contained viewer.

## Published build artifacts

`solid build` renders once and publishes the complete current model, then
exits: zero when the build is current, nonzero when it failed. It is the
finite form of what `solid develop` does on every save, and it is how a
process that must not serve the model still verifies one.

`SOLID_BUILD_DIR` (default `_build`) is a symlink to a versioned sibling
directory. Each publication renames a completed candidate into a fresh
version and atomically moves the symlink onto it, dropping the previous
one; a reader following the link therefore sees one complete artifact set
or the next, never a mixture. Hold the symlink path and resolve it at each
use — a resolved path names one publication and stops existing at the next.

Inside a publication:

- `viewer.json` — `{version, animation: {fps, frames}, root}`, where the
  node tree carries the same `name`, `type`, `color`, `mtime`,
  `operations`, and either `children` or a rigid node's `model` path
  relative to the build directory.
- the rendered STLs, at the `model` paths `viewer.json` names.
- `errors.json` — `{error, tstamp}`, written into the build path instead
  of a publication when a build fails, so the previous model keeps
  serving.

## Viewer HTTP surface

`solid develop` serves this; a build publication does not. With it running
on `SOLID_NODE_PORT`:

- `GET /node/` — root JSON containing operations, type, name, color,
  mtime, and child names.
- `GET /node/<Child>/.../` — nested state. A rigid node exposes a
  `model` instead of children.
- `GET /node/<path>/<Name>.stl` — the STL; waits for its file to exist.
- `GET /_build_error` — `{}` when clean, otherwise the active build error.
- `WS /ws/reload` — viewer reload signal.

Operations serialize as rotation/translation tuples with raw expressions;
animated expressions retain symbolic `$t`.
