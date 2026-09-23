# Mates and sketches: placing parts by relation instead of by coordinate

**Status: provisional direction, 2026-09-23.** Nothing here is ratified and
no OpenSpec change has been cut from it. It records an assessment the pilot
asked for after reading about MakerCAD
(<https://github.com/marcuswu/makercad>): how the way mainstream CAD builds
parts and assemblies — constrained sketches, mate connectors, joints between
them, skeleton layouts — could come into machinome, and whether it should.
It does *not* claim that any spelling below exists, that the layering is
settled, or that any project has been migrated. Where it disagrees with a
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

### 5.1 Named frames on parts

A part declares its connectors once, in its own frame, as class-body
declarations whose components may be formulas over its parameters. They add
no solid and no build identity (the `Marking` precedent: a thing a part
carries). They work for every backend, STL and OpenSCAD imports included,
because they are declared, not picked from B-rep faces — which is what
Onshape's mate connectors are anyway.

### 5.2 Mates that compile to what already exists

In a tree-shaped assembly — most machines — "put `link.hole` on
`base.pivot`, free about their common z" needs no solver. It is transform
algebra: the child's rest placement is the parent frame composed with the
inverse of the child frame, and the leftover freedom is an existing joint
whose axis and `at` are that frame's. A mate therefore **compiles into rest
placement plus an ADR-093/094/095 joint**, symbolically. The document, the
viewer, contracts and the running and clocked machinery see nothing new.
A candidate spelling, for discussion only:

```python
class Base(CadQueryNode):
    pivot = Frame(at=(0, 0, height), z=(0, 1, 0))

class Link(CadQueryNode):
    hole = Frame(at=(0, 0, 0), z=(0, 0, 1))

class Arm(AssemblyNode):
    base = Base()
    link = Link()
    hinge = Revolute.between(base.pivot, link.hole)   # places AND articulates
```

Coordinates do not disappear: they move into the one place they are local
and obvious, and are written once. This layer answers every item of §4
except the hand-closed loops, and is expected to carry most of the value.

Questions a proposal would have to settle: whether a mate may coexist with
a hand-written `translate` on the same child (probably refused, so a
placement is stated once); what a rigid mate is called (`Fixed`?); how a
mate states a site-level conditional placement like Inmoov's; how a frame on
a `.repeat()` copy is addressed; and whether frames are published in the
document so the viewer can draw and pick them.

### 5.3 A solver for closed loops

A skeleton or a set of mates that closes a loop — a four-bar, a
slider-crank, a delta, a Peaucellier — needs a solver. This is an
architecture decision, because the viewer evaluates closed-form expressions
at frame rate in the browser and a run-time numeric solve breaks that
unless something else changes. Options, none chosen:

- solve numerically in Python and publish a table or a fitted law;
- run a solver compiled to WebAssembly in the viewer (a viewer change, in
  its own repository);
- keep growing the closed-form helper library loop shape by loop shape.

Open solvers exist (SolveSpace's, FreeCAD's planegcs, FreeCAD's Assembly
solver), so the mathematics need not be invented. The pilot's call; a
natural neighbour of 0.9 dynamics on the roadmap.

### 5.4 Constrained part sketches

Left to the backends. A machinome sketch solver feeding build123d is
possible but duplicates backend work, and machinome's distinct job is the
machine, not the part. Revisit only if a project's parts genuinely suffer
from it.

## 6. What would start a cycle

Under the evidence rule, none of §5 is proposed until a named project needs
it now.

- **§5.1 + §5.2, one change.** Originating project: a catalogue machine
  whose placement already bled coordinates — Inmoov-sim, YouCanBuildDog or
  AlbertPro are candidates. Validation: re-place that machine with mates,
  delete its hand-written offsets and callables, and compare poses at
  maximum deviation 0 against the current tree, the way the ADR-097 survey
  did.
- **§5.3.** Originating project: a linkage machine that wants its loop
  closed rather than derived — a second flexure stage, or a new Foundry
  machine built around a four-bar or slider-crank.
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
