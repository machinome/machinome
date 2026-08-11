---
name: solid-node
description: Build and test parametric mechanical components in a solid-node project. Use when creating or modifying nodes (parts, assemblies), writing mesh contract tests, animating assemblies, or wiring components into the web viewer. solid-node treats mechanical parts as software — parametric interfaces, unit tests, integration contracts verified on meshes.
---

# Building solid-node components

solid-node is a Python framework for parametric, 3D-printable mechanical
projects. A project is a package — `solid new snowman` scaffolds
`snowman/snowman/`, with the root node in `snowman.py` beside an empty
`__init__.py`, and `pyproject.toml` naming it under `[tool.solid-node]`. Its
nodes form a tree: leaf nodes produce geometry through a CAD backend, assembly
nodes compose and animate children. Mechanical contracts (parts mesh, fit,
clear, transmit torque) are expressed as tests over the rendered meshes.

Commands (run from the project directory, with the project's venv):

    solid build                 # build once and publish the model
    solid test <pkg>/<node>.py  # run tests for one node (passing the
                                # test_*.py path works too)
    solid snapshot -o out.png --autocenter   # render an image

Commands take an optional node reference — `package.module:Class`,
`path/to/file.py`, or `path/to/file.py:Class`. Omit it and the project's
model from `[tool.solid-node]` in `pyproject.toml` is used. A directory is
not a reference.

`solid develop` also exists, and serves a live viewer that rebuilds on save.
Do not run it here: the shop already watches the project, rebuilds it, and
keeps the maker's view current. Your builds are verification of your own work,
and they are finite.

Read `../solid-node-api/SKILL.md` in full before building unless it is already
loaded. It is the authoritative public surface, and it is all you have:
framework source is not available to you. This manual owns implementation
craft: parameter flow, placement, contract tests, measurement, and the
definition of done. If the API skill does not describe the behavior you need,
report the gap — never infer an interface from a name or a traceback.

## Writing nodes

Leaf nodes subclass a backend adapter: `CadQueryNode`, `Solid2Node`,
`OpenScadNode`, or `JScadNode` (all from `solid_node.node`). Rules:

- Store every parameter as an attribute AND pass them all as kwargs to
  `super().__init__()` — the kwargs key the build artifacts, so two
  instances with different parameters never share a stale STL.
- Every parameter needs a sensible default: the test runner instantiates
  the node class with NO arguments.
- `render()` returns the backend's native object (a cadquery Workplane, a
  solid2 object, ...).

```python
class Shaft(CadQueryNode):
    def __init__(self, diameter=4.8, length=30.0, flat_h=1.0, name=None):
        self.diameter = diameter
        self.length = length
        self.flat_h = flat_h
        super().__init__(diameter=diameter, length=length, flat_h=flat_h,
                         name=name)

    def render(self):
        ...return a cq.Workplane...
```

Assembly nodes subclass `AssemblyNode`; `render()` returns a list of
children. Children must be PERSISTENT: create them in `__init__` as
instance attributes. Never create children inside `render()` (render runs
once per keyframe; identity must persist), and never as class attributes
(a second instantiation would re-apply their placement operations).

A leaf's `render()` may return several solids and nothing checks that
they touch. If they are one printed part, union them with real
overlap; if they are not, they are separate nodes. A backend "union"
of solids that do not overlap does not fail — it hands back a
compound, which exports as one file holding several loose pieces.

Children are named automatically after the attribute their parent holds
them under (`self.input_gear` → `input_gear`; members of a list
attribute get `attr-N`), so the viewer tree and test vocabulary agree.
An explicit `name=` kwarg overrides; names never affect build
artifacts, which stay parameter-keyed.

## One node per file

Put exactly one node class in each file. This is the framework's premise, not
a filing preference: a node's artifacts are keyed to the file it lives in, so
editing one file rebuilds one node, and the invalidation aggregates upward
through the assemblies that contain it and nowhere sideways.

Two nodes in one file share one mtime. Editing either rebuilds both, plus
every assembly above either of them — permanently, at leaf tessellation cost,
which is the expensive part of a build. A multi-node file also loses the bare
path reference: `solid build root/parts.py` and `solid snapshot root/parts.py`
fail as ambiguous, since there is no way to declare a main class. Only
`solid test` tolerates it, and it then runs every node in the file.

So: one class per file, named after it. Shared values live in a module that
defines **no** node — the conventional `parameters.py` or `kinematics.py`. The
framework tracks the modules each node's source imports and invalidates
exactly the nodes that import the edited one.

Two traps follow from how that tracking works:

- Import shared values from the module that defines them, never through the
  package. `from .parameters import D_SHAFT` is tracked;
  `from . import D_SHAFT` re-exported by `__init__.py` is **not**, and editing
  the value will leave every artifact reporting up to date while the model is
  stale.
- Never import one node's file from another node's file. That drags the
  sibling's source into your node's set, so editing either rebuilds both —
  the exact coupling this discipline removes. If two nodes need the same
  number, it belongs in the parameter module.

When you inherit a file holding several nodes, split it: one class per file,
imports pointed at the parameter module, companion test files renamed to match.
Until it is split, every `TestCase` in its companion file must declare
`node = TheClass`, or the run fails listing the candidates.

## Parameters: master knobs, derived dimensions

A project has few real degrees of freedom — a scale, a shaft nominal,
a gear module and tooth counts, a clearance — and everything else is
derived. Keep the true knobs in ONE module (conventionally
`root/parameters.py`); derive every other dimension from them in code,
where it is used:

- Node defaults read the parameter module (`diameter=params.D_SHAFT`);
  a mating dimension is a relationship (`bore = params.D_SHAFT +
  2 * params.CLEARANCE`), never a second independent literal. A
  hand-computed default like `29.4` (really `30.0 - 2*0.3`) freezes
  the design at one point of its parameter space — turn any knob and
  its mates silently stop following.
- Process constraints are the only genuinely absolute numbers, and
  they belong to the PRINTER, not the design: running clearance per
  side, minimum wall, minimum printable tooth module, bed envelope.
  Keep them in the parameter module too. They do NOT scale with the
  model — they bound the validity envelope of the parameter space,
  and each deserves a guard test that reddens, with its reason, when
  a parameter change leaves the envelope.

## Operations, placement, animation

`child.rotate(angle, [x, y, z])` and `child.translate([x, y, z])` append
operations that both the viewer and the test meshes honor, applied in
order. A child's own operations apply in its local frame before any parent
operation places it, so "rotate around own axis, then translate into
place" is the natural order.

- Static placement: apply ONCE, in the assembly's `__init__`.
- Time-dependent (kinematic) operations: apply in `render()` from
  `self.time` (0..1 over the animation cycle — the symbolic `$t` in the
  viewer, numeric under `set_keyframe()` in tests). Renders are
  IDEMPOTENT: before an assembly re-renders, every node its previous
  render touched is restored to its pre-render operations. So render()
  simply states the absolute kinematics of its instant — no cleanup
  bookkeeping.
- Kinematic math imports from `solid_node.math` (`sin, cos, tan,
  asin, acos, atan, atan2, sqrt`), NEVER stdlib math: `self.time` is
  symbolic in the viewer, and these functions compute numerically on
  numbers while building the viewer's `$t` expression on symbols —
  one formula drives both. Trig is in DEGREES.
- `set_keyframe()` propagates down the tree: nested assemblies and
  their children render numerically in tests too.
- An assembly may apply kinematic operations directly to a grandchild
  leaf — operations live on the node, and local-before-ancestor
  ordering keeps the motion correct.
- A part that is both placed somewhere and spins about its own axis
  needs its rotation BEFORE its translation in the operations list:
  either apply both in `render()` (rotate, then translate), or wrap
  the part in a sub-assembly — place the wrapper statically, rotate
  the leaf in `render()`.

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
`assertNotIntersecting`, `assertIntersecting`, `assertInside`,
`assertClose`, `assertFar`, `assertIntersectVolumeAbove`,
`assertIntersectVolumeBelow`, `assertBlockedBeyond`, `assertFreeWithin`,
`assertJoined` — all take nodes; `node.mesh` is a trimesh in world
coordinates.

`assertNoPairwiseIntersections` is DEPRECATED — do not write it. It
walks leaf pairs and checks leaves, which stopped being the unit of a
printed part; `assertNoSolidInterference` replaces it. If you inherit a
project that calls it, replace the call rather than carrying it forward.
`assertOneBody`, `assertBodyCount`, and `assertNoDisconnectedParts` no
longer exist at all.

- Sweep the animation with `@testing_steps(n, start=..., end=...)` or pin
  an instant with `@testing_instant(t)`. Sweep only the period over which
  the geometry repeats (e.g. one tooth pitch), full cycle coarsely.
- Extra nodes needed inside a test: `n = SomeNode(params)`,
  `n.assemble()`, `n.build_stls()`, then `n.mesh` works.
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
- `mesh.contains(points)` needs `rtree`; `trimesh.proximity` needs
  `scipy`. Neither is pulled in by solid-node — add both to the project
  requirements.

The unit both disciplines below work in is the PRINTED SOLID: the
topmost rigid node on each branch — a leaf, or a `FusionNode`, whose
parent is an assembly. The framework stops there and does not look
inside. Leaves fused into one solid are its ingredients, never compared
against each other and never individually required to be connected;
only the solid they make is.

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
  once, reading each solid's own STL with no placement composed. Add
  `assertJoined(a, b, min_weld_volume=...)` where the drawing names a
  junction — the one place two solids are REQUIRED to share volume,
  and it holds only WITHIN one printed solid: hand it two features from
  different solids and it fails saying so, because that question is
  about the model, not the geometry. The classic generators: a feature
  located from a typed radius instead of from the surface it must land
  on, and a sub-feature placed in its own node so the gap never even
  looks like a gap.
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
alone; interference checking is cheap (a spatial index, milliseconds on
a model of ~125 solids), so sweep generously and cover the whole cycle.
Where a mechanism's geometry repeats faster than the cycle — a gear
train, a cam — the same rule as any meshing contract applies: sample
over one tooth or lobe pitch with `start=`/`end=`, and cover the full
cycle more coarsely alongside it.

What you may not do is weaken either one: no epsilon, no narrowing to a
subtree that skips the parts you just moved, no deletion because it went
red. A red integrity test is the net doing its job.

One honest limit: `test_assembly_integrity` passes vacuously while the
project is still a single leaf or fusion, since it selects fewer than
two solids and has nothing to compare. It is not evidence until the
model is an assembly — do not report it as coverage before then.

- Preconditions fail at construction, not in a mesh test (e.g. a gear
  pair refuses mismatched modules by building both gears from one).
- Non-interference alone is gameable (parts a meter apart pass). Pair
  every "does not collide" contract with the engagement contract that
  pins the part in place: blocked beyond the play, free within it.
- Bound clearances on BOTH sides, deriving bounds from the clearance
  constant in the parameter module, not magic numbers.
- One measured literal per physical gap: a single min-distance
  assertion spanning two independent gaps (a radial ring gap and an
  axial lip gap) is blind to either failing alone — the unaffected
  gap always wins the min(). If two things can fail independently,
  they are two contracts.
- Expected DIMENSIONS come from the parameter module, through the
  test's OWN arithmetic — never read off the node at assert time.
  Tests may share the design's INPUTS (`params.TOWER_HEIGHT`); they
  must never share the implementation's DERIVATIONS: an expectation
  read from a node attribute follows the very wiring bug it should
  catch and stays tautologically green. Live attributes may LOCATE a
  feature, never judge it. Editing a parameter then moves model and
  tests together — that is the knob working, not a coverage hole;
  the bugs tests exist to catch live in NODE CODE (a parameter
  ignored, misapplied, sign-flipped, a derivation done wrong), and
  those the shared-input test catches. The tautology trap still
  hides in two places: DERIVED play bounds (a blocked/free bound
  computed by calling the node's own formula moves with the bug it
  should catch — the test redoes the derivation itself, from the
  parameters) and MEASUREMENT FRAMES (a projection axis read live
  off the node, `unit.bank`, follows a wiring bug instead of
  catching it — axes and directions used to measure are computed in
  the test from the parameters too). Max-projection onto an axis is
  forgiving of axis errors near dead center (off-axis vertices
  compensate); anchor mid-stroke instants as well as TDC/BDC when
  the axis direction itself is under test. And check margins against
  the MEASURED bind angle — small-angle atan estimates undershoot
  the true corner-bind by a few tenths of a degree, more at larger
  clearance ratios.
- `volume_epsilon` on `assertBlockedBeyond` / `assertFreeWithin`
  dismisses an intersection below the given volume. It exists because
  parts abutting exactly FLUSH (butt-jointed shaft segments) produce
  float-noise booleans that read as interference. DO NOT REACH FOR IT.
  It is documented so you recognise it in a test you inherited, and the
  right response to finding one is to remove it: give the joint the
  clearance the drawing owes it, or weld the two features into one
  solid if they are one part, and the contract then holds at the
  default 0.0 with no threshold to argue about. A tuned epsilon is a
  number nobody can derive from the design, and it hides exactly the
  small interferences worth catching.
  `assertNoSolidInterference` has no epsilon at all, by design.

## Definition of done — every component step

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
   the specific contract tests fail, revert, confirm green. Editing the
   parameter module is inert BY DESIGN — tests share those inputs and
   follow the knob — so mutate the code that USES the parameter, not
   the parameter. The mutation must FLOW: mutating a child's default is
   inert when the parent passes the value explicitly — mutate at the
   level the value actually comes from. And it must EXCEED the margin
   that actually bounds the error: identify which physical gap or play
   the mutation eats into, and size the mutation past it (a 3mm station
   shift survives a 4mm axial gap; 4.5mm kills). If a mutation
   unexpectedly survives, investigate and report which contract truly
   bounds that error instead of shrugging. Also note which tests are
   structurally blind to a mutation class (e.g. a ratio check built on
   abs() can never catch a sign flip) — say so rather than counting
   them as coverage.
5. Wire the component into the root assembly. A component that does not
   change the model the maker sees is not done. You run no server;
   verify from a finite build:

       solid build

   It exits nonzero if the build fails, and on success publishes the
   whole current model. Read `viewer.json` in the build directory
   (`_build` by default, a symlink to the current publication — always
   go through the link, never a resolved versioned path): walk from
   `root` down to the new component, confirm each `operations` entry
   holds the expected rotation/translation (symbolic `$t` for animated
   ones), and confirm every rigid leaf's `model` file exists.

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
   host that needs a transparent background, not for your inspection. Do not try to see a defect a snapshot cannot
   resolve: a gear pair that never touches, or a blade stopping 3mm
   short of its hub, is what the connectivity and engagement contracts
   are for — they fail deterministically, at any scale, without a
   framing guess. Snapshots answer whether the component is wired and
   posed as intended.
7. A broken save is not private. A failed build exits nonzero and
   writes `errors.json` into the build directory instead of publishing;
   the previous publication keeps serving, so the maker goes on seeing
   the older model — never read a stale snapshot as evidence for the
   edit you just made. The shop watches project sources and runs the
   same build itself, whoever saved, and reports the failure to the
   maker: leave the tree building green, and rebuild after fixing an
   error rather than assuming the next save heals it.

## Public API

The complete supported surface is in the separately loaded
`solid-node-api` skill, and it is the only description of the framework
you have — its source is not available to you. If the skill is
unavailable, stop and report the packaging gap. If it is loaded but
silent on something you need, report that gap too: an interface guessed
from a name or reconstructed from a traceback is not a supported
interface, and a project built on one breaks at the next release.
