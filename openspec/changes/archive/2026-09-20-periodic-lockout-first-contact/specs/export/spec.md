## MODIFIED Requirements

### Requirement: The two runtimes share a conformance corpus

The framework SHALL provide a generator that writes a JSON conformance
fixture from its own run, covering a set of small running roots, and the
framework's own suite SHALL replay that committed fixture and reproduce it.
The fixture is the contract between the framework's run and any other
runtime executing a published program: every expected value in it SHALL be
a value the framework's run PRODUCED, never a value recomputed a second way,
so a disagreement means the other runtime drifted.

The fixture SHALL carry, per machine: its name, its `dt`, the published
document's program-bearing keys — `format`, `version`, `drivers`,
`instructions`, `bindings` and `program` — verbatim; a SCRIPT of commands
(moves by a travel or to a value, rates, instruction triggers, a snapshot
and a restore) each naming the tick it is applied before and the handle its
outcomes are reported under; and EVERY TICK of the run, oldest first, each
carrying the whole committed bank, the crossings located in that tick, the
stops located in that tick, and every command created so far with its status
and the travel it has admitted. A sampled fixture SHALL NOT be accepted: a
divergence that heals between two samples is a divergence.

Agreement SHALL be EXACT for discrete state — tick numbers, command
statuses, coordinate, relation, primitive, bound and input names, crossing
surface levels, and the ORDER of every list — and within a stated RELATIVE
tolerance for floats: the bank's values, a crossing's or stop's fraction of
the tick, a stop's evaluated bound and a command's admitted travel. That
tolerance SHALL be the run's own agreement window, the same number the
document publishes as `program.limits.agreement`, because a consumer inside
it cannot manufacture a disagreement the run itself would not.

The generator SHALL REFUSE to write a corpus that does not exercise each of:
the five discontinuous primitives, a multi-source law, a stop located inside
a tick, a bound stated as an expression, a bound reading another
coordinate, a stop reached by the motion of what a bound reads — one whose
coordinate holds the same value before and after its tick — a command
retired `blocked`, a rate, a snapshot and restore, an instruction in each
of its two forms, a tick carrying both a crossing and a stop, a law that
READS THE COORDINATE IT DRIVES — one whose driven coordinate holds at its
gate while the input that reached it goes on moving — a tick in which a
self-read crossing and a stop both fall, a SWITCHED SOURCE — a law edge
reading a coordinate another member of its own block determines — a
SELECTION CROSSING located inside a tick, a tick in which a selection
crossing and a stop both fall, and an IN-BLOCK GATE CROSSING located
STRICTLY INSIDE a tick — a crossing recorded under a block member that
only a jump reading a coordinate ANOTHER member of that block determines
can account for, the member's own driven end excluded. The framework's
suite SHALL test that refusal directly, so the corpus's width is visible
without running the generator. Required coverage SHALL also include a
periodic moving-read constraint that stops a request at an interior contact
even though its untruncated endpoint would have returned to an open window.
That case SHALL expose the admitted travel, stopped admission, stop fraction
and retained coordinates, and SHALL include replay from a snapshot.

The corpus SHALL DISCRIMINATE the order in which a block's members are
run, because a document publishes a block's members as a listing and not
as an execution order: a consumer that ran them in the order they are
published, rather than ordering each piece of the tick for itself, SHALL
disagree with the corpus by more than the stated tolerance on the bank of
at least one tick. A framework test SHALL assert this directly, on a
named scenario, rather than inferring it from the feature list.

A framework test SHALL assert that each fixture machine's REAL published
document reproduces the fixture's own program-bearing keys, so the fixture
cannot drift from the producer it claims to come from.

#### Scenario: The framework reproduces its own corpus

- **WHEN** the committed fixture is replayed through the framework's run,
  machine by machine, applying each script entry before the tick it names
- **THEN** every tick's bank, crossings, stops and command outcomes match the
  fixture, exactly for discrete state and within the stated relative
  tolerance for floats

#### Scenario: The corpus carries the document it was run against

- **WHEN** a fixture machine's document is published afresh
- **THEN** its `program`, `drivers`, `instructions` and `bindings` equal the
  fixture's copy

#### Scenario: A corpus missing a primitive is refused

- **WHEN** the generator is asked to write a corpus whose machines contain
  no `%` law
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: Every tick is present

- **WHEN** a fixture machine runs for forty ticks
- **THEN** the fixture lists forty tick entries, in order, with no gaps

#### Scenario: A corpus missing a bound reading another coordinate is refused

- **WHEN** the generator is asked to write a corpus whose machines declare
  no bound reading another coordinate, or record no stop whose coordinate
  did not move
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing a law that reads its own driven coordinate is refused

- **WHEN** the generator is asked to write a corpus none of whose machines
  states a law reading the coordinate it drives, or none of whose ticks
  holds such a coordinate at its gate while the input reaching it moves on
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing a switched source is refused

- **WHEN** the generator is asked to write a corpus none of whose
  machines carries a block, or none of whose ticks locates a selection
  crossing
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing an in-block gate crossing is refused

- **WHEN** the generator is asked to write a corpus none of whose ticks
  records a crossing, strictly inside the tick, under a block member that
  only a gate on a coordinate another member of that block determines can
  account for
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: The corpus catches a consumer that runs a block in the published order

- **WHEN** a corpus scenario carrying a block is replayed through the
  framework's run with the block's members run in the order the document
  publishes them, instead of ordered for each piece of the tick
- **THEN** the replay disagrees with the corpus by more than the stated
  tolerance on the bank of at least one tick, while the same replay with
  the members ordered per piece reproduces the corpus

#### Scenario: A corpus missing the periodic first-contact regression is refused

- **WHEN** corpus generation omits the periodic moving-read contact case
  whose requested endpoint is free again, or its replay evidence
- **THEN** generation refuses naming the missing coverage rather than
  publishing a corpus that cannot distinguish the endpoint-only pushing bug

#### Scenario: The corpus discriminates endpoint-only pushing

- **WHEN** the periodic contact scenario is replayed using the old
  whole-request endpoint comparison to select pushing admissions
- **THEN** replay fails or disagrees with the committed expected result;
  the corrected producer reproduces the full case and its snapshot replay
