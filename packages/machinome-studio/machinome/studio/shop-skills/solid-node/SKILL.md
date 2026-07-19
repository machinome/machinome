---
name: solid-node
description: Build and test parametric mechanical components in a solid-node project. Use when creating or modifying nodes (parts, assemblies), writing mesh contract tests, animating assemblies, or wiring components into the web viewer. solid-node treats mechanical parts as software — parametric interfaces, unit tests, integration contracts verified on meshes.
---

# Building solid-node components

solid-node is a Python framework for parametric, 3D-printable mechanical
projects. A project is a package (conventionally `root/`) whose nodes form a
tree: leaf nodes produce geometry through a CAD backend, assembly nodes
compose and animate children. Mechanical contracts (parts mesh, fit, clear,
transmit torque) are expressed as tests over the rendered meshes.

Commands (run from the project directory, with the project's venv):

    solid develop root          # build + watch + web viewer on :8000
    solid test root/<node>.py   # run tests for one node (passing the
                                # test_*.py path works too)

Read `../solid-node-api/SKILL.md` in full before building unless it is already
loaded. It is the authoritative public surface. This manual owns implementation
craft: parameter flow, placement, contract tests, measurement, and the
definition of done. Use public interfaces in project code. If a machinist role
permits framework-source inspection, keep it narrow and diagnostic; source does
not enlarge the supported API.

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

A file with exactly one node class needs nothing extra; a file defining
several must name the main one with a module attribute after the class
definitions — `NODE = MyAssembly` — or the loader fails loudly.

Children are named automatically after the attribute their parent holds
them under (`self.input_gear` → `input_gear`; members of a list
attribute get `attr-N`), so the viewer tree and test vocabulary agree.
An explicit `name=` kwarg overrides; names never affect build
artifacts, which stay parameter-keyed.

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

Tests for `root/foo.py` live in `root/test_foo.py` (for a package,
`root/test.py`); one class subclassing `solid_node.test.TestCase`. The
runner builds the node at time 0 and exposes it on the test as a
snake_case alias of the test class name: `SpurGearTest` gets
`self.spur_gear`. Mesh assertions available: `assertNotIntersecting`,
`assertIntersecting`, `assertInside`, `assertClose`, `assertFar`,
`assertIntersectVolumeAbove`, `assertIntersectVolumeBelow`,
`assertBlockedBeyond`, `assertFreeWithin`,
`assertNoPairwiseIntersections` — all take nodes; `node.mesh` is a
trimesh in world coordinates.

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

Contract design principles:

- ADJACENCY DISCIPLINE: no two distinct parts may EVER share volume, at
  any instant — overlapping rigid bodies are physically impossible.
  Interference (press) fits are print-time compensation (printer
  profiles shrink holes); model them as small locational clearances.
  `assertIntersectVolume*` is for detecting contact, never for
  legitimizing overlap.
- Every project root gets the discipline safety net — one test that
  walks the assembled tree and asserts pairwise non-intersection over
  sampled instants, covering any adjacency nobody thought to test:

```python
@testing_steps(4)   # scale instants down (3) past ~20 leaves: cost is
def test_no_two_parts_intersect(self):   # pairs x instants booleans
    self.assertNoPairwiseIntersections(self.root_node)
```

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
- Parts that legitimately abut FLUSH (butt-jointed shaft segments)
  produce float-noise boolean intersections that read as
  interference: pass `volume_epsilon=1e-6` to
  `assertNoPairwiseIntersections` / `assertBlockedBeyond` /
  `assertFreeWithin` — noise sits orders below real engagement
  volumes, so the threshold is unambiguous. Default 0.0 keeps strict
  is_empty semantics; don't pass epsilon where nothing abuts flush.

## Definition of done — every component step

1. Write the test file first; run it; watch it fail.
2. Implement to green.
3. Full regression: run `solid test` for EVERY node file in the project
   (a failing run exits nonzero, so chaining files with `&&` works).
   If you redirect a chained run's output to one log file, only the
   last command's output survives — redirect per file (or just run
   them as separate foreground invocations) when you'll inspect logs.
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
   change the model in the running viewer is not done. Verify over HTTP:
   `curl http://localhost:8000/node/` lists children; walk the
   paths (`/node/<Child>/.../<Leaf>.stl` returns 200; assembly JSON
   shows the expected operations, symbolic `$t` for animated ones).
6. LOOK at the result — endpoints being correct does not mean the model
   looks right, and the user judges pixels. Render and read images:

       solid snapshot root -o out.png --autocenter --time 0.1

   Render at least an isometric view and one view along the axis that
   the new component's alignments live on, and inspect them before
   declaring done.
7. A broken save no longer kills `solid develop`: import errors surface
   at `/_build_error` and the next clean save recovers automatically.
   While an error is up the viewer serves the last good model — check
   `/_build_error` returns `{}` before judging what the user sees. A
   DEAD backend is visible too: the browser shows a red banner and
   heals itself when the server comes back.

## Public API

The complete supported surface is in the separately loaded
`solid-node-api` skill. If it is unavailable, stop and report the packaging
gap rather than rediscovering the API from framework implementation.
