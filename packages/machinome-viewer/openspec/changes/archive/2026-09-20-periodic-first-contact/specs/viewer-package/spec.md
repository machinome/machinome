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
  endpoint values solved rather than searched; one the viewer finds
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
inside a step, a step carrying both a selection crossing and a stop, and
an IN-BLOCK GATE CROSSING located STRICTLY INSIDE a step — a crossing
recorded under a member of a block that only a jump reading a value
ANOTHER member of that block determines can account for, the member's own
driven value excluded — and a STOP LOCATED STRICTLY INSIDE a step ON A
KINKED DETERMINER — a coordinate whose determining law carries no jump
plan at all and whose published expression, closed over the corpus's
bindings table, calls one of the CONTINUOUS SELECTIONS `abs`, `min` or
`max`, so that its value along a step is piecewise affine rather than
affine and a consumer dividing once over the whole step would place the
stop where the coordinate never was — so that a narrower corpus copied in
is refused here without anyone running the producer's generator. A bound
reading another coordinate SHALL be recognised through the corpus's own
bindings table, so a corpus whose bound reaches its reads through a
shared subexpression counts as covering it. A block and its selectors
SHALL be re-derived for this assertion FROM THE CORPUS'S OWN DOCUMENTS
and tick logs, by the same reading a consumer of the document makes and
not by asking the run engine, so that the assertion is red on a narrowed
corpus even when the engine is broken; a KINKED DETERMINER SHALL be
re-derived the same way and from the same two sources — the absent plan
and the expression closed over the bindings table — and never by asking
the run engine what it classified; and a crossing SHALL count as a
SELECTION crossing only where its primitive belongs to a selector of the
member that determines its coordinate and to no other jump of that
member, so that a gate which happens to share an operator is not
mistaken for one. An in-block gate crossing SHALL be recognised from the
crossing's own primitive and the preceding step's committed values: the
jumps of that member carrying the primitive, their level quantities closed
over the corpus's bindings table, SHALL be separated into those reaching a
value the block determines other than the member's own and those reaching
none of the block's values, and the crossing SHALL count only where one of
the first kind reads a value that MOVED across the step and no one of the
second kind reads a value that moved or a value the step does not carry.
A step with no predecessor SHALL be skipped, having nothing to compare
against.

The committed corpus SHALL DISCRIMINATE the order in which a block's
members are run, because a document publishes those members as a listing
and not as an execution order: replaying a named scenario through the
shipped engine with the block's members run in the order the document
publishes them, instead of ordered for each piece of the step, SHALL
disagree with the corpus by more than the stated tolerance on the
committed values of at least one step, while the same replay with the
members ordered per piece reproduces them. The suite SHALL assert this
directly, rather than inferring it from the width above.

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

#### Scenario: A corpus with no in-block gate crossing is refused

- **WHEN** the committed corpus is replaced by one none of whose steps
  records a crossing, strictly inside the step, under a member of a block
  that only a gate on a value another member of that block determines can
  account for
- **THEN** the suite fails naming the feature no longer covered

#### Scenario: An engine that runs a block in the published order is caught

- **WHEN** a corpus scenario carrying a block is replayed through the run
  engine with the block's members run in the order the document publishes
  them, instead of ordered for each piece of the step
- **THEN** the replay disagrees with the corpus by more than the stated
  tolerance on the committed values of at least one step, while the same
  replay with the members ordered per piece reproduces them

#### Scenario: A corpus with no stop on a kinked determiner is refused

- **WHEN** the committed corpus is replaced by one none of whose steps
  records a stop, strictly inside the step, on a coordinate whose
  determining law carries no jump plan and whose expression calls a
  continuous selection
- **THEN** the suite fails naming the feature no longer covered

#### Scenario: Periodic first-contact coverage cannot disappear

- **WHEN** the corpus lacks a long periodic request with an actual blocked stop
  before a free endpoint, or lacks its snapshot/restore replay
- **THEN** the coverage assertion fails naming periodic first contact
- **AND** the old endpoint-only attribution fails the intact corpus scenario


