## MODIFIED Requirements

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
it publishes. An instruction naming NONE or MORE THAN ONE driver SHALL NOT
appear in any document either, and for the same reason: an instruction under a
clocked root is ONE request, a request names exactly one moving input, and the
machine's compile refuses the others where it refuses a state. Every
instruction a version 8 document carries is therefore one a consumer can
PLAY.

A published instruction MEANS one request over the driver it names —
`targets` a move TO that value and `by` a move BY that travel — stated by the
simulation capability's requirement "Instructions carry design-unit targets"
and executed by the same published machine every other request is executed by.
The document SHALL carry NO field, key or version saying so: a version 8
document published after an instruction has that meaning SHALL be byte for
byte the document the same root published before it had one. `duration` SHALL
remain what it is published as — seconds — and the document SHALL say nothing
about how a consumer spends them: drawing the transition is the consumer's,
and no frame, cadence or clock is stated here.

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
  and the document is byte for byte the one that root published when an
  instruction had no execution meaning

#### Scenario: A stateless tree enters no clocked path when published

- **WHEN** a driven, stateless model is published
- **THEN** no clocked code path is entered at any point

#### Scenario: A clocked document carries no instruction a consumer cannot play

- **WHEN** a clocked root declaring an instruction that names two drivers is
  published through any producer
- **THEN** no document is written, the refusal comes from the machine's
  compile naming the instruction, and every instruction of every document that
  IS written names exactly one driver

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
`instructions`, `bindings` and `clocked` — VERBATIM; a SCRIPT of steps, each a
request naming one input and exactly one of a travel and a target value, a
TRIGGER naming one declared instruction, or a snapshot, a restore or a reset;
and, per step, the whole bank after it, the travel ADMITTED, BOTH ENDS OF THE
PATH, every event fired in path order — each carrying the relations that fired,
the fraction of the requested travel, the input's value there and the targets
with their new values — and every bound met, each carrying the coordinate, the
side, the bound evaluated at the landing, the coordinate's value there, the
input's value and the fraction.

A TRIGGER step SHALL be recorded exactly as the request it makes, in the same
shape a request step is recorded, so that the fixture pins what an instruction
MEANS under a clocked root and not merely that it was accepted. The declared
`duration` SHALL NOT appear in a recorded step: it is published in the
document the fixture already carries verbatim, and the machine does not read
it.

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
reset; an instruction played as a request BY a travel; an instruction played
as a request TO a target; a banked clock; an event located on the clock; a
time request refused for running backwards; a time request no bound clips; a
request refused for exceeding the crossing maximum; a STRICT surface reached
exactly at a request's endpoint and fired by the request that begins on it;
and a request stopped at a bound from a coordinate standing at exactly ZERO.
The framework's suite SHALL test that refusal directly, so the corpus's width
is visible without running the generator.

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
- **THEN** every bank, admitted travel, path end, event and stop matches the
  fixture exactly, floats included

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

#### Scenario: A corpus missing a triggered instruction is refused

- **WHEN** the generator is asked to write a corpus none of whose machines
  plays a declared instruction, or one that plays only the relative form
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A triggered step records the request the instruction made

- **WHEN** a corpus script triggers an instruction declared `by` a travel over
  a machine whose stroke commits on the way
- **THEN** the fixture records that step exactly as it records the same
  request made by hand — the bank, the admitted travel, both ends of the path,
  the events and the stops — and the replay reproduces it
