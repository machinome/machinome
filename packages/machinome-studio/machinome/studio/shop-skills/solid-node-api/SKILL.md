---
name: solid-node-api
description: Complete public API reference for solid-node 0.6. Use when designing a mechanical project against solid-node capabilities, specifying nodes, parameters, drivers, ports and kinematics without inspecting framework implementation, or implementing nodes, tests, scenarios, snapshots, and exports through supported public interfaces.
---

# solid-node public API

Use this as the authoritative public contract. It is the whole of what a
project may rely on: framework source is not available to you, so a behavior
this document does not describe is a gap to report, not a thing to discover.
Never guess an interface from a symbol name.

This describes solid-node 0.6 plus the declarative node API that followed
it on the framework's main branch.

## Imports

Each module answers one question, and an import line says which:

```python
from solid_node.node import (                  # what the machine is made of
    AssemblyNode, FusionNode,
    CadQueryNode, Build123dNode, Solid2Node, OpenScadNode, JScadNode,
    Build123dSheetNode, StlNode, MolejoNode,
    Port, RotationalPort, TranslationalPort, SignalPort,
    declared_children, declared_ports, property_as_number,
)
from solid_node.parameters import (            # what is built
    Length, Angle, Count, Ratio, Scalar, Flag, Quantity,
    declared_parameters, DimensionError, ParameterError)
from solid_node.simulation import (            # how it runs
    Driver, Instruction, Sim, ScenarioTest, RampProgram,
    qualified_drivers, qualified_instructions)
from solid_node.test import (
    TestCase, TestCaseMixin, testing_instant, testing_steps)
from solid_node.math import (
    sin, cos, tan, asin, acos, atan, atan2, sqrt)   # DEGREES
```

The parameter kinds are exported by `solid_node.parameters` and by nothing
else: `solid_node.node` does not provide `Length`, and importing it from
there fails.
`SheetLeafNode` and `FlexibleNode` are also exported from `solid_node.node`
as the abstract bases of the sheet and flexible kinds; a project subclasses
their concrete adapters.

## Node kinds

Leaves make one part each; internal nodes combine parts.

| class | extension point | returns | exact | needs |
| --- | --- | --- | --- | --- |
| `Solid2Node` | `render()` | a solid2 object | no | OpenSCAD |
| `OpenScadNode` | `scad_source` (+ `module_name`) | — | no | OpenSCAD |
| `JScadNode` | `jscad_source` | — | no | the `jscad` CLI |
| `CadQueryNode` | `render()` | a cadquery `Workplane` | yes | nothing |
| `Build123dNode` | `render()` | a build123d `Part`/`Solid`/`Compound`, or a `BuildPart` builder | yes | nothing |
| `Build123dSheetNode` | `profile()` + `thickness` | one planar build123d face (`Sketch`, `Face`, or `BuildSketch`) | yes | nothing |
| `StlNode` | `stl_source` (+ `body`, `adjust()`, `require_watertight`) | — | no | nothing |
| `MolejoNode` | `render()` + one port per shape parameter | a molejo `Shape` | yes | nothing |
| `AssemblyNode` | `render()`, `simulate()` | child nodes | if all children are | — |
| `FusionNode` | `render()` | child nodes, fused into one rigid solid | if all children are | OpenSCAD when any child is faceted |

- `Solid2Node.as_number()` resolves a solid2 expression by running OpenSCAD
  once per call; keep ordinary dimensions in Python.
  `property_as_number` turns a solid2-expression-valued method into a
  numerically resolved property.
- `OpenScadNode`: `scad_source` is relative to the node's Python file; the
  module named after the file, or `module_name`, receives the constructor's
  `*args/**kwargs`.
- `Build123dNode` accepts builder or algebra mode and takes `.part` off a
  returned builder. A sketch or curve is refused naming the node.
- `Build123dSheetNode`: `thickness` is required and positive, as a class
  attribute or a `thickness=` constructor argument. `render()` is not an
  extension point: the solid is the profile extruded from XY along +Z. The
  profile must be exactly one planar face on XY with holes strictly inside;
  anything else fails naming the node. Each build writes a nominal,
  kerf-free `.dxf` (arcs kept as arcs) beside the `.stl` and `.brep`;
  `dxf_file` is its path. No kerf compensation, SVG/DXF import, engraving
  or nesting.
- `StlNode`: `stl_source` is a committed `.stl` beside the module. The
  artifact is materialized from it; nothing is repaired. A non-watertight
  body fails the build naming the defect unless `require_watertight =
  False` admits it knowingly (admission only, never geometry). A multi-body
  file is a pack: declare `body = <0-based index>` (components ordered by
  centroid x, y, z); omitting it fails with a per-body inventory of
  centroid, bounds and volume. `adjust(self, mesh)` receives the selected
  body as a trimesh mesh and returns the corrected one; what it returns is
  the artifact. The declaring module is tracked as a source. An `StlNode`
  makes any fusion holding it faceted and slow. It is never exact.
- `MolejoNode`: `render()` returns a molejo shape whose moving dimensions
  are molejo parameters (`P.height`); the node declares one port per
  parameter under the same name, and both name sets must match exactly or
  assembly fails naming the node and both sets. Per-instant values arrive
  only through ports; constructor arguments are structural and key the
  artifact. An unbound port fails naming the node and port. Molejo paths
  start at the node's origin: a helix winds about an axis offset by its
  radius. `shape_tolerance` reports the approximation of the current
  solid (`0.0` when analytic). A flexible leaf is non-rigid, never a
  printed piece, never fusable, and has no `time`. In the browser it
  travels as its shape spec (document version 3); OpenSCAD gets a snapshot
  STL at the bound state.
- `AssemblyNode` children are separate parts that move relative to each
  other; `self.time`, drivers and ports are read in `simulate()`.
- `FusionNode` children fuse into one rigid printed part and one STL.
  Every child must be rigid: a fusion refuses an assembly and a flexible
  leaf, naming both nodes, at validation. It has no `self.time`; a fusion
  is animated by the assembly holding it. Children may be created in
  `render()`, since they do not need identity across renders. Exact
  children (any mix of OCCT backends) fuse exactly in process; one faceted
  child routes the fusion through OpenSCAD/CGAL.

## Declaring a node

The class body declares what a part is; the framework derives identity,
propagation and the command-line surface. This is the preferred form.

```python
from solid_node.node import CadQueryNode
from solid_node.parameters import Length

class Piston(CadQueryNode):

    diameter     = Length(29.4, min=0)
    crown_height = Length(18.0, min=0)
    skirt_depth  = Length(12.0, min=0)

    total_height = crown_height + skirt_depth      # derived

    def render(self):
        return (cq.Workplane("XY")
                .circle(self.diameter / 2)
                .extrude(self.total_height))
```

Every value a node uses is one of three things:

| layer | says | lives |
| --- | --- | --- |
| parameter | what is built | a `Length(...)`-style declaration; propagates to children; enters build identity; settable by a parent or `--set` |
| constant | where it sits | bare Python in a module or class body; read in `render()`; invisible to the framework |
| port | how it runs | a port declaration; bound at runtime; never build identity |

Wrapped is a parameter, bare is a constant. Placement arithmetic, lookup
tables and naming logic are constants and ordinary code.

### Kinds

`Length` (mm, signed unless `min=0`), `Angle` (degrees), `Count` (an
`int`; refuses `2.5`), `Ratio` (dimensionless), `Flag` (a boolean, outside
the algebra), `Scalar` (an unchecked number). Numeric kinds take an
optional default plus `min=` and `max=`; constraints are checked at
construction and a violation raises naming the class, parameter and rule.
Values are coerced, so `diameter=30` and `diameter=30.0` are one part.

A declaration may omit its default (`height = Length(min=0)`): the parent
must supply it, and constructing without it raises naming the class and
parameter. Loading such a node directly needs `--set height=300`.

On an instance a declared parameter reads as a plain `float`, `int` or
`bool`; on the class it is the symbolic token. Assigning to one on an
instance raises. A declaration may not shadow an attribute a base carries
(`name`, `time`, `mesh`, `children`, `color`, a sheet's `thickness`, ...):
class definition raises. `declared_parameters(cls)` enumerates them.

### Formulas and the algebra

A bare class-body expression over tokens is a **derived parameter**: read
on the instance it is the evaluated value, and it cannot be supplied by a
parent, by `--set`, or by assignment. Every quantity carries dimension
exponents: products add, quotients subtract, sums and differences need
equality, and a mismatch raises `DimensionError` on `import`.
`teeth * module` is a length, `bore / stroke` dimensionless, `bore +
pressure_angle` an error. `solid_node.math` takes part: `sqrt` halves even
exponents, `sin`/`cos`/`tan` need an `Angle` and return dimensionless,
`asin`/`acos`/`atan`/`atan2` return an `Angle`. Comparisons are refused in a
declaration; they belong in `render()` or `check()`. `Count` and `Ratio`
are both dimensionless, so the algebra does not separate them. A project
needing another kind subclasses `Quantity` with its own `dimension`
exponents; `.value` on a token or formula yields the unchecked form.

### Declaring children

A node constructed in a node class body is a **declaration**, never an
instance: each parent instance realizes its own child at construction.
Tokens are passed by reference and resolved top-down from the root, so
`Engine(bore=32.0)` moves every derived value and child that reads
`bore`. A `Flag` flows the same way. Siblings never reach into each
other: `ConRod(pin_bore=piston.pin_bore)` in a class body raises, advising
that the shared parameter be declared on the parent. A child whose class
has an ordinary `__init__` is realized by calling it with the resolved
arguments, so the two styles mix in one tree. `name=` passes through and
wins. `declared_children(cls)` enumerates them.

```python
class Engine(AssemblyNode):

    count = Count(8, min=2)
    bore  = Length(30.0, min=0)

    cylinders = Cylinders(count=count, bore=bore)
    block     = BlockAssembly(count=count, bore=bore)
```

Lists and repetition:

- A literal list declares enumerated, different children named
  `<attr>-0`, `<attr>-1`, ...
- `Unit(bore=bore).repeat(count)` declares `count` identical children
  (an integer or a `Count` token): one geometry, one artifact, `count`
  placements. Per-unit variation never lives in the declaration;
  placement variation is `enumerate` plus constants in `render()`, drive
  variation is port feeding in `simulate()`.
- A list comprehension in a class body cannot see class-level names
  (Python scoping; `NameError`). One over module-level names or literals
  declares an enumerated list like a literal one.
- Indices are identity and never renumber; an omitted `units-3` leaves
  `units-4` as `units-4`.
- A driver declared on a list-held child cannot be qualified (`units-3`
  is not an identifier); drive identical units through ports instead.

A declarative class rejects positional arguments and unknown keywords
with a `TypeError` listing the declared names. A class carrying its own
metaclass derives it from `solid_node.node.declarative.NodeMeta`.

### render() that returns nothing

On a class with declared children, an internal node's `render()` may
return `None`: the children are then the declared ones in declaration
order minus any it omitted, and `render()` only places and selects. A pure
grouping node needs no `render()` at all. A `render()` that returns a list
keeps that contract to the letter and the framework builds exactly that
list. Both forms work on assemblies and fusions. A leaf `render()`
returning `None` is still an error.

### omit()

`child.omit()` in `render()` removes a declared child from the machine
for that realization: not linked, built, exported, fused or serialized.
Every child is always declared; `render()` selects presence from declared
parameters only. Structure varies with parameters, never with time:
`omit()` in `simulate()` raises `StructureError` (defined in
`solid_node.node.declarative`), and on the legacy
re-running render path an omitted set that differs from the first run
raises naming the node and both sets.

### check()

The framework calls `check()` on a declarative node once its parameters
are resolved and before any child is realized; whatever it raises
propagates unchanged (`ValueError` is the convention) and a refused root
realizes nothing. The base does nothing, so `super().check()` chains.
A class that declares nothing is not called.

### --set

Every command that loads a node accepts `--set NAME=VALUE`, repeatable,
on the root's declared parameters: a float for `Length`, `Angle`, `Ratio`
and `Scalar`, an integer for `Count`, `true`/`false` for `Flag`, checked by
the declared constraints. An unknown name fails listing the settable
parameters; a derived parameter cannot be set; a root that declares
nothing refuses the flag. A develop session reapplies overrides on every
rebuild. Artifacts of different parameter sets coexist in the build
directory.

## The constructor form

A class that declares nothing keeps the older form and keeps working:

```python
class Shaft(CadQueryNode):
    def __init__(self, diameter=4.8, length=30.0, name=None):
        self.diameter = diameter
        self.length = length
        super().__init__(diameter=diameter, length=length, name=name)
```

All nodes accept `__init__(self, *args, name=None, **kwargs)`. The
artifact key is hashed over the positional args and sorted kwargs that
reach `super().__init__()`, so a parameter kept on `self` but not
forwarded silently shares a stale artifact between variants. Assembly
children in this form are created in `__init__` as instance attributes
(never in `render()`, since identity must persist). Any node constructed
in a class body is a declaration, on either form.

Migrating a class that forwarded every keyword with float defaults keeps
its build identity; one that forgot a keyword, or passed an integer where
a float kind now resolves, re-keys once.

## Identity and names

Two independent things:

- **Build identity** (`uniq_id`, the artifact key): the class plus its
  parameters, derived by the framework for a declarative class from the
  resolved declared values. Identical instances, and repeated units, share
  one artifact. Driver and port values are never part of it.
- **Tree name**: `name=` when given, else the parent attribute holding the
  child (`self.input_gear` becomes `input_gear`; list members
  `<attr>-<index>`; `_`-prefixed attributes ignored; class name as the
  fallback). Names address the viewer tree, tests and driver ids and never
  touch the artifact key.

## Lifecycle: render() at rest, simulate() per instant

`assemble()` is the framework's template method and is never overridden;
its result is memoized per instance. On an assembly the framework runs
`render()` then `simulate()` on every enumeration of its children.

`render()` builds the machine **at rest**: declares presence with
`omit()` and places every part that does not move. It reads no driver, no
`self.time` and no port, and a `render()` that reads none runs **once per
instance**: the children it returns and the operations it applies are
kept for good.

`simulate()` **moves** it: run after `render()` on every instant, under
symbolic `$t` in the build and viewer and under plain numbers in tests,
snapshots and a stepped simulation. It is the one place drivers, time and
ports are read and bound. Each operation it applies is motion: stated
absolutely for its instant, dropped before the next run, and composed
**inside** the part's rest placement, so a part rotated in `simulate()`
and translated in `render()` spins about its own axis and is then
carried to its seat. Two assemblies simulating one node keep their
operations apart. The base `simulate()` does nothing; `super().simulate()`
chains; a part that does not move needs none.

```python
class Block(AssemblyNode):

    caps  = MainBearingCap().repeat(5)
    crank = Crankshaft()

    angle = Driver(default=0.0, range=(0.0, 720.0), unit='deg')

    def render(self):
        for cap, x in zip(self.caps, BEARING_CENTERS):
            cap.translate([x, 0, 0])
        self.crank.translate([0, 0, CRANK_HEIGHT])

    def simulate(self):
        self.crank.rotate(self.angle, [1, 0, 0])
```

The rule is enforced by what a method reads, not by its name. A
`render()` that reads a driver, `self.time` or a port, or binds a port,
keeps working as the legacy form (it re-runs per instant and its
operations are swept) and the build prints one `FutureWarning` per class
per process naming the read and `simulate()`. The decision is made on the
instance's first `render()`. Placement applied in `__init__` still works
and composes after motion; it is no longer recommended.

## Drivers, time, ports, instructions

**Drivers** are the machine's named inputs, declared on an assembly:

```python
from solid_node.simulation import Driver

class Axis(AssemblyNode):
    position = Driver(default=20.0, range=(0.0, TRAVEL), unit='mm')

    def simulate(self):
        self.carriage.translate([self.position - TRAVEL / 2, 0, 11])
```

`Driver(default, range=None, unit=None, dtype=None, scale=None)`. The
value is read as an attribute in `simulate()` and used in expressions
exactly like `self.time`: symbolic in the build and viewer, numeric under
a bound snapshot. Assigning to a driver raises naming `set_state`;
reading one no snapshot bound raises naming the driver; a declaration
shadowing a node member fails at class definition. `range` is
presentation metadata in design units and never clamps. `dtype=int` marks
a discrete device and `scale` declares design units per native unit (the
value is native, `range` and instruction targets are design units). The
build, test, snapshot and export paths bind every declared default before
the first render, so a driven project needs no self-binding.

A driver's public identity is its **instance-qualified id**, the dotted
attribute path to the declaring node plus the local name:
`x_axis.position`, or the bare name for a root-declared driver. It is the
same string in the published document, `set_state`, instruction targets
and a simulation's state. A tree that cannot be qualified (a
driver-declaring node held in a list) fails loudly.

**State binding** on an assembly:

- `set_state(**states)` merges numeric entries into the current snapshot
  and propagates down the tree. A dotted id is passed as a mapping
  (`set_state(**{'x_axis.position': 40.0})`) and reaches only that
  subtree; a bare name is valid while exactly one driver in the tree
  bears it and fails naming both ids when two do; a name no declaration
  backs is rejected listing what is declared. `time` is global and needs
  no declaration.
- `clear_state(*names)` removes entries (all with no names) and
  re-simulates symbolically.
- `set_keyframe(t)` is `set_state(time=t)`; `clear_keyframe()` is
  `clear_state('time')`. Both recurse and are no-ops on leaves and
  fusions. Nothing accumulates across cycles; rest placement is untouched.
- `self.time` is `$t` from 0 through 1 in the build and viewer, the
  bound number under a keyframe, and the simulation clock in seconds
  under `Sim`. Assemblies only: leaves and fusions raise on `time`.

**Ports** are connection points between parts, declared as class
attributes on any node: `RotationalPort(unit=None, out=False,
scale=None)`, `TranslationalPort(...)`, `SignalPort(...)`, sharing the
`Port` base. Reading a port off an instance yields the bound port;
`.value` is what was bound, or `None` when nothing has (a wiring mistake to
notice, never a zero). A parent binds ports in `simulate()`, either
`self.connect(source, sink)` or by assignment (`unit.crank = self.crank +
phase`); both apply the sink's `scale` and the source may be a port, a
number or a symbolic expression. The framework runs a parent's
`simulate()` before its children's, so a child reads in its own
`simulate()` what its parent bound. Bindings are re-evaluated absolutely
every `simulate()` and never enter build identity. Ports are kinematic
only (no torque or force). `declared_ports(cls)` enumerates them.

**Instructions** are declared moves, in an `instructions` dict on the
assembly that owns the move, with targets in design units:

```python
instructions = {
    'Home': Instruction({'x_axis.position': 0.0, 'y_axis.position': 0.0},
                        duration=2.0),
}
```

Each becomes a viewer button and a `trigger()` in simulations; triggering
ramps every target from its current value and lands exactly on it, and a
new trigger replaces a running ramp. The viewer shows one slider per
driver and one button per instruction declared at the focused assembly
layer, with a breadcrumb into subassemblies; a root that declares nothing
shows no controls.

## Instance surface

- `.rotate(angle, axis)` and `.translate([x, y, z])` append an operation,
  return the node, and chain. Operations apply in order; a node's own
  apply before its ancestors'. `.operations` is the ordered list.
- `.mesh` is a fresh trimesh copy in world coordinates, every ancestor
  operation composed at access time.
- `.stl_file` is the built artifact path (rigid nodes only).
- `.exact` reports whether exact geometry is available (fixed by adapter
  type; an internal node is exact when every child is, and raises before
  its children are linked). `.shape()` returns an exact node's OCCT solid
  in its local frame.
- `.name`, `.children`, `.time` (assemblies only), `.rigid` (by type:
  leaves and fusions true, assemblies and flexible leaves false; not
  settable).
- `.assemble()` then `.build_stls()` prepares an independently created
  node for mesh use. `.set_keyframe(t)`, `.clear_keyframe()`,
  `.set_state(...)`, `.clear_state(...)` as above.
- `.save_checkpoint()` and `.restore_checkpoint()` mark and roll back the
  operations list.
- `.connect(source, sink)` on internal nodes; `.omit()` and `.check()` as
  above; `.shape_tolerance` on a flexible leaf; `.dxf_file` on a sheet.

Class attributes: `color = '#RRGGBB'` (anything else raises); `fn = N`
sets OpenSCAD's `$fn` and affects only `Solid2Node` and `OpenScadNode`;
`optimize` defaults true and false keeps unflattened SCAD for the
OpenSCAD viewer.

There is no `bodies` declaration. Connectivity is not a build check: the
build never opens an STL to count components. It is a project test
contract (see the test surface).

## Files, references and rebuilds

A project is a package with a `pyproject.toml` whose `[tool.solid-node]
model = "package.module:Class"` names the root. The project root is the
nearest ancestor manifest, discovered from a referenced path or the
working directory, so every command behaves identically from any
directory. A node **reference** is `package.module:Class`, `path/to/file.py`
or `path/to/file.py:Class`; a directory is not a reference. A bare path
resolves only when the file defines exactly one node class; otherwise it
raises `AmbiguousNodeError` listing the candidates, and `solid build`,
`solid snapshot` and `solid develop` need the class named. `solid test`
on a bare path to such a file runs every node it defines.

An artifact rebuilds when its stamp no longer equals the node's source
mtime, compared as exact integer nanoseconds. The **source set** is the
node's own file plus the transitive closure of project-local modules it
imports, resolved statically; the framework and anything outside the
project tree are not tracked. Internal nodes union their children's sets,
so a leaf's edit invalidates the assemblies above it and nothing sideways.
When stamps disagree but a digest of the tracked sources matches what
produced the artifact (a clone, branch switch or stash pop), the artifact
is restamped rather than rebuilt.

Consequences:

- Editing a module that defines no node correctly invalidates exactly the
  nodes that import it.
- The walk never follows a package's `__init__.py`. A value reached
  through the package rather than the module that defines it is **not
  tracked**; its edit serves a stale model.
- A current leaf is not rendered at all: `assemble()` may call `render()`
  zero times. Nothing may depend on a render side effect, and geometry
  that depends on something the import walk cannot see (a data file read
  at runtime, `importlib`, an environment variable) can look current when
  it is not. `StlNode` tracks its own `.stl` and declaring module.
- The digest is scoped to the node. Two node classes in one file share
  one stamp, but each node's digest covers the file minus the other node
  classes' bodies (any the remaining text names stay in), so editing one
  class rebuilds that node and the fusions above it and only restamps the
  other. Editing module-level code they share rebuilds both.

## Printed solids

A **topmost rigid node** is one printed solid: a rigid node whose parent
is non-rigid, or a rigid root. Whole-model assertions work in this unit
and do not descend into it. Leaves inside a `FusionNode` are ingredients
of that solid, never compared against each other and not individually
required to be connected. A flexible leaf is never a printed solid.

Published documents carry a `pieces` inventory: one entry per distinct
built-artifact content with `id`, `name`, `sources`, `models`, `count`,
`size` (mm extents), `volume` (mm³) and `watertight`; every rigid tree
node carries its `piece` id. Identity is content-derived, so a repeated
part is one piece with a count, and handed variants are two.

## Test surface

Tests for `foo.py` live in `test_foo.py` beside it; a package rooted at
`__init__.py` uses `test.py`. Subclass `solid_node.test.TestCase`, or mix
`TestCaseMixin` into the node class. The runner exposes the built node as
`self.node` and as the snake-case name of the test class (`SpurGearTest`
gives `self.spur_gear`). Every `TestCase` in a companion file is loaded;
when the node file defines several node classes, each must declare
`node = TheClass` or the run fails naming the candidates.

The runner builds each node under test (load, `set_keyframe(0)`, render,
assemble, `build_stls`) holding the project build lock and releasing it
before the first test, then runs `test_`-prefixed methods once per
declared instant (default `[0]`), restoring operation checkpoints between
instants and tests. `@testing_instant(t)` pins time; `@testing_steps(n,
start=0, end=1)` sweeps it (`n >= 2`, the last instant exactly `end`).
It prints `Ran N tests in X seconds: P passed, F failed`, exits 1 on any
failure, and `--failfast` stops at the first. `--set` applies to the root
under test.

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
assertJoined(node1, node2, min_weld_volume=0.0)
assertNoDisconnectedSolids(node)
assertNoSolidInterference(node)
assertAssemblySupported(node, gravity=(0, 0, -1), max_drop=1.0,
                        ground=None, supports=None, stability_margin=0.0)
```

Intersection and containment questions are answered exactly when both
nodes are exact and on meshes otherwise; `assertInside`, `assertClose`
and `assertFar` always sample mesh vertices against a mesh surface.
Standard `unittest` assertions are available. `rtree`, `scipy` and
`manifold3d` are framework dependencies; an all-exact project runs its
assertions without the faceted kernel.

`assertNoDisconnectedSolids(node)` requires every printed solid below
`node` to be exactly one body: the exact geometry's solid count for an
exact solid, a split of the node's own STL otherwise, with no operations
composed, so the verdict is the same at every instant. Watertightness is
not connectedness.

`assertNoSolidInterference(node)` requires the printed solids below
`node` to share no positive volume in world coordinates at the runner's
current instant. Exact boundary contact passes; there is no epsilon and
will be none. It passes vacuously with zero or one selected solid.

`assertJoined(node1, node2, min_weld_volume=0.0)` requires two features of
the **same** printed solid to be one body (an exact fuse yielding one
solid, or one mesh component), with a shared volume of at least
`min_weld_volume` mm³. Tangential contact is not a join. A pair from two
different solids fails naming both rather than being answered in the
wrong frame.

`assertAssemblySupported(node, ...)` proves the assembly can exist under
gravity: every printed solid, displaced by `max_drop` mm along `gravity`,
lands with positive volume on a solid that leads to ground, and
push-only normal forces over the detected contacts (drop and lift) balance
every solid's weight and torque in frictionless static equilibrium.
With `ground=None` the solids nearest the far extent along gravity are
grounded on a virtual floor; `ground` (a node or nodes) anchors an
assembly hung or bolted elsewhere; `supports=[(supported, supporter), ...]`
declares press fits and glue the geometry cannot prove; `stability_margin`
(mm) shrinks contact patches to reject knife-edge balances. `max_drop`
must exceed the vertical clearance play and stay below the thinnest
supporting feature plus its gap. Friction, adhesion, lateral wall
reactions, single-solid toppling and dynamics are out of scope.

Perturbation assertions rotate about the node's own axis by default
(`axis`, `(0, 0, 1)` when omitted); `along=(x, y, z)` selects linear
displacement in mm instead, and giving both raises. Directions are local
and carried by placement rotations. `directions='forward'` checks only the
positive sense. `assertFreeWithin` accepts a list of amounts. The
perturbation is inserted before the node's first placement translation
and always removed afterwards. `volume_epsilon` counts an intersection
below the given volume as none; it applies only on the faceted path, is
ignored with a warning when every comparison routed exact, and is a smell
rather than a tool.

Deprecated: `assertNoPairwiseIntersections(root, volume_epsilon=0.0)`
walks leaf pairs quadratically and warns; `assertNoSolidInterference`
replaces it. `assertOneBody`, `assertBodyCount` and
`assertNoDisconnectedParts` do not exist.

`solid new` scaffolds both whole-model contracts into the root test file,
because the framework enforces neither itself:

```python
class MyProjectTest(TestCase):

    def test_solid_integrity(self):
        self.assertNoDisconnectedSolids(self.node)

    def test_assembly_integrity(self):
        self.assertNoSolidInterference(self.node)
```

A node created inside a test needs `.assemble()` and `.build_stls()`
before `.mesh` is available.

### Scenario tests

A driven machine is also testable in motion. `Sim(node, dt=...)` steps an
assembly with a fixed step whose instants are integer ticks (`sim.time`
is `tick * dt` seconds; a non-tick instant is rejected). `sim.at(t)
.trigger('Home')` or `.run(callable)` schedules an action (actions due at
the current tick fire before the first step); `sim.every(period, fn,
*args)` calls `fn` on a cadence; `sim.run(duration)` steps, binding a full
qualified snapshot plus `time` each tick and appending to
`sim.trajectory`. `sim.state` is the live bank by qualified id;
`sim.tick`, `sim.cadence_costs` and `sim.assertion_stats` report progress
and cost. A triggered `Instruction` ramps as a `RampProgram` and lands
exactly on target; integer drivers ramp integer-exactly.

```python
from solid_node.simulation import ScenarioTest

class AxisScenarioTest(ScenarioTest):
    node = Axis
    dt = 0.02
    meshes = True            # build STLs; only for geometric assertions

    def test_homing_stays_clear_of_the_stop(self):
        sim = self.simulation()               # fresh per scenario
        sim.at(0.0).trigger('Home')
        sim.every(0.1, self.assertNoSolidInterference, self.node)
        sim.run(3.0)
```

A `ScenarioTest` is a `TestCase`: as a companion test it runs under
`solid test`, and imported into a pytest module it runs under `pytest`,
unmodified. `dt` is part of the scenario's meaning.

## CLI

```text
solid new <name>
solid build   [ref] [--set NAME=VALUE ...]
solid test    [ref] [--set ...] [--failfast]
solid snapshot [ref] [--set ...] -o out.png [--time 0..1] [--autocenter]
      [--viewall] [--camera tx,ty,tz,rx,ry,rz,dist | ex,ey,ez,cx,cy,cz]
      [--imgsize 1920x1080] [--renderer openscad|web]
      [--projection ortho|perspective] [--colorscheme Cornfield|...]
      [--render | --preview] [--view axes,crosshairs,edges,scales,wireframe]
solid export  [ref] [--set ...] [-o export] [--fps 30] [--frames 360] [--no-widget]
solid develop [ref] [--set ...] [--web | --openscad | --web-dev | --no-web]
      [--callback URL] [--debug-builder]
solid viewer
```

`ref` is a node reference as above; omitted, the manifest's model is used.
The command comes first. The CLI loads `./.env` at startup with the real
environment taking precedence: `SOLID_NODE_PORT` (viewer, default 8000),
`SOLID_NODE_FRONTEND_PORT` (viewer dev server, 3000), `SOLID_BUILD_DIR`
(artifact directory, `_build`, resolved against the project root).

`solid build` renders once, publishes the complete current model, and
exits: 0 when the model built or was already current, 66
(`MODEL_NOT_FOUND`) when the reference resolves to nothing, another
nonzero status when the build failed. It is the finite form of what
`solid develop` does on every save.

`solid snapshot` poses the model through `--time` (`$t` only; drivers
render at their defaults). Leave the renderer at the default `openscad`:
it is fast, needs no browser, self-wraps with `xvfb-run` when headless,
and stays the default whatever is installed. The `web` renderer exists
so a host can get a transparent background through headless Chromium; it
needs the separately installed `solid-node-viewer` package with its
browser (`pip install "solid-node[web-snapshot]"` plus `playwright install
chromium`), rejects the OpenSCAD-only options by name, and never falls
back. It is not for inspecting your own work.

`solid develop` opens a live viewer that rebuilds on save: the browser
viewer when `solid-node-viewer` is installed (`pip install
"solid-node[viewer]"`), the OpenSCAD GUI otherwise; a requested viewer
that cannot open is refused, never swapped. `--no-web` runs the watch
loop alone, `--callback URL` POSTs after each complete build. The shop
already watches the project and keeps the maker's view current, so you
never run it.

`solid new <name>` scaffolds `<name>/<name>/<name>.py` with a starter
`Solid2Node`, `<name>/<name>/test_<name>.py` with the two default
contracts, an empty `__init__.py`, a `.gitignore` covering the build
path, and a `pyproject.toml` declaring the model. It refuses an existing
directory.

`solid export` writes `manifest.json`, deduplicated `models/`, and unless
`--no-widget` a self-contained viewer copied from the installed
`solid-node-viewer` package; without that package, export with
`--no-widget` or the command fails naming the `viewer` extra. Exports
carry drivers, instructions and animation and never freeze a pose.

## Build directory

`SOLID_BUILD_DIR` (default `_build`) is an ordinary directory under the
project root, written directly. Per node it holds `<script>-<uniq_id>.scad`
and `.stl`, plus `.brep` for an exact node and `.dxf` for a sheet part;
artifacts of different parameter sets coexist. Each artifact is written
whole or not at all (temporary file plus atomic replace), every artifact
a snapshot names is in place before the snapshot, and a successful
publication sweeps files the snapshot no longer references. Builds of
one project serialize on an advisory lock file beside the build directory
and are never held while watching or testing.

Inside a publication:

- `viewer.json` — `{format: "solid-node-export", version, animation:
  {fps, frames}, drivers, instructions, root, pieces}`. `version` is 2, or
  3 when the tree holds a flexible part. `drivers` and `instructions` are
  tables keyed by qualified id (empty for a driverless model). Each tree
  node carries `name`, `type`, `color`, `mtime`, `operations`, and either
  `children`, a rigid node's `model` path relative to the build directory
  with its `piece` id, or a flexible leaf's `flexible` spec. Operations
  serialize as `['r', angle, axis]` / `['t', vector]` with raw
  expressions; animated values keep symbolic `$t` and qualified driver
  ids.
- the rendered STLs at the `model` paths.
- `errors.json` — `{error, tstamp}`, written atomically on a failed build
  and removed after the next successful one. A failed build after a
  success may leave a **partially updated** model beside it; the snapshot
  still names files that are present and complete, but do not read it as
  the previous model.

`solid viewer` prints one JSON object naming the installed bundle
(`path`), the standalone export page (`index`), its integer `apiVersion`
and the viewer package `version`; without the package it prints nothing
on stdout, names `pip install "solid-node[viewer]"` on stderr and exits 1.
A consumer must reject a missing or too-old bundle before opening.

## Viewer HTTP surface

`solid develop` runs the viewer package's own server as a separate
process on the build directory; a build publication serves nothing. With
it running on `SOLID_NODE_PORT`:

- `GET /build/viewer.json` and `GET /build/<model path>` — the published
  document and the STLs it names.
- `GET /_viewer` — `{available, apiVersion, remedy}`; `GET
  /_viewer/bundle.js` — the bundle.
- `GET /_build_error` — `{}` when clean, otherwise the active error.
- `WS /ws/reload` — reload signal.
