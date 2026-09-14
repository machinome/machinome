---
name: solid-node-api
description: Complete public API reference for solid-node 0.6. Use when designing a mechanical project against solid-node capabilities, specifying nodes, parameters, drivers, ports, joints and relations without inspecting framework implementation, or implementing nodes, tests, scenarios, snapshots, and exports through supported public interfaces.
---

# solid-node public API

Use this as the authoritative public contract. It is the whole of what a
project may rely on: framework source is not available to you, so a behavior
this document does not describe is a gap to report, not a thing to discover.
Never guess an interface from a symbol name.

This describes solid-node 0.6 plus what followed it on the framework's
main branch: the declarative node API, the motion layer (joints,
relations, `solid_node.motion`), and open-run simulation through
`publish-the-mechanical-program` (ADRs 104–110). These additions are local
development capabilities, not a claim about the published 0.6.0 package.

## Imports

Each module answers one question, and an import line says which:

```python
from solid_node.node import (                  # what the machine is made of
    AssemblyNode, FusionNode,
    CadQueryNode, Build123dNode, Solid2Node, OpenScadNode, JScadNode,
    Build123dSheetNode, StlNode, StepNode, MolejoNode,
    declared_children, property_as_number,
)
from solid_node.parameters import (            # what is built
    Length, Angle, Count, Ratio, Scalar, Flag, Quantity,
    declared_parameters, DimensionError, ParameterError)
from solid_node.motion.ports import (          # a value between nodes
    Port, RotationalPort, TranslationalPort, SignalPort, Time,
    declared_ports, declared_time, get_coordinate, set_coordinate)
from solid_node.motion.joints import (         # where a body may move
    Revolute, Prismatic, Orbit, Free, JointRangeError, declared_joints)
from solid_node.motion.couplings import (      # a law between two coordinates
    Affine, UnreachedCoordinate, DoublyBound, NotInvertible, PrematureRead)
from solid_node.simulation import (            # how it runs
    Driver, Instruction, Button, Turn, Sim, ScenarioTest, RampProgram,
    qualified_drivers, qualified_instructions,
    RunConflict, UnsupportedLaw, TooManyCrossings, Crossing, Stop)
from solid_node.test import (
    TestCase, TestCaseMixin, testing_instant, testing_steps)
from solid_node.math import (
    sin, cos, tan, asin, acos, atan, atan2, sqrt,   # DEGREES
    abs, min, max, floor, ceil, sign,
    clamp, clamp01, ramp, lerp, wrap, piecewise)
```

The parameter kinds are exported by `solid_node.parameters` and by nothing
else: `solid_node.node` does not provide `Length`, and importing it from
there fails.
`SheetLeafNode` and `FlexibleNode` are also exported from `solid_node.node`
as the abstract bases of the sheet and flexible kinds; a project subclasses
their concrete adapters.

Ports, joints and couplings live in `solid_node.motion` — three submodules,
each answering one question, and nothing importable from the package itself:
`from solid_node.motion import RotationalPort` fails; only `from
solid_node.motion.ports import RotationalPort` works. `solid_node.node` no
longer exports `Port`, `RotationalPort`, `TranslationalPort`, `SignalPort` or
`declared_ports`; importing them from there raises `ImportError` naming
`solid_node.motion.ports`.

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
| `StepNode` | `step_source` (+ `part`, `adjust()`) | — | yes | nothing |
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
- `StlNode`: `stl_source` is an `.stl` beside the module. The
  artifact is materialized from it; nothing is repaired. A non-watertight
  body fails the build naming the defect unless `require_watertight =
  False` admits it knowingly (admission only, never geometry). A multi-body
  file is a pack: declare `body = <0-based index>` (components ordered by
  centroid x, y, z); omitting it fails with a per-body inventory of
  centroid, bounds and volume. `adjust(self, mesh)` receives the selected
  body as a trimesh mesh and returns the corrected one; what it returns is
  the artifact. The declaring module is tracked as a source. An `StlNode`
  makes any fusion holding it faceted and slow. It is never exact.
- `StepNode`: `step_source` is a STEP file, relative to the module (an
  absolute path resolves to itself); the file need not be committed.
  `part` names the product as the file carries it. A file with exactly
  one candidate product (one part alone, or one part wrapped in an
  assembly root) needs no `part`; a multi-component root is never
  selected by omission. A missing or wrong name fails with the document's
  inventory (name, kind, occurrences, solids, bounds, volume per
  product); two products of one name fail naming the ambiguity. The
  geometry is the product's own frame, never an occurrence's placement.
  `adjust(self, shape)` receives a cadquery `Shape` and returns the
  corrected one; a result holding no solid fails naming what it holds,
  and nothing is sewn silently: call
  `solid_node.node.adapters.step.solids_from_faces(shape, tolerance)`
  from `adjust` knowingly. A subclass declaring no `color` takes the
  product's colour from the file (sRGB `#RRGGBB`). One document is read
  per file per process, however many nodes select from it. It is exact:
  `shape()`, `.brep`, exact fusion and the spatial contracts work as for
  `CadQueryNode`. `StepAssembly(path)` in the same module reads the
  document's structure without building it: `products` and
  `occurrences`, each occurrence with its placement and world matrices
  and the exact `angle_deg`/`axis`/`translation` that reproduces it as
  `rotate` then `translate`; a mirrored or scaled placement is reported
  improper, not decomposed. Vendor STEP is fillets and threads: declare
  `angular_deflection = 0.5` (one measured part: 19.9 MB at the default,
  1.76 MB at 0.5).
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
ports are read and bound. Under a running simulation the run binds the
joint coordinates; `simulate()` may compute plain ports from them but
must not overwrite them (see "Running simulations"). Each operation it
applies is motion: stated
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

## Drivers, time, ports, joints, relations, instructions

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
  backs is rejected listing what is declared. Under a running root it
  also accepts qualified joint-coordinate ids, including joints on leaves;
  this is the run's binding path, not a command or a replacement for
  `sim.restore()`. `time` is global and needs no declaration.
- `clear_state(*names)` removes entries (all with no names) and
  re-simulates symbolically.
- `set_keyframe(t)` is `set_state(time=t)`; `clear_keyframe()` is
  `clear_state('time')`. Both recurse and are no-ops on leaves and
  fusions. Nothing accumulates across cycles; rest placement is untouched.
- Without a declaration, `self.time` is symbolic `$t` (0 through 1 on
  the timeline), or the bound number. A root assembly may instead declare
  `time = Time(loop=seconds)` or `time = Time.running()`, imported from
  `solid_node.motion.ports`. `Time()` without a base is refused. A loop
  is positive finite seconds: unbound reads become `$t * seconds`, while
  a bound value is already in seconds. Running time is elapsed seconds
  that never wrap; outside a document producer its unbound preview is
  still bare `$t`, but its version-5 document publishes the clock name
  `time`. `Sim` binds `tick * dt` seconds under every base.
- Declare `Time` only as `time` on the root assembly, never a leaf or a
  linked descendant; descendants read their root's base. `Root.time.mode`
  is `'loop'` or `'running'`, and `.loop` is the span or `None`.
  `declared_time(cls)` returns the inherited declaration or `None`.
  Leaves and fusions have no readable `time`.

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
`get_coordinate(node, name)` / `set_coordinate(node, name, value)` read and
bind any coordinate — a port, a joint's, or one of a multi-coordinate
joint's — by the exact name the port enumerator reports it under, plain or
dotted (`pose.roll`); a name that enumerator does not report is refused
rather than answered with `None`.

**Joints** say where a body MAY move, next to the body, once: a class
attribute of the node it moves, from `solid_node.motion.joints`.
`Revolute(axis, at=(0,0,0), range=None, unit='deg')` turns a body about a
line; `Prismatic(axis, at=(0,0,0), range=None, unit='mm')` slides it along
one (`at` does not affect a `Prismatic`'s placement — a translation along a
line is the same wherever the line is taken to pass — it is carried only
as the declared position of the slide, for a reader or an exporter);
`Orbit(axis, at=(0,0,0), carries=(0,0,0), range=None, unit='deg')`
carries a point of the body round a line while the body's own attitude
stays fixed; `Free(at=(0,0,0), angle_unit='deg', length_unit='mm')` floats
a body on all six, `at` being the point the three rotations pass through
(no `axis`, no `range` — a free body turns about its own frame's three
directions and has no travel to bound). A joint owning ONE coordinate
names it after the joint (a
`Revolute` called `turn` gives a coordinate `turn`); reading the joint on
an instance yields that coordinate's port slot, assigning to it binds
through the same path `connect()` uses, and `declared_ports` reports it
under the joint's name. `Free` owns SIX — `pose.roll`, `pose.pitch`,
`pose.yaw` in `angle_unit`, `pose.x`, `pose.y`, `pose.z` in `length_unit` —
each a dotted name and NOT a Python identifier: bound by assignment or by
a relation, never by a wiring keyword; an unbound one places nothing (a
plain zero) while still reading `.value is None`, and binding any one
re-places the whole joint, so the order the six are bound in never shows.
Assigning to a `Free` AS A WHOLE (`self.chassis.pose = 12.0`) is refused
naming the joint and its six coordinates. Its composition is FIXED, not
choosable by declaration order: `R(roll, x̂)·R(pitch, ŷ)·R(yaw, ẑ)·T(x, y,
z)`, about `at`, in the body's own frame's three fixed directions — the
translation is the OUTERMOST operation, so it displaces along those fixed
directions rather than along whatever the three rotations have just
turned the body to. `declared_joints(cls)` enumerates a class's joints by
name with no instance constructed, in DECLARATION order (base before
subclass, written order within a body, a redeclared joint keeping the
position its base gave it); a name cannot be both a joint and a port on
one class.

**The frame rule (ADR-097): a joint is stated in the frame of whoever
declares it.** Written in a class body, `axis`, `at` and (`Orbit`'s)
`carries` are read in THAT BODY'S OWN rest frame — the frame its own
`render()` states its geometry in — never the parent's, and the framework
transforms nothing. `at` defaults to `(0, 0, 0)`, the body's own origin, so
a wheel turning on its own bearing needs no anchor at all; **an `at` that
restates the parent's placement is a bug (a double offset)** under this
rule, never a requirement. Because a joint's operations are placed
innermost, before the rest placement, **a body its parent rotates carries
its joint line WITH it** — one shared or catalogue class placed at several
sites, or several attitudes, states one declaration and gets the right
line everywhere; a body its parent only translates is unaffected either
way. A joint's arguments never depend on the node's rest placement, so a
joint is placeable even when that placement carries a value the framework
cannot evaluate numerically.

Each of `axis`, `at`, `range` and `Orbit`'s `carries` may be a number, a
declared-parameter token, a formula over them, or — for the whole
argument — a callable of the realized node, called once at realization;
none enters the node's build identity, so two instances differing only in
a resolved joint argument share one artifact. An unresolvable argument (an
undeclared token, a two-component or zero-length `axis`, a reversed
`range`) fails at realization naming the class, the joint and the
argument. **A `.repeat()` copy's `index` does not exist yet when that
copy's own joint arguments resolve** (it is assigned after the copy's
`__init__` returns): a callable reading `node.index` on a JOINT argument
fails by naming a missing attribute, even though the identical-looking
read works inside a relation's `law=`, which runs after the copy exists.
Derive a per-copy joint argument from the parent's own placement instead,
or drive the per-copy difference through a broadcast relation's `law=`.

**Composition (ADR-093): the joints of one class compose in DECLARATION
order, innermost first**, whatever order their coordinates happen to be
bound in — the first declared is applied closest to the body, the last
outermost; base-class joints come before a subclass's own, and a subclass
redeclaring an inherited joint keeps the base's position. There is no
ordering keyword: reorder the declarations to restack. Hand-written
`rotate()`/`translate()` in `simulate()` composes OUTSIDE the whole joint
block, keeping its own call order among itself.

`Orbit`'s eccentric radius and starting phase are never declared: they
derive from `carries` (the point of the body that travels, defaulting to
the body's own origin) and the line `axis`/`at` state. A `carries` that
lies ON that line derives a radius of zero and is refused by name at the
first binding — usually the sign that the body was not placed where the
class assumed it would be.

A numeric binding outside a declared `range` raises `JointRangeError`
naming the node's path, the joint, the value, the range and the unit; a
symbolic binding is not checked at bind time, because its value is not yet
known; a joint with no declared `range` accepts any binding. Either bound
may be `None` (unbounded on that side), a one-argument callable over
that joint's own coordinate, or `Bound(expression, reads=(...))`, a
callable over that coordinate AND the coordinates it names:

```python
from solid_node.motion.joints import Bound, Prismatic, Revolute

turn = Revolute(axis=(1, 0, 0),
                range=(lambda turn: 36 * floor(turn / 36), None))

class Plug(AssemblyNode):
    p1 = Pin()
    p2 = Pin()
    turn = Revolute(axis=(0, 0, 1), unit='deg', range=(0, Bound(
        lambda turn, a, b: 90 * (abs(a) <= 0.05) * (abs(b) <= 0.05),
        reads=(p1.lift, p2.lift))))
    key = Key(insert=Prismatic(axis=(0, 0, 1), unit='mm', range=(
        Bound(lambda insert, turn: -60 + 60 * (abs(turn) > 0),
              reads=(turn,)), 0)))
```

The first lower bound is the last seated ratchet tooth. The plug's upper
bound lets it turn only while both pins clear a window, and the key's
lower bound captures it at full insertion while the plug is turned. A
`Bound`'s expression is applied to the joint's own coordinate FIRST and
then to each read in the order `reads` states them, and returns a number
or an expression in `solid_node.math`'s vocabulary. Reads are named as a
relation's ends are — a joint or port the class body owns, a path through
child declarations, a driver of the class — and are refused at class
definition by the same rules (no list-held child, no `.repeat()`, no
sideways driver read) plus one: never the bounded coordinate itself.
Reads resolve against the joint's DECLARER: the node for a class-body
joint, the declaring parent for a site joint (`key = Key(insert=...)`
above reads `Plug`'s own `turn`), so declare the joint in the body whose
subtree holds everything it reads. A `Bound` that returns a plain number
or never uses a read it declares is refused at simulation construction,
and so is a read of a plain port or derived coordinate — a bound reads
the state; read the joint the port follows. A callable INSIDE the pair
reads coordinates; a callable for the WHOLE `range`,
`range=lambda node: (lo, hi)`, reads the realized declarer as before.

At numeric binding, a one-argument bound is evaluated at the proposed
value. A `Bound` with reads is not judged at bind time — its reads are
bound in solver order — but when the enumeration closes, over the values
then bound: an impossible pose raises `JointRangeError` naming the joint,
the value, the evaluated bound and every read with its value, and a read
left unbound or symbolic is not judged. In a running simulation a
one-argument bound is compiled and evaluated at the committed value at
the start of each tick, then held fixed for that tick; a `Bound` with
reads is a CONSTRAINT evaluated along the tick's path (see "Running
simulations"). An invalid/reversed evaluated pair is refused by name.
Under a run, travel that would exceed a joint range stops the pushing
inputs at the bound; it does not fail as an out-of-range pose. The driver's
own range remains presentation metadata (see "Running simulations").

**A joint may be declared where a child is placed (ADR-098):** a shared
catalogue class that carries no joint of its own — a bought bearing, a
fastener, `GearLockScrew` — is given one by the site that places it,
passed as a KEYWORD:

```python
screw = ZScrew(turn=Revolute(axis=(0, 0, 1), unit='deg'))
gear_screws = GearLockScrew(orbit=Revolute(axis=(0, 0, 1), unit='deg')).repeat(2)
```

`axis`, `at` and every further point are read in the DECLARING PARENT'S
OWN frame this time, never the child's, and `at` defaults to `(0, 0, 0)`,
the **parent's** own origin — the opposite of a class-declared joint's
default and the same sentence: the declarer's own origin. A child the
parent TRANSLATES therefore SWINGS about the parent's origin, not its
own, unless `at` names the child's own placement; that is the whole
point, not a hazard — it lets a class that knows nothing about where it
will be placed carry no anchor at all wherever the parent's own origin
already is the line (a motor shaft, a fork pivot, a drive axis). An
`Orbit`'s `carries` keeps its asymmetry here too: WRITTEN at a site it is
a point of the parent's frame, like `at`; DEFAULTED it is still the
CHILD's own origin, never the parent's, so the two defaults never
collapse onto the line and the derived radius is never forced to zero.

A joint passed this way is told apart from a wiring by the VALUE, never
by the keyword or by where the code sits: a coordinate the DECLARING
class already owns is a wiring, exactly as always (see "Passing a
coordinate down" below); a fresh `Revolute(...)`/`Orbit(...)`/`Free(...)`,
built right there in the argument list and belonging to no class yet, is
a site declaration; one declared on some THIRD class is refused. It is
NOT a parameter and NOT identity: the keyword never reaches the child's
constructor and never enters its build identity, so two children of one
class differing only in the joints their sites passed still key one
artifact. A site joint of a name the child's class already declares
REPLACES that declaration WHOLE — axis, anchor, unit, range together —
and keeps that name's slot in the composition order; a site joint of a
new name is appended after every class-declared joint, in keyword order.
The realized child is an instance of a SPECIALIZATION of the declared
class, built once per declaration site and shared by every child (and
every `.repeat()` copy) that site realizes: `isinstance` against the
written class holds, `type(x) is C` does not, and every enumerator that
reads a class — `declared_joints`, `declared_ports`, a relation's path —
sees the site's joint exactly as it would a class-declared one, under the
written class's own name, module and file.

A site joint MAY be passed to a `.repeat()` or a list-held declaration:
ONE declaration serves every copy, resolving the SAME arguments once
against the declaring parent, and each copy's own operations are carried
through ITS OWN rest placement — so one parent-frame axis, no anchor, no
sign, no index, produces opposite local axes at two opposed placements
(a mirrored roller pair, a mirrored belt-guide pair) with nothing written
per copy. A relation may still name the coordinate through the repeat
exactly as a class-declared one: `eccentric_shaft.spin.drives(
eccentric_bearings.orbit)`. A callable given for a site joint's argument
is handed the realized DECLARING PARENT (never the child, and never a
`.repeat()` copy's `index`, which does not exist yet when a site's
arguments resolve). **A site value is the line in the parent's frame
where the child FINALLY rests, after every rest operation the parent
applies to it** — so when one of those operations is conditional (a wrist
that may be pre-presented, a lid that may be flipped), a plain literal is
silently wrong for the branch it did not anticipate and the argument
needs a callable of the parent instead, reading the same condition the
parent's own `render()` does.

Refused by name at class definition: a site keyword naming a port, a
parameter, or any other attribute the child already answers to; a joint
declared on some third class; two site joints of one name; a site joint
and a wiring naming the same coordinate. The one thing a site joint costs
that a class-declared one does not: its operations are carried through
the inverse of the child's own rest placement before they are applied, so
a body whose rest placement carries a value the framework cannot evaluate
numerically refuses a SITE-declared joint by name — where a class-declared
one on the same body would not.

**Relations** say that one coordinate's motion IS another's, stated with
`drives` in a class body — no import needed for the verb itself, imported
names come only from `solid_node.motion.couplings`:

```python
power.drives(centre, law=going_train)
anchor.turn.drives(pendulum.swing)
elbow_pulley.turn.drives(elbow_belt.travel, ratio=PITCH_ARC)
tilt.drives(chassis.pose.pitch)                    # one coordinate of a Free
earth.drives(earth_beads.travel, law=earth_lift)   # broadcasts over a .repeat()
```

Either end may be a port, a joint, a child declaration (standing for its
class's ONE joint; refused by name if that class declares none or
several), a path through declared children, a derived coordinate, or — as
the SOURCE only — a `Driver`. A path through a `.repeat()`ed child is a
**broadcast**: it resolves to one relation per realized copy, permitted as
the DRIVEN end only and refused by name as a source; a path through a
list-held child, or through two repeated declarations, stays refused. A
path that stops on a multi-coordinate joint, or names a coordinate such a
joint does not own, is refused listing what it does own. Direction is
MECHANICAL (`a.drives(b)` says what turns what); which way it is SOLVED is
decided per run from whichever end is actually bound — forward through the
law, backward through its inverse — with nothing reordered by hand.

`ratio=`/`offset=` are shorthand for `Affine(ratio, offset=0)` (`driven =
ratio * driver + offset`), self-inverting unless `ratio` is numerically
zero; under a broadcast they resolve ONCE against the declaring instance
and every copy shares that one `Affine`. `law=` is a callable of two
arguments — driver first, driven second — called exactly ONCE per relation
(once per COPY under a broadcast) at realization, with the two realized
nodes that OWN the coordinates, so it may read a built library object, a
resolved parameter, or a broadcast copy's own `index`; it must return an
object with `forward(x)` and, if the relation is ever solved backwards,
`inverse(y)` — a plain function or lambda is taken forward-only. `ratio=`
or `offset=` given together with `law=` is refused at class definition.

Three refusals keep a wrong drive network from becoming a pose, each its
own error kind from `solid_node.motion.couplings`, each naming the node
paths and the relation as written: `UnreachedCoordinate` (nothing bound
either end, or for a relation of several sources, exactly the sources
still unbound); `DoublyBound` (something else — the author's `simulate()`,
a wiring, or another relation, even one that would give the same value —
already bound it); `NotInvertible` (the driven end is the bound one and
the law has no inverse, or the relation is one copy of a broadcast or
names several coordinates at an end, either of which is NEVER read
backwards whatever its law offers). A **derived coordinate**
(`relative_elbow = art3.elbow - shoulder`, `left = wrist + 2 * tool`) is a
linear formula over coordinates — `+`, `-`, unary `-`, and scaling by a
number or a declared parameter, nothing else — itself a coordinate of the
class, reported by `declared_ports` under its own name; a product of two
coordinates, or any nonlinear function of one, is refused where it is
written. It solves from its terms when all are bound, and for its one
remaining term when it is bound itself.

**Resolution is a whole-tree fixpoint (ADR-099).** Every assembly's
relations are still ATTEMPTED at the end of that instance's own simulate
phase, parents before children, so a parent's relation reaching a
coordinate by path still binds before the reached descendant's own
relations run. What one instance's own attempt cannot yet reach is
DEFERRED rather than refused, and resolved once every assembly in the
tree has had its phase — which is what lets a relation be stated inside
the class that actually owns it (a going train chained inside `Train`,
only the escapement bound two levels up in `Movement`) instead of
hoisted, duplicated, or re-sourced from a driver to route around a
per-instance-only solve. An ANCESTOR may source from a coordinate a
DESCENDANT's own relations solve, and it reads fresh on every re-pose, not
the previous enumeration's stale value. `DoublyBound` is never deferred: a
contradiction is not a question of timing and is raised the instant it is
found. A subclass may REPLACE a base's NAMED relation
(`drive = free_run.drives(Actuator.rotor.spin, ratio=1.0)` on a subclass
that assigns the name `Actuator.drive` used), keeping the base's position
in the solve, by the same rule a redeclared joint already follows; a bare
relation, or one whose name no base used, stays additive.

**A read of a coordinate its own relation, a derived formula or a wiring
is going to bind is refused by name — `PrematureRead`, from
`solid_node.motion.couplings` — never a silent empty slot**, because
`simulate()` runs before that class's own relations are solved and a
descendant's after that. The message names the coordinate, the reading
class and the binder. The ordinary rest-default guard is NOT refused by
this rule: `if self.coordinate.value is None: self.coordinate = default`
reads a slot the AUTHOR itself then binds, and that is a rest default, not
a mistake — the same case as always, for a joint's own coordinate or a
class's own derived coordinate alike. And it is now genuinely safe to
write on every run: a coordinate a relation, a wiring, or the AUTHOR'S OWN
`simulate()` bound is cleared, value and motion together, at the start of
that assembly's NEXT phase, so the guard finds the coordinate unbound and
rebinds and re-places the body on every enumeration rather than standing,
from the second run on, at a stale number with no operation left to show
for it. Under a running simulation the run-owned slots survive this
clear: the guard initializes the rest pose, then leaves those slots alone.

**A relation may name several coordinates at each end (ADR-100).** A
source group is written with `&`, free on every declaration that carries
`drives` and chaining flat (`x & y & z` is one group of three, never
nested); a driven group is written as a tuple, exactly as it already
reached the framework, or with `&` as well:

```python
(count & next_count).drives(sautoir.pawl.swing, law=pawl_deflection)
(x & y & z).drives((rod.spin, rod.lean, rod.swing, rod.rise), law=delta_rod)
(x & y).drives(towers.height, law=delta_carriage_law)   # several sources, one driven end
```

The law's two arguments are SHAPED by the sentence, never spread one per
end: a side naming one coordinate hands that coordinate's realized OWNER,
exactly as a one-to-one relation always has; a side naming several hands
the TUPLE of their owners, in the order written — a six-source law still
takes two arguments, never eight. `forward` is called with one positional
argument per SOURCE, in written order, and returns the driven value
itself for one driven end, or a SEQUENCE of exactly as many values, in
written order, for several; a return with no length, that is text, or of
the wrong length is refused by name at the moment it is applied, naming
the relation, the law, the driven ends as written and what came back. A
relation naming several coordinates at either end is read FORWARD ONLY,
whatever its law offers — the same reason a broadcast is: recovering
several sources from several driven values means comparing or solving
values, which the framework does not do — so `ratio=`/`offset=` and the
bare default law are refused with a group on either side; such a relation
always carries a `law=`. Guidance: write a DERIVED coordinate when the
combination is linear and keep both directions; write a multi-source
`law=` only when it is not, and accept losing the reverse.

**Passing a coordinate down** hands a child a port or joint the parent
already owns, by naming it as a keyword the child class declares:
`wheel = Arbor(turn=turn)`. This is a WIRING, not a parameter: absent from
the child's parameters and its identity, rebound from the parent's end
after every parent `simulate()`, refused at class definition when the
child cannot receive it, and a wired coordinate has exactly one binder —
binding the child's end by hand in the declaring parent is refused. A
joint owning several coordinates cannot be wired whole, and none of its
dotted coordinate names is a wiring keyword.

**Instructions** are declared moves, in an `instructions` dict on the
assembly that owns the move, in design units:

```python
instructions = {
    'Home': Instruction({'x_axis.position': 0.0, 'y_axis.position': 0.0},
                        duration=2.0),
    'Advance': Instruction(by={'x_axis.position': 5.0}, duration=0.2),
}
```

`Instruction(targets=None, duration=None, *, by=None)` requires exactly
one mapping: `targets` states destinations, `by` states relative travel
from the current input values. Supply a finite nonnegative duration in
seconds; a simulation requires whole ticks. Names resolve relative to the
declaring assembly, so a child instruction targets its own subtree.

Under an undeclared or looping root, triggering ramps from the current
values and a new trigger replaces the ramp; only absolute instructions
publish as viewer buttons. Under a running root, both forms publish in
version 5 and `sim.trigger(name)` returns a tuple of move handles. All
target inputs are checked for ownership before issuing commands; an
already-owned input refuses the instruction rather than replacing its move.

**Controls** put a request on the PART instead of a panel button, in a
`controls` dict beside `instructions`, on a root declaring
`Time.running()`:

```python
controls = {
    'units dial': Button(units.input.dial, 'Add one'),
    'turn units': Turn(units.input.dial, units_entry),
}
```

`Button(part, instruction)` is a press submitting that named instruction;
`Turn(part, input)` is a drag about the rotational coordinate the part
rides, issued as relative moves on `input`. `Slide`, for a prismatic
coordinate, does not exist yet. A control MOVES NOTHING ITSELF and carries
no state: it names a request the run already accepts, so ownership,
admission, stops and outcomes are exactly what `trigger`, `move` and
`rate` state, and a blocked drag reports blocked with no hidden backlog.

`part` is a NODE, written the way a relation's path ends are —
`units.input.dial`, a declared child or a path of declared children
through one — never a coordinate and never a driver. `Turn`'s `input` is
the `Driver` DECLARATION, not a qualified id string; a child's driver is
reached by declaring the control on that child, exactly as an instruction
over it is. Controls qualify through the declaring node's instance path
(`column.dial`), and a button's instruction qualifies with it, so it is a
key of the tree's instruction table by construction. `controls` is a
reserved name on a node class: a mistyped table is never silently inert.

Nothing about the gesture is declared. The coordinate is the one owned by
the nearest ancestor-or-self of the part that declares a joint the run
banks; the axis and the point the part turns about are read off the tree,
being the values that joint's own placement used; and `per_unit` — the
coordinate units the part moves per design unit the input travels — is
MEASURED from the compiled program at the rest bank, with that input
displaced a little each way and nothing else moved. It is a reading AT
REST: a law whose response to that input changes with state makes a drag
looser, never wrong, because the part is posed only by what the run
commits. Declaring the ratio would repeat a relation the program already
holds.

Every mistake is refused where its facts exist. At class definition: a
part the declaring class does not hold, a misspelt path segment, a
coordinate or a driver written where a part belongs, a repeated or
list-held child, a `Turn` over a driver that class does not declare, and a
`controls` value that is not a table of controls. When the tree is
enumerated or the program compiled: a `Button` naming no declared
instruction, a part no run-owned coordinate poses, a posing node declaring
several joints or a joint owning several coordinates, a `Turn` over a
coordinate whose domain is not rotational, a `Turn` whose input does not
reach the coordinate (naming the inputs that do). A control under a root
that does not declare `Time.running()` is refused when the simulation is
constructed and again at publication. At publication: a `Turn`
whose input moves the part by nothing at rest, and one whose two readings
disagree.

A version 5 document publishes a `controls` table beside `instructions`,
keyed and ordered by qualified name: `kind` (`"button"` or `"turn"`),
`part` and `joint` as node-name paths, `instruction` or `input` with
`per_unit`, `coordinate`, `axis` and `origin` (the axis and the point in
the joint node's own frame). It is ADDITIVE — the version does not move,
the key is absent when nothing is declared, and the compiled program's
`identity` never learns a control exists, so a model that declares one
publishes the same program as before. A control whose part THIS render
omitted is left out rather than refused; the headless browser-snapshot
capture publishes no table at all, as it publishes no instructions.

The viewer scopes the driving panel to the focused assembly, with a breadcrumb into
subassemblies; declare a whole-machine move on the root. Versions 1–4 use
driver sliders and absolute instruction buttons. A viewer supporting the
running controls uses nudge, hold-to-jog and instruction buttons with
committed readouts instead of position sliders, and run/pause/step/speed/
elapsed-time/reset transport instead of a seekable timeline. A viewer that
reads the `controls` table (viewer API 12) also hovers each declared part,
presses it to submit its instruction and drags it round its own axis,
reporting a blocked travel where the run refuses it. Check the installed
viewer's `solid viewer` report, not its package version alone.

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
OpenSCAD viewer. On an exact leaf (`CadQueryNode`, `Build123dNode`,
`Build123dSheetNode`, `StepNode`) and on `FusionNode`,
`linear_deflection` (mm, default 0.1) and `angular_deflection` (rad,
default 0.1) set the STL tessellation of that node's own artifact: not
a constructor parameter, not artifact identity (editing it rebuilds the
same artifact through the declaring module's currency), shaping only the
mesh, never `shape()` or the `.brep`. A fusion declares its own and does
not inherit a child's. A coarser mesh moves faceted-kernel verdicts and
changes the printed-piece id; the exact kernel is unaffected. A value
that is not a positive finite number fails at export naming the node
and attribute.

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
on a bare path to such a file runs the node classes its companion test
cases declare (each `TestCase` there must declare `node = TheClass`) and
builds no other; with no companion, every node it defines.

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
  it is not. `StlNode` and `StepNode` track their own file and declaring module.
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
displacement in mm instead, and giving both raises. Directions are the
node's own: the perturbation is inserted before every operation of the
node, so all of its rotations, a leading one included, carry them.
`directions='forward'` checks only the positive sense. `assertFreeWithin`
accepts a list of amounts. The perturbation is always removed
afterwards. `volume_epsilon` counts an intersection
below the given volume as none; it applies only on the faceted path, is
ignored with a warning when every comparison routed exact, and is a smell
rather than a tool.

A run compares on one **kernel**, a property of the run and never of the
model: `exact` (the default; two exact nodes are decided on their solids)
or `faceted` (every question decided on the parts' meshes at tessellation
precision, about 30x cheaper on flexible parts). `solid test --faceted`
or `--exact` selects it; without a flag `SOLID_TEST_KERNEL` in the
project's ignored `.env` does; without that the run is exact. A faceted
run prints `Comparing on the faceted kernel ...` before the first build
and ends its summary line with `(faceted kernel, volume epsilon E mm³)`;
an exact run's output is unchanged. `--volume-epsilon MM3` (else
`SOLID_TEST_VOLUME_EPSILON`, else 0) makes a faceted run report every
intersection of at most that volume as empty, before any assertion reads
it; the exact kernel refuses it. `node.exact` and the build do not change
with the kernel. A faceted verdict is at the precision of the 0.1 mm STL
tessellation and is not commit evidence: a project's `.env` may select
the faceted kernel for the loop, and the exact run is the one a verdict
is certified on.

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

A driven machine is also testable in motion.
`Sim(node, dt, meshes=False, state=None, record=None)` steps an
assembly with a fixed step whose instants are integer ticks (`sim.time`
is `tick * dt` seconds; a non-tick instant is rejected). `sim.at(t)
.trigger('Home')` or `.run(callable)` schedules an action (actions due at
the current tick fire before the first step); `sim.every(period, fn,
*args)` calls `fn` on a cadence; `sim.run(duration)` steps, binding a full
qualified snapshot plus `time` each tick. Without a running time base it
appends every tick to `sim.trajectory`; a running root records only when
requested (below). `state=` overrides initial declared drivers by qualified
id in native units, never joint coordinates. `sim.state` returns a fresh
mapping of the current bank by qualified id;
`sim.tick`, `sim.cadence_costs` and `sim.assertion_stats` report progress
and cost. A triggered `Instruction` ramps as a `RampProgram` without a
running base; under a running root it issues commands which may meet a stop.
Integer driver ramps use native steps; a physical stop can admit fractional
travel.

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

### Running simulations

Declare `time = Time.running()` on the machine root when operation must
retain history. This is the same `Sim` and the same `drives` laws, with a
different reading: a continuous law moves its driven coordinate by
`f(end) - f(start)` from where it stood. A periodic law contributes its
continuous travel with discontinuous jumps subtracted, so a register
retains each revolution's throw. There is no project-declared `State`,
event/memory protocol, second running face on a law, or state accumulated
inside `simulate()`.

The run banks every driver and every joint coordinate in the linked tree,
including joints on leaves, site-declared joints and all six coordinates
of a `Free`. Plain ports and derived coordinates are recalculated from
that bank each tick. Rest values come from the ordinary pose at time zero
and the requested driver values. Every joint coordinate must be bound at
rest, by a relation, wiring or guarded rest default:

```python
def simulate(self):
    if self.slide.travel.value is None:
        self.slide.travel = 4.0
```

An unconditional hand binding of a run-owned joint raises `DoublyBound` at
construction; express its law with `drives`. Plain ports may still be fed
in `simulate()` from owned coordinates, for example a spring's height or
a readout. But an imperatively fed port cannot source a compiled law into
a banked coordinate; express that input through a relation or a joint.
A single tree has one run owner: constructing a new `Sim` over it starts
fresh and releases the previous simulation, which then refuses to advance.

This minimal travel model shows repeatable commands and a physical stop;
replace the grouping `Carriage` with the project's actual moving assembly:

```python
from solid_node.node import AssemblyNode
from solid_node.motion.ports import Time
from solid_node.motion.joints import Prismatic
from solid_node.simulation import Driver, Instruction, Sim

class Carriage(AssemblyNode):
    travel = Prismatic(axis=(1, 0, 0), range=(0, 12), unit='mm')

class Feed(AssemblyNode):
    time = Time.running()
    feed = Driver(default=0, range=(0, 12), unit='mm')
    carriage = Carriage()
    feed.drives(carriage.travel)
    instructions = {
        'Advance': Instruction(by={'feed': 5}, duration=0.2),
        'Home': Instruction({'feed': 0}, duration=0.2),
    }

sim = Sim(Feed(), dt=0.02, record=64)
for _ in range(2):
    sim.trigger('Advance')
    sim.run(0.2)
assert abs(sim.state['carriage.travel'] - 10) < 1e-9
command, = sim.trigger('Advance')
sim.run(0.2)
assert command.status == 'blocked'
assert abs(command.admitted - 2) < 1e-9
assert sim.state['carriage.travel'] == 12
saved = sim.snapshot()
sim.trigger('Home')
sim.run(0.2)
sim.restore(saved)
assert sim.state['carriage.travel'] == 12
sim.reset()
assert sim.state['carriage.travel'] == 0
```

**Commands and units.** `sim.move(input_id, by=travel, duration=seconds)`
or `sim.move(input_id, to=value, duration=seconds)` takes exactly one of
`by`/`to`. Only declared drivers are commandable, by qualified id; a joint
coordinate is an output. Travel and destinations are design units; the
driver bank remains native units (`scale` converts between them). Use a
nonnegative duration in whole ticks; omitted/zero duration settles at the
current tick without advancing time. `sim.rate(input_id, rate)` requests
design units per simulated second until `sim.rate(input_id, 0)` releases
that rate and marks its handle completed. A stop also terminates a rate.
There is one command owner per input: a second move/rate refuses while
that input is owned. Multiple inputs can run together.

Move/rate handles report `status` (`active`, `completed`, `blocked`,
`refused`, `cancelled`), `input`, `kind`, and travel `requested`, `admitted`
and `remaining` in design units; rates have no requested total or
remaining travel and expose `rate`. `sim.commands` is the tuple of
currently held commands. A blocked command reports only the travel
admitted before the stop and never resumes automatically; issue a new
request to retry or reverse. Read the result, not just the requested target.

Known Python limitation at framework commit `9238ef8`: `handle.cancel()`
sets `status` to `cancelled` but does not release the input or suppress
its subsequent travel. A 5 mm move over 0.2 s cancelled before the first
0.02 s tick still moves 0.5 mm on that tick. Do not rely on it to stop or
replace a move until the framework fixes this; `rate(input, 0)` releases
an active rate, and restore/reset replace the run state. This is a
measured defect, not the intended cancellation contract.

**One law, two readings.** Laws are compiled once at construction by
applying them to symbolic sources, in the direction the rest pose solved
each relation. Use arithmetic and `solid_node.math`, not Python `math`,
Python `if`/`and`/`or` over coordinates, or per-tick mutation. The math
helpers keep numeric and symbolic readings:
`clamp(x, lo, hi)`, `clamp01(x)`, `ramp(x, start, end)` (clamped 0–1),
`lerp(a, b, u)` (unclamped), `wrap(x, period=360)` (in `(-period/2, period/2]`),
and `piecewise(x, [(x0, y0), ...])` (continuous linear interpolation,
holding the endpoint values outside the ordered plain-number x positions).
Use the framework's `min`/`max`/`abs` for symbolic inputs too.

`floor`, `ceil`, `sign`, `%` and comparisons may appear in a law: the run
locates their crossings and integrates each continuous piece. A jump
itself moves nothing. A law made only of jumps, such as `floor(turns)`,
is refused; so is a jumping law into only plain ports/derived coordinates,
which cannot retain its history. Put the law into the joint and let a port
follow the joint. A group mixing banked and nonbanked driven ends is
refused. A constant law contributes zero; an undriven joint holds.

Disengagement is a zero-slope region or a gate in a multi-source law:

```python
def clutch(sources, target):
    return lambda shaft, sleeve: -2 * shaft * (sleeve > 0.5)

# shaft and sleeve are declared child nodes with these joints:
(shaft.turn & sleeve.travel).drives(wheel.turn, law=clutch)
```

The wheel holds while disengaged and admits shaft travel only during
engagement, including a gate crossing within a tick. A gate does not
itself block the input command: that input may complete with its driven
coordinate unmoved. Use a joint range to express a physical stop. Multiple
contributions to one coordinate belong in one multi-source law, not two
competing bindings; inputs are never back-driven.

**Stops and precision.** A joint's inclusive range is a physical stop.
Travel beyond it stops at the bound and blocks only inputs whose movement
actually pushes that coordinate; independent or disengaged inputs keep
moving for the rest of the tick. Landing exactly on a bound completes
normally. A spring's plain height port has no stop of its own: bound the
mechanical joint that compresses it and derive its height from that joint.
Driver slider ranges and clamping a displayed flexible height do not
constrain the machine. No mesh-contact detection, force equilibrium,
spring stiffness or material limits are inferred by the simulation.

Affine crossings are solved exactly. Nonlinear crossings are bracketed
over 64 subdivisions and bisected; multiple turns inside one subdivision
can be missed. More than 1000 crossings of one law in a tick is refused.
For a bound over its own coordinate alone, an excursion outside the
range that returns inside before the tick ends can escape stop detection
(impossible for an affine determiner). With nonlinear upstream laws, only
the stopped coordinate lands exactly on its bound; related travel uses
the linearized source path. Choose and test a smaller `dt` where these
limits matter.

**A bound that reads other coordinates is a constraint.** Its own
coordinate in the expression takes the tick's committed value, so a
ratchet's tooth stays the tooth it started on; every read takes the value
it has along the tick's path, computed over the edges that determine it.
Detection looks inside the tick: whenever a READ moves, the constraint
is sampled at 64 fractions of the tick, stopped at the first sample
carried outward and bisected to the crossing tolerance, and the
coordinate is left inside the bound by at most that tolerance of the
tick's travel rather than snapped onto it; when only the bounded
coordinate moves, the bound is the number its standing reads give and
the coordinate stops exactly as a self-only bound does. The stop blocks
every input whose own motion carries the constraint outward — through
the bounded coordinate OR through what it reads — so a dependency that
would invalidate a standing coordinate is stopped where the constraint
becomes active and the standing coordinate does not move: a plug bounded
by its pins' lifts stops the key's withdrawal, `sim.stops` naming the
plug's coordinate and the key's input. An input moving a read so as to
relieve the constraint runs its full tick, and a command on it completes.
A tick in which nothing the constraint depends on moves pays nothing
extra, and one in which only the bounded coordinate moves pays one
evaluation; a tick in which a read moves pays up to 64 sub-program
passes for that constraint whether or not it stops (0.36 ms quiet,
5.4 ms active, 3.3 ms blocking on a four-edge fixture; on the pin
tumbler lock, whose plug bound reads five `piecewise` lift laws, 2.9 ms
idle, 4.7 ms turning, 45 ms advancing the key). Keep the laws a bound
reads small, and declare one bound per coordinate side that needs it. A violation that begins
and ends inside one of the 64 sub-intervals is missed, and the pushing
test is net over the tick. A published document carries the bound's
expression over the ids it reads under the same version 5; the shipped
viewer worker refuses such a document by name until the viewer's own
cycle executes it.

**Naming under a running root.** `set_state` records every joint
coordinate under its bare name beside the drivers, so a root driver named
like any joint anywhere in the tree — a `turn` driver beside a
`plug.turn` joint — is refused as ambiguous at simulation construction:
name the input differently. A `.repeat()` child that owns a joint is
refused too, because `drivers-0` is not a legal id segment, and a
`.repeat()` child whose PORT a relation drives makes `solid build`
refuse the document (`the program names 'PenSpring.height', which is a
FALLBACK derived from a class name`) although the run itself works:
under a running root, hold every child that owns a joint or a driven
port on a named attribute. A running root's drivers are bound by a
`Sim`, a `set_state` or the loader, never by construction: a bare
`assemble()` on one raises on the first unbound driver. And declare a
relation whose driven coordinate a ROOT relation also reads in the
root's body: a child-declared relation read by a root-declared one
publishes as a false `DoublyBound` (framework wart, 2026-09-14).
`RunConflict`, `UnsupportedLaw` and `TooManyCrossings` are exported from
`solid_node.simulation`. A refused tick commits no bank, time, pose or
record change, and the commands that attempted travel retire `refused`.

**Snapshots and evidence.** `sim.snapshot()` captures the bank, tick,
active commands, `dt` and program identity; `sim.restore(saved)` restores
that value and refuses a different program or step size before mutation.
`sim.initial` is the initial snapshot and `sim.reset()` restores it.
Restore recreates command handles and cancels the old ones; reread
`sim.commands`. Scheduled Python callbacks/cadences are not part of the
snapshot, so reschedule consumed actions when replaying a scenario.
Inspecting or rendering the same bound tree advances nothing.

Running simulations keep no history by default (`record=None`);
`record=N`, a positive integer, keeps three separate bounded rings:
`sim.trajectory` with `(tick, bank)` entries, `sim.crossings` with located
jump events, and `sim.stops` with reached bounds and blocked inputs.
Restore/reset clear all three. `sim.every()` can inspect every tick
without keeping an unbounded recording. `sim.running` reports the mode;
the command/snapshot/program surface is refused on other time bases.

Use scenario tests for retained state: repeated instructions, partial
travel, both directions at each stop, disengagement/re-engagement,
snapshot replay, and interleaved independent controls. Assert geometry on
the same stepped node, with `meshes=True` and a declared cadence; changing
`--time` or rebinding a final input position does not replay that history.

## CLI

```text
solid new <name>
solid build   [ref] [--set NAME=VALUE ...]
solid test    [ref] [--set ...] [--failfast] [--exact | --faceted]
      [--volume-epsilon MM3]
solid snapshot [ref] [--set ...] -o out.png [--time 0..1] [--autocenter]
      [--drive NAME=VALUE ...]
      [--viewall] [--camera tx,ty,tz,rx,ry,rz,dist | ex,ey,ez,cx,cy,cz]
      [--imgsize 1920x1080] [--renderer openscad|web]
      [--projection ortho|perspective] [--colorscheme Cornfield|...]
      [--render | --preview] [--view axes,crosshairs,edges,scales,wireframe]
solid export  [ref] [--set ...] [-o export] [--fps 30] [--frames 360] [--no-widget]
solid develop [ref] [--set ...] [--web | --openscad | --web-dev | --no-web]
      [--callback URL] [--debug-builder]
solid viewer
solid import-step FILE [--into PACKAGE_DIR] [--model NAME]
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

`solid snapshot --drive NAME=VALUE` sets declared drivers by qualified id,
in native units as with `set_state`; `--set` changes build parameters
instead. Drivers not overridden use their defaults. `--time` is the 0–1
timeline fraction: it binds the fraction for an undeclared root or the
fraction times the declared loop in seconds. A running root accepts only
`--time 0` (the default); a nonzero time is refused naming `--drive`.
Its still is the untimed rest pose at those input values, not an elapsed
run or a saved state; verify accumulated motion on the stepped node.
Leave the renderer at the default `openscad`:
it is fast, needs no browser, self-wraps with `xvfb-run` when headless,
and stays the default whatever is installed. The `web` renderer exists
so a host can get a transparent background through headless Chromium; it
needs the separately installed `solid-node-viewer` package with its
browser (`pip install "solid-node[web-snapshot]"` plus `playwright install
chromium`), rejects the OpenSCAD-only options and an unsupported document
version by name, and never falls
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

`solid import-step FILE` scaffolds project-owned source from a STEP
document's assembly structure: `parts.py` with one `StepNode` subclass
per part product (exact `part` name, `angular_deflection = 0.5`) and
`assembly.py` with one `AssemblyNode` per assembly product, one declared
child per occurrence and a `render()` placing each by the document's own
`rotate`/`translate` pair, at rest, with no driver. It loads no node,
never overwrites (either file present stops it), refuses a document with
a mirrored or scaled placement, and prints the manifest line to add
instead of editing `pyproject.toml`. Edit the generated files as your
own; regenerate only by removing them.

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
  {fps, frames, loop?}, drivers, instructions, bindings?, program?, root, pieces}`.
  `version` is 2; 3 when the tree holds a flexible part; 4 when the
  document carries a `bindings` table, which the serializer publishes
  whenever a subexpression repeats across the document (a shared value
  reaching two nodes is enough, so nearly every animated model is version
  4). A root declaring `Time.running()` always publishes version **5**,
  with `program`, even if it has no flexible or shared expressions.
  `bindings` is an ordered array of `{name, expression}` entries,
  names `_b0`, `_b1`, ..., each expression under versions 2–4 naming only
  `$t`, declared driver ids and earlier entries; an operation or flexible `params`
  expression references an entry by its bare name, and an expression the
  serializer cannot read is published verbatim with a warning. A viewer
  older than API 7 refuses version 4. `drivers` and `instructions` are
  tables keyed by qualified id (empty for a driverless model). Each tree
  node carries `name`, `type`, `color`, `mtime`, `operations`, and either
  `children`, a rigid node's `model` path relative to the build directory
  with its `piece` id, or a flexible leaf's `flexible` spec. Operations
  serialize as `['r', angle, axis]` / `['t', vector]` with raw
  expressions; animated values keep symbolic `$t` and qualified driver
  ids under non-running roots. Under version 5, joint placements name
  their banked coordinate ids; ports and flexible parameters read the
  committed bank, and the clock is `program.clock` (`time`), not `$t`.
- In version 5, `program` carries the coordinate table and rest values,
  intermediates, ordered compiled edges and jump plans, spans, candidate
  input sources, identity, clock name and integration constants. It is
  the program Python `Sim` runs, not a second project-authored format.
  Both absolute and relative instructions publish. A running root that
  cannot construct a run cannot build/export a program either. Shared
  expressions may additionally name bank coordinates, the clock and
  compiler-minted branch placeholders. Do not hand-author those tables.
- the rendered STLs at the `model` paths.
- `errors.json` — `{error, tstamp}`, written atomically on a failed build
  and removed after the next successful one. A failed build after a
  success may leave a **partially updated** model beside it; the snapshot
  still names files that are present and complete, but do not read it as
  the previous model.

`solid viewer` prints one JSON object naming the installed bundle
(`path`), the standalone export page (`index`), its integer `apiVersion`,
supported `documentVersions`, and the viewer package `version`; without
the package it prints nothing
on stdout, names `pip install "solid-node[viewer]"` on stderr and exits 1.
A consumer must reject a missing or too-old bundle before opening.
An older report without `documentVersions` means support for `[1, 2, 3, 4]`,
not 5. Build/develop/export still publish version 5 and warn if the
installed viewer cannot render it; a web snapshot refuses before opening
the browser. Viewer API 8 supports version 5 and the running controls in
the current development checkout; that does not imply a published release.

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
