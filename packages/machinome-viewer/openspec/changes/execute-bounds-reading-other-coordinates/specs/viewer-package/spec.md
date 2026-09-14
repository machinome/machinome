## ADDED Requirements

### Requirement: A declared bound may read other coordinates

A span the document publishes as an expression MAY name, beside the
bounded coordinate's own identifier, other coordinates of the program's
bank. The viewer SHALL read such a bound as a CONSTRAINT between the
bounded coordinate and what it reads, and SHALL derive everything it
needs to execute one WHEN THE DOCUMENT IS LOADED, from what the document
already publishes — the producer publishes no further table for it.

For each side of each span whose expression names a coordinate other
than the bounded one, the viewer SHALL derive:

- its READS: the free names of that expression, CLOSED OVER the
  document's own bindings table, minus the bounded coordinate's own
  identifier. A bound whose expression reaches a coordinate only through
  a shared subexpression SHALL read that coordinate, exactly as one
  naming it directly does; a bound whose expression never names the
  bounded coordinate is well formed, because the test is containment and
  not equality;
- its SUB-PROGRAM: the published edges that determine the bounded
  coordinate and every read, and everything those need, in the program's
  own published order, a check edge never among them;
- its CANDIDATES: the input identifiers the program's own reaching-input
  table gives for the bounded coordinate or for any read, without
  repetition and in a determinate order.

None of the three SHALL be published in the document, and the viewer
SHALL NOT require any of them to be: each is a projection of the
coordinates, the edges and the reaching-input table the document already
carries.

A span side that is `null` or a number, and one whose expression names
the bounded coordinate alone, SHALL NOT become a constraint: their
meaning, their code path and their cost SHALL be exactly what they are
today.

#### Scenario: A bound reaching a coordinate through a shared subexpression reads it

- **WHEN** a loaded document's bound names only entries of the bindings
  table, and those entries resolve to other bank coordinates
- **THEN** the bound's reads are those coordinates, and a step in which
  one of them moves is measured along the step's path rather than
  against a number taken at its start

#### Scenario: A bound naming no coordinate but its own is not a constraint

- **WHEN** a loaded document declares a bound whose expression names the
  bounded coordinate alone
- **THEN** it is evaluated once per step from the committed bank, the
  coordinate is committed exactly at it when it stops there, and nothing
  about the step differs from before this capability existed

#### Scenario: The sub-program is the published edges, in the published order

- **WHEN** a bound reads coordinates determined by some of the
  program's edges and not others
- **THEN** the constraint's sub-program holds exactly the edges
  determining the bounded coordinate, the reads and what those need, in
  the document's own edge order

## MODIFIED Requirements

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
be stopped. A bound that reads the bounded coordinate alone SHALL be
evaluated once per step from the committed bank, so every segment of one
step is measured against the same number.

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
limit, a law that cannot be integrated over the step's path, a stop that
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

#### Scenario: A bound reading another coordinate loads

- **WHEN** a loaded program's bound names other bank coordinates, whether
  directly or through the bindings table
- **THEN** the document loads, its run is created at the published rest
  values, and the bound is executed as a constraint

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
rate, a run state taken and restored, both instruction forms, and a step
carrying both a crossing and a stop — so that a narrower corpus copied in
is refused here without anyone running the producer's generator. A bound
reading another coordinate SHALL be recognised through the corpus's own
bindings table, so a corpus whose bound reaches its reads through a
shared subexpression counts as covering it.

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

#### Scenario: A drifted engine is caught, not tolerated

- **WHEN** the engine's arithmetic is changed so one machine's bank
  differs in the last bits beyond the corpus's tolerance
- **THEN** the suite fails naming the scenario, the step and the
  coordinate
