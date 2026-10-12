## ADDED Requirements

### Requirement: A piecewise-affine quantity is cut at its own kinks

Following a quantity along a step's path, the viewer decides between
SOLVING it — determining it everywhere on a stretch from that stretch's
two endpoint values — and SEARCHING it, by sampling the published number
of sub-intervals and bisecting. The producer publishes, per driven end of
a law and per jump level, whether that quantity is AFFINE in its sources;
that flag is TWO-VALUED and says nothing about a quantity that is not
affine.

A quantity built over the CONTINUOUS SELECTIONS of the expression
vocabulary — `abs`, `min` and `max`, each of which returns one of its
operands exactly and is continuous where the operands meet — is PIECEWISE
AFFINE: affine on each stretch between the points where it changes which
operand it returns. The viewer SHALL recognise such a quantity FROM THE
PUBLISHED EXPRESSION ITSELF and SHALL solve it on those stretches rather
than search it. No document field is read for this, no document version
and no viewer API version moves for it, and nothing an author writes, no
host call, no option and no tolerance selects it.

**The classification SHALL be structural, conservative, and decided per
published quantity rather than per step.** A number and a jump node's
branch placeholder are CONSTANT; a source name is AFFINE; a name the
document's bindings table defines takes the shape of that table's own
expression; a unary minus, a sum, a difference, a product with a constant
operand and a division by a constant take the shape of their moving
operand and are KINKED exactly when it is; one of the three continuous
selections over operands that are each constant, affine or kinked is
KINKED; everything else — another call, a power, a product of two moving
operands, a moving divisor, a comparison — is UNCLASSIFIED and SHALL go
on being searched. A continuous selection over a CURVED operand SHALL
therefore stay unclassified, even where one of its pieces happens to be
straight.

**The viewer's classification SHALL agree with the flag the producer
publishes.** A quantity the viewer finds constant or affine SHALL be one
the producer published as affine, and a quantity the viewer finds kinked
or unclassified SHALL be one the producer published as not affine. The
viewer SHALL NOT weaken what the producer published: a quantity published
affine SHALL be solved over the whole stretch as it already was.

**A kink's own breakpoints SHALL be SOLVED, never sampled.** A continuous
selection has a level quantity of its own — the argument of `abs`, and
the difference of the two operands of `min` and `max` — whose single
surface, at zero, is where it changes which operand it returns. Over a
stretch those breakpoints SHALL be located by taking the kinks in the
expression's own postorder, so that a kink nested inside another's level
is cut first; by evaluating each kink's level at the two ends of each
sub-interval the earlier kinks have already produced, where that level is
affine in the fraction and its zero is therefore one division; by keeping
only a zero that lies strictly inside its sub-interval and strictly
between the two end values; and by folding the result into the
sub-division under the SAME crossing tolerance two crossings are folded
under. No sampling, no bisection and NO FURTHER TOLERANCE SHALL be
introduced. A level that does not move over a sub-interval reaches
nothing inside it.

**A kink breakpoint SHALL NOT be a crossing.** The quantity is continuous
there. A breakpoint SHALL NOT be recorded among a step's crossings, SHALL
NOT enter any partition an increment is summed over, SHALL NOT place a
coordinate at the far side of a surface, and SHALL NOT count toward the
published crossing maximum. It exists only as a sub-division inside a
solve, and this is what keeps every answer that did not sit on a
reclassified quantity bit-identical.

**A stop SHALL be solved on a kinked determiner.** Where a coordinate's
determining law is piecewise affine, the fraction of the stretch at which
it reaches a declared bound SHALL be located by bracketing the bound
between two consecutive breakpoints and dividing, and not by sampling.
Where such a law carries a jump plan, the breakpoints are the union of
that plan's own partition and the skeleton's kinks, the kinks located
inside each piece of the partition with that piece's branch readings
substituted, because a branch placeholder is constant only within its own
piece. Where such a law carries NO jump plan at all — the shape that
otherwise divides once over the whole step and so reports a stop where
the coordinate never was — the breakpoints are its own kinks over the
step as one piece. Where a kinked law reaches no kink over a step, there
are no breakpoints, the path IS affine over the whole step, and the
single division SHALL be taken exactly as it is for an affine law.

A stop on a coordinate a BLOCK determines SHALL still be searched: a
block has no single published expression until a branch vector is fixed,
and the order its members run in may differ from piece to piece. This
requirement does not lift that, and a bound that READS OTHER COORDINATES
SHALL go on being examined exactly as the requirement "A declared bound
may read other coordinates" states.

Nothing else SHALL move. Every banked value, every recorded crossing,
every landing, every stop, every command outcome and every refusal of a
machine none of whose followed quantities is reclassified SHALL be the
value it was, bit for bit, and the count of points such a machine
evaluates SHALL NOT change.

#### Scenario: A stop on a kinked determiner with no jump plan is solved

- **WHEN** a coordinate's only determining law carries no jump node at
  all, its expression clamps a source into a window, a declared bound
  lies on the sloped piece and the step's path starts on the flat one
- **THEN** the stop is located at the fraction the bracketing division
  gives over the piece the bound lies in, which is the producer's own
  recorded fraction, and not at the fraction a single division over the
  whole step would give

#### Scenario: A kinked level's crossing is solved rather than searched

- **WHEN** a jump node's level quantity is built over a continuous
  selection and the step's path crosses one of that node's surfaces
- **THEN** the crossing is located by solving on the sub-interval between
  the level's own kinks, and the surface lying exactly on an interior
  breakpoint is located once and not twice

#### Scenario: A kink breakpoint is not recorded as a crossing

- **WHEN** a step's path passes a breakpoint of a kinked quantity
- **THEN** no crossing is recorded there, no coordinate is placed at a
  far side, the increment is summed over the same pieces as before, and
  the breakpoint counts toward no published limit

#### Scenario: A curved quantity is still searched

- **WHEN** a followed quantity is a continuous selection over a curved
  operand, a product of two moving operands, or a quantity divided by a
  moving one
- **THEN** it is sampled and bisected exactly as before, at the same
  sub-interval count, the same tolerance and the same number of rounds

#### Scenario: A machine with no kink pays nothing

- **WHEN** a machine none of whose followed quantities is piecewise
  affine is stepped
- **THEN** every value it commits is unchanged bit for bit and the number
  of subexpression resolutions it performs per step is unchanged exactly

#### Scenario: The classification agrees with the published flag

- **WHEN** every law's driven end and every jump level of a published
  document is classified by the viewer
- **THEN** the quantities it finds constant or affine are exactly those
  the document publishes as affine, and no quantity it finds kinked or
  unclassified is published as affine

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
  and the plan's skeleton as affine; solved on SUB-INTERVALS where
  neither is curved and at least one is PIECEWISE AFFINE under the
  requirement "A piecewise-affine quantity is cut at its own kinks", the
  piece being cut first at the SKELETON's kinks — which are what make the
  driven coordinate's own path affine at all — and each of those cut
  again at the LEVEL's own, which ride that path and SHALL therefore be
  located inside one skeleton sub-piece with the driven coordinate read
  by interpolation between that sub-piece's two ends; otherwise sampled
  at the published number of sub-intervals and bisected to the published
  crossing tolerance within the published number of rounds. No further tolerance
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
