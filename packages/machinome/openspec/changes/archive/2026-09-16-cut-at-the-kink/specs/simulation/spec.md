## ADDED Requirements

### Requirement: A kink is a cut, and a piecewise-affine quantity is solved

Under a running root a quantity the run has to follow along a tick's path
— a jump node's LEVEL QUANTITY, a law's SKELETON, a determiner's value —
SHALL be classified from its expression alone, once, at compile:

- AFFINE in the sources: a number, a source name, a branch placeholder
  (a constant on the piece being cut), a unary minus, a sum or difference
  of affine operands, a product with a constant operand, or a quotient by
  a constant one.
- PIECEWISE AFFINE in the sources: the same, admitting KINK NODES whose
  operands are themselves affine or piecewise affine. The KINK NODES
  SHALL be exactly the CONTINUOUS SELECTIONS of the symbolic vocabulary —
  `abs(x)`, `min(a, b)` and `max(a, b)` — each of which returns one of
  its operands exactly and is continuous where they meet. `clamp`,
  `clamp01`, `ramp` and `piecewise` are compositions of those over their
  arguments and SHALL therefore be piecewise affine wherever their
  arguments are.
- Neither: a call outside the kinks — `sin`, `cos`, `tan`, `asin`,
  `acos`, `atan`, `atan2`, `sqrt` — a power, or a product or quotient of
  two operands that both move.

A kink node SHALL have a LEVEL of its own — `x` for `abs(x)`, `a − b` for
`min(a, b)` and `max(a, b)` — and ONE surface, at zero. Its BREAKPOINTS
over a stretch of the path SHALL be the fractions at which that level
reaches zero, computed in the graph's POSTORDER so that a kink nested
inside another's level is cut first: on each sub-interval its inner kinks
have already produced, the level is affine, and its zero SHALL be SOLVED
from the sub-interval's two endpoint values. No sampling, no bisection
and NO FURTHER TOLERANCE SHALL be introduced; two breakpoints closer than
the crossing tolerance SHALL be one, exactly as two crossings are.

**A kink breakpoint is NOT a crossing.** The quantity is CONTINUOUS
there: the breakpoint SHALL NOT be recorded among the tick's crossings,
SHALL NOT enter the jump partition a law's increment is summed over,
SHALL NOT move a coordinate to the far side of anything, and SHALL NOT
count toward the maximum number of crossings a tick admits. It is a
sub-division used to SOLVE, and a machine whose laws carry no kink SHALL
pay nothing for this requirement.

Classification SHALL be conservative and structural: a quantity the rules
above do not classify SHALL keep the sampled search unchanged, with the
same sub-interval count, the same bisection and the same documented
limit. In particular a kink over a CURVED operand — `max(0, sin(x))` —
is not piecewise affine and SHALL be searched, even though a particular
piece of it may happen to be constant.

#### Scenario: A clamped window's crossing is solved, not searched

- **WHEN** a running root's law gates on a comparison whose level reads
  `clamp01((control − 0.1) / 0.8)` of a driver, and the gate's surface is
  crossed strictly inside a tick in which the clamp itself is not at
  either of its kinks
- **THEN** the crossing is located at the fraction the affine solution
  gives, to within a few units in the last place, rather than to the
  bisection's own tolerance, and the tick evaluates the law a small
  bounded number of times rather than once per sub-interval of the search

#### Scenario: A path that crosses the kink is cut there before it is solved

- **WHEN** the same law is driven over a tick whose path takes the clamp
  from inside its window out past `1`, and the gate's surface lies beyond
  the kink
- **THEN** the crossing is located exactly on the sloped piece it
  actually lies in, and the answer equals the one the same movement gives
  when it is split into two ticks meeting at the kink

#### Scenario: A stop on a kinked determiner that carries no jump at all

- **WHEN** a coordinate declaring a range is driven by a law with no jump
  node in it whose value is `4 + 72 * clamp01((lever − 113.5) / 11.25)`,
  and one tick's path starts on the law's FLAT piece and would end past
  the bound on its SLOPED one
- **THEN** the stop is located at the fraction on the sloped piece, the
  coordinate is committed AT its bound exactly, and the answer is not the
  one a single linear division over the whole tick would give

The classification SHALL remain INTERNAL to the run. The published
document says, per driven end of a law and per jump, whether that
quantity is AFFINE in its sources — a two-valued statement a consumer
uses to choose between a solution and a search — and a PIECEWISE AFFINE
quantity is not affine. So a kinked quantity SHALL publish that flag as
FALSE, exactly as it does before this requirement exists, and no
published document SHALL change and no document version SHALL move
because a quantity is now cut at its kinks. A consumer that has not
learned to cut at a kink SHALL therefore keep searching such a quantity,
which is correct and slower.

#### Scenario: A kinked quantity still publishes itself as not affine

- **WHEN** a running root whose law has a kinked determiner, and whose
  gate has a kinked level, is exported before and after this requirement
  exists
- **THEN** both documents declare the version they always did and are
  byte-identical, the law's driven end publishing `affine` FALSE and the
  jump publishing `affine` FALSE in each

#### Scenario: A curved law is searched exactly as before

- **WHEN** a running root's law carries `sin` or `cos` of a moving
  source, or a product of two moving sources
- **THEN** its crossings and any stop on it are located by the same
  sampled search, at the same sub-interval count and tolerance, and the
  number of evaluations the tick pays is unchanged

## MODIFIED Requirements

### Requirement: A jump is located inside the tick and subtracted

Under a running root a law whose expression contains a DISCONTINUOUS
primitive SHALL contribute, over one tick, the CONTINUOUS part of its
change: the tick's path SHALL be cut at every crossing of every jump
surface it meets, and the law's change SHALL be summed over the pieces
between those cuts, so that no jump ever moves a part.

The PATH of a tick SHALL be the straight line from the values the law's
sources hold to those values plus the increments they were given,
parametrised by a fraction `t` in `[0, 1]` — in the JOINT space of the
sources for a law naming several. A tick in which no source moves SHALL
contribute zero without evaluating the law.

Each jump node SHALL have a LEVEL QUANTITY and a family of SURFACES:
`floor(x)` and `ceil(x)` over `x` at every integer; `sign(x)` over `x`
at zero; `a % b` over `a / b` at every NONZERO integer, the operator
being the remainder that takes the sign of the DIVIDEND and is
therefore continuous where `a / b` crosses zero; a comparison over
`a − b` at zero. `wrap()` SHALL be integrated as the `ceil` it is built
on, and `piecewise()` SHALL need nothing, being built on `clamp01`.

On each open piece between two cuts every jump node SHALL hold one
BRANCH — the integer for `floor` and `ceil`, `-1`, `0` or `+1` for
`sign`, the integer quotient for `%` so that the node reads `a − q·b`,
and `1` or `0` for a comparison — determined by evaluating its level
quantity at the MIDPOINT of that piece, in the graph's postorder so
that a jump nested inside another's argument is determined first — with
the one amendment the requirement "A law may read the coordinate it
drives" states for a node that DEPENDS on the law's own driven
coordinate, whose value at a midpoint is a consequence of the branch
being asked for. The
law with those branches substituted SHALL be continuous on the closed
piece, and the increment SHALL be the sum, over the pieces, of that
substituted law's value at the piece's end minus its value at the
piece's start. A piece's endpoints SHALL therefore carry the one-sided
values of the law, at the tick's own start and end as well as at each
cut.

Crossings SHALL be found for every jump node of the law, in the graph's
postorder, over each piece the nodes before it have already produced,
and ALL crossings of one node inside one piece SHALL be found — not
only the difference of the piece's endpoints. Where the level quantity
is AFFINE in the sources along the path the crossings SHALL be solved
exactly, every surface between the endpoint values included. Where it is
PIECEWISE AFFINE — the requirement "A kink is a cut, and a
piecewise-affine quantity is solved" — the piece SHALL be SUB-DIVIDED at
that level's own kink breakpoints and the crossings SHALL be solved
exactly on each sub-piece, again every surface between that sub-piece's
endpoint values included. Otherwise
the piece SHALL be sampled at a fixed number of sub-intervals and each
bracketed crossing located by bisection to a stated tolerance, with the
limit of that search documented. Two crossings closer than the
tolerance SHALL be one cut, and several jump nodes crossing at one
fraction SHALL be one cut whose midpoint sample fixes every branch at
once. For a law that reads its own driven coordinate THIS partition SHALL be
built over the jump nodes that do NOT depend on that coordinate, and the
nodes that DO SHALL be walked piece by piece INSIDE each of its pieces,
under the requirement "A law may read the coordinate it drives", because
the path of that coordinate on one piece is a consequence of the
branches of the piece before it. Merging two crossings closer than the
tolerance into one cut belongs to THIS partition and SHALL NOT be
applied in that walk.

A tick that would cut one law's path more than a stated maximum number
of times SHALL be refused naming the relation, the driven coordinate,
the primitive and the count, and SHALL commit nothing — the bank, the
tick count and the bound tree standing as before and the commands that
moved an input in it retired reporting `refused` — exactly as a
conflict does. A `%` whose divisor is zero anywhere the tick evaluates
SHALL be refused the same way.

#### Scenario: A periodic window advances once per revolution

- **WHEN** a running root states
  `crank.drives(pinion.turn, law=periodic_window)` carrying
  `4 + 72 * clamp01((angle − 360 * floor(angle / 360) − 113.5) / 11.25)`,
  the crank rests at `100`, `dt` is `1/240`, and the simulation moves
  `crank` by `360` over one second, twice
- **THEN** `pinion.turn` reads `4` before the first move, `76` after it
  and `148` after the second, and the tick in which the crank passes
  `360` contributes exactly zero

#### Scenario: A tick that passes three windows adds three throws

- **WHEN** the same root is given `move('crank', by=1080, duration=0)`
  from a crank of `100`
- **THEN** `pinion.turn` reads `220`, three crossings are located inside
  that one tick, and the crank stands at `1180`

#### Scenario: A gate holds open and re-engages without a jump

- **WHEN** a running root states
  `(shaft.turn & sleeve.travel).drives(wheel.turn, law=clutch)` carrying
  `-2 * shaft * (sleeve > 0.5)`, and the shaft turns by `4` over a tick
  in which the sleeve stands at `0`, then over a tick in which it
  stands at `1`, then over a tick in which it travels from `0` to `1`
- **THEN** `wheel.turn` moves by `0`, then by `-8`, then by `-4` — the
  travel after engagement only — and never by the value the gate factor
  would have jumped to

#### Scenario: A wrapped law integrates to the unwrapped travel

- **WHEN** a running root's law is `2 * wrap(angle, 360)` and the crank
  travels `500` degrees from `100`
- **THEN** the driven coordinate gains exactly `1000`, and the two
  `ceil` crossings inside that travel contribute nothing of their own

#### Scenario: A remainder window and a floor window agree

- **WHEN** two running roots carry the same tooth window, one written
  with `angle − 360 * floor(angle / 360)` and one with `angle % 360`,
  and both cranks are moved through one revolution from `100`
- **THEN** both driven coordinates read the same value at every tick

#### Scenario: A sign that does not jump integrates as its continuous twin

- **WHEN** a running root's law is `5 * (x − 50) * sign(x − 50)` and a
  second root's is `5 * abs(x − 50)`, and both are driven across `50`
- **THEN** both driven coordinates read the same value at every tick,
  the crossing of `sign` having been located and contributed nothing

#### Scenario: A jump nested in another jump's argument

- **WHEN** a running root's law engages only on alternate revolutions,
  `72 * clamp01((angle − 360 * w − 113.5) / 11.25) * (1 − (w − 2 * floor(w / 2)))`
  with `w = floor(angle / 360)`, and the crank is moved through four
  revolutions from `100`
- **THEN** the driven coordinate reads `72` after the first revolution,
  `72` after the second, `144` after the third and `144` after the
  fourth

#### Scenario: The same movement split differently gives the same answer

- **WHEN** one running simulation takes a revolution of the crank in a
  single tick, another in twelve, and another in two hundred and forty
- **THEN** all three leave the driven coordinate at the same value

#### Scenario: A tick that would cross too many surfaces is refused

- **WHEN** a periodic law is driven far enough in one tick to cross more
  surfaces than the stated maximum
- **THEN** the tick is refused naming the relation, the coordinate, the
  primitive and the count; the bank, the tick count and the tree are
  unchanged; and the move's handle reports `refused`

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
many stop events as it has inputs admitting travel, because each event
stops at least one moving input for the rest of that tick.

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

### Requirement: A law may read the coordinate it drives

Under a running root a relation whose source group names its own DRIVEN
end SHALL be integrated so that the law reads, on each piece of the tick,
the value that coordinate HELD at the piece's start — its RETAINED value
— and never a value the same piece is computing.

Such a relation SHALL drive exactly ONE coordinate. A relation whose
driven end is a GROUP and whose source group names any member of that
group SHALL be REFUSED at class definition, naming the relation and the
coordinate, and saying that a relation reading its own driven end drives
one coordinate — whether the member reads ITSELF or a SIBLING driven end.

**The read SHALL be a SWITCH.** The system SHALL REFUSE, at construction
and by relation identity — naming the relation as written and the class
that stated it — a law whose SKELETON, the expression with every jump
node replaced by its branch, still names the driven coordinate it reads.
A read that survives the skeleton enters the law continuously, which
makes the relation a differential equation that the difference of two
evaluations does not define. The message SHALL say that a read must pass
through a node that is piecewise constant in it — `floor`, `ceil`,
`sign` or a comparison — and that a remainder alone is not one, because
a fixed quotient leaves `a − q·b`, which still carries the coordinate's
slope.

The system SHALL likewise REFUSE, at construction and by relation
identity, a relation reading a driven end the run does not BANK — a
plain port or a derived coordinate — saying that a retained value is a
history and only a coordinate the run owns keeps one.

**Over one tick such a law SHALL be integrated PIECE BY PIECE.** A jump
node DEPENDS on the driven coordinate when that coordinate is among the
free names of the node's argument subtree. The tick's path SHALL first
be partitioned by the jump nodes that do NOT depend on it, exactly as any
other law's path is, their branches read at that partition's midpoints;
INSIDE each of its pieces the dependent nodes SHALL then be walked:

- At the walk's left end the driven coordinate holds a known value: the
  tick's committed value at the start, and the value the cuts already
  taken placed it at afterwards.
- Every dependent node's branch SHALL be determined in the graph's
  postorder, with the driven coordinate at that retained value and every
  OTHER source at the piece's LEFT END — not at its midpoint, because a
  level quantity naming both the driven coordinate and a source may cross
  inside the piece by the source's motion alone, and the branch read past
  that crossing is not the branch the piece begins under.
- A dependent node whose level sits EXACTLY on a surface at that left end
  SHALL take the branch its operator gives; if the level then LEAVES the
  surface into the other branch's region, that node SHALL be flipped to
  the other branch at the left end and every branch decided again. If the
  flipped branch carries the level back across as well, the tick SHALL be
  REFUSED naming the relation, the coordinate and the primitive, and
  SHALL commit nothing.
- With those branches fixed the substituted law SHALL be continuous on
  the piece and SHALL NOT name the driven coordinate, so that
  coordinate's own value along the piece is one ordinary evaluation.
- Each dependent node's level quantity SHALL be followed along the piece
  — through the driven coordinate's own path and through the sources —
  and the piece SHALL be CUT at the FIRST surface any of them reaches
  strictly inside it: SOLVED exactly where that level is affine along the
  path, and equally where that level and the driven coordinate's own path
  over the piece are each affine or PIECEWISE AFFINE — the requirement
  "A kink is a cut, and a piecewise-affine quantity is solved" — the
  piece being SUB-DIVIDED at the kink breakpoints of BOTH before each
  sub-piece is solved; otherwise sampled at the same fixed number of
  sub-intervals and
  bisected to the same tolerance a jump search already uses. No further
  tolerance SHALL be introduced, and a crossing found within that
  tolerance of the piece's left end SHALL NOT be merged into it.
- The piece's contribution SHALL be the substituted law's change over it,
  and the next piece SHALL be decided the same way.

A tick whose path is cut more times than the stated maximum SHALL be
refused exactly as any other over-crossed tick is.

**After a cut the driven coordinate SHALL be committed AT THE FAR SIDE OF
THE SURFACE, at the nearest representable value.** Where the piece moved
it, the coordinate SHALL be placed at the representable value NEAREST the
surface among those at which the crossing node's level — evaluated with
the driven coordinate at that value and every other source at the
crossing's own fraction — reads the branch on the side the level was
moving TOWARD. That value SHALL be what the next piece starts from, and a
tick in which at least one cut placed the coordinate SHALL COMMIT the
value the walk left it at — the last landing and whatever the pieces
after it contributed — rather than its starting value plus the
increment, exactly as a stopped coordinate is committed at its bound. Where the piece did NOT move the coordinate, it SHALL stand where
it stood. A coordinate held at a gate SHALL therefore read the same
branch on every later tick, whatever its sources do, and SHALL survive a
snapshot and a restore bit for bit.

A model SHALL state a gate whose DISENGAGED state has WIDTH — the
mechanism's own clearance — because a gate whose disengaged state is a
single value of the coordinate reads engaged on one side of it and cannot
hold when the coordinate arrives from that side. The width is the
model's to state and the system SHALL NOT require any particular one: a
band of any positive width holds from both directions.

**A self-read crossing is NOT a stop.** It SHALL stop no input, retire
no command and appear in the crossing record rather than the stop
record. A declared range on the driven coordinate SHALL stop it exactly
as it stops any other, located over this same partition, and SHALL be
committed at its bound even where a cut of the same segment placed it
elsewhere.

**At rest such a relation SHALL bind nothing.** It SHALL be recorded
solved FORWARD, its law unapplied, so the rest render poses the tree from
the author's own rest default and the run refuses by name when there is
none. Binding the whole bank again, rendering, or inspecting the tree
SHALL advance it by nothing: the relation moves its coordinate only
through a tick.

#### Scenario: A wheel clears to its gap and the ring runs on

- **WHEN** a running root states
  `(ring & wheel.turn).drives(wheel.turn, law=missing_tooth)`, whose gate
  is disengaged over a band of half-width `g` about every multiple of
  `360`, the wheel rests at `108`, and `move('ring', by=500, duration=1)`
  is run at `dt = 0.1`
- **THEN** the tick sequence commits with `ring` at `500` and its handle
  `completed`, `wheel.turn` at the band's lower edge — within `g` of
  `360`, at the nearest representable value on the disengaged side — and
  the crossing at which the wheel reached its gap recorded in
  `sim.crossings` and not in `sim.stops`

#### Scenario: Sweeping an already-cleared wheel moves it by nothing

- **WHEN** the same root is swept a second time by another
  `move('ring', by=500, duration=1)`, and a third
- **THEN** `ring` reads `1500`, `wheel.turn` holds the SAME float it
  landed on, bit for bit, after each of them, and every handle reports
  `completed`

#### Scenario: Swept backward, a digit clears to zero the short way

- **WHEN** the wheel rests at `108` and the ring is swept BACKWARD far
  enough to carry it past zero
- **THEN** the wheel ends at the band's UPPER edge — within `g` above
  `0`, at the nearest representable value on the disengaged side — having
  turned three teeth and no more, and it does not move on a further
  backward sweep

#### Scenario: Every digit clears and no digit overruns

- **WHEN** the same root is constructed ten times, its wheel resting at
  each of `0, 36, 72, … 324`, and each is given a sweep long enough to
  reach the gap
- **THEN** each wheel ends within `g` of the next multiple of `360` in
  the sweep's direction — the one it already stood on for the wheel that
  rested at `0`, which does not move at all

#### Scenario: A wheel standing exactly on a band edge is not driven through it

- **WHEN** a wheel is placed exactly at the value its own gate's surface
  sits on — the float a previous sweep landed it at — and the ring is
  swept, first in the direction that carries the level INTO the gate's
  engaged region and then in the direction that carries it away
- **THEN** it holds in the direction that would take it deeper into the
  band, turns in the direction that leaves it, and in neither case is it
  carried through the band by a piece integrated under the wrong branch

#### Scenario: A partial sweep is retained and resumes

- **WHEN** the wheel rests at `108`, `move('ring', by=120, duration=1)`
  completes, the caller then reads `sim.state`, renders the tree, takes a
  snapshot and restores it, and only then requests another
  `move('ring', by=380, duration=1)`
- **THEN** the wheel stands at `228` after the first move and unchanged
  through every inspection, and at the band's edge after the second — no
  starting register having been supplied by the caller

#### Scenario: The same sweep at three cadences agrees

- **WHEN** one running simulation takes the whole sweep in a single
  tick, another in twelve and another in two hundred and forty, and a
  fourth takes it as four partial commands with the ring released
  between them
- **THEN** all four leave the wheel and the ring at the same values
  within the run's agreement window, no tick records a stop, no command
  is retired `blocked`, and the total travel admitted is the same

#### Scenario: A continuous read is refused

- **WHEN** a running root states
  `(ring & wheel.turn).drives(wheel.turn, law=...)` whose law is
  `ring * wheel`, or `ring * (wheel % 360)`
- **THEN** construction is refused naming the relation and the class that
  stated it, and saying the read must pass through a node that is
  piecewise constant in it and that a remainder alone is not one

#### Scenario: A self-read of a coordinate the run does not bank is refused

- **WHEN** a running root states a self-read relation whose driven end is
  a plain port rather than a joint coordinate
- **THEN** construction is refused naming the relation and the port, and
  saying that a retained value is a history and only a coordinate the run
  owns keeps one

#### Scenario: A driven group with a self-read is refused

- **WHEN** a class states
  `(crank & lever.swing & pawl.turn).drives((lever.swing, pawl.turn), law=...)`
- **THEN** class definition is refused naming the relation and the
  coordinate read, and saying that a relation reading its own driven end
  drives one coordinate

#### Scenario: Several wheels clear independently from one ring

- **WHEN** a running root drives four wheels resting at `0`, `108`, `252`
  and `324` from one `ring` input, each by its own self-read relation
  whose rack term opens over that wheel's own station, and the ring is
  swept through the first three stations only
- **THEN** the first wheel does not move, the second and third each end
  at their band's edge, the fourth is untouched, and the ring's handle
  reports `completed` with its whole travel admitted

#### Scenario: A declared range on the ring still blocks

- **WHEN** the ring's own coordinate declares `range=(None, 400)` and a
  sweep of `500` is requested
- **THEN** the ring stops at exactly `400`, its command retires
  `blocked`, `sim.stops` names the ring's coordinate, and the wheels
  cleared only as far as the admitted sweep carried their racks

#### Scenario: Reversal inside the gap moves nothing

- **WHEN** a wheel standing INSIDE its band is swept backwards and then
  forwards again
- **THEN** it does not move in either direction, both handles report
  `completed`, and no stop is recorded

#### Scenario: Reversal while engaged backs the wheel up

- **WHEN** a sweep carries a wheel from `108` part way toward its gap and
  the ring is then swept back the same distance
- **THEN** the wheel returns to `108` within the run's agreement window,
  the two increments having been the same law read in both directions

#### Scenario: A stop and a self-read crossing in one tick

- **WHEN** one tick would carry a wheel through its gap at one fraction
  and take an unrelated ranged coordinate past its bound at another
- **THEN** the ranged coordinate stops at its bound exactly, the wheel
  holds at its gap, the crossing is recorded at its fraction OF THE TICK
  rather than of the segment, and `sim.stops` names only the ranged
  coordinate

#### Scenario: A self-read law's identity names what it reads

- **WHEN** two running roots differ only in whether their law reads the
  driven coordinate
- **THEN** the program's described listing differs, their identities
  differ, and a snapshot of one is refused by the other

#### Scenario: A tick that fails after a self-read cut commits nothing

- **WHEN** a segment after a self-read cut meets a conflict
- **THEN** the bank, the tick count and the tree stand as before the
  whole tick, no crossing is recorded, the coordinate is NOT left at the
  value the cut placed it at, and the commands that moved retire
  `refused`

### Requirement: A selection decides which sources a law reads

A mechanism's dependencies may be SELECTED by where one of its own parts
stands, so that the union of what it reads over every selection is
cyclic although each selection's own dependencies are not — the same
fixed carry lever of a Curta is tripped by the dial the carriage has
brought under it and advances the dial beyond that one.

Under a running root the system SHALL admit such a union and SHALL order
it once per PIECE of a tick rather than once per program.

**A BLOCK is a nontrivial strongly connected component** of the
dependency graph the requirement "A relation's law is compiled to an
expression over coordinate ids" defines. Every coordinate a block's edges
read SHALL therefore be one the block itself determines, or one
determined UPSTREAM of it, or an input, or a coordinate that holds.

**A SELECTOR is a jump node of a block member's law whose LEVEL QUANTITY
reads no coordinate the block determines** — a placeholder standing in
that level being resolved into the jump node it replaced, transitively.
A jump node whose level reads a coordinate the block determines,
including the member's own driven end, SHALL NOT be a selector.

**FOLDING a law means setting jump placeholders to ZERO in the member's
SKELETON and simplifying**: a product or a quotient with a zero numerator
being zero, a sum or a difference with a zero operand being the other
operand (negated where it is subtracted). What the member READS under a
fold SHALL be the folded skeleton's free names, with every surviving
placeholder followed into its own folded level quantity, transitively.

**A placeholder SHALL be foldable to zero only where its primitive holds
the ZERO branch over an INTERVAL of its level quantity** — `floor` over
`[0, 1)`, `ceil` over `(-1, 0]`, a remainder's quotient over `(-1, 1)`,
a comparison over the whole of its false side. `sign` reads zero at a
single POINT of its level and SHALL NOT be foldable: a source it gates
is active on every piece of positive width, so treating it as removable
would admit at construction a machine every tick refuses.

**A member's UNCONDITIONAL dependencies SHALL be the coordinates the
block determines that it still reads with EVERY foldable selector of that
member at zero AT ONCE**, and a source it reads with nothing folded but
not under that one fold SHALL be SWITCHED. One fold SHALL decide both:
folding a further placeholder can only remove names and never add one, so
the reads under that single fold are the fewest any selection can leave.

Folding at compile time and reading a branch at run time are DIFFERENT
operations and SHALL NOT be conflated: over a piece the system substitutes
the branch values actually read, whatever they are, and keeps whatever
survives.

The system SHALL REFUSE, at construction and by relation identity —
naming the relations as written and the classes that stated them:

- a block containing a WIRING or a DERIVED COORDINATE, saying that
  neither carries a jump node and neither can therefore be switched;
- a block whose members' UNCONDITIONAL dependencies still form a cycle,
  under the refusal the compile requirement states — a cycle present on
  every piece is a cycle the run cannot order;
- a block one of whose driven ends the run does not BANK — a plain port
  or a derived coordinate — saying that a block advances its coordinates
  piece by piece and only a coordinate the run owns keeps that history,
  and to state the relation into the joint coordinate so the port follows
  it;
- a block member whose driven end is a GROUP, saying that a member of a
  block drives ONE coordinate.

**Over a stretch of a tick the block's SELECTORS SHALL be located
first.** Every selector's level SHALL be followed along the path its
coordinates take over the stretch — the same linear path every other
source takes — and the stretch SHALL be CUT at every surface any of them
reaches: solved exactly where that level is affine or PIECEWISE AFFINE —
the requirement "A kink is a cut, and a piecewise-affine quantity is
solved" — otherwise sampled at
the same fixed number of sub-intervals and bisected to the same tolerance
a jump crossing already uses. Two cuts within that tolerance SHALL be
ONE, a tick cut more times than the stated maximum SHALL be refused
exactly as any other over-crossed tick is, and no further tolerance SHALL
be introduced.

**On each piece the block SHALL be ORDERED and then RUN.** Every
selector's branch SHALL be read at the piece's MIDPOINT; what each member
reads with THOSE branch values substituted — not the compile's zero ones
— SHALL give the piece's ACTIVE dependencies; and the members SHALL be
ordered topologically over them.
A piece whose active dependencies are STILL CYCLIC SHALL REFUSE the tick,
naming the piece, the selector branches it was read under and the
relations on the cycle, and SHALL COMMIT NOTHING: the bank, the tick
count, the tree and the records SHALL stand as they were and the commands
that moved an input SHALL be retired refused, exactly as for a conflict.

**On a piece a selector SHALL be a CONSTANT for every member of the
block**: the branch read at the midpoint SHALL be substituted into the
member's own integration rather than re-located by it, so the order the
block chose and the branch the member reads cannot disagree. Each member
SHALL otherwise be integrated over the piece by the rules that already
govern it — the jump partition, and the walk of a law that reads the
coordinate it drives — with a coordinate the block determines taken at
the value the block has advanced it to and moving by the increment
computed for it on THAT piece, and every other coordinate taken along the
stretch's own path restricted to the piece.

The block's contribution to each of its coordinates SHALL be the sum over
the pieces. Where ANY piece's integration LANDED a coordinate at an
absolute value, the block SHALL report for that coordinate the ABSOLUTE
value it has itself advanced it to by the END of the stretch — that
landing, and every increment the later pieces gave it — and the run SHALL
commit that value exactly where it commits a landing of a law that reads
the coordinate it drives. A coordinate no piece landed SHALL be reported
as an increment only, and committed as its value plus that increment. A
landing followed by further motion SHALL therefore commit the motion:
reporting the landing alone would discard it. Every crossing a piece
reports SHALL be recorded at its fraction of the whole tick, and a
selector's own crossings SHALL be recorded as the crossings of the member
whose law states them.

A source a piece's fold switched OUT, and which the piece's order has not
yet determined, SHALL be given to the member that reads it at the value
the block has advanced it to at the piece's START, moving by nothing.

**A selector crossing is NOT a stop.** It SHALL stop no input, retire no
command, and appear in the crossing record rather than the stop record. A
DECLARED RANGE on a coordinate a block determines SHALL stop it exactly
as it stops any other, located through the block, and SHALL be committed
at its bound even where a piece of the same segment landed it elsewhere.
An input that reaches a stopped coordinate only through a selection that
is INACTIVE over the stretch SHALL NOT be stopped by it.

**At rest a block relation SHALL bind nothing.** It SHALL be recorded
solved FORWARD, its law unapplied, so the rest render poses the tree from
the author's own rest default and the run refuses by name when there is
none. Binding the whole bank again, rendering, or inspecting the tree
SHALL advance a block's coordinates by nothing.

**Membership SHALL be decided BEFORE the rest render**, over the
relations, wirings and derived coordinates of the linked tree, each read
in the direction it is DECLARED. Every relation on a dependency cycle
that determines at least one coordinate the run BANKS SHALL be so
decided, whether it names one coordinate at each end or several, so that
every such cycle reaches the compile and is answered there by name rather
than by the rest render's own refusals. A cycle that determines NO banked
coordinate SHALL be left alone and SHALL behave exactly as it does
without this requirement.

Deciding membership again over the same tree SHALL give the same answer,
and a simulation constructed over a tree a previous simulation owned
SHALL decide it afresh, so a tree posed by one run and handed to another
carries nothing of the first.

Under a root that does NOT declare `Time.running()` nothing SHALL change:
the same relations SHALL be solved, deferred and refused by the ordinary
enumeration exactly as they are without this requirement.

**A SELECTION CHANGE ALONE SHALL MOVE NOTHING.** A selector is a jump
node, and a jump never moves a part: with its sources otherwise still, a
tick in which a selection changes SHALL commit every coordinate of the
block unchanged.

A command taken in one tick, and the same command taken in many, SHALL
agree within the run's own agreement window for every coordinate and for
the travel each command admits, and EXACTLY for every command's STATUS
and for every discrete reading of a coordinate — a gate set or not, a
digit — taken where no committed value stands within that window of a
surface, a bound or a gate threshold. The travel a command admits is
accumulated once per tick and SHALL NOT be required to agree bit for bit
across two partitions of one command.

The program's IDENTITY SHALL distinguish a program carrying a block from
one that does not, and SHALL distinguish two programs whose blocks hold
different members. A block's members SHALL be listed in an order
deterministic for a given tree, and the program's listing SHALL name the
block at its position in the program's order and then carry each of its
members' own entries, so the identity covers every member's ends,
direction and expression as it does any other edge's.

#### Scenario: A carriage selects which wheel a lever reads

- **WHEN** a running root states a lever driven by `lower.turn` gated by
  `shift < .5` and by `higher.turn` gated by `shift >= .5`, and a
  `higher.turn` driven by the crank gated by `shift >= .5` and by the
  lever gated by `shift < .5` — a union the compiler cannot order — with
  a rest default on every driven coordinate
- **THEN** construction succeeds, the program carries ONE block holding
  those two relations, and its listing names the block

#### Scenario: The carry happens at one position and not the other

- **WHEN** that root is cranked with `shift` at `0`, and again with
  `shift` at `1`
- **THEN** at `0` the lower wheel drives the lever and the lever advances
  the higher wheel, at `1` the higher wheel drives the lever and the
  higher wheel is driven by the crank directly, and each result equals
  the one the SAME laws give with `shift` frozen at that value and
  compiled as an ordinary acyclic program

#### Scenario: A selection change inside a tick moves nothing

- **WHEN** `shift` is moved from `0` to `1` in one tick, crossing both
  selectors, with every other input standing still
- **THEN** every coordinate of the block commits the float it held, the
  selector crossings are recorded in `sim.crossings`, and no stop is
  recorded

#### Scenario: A shift away and back preserves every part's state

- **WHEN** the crank is turned until the lever is set, the carriage is
  shifted to another position, the crank is turned again, and the
  carriage is shifted back
- **THEN** the lever still stands where the mechanism left it, each wheel
  holds the angle its own motion gave it, and nothing was reset by the
  shifts

#### Scenario: A finer partition agrees with a coarser one

- **WHEN** the same crank travel is requested as one tick, as twelve, and
  as two hundred and forty, each from the same restored snapshot, with
  every gate threshold and declared bound chosen away from where a tick
  ends
- **THEN** every coordinate agrees within the run's agreement window,
  every command's admitted travel agrees within that same window, and
  every command reports the same status

#### Scenario: A landing in one piece and motion in a later one commit both

- **WHEN** one tick carries a selector crossing, a coordinate the block
  drives is landed at a gate in the piece BEFORE that crossing, and the
  selection the crossing brings in drives that same coordinate further in
  the piece after it
- **THEN** the bank commits the absolute value the block advanced it to
  over the whole stretch — the landing plus the later piece's increment —
  and not the landing alone

#### Scenario: A switched-out source is handed no motion

- **WHEN** a piece's selection switches an in-block source out of a
  member's law, and the same tick is run again with that source given a
  different increment
- **THEN** the member's contribution on that piece is the same float in
  both runs

#### Scenario: A cycle with no self-read and no selection is refused by the compile

- **WHEN** a running root states an UNCONDITIONAL cycle of multi-source
  relations, none of which gates a source behind a jump node and none of
  which reads the coordinate it drives, each driven coordinate carrying
  its own guarded rest default
- **THEN** construction is refused naming the relations on the cycle and
  the coordinates they wait on — the compile's own refusal, rather than
  the rest render's refusal of a doubly bound coordinate

#### Scenario: A selected cycle with no self-read is admitted

- **WHEN** the same cycle gates each in-block source behind a comparison
  on a coordinate it does not determine, still with no relation reading
  the coordinate it drives
- **THEN** construction succeeds, the program carries one block holding
  those relations, and each driven coordinate's rest value is its own
  guarded default

#### Scenario: A cycle no selection breaks is refused at construction

- **WHEN** a running root states the same two relations with their
  selections removed, so each reads the other's coordinate
  unconditionally
- **THEN** construction is refused naming both relations and the
  coordinates they wait on

#### Scenario: A plain port among a block's driven ends is refused

- **WHEN** one of the two relations drives a plain port that a wiring
  carries into a joint coordinate, rather than the joint coordinate
  itself
- **THEN** construction is refused naming the relation and the port, and
  saying that only a coordinate the run owns keeps a block's history

#### Scenario: A piece that cannot be ordered refuses the tick

- **WHEN** a running root's two selections are written so that some
  reachable value of the selecting input leaves both dependencies active
  at once, and the input is moved to that value
- **THEN** the tick is refused naming the selector branches and the
  relations on the cycle, `sim.state` is the bank the previous tick
  committed, the tick count did not advance, and the commands that moved
  an input report `refused`

#### Scenario: An inactive association does not block an input

- **WHEN** a wheel the block drives declares a range, stands at its
  bound, and an input that reaches it ONLY through a currently inactive
  selection is moved
- **THEN** that input's command is not retired `blocked`, it admits its
  whole travel, and the stopped wheel does not move

#### Scenario: A range on a block coordinate stops it and wins over a landing

- **WHEN** a coordinate the block drives declares a range and one tick
  both lands it at a gate and carries it past that range
- **THEN** it is committed AT its bound, the stop is recorded naming the
  inputs that pushed it, and the landing does not overwrite the bound

#### Scenario: A block member that reads its own coordinate walks inside each piece

- **WHEN** one of the block's relations also reads the coordinate it
  drives through a switch — a latch set by a pin and reset by a cam — and
  one tick carries both a selector crossing and a crossing of that
  latch's own gate
- **THEN** both crossings are recorded at their own fractions of the
  tick, the latch is committed at the value its walk left it at, and the
  tick's result equals the one the same tick gives with the selection
  frozen at each of its two branches over the corresponding parts of the
  travel

