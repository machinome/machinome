## Context

solid-node's ADR-122 (`select-the-source`, framework commit `0b0f02a`)
compiles a cycle every selection breaks as a **BLOCK** and orders it once
per PIECE of a tick instead of once per program. This cycle makes the
browser viewer execute such a program, against the corpus that change
regenerated. It is the consumer half of ADR-110/111: one published
program, one conformance corpus, two runtimes that are one algorithm.

Everything here mirrors `solid_node/simulation/program.py` at `0b0f02a`
function for function, as `jumps.ts`, `edges.ts` and `run.ts` already
mirror `JumpPlan`, `Edge` and `Run`. **Where this document and ADR-122
disagree, ADR-122 is right; where the TypeScript and `program.py`
disagree, `program.py` is right.** The corpus is the contract.

### What the producer publishes, and what it does not

A version 7 document carries **no new key**. `Program.published` emits a
block's members as ORDINARY law edges, contiguous at the block's position
in the producer's own deterministic order (`program.py:1871-1886`,
`Program.listed`), and that order is a LISTING and not an execution
order. A consumer re-derives:

- **the block**: the nontrivial strongly connected components of the
  graph over the edges' own `needs` and `gives`, with `needs ∩ gives`
  excluded — the same exclusion this viewer already makes for the
  self-read (`program.ts:803-881`);
- **the selectors**: per member, the jumps of its plan whose published
  `level` — placeholders resolved transitively into their own jumps'
  levels, and binding names closed over the document's own table — names
  no id the block gives.

ADR-110's line is why: the document carries what compile time DECIDED,
not what is computable from it. `sources` is published because it is a
decision about candidates; `constraints` is derived; membership and
selectorhood are functions of the published edges, so they are derived
too.

### What this viewer does today, exactly

`loadProgram` (`program.ts:321-968`) **reads no version number, performs
no ordering and detects no cycle**. It validates each published edge,
inverts `gives` into `determiner` (`program.ts:715-718`), and hands
`Run.pass` (`run.ts:526-553`) the published array to walk once per
stretch. So the engine executes the LISTING. The version gate that keeps
a version 7 document out of a real page is `RENDERED_VERSIONS`
(`viewer.ts:1824`) in `assertRenderable` (`viewer.ts:1933-1942`) — a
document-loader gate, not a program-loader one, and the corpus suite
reaches `Engine.load` without passing through it.

That gate is the ONLY thing between this viewer and a silently wrong
machine, and the size of the wrong is measured in `proposal.md`: one tick
of `ShiftedCarry` at `dt = 1.0` commits `higher.turn = 0` where the
producer commits `1.0`, and `1` if the two members had been listed the
other way round.

## Goals / Non-Goals

**Goals**

- Execute a version 7 document exactly as `program.py` at `0b0f02a` does,
  and prove it against the framework's own 19-scenario corpus.
- Re-derive the block and its selectors from the published edges, with no
  new key demanded of the producer and nothing new published by anybody.
- Refuse at LOAD, by name and quoting the document, every shape the
  producer refuses at CONSTRUCTION; refuse at TICK, transactionally and
  word for word, the piece the producer refuses at tick.
- Leave a document with no block byte-identical in behaviour, cost and
  code path — including every version 5 and 6 document the viewer
  executes today, save for the one ulp the walk's parenthesisation fixes.
- Run the Curta's own carriage in a real browser, at the framework's own
  step size, against the framework's own numbers.

**Non-Goals**

- No change to the published document, to the framework, or to the
  entry-point contract between the two packages.
- No re-derivation of anything the producer publishes: `affine` on a
  non-block edge, `sources`, `limits`, the plan postorder and the edge
  order are READ (ADR-047), never recomputed.
- No consumer counterpart to the producer's construction-time pre-pass,
  its rest rule, `MembershipInvariantError` or `release_tree` (D1.7).
- No classification of a block give as affine under a fixed branch
  vector; the producer recorded that as a follow-up with a measurement
  behind it, and so does this.
- No attempt to decide which branch VECTORS are reachable. That is a
  satisfiability question — a solver — and it is why the load-time check
  is necessary and not sufficient and a genuinely cyclic piece is refused
  at run time.

## Decisions

### D1. The block is re-derived at LOAD, and what cannot be one is refused there

`loadProgram` gains a pass, after the edges are validated and after the
self-read reading is derived, that turns the published list of law edges
into the list the engine executes.

**D1.1 The components.** Over the validated edges in published order:
edge A precedes edge B when B `needs` a key A `gives`, with a need an
edge itself gives EXCLUDED. Tarjan, **iterative** (a deep chain must not
exhaust the JavaScript stack any more than it may exhaust the
interpreter's), with every adjacency list built in the published order,
components emitted with their members sorted and the components sorted by
their first member — `_components` (`program.py:3474-3501`) and
`_strongly_connected` (`program.py:3794-3833`) reproduced. A component of
one edge is not a block and changes nothing.

A `check` edge determines nothing, so it has no outgoing adjacency and
can never be in a component; it is left exactly where it is published.
(The generator's own consumer-side re-derivation drops checks before
building the graph, `tools/generate_running_corpus.py:453-470`; excluding
them by `gives` being empty is the same set.)

**D1.2 The contraction, and what happens when the listing is not
contiguous.** Each nontrivial component becomes ONE derived edge of a new
kind, `block`, placed at the index of its FIRST member; every other edge
keeps its published position and its relative order. That is
`_blocked` (`program.py:3503-3536`) exactly, and on a well-formed
document it reproduces `Program.published`'s own order with the members
folded back up.

The loader then **verifies** that the contracted sequence is a
topological order of the contracted graph — every edge's needs, minus
what it gives itself, are given by an earlier entry or by no entry at all
— and refuses the document by name if it is not:

> `<source>` declares document version 7 and its published edges are not
> in an order this engine can execute: `<description>` reads
> `<id>`, which `<description>` determines LATER in the published
> listing. The published order of a program's edges is the order it runs
> in, with a block's members contracted to one entry; a consumer that
> re-sorted them would be inventing an ordering decision the producer
> already made.

**Rejected: Kahn-order the contracted program ourselves.** It is what the
producer does (`_ordered`, `program.py:3606-3630`) and it would silently
accept a document whose published listing disagrees with its own content
— which is precisely the failure version 7 exists to make loud. This
viewer reads the order compile time decided (ADR-047) and checks it;
re-sorting would make the engine's answer a function of the consumer's
tie-breaking rather than of the document. The check costs one pass and
turns a malformed producer into a named refusal instead of a different
machine.

**Rejected: trust contiguity.** The published members ARE contiguous
today. Relying on it would make a hostile or future document reach the
tick with a block whose members the engine never grouped, which is the
one shape that must not happen quietly.

**D1.3 `kind: "block"` is derived and never read.** `EDGE_KINDS` stays
`law | wiring | formula | check`: a document publishing an edge of kind
`block` is refused as an unknown kind exactly as today. The block entry
is synthesised by the loader, carries the union of its members' `needs`
in first-seen order and all their `gives` (`_block_edge`,
`program.py:3538-3550`), its `description` is the members' descriptions
joined with `'; '` and its `statedBy` their classes de-duplicated in
order — so every refusal that prints an edge prints the block's members.
Its `affine` is `false` for every give (D4.2).

**D1.4 The selectors.** Per member, over its one plan's jumps in the
plan's published (postorder) order — `_selectors`
(`program.py:1245-1266`) reproduced:

```
reaches = new Map<string, boolean>()
for each jump in plan.jumps:
    names   = namesOf(jump.level)          // bindings CLOSURE
    touches = any(name ∈ blockGives for name in names)
           or any(reaches.get(name) === true for name in names)
    reaches.set(jump.name, touches)
    if not touches: selectors.push(jump)
```

`namesOf` is the loader's existing `table.closure(freeVariables(...))`,
the same one ADR-057's dependence uses and for the same reason: a level
written `_b2` reaches `shift` only through the bindings table, and a
viewer reading `freeVariables` alone would misclassify it. Measured on
the corpus: every level of both new machines' selectors is `_b2`, a
binding for `(shift - 0.5)`.

The relation is upward closed along the nesting because a placeholder
stands for exactly the subtree it replaced, and the plan lists its jumps
in postorder, so an inner node is decided before the node it sits in.

A node whose level reads the member's OWN driven end is not a selector —
the own end is one of the block's gives — so it stays exactly where
ADR-057 put it, in the walked layer inside the piece. That is what makes
the Curta lever's selector (on the carriage) and its latch (on its own
travel) compose.

**D1.5 The fold, as a traversal rather than a rewrite.** The producer
substitutes numbers into the skeleton, folds `x*0→0`, `0*x→0`, `0/x→0`,
`0+y→y`, `y+0→y`, `y−0→y`, `0−y→−y`, and takes the free names
(`_folded`/`_reads_under`, `program.py:1177-1243`). The viewer needs only
the NAMES, never the folded tree, so it computes them in one bottom-up
pass over the hash-consed expression DAG, returning per node a pair
`(isZero, names)`:

| node | pair |
| --- | --- |
| a name in the substitution | `(value === 0, ∅)` |
| a constant `0` | `(true, ∅)` |
| `a * b` | either zero → `(true, ∅)`; else `(false, A ∪ B)` |
| `a / b` | `a` zero → `(true, ∅)`; else `(false, A ∪ B)` |
| `a + b` | `a` zero → B; `b` zero → A; else `(false, A ∪ B)` |
| `a − b` | `b` zero → A; `a` zero → `(false, B.names)`; else `(false, A ∪ B)` |
| unary `−a` | `(false, A.names)` |
| any other name | `(false, {name})` |
| anything else | `(false, ∪ children)` |

which is the producer's rules read for their effect on names. Two rows
are deliberately NOT zero-propagating, because the producer's `is_zero`
(`program.py:_folded`) is true only of a NUMERIC LITERAL: `0 − y` becomes
a `unary` node, never a literal, so its pair is `(false, B.names)`
whatever `y` is, and a unary minus over a zero stays a unary node for the
same reason. "A constant `0`" means a literal whose numeric value is zero
in any spelling (`0`, `0.0`, `-0.0`), as the producer's `float(text) == 0.0`
reads it. The table is monotone for the producer's own reason: every rule either removes names
or keeps exactly the names its operand had, and a call's names are the
union of its arguments'. A substituted placeholder contributes no names
whatever its value, because the producer replaces it with a numeric
literal.

`readsUnder(plan, substitution)` then takes the folded skeleton's names
and follows every SURVIVING placeholder into its OWN folded level,
transitively, closing each through the bindings table — `_reads_under`
exactly.

This needs one read-only structural accessor exported from
`expressions.ts`, where the DAG store lives, giving a node's kind,
operator and child ids. **Rejected: a second expression parser in
`run/`.** A copy drifts from the one the evaluator uses at the first
correction either receives, which is the failure the corpus exists to
prevent; the same argument `jumps.ts` gives for reusing `partition`
rather than copying it. **Rejected: rewriting the tree and re-preparing
it.** It would mint DAG nodes at load for an answer that is a set of
strings, and `expressionGeneration` would have to be respected for a
value nothing evaluates.

**D1.6 Unconditional, switched, and the one all-zero fold.** Per member,
with `own` its single give:

- `zero` = `{placeholder: 0 for every selector whose primitive is
  FOLDABLE}`, where FOLDABLE is `floor`, `ceil`, `%` and the six
  comparisons — and NOT `sign`. `sign`'s zero branch is the single point
  where the level is exactly `0.0` (`branchOf`, `jumps.ts:63-65`), not an
  interval, so a `sign`-gated source counted as switched would admit at
  load a machine every tick refuses.
- `whole` = in-block ids among `readsUnder(plan, {})`, minus `own`.
- `least` = in-block ids among `readsUnder(plan, zero)`, minus `own`.
- `unconditional[i] = least`; `switched[i] = whole − least`.

The producer's `_Block.__init__` (`program.py:1268-1320`). `own` is
excluded from both because a read of a member's own driven end is
ADR-121's self-read, not a wait on anything else — the same exclusion the
graph of D1.1 makes. A member with NO plan carries no selector at all, so
its unconditional set is simply its in-block needs minus its own.

ONE fold per member answers both questions the load asks, because the
fold is monotone and the all-zero assignment is therefore the minimum
over every assignment. **Rejected: a search over `2^n` selector
assignments**, for the producer's reason: it invites `2^n` folds per
member and leaves the load's cost undefined.

**D1.7 What the loader refuses, by name.** `_refuse_unselectable`
(`program.py:3552-3589`) and `_Block.unconditional_cycle`
(`program.py:1328-1350`) reproduced, each message naming the edge, its
`statedBy`, and every member of the block:

1. **A wiring or a formula on a cycle.** Neither carries a jump node, so
   no selection can switch what it reads.
2. **A member driving a GROUP** — more than one give. What a selection
   switches is decided per driven end off that end's own skeleton, while
   a group's ends are claimed and bound together.
3. **A member whose give is not a bank coordinate.** A block advances its
   coordinates piece by piece inside a tick and hands the run an absolute
   landing for each; only a coordinate the run banks keeps that history.
4. **A cycle no selection can break** — the block's UNCONDITIONAL graph
   still has a cycle. The producer's `_cycle_message`
   (`program.py:3591-3604`) word for word, including the sentence saying
   what a switch would be and that `sign` is not one.

The producer never publishes such a document, and that is exactly why the
loader is the guard: a consumer that met one of these first at tick time
would meet it while a frame was being drawn. This is the surface the
viewer already stands on — "Every shape the engine cannot execute is
refused HERE, when the document is loaded" (`program.ts:23-25`).

**D1.8 What has NO consumer counterpart, said out loud.** The producer's
pre-pass over the records (`_block_members`, run at `Sim.__init__` before
the rest render), its rest rule (a block relation binds nothing at rest),
`_agree_on_membership`/`MembershipInvariantError`, and `release_tree`'s
mark handling are all about CONSTRUCTING a tree. This viewer constructs
nothing: the document's `coordinates[].initial` already carries the rest
bank the producer's rest render produced, and `loadProgram` reads it
(`program.ts:407-421`). There is exactly one reading of membership here,
so there is nothing to assert equal to a second one.

**D1.9 A version 7 document with no block.** Nothing in this pass tests
the version number. A document declaring 7 whose edges hold no nontrivial
component produces no block entry and takes the version 5/6 path
unchanged — the same stance the viewer already takes for a version 6
document carrying no self-read edge ("the version is a property of the
content the producer published, and this viewer judges the content").

### D2. A tick runs a block PIECE BY PIECE

`_Block.increments` (`program.py:1352-1418`) reproduced as
`blockIncrements(program, block, values, deltas, crossings, tick,
landings)`, reached from `edgeIncrements` on `kind === 'block'`.

**D2.1 The selector partition, located FIRST, over the whole stretch.**
Per member, a plan of that member's SELECTORS ALONE over the member's own
published skeleton — `{skeleton: plan.skeleton, jumps: selectors}` — is
handed to the existing `partition` (`jumps.ts:399-446`) with the member's
`start`/`delta` maps, its description and its driven id. Its crossings
are recorded (under that member's description and coordinate, located
over the whole stretch) and its interior cuts merged into one running cut
list with the existing `merged`, in the members' own order and each
member's postorder. `_Block._partition` (`program.py:1420-1436`).

Every selector's level reads only coordinates the block does not give, so
its path over the stretch is the linearisation `values + deltas·t` that
`along` already builds — the same arithmetic the member's own plan would
use for that node. Nothing new locates anything.

**D2.2 The branches, read at the piece's MIDPOINT.** Per piece
`[left, right]`, `_Block._forced` (`program.py:1438-1449`): the same
selector-only plan's `branchesAt` at `(left + right) / 2`, giving one
`{placeholder: branch}` map per member. ADR-107's own rule, valid for
ADR-107's own reason.

**D2.3 The order, memoised by the branch VALUE vector.**
`_Block._order` (`program.py:1451-1477`): per member,
`readsUnder(plan, forced[i])` — the RUN-TIME fold, actual branch values
substituted, not the load's all-zero one — restricted to the block's
gives is that member's ACTIVE graph on this piece; Kahn over it, with a
member's own give ignored, gives the order.

The memo key is the vector of actual branch VALUES, not of booleans:
`branchOf` returns an integer for `floor`, `ceil` and `%`, so a crank
passing three tooth windows in one tick gives three different keys. In
JavaScript the key is built by sorting each member's `[name, value]`
pairs and joining them; `branchOf`'s `whole()` already normalises `-0` to
`0` (`jumps.ts:44-46`), so the two zeros cannot key two entries.

**D2.4 A still-cyclic piece refuses the tick, transactionally.**
`_Block._refused` (`program.py:1479-1495`) word for word:

```text
over the piece [<left>, <right>] of this tick the relations <members>
form a cycle the run cannot order: each waits on a coordinate another
determines, and the selection this piece was read under leaves every
dependency on this cycle active. The selectors read <name>: <primitive>
on <level> reads <value>; …. The tick committed nothing: the bank, the
tick count and the tree stand as they were.
```

The WORDS are the producer's; the FLOATS are spelled by each runtime —
Python's `repr` writes `1.0` where JavaScript's `String` writes `1`, and
neither runtime ever sees the other's message (a refusal is not corpus
state). The tests therefore assert the message's shape and the numbers it
names, not byte equality with a `repr` this runtime cannot produce.

It is an `UnsupportedLaw`, so `RefusalKind` gains nothing and it reaches
the page through `protocol.ts` exactly as a conflict does. `Run.integrate`
already catches `UnsupportedLaw` around the whole segmented tick
(`run.ts:468-478`) and calls `refuse(moved)`: no new rollback is written.

The two numbers in `[<left>, <right>]` are the piece's fractions of the
STRETCH, as the producer prints them, and the float formatting must match
the producer's `repr` for the message to be word for word; the levels are
the published `level` strings.

**D2.5 The members, run over the piece, in that order.** For each member
in the piece's order, over its own `needs`:

- a key the block does NOT give: start `values[k] + deltas[k]·left`,
  delta `deltas[k]·(right − left)`;
- a key the block DOES give: start = the BLOCK-ADVANCED value it holds at
  this piece's start, delta = the increment computed for it ON THIS PIECE
  (`0` if this piece's order has not reached it yet).

Then `memberIncrement` — `_integrated` (`program.py:1517-1536`) — which
is the member's existing machinery with `forced` passed: no plan → the
difference of two evaluations; a plan and no self-read reading →
`planIncrement`; a self-read reading → `retainedIncrement`, returning
`(increment, landing)`.

The block accumulates `total[own] += increment`, and advances
`advanced[own] = landing ?? advanced[own] + increment`, remembering
whether it landed.

**The in-block value MUST be advanced between pieces.** The producer
measured the negative control rather than asserting it (`spikes/pieces.py`:
three pieces of one stretch sum to `1.0` advanced and `2.0` not), and
this cycle mirrors that measurement as a test.

**A switched-out source this piece has not determined is handed its
block-advanced value with a delta of `0.0`.** Safe without a tolerance,
for the producer's three reasons: every term reading it is multiplied by
a placeholder the block FORCED to zero, so the float is multiplied by
zero; a non-selector node whose level reads only such a source has a
constant level and a constant level crosses nothing (`crossingsOf`
returns `[]` the moment `high === low`, `jumps.ts:337`); and a
switched-out source determined EARLIER in this piece's order is handed
its real piece increment, not zero.

**D2.6 Crossings.** A member's crossings are collected per piece into a
fresh list and rescaled `left + t·(right − left)` before being added to
the block's located list — the same map `record` (`run.ts:1117-1125`)
then applies from the segment to the tick. When every piece is done, the
whole located list (selector crossings located over the stretch AND
members' own crossings rescaled out of their pieces) is **sorted by
fraction** and only then extended onto the caller's list, so the listing
does not depend on which was computed first.

**D2.7 The two-argument call shape.** `Run.along` (`run.ts:923-936`) and
`Run.pushes` (`run.ts:955-972`) call `edgeIncrements` with
`crossings = null`, `tick = 0` and no landings. A block's increments must
therefore be complete and side-effect-free with all three absent — it
records no crossing, reports no landing and mutates nothing — **and must
still refuse a genuinely cyclic piece**, under the SAME midpoint reading
and the SAME ordering it uses inside the tick. A probe that refused where
the tick would not, or ran where the tick would refuse, would make a
stop's blocked group a function of the probe rather than of the machine.

### D3. A selector is a CONSTANT on the piece: the `forced` map

Forcing reaches exactly TWO points, and everything else inherits it —
`program.py`'s own §3 finding, and the reason the walk needs no second
copy:

- `partition` (`jumps.ts:399`) **skips** locating a forced node's
  crossings. The block located them over the whole stretch already, and
  re-locating them inside the piece is the second reading this design
  exists to remove.
- `branchesAt` (`jumps.ts:288`) returns the FORCED value for a forced
  placeholder instead of evaluating its level.

`planIncrement`, `planCuts`, `retainedIncrement`, `retainedCuts` and the
`Walk` constructor gain an optional `forced` argument and pass it down.
`Walk.outerCuts` and `Walk.outerBranches` are `partition` and
`branchesAt` over the independent layer, so `decide`, `tentative`,
`probe`, `firstCut`, `crossing`, `searched`, `bisectTo`, `land`,
`farSide`, `skeletonAt` and `levelOfJump` all read the forced branch out
of the `branches` map they are already given. **No other function
changes.**

That a selector is always an INDEPENDENT node in ADR-057's split is not
an assumption but a consequence: a selector's level reads nothing the
block gives, the member's own driven end included, so it can never be
dependent. The split itself stays decided at LOAD with the selectors
still symbolic — forcing could only move a node from dependent to
independent, and taking that improvement would make the split a property
of the piece and force the two-layer reading to be rebuilt per piece.

**Rejected: let each member RE-LOCATE the selector's surface inside its
own piece.** The two readings agree in the ordinary case, and the
argument from `surfacesOf(..., inclusive=false)` and `merged`'s tolerance
is sound — but it is an argument about ulps at a cut that becomes false
for a short enough piece: `merged` folds cuts closer than the crossing
tolerance IN THE FRACTION of the path being cut, so a level recomputed a
few ulps on the wrong side at the left end of a piece of width `1e-9` is
a genuine cut at relative position `1e-3`, and the member would integrate
part of that piece under the branch the block did not order it under.
Substituting the branch removes the question rather than bounding it, at
one map entry per selector per piece.

### D4. What a block reports, and what it is asked

**D4.1 The landing is the ADVANCED ABSOLUTE at the stretch's end**, not
the last landing: for every coordinate any piece landed, the block
reports the value it has itself advanced that coordinate to by the
stretch's END — the landing plus every later piece's increment. A
coordinate no piece landed is reported as an increment only.

`Run.landed` (`run.ts:518-521`) OVERWRITES `value + delta` with a
reported landing, so reporting the landing of piece 2 while piece 3 moved
the coordinate further would commit the landing and DISCARD the motion.
The producer measured this by reverting to the other rule (`1.0 != 3.0`),
and this cycle mirrors that as a test on `LandedCarry`'s shape.

**D4.2 `affine` is FALSE on every give of a block.** A block's value is
piecewise in the selector partition AND re-ordered across it, so
`Run.locate` (`run.ts:834-861`) must take `searched` and never
`piecewise`. This is not a refinement: it is the measured cause of the
one corpus scenario that fails on this base, where the MEMBER's published
`affine: [true]` sends a stop on `carry.travel` down the piecewise path
and commits `spin` at `0.6` where the producer commits
`0.5999999999994543`. `Edge._affine_ends` (`program.py:1605-1610`).

The cost is stated rather than discovered: a stop on a block coordinate
is up to `subdivisions` samples plus `bisectionRounds`, each of which
re-locates the selector partition and re-runs the whole block. It is the
expensive case and D9 measures it.

**D4.3 `cuts` on a block** is the selector partition — `_Block.cuts`
(`program.py:1497-1515`). `Run.locate` reaches `edgeCuts` only through
the affine path and a block's gives are never affine, so nothing calls it
today; it is defined rather than left to throw, because `piecewise`
becomes meaningful over it the day a later cycle classifies a block give
as affine under a fixed branch vector.

**D4.4 `values` on a block is nothing.** `edgeValues` returns `[]`, and
`Run.valuesOf` (`run.ts:586-600`) never asks: it skips an edge all of
whose gives are bank keys, and every give of a block is a bank
coordinate by D1.7's third refusal. `Program.values_of`
(`program.py:1459`) skips it on the same test.

**D4.5 `sources`, `determiner` and the sub-program.** `sources` is
published and is already the union over a block's members — the producer
treats a block as one node, so the candidate table is deliberately
over-broad and the ANSWER is still right because `Run.pushes` filters per
tick. `determiner` maps each give to `{edge: theBlock, index}` where
`index` is that give's position in the block's `gives`, which is what
`Run.locate` reads `affine[index]` and `edgeCuts(..., index)` by. The
constraint sub-program (`program.ts:891-904`) filters `edges` in program
order and therefore takes the whole block or none of it, which is the
right granularity: a block's members are inseparable within a tick.

**D4.6 `Run.pushes`'s break is checked, because the answer depends on
it.** `pushes` (`run.ts:955-972`) runs an edge and then breaks on
`edge.gives.includes(key)`. With the block as ONE entry, `gives` holds
every member's give, so the break happens AFTER the whole block has run
under that one input's displacement — which is what makes an input
coupled to a stopped coordinate only through an INACTIVE selection
contribute nothing and not be stopped. It would NOT be true if the
members were separate entries with the probe stopping at the first to
name `key`. Its guard, `edge.needs.some((need) => deltas[need])`, reads
the block's union of needs and is therefore right by D1.3.

### D5. The walk's own arithmetic, parenthesised

`Walk.run`'s `ownAt` closure (`jumps.ts:566-567`) computes
`from + this.skeletonAt(s, branches) - base` and `Walk.probe`
(`jumps.ts:700`) computes `ownLeft + this.skeletonAt(s, branches) - base`.
JavaScript, like Python, takes those left to right as
`(own_left + S) − base`, which rounds whenever `|S|` is comparable to
`|own_left|`: a piece whose skeleton does NOT move still shifts the
coordinate by an ulp. Both become `ownLeft + (S − base)`, as
`_Walk.run`/`_Walk._probe` now do (`program.py:809-821`, `919-930`).

This is a behaviour change for **version 6 documents too**, and it is
fixed here rather than separately because ADR-122's "a selection change
alone moves nothing" is a BIT-FOR-BIT promise that cannot be asserted
while the walk adds an ulp of its own — the Curta acceptance asserts
exactly that across a lift/shift/drop.

The corpus does not move: the producer regenerated it AFTER this fix and
every pre-existing entry is byte-identical (`proposal.md`'s byte
comparison: `changed: []`). So the seventeen scenarios this viewer
already replays must stay green over it, which is the regression test.
The red-first test is the producer's own `HeldAngle` shape on a version 6
document with no block anywhere: a crank standing at `72.0`, a wheel
resting at `71.99999999999996`, a lift moved alone — `71.99999999999994`
before, `71.99999999999996` after.

### D6. The commit path does not change in shape

`run.ts` gains nothing structural, and the claim has a reason: the
producer's `run.py` gained nothing either. `pass` walks
`this.program.edges`, which now holds a block where a run of members
stood; `landed` applies whatever `landings` holds; `locate` reads
`affine[index]` and takes `searched`; `along`, `groupOf` and `pushes`
call `edgeIncrements`. The block meets all six through the edge interface
they already call.

The one new failure mode is D2.4's cyclic piece, an `UnsupportedLaw` at
TICK time: transactional, caught with the other five in
`Run.integrate`'s `catch`, reaching the page as `refusalKind` `'law'`.
`RefusalKind` (`program.ts:82-83`) is unchanged.

### D7. Versions

- **`documentVersions` becomes `[1, 2, 3, 4, 5, 6, 7]`** in
  `widget/package.json`, the ONE declaration `vitest.config.ts`,
  `build.mjs` and `bundle.py` all read; `RENDERED_VERSIONS`
  (`viewer.ts:1824`) follows, and `version.test.ts` pins them together.
- **`solidNodeViewerApi` rises 15 → 16.** Executing a version 7 document
  is a capability a host may require BEFORE it mounts, because unlike a
  `controls` table or a `markings` list it is not additive: a build at 15
  refuses such a document by name and renders nothing at all. The
  precedent is exact — `execute-the-self-read` raised 14 → 15 when
  `documentVersions` gained 6.
- **`bundle.py`'s `RELEASED_DOCUMENT_VERSIONS` does NOT move.** It is
  `[1, 2, 3, 4]` (`bundle.py:53`), the list a consumer that receives no
  `documentVersions` is entitled to assume, and 0.1.0 read exactly that.
  `document_versions()` already reads the package's own declaration, so
  `describe()` reports the new list with no further change.
- **`capture.py`'s `carries_program` and `viewer.ts`'s program gate do
  NOT move** — checked, not assumed. Both are already FLOORS at version
  5: `capture.py:71-73` is `version >= 5` and `viewer.ts:1962` is
  `document.version >= 5 || program !== undefined`. The previous cycle
  turned both from `== 5` into floors precisely so the next version
  number would cost nothing.
- The spec scenario "A version beyond the ones it reads is refused"
  mounts a document declaring **version 7** today; it becomes version 8.

### D8. The corpus, and the width guard

`src/running-corpus.json` is replaced by the framework's
`tests/running-corpus.json` at `0b0f02a`, **byte for byte** — 19
scenarios over 16 machines, 356 ticks. The census in
`running-corpus.test.ts` (17, 14, 328) follows.

The width guard's `REQUIRED` gains the producer's three new features, in
the producer's own order and spelling:

- `'a switched source'`;
- `'a selection crossing inside a tick'`;
- `'a tick carrying both a selection crossing and a stop'`.

They are detected as `tools/generate_running_corpus.py:445-510`'s
`_member_of` and `_selection` detect them, re-derived from the DOCUMENT
and the tick log and never from the loader: the guard must be red on a
narrowed corpus **even when the engine is broken**, which is why
`freeNamesOf` already exists there as a second, deliberate copy of the
bindings closure. A selector's primitive counts only if NO other jump of
that member has it, so a crossing carrying it is a selection crossing and
not a gate that happens to share an operator.

**Measured, before any of this is written.** A JavaScript spike of that
re-derivation over both files (`scratchpad/viewer-spikes/selection-spike.ts`)
finds, on the framework's file, blocks `{higher.turn, carry.travel}` for
both new machines — ADR-122's evidence group 8's own answer — with
selector primitives `{<}` and `{>=}` on `ShiftedCarry`'s two members, and
reports the three features COVERED; over the committed file it reports
all three UNCOVERED. The existing `REQUIRED` is satisfied by both files,
so nothing is red until it gains the three.

The narrowed-corpus test names one of them, as it already names the
self-read's three.

### D9. What it costs

Measured in `cost.test.ts` beside the numbers already there (the
Pascaline at `1/240`, the Clearing fixture, the lock's five bounds):

- `ShiftedCarry` at `dt = 0.05`, a QUIET tick (one piece) and the tick
  that crosses the detent (two pieces) — the producer measured 1.306 and
  2.671 ms/tick against `FixedZero`'s 0.799, the honest baseline being
  the same laws as three separate edges with the carriage frozen;
- the Curta carriage fixture, one block of seven — the producer measured
  10.658 ms/tick at `dt = 0.02`;
- a stop on a block coordinate, the expensive case: `RangedBlock`'s
  searched stop, which the producer measured at 17.186 ms/tick against
  1.306 for a quiet tick of the same machine, a **22x** ratio.

The absolute numbers are a different runtime's and are not the assertion;
the RATIOS are what this cycle records, together with the one number that
must not move: a document with NO block pays one extra test per edge per
tick — `kind === 'block'` in `edgeIncrements` — and nothing else. The
Pascaline's existing figure is the control.

### D10. The acceptance: a version 7 document in a real page

`tests/fixtures/carriage/`, produced reproducibly from a THROWAWAY copy
of solid-node at `0b0f02a` (`git archive 0b0f02a | tar -x -C <scratch>`)
and never from the pilot's checkout:

```text
$ PYTHONPATH="$PWD" solid export \
    tests/carriage_project/machine.py:CurtaCarriage -o <dir> --no-widget
WARNING - core.export - this model needs document version 7, and the
  installed browser viewer renders 1, 2, 3, 4, 5, 6 (solid-node-viewer
  0.1.0). …
```

Already run: the file written is `manifest.json`, **32,791 bytes**,
`md5 1598d57e18f772315183a7e466123a39`, declaring **version 7**, five
drivers (`clearing`, `crank`, `lift`, `position`, `reset`), fourteen
coordinates all resting at `0.0`, thirty-five bindings, no intermediates,
a `seat` span both of whose sides are `Bound(..., reads=)` expressions,
and **nine law edges of which seven — edges 2 to 8, the three levers and
the four dials — form ONE block**, each carrying a self-read and each
published `affine: [true]`.

As with the clearing fixture, the export needs ONE line changed in the
throwaway copy — `tests/carriage_project/machine.py`'s
`from ..running_project.parts import …` becomes
`from running_project.parts import …`, because `solid export` takes
`tests/pyproject.toml` as the project root and the relative import then
goes beyond the top-level package. That it changes nothing is checked the
way the previous cycle checked it, by running the framework's own
carriage tests on both copies and comparing the published program.

The page then, in Chromium, at the framework's own **`dt = 0.02`** (not
the viewer's default `1/240`, so the numbers are the producer's own):

1. lift, shift to position 1, drop, crank by 36 — `dial0` and `dial1`
   read `36`, `dial2` and `dial3` read `72`, `lever0.travel` is exactly
   `1.0` (`CurtaShapedTest.test_a_shift_away_and_back_preserves_every_part`);
2. lift, shift to position 2, drop — **every coordinate but `seat`,
   `hoist`, `position` and `lift` is BIT-IDENTICAL** to what it was, and
   `seat` reads `40.0`. This is what D5 is for;
3. lift, reset, drop — the levers return to `0.0` within the run's
   agreement window (the cam drives each exactly onto its own surface, so
   they rest at `1.1102230246251565e-16`, and a reading taken ON a
   surface is outside the exact promise), and `dial3` still reads `72`;
4. crank by 36 again — `dial2` reads `108` and `dial3` reads `144`, each
   lever now acting on the wheel it FACES;
5. **the interlock**: with the carriage DOWN and a lever standing set,
   the same shift retires `blocked` with `0.0` admitted, `seat` stands at
   `20.0`, the stop names `('position',)` and no dial or lever moved
   (`CarriageInterlockTest`);
6. **a refusal reaches the page**: the producer's `BothActive` shape —
   two laws each gated `shift >= 0.5`, orderable below the detent and
   cyclic above it — is driven past the detent and the run reports a
   refusal, the bank standing where it stood.

Nothing in the page poses anything; everything is driven by the
document's own declared drivers, as the clearing acceptance is.

`ShiftedCarry` is exported beside it for an engine-level test that needs
no browser — the one-tick table of `proposal.md`, turned from a
measurement of the bug into an assertion of the fix.

### D11. ADR-058 (EXPORT), extracted after implementation

"A block is ordered per piece from the published edges" — extends
ADR-045 (the run in the worker) and ADR-047 (the corpus), builds on
ADR-057 (deriving a reading at load and threading it through the walk),
consumes solid-node ADR-122. Its decision: the consumer re-derives
membership and selectorhood from `needs`, `gives` and the published
`level` expressions, executes the derived order rather than the published
listing, verifies the listing is one, and forces a selector's branch into
the member's plan at the producer's own two points.

## Risks / Trade-offs

1. **The corpus does not discriminate the ordering.** `ShiftedCarry`
   replays green on the base under two different orders (measured), so
   the corpus alone would pass a broken implementation of D1/D2. Mitigated
   by the one-tick engine test of D10 and by the Curta acceptance, both of
   which are order-sensitive by construction, and by the load-time
   refusals, which have their own red-first tests. The gap itself is the
   PRODUCER's to close — a `ShiftedCarry` script whose latch crosses its
   threshold strictly inside a tick would discriminate — and is recorded
   for the framework as a follow-up, not widened into this cycle.
2. **The fold needs a structural view of an expression the evaluator
   owns.** D1.5 adds one read-only accessor to `expressions.ts`. The risk
   is that it becomes a second, drifting representation; mitigated by
   exporting a view of the EXISTING store rather than a parser, and by
   keeping the fold's rules in `run/program.ts` where the mirror lives.
3. **A refusal message that must be word for word.** D2.4 quotes the
   producer's float `repr` for the piece bounds. JavaScript's `String`
   and Python's `repr` agree on doubles for almost every value and not
   for all; the test asserts the message's SHAPE and the numbers it
   names, and the design does not claim byte equality with a Python
   `repr` it cannot run.
4. **The searched stop is expensive.** D4.2 makes every stop on a block
   coordinate a search over the whole block. The producer measured 22x a
   quiet tick on the same machine. This viewer runs in a browser and the
   Curta carriage is seven members; D9 measures it rather than hoping,
   and the follow-up (classifying a block give as affine under a fixed
   branch vector) is recorded on both sides.
5. **`sign` is deliberately not foldable.** An author who gates a block's
   only conditional dependency on `sign` gets the load-time cycle refusal
   rather than a machine that refuses every tick. That is the producer's
   intended answer and its message says so; it remains a shape an author
   could reasonably expect to work.
6. **ADR-113's one-input pushing probe cannot see a push that needs TWO
   inputs moving together**, and the tick is then refused
   (`StopInvariantError`) rather than answered wrongly. It is
   PRE-EXISTING — the producer measured it on a machine with no block at
   all — this cycle inherits it and does not lift it.

## Open Questions

1. Should the loader ALSO verify that a block's published members are
   contiguous, rather than only that the contracted order is
   topological? D1.2 says no: contiguity is a property of the producer's
   own listing convention, and refusing a non-contiguous but correctly
   ordered listing would refuse a document this engine can execute
   exactly.
2. The producer's follow-up list includes naming the SELECTOR ids in the
   `block` line of the program identity. If it ever does, nothing here
   changes — the identity is the producer's and this viewer only
   compares it — but the corpus would move and this repository would take
   the new file.
