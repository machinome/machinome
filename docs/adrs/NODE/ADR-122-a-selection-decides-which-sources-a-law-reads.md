# ADR-122: A Selection Decides Which Sources a Law Reads — A Cycle Every Selection Breaks Is a Block, Ordered Piece by Piece

**Status:** Accepted
**Date:** 2026-09-15
**Depends on:**
- [ADR-105: The run owns the coordinates and binds them](./ADR-105-the-run-owns-the-coordinates-and-binds-them.md) — memory lives on real banked coordinates and nowhere else, which is what a block's history is kept on
- [ADR-106: One law, two readings](./ADR-106-one-law-two-readings.md) — the compiled program this decision reorders
- [ADR-107: A jump is located inside the tick and subtracted](./ADR-107-a-jump-is-located-inside-the-tick-and-subtracted.md) — the partition, the midpoint branch and the three tolerances a selector's crossings are located under
- [ADR-121: A law may read the coordinate it drives](./ADR-121-a-law-may-read-the-coordinate-it-drives.md) — the walk a member still runs inside each piece, the absolute landing the run commits, and the precedent for a relation that binds nothing at rest
**Amends:**
- [ADR-106](./ADR-106-one-law-two-readings.md) — its "edges are ordered by Kahn over the ends they determine": the ordering is now Kahn over the program with every nontrivial strongly connected component CONTRACTED to one entry, and that entry is ordered again, per piece of a tick. A program with no such component is ordered exactly as before.
**Cites:**
- [ADR-113: A bound may read other coordinates](./ADR-113-a-bound-may-read-other-coordinates.md) — the pushing test a stop's blocked group is filtered by, one input displaced at a time
- [ADR-057: The flexible leaf, whose geometry travels as a spec](./ADR-057-the-flexible-leaf-and-spec-carried-geometry.md) — the rule that a producer emits the lowest version its content needs
- [ADR-110: The compiled program is published in the document](../EXPORT/ADR-110-the-compiled-program-is-published-in-the-document.md)
- [ADR-111: A conformance corpus is the contract between the two runtimes](../EXPORT/ADR-111-a-conformance-corpus-is-the-contract-between-the-two-runtimes.md)
**OpenSpec change:** `select-the-source`

## Context and Problem Statement

A running program is ordered ONCE, by Kahn over the ends its edges
determine (ADR-106), and every mechanism the campaign had met has an
acyclic union of dependencies — until a machine's dependencies are
SELECTED by where one of its own parts stands.

The originating project is `projects/Calculators/Curta-Type-I-3x`,
branch `direct-operation`, checkpoint `6a00abe`, and the requirement is
recorded whole in `workflow/docs/curta-shifted-carry-association.md`.
The Curta's carry levers and transmission shafts belong to the FIXED
frame; the number dials ride on the CARRIAGE. The same fixed lever is
therefore tripped by dial `s` and advances dial `s + 1`, where `s` is
the carriage position the maker chose — so which dial a lever reads, and
which lever a dial is advanced by, changes as the carriage turns. At any
one position the active dependencies are a chain and acyclic. Their
UNION over the six working positions is cyclic, and the union is what
the compiled program orders.

The project's executable diagnostic is
`simulation/tools/shifted_carry_probe.py`: two wheels, one fixed lever
and a live `shift` driver, every association written as a mutually
exclusive comparison factor (`c * (s < .5)`, `c * (s >= .5)`). Rerun as
the change's own reduced fixture (`spikes/reduced.py`), construction is
refused before any operation:

```text
UnsupportedLaw: the relations
(crank, shift, clearing, carry.travel, higher.turn) drives higher.turn,
(lower.turn, higher.turn, shift, carry.travel) drives carry.travel
form a cycle the run cannot order: each waits on a coordinate another
determines. A running program is acyclic, because the rest render solved
every relation in one direction.
```

Specializing the SAME laws to either fixed carriage position constructs
and runs. The union is the only thing refused.

**The refusal is the only thing standing between the model and a wrong
answer, and that too was measured.** With `_ordered` monkeypatched to
return the candidate edges in DECLARATION order, and again REVERSED, the
fixture compiles and the machine moves wrongly IN SILENCE
(`spikes/arbitrary.py`). Against the position-0 specialization, which
the framework orders correctly today and which is the ground truth:

| order | `lower.turn` | `higher.turn` | `carry.travel` |
| --- | --- | --- | --- |
| Kahn, position frozen at 0 | `2.0000000000000027` | `1.5000000000000018` | `1.0` |
| union, declaration order | agrees | `1.4800000000000013` | agrees |
| union, reversed order | agrees | `0.0` | `0.0` |

Declaration order loses a tick of the carry; reversed order never
carries at all. Nothing is reported in either case. That is what the
requirement note means by "accepting an arbitrary evaluation order
supplies no such semantics".

**Three routes through the model as it stood fail, and the note names
them** (`workflow/docs/curta-shifted-carry-association.md`, "The
following do not meet the originating project's approved outcome"):
making the carriage position a construction parameter, or reconstructing
the run on every shift — neither demonstrates retained state or a stable
program and snapshot identity through an actual shift; virtual per-dial
lever memories, duplicated coordinates kept only to store history, or
page-owned registers — ADR-105 puts memory on real banked coordinates
and nowhere else; and computing an independent calculator result and
driving decorative carry parts from it — then the lever no longer causes
the next digit's motion, which is the mechanism under test.

What the model could not express is a dependency that is CONDITIONAL.
The selection is already written — every association in the fixture is a
term multiplied by a comparison on the carriage — and the compiler
already reads a law's SKELETON, the expression with every jump node
replaced by its branch (ADR-107). What it did not do is notice that on a
piece where a comparison reads zero, the product it gates reads NOTHING.

**One further fact decided where the recognition has to live, and it was
measured rather than assumed** (`spikes/reduced.py`): without a
self-read the cycle never reaches the compile at all. The same three
relations with their `own` terms removed are refused by the REST RENDER
— `DoublyBound: higher.turn would be bound by the relation (crank,
shift, carry.travel) drives higher.turn and by the author's simulate()`
where the driven ends carry rest guards, and `UnreachedCoordinate:
(crank, shift, carry.travel) drives higher.turn: waiting for
carry.travel` where they do not. A rule only the compile knows cannot
save such a model.

## Decision Drivers

- The selection is already in the model. A Curta dial is driven by the
  crank UNCONDITIONALLY, by its own clearing rack through a retained-angle
  gate, and by a carry lever only when the carriage aligns them — three
  terms of ONE law with three different conditions. Whatever expresses
  the condition has to live on the TERM, which is where the model already
  writes it.
- Three tolerances and no epsilon anybody has to justify:
  `_SUBDIVISIONS`, `_CROSSING_TOLERANCE` and `_BISECTION_ROUNDS` are the
  whole budget, and a convergence tolerance would be a fourth — the
  reason ADR-121 refused a coupled solve for its own cycle of length one.
- Memory lives on banked coordinates (ADR-105): a lever left set at one
  carriage position must still be set when the carriage comes back,
  because the lever is a real part with a real coordinate.
- Nothing about a program with no such cycle may change: not its
  meaning, not its code path, not its cost, not its document, not one
  byte of the conformance corpus.
- What the reading cannot support must be REFUSED by relation identity
  at construction; what only a particular selection makes impossible must
  be refused TRANSACTIONALLY at run time, never integrated by guesswork.
- A consumer that cannot order a block per piece must refuse the
  document by name rather than execute the published order and move the
  machine by the amounts the table above records (ADR-057).
- The requirement note's seven acceptance items must follow from the
  RUN, not from project bookkeeping.

## Considered Options

**The spelling.**

1. A `Selected(position, {0: lower.turn, 1: higher.turn})` SOURCE END.
   Rejected on three counts. It is a new coordinate kind, with a
   resolution path, a rest rule, a publication and a refusal set of its
   own, for something the expression language already says. It needs a
   "no member" answer for the carriage between detents and for the LIFTED
   carriage, which is a second selection over the first. And it says
   nothing about the DRIVEN side: a dial is advanced by whichever lever
   faces it, so the dial's law must name EVERY lever and gate each.
2. `drives(..., when=...)`, or any relation-level condition. Rejected for
   ADR-121's own reason, with more force: the gate belongs to a TERM of a
   multi-source law. Three differently conditioned terms would become
   three relations into one driven coordinate, which the solver refuses
   as doubly bound.
3. A new verb. Rejected for ADR-089's reason: one verb states mechanical
   direction.
4. A coupled solver, or a fixed point per piece. Rejected for ADR-121's
   reason — a fourth tolerance and a per-piece iteration count. A block
   is ORDERED on each piece, and a piece that cannot be ordered is
   refused by name rather than iterated toward.
5. Removing the cycle detection, freezing every read for a tick, or
   taking the declaration order. The note names all three as supplying no
   semantics, and the table above is what the last one actually does.
6. **The comparison the model already writes.** Chosen: nothing is
   declared, no new keyword, no new document key.

**Recognizing what a selection can switch.**

1. A list of ADMITTED PRIMITIVES — the reviewer's briefing proposed
   comparisons and `sign`, excluding `floor`, `ceil` and `%`. Rejected in
   that form: the primitive is not what makes a term vanish, an
   ATTAINABLE zero branch is.
2. **The INTERVAL rule**, stated once over the fold and applied to every
   primitive by asking where each holds its zero branch: `floor` over
   `[0, 1)`, `ceil` over `(-1, 0]`, a remainder's quotient over
   `(-1, 1)`, a comparison over the whole of its false side — and `sign`
   nowhere, its zero being the single point where the level is exactly
   `0.0` (`_branch_of` returns `float((level > 0) - (level < 0))`).
   Chosen. It happens to exclude exactly the one the briefing wanted to
   admit and to admit all three it wanted to exclude.
3. A SEARCH over selector assignments — "switched by some SET of
   branches" — which invites `2^n` folds per member and leaves the
   construction check's cost undefined. Rejected: the fold is MONOTONE in
   the set of placeholders zeroed (every rule either removes names or
   keeps exactly the names its operand had, and a call's reads are the
   union of its arguments'), so **ONE all-zero fold per member** is the
   minimum over every assignment and answers both questions the compile
   asks.
4. Requiring EVERY in-block dependency to be switched. Simpler to state
   and strictly wrong: a block in which `A ← B` is unconditional while
   `B ← A` is switched is orderable on every piece. **The SCC of the
   UNCONDITIONAL graph** is the same cost — one more Tarjan pass over a
   graph the size of the block — and refuses exactly the shapes that can
   never work. Chosen.

**Evaluating a piece.**

1. Each member RE-LOCATES the selector's surface inside its own piece,
   the two readings argued to agree from `_surfaces(inclusive=False)` and
   `_merged`'s tolerance. Rejected: the argument is about ulps at a cut
   and becomes false for a short enough piece, because `_merged` folds
   cuts closer than `_CROSSING_TOLERANCE` in the FRACTION of the path
   being cut, so a level recomputed a few ulps on the wrong side at the
   left end of a piece of width `1e-9` is a genuine cut at relative
   position `1e-3` — and the member would integrate part of that piece
   under the branch the block did not order it under.
2. **A selector is a CONSTANT on the piece**: the branch the block read
   at the midpoint is SUBSTITUTED into the member's own plan. Chosen —
   the question is removed rather than bounded, at one dict entry per
   selector per piece, and the re-location is saved. Measured by
   reverting it (evidence.md, task 4.3): the member re-locates the
   selector's surface inside the piece
   (`[Crossing(..., primitive='>=', level=0.0, t=0.5)] != []`) and
   flipping the forced branch stops changing the answer
   (`0.0 != 1.0`).
3. Reporting the LAST landing of the stretch. Rejected: `Run._landed`
   OVERWRITES `value + delta` with a reported landing, so a landing in
   piece 2 followed by motion in piece 3 would discard the motion.
   Measured by reverting to it (evidence.md, task 4.7): `1.0 != 3.0`,
   exactly the design's prediction.
4. **The block's own ADVANCED ABSOLUTE at the stretch's end** — the
   landing plus every later piece's increment. Chosen. Measured on
   `LandedCarry` at `dt = 1.0`, cranked by `4.0` with `shift` `0 -> 1`:
   `carry.travel` commits `3.0`, the landing `1.0` from the piece before
   the detent plus the `2.0` the higher wheel gives it after; run to the
   first half only (`dt = 0.5`) it commits `1.0`, which is what "the last
   landing" would have committed for the whole tick.

**Where membership is decided.**

1. At CLASS DEFINITION, where ADR-121 recognized its self-read. Rejected:
   a cycle is a property of the LINKED TREE, not of one class body — the
   Curta's lever and its dials are different classes, and the shift that
   makes them a cycle is a relation of the root's. The records with
   RESOLVED ends exist only after construction (`spikes/membership.py`
   walks `_units(root)` over a freshly constructed, unrendered tree and
   prints all three records with their resolved driven slot identities
   and `direction=None`).
2. At COMPILE, where every other program refusal lives. Rejected by the
   measurement above: without a self-read the rest render refuses the
   model first and the compile never runs.
3. **A PRE-PASS over the records, before the rest render.** Chosen.
4. Marking only relations naming SEVERAL ends. Rejected: three shapes
   would then never reach the compile, and the refusals this decision
   promises for them would be dead text — a cycle through a
   single-ended relation, a cycle through a WIRING or a DERIVED
   COORDINATE (`_check_wiring` accepts any coordinate the declaring
   parent declares, so a parent joint another relation determines may be
   wired into a child and carried back), and, symmetrically, an SCC that
   reaches NO banked coordinate, which `_reaching_the_bank` drops before
   the compile orders anything and which must NOT be marked. **Every
   record on a cycle that determines at least one BANKED end** is the
   rule that admits the first two and excludes the third, and it is what
   makes the pre-pass and the compile agree by construction.

**Publication.**

1. A `block` key, and a selector list, in the document. Rejected on
   ADR-110's own line: the document carries what compile time DECIDED and
   not what is computable from it (`sources` is published because it is a
   decision about candidates; `constraints` is derived and is not).
   Membership and selectorhood are both functions of the published edges.
2. **Re-derivation from `needs`, `gives` and the published `level`
   expressions.** Chosen, with no new key. Measured in the test itself
   (evidence.md, group 8): the SCC over `needs`/`gives` with
   `needs ∩ gives` excluded gives `{1, 2}` and
   `{carry.travel, higher.turn}`, and resolving each jump's `level`
   transitively through the document's `bindings` picks out `['>=', '<']`
   for the wheel and `['<', '>=']` for the lever.

## Decision

**A cycle every selection breaks is a BLOCK, and the program orders it
once per PIECE instead of once per program.** The nontrivial strongly
connected components of the dependency graph over the compiled candidate
edges — edge A before edge B when B `needs` a key A `gives`, a need an
edge itself gives excluded, which is ADR-121's self-read — are BLOCKS
(`_components`). Each is contracted to ONE compound `block` edge
(`_blocked`, `_block_edge`) carrying the union of its members' `needs`
and all their `gives`, so `_ordered` is Kahn over an acyclic program
again and `run.py` is unchanged in shape: `_pass`, `_locate`, `_along`,
`_group`, `_pushes` and `_landed` meet a block through the `Edge`
interface they already call. Everything outside a block is what it was.

**A SELECTOR is a jump node of a block member's law whose LEVEL QUANTITY
reads no coordinate the block determines** (`_selectors`), a placeholder
in that level resolved into the jump it replaced, transitively, exactly
as `_dependence` resolves ADR-121's dependence. Its branch is therefore
known before the block runs, from what the upstream edges already gave —
every name a block edge reads is in-block or UPSTREAM, because a
downstream edge giving it would be in the block. A node whose level
reads the member's OWN driven end is not a selector and stays where
ADR-121 put it, in the walked layer inside the piece.

**A source is SWITCHED when folding a selector's branch to ZERO removes
it from the law.** `_folded` sets placeholders to zero in the member's
SKELETON and folds `x*0 → 0`, `0*x → 0`, `0/x → 0`, `0+y → y`,
`y+0 → y`, `y−0 → y`, `0−y → −y`; `_reads_under` takes the folded
skeleton's free names with every surviving placeholder followed into its
own folded level, transitively. Measured on the fixture
(`spikes/fold.py`): the lever's skeleton is
`(((lower.turn * $j0) + (higher.turn * $j1)) * $j2)`, where `$j0` is
`shift − 0.5 < 0`, `$j1` is `shift − 0.5 >= 0` and `$j2` reads the
lever's own retained travel; with `$j1` folded to zero the edge still
reads `carry.travel`, `lower.turn` and `shift` and NO LONGER reads
`higher.turn`. The wheel's skeleton drops `carry.travel` under the
COMPLEMENTARY comparison. A branch counts as foldable only where the
primitive holds ZERO over an INTERVAL of its level (`_FOLDABLE`:
`floor`, `ceil`, `%`, the comparisons); `sign` does not, and a
`sign`-gated source counted as switched would admit at construction a
machine every tick refuses. The fold is MONOTONE, so ONE fold per member
— every foldable selector at zero at once — decides both what is
unconditional and what is switched.

**Refused at construction, by relation identity** (`_refuse_unselectable`,
`_Block.unconditional_cycle`, `_cycle_message`), naming the relations as
written and the classes that stated them: a block containing a WIRING or
a FORMULA, neither of which carries a jump node; a block whose members'
UNCONDITIONAL dependencies still form a cycle — today's message, kept,
extended with one sentence saying what a switch would be; an
INTERMEDIATE among a block's driven ends, because a block advances its
coordinates piece by piece and only a coordinate the run banks keeps
that history; and a block member driving a GROUP, because the fold is
computed per driven end off that end's own skeleton while a group's ends
are claimed and bound together. The check is NECESSARY and not
SUFFICIENT, and deliberately so: which branch VECTORS are reachable is
arithmetic about the selecting input, not structure, and deciding it is
a satisfiability question — a solver, the thing the note rules out.

**Over a stretch the selectors are located FIRST and the block runs
PIECE BY PIECE** (`_Block.increments`). Every selector's crossings are
located over the whole stretch by ADR-107's own machinery — solved where
the level is affine, sampled at `_SUBDIVISIONS` and bisected to
`_CROSSING_TOLERANCE` otherwise — merged by `_merged` under the same
tolerance, bounded by the same `_MAX_CROSSINGS`, in the members' own
order and each member's postorder, so the partition is deterministic. On
each piece the branches are read at the MIDPOINT (`_forced`), the
run-time fold gives each member's ACTIVE in-block reads, Kahn over those
gives the order (`_order`, memoised per branch VALUE vector), and the
members run over the piece with their in-block values carried forward.
Measured (`spikes/pieces.py`): a member run over `[0, 0.25]`,
`[0.25, 0.6]`, `[0.6, 1]` with its in-block value advanced between
pieces gives `0.5 + 0.5 + 0.0 = 1.0` — the same increment, the same
landing float `1.0` and the same crossing fraction `0.5` the
whole-stretch run gives; the negative control, the same three pieces
with the in-block value NOT advanced, sums to `2.0`.

**On a piece a selector is a CONSTANT for every member.** Forcing
reaches exactly two points, `JumpPlan._partition` (which skips locating a
forced node's crossings) and `JumpPlan._branches` (which returns the
forced value), and everything downstream — `_Retained.outer`,
`_Walk._decide`, `_tentative`, `_probe`, `_crossing`, `_searched`,
`_bisect`, `_skeleton`, `_level`, `_land`, `_far_side` — reads the same
`branches` map. So a member whose selector sits in layer one and whose
LATCH sits in ADR-121's layer three holds the forced branch through the
whole walk, including the far-side landing. A source a piece switched
OUT and has not yet determined is handed the block-advanced value it
holds at the piece's start, moving by `0.0`: every term reading it is
multiplied by a placeholder forced to zero, so the float is multiplied
by zero, and a constant level crosses nothing.

**What the block REPORTS for a landed coordinate is the ABSOLUTE value
it has advanced that coordinate to by the stretch's END** — the landing
plus every later piece's increment — because `Run._landed` commits a
reported landing absolutely and would otherwise discard the motion after
it. A coordinate no piece landed is reported as an increment only. Every
crossing is recorded at its fraction of the whole tick, and the located
crossings are sorted by that fraction before they reach the run's record,
because a selector's crossing is located over the stretch while a
member's own is rescaled out of its piece.

**A still-cyclic piece REFUSES the tick, transactionally**
(`_Block._refused`), naming the piece, the selector branches it was read
under and the relations on the cycle. `Run.integrate` already catches
`UnsupportedLaw` around the whole segmented tick, so no new rollback is
written. Measured:

```text
UnsupportedLaw: over the piece [0.5, 1.0] of this tick the relations
(crank, shift, higher.turn) drives lower.turn, (crank, shift, lower.turn)
drives higher.turn form a cycle the run cannot order: each waits on a
coordinate another determines, and the selection this piece was read
under leaves every dependency on this cycle active. The selectors read
lower.turn: >= on (shift - 0.5) reads 1.0; higher.turn: >= on
(shift - 0.5) reads 1.0. The tick committed nothing: ...
```

with `sim.state`, `sim.tick`, `sim.crossings` and `sim.stops` the
previous tick's and the command that moved `shift` reporting `refused`.

**A block relation binds NOTHING at rest under a running root**, as a
self-read relation does (ADR-121): `_step_relation` records a marked
record solved `'forward'` and applies no law, under
`_under_running_root` and only there, so the driven coordinate's rest
value is the author's own guarded rest default and construction refuses
by name when there is none. Membership is therefore decided BEFORE the
rest render — in practice before the FIRST enumeration of a
construction, since `Sim.__init__`'s own driver walk is one and a
producer binding declared defaults (`bind_declared_defaults`) is another,
and a marked cycle is refused by either — by a pre-pass
(`_block_members`) that walks `_units(root)`
over the linked tree, builds one dependency graph over RESOLVED DRIVEN
SLOTS from every relation, wiring and derived coordinate taken FORWARD AS
DECLARED, and marks every relation record in a nontrivial SCC holding at
least one BANKED driven end. Wirings and derived coordinates are in the
graph so the cycle is SEEN and carry no mark; an SCC reaching no banked
coordinate is left alone (`UnbankedCycle` constructs, bank
`{'crank': 0.0, 'wheel.turn': 0.0}`). The pre-pass is idempotent and
recomputes from the records, so a second simulation over a shared tree
decides afresh. **Two outcomes change**, both measured: a SELECTED cycle
with no self-read, `DoublyBound` today (`SelectedBare`), now constructs;
and an UNCONDITIONAL one, `DoublyBound` today (`UnconditionalBare`), is
now refused by the compile with the cycle message naming every relation
on it. Under any other time base nothing is marked and nothing changes.

**Membership is computed twice and the two readings are ASSERTED equal**
(`_agree_on_membership`, raising `MembershipInvariantError`, an internal
invariant of the compile whose message ends "Construction refused the
model."). They agree by construction: the pre-pass keeps only an SCC with
a banked driven end, `_reaching_the_bank` drops a candidate only when NO
driven end reaches the bank, and an intermediate among a block's gives is
refused.

**A document whose program carries a block is a VERSION 7 document**
(`serializer.BLOCK_DOCUMENT_VERSION`, `_carries_a_block`, read off the
published edges exactly as a consumer re-derives it). Seven dominates
six: a block says nothing about self-reads and a self-read says nothing
about blocks. The members publish as ORDINARY law edges, contiguous at
the block's position in the producer's own deterministic order, and that
order is a LISTING and not an execution order — which is the breaking
part and why it gets a version rather than a flag. `Program.described()`
gains one `block` line naming the members' driven ids at the block's
position, followed by each member's ordinary edge line, so the identity
distinguishes a program carrying a block and two blocks of different
membership, and a program with no block prints what it printed before,
character for character. Measured (evidence.md, group 8): `ShiftedCarry`
publishes `version: 7` while `Train` still publishes `5` and `Clearing`
`6`; its published edges give `[['lower.turn'], ['higher.turn'],
['carry.travel']]` in that order, the block's two members ORDINARY law
edges contiguous at its position, each carrying `affine`, `description`,
`expressions`, `gives`, `kind`, `needs`, `plans`, `stated_by` and
nothing else;
`program`'s keys are unchanged; and placeholder minting over a document
with a block is still `_j0 … _j8` in edge order and then postorder over
the flat list of law edges (2 + 4 + 3).

**The conformance corpus (ADR-111) is what pins the two runtimes to each
other**, and it gains three `REQUIRED` features the generator refuses a
corpus without — a switched source, a selection crossing inside a tick,
and a tick carrying both a selection crossing and a stop — each detected
from the document and the tick log the way the existing ones are, with
the block and its selectors re-derived as a consumer must. Regenerated:
`removed: []`, `changed: []`, `added: [('RangedBlock', 0.05, 8),
('ShiftedCarry', 0.05, 20)]`, the pre-existing entries' order preserved,
19 scenarios over 16 machines and 356 ticks.

**The accuracy contract.** A selection change ALONE moves nothing — not
approximately zero, exactly the number zero, because a selector is a jump
node and ADR-107 subtracts every jump, so both pieces evaluate a constant
law at two equal points. A command taken in one tick, in twelve and in
two hundred and forty agrees within the run's own agreement window
`1e-9·max(1, |a|, |b|)` for every coordinate and for the travel each
command admits, and EXACTLY for each command's status and for every
discrete reading taken away from a surface. Admitted travel is NOT
promised bit for bit across two partitions: `Command.admits` returns a
per-tick difference and `Run.integrate` accumulates it once per tick, so
240 ticks are a float sum of 240 differences where one tick is a single
difference — a property of the command bookkeeping that has nothing to do
with blocks, and one this decision does not promise away.

**The selected machine equals the frozen twin.** Cranked by `2.0` over 12
ticks of `dt = 1/12` (evidence.md, task 4.1):

| coordinate | selected, `shift = 0` | `FixedZero` | selected, `shift = 1` | `FixedOne` |
| --- | --- | --- | --- | --- |
| `lower.turn` | `1.9999999999999998` | `1.9999999999999998` | `0.0` | `0.0` |
| `higher.turn` | `1.4999999999999998` | `1.4999999999999998` | `1.9999999999999998` | `1.9999999999999998` |
| `carry.travel` | `1.0` | `1.0` | `1.0` | `1.0` |

At `dt = 1.0`, one tick, the selected machine gives `lower.turn 2.0`,
`higher.turn 1.5000000000000002`, `carry.travel 1.0` against the twin's
identical values — and against `spikes/arbitrary.py`'s
`1.4800000000000013` under declaration order and `0.0` under the reverse.

## Consequences

- **The Curta's requirement is sayable, and what the model owes is
  stated rather than hidden.** The seven-relation `CurtaCarriage` fixture
  — three fixed levers and four dials, refused today as ONE cycle naming
  all seven relations — constructs and operates: with the carriage DOWN
  and every lever standing at `1.0`, `position` is retired `blocked` with
  `0.0` admitted and the stop names `('position',)`; lifted first, the
  same shift completes. Cranked at position 1 at `dt = 0.02` it reads
  `dial2 = 72`, `dial3 = 72` (each `+36` from the lever facing the dial
  below it) with every lever at `1.0`; lift, shift to position 2, drop —
  every coordinate but the carriage's unchanged; reset while lifted — the
  levers return to `0.0` and `dial3` still reads `72`; crank again —
  `dial2 = 108` from the crank alone and `dial3 = 144` from the crank
  plus the lever it NOW faces (evidence.md, tasks 5.5 and 5.6). What the
  model owes in return: every association written as a comparison factor
  on the carriage's own JOINT coordinate rather than on the `position`
  driver, the lift as a second factor, and a guarded rest default on
  every dial and every lever. The project's own migration is project work
  in the project's repository; what it needs is listed in the change's
  design.md §12, including the trap that the existing pose model's
  triangular hat is built on `clamp01`, a CALL and therefore not a jump
  node at all.
- **A run-time refusal is a NEW failure mode.** Until now a running model
  that constructed could refuse a tick only for a conflict, an
  over-crossed law or an unintegrable level; a piece whose active graph is
  still cyclic is a fourth. It is transactional and it names the
  selection, but it is a failure an author can only meet by RUNNING. The
  construction check catches every cycle no selection can break;
  eliminating the rest means deciding which branch vectors are reachable,
  which is a solver.
- **A stop on a block coordinate is SEARCHED, and it is the expensive
  case.** `Edge.affine` is `False` on every give of a block, so
  `Run._locate` takes `_searched`: up to `_SUBDIVISIONS` samples plus
  `_BISECTION_ROUNDS`, each of which re-locates the selector partition
  and re-runs the whole block. Measured at `dt = 0.02`
  (`tools/bench_selection.py`, best of three, one job at a time):

  | bench | ms/tick |
  | --- | --- |
  | `Train` — the control, no block | 0.482 |
  | `FixedZero` — the frozen twin as three separate edges, the machine the project can build today | 0.799 |
  | `ShiftedCarry` — one block of two, no crossing | 1.306 |
  | `ShiftedCarry` — the tick that crosses the detent (two pieces) | 2.671 |
  | `RangedBlock` — the tick that drives a block coordinate INTO its range | 17.186 |
  | `CurtaCarriage` — one block of seven, four dials and three levers | 10.658 |

  Against the honest baseline, a two-member block costs **1.6x** the same
  laws run as separate edges with the carriage frozen, and **2.0x** on
  the one tick that crosses a detent — "about `p` times the members'
  ordinary cost", with `p` of 1 and 2. The searched stop is **22x** a
  quiet tick of the same machine. Classifying a block give as affine
  under a fixed branch vector would turn that search into `_piecewise`;
  it is a follow-up with a measurement behind it, not this decision.
- **Nothing without a block changes, and it was measured rather than
  argued.** The whole suite is green at **3002 passed, 4 skipped, 1679
  subtests** in 345.74 s; the named running and export suites at **611
  passed, 762 subtests** in 61.13 s. Every pre-existing corpus entry is
  byte-identical and none moved by so much as an ulp. `Train` publishes
  version 5 and `Clearing` version 6 exactly as before, a law with no
  block is partitioned exactly as before (`CurtaInterface`'s dial keeps
  its 2 dependent and 2 independent nodes and its program is still six
  plain `law` edges), and the control bench reads 0.482 ms/tick — this
  machine's number for a program with no block at all, which no test
  pins.
- **ADR-121's walk moved a held coordinate by one ulp, and this cycle
  fixed it because the promise depends on it.** `_Walk.run`'s `own_at`
  and `_Walk._probe` computed `own_left + self._skeleton(s, branches) -
  base`, which Python takes as `(own_left + S) - base`; when `S == base`
  but `|S|` is comparable to `|own_left|` the sum rounds and a self-read
  member whose skeleton was UNCHANGED over a piece still moved whenever
  any of its sources moved. Pre-existing on main and reproduced with NO
  block anywhere: a crank at `72.0`, a wheel resting at
  `71.99999999999996` and `hoist` moved by `0.2` left the wheel at
  `71.99999999999994` before the fix and at `71.99999999999996` after.
  Both expressions are now parenthesized as `own_left + (S - base)` and
  nothing else in the walk changed. It is fixed HERE because "a selection
  change alone moves nothing" is a BIT-FOR-BIT promise that cannot be
  asserted while the walk adds an ulp of its own — and the strengthened
  contract test now asserts bit-for-bit equality for every block
  coordinate across a lift/shift/drop. One assertion had to be RELAXED in
  exchange: the reset cam drives each lever exactly onto its own
  `travel > RETURNED` surface, and the levers now rest at
  `1.1102230246251565e-16` rather than exactly `0.0` — one minus the
  float sum of ten increments of a tenth. The old exact `0.0` was the
  walk's error cancelling the command bookkeeping's, and a reading taken
  ON a surface is explicitly outside the exact promise.
- **ADR-113's pushing test cannot see a push that needs TWO inputs moving
  together, and the tick is then refused rather than answered wrongly.**
  `Run._pushes` displaces ONE input with the others held, so an input
  that reaches a stopped coordinate only once ANOTHER input has moved the
  selection contributes nothing to the probe, `Run._group` comes back
  empty, and the run raises `StopInvariantError: ... locating the stop
  stopped no input that was moving`. Measured on `RangedBlock` and,
  identically, on a machine with NO block at all — a clutch
  `(shaft & sleeve).drives(wheel.turn, law=s * (v > 0.5))` with
  `wheel.turn` ranged `(None, 0.3)`, `sleeve` and `shaft` both `0 -> 1`
  in one tick of `dt = 1.0` — on this worktree and on the tree before it
  alike. It is PRE-EXISTING, this decision inherits it and does not lift
  it, and lifting it means displacing the selecting input alongside the
  candidate, which is a change to the pushing test rather than to the
  block.
- **The candidate table is over-broad on purpose.** `Program.sources`
  treats a block as one node, so every input reaching any member is a
  candidate for a stop on any other — measured as
  `['crank', 'shift', 'spin']` for `carry.travel` on `RangedBlock`. The
  ANSWER is still right, because `_pushes` filters per tick and runs the
  WHOLE block before its `key in edge.gives` break: `spin`, which reaches
  the stopped lever only through an inactive selection, retires
  `completed` with its whole `1.0` while `crank` retires `blocked`. The
  cost is one extra propagation per spurious candidate, on a blocking
  tick only.
- **A `sign`-gated source is never switched.** A model that gates its
  only conditional dependency on `sign` is refused at construction with
  the cycle message rather than admitted, which is the intended answer —
  `sign`'s zero is one point, so such a gate is active on every piece of
  positive width — but it is a shape an author could reasonably expect to
  work, which is why the refusal says so in its own words.
- **Two shapes stay out.** A block member driving a GROUP is refused by
  name, because the fold is computed per driven end off that end's own
  skeleton while a group's ends are claimed and bound together; splitting
  such a group is a follow-up nothing has asked for. And a cycle that
  reaches no banked coordinate is deliberately untouched — the shape a
  `.repeat()` child's plain ports make, which the compile drops before it
  orders anything, and which ADR-121 already recorded as unable to be a
  running machine for its own reason.
- **A version 7 document breaks every current consumer, which is the
  point.** A consumer must re-derive the block from `needs` and `gives`,
  re-derive its selectors from the published `level` expressions, fold a
  published skeleton by the same rules, cut the stretch at the selectors'
  crossings and order the members per piece. One that executes the
  published order moves the machine by whatever that order happens to
  give — silently, and by a different amount for each order it might have
  chosen. The browser viewer executes such a document in its own cycle in
  its own repository, held to the corpus this change regenerates; this
  cycle records the producer side.
- **Follow-ups, recorded rather than guessed at:** classifying a block
  give as affine under a fixed branch vector, so a stop on one is
  `_piecewise` rather than searched; a joint walk for a driven group one
  of whose members is switched; naming the SELECTOR ids in the `block`
  line so a change in which nodes qualify is visible in the identity
  independently of the expression change that caused it (redundancy
  today, since the expression change already moves the identity); and
  ADR-113's pushing test, which remains net over the stretch and one
  input at a time.

## Amendment, 2026-09-16 (`pin-the-block-order`)

The `ShiftedCarry` scenario this decision added to pin the corpus against
a consumer that executes a block's published listing as an execution
order did not, in fact, discriminate it. Measured
(`pin-the-block-order` evidence.md, `spikes/order.py`,
`spikes/patched_corpus.py`): with `_Block._order` monkeypatched at
runtime to return the members in the order they are LISTED — exactly
what a version 7 consumer that ignored this ADR's own "SHALL NOT execute
the members in the published order" would do — the committed
`ShiftedCarry` entry replayed GREEN under both the listing order and the
two members reversed, every bank value, crossing, stop and command
identical over twenty ticks. Across the whole 19-scenario corpus the
listing order reproduced every committed value; the only disagreement
anywhere was `RangedBlock` tick 1's crossing COUNT (2 against 3), a
different feature. The cause was the scenario's own arithmetic: cranking
by `2.0` over `0.2 s` at `dt = 0.05` steps `carry.travel` through
`0.5, 1.0` and lands it on the higher wheel's `>= 0.5` gate EXACTLY at a
tick boundary, so the order in which the block's two members are read
within a tick never has a chance to matter — reading the gate at the
left end of a tick and reading it after the lever has advanced within
that tick give the same answer.

The decision itself is unchanged: a block's members are still an ordered
LISTING and not an execution order, and nothing about how the run orders
a piece moved. What changed is the scenario meant to hold a consumer to
that promise. `pin-the-block-order` cranks the same scenario by `2.0`
over `0.3 s` instead — six ticks of `1/3` — so `carry.travel` reaches
`0.5` strictly inside tick 2. The listing order then loses one sixth of
a turn of `higher.turn` from that tick onward and never heals it (`3.5`
against `3.3333333333333335` by tick 20): 21 disagreements against zero
before. `tests/test_running_corpus.py::BlockOrderTest` now replays
`ShiftedCarry` under the patched order and asserts the divergence
directly, rather than trusting the feature list of `CoverageGuardTest`
as a proxy for it, and `uncovered_features` refuses a corpus missing the
new `'an in-block gate crossing inside a tick'` feature. No other
scenario, and nothing under `solid_node/`, moved.
