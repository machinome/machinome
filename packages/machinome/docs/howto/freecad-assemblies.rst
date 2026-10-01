# Native FreeCAD assemblies

`FreeCADAssemblyNode` loads the complete supported native machine at instance
construction. `FreeCADJoint` selects an existing revolute by its internal
FreeCAD `Name`; an editable display `Label` is not a selector.

```python
from machinome_freecad import FreeCADAssemblyNode, FreeCADJoint
from machinome.motion.ports import Time
from machinome.simulation import Driver, Sim

class DumE(FreeCADAssemblyNode):
    freecad_source = "cad/MA_Dum_E_v2_Assembly.FCStd"
    time = Time.running()
    turntable = FreeCADJoint("Joint001")
    turn = Driver(default=0, unit="deg")
    turn.drives(turntable)

node = DumE()
sim = Sim(node, dt=0.02)
command = sim.move("turn", to=150, duration=1.0)
sim.run(1.0)
print(command.status, node.turntable.value)
```

This follows the independently validated corrected-source project declaration.
The untouched upstream Dum-E assembly is
refused because its Fixed `Joint002` has inconsistent connector orientation;
the source in this example must be the project's explicitly corrected native
copy, not the untouched upstream file. Place it in a normal machinome project with
a `pyproject.toml` containing `[tool.machinome]` and its `model` entry.
Install the package and configure the [recorded native runtime](runtime.md).
Public module imports and class declaration need no FreeCAD runtime. Creating
an instance does: source selection is validated before relations resolve and
before `Sim` enumerates or compiles the graph.

`freecad_source` accepts a string or path-like object. Relative paths resolve
from the Python module that declared the attribute, even under inheritance
and after changing cwd. The root source must belong to that module's machinome
project, following the existing framework source-file rule. Native external
links are resolved by FreeCAD; retain their relative layout when relocating
the project. Linked products may be in a sibling directory, not only next to
the assembly file.

The instance alias returns the original `BoundPort`, so `node.turntable.value`
reads the physical coordinate in degrees. It contributes no proxy coordinate
or second simulation-bank entry. Two aliases of one native Name read the same
slot; ordinary duplicate-writer rules reject two drivers commanding it.
Two model instances own separate slots and imported node trees.

The example commands native coordinate zero as its initial state. It does not
make the saved assembly pose a new zero. Uncommanded revolutes retain their
saved native coordinates; repeated rendering and fresh simulation enumeration
preserve those defaults while leaving commanded or run-owned values alone.
The `Angle` property of a generic FreeCAD joint is not read as a revolute's
coordinate. The adapter resolves connector frames and offsets through native
helpers and reads the native angular coordinate, converting radians to degrees.

Only enabled native limit sides constrain the imported joint. Disabled stored
zero values are unbounded, including one-sided ranges. Driver `range=` is
presentation metadata, not a replacement mechanical bound. An invalid initial
request is refused by ordinary joint validation before a running program is
compiled. An outward move reaches an enabled physical stop and sets
`command.status` to `"blocked"`; an admitted target becomes `"completed"`.
Use `sim.state` for the qualified physical coordinate and driver values, and
`sim.stops` for ordinary running stop observations.

## Selectors and refusals

Find the native internal Name in FreeCAD's property editor. A missing selector
or selection of a fixed connection raises an error with the source path,
selector, its type when present and the available moving Names. An unused alias
is validated too. `FreeCADJoint("Joint001", axis=..., range=...)` is invalid:
the source owns those mechanical facts. A reference declared on another,
unrelated model cannot be used as a local relation target.

The supported graph contains exactly one native `Assembly::AssemblyObject`,
one grounded occurrence, rigid occurrences and unsuppressed Fixed/Revolute
connections forming one connected acyclic tree. Every occurrence and fixed
connection is preserved; fixed solids are separate rather than fused. Joint
endpoint order does not determine the carrying tree: connectivity rooted at the
ground does. Unknown connection objects, unsupported joint types, suppression,
loops, disconnected objects, multiple groundings, unresolved native references,
non-solid shapes and non-rigid scale are explicit refusals.

Native recomputation and `assembly.solve()` must succeed. After recomputing
authored references and offsets, and again after solving, every joint's native
marker residuals must be finite and within 0.01 mm and 0.001 degree. Both
joint types require coincident connector origins. Fixed connections require
native direction-cosines `(Iy·Jx, Iz·Jx, Iz·Jy)` to be zero: this admits identity
and the three proper π-rotation branches, not an arbitrary relative connector
orientation. Revolutes require `(Iz·Jx, Iz·Jy)` to be zero, accepting parallel
or antiparallel Z axes with free twist. Angular distance to the applicable
branch/axis and the raw direction-cosines are checked; the latter's dimensionless
tolerance is `sin(0.001°)`. These are the pinned native solver conventions,
not replacement project-authored mechanics.

Solving must retain
the saved placements within 0.01 mm and 0.001 degree. Source drift beyond those
tolerances is refused instead of quietly replacing the saved assembly. This
first version has no generalized diagnostic CLI or second inventory API.

Solver status 0 alone is insufficient. Inconsistent sources are refused with
source, assembly, joint and endpoint Names, measured residuals and tolerances.
The adapter does not repair a constraint, change a source or invent a fixed
transform. Untouched Dum-E is negative evidence. The separate project author
established native moving-pose parity for all nine occurrences in eight cases
against the project-owned correction, with maximum errors below 0.01 mm and
0.001 degree, and the unchanged-wrapper 180°/120° command experiment passed.
These corrected-source results do not retroactively certify upstream. See
[the review](../workflow/archive/native-freecad-assembly/native-freecad-adversarial-review.md).

## Refresh and geometry

After changing native mechanics or a consumed linked file, construct a fresh
model and a fresh `Sim`. Do not reinterpret an active simulation in place.
Every fresh construction performs native discovery, brackets a second native
load with the complete observed closure, recomputes, checks the solver, and
rejects interrupted generations. Content digests and strong metadata detect
semantic edits and same-size replacements with restored mtime. Immutable
snapshots are reused only after that native handshake, without sharing mutable
nodes or coordinates. The acceptance recipe is versioned; older provisional
snapshots cannot satisfy residual admission or be a fallback after refusal.
That recipe also participates in exact artifact currency. There is currently a cost of two native processes per
fresh model; this is a correctness-first compatibility boundary, not live sync.

Exact geometry is transferred as own-frame BREP into the framework OCCT kernel.
The worker owns native geometry and joint interpretation; ordinary exact leaf
materialization writes BREP/STL artifacts, and ordinary operations express the
carrying poses. Source geometry and native/importer recipe participate in
artifact currency. An older model whose consumed source identity changes is
refused when its geometry or currency is consumed; rebuild it.

For a source change during exact materialization, the adapter restores that
leaf's prior BREP/STL and currency sidecars (or removes outputs just created by
that failed attempt). Output files may exist transiently while that attempt
runs; this is not a transaction across other processes or an entire build.

The ordinary framework build/export/snapshot surfaces remain the consumers.
No viewer engine, custom motion format or additional export field is required.
For numerical comparison, all required surfaces are public: `render()` gives
the carrying children, each node has `name` and `operations`, each operation
has `matrix()`, and exact leaves have `shape()`.

```python
import numpy as np

def occurrence_poses(node, parent=None, path=()):
    parent = np.eye(4) if parent is None else parent
    rendered = node.render()
    local = np.eye(4)
    for operation in node.operations:
        local = operation.matrix() @ local
    world = parent @ local
    yield path + (node.name,), world
    if isinstance(rendered, (list, tuple)):
        for child in rendered:
            yield from occurrence_poses(child, world, path + (node.name,))

# Bind operating defaults through Sim first, then inspect poses.
sim = Sim(node, dt=0.02)
poses = dict(occurrence_poses(node))
```

Names preserve the native occurrence Names through reparenting. A `solid`
child is an exact leaf in its carrier's own frame; nested carrier transforms
compose parent-first. Compare these matrices with an independent native solver
reference. Do not recover physical zero or limits from rendered shape alone.
