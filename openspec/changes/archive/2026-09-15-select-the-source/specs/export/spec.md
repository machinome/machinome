## MODIFIED Requirements

### Requirement: A running root's document publishes the compiled program

A document declaring `version: 5` OR ABOVE SHALL carry a top-level
`program` object,
beside `drivers`, `instructions` and `bindings` and ahead of `root`, holding
what COMPILE TIME decided about the machine and nothing the tick computes.

Every expression it carries SHALL be written in the document's existing
expression language and SHALL participate in the same ordered `bindings`
table the tree's expressions use, so no subexpression is published twice and
no producer-local sharing syntax appears anywhere in the document. The
object SHALL be ordered deterministically for a given tree, so republishing
an unchanged model produces a byte-identical document.

The producer SHALL declare `version: 7` for a program carrying a BLOCK —
a set of two or more edges whose dependencies are cyclic, ordered per
piece under the simulation requirement "A selection decides which sources
a law reads" — `version: 6` for a program with no block at least one of
whose LAW edges names one of its own `gives` among its `needs` — a law
that reads the coordinate it drives — and `version: 5` for a program with
neither, whose document SHALL be byte-identical to the one it published
before this rule existed. The shape of the document SHALL NOT otherwise change: the self-read
is `needs ∩ gives`, no key is added for it, and the free names of a law
edge's expressions SHALL still be exactly the ids in `needs`. NO KEY is
added for a block either: a consumer SHALL re-derive it as the strongly
connected components of the graph over the edges' own `needs` and
`gives`, with `needs ∩ gives` excluded, and SHALL re-derive its SELECTORS
as the jump nodes of its members' published plans whose `level` —
placeholders resolved transitively into their own jumps' levels — names
no id the block gives.

Each version says what a lower consumer would get wrong. **Version 6**
carries a law edge that reads the coordinate it drives: a runtime that
evaluated such an edge as the difference of its two endpoint evaluations
would read the self-read at BOTH ends, freeze the branch it selects and
move the part by a different mechanism without saying so. **Version 7**
carries a block: the published ORDER of its members is a listing, not an
execution order, so a runtime that executes them in it moves the machine
by whatever that order happens to give — silently, and by a different
amount for each order it might have chosen.

Where a self-read edge's driven coordinate ends a tick at a crossing,
what it is COMMITTED at is behaviour rather than a document key: a
runtime that commits it a single float short of the far side re-engages
the gate and diverges from the corpus's bank on a LATER tick, far outside
the agreement window, which is where that rule is pinned.

`program` SHALL carry:

- `identity`: the compiled program's identity — a digest over the root
  class, the bank's ids, the inputs' declarations, the spans and every
  edge's ends, direction and expression — so a state taken against one
  program is refused against another.
- `clock`: the free name elapsed simulation seconds bind to, under the
  requirement "A running document's clock is a published name".
- `coordinates`: one entry per BANK id, in the compiled program's own order
  — inputs first, then joint coordinates, each sorted — each carrying
  `kind` (`"input"` for a declared driver, `"coordinate"` for a joint
  coordinate), `initial` (the value the untimed REST POSE gave it), and,
  for a joint coordinate, `unit` (the joint's declared unit, or `null`). An
  input entry SHALL NOT repeat `unit`, `dtype`, `scale`, `range` or
  `default`: the document's `drivers` table publishes them under the same
  qualified id, and the two tables SHALL name exactly the same set of ids.
- `intermediates`: the sorted qualified ids of every value a compiled edge
  determines that the bank does NOT hold — a plain port, a derived
  coordinate — which a consumer recomputes from the bank on every tick and
  never stores. A value NO compiled edge determines SHALL NOT be listed:
  the end of a relation left to the ordinary enumeration is not part of
  the program and SHALL NOT be published as one, so every id here is
  named in the `gives` of an `edges` entry.
- `edges`: one entry per compiled edge, IN PROGRAM ORDER, defined by the
  requirement "The published edges say what each one reads, gives and
  computes". PROGRAM ORDER is a topological order of the dependency graph
  with each BLOCK contracted to one node; a block's members SHALL appear
  CONTIGUOUSLY at that node's position, in an order deterministic for a
  given tree. A consumer SHALL NOT execute a block's members in that
  order: it SHALL re-derive the block and its selectors, cut the stretch
  at the selectors' crossings, and order the members on each piece, as
  the producer does. It SHALL fold a published `skeleton` by the SAME
  rules the simulation requirement "A selection decides which sources a
  law reads" states — the same folding arithmetic, the same rule about
  which primitives hold a zero branch on an interval of their level, and
  the same distinction between the single compile-time fold and the
  run-time substitution of the branches actually read — because those
  rules decide the ORDER the members run in on every piece, and the
  conformance corpus pins the bank that order produces.
- `spans`: one entry per banked coordinate whose joint declares a range,
  keyed by its qualified id, carrying `low` and `high`, each `null` for
  unbounded, a number, or `{"expression": <text>}` for a bound stated as an
  expression over that coordinate's OWN id and, for a bound that reads
  other coordinates, the qualified ids it reads — the same ids the
  `coordinates` table publishes.
- `sources`: for each bank id and each intermediate, the sorted list of
  INPUT ids that reach it through the program — the candidate table a
  stop's blocked group is filtered out of.
- `limits`: the constants the algorithm is defined by, as numbers, so a
  consumer cannot silently differ from the producer: `crossing_tolerance`,
  `subdivisions`, `bisection_rounds`, `max_crossings` and `agreement` (the
  relative window inside which two increments on one coordinate are called
  equal).

The producer SHALL REFUSE to publish a program naming a coordinate or
intermediate whose qualified id could not be computed from its position in
the tree, naming the node and the reason: a fallback name derived from a
class name is not unique across two instances of that class, and publishing
it would put two different values under one name in one expression scope.
That refusal SHALL be over the coordinates the program COMPUTES — the
bank's, and the ends its compiled edges read and give — and over nothing
else: a value the ordinary enumeration recomputes from the bank, whose
relation reaches no bank coordinate, is not part of the program, is
published nowhere in it, and SHALL NOT refuse the document however its
node is named. A machine whose optional part this render omits, and a
machine whose `.repeat()` children own a port a relation drives, SHALL
therefore publish.

The producer SHALL REFUSE a running root on which a declared driver or a
joint coordinate qualifies to the id `time`, naming it and the reservation:
`time` is the one snapshot entry that is global by contract and the name a
running document's clock is published under.

Every entry of `program.coordinates`, input or joint coordinate, SHALL
carry a `domain` field, so a consumer's readouts and jog controls need no
second reading of the tree. For a JOINT COORDINATE its value SHALL be the
declared domain of the port the joint owns — `rotational`,
`translational` or `signal`, as the port kinds name them — beside its
unit. For an INPUT its value SHALL be `null`: a driver declaration states
a default, a range, a unit, a dtype and a scale, and no domain, and the
producer SHALL NOT derive one from the unit. The document SHALL NOT
publish a `dt`: the step is the executing runtime's choice, the supported
law class is exact across its kinks and locates its jumps and stops
inside whatever tick they fall in, and the conformance corpus pins each
machine's step per scenario.

Publication SHALL succeed over a tree a live running simulation owns and
SHALL leave that simulation's ownership, bank and ability to advance
intact: the publication binder is admitted over a run-owned slot and the
run's binder is restored afterwards.

#### Scenario: Coordinates publish their domain

- **WHEN** the Pascaline module's running root is exported
- **THEN** every `program.coordinates` entry carries `domain`, each arbor
  coordinate reading `rotational` beside its unit, and each dial — a
  declared driver, which states no domain — reading `null`

#### Scenario: Publishing does not disturb a live run

- **WHEN** a running simulation is halfway through a move and the tree's
  document is serialized in the same process
- **THEN** the document is produced, the simulation's bank and commands
  are unchanged, and the next tick advances exactly as it would have

#### Scenario: The program names the bank and the edges

- **WHEN** a running root with three drivers, nine joint coordinates and
  nine relations is published
- **THEN** `program.coordinates` has twelve entries with the drivers' ids
  first, each joint coordinate entry carries the rest pose's value and the
  joint's unit, and `program.edges` lists the nine relations in the order
  the run propagates them

#### Scenario: The drivers table is the one declaration

- **WHEN** a version 5 document is published
- **THEN** every `program.coordinates` entry whose `kind` is `"input"` is a
  key of the document's `drivers` table and every key of that table is such
  an entry, and no declaration field is repeated inside `program`

#### Scenario: A plain port is an intermediate, not a bank entry

- **WHEN** a running root drives a plain port from a driver and drives a
  joint coordinate from that port
- **THEN** that port's qualified id is in `program.intermediates`, is not in
  `program.coordinates`, the edge that computes it names it in `gives`,
  and `program.sources` names the driver that reaches it

#### Scenario: A plain port the program does not compute is published nowhere

- **WHEN** a running root drives a plain readout port from a joint
  coordinate and no relation carries that port back to a bank coordinate
- **THEN** the document is published, that port's qualified id is in
  neither `program.intermediates` nor `program.coordinates` nor
  `program.sources`, no `edges` entry names it, and the pose expression
  the port drives still resolves to the joint coordinate's qualified id

#### Scenario: A repeated child's driven port does not refuse the document

- **WHEN** a running root drives the `height` port of its `.repeat()`
  children, whose list-held names are not legal id segments
- **THEN** the document is published, no copy's port appears in
  `program`, and the same root without `Time.running()` publishes the
  document it always has

#### Scenario: An omitted part's driven coordinate does not refuse the document

- **WHEN** a running root's parameter omits an optional part whose joint
  one of its drivers drives
- **THEN** the document is published, the omitted part's coordinate
  appears nowhere in `program`, and the same root with the part fitted
  publishes it as a bank coordinate

#### Scenario: An omitted part the program still reads is refused

- **WHEN** a running root's parameter omits a part whose coordinate a
  chain of relations reaching a bank coordinate passes through, so a
  compiled edge still reads and gives it
- **THEN** publication is refused naming that node and saying a fallback
  class name is not unique, and no document is written

#### Scenario: A declared range travels as a span

- **WHEN** a running root declares
  `range=(lambda turn: 36 * floor(turn / 36), None)` on a joint
- **THEN** `program.spans` carries that coordinate with `low` an expression
  over that coordinate's own id and `high` `null`

#### Scenario: A bound reading other coordinates travels as a span naming them

- **WHEN** a running root declares
  `range=(0, Bound(lambda turn, a, b: 90 * (abs(a) <= 0.05) * (abs(b) <= 0.05), reads=(p1.lift, p2.lift)))`
  on `plug.turn`
- **THEN** `program.spans` carries `plug.turn` with `high` an expression
  whose free names are drawn from `plug.turn`, `plug.p1.lift` and
  `plug.p2.lift` -- here `plug.p1.lift` and `plug.p2.lift`, the two the
  expression actually reads, its own coordinate not appearing in it --
  every one of them a key of `program.coordinates`, and the document's
  version is `5`

#### Scenario: A program with a self-read law is a version 6 document

- **WHEN** a running root states
  `(ring & wheel.turn).drives(wheel.turn, law=missing_tooth)` and is
  exported
- **THEN** the document declares `version: 6`, the law edge's `needs`
  holds `ring` and `wheel.turn` and its `gives` holds `wheel.turn`, the
  expression's free names are exactly those in `needs`, and no key was
  added to `program` for the read

#### Scenario: A program with no self-read law is unchanged

- **WHEN** a running root that declares no self-read law is exported
  before and after this change
- **THEN** both documents declare `version: 5` and are byte-identical,
  the program's ordering and its minted names included

#### Scenario: A self-read law publishes its plan like any other

- **WHEN** the same self-read law gates on
  `(wheel + g) - 360 * floor((wheel + g) / 360) >= 2 * g`
- **THEN** its edge carries one plan whose `jumps` hold the `floor` node
  over `(wheel.turn + g) / 360` and the comparison over the remainder,
  each marked affine, and whose `skeleton` does not name `wheel.turn` at
  all

#### Scenario: The program's expressions share the document's bindings

- **WHEN** a running root's law and one of its jump plans read the same
  subexpression
- **THEN** that subexpression appears once, as a `bindings` entry, and both
  the law's expression and the plan reference it by name; no `program`
  expression carries producer-local sharing syntax

#### Scenario: Republishing an unchanged running model changes nothing

- **WHEN** an unchanged running model is published twice
- **THEN** the two documents are byte-identical, the program's ordering and
  its minted names included

#### Scenario: An id that cannot be qualified is refused

- **WHEN** a COMPILED edge of a running root's program reaches a value on
  a node whose qualified id is not computable — its instance path is not
  derivable, or a name on that path is not a legal id segment
- **THEN** publication fails naming that node and saying a fallback class
  name is not unique, and no document is written

#### Scenario: A driver named like the clock is refused

- **WHEN** a running root declares a driver whose qualified id is `time`
- **THEN** the simulation refuses at construction, naming the id and that
  `time` is reserved for the clock

#### Scenario: A program carrying a block declares version 7

- **WHEN** a running root whose relations form a block — two laws each
  reading a coordinate the other determines, each behind a comparison on
  a third input — is exported
- **THEN** the document declares `version: 7`, its `program.edges` lists
  the two members contiguously, and no key beyond the ones this
  requirement lists appears anywhere in `program`

#### Scenario: A program with no block is byte-identical

- **WHEN** a running root with no block is exported before and after this
  rule exists
- **THEN** the two documents are byte-identical and declare the version
  they always did

### Requirement: The published edges say what each one reads, gives and computes

Each `program.edges` entry SHALL carry `kind` (`"law"`, `"wiring"`,
`"formula"` or `"check"`), `needs` and `gives` as lists of qualified ids
(`gives` empty for a check), `description` — the relation or derived
coordinate AS WRITTEN — and `stated_by`, the class that stated it, so a
consumer's refusal names what a reader can find in the model. The free
names each of the entry's expressions reads SHALL be exactly the ids in
`needs`, so no separate name list is published. That holds for a BLOCK's
members exactly as for any other edge: a block is published as its member
edges and never as an entry of its own, so nothing about an entry's shape
says whether it belongs to one.

**A law** SHALL carry three lists aligned with `gives`: `expressions`, the
law applied once to a symbolic token per source, or `null` where the law is
a constant and contributes nothing; `affine`, whether that driven end's
value is affine in its sources along a tick's path; and `plans`, `null`
where the expression carries no discontinuous primitive and otherwise a
JUMP PLAN carrying `skeleton` — the whole expression with every jump node
replaced by a branch placeholder — and `jumps`, the jump nodes IN THE
EXPRESSION'S POSTORDER, each with `name` (the placeholder the skeleton
reads it under), `primitive` (`floor`, `ceil`, `sign`, `%`, or a
comparison), `level` (the expression of the level quantity whose surfaces
it crosses, with every jump inside it already replaced by its own
placeholder) and `affine` (whether that level quantity is affine in the
sources). A `%` node SHALL NOT appear as a placeholder in the skeleton: the
skeleton SHALL already carry `a − q * b`, `q` being that node's
placeholder.

Branch placeholders SHALL be minted AT PUBLICATION and be unique across the
WHOLE document — `_j0`, `_j1`, … in edge order and then postorder — under a
prefix lengthened by a leading underscore for as long as any published id
matches `<prefix>` followed by digits. A placeholder that repeated across
two plans would let two different jump nodes share one published
subexpression.

**A wiring** SHALL carry `factor`: its value is `source × factor` and its
increment `Δsource × factor`.

**A formula and a check** SHALL carry `factors` aligned with `needs`,
`constant`, and `slot` — the derived coordinate's own id — and SHALL be
evaluated by these rules and no others:

- forward, where `slot` is in `gives`: the value is
  `constant + Σ needs[i] × factors[i]`;
- backward, where `gives` is one term of the formula: `needs` carries the
  slot FIRST with factor `0.0`, then the other terms, then the solved-for
  term itself with its own coefficient LAST, and the value is
  `(slot − constant − Σ other × factor) ÷ own`;
- an INCREMENT is the same arithmetic with `constant` replaced by zero;
- a check determines nothing: it PREDICTS `constant + Σ needs[i] ×
  factors[i]` over every need but the slot, and a tick in which that
  disagrees with the increment the slot received, relatively beyond
  `limits.agreement`, is a conflict that commits nothing.

#### Scenario: A law with a jump publishes its plan

- **WHEN** a running root's law is
  `4 + 72 * clamp01((angle − 360 * floor(angle / 360) − 113.5) / 11.25)`
- **THEN** its edge carries one expression, `affine: [false]`, and one plan
  whose `jumps` holds a single `floor` entry whose `level` is that source's
  id divided by 360, marked affine, and whose `skeleton` reads that entry's
  placeholder where the `floor` stood

#### Scenario: Placeholders are unique across the document

- **WHEN** a running root carries three laws each holding one `floor`
- **THEN** the three plans' placeholders are three distinct names, and no
  `bindings` entry is referenced from two of the three skeletons in place of
  two different jump nodes

#### Scenario: A remainder is written out in the skeleton

- **WHEN** a running root's law contains `angle % 360`
- **THEN** the plan's jump entry carries `primitive: "%"` and the skeleton
  carries the subtraction of that placeholder times the divisor rather than
  the placeholder alone

#### Scenario: A derived coordinate publishes its coefficients

- **WHEN** a running root declares `left = wrist + 2 * tool` and the rest
  render solves it backward into one term
- **THEN** that edge is a formula whose `needs` names the slot first with
  coefficient `0.0`, the other terms next, and the solved-for term last with
  its own coefficient

#### Scenario: A check publishes what it predicts

- **WHEN** a running root's derived coordinate and every one of its terms
  are determined by other edges
- **THEN** the program carries a `check` edge with empty `gives`, naming the
  slot and the coefficients it predicts from

#### Scenario: A block's members publish as ordinary law edges

- **WHEN** a running root carrying a block is exported
- **THEN** each member is an ordinary `law` entry carrying `expressions`,
  `affine` and `plans`, the free names of each expression are exactly
  that entry's `needs`, and the coordinate each member reads from another
  member is an ordinary id of `needs` with no marking of any kind

#### Scenario: A selector is derivable from the published plan

- **WHEN** a block member's law gates a source behind a comparison on a
  coordinate the block does not determine
- **THEN** that comparison appears in the member's plan as a jump entry
  whose `level` names only ids the block does not give, and whose
  placeholder the member's `skeleton` reads where the comparison stood

### Requirement: The two runtimes share a conformance corpus

The framework SHALL provide a generator that writes a JSON conformance
fixture from its own run, covering a set of small running roots, and the
framework's own suite SHALL replay that committed fixture and reproduce it.
The fixture is the contract between the framework's run and any other
runtime executing a published program: every expected value in it SHALL be
a value the framework's run PRODUCED, never a value recomputed a second way,
so a disagreement means the other runtime drifted.

The fixture SHALL carry, per machine: its name, its `dt`, the published
document's program-bearing keys — `format`, `version`, `drivers`,
`instructions`, `bindings` and `program` — verbatim; a SCRIPT of commands
(moves by a travel or to a value, rates, instruction triggers, a snapshot
and a restore) each naming the tick it is applied before and the handle its
outcomes are reported under; and EVERY TICK of the run, oldest first, each
carrying the whole committed bank, the crossings located in that tick, the
stops located in that tick, and every command created so far with its status
and the travel it has admitted. A sampled fixture SHALL NOT be accepted: a
divergence that heals between two samples is a divergence.

Agreement SHALL be EXACT for discrete state — tick numbers, command
statuses, coordinate, relation, primitive, bound and input names, crossing
surface levels, and the ORDER of every list — and within a stated RELATIVE
tolerance for floats: the bank's values, a crossing's or stop's fraction of
the tick, a stop's evaluated bound and a command's admitted travel. That
tolerance SHALL be the run's own agreement window, the same number the
document publishes as `program.limits.agreement`, because a consumer inside
it cannot manufacture a disagreement the run itself would not.

The generator SHALL REFUSE to write a corpus that does not exercise each of:
the five discontinuous primitives, a multi-source law, a stop located inside
a tick, a bound stated as an expression, a bound reading another
coordinate, a stop reached by the motion of what a bound reads — one whose
coordinate holds the same value before and after its tick — a command
retired `blocked`, a rate, a snapshot and restore, an instruction in each
of its two forms, a tick carrying both a crossing and a stop, a law that
READS THE COORDINATE IT DRIVES — one whose driven coordinate holds at its
gate while the input that reached it goes on moving — a tick in which a
self-read crossing and a stop both fall, a SWITCHED SOURCE — a law edge
reading a coordinate another member of its own block determines — a
SELECTION CROSSING located inside a tick, and a tick in which a selection
crossing and a stop both fall. The framework's suite SHALL test
that refusal directly, so the corpus's width is visible without running the
generator.

A framework test SHALL assert that each fixture machine's REAL published
document reproduces the fixture's own program-bearing keys, so the fixture
cannot drift from the producer it claims to come from.

#### Scenario: The framework reproduces its own corpus

- **WHEN** the committed fixture is replayed through the framework's run,
  machine by machine, applying each script entry before the tick it names
- **THEN** every tick's bank, crossings, stops and command outcomes match the
  fixture, exactly for discrete state and within the stated relative
  tolerance for floats

#### Scenario: The corpus carries the document it was run against

- **WHEN** a fixture machine's document is published afresh
- **THEN** its `program`, `drivers`, `instructions` and `bindings` equal the
  fixture's copy

#### Scenario: A corpus missing a primitive is refused

- **WHEN** the generator is asked to write a corpus whose machines contain
  no `%` law
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: Every tick is present

- **WHEN** a fixture machine runs for forty ticks
- **THEN** the fixture lists forty tick entries, in order, with no gaps

#### Scenario: A corpus missing a bound reading another coordinate is refused

- **WHEN** the generator is asked to write a corpus whose machines declare
  no bound reading another coordinate, or record no stop whose coordinate
  did not move
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing a law that reads its own driven coordinate is refused

- **WHEN** the generator is asked to write a corpus none of whose machines
  states a law reading the coordinate it drives, or none of whose ticks
  holds such a coordinate at its gate while the input reaching it moves on
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing a switched source is refused

- **WHEN** the generator is asked to write a corpus none of whose
  machines carries a block, or none of whose ticks locates a selection
  crossing
- **THEN** it refuses naming the uncovered feature and writes nothing
