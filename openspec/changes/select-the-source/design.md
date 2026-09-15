## Context

`proposal.md` states the requirement, the reproduction and the three
routes the note rejects. This document answers the eight design
questions the requirement note leaves open — recognition, evaluation,
rest and initialization, stops and constraints, retention, composition
with ADR-121, publication, and cost — and records the alternatives
rejected for each, with the measurement that rejected them.

The ground it stands on is unchanged and is not re-argued here:

- **ADR-105** — the run owns every driver and joint coordinate, binds
  them through `set_state`, and inspecting a model advances nothing.
  Memory lives on real banked coordinates, nowhere else.
- **ADR-106** — a law is compiled ONCE, in the direction the rest render
  solved it, contributes `f(end) − f(start)` over a tick, and the edges
  are ordered by Kahn over the ends they determine. **This cycle amends
  that last clause and nothing else of it.**
- **ADR-107** — a law that jumps contributes the CONTINUOUS part of its
  change: the path is cut at every crossing, a branch is read at each
  piece's midpoint, and the pieces are summed. A jump never moves a part.
- **ADR-108/109/113** — a declared range is a physical stop that stops
  what pushes; a bound may be an expression over the coordinate's own
  value; a bound may read other coordinates and is then sampled along the
  stretch over a SUB-PROGRAM, so the sample arithmetic is the segment
  arithmetic.
- **ADR-110/111** — Python and the browser execute one published
  program, and a conformance corpus is the contract between them.
- **ADR-121** — a law may read the coordinate it drives, through a
  SWITCH, walked in two layers inside each of ADR-107's pieces.
- **ADR-057** — a producer emits the LOWEST version its content needs.

Five facts about the code as it stands are load-bearing below and were
MEASURED on this worktree rather than read. The scripts are under the
change's own `spikes/` directory; each is quoted where it is used.

1. **The refusal is `_ordered` and nothing else** (`program.py:2966`).
   It is Kahn over the ends each edge determines, over the union of every
   edge's `needs`, with a need an edge itself gives ignored (ADR-121's
   self-read). `spikes/reduced.py` reproduces the note's message verbatim
   on this tree.
2. **Without a self-read the cycle never reaches the compile at all.**
   The same three relations with no self-read term are refused by the
   REST RENDER: `DoublyBound: higher.turn would be bound by the relation
   (crank, shift, carry.travel) drives higher.turn and by the author's
   simulate()` where the driven ends carry rest guards, and
   `UnreachedCoordinate: (crank, shift, carry.travel) drives higher.turn:
   waiting for carry.travel` where they do not (`spikes/reduced.py`,
   classes `NoSelfRead` and `Unguarded`). **This decides §5**: membership
   must be known BEFORE the rest render.
3. **The records exist, with resolved ends, before the rest render.**
   `spikes/membership.py` walks `_units(root)` over a freshly
   constructed tree — nothing rendered, nothing bound — and prints all
   three records with their resolved driven SLOT IDENTITIES and
   `direction=None`. So the pre-pass of §5 has everything it needs.
4. **The fold is computable and says what §1 needs it to say.**
   `spikes/fold.py` drives `_law_graphs`/`_plan_of` on the fixture and
   folds the skeleton with one placeholder at zero. Quoted in §2.
5. **Piece-by-piece composition is exact.** `spikes/pieces.py` calls a
   member edge's own `increments` over three pieces of one stretch with
   the in-block coordinate advanced between them; the increments sum to
   the whole-stretch answer, the landing is the same float, and the
   crossing rescales to the same fraction. Quoted in §3. Its landing
   falls in the SECOND piece and the third piece's increment is `0.0`, so
   it does NOT settle what the block reports when a landing is followed
   by further motion; §3 states that rule separately and task 4.7 pins
   it.

And one fact about the SPECS, verified: **the cycle refusal is specified
nowhere.** `grep -rn cycle openspec/specs/` finds no requirement and no
scenario about it, and `grep -rn 'form a cycle' tests/` finds no test.
It exists only as the message in `_ordered` and one sentence in
`docs/architecture.md`. This cycle therefore SPECIFIES it for the first
time, in the requirement that owns the compile step, and adds the test
that pins it.

## Goals / Non-Goals

**Goals**

- One persistent run admits a machine whose dependencies are SELECTED by
  a live input, changes between selections inside a tick, and keeps every
  part's history on that part.
- The seven acceptance items of the requirement note follow from the run,
  not from project bookkeeping.
- Nothing about a program with no block changes: not its meaning, not
  its code path, not its cost, not its document, not one byte of the
  corpus.
- What the reading cannot support is refused — at construction by
  relation identity where the shape is wrong, at run time
  TRANSACTIONALLY where a particular selection is genuinely cyclic.

**Non-Goals** — as `proposal.md` lists them: viewer execution, the
Curta's own migration, a coupled solver, a new spelling, frozen reads or
an accepted declaration order, untimed posing, a block member driving a
group, and ADR-113's net-over-the-stretch pushing test.

## Decisions

### 1. Spelling: the selection is the comparison the model already writes

**Decision.** Nothing is declared. A selection is a jump node already in
a law, and a switched source is a source that a folded branch removes.
The Curta's association is written as it is written in the project
today:

```python
CARRIAGE = 20.0                  # degrees of carriage per working position

def advanced(place):
    """Dial `place` is advanced by lever k whenever the carriage has
    brought it under that lever -- and by the crank, and by its own
    clearing rack, in the same law."""
    def factory(sources, target):
        def law(crank, seat, clearing, *levers_then_own):
            levers, own = levers_then_own[:-1], levers_then_own[-1]
            here = seat / CARRIAGE
            total = crank + clearing * missing_tooth(own)
            for k, lever in enumerate(levers):
                aligned = (here >= place - k - .5) * (here < place - k + .5)
                total = total + STEP * aligned * (lever >= SET)
            return total
        return law
    return factory

(crank & seat.turn & clearing & levers.travel & dial.turn).drives(
    dial.turn, law=advanced(place))
```

`seat.turn` stands for the carriage's own JOINT coordinate, which the
project already wires from its `position` driver as
`position.drives(registers.turn, ratio=20)`
(`simulation/mechanism.py:186`). The sketch is illustrative — the
project's own migration is §12 — and its point is only this: the
selector reads a JOINT COORDINATE, not the driver.
A selector therefore reads a coordinate an UPSTREAM EDGE determines
rather than an input, and the design must work for that case. It does,
because the rule is "not given by the block", and an upstream edge's
give is not.

**Alternatives rejected.**

- **A `Selected(position, {0: lower.turn, 1: higher.turn})` source
  end.** Rejected on three counts. It is a NEW COORDINATE KIND, with a
  resolution path, a rest rule, a publication and a refusal set of its
  own, for something the expression language already says. It needs a
  "no member" answer for the carriage between detents and for the LIFTED
  carriage, which is a second selection over the first. And it does not
  cover the DRIVEN side at all: a dial is advanced by whichever lever
  faces it, so the dial's law must name EVERY lever and gate each — the
  one multi-source law ADR-105's shape asks for — and a source-end
  selector says nothing about that.
- **`drives(..., when=...)`, or any relation-level condition.**
  Rejected for ADR-121's own reason, which applies here with more force:
  the gate belongs to a TERM of a multi-source law, not to the relation.
  A Curta dial is driven by the crank UNCONDITIONALLY, by its own
  clearing rack through a retained-angle gate, and by a carry lever only
  when the carriage aligns them — three terms of one law with three
  different conditions. A relation-level `when=` would force three
  relations into one driven coordinate, which the solver refuses as
  doubly bound.
- **A new verb.** Rejected for ADR-089's reason: one verb states
  mechanical direction.
- **A coupled solver, or a fixed point per piece.** Rejected for
  ADR-121's reason: it introduces a convergence tolerance — a fourth
  tolerance — and a per-piece iteration count, into a design whose claim
  is three tolerances and no epsilon anyone has to justify. A block is
  ORDERED on each piece, and a piece that cannot be ordered is refused
  by name rather than iterated toward.
- **Removing the cycle detection, freezing reads for a tick, or taking
  the declaration order.** The note names all three as supplying no
  semantics, and `spikes/arbitrary.py` measures what the last one
  actually does: the carry loses a tick under declaration order and never
  happens at all under the reverse, silently, with the same ground truth
  available one specialization away (`proposal.md`'s table).

**The cost of the choice, stated.** A reader cannot tell from a class
body that two relations form a block; the selection is visible only in
the laws' terms. Four places name it: the program's `described()`
listing (and therefore the identity), the run-time refusal when a piece
cannot be ordered, the document's version 7, and the documentation.

**The shape, stated.** A block member drives exactly ONE coordinate. A
relation in a block whose driven end is a GROUP is REFUSED at
construction, naming the relation and the block, because the fold of §2
is computed per driven end off THAT end's own skeleton while a group's
ends are claimed and bound TOGETHER — a group one of whose ends is
switched and another not would have to be split, and no mechanism in the
campaign has asked for one. Recorded as a follow-up.

### 2. Recognition: blocks, selectors, switched sources

**The union dependency graph.** Over the compiled candidate edges: edge
A precedes edge B when B `needs` a key A `gives`, with a need an edge
itself gives EXCLUDED (that is ADR-121's self-read, which is not a wait
on anything else). Its nontrivial strongly connected components are the
**BLOCKS**. Everything outside a block is what it is today.

Note what the definition already gives for free: **every name a block
edge reads is either in-block or UPSTREAM of the block.** A downstream
edge giving it would be reachable from the block and reach it back, so
it would be in the block. That is why a selector's branch can be known
before the block runs.

**A SELECTOR** is a jump node of a block member's plan whose LEVEL
QUANTITY reads no coordinate the block gives — resolving a placeholder
in that level into the jump it stands for, transitively, exactly as
`_dependence` (`program.py:598`) resolves ADR-121's dependence. The
relation is upward closed along the nesting for the same reason it is
there: a placeholder stands for exactly the subtree it replaced, so a
node whose level names a non-selector placeholder is itself not a
selector.

This definition is self-consistent with ADR-121: a node whose level
reads the member's OWN driven end reads a coordinate the block gives, so
it is NOT a selector and stays where ADR-121 put it — the walked layer
inside the piece.

**The FOLD.** Take the member's SKELETON, set a set of jump placeholders
to ZERO, and fold: `x*0 → 0`, `0*x → 0`, `0/x → 0`, `0+y → y`,
`y+0 → y`, `y−0 → y`, `0−y → −y`. The edge's READS under that
assignment are the folded skeleton's free names, with every surviving
placeholder followed into its own (folded) level quantity, transitively.

**A SWITCHING selector.** A placeholder may be folded to zero at COMPILE
time only where its primitive holds the zero branch on an INTERVAL of
its level quantity, because the compile is asserting that some piece of
some tick actually reads it there:

| primitive | zero branch | where |
| --- | --- | --- |
| `floor` | `0.0` | `[0, 1)` of the level — an interval |
| `ceil` | `0.0` | `(-1, 0]` — an interval |
| comparison | `0.0` | its whole FALSE side — an interval |
| `%` | quotient `0` | `(-1, 1)` of `a / b` — an interval |
| `sign` | `0.0` | `{0}` — a POINT, not an interval |

`sign` is the one that does not qualify, and it matters: `_branch_of`
(`program.py:527`) returns `float((level > 0) - (level < 0))`, which is
`0.0` only where the level is EXACTLY `0.0`. A `sign`-gated source
counted as switched at compile would be active on every real piece, and
the block would be refused at the first tick instead of at construction —
the run-time refusal standing in for a check that could have been made
before the machine ever moved. So a `sign` node is a selector (its level
may read nothing the block gives) and its branch is still FORCED on a
piece like any other; it simply cannot make a source switched.

`%` qualifies under the same rule and still cannot switch an IN-BLOCK
source, for a reason that follows from the rule rather than from a
special case. `_skeleton` (`program.py:2727`) rewrites `a % b` to
`a − q·b`, so folding `q` to zero keeps `a` and drops only `b`; and
`_argument_graph` (`program.py:2757`) makes the node's level `a / b`, so
a `%` node that is a SELECTOR has a level reading no in-block
coordinate — which means neither `a` nor `b` is in-block, and the name
the fold drops was never an in-block dependency. That is the same reason
ADR-121 refuses a bare remainder as a self-read switch, arriving here for
free.

**A source is SWITCHED, and the fold is done ONCE.** The fold is
MONOTONE in the set of placeholders zeroed: every rule either removes
names (`x*0`, `0*x`, `0/x`) or keeps exactly the names its operand had
(`0+y`, `y+0`, `y−0`, `0−y`), and a placeholder inside a call argument
can only lose names as that argument does, because a call's reads are
the union of its arguments'. So zeroing one MORE placeholder never ADDS
a read, and the reads under "every switching selector of this member at
its zero branch AT ONCE" are the MINIMUM over every assignment.

That collapses what would otherwise be a search over `2^n` assignments to
one fold per member:

- the member's UNCONDITIONAL dependencies are the in-block reads that
  survive that single all-zero fold;
- a source is SWITCHED exactly when it is in the member's reads with
  nothing folded and absent from that one fold.

The RUN-TIME fold is a different computation and is not this one: on a
piece it substitutes the ACTUAL branch values read at the midpoint — an
integer for `floor`, `ceil` or `%`, `0.0` or `1.0` for a comparison,
`-1.0`, `0.0` or `1.0` for `sign` — and keeps whatever survives. The
compile-time fold asks what can NEVER be removed; the run-time fold asks
what is removed HERE.

Measured on the fixture (`spikes/fold.py`), with `$j0`, `$j1`, ... the
compiler's own per-plan placeholder names (each plan numbers its own
jumps, which is why both edges start at `$j0`):

```text
=== ['crank', 'shift', 'clearing', 'carry.travel', 'higher.turn'] -> ['higher.turn'] ===
  skeleton : (((crank * $j0) + ((crank * $j1) * $j2)) + (clearing * $j3))
    $j0: >= on (shift - 0.5)  affine=True  level reads ['shift']
    $j1: < on (shift - 0.5)  affine=True  level reads ['shift']
    $j2: >= on (carry.travel - 0.5)  affine=True  level reads ['carry.travel']
    $j3: > on (higher.turn - 0.5)  affine=True  level reads ['higher.turn']
  reads with nothing folded: ['carry.travel', 'clearing', 'crank', 'higher.turn', 'shift']
  reads with $j1=0: ['clearing', 'crank', 'higher.turn', 'shift']

=== ['lower.turn', 'higher.turn', 'shift', 'carry.travel'] -> ['carry.travel'] ===
  skeleton : (((lower.turn * $j0) + (higher.turn * $j1)) * $j2)
    $j0: < on (shift - 0.5)  affine=True  level reads ['shift']
    $j1: >= on (shift - 0.5)  affine=True  level reads ['shift']
    $j2: < on (carry.travel - 1)  affine=True  level reads ['carry.travel']
  reads with nothing folded: ['carry.travel', 'higher.turn', 'lower.turn', 'shift']
  reads with $j1=0: ['carry.travel', 'lower.turn', 'shift']
```

The block is `{higher.turn's relation, carry.travel's relation}` — which
is exactly the pair today's message names. `$j0` and `$j1` are
selectors in both (their levels read `shift`, an input); `$j2` and `$j3`
are not (their levels read coordinates the block gives). `carry.travel` is
switched out of the WHEEL's law by that plan's `$j1` — its
`shift < 0.5` — reading zero, and `higher.turn` is switched out of the
LEVER's law by that plan's `$j1` — its `shift >= 0.5` — reading zero.
The two comparisons are complementary, so at any value of `shift` at
most one of the two dependencies is active; the compiler does not know
that (it is arithmetic about `shift`, not structure) and does not need
to, because both dependencies are switched and that is all construction
asks. Nothing is refused.

**What is refused at construction**, by relation identity, naming the
relations as written and the classes that stated them:

- **A block containing a WIRING or a FORMULA edge.** Neither carries a
  jump node, so neither can be switched; the message says so and names
  the wiring or the derived coordinate. Both shapes are REACHABLE — which
  is what §5's pre-pass rule is for, and why this bullet is not dead
  text. A wiring can genuinely sit on a cycle: its source is any
  coordinate the DECLARING PARENT declares, `_check_wiring`
  (`declarative.py:346`) accepting a value found in
  `declared_ports(owner)` or `declared_joints(owner)` and not a driver
  only, so a parent joint another relation determines may be wired into
  a child and carried back.
- **A cycle no selection can break.** Build the block's UNCONDITIONAL
  dependency graph: per member, the in-block reads that survive its one
  all-zero fold. If it still has a cycle, that cycle is present on every
  piece, and it is refused with today's message — which is what a plain
  cycle of two ordinary laws gets, unchanged, plus a sentence saying
  what a switch would be.
- **An INTERMEDIATE among a block's driven ends** — a plain port or a
  derived coordinate. A block advances its coordinates PIECE BY PIECE
  inside a tick and hands the run an absolute landing for each, and only
  a coordinate the run banks keeps that. Refused by name, as ADR-121
  refuses a self-read of one, and with the same advice: state the
  relation into the joint coordinate and let the port follow it.
- **A block member driving a GROUP** (§1).

**Why the check is NECESSARY and not SUFFICIENT, said out loud.** The
compiler cannot know which branch VECTORS are reachable: `$j0` and `$j1`
above are complementary, but that is arithmetic about `shift`, not
structure. So the construction check refuses only what can never work,
and a particular piece that is genuinely cyclic is refused at run time
(§3). This is deliberate: the alternative is a satisfiability question
over the levels, which is a solver, which is the thing the note rules
out.

**Alternative rejected: restrict a selector to a comparison or `sign`,
by PRIMITIVE.** The reviewer's briefing proposed admitting comparisons
and `sign` and excluding `floor`, `ceil` and `%`, on the ground that the
latter's placeholders are unbounded integers and fold nothing. Rejected
in that form, because the primitive is not what makes a term vanish — an
ATTAINABLE zero branch is. The rule above is therefore stated once, over
the fold, and applies to every primitive by asking where each holds its
zero branch. It happens to exclude exactly the one the briefing wanted
to admit, `sign`, and to admit all three it wanted to exclude.

**Alternative rejected: search over selector ASSIGNMENTS.** An earlier
draft of this document defined a source as switched "by a SET of
selector branches", which invites `2^n` folds per member and leaves the
construction check's cost undefined. The monotonicity above makes the
all-zero fold the minimum over every assignment, so ONE fold per member
answers both questions the compile asks. `spikes/fold.py` measured a
single-placeholder fold; task 2.4 pins the monotonicity itself, by
asserting on the fixture that the reads under all-zero are a subset of
the reads under each single zero.

**Alternative rejected: require EVERY in-block dependency to be
switched.** Simpler to state, and strictly wrong: a block in which
`A ← B` is unconditional while `B ← A` is switched is orderable on every
piece (B, then A, when `B ← A` is inactive), and this rule would refuse
it. Taking the SCC of the unconditional graph is the same cost — one
more Tarjan pass over a graph the size of the block — and refuses
exactly the shapes that can never work.

### 3. Evaluation: a block runs piece by piece, and a selector is a constant on a piece

**The block is ONE entry in `program.edges`.** A compound `block` edge
carries the union of its members' `needs`, all their `gives`, and the
members themselves. `_ordered` therefore contracts each block to one
node and the program's order is a total order again — which is what
keeps `Run._pass`, `Run._locate`, `Run._group`, `Run._pushes`,
`Program.determiner`, `Program.sources`, `Program._sub_program`,
`Program.values_of` and `Program.response` working through the `Edge`
interface they already use, with no new branch in `run.py` at all.

**`Edge.increments(values, deltas, crossings, tick, landings)` for a
block**, in four steps:

1. **Locate the selector crossings over the stretch.** Every selector's
   level reads only coordinates the block does not give, so its path
   over the stretch is the linearization `values + deltas·t` that
   `_along` (`program.py:518`) already builds — the same arithmetic the
   member's own plan would use for that node. Crossings are located by
   `JumpPlan._crossings_of`'s two cases unchanged: SOLVED where the
   level is affine, sampled at `_SUBDIVISIONS` and bisected to
   `_CROSSING_TOLERANCE` otherwise. They are deduplicated by
   `_deduplicated`, merged into the partition by `_merged` (two cuts
   closer than the tolerance are one), and bounded by `_MAX_CROSSINGS`.
   The selectors of ALL members are located into ONE partition, in the
   members' own order and each member's postorder, so the partition is
   deterministic.

2. **Order the block on each piece.** Every selector's branch is read at
   the piece's MIDPOINT — ADR-107's own rule, valid here for ADR-107's
   own reason: the midpoint is a point genuinely inside the piece, and
   these levels do not depend on anything the block computes. §2's
   RUN-TIME fold — the actual branch values substituted, not the
   compile's all-zero one — gives each member's active reads; the
   in-block ones are the piece's ACTIVE GRAPH; Kahn over it gives the
   order. The order is MEMOISED per branch vector, so a stretch of many
   pieces under two selections costs two Tarjan-free Kahn passes, not
   one per piece.

3. **Refuse a still-cyclic piece, transactionally.** A `UnsupportedLaw`
   naming the piece's fraction of the stretch, the selector branches it
   was read under, and the relations on the cycle. `Run.integrate`
   already catches `UnsupportedLaw` around the whole segmented tick
   (`run.py:633`) and calls `_refuse(moved)`: the bank, the tick count,
   the tree and the three records stand as they were, and the commands
   that moved an input are retired `refused`. No new rollback is
   written.

4. **Run the members over the piece, in that order.** Each member is
   evaluated by its EXISTING machinery — ADR-107's partition, ADR-121's
   walk — over the piece, with:
   - a coordinate the block does NOT give at `values[k] + deltas[k]·a`
     and moving by `deltas[k]·(b − a)`;
   - a coordinate the block DOES give AND the piece's order has already
     determined, at the BLOCK-ADVANCED value it holds at the piece's
     start — the running absolute the block keeps for it, which a
     landing REPLACES and an increment ADDS to — and moving by the
     increment computed for it ON THIS PIECE;
   - a coordinate the block gives that this piece's order has NOT yet
     determined, at the block-advanced value it holds at the piece's
     START and moving by `0.0` (below);
   - **every SELECTOR placeholder FORCED to the branch step 2 read.**

   The member's increments are accumulated per coordinate; every
   crossing a member reports is rescaled from the piece to the stretch as
   `a + t·(b − a)` — the same map `Run._record` (`run.py:1234`) then
   applies from the segment to the tick — and the selector crossings
   located in step 1 are reported as the `Crossing` entries the owning
   member's plan would have reported, one per member per node per
   surface.

**What the block REPORTS as a landing, and why it is not the last one.**
A member's `increments` returns a per-coordinate increment and, where
ADR-121's walk cut the path, a `landings[key]` — the ABSOLUTE value that
end holds (`program.py:1259`). `Run._landed` (`run.py:661`) then
OVERWRITES `value + delta` with that float in the committed bank
(`run.py:586-590`). So whatever the block puts in `landings` is what the
run commits, absolutely, and an increment the block reported alongside it
is DISCARDED.

Reporting the LAST landing is therefore wrong. If piece 2 lands
`carry.travel` at `1.0` and piece 3 — the selection having changed, so a
different source now drives it — moves it by a further `+0.3`, reporting
`1.0` makes the run commit `1.0` and loses the `0.3`. The rule is:

> For every coordinate that landed in ANY piece of the stretch, the
> block reports the ABSOLUTE value it has itself advanced that
> coordinate to by the stretch's END — the landing plus every later
> piece's increment, accumulated by the block as it goes. For a
> coordinate that landed in NO piece the block reports nothing, and the
> run commits `value + delta` exactly as it does today.

That keeps ADR-121's reason for landings intact (`x + (y − x) != y` for
about six pairs of floats in a hundred, so the exact float a walk left a
coordinate at must not be reconstructed by addition) while making the
block's own accumulation the thing that is reported, per block rather
than per edge.

**What a member is handed for an in-block source it has not been given
yet.** On a piece, a member's `needs` still lists EVERY in-block source
it ever reads, including ones this piece switched OUT and which the
active order therefore determines later, or not at all. `Edge._inputs`
(`program.py:1193`) builds `values[k] + deltas[k]` for all of them
unconditionally, so the block must put something in both maps. It puts
the coordinate's BLOCK-ADVANCED value at the piece's start, and a delta
of `0.0`.

That is safe, and not by a tolerance:

- **Numerically irrelevant.** The fold is what said the source is
  switched out on this piece: every term reading it is multiplied by a
  selector placeholder the block has FORCED to zero, so whatever float
  is handed over is multiplied by zero. The value could be anything; the
  block hands over the most honest one available.
- **It records no crossing of its own.** A non-selector jump node whose
  level reads ONLY such a source has a constant level over the piece,
  and a constant level crosses nothing: `_crossings_of` returns `[]` on
  the affine path the moment `high == low` (`program.py:452`), and the
  searched path finds no surface between two equal samples. The one
  exception is a constant level sitting EXACTLY on a surface, which the
  inclusive search would report — but that is today's behaviour for any
  source that does not move in a tick, not something a block introduces.
- **A switched-out source that was determined EARLIER in the piece's
  order** — because it is upstream of another member — is handed its
  REAL piece increment, not zero. Its dead terms still evaluate to zero,
  and a non-selector node inside one may still record crossings. That is
  exactly what a dead term's jump node does in an acyclic program today;
  ADR-107 subtracts every jump, so a crossing records without moving a
  part.

**Forcing has to reach every place the member's plan reads that node.**
A selector is a jump node of the MEMBER's own plan, and a selector's
level reads nothing the block gives — including the member's own driven
end — so a selector is always an INDEPENDENT node in ADR-121's split
(`_Retained.__init__`, `program.py:682`), never a dependent one. Forcing
is therefore applied at exactly two points and inherited everywhere
else:

- `JumpPlan._partition` (`program.py:397`) SKIPS locating a forced
  node's crossings — the block located them over the stretch already,
  and re-locating them inside the piece is the second reading this
  design exists to remove;
- `JumpPlan._branches` (`program.py:345`) returns the FORCED value for a
  forced placeholder instead of calling `_branch_of`.

Everything downstream reads those: `_Walk._outer` and
`_Walk._outer_branches` (`program.py:788`, `797`) are `_Retained.outer`'s
`_partition` and `_branches`; `_Walk._decide` and `_Walk._tentative`
start from `branches = dict(outer_branches)`; `_probe`, `_crossing`,
`_searched`, `_bisect`, `_skeleton`, `_level`, `_land` and `_far_side`
all evaluate through that same `branches` map; and `JumpPlan.cuts` and
`_Retained.cuts` take the same partition. So a member whose selector sits
in layer one and whose LATCH sits in layer three — the Curta lever
exactly: selector on the carriage, hysteresis on the lever's own
travel — holds the forced branch through the whole walk, including the
far-side landing.

**The memoisation key is the vector of ACTUAL branch VALUES**, not of
booleans: `_branch_of` returns an integer float for `floor`, `ceil` and
`%`, and a crank passing three tooth windows in one tick gives three
different keys, not one "true". Two pieces share a Kahn pass only when
every selector reads the same float on both.

**Why the block's reading and the member's own reading CANNOT disagree.**
Because there is no second reading: the branch is SUBSTITUTED, not
re-derived. This is the design's main departure from the reviewer's
sketch, which had the member re-locate the same surface and argued from
`_surfaces(inclusive=False)` (`program.py:544`) and `_merged`'s
tolerance that the two would agree. They agree in the ordinary case and
the argument is sound, but it is an argument about ulps at a cut that
becomes false for a short enough piece: `_merged` folds cuts closer than
`_CROSSING_TOLERANCE` **in the fraction of the path being cut**, so a
level recomputed a few ulps on the wrong side of its surface at the left
end of a piece of width `1e-9` is a genuine cut at relative position
`1e-3`, and the member would integrate part of that piece under the
branch the block did not order it under. Forcing the branch removes the
question rather than bounding it, costs one dict entry per selector per
piece, and saves the re-location.

**Measured (`spikes/pieces.py`).** The lever edge `(lower.turn,
carry.travel) drives carry.travel`, law `lo * (own < 1)`, over a stretch
in which `lower.turn` sweeps `0 → 2` from `carry.travel == 0`:

```text
WHOLE stretch  [0, 1]
  increment 1.0
  landing   1.0
  crossings [('<', 0.0, 0.5)]

PIECE BY PIECE, cut at 0.25 and 0.6, the in-block coordinate ADVANCED
  [0.0, 0.25] increment=0.5 landing=None -> own=0.5 crossings(rescaled)=[]
  [0.25, 0.6] increment=0.5 landing=1.0 -> own=1.0 crossings(rescaled)=[('<', 0.0, 0.5)]
  [0.6, 1.0] increment=0.0 landing=None -> own=1.0 crossings(rescaled)=[]
  sum over pieces = 1.0   final landing = 1.0
  whole stretch   = 1.0   landing = 1.0

THE SAME PIECES, the in-block coordinate NOT advanced -- the one thing
the implementation must not get wrong
  [0.0, 0.25] increment=0.5
  [0.25, 0.6] increment=0.7
  [0.6, 1.0] increment=0.8
  sum over pieces = 2.0   (whole stretch = 1.0)
```

Same increment, same landing float, and the crossing rescales to exactly
the fraction the whole-stretch run reported. The negative control in the
same run — the same three pieces with the in-block value NOT advanced —
sums to `2.0`, which is the one thing the implementation must not get
wrong and is why it is measured here rather than asserted.

**What this measurement does NOT settle, said out loud.** The landing
falls in the SECOND piece and the third piece's increment is `0.0`, so
"the last landing" and "the block-advanced absolute" are the same float
here and the spike cannot tell them apart. It is not evidence for the
reporting rule above; task 4.7 is — a landing in one piece and a further
increment in a later piece of the same stretch, with the committed float
asserted equal to the block's advanced absolute rather than to the
landing.

**"The block's own deterministic order", defined.** It is the CANDIDATE
EDGES' own order, restricted to the block's members: `compile_program`
builds its candidates by walking `_units(root)` (`program.py:2457`),
which visits the linked tree in tree order and takes each assembly's
records in the order `resolve_declared_relations` recorded them
(`couplings.py:1785-1804`) — declaration order, and copy order within a
broadcast. Nothing is sorted and nothing is hashed, so the order is the
same for a given tree on every run and in every process. The members
appear in it exactly where they would have appeared had there been no
block; contracting an SCC changes where the GROUP sits in the program
order, never the members' order inside it.

That one order is used in four places, and they must not diverge:

- the block's `increments`, so the selector partition of step 1 is
  merged in the members' order and each member's postorder;
- `Program.described()`, which emits the `block` line at the block's
  position and then each member's ORDINARY edge line contiguously, in
  that order. The `block` line names the members' driven ids; the member
  lines carry their expressions. So the program IDENTITY covers every
  member's law exactly as it covers any other edge's, and a program with
  no block prints what it printed before, character for character;
- `Program._placeholders` and `Program.published`
  (`program.py:1713`, `1620`), which walk `self.edges` in step and index
  one by the other, so both must EXPAND a block into its members in that
  same order — leaving placeholder minting "edge order then postorder"
  over a flat list of law edges, exactly as today;
- `Program.published`'s `edges` list itself, which is what §9's
  "contiguously, in the producer's own deterministic order" means.

**The `Edge` interface on a block**, stated so nothing in `run.py` has
to guess:

- `affine` is `False` on every give. A block's value is piecewise in the
  selector partition AND re-ordered across it, so a stop on a block
  coordinate is SEARCHED (§7), never solved.
- `cuts` is the selector partition merged with each member's own cuts
  inside each piece. `Run._locate` reaches it only through the affine
  path, so it is unreachable today; it is defined rather than left to
  raise, because `_piecewise` is meaningful over it the day a later
  cycle classifies a block give as affine.
- `values` is `()`. Every give of a block is a BANKED coordinate by the
  refusal in §2, so `Program.values_of` (`program.py:1459`) skips the
  block on its own existing test and never asks.
- `predicts` is not reached: a block is never a `check`.
- `description` is the members' descriptions joined, and `stated_by` the
  classes that stated them, so every refusal that prints an edge prints
  the block's members.

### 4. The accuracy contract

**A selection change alone moves NOTHING.** A selector is a jump node of
its member's law, and ADR-107 subtracts every jump: the increment on
each piece is the change of the BRANCH-SUBSTITUTED law over that piece,
and nothing in the sum ever spans the cut. So a carriage moved from one
position to another with the crank standing still contributes zero to
every dial and every lever — not "approximately zero", exactly the
number zero, because both pieces evaluate a constant law at two equal
points. This is requirement-note item 2's second sentence.

**A command taken in one tick, in twelve, and in two hundred and forty
agree to the run's own AGREEMENT TOLERANCE**, `1e-9·max(1, |a|, |b|)`
per coordinate — the tolerance `Run._agree` already calls equality
(`run.py:80`) and the one the document publishes as `limits.agreement`.
A command's STATUS agrees exactly; its ADMITTED TRAVEL agrees within the
same window, not exactly.

**Why admitted travel is not exact across partitions, measured off the
code.** `Command.admits` (`run.py:183-200`) returns
`value_at(elapsed) − value_at(elapsed − 1)` for the tick ending at
`elapsed`, and `Run.integrate` accumulates `admitted_native += delta`
once per tick (`run.py:645`). Over 240 ticks that is a float sum of 240
differences where the one-tick run is a single difference. The sum
telescopes in real arithmetic and not in doubles, so the two answers are
ulps apart by construction — a fact about the command bookkeeping that
has nothing to do with blocks, and one this cycle must not promise away.
Stating admitted travel inside the agreement window is the honest
contract; promising bit-equality would be a claim the existing code
already falsifies.

**What "exactly" covers, and its precondition.** A STATUS
(`completed`/`blocked`/`refused`), a lever set or not, a dial's digit,
the ORDER of the records: these are discrete readings of a float, and
they are exact only where the float is not on a knife edge. The fixture
for this contract therefore chooses values that sit AWAY from every
surface at each tick's end — no gate threshold, no declared bound and no
selector surface within the agreement window of a committed value. That
is a precondition of the contract, stated here rather than discovered in
a flaky test.

The corpus's own "EXACT for discrete state" is a different promise and is
untouched: it is about two runtimes replaying the SAME tick sequence, not
about two different partitions of one command.

The argument, and its honest limit. Inside a piece a member's increment
is the difference of two evaluations of a continuous function along a
straight path in its sources — exact, at any number of pieces. The one
approximation is that an IN-BLOCK source's path within a piece is
LINEARIZED from its net increment on that piece. That is not a new
approximation: `Run._pass` (`run.py:678`) already hands a downstream
edge the net `deltas[X]` an upstream edge produced over the WHOLE
stretch and lets it read `values[X] + deltas[X]·t`. Cutting at every
selector crossing makes the same linearization strictly FINER, never
coarser. So refining the tick can only improve the answer, and the
contract is stated as the agreement window rather than as bit-equality —
which is what the note's item 4 asks for ("a stated accuracy
contract") and what is honest.

**A partial command, released and resumed, is the same machine.** Each
tick is integrated from the committed bank; a released command retires
with the travel it admitted and nothing remembers what it did not make
(ADR-108). Nothing about a block changes that: its coordinates are
banked, and a block that ran for half a revolution has advanced them by
exactly what half a revolution moves.

### 5. Rest, initialization, and where membership is decided

**Decision: a PRE-PASS at `Sim` construction, before the rest render.**
Fact 2 forces it: the same cycle with no self-read is refused BY THE
REST RENDER, with `DoublyBound` where the driven ends carry rest guards
and `UnreachedCoordinate` where they do not. The compile never runs. So
a rule that only the compile knows cannot save it.

Fact 3 says the pre-pass is possible: `spikes/membership.py` walks
`_units(root)` over a freshly constructed, unrendered tree and finds
every record with its ends resolved and its driven SLOT identity
available.

**The rule, stated once.** The pre-pass:

- walks the linked tree exactly as `_units` (`program.py:2457`) does,
  and builds ONE dependency graph over RESOLVED DRIVEN SLOTS from EVERY
  relation record, EVERY wiring and EVERY derived coordinate that walk
  returns — each taken FORWARD AS DECLARED, which for a relation of
  several ends is the only direction it has (couplings, "A relation may
  name several coordinates at each end") and for a wiring is the only
  direction it has at all;
- takes the nontrivial SCCs of that graph, and KEEPS only those holding
  at least one BANKED driven end — a driver or a joint coordinate;
- marks every RELATION RECORD in a kept SCC as a BLOCK MEMBER. A wiring
  and a derived coordinate are in the graph so the cycle is SEEN; they
  carry no mark, because they bind nothing this rule could change and
  the compile is what refuses them.

`_step_relation` (`couplings.py:2201`) then skips a marked record
exactly where it skips a self-read: recorded solved `'forward'`, its law
unapplied, under a running root and only there. **A block relation binds
NOTHING at rest**; its driven coordinate's rest value is the author's own
guarded rest default, and construction refuses by name when there is none
— the refusal the run already makes for a joint coordinate the rest
render leaves unbound (`spikes/reduced.py`, class `Unguarded`, shows
exactly that shape arriving one step earlier today).

**Why every cycle that touches the bank must be marked.** An earlier
draft marked only records naming SEVERAL ends. Three shapes then never
reached the compile at all, and the refusals §2 promises for them would
have been dead text:

- a union cycle passing through a SINGLE-ENDED relation — `x.drives(y)`
  inside a cycle of multi-source laws;
- a union cycle passing through a WIRING or a DERIVED COORDINATE, which
  is exactly what §2's first refusal bullet names. A wiring genuinely
  can sit on a cycle: `_check_wiring` (`declarative.py:346`) accepts
  any coordinate the declaring parent declares — `declared_ports(owner)`
  or `declared_joints(owner)` — so a parent joint another relation
  determines may be wired into a child and carried back;
- and, symmetrically, an SCC entirely among relations that reach NO bank
  coordinate — a cycle of plain-port relations that `_reaching_the_bank`
  (`program.py:2917`) DROPS before the compile ever orders anything.
  Marking one of those would make a legitimate model bind nothing at
  rest for a block that is never compiled, and would fire risk 5's
  "pre-pass and compile agree" assertion as an internal error on a model
  that works today.

The banked-driven-end condition is what excludes the third case, and
taking every record forward is what admits the first two. Together they
make risk 5's assertion hold BY CONSTRUCTION: `_reaching_the_bank` drops
a candidate only when NO driven end reaches the bank, and §2 refuses an
intermediate among a block's gives, so an SCC the pre-pass keeps is an
SCC the compile sees.

**A single-ended relation so marked is recorded solved FORWARD**, like
every other marked record. The forward reading is not a guess that could
lose a legitimate direction: for a single-ended relation to be in a
nontrivial SCC at all, its ONE source must be a coordinate the cycle
determines and its ONE driven end must be read back by the cycle. Any
jump that could gate that source has a level reading it, which is
in-block, so the node is not a selector and the dependency is
UNCONDITIONAL — whichever way the solver would have read the relation.
Every such cycle is therefore refused at compile with today's cycle
message, and no direction that would have worked is thrown away.

**The observable changes this makes, stated rather than discovered.**
Today a cycle reaches `_ordered` at all only when at least one of its
relations reads its own driven end: that is what makes `_step_relation`
defer it. Without a self-read the REST RENDER refuses it first —
`DoublyBound` where the driven ends carry rest guards,
`UnreachedCoordinate` where they do not (`spikes/reduced.py`, classes
`NoSelfRead` and `Unguarded`, both rerun on this worktree). Marking
membership before the rest render moves every banked cycle past that
gate, which changes two outcomes:

- **A SELECTED cycle with no self-read now CONSTRUCTS.** That is the
  point of the cycle, and `spikes/reduced.py`'s `NoSelfRead` — whose
  relations carry the `shift < .5` / `shift >= .5` factors but no `own`
  term — is exactly that shape, refused `DoublyBound` today.
- **An UNCONDITIONAL cycle with no self-read is still refused, but by the
  COMPILE.** It is marked, binds nothing at rest, reaches `_ordered`, and
  gets the cycle message naming every relation and the coordinates they
  wait on, where today it gets `DoublyBound` naming one coordinate and
  the author's `simulate()`. A better message for the same verdict — and
  a behaviour change, so it is a scenario, not a footnote.

Both were measured on this worktree, on the reduced fixture with its
selections removed: the unconditional cycle whose relations KEEP their
self-read terms reaches `_ordered` today and prints
`UnsupportedLaw: the relations (crank, clearing, carry.travel,
higher.turn) drives higher.turn, (lower.turn, higher.turn, carry.travel)
drives carry.travel form a cycle the run cannot order` verbatim, while
the same cycle with the self-reads also removed prints
`DoublyBound: higher.turn would be bound by the relation ... and by the
author's simulate()`. Task 2.2's "passes today" fixture is the FIRST of
those two — the one that already gets the message the task asserts.

**Under a NON-running root, nothing changes.** No new declaration exists,
so the same relations are the same relations, and the untimed
enumeration refuses them as it does today (measured: `DoublyBound` and
`UnreachedCoordinate`). This is where the design deliberately differs
from ADR-121, which had to add a refusal because `(rack &
wheel.turn).drives(wheel.turn, ...)` was a NEW sentence that would
otherwise stand inert. Extending a running-only rest rule into untimed
posing would be inventing a meaning for a cycle in a pose, which nothing
asks for.

**An untimed `set_state` on a running root is INERT**, as under ADR-121:
the run owns the bank, the block relation binds nothing at rest, and
rendering or rebinding the same snapshot advances nothing (ADR-105).

**Snapshot, restore, reset and recording are unchanged.** A block's
coordinates are ordinary banked coordinates; the bank is the whole
state. `snapshot`/`restore` still refuse on a program identity or `dt`
mismatch before touching live state.

**Program identity.** `Program.described()` gains ONE `block` line per
block, naming its members' driven ids in the block's own order (§3),
placed where the block sits in the program's order — and then each
member's ORDINARY edge line, contiguously, in that same order. So the
identity covers every member's ends, direction and expression exactly as
it covers any other edge's: a program whose block MEMBERSHIP changes has
a different identity because the `block` line differs, and a program
whose SELECTORS change has one because a selector is part of a law's
expression and `described()` prints every edge's expression. A program
with no block prints exactly what it printed before, so every existing
identity, and every snapshot taken against one, is unchanged.

**`couplings` is not modified.** The one behaviour the enumeration gains
is "skip a marked record", which is the self-read rule with a different
marker, and the self-read's own rest rule is stated in the SIMULATION
spec ("A law may read the coordinate it drives": *At rest such a relation
SHALL bind nothing*) and not in `couplings`. Following that precedent
keeps one place to read the rest rules; inventing a second would split
them.

### 6. Composition with ADR-121

A block member's plan is now read in THREE layers, and the first two
were already there:

1. **Selectors** — forced by the block, CONSTANT on the piece (§3).
2. **ADR-121's independent layer** — `_Retained.outer`, ADR-107's own
   partition over the remaining jump nodes that do not depend on the
   member's own driven end, branches at its midpoints.
3. **ADR-121's dependent layer** — `_Walk`, branches read at the piece's
   LEFT END from the value the coordinate retains there, cut at the first
   surface any dependent level reaches, the coordinate committed at the
   FAR SIDE of the surface.

**The split of layers 2 and 3 is decided ONCE, at compile, with the
selectors still SYMBOLIC.** `_Retained.__init__` (`program.py:682`)
computes `_dependence` over the whole plan; forcing a selector to a
number later could only REMOVE names from a level, so it could only move
a node from "dependent" to "independent" — an improvement the design
declines to take, because taking it would make the split a property of
the piece rather than of the plan, and ADR-121's two-layer partition
would then have to be rebuilt per piece. Keeping the compile-time split
is conservative, identical to today's behaviour for every non-block law,
and one fewer thing to get wrong.

This is what makes the Curta's two ADR-121 gates compose with the
selection inside one tick: the carry lever's LATCH (set by the dial's
pin, held, reset by the crank's cam — a hysteresis on the lever's own
travel, `simulation/carry_motion.py:14`) and each dial's MISSING-TOOTH
clearing gate are layer-3 reads of their own coordinates, walked inside
each selector piece, while the carriage's position cuts the piece
boundaries. A tick carrying a selector crossing AND a self-read crossing
reports both in `sim.crossings`, the selector's located over the
stretch, the self-read's rescaled out of its piece.

### 7. Stops and constraints in the same tick

**A declared range on a block coordinate.** `Run._reached` sees it left
its bound; `Run._locate` (`run.py:949`) finds `program.determiner[key]`
— the block edge — reads `affine[index]` as `False`, and takes
`_searched`: `_SUBDIVISIONS` samples of `edge.increments` over the
stretch truncated at each fraction, bracketed and bisected to
`_CROSSING_TOLERANCE`. Truncating every delta by `t` is exactly what the
block needs: a selector crossing at fraction `s` of the full stretch
reappears at `s/t` of the truncated one, i.e. at the same absolute
point, so the localization is consistent with the integration. The
coordinate is then committed AT its bound, and `Run._landed`
(`run.py:661`) runs BEFORE the stops are located, so a block landing on
the same coordinate in the same segment is overwritten by the bound —
"a physical bound is a bound of the coordinate itself", unchanged.

**A stop EARLIER in the stretch than the selector crossing.**
`Run.integrate` cuts the tick at `t*` and re-integrates `[0, t*]` with
the WHOLE program; the block relocates its selectors on the shorter
stretch and finds none. The remainder is then examined as a fresh
stretch, in which the crossing falls. Both happen, in order, and the
whole tick is staged.

**A stop LATER than the selector crossing.** The block crosses inside
the first segment and the stop cuts after it. Same machinery.

**A stop's blocked group when the pushing input reaches the coordinate
only through an INACTIVE selection.** `Run._group` takes the compiled
candidates — `Program.sources[key]`, which for a block is the union of
every input reaching any member, deliberately over-broad — and filters
them by `Run._pushes` (`run.py:1055`), which displaces ONE input, runs
the edges, and asks whether `key` moved. For a block that runs the whole
block under that one displacement, so an input coupled to the coordinate
only through a currently-inactive selection contributes NOTHING and is
NOT stopped. That is ADR-113's per-tick test working exactly as designed
and exactly for this mechanism; it is requirement-note item 2's first
sentence ("an inactive association neither moves its former wheel nor
blocks an input the mechanism permits"), and it is why that item needs
no new machinery. It gets a scenario anyway, because "no new machinery"
is a claim, not a test.

**Checked, because the break depends on it.** `Run._pushes`
(`run.py:1055`) runs `edge.increments(values, deltas)` and then breaks on
`if key in edge.gives`. With the block as ONE compound edge, `gives`
holds every member's give, so the break happens AFTER the whole block
has run under that one input's displacement — which is exactly what the
paragraph above needs, and would NOT be true if the members were separate
entries with the probe stopping at the first one to name `key`. The same
call shape is what `Program.response` (`program.py:1493`) and
`Run._along` (`run.py:1031`) use: two positional arguments, so
`crossings` is `None`, `tick` is `0` and `landings` is `None`. A block's
`increments` must therefore be complete and side-effect-free with all
three omitted — it records no `Crossing`, reports no landing, and mutates
nothing — and must still refuse a genuinely cyclic piece: the SAME
midpoint reading and the SAME ordering it does inside the tick, so a
displacement probe and the tick it is probing for cannot disagree about
whether the model can be ordered. A probe that refused where the tick
would not, or ran where the tick would refuse, would make a stop's
blocked group a function of the probe rather than of the machine.

**A `Bound(..., reads=)` on the carriage itself** — the Curta's
interlock, "no shift unless lifted". ADR-113's constraint is sampled
over its SUB-PROGRAM, `Program._sub_program` (`program.py:1411`), a
filter of `program.edges` in program order. With the block as one entry
the filter either takes the whole block or none of it, which is the
right granularity: the block's members are inseparable within a tick.
The interlock's own reads (`lift`) are UPSTREAM of the block, so its
sub-program contains no block at all and costs nothing new. A constraint
on a coordinate the block gives pulls the block in and pays for it,
which §8 states.

**ADR-113's recorded limit is untouched**: the pushing test is net over
the stretch, not local at `t*`.

### 8. Retention

Nothing here is new machinery; it is what banked coordinates already do,
and the design states it because the requirement note's items 1 and 3
are about exactly this.

- **Shifting away and back preserves history.** Every dial and every
  lever is a banked joint coordinate. A selection that goes inactive
  drives nothing, and a coordinate no edge determines HOLDS
  (`_ordered`'s own first sentence). So a lever left SET at position 0
  and shifted to position 1 stands at the value it was left at until the
  mechanism — the crank's reset cam, through its own term of the lever's
  law — returns it, and then it acts on the wheel it now faces.
- **Selection alone creates no motion** (§4).
- **A locked shift stops at its restraint**, through ADR-113's
  constraint, retiring its command `blocked` with the travel it admitted;
  nothing discards a pending carry and nothing finishes one.

### 9. Publication

**Version 7 for a program carrying a block; byte-identical otherwise.**
A version 6 consumer Kahn-orders the published edges, so it would either
refuse the program by name or — if it executed the published order — move
the machine by the amounts `proposal.md`'s table records. ADR-057's rule
gives such a document the version its content needs; a document whose
program has no block keeps declaring 5 or 6, byte for byte.
`serializer.document_version` (`serializer.py:432`) gains a
`_carries_a_block` beside `_reads_its_own`, and 7 dominates 6 (a block
says nothing about self-reads and a self-read says nothing about blocks).

**The members are published as ORDINARY EDGES, contiguous at the block's
position, in the block's own deterministic order.** The compound edge is
a producer-internal representation and appears nowhere in the document.
This keeps every existing rule of "The published edges say what each one
reads, gives and computes" literally true — a law edge still carries
`expressions`, `affine` and `plans`, and its expressions' free names are
still exactly its `needs`.

**NO new document key.** A consumer re-derives both facts from what is
already published:

- **the block**: the strongly connected components of the graph over the
  edges' own `needs` and `gives`, with `needs ∩ gives` excluded — the
  same exclusion a version 6 consumer already makes for the self-read;
- **the selectors**: for each law edge's plan, a jump whose `level`
  expression — with placeholders resolved transitively into their own
  jumps' levels — names no id the block `gives`. The published plan
  already carries `level` per jump (`program.py:3026`, and the export
  requirement names it), so nothing is missing.

A key was considered and rejected: publishing the block membership and
the selector names would be publishing a DERIVATION, and ADR-110's line
is that the document carries what compile time DECIDED and not what is
computable from it (`sources` and `constraints` sit on opposite sides of
that line today, `sources` published because it is a compile-time
decision about candidates and `constraints` derived and not published).
Membership and selectorhood are both functions of the published edges.

**What "IN PROGRAM ORDER" means for a block.** The order is a Kahn order
of the program with each block CONTRACTED to one node; a block's members
appear contiguously at that node's position, in the producer's own
deterministic order. A consumer SHALL NOT execute the members in the
published order: it re-derives the block, locates its selectors'
crossings, and orders the members per piece, as the producer does. The
published order is an identity and a listing, not an execution order —
which is precisely the breaking part of version 7 and why it gets a
version rather than a flag.

**The corpus** gains three features, stated in
`tools/generate_running_corpus.py`'s `REQUIRED` tuple so the generator
REFUSES to write a corpus that lacks one, each derivable from the
document and the tick log exactly as the existing entries are:

- `'a switched source'` — a published law edge with an in-block
  dependency;
- `'a selection crossing inside a tick'` — a tick whose `crossings` name
  a jump node that is a selector of a block member;
- `'a tick carrying both a selection crossing and a stop'`.

Item 7 of the requirement note — paired replay through the independent
viewer — is discharged by the viewer's own cycle in its own repository,
against this corpus. This cycle records the producer-side content commit.

### 10. Cost

**With no block: nothing.** The pre-pass of §5 is one walk of the
records and one Tarjan over a graph with no nontrivial SCC, at
construction. Per tick there is no block edge, so there is no extra
test in `_pass` at all. The `Train` bench's measured `1.05 ms/tick`
(`docs/architecture.md`) must be unchanged; note that no TEST pins it —
it is an evidence number, and this cycle re-measures it rather than
asserting it.

**With a block.** Per stretch: one selector partition, whose cost is
ADR-107's `_partition` over the block's selector nodes only. Per piece:
one fold-and-Kahn (memoised per branch vector, so a stretch crossing one
selector costs two) plus one evaluation of each member over the piece.
A stretch cut into `p` pieces therefore costs about `p` times the
members' ordinary cost — the expected dominant term for a Curta tick at
`dt = 0.02`, where `p` is 1 for almost every tick and 2 on the tick a
detent is crossed.

**The expensive case, named.** A stop on a BLOCK coordinate is SEARCHED
(§7): up to `_SUBDIVISIONS` (64) plus `_BISECTION_ROUNDS` evaluations of
the WHOLE block, each of which relocates the selector partition. The
expectation is that this is the one shape a Curta-scale model must be
measured on, and it is measured rather than assumed.

**The measurement plan.** A bench beside the `tests/carriage_project/`
fixture, `dt = 0.02`, `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, one
job at a time: (a) a full crank revolution at a fixed carriage position,
no block coordinate declaring a range; (b) the same with a range on a
dial, so every tick that reaches it pays the search; (c) a tick in which
the carriage crosses a detent; (d) the `Train` bench unchanged, as the
control. Reported as ms/tick beside the architecture's existing numbers,
recorded in the change's evidence, and compared against the same
fixture's members run as three separate edges with the carriage frozen —
which is the honest baseline, because that is the machine the project
can build today.

### 11. What changes, by function name

- `solid_node/simulation/sim.py` — the running branch of `__init__`
  (`sim.py:151-159`): a pre-pass marking block members, between
  `release_tree(node)` and `self._bind_initial(state)`.
- `solid_node/motion/couplings.py` — `_step_relation`: skip a marked
  record where it skips a self-read.
- `solid_node/simulation/program.py` — a `_block_members(root)` pre-pass
  helper shared with `sim.py`; `_Selection` on a plan (the selector set
  and the fold); `_relation_edge` recording it; a `_Block` reading and a
  compound `block` `Edge` kind with `increments`, `cuts`, `values` and
  `affine` as §3 states; `compile_program` grouping the marked edges;
  `_ordered` contracting each block and keeping today's message for a
  cycle no selection breaks; `Program.described` emitting the `block`
  line and then its members' ordinary lines; `Program._placeholders` and
  `Program.published` expanding a block into its members contiguously;
  `release_tree` clearing the marks (below).
- `solid_node/simulation/program.py`, the two forcing points — the ONLY
  places a forced selector is read (§3): `JumpPlan._partition`
  (`program.py:397`) skips locating a forced node's crossings, and
  `JumpPlan._branches` (`program.py:345`) returns the forced value.
  `_Retained.outer` is a `JumpPlan`, so `_Walk._outer` and
  `_Walk._outer_branches` inherit both, and `_decide`, `_tentative`,
  `_probe`, `_crossing`, `_searched`, `_bisect`, `_skeleton`, `_level`,
  `_land` and `_far_side` read the forced branch out of the `branches`
  map they are already given. No other function changes.
- `solid_node/simulation/run.py` — no structural change, and F11 and the
  forcing points above are what keep that true: `_pass`, `_locate`,
  `_searched`, `_along`, `_group`, `_pushes` and `_landed` meet the block
  through the `Edge` interface they already call.
- `solid_node/core/serializer.py` — `BLOCK_DOCUMENT_VERSION = 7`,
  `_carries_a_block`, `document_version`.

**The marks are per-RECORD and therefore outlive a render, which
`release_tree` has to answer.** `resolve_declared_relations`
(`couplings.py:1785`) stores `node.__dict__['_relations']` ONCE, at the
end of the instance's construction — not per render — so a mark written
on a record is still there for the next simulation over the same tree.
Two consequences, both stated so neither is discovered later:

- `release_tree` (`program.py:3076`) CLEARS the marks alongside the
  run's claim on the tree, and the pre-pass is IDEMPOTENT — it recomputes
  membership from the records and rewrites the marks, so a second `Sim`
  over a shared tree (`ScenarioTest.simulation()`'s "fresh per call")
  behaves exactly as the first.
- A later NON-running `Sim` over the same tree never calls
  `release_tree`, so stale marks could in principle survive into it —
  except that `_step_relation`'s marked branch, like its self-read
  branch, is guarded by `_under_running_root(record)`. Under any other
  time base a marked record is solved, deferred and refused exactly as
  it is today. Both halves are tested (task 3.6).

### 12. What the Curta must do to migrate (project work, named here)

Not this cycle's work, and named so the project's agent does not have to
re-derive it:

- Every association becomes a COMPARISON FACTOR on the carriage's own
  JOINT coordinate `registers.turn`, not on the `position` driver:
  `position.drives(registers.turn, ratio=20)` already exists
  (`simulation/mechanism.py:186`), and reading the joint is what makes
  the selection follow the part rather than the request.
- The existing pose model's selector is `1 − clamp01(|place − channel −
  shift|)` (`simulation/transmission.py:24`) — a triangular hat built on
  `clamp01`, which is a CALL and therefore not a jump node at all. It
  must be rewritten as a pair of comparisons (`here >= k − .5` and
  `here < k + .5`) for the compiler to see a selector. This is the single
  most likely migration trap and the reason it is written down.
- The carriage LIFT is a second selector factor on every association, so
  a lifted carriage drives nothing.
- Every dial and every carry lever needs a guarded REST DEFAULT in its
  own `simulate()`, because a block relation binds nothing at rest.
- The latch's hysteresis and each dial's missing-tooth gate stay ADR-121
  self-reads of their own coordinates, inside the same laws.
- The interlock ("no shift unless lifted", "no crank unless seated")
  stays an ADR-113 `Bound(..., reads=)` on the carriage coordinate.

## Risks / Trade-offs

- **A run-time refusal is new.** Until now a running model that
  constructed could only refuse a tick for a conflict, an over-crossed
  law or an unintegrable level. A piece whose active graph is still
  cyclic is a fourth. It is transactional and names the selection, but
  it is a failure mode an author can only meet by running. Mitigated by
  §2's construction check, which catches every cycle no selection can
  break; not eliminated, because eliminating it means solving for which
  branch vectors are reachable.
- **The over-broad candidate table.** `Program.sources` treats a block
  as one node, so every input reaching any member is a candidate for a
  stop on any other. `_pushes` filters it per tick, so the ANSWER is
  right; the cost is one extra propagation per spurious candidate on a
  blocking tick only.
- **The compile-time check is necessary, not sufficient** (§2), stated
  rather than hidden.
- **A block is opaque to `_locate`'s affine path**, so every stop on a
  block coordinate is searched (§10). A later cycle could classify a
  block give as affine under a fixed branch vector; this one does not.
- **Membership is computed twice** — once in the pre-pass over records,
  once at compile over edges. The two agree BY CONSTRUCTION under §5's
  rule and not by luck: the pre-pass keeps only an SCC holding a BANKED
  driven end, `_reaching_the_bank` (`program.py:2917`) drops a candidate
  only when NO driven end reaches the bank, and §2 refuses an
  intermediate among a block's gives. The implementation asserts it
  rather than trusting the argument, and a disagreement is an internal
  error naming both sides. The shape the earlier draft would have got
  wrong is named in §5: an SCC of plain-port relations the compile drops,
  marked for a block that is never compiled, would have fired that
  assertion on a model that works today.
- **A `sign`-gated source is never switched** (§2), so a model that gates
  its only conditional dependency on `sign` is refused at construction
  with the cycle message rather than admitted. That is the intended
  answer — `sign`'s zero is one point, so such a gate is active on every
  real piece — but it is a shape an author could reasonably expect to
  work, and the refusal message has to say why. Recorded as a follow-up
  in case a mechanism ever asks for it.

## Open Questions

- Whether the `block` line in `described()` should also name the
  SELECTOR ids, so that a change in which jump nodes qualify is visible
  in the identity independently of the expression change that caused it.
  The expression change already moves the identity, so this is
  redundancy, not coverage; deferred.
- Whether a block give could be marked affine per branch vector, turning
  the searched stop of §10 into `_piecewise`. Deferred to a follow-up
  with a measurement behind it.
