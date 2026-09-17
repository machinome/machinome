## ADDED Requirements

### Requirement: A clocked root's document publishes its compiled machine

A document serialized from a CLOCKED root — one in whose tree anything
declares a `State` — SHALL declare `version: 8` and SHALL carry a top-level
`clocked` object, beside `drivers`, `states`, `instructions` and `bindings`
and ahead of `root`, holding what COMPILE TIME decided about the machine and
nothing a request computes.

The version SHALL be a property of the ROOT'S DECLARATION and not of the
tree's content, exactly as `version: 5` is: a clocked root with one state, no
flexible leaf and nothing shared is still a machine a lower consumer would
animate wrongly. `version: 8` SHALL dominate every other rung, so a clocked
document carrying a flexible leaf or a non-empty `bindings` table still
declares 8. A root that declares no `State` SHALL NEVER declare `version: 8`,
SHALL NOT carry a `clocked` key, and SHALL publish the document it published
before this rule existed, byte for byte.

The bump SHALL NOT be treated as additive. A clocked tree's pose expressions
read its declared states as FREE NAMES, which a consumer of a lower version
can bind to nothing, so a consumer that cannot read version 8 SHALL REFUSE it
by name rather than render it. A clocked model SHALL NOT be published at a
lower version with its states rendered as their initial values: the geometry
would be right only at the initial state and would then silently stop
following the machine.

The one function every document producer passes through SHALL go on asking,
structurally and without rendering, whether the tree declares a `State`, and
SHALL REFUSE a clocked tree published WITHOUT its compiled machine, naming
the states. That refusal is a PRODUCER error and not a model error: it is
what stops a producer from reaching a lower-version document by a route the
check does not cover, which is why the check is placed there and not on the
symbolic walk that a browser-rendered snapshot bypasses.

Every expression the object carries SHALL be written in the document's
existing expression language and SHALL participate in the SAME ordered
`bindings` table the tree's expressions use, so no subexpression is published
twice and no producer-local sharing syntax appears anywhere in the document.
The object SHALL be ordered deterministically for a given tree, so
republishing an unchanged model produces a byte-identical document.

`clocked` SHALL carry:

- `identity`: a digest over the root class, the bank's ids with their declared
  `dtype` and `scale`, every committing relation's ends, event primitive and
  law, and every compiled constraint's coordinate, side and level — so a bank
  taken against one machine is refused against another, and so a changed range
  changes the identity.
- `clock`: the free name elapsed simulation seconds bind to, under the
  requirement "A clocked document's clock and animation variable", or `null`
  where the root declares no elapsed base.
- `own`: the free name every published bound reads its own coordinate's
  start-of-request value under. It SHALL be a legal name of the document's
  expression language, minted so that it collides with no published id, and a
  consumer SHALL evaluate that bound's `value` over the bank at the request's
  start and hold the result under this name for the whole request.
- `commits`: one entry per committing relation, in the tree's own order,
  defined by the requirement "A published commit says what it reads, writes
  and fires on".
- `bounds`: one entry per COMPILED CONSTRAINT — one side of one bounded
  coordinate's declared range — defined by the requirement "A published bound
  says where a clocked request stops".
- `limits`: the constants the shared locator is defined by, as numbers, so a
  consumer cannot silently differ from the producer: `crossing_tolerance` —
  which a clocked path introduces no NEW use of but does REACH, when a kinked
  event level's crossings are merged and when a jumped constraint level's cuts
  are folded — and `max_crossings`. The object SHALL NOT publish a
  subdivision count, a bisection count or an increment-agreement window: a
  clocked path never searches, never bisects and never compares two
  increments, and publishing them would state a contract this discipline has
  not got.

A version 8 document SHALL carry EVERY declared instruction in its
`instructions` table, in the shape a version 5 document carries them: each
entry carrying exactly one of `targets` (where the drivers land) and `by` (how
far they travel from where they stand), both keyed by qualified driver id and
both in design units, beside `duration` in seconds. A RELATIVE instruction
SHALL NOT be omitted here: the omission below version 5 exists because a
shipped consumer of those versions reads `targets` off every entry, and a
consumer of this version is a new consumer, so omitting one would be a producer
discarding a declaration for a reason that does not apply. An instruction
naming a STATE as a target SHALL NOT appear in any document: the machine's
compile refuses it before a document exists, and every producer compiles before
it publishes. This version SHALL give a published instruction NO execution
meaning — a clocked machine has no command surface — and what a consumer may do
with one is not settled by this capability.

`clocked` SHALL NOT carry a table of the BANK. A clocked bank holds no joint
coordinate — it is every declared driver and every declared state at its
declared default, with the clock at zero where there is one — so every value
in it is already published by the `drivers` and `states` tables and by
`clock`, and repeating a declaration inside `clocked` is forbidden for the
same reason it is forbidden inside `program`. A value set as SESSION SETUP
SHALL NOT be published: a document says where the machine RESTS.

`clocked` and `program` SHALL NEVER appear in one document. A `State` under a
root declaring `Time.running()` is refused where declared defaults are bound,
so the two are mutually exclusive by construction.

Publication SHALL compile the machine through the same construction a
simulation makes, so the published machine is the simulation's by
construction rather than by two implementations agreeing, and SHALL leave the
tree posed exactly as it found it — every node's snapshot restored and the
tree re-rendered — so a producer that arrives holding a posed tree still
holds one afterwards. The clocked compiler SHALL be imported only where that
compile happens, so a model that declares no `State` loads none of it.

#### Scenario: A clocked model publishes version 8

- **WHEN** a root whose tree declares `units = State(default=0)` is serialized
- **THEN** the document declares `version: 8`, carries a `clocked` object with
  `identity`, `clock`, `own`, `commits`, `bounds` and `limits`, and the pose
  expressions of the parts its states move read those states by qualified id

#### Scenario: A stateless model publishes unchanged

- **WHEN** a model that declares no `State` is serialized before and after
  this capability exists
- **THEN** the two documents are identical byte for byte, and the later one
  carries no `clocked` key and no `states` key

#### Scenario: The version dominates the content ladder

- **WHEN** a clocked root carrying a flexible leaf and a repeated
  subexpression is serialized
- **THEN** the document declares `version: 8`, carries `bindings` and a
  `flexible` node, and the same tree with its `State` removed declares the
  version its content alone gives it

#### Scenario: Every document producer publishes a clocked model

- **WHEN** a clocked model is published through a build, through an export and
  through the development server's publish
- **THEN** each writes a version 8 document carrying the same `clocked`
  object, and each logs that the installed viewer cannot read it while writing
  it anyway

#### Scenario: A producer that publishes a clocked model without compiling it is refused

- **WHEN** a document body is assembled for a clocked tree with no compiled
  machine supplied
- **THEN** it is refused naming the states, and no document is written

#### Scenario: Republishing an unchanged clocked model changes nothing

- **WHEN** an unchanged clocked model is published twice
- **THEN** the two documents are byte-identical, the `clocked` object's
  ordering and its minted names included

#### Scenario: Publication leaves the tree as it found it

- **WHEN** a clocked model posed at chosen driver values has its document
  serialized in the same process
- **THEN** the document is produced and every node holds the snapshot and the
  rendered operations it held before

#### Scenario: A clocked model is still built, tested and photographed

- **WHEN** a clocked model is rendered, assembled, has its STLs built, is run
  under the test runner, and is photographed with the OpenSCAD renderer
- **THEN** each succeeds, and the OpenSCAD image shows the INITIAL BANK —
  every state at its declared default, with `--drive` posing declared drivers
  and a state named there refused by name

#### Scenario: A clocked document publishes both instruction forms

- **WHEN** a clocked root declares an absolute instruction and a relative one,
  each naming a declared driver
- **THEN** the version 8 document's `instructions` table carries both, the
  first with `targets` and no `by` and the second with `by` and no `targets`,
  and the document gives neither any execution meaning

#### Scenario: A stateless tree enters no clocked path when published

- **WHEN** a driven, stateless model is published
- **THEN** no clocked code path is entered at any point

### Requirement: A clocked document publishes its states beside its drivers

A version 8 document SHALL carry a top-level `states` table beside `drivers`,
keyed by each declared state's qualified id and ordered by it, each entry
carrying `default`, `range`, `unit`, `dtype` and `scale` under exactly the
rules the `drivers` table follows: `default` in NATIVE units, `range` in
DESIGN units and never a clamp, `dtype` published by name because a document
is JSON, and `scale` and `unit` verbatim.

The two tables SHALL name DISJOINT sets of ids, and the split SHALL be the
HANDLE rule: every key of `drivers` is an input a person may move, and no key
of `states` ever is — a state is written by the machine at an event, and a
consumer that offered one as a handle would be offering what the framework
refuses. A version 8 consumer SHALL therefore drive the machine only from
`drivers` and from the clock.

Every free name a version 8 document's pose expressions read SHALL be a key
of `drivers`, a key of `states`, the published clock, or a name of the
document's own `bindings` table.

A document that declares no state SHALL NOT carry the key at all, so every
existing document is unchanged.

#### Scenario: States publish their declarations

- **WHEN** a clocked root holding two children of one class declaring
  `digit = State(default=0, range=(0, 9), dtype=int)` is published
- **THEN** the `states` table holds exactly `a.digit` and `b.digit`, each
  carrying that default, that range in design units, and `dtype: "int"`

#### Scenario: A state is not a handle

- **WHEN** a version 8 document is published
- **THEN** no key of `states` is a key of `drivers`, no `instructions` entry
  targets a key of `states`, and the document carries no `controls` key

#### Scenario: Every pose expression resolves

- **WHEN** a clocked root's dials are posed from its states and its drivers
- **THEN** every free name in every operation of the tree is a key of
  `drivers`, a key of `states`, the published clock or a `bindings` name

### Requirement: A published commit says what it reads, writes and fires on

Each `clocked.commits` entry SHALL carry `sources` and `targets` as lists of
qualified ids IN WRITTEN ORDER, `description` — the relation AS WRITTEN — and
`stated_by`, the class that stated it, so a consumer's refusal names what a
reader can find in the model. Every id in `sources` SHALL be a key of
`drivers`, a key of `states` or the published clock; every id in `targets`
SHALL be a key of `states`.

`at` SHALL carry `primitive` — `floor`, `ceil`, `sign`, or one of the six
comparisons — and `level`, the expression of the LEVEL QUANTITY whose surfaces
that primitive crosses. The level SHALL carry no jump node inside it, one
event being ONE surface family. A remainder SHALL NOT appear as an event
primitive, nor anywhere within a level: a remainder IS a jump, and a level
carries none. The SURFACES of a primitive and the BRANCH it reads on a piece are
the ones the published jump vocabulary already defines and SHALL NOT be
published again.

`law` SHALL be a list of expressions ALIGNED WITH `targets`: the project's law
applied once to a symbolic token per source, which is exactly what the
framework inspects it as. A law returning a plain number SHALL publish a
numeric literal and never a null — a commit's law IS the value written, so a
constant is an answer and not an absence. A consumer SHALL evaluate those
expressions at the moving input's landing and at the PRE-EVENT value of every
state.

A published law SHALL say what the framework's executor COMPUTES, which is not
always what the author's text spells. The executor calls the project's own
callable with numbers, and that callable's REMAINDER takes the sign of the
DIVISOR, while the document's `%` primitive is the truncated remainder — the
sign of the DIVIDEND — that both runtimes already evaluate identically. A
published law SHALL therefore carry a remainder in the floored form, composed
from the document's own `%` and its arithmetic, so that the published graph and
the callable give the SAME double for every pair of operands, the SIGN of a
zero result excepted, which compares equal as a number in either runtime. The
document's `%` SHALL keep its existing meaning everywhere else — a published
CHAIN, BOUND and constraint LEVEL included — because the framework evaluates
THOSE through the graph, and a published graph must say what was evaluated.

A target declaring `dtype: "int"` SHALL be rounded ONCE, at the commit, to the
nearest whole NATIVE unit, and a value exactly halfway between two of them
SHALL take the EVEN one. NO conversion by `scale` SHALL be applied at a commit:
a commit law speaks native units already. The consumer SHALL read the
declaration from the `states` table and no key SHALL be added for it. The rule
is stated rather than left to a consumer because the runtimes' own rounding
functions disagree — one takes a half toward positive infinity, another away
from zero — on a value a counting machine lands on constantly.

A commit whose law cannot be evaluated — a remainder by zero being the case the
framework raises on — SHALL refuse the WHOLE request and commit nothing, which
is the atomicity a clocked request already has. A document cannot express a
raise, so a consumer that computes a NON-FINITE value for a commit SHALL refuse
the request rather than bank it.

`shapes` SHALL carry one entry per input that can MOVE this relation's event
level, keyed by that input's id, whose value is the level's structural shape
in that input — `"affine"`, solved by one division, or `"kinked"`, cut at its
own breakpoints and each piece solved the same way. An input ABSENT from
`shapes` cannot move the level, and a consumer SHALL NOT examine the relation
for it. A CURVED level is refused at simulation construction and SHALL
therefore never appear. The kink BREAKPOINTS SHALL NOT be published: they are
the continuous selections in the published expression, which a consumer
re-derives.

#### Scenario: A commit publishes its event and its law

- **WHEN** a clocked root states
  `(crank & units & tens).commits((units, tens), at=floor(crank / 360), law=advance)`
- **THEN** its `commits` entry names `crank`, `units`, `tens` as sources in
  that order, `units` and `tens` as targets, `at.primitive` is `"floor"`,
  `at.level` is the crank id divided by 360, and `law` holds two expressions
  whose free names are drawn from the sources

#### Scenario: An event level that reads the state it commits publishes it

- **WHEN** a clearing relation states
  `at = ring >= START + PITCH * (10 - digit)` over the digit it writes
- **THEN** `at.primitive` is `">="`, `at.level` is the difference whose zero
  is that surface, and the digit's id appears in it as an ordinary free name
  with no marking of any kind

#### Scenario: A relation an input cannot move is not listed for it

- **WHEN** a clocked root has one relation on a crank level and one on a ring
  level
- **THEN** the first entry's `shapes` names the crank and not the ring, and
  the second names the ring and not the crank

#### Scenario: A law taking a remainder of a negative publishes what the executor computes

- **WHEN** a commit law states a remainder over a quantity a request drives
  NEGATIVE
- **THEN** the value the framework banks is the remainder carrying the
  divisor's sign, the published law evaluated under the document's own
  expression semantics gives that same double, and no bare `%` stands where
  the two would differ

#### Scenario: An integer state landing on an exact half takes the even unit

- **WHEN** a commit law lands a `dtype: "int"` state exactly halfway between
  two whole native units
- **THEN** the banked value is the EVEN one, and that is the value the
  conformance corpus records for a second runtime to reproduce

#### Scenario: A kinked event level says so

- **WHEN** a committing relation's `at` is `floor(max(crank, 0) / 360)`
- **THEN** its `shapes` entry for the crank reads `"kinked"`, and the
  continuous selection stands in the published level for a consumer to cut at

### Requirement: A published bound says where a clocked request stops

Each `clocked.bounds` entry SHALL be ONE COMPILED CONSTRAINT — one side of one
bounded coordinate's declared range — and SHALL carry `coordinate` (the joint
coordinate's qualified id), `side` (`"low"` or `"high"`), `unit`, `node` and
`joint` naming what a stop report must name, and `description`.

`value` SHALL be the CHAIN: one expression over the bank's ids giving that
coordinate's value, composed by substitution from the relations that determine
it, down to declared drivers and declared states, which stay free names. An
intermediate port SHALL be composed THROUGH and never appear. Every free name
of `value` SHALL be a key of `drivers` or of `states`.

`bound` SHALL be the declared bound compiled to an expression, reading the
coordinate's own start-of-request value under the document's published `own`
name and every coordinate it declares itself to read through that
coordinate's own chain. A numeric bound SHALL publish a number.

The LEVEL SHALL NOT be published: it is `value − bound` on the high side and
`bound − value` on the low side, `side` says which, and publishing it as well
would publish the bound twice. A consumer SHALL take the threshold
`max(0, level)` at the request's start, SHALL admit the largest fraction of
the travel at which no constraint's level exceeds its own threshold, SHALL
land on the LAST REPRESENTABLE value of the input that satisfies it — deciding
membership by EVALUATING the level there and never by comparing a float to a
bound — and SHALL judge every constraint again over the bank the request ends
at, refusing the whole request where one is violated.

`plan` SHALL be the level's JUMP PLAN where the level carries a discontinuous
primitive and `null` otherwise, in exactly the shape a published program's
jump plan has: `skeleton`, the whole level with every jump node replaced by a
branch placeholder, and `jumps`, the jump nodes in the expression's postorder,
each with `name`, `primitive` and `level`. Placeholders SHALL be minted at
publication and be unique across the WHOLE document, under the same rule the
program's are, because a placeholder repeated across two plans would let two
different jump nodes share one published subexpression.

`shapes` SHALL carry one entry per input that can move the level, keyed by
that input's id, carrying the SKELETON's structural shape and one shape per
published jump, aligned with `plan.jumps`. An input absent cannot move the
level and SHALL NOT be examined for it. A CURVED level is refused at
simulation construction and SHALL never appear.

A declared range that NOTHING binds SHALL still be published, its `value` a
constant and its `shapes` empty: a decorative range on a part that rests is a
range the machine really declares, and a consumer examining it finds it moves
with nothing.

A clocked document SHALL NOT publish a `spans` table: a clocked simulation
banks no joint coordinate, so there is no banked coordinate for a span to be
keyed by, and a bounded coordinate is reached only through its chain.

#### Scenario: A numeric range publishes its chain

- **WHEN** a clocked root declares `range=(0, 9)` on a lift a driver reaches
  through one relation
- **THEN** two entries appear, `low` and `high`, each with the same `value`
  chain over that driver's id, `bound` a number, `plan` null, and `shapes`
  naming that driver

#### Scenario: A ratchet publishes a bound reading its own coordinate

- **WHEN** a clocked root declares
  `range=(lambda turn: PITCH * floor(turn / PITCH), None)` on a crank's joint
- **THEN** one `low` entry appears whose `bound` reads the document's `own`
  name, whose `plan` carries the `floor` node with its level, and whose
  `shapes` entry for the crank carries a shape for the skeleton and one for
  that jump

#### Scenario: A freeze publishes both sides reading the own coordinate

- **WHEN** a clocked root states both bounds of a selector's joint over that
  coordinate's own value and a comparison on the crank's phase
- **THEN** both entries publish, each reading the `own` name and the crank's
  id, and the crank's `shapes` entry names the comparison's jump

#### Scenario: A chain through a port carries no port

- **WHEN** a selector is wired `setting.drives(knob.travel, ratio=6)` through
  a plain `Port` and the knob's joint declares a range
- **THEN** the entry's `value` is an expression over the selector's driver id
  alone, the port's id appears nowhere in the document's `clocked` object, and
  no `intermediates` list is published

#### Scenario: A decorative range publishes as a constant

- **WHEN** a clocked root declares a range on a part no relation, wiring,
  formula or author code binds
- **THEN** its entries publish with a constant `value` and an empty `shapes`

### Requirement: A clocked document's clock and animation variable

Under a clocked root declaring `time = Time.elapsed()` the producer SHALL bind
`time` symbolically for the serialization, so a version 8 document carries the
free name `time` — and NOT the animation variable — wherever the model reads
the clock, and SHALL publish that name as `clocked.clock`. A consumer running
the machine SHALL bind it to ELAPSED SIMULATION SECONDS, which never wrap and
never run backwards; a consumer with no run SHALL bind it to ZERO, the instant
the rest pose is defined at.

Under a clocked root that declares NO time base, `clocked.clock` SHALL be
`null` and nothing about the animation variable SHALL change: such a root has
no clock, a pose leaves an unbound `time` the untimed symbolic animation
variable exactly as it does today, and a geometry that is a formula of time
SHALL go on animating on the document's own `animation` timeline while the
bank stands. A consumer previewing such a document without driving it SHALL
show the INITIAL BANK — every driver and every state at its declared default —
posed, with the animation variable sweeping.

The `animation` object of a version 8 document SHALL carry `fps` and `frames`
as it always has and SHALL omit `loop`, neither of the bases a clocked root
may declare having one.

Every reading of an unbound `time` outside the document producer SHALL be
unchanged, so the OpenSCAD path, a bare render and a numeric pose are
untouched.

#### Scenario: An elapsed clocked document carries the clock by name

- **WHEN** a clocked root declaring `Time.elapsed()` whose part is posed from
  `self.time` is published
- **THEN** the operation reads the free name `time`, `clocked.clock` is
  `"time"`, and no expression anywhere in the document reads the animation
  variable

#### Scenario: A clocked root with no base keeps the animation variable

- **WHEN** a clocked root that declares no time base and whose part is posed
  from `self.time` is published
- **THEN** `clocked.clock` is `null`, the operation reads the animation
  variable exactly as it does for a root declaring no base at all, and the
  `animation` object carries `fps` and `frames` and no `loop`

#### Scenario: The Python preview is unchanged

- **WHEN** a clocked root's `time` is read outside a simulation and outside
  the document producer
- **THEN** it reads exactly what it read before this change

### Requirement: The two runtimes share a clocked conformance corpus

The framework SHALL provide a generator that writes a JSON conformance fixture
from its own CLOCKED executor, covering a set of small clocked roots, and the
framework's own suite SHALL replay that committed fixture and reproduce it.
The fixture is the contract between the framework's clocked executor and any
other runtime executing a version 8 document: every expected value in it SHALL
be a value the framework's executor PRODUCED, never a value recomputed a
second way, so a disagreement means the other runtime drifted.

The fixture SHALL carry, per machine: its name; the published document's
machine-bearing keys — `format`, `version`, `drivers`, `states`,
`instructions`, `bindings` and `clocked` — VERBATIM; a SCRIPT of steps, each
a request naming one input and exactly one of a travel and a target value, or
a snapshot, a restore or a reset; and, per step, the whole bank after it, the
travel ADMITTED, every event fired in path order — each carrying the relations
that fired, the fraction of the requested travel, the input's value there and
the targets with their new values — and every bound met, each carrying the
coordinate, the side, the bound evaluated at the landing, the coordinate's
value there, the input's value and the fraction.

A step the executor REFUSED SHALL be recorded as the refusal's KIND and the
qualified names its message must name, together with the bank AFTER it, which
SHALL be the bank before it: a refused request commits nothing. The message
TEXT SHALL NOT be pinned — prose is edited for clarity, and a fixture that
pinned it would make every such edit a regeneration — while the kind and the
names are the contract a second runtime must reproduce.

**Agreement SHALL be EXACT, bit for bit, for every value including floats**,
and the fixture SHALL state that as a field of its own rather than leave it to
a reader's convention. A clocked executor has no window inside which it
declines to distinguish two values: there is no step, every event is solved by
division, and two relations are ONE event exactly when their landings are the
SAME floating-point value — so a consumer agreeing only within a tolerance
would merge events this framework keeps apart and split events it joins, which
is precisely what the discipline exists to be right about.

The claim SHALL rest on operations that are exact or identically rounded in
both runtimes, and the fixture SHALL exercise no others: IEEE addition,
subtraction, multiplication, division and square root; the truncated
remainder, which is exact; the floored remainder composed from it, whose
correction is one addition; floor, ceiling, absolute value, sign, minimum,
maximum and the comparisons, which select rather than round; and the LANDING
WALK, which is a bisection in the ORDINAL space of a double's own bits and
which a second runtime SHALL reproduce as a bit walk rather than by stepping a
small quantity. A TRANSCENDENTAL function and a POWER are OUTSIDE the claim —
neither is correctly rounded, and two runtimes' libraries need not agree in the
last bit — so the generator SHALL REFUSE a machine carrying one in a published
commit law, event level, constraint level or chain. That is a stated
limitation, not a hidden assumption: a machine that needed one would need a
tolerance declared for ITSELF, beside the file's own, rather than a window the
whole fixture relaxes into.

The generator SHALL REFUSE to write a corpus that does not exercise each of:
the four event primitives (`floor`, `ceil`, `sign` and a comparison); a commit
law taking a remainder of a NEGATIVE operand; a multi-source commit law; a
commit writing several targets; an integer state rounded once; an integer state
whose law lands exactly halfway between two whole native units; a scaled state;
a rising step that fires; a falling step that fires nothing; a kinked event
level cut at its breakpoints; two relations landing on ONE float; two surfaces
one representable value apart taken as two events; two relations writing one
state at one landing refusing the request; an event level that reads the state
it commits; one state written by two relations on two inputs; a request
clipped at a numeric bound; a request clipped at a bound stated as an
expression; a bound reading ANOTHER coordinate; a bound reading its OWN
coordinate; a bound pair both of whose sides read the own coordinate; a
constraint level partitioned at its own jump surfaces; a kinked constraint
level; a request admitted at ZERO travel; a declared range nothing binds; a
bank standing outside a bound and moving back inside it; an end-of-request
judgement refusing a request whose own commit carried a coordinate out of
range; a chain composed through an intermediate port; a snapshot; a restore; a
reset; a banked clock; an event located on the clock; a time request refused
for running backwards; a time request no bound clips; a request refused
for exceeding the crossing maximum; a STRICT surface reached exactly at a
request's endpoint and fired by the request that begins on it; and a request
stopped at a bound from a coordinate standing at exactly ZERO. The framework's
suite SHALL test that refusal directly, so the corpus's width is visible
without running the generator.

A framework test SHALL assert that each fixture machine's REAL published
document reproduces the fixture's own copy, so the fixture cannot drift from
the producer it claims to come from.

The corpus SHALL include one machine carrying, together, several banked wheels
of ONE class, a state written at two different events by two relations on two
inputs, an event level that reads the state it commits, a bound reading its
own coordinate, a bound pair that freezes a coordinate while another input is
off its rest, and a chain composed through an intermediate port — because the
cases a second runtime gets wrong are the interactions, and a corpus of
machines that each carry one feature exercises none of them.

#### Scenario: The framework reproduces its own corpus

- **WHEN** the committed fixture is replayed through the framework's clocked
  executor, machine by machine, applying each script step in order
- **THEN** every bank, admitted travel, event and stop matches the fixture
  exactly, floats included

#### Scenario: The corpus carries the document it was run against

- **WHEN** a fixture machine's document is published afresh
- **THEN** its `clocked`, `drivers`, `states`, `instructions` and `bindings`
  equal the fixture's copy

#### Scenario: A corpus missing an event primitive is refused

- **WHEN** the generator is asked to write a corpus whose machines state no
  `sign` event
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing a tie is refused

- **WHEN** the generator is asked to write a corpus in which no two relations
  land on one floating-point value
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing a clip is refused

- **WHEN** the generator is asked to write a corpus none of whose requests is
  clipped at a declared bound, or none of which is admitted at zero travel
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing a strict surface reached exactly is refused

- **WHEN** the generator is asked to write a corpus none of whose requests
  ends exactly on a STRICT comparison's surface
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing a stop from a coordinate at zero is refused

- **WHEN** the generator is asked to write a corpus none of whose requests is
  stopped at a bound with the moving input standing at exactly `0.0`
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A machine whose machinery is not exactly reproducible is refused

- **WHEN** the generator is asked to include a machine whose commit law or
  whose event level calls a trigonometric function
- **THEN** it refuses naming the operation the exactness claim does not cover,
  and writes nothing

#### Scenario: A refused request is recorded as its kind and its names

- **WHEN** a corpus step asks a clocked machine for a request its own commit
  carries out of range
- **THEN** the fixture records the refusal's kind and the coordinate and side
  its message names, and the bank after the step equals the bank before it

## REMOVED Requirements

### Requirement: A clocked model is refused publication

**Reason**: The requirement stated an owned GAP, not a durable behaviour: the
document version that carries declared states did not exist, so every producer
refused a clocked model by name rather than publish one a consumer would
animate wrongly. This change defines that version, so the refusal it demanded
is gone.

**Migration**: A clocked model now publishes `version: 8` under the
requirement "A clocked root's document publishes its compiled machine". Of the
old requirement, three parts survive and are restated there rather than
dropped: the structural check stays in the one function every producer passes
through, now refusing a clocked tree published WITHOUT its compiled machine;
a clocked model is still never published at a lower version with its states
rendered as their initial values; and everything that writes no document —
rendering, assembling, STL building, the test runner and an OpenSCAD snapshot
— is still untouched. A consumer that cannot read version 8 refuses it by
name, which is the protection the refusal stood in for.
