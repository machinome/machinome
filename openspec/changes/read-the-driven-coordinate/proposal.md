## Why

A running law says how far a coordinate moves for its sources' movement.
Every law the framework admits today is a function of coordinates OTHER
than the one it drives, because ADR-100 gave a coordinate named on both
sides of one relation no meaning and refused it at class definition. That
covers every mechanism the campaign has met so far — until a mechanism's
engagement depends on where the driven part itself stands.

The originating project is `projects/Calculators/Curta-Type-I-3x`, branch
`direct-operation`, checkpoint `b285393`, and the requirement is recorded
whole in `workflow/docs/curta-retained-angle-clearing.md`. The Curta is
cleared by sweeping a ring that carries two nine-tooth racks past the
register dials. A rack turns a dial only while its teeth reach it AND the
dial is not already standing at its missing-tooth zero: nine teeth, one
gap, and the gap is what lets the ring go on sweeping past a dial that has
finished while it still clears the dials beyond it. Releasing the ring
part way keeps the partial clearing; resuming continues from there;
sweeping an already-zero dial does not turn it again. The dial's own
retained angle decides whether the rack moves it, so **the law that moves
the dial has to read where the dial stands.**

The project's executable diagnostic is
`simulation/tools/direct_operation_probe.py` in that repository. Its
clearing fixture is refused before a run exists:

```text
TypeError: wheel.rotation is named as both a source and a driven end of one relation:
a coordinate is a source or a driven end of one relation, not both.
```

Three routes through the model as it stands were measured on this
worktree, and each fails in its own way
(`evidence.md` §1; spikes under the change's own record):

- **A declared range on the dial stops the RING.** A wheel declaring
  `range=(None, 360)` driven from a `ring` input by `move('ring', by=500)`
  commits the wheel at `360`, retires the ring's command `blocked` with
  `360.0` of `500` admitted, and records a stop naming `('ring',)`. A
  `Bound(..., reads=(ring,))` gives the same answer to a ulp. That is
  ADR-108 working exactly as designed and exactly against the mechanism:
  the missing tooth frees the ring, it does not hold it.
- **A gate recomputed from the ring's own travel loses the dial's
  history.** `ring.drives(wheel.turn, law=...)` over `90 * clamp01((ring -
  100) / 90)` runs the wheel to `90` on the first sweep, back to `0` when
  the ring is returned, and to `90` again on the second — a dial that
  un-clears itself and then repeats its former contribution, which is
  requirement items 2 and 3 failing together. Every dial reachable by the
  same rack gets the same contribution whatever digit it stood at.
- **A duplicated coordinate carrying the previous angle does not solve.**
  `wheel.turn.drives(shadow.turn)` plus `(ring & shadow.turn).drives(
  wheel.turn, law=...)` raises `UnreachedCoordinate: wheel.turn drives
  shadow.turn: nothing bound either end` — a cycle with no side to be read
  from, refused at the close of the enumeration.

**Deleting the refusal is not an implementation, and that too is
measured.** With `_refuse_shared_coordinate` monkeypatched out and the
Kahn ordering made to ignore the self-edge, the fixture compiles, the
program's listing names the read, and the tick is WRONG in silence: a
`500`-degree rack sweep from a dial standing at `108` leaves the dial at
`608` and a second sweep leaves it at `1108`, with no crossing located at
all. The run evaluated `f(end) − f(start)` with the driven coordinate at
the same value at both ends, so the gate was frozen open for the whole
tick and the dial never disengaged (`evidence.md` §2).

The program cannot express this because a relation's law depends on its
OWN driven coordinate — a cycle of length one. Reading ANOTHER banked
coordinate through a jump is already legal and already exact: the `Clutch`
fixture's `-2 * shaft * (sleeve > 0.5)` is a source-gated clutch whose
crossing is located inside the tick, and the Pascaline's carry reads the
column below it. The one thing missing is the self-read, and it is exactly
the retained-angle gate.

## What Changes

- **A coordinate named as a source AND as the driven end of one relation
  is a READ of that relation's own driven end.** The refusal
  `_refuse_shared_coordinate` becomes the recognition point. The law is
  handed that coordinate's owner exactly as it is handed any source's, so
  `(rack & wheel.turn).drives(wheel.turn, law=f)` calls `f(rack, wheel)`
  written as it is written today. The read is the value the coordinate
  HOLDS, never a value the same relation is about to give it.
- **A read must be a SWITCH, never a factor.** With every jump node of the
  law replaced by its branch — the SKELETON the jump plan already builds —
  the law must no longer name the driven coordinate. A read that survives
  the skeleton enters the law continuously, which makes the relation a
  differential equation that `f(end) − f(start)` does not define, and it
  is refused at construction by relation identity. `%` alone is not a
  switch: `a % b` leaves `a − q·b`, which still carries the coordinate's
  slope.
- **A self-read law is integrated PIECE BY PIECE, the branch decided from
  the retained value.** ADR-107's partition is built first over the jump
  nodes that do NOT depend on the driven coordinate, unchanged, branches
  read at its midpoints; inside each of its pieces the nodes that DO
  depend on it are WALKED. Their branches are read at the piece's LEFT
  END — the driven coordinate at the value it retains there, every other
  source at that same fraction, because a level naming both can cross
  inside the piece by the source's motion alone. With the branches fixed
  the driven coordinate's own path is a known function of the fraction;
  the level quantities are followed along it and the piece is cut at the
  first surface any of them reaches — solved where that level is affine
  along the path, searched otherwise, on the three tolerances that
  already exist — and the next piece is decided the same way. A law with
  no self-read takes ADR-107's path with nothing rebuilt at all.
- **After a cut the driven coordinate is committed AT THE FAR SIDE of the
  surface, at the nearest representable value** — ADR-108's "committed AT
  its bound exactly" transposed to a surface that is not stated in the
  coordinate's own units. The segment's arithmetic finds the landing and
  the landing is walked to the adjacent float, with no tolerance
  anywhere; the run commits THAT float rather than `value + delta`, the
  way it already commits a stop at its bound. Measured over the real
  classes: without it, 6.3 % of crossings leave the gate ENGAGED and
  another 12.7 % are refused as `TooManyCrossings`; with it, 200 000
  randomized crossings hold, in both directions, at every gap width
  (`evidence.md` §7). The design states the obligation this puts on the
  model: a gate's DISENGAGED state must have WIDTH — the mechanism's own
  clearance, a band about the zero entered from either side — because a
  gate whose disengaged set is a single point cannot hold when the
  coordinate arrives from the engaged side.
- **A self-read relation binds nothing at rest.** Under a running root it
  is recorded solved forward without applying its law, the driven
  coordinate's rest value is the author's own rest-default guard, and
  construction refuses by name when there is none — the refusal the run
  already makes for a joint coordinate the rest render leaves unbound.
  Under any other time base the relation is refused by name at the close
  of the enumeration rather than standing silently inert: it states
  increments, which only a run integrates.
- **The self-read is a `needs` of the compiled edge that is also one of its
  `gives`**, and the Kahn ordering ignores a need an edge itself gives. So
  the published rule that an edge's expressions read exactly the ids in
  `needs` stays true, and a consumer identifies the self-read as
  `needs ∩ gives` with no new document key.
- **BREAKING for consumers: a document whose program carries a self-read
  edge is a version 6 document.** A version 5 consumer would evaluate
  `f(end) − f(start)` with the read at both ends and move the part wrongly
  in silence, so ADR-057's rule gives such a document the version its
  content needs. A document with no self-read stays byte-identical at 5.
  The browser viewer executes it in its own cycle in its own repository;
  this cycle's conformance corpus is that cycle's contract.
- A self-read crossing is **not a stop**: it stops no input, retires no
  command, and records as a `Crossing`.
- **A self-read relation drives ONE coordinate.** A driven GROUP one of
  whose members the source group names — itself or a sibling — is refused
  at class definition by name. A BROADCAST is admitted, because each copy
  is its own record with one driven end reading itself.

## Capabilities

### New Capabilities

None. The change gives a meaning to a sentence three existing
capabilities already refuse.

### Modified Capabilities

- `couplings`: "A relation may name several coordinates at each end" — a
  coordinate named on both sides of one relation is no longer refused; it
  is a read of the driven end, drives exactly ONE coordinate, and is
  refused where the driven end is a group. "Each end of a relation
  resolves…" gains the one exception to the broadcast-source refusal: the
  broadcast the same relation drives.
- `simulation`: "A jump is located inside the tick and subtracted" (the
  two-layer partition and the retained-value branch) and "A running root's
  simulation owns every driver and joint coordinate" (the rest rule), plus
  ONE ADDED requirement, "A law may read the coordinate it drives", which
  states the recognition, the refusals, the walk, the landing and the
  width obligation in one place.
- `export`: "A running root's document publishes the compiled program" and
  "The two runtimes share a conformance corpus" — version 6 for a program
  that carries a self-read edge, and corpus coverage of one.

## Impact

- `solid_node/motion/couplings.py`: `_refuse_shared_coordinate` becomes
  recognition; `_step_relation` gains the rest rule; `_refuse` gains the
  non-running refusal.
- `solid_node/simulation/program.py`: `_relation_edge` records the
  self-read and its two refusals; `Edge` carries it; `JumpPlan` gains the
  two-layer partition, the retained-value branch reading and the far-side
  landing; `_ordered`
  and `_reaching_inputs` ignore a self-need; `Program.published` emits
  version 6 for a self-read edge.
- `solid_node/simulation/run.py`: `_pass` carries an edge's reported
  LANDINGS the way it already carries its crossings, `integrate` applies
  them where it already commits a stop at its bound, and `_locate`'s
  `edge.cuts` path follows the same partition.
- `solid_node/core/serializer.py`: the version ladder.
- `tests/running_project/`, `tests/clearing_project/`,
  `tests/running-corpus.json`, `tools/generate_running_corpus.py`,
  `docs/scenarios.rst`, `HISTORY.rst`.
- One ADR, **ADR-121** (NODE), extracted after implementation.

### Non-goals

- **Executing a version 6 document in the browser.** `solid-node-viewer`
  is a separate repository with its own OpenSpec records; its cycle is
  held to the corpus this cycle regenerates. Requirement item 8's replay
  through the independent viewer is therefore discharged there, and this
  cycle records the producer-side content commit.
- **Migrating the Curta.** Requirement item 9 is project work in the
  project's own repository. What it needs from this cycle is stated in
  design.md §12: a rest default on every dial's `rotation`, and the
  clearing law rewritten from `cleared_position`'s pose form to a rack
  term gated by the dial's own retained angle.
- **A continuous read.** A law in which the driven coordinate carries
  slope is an ODE and is refused, not integrated.
- **A new declaration.** No `reads=` keyword on `drives`, no `engaged=`,
  no rest-value declaration on a joint: design.md §1 and §5 record why
  each was rejected.
- **A driven GROUP with a self-read.** `Edge.increments` walks one plan
  per driven end, and a member reading a sibling needs that sibling's
  path while the sibling's own walk is cutting it — a joint walk over
  several plans that no mechanism in the campaign has asked for. Refused
  by name here and recorded as a follow-up (design.md §1, tasks 9.1).
- **`a.drives(a)`, one to one.** ADR-100 declined to widen the refusal to
  it and this cycle does not either; it still deadlocks into
  `UnreachedCoordinate` (measured, `evidence.md` §1).
- **The pushing test at `t*`.** ADR-113's recorded limit (the test is net
  over the stretch) is untouched.
