# Mates and sketches: placing parts by relation instead of by coordinate

**Status: provisional direction, 2026-09-23.** Nothing here is ratified and
no OpenSpec change has been cut from it. It records an assessment the pilot
asked for after reading about MakerCAD
(<https://github.com/marcuswu/makercad>): how the way mainstream CAD builds
parts and assemblies — constrained sketches, mate connectors, joints between
them, skeleton layouts — could come into machinome, and whether it should.
It does *not* claim that any spelling below exists, that the layering is
settled, or that any project has been migrated. On 2026-09-23 §5 was
revised from a direction with one candidate spelling into a proposed
interface — frames, mates, loops and the document shape — and §6's
candidates were re-read against it; that revision is still a proposal in
a note, not a ratified interface. One point is the pilot's
settled direction (2026-09-23), not a proposal: every solve happens at
compile time and the viewer solves nothing, while still receiving the mates
so it can represent them (§5.3, §5.5). Where it disagrees with a
baseline spec or an accepted ADR, the spec and the ADR are right and this
note is stale. Under the evidence rule, no cycle is cut from it until a named
project needs that cycle now (§6).

---

## 1. The gap

Every placement in machinome is a coordinate. A parent's `render()` places a
child with `translate`/`rotate` and numbers; a joint's `axis=`, `at=` and
`carries=` are numbers (ADR-097 reads them in the declarer's own frame, which
made them local, not relational); a closed kinematic loop is a law a person
derives and writes as a formula. Nothing lets an author say *this bore's
axis* or *flush with that face* and have the framework compute the numbers.

This is the interface of OpenSCAD. It is not the interface most makers
learned on. Fusion, Onshape, SolidWorks and FreeCAD all place and articulate
parts by relation, and a maker arriving from any of them brings that model
with them. The framework's author came to machinome without it, which is
how the coordinate interface became the only one.

## 2. What mainstream CAD does, in three separate ideas

They are distinct and have different value here; they must not be merged
into one proposal.

1. **Constrained part sketches.** A rough 2D profile is drawn on a plane or
   a face, then related — horizontal, equal, tangent, coincident, a distance
   from an edge — and a solver computes the coordinates. Features (extrude,
   revolve, cut, fillet) are built from the solved sketch. Design intent is
   stated as relations, never computed by hand; one dimension changes and
   everything depending on it follows. MakerCAD is this idea in Go over
   OCCT, with its own solver (`dlineate`).
2. **Mates, or joints, between named frames.** Each part carries named
   reference frames on its own geometry — Onshape's *mate connectors*,
   Fusion's *joint origins*. An assembly relates two such frames: "this
   shaft end in that bore, free to turn" is a revolute mate. **The same
   statement places the part and declares its freedom.** The freedoms the
   mates leave open are the machine's motion; dragging a part moves it as
   the mates allow.
3. **Skeleton, or layout, sketches.** A mechanism is first drawn as a stick
   figure — links as lines, pivots as points, lengths as dimensions — and
   dragged: the solver keeps every loop closed. Parts are then built on the
   skeleton. A four-bar or a slider-crank never has its law derived by hand.

## 3. Where machinome stands against each

- **Idea 2 is half there.** `Revolute`, `Prismatic`, `Orbit` and `Free` are
  Fusion's joint vocabulary, declared on the body that moves. ADR-097's frame
  rule — a joint is stated in its declarer's own frame — is the first half of
  a mate connector: the coordinates already live with the part. The missing
  half is naming them, and letting an assembly relate two named frames
  instead of restating the placement in numbers.
- **Idea 3 is absent.** Closed loops are hand-derived laws: the kinematics
  helpers (ADR-076), the `Follow` law, inverse kinematics inverted by hand.
- **Idea 1 belongs to the backends.** build123d and CadQuery build 2D
  profiles; CadQuery has an experimental constrained `Sketch`, and
  `cq.Assembly.constrain(...)`/`solve()` is a numeric mate solver for static
  placement already inside a dependency. machinome's parameter algebra
  states design intent as one-way formulas (derived parameters), not as
  solved constraints.

## 4. Evidence already on record

Every item is a coordinate stated in two places that drifted, or a loop
closed by hand. All are in `workflow/warts.md`.

- **Restated placements, measured.** The `joint-frame-follows-declarer`
  survey (`openspec/changes/archive/2026-09-10-joint-frame-follows-declarer`,
  `evidence/survey.md`): 23 projects, 249 class-body joint declarations, 69
  of them restating their parent's placement as `at`, plus about 30
  hand-written rotations. ADR-097 removed the restatement for joints; the
  rest placement itself is still a coordinate, and the joint line and the
  placement are still two statements.
- **A joint line silently wrong for one branch of a placement.** Inmoov-sim
  stage B (2026-09-10): the wrist `Bolt`'s site joint, written as plain
  numbers, was right with `presented=False` and wrong under the project's
  own default — 622 mm³ of palm/axle interference at rest, 14.2 mm at full
  wrist travel, no refusal. The fix was a callable re-deriving the
  placement. A mate would have been one statement, right in both branches.
- **One pivot shared by five placements.** YouCanBuildDog: five bodies per
  leg, five rest placements, one knee pivot, which had to be named by hand
  so that `Orbit`'s `carries` agreed with all five.
- **Offsets found only by measurement.** Don1: the blueprint nests each foot
  11.5 mm short of the thigh's knee shaft.
- **Loops closed by hand.** The hexapod's inverse kinematics hand-invert
  `R_roll · R_pitch · R_yaw · T_height`; the openflexure four-bar
  decomposition (`leg_lean`, `lever_rise`) is deferred as a mechanism law
  waiting for a second flexure stage (ADR-076 open question).

This is evidence of a class of friction, not a requirement. §6 says what
turns it into one.

## 5. Direction, cheapest layer first

**Interface proposal, 2026-09-23.** §5 was first written as a direction
with one candidate spelling. It is now the interface the pilot asked for,
worked out against the joint ADRs (088, 093, 094, 095, 097, 098), the
marking precedent (ADR-120), the relation and broadcast rules (ADR-089,
ADR-096), the control rule (ADR-117), the document version ladder, the
mechanics helpers as released, and three projects read for their placement
code: Inmoov-sim, YouCanBuildDog and the strandbeest. It is a proposal in a
design note, not a spelling that exists; a cycle cut from it re-checks
every rule here against its originating project's evidence. The pilot's two
directions (§5.3, §5.5) are kept as written and are not proposals.

### 5.1 Named frames on parts

A part declares its connectors once, in its own frame, as class-body
declarations:

```python
from machinome.node.frames import Frame

class Base(CadQueryNode):
    height = Length(40.0)
    pivot = Frame(at=(0, 0, height), z=(0, 1, 0))   # a line through a point
    foot  = Frame()                                  # the part's own origin and axes

class Link(CadQueryNode):
    span = Length(40.0)
    hole = Frame(z=(0, 0, 1))                        # at the origin
    knee = Frame(at=(span, 0, 0), z=(0, 0, 1))

class Bolt(StepNode):                                # catalogue hardware
    length = Length(20.0)
    shank = Frame(z=(1, 0, 0))
```

- **Signature.** `Frame(at=(0, 0, 0), z=(0, 0, 1), x=None)`. `z` is the
  line a revolute turns about or a prismatic slides along. `x` matters
  only to a rigid mate and, when omitted, follows the rule `Wrapped`
  already uses for `zero` — the next principal axis in right-hand order —
  refused for a diagonal `z` naming `x` as the remedy. `y` is `z × x`.
  Vectors need not be unit: `z` is normalized and `x` squared up against
  it, exactly as Inmoov-sim's project-local `Frame`
  (`Inmoov_sim/frames.py`) does today.
- **Components** follow the joint rule (ADR-088): a number, a
  declared-parameter token, a formula over them, or — for the whole
  argument — a callable of the realized node.
- **Frame of reference.** The declarer's own rest frame, ADR-097's rule,
  and the framework transforms nothing.
- **Where.** On any node kind — a leaf adapter, a fusion, and an
  *assembly*, because an assembly's connectors are its interface to the
  assembly above it (the hand's wrist, a leg's hip). This is the one place
  the `Marking` precedent is not followed: a marking is refused on an
  assembly because it is drawn on a surface; a frame is drawn on nothing.
- **What it is, and is not.** A fifth kind of class-body declaration in
  the `Marking` mould (ADR-120): not a solid, not a child, not build
  identity, not a port, not a descriptor. Collected in `NodeMeta.__new__`,
  duck-typed on a `frame_kind` attribute; inherited through the MRO;
  allowed in a plain mixin; dropped by a subclass assigning
  `pivot = None`; a name clashing with a parameter, a child, a port, a
  joint coordinate, a marking or an attribute every node carries is refused
  at class creation; enumerated by `declared_frames(cls)`.
- **Repeated frames.** A parent that carries one connector per copy of a
  repeated child declares
  `pivots = Frame(at=lambda base, index: ..., z=(0, 1, 0)).repeat(4)`. A
  repeated frame's callable takes the node and the copy index, and is
  resolved when the parent places its children — after every copy exists —
  so the `.repeat()` `index` trap ADR-098 records for joint arguments does
  not arise.

### 5.2 Mates that compile to what already exists

In a tree-shaped assembly — most machines — "put `link.hole` on
`base.pivot`, free about their common z" needs no solver. It is transform
algebra, and the leftover freedom is an existing joint.

```python
class Arm(AssemblyNode):
    base = Base()
    link = Link()
    cap  = Cap()
    hinge = link.hole.on(base.pivot, Revolute(range=(-90, 90), unit='deg'))
    lid   = cap.bottom.on(link.knee)                 # rigid: no coordinate
```

**The sentence.** `<moving frame>.on(<fixed frame>, <freedom>)`, written in
the assembly's class body. This replaces the earlier candidate
`Revolute.between(base.pivot, link.hole)` for one reason: the frame that
speaks is the one that moves, exactly as `a.drives(b)` says what turns
what, so a reader never has to remember an argument order. Rigid is the
default, so the base sentence is placement and the freedom is the
addition. Either frame is named as a relation's end is named: a frame the
class body's own children declare, or a path through declared children
(`arm.link.hole`), validated at class definition by the `PathRef` rules; a
list-held child is refused as it is for relations.

**The freedom** is a joint written with no `axis` and no `at`, because the
two frames supply both: `Revolute(range=, unit=)`,
`Prismatic(range=, unit=)`, `Free(angle_unit=, length_unit=)`. `Orbit` is
not a mate freedom: its geometry needs a third point, and every `Orbit` in
the catalogue that a mate would replace — YouCanBuildDog's twenty `carry`
joints, the cycloidal disks — is one body of a parallelogram or an
eccentric, which is a loop (§5.3). The one signature change is that a
joint's `axis` becomes optional; a class-body or site joint written
without one is refused naming the mate as the only place it is allowed.

**What a mate compiles to** — three things the framework has:

1. **A rest placement** on the assembly's own child at the top of the
   moving path, as ordinary `rotate` and `translate` operations, as if
   written in `render()`: the moving child's matrix is the fixed frame's
   owner placement, composed with the fixed frame, composed with the
   inverse of the moving frame. Mates resolve in dependency order, fixed
   side first; a child neither mated nor hand-placed rests at the identity
   as today.
2. **A joint on the moving child**, in ADR-097's class form, with the
   moving frame's `z` as `axis` and its `at` as anchor, copied literally:
   the frame is already in the child's own frame, so nothing is inverted
   and the churn ADR-098 accepted for site joints is not repeated. It
   occupies a slot after the child's class-declared joints, by ADR-098's
   rule, so a wheel with its own `spin` mated on an axle spins on its
   bearing and rests where the mate put it.
3. **A coordinate on the assembly** under the mate's name, wired down to
   that joint through the existing wiring path (ADR-088). `arm.hinge`
   therefore binds and reads as a joint's coordinate, `declared_ports(Arm)`
   reports it, and relations, drivers, `Bound` reads, controls (ADR-117),
   the running and the clocked machinery see nothing new. A rigid mate
   declares no coordinate; reading `arm.lid` yields the declaration.

**Rules the proposal fixes**, answering the questions the first draft of
this section left open:

- *A mate and a hand-written placement on one child.* Refused by name: a
  `translate`/`rotate` applied in `render()` to a child a mate places names
  the mate. A placement is stated once.
- *A second mate on a placed child* is not refused: it is a loop (§5.3),
  and until §5.3 exists the build refuses it naming both mates.
- *The rigid mate* is the default of `on()` and needs no class; its
  document kind is `fixed`.
- *Symbolic frames.* A symbolic `at` publishes as a symbolic translation,
  exactly as a formula in `render()` does. A symbolic axis is refused in
  the first cycle, naming the frame: the document carries only `rotate`
  and `translate` operations, and a symbolic axis-angle derived from a
  symbolic matrix is not a thing to publish.
- *Broadcast.* A moving path through a `.repeat()` is a broadcast
  (ADR-096): one mate per copy, in copy order, the fixed side either one
  frame or a repeated frame of the same count, a count mismatch refused by
  name. A repeated fixed side with a single moving side is refused.
- *Site-level conditional placement.* Inmoov's wrist stops needing a
  callable on the joint. The hand becomes a sub-assembly mated onto a
  forearm frame, and `present()` is either that frame being conditional in
  one place — `Frame(z=lambda forearm: ...)`, reading the same `presented`
  flag `render()` reads — or one rigid mate of the whole group onto the
  viewer's frame. The wrist bolt is `axle.shank.on(clevis.ear, Revolute())`
  with no arithmetic at all, once `Bolt` carries a `shank` frame and the
  clevis an `ear`.
- *Range and `Bound`.* Unchanged: both come from the joint passed to the
  mate, and a `Bound`'s reads resolve against the assembly that declares
  the mate.

Coordinates do not disappear: they move into the one place they are local
and obvious, and are written once. This layer answers every item of §4
except the hand-closed loops, and is expected to carry most of the value.

### 5.3 A solver for closed loops

A skeleton or a set of mates that closes a loop — a four-bar, a
slider-crank, a delta, a Peaucellier — needs a solver.

**Pilot direction, 2026-09-23: every solve happens at compile time, never
in the viewer.** Solving is expensive; the viewer receives an optimal
application — closed-form laws it evaluates at frame rate, as it does
today — and no solver ships to the browser. The viewer does receive the
mates themselves, as declarations, so it can represent them (§5.5); it
never solves them. A run-time solver in the viewer, WebAssembly or
otherwise, is rejected.

**Proposed interface.** The mates of an assembly form a graph over its
children. A tree compiles as §5.2 says. A cycle is a loop, closed at build
time under the direction above. The interface adds one keyword and no new
declaration:

- **Inputs and solved coordinates.** The mate coordinates something binds
  — a driver, a relation, a wiring — are the loop's inputs; every other
  mate coordinate in the loop is solved per pose. Too few or too many
  bound coordinates against the loop's mobility is refused at simulation
  construction, naming the loop and the coordinates, the way
  `UnreachedCoordinate` and `DoublyBound` already name theirs.
- **Branch.** `rest=` on the joint passed to the mate —
  `Revolute(rest=35)` — is the solved coordinate's approximate value at
  the machine's rest pose, defaulting to zero. The compiler solves the
  exact rest pose from that guess once and holds the branch (a four-bar's
  assembly mode) for every pose after. Dead points, lock-up and the range
  over which the loop closes at all are found at build time and published
  as the joint's range — never discovered by a viewer that cannot close
  the loop.
- **Symbolic closure where it exists.** A loop the compiler can name emits
  the closed form as an ordinary law — the one law every consumer
  evaluates, the Python run included, so the viewer and a test cannot
  disagree. The catalogue of named loops is the mechanics package as it
  stands: four parallel revolutes are `four_bar_pose`; a revolute crank
  and a prismatic slider are `crank_rod_angle` and `piston_height`; two
  links reaching a bound point are `two_link_angles`; three carriages
  under a `Free` platform are `delta_carriage`. Each helper already
  carries the branch sign the `rest=` guess selects.
- **A sampled law where it does not.** Solve numerically over the input's
  range at build time and publish a table or a fitted curve the viewer
  interpolates. The cost grows with the number of inputs a loop has, so a
  multi-input loop wants its closed form, or its inverse kinematics,
  rather than a table. The sampling resolution and the residual tolerance
  are build knobs whose spelling waits for the cycle.

The strandbeest is the measure of this layer. Today every `LinkPlate` and
`TrianglePlate` carries `turn`, `x` and `y`, and `strandbeest/leg.py`
states ten hand-written laws over two `four_bar_pose` closures and three
circle intersections. With mates each plate declares frames on its bores,
the leg declares revolute mates between them, and those ten laws are what
the compiler derives.

Open solvers exist (SolveSpace's, FreeCAD's planegcs, FreeCAD's Assembly
solver) and are candidates for the build-time side only, so the mathematics
need not be invented. A natural neighbour of 0.9 dynamics on the roadmap.

### 5.4 Constrained part sketches

Left to the backends. A machinome sketch solver feeding build123d is
possible but duplicates backend work, and machinome's distinct job is the
machine, not the part. Revisit only if a project's parts genuinely suffer
from it.

### 5.5 The viewer knows the mates, and solves nothing

Pilot direction, 2026-09-23. The published document carries each frame and
each mate — which two frames, what kind, which freedom it leaves — beside
the compiled placement and laws, so the viewer can represent them: draw a
connector, show what a part is mated to, highlight the freedom a drag will
move. The mates are information for representation; the compiled laws are
what moves the model. That is a new document version and a viewer change,
one change in each repository, cut alongside whichever of §5.2 or §5.3
first publishes a mate.

**Proposed document shape.** A node entry gains an additive `frames` list,
one entry per declared frame — `{name, at, x, y, z}` in the node's own
frame, components published as operations are, symbolic where the
declaration is. An assembly entry gains an additive `mates` list —
`{name, kind: fixed|revolute|prismatic|free, fixed: "base.pivot",
moving: "link.hole", coordinate: "hinge" | null, solved: bool}` — frames
and coordinates named by the qualified ids the bindings table uses. Both
follow the `markings` precedent (ADR-120): additive, absent when none is
declared, a document with none byte-identical to before.

One point for the pilot to decide against the direction above, which
expected a new version: the proposal argues that frames and mates alone
move **no** version, because the compiled placement is already in
`operations`, so a version 13 consumer renders the right picture and only
lacks the connector drawing; the viewer cycle declares the fields it
draws. What does move the version is §5.3's sampled law, by the ladder's
own rule — an expression kind a consumer cannot evaluate would render a
wrong pose, which is exactly why `bindings` bumped (ADR-080).

## 6. What would start a cycle

Under the evidence rule, none of §5 is proposed until a named project needs
it now. The candidates were re-read on 2026-09-23 against the interface
above.

- **§5.1 + §5.2, one change.** Originating project: **Inmoov-sim** is the
  clean candidate. Its frames already exist as project code — `Frame`,
  `FRAMES`, `STATIONS`, `WRIST` and `PRESENTATION`, each placed by
  `rotation()` plus a `translate`, and the wrist axle's `_presented`
  callable — so the migration is a port rather than a redesign, and it
  exercises the assembly-level frame, the conditional frame and the
  catalogue-hardware frame in one machine. AlbertPro remains a candidate.
  **YouCanBuildDog is reclassified**: its legs are parallelograms, and
  every one of its thirty-three restated pivots (thirteen `turn` and
  twenty `carry` joints, each re-typing a chassis pivot and a knee pivot
  from `layout.py`) comes from that loop, so it is a §5.3 machine and a
  §5.2 migration alone would keep every `Orbit`. Validation: re-place the
  machine with frames and mates, delete its hand-written offsets and
  callables, and compare poses at maximum deviation 0 against the current
  tree, the way the ADR-097 survey did.
- **§5.3.** Originating project: the **strandbeest** — six rigid parts
  per leg, two four-bar closures, three circle intersections, ten
  hand-written laws — is the named candidate, and YouCanBuildDog's
  parallelogram the trivial second, a four-bar with equal parallel links.
  A second flexure stage or a new Foundry machine built around a linkage
  would do as well.
- **§5.4.** Real demand only.

## 7. MakerCAD itself

MakerCAD is an MIT-licensed Go library, early (no releases, one maintainer,
about 140 stars in September 2026). It sits in the same layer as CadQuery
and build123d — the geometry of one part — with no assemblies or motion. It
is a possible backend, not a competitor, and no project uses it. A program
written in it can already enter a model today by writing STEP for
`StepNode`; a dedicated adapter would be modelled on `JScadNode` over
`ExactLeafNode` and waits for a project that needs one. Its lasting value to
machinome is the reminder in §2, idea 1.
