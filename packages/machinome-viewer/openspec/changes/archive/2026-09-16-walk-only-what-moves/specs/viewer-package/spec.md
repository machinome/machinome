## ADDED Requirements

### Requirement: Only what moves along a step's path is walked

Executing a published program, the viewer FOLLOWS a quantity along a
step's path: it evaluates one published expression at many points of that
path — the sub-intervals of a sampled search and the rounds of its
bisection, the two ends of each piece of a solve, the midpoint of each
piece of a partition, the points of a self-read walk. Over ONE path, with
ONE branch reading, the value of the part of that expression which reads
no name the step MOVES cannot change. That part SHALL be computed ONCE
for the piece and read back at every point of it, and only the remainder
SHALL be evaluated per point.

Which names MOVE along a path SHALL be the run's own statement and never
inferred from sampling, from comparing two evaluations, or from a
tolerance:

- a source whose increment over the step is non-zero MOVES;
- a jump node's BRANCH, a constant of its piece by construction, STANDS;
- the coordinate a law READS AND DRIVES moves for a quantity the walk
  hands its value to at every point, and stands for one that by refusal
  does not name it at all;
- a name the document's bindings table defines SHALL be followed INTO
  that table's own expression and SHALL move exactly when that expression
  does, so a quantity reaching a moving source only through a shared
  subexpression moves exactly as one naming it directly does.

The arithmetic SHALL be unchanged: the same nodes, in the same order,
through the same operators and the same function table, on the same
operand values. A quantity's value at any point of a path SHALL therefore
be the SAME FLOAT, bit for bit, that evaluating its whole expression at
that point gives. This requirement changes what the viewer COMPUTES TWICE
and SHALL change no crossing, no landing, no branch reading, no
increment, no stop, no refusal and no committed value.

A quantity's standing part SHALL belong to ONE piece. A piece SHALL be
identified so that no value computed under one piece's branches can be
read back under another's, and nothing decided for a step SHALL outlive
that step: there SHALL be no cache across steps and therefore no
condition under which one goes stale.

Resolving a QUALIFIED id while following a path SHALL read the run's bank
by that id whole. This is the same number the whole-expression walk
reaches by member access at every segment, because a program whose
identifiers could make the two disagree — one id a strict prefix of
another — is already refused when the document is loaded, under the
requirement "A program the viewer cannot execute is refused by name".

The saving SHALL be structural and unconditional. No declaration, option,
tolerance, cache size or sampling count SHALL be introduced; nothing an
author writes and no host call SHALL select it; no document field SHALL
be read for it and no document version or viewer API version SHALL move
for it. A machine whose laws are small, or whose followed quantities move
entirely, SHALL be no slower for it than the cost of deciding, once per
followed quantity per step, which of its nodes move.

The COUNT of points a step evaluates SHALL NOT change: the same search,
the same sub-interval count, the same tolerances and the same rounds.
What falls is the work inside one point, and the widget SHALL report that
work to its own tests through the subexpression-resolution probe it
already exposes, so the fall is asserted as work performed and never as
elapsed time.

#### Scenario: A searched crossing evaluates only the moving part of the law

- **WHEN** a running document's law reads the coordinate it drives
  through a skeleton the producer did not publish as affine, and that law
  also reads sibling coordinates the step does not move, so that most of
  its expression stands
- **THEN** the crossing is located by the same sampled search, at the
  same sub-interval count, the same tolerance and the same number of
  rounds, and the node visits the step performs inside that search fall
  by the share of the expression that stands

#### Scenario: Every value the machine commits is unchanged

- **WHEN** such a machine is stepped for dozens of steps, idle and moving
- **THEN** every banked coordinate, every recorded crossing, every
  landing and every stop is the value it was before this requirement, bit
  for bit, and every scenario of the conformance corpus replays

#### Scenario: A quantity that moves entirely is evaluated whole

- **WHEN** a followed quantity reads only names the step moves, so that
  nothing in it stands
- **THEN** every point evaluates the whole expression exactly as before,
  and the step pays the decision of which nodes move once for that
  quantity rather than once per point

#### Scenario: A branch reading holds for its own piece and no other

- **WHEN** a step's path is cut into several pieces and a jump node reads
  a different branch on each
- **THEN** the standing part is computed again for each piece under that
  piece's own branches, and no value computed under one piece's branches
  is read back under another's

#### Scenario: A qualified id is read whole

- **WHEN** a followed quantity names a coordinate whose id has several
  dotted segments
- **THEN** it reads the value the bank holds under that whole id, which
  is the value the whole-expression walk reaches by member access, and no
  nested scope is built for that point
