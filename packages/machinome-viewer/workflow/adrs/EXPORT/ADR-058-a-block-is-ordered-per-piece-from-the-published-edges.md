# ADR-058: A block is ordered per piece from the published edges

**Status:** Accepted

**Date:** 2026-09-15

**Change:** `execute-the-selection`

**Extends:**
- [ADR-045: The run executes in a worker and the main thread only poses](ADR-045-the-run-executes-in-a-worker.md)
- [ADR-047: The corpus is what makes the two runtimes one algorithm](ADR-047-the-corpus-makes-the-two-runtimes-one-algorithm.md)

**Builds on:**
- [ADR-057: A self-read edge is executed from the retained value, piece by piece](ADR-057-a-self-read-edge-is-executed-from-the-retained-value.md)

**Consumes:**
- solid-node ADR-122: A selection decides which sources a law reads — a
  cycle every selection breaks is a block, ordered piece by piece

## Context

ADR-045 mirrored `simulation/program.py` and `simulation/run.py`
function for function; ADR-047 pinned the mirror to the producer's own
corpus; ADR-057 widened a law to read the coordinate it drives. Under all
three the compiled program was ordered ONCE, by Kahn over the ends its
edges determine, and the published order of the edges was the order the
engine ran them in.

solid-node's ADR-122 breaks that. A machine's dependencies may be
SELECTED by where one of its own parts stands: the Curta's carry levers
belong to the fixed frame and its number dials ride on the carriage, so
the same lever is tripped by dial `s` and advances dial `s + 1`, where
`s` is the carriage position the maker chose. At any one position the
active dependencies are a chain and acyclic; their UNION over the working
positions is cyclic, and the union is what the compiled program orders.
The producer compiles such a union as a **block** — the nontrivial
strongly connected components of the dependency graph over the edges'
`needs` and `gives`, a need an edge itself gives excluded, each contracted
to one entry — and orders that entry once per **piece** of a tick.

**The producer publishes that as a version 7 document and adds no key for
it.** `Program.published` emits a block's members as ordinary law edges,
contiguous at the block's position in its own deterministic order, and
that order is a LISTING and not an execution order. A consumer re-derives
membership from the published `needs` and `gives`, and selectorhood from
each plan's published `level` expressions. ADR-110's line is the reason:
the document carries what compile time DECIDED, not what is computable
from it — `sources` is published because it is a decision about
candidates, `constraints` are derived (ADR-054), and membership and
selectorhood are functions of the published edges, so they are derived
too.

**What this viewer did with such a document before, measured on the base
`fff31e4` + the planning commit `1911bdd`.** In a real page it refused it
by name, which was correct: `RENDERED_VERSIONS` was `[1, 2, 3, 4, 5, 6]`
and `assertRenderable` turned a version 7 document away before a pose was
evaluated. The producer's own export said so, exporting the framework's
`CurtaCarriage` from a throwaway copy of solid-node at `0b0f02a`:

```text
WARNING - core.export - this model needs document version 7, and the
  installed browser viewer renders 1, 2, 3, 4, 5, 6 (solid-node-viewer
  0.1.0). The export is written anyway: an export is an artifact a LATER
  viewer may open, and a viewer that cannot read it refuses it by name
  rather than rendering part of a machine it does not understand.
```

**In the engine it refused nothing at all — it executed the listing.**
`loadProgram` read no version number, did no ordering and detected no
cycle; it inverted `gives` into `determiner` and handed `Run.pass` the
published array. So a block reached the engine as an ordinary run of law
edges in the producer's listing order. Measured with the corpus's own
`ShiftedCarry` document — two wheels, one fixed lever, a live `shift` —
cranked by `2.0` in ONE tick of `dt = 1.0`:

| run | `lower.turn` | `higher.turn` | `carry.travel` |
| --- | --- | --- | --- |
| the producer at `0b0f02a` (ground truth) | `2.0` | **`1.0`** | `1.0` |
| this viewer, published listing order | `2.0` | **`0`** | `1.0` |
| this viewer, the block's two members swapped | `2.0` | **`1`** | `1.0` |

Nothing was reported in any case: no refusal, no crossing, no stop. The
carry was simply lost, by a different amount for each order the producer
might have listed — ADR-122's own silent-wrong-answer table, reproduced
on the consumer side.

**The corpus gap was measured before anything was written.** The
committed `src/running-corpus.json` was one framework regeneration
behind: 17 scenarios, 14 machines, 328 ticks (md5
`0ba7939ad5b5988f739aa114a26ab464`) against the framework's 19, 16, 356
(md5 `c682b7f2c70bc7ef4f29a610ecfa8cb5`). Two scenarios added —
`('ShiftedCarry', 0.05, 20)` and `('RangedBlock', 0.05, 8)` — none
removed, and **none changed**: every pre-existing entry byte-identical.
The framework's file replayed through the shipped engine failed exactly
one of the nineteen,

```text
× replays RangedBlock at dt=0.05 (scenario 18)
  → RangedBlock at dt=0.05, tick 1, the number of crossings:
    expected 3, got 2
```

and beyond that first assertion the same tick put the stop's fraction at
`0.3` where the producer puts `0.29999999999972715`, and committed `spin`
and `lower.turn` at `0.6` where the producer commits
`0.5999999999994543`. The cause is structural and is half of this
decision: `carry.travel` is a block give, so the producer's `Edge.affine`
is `False` on it and `Run._locate` searches, while the consumer read the
MEMBER's published `affine: [true]` and solved a bound piecewise on a
value that is re-ordered across the selector partition.

**And `ShiftedCarry` replayed GREEN on the base, which is evidence of
nothing.** Its twenty ticks at `dt = 0.05` record no crossing at all and
its one in-block gate never changes branch inside a tick; exchanging the
two members in the published listing changes not one float of that
scenario. A corpus scenario that passes under two different orders proves
neither.

## Decision

**The block is re-derived at LOAD, from the published edges alone, and
what cannot be one is refused there.** `loadProgram` gains one pass after
the edges are validated and after ADR-057's retained reading is derived.
Nothing in it tests the version number: a version 7 document whose edges
hold no nontrivial component produces no block and takes exactly the path
a version 5 or 6 one takes, which is the stance ADR-057 already took for
a version 6 document carrying no self-read.

- **The components.** `componentsOf` builds the dependency graph over the
  validated edges in published order — an edge is adjacent to the edge
  that determines each key it needs, a key it gives itself EXCLUDED, the
  same exclusion ADR-057 makes for the self-read — and `stronglyConnected`
  is Tarjan, **iterative**: a deep chain must not exhaust the JavaScript
  stack any more than it may exhaust the interpreter's. Members are
  emitted sorted and components sorted by their first member
  (`_components`, `_strongly_connected`). A `check` determines nothing, so
  nothing ever waits on it and it can never be in a component.
- **The contraction.** Each nontrivial component becomes ONE derived edge
  of a new kind, `block`, at the index of its FIRST member; every other
  edge keeps its published position and relative order (`_blocked`). The
  block entry carries the union of its members' `needs` in first-seen
  order, all their `gives`, their descriptions joined with `'; '` and
  their classes de-duplicated in order, so every refusal that prints an
  edge prints the block's members. `kind: "block"` is DERIVED and never
  read: `EDGE_KINDS` stays `law | wiring | formula | check`, and a
  document publishing an edge of kind `block` is still refused as an
  unknown kind.
- **The order is VERIFIED, never re-sorted.** The contracted sequence is
  checked to be a topological order of the contracted graph, and the
  document is refused by name if it is not — `<edge> reads "<id>", which
  <edge> determines LATER in the published listing`. Kahn-ordering it
  here, which is what the producer does at construction, would silently
  accept a document whose published listing disagrees with its own
  content, which is precisely the failure version 7 exists to make loud.
  This viewer reads the order compile time decided (ADR-047) and checks
  it. Contiguity is NOT required: a correctly ordered non-contiguous
  listing is a document this engine can execute exactly.

**The selectors are re-derived per member, and one all-zero fold answers
both questions the load asks.** A selector is a jump of the member's plan
whose published `level` reads no id the block gives — asked of the level
CLOSED OVER the document's bindings table, ADR-054's lesson a third time,
because every selector level of both new corpus machines is `_b2`, a
binding for `(shift - 0.5)`, and a viewer reading raw free names would
misclassify all of them. `selectorsOf` propagates through the
placeholders of non-selector inner nodes in the plan's postorder, which is
well defined because a placeholder stands for exactly the subtree it
replaced. A node whose level reads the member's OWN driven end is not a
selector — the own end is one of the block's gives — so it stays where
ADR-057 put it, in the walked layer inside the piece, and the Curta
lever's selector on the carriage composes with its latch on its own
travel.

The fold is a TRAVERSAL, not a rewrite: `foldedNames` walks the
hash-consed DAG bottom-up returning per node the pair `(is it the literal
zero, what names does it still read)`, which is the producer's `_folded`
read for its effect on names. Two rows deliberately do not propagate
zero, because the producer's `is_zero` is true only of a numeric literal:
`0 − y` becomes a unary node, never a literal, and a unary minus over a
zero stays one. A literal counts as zero in any spelling, as
`float(text) == 0.0` reads it. `readsUnder` then follows every SURVIVING
placeholder into its own folded level, transitively (`_reads_under`), and
a BINDING name is walked INTO rather than reported — `CarryLead`'s
`_b6 = (360.0 * _j0)` is a binding carrying a placeholder that the
producer really publishes, and stopping the fold at the name would leave
that zero unpropagated and over-approximate a member's reads. With `zero`
the substitution sending every FOLDABLE selector's placeholder to zero —
`floor`, `ceil`, `%` and the six comparisons, and NOT `sign`, whose zero
branch is a single point rather than an interval — `unconditional` is
what no selection can switch and `switched` is what it can. ONE fold per
member suffices because the fold is monotone and the all-zero assignment
is therefore the minimum over every assignment; a search over `2^n`
selector assignments would leave the load's cost undefined.

**Four shapes are refused at LOAD, by relation identity**, exactly the
ones the producer refuses at CONSTRUCTION (`_refuse_unselectable`,
`_Block.unconditional_cycle`), each message naming the edge, its
`statedBy` and every member of the block: a **wiring or a formula** on a
cycle, which carries no jump node so no selection can switch what it
reads; a member driving a **group**, because what a selection switches is
decided per driven end off that end's own expression while a group's ends
are claimed together; a member whose give is **not a bank coordinate**,
because a block advances its coordinates piece by piece and only a
coordinate the run owns keeps that history; and a **cycle no selection
breaks**, where the block's unconditional graph still has a cycle — the
producer's `_cycle_message` word for word, including the sentence saying
what a switch is and that `sign` is not one. The producer never publishes
such a document, and that is exactly why the loader is the guard: a
consumer meeting one of these first at tick time would meet it while a
frame was being drawn.

**A tick runs a block PIECE BY PIECE** (`blockIncrements`,
`_Block.increments`), reached from `edgeIncrements` on `kind === 'block'`:

- **the selector partition is located FIRST, over the whole stretch.**
  Per member, a plan of that member's SELECTORS ALONE over its own
  published skeleton is handed to the existing `partition` — not a copy —
  its crossings recorded under that member's description and coordinate
  and its interior cuts merged into ONE cut list in the members' order and
  each member's postorder. Every selector level reads only coordinates the
  block does not give, so its path is the linearisation `along` already
  builds and nothing new locates anything;
- **the branches are read at each piece's MIDPOINT**, ADR-107's own rule
  for ADR-107's own reason, giving one `{placeholder: branch}` map per
  member;
- **the order is Kahn over the RUN-TIME fold**, `activeReads(index,
  forced)` restricted to the block's gives with a member's own end
  ignored, **memoised by the branch VALUE vector** — not by booleans,
  because `branchOf` answers an integer for `floor`, `ceil` and `%`, so a
  crank passing three tooth windows in one tick gives three keys;
  `whole()` has already normalised `-0` to `0`, so the two zeros cannot
  key two entries;
- **the members run over the piece in that order**, each source the block
  does not give started at `values + deltas·left` and moved by
  `deltas·(right − left)`, and each source the block DOES give handed the
  block-advanced value it holds at this piece's start with the increment
  computed for it ON THIS PIECE, or zero where the order has not reached
  it. **The in-block value is advanced between pieces**, which the
  producer measured rather than asserted and this cycle mirrors as a test.
  A switched-out source this piece has not determined is handed its
  block-advanced value with a delta of `0.0`, safe without a tolerance:
  every term reading it is multiplied by a placeholder forced to zero, a
  non-selector node whose level reads only such a source has a constant
  level and a constant level crosses nothing, and a switched-out source
  determined EARLIER in the order gets its real increment;
- **a still-cyclic piece refuses the TICK**, transactionally, with the
  producer's message word for word — `over the piece [<left>, <right>] of
  this tick the relations <members> form a cycle the run cannot order …
  The selectors read <name>: <primitive> on <level> reads <value>; … The
  tick committed nothing`. It is an `UnsupportedLaw`, so `RefusalKind`
  gains nothing and `Run.integrate`'s existing catch rolls the tick back.
  No branch VECTOR reachability is decided anywhere: that is a
  satisfiability question, which is why the load-time check is necessary
  and not sufficient.

**A selector is a CONSTANT on the piece.** The branch the block read is
substituted into the member's own plan through a new `forced` map,
threaded to exactly the TWO points the producer threads it to: `partition`
SKIPS locating a forced node's crossings — the block located them over the
whole stretch already — and `branchesAt` returns the forced value instead
of evaluating the level. `planIncrement`, `planCuts`, `retainedIncrement`,
`retainedCuts` and the `Walk` constructor pass it down, and everything
downstream — the walk's two layers, its probe, its cuts, its far-side
landing — reads the same `branches` map and inherits it. **No other
function changes.** That a selector is always an INDEPENDENT node in
ADR-057's split is a consequence and not an assumption: its level reads
nothing the block gives, the member's own driven end included, so it can
never be dependent, and the split stays decided at load with the selectors
still symbolic.

**What a block reports.** For a coordinate any piece LANDED, the ABSOLUTE
value the block advanced it to by the stretch's END — the landing plus
every later piece's increment — because `Run.landed` commits a reported
landing absolutely and would otherwise discard the motion after it.
**`affine` is FALSE on every give of a block**, so a stop on a block
coordinate is SEARCHED and never solved: a block's value is piecewise in
the selector partition AND re-ordered across it. Crossings are rescaled
`left + t·(right − left)` out of their piece, and the whole located list —
selector crossings over the stretch and members' own crossings out of
their pieces — is SORTED by fraction before it reaches the record, so the
listing does not depend on which was computed first. `edgeValues` answers
nothing for a block, as `Program.values_of` skips it, and `blockCuts` is
defined rather than left to throw because `piecewise` becomes meaningful
over it the day a later cycle classifies a block give as affine under a
fixed branch vector. `determiner` maps each give to `{edge: theBlock,
index}`, which is what `Run.locate` reads `affine[index]` and
`edgeCuts(…, index)` by.

**`run.ts` does not change at all**, and that is a claim with a reason:
the producer's `run.py` did not either. `pass`, `landed`, `locate`,
`along`, `groupOf` and `pushes` meet a block through the edge interface
they already call. `pushes`'s `edge.gives.includes(key)` break therefore
happens AFTER the whole block has run under one input's displacement,
which is what makes an input coupled to a stopped coordinate only through
an INACTIVE selection contribute nothing and not be stopped — it would not
be true if the members were separate entries. A block's increments are
complete and side-effect-free with `crossings`, `tick` and `landings`
absent, as `Run.along` and `Run.pushes` call them, and still refuse a
genuinely cyclic piece under the same midpoint reading and the same
ordering the tick uses: a probe that refused where the tick would not
would make a stop's blocked group a function of the probe rather than of
the machine.

**The walk's own arithmetic is parenthesised.** `Walk.run`'s `ownAt`
closure and `Walk.probe` now compute `ownLeft + (S − base)` where they
computed `(ownLeft + S) − base`, as `_Walk.run`/`_Walk._probe` now do.
This is a behaviour change for **version 6 documents too**, taken here
rather than separately because ADR-122's "a selection change alone moves
nothing" is a BIT-FOR-BIT promise that cannot be asserted while the walk
adds an ulp of its own. Measured red first on the producer's `HeldAngle`
shape — a version 6 document with no block anywhere, a crank standing at
`72.0`, a dial resting at `71.99999999999996`, the lift moved alone —
which committed `71.99999999999994` from an increment of
`-1.4210854715202004e-14`, and after the change leaves the dial at
`71.99999999999996` exactly.

**`documentVersions` becomes `[1, 2, 3, 4, 5, 6, 7]` and the declared API
version rises 15 → 16.** Executing a version 7 document is a capability a
host may require BEFORE it mounts, because it is not additive: a build at
15 refuses the Curta's carriage by name and renders nothing at all. The
precedent is exact — ADR-057 raised 14 → 15 when the list gained 6.
`bundle.py`'s `RELEASED_DOCUMENT_VERSIONS` does NOT move: it is what a
consumer receiving no declaration is entitled to assume, and the only
released viewer, 0.1.0, reads `[1, 2, 3, 4]`. `capture.py`'s
`carries_program` and `viewer.ts`'s program gate do not move either —
checked, not assumed, and now asserted: both were turned into floors at
version 5 by the previous cycle precisely so the next version number would
cost nothing.

**The corpus is what holds the two runtimes together here too.** The
producer's regenerated fixture is committed byte for byte — 19 scenarios
over 16 machines, 356 ticks, `ShiftedCarry` and `RangedBlock` among them —
and the width guard gains the producer's three new required features (`a
switched source`, `a selection crossing inside a tick`, `a tick carrying
both a selection crossing and a stop`), detected as the generator's own
`_selection` and `_member_of` detect them, from the DOCUMENT and the tick
log and never through `loadProgram`, so the guard is red on a narrowed
corpus even when the engine is broken.

## Alternatives weighed

- **Kahn-order the contracted program ourselves.** It is what the producer
  does at construction, and it would silently accept a document whose
  published listing disagrees with its own content — the exact failure
  version 7 exists to make loud. Re-sorting would make the engine's answer
  a function of the consumer's tie-breaking rather than of the document.
  The verification costs one pass and turns a malformed producer into a
  named refusal instead of a different machine.
- **Trust contiguity.** The published members ARE contiguous today.
  Relying on it would let a hostile or future document reach the tick with
  a block the engine never grouped, which is the one shape that must not
  happen quietly.
- **A published `block` key, or a published execution order.** Membership
  and selectorhood are functions of the published `needs`, `gives` and
  `level` expressions. A derivation with no decision in it is the
  producer's to refuse (ADR-110) and this viewer's to make at load, where
  ADR-054 put the constraint table and ADR-057 the retained reading.
- **A second expression parser in `run/`, or rewriting the folded tree.**
  A copy drifts from the one the evaluator uses at the first correction
  either receives, which is the failure the corpus exists to prevent;
  rewriting would mint DAG nodes at load for an answer that is a set of
  strings. One read-only structural view of the EXISTING store
  (`structureOf`) is exported instead.
- **A search over `2^n` selector assignments** to find each member's
  unconditional reads. The fold is monotone, so the all-zero assignment is
  already the minimum; the search invites `2^n` folds per member and leaves
  the load's cost undefined. The producer rejected it for the same reason.
- **Let each member RE-LOCATE its selectors' surfaces inside its own
  piece.** The two readings agree in the ordinary case, but `merged` folds
  cuts closer than the tolerance IN THE FRACTION of the path being cut, so
  a level recomputed a few ulps on the wrong side at the left end of a
  piece of width `1e-9` is a genuine cut at relative position `1e-3`, and
  the member would integrate part of that piece under a branch the block
  did not order it under. Substituting the branch removes the question
  rather than bounding it, at one map entry per selector per piece.
- **Making `sign` foldable.** Its zero branch is the single point where the
  level is exactly `0.0`, not an interval, so a `sign`-gated source counted
  as switched would admit at LOAD a machine every tick refuses. The
  producer's intended answer is the load-time cycle refusal, and its
  message says so.
- **Leaving the API at 15 and moving only the document list.** It would let
  a host mount a bundle that refuses by name the machine it was mounted
  for.

## Consequences

- **A version 7 document loads, runs, and agrees with the framework tick
  for tick.** All nineteen corpus scenarios replay green — exactly for
  discrete state and within the corpus's own `1e-9` relative window for
  floats — and the width guard is green on the new file, red on the old
  one and red on the trimmed one. The derivation finds on both new
  machines exactly ONE nontrivial component, `{higher.turn,
  carry.travel}`, which is ADR-122's own evidence group 8's answer;
  `ShiftedCarry`'s three published law edges become TWO entries, the
  block's `affine` reading `[false, false]` and its `determiner` mapping
  `higher.turn → {block, 0}` and `carry.travel → {block, 1}`. On its
  members the fold leaves `unconditional` EMPTY for both and `switched`
  `{carry.travel}` and `{higher.turn}` — nothing is left on the cycle once
  the selectors fold, which is why the document loads at all.

- **The one-tick table is now an assertion of the fix.** The corpus's own
  `ShiftedCarry` at `dt = 1.0` cranked by `2.0` commits `lower.turn 2.0`,
  `higher.turn 1.0`, `carry.travel 1.0`, and does so with the two block
  members EXCHANGED in the published listing — which the base could not do,
  having answered `0` and `1`. Over 12 ticks of `dt = 1/12` the same crank
  gives, asserted bit for bit against the producer at `0b0f02a` on the same
  document, `lower.turn 2.0 / higher.turn 1.5 / carry.travel 1.0` at
  `shift = 0` and `0.0 / 2.0 / 1.0` at `shift = 1`. A selection change
  alone moves nothing: cranked, then shifted across the detent and back,
  all three coordinates are `Object.is`-identical to what they were.

- **The order really does flip with the selection, and the memo really is
  keyed by values.** On the detent bench the ordering is asked for under
  `{_j0:1,_j1:0} {_j2:1}` below the detent and `{_j0:0,_j1:1} {_j2:0}`
  above it; a `floor` selector on an input swept `0 → 3.5` makes FOUR
  pieces, four distinct keys and eight `activeReads` calls with the branch
  reading `0, 1, 2, 3` in turn.

- **The Curta's own carriage runs in a real page.** The framework's
  `CurtaCarriage`, exported from a throwaway copy of solid-node at
  `0b0f02a` and committed as `tests/fixtures/carriage/` — **32,791 bytes**,
  md5 `1598d57e18f772315183a7e466123a39`, version 7, five drivers, fourteen
  coordinates, thirty-five bindings, nine law edges of which **seven form
  ONE block** — mounts in Chromium at the framework's own `dt = 0.02`,
  driven only by the document's declared drivers. Lifted, shifted to
  position 1, dropped and cranked by 36 it reads `dial0 36, dial1 36,
  dial2 72, dial3 72`, every lever at `1` and `seat 20`; lifted and shifted
  to position 2 it leaves **every dial and every lever BIT-IDENTICAL**
  with `seat 40`, which is what the parenthesised walk is for; reset, the
  levers return to `1.1102230246251565e-16` — the residue of adding a
  tenth ten times, a reading taken ON a surface and so outside the exact
  promise — with `dial3` still at `72`; cranked by 36 again, each lever now
  acting on the wheel it FACES, `dial2` reads `107.99999999999999` and
  `dial3` `144.00000000000006`, within the run's agreement window. 51
  crossings, 0 stops. The **interlock** holds: with the carriage down and a
  lever standing set, the same shift retires `[['position', 'blocked',
  0.0]]`, `seat` stands at `20.0`, the stop names coordinate `seat` and
  inputs `['position']`, and no dial or lever moved. And a **refusal
  reaches the page**: the producer's `BothActive` shape, orderable below
  the detent and cyclic above it, puts the cyclic-piece message into the
  page's own `.run-refusal` line with the bank and the tick count standing
  where they stood.

- **The refusal's words are the producer's and its floats are this
  runtime's.** `over the piece [0.5, 1] …` where Python's `repr` writes
  `0.5, 1.0`, and `reads 1` where it writes `reads 1.0`. Neither runtime
  ever sees the other's message — a refusal is not corpus state — so the
  tests assert the message's shape and the numbers it names, not byte
  equality with a `repr` this runtime cannot produce.

- **A block tick costs, and the searched stop costs a great deal.**
  Measured on this bench: `ShiftedCarry`'s quiet block tick **4 394
  ticks/s** against its frozen twin's **7 079**, and a crossing tick
  **2 083** — **1.6×** and **2.1×**, against the producer's own 1.6× and
  2.0×. The Curta carriage, one block of seven, runs at **280 ticks/s** =
  3.6 ms/tick, against the producer's 10.658 ms/tick.
  `RangedBlock`'s searched stop runs at **266 ticks/s** against **28 897**
  for a quiet tick of the same machine replayed from the same snapshot —
  **108.6×**, where the producer recorded 22× against a busier control.
  The number that matters is the absolute one: **3.8 ms** for a searched
  stop on a two-member block. **The control does not move**: the Pascaline
  reads 39 992 ticks/s where the base read 38 463, and `Train`, which
  carries no block, 177 353 against 185 910 — both inside this host's
  run-to-run spread. The whole suite goes 869 → 922 tests and the bundle
  702.5 kb → 723.9 kb.

- **The corpus does not discriminate the ordering, and this is the second
  time that is worth saying.** `ShiftedCarry` replays green on the base
  under either published order of its two block members; the corpus alone
  would pass a broken implementation of the derivation or the per-piece
  order. What catches it here is the one-tick engine test — asserted under
  BOTH orders — and the Curta acceptance, which is order-sensitive by
  construction, together with seventeen load-time tests measured red by
  disabling the contraction and the order verification in turn. The gap
  itself is the PRODUCER's to close — a `ShiftedCarry` script whose latch
  crosses its threshold strictly inside a tick would discriminate — and is
  recorded as a follow-up rather than widened into this cycle. As ADR-057
  already found for the walk's three corrections: the corpus pins the
  algorithm's ANSWERS on the machines it carries, not the corrections
  themselves.

- **Where the design's prose and `program.py` disagreed, `program.py`
  won, and it is recorded.** The ratified design closes the folded names
  through the bindings table AFTER the fold; implemented that way, a
  binding that CARRIES a placeholder stops the zero at the binding's name.
  That shape is real and published — `CarryLead`'s own table holds
  `{"name": "_b6", "expression": "(360.0 * _j0)"}` — so `foldedNames`
  resolves a binding by walking into its own DAG root instead, which is
  `_reads_under` exactly and is what the design says the function IS. The
  two readings agree wherever a binding carries no placeholder and no
  foldable zero, which is every binding on the corpus's block machines;
  the difference is that the implemented one cannot over-approximate a
  member's reads and so cannot invent an unconditional cycle.

- **A document with no block is untouched** — same meaning, same code
  path, one extra `kind === 'block'` test per edge per tick — save for the
  one ulp the walk's parenthesisation removes from every version 6
  document. The corpus's seventeen pre-existing scenarios stayed green
  over the new file, which is the regression test for it, the producer
  having regenerated the corpus after making the same fix.

- **Two limits are inherited rather than lifted.** ADR-113's one-input
  pushing probe still cannot see a push that needs TWO inputs moving
  together, and the tick is refused rather than answered wrongly; it is
  pre-existing, measured by the producer on a machine with no block at
  all. And no block give is classified as affine under a fixed branch
  vector, which is what would make a stop on one solvable rather than
  searched; `blockCuts` is already defined for the day that lands, and the
  follow-up is recorded on both sides.

- **The fixture's provenance is recorded rather than reproducible on
  demand**, as the clearing fixture's is. The throwaway copy needs one
  relative import rewritten so the machine loads outside pytest, and that
  it changes nothing was checked rather than assumed: the framework's own
  carriage tests pass on both copies, and the published programs differ in
  their `identity` hash alone (`d69d5211…` against `917094ae…`), that hash
  taking in the module path — the framework finding ADR-057 already
  recorded, met a second time.

- **One task is not doable as stated and is left undone.** The rebuilt
  `dist/solid-widget.js` cannot be committed "as the previous cycles
  committed theirs": it is gitignored in this repository and has never been
  tracked. It IS rebuilt, every Python suite ran against it (129 passed),
  and `check-dist` reports `apiVersion 16`, `documentVersions [1,2,3,4,5,6,7]`
  and uploads nothing.

## Amendment — 2026-09-22

Endpoint-increment handoff and unconditional block-stop search are superseded; selected ordering and transactional cycle refusal remain.
See [ADR-071](ADR-071-determined-sources-retain-their-motion-path.md).
