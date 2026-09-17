## ADDED Requirements

### Requirement: The viewer executes a clocked machine's requests

A version 8 document carries a compiled CLOCKED machine: a bank of every
declared driver and every declared state at its published default, plus
the clock at zero where the machine declares one, and a set of committing
relations each naming the inputs it moves with, the event level it fires
on, and one law per value it writes.

The viewer SHALL hold that bank, SHALL expose it and the machine's
identity on the mount handle, and SHALL accept a REQUEST that moves ONE
declared input along a straight path from where it stands to a stated
value. The value a request names and the travel it reports SHALL both be
in that input's DESIGN units, whatever units the bank holds it in.
Executing a request SHALL, without posing anything until it is done:

- clip the path at every stop the machine declares, under the stop
  requirement below, before locating any event;
- examine every committing relation whose published shapes name the
  moving input, and no others;
- locate every crossing of that relation's event level on the path,
  taking both ends of the path, solving an `affine` level by division and
  cutting a `kinked` level at its own breakpoints before solving each
  piece, and merging crossings no further apart than the machine's
  published crossing tolerance;
- refuse the request when one relation's level crosses more surfaces than
  the machine's published maximum;
- land each crossing on the nearest representable value on the FAR side
  of the surface, deciding membership by reading the level's branch there
  and never by comparing a value to the surface;
- fire a crossing only where the branch RISES between the piece the path
  came from and the landing, and only where the landing lies on the
  request's own path — a landing one representable value beyond the
  request's end belongs to the next request and SHALL NOT fire here,
  while a request resuming from its own landing SHALL fire nothing;
- treat two relations as ONE event exactly when their landings are the
  SAME value, and otherwise as two events in path order;
- read, at each event, every firing relation's sources from the bank as it
  stood BEFORE that event with the moving input at the landing, so the
  order of relations at one event is not observable;
- refuse the request naming the value, both relations and the landing
  when two relations write one value at one event;
- write every firing relation's results together, advance the input to the
  landing, and locate the next event from there, so an event level that
  reads a value the machine just wrote moves with it;
- round a target whose declared type is a whole number to the nearest
  whole number ONCE, taking an exact half to the EVEN one, and apply no
  scaling to a committed value;
- refuse the request when a law produces a value that is not finite.

The request SHALL then pose the tree ONCE from the resulting bank, and
SHALL report the travel it admitted, the stops that truncated it, and the
events it fired, each with the relations that fired it, the fraction of
the path, the input's value there and the values written.

A request the viewer refuses for any reason SHALL leave the bank, the
pose and the model exactly as they stood.

The viewer SHALL provide session control over that bank: a SNAPSHOT of
where the machine stands, a RESTORE of one taken against the SAME
machine — refused by name against another, judged by the machine's
published identity — and a RESET to every published default.

#### Scenario: A request commits what the machine writes

- **WHEN** a host requests that a clocked machine's crank move by one full
  turn, and the machine commits its register at the end of a stroke
- **THEN** the register's new value stands in the bank, the model is posed
  with it, and the request reports one event with the crank's value there

#### Scenario: Several events on one path fire in path order

- **WHEN** a host requests a travel long enough to cross ten event
  surfaces
- **THEN** ten events are reported in path order, each one reading what
  the events before it wrote

#### Scenario: Two relations landing on one value are one event

- **WHEN** two committing relations of one machine land on exactly the
  same value of the moving input
- **THEN** both are reported as ONE event, and each reads the bank as it
  stood before that event rather than what the other wrote

#### Scenario: Two surfaces one representable value apart are two events

- **WHEN** two committing relations land one representable value apart
- **THEN** they are reported as TWO events in path order, and the second
  reads what the first wrote

#### Scenario: A falling step fires nothing

- **WHEN** a request crosses an event surface in the direction that lowers
  the level's branch
- **THEN** no event is reported and nothing is written

#### Scenario: Two writers at one event refuse the request

- **WHEN** two committing relations would write one value at one landing
- **THEN** the request is refused naming that value, both relations as
  they are written in the model, and the landing, and the bank stands
  where it stood

#### Scenario: An integer commit takes an exact half to the even value

- **WHEN** a law lands a whole-number state on an exact half
- **THEN** the value banked is the nearest EVEN whole number, not the one
  a rounding toward positive infinity would give

#### Scenario: A request is refused whole

- **WHEN** a request would produce a value that is not finite, or crosses
  more surfaces than the machine admits
- **THEN** the request is refused naming what happened, and the bank, the
  pose and the model are exactly as they were before it

#### Scenario: A bank is restored only onto the machine it was taken from

- **WHEN** a host restores a snapshot taken against a different clocked
  machine
- **THEN** the restore is refused naming the two identities, and the
  machine stands where it stood

### Requirement: A declared stop stops a clocked request on its path

A clocked machine publishes one compiled CONSTRAINT per bounded
coordinate and side, each carrying the expression that gives the
coordinate its value over the bank, the bound itself, the level's jump
plan, and the classification of that level in each input that can move
it.

The viewer SHALL CLIP a request against every such constraint the moving
input can move, BEFORE it locates a single event, and SHALL truncate the
request's travel to the largest the machine's stops allow. It SHALL, for
each constraint:

- evaluate the coordinate's own expression over the bank as it stands
  when the request BEGINS, and hold that value under the machine's
  published reserved name for the whole request, so a bound reading its
  own coordinate reads where it stood rather than where it is going;
- read its threshold ONCE, at the request's start, as the greater of zero
  and the level there, so a machine standing OUTSIDE a bound may move as
  long as it does not go further out, and nothing is ever clamped or
  silently repaired;
- take the level as the bound subtracted from the coordinate's value on
  the high side and the reverse on the low, partition the path at the
  level's own jump surfaces, and solve each piece by that level's
  published classification, taking the stop at the end of the last piece
  on which the level was satisfied;
- land on the nearest representable value of the input that still
  satisfies the constraint, deciding membership by EVALUATING the level
  there and never by comparing a value to a bound.

The EARLIEST landing across every constraint SHALL become the request's
end, and the request SHALL then locate its events on the clipped path
only. A request clipped to ZERO travel SHALL be ADMITTED, not refused: it
commits nothing, poses nothing new, and reports what stopped it.

Every constraint met at that landing SHALL be reported as a STOP naming
the coordinate, the side, what the bound evaluates to there, what the
coordinate is worth there, where the input landed and the fraction of the
requested travel that was. A constraint the moving input cannot move
SHALL NOT be examined on the path.

After the last event and BEFORE the model is posed, the viewer SHALL
judge every constraint again over the bank the request ends at, through
the same expressions and against the same thresholds. A coordinate
carried outside its bound by a COMMIT SHALL refuse the whole request,
naming the node, the joint, the coordinate, the side, the bound and the
value, and SHALL leave the bank, the pose and the model exactly as they
stood.

#### Scenario: An interlock stops a request short

- **WHEN** a maker asks a clocked machine's crank to turn further than a
  declared stop allows
- **THEN** the crank stands at the stop, the request reports the travel
  it admitted and the stop by coordinate and side, and only the events on
  the travelled part of the path fired

#### Scenario: A held part admits nothing and says so

- **WHEN** a maker asks an input to move while an interlock holds it
- **THEN** the request is ADMITTED with zero travel, nothing is committed,
  the model does not move, and the stop is reported rather than an error

#### Scenario: A machine standing outside a bound may move back

- **WHEN** a clocked machine's bank stands outside a declared bound and a
  request moves it back towards the bound
- **THEN** the request is admitted, and a request that would carry it
  further out is stopped where it stands

#### Scenario: A bound that reads its own coordinate holds it still

- **WHEN** both bounds of a coordinate read that coordinate's own value,
  and a request would move it while the machine is off rest
- **THEN** the request admits no travel at all, and the same request with
  the machine at rest admits all of it

#### Scenario: A commit that carries a coordinate out of range refuses the request

- **WHEN** an event inside a request writes a value that carries a
  bounded coordinate outside its bound
- **THEN** the whole request is refused naming the joint, the coordinate,
  the side and the bound, nothing is committed, and the model is not
  posed

### Requirement: A clocked machine the viewer cannot execute is refused by name

A document this viewer cannot execute SHALL be refused rather than
rendered in part, and the refusal SHALL name what the document carries.

The viewer SHALL refuse at load, naming the offending key and value: a
version 8 document carrying no clocked machine; a clocked machine missing
any of its published keys, or carrying one of the wrong type; a
committing relation whose event level names a primitive this viewer does
not implement, whose shapes name a classification it does not implement,
or whose laws do not align with the values it writes; a compiled
constraint missing a published key, naming a side that is neither low nor
high, or carrying a jump plan or a classification this viewer does not
implement; a states table that is not a table of declarations, or one
whose names collide with the declared drivers; an expression naming an
identifier neither table nor the machine's own reserved names declare.

The viewer SHALL refuse a REQUEST, leaving the document loaded and the
model posed, when the request names the machine's CLOCK — this build
poses a clocked machine at the instant its clock stands at and does not
advance it — and when a host asks a clocked machine for a cadence it does
not have: a rate, a triggered instruction, or a step of a run.

#### Scenario: A malformed clocked machine is refused by name

- **WHEN** a mounted version 8 document's clocked machine carries a
  relation whose event level names a primitive this viewer does not
  implement
- **THEN** mounting fails naming that relation as it is written in the
  model and the primitive, rather than executing a machine it does not
  understand

#### Scenario: A request on the clock is refused and the model stands

- **WHEN** a host requests that a clocked machine's clock advance
- **THEN** the request is refused naming the clock, the document stays
  loaded, and the model stays posed at the bank it already showed

#### Scenario: A cadence a clocked machine does not have is refused

- **WHEN** a host asks a clocked machine to trigger a declared
  instruction, or to run at a rate
- **THEN** the call is refused naming what was asked and what a clocked
  machine offers instead, and nothing about the machine changes

### Requirement: The two runtimes agree on the clocked corpus

The producer publishes a clocked conformance corpus: one document per
machine, embedded verbatim, a script of requests and session operations,
and — per step — the whole bank afterwards, the travel admitted, the
events fired with their landings and the values written, and, for a step
the producer refused, the KIND of refusal and the qualified names its
message carries.

The package SHALL carry that corpus as the producer generated it, byte
for byte, and SHALL replay it. Agreement SHALL be EXACT: every recorded
number SHALL be reproduced bit for bit, and the tolerance compared
against SHALL be the one the corpus file itself states rather than one
the reader chooses. A disagreement SHALL be treated as a defect of this
engine, and SHALL NOT be answered by widening a comparison, editing the
fixture or omitting a scenario.

The replay SHALL load and execute EVERY machine of the corpus, and SHALL
compare, per step, the whole bank, the travel admitted, the events fired,
the STOPS met and the refusals by kind and by name.

Where this build deliberately does not do what the producer did — a
request that advances a machine's CLOCK, which this build refuses — the
replay SHALL assert that departure explicitly, by kind and by name, and
SHALL name the steps it therefore cannot compare because the bank has
diverged. The set of such steps SHALL be derived from the corpus file
itself rather than from a list maintained by hand, and a CENSUS of the
replayed, departed and deferred steps SHALL be asserted, so a corpus
regenerated wider or narrower than the one this build was written against
fails loudly here without anyone running the producer's generator.

#### Scenario: The engine reproduces the producer's own numbers

- **WHEN** the corpus is replayed through this package's clocked executor
- **THEN** every recorded bank value, admitted travel, landing and written
  value is reproduced exactly, with no tolerance

#### Scenario: A refusal is matched by kind and by name

- **WHEN** the corpus records a step the producer refused
- **THEN** this engine refuses the same step with the same kind, its
  message carries every qualified name the corpus lists, and the bank
  afterwards is the one the corpus records

#### Scenario: A machine with interlocks is replayed like any other

- **WHEN** the corpus carries a machine whose clocked object declares a
  stop
- **THEN** its script is replayed step by step like every other machine's,
  and the stops it records are reproduced exactly

#### Scenario: A step this build does not perform is a stated departure

- **WHEN** the corpus records a step that advances a machine's clock
- **THEN** the replay asserts that this build refuses that step by kind
  and by name, and names the steps after it that it therefore does not
  compare, rather than passing over them in silence

#### Scenario: A regenerated corpus is loud

- **WHEN** a corpus is copied in carrying more machines or more steps than
  this build was written against
- **THEN** the census fails naming the difference, rather than replaying a
  subset in silence

### Requirement: A maker operates a clocked machine on screen

For a document carrying a clocked machine, the viewer SHALL present the
focused layer's declared inputs as HANDLES and its declared states as
follow-only READOUTS.

Each input's handle SHALL show where the input stands, in design units,
and SHALL offer a way to move it to another value; every such gesture
SHALL submit exactly ONE request to move that input TO the value the
gesture names, and SHALL report that request's outcome where the gesture
was made — the travel admitted, the STOPS that truncated it named by
coordinate and side, or the refusal's own message. A gesture an interlock
holds SHALL be reported as a stop at that control rather than passed over
as a control that did nothing. A declared range SHALL be presentation only
and SHALL NOT clamp a request.

A state SHALL NOT be presented as a handle and SHALL NOT be a source of
any request; its readout SHALL follow the committed bank. A machine's
CLOCK, where it declares one, SHALL likewise be shown as a readout and
never as a handle.

Declared instructions SHALL be listed and SHALL be presented as
unavailable, with the reason available to a reader and to assistive
tools: a clocked document publishes its instructions and this build gives
them no meaning.

The chrome SHALL offer snapshot, restore and reset of the machine's bank,
and SHALL NOT offer a transport — a clocked machine has no cadence to
run, step or speed. A document's `$t` animation SHALL be presented
exactly as it is for a document carrying no machine at all.

#### Scenario: A maker moves an input and the machine commits

- **WHEN** a maker moves a clocked machine's crank handle to a new value
- **THEN** one request is submitted to move that input to that value, the
  model poses at the resulting bank, and the handle reports the travel
  admitted

#### Scenario: A register is read, never driven

- **WHEN** a clocked machine's focused layer declares states
- **THEN** each is shown as a readout following the committed bank, with
  no control that could move it

#### Scenario: A refused request is reported where it was made

- **WHEN** a maker's gesture submits a request the machine refuses
- **THEN** the refusal's message is shown at that control, and every
  readout still shows the bank the machine stood at

#### Scenario: A gesture an interlock holds says so at the control

- **WHEN** a maker moves a handle an interlock holds still
- **THEN** that control reports the stop by coordinate and side and the
  travel it admitted, the model does not move, and nothing is reported as
  an error

#### Scenario: A declared instruction is shown and unavailable

- **WHEN** a clocked document declares instructions
- **THEN** each is listed and presented as unavailable, rather than hidden
  or offered as a gesture that cannot be honoured

#### Scenario: A clocked model animates while its bank stands

- **WHEN** a clocked document carries geometry that is a formula of `$t`
- **THEN** the timeline plays it exactly as it does for a document
  carrying no machine, and the bank stands throughout

## MODIFIED Requirements

### Requirement: One loader reads either published document

The viewer SHALL render either portable `manifest.json` or normal-build
`viewer.json`, reading their shared fields. It SHALL render document
versions 1, 2, 3, 4, 5, 6, 7 and 8, and SHALL refuse any other version
naming it and the versions it renders. A document whose `drivers`
table is empty SHALL render exactly as a version 1 document. A document
whose `drivers` table is non-empty SHALL load and render at the pose its
expressions evaluate to under the table's declared defaults, with driver
and instruction entries exposed through the handle's driving API. A
document whose expressions reference a qualified id absent from both its
`drivers` table and its `bindings` table is malformed and SHALL fail
loudly naming the id; under version 5 and above the identifiers an
expression may name also include the program's clock name, its bank coordinates, the
values it publishes as computed, and, inside a jump plan's own
expressions, that plan's branch placeholders; under version 8 they are
the document's declared drivers, its declared states, the clocked
machine's clock name where it declares one, its published reserved name
for a bound's own coordinate, and, inside a constraint's jump plan, that
plan's branch placeholders. A version 4 document carries
an ordered `bindings` table, which the viewer SHALL resolve under the
binding requirements above; a document that carries no such table SHALL be
read exactly as it was before the viewer knew of bindings. A version 5
document additionally carries a `program` object, which the viewer SHALL
load and validate under the program requirements above, and whose bank
SHALL pose the tree. A version 6 document is a version 5 one whose
compiled program carries at least one law edge that reads the coordinate
it drives; it carries NO further key, its shape is otherwise identical,
and the viewer SHALL load, validate and execute it exactly as it does a
version 5 one. A version 6 document whose program carries no such edge
SHALL NOT be refused for that: the version is a property of the content
the producer published, and this viewer judges the content. A version 7
document is a version 6 one whose compiled program carries a cycle of
edges every one of whose in-cycle dependencies some selection switches;
it too carries NO further key and its shape is otherwise identical, and
the viewer SHALL load, validate and execute it under the requirement
"The worker orders a block per piece". A version 7 document whose program
carries no such cycle SHALL NOT be refused for that either, and SHALL
load, pose and run exactly as the same document declared at version 5 or
6 would. A version 8 document is a CLOCKED
machine rather than a running one: it carries a `states` table beside
`drivers`, a `clocked` object, and NO `program` and NO `controls` key. The
viewer SHALL load and validate that object under the clocked requirements
below, SHALL pose the tree from the bank its two tables declare, and SHALL
present the document's `$t` animation over that standing bank. A version 8
document carrying no `clocked` object, or carrying a `program` object
beside it, SHALL be refused naming what it carries. A version 5 document MAY also carry a `controls`
table, which the viewer SHALL read and validate under the control
requirements above; the table is additive and does not move the document's
version, a document carrying none SHALL be read exactly as it was before
the viewer knew of controls, and a document below version 5 carrying one
SHALL be refused naming it. The
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

#### Scenario: A document carrying a controls table is rendered

- **WHEN** a host mounts a document declaring version 5 and carrying both a
  `program` object and a `controls` table
- **THEN** it renders exactly as the same document without that table does,
  its run is available on the handle, and the parts the table names are
  touchable

#### Scenario: A version beyond the ones it reads is refused

- **WHEN** a host mounts a document declaring version 9
- **THEN** mounting fails naming that version and the versions the viewer
  renders

#### Scenario: A document whose program reads a driven coordinate is rendered

- **WHEN** a host mounts a document declaring version 6, whose program
  carries a law edge naming one of its driven ends among the values it
  reads
- **THEN** it renders at the pose the program's published rest values
  evaluate to, its run is available on the handle, and nothing about the
  document's shape differs from a version 5 one

#### Scenario: A version 6 document with no such law is rendered too

- **WHEN** a host mounts a document declaring version 6 whose program
  carries no law edge reading a coordinate it drives
- **THEN** it loads, poses and runs exactly as the same document declared
  at version 5 would

#### Scenario: A document whose program carries a block is rendered

- **WHEN** a host mounts a document declaring version 7, whose program's
  edges carry a cycle over what they read and determine
- **THEN** it renders at the pose the program's published rest values
  evaluate to, its run is available on the handle, and nothing about the
  document's shape differs from a version 6 one

#### Scenario: A version 7 document with no such cycle is rendered too

- **WHEN** a host mounts a document declaring version 7 whose program's
  edges carry no cycle at all
- **THEN** it loads, poses and runs exactly as the same document declared
  at version 5 or 6 would

#### Scenario: Older documents are untouched

- **WHEN** a host mounts a document declaring version 1, 2, 3 or 4
- **THEN** it loads, poses, animates and drives exactly as it did before
  the viewer could read a program

#### Scenario: A clocked document is rendered at its initial bank

- **WHEN** a host mounts a document declaring version 8, carrying a
  `states` table and a `clocked` object
- **THEN** it renders at the pose its drivers' and states' declared
  defaults evaluate to, its machine is available on the handle, and its
  `run()` is null

#### Scenario: A version 8 document carrying no clocked machine is refused

- **WHEN** a host mounts a document declaring version 8 with no `clocked`
  key
- **THEN** mounting fails saying a version 8 document is a compiled
  clocked machine and there is nothing to operate without it

#### Scenario: A document carrying both a program and a clocked machine is refused

- **WHEN** a host mounts a document carrying both a `program` object and a
  `clocked` object
- **THEN** mounting fails naming both, rather than executing one of two
  machines

### Requirement: The viewer declares its API version

The package SHALL declare one API version, expose it on every mount handle and
the browser global, and make it readable without executing the bundle. It SHALL
be raised whenever the mount interface or handle changes incompatibly, and when
a capability a host may require is added. The declared version SHALL be 17,
reflecting the execution of a clocked machine's requests — the version 8
document a build at the previous version refuses by name — on top of the
ordering of a block of the compiled program once per piece of a step, and of the execution of a law that reads the coordinate it drives, the
drawing of the markings a document's parts carry, part controls, the inspector
layout, the mountable assembly navigator, the published assembly-navigation
state and its change subscription.

The package SHALL also declare, in the same one place, the document schema
versions this build reads, and SHALL report them beside the API version
wherever the API version is reported. A consumer asking which documents a
viewer reads SHALL be answered with that list rather than having to infer
it from the API version, and a consumer that receives no such list SHALL be
entitled to assume the versions every released viewer reads. Reading a
document's controls table or a node's markings list SHALL NOT change that list:
both are additive within the document versions that carry them, and the API
version is the only capability gate either moves.

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

#### Scenario: A host requires the published navigation state

- **WHEN** a host needs to read the focused root and the hidden paths, and
  to be told when they change
- **THEN** the declared API version tells it whether the capability is
  available, before it mounts a bundle it cannot build a navigator on

#### Scenario: A host requires the mountable navigator

- **WHEN** a host means to present the package's own assembly navigator
  rather than build one
- **THEN** the declared API version tells it whether the bundle carries
  one, before it mounts a bundle that publishes the navigation state but
  no navigator

#### Scenario: A host requires the inspector layout

- **WHEN** a host means to mount the package's composed inspector —
  sidebar, navigator and viewer in one element — rather than lay those
  parts out itself
- **THEN** the declared API version tells it whether the bundle carries
  one, before it mounts a bundle that carries a navigator and no layout to
  put it in

#### Scenario: A host requires part controls

- **WHEN** a host means to present a machine a maker drives by touching it,
  rather than only from a panel
- **THEN** the declared API version tells it whether this bundle reads a
  document's controls table and binds a pick to it, before it mounts a
  bundle that would show the same document with no affordance at all

#### Scenario: A producer asks which documents this viewer reads

- **WHEN** a producer asks the installed viewer what it reads, before
  publishing a document
- **THEN** it receives the list of document schema versions this build
  renders, including the running version, from the same declaration the
  bundle refuses by

#### Scenario: A host requires a self-read program executed

- **WHEN** a host means to present a machine one of whose laws reads the
  coordinate it drives — a rack that turns a dial only while the dial is
  not already standing in its own gap — which the producer publishes as a
  version 6 document
- **THEN** the declared API version tells it whether this bundle executes
  one, before it mounts a bundle that would refuse the document by name
  and render nothing at all

#### Scenario: A host requires the markings drawn

- **WHEN** a host means to present a machine whose answer is printed on its
  parts — a calculator's digits, a dial's graduations — rather than a blank
  drum
- **THEN** the declared API version tells it whether this bundle draws a
  document's markings, before it mounts a bundle that would show the same
  document with nothing readable on it

#### Scenario: A host requires a clocked machine executed

- **WHEN** a host means to present a machine with MEMORY and no cadence —
  a calculator whose registers are written at the end of a stroke — which
  the producer publishes as a version 8 document
- **THEN** the declared API version tells it whether this bundle executes
  one, before it mounts a bundle that would refuse the document by name
  and render nothing at all
