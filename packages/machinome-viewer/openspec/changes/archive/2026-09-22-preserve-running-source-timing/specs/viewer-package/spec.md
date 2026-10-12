## MODIFIED Requirements

### Requirement: The step reproduces the producer's own integration

For each step the viewer SHALL take the movement each active command
admits for that step — a pure function of the number of steps since the
command started, so a replayed run admits exactly the same travel — and
propagate it over the edges in the published order, producing one
increment per determined value and committing them together. Where the
published edges carry a cycle, the entries propagated over are the edges
with each such cycle contracted to ONE entry, ordered under the
requirement "The worker orders a block per piece"; a program with no
cycle retains its published propagation order while preserving determined
source timing as specified below.

The path SHALL follow each source at the same fraction of the request:
commanded motion for inputs, constant motion for held values, and determined
motion for driven values. Driven paths SHALL retain dwell, kink, crossing and
landing timing in ordinary chains and selected blocks, not interpolate their
net increments. Restriction SHALL preserve that timing. Physical results SHALL
agree between a bulk request and its portions within the published agreement
window, with exact statuses and discrete readings away from threshold
neighborhoods. Additional stations that do not influence an earlier carry SHALL
NOT alter it. Queries SHALL be pure and caches SHALL NOT outlive a propagation.

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
  affine in its sources SHALL be solved only where those source paths make
  the level affine in request fraction; one the viewer finds
  PIECEWISE AFFINE under the requirement "A piecewise-affine quantity is
  cut at its own kinks" SHALL have the piece SUB-DIVIDED at that
  quantity's own kinks and every surface of each sub-piece solved the
  same way; any other SHALL be sampled, bracketed and bisected under the
  published subdivision, rounding and tolerance limits.
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
stretch's determined path, shared with the propagation that will commit the
segment. Where a path is unavailable, the bound SHALL use fresh prefix replay
with each admission scaled by the fraction, never a replacement endpoint chord. The CONSTRAINT LEVEL of
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
sub-intervals along those same paths, and the
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
the constraint level from the inside to the outside end of the located
contact bracket. Both sightings SHALL replay from the original stretch origin,
with the own-coordinate argument frozen at tick start. A later free endpoint
SHALL NOT erase the push at the first contact. An input
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

#### Scenario: A later free revolution does not erase first contact

- **WHEN** a requested crank movement meets a periodic moving-read stop before
  returning to equal or lower constraint level at its final endpoint
- **THEN** it stops at the first located contact and reports blocked with only
  admitted travel, leaving independent, relieving and disengaged inputs free
- **AND** retry, relief and snapshot replay preserve that stopped state without
  remembering the rejected remainder

### Requirement: The worker orders a block per piece

A published program's dependency graph — edge A before edge B when B
reads a value A determines, with a value an edge itself determines
EXCLUDED — MAY carry a cycle. Every nontrivial strongly connected
component of it is a **BLOCK**, and the viewer SHALL recognise a block
from what the document already carries, requiring no further key for it.
A program with no such component SHALL preserve source timing too. Exact affine
propagation SHALL retain its arithmetic fast path; ordinary endpoint
approximations that lose dwell or landing timing SHALL be corrected.

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
  machinery that already governs it. Every determined source SHALL follow
  its actual motion restricted to this piece, retaining dwell and landing
  timing, whether determined outside or inside the block. A switched-out
  in-block source this piece has not determined SHALL hold its value at the
  piece's start, since the forced branch removes its influence.
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

**A declared bound SHALL be located along the same determined path.** Where
that path is certified piecewise affine, each segment SHALL be solved; otherwise
it SHALL use the published bounded search. A member's published affinity alone
SHALL NOT certify its block's whole path.

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

#### Scenario: A stop on a block's value follows its actual path

- **WHEN** a step drives a value a block determines into a declared bound
- **THEN** the fraction at which it reaches the bound follows its determined
  path, solved per certified affine segment or otherwise searched, and the
  value is committed exactly at its bound

#### Scenario: An inactive selection blocks nothing

- **WHEN** a value a block determines reaches a declared bound while an
  input that reaches it only through a selection that is currently
  inactive is running
- **THEN** that input is not blocked and its command completes its whole
  travel, while the input that does push the value retires blocked

#### Scenario: An ordinary frozen carry has the same physical timing

- **WHEN** the existing FixedZero ordinary carry and ShiftedCarry at shift 0
  receive crank 0..4 whole and in sixteen portions
- **THEN** both finish with carry.travel 1 and higher.turn 3.5, completed
  status and full admitted travel, rather than spreading the lever's stroke
  over the whole request

## ADDED Requirements

### Requirement: Source-timed running programs are compatible by declaration

The viewer SHALL accept producer document version 11 as a running program with
source-timed semantics, including well-formed optional Play and time-drive
declarations. It SHALL validate those features by content and refuse malformed
mappings or clock reads without their required admission mapping before ticking.
Version 11 SHALL NOT be treated as a clocked program. This extends the loader's
supported document list without adding a new document key.

Legacy running documents SHALL remain loadable and receive corrected source
timing too, not a separately preserved endpoint-approximation algorithm. Posed,
looping, clocked and clearance-aware Play behavior SHALL remain unchanged
except for explicitly measured timing corrections in supported running chains.

#### Scenario: Corrected exports cannot silently enter an old viewer

- **WHEN** Curta is re-exported by the corrected producer as version 11 and
  offered to an old viewer whose supported versions end at 10
- **THEN** the old viewer refuses the version before operation rather than
  silently executing the old carry arithmetic

#### Scenario: Driver-only and autonomous documents load

- **WHEN** valid version-11 driver-only and time-driven programs are loaded
- **THEN** both run, while a missing mapping for a clock-reading edge is refused

### Requirement: Curta source timing is pinned by producer evidence

The viewer suite SHALL replay producer-generated timing fixtures without
importing the framework or project. It SHALL compare full banks, statuses,
admitted travel, crossings and stops under the producer's published float and
discrete agreement rules. Fixtures SHALL retain producer content hashes and
the unchanged physical oracle. The existing corpus SHALL remain a control;
an expectation change requires recorded physical evidence, not regeneration
solely to make a failure pass.

#### Scenario: The complete diagnostic result bank preserves its carry

- **WHEN** unchanged six-, seven- and eleven-station Curta diagnostic exports,
  including the constrained full bank, receive digit 0, height 9, crank 90,
  then one bulk crank 180 request
- **THEN** all complete at crank 180, ones 724, tens 704 and first lever 0,
  and the full bank agrees with partitioned replay from the same snapshot

#### Scenario: A dwelling and curved source keep their timing

- **WHEN** producer fixtures include a landed source, a piecewise or curved
  upstream law, and an irrelevant later selector
- **THEN** the viewer reproduces the producer's physical gate times, including
  a landing exactly on an inherited breakpoint recorded once

#### Scenario: Browser transports execute the same carry

- **WHEN** the diagnostic export is operated in a real browser through worker
  and in-thread fallback, then restored and replayed
- **THEN** both match the producer bank and command outcomes and the rendered
  parts follow the committed bank, without claiming whole-machine acceptance
