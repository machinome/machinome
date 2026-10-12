## MODIFIED Requirements

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
