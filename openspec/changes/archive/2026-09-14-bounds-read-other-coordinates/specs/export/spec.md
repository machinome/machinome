## MODIFIED Requirements

### Requirement: A running root's document publishes the compiled program

A document declaring `version: 5` SHALL carry a top-level `program` object,
beside `drivers`, `instructions` and `bindings` and ahead of `root`, holding
what COMPILE TIME decided about the machine and nothing the tick computes.
Every expression it carries SHALL be written in the document's existing
expression language and SHALL participate in the same ordered `bindings`
table the tree's expressions use, so no subexpression is published twice and
no producer-local sharing syntax appears anywhere in the document. The
object SHALL be ordered deterministically for a given tree, so republishing
an unchanged model produces a byte-identical document.

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
  never stores.
- `edges`: one entry per compiled edge, IN PROGRAM ORDER, defined by the
  requirement "The published edges say what each one reads, gives and
  computes".
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

- **WHEN** a running root drives a plain readout port from a joint
  coordinate
- **THEN** that port's qualified id is in `program.intermediates`, is not in
  `program.coordinates`, and the edge that computes it names it in `gives`

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

- **WHEN** a running root's relation reaches a value on a node whose
  instance path is not computable
- **THEN** publication fails naming that node and saying a fallback class
  name is not unique, and no document is written

#### Scenario: A driver named like the clock is refused

- **WHEN** a running root declares a driver whose qualified id is `time`
- **THEN** the simulation refuses at construction, naming the id and that
  `time` is reserved for the clock

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
of its two forms, and a tick carrying both a crossing and a stop. The framework's suite SHALL test
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
