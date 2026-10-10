## MODIFIED Requirements

### Requirement: A continuous law is integrated over a tick and increments propagate

Under a running root the driven coordinate of a relation SHALL move BY the
change of its law along its sources' movement, from where it stood: over
one tick a CONTINUOUS law contributes exactly `f(end) − f(start)`, `f`
being the law's `forward` face — or its `inverse` face where the rest
render solved the relation backward — evaluated over the sources' values
at the start and at the end of the tick. This SHALL be exact across the
kinks of `abs`, `min` and `max` and of the compositions built on them
(`clamp`, `clamp01`, `ramp`, `piecewise`), because it is the difference
of two exact evaluations. A law whose increment is zero although its
source moved SHALL contribute nothing, which is what disengagement is.
A law whose expression contains a DISCONTINUOUS primitive SHALL
contribute the sum of its change over the continuous pieces between its
crossings, under the requirement "A jump is located inside the tick and
subtracted"; every other rule of this requirement applies to it
unchanged.

The tick SHALL be: every input's increment is the movement its active
command admits for the tick, zero with no command. In addition, explicit
time-source relations SHALL admit the elapsed interval under "Declared time
drives retain motion across operating history"; no command is required for
those sources. The same incremental reading SHALL apply to their laws, and
time SHALL remain read-only. Increments SHALL then
propagate over the relation graph in the direction each relation was
solved by the rest render — forward through a law, backward through an
invertible one, identity through a wiring into a bank coordinate,
forward or backward through a derived coordinate's linear formula —
every source of a relation naming several being determined before it
contributes. A coordinate no increment reaches SHALL HOLD its committed
value. Two increments that disagree on one coordinate — beyond
`1e-9 · max(1, |a|, |b|)` — SHALL be a CONFLICT, refused naming the
formula or relation that predicted each and the coordinate. A joint
coordinate whose new value would leave its declared range SHALL NOT
fail the tick: it SHALL STOP at its bound under the requirement "A
declared range is a physical stop located inside the tick", which
splits the tick into segments and integrates each by this requirement
unchanged. A tick that fails
SHALL commit nothing: the bank, the tick count and the bound tree stand
as before, every segment of it included, and every command that moved
an input in that tick is
retired reporting `refused`. A tick that succeeds SHALL commit the
increments, advance the tick count, bind the whole snapshot through
`set_state` with `time` at `k*dt`, record if recording is on, and only
then run due actions and cadences.

Derived coordinates and plain ports SHALL NOT be stored: the ordinary
enumeration computes them from the run-bound terms on every tick.

#### Scenario: Moves accumulate and an affine chain follows

- **WHEN** a running root states `crank.drives(first.turn, ratio=2.0)`
  and `first.turn.drives(second.turn, ratio=-1.5)`, and the simulation
  moves `crank` by `10` over one second twice
- **THEN** the bank reads `crank == 20`, `first.turn == 40` and
  `second.turn == -60`, and the leaves stand at those angles

#### Scenario: A law with a kink integrates exactly

- **WHEN** `lever.drives(slide.travel, law=tooth_window)` carries
  `4 + 72 * clamp01((angle − 113.5) / 11.25)` and `lever` moves from
  `100` to `140` in eight ticks of five degrees
- **THEN** `slide.travel` reads exactly `13.6` after the third tick,
  `45.6` after the fourth, `76.0` from the fifth on, and stays `76.0`
  while the lever goes on to `140`

#### Scenario: Backward propagation through an invertible law

- **WHEN** a running root states `crank.drives(first.turn, ratio=2.0)`
  and `second.turn.drives(first.turn, ratio=4.0)`, so the rest render
  solved the second relation backward, and `crank` moves by `10`
- **THEN** `first.turn` reads `20` and `second.turn` reads `5`, the
  inverse of the affine law having propagated the increment

#### Scenario: An undriven joint holds while an unrelated input moves

- **WHEN** the crank of the same root moves while `lever` has no command
- **THEN** `slide.travel` and `lever` read exactly what they read before
  the move, on every tick

#### Scenario: Two inputs prescribing one rigid group inconsistently are refused

- **WHEN** a running root declares `wrist` and `tool` joints,
  `left = wrist + 2 * tool`, and states `wrist_in.drives(wrist)`,
  `wrist.drives(tool, ratio=1.0)` and `sum_in.drives(left)`, and the
  simulation moves `wrist_in` by `10` while `sum_in` has no command
- **THEN** the tick is refused naming `left`, the formula, the relation
  from `sum_in` and the two increments `0` and `30`; the bank, the tick
  count and the tree are unchanged; the move's handle reports `refused`
  with no travel admitted

#### Scenario: The same group moved consistently is admitted

- **WHEN** the same simulation moves `wrist_in` by `10` and `sum_in` by
  `30` over the same duration
- **THEN** every tick is admitted and the bank reads `wrist == 10`,
  `tool == 10` and the derived `left` reads `30`

#### Scenario: A joint's range stops the tick's motion rather than failing it

- **WHEN** `first.turn` declares `range=(-90, 90)` and the crank is moved
  so that `first.turn` would reach `100`
- **THEN** the tick commits with `first.turn` at exactly `90`, the tick
  count advances, and the move's handle reports `blocked` with the
  travel it admitted

### Requirement: A relation's law is compiled to an expression over coordinate ids

At construction under a running root the system SHALL COMPILE the
relations the rest render solved into a program over the bank: each
relation's law SHALL be applied ONCE to a symbolic token per source
coordinate, in the direction the rest render solved it, and the
expression graph that application builds — over the qualified ids of
the sources — SHALL be what the run evaluates on every tick and what
the refusals below inspect. A graph containing a DISCONTINUOUS
primitive — a call to `floor`, `ceil` or `sign`, the `%` operator, or a
comparison — SHALL additionally be compiled into a JUMP PLAN: its jump
nodes in the graph's postorder, each with the level quantity whose
surfaces it crosses, the graph of that level quantity with the jump
nodes inside it replaced by branch placeholders, whether that level
quantity is AFFINE in the sources, and the SKELETON of the whole
expression with every jump node so replaced. A wiring into a bank
coordinate SHALL be an
identity edge and a derived coordinate a linear edge.

The compiled edges SHALL be ORDERED so that every edge's sources are
determined before it runs: over the DEPENDENCY GRAPH in which edge A
precedes edge B when B reads a coordinate A determines — a coordinate an
edge itself determines EXCLUDED, because that is a read of what the
coordinate holds — the edges SHALL be ordered topologically, with each
nontrivial STRONGLY CONNECTED COMPONENT of that graph contracted to ONE
entry, a BLOCK, under the requirement "A selection decides which sources
a law reads". A coordinate no edge determines SHALL be resolved from the
start: it is an input, or it HOLDS. A relation or
wiring none of whose driven ends is, or reaches through such
intermediates, a bank coordinate SHALL be left to the ordinary
enumeration, and SHALL leave nothing of itself in the program: the
program's COORDINATES SHALL be the bank's, plus exactly the ends its
compiled edges read and give. An end of a relation left to the ordinary
enumeration SHALL NOT be a coordinate of the program, SHALL NOT be
published as one, and SHALL NOT be a reason to refuse the program — the
run never computes it, and the ordinary enumeration recomputes it from
the bank on every tick exactly as it does under no time base at all.
The program SHALL have an IDENTITY derived from the root
class, the bank's ids, the inputs' declarations and every edge's ends,
direction and expression.

The system SHALL refuse, at construction and by relation identity —
naming the relation as written and the class that stated it:

- a law that cannot be applied to symbols — one that raises when handed
  a symbolic token, returns something that is neither a number nor an
  expression, or whose expression holds text the framework cannot
  evaluate or a call outside the symbolic vocabulary — saying that a
  running law is an expression over its sources;
- a relation or wiring INTO a bank coordinate whose source is a
  coordinate the run does not own and no compiled edge computes, EXCEPT
  the root's explicitly declared running time source — a
  plain port the author's `simulate()` binds — saying to state that
  value as a relation or a joint;
- a compiled law with a free clock name not declared among its sources,
  including a symbolic `owner.time` captured by a factory — naming the
  relation and showing the explicit `time` source in `drives` as the repair;
  no implicit time dependency SHALL be inferred. Any other unsupported free
  name SHALL likewise be refused as outside the declared sources. This
  does not claim to detect a Python read already reduced to a numeric
  constant before graph compilation;
- a relation naming several driven ends of which some are bank
  coordinates and some are not;
- a set of relations whose dependencies form a CYCLE that no selection
  breaks — naming every relation on the cycle and the coordinates they
  wait on, saying that a running program is ordered before it runs, and
  saying what a switch would be, in the terms the requirement "A
  selection decides which sources a law reads" defines: a source that
  folding a jump node to zero removes from the law, where that node's
  level reads no coordinate the cycle determines and its zero branch is
  one the node holds over an interval of that level — so a `sign` is not
  one;
- a law whose expression contains a DISCONTINUOUS primitive and none of
  whose driven ends is a coordinate the run owns — a plain port or a
  derived coordinate the ordinary enumeration recomputes from the bank
  on every tick — saying that a subtracted jump implies a history,
  that only a coordinate the run owns keeps one, and that the relation
  should be stated into the joint coordinate so the port follows it.

A law whose expression has no free coordinate — a constant — SHALL
compile and contribute a zero increment; a law that can move its
coordinate only by jumping SHALL be refused under the requirement "A
law that can only jump is refused as arithmetic".

#### Scenario: A running root with a floor in a law compiles

- **WHEN** a running root states `crank.drives(first.turn, law=window)`
  where the law's expression contains `floor(angle / 360)`
- **THEN** construction succeeds, the compiled graph names the source's
  qualified id, its jump plan holds one `floor` node whose level
  quantity is that qualified id divided by 360 and is AFFINE in the
  sources, and the same root without `Time.running()` poses exactly as
  before

#### Scenario: A jumping law into a plain port is refused

- **WHEN** a running root states `crank.drives(register, law=window)`
  where `register` is a plain port wired to a joint coordinate and the
  law's expression contains `floor`
- **THEN** construction is refused naming the relation and the port, and
  saying to state the relation into the joint coordinate the run owns;
  and the same relation stated into that joint coordinate compiles

#### Scenario: A law over stdlib math is refused as non-symbolic

- **WHEN** a running root's law computes `math.sin(angle)` from Python's
  standard library
- **THEN** construction is refused naming the relation and saying the law
  cannot be applied to symbols

#### Scenario: A relation sourced from an author-bound port is refused

- **WHEN** a running root's `simulate()` binds a plain port from its
  crank and a relation drives a joint from that port
- **THEN** construction is refused naming the relation and the port, and
  advising a relation or a joint

#### Scenario: A law with a kink compiles

- **WHEN** a running root's law is `4 + 72 * clamp01((angle − 113.5) / 11.25)`
- **THEN** construction succeeds and the compiled expression names the
  source's qualified id and only `min` and `max` among calls

#### Scenario: A relation the enumeration keeps leaves no coordinate in the program

- **WHEN** a running root drives the `height` port of its `.repeat()`
  children, and no relation carries those ports back to a joint
  coordinate
- **THEN** the compiled program's coordinates are the driver and the
  joint coordinates only, no copy's port is among them, the program's
  edges are unchanged, and the run poses every copy exactly as the same
  root without `Time.running()` does

#### Scenario: A part this render omits leaves no coordinate in the program

- **WHEN** a running root holds an optional part whose joint one of its
  drivers drives, and this render `omit()`s that part
- **THEN** the compiled program's coordinates are the driver and the
  joint coordinates of the parts that ARE in the machine, the omitted
  part's coordinate is not among them, and construction succeeds

#### Scenario: Two relations waiting on each other are refused

- **WHEN** a running root states `(a & b.turn).drives(c.turn, law=...)`
  and `(a & c.turn).drives(b.turn, law=...)`, neither law gating the
  other's coordinate behind a jump node
- **THEN** construction is refused naming BOTH relations and saying they
  form a cycle the run cannot order

#### Scenario: A wiring on a cycle is refused by name

- **WHEN** a running root states a cycle one of whose steps is a wiring
  or a derived coordinate rather than a law
- **THEN** construction is refused naming that wiring or derived
  coordinate and saying it carries no jump node and therefore no
  selection

#### Scenario: Captured symbolic time is not a hidden motor

- **WHEN** a compiled running law closes over symbolic `owner.time` but
  its relation names only ordinary coordinates as sources
- **THEN** construction refuses it by relation identity and explains how
  to name the root's `time` in the source group, rather than accepting a
  law whose free clock is never advanced

#### Scenario: An explicit time source is owned by the run clock

- **WHEN** a running law names the root's `time` as a source
- **THEN** compilation recognizes a read-only clock path rather than
  refusing it as an unowned port, and preserves all existing law-class
  checks, including refusal of unsupported self-read arithmetic


### Requirement: A declared range is a physical stop located inside the tick

Under a running root a banked joint coordinate's declared `range` SHALL
be a PHYSICAL STOP rather than a refusal: when the committed value of
the coordinate at the end of the stretch of tick being integrated would
lie outside one of its bounds AND lie further outside than the value it
held at the START of that stretch, the system SHALL
LOCATE the fraction `t*` of the tick at which the coordinate reaches
that bound and SHALL truncate that tick's motion there for the
coordinate and its group. A coordinate that does not move over a
stretch SHALL NOT stop in it. The tick SHALL COMMIT and the tick count
SHALL advance. Both bounds SHALL remain INCLUSIVE, so a tick landing
exactly on a bound SHALL NOT be a stop. A bound stated as `None` SHALL
be unbounded on that side and SHALL never stop anything.

A bound that reads the joint's own coordinate alone SHALL be evaluated
ONCE PER TICK, at the tick's START, from the committed bank, so that
every segment of one tick is measured against the same number.

A bound that READS OTHER COORDINATES (a `Bound` with reads) SHALL be a
CONSTRAINT between the coordinate and what it reads, evaluated ALONG
the path of each stretch: the joint's own coordinate in the expression
SHALL take the value it holds in the tick's committed bank, and every
coordinate the bound reads SHALL take the value it has along the
stretch's path — an input its admission scaled by the fraction, a
coordinate the increment its determiner gives over the path truncated
there, computed over the SUB-PROGRAM that determines the bounded
coordinate and what the bound reads, by the same arithmetic the segment
is later committed by. The CONSTRAINT LEVEL of such a bound is the
coordinate's value minus the evaluated upper bound, or the evaluated
lower bound minus the coordinate's value; outside is a positive level.
Such a constraint SHALL be examined on a stretch only when the bounded
coordinate or a coordinate it reads has a nonzero increment over that
stretch; a stretch in which nothing the bound depends on moves SHALL
raise nothing and evaluate nothing, so a coordinate standing outside is
free until something carries it further. On a stretch in which NO READ
moves, the bound SHALL be the number its expression gives at the tick's
committed own value and the reads' standing values, evaluated once, and
the coordinate SHALL be stopped or freed exactly as a bound over its own
value alone is — the same detection, localization and commit at the
bound. When a read moves, the level SHALL be sampled at the same fixed number of sub-intervals a jump
search uses — each sample one pass over the bound's sub-program with
every admission scaled by that fraction — and the coordinate SHALL stop
in the stretch at the FIRST sample at which the level is positive AND
greater than the level at the stretch's start: carried further outside
than it stood, by whatever moved, whether the coordinate itself, what
the bound reads, or both — so a constraint violated inside a stretch and
satisfied again at its end is stopped where the violation begins, not
committed. A violation that begins and ends inside one sub-interval is
outside that guarantee, and the answer to it is a smaller `dt`.

The coordinate's value along the tick SHALL be `v(0)` plus the
increment its DETERMINER gives over the tick's path truncated at `t` —
the same path, in the same joint source space, that a law is integrated
over, so that a law which jumps contributes its subtracted-jump
increment here too. `t*` SHALL be the SMALLEST fraction at which that
value reaches the bound, and SHALL be `0` when the coordinate already
stands at or beyond it. Where the determiner is AFFINE in its sources
along the path `t*` SHALL be SOLVED exactly, over the pieces of its own
jump partition where it has one. Where the determiner is PIECEWISE
AFFINE — the requirement "A kink is a cut, and a piecewise-affine
quantity is solved" — `t*` SHALL be SOLVED exactly over those pieces
SUB-DIVIDED at the determiner's own kink breakpoints; those breakpoints
SHALL be taken even where the determiner carries no jump plan at all, a
quantity that is linear between its kinks being not linear across them.
Otherwise the value SHALL be sampled
at the same fixed number of sub-intervals a jump search uses and `t*`
bracketed and bisected to the same tolerance, with the same documented
limit. No further tolerance SHALL be introduced, and a coordinate stopped by a
bound reading its own coordinate alone SHALL be committed at its bound
EXACTLY.

For a bound that reads other coordinates `t*` SHALL be located from the
samples above: `0` when the level is already positive at the stretch's
start and the first sample is higher; otherwise the crossing bracketed
between the last sample at which the bound was satisfied and the first
at which it was not, bisected to the same tolerance with the same
documented limit, `t*` being the INSIDE end of the final bracket — the
last fraction at which the bound is satisfied.
The coordinate SHALL NOT be moved onto the bound: the segment committed
at `t*` by the same arithmetic satisfies it, and the system SHALL assert
that the level at the committed state is at most zero, refusing the
whole tick as a broken invariant otherwise.

For a program with explicit time drives, the source/group procedure below
SHALL additionally consider one independent time-drive admission per resolved
time-source relation, under "Declared time drives retain motion across
operating history". These admissions participate in the same outward-motion
tests and segmented integration as inputs but are NOT commandable inputs;
a stopped time admission holds for the remainder of that tick and is retried
from global elapsed time on the next tick. Time itself is never stopped.
All the following command-retirement rules apply only to actual commands.

The GROUP a stop stops SHALL be every INPUT that reaches the stopped
coordinate through the compiled program AND whose own movement over the
stretch changes it — tested with that input's admission alone and every
other input's set to zero — together with everything those inputs alone
determine. For a bound that reads other coordinates the candidates
SHALL be the inputs reaching the bounded coordinate OR any coordinate
the bound reads, and a candidate SHALL be in the group when its
admission alone, over the bound's sub-program, carries the constraint
level OUTWARD — raises it — so an input moving a read coordinate so as
to make a standing position invalid is stopped where the constraint
becomes active and the standing coordinate does not move, while an
input moving a read coordinate so as to relieve the constraint runs
its full tick. An input that does not reach it, or reaches it only through
a law that contributes nothing to it over the stretch (a disengaged
coupling), SHALL run its full tick; a coordinate determined by both a stopped input and a free
one SHALL move by what the free one contributes after `t*`. The tick
SHALL therefore be integrated as SEGMENTS — `[0, t*]` with every
input's admission scaled by `t*`, then `[t*, 1]` with the stopped
inputs admitting nothing and the others scaled by `1 − t*` — each
segment by the ordinary tick procedure, its own jump partition
included.

The remaining segment SHALL then be examined for a further stop and the
process repeated, always taking the EARLIEST `t*` first. Two stops
whose fractions are within the crossing tolerance of each other SHALL
be ONE event, stopping the union of their groups at one boundary,
whether they are on one group or on two. A tick SHALL admit at most as
many stop events as it has inputs PLUS time-drive admissions admitting
travel, because each event stops at least one moving admission for the rest
of that tick.

A tick SHALL remain ATOMIC across its segments: the bank, the commands'
admitted travel and the records SHALL be staged and applied only when
every segment has succeeded, and a conflict or an unintegrable law in
any segment SHALL commit nothing and retire the commands that moved as
`refused`, exactly as an unsegmented tick does.

Untimed and looping documents SHALL be unchanged: there a declared
range REFUSES a binding outside it and never clamps or stops — a
bound reading other coordinates at the close of the enumeration, under
the joints requirement "A declared range refuses a binding outside it".

#### Scenario: A rack stops at its bound while an independent motor continues

- **WHEN** a running root drives `rack.travel`, declaring
  `range=(None, 50)` and standing at `45`, from `steer` at ratio `1.0`,
  drives an unrelated `wheel.turn` from `motor` at ratio `3.0` under
  `rate('motor', 90)`, and `move('steer', by=10, duration=0.1)` is
  requested at `dt = 0.1`
- **THEN** the tick commits with `rack.travel` at exactly `50`, the
  steering handle reports `blocked` with `5.0` admitted of `10`
  requested, the wheel gains its full `27` degrees for that tick, and
  the rack does not move on any later tick

#### Scenario: A ratchet blocks reverse at the last seated tooth

- **WHEN** an input arbor declares
  `range=(lambda turn: 36 * floor(turn / 36), None)`, stands at `40`,
  and `move('arbor', by=-10, duration=0.1)` is requested at `dt = 0.1`
- **THEN** the tick commits with the arbor at exactly `36`, the handle
  reports `blocked` with `-4` admitted, and a further
  `move('arbor', by=-10, duration=0.1)` from `36` reports `blocked` with
  `0` admitted while a `move('arbor', by=4, duration=0.1)` completes

#### Scenario: A stop admits the same travel at any cadence

- **WHEN** the same reverse move of `-10` from `40` against the same
  ratchet is taken in one tick, in four and in forty
- **THEN** all three leave the arbor at exactly `36` and all three
  handles report exactly `-4` admitted

#### Scenario: A multi-source coordinate keeps moving on its free input

- **WHEN** `a_in` drives `c.turn` at ratio `1.0` with
  `range=(None, 10)` from `8`, `(a_in & b_in).drives(d.turn, law=2a+3b)`
  is stated, and one tick moves `a_in` by `4` and `b_in` by `6`
- **THEN** `c.turn` stops at `10` with `a_in` admitting `2`, `b_in`
  admits its full `6`, and `d.turn` gains exactly `22` rather than `26`

#### Scenario: Two stops in one tick are taken earliest first

- **WHEN** one tick would take a lever past its bound at a quarter of
  the tick and a rack past its own at half of it, on two groups that
  share no input
- **THEN** both commit at their bounds, both handles report `blocked`
  with the travel each made, and `sim.stops` holds two entries with the
  two fractions in that order

#### Scenario: A stop and a jump crossing in one tick

- **WHEN** a crank at `130` drives `first.turn` at ratio `1.0` with
  `range=(None, 145)` and drives `wrapped.turn` by
  `2 * wrap(angle, 90)`, whose fold falls at `135`, and one tick would
  move the crank by `20`
- **THEN** `first.turn` stops at `145`, `wrapped.turn` gains exactly
  `30`, the `wrap` crossing is recorded at the fraction `0.25` OF THE
  TICK — not at the `1/3` it sits at within the segment — the stop at
  `0.75`, and the handle reports `blocked` with `15` admitted

#### Scenario: A block replays identically from a snapshot

- **WHEN** a snapshot taken before a blocking tick is restored and the
  same command is issued again
- **THEN** the run blocks at the same coordinate value, admits the same
  travel and records the same stop; and a snapshot taken AFTER the block
  restores a run with no command on that input

#### Scenario: A tick that fails after a stop commits nothing

- **WHEN** the segment after a stop meets a conflict
- **THEN** the bank, the tick count and the tree stand as before the
  whole tick, no stop and no crossing is recorded, and the commands that
  moved retire `refused`

#### Scenario: A disengaged coupling does not stop its input

- **WHEN** a wheel with a declared upper bound is driven by
  `(push & crank & gate)` through `push + crank * (gate > 0.5)`, `crank`
  also drives an unrelated flywheel, the gate stands at `0`, and one tick
  moves `push` past the wheel's bound while `crank` moves too
- **THEN** the wheel stops at its bound, `push`'s command is retired
  `blocked` with the travel admitted before the stop, `crank`'s command
  runs its full tick and completes, and the flywheel gains the full
  tick's travel; with the gate at `1` the same tick retires both
  commands `blocked`

#### Scenario: A plug does not turn while a pin crosses the shear line

- **WHEN** a running root drives `key.travel` from `feed` at ratio `1.0`,
  drives `p1.lift` and `p2.lift` from `key.travel` through the laws
  `5 - 5 * clamp01((travel - 10) / 5)` and
  `5 - 5 * clamp01((travel - 13) / 5)`, so the first lift enters the
  window at a travel of `14.95`, the second at `17.95`, and both stand
  at `0` from `18` on, drives
  `plug.turn` from `turn`, `plug.turn` declaring
  `range=(0, Bound(lambda turn, a, b: 90 * (abs(a) <= 0.05) * (abs(b) <= 0.05), reads=(p1.lift, p2.lift)))`,
  the key stands at `10`, and `move('turn', by=30, duration=0.1)` is
  requested at `dt = 0.1`
- **THEN** the tick commits with `plug.turn` and `turn` at exactly `0`,
  the handle reports `blocked` with `0` admitted, `sim.commands` is
  empty, and `sim.stops` holds one entry naming `plug.turn`, `high`,
  the evaluated bound `0`, the fraction `0` and the inputs `('turn',)`

#### Scenario: A plug turns once every pin clears

- **WHEN** the same root has moved `feed` to `20` over four ticks and
  `move('turn', by=30, duration=0.1)` is then requested
- **THEN** the tick commits with `plug.turn` at `30`, the handle reports
  `completed` with `30` admitted, and `sim.stops` is empty

#### Scenario: Insertion and turning in one tick

- **WHEN** the key stands at `10` and, in the same tick,
  `move('feed', by=10, duration=0.1)` and `move('turn', by=30, duration=0.1)`
  are both requested, the pins clearing at `0.8` of the tick
- **THEN** the tick commits with `key.travel` at `20` and `plug.turn` at
  `0`, the feed handle reports `completed` with `10` admitted, the turn
  handle reports `blocked` with `0` admitted, and a
  `move('turn', by=30, duration=0.1)` requested on the next tick completes

#### Scenario: Withdrawing the key from a turned plug stops the key, not the plug

- **WHEN** the key stands at `20` with the plug turned to `30` and no
  bound is declared on `key.travel`, and `move('feed', by=-5, duration=0.1)`
  is requested, the second pin's lift leaving the window at a travel of
  `17.95`
- **THEN** the tick commits with `plug.turn` at exactly `30` and
  `key.travel` within the crossing tolerance of the tick's travel below
  `17.95` and inside the window, the handle reports `blocked` with the
  travel it made, and `sim.stops` holds one entry naming `plug.turn`,
  `high`, the evaluated bound `90`, the fraction at which the pin left
  the window and the inputs `('feed',)`

#### Scenario: A declared capture stops the key at once

- **WHEN** `key.travel` additionally declares
  `range=(Bound(lambda travel, turn: 20 * (turn > 0), reads=(plug.turn,)), 20)`,
  the plug stands turned at `30` and `move('feed', by=-5, duration=0.1)`
  is requested
- **THEN** the tick commits with `key.travel` at exactly `20`, the
  handle reports `blocked` with `0` admitted, and the stop names
  `key.travel`, `low`, `20`, the fraction `0` and `('feed',)`

#### Scenario: Returning the plug and withdrawing the key in one tick

- **WHEN** the plug stands at `30`, the key at `20` with the capture
  declared, and in one tick `move('turn', by=-30, duration=0.1)` and
  `move('feed', by=-5, duration=0.1)` are both requested
- **THEN** the plug returns to `0` and its handle completes, the key
  stands at `20` and its handle reports `blocked` with `0` admitted, and
  a withdrawal requested on the next tick completes

#### Scenario: A pawl lifting during the tick releases the ratchet

- **WHEN** an arbor's wheel declares
  `range=(Bound(lambda turn, lift: 36 * floor(turn / 36) - 1000 * (lift >= 1), reads=(pawl.lift,)), None)`,
  stands at `40`, and one tick moves the arbor by `-10` while a `lift`
  input raises `pawl.lift` from `0` to `1` at `0.3` of the tick
- **THEN** the arbor completes at `30` with `-10` admitted and no stop
  is recorded; and with the pawl reaching `1` at `0.5` of the tick
  instead, the wheel stops at exactly `36` at `0.4` of the tick and the
  arbor's handle reports `blocked` with `-4` admitted

#### Scenario: A bound reading other coordinates admits the same travel at any cadence

- **WHEN** the withdrawal from the turned plug is taken in one tick, in
  four and in forty
- **THEN** all three stop the key at the same travel within the crossing
  tolerance and all three handles report the same admitted travel

#### Scenario: A constraint stop replays identically from a snapshot

- **WHEN** a snapshot taken before a tick that stops the key from a
  turned plug is restored and the same command is issued again
- **THEN** the run blocks at the same travel, admits the same travel and
  records the same stop

#### Scenario: A machine with no bound reading other coordinates pays nothing

- **WHEN** the `Train` fixture is stepped after this change
- **THEN** one tick costs what ADR-108 recorded within measurement noise
  and the deterministic count of graph evaluations per tick is unchanged

## ADDED Requirements

### Requirement: Declared time drives retain motion across operating history

A running simulation SHALL advance a relation explicitly sourced by its
root's time without a command, according to the existing continuous-law
increment, jump-subtraction and supported self-read rules. At tick `k`,
elapsed seconds SHALL traverse `[k*dt, (k+1)*dt]`; an instantaneous input
operation SHALL traverse no time. The first tick starts from the numeric
rest at time zero. Ordinary driver inputs SHALL still move only through
their admitted commands. A relation's value SHALL NOT be reinterpreted as
a velocity: the existing multivariate incremental law semantics SHALL apply.

A disabled relation SHALL contribute no motion when its declared law
contributes none. Its banked coordinates SHALL hold and resume from those
held values, without accumulating or recovering motion for elapsed intervals
in which the drive was disengaged. Enable discontinuities SHALL be handled
by the existing jump-subtraction rules, not by resetting the joint to an
absolute time-derived value. A nonlinear time law SHALL use current global
seconds, not a mechanism-local clock, when re-enabled.

Each resolved relation naming time SHALL have one independent time-drive
admission identity. Its multiple targets SHALL share that identity, and its
downstream relations SHALL follow the retained motion of their declared
source coordinates. Two separate time drives SHALL NOT be treated as one
physical input just because they read the same clock. Stops SHALL suppress
only the admissions the existing source-sensitive stop test identifies as
pushing the affected mechanism. Disengaged and unrelated drives SHALL
continue. Existing incompatible-writer conflicts SHALL remain atomic
refusals, not be resolved by giving one drive priority.

A stopped time admission SHALL remain suppressed through that tick's
remainder. Its time path SHALL hold at the stopping instant for that
remainder; other sources SHALL follow their remaining admitted paths.
On the next tick it SHALL attempt only that tick's elapsed interval, without
an increment for the gap since it last moved. A still-active bound SHALL
admit zero; a subsequently released constraint SHALL permit new motion
without a new command. There SHALL be no deferred travel and no hidden
restart latch. An operator command stopped by the same mechanism SHALL
still retire `blocked`; it SHALL NOT acquire automatic retry.

The global clock SHALL advance for every successful advancing tick even
when all mechanical motion stops. Failure SHALL commit neither time nor
mechanical state nor partial records. Snapshot, restore and reset SHALL
reproduce the clock, bank and subsequent time-driven behavior without extra
author-managed phase state. A non-ticking pose, render, publication or state
read SHALL leave the retained state untouched.

When recording is enabled, a running stop SHALL keep `inputs` as actual
driver IDs and SHALL additionally expose `time_drives` as a sorted tuple of
the blocked time-drive IDs, empty when none are blocked. Existing fields and
command-only serialized records SHALL retain their representation; serialized
records SHALL add `time_drives` only when nonempty. The IDs SHALL map to the
relations in the published program. Repeated attempts against a standing bound
may record a new zero-travel stop on each advancing tick, within the existing
bounded ring policy.

#### Scenario: Construction and inspection do not run a shaft

- **WHEN** an affine time-driven shaft with zero rest is constructed,
  inspected, rendered and published before any tick
- **THEN** its retained angle remains zero and no command or tick is created

#### Scenario: Seconds drive a retained shaft without a rate command

- **WHEN** `time.drives(shaft.turn, ratio=6)` starts at zero and advances
  two simulated seconds at `dt=0.02` with no commands
- **THEN** `shaft.turn` is 12 native angular units, `sim.time` is 2,
  and the command registry and declared input set remain empty

#### Scenario: Enable changes preserve accumulated angle

- **WHEN** the law is `6*t*(enabled > 0.5)`, it runs enabled for two
  seconds, is disabled instantaneously for two more, is enabled
  instantaneously again and runs for one more second
- **THEN** the shaft reads 12 before disabling, 12 throughout the disabled
  interval and both input changes, and 18 at time 5

#### Scenario: Winding changes reserve without rewinding the train

- **WHEN** the Astrarium-equivalent fixture uses
  `(time & enabled & wind & shaft.turn)` with the law
  `t*(enabled > 0.5)*(angle-wind < 10)`, and
  `(shaft.turn & wind)` drives a weight by `angle-wind` in range 0 to 10;
  it runs two seconds, is disabled for two, winds by 2 instantaneously,
  then is enabled and runs another second
- **THEN** the shaft reads 2 throughout stopping and winding, the weight
  moves from 2 to 0 when wound, and they end at shaft 3 and weight 1
  at time 5 without a dummy input or rate command

#### Scenario: Exhaustion and rewind resume only new motion

- **WHEN** the same fixture runs for twelve seconds, is disabled, winds
  by 5 instantaneously, is enabled and runs another second
- **THEN** exhaustion leaves shaft and weight at 10 at time 12, winding
  leaves shaft at 10 and weight at 5, and resumption ends at shaft 11 and
  weight 6, without catching up the two exhausted seconds

#### Scenario: A hard stop holds the connected train but not another time drive

- **WHEN** one time relation drives a shaft at 1 unit per second, that shaft
  drives a weight at ratio 1 bounded at 2.5, and an independent time
  relation drives another shaft at 2 units per second; four one-second
  ticks run from zero
- **THEN** the first shaft and weight end at 2.5, the independent shaft
  ends at 8 and time at 4; the first stop lies halfway through tick 3,
  and its record names the first time drive, no unrelated drive and no
  fabricated operator input

#### Scenario: Grouped targets share one physical drive

- **WHEN** one time-source relation gives two shaft coordinates and a
  downstream bound stops motion supplied by that relation
- **THEN** both targets receive only their coherent admitted prefix,
  while a separately declared unrelated time drive continues

#### Scenario: Release takes effect without restarting a rate

- **WHEN** a time-driven coordinate has stopped at a bound, a zero-duration
  operator action relieves that constraint, and one more tick runs
- **THEN** the coordinate gains only the new tick's permitted motion, no
  command is created, and elapsed time includes the stopped interval

#### Scenario: Retained phase and global time are not conflated

- **WHEN** a shaft follows the law `t*t*(enabled > 0.5)`, runs for one
  second, is disabled until time 3 and then runs enabled until time 4
- **THEN** its retained value is 1 while disabled and 8 at time 4,
  because the last interval contributes `4*4-3*3`, not a restarted age

#### Scenario: Snapshot replay and reset include autonomous motion

- **WHEN** a snapshot is taken before a sequence of running, disabling,
  winding and restarting, then restored and the same operations repeated
- **THEN** every tick's bank, time, stops and crossings agree within the
  existing numerical contract; reset returns the original bank and tick,
  after which the first tick behaves exactly like a fresh run

#### Scenario: A late failure cannot leave a partially advanced clock

- **WHEN** a segmented tick first reaches a stop and then encounters an
  existing-law conflict on an independent branch
- **THEN** neither elapsed time, any bank value nor any ring entry commits;
  actual moved commands retire as refused under the existing rule

#### Scenario: Commanded and pose-only running models remain unchanged

- **WHEN** existing commanded-driver fixtures and a root using time only
  for a plain part's absolute pose are run without declared time drives
- **THEN** their state, command outcomes, ownership checks and clock
  behavior match the pre-change fixtures
