---
name: solid-node
description: Build and test parametric mechanical components in a solid-node project. Use when creating or modifying nodes (parts, assemblies), declaring parameters, writing mesh contract tests, driving and animating assemblies, or wiring components into the model the maker sees. solid-node treats mechanical parts as software — declared parameters, unit tests, integration contracts verified on meshes.
---

# Building solid-node components

solid-node is a Python framework for parametric, 3D-printable mechanical
projects. A project is a package — `solid new snowman` scaffolds
`snowman/snowman/`, with the root node in `snowman.py` beside an empty
`__init__.py`, and `pyproject.toml` naming it under `[tool.solid-node]`. Its
nodes form a tree: leaf nodes produce geometry through a CAD backend, assembly
nodes compose, place and drive children. Mechanical contracts (parts mesh,
fit, clear, transmit torque, stand up) are expressed as tests over the
rendered geometry.

Commands (run from the project directory, with the project's venv):

    solid build                 # build once and publish the model
    solid test <pkg>/<node>.py  # run tests for one node (passing the
                                # test_*.py path works too)
    solid test --faceted        # the same run decided on meshes: the
                                # fast loop, never commit evidence
    solid test --exact          # the certified run (the default when
                                # neither flag nor the project's .env
                                # says otherwise)
    solid snapshot -o out.png --autocenter   # render an image
    solid build --set bore=32.0 # the same model at another parameter value

Commands take an optional node reference — `package.module:Class`,
`path/to/file.py`, or `path/to/file.py:Class`. Omit it and the project's
model from `[tool.solid-node]` in `pyproject.toml` is used. A directory is
not a reference.

`solid develop` also exists, and opens a live viewer that rebuilds on save —
the browser viewer from the separately installed `solid-node-viewer` package,
or OpenSCAD when that package is absent. Do not run it here: the shop already
watches the project, rebuilds it, and keeps the maker's view current. Your
builds are verification of your own work, and they are finite.

Read `../solid-node-api/SKILL.md` in full before building unless it is already
loaded. It is the authoritative public surface, and it is all you have:
framework source is not available to you. This manual owns implementation
craft: parameter flow, placement and motion, contract tests, measurement, and
the definition of done. If the API skill does not describe the behavior you
need, report the gap — never infer an interface from a name or a traceback.

## Writing nodes

Declare a node in its class body. Parameters are typed declarations from
`solid_node.parameters`; derived dimensions are formulas over them; children
are constructed in the class body and realized per instance:

```python
from solid_node.node import AssemblyNode, CadQueryNode
from solid_node.parameters import Length

class Shaft(CadQueryNode):

    diameter = Length(4.8, min=0)
    length   = Length(30.0, min=0)
    flat_h   = Length(1.0, min=0)

    def render(self):
        ...return a cq.Workplane; self.diameter is a plain float here...


class Spindle(AssemblyNode):

    shaft_diameter = Length(4.8, min=0)
    clearance      = Length(0.3, min=0)

    bore = shaft_diameter + 2 * clearance        # a relationship, not a literal

    shaft = Shaft(diameter=shaft_diameter)
    sleeve = Sleeve(bore=bore)

    def render(self):
        self.sleeve.translate([0, 0, SLEEVE_SEAT])   # rest placement
```

Rules:

- **Wrapped is a parameter, bare is a constant.** A `Length(...)` enters the
  build identity, propagates to children and can be set from the shell; a
  bare number is placement or process detail Python already handles. Never
  hand-forward parameters to `super().__init__()` in a declarative class:
  identity is complete by construction, which is the point.
- **A parameter that depends on the parent has no default.** Declare it as
  `Length(min=0)` and let the parent supply it; a made-up default is a
  quiet mistake the framework would otherwise cache.
- **Children are declared, never instantiated, in a class body.** Each
  parent instance realizes its own. Identical units are one declaration
  repeated (`CylinderUnit().repeat(count)`); different units are individual
  attributes or a literal list. Per-unit variation never lives in the
  declaration: placement variation is `enumerate` plus constants in
  `render()`, drive variation is a port fed in `simulate()`.
- **Siblings do not reach into each other.** A value two children share is
  declared on their parent and passed to both. The framework refuses
  `ConRod(pin_bore=piston.pin_bore)` in a class body; declare `pin_bore` on
  the parent.
- **Guards over several parameters go in `check()`**, raising `ValueError`
  with the reason; single-value bounds are `min=`/`max=` on the
  declaration. Both refuse construction, before any child is realized.
- `render()` returns the backend's native object on a leaf. On an
  assembly or fusion with declared children it returns nothing and only
  places and selects; a pure grouping node needs no `render()` at all.
- `omit()` selects structure from parameters in `render()`; never from
  time, and never in `simulate()`.

A class with an ordinary `__init__` still works and mixes freely with
declared ones. When you touch such a class, prefer migrating it: store
nothing on `self` by hand, declare instead. In the constructor form every
parameter must be forwarded to `super().__init__()` or variants share a
stale artifact, and assembly children must be created in `__init__`.

A leaf's `render()` may return several solids and nothing checks that
they touch. If they are one printed part, union them with real
overlap; if they are not, they are separate nodes. A backend "union"
of solids that do not overlap does not fail — it hands back a
compound, which exports as one file holding several loose pieces.

Children are named automatically after the attribute their parent holds
them under (`self.input_gear` → `input_gear`; members of a list or a
`repeat` get `attr-N`), so the viewer tree and test vocabulary agree.
An explicit `name=` kwarg overrides; names never affect build
artifacts, which stay parameter-keyed.

## Files, references and rebuild cost

How a project is laid out is the project's choice, not the framework's.
Know the costs and pick deliberately:

- Rebuild tracking is per node. Two node classes in one file share one
  stamp, but the content check beneath it is scoped to each class: editing
  one rebuilds that node and the fusions above it and only restamps the
  other. Editing what they share in the file — imports, constants, helper
  functions, a class either of them names — rebuilds both.
- A bare path to a file with several node classes is ambiguous: `solid
  build root/parts.py` and `solid snapshot root/parts.py` fail listing the
  candidates, so name the class (`root/parts.py:Gear`). `solid test`
  tolerates the bare path and runs the nodes its companion's `TestCase`s
  declare (`node = TheClass`, mandatory beside such a file); a
  sub-assembly no test declares is not built, so a file holding a machine
  and the sub-assemblies only it can bind is tested by its bare path.

One class per file, named after it, is what `solid new` sets up; it buys
unambiguous bare paths, not a cheaper build. Do not reorganize an inherited
layout for the cache's sake; name the class in references and in tests.

Shared values live where their kind says: design parameters are declared on
the node that owns them and passed down (see the next section); constants —
layout tables, placement offsets, process limits, kinematic helper functions
— live in a module that defines no node, conventionally `layout.py`,
`parameters.py` or `kinematics.py`. The framework tracks the modules each
node's source imports and invalidates exactly the nodes that import the
edited one. Two traps follow:

- Import shared values from the module that defines them, never through
  the package. `from .layout import STATION_PITCH` is tracked;
  `from . import STATION_PITCH` re-exported by `__init__.py` is **not**, and
  editing the value will leave every artifact reporting up to date while
  the model is stale.
- A node's file imports its children's files and the constant modules it
  reads. It never imports a sibling's file for a number: that drags the
  sibling's source into its set, so editing either rebuilds both. If two
  nodes need the same number, it is a parameter on their common ancestor or
  a constant in a module.

## Parameters: master knobs, derived dimensions

A machine has few real degrees of freedom — a scale, a shaft nominal, a
gear module and tooth counts, a running clearance — and everything else is
derived. Declare each true knob **once, on the node that owns it**: a
machine-wide value on the root, a mechanism's own on the mechanism. Pass it
down to every child that needs it and derive every other dimension as a
formula where it is used:

- A mating dimension is a relationship (`bore = shaft_diameter + 2 *
  clearance`), never a second independent literal. A hand-computed default
  like `29.4` (really `30.0 - 2 * 0.3`) freezes the design at one point of
  its parameter space — turn the knob and its mates silently stop following.
- One number moves the whole machine: `solid build --set clearance=0.35`
  re-realizes every child that reads it and rebuilds exactly those
  artifacts. Anything the maker should be able to tune from the shell
  belongs on the root for that reason.
- The dimension algebra is your first test. `bore + pressure_angle` fails
  on `import`; a formula that type-checks is not therefore right, only
  dimensionally sane.
- Process constraints are the only genuinely absolute numbers, and they
  belong to the PRINTER, not the design: running clearance per side,
  minimum wall, minimum printable tooth module, bed envelope. They bound
  the validity envelope of the parameter space rather than scaling with
  it. Express each as `min=`/`max=` on the declaration or a `check()`
  guard that raises with its reason, and prove the guard in a test:
  construct the node outside the envelope inside `assertRaises`.

## Operations, placement, motion

`child.rotate(angle, [x, y, z])` and `child.translate([x, y, z])` append
operations that both the viewer and the test meshes honor, applied in
order. A child's own operations apply in its local frame before any parent
operation places it.

Two methods, two kinds of statement:

- **`render()` places at rest.** Where a part sits when nothing moves —
  a sleeve on its seat, a cap on its saddle, a unit at its station. It
  reads no driver, no `self.time`, no port, and the framework runs it once
  per instance, so each part carries exactly one rest placement for the
  life of the tree. Rotation before translation is the canonical order
  when a part carries both.
- **`simulate()` moves.** It runs after `render()` on every instant and is
  the one place to read `self.time`, a declared driver, or a port, and to
  bind a child's port. Every operation it applies is absolute for its
  instant, swept before the next run, and composed **inside** the rest
  placement: a crank rotated in `simulate()` and translated in `render()`
  spins about its own axis and is then carried to its seat. No wrapper
  assembly is needed to separate the two frames any more; no cleanup
  bookkeeping either.

```python
class Cylinders(AssemblyNode):

    units = CylinderUnit().repeat(len(CYLINDER_LAYOUT))

    def render(self):
        for index, unit in enumerate(self.units):
            station_x, bank = cylinder_placement(index)
            unit.rotate(bank, [1, 0, 0])
            unit.translate([station_x, 0, 0])

    def simulate(self):
        for index, unit in enumerate(self.units):
            unit.crank = crank_angle(self.time) + THROW_PHASES[index // 2]
```

- **Repeated units are driven through ports.** A unit declares `crank =
  RotationalPort(unit='deg')`, the parent feeds it in `simulate()` by
  assignment or `connect()`, and the unit reads `self.crank.value` in its
  own `simulate()` (the parent's runs first). A driver declared on a
  repeated or list-held child cannot be qualified; ports are the way.
  A port's `.value` is `None` until bound: treat that as a wiring fault to
  surface, not a zero to default.
- **Machine inputs are drivers**, declared on the assembly that owns the
  move: `angle = Driver(default=0.0, range=(0.0, 720.0), unit='deg')`,
  read as `self.angle` in `simulate()`. The viewer turns them into
  sliders and `instructions` into buttons at the layer that declares
  them, so declare a whole-machine move on the machine. `self.time` is
  one driver among them: `$t` from 0 through 1 on the timeline, a number
  in tests.
- Kinematic math imports from `solid_node.math` (`sin, cos, tan, asin,
  acos, atan, atan2, sqrt`), NEVER stdlib math: time and drivers are
  symbolic in the viewer, and these functions compute numerically on
  numbers while building the viewer's expression on symbols — one formula
  drives both. Trig is in DEGREES.
- A `FutureWarning` naming one of your classes means its `render()` read
  time, a driver or a port and is on the deprecated re-running path.
  Move the read and the operations it feeds into `simulate()` in the
  same slice; leave no warning in a class you touched, and report any you
  found in one you did not.
- An assembly may apply motion directly to a grandchild leaf — operations
  live on the node, and local-before-ancestor ordering keeps it correct.

`node.mesh` is the node's mesh in WORLD coordinates: its own operations
composed with every ancestor's, exactly the geometry the viewer shows.
Placing a sub-assembly by translating the wrapper is fine — its leaves'
meshes follow.

## Testing

Tests for `foo.py` live in `test_foo.py` beside it (for a package,
`test.py`); one class subclassing `solid_node.test.TestCase`. The
runner builds the node at time 0 and exposes it on the test as
`self.node` and as a snake_case alias of the test class name:
`SpurGearTest` gets `self.spur_gear`. Mesh assertions available:
`assertNoDisconnectedSolids`, `assertNoSolidInterference`,
`assertAssemblySupported`, `assertNotIntersecting`, `assertIntersecting`,
`assertInside`, `assertClose`, `assertFar`, `assertIntersectVolumeAbove`,
`assertIntersectVolumeBelow`, `assertBlockedBeyond`, `assertFreeWithin`,
`assertJoined` — all take nodes; `node.mesh` is a trimesh in world
coordinates. Between two exact nodes (CadQuery, build123d, sheet, molejo)
the intersection questions are answered by the kernel, not on triangles.

`assertNoPairwiseIntersections` is DEPRECATED — do not write it. It
walks leaf pairs and checks leaves, which stopped being the unit of a
printed part; `assertNoSolidInterference` replaces it. If you inherit a
project that calls it, replace the call rather than carrying it forward.
`assertOneBody`, `assertBodyCount`, and `assertNoDisconnectedParts` no
longer exist at all.

- Sweep the animation with `@testing_steps(n, start=..., end=...)` or pin
  an instant with `@testing_instant(t)`. Sweep only the period over which
  the geometry repeats (e.g. one tooth pitch), full cycle coarsely.
- Extra nodes needed inside a test: `n = SomeNode(bore=...)`,
  `n.assemble()`, `n.build_stls()`, then `n.mesh` works. A node created
  at another parameter value is how a test exercises the range.
- A driven machine is tested in motion with a `ScenarioTest`: declare
  `node`, `dt` and `meshes = True` when geometry is asserted, script
  `sim.at(t).trigger(...)` and `sim.every(period, assertion, ...)`, run a
  bounded slice, and write the run that must fail as well as the one that
  must pass — a scenario that only ever passes is not evidence.
- Perturbation tests (prove a part is blocked/free):
  `assertBlockedBeyond(node, amount, against)` — perturbed by
  ±amount, `node` must foul `against` in BOTH directions.
  `assertFreeWithin(node, amount, against)` — the anti-gaming twin:
  still clear within the play; `amount` may be a list for journal
  (freewheel) sweeps. Two modes: default is rotation (`amount` in
  degrees about `axis=`, about the node's own axis); pass
  `along=(x,y,z)` instead and `amount` is mm of translation — for
  linear fits (a pin captured in a bore, axial thrust float, a
  sleeve seated against a lip). Directions are LOCAL, pre-placement:
  placement rotations (own and ancestors') carry them, so one
  contract covers mirrored/banked instances. For deliberately
  one-sided constraints (blocked inward by a lip, free outward)
  pass `directions='forward'`. Both modes insert the perturbation
  before the node's placement and restore the operations exactly,
  pass or fail. Perturbation proves ENGAGEMENT; it does not pin
  dimensions — keep the parameter-anchored dimension checks
  alongside it.

Mesh measurement rules (STL vertices lie exactly on the true surface):

- Dimensional assertions: delta 0.01 is enough; no tessellation slack.
- Diameters: use max (or min) radial vertex distance from the axis,
  NEVER bounding boxes — with an odd feature count (e.g. 17 teeth) a
  tooth faces a gap and the bbox under-measures.
- Straight cylinders tessellate with vertices ONLY on their end rims.
  Measure gaps FROM the feature-rich mesh's vertices TO the other mesh's
  surface: `trimesh.proximity.closest_point(target_mesh, vertices)[1]`.
- Where two features butt-join in one plane (a pin's end rim on a web
  face), both features' vertices lie in that same plane — filtering by
  the coordinate along the joint axis cannot separate them. Select a
  feature's vertices by distance to its OWN axis instead.
- Centroid-style measurements (deriving a bore center from rim
  vertices) are biased by whatever the joining geometry removes from
  the rim: make the joint SYMMETRIC about the feature (a shank
  passing through both poles of a boss cancels exactly; one entering
  from a single side does not). Boolean re-tessellation adds ~0.1mm
  noise at cadquery's default tolerance — for centroid contracts,
  pre-tessellate in render(): `.mesh(tolerance=0.001,
  angularTolerance=0.01)` on the shape before returning it; the STL
  export reuses the finer triangulation. Finer tessellation cures
  bias only where the joining edges are simple curves (flat shank
  meeting a circular rim). Where two ROUND features intersect (a
  bore breaching a cylindrical OD), the join is a warped space curve
  tessellated independently on each side — the ~0.1-0.2mm asymmetry
  does NOT shrink with tolerance. Don't chase it: EXCLUDE vertices
  near the breach by coordinate and measure the geometrically clean
  region of the feature instead.
- OpenSCAD-family leaves (`Solid2Node`, `OpenScadNode`) approximate
  circles with `fn` segments; a hexagonal hole is tighter than the
  circle it stands for. Set `fn` high enough for the fit, or author the
  fit on an exact backend.

The unit both disciplines below work in is the PRINTED SOLID: the
topmost rigid node on each branch — a leaf, or a `FusionNode`, whose
parent is an assembly. The framework stops there and does not look
inside. Leaves fused into one solid are its ingredients, never compared
against each other and never individually required to be connected;
only the solid they make is. A flexible part (a spring, a belt) is never
a printed solid: it is bought, not printed, and it can never be fused.

Contract design principles:

- ADJACENCY DISCIPLINE: no two distinct solids may EVER share volume, at
  any instant — overlapping rigid bodies are physically impossible.
  Interference (press) fits are print-time compensation (printer
  profiles shrink holes); model them as small locational clearances.
  `assertIntersectVolume*` is for detecting contact, never for
  legitimizing overlap. `assertNoSolidInterference` admits no epsilon:
  exact zero-volume boundary contact passes and any positive shared
  volume fails, so a clearance is a length your drawing states, not a
  volume of interpenetration you tolerate.
- CONNECTIVITY DISCIPLINE, its twin, and never skip it: a printed solid
  is exactly ONE connected body. Adjacency discipline alone is a
  one-sided force — it pushes parts APART, and a part that has fallen
  into floating fragments satisfies every non-interference contract in
  the project. Nothing else reports it either: the build does not check
  it, and watertightness is a per-shell property, so a mesh of five
  disjoint closed shells is watertight, has positive volume, exports a
  valid STL, and renders in the viewer looking like a part. Features
  that must be one piece have to INTERPENETRATE by a stated weld
  (~0.5mm is a sound default); solids that abut tangentially, or that
  stop a couple of millimetres short of each other, stay separate
  bodies. `assertNoDisconnectedSolids(root)` catches every such part at
  once, reading each solid's own geometry with no placement composed. Add
  `assertJoined(a, b, min_weld_volume=...)` where the drawing names a
  junction — the one place two features are REQUIRED to share volume,
  and it holds only WITHIN one printed solid: hand it two features from
  different solids and it fails saying so, because that question is
  about the model, not the geometry. The classic generators: a feature
  located from a typed radius instead of from the surface it must land
  on, and a sub-feature placed in its own node so the gap never even
  looks like a gap.
- SUPPORT: parts that clear each other and hold together can still float.
  `assertAssemblySupported(root)` proves every printed solid rests,
  transitively, on something that reaches ground, and that the assembly
  balances under gravity on the contacts it detects. Use it wherever the
  drawing says the machine stands, hangs (`ground=`) or is bolted; declare
  press fits and glue in `supports=` so the exemption is visible in the
  test, and choose `max_drop` above the clearance play and below the
  thinnest supporting wall.
- A DRIVING PAIR must be shown to drive. Non-interference plus a ratio
  computed from tooth counts proves nothing — two gears a millimetre
  apart satisfy both, and so do two gears whose teeth sweep straight
  through each other. Engagement is a perturbation contract:
  `assertBlockedBeyond(driven, backlash_angle + margin, driver)`
  paired with `assertFreeWithin(driven, backlash_angle, driver)`. The
  driven member must foul its mate in BOTH directions just past the
  backlash and stay clear within it. Derive `backlash_angle` in the
  test from the drawing's linear backlash and pitch radius, never from
  the node. A pair also needs a PHASE relation — a tooth of one member
  sitting in a gap of the other — and the drawing owns it; without a
  phase term the two members turn at exactly the right speeds through
  each other. Teeth built as separate primitives are unioned to the
  blank and located from the blank's surface AT THAT STATION (the cone
  or cylinder radius where the tooth sits), which is connectivity
  discipline applied to the one feature most often typed by eye.
- Sample MESHING geometry over one tooth pitch, not over the animation
  cycle. `@testing_steps(3)` across a full cycle samples three
  arbitrary tooth phases and misses interference at every other one;
  it is not coverage for anything whose geometry repeats per tooth.
- A contract asserts GEOMETRY, not a claim about it. `assertTrue(
  part.is_open_topped)` and `assertEqual(part.foot_count, 6)` test
  that an attribute the node code sets still holds the value the node
  code set — they cannot fail for any reason a maker cares about.
  Metadata may LOCATE or PARAMETERIZE a measurement; the assertion
  itself measures the mesh.
- Every project root carries BOTH discipline safety nets, covering the
  adjacencies and the junctions nobody thought to test. Neither is
  optional and neither substitutes for the other: the first says
  parts stay out of each other, the second says each part holds
  together.

`solid new` writes both into the root test file, so a new project starts
with them:

```python
def test_solid_integrity(self):
    self.assertNoDisconnectedSolids(self.node)

def test_assembly_integrity(self):
    self.assertNoSolidInterference(self.node)
```

Neither is decoration and neither is optional. The framework checks
neither property on its own, so deleting one removes the project's only
structural net for it. A project that predates the scaffold, or one
whose root test file lacks them, gets them ADDED as your first act on
that project — before the slice you were assigned, since every later
contract is read against them. Replace any inherited
`assertNoPairwiseIntersections` call with `assertNoSolidInterference` at
the same time.

They are a floor, not a finished contract, and one of them is expected
to GROW. `test_solid_integrity` asks a question about geometry rather
than pose — a solid is connected or it is not, whatever the assembly
does with it — so one instant settles it and the scaffolded form is
already complete. `test_assembly_integrity` asks where the solids ARE,
which is exactly what the animation changes. As soon as the model moves,
sweep it:

```python
@testing_steps(8)          # a pose contract: one instant is one pose
def test_assembly_integrity(self):
    self.assertNoSolidInterference(self.node)
```

Two parts that clear each other at t=0 routinely collide mid-cycle, and
the single-instant form cannot see it. Sweeping is the intended
evolution of that test, not an edit to a contract you were told to leave
alone; interference checking is cheap (a spatial index, and a verdict
computed once per pair and relative placement per run), so sweep
generously and cover the whole cycle. Where a mechanism's geometry
repeats faster than the cycle — a gear train, a cam — the same rule as
any meshing contract applies: sample over one tooth or lobe pitch with
`start=`/`end=`, and cover the full cycle more coarsely alongside it. A
machine driven by more than the timeline gets the same check on a
scenario cadence, along the moves its instructions make.

What you may not do is weaken either one: no epsilon, no narrowing to a
subtree that skips the parts you just moved, no deletion because it went
red. A red integrity test is the net doing its job.

One honest limit: `test_assembly_integrity` passes vacuously while the
project is still a single leaf or fusion, since it selects fewer than
two solids and has nothing to compare. It is not evidence until the
model is an assembly — do not report it as coverage before then.

- Preconditions fail at construction, not in a mesh test (e.g. a gear
  pair refuses mismatched modules by building both gears from one
  declared `module`; a `check()` refuses a stop that cannot clear its
  stem).
- Non-interference alone is gameable (parts a meter apart pass). Pair
  every "does not collide" contract with the engagement contract that
  pins the part in place: blocked beyond the play, free within it.
- Bound clearances on BOTH sides, deriving bounds from the declared
  clearance, not magic numbers.
- One measured literal per physical gap: a single min-distance
  assertion spanning two independent gaps (a radial ring gap and an
  axial lip gap) is blind to either failing alone — the unaffected
  gap always wins the min(). If two things can fail independently,
  they are two contracts.
- Expected DIMENSIONS come from the design's INPUTS, through the test's
  OWN arithmetic — never read off a derivation at assert time. Tests may
  share the declared knobs (`self.node.clearance`, a layout constant);
  they must never share the implementation's DERIVATIONS: an expectation
  read from a derived parameter or a node attribute follows the very
  wiring bug it should catch and stays tautologically green. Live
  attributes may LOCATE a feature, never judge it. Editing a knob then
  moves model and tests together — that is the knob working, not a
  coverage hole; the bugs tests exist to catch live in NODE CODE (a
  parameter ignored, misapplied, sign-flipped, a formula done wrong), and
  those the shared-input test catches. The tautology trap still hides in
  two places: DERIVED play bounds (a blocked/free bound computed by
  reading the node's own formula moves with the bug it should catch — the
  test redoes the derivation itself, from the inputs) and MEASUREMENT
  FRAMES (a projection axis read live off the node, `unit.bank`, follows
  a wiring bug instead of catching it — axes and directions used to
  measure are computed in the test from the inputs too). Max-projection
  onto an axis is forgiving of axis errors near dead center (off-axis
  vertices compensate); anchor mid-stroke instants as well as TDC/BDC
  when the axis direction itself is under test. And check margins
  against the MEASURED bind angle — small-angle atan estimates undershoot
  the true corner-bind by a few tenths of a degree, more at larger
  clearance ratios.
- A parametric contract needs evidence at more than the default. Build a
  second instance at a boundary value inside the test, or run the file
  under `solid test --set knob=value`, and say which values you covered.
- `volume_epsilon` on `assertBlockedBeyond` / `assertFreeWithin`
  dismisses an intersection below the given volume. It exists because
  parts abutting exactly FLUSH (butt-jointed shaft segments) produce
  float-noise booleans on the faceted path. DO NOT REACH FOR IT. It is
  documented so you recognise it in a test you inherited, and the right
  response to finding one is to remove it: give the joint the clearance
  the drawing owes it, or weld the two features into one solid if they
  are one part, and the contract then holds at the default 0.0 with no
  threshold to argue about. Between exact parts it is ignored with a
  warning anyway. A tuned epsilon is a number nobody can derive from the
  design, and it hides exactly the small interferences worth catching.
  `assertNoSolidInterference` has no epsilon at all, by design.

## Definition of done — every component step

0. Work on the faceted kernel. Every `solid test` you run while
   building — the red run, the green run, the regression, the mutation
   check — is `solid test --faceted` (on the floor, `solid_test` with
   `kernel="faceted"`). It decides the same assertions on the parts'
   meshes, about twenty times faster on exact parts and thirty on
   springs and belts, and it labels its own output. Only the last step
   below runs exact.
1. Write the test file first; run it; watch it fail.
2. Implement to green.
3. Full regression: run `solid test` for EVERY node file in the project
   (a failing run exits nonzero, so chaining files with `&&` works),
   including the root, whose two integrity contracts are what catch a
   part you broke somewhere else. If you redirect a chained run's output
   to one log file, only the last command's output survives — redirect
   per file (or just run them as separate foreground invocations) when
   you'll inspect logs.
4. Mutation check: break the geometry contract IN NODE CODE (wrong
   phase, a dropped clearance term, a misapplied parameter...), confirm
   the specific contract tests fail, revert, confirm green. Changing a
   declared knob's value is inert BY DESIGN — tests share those inputs
   and follow the knob — so mutate the formula or the code that USES
   the parameter, not the parameter. The mutation must FLOW: mutating a
   child's default is inert when the parent passes the value
   explicitly — mutate at the level the value actually comes from. And
   it must EXCEED the margin that actually bounds the error: identify
   which physical gap or play the mutation eats into, and size the
   mutation past it (a 3mm station shift survives a 4mm axial gap;
   4.5mm kills). If a mutation unexpectedly survives, investigate and
   report which contract truly bounds that error instead of shrugging.
   Also note which tests are structurally blind to a mutation class
   (e.g. a ratio check built on abs() can never catch a sign flip) —
   say so rather than counting them as coverage.
5. Wire the component into the root assembly. A component that does not
   change the model the maker sees is not done. You run no server;
   verify from a finite build:

       solid build

   It exits nonzero if the build fails, and on success publishes the
   whole current model into the build directory (`_build` by default,
   an ordinary directory). Read `viewer.json` there: walk from `root`
   down to the new component, confirm each `operations` entry holds the
   expected rotation/translation (symbolic `$t` or a qualified driver id
   for animated ones), confirm every rigid leaf's `model` file exists,
   and, for a driven machine, that its `drivers` table lists the ids you
   declared.

   A build rebuilds only what its source tracking says is stale, and a
   current leaf is not rendered at all. If a build seems to ignore an
   edit you just made, you have found a tracking hole, not a caching
   nicety: you are reaching a value through the package `__init__.py`,
   or through something a static import walk cannot see. Fix the import
   rather than deleting the build directory and moving on.
6. LOOK at the result — a correct build tree does not mean the model
   looks right, and the user judges pixels. Render and read images:

       solid snapshot -o out.png --autocenter --time 0.1

   Render at least an isometric view and one view along the axis that
   the new component's alignments live on, and inspect them before
   declaring done. Keep the default renderer; `--renderer web` is for a
   host that needs a transparent background (and needs the separately
   installed viewer package), not for your inspection. A driven machine
   snapshots at its driver defaults; pose it through `--time` only. Do
   not try to see a defect a snapshot cannot resolve: a gear pair that
   never touches, or a blade stopping 3mm short of its hub, is what the
   connectivity and engagement contracts are for — they fail
   deterministically, at any scale, without a framing guess. Snapshots
   answer whether the component is wired and posed as intended.
7. The exact run, once, at the end. Repeat the full regression of step
   3 on the exact kernel — `solid test --exact` (`kernel="exact"`) for
   every node file including the root — and only that run certifies the
   contracts and evidences the commit: a summary line that ends in
   `(faceted kernel, ...)` is not evidence. When the two kernels
   disagree the exact verdict stands. A faceted failure the exact run
   clears is a clearance thinner than the 0.1 mm tessellation reading
   as overlap on meshes; a faceted pass the exact run fails is a thin
   real interference the meshes missed. Either way fix the model or the
   contract, and never reach for a volume epsilon to make the two agree.
8. A broken save is not private. A failed build exits nonzero and
   writes `errors.json` into the build directory; what it leaves beside
   it may be a partially updated model, not the last good one — never
   read a snapshot taken after a failed build as evidence for the edit
   you just made. The shop watches project sources and runs the same
   build itself, whoever saved, and reports the failure to the maker:
   leave the tree building green, and rebuild after fixing an error
   rather than assuming the next save heals it. Leave no `FutureWarning`
   in the build output for a class you touched.

## Public API

The complete supported surface is in the separately loaded
`solid-node-api` skill, and it is the only description of the framework
you have — its source is not available to you. If the skill is
unavailable, stop and report the packaging gap. If it is loaded but
silent on something you need, report that gap too: an interface guessed
from a name or reconstructed from a traceback is not a supported
interface, and a project built on one breaks at the next release.
