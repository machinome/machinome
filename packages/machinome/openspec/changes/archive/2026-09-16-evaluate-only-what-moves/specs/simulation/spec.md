## ADDED Requirements

### Requirement: Only what moves along a tick's path is evaluated

Under a running root the engine follows a quantity along a tick's path by
evaluating its expression at many points of that path: the sub-intervals
of a sampled search, the two ends of each piece of a solve, the midpoint
of each piece of a partition. Over ONE path, with ONE branch reading, the
value of a part of that expression CANNOT change — the part that reads no
source the tick moves. That part SHALL be computed ONCE and read back at
every point, and only the remainder SHALL be evaluated per point.

Which names MOVE along a path SHALL be the run's own statement and never
inferred from sampling or from a tolerance:

- a source whose increment over the tick is non-zero MOVES;
- a jump node's BRANCH, which is a constant of the piece by construction,
  STANDS;
- the coordinate a law READS AND DRIVES moves for a quantity the walk
  hands its value to per point, and stands for one that by refusal does
  not name it at all.

The arithmetic SHALL be unchanged: the same nodes, in the same order,
through the same operators, on the same operand values. A quantity's
value at any point of a path SHALL therefore be the SAME FLOAT, bit for
bit, that evaluating its whole expression at that point gives. This
requirement changes what the run COMPUTES TWICE and SHALL change no
crossing, no landing, no branch reading, no increment, no stop, no
refusal and no committed value.

The saving SHALL be structural and unconditional. No declaration, option,
tolerance, cache size or sampling count SHALL be introduced, and nothing
an author writes SHALL select it. A machine whose laws are small or whose
followed quantities move entirely SHALL be no slower for it than the cost
of deciding, once per quantity per tick, which of its nodes move.

The COUNT of evaluations a tick pays SHALL NOT change: the same points
are evaluated, and a point evaluated through a followed path SHALL be
counted as one evaluation by any probe that counts them, so the
evaluation counts other requirements pin stand unmoved. What falls is the
work inside one evaluation, and a probe that reports the run's cost SHALL
be able to report it in the unit that moves.

#### Scenario: A searched crossing evaluates only the moving part of the law

- **WHEN** a running root's law reads its own driven coordinate through a
  skeleton the run cannot classify — a detent cam carrying `sin`, `cos`
  and `sqrt` of a kinked phase — and that law also reads a chain of
  sibling coordinates that the tick does not move, so that most of the
  expression stands
- **THEN** the crossing is located by the same sampled search, at the
  same sub-interval count, the same tolerance and the same number of
  evaluations, and the work the tick does inside that search falls by
  the share of the expression that stands

#### Scenario: Every value the machine commits is unchanged

- **WHEN** that machine is stepped for a dozen ticks
- **THEN** every banked coordinate, every recorded crossing, every
  landing and every stop is the value it was before this requirement,
  bit for bit, and the conformance corpus replays byte-identical

#### Scenario: A quantity that moves entirely is evaluated whole

- **WHEN** a law's followed quantity reads only sources the tick moves,
  so that nothing in it stands
- **THEN** every point evaluates the whole expression exactly as before,
  and the tick pays the decision of which nodes move once for that
  quantity rather than once per point

#### Scenario: A branch reading holds for its own piece and no other

- **WHEN** a tick's path is cut into several pieces and a jump node reads
  a different branch on each
- **THEN** the part of the expression that stands is computed again for
  each piece, under that piece's own branches, and no value computed
  under one piece's branches is read back under another's
