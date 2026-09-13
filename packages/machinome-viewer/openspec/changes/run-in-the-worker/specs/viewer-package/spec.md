## ADDED Requirements

### Requirement: The viewer executes a document's published program

A document may carry a compiled mechanical program: the bank of
coordinates in the order the program propagates them, with the value the
rest pose gave each one; the values the program computes and never stores;
the edges in propagation order with their expressions, their affinity and
their jump plans; the declared bounds; the inputs that reach each value;
the constants the algorithm is defined by; and the free name elapsed
simulation seconds bind to. The viewer SHALL execute that program: on
every step it admits the movement the active commands ask for, propagates
it over the edges, and commits one bank — the machine running, rather than
a pose evaluated.

The run SHALL be executed off the rendering thread. Rendering SHALL NOT
advance it: a dropped display frame SHALL drop display and never a step,
and the mechanism SHALL never be advanced by more steps than elapsed time
has earned. A page that is not being displayed SHALL accumulate no
unseen steps and SHALL resume from where it stands. A host environment
that cannot run the engine off the rendering thread SHALL run the same
engine on it and SHALL say so on the handle, rather than failing to open
the machine.

The step size SHALL be the viewer's own choice — the document publishes
none — SHALL default to a value fine enough to resolve the mechanisms the
producer publishes, and SHALL be settable once when the viewer is mounted.
It SHALL NOT change afterwards, because a run state is only valid at the
step size it was taken at. A non-finite or non-positive step size SHALL
be refused naming the value.

Playback speed SHALL keep its existing meaning — a multiple of real time —
and SHALL change how many steps are taken per second of wall time, never
the step size, so that watching a machine faster does not simulate it more
coarsely.

A run SHALL NOT begin advancing merely because a document was mounted: it
SHALL be created at the program's published rest values, stopped, and
SHALL begin when a host or a control asks it to — so a page that is only
being looked at, a still capture or a thumbnail, shows the rest state
without knowing that a run exists. A host MAY ask at mount time for a run
that begins at once.

The handle SHALL expose the run for a document that carries a program and
SHALL report its absence for one that does not. A host SHALL be able to
read the identity of the program, the step size, the step count, the
elapsed simulation seconds, the committed bank and each coordinate's kind,
unit and domain; to start, pause and advance an exact number of steps; to
request a movement of a declared input by a travel or to a value over a
duration, a continuous rate, a declared instruction, and the cancellation
of any of them; to take, restore and reset a run state; and to be told of
every committed step and every command outcome.

#### Scenario: A machine runs where a pose could not

- **WHEN** a host mounts a document carrying a program, asks for a
  declared instruction that advances an input by one unit, and lets the
  run advance until the command retires, ten times over
- **THEN** the coordinate the program's law drives stands where ten
  separate movements left it, not where one would have

#### Scenario: Display and mechanics are separate

- **WHEN** rendering falls behind while a command is running
- **THEN** no step is skipped, the committed bank a later frame draws is
  the one the run reached, and the elapsed simulation time reports the
  steps actually taken

#### Scenario: A page nobody is watching holds still

- **WHEN** the page carrying a running document stops being displayed and
  is displayed again later
- **THEN** the machine stands where it stood, no steps were taken while it
  was hidden, and the elapsed simulation time did not advance

#### Scenario: The step size is fixed for the life of a mount

- **WHEN** a host mounts with a chosen step size
- **THEN** the run uses it, the handle reports it, and there is no
  operation that changes it on a live run

#### Scenario: Watching faster is not simulating coarser

- **WHEN** the same document is run at real time and at a large multiple
  of it, each for the same number of steps
- **THEN** both reach the same bank, step for step

#### Scenario: A document only being looked at shows its rest state

- **WHEN** a document carrying a program is mounted by a host that asks
  for nothing
- **THEN** no step is taken, the elapsed simulation time stays at zero,
  and the model stands at the published rest values until something asks
  the run to begin

#### Scenario: A document with no program has no run

- **WHEN** a host asks a mounted document with no published program for
  its run
- **THEN** it is told there is none, and every other handle operation
  behaves exactly as it does today

### Requirement: The step reproduces the producer's own integration

For each step the viewer SHALL take the movement each active command
admits for that step — a pure function of the number of steps since the
command started, so a replayed run admits exactly the same travel — and
propagate it over the edges in the published order, producing one
increment per determined value and committing them together.

- A **continuous law** SHALL contribute the difference of its expression
  evaluated at the end of the step's path and at its start.
- A **law that jumps** SHALL contribute the continuous part only: its
  path SHALL be cut at every crossing of every jump surface it meets,
  taking the jump nodes in the published order so that an inner node has
  already cut the path before an outer one is asked; on each piece every
  jump node SHALL hold one branch, read by evaluating its published level
  quantity at that piece's midpoint; and the contribution SHALL be the sum
  of the branch-substituted law's change over the pieces. A jump SHALL
  therefore never move a part. A level quantity the producer published as
  affine in its sources SHALL have every surface between a piece's two
  endpoint values solved rather than searched; any other SHALL be sampled,
  bracketed and bisected under the published subdivision, rounding and
  tolerance limits.
- A **wiring** SHALL contribute its source's increment times its published
  factor; a **derived coordinate** SHALL contribute its published linear
  combination, forward or solved backward into its one term, with the
  constant replaced by zero for an increment; and a **check** SHALL
  determine nothing and instead predict what its coordinate should have
  received.
- A value no edge determines SHALL hold.
- Two increments that disagree on one value beyond the published agreement
  window, and a check whose prediction disagrees with what its coordinate
  received, SHALL be a conflict.

A step that would take a banked coordinate outside a declared bound, and
further outside than it stood at the start of the stretch, SHALL treat
that bound as a physical stop: the fraction of the stretch at which the
coordinate reaches it SHALL be located, the earliest one taken first and
everything within the crossing tolerance of it treated as one event; the
stretch SHALL be re-integrated up to that fraction only; the coordinate
SHALL be committed exactly at its bound; every input whose own movement
pushes it SHALL be stopped for the remainder of the step; and what remains
of the step SHALL be examined again. An input that reaches a stopped
coordinate only through a law that is disengaged at that moment SHALL NOT
be stopped. Each declared bound SHALL be evaluated once per step from the
committed bank, so every segment of one step is measured against the same
number.

A step SHALL be atomic across its segments: the bank, the commands'
admitted travel and the records SHALL be applied only once every segment
has succeeded. A conflict, a partition exceeding the published crossing
limit, a law that cannot be integrated over the step's path, or a stop
that stops no moving input SHALL commit nothing — the bank, the step count
and the pose stand — SHALL retire the commands that moved an input in that
step reporting that the step did not happen, and SHALL report what
disagreed, naming the relation as its author wrote it and the class that
stated it.

A command SHALL retire reporting completed, blocked, refused or cancelled,
with the travel it actually admitted in the units the request was stated
in. A command whose input was stopped SHALL retire **blocked** with the
travel it made, and nothing SHALL remember the travel it did not make.
One input SHALL have one owner at a time.

The viewer SHALL keep a bounded record of the most recent steps, of the
jump surfaces crossed inside them and of the stops located inside them,
each entry naming what a reader of the model can find: the relation, the
coordinate, the primitive and the surface level for a crossing; the
coordinate, the side, the evaluated bound, the fraction of the step and
the inputs blocked for a stop.

#### Scenario: A kink costs nothing and a jump moves nothing

- **WHEN** a step moves a source across a kink of a continuous law and, in
  another law, across a jump surface
- **THEN** the continuous law's coordinate moves by the difference of the
  two evaluations, and the jumping law's coordinate moves by its
  continuous part alone, with the jump's own step subtracted

#### Scenario: Several surfaces in one step are all counted

- **WHEN** one step carries a source across three surfaces of one affine
  level quantity
- **THEN** the path is cut three times and the law's contribution is the
  sum over the four pieces

#### Scenario: A stop blocks the group that pushes it

- **WHEN** a coordinate reaches a declared bound part-way through a step
  while an unrelated input is running
- **THEN** the coordinate is committed at its bound, the command on every
  input whose movement pushes it retires blocked with the travel admitted
  before the stop, and the unrelated input completes its whole step

#### Scenario: A disengaged coupling is not stopped

- **WHEN** a stopped coordinate is reachable from an input only through a
  law whose slope is zero at that instant
- **THEN** that input is not stopped and its command continues

#### Scenario: Two increments that disagree commit nothing

- **WHEN** two routes give one coordinate increments differing by more
  than the published agreement window
- **THEN** the step commits nothing, the bank and step count stand, the
  commands that moved are retired as refused, and the report names both
  relations and the coordinate

#### Scenario: A run state restores only into the machine it came from

- **WHEN** a host restores a run state whose program identity or step size
  differs from the running one
- **THEN** the restore is refused naming both, before any live state
  changes

### Requirement: A program the viewer cannot execute is refused by name

A document whose published program the viewer cannot execute SHALL be
refused when the document is loaded — beside the refusals for an
unreadable document version, an unknown flexible technology, an
unresolvable bindings table and an undeclared name — naming what is wrong
and quoting the document. Nothing SHALL be rendered from it and no step
SHALL ever be taken on it.

The refusal SHALL cover at least: a document declaring the running version
with no program object or missing one of its published parts; a coordinate
entry whose kind is unknown or whose rest value is not a finite number;
a set of input coordinates that disagrees with the document's own drivers
table in either direction; an edge whose kind is unknown, or whose
per-output lists are not aligned with its outputs; an edge naming a value
that is neither a bank coordinate nor a published computed value; a jump
whose primitive is outside the published set; a branch placeholder two
plans share; an expression, skeleton, level quantity or bound whose free
names are not among the ones that edge or bound may read; a declared bound
over a coordinate the bank does not hold; a limit that is missing or not a
finite number; a computed value the document reads that no edge
determines; a clock name that is also a coordinate or a driver id; and an
identifier set that cannot be resolved as names, such as one identifier
being a strict prefix of another.

#### Scenario: A primitive the engine does not know

- **WHEN** a loaded program carries a jump whose primitive is not one the
  viewer can read a branch from
- **THEN** loading fails naming that primitive and the ones it knows, and
  no frame is rendered

#### Scenario: Two plans sharing one placeholder

- **WHEN** two jump plans of one document name their jump nodes with the
  same placeholder
- **THEN** loading fails naming the placeholder, rather than letting two
  different jump nodes share one published subexpression

#### Scenario: The two declarations of an input disagree

- **WHEN** a program declares an input coordinate the document's drivers
  table does not, or the table declares a driver the program does not
- **THEN** loading fails naming the difference

#### Scenario: A pose that reads a value nothing computes

- **WHEN** a document's pose expression reads a published computed value
  that no edge determines
- **THEN** loading fails naming that value, rather than posing the model
  from a number that was never produced

### Requirement: A committed bank poses the geometry

For a document carrying a program, the viewer SHALL pose the model from
the bank the run last committed, by evaluating the document's own
expressions with the bank's coordinate identifiers available as names
beside the driver identifiers, through the same evaluation the viewer
performs for any other document. No second pose path and no second table
of poses SHALL exist, and a flexible part's shape parameters SHALL follow
the bank by the same rule as a rigid part's placement.

The program's published clock name SHALL resolve to the elapsed
simulation seconds, which never wrap; with no run — a still capture, a
thumbnail — it SHALL resolve to zero, the instant the rest pose is defined
at. Before the first step, the model SHALL be posed at the rest values the
program publishes.

Only the parts whose expressions read a coordinate that moved SHALL be
re-evaluated, which is the bound the viewer already holds for a driver.

A qualified identifier SHALL resolve at every one of its segments, so an
identifier naming an instance path of any depth resolves to the value
published under it.

#### Scenario: A wheel follows its coordinate

- **WHEN** a run commits a bank in which one joint coordinate moved
- **THEN** the part whose placement names that coordinate is re-posed,
  parts naming only other coordinates keep the matrices they have, and a
  flexible part whose parameter reads it changes shape

#### Scenario: A document opens at its rest pose

- **WHEN** a document carrying a program is mounted and no step has been
  taken
- **THEN** every part stands where the published rest values put it

#### Scenario: A three-segment identifier resolves

- **WHEN** an expression names an identifier of three or more segments,
  such as a joint coordinate on a nested assembly
- **THEN** it resolves to that value rather than to nothing, and the pose
  is a number

### Requirement: The two runtimes agree on a conformance corpus

The widget suite SHALL replay the producer's committed running corpus
through the shipped run engine and SHALL agree with it on every step of
every scenario. The corpus's expected values are the producer's own; a
disagreement means this viewer drifted, and SHALL be fixed here rather
than admitted by widening a tolerance.

For each scenario the suite SHALL build the engine from the corpus's own
copy of the published document — the program, the drivers, the
instructions and the bindings table — at the corpus's step size, apply
each scripted command before the step it names in the order the corpus
lists them, and compare every step: the committed bank, the crossings and
the stops located in that step, and every command created so far with its
status and the travel it has admitted.

Agreement SHALL be EXACT for discrete state — step numbers, command
statuses, coordinate, relation, primitive, bound and input names, crossing
surface levels, and the ORDER of every list — and within the corpus's
stated relative tolerance for floats, which is the run's own agreement
window. A sampled comparison SHALL NOT be accepted: every step the corpus
lists SHALL be compared.

The suite SHALL also assert the corpus's own width — the discontinuous
primitives, a multi-source law, a stop located inside a step, a bound
stated as an expression, a command retired blocked, a rate, a run state
taken and restored, both instruction forms, and a step carrying both a
crossing and a stop — so that a narrower corpus copied in is refused here
without anyone running the producer's generator.

#### Scenario: Every scenario of the corpus replays

- **WHEN** the widget suite replays the committed corpus through the run
  engine
- **THEN** every step of every scenario matches, exactly for discrete
  state and within the stated relative tolerance for floats

#### Scenario: A narrowed corpus is refused

- **WHEN** the committed corpus is replaced by one exercising fewer of the
  stated features
- **THEN** the suite fails naming the feature no longer covered

#### Scenario: A drifted engine is caught, not tolerated

- **WHEN** the engine's arithmetic is changed so one machine's bank
  differs in the last bits beyond the corpus's tolerance
- **THEN** the suite fails naming the scenario, the step and the
  coordinate

## MODIFIED Requirements

### Requirement: One loader reads either published document

The viewer SHALL render either portable `manifest.json` or normal-build
`viewer.json`, reading their shared fields. It SHALL render document
versions 1, 2, 3, 4 and 5, and SHALL refuse any other version naming it
and the versions it renders. A document whose `drivers`
table is empty SHALL render exactly as a version 1 document. A document
whose `drivers` table is non-empty SHALL load and render at the pose its
expressions evaluate to under the table's declared defaults, with driver
and instruction entries exposed through the handle's driving API. A
document whose expressions reference a qualified id absent from both its
`drivers` table and its `bindings` table is malformed and SHALL fail
loudly naming the id; under version 5 the identifiers an expression may
name also include the program's clock name, its bank coordinates, the
values it publishes as computed, and, inside a jump plan's own
expressions, that plan's branch placeholders. A version 4 document carries
an ordered `bindings` table, which the viewer SHALL resolve under the
binding requirements above; a document that carries no such table SHALL be
read exactly as it was before the viewer knew of bindings. A version 5
document additionally carries a `program` object, which the viewer SHALL
load and validate under the program requirements above, and whose bank
SHALL pose the tree. The
host supplies the document URL
and an optional mesh base; the base defaults to the document's directory, which
for a document URL naming no directory is the directory the document is served
from and never the server root. A fetch or parse failure SHALL name the
document and the reason.

#### Scenario: A build snapshot rooted elsewhere

- **WHEN** a host mounts a `viewer.json` with a mesh base unrelated to its
  document URL
- **THEN** models load from that base with the same tree, colours, and
  animation as the equivalent export

#### Scenario: A self-contained export

- **WHEN** a host mounts an export without supplying a mesh base
- **THEN** its model paths resolve beside the manifest and it renders

#### Scenario: An export served under a subpath

- **WHEN** a host mounts a document URL that names no directory, as the shipped
  export page does with `manifest.json`, and the page is served under a
  subpath rather than at the server root
- **THEN** model paths resolve beside that document under the same subpath, and
  no request is made to the server root

#### Scenario: An unreachable document

- **WHEN** the source document cannot be fetched
- **THEN** mounting fails with an error naming the document and failure

#### Scenario: A driver document renders at its defaults

- **WHEN** a host mounts a document whose `drivers` table declares
  `x_axis.motor` with default 8000
- **THEN** the model renders at the pose its expressions evaluate to
  with `x_axis.motor = 8000`, and no error is raised

#### Scenario: A malformed driver document is refused

- **WHEN** a mounted document's expressions reference a qualified id
  neither its `drivers` table nor its `bindings` table declares
- **THEN** mounting fails naming that id rather than rendering a wrong
  pose

#### Scenario: A document carrying a bindings table is rendered

- **WHEN** a host mounts a document declaring version 4 and carrying a
  non-empty `bindings` table
- **THEN** it renders at the pose its expressions evaluate to through that
  table

#### Scenario: A document carrying a program is rendered

- **WHEN** a host mounts a document declaring version 5 and carrying a
  `program` object
- **THEN** it renders at the pose the program's published rest values
  evaluate to, and its run is available on the handle

#### Scenario: A version beyond the ones it reads is refused

- **WHEN** a host mounts a document declaring version 6
- **THEN** mounting fails naming that version and the versions the viewer
  renders

#### Scenario: Older documents are untouched

- **WHEN** a host mounts a document declaring version 1, 2, 3 or 4
- **THEN** it loads, poses, animates and drives exactly as it did before
  the viewer could read a program

### Requirement: The viewer declares its API version

The package SHALL declare one API version, expose it on every mount handle and
the browser global, and make it readable without executing the bundle. It SHALL
be raised whenever the mount interface or handle changes incompatibly, and when
a capability a host may require is added to the handle. The declared version
SHALL be 8, reflecting the addition of version-5 document execution — the
document's `program` object, the run it describes, and the `run()` operation
on the handle — on top of version-4 rendering.

The package SHALL also declare, in the same one place, the document schema
versions this build reads, and SHALL report them beside the API version
wherever the API version is reported. A consumer asking which documents a
viewer reads SHALL be answered with that list rather than having to infer
it from the API version, and a consumer that receives no such list SHALL be
entitled to assume the versions every released viewer reads.

#### Scenario: A host checks compatibility before mounting

- **WHEN** a host reads the installed viewer API version
- **THEN** it obtains the package's single declared version without running a
  browser bundle

#### Scenario: A mounted viewer reports its version

- **WHEN** a host inspects a mount handle or the browser global
- **THEN** both report the same declared API version

#### Scenario: A host requires targeted updates

- **WHEN** a host needs `artifactChanged()` and `manifestChanged()`
- **THEN** the declared API version tells it whether they are available

#### Scenario: A host requires camera orientation control

- **WHEN** a host needs to supply an up direction and field of view
- **THEN** the declared API version tells it whether they are available

#### Scenario: A host requires flexible geometry

- **WHEN** a host needs `version: 3` documents rendered
- **THEN** the declared API version tells it whether the capability is
  available

#### Scenario: A host requires documents carrying a bindings table

- **WHEN** a host needs `version: 4` documents rendered
- **THEN** the declared API version tells it whether the capability is
  available

#### Scenario: A producer asks which documents this viewer reads

- **WHEN** a producer asks the installed viewer what it reads, before
  publishing a document
- **THEN** it receives the list of document schema versions this build
  renders, including the running version, from the same declaration the
  bundle refuses by

### Requirement: Client evaluation matches producer numerics

The viewer's expression evaluation — OpenSCAD degree trig, `^` as
exponentiation, `$t`, qualified identifiers resolved through the
value map at every segment of the identifier, and binding names resolved
through the document's table —
SHALL match the producer's numeric resolution of the
same expressions to within floating-point rounding, and that agreement
SHALL be enforced by tests against the shipped evaluator module using
producer-computed expected values covering at least: linear and scaled
driver terms, degree-trig chains, `^` terms, sums whose leading term is
negative, expressions mixing `$t` with drivers, expressions that are or
contain a binding name, and design-to-native
instruction target conversion for integer dtypes.

`sign` SHALL resolve as the producer's own definition does — which side of
zero its argument is on — including at negative zero, where a runtime's
own sign function does not.

The producer-generated corpus SHALL carry the bindings table its cases
reference, and the tests SHALL resolve a case's expression through that
table exactly as the viewer resolves a document's, so the corpus pins the
table's semantics as well as the functions': an entry naming an earlier
entry, an entry over a driver id as well as over `$t`, and an entry
reached from more than one case. A case pinned by an earlier corpus SHALL
keep its key and its expected value.

Agreement SHALL include operator precedence and not only arithmetic. A
unary minus SHALL bind to the term beside it rather than to the rest of
the expression, so a sum whose leading term is negative resolves to that
negative term plus the rest and never to the negation of the whole; and
`^` SHALL bind tighter than a unary minus, as the producer's own
language does.

Agreement SHALL also include the form of the numbers themselves. The
client SHALL read every numeric literal the producer can write, in
particular a literal in exponent notation — which the producer emits
for any magnitude its language prints that way — and SHALL resolve it to
the value those digits name, at any magnitude and without loss from a
floating-point round-trip. A name that merely begins with or contains
the exponent marker SHALL remain a name.

Agreement SHALL hold however evaluation is organized. Sharing a
subexpression between the places that read it, reusing a value already
resolved for the same inputs, and reading a subexpression through a name
the producer published it under, SHALL NOT move a number: a shared
reading, a bound reading and a reading that walked every occurrence
separately SHALL agree exactly, and a
value that is not a number — an unresolved name, or a term that produced no
number — SHALL reach the caller as it does today rather than as a stale or
substituted one.

An expression form the viewer's evaluation cannot support SHALL be refused
when the document is loaded — with the refusals for an unreadable document
version, an unknown flexible technology, an unresolvable bindings table
and an undeclared driver id — naming
the form and quoting the expression, and quoting it in part rather than
whole, since a published expression may be megabytes long. The refusal
SHALL cover every expression the document carries, an operation's, a
flexible node's parameters, a binding's and a program's alike, so that no
such expression is first met while a frame is being rendered or a step
integrated.

#### Scenario: The parity corpus pins the shipped evaluator

- **WHEN** the widget test suite runs the producer-generated parity
  fixture against the shipped evaluator
- **THEN** every expression's client value matches the producer value
  within float rounding, and removing the `^` rewrite makes the suite
  fail

#### Scenario: The corpus pins the bindings table

- **WHEN** the suite runs a corpus whose cases name entries of its
  bindings table, including a case whose whole expression is one name
- **THEN** each value matches the producer value within float rounding,
  and running the same cases without the table installed fails

#### Scenario: A sum whose leading term is negative crosses the boundary

- **WHEN** the corpus carries an expression whose head is a negative
  literal, evaluated at more than one driver setting
- **THEN** the client value matches the producer value at every one of
  them, and a reader that bound the unary minus to the whole sum instead
  would agree at no more than one

#### Scenario: A driver scaled by an exponent-printed factor

- **WHEN** the corpus carries a driver term whose scale is small enough
  that the producer prints it in exponent notation, together with a bare
  tiny literal and a bare large one
- **THEN** the client resolves each to the producer's value, and a reader
  that could not read an exponent literal would fail to parse them at all

#### Scenario: An identifier is not a literal

- **WHEN** an expression names a driver whose id begins with the exponent
  marker, or calls a function whose name contains it
- **THEN** the evaluator reads it as that name and resolves it through
  the driver map or the math context, unchanged

#### Scenario: A shared reading is the same reading

- **WHEN** every expression of the parity corpus is evaluated through the
  sharing evaluation, one input set at a time
- **THEN** each value matches the producer value within float rounding,
  including the degree-trig chains, the `^` terms and the leading negative
  sums

#### Scenario: An unresolved name is still not a number

- **WHEN** an expression names a driver the document does not declare, or
  reaches through one whose value is not a map, and it is evaluated twice
  for the same inputs
- **THEN** both readings produce exactly what the viewer produces today for
  that expression — the same non-number, or the same failure — and neither
  substitutes another node's value

#### Scenario: An unsupported form is refused at load

- **WHEN** a document is loaded whose operation expression, whose flexible
  node's parameter expression, or whose bindings entry carries a form the
  viewer's evaluation does not support, such as an inline function
- **THEN** loading fails naming the form and quoting part of the
  expression, no tree is built for it, a model already standing is left
  standing, and no frame is ever rendered from it

#### Scenario: An identifier of any depth resolves to its value

- **WHEN** an expression names an identifier of three or more segments and
  the viewer holds a value under exactly that identifier
- **THEN** it resolves to that value, as a one- or two-segment identifier
  already does

#### Scenario: The sign of negative zero is the producer's

- **WHEN** an expression applies `sign` to a value that is negative zero
- **THEN** it resolves to what the producer resolves it to
