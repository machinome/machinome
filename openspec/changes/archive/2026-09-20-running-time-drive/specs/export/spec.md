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

A program carrying an explicit time-drive admission SHALL declare
`version: 10` under "A time-driven program publishes its independent drives".
For programs with no such admission, the existing version-selection rules
remain unchanged: the producer SHALL declare `version: 7` for a program carrying a BLOCK —
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
  edge's ends, direction and expression, including the time-drive mapping
  and its semantics version when present — so a state taken against one
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
  INPUT ids and, for a time-driven program, the independent time-drive IDs
  that reach it through the program — the candidate table a stop's blocked
  group is filtered out of. A drive ID is not an input or bank coordinate.
- `time_drives`: present ONLY for a program using explicit time drives,
  mapping their identities to their edges under "A time-driven program
  publishes its independent drives"; absent in every pre-existing program.
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

## ADDED Requirements

### Requirement: A time-driven program publishes its independent drives

A running program that compiles an explicit time source SHALL publish
document `version: 10` and SHALL carry `program.time_drives`: an ordered
list of objects with `id` and `edge`, identifying each resolved time-source
relation and its zero-based index in `program.edges`. Each `id` SHALL be
`@time:<edge-index>`, separate from the qualified coordinate/input ID
namespace, and entries SHALL be ordered by ascending edge index.
All targets of one resolved relation SHALL share its ID; two separate
resolved relations SHALL have different IDs.

Each listed edge SHALL name the existing clock name `time` in `needs`,
never in `gives`. Expressions SHALL use the existing expression language,
bindings table and published jump plans; the elapsed source SHALL NOT be
hidden inside a pose binding. `program.sources` SHALL propagate drive IDs
alongside input IDs for stop grouping. A listed drive's read of time SHALL
follow the independent admission behavior of the simulation requirement
"Declared time drives retain motion across operating history", even though
all of them begin an advancing tick at the same elapsed seconds.

The published bank, drivers and intermediates SHALL NOT gain clock-drive
coordinates or operator inputs. `program.clock` SHALL remain `time`.
The time-drive mapping and its semantics version SHALL participate in
program identity. Republishing an unchanged model SHALL produce identical
bytes. Publishing a live run SHALL preserve its bank, tick, ownership and
next-tick behavior.

A program with no compiled time drive SHALL omit `time_drives` and retain
its existing minimum document version and byte representation, including a
model that reads `self.time` solely in ordinary pose expressions. A consumer
supporting only earlier document versions SHALL refuse version 10 before
executing it; silently dropping the new semantics is not compatibility.
Browser execution requires a separately implemented matching consumer and
SHALL NOT be claimed on producer-only evidence.

#### Scenario: A time drive is explicit and not a fabricated driver

- **WHEN** a root with one `time.drives(shaft.turn, ratio=6)` is published
- **THEN** the document is version 10, the corresponding edge reads
  `time`, `time_drives` maps its `@time:<edge-index>` ID to that edge,
  and the ID appears in the shaft's source candidates but not in
  `drivers` or `coordinates`

#### Scenario: Independent autonomous trains publish independent stop identities

- **WHEN** two unrelated time-driven shafts are published
- **THEN** they carry distinct time-drive IDs, and each shaft's source
  candidates contain only its own drive ID unless the declared mechanical
  graph connects them

#### Scenario: A retained gate keeps its published plan

- **WHEN** an explicit time-drive law also reads its retained shaft angle
  to gate travel at exhaustion
- **THEN** the version-10 document carries the existing self-read law
  expression and jump plan together with the time-drive mapping;
  no Python-only callback is needed to reproduce the mechanism

#### Scenario: Publishing is deterministic and does not tick a live machine

- **WHEN** an unchanged time-driven model is published twice while its
  live run holds a nonzero retained angle
- **THEN** both documents are byte-identical, the live run has not moved,
  and its next tick agrees with a run that was not published

#### Scenario: A pose clock alone does not require the new version

- **WHEN** a pre-existing running model uses `self.time` only to rotate
  a plain part and is exported before and after the change
- **THEN** its documents are byte-identical and declare the same version,
  with no `time_drives` field

#### Scenario: An older consumer cannot silently display an inert mechanism

- **WHEN** a version-10 time-driven document is passed to a consumer
  advertising support only through version 9
- **THEN** its unsupported-document-version refusal is reached before
  execution, rather than opening a motionless or wrongly stopped machine

### Requirement: The producer corpus pins retained time-drive behavior

The framework SHALL generate committed conformance fixtures through its
real publication and simulation paths for explicit time-driven motion.
Fixtures SHALL include the model document, step size, operation sequence
and expected per-tick clock, bank, crossings, stops including time-drive
provenance, and command outcomes. Snapshot, restore and reset sequences
SHALL be included. Expected results SHALL come from the producer run, not
from a second handwritten algorithm.

Coverage SHALL include no-command motion, enable at nonzero time,
Astrarium-equivalent winding and exhaustion, hard-stop isolation between
time drives, connected downstream motion, mixed commanded and time-driven
sources, and replay. Existing commanded and pose-only corpus documents
SHALL remain unchanged. The independent viewer SHALL consume these same
artifacts in its own repository before cross-runtime parity is claimed;
the framework SHALL record that consumer validation as outstanding when
only the producer has been tested.

#### Scenario: The Astrarium acceptance sequence travels with the document

- **WHEN** the time-drive corpus is generated
- **THEN** it includes the two-cube shaft/weight acceptance operations
  with enabled, wind and retained angle, no artificial drive command,
  expected exhaustion and restart results, and a snapshot replay

#### Scenario: A shared clock does not hide stop coupling

- **WHEN** the independent-trains corpus scenario reaches one train's bound
- **THEN** its expected records identify only that train's time drive as
  stopped while the other train and global elapsed seconds continue

#### Scenario: Producer-only validation is reported honestly

- **WHEN** the framework fixtures pass but no matching viewer replay has run
- **THEN** the implementation report identifies the separate viewer
  dependency and does not report browser or whole-project completion
