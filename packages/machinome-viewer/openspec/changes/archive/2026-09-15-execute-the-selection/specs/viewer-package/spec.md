## ADDED Requirements

### Requirement: The worker orders a block per piece

A published program's dependency graph — edge A before edge B when B
reads a value A determines, with a value an edge itself determines
EXCLUDED — MAY carry a cycle. Every nontrivial strongly connected
component of it is a **BLOCK**, and the viewer SHALL recognise a block
from what the document already carries, requiring no further key for it.
A program with no such component SHALL be executed exactly as it is
today, by the same code, at the same cost.

**The published order of a block's members is a LISTING and not an
execution order.** The viewer SHALL NOT execute a block's members in the
order they are published. It SHALL contract each block to ONE entry of
the program, at the position of the block's first published member, every
other edge keeping its published position and the edges their relative
order; and it SHALL verify that the result is an order in which every
entry's sources are determined before it runs, refusing the document
naming the two edges and the value otherwise. A consumer that re-sorted
the published edges would be inventing an ordering decision the producer
already made.

A **SELECTOR** of a block member is a jump node of that member's plan
whose published level quantity, closed over the document's own bindings
table and resolved transitively through the branch placeholders it names,
reads no value the block determines. A selector's branch is therefore
known before the block runs. A node whose level reads the member's own
driven end is NOT a selector and SHALL stay in the walked layer of the
requirement "The worker executes a law that reads the coordinate it
drives".

A source of a member is **SWITCHED** when setting a selector's branch to
ZERO removes it from that member's law. The viewer SHALL decide this by
folding the member's published skeleton with `x*0`, `0*x` and `0/x`
taken as zero, `0+y`, `y+0`, `y−0` as the surviving operand and `0−y` as
its negation, and reading what the folded skeleton then names, following
every surviving placeholder into its own folded level quantity. A branch
SHALL be admitted as foldable only where its primitive holds that branch
over an INTERVAL of its level quantity — a floor, a ceiling, a remainder
or a comparison — and never where it holds it at a single point, which
is the case of a sign. ONE fold per member with every foldable selector
at zero SHALL decide both what that member reads unconditionally and what
a selection can switch; the value a member reads of its OWN driven end is
neither.

A shape that can never be ordered SHALL be refused when the document is
loaded, under the requirement "A program the viewer cannot execute is
refused by name". The check is deliberately NECESSARY and not SUFFICIENT:
which branch vectors a machine can actually reach is arithmetic about its
inputs rather than structure, so a particular piece that is still cyclic
is refused when it is met.

**Over one step a block SHALL be run PIECE BY PIECE.**

- Every member's SELECTOR crossings SHALL be located over the WHOLE
  stretch, by the partition any other law's path is cut by, over a plan
  of that member's selectors alone; they SHALL be merged into one cut
  list in the members' own order and each member's published jump order,
  under the published crossing tolerance and crossing limit; and they
  SHALL be recorded as crossings of the member whose plan states them.
- On each piece every selector's branch SHALL be read at the piece's
  MIDPOINT, and each member's ACTIVE sources SHALL be what its skeleton
  still reads with those actual branch values substituted. The members
  SHALL be ordered over the in-block ones, a member's own driven end
  ignored, and that order SHALL be reused for any later piece whose
  selectors read the same branch VALUES.
- A piece whose active dependencies are still cyclic SHALL refuse the
  step, naming the piece, the relations on the cycle, and each selector
  with its primitive, its level quantity and the value it read. The step
  SHALL commit nothing.
- The members SHALL then run over the piece in that order, each by the
  machinery that already governs it. A source the block does not
  determine SHALL be taken at its value at the piece's left end, moving
  by its share of the stretch. A source the block DOES determine SHALL be
  taken at the value the block has advanced it to by the piece's start,
  moving by the increment computed for it ON THIS PIECE — and by ZERO
  where this piece's order has not determined it, which is safe because
  every term reading it is multiplied by a branch the block forced to
  zero.
- **Every selector SHALL be a CONSTANT for every member on that piece**:
  the branch the block read SHALL be substituted into the member's own
  plan rather than re-derived inside the piece. A forced node's crossings
  SHALL NOT be located again, and every reading of its branch — in either
  layer of a self-read walk, in a probe, in a cut and in a far-side
  landing — SHALL be the value the block substituted.

**What a block reports.** For each value it determines it SHALL report
the sum of that value's increments over the pieces. For a value at least
one piece PLACED, it SHALL additionally report the ABSOLUTE value it has
advanced that value to by the END of the stretch — the placement plus
every later piece's increment — and the step SHALL commit that, because a
reported absolute replaces the starting value plus the increment and
would otherwise discard the motion after it. A value no piece placed
SHALL be reported as an increment only.

Every crossing a member reports inside a piece SHALL be rescaled to its
fraction of the whole stretch, and the whole list — the selectors'
crossings located over the stretch and the members' own rescaled out of
their pieces — SHALL be sorted by that fraction before it is recorded, so
the listing does not depend on which was computed first.

**A declared bound on a value a block determines SHALL be SEARCHED and
never solved**, whatever affinity the member that determines it
publishes: a block's value is piecewise in the selector partition and
re-ordered across it.

A block SHALL be complete and side-effect-free when it is asked for
increments alone — as the probe that decides which inputs a stop blocks
asks — recording no crossing, reporting no placement and mutating
nothing, and SHALL refuse a cyclic piece there under the same midpoint
reading and the same ordering it uses inside the step, so that a probe
and the step it is probing for cannot disagree about whether the machine
can be ordered. The inputs a stop on a block's value blocks SHALL be
decided by displacing each candidate alone and running the WHOLE block
under that displacement, so an input that reaches the stopped value only
through a selection that is inactive at that moment SHALL NOT be blocked.

#### Scenario: A carry that follows the carriage runs

- **WHEN** a document is mounted whose program carries two laws each
  reading what the other determines, one gated on a carriage position
  below a detent and the other above it, and the carriage is left below
  the detent while the crank is turned
- **THEN** the run commits the values the producer commits for the same
  machine, the carry reaching the wheel in the step it was made rather
  than a step later or not at all

#### Scenario: The published listing is not the execution order

- **WHEN** a block's members are published in an order in which one reads
  what a later one determines, which is what the producer's listing does
- **THEN** the step orders them by the dependencies the piece's own
  selection leaves active, and the committed bank does not depend on the
  order the members were listed in

#### Scenario: A selection crossing cuts the step

- **WHEN** one step carries the selecting input across the value at which
  a block's selection changes
- **THEN** the stretch is cut there, each piece is ordered under the
  branches read at its own midpoint, the members run over each piece with
  their in-block values carried forward, and the crossing is recorded at
  its fraction of the step

#### Scenario: A selection change alone moves nothing

- **WHEN** the selecting input is moved from one side of a selection to
  the other and back, with nothing else moving
- **THEN** every value the block determines holds the float it held,
  bit for bit

#### Scenario: A value placed in one piece and moved in a later one

- **WHEN** one step places a block's value at a gate in one piece and
  another source drives it further in a later piece of the same step
- **THEN** the committed bank holds the value the block advanced it to by
  the end of the step, not the value the placement left it at

#### Scenario: A piece that cannot be ordered refuses the step

- **WHEN** a step reads a selection under which every dependency of a
  block's cycle is active
- **THEN** the step commits nothing, the bank, the step count and the
  pose stand, the commands that moved are retired reporting that the step
  did not happen, and the report names the piece, the relations on the
  cycle and what each selector read

#### Scenario: A stop on a block's value is searched

- **WHEN** a step drives a value a block determines into a declared bound
- **THEN** the fraction at which it reaches the bound is found by
  sampling and bisection over the whole block rather than solved from the
  member's published affinity, and the value is committed exactly at its
  bound

#### Scenario: An inactive selection blocks nothing

- **WHEN** a value a block determines reaches a declared bound while an
  input that reaches it only through a selection that is currently
  inactive is running
- **THEN** that input is not blocked and its command completes its whole
  travel, while the input that does push the value retires blocked

#### Scenario: A program with no cycle is untouched

- **WHEN** a document whose program's dependency graph has no cycle is
  run
- **THEN** every step propagates over the published edges in the
  published order exactly as it did before the viewer knew of blocks, at
  the same cost, and the committed bank is the same float for float

## MODIFIED Requirements

### Requirement: One loader reads either published document

The viewer SHALL render either portable `manifest.json` or normal-build
`viewer.json`, reading their shared fields. It SHALL render document
versions 1, 2, 3, 4, 5, 6 and 7, and SHALL refuse any other version naming
it and the versions it renders. A document whose `drivers`
table is empty SHALL render exactly as a version 1 document. A document
whose `drivers` table is non-empty SHALL load and render at the pose its
expressions evaluate to under the table's declared defaults, with driver
and instruction entries exposed through the handle's driving API. A
document whose expressions reference a qualified id absent from both its
`drivers` table and its `bindings` table is malformed and SHALL fail
loudly naming the id; under version 5 and above the identifiers an
expression may name also include the program's clock name, its bank coordinates, the
values it publishes as computed, and, inside a jump plan's own
expressions, that plan's branch placeholders. A version 4 document carries
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
6 would. A version 5 document MAY also carry a `controls`
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

- **WHEN** a host mounts a document declaring version 8
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

### Requirement: The viewer declares its API version

The package SHALL declare one API version, expose it on every mount handle and
the browser global, and make it readable without executing the bundle. It SHALL
be raised whenever the mount interface or handle changes incompatibly, and when
a capability a host may require is added. The declared version SHALL be 16,
reflecting the ordering of a block of the compiled program once per piece of a
step — the version 7 document a build at the previous version refuses by name —
on top of the execution of a law that reads the coordinate it drives, the
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

### Requirement: The step reproduces the producer's own integration

For each step the viewer SHALL take the movement each active command
admits for that step — a pure function of the number of steps since the
command started, so a replayed run admits exactly the same travel — and
propagate it over the edges in the published order, producing one
increment per determined value and committing them together. Where the
published edges carry a cycle, the entries propagated over are the edges
with each such cycle contracted to ONE entry, ordered under the
requirement "The worker orders a block per piece"; a program with no
cycle is propagated over exactly as it was before the viewer knew of
blocks.

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
- A **law that READS THE COORDINATE IT DRIVES** SHALL instead be
  integrated piece by piece, under the requirement "The worker executes a
  law that reads the coordinate it drives" below. Such a law SHALL
  additionally report, for a driven end at least one of whose cuts placed
  it, the ABSOLUTE value that end holds at the end of the step, and the
  step SHALL commit that value rather than the coordinate's starting
  value plus its increment.
- A **BLOCK** — a cycle of edges contracted to one entry — SHALL
  contribute, for each value it determines, the sum of that value's
  increments over the pieces its selectors cut the step into, each piece
  ordered and run under the requirement "The worker orders a block per
  piece"; and SHALL additionally report, for a value at least one of
  those pieces placed, the ABSOLUTE value it has advanced that value to
  by the END of the step, which the step SHALL commit in place of the
  starting value plus the increment.
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
be stopped. A bound that reads the bounded coordinate alone SHALL be
evaluated once per step from the committed bank, so every segment of one
step is measured against the same number.

An absolute value reported by a law that reads the coordinate it drives,
or by a block, SHALL be applied to the segment's committed state BEFORE
any bound is examined, so that the bounds are judged against the value the step will
actually commit; and where a declared bound stops the same coordinate in
the same segment, the BOUND SHALL win, the coordinate being committed
exactly at it. Such a report SHALL NOT be a stop: it stops no input,
retires no command, and appears in the crossing record rather than the
stop record.

A bound that READS OTHER COORDINATES SHALL instead be evaluated ALONG
the path of each stretch: the bounded coordinate inside the expression
SHALL take the value it holds in the STEP's committed bank, and every
coordinate the bound reads SHALL take the value it has along the
stretch's path, computed by one pass over that bound's sub-program with
every input's admission scaled by the fraction — the same arithmetic the
segment is later committed by, edge for edge. The CONSTRAINT LEVEL of
such a bound is the coordinate's value minus the evaluated upper bound,
or the evaluated lower bound minus the coordinate's value; outside is
positive.

Such a bound SHALL be examined on a stretch only when the bounded
coordinate or one of its reads has a nonzero increment over that
stretch, so a stretch in which nothing it depends on moves SHALL
evaluate nothing and SHALL stop nothing, and a coordinate left standing
outside SHALL be free until something carries it further. On a stretch
in which NO read moves, the bound SHALL be the number its expression
gives at the step's committed own value and the reads' start-of-stretch
values, evaluated once, and the coordinate SHALL be stopped or freed
exactly as a bound over its own value alone is — the same detection, the
same localization, and the same commit exactly at the bound.

When a read moves, the level SHALL be sampled at the published number of
sub-intervals, each sample one pass over the sub-program, and the
stretch SHALL stop at the FIRST sample at which the level is positive
AND greater than the level at the stretch's start; a level already
positive at the start with a higher first sample SHALL stop the stretch
at its beginning. The crossing SHALL be bracketed against the previous
sample and bisected to the published crossing tolerance within the
published number of rounds, and the fraction taken SHALL be the INSIDE
end of the final bracket — the last fraction at which the bound is
satisfied. The coordinate SHALL NOT be moved onto such a bound: the
segment committed at that fraction satisfies it by the same arithmetic
that located it. The viewer SHALL assert that it does, at the state the
segment commits, and SHALL refuse the whole step as a broken invariant
otherwise.

The GROUP such a stop stops SHALL be every candidate of that bound with
a nonzero admission whose admission ALONE, over the sub-program, raises
the constraint level from the start of the stretch to its end. An input
moving the bounded coordinate against the bound SHALL therefore be
stopped; an input moving a read so as to make a STANDING position
invalid SHALL be stopped where the bound becomes active, and the
standing coordinate SHALL NOT move; and an input moving a read so as to
RELIEVE the bound SHALL run its whole step. The stop SHALL record the
bound EVALUATED at the committed state, which for such a bound is not
the value the coordinate holds.

A step SHALL be atomic across its segments: the bank, the commands'
admitted travel and the records SHALL be applied only once every segment
has succeeded. A conflict, a partition exceeding the published crossing
limit, a law that cannot be integrated over the step's path, a cut that
places a self-read coordinate nowhere, a stop that
stops no moving input, or a bound the committed state does not satisfy
SHALL commit nothing — the bank, the step count and the pose stand —
SHALL retire the commands that moved an input in that step reporting that
the step did not happen, and SHALL report what disagreed, naming the
relation as its author wrote it and the class that stated it.

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

#### Scenario: A step commits the value a cut left a coordinate at

- **WHEN** a step cuts a self-read law's path and the cut places its
  driven coordinate, and no declared bound stops that coordinate in the
  same segment
- **THEN** the committed bank holds the value the walk left it at rather
  than its starting value plus the step's increment, no stop is recorded
  for it, and the crossing is in the crossing record

#### Scenario: A bound on the same coordinate wins over the value a cut left

- **WHEN** one segment both cuts a self-read law's path, placing its
  driven coordinate, and takes that same coordinate past a declared bound
- **THEN** the coordinate is committed exactly at its bound, the stop is
  recorded naming it, and the value the cut placed it at is not what the
  step commits

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

#### Scenario: A bounded coordinate is blocked while what its bound reads is in the wrong place

- **WHEN** a step asks an input to move a coordinate whose bound reads
  other coordinates, and those coordinates stand where the bound
  evaluates to the coordinate's current value
- **THEN** the step commits with the coordinate exactly where it stood,
  the command retires blocked with nothing admitted, and the stop names
  the coordinate, the side, the evaluated bound, the fraction zero and
  that input

#### Scenario: One step both frees the bound and asks for the movement it frees

- **WHEN** one step moves the coordinates a bound reads into the place
  that frees it AND asks an input to move the bounded coordinate
- **THEN** the step that frees it completes in full, the bounded
  coordinate does not move inside that step, and the same request made
  on the next step completes

#### Scenario: A dependency never overruns a standing coordinate

- **WHEN** a coordinate stands inside its bound and an input moves a
  coordinate that bound READS, so as to make that standing position
  invalid
- **THEN** the input moving the read is stopped at the fraction at which
  the bound becomes active, its command retires blocked with the travel
  it made, the standing coordinate does not move at all, and the stop
  names the STANDING coordinate with the bound evaluated at the
  committed state

#### Scenario: A bound satisfied again by the end of the step is still a stop

- **WHEN** a step would carry a bound outside part-way through and back
  inside by its end
- **THEN** the step is stopped where the violation begins rather than
  committed whole

#### Scenario: A quiet bound costs nothing

- **WHEN** a step moves nothing a bound that reads other coordinates
  depends on
- **THEN** that bound is not evaluated, nothing is stopped by it, and a
  coordinate standing outside it stays where it is

#### Scenario: A block's values are committed together with the rest

- **WHEN** a step propagates over a program whose edges carry a cycle
- **THEN** the values that cycle determines are committed in the same
  bank as every other value of that step, a conflict between two routes
  is judged by the same agreement window, and a step that fails commits
  none of them

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
plans share; an expression, skeleton or level quantity whose free names
are not among the ones that edge may read; a bound naming anything but
the coordinate it bounds and the program's own bank coordinates; a
declared bound over a coordinate the bank does not hold; a limit that is
missing or not a finite number; a computed value the document reads that
no edge determines; a clock name that is also a coordinate or a driver
id; and an identifier set that cannot be resolved as names, such as one
identifier being a strict prefix of another.

For a law edge that READS THE COORDINATE IT DRIVES — one naming a value
among both what it reads and what it determines — the refusal SHALL also
cover: such an edge that determines more than one value, or that reads
more than one of the values it determines, saying that a law reading its
own driven end drives exactly one coordinate; such an edge whose driven
end is a published computed value rather than a coordinate of the bank,
saying that a retained value is a history and only a coordinate the run
banks keeps one; and such an edge whose jump plan's SKELETON — its
expression with every jump node replaced by that node's branch — still
names the driven coordinate, saying that the read must pass through a
node that is piecewise constant in the coordinate and that a remainder
alone is not one, because with its quotient fixed a remainder still
carries the coordinate's slope. Each refusal SHALL name the edge, the
coordinate and the document.

For a BLOCK — a cycle of the published edges over what they read and
determine, a value an edge itself determines excluded — the refusal SHALL
also cover: a published listing of the edges that is not an order in
which every entry's sources are determined before it runs once each such
cycle is contracted, naming the two edges and the value; a wiring or a
derived coordinate on such a cycle, saying that it carries no jump node
so no selection can switch what it reads; a member of such a cycle that
determines more than one value, saying that what a selection switches is
decided per driven end while a group's ends are bound together; a member
whose driven value is a published computed value rather than a coordinate
of the bank, saying that a block advances its values piece by piece and
only a coordinate the run banks keeps that; and a cycle whose members'
UNCONDITIONAL dependencies — what each still reads with every foldable
selector at its zero branch — are themselves cyclic, saying that such a
cycle is present on every piece and that a dependency inside a cycle is
admitted only where some selection switches it. Each refusal SHALL name
the edge, the class that stated it, and every relation on the cycle.

A bound's free names SHALL be judged after the document's bindings table
has been closed over, so a name reached only through a shared
subexpression is judged as the coordinate it resolves to. A refusal of a
name that the document publishes as a COMPUTED VALUE rather than a bank
coordinate SHALL say so, because such a bound must name the coordinate
that value is computed from.

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

#### Scenario: A bound reading a computed value is refused by name

- **WHEN** a loaded program's bound names a published computed value
  rather than a bank coordinate
- **THEN** loading fails naming that value, saying it is a computed value
  and not a coordinate of the bank, quoting the expression, and nothing
  is rendered

#### Scenario: A bound reading a name the program never declares

- **WHEN** a loaded program's bound names something that is neither the
  bounded coordinate, nor a bank coordinate, nor a computed value
- **THEN** loading fails naming it and saying what such a bound may read

#### Scenario: A self-read law driving more than one coordinate

- **WHEN** a loaded program carries a law edge that determines two values
  and names one of them among the values it reads
- **THEN** loading fails naming that edge and that coordinate, saying a
  law reading its own driven end drives exactly one coordinate, and no
  frame is rendered

#### Scenario: A self-read of a value the bank does not hold

- **WHEN** a loaded program carries a law edge that reads a value it
  determines, and that value is a published computed value rather than a
  bank coordinate
- **THEN** loading fails naming it and saying that a retained value is a
  history and only a coordinate the run banks keeps one

#### Scenario: A read that survives the skeleton

- **WHEN** a loaded program carries a law edge reading a coordinate it
  drives, whose plan's skeleton still names that coordinate
- **THEN** loading fails naming the edge and the coordinate, saying the
  read must pass through a node that is piecewise constant in it and that
  a remainder alone is not one

#### Scenario: A bound reading another coordinate loads

- **WHEN** a loaded program's bound names other bank coordinates, whether
  directly or through the bindings table
- **THEN** the document loads, its run is created at the published rest
  values, and the bound is executed as a constraint

#### Scenario: A cycle no selection can break

- **WHEN** a loaded program's edges carry a cycle one of whose in-cycle
  dependencies survives folding every foldable selector of its member to
  zero
- **THEN** loading fails naming every relation on the cycle and saying
  that a dependency inside a cycle is admitted only where a selection
  switches it, and no frame is rendered

#### Scenario: A wiring on a cycle

- **WHEN** a loaded program's cycle passes through a wiring or a derived
  coordinate
- **THEN** loading fails naming it and the cycle, saying that it carries
  no jump node and that no selection can switch what it reads

#### Scenario: A block member that is not a banked coordinate

- **WHEN** a loaded program's cycle determines a published computed value
- **THEN** loading fails naming that edge and that value, saying that
  only a coordinate the run banks keeps the history a block advances
  piece by piece

#### Scenario: A published listing that is not an order

- **WHEN** a loaded program publishes an edge that reads a value another
  edge determines LATER in the listing, once every cycle is contracted
- **THEN** loading fails naming both edges and the value, rather than
  re-sorting the published edges

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
stated as an expression, a bound READING ANOTHER COORDINATE, a stop
reached by the motion of what a bound reads (one whose coordinate holds
the same value before and after its step), a command retired blocked, a
rate, a run state taken and restored, both instruction forms, a step
carrying both a crossing and a stop, A LAW THAT READS THE COORDINATE IT
DRIVES, a self-read coordinate that HOLDS at its gate over a step in
which an input reaching it goes on moving, a step carrying both a
self-read crossing and a stop, A SWITCHED SOURCE — a published edge on a
cycle that reads a value the cycle determines — a SELECTION CROSSING
inside a step, and a step carrying both a selection crossing and a stop —
so that a narrower corpus copied in
is refused here without anyone running the producer's generator. A bound
reading another coordinate SHALL be recognised through the corpus's own
bindings table, so a corpus whose bound reaches its reads through a
shared subexpression counts as covering it. A block and its selectors
SHALL be re-derived for this assertion FROM THE CORPUS'S OWN DOCUMENTS
and tick logs, by the same reading a consumer of the document makes and
not by asking the run engine, so that the assertion is red on a narrowed
corpus even when the engine is broken; and a crossing SHALL count as a
SELECTION crossing only where its primitive belongs to a selector of the
member that determines its coordinate and to no other jump of that
member, so that a gate which happens to share an operator is not
mistaken for one.

#### Scenario: Every scenario of the corpus replays

- **WHEN** the widget suite replays the committed corpus through the run
  engine
- **THEN** every step of every scenario matches, exactly for discrete
  state and within the stated relative tolerance for floats

#### Scenario: A narrowed corpus is refused

- **WHEN** the committed corpus is replaced by one exercising fewer of the
  stated features
- **THEN** the suite fails naming the feature no longer covered

#### Scenario: A corpus with no bound reading another coordinate is refused

- **WHEN** the committed corpus is replaced by one whose machines declare
  no bound reading another coordinate, or record no stop whose
  coordinate did not move
- **THEN** the suite fails naming the feature no longer covered

#### Scenario: A corpus with no law reading the coordinate it drives is refused

- **WHEN** the committed corpus is replaced by one none of whose machines
  states a law reading the coordinate it drives, or none of whose steps
  holds such a coordinate at its gate while an input reaching it moves on
- **THEN** the suite fails naming the feature no longer covered

#### Scenario: A corpus with no selection is refused

- **WHEN** the committed corpus is replaced by one none of whose machines
  publishes a cycle of edges with a switched source, or none of whose
  steps carries a selection crossing, or none of whose steps carries both
  a selection crossing and a stop
- **THEN** the suite fails naming the feature no longer covered

#### Scenario: A drifted engine is caught, not tolerated

- **WHEN** the engine's arithmetic is changed so one machine's bank
  differs in the last bits beyond the corpus's tolerance
- **THEN** the suite fails naming the scenario, the step and the
  coordinate

### Requirement: The worker executes a law that reads the coordinate it drives

A published law edge MAY name, among the values it READS, one of the
values it DETERMINES. That is a law reading the coordinate it drives, and
the viewer SHALL recognise it from what the document already carries —
the intersection of the edge's read set with its determined set — and
SHALL require no further key for it. A law edge with an empty
intersection SHALL be integrated exactly as it is today, by the same
code, at the same cost.

Such an edge SHALL determine exactly ONE value and SHALL read exactly one
of the values it determines, and that value SHALL be a coordinate of the
bank; a shape that is not so SHALL be refused when the document is
loaded, under the requirement "A program the viewer cannot execute is
refused by name". The plan's SKELETON — its expression with every jump
node replaced by that node's branch — SHALL NOT name the driven
coordinate, and one that does SHALL be refused there too: a read that
survives the skeleton enters the law continuously, and the difference of
two evaluations does not define that.

The viewer SHALL derive, WHEN THE DOCUMENT IS LOADED, which of the plan's
jump nodes DEPEND on the driven coordinate: a node depends on it when
that coordinate is among the free names of the node's published level
quantity, CLOSED OVER the document's own bindings table, or when that
level names the branch placeholder of a node that depends on it. A node
reaching the driven coordinate only through a shared subexpression
depends on it exactly as one naming it directly does. Nothing of this
SHALL be published in the document and the viewer SHALL NOT require any
of it to be.

**Over one step such a law SHALL be integrated PIECE BY PIECE.** The
step's path SHALL first be partitioned by the jump nodes that do NOT
depend on the driven coordinate, exactly as any other law's path is,
their branches read at that partition's midpoints; INSIDE each of its
pieces the dependent nodes SHALL then be walked:

- At the walk's left end the driven coordinate holds a known value: the
  step's committed value at the start, and the value the cuts already
  taken placed it at afterwards.
- Every dependent node's branch SHALL be determined in the plan's
  published order, with the driven coordinate at that retained value and
  every OTHER source at the piece's LEFT END — not at its midpoint,
  because a level naming both the driven coordinate and a source may
  cross inside the piece by the source's motion alone, and the branch
  read past that crossing is not the branch the piece begins under.
- A dependent node whose level sits EXACTLY on a surface at that left end
  SHALL take the branch its primitive gives; if the level then LEAVES the
  surface into another branch's region, that node SHALL be flipped to the
  branch of the region IMMEDIATELY on the side it departs to, at the left
  end, and every branch decided again. If the flipped branch carries the
  level back across as well, the STEP SHALL be refused naming the
  relation, the coordinate and the primitive, and SHALL commit nothing.
- With those branches fixed the substituted law SHALL NOT name the driven
  coordinate, so that coordinate's own value along the piece is one
  ordinary evaluation.
- Each dependent node's level quantity SHALL be followed along the piece
  — through the driven coordinate's own path and through the sources —
  and the piece SHALL be CUT at the FIRST surface any of them reaches
  strictly inside it: SOLVED where the producer published both that level
  and the plan's skeleton as affine, otherwise sampled at the published
  number of sub-intervals and bisected to the published crossing
  tolerance within the published number of rounds. No further tolerance
  SHALL be introduced, and a crossing found within that tolerance of the
  piece's left end SHALL NOT be merged into it — the merging of two near
  cuts belongs to the partition over the independent nodes and SHALL NOT
  be applied in this walk.
- The piece's contribution SHALL be the substituted law's change over it,
  and the next piece SHALL be decided the same way, until the enclosing
  piece is exhausted or the published crossing limit is reached, which
  refuses the step as any other over-cut path is refused.

**After a cut the driven coordinate SHALL be placed AT THE FAR SIDE OF
THE SURFACE, at the nearest representable value.** Where the piece moved
it, the coordinate SHALL be placed at the representable value NEAREST the
surface among those at which the crossing node's level — evaluated with
the driven coordinate at that value and every other source at the
crossing's own fraction — reads the branch on the side the level was
moving TOWARD, judged by the VIEWER'S OWN evaluation of the published
level. Where the piece did NOT move it, the coordinate SHALL stand where
it stood. A step at least one of whose cuts placed the coordinate SHALL
COMMIT the value the walk left it at rather than its starting value plus
the increment; a step none of whose cuts placed it SHALL commit as it
always has. A cut that can place the coordinate nowhere SHALL refuse the
step naming the relation, the coordinate and the primitive, as a broken
invariant of the run rather than a step size that is too coarse, and
SHALL commit nothing.

The driven coordinate's own value along a piece SHALL be computed by
adding to the value it holds at the piece's left end the CHANGE of the
substituted law over the piece — the change taken FIRST — so that a piece
whose substituted law does not move adds a true zero and the coordinate
keeps the exact float it held. Computed in the other association the sum
rounds whenever the law's magnitude is comparable to the coordinate's,
and a coordinate nothing moved would still shift by one unit in the last
place.

Where such a law is a member of a block, every SELECTOR of its plan SHALL
hold, through the whole of this walk, the branch the block read at the
piece's midpoint — in the partition over the independent nodes, in every
branch reading, in every probe, in every cut and in the far-side landing
— and that node's crossings SHALL NOT be located again inside the piece.

A coordinate held at its gate SHALL therefore read the same branch on
every later step, whatever its sources do, SHALL be unmoved by a further
step in the same direction BIT FOR BIT, and SHALL survive a run state
taken and restored unchanged.

A crossing located by this walk SHALL be recorded as a CROSSING — the
relation, the coordinate, the primitive, the surface level and the
fraction of the step — and never as a stop.

A declared bound on the driven coordinate SHALL still stop it exactly as
it stops any other coordinate — located over this same partition and
committed AT the bound — and where a step's cut has placed the
coordinate and a bound of the same coordinate is reached in the same
segment, the bound SHALL win: a physical bound is a bound of the
coordinate itself.

#### Scenario: A dial clears to its gap and the ring sweeps on

- **WHEN** a document whose law gates a dial on the dial's own retained
  angle, disengaged over a band about every full turn, is run with the
  dial resting part way and the ring swept far enough to carry it to the
  band
- **THEN** the dial ends within the band, at a value that reads
  disengaged under the viewer's own evaluation of the published level,
  the ring completes its whole travel, and the crossing appears in the
  crossing record and not in the stop record

#### Scenario: Sweeping an already-cleared dial moves it by nothing

- **WHEN** the same machine is swept again, and again

- **THEN** the dial holds the same value bit for bit after each sweep,
  every request completes, and no stop is recorded

#### Scenario: A branch is read from the retained value, not the midpoint

- **WHEN** a law's level quantity names both the driven coordinate and a
  moving source, so that it crosses inside a piece by the source's motion
  alone
- **THEN** the piece is integrated under the branch its LEFT END gives
  and cut where the level reaches the surface, rather than under the
  branch a midpoint reading would have chosen

#### Scenario: A coordinate standing exactly on a surface is not driven through it

- **WHEN** the driven coordinate stands exactly at the value its own
  gate's surface sits on — the value a previous cut placed it at — and
  the sources are moved, first so as to carry the level into the engaged
  region and then so as to carry it away
- **THEN** it holds in the first case and moves in the second, and in
  neither is it carried through the band by a piece integrated under the
  wrong branch

#### Scenario: A level that will not settle refuses the step

- **WHEN** a dependent node sits on a surface at a piece's left end and
  each of the two branches carries the level back across it
- **THEN** the step is refused naming the relation, the coordinate and
  the primitive, the bank, the step count and the pose stand as they
  were, and the commands that moved are retired reporting that the step
  did not happen

#### Scenario: Several coordinates clear independently from one input

- **WHEN** one input drives several coordinates, each by its own law
  reading its own driven end, and the input is moved far enough to reach
  some of them and not others
- **THEN** each reached coordinate ends at its own band, each unreached
  one is untouched, one coordinate's disengagement cuts only its own
  path, and the input's command completes with its whole travel admitted

#### Scenario: A declared bound on the same coordinate still stops it

- **WHEN** the coordinate a self-read law drives declares a bound, and
  one step carries the coordinate through a cut of its own gate and on
  to that bound
- **THEN** the coordinate is committed at the bound exactly, the stop
  is recorded in the stop record naming it, the crossing is recorded
  in the crossing record at its fraction of the step, and the inputs
  that pushed it are retired blocked

#### Scenario: A coordinate no piece moved keeps its exact float

- **WHEN** a step moves a source of a self-read law whose substituted law
  does not change over the piece, and the driven coordinate stands at a
  value of a magnitude comparable to that law's
- **THEN** the coordinate holds the float it held, bit for bit, rather
  than shifting by one unit in the last place

#### Scenario: A law that reads nothing of its own is untouched

- **WHEN** a document whose every law edge reads only values it does not
  determine is run
- **THEN** every step is the partition, the midpoint branches and the sum
  it always was, and the run takes the same path at the same cost
