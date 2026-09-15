## Why

A running program is ordered ONCE, by Kahn over the ends its edges
determine, and every mechanism the campaign has met so far has an
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
UNION over the six positions is cyclic, and the union is what the
compiled program orders.

The project's executable diagnostic is
`simulation/tools/shifted_carry_probe.py` in that repository: two
wheels, one fixed lever, and a live `shift` driver, with every
association written as a mutually exclusive comparison factor
(`c * (s < .5)`, `c * (s >= .5)`). Rerun on THIS worktree
(`spikes/reduced.py`), construction is refused before any operation:

```text
UnsupportedLaw: the relations
(crank, shift, clearing, carry.travel, higher.turn) drives higher.turn,
(lower.turn, higher.turn, shift, carry.travel) drives carry.travel
form a cycle the run cannot order: each waits on a coordinate another
determines. A running program is acyclic, because the rest render solved
every relation in one direction.
```

Specializing the SAME laws to either fixed position constructs and runs.
The union is the only thing refused.

**The refusal is the only thing standing between the model and a wrong
answer, and that too is measured.** With `_ordered` monkeypatched to
return the candidate edges in DECLARATION order, and again in REVERSED
order, the fixture compiles and the machine moves WRONGLY IN SILENCE
(`spikes/arbitrary.py`). Against the position-0 specialization, which
the framework orders correctly today and which is the ground truth:

| order | `lower.turn` | `higher.turn` | `carry.travel` |
| --- | --- | --- | --- |
| Kahn, position frozen at 0 | `2.0000000000000027` | `1.5000000000000018` | `1.0` |
| union, declaration order | agrees | `1.4800000000000013` | agrees |
| union, reversed order | agrees | `0.0` | `0.0` |

Declaration order loses a tick of the carry; reversed order never
carries at all. Nothing is reported in either case. That is exactly what
the requirement note means by "accepting an arbitrary evaluation order
supplies no such semantics".

**Three routes through the model as it stands fail, and the note names
them** (`workflow/docs/curta-shifted-carry-association.md`, "The
following do not meet the originating project's approved outcome"):
freezing the carriage as a construction parameter or rebuilding the run
on every shift (no retained state, no stable program or snapshot
identity); virtual per-dial lever memories or page-owned registers
(ADR-105 puts memory on real run-banked coordinates and nowhere else);
and computing an arithmetic answer separately and driving decorative
levers from it (then the lever is no longer the cause of the next
digit's motion, which is the mechanism under test).

What the model cannot express is a dependency that is CONDITIONAL. The
selection is already written — every association in the fixture is a
term multiplied by a comparison on the carriage — and the compiler
already reads a law's SKELETON, the expression with every jump node
replaced by its branch. What it does not do is notice that on a piece
where a comparison reads zero, the product it gates reads NOTHING.

## What Changes

- **A cycle every selection breaks is a BLOCK, and the program orders
  it once per piece instead of once per program.** The nontrivial
  strongly connected components of the union dependency graph — edge A
  before edge B when B needs something A gives, a self-read excluded —
  are BLOCKS. A block is a single entry in the program's order, so the
  program as a whole is acyclic again and nothing outside a block
  changes.
- **A SELECTOR is a jump node of a block member's law whose level
  quantity reads no coordinate the block determines.** Its branch is
  therefore known before the block runs, from the paths the upstream
  edges already gave. Nothing new is declared: the selector is the
  comparison the model already writes.
- **A source is SWITCHED when folding a selector's branch to ZERO
  removes it from the law.** Measured on the fixture (`spikes/fold.py`):
  the lever's skeleton is `(((lower.turn * $j0) + (higher.turn * $j1))
  * $j2)`, where `$j0` is `(shift − 0.5) < 0`, `$j1` is
  `(shift − 0.5) >= 0` and `$j2` reads the lever's own retained travel;
  with `$j1` folded to zero the edge still reads `carry.travel`,
  `lower.turn` and `shift` and NO LONGER reads `higher.turn`. The
  wheel's own skeleton drops `carry.travel` under the COMPLEMENTARY
  comparison, so at any value of `shift` at most one of the two
  dependencies is active and the pair is orderable. A branch counts as
  foldable only where the primitive holds ZERO over an INTERVAL of its
  level — `floor`, `ceil`, a remainder's quotient and a comparison do;
  `sign`, whose zero is a single point, does not and would admit at
  construction a machine every tick refuses. The fold is MONOTONE, so
  ONE fold per member — every foldable selector at zero at once — decides
  both what is switched and what is unconditional; it needs no new
  declaration, no new keyword and no new document key.
- **Over a stretch a block's selectors are located FIRST and the block
  runs PIECE BY PIECE.** Every selector's crossings are located over the
  stretch by the machinery ADR-107 already uses — solved where the level
  is affine, sampled and bisected otherwise, merged under the same three
  tolerances and bounded by the same maximum. On each piece the
  selectors' branches are read at the MIDPOINT, the folded ACTIVE graph
  is Kahn-ordered, and the members run over the piece in that order with
  their in-block values carried forward. Measured
  (`spikes/pieces.py`): a member run over `[0, 0.25]`, `[0.25, 0.6]`,
  `[0.6, 1]` with its in-block value advanced between pieces gives
  `0.5 + 0.5 + 0.0 = 1.0`, the same landing `1.0` and the same crossing
  the whole-stretch run gives, at the same fraction `0.5`. What the block
  REPORTS for a coordinate some piece landed is the absolute value the
  block advanced it to by the stretch's END — the landing plus every
  later piece's increment — because the run commits a reported landing
  absolutely and would otherwise discard the motion after it
  (design.md §3).
- **On a piece a selector is a CONSTANT for every member of the
  block.** The branch the block read at the midpoint is substituted into
  the member's own plan rather than re-located by it, so the ordering
  and the member's own branch reading cannot disagree — by construction,
  not by a tolerance.
- **A still-cyclic piece REFUSES the tick, transactionally**, naming the
  piece, the selector branches it was read under and the cycle. The bank,
  the tick count and the tree stand as they were, exactly as a conflict
  or an over-crossed tick does.
- **A block relation binds NOTHING at rest under a running root**, as a
  self-read relation does (ADR-121): its driven coordinate's rest value
  is the author's own guarded rest default, and construction refuses by
  name when there is none. Membership must be known BEFORE the rest
  render and is (`spikes/reduced.py`, `spikes/membership.py`): the same
  cycle with no self-read in its relations is refused by the rest render
  itself — `DoublyBound` where the driven ends carry rest guards,
  `UnreachedCoordinate` where they do not — long before the compile is
  reached, while the resolved records and their resolved driven slots
  already exist on a freshly constructed tree. The pre-pass therefore
  reads EVERY relation, wiring and derived coordinate of the linked tree
  as declared, and marks every relation on a cycle that determines a
  coordinate the run BANKS — so every such cycle reaches the compile and
  is answered there by name. **Two outcomes change**: a SELECTED cycle
  with no self-read, `DoublyBound` today, now constructs; and an
  UNCONDITIONAL one, `DoublyBound` today, is now refused by the compile
  with the cycle message that names every relation on it.
- **Refused at construction, by relation identity**: a block containing
  a wiring or a formula (neither carries a jump node, so neither can be
  switched); a cycle inside a block that NO selector assignment breaks
  (today's message, kept, for a plain unconditional cycle); an
  INTERMEDIATE among a block's driven ends (a block advances its
  coordinates piece by piece and only a coordinate the run banks keeps
  that history); and a block member driving a GROUP.
- **BREAKING for consumers: a document whose program carries a block is
  a version 7 document.** A version 6 consumer Kahn-orders the published
  edges and would refuse a cyclic program by name — or, worse, execute
  the published order and move the machine by the amounts the table
  above records. A document with no block stays byte-identical at its
  current version. The browser viewer executes it in its own cycle in
  its own repository; this cycle's conformance corpus is that cycle's
  contract.
- **Nothing without a block changes**: the same edges, the same order,
  the same document, every existing corpus scenario byte-identical, one
  extra boolean test at compile and none per tick.

## Capabilities

### New Capabilities

None. The change gives a meaning to a union the compiler already refuses.

### Modified Capabilities

- `simulation`: ONE ADDED requirement, "A selection decides which
  sources a law reads", stating the recognition, the refusals, the
  piecewise ordering, the transactional runtime refusal and the rest
  rule in one place; and MODIFIED "A relation's law is compiled to an
  expression over coordinate ids" (the program is ordered over the
  BLOCKS, and the unconditional cycle is refused there by name — it is
  specified nowhere today) and "A running root's simulation owns every
  driver and joint coordinate" (the rest rule).
  (`couplings` is deliberately NOT touched: nothing is declared
  differently, and the self-read's own rest rule was likewise stated in
  `simulation` rather than there — design.md §5.)
- `export`: "A running root's document publishes the compiled program"
  (version 7, and what IN PROGRAM ORDER means for a block's members),
  "The published edges say what each one reads, gives and computes" (a
  consumer re-derives a block and its selectors from `needs`, `gives`
  and the published `level` expressions, with no new key), and "The two
  runtimes share a conformance corpus" (three added features the
  generator refuses a corpus without).

## Impact

- `solid_node/simulation/sim.py`: a pre-pass at construction, before the
  rest render, marking the block members.
- `solid_node/motion/couplings.py`: `_step_relation` skips a marked
  record exactly where it skips a self-read.
- `solid_node/simulation/program.py`: `_relation_edge` records each law
  edge's selectors; a new `_Block` reading and a compound `block` edge;
  `_ordered` contracts each block to one node and keeps today's message
  for a cycle no selection breaks; `Program.described()` gains one
  `block` line; `Program.published` emits the members contiguously.
- `solid_node/simulation/run.py`: unchanged in shape — `_pass`,
  `_locate`, `_along`, `_group`, `_pushes` and `_landed` meet the block
  through the `Edge` interface they already use. Verified against the
  code rather than assumed (design.md §3, §7, §11): `_pushes`
  (`run.py:1055`) breaks on `key in edge.gives`, which with the compound
  block edge falls after the WHOLE block has run under one input's
  displacement — the granularity §7 needs; `_pushes`, `_along`
  (`run.py:1031`) and `Program.response` (`program.py:1493`) all call
  `increments` with two positional arguments, so a block must be
  complete with no `crossings`, no `tick` and no `landings`; and forcing
  a selector touches only `JumpPlan._partition` and `JumpPlan._branches`,
  which are inside `program.py`.
- `solid_node/core/serializer.py`: the version ladder.
- `tests/carriage_project/`, `tests/running_project/machine.py`,
  `tests/running-corpus.json`, `tools/generate_running_corpus.py`,
  `docs/driving.rst`, `docs/scenarios.rst`, `HISTORY.rst`, and the
  requirement note's status line.
- One ADR, **ADR-122** (NODE), extracted after implementation. It amends
  ADR-106's "edges are ordered by Kahn over the ends they determine".

### Non-goals

- **Executing a version 7 document in the browser.**
  `solid-node-viewer` is a separate repository with its own OpenSpec
  records; its cycle is held to the corpus this cycle regenerates.
  Requirement item 7's paired replay is discharged there, and this
  cycle records the producer-side content commit.
- **Migrating the Curta.** Requirement item 6 is project work in the
  project's own repository, and the pilot has assigned it elsewhere.
  What it needs from this cycle is stated in design.md §12: every
  association written as a comparison factor on the carriage's JOINT
  coordinate (`position.drives(registers.turn, ratio=20)` — the
  selector reads `registers.turn`, not the driver), the carriage lift as
  a second factor, and a rest default on every dial and every lever.
- **A coupled solver, or a fixed point per piece.** It would introduce a
  convergence tolerance — a fourth tolerance — and a per-piece iteration
  count, which ADR-121 rejected for the same reason. A block is ORDERED
  on each piece, never solved.
- **A new spelling.** No `Selected(...)` source end, no
  `drives(..., when=...)`, no relation-level condition, no new document
  key: design.md §1 records why each was rejected.
- **Freezing reads for a tick, or accepting the declaration order.** The
  note names both as supplying no semantics, and the table above is what
  the declaration order actually does.
- **Extending the running-only rest rule into untimed posing.** Under
  any other time base the same relations are what they are today, and
  the enumeration refuses them as it does today (`DoublyBound` or
  `UnreachedCoordinate`, both measured). Nothing new is declared, so
  there is nothing new to refuse.
- **A block member driving a GROUP.** The fold that decides an active
  dependency is computed per driven end off that end's own skeleton,
  and a group's ends are claimed and bound together, so a group one of
  whose ends is switched and another not would have to be split.
  Refused by name here and recorded as a follow-up (design.md §1).
- **ADR-113's net-over-the-stretch pushing test.** Its recorded limit is
  untouched; §7 shows why it already answers this mechanism's question.
