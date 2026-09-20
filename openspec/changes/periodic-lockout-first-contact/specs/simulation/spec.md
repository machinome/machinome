## MODIFIED Requirements

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
level OUTWARD AT THE LOCATED CONTACT — raises it between the inside and
outside sides of that contact's search bracket. A later return to the same
or a lower level SHALL NOT cancel this pushing motion. Each candidate's
path SHALL be evaluated from the same stretch origin at those fractions,
with other admissions set to zero and the bound's own-coordinate argument
still frozen at the tick's committed value. This rule applies equally to
independent time-drive admissions. It SHALL NOT introduce a new tolerance,
a request-length cap, or additional synthetic input requests. Thus an input
moving a read coordinate so as
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

#### Scenario: A periodic lockout stops a long request at its first contact

- **WHEN** a crank at 120° drives a bell and a co-rotating drum, the bell's
  lower bound reads the drum as `-360*floor((-drum-10.8)/360)-125.22`, and
  an immediate request asks for crank 840°, crossing a sampled forbidden
  interval before ending in a later revolution's open window
- **THEN** the request reports `blocked` at crank 125.22° within the
  existing search tolerance, admitting approximately 5.22°, instead of
  raising an invariant error or passing through the first obstruction

#### Scenario: Short and long requests meet the same periodic contact

- **WHEN** the same prepared lockout receives a short immediate request to
  150°, a long immediate request to 840°, or a timed request to 840° whose
  ticks resolve that contact under the existing sampling guarantee
- **THEN** all requests stop at the same first contact within the existing
  agreement tolerance and the retained follower does not move

#### Scenario: Retrying a periodic contact does not resume hidden travel

- **WHEN** the blocked crank is requested forward again, then relieved a
  small distance backward and requested forward again
- **THEN** it blocks at the same contact, backward relief is admitted, and
  no portion of the earlier request is resumed or remembered

#### Scenario: A free periodic mechanism keeps unrestricted legal travel

- **WHEN** the actual retained follower tracks its legal indexed positions
  so the periodic bound remains satisfied over a three-turn request
- **THEN** the request completes all three turns with the expected retained
  displacement; the fix introduces no one-turn cap or artificial stop

#### Scenario: Periodic contact preserves unrelated motion and replay

- **WHEN** a periodic contact stops one admission while an independent
  admission moves, and the same operation is replayed from a snapshot
- **THEN** the independent admission completes, the pushing admission
  reports only its admitted travel, and replay reproduces the committed
  bank, stop identities, statuses and travel under the existing tolerances
