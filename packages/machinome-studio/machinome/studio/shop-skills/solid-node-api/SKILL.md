---
name: solid-node-api
description: Complete public API reference for solid-node. Use when designing a mechanical project against solid-node capabilities, specifying nodes and kinematics without inspecting framework implementation, or implementing nodes, tests, viewer wiring, snapshots, and exports through supported public interfaces.
---

# solid-node public API

Use this as the authoritative public contract. It is the whole of what a
project may rely on: framework source is not available to you, so a behavior
this document does not describe is a gap to report, not a thing to discover.
Never guess an interface from a symbol name.

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
  inseparable printed part and one STL. It has no `self.time`, and every
  child must itself be rigid: you fuse solids, then assemble them. A
  non-rigid child raises at validation.
- `property_as_number` — turns a solid2-expression-valued method into
  a numerically resolved property.

## One node per file

A file defines one node class. This is the framework's premise, not a style
preference: a node's artifacts are invalidated by the file it lives in, so two
nodes sharing a file rebuild together forever. See the source-set rules below
and the `solid-node` skill for the discipline.

A file that defines several node classes has no main class and no way to
declare one. Every reference to it must name the class
(`path/to/file.py:Class`); a bare path fails as ambiguous, listing the
candidates. `solid build` and `solid snapshot` therefore cannot use a bare
path to such a file at all, and `solid test` is the sole exception — it tests
every node the file defines, as one run.

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
- `rigid` — determined by node type and not settable: true for leaves and
  fusions, false for assemblies.

There is no `bodies` declaration. Connectivity is not a build-time check and
the build never opens an STL to count components; it is a project test
contract (see the test surface below).

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

Builds go to `_build/`, or `SOLID_BUILD_DIR`, as parameter-keyed STLs.

An artifact rebuilds when any file in the node's **source set** is newer than
it. That set is the node's own file plus the transitive closure of the
project-local modules that file imports, resolved statically from the source
text; the framework and anything outside the project tree are libraries and
are not tracked. Internal nodes union in their children's sets, so a leaf's
edit invalidates the assemblies above it and nothing sideways.

Three consequences:

- Editing a module that defines no node — a `parameters.py` or
  `kinematics.py` — correctly invalidates exactly the nodes that import it.
- The walk never follows a package's `__init__.py`. A value reached through
  the package rather than through a named module is therefore **not tracked**
  and its edit will serve a stale model. Import shared values from the module
  that defines them, never from the package.
- A leaf that is current is not rendered at all: `assemble()` may call
  `render()` zero times, not once. Nothing may depend on a render side
  effect. The skip trusts the source set, so geometry that depends on
  something a static import walk cannot see — a data file read at runtime, a
  module reached through `importlib`, an environment variable — can look
  current when it is not. Do not build geometry that way.

## Printed solids

A **topmost rigid node** is one printed solid: a rigid node whose parent is
non-rigid, or the root when the root is itself rigid. This is the unit the
whole-model assertions work in.

The traversal stops at a solid and does not descend into it. Leaves inside a
`FusionNode` are ingredients of that solid, not parts — they are never
compared against each other and are not individually required to be connected;
only the solid they fuse into is.

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

Tests for `foo.py` live in `test_foo.py` beside it; a package rooted at
`__init__.py` uses `test.py`. Subclass `solid_node.test.TestCase`.
The runner exposes the built node as `self.node` and as the snake-case name of
the test class (`SpurGearTest` gives `self.spur_gear`). When the node file
defines more than one node class, each test class must additionally declare
`node = TheClass` to say which one it exercises, or the run fails naming the
candidates.

```python
assertNoDisconnectedSolids(node)
assertNoSolidInterference(node)
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
assertJoined(node1, node2, min_weld_volume=0.0)
```

`assertNoDisconnectedSolids(node)` requires every printed solid below `node`
to be exactly one connected body. Each solid is read from its own STL with no
operations composed: connectivity is invariant under placement, so no world
matrix is involved and no animated `$t` can reach it. Watertightness does not
imply connectedness — a mesh of several disjoint closed shells is watertight,
has positive volume, exports a valid STL, and renders in the viewer looking
like a part.

`assertNoSolidInterference(node)` requires the printed solids below `node` to
share no volume, placed in world coordinates at the testing instant the runner
has selected. It has no overlap epsilon and will not gain one: exact
zero-volume boundary contact passes, and any positive shared volume fails.
Manufacturing clearance is a length-based contract of your project, not a
tolerated volume of interpenetration. The assertion passes vacuously when it
selects zero or one solid, so it proves nothing about a project that is still
a single leaf or fusion.

`assertJoined(node1, node2, min_weld_volume=0.0)` requires two features to
fuse into a single body — the one case where sharing volume is required rather
than forbidden — and `min_weld_volume` (mm³) additionally requires that shared
volume to be substantial rather than a numerical lick of contact. Both nodes
must belong to the **same** solid; the comparison runs in that solid's frame.
A pair drawn from two different solids fails as such, naming both, rather than
being answered in the wrong frame.

Deprecated: `assertNoPairwiseIntersections(root, volume_epsilon=0.0)`. Do not
write it. It walks leaf pairs quadratically and checks leaves rather than
printed solids, which is the wrong unit. It survives only so existing projects
keep running, and it warns when called; `assertNoSolidInterference` replaces
it. `assertOneBody`, `assertBodyCount`, and `assertNoDisconnectedParts` were
removed outright — `assertNoDisconnectedSolids` covers what they did.

`assertClose` bounds every vertex of the second node within a maximum distance
of the first; `assertFar` requires every vertex to remain at least the minimum
distance away. The perturbation assertions rotate locally by default; pass
`along=(x, y, z)` for linear displacement, `directions='forward'` for an
intentional one-sided constraint, and a sequence of amounts to
`assertFreeWithin` for a sweep. Directions are local and follow placement.

`volume_epsilon` on the perturbation assertions treats an intersection below
the given volume as no intersection. It exists for float noise between parts
that abut exactly flush. Treat it as a smell rather than a tool: reach for it
only to understand a test you inherited, and prefer to remove it by giving the
geometry a real clearance, so the contract holds without a threshold. Default
`0.0` keeps exact emptiness semantics.

Use `@testing_instant(t)` to pin time and `@testing_steps(n, start=0, end=1)`
to sweep it. A node created inside a test needs `.assemble()` and
`.build_stls()` before `.mesh` is available. Intersection assertions use a
fast cached path for watertight built STLs. `mesh.contains` requires `rtree`;
`trimesh.proximity` requires `scipy`.

The test runner builds at keyframe 0 before tests, runs node mixin and test-case
methods alphabetically with `setUp`/`tearDown`, sets each requested keyframe,
and restores operation state between instants. Any failure exits nonzero;
`--failfast` stops at the first.

`solid new` scaffolds both whole-model contracts into the project's root test
file, because the framework enforces neither of them itself:

```python
class MyProjectTest(TestCase):

    def test_solid_integrity(self):
        self.assertNoDisconnectedSolids(self.node)

    def test_assembly_integrity(self):
        self.assertNoSolidInterference(self.node)
```

They run because the project wrote them down. Nothing else in the framework
will notice a part that has fallen into fragments or two parts occupying the
same material.

Both are ordinary test methods, so the animation decorators apply. A project
whose model moves is expected to decorate `test_assembly_integrity` with
`@testing_steps(...)`: interference is a question about where the solids are,
and the scaffolded form only answers it for the instant the runner has
selected. Connectivity does not vary with pose, so `test_solid_integrity`
needs no sweep.

## CLI

```text
solid new <name>
solid build <path>
solid test <path> [--failfast]
solid snapshot <path> -o out.png [--time 0..1] [--autocenter] [--viewall]
      [--camera tx,ty,tz,rx,ry,rz,dist | ex,ey,ez,cx,cy,cz]
      [--imgsize 1920x1080] [--projection ortho|perspective]
      [--colorscheme Cornfield|Metallic|...] [--render | --preview]
      [--view axes,crosshairs,edges,scales,wireframe]
solid export <path> [-o export] [--fps 30] [--frames 360] [--no-widget]
```

`solid snapshot` also takes `--renderer openscad|web`. Leave it at the default
`openscad`: it is fast and needs no browser. The `web` renderer exists so a
host can obtain a transparent background through headless Chromium; it is an
optional install and rejects `--projection`, `--colorscheme`, `--view`,
`--preview`, and `--render`. It is not for inspecting your own work.

`solid develop` serves a live viewer that rebuilds on save. The shop already
watches the project and keeps the maker's view current, so you never run it.

`solid new <name>` scaffolds `<name>/<name>/<name>.py` with a starter node,
`<name>/<name>/test_<name>.py` with the two default contracts, an empty
`__init__.py`, a `.gitignore` covering `_build*`, `__pycache__/` and
`snapshot.png`, and a `pyproject.toml` whose `[tool.solid-node] model`
declares the root node.

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

- `viewer.json` — `{format, version, animation: {fps, frames}, root}`, where the
  node tree carries the same `name`, `type`, `color`, `mtime`,
  `operations`, and either `children` or a rigid node's `model` path
  relative to the build directory.
- the rendered STLs, at the `model` paths `viewer.json` names.
- `errors.json` — `{error, tstamp}`, written into the build path instead
  of a publication when a build fails, so the previous model keeps
  serving.

`solid viewer` prints JSON naming the installed `solid-widget.js` bundle and
its integer `apiVersion`. A consumer must reject a missing or too-old bundle
before opening. The first build after a framework upgrade may add the additive
`format` field and therefore produce one ordinary model-change refresh.

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
